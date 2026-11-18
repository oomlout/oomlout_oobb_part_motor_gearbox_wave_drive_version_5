"""Native checks for the alignment key, open output plate and extended input."""
import copy
import json
from pathlib import Path

import numpy as np
import trimesh
import working_scad


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    folder = Path(kwargs["part_folder"]).resolve()
    c = json.loads((folder/"manifest.json").read_text())["configuration"]
    target = folder/"render/cache/eccentric_options"
    target.mkdir(parents=True, exist_ok=True)
    prefix = "\n".join(f"include <{(folder/name).as_posix()}>" for name in ["parameters.scad", "oobb_hardware.scad", "geometry.scad", "motor_reference_parameters.scad", "nema17_reference.scad"])
    report = {"checks": [], "extended_collision_angles": [], "status": "running"}

    def check(name, body, expect_empty=True):
        path = target/(name+".scad")
        path.write_text(prefix+"\ntranslate([80,0,0]) cube([1,1,1]);\n"+body+"\n")
        working_scad.render_scad(path, path.with_suffix(".stl"))
        mesh = trimesh.load(path.with_suffix(".stl"), force="mesh")
        solids = [p for p in mesh.split(only_watertight=False) if np.linalg.svd(p.vertices-p.vertices.mean(axis=0), compute_uv=False)[-1] > 1e-7]
        witness_only = len(solids)==1 and np.allclose(solids[0].bounds, [[80,0,0],[81,1,1]], atol=1e-5)
        assert witness_only == expect_empty, (name, [(p.bounds.tolist(),float(p.volume)) for p in solids])
        report["checks"].append({"name": name, "status": "passed", "expect_empty": expect_empty})

    check("aligned_halves", "intersection() { translate([0,0,cam_base_z]) motor_eccentric(); translate([0,0,cam_cap_z]) motor_eccentric_cap(); }")
    check("key_rejects_half_turn", "intersection() { translate([0,0,cam_cap_z]) eccentric_key(eccentric_key_depth); translate([eccentricity,0,cam_cap_z]) rotate([0,0,180]) translate([-eccentricity,0,0]) motor_eccentric_cap(); }", False)
    plate = "union() { translate([0,0,cage_floor_z]) cage(); translate([0,0,output_cover_z]) mirror([0,0,1]) output_retainer(); translate([0,0,output_cover_z]) output_cover(); }"
    check("viewing_hole", "intersection() { "+plate+" translate([0,0,cage_floor_z-1]) cylinder(d=output_view_diameter-0.02,h=assembly_height-cage_floor_z+2); }")
    check("payload_clearance", "intersection() { "+plate+" at_mounts(output_m3_attachment_mounts) translate([0,0,cage_floor_z-1]) cylinder(r=1.5,h=assembly_height-cage_floor_z+2); }")

    if c["include_extended_eccentric"]:
        check("extended_clamp_nut_loading", "intersection() { translate([0,0,cam_cap_z]) motor_eccentric_cap(true); translate([5.01,-3.34,shaft_clamp_z]) cube([2.68,6.68,assembly_height-shaft_clamp_z+1]); }")
        for angle in [0,45,90,135,180,225,270,315]:
            # Reuse the production collision scene; it already contains a witness.
            path = target/f"extended_collision_{angle}.stl"
            working_scad.render_scad(folder/"collision_check.scad", path, options=["-D",f"check_angle={angle}","-D","use_extended=true"])
            mesh = trimesh.load(path, force="mesh")
            solids = [p for p in mesh.split(only_watertight=False) if min(p.extents) > 1e-7]
            assert len(solids)==1 and np.allclose(solids[0].bounds, [[70,0,0],[71,1,1]], atol=1e-5), angle
            report["extended_collision_angles"].append({"angle":angle,"interference_mm3":0})
        records = json.loads((folder/"render/cache/instances.json").read_text())
        calls = []
        for record in records:
            if record["kind"] != "fastener":
                continue
            matrix = copy.deepcopy(record["matrix"])
            part = record["part"]
            if part == "screw_eccentric":
                part = "screw_eccentric_extended"
                matrix[2][3] = c["extended_eccentric_head_z"]
            mesh = folder/"render/hardware"/(part+".stl")
            calls.append(f'multmatrix({json.dumps(matrix)}) import("{mesh.as_posix()}");')
        check("extended_fasteners", "intersection() { union() { assembly(0,0,true); nema17_reference(); } union() { "+"\n".join(calls)+" } }")
        mesh = trimesh.load(folder/"motor_eccentric_cap_extended.stl", force="mesh")
        assert abs(mesh.bounds[1,2]+c["cam_cap_z"]-c["assembly_height"]) < 1e-5
        report["extended_top_z_mm"] = c["assembly_height"]
        report["extended_radial_clearance_mm"] = (c["output_view_diameter"]-c["extended_eccentric_diameter"])/2
        report["extended_screw_tip_clearance_mm"] = c["extended_eccentric_head_z"]-c["extended_eccentric_screw_length"]-c["cam_base_z"]
    report["status"] = "passed"
    report["limitations"] = "Geometric checks only; printed fit and running performance require physical tests."
    (folder/"render/extended_eccentric_validation.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PASS: keyed shaft, viewing hole, payload clearance and extended input option.", flush=True)
