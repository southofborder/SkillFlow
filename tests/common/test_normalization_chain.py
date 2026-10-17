"""Completed raw responses, normalization receipts and replay remain distinct."""

from copy import deepcopy
import json
import socket
from threading import Event

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.llm.config import LlmClientError, OutputTruncatedError
from skillflow.common.recording import (
    canonical_sha256, injected_factory, read_json, SavedCallFailure,
)
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common import structural_correction as correction
from skillflow.common.structural_correction import (
    ResponseChain, ResponseChainError, chain_counts, correct_response,
    response_chain_files,
)
from skillflow.common.validation import structural_error
from skillflow.propagation.annotation.config import annotation_config
from skillflow.propagation.annotation.services import parse_candidate_json


PREFIX = "calls/annotation"
BASE_PROMPT = "A frozen synthetic task, source and target index."
RAW_OK = ' \r\n{"ok":true}\t}\r\n'


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("These response-chain tests must never access the network")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)


class Script:
    def __init__(self, responses):
        self.responses, self.prompts = iter(responses), []

    def complete(self, prompt):
        self.prompts.append(prompt)
        value = next(self.responses)
        if isinstance(value, BaseException):
            raise value
        return deepcopy(value)


def validate(raw):
    value = parse_candidate_json(raw)
    if value == {"ok": True}:
        return {"validated": True}
    if value == {"outcome": "cannot_assess"}:
        raise SemanticFailure({"reason": "Required source evidence is absent.", "evidences": []})
    if value == {"internal_error": True}:
        raise RuntimeError("synthetic implementation failure")
    raise structural_error("schema", "/ok", "The sole required member is ok=true")


def run(directory, client=None, **kwargs):
    writer = kwargs.pop("writer", ArtifactWriter(()))
    validator = kwargs.pop("validate", validate)
    return ResponseChain(
        directory, prefix=PREFIX, base_prompt=BASE_PROMPT, request_kind="base",
        config=annotation_config({}), writer=writer, validate=validator,
        client_factory=None if client is None else injected_factory(client), **kwargs,
    )


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def file_bytes(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob("*") if path.is_file()}


def test_one_completed_call_keeps_raw_candidate_and_receipt_distinct(tmp_path):
    client = Script([RAW_OK])
    chain = run(tmp_path, client)
    assert chain.run() == {"validated": True}
    assert client.prompts == [BASE_PROMPT]
    assert chain.accepted_call == PREFIX + "/a001"
    assert chain.response == RAW_OK
    offset = RAW_OK.rindex("}")
    candidate = RAW_OK[:offset] + RAW_OK[offset + 1:]
    assert chain.candidate == candidate
    assert chain.normalization == {
        "version": "skillflow-json-normalization-v1",
        "rule": "trailing_single_object_closer",
        "raw_sha256": canonical_sha256(RAW_OK),
        "normalized_sha256": canonical_sha256(candidate),
        "removed_offset": offset,
        "removed_character": "}",
    }
    call_dir = tmp_path / PREFIX / "a001"
    assert read_json(call_dir / "response.json") == RAW_OK
    assert read_json(call_dir / "call.json")["response"] == RAW_OK
    assert read_json(call_dir / "transport.json")[0]["response"] == RAW_OK
    assert read_json(call_dir / "normalization.json") == chain.normalization
    validation = read_json(call_dir / "validation.json")
    assert validation["response_sha256"] == canonical_sha256(RAW_OK)
    assert validation["candidate_sha256"] == canonical_sha256(candidate)
    assert validation["normalization_sha256"] == canonical_sha256(chain.normalization)
    assert PREFIX + "/a001/normalization.json" in response_chain_files(tmp_path, PREFIX)
    counts = chain_counts(tmp_path, PREFIX)
    assert counts["logical_calls"] == 1
    assert counts["structural_corrections"] == 0
    assert counts["json_normalizations"] == 1
    assert counts["record_integrity_errors"] == []

    before = file_bytes(tmp_path)
    replay = run(tmp_path, replay=True, read_only=True)
    assert replay.run() == chain.value
    assert replay.snapshot() == chain.snapshot()
    assert replay.response == RAW_OK
    assert replay.candidate == candidate
    assert file_bytes(tmp_path) == before
    unexpected_client = Script([])
    assert run(tmp_path, unexpected_client).run() == chain.value
    assert unexpected_client.prompts == []


