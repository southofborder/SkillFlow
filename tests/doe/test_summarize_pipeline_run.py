"""Metrics are derived from recorded requests, not provider calls or estimates."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket

import pytest

from skillflow.common.recording import canonical_sha256
from tools.doe import summarize_pipeline_run as metrics


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *_a, **_kw: pytest.fail("Metrics used network"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def seal(value):
    return {**value, "record_sha256": canonical_sha256(value)}


USAGE = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
         "completion_tokens_details": {"reasoning_tokens": 15},
         "prompt_cache_hit_tokens": 4, "prompt_cache_miss_tokens": 6}


def add_call(root, stage, *, index=1, usages=None, normalized=False, observed=True):
    relative, prefix = metrics.STAGES[stage]
    target = root / "cases/001" / relative / "calls" / prefix / f"a{index:03}"
    target.mkdir(parents=True, exist_ok=True)
    write(target / "call.json", {"started_at": "2026-10-15T00:00:00+00:00",
          "finished_at": "2026-10-15T00:00:05+00:00", "status": "complete"})
    write(target / "request.json", {"index": index, "kind": "structural_correction" if index > 1 else "base"})
    write(target / "validation.json", {"status": "valid", "normalization_sha256": "normal" if normalized else None})
    if normalized:
        write(target / "normalization.json", {"audit": "exact repair receipt"})
    (target / "prompt.txt").write_bytes("校准\r\nquery".encode("utf-8"))
    usages = [deepcopy(USAGE)] if usages is None else usages
    attempts = [{"status": "complete" if usage else "execution_error", "http_status": 200,
                "usage": usage, "returned_model": "test-model", "elapsed_seconds": 2,
                "stream": {"received_bytes": 10}} for usage in usages]
    trace = {"http_attempts_observed": observed, "http_attempts": attempts,
             "usage": deepcopy(USAGE), "elapsed_seconds": 4}
    write(target / "transport.json", [seal(trace)])
    return target


def finish(root, *, calls, corrections=0, http=None, retries=0, normalizations=0):
    counts = {"logical_calls": calls, "structural_corrections": corrections,
              "http_attempts": calls if http is None else http, "http_retries": retries,
              "json_normalizations": normalizations}
    result = {"status": "complete", "counts": counts,
              "task": {"status": "complete"}, "selected_annotation": {"path": "annotation"}}
    write(root / "cases/001/result.json", result)
    write(root / "manifest.json", {"cases": {"001": {} }})
    write(root / "summary.json", {"cases": {"001": result}, "not_started": []})
    terminal = datetime(2026, 10, 15, 0, 1, tzinfo=timezone.utc).timestamp()
    for path in (root / "cases/001/result.json", root / "summary.json"):
        os.utime(path, (terminal, terminal))


@pytest.mark.parametrize("stages,count,route", [
    (["task_extraction", "annotation", "initial_review"], 3, "none"),
    (["task_extraction", "annotation", "initial_review", "annotation_repair", "final_review"], 5, "fixed_task_annotation_repair"),
    (list(metrics.STAGES), 6, "task_revision_and_reannotation"),
])
def test_actual_three_five_six_paths_without_api(tmp_path, stages, count, route):
    for stage in stages:
        add_call(tmp_path, stage)
    finish(tmp_path, calls=count)
    result = metrics.collect(tmp_path, final=True)
    assert result["totals"]["logical_calls"] == count
    assert result["totals"]["stage_initial_requests"] == count
    assert result["cases"]["001"]["repair_route"] == route
    assert result["cases"]["001"]["pipeline_counts_match_observed"] is True
    assert result["totals"]["token_usage"]["total_tokens"]["total"] == 30 * count
    repaired = [call for call in result["calls"] if call["stage"] == "annotation_repair"]
    if repaired:
        assert repaired[0]["semantic_role"] == ("new_task_reannotation" if count == 6 else "fixed_task_semantic_repair")


def test_usage_once_and_missing_unknown_not_zero(tmp_path):
    add_call(tmp_path, "annotation", usages=[None, deepcopy(USAGE)])
    finish(tmp_path, calls=1, http=2, retries=1)
    result = metrics.collect(tmp_path, final=True)
    totals = result["totals"]
    usage = totals["token_usage"]
    assert usage["total_tokens"] == {"total": None, "reported_subtotal": 30, "attempts_with_value": 1, "attempts_missing_value": 1}
    assert usage["api_reported_fields"]["completion_tokens_details.reasoning_tokens"]["reported_subtotal"] == 15
    assert usage["api_reported_fields"]["prompt_cache_hit_tokens"]["reported_subtotal"] == 4
    assert totals["http_retries"] == 1
    assert totals["prompt_input_size"]["characters"] == len("校准\r\nquery")
    assert totals["prompt_input_size"]["utf8_bytes"] == len("校准\r\nquery".encode("utf-8"))
    assert totals["call_wall_seconds"]["total"] == 5
    assert totals["transport_call_seconds"]["total"] == 4
    assert totals["http_seconds"]["total"] == 4


def test_structural_chain_and_normalization_are_not_extra_semantic_rounds(tmp_path):
    add_call(tmp_path, "annotation")
    add_call(tmp_path, "annotation", index=2, normalized=True)
    finish(tmp_path, calls=2, corrections=1, normalizations=1)
    result = metrics.collect(tmp_path, final=True)
    assert result["totals"]["stage_initial_requests"] == 1
    assert result["totals"]["structural_corrections"] == 1
    assert result["totals"]["json_normalizations"] == 1
    assert result["totals"]["semantic_repair_requests"] == 0


def test_final_times_and_call_inventory_survive_replay(tmp_path):
    call = add_call(tmp_path, "task_extraction")
    finish(tmp_path, calls=1)
    start = "2026-10-14T23:59:50+00:00"
    initial = metrics.write_metrics(tmp_path, final=True, online_start=start)
    frozen = initial["frozen_call_files"]
    for path in (tmp_path / "cases/001/result.json", tmp_path / "summary.json"):
        os.utime(path, None)
    write(tmp_path / "replay-summary.json", {"api_calls": 0, "history_unchanged": True,
          "cases": {"001": {"status": "complete"}}})
    replayed = metrics.write_metrics(tmp_path, final=True)
    assert replayed["online_timing"] == initial["online_timing"]
    assert replayed["cases"]["001"]["online_timing"] == initial["cases"]["001"]["online_timing"]
    assert replayed["frozen_call_files"] == frozen
    assert replayed["zero_api_replay"]["call_files_unchanged"] is True
    assert replayed["online_timing"]["elapsed_seconds"] == 70
    (call / "response.txt").write_text("tampered new response", encoding="utf-8")
    with pytest.raises(ValueError, match="call files changed"):
        metrics.write_metrics(tmp_path, final=True)
    assert metrics.read(tmp_path / "metrics.json")["frozen_call_files"] == frozen


def test_clock_cannot_be_silently_changed(tmp_path):
    add_call(tmp_path, "task_extraction")
    finish(tmp_path, calls=1)
    metrics.write_metrics(tmp_path, final=True, online_start="2026-10-15T00:00:00+00:00")
    with pytest.raises(ValueError, match="start differs"):
        metrics.collect(tmp_path, online_start="2026-10-15T00:00:01+00:00")


def test_injected_http_parameters_unobservable_stay_unknown(tmp_path):
    add_call(tmp_path, "annotation", usages=[], observed=False)
    finish(tmp_path, calls=1, http=0)
    result = metrics.collect(tmp_path, final=True)
    assert result["totals"]["http_attempts"] == 0
    assert result["calls"][0]["http_attempts_observed"] is False
    assert result["totals"]["token_usage"]["total_tokens"]["total"] is None


def test_final_rejects_counts_and_transport_tampering(tmp_path):
    call = add_call(tmp_path, "annotation")
    finish(tmp_path, calls=2)
    with pytest.raises(ValueError, match="pipeline counts"):
        metrics.collect(tmp_path, final=True)
    finish(tmp_path, calls=1)
    trace = json.loads((call / "transport.json").read_text())
    trace[0]["elapsed_seconds"] = 900
    write(call / "transport.json", trace)
    with pytest.raises(ValueError, match="integrity"):
        metrics.collect(tmp_path, final=True)


def test_prepared_directory_does_not_imply_a_request(tmp_path):
    (tmp_path / "cases/001/refinement/task-revision").mkdir(parents=True)
    write(tmp_path / "cases/001/refinement/task-revision/manifest.json", {})
    add_call(tmp_path, "task_extraction")
    finish(tmp_path, calls=1)
    result = metrics.collect(tmp_path, final=True)
    assert result["cases"]["001"]["repair_route"] == "none"
    assert result["totals"]["task_revision_requests"] == 0


def test_final_requires_terminal_results_and_cli_has_explicit_run_directory(tmp_path, capsys):
    (tmp_path / "cases/001").mkdir(parents=True)
    write(tmp_path / "manifest.json", {"cases": {"001": {}}})
    with pytest.raises(ValueError, match="terminal"):
        metrics.collect(tmp_path, final=True)
    add_call(tmp_path, "annotation")
    finish(tmp_path, calls=1)
    assert metrics.main(["--run-dir", str(tmp_path), "--final"]) == 0
    assert json.loads(capsys.readouterr().out)["logical_calls"] == 1
    assert "not establish semantic correctness" in (tmp_path / "metrics.md").read_text()
