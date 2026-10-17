"""Executable independent lessons, target capabilities and mechanical boundaries."""
from copy import deepcopy
import json

import pytest
from pydantic import ValidationError

from skillflow.common.validation import StructuralValidationError
from skillflow.common.structural_correction import correct_response
from skillflow.propagation.annotation.binding_examples import binding_examples, example_material, prompt_binding_examples
from skillflow.propagation.annotation.compiler import compile_response, InternalCompilationError
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.prompt_examples import compact_prompt_examples
from skillflow.propagation.contracts.demand import goal_target_capability
from skillflow.propagation.contracts.task import validate_task_candidate
from skillflow.propagation.contracts.joint import joint_source_files


def target(material, pointer):
    from skillflow.propagation.contracts.task import build_task_target_index
    return next(item["target"] for item in build_task_target_index(material["cfg"]).values() if item["pointer"] == pointer)


@pytest.mark.parametrize("index", range(7))
def test_seven_independent_lessons_compile_with_their_own_source_and_cfg(index):
    fixture = binding_examples()[index]
    before = deepcopy(fixture)
    material = example_material(fixture)
    checked, compiled, mapping = compile_response(fixture["annotation"], material)
    assert fixture == before
    assert material["task"]["requirements"][0]["text"] == fixture["source"]
    assert compiled["task_ref"]["task_sha256"] == material["task"]["task_sha256"]
    assert mapping["events"]
    assert set(checked["ir_semantics"]) == set(fixture["annotation"]["ir_semantics"])


def test_lessons_stay_separate_from_actual_prompt_and_have_no_evaluated_case_names():
    fixture = binding_examples()[0]
    material = example_material(fixture)
    prompt = build_prompt(material)
    shown = json.JSONDecoder().raw_decode(prompt.split("\nBINDING_EXAMPLES\n", 1)[1].split("\nFORMAT_EXAMPLE\n", 1)[0])[0]
    assert shown == compact_prompt_examples() and len(shown) == 3
    text = json.dumps(shown, ensure_ascii=False)
    for excluded in ("FAST_KEY", "notify.send", "access_token", "from_date", "source_id", "opted_out", "ir_001", "ir_013"):
        assert excluded not in text
    assert all("cfg" not in row and "annotation" not in row for row in shown)
    assert "operation slots differ from IR operand indexes" in shown[1]["rule"]



@pytest.mark.parametrize("pointer,property", [
    ("/blocks/sample/instructions/0/outputs/0/identifier", "value"),
    ("/blocks/sample/instructions/0", "cardinality"),
    ("/blocks/sample", "action"),
])
def test_existing_but_unexecutable_goal_target_is_rejected_before_doe(pointer, property):
    fixture = binding_examples()[0]
    material = example_material(fixture)
    fixture["annotation"]["demands"][0].update(target=target(material, pointer), preserve=property)
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], material)
    assert caught.value.diagnostics[0]["code"] == "demand_target_capability"
    assert caught.value.diagnostics[0]["path"] == "/demands/0/target"


def test_task_correspondence_can_still_bind_general_graph_positions_and_no_goal_is_not_fabricated():
    fixture = binding_examples()[0]
    material = example_material(fixture)
    realization = fixture["annotation"]["realizations"][0]
    realization.update(status="retained_only", bindings=[{"target": target(material, "/blocks/sample"), "reason": "整块实现此要求。"}],
                       gaps=[{"reason": "此测试只登记对应关系。", "evidences": material["task"]["requirements"][0]["evidences"]}])
    fixture["annotation"]["demands"] = []
    assert compile_response(fixture["annotation"], material)[1]["demands"] == []


def test_all_independent_goal_capability_errors_are_reported_together():
    fixture = binding_examples()[0]
    material = example_material(fixture)
    first = fixture["annotation"]["demands"][0]
    fixture["annotation"]["demands"] = [
        {**first, "target": target(material, "/blocks/sample/instructions/0/id")},
        {**first, "target": target(material, "/blocks/sample/instructions/0/outputs/0/identifier")},
    ]
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], material)
    assert [row["path"] for row in caught.value.diagnostics] == ["/demands/0/target", "/demands/1/target"]


def test_expression_wrapper_and_control_scope_have_distinct_structural_failures():
    fixture = binding_examples()[2]
    op = fixture["annotation"]["ir_semantics"]["ir_sample_count"]["events"][0]["events"][0]["atomic_ops"][0]
    op["expression"] = op["expression"]["expression"]
    with pytest.raises((ValidationError, StructuralValidationError)):
        compile_response(fixture["annotation"], example_material(fixture))

    fixture = binding_examples()[3]
    fixture["annotation"]["expressions"][0]["expression"] = {"op": "ref", "value": {"kind": "local", "name": "is_warm"}}
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], example_material(fixture))
    row = caught.value.diagnostics[0]
    assert row["code"] == "local_scope" and row["path"] == "/expressions/0/expression"
    assert row["context"]["available_locals"] == []


