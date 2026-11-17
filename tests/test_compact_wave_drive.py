"""Single-bank motion, motor load path, packaging and fastener engagement."""
import copy
from collections import Counter
import math
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import Point, Polygon

import working_scad
from wave_drive.wave_profile import working as profile

ROOT = Path(__file__).resolve().parents[1]


def test_single_bank_full_cycle_clearance_and_ratio():
    c = working_scad.resolve()
    ring = Polygon(profile.action(**c))
    for alpha in np.linspace(0, 360, 361):
        state = profile.motion(float(alpha), **c)
        centers = np.asarray(state["roller_centers"])
        assert len(centers) == 12
        assert np.allclose(np.linalg.norm(centers-np.asarray(state["wave_center"]),axis=1), c["pitch_radius"], atol=1e-10)
        for index, center in enumerate(centers):
            p = Point(center)
            assert ring.contains(p)
            assert c["profile_clearance"]-.002 < ring.boundary.distance(p)-c["roller_radius"] < c["profile_clearance"]+.002
            theta = math.radians(state["output_angle"])+2*math.pi*index/12
            assert abs(np.dot(center, [-math.sin(theta),math.cos(theta)])) < 1e-10
    assert profile.motion(360, **c)["output_angle"] == pytest.approx(-30)
    assert profile.motion(4320, **c)["output_angle"] == pytest.approx(-360)


def test_compact_inventory_and_bearing_envelope():
    from wave_drive.instances import instance_definitions
    c = working_scad.resolve()
    pieces = working_scad.piece_definitions(**c)
    records = instance_definitions(configuration=c)
    assert len(pieces) == sum(p["quantity"] for p in pieces) == 11
    assert Counter(r["kind"] for r in records) == {"printed":11,"roller":12,"bearing":2,"fastener":75}
    assert sum(r["part"]=="bearing_6810" for r in records) == 1
    assert sum(r["part"]=="bearing_6704" for r in records) == 1
    assert len(records) == len(set(r["name"] for r in records))
    assert c["roller_length"] == 12 and c["roller_diameter"] == 7
    assert c["base_edge_radius"] == 1.5
    assert c["output_plate_diameter"] == 65
    assert c["output_grid_pitch"] == 15
    assert c["hub_height"]-c["shaft_blind_depth"] >= .5
    assert c["assembly_height"]-c["housing_top_z"] == pytest.approx(1.5)
    assert 2*c["housing_radius"] == pytest.approx(71.2)
    assert c["housing_flange_width"] == 104
    assert c["housing_flange_height"] == 74
    assert c["housing_flange_corner_radius"] == 5
    for d in working_scad.hardware_definitions(**c):
        assert d["kwargs"]["overhang"] is True
    assert any(d["kwargs"]["shape"] == "oobb_screw_countersunk" for d in working_scad.hardware_definitions(**c))


