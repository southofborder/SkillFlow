"""Two authored propagation-only comparisons; preparation never calls propagate.

Run only after the root's full old/new comparison has stopped. This script has
no controller, subprocess supervisor, replay, DOE or model entry point. It is a
small companion receipt, not a substitute for the full fixed-input comparison.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import socket
import statistics
import subprocess
import sys
import time
import traceback


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
POLICY = {"scope": "propagation-only micro comparison", "full_doe": False,
          "model_calls": 0, "execute_skill": False, "historical_replay": False,
          "repetitions": 3, "schedule": "default FIFO", "parallel_workers": 0}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def new_output(path):
    path = Path(path).resolve()
    if path == HERE or not path.is_relative_to(HERE) or path.exists():
        raise ValueError("Use a new output file under this verification directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n")


def offline_only():
    def forbidden(*args, **kwargs):
        raise RuntimeError("This authored micro comparison forbids network and child execution")
    socket.socket.connect = forbidden
    socket.socket.connect_ex = forbidden
    socket.create_connection = forbidden
    subprocess.Popen = forbidden


def select_source(src):
    src = Path(src).resolve()
    if not (src / "skillflow/propagation/solver.py").is_file():
        raise ValueError("--src must name the selected source directory containing skillflow")
    if any(name == "skillflow" or name.startswith("skillflow.") for name in sys.modules):
        raise ValueError("Select the frozen source before importing any SkillFlow module")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(src))
    return src


def source_identity(src):
    files = {path.relative_to(src).as_posix(): file_sha(path)
             for path in sorted((src / "skillflow").rglob("*.py"))}
    return {"source_directory": str(src), "files": files, "sha256": sha(files)}


def prepare(args):
    """Reuse existing fixture builders once; neither fixture is evaluated here."""
    output = new_output(args.output)
    selected = select_source(args.src)
    sys.path.insert(1, str(REPOSITORY))
    from tests.propagation.test_explicit_loops import explicit_loop_fixture, nested_loop_fixture
    from examples.propagation.propagation_demo import instruction, input_ref
    from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
    from skillflow.propagation.contracts.profiles import AnnotationPayload
    from skillflow.propagation.contracts.specs import validate_specs
    from skillflow.graph.ir.cfg import ControlFlowGraph

    cfg, payload = deepcopy(explicit_loop_fixture(("alpha", "beta")))
    # The extra root follows the existing independent-root test construction.
    # Its literal and endpoint are unrelated to the loop's acquisitions.
    cfg["blocks"]["independent"] = {"block_id": "independent", "block_name": "independent",
        "instructions": [instruction("independent", [{"type": "literal",
            "literal_value": "independent-payload"}], opcode="return")]}
    evidence = {"target": {"instruction_id": "ir_independent", "path": []},
                "reason": "An authored independent delivery is unrelated to the explicit loop."}
    spec = deepcopy(payload["ir_semantics"]["ir_fetch"])
    spec["operator_evidences"] = [{**deepcopy(evidence), "value": value} for value in spec["operator"]]
    spec["output_bindings"] = []
    spec["events"] = [{"effect": "net_send", "evidences": [deepcopy(evidence)],
        "atomic_ops": [{"op": "deliver", "target": "api", "inputs": [input_ref()],
                        "evidences": [deepcopy(evidence)]}]}]
    payload["ir_semantics"]["ir_independent"] = spec
    payload["sink_boundaries"] = [value.model_dump(mode="json") for value in
        derive_sink_boundaries(payload["locations"], payload["ir_semantics"])]
    nested_cfg, nested_payload = nested_loop_fixture()
    cases = {"loop_with_independent_root": {"cfg": cfg, "payload": payload},
             "nested_receiver_pairs": {"cfg": nested_cfg, "payload": nested_payload}}
    for item in cases.values():
        graph = ControlFlowGraph.model_validate(item["cfg"])
        graph.validate_integrity()
        item["cfg"] = json.loads(graph.to_json())
        parsed = AnnotationPayload.model_validate(item["payload"])
        validate_specs(item["cfg"], parsed)
        item["payload"] = parsed.model_dump(mode="json")
    value = {"schema_version": "authored-propagation-micro-input-v1", "policy": POLICY,
        "preparation_source": source_identity(selected),
        "fixture_files": {str(path.relative_to(REPOSITORY)): file_sha(path) for path in (
            REPOSITORY / "tests/propagation/test_explicit_loops.py",
            REPOSITORY / "examples/propagation/propagation_demo.py")},
        "recipe": {"loop": "explicit_loop_fixture(('alpha','beta')) plus the disconnected-root pattern from test_unsupported_typed_guard_does_not_stop_independent_sink_root; keep the valid has_member guard",
                   "nested": "nested_loop_fixture() unchanged",
                   "existing_fixture_evidence": "Existing authored citations are retained; the new independent-root evidence is English."},
        "cases": cases}
    save_new(output, value)
    print(canonical({"prepared": str(output), "sha256": file_sha(output), "propagation_evaluations": 0}))


@contextmanager
def observed_propagation():
    """Count only these known validation/evaluation boundaries during propagate."""
    from skillflow.propagation.data.registry import DataRegistry
    from skillflow.propagation.records import PropagationRecords
    from skillflow.propagation.interpreter import TransferInterpreter
    metrics = {"validators": {}, "ir_evaluations": Counter(), "block_ir_evaluations": Counter(), "maxima": {}}
    restores = []

    def maximum(name, number):
        metrics["maxima"][name] = max(metrics["maxima"].get(name, 0), number)

    def count(name, size):
        value = metrics["validators"].setdefault(name, {"calls": 0, "total_rows": 0, "max_rows": 0})
        value["calls"] += 1
        value["total_rows"] += size
        value["max_rows"] = max(value["max_rows"], size)

    def patch(owner, name, size, *, static=False):
        previous = inspect.getattr_static(owner, name)
        original = getattr(owner, name)
        label = owner.__name__ + "." + name
        metrics["validators"][label] = {"calls": 0, "total_rows": 0, "max_rows": 0}
        def counted(*args, **kwargs):
            count(label, size(args))
            return original(*args, **kwargs)
        setattr(owner, name, staticmethod(counted) if static else counted)
        restores.append((owner, name, previous))

    patch(DataRegistry, "validate", lambda args: len(args[0]._records))
    patch(DataRegistry, "_validate_records", lambda args: len(args[1]))
    patch(DataRegistry, "_validate_data_values", lambda args: len(args[0]), static=True)
    patch(PropagationRecords, "validate", lambda args: len(args[0]._records))
    patch(PropagationRecords, "_validate_record", lambda args: len(args[3]))
    original_evaluate = TransferInterpreter.evaluate

    def state_size(state, prefix):
        maximum(prefix + "_bindings", len(state.bindings))
        maximum(prefix + "_candidate_ids", sum(len(binding.data_ids) for binding in state.bindings))
        maximum(prefix + "_slot_candidates", max((len(binding.data_ids) for binding in state.bindings), default=0))

    def evaluate(interpreter, ir, spec, state):
        identity, block = ir["id"], interpreter.current_block
        metrics["ir_evaluations"][identity] += 1
        metrics["block_ir_evaluations"][str(block)] += 1
        state_size(state, "entry_state")
        maximum("ordinary_registry_records", len(interpreter.registry._records))
        maximum("loop_families", len(getattr(interpreter.registry, "facts", {})))
        frame = sys._getframe(1)
        try:
            for name in ("environments", "rows"):
                value = frame.f_locals.get(name)
                if value is not None and hasattr(value, "__len__"):
                    maximum("caller_" + name, len(value))
        finally:
            del frame
        record = original_evaluate(interpreter, ir, spec, state)
        state_size(record.exit_state, "exit_state")
        for event in record.events:
            children = [child for instance in event.instances for child in instance.body] if hasattr(event, "instances") else [event]
            for child in children:
                for operation in child.atomic_ops:
                    maximum("operation_alternatives", len(operation.alternatives))
                    maximum("operation_slot_candidates", max((len(slot) for slot in
                        [*operation.inputs, *operation.outputs]), default=0))
        return record

    TransferInterpreter.evaluate = evaluate
    try:
        yield metrics
    finally:
        TransferInterpreter.evaluate = original_evaluate
        for owner, name, previous in reversed(restores):
            setattr(owner, name, previous)


def fact_check(case, result):
    """Inspect completed facts outside the measured propagation interval."""
    from skillflow.propagation.data.summary import content_options
    registry = result.registry.to_dict()  # Same explicit full audit on both versions.
    records = result.records.records_dict()
    facts = {identity: {key: row[key] for key in ("order", "precedence", "events")}
             for identity, row in records.items()}
    checked = {"complete": result.status == "complete", "diagnostics": deepcopy(result.diagnostics),
        "data_sha256": sha(registry), "operation_facts_sha256": sha(facts),
        "data_count": len(registry["records"]), "record_count": len(records), "coverage": deepcopy(result.coverage)}
    if case == "nested_receiver_pairs":
        operation = result.records.get("ir_send").events[0].atomic_ops[0]
        pairs = set()
        for alternative in operation.alternatives:
            if any(len(slot) != 1 for slot in alternative.inputs):
                raise ValueError("The nested fixture lost its per-occurrence single-value input pairing")
            values = [content_options(result.registry, next(iter(slot))) for slot in alternative.inputs]
            if any(value["form"] != "literal" for slot in values for value in slot):
                raise ValueError("Nested receiver/payload validation needs the fixture's literal values")
            pairs.update((receiver["value"], payload["value"]) for receiver in values[0] for payload in values[1])
        expected = {("A", "a0"), ("A", "a1"), ("B", "b0"), ("B", "b1")}
        checked.update(receiver_payload_pairs=sorted(pairs), expected_pairs=sorted(expected),
                       alternative_count=len(operation.alternatives),
                       paired_values_preserved=pairs == expected and len(operation.alternatives) == 4)
    else:
        member = result.records.get("ir_member").events[0].atomic_ops[0]
        delivery = result.records.get("ir_independent").events[0].atomic_ops[0]
        values = [value for identity in delivery.inputs[0] for value in content_options(result.registry, identity)]
        members = [value for identity in member.outputs[0] for value in content_options(result.registry, identity)]
        member_values = sorted(value["value"] for value in members if value["form"] == "literal")
        checked.update(member_output_count=len(member.outputs[0]), member_alternative_count=len(member.alternatives),
            member_literal_values=member_values, independent_payload=values,
            paired_values_preserved=(len(member.outputs[0]) == 2 and len(member.alternatives) == 2
                and len(members) == 2 and member_values == ["alpha", "beta"]
                and values == [{"form": "literal", "value": "independent-payload"}]))
    checked["passed"] = checked["complete"] and checked["paired_values_preserved"]
    return checked


def run(args):
    output = new_output(args.output)
    selected = select_source(args.src)
    initial_source = source_identity(selected)
    input_path = Path(args.input).resolve()
    input_hash = file_sha(input_path)
    prepared = json.loads(input_path.read_text(encoding="utf-8"))
    if prepared.get("schema_version") != "authored-propagation-micro-input-v1":
        raise ValueError("Unexpected micro input identity")
    from skillflow.propagation.solver import propagate
    if not Path(inspect.getfile(propagate)).resolve().is_relative_to(selected):
        raise ValueError("Propagation was imported from a different source tree")
    signature = inspect.signature(propagate)
    if signature.parameters["schedule"].default != "fifo":
        raise ValueError("The selected version does not use the required default FIFO schedule")
    report = {"policy": POLICY, "input": str(input_path), "input_sha256": input_hash,
        "implementation": initial_source, "propagate_signature": str(signature), "cases": {},
        "measurement_scope": "Timers and validation counts cover direct propagate only. Imports, input preparation, full fact audits, hashing and JSON saving are outside those intervals. Validator counters are nested and must not be summed as independent work. Block statistics returned by the solver are authoritative; block_ir_evaluations counts instruction visits, not block visits."}
    failure = None
    try:
        for case, item in prepared["cases"].items():
            rows = report["cases"][case] = []
            for repetition in range(1, 4):
                cfg, payload = deepcopy(item["cfg"]), deepcopy(item["payload"])
                with observed_propagation() as counters:
                    started, cpu = time.perf_counter(), time.process_time()
                    solved = propagate(cfg, payload)
                    wall, used_cpu = time.perf_counter() - started, time.process_time() - cpu
                checked = fact_check(case, solved)
                rows.append({"repetition": repetition, "wall_seconds": wall, "cpu_seconds": used_cpu,
                    "solver_stats": deepcopy(solved.stats), "ir_evaluation_total": sum(counters["ir_evaluations"].values()),
                    "independent_ir_evaluations": counters["ir_evaluations"].get("ir_independent"),
                    **counters, "fact_check": checked})
                if not checked["passed"]:
                    raise ValueError("Completed micro fixture failed its declared fact/pair checks: " + case)
        report["summary"] = {case: {"wall_seconds_median": statistics.median(row["wall_seconds"] for row in rows),
            "cpu_seconds_median": statistics.median(row["cpu_seconds"] for row in rows),
            "ir_evaluations": [row["ir_evaluation_total"] for row in rows],
            "block_evaluations": [row["solver_stats"].get("block_evaluations") for row in rows],
            "independent_ir_evaluations": [row["independent_ir_evaluations"] for row in rows],
            "operation_facts_repeat_equal": len({row["fact_check"]["operation_facts_sha256"] for row in rows}) == 1,
            "data_repeat_equal": len({row["fact_check"]["data_sha256"] for row in rows}) == 1,
            "all_fact_checks_passed": all(row["fact_check"]["passed"] for row in rows)}
            for case, rows in report["cases"].items()}
        if not all(value["operation_facts_repeat_equal"] and value["data_repeat_equal"] for value in report["summary"].values()):
            raise ValueError("Repeated propagation produced unequal canonical facts")
    except Exception as error:
        failure = error
        report["failure"] = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()}
    report["source_unchanged"] = source_identity(selected) == initial_source
    report["input_unchanged"] = file_sha(input_path) == input_hash
    report["status"] = "complete" if failure is None and report["source_unchanged"] and report["input_unchanged"] else "failed"
    save_new(output, report)
    print(canonical({"output": str(output), "status": report["status"], "summary": report.get("summary")}))
    if report["status"] != "complete":
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    preparation = sub.add_parser("prepare", help="Prepare both authored CFG/payload inputs once; no propagation")
    preparation.add_argument("--src", required=True)
    preparation.add_argument("--output", required=True)
    execution = sub.add_parser("run", help="Run the fixed two inputs, three sequential repetitions each")
    execution.add_argument("--src", required=True)
    execution.add_argument("--input", required=True)
    execution.add_argument("--output", required=True)
    args = parser.parse_args()
    offline_only()
    (prepare if args.command == "prepare" else run)(args)


if __name__ == "__main__":
    main()
