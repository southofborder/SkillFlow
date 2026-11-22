"""Pure dependency selection; no semantic model, backend or historical replay."""
from copy import deepcopy
import re

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.document_guided.cfg_correction import select_cfg_correction
from skillflow.graph.extraction.compiler import compile_candidate
from tests.graph.extraction.test_compiler_causal_diagnostics import loop_candidate


def diagnostics_for(candidate):
    result = compile_candidate(candidate)
    diagnostics = []
    for row in result.diagnostics:
        path = "" if row.path == "cfg" else "/" + "/".join(re.findall(r"[^.\[\]]+", row.path))
        diagnostics.append({"code": row.code, "path": path, "message": row.message,
            "context": {**deepcopy(row.context), "cfg_correction_candidate_sha256": canonical_sha256(candidate)}})
    return diagnostics


def test_filter_head_scope_contains_real_body_carry_and_producer_boundary():
    candidate = loop_candidate()
    diagnostics = diagnostics_for(candidate)
    before = deepcopy((candidate, diagnostics))
    scope = select_cfg_correction(candidate, diagnostics)
    assert scope["mode"] == "records"
    assert set(scope["records"]) == {"/blocks/0", "/blocks/1", "/blocks/2", "/blocks/3"}
    assert scope["records"]["/blocks/2"] == candidate["blocks"][2]
    evidence = scope["evidence"]
    assert evidence["candidate_sha256"] == canonical_sha256(candidate)
    assert evidence["diagnostics_sha256"] == canonical_sha256(diagnostics)
    assert evidence["root_records"] == ["/blocks/1"]
    assert {row["kind"] for row in evidence["dependencies"]} == {
        "control_cycle", "immediate_predecessor", "result_producer", "declared_carry_predecessor"}
    assert any(row.get("consumer") == "/blocks/4/instructions/0/inputs/0" for row in evidence["readonly_boundary"])
    assert (candidate, diagnostics) == before
    scope["records"]["/blocks/2"]["block_ref"] = "changed_copy"
    assert candidate == before[0]


def test_two_independent_filters_include_both_four_operational_repair_blocks():
    first, second = loop_candidate("first"), loop_candidate("second")
    first["blocks"].extend(second["blocks"])
    first["edges"].extend(second["edges"])
    scope = select_cfg_correction(first, diagnostics_for(first))
    assert scope["mode"] == "records"
    assert {"/blocks/1", "/blocks/2", "/blocks/6", "/blocks/7"} <= scope["records"].keys()
    assert set(scope["records"]) == {f"/blocks/{bi}" for bi in (0, 1, 2, 3, 5, 6, 7, 8)}
    assert scope["evidence"]["root_records"] == ["/blocks/1", "/blocks/6"]


def test_actual_producer_outside_immediate_predecessor_is_selected():
    candidate = loop_candidate()
    items = candidate["blocks"][0]["instructions"][0]["outputs"].pop(0)
    candidate["blocks"].append({"block_ref": "actual_producer", "block_name": "Producer",
        "instructions": [{"instruction_ref": "actual_read", "opcode": "read", "outputs": [items]},
                         {"instruction_ref": "actual_jump", "opcode": "dispatch"}]})
    candidate["entry_block_ref"] = "actual_producer"
    candidate["edges"].append({"source_block_ref": "actual_producer", "target_block_ref": "item_init"})
    scope = select_cfg_correction(candidate, diagnostics_for(candidate))
    assert scope["mode"] == "records" and "/blocks/5" in scope["records"]
    assert any(row["kind"] == "result_producer" and row["record"] == "/blocks/5"
               for row in scope["evidence"]["dependencies"])
    assert not any(row["kind"] == "immediate_predecessor" and row["record"] == "/blocks/5"
                   for row in scope["evidence"]["dependencies"])


def test_519_instruction_candidate_keeps_unrelated_regions_outside_edit_scope():
    # An independent synthetic scale regression, with no historical candidate
    # or answer imported. Scope depends on relationships, not size or names.
    candidate, second = loop_candidate("first"), loop_candidate("second")
    candidate["blocks"].extend(second["blocks"])
    candidate["edges"].extend(second["edges"])
    for bi in range(227):
        count = 3 if bi < 47 else 2
        candidate["blocks"].append({"block_ref": f"unrelated_{bi}", "block_name": "Independent behavior",
            "instructions": [{"instruction_ref": f"unrelated_{bi}_{ii}",
                "opcode": "return" if ii == count - 1 else "observe", "metadata": {"text": "first_current"}}
                for ii in range(count)]})
    assert sum(len(block["instructions"]) for block in candidate["blocks"]) == 519
    scope = select_cfg_correction(candidate, diagnostics_for(candidate))
    assert scope["mode"] == "records"
    assert set(scope["records"]) == {f"/blocks/{bi}" for bi in (0, 1, 2, 3, 5, 6, 7, 8)}
    assert {"/blocks/1", "/blocks/2", "/blocks/6", "/blocks/7"} <= scope["records"].keys()


@pytest.mark.parametrize("mutation", ["candidate", "owner_index", "owner_ref", "cause_diag", "endpoint",
    "endpoint_missing", "endpoint_extra", "complete", "version", "unbound", "global"])
