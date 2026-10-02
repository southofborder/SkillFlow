"""Durable whole-graph annotation and replay, with no real network calls."""
from copy import deepcopy
import json
from pathlib import Path
from threading import Event

import pytest

from skill_ir.security_profile import runner
from security_profile.helpers import FakeClient, graph, profile, with_specs


def setup_run(tmp_path, **kwargs):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text(
        "---\nname: local-config\ndescription: 配置处理\n---\n"
        "读取配置 config.json，在本地筛选后返回内部结果。\n禁止泄露密钥。\n",
        encoding="utf-8")
    (source / "helper.txt").write_bytes("完整附加文件\r\n第二行\n".encode())
    analysis = tmp_path / "analysis.json"
    analysis.write_text(json.dumps({"cfg": graph(), "candidate": "OLD_CANDIDATE_CANARY",
                                    "review": "OLD_REVIEW_CANARY"}, ensure_ascii=False), encoding="utf-8")
    directory = tmp_path / "run"
    manifest = runner.prepare_run(source, analysis, run_dir=directory, **kwargs)
    assert manifest["preparation_status"] == "ready", manifest["preparation_error"]
    return directory, source, analysis


def forbidden(*args, **kwargs):
    raise AssertionError("network or online client must not be used")


def test_one_call_exact_input_resume_and_offline_replay(tmp_path, monkeypatch):
    directory, source, _ = setup_run(tmp_path)
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    client = FakeClient()
    first = runner.run_annotation(directory, client=client)
    assert first["status"] == "complete"
    assert first["schema_version"] == 11
    assert first["profile_schema_version"] == "security-profile-v10"
    assert first["request_validation"]["transport"] == "injected"
    assert first["request_validation"]["observed"] is False
    assert len(client.prompts) == first["counts"]["logical_calls"] == 1
    assert first["validation"]["profile_count"] == 3
    prompt = client.prompts[0]
    assert "OLD_CANDIDATE_CANARY" not in prompt and "OLD_REVIEW_CANARY" not in prompt
    material = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
    assert material["cfg"] == graph()
    assert material["source"]["files"][1]["content"] == "完整附加文件\r\n第二行\n"
    assert prompt.encode() == (directory / "inputs/prompt.txt").read_bytes()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    resumed = runner.run_annotation(directory, client_factory=forbidden)
    replayed = runner.replay_run(directory)
    assert first == resumed == replayed
    assert before == {p.name: p.read_bytes() for p in source.iterdir()}
    assert (directory / "replay/report.md").is_file()
    sidecar = json.loads((directory / "audit/location-evidences.json").read_text(encoding="utf-8"))
    assert first["location_evidences_sha256"] == runner.canonical_sha256(sidecar)
    assert "location_evidences" not in first
    assert first["validation"]["location_evidence_count"] == sum(map(len, sidecar.values()))
    assert first["validation"]["sink_boundary_count"] == len(first["sink_boundaries"])
    sink_file = directory / "sink-boundaries.json"
    assert json.loads(sink_file.read_text(encoding="utf-8")) == first["sink_boundaries"]
    assert first["compilation"]["sink_boundaries_sha256"] == runner.canonical_sha256(first["sink_boundaries"])
    assert (directory / "replay/sink-boundaries.json").read_bytes() == sink_file.read_bytes()
    assert (directory / "replay/audit/location-evidences.json").read_bytes() == (directory / "audit/location-evidences.json").read_bytes()


