"""Project landing README and complete build notes from the populated recipe."""
import copy
import json
import re
from pathlib import Path
from PIL import Image, ImageOps


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
    rows = [
        f"# {book['cover_title']} - {book['cover_subtitle']}",
        "",
        f"**[Open the full-screen assembly instructions]({viewer})**",
        "",
        f"[PDF booklet]({rel}/assembly/assembly_instructions.pdf) · [Download the standalone HTML]({book['project_url']}/raw/refs/heads/main/{rel}/assembly/assembly_instructions.html) · [Full details and written instructions](README_DETAILS.md)",
        "",
        "> AI-generated CAD images and instructions. Errors possible.",
        "",
        "## Summary",
        "",
        book["project_summary"],
        "",
        "This is an entirely AI-generated coding project. Generated outputs are included and generally run, but the main purpose of publishing is to provide a starting point for modification with your own AI tools. Physical fit, wear, speed and load capacity have not been tested.",
        "",
        f"[![AI-generated CAD render of the assembled gearbox and motor]({rel}/assembly/readme/motor_fit.png)]({viewer})",
        "",
        "## Details",
        "",
        f"The gearbox uses one 6810 output bearing, one 6704 wave bearing and a {c['motor_body_depth']:g} mm NEMA 17 body. Its centred {c['base_width']} x {c['base_height']} OOBB base has M6 grid holes and M3 half-grid holes. The output face carries captive M6 and M3 nuts.",
        "",
        f"[Printable files and SCAD source]({rel}/) · [Dimensions, regeneration and assembly](README_DETAILS.md)",
        "",
        "## Parts",
        "",
        f"Print the {manifest['printed_piece_count']} gearbox parts. The combined `3dpr` file and print-bed layouts also contain {c['roller_count']} optional spacers: {c['roller_diameter']:g} mm OD x {c['roller_length']:g} mm depth, {c['roller_bore_diameter']:g} mm bore. Use these **or** purchased nylon spacers. Do not fit both sets.",
        "",
        f"[Boxed parts list]({viewer}#parts) · [Hardware quantities and print options](README_DETAILS.md#hardware)",
        "",
        f"[![AI-generated exploded CAD view with motor]({rel}/assembly/readme/exploded_motor.png)]({rel}/render/images/exploded_motor.png)",
        "",
        "## Assembly",
        "",
        f"[Start at step 1]({viewer}#step-01). Each screen shows one step and the parts needed. Use the arrow keys, swipe or the step selector; choose **Full screen** for the largest view. The downloaded HTML works offline with all images included.",
        "",
        f"For paper instructions, use the [eight-page A4 landscape PDF]({rel}/assembly/assembly_instructions.pdf). For preparation, screw lengths, shaft-clamp access and the complete written sequence, use the [detailed README](README_DETAILS.md#assembly-instructions).",
        "",
    ]
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
