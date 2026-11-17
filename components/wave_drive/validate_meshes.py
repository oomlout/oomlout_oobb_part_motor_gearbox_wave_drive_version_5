"""Render-backed validation; checks all solids and OpenSCAD intersection witnesses."""
import json
import hashlib
from pathlib import Path
import sys

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import working_scad
from wave_drive.wave_profile.working import action as profile_points
from shapely.geometry import Point, Polygon


def main(**kwargs):
    folder = Path(kwargs["part_folder"])
    manifest = json.loads((folder/"manifest.json").read_text())
    report = {"solids": [], "collision_angles": [], "status": "running"}
    report["source_sha256"] = {
        name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
        for name in ["parameters.scad","geometry.scad","compact_helpers.scad","oobb_hardware.scad"]
    }
    for piece in manifest["pieces"]+manifest.get("optional_print_pieces", []):
        path = folder/(piece["name"]+".stl")
        mesh = trimesh.load(path,force="mesh")
        components = len(mesh.split())
        result = {
            "name":piece["name"],
            "watertight":bool(mesh.is_watertight),
            "positive_volume":bool(mesh.volume>0),
            "connected_components":components,
            "volume_mm3":round(float(mesh.volume),3),
            "bounds_mm":mesh.bounds.tolist(),
        }
        assert mesh.is_watertight and mesh.volume>0 and components==1, result
        assert abs(mesh.bounds[0,2]) < .001, result
        report["solids"].append(result)
    report["print_beds"] = []
    c = manifest["configuration"]
    if c["input_shaft_flat_depth"] == 0:
        report["round_shaft_bores"] = []
        expected_radius = c["input_shaft_diameter"]/2+c["shaft_fit_clearance"]
        for name in ["motor_eccentric", "motor_eccentric_cap"]:
            mesh = trimesh.load(folder/(name+".stl"), force="mesh")
            section = mesh.section(plane_origin=[0,0,.5], plane_normal=[0,0,1])
            loops = [loop for loop in section.discrete if Polygon(loop[:,:2]).contains(Point(0,0))]
            bore = min(loops, key=lambda loop: Polygon(loop[:,:2]).area)
            radii = np.linalg.norm(bore[:,:2], axis=1)
            error = float(np.max(np.abs(radii-expected_radius)))
            assert error < .002, (name, error)
            report["round_shaft_bores"].append({"part":name, "diameter_mm":2*expected_radius, "maximum_radial_error_mm":error})
    ring = trimesh.load(folder/"fixed_profile_ring.stl",force="mesh")
    section = ring.section(plane_origin=[0,0,ring.extents[2]/2],plane_normal=[0,0,1])
    profile_loop = max(section.discrete,key=len)
    actual_profile = Polygon(profile_loop[:,:2])
    expected_profile = Polygon(profile_points(**manifest["configuration"]))
    error = actual_profile.boundary.hausdorff_distance(expected_profile.boundary)
    assert error < 1e-5, error
    report["scad_python_profile_max_error_mm"] = error
    for index, bed in enumerate(manifest["print_beds"],1):
        mesh = trimesh.load(folder/f"print_bed_{index:02d}.stl",force="mesh")
        parts = mesh.split()
        assert len(parts)==len(bed["parts"]), (index,len(parts),len(bed["parts"]))
        assert mesh.is_watertight
        assert min(mesh.bounds[0,:2])>=3-1e-5 and max(mesh.bounds[1,:2])<=217+1e-5
        report["print_beds"].append({"bed":index,"parts":len(parts),"bounds_mm":mesh.bounds.tolist()})
    whole = trimesh.load(folder/"3dpr.stl",force="mesh")
    assert len(whole.split())==manifest.get("print_instance_count", manifest["printed_piece_count"])
    report["print_instance_count"] = len(whole.split())
    if manifest.get("optional_print_pieces"):
        spacer = trimesh.load(folder/"printable_spacer.stl", force="mesh")
        c = manifest["configuration"]
        assert np.allclose(spacer.extents, [c["roller_diameter"], c["roller_diameter"], c["roller_length"]], atol=.001)
        section = spacer.section(plane_origin=[0,0,c["roller_length"]/2], plane_normal=[0,0,1])
        radii = sorted(float(np.linalg.norm(loop[:,:2], axis=1).mean()) for loop in section.discrete)
        assert len(radii) == 2 and abs(radii[0]-c["roller_bore_diameter"]/2) < .002
    for angle in [0,45,90,135,180,225,270,315]:
        print("Collision check",angle,flush=True)
        output = folder/f"collision_{angle}.stl"
        working_scad.render_scad(folder/"collision_check.scad",output,options=["-D",f"check_angle={angle}"])
        mesh = trimesh.load(output,force="mesh")
        # Manifold can emit zero-thickness sheets at intentional bearing shoulder
        # contacts. Only coplanar pieces are ignored; every 3D piece must be the witness.
        solids = []
        contact_sheets = 0
        for piece in mesh.split(only_watertight=False):
            if min(piece.extents) < 1e-7:
                contact_sheets += 1
                continue
            solids.append(piece)
        assert len(solids)==1, (angle,[p.bounds.tolist() for p in solids])
        assert np.allclose(solids[0].bounds,[[70,0,0],[71,1,1]],atol=1e-5), (angle,solids[0].bounds)
        assert abs(solids[0].volume-1.0)<1e-6
        report["collision_angles"].append({"angle":angle,"interference_mm3":0,"planar_contact_fragments":contact_sheets})
    report["status"] = "passed"
    report["limitations"] = "Geometric checks only. Printed fit, friction, wear, backlash and torque require bench tests."
    (folder/"mesh_validation.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PASS:",len(report["solids"]),"watertight connected print solids; 8 empty collision checks")


if __name__=="__main__":
    main()