def test_motor_shaft_and_screw_engagement():
    c = working_scad.resolve()
    assert c["cam_cap_z"]+c["cam_cap_height"] < c["motor_shaft_length"]-1
    assert c["motor_pilot_height"]+.2 < c["motor_plate_depth"]
    # Every tooth gets a screw, tightened from above before the 6810 is fitted.
    assert c["cage_screw_count"] == c["roller_count"] == 12
    for i in range(c["cage_screw_count"]):
        a = math.radians(180/c["roller_count"]+360*i/c["cage_screw_count"])
        x,y = c["cage_screw_radius"]*math.cos(a), c["cage_screw_radius"]*math.sin(a)
        assert math.hypot(x,y)-1 > 25-c["journal_clearance"]
    assert c["cage_head_seat"]-c["cage_screw_length"] <= c["cage_nut_z"]
    assert c["cage_nut_z"] > c["cage_cap_z"]
    assert c["cage_screw_length"] == 20
    assert c["cage_head_lift"] == pytest.approx(3)
    assert c["cage_tip_clearance"] == pytest.approx(1.6)
    assert c["cage_nut_z"]+1.6 < c["roller_z"]
    assert c["cage_upper_plate_depth"] == pytest.approx(6)
    engagement = c["motor_screw_length"]-c["motor_head_seat"]
    assert 3 <= engagement <= c["motor_thread_depth"]-.5
    # Full nominal nut engagement, and no screw projecting into the other moving body.
    for seat, length, floor, thickness in [
        (c["case_head_seat"], c["case_screw_length"], c["case_nut_z"], 2.5),
    ]:
        assert seat-length <= floor+1e-8
        assert seat-length >= -.1
    assert c["motor_screw_length"] == 8
    assert c["motor_head_seat"] == c["motor_plate_depth"]+c["countersunk_head_proud"]
    primitive = next(d for d in working_scad.hardware_definitions(**c) if d["name"] == "oobb_motor_countersunk_m3")["kwargs"]
    assert primitive["shape"] == "oobb_screw_countersunk"
    assert primitive["clearance"] == "top"
    from wave_drive.instances import instance_definitions
    placements = instance_definitions(configuration=c)
    case_screws = [r for r in placements if r["part"] == "screw_case"]
    assert len(case_screws) == 6
    assert all(r.get("rotation_y", 0) == 0 for r in case_screws)
    assert c["case_nut_z"]+2.5 < c["motor_plate_depth"]
    output_tip = c["output_head_seat"]-c["output_screw_length"]
    assert output_tip <= c["output_nut_z"]+1e-8
    assert output_tip > c["wave_z"]+c["wave_height"]
    wave_tip = c["wave_height"]-c["wave_head_recess"]-c["wave_screw_length"]
    assert 0 <= wave_tip < c["wave_nut_z"]
    assert c["wave_nut_z"]+2.5 < c["wave_lower_depth"]
    assert c["wave_head_recess"] == -c["countersunk_head_proud"]
    eccentric_nuts = [r for r in placements if r["name"].startswith("eccentric_join_nut_")]
    assert len(eccentric_nuts) == 2 and all(r["part"] == "nut_m3" for r in eccentric_nuts)
    assert c["eccentric_join_head_z"]-c["eccentric_join_screw_length"] <= c["eccentric_join_nut_z"]
    assert c["eccentric_join_nut_z"]+2.5 < c["cam_z"]
    assert c["cage_head_seat"] < c["bearing_z"]
    for row in working_scad.bom(**c):
        if "length_mm" in row:
            assert row["length_mm"] <= 35


def test_output_sandwich_pocket_walls_and_capture():
    c = working_scad.resolve()
    assert len(c["output_m6_mounts"]) == 5
    assert len(c["output_m3_mounts"]) == 8
    pockets = [(p, c["mount_m6_pocket_radius"]) for p in c["output_m6_mounts"]]
    pockets += [(p, c["mount_m3_pocket_radius"]) for p in c["output_m3_mounts"]]
    for index, (point, radius) in enumerate(pockets):
        for other, other_radius in pockets[index+1:]:
            assert math.dist(point, other)-radius-other_radius >= c["mount_minimum_web"]
    from wave_drive.compact_recipe import output_m3_pocket_points
    import oobb
    assert c["mount_m3_hex_radius"] == pytest.approx(oobb.gv("nut_radius_m3","3dpr"))
    for point in c["output_m3_mounts"]:
        for vertex in output_m3_pocket_points(point, **c):
            assert math.hypot(*vertex)+c["mount_m3_edge_wall"] <= 25-c["journal_clearance"]
        for fixing in c["output_fixing_mounts"]:
            assert math.dist(point,fixing) >= c["mount_m3_pocket_radius"]+1.8+c["mount_minimum_web"]
    assert all([x,y] in c["output_m3_mounts"] for x in [-15,15] for y in [-15,15])
    assert c["output_head_seat"]-c["assembly_height"] == pytest.approx(1)
    assert c["output_screw_length"] == 16
    for key, height in [("output_attachment_nut_z",5), ("output_m3_attachment_nut_z",2.5)]:
        assert c[key]+height < c["output_cover_z"]
        assert c[key] > c["hub_z"]+c["shaft_blind_depth"]
    assert c["output_attachment_nut_z"]-.1-.6-(c["hub_z"]+c["shaft_blind_depth"]) >= .5-1e-8


