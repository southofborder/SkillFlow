"""Shared durable model-call recording and offline recovery.

One client instance owns one logical request. Streaming, HTTP retry policy and
accepted-response handling remain in the existing SSE transport adapter.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
from typing import Callable

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.llm.config import LlmConfig, load_environment
from skill_ir.recording_errors import error_fields, finalize_record

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]


def canonical_sha256(value) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def implementation_provenance() -> dict:
    paths = set((PACKAGE_ROOT / "src/skill_ir").rglob("*.py"))
    paths.add(PACKAGE_ROOT / "experiments/semantics_baseline/tools/stream_transport.py")
    paths.update((PACKAGE_ROOT / "formal").rglob("*.lean"))
    paths = {p for p in paths if ".lake" not in p.parts}
    paths.update(PACKAGE_ROOT / "formal" / name for name in ("lakefile.toml", "lean-toolchain"))
    files = {p.relative_to(REPOSITORY_ROOT).as_posix(): sha_file(p) for p in sorted(paths)}
    return {"files": files, "sha256": canonical_sha256(files), "python": platform.python_version()}


def streaming_factory(config: dict, *, env_file: Path | None = None):
    """Inject the existing recorded SSE client without changing its old runner."""
    environment = load_environment(env_file=env_file)
    secret = environment.get("LLM_API_KEY", "").strip()
    if not secret:
        raise ValueError("LLM_API_KEY is required in the existing environment or explicit --env-file")
    llm_config = LlmConfig(api_key=secret, **config)
    adapter_path = PACKAGE_ROOT / "experiments/semantics_baseline/tools/stream_transport.py"
    spec = importlib.util.spec_from_file_location("_skill_ir_recorded_sse", adapter_path)
    if spec is None or spec.loader is None:
        raise ValueError("The recorded SSE transport adapter cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def factory(writer, on_record):
        return module.StreamingReplayClient(llm_config, prior_calls=[], writer=writer, on_record=on_record)

    return factory, (secret,)


def injected_factory(client):
    """Adapt a plain ``complete(prompt)`` client to the durable record contract.

    The adapter observes a logical call only. It makes no claim about the injected
    client's HTTP attempts, returned model or usage; those remain explicitly
    unobserved rather than being inferred from request configuration.
    """
    if not callable(getattr(client, "complete", None)):
        raise TypeError("An injected client must provide complete(prompt)")

    def factory(writer, on_record):
        class InjectedClient:
            def complete(self, prompt):
                record = {
                    "status": "running", "prompt": prompt, "started_at": now(),
                    "transport": "injected", "http_attempts": [],
                    "http_attempts_observed": False, "returned_model": None, "usage": None,
                }
                on_record([record])
                primary_error = None
                try:
                    response = client.complete(prompt)
                    record.update(status="complete", response=response)
                    return response
                except BaseException as error:
                    primary_error = error
                    record.update(
                        status="interrupted" if isinstance(error, KeyboardInterrupt) else "error",
                        **error_fields(error),
                    )
                    raise
                finally:
                    record["finished_at"] = now()
                    finalize_record(lambda: on_record([record]), primary_error, record)
        return InjectedClient()

    return factory


def validated_trace(path: Path) -> list:
    trace = read_json(path) if path.exists() else []
    if not isinstance(trace, list) or any(not isinstance(record, dict) for record in trace):
        raise ValueError("Transport record must be a list of objects")
    for record in trace:
        saved = deepcopy(record)
        digest = saved.pop("record_sha256", None)
        if digest != canonical_sha256(saved):
            raise ValueError("Transport record digest mismatch")
    return trace


class SavedCallFailure(ValueError):
    """Preserve an already-recorded failure's identity during offline replay."""

    def __init__(self, error_type: str, message: str):
        super().__init__(message)
        self.error_type = error_type


class ResponseIntegrityError(ValueError):
    """A returned response cannot be used faithfully from its durable record."""


def _complete_transport_response(trace, prompt):
    if (len(trace) != 1 or trace[0].get("status") != "complete"
            or trace[0].get("prompt") != prompt or "response" not in trace[0]
            or trace[0].get("response_rejected")):
        raise ValueError("Call and transport response records disagree")
    return trace[0]["response"]


