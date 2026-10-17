from skillflow.common.prompt_format import render_prompt_format
from skillflow.propagation.contracts.profiles import RawAnnotationResponse, FailureResponse
from pydantic import TypeAdapter
from tests.propagation.annotation.helpers import effects_of
"""Typed processing implications, without LLM semantic claims or API calls."""
from copy import deepcopy
import json

import pytest

from skillflow.propagation.contracts.specs import IRSemantics
from skillflow.propagation.contracts.specs import iter_effect_events
from skillflow.propagation.contracts.specs import iter_scoped_events
from skillflow.common.recording import canonical_sha256
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.contracts.profiles import AnnotationResponse
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.services import validate_response
from skillflow.propagation.annotation.services import validate_compiled_response
from skillflow.propagation.annotation.services import annotate_skill
from tests.propagation.annotation.helpers import material, valid_response, valid_raw_response, semantics, FakeClient


def set_operator(spec, prepared, ir_id, operators):
    template = semantics(prepared, ir_id, operator=operators)
    for key in ("operator", "operator_evidences"):
        spec[key] = template[key]


def raw_fixture():
    prepared = material()
    response = valid_raw_response(prepared)
    for ir_id, spec in response["ir_semantics"].items():
        if spec["events"]:
            spec["events"][0]["mode"] = "default"
    return prepared, response


def test_default_acquisition_observes_output_and_each_transform_phase_inputs():
    prepared, raw = raw_fixture()
    before = deepcopy(raw)
    checked, compiled, mapping = compile_response(raw, prepared)
    assert checked == before and raw == before
    assert effects_of(compiled["ir_semantics"]["ir_read"]) == ["fs_read", "model_observe"]
    assert effects_of(compiled["ir_semantics"]["ir_filter"]) == ["model_observe", "transform"]
    observation = compiled["ir_semantics"]["ir_read"]["events"][1]["atomic_ops"][0]
    assert observation["inputs"] == [{"kind": "local", "name": "stage_0"}]
    assert mapping["raw_sha256"] == canonical_sha256(checked)
    assert mapping["compiled_sha256"] == canonical_sha256(compiled)
    assert validate_response(raw, prepared) == compiled
    assert validate_compiled_response(compiled, prepared) == compiled
    with pytest.raises(ValueError):
        validate_response(compiled, prepared)  # no implicit raw/compiled compatibility
    assert SCHEMA_VERSION == "security-profile-v14"


@pytest.mark.parametrize("returns,expected", [([], ["fs_read"]),
    ([{"kind": "local", "name": "stage_0"}], ["fs_read", "model_observe"])])
def test_local_acquisition_only_observes_explicit_returns(returns, expected):
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    segment.update(mode="local", returns=returns)
    compiled = compile_response(raw, prepared)[1]
    assert effects_of(compiled["ir_semantics"]["ir_read"]) == expected


def test_local_boundary_requires_explicit_return_list_and_non_contract_evidence():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    segment["mode"] = "local"
    segment.pop("returns")
    with pytest.raises(ValueError, match="explicit returns"):
        compile_response(raw, prepared)
    segment["returns"] = []
    rule = prepared["runtime_contract"]["rules"][0]
    segment["evidences"] = [{"rule_id": rule["id"], "reason": "不能单靠默认推断局部隔离。"}]
    with pytest.raises(ValueError, match="mechanism evidence"):
        compile_response(raw, prepared)


def test_raw_model_observe_and_model_mode_without_llm_are_rejected():
    prepared, raw = raw_fixture()
    raw["ir_semantics"]["ir_filter"]["events"][0]["mode"] = "model"
    with pytest.raises(ValueError, match="requires llm"):
        compile_response(raw, prepared)
    set_operator(raw["ir_semantics"]["ir_filter"], prepared, "ir_filter", ["llm"])
    assert effects_of(compile_response(raw, prepared)[1]["ir_semantics"]["ir_filter"]) == ["model_observe", "transform"]
    raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["effect"] = "model_observe"
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


