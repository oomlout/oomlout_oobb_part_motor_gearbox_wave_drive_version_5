"""Project landing README and complete build notes from the populated recipe."""
import copy
import json
import re
from pathlib import Path
from PIL import Image, ImageOps
from working_oomp_populate import define_project_readme


def generate(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    root, folder = Path(kwargs["output_root"]), Path(kwargs["part_folder"])
    manifest = json.loads((folder/"manifest.json").read_text())
    c = manifest["configuration"]
    book = {k:v.format(**c) if isinstance(v,str) else v for k,v in c["assembly_book"].items()}
    rel = folder.relative_to(root).as_posix()
    viewer = book["viewer_url"]
    thumbs = folder/"assembly/readme"
    thumbs.mkdir(parents=True, exist_ok=True)
    for image_name in ["motor_fit", "exploded_motor"]:
        source = folder/"render/images"/(image_name+".png")
        if source.exists():
            ImageOps.contain(Image.open(source), (480,480)).save(thumbs/(image_name+".png"))
    kwargs.setdefault("readme", define_project_readme())
    page = kwargs["readme"]
    inspiration = page["inspiration"]
    rows = [
        f"# {page['title']}",
        "",
        page["description"],
        "",
        f"Inspired by [{inspiration['creator']}]({inspiration['creator_url']}) and their video [{inspiration['title']}]({inspiration['video_url']}).",
        "",
        page["ai_notice"],
        "",
        "> AI-generated CAD images and instructions. Errors possible.",
        "",
        "## Versions",
        "",
        "Open **HTML assembly instructions** to view the full-screen steps directly in your browser. Use **PDF download** for the printable booklet.",
        "",
        "| Image | Version and description | Main README | HTML assembly instructions | PDF download |",
        "| --- | --- | --- | --- | --- |",
    ]
    for version in page["versions"]:
        rows.append(
            f"| [![AI-generated CAD render: {version['name']}]({version['image']})]({version['html']}) "
            f"| **{version['name']}**<br>{version['description']} "
            f"| [README]({version['readme']}) "
            f"| [Open in browser]({version['html']}) "
            f"| [Download PDF]({version['pdf']}) |"
        )
    rows.append("")
    (root/"README.md").write_text("\n".join(rows), encoding="utf-8")

    def root_links(value):
        def substitute(match):
            link = match.group(1)
            if link.startswith(("http:", "https:", "#")):
                return match.group(0)
            return "]("+rel+"/"+link+")"
        return re.sub(r"\]\(([^)]+)\)", substitute, value)

    part_notes = (folder/"README.md").read_text(encoding="utf-8").split("\n",1)[1]
    instructions = (folder/"ASSEMBLY.md").read_text(encoding="utf-8").split("\n",1)[1]
    lines = [
        "# Wave drive - design and assembly",
        "",
        f"[Full-screen HTML instructions]({viewer}) · [PDF booklet]({rel}/assembly/assembly_instructions.pdf) · [Project overview](README.md)",
        "",
        "## Regenerate",
        "",
        "Edit `working_oomp_populate.py`. The standard build runs `working_oomp_populate` -> `working_oomp` -> `working_scad`, then generates the drawings, meshes, Blender renders, PDF, standalone HTML and these READMEs. No AI session is needed to rebuild.",
        "",
        "```powershell",
        "python working.py",
        "python working.py --scad-only     # editable drawings without mesh export",
        "python working.py --no-renders    # meshes and checks without Blender",
        "python working.py --assembly-only # instructions from validated meshes",
        "python -m pytest -q",
        "```",
        "",
        "Python regeneration needs the installed OOBB/OOMP packages, `requirements.txt`, OpenSCAD with its Manifold backend and Blender on PATH. Generated SCAD is portable. Use `get_options()` for named configurations; all configuration-specific output stays inside its `parts/<part-id>/` folder.",
        "",
        "The published HTML is served from this repository's `gh-pages` branch. `components/wave_drive/publish_github.py` republishes the generated viewer and PDF; it does not regenerate CAD.",
        "",
        "## Design details",
        root_links(part_notes),
        "",
        "## Assembly instructions",
        root_links(instructions),
    ]
    (root/"README_DETAILS.md").write_text("\n".join(lines), encoding="utf-8")
