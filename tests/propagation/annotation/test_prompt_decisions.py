"""Executable authored examples; these tests do not predict model decisions."""

from copy import deepcopy
import json
import re

import pytest

from tests.propagation.annotation.helpers import source_bundle
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.profiles import RawAnnotationResponse
from skillflow.propagation.contracts.profiles import FailureResponse
from pydantic import TypeAdapter
from skillflow.propagation.annotation.prompts import INSTRUCTIONS
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.prompts import response_format_example


def example_material(source=None):
    raw = response_format_example()
    quote = raw["profiles"]["ir_example_select"]["evidences"][0]["quote"]
    cfg = {
        "entry_block_id": "entry", "constraints": [], "edges": [], "declared_context_keys": [],
        "blocks": {"entry": {
            "block_id": "entry", "block_name": "Example", "constraints": [], "data_source_kind": None,
            "instructions": [
                {"id": "ir_example_select", "opcode": "select_excerpt", "constraints": [], "metadata": {},
                 "inputs": [{"type": "literal", "literal_value": {"excerpt": "Original text"}}],
                 "outputs": [{"type": "result", "identifier": "selected"}]},
                {"id": "ir_example_return", "opcode": "return", "constraints": [], "metadata": {},
                 "inputs": [{"type": "result", "identifier": "selected"}], "outputs": []},
            ],
        }},
    }
    return prepare_material(source_bundle(source or quote), cfg), raw


def bind_example_evidence(raw, material, quote=None):
    """Bind an independently authored fixture to its real evidence unit."""
    if isinstance(raw, dict):
        if raw.get("ref_id") == "s_example":
            raw["ref_id"] = material["source_index"][0]["id"]
            if quote is not None:
                raw["quote"] = quote
        for value in raw.values():
            bind_example_evidence(value, material, quote)
    elif isinstance(raw, list):
        for value in raw:
            bind_example_evidence(value, material, quote)


def test_complete_format_example_is_typed_and_executable_with_its_own_evidence():
    material, raw = example_material()
    serialized = json.dumps(raw, ensure_ascii=False)
    assert RawAnnotationResponse.model_validate_json(serialized)
    assert set(raw) == {"profiles", "locations", "transfer_specs", "outcome", "location_evidences"}
    bind_example_evidence(raw, material)
    checked, compiled, _ = compile_response(raw, material)
    assert checked == RawAnnotationResponse.model_validate(raw).model_dump(mode="json")
    assert compiled["profiles"]["ir_example_select"]["effects"] == ["model_observe", "transform"]
    assert compiled["transfer_specs"]["ir_example_select"]["events"][1]["atomic_ops"][0]["op"] == "select_part"
    assert compiled["transfer_specs"]["ir_example_return"] == {"order": "fixed", "precedence": [], "events": [], "output_bindings": []}


def test_format_example_is_separate_from_schema_and_complete_original_input():
    material, _ = example_material()
    before = deepcopy(material)
    prompt = build_prompt(material)
    example = json.loads(prompt.split("\nFORMAT_EXAMPLE\n")[1].split("\nRESPONSE_JSON_SCHEMA\n")[0])
    schema = json.loads(prompt.split("\nRESPONSE_JSON_SCHEMA\n")[1].split("\nINPUT_JSON\n")[0])
    payload = json.loads(prompt.split("\nINPUT_JSON\n")[1])
    assert example == response_format_example()
    assert schema == TypeAdapter(RawAnnotationResponse | FailureResponse).json_schema()
    assert payload == before == material
    assert "Never copy its IDs, quotes, fields, or conclusions" in INSTRUCTIONS
    assert not re.search(r"[\u3400-\u9fff]", INSTRUCTIONS)
    assert "Write all inference reasons and failure explanations in Chinese" in INSTRUCTIONS


