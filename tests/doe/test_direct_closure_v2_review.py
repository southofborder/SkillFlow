"""Invented closure counterexamples; no live cohort, launch, or semantic review."""
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from tools.doe.real_comparison import direct_closure_v2 as closure
from tools.doe.real_comparison.artifacts import seal_candidate, verify_candidate
from tools.doe.real_comparison.protocol import sha256


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def terminal_run(tmp_path, monkeypatch):
    """Exercise the closure loop with invented outcomes and an offline boundary."""
    run, donor = tmp_path / "remaining", tmp_path / "donor"
    donor.mkdir()
    save(donor / "freeze.json", {})
    save(donor / "output-freeze.json", {"files": {}})
    save(run / "freeze.json", {})
    save(run / "controller-finished.json", {"finished_at": "2026-10-24T12:30:00Z"})
    save(run / "dispatch-stop.json", {"automatic_retry": False})
    rows = [{"workflow_id": f"invented-{index:03d}",
             "kind": "main" if index < 144 else "review",
             "method": "audit" if index % 2 else "chain"}
            for index in range(192)]
    lineage = {"donor_run": str(donor), "retained_workflows": [],
               "new_workflow_ids": [row["workflow_id"] for row in rows],
               "donor_output_freeze_sha256": sha256(donor / "output-freeze.json"),
               "donor_input_freeze_sha256": sha256(donor / "freeze.json")}
    save(run / "remaining-output-lineage.json", lineage)
    for item in rows:
        save(run / "workflows" / item["workflow_id"] / "result.json",
             {"workflow_id": item["workflow_id"], "status": "protocol_aborted", "attempts": 0})
    original_driver, original_base = closure.driver, closure.base
    monkeypatch.setattr(closure, "driver", SimpleNamespace(
        verify=lambda *args, **kwargs: {}, require=original_driver.require,
        read=original_driver.read, verify_donor=lambda path: {"files": {}}))
    monkeypatch.setattr(closure, "base", SimpleNamespace(
        planned=lambda path: deepcopy(rows), requests=original_base.requests,
        usage=lambda path: {}, verify_candidate=verify_candidate))
    reports = {}
    monkeypatch.setattr(closure, "inspect_new_request", lambda run, item, query, manifest:
                        {"request": query.relative_to(run).as_posix(),
                         "accepted": reports.get(query.name, False), "usage_known": False,
                         "session_id": query.name, "response_ids": []})
    return run, rows[0]["workflow_id"], reports


def launched(terminal_run, *, accepted=False, name="q001"):
    run, wid, reports = terminal_run
    request = run / "workflows" / wid / "requests" / name
    save(request / "cli/process-start.json", {"actual_cli_process_started": True})
    save(run / "workflows" / wid / "result.json",
         {"workflow_id": wid, "status": "failed", "attempts": 1})
    reports[name] = accepted
    return request


def test_closure_uses_private_new_transport_without_changing_old_inspector():
    original = closure.previous.inspect_new_request
    clone = closure.inspect_new_request
    assert clone.__code__ is original.__code__
    assert clone.__globals__ is not original.__globals__
    assert clone.__globals__["base"].cli is closure.driver.transport
    assert original.__globals__["base"].cli is not closure.driver.transport


def test_stopped_no_launch_scope_remains_terminal_and_zero_call(terminal_run):
    run, _, _ = terminal_run
    report = closure.verify(run)
    assert report["model_calls"] == 0
    assert report["actual_starts_including_imports"] == 0
    assert report["terminal_statuses"] == {"protocol_aborted": 192}


def test_extra_unplanned_workflow_cannot_enter_a_closure_seal(terminal_run):
    run, _, _ = terminal_run
    save(run / "workflows/unplanned/result.json", {"status": "complete"})
    with pytest.raises(ValueError):
        closure.verify(run)


def test_retained_global_stop_is_required_for_this_closure(terminal_run):
    run, _, _ = terminal_run
    (run / "dispatch-stop.json").unlink()
    with pytest.raises(ValueError):
        closure.verify(run)


def test_rejected_saved_request_remains_failed_and_usage_unknown(terminal_run):
    run, _, _ = terminal_run
    launched(terminal_run)
    report = closure.verify(run)
    assert report["new_actual_starts"] == 1
    assert report["terminal_statuses"]["failed"] == 1
    assert report["request_reports"][0]["accepted"] is False
    assert report["request_reports"][0]["usage_known"] is False


def test_failed_outcome_cannot_hide_unexplained_accepted_delivery(terminal_run):
    run, _, _ = terminal_run
    launched(terminal_run, accepted=True)
    with pytest.raises(ValueError):
        closure.verify(run)


def test_accepted_delivery_with_retained_seal_failure_stays_failed(terminal_run):
    run, wid, _ = terminal_run
    launched(terminal_run, accepted=True)
    save(run / "workflows" / wid / "result.json",
         {"workflow_id": wid, "status": "failed", "attempts": 1,
          "candidate_seal_error": "Invented retained candidate integrity failure"})
    report = closure.verify(run)
    assert report["terminal_statuses"]["failed"] == 1
    assert report["request_reports"][0]["accepted"] is True


@pytest.mark.parametrize("defect", ["replacement_name", "second_request"])
def test_launched_failed_direct_outcome_preserves_its_single_q001(terminal_run, defect):
    run, _, _ = terminal_run
    launched(terminal_run, name="q002" if defect == "replacement_name" else "q001")
    if defect == "second_request":
        launched(terminal_run, name="q002")
    with pytest.raises(ValueError):
        closure.verify(run)


@pytest.mark.parametrize("field", ["artifact_manifest_sha256", "candidate_view_sha256"])
def test_complete_result_must_bind_actual_candidate_seal(terminal_run, field):
    run, wid, _ = terminal_run
    request = launched(terminal_run, accepted=True)
    directory = run / "workflows" / wid
    for answer in (directory / "answer.txt", request / "answer.txt"):
        answer.write_bytes(b"Invented English answer with original quotation: \xe5\x8e\x9f\xe6\x96\x87\r\n")
    result = {"workflow_id": wid, "status": "complete", "attempts": 1,
              "answer_sha256": sha256(request / "answer.txt"), **seal_candidate(run, wid)}
    result[field] = "0" * 64
    save(directory / "result.json", result)
    with pytest.raises(ValueError):
        closure.verify(run)


def test_complete_result_accepts_original_seal_and_newline_rendering(terminal_run):
    run, wid, _ = terminal_run
    request = launched(terminal_run, accepted=True)
    directory = run / "workflows" / wid
    for answer in (directory / "answer.txt", request / "answer.txt"):
        answer.write_bytes(b"Invented English answer\r\n")
    result = {"workflow_id": wid, "status": "complete", "attempts": 1,
              "answer_sha256": sha256(request / "answer.txt"), **seal_candidate(run, wid)}
    save(directory / "result.json", result)
    report = closure.verify(run)
    assert report["terminal_statuses"]["complete"] == 1
    assert report["request_reports"][0]["accepted"] is True
