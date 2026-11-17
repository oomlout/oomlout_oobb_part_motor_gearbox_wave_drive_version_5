"""Package only the current manifest's print parts, portable SCAD and verified previews."""
import json
import hashlib
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[2]


def main(**kwargs):
    folder = Path(kwargs["part_folder"])
    manifest=json.loads((folder/"manifest.json").read_text())
    report=json.loads((folder/"mesh_validation.json").read_text())
    assert report["status"]=="passed"
    for name,digest in report["source_sha256"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest, name
    render_report = json.loads((folder/"render/validation.json").read_text(encoding="utf-8"))
    for name,digest in render_report["source_sha256"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest, name
    files={}
    for piece in manifest["pieces"]+manifest.get("optional_print_pieces", []):
        for suffix in [".scad",".stl"]:
            name=piece["name"]+suffix
            files[name]=folder/name
    for index in range(1,len(manifest["print_beds"])+1):
        for suffix in [".scad",".stl"]:
            name=f"print_bed_{index:02d}"+suffix
            files[name]=folder/name
    names=[
        "parameters.scad","geometry.scad","compact_helpers.scad","oobb_hardware.scad","manifest.json",
        "hardware.yaml","working.yaml","README.md","validation.txt","mesh_validation.json",
        "assembly.scad","animation.scad","cutaway.scad","exploded.scad","motion_section.scad",
        "3dpr.scad","3dpr.stl","fit_coupons.scad","fit_coupons.stl",
        "motor_fit.scad","exploded_motor.scad","motor_reference_parameters.scad","nema17_reference.scad",
    ]
    files.update({name:folder/name for name in names})
    for name in ["assembly.png","cutaway.png","exploded.png","3dpr.png","motion_section.png","fit_coupons.png"]:
        if (folder/name).exists(): files[name] = folder/name
    files["ASSEMBLY.md"]=folder/"ASSEMBLY.md"
    for name in manifest["configuration"]["render_style"]["views"]:
        path = folder/"render/images"/(name+".png")
        if path.exists() and render_report.get("render_complete",False): files["render/images/"+name+".png"] = path
    for name in ["validation.json","fastener_validation.json","shaft_access_validation.json","assembly_access_validation.json","stock_lengths_validation.json","motor_fit.json","style.json"]:
        path = folder/"render"/name
        if path.exists(): files["render/"+name] = path
    scene = folder/"render/scenes/wave_drive.blend"
    if render_report.get("render_complete",False) and scene.exists():
        files["render/scenes/wave_drive.blend"] = scene
    target=folder/"print_pack.zip"
    instruction_folder = folder/"assembly"
    if manifest["configuration"].get("generate_assembly_cards") and (instruction_folder/"validation.json").exists():
        instruction_manifest = json.loads((instruction_folder/"assembly_manifest.json").read_text())
        c = manifest["configuration"]
        current_recipe_hash = hashlib.sha256(json.dumps({
            key: c[key] for key in ["assembly_cards", "assembly_card_style", "assembly_part_labels", "assembly_book"]
        }, sort_keys=True).encode()).hexdigest()
        assert instruction_manifest["recipe_sha256"] == current_recipe_hash, "Rebuild assembly cards after editing the recipe"
        for name, digest in instruction_manifest["source_sha256"].items():
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest, "Rebuild assembly cards: "+name
        instruction_report = json.loads((instruction_folder/"validation.json").read_text())
        assert instruction_report["status"] == "passed"
        assert hashlib.sha256((instruction_folder/"assembly_instructions.pdf").read_bytes()).hexdigest() == instruction_report["pdf_sha256"]
        if c["assembly_book"].get("viewer_enabled", True):
            html = instruction_folder/"assembly_instructions.html"
            assert hashlib.sha256(html.read_bytes()).hexdigest() == instruction_report["html_sha256"]
            files["assembly/assembly_instructions.html"] = html
        for name in ["assembly_instructions.pdf", "assembly_manifest.json", "parts.csv", "validation.json", "contact_sheet.png"]:
            files["assembly/"+name] = instruction_folder/name
        for path in (instruction_folder/"cards").glob("*.png"):
            files[path.relative_to(folder).as_posix()] = path
        for path in (instruction_folder/"assets").glob("*.svg"):
            files[path.relative_to(folder).as_posix()] = path
    staging=target.with_suffix(".tmp.zip")
    with zipfile.ZipFile(staging,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,path in sorted(files.items()):
            assert path.is_file(),path
            archive.write(path,name)
    with zipfile.ZipFile(staging) as archive:
        assert archive.testzip() is None
        for name,path in files.items():
            assert archive.read(name)==path.read_bytes(),name
    staging.replace(target)
    print("Verified current print pack:",target)


if __name__=="__main__":
    main()
