"""Conditional construction, effect payload and exact request-version regressions."""
from copy import deepcopy

import pytest
from pydantic import TypeAdapter

from skillflow.propagation.data import DataRegistry
from skillflow.propagation.data import LiteralContent
from skillflow.propagation.data import KnownPartsContent
from skillflow.propagation.data import Origin
from skillflow.propagation.conditions import guard_truths
from skillflow.propagation.conditions import payload_inputs
from skillflow.propagation.conditions import payload_input_indices
from skillflow.propagation.conditions import validate_record_consumption
from skillflow.propagation.conditions import record_consumption_shape
from skillflow.propagation.interpreter import TransferInterpreter
from skillflow.propagation.interpreter import PendingValue
from skillflow.propagation.interpreter import PropagationLimitError
from skillflow.propagation.models import AtomicOpRecord
from skillflow.propagation.models import FlowState
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.contracts.specs import AtomicOp
from skillflow.propagation.contracts.specs import IRTransferSpec


EVIDENCE = [{"basis": "cfg", "ref_id": "g_1", "quote": "action", "reason": "测试定位"}]


def literal(value):
    return {"kind": "literal", "value": value}


def local(name):
    return {"kind": "local", "name": name}


def operation(kind, **fields):
    return {"op": kind, "evidences": deepcopy(EVIDENCE), **fields}


def harness(events, outputs=None, *, order="fixed", precedence=None, inputs=None, state=None):
    registry = DataRegistry("conditional-fixture")
    ir = {"id": "ir_action", "inputs": inputs or [], "outputs": [
        {"type": "result", "identifier": "result"}
    ] if outputs is not None else []}
    spec = IRTransferSpec.model_validate({"order": order, "precedence": precedence or [],
        "events": [{"effect_index": index, "atomic_ops": ops} for index, ops in enumerate(events)],
        "output_bindings": [{"output_index": 0, "value": outputs, "evidences": EVIDENCE}] if outputs is not None else []})
    annotation = {"locations": {
        "model": {"kind": "model_context", "name": "model", "operand_refs": [], "access_scope": "recipient", "retention": None},
        "tool": {"kind": "tool", "name": "lookup", "operand_refs": [], "access_scope": "recipient", "retention": None}},
        "profiles": {ir["id"]: {"effects": ["transform"] * len(events)}}}
    interpreter = TransferInterpreter({"blocks": {"b": {"instructions": [ir]}}}, annotation, registry)
    return registry, interpreter, ir, spec, state or FlowState()


def build(parts, **kwargs):
    return operation("build", parts=parts, container="object", output="request", **kwargs)


def evaluated(parts):
    registry, interpreter, ir, spec, state = harness([[build(parts)]], local("request"))
    record = interpreter.evaluate(ir, spec, state)
    return registry, interpreter, ir, spec, state, record


def output_data(registry, record):
    return [registry.get(data_id) for data_id in record.events[0].atomic_ops[0].outputs[0]]


def test_false_member_does_not_resolve_absent_value_and_is_not_null():
    registry, _, _, _, _, record = evaluated([
        {"path": ["optional"], "value": local("not_available"), "when": literal(False)}])
    op = record.events[0].atomic_ops[0]
    assert len(op.inputs) == 1 and op.members[0].value_input_index is None
    assert op.members[0].when_input_index == 0
    assert output_data(registry, record)[0].content == LiteralContent(value={})
    validate_record_consumption(op, registry)


def test_true_member_retains_literal_original_and_parameter_order():
    registry, _, _, _, _, record = evaluated([
        {"path": ["required"], "value": literal("same")},
        {"path": ["optional"], "value": literal("same"), "when": literal(True)}])
    op = record.events[0].atomic_ops[0]
    assert [(row.value_input_index, row.when_input_index) for row in op.members] == [(0, None), (2, 1)]
    result = output_data(registry, record)[0]
    assert isinstance(result.content, KnownPartsContent)
    assert registry.resolve_part(result.id, ["required"]).content.value == "same"
    assert registry.resolve_part(result.id, ["optional"]).content.value == "same"
    assert len(result.origin.inputs) == 3
    validate_record_consumption(op, registry)


def test_true_missing_member_is_pending_instead_of_false_only_success():
    with pytest.raises(PendingValue):
        evaluated([{"path": ["optional"], "value": local("missing"), "when": literal(True)}])


