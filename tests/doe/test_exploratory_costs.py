"""Synthetic accounting checks; no real target, model or semantic report access."""
import csv
import hashlib
import json
from pathlib import Path

import pytest

from tools.doe.real_comparison import exploratory_costs as costs


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def counters(total=150):
    return dict(input_tokens=100, cached_input_tokens=60, cache_write_input_tokens=0,
                output_tokens=50, reasoning_output_tokens=40, total_tokens=total)


def schedule():
    main = [dict(workflow_id=f"c{case:02d}_{method}_r{repeat}", case_id=f"c{case:02d}", method=method,
                 repeat=repeat, kind="main") for case in range(24) for method in ("skillflow", "audit", "chain") for repeat in (1, 2, 3)]
    reviews = [dict(workflow_id=f"c{case:02d}_{method}_review", original_workflow_id=f"c{case:02d}_{method}_r1",
                    case_id=f"c{case:02d}", method=method, repeat=1, kind="review")
               for case in range(24) for method in ("audit", "chain")]
    return dict(main=main, reviews=reviews)


def request(run, workflow, name="q001", *, usage=None, accepted=True, started=True, dispatch=True, verified=True):
    directory = run / "workflows" / workflow / "requests" / name
    put(directory / "request.json", {"workflow_id": workflow, "created_at": "2026-10-22T00:00:00Z"})
    if dispatch:
        put(directory / "dispatch.json", {"attempted_at": "2026-10-22T00:00:02Z", "retries": 0})
    if started:
        put(directory / "cli/process-start.json", {"actual_cli_process_started": True, "started_at": "2026-10-22T00:00:03Z"})
        put(directory / "cli/process-result.json", {"actual_cli_process_started": True, "status": "process_exited", "returncode": 0,
            "supervisor_elapsed_seconds": 8, "finished_at": "2026-10-22T00:00:11Z", "retries": 0})
    if usage is not None:
        put(directory / "receipt.json", {"usage": {"by_response_id": usage}, "usage_verified": verified,
            "cli_session_id": "synthetic-session", "timing": {"duration_ms": 6000, "time_to_first_token_ms": 1000},
            "protocol_status": "conformant", "raw_receipt_path": "synthetic-archive.jsonl", "raw_receipt_sha256": "ab" * 32,
            "prompt_delivery_audit": {"message": "DO NOT DECODE THIS BODY"}})
        put(directory / "response.json", {"accepted": accepted, "imported_at": "2026-10-22T00:00:12Z"})
    if not accepted:
        put(directory / "failure.json", {"failed_at": "2026-10-22T00:00:13Z", "reason": "Do not export semantic failure text", "automatic_retry": False})
    return directory


def seal(run):
    hashes = {path.relative_to(run).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in (run / "workflows").rglob("*") if path.is_file()}
    put(run / "output-freeze.json", {"planned_outputs": 264, "closed_at": "2026-10-22T01:00:00Z", "files": hashes})
    put(run / "freeze.json", {"files": {"schedule.json": hashlib.sha256((run / "schedule.json").read_bytes()).hexdigest()}})


@pytest.fixture
def run(tmp_path):
    run = tmp_path / "run"
    plan = schedule()
    put(run / "schedule.json", plan)
    for item in plan["main"] + plan["reviews"]:
        workflow = run / "workflows" / item["workflow_id"]
        put(workflow / "state.json", {"started_at": "2026-10-22T00:00:00Z"})
        put(workflow / "result.json", {"workflow_id": item["workflow_id"], "status": "failed",
            "finished_at": "2026-10-22T00:00:20Z", "native": {"semantic_secret": "DO NOT DECODE THIS BODY"},
            "reason": "DO NOT DECODE THIS BODY", "timing": {"workflow_elapsed_seconds": 15,
                "cli_wait_seconds": 11, "local_processing_seconds": 4, "schedule_wait_seconds": 8}})
    return run


def test_metadata_projection_does_not_decode_unselected_bodies(tmp_path, monkeypatch):
    path = put(tmp_path / "mixed.json", {"native": {"secret": 'DO NOT DECODE THIS BODY \\" 中文 { [ ]'}, "status": "failed",
        "messages": [{"content": "DO NOT DECODE THIS BODY"}], "timing": {"workflow_elapsed_seconds": 3}})
    original = json.loads

    def guarded(raw, *args, **kwargs):
        assert "DO NOT DECODE THIS BODY" not in raw
        return original(raw, *args, **kwargs)

    monkeypatch.setattr(costs.json, "loads", guarded)
    assert costs.read_metadata(path, ("status", "timing")) == {"status": "failed", "timing": {"workflow_elapsed_seconds": 3}}


