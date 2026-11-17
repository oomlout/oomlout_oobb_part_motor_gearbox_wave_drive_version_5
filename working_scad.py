"""OOBB hardware dictionaries + an editable native OpenSCAD drawing.

No imported STL geometry, SolidCraft, web services, or cycloidal-project imports.
"""
import argparse
import copy
import json
import math
import re
from pathlib import Path
import shutil
import subprocess
import sys

import oobb
import opsc
from solid2 import scad_render
import yaml

from working_oomp_populate import define

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "components"))


def bearing_spec(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("bearing_size", "6810")
    kwargs.setdefault("shape", "oobb_bearing")
    kwargs.setdefault("type", "p")
    kwargs.setdefault("pos", [0, 0, 0])
    kwargs.setdefault("overhang", True)
    result = oobb.oe(**kwargs)
    while isinstance(result, list):
        result = result[0]
    return {
        "id": 2 * result["id"],
        "od": 2 * result["od"],
        "depth": result["depth"],
    }


def resolve(**kwargs):
    from wave_drive.compact_recipe import resolve as action
    return action(**kwargs)


def piece_definitions(**kwargs):
    from wave_drive.compact_recipe import piece_definitions as action
    return action(**kwargs)


def hardware_definitions(**kwargs):
    from wave_drive.compact_recipe import hardware_definitions as action
    return action(**kwargs)


def get_version_5(thing=None, **kwargs):
    """Familiar OOBB dispatcher entry; the native SCAD modules perform the drawing."""
    if thing is None:
        thing = {}
    thing["kwargs"] = resolve(**kwargs)
    thing["pieces"] = piece_definitions(**kwargs)
    thing["hardware_primitives"] = hardware_definitions(**kwargs)
    return thing


def scad_literal(value):
    return json.dumps(value, ensure_ascii=True)


def export_hardware(folder, **kwargs):
    from wave_drive.compact_recipe import ensure_local_hardware
    ensure_local_hardware()
    modules = ["// Generated from installed OOBB v5. All primitives use overhang=True.\n"]
    native_sources = {}
    for definition in hardware_definitions(**kwargs):
        primitive_kwargs = copy.deepcopy(definition["kwargs"])
        objects = oobb.oe(**primitive_kwargs)
        shape = opsc.opsc_get_object(copy.deepcopy(objects), mode="3dpr")
        rendered = scad_render(shape)
        # SolidPython emits raw-component use directives globally. Inline their
        # native SCAD definitions once, outside wrappers, to keep this part portable.
        for match in re.finditer(r"(?:use|include)\s+<([^>]+)>;?", rendered):
            path = Path(match.group(1))
            native_sources[str(path)] = path.read_text(encoding="utf-8")
        rendered = re.sub(r"(?:use|include)\s+<[^>]+>;?", "", rendered).strip()+"\n"
        modules.append("module " + definition["name"] + "() {\n" + rendered + "\n}\n")
    (folder / "oobb_hardware.scad").write_text("\n".join(native_sources.values())+"\n"+"\n".join(modules), encoding="utf-8")
    from solid2.core.scad_import import extra_scad_includes
    extra_scad_includes.clear()


def bom(**kwargs):
    from wave_drive.compact_recipe import bom as action
    return action(**kwargs)


def render_scad(source, output, **kwargs):
    executable = shutil.which("openscad")
    if not executable:
        raise RuntimeError("OpenSCAD must be on PATH to render")
    command = [executable, "--backend=Manifold", "-o", str(output)]
    command.extend(kwargs.get("options", []))
    command.append(str(source))
    result = subprocess.run(command, capture_output=True, text=True, timeout=240)
    log = result.stdout + result.stderr
    output.with_suffix(output.suffix + ".log").write_text(log, encoding="utf-8")
    if result.returncode or "ERROR:" in log or "WARNING:" in log or not output.exists():
        raise RuntimeError(f"OpenSCAD failed: {source.name}\n{log}")


def make_part(part, **kwargs):
    thing = get_version_5(**copy.deepcopy(part["oobb_details"]))
    c = thing["kwargs"]
    output_root = Path(kwargs.get("output_root", ROOT))
    folder = output_root / part["directory"]
    folder.mkdir(parents=True, exist_ok=True)
    if kwargs.get("assembly_only", False):
        from wave_drive import assembly_cards, documentation, package_release
        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            raise RuntimeError("Run a full build before --assembly-only")
        manifest = json.loads(manifest_path.read_text())
        presentation_keys = {"assembly_cards", "assembly_card_style", "assembly_part_labels", "assembly_book", "assembly_steps", "generate_assembly_cards", "package_outputs"}
        for key, value in c.items():
            if key not in presentation_keys and manifest["configuration"].get(key) != value:
                raise ValueError(f"Mechanical/build setting changed ({key}); run python working.py first")
        for key in presentation_keys:
            manifest["configuration"][key] = c[key]
        manifest_path.write_text(json.dumps(manifest, indent=2)+"\n")
        assembly_cards.main(part_folder=folder, threads=c.get("render_threads", 8))
        documentation.generate(part_folder=folder)
        if c.get("package_outputs", False):
            package_release.main(part_folder=folder)
        return folder
    # Base variables, not derived coordinates, are emitted so SCAD editing stays live.
    settings = define(**copy.deepcopy(part["oobb_details"]))
    skip = {"oobb_name", "oobb_type"}
    header = "// Generated by working_scad.py. Edit the Python recipe to persist changes.\n"
    (folder / "parameters.scad").write_text(header + "\n".join(
        f"{name} = {scad_literal(value)};"
        for name, value in settings.items()
        if not name.startswith("taxonomy_") and name not in skip and isinstance(value, (int, float, str, bool))
    ) + "\n", encoding="utf-8")
    shutil.copyfile(ROOT / "components" / "wave_drive" / "wave_drive.scad", folder / "geometry.scad")
    shutil.copyfile(ROOT / "components" / "wave_drive" / "compact_helpers.scad", folder / "compact_helpers.scad")
    export_hardware(folder, **c)
    prefix = "include <parameters.scad>;\nuse <oobb_hardware.scad>;\ninclude <geometry.scad>;\n"
    pieces = thing["pieces"]
    from wave_drive.compact_recipe import optional_print_definitions
    optional_prints = optional_print_definitions(**c)
    print_pieces = pieces+optional_prints
    placements = []
    row_x = 0
    row_y = 0
    row_height = 0
    # Multiple plates are intentional; the full set is not falsely labelled a 220 mm bed.
    for piece in print_pieces:
        call = piece["module"] + "(" + ", ".join(scad_literal(x) for x in piece["arguments"]) + ");"
        (folder / (piece["name"] + ".scad")).write_text(prefix + call + "\n", encoding="utf-8")
        for index in range(piece["quantity"]):
            width, height = piece["size"]
            if row_x + width > 360:
                row_x = 0
                row_y += row_height + 10
                row_height = 0
            placements.append({"part": piece["name"], "instance": index, "xy": [row_x + width/2, row_y + height/2], "call": call})
            row_x += width + 10
            row_height = max(row_height, height)
    print_scene = "\n".join(f"translate({scad_literal([*p['xy'], 0])}) {p['call']}" for p in placements)
    (folder / "3dpr.scad").write_text(prefix + "// Complete inventory, spread across multiple print beds.\n" + print_scene, encoding="utf-8")
    print_beds = pack_print_beds(print_pieces)
    for index, bed in enumerate(print_beds, 1):
        scene = []
        for placement in bed["parts"]:
            piece = next(p for p in print_pieces if p["name"] == placement["part"])
            call = piece["module"] + "(" + ", ".join(scad_literal(x) for x in piece["arguments"]) + ");"
            scene.append(f"translate({scad_literal([*placement['xy'], 0])}) {call}")
        (folder / f"print_bed_{index:02d}.scad").write_text(prefix + "\n".join(scene), encoding="utf-8")
    scenes = {
        "assembly": 'input_angle = 0;\nexplode = 0;\nassembly(input_angle, explode);',
        "animation": 'input_angle = 360 * $t;\nassembly(input_angle, 0);',
        "exploded": 'assembly(0, exploded_spacing);',
        "cutaway": 'difference() { assembly(0, 0); translate([-100,-100,cage_floor_z]) cube([200,100,100]); }',
        "motion_section": 'motion_section(0);',
        "fit_coupons": 'fit_coupons();',
        "collision_check": 'collision_check(is_undef(check_angle) ? 0 : check_angle);',
    }
    for name, body in scenes.items():
        (folder / (name + ".scad")).write_text(prefix + body + "\n", encoding="utf-8")
    manifest = {
        "configuration": c,
        "pieces": pieces,
        "printed_piece_count": sum(p["quantity"] for p in pieces),
        "optional_print_pieces": optional_prints,
        "print_instance_count": sum(p["quantity"] for p in print_pieces),
        "hardware": bom(**c),
        "layout": placements,
        "print_beds": print_beds,
        "validation_status": "generated; see validation reports for executed checks",
    }
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (folder / "hardware.yaml").write_text(yaml.safe_dump(bom(**c), sort_keys=False), encoding="utf-8")
    from wave_drive import motor_reference, documentation
    motor_reference.generate(part_folder=folder, configuration=c)
    documentation.generate(part_folder=folder)
    render = c.get("generate_stl", True) if kwargs.get("render") is None else kwargs["render"]
    images = c.get("generate_previews", True) if kwargs.get("images") is None else kwargs["images"]
    if kwargs.get("scad_only", False):
        render = images = False
    if render:
        for piece in print_pieces:
            print("Rendering", piece["name"], flush=True)
            render_scad(folder / (piece["name"] + ".scad"), folder / (piece["name"] + ".stl"))
        render_scad(folder / "fit_coupons.scad", folder / "fit_coupons.stl")
        render_scad(folder / "3dpr.scad", folder / "3dpr.stl")
        for index in range(1, len(print_beds)+1):
            render_scad(folder / f"print_bed_{index:02d}.scad", folder / f"print_bed_{index:02d}.stl")
    if images:
        for name in ["assembly", "cutaway", "exploded", "3dpr", "motion_section", "fit_coupons"]:
            print("Preview", name, flush=True)
            options = ["--imgsize=1600,1200", "--viewall", "--autocenter", "--colorscheme=Tomorrow", "--projection=o"]
            if name in ["motion_section", "3dpr", "fit_coupons"]:
                options.extend(["--camera=0,0,0,0,0,0,500"])
            render_scad(folder / (name + ".scad"), folder / (name + ".png"), options=options)
    if render:
        from wave_drive import validate_meshes, render_pipeline, validate_fasteners, validate_stock_lengths, package_release
        validate_meshes.main(part_folder=folder)
        render_pipeline.main(
            part_folder=folder,
            render=c.get("generate_renders", True) and not kwargs.get("no_renders", False),
            threads=c.get("render_threads", 8),
        )
        validate_fasteners.main(part_folder=folder)
        validate_stock_lengths.main(part_folder=folder)
        documentation.generate(part_folder=folder)
        if c.get("generate_assembly_cards", True) and c.get("generate_renders", True) and not kwargs.get("no_renders", False):
            from wave_drive import assembly_cards
            assembly_cards.main(part_folder=folder, threads=c.get("render_threads", 8))
            documentation.generate(part_folder=folder)
        if c.get("package_outputs", False):
            package_release.main(part_folder=folder)
    return folder


def get_wave_drive(thing=None, **kwargs):
    return get_version_5(thing=thing, **kwargs)


def pack_print_beds(pieces, **kwargs):
    """Simple guillotine packing with an explicit border and inter-part gap."""
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("bed_size", 220)
    kwargs.setdefault("margin", 3)
    kwargs.setdefault("gap", 4)
    bed_size = kwargs["bed_size"]
    margin = kwargs["margin"]
    gap = kwargs["gap"]
    beds = []
    instances = []
    for piece in pieces:
        for index in range(piece["quantity"]):
            instances.append({
                "part": piece["name"],
                "instance": index,
                "size": piece["size"],
            })
    instances.sort(key=lambda p: max(p["size"]), reverse=True)
    for instance in instances:
        width, height = instance["size"]
        if max(width, height) > bed_size-2*margin:
            raise ValueError(f"{instance['part']} does not fit the selected print bed")
        candidates = []
        for bi, bed in enumerate(beds):
            for ri, rectangle in enumerate(bed["free"]):
                x,y,w,h = rectangle
                if width <= w and height <= h:
                    candidates.append((w*h-width*height, bi, ri))
        if not candidates:
            beds.append({
                "size_mm": [bed_size, bed_size],
                "free": [[margin, margin, bed_size-2*margin, bed_size-2*margin]],
                "parts": [],
            })
            candidates = [(0, len(beds)-1, 0)]
        _, bi, ri = min(candidates)
        bed = beds[bi]
        x,y,w,h = bed["free"].pop(ri)
        bed["parts"].append({
            **instance,
            "xy": [x+width/2, y+height/2],
        })
        if w-width-gap > 0:
            bed["free"].append([x+width+gap, y, w-width-gap, height])
        if h-height-gap > 0:
            bed["free"].append([x, y+height+gap, w, h-height-gap])
    for bed in beds:
        bed.pop("free")
    return beds


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    output_root = Path(kwargs.get("output_root", ROOT))
    parts = kwargs.pop("parts", None)
    if parts is None:
        parts = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in sorted((output_root/"parts").glob("*/working.yaml"))]
    folders = []
    for part in parts:
        if kwargs.get("part_filter", "") not in part["id"]:
            continue
        if part["oobb_details"].get("run_scad", True):
            folders.append(make_part(part, **kwargs))
    if folders:
        first = folders[0].relative_to(output_root).as_posix()
        (output_root/"working.scad").write_text(f"include <{first}/motor_fit.scad>;\n",encoding="utf-8")
        rows = ["# Generated gearbox configurations", "", "Each folder is generated from working_oomp_populate.py.", ""]
        for folder in folders:
            rows.append(f"- [{folder.name}]({folder.name}/README.md)")
        (output_root/"parts/index.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
        from wave_drive.project_readme import generate
        generate(output_root=output_root, part_folder=folders[0])
    return folders


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scad-only", action="store_true")
    parser.add_argument("--no-renders", action="store_true")
    parser.add_argument("--part-filter", default="")
    main(**vars(parser.parse_args()))
