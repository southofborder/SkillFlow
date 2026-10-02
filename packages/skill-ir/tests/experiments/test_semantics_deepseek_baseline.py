"""Offline provider-switch identity, full-corpus isolation and SSE compatibility."""

from dataclasses import replace
from copy import deepcopy
import importlib
import io
import json
from pathlib import Path

import pytest


BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"


@pytest.fixture
def entry(monkeypatch):
    monkeypatch.syspath_prepend(str(BASE / "tools"))
    module = importlib.import_module("run_deepseek_baseline")

    def forbidden(*args, **kwargs):
        pytest.fail("DeepSeek tests must never use the network")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    return module


def resolve(entry):
    return entry.resolve_experiment(entry.CONFIG, environ={
        "LLM_API_KEY": "offline-provider-secret", "LLM_ENDPOINT": "https://wrong.invalid/v1",
        "LLM_MODEL": "wrong-model", "LLM_REASONING_EFFORT": "low", "LLM_TIMEOUT": "1",
        "LLM_MAX_RETRIES": "99", "LLM_RETRY_BASE_MS": "99", "LLM_RETRY_MAX_BACKOFF_MS": "99",
    })


@pytest.fixture
def locked_reference_identity(entry):
    """Read immutable reference bytes; tests never update the locked baseline."""
    change = json.loads(entry.CHANGE_MANIFEST.read_text(encoding="utf-8"))
    reference = change["prior_runs"][change["semantic_reference_index"]]
    return json.loads((entry.BASE / reference["directory"] / "experiment.json").read_text(encoding="utf-8"))


@pytest.fixture
def matching_source_provenance(entry, monkeypatch, locked_reference_identity):
    """Model the provider-only switch's explicitly unchanged-source premise.

    Production has evolved since this immutable baseline was recorded. These
    unit tests exercise provider preflight and mocked transport, not permission
    to resume the historical run with today's code. The real runner still
    rejects source drift; its guard is tested independently below.
    """
    current = entry.runtime_provenance()
    current["source_sha256"] = deepcopy(locked_reference_identity["provenance"]["source_sha256"])
    monkeypatch.setattr(entry, "runtime_provenance", lambda: deepcopy(current))
    return current


@pytest.fixture
def matching_prompt_identity(entry, monkeypatch, locked_reference_identity):
    """Isolate the old provider-only experiment's unchanged-prompt premise.

    Only the provider entrypoint's compared prompt digest is fixed here. Case
    IDs, splits, source digests, and all other identity fields still come from
    the real identity builder. Actual prompt construction and mocked transport
    remain real. This is not permission to run today's prompt as that baseline;
    the separate drift test below exercises the real prompt-identity guard.
    """
    build_identity = entry.experiment_identity
    locked = {case["id"]: case["prompt_sha256"]
              for case in locked_reference_identity["cases"]}

    def identity_with_locked_prompt(*args, **kwargs):
        current = build_identity(*args, **kwargs)
        for case in current["cases"]:
            if case["id"] in locked:
                case["prompt_sha256"] = locked[case["id"]]
        return current

    monkeypatch.setattr(entry, "experiment_identity", identity_with_locked_prompt)


