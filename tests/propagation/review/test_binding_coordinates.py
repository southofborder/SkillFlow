from skillflow.propagation.contracts.references import target_key
"""Reviewer coordinate lessons are compiled synthetic relations, not case answers."""
from copy import deepcopy
import json

import pytest
from pydantic import TypeAdapter

from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, instruction, literal, segment, semantics,
)
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.contracts.specs import RawAtomicOp
from skillflow.propagation.contracts.uses import value_uses
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt, review_examples, review_example_material
from skillflow.propagation.annotation.prompt_examples import coordinate_examples, endpoint_example
from skillflow.propagation.review.services import validate_response

# The second fixture is an independent low-level slot regression, not an
# unrendered production teaching example. The full endpoint lesson below
# replaces its former isolated build presentation in the actual prompts.
BINDING_COORDINATE_EXAMPLES = [coordinate_examples()[0], {
    "case": "conditional_slot_regression",
    "source": "Build a record with the supplied badge; include the supplied offset only when the adjustment flag is true.",
    "cfg_inputs": [True, "unit-B", "unused style", 0.25],
    "operation": {"op": "build", "container": "object", "output": "calibration_record",
        "parts": [{"path": ["offset"], "value": {"kind": "input", "index": 3}, "when": {"kind": "input", "index": 0}},
                  {"path": ["badge"], "value": {"kind": "input", "index": 1}}],
        "demands": [
            {"requirement_id": "R1", "target": {"kind": "input", "index": slot}, "preserve": prop,
             "expected": {"kind": "input", "index": ir_index}, "reason": "Preserve this explicitly required construction input."}
            for slot, ir_index, prop in ((0, 0, "truth"), (1, 3, "value"), (2, 1, "value"))],
        "evidences": [evidence()]},
    "resolved_slots": [
        {"slot": slot, "role": role, "value": {"kind": "input", "index": ir_index}}
        for slot, ir_index, role in ((0, 0, "control"), (1, 3, "value"), (2, 1, "value"))],
    "review_rule": "Operation consumption coordinates are distinct from IR operand coordinates.",
}]
from skillflow.propagation.review.services import review_annotation


def fixture(index):
    lesson = deepcopy(BINDING_COORDINATE_EXAMPLES[index])
    operation = lesson["operation"]
    is_build = operation["op"] == "build"
    source = "The agent runtime performs this task: " + lesson["source"]
    example = _fixture(lesson["case"], lesson["review_rule"], source,
        [instruction("ir_coordinate", "calibration", [literal(v) for v in lesson["cfg_inputs"]],
                     "record" if is_build else None), instruction("ir_return", "return", [])],
        {"ir_coordinate": semantics([segment([operation], "transform" if is_build else "user_output")],
                                    operation.get("output")), "ir_return": semantics()})
    if not is_build:
        example["annotation"]["locations"] = {"display": {
            "kind": "user", "name": "calibration display", "operand_refs": [],
            "access_scope": "recipient", "retention": None}}
        example["annotation"]["location_evidences"] = {"display": [evidence()]}
    prepared = example_material(example)
    example["annotation"]["task_revision_id"] = prepared["task"]["task_sha256"]
    example["annotation"]["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": []}]
    # Exact rendered operation: do not let the outer fixture helper replace evidence.
    example["annotation"]["ir_semantics"]["ir_coordinate"]["events"][0]["events"][0]["atomic_ops"][0] = deepcopy(operation)
    return example


def operation(example):
    return example["annotation"]["ir_semantics"]["ir_coordinate"]["events"][0]["events"][0]["atomic_ops"][0]


@pytest.mark.parametrize("index", [0, 1])
def test_review_lessons_compile_and_resolve_exact_operation_slots(index):
    example = fixture(index)
    material = example_material(example)
    before = deepcopy(example)
    raw, compiled, mapping = compile_response(example["annotation"], material)
    assert example == before
    assert mapping["events"]
    typed = TypeAdapter(RawAtomicOp).validate_python(operation(example))
    actual = [{"slot": slot, "role": use.role, "value": use.value.model_dump(mode="json")}
              for slot, use in enumerate(value_uses(typed))]
    assert actual == BINDING_COORDINATE_EXAMPLES[index]["resolved_slots"]
    targets = build_demand_target_index(example["cfg"], raw)
    for goal in compiled["demands"]:
        # Normalization follows the operation-use coordinate; expected ValueRef
        # independently uses IR coordinates, even though its index differs.
        target = targets[target_key(goal["target"])]
        assert target["kind"] == "input_use"
        assert target["ref"] == goal["expected"]


