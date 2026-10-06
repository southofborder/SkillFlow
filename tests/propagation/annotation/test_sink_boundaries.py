"""Boundary grading and sink collection use one explicit structural contract."""
import pytest

from skillflow.propagation.contracts.compatibility import validate_operation_boundary
from skillflow.propagation.contracts.specs import LocationSpec
from skillflow.propagation.contracts.specs import validate_specs
from skillflow.propagation.contracts.boundaries import SinkBoundary
from skillflow.propagation.contracts.boundaries import classify_sink
from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
from skillflow.propagation.contracts.boundaries import exposure_level
from skillflow.propagation.contracts.profiles import AnnotationPayload
from skillflow.propagation.contracts.profiles import RawAnnotationResponse


def location(kind="tool", scope="recipient", retention=None):
    return {"kind": kind, "name": "boundary", "operand_refs": [],
            "access_scope": scope, "retention": retention}


def evidence():
    return [{"basis": "cfg", "ref_id": "C001", "quote": "operation", "reason": "结构验收。"}]


def delivery(target="dst", inputs=None):
    return {"op": "deliver", "inputs": inputs if inputs is not None else [{"kind": "literal", "value": "payload"}],
            "target": target, "evidences": evidence()}


def spec(events):
    return {"order": "fixed", "precedence": [], "events": events, "output_bindings": []}


@pytest.mark.parametrize("scope,retention,level", [
    ("task", None, 0), ("task", "task", 0), ("task", "persistent", 1),
    ("recipient", None, 2), ("recipient", "persistent", 2),
    ("shared", "task", 2), ("public", None, 3), ("public", "persistent", 3),
])
def test_fixed_grade_takes_highest_scope_or_retention(scope, retention, level):
    assert exposure_level(location(scope=scope, retention=retention)) == level


@pytest.mark.parametrize("kind,scope,retention", [
    ("storage", "task", None), ("runtime_context", "task", None),
    ("model_context", "task", None), ("remote", "task", "persistent"), ("user", "task", None),
])
def test_missing_retention_and_internal_receivers_are_rejected(kind, scope, retention):
    with pytest.raises(ValueError):
        LocationSpec.model_validate(location(kind, scope, retention))


@pytest.mark.parametrize("change", [
    lambda value: value.pop("access_scope"), lambda value: value.pop("retention"),
    lambda value: value.update(access_scope="unknown"), lambda value: value.update(retention="none"),
    lambda value: value.update(exposure_level=2),
])
def test_model_location_requires_only_declared_properties(change):
    value = location()
    change(value)
    with pytest.raises(ValueError):
        LocationSpec.model_validate(value)


@pytest.mark.parametrize("operation,effect,kind,scope,retention,mode,expected", [
    ("deliver", None, "tool", "task", None, None, None),
    ("deliver", None, "tool", "recipient", None, None, ("external_tool", 2)),
    ("deliver", "net_send", "remote", "recipient", None, None, ("network_send", 2)),
    ("deliver", "net_send", "remote", "public", None, None, ("network_send", 3)),
    ("deliver", "model_observe", "model_context", "recipient", None, None, ("model_observe", 2)),
    ("deliver", "user_output", "user", "recipient", None, None, ("user_output", 2)),
    ("write", "fs_write", "storage", "task", "persistent", "append", ("storage_write", 1)),
    ("write", "context_write", "runtime_context", "task", "task", "replace", None),
    ("write", "context_write", "runtime_context", "shared", "task", "replace", ("context_save", 2)),
    ("write", "context_write", "runtime_context", "task", "persistent", "replace", ("context_save", 1)),
    ("write", "fs_write", "storage", "public", "persistent", "delete", None),
    ("receive", None, "tool", "recipient", None, None, None),
])
def test_classification_uses_operation_not_role_or_opcode(operation, effect, kind, scope, retention, mode, expected):
    assert classify_sink(operation, effect, location(kind, scope, retention), write_mode=mode) == expected


def test_zero_parameter_delivery_is_only_legal_for_unlabelled_tool():
    validate_operation_boundary("deliver", None, "tool", input_count=0)
    for effect, kind in [("net_send", "remote"), ("model_observe", "model_context"), ("user_output", "user")]:
        with pytest.raises(ValueError, match="empty delivery"):
            validate_operation_boundary("deliver", effect, kind, input_count=0)
    with pytest.raises(ValueError, match="effect-free"):
        validate_operation_boundary("deliver", None, "remote", input_count=1)


def test_repeated_body_observations_retain_actual_scope_and_coordinates():
    locations = {"dst": location("model_context")}
    body = [{"effect_index": index, "atomic_ops": [delivery(inputs=[{"kind": "local", "name": "member"}])]}
            for index in range(2)]
    scopes = [{"kind": "for_each", "collection": {"kind": "literal", "value": []},
               "item": "member", "body": body, "evidences": evidence()}]
    profiles = {"ir_z": {"effects": ["model_observe", "model_observe"], "roles": []},
                "ir_a": {"effects": ["model_observe"], "roles": []}}
    specs = {"ir_z": spec(scopes), "ir_a": spec([{"effect_index": 0, "atomic_ops": [delivery()]}])}
    result = derive_sink_boundaries(locations, specs, profiles)
    assert [(item.instruction_id, item.event_index, item.body_event_index, item.scope) for item in result] == [
        ("ir_a", 0, None, None), ("ir_z", 0, 0, "element"), ("ir_z", 0, 1, "element")]
    assert result == derive_sink_boundaries(locations, dict(reversed(list(specs.items()))), profiles)


def test_direct_compiled_payload_rejects_missing_or_tampered_sink():
    cfg = {"blocks": {"entry": {"instructions": [{"id": "call", "inputs": [], "outputs": []}]}}}
    value = {"profiles": {"call": {"operator": ["tool"], "roles": [], "effects": [], "evidences": []}},
             "locations": {"dst": location()},
             "transfer_specs": {"call": spec([{"effect_index": None, "atomic_ops": [delivery(inputs=[])]}])}}
    with pytest.raises(ValueError):
        AnnotationPayload.model_validate(value)
    value["sink_boundaries"] = [item.model_dump(mode="json") for item in derive_sink_boundaries(
        value["locations"], value["transfer_specs"], value["profiles"])]
    validate_specs(cfg, value)
    value["sink_boundaries"][0]["exposure_level"] = 1
    with pytest.raises(ValueError, match="deterministic"):
        validate_specs(cfg, value)


@pytest.mark.parametrize("change", [
    lambda value: value.update(exposure_level=True), lambda value: value.update(exposure_level=0),
    lambda value: value.update(event_index=True), lambda value: value.update(body_event_index=0),
])
def test_sink_derived_dto_rejects_invalid_coordinates_and_grades(change):
    value = {"instruction_id": "ir", "event_index": 0, "op_index": 0, "target": "dst",
             "sink_type": "external_tool", "exposure_level": 2}
    change(value)
    with pytest.raises(ValueError):
        SinkBoundary.model_validate(value)


def test_raw_model_response_cannot_supply_program_sink_table():
    raw = {"outcome": "completed", "profiles": {}, "locations": {}, "transfer_specs": {},
           "location_evidences": {}, "sink_boundaries": []}
    with pytest.raises(ValueError):
        RawAnnotationResponse.model_validate(raw)
