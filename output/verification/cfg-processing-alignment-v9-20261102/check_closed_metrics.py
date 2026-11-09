"""Offline extractor checks: synthetic directories and read-only old JSON only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("closed_metrics", HERE / "extract_closed_metrics.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def check():
    assertions = []
    with TemporaryDirectory(dir=HERE, prefix="metrics-test-") as temporary:
        root = Path(temporary).resolve()
        assert root.parent == HERE.resolve()
        run = root / "experiments/doe/runs" / f"document-guided-ga4-alignment-high-v9-{module.TAG}"
        run.mkdir(parents=True)
        verify = root / "verify"
        write(verify / "prepared-runs.json", {"run_order": [{"case_id": "ga4", "run_directory": str(run)}]})
        module.PROJECT, module.VERIFY = root, verify
        # A malformed result proves the early guard does not open it.
        (run / "result.json").write_text("unreadable live result", encoding="utf-8")
        try:
            module.extract("ga4")
        except ValueError as error:
            assert "controller-finished" in str(error)
        else:
            raise AssertionError("Unfinished run was read")
        assertions.append("Unfinished exact run is refused before candidate/result reads")
        write(run / "controller-finished.json", {"status": "partial", "finished_at": "2026-11-02T02:01:00+00:00"})
        write(run / "result.json", {"status": "partial", "selected_annotation": "annotation", "counts": {"logical_calls": 3}})
        write(run / "annotation/inputs/references.json", {"cfg": {"path": "../graph/selected.json"}})
        statuses = dict(zip([f"ir_{n}" for n in range(6)], module.STATUSES))
        write(run / "graph/selected.json", {"cfg": {"blocks": {"b": {"instructions": [{"id": key} for key in statuses]}}}})
        write(run / "propagation/manifest.json", {"status": "incomplete", "coverage": statuses})
        write(run / "propagation/records.json", {"ir_0": {}})
        write(run / "doe/doe-result.json", {"status": "partial", "sinks": [{"data_reviews": [{"conclusion": "no_excess_established"}]}],
            "coverage": {"declarations": 2, "resolved_declarations": 1, "unresolved_boundaries": [{}]}})
        write(run / "analysis-finished.json", {"started_at": "2026-11-02T02:00:00+00:00", "analysis_seconds": 40})
        write(run / "replay-check.json", {"status": "matched", "elapsed_seconds": 18, "new_native_markers": 0})
        rows = [{"logical_request": "transport/graph/one", "structural_correction": False, "network_attempt_index": n} for n in [1, 2]]
        rows += [{"logical_request": "transport/graph/two", "structural_correction": True},
                 {"logical_request": "transport/revision-processing/three", "structural_correction": False}]
        write(run / "metrics.json", {"native_process_starts": 4, "logical_requests": 3, "network_retry_attempts": 1,
            "known_token_usage": {"input_tokens": 100, "cached_input_tokens": 40, "output_tokens": 20, "total_tokens": 120},
            "partial_token_usage": {"input_tokens": 10}, "unknown_usage_requests": 1,
            "total_usage_known": False, "requests": rows, "http_attempts": None})
        write(run / "component-timing.json", {"records": [{"phase": "analysis", "component": name, "elapsed_seconds": seconds, "returned": True}
            for name, seconds in [("propagation_total", 10), ("propagation_compute", 4), ("propagation_save", 3)]]})
        value = module.extract("ga4")
        coverage = value["propagation"]["generated_ir"]
        assert coverage["total"] == 6 and coverage["cutoff_count"] == 2
        assert coverage["by_status"]["not_reached"] == 1 and coverage["processed_fraction"] == 1 / 6
        assert value["doe"]["comparisons"] == 1 and value["doe"]["coverage"]["resolved_declarations"] == 1
        assert value["transport"]["known_token_usage"]["total_tokens"] == 120
        assert value["transport"]["partial_token_usage"] == {"input_tokens": 10}
        assert value["transport"]["logical_categories"]["by_category"] == {"normal_generation": 1, "structural_correction": 1, "semantic_repair_generation": 1}
        assert value["transport"]["native_process_starts"] == 4 and value["transport"]["http_attempts"] is None
        assert value["timing"]["controller_wall_seconds"] == 60 and len(value["timing"]["component_records"]) == 3
        assertions.append("All six coverage states, cutoff denominator, DOE declarations and raw comparison count preserved")
        assertions.append("Transport retries deduplicate logical identity; partial/unknown usage remains separate and cache is not added twice")
        assertions.append("Nested component intervals are retained individually; analysis and replay remain separate")
        (run / "metrics.json").unlink()
        (run / "component-timing.json").unlink()
        value = module.extract("ga4")
        assert value["transport"] is None and value["timing"]["component_records"] is None
        assertions.append("Missing cost and timing artifacts stay null, not zero")
        write(verify / "prepared-runs.json", {"run_order": [{"case_id": "ga4", "run_directory": str(root / "some-other-run")}]})
        try:
            module.extract("ga4")
        except ValueError as error:
            assert "exact authorized" in str(error)
        else:
            raise AssertionError("Wrong run accepted")
        assertions.append("Public entry rejects a different run even if case ID matches")
    # Read old closed JSON only; never call analysis, loader, replay or a process.
    old = []
    expected = {"ga4": (420, 29, 0), "001": (13, 2, 1), "010": (23, 19, 0), "013": (26, 15, 4)}
    for case, (total, processed, comparisons) in expected.items():
        tag = "20261101-214322" if case == "ga4" else "20261101-214748"
        run = PROJECT / "experiments/doe/runs" / f"document-guided-{case}-general-loops-high-v8-{tag}"
        value = module._summarize_closed(run)
        actual = value["propagation"]["generated_ir"]
        assert (actual["total"], actual["by_status"]["processed"], value["doe"]["comparisons"]) == (total, processed, comparisons)
        assert not value["warnings"], value["warnings"]
        for name, digest in value["evidence_sha256"].items():
            assert hashlib.sha256((run / name).read_bytes()).hexdigest() == digest
        old.append({"case": case, "generated_ir": total, "processed": processed, "engine_comparisons": comparisons,
                    "read_artifacts_unchanged": True})
    receipt = {"status": "passed", "assertion_groups": assertions, "old_closed_json_checks": old,
               "model_calls": 0, "process_launches": 0, "replays": 0, "live_answers_read": False,
               "extractor_sha256": hashlib.sha256((HERE / "extract_closed_metrics.py").read_bytes()).hexdigest()}
    write(HERE / "closed-metrics-validation.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    check()
