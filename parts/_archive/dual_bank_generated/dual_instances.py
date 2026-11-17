"""Explicit placements for the dual-bank SCAD assembly and nominal hardware."""
import copy
import math

from wave_components.wave_profile.working import motion


def instance_definitions(**kwargs):
    from working_blender import transform
    c = copy.deepcopy(kwargs["configuration"])
    records = []

    def add(**item):
        item = copy.deepcopy(item)
        item.setdefault("name",item["part"])
        item.setdefault("pos",[0,0,0])
        item.setdefault("material","teal")
        item.setdefault("kind","printed")
        item.setdefault("group","fixed")
        item.setdefault("level",8)
        item.setdefault("open",True)
        item.setdefault("mirror",False)
        item["matrix"] = transform(height=c["assembly_height"],**item).tolist()
        records.append(item)

    def hardware(**item):
        item.setdefault("kind","fastener")
        item.setdefault("group","fasteners")
        item.setdefault("material","steel" if item["part"].startswith("nut_") else "bolt")
        add(**item)

    add(**{
        "part":"stationary_joint_ring",
        "pos":[0,0,c["joint_z"]],
        "open":False,
    })
    add(**{
        "part":"output_cage_joint",
        "pos":[0,0,c["joint_z"]],
        "group":"cage",
        "material":"black",
        "open":False,
    })
    add(**{
        "part":"shaft",
        "pos":[0,0,-12],
        "kind":"shaft",
        "group":"input",
        "material":"steel",
    })
    mounts = [(x,y) for x in [-15,-7.5,7.5,15] for y in [-15,-7.5,7.5,15] if abs(x)!=abs(y)]
    for upper in [False,True]:
        suffix = "upper" if upper else "lower"
        ex = -c["eccentricity"] if upper else c["eccentricity"]
        clock = 11.25 if upper else 0
        pieces = [
            ("housing_top" if upper else "housing_bottom",0,0,"fixed","teal",0),
            ("fixed_profile_ring_"+suffix,0,c["ring_z"],"fixed","teal",3),
            ("output_cage_"+suffix,0,c["cage_base_z"],"cage","black",4),
            ("output_bearing_hub",0,c["bearing_z"],"cage","black",2),
            ("output_bearing_retainer",0,c["bearing_z"]-c["retainer_depth"],"cage","black",1),
            ("wave_generator",ex,c["wave_z"],"wave","teal",5),
            ("wave_bearing_cap",ex,c["wave_z"]+c["wave_height"]-c["wave_cap_depth"],"wave","teal",6),
            ("eccentric_cam_"+suffix,0,c["cam_z"],"input","black",6),
            ("input_bearing_journal",0,c["bearing_z"],"input","yellow",2),
            ("input_spacer_outer",0,c["outer_spacer_z"],"input","black",4),
            ("input_spacer_middle_"+suffix,0,c["middle_spacer_z"],"input","black",7),
            ("input_collar",0,c["bearing_z"]-13,"input","yellow",-1),
        ]
        for part,x,z,group,material,level in pieces:
            add(**{
                "part":part,
                "name":part if part.endswith(("lower","upper","bottom","top")) else part+"_"+suffix,
                "pos":[x,0,z],
                "mirror":upper,
                "group":group,
                "material":material,
                "level":16-level if upper else level,
                "open":not upper,
            })
        for part,x,z,level,label in [
            ("bearing_6810",0,c["bearing_z"],2,"output"),
            ("bearing_6704",0,c["bearing_z"]+c["bearing_axial_clearance"]/2,2,"input"),
            ("bearing_6704",ex,c["wave_bearing_z"],5,"wave"),
        ]:
            add(**{
                "part":part,
                "name":part+"_"+label+"_"+suffix,
                "pos":[x,0,z],
                "mirror":upper,
                "kind":"bearing",
                "group":"bearings",
                "material":"steel",
                "level":16-level if upper else level,
                "open":not upper,
            })
        config = copy.deepcopy(c)
        config["bank_phase_degrees"] = 180 if upper else 0
        for index,point in enumerate(motion(0,**config)["roller_centers"]):
            add(**{
                "part":"roller",
                "name":f"roller_{suffix}_{index:02d}",
                "pos":[*map(float,point),c["roller_z"]],
                "mirror":upper,
                "kind":"roller",
                "group":"rollers",
                "material":"nylon",
                "level":11 if upper else 5,
                "open":not upper,
            })
        for index in range(c["housing_screw_count"]):
            for join in [False,True]:
                angle = math.radians(clock+(22.5 if join else 0)+(5 if join and index==0 else 0)+360*index/c["housing_screw_count"])
                xy = [c["housing_screw_pitch_radius"]*math.cos(angle),c["housing_screw_pitch_radius"]*math.sin(angle)]
                label = "ring_join" if join else "case"
                hardware(**{
                    "part":"screw_"+label,
                    "name":f"{label}_screw_{suffix}_{index:02d}",
                    "pos":xy+[c["ring_join_head_seat"] if join else c["case_head_seat"]],
                    "rotation_y":180,
                    "mirror":upper,
                    "level":14 if upper else 2,
                    "open":False if upper else not join,
                })
                hardware(**{
                    "part":"nut_m3",
                    "name":f"{label}_nut_{suffix}_{index:02d}",
                    "rotation_z":math.degrees(angle),
                    "pos":xy+[c["joint_z"] if join else c["case_nut_z"]],
                    "mirror":upper,
                    "level":8 if join else 13 if upper else 3,
                    "open":False if join else not upper,
                })
        for index,(x,y) in enumerate(mounts):
            hardware(**{
                "part":"screw_output",
                "name":f"output_screw_{suffix}_{index:02d}",
                "pos":[x,y,c["bearing_z"]-c["retainer_depth"]+c["output_head_recess"]],
                "rotation_y":180,
                "mirror":upper,
                "level":15 if upper else 1,
                "open":not upper,
            })
            hardware(**{
                "part":"nut_m3",
                "name":f"output_nut_{suffix}_{index:02d}",
                "pos":[x,y,c["window_z"]-2.7],
                "mirror":upper,
                "level":12 if upper else 4,
                "open":not upper,
            })
        for index in range(c["cage_screw_count"]):
            angle = math.radians(180/c["roller_count"]+(360/c["roller_count"] if upper else 0)+360*index/c["cage_screw_count"])
            xy = [c["pitch_radius"]*math.cos(angle),c["pitch_radius"]*math.sin(angle)]
            hardware(**{
                "part":"screw_cage",
                "name":f"cage_screw_{suffix}_{index:02d}",
                "pos":xy+[c["cage_head_seat"]],
                "rotation_y":180,
                "mirror":upper,
                "level":13 if upper else 3,
                "open":not upper,
            })
            hardware(**{
                "part":"nut_m2",
                "name":f"cage_nut_{suffix}_{index:02d}",
                "rotation_z":math.degrees(angle),
                "pos":xy+[c["joint_z"]],
                "mirror":upper,
                "level":8,
                "open":False,
            })
        for index in range(4):
            angle = math.pi*index/2
            xy = [ex+18*math.cos(angle),18*math.sin(angle)]
            hardware(**{
                "part":"screw_wave",
                "name":f"wave_screw_{suffix}_{index:02d}",
                "pos":xy+[c["wave_z"]+c["wave_height"]-c["wave_head_recess"]],
                "mirror":upper,
                "level":10 if upper else 6,
                "open":not upper,
            })
            hardware(**{
                "part":"nut_m3",
                "name":f"wave_nut_{suffix}_{index:02d}",
                "pos":xy+[c["wave_z"]+c["wave_nut_z"]],
                "mirror":upper,
                "level":11 if upper else 5,
                "open":not upper,
            })
        for part,x in [("grub_m3",10),("nut_m3",5)]:
            hardware(**{
                "part":part,
                "name":f"collar_{part}_{suffix}",
                "pos":[x,0,c["bearing_z"]-6],
                "rotation_y":90,
                "mirror":upper,
                "level":17 if upper else -1,
                "open":not upper,
            })
    return records
