"""Joint v5 symbolic specification checks, without semantic guessing or API."""

from copy import deepcopy
import json

import pytest

from skill_ir.propagation.specs import IRTransferSpec, LiteralRef, validate_specs
from skill_ir.security_profile.models import AnnotationPayload, AnnotationResponse
from skill_ir.security_profile.prompts import build_prompt
from skill_ir.security_profile.services import to_payload, validate_compiled_response
from security_profile.helpers import material, profile, valid_response, with_specs


def fixture():
    prepared = material()
    return prepared, valid_response(prepared)


def operation(response, ir="ir_filter", event=0):
    return response["transfer_specs"][ir]["events"][event]["atomic_ops"][0]


def evidence(response):
    return deepcopy(operation(response)["evidences"])


@pytest.mark.parametrize("field", ["locations", "transfer_specs", "location_evidences"])
def test_new_fields_are_required_without_legacy_autofill(field):
    prepared, response = fixture()
    response.pop(field)
    with pytest.raises(ValueError, match=field):
        validate_compiled_response(response, prepared)


def test_joint_schema_is_sent_separately_from_unchanged_full_input():
    prepared, response = fixture()
    prompt = build_prompt(prepared)
    schema = json.loads(prompt.split("\nRESPONSE_JSON_SCHEMA\n")[1].split("\nINPUT_JSON\n")[0])
    assert set(schema["$defs"]["RawAnnotationResponse"]["required"]) == {"profiles", "locations", "transfer_specs", "outcome", "location_evidences"}
    assert json.loads(prompt.split("\nINPUT_JSON\n")[1]) == prepared
    assert validate_compiled_response(json.dumps(response, ensure_ascii=False), prepared) == response
    validate_specs(prepared["cfg"], to_payload(response))


@pytest.mark.parametrize("mutate", [
    lambda r: r["transfer_specs"].pop("ir_return"),
    lambda r: r["transfer_specs"].update(absent=r["transfer_specs"]["ir_filter"]),
    lambda r: r["transfer_specs"]["ir_filter"]["output_bindings"].clear(),
    lambda r: r["transfer_specs"]["ir_filter"]["output_bindings"].append(deepcopy(r["transfer_specs"]["ir_filter"]["output_bindings"][0])),
    lambda r: r["transfer_specs"]["ir_filter"]["output_bindings"][0].update(output_index=True),
    lambda r: operation(r).update(inputs=[{"kind": "input", "index": 999}]),
    lambda r: operation(r).update(inputs=[{"kind": "local", "name": "missing"}]),
    lambda r: operation(r).update(data_ids=["forbidden-propagated-id"]),
    lambda r: operation(r)["evidences"][0].update(quote="not the cited text"),
    lambda r: r["locations"]["ir_read_boundary_0"]["operand_refs"][0].update(index=True),
    lambda r: r["locations"]["ir_read_boundary_0"]["operand_refs"][0].update(instruction_id="absent"),
    lambda r: r["locations"]["ir_read_boundary_0"].update(anchors=[{"kind": "source", "location": "absent"}]),
    lambda r: r["locations"]["ir_read_boundary_0"].update(kind="remote"),
    lambda r: operation(r, "ir_read").update(location="missing"),
])
def test_scope_coverage_locations_and_quotes_are_checked(mutate):
    prepared, response = fixture()
    mutate(response)
    with pytest.raises(ValueError):
        validate_compiled_response(response, prepared)


def test_duplicate_location_identity_rejected_even_with_different_ids():
    prepared, response = fixture()
    response["locations"]["duplicate"] = deepcopy(response["locations"]["ir_read_boundary_0"])
    response["location_evidences"]["duplicate"] = deepcopy(response["location_evidences"]["ir_read_boundary_0"])
    with pytest.raises(ValueError, match="duplicate location"):
        validate_compiled_response(response, prepared)


def test_empty_effects_bind_an_unchanged_result_without_events():
    prepared, response = fixture()
    response["profiles"]["ir_filter"] = profile(prepared, "ir_filter")
    with_specs(prepared, response)
    parsed = validate_compiled_response(response, prepared)
    spec = parsed["transfer_specs"]["ir_filter"]
    assert spec["events"] == []
    assert spec["output_bindings"][0]["value"] == {"kind": "input", "index": 0}


def test_null_event_is_conservative_compute_not_a_hidden_side_effect():
    prepared, response = fixture()
    response["profiles"]["ir_filter"] = profile(prepared, "ir_filter")
    with_specs(prepared, response)
    spec = response["transfer_specs"]["ir_filter"]
    quotes = spec["output_bindings"][0]["evidences"]
    spec["events"] = [{"effect_index": None, "atomic_ops": [{
        "op": "compute", "inputs": [], "dependencies": [], "output": "new", "evidences": quotes,
    }]}]
    spec["output_bindings"][0]["value"] = {"kind": "local", "name": "new"}
    assert validate_compiled_response(response, prepared) == response
    operation(response)["inputs"] = [{"kind": "input", "index": 0}]
    operation(response)["dependencies"] = ["derived"]
    with pytest.raises(ValueError, match="effect-free"):
        validate_compiled_response(response, prepared)
    operation(response).update(op="read", location="ir_read_boundary_0")
    operation(response).pop("inputs")
    operation(response).pop("dependencies")
    with pytest.raises(ValueError, match="effect-free"):
        validate_compiled_response(response, prepared)


