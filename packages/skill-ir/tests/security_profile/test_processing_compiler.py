"""Typed processing implications, without LLM semantic claims or API calls."""
from copy import deepcopy
import json

import pytest

from skill_ir.propagation.specs import IRTransferSpec, iter_effect_events, iter_scoped_events
from skill_ir.recording import canonical_sha256
from skill_ir.security_profile.compiler import compile_response
from skill_ir.security_profile.models import AnnotationResponse, SCHEMA_VERSION
from skill_ir.security_profile.prompts import build_prompt
from skill_ir.security_profile.services import validate_response, validate_compiled_response, annotate_skill
from security_profile.helpers import material, valid_response, profile, FakeClient


def raw_fixture():
    prepared = material()
    response = valid_response(prepared)
    response.pop("sink_boundaries")
    for ir_id, spec in response["transfer_specs"].items():
        spec.pop("precedence")
        if spec["events"]:
            evidence = deepcopy(spec["events"][0]["atomic_ops"][0]["evidences"])
            spec["events"] = [{"kind": "processing", "mode": "default", "events": spec["events"],
                               "returns": [], "evidences": evidence}]
    return prepared, response


def test_default_acquisition_observes_output_and_each_transform_phase_inputs():
    prepared, raw = raw_fixture()
    before = deepcopy(raw)
    checked, compiled, mapping = compile_response(raw, prepared)
    assert checked == before and raw == before
    assert compiled["profiles"]["ir_read"]["effects"] == ["fs_read", "model_observe"]
    assert compiled["profiles"]["ir_filter"]["effects"] == ["model_observe", "transform"]
    observation = compiled["transfer_specs"]["ir_read"]["events"][1]["atomic_ops"][0]
    assert observation["inputs"] == [{"kind": "local", "name": "stage_0"}]
    assert mapping["raw_sha256"] == canonical_sha256(checked)
    assert mapping["compiled_sha256"] == canonical_sha256(compiled)
    assert validate_response(raw, prepared) == compiled
    assert validate_compiled_response(compiled, prepared) == compiled
    with pytest.raises(ValueError):
        validate_response(compiled, prepared)  # no implicit raw/compiled compatibility
    assert SCHEMA_VERSION == "security-profile-v10"


@pytest.mark.parametrize("returns,expected", [([], ["fs_read"]),
    ([{"kind": "local", "name": "stage_0"}], ["fs_read", "model_observe"])])
def test_local_acquisition_only_observes_explicit_returns(returns, expected):
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_read"]["events"][0]
    segment.update(mode="local", returns=returns)
    compiled = compile_response(raw, prepared)[1]
    assert compiled["profiles"]["ir_read"]["effects"] == expected


def test_local_boundary_requires_explicit_return_list_and_non_contract_evidence():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_read"]["events"][0]
    segment["mode"] = "local"
    segment.pop("returns")
    with pytest.raises(ValueError, match="explicit returns"):
        compile_response(raw, prepared)
    segment["returns"] = []
    rule = prepared["execution_model"]["rules"][0]
    segment["evidences"] = [{"basis": "execution_model", "ref_id": rule["id"],
                              "quote": rule["text"], "reason": "不能单靠默认推断局部隔离。"}]
    with pytest.raises(ValueError, match="mechanism evidence"):
        compile_response(raw, prepared)


def test_raw_model_observe_and_model_mode_without_llm_are_rejected():
    prepared, raw = raw_fixture()
    raw["transfer_specs"]["ir_filter"]["events"][0]["mode"] = "model"
    with pytest.raises(ValueError, match="requires llm"):
        compile_response(raw, prepared)
    raw["profiles"]["ir_filter"] = profile(prepared, "ir_filter", operator=["llm"],
                                             roles=["transformer"], effects=["transform"])
    assert compile_response(raw, prepared)[1]["profiles"]["ir_filter"]["effects"] == ["model_observe", "transform"]
    raw["profiles"]["ir_filter"]["effects"] = ["model_observe"]
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