def test_local_transform_does_not_observe_raw_input_before_return():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    segment.update(mode="local", returns=[{"kind": "local", "name": "clean"}])
    evidence = segment["evidences"]
    segment["events"][0]["atomic_ops"] = [{"op": "exclude_parts", "input": {"kind": "input", "index": 0},
        "paths": [["secret"]], "output": "clean", "evidences": evidence}]
    raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = {"kind": "local", "name": "clean"}
    compiled = compile_response(raw, prepared)[1]
    assert effects_of(compiled["ir_semantics"]["ir_filter"]) == ["transform", "model_observe"]
    assert compiled["ir_semantics"]["ir_filter"]["events"][1]["atomic_ops"][0]["inputs"] == [{"kind": "local", "name": "clean"}]


def test_two_transforms_keep_intermediate_version_without_observing_own_computation():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    first = segment["events"][0]["atomic_ops"][0]
    second = deepcopy(first)
    second.update(inputs=[{"kind": "local", "name": "stage_0"}], output="stage_1")
    segment["events"][0]["atomic_ops"].append(second)
    raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"]["name"] = "stage_1"
    _, compiled, mapping = compile_response(raw, prepared)
    assert effects_of(compiled["ir_semantics"]["ir_filter"]) == ["model_observe", "transform"]
    assert compiled["ir_semantics"]["ir_filter"]["events"][1]["atomic_ops"][1]["inputs"] == [{"kind": "local", "name": "stage_0"}]
    assert compiled["ir_semantics"]["ir_filter"]["operator"] == raw["ir_semantics"]["ir_filter"]["operator"]
    assert "roles" not in compiled["ir_semantics"]["ir_filter"]


def test_observation_dedup_is_per_processing_segment_not_global():
    prepared, raw = raw_fixture()
    spec = raw["ir_semantics"]["ir_filter"]
    first = spec["events"][0]
    second = deepcopy(first)
    second["events"][0]["atomic_ops"][0]["output"] = "stage_1"
    spec["events"].append(second)
    compiled = compile_response(raw, prepared)[1]
    assert effects_of(compiled["ir_semantics"]["ir_filter"]) == ["model_observe", "transform", "model_observe", "transform"]


def test_for_each_shared_item_and_no_local_escape_or_acquisition():
    prepared, raw = raw_fixture()
    spec = raw["ir_semantics"]["ir_filter"]
    segment = spec["events"][0]
    segment["events"][0]["atomic_ops"] = [
        {"op": "select_part", "input": {"kind": "local", "name": "row"}, "path": [field],
         "output": field, "evidences": segment["evidences"]} for field in ("recipient", "summary")]
    spec["events"] = [{"kind": "for_each", "collection": {"kind": "input", "index": 0},
                       "item": "row", "body": [segment], "evidences": segment["evidences"]}]
    spec["output_bindings"][0]["value"] = {"kind": "input", "index": 0}
    compiled = compile_response(raw, prepared)[1]
    typed = IRSemantics.model_validate(compiled["ir_semantics"]["ir_filter"])
    assert len(list(iter_effect_events(typed))) == 2
    assert [(a, b) for a, b, _ in iter_scoped_events(typed)] == [(0, 0), (0, 1)]
    assert typed.events[0].body[0].atomic_ops[0].inputs[0].name == "row"
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "summary"}
    with pytest.raises(ValueError, match="undefined local"):
        compile_response(raw, prepared)
    spec["output_bindings"][0]["value"] = {"kind": "input", "index": 0}
    segment["events"][0]["atomic_ops"] = [{"op": "read", "location": "ir_read_boundary_0", "output": "bad", "evidences": segment["evidences"]}]
    segment["events"][0]["effect"] = "fs_read"
    with pytest.raises(ValueError, match="must not read, receive, or write"):
        compile_response(raw, prepared)


