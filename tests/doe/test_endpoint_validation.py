"""Durable paired endpoint validation without network or quality retries."""
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
from threading import Event

import pytest

from skillflow.common.llm.config import OutputTruncatedError
from skillflow.common.recording import ResponseIntegrityError, injected_factory, sha_file
from skillflow.common.structural_correction import ResponseChainError
from tools.doe.endpoint_validation import (
    load_validation, prepare_validation, replay_validation, run_validation,
)
from tools.doe.summarize_pipeline_run import sum_usage


CONFIG = {
    "endpoint": "https://example.invalid/v1/chat/completions",
    "model": "endpoint-validation-test", "reasoning_effort": "max",
    "timeout_ms": 1000, "max_retries": 0, "retry_base_ms": 1,
    "retry_max_backoff_ms": 1, "response_format": "json_object",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def template(tmp_path_factory):
    directory = tmp_path_factory.mktemp("endpoint-validation")
    baseline = directory / "baseline"
    sources = Path(__file__).resolve().parents[2] / "src"
    receipt = {}
    for source in sorted((sources / "skillflow").rglob("*.py")):
        target = baseline / "src" / source.relative_to(sources)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        receipt[target.relative_to(baseline).as_posix()] = sha_file(target)
    (baseline / "files.json").write_text(json.dumps(receipt), encoding="utf-8")
    prepare_validation(directory / "prepared", baseline_dir=baseline, config=CONFIG)
    return directory / "prepared"


@pytest.fixture
def prepared(tmp_path, template):
    return Path(shutil.copytree(template, tmp_path / "validation"))


class Client:
    """Each response belongs to a new logical request, not a transport retry."""

    def __init__(self, *responses, event=None):
        self.responses = list(responses)
        self.prompts = []
        self.event = event

    def complete(self, prompt):
        index = len(self.prompts)
        self.prompts.append(prompt)
        assert index < len(self.responses), "Unexpected additional logical request"
        if self.event is not None:
            self.event.set()
        value = self.responses[index]
        if isinstance(value, BaseException):
            raise value
        return deepcopy(value)


def clients(directory):
    manifest = load_validation(directory)
    return {
        (case["name"], arm): Client(read(
            directory / "audit/fixtures" / (case["name"] + ".json")
        )["reference_response"])
        for case in manifest["cases"] for arm in ("baseline", "latest")
    }


def first_key(directory, stage="annotation", arm="latest"):
    case = next(case for case in load_validation(directory)["cases"]
                if case["stage"] == stage)
    return case["name"], arm


def row_for(result, key):
    return next(row for row in result["results"]
                if (row["case"], row["arm"]) == key)


def snapshot(directory):
    return {path.relative_to(directory).as_posix(): sha_file(path)
            for path in directory.rglob("*")
            if path.is_file() and path.name not in {".runner.lock", "replay.json"}}


def test_eight_chains_accept_first_responses_and_replay_without_network(prepared):
    live = clients(prepared)
    result = run_validation(prepared, clients=live)
    assert result["status"] == "complete"
    assert len(result["results"]) == 8
    assert {row["stage"] for row in result["results"]} == {"annotation", "review"}
    assert all(row["status"] == "complete" and row["first_response_valid"] is True
               for row in result["results"])
    assert all(row["metrics"]["logical_calls"] == 1
               and row["metrics"]["structural_corrections"] == 0
               for row in result["results"])
    assert all(row["metrics"]["usage"]["total_tokens"]["total"] is None
               and row["metrics"]["http_attempts_observed"] is False
               for row in result["results"])
    assert all(len(client.prompts) == 1 for client in live.values())
    before = snapshot(prepared)
    assert replay_validation(prepared)["api_calls"] == 0
    assert snapshot(prepared) == before
    run_validation(prepared, clients=live)
    assert all(len(client.prompts) == 1 for client in live.values())
    assert not re.search(r"[\u4e00-\u9fff]",
                         (prepared / "report.md").read_text(encoding="utf-8"))


@pytest.mark.parametrize("stage", ["annotation", "review"])
def test_multiple_structural_corrections_preserve_first_response_outcome(prepared, stage):
    live = clients(prepared)
    key = first_key(prepared, stage)
    valid = live[key].responses[0]
    # Complete schema-invalid objects are correctable; they are not transport
    # failures. Repeating an error must not impose an implicit progress limit.
    invalid = {**deepcopy(valid), "unsupported_test_field": True}
    live[key] = Client(invalid, invalid, invalid, valid)
    result = run_validation(prepared, clients=live)
    row = row_for(result, key)
    assert row["status"] == "complete"
    assert row["first_response_valid"] is False
    assert row["metrics"]["logical_calls"] == 4
    assert row["metrics"]["structural_corrections"] == 3
    assert len(live[key].prompts) == 4
    assert all("STRUCTURAL_CORRECTION_CONTEXT" in prompt
               for prompt in live[key].prompts[1:])
    assert all("CURRENT_CANDIDATE_AND_DIAGNOSTICS" in prompt
               for prompt in live[key].prompts[1:])
    assert row["accepted_call"].endswith("/a004")
    calls = sorted((prepared / "cases" / key[0] / key[1]).rglob("call.json"))
    assert len(calls) == 4
    assert read(calls[0])["response"] == invalid
    assert read(calls[-1])["response"] == valid
    assert replay_validation(prepared)["status"] == "matched"
    run_validation(prepared, clients=live)
    assert len(live[key].prompts) == 4


def test_normalization_preserves_raw_response_and_does_not_count_as_correction(prepared):
    live = clients(prepared)
    key = first_key(prepared)
    raw = json.dumps(live[key].responses[0]) + "}"
    live[key] = Client(raw)
    result = run_validation(prepared, clients=live)
    row = row_for(result, key)
    assert row["status"] == "complete" and row["first_response_valid"] is True
    assert row["first_response_valid_without_normalization"] is False
    assert row["metrics"]["structural_corrections"] == 0
    call = next((prepared / "cases" / key[0] / key[1]).rglob("call.json"))
    assert read(call)["response"] == raw
    assert (call.parent / "normalization.json").is_file()
    assert replay_validation(prepared)["status"] == "matched"


@pytest.mark.parametrize("stage", ["annotation", "review"])
def test_valid_cannot_assess_is_protocol_valid_but_not_completed_analysis(prepared, stage):
    live = clients(prepared)
    key = first_key(prepared, stage)
    material = read(prepared / "cases" / key[0] / "material.json")
    evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "This source is the scope of the unsupported assessment."}
    failure = {"reason": "Synthetic assessment failure, distinct from an empty successful result.",
               "evidences": [evidence]}
    if stage == "annotation":
        failure["instruction_ids"] = [next(iter(live[key].responses[0]["ir_semantics"]))]
    else:
        failure["target_ids"] = [material["target_index"][0]["id"]]
    live[key] = Client({"outcome": "cannot_assess", "failure": failure})
    result = run_validation(prepared, clients=live)
    row = row_for(result, key)
    assert row["status"] == "semantic_failure"
    assert row["first_response_valid"] is True
    assert row["metrics"]["logical_calls"] == 1
    assert row["metrics"]["structural_corrections"] == 0
    assert row["accepted_call"] is None
    assert replay_validation(prepared)["status"] == "matched"


