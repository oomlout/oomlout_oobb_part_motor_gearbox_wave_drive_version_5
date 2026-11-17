"""Single-file offline viewer, generated from the audited assembly inventory."""
import base64
import copy
import hashlib
import html
import json
from pathlib import Path


def publish(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    output = Path(kwargs["output"])
    data = kwargs["data"]
    book = data["book"]
    if not book.get("viewer_enabled", True):
        return

    def embedded(path):
        return "data:image/png;base64,"+base64.b64encode(path.read_bytes()).decode("ascii")

    images = {}
    slides = []
    for index, page in enumerate(data["book_pages"], 1):
        if page["kind"] not in ["cover", "details", "parts", "back"]:
            continue
        name = page["kind"]
        images[name] = embedded(output/"pages"/f"page_{index:02d}.png")
    slides.extend([
        {"id": "cover", "label": "Cover", "image": "cover", "mode": "page"},
        {"id": "details", "label": "Project details", "image": "details", "mode": "page"},
    ])
    for step in data["steps"]:
        key = step["key"]
        images[key] = embedded(output/"render/raw"/(key+".png"))
        slides.append({
            "id": key.replace("_", "-"),
            "label": "Step "+str(step["number"]),
            "number": step["number"],
            "image": key,
            "mode": "step",
            "description": step["action"],
            "parts": step["loose_parts"],
        })
    if book["summary_step"]:
        number = len(data["steps"])+1
        images["complete"] = embedded(output/"render/raw"/(book["summary_view"]+".png"))
        slides.append({"id": f"step-{number:02d}", "label": f"Step {number}", "number": number, "image": "complete", "mode": "step", "parts": {}, "description": "Completed gearbox with NEMA 17 motor."})
    slides.extend([
        {"id": "parts", "label": "Parts list", "image": "parts", "mode": "page"},
        {"id": "back", "label": "Back cover", "image": "back", "mode": "page"},
    ])
    parts = {}
    for key, part in data["parts"].items():
        images["part_"+key] = embedded(output/"render/raw"/("part_"+key+".png"))
        parts[key] = {k: part[k] for k in ["name", "short_url", "md5_6_alpha"] if k in part}
    payload = {
        "slides": slides,
        "images": images,
        "parts": parts,
        "start": book["viewer_start"],
    }
    template = Path(__file__).with_name("assembly_viewer.html").read_text(encoding="utf-8")
    result = template.replace("__TITLE__", html.escape(book["cover_title"]+" | Assembly instructions"))
    result = result.replace("__PROJECT_URL__", html.escape(book["project_url"], quote=True))
    result = result.replace("__DATA__", json.dumps(payload, separators=(",", ":")).replace("<", "\\u003c"))
    target = output/"assembly_instructions.html"
    target.write_text(result, encoding="utf-8")
    report_path = output/"validation.json"
    report = json.loads(report_path.read_text())
    report["html_sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    report["html_slides"] = len(slides)
    report["html_steps"] = sum(s["mode"] == "step" for s in slides)
    report["html_self_contained"] = True
    report_path.write_text(json.dumps(report, indent=2))
