"""Mechanical correction is unbounded, deterministic and never a resend."""
from copy import deepcopy
import json
from threading import Event

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory, read_json
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.structural_correction import (
    ResponseChain, ResponseChainError, correction_prompt, chain_counts, correct_response,
    StructuralCorrectionLimitReached,
)
from skillflow.common.validation import structural_error
from skillflow.propagation.annotation.config import annotation_config


class Script:
    def __init__(self, responses):
        self.responses, self.prompts = iter(responses), []

    def complete(self, prompt):
        self.prompts.append(prompt)
        value = next(self.responses)
        if isinstance(value, BaseException):
            raise value
        return deepcopy(value)


def validate(value):
    if value == {"ok": True}:
        return {"validated": True}
    if value == {"fail": True}:
        raise SemanticFailure({"reason": "The source is contradictory.", "evidences": []})
    if value == {"bug": True}:
        raise ValueError("implementation failure")
    raise structural_error("shape", "/ok", "A boolean true is required")


def run(directory, client=None, **kwargs):
    return ResponseChain(directory, prefix="calls/annotation", base_prompt="Frozen task and target index.",
        request_kind="base", config=annotation_config({}), writer=ArtifactWriter(()), validate=validate,
        client_factory=None if client is None else injected_factory(client), **kwargs)


def test_many_corrections_then_exact_offline_replay(tmp_path):
    client = Script([{"bad": index} for index in range(13)] + [{"ok": True}])
    chain = run(tmp_path, client)
    assert chain.run() == {"validated": True}
    assert chain.accepted_call == "calls/annotation/a014"
    assert chain_counts(tmp_path, "calls/annotation")["structural_corrections"] == 13
    assert len(client.prompts) == 14
    assert '"bad":12' in client.prompts[-1] and '"bad":11' not in client.prompts[-1]
    replay = run(tmp_path, replay=True, read_only=True)
    assert replay.run() == chain.value
    assert replay.snapshot() == chain.snapshot()
    resumed = run(tmp_path)
    assert resumed.run() == chain.value
    assert resumed.snapshot() == chain.snapshot()


def test_same_error_repeats_without_stagnation_cap_until_user_interrupts(tmp_path):
    stopping = Event()
    class Repeating:
        calls = 0
        def complete(self, prompt):
            self.calls += 1
            if self.calls == 12:
                stopping.set()
            return {"bad": "same"}
    client = Repeating()
    chain = run(tmp_path, client, stop_event=stopping)
    with pytest.raises(KeyboardInterrupt):
        chain.run()
    assert client.calls == 12
    replay = run(tmp_path, replay=True, read_only=True, interruption=chain.cursor)
    with pytest.raises(KeyboardInterrupt):
        replay.run()
    assert replay.snapshot() == chain.snapshot()
    resume_client = Script([{"ok": True}])
    resumed = run(tmp_path, resume_client)
    assert resumed.run() == {"validated": True}
    assert len(resume_client.prompts) == 1
    assert resumed.accepted_call == "calls/annotation/a013"


@pytest.mark.parametrize("response,error", [({"bug": True}, ValueError), ({"fail": True}, SemanticFailure)])
def test_nonstructural_failures_stop_without_new_call(tmp_path, response, error):
    client = Script([response])
    chain = run(tmp_path, client)
    with pytest.raises(error):
        chain.run()
    assert len(client.prompts) == 1
    replay = run(tmp_path, replay=True, read_only=True)
    with pytest.raises(error):
        replay.run()


@pytest.mark.parametrize("point", ["before_transport", "after_call", "after_validation"])
def test_interrupt_and_replay_at_exact_boundary(tmp_path, point):
    stopping = Event()
    client = Script([{"ok": True}])
    chain = run(tmp_path, client, stop_event=stopping)
    original = chain._stop
    def stop(where, call):
        if where == point:
            stopping.set()
        original(where, call)
    chain._stop = stop
    with pytest.raises(KeyboardInterrupt):
        chain.run()
    replay = run(tmp_path, replay=True, read_only=True, interruption=chain.cursor)
    with pytest.raises(KeyboardInterrupt):
        replay.run()
    assert replay.snapshot() == chain.snapshot()


