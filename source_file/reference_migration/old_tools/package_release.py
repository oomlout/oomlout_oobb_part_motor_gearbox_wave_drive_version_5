"""Package only the current manifest's print parts, portable SCAD and verified previews."""
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=next((ROOT/"parts").iterdir())
    manifest=json.loads((folder/"manifest.json").read_text())
    report=json.loads((folder/"mesh_validation.json").read_text())
    assert report["status"]=="passed"
    files={}
    for piece in manifest["pieces"]:
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
        "3dpr.scad","3dpr.stl","3dpr.png","fit_coupons.scad","fit_coupons.stl","fit_coupons.png",
        "motor_fit.scad","exploded_motor.scad","motor_reference_parameters.scad","nema17_reference.scad",
    ]
    files.update({name:folder/name for name in names})
    files["ASSEMBLY.md"]=ROOT/"ASSEMBLY.md"
    for name in ["assembly","open_mechanism","exploded_motor","motor_fit","motor_side","parts"]:
        files["renders/"+name+".png"]=ROOT/"presentation/images"/(name+".png")
    for name in ["fastener_validation.json","stock_lengths_validation.json","motor_fit.json"]:
        files["checks/"+name]=ROOT/"presentation"/name
    target=ROOT/"release/wave_drive_12_to_1_print_pack.zip"
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