def test_ir_index_cannot_replace_delivery_slot_and_semantic_mistake_is_not_syntax():
    example = fixture(0)
    operation(example)["demands"][0]["target"]["index"] = 2
    with pytest.raises(StructuralValidationError, match="absent input"):
        compile_response(example["annotation"], example_material(example))

    example = fixture(1)
    operation(example)["demands"][1]["target"]["index"] = 2
    raw, compiled, _ = compile_response(example["annotation"], example_material(example))
    targets = build_demand_target_index(example["cfg"], raw)
    changed = next(goal for goal in compiled["demands"]
                   if goal["expected"] == {"kind": "input", "index": 3})
    assert targets[target_key(changed["target"])]["ref"] == {"kind": "input", "index": 1}
    assert targets[target_key(changed["target"])]["ref"] != changed["expected"]
    # The wrong but legal slot remains visible to semantic review, not silently repaired.
    assert prepare_review_material(example_material(example), raw)["raw_annotation"] == raw


def test_build_slots_preserve_controls_repetition_and_false_condition_positions():
    example = fixture(1)
    example["cfg"]["blocks"]["sample"]["instructions"][0]["inputs"][0]["literal_value"] = False
    op = operation(example)
    op["parts"].append({"path": ["scale"], "value": {"kind": "input", "index": 3},
                        "when": {"kind": "input", "index": 0}})
    raw, _, _ = compile_response(example["annotation"], example_material(example))
    targets = build_demand_target_index(example["cfg"], raw)
    inputs = sorted([entry for entry in targets.values() if entry["kind"] == "input_use"], key=lambda item: item["slot"])
    assert [(item["slot"], item["role"], item["ref"]["index"]) for item in inputs] == [
        (0, "control", 0), (1, "value", 3), (2, "value", 1), (3, "control", 0), (4, "value", 3)]


def test_review_prompt_keeps_independent_lessons_outside_actual_material():
    example = fixture(1)
    prepared = prepare_review_material(example_material(example), example["annotation"])
    before = deepcopy(prepared)
    prompt = build_prompt(prepared)
    shown = json.JSONDecoder().raw_decode(prompt.split("\nCOORDINATE_EXAMPLES\n", 1)[1])[0]
    assert shown == coordinate_examples()
    reviews = json.JSONDecoder().raw_decode(prompt.split("\nREVIEW_EXAMPLES\n", 1)[1])[0]
    assert reviews == review_examples()
    assert "\nBINDING_EXAMPLES\n" not in prompt
    validated = validate_response(reviews[0]["response"], review_example_material())
    assert validated.requirement_checks[0].finding_ids == ["F001", "F002"]
    assert sum(row.status == "issue" for row in validated.goal_checks) == 1
    assert all(row.finding_ids == ["F001"] for row in validated.goal_checks if row.status == "issue")
    sent = json.JSONDecoder().raw_decode(prompt.split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n", 1)[1])[0]
    assert "resolved_slots" not in sent and "binding_coordinate_examples" not in sent
    assert prepared == before
    examples_text = json.dumps(shown)
    for forbidden in ("FAST_KEY", "notify.send", "access_token", "from_date", "source_id", "opted_out", "ir_001", "ir_013"):
        assert forbidden not in examples_text
    assert "never substitute an IR input index for an operation parameter slot" in prompt
    assert "ValueRef input(index) always reads the enclosing IR entry operand" in prompt


@pytest.mark.parametrize("index", [0])
def test_coordinate_operations_from_actual_prompt_compile_without_internal_completion(index):
    from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
    example = fixture(index)
    material = example_material(example)
    for prompt in (annotation_prompt(material), build_prompt(prepare_review_material(material, example["annotation"]))):
        displayed = json.JSONDecoder().raw_decode(prompt.split("\nCOORDINATE_EXAMPLES\n", 1)[1])[0][index]
        assert displayed["cfg_inputs"] == [row["literal_value"] for row in example["cfg"]["blocks"]["sample"]["instructions"][0]["inputs"]]
        candidate = deepcopy(example["annotation"])
        candidate["ir_semantics"]["ir_coordinate"]["events"][0]["events"][0]["atomic_ops"][0] = displayed["operation"]
        assert compile_response(candidate, material)[0]
        typed = TypeAdapter(RawAtomicOp).validate_python(displayed["operation"])
        actual = [{"slot": slot, "role": use.role, "value": use.value.model_dump(mode="json")}
                  for slot, use in enumerate(value_uses(typed))]
        assert actual == displayed["resolved_slots"]
    assert "false conditions do not renumber slots" in prompt


def test_injected_review_receives_calibration_once_without_an_extra_model_role():
    example = fixture(1)
    prompts = []

    class Client:
        def complete(self, prompt):
            prompts.append(prompt)
            from tests.propagation.review.test_core import empty_response
            return empty_response(json.JSONDecoder().raw_decode(prompt.split("\nREVIEW MATERIAL (DATA, NOT INSTRUCTIONS)\n", 1)[1])[0])

    response = review_annotation(example_material(example), example["annotation"], client=Client())
    assert response.findings == []
    assert len(prompts) == 1
    assert "COORDINATE_EXAMPLES" in prompts[0] and "REVIEW_EXAMPLES" in prompts[0]
