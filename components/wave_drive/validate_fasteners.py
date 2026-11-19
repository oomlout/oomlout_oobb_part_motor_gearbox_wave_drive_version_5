"""Check the rendered nominal socket caps and nuts against the actual native SCAD."""
import json
from pathlib import Path
import sys

import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import working_scad


def main(**kwargs):
    folder = Path(kwargs["part_folder"])
    records=json.loads((folder/"render/cache/instances.json").read_text())
    fasteners=[r for r in records if r["kind"]=="fastener"]
    prefix="\n".join(f"include <{(folder/name).as_posix()}>" for name in ["parameters.scad","oobb_hardware.scad","geometry.scad","motor_reference_parameters.scad","nema17_reference.scad"])
    calls=[]
    for r in fasteners:
        mesh=folder/"render/hardware"/(r["part"]+".stl")
        calls.append(f'multmatrix({json.dumps(r["matrix"])}) import("{mesh.as_posix()}");')
    body=prefix+"\ntranslate([80,0,0]) cube([1,1,1]);\nintersection() { union() { assembly(0); translate([0,0,motor_face_z]) nema17_reference(); } union() {\n"+"\n".join(calls)+"\n} }\n"
    path=folder/"render/cache/fastener_check.scad"
    path.write_text(body)
    working_scad.render_scad(path,path.with_suffix(".stl"))
    mesh=trimesh.load(path.with_suffix(".stl"),force="mesh")
    # Coplanar contacts may be tilted cylinder facets, not axis-aligned sheets.
    # Reject only rank-2 surfaces; retain every genuine 3D interference.
    pieces = mesh.split(only_watertight=False)
    solids = [p for p in pieces if np.linalg.svd(p.vertices-p.vertices.mean(axis=0),compute_uv=False)[-1]>1e-7]
    passed=len(solids)==1 and np.allclose(solids[0].bounds,[[80,0,0],[81,1,1]],atol=1e-5)
    c = json.loads((folder/"manifest.json").read_text())["configuration"]
    cage_screw = trimesh.load(folder/"render/hardware/screw_cage.stl", force="mesh")
    cage_stack = []
    joint_stack = []
    for record in fasteners:
        if record["part"] in ["screw_eccentric", "screw_wave", "screw_output", "screw_output_clamp"]:
            joint_mesh = trimesh.load(folder/"render/hardware"/(record["part"]+".stl"), force="mesh")
            bounds = joint_mesh.apply_transform(record["matrix"]).bounds
            eccentric = record["part"] == "screw_eccentric"
            output = record["part"] in ["screw_output", "screw_output_clamp"]
            sandwich = record["part"] == "screw_output_clamp"
            nut_bottom = c["output_plate_clamp_nut_z"] if sandwich else c["output_nut_z"] if output else c["eccentric_join_nut_z"] if eccentric else c["wave_z"]+c["wave_nut_z"]
            underside = c["retainer_z"] if sandwich else c["cage_floor_z"] if output else c["cam_base_z"] if eccentric else c["wave_z"]
            head_top = c["output_head_seat"] if output else c["eccentric_join_head_z"] if eccentric else c["wave_z"]+c["wave_height"]-c["wave_head_recess"]
            assert bounds[0, 2] <= nut_bottom+1e-4
            assert bounds[0, 2] >= underside-1e-4
            assert abs(bounds[1, 2]-head_top) < 1e-4
            surface = c["assembly_height"] if output else c["cam_cap_z"]+c["cam_cap_height"] if eccentric else c["wave_z"]+c["wave_height"]
            assert abs(bounds[1, 2]-surface-c["countersunk_head_proud"]) < 1e-4
            joint_stack.append({"name":record["name"], "size":"M3", "head":"countersunk", "head_proud_mm":float(bounds[1, 2]-surface), "tip_clearance_mm":float(bounds[0, 2]-underside), "nut_engagement_mm":2.5})
        if record["part"] != "screw_cage":
            continue
        bounds = cage_screw.copy().apply_transform(record["matrix"]).bounds
        clearance = float(bounds[0, 2]-c["cage_cap_z"])
        assert clearance >= c["cage_tip_clearance"]-1e-4
        assert bounds[0, 2] <= c["cage_nut_z"]+1e-4
        cage_stack.append({"name":record["name"], "tip_clearance_mm":clearance, "nut_engagement_mm":1.6})
    report={
        "status":"passed" if passed else "failed",
        "fastener_instances":len(fasteners),
        "cage_screw_stack": cage_stack,
        "eccentric_and_clamshell_stack": joint_stack,
        "planar_contact_fragments":len(pieces)-len(solids),
        "volumetric_components":[{"bounds_mm":p.bounds.tolist(),"volume_mm3":float(p.volume)} for p in solids],
        "scope":"Nominal screw and nut envelopes against every native gearbox body and the full motor at input angle zero; intended motor thread engagement uses smooth nominal bores.",
    }
    (folder/"render/fastener_validation.json").write_text(json.dumps(report,indent=2))
    assert passed, report
    print(f"PASS: {len(fasteners)} screw/nut envelopes clear the native gearbox.")
    # The upper clamp is tightened before the fixed ring and upper cage are fitted.
    driver = "translate([shaft_clamp_head_radius+0.05,0,shaft_clamp_z]) rotate([0,90,0]) cylinder(d=shaft_driver_diameter,h=60,$fn=64);"
    accessible_calls = [call for record,call in zip(fasteners,calls) if record["level"] <= 7]
    access_body = prefix+"\ntranslate([80,0,0]) cube([1,1,1]);\nintersection() { "+driver+" union() { motor_mount_plate(); translate([0,0,cage_cap_z]) cage_cap(); input_assembly(0); wave_assembly(0); roller_assembly(0); translate([0,0,motor_face_z]) nema17_reference();\n"+"\n".join(accessible_calls)+"\n} }\n"
    access_path = folder/"render/cache/shaft_access_check.scad"
    access_path.write_text(access_body)
    working_scad.render_scad(access_path,access_path.with_suffix(".stl"))
    access_mesh = trimesh.load(access_path.with_suffix(".stl"),force="mesh")
    access_pieces = access_mesh.split(only_watertight=False)
    access_solids = [p for p in access_pieces if np.linalg.svd(p.vertices-p.vertices.mean(axis=0),compute_uv=False)[-1]>1e-7]
    access_passed = len(access_solids)==1 and np.allclose(access_solids[0].bounds,[[80,0,0],[81,1,1]],atol=1e-5)
    access_report = {
        "status": "passed" if access_passed else "failed",
        "scope": "Straight driver access to the upper M3 shaft clamp before fitting the outer case and upper cage; lower cage, wave halves, rollers, motor and installed fasteners included. No housing access port is required.",
        "volumetric_components": [{"bounds_mm":p.bounds.tolist(),"volume_mm3":float(p.volume)} for p in access_solids],
    }
    (folder/"render/shaft_access_validation.json").write_text(json.dumps(access_report,indent=2))
    assert access_passed, access_report
    print("PASS: upper shaft clamp is accessible before the case is fitted.")
    # Assembly access is different from an interference-free final position.
    eccentric_hardware = [call for record, call in zip(fasteners, calls) if record["name"].startswith(("motor_clamp_", "eccentric_join_"))]
    eccentric_group = "union() { input_assembly(0); "+"\n".join(eccentric_hardware)+" }"
    checks = [
        {
            "name": "cage_head_entry",
            "scope": "2.15 mm radius screw-head envelope through the integrated upper disc before the bearing and output nut carrier are installed.",
            "body": "intersection() { translate([0,0,cage_floor_z]) cage(); cage_mounts() translate([0,0,cage_head_seat+0.01]) cylinder(r=2.15,h=cage_slope_height+hub_height+2); }",
        },
        {
            "name": "lower_cage_over_eccentric",
            "scope": "Continuous conservative convex sweep of the assembled eccentric shaft and its screws/nuts through the lower cage; install the 6704 and rolling clamshells afterwards.",
            "body": "intersection() { translate([0,0,cage_cap_z]) cage_cap(); hull() { "+eccentric_group+" translate([0,0,-30]) "+eccentric_group+" } }",
        },
    ]
    access_checks = []
    for check in checks:
        check_path = folder/"render/cache"/(check["name"]+".scad")
        check_path.write_text(prefix+"\ntranslate([80,0,0]) cube([1,1,1]);\n"+check["body"])
        working_scad.render_scad(check_path,check_path.with_suffix(".stl"))
        check_mesh = trimesh.load(check_path.with_suffix(".stl"),force="mesh")
        check_solids = [p for p in check_mesh.split(only_watertight=False) if np.linalg.svd(p.vertices-p.vertices.mean(axis=0),compute_uv=False)[-1]>1e-7]
        check_passed = len(check_solids)==1 and np.allclose(check_solids[0].bounds,[[80,0,0],[81,1,1]],atol=1e-5)
        result = {
            "name": check["name"],
            "scope": check["scope"],
            "status": "passed" if check_passed else "failed",
            "volumetric_components": [{"bounds_mm":p.bounds.tolist(),"volume_mm3":float(p.volume)} for p in check_solids],
        }
        access_checks.append(result)
        (folder/"render/assembly_access_validation.json").write_text(json.dumps(access_checks,indent=2))
        assert check_passed, result
    print("PASS: cage screw heads insert and the lower cage slides over the eccentric shaft.")


if __name__=="__main__":
    main()
