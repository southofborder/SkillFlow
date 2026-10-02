import importlib.util
import json
from pathlib import Path

import pytest

from skill_ir.experiments.resumable import _exclusive_run


BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
SPEC = importlib.util.spec_from_file_location("reconcile_interrupted", BASE / "tools/reconcile_interrupted.py")
reconciler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reconciler)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def interrupted_run(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Offline reconciliation must never load credentials, run extraction, or send a request")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    monkeypatch.setattr("skill_ir.llm.config.load_environment", forbidden)
    monkeypatch.setattr("skill_ir.experiments.resumable.analyze_skill", forbidden)
    monkeypatch.setattr("skill_ir.llm.client.LlmClient.complete", forbidden)
    samples = reconciler.read(BASE / "frozen/corpus/corpus.json")["samples"]
    run = tmp_path / "run"
    write(run / "experiment.json", {
        "cases": [{"id": sample["id"], "split": sample["split"]} for sample in samples],
        "variants": [{"id": "sol-max"}], "repetitions": 3,
    })
    trials = []
    for sample in samples:
        for repetition in (1, 2, 3):
            artifacts = f"trials/{sample['id']}/sol-max/{repetition}"
            record = {
                "case": sample["id"], "variant": "sol-max", "repetition": repetition,
                "split": sample["split"], "artifacts": artifacts,
                "status": "running" if len(trials) < 4 else "not_run",
                "semantic_review_status": "pending_joint_review",
            }
            write(run / artifacts / "record.json", record)
            if record["status"] == "running":
                write(run / artifacts / "trace.json", {"calls": [{
                    "status": "running", "prompt": "synthetic prompt", "response": None,
                    "http_attempts": [
                        {"status": "error", "http_status": 524, "error": "HTTP 524"},
                        {"status": "error", "http_status": None, "error": "The read operation timed out"},
                        {"status": "running", "http_status": None},
                    ],
                }]})
            trials.append(record)
    write(run / "report.json", {"status": "running", "mode": "online", "trials": trials})
    return run


def test_offline_reconciliation_preserves_all_90_records_and_exact_trace_bytes(interrupted_run):
    run = interrupted_run
    traces = {path: path.read_bytes() for path in run.rglob("trace.json")}
    pending = {
        path: path.read_bytes() for path in run.rglob("record.json")
        if reconciler.read(path)["status"] == "not_run"
    }
    report = reconciler.reconcile(run, reason="Operator stopped the process after repeated timeouts.")
    assert report["status"] == "needs_attention"
    assert report["reconciliation"]["trial_status_counts"] == {"uncertain": 4, "not_run": 86}
    assert report["summary"]["planned"] == 90
    assert report["summary"]["generation_attempts"] == 4
    assert report["summary"]["repair_attempts"] == 0
    assert report["summary"]["http_attempts"] == 12
    assert report["summary"]["http_retries"] == 8
    assert report["summary"]["usage_records"] == 0
    assert report["summary"]["known_token_usage"] == {
        "input_tokens": None, "output_tokens": None, "total_tokens": None
    }
    assert report["reconciliation"]["http_outcome_counts"] == {"error": 8, "unknown_after_interruption": 4}
    assert report["reconciliation"]["network_requests_sent_by_reconciler"] == 0
    assert report["interruption"]["occurred_at"] is None
    assert report["interruption"]["observed_at"] == report["reconciliation"]["reconciled_at"]
    assert all(path.read_bytes() == data for path, data in {**traces, **pending}.items())
    for record in report["trials"][:4]:
        trace = run / record["artifacts"] / "trace.json"
        assert record["artifact_sha256"]["trace.json"] == reconciler.sha(trace)
        assert record["semantic_review_status"] == "pending_joint_review"


def test_reconciliation_is_idempotent_without_resending_or_rewriting_trace(interrupted_run):
    run = interrupted_run
    first = reconciler.reconcile(run, reason="Operator stopped the process.")
    before = {path: path.read_bytes() for path in run.rglob("*") if path.is_file()}
    second = reconciler.reconcile(run, reason="Operator stopped the process.")
    assert first == second
    assert all(path.read_bytes() == content for path, content in before.items())


def test_operator_timestamp_is_preserved_as_actual_time_when_explicit(interrupted_run):
    result = reconciler.reconcile(
        interrupted_run, reason="Operator stopped the process.",
        interrupted_at="2026-09-10T17:30:00+08:00",
    )
    assert result["interruption"]["occurred_at"] == "2026-09-10T09:30:00+00:00"


def test_live_runner_lock_blocks_reconciliation(interrupted_run):
    with _exclusive_run(interrupted_run):
        with pytest.raises(ValueError, match="Another runner"):
            reconciler.reconcile(interrupted_run, reason="Attempt while running.")


def test_missing_record_rejects_before_changing_any_trial(interrupted_run):
    run = interrupted_run
    final = reconciler.read(run / "report.json")["trials"][-1]
    (run / final["artifacts"] / "record.json").unlink()
    before = {path: path.read_bytes() for path in run.rglob("*.json")}
    with pytest.raises(ValueError, match="Missing durable trial"):
        reconciler.reconcile(run, reason="Operator stopped the process.")
    assert all(path.read_bytes() == content for path, content in before.items())


def test_incomplete_trial_inventory_is_rejected(interrupted_run):
    run = interrupted_run
    report = reconciler.read(run / "report.json")
    report["trials"].pop()
    write(run / "report.json", report)
    with pytest.raises(ValueError, match="90 unique trial"):
        reconciler.reconcile(run, reason="Operator stopped the process.")