@pytest.mark.parametrize("path", ["a001/request.json", "a001/validation.json", "a001/call.json", "a002/call.json", "chain.json"])
def test_chain_tampering_is_rejected(tmp_path, path):
    chain = run(tmp_path, Script([{"bad": 1}, {"ok": True}]))
    chain.run()
    target = tmp_path / "calls/annotation" / path
    value = read_json(target)
    value["tampered"] = True
    target.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ResponseChainError):
        run(tmp_path, replay=True, read_only=True).run()


@pytest.mark.parametrize("change", ["accepted_call", "ghost_pending", "terminal_pending", "missing_chain"])
def test_normal_resume_rejects_changed_terminal_history_before_overwriting(tmp_path, change):
    run(tmp_path, Script([{"bad": 1}, {"ok": True}])).run()
    path = tmp_path / "calls/annotation/chain.json"
    saved = read_json(path)
    if change == "missing_chain":
        path.unlink()
    else:
        if change == "accepted_call":
            saved["accepted_call"] = "calls/annotation/a001"
        elif change == "ghost_pending":
            saved["attempts"].append({"call": "calls/annotation/a003", "request_sha256": "fake",
                                      "status": "pending", "validation_sha256": None})
        else:
            saved["attempts"][-1]["status"] = "pending"
        path.write_text(json.dumps(saved), encoding="utf-8")
    before = path.read_bytes() if path.exists() else None
    client = Script([{"ok": True}])
    with pytest.raises(ResponseChainError):
        run(tmp_path, client).run()
    assert not client.prompts
    assert (path.read_bytes() if path.exists() else None) == before


def test_memory_service_uses_the_same_transition_and_prompt():
    client = Script([{"bad": 1}, {"ok": True}])
    assert correct_response("base", complete=client.complete, validate=validate) == {"validated": True}
    assert client.prompts[1] == correction_prompt("base", {"bad": 1}, [
        {"code": "shape", "path": "/ok", "message": "A boolean true is required"}])


def test_lazy_credentials_are_loaded_before_prompt_is_written_or_sent(tmp_path):
    from skillflow.common.recording import ResponseIntegrityError
    client = Script([{"ok": True}])
    def provider(writer):
        writer.secrets = ("Frozen task",)
        return injected_factory(client)
    chain = run(tmp_path, factory_provider=provider)
    with pytest.raises(ValueError, match="credential"):
        chain.run()
    assert not client.prompts
    assert not (tmp_path / "calls/annotation/a001/prompt.txt").exists()
    assert all(b"Frozen task" not in path.read_bytes() for path in tmp_path.rglob("*") if path.is_file())


def test_opt_in_limit_records_two_invalid_calls_and_replays_terminal_failure(tmp_path):
    client = Script([{"bad": 1}, {"bad": 2}, {"ok": True}])
    chain = run(tmp_path, client, max_corrections=1)
    with pytest.raises(StructuralCorrectionLimitReached):
        chain.run()
    assert len(client.prompts) == 2
    assert not (tmp_path / "calls/annotation/a003").exists()
    assert chain.snapshot()["max_corrections"] == 1
    assert [row["status"] for row in chain.attempts] == ["structural_invalid", "structural_invalid"]
    for kwargs in ({"replay": True, "read_only": True}, {}):
        resumed = run(tmp_path, max_corrections=1, **kwargs)
        with pytest.raises(StructuralCorrectionLimitReached):
            resumed.run()
        assert resumed.snapshot() == chain.snapshot()
    with pytest.raises(ResponseChainError):
        run(tmp_path, max_corrections=2)
    with pytest.raises(ResponseChainError):
        run(tmp_path)


def test_opt_in_limit_accepts_one_correction_without_changing_legacy_shape(tmp_path):
    client = Script([{"bad": True}, {"ok": True}])
    chain = run(tmp_path / "bounded", client, max_corrections=1)
    assert chain.run() == {"validated": True}
    replay = run(tmp_path / "bounded", replay=True, read_only=True, max_corrections=1)
    assert replay.run() == chain.value
    legacy = run(tmp_path / "legacy", Script([{"bad": 1}, {"bad": 2}, {"ok": True}]))
    assert legacy.run() == {"validated": True}
    assert "max_corrections" not in legacy.snapshot()


@pytest.mark.parametrize("value", [-1, True, 1.5, "1"])
def test_invalid_correction_limit_fails_before_dispatch(tmp_path, value):
    with pytest.raises(ValueError, match="max_corrections"):
        run(tmp_path, max_corrections=value)
