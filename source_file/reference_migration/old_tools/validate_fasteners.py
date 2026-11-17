"""Check the rendered nominal socket caps and nuts against the actual native SCAD."""
import json
from pathlib import Path
import sys

import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import working_scad


def main():
    folder=next((ROOT/"parts").iterdir())
    records=json.loads((ROOT/"presentation/cache/instances.json").read_text())
    fasteners=[r for r in records if r["kind"]=="fastener"]
    prefix="\n".join(f"include <{(folder/name).as_posix()}>" for name in ["parameters.scad","oobb_hardware.scad","geometry.scad","motor_reference_parameters.scad","nema17_reference.scad"])
    calls=[]
    for r in fasteners:
        mesh=ROOT/"presentation/hardware"/(r["part"]+".stl")
        calls.append(f'multmatrix({json.dumps(r["matrix"])}) import("{mesh.as_posix()}");')
    body=prefix+"\ntranslate([80,0,0]) cube([1,1,1]);\nintersection() { union() { assembly(0); translate([0,0,motor_face_z]) nema17_reference(); } union() {\n"+"\n".join(calls)+"\n} }\n"
    path=ROOT/"presentation/cache/fastener_check.scad"
    path.write_text(body)
    working_scad.render_scad(path,path.with_suffix(".stl"))
    mesh=trimesh.load(path.with_suffix(".stl"),force="mesh")
    # Coplanar contacts may be tilted cylinder facets, not axis-aligned sheets.
    # Reject only rank-2 surfaces; retain every genuine 3D interference.
    pieces = mesh.split(only_watertight=False)
    solids = [p for p in pieces if np.linalg.svd(p.vertices-p.vertices.mean(axis=0),compute_uv=False)[-1]>1e-7]
    passed=len(solids)==1 and np.allclose(solids[0].bounds,[[80,0,0],[81,1,1]],atol=1e-5)
    report={
        "status":"passed" if passed else "failed",
        "fastener_instances":len(fasteners),
        "planar_contact_fragments":len(pieces)-len(solids),
        "volumetric_components":[{"bounds_mm":p.bounds.tolist(),"volume_mm3":float(p.volume)} for p in solids],
        "scope":"Nominal screw and nut envelopes against every native gearbox body and the full motor at input angle zero; intended motor thread engagement uses smooth nominal bores.",
    }
    (ROOT/"presentation/fastener_validation.json").write_text(json.dumps(report,indent=2))
    assert passed, report
    print(f"PASS: {len(fasteners)} socket-cap/grub/nut envelopes clear the native gearbox.")


if __name__=="__main__":
    main()
