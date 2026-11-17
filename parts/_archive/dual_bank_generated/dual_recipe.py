"""Editable dimensional stack for two opposed roller-wave banks."""
import copy
import math

from working_oomp_populate import define


def ensure_local_hardware():
    """Fill a missing OOBB M2 socket-cap entry in memory only; no library edits.

    DIN 912 / ISO 4762 nominal head: diameter 3.8, height 2 mm.
    https://www.accu.co.uk/api/product-datasheet?id=2775
    """
    import oobb
    for mode,height,radius in [("true",2.0,1.9),("3dpr",2.2,2.1),("laser",2.0,1.9)]:
        for name,value in [("screw_socket_cap_height_m2",height),("screw_socket_cap_radius_m2",radius)]:
            try:
                oobb.gv(name,mode)
            except KeyError:
                oobb.set_variable(name,value,mode)


def resolve(**kwargs):
    from working_scad import bearing_spec
    c = define(**kwargs)
    for key in ["reduction", "cage_screw_count", "housing_screw_count"]:
        if isinstance(c[key], bool) or c[key] < 1 or int(c[key]) != c[key]:
            raise ValueError(key + " must be a positive integer")
    if c["reduction"] < 2*c["cage_screw_count"] or c["reduction"] % c["cage_screw_count"]:
        raise ValueError("Cage screws must divide the integer reduction")
    if c["roller_length"] not in c["roller_lengths_available"]:
        raise ValueError("Choose a stocked nylon spacer length")
    if c["overhang"] is not True:
        raise ValueError("OOBB hardware requires overhang=True")
    if c["max_screw_length"] > 35 or c["max_screw_length"] <= 0:
        raise ValueError("Socket cap screw length limit must be <= 35 mm")
    for key in ["profile_clearance", "roller_slot_clearance", "roller_end_clearance", "bearing_seat_clearance", "journal_clearance", "bearing_axial_clearance", "shaft_fit_clearance"]:
        if not math.isfinite(c[key]) or c[key] < 0:
            raise ValueError(key + " must be finite and nonnegative")
    if c["circle_fragments"] < 96 or c["profile_samples_per_cavity"] < 40:
        raise ValueError("Insufficient surface sampling")
    if not 0 < c["roller_bore_diameter"] < c["roller_diameter"]:
        raise ValueError("Nylon spacer bore must be smaller than its OD")
    if not 0 < c["housing_flange_corner_radius"] < c["housing_flange_width"]/2:
        raise ValueError("Invalid plate corner radius")
    c["roller_count"] = int(c["reduction"])
    c["roller_bank_count"] = 2
    c["total_roller_count"] = 2*c["roller_count"]
    c["cavity_count"] = c["roller_count"]+1
    c["roller_radius"] = c["roller_diameter"]/2
    c["pitch_radius"] = c["wave_radius"]+c["roller_radius"]
    c["cage_inner_radius"] = c["pitch_radius"]-c["cage_wall"]/2
    c["cage_outer_radius"] = c["pitch_radius"]+c["cage_wall"]/2
    c["cage_joint_radius"] = c["cage_outer_radius"]+1
    c["stationary_joint_inner_radius"] = c["cage_joint_radius"]+1
    c["profile_min_radius"] = c["wave_radius"]+c["roller_diameter"]-c["eccentricity"]
    c["profile_max_radius"] = c["wave_radius"]+c["roller_diameter"]+c["eccentricity"]
    if c["eccentricity"] <= 0 or c["wave_radius"] <= 0 or c["cage_wall"] < 4:
        raise ValueError("Invalid cam or cage dimensions")
    if c["cage_inner_radius"]-c["wave_radius"]-c["eccentricity"] < .2 or c["profile_min_radius"]-c["cage_outer_radius"] < .2:
        raise ValueError("Wave, cage and fixed ring need radial clearance")
    chord = 2*(c["pitch_radius"]-c["eccentricity"])*math.sin(math.pi/c["roller_count"])
    if chord < c["roller_diameter"]+c["roller_slot_clearance"]+3:
        raise ValueError("Insufficient material between roller windows")
    if c["housing_screw_pitch_radius"]-3.5-c["profile_max_radius"]-c["profile_clearance"] < 1:
        raise ValueError("Ring nut pocket would break into its profile")
    if c["housing_radius"]-c["housing_screw_pitch_radius"]-3.5 < .5:
        raise ValueError("Housing perimeter too thin at the nut pockets")
    c["output_bearing"] = bearing_spec(bearing_size=c["bearing_output"])
    c["input_bearing"] = bearing_spec(bearing_size=c["bearing_input"])
    c["wave_bearing"] = bearing_spec(bearing_size=c["bearing_wave"])
    if c["output_bearing"] != {"id":50.,"od":65.,"depth":7.} or c["input_bearing"] != {"id":20.,"od":27.,"depth":4.} or c["wave_bearing"] != c["input_bearing"]:
        raise ValueError("This recipe requires 6810 outputs and 6704 input/wave bearings")
    c["opposed_bank_phase_degrees"] = 180.0
    c["upper_profile_rotation"] = 180.0/c["cavity_count"]
    c["bearing_z"] = c["housing_flange_depth"]
    c["ring_z"] = c["bearing_z"]+7
    c["cage_base_z"] = c["ring_z"]+c["bearing_axial_clearance"]
    c["window_z"] = c["cage_base_z"]+c["cage_plate_depth"]
    c["wave_height"] = max(c["roller_length"],10.2)
    c["window_height"] = c["wave_height"]+2*c["roller_end_clearance"]
    c["wave_z"] = c["window_z"]+c["roller_end_clearance"]
    c["roller_z"] = c["wave_z"]+(c["wave_height"]-c["roller_length"])/2
    c["roller_window_z"] = c["window_z"]+(c["wave_height"]-c["roller_length"])/2
    c["roller_window_height"] = c["roller_length"]+2*c["roller_end_clearance"]
    c["joint_z"] = c["window_z"]+c["window_height"]
    c["mirror_z"] = c["joint_z"]+c["central_joint_depth"]/2
    c["assembly_height"] = 2*c["mirror_z"]
    c["ring_height"] = c["joint_z"]-c["ring_z"]
    c["shaft_length"] = 5*math.ceil((c["assembly_height"]+25)/5)
    c["wave_cap_depth"] = 4.2
    c["wave_seat_z"] = c["wave_height"]-c["wave_cap_depth"]-4-c["bearing_axial_clearance"]
    c["wave_bearing_z"] = c["wave_z"]+c["wave_seat_z"]+c["bearing_axial_clearance"]/2
    c["cam_z"] = c["wave_z"]+c["wave_seat_z"]-1
    c["cam_height"] = 5+c["bearing_axial_clearance"]
    c["outer_spacer_z"] = c["bearing_z"]+5+c["bearing_axial_clearance"]
    c["outer_spacer_length"] = c["cam_z"]-c["outer_spacer_z"]
    c["middle_spacer_z"] = c["cam_z"]+c["cam_height"]
    c["middle_spacer_length"] = c["mirror_z"]-c["middle_spacer_z"]
    c["case_head_seat"] = 3.2
    c["case_screw_length"] = 12
    c["case_nut_z"] = c["case_head_seat"]+c["case_screw_length"]-3
    c["output_head_recess"] = 2.0
    c["output_screw_length"] = 12
    c["wave_head_recess"] = 3.2
    c["wave_screw_length"] = 6
    c["wave_nut_z"] = c["wave_height"]-c["wave_head_recess"]-c["wave_screw_length"]+.3
    available = [6,8,10,12,14,16,18,20,25,30,35]
    def select(target, minimum_seat):
        allowed = [v for v in available if v <= min(c["max_screw_length"],target-minimum_seat+1e-6)]
        if not allowed:
            raise ValueError("No stocked socket cap length fits this stack")
        length = max(allowed)
        return length, target-length
    c["ring_join_screw_length"], c["ring_join_head_seat"] = select(c["joint_z"]+3,c["ring_z"]+3.2)
    c["cage_screw_length"], c["cage_head_seat"] = select(c["joint_z"]+2.6,c["cage_base_z"]+2.2)
    for key in ["case_screw_length", "output_screw_length", "wave_screw_length", "ring_join_screw_length", "cage_screw_length"]:
        if c[key] > c["max_screw_length"]:
            raise ValueError("Screw length exceeds user limit")
    if c["outer_spacer_length"] <= 0 or c["middle_spacer_length"] <= 1:
        raise ValueError("Invalid input spacer stack")
    if c["central_joint_depth"] < 6:
        raise ValueError("Central joint needs 6 mm for opposed nut pockets")
    c["output_direction"] = "opposite_to_input"
    return c


