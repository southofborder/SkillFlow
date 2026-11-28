"""Current-route contract coverage, local uncertainty and projection claims."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import split_fragments, validate_fragment
from skillflow.propagation.annotation.binding_examples import (
    _fixture, example_material, evidence, instruction, literal, result,
)
from skillflow.propagation.contracts.input_requirements import (
    InputRequirement, InputRequirementGap, ToolInputContract,
    expected_input_contract_obligations,
)
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.contracts.references import target_key


def required(index, path):
    return {"input_index": index, "required": [{"property": "value", "path": path}],
            "remainder": "independent", "reason": "The stated interface uses only this parameter."}


def source_gap():
    return {"code": "ambiguous_semantics", "reason": "The source does not state whether the y field selects a counting population.",
            "missing": "Whether y changes the selected population whose cardinality is returned.",
            "resolution": "Supply the population-selection relation for y in this count operation.",
            "evidences": [evidence()]}


def call_sample(*, empty=False):
    source = ("Call Service without arguments and return its response." if empty else
        "Call Service with query unchanged. The optional fields parameter selects exactly the returned items field. Return the response.")
    fixture = _fixture("contract_coverage", "Source-owned interface requirements.", source,
        [instruction("ir_call", "invoke", [] if empty else [literal({"query": "books", "extra": "unchanged"})], "reply"),
         instruction("ir_return", "return", [result("reply")])], {})
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "locations": {"service": {"kind": "tool", "name": "Service", "evidences": [evidence()]}},
        "ir_semantics": {"ir_call": {"evidences": [evidence()], "segments": [{"ops": [{
            "op": "call", "location": "service", "inputs": [] if empty else [{"kind": "input", "index": 0}],
            "output": "reply", "input_contract": {"inputs": [] if empty else [required(0, ["query"])],
                "reason": "The interface has no arguments." if empty else "The interface requires query; fields is optional.",
                "evidences": [evidence()]},
            "demands": [{"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value",
                         "reason": "Return the service response."}]}]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "reply"}}]},
            "ir_return": {"evidences": [evidence()]}}}
    return example_material(fixture), wire


def compute_sample():
    fixture = _fixture("contract_compute", "Exact computation coverage.", "Return x unchanged; y is not used.",
        [instruction("ir_compute", "copy", [literal({"x": 1}), literal({"y": 2})], "out"),
         instruction("ir_return", "return", [result("out")])], {})
    op = {"op": "compute", "inputs": [{"kind": "input", "index": i} for i in range(2)], "output": "out",
          "demands": [{"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value",
                       "reason": "Return x unchanged."}]}
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "ir_semantics": {"ir_compute": {"evidences": [evidence()], "segments": [{"ops": [op]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "out"}}]},
            "ir_return": {"evidences": [evidence()]}}}
    return example_material(fixture), wire


@pytest.mark.parametrize("empty", [False, True])
def test_every_tool_call_including_zero_inputs_requires_explicit_contract(empty):
    material, wire = call_sample(empty=empty)
    original = deepcopy(wire)
    _, raw, compiled, _ = compile_flat_response(wire, material)
    targets = build_demand_target_index(material["cfg"], raw)
    obligations = expected_input_contract_obligations(targets, raw["locations"], exact_expression_targets=[])
    assert len(obligations) == 2
    assert {x["input_count"] for x in obligations} == {0 if empty else 1}
    assert len({x["request_pair_id"] for x in obligations}) == 1
    assert {x["contract_id"] for x in obligations} == {x["id"] for x in compiled["input_contracts"]}
    assert wire == original
    wire["ir_semantics"]["ir_call"]["segments"][0]["ops"][0].pop("input_contract")
    for check in (lambda: compile_flat_response(wire, material),
                  lambda: validate_fragment("processing", split_fragments(wire)["processing"], material)):
        with pytest.raises(StructuralValidationError) as caught:
            check()
        rows = [x for x in caught.value.diagnostics if x["code"] == "input_contract_required"]
        assert rows and all(x["path"] == "/ir_semantics/ir_call/segments/0/ops/0/input_contract" for x in rows)


def test_exact_compute_expression_exempts_only_its_own_operation():
    material, wire = compute_sample()
    with pytest.raises(StructuralValidationError, match="requires an explicit"):
        compile_flat_response(wire, material)
    op = wire["ir_semantics"]["ir_compute"]["segments"][0]["ops"][0]
    expression = {"expression": {"op": "ref", "value": {"kind": "input", "index": 0}}, "evidences": [evidence()]}
    op["expression"] = expression
    _, raw, compiled, _ = compile_flat_response(wire, material)
    targets = build_demand_target_index(material["cfg"], raw)
    exact = [target_key(x["target"]) for x in compiled["expressions"]]
    assert not expected_input_contract_obligations(targets, raw["locations"], exact_expression_targets=exact)
    # A broader CFG key is not an operation relation, even in the same IR.
    obligations = expected_input_contract_obligations(targets, raw["locations"],
        exact_expression_targets=[target_key({"instruction_id": "ir_compute", "path": []})])
    assert len(obligations) == 1
    second = deepcopy(op)
    second.pop("expression", None)
    second.pop("demands", None)
    second["output"] = "unused"
    wire["ir_semantics"]["ir_compute"]["segments"][0]["ops"].append(second)
    with pytest.raises(StructuralValidationError) as caught:
        compile_flat_response(wire, material)
    assert any(x["code"] == "input_contract_required" and x["path"].endswith("/ops/1/demand_transfer")
               for x in caught.value.diagnostics)


def test_manual_raw_compilation_retains_optional_legacy_contract_behavior():
    from skillflow.propagation.annotation.compiler import compile_response
    material, wire = call_sample()
    _, raw, _, _ = compile_flat_response(wire, material)
    original_inputs = []
    for event in raw["ir_semantics"]["ir_call"]["events"][0]["events"]:
        op = event["atomic_ops"][0]
        original_inputs.append(deepcopy(op["inputs"]))
        op.pop("input_contract")
    _, compiled, _ = compile_response(raw, material)
    assert not compiled.get("input_contracts")
    assert original_inputs == [x["atomic_ops"][0]["inputs"] for x in raw["ir_semantics"]["ir_call"]["events"][0]["events"]]


def test_explicit_unknown_range_does_not_expand_to_independent_complement():
    value = required(0, ["x"])
    value["unresolved_ranges"] = [{"information": {"property": "value", "path": ["y"]}, "gap": source_gap()}]
    parsed = InputRequirement.model_validate(value).model_dump(mode="json")
    assert parsed == value and parsed["remainder"] == "independent"
    assert "unresolved_ranges" not in InputRequirement.model_validate(required(0, ["x"])).model_dump(mode="json")
    for path in (["x"], []):
        invalid = deepcopy(value)
        invalid["unresolved_ranges"][0]["information"]["path"] = path
        with pytest.raises(ValidationError, match="distinct|overlap"):
            InputRequirement.model_validate(invalid)
    invalid = deepcopy(value)
    invalid["unresolved_ranges"].append(deepcopy(invalid["unresolved_ranges"][0]))
    with pytest.raises(ValidationError, match="distinct"):
        InputRequirement.model_validate(invalid)


@pytest.mark.parametrize("required_path,unknown_path", [
    (["rows", 0, "x"], ["rows", {"kind": "each"}, "x"]),
    (["rows", {"kind": "each"}, "x"], ["rows", 0, "x"]),
    (["rows", 0], ["rows", {"kind": "each"}, "x"]),
    (["rows", {"kind": "each"}, "children", 1, "x"],
     ["rows", 2, "children", {"kind": "each"}, "x"]),
])
def test_each_and_concrete_index_cannot_assign_overlapping_uncertainty(required_path, unknown_path):
    value = required(0, required_path)
    value["unresolved_ranges"] = [{"information": {"property": "value", "path": unknown_path}, "gap": source_gap()}]
    with pytest.raises(ValidationError, match="overlap"):
        InputRequirement.model_validate(value)
    # A different field or information property is a distinct obligation.
    value["unresolved_ranges"][0]["information"]["property"] = "presence"
    assert InputRequirement.model_validate(value).remainder == "independent"


def test_each_and_concrete_unknown_ranges_cannot_overlap_each_other():
    value = required(0, ["x"])
    value["unresolved_ranges"] = [{"information": {"property": "value", "path": path}, "gap": source_gap()}
        for path in (["rows", {"kind": "each"}, "y"], ["rows", 2, "y"])]
    with pytest.raises(ValidationError, match="overlap"):
        InputRequirement.model_validate(value)
    value["unresolved_ranges"][1]["information"]["path"] = ["rows", 2, "z"]
    assert len(InputRequirement.model_validate(value).unresolved_ranges) == 2


@pytest.mark.parametrize("field,value", [("reason", "The computation is opaque."), ("missing", "Unknown"),
                                         ("resolution", "Review source")])
def test_gap_specificity_and_resolution_are_shared_for_local_and_remainder_gaps(field, value):
    gap = source_gap()
    gap[field] = value
    with pytest.raises(ValidationError, match="specific missing fact"):
        InputRequirementGap.model_validate(gap)
    gap = source_gap()
    gap.pop("resolution")
    with pytest.raises(ValidationError, match="resolution"):
        InputRequirementGap.model_validate(gap)


def test_optional_projection_is_paired_source_claim_without_request_rewrite():
    material, wire = call_sample()
    call = wire["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]
    capability = {"selection_input_index": 0, "selection_parameter_path": ["fields"],
        "returned_range": {"property": "value", "path": ["items"]},
        "reason": "The documented fields argument supports requesting exactly the items result range.",
        "evidences": [evidence()]}
    call["input_contract"]["acquisition_projections"] = [capability]
    original = deepcopy(wire)
    _, raw, compiled, _ = compile_flat_response(wire, material)
    assert wire == original
    assert all(x["contract"]["acquisition_projections"] == [capability] for x in compiled["input_contracts"])
    actual = [e["atomic_ops"][0] for e in raw["ir_semantics"]["ir_call"]["events"][0]["events"]]
    assert all(x["inputs"] == call["inputs"] for x in actual)
    ir = next(ir for block in material["cfg"]["blocks"].values() for ir in block["instructions"] if ir["id"] == "ir_call")
    assert "fields" not in ir["inputs"][0]["literal_value"]
    bad = deepcopy(call["input_contract"])
    bad["acquisition_projections"][0]["selection_input_index"] = 1
    with pytest.raises(ValidationError, match="actual request input"):
        ToolInputContract.model_validate(bad)
    bad = deepcopy(call["input_contract"])
    bad["acquisition_projections"][0]["returned_range"]["property"] = "presence"
    with pytest.raises(ValidationError):
        ToolInputContract.model_validate(bad)
    bad = deepcopy(call["input_contract"])
    bad["acquisition_projections"].append(deepcopy(capability))
    with pytest.raises(ValidationError, match="must not repeat"):
        ToolInputContract.model_validate(bad)


def test_loop_calls_keep_exact_scope_and_missing_contract_points_to_body():
    from tests.document_guided.test_annotation_wire import sample
    material, wire = sample()
    spec = wire["ir_semantics"]["ir_call"]
    call = spec["segments"][0]["ops"][0]
    call["inputs"] = [{"kind": "local", "name": "row"}]
    spec["segments"] = [{"kind": "for_each", "collection": {"kind": "input", "index": 0},
        "item": "row", "body": [{"mode": "local", "returns": [], "ops": [call]}],
        "yield": {"kind": "local", "name": "reply"}, "output": "replies"}]
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "replies"}
    _, raw, _, _ = compile_flat_response(wire, material)
    targets = build_demand_target_index(material["cfg"], raw)
    obligations = expected_input_contract_obligations(targets, raw["locations"], exact_expression_targets=[])
    assert len(obligations) == 2 and all(x["scope_path"] == ["events", 0] for x in obligations)
    assert len({x["request_pair_id"] for x in obligations}) == 1
    call.pop("input_contract")
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", split_fragments(wire)["processing"], material)
    assert all(x["path"].endswith("/segments/0/body/0/ops/0/input_contract") for x in caught.value.diagnostics
               if x["code"] == "input_contract_required")


def test_obligation_inventory_does_not_infer_tool_interface_from_equal_operands_or_storage():
    material, wire = call_sample()
    spec = wire["ir_semantics"]["ir_call"]
    call = deepcopy(spec["segments"][0]["ops"][0])
    call["output"] = "second_reply"
    call.pop("demands")
    spec["segments"].append({"ops": [call]})
    _, raw, _, _ = compile_flat_response(wire, material)
    targets = build_demand_target_index(material["cfg"], raw)
    obligations = expected_input_contract_obligations(targets, raw["locations"], exact_expression_targets=[])
    assert len(obligations) == 4 and len({x["request_pair_id"] for x in obligations}) == 2
    storage = deepcopy(raw["locations"])
    storage["service"]["kind"] = "storage"
    assert not expected_input_contract_obligations(targets, storage, exact_expression_targets=[])


def test_projection_cannot_be_attached_to_an_unpaired_delivery():
    from skillflow.propagation.contracts.input_requirements import normalize_input_contracts
    from skillflow.propagation.contracts.task import task_source_files
    material, wire = call_sample()
    _, raw, _, _ = compile_flat_response(wire, material)
    targets = build_demand_target_index(material["cfg"], raw)
    target = deepcopy(next(x for x in targets.values() if x.get("kind") == "operation" and x["value"]["op"] == "deliver"))
    target["value"]["input_contract"]["acquisition_projections"] = [{
        "selection_input_index": 0, "selection_parameter_path": ["fields"],
        "returned_range": {"property": "value", "path": ["items"]},
        "reason": "The source documents selection of items via fields.", "evidences": [evidence()]}]
    with pytest.raises(StructuralValidationError, match="exact paired response"):
        normalize_input_contracts({"request": target}, task_source_files(material["source"]), raw["locations"])


def test_public_supplement_does_not_introduce_a_new_operation_target_syntax():
    material, wire = compute_sample()
    wire["expressions"] = [{"target": {"instruction_id": "ir_compute", "operation_path": ["segments", 0, "ops", 0],
        "slot": {"kind": "self"}}, "expression": {"op": "ref", "value": {"kind": "input", "index": 0}},
        "evidences": [evidence()]}]
    with pytest.raises(StructuralValidationError) as caught:
        compile_flat_response(wire, material)
    assert any(x["path"].startswith("/expressions/0/target") for x in caught.value.diagnostics)


def test_compiled_local_gap_preserves_actual_whole_input_and_observation():
    from skillflow.propagation.contracts.specs import IRSemantics, operation_items
    fixture = _fixture("local_input_gap", "Local uncertainty retains only its named information.",
        "Calculate the score from x. y may select the counting population, but its relation is unspecified. z does not affect the score.",
        [instruction("ir_compute", "calculate", [literal({"x": 1, "y": 2, "z": "extra"})], "score"),
         instruction("ir_return", "return", [result("score")])], {})
    row = required(0, ["x"])
    row["unresolved_ranges"] = [{"information": {"property": "value", "path": ["y"]}, "gap": source_gap()}]
    transfer = {"rules": [{"output": {"property": "value", "path": []}, "inputs": [row],
        "reason": "The score uses x; only y's selection relation remains unknown, while z is independent.", "evidences": [evidence()]}]}
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}], "ir_semantics": {
        "ir_compute": {"evidences": [evidence()], "segments": [{"mode": "model", "ops": [{
            "op": "compute", "inputs": [{"kind": "input", "index": 0}], "output": "score", "demand_transfer": transfer,
            "demands": [{"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value",
                         "reason": "Return the calculated score."}]}]}],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "score"}}]},
        "ir_return": {"evidences": [evidence()]}}}
    original = deepcopy(wire)
    _, _, compiled, _ = compile_flat_response(wire, example_material(fixture))
    assert wire == original and compiled["input_contracts"][0]["contract"] == transfer
    ops = list(operation_items(IRSemantics.model_validate(compiled["ir_semantics"]["ir_compute"])).values())
    actual = next(op for op in ops if op.op == "compute")
    assert [x.model_dump(mode="json") for x in actual.inputs] == [{"kind": "input", "index": 0}]
    assert actual.dependencies == ["possible"]
    assert any(op.op == "deliver" and [x.model_dump(mode="json") for x in op.inputs] == [{"kind": "input", "index": 0}] for op in ops)