def test_local_transform_does_not_observe_raw_input_before_return():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    segment.update(mode="local", returns=[{"kind": "local", "name": "clean"}])
    evidence = segment["evidences"]
    segment["events"][0]["atomic_ops"] = [{"op": "exclude_parts", "input": {"kind": "input", "index": 0},
        "paths": [["secret"]], "output": "clean", "evidences": evidence}]
    raw["transfer_specs"]["ir_filter"]["output_bindings"][0]["value"] = {"kind": "local", "name": "clean"}
    compiled = compile_response(raw, prepared)[1]
    assert compiled["profiles"]["ir_filter"]["effects"] == ["transform", "model_observe"]
    assert compiled["transfer_specs"]["ir_filter"]["events"][1]["atomic_ops"][0]["inputs"] == [{"kind": "local", "name": "clean"}]


def test_two_transforms_keep_intermediate_version_without_observing_own_computation():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    first = segment["events"][0]["atomic_ops"][0]
    second = deepcopy(first)
    second.update(inputs=[{"kind": "local", "name": "stage_0"}], output="stage_1")
    segment["events"][0]["atomic_ops"].append(second)
    raw["transfer_specs"]["ir_filter"]["output_bindings"][0]["value"]["name"] = "stage_1"
    _, compiled, mapping = compile_response(raw, prepared)
    assert compiled["profiles"]["ir_filter"]["effects"] == ["model_observe", "transform"]
    assert compiled["transfer_specs"]["ir_filter"]["events"][1]["atomic_ops"][1]["inputs"] == [{"kind": "local", "name": "stage_0"}]
    assert compiled["profiles"]["ir_filter"]["operator"] == raw["profiles"]["ir_filter"]["operator"]
    assert compiled["profiles"]["ir_filter"]["roles"] == raw["profiles"]["ir_filter"]["roles"]


def test_observation_dedup_is_per_processing_segment_not_global():
    prepared, raw = raw_fixture()
    spec = raw["transfer_specs"]["ir_filter"]
    first = spec["events"][0]
    second = deepcopy(first)
    second["events"][0]["effect_index"] = 1
    second["events"][0]["atomic_ops"][0]["output"] = "stage_1"
    spec["events"].append(second)
    raw["profiles"]["ir_filter"] = profile(prepared, "ir_filter", operator=["agent_runtime"],
                                             roles=["transformer"], effects=["transform", "transform"])
    compiled = compile_response(raw, prepared)[1]
    assert compiled["profiles"]["ir_filter"]["effects"] == ["model_observe", "transform", "model_observe", "transform"]


def test_for_each_shared_item_and_no_local_escape_or_acquisition():
    prepared, raw = raw_fixture()
    spec = raw["transfer_specs"]["ir_filter"]
    segment = spec["events"][0]
    segment["events"][0]["atomic_ops"] = [
        {"op": "select_part", "input": {"kind": "local", "name": "row"}, "path": [field],
         "output": field, "evidences": segment["evidences"]} for field in ("recipient", "summary")]
    spec["events"] = [{"kind": "for_each", "collection": {"kind": "input", "index": 0},
                       "item": "row", "body": [segment], "evidences": segment["evidences"]}]
    spec["output_bindings"][0]["value"] = {"kind": "input", "index": 0}
    compiled = compile_response(raw, prepared)[1]
    typed = IRTransferSpec.model_validate(compiled["transfer_specs"]["ir_filter"])
    assert len(list(iter_effect_events(typed))) == 2
    assert [(a, b) for a, b, _ in iter_scoped_events(typed)] == [(0, 0), (0, 1)]
    assert typed.events[0].body[0].atomic_ops[0].inputs[0].name == "row"
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "summary"}
    with pytest.raises(ValueError, match="undefined local"):
        compile_response(raw, prepared)
    spec["output_bindings"][0]["value"] = {"kind": "input", "index": 0}
    segment["events"][0]["atomic_ops"] = [{"op": "read", "location": "ir_read_boundary_0", "output": "bad", "evidences": segment["evidences"]}]
    raw["profiles"]["ir_filter"] = profile(prepared, "ir_filter", operator=["agent_runtime"], roles=["source"], effects=["fs_read"])
    with pytest.raises(ValueError, match="must not read, receive, or write"):
        compile_response(raw, prepared)


