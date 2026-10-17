from copy import deepcopy
import json

import pytest

from skillflow.propagation.annotation.binding_examples import example_material
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.prompt_examples import compact_prompt_examples, prompt_examples, endpoint_example, endpoint_example_context
from skillflow.propagation.annotation.prompts import build_prompt
from pydantic import TypeAdapter, ValidationError
from skillflow.propagation.contracts.specs import RawAtomicOp
from skillflow.propagation.contracts.demand import OperationExpression


@pytest.mark.parametrize("index", range(3))
def test_independent_cases_and_semantic_contrasts_are_structurally_valid(index):
    fixture = prompt_examples()[index]
    before = deepcopy(fixture)
    material = example_material(fixture)
    for field in ("annotation", "contrast"):
        raw, compiled, mapping = compile_response(fixture[field], material)
        assert raw["task_revision_id"] == material["task"]["task_sha256"]
        assert compiled["demands"] and mapping["events"]
    assert fixture == before


def test_prompt_fragments_are_compact_and_do_not_include_pilot_answers():
    examples = compact_prompt_examples()
    text = json.dumps(examples, ensure_ascii=False, separators=(",", ":"))
    assert len(text) < 8500  # Complete evidence/goal objects replace invalid stripped fragments.
    for excluded in ("FAST_KEY", "notify.send", "access_token", "from_date", "source_id", "opted_out", "ir_001", "ir_013"):
        assert excluded not in text
    for example in examples:
        assert not {"cfg", "annotation", "contrast", "task_candidate"} & example.keys()
    repeated = examples[1]["fragments"]
    first = repeated["first_ir"]["events"][0]["events"][0]["atomic_ops"][0]
    assert first["inputs"][0]["index"] == 2
    assert first["demands"][1]["target"]["index"] == 0
    assert examples[2]["fragments"]["realization"]["status"] == "expressed"
    assert examples[2]["fragments"]["realization"]["gaps"] == []
    assert "Open encoding alone adds no gap" in examples[2]["fragments"]["avoid"]


def test_exact_rendered_fragments_compile_in_declared_outer_context_without_internal_repairs():
    fixture = prompt_examples()[0]
    prompt = build_prompt(example_material(fixture))
    rendered = json.JSONDecoder().raw_decode(prompt.split("\nBINDING_EXAMPLES\n", 1)[1])[0]
    for shown, full in zip(rendered, prompt_examples(), strict=True):
        assert shown["source"] == full["source"]
        context = shown["context"]
        assert (context["file"], context["line"], context["requirement_id"]) == ("skill/SKILL.md", 1, "R1")
        instructions = {row["id"]: row for row in full["cfg"]["blocks"]["sample"]["instructions"]}
        assert all(inputs == instructions[ir]["inputs"] for ir, inputs in context["ir_inputs"].items())
        candidate = deepcopy(full["annotation"])
        for name, path in context["placements"].items():
            parent = candidate if path[0] == "realizations" else candidate["ir_semantics"]
            for step in path[:-1]:
                parent = parent[step]
            # Only the explicitly declared outer context comes from the fixture.
            # No reason, evidence or any other field is added to the shown object.
            assert parent[path[-1]] == shown["fragments"][name]
            parent[path[-1]] = deepcopy(shown["fragments"][name])
        assert compile_response(candidate, example_material(full))[0]


def test_displayed_required_fields_cannot_be_removed_and_null_effect_hierarchy_is_complete():
    shown = compact_prompt_examples()
    operation = shown[0]["fragments"]["filter"]
    TypeAdapter(RawAtomicOp).validate_python(operation)
    expression = shown[0]["fragments"]["count_expression"]
    OperationExpression.model_validate(expression)
    for value, field, validator in (
        (operation, "evidences", TypeAdapter(RawAtomicOp).validate_python),
        (expression, "evidences", OperationExpression.model_validate),
    ):
        broken = deepcopy(value)
        del broken[field]
        with pytest.raises(ValidationError):
            validator(broken)
    assert operation["demands"][0]["reason"]
    ir = shown[1]["fragments"]["first_ir"]
    event = ir["events"][0]["events"][0]
    assert event["effect"] is None and not event.get("evidences")
    assert ir["empty_effect_evidences"] and ir["events"][0]["evidences"]
    assert all(op["evidences"] for op in event["atomic_ops"])


def test_full_endpoint_example_and_contrast_preserve_distinct_scopes_without_mutation():
    fixture = endpoint_example()
    before = deepcopy(fixture)
    context = endpoint_example_context()
    material = example_material(fixture)
    assert context == {key: material[key] for key in ("source", "cfg", "task")}
    for field in ("annotation", "contrast"):
        raw, compiled, mapping = compile_response(fixture[field], material)
        assert raw["task_revision_id"] == context["task"]["task_sha256"]
        assert mapping["events"] and compiled["demands"]
    assert fixture == before

    def operation(candidate, name):
        node = candidate
        for part in fixture["positions"][name]:
            node = node[part]
        return node

    positive, negative = fixture["annotation"], fixture["contrast"]
    assert "demands" not in operation(positive, "read")
    assert "demands" not in operation(positive, "build")
    receiver = operation(positive, "deliver")
    contents = [row for row in receiver["demands"] if row["preserve"] == "value"]
    assert {tuple(row["path"]) for row in contents} == {("badge",), ("offset",)}
    assert all(row["target"] == {"kind": "input", "index": 0} for row in contents)
    by_path = {tuple(row["path"]): row for row in contents}
    assert by_path[("badge",)]["expected"] == {"kind": "input", "index": 0}
    assert by_path[("badge",)]["expected_path"] == ["badge"]
    assert not {"expected", "expected_path"} & by_path[("offset",)].keys()
    assert operation(positive, "build")["parts"][1]["when"] == {"kind": "local", "name": "adjustment"}
    assert operation(negative, "read")["demands"][0]["preserve"] == "value"
    assert {d["preserve"] for d in operation(negative, "deliver")["demands"]} == {"action", "shape"}
    # The contrast changes demand claims only; it does not narrow acquisition,
    # repair delivery, erase sensitivity, or rewrite the task to pass a check.
    def without_demands(value):
        if isinstance(value, dict):
            return {k: without_demands(v) for k, v in value.items() if k != "demands"}
        return [without_demands(v) for v in value] if isinstance(value, list) else value
    assert without_demands(positive) == without_demands(negative)


def test_actual_prompt_contains_endpoint_slot_map_and_complete_receiver_fields():
    fixture = endpoint_example()
    prompt = build_prompt(example_material(fixture))
    shown = json.JSONDecoder().raw_decode(prompt.split("\nENDPOINT_COORDINATES_AND_CONTRAST\n", 1)[1])[0]
    assert shown == fixture["show"]
    assert [row["role"] for row in shown["build_slots"]] == ["value", "control", "value"]
    assert shown["delivery_slot"] == {"slot": 0, "value": {"kind": "local", "name": "calibration_record"}}
    assert "whole read is not by itself a whole-value demand seed" in prompt
    assert "action plus shape cannot substitute for required parameter content" in prompt
    assert "independent source demand does not inherit build.when" in prompt