def test_offline_check_reads_no_credentials_schedules_all_frozen_cases(entry, matching_source_provenance, matching_prompt_identity, tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    # A nonexistent env file proves offline preflight does not discover or open it.
    run = tmp_path / "new-deepseek"
    assert entry.main(["--run-dir", str(run), "--env-file", str(tmp_path / "absent.env"), "--split", "all", "--check"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["planned"] == report["selected"] == 90
    assert report["mode"] == "offline_deepseek_preflight"
    assert report["provider_change"]["inherited_trials"] == 0
    assert report["provider_change"]["case_and_prompt_identity_equal"]
    assert report["provider_change"]["production_source_identity_equal"]
    assert report["semantic_review_status"] == "pending_joint_review"
    assert report["variants"] == [entry.EXPECTED_VARIANT]
    assert not run.exists()


def test_explicit_provider_settings_override_all_nonsecret_environment_values(entry):
    resolved = resolve(entry)
    entry.validate_deepseek_baseline(resolved)
    assert resolved.variants[0].snapshot() == entry.EXPECTED_VARIANT
    assert len(resolved.cases) == 30
    assert len({case.id for case in resolved.cases}) == 30
    assert "offline-provider-secret" not in json.dumps(entry.experiment_identity(resolved, entry.baseline_definition()))


@pytest.mark.parametrize("field,value", [("endpoint", "https://proxy.invalid/chat/completions"), ("model", "deepseek-flash"), ("reasoning_effort", "high"), ("max_retries", 99)])
def test_runtime_provider_drift_is_rejected(entry, field, value):
    resolved = resolve(entry)
    variant = replace(resolved.variants[0], config=replace(resolved.variants[0].config, **{field: value}))
    with pytest.raises(ValueError, match="pinned official provider"):
        entry.validate_deepseek_baseline(replace(resolved, variants=(variant,)))


@pytest.mark.parametrize("relative", ["frozen/corpus/inputs/controlled/N01/out", "runs/baseline-sol-max-v1", "runs/baseline-sol-max-sse-20260910/new", "runs"])
def test_frozen_and_prior_run_directories_rejected_without_mutation(entry, relative):
    with pytest.raises(ValueError, match="frozen corpus|separate new run directory"):
        entry.require_deepseek_directory(BASE / relative)


def test_unrelated_existing_identity_cannot_be_reused(entry, tmp_path):
    (tmp_path / "experiment.json").write_text('{"provenance":{"transport":{"protocol":"chat-completions-sse-v1"}}}')
    with pytest.raises(ValueError, match="model results cannot be mixed"):
        entry.require_deepseek_directory(tmp_path)


def test_provenance_binds_unchanged_inputs_prompts_production_and_separate_runs(entry, matching_source_provenance, matching_prompt_identity):
    resolved = resolve(entry)
    provenance = entry.provider_provenance(resolved, entry.baseline_definition())
    change = provenance["provider_change"]
    assert len(change["prior_runs"]) == 3
    assert len(change["provider_checks"]) == 2
    assert change["target_variant"]["model"] == "deepseek-v4-flash"
    assert "returned model deepseek-flash" in change["requested_returned_model_note"]
    assert change["config_sha256"] == entry._sha(entry.CONFIG)
    assert change["entrypoint_sha256"] == entry._sha(Path(entry.__file__))
    assert provenance["transport"]["source_sha256"]["stream_transport.py"] == entry._sha(Path(entry.stream_transport.__file__))
    from skill_ir.extraction.prompt import build_whole_skill_prompt
    for case in resolved.cases:
        prompt = build_whole_skill_prompt(case.package)
        assert case.source.is_relative_to(BASE / "frozen/corpus/inputs")
        assert prompt.count("<skill-file path=") == len(case.package.files)
        for marker in ('"coverage_targets"', '"acceptable_variants"', '"must_not_infer"', "待共同复核"):
            assert marker not in prompt


def test_changed_production_sources_cannot_resume_provider_only_baseline(entry, matching_source_provenance, matching_prompt_identity, monkeypatch):
    drifted = deepcopy(matching_source_provenance)
    source = next(iter(drifted["source_sha256"]))
    drifted["source_sha256"][source] = "0" * 64
    monkeypatch.setattr(entry, "runtime_provenance", lambda: deepcopy(drifted))
    with pytest.raises(ValueError, match="locked semantic/runtime sources: source_sha256"):
        entry.provider_provenance(resolve(entry), entry.baseline_definition())


def test_current_changed_prompt_cannot_resume_provider_only_baseline(
    entry, matching_source_provenance, locked_reference_identity,
):
    # Intentionally omit matching_prompt_identity: these are actual current
    # prompts. Equal source provenance alone must not bypass exact prompt locks.
    resolved = resolve(entry)
    splits = entry.baseline_definition()
    actual_cases = entry.experiment_identity(resolved, splits)["cases"]
    locked_cases = locked_reference_identity["cases"]
    without_prompt = lambda cases: [
        {key: value for key, value in case.items() if key != "prompt_sha256"}
        for case in cases
    ]
    assert without_prompt(actual_cases) == without_prompt(locked_cases)
    assert all(actual["prompt_sha256"] != locked["prompt_sha256"]
               for actual, locked in zip(actual_cases, locked_cases, strict=True))
    with pytest.raises(ValueError, match="frozen case or exact Prompt identity"):
        entry.provider_provenance(resolved, splits)


@pytest.mark.parametrize("field", ["report_sha256", "experiment_sha256"])
def test_prior_record_tampering_is_rejected(entry, tmp_path, monkeypatch, field):
    manifest = json.loads(entry.CHANGE_MANIFEST.read_text(encoding="utf-8"))
    manifest["prior_runs"][2][field] = "0" * 64
    path = tmp_path / "changed-manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(entry, "CHANGE_MANIFEST", path)
    with pytest.raises(ValueError, match="Prior run provenance changed"):
        entry.provider_provenance(resolve(entry), entry.baseline_definition())


def test_provider_authentication_evidence_tampering_is_rejected(entry, tmp_path, monkeypatch):
    manifest = json.loads(entry.CHANGE_MANIFEST.read_text(encoding="utf-8"))
    manifest["provider_checks"][1]["sha256"] = "0" * 64
    path = tmp_path / "changed-manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(entry, "CHANGE_MANIFEST", path)
    with pytest.raises(ValueError, match="availability preflight provenance changed"):
        entry.provider_provenance(resolve(entry), entry.baseline_definition())


def test_mocked_provider_trial_keeps_current_prompt_and_reasoning_out_of_candidate(entry, matching_source_provenance, matching_prompt_identity, tmp_path, monkeypatch):
    # The fixtures simulate the provider-only protocol's locked premises. This
    # exercises current prompts and mocked SSE, not historical prompt replay.
    requests = []
    candidate = {"entry_block_ref": "finish", "blocks": [{"block_ref": "finish", "block_name": "结束", "instructions": [{"instruction_ref": "finish", "opcode": "return", "inputs": [{"type": "literal", "literal_value": "仅用于离线结构测试"}]}]}], "edges": []}

    class Response(io.BytesIO):
        status = 200
        headers = {"Content-Type": "text/event-stream", "x-request-id": "offline-deepseek"}

    def respond(request, timeout):
        payload = json.loads(request.data)
        requests.append(payload)
        assert request.full_url == "https://api.deepseek.com/chat/completions"
        assert payload["model"] == "deepseek-v4-flash" and payload["reasoning_effort"] == "max"
        assert payload["stream"] is True and payload["stream_options"] == {"include_usage": True}
        assert "待共同复核" not in payload["messages"][0]["content"]
        events = [
            {"delta": {"reasoning_content": "PRIVATE_REASONING_SENTINEL"}, "finish_reason": None},
            {"delta": {"content": json.dumps(candidate, ensure_ascii=False)}, "finish_reason": None},
            {"delta": {}, "finish_reason": "stop"},
        ]
        raw = "".join("data: " + json.dumps({"id": "offline-deepseek", "model": "deepseek-flash", "choices": [{"index": 0, **item}]}, ensure_ascii=False) + "\n\n" for item in events)
        raw += 'data: {"id":"offline-deepseek","model":"deepseek-flash","choices":[],"usage":{"prompt_tokens":10,"completion_tokens":5,"total_tokens":15}}\n\ndata: [DONE]\n\n'
        return Response(raw.encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", respond)
    monkeypatch.setenv("LLM_API_KEY", "offline-provider-secret")
    run = tmp_path / "deepseek-run"
    arguments = ["--run-dir", str(run), "--max-new-trials", "1"]
    assert entry.main(arguments) == 0
    report = json.loads((run / "report.json").read_text(encoding="utf-8"))
    assert len(report["trials"]) == 90
    assert sum(item["status"] == "complete" for item in report["trials"]) == 1
    assert sum(item["status"] == "not_run" for item in report["trials"]) == 89
    trial = next(item for item in report["trials"] if item["status"] == "complete")
    trace_path = run / trial["artifacts"] / "trace.json"
    trace_bytes = trace_path.read_bytes()
    call = json.loads(trace_bytes)["calls"][0]
    from skill_ir.extraction.prompt import build_whole_skill_prompt
    case = next(case for case in resolve(entry).cases if case.id == trial["case"])
    expected_prompt = build_whole_skill_prompt(case.package)
    assert requests[0]["messages"][0]["content"] == call["prompt"] == expected_prompt
    assert call["response"] == json.dumps(candidate, ensure_ascii=False)
    assert "PRIVATE_REASONING_SENTINEL" in call["http_attempts"][0]["stream"]["raw_sse"]
    assert call["http_attempts"][0]["returned_model"] == "deepseek-flash"
    assert call["usage"]["total_tokens"] == 15
    assert b"offline-provider-secret" not in trace_bytes
    # A same-identity resume starts the next repetition and leaves the first
    # trial byte-for-byte intact; no trial from any previous provider is copied.
    assert entry.main(arguments) == 0
    assert len(requests) == 2 and trace_path.read_bytes() == trace_bytes
    assert requests[1]["messages"][0]["content"] == expected_prompt
