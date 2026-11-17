"""Reproducible CAD assembly panels: populate -> Blender -> four-up landscape A4.

Run `python -m wave_drive.assembly_cards` via the project import setup, or use
`python working.py --assembly-only` after a full mesh build. No mesh is invented.
"""
from collections import Counter
import copy
import csv
import fnmatch
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageOps, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


ROOT = Path(__file__).resolve().parents[2]


def md5_alpha(digest):
    """OOMP md5_6_alpha: first six hex digits of MD5 encoded in lower-case base36."""
    value = int(digest[:6], 16)
    result = ""
    while value:
        value, remainder = divmod(value, 36)
        result = "0123456789abcdefghijklmnopqrstuvwxyz"[remainder]+result
    return result or "0"


def select(patterns, records):
    names = []
    for pattern in patterns:
        matches = [r["name"] for r in records if fnmatch.fnmatchcase(r["name"], pattern)]
        if not matches:
            raise ValueError(f"Assembly selector matches nothing: {pattern}")
        names.extend(matches)
    return list(dict.fromkeys(names))


def part_key(record):
    return "nema17" if record["name"].startswith("nema17_") else record["part"]


def quantities(names, records):
    chosen = [r for r in records if r["name"] in names]
    counts = Counter(part_key(r) for r in chosen if not r["name"].startswith("nema17_"))
    motor = [r for r in chosen if r["name"].startswith("nema17_")]
    if motor:
        assert len(motor) == 6, "The motor must be counted as one complete purchased unit"
        counts["nema17"] = 1
    return counts


def identities(**kwargs):
    c = kwargs["configuration"]
    folder = Path(kwargs["part_folder"])
    parts = {}
    for key, raw in c["assembly_part_labels"].items():
        spec = copy.deepcopy(raw)
        name = spec["name"].format(**c)
        detail = spec.get("detail", "").format(**c)
        identity = spec.get("catalogue_id", "").format(**c)
        matches = all(c[k] == v for k, v in spec.get("catalogue_match", {}).items())
        source = "OOMP catalogue identity"
        if not identity or not matches:
            # Local namespace is explicit; do not claim a new public OOMP record.
            identity = folder.name+"__"+key
            if key.startswith("screw_") or key == "roller" or key == "nema17":
                identity += "__"+(name+" "+detail).lower().replace(" ", "_")
            source = "Project-local assembly identity"
        digest = hashlib.md5(identity.encode("utf-8")).hexdigest()
        alpha = md5_alpha(digest)
        parts[key] = {
            "key": key,
            "name": name,
            "detail": detail,
            "id": identity,
            "identity_source": source,
            "md5": digest,
            "md5_6_alpha": alpha,
            "short_url": "https://oom.lt/a/"+alpha,
            "short_label": "oom.lt/a/"+alpha,
        }
        if spec.get("printed", False):
            for field in ["md5", "md5_6_alpha", "short_url", "short_label"]:
                parts[key].pop(field)
    code_ids = {}
    for part in parts.values():
        if "md5_6_alpha" not in part:
            continue
        previous = code_ids.setdefault(part["md5_6_alpha"], part["id"])
        assert previous == part["id"], "MD5-alpha collision between different identities"
    return parts