def test_stale_incomplete_or_unexplained_cause_uses_whole_response(mutation):
    candidate = loop_candidate()
    diagnostics = diagnostics_for(candidate)
    cause = diagnostics[-1]["context"]["cfg_rejected_block_cascade"]
    if mutation == "candidate":
        candidate["blocks"][0]["block_name"] = "changed"
    elif mutation == "owner_index":
        cause["rejected_blocks"][0]["block_index"] = 0
    elif mutation == "owner_ref":
        cause["rejected_blocks"][0]["block_ref"] = "other"
    elif mutation == "cause_diag":
        cause["rejected_blocks"][0]["diagnostic_index"] = 1
    elif mutation == "endpoint":
        cause["endpoints"][0]["edge_index"] = 2
    elif mutation == "endpoint_missing":
        cause["endpoints"].pop()
    elif mutation == "endpoint_extra":
        cause["endpoints"].append(deepcopy(cause["endpoints"][0]))
    elif mutation == "complete":
        cause["complete"] = False
    elif mutation == "version":
        cause["version"] = "unsupported"
    elif mutation == "unbound":
        diagnostics[-1]["context"].pop("cfg_correction_candidate_sha256")
    else:
        diagnostics.append({"code": "UNEXPLAINED_GLOBAL", "path": "", "message": "Unexplained defect"})
    scope = select_cfg_correction(candidate, diagnostics)
    assert scope["mode"] == "whole" and not scope["records"]
    assert scope["evidence"]["reason"]


@pytest.mark.parametrize("mutation", ["duplicate_block", "duplicate_result", "duplicate_instruction",
    "duplicate_edge", "malformed_block", "missing_producer", "missing_predecessor", "wrong_predecessor",
    "nonincoming_predecessor", "missing_endpoint", "binary_dispatch"])
def test_ambiguous_malformed_or_insufficient_dependency_scope_is_whole(mutation):
    candidate = loop_candidate()
    if mutation == "duplicate_block":
        candidate["blocks"][4]["block_ref"] = "item_init"
    elif mutation == "duplicate_result":
        candidate["blocks"][2]["instructions"][0]["outputs"][0]["identifier"] = "item_initial"
    elif mutation == "duplicate_instruction":
        candidate["blocks"][2]["instructions"][0]["instruction_ref"] = "item_merge"
    elif mutation == "duplicate_edge":
        candidate["edges"].append(deepcopy(candidate["edges"][0]))
    elif mutation == "malformed_block":
        candidate["blocks"][4]["block_ref"] = " "
    elif mutation == "missing_producer":
        candidate["blocks"][3]["instructions"][0]["inputs"].append({"type": "result", "identifier": "missing"})
    elif mutation in {"missing_predecessor", "wrong_predecessor", "nonincoming_predecessor"}:
        predecessors = candidate["blocks"][1]["instructions"][0]["metadata"]["predecessors"]
        predecessors[1] = {"missing_predecessor": "absent", "wrong_predecessor": "item_init",
                           "nonincoming_predecessor": "item_done"}[mutation]
    elif mutation == "missing_endpoint":
        candidate["edges"][2]["target_block_ref"] = "absent"
    diagnostics = [{"code": "RESULT_READ_BEFORE_DEFINITION", "path": "/blocks/1", "message": "Invalid local read"}]
    if mutation == "binary_dispatch":
        diagnostics.append({"code": "binary_dispatch", "path": "/blocks/1", "message": "Needs new blocks"})
    scope = select_cfg_correction(candidate, diagnostics)
    assert scope["mode"] == "whole" and not scope["records"]


def test_true_missing_endpoint_is_not_suppressed_by_a_rejected_block_cascade():
    candidate = loop_candidate()
    candidate["edges"][2]["target_block_ref"] = "absent"
    diagnostics = diagnostics_for(candidate)
    assert any(row["code"] == "EDGE_TARGET_NOT_FOUND" for row in diagnostics)
    assert select_cfg_correction(candidate, diagnostics)["mode"] == "whole"


@pytest.mark.parametrize("path,record", [("/blocks/2/instructions/0/opcode", "/blocks/2"),
    ("/edges/0/condition_text", "/edges/0"), ("/entry_block_ref", "/entry_block_ref")])
def test_direct_local_record_diagnostics_preserve_existing_scope_behavior(path, record):
    candidate = loop_candidate()
    scope = select_cfg_correction(candidate, [{"code": "schema", "path": path, "message": "Fix this field"}])
    assert scope["mode"] == "records" and set(scope["records"]) == {record}


def test_local_fix_can_insert_fresh_carry_instruction_and_pass_whole_validation():
    candidate = loop_candidate()
    scope = select_cfg_correction(candidate, diagnostics_for(candidate))
    assert scope["mode"] == "records"
    body = scope["records"]["/blocks/2"]
    body["instructions"].insert(1, {"instruction_ref": "item_retain", "opcode": "retain",
        "inputs": [{"type": "result", "identifier": "item_current"}],
        "outputs": [{"type": "result", "identifier": "item_retained"}]})
    scope["records"]["/blocks/1"]["instructions"][0]["inputs"][1]["identifier"] = "item_retained"
    merged = deepcopy(candidate)
    for path, block in scope["records"].items():
        merged["blocks"][int(path.rsplit("/", 1)[1])] = block
    assert compile_candidate(merged).ok
    assert merged["edges"] == candidate["edges"]
    assert merged["blocks"][4] == candidate["blocks"][4]
