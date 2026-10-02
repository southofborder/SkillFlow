"""Experimental Chat Completions SSE adapter; never imported by production.

Only HTTP framing changes. The original pipeline, replay, generation accounting,
and bounded retry loop are inherited. HTTP 200 followed by an incomplete stream
is not retried: its remote outcome and partial bytes remain in the trace.
"""

from __future__ import annotations

import codecs
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import threading
import time
import urllib.error
import urllib.request

from skill_ir.artifact_io import ArtifactWriteError
from skill_ir.experiments import resumable
from skill_ir.llm.client import _is_transient_status, _parse_retry_after
from skill_ir.llm.config import LlmClientError
from skill_ir.recording_errors import finalize_record


ORIGINAL_REPLAY_CLIENT = resumable._ReplayClient
STREAM_PARAMETERS = {"stream": True, "stream_options": {"include_usage": True}}
CHECKPOINT_INTERVAL_SECONDS = 5.0
TRANSPORT_POLICY = {
    "protocol": "chat-completions-sse-v1",
    "parameters": STREAM_PARAMETERS,
    "completion": "Require a complete SSE [DONE] event and a non-null finish_reason for choice index 0.",
    "retry": "Inherit bounded HTTP retries before an accepted 2xx response; never automatically retry any failure after 2xx headers.",
    "timeout": "Use the unchanged timeout_ms for blocking socket operations; it is an inactivity timeout, not an absolute generation deadline. Arriving events may extend total elapsed time.",
    "usage": "Request include_usage; retain null if missing; reject an unsupported-option error without fallback.",
    "trace": "Preserve all received SSE text and its wire SHA256, with existing secret redaction; malformed UTF-8 bytes are backslash-escaped in the diagnostic text.",
    "checkpoint": "Force checkpoints at stream start and termination, including errors; intermediate snapshots wait at least five seconds after the previous successful checkpoint finishes. Local recording failures never cause an HTTP retry.",
}


def _now():
    return datetime.now(timezone.utc).isoformat()


class SSECompletion:
    """Incremental SSE framing and a strict, single-choice chat accumulator."""

    def __init__(self):
        self.decoder = codecs.getincrementaldecoder("utf-8")("strict")
        self.line = ""
        self.after_cr = False
        self.data = []
        self.event_type = ""
        self.done = False
        self.finish_reason = None
        self.content = []
        self.refusal = []
        self.tool_deltas = []
        self.metadata = {}
        self.usage = None
        self.events = 0
        self.first_event_at = None
        self.first_content_at = None
        self.last_event_at = None

    def feed(self, value: bytes):
        for character in self.decoder.decode(value):
            if self.after_cr:
                self.after_cr = False
                if character == "\n":
                    continue
            if character in "\r\n":
                self._line(self.line)
                self.line = ""
                self.after_cr = character == "\r"
            else:
                self.line += character

    def _line(self, line):
        if not line:
            if self.data:
                self._event("\n".join(self.data))
            self.data = []
            self.event_type = ""
            return
        if line.startswith(":"):
            return
        field, separator, value = line.partition(":")
        if separator and value.startswith(" "):
            value = value[1:]
        if field == "data":
            self.data.append(value)
        elif field == "event":
            self.event_type = value

    def _event(self, data):
        if self.done:
            raise LlmClientError("SSE contained another data event after [DONE]")
        self.events += 1
        self.last_event_at = _now()
        self.first_event_at = self.first_event_at or self.last_event_at
        if data == "[DONE]":
            self.done = True
            return
        try:
            event = json.loads(data)
        except json.JSONDecodeError as error:
            raise LlmClientError(f"Invalid SSE JSON event: {error}") from error
        if not isinstance(event, dict):
            raise LlmClientError("SSE data must be a JSON object")
        if self.event_type == "error" or "error" in event:
            raise LlmClientError("SSE provider error: " + json.dumps(event, ensure_ascii=False))
        for key in ("id", "model", "created", "system_fingerprint", "service_tier"):
            if key in event:
                if key in {"id", "model"} and key in self.metadata and self.metadata[key] != event[key]:
                    raise LlmClientError(f"SSE changed completion {key} mid-stream")
                self.metadata[key] = event[key]
        if event.get("usage") is not None:
            if not isinstance(event["usage"], dict):
                raise LlmClientError("SSE usage must be an object or null")
            self.usage = event["usage"]
        choices = event.get("choices")
        if not isinstance(choices, list):
            raise LlmClientError("SSE event must contain a choices array")
        for choice in choices:
            if not isinstance(choice, dict) or type(choice.get("index")) is not int or choice["index"] != 0:
                raise LlmClientError("SSE adapter requires only choice index 0")
            if self.finish_reason is not None:
                raise LlmClientError("SSE emitted choice data after its finish_reason")
            delta = choice.get("delta")
            if not isinstance(delta, dict):
                raise LlmClientError("SSE choice.delta must be an object")
            for name, target in (("content", self.content), ("refusal", self.refusal)):
                value = delta.get(name)
                if value is not None:
                    if not isinstance(value, str):
                        raise LlmClientError(f"SSE delta.{name} must be text or null")
                    target.append(value)
                    if name == "content" and value:
                        self.first_content_at = self.first_content_at or _now()
            # No tools are supplied by this experiment. Preserve unexpected tool
            # fields in raw_sse, but never reinterpret them as candidate text.
            if delta.get("tool_calls") or delta.get("function_call"):
                self.tool_deltas.append(delta)
            reason = choice.get("finish_reason")
            if reason is not None:
                if reason not in {"stop", "length", "content_filter", "tool_calls", "function_call"}:
                    raise LlmClientError("Unknown SSE finish_reason")
                self.finish_reason = reason

    def response(self):
        if not self.done or self.finish_reason is None:
            raise LlmClientError("Incomplete SSE response: both [DONE] and choice finish_reason are required")
        if self.tool_deltas:
            raise LlmClientError("Unexpected tool-call output in the text-only SSE experiment")
        return {
            **self.metadata, "object": "chat.completion", "usage": self.usage,
            "choices": [{"index": 0, "finish_reason": self.finish_reason, "message": {
                "role": "assistant", "content": "".join(self.content),
                "refusal": "".join(self.refusal) or None,
            }}],
        }