@pytest.mark.parametrize("raw", ['{"x":1,"x":2}', '{"x":1} trailing', '{"skip":[1,2}', '{"x" 1}'])
def test_metadata_projection_rejects_malformed_structure(tmp_path, raw):
    path = tmp_path / "bad.json"
    path.write_text(raw, encoding="utf-8")
    with pytest.raises(ValueError):
        costs.read_metadata(path, ("x",))


def test_closure_required_before_any_target_request_read(run, monkeypatch):
    monkeypatch.setattr(costs, "request_rows", lambda _: pytest.fail("Opened requests before closure"))
    with pytest.raises(ValueError, match="264 planned outputs"):
        costs.build_cost_ledger(run)


def test_complete_deduplicated_tokens_do_not_add_cache_or_reasoning():
    rows = [{"request_id": f"q{index}", "workflow_id": "w", "receipt_path": f"p{index}",
             "usage_by_response_id": {"resp-shared": counters()}, "cost_observation_expected": True} for index in (1, 2)]
    usage = costs.summarize_requests(rows)
    assert usage["totals"]["total_tokens"] == 150
    assert usage["totals"]["input_tokens"] == 100
    assert usage["totals"]["output_tokens"] == 50
    assert usage["known_subtotals"]["total_tokens"] == 150
    assert usage["response_count"] == 1
    assert usage["reused_response_ids"] == ["resp-shared"]
    assert len(usage["response_ledger"][0]["source_locations"]) == 2


def test_unknown_failed_request_preserves_known_subtotal(run):
    workflow = "c00_skillflow_r1"
    request(run, workflow, usage={"resp-ok": counters()}, accepted=True)
    request(run, workflow, "q002", accepted=False)
    seal(run)
    ledger = costs.build_cost_ledger(run)
    usage = ledger["target_usage"]
    assert usage["totals"]["total_tokens"] is None
    assert usage["known_subtotals"]["total_tokens"] == 150
    assert usage["unknown_request_count"] == 1
    assert len(ledger["requests"]) == 2
    assert ledger["requests"][1]["failure_recorded"] is True
    assert ledger["requests"][1]["usage_verified"] is False
    assert ledger["workflow_summary"]["statuses"]["failed"] == 264


def test_conflicting_identity_is_not_arbitrarily_resolved():
    rows = [{"request_id": f"q{i}", "usage_by_response_id": {"conflict": counters(total)}} for i, total in ((1, 150), (2, 151))]
    rows.append({"request_id": "q3", "usage_by_response_id": {"known": counters(200)}})
    summary = costs.summarize_requests(rows)
    assert summary["totals"]["total_tokens"] is None
    assert summary["known_subtotals"]["total_tokens"] == 200
    assert summary["unknown_response_counts"]["total_tokens"] == 1
    response = next(row for row in summary["response_ledger"] if row["response_id"] == "conflict")
    assert response["counters"]["total_tokens"] is None
    assert len(response["reported_counter_variants"]) == 2


def test_missing_details_and_invalid_counters_stay_unknown():
    row = counters()
    row.update(cached_input_tokens=None, reasoning_output_tokens=True, total_tokens=-1)
    summary = costs.summarize_requests([{"request_id": "q", "usage_by_response_id": {"partial": row}}])
    assert summary["totals"]["input_tokens"] == 100
    assert summary["totals"]["cached_input_tokens"] is None
    assert summary["totals"]["reasoning_output_tokens"] is None
    assert summary["totals"]["total_tokens"] is None
    assert summary["known_subtotals"]["total_tokens"] is None


def test_prelaunch_failure_zero_differs_from_unknown_start(run):
    directory = request(run, "c00_audit_r1", accepted=False, started=False)
    put(directory / "cli/process-result.json", {"actual_cli_process_started": False, "status": "launch_failed"})
    rows = costs.request_rows(run)
    assert costs.summarize_requests(rows)["totals"]["total_tokens"] == 0
    request(run, "c00_chain_r1", accepted=False, started=False)
    rows = costs.request_rows(run)
    assert costs.summarize_requests(rows)["totals"]["total_tokens"] is None
    assert rows[1]["actual_cli_process_start_unknown"] is True


def test_zero_response_verified_flag_cannot_make_started_process_free(run):
    request(run, "c00_audit_r1", usage={}, verified=True)
    rows = costs.request_rows(run)
    assert costs.summarize_requests(rows)["unknown_request_count"] == 1
    assert costs.summarize_requests(rows)["totals"]["total_tokens"] is None


