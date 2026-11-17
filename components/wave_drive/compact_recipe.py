"""Single-bank, motor-supported input. Editable dimensions in millimetres."""
import copy
import math

from working_oomp_populate import define
from wave_drive.oobb_hardware import ensure_local_hardware, hardware_definitions


def output_m3_pocket_points(point, **kwargs):
    # Include the OOBB hex and both overhang bridge rectangles in the XY envelope.
    angle = math.atan2(point[1], point[0])-math.pi/6
    radius = kwargs["mount_m3_hex_radius"]
    vertices = [[radius*math.cos(i*math.pi/3), radius*math.sin(i*math.pi/3)] for i in range(6)]
    vertices += [[x, y] for x in [-kwargs["mount_m3_bridge_half_width"], kwargs["mount_m3_bridge_half_width"]] for y in [-kwargs["mount_m3_bridge_half_height"], kwargs["mount_m3_bridge_half_height"]]]
    return [[point[0]+x*math.cos(angle)-y*math.sin(angle), point[1]+x*math.sin(angle)+y*math.cos(angle)] for x,y in vertices]


def output_mount_layout(**kwargs):
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("output_grid_pitch", 15.0)
    pitch = kwargs["output_grid_pitch"]
    radius = min(kwargs["output_plate_diameter"]/2, 25-kwargs["journal_clearance"])
    web = kwargs["mount_minimum_web"]
    m3_radius = kwargs["mount_m3_pocket_radius"]
    m6_radius = kwargs["mount_m6_pocket_radius"]
    m6 = [[0, 0], [pitch, 0], [-pitch, 0], [0, pitch], [0, -pitch]]
    x, y = kwargs["output_fixing_x"], kwargs["output_fixing_y"]
    assembly = [[x, y], [-y, x], [-x, -y], [y, -x]]
    # Half-grid candidates, including axial positions; reject any pocket that
    # would merge with another nut, an assembly screw, or the outside edge.
    count = math.floor(radius/(pitch/2))
    m3 = []
    for i in range(-count, count+1):
        for j in range(-count, count+1):
            point = [i*pitch/2, j*pitch/2]
            if max(math.hypot(*p) for p in output_m3_pocket_points(point, **kwargs))+kwargs["mount_m3_edge_wall"] > radius:
                continue
            if any(math.dist(point, other) < m3_radius+m6_radius+web for other in m6):
                continue
            if any(math.dist(point, other) < m3_radius+1.8+web for other in assembly):
                continue
            if any(math.dist(point, other) < 2*m3_radius+web for other in m3):
                continue
            m3.append(point)
    return {
        "output_fixing_mounts": assembly,
        "output_m6_mounts": m6,
        "output_m3_mounts": m3,
        "output_m6_mount_count": len(m6),
        "output_m3_mount_count": len(m3),
    }