@pytest.mark.parametrize("target", ["missing", "changed", "changed_and_rehashed", "bad_json", "bad_result_json"])
def test_sidecar_tampering_refuses_resume_and_replay_without_api(tmp_path, monkeypatch, target):
    directory, _, _ = setup_run(tmp_path)
    client = FakeClient()
    first = runner.run_annotation(directory, client=client)
    sidecar_path = directory / "audit/location-evidences.json"
    if target == "missing":
        sidecar_path.unlink()
    elif target == "bad_json":
        sidecar_path.write_text("{not valid JSON", encoding="utf-8")
    elif target == "bad_result_json":
        (directory / "result.json").write_text("{not valid JSON", encoding="utf-8")
    else:
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        next(iter(sidecar.values()))[0]["reason"] = "篡改后的解释"
        sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False), encoding="utf-8")
        if target == "changed_and_rehashed":
            first["location_evidences_sha256"] = runner.canonical_sha256(sidecar)
            (directory / "result.json").write_text(json.dumps(first, ensure_ascii=False), encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    with pytest.raises(runner.RunIdentityError, match="location evidence"):
        runner.run_annotation(directory, client_factory=forbidden)
    with pytest.raises(runner.RunIdentityError, match="location evidence"):
        runner.replay_run(directory)
    assert (directory / "result.json").read_bytes() == before
    assert len(client.prompts) == 1


def test_sink_projection_tampering_refuses_resume_and_replay_without_resend(tmp_path, monkeypatch):
    directory, _, _ = setup_run(tmp_path)
    client = FakeClient()
    first = runner.run_annotation(directory, client=client)
    assert first["status"] == "complete"
    (directory / "sink-boundaries.json").write_text('[{"exposure_level":3}]', encoding="utf-8")
    before = (directory / "result.json").read_bytes()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    with pytest.raises(runner.RunIdentityError, match="sink boundary projection"):
        runner.run_annotation(directory, client_factory=forbidden)
    with pytest.raises(runner.RunIdentityError, match="sink boundary projection"):
        runner.replay_run(directory)
    assert before == (directory / "result.json").read_bytes()
    assert len(client.prompts) == 1


def test_location_evidence_save_precedes_success_commit_and_recovers_without_resend(tmp_path, monkeypatch):
    directory, _, _ = setup_run(tmp_path)
    client = FakeClient()
    original = runner.ArtifactWriter.json
    order = []
    def failing_write(self, path, value):
        order.append(Path(path))
        if Path(path) == directory / "audit/location-evidences.json":
            raise OSError("simulated sidecar write failure")
        return original(self, path, value)
    monkeypatch.setattr(runner.ArtifactWriter, "json", failing_write)
    with pytest.raises(OSError, match="sidecar"):
        runner.run_annotation(directory, client=client)
    assert not (directory / "result.json").exists()
    assert (directory / "calls/annotation/a001/call.json").is_file()
    monkeypatch.setattr(runner.ArtifactWriter, "json", original)
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    recovered = runner.run_annotation(directory, client_factory=forbidden)
    assert recovered["status"] == "complete"
    assert len(client.prompts) == recovered["counts"]["logical_calls"] == 1


@pytest.mark.parametrize("effects,mode,expected", [
    (["transform", "transform"], "model", ["model_observe", "transform", "model_observe", "transform"]),
    (["context_write", "transform", "context_write"], "local", ["context_write", "transform", "context_write"]),
])
def test_ordered_repeated_effects_survive_single_call_and_zero_api_replay(tmp_path, monkeypatch, effects, mode, expected):
    directory, _, _ = setup_run(tmp_path)
    class Ordered(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            material = json.loads(prompt.split("\nINPUT_JSON\n", 1)[1])
            response["profiles"]["ir_filter"] = profile(
                material, "ir_filter", operator=["llm"], roles=["sink", "transformer"],
                effects=effects,
            )
            with_specs(material, response)
            response.pop("sink_boundaries")
            for ir_id, spec in response["transfer_specs"].items():
                spec.pop("precedence")
                selected_mode = mode if ir_id == "ir_filter" else "local"
                spec["events"] = [{"kind": "processing", "mode": selected_mode, "returns": [],
                                   "events": [event], "evidences": event["atomic_ops"][0]["evidences"]}
                                  for event in spec["events"]]
            return response
    client = Ordered()
    first = runner.run_annotation(directory, client=client)
    assert first["status"] == "complete"
    assert len(client.prompts) == first["counts"]["logical_calls"] == 1
    assert first["profiles"]["ir_filter"]["effects"] == expected
    effect_evidence = [e for e in first["profiles"]["ir_filter"]["evidences"] if e["field"] == "effects"]
    assert sorted({e["effect_index"] for e in effect_evidence}) == list(range(len(expected)))
    assert (directory / "audit/raw-annotation.json").is_file()
    assert (directory / "audit/compiled-response.json").is_file()
    assert (directory / "audit/compilation-map.json").is_file()
    monkeypatch.setattr(runner, "RecordingClient", forbidden)
    assert runner.run_annotation(directory, client_factory=forbidden) == first
    assert runner.replay_run(directory) == first


def test_partial_order_completes_and_replays(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    class PartialOrder(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            response["transfer_specs"]["ir_filter"]["order"] = "partial"
            return response
    result = runner.run_annotation(directory, client=PartialOrder())
    assert result["status"] == "complete"
    assert result["transfer_specs"]["ir_filter"]["order"] == "partial"
    assert "unresolved" not in result
    assert not (directory / "unresolved.json").exists()
    assert runner.replay_run(directory) == result


@pytest.mark.parametrize("change", [
    {"identity": "skill-ir-security-profile-v1", "schema_version": 1},
    {"profile_schema_version": "security-profile-v1"},
    {"identity": "skill-ir-security-profile-v2", "schema_version": 2},
    {"profile_schema_version": "security-profile-v2"},
    {"identity": "skill-ir-security-profile-v3", "schema_version": 3},
    {"profile_schema_version": "security-profile-v3"},
    {"identity": "skill-ir-security-profile-v4", "schema_version": 4},
    {"profile_schema_version": "security-profile-v4"},
])
def test_legacy_run_or_profile_identity_is_rejected_without_reinterpretation(tmp_path, change):
    directory, _, _ = setup_run(tmp_path)
    path = directory / "manifest.json"
    manifest = runner._unseal(json.loads(path.read_text(encoding="utf-8")))
    manifest.update(change)
    path.write_text(json.dumps(runner._seal(manifest)), encoding="utf-8")
    before = path.read_bytes()
    for action in (lambda: runner.run_annotation(directory, client_factory=forbidden),
                   lambda: runner.replay_run(directory)):
        with pytest.raises(runner.RunIdentityError, match="Unsupported"):
            action()
    assert path.read_bytes() == before
    assert not (directory / runner.CALL_PATH).exists()


def test_legacy_unresolved_rejected_and_semantic_failure_replays(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    class Failure(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            evidence = response["profiles"]["ir_read"]["evidences"][0]
            return {"outcome": "cannot_assess", "failure": {
                "reason": "必要的来源约束互相冲突，不能给出一致的标注。",
                "instruction_ids": ["ir_read"],
                "evidences": [{key: evidence[key] for key in ("basis", "ref_id", "quote", "reason")}],
            }}
    result = runner.run_annotation(directory, client=Failure())
    assert result["status"] == "semantic_failure"
    assert result["error_kind"] == "cannot_assess"
    assert result["profiles"] == {}
    assert runner.replay_run(directory) == result


@pytest.mark.parametrize("kind", ["json", "missing", "quote", "enum", "duplicate_key"])
def test_invalid_response_is_saved_without_repair(tmp_path, kind):
    directory, _, _ = setup_run(tmp_path)
    class Invalid(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            if kind == "json": return "{invalid"
            if kind == "duplicate_key": return '{"profiles":{},"profiles":{},"unresolved":[]}'
            if kind == "missing": del response["profiles"]["ir_return"]
            if kind == "quote": response["profiles"]["ir_read"]["evidences"][0]["quote"] = "NOT_IN_GRAPH"
            if kind == "enum": response["profiles"]["ir_read"]["effects"] = ["safe"]
            return response
    client = Invalid()
    result = runner.run_annotation(directory, client=client)
    assert result["status"] == "invalid_response"
    assert result["validation"]["status"] == "failed"
    assert result["profiles"] == {}
    assert len(client.prompts) == 1
    assert runner.run_annotation(directory, client_factory=forbidden) == result
    assert runner.replay_run(directory) == result


@pytest.mark.parametrize("interrupt", [False, True])
def test_failed_call_never_resent(tmp_path, interrupt):
    directory, _, _ = setup_run(tmp_path)
    class Failed:
        def complete(self, prompt):
            if interrupt: raise KeyboardInterrupt("user stop")
            raise RuntimeError("accepted response incomplete")
    result = runner.run_annotation(directory, client=Failed())
    assert result["status"] == ("interrupted" if interrupt else "execution_error")
    for restored in (runner.run_annotation(directory, client_factory=forbidden), runner.replay_run(directory)):
        assert restored["status"] == result["status"]
        assert restored["reason"] == result["reason"]
        assert restored["counts"]["logical_calls"] == 1


def test_interruption_before_call_and_replay(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    stop = Event()
    stop.set()
    result = runner.run_annotation(directory, stop_event=stop, client_factory=forbidden)
    assert result["status"] == "interrupted"
    assert result["counts"]["logical_calls"] == 0
    assert runner.replay_run(directory) == result


def test_stop_requested_from_progress_does_not_start_a_request(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    stop = Event()
    client = FakeClient()
    result = runner.run_annotation(directory, stop_event=stop, client=client,
                                   progress=lambda _: stop.set())
    assert result["status"] == "interrupted"
    assert not client.prompts
    assert result["counts"]["logical_calls"] == 0
    assert runner.replay_run(directory) == result
    report = (directory / "report.md").read_text(encoding="utf-8")
    assert "没有记录未决项或执行问题" not in report


def test_accepted_response_interruption_replay_then_resume_without_resend(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    stop = Event()
    class Accepted(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            stop.set()
            return response
    result = runner.run_annotation(directory, client=Accepted(), stop_event=stop)
    assert result["status"] == "interrupted"
    assert result["counts"]["logical_calls"] == 1
    assert runner.replay_run(directory) == result
    resumed = runner.run_annotation(directory, client_factory=forbidden)
    assert resumed["status"] == "complete"
    assert resumed["counts"]["logical_calls"] == 1
    assert runner.replay_run(directory) == resumed


@pytest.mark.parametrize("target", ["source", "analysis", "prompt", "manifest", "implementation", "config"])
def test_identity_changes_refuse_without_call_or_result_overwrite(tmp_path, monkeypatch, target):
    directory, source, analysis = setup_run(tmp_path, config={"model": "model-a"})
    before = runner.run_annotation(directory, client=FakeClient())
    result_bytes = (directory / "result.json").read_bytes()
    kwargs = {}
    if target == "source": (source / "SKILL.md").write_text("changed", encoding="utf-8")
    if target == "analysis": analysis.write_text("{}", encoding="utf-8")
    if target == "prompt": (directory / "inputs/prompt.txt").write_text("changed", encoding="utf-8")
    if target == "manifest":
        manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
        manifest["graph_sha256"] = "0" * 64
        (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    if target == "implementation": monkeypatch.setattr(runner, "implementation_provenance", lambda: {})
    if target == "config": kwargs["config"] = {"model": "model-b"}
    with pytest.raises((ValueError, OSError)):
        runner.run_annotation(directory, client_factory=forbidden, **kwargs)
    assert (directory / "result.json").read_bytes() == result_bytes


def test_offline_replay_uses_frozen_source_not_changed_original(tmp_path):
    directory, source, analysis = setup_run(tmp_path)
    original = runner.run_annotation(directory, client=FakeClient())
    (source / "SKILL.md").write_text("changed after run", encoding="utf-8")
    analysis.write_text("{}", encoding="utf-8")
    assert runner.replay_run(directory) == original


def test_verify_prepared_is_readonly_and_repeat_prepare_rejected(tmp_path):
    directory, source, analysis = setup_run(tmp_path)
    before = {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    assert runner.verify_prepared(directory)["preparation_status"] == "ready"
    assert before == {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    with pytest.raises(runner.RunIdentityError):
        runner.prepare_run(source, analysis, run_dir=directory)


def test_nested_output_rejected_before_writing(tmp_path):
    directory, source, analysis = setup_run(tmp_path)
    nested = source / "generated"
    with pytest.raises(ValueError, match="nested"):
        runner.prepare_run(source, analysis, run_dir=nested)
    assert not nested.exists()


def test_invalid_graph_input_never_calls(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("# test", encoding="utf-8")
    analysis = tmp_path / "invalid.json"
    analysis.write_text('{"cfg":{}}', encoding="utf-8")
    directory = tmp_path / "run"
    manifest = runner.prepare_run(source, analysis, run_dir=directory)
    assert manifest["preparation_status"] == "input_error"
    result = runner.run_annotation(directory, client_factory=forbidden)
    assert result["status"] == "input_error"
    assert result["counts"]["logical_calls"] == 0
    assert runner.replay_run(directory) == result


def test_response_credential_is_redacted_and_rejected_not_retried(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    secret = "test-sensitive-credential-1234567"
    class Overlap(FakeClient):
        def complete(self, prompt):
            response = super().complete(prompt)
            response["profiles"]["ir_read"]["evidences"][0]["reason"] = secret
            return response
    result = runner.run_annotation(directory, client=Overlap(), secrets=(secret,))
    assert result["status"] == "execution_error"
    assert "credential" in result["reason"]
    for path in directory.rglob("*"):
        if path.is_file(): assert secret.encode() not in path.read_bytes()
    assert runner.run_annotation(directory, client_factory=forbidden, secrets=(secret,)) == result
    assert runner.replay_run(directory) == result


def test_prompt_credential_overlap_refuses_before_call(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    result = runner.run_annotation(directory, client_factory=forbidden, secrets=("配置处理",))
    assert result["status"] == "input_error"
    assert result["counts"]["logical_calls"] == 0
    assert runner.replay_run(directory) == result


def test_interrupt_during_local_validation_replays_interruption(tmp_path, monkeypatch):
    directory, _, _ = setup_run(tmp_path)
    original = runner.compile_response
    def interrupted(*args):
        raise KeyboardInterrupt("local validation interrupted")
    monkeypatch.setattr(runner, "compile_response", interrupted)
    result = runner.run_annotation(directory, client=FakeClient())
    monkeypatch.setattr(runner, "compile_response", original)
    assert result["status"] == "interrupted"
    assert runner.replay_run(directory) == result
    assert runner.run_annotation(directory, client_factory=forbidden)["status"] == "complete"


def test_missing_injected_client_is_replayed_as_execution_error(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    result = runner.run_annotation(directory)
    assert result["status"] == "execution_error"
    assert result["counts"]["logical_calls"] == 0
    assert runner.replay_run(directory) == result


def test_uncertain_saved_call_has_no_fallback_client(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    runner.run_annotation(directory, client=FakeClient())
    path = directory / runner.CALL_PATH / "call.json"
    call = json.loads(path.read_text(encoding="utf-8"))
    call["status"] = "running"
    path.write_text(json.dumps(call), encoding="utf-8")
    # Fully accepted transport response survives an interrupted call-finalization.
    assert runner.run_annotation(directory, client_factory=forbidden)["status"] == "complete"
    (directory / runner.CALL_PATH / "transport.json").write_text("[]", encoding="utf-8")
    # Erasing the accepted request trace is an identity violation in v8, not
    # authorization to resend or silently replace the previously saved result.
    before = (directory / "result.json").read_bytes()
    with pytest.raises(runner.RunIdentityError, match="request identity"):
        runner.run_annotation(directory, client_factory=forbidden)
    assert (directory / "result.json").read_bytes() == before


def test_offline_mode_rejects_client_injection(tmp_path):
    directory, _, _ = setup_run(tmp_path)
    with pytest.raises(ValueError, match="Offline"):
        runner.run_annotation(directory, replay=True, client=FakeClient())


@pytest.mark.parametrize("field,value", [
    ("schema_version", 6),
    ("profile_schema_version", "security-profile-v6"),
    ("identity", "skill-ir-security-profile-v6"),
])
def test_v7_rejects_prior_annotation_identity_without_calls(tmp_path, field, value):
    directory, _, _ = setup_run(tmp_path)
    path = directory / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest[field] = value
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(runner.RunIdentityError, match="Unsupported"):
        runner.run_annotation(directory, client_factory=forbidden)
    with pytest.raises(runner.RunIdentityError, match="Unsupported"):
        runner.replay_run(directory)
    assert not (directory / runner.CALL_PATH).exists()
