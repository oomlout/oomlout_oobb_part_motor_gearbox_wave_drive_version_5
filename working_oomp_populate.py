"""Editable recipe: populate -> working_oomp -> working_scad. Units are mm."""
import copy
from pathlib import Path

import yaml
from oomp_populate_helper import build_oomp_id

ROOT = Path(__file__).resolve().parent


def define(**kwargs):
    option = {
        "style": "version_5",
        "reduction": 12,
        "bearing_output": "6810",
        "bearing_wave": "6704",
        "roller_diameter": 7.0,
        "roller_bore_diameter": 3.2,
        "roller_length": 12.0,
        "roller_lengths_available": [6, 12, 15, 18, 20, 25, 30],
        "roller_material": "nylon",
        "include_printable_spacers": True,
        "roller_bank_count": 1,
        "motor_plate_depth": 4.0,
        "motor_screw_length": 8,
        "case_screw_length": 30,
        "case_socket_recess": 3.6,
        "case_nut_z": 0.1,
        "motor_body_depth": 40.0,
        "motor_shaft_length": 24.0,
        "motor_hole_pitch": 31.0,
        "motor_thread_depth": 6.0,
        "motor_pilot_diameter": 22.0,
        "motor_pilot_height": 2.0,
        "output_holder_wall": 3.0,
        "case_boss_wall": 2.0,
        "case_boss_rounding_fraction": 1.0,
        "case_boss_overlap": 1.5,
        "max_screw_length": 35.0,
        "eccentricity": 0.75,
        "wave_radius": 23.25,
        "profile_clearance": 0.15,
        "roller_slot_clearance": 0.30,
        "roller_end_clearance": 0.30,
        "cage_wall": 5.0,
        "cage_plate_depth": 3.0,
        "cage_center_diameter": 25.0,
        "cage_screw_radial_offset": -0.5,
        "cage_screw_length": 20,
        "cage_screw_reference_length": 18,
        "cage_tip_extra_clearance": 1.0,
        "shaft_clamp_screw_length": 8,
        "shaft_clamp_head_radius": 10.5,
        "shaft_clamp_axis_z": 5.8,
        "shaft_access_diameter": 2.6,
        "shaft_driver_diameter": 2.4,
        "bearing_seat_clearance": 0.10,
        "journal_clearance": 0.05,
        "bearing_axial_clearance": 0.20,
        "output_plate_diameter": 65.0,
        "output_cover_depth": 4.3,
        "output_above_housing": 1.5,
        "output_hub_depth": 2.1,
        "output_grid_pitch": 15.0,
        "output_fixing_x": 20.0,
        "output_fixing_y": 10.0,
        "output_face_clearance": 0.80,
        "output_radial_clearance": 0.60,
        "output_socket_recess": 3.2,
        "output_screw_length": 12,
        "output_nut_depth": 5.2,
        "output_nut_height": 5.0,
        "output_m3_nut_depth": 2.7,
        "output_m3_nut_height": 2.5,
        "mount_minimum_web": 0.9,
        "mount_m3_pocket_radius": 3.70,
        "mount_m3_hex_radius": 3.462,
        "mount_m3_bridge_half_width": 1.75,
        "mount_m3_bridge_half_height": 3.25,
        "mount_m3_edge_wall": 0.50,
        "mount_m6_pocket_radius": 5.92,
        "motor_shaft_end_clearance": 0.5,
        
        "base_width": 7,
        "base_height": 5,
        "oobb_grid_pitch": 15.0,
        "oobb_size_allowance": 1.0,
        "base_edge_radius": 1.5,
        "housing_flange_corner_radius": 5.0,
        "housing_screw_pitch_radius": 38.3,
        "housing_screw_count": 6,
        "housing_screw_angle": 30.0,
        "input_shaft_diameter": 5.0,
        "input_shaft_flat_depth": 0.0,  # Zero gives a plain round motor shaft.
        "shaft_fit_clearance": 0.10,
        "eccentric_join_screw_length": 16,
        "eccentric_join_pitch_radius": 6.75,
        "wave_screw_length": 12,
        "exploded_spacing": 24.0,
        "profile_samples_per_cavity": 100,
        "circle_fragments": 120,
        "overhang": True,
        "run_scad": True,
        "run_solidcraft": False,
        "generate_stl": True,
        "generate_previews": True,
        "generate_renders": True,
        "package_outputs": False,
        "render_threads": 8,
        "render_style": define_render_style(),
        "assembly_steps": define_assembly_steps(),
        "generate_assembly_cards": True,
        "assembly_card_style": define_assembly_card_style(),
        "assembly_cards": define_assembly_cards(),
        "assembly_part_labels": define_assembly_part_labels(),
        "assembly_book": define_assembly_book(),
    }
    option.update(copy.deepcopy(kwargs))
    return option