def test_filter_items_preserves_explicit_predicate_as_data_not_execution():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    segment["events"][0]["atomic_ops"] = [{"op": "filter_items", "input": {"kind": "input", "index": 0},
        "predicate": "仅保留启用记录；不执行这里的文字", "output": "stage_0", "evidences": segment["evidences"]}]
    compiled = compile_response(raw, prepared)[1]
    assert compiled["ir_semantics"]["ir_filter"]["events"][1]["atomic_ops"][0]["predicate"] == "仅保留启用记录；不执行这里的文字"


def test_one_model_call_compiles_and_preserves_partial_order():
    prepared, raw = raw_fixture()
    raw["ir_semantics"]["ir_filter"]["order"] = "partial"
    client = FakeClient(raw)
    result = annotate_skill(prepared["source"], prepared["cfg"], client=client, task_baseline=prepared["task"])
    assert len(client.prompts) == 1 and result["ir_semantics"]["ir_filter"]["order"] == "partial"
    prompt = build_prompt(prepared)
    schema = TypeAdapter(RawAnnotationResponse | FailureResponse).json_schema()
    assert render_prompt_format(schema) in prompt and "RESPONSE_JSON_SCHEMA" not in prompt
    assert "RawAnnotationResponse" in json.dumps(schema)
    assert "No handwritten model_observe" in prompt
    rules = prepared["runtime_contract"]["rules"]
    assert all(rule["id"] in prompt for rule in rules)


def test_default_tool_receive_observes_response_not_request_arguments():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    operation = segment["events"][0]["atomic_ops"][0]
    operation.update(op="receive", inputs=[{"kind": "literal", "value": "request argument"}])
    segment["events"][0]["atomic_ops"].insert(0, {
        "op": "deliver", "inputs": deepcopy(operation["inputs"]),
        "target": operation["location"], "evidences": deepcopy(operation["evidences"])})
    raw["locations"][operation["location"]]["kind"] = "tool"
    segment["events"][0]["effect"] = None
    segment["events"][0].pop("evidences")
    set_operator(raw["ir_semantics"]["ir_read"], prepared, "ir_read", ["tool"])
    raw["ir_semantics"]["ir_read"]["empty_effect_evidences"] = deepcopy(segment["evidences"])
    compiled = compile_response(raw, prepared)[1]
    assert effects_of(compiled["ir_semantics"]["ir_read"]) == ["model_observe"]
    events = compiled["ir_semantics"]["ir_read"]["events"]
    assert events[0]["effect"] is None
    assert events[1]["atomic_ops"][0]["inputs"] == [{"kind": "local", "name": "stage_0"}]
    assert all(ref.get("value") != "request argument" for ref in events[1]["atomic_ops"][0]["inputs"])


def test_model_compute_and_delivery_do_not_reobserve_generated_result():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    segment["mode"] = "model"
    evidence = segment["evidences"]
    raw["locations"]["remote"] = {"kind": "remote", "name": "test destination", "operand_refs": [],
                                   "access_scope": "recipient", "retention": None}
    raw["location_evidences"]["remote"] = evidence
    segment["events"][0]["atomic_ops"].append({"op": "deliver", "inputs": [{"kind": "local", "name": "stage_0"}],
                                               "target": "remote", "evidences": evidence})
    set_operator(raw["ir_semantics"]["ir_filter"], prepared, "ir_filter", ["llm"])
    segment["events"][0]["effect"] = "net_send"
    checked, compiled, mapping = compile_response(raw, prepared)
    item = compiled["ir_semantics"]["ir_filter"]
    assert effects_of(item) == ["model_observe", "net_send"]
    assert sum(effect == "net_send" for effect in effects_of(item)) == 1
    assert item["events"][1]["effect"] == "net_send" and item["events"][1]["evidences"]
    assert len(compiled["ir_semantics"]["ir_filter"]["events"][1]["atomic_ops"]) == 2
    changed = deepcopy(compiled)
    changed["ir_semantics"]["ir_filter"]["events"][0]["atomic_ops"][0]["inputs"] = [{"kind": "literal", "value": "changed"}]
    assert canonical_sha256(changed) != mapping["compiled_sha256"]
    assert compile_response(checked, prepared)[1:] == (compiled, mapping)


