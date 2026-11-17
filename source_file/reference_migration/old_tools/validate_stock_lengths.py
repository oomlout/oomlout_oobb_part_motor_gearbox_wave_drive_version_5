"""Check stock choices against the compact motor stack; record rejected lengths."""
import json
from pathlib import Path
import sys
import numpy as np
import trimesh
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import working_scad


def main():
    folder = next((ROOT/"parts").iterdir())
    target = ROOT/"presentation/cache/compact_stock_lengths"
    target.mkdir(parents=True, exist_ok=True)
    report = []
    for length in [6,12,15,18,20,25,30]:
        result = {
            "roller_length_mm": length,
            "scope": "Compact motor stack; only 12 mm is the release default",
        }
        try:
            c = working_scad.resolve(roller_length=length)
        except ValueError as error:
            result["status"] = "rejected_by_stack_constraints"
            result["reason"] = str(error)
            report.append(result)
            continue
        result["angles"] = []
        for angle in [0,45]:
            path = target/f"collision_L{length}_a{angle}.stl"
            working_scad.render_scad(folder/"collision_check.scad",path,options=["-D",f"roller_length={length}","-D",f"check_angle={angle}"])
            mesh = trimesh.load(path, force="mesh")
            solids = [piece for piece in mesh.split(only_watertight=False) if min(piece.extents)>1e-7]
            assert len(solids)==1 and np.allclose(solids[0].bounds,[[70,0,0],[71,1,1]],atol=1e-5), (length,angle)
            result["angles"].append({
                "input_angle": angle,
                "interference_mm3": 0,
            })
        result["status"] = "geometry_passed"
        result["assembly_height_mm"] = c["assembly_height"]
        report.append(result)
    (ROOT/"presentation/stock_lengths_validation.json").write_text(json.dumps(report,indent=2))
    print("Stock-length checks:", [(r["roller_length_mm"],r["status"]) for r in report])


if __name__ == "__main__":
    main()
