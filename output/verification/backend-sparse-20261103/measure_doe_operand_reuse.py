"""Post-cap operand-query micro comparison; not a full DOE or GA4 run."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import inspect
import json
from pathlib import Path
import socket
import statistics
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]


def forbidden(*_args, **_kwargs):
    raise RuntimeError("This fixture measurement permits no network or subprocess calls")


def file_digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-src", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(HERE) or output.exists():
        parser.error("output must be a new file within this verification directory")
    reference_file = args.reference_src.resolve() / "skillflow/doe/demand_engine.py"
    current_file = REPOSITORY / "src/skillflow/doe/demand_engine.py"
    before = {str(path): file_digest(path) for path in (reference_file, current_file)}
    socket.socket.connect = forbidden
    socket.socket.connect_ex = forbidden
    socket.create_connection = forbidden
    subprocess.Popen = forbidden
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(REPOSITORY / "src"), str(REPOSITORY)]

    import pytest
    from skillflow.common.recording import canonical_sha256
    from skillflow.doe.demand_engine import DemandEngine
    from skillflow.propagation.loading import PropagationMaterials
    from tests.doe.test_component_snapshot_reuse import owned_fixture
    from tests.doe.test_demand_engine import candidate

    # Compile only the original operand method, not the old solver/module. Both
    # methods query exactly the same new, detached synthetic engine/material.
    source = reference_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(reference_file))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DemandEngine")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "_operand_data")
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(reference_file), "exec"), namespace)
    reference = namespace["_operand_data"]
    assert Path(inspect.getfile(DemandEngine)).resolve() == current_file.resolve()
    with pytest.MonkeyPatch.context() as patch:
        facts, task, annotation, targets = owned_fixture(patch)

    getters = {name: getattr(PropagationMaterials, name) for name in ("cfg", "data", "records")}

    def install_counts(counts):
        for name, descriptor in getters.items():
            def counted(owner, *, name=name, getter=descriptor.fget):
                counts[name] += 1
                return getter(owner)
            setattr(PropagationMaterials, name, property(counted))

    def restore_getters():
        for name, descriptor in getters.items():
            setattr(PropagationMaterials, name, descriptor)

    initialization = Counter({name: 0 for name in getters})
    install_counts(initialization)
    try:
        engine = DemandEngine(facts, task, annotation, candidate(targets), targets)
    finally:
        restore_getters()
    queries = [(ir, slot, side) for ir, instruction in engine.index.instructions.items()
               for side in ("inputs", "outputs") for slot in range(len(instruction[side]))]
    expected = [sorted(reference(engine, *query)) for query in queries]
    fixture_sha256 = canonical_sha256({"cfg": facts.cfg, "records": facts.records,
                                      "annotation": annotation})
    repetitions, cycles = [], 200
    for label, function in (("frozen_r2_operand_method", reference),
                            ("post_cap_r3_operand_method", DemandEngine._operand_data)):
        for repetition in range(1, 4):
            counts = Counter({name: 0 for name in getters})
            install_counts(counts)
            try:
                wall, cpu = time.perf_counter(), time.process_time()
                candidate_visits = 0
                for _ in range(cycles):
                    last = []
                    for query in queries:
                        result = function(engine, *query)
                        candidate_visits += len(result)
                        last.append(result)
                cpu = time.process_time() - cpu
                wall = time.perf_counter() - wall
            finally:
                restore_getters()
            actual = [sorted(values) for values in last]
            assert actual == expected
            assert candidate_visits == cycles * sum(map(len, expected))
            repetitions.append({"arm": label, "repetition": repetition,
                "wall_seconds": wall, "cpu_seconds": cpu, "queries": cycles * len(queries),
                "candidate_visits": candidate_visits, "component_getter_calls": dict(counts),
                "operand_candidates_sha256": canonical_sha256(actual), "candidates_match": True})

    summaries = {}
    for label in {row["arm"] for row in repetitions}:
        rows = [row for row in repetitions if row["arm"] == label]
        summaries[label] = {"median_wall_seconds": statistics.median(row["wall_seconds"] for row in rows),
            "median_cpu_seconds": statistics.median(row["cpu_seconds"] for row in rows),
            "records_getter_calls": [row["component_getter_calls"]["records"] for row in rows]}
    assert len({row["operand_candidates_sha256"] for row in repetitions}) == 1
    assert initialization == {"cfg": 1, "data": 1, "records": 1}
    assert all(row["component_getter_calls"]["records"] ==
               (cycles * len(queries) if row["arm"] == "frozen_r2_operand_method" else 0)
               for row in repetitions)
    after = {path: file_digest(Path(path)) for path in before}
    assert after == before
    report = {"schema_version": "doe-operand-query-micro-v1", "status": "complete",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Post-cap repeated operand-query micro comparison on one synthetic fixture",
        "full_doe": False, "ga4_execution": False, "model_calls": 0,
        "historical_replay": False, "skill_execution": False,
        "reference_scope": "Only the frozen r2 _operand_data method; no old full engine run",
        "measurement_scope": "Queries only; fixture propagation, engine initialization, hashes and JSON save excluded",
        "source_files_sha256": before, "sources_unchanged": True,
        "reference_method_sha256": sha256(ast.get_source_segment(source, method).encode()).hexdigest(),
        "fixture_sha256": fixture_sha256, "queries_per_cycle": len(queries), "cycles": cycles,
        "current_engine_initialization_getter_calls": dict(initialization),
        "repetitions": repetitions, "summary": summaries,
        "same_candidates_all_six_measurements": True,
        "limits": "This does not measure full DOE, GA4 latency, or whole-run memory and cannot amend the timed-out r2 receipt."}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"output": str(output), "status": report["status"], "summary": summaries}))


if __name__ == "__main__":
    main()