def resolve(**kwargs):
    from working_scad import bearing_spec
    kwargs = copy.deepcopy(kwargs)
    kwargs.setdefault("roller_bank_count", 1)
    c = define(**kwargs)
    c["cage_screw_count"] = int(c["reduction"])
    for key in ["reduction", "cage_screw_count", "housing_screw_count"]:
        if isinstance(c[key], bool) or c[key] < 1 or int(c[key]) != c[key]:
            raise ValueError(key + " must be a positive integer")
    if c["roller_bank_count"] != 1:
        raise ValueError("This is the single-bank recipe")
    if c["roller_length"] not in c["roller_lengths_available"]:
        raise ValueError("Choose a stocked nylon spacer length")
    if c["overhang"] is not True or not 0 < c["max_screw_length"] <= 35:
        raise ValueError("Use OOBB overhang=True and socket caps <=35 mm")
    for key in ["profile_clearance", "roller_slot_clearance", "roller_end_clearance", "bearing_seat_clearance", "journal_clearance", "bearing_axial_clearance", "shaft_fit_clearance"]:
        if not math.isfinite(c[key]) or c[key] < 0:
            raise ValueError(key + " must be finite and nonnegative")
    if c["circle_fragments"] < 96 or c["profile_samples_per_cavity"] < 40:
        raise ValueError("Insufficient surface sampling")
    if not 0 < c["roller_bore_diameter"] < c["roller_diameter"]:
        raise ValueError("Invalid nylon spacer bore")
    c["output_bearing"] = bearing_spec(bearing_size=c["bearing_output"])
    c["wave_bearing"] = bearing_spec(bearing_size=c["bearing_wave"])
    if c["output_bearing"] != {"id":50., "od":65., "depth":7.} or c["wave_bearing"] != {"id":20., "od":27., "depth":4.}:
        raise ValueError("This stack requires a 6810 output and 6704 wave bearing")
    c["housing_flange_width"] = c["base_width"]*c["oobb_grid_pitch"]-c["oobb_size_allowance"]
    c["housing_flange_height"] = c["base_height"]*c["oobb_grid_pitch"]-c["oobb_size_allowance"]
    if min(c["base_width"],c["base_height"]) < 5:
        raise ValueError("The base needs at least five OOBB units; the central housing footprint extends it")
    if c["base_edge_radius"] < 0 or 2*c["base_edge_radius"] > c["motor_plate_depth"] or c["base_edge_radius"] > c["housing_flange_corner_radius"]:
        raise ValueError("Plate edge radii must fit its depth and corner radius")
    c["housing_radius"] = c["output_bearing"]["od"]/2+c["bearing_seat_clearance"]+c["output_holder_wall"]
    c["case_boss_radius"] = c["mount_m3_pocket_radius"]+c["case_boss_wall"]
    # Bury the rear rounding inside the cylinder so the visible junction stays flat.
    c["case_boss_inner_radius"] = c["housing_radius"]-c["case_boss_overlap"]-c["case_boss_radius"]
    c["case_boss_outer_radius"] = c["housing_screw_pitch_radius"]+c["case_boss_radius"]
    c["case_boss_radial_depth"] = c["case_boss_outer_radius"]-c["case_boss_inner_radius"]
    c["case_boss_corner_radius"] = c["case_boss_rounding_fraction"]*min(c["case_boss_outer_radius"]-c["housing_screw_pitch_radius"],c["case_boss_radius"],c["case_boss_radial_depth"]/2)
    c["case_boss_center_radius"] = (c["case_boss_inner_radius"]+c["case_boss_outer_radius"])/2
    c["housing_envelope_radius"] = math.hypot(c["case_boss_outer_radius"],c["case_boss_radius"])
    c["base_envelope_width"] = max(c["housing_flange_width"],2*c["housing_envelope_radius"])
    c["base_envelope_height"] = max(c["housing_flange_height"],2*c["housing_envelope_radius"])
    c["roller_count"] = int(c["reduction"])
    c["total_roller_count"] = c["roller_count"]
    c["cavity_count"] = c["roller_count"]+1
    c["roller_radius"] = c["roller_diameter"]/2
    c["pitch_radius"] = c["wave_radius"]+c["roller_radius"]
    c["cage_screw_radius"] = c["pitch_radius"]+c["cage_screw_radial_offset"]
    c["cage_inner_radius"] = c["pitch_radius"]-c["cage_wall"]/2
    c["cage_outer_radius"] = c["pitch_radius"]+c["cage_wall"]/2
    if c["cage_center_diameter"]/2 < 11+c["eccentricity"]+.5:
        raise ValueError("Lower cage opening must pass over the eccentric collars with clearance")
    c["profile_max_radius"] = c["wave_radius"]+c["roller_diameter"]+c["eccentricity"]+c["profile_clearance"]
    if c["eccentricity"] <= 0 or c["wave_radius"] < 23 or c["cage_wall"] < 4:
        raise ValueError("Wave wheel needs material around its 44 mm bearing cap")
    if c["cage_inner_radius"]-c["wave_radius"]-c["eccentricity"] < .2:
        raise ValueError("Wave wheel would touch the cage")
    chord = 2*(c["pitch_radius"]-c["eccentricity"])*math.sin(math.pi/c["roller_count"])
    if chord < c["roller_diameter"]+c["roller_slot_clearance"]+3:
        raise ValueError("Too many rollers for this compact radius")
    if c["housing_screw_pitch_radius"]-3.5-c["profile_max_radius"] < .75:
        raise ValueError("Case nut pockets break into the wave profile")
    if c["output_holder_wall"] < 3 or c["case_boss_wall"] < 2:
        raise ValueError("Keep a 3 mm bearing wall and 2 mm screw-boss walls")
    if c["housing_screw_pitch_radius"]-c["mount_m3_pocket_radius"]-(32.5+c["bearing_seat_clearance"]) < c["case_boss_wall"]-1e-8:
        raise ValueError("Case nut pockets need the specified wall beside the bearing seat")
    if not 0 < c["housing_flange_corner_radius"] < c["housing_flange_width"]/2 or c["housing_flange_width"] < 2*c["housing_radius"]:
        raise ValueError("Invalid rounded mounting plate")
    c["ring_z"] = c["motor_plate_depth"]
    c["cage_cap_z"] = c["ring_z"]+.3
    c["window_z"] = c["cage_cap_z"]+c["cage_plate_depth"]
    c["wave_height"] = max(c["roller_length"], 10.2)
    c["window_height"] = c["wave_height"]+2*c["roller_end_clearance"]
    c["wave_z"] = c["window_z"]+c["roller_end_clearance"]
    c["roller_z"] = c["wave_z"]+(c["wave_height"]-c["roller_length"])/2
    c["cage_floor_z"] = c["window_z"]+c["window_height"]
    c["cage_head_lift"] = c["cage_screw_length"]-c["cage_screw_reference_length"]+c["cage_tip_extra_clearance"]
    c["cage_upper_plate_depth"] = c["cage_plate_depth"]+c["cage_head_lift"]
    c["hub_z"] = c["cage_floor_z"]+c["cage_upper_plate_depth"]
    c["bearing_z"] = c["hub_z"]+.1
    c["ring_height"] = c["hub_z"]-c["ring_z"]
    c["bearing_stack_height"] = 7.2
    c["hub_height"] = c["output_hub_depth"]
    c["retainer_z"] = c["hub_z"]+c["hub_height"]

    c["wave_seat_z"] = (c["wave_height"]-4)/2-.4
    c["wave_bearing_z"] = c["wave_z"]+c["wave_seat_z"]+.1
    c["wave_split_z"] = c["wave_bearing_z"]+2
    c["wave_lower_depth"] = c["wave_split_z"]-c["wave_z"]
    c["wave_cap_depth"] = c["wave_height"]-c["wave_lower_depth"]
    c["cam_z"] = c["wave_z"]+c["wave_seat_z"]-1
    c["cam_base_z"] = c["shaft_clamp_axis_z"]-3.4
    c["cam_shoulder_z"] = c["cam_z"]-c["cam_base_z"]
    c["cam_cap_z"] = c["cam_z"]+5.2
    c["cam_cap_height"] = 6.8
    c["shaft_clamp_z"] = c["shaft_clamp_axis_z"]
    c["eccentric_join_head_z"] = c["cam_cap_z"]+c["cam_cap_height"]
    c["eccentric_join_nut_z"] = c["eccentric_join_head_z"]-c["eccentric_join_screw_length"]+.1
    c["wave_head_recess"] = 0.0
    c["wave_nut_z"] = c["wave_height"]-c["wave_screw_length"]+.3
    if c["wave_nut_z"] < .2 or c["wave_nut_z"]+2.5 > c["wave_lower_depth"]-.5:
        raise ValueError("Wave screws must fully engage nuts retained inside the lower clamshell")
    if math.hypot(c["eccentricity"], c["eccentric_join_pitch_radius"])-3.6-c["input_shaft_diameter"]/2-c["shaft_fit_clearance"] < .5:
        raise ValueError("Eccentric M3 countersinks need a 0.5 mm web beside the motor shaft")
    if c["eccentric_join_pitch_radius"]+3.6 > 10.5:
        raise ValueError("Eccentric countersinks need a 0.5 mm rim inside the 22 mm collar")
    c["housing_top_z"] = c["hub_z"]+c["bearing_stack_height"]+3.5
    c["case_socket_depth"] = c["case_socket_recess"]+c["cage_head_lift"]
    c["case_head_seat"] = c["housing_top_z"]-c["case_socket_depth"]
    c["housing_top_depth"] = c["housing_top_z"]-c["hub_z"]
    c["motor_head_seat"] = c["motor_plate_depth"]
    c["assembly_height"] = c["housing_top_z"]+c["output_above_housing"]
    c["output_cover_z"] = c["assembly_height"]-c["output_cover_depth"]
    c["output_plate_z"] = c["output_cover_z"]
    c["output_flange_z"] = c["housing_top_z"]+c["output_face_clearance"]
    c["output_neck_height"] = c["output_cover_z"]-c["retainer_z"]
    c["retainer_depth"] = c["output_neck_height"]
    c["output_head_seat"] = c["assembly_height"]-c["output_socket_recess"]
    c["motor_thread_engagement"] = c["motor_screw_length"]-c["motor_head_seat"]
    c["shaft_blind_depth"] = max(0,c["motor_shaft_length"]+c["motor_shaft_end_clearance"]-c["hub_z"])
    c["output_attachment_nut_z"] = c["output_cover_z"]-c["output_nut_depth"]+.1
    c["output_m3_attachment_nut_z"] = c["output_cover_z"]-c["output_m3_nut_depth"]+.1
    c["output_bolt_projection_max"] = c["assembly_height"]-c["output_attachment_nut_z"]
    c["output_bolt_projection_min"] = c["assembly_height"]-(c["output_attachment_nut_z"]+c["output_nut_height"])+3.0
    c["output_m3_bolt_projection_max"] = c["assembly_height"]-c["output_m3_attachment_nut_z"]
    c["output_m3_bolt_projection_min"] = c["assembly_height"]-(c["output_m3_attachment_nut_z"]+c["output_m3_nut_height"])+2.0
    c.update(output_mount_layout(**c))
    if not 0 < c["case_boss_rounding_fraction"] <= 1:
        raise ValueError("Boss rounding fraction must be greater than zero and at most one")
    if not 0 < c["output_face_clearance"] <= c["output_above_housing"]-.7+1e-8:
        raise ValueError("Leave at least 0.7 mm of output face above its visible gap")
    if c["shaft_blind_depth"] > c["hub_height"]-.5+1e-8:
        raise ValueError("Motor shaft recess would break through the output hub")
    if c["output_neck_height"] < 0 or c["output_cover_depth"]-c["output_socket_recess"] < 1:
        raise ValueError("Output plate must clear the stationary housing and retain its screw heads")
    if c["output_attachment_nut_z"]-.1-.6-(c["hub_z"]+c["shaft_blind_depth"]) < .5-1e-8:
        raise ValueError("Nut pocket bridges must leave a blind floor above the motor shaft")
    if c["output_grid_pitch"]+c["mount_m6_pocket_radius"]+c["mount_minimum_web"] > 26.2:
        raise ValueError("M6 pockets need support from the output carrier neck")
    if c["output_head_seat"]-c["output_screw_length"] < c["wave_z"]+c["wave_height"]+.2:
        raise ValueError("Output screws would enter the moving wave wheel")
    c["output_nut_z"] = c["cage_floor_z"]+c["cage_head_lift"]+.2
    if c["output_head_seat"]-c["output_screw_length"] > c["output_nut_z"]:
        raise ValueError("Output screws do not fully engage the captive cage nuts")
    c["cage_head_seat"] = c["hub_z"]
    c["cage_nut_z"] = c["cage_head_seat"]-c["cage_screw_length"]
    c["cage_tip_clearance"] = c["cage_head_seat"]-c["cage_screw_length"]-c["cage_cap_z"]
    # Deeper underside nut tunnels reach into the tooth roots; nominal nuts
    # remain below the rolling member and keep their full 1.6 mm engagement.
    if c["cage_nut_z"] < c["cage_cap_z"]+.2 or c["cage_nut_z"]+1.6 > c["roller_z"]-.05:
        raise ValueError("Cage countersunk screws must engage the lower nuts without protruding")
    if c["shaft_clamp_z"]+c["shaft_access_diameter"]/2 >= c["roller_z"]:
        raise ValueError("Shaft driver must pass below the rollers")
    if c["shaft_driver_diameter"] >= c["shaft_access_diameter"]:
        raise ValueError("Driver needs clearance through the service port")
    if c["cam_base_z"] <= c["motor_pilot_height"]+.1:
        raise ValueError("Recessed eccentric must clear the motor pilot")
    if abs(c["shaft_clamp_head_radius"]-c["shaft_clamp_screw_length"]-(c["input_shaft_diameter"]/2-c["input_shaft_flat_depth"])) > .05:
        raise ValueError("Shaft-clamp screw length must reach the motor flat at its nominal head position")
    # Motor-supported input has a finite shaft reach; reject unsupported long edits.
    if c["cam_cap_z"]+c["cam_cap_height"] > c["motor_shaft_length"]-1:
        raise ValueError("Motor shaft too short: increase verified motor shaft length for this roller")
    if c["housing_top_depth"] < c["bearing_stack_height"]+2:
        raise ValueError("This motor stack needs a taller top holder / longer case screws")
    for key in ["case_screw_length", "motor_screw_length", "output_screw_length", "wave_screw_length", "cage_screw_length", "eccentric_join_screw_length", "shaft_clamp_screw_length"]:
        if c[key] > c["max_screw_length"]:
            raise ValueError("Socket cap exceeds requested maximum")
    if c["motor_screw_length"]-c["motor_head_seat"] > c["motor_thread_depth"]-.5:
        raise ValueError("Motor mounting screws would bottom in the reference threads")
    case_tip = c["case_head_seat"]-c["case_screw_length"]
    if case_tip < -.1 or case_tip > c["case_nut_z"]:
        raise ValueError("Top-entering case screw must fully engage the base nut without projecting below the plate")
    c["output_direction"] = "opposite_to_input"
    return c