def prepare(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    folder = Path(kwargs["part_folder"])
    manifest = json.loads((folder/"manifest.json").read_text())
    c = manifest["configuration"]
    style = c["assembly_card_style"]
    output = folder/"assembly"
    output.mkdir(exist_ok=True)
    stage = output/"render"
    (stage/"cache").mkdir(parents=True, exist_ok=True)
    records = json.loads((folder/"render/cache/instances.json").read_text())
    # Refuse diagrams from a stale production-mesh cache.
    production = json.loads((folder/"render/validation.json").read_text())
    for name, digest in production["source_sha256"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest, name
    for name in ["instances.json", "meshes.npz"]:
        shutil.copyfile(folder/"render/cache"/name, stage/"cache"/name)
    parts = identities(configuration=c, part_folder=folder)
    render_style = copy.deepcopy(c["render_style"])
    render_style["samples"] = style["samples"]
    render_style["materials"]["context"] = {
        "name": "Previously assembled - muted grey",
        "color": "A6B6B5",
        "roughness": 0.55,
        "metallic": 0.0,
    }
    render_style["views"] = {}
    consumed = set()
    cards = []
    lookup = {r["name"]: r for r in records}
    for index, definition in enumerate(c["assembly_cards"], 1):
        step = copy.deepcopy(definition)
        step["number"] = index
        step["key"] = f"step_{index:02d}"
        for field in ["action", "tools"]:
            step[field] = step.get(field, "").format(**c)
        added = select(step["add"], records)
        assert not consumed.intersection(added), f"Step {index}: part added twice"
        # Keep the entire assembly-so-far. Occlusion does not remove inventory.
        shown = [r["name"] for r in records if r["name"] in consumed.union(added)]
        prepared = select(step.get("prepared", []), records)
        assert set(prepared) <= consumed, f"Step {index}: prepared part not yet built"
        assert set(shown) <= consumed.union(added), f"Step {index}: future part shown"
        assert set(added) <= set(shown), f"Step {index}: added part is invisible"
        offsets = {}
        arrows = {}
        targets = {}
        for pattern, vector in step.get("targets", {}).items():
            targets.update({name: vector for name in select([pattern], records)})
        for pattern, vector in step["move"].items():
            moving = select([pattern], records)
            assert set(moving) <= set(shown)
            offsets.update({name: [v*style["explosion_scale"] for v in vector] for name in moving})
            # One direction arrow per repeated component group avoids spaghetti.
            # Choose its screen-right instance, calculated by the Blender camera.
            representative = max(moving, key=lambda n: lookup[n]["pos"][0])
            target = targets.get(representative, [0, 0, 0])
            arrows[representative] = [a-b for a, b in zip(vector, target)]
        active = set(added).union(offsets)
        view = {
            "eye": step.get("eye", style["underside_eye"] if step.get("underside") else style["eye"]),
            "size": style["image_size"],
            "margin": 1.12,
            "include_names": shown,
            "offsets": offsets,
            "muted_names": [],
            "arrow_offsets": {},
        }
        render_style["views"][step["key"]] = view
        step["loose_parts"] = dict(quantities(added, records))
        step["prepared_parts"] = dict(quantities(prepared, records))
        step["added_instances"] = added
        step["shown_instances"] = shown
        cards.append(step)
        consumed.update(added)
    assert consumed == set(lookup), f"Missing instances: {set(lookup)-consumed}"
    total = quantities(list(consumed), records)
    assert sum(total.values()) == manifest["printed_piece_count"]+sum(h["quantity"] for h in manifest["hardware"])+1
    assert set(parts) == set(total), "Missing or unused part label"
    for key in parts:
        names = [r["name"] for r in records if part_key(r) == key]
        if key != "nema17":
            names = names[:1]
        render_style["views"]["part_"+key] = {
            "eye": style["eye"],
            "size": [360, 300],
            "margin": 1.2,
            "include_names": names,
        }
        parts[key]["quantity"] = total[key]
    render_style["views"]["book_cover"] = {
        "eye": [1.2, -1.6, 1.05],
        "size": [1800, 1200],
        "margin": 1.12,
        "include_names": list(lookup),
    }
    (stage/"style.json").write_text(json.dumps(render_style, indent=2))
    data = {
        "style": style,
        "configuration_title": style["title"].format(**c),
        "parts": parts,
        "steps": cards,
        "physical_item_count": sum(total.values()),
        "printed_keys": [piece["name"] for piece in manifest["pieces"]],
        "book": {
            key: [line.format(**c) for line in value] if isinstance(value, list)
            else value.format(**c) if isinstance(value, str) else value
            for key, value in c["assembly_book"].items()
        },
        "source_sha256": production["source_sha256"],
        "recipe_sha256": hashlib.sha256(json.dumps({
            key: c[key] for key in ["assembly_cards", "assembly_card_style", "assembly_part_labels", "assembly_book"]
        }, sort_keys=True).encode()).hexdigest(),
        "generator_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [ROOT/"working_oomp_populate.py", Path(__file__), Path(__file__).with_name("render_studio.py"), Path(__file__).with_name("assembly_booklet.py"), Path(__file__).with_name("assembly_viewer.py"), Path(__file__).with_name("assembly_viewer.html"), ROOT/c["assembly_book"]["logo_svg"]]
        },
        "short_code_method": "OOMP md5_6_alpha: base36(first six hex digits of MD5(UTF-8 identity)). URL formatting does not register a redirect; local identities are explicitly marked.",
    }
    (output/"assembly_manifest.json").write_text(json.dumps(data, indent=2))
    with (output/"parts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["key", "name", "detail", "quantity", "id", "md5_6_alpha", "short_url", "identity_source"])
        writer.writeheader()
        for part in parts.values():
            writer.writerow({k: part.get(k, "") for k in writer.fieldnames})
    return output, data


def fonts():
    for name, filename in [("Assembly", "segoeui.ttf"), ("AssemblyBold", "segoeuib.ttf")]:
        path = Path("C:/Windows/Fonts")/filename
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))
    return ("Assembly", "AssemblyBold") if "Assembly" in pdfmetrics.getRegisteredFontNames() else ("Helvetica", "Helvetica-Bold")


def panel_geometry(style):
    width, height = style["page_mm"]
    columns, rows = style["columns"], style["rows"]
    margin, gap = style["margin_mm"], style["gutter_mm"]
    return (
        (width-2*margin-(columns-1)*gap)/columns,
        (height-2*margin-(rows-1)*gap)/rows,
    )


def publish(**kwargs):
    from wave_drive.assembly_booklet import publish as action
    return action(**kwargs)


def review_outputs(**kwargs):
    from wave_drive.assembly_booklet import review_outputs as action
    return action(**kwargs)


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("render", True)
    kwargs.setdefault("threads", 8)
    output, data = prepare(**kwargs)
    if kwargs["render"]:
        blender = shutil.which("blender")
        if not blender:
            raise RuntimeError("Blender must be on PATH to generate assembly diagrams")
        command = [blender, "--background", "--factory-startup", "-t", str(kwargs["threads"]), "--python-exit-code", "1", "--python", str(Path(__file__).with_name("render_studio.py")), "--", str(output/"render")]
        with (output/"render/blender.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    publish(output=output, data=data)
    review_outputs(output=output, data=data)
    from wave_drive.assembly_viewer import publish as publish_viewer
    publish_viewer(output=output, data=data)
    print("Assembly instructions ready:", output/"assembly_instructions.pdf", flush=True)
    return output
