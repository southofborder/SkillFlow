"""Read-dependent relation partitions preserve useful tuples, not dead history."""
from copy import deepcopy

from skillflow.propagation.solver import propagate, _row_key
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.data.summary import content_options
from tests.propagation.test_explicit_loops import explicit_loop_fixture, nested_loop_fixture
from examples.propagation.propagation_demo import instruction, operand


def test_relation_row_key_does_not_union_correlated_fields():
    x, y = FlowLocation(kind="result", name="x"), FlowLocation(kind="result", name="y")
    assert _row_key({x: frozenset(["a"]), y: frozenset(["A"])}) != _row_key(
        {x: frozenset(["b"]), y: frozenset(["B"])})


def test_projected_exit_retains_public_output_but_drops_dead_seed_at_return():
    cfg, annotation = explicit_loop_fixture()
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    seed = result.records.get("ir_seed")
    assert {b.location.name for b in seed.exit_state.bindings} >= {"initial", "items"}
    returned = result.records.get("ir_return")
    assert "initial" not in {b.location.name for b in returned.entry_state.bindings}
    assert result.stats["projected_locations_removed"] > 0


def test_partitioned_nested_receivers_remain_paired_and_schedules_agree():
    cfg, annotation = nested_loop_fixture()
    results = [propagate(cfg, annotation, schedule=order) for order in ("fifo", "lifo")]
    for result in results:
        assert result.status == "complete", result.diagnostics
        op = result.records.get("ir_send").events[0].atomic_ops[0]
        pairs = set()
        for alternative in op.alternatives:
            values = [content_options(result.registry, next(iter(slot))) for slot in alternative.inputs]
            pairs.update((a["value"], b["value"]) for a in values[0] for b in values[1])
        assert pairs == {("A", "a0"), ("A", "a1"), ("B", "b0"), ("B", "b1")}
    assert results[0].records.records_dict() == results[1].records.records_dict()


def test_unknown_branch_rows_do_not_mix_repeated_operand():
    from tests.propagation.test_explicit_loops import fixture_annotation, literal, local, input_ref
    def block(name, rows):
        return {"block_id": name, "block_name": name, "instructions": rows}
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("start", [{"type": "literal", "literal_value": True}], opcode="dispatch")]),
        "left": block("left", [instruction("left"), instruction("left_next", opcode="dispatch")]),
        "right": block("right", [instruction("right"), instruction("right_next", opcode="dispatch")]),
        "join": block("join", [instruction("read", outputs=["x"]),
            instruction("twice", [operand("x")], ["both"]), instruction("return", [operand("both")], opcode="return")])},
        "edges": [{"source_block_id": a, "target_block_id": b} for a, b in
                  [("entry", "left"), ("entry", "right"), ("left", "join"), ("right", "join")]]}
    plans = {
        "left": (["context_write"], [(0, [{"op": "write", "target": "xloc", "mode": "replace", "input": literal("a")}])], []),
        "right": (["context_write"], [(0, [{"op": "write", "target": "xloc", "mode": "replace", "input": literal("b")}])], []),
        "read": (["context_read"], [(0, [{"op": "read", "location": "xloc", "output": "x"}])], [local("x")]),
        "twice": (["transform"], [(0, [{"op": "compute", "inputs": [input_ref(), input_ref()],
             "dependencies": ["possible", "possible"], "output": "both"}])], [local("both")])}
    cfg, annotation = fixture_annotation(cfg, plans, {"xloc": ("runtime_context", "x")})
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    op = result.records.get("ir_twice").events[0].atomic_ops[0]
    pairs = set()
    for alternative in op.alternatives:
        values = [content_options(result.registry, next(iter(slot)))[0]["value"] for slot in alternative.inputs]
        pairs.add(tuple(values))
    assert pairs == {("a", "a"), ("b", "b")}


def test_unrelated_branch_is_not_revisited_when_loop_families_grow():
    cfg, annotation = explicit_loop_fixture()
    # A disconnected root is an admitted independent branch in this CFG contract.
    extra = instruction("independent", opcode="return")
    cfg["blocks"]["independent"] = {"block_id": "independent", "block_name": "independent", "instructions": [extra]}
    template = deepcopy(annotation["ir_semantics"]["ir_seed"])
    template["output_bindings"] = []
    annotation["ir_semantics"]["ir_independent"] = template
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.stats["block_evaluation_counts"]["independent"] == 1
    assert result.stats["dependency_wakeups"] > 0
