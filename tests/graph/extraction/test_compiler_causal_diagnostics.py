"""Rejected-block causes remain additive to the strict compiler's failures."""
from copy import deepcopy

from skillflow.common.recording import canonical_sha256
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.graph.extraction.candidate import IRAnalysisCandidate


def loop_candidate(prefix="item"):
    def result(name):
        return {"type": "result", "identifier": f"{prefix}_{name}"}

    def instruction(name, opcode, inputs=(), outputs=(), **metadata):
        return {"instruction_ref": f"{prefix}_{name}", "opcode": opcode,
                "inputs": [result(value) for value in inputs],
                "outputs": [result(value) for value in outputs], "metadata": metadata}

    def block(name, rows):
        return {"block_ref": f"{prefix}_{name}", "block_name": name, "instructions": rows}

    blocks = [
        block("init", [instruction("read", "read_items", outputs=["items", "initial"]),
                       instruction("enter", "dispatch")]),
        block("head", [instruction("merge", "merge", ["initial", "current", "updated"], ["current"],
                                  predecessors=[f"{prefix}_{value}" for value in ("init", "body", "keep")]),
                       instruction("next", "dispatch", ["items"])]),
        block("body", [instruction("member", "member", ["items"], ["member"]),
                       instruction("filter", "dispatch", ["member"])]),
        block("keep", [instruction("append", "append", ["current", "member"], ["updated"]),
                       instruction("back", "dispatch")]),
        block("done", [instruction("return", "return", ["current"])]),
    ]
    edges = []
    for source, target, condition in [("init", "head", None), ("head", "body", "true"),
            ("head", "done", "false"), ("body", "keep", "true"),
            ("body", "head", "false"), ("keep", "head", None)]:
        edge = {"source_block_ref": f"{prefix}_{source}", "target_block_ref": f"{prefix}_{target}"}
        if condition is not None:
            edge["condition_text"] = condition
        edges.append(edge)
    return {"entry_block_ref": f"{prefix}_init", "blocks": blocks, "edges": edges}


def test_rejected_head_endpoint_cascade_has_exact_additive_ownership():
    candidate = loop_candidate()
    before = deepcopy(candidate)
    result = compile_candidate(candidate)
    assert not result.ok and result.cfg is None and candidate == before
    assert [row.code for row in result.diagnostics] == ["RESULT_READ_BEFORE_DEFINITION", "CFG_STRUCTURE_INVALID"]
    assert [row.path for row in result.diagnostics] == ["blocks[1]", "cfg"]
    local, root = result.diagnostics
    assert "is read before instruction" in local.message
    assert root.message.count("EDGE_ENDPOINT_NOT_FOUND") == 5
    cause = root.context["cfg_rejected_block_cascade"]
    assert cause["complete"] is True
    assert cause["rejected_blocks"] == [{"block_index": 1, "block_ref": "item_head",
        "canonical_block_id": "block_002", "diagnostic_index": 0,
        "original_diagnostic": local.model_dump(exclude={"context"})}]
    assert [(item["edge_index"], item["role"]) for item in cause["endpoints"]] == [
        (0, "target"), (1, "source"), (2, "source"), (4, "target"), (5, "target")]
    assert cause["compiled_candidate_sha256"] != canonical_sha256(candidate)  # parsed defaults included
    assert local.context == {}


def test_real_missing_endpoint_cannot_acquire_rejected_block_ownership():
    candidate = loop_candidate()
    candidate["edges"][2]["target_block_ref"] = "actually_absent"
    result = compile_candidate(candidate)
    assert not result.ok
    assert any(row.code == "EDGE_TARGET_NOT_FOUND" for row in result.diagnostics)
    # The remaining cascade can still carry accurate provenance. It cannot
    # claim ownership of the independent actual missing-reference diagnostic.
    for row in result.diagnostics:
        if row.code == "EDGE_TARGET_NOT_FOUND":
            assert row.context == {}
        for endpoint in row.context.get("cfg_rejected_block_cascade", {}).get("endpoints", []):
            assert endpoint["block_ref"] == "item_head"
            assert endpoint["edge_index"] != 2


def test_unrelated_structural_failure_prevents_complete_cascade_annotation():
    candidate = loop_candidate()
    candidate["blocks"][4]["instructions"][0]["opcode"] = "dispatch"
    result = compile_candidate(candidate)
    root = next(row for row in result.diagnostics if row.code == "CFG_STRUCTURE_INVALID")
    assert "EDGE_ENDPOINT_NOT_FOUND" in root.message
    assert "DISPATCH_HAS_NO_TARGET" in root.message
    assert root.context == {} and not result.ok


def test_rejected_entry_is_not_mislabeled_as_endpoint_only_cascade():
    candidate = loop_candidate()
    candidate["entry_block_ref"] = "item_head"
    root = next(row for row in compile_candidate(candidate).diagnostics if row.code == "CFG_STRUCTURE_INVALID")
    assert "ENTRY_BLOCK_NOT_FOUND" in root.message and root.context == {}


def test_constructor_field_error_is_not_mislabeled_by_the_diagnostic_projection():
    candidate = IRAnalysisCandidate.model_validate(loop_candidate())
    # Accepted model instances are an existing compiler input form. A mutated
    # field must still retain its actual constructor failure, not a plausible
    # endpoint explanation from the separately inspected graph structure.
    candidate.declared_context_keys = ["same", "same"]
    result = compile_candidate(candidate)
    root = next(row for row in result.diagnostics if row.code == "CFG_STRUCTURE_INVALID")
    assert "duplicate declared context key" in root.message
    assert root.context == {} and not result.ok


def test_repair_preserves_strict_acceptance_and_original_result_names():
    candidate = loop_candidate()
    candidate["blocks"][2]["instructions"].insert(1, {
        "instruction_ref": "item_retain", "opcode": "retain", "inputs": [{"type": "result", "identifier": "item_current"}],
        "outputs": [{"type": "result", "identifier": "item_retained"}]})
    candidate["blocks"][1]["instructions"][0]["inputs"][1]["identifier"] = "item_retained"
    result = compile_candidate(candidate)
    assert result.ok and not result.diagnostics
    assert result.cfg.blocks["block_003"].instructions[1].inputs[0].semantic_name == "item_current"
