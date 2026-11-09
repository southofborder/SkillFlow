"""Offline flat-wire semantics and exact request pairing; no model clients."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import FlatAnnotationResponse, compile_flat_response, normalize_flat_annotation
from skillflow.propagation.annotation.binding_examples import (
    _fixture, example_material, evidence, instruction, literal, result,
)
from skillflow.propagation.contracts.specs import IRTransferSpec, operation_items
from skillflow.propagation.contracts.uses import request_pairs


def sample():
    fixture = _fixture("flat", "Explicit calls preserve response identity.",
        "Call the service with the query and return its independently acquired response.",
        [instruction("ir_call", "invoke", [literal("query")], "response"),
         instruction("ir_return", "return", [result("response")])], {})
    material = example_material(fixture)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "locations": {"service": {"kind": "tool", "name": "Service", "evidences": [evidence()]}},
        "ir_semantics": {
            "ir_call": {"evidences": [evidence()], "segments": [{"ops": [
                {"op": "call", "location": "service", "inputs": [{"kind": "input", "index": 0}],
                 "output": "reply", "demands": [{"requirement_id": "R1", "target": {"kind": "output"},
                     "preserve": "value", "reason": "Return this response."}]}]}],
                "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "reply"}}]},
            "ir_return": {"evidences": [evidence()]}}}
    return material, wire


def test_program_metadata_is_absent_from_flat_model_schema():
    schema = str(FlatAnnotationResponse.model_json_schema())
    for name in ("request_id", "task_revision_id", "operator_evidences", "empty_effect_evidences", "'status'", "'operator'"):
        assert name not in schema


def test_wire_evidence_reason_is_optional_without_inventing_source_support():
    material, wire = sample()
    for spec in wire["ir_semantics"].values():
        for citation in spec["evidences"]:
            citation.pop("reason")
    wire["locations"]["service"]["evidences"][0].pop("reason")
    saved, raw, _, _ = compile_flat_response(wire, material)
    assert "reason" not in saved["ir_semantics"]["ir_call"]["evidences"][0]
    notice = "Declaration citation; semantic support is not independently verified."
    assert raw["location_evidences"]["service"][0]["reason"] == notice
    operation = raw["ir_semantics"]["ir_call"]["events"][0]["events"][0]["atomic_ops"][0]
    assert operation["evidences"][0]["reason"] == notice


def test_flat_call_injects_metadata_derives_status_and_inherits_evidence():
    material, wire = sample()
    original = deepcopy(wire)
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    assert saved == wire == original
    assert "task_revision_id" not in saved
    assert raw["task_revision_id"] == material["task"]["task_sha256"]
    assert raw["realizations"][0]["status"] == "expressed"
    assert raw["ir_semantics"]["ir_call"]["operator"] is None
    assert raw["locations"]["service"]["access_scope"] == "recipient"
    assert raw["locations"]["service"]["retention"] is None
    assert raw["location_evidences"]["service"] == [evidence()]
    assert raw["ir_semantics"]["ir_call"]["output_bindings"][0]["evidences"] == [evidence()]
    event = raw["ir_semantics"]["ir_call"]["events"][0]
    assert [row["atomic_ops"][0]["op"] for row in event["events"]] == ["deliver", "receive"]
    assert all(row["atomic_ops"][0]["evidences"] == [evidence()] for row in event["events"])
    assert any(row["kind"] == "observation" for row in mapping["events"])
    assert mapping["goals"][0]["wire_pointer"].endswith("/segments/0/ops/0/demands/0")
    assert compiled["demands"][0]["target"]["operation_path"][-4:] == ["events", 1, "atomic_ops", 0]


def test_identical_partial_calls_are_explicitly_paired():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_call"]
    first = spec["segments"][0]["ops"][0]
    second = deepcopy(first)
    second["output"] = "reply2"
    second.pop("demands")
    spec["order"] = "partial"
    spec["segments"].append({"ops": [second]})
    _, _, compiled, _ = compile_flat_response(wire, material)
    typed = IRTransferSpec.model_validate({key: compiled["ir_semantics"]["ir_call"][key]
        for key in IRTransferSpec.model_fields})
    operations = operation_items(typed)
    pairs = request_pairs(typed)
    assert len(pairs) == 2
    assert len({operations[key].request_id for key in pairs}) == 2
    for response, request in pairs.items():
        assert operations[response].request_id == operations[request].request_id
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.solver import propagate
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    responses = [op.outputs[0] for event in solved.records.get("ir_call").events
                 for op in event.atomic_ops if op.op == "receive"]
    assert len(responses) == 2 and responses[0] != responses[1]


@pytest.mark.parametrize("slot,expected_event", [("self", 0), ("input", 0), ("output", 1)])
def test_call_demand_slot_has_exact_phase(slot, expected_event):
    material, wire = sample()
    goal = wire["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]["demands"][0]
    goal.update(target={"kind": slot, **({"index": 0} if slot == "input" else {})},
                preserve="action" if slot == "self" else "value")
    _, _, compiled, _ = compile_flat_response(wire, material)
    assert compiled["demands"][0]["target"]["operation_path"][3] == expected_event


@pytest.mark.parametrize("phase,event", [(None, 0), ("request", 0), ("response", 1)])
def test_constraint_call_phase_defaults_to_request(phase, event):
    material, wire = sample()
    target = {"instruction_id": "ir_call", "operation_path": ["segments", 0, "ops", 0], "slot": {"kind": "self"}}
    if phase is not None:
        target["phase"] = phase
    wire["realizations"][0]["constraints"] = [{"kind": "at_most", "scope": {"kind": "task"},
        "events": [target], "limit": 1, "unit": "attempt"}]
    raw = normalize_flat_annotation(wire, material)
    normalized = raw["realizations"][0]["constraints"][0]["events"][0]
    assert normalized["operation_path"] == ["events", 0, "events", event, "atomic_ops", 0]
    assert "phase" not in normalized


def test_pure_local_return_and_model_mode_operator_derivation():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_return"]
    spec["segments"] = [{"mode": "local", "returns": [{"kind": "input", "index": 0}]}]
    _, _, compiled, mapping = compile_flat_response(wire, material)
    assert any(row["instruction_id"] == "ir_return" and row["kind"] == "observation" for row in mapping["events"])
    spec["segments"] = [{"mode": "model", "ops": [{"op": "compute", "inputs": [{"kind": "input", "index": 0}],
        "dependencies": ["possible"], "output": "copy"}]}]
    raw = normalize_flat_annotation(wire, material)
    assert raw["ir_semantics"]["ir_return"]["operator"] == ["llm"]


def test_local_empty_returns_explicit_and_compute_effect_is_not_guessed():
    material, wire = sample()
    value = wire["ir_semantics"]["ir_return"]
    op = {"op": "compute", "inputs": [{"kind": "input", "index": 0}], "dependencies": ["possible"], "output": "unused"}
    value["segments"] = [{"mode": "local", "ops": [op]}]
    with pytest.raises(StructuralValidationError, match="returns"):
        normalize_flat_annotation(wire, material)
    value["segments"][0]["returns"] = []
    raw = normalize_flat_annotation(wire, material)
    assert raw["ir_semantics"]["ir_return"]["events"][0]["events"][0]["effect"] == "transform"
    op["effect"] = None
    raw = normalize_flat_annotation(wire, material)
    assert raw["ir_semantics"]["ir_return"]["events"][0]["events"][0]["effect"] is None


def test_source_only_inheritance_does_not_turn_cfg_into_sensitivity_evidence():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_call"]
    spec["evidences"] = [{"target": {"instruction_id": "ir_call", "path": []}, "reason": "The instruction is present."}]
    spec["sensitivity"] = [{"value": {"kind": "input", "index": 0}, "path": [], "property": "value", "label": "credential"}]
    with pytest.raises(StructuralValidationError, match="frozen source"):
        normalize_flat_annotation(wire, material)


def test_flat_foreach_call_yield_and_outer_result_are_compiled_without_exporting_body_local():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_call"]
    call = spec["segments"][0]["ops"][0]
    call["inputs"] = [{"kind": "local", "name": "row"}]
    spec["segments"] = [{"kind": "for_each", "collection": {"kind": "input", "index": 0},
        "item": "row", "body": [{"mode": "local", "returns": [], "ops": [call]}],
        "yield": {"kind": "local", "name": "reply"}, "output": "replies"}]
    spec["order"] = "fixed"
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "replies"}
    _, raw, compiled, mapping = compile_flat_response(wire, material)
    loop = compiled["ir_semantics"]["ir_call"]["events"][0]
    assert loop["yield"] == {"kind": "local", "name": "reply"}
    assert loop["output"] == "replies"
    assert [event["atomic_ops"][0]["op"] for event in loop["body"]] == ["deliver", "receive"]
    assert any(row["kind"] == "collection_result" for row in mapping["events"])
    assert raw["ir_semantics"]["ir_call"]["events"][0]["evidences"] == [evidence()]
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "reply"}
    with pytest.raises(StructuralValidationError, match="undefined local"):
        normalize_flat_annotation(wire, material)


def test_noncall_constraint_phase_rejected_and_failed_shape_not_silently_repaired():
    material, wire = sample()
    wire["ir_semantics"]["ir_call"]["segments"][0]["ops"][0] = {
        "op": "receive", "location": "service", "inputs": [], "output": "reply"}
    wire["realizations"][0]["constraints"] = [{"kind": "at_most", "scope": {"kind": "task"},
        "events": [{"instruction_id": "ir_call", "operation_path": ["segments", 0, "ops", 0],
                    "slot": {"kind": "self"}, "phase": "response"}], "unit": "attempt", "limit": 1}]
    with pytest.raises(StructuralValidationError, match="only on a call"):
        normalize_flat_annotation(wire, material)


def test_multiple_segments_default_to_fixed_order_and_allow_explicit_partial():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_call"]
    spec["segments"].append({"ops": [{"op": "compute", "inputs": [], "dependencies": [], "output": "unrelated"}]})
    assert normalize_flat_annotation(wire, material)["ir_semantics"]["ir_call"]["order"] == "fixed"
    spec["order"] = "partial"
    normalize_flat_annotation(wire, material)


def test_sensitivity_and_expression_inherit_real_source_evidence():
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_return"]
    spec["sensitivity"] = [{"value": {"kind": "input", "index": 0}, "path": [], "property": "value", "label": "credential"}]
    spec["segments"] = [{"ops": [{"op": "compute", "inputs": [{"kind": "input", "index": 0}],
        "dependencies": ["possible"], "output": "truth", "expression": {
            "expression": {"op": "present", "arg": {"op": "ref", "value": {"kind": "input", "index": 0}}}}}]}]
    raw = normalize_flat_annotation(wire, material)
    assert raw["ir_semantics"]["ir_return"]["sensitivity"][0]["evidences"] == [evidence()]
    assert raw["ir_semantics"]["ir_return"]["events"][0]["events"][0]["atomic_ops"][0]["expression"]["evidences"] == [evidence()]
