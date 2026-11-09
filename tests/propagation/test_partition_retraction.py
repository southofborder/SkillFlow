"""An old backedge cannot keep a loop alive after external support is removed."""
from collections import Counter

import pytest

from examples.propagation.propagation_demo import (
    fixture_annotation, input_ref, instruction, literal, local, operand,
)
from skillflow.propagation import propagate
from skillflow.propagation.data import DataRegistry, KnownPartsContent
from skillflow.propagation.interpreter import TransferInterpreter, UnsupportedLoopDomain


def loop_with_external_entries(*, surviving_entry=False):
    def block(name, rows):
        return {"block_id": name, "block_name": name, "instructions": rows}

    blocks = {
        "entry": block("entry", [instruction("start", [{"type": "literal", "literal_value": True}], opcode="dispatch")]),
        "left": block("left", [instruction("write_left"), instruction("gate_left", opcode="dispatch")]),
        "head": block("head", [instruction("read", outputs=["current"]),
                               instruction("head_next", [operand("current")], opcode="dispatch")]),
        "body": block("body", [instruction("send", [operand("current")]),
                               instruction("body_next", [operand("current")], opcode="dispatch")]),
        "exit": block("exit", [instruction("return", [operand("current")], opcode="return")]),
    }
    edges = [("entry", "left"), ("left", "head"), ("head", "body"), ("body", "head"), ("body", "exit")]
    plans = {
        "write_left": (["context_write"], [(0, [{"op": "write", "target": "value", "mode": "replace",
                                                 "input": literal("withdrawn")}])], []),
        "read": (["context_read"], [(0, [{"op": "read", "location": "value", "output": "current"}])], [local("current")]),
        "send": (["net_send"], [(0, [{"op": "deliver", "target": "api", "inputs": [input_ref()]}])], []),
    }
    if surviving_entry:
        blocks["right"] = block("right", [instruction("write_right"), instruction("right_next", opcode="dispatch")])
        edges.extend([("entry", "right"), ("right", "head")])
        plans["write_right"] = (["context_write"], [(0, [{"op": "write", "target": "value", "mode": "replace",
                                                        "input": literal("surviving")}])], [])
    cfg = {"entry_block_id": "entry", "blocks": blocks,
           "edges": [{"source_block_id": source, "target_block_id": target} for source, target in edges]}
    return fixture_annotation(cfg, plans, {"value": ("runtime_context", "value"), "api": ("remote", "api")})


def withdraw_after_a_backedge(monkeypatch, cfg, annotation, *, schedule):
    """A true descriptor read/refinement invalidates the external gate once."""
    registry = DataRegistry("cyclic-entry-retraction")
    prerequisite = registry.register_source("gate", acquired_from="fixture:gate")
    original = TransferInterpreter.evaluate
    calls = Counter()
    withdrawn = False

    def evaluate(self, ir, spec, state):
        nonlocal withdrawn
        calls[ir["id"]] += 1
        if ir["id"] == "ir_gate_left":
            if isinstance(self.registry.get(prerequisite.id).content, KnownPartsContent):
                raise UnsupportedLoopDomain("The external entry prerequisite is no longer supported")
        result = original(self, ir, spec, state)
        # The exit is reached only after body OUT has published its backedge.
        # With LIFO, a surviving entry may reach it before the left gate; wait
        # until that gate really supplied an external row before withdrawing it.
        if ir["id"] == "ir_return" and calls["ir_gate_left"] and not withdrawn:
            withdrawn = True
            self.registry.resolve_part(prerequisite.id, ["withdrawn"])
        return result

    monkeypatch.setattr(TransferInterpreter, "evaluate", evaluate)
    result = propagate(cfg, annotation, initial_registry=registry, schedule=schedule)
    assert withdrawn and calls["ir_send"] > 0
    assert calls["ir_gate_left"] >= 2
    return result, calls


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_losing_the_only_external_entry_retracts_old_backedge_and_records(monkeypatch, schedule):
    result, calls = withdraw_after_a_backedge(monkeypatch, *loop_with_external_entries(), schedule=schedule)
    assert result.status == "incomplete", result.diagnostics
    assert result.stats["scc_rebuilds"] == 1
    assert result.coverage["ir_gate_left"] == "unresolved_binding"
    for identity in ("ir_read", "ir_send", "ir_return"):
        assert result.coverage[identity] == "blocked"
        with pytest.raises(KeyError):
            result.records.get(identity)
    # Reconstruction withdraws execution support, not immutable Data history.
    assert any(entry["data"]["content"] == {"form": "literal", "value": "withdrawn"}
               for entry in result.registry.to_dict()["records"])
    assert calls["ir_send"] < 10


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_other_external_entry_survives_component_reconstruction(monkeypatch, schedule):
    result, _ = withdraw_after_a_backedge(monkeypatch, *loop_with_external_entries(surviving_entry=True), schedule=schedule)
    assert result.status == "incomplete", result.diagnostics
    assert result.stats["scc_rebuilds"] == 1
    assert result.coverage["ir_send"] == result.coverage["ir_return"] == "processed"
    sent = result.records.get("ir_send").events[0].atomic_ops[0]
    assert {result.registry.get(identity).content.value for identity in sent.inputs[0]} == {"surviving"}


def test_internal_backedge_updates_do_not_repeatedly_rebuild_the_component():
    result = propagate(*loop_with_external_entries(surviving_entry=True))
    assert result.status == "complete", result.diagnostics
    assert result.stats["scc_rebuilds"] == 0
    sent = result.records.get("ir_send").events[0].atomic_ops[0]
    assert {result.registry.get(identity).content.value for identity in sent.inputs[0]} == {"withdrawn", "surviving"}


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
@pytest.mark.parametrize("surviving_entry", [False, True])
def test_internal_gate_withdrawal_removes_self_supported_rows(monkeypatch, schedule, surviving_entry):
    cfg, annotation = loop_with_external_entries(surviving_entry=surviving_entry)
    # The gate now belongs to the same static SCC as the head and body. Its
    # withdrawal is internal even though every valid path for the old row used it.
    cfg["edges"].append({"source_block_id": "head", "target_block_id": "left"})
    original = TransferInterpreter.evaluate
    attempts = 0

    def bounded(self, ir, spec, state):
        nonlocal attempts
        attempts += 1
        assert attempts <= 200, "internal withdrawal must not restart the component indefinitely"
        return original(self, ir, spec, state)

    monkeypatch.setattr(TransferInterpreter, "evaluate", bounded)
    result, calls = withdraw_after_a_backedge(monkeypatch, cfg, annotation, schedule=schedule)
    assert result.status == "incomplete", result.diagnostics
    assert result.coverage["ir_gate_left"] == "unresolved_binding"
    assert calls["ir_send"] > 0
    if surviving_entry:
        # Block reachability alone cannot distinguish this surviving row from
        # the unsupported row circulating around the same head/body cycle.
        assert result.coverage["ir_send"] == result.coverage["ir_return"] == "processed"
        sent = result.records.get("ir_send").events[0].atomic_ops[0]
        assert {result.registry.get(identity).content.value for identity in sent.inputs[0]} == {"surviving"}
    else:
        for identity in ("ir_read", "ir_send", "ir_return"):
            assert result.coverage[identity] == "blocked"
            with pytest.raises(KeyError):
                result.records.get(identity)
