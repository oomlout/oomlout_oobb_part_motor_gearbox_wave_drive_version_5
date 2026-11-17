"""Independent geometry, phase, inventory and stock-length checks."""
import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import Point, Polygon

import working_scad
from wave_components.wave_profile import working as profile

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def config():
    return working_scad.resolve()


def test_two_bank_motion_clearance_and_ratio(config):
    c = config
    boundary0 = np.asarray(profile.action(**c))
    largest_shared_roller_mismatch = 0
    for alpha in np.linspace(0,360,361):
        banks = []
        for phase in [0,180]:
            settings = dict(c,bank_phase_degrees=phase)
            state = profile.motion(float(alpha),**settings)
            delta = math.radians(phase/c["cavity_count"])
            rotation = np.array([[math.cos(delta),-math.sin(delta)],[math.sin(delta),math.cos(delta)]])
            ring = Polygon(boundary0 @ rotation.T)
            centers = np.asarray(state["roller_centers"])
            cam = np.asarray(state["wave_center"])
            assert np.allclose(np.linalg.norm(centers-cam,axis=1),c["pitch_radius"],atol=1e-10)
            beta = math.radians(state["output_angle"])
            for index,center in enumerate(centers):
                p = Point(center)
                assert ring.contains(p)
                clearance = ring.boundary.distance(p)-c["roller_radius"]
                assert c["profile_clearance"]-.002 < clearance < c["profile_clearance"]+.002
                theta = beta+2*math.pi*index/c["roller_count"]
                assert abs(np.dot(center,[-math.sin(theta),math.cos(theta)])) < 1e-10
            banks.append(state)
        assert np.allclose(np.asarray(banks[0]["wave_center"])+banks[1]["wave_center"],[0,0],atol=1e-10)
        assert banks[0]["output_angle"] == pytest.approx(banks[1]["output_angle"])
        mismatch = np.linalg.norm(np.asarray(banks[0]["roller_centers"])-banks[1]["roller_centers"],axis=1).max()
        largest_shared_roller_mismatch = max(largest_shared_roller_mismatch,mismatch)
    assert largest_shared_roller_mismatch == pytest.approx(2*c["eccentricity"])
    assert profile.motion(360,**c)["output_angle"] == pytest.approx(-18)
    assert profile.motion(7200,**c)["output_angle"] == pytest.approx(-360)


@pytest.mark.parametrize("length",[6,12,15,18,20,25,30])
def test_stocked_roller_lengths_and_fastener_engagement(length):
    c = working_scad.resolve(roller_length=length)
    assert c["roller_diameter"] == 7
    assert c["roller_length"] == length
    assert c["wave_height"] >= length
    assert c["wave_seat_z"] >= 1.79
    assert c["wave_cap_depth"]-c["wave_head_recess"] >= .99
    assert c["roller_z"]-c["window_z"] >= c["roller_end_clearance"]-1e-8
    assert c["roller_z"]-c["roller_window_z"] == pytest.approx(.3)
    assert c["roller_window_z"]+c["roller_window_height"]-c["roller_z"]-length == pytest.approx(.3)
    assert c["joint_z"]-c["roller_z"]-length >= c["roller_end_clearance"]-1e-8
    assert c["wave_bearing_z"]-(c["cam_z"]+1) == pytest.approx(.1)
    assert c["wave_z"]+c["wave_height"]-c["wave_cap_depth"]-(c["wave_bearing_z"]+4) == pytest.approx(.1)
    assert c["ring_join_head_seat"]-c["ring_z"] >= 3.2-1e-8
    assert c["cage_head_seat"]-c["cage_base_z"] >= 2.2-1e-8
    # All lengths are under-head shaft lengths; compare actual engaged nut thickness.
    for seat,length_key,nut_floor,nut_height in [
        (c["case_head_seat"],"case_screw_length",c["case_nut_z"],2.5),
        (c["ring_join_head_seat"],"ring_join_screw_length",c["joint_z"],2.5),
        (c["cage_head_seat"],"cage_screw_length",c["joint_z"],1.6),
        (c["bearing_z"]-c["retainer_depth"]+c["output_head_recess"],"output_screw_length",c["window_z"]-2.7,2.5),
    ]:
        tip = seat+c[length_key]
        assert tip >= nut_floor+nut_height-1e-8
        assert c[length_key] <= 35
    assert c["cage_head_seat"]+c["cage_screw_length"] < c["joint_z"]+c["central_joint_depth"]
    assert c["ring_join_head_seat"]+c["ring_join_screw_length"] < c["joint_z"]+c["central_joint_depth"]
    wave_tip = c["wave_height"]-c["wave_head_recess"]-c["wave_screw_length"]
    assert 0 < wave_tip < c["wave_nut_z"]
    for row in working_scad.bom(**c):
        if "length_mm" in row:
            assert row["length_mm"] <= 35