def test_filter_items_preserves_explicit_predicate_as_data_not_execution():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    segment["events"][0]["atomic_ops"] = [{"op": "filter_items", "input": {"kind": "input", "index": 0},
        "predicate": "仅保留启用记录；不执行这里的文字", "output": "stage_0", "evidences": segment["evidences"]}]
    compiled = compile_response(raw, prepared)[1]
    assert compiled["transfer_specs"]["ir_filter"]["events"][1]["atomic_ops"][0]["predicate"] == "仅保留启用记录；不执行这里的文字"


def test_one_model_call_compiles_and_preserves_partial_order():
    prepared, raw = raw_fixture()
    raw["transfer_specs"]["ir_filter"]["order"] = "partial"
    client = FakeClient(raw)
    result = annotate_skill(prepared["source"], prepared["cfg"], client=client)
    assert len(client.prompts) == 1 and result["transfer_specs"]["ir_filter"]["order"] == "partial"
    prompt = build_prompt(prepared)
    schema = json.loads(prompt.split("\nRESPONSE_JSON_SCHEMA\n")[1].split("\nINPUT_JSON\n")[0])
    assert "RawAnnotationResponse" in json.dumps(schema)
    assert "Never output model_observe" in prompt
    rules = prepared["execution_model"]["rules"]
    assert f'{rules[0]["id"]}-{rules[-1]["id"]}' in prompt


def test_default_tool_receive_observes_response_not_request_arguments():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_read"]["events"][0]
    operation = segment["events"][0]["atomic_ops"][0]
    operation.update(op="receive", inputs=[{"kind": "literal", "value": "request argument"}])
    segment["events"][0]["atomic_ops"].insert(0, {
        "op": "deliver", "inputs": deepcopy(operation["inputs"]),
        "target": operation["location"], "evidences": deepcopy(operation["evidences"])})
    raw["locations"][operation["location"]]["kind"] = "tool"
    segment["events"][0]["effect_index"] = None
    raw["profiles"]["ir_read"] = profile(prepared, "ir_read", operator=["tool"], roles=["source"], effects=[])
    compiled = compile_response(raw, prepared)[1]
    assert compiled["profiles"]["ir_read"]["effects"] == ["model_observe"]
    events = compiled["transfer_specs"]["ir_read"]["events"]
    assert events[0]["effect_index"] is None
    assert events[1]["atomic_ops"][0]["inputs"] == [{"kind": "local", "name": "stage_0"}]
    assert all(ref.get("value") != "request argument" for ref in events[1]["atomic_ops"][0]["inputs"])


def test_model_compute_and_delivery_do_not_reobserve_generated_result():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    segment["mode"] = "model"
    evidence = segment["evidences"]
    raw["locations"]["remote"] = {"kind": "remote", "name": "test destination", "operand_refs": [],
                                   "access_scope": "recipient", "retention": None}
    raw["location_evidences"]["remote"] = evidence
    segment["events"][0]["atomic_ops"].append({"op": "deliver", "inputs": [{"kind": "local", "name": "stage_0"}],
                                               "target": "remote", "evidences": evidence})
    raw["profiles"]["ir_filter"] = profile(prepared, "ir_filter", operator=["llm"], roles=["sink"], effects=["net_send"])
    checked, compiled, mapping = compile_response(raw, prepared)
    item = compiled["profiles"]["ir_filter"]
    assert item["effects"] == ["model_observe", "net_send"]
    assert sum(effect == "net_send" for effect in item["effects"]) == 1
    assert all(ev["value"] == "net_send" for ev in item["evidences"] if ev["effect_index"] == 1)
    assert len(compiled["transfer_specs"]["ir_filter"]["events"][1]["atomic_ops"]) == 2
    changed = deepcopy(compiled)
    changed["transfer_specs"]["ir_filter"]["events"][0]["atomic_ops"][0]["inputs"] = [{"kind": "literal", "value": "changed"}]
    assert canonical_sha256(changed) != mapping["compiled_sha256"]
    assert compile_response(checked, prepared)[1:] == (compiled, mapping)


