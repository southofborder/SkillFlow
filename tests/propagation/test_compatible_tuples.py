"""Candidate budgets apply after relational compatibility, not before it."""
from itertools import product

import pytest

from skillflow.propagation.interpreter import (
    PropagationLimitError, TransferInterpreter, UnsupportedLoopDomain,
)


class Bindings:
    def __init__(self, values):
        self.values = values
        self.reads = []

    def bindings(self, identity):
        self.reads.append(identity)
        return self.values[identity]


def interpreter(bindings, budget=100000):
    return TransferInterpreter({"blocks": {}}, {"locations": {}, "ir_semantics": {}},
                               Bindings(bindings), max_variants=budget)


def test_large_raw_product_keeps_only_member_paired_candidates():
    bindings = {f"{kind}{index:03}": {"member:rows": str(index)}
                for kind in ("recipient", "payload") for index in range(60)}
    engine = interpreter(bindings, budget=60)
    rows = list(engine._tuples([
        {identity for identity in bindings if identity.startswith("recipient")},
        {identity for identity in bindings if identity.startswith("payload")},
    ]))
    assert rows == [(f"recipient{index:03}", f"payload{index:03}") for index in range(60)]
    assert len(engine.registry.reads) == len(bindings)


def test_unbound_values_remain_compatible_without_losing_slot_order():
    engine = interpreter({"a": {"member": "A"}, "b": {"member": "B"},
                          "left": {}, "right": {}})
    assert list(engine._tuples([{"right", "left"}, {"b", "a"}, {"left"}])) == [
        (left, member, "left") for left in ("left", "right") for member in ("a", "b")]


def test_compatible_product_has_an_explicit_limit_without_partial_success():
    engine = interpreter({identity: {} for identity in ("a", "b", "x", "y")}, budget=3)
    with pytest.raises(PropagationLimitError, match="compatible candidate relation"):
        list(engine._tuples([{"a", "b"}, {"x", "y"}]))


def test_incompatible_later_operand_does_not_report_an_unsupported_prefix():
    engine = interpreter({
        "old_x": {"member": "A", "incoming:member": "P", "unresolved:member": "multiple_generations"},
        "old_y": {"member": "A", "incoming:member": "P"},
        "other": {"member": "B"},
    })
    assert list(engine._tuples([{"old_x"}, {"old_y"}, {"other"}])) == []


def test_compatible_unresolved_generations_still_fail_without_guessing_pairs():
    engine = interpreter({
        "old_x": {"incoming:member": "P", "unresolved:member": "multiple_generations"},
        "old_y": {"incoming:member": "P"},
    })
    with pytest.raises(UnsupportedLoopDomain, match="correlation across multiple generations"):
        list(engine._tuples([{"old_x"}, {"old_y"}]))
    assert list(engine._tuples([{"old_x"}, {"old_x"}])) == [("old_x", "old_x")]


def test_tuple_join_matches_filtered_product_for_partially_bound_axes():
    bindings = {
        "a": {"member": "A"}, "b": {"member": "B"}, "free": {},
        "x": {"member": "A", "predecessor": "left"},
        "y": {"member": "B", "predecessor": "right"},
        "p": {"predecessor": "left"}, "q": {"predecessor": "right"},
    }
    groups = [{"a", "b", "free"}, {"x", "y"}, {"p", "q"}]
    expected = []
    for row in product(*(sorted(group) for group in groups)):
        context = {}
        for identity in row:
            if any(axis in context and context[axis] != value for axis, value in bindings[identity].items()):
                break
            context.update(bindings[identity])
        else:
            expected.append(row)
    assert list(interpreter(bindings)._tuples(groups)) == expected


def test_empty_slots_and_zero_argument_operations_retain_their_meaning():
    engine = interpreter({})
    assert list(engine._tuples([])) == [()]
    assert list(engine._tuples([set()])) == []


def test_ordinary_compute_publishes_each_outputs_actual_input_tuple():
    from skillflow.propagation.data import DataRegistry, LiteralContent
    from skillflow.propagation.models import FlowState, FlowLocation
    from tests.propagation.test_projected_states import ir, ref, local, spec

    registry = DataRegistry("ordinary-tuple-publication")
    values = {registry.register_source(value, acquired_from="fixture", content=LiteralContent(value=value)).id
              for value in ("a", "b")}
    instruction = ir("compute", ("x",), ("result",))
    semantics = spec([{"op": "compute", "inputs": [ref(), ref()],
                       "dependencies": ["possible", "possible"], "output": "combined"}], [local("combined")])
    annotation = {"locations": {}, "ir_semantics": {instruction["id"]: semantics.model_dump(mode="json")}}
    engine = TransferInterpreter({"blocks": {"b": {"instructions": [instruction]}}}, annotation, registry,
                                 typed_specs={instruction["id"]: semantics})
    record = engine.evaluate(instruction, semantics, FlowState.from_mapping({
        FlowLocation(kind="result", name="x"): frozenset(values)}))
    operation = record.events[0].atomic_ops[0]
    assert len(operation.alternatives) == 4
    for alternative in operation.alternatives:
        assert len(alternative.outputs[0]) == 1
        result = registry.get(next(iter(alternative.outputs[0])))
        assert result.origin.inputs == [next(iter(slot)) for slot in alternative.inputs]
