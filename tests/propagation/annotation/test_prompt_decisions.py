from skillflow.common.prompt_format import render_prompt_format
from skillflow.propagation.contracts.profiles import RawAnnotationResponse, FailureResponse
from tests.propagation.annotation.helpers import effects_of
"""Executable authored examples; these tests do not predict model decisions."""

from copy import deepcopy
import json
import re

import pytest

from tests.propagation.annotation.helpers import source_bundle
from skillflow.propagation.annotation.compiler import compile_response
from tests.propagation.annotation.helpers import prepare_material
from skillflow.propagation.material import model_material, compact_schema, prepare_material as prepare_frozen_material
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.contracts.profiles import FailureResponse
from pydantic import TypeAdapter
from skillflow.propagation.annotation.prompts import INSTRUCTIONS
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.prompts import response_format_example, format_example_context


def example_material(source=None):
    """Independent test fixture, not a repaired version of the shown response."""
    text = source or "The agent runtime returns the original excerpt field internally."
    ev = [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
           "reason": "This independent test source states the relationship under test."}]
    cfg = {"entry_block_id": "entry", "constraints": [], "edges": [], "declared_context_keys": [],
        "blocks": {"entry": {"block_id": "entry", "block_name": "Example", "constraints": [], "data_source_kind": None,
            "instructions": [
                {"id": "ir_example_select", "opcode": "select_excerpt", "constraints": [], "metadata": {},
                 "inputs": [{"type": "literal", "literal_value": {"excerpt": "Original text"}}],
                 "outputs": [{"type": "result", "identifier": "selected"}]},
                {"id": "ir_example_return", "opcode": "return", "constraints": [], "metadata": {},
                 "inputs": [{"type": "result", "identifier": "selected"}], "outputs": []}]}}}
    material = prepare_material(source_bundle(text), cfg)
    base = {"operator": ["agent_runtime"], "operator_evidences": [{**ev[0], "value": "agent_runtime"}],
            "order": "fixed", "events": [], "output_bindings": [], "sensitivity": []}
    selected = deepcopy(base)
    selected["events"] = [{"kind": "processing", "mode": "default", "returns": [], "evidences": ev,
        "events": [{"effect": "transform", "evidences": ev, "atomic_ops": [
            {"op": "select_part", "input": {"kind": "input", "index": 0}, "path": ["excerpt"],
             "output": "excerpt", "evidences": ev, "demands": [{"requirement_id": "R001",
                 "target": {"kind": "output"}, "preserve": "value", "expected": {"kind": "input", "index": 0},
                 "expected_path": ["excerpt"], "reason": "Preserve the original field for the internal return."}]}]}]}]
    selected["output_bindings"] = [{"output_index": 0, "value": {"kind": "local", "name": "excerpt"}, "evidences": ev}]
    returned = {**deepcopy(base), "empty_effect_evidences": ev}
    raw = {"outcome": "completed", "task_revision_id": material["task"]["task_sha256"],
           "realizations": [{"requirement_id": "R001", "status": "expressed", "bindings": [], "gaps": []}],
           "demands": [], "expressions": [], "locations": {}, "location_evidences": {},
           "ir_semantics": {"ir_example_select": selected, "ir_example_return": returned}}
    return material, raw