def test_bearing_clamshell_eccentric_joint_and_case_walls():
    c = working_scad.resolve()
    assert c["wave_split_z"] == pytest.approx(c["wave_bearing_z"]+c["wave_bearing"]["depth"]/2)
    assert c["wave_lower_depth"]+c["wave_cap_depth"] == pytest.approx(c["roller_length"])
    assert c["wave_lower_depth"]-c["wave_seat_z"] == pytest.approx(2.1)
    assert c["eccentric_join_head_z"]-c["eccentric_join_screw_length"] < c["eccentric_join_nut_z"]
    assert c["eccentric_join_nut_z"]+1.6 < c["cam_z"]
    assert c["eccentric_join_pitch_radius"]-1.35 > c["input_shaft_diameter"]/2+c["shaft_fit_clearance"]
    assert c["housing_radius"]-(32.5+c["bearing_seat_clearance"]) >= 3-1e-8
    assert c["case_boss_radius"]-c["mount_m3_pocket_radius"] >= 2-1e-8
    assert c["housing_screw_pitch_radius"]-c["mount_m3_pocket_radius"]-(32.5+c["bearing_seat_clearance"]) >= 2-1e-8
    assert c["case_boss_inner_radius"] < c["housing_radius"]
    assert c["case_boss_corner_radius"] == pytest.approx(5.7)
    assert c["case_boss_outer_radius"]-c["case_boss_corner_radius"] == pytest.approx(c["housing_screw_pitch_radius"])


def test_insertion_clearances_and_visible_output_gap():
    c = working_scad.resolve()
    assert c["cage_center_diameter"]/2 > 11+c["eccentricity"]+.5
    assert c["output_face_clearance"] == .8 and c["output_radial_clearance"] == .6
    assert c["assembly_height"]-c["output_flange_z"] >= .7-1e-8
    primitive = next(d for d in working_scad.hardware_definitions(**c) if d["name"] == "oobb_cage_countersunk_m2")["kwargs"]
    assert primitive["clearance"] == "top" and primitive["overhang"] is True


def test_proud_m3_heads_clear_rotating_cage_and_retain_threads():
    c = working_scad.resolve()
    assert c["motor_head_relief_depth"] == pytest.approx(1)
    assert c["wave_head_relief_depth"] == pytest.approx(1)
    assert c["cage_cap_z"]+c["motor_head_relief_depth"]-c["motor_head_seat"] == pytest.approx(.3)
    assert c["cage_floor_z"]+c["wave_head_relief_depth"]-(c["wave_z"]+c["wave_height"]-c["wave_head_recess"]) == pytest.approx(.3)
    assert c["cage_plate_depth"]-c["motor_head_relief_depth"] >= 2-1e-8
    assert c["eccentric_join_head_z"]-c["cam_cap_z"]-c["cam_cap_height"] == pytest.approx(1)
    assert c["eccentric_join_nut_z"]-(c["eccentric_join_head_z"]-c["eccentric_join_screw_length"]) == pytest.approx(.1)
    assert c["wave_nut_z"]-(c["wave_height"]-c["wave_head_recess"]-c["wave_screw_length"]) == pytest.approx(.3)