def test_all_planned_rows_enhanced_costs_and_timing_are_separate(run, tmp_path, monkeypatch):
    request(run, "c00_audit_r1", usage={"original": counters()})
    request(run, "c00_audit_review", usage={"review": counters(200)})
    # Duplicate response IDs are charged once even across original and review.
    request(run, "c00_chain_r1", usage={"same": counters()})
    request(run, "c00_chain_review", usage={"same": counters()})
    seal(run)
    original = json.loads

    def guarded(raw, *args, **kwargs):
        assert "DO NOT DECODE THIS BODY" not in raw
        return original(raw, *args, **kwargs)

    monkeypatch.setattr(costs.json, "loads", guarded)
    ledger = costs.build_cost_ledger(run)
    assert len(ledger["workflows"]) == 264
    assert len(ledger["enhanced_original_plus_review_cost"]) == 48
    enhanced = {row["workflow_id"]: row for row in ledger["enhanced_original_plus_review_cost"]}
    assert enhanced["c00_audit_review"]["reported_total_tokens"] == 350
    assert enhanced["c00_chain_review"]["reported_total_tokens"] == 150
    assert enhanced["c00_audit_review"]["additive_workflow_seconds"] == 30
    assert ledger["target_usage"]["totals"]["total_tokens"] == 500
    shared = next(row for row in ledger["workflows"] if row["workflow_id"] == "c00_chain_r1")
    assert shared["usage"]["cost_attribution_ambiguous"] is True
    assert shared["reported_total_tokens"] is None
    assert shared["usage"]["observed_scope_totals"]["total_tokens"] == 150
    call = ledger["requests"][0]
    assert (call["queue_seconds"], call["process_supervision_seconds"], call["receipt_turn_duration_seconds"], call["request_elapsed_seconds"]) == (2, 8, 6, 12)
    assert call["service_response_seconds"] is None
    workflow = next(row for row in ledger["workflows"] if row["workflow_id"] == "c00_audit_r1")
    assert (workflow["workflow_elapsed_seconds"], workflow["cli_wait_seconds"], workflow["local_processing_seconds"], workflow["workflow_wall_span_seconds"]) == (15, 11, 4, 20)
    assert ledger["actual_human_work_seconds"] is None
    out = tmp_path / "cost-artifacts"
    costs.write_cost_ledger(ledger, out)
    with (out / "workflows.csv").open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == 264
    assert (out / "responses.json").is_file()
    assert (out / "responses.csv").is_file()
    assert (out / "summary.json").is_file()
    with pytest.raises(ValueError, match="fresh output"):
        costs.write_cost_ledger(ledger, out)
    with pytest.raises(ValueError, match="outside"):
        costs.write_cost_ledger(ledger, run / "new-costs")


def test_missing_workflow_duration_remains_unknown_even_for_unlaunched_review(run):
    path = run / "workflows/c00_audit_review/result.json"
    put(path, {"workflow_id": "c00_audit_review", "status": "not_reviewable"})
    seal(run)
    ledger = costs.build_cost_ledger(run)
    enhanced = next(row for row in ledger["enhanced_original_plus_review_cost"] if row["workflow_id"] == "c00_audit_review")
    assert enhanced["reported_total_tokens"] == 0
    assert enhanced["additive_workflow_seconds"] is None
    assert ledger["workflow_summary"]["unknown_workflow_elapsed_count"] == 1
    assert ledger["workflow_summary"]["reported_workflow_elapsed_seconds_sum"] is None


@pytest.mark.parametrize("kind", ["terminal", "receipt", "schedule", "deleted_receipt", "deleted_state"])
def test_changed_or_missing_sealed_metadata_rejected(run, kind):
    directory = request(run, "c00_audit_r1", usage={"x": counters()})
    seal(run)
    if kind == "terminal":
        (run / "workflows/c00_audit_r1/result.json").unlink()
    elif kind == "receipt":
        put(directory / "receipt.json", {"usage": {}})
    elif kind == "deleted_receipt":
        (directory / "receipt.json").unlink()
    elif kind == "deleted_state":
        (run / "workflows/c00_audit_r1/state.json").unlink()
    else:
        plan = schedule()
        plan["main"].pop()
        put(run / "schedule.json", plan)
    with pytest.raises(ValueError):
        costs.build_cost_ledger(run)


