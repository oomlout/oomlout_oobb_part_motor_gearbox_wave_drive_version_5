"""Cream technical sheets using the cycloidal presentation's palette and type."""
import copy
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size, bold=False):
    return ImageFont.truetype(str(Path("C:/Windows/Fonts")/("segoeuib.ttf" if bold else "segoeui.ttf")), size)


def publish(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("folder", Path(__file__).resolve().parent)
    folder = Path(kwargs["folder"])
    style = json.loads((folder/"style.json").read_text())
    (folder/"images").mkdir(exist_ok=True)
    from wave_drive.documentation import captions
    manifest = json.loads((Path(kwargs["part_folder"])/"manifest.json").read_text(encoding="utf-8"))
    items = captions(manifest=manifest)
    definitions = [{"key":key, **items[key]} for key in style["views"]]
    for item in definitions:
        raw = Image.open(folder/"raw"/(item["key"]+".png")).convert("RGBA")
        size = (1600, 2080) if item["key"] == "exploded_motor" else (1600, 1790) if item["key"] in ["exploded", "motor_side"] else (1600, 1540) if item["key"] == "motor_fit" else (1600, 1360)
        size = tuple(style["views"][item["key"]].get("sheet_size", size))
        page = Image.new("RGB", size, "white")
        draw = ImageDraw.Draw(page)
        draw.text((48, 26), item["title"], font=font(46, True), fill="#222625")
        draw.text((50, 99), item["subtitle"], font=font(25), fill="#59615F")
        box = (45, 160, 1510, size[1]-280)
        x, y, width, height = box
        scale = min(width/raw.width, height/raw.height)
        raw = raw.resize((round(raw.width*scale), round(raw.height*scale)), Image.Resampling.LANCZOS)
        page.paste(Image.new("RGB", (width, height), style["background"]), (x, y))
        page.paste(raw, (x+(width-raw.width)//2, y+(height-raw.height)//2), raw)
        draw.text((50, size[1]-112), item["footer"], font=font(23), fill="#59615F")
        draw.text((48, size[1]-47), "OpenSCAD geometry · Blender Cycles studio · Prototype: physical fit and load testing pending.", font=font(22), fill="#59615F")
        page.save(folder/"images"/(item["key"]+".png"))


if __name__ == "__main__":
    publish()