@pytest.mark.parametrize("value", [None, 0, 1, "", "false", [], {}])
def test_condition_does_not_apply_language_truthiness(value):
    with pytest.raises(ValueError, match="Boolean"):
        evaluated([{"path": ["optional"], "value": literal("x"), "when": literal(value)}])


def test_shared_abstract_guard_has_two_correlated_shapes_and_stable_ids():
    guard = {"kind": "input", "index": 0}
    parts = [{"path": [name], "value": literal(name), "when": guard} for name in ("a", "b")]
    registry, interpreter, ir, spec, _ = harness([[build(parts)]], local("request"),
        inputs=[{"type": "result", "identifier": "guard"}])
    unknown = registry.register_source("opaque-bool", acquired_from="runtime:flag")
    state = FlowState.from_mapping({FlowLocation(kind="result", name="guard"): frozenset([unknown.id])})
    record = interpreter.evaluate(ir, spec, state)
    results = output_data(registry, record)
    shapes = sorted(tuple(part.path[0] for part in data.content.parts) if isinstance(data.content, KnownPartsContent) else () for data in results)
    assert shapes == [(), ("a", "b")]
    before = len(registry)
    assert interpreter.evaluate(ir, spec, state).model_dump(mode="json") == record.model_dump(mode="json")
    assert len(registry) == before
    op = record.events[0].atomic_ops[0]
    assert [row.when_input_index for row in op.members] == [0, 2]
    assert op.inputs[0] == op.inputs[2] == frozenset([unknown.id])
    validate_record_consumption(op, registry)


def test_abstract_guard_missing_value_does_not_fall_back_to_omission():
    registry, interpreter, ir, spec, _ = harness([[build([
        {"path": ["a"], "value": local("missing"), "when": {"kind": "input", "index": 0}}])]],
        local("request"), inputs=[{"type": "result", "identifier": "guard"}])
    guard = registry.register_source("guard", acquired_from="runtime:flag")
    state = FlowState.from_mapping({FlowLocation(kind="result", name="guard"): frozenset([guard.id])})
    with pytest.raises(PendingValue):
        interpreter.evaluate(ir, spec, state)


def test_false_observation_resolves_control_only_not_payload():
    registry, interpreter, ir, spec, state = harness([[operation("deliver", inputs=[local("missing")], target="model", when=literal(False))]])
    record = interpreter.evaluate(ir, spec, state)
    op = record.events[0].atomic_ops[0]
    assert op.when_input_index == 0 and len(op.inputs) == 1
    assert payload_inputs(op) == [] and payload_input_indices(op) == ()
    assert op.model_dump(mode="json")["when_input_index"] == 0
    assert "members" not in op.model_dump(mode="json")
    validate_record_consumption(op, registry)


def test_true_observation_keeps_control_separate_from_payload():
    registry, interpreter, ir, spec, state = harness([[operation("deliver", inputs=[literal("payload")], target="model", when=literal(True))]])
    op = interpreter.evaluate(ir, spec, state).events[0].atomic_ops[0]
    assert op.when_input_index == 1 and payload_input_indices(op) == (0,)
    assert registry.get(next(iter(payload_inputs(op)[0]))).content.value == "payload"
    validate_record_consumption(op, registry)


def test_receive_uses_delivered_literal_identity_not_receive_site_literal():
    registry, interpreter, ir, spec, state = harness([
        [operation("deliver", inputs=[literal("query")], target="tool")],
        [operation("receive", inputs=[literal("query")], location="tool", output="response")]], local("response"))
    record = interpreter.evaluate(ir, spec, state)
    delivered, received = [event.atomic_ops[0] for event in record.events]
    assert received.inputs == delivered.inputs
    response = registry.get(next(iter(received.outputs[0])))
    assert response.origin.inputs == [next(iter(delivered.inputs[0]))]
    assert response.origin.acquired_from == "tool:lookup"


@pytest.mark.parametrize("change", ["value_index", "guard_index", "missing_member", "wrong_op"])
def test_record_consumption_corruption_is_rejected(change):
    registry, _, _, _, _, record = evaluated([
        {"path": ["a"], "value": literal("x"), "when": literal(True)}])
    op = record.events[0].atomic_ops[0].model_dump(mode="json")
    if change == "value_index":
        op["members"][0]["value_input_index"] = 0
    elif change == "guard_index":
        op["members"][0]["when_input_index"] = True
    elif change == "missing_member":
        op["members"] = []
    else:
        op["op"] = "compute"
    with pytest.raises(ValueError):
        candidate = AtomicOpRecord.model_validate(op)
        validate_record_consumption(candidate, registry)


