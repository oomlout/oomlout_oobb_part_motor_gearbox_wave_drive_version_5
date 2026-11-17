"""Local OOBB hardware helpers; no library edits."""
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


def hardware_definitions(**kwargs):
    definitions = [
        {
            "name": "oobb_motor_countersunk_m3",
            "kwargs": {
                "shape": "oobb_screw_countersunk",
                "type": "p",
                "radius_name": "m3",
                "depth": kwargs.get("motor_screw_length", 8),
                "pos": [0, 0, 0],
                "zz": "top",
                "hole": False,
                "nut_include": False,
                "clearance": "top",
                "mode": "3dpr",
                "overhang": True,
            },
        },
        {
            "name": "oobb_cage_countersunk_m2",
            "kwargs": {
                "shape": "oobb_screw_countersunk",
                "type": "p",
                "radius_name": "m2",
                "depth": 1,
                "pos": [0, 0, 0],
                "zz": "top",
                "hole": False,
                "nut_include": False,
                "clearance": "top",
                "mode": "3dpr",
                "overhang": True,
            },
        },
        {
            "name": "oobb_shaft_clamp_m3",
            "kwargs": {
                "shape": "oobb_screw_countersunk",
                "type": "p",
                "radius_name": "m3",
                "depth": kwargs.get("shaft_clamp_screw_length", 8),
                "pos": [0, 0, 0],
                "zz": "top",
                "hole": False,
                "nut_include": False,
                "clearance": "top",
                "mode": "3dpr",
                "overhang": True,
            },
        },
        {
            "name": "oobb_countersunk_m3",
            "kwargs": {
                "shape": "oobb_screw_countersunk",
                "type": "p",
                "radius_name": "m3",
                "depth": 1,
                "pos": [0, 0, 0],
                "zz": "top",
                "hole": False,
                "nut_include": False,
                "clearance": "top",
                "mode": "3dpr",
                "overhang": True,
            },
        },
        {
            "name": "oobb_motor_plate_body",
            "kwargs": {
                "shape": "oobb_rounded_rectangle_rounded",
                "type": "p",
                "size": [
                    kwargs.get("base_width",6)*kwargs.get("oobb_grid_pitch",15)-kwargs.get("oobb_size_allowance",1),
                    kwargs.get("base_height",6)*kwargs.get("oobb_grid_pitch",15)-kwargs.get("oobb_size_allowance",1),
                    kwargs.get("motor_plate_depth",4),
                ],
                "radius": kwargs.get("housing_flange_corner_radius",5.0),
                "radius_top": kwargs.get("base_edge_radius",1.5),
                "radius_bottom": kwargs.get("base_edge_radius",1.5),
                "pos": [0,0,0],
                "overhang": True,
            },
        },
    ]
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
    for size,depth in [("m2",2.2),("m3",2.7),("m6",kwargs.get("output_nut_depth",5.2))]:
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
        if size == "m6":
            continue
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

