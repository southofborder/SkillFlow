"""Offline comparison of DOE publication only, using new temporary fake data."""
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.doe import formal_runner
from skillflow.doe.demand_engine import DemandEngine
from tests.doe.test_formal_runner import propagation_run, stable_test_implementation


def main():
    directory = Path(__file__).resolve().parent
    saved_source = directory / "before/src/skillflow/doe/formal_runner.py"
    spec = importlib.util.spec_from_file_location("skillflow.doe._reuse_baseline", saved_source)
    baseline = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = baseline
    spec.loader.exec_module(baseline)
    measurements = {}
    outputs = {}
    with pytest.MonkeyPatch.context() as setup, TemporaryDirectory(prefix="skillflow-doe-reuse-") as temp:
        stable_test_implementation.__wrapped__(setup)
        setup.setattr(baseline, "implementation_provenance", formal_runner.implementation_provenance)
        root = Path(temp)
        upstream = propagation_run.__wrapped__(root, setup)
        for label, module in (("before_publication_only", baseline), ("after_publication_only", formal_runner)):
            counters = {"upstream_bundle_loads": 0, "formal_result_reconstructions": 0, "demand_solves": 0}
            with pytest.MonkeyPatch.context() as instrument:
                for owner, name, key in ((module, "_model_bundle", "upstream_bundle_loads"),
                                         (module, "_validate", "formal_result_reconstructions"),
                                         (DemandEngine, "solve", "demand_solves")):
                    original = getattr(owner, name)
                    def wrapped(*args, _original=original, _key=key, **kwargs):
                        counters[_key] += 1
                        return _original(*args, **kwargs)
                    instrument.setattr(owner, name, wrapped)
                started = perf_counter()
                result = module.run_doe(upstream, run_dir=root / label)
                counters["elapsed_seconds"] = perf_counter() - started
            outputs[label] = {key: canonical_sha256(result[key]) for key in ("result", "support")}
            outputs[label]["index"] = canonical_sha256(result["review"].index_dict())
            counters["status"] = result["result"]["status"]
            measurements[label] = counters
    evidence = {"scope": "Synthetic fresh fake-client fixture; DOE publication only, shared current dependencies",
        "not_a_real_skill_speedup": True, "new_model_calls": 0, "historical_runs_touched": 0,
        "baseline_formal_runner_sha256": sha_file(saved_source),
        "current_formal_runner_sha256": sha_file(Path(formal_runner.__file__)),
        "measurements": measurements, "output_hashes": outputs,
        "same_result_index_and_support": len({canonical_sha256(value) for value in outputs.values()}) == 1}
    assert evidence["same_result_index_and_support"]
    destination = directory / "doe-publication-benchmark.json"
    destination.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