def test_explicit_supplementary_calibration_and_assistant_capture_never_join_target(run, tmp_path):
    request(run, "c00_audit_r1", usage={"target-response": counters()})
    seal(run)
    calibration = tmp_path / "cc-synthetic"
    request(calibration, "engineering", usage={"calibration-response": counters(200)})
    put(calibration / "workflows/engineering/result.json", {"workflow_id": "engineering", "status": "failed", "timing": {"elapsed_seconds": 9}})
    capture = put(tmp_path / "assistant-capture.json", {"schema_version": "skillflow-preparation-receipt-capture-v2",
        "since": "2026-10-22T00:00:00Z", "captured_at": "2026-10-22T01:00:00Z", "observed": {"by_response_id": {"assistant-response": counters(300)}},
        "response_locations": {"assistant-response": [{"session_id": "exact-thread", "path": "receipt.jsonl", "line": 20}]}})
    ledger = costs.build_cost_ledger(run, supplementary_runs=[("engineering_calibration", calibration)],
        receipt_captures=[("preparation_assistant", capture)])
    assert ledger["target_usage"]["totals"]["total_tokens"] == 150
    extras = ledger["supplementary_costs"]
    assert [row["usage"]["totals"]["total_tokens"] for row in extras] == [200, 300]
    assert all(row["included_in_target_usage"] is False for row in extras)
    assert extras[0]["workflows"][0]["workflow_elapsed_seconds"] == 9
    assert extras[1]["response_locations"]["assistant-response"][0]["session_id"] == "exact-thread"
    assert ledger["combined_study_cost"] is None
    with pytest.raises(ValueError, match="cannot also"):
        costs.build_cost_ledger(run, supplementary_runs=[("historical_probe", run)])


def test_receipt_capture_preserves_conflicts(tmp_path):
    row = {key: None for key in costs.FIELDS}
    capture = put(tmp_path / "conflict.json", {"schema_version": "skillflow-preparation-receipt-capture-v2",
        "observed": {"by_response_id": {"bad": row}, "conflicting_response_ids": ["bad"]},
        "counter_conflicts": {"bad": [counters(150), counters(151)]}})
    record = costs.receipt_capture(capture, "scoring_assistant")
    assert record["usage"]["conflicting_response_ids"] == ["bad"]
    assert record["usage"]["totals"]["total_tokens"] is None
    assert record["actual_human_work_seconds"] is None


def test_empty_assistant_capture_is_unknown_not_free(tmp_path):
    capture = put(tmp_path / "empty.json", {"schema_version": "skillflow-preparation-receipt-capture-v2", "observed": {"by_response_id": {}}})
    record = costs.receipt_capture(capture, "preparation_assistant")
    assert record["usage"]["totals"]["total_tokens"] is None
    assert record["usage"]["known_subtotals"]["total_tokens"] is None
    assert record["usage"]["unknown_request_count"] == 1


def test_response_shared_with_supplementary_work_is_not_allocated_twice(run, tmp_path):
    request(run, "c00_audit_r1", usage={"shared-charge": counters()})
    seal(run)
    capture = put(tmp_path / "shared.json", {"schema_version": "skillflow-preparation-receipt-capture-v2",
        "observed": {"by_response_id": {"shared-charge": counters()}}})
    ledger = costs.build_cost_ledger(run, receipt_captures=[("preparation_assistant", capture)])
    assert ledger["target_usage"]["totals"]["total_tokens"] is None
    assert ledger["target_usage"]["known_subtotals"]["total_tokens"] == 150
    assert ledger["cross_category_response_ids"]["shared-charge"][0]["category"] == "target"
    workflow = next(row for row in ledger["workflows"] if row["workflow_id"] == "c00_audit_r1")
    assert workflow["reported_total_tokens"] is None
    assert ledger["supplementary_costs"][0]["usage"]["totals"]["total_tokens"] is None


def test_no_answer_prompt_raw_session_or_native_stage_opened(run, monkeypatch):
    directory = request(run, "c00_audit_r1", usage={"x": counters()})
    for path in (directory / "answer.txt", directory / "prompt.txt", directory / "cli/stdout.jsonl",
                 run / "workflows/c00_audit_r1/attempts/001/native-report.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("FORBIDDEN", encoding="utf-8")
    seal(run)
    original = Path.open

    def guarded(path, *args, **kwargs):
        assert path.name not in ("answer.txt", "prompt.txt", "stdout.jsonl", "native-report.json")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    assert costs.build_cost_ledger(run)["target_usage"]["totals"]["total_tokens"] == 150