def test_shaft_clamp_service_path_and_countersunk_head():
    c = working_scad.resolve()
    assert c["input_shaft_flat_depth"] == 0
    assert c["input_shaft_diameter"] == 5
    assert c["shaft_clamp_z"]+c["shaft_access_diameter"]/2 < c["roller_z"]
    assert c["shaft_driver_diameter"] < c["shaft_access_diameter"]
    assert c["shaft_clamp_head_radius"]-c["shaft_clamp_screw_length"] == pytest.approx(c["input_shaft_diameter"]/2-c["input_shaft_flat_depth"])
    assert c["cam_base_z"] > c["motor_pilot_height"]+.1
    primitive = next(d for d in working_scad.hardware_definitions(**c) if d["name"] == "oobb_shaft_clamp_m3")["kwargs"]
    assert primitive["shape"] == "oobb_screw_countersunk"
    assert primitive["radius_name"] == "m3" and primitive["clearance"] == "top"
    # Case bolts must not sit in the radial +X driver corridor.
    for i in range(c["housing_screw_count"]):
        angle = math.radians(c["housing_screw_angle"]+360*i/c["housing_screw_count"])
        x,y = c["housing_screw_pitch_radius"]*math.cos(angle), c["housing_screw_pitch_radius"]*math.sin(angle)
        if x > 0:
            assert abs(y) > 1.5+c["shaft_driver_diameter"]/2


def test_settings_copy_and_smaller_ratio():
    supplied = {"reduction":8}
    before = copy.deepcopy(supplied)
    c = working_scad.resolve(**supplied)
    assert supplied == before
    assert profile.motion(360, **c)["output_angle"] == pytest.approx(-45)


@pytest.mark.parametrize("override", [
    {"roller_bank_count":2}, {"reduction":20}, {"reduction":0},
    {"reduction":12.5}, {"overhang":False}, {"max_screw_length":40},
    {"output_holder_wall":2.9}, {"wave_radius":22}, {"eccentricity":2},
    {"profile_clearance":-.1}, {"roller_bore_diameter":8},
    {"bearing_output":"6808"}, {"roller_length":8}, {"roller_length":30},
    {"motor_shaft_length":20}, {"motor_thread_depth":3},
])
def test_invalid_changes_rejected(override):
    with pytest.raises(ValueError):
        working_scad.resolve(**override)


def test_portable_scad_and_complete_print_beds():
    folder = next(path.parent for path in (ROOT/"parts").glob("*/manifest.json"))
    for name in ["parameters.scad","geometry.scad","compact_helpers.scad","oobb_hardware.scad","assembly.scad"]:
        contents = (folder/name).read_text()
        assert "import(" not in contents
        assert "C:/" not in contents and "C:\\" not in contents
    pieces = working_scad.piece_definitions()
    expected = {(p["name"],i) for p in pieces for i in range(p["quantity"])}
    found = []
    for bed in working_scad.pack_print_beds(pieces):
        for i,p in enumerate(bed["parts"]):
            found.append((p["part"],p["instance"]))
            x,y = p["xy"]; w,h = p["size"]
            assert min(x-w/2,y-h/2) >= 3
            assert max(x+w/2,y+h/2) <= 217
            for q in bed["parts"][i+1:]:
                xx,yy = q["xy"]; ww,hh = q["size"]
                assert abs(x-xx)>=(w+ww)/2+3.99 or abs(y-yy)>=(h+hh)/2+3.99
    assert set(found)==expected and len(found)==len(expected)


def test_optional_printable_spacers_are_packed_without_duplicate_assembly_parts():
    from wave_drive.compact_recipe import optional_print_definitions
    c = working_scad.resolve()
    pieces = working_scad.piece_definitions(**c)
    extra = optional_print_definitions(**c)
    assert len(extra) == 1 and extra[0]["quantity"] == 12
    assert extra[0]["module"] == "roller" and extra[0]["replaces"] == "roller"
    beds = working_scad.pack_print_beds(pieces+extra)
    assert sum(len(bed["parts"]) for bed in beds) == 23
    assert sum(p["part"] == "printable_spacer" for bed in beds for p in bed["parts"]) == 12
    assert optional_print_definitions(include_printable_spacers=False) == []