def test_primary_effect_operation_cannot_be_replaced_by_a_computation():
    prepared, response = fixture()
    response["transfer_specs"]["ir_read"]["events"][0]["atomic_ops"] = [deepcopy(operation(response))]
    with pytest.raises(ValueError, match="primary operation"):
        validate_compiled_response(response, prepared)


@pytest.mark.parametrize("mutation", [
    lambda spec: spec["events"][0].update(effect_index=True),
    lambda spec: spec["events"][0].update(effect_index=7),
    lambda spec: spec["events"].append(deepcopy(spec["events"][0])),
])
def test_effect_positions_are_exact_and_not_a_second_sequence(mutation):
    prepared, response = fixture()
    mutation(response["transfer_specs"]["ir_filter"])
    with pytest.raises(ValueError):
        validate_compiled_response(response, prepared)


def test_unknown_order_forward_candidate_preserves_original_and_rejects_cycles():
    prepared, response = fixture()
    response["profiles"]["ir_filter"] = profile(prepared, "ir_filter", effects=["model_observe", "transform"])
    with_specs(prepared, response)
    spec = response["transfer_specs"]["ir_filter"]
    future = {"kind": "local", "name": "stage_1"}
    original = {"kind": "input", "index": 0}
    spec["events"][0]["atomic_ops"][0]["inputs"] = [{"kind": "alternatives", "items": [original, future]}]
    with pytest.raises(ValueError, match="precedes definition"):
        validate_compiled_response(response, prepared)
    spec["order"] = "partial"
    assert validate_compiled_response(response, prepared) == response
    spec["events"][0]["atomic_ops"][0]["inputs"][0]["items"] = [future]
    with pytest.raises(ValueError, match="already available"):
        validate_compiled_response(response, prepared)
    spec["events"][0]["atomic_ops"][0]["inputs"][0]["items"] = [original, future]
    spec["events"][1]["atomic_ops"][0]["inputs"] = [{"kind": "alternatives", "items": [original, future]}]
    with pytest.raises(ValueError, match="cyclic"):
        validate_compiled_response(response, prepared)


@pytest.mark.parametrize("kind", ["select_part", "exclude_parts", "update_fields", "build"])
def test_explicit_typed_data_operations_preserve_symbolic_structure(kind):
    prepared, response = fixture()
    base = {"kind": "input", "index": 0}
    value = {"kind": "literal", "value": {"中文": [None, 1, False]}}
    extra = {
        "select_part": {"input": base, "path": ["records", 0]},
        "exclude_parts": {"input": base, "paths": [["api_key"], ["records", 0]]},
        "update_fields": {"input": base, "updates": [{"path": ["meta"], "value": value}]},
        "build": {"parts": [{"path": ["meta"], "value": value, "when": None}], "container": "object"},
    }[kind]
    response["transfer_specs"]["ir_filter"]["events"][0]["atomic_ops"] = [
        {"op": kind, "output": "stage_0", "evidences": evidence(response), **extra}]
    assert validate_compiled_response(response, prepared) == response


@pytest.mark.parametrize("path", [[True], [-1], [], [1.5]])
def test_invalid_path_segments_cannot_be_coerced(path):
    prepared, response = fixture()
    operation(response).clear()
    operation(response).update(op="select_part", input={"kind": "input", "index": 0}, path=path,
                               output="stage_0", evidences=[{"basis": "cfg", "ref_id": prepared["instruction_index"]["ir_filter"]["ref_id"],
                                                            "quote": "select_fields_locally", "reason": "测试"}])
    with pytest.raises(ValueError):
        validate_compiled_response(response, prepared)


def test_delete_context_binding_has_no_input_and_cannot_hide_a_read():
    prepared, response = fixture()
    response["profiles"]["ir_filter"] = profile(prepared, "ir_filter", effects=["context_write"])
    with_specs(prepared, response)
    op = operation(response)
    op.update(mode="delete", input=None)
    assert validate_compiled_response(response, prepared) == response
    op["input"] = {"kind": "input", "index": 0}
    with pytest.raises(ValueError, match="must not read"):
        validate_compiled_response(response, prepared)


def test_json_literal_types_are_not_coerced():
    for value in (None, {}, [], "0", 0, False):
        model = LiteralRef(kind="literal", value=value)
        assert type(model.value) is type(value)
    with pytest.raises(ValueError):
        LiteralRef(kind="literal", value={1, 2})


