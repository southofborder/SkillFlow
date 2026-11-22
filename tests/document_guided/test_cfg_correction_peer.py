"""Independent boundary and ownership checks for CFG correction permissions."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.cfg_correction import select_cfg_correction
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.online import validate_step
from tests.document_guided.test_parallel_runner import _cfg_wire
from tests.graph.extraction.test_compiler_causal_diagnostics import loop_candidate


def errors(candidate, files=None):
    with pytest.raises(StructuralValidationError) as caught:
        validate_step("cfg_wire_v5", candidate, context={"files": files or {}})
    return caught.value.diagnostics


def repair(candidate):
    head, body = deepcopy(candidate["blocks"][1]), deepcopy(candidate["blocks"][2])
    head["instructions"][0]["inputs"][1]["identifier"] = "item_retained"
    body["instructions"].insert(1, {"opcode": "retain",
        "inputs": [{"type": "result", "identifier": "item_current"}],
        "outputs": [{"type": "result", "identifier": "item_retained"}]})
    return {"replacements": [{"record_id": "/blocks/1", "value": head},
                             {"record_id": "/blocks/2", "value": body}]}


def test_transitive_upstream_producer_is_explicit_readonly_boundary_not_implicit_edit_permission():
    candidate = _cfg_wire(loop_candidate())
    candidate["entry_block_ref"] = "prepare"
    candidate["blocks"][0]["instructions"][0]["inputs"] = [{"type": "result", "identifier": "seed"}]
    candidate["blocks"].append({"block_ref": "prepare", "instructions": [
        {"opcode": "prepare", "inputs": [{"type": "literal", "literal_value": 1}],
         "outputs": [{"type": "result", "identifier": "seed"}]},
        {"opcode": "dispatch", "inputs": [], "outputs": []}]})
    candidate["edges"].append({"source_block_ref": "prepare", "target_block_ref": "item_init"})
    rows = errors(candidate)
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "records"
    assert set(scope["records"]) == {f"/blocks/{i}" for i in (0, 1, 2, 3)}
    assert {"kind": "result_boundary", "identifier": "seed",
            "producer": "/blocks/5/instructions/0/outputs/0",
            "consumer": "/blocks/0/instructions/0/inputs/0"} in scope["evidence"]["readonly_boundary"]
    assert {"kind": "unchanged_control_edge", "path": "/edges/6",
            "source": "/blocks/5", "target": "/blocks/0"} in scope["evidence"]["readonly_boundary"]
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt("The complete original source.", candidate, rows)
    merged = strategy.merge(candidate, repair(candidate))
    assert merged["blocks"][5] == candidate["blocks"][5]
    assert validate_step("cfg_wire_v5", merged, context={"files": {}})
    illegal = repair(candidate)
    illegal["replacements"].append({"record_id": "/blocks/5", "value": candidate["blocks"][5]})
    with pytest.raises(StructuralValidationError, match="record_id"):
        strategy.merge(candidate, illegal)


def test_unselected_consumer_is_revalidated_after_all_selected_records_are_locally_fixed():
    candidate = _cfg_wire(loop_candidate())
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt("Complete source.", candidate, errors(candidate))
    corrected = repair(candidate)
    corrected["replacements"].append({"record_id": "/blocks/3", "value": deepcopy(candidate["blocks"][3])})
    # Change the selected SCC consistently, leaving only the outside return's
    # old result name invalid. Editing permission must not certify this merge.
    for replacement in corrected["replacements"]:
        for instruction in replacement["value"]["instructions"]:
            for side in ("inputs", "outputs"):
                for operand in instruction.get(side, []):
                    if operand.get("identifier") == "item_current":
                        operand["identifier"] = "item_new_current"
    merged = strategy.merge(candidate, corrected)
    assert merged["blocks"][4] == candidate["blocks"][4]
    rows = errors(merged)
    assert any(row["code"] == "RESULT_NOT_DEFINED"
               and row["path"] == "/blocks/4/instructions/0/inputs/0" for row in rows)


def test_source_copy_compiler_identity_does_not_replace_exact_original_wire_binding():
    candidate = _cfg_wire(loop_candidate())
    span = {"file": "skill/source.ts", "start_line": 1, "end_line": 1}
    candidate["blocks"][1]["instructions"][0]["metadata"]["_source_span"] = span
    files = {"skill/source.ts": "const current = merge(initial, current, updated);\n"}
    before = deepcopy(candidate)
    rows = errors(candidate, files)
    assert all(row["context"]["cfg_correction_candidate_sha256"] == canonical_sha256(candidate) for row in rows)
    cause = next(row for row in rows if row["code"] == "CFG_STRUCTURE_INVALID")["context"]["cfg_rejected_block_cascade"]
    assert cause["compiled_candidate_sha256"] != canonical_sha256(candidate)
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "records"
    assert scope["records"]["/blocks/1"]["instructions"][0]["metadata"]["_source_span"] == span
    assert "script_content" not in candidate["blocks"][1]["instructions"][0]["metadata"]
    assert candidate == before
    changed = deepcopy(candidate)
    changed["blocks"][1]["instructions"][0]["metadata"]["_source_span"]["end_line"] = 2
    assert select_cfg_correction(changed, rows)["mode"] == "whole"


def test_rejected_entry_and_unrelated_global_failure_do_not_gain_local_topology_permission():
    for entry_rejected in (False, True):
        candidate = _cfg_wire(loop_candidate())
        if entry_rejected:
            candidate["entry_block_ref"] = "item_head"
        else:
            candidate["blocks"][4]["instructions"][0]["opcode"] = "dispatch"
        rows = errors(candidate)
        assert any(row["code"] == "CFG_STRUCTURE_INVALID" for row in rows)
        scope = select_cfg_correction(candidate, rows)
        assert scope["mode"] == "whole" and scope["records"] == {}