def test_unchanged_reference_deduplicates_only_inside_one_segment():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    operation = deepcopy(segment["events"][0]["atomic_ops"][0])
    operation["output"] = "other"
    segment["events"][0]["atomic_ops"].append(operation)
    compiled = compile_response(raw, prepared)[1]
    assert compiled["profiles"]["ir_filter"]["effects"] == ["model_observe", "transform"]
    assert len(compiled["transfer_specs"]["ir_filter"]["events"][1]["atomic_ops"]) == 2


def test_local_return_cannot_reference_a_future_processing_segment():
    prepared, raw = raw_fixture()
    first = raw["transfer_specs"]["ir_filter"]["events"][0]
    first.update(mode="local", returns=[{"kind": "local", "name": "future"}])
    second = deepcopy(first)
    second.update(mode="default", returns=[])
    second["events"][0]["atomic_ops"][0]["output"] = "future"
    second["events"][0]["effect_index"] = 1
    raw["transfer_specs"]["ir_filter"]["events"].append(second)
    raw["profiles"]["ir_filter"] = profile(prepared, "ir_filter", operator=["agent_runtime"],
                                             roles=["transformer"], effects=["transform", "transform"])
    with pytest.raises(ValueError, match="undefined local"):
        compile_response(raw, prepared)


def test_acquisition_observation_slices_data_tail_without_duplicating_read():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_read"]["events"][0]
    segment["events"][0]["atomic_ops"].append({
        "op": "select_part", "input": {"kind": "local", "name": "stage_0"},
        "path": ["requested"], "output": "leaf", "evidences": segment["evidences"]})
    raw["transfer_specs"]["ir_read"]["output_bindings"][0]["value"] = {"kind": "local", "name": "leaf"}
    _, compiled, mapping = compile_response(raw, prepared)
    item = compiled["profiles"]["ir_read"]
    assert item["effects"] == ["fs_read", "model_observe", "transform"]
    assert item["operator"] == raw["profiles"]["ir_read"]["operator"]
    assert item["roles"] == raw["profiles"]["ir_read"]["roles"]
    assert [op["op"] for event in compiled["transfer_specs"]["ir_read"]["events"] for op in event["atomic_ops"]] == ["read", "deliver", "select_part"]
    assert any(e["field"] == "effects" and e["value"] == "transform" and e["effect_index"] == 2 for e in item["evidences"])
    assert any(row["kind"] == "slice" and row["raw_atomic_range"] == [1, 2] for row in mapping["events"])


@pytest.mark.parametrize("step", [{"kind": "element", "scope": "forged"}, True, -1])
@pytest.mark.parametrize("operation", ["select_part", "exclude_parts", "update_fields", "build"])
def test_annotation_paths_reject_program_generated_element_scope_and_invalid_indexes(operation, step):
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
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
    schema = build_prompt(prepared).split("\nRESPONSE_JSON_SCHEMA\n")[1].split("\nINPUT_JSON\n")[0]
    assert '"ElementStep"' not in schema
    assert '"scope"' not in schema


def guarded_build_fixture():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    evidence = deepcopy(segment["evidences"])
    segment["events"][0]["atomic_ops"] = [{"op": "build", "container": "object",
        "parts": [{"path": ["optional"], "value": {"kind": "input", "index": 0},
                   "when": {"kind": "literal", "value": False}}],
        "output": "stage_0", "evidences": evidence}]
    return prepared, raw


