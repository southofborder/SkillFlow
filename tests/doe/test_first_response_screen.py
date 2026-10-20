from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
from threading import Event

import pytest

from skillflow.common.llm.config import OutputTruncatedError
from skillflow.common.recording import ResponseIntegrityError, canonical_sha256, sha_file
from tools.doe.prompt_screen import (
    load_screen, prepare_screen, replay_screen, run_screen,
)
from tools.doe.prompt_screen_fixtures import screen_fixtures, ev


CONFIG = {"endpoint": "https://example.invalid/v1/chat/completions", "model": "screen-test",
          "reasoning_effort": "max", "timeout_ms": 1000, "max_retries": 0,
          "retry_base_ms": 1, "retry_max_backoff_ms": 1, "response_format": "json_object"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def template(tmp_path_factory):
    directory = tmp_path_factory.mktemp("first-response-screen")
    baseline = directory / "baseline"
    root = Path(__file__).resolve().parents[2]
    sources = root / "src"
    files = {}
    for path in sorted((sources / "skillflow").rglob("*.py")):
        target = baseline / "src" / path.relative_to(sources)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        files[target.relative_to(baseline).as_posix()] = sha_file(target)
    (baseline / "files.json").write_text(json.dumps(files), encoding="utf-8")
    prepare_screen(directory / "prepared", baseline_dir=baseline, config=CONFIG)
    return directory / "prepared"


@pytest.fixture
def prepared(tmp_path, template):
    return Path(shutil.copytree(template, tmp_path / "screen"))


class Client:
    def __init__(self, response, event=None):
        self.response, self.event, self.prompts = response, event, []

    def complete(self, prompt):
        self.prompts.append(prompt)
        assert len(self.prompts) == 1, "No screen arm may call its client twice"
        if self.event is not None:
            self.event.set()
        if isinstance(self.response, BaseException):
            raise self.response
        return deepcopy(self.response)


def clients(directory):
    manifest = load_screen(directory)
    return {(case["name"], arm): Client(read(directory / "audit/fixtures" / (case["name"] + ".json"))["reference_response"])
            for case in manifest["cases"] for arm in ("baseline", "revised")}


def snapshot(directory):
    return {p.relative_to(directory).as_posix(): sha_file(p) for p in directory.rglob("*")
            if p.is_file() and p.name not in {".runner.lock", "replay.json"}}


def test_eight_first_responses_are_durable_and_replay_without_api(prepared):
    live = clients(prepared)
    result = run_screen(prepared, clients=live)
    assert result["status"] == "complete"
    assert len(result["results"]) == 8
    assert {r["stage"] for r in result["results"]} == {"annotation", "review"}
    assert all(r["status"] == "valid" and r["metrics"]["logical_calls"] == 1 for r in result["results"])
    assert all(r["semantic_acceptance"] == "not_assessed" for r in result["results"])
    assert all(r["metrics"]["usage"]["total_tokens"]["total"] is None for r in result["results"])
    assert all(not r["metrics"]["http_attempts_observed"] for r in result["results"])
    assert len(list(prepared.glob("cases/*/*/calls/*/a001/call.json"))) == 8
    assert not list(prepared.rglob("a002"))
    metrics = read(prepared / "metrics.json")
    assert metrics["structural_corrections"] == metrics["task_calls"] == metrics["semantic_repairs"] == 0
    assert metrics["gate"] == {"structural": True, "semantic": "pending_external_review", "formal_rerun": "not_scheduled"}
    before = snapshot(prepared)
    assert replay_screen(prepared)["api_calls"] == 0
    assert snapshot(prepared) == before
    assert all(len(client.prompts) == 1 for client in live.values())
    assert not re.search(r"[\u4e00-\u9fff]", (prepared / "report.md").read_text(encoding="utf-8"))


@pytest.mark.parametrize("kind", ["syntax", "duplicate", "schema", "reference", "review_schema", "review_reference"])
def test_invalid_first_response_is_diagnosed_without_correction(prepared, kind):
    live = clients(prepared)
    key = ("review_a_display", "revised") if kind.startswith("review_") else ("annotation_a_receipt", "revised")
    candidate = deepcopy(live[key].response)
    if kind == "syntax": candidate = '{"outcome":'
    elif kind == "duplicate": candidate = '{"outcome":"completed","outcome":"completed"}'
    elif kind == "schema": candidate["extra_field"] = 1
    elif kind == "reference": candidate["demands"][0]["target"]["instruction_id"] = "ir_missing"
    elif kind == "review_schema": candidate["extra_field"] = 1
    else: candidate["findings"] = [{"domain": "annotation", "target_ids": ["absent"], "explanation": "Unsupported target", "evidences": [ev()], "suggestion": "Use a real target."}]
    live[key] = Client(candidate)
    result = run_screen(prepared, clients=live)
    row = next(r for r in result["results"] if (r["case"], r["arm"]) == key)
    assert row["status"] == "structural_invalid"
    assert row["validation"]["diagnostics"]
    assert row["validation"]["raw_diagnostics"]
    assert row["validation"]["diagnostic_mapping"]
    assert len(live[key].prompts) == 1
    assert len(result["results"]) == 8
    assert not read(prepared / "metrics.json")["gate"]["structural"]
    assert replay_screen(prepared)["status"] == "matched"


def test_limited_normalization_retains_original_response(prepared):
    live = clients(prepared); key = ("annotation_a_receipt", "revised")
    raw = json.dumps(live[key].response) + "}"
    live[key] = Client(raw)
    result = run_screen(prepared, clients=live)
    row = next(r for r in result["results"] if (r["case"], r["arm"]) == key)
    assert row["status"] == "valid" and row["normalization"]
    call = prepared / "cases" / key[0] / key[1] / "calls/annotation/a001"
    assert read(call / "call.json")["response"] == raw
    assert read(call / "normalization.json") == row["normalization"]
    assert read(prepared / "metrics.json")["arms"]["revised"]["valid_without_normalization"] == 3
    assert replay_screen(prepared)["status"] == "matched"


@pytest.mark.parametrize("stage", ["annotation", "review"])
def test_cannot_assess_is_a_semantic_failure_not_empty_success(prepared, stage):
    live = clients(prepared)
    key = ("annotation_a_receipt" if stage == "annotation" else "review_a_display", "revised")
    material = read(prepared / "cases" / key[0] / "material.json")
    failure = {"reason": "The necessary judgment cannot be supported by this source.", "evidences": [ev()]}
    failure["instruction_ids" if stage == "annotation" else "target_ids"] = (["ir_load_loan"] if stage == "annotation" else [material["target_index"][0]["id"]])
    live[key] = Client({"outcome": "cannot_assess", "failure": failure})
    result = run_screen(prepared, clients=live)
    row = next(r for r in result["results"] if (r["case"], r["arm"]) == key)
    assert row["status"] == "semantic_failure"
    assert replay_screen(prepared)["status"] == "matched"


@pytest.mark.parametrize("error", [TimeoutError("Synthetic transport timeout"), OutputTruncatedError("finish_reason=length")])
def test_transport_and_truncation_are_recorded_not_corrected(prepared, error):
    live = clients(prepared); key = ("annotation_a_receipt", "baseline"); live[key] = Client(error)
    result = run_screen(prepared, clients=live)
    assert result["results"][0]["status"] == "execution_error"
    assert result["results"][0]["error"]["type"] == type(error).__name__
    assert len(result["results"]) == 8
    assert replay_screen(prepared)["status"] == "matched"


def test_accepted_response_interruption_resumes_without_resend(prepared):
    live = clients(prepared); event = Event(); key = ("annotation_a_receipt", "baseline")
    live[key].event = event
    first = run_screen(prepared, clients=live, stop_event=event)
    assert first["status"] == "interrupted" and len(first["results"]) == 1
    assert first["results"][0]["metrics"]["logical_calls"] == 1
    assert replay_screen(prepared)["status"] == "matched"
    event.clear()
    result = run_screen(prepared, clients=live, stop_event=event)
    assert result["status"] == "complete"
    assert all(len(client.prompts) == 1 for client in live.values())
    assert replay_screen(prepared)["status"] == "matched"


def test_transport_interruption_does_not_automatically_resend(prepared):
    live = clients(prepared); key = ("annotation_a_receipt", "baseline")
    live[key] = Client(KeyboardInterrupt())
    first = run_screen(prepared, clients=live)
    assert first["status"] == "interrupted"
    second = run_screen(prepared, clients=live)
    assert second == first
    assert len(live[key].prompts) == 1 and sum(len(c.prompts) for c in live.values()) == 1
    assert replay_screen(prepared)["status"] == "matched"


def test_pre_first_request_stop_replays_and_does_not_authorize_a_call(prepared):
    event = Event(); event.set(); live = clients(prepared)
    first = run_screen(prepared, clients=live, stop_event=event)
    assert first["status"] == "interrupted" and first["results"] == []
    assert not list(prepared.rglob("call.json"))
    assert replay_screen(prepared)["status"] == "matched"
    assert all(not client.prompts for client in live.values())
    # A partial saved decision remains partial. Replay never converts it to a
    # stop or treats either status as permission to start a missing request.
    partial = {**first, "status": "partial"}
    (prepared / "summary.json").write_text(json.dumps(partial), encoding="utf-8")
    assert replay_screen(prepared)["summary_sha256"] == canonical_sha256(partial)
    assert not list(prepared.rglob("call.json"))
    assert all(not client.prompts for client in live.values())


@pytest.mark.parametrize("target", ["prompt", "material", "config", "snapshot"])
def test_frozen_input_or_identity_tampering_fails(prepared, target):
    if target == "config":
        path = prepared / "manifest.json"; value = read(path); value["config"]["model"] = "tampered"
        path.write_text(json.dumps(value), encoding="utf-8")
    else:
        path = ({"prompt": prepared / "cases/annotation_a_receipt/revised/prompt.txt",
                 "material": prepared / "cases/annotation_a_receipt/material.json",
                 "snapshot": next((prepared / "audit/baseline-source/src").rglob("*.py"))})[target]
        path.write_bytes(path.read_bytes() + b"\nchanged")
    with pytest.raises((ValueError, ResponseIntegrityError)):
        load_screen(prepared, check_implementation=True)


def test_actual_response_tampering_fails_replay(prepared):
    run_screen(prepared, clients=clients(prepared))
    path = prepared / "cases/annotation_a_receipt/revised/calls/annotation/a001/call.json"
    value = read(path); value["response"]["expressions"].append({"altered": True})
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ResponseIntegrityError): replay_screen(prepared)