@pytest.mark.parametrize("error", [
    TimeoutError("Synthetic transport timeout"),
    OutputTruncatedError("finish_reason=length"),
])
def test_transport_and_truncation_stop_the_chain_without_quality_retry(prepared, error):
    live = clients(prepared)
    key = first_key(prepared)
    live[key] = Client(error)
    result = run_validation(prepared, clients=live)
    row = row_for(result, key)
    assert row["status"] == "execution_error"
    assert row["first_response_valid"] is None
    assert row["metrics"]["logical_calls"] == 1
    assert row["metrics"]["structural_corrections"] == 0
    assert len(result["results"]) == 8
    assert replay_validation(prepared)["status"] == "matched"
    run_validation(prepared, clients=live)
    assert len(live[key].prompts) == 1


def test_accepted_interruption_resumes_without_sending_accepted_request_again(prepared):
    live = clients(prepared)
    first = load_validation(prepared)["schedule"][0]
    key = first["case"], first["arm"]
    event = Event()
    live[key].event = event
    result = run_validation(prepared, clients=live, stop_event=event)
    assert result["status"] == "interrupted"
    assert sum(len(client.prompts) for client in live.values()) == 1
    assert replay_validation(prepared)["api_calls"] == 0
    assert len(live[key].prompts) == 1
    event.clear()
    result = run_validation(prepared, clients=live, stop_event=event)
    assert result["status"] == "complete"
    assert all(len(client.prompts) == 1 for client in live.values())
    assert replay_validation(prepared)["status"] == "matched"


def test_stop_before_first_request_has_zero_calls_and_replays(prepared):
    live = clients(prepared)
    stopping = Event()
    stopping.set()
    result = run_validation(prepared, clients=live, stop_event=stopping)
    assert result["status"] == "interrupted" and result["results"] == []
    assert not list(prepared.rglob("call.json"))
    assert all(not client.prompts for client in live.values())
    assert replay_validation(prepared)["api_calls"] == 0