def test_plain_operation_has_no_consumption_wrappers_and_shape_keeps_arity():
    op = AtomicOpRecord(op="compute", inputs=[frozenset(["a"]), frozenset(["a"])])
    assert "members" not in op.model_dump(mode="json")
    assert "when_input_index" not in op.model_dump(mode="json")
    assert record_consumption_shape(op) == ("compute", 2)


def test_conditional_constructor_rejects_list_positions():
    with pytest.raises(ValueError):
        TypeAdapter(AtomicOp).validate_python(operation("build", container="list", output="list",
            parts=[{"path": [0], "value": literal("x"), "when": literal(True)}]))


def test_false_context_member_is_not_preseeded_as_a_new_source():
    registry, interpreter, ir, spec, _ = harness([[build([
        {"path": ["a"], "value": {"kind": "input", "index": 0}, "when": literal(False)}])]],
        local("request"), inputs=[{"type": "context_key", "identifier": "unused_context"}])
    interpreter.annotation["transfer_specs"] = {ir["id"]: spec.model_dump(mode="json")}
    assert interpreter.initial_locations() == set()
    assert len(registry) == 0


def test_same_boolean_data_selected_through_distinct_guard_refs_is_correlated():
    parts = [{"path": ["a"], "value": literal("a"), "when": {"kind": "input", "index": 0}},
             {"path": ["b"], "value": literal("b"), "when": {"kind": "input", "index": 1}}]
    registry, interpreter, ir, spec, _ = harness([[build(parts)]], local("request"), inputs=[
        {"type": "result", "identifier": "left"}, {"type": "result", "identifier": "right"}])
    flag = registry.register_source("flag", acquired_from="flag")
    state = FlowState.from_mapping({FlowLocation(kind="result", name=name): frozenset([flag.id])
                                    for name in ("left", "right")})
    record = interpreter.evaluate(ir, spec, state)
    assert len(record.events[0].atomic_ops[0].outputs[0]) == 2


def test_repeated_alternatives_condition_shares_choice_and_actual_guard_ids():
    condition = {"kind": "alternatives", "items": [literal(True), literal(False)]}
    registry, _, _, _, _, record = evaluated([
        {"path": ["a"], "value": literal("a"), "when": condition},
        {"path": ["b"], "value": literal("b"), "when": condition}])
    op = record.events[0].atomic_ops[0]
    assert op.inputs[0] == op.inputs[2]
    shapes = sorted(tuple(part.path[0] for part in data.content.parts) if isinstance(data.content, KnownPartsContent) else ()
                    for data in output_data(registry, record))
    assert shapes == [(), ("a", "b")]


def test_conditional_candidate_overflow_is_explicit_not_truncated():
    refs = [{"kind": "input", "index": i} for i in range(3)]
    registry, interpreter, ir, spec, _ = harness([[build([
        {"path": [str(i)], "value": literal(i), "when": ref} for i, ref in enumerate(refs)])]],
        local("request"), inputs=[{"type": "result", "identifier": str(i)} for i in range(3)])
    flags = [registry.register_source(str(i), acquired_from=str(i)).id for i in range(3)]
    state = FlowState.from_mapping({FlowLocation(kind="result", name=str(i)): frozenset([data_id])
                                    for i, data_id in enumerate(flags)})
    interpreter.max_variants = 4
    with pytest.raises(PropagationLimitError):
        interpreter.evaluate(ir, spec, state)


def test_partial_request_order_uses_same_delivered_data_in_all_arrangements():
    registry, interpreter, ir, spec, state = harness([
        [operation("deliver", inputs=[literal("query")], target="tool")],
        [operation("receive", inputs=[literal("query")], location="tool", output="response")]],
        local("response"), order="partial")
    record = interpreter.evaluate(ir, spec, state)
    assert record.events[0].atomic_ops[0].inputs == record.events[1].atomic_ops[0].inputs


def test_partial_guard_records_merge_without_relabeling_control_as_payload():
    registry, interpreter, ir, spec, state = harness([
        [operation("compute", inputs=[], dependencies=[], output="other")],
        [operation("deliver", inputs=[literal("payload")], target="model", when=literal(True))]],
        order="partial")
    record = interpreter.evaluate(ir, spec, state)
    guarded = record.events[1].atomic_ops[0]
    assert guarded.when_input_index == 1 and len(payload_inputs(guarded)) == 1
    validate_record_consumption(guarded, registry)
