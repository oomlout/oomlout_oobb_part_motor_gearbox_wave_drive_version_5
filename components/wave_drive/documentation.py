"""Deterministic part-local instructions and drawing captions from the populated recipe."""
import copy
import json
from pathlib import Path


def generate(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    folder = Path(kwargs["part_folder"])
    manifest = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
    c = manifest["configuration"]
    viewer = c["assembly_book"]["viewer_url"]
    rows = [
        f"# {c['reduction']}:1 OOBB roller wave drive",
        "",
        f"One bank of {c['roller_count']} nylon spacers, {c['roller_diameter']:g} mm OD x {c['roller_length']:g} mm deep. Output speed is -1/{c['reduction']} of input speed. One 6810 supports the output; one 6704 supports the wave wheel.",
        "",
        f"[Assembly instructions in your browser]({viewer}) · [PDF booklet](assembly/assembly_instructions.pdf) · [Written sequence](ASSEMBLY.md)",
        "",
        f"The {c['base_width']} x {c['base_height']} OOBB base has M6 and M3 holes, {c['housing_flange_corner_radius']:g} mm corner radii and {c['base_edge_radius']:g} mm rounded edges. The main housing is {2*c['housing_radius']:g} mm OD. Reference motor: {c['motor_body_depth']:g} mm NEMA 17 body, plain round {c['input_shaft_diameter']:g} mm shaft, {c['motor_shaft_length']:g} mm long.",
        "",
        "## Wiggle shaft",
        "",
        f"Both eccentric pieces split at Z={c['cam_cap_z']:g} mm, the centre of the 6704 bearing. Align the small semicircular edge marks on the two collars.",
        "",
        f"Load the upper radial M3 nut from the top and tighten the M3 x {c['shaft_clamp_screw_length']} countersunk clamp onto the motor shaft before fitting the fixed ring and upper cage. The case and lower cage have no adjustment access holes. Two M3 x {c['eccentric_join_screw_length']} countersunk screws join the short eccentric to its lower captive nuts.",
        "",
        f"Optional extended version: [motor_eccentric_cap_extended.stl](motor_eccentric_cap_extended.stl) sits on the standard upper collar. Its {c['extended_eccentric_diameter']:g} mm stem reaches the output face at Z={c['assembly_height']:g} mm, with clearance through the {c['output_view_diameter']:g} mm viewing hole. Use two M3 x {c['extended_eccentric_screw_length']} socket caps instead of the short version's countersunk joiners. Reuse the lower piece and captive nuts. See [assembly_extended.scad](assembly_extended.scad). Fit the shaft clamp nut before adding the lifter.",
        "",
        "## Output plate",
        "",
        f"The flat-sided output face is {c['output_plate_diameter']:g} mm OD with a {c['output_view_diameter']:g} mm central viewing hole. It has no overhanging outer lip; the bearing remains visible. The output face stays {c['output_above_housing']:g} mm above the housing.",
        "",
        f"Preassemble the carrier and cover with two M3 x {c['output_plate_clamp_screw_length']} countersunk screws and separate captive M3 nuts. Then attach the complete sandwich to the cage with four M3 x {c['output_screw_length']} countersunk screws. The short screws stay in place while installing or removing the plate.",
        "",
        f"The carrier holds {c['output_m3_mount_count']} M3 attachment nuts on the OOBB half-grid. The carrier also holds {c['output_m6_mount_count']} M6 nuts with their flats toward the centre. M6 holes remain in the base. M3 centres in mm: {c['output_m3_mounts']}. M6 centres in mm: {c['output_m6_mounts']}.",
        "",
        f"Clearance holes continue below the attachment nuts through the carrier and cage. M3 payload bolt projection below the output face may be {c['output_m3_bolt_projection_min']:.2f} to {c['output_m3_bolt_projection_max']:.2f} mm, allowing at least 2 mm thread engagement while stopping above the moving wave screws. Measure the actual printed assembly; longer bolts must not reach the moving parts.",
        "",
        "## Printing and assembly",
        "",
        f"Print the {manifest['printed_piece_count']} required gearbox pieces. The combined 3dpr file and print beds also include {c['roller_count']} optional printable spacers and the optional separate shaft lifter. Fit the lifter for the tall option. Choose either purchased nylon spacers or printed spacers. Bearings, motor and fasteners are purchased items.",
        "",
        "Print the lower cage with its teeth upward and the upper cage with its hub face on the bed and its 45-degree shoulder widening upward. Inspect bridge material, bearing seats and the orientation marks before assembly. The upper and lower cage have annular clearances for the raised M3 wave and motor screw heads.",
        "",
        f"M3 axial countersunk heads sit {c['countersunk_head_proud']:g} mm proud; do not force them flush. M2 cage screws stay seated, with {c['cage_tip_clearance']:g} mm nominal tip clearance. The radial shaft clamp tightens onto the shaft. Motor screws retain {c['motor_thread_engagement']:g} mm nominal thread engagement. Socket-cap lengths exclude the head; countersunk lengths include it.",
        "",
        "![Motor assembly](render/images/motor_fit.png)",
        "",
        "![Exploded assembly](render/images/exploded_motor.png)",
        "",
        "## Hardware",
        "",
        "Quantities below are for the short-shaft assembly. The extended option replaces its two eccentric joiners with two M3 x 35 socket caps.",
        "",
        "| Item | Quantity | Size / length |",
        "| --- | ---: | --- |",
    ]
    for item in manifest["hardware"]:
        dimension = item.get("dimensions", (item.get("size", "")+" x "+str(item["length_mm"])+" mm") if "length_mm" in item else "")
        rows.append(f"| {item['item']} | {item['quantity']} | {dimension} |")
    rows += ["", "## Verification", "", "See mesh_validation.json and the reports in render/ for the checks actually performed. This single-bank design is not counterbalanced. Printed fit, clamp grip, wear, backlash, motor bearing loads and operating speed/torque still need physical testing.", ""]
    (folder/"README.md").write_text("\n".join(rows),encoding="utf-8")
    assembly = [f"# Assembly - {c['reduction']}:1 wave drive", "", "AI-generated images and instructions. Errors possible.", "", f"[Open the browser instructions]({viewer}) · [Print the booklet](assembly/assembly_instructions.pdf)", "", "The diagrams show the short eccentric. For the extended option, place the lifter on the standard upper collar and use two M3 x 35 socket caps at the eccentric closing step. Tighten the upper shaft clamp before installing the outer case. Prepare the complete output sandwich before installing it.", ""]
    for index, step in enumerate(c["assembly_cards"],1):
        assembly += [f"## {index:02d}. {step['title']}", "", step["action"].format(**c), "", f"[![AI-generated assembly step {index}](assembly/cards/step_{index:02d}.png)](assembly/cards/step_{index:02d}.png)", ""]
    assembly += [f"M3 payload bolt projection below the output face: {c['output_m3_bolt_projection_min']:.2f} to {c['output_m3_bolt_projection_max']:.2f} mm. Check the actual print before fitting longer bolts.", ""]
    (folder/"ASSEMBLY.md").write_text("\n".join(assembly),encoding="utf-8")
    checks = [name+": see report for scope" for name in ["mesh_validation.json","render/fastener_validation.json","render/motor_fit.json","render/shaft_access_validation.json","render/extended_eccentric_validation.json"] if (folder/name).exists()]
    (folder/"validation.txt").write_text("\n".join(checks)+"\n",encoding="utf-8")


def captions(**kwargs):
    manifest = kwargs["manifest"]
    c = manifest["configuration"]
    n = manifest["printed_piece_count"]
    fasteners = sum(row["quantity"] for row in manifest["hardware"] if row["item"] not in ["6810 bearing","6704 bearing","Nylon spacer roller"])
    return {
        "assembly": {
            "title": f"{c['reduction']}:1 OOBB roller wave gearbox",
            "subtitle": f"Flat output plate: {c['output_view_diameter']:g} mm viewing hole, {c['output_m6_mount_count']} captive M6 nuts and {c['output_m3_mount_count']} captive M3 nuts.",
            "footer": f"{2*c['housing_radius']:g} mm body OD | {c['output_plate_diameter']:g} mm output face | one 6810 + one 6704",
        },
        "motor_fit": {
            "title": "OOBB wave drive on the NEMA 17",
            "subtitle": f"{c['motor_body_depth']:g} mm motor; recessed black output face {c['output_above_housing']:g} mm above the teal housing.",
            "footer": f"{c['base_width']} x {c['base_height']} OOBB base | {c['housing_flange_corner_radius']:g} mm corners | M6 and M3 mounting holes",
        },
        "motor_side": {
            "title": "Motor and output | side elevation",
            "subtitle": f"{c['assembly_height']:g} mm gearbox height above the motor face. Input supported by motor bearings.",
            "footer": "Upper bearing supports the output cage. Motor load capacity remains untested.",
        },
        "exploded_motor": {
            "title": "OOBB wave drive | exploded with motor",
            "subtitle": f"{c['roller_count']} nylon rollers, {c['roller_diameter']:g} x {c['roller_length']:g} mm. Expanded spacing separates both bearing clamshells.",
            "footer": f"{n} printed pieces | 2 bearings | {fasteners} screws and nuts | populated configuration: {c.get('variant','default')}",
        },
        "exploded": {
            "title": "The complete output and roller stack",
            "subtitle": f"{n} printed pieces, {c['roller_count']} nylon rollers and two bearings. Full output plate above.",
            "footer": "One bank | short and extended input options | independently clamped output plate",
        },
        "open_mechanism": {
            "title": "Inside the roller wave drive",
            "subtitle": f"{c['roller_count']} nylon rollers follow the eccentric wave wheel. Upper cage and cover hidden.",
            "footer": f"7 mm OD rollers | {c['reduction']}:1 reverse output | motor-supported input",
        },
        "parts": {
            "title": "Required gearbox parts",
            "subtitle": f"{n} printed instances on {len(manifest['print_beds'])} beds. Purchased hardware is excluded.",
            "footer": "Production SCAD meshes | printing orientations shown | fit coupons provided separately",
        },
    }
