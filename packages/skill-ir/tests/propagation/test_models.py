"""Strict compact record structures and deterministic state snapshots."""
import json
import pytest
from pydantic import ValidationError
from skill_ir.propagation.models import (
    AtomicOpRecord, EffectEvent, FlowLocation, FlowState, IRFlowRecord,
    StateBinding, StateChange,
)


def binding(ids=frozenset({"A"})):
    return AtomicOpRecord(op="compute", inputs=[ids]).inputs[0]


def test_location_identity_is_typed_and_empty_state_is_not_unknown():
    result, remote = FlowLocation(kind="result", name="same"), FlowLocation(kind="remote", name="same")
    state = FlowState.from_mapping({result: frozenset({"A"}), remote: frozenset({"B"})})
    assert state.get(result) == frozenset({"A"}) and state.get(remote) == frozenset({"B"})
    assert FlowState().get(result) is None
    with pytest.raises(ValidationError):
        StateBinding(location=result, data_ids=frozenset())
    with pytest.raises(ValidationError):
        result.name = "new"


def test_state_index_cannot_be_changed_through_public_bindings():
    location = FlowLocation(kind="result", name="r")
    supplied = [StateBinding(location=location, data_ids=frozenset({"A"}))]
    state = FlowState(bindings=supplied)
    supplied.clear()
    assert state.get(location) == frozenset({"A"})
    with pytest.raises(AttributeError):
        state.bindings.append(None)
    with pytest.raises(ValidationError):
        FlowState(bindings=[state.bindings[0], state.bindings[0]])


def test_state_serialization_is_deterministic():
    first, second = FlowLocation(kind="result", name="中文"), FlowLocation(kind="storage", name="B")
    left = FlowState.from_mapping({first: frozenset({"B", "A"}), second: frozenset({"Z"})})
    right = FlowState.from_mapping({second: frozenset({"Z"}), first: frozenset({"A", "B"})})
    assert left.model_dump_json() == right.model_dump_json()
    assert FlowState.model_validate_json(left.model_dump_json()) == left
    assert json.loads(left.model_dump_json())["bindings"][0]["data_ids"] == ["A", "B"]


@pytest.mark.parametrize("ids", [[], frozenset(), ["A", "A"], [True], [1], [""], ["  "], "A", {"A"}, ("A",)])
def test_binding_candidate_ids_are_nonempty_strict_and_unique(ids):
    with pytest.raises(ValidationError):
        binding(ids)


@pytest.mark.parametrize("ref", [
    {"kind": "input", "index": True}, {"kind": "input", "index": -1},
    {"kind": "input", "index": 0, "data": "A"}, {"kind": "output", "index": 0},
    {"kind": "local", "name": ""},
])
def test_record_slots_reject_removed_symbolic_reference_wrappers(ref):
    with pytest.raises(ValidationError):
        AtomicOpRecord(op="compute", inputs=[{"ref": ref, "data_ids": ["A"]}])


def test_effect_events_preserve_duplicate_binding_and_operation_positions():
    values = [binding(), binding()]
    operation = AtomicOpRecord(op="compute", inputs=values, outputs=[binding(frozenset({"sum"}))])
    second = AtomicOpRecord(op="compute", inputs=[binding(frozenset({"sum"}))], outputs=[binding(frozenset({"final"}))])
    event = EffectEvent(effect=None, atomic_ops=[operation, second])
    assert len(event.atomic_ops[0].inputs) == 2
    assert EffectEvent.model_validate_json(event.model_dump_json()) == event
    with pytest.raises(ValidationError):
        EffectEvent(effect_index=None, effect="transform", atomic_ops=[])
    with pytest.raises(ValidationError):
        EffectEvent(effect_index=True, effect="transform", atomic_ops=[])
    with pytest.raises(ValidationError):
        AtomicOpRecord(op_index=0, op="compute", inputs=values)
    assert event.atomic_ops[0].outputs == event.atomic_ops[1].inputs
    with pytest.raises(ValidationError):
        AtomicOpRecord(op="compute", notes=["removed"])


def test_changes_allow_missing_binding_but_not_empty_data_identity():
    change = StateChange(location=FlowLocation(kind="runtime_context", name="cache"),
                         before=frozenset(), after=frozenset({"A"}), update="strong")
    assert StateChange.model_validate_json(change.model_dump_json()) == change
    with pytest.raises(ValidationError):
        StateChange(location=change.location, before=[""], after=[], update="delete")


def test_empty_effects_do_not_require_unchanged_state():
    record = IRFlowRecord(order="fixed", precedence=[], entry_state=FlowState(), exit_state=FlowState.from_mapping({
        FlowLocation(kind="result", name="alias"): frozenset({"A"})}), events=[])
    assert record.entry_state != record.exit_state
    with pytest.raises(ValidationError):
        EffectEvent(effect_index=0, effect="transform", inputs=[])