def piece_definitions(**kwargs):
    c = resolve(**kwargs)
    return [
        {
            "name": 'housing_bottom',
            "module": 'housing',
            "arguments": [False],
            "quantity": 1,
            "size": [c['housing_flange_width'], c['housing_flange_width']],
        },
        {
            "name": 'housing_top',
            "module": 'housing',
            "arguments": [True],
            "quantity": 1,
            "size": [c['housing_flange_width'], c['housing_flange_width']],
        },
        {
            "name": 'fixed_profile_ring_lower',
            "module": 'fixed_ring',
            "arguments": [False],
            "quantity": 1,
            "size": [2 * c['housing_radius'], 2 * c['housing_radius']],
        },
        {
            "name": 'fixed_profile_ring_upper',
            "module": 'fixed_ring',
            "arguments": [True],
            "quantity": 1,
            "size": [2 * c['housing_radius'], 2 * c['housing_radius']],
        },
        {
            "name": 'stationary_joint_ring',
            "module": 'stationary_joint',
            "arguments": [],
            "quantity": 1,
            "size": [2 * c['housing_radius'], 2 * c['housing_radius']],
        },
        {
            "name": 'output_cage_lower',
            "module": 'cage',
            "arguments": [False],
            "quantity": 1,
            "size": [2 * c['cage_outer_radius'], 2 * c['cage_outer_radius']],
        },
        {
            "name": 'output_cage_upper',
            "module": 'cage',
            "arguments": [True],
            "quantity": 1,
            "size": [2 * c['cage_outer_radius'], 2 * c['cage_outer_radius']],
        },
        {
            "name": 'output_cage_joint',
            "module": 'cage_joint',
            "arguments": [],
            "quantity": 1,
            "size": [2 * c['cage_joint_radius'], 2 * c['cage_joint_radius']],
        },
        {
            "name": 'output_bearing_hub',
            "module": 'output_hub',
            "arguments": [],
            "quantity": 2,
            "size": [50, 50],
        },
        {
            "name": 'output_bearing_retainer',
            "module": 'output_retainer',
            "arguments": [],
            "quantity": 2,
            "size": [53, 53],
        },
        {
            "name": 'wave_generator',
            "module": 'wave_generator',
            "arguments": [],
            "quantity": 2,
            "size": [2 * c['wave_radius'], 2 * c['wave_radius']],
        },
        {
            "name": 'wave_bearing_cap',
            "module": 'wave_cap',
            "arguments": [],
            "quantity": 2,
            "size": [44, 44],
        },
        {
            "name": 'eccentric_cam_lower',
            "module": 'eccentric_cam',
            "arguments": [False],
            "quantity": 1,
            "size": [24, 24],
        },
        {
            "name": 'eccentric_cam_upper',
            "module": 'eccentric_cam',
            "arguments": [True],
            "quantity": 1,
            "size": [24, 24],
        },
        {
            "name": 'input_bearing_journal',
            "module": 'input_journal',
            "arguments": [],
            "quantity": 2,
            "size": [22, 22],
        },
        {
            "name": 'input_spacer_outer',
            "module": 'input_spacer',
            "arguments": [c['outer_spacer_length'], False, False],
            "quantity": 2,
            "size": [22, 22],
        },
        {
            "name": 'input_spacer_middle_lower',
            "module": 'input_spacer',
            "arguments": [c['middle_spacer_length'], True, False],
            "quantity": 1,
            "size": [24, 24],
        },
        {
            "name": 'input_spacer_middle_upper',
            "module": 'input_spacer',
            "arguments": [c['middle_spacer_length'], True, True],
            "quantity": 1,
            "size": [24, 24],
        },
        {
            "name": 'input_collar',
            "module": 'input_collar',
            "arguments": [],
            "quantity": 2,
            "size": [36, 36],
        },
    ]