def test_external_resource_operand_is_a_boundary_not_a_value_reference():
    prepared, response = fixture()
    response["transfer_specs"]["ir_read"]["output_bindings"][0]["value"] = {"kind": "input", "index": 0}
    with pytest.raises(ValueError, match="resource identity"):
        validate_compiled_response(response, prepared)
    response["transfer_specs"]["ir_read"]["output_bindings"][0]["value"] = {"kind": "literal", "value": "config.json"}
    assert validate_compiled_response(response, prepared) == response


@pytest.mark.parametrize("container,paths", [
    ("list", [[2]]),
    ("list", [[0], [2]]),
    ("object", [["nested", 1]]),
    ("object", [["nested", "field"], ["nested", 0]]),
])
def test_complete_build_rejects_sparse_or_incompatible_container_paths(container, paths):
    prepared, response = fixture()
    quotes = evidence(response)
    op = operation(response)
    op.clear()
    op.update(op="build", container=container, parts=[
        {"path": path, "value": {"kind": "literal", "value": "value"}} for path in paths
    ], output="stage_0", evidences=quotes)
    with pytest.raises(ValueError, match="construction"):
        validate_compiled_response(response, prepared)


def test_complete_build_preserves_dense_nested_lists():
    prepared, response = fixture()
    quotes = evidence(response)
    op = operation(response)
    op.clear()
    op.update(op="build", container="object", parts=[
        {"path": ["nested", index, "value"], "value": {"kind": "literal", "value": index}, "when": None}
        for index in (0, 1)
    ], output="stage_0", evidences=quotes)
    assert validate_compiled_response(response, prepared) == response


def test_location_declaration_is_five_fields_and_can_have_no_public_operand():
    prepared, response = fixture()
    location = response["locations"]["ir_read_boundary_0"]
    assert set(location) == {"kind", "name", "operand_refs", "access_scope", "retention"}
    location["operand_refs"] = []
    assert validate_compiled_response(response, prepared) == response
    assert set(prepared["instruction_index"]["ir_read"]) == {"block_id", "position", "ref_id"}


@pytest.mark.parametrize("extra,value", [
    ("key", "old"), ("anchors", []), ("evidences", []),
])
def test_legacy_location_structure_is_rejected(extra, value):
    prepared, response = fixture()
    response["locations"]["ir_read_boundary_0"][extra] = value
    with pytest.raises(ValueError):
        validate_compiled_response(response, prepared)


def test_operand_refs_are_actual_unique_three_field_references():
    prepared, response = fixture()
    refs = response["locations"]["ir_read_boundary_0"]["operand_refs"]
    assert set(refs[0]) == {"instruction_id", "side", "index"}
    refs.append(deepcopy(refs[0]))
    with pytest.raises(ValueError, match="duplicate location operand"):
        validate_compiled_response(response, prepared)
    refs.pop()
    refs[0]["kind"] = "operand"
    with pytest.raises(ValueError):
        validate_compiled_response(response, prepared)


@pytest.mark.parametrize("mutation", [
    lambda r: r["location_evidences"].clear(),
    lambda r: r["location_evidences"].update(extra=deepcopy(r["location_evidences"]["ir_read_boundary_0"])),
    lambda r: r["location_evidences"].update(ir_read_boundary_0=[]),
    lambda r: r["location_evidences"]["ir_read_boundary_0"][0].update(ref_id="g_missing"),
    lambda r: r["location_evidences"]["ir_read_boundary_0"][0].update(quote="not a real quote"),
    lambda r: r["location_evidences"]["ir_read_boundary_0"][0].update(location="g_0001"),
])
def test_independent_location_evidence_has_exact_coverage_and_real_quotes(mutation):
    prepared, response = fixture()
    mutation(response)
    with pytest.raises(ValueError):
        validate_compiled_response(response, prepared)


def test_explicit_projection_keeps_four_business_fields_for_dict_and_model():
    prepared, response = fixture()
    validated = validate_compiled_response(response, prepared)
    payload = to_payload(validated)
    assert set(payload) == {"profiles", "locations", "transfer_specs", "sink_boundaries"}
    assert to_payload(AnnotationResponse.model_validate(validated)) == payload
    assert AnnotationPayload.model_validate(payload).model_dump(mode="json") == payload
    with pytest.raises(ValueError, match="location_evidences"):
        AnnotationPayload.model_validate(validated)
    with pytest.raises(ValueError, match="location_evidences"):
        to_payload(payload)
    payload["locations"]["ir_read_boundary_0"]["operand_refs"].clear()
    assert validated["locations"]["ir_read_boundary_0"]["operand_refs"]


def test_full_response_requires_an_explicit_empty_location_evidence_table():
    prepared, response = fixture()
    for ir_id in response["profiles"]:
        response["profiles"][ir_id] = profile(prepared, ir_id)
    with_specs(prepared, response)
    assert response["locations"] == response["location_evidences"] == {}
    assert validate_compiled_response(response, prepared) == response
    response.pop("location_evidences")
    with pytest.raises(ValueError, match="location_evidences"):
        validate_compiled_response(response, prepared)
