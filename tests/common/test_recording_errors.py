"""Record finalization cannot hide an error or permit another request."""
import pytest

from skillflow.common import audit_execution
from skillflow.common.artifact_io import ArtifactWriteError
from skillflow.common.recording_errors import finalize_record


def test_user_interrupt_survives_failed_final_record():
    primary = KeyboardInterrupt("user stopped")
    record = {}

    def fail():
        raise ArtifactWriteError(None, "callback", PermissionError("busy"))

    with pytest.raises(KeyboardInterrupt) as raised:
        try:
            raise primary
        finally:
            finalize_record(fail, primary, record)
    assert raised.value is primary
    assert record["recording_failed"] is True
    assert record["recording_errors"][0]["error_type"] == "ArtifactWriteError"


@pytest.mark.parametrize("eligible", [False, True])
def test_failed_retry_decision_save_preserves_first_error_and_never_resends(tmp_path, monkeypatch, eligible):
    primary = TimeoutError("original request timed out")
    (tmp_path / "call.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(audit_execution, "classify_failure", lambda *args: {
        "eligible": eligible, "category": "temporary_connection" if eligible else "non_retryable_execution_error",
    })
    executions = []

    def execute(prompt):
        executions.append(prompt)
        raise primary

    def fail_persist(*args):
        raise ArtifactWriteError(None, "callback", PermissionError("decision file busy"))

    client = audit_execution.RetryingAuditClient(
        execute=execute, retries=2, call_path=lambda _: (tmp_path, "a001"), persist=fail_persist,
        wait_for_retry=lambda *args: pytest.fail("No retry without a saved decision"),
        notify=lambda *args: pytest.fail("No continuation without a saved decision"),
    )
    with pytest.raises(TimeoutError) as raised:
        client.complete("exact input")
    assert raised.value is primary
    assert primary.recording_failed is True
    assert primary.recording_errors[0]["error_type"] == "ArtifactWriteError"
    assert executions == ["exact input"]


def test_successful_call_still_fails_if_success_decision_cannot_be_saved(tmp_path):
    executions = []

    def execute(prompt):
        executions.append(prompt)
        return "complete response"

    def fail_persist(*args):
        raise ArtifactWriteError(None, "callback", PermissionError("decision file busy"))

    client = audit_execution.RetryingAuditClient(
        execute=execute, retries=2, call_path=lambda _: (tmp_path, "a001"), persist=fail_persist,
        wait_for_retry=lambda *args: pytest.fail("Must not retry accepted response"),
    )
    with pytest.raises(ArtifactWriteError):
        client.complete("exact input")
    assert executions == ["exact input"]