def hardware_definitions(**kwargs):
    definitions = []
    for size in ["m2", "m3", "m6"]:
        definitions.append({
            "name": "oobb_hole_"+size,
            "kwargs": {
                "shape": "oobb_hole",
                "type": "p",
                "radius_name": size,
                "depth": 1,
                "pos": [0,0,0],
                "mode": "3dpr",
                "overhang": True,
            },
        })
    for size,depth in [("m2",2.2),("m3",2.7)]:
        definitions.append({
            "name": "oobb_nut_"+size,
            "kwargs": {
                "shape": "oobb_nut",
                "type": "p",
                "radius_name": size,
                "depth": depth,
                "pos": [0,0,0],
                "zz": "bottom",
                "mode": "3dpr",
                "overhang": True,
            },
        })
        definitions.append({
            "name": "oobb_socket_"+size,
            "kwargs": {
                "shape": "oobb_screw_socket_cap",
                "type": "p",
                "radius_name": size,
                "depth": 1,
                "pos": [0,0,0],
                "zz": "none",
                "hole": False,
                "nut_include": False,
                "mode": "3dpr",
                "overhang": True,
            },
        })
    return definitions


def bom(**kwargs):
    c = resolve(**kwargs)
    return [
        {
            'item': '6810 bearing',
            'quantity': 2,
            'dimensions': '50 x 65 x 7 mm',
            'role': 'output cage support',
        },
        {
            'item': '6704 bearing',
            'quantity': 4,
            'dimensions': '20 x 27 x 4 mm',
            'role': 'two input supports and two opposed wave bearings',
        },
        {
            'item': 'Nylon spacer roller',
            'quantity': c['total_roller_count'],
            'dimensions': f'{c['roller_diameter']:g} OD x {c['roller_bore_diameter']:g} ID x {c['roller_length']:g} mm',
            'role': 'two independent banks; free rollers, no fixed axle',
        },
        {
            'item': '5 mm D shaft',
            'quantity': 1,
            'dimensions': f'{c['shaft_length']} mm long',
            'role': 'shared keyed input',
        },
        {
            'item': 'Case socket cap screw',
            'size': 'M3',
            'length_mm': c['case_screw_length'],
            'quantity': 2 * c['housing_screw_count'],
            'role': 'end housings to profile rings',
        },
        {
            'item': 'Ring joint socket cap screw',
            'size': 'M3',
            'length_mm': c['ring_join_screw_length'],
            'quantity': 2 * c['housing_screw_count'],
            'role': 'profile rings to stationary centre ring',
        },
        {
            'item': 'Output socket cap screw',
            'size': 'M3',
            'length_mm': c['output_screw_length'],
            'quantity': 16,
            'role': 'retainers, bearing hubs and cage floors',
        },
        {
            'item': 'Wave cap socket cap screw',
            'size': 'M3',
            'length_mm': c['wave_screw_length'],
            'quantity': 8,
            'role': 'two wave bearing caps',
        },
        {
            'item': 'Cage joint socket cap screw',
            'size': 'M2',
            'length_mm': c['cage_screw_length'],
            'quantity': 2 * c['cage_screw_count'],
            'role': 'two cage halves to one central output plate',
        },
        {
            'item': 'M3 x 8 grub screw',
            'quantity': 2,
            'length_mm': 8,
            'role': 'shaft collars',
        },
        {
            'item': 'M3 hex nut',
            'quantity': 4 * c['housing_screw_count'] + 26,
            'role': 'cases, stationary joints, output hubs, wave caps and collars',
        },
        {
            'item': 'M2 hex nut',
            'quantity': 2 * c['cage_screw_count'],
            'role': 'cage centre joint',
        },
    ]
