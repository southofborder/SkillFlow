"""Conditional value uses and request pairing are structural, not semantic guesses."""
from copy import deepcopy

import pytest
from pydantic import TypeAdapter

from skill_ir.propagation.specs import (AtomicOp, BuildOp, IRTransferSpec, RawAtomicOp,
                                       value_refs, precedence_edges, validate_precedence)
from skill_ir.propagation.uses import value_uses, request_pairs, active_value_uses


EVIDENCE = [{"basis": "source", "ref_id": "s1", "quote": "call", "reason": "真实关系的结构示例。"}]
TERM = {"kind": "input", "index": 0}
FLAG = {"kind": "input", "index": 1}
LOCAL = {"kind": "local", "name": "request"}


def atom(kind, **values):
    return {"op": kind, "evidences": EVIDENCE, **values}


def spec(operations, *, order="fixed", precedence=None):
    return IRTransferSpec.model_validate({"order": order, "precedence": precedence or [],
        "events": [{"effect_index": None, "atomic_ops": operations}], "output_bindings": []})


def test_build_uses_preserve_field_and_guard_position_without_changing_updates():
    build = BuildOp.model_validate(atom("build", container="object", output="request", parts=[
        {"path": ["q"], "value": TERM}, {"path": ["optional"], "value": TERM, "when": FLAG}]))
    uses = value_uses(build)
    assert [(use.value.model_dump(), use.role, use.member_index) for use in uses] == [
        (TERM, "value", 0), (FLAG, "control", 1), (TERM, "value", 1)]
    assert uses[-1].when.model_dump() == FLAG
    assert [ref.model_dump() for ref in value_refs(build)] == [TERM, FLAG, TERM]
    with pytest.raises(ValueError):
        TypeAdapter(AtomicOp).validate_python(atom("update_fields", input=TERM, output="updated",
            updates=[{"path": ["q"], "value": TERM, "when": FLAG}]))


@pytest.mark.parametrize("value", [None, "false", 0, [], {}])
def test_condition_is_not_python_truthiness(value):
    with pytest.raises(ValueError, match="Boolean"):
        BuildOp.model_validate(atom("build", container="object", output="request",
            parts=[{"path": ["q"], "value": TERM, "when": {"kind": "literal", "value": value}}]))


def test_conditional_list_build_is_not_implicit_compaction():
    with pytest.raises(ValueError, match="object container"):
        BuildOp.model_validate(atom("build", container="list", output="request",
            parts=[{"path": [0], "value": TERM, "when": FLAG}]))


def test_definitely_false_value_use_is_inactive_but_guard_remains():
    build = BuildOp.model_validate(atom("build", container="object", output="request", parts=[
        {"path": ["optional"], "value": TERM, "when": {"kind": "literal", "value": False}}]))
    assert [use.role for use in active_value_uses(build)] == ["control"]
    build = BuildOp.model_validate(atom("build", container="object", output="request", parts=[
        {"path": ["optional"], "value": TERM, "when": FLAG}]))
    instruction = {"inputs": [{"type": "result", "identifier": "data"},
                               {"type": "literal", "literal_value": False}]}
    assert [use.role for use in active_value_uses(build, instruction)] == ["control"]
    instruction["inputs"][1]["literal_value"] = True
    assert [use.role for use in active_value_uses(build, instruction)] == ["control", "value"]


def test_false_guard_is_not_a_truthiness_conversion():
    build = BuildOp.model_validate(atom("build", container="object", output="request", parts=[
        {"path": ["optional"], "value": TERM, "when": FLAG}]))
    with pytest.raises(ValueError, match="Boolean"):
        active_value_uses(build, {"inputs": [{"type": "result", "identifier": "data"},
                                            {"type": "literal", "literal_value": "false"}]})


def test_raw_schema_does_not_accept_compiler_guarded_deliver():
    deliver = atom("deliver", target="model", inputs=[TERM], when=FLAG)
    TypeAdapter(AtomicOp).validate_python(deliver)
    with pytest.raises(ValueError):
        TypeAdapter(RawAtomicOp).validate_python(deliver)
    raw_schema = TypeAdapter(RawAtomicOp).json_schema()
    assert "when" not in raw_schema["$defs"]["RawDeliverOp"]["properties"]


def test_serial_requests_consume_once_preserve_parameter_order_and_repeats():
    request = [TERM, TERM, FLAG]
    operations = [atom("deliver", target="tool", inputs=request),
                  atom("receive", location="tool", inputs=request, output="r1"),
                  atom("deliver", target="tool", inputs=request),
                  atom("receive", location="tool", inputs=request, output="r2")]
    assert request_pairs(spec(operations)) == {(0, None, 1): (0, None, 0), (0, None, 3): (0, None, 2)}
    operations[1]["inputs"] = [TERM, FLAG, TERM]
    with pytest.raises(ValueError, match="match"):
        request_pairs(spec(operations))