@pytest.mark.parametrize("response", ['{"ok":true}', {"ok": True}])
def test_already_valid_response_has_no_receipt_or_normalization_count(tmp_path, response):
    chain = run(tmp_path, Script([response]))
    assert chain.run() == {"validated": True}
    assert chain.response == chain.candidate == response
    assert chain.normalization is None
    assert not (tmp_path / PREFIX / "a001/normalization.json").exists()
    assert chain_counts(tmp_path, PREFIX)["json_normalizations"] == 0
    validation = read_json(tmp_path / PREFIX / "a001/validation.json")
    assert validation["response_sha256"] == validation["candidate_sha256"]
    assert validation["normalization_sha256"] is None


def test_in_memory_and_recorded_paths_use_same_candidate_and_raw_callbacks(tmp_path):
    calls, normalized = [], []
    client = Script([RAW_OK])
    value = correct_response(
        BASE_PROMPT, complete=client.complete, validate=validate,
        on_attempt=lambda *args: calls.append(args),
        on_normalization=lambda *args: normalized.append(args),
    )
    persisted = run(tmp_path, Script([RAW_OK]))
    assert persisted.run() == value == {"validated": True}
    assert len(client.prompts) == 1
    assert calls == [(1, RAW_OK, None)]
    assert normalized == [(1, RAW_OK, persisted.normalization)]


