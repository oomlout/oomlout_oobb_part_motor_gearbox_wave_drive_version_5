"""The project entry must run the complete deterministic progression."""
from unittest.mock import patch
from types import SimpleNamespace
import working


def test_entry_populates_then_catalogues_then_draws():
    events = []
    options = [{"id":"test_one"},{"id":"test_two"}]
    parts = [{"id":"test_one","directory":"parts/test_one"}]
    modules = {
        "working_oomp_populate": SimpleNamespace(main=lambda **kw: events.append(("populate",kw)) or options),
        "working_oomp": SimpleNamespace(main=lambda **kw: events.append(("catalogue",kw)) or parts),
        "working_scad": SimpleNamespace(main=lambda **kw: events.append(("draw",kw)) or ["done"]),
    }
    with patch.dict("sys.modules",modules):
        result = working.main(scad_only=True)
    assert [name for name,_ in events] == ["populate","catalogue","draw"]
    assert events[1][1]["part_ids"] == ["test_one","test_two"]
    assert events[2][1]["parts"] == parts
    assert result == ["done"]


def test_solidcraft_is_not_a_project_dependency():
    import pytest
    with pytest.raises(ValueError,match="SCAD pipeline"):
        working.main(run_solidcraft=True)
