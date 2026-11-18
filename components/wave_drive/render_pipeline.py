"""OpenSCAD production meshes -> editable Blender studio -> technical sheets.

Run after `python working.py --render`. No SolidCraft or STEP dependency.
The cycloidal project supplied the studio style, never the new geometry.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
import math
import re
from pathlib import Path
import shutil
import subprocess

import numpy as np
import oobb
import opsc
from solid2 import scad_render
import trimesh

import working_scad
from wave_drive.wave_profile.working import motion

ROOT = Path(__file__).resolve().parents[2]


def define(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    if "part_folder" not in kwargs:
        raise ValueError("Pass the populated part folder")
    kwargs.setdefault("render_folder", Path(kwargs["part_folder"])/"render")
    kwargs.setdefault("blender", shutil.which("blender"))
    kwargs.setdefault("render", True)
    kwargs.setdefault("threads", 8)
    return kwargs


def transform(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("pos", [0, 0, 0])
    kwargs.setdefault("mirror", False)
    kwargs.setdefault("height", 0)
    kwargs.setdefault("rotation_y", 0)
    kwargs.setdefault("rotation_z", 0)
    angle = math.radians(kwargs["rotation_y"])
    matrix = np.array([
        [math.cos(angle), 0, math.sin(angle), kwargs["pos"][0]],
        [0, 1, 0, kwargs["pos"][1]],
        [-math.sin(angle), 0, math.cos(angle), kwargs["pos"][2]],
        [0, 0, 0, 1],
    ], dtype=float)
    z = math.radians(kwargs["rotation_z"])
    rz = np.array([[math.cos(z),-math.sin(z),0],[math.sin(z),math.cos(z),0],[0,0,1]])
    matrix[:3,:3] = rz @ matrix[:3,:3]
    if kwargs["mirror"]:
        reflection = np.diag([1., 1., -1., 1.])
        reflection[2, 3] = kwargs["height"]
        matrix = reflection @ matrix
    return matrix


def instance_definitions(**kwargs):
    from wave_drive.instances import instance_definitions as action
    return action(**kwargs)


def hardware_scad(shape):
    # Nominal hardware uses no raw helper modules; remove cached global imports.
    return re.sub(r"(?:use|include)\s+<[^>]+>;?", "", scad_render(shape))


def hardware_meshes(**kwargs):
    """Nominal visual hardware, separate from print-clearance cutters."""
    c = kwargs["configuration"]
    folder = Path(kwargs["folder"])
    folder.mkdir(parents=True, exist_ok=True)
    source = Path(kwargs["part_folder"])
    includes = "\n".join(f"include <{(source/name).as_posix()}>" for name in ["parameters.scad", "oobb_hardware.scad", "geometry.scad"])
    from wave_drive.compact_recipe import ensure_local_hardware
    ensure_local_hardware()
    bodies = {
        "roller": "roller();",
    }
    for name, spec in [
        ("bearing_6810", c["output_bearing"]),
        ("bearing_6704", c["wave_bearing"]),
    ]:
        # These dimensions were resolved from OOBB by working_scad.resolve().
        bodies[name] = f"tube({spec['od']/2},{spec['id']/2},{spec['depth']});"
    for name, size, length in [
        ("screw_case", "m3", c["case_screw_length"]),
        ("screw_eccentric_extended", "m3", c["extended_eccentric_screw_length"]),
    ]:
        primitive = {
            "shape": "oobb_screw_socket_cap",
            "type": "p",
            "radius_name": size,
            "depth": length,
            "pos": [0, 0, 0],
            "zz": "none",
            "hole": True,
            "nut_include": False,
            "mode": "true",
            "overhang": True,
        }
        shape = opsc.opsc_get_object(copy.deepcopy(oobb.oe(**primitive)), mode="true")
        socket = 1.0 if size == "m3" else 0.75
        bodies[name] = f"difference() {{ {hardware_scad(shape)} translate([0,0,{2 if size == "m3" else 1}]) cylinder(r={socket},h=1.01,$fn=6); }}"
    for name, size, length in [
        ("screw_motor", "m3", c["motor_screw_length"]),
        ("screw_output", "m3", c["output_screw_length"]),
        ("screw_output_clamp", "m3", c["output_plate_clamp_screw_length"]),
        ("screw_eccentric", "m3", c["eccentric_join_screw_length"]),
        ("screw_wave", "m3", c["wave_screw_length"]),
        ("screw_cage", "m2", c["cage_screw_length"]),
        ("screw_shaft_clamp", "m3", c["shaft_clamp_screw_length"]),
    ]:
        primitive = {
            "shape": "oobb_screw_countersunk",
            "type": "p",
            "radius_name": size,
            "depth": length,
            "pos": [0, 0, 0],
            "zz": "top",
            "hole": True,
            "nut_include": False,
            "mode": "true",
            "overhang": True,
        }
        shape = opsc.opsc_get_object(copy.deepcopy(oobb.oe(**primitive)), mode="true")
        socket = 2/math.sqrt(3) if size == "m3" else .65
        bodies[name] = f"difference() {{ {hardware_scad(shape)} translate([0,0,-0.45]) cylinder(r={socket},h=0.46,$fn=6); }}"
    primitive = {
        "shape": "oobb_nut",
        "type": "p",
        "radius_name": "m3",
        "depth": 2.5,
        "pos": [0, 0, 0],
        "zz": "bottom",
        "mode": "true",
        "overhang": True,
    }
    shape = opsc.opsc_get_object(copy.deepcopy(oobb.oe(**primitive)), mode="true")
    bodies["nut_m3"] = f"difference() {{ intersection() {{ {hardware_scad(shape)} translate([-5,-5,0]) cube([10,10,2.5]); }} translate([0,0,-0.01]) cylinder(r=1.5,h=2.52); }}"
    primitive["radius_name"] = "m2"
    primitive["depth"] = 1.6
    shape = opsc.opsc_get_object(copy.deepcopy(oobb.oe(**primitive)), mode="true")
    bodies["nut_m2"] = f"difference() {{ intersection() {{ {hardware_scad(shape)} translate([-5,-5,0]) cube([10,10,1.6]); }} translate([0,0,-0.01]) cylinder(r=1,h=1.62); }}"
    primitive["radius_name"] = "m6"
    primitive["depth"] = c["output_nut_height"]
    shape = opsc.opsc_get_object(copy.deepcopy(oobb.oe(**primitive)), mode="true")
    bodies["nut_m6"] = f"difference() {{ intersection() {{ {hardware_scad(shape)} translate([-8,-8,0]) cube([16,16,{c['output_nut_height']}]); }} translate([0,0,-0.01]) cylinder(r=3,h={c['output_nut_height']+.02}); }}"
    for name, body in bodies.items():
        path = folder / (name + ".scad")
        path.write_text(includes + "\n" + body, encoding="utf-8")
        working_scad.render_scad(path, path.with_suffix(".stl"))


def stage(**kwargs):
    settings = define(**kwargs)
    folder = Path(settings["part_folder"])
    presentation = Path(settings["render_folder"])
    cache = presentation / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((folder / "manifest.json").read_text())
    c = manifest["configuration"]
    (presentation/"style.json").write_text(json.dumps(c["render_style"],indent=2),encoding="utf-8")
    report = json.loads((folder / "mesh_validation.json").read_text())
    for name, digest in report["source_sha256"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest, "Run mesh validation after changing geometry"
    hardware_meshes(configuration=c, folder=presentation/"hardware", part_folder=folder)
    records = instance_definitions(configuration=c)
    printed = Counter(r["part"] for r in records if r["kind"] == "printed")
    assert printed == Counter({p["name"]: p["quantity"] for p in manifest["pieces"]})
    expected = Counter({"printed": manifest["printed_piece_count"]})
    for row in manifest["hardware"]:
        if row["item"] == "Nylon spacer roller":
            expected["roller"] += row["quantity"]
            continue
        kind = "bearing" if "bearing" in row["item"] else "shaft" if "shaft" in row["item"] else "fastener"
        expected[kind] += row["quantity"]
    counts = Counter(r["kind"] for r in records)
    assert counts == expected, (counts, expected)
    arrays = {}
    sources = {}
    meshes = {}
    layout = {p["name"]: iter([x for x in manifest["layout"] if x["part"] == p["name"]]) for p in manifest["pieces"]}
    for record in records:
        name, part = record["name"], record["part"]
        path = (folder if record["kind"] == "printed" else presentation/"hardware") / (part+".stl")
        local = trimesh.load(path, force="mesh")
        assert local.is_watertight and local.volume > 0, part
        mesh = local.copy().apply_transform(np.array(record["matrix"]))
        meshes[name] = mesh
        arrays[name+"_v"] = np.asarray(mesh.vertices)
        arrays[name+"_f"] = np.asarray(mesh.faces)
        sources[str(path.relative_to(folder))] = hashlib.sha256(path.read_bytes()).hexdigest()
        if record["kind"] == "printed":
            item = next(layout[part])
            bed = local.copy().apply_translation(item["xy"]+[0])
            arrays[name+"_layout"] = np.asarray(bed.vertices)
            arrays[name+"_layout_f"] = np.asarray(bed.faces)
    # Independent native SCAD assemblies verify reflection and registration.
    checks = []
    includes = "\n".join(f"include <{(folder/name).as_posix()}>" for name in ["parameters.scad", "oobb_hardware.scad", "geometry.scad"])
    for group, module in [("cage", "cage_assembly"), ("input", "input_assembly"), ("wave", "wave_assembly"), ("bearings", "nominal_bearings"), ("fixed", "fixed_assembly"), ("rollers", "roller_assembly")]:
        path = cache / ("check_"+group+".scad")
        path.write_text(includes+"\n"+module+"(0);", encoding="utf-8")
        working_scad.render_scad(path, path.with_suffix(".stl"))
        native = trimesh.load(path.with_suffix(".stl"), force="mesh")
        staged = trimesh.util.concatenate([meshes[r["name"]] for r in records if r["group"] == group])
        bound_error = float(np.abs(native.bounds-staged.bounds).max())
        volume_error = abs(float(native.volume-staged.volume))/float(native.volume)
        assert bound_error < 1e-4 and volume_error < 1e-5, (group, bound_error, volume_error)
        checks.append({"group": group, "bounds_error_mm": bound_error, "relative_volume_error": volume_error})
    from wave_drive.motor_reference import stage as stage_motor
    motor_records, motor_arrays, motor_hashes = stage_motor(
        root=ROOT,
        part_folder=folder,
        render_folder=presentation,
        configuration=c,
        motor=kwargs.get("motor", {}),
    )
    records.extend(motor_records)
    arrays.update(motor_arrays)
    sources.update(motor_hashes)
    np.savez_compressed(cache/"meshes.npz", **arrays)
    (cache/"instances.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    validation = {
        "pipeline": "OpenSCAD STL -> Blender Cycles -> Pillow sheets",
        "render_complete": False,
        "printed_instances": counts["printed"],
        "bearing_instances": counts["bearing"],
        "shaft_instances": counts["shaft"],
        "nylon_roller_instances": counts["roller"],
        "fastener_instances": counts["fastener"],
        "total_instances": len(records),
        "gearbox_instances": sum(counts.values()),
        "motor_reference_meshes": len(motor_records),
        "native_scad_registration_checks": checks,
        "source_sha256": sources,
        "hardware_detail": "Nominal envelopes; screw threads and internal bearing balls omitted. Ivory rollers are purchased 7 mm OD nylon spacers; they are excluded from the print beds.",
    }
    (presentation/"validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    return settings


def main(**kwargs):
    settings = stage(**kwargs)
    presentation = Path(settings["render_folder"])
    if settings["render"]:
        if not settings["blender"]:
            raise RuntimeError("Blender must be on PATH, or pass blender= its executable path")
        command = [settings["blender"], "--background", "--factory-startup", "-t", str(settings["threads"]), "--python-exit-code", "1", "--python", str(Path(__file__).with_name("render_studio.py")), "--", str(presentation)]
        with (presentation/"blender.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        from wave_drive.render_sheets import publish
        publish(folder=presentation, part_folder=Path(settings["part_folder"]))
        report_path = presentation/"validation.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["render_complete"] = True
        report_path.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("Presentation ready:", presentation, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-only", action="store_true")
    args = parser.parse_args()
    main(render=not args.stage_only)