def test_schema_failure_after_normalization_still_needs_correction(tmp_path):
    bad = '{"bad":"retained raw candidate"}}'
    client = Script([bad, RAW_OK])
    chain = run(tmp_path, client)
    assert chain.run() == {"validated": True}
    assert len(client.prompts) == 2
    assert chain.accepted_call == PREFIX + "/a002"
    first = tmp_path / PREFIX / "a001"
    assert read_json(first / "response.json") == bad
    assert read_json(first / "normalization.json")["raw_sha256"] == canonical_sha256(bad)
    validation = read_json(first / "validation.json")
    assert validation["status"] == "structural_invalid"
    assert validation["normalization_sha256"] is not None
    context = json.loads(client.prompts[1].split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
    assert context["candidate"] == bad
    counts = chain_counts(tmp_path, PREFIX)
    assert (counts["logical_calls"], counts["structural_corrections"], counts["json_normalizations"]) == (2, 1, 2)
    assert run(tmp_path, replay=True, read_only=True).run() == chain.value


@pytest.mark.parametrize("raw,error,status", [
    ('{"outcome":"cannot_assess"}}', SemanticFailure, "semantic_failure"),
    ('{"internal_error":true}}', RuntimeError, "execution_error"),
])
def test_normalization_does_not_turn_nonstructural_failure_into_correction(tmp_path, raw, error, status):
    client = Script([raw])
    chain = run(tmp_path, client)
    with pytest.raises(error):
        chain.run()
    assert len(client.prompts) == 1
    assert chain.accepted_call is None
    assert read_json(tmp_path / PREFIX / "a001/validation.json")["status"] == status
    assert (tmp_path / PREFIX / "a001/normalization.json").is_file()
    with pytest.raises(error):
        run(tmp_path, replay=True, read_only=True).run()
    memory_client = Script([raw])
    with pytest.raises(error):
        correct_response(BASE_PROMPT, complete=memory_client.complete, validate=validate)
    assert len(memory_client.prompts) == 1


@pytest.mark.parametrize("point", ["after_call", "normalize", "after_normalization", "after_validation"])
def test_interruption_recovers_same_accepted_raw_response_without_resending(tmp_path, point):
    stop_event = Event()
    client = Script([RAW_OK])
    chain = run(tmp_path, client, stop_event=stop_event)
    original_stop = chain._stop

    def interrupt(where, call):
        if where == point:
            stop_event.set()
        original_stop(where, call)

    chain._stop = interrupt
    with pytest.raises(KeyboardInterrupt):
        chain.run()
    assert client.prompts == [BASE_PROMPT]
    raw_bytes = (tmp_path / PREFIX / "a001/response.json").read_bytes()
    replay = run(tmp_path, replay=True, read_only=True, interruption=chain.cursor)
    with pytest.raises(KeyboardInterrupt):
        replay.run()
    assert replay.snapshot() == chain.snapshot()
    never_called = Script([])
    resumed = run(tmp_path, never_called)
    assert resumed.run() == {"validated": True}
    assert never_called.prompts == []
    assert resumed.accepted_call == PREFIX + "/a001"
    assert (tmp_path / PREFIX / "a001/response.json").read_bytes() == raw_bytes
    assert run(tmp_path, replay=True, read_only=True).run() == resumed.value


@pytest.mark.parametrize("change", [
    "missing_receipt", "receipt_version", "receipt_rule", "receipt_offset",
    "receipt_character", "receipt_raw_hash", "receipt_normalized_hash", "extra_receipt_field",
    "normalization_policy", "chain_version", "raw_response", "call_response",
    "validation_hash", "validation_candidate", "validation_raw_hash",
])
def test_tampered_normalization_material_is_rejected_on_load_and_resume(tmp_path, change):
    run(tmp_path, Script([RAW_OK])).run()
    call_dir = tmp_path / PREFIX / "a001"
    target = call_dir / "normalization.json"
    if change == "missing_receipt":
        target.unlink()
    else:
        if change.startswith("receipt_") or change == "extra_receipt_field":
            material = read_json(target)
            field = {
                "receipt_version": "version", "receipt_rule": "rule",
                "receipt_offset": "removed_offset", "receipt_character": "removed_character",
                "receipt_raw_hash": "raw_sha256", "receipt_normalized_hash": "normalized_sha256",
                "extra_receipt_field": "extra",
            }[change]
            material[field] = 0 if field == "removed_offset" else "tampered"
        elif change in {"normalization_policy", "chain_version"}:
            target = tmp_path / PREFIX / "chain.json"
            material = read_json(target)
            material["normalization_policy" if change == "normalization_policy" else "version"] = "unsupported"
        elif change == "raw_response":
            target = call_dir / "response.json"
            material = '{"ok":true}'
        elif change == "call_response":
            target = call_dir / "call.json"
            material = read_json(target)
            material["response"] = '{"ok":true}'
        else:
            target = call_dir / "validation.json"
            material = read_json(target)
            field = {"validation_hash": "normalization_sha256", "validation_candidate": "candidate_sha256",
                     "validation_raw_hash": "response_sha256"}[change]
            material[field] = "0" * 64
        write_json(target, material)
    before = file_bytes(tmp_path)
    with pytest.raises(ValueError):
        run(tmp_path, replay=True, read_only=True).run()
    assert file_bytes(tmp_path) == before
    never_called = Script([])
    with pytest.raises(ValueError):
        run(tmp_path, never_called).run()
    assert never_called.prompts == []
    assert file_bytes(tmp_path) == before


def test_unmodified_legal_response_cannot_acquire_a_normalization_receipt(tmp_path):
    run(tmp_path, Script(['{"ok":true}'])).run()
    write_json(tmp_path / PREFIX / "a001/normalization.json", {"version": "skillflow-json-normalization-v1"})
    with pytest.raises(ResponseChainError, match="Unexpected normalization receipt"):
        run(tmp_path, replay=True, read_only=True).run()


@pytest.mark.parametrize("change", ["duplicate_receipt_key", "float_offset", "boolean_request_index"])
def test_type_equivalent_or_duplicate_audit_values_are_not_accepted(tmp_path, change):
    run(tmp_path, Script([RAW_OK])).run()
    call_dir = tmp_path / PREFIX / "a001"
    path = call_dir / "normalization.json"
    value = read_json(path)
    if change == "duplicate_receipt_key":
        # Ordinary json.loads would discard one member and reproduce exactly
        # the expected dict. Strict artifact loading must still reject it.
        text = json.dumps(value, ensure_ascii=False)
        path.write_text(text[:-1] + ', "rule": ' + json.dumps(value["rule"]) + '}', encoding="utf-8")
        assert json.loads(path.read_text(encoding="utf-8")) == value
    elif change == "float_offset":
        value["removed_offset"] = float(value["removed_offset"])
        write_json(path, value)
    else:
        path = call_dir / "request.json"
        value = read_json(path)
        assert value["index"] == 1
        value["index"] = True
        write_json(path, value)
    before = file_bytes(tmp_path)
    with pytest.raises(ValueError):
        run(tmp_path, replay=True, read_only=True).run()
    assert file_bytes(tmp_path) == before
    never_called = Script([])
    with pytest.raises(ValueError):
        run(tmp_path, never_called).run()
    assert never_called.prompts == []
    assert file_bytes(tmp_path) == before


@pytest.mark.parametrize("error", [
    ConnectionError("network unavailable"),
    OutputTruncatedError("finish_reason=length"),
    LlmClientError("Incomplete SSE response: both [DONE] and choice finish_reason are required"),
])
def test_transport_failure_never_reaches_normalization_or_new_call(tmp_path, monkeypatch, error):
    def forbidden(*args):
        raise AssertionError("Normalization must follow accepted complete transport")

    monkeypatch.setattr(correction, "normalize_response", forbidden)
    client = Script([error])
    with pytest.raises(type(error), match=str(error).replace("[", r"\[").replace("]", r"\]")):
        run(tmp_path, client).run()
    assert len(client.prompts) == 1
    assert not (tmp_path / PREFIX / "a001/normalization.json").exists()
    assert not (tmp_path / PREFIX / "a002").exists()
    never_called = Script([])
    with pytest.raises(SavedCallFailure):
        run(tmp_path, never_called).run()
    assert never_called.prompts == []
    with pytest.raises(SavedCallFailure):
        run(tmp_path, replay=True, read_only=True).run()
    memory_client = Script([error])
    with pytest.raises(type(error)):
        correct_response(BASE_PROMPT, complete=memory_client.complete, validate=validate)
    assert len(memory_client.prompts) == 1


@pytest.mark.parametrize("filename", ["normalization.json", "validation.json"])
def test_disk_failure_stops_then_resumes_from_saved_response(tmp_path, filename):
    class BrokenWriter(ArtifactWriter):
        def json(self, path, value):
            if path.name == filename:
                raise OSError("synthetic disk failure")
            return super().json(path, value)

    client = Script([RAW_OK])
    chain = run(tmp_path, client, writer=BrokenWriter(()))
    with pytest.raises(OSError, match="synthetic disk failure"):
        chain.run()
    assert len(client.prompts) == 1
    assert chain.accepted_call is None
    assert not (tmp_path / PREFIX / "a002").exists()
    never_called = Script([])
    assert run(tmp_path, never_called).run() == {"validated": True}
    assert never_called.prompts == []
    assert read_json(tmp_path / PREFIX / "a001/response.json") == RAW_OK


def test_old_chain_protocol_cannot_be_silently_upgraded(tmp_path):
    run(tmp_path, Script([RAW_OK])).run()
    path = tmp_path / PREFIX / "chain.json"
    value = read_json(path)
    value["version"] = "skillflow-structural-correction-v1"
    del value["normalization_policy"]
    write_json(path, value)
    original = path.read_bytes()
    with pytest.raises(ResponseChainError, match="protocol"):
        run(tmp_path, replay=True, read_only=True)
    never_called = Script([])
    with pytest.raises(ResponseChainError, match="protocol"):
        run(tmp_path, never_called)
    assert never_called.prompts == []
    assert path.read_bytes() == original