def test_complete_format_example_is_typed_and_executable_with_its_own_evidence():
    actual_input, _ = example_material("An independent caller requests a different result.")
    prompt = build_prompt(actual_input)
    decoder = json.JSONDecoder()
    context = decoder.raw_decode(prompt.split("\nFORMAT_EXAMPLE_CONTEXT\n", 1)[1])[0]
    raw = decoder.raw_decode(prompt.split("\nFORMAT_EXAMPLE\n", 1)[1])[0]
    before = deepcopy(raw)
    material = prepare_frozen_material(context["source"], context["cfg"], task_baseline=context["task"])
    assert set(context) == {"source", "cfg", "task"}
    assert context["source"] != actual_input["source"]
    assert len(context["source"]["files"][0]["content"].splitlines()) == 1
    assert "Boolean adjustment" in context["source"]["files"][0]["content"]
    assert raw["task_revision_id"] == context["task"]["task_sha256"]
    assert "the_exact_supplied_task_sha256" not in prompt
    serialized = json.dumps(raw, ensure_ascii=False)
    assert RawAnnotationResponse.model_validate_json(serialized)
    assert set(raw) == {"ir_semantics", "locations", "ir_semantics", "outcome", "location_evidences", "task_revision_id", "realizations", "demands", "expressions"}
    checked, compiled, _ = compile_response(raw, material)
    assert raw == before
    assert checked == RawAnnotationResponse.model_validate(raw).model_dump(mode="json")
    assert effects_of(compiled["ir_semantics"]["ir_packet_read"]) == ["context_read", "model_observe"]
    assert effects_of(compiled["ir_semantics"]["ir_packet_send"]) == ["model_observe", "transform"]
    assert compiled["ir_semantics"]["ir_packet_return"]["events"] == []
    assert compiled["ir_semantics"]["ir_packet_return"]["output_bindings"] == []
    assert compiled["ir_semantics"]["ir_packet_return"]["operator"] == ["agent_runtime"]
    assert compiled["ir_semantics"]["ir_packet_return"]["empty_effect_evidences"]
    assert raw["ir_semantics"]["ir_packet_read"]["output_bindings"][0]["output_index"] == 0
    assert checked["ir_semantics"]["ir_packet_read"]["sensitivity"][0]["path"] == ["badge"]
    assert {tuple(d["path"]) for d in compiled["demands"] if d["preserve"] == "value"} == {("badge",), ("offset",)}
    assert not raw["demands"]
    assert "demands" not in raw["ir_semantics"]["ir_packet_read"]["events"][0]["events"][0]["atomic_ops"][0]
    assert checked["realizations"][0]["bindings"][0]["target"] == {"instruction_id": "ir_packet_send", "path": []}


def test_format_example_is_separate_from_schema_and_complete_original_input():
    material, _ = example_material()
    before = deepcopy(material)
    prompt = build_prompt(material)
    context = json.JSONDecoder().raw_decode(prompt.split("\nFORMAT_EXAMPLE_CONTEXT\n")[1])[0]
    example = json.JSONDecoder().raw_decode(prompt.split("\nFORMAT_EXAMPLE\n")[1])[0]
    assert context == format_example_context()
    assert example["task_revision_id"] == context["task"]["task_sha256"]
    schema = TypeAdapter(RawAnnotationResponse | FailureResponse).json_schema()
    assert render_prompt_format(schema) in prompt and "RESPONSE_JSON_SCHEMA" not in prompt
    payload = json.JSONDecoder().raw_decode(prompt.split("\nINPUT_JSON\n")[1])[0]
    assert example == response_format_example()
    assert schema == TypeAdapter(RawAnnotationResponse | FailureResponse).json_schema()
    assert payload == model_material(before) and before == material
    assert "not facts about this Skill or expected DOE answers" in INSTRUCTIONS
    assert not re.search(r"[\u3400-\u9fff]", INSTRUCTIONS)
    assert "failure reasons in English" in INSTRUCTIONS


def test_target_effect_and_expression_guidance_is_explicit_without_new_business_fields():
    from skillflow.propagation.review.prompts import INSTRUCTIONS as REVIEW_INSTRUCTIONS
    for prompt in (INSTRUCTIONS, REVIEW_INSTRUCTIONS):
        assert '"instruction_id":"ir_demo","path":[]' in prompt
        assert '"block_id":"block_demo","path":[]' in prompt
        assert "Non-action self" in prompt and "not its attached expression" in prompt
        assert "neither self/truth nor output/truth" in prompt
        assert "it does not execute select_part" in prompt
        assert "or encode a Boolean when" in prompt
        assert "Open encoding alone creates no gap" in prompt
    assert "even when atomic operations exist" in INSTRUCTIONS
    assert "accepted requires finding_indexes: []" in REVIEW_INSTRUCTIONS
    assert "Do not invent or infer a pointer for a missing demand" in REVIEW_INSTRUCTIONS