def test_attached_expression_error_uses_raw_candidate_path():
    fixture = binding_examples()[2]
    op = fixture["annotation"]["ir_semantics"]["ir_sample_count"]["events"][0]["events"][0]["atomic_ops"][0]
    op["expression"]["expression"]["arg"]["value"] = {"kind": "local", "name": "not_defined"}
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], example_material(fixture))
    assert caught.value.diagnostics[0]["path"] == "/ir_semantics/ir_sample_count/events/0/events/0/atomic_ops/0/expression/expression"


def test_capability_does_not_interpret_task_or_source_prose():
    assert goal_target_capability({"kind": "graph"}, "prohibit") is None
    assert goal_target_capability({"kind": "instruction", "instruction_id": "ir_x"}, "action") == "ir_action"
    assert goal_target_capability({"kind": "instruction", "instruction_id": "ir_x"}, "value") is None
    assert goal_target_capability({"kind": "input", "instruction_id": "ir_x"}, "value") == "ir_input"


def test_literal_substitution_schema_error_is_mechanical_and_located():
    fixture = binding_examples()[2]
    fixture["cfg"]["blocks"]["sample"]["instructions"][0]["inputs"][0]["literal_value"] = "not a collection"
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(fixture["annotation"], example_material(fixture))
    assert caught.value.diagnostics[0]["code"] == "schema"
    assert caught.value.diagnostics[0]["path"].startswith("/ir_semantics/ir_sample_count/events/0/events/0/atomic_ops/0/expression/expression")


def test_duplicate_control_expression_is_mechanical_not_an_indexing_crash():
    fixture = binding_examples()[3]
    fixture["annotation"]["expressions"] *= 2
    with pytest.raises(StructuralValidationError, match="multiple expression supplements"):
        compile_response(fixture["annotation"], example_material(fixture))


def test_generated_sink_invariant_failure_stops_without_structural_correction(monkeypatch):
    fixture = binding_examples()[0]
    material = example_material(fixture)
    prompts = []
    monkeypatch.setattr("skillflow.propagation.annotation.compiler.derive_sink_boundaries", lambda *_: [])

    def complete(prompt):
        prompts.append(prompt)
        assert len(prompts) == 1, "An implementation fault must not request model correction"
        return deepcopy(fixture["annotation"])

    with pytest.raises(InternalCompilationError, match="sink boundaries") as caught:
        correct_response("frozen prompt", complete=complete,
                         validate=lambda raw: compile_response(raw, material))
    assert len(prompts) == 1
    assert isinstance(caught.value.__cause__, StructuralValidationError)


def test_explicit_candidate_compilation_precondition_remains_correctable():
    fixture = binding_examples()[0]
    material = example_material(fixture)
    broken = deepcopy(fixture["annotation"])
    broken["ir_semantics"]["ir_sample_pick"]["events"][0]["mode"] = "model"
    with pytest.raises(StructuralValidationError) as caught:
        compile_response(broken, material)
    assert caught.value.diagnostics[0]["code"] == "model_operator"
    responses = iter([broken, fixture["annotation"]])
    attempts = []
    result = correct_response("frozen prompt", complete=lambda _: next(responses),
        validate=lambda raw: compile_response(raw, material),
        on_attempt=lambda number, *_: attempts.append(number))
    assert attempts == [1, 2]
    assert result[1]["sink_boundaries"]


def test_candidate_request_ambiguity_is_rejected_before_generated_invariant_boundary():
    fixture = binding_examples()[4]
    raw = fixture["annotation"]
    raw["locations"]["display"]["kind"] = "tool"
    spec = raw["ir_semantics"]["ir_sample_display"]
    spec["empty_effect_evidences"] = deepcopy(spec["operator_evidences"])
    for evidence in spec["empty_effect_evidences"]:
        evidence.pop("value")
    event = spec["events"][0]["events"][0]
    event["effect"] = None
    event.pop("evidences")
    delivery = event["atomic_ops"][0]
    event["atomic_ops"] = [delivery, deepcopy(delivery), {
        "op": "receive", "location": "display", "inputs": deepcopy(delivery["inputs"]),
        "output": "response", "evidences": deepcopy(delivery["evidences"])}]
    with pytest.raises(StructuralValidationError, match="ambiguous"):
        compile_response(raw, example_material(fixture))
