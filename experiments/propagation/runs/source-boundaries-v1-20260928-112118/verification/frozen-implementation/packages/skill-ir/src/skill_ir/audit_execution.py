"""Conservative retry eligibility from terminal, integrity-checked call records.

This policy does not classify model conclusions or repair responses. An accepted
but demonstrably incomplete transport may start a separately recorded execution;
an uncertain/running request or any complete response may never do so.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from skill_ir.recording import canonical_sha256, read_json, sha_file, validated_trace
from skill_ir.recording_errors import finalize_record


AUDIT_RETRY_POLICY = {
    "version": "audit-transport-retry-v1",
    "complete_response_retry": False,
    "uncertain_request_retry": False,
    "terminal_incomplete_stream_retry": True,
    "base_backoff_ms": 5000,
    "max_backoff_ms": 30000,
}


def retry_delay_ms(retry_number: int) -> int:
    return min(AUDIT_RETRY_POLICY["base_backoff_ms"] * 2 ** (retry_number - 1),
               AUDIT_RETRY_POLICY["max_backoff_ms"])


def classify_failure(directory: Path, prompt: str) -> dict:
    """Allow only explicit temporary transport failures, never broad Exception.

    Record corruption deliberately raises: it must not be hidden by retrying.
    The same saved records drive live recovery and offline replay.
    """
    record = read_json(directory / "call.json")
    if record.get("prompt") != prompt or record.get("prompt_sha256") != canonical_sha256(prompt):
        raise ValueError("Audit retry prompt record mismatch")
    trace = validated_trace(directory / "transport.json")
    blocked = {"eligible": False, "category": "non_retryable_execution_error"}
    if (record.get("status") != "error" or record.get("response_rejected")
            or record.get("response") is not None or len(trace) != 1):
        return {**blocked, "category": "complete_interrupted_or_uncertain_call"}
    call = trace[0]
    if (record.get("recording_failed") or call.get("recording_failed")
            or record.get("error_type") == "ArtifactWriteError"
            or call.get("error_type") == "ArtifactWriteError"
            or any(attempt.get("recording_failed") or attempt.get("error_type") == "ArtifactWriteError"
                   for attempt in call.get("http_attempts", []))):
        return {**blocked, "category": "local_storage_integrity_or_interrupt"}
    if (call.get("status") != "error" or call.get("response_rejected") or call.get("response") is not None
            or call.get("prompt") != prompt):
        return {**blocked, "category": "complete_interrupted_or_uncertain_transport"}
    if any(record.get(key) != call.get(key) for key in ("error", "error_type")):
        return {**blocked, "category": "call_transport_error_mismatch"}
    message = str(record.get("error", "")).lower()
    error_type = record.get("error_type", "")
    attempts = call.get("http_attempts", [])
    last = attempts[-1] if attempts else {}
    status = last.get("http_status")
    stream = last.get("stream", {})
    if attempts and (last.get("status") != "error" or stream.get("outcome") == "pending"):
        return {**blocked, "category": "uncertain_http_attempt"}
    if stream.get("outcome") == "complete" or (stream.get("done_received") and stream.get("finish_reason") is not None):
        return {**blocked, "category": "complete_stream"}
    # The old transport wraps local OSError from persistence as a network error.
    # Reject it first, even if an HTTP 200 stream happens to be unfinished.
    if (error_type in {"PermissionError", "ResponseIntegrityError", "KeyboardInterrupt"}
            or any(token in message for token in (
                "permission denied", "access is denied", "winerror 5", "winerror 32", "errno 13",
                "拒绝访问", "另一个程序正在使用", "transport.json", "call.json",
                "disk full", "no space left", "read-only file system", "record digest",
                "response digest", "prompt digest", "credential overlaps"))):
        return {**blocked, "category": "local_storage_integrity_or_interrupt"}
    if isinstance(status, int) and 400 <= status < 500 and status != 429:
        return {**blocked, "category": "non_retryable_http"}
    if status == 429 or isinstance(status, int) and 500 <= status <= 599:
        return {"eligible": True, "category": "temporary_http"}
    if error_type == "RemoteDisconnected" and status is None:
        return {"eligible": True, "category": "temporary_connection"}
    if (error_type in {"IncompleteRead", "RemoteDisconnected"}
            or message.startswith("incomplete sse response: both [done] and choice finish_reason are required")):
        if (isinstance(status, int) and 200 <= status < 300
                and not (stream.get("done_received") and stream.get("finish_reason") is not None)):
            return {"eligible": True, "category": "incomplete_accepted_stream"}
        return {**blocked, "category": "unconfirmed_incomplete_stream"}
    if error_type in {"TimeoutError", "ConnectionError", "ConnectionResetError", "ConnectionAbortedError",
                      "ConnectionRefusedError", "gaierror"}:
        return {"eligible": True, "category": "temporary_connection"}
    # Match explicit causes preserved by URLError / the recorded SSE wrapper.
    transport_error = (error_type in {"URLError", "OSError"}
                       or error_type == "LlmClientError" and message.startswith("llm sse network failure:"))
    network_markers = ("getaddrinfo failed", "name or service not known", "temporary failure in name resolution",
                       "timed out", "connection reset", "connection aborted", "connection refused",
                       "network is unreachable", "host is unreachable", "remote end closed connection")
    if transport_error and any(token in message for token in network_markers):
        return {"eligible": True, "category": "temporary_connection"}
    return blocked


class RetryingAuditClient:
    """One audit unit with shared, bounded, durable transport retry decisions.

    The caller owns single-execution recording/recovery and interruption markers.
    ``persist`` must durably save and verify each decision before a retry starts;
    ``wait_for_retry`` preserves the caller's live/replay interruption boundary.
    Response parsing is intentionally outside this transport-only loop.
    """

    def __init__(self, *, execute: Callable, retries: int, call_path: Callable,
                 persist: Callable, wait_for_retry: Callable,
                 notify: Callable | None = None, delay: Callable | None = None):
        if type(retries) is not int or not 0 <= retries <= 5:
            raise ValueError("Audit execution retries must be an integer from 0 to 5")
        self.execute, self.retries, self.call_path = execute, retries, call_path
        self.persist, self.wait_for_retry = persist, wait_for_retry
        self.notify, self.delay = notify, delay or retry_delay_ms

    def complete(self, prompt):
        for attempt in range(1, self.retries + 2):
            directory, relative = self.call_path(attempt)
            try:
                response = self.execute(prompt)
            except Exception as error:
                if getattr(error, "error_type", None) == "KeyboardInterrupt":
                    raise
                category = classify_failure(directory, prompt) if (directory / "call.json").exists() else {
                    "eligible": False, "category": "missing_call_record"}
                retry = category["eligible"] and attempt <= self.retries
                decision = {
                    "attempt": attempt, "call": relative, "status": "error", **category,
                    "retry": retry, "prompt_sha256": canonical_sha256(prompt),
                    "call_sha256": sha_file(directory / "call.json") if (directory / "call.json").exists() else None,
                    "transport_sha256": sha_file(directory / "transport.json") if (directory / "transport.json").exists() else None,
                    "backoff_ms": self.delay(attempt) if retry else 0,
                }
                finalize_record(lambda: self.persist(attempt, decision), error, decision)
                if getattr(error, "recording_failed", False) or not retry:
                    raise
                if self.notify:
                    self.notify(decision)
                self.wait_for_retry(decision["backoff_ms"], attempt + 1)
            else:
                self.persist(attempt, {"attempt": attempt, "call": relative, "status": "complete", "retry": False,
                                       "prompt_sha256": canonical_sha256(prompt)})
                return response
        raise AssertionError("Audit execution retry loop exceeded its bound")