def test_multiple_equivalent_unconsumed_requests_are_not_fifo():
    with pytest.raises(ValueError, match="ambiguous"):
        request_pairs(spec([atom("deliver", target="tool", inputs=[TERM]),
            atom("deliver", target="tool", inputs=[TERM]),
            atom("receive", location="tool", inputs=[TERM], output="response")]))


def test_partial_unique_pair_adds_request_cause_and_rejects_response_before_request():
    typed = IRTransferSpec.model_validate({"order": "partial", "precedence": [],
        "events": [{"effect_index": None, "atomic_ops": [atom("deliver", target="tool", inputs=[TERM])]},
                   {"effect_index": None, "atomic_ops": [atom("receive", location="tool", inputs=[TERM], output="response")]}],
        "output_bindings": []})
    assert request_pairs(typed) == {(1, None, 0): (0, None, 0)}
    assert ((0, None, 0), (1, None, 0)) in precedence_edges(typed)
    validate_precedence(typed)
    raw = typed.model_dump(mode="json")
    raw["precedence"] = [{"before": {"event_index": 1, "op_index": 0}, "after": {"event_index": 0, "op_index": 0}}]
    with pytest.raises(ValueError):
        request_pairs(IRTransferSpec.model_validate(raw))


def test_partial_repeated_requests_without_unique_order_are_rejected():
    typed = IRTransferSpec.model_validate({"order": "partial", "precedence": [],
        "events": [{"effect_index": None, "atomic_ops": [op]} for op in [
            atom("deliver", target="tool", inputs=[TERM]), atom("deliver", target="tool", inputs=[TERM]),
            atom("receive", location="tool", inputs=[TERM], output="a"), atom("receive", location="tool", inputs=[TERM], output="b")]],
        "output_bindings": []})
    with pytest.raises(ValueError, match="ambiguous"):
        request_pairs(typed)


def test_raw_partial_segment_keeps_serial_request_order_before_compilation():
    from skill_ir.propagation.specs import RawIRTransferSpec, flatten_raw_spec
    operations = [atom("deliver", target="tool", inputs=[TERM]),
                  atom("receive", location="tool", inputs=[TERM], output="one"),
                  atom("deliver", target="tool", inputs=[TERM]),
                  atom("receive", location="tool", inputs=[TERM], output="two")]
    raw = RawIRTransferSpec.model_validate({"order": "partial", "events": [{
        "kind": "processing", "mode": "default", "evidences": EVIDENCE,
        "events": [{"effect_index": None, "atomic_ops": [operation]} for operation in operations]}],
        "output_bindings": []})
    assert request_pairs(flatten_raw_spec(raw)) == {(1, None, 0): (0, None, 0), (3, None, 0): (2, None, 0)}


def test_zero_argument_and_unsolicited_acquisition_are_distinct_legal_cases():
    assert request_pairs(spec([atom("receive", location="tool", inputs=[], output="incoming")])) == {}
    assert request_pairs(spec([atom("deliver", target="tool", inputs=[]),
        atom("receive", location="tool", inputs=[], output="incoming")])) == {(0, None, 1): (0, None, 0)}


@pytest.mark.parametrize("order", ["fixed", "partial"])
def test_zero_argument_request_cannot_be_consumed_twice(order):
    typed = IRTransferSpec.model_validate({"order": order, "precedence": [
        {"before": {"event_index": 0, "op_index": 0}, "after": {"event_index": 1, "op_index": 0}},
        {"before": {"event_index": 1, "op_index": 0}, "after": {"event_index": 2, "op_index": 0}}],
        "events": [{"effect_index": None, "atomic_ops": [operation]} for operation in [
            atom("deliver", target="tool", inputs=[]),
            atom("receive", location="tool", inputs=[], output="one"),
            atom("receive", location="tool", inputs=[], output="two")]],
        "output_bindings": []})
    with pytest.raises(ValueError, match="match|missing|ambiguous"):
        request_pairs(typed)


def test_unpaired_acquisition_dependency_is_not_an_invented_request():
    assert request_pairs(spec([atom("receive", location="tool", inputs=[TERM], output="incoming")])) == {}
    assert request_pairs(spec([atom("deliver", target="other", inputs=[TERM]),
        atom("receive", location="tool", inputs=[TERM], output="incoming")])) == {}


def test_declared_request_mismatch_is_rejected():
    with pytest.raises(ValueError):
        request_pairs(spec([atom("deliver", target="tool", inputs=[FLAG]),
            atom("receive", location="tool", inputs=[TERM], output="incoming")]))
