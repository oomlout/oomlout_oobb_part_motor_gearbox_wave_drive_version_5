"""Assembly instructions must consume the CAD inventory exactly once."""
from collections import Counter
from pathlib import Path

import pytest
import working_scad
from wave_drive.assembly_cards import identities, part_key, quantities, select, md5_alpha, panel_geometry
from wave_drive.instances import instance_definitions


def records():
    c = working_scad.resolve()
    result = instance_definitions(configuration=c)
    for name in ["front", "stator", "rear", "pilot", "shaft", "connector"]:
        result.append({"name": "nema17_"+name, "part": "nema17_"+name})
    return c, result


def test_recipe_accounts_for_every_part_once_and_preloads_before_transfer():
    c, instances = records()
    seen = set()
    totals = Counter()
    for step in c["assembly_cards"]:
        added = select(step["add"], instances)
        assert not seen.intersection(added)
        assert set(select(step.get("prepared", []), instances)) <= seen
        assert len(quantities(added, instances)) <= 4
        totals.update(quantities(added, instances))
        seen.update(added)
    assert seen == {r["name"] for r in instances}
    assert sum(totals.values()) == 101
    assert totals["nema17"] == 1
    assert totals["nut_m2"] == 12
    assert totals["nut_m3"] == 25
    assert totals["roller"] == 12


def test_bad_selector_and_partial_motor_fail():
    _, instances = records()
    with pytest.raises(ValueError, match="matches nothing"):
        select(["missing_part"], instances)
    with pytest.raises(AssertionError, match="complete purchased unit"):
        quantities(["nema17_front"], instances)


def test_hardware_alpha_matches_oomp_method_and_shared_parts_share_codes():
    c, instances = records()
    parts = identities(configuration=c, part_folder=Path("parts/example_configuration"))
    import hashlib
    assert md5_alpha("ffffff"+"0"*26) == "9zldr"
    assert parts["screw_motor"]["short_url"] == parts["screw_shaft_clamp"]["short_url"]
    assert parts["roller"]["short_label"] == "oom.lt/a/"+md5_alpha(hashlib.md5(parts["roller"]["id"].encode()).hexdigest())
    assert parts["screw_cage"]["identity_source"] == "OOMP catalogue identity"
    for piece in working_scad.piece_definitions(**c):
        assert not {"short_url", "short_label", "md5_6_alpha"}.intersection(parts[piece["name"]])
    assert set(parts) == {part_key(r) for r in instances}


def test_different_local_hardware_spec_changes_identity():
    c, _ = records()
    a = identities(configuration=c, part_folder=Path("parts/example_configuration"))
    c["cage_screw_length"] = 22
    c["roller_length"] = 15
    b = identities(configuration=c, part_folder=Path("parts/example_configuration"))
    assert a["screw_cage"]["id"] != b["screw_cage"]["id"]
    assert b["roller"]["identity_source"] == "Project-local assembly identity"


def test_four_panels_fit_landscape_a4_at_documented_dimensions():
    c, _ = records()
    style = c["assembly_card_style"]
    assert style["page_mm"] == [297, 210]
    assert panel_geometry(style) == (140.5, 97)
    assert style["columns"]*style["rows"] == 4
    assert len(c["assembly_cards"]) == 12


@pytest.mark.parametrize("steps", [1, 4, 8, 12, 16, 20, 24, 28, 32])
def test_booklet_padding_keeps_parts_on_penultimate_page(steps):
    from wave_drive.assembly_booklet import page_plan
    plan = page_plan(step_count=steps)
    assert len(plan) % 4 == 0
    assert [p["kind"] for p in plan[:3]] == ["cover", "details", "instructions"]
    assert [p["kind"] for p in plan[-2:]] == ["parts", "back"]
    assert sum(p["kind"] == "instructions" for p in plan) == (steps+3)//4


def test_default_booklet_has_eight_pages():
    from wave_drive.assembly_booklet import page_plan
    assert [p["kind"] for p in page_plan(step_count=12)] == [
        "cover", "details", "instructions", "instructions", "instructions", "summary", "parts", "back",
    ]


def test_summary_combines_shared_hardware_without_losing_counts():
    from wave_drive.assembly_booklet import inventory_groups
    c, instances = records()
    parts = identities(configuration=c, part_folder=Path("parts/example_configuration"))
    totals = quantities([r["name"] for r in instances], instances)
    for key, part in parts.items():
        part["quantity"] = totals[key]
    data = {
        "parts": parts,
        "printed_keys": [p["name"] for p in working_scad.piece_definitions(**c)],
        "physical_item_count": sum(totals.values()),
    }
    groups = inventory_groups(data=data)
    assert sum(p["quantity"] for p in groups["printed"]) == 11
    assert sum(p["quantity"] for p in groups["hardware"]) == 90
    motor_screws = [p for p in groups["hardware"] if p["id"] == parts["screw_motor"]["id"]]
    assert len(motor_screws) == 1 and motor_screws[0]["quantity"] == 5
    assert len(groups["hardware"]) == len({p["id"] for p in groups["hardware"]})