class StreamingReplayClient(ORIGINAL_REPLAY_CLIENT):
    def _post_once(self, payload):
        body = json.dumps({**payload, **STREAM_PARAMETERS}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(self.config.endpoint, data=body, method="POST", headers={
            "Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json",
            "Content-Length": str(len(body)), "Accept": "text/event-stream",
        })
        attempt = self._active_http
        if attempt is None:
            raise ValueError("Experimental SSE requires the original recorded-call wrapper")
        state = {
            "request_parameters": STREAM_PARAMETERS, "request_body_sha256": hashlib.sha256(body).hexdigest(),
            "raw_sse": "", "wire_sha256": None, "received_bytes": 0,
            "headers_received_at": None, "first_byte_at": None, "first_event_at": None, "first_content_at": None,
            "last_event_at": None, "event_count": 0, "done_received": False,
            "finish_reason": None, "partial_content": "", "outcome": "pending",
        }
        attempt["stream"] = state
        raw = bytearray()
        parser = SSECompletion()
        accepted = False
        last_checkpoint = 0.0

        def checkpoint(force=False):
            nonlocal last_checkpoint
            current = time.monotonic()
            if force or current - last_checkpoint >= CHECKPOINT_INTERVAL_SECONDS:
                state.update(
                    raw_sse=raw.decode("utf-8", errors="backslashreplace"),
                    wire_sha256=hashlib.sha256(raw).hexdigest(), received_bytes=len(raw),
                    first_event_at=parser.first_event_at, first_content_at=parser.first_content_at,
                    last_event_at=parser.last_event_at, event_count=parser.events,
                    done_received=parser.done, finish_reason=parser.finish_reason,
                    partial_content="".join(parser.content),
                )
                if parser.usage is not None:
                    attempt["usage"] = parser.usage
                if parser.metadata.get("model") is not None:
                    attempt["returned_model"] = parser.metadata["model"]
                self._notify()
                # Slow serialization must not consume the next interval and
                # turn every subsequent chunk into another full snapshot.
                last_checkpoint = time.monotonic()

        primary_error = None
        try:
            try:
                self._notify()
                with urllib.request.urlopen(request, timeout=self.config.timeout_ms / 1000) as response:
                    status = int(response.status)
                    headers = response.headers or {}
                    attempt.update(http_status=status, request_id=headers.get("x-request-id"))
                    state["headers_received_at"] = _now()
                    state["response_content_type"] = headers.get("Content-Type")
                    if not 200 <= status < 300:
                        attempt["raw_response"] = response.read().decode("utf-8", errors="replace")
                        raise LlmClientError(f"LLM HTTP {status}: {attempt['raw_response']}", status_code=status, transient=_is_transient_status(status))
                    accepted = True
                    if (headers.get("Content-Type") or "").split(";", 1)[0].strip().lower() != "text/event-stream":
                        raw.extend(response.read())
                        if raw:
                            state["first_byte_at"] = _now()
                        raise LlmClientError("Expected text/event-stream; provider did not accept SSE framing")
                    checkpoint(force=True)
                    while not parser.done:
                        # read1 consumes available bytes without waiting to fill the
                        # requested buffer. read(1) is a conservative fallback.
                        chunk = response.read1(8192) if hasattr(response, "read1") else response.read(1)
                        if not chunk:
                            break
                        state["first_byte_at"] = state["first_byte_at"] or _now()
                        raw.extend(chunk)
                        parser.feed(chunk)
                        if not parser.done:
                            checkpoint()
                    result = parser.response()
                    state["outcome"] = "complete"
                    return result
            except ArtifactWriteError:
                # Persistence shares this stack with socket I/O, but is not a
                # network error. Keep the observed HTTP/stream facts unchanged.
                state["outcome"] = "recording_error"
                state["recording_failed"] = True
                attempt["recording_failed"] = True
                raise
            except urllib.error.HTTPError as error:
                text = error.read().decode("utf-8", errors="replace") if error.fp else ""
                headers = error.headers or {}
                attempt.update(raw_response=text, http_status=error.code, request_id=headers.get("x-request-id"))
                state["outcome"] = "remote_outcome_unknown" if accepted else "http_error"
                raise LlmClientError(f"LLM HTTP {error.code}: {text}", status_code=error.code,
                                     retry_after_ms=_parse_retry_after(headers.get("Retry-After")),
                                     transient=not accepted and _is_transient_status(error.code)) from error
            except (TimeoutError, OSError, urllib.error.URLError) as error:
                state["outcome"] = "remote_outcome_unknown" if accepted else "network_error"
                raise LlmClientError(f"LLM SSE network failure: {error}",
                                     status_code=attempt.get("http_status") if accepted else None,
                                     transient=not accepted) from error
            except UnicodeDecodeError as error:
                state["outcome"] = "remote_outcome_unknown"
                raise LlmClientError(f"Invalid UTF-8 in SSE response: {error}", status_code=attempt.get("http_status")) from error
            except LlmClientError as error:
                state["outcome"] = "remote_outcome_unknown" if accepted else "http_error"
                if accepted:
                    # The inherited recorder copies status_code over http_status.
                    # Retain the observed 200 even when the body later fails.
                    error.status_code = attempt.get("http_status")
                    error.transient = False
                raise
            except BaseException:
                state["outcome"] = "remote_outcome_unknown" if accepted else "http_error"
                raise
        except BaseException as error:
            primary_error = error
            raise
        finally:
            # The final snapshot must not replace an earlier transport/parser
            # error; recording_failed also prevents retrying that request.
            finalize_record(lambda: checkpoint(force=True), primary_error, attempt)


@contextmanager
def isolated_streaming_client():
    """Select a factory only in a dedicated process before workers are created.

    The existing runner has no public client factory hook. This explicit binding
    is limited to its module-local factory; no HTTP/global production client is
    patched, and all worker threads are drained before restoration.
    """
    if resumable._ReplayClient is not ORIGINAL_REPLAY_CLIENT or threading.active_count() != 1:
        raise ValueError("SSE experiments require an otherwise single-threaded dedicated process")
    resumable._ReplayClient = StreamingReplayClient
    try:
        yield
    finally:
        resumable._ReplayClient = ORIGINAL_REPLAY_CLIENT
