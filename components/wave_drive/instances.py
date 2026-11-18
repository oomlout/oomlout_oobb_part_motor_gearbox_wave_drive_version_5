"""Named single-bank placements; verified against the native SCAD assembly."""
import copy
import math

from wave_drive.wave_profile.working import motion


def instance_definitions(**kwargs):
    from wave_drive.render_pipeline import transform
    c = copy.deepcopy(kwargs["configuration"])
    records = []

    def add(**item):
        item = copy.deepcopy(item)
        item.setdefault("name", item["part"])
        item.setdefault("pos", [0, 0, 0])
        item.setdefault("kind", "printed")
        item.setdefault("group", "fixed")
        item.setdefault("material", "teal")
        item.setdefault("level", 0)
        item.setdefault("open", True)
        item.setdefault("height", 0)
        item["matrix"] = transform(**item).tolist()
        records.append(item)

    def hardware(**item):
        item.setdefault("kind", "fastener")
        item.setdefault("group", "fasteners")
        item.setdefault("material", "steel" if item["part"].startswith("nut_") else "bolt")
        add(**item)

    add(**{
        "part": "motor_mount_plate",
        "level": 0,
    })
    add(**{
        "part": "fixed_profile_ring",
        "pos": [0, 0, c["ring_z"]],
        "level": 2,
        "open": False,
    })
    add(**{
        "part": "output_bearing_housing",
        "mirror": True,
        "height": c["housing_top_z"],
        "level": 12,
        "open": False,
    })
    for item in [
        {
            "part": "cage_lower_cap",
            "pos": [0, 0, c["cage_cap_z"]],
            "level": 1,
        },
        {
            "part": "output_cage",
            "pos": [0, 0, c["cage_floor_z"]],
            "level": 9,
            "open": False,
        },
        {
            "part": "output_retainer",
            "mirror": True,
            "height": c["output_cover_z"],
            "level": 13,
            "open": False,
        },
        {
            "part": "output_cover",
            "pos": [0, 0, c["output_cover_z"]],
            "level": 14,
            "open": False,
        },
    ]:
        add(**{
            **item,
            "group": "cage",
            "material": "black",
        })
    for part, z, level in [
        ("motor_eccentric", c["cam_base_z"], 3),
        ("motor_eccentric_cap", c["cam_cap_z"], 6),
    ]:
        add(**{
            "part": part,
            "pos": [0, 0, z],
            "group": "input",
            "material": "yellow",
            "level": level,
        })
    for part, z, level in [
        ("wave_generator", c["wave_z"], 4),
        ("wave_bearing_cap", c["wave_split_z"], 7),
    ]:
        add(**{
            "part": part,
            "pos": [c["eccentricity"], 0, z],
            "group": "wave",
            "level": level,
        })
    for part, x, z, level in [
        ("bearing_6810", 0, c["bearing_z"], 11),
        ("bearing_6704", c["eccentricity"], c["wave_bearing_z"], 5),
    ]:
        add(**{
            "part": part,
            "pos": [x, 0, z],
            "kind": "bearing",
            "group": "bearings",
            "material": "steel",
            "level": level,
            "open": part == "bearing_6704",
        })
    for index, point in enumerate(motion(0, **c)["roller_centers"]):
        add(**{
            "part": "roller",
            "name": f"roller_{index:02d}",
            "pos": [*map(float, point), c["roller_z"]],
            "kind": "roller",
            "group": "rollers",
            "material": "nylon",
            "level": 8,
        })
    # A screw's native head extends above zero and its shaft points down.
    for index in range(c["housing_screw_count"]):
        angle = c["housing_screw_angle"]+360*index/c["housing_screw_count"]
        xy = [c["housing_screw_pitch_radius"]*math.cos(math.radians(angle)), c["housing_screw_pitch_radius"]*math.sin(math.radians(angle))]
        hardware(**{
            "part": "screw_case",
            "name": f"case_screw_{index}",
            "pos": xy+[c["case_head_seat"]],
            "level": 12,
            "open": False,
        })
        hardware(**{
            "part": "nut_m3",
            "name": f"case_nut_{index}",
            "pos": xy+[c["case_nut_z"]],
            "rotation_z": angle,
            "level": 0,
            "open": False,
        })
    for index, (x, y) in enumerate(( (x,y) for x in [-c["motor_hole_pitch"]/2,c["motor_hole_pitch"]/2] for y in [-c["motor_hole_pitch"]/2,c["motor_hole_pitch"]/2] )):
        hardware(**{
            "part": "screw_motor",
            "name": f"motor_screw_{index}",
            "pos": [x, y, c["motor_head_seat"]],
            "level": 0,
        })
    for label, radius, offset, seat, nut_z, screw_level, nut_level in [
        ("output", 20, 0, c["output_head_seat"], c["output_nut_z"], 14, 9),
        ("wave", 18, c["eccentricity"], c["wave_z"]+c["wave_height"]-c["wave_head_recess"], c["wave_z"]+c["wave_nut_z"], 7, 4),
    ]:
        for index in range(4):
            xy = (c["output_fixing_mounts"][index] if label == "output" else [offset+radius*math.cos(math.pi*index/2), radius*math.sin(math.pi*index/2)])
            hardware(**{
                "part": "screw_"+label,
                "name": f"{label}_screw_{index}",
                "pos": xy+[seat],
                "level": screw_level,
                "open": label == "wave",
            })
            hardware(**{
                "part": "nut_m3",
                "name": f"{label}_nut_{index}",
                "pos": xy+[nut_z],
                "level": nut_level,
                "open": label == "wave",
            })
    for index in range(c["cage_screw_count"]):
        angle = 180/c["roller_count"]+360*index/c["cage_screw_count"]
        xy = [c["cage_screw_radius"]*math.cos(math.radians(angle)), c["cage_screw_radius"]*math.sin(math.radians(angle))]
        hardware(**{
            "part": "screw_cage",
            "name": f"cage_screw_{index}",
            "pos": xy+[c["cage_head_seat"]],
            "level": 9,
            "open": False,
        })
        hardware(**{
            "part": "nut_m2",
            "name": f"cage_nut_{index}",
            "pos": xy+[c["cage_nut_z"]],
            "rotation_z": angle,
            "level": 1,
            "open": False,
        })
    for index, (z, level) in enumerate([(c["shaft_clamp_z"],6)]):
        for part, x in [("screw_shaft_clamp",c["shaft_clamp_head_radius"]), ("nut_m3",5)]:
            hardware(**{
                "part": part,
                "name": f"motor_clamp_{index}_{part}",
                "pos": [x, 0, z],
                "rotation_y": 90,
                "level": level,
            })
    for index, y in enumerate([-c["eccentric_join_pitch_radius"], c["eccentric_join_pitch_radius"]]):
        hardware(**{
            "part": "screw_eccentric",
            "name": f"eccentric_join_screw_{index}",
            "pos": [c["eccentricity"], y, c["eccentric_join_head_z"]],
            "level": 6,
        })
        hardware(**{
            "part": "nut_m3",
            "name": f"eccentric_join_nut_{index}",
            "pos": [c["eccentricity"], y, c["eccentric_join_nut_z"]],
            "level": 3,
        })
    for index, xy in enumerate(c["output_m6_mounts"]):
        hardware(**{
            "part": "nut_m6",
            "name": f"output_attachment_nut_{index}",
            "pos": xy+[c["output_attachment_nut_z"]],
            "level": 13.5,
            "open": False,
        })
    for index, xy in enumerate(c["output_m3_mounts"]):
        hardware(**{
            "part": "nut_m3",
            "name": f"output_attachment_m3_nut_{index}",
            "pos": xy+[c["output_m3_attachment_nut_z"]],
            "rotation_z": math.degrees(math.atan2(xy[1],xy[0]))-30,
            "level": 13.5,
            "open": False,
        })
    for index, xy in enumerate(c["output_plate_clamp_mounts"]):
        for part, z in [("screw_output_clamp", c["output_head_seat"]), ("nut_m3", c["output_plate_clamp_nut_z"])]:
            hardware(**{
                "part": part,
                "name": f"plate_clamp_{index}_{part}",
                "pos": xy+[z],
                "level": 14,
                "open": False,
            })
    return records