def get_options(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    # Add further named configurations here; each owns a separate parts directory.
    kwargs.setdefault("configurations", [
        {
            "variant": "default",
            "reduction": 12,
            "roller_length": 12.0,
            "base_width": 7,
            "base_height": 5,
        },
    ])
    configurations = kwargs.pop("configurations")
    options = []
    for configuration in configurations:
        settings = copy.deepcopy(configuration)
        settings.update(copy.deepcopy(kwargs))
        option = define(**settings)
        option["taxonomy_1"] = "oobb"
        option["taxonomy_2"] = "part"
        option["taxonomy_3"] = "motor_gearbox"
        option["taxonomy_4"] = "wave_drive"
        option["taxonomy_5"] = option["style"]
        variant = option.get("variant", "default")
        if not variant.replace("_", "").isalnum():
            raise ValueError("Variant names must use letters, numbers and underscores")
        option["taxonomy_6"] = f"{option['reduction']}_to_1_reduction" + ("" if variant == "default" else "_"+variant)
        option["oobb_type"] = "wave_drive"
        details = copy.deepcopy(option)
        details["oobb_name"] = option["style"]
        option["oobb_details"] = details
        option["id"] = build_oomp_id(option)
        options.append(option)
    if len({item["id"] for item in options}) != len(options):
        raise ValueError("Every populated configuration needs a unique variant name")
    return options


def main(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("output_root", ROOT)
    output_root = Path(kwargs.pop("output_root"))
    options = get_options(**kwargs)
    for option in options:
        folder = output_root / "parts_source" / option["id"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "working.yaml").write_text(
            yaml.safe_dump(option, sort_keys=False), encoding="utf-8"
        )

    return options


def define_project_readme(**kwargs):
    """Landing page content; append one entry per published design version."""
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("title", "Wave drive")
    kwargs.setdefault("description", "A 3D-printable roller wave gearbox for a NEMA 17 motor, with OOBB mounting holes on the base and output face. An eccentric wheel drives a cage through a ring of nylon rollers. This repository includes editable Python/OpenSCAD source, printable files and illustrated assembly instructions.")
    kwargs.setdefault("inspiration", {
        "creator": "Mishin Machine",
        "creator_url": "https://www.youtube.com/@MishinMachine",
        "title": "Wave Drive with Rolling Elements — Cycloidal Gear Alternative!",
        "video_url": "https://www.youtube.com/watch?v=zOLQw-TxE7s",
    })
    kwargs.setdefault("ai_notice", "This is an entirely AI-generated coding project. The source code is largely unreadable by humans, but usable generated files are included. It is published so others can use their own AI tools to understand, modify and regenerate the design. Physical fit, wear, speed and load capacity have not been tested.")
    kwargs.setdefault("versions", [
        {
            "name": "12:1 / NEMA 17",
            "description": "Single roller bank; twelve 7 mm OD × 12 mm spacers; 6810 output bearing and 6704 wave bearing; 7 × 5 OOBB base. Includes optional printable spacers.",
            "image": "parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/assembly/readme/motor_fit.png",
            "readme": "parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/README.md",
            "html": "https://oomlout.github.io/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/",
            "pdf": "https://github.com/oomlout/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/raw/refs/heads/main/parts/oobb_part_motor_gearbox_wave_drive_version_5_12_to_1_reduction/assembly/assembly_instructions.pdf",
        },
    ])
    return kwargs


def define_render_style(**kwargs):
    settings = {'provenance': 'OOBB SCAD meshes with the retained cream/teal/black/yellow studio '
                   'palette.',
     'samples': 48,
     'view_transform': 'AgX',
     'world_color': [0.77, 0.79, 0.81, 1.0],
     'world_strength': 0.48,
     'background': '#FAF8F2',
     'materials': {'nylon': {'name': 'Natural nylon spacers',
                             'color': 'E9E5D8',
                             'roughness': 0.48,
                             'metallic': 0.0},
                   'teal': {'name': 'Turquoise 10605',
                            'color': '00B1B7',
                            'roughness': 0.4,
                            'metallic': 0.0},
                   'black': {'name': 'Black 10101',
                             'color': '121212',
                             'roughness': 0.39,
                             'metallic': 0.0},
                   'yellow': {'name': 'Sunflower 10402',
                              'color': 'FEC601',
                              'roughness': 0.4,
                              'metallic': 0.0},
                   'steel': {'name': 'Bearing and nut steel',
                             'color': 'BFC5C9',
                             'roughness': 0.26,
                             'metallic': 0.88},
                   'bolt': {'name': 'Oxidised screw steel',
                            'color': '575D63',
                            'roughness': 0.31,
                            'metallic': 0.81}},
     'lights': [{'offset': [70, 25, 185], 'power': 370000, 'size': 130},
                {'offset': [-100, 60, 95], 'power': 190000, 'size': 110},
                {'offset': [10, -140, 105], 'power': 300000, 'size': 95},
                {'offset': [135, 160, 35], 'power': 110000, 'size': 140}],
     'views': {'assembly': {'eye': [0.86, 1.4, 0.87], 'size': [1510, 1080], 'margin': 1.12},
               'open_mechanism': {'eye': [0.65, 1.4, 1.9],
                                  'size': [1510, 1080],
                                  'margin': 1.12},
               'exploded': {'eye': [0.45, 1.4, 0.65],
                            'size': [1600, 3200],
                            'sheet_size': [1600, 3400],
                            'margin': 1.12,
                            'spacing': 24},
               'parts': {'eye': [0.25, -0.7, 2.3], 'size': [1510, 1080], 'margin': 1.1},
               'motor_fit': {'eye': [0.86, 1.4, 0.5], 'size': [1510, 1260], 'margin': 1.15},
               'motor_side': {'eye': [0, 1, 0], 'size': [1100, 1300], 'margin': 1.18},
               'exploded_motor': {'eye': [0.45, 1.4, 0.55],
                                  'size': [1600, 3600],
                                  'sheet_size': [1600, 3800],
                                  'margin': 1.12,
                                  'spacing': 24}}}
    settings.update(copy.deepcopy(kwargs))
    return settings


def define_assembly_steps(**kwargs):
    return [
        "Print the fit coupons. Check the 6810 seat, 6704 seat, motor shaft, roller windows and OOBB nut pockets before the full build.",
        "Load six M3 case nuts into the underside of the base. Mount the {motor_body_depth:g} mm NEMA 17 with four M3 x {motor_screw_length} countersunk screws, heads flush with the plate. Confirm {motor_thread_engagement:g} mm engagement fits the motor threads.",
        "Print cage_lower_cap with its teeth upright. Print output_cage with its broad closure face on the bed and integrated hub upward; inspect the bridge over its central blind recess. The cage rings remain {cage_plate_depth:g} mm thick to support the captive nuts and service bore.",
        "Seat {cage_screw_count} M2 nuts in the underside of the lower cage, one for each tooth, and lower it around the motor shaft. Its {cage_center_diameter:g} mm centre opening can also pass over the already fitted eccentric shaft and collars; fit the 6704 and rolling clamshells afterwards. Align its radial service hole along +X.",
        "Preload two M3 nuts into the underside of the lower eccentric and an M3 nut into its radial pocket. Preload the M3 x {shaft_clamp_screw_length} countersunk shaft-clamp screw before closing the gearbox; its head has top clearance, so the tip can tighten onto the motor shaft. Fit the eccentric at Z={cam_base_z:g} mm with the clamp facing +X.",
        "Load four M3 nuts into the lower 6704 clamshell (wave_generator), slide it over the eccentric journal and seat the 6704. The joint is at Z={wave_split_z:g} mm, exactly through the bearing centre; each half encloses 2 mm of bearing width plus its fit clearance.",
        "Fit the upper eccentric collar and join it to the lower eccentric using two M3 x {eccentric_join_screw_length} countersunk screws and the preloaded nuts. These lengths include the head. Both heads sit flush; the journal shoulders preserve the bearing axial clearance.",
        "Close the upper 6704 clamshell (wave_bearing_cap) with four M3 x {wave_screw_length} countersunk screws. Lower the fixed ring over the upright cage and align its rounded rectangular bosses. Its +X service hole must line up with the lower cage's hole and shaft-clamp screw.",
        "At input angle zero, the eccentric points along +X. Insert all {roller_count} nylon spacers axially between the lower cage teeth. Preload the four M3 output nuts into the underside of the combined upper closure/hub (output_cage), then fit it over the teeth.",
        "Install one M2 x {cage_screw_length} countersunk screw through every tooth from above into its captive lower nut. The OOBB top-clearance cuts let the complete heads pass through the integrated upper disc. Tighten all {cage_screw_count} before fitting the 6810 and output carrier. Countersunk screw lengths include their heads.",
        "Fit the single 6810 around the integrated upper hub. There is no separate output_hub disc. The central blind recess clears the motor shaft tip by {motor_shaft_end_clearance:g} mm.",
        "Fit the upper bearing housing with its mouth downward. Install the {housing_screw_count} M3 x {case_screw_length} socket caps from the top into the captive base nuts. The fixed ring and upper housing retain the bearing outer race.",
        "Place the recessed output nut carrier (output_retainer) on the hub inside the 6810 with its hex pockets upward. The hub backs the carrier's nut-pocket bridge cuts. Load all {output_m6_mount_count} M6 and {output_m3_mount_count} M3 attachment nuts; all pockets fit inside the 50 mm bearing bore.",
        "Close the sandwich with the stepped output_cover and four M3 x {output_screw_length} socket caps in the off-grid fixing positions {output_fixing_mounts}. The freed corner grid holes now take attachment nuts: {output_m6_mount_count} M6 and {output_m3_mount_count} M3 in total. The face remains {output_above_housing:g} mm above the teal housing, with a {output_face_clearance:g} mm underside gap and {output_radial_clearance:g} mm radial neck clearance. Use light preload at the printed cage nut seats and the generated attachment-depth limits.",
        "To tighten the motor shaft clamp after assembly, turn the input until the housing port, rotating cage port and screw head all line up along +X. Insert a straight 2 mm hex driver with a shaft no larger than {shaft_driver_diameter:g} mm through the {shaft_access_diameter:g} mm service bore at Z={shaft_clamp_z:g} mm. The bore is for the slim driver, not a full-size bit holder or screw insertion. Withdraw the driver before rotating the input.",
        "Turn the input slowly by hand and check one reverse output turn per {reduction} input turns. Physical fit, motor bearing loads, vibration and printed strength remain untested.",
    ]


def define_assembly_card_style(**kwargs):
    """Four largely pictorial panels on landscape A4; dimensions in mm."""
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("page_mm", [297, 210])
    kwargs.setdefault("columns", 2)
    kwargs.setdefault("rows", 2)
    kwargs.setdefault("margin_mm", 6)
    kwargs.setdefault("gutter_mm", 4)
    kwargs.setdefault("border_radius_mm", 3)
    kwargs.setdefault("border_width_pt", 3.0)
    kwargs.setdefault("component_border_width_pt", 1.1)
    kwargs.setdefault("thumbnail_height_mm", 8.5)
    kwargs.setdefault("quantity_shift_mm", 1.0)
    kwargs.setdefault("paper", "FFFFFF")
    kwargs.setdefault("ink", "000000")
    kwargs.setdefault("accent", "000000")
    kwargs.setdefault("border", "000000")
    kwargs.setdefault("image_size", [1500, 1100])
    kwargs.setdefault("samples", 24)
    kwargs.setdefault("eye", [1.2, -1.6, 1.35])
    kwargs.setdefault("underside_eye", [1.2, -1.6, -1.5])
    kwargs.setdefault("font_body_pt", 7)
    kwargs.setdefault("font_code_pt", 6.4)
    kwargs.setdefault("font_url_prefix_pt", 4.8)
    kwargs.setdefault("quantity_pt", 5.8)
    kwargs.setdefault("explosion_scale", 1.35)
    kwargs.setdefault("draw_arrows", False)
    kwargs.setdefault("revision", "4")
    kwargs.setdefault("title", "OOBB wave drive | {reduction}:1")
    return kwargs


def define_assembly_book(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("cover_title", "Wave drive")
    kwargs.setdefault("cover_subtitle", "{reduction}:1 reduction / NEMA 17")
    kwargs.setdefault("project_name", "oomlout_oobb_part_motor_gearbox_wave_drive_version_5")
    kwargs.setdefault("project_url", "https://github.com/oomlout/oomlout_oobb_part_motor_gearbox_wave_drive_version_5")
    kwargs.setdefault("viewer_enabled", True)
    kwargs.setdefault("viewer_start", "step-01")
    kwargs.setdefault("viewer_url", "https://oomlout.github.io/oomlout_oobb_part_motor_gearbox_wave_drive_version_5/")
    kwargs.setdefault("project_summary", "A 3D-printable {reduction}:1 roller wave gearbox for a NEMA 17 motor, with an OOBB mounting base and output face. Twelve nylon spacers transfer motion from an eccentric wheel to the output cage. The output turns once in the opposite direction for every {reduction} motor turns.")
    kwargs.setdefault("logo_svg", "source_file/oomlout_logo_unshaded_original.svg")
    kwargs.setdefault("logo_symbol_subpaths", 3)
    kwargs.setdefault("details_title", "Project details")
    kwargs.setdefault("details", [
        "Reduction: {reduction}:1. Output rotates opposite to the motor.",
        "Motor: NEMA 17, {motor_body_depth:g} mm body, {motor_shaft_length:g} mm shaft.",
        "Rollers: 12 nylon spacers, {roller_diameter:g} mm OD, {roller_length:g} mm depth, {roller_bore_diameter:g} mm bore.",
        "Bearings: 6810 (50 x 65 x 7 mm); 6704 (20 x 27 x 4 mm).",
        "Cage: M2 x {cage_screw_length} countersunk screws; {cage_tip_clearance:.1f} mm nominal tip clearance.",
        "Eccentric joint: M3 x {eccentric_join_screw_length} countersunk screws and captive nuts.",
        "Clamshell joint: M3 x {wave_screw_length} countersunk screws and captive nuts.",
        "Case: M3 x {case_screw_length} screws from above; nuts underneath the base.",
        "Motor mount: M3 x {motor_screw_length} countersunk screws.",
        "Regenerate CAD and instructions: python working.py",
        "Hardware links: OOMP catalogue codes. Printed parts are named in the parts list.",
        "AI-generated CAD and instructions. Fit and load capacity not physically tested.",
    ])
    kwargs.setdefault("summary_title", "Printed parts")
    kwargs.setdefault("hardware_title", "Hardware")
    kwargs.setdefault("summary_step", True)
    kwargs.setdefault("summary_view", "book_cover")
    kwargs.setdefault("signature_pages", 4)
    kwargs.setdefault("summary_scope", "printed_and_hardware")
    return kwargs


def define_assembly_part_labels(**kwargs):
    """Names and identities, not supplier recommendations. Local IDs are explicit.

    Catalogue IDs below were matched to the local OOMP working.yaml records.
    A project-local ID is used where an exact catalogue record is not available.
    """
    return {
        "motor_mount_plate": {
            "printed": True,
            "name": "Motor base plate",
        },
        "fixed_profile_ring": {
            "printed": True,
            "name": "Fixed profile ring",
        },
        "output_bearing_housing": {
            "printed": True,
            "name": "6810 bearing housing",
        },
        "cage_lower_cap": {
            "printed": True,
            "name": "Lower cage with teeth",
        },
        "output_cage": {
            "printed": True,
            "name": "Upper cage and hub",
        },
        "output_retainer": {
            "printed": True,
            "name": "Output nut carrier",
        },
        "output_cover": {
            "printed": True,
            "name": "OOBB output cover",
        },
        "motor_eccentric": {
            "printed": True,
            "name": "Lower eccentric shaft",
        },
        "motor_eccentric_cap": {
            "printed": True,
            "name": "Upper eccentric collar",
        },
        "wave_generator": {
            "printed": True,
            "name": "Lower wave clamshell",
        },
        "wave_bearing_cap": {
            "printed": True,
            "name": "Upper wave clamshell",
        },
        "bearing_6810": {
            "name": "6810 bearing",
            "detail": "50 x 65 x 7 mm",
            "catalogue_id": "hardware_bearing_6800_series_6810_size_50_mm_id_65_mm_od_7_mm_depth",
        },
        "bearing_6704": {
            "name": "6704 bearing",
            "detail": "20 x 27 x 4 mm",
            "catalogue_id": "hardware_bearing_6700_series_6704_size_20_mm_id_27_mm_od_4_mm_depth",
        },
        "roller": {
            "name": "Spacer {roller_diameter:g}mm OD {roller_length:g}mm depth",
            "detail": "{roller_diameter:g} OD x {roller_length:g} mm; 3.2 bore",
            "catalogue_id": "hardware_spacer_m3_nylon_white_7_mm_outer_diameter_12_mm_depth",
            "catalogue_match": {"roller_diameter": 7.0, "roller_length": 12.0, "roller_bore_diameter": 3.2},
        },
        "screw_case": {
            "name": "M3 x {case_screw_length} socket cap",
            "catalogue_id": "hardware_screw_socket_cap_hex_head_black_m3_diameter_{case_screw_length}_mm_length",
        },
        "screw_motor": {
            "name": "M3 x {motor_screw_length} countersunk",
            "catalogue_id": "hardware_screw_countersunk_hex_head_black_m3_diameter_{motor_screw_length}_mm_length",
        },
        "screw_output": {
            "name": "M3 x {output_screw_length} socket cap",
            "catalogue_id": "hardware_screw_socket_cap_hex_head_black_m3_diameter_{output_screw_length}_mm_length",
        },
        "screw_wave": {
            "name": "M3 x {wave_screw_length} countersunk",
            "catalogue_id": "hardware_screw_countersunk_hex_head_black_m3_diameter_{wave_screw_length}_mm_length",
        },
        "screw_cage": {
            "name": "M2 x {cage_screw_length} countersunk",
            "detail": "Hex drive; length includes head",
            "catalogue_id": "hardware_screw_countersunk_hex_head_black_m2_diameter_{cage_screw_length}_mm_length",
        },
        "screw_eccentric": {
            "name": "M3 x {eccentric_join_screw_length} countersunk",
            "detail": "Hex drive; length includes head",
            "catalogue_id": "hardware_screw_countersunk_hex_head_black_m3_diameter_{eccentric_join_screw_length}_mm_length",
        },
        "screw_shaft_clamp": {
            "name": "M3 x {shaft_clamp_screw_length} countersunk",
            "detail": "Hex drive; length includes head",
            "catalogue_id": "hardware_screw_countersunk_hex_head_black_m3_diameter_{shaft_clamp_screw_length}_mm_length",
        },
        "nut_m2": {
            "name": "M2 hex nut",
            "catalogue_id": "hardware_nut_m2",
        },
        "nut_m3": {
            "name": "M3 hex nut",
            "catalogue_id": "hardware_nut_m3",
        },
        "nut_m6": {
            "name": "M6 hex nut",
            "catalogue_id": "hardware_nut_m6",
        },
        "nema17": {
            "name": "NEMA 17 motor",
            "detail": "{motor_body_depth:g} mm body; {motor_shaft_length:g} x {input_shaft_diameter:g} mm shaft",
        },
    }


def define_assembly_cards(**kwargs):
    """Cumulative views. Offset nuts below the receiving part in the same panel.

    Actions remain editable companion notes; the printed panels show only their
    number, CAD diagram, arrows and part details. `targets` defines intermediate
    insertion positions when nuts load into an already exploded component.
    """
    return [
        {
            "title": "Mount the motor and capture the case nuts",
            "action": "Load six M3 nuts from below the plate. Seat the plate on the motor pilot and install four M3 x {motor_screw_length} countersunk screws flush with its top face.",
            "add": ["nema17_*", "motor_mount_plate", "case_nut_*", "motor_screw_*"],
            "move": {
                "motor_mount_plate": [0, 0, 22],
                "case_nut_*": [0, 0, 12],
                "motor_screw_*": [0, 0, 40],
            },
            "targets": {
                "case_nut_*": [0, 0, 22],
                "motor_screw_*": [0, 0, 22],
            },
        },
        {
            "title": "Fit the cage with its captive nuts",
            "action": "Seat twelve M2 nuts underneath the lower cage, then lower the cage teeth upward onto the plate. Align the service hole with the shaft clamp (+X).",
            "add": ["cage_lower_cap", "cage_nut_*"],
            "move": {
                "cage_lower_cap": [0, 0, 42],
                "cage_nut_*": [0, 0, 28],
            },
            "targets": {
                "cage_nut_*": [0, 0, 42],
            },
        },
        {
            "title": "Prepare and fit the lower eccentric",
            "action": "Load two M3 joint nuts from below and one radial M3 clamp nut. Start the M3 x {shaft_clamp_screw_length} countersunk screw, leaving the bore clear. Slide onto the motor shaft and snug the clamp through the cage port.",
            "add": ["motor_eccentric", "eccentric_join_nut_*", "motor_clamp_*"],
            "move": {
                "motor_eccentric": [0, 0, 43],
                "eccentric_join_nut_*": [0, 0, 31],
                "motor_clamp_0_nut_m3": [16, 0, 43],
                "motor_clamp_0_screw_shaft_clamp": [32, 0, 43],
            },
            "targets": {
                "eccentric_join_nut_*": [0, 0, 43],
                "motor_clamp_*": [0, 0, 43],
            },
        },
        {
            "title": "Fit the lower wave half and 6704",
            "action": "Seat four M3 nuts underneath the lower clamshell. Lower it around the eccentric journal and seat the 6704 bearing squarely in its recess.",
            "add": ["wave_generator", "wave_nut_*", "bearing_6704"],
            "move": {
                "wave_generator": [0, 0, 34],
                "wave_nut_*": [0, 0, 21],
                "bearing_6704": [0, 0, 53],
            },
            "targets": {
                "wave_nut_*": [0, 0, 34],
                "bearing_6704": [0, 0, 34],
            },
        },
        {
            "title": "Close the eccentric shaft",
            "action": "Fit the upper eccentric collar and tighten two M3 x {eccentric_join_screw_length} countersunk screws into the lower nuts.",
            "add": ["motor_eccentric_cap", "eccentric_join_screw_*"],
            "move": {
                "motor_eccentric_cap": [0, 0, 24],
                "eccentric_join_screw_*": [0, 0, 44],
            },
            "targets": {
                "eccentric_join_screw_*": [0, 0, 24],
            },
        },
        {
            "title": "Close the wave clamshell",
            "action": "Fit the upper wave half around the 6704 bearing. Tighten four M3 x {wave_screw_length} countersunk screws into the lower nuts.",
            "add": ["wave_bearing_cap", "wave_screw_*"],
            "move": {
                "wave_bearing_cap": [0, 0, 25],
                "wave_screw_*": [0, 0, 43],
            },
            "targets": {
                "wave_screw_*": [0, 0, 25],
            },
        },
        {
            "title": "Lower the fixed ring",
            "action": "Lower the fixed ring around the cage. Align all six fins with the base and the service hole with the cage port (+X).",
            "add": ["fixed_profile_ring"],
            "move": {
                "fixed_profile_ring": [0, 0, 37],
            },
        },
        {
            "title": "Insert twelve rollers",
            "action": "At input angle zero, insert one {roller_diameter:g} mm OD x {roller_length:g} mm nylon spacer in each cage slot.",
            "add": ["roller_*"],
            "move": {
                "roller_*": [0, 0, 29],
            },
        },
        {
            "title": "Fit and fasten the upper cage",
            "action": "Load four M3 output nuts underneath the upper cage, then lower it over the teeth. Install all twelve M2 x {cage_screw_length} countersunk screws through the disc into the lower cage nuts.",
            "add": ["output_cage", "output_nut_*", "cage_screw_*"],
            "move": {
                "output_cage": [0, 0, 31],
                "output_nut_*": [0, 0, 19],
                "cage_screw_*": [0, 0, 55],
            },
            "targets": {
                "output_nut_*": [0, 0, 31],
                "cage_screw_*": [0, 0, 31],
            },
        },
        {
            "title": "Fit the output bearing and close the case",
            "action": "Seat the 6810 over the upper cage hub. Lower the housing over the bearing outer race. Insert six M3 x {case_screw_length} socket caps from the top and tighten into the captive base nuts.",
            "add": ["bearing_6810", "output_bearing_housing", "case_screw_*"],
            "move": {
                "bearing_6810": [0, 0, 22],
                "output_bearing_housing": [0, 0, 43],
                "case_screw_*": [0, 0, 83],
            },
            "targets": {
                "case_screw_*": [0, 0, 43],
            },
        },
        {
            "title": "Load and fit the output nut carrier",
            "action": "Fit five M6 nuts and eight M3 nuts in the carrier's upward-facing pockets. Lower the loaded carrier into the 6810 bore, keeping the four off-grid fixing holes clear.",
            "add": ["output_retainer", "output_attachment*"],
            "move": {
                "output_retainer": [0, 0, 24],
                "output_attachment_nut_*": [0, 0, 42],
                "output_attachment_m3_nut_*": [0, 0, 42],
            },
            "targets": {
                "output_attachment*": [0, 0, 24],
            },
        },
        {
            "title": "Close the output face",
            "action": "Fit the output cover and tighten four M3 x {output_screw_length} socket caps in the off-grid fixing holes. Align the service ports to adjust the shaft clamp with a slim 2 mm hex driver. Withdraw it, disconnect power and hand-turn the input {reduction} times for one reverse output turn.",
            "add": ["output_cover", "output_screw_*"],
            "move": {
                "output_cover": [0, 0, 24],
                "output_screw_*": [0, 0, 44],
            },
            "targets": {
                "output_screw_*": [0, 0, 24],
            },
        },
    ]


if __name__ == "__main__":
    main()