def piece_definitions(**kwargs):
    c = resolve(**kwargs)
    return [
        {
            "name": "motor_mount_plate",
            "module": "motor_mount_plate",
            "arguments": [],
            "quantity": 1,
            "size": [c["base_envelope_width"], c["base_envelope_height"]],
        },
        {
            "name": "fixed_profile_ring",
            "module": "fixed_ring",
            "arguments": [],
            "quantity": 1,
            "size": [2*c["housing_envelope_radius"], 2*c["housing_envelope_radius"]],
        },
        {
            "name": "output_bearing_housing",
            "module": "output_housing",
            "arguments": [],
            "quantity": 1,
            "size": [2*c["housing_envelope_radius"], 2*c["housing_envelope_radius"]],
        },
        {
            "name": "output_cage",
            "module": "cage",
            "arguments": [],
            "quantity": 1,
            "size": [2*c["cage_outer_radius"], 2*c["cage_outer_radius"]],
        },
        {
            "name": "cage_lower_cap",
            "module": "cage_cap",
            "arguments": [],
            "quantity": 1,
            "size": [2*c["cage_outer_radius"], 2*c["cage_outer_radius"]],
        },
        {
            "name": "output_retainer",
            "module": "output_retainer",
            "arguments": [],
            "quantity": 1,
            "size": [c["output_plate_diameter"], c["output_plate_diameter"]],
        },
        {
            "name": "output_cover",
            "module": "output_cover",
            "arguments": [],
            "quantity": 1,
            "size": [c["output_plate_diameter"], c["output_plate_diameter"]],
        },
        {
            "name": "wave_generator",
            "module": "wave_generator",
            "arguments": [],
            "quantity": 1,
            "size": [2*c["wave_radius"], 2*c["wave_radius"]],
        },
        {
            "name": "wave_bearing_cap",
            "module": "wave_cap",
            "arguments": [],
            "quantity": 1,
            "size": [2*c["wave_radius"], 2*c["wave_radius"]],
        },
        {
            "name": "motor_eccentric",
            "module": "motor_eccentric",
            "arguments": [],
            "quantity": 1,
            "size": [24, 24],
        },
        {
            "name": "motor_eccentric_cap",
            "module": "motor_eccentric_cap",
            "arguments": [],
            "quantity": 1,
            "size": [24, 24],
        },
    ]