def test_unchanged_reference_deduplicates_only_inside_one_segment():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    operation = deepcopy(segment["events"][0]["atomic_ops"][0])
    operation["output"] = "other"
    segment["events"][0]["atomic_ops"].append(operation)
    compiled = compile_response(raw, prepared)[1]
    assert effects_of(compiled["ir_semantics"]["ir_filter"]) == ["model_observe", "transform"]
    assert len(compiled["ir_semantics"]["ir_filter"]["events"][1]["atomic_ops"]) == 2


def test_local_return_cannot_reference_a_future_processing_segment():
    prepared, raw = raw_fixture()
    first = raw["ir_semantics"]["ir_filter"]["events"][0]
    first.update(mode="local", returns=[{"kind": "local", "name": "future"}])
    second = deepcopy(first)
    second.update(mode="default", returns=[])
    second["events"][0]["atomic_ops"][0]["output"] = "future"
    raw["ir_semantics"]["ir_filter"]["events"].append(second)
    with pytest.raises(ValueError, match="undefined local"):
        compile_response(raw, prepared)


def test_acquisition_observation_slices_data_tail_without_duplicating_read():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    segment["events"][0]["atomic_ops"].append({
        "op": "select_part", "input": {"kind": "local", "name": "stage_0"},
        "path": ["requested"], "output": "leaf", "evidences": segment["evidences"]})
    raw["ir_semantics"]["ir_read"]["output_bindings"][0]["value"] = {"kind": "local", "name": "leaf"}
    _, compiled, mapping = compile_response(raw, prepared)
    item = compiled["ir_semantics"]["ir_read"]
    assert effects_of(item) == ["fs_read", "model_observe", "transform"]
    assert item["operator"] == raw["ir_semantics"]["ir_read"]["operator"]
    assert "roles" not in item
    assert [op["op"] for event in compiled["ir_semantics"]["ir_read"]["events"] for op in event["atomic_ops"]] == ["read", "deliver", "select_part"]
    assert item["events"][2]["effect"] == "transform" and item["events"][2]["evidences"]
    assert any(row["kind"] == "slice" and row["raw_atomic_range"] == [1, 2] for row in mapping["events"])


@pytest.mark.parametrize("step", [{"kind": "element", "scope": "forged"}, True, -1])
@pytest.mark.parametrize("operation", ["select_part", "exclude_parts", "update_fields", "build"])
def test_annotation_paths_reject_program_generated_element_scope_and_invalid_indexes(operation, step):
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    atom = {"op": operation, "output": "stage_0", "evidences": segment["evidences"]}
    value = {"kind": "input", "index": 0}
    if operation != "build":
        atom["input"] = value
    if operation == "select_part":
        atom["path"] = [step]
    elif operation == "exclude_parts":
        atom["paths"] = [[step]]
    elif operation == "update_fields":
        atom["updates"] = [{"path": [step], "value": value}]
    else:
        atom.update(container="object", parts=[{"path": [step], "value": value}])
    segment["events"][0]["atomic_ops"] = [atom]
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


def test_model_schema_does_not_expose_data_element_step():
    prepared, _ = raw_fixture()
    schema = render_prompt_format(TypeAdapter(RawAnnotationResponse | FailureResponse).json_schema())
    assert schema in build_prompt(prepared)
    assert '"ElementStep"' not in schema
    assert '"scope"' not in schema


def guarded_build_fixture():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    evidence = deepcopy(segment["evidences"])
    segment["events"][0]["atomic_ops"] = [{"op": "build", "container": "object",
        "parts": [{"path": ["optional"], "value": {"kind": "input", "index": 0},
                   "when": {"kind": "literal", "value": False}}],
        "output": "stage_0", "evidences": evidence}]
    return prepared, raw