def test_conditional_member_observation_and_control_use_share_guard():
    prepared, raw = guarded_build_fixture()
    checked, compiled, mapping = compile_response(raw, prepared)
    atoms = [op for event in compiled["transfer_specs"]["ir_filter"]["events"] for op in event["atomic_ops"]]
    observations = [op for op in atoms if op["op"] == "deliver"]
    assert observations[0]["inputs"] == [{"kind": "literal", "value": False}]
    assert "when" not in observations[0]
    assert observations[1]["inputs"] == [{"kind": "input", "index": 0}]
    assert observations[1]["when"] == {"kind": "literal", "value": False}
    assert atoms[-1]["parts"][0]["when"] == observations[1]["when"]
    assert mapping["compiler_version"] == "skillflow-processing-compiler-v4"
    assert compile_response(checked, prepared)[1:] == (compiled, mapping)


def test_conditional_observation_cannot_suppress_later_unconditional_input():
    prepared, raw = guarded_build_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    original = segment["events"][0]["atomic_ops"][0]
    second = deepcopy(original)
    second["output"] = "other"
    second["parts"][0].pop("when")
    segment["events"][0]["atomic_ops"].append(second)
    compiled = compile_response(raw, prepared)[1]
    observations = [op for event in compiled["transfer_specs"]["ir_filter"]["events"]
                    for op in event["atomic_ops"] if op["op"] == "deliver"
                    and op["inputs"] == [{"kind": "input", "index": 0}]]
    assert len(observations) == 2
    assert observations[0]["when"]["value"] is False
    assert "when" not in observations[1]


def test_earlier_unconditional_observation_covers_later_conditional_repeat():
    prepared, raw = guarded_build_fixture()
    segment = raw["transfer_specs"]["ir_filter"]["events"][0]
    conditional = deepcopy(segment["events"][0]["atomic_ops"][0])
    conditional["output"] = "other"
    segment["events"][0]["atomic_ops"][0]["parts"][0].pop("when")
    segment["events"][0]["atomic_ops"].append(conditional)
    compiled = compile_response(raw, prepared)[1]
    observations = [op for event in compiled["transfer_specs"]["ir_filter"]["events"]
                    for op in event["atomic_ops"] if op["op"] == "deliver"
                    and op["inputs"] == [{"kind": "input", "index": 0}]]
    assert len(observations) == 1 and "when" not in observations[0]


def test_raw_guarded_delivery_is_not_a_model_generated_observation():
    prepared, raw = raw_fixture()
    segment = raw["transfer_specs"]["ir_read"]["events"][0]
    read = deepcopy(segment["events"][0]["atomic_ops"][0])
    read.update(op="deliver", inputs=[{"kind": "literal", "value": "payload"}],
                target=read.pop("location"), when={"kind": "literal", "value": True})
    read.pop("output")
    segment["events"][0]["atomic_ops"] = [read]
    with pytest.raises(ValueError):
        compile_response(raw, prepared)


def test_compiler_preserves_unique_partial_request_causal_link():
    prepared, raw = raw_fixture()
    spec = raw["transfer_specs"]["ir_read"]
    spec["order"] = "partial"
    segment = spec["events"][0]
    read = segment["events"][0]["atomic_ops"][0]
    evidence, location = deepcopy(read["evidences"]), read["location"]
    raw["locations"][location]["kind"] = "tool"
    raw["profiles"]["ir_read"] = profile(prepared, "ir_read", operator=["tool"], roles=["source"], effects=[])
    segment["events"] = [{"effect_index": None, "atomic_ops": [
        {"op": "deliver", "inputs": [{"kind": "literal", "value": "request"}], "target": location, "evidences": evidence},
        {"op": "receive", "inputs": [{"kind": "literal", "value": "request"}], "location": location, "output": "stage_0", "evidences": evidence}]}]
    compiled = compile_response(raw, prepared)[1]
    precedence = compiled["transfer_specs"]["ir_read"]["precedence"]
    assert any(item["before"] == {"event_index": 0, "body_event_index": None, "op_index": 0}
               and item["after"] == {"event_index": 0, "body_event_index": None, "op_index": 1}
               for item in precedence)
