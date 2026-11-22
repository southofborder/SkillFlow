"""Semantic requirement contracts preserve real inputs and owner isolation."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import assemble_fragments, split_fragments, validate_fragment
from skillflow.propagation.annotation.binding_examples import (
    _fixture, example_material, evidence, instruction, literal, result,
)
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.input_requirements import (
    DemandTransfer, InputRequirement, InputInformationRequirement, CompiledInputContract,
)
from skillflow.propagation.contracts.specs import operation_items, IRTransferSpec


def row(index, *paths):
    return {"input_index": index,
            "required": [{"property": "value", "path": list(path)} for path in paths],
            "remainder": "independent", "reason": "The stated calculation uses only the listed field values."}


def transfer():
    return {"rules": [{"output": {"property": "value", "path": []},
        "inputs": [row(0, ["a"]), row(1, ["b"]), row(2)],
        "reason": "The result is the sum of a.a and b.b; c is not used by this calculation.",
        "evidences": [evidence()]}]}


def compute_sample():
    source = "Return y = a.a + b.b. Inputs a, b and c are supplied; no other fields affect y."
    fixture = _fixture("input_requirements", "Extra inputs remain actual inputs.", source,
        [instruction("ir_calc", "calculate", [literal({"a": 3, "secret": "A"}),
             literal({"b": 4}), literal({"c": "extra"})], "y"),
         instruction("ir_return", "return", [result("y")])], {})
    material = example_material(fixture)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "ir_semantics": {"ir_calc": {"evidences": [evidence()], "segments": [{"mode": "model", "ops": [
            {"op": "compute", "inputs": [{"kind": "input", "index": i} for i in range(3)],
             "output": "y", "demand_transfer": transfer(),
             "demands": [{"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value",
                          "reason": "Return the required sum."}]}]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "y"}}]},
            "ir_return": {"evidences": [evidence()]}}}
    return material, wire


def test_compute_contract_compiles_without_erasing_extra_input_or_observation():
    material, wire = compute_sample()
    original = deepcopy(wire)
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    assert wire == saved == original
    contracts = compiled["input_contracts"]
    assert len(contracts) == 1
    contract = contracts[0]
    assert contract["kind"] == "compute" and contract["contract"] == transfer()
    assert contract["raw_path"] == ["events", 0, "events", 0, "atomic_ops", 0]
    assert contract["raw_pointer"].endswith("/atomic_ops/0/demand_transfer")
    assert mapping["input_contracts"][0]["wire_pointer"].endswith("/segments/0/ops/0/demand_transfer")
    operations = operation_items(IRTransferSpec.model_validate({key: compiled["ir_semantics"]["ir_calc"][key]
        for key in IRTransferSpec.model_fields}))
    compute = next(op for op in operations.values() if op.op == "compute")
    assert len(compute.inputs) == 3 and compute.dependencies == ["possible"] * 3
    assert "demand_transfer" not in compute.model_dump(mode="json")
    observed = [op for op in operations.values() if op.op == "deliver"]
    assert observed and sum(len(op.inputs) for op in observed) == 3
    assert to_payload(compiled)["input_contracts"] == contracts
    assert compile_flat_response(saved, material) == (saved, raw, compiled, mapping)


def test_processing_contract_is_source_only_and_survives_fragment_assembly():
    material, wire = compute_sample()
    fragments = split_fragments(wire)
    processing = fragments["processing"]
    assert validate_fragment("processing", processing, {k: v for k, v in material.items() if k != "task"}) == processing
    _, _, compiled, _ = assemble_fragments(processing, fragments["task-correspondence"],
                                           fragments["sensitivity"], material)
    assert len(compiled["input_contracts"]) == 1
    bad = deepcopy(fragments["task-correspondence"])
    bad["input_contracts"] = compiled["input_contracts"]
    with pytest.raises(StructuralValidationError):
        validate_fragment("task-correspondence", bad, material, processing)


@pytest.mark.parametrize("change", ["missing_input", "repeated_input", "unknown_input", "expression", "bad_source"])
def test_invalid_compute_contract_is_rejected_at_its_original_location(change):
    material, wire = compute_sample()
    op = wire["ir_semantics"]["ir_calc"]["segments"][0]["ops"][0]
    rule = op["demand_transfer"]["rules"][0]
    if change == "missing_input":
        rule["inputs"].pop()
    elif change == "repeated_input":
        rule["inputs"].append(deepcopy(rule["inputs"][0]))
    elif change == "unknown_input":
        rule["inputs"][2]["input_index"] = 9
    elif change == "expression":
        op["expression"] = {"expression": {"op": "ref", "value": {"kind": "input", "index": 0}},
                            "evidences": [evidence()]}
    else:
        rule["evidences"][0]["end_line"] = 500
    with pytest.raises((StructuralValidationError, ValidationError, ValueError)):
        compile_flat_response(wire, material)


def test_unresolved_remainder_requires_a_specific_source_backed_gap():
    unknown = row(0)
    unknown["remainder"] = "unresolved"
    with pytest.raises(ValidationError):
        InputRequirement.model_validate(unknown)
    unknown["gap"] = {"code": "missing_interface", "reason": "opaque computation", "missing": "unknown",
                      "resolution": "Provide the renderer implementation or its options-field dependency specification.",
                      "evidences": [evidence()]}
    with pytest.raises(ValidationError, match="specific missing fact"):
        InputRequirement.model_validate(unknown)
    unknown["gap"].update(reason="The computation is opaque.", missing="The fields accessed from options.")
    with pytest.raises(ValidationError, match="specific missing fact"):
        InputRequirement.model_validate(unknown)
    unknown["gap"].update(reason="The renderer options are supplied by an unavailable imported implementation.",
                          missing="The fields the renderer reads from its options parameter.")
    assert InputRequirement.model_validate(unknown).gap.code == "missing_interface"
    unknown["remainder"] = "independent"
    with pytest.raises(ValidationError):
        InputRequirement.model_validate(unknown)


def test_output_selectors_are_exact_distinct_and_support_nested_members():
    contract = transfer()
    contract["rules"][0]["output"]["path"] = ["rows", {"kind": "each"}, "score"]
    parsed = DemandTransfer.model_validate(contract).model_dump(mode="json")
    assert parsed["rules"][0]["output"]["path"] == ["rows", {"kind": "each"}, "score"]
    contract["rules"].append(deepcopy(contract["rules"][0]))
    with pytest.raises(ValidationError, match="selectors must be distinct"):
        DemandTransfer.model_validate(contract)


def test_closed_output_decomposition_requires_an_explicit_complete_part_inventory():
    contract = transfer()
    contract["rules"][0]["output"]["path"] = ["total"]
    assert "output_parts" not in DemandTransfer.model_validate(contract).model_dump(mode="json")
    contract["output_parts"] = [{"property": "value", "path": ["total"]}]
    assert DemandTransfer.model_validate(contract).output_parts[0].path == ["total"]
    for parts in ([], [{"property": "value", "path": ["missing"]}],
                  [{"property": "value", "path": ["total"]}] * 2):
        with pytest.raises(ValidationError, match="Closed output parts"):
            DemandTransfer.model_validate({**contract, "output_parts": parts})
    whole = transfer()
    whole["output_parts"] = [{"property": "value", "path": []}]
    with pytest.raises(ValidationError, match="recursive whole-output"):
        DemandTransfer.model_validate(whole)


def test_optional_input_selector_defaults_and_output_scope_are_strict():
    selector = {"property": "value", "path": ["limit"]}
    assert InputInformationRequirement.model_validate(selector).model_dump(mode="json") == selector
    assert InputInformationRequirement.model_validate({**selector, "if_present": False}).model_dump(mode="json") == selector
    assert InputInformationRequirement.model_validate({**selector, "if_present": True}).model_dump(mode="json") == {
        **selector, "if_present": True}
    duplicate = row(0, ["limit"])
    duplicate["required"].append({**selector, "if_present": True})
    with pytest.raises(ValidationError, match="must not repeat"):
        InputRequirement.model_validate(duplicate)
    contract = transfer()
    contract["rules"][0]["output"]["if_present"] = True
    with pytest.raises(ValidationError, match="Extra inputs"):
        DemandTransfer.model_validate(contract)
    contract = transfer()
    contract["rules"][0]["output"]["path"] = ["total"]
    contract["output_parts"] = [{"property": "value", "path": ["total"], "if_present": True}]
    with pytest.raises(ValidationError, match="Extra inputs"):
        DemandTransfer.model_validate(contract)


@pytest.mark.parametrize("optional_limit", [None, 7])
def test_tool_interface_fields_copy_to_request_response_and_keep_extra_payload(optional_limit):
    fixture = _fixture("tool_input_fields", "Use the interface requirement, not the whole actual parameter.",
        "Call Service with the required query field and return the response. Its optional limit field must retain its value when supplied; absence is valid. Audit metadata is not required by its interface.",
        [instruction("ir_call", "invoke", [literal({"query": "books", "audit": "extra",
             **({"limit": optional_limit} if optional_limit is not None else {})})], "response"),
         instruction("ir_return", "return", [result("response")])], {})
    material = example_material(fixture)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "locations": {"service": {"kind": "tool", "name": "Service", "evidences": [evidence()]}},
        "ir_semantics": {"ir_call": {"evidences": [evidence()], "segments": [{"ops": [
            {"op": "call", "location": "service", "inputs": [{"kind": "input", "index": 0}],
             "output": "reply", "demands": [{"requirement_id": "R1", "target": {"kind": "output"},
                 "preserve": "value", "reason": "Return the tool response."}]}]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "reply"}}]},
            "ir_return": {"evidences": [evidence()]}}}
    call = wire["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]
    call["input_contract"] = {"inputs": [row(0, ["query"])],
        "reason": "The tool interface requires query and, when supplied, limit; audit metadata is not a parameter requirement.",
        "evidences": [evidence()]}
    call["input_contract"]["inputs"][0]["required"].append({
        "property": "value", "path": ["limit"], "if_present": True})
    _, raw, compiled, mapping = compile_flat_response(wire, material)
    contracts = compiled["input_contracts"]
    assert len(contracts) == 2 and {c["kind"] for c in contracts} == {"tool"}
    assert len({c["id"] for c in contracts}) == 2
    assert all(c["contract"] == call["input_contract"] for c in contracts)
    assert len({c["wire_pointer"] for c in mapping["input_contracts"]}) == 1
    request, response = [event["atomic_ops"][0] for event in raw["ir_semantics"]["ir_call"]["events"][0]["events"]]
    assert request["input_contract"] == response["input_contract"]
    assert request["input_contract"]["inputs"][0]["required"][1]["if_present"] is True
    assert "if_present" not in request["input_contract"]["inputs"][0]["required"][0]
    assert request["inputs"] == response["inputs"] == call["inputs"]
    assert compile_flat_response(wire, material)[2]["input_contracts"] == contracts
    mismatched = deepcopy(raw)
    mismatched["ir_semantics"]["ir_call"]["events"][0]["events"][1]["atomic_ops"][0]["input_contract"]["inputs"][0]["required"][1]["if_present"] = False
    from skillflow.propagation.annotation.services import compile_response
    with pytest.raises(StructuralValidationError, match="paired request and response"):
        compile_response(mismatched, material)
    altered = deepcopy(contracts[0])
    altered["contract"]["inputs"][0]["required"][0]["path"] = ["secret"]
    with pytest.raises(ValidationError, match="identity differs"):
        CompiledInputContract.model_validate(altered)
    response["input_contract"]["inputs"][0]["required"][0]["path"] = ["audit"]
    from skillflow.propagation.annotation.services import compile_response
    with pytest.raises(StructuralValidationError, match="paired request and response"):
        compile_response(raw, material)
