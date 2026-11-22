"""Fatal request replay follows bound observations, not a second worker race."""
from copy import deepcopy
from threading import Event

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.online import read, file_reference
from skillflow.document_guided.fatal_frontier import PATH
from tests.document_guided.test_parallel_runner import freeze_producer
from tests.document_guided.test_repair_request_failure import RequestFailureHarness


@pytest.fixture(autouse=True)
def offline_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


def controlled_run(tmp_path, monkeypatch, *, failed_stage="revision/task", sibling_first=True, zero_call_sibling=False):
    from skillflow.task import runner as task_runner
    sibling = "revision-graph" if failed_stage == "revision/task" else "revision/task"
    ready, observed, failed = Event(), Event(), Event()
    actual_step, actual_task = runner.run_step, task_runner.run_task

    def step(owner, **kwargs):
        if owner.name == "revision-processing" and zero_call_sibling and not kwargs.get("replay"):
            ready.set()
            assert kwargs["stop_event"].wait(10), "Fatal stage did not cancel its already-prepared sibling"
        value = actual_step(owner, **kwargs)
        if owner.name == sibling and not sibling_first and not kwargs.get("replay"):
            ready.set()
            assert failed.wait(10), "The primary failure was not observed"
        return value

    def task(owner, **kwargs):
        value = actual_task(owner, **kwargs)
        if owner.name == "task" and owner.parent.name == "revision" and sibling == "revision/task" and not sibling_first and not kwargs.get("replay"):
            ready.set()
            assert failed.wait(10), "The primary failure was not observed"
        return value

    monkeypatch.setattr(runner, "run_step", step)
    monkeypatch.setattr(task_runner, "run_task", task)

    class OrderedHarness(RequestFailureHarness):
        def complete(self, stage, prompt):
            if stage == failed_stage:
                gate = ready if zero_call_sibling or not sibling_first else observed
                assert gate.wait(10), "The requested deterministic completion order was not reached"
            return super().complete(stage, prompt)

    harness = OrderedHarness(tmp_path / "run", domains=("task", "cfg"), annotation_failure=True, failed_stage=failed_stage)
    harness.prepare(tmp_path / "package")

    def progress(state):
        if state["stage"] == sibling and state["stages"][sibling]["status"] == "complete":
            observed.set()
        if state["stage"] == failed_stage and state["stages"][failed_stage]["status"] == "failed":
            failed.set()

    result = runner.run(harness.directory, client_factory=harness.factory, progress=progress)
    assert result["status"] == "failed" and result["selected_annotation"] is None, result
    assert result["stage"] == failed_stage and result["repair_used"]
    assert result["stages"][failed_stage]["status"] == "failed"
    assert "fatal_frontier" in result
    return harness, result, sibling


@pytest.mark.parametrize("failed_stage", ["revision/task", "revision-processing"])
@pytest.mark.parametrize("sibling_first", [True, False])
def test_both_completion_orders_preserve_exact_fatal_frontier(tmp_path, monkeypatch, failed_stage, sibling_first):
    harness, result, sibling = controlled_run(tmp_path, monkeypatch, failed_stage=failed_stage, sibling_first=sibling_first)
    assert result["stages"][sibling]["status"] == ("complete" if sibling_first else "aborted")
    before = {str(path.relative_to(harness.directory)): path.read_bytes() for path in harness.directory.rglob("call.json")}
    calls = len(harness.calls)
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == calls
    assert before == {str(path.relative_to(harness.directory)): path.read_bytes() for path in harness.directory.rglob("call.json")}
    assert not (harness.directory / "propagation").exists() and not (harness.directory / "doe").exists()


def test_prepared_zero_call_interrupted_sibling_is_verified(tmp_path, monkeypatch):
    harness, result, _ = controlled_run(tmp_path, monkeypatch, zero_call_sibling=True)
    sibling = harness.directory / "steps/revision-processing"
    assert read(sibling / "result.json")["status"] == "interrupted"
    assert not list((sibling / "calls").glob("a*/call.json"))
    receipt = read(harness.directory / PATH)
    assert "revision-processing" in receipt["owners"]
    assert runner.replay(harness.directory) == result


@pytest.mark.parametrize("mutation", ["missing_journal", "missing_reference", "missing_both", "missing_owner",
    "missing_transport", "changed_result", "rebound_reason", "rebound_sibling_status", "rebound_unknown_aborted"])
def test_frontier_missing_or_tampered_evidence_is_rejected(tmp_path, monkeypatch, mutation):
    harness, result, sibling = controlled_run(tmp_path, monkeypatch, failed_stage="revision-processing")
    run = harness.directory
    receipt = read(run / PATH)
    changed = deepcopy(result)
    if mutation in {"missing_journal", "missing_both"}:
        (run / PATH).unlink()
    if mutation in {"missing_reference", "missing_both"}:
        changed.pop("fatal_frontier")
    if mutation == "missing_owner":
        (run / "revision/task/manifest.json").unlink()
    if mutation == "missing_transport":
        (run / "steps/revision-processing/calls/a001/transport.json").unlink()
    if mutation == "changed_result":
        changed["stages"][sibling] = {"status": "aborted", "reason": changed["reason"]}
    if mutation == "rebound_reason":
        receipt["guided_state"]["reason"] = changed["reason"] = "ModelRequestFailure: forged reason"
        receipt["guided_state"]["stages"][changed["stage"]]["reason"] = changed["stages"][changed["stage"]]["reason"] = changed["reason"]
    if mutation == "rebound_sibling_status":
        receipt["guided_state"]["stages"][sibling] = changed["stages"][sibling] = {"status": "partial"}
    if mutation == "rebound_unknown_aborted":
        receipt["guided_state"]["stages"]["invented-stage"] = changed["stages"]["invented-stage"] = {
            "status": "aborted", "reason": changed["reason"]}
    if mutation.startswith("rebound_"):
        runner.WRITER.json(run / PATH, receipt)
        changed["fatal_frontier"] = file_reference(run, run / PATH)
    runner.WRITER.json(run / "result.json", changed)
    with pytest.raises(ValueError):
        runner.replay(run)


def test_recording_failure_stays_failed_without_frontier(tmp_path):
    from skillflow.common.llm.request_errors import ModelRequestFailure
    def failed_recording(message):
        error = ModelRequestFailure(message)
        error.recording_failed = True
        error.recording_errors = [{"error_type": "OSError", "error": "Injected record failure"}]
        return error
    harness = RequestFailureHarness(tmp_path / "run", failed_stage="processing", error_type=failed_recording)
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["stages"]["processing"]["status"] == "failed"
    assert "fatal_frontier" not in result and "fatal_frontier_error" not in result
    assert read(harness.directory / "result.json")["status"] == "failed"


def test_frontier_capture_failure_preserves_primary_terminal_result(tmp_path, monkeypatch):
    actual = runner.WRITER.json
    def reject_frontier(path, value):
        if path.name == "fatal-semantic-frontier.json":
            raise OSError("Injected frontier persistence failure")
        return actual(path, value)
    monkeypatch.setattr(runner.WRITER, "json", reject_frontier)
    harness = RequestFailureHarness(tmp_path / "run", failed_stage="processing")
    harness.prepare(tmp_path / "package")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["reason"].startswith("ModelRequestFailure:")
    assert result["fatal_frontier_error"] == "OSError: Injected frontier persistence failure"
    assert read(harness.directory / "result.json") == result
    with pytest.raises(ValueError, match="lacks a complete fatal frontier"):
        runner.replay(harness.directory)