@pytest.mark.parametrize("operation", ["filter_items", "compute"])
@pytest.mark.parametrize("mode", ["default", "local"])
def test_authored_filter_count_pairs_keep_input_or_return_observation_versions(operation, mode):
    task = "Keep enabled records unchanged." if operation == "filter_items" else "Count the records."
    boundary = (" Run this operation in an isolated local worker; only its result is returned to the agent, "
                "without returning the input records.") if mode == "local" else ""
    source = task + boundary
    material, raw = example_material(source)
    bind_example_evidence(raw, material, source)
    segment = raw["transfer_specs"]["ir_example_select"]["events"][0]
    segment["mode"] = mode
    segment["returns"] = [{"kind": "local", "name": "processed"}] if mode == "local" else []
    evidence = segment["evidences"]
    operation_spec = {"op": operation, "output": "processed", "evidences": evidence}
    if operation == "filter_items":
        operation_spec.update(input={"kind": "input", "index": 0}, predicate="enabled records")
    else:
        operation_spec.update(inputs=[{"kind": "input", "index": 0}], dependencies=["derived"])
    segment["events"][0]["atomic_ops"] = [operation_spec]
    raw["transfer_specs"]["ir_example_select"]["output_bindings"][0]["value"]["name"] = "processed"
    _, compiled, _ = compile_response(raw, material)
    profile = compiled["profiles"]["ir_example_select"]
    expected = ["transform", "model_observe"] if mode == "local" else ["model_observe", "transform"]
    assert profile["effects"] == expected
    observation_index = expected.index("model_observe")
    observed = compiled["transfer_specs"]["ir_example_select"]["events"][observation_index]["atomic_ops"][0]["inputs"]
    assert observed == ([{"kind": "local", "name": "processed"}] if mode == "local"
                        else [{"kind": "input", "index": 0}])


def test_same_ir_classification_and_unchanged_field_have_separate_relations():
    text = "The agent runtime classifies the response and returns its payload field unchanged."
    material, raw = example_material(text)
    cfg = deepcopy(material["cfg"])
    cfg["blocks"]["entry"]["instructions"][0]["outputs"].append({"type": "result", "identifier": "classification"})
    material = prepare_material(source_bundle(text), cfg)
    bind_example_evidence(raw, material, text)
    spec = raw["transfer_specs"]["ir_example_select"]
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
    atoms = compiled["transfer_specs"]["ir_example_select"]["events"][1]["atomic_ops"]
    assert [(a["op"], a["output"]) for a in atoms] == [("select_part", "payload"), ("compute", "classification")]
    assert compiled["profiles"]["ir_example_select"]["effects"] == ["model_observe", "transform"]


def test_prompt_replaces_implementation_guessing_and_opaque_field_fallback():
    decision = INSTRUCTIONS.split("Use the following decision order", 1)[1].split("The compiler observes", 1)[0]
    assert decision.index("Identify the content") < decision.index("use model") < decision.index("Use local only") < decision.index("Otherwise use default")
    for boundary in (
        "Could be implemented locally does not mean local isolation is specified",
        "A selection predicate, an opcode name, an executor label",
        "[] requires a supported no-content-return mechanism",
        "Do not weaken an explicit unchanged field relation to opaque compute",
        "Neither output's operation choice determines the other",
        "only specifies a filter: use default with filter_items",
        '"Count the records" uses default with compute',
    ):
        assert boundary in INSTRUCTIONS


def test_boundary_properties_and_score_ownership_are_separate_from_model_response():
    material, raw = example_material()
    assert "sink_boundaries" not in raw
    bind_example_evidence(raw, material)
    _, compiled, _ = compile_response(raw, material)
    assert compiled["sink_boundaries"][0]["sink_type"] == "model_observe"
    assert compiled["sink_boundaries"][0]["exposure_level"] == 2
    assert "Do not output sink_boundaries, sink_type, exposure_level" in INSTRUCTIONS
    assert "identity, category, access_scope and retention" in INSTRUCTIONS
    assert "receive dependencies and subsequent model observation" in INSTRUCTIONS
