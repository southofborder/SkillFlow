"""Synthetic saved-read comparison; no target clients or historical runs."""
from pathlib import Path
import json
import sys
import tempfile
import time
import types
from statistics import median

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pytest import MonkeyPatch
from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.document_guided import online, runner
from tests.document_guided.test_parallel_runner import Harness, freeze_producer


def main():
    before_file = ROOT / "output/verification/material-reuse-20261102/before/src/skillflow/document_guided/online.py"
    old = types.ModuleType("skillflow.document_guided._saved_read_before")
    old.__package__ = "skillflow.document_guided"
    old.__file__ = str(before_file)
    exec(compile(before_file.read_text(encoding="utf-8"), str(before_file), "exec"), old.__dict__)
    result = {"scope": "fresh injected seven-call fixture; ordinary read only; same current dependencies",
              "before_source_sha256": sha_file(before_file),
              "after_source_sha256": sha_file(Path(online.__file__)), "repetitions": 3}
    with MonkeyPatch.context() as patch, tempfile.TemporaryDirectory(prefix="skillflow-reuse-bench-") as temp:
        freeze_producer(patch)
        old.implementation_provenance = online.implementation_provenance
        patch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
        home = Path(temp)
        harness = Harness(home / "run")
        harness.prepare(home / "package")
        def stop_before_backend(state):
            if state["stage"] == "propagation":
                raise KeyboardInterrupt("Synthetic benchmark only needs the saved annotation")
        state = runner.run(harness.directory, client_factory=harness.factory, progress=stop_before_backend)
        assert state["status"] == "interrupted" and len(harness.calls) == 7
        annotation = harness.directory / "annotation"
        inventory = lambda: {str(p.relative_to(harness.directory)): sha_file(p)
                             for p in harness.directory.rglob("*") if p.is_file()}
        files = inventory()
        returned = {}
        for name, module in (("before", old), ("after", online)):
            counts = {"full_assembly": 0, "semantic_chain": 0}
            original_assembly, original_chain = module._assembled_values, module._run_candidate
            def assembly(*args, **kwargs):
                counts["full_assembly"] += 1
                return original_assembly(*args, **kwargs)
            def chain(*args, **kwargs):
                counts["semantic_chain"] += 1
                return original_chain(*args, **kwargs)
            elapsed = []
            with MonkeyPatch.context() as observed:
                observed.setattr(module, "_assembled_values", assembly)
                observed.setattr(module, "_run_candidate", chain)
                for _ in range(result["repetitions"]):
                    started = time.perf_counter()
                    loaded = module.load_annotation(annotation)
                    elapsed.append(time.perf_counter() - started)
                    returned[name] = canonical_sha256(loaded)
            result[name] = {"seconds": elapsed, "median_seconds": median(elapsed),
                            "measured_calls_across_repetitions": counts,
                            "returned_material_sha256": returned[name]}
        assert returned["before"] == returned["after"]
        assert files == inventory()
        assert len(harness.calls) == 7
        result.update(all_returned_material_equal=True, input_artifacts_unchanged=True,
                      injected_fixture_calls=7, benchmark_new_model_calls=0,
                      historical_runs_read_or_replayed=0)
    target = Path(__file__).with_name("saved-annotation-benchmark.json")
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
