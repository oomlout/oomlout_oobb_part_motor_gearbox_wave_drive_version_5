"""Clean regeneration and independent named configuration outputs."""
import json
import hashlib
from pathlib import Path
import working
import working_oomp_populate


def test_two_populated_variants_regenerate_from_code(tmp_path):
    configurations = [
        {
            "variant": "proof_a",
            "reduction": 12,
            "base_width": 6,
        },
        {
            "variant": "proof_b",
            "reduction": 8,
            "base_width": 7,
        },
    ]
    folders = working.main(output_root=tmp_path, configurations=configurations, scad_only=True)
    assert len(folders) == 2 and folders[0] != folders[1]
    tracked = {}
    for folder,reduction,width in zip(folders,[12,8],[6,7]):
        manifest=json.loads((folder/"manifest.json").read_text())
        assert manifest["configuration"]["reduction"]==reduction
        assert manifest["configuration"]["base_width"]==width
        assert f"{reduction}:1" in (folder/"ASSEMBLY.md").read_text()
        for name in ["geometry.scad","compact_helpers.scad","oobb_hardware.scad","parameters.scad","motor_fit.scad","exploded_motor.scad","README.md","ASSEMBLY.md","hardware.yaml"]:
            path=folder/name
            assert path.exists()
            tracked[path]=hashlib.sha256(path.read_bytes()).hexdigest()
        assert "C:" not in (folder/"oobb_hardware.scad").read_text()
    working.main(output_root=tmp_path, configurations=configurations, scad_only=True)
    assert all(hashlib.sha256(path.read_bytes()).hexdigest()==digest for path,digest in tracked.items())
    assert not (tmp_path/"presentation").exists()
    assert not (tmp_path/"release").exists()


def test_populate_owns_visuals_and_instructions():
    for option in working_oomp_populate.get_options():
        c=option["oobb_details"]
        assert c["render_style"]["views"]["exploded_motor"]
        assert c["assembly_steps"]
        assert c["run_solidcraft"] is False