def test_hardware_inventory_and_common_output(config):
    from presentation.dual_instances import instance_definitions
    from collections import Counter
    pieces = working_scad.piece_definitions(**config)
    assert len(pieces) == 19
    assert sum(p["quantity"] for p in pieces) == 26
    records = instance_definitions(configuration=config)
    assert len(records) == len(set(r["name"] for r in records))
    counts = Counter(r["kind"] for r in records)
    assert counts == {"printed":26,"roller":40,"bearing":6,"shaft":1,"fastener":136}
    assert sum(r["part"]=="output_cage_joint" for r in records)==1
    assert sum(r["part"]=="wave_generator" for r in records)==2
    assert sum(r["part"]=="bearing_6810" for r in records)==2
    assert sum(r["part"]=="bearing_6704" for r in records)==4
    for primitive in working_scad.hardware_definitions(**config):
        assert primitive["kwargs"]["overhang"] is True
        assert "countersunk" not in primitive["kwargs"]["shape"]
    assert config["upper_profile_rotation"] == pytest.approx(180/21)


def test_kwargs_not_mutated_and_real_ratio():
    original = {"reduction":15,"cage_screw_count":5}
    saved = copy.deepcopy(original)
    c = working_scad.resolve(**original)
    assert original == saved
    assert profile.motion(360,**c)["output_angle"] == pytest.approx(-24)


@pytest.mark.parametrize("override",[
    {"reduction":20.5},{"reduction":0},{"eccentricity":2},
    {"cage_wall":3},{"roller_length":8},{"bearing_output":"6808"},
    {"profile_clearance":-0.1},{"overhang":False},{"profile_samples_per_cavity":10},
    {"reduction":100},{"housing_radius":50},{"cage_screw_count":0},
    {"circle_fragments":12},{"max_screw_length":40},{"central_joint_depth":4},
    {"roller_bore_diameter":8},
])
def test_invalid_edits_fail_before_export(override):
    with pytest.raises(ValueError):
        working_scad.resolve(**override)


def test_portable_scad_and_print_beds(config):
    folder = next((ROOT/"parts").iterdir())
    for name in ["parameters.scad","geometry.scad","oobb_hardware.scad","assembly.scad","collision_check.scad"]:
        contents = (folder/name).read_text()
        assert "import(" not in contents
        assert "C:/" not in contents and "C:\\" not in contents
    pieces = working_scad.piece_definitions(**config)
    expected = {(p["name"],i) for p in pieces for i in range(p["quantity"])}
    observed = []
    for bed in working_scad.pack_print_beds(pieces):
        for i,p in enumerate(bed["parts"]):
            observed.append((p["part"],p["instance"]))
            x,y = p["xy"]; w,h = p["size"]
            assert min(x-w/2,y-h/2) >= 3
            assert max(x+w/2,y+h/2) <= 217
            for q in bed["parts"][i+1:]:
                xx,yy=q["xy"]; ww,hh=q["size"]
                assert abs(x-xx)>=(w+ww)/2+3.99 or abs(y-yy)>=(h+hh)/2+3.99
    assert set(observed)==expected and len(observed)==len(expected)