def test_conditional_member_observation_and_control_use_share_guard():
    prepared, raw = guarded_build_fixture()
    checked, compiled, mapping = compile_response(raw, prepared)
    atoms = [op for event in compiled["ir_semantics"]["ir_filter"]["events"] for op in event["atomic_ops"]]
    observations = [op for op in atoms if op["op"] == "deliver"]
    assert observations[0]["inputs"] == [{"kind": "literal", "value": False}]
    assert "when" not in observations[0]
    assert observations[1]["inputs"] == [{"kind": "input", "index": 0}]
    assert observations[1]["when"] == {"kind": "literal", "value": False}
    assert atoms[-1]["parts"][0]["when"] == observations[1]["when"]
    assert mapping["compiler_version"] == "skillflow-processing-compiler-v8"
    assert compile_response(checked, prepared)[1:] == (compiled, mapping)


def test_conditional_observation_cannot_suppress_later_unconditional_input():
    prepared, raw = guarded_build_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    original = segment["events"][0]["atomic_ops"][0]
    second = deepcopy(original)
    second["output"] = "other"
    second["parts"][0].pop("when")
    segment["events"][0]["atomic_ops"].append(second)
    compiled = compile_response(raw, prepared)[1]
    observations = [op for event in compiled["ir_semantics"]["ir_filter"]["events"]
                    for op in event["atomic_ops"] if op["op"] == "deliver"
                    and op["inputs"] == [{"kind": "input", "index": 0}]]
    assert len(observations) == 2
    assert observations[0]["when"]["value"] is False
    assert "when" not in observations[1]


def test_earlier_unconditional_observation_covers_later_conditional_repeat():
    prepared, raw = guarded_build_fixture()
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    conditional = deepcopy(segment["events"][0]["atomic_ops"][0])
    conditional["output"] = "other"
    segment["events"][0]["atomic_ops"][0]["parts"][0].pop("when")
    segment["events"][0]["atomic_ops"].append(conditional)
    compiled = compile_response(raw, prepared)[1]
    observations = [op for event in compiled["ir_semantics"]["ir_filter"]["events"]
                    for op in event["atomic_ops"] if op["op"] == "deliver"
                    and op["inputs"] == [{"kind": "input", "index": 0}]]
    assert len(observations) == 1 and "when" not in observations[0]


def test_raw_guarded_delivery_is_not_a_model_generated_observation():
    prepared, raw = raw_fixture()
    segment = raw["ir_semantics"]["ir_read"]["events"][0]
    read = deepcopy(segment["events"][0]["atomic_ops"][0])
    read.update(op="deliver", inputs=[{"kind": "literal", "value": "payload"}],
                target=read.pop("location"), when={"kind": "literal", "value": True})
    read.pop("output")
    segment["events"][0]["atomic_ops"] = [read]
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


def test_compiler_preserves_unique_partial_request_causal_link():
    prepared, raw = raw_fixture()
    spec = raw["ir_semantics"]["ir_read"]
    spec["order"] = "partial"
    segment = spec["events"][0]
    read = segment["events"][0]["atomic_ops"][0]
    evidence, location = deepcopy(read["evidences"]), read["location"]
    raw["locations"][location]["kind"] = "tool"
    set_operator(spec, prepared, "ir_read", ["tool"])
    spec["empty_effect_evidences"] = deepcopy(segment["evidences"])
    segment["events"] = [{"effect": None, "atomic_ops": [
        {"op": "deliver", "inputs": [{"kind": "literal", "value": "request"}], "target": location, "evidences": evidence},
        {"op": "receive", "inputs": [{"kind": "literal", "value": "request"}], "location": location, "output": "stage_0", "evidences": evidence}]}]
    compiled = compile_response(raw, prepared)[1]
    precedence = compiled["ir_semantics"]["ir_read"]["precedence"]
    assert any(item["before"] == {"event_index": 0, "body_event_index": None, "op_index": 0}
               and item["after"] == {"event_index": 0, "body_event_index": None, "op_index": 1}
               for item in precedence)
