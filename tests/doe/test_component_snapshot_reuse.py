"""Real material getters are detached once per analysis, never per operand."""
from collections import Counter
from copy import deepcopy

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.sensitivity_engine import SensitivityEngine
from skillflow.doe.sensitivity_material import build_sensitivity_index
from skillflow.doe.task_material import prepare_task_review
from skillflow.propagation.loading import PropagationMaterials
from tests.doe import test_demand_engine as fixtures
from tests.doe.test_sensitivity_engine import declarations, rows


def owned_fixture(monkeypatch, *, with_bindings=False):
    # Retain the real owner produced by the existing fixture, not its mutable
    # algorithm-test adapter. This is the getter behavior used in formal DOE.
    monkeypatch.setattr(fixtures, "mutable_components", lambda facts: facts)

    def add_literal(cfg):
        cfg["blocks"]["entry"]["instructions"][0]["inputs"].append(
            {"type": "literal", "literal_value": "unused literal"})

    def bind_targets(_prepared, raw, _evidence):
        if with_bindings:
            raw["realizations"][0]["bindings"] = [
                {"target": {"instruction_id": ir, "side": "input", "index": 0},
                 "reason": "The fixture binds the declared requirement to this actual operand."}
                for ir in ("ir_read", "ir_return")]

    values = fixtures.fixture([
        {"op": "select_part", "input": fixtures.inp(), "path": ["body"], "output": "body"},
    ], mode="model", graph_change=add_literal, custom=bind_targets)
    assert type(values[0]) is PropagationMaterials
    return values


def reference_operands(records, instructions, locations):
    """Frozen scan semantics, independent of the new binding indexes."""
    expected = {}
    for ir, instruction in instructions.items():
        for side in ("inputs", "outputs"):
            state = records.get(ir, {}).get(
                "entry_state" if side == "inputs" else "exit_state", {"bindings": []})
            for slot, operand in enumerate(instruction[side]):
                if operand["type"] == "literal":
                    expected[(ir, slot, side)] = set()
                    continue
                selected = [{"kind": "result", "name": operand["identifier"]}] if operand["type"] == "result" else [
                    {"kind": location["kind"], "name": location["name"]}
                    for location in locations.values()
                    if {"instruction_id": ir, "side": "input" if side == "inputs" else "output", "index": slot}
                    in location["operand_refs"]]
                expected[(ir, slot, side)] = {value for binding in state["bindings"]
                    if binding["location"] in selected for value in binding["data_ids"]}
    return expected


def test_real_material_getters_are_read_once_through_demand_and_sensitivity(monkeypatch):
    facts, task, annotation, targets = owned_fixture(monkeypatch)
    before = {name: getattr(facts, name) for name in ("records", "cfg", "data")}
    calls = Counter()
    getters = {name: getattr(PropagationMaterials, name).fget for name in before}
    for name, getter in getters.items():
        def counted(owner, *, name=name, getter=getter):
            calls[name] += 1
            return getter(owner)
        monkeypatch.setattr(PropagationMaterials, name, property(counted))

    engine = DemandEngine(facts, task, annotation, fixtures.candidate(targets), targets)
    expected = reference_operands(before["records"], engine.index.instructions, engine.compiled["locations"])
    assert expected[("ir_read", 0, "inputs")]
    assert expected[("ir_read", 1, "inputs")] == set()
    for _ in range(20):
        for position, values in expected.items():
            assert set(engine._operand_data(*position)) == values
    demand = engine.solve()
    sensitivity = SensitivityEngine(engine, demand,
        build_sensitivity_index(annotation, declarations())["declarations"]).solve()
    assert sensitivity["status"] == "complete"
    assert rows(sensitivity)
    assert {row["conclusion"] for row in rows(sensitivity)} == {"excess_supported"}
    assert calls == {"records": 1, "cfg": 1, "data": 1}
    assert all(getter(facts) == before[name] for name, getter in getters.items())


def test_index_and_returned_candidates_preserve_public_copy_isolation(monkeypatch):
    facts, task, annotation, targets = owned_fixture(monkeypatch)
    before = {name: getattr(facts, name) for name in ("records", "cfg", "data", "coverage")}
    engine = DemandEngine(facts, task, annotation, fixtures.candidate(targets), targets)
    other = DemandEngine(facts, task, annotation, fixtures.candidate(targets), targets)
    expected = deepcopy(engine.index.records)
    facts.records.clear()
    facts.cfg["blocks"].clear()
    facts.data.clear()
    assert engine.index.records == other.index.records == expected
    values = engine._operand_data("ir_read", 0, "inputs")
    original = set(values)
    values.add("outside-the-material")
    assert engine._operand_data("ir_read", 0, "inputs") == original
    result = engine.solve()
    result["coverage"]["upstream"].clear()
    assert engine.index.coverage == before["coverage"]
    engine.index.records.clear()
    engine.index.cfg["blocks"].clear()
    engine.index.data.clear()
    assert other.index.records == expected
    assert all(getattr(facts, name) == value for name, value in before.items())


def test_task_review_reads_cfg_once_for_multiple_realization_bindings(monkeypatch):
    facts, task, _annotation, _targets = owned_fixture(monkeypatch, with_bindings=True)
    getter, calls = PropagationMaterials.cfg.fget, []
    original = getter(facts)

    def counted(owner):
        calls.append(owner)
        return getter(owner)

    monkeypatch.setattr(PropagationMaterials, "cfg", property(counted))
    review = prepare_task_review(facts, task)
    assert len(calls) == 1
    assert len(review.targets) == 2
    review.cfg["blocks"].clear()
    review.targets.clear()
    assert getter(facts) == original