def test_prepare_rejects_secret_config_and_bad_snapshot(tmp_path, template):
    baseline = template.parent / "baseline"
    with pytest.raises(ValueError, match="public"):
        prepare_screen(tmp_path / "secret", baseline_dir=baseline, config={**CONFIG, "api_key": "not-a-real-key"})
    bad = tmp_path / "bad-baseline"; bad.mkdir()
    (bad / "files.json").write_text(json.dumps({"src/skillflow/__init__.py": "0" * 64}), encoding="utf-8")
    with pytest.raises(ValueError, match="snapshot"):
        prepare_screen(tmp_path / "bad", baseline_dir=bad, config=CONFIG)


def test_fixtures_are_held_out_and_review_controls_are_faithful(prepared):
    manifest = load_screen(prepared)
    assert [(x["stage"], x["arm"]) for x in manifest["schedule"]] == [
        ("annotation", "baseline"), ("annotation", "revised"), ("review", "revised"), ("review", "baseline"),
        ("annotation", "baseline"), ("annotation", "revised"), ("review", "revised"), ("review", "baseline")]
    for case in manifest["cases"]:
        prompts = [(prepared / "cases" / case["name"] / arm / "prompt.txt").read_text(encoding="utf-8") for arm in ("baseline", "revised")]
        inputs = [re.search(r"SKILLFLOW_PROMPT:INPUT:BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:INPUT:END", p, re.S).group(1) for p in prompts]
        assert inputs[0] == inputs[1]
        for prompt in prompts:
            teaching = re.search(r"SKILLFLOW_PROMPT:EXAMPLES:BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:EXAMPLES:END", prompt, re.S).group(1)
            assert case["name"] not in teaching
            assert "semantic_checks" not in prompt and "expected_findings" not in prompt
            assert not re.search(r"[\u4e00-\u9fff]", prompt)
    fixtures = {f["name"]: f for f in screen_fixtures()}
    b = fixtures["annotation_b_occupancy"]
    assert b["material"]["cfg"]["declared_context_keys"] == ["parking_envelope"]
    assert all(not r["gaps"] for r in b["reference"]["realizations"])
    positive = read(prepared / "audit/fixtures/review_a_display.json")
    assert positive["reference_response"]["findings"] == []
    assert "Then save" not in json.dumps(positive["material"]["source"])
    assert "caption" in positive["material"]["task"]["purpose"]["text"]
    negative = read(prepared / "audit/fixtures/review_b_dispatch.json")
    assert len(negative["reference_response"]["findings"]) == 2
    assert all(f["domain"] == "annotation" for f in negative["reference_response"]["findings"])
    imports = read(prepared / "audit/baseline-render.json")
    assert imports["network_disabled"]
    assert all(p.startswith("src/skillflow/") for p in imports["imports"].values())
