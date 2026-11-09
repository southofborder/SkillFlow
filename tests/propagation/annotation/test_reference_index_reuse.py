"""Program-generated coordinates keep their meaning without repeated lookups."""
from copy import deepcopy

import pytest

from skillflow.propagation.contracts import references
from tests.propagation.annotation.test_direct_references import direct_graph


def test_index_matches_external_resolution_at_every_position_and_after_reorder():
    cfg = direct_graph()
    for _ in range(2):
        entries = references.cfg_target_index(cfg)
        assert entries
        for key, entry in entries.items():
            assert key == references.target_key(entry["target"])
            assert entry == references.resolve_cfg_target(entry["target"], cfg)
        cfg["blocks"]["entry"]["instructions"].reverse()


def test_index_values_do_not_alias_cfg_or_other_index_entries():
    cfg = direct_graph()
    original = deepcopy(cfg)
    entries = references.cfg_target_index(cfg)
    entries[references.target_key({"path": []})]["value"]["blocks"].clear()
    ir_key = references.target_key({"instruction_id": "ir_read", "path": []})
    entries[ir_key]["value"]["metadata"].clear()
    leaf = {"instruction_id": "ir_read", "path": ["metadata", "0", "a/b~c", 0]}
    assert entries[references.target_key(leaf)]["value"] == "payload"
    assert cfg == original


def test_index_does_not_rescan_instructions_for_program_generated_targets(monkeypatch):
    def redundant_resolve(*args, **kwargs):
        pytest.fail("Index construction must use the positions already being walked")
    monkeypatch.setattr(references, "resolve_cfg_target", redundant_resolve)
    entries = references.cfg_target_index(direct_graph())
    assert any(entry["kind"] == "input" for entry in entries.values())
    assert any(entry["kind"] == "metadata_value" for entry in entries.values())


def test_duplicate_instruction_identity_is_still_rejected():
    cfg = direct_graph()
    cfg["blocks"]["entry"]["instructions"].append(
        deepcopy(cfg["blocks"]["entry"]["instructions"][0]))
    with pytest.raises(ValueError, match="does not exist uniquely"):
        references.cfg_target_index(cfg)
