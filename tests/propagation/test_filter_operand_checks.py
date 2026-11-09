"""Collection-operand errors remain local checks in trusted computation."""
import pytest

from skillflow.propagation.data import (
    DataConflictError, DataRegistry, LiteralContent, OpaqueContent, Origin,
    WholeExceptContent,
)
from skillflow.propagation.interpreter import TransferInterpreter
from skillflow.propagation.loop_domain import LoopFactRegistry
from skillflow.propagation.models import FlowLocation, FlowState
from tests.propagation.test_projected_states import ir, literal, local, ref, spec


def engine_for(registry, reference):
    instruction = ir("filter", ("source",), ("filtered",))
    semantics = spec([{"op": "filter_items", "input": reference, "predicate": "keep",
                       "output": "filtered"}], [local("filtered")])
    annotation = {"locations": {}, "ir_semantics": {"filter": semantics.model_dump(mode="json")}}
    engine = TransferInterpreter({"blocks": {"b": {"instructions": [instruction]}}}, annotation, registry,
                                 typed_specs={"filter": semantics})
    return engine, instruction, semantics


@pytest.mark.parametrize("value", [7, {"field": "value"}])
@pytest.mark.parametrize("loop", [False, True])
def test_filter_rejects_known_scalar_and_object_before_publishing_a_subset(value, loop):
    registry = DataRegistry("filter-operand")
    if loop:
        registry = LoopFactRegistry(registry, {})
    registry.enable_computation()
    base = (registry.family("loop", ["input"], [], LiteralContent(value=value), Origin(at="input"))
            if loop else registry.register_source("input", acquired_from="fixture", content=LiteralContent(value=value)))
    engine, instruction, semantics = engine_for(registry, ref())
    state = FlowState.from_mapping({FlowLocation(kind="result", name="source"): frozenset({base.id})})
    before = registry.snapshot_computed()
    with pytest.raises(DataConflictError, match="requires a collection"):
        engine.evaluate(instruction, semantics, state)
    assert registry.snapshot_computed() == before
    registry.validate()


def test_filter_rejects_open_known_object_and_tracks_structural_base_reads():
    registry = DataRegistry("filter-object-base").enable_computation()
    base = registry.register_source("object", acquired_from="fixture")
    registry.register_part(base.id, ["field"])
    view = registry.create_result("view", content=WholeExceptContent(base=base.id, excluded_parts=[["hidden"]]),
                                  origin=Origin(at="view", inputs=[base.id]))
    unrelated = registry.register_source("unrelated", acquired_from="fixture")
    engine, instruction, semantics = engine_for(registry, ref())
    state = FlowState.from_mapping({FlowLocation(kind="result", name="source"): frozenset({view.id})})
    with registry.observe_reads() as observed:
        with pytest.raises(DataConflictError, match="requires a collection"):
            engine.evaluate(instruction, semantics, state)
    assert ("data", base.id) in observed
    assert ("data", unrelated.id) not in observed


@pytest.mark.parametrize("loop", [False, True])
def test_unknown_collection_does_not_need_a_size_or_materialized_members(loop):
    registry = DataRegistry("filter-unknown")
    if loop:
        registry = LoopFactRegistry(registry, {})
    registry.enable_computation()
    base = (registry.family("loop", ["input"], [], OpaqueContent(), Origin(at="input"))
            if loop else registry.register_source("input", acquired_from="fixture"))
    engine, instruction, semantics = engine_for(registry, ref())
    state = FlowState.from_mapping({FlowLocation(kind="result", name="source"): frozenset({base.id})})
    result = engine.evaluate(instruction, semantics, state)
    assert result.events[0].atomic_ops[0].outputs[0]
    registry.validate()


def test_repeated_literal_collection_keeps_its_existing_result_identity():
    registry = DataRegistry("filter-literal").enable_computation()
    engine, instruction, semantics = engine_for(registry, literal(["a", "b"]))
    first = engine.evaluate(instruction, semantics, FlowState())
    count = len(registry)
    second = engine.evaluate(instruction, semantics, FlowState())
    assert first.events[0].atomic_ops[0].outputs == second.events[0].atomic_ops[0].outputs
    assert len(registry) == count
    registry.validate()
