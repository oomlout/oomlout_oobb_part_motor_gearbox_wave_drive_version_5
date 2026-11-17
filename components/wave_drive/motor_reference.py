"""Editable purchased motor on the designed mounting plate and direct eccentric."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
import trimesh

import working_scad


def define(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("motor_body_depth", 40.0)
    kwargs.setdefault("motor_body_width", 42.3)
    kwargs.setdefault("motor_shaft_length", 24.0)
    kwargs.setdefault("motor_shaft_diameter", 5.0)
    kwargs.setdefault("motor_pilot_diameter", 22.0)
    kwargs.setdefault("motor_pilot_height", 2.0)
    kwargs.setdefault("motor_hole_pitch", 31.0)
    kwargs.setdefault("motor_thread_depth", 6.0)
    kwargs.setdefault("motor_cap_depth", 6.0)
    kwargs.setdefault("motor_corner_chamfer", 3.0)
    kwargs.setdefault("motor_shaft_flat_depth", 0.0)
    return kwargs


def generate(**kwargs):
    root = Path(__file__).resolve().parents[2]
    parts = Path(kwargs["part_folder"])

    c = kwargs["configuration"]
    motor_settings = {key:value for key,value in c.items() if key.startswith("motor_") and key not in ["motor_head_seat","motor_screw_length","motor_plate_depth"]}
    motor_settings.update(copy.deepcopy(kwargs.get("motor", {})))
    motor_settings["motor_shaft_diameter"] = c["input_shaft_diameter"]
    settings = define(**motor_settings)
    settings["motor_shaft_flat_depth"] = c["input_shaft_flat_depth"]
    face_z = 0.0
    if settings["motor_body_depth"] <= 2*settings["motor_cap_depth"]:
        raise ValueError("Motor body must be longer than both end caps")
    if settings["motor_thread_depth"] > settings["motor_cap_depth"]:
        raise ValueError("Reference thread depth exceeds the front cap")
    parameter_file = parts/"motor_reference_parameters.scad"
    parameter_file.write_text("// Purchased motor envelope. Recipe defines body, shaft and mounting dimensions.\n"+"\n".join(f"{key} = {json.dumps(value)};" for key,value in settings.items())+f"\nmotor_face_z = {face_z};\n",encoding="utf-8")
    shutil.copyfile(root/"components/wave_drive/nema17_reference.scad", parts/"nema17_reference.scad")
    prefix = 'include <parameters.scad>;\nuse <oobb_hardware.scad>;\ninclude <geometry.scad>;\ninclude <motor_reference_parameters.scad>;\ninclude <nema17_reference.scad>;\n'
    (parts/"motor_fit.scad").write_text(prefix+'assembly(0,0);\ntranslate([0,0,motor_face_z]) nema17_reference();\n',encoding="utf-8")
    (parts/"exploded_motor.scad").write_text(prefix+'assembly(0,exploded_spacing);\ntranslate([0,0,motor_face_z-2*exploded_spacing]) nema17_reference();\n',encoding="utf-8")
    return settings


def stage(**kwargs):
    parts = Path(kwargs["part_folder"])
    render_folder_path = Path(kwargs["render_folder"])
    settings = generate(**kwargs)
    face_z = 0.0
    hardware = render_folder_path/"hardware"
    hardware.mkdir(parents=True,exist_ok=True)
    parameter_file = parts/"motor_reference_parameters.scad"
    definitions = [
        {
            "part": "nema17_front",
            "material": "steel",
        },
        {
            "part": "nema17_stator",
            "material": "black",
        },
        {
            "part": "nema17_rear",
            "material": "steel",
        },
        {
            "part": "nema17_pilot",
            "material": "steel",
        },
        {
            "part": "nema17_shaft",
            "material": "steel",
        },
        {
            "part": "nema17_connector",
            "material": "black",
        },
    ]
    records, arrays, hashes = [], {}, {}
    mesh_prefix = f'include <{parameter_file.as_posix()}>\ninclude <{(parts/"nema17_reference.scad").as_posix()}>\n$fn=120;\n'
    for item in definitions:
        name = item["part"]
        scad = hardware/(name+".scad")
        scad.write_text(mesh_prefix+name+"();\n",encoding="utf-8")
        working_scad.render_scad(scad,scad.with_suffix(".stl"))
        mesh = trimesh.load(scad.with_suffix(".stl"),force="mesh")
        assert mesh.is_watertight and mesh.volume > 0, name
        mesh.apply_translation([0,0,face_z])
        arrays[name+"_v"] = np.asarray(mesh.vertices)
        arrays[name+"_f"] = np.asarray(mesh.faces)
        hashes[str(scad.with_suffix(".stl").relative_to(parts))] = hashlib.sha256(scad.with_suffix(".stl").read_bytes()).hexdigest()
        record = {
            "name": name,
            "part": name,
            "kind": "motor_reference",
            "group": "motor_reference",
            "material": item["material"],
            "open": False,
            "level": -2,
            "views": ["motor_fit", "motor_side", "exploded_motor"],
        }
        records.append(record)
    prefix = 'include <parameters.scad>;\nuse <oobb_hardware.scad>;\ninclude <geometry.scad>;\ninclude <motor_reference_parameters.scad>;\ninclude <nema17_reference.scad>;\n'
    # An exact boolean verifies that the reference does not overlap the gearbox.
    witness = parts/"motor_fit_check.scad"
    witness.write_text(prefix+'translate([80,0,0]) cube([1,1,1]);\nintersection() { assembly(0,0); translate([0,0,motor_face_z]) nema17_reference(); }\n',encoding="utf-8")
    working_scad.render_scad(witness,hardware/"motor_fit_check.stl")
    check = trimesh.load(hardware/"motor_fit_check.stl",force="mesh")
    # The motor face intentionally contacts the mounting plate at Z=0.
    solids = [piece for piece in check.split(only_watertight=False) if min(piece.extents)>1e-7]
    assert len(solids)==1, [(piece.bounds.tolist(),float(piece.volume)) for piece in solids]
    assert np.allclose(solids[0].bounds,[[80,0,0],[81,1,1]],atol=1e-5)
    assert abs(solids[0].volume-1) < 1e-6
    info = {
        "motor": settings,
        "source": "Cycloidal gearbox gearbox_native/nema17_double_bearing.py: previous 40 mm reference motor; external end-cap and connector details are illustrative.",
        "motor_face_z_mm": face_z,
        "motor_rear_z_mm": face_z-settings["motor_body_depth"],
        "gearbox_mounting_face_z_mm": 0,
        "motor_face_to_gearbox_mounting_face_mm": -face_z,
        "motor_shaft_tip_z_mm": face_z+settings["motor_shaft_length"],
        "motor_mount_holes_xy_mm": [[x,y] for x in [-15.5,15.5] for y in [-15.5,15.5]],
        "motor_to_gearbox_interference_mm3": 0,
        "fit_status": f"Direct motor plate and eccentric adapter are designed. Reference shaft: {settings['motor_shaft_length']:g} mm long, {settings['motor_shaft_diameter']:g} mm diameter, {settings['motor_shaft_flat_depth']:g} mm flat depth (zero means round). Bearing load limits, fit and clamp grip require confirmation on the actual motor.",
    }
    (render_folder_path/"motor_fit.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
    return records, arrays, hashes