def test_restore_accepted_response_initializes_transport_only_for_missing_calls(prepared, monkeypatch):
    import tools.doe.endpoint_validation as validation

    manifest = load_validation(prepared)
    schedule = manifest["schedule"]
    live = clients(prepared)
    first_key = schedule[0]["case"], schedule[0]["arm"]
    stopping = Event()
    live[first_key].event = stopping
    assert run_validation(prepared, clients=live, stop_event=stopping)["status"] == "interrupted"
    pending = Client(*[live[(item["case"], item["arm"])].responses[0]
                       for item in schedule[1:]])
    created = []

    def lazy_factory(config, *, env_file=None):
        created.append(deepcopy(config))
        return injected_factory(pending), ()

    monkeypatch.setattr(validation, "streaming_factory", lazy_factory)
    result = run_validation(prepared)
    assert result["status"] == "complete"
    assert len(live[first_key].prompts) == 1
    assert len(pending.prompts) == 7
    assert len(created) == 1
    assert replay_validation(prepared)["api_calls"] == 0
    assert len(created) == 1 and len(pending.prompts) == 7


def test_paired_prompts_share_inputs_and_exclude_external_expectations(prepared):
    manifest = load_validation(prepared)
    assert len(manifest["cases"]) == 4
    assert len(manifest["schedule"]) == 8
    assert {(item["case"], item["arm"]) for item in manifest["schedule"]} == {
        (case["name"], arm) for case in manifest["cases"]
        for arm in ("baseline", "latest")}
    for case in manifest["cases"]:
        prompts = [(prepared / "cases" / case["name"] / arm / "prompt.txt").read_text(
            encoding="utf-8") for arm in ("baseline", "latest")]
        inputs = [re.search(
            r"SKILLFLOW_PROMPT:INPUT:BEGIN -->\n(.*?)\n<!-- SKILLFLOW_PROMPT:INPUT:END",
            prompt, re.S).group(1) for prompt in prompts]
        assert inputs[0] == inputs[1]
        for prompt in prompts:
            assert not re.search(r"[\u4e00-\u9fff]", prompt)
            assert '"semantic_checks"' not in prompt
            assert '"expected_relations"' not in prompt
            assert '"reference_response"' not in prompt
    assert read(prepared / "audit/baseline-render.json")["network_disabled"] is True


@pytest.mark.parametrize("target", ["prompt", "material", "config", "snapshot"])
def test_frozen_input_tamper_is_rejected_before_new_calls(prepared, target):
    first = load_validation(prepared)["schedule"][0]
    case = prepared / "cases" / first["case"]
    if target == "config":
        path = prepared / "manifest.json"
        value = read(path)
        value["config"]["model"] = "tampered"
        path.write_text(json.dumps(value), encoding="utf-8")
    else:
        path = {
            "prompt": case / first["arm"] / "prompt.txt",
            "material": case / "material.json",
            "snapshot": next((prepared / "audit/baseline-source/src").rglob("*.py")),
        }[target]
        path.write_bytes(path.read_bytes() + b"\nchanged")
    with pytest.raises((ValueError, ResponseIntegrityError)):
        load_validation(prepared, check_implementation=True)


def test_accepted_response_tamper_is_rejected_on_replay(prepared):
    run_validation(prepared, clients=clients(prepared))
    path = next(prepared.glob("cases/*/*/calls/*/a001/call.json"))
    value = read(path)
    value["response"]["unexpected_field"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises((ResponseIntegrityError, ResponseChainError)):
        replay_validation(prepared)


def test_usage_is_unknown_when_unobserved_and_breakdowns_are_not_extra_tokens():
    assert sum_usage([])["total_tokens"]["total"] is None
    attempts = [{"usage": {
        "prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180,
        "completion_tokens_details": {"reasoning_tokens": 60},
        "prompt_cache_hit_tokens": 40,
    }}]
    value = sum_usage(attempts)
    assert value["input_tokens"]["total"] == 100
    assert value["output_tokens"]["total"] == 80
    assert value["total_tokens"]["total"] == 180
    assert value["api_reported_fields"][
        "completion_tokens_details.reasoning_tokens"]["reported_subtotal"] == 60
    mixed = sum_usage([*attempts, {"usage": None}])
    assert mixed["total_tokens"]["total"] is None
    assert mixed["total_tokens"]["reported_subtotal"] == 180


def test_unexpected_validator_fault_is_not_recast_as_structural_correction(prepared, monkeypatch):
    import tools.doe.endpoint_validation as validation

    live = clients(prepared)
    key = first_key(prepared, arm="baseline")

    def fault(*args, **kwargs):
        raise RuntimeError("Synthetic implementation fault")

    monkeypatch.setattr(validation, "compile_response", fault)
    with pytest.raises(RuntimeError, match="implementation fault"):
        run_validation(prepared, clients=live)
    assert len(live[key].prompts) == 1
    assert sum(len(client.prompts) for client in live.values()) == 1
    assert not list(prepared.rglob("a002"))