class SavedResponseClient:
    """One exact saved response; exhaustion/errors can never fall through to HTTP."""

    def __init__(self, directory: Path, writer: ArtifactWriter):
        self.directory, self.writer, self.calls = directory, writer, 0

    def complete(self, prompt):
        self.calls += 1
        if self.calls != 1:
            raise ValueError("Each recorded client is limited to one logical model call")
        record = read_json(self.directory / "call.json")
        if record.get("response_rejected") or record.get("status") == "invalid_record":
            raise SavedCallFailure(record.get("error_type", "ResponseIntegrityError"),
                                   record.get("error", "Recorded response was rejected; no automatic recovery is permitted"))
        if record["prompt"] != self.writer.clean(prompt):
            raise ValueError("Replay prompt differs from the recorded call input")
        if record["prompt_sha256"] != canonical_sha256(record["prompt"]):
            raise ValueError("Recorded prompt digest mismatch")
        trace = validated_trace(self.directory / "transport.json")
        if record.get("status") == "complete":
            if record.get("response_sha256") != canonical_sha256(record["response"]):
                raise ValueError("Recorded response digest mismatch")
            saved_response = _complete_transport_response(trace, record["prompt"])
            if canonical_sha256(saved_response) != record["response_sha256"]:
                raise ValueError("Call and transport response records disagree")
            return deepcopy(record["response"])
        # A process may stop just after the transport persisted a complete response.
        # Use it offline, never send an uncertain call again.
        if len(trace) == 1 and trace[0].get("status") == "complete" and trace[0]["prompt"] == record["prompt"]:
            return deepcopy(_complete_transport_response(trace, record["prompt"]))
        raise SavedCallFailure(record.get("error_type", "IncompleteResponse"), record.get("error", "Saved call is incomplete; no automatic resend is permitted"))


class RecordingClient:
    """Persist before I/O; never overwrite or retransmit an existing call."""

    def __init__(self, directory: Path, factory: Callable, writer: ArtifactWriter):
        self.directory, self.factory, self.writer, self.calls = directory, factory, writer, 0

    def complete(self, prompt):
        self.calls += 1
        if self.calls != 1:
            raise ValueError("Each recorded client is limited to one logical model call")
        clean_prompt = self.writer.clean(prompt)
        if clean_prompt != prompt:
            raise ValueError("A credential overlaps the model prompt; refusing to alter or transmit checked content")
        path = self.directory / "call.json"
        if any((self.directory / name).exists() for name in (
            "call.json", "transport.json", "prompt.txt", "response.json"
        )):
            raise ValueError("A recorded call already exists; use SavedResponseClient without automatic resend")
        record = {"status": "running", "started_at": now(), "prompt": clean_prompt,
                  "prompt_sha256": canonical_sha256(clean_prompt)}
        self.writer.json(path, record)  # Durable before any network I/O.
        self.writer.text(self.directory / "prompt.txt", prompt)

        def reject_response(message):
            record.update(status="invalid_record", response_rejected=True,
                          error=self.writer.clean(message), error_type="ResponseIntegrityError")
            self.writer.json(path, record)
            raise ResponseIntegrityError(message)

        def checkpoint(calls):
            cleaned = self.writer.clean(deepcopy(calls))
            rejected = False
            for original, call in zip(calls, cleaned):
                if (original.get("status") == "complete" and "response" in original
                        and canonical_sha256(original["response"]) != canonical_sha256(call["response"])):
                    call["response_rejected"] = True
                    rejected = True
                call["record_sha256"] = canonical_sha256(call)
            self.writer.json(self.directory / "transport.json", cleaned)
            if rejected:
                # Durable even if the transport callback is the final event before
                # process interruption: a redacted substitute is not a response.
                reject_response("A credential overlaps the model response; refusing altered semantic content")

        primary_error = None
        try:
            client = self.factory(self.writer, checkpoint)
            response = client.complete(prompt)
            clean_response = self.writer.clean(response)
            try:
                response_digest = canonical_sha256(response)
                clean_response_digest = canonical_sha256(clean_response)
            except (TypeError, ValueError):
                reject_response("Returned response is not a serializable JSON value")
            record.update(response=clean_response,
                          response_sha256=clean_response_digest)
            self.writer.json(self.directory / "response.json", clean_response)
            if response_digest != record["response_sha256"]:
                reject_response("A credential overlaps the model response; refusing altered semantic content")
            try:
                trace = validated_trace(self.directory / "transport.json")
                stored_response = _complete_transport_response(trace, clean_prompt)
                if canonical_sha256(stored_response) != record["response_sha256"]:
                    raise ValueError("Returned response differs from the saved transport response")
            except Exception as error:
                reject_response("Returned response failed durable record verification: " + str(error))
            record["status"] = "complete"
            return response
        except BaseException as error:
            primary_error = error
            if not record.get("response_rejected"):
                record.update(status="interrupted" if isinstance(error, KeyboardInterrupt) else "error",
                              **self.writer.clean(error_fields(error)))
            raise
        finally:
            record["finished_at"] = now()
            finalize_record(lambda: self.writer.json(path, record), primary_error, record)