@pytest.mark.parametrize("operation", ["filter_items", "compute"])
@pytest.mark.parametrize("mode", ["default", "local"])
def test_authored_filter_count_pairs_keep_input_or_return_observation_versions(operation, mode):
    task = "Keep enabled records unchanged." if operation == "filter_items" else "Count the records."
    boundary = (" Run this operation in an isolated local worker; only its result is returned to the agent, "
                "without returning the input records.") if mode == "local" else ""
    source = task + boundary
    material, raw = example_material(source)
    segment = raw["ir_semantics"]["ir_example_select"]["events"][0]
    segment["mode"] = mode
    segment["returns"] = [{"kind": "local", "name": "processed"}] if mode == "local" else []
    evidence = segment["evidences"]
    operation_spec = {"op": operation, "output": "processed", "evidences": evidence}
    if operation == "filter_items":
        operation_spec.update(input={"kind": "input", "index": 0}, predicate="enabled records")
    else:
        operation_spec.update(inputs=[{"kind": "input", "index": 0}], dependencies=["derived"])
    segment["events"][0]["atomic_ops"] = [operation_spec]
    raw["demands"] = [{"requirement_id": "R001", "target": {"instruction_id": "ir_example_return", "side": "input", "index": 0}, "preserve": "value", "reason": "保持此人工案例的返回值。"}]
    raw["ir_semantics"]["ir_example_select"]["output_bindings"][0]["value"]["name"] = "processed"
    _, compiled, _ = compile_response(raw, material)
    profile = compiled["ir_semantics"]["ir_example_select"]
    expected = ["transform", "model_observe"] if mode == "local" else ["model_observe", "transform"]
    assert effects_of(profile) == expected
    observation_index = expected.index("model_observe")
    observed = compiled["ir_semantics"]["ir_example_select"]["events"][observation_index]["atomic_ops"][0]["inputs"]
    assert observed == ([{"kind": "local", "name": "processed"}] if mode == "local"
                        else [{"kind": "input", "index": 0}])


def test_same_ir_classification_and_unchanged_field_have_separate_relations():
    text = "The agent runtime classifies the response and returns its payload field unchanged."
    material, raw = example_material(text)
    cfg = deepcopy(material["cfg"])
    cfg["blocks"]["entry"]["instructions"][0]["outputs"].append({"type": "result", "identifier": "classification"})
    material = prepare_material(source_bundle(text), cfg)
    spec = raw["ir_semantics"]["ir_example_select"]
    atom = spec["events"][0]["events"][0]["atomic_ops"][0]
    atom.update(path=["payload"], output="payload")
    spec["output_bindings"][0]["value"]["name"] = "payload"
    spec["events"][0]["events"][0]["atomic_ops"].append({
        "op": "compute", "inputs": [{"kind": "input", "index": 0}],
        "dependencies": ["derived"], "output": "classification", "evidences": atom["evidences"],
    })
    spec["output_bindings"].append({"output_index": 1, "value": {"kind": "local", "name": "classification"},
                                    "evidences": atom["evidences"]})
    compiled = compile_response(raw, material)[1]
    atoms = compiled["ir_semantics"]["ir_example_select"]["events"][1]["atomic_ops"]
    assert [(a["op"], a["output"]) for a in atoms] == [("select_part", "payload"), ("compute", "classification")]
    assert effects_of(compiled["ir_semantics"]["ir_example_select"]) == ["model_observe", "transform"]


def test_prompt_replaces_implementation_guessing_and_opaque_field_fallback():
    decision = INSTRUCTIONS.split("PROCESSING DECISION ORDER", 1)[1].split("EXPLICIT VALUE RELATIONS", 1)[0]
    assert decision.index("Identify the actual content") < decision.index("mode=model") < decision.index("mode=local") < decision.index("mode=default")
    for boundary in (
        "Could be implemented locally does not mean local isolation is specified",
        "opcode, executor labels, a predicate and absence of an LLM mention",
        "[] requires supported no-content return",
        "Do not weaken an explicit field-original relation into opaque compute",
        "Choose each output relation independently",
        "unchanged selected members -> filter_items",
        "classification/count/summary -> compute",
    ):
        assert boundary in INSTRUCTIONS


def test_boundary_properties_and_score_ownership_are_separate_from_model_response():
    material, raw = example_material()
    assert "sink_boundaries" not in raw
    _, compiled, _ = compile_response(raw, material)
    assert compiled["sink_boundaries"][0]["sink_type"] == "model_observe"
    assert compiled["sink_boundaries"][0]["exposure_level"] == 2
    assert "Do not emit sink_boundaries, sink_type, exposure_level" in INSTRUCTIONS
    assert "kind,name,operand_refs,access_scope,retention" in INSTRUCTIONS
    assert "Request delivery is distinct from receive inputs" in INSTRUCTIONS
