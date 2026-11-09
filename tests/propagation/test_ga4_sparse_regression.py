"""Selected v9 GA4 semantics, exercised offline without the paused controller."""
import json
from pathlib import Path

from skillflow.propagation import solver
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.data import LiteralContent, Origin


FIXTURE = Path(__file__).parents[1] / "fixtures" / "backend_sparse_ga4_v9"


def load():
    return tuple(json.loads((FIXTURE / name).read_text(encoding="utf-8"))
                 for name in ("cfg.json", "payload.json"))


def test_actual_ga4_cycle_liveness_retains_completion_inputs_without_all_history(monkeypatch):
    def inspect(cfg, annotation, interpreter, registry, result, seed,
                roots, predecessors, successors, dominators, live, **kwargs):
        inputs = {FlowLocation(kind="result", name=name) for name in ("result_174", "result_175")}
        assert inputs <= live.before["ir_238"]
        assert FlowLocation(kind="result", name="result_178") in live.after["ir_238"]
        all_results = {FlowLocation(kind="result", name=out["identifier"])
                       for block in cfg["blocks"].values() for ir in block["instructions"]
                       for out in ir["outputs"]}
        assert len(live.block_in["block_119"] & all_results) < len(all_results) // 2
        assert len([ir for name, b in cfg["blocks"].items() if name in {f"block_{x}" for x in range(115,126)}
                    for ir in b["instructions"]]) == 24
        return len(live.before["ir_238"])
    monkeypatch.setattr(solver, "_solve_relations", inspect)
    assert solver.propagate(*load()) > 0


def test_actual_completion_operation_does_not_scan_registry_for_repeated_literals(monkeypatch):
    def inspect(cfg, annotation, interpreter, registry, result, seed,
                roots, predecessors, successors, dominators, live, **kwargs):
        # These are explicit fixture entry values, not a reconstruction of the
        # suspended 1,486 environments or a model-quality correction.
        state = {binding.location: binding.data_ids for binding in seed.bindings}
        for name, value in (("result_174", []), ("result_175", "https://fixture.invalid/item")):
            data = registry.create_result("fixture:" + name, content=LiteralContent(value=value),
                                          origin=Origin(at="offline-entry"))
            state[FlowLocation(kind="result", name=name)] = frozenset([data.id])
        ir = next(ir for ir in cfg["blocks"]["block_119"]["instructions"] if ir["id"] == "ir_238")
        interpreter.current_block = "block_119"
        def forbidden(*args, **kwargs):
            raise AssertionError("trusted completion execution must not validate the complete registry")
        monkeypatch.setattr(registry, "_validate_records", forbidden)
        record = interpreter.evaluate(ir, annotation.ir_semantics["ir_238"], FlowState.from_mapping(state))
        assert record.exit_state.get(FlowLocation(kind="result", name="result_178"))
        assert len(record.events) == len(annotation.ir_semantics["ir_238"].events)
        return record
    monkeypatch.setattr(solver, "_solve_relations", inspect)
    solver.propagate(*load())