def optional_print_definitions(**kwargs):
    c = resolve(**kwargs)
    if not c["include_printable_spacers"]:
        return []
    return [
        {
            "name": "printable_spacer",
            "module": "roller",
            "arguments": [],
            "quantity": c["roller_count"],
            "size": [c["roller_diameter"], c["roller_diameter"]],
            "replaces": "roller",
            "role": "Optional printed alternative to the purchased nylon spacers; use one set only",
        },
    ]


def bom(**kwargs):
    c = resolve(**kwargs)
    return [
        {
            "item": "6810 bearing",
            "quantity": 1,
            "dimensions": "50 x 65 x 7 mm",
            "role": "single upper output support",
        },
        {
            "item": "6704 bearing",
            "quantity": 1,
            "dimensions": "20 x 27 x 4 mm",
            "role": "wave wheel on the motor eccentric",
        },
        {
            "item": "Nylon spacer roller",
            "quantity": c["roller_count"],
            "dimensions": f'{c["roller_diameter"]:g} OD x {c["roller_bore_diameter"]:g} ID x {c["roller_length"]:g} mm',
            "role": "one bank; free rollers without fixed axles",
        },
        {
            "item": "Case socket cap screw",
            "size": "M3",
            "length_mm": c["case_screw_length"],
            "quantity": c["housing_screw_count"],
        },
        {
            "item": "Motor countersunk screw",
            "size": "M3",
            "length_mm": c["motor_screw_length"],
            "quantity": 4,
            "role": "motor plate to four tapped motor holes",
        },
        {
            "item": "Output socket cap screw",
            "size": "M3",
            "length_mm": c["output_screw_length"],
            "quantity": 4,
        },
        {
            "item": "Wave clamshell countersunk screw",
            "size": "M3",
            "length_mm": c["wave_screw_length"],
            "quantity": 4,
        },
        {
            "item": "Cage tooth countersunk screw",
            "size": "M2",
            "length_mm": c["cage_screw_length"],
            "quantity": c["cage_screw_count"],
        },
        {
            "item": "Eccentric countersunk screw",
            "size": "M3",
            "quantity": 2,
            "length_mm": c["eccentric_join_screw_length"],
            "role": "join the eccentric halves; length includes the countersunk head",
        },
        {
            "item": "Shaft clamp countersunk screw",
            "size": "M3",
            "quantity": 1,
            "length_mm": c["shaft_clamp_screw_length"],
            "role": "motor shaft flat; captive nut and clearance above the head, serviced through aligned radial port",
        },
        {
            "item": "M3 hex nut",
            "quantity": c["housing_screw_count"]+11+c["output_m3_mount_count"],
            "role": "assembly nuts plus captive half-grid output attachment nuts",
        },
        {
            "item": "M6 hex nut",
            "quantity": c["output_m6_mount_count"],
            "role": "OOBB output attachment; payload bolts depend on attached plate thickness",
        },
        {
            "item": "M2 hex nut",
            "quantity": c["cage_screw_count"],
        },
    ]
