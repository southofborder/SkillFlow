"""Current-candidate mixed-gate diagnostics under one unchanged correction."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import canonical_sha256, injected_factory, read_json
from skillflow.common.structural_correction import ResponseChain, chain_counts
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.cfg_correction import select_cfg_correction
from skillflow.document_guided.cfg_wire import normalize_cfg_wire, prepare_cfg_wire
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.online import analysis_config, validate_step
from tests.common.test_structural_correction import Script
from tests.document_guided.test_parallel_runner import _cfg_wire
from tests.graph.extraction.test_compiler_causal_diagnostics import loop_candidate


SOURCE = "Read complete input.\nKeep or skip each member and retain the accumulator.\nRun the action before guarded completion.\n"
FILES = {"skill/source.txt": SOURCE}


def mixed_candidate():
    first, second = loop_candidate("first"), loop_candidate("second")
    first["blocks"].extend(second["blocks"])
    first["edges"].extend(second["edges"])
    wire = _cfg_wire(first)
    wire["blocks"].extend([
        {"block_ref": "guarded_action", "instructions": [
            {"opcode": "act", "outputs": [{"type": "result", "identifier": "completed_action"}]},
            {"opcode": "dispatch"}]},
        {"block_ref": "guarded_done", "instructions": [{"opcode": "return"}]}])
    wire["edges"].append({"source_block_ref": "guarded_action", "target_block_ref": "guarded_done",
                          "condition_text": "normal completion"})
    for bi in (0, 5):
        wire["blocks"][bi]["instructions"][0]["metadata"]["_source_span"] = {
            "file": "skill/source.txt", "start_line": 1, "end_line": 3}
    return wire


def errors(candidate, files=None):
    with pytest.raises(StructuralValidationError) as caught:
        validate_step("cfg_wire_v5", candidate, context={"files": FILES if files is None else files})
    return caught.value.diagnostics


def corrected_records(candidate):
    replacements = []
    for prefix, head_index, body_index in (("first", 1, 2), ("second", 6, 7)):
        head, body = (deepcopy(candidate["blocks"][bi]) for bi in (head_index, body_index))
        head["instructions"][0]["inputs"][1]["identifier"] = prefix + "_retained"
        body["instructions"].insert(1, {"opcode": "retain",
            "inputs": [{"type": "result", "identifier": prefix + "_current"}],
            "outputs": [{"type": "result", "identifier": prefix + "_retained"}]})
        replacements.extend([{"record_id": f"/blocks/{head_index}", "value": head},
                             {"record_id": f"/blocks/{body_index}", "value": body}])
    dispatch = deepcopy(candidate["blocks"][10])
    dispatch["instructions"][-1]["inputs"] = [{"type": "result", "identifier": "completed_action"}]
    replacements.append({"record_id": "/blocks/10", "value": dispatch})
    return {"replacements": replacements}


def test_online_path_collects_dispatch_two_self_reads_and_ten_cascades_without_acceptance():
    candidate = mixed_candidate()
    before = deepcopy(candidate)
    prepared, preflight = prepare_cfg_wire(candidate)
    assert [row["code"] for row in preflight] == ["dispatch_inputs"]
    assert prepared["blocks"][10]["instructions"][-1].get("inputs", []) == []
    with pytest.raises(StructuralValidationError):
        normalize_cfg_wire(candidate)
    rows = errors(candidate)
    assert [row["code"] for row in rows] == ["dispatch_inputs", "RESULT_READ_BEFORE_DEFINITION",
                                               "RESULT_READ_BEFORE_DEFINITION", "CFG_STRUCTURE_INVALID"]
    assert rows[-1]["message"].count("EDGE_ENDPOINT_NOT_FOUND") == 10
    assert rows[-1]["message"].count("DISPATCH_INPUTS_MISSING") == 1
    cause = rows[-1]["context"]["cfg_rejected_block_cascade"]
    assert cause["version"] == "skillflow-cfg-rejected-block-cascade-v2"
    assert cause["structure_issue_count"] == 11
    assert [owner["diagnostic_index"] for owner in cause["rejected_blocks"]] == [1, 2]
    assert [owner["original_diagnostic"]["code"] for owner in cause["rejected_blocks"]] == [
        "RESULT_READ_BEFORE_DEFINITION", "RESULT_READ_BEFORE_DEFINITION"]
    assert len(cause["endpoints"]) == 10 and cause["dispatches"][0]["block_index"] == 10
    assert all(row["context"]["cfg_correction_candidate_sha256"] == canonical_sha256(candidate) for row in rows)
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "records"
    assert set(scope["records"]) == {f"/blocks/{bi}" for bi in (0, 1, 2, 3, 5, 6, 7, 8, 10)}
    assert scope["evidence"]["root_records"] == ["/blocks/1", "/blocks/10", "/blocks/6"]
    assert candidate == before


def test_one_recorded_correction_receives_all_errors_complete_source_and_actual_dependency_scope(tmp_path):
    candidate = mixed_candidate()
    original = deepcopy(candidate)
    client = Script([candidate, corrected_records(candidate)])
    base = "COMPLETE SOURCE\n" + SOURCE + "END SOURCE\n"
    chain = ResponseChain(tmp_path, prefix="calls/graph", base_prompt=base, request_kind="base",
        config=analysis_config(), writer=ArtifactWriter(()),
        validate=lambda value: validate_step("cfg_wire_v5", value, context={"files": FILES}),
        client_factory=injected_factory(client), max_corrections=1,
        correction_strategy=fragment_correction_strategy("cfg"))
    accepted = chain.run()
    assert len(client.prompts) == 2 and chain.accepted_call == "calls/graph/a002"
    assert chain_counts(tmp_path, "calls/graph")["structural_corrections"] == 1
    prompt = client.prompts[1]
    assert prompt.startswith(base) and prompt.count(SOURCE) == 1
    context = json.loads(prompt.rsplit("\n", 1)[1])
    assert context["candidate"] == candidate
    assert len(context["diagnostics"]) == 4
    assert context["correction_scope"]["scope_policy"] == "affected_control_components_with_producer_and_predecessor_boundary"
    assert set(context["allowed_record_ids"]) == {f"/blocks/{bi}" for bi in (0, 1, 2, 3, 5, 6, 7, 8, 10)}
    merged = read_json(tmp_path / "calls/graph/a002/merged-candidate.json")
    assert [bi for bi, (a, b) in enumerate(zip(candidate["blocks"], merged["blocks"])) if a != b] == [1, 2, 6, 7, 10]
    assert merged["edges"] == candidate["edges"] and merged["entry_block_ref"] == candidate["entry_block_ref"]
    assert accepted["blocks"][0]["instructions"][0]["metadata"]["script_content"] == SOURCE
    assert read_json(tmp_path / "calls/graph/a001/response.json") == original and candidate == original
    assert read_json(tmp_path / "calls/graph/a001/validation.json")["status"] == "structural_invalid"
    assert read_json(tmp_path / "calls/graph/a002/validation.json")["status"] == "valid"


@pytest.mark.parametrize("barrier", ["wire_schema", "canonical_schema", "source_copy"])
def test_schema_and_source_barriers_retain_preflight_and_never_compile(monkeypatch, barrier):
    candidate = mixed_candidate()
    if barrier == "wire_schema":
        candidate["blocks"][0]["instructions"][0]["unknown_field"] = True
    elif barrier == "canonical_schema":
        candidate["blocks"][0]["block_name"] = ""
    else:
        candidate["blocks"][0]["instructions"][0]["metadata"]["_source_span"]["end_line"] = 100
    def forbidden(*args, **kwargs):
        raise AssertionError("Compilation must not pass the explicit unsafe-input barrier")
    monkeypatch.setattr("skillflow.graph.extraction.compiler.compile_candidate", forbidden)
    rows = errors(candidate)
    assert rows[0]["code"] == "dispatch_inputs" and len(rows) >= 2
    assert any(row.get("context", {}).get("cfg_validation_barrier") == barrier for row in rows)
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "records"
    assert set(scope["records"]) == {"/blocks/0", "/blocks/10"}
    assert scope["evidence"]["scope_policy"] == "direct_records"
    assert not scope["evidence"]["dependencies"]


@pytest.mark.parametrize("change", ["count", "dispatch_removed", "dispatch_duplicate", "dispatch_index", "instruction",
                                    "edges", "owner_offset", "version", "missing_preflight", "stale_binding",
                                    "root_message", "root_code", "root_binding"])
def test_mixed_root_without_complete_current_ownership_stays_whole(change):
    candidate = mixed_candidate()
    rows = errors(candidate)
    cause = rows[-1]["context"]["cfg_rejected_block_cascade"]
    if change == "count":
        cause["structure_issue_count"] -= 1
    elif change == "dispatch_removed":
        cause["dispatches"] = []
    elif change == "dispatch_duplicate":
        cause["dispatches"].append(deepcopy(cause["dispatches"][0]))
        cause["structure_issue_count"] += 1
    elif change == "dispatch_index":
        cause["dispatches"][0]["block_index"] = 9
    elif change == "instruction":
        cause["dispatches"][0]["canonical_instruction_id"] = "ir_001"
    elif change == "edges":
        cause["dispatches"][0]["edge_indices"] = []
    elif change == "owner_offset":
        cause["rejected_blocks"][0]["diagnostic_index"] = 0
    elif change == "version":
        cause["version"] = "skillflow-cfg-rejected-block-cascade-v1"
    elif change == "missing_preflight":
        rows[0]["code"] = "unknown_local"
    elif change == "root_message":
        rows[-1]["message"] += "; UNEXPLAINED_GLOBAL: unrelated root defect"
    elif change == "root_code":
        rows[-1]["code"] = "UNEXPLAINED_GLOBAL"
    elif change == "root_binding":
        cause.pop("root_diagnostic_sha256")
    else:
        rows[0]["context"]["cfg_correction_candidate_sha256"] = "0" * 64
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "whole" and not scope["records"]


def test_pure_endpoint_proof_also_binds_original_root_in_new_producer():
    candidate = _cfg_wire(loop_candidate())
    rows = errors(candidate)
    assert rows[-1]["context"]["cfg_rejected_block_cascade"]["version"] == "skillflow-cfg-rejected-block-cascade-v1"
    assert select_cfg_correction(candidate, rows)["mode"] == "records"
    rows[-1]["message"] += "; UNEXPLAINED_GLOBAL: unrelated root defect"
    assert select_cfg_correction(candidate, rows)["mode"] == "whole"


@pytest.mark.parametrize("change", ["unknown_global", "ambiguous_identity", "binary", "missing_endpoint", "unrelated_root"])
def test_other_global_topology_or_identity_defects_keep_all_errors_and_whole_fallback(change):
    candidate = mixed_candidate()
    if change == "ambiguous_identity":
        candidate["blocks"][11]["block_ref"] = "first_init"
    elif change == "binary":
        candidate["edges"].extend({"source_block_ref": "guarded_action", "target_block_ref": ref}
                                  for ref in ("first_init", "second_init"))
    elif change == "missing_endpoint":
        candidate["edges"][-1]["target_block_ref"] = "absent"
    elif change == "unrelated_root":
        candidate["blocks"][11]["instructions"][0]["opcode"] = "dispatch"
    rows = errors(candidate)
    assert rows[0]["code"] in {"binary_dispatch", "dispatch_inputs"}
    assert sum(row["code"] == "RESULT_READ_BEFORE_DEFINITION" for row in rows) == 2
    if change == "unknown_global":
        rows.append({"code": "UNKNOWN_GLOBAL", "path": "", "message": "Independent global issue"})
    assert select_cfg_correction(candidate, rows)["mode"] == "whole"


def test_fixing_only_heads_cannot_bypass_undefined_carry_or_whole_merged_validation():
    candidate = mixed_candidate()
    strategy = fragment_correction_strategy("cfg")
    strategy.build_prompt(SOURCE, candidate, errors(candidate))
    correction = corrected_records(candidate)
    correction["replacements"] = [row for row in correction["replacements"] if row["record_id"] not in {"/blocks/2", "/blocks/7"}]
    merged = strategy.merge(candidate, correction)
    rows = errors(merged)
    undefined = {row["path"] for row in rows if row["code"] == "RESULT_NOT_DEFINED"}
    assert {f"/blocks/{bi}/instructions/0/inputs/1" for bi in (1, 6)} <= undefined


def test_unknown_compiler_failure_is_not_reclassified_or_used_for_correction(monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("Unexpected compiler failure")
    monkeypatch.setattr("skillflow.graph.extraction.compiler.compile_candidate", broken)
    with pytest.raises(RuntimeError, match="Unexpected compiler failure"):
        validate_step("cfg_wire_v5", mixed_candidate(), context={"files": FILES})


def test_compiler_success_never_overrides_independent_application_rejection():
    candidate = {"entry_block_ref": "choose", "blocks": [
        {"block_ref": "choose", "instructions": [{"opcode": "dispatch", "inputs": [
            {"type": "literal", "literal_value": True}]}]},
        *({"block_ref": name, "instructions": [{"opcode": "return"}]} for name in ("a", "b", "c"))],
        "edges": [{"source_block_ref": "choose", "target_block_ref": name} for name in ("a", "b", "c")]}
    from skillflow.graph.extraction.compiler import compile_candidate
    prepared, preflight = prepare_cfg_wire(candidate)
    assert compile_candidate(prepared).ok
    assert [row["code"] for row in preflight] == ["binary_dispatch"]
    assert [row["code"] for row in errors(candidate)] == ["binary_dispatch"]


def test_two_preflight_records_rebase_every_original_owner_and_preserve_pure_dispatch_scope():
    candidate = mixed_candidate()
    candidate["blocks"].extend([
        {"block_ref": "other_guard", "instructions": [{"opcode": "dispatch"}]},
        {"block_ref": "other_done", "instructions": [{"opcode": "return"}]}])
    candidate["edges"].append({"source_block_ref": "other_guard", "target_block_ref": "other_done",
                               "condition_text": "the condition"})
    rows = errors(candidate)
    cause = rows[-1]["context"]["cfg_rejected_block_cascade"]
    assert [row["code"] for row in rows[:2]] == ["dispatch_inputs", "dispatch_inputs"]
    assert [owner["diagnostic_index"] for owner in cause["rejected_blocks"]] == [2, 3]
    assert cause["structure_issue_count"] == 12 and len(cause["dispatches"]) == 2
    assert select_cfg_correction(candidate, rows)["mode"] == "records"
    incomplete = deepcopy(rows)
    proof = incomplete[-1]["context"]["cfg_rejected_block_cascade"]
    proof["dispatches"].pop()
    proof["structure_issue_count"] -= 1
    assert select_cfg_correction(candidate, incomplete)["mode"] == "whole"
    pure = {"entry_block_ref": "other_guard", "blocks": candidate["blocks"][-2:], "edges": candidate["edges"][-1:]}
    pure_rows = errors(pure)
    pure_cause = pure_rows[-1]["context"]["cfg_rejected_block_cascade"]
    assert pure_cause["endpoints"] == [] and pure_cause["rejected_blocks"] == []
    assert set(select_cfg_correction(pure, pure_rows)["records"]) == {"/blocks/0"}


def test_all_original_preflight_errors_survive_a_later_schema_barrier():
    candidate = mixed_candidate()
    candidate["edges"].extend({"source_block_ref": "guarded_action", "target_block_ref": ref}
                              for ref in ("first_init", "second_init"))
    candidate["blocks"][0]["data_source_kind"] = "external"
    candidate["blocks"][0]["instructions"][0]["unknown"] = True
    rows = errors(candidate)
    assert {"external_acquisition_inputs", "binary_dispatch", "dispatch_inputs"} <= {row["code"] for row in rows}
    assert all(row["context"]["cfg_validation_barrier"] == "wire_schema" for row in rows)
    assert not any(row["code"] == "RESULT_READ_BEFORE_DEFINITION" for row in rows)


@pytest.mark.parametrize("barrier", ["candidate_schema", "wire_schema", "canonical_schema", "source_copy"])
def test_known_barrier_never_authorizes_compiler_dependency_or_global_cause(barrier):
    candidate = mixed_candidate()
    rows = errors(candidate)
    rows[0]["context"]["cfg_validation_barrier"] = barrier
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "whole" and not scope["records"]
    # A precisely located read-before-definition still invokes dependency
    # inference, even if the aggregate root is absent from this partial set.
    assert select_cfg_correction(candidate, rows[:-1])["mode"] == "whole"


@pytest.mark.parametrize("barrier", ["unknown", "", [], {"kind": "schema"}])
def test_unknown_or_malformed_barrier_does_not_gain_direct_edit_permission(barrier):
    candidate = mixed_candidate()
    rows = [{"code": "schema", "path": "/blocks/0/instructions/0/inputs", "message": "Invalid field",
             "context": {"cfg_validation_barrier": barrier,
                         "cfg_correction_candidate_sha256": canonical_sha256(candidate)}}]
    assert select_cfg_correction(candidate, rows)["mode"] == "whole"


def test_exact_local_source_copy_error_can_replace_its_block_without_any_compiler_pass(monkeypatch):
    from tests.document_guided.test_typed_record_correction import cfg_candidate
    candidate = cfg_candidate()
    candidate["blocks"][0]["instructions"][0]["metadata"] = {"_source_span": {
        "file": "skill/source.txt", "start_line": 1, "end_line": 100}}
    def forbidden(*args, **kwargs):
        raise AssertionError("A source-copy barrier must still prevent compiler inspection")
    monkeypatch.setattr("skillflow.graph.extraction.compiler.compile_candidate", forbidden)
    rows = errors(candidate)
    assert [row["code"] for row in rows] == ["source_copy"]
    scope = select_cfg_correction(candidate, rows)
    assert scope["mode"] == "records" and set(scope["records"]) == {"/blocks/0"}
    assert scope["evidence"]["scope_policy"] == "direct_records"
