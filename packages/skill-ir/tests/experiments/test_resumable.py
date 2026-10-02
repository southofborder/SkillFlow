import io
import json
from pathlib import Path
import runpy
import threading
import urllib.error

import pytest

from skill_ir.experiments.resumable import (
    REVIEW_PENDING,
    _exclusive_run,
    run_resumable_experiment,
)


CANDIDATE = {
    "entry_block_ref": "answer",
    "constraints": ["Keep the original scope"],
    "blocks": [{
        "block_ref": "answer", "block_name": "Return answer",
        "instructions": [{
            "instruction_ref": "answer", "opcode": "return",
            "inputs": [{"type": "literal", "literal_value": "ok"}],
        }],
    }],
    "edges": [],
}


class Response:
    status = 200
    headers = {"x-request-id": "test-request"}

    def __init__(self, content=None):
        self.content = json.dumps(CANDIDATE) if content is None else content

    def read(self):
        return json.dumps({
            "model": "returned-model", "choices": [{"message": {"content": self.content}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def setup(tmp_path, monkeypatch):
    for name in ("dev", "held"):
        source = tmp_path / "inputs" / name
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("Return the input without changes", encoding="utf-8")
    # This is intentionally external to both input packages.
    write(tmp_path / "annotations/dev.json", {"secret_fact_label": "ANNOTATION_SENTINEL"})
    write(tmp_path / "dataset.json", {"cases": [
        {"id": name, "input": f"inputs/{name}"} for name in ("dev", "held")
    ]})
    config = tmp_path / "experiment.json"
    write(config, {
        "name": "resumable", "dataset": "dataset.json", "repetitions": 3,
        "variants": [{"id": "sol-max", "max_repair_rounds": 1}],
    })
    env = {
        "LLM_API_KEY": "test-secret", "LLM_ENDPOINT": "https://provider.example/v1",
        "LLM_MODEL": "gpt-5.6-sol", "LLM_REASONING_EFFORT": "max",
        "LLM_MAX_RETRIES": "1", "LLM_RETRY_BASE_MS": "1",
    }
    arguments = {
        "run_directory": tmp_path / "run",
        "case_splits": {"dev": "development", "held": "held_out"},
        "environ": env, "provenance": {"contract": "constraints-v2"},
    }

    def no_network(*args, **kwargs):
        pytest.fail("No live network is allowed in experiment tests")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    return config, arguments


def record_path(result, index=0):
    return result.run_directory / result.report["trials"][index]["artifacts"] / "record.json"


def test_split_resume_bounded_concurrency_and_annotation_isolation(setup, monkeypatch):
    config, args = setup
    requests = []
    barrier = threading.Barrier(3)

    def respond(request, timeout):
        requests.append(json.loads(request.data))
        barrier.wait(timeout=5)
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", respond)
    first = run_resumable_experiment(config, **args, split="development", workers=3)
    assert first.status == "partial"
    assert [t["status"] for t in first.report["trials"]] == ["complete"] * 3 + ["not_run"] * 3
    assert first.report["by_split"]["held_out"]["attempted"] == 0
    before = {p: p.read_bytes() for p in first.run_directory.glob("trials/dev/**/*") if p.is_file()}
    final = run_resumable_experiment(config, **args, split="held_out", workers=3)
    assert final.status == "complete" and len(requests) == 6
    assert all(path.read_bytes() == content for path, content in before.items())
    assert all("ANNOTATION_SENTINEL" not in item["messages"][0]["content"] for item in requests)
    assert final.report["semantic_review_status"] == REVIEW_PENDING
    assert all(t["semantic_review_status"] == REVIEW_PENDING for t in final.report["trials"])
    assert final.report["summary"]["structural_pass_rate"] == 1
    assert final.report["summary"]["known_token_usage"]["total_tokens"] == 90
    assert all(t["finished_at"] and t["elapsed_seconds"] >= 0 for t in final.report["trials"])
    again = run_resumable_experiment(config, **args, workers=1)
    assert again.status == "complete" and len(requests) == 6


def test_error_is_durable_and_not_retried_on_resume(setup, monkeypatch):
    config, args = setup
    requests = []

    def respond(request, timeout):
        requests.append(request)
        if len(requests) == 1:
            raise urllib.error.HTTPError(request.full_url, 403, "denied", {}, io.BytesIO(b"test-secret"))
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_resumable_experiment(config, **args, workers=1)
    assert result.status == "failed"
    assert [t["status"] for t in result.report["trials"]] == ["error"] + ["complete"] * 5
    assert "test-secret" not in str(result.report)
    again = run_resumable_experiment(config, **args, workers=2)
    assert again.status == "failed" and len(requests) == 6
    for path in again.run_directory.rglob("*.json"):
        assert "test-secret" not in path.read_text(encoding="utf-8")


def test_replays_completed_generation_after_lost_trial_commit(setup, monkeypatch):
    config, args = setup
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: requests.append(1) or Response())
    first = run_resumable_experiment(config, **args, workers=1)
    path = record_path(first)
    record = json.loads(path.read_text())
    record["status"] = "running"
    write(path, record)
    # Simulate a crash after the response checkpoint but before artifact writes.
    for name in ("analysis.json", "candidate.json", "graph.mmd"):
        (path.parent / name).unlink()
    (first.run_directory / "report.json").unlink()
    again = run_resumable_experiment(config, **args, workers=1)
    assert again.status == "complete" and len(requests) == 6
    assert again.report["trials"][0]["replayed_generations"] == 1
    assert (path.parent / "analysis.json").is_file()


def test_replay_resumes_only_an_unsent_repair_generation(setup, monkeypatch):
    config, args = setup
    responses = iter([Response("not JSON"), Response(), *[Response() for _ in range(5)]])
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: next(responses))
    first = run_resumable_experiment(config, **args, workers=1)
    path = record_path(first)
    record = json.loads(path.read_text())
    record["status"] = "running"
    write(path, record)
    trace_path = path.parent / "trace.json"
    trace = json.loads(trace_path.read_text())
    trace["calls"] = trace["calls"][:1]
    write(trace_path, trace)
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: requests.append(1) or Response())
    again = run_resumable_experiment(config, **args, workers=1)
    assert len(requests) == 1 and again.status == "complete"
    assert again.report["trials"][0]["generation_attempts"] == 2
    assert again.report["trials"][0]["replayed_generations"] == 1


def test_unknown_request_outcome_is_never_automatically_resent(setup, monkeypatch):
    config, args = setup
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: requests.append(1) or Response())
    first = run_resumable_experiment(config, **args, workers=1)
    path = record_path(first)
    record = json.loads(path.read_text())
    record["status"] = "running"
    write(path, record)
    trace_path = path.parent / "trace.json"
    trace = json.loads(trace_path.read_text())
    trace["calls"][0]["status"] = "running"
    trace["calls"][0]["response"] = None
    write(trace_path, trace)
    again = run_resumable_experiment(config, **args, workers=2)
    assert again.status == "needs_attention" and len(requests) == 6
    assert again.report["trials"][0]["status"] == "uncertain"
    assert again.report["trials"][0]["semantic_review_status"] == REVIEW_PENDING


@pytest.mark.parametrize("change", ["input", "config", "provenance", "artifact"])
def test_changed_identity_or_committed_artifact_rejected_before_network(setup, monkeypatch, change):
    config, args = setup
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: requests.append(1) or Response())
    result = run_resumable_experiment(config, **args, workers=1)
    if change == "input":
        (config.parent / "inputs/dev/SKILL.md").write_text("Changed input")
    elif change == "config":
        args["environ"]["LLM_REASONING_EFFORT"] = "high"
    elif change == "provenance":
        args["provenance"] = {"contract": "changed-contract"}
    else:
        (record_path(result).parent / "analysis.json").write_text("{}")
    with pytest.raises(ValueError, match="changed"):
        run_resumable_experiment(config, **args, workers=1)
    assert len(requests) == 6


def test_http_retries_and_structural_repair_remain_distinct(setup, monkeypatch):
    config, args = setup
    responses = iter([
        urllib.error.HTTPError("https://provider.example/v1", 500, "retry", {"Retry-After": "0"}, io.BytesIO(b"retry")),
        Response("not JSON"), Response(), *[Response() for _ in range(5)],
    ])

    def respond(*a, **kw):
        value = next(responses)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_resumable_experiment(config, **args, workers=1)
    trial = result.report["trials"][0]
    assert (trial["generation_attempts"], trial["repair_attempts"], trial["http_attempts"], trial["http_retries"]) == (2, 1, 3, 1)
    trace = json.loads((record_path(result).parent / "trace.json").read_text())
    assert trace["calls"][0]["http_attempts"][0]["http_status"] == 500
    assert trace["calls"][1]["request_id"] == "test-request"


def test_run_lock_prevents_two_runners_using_same_directory(tmp_path):
    with _exclusive_run(tmp_path / "run"):
        with pytest.raises(ValueError, match="Another runner"):
            with _exclusive_run(tmp_path / "run"):
                pytest.fail("Second lock must not be acquired")
    with _exclusive_run(tmp_path / "run"):
        pass


def test_output_directory_cannot_pollute_a_skill_input(setup):
    config, args = setup
    args["run_directory"] = config.parent / "inputs/dev/results"
    with pytest.raises(ValueError, match="separate"):
        run_resumable_experiment(config, **args)
    assert not args["run_directory"].exists()


def test_committed_record_rebuilds_report_without_resending(setup, monkeypatch):
    config, args = setup
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: requests.append(1) or Response())
    result = run_resumable_experiment(config, **args, workers=2)
    (result.run_directory / "report.json").write_text("truncated")
    again = run_resumable_experiment(config, **args, workers=1)
    assert again.status == "complete" and len(requests) == 6


def test_real_baseline_inventory_uses_only_frozen_inputs_and_original_sol_settings(monkeypatch):
    package = Path(__file__).resolve().parents[2]
    base = package / "experiments/semantics_baseline"
    monkeypatch.syspath_prepend(str(base / "tools"))
    namespace = runpy.run_path(str(base / "tools/run_baseline.py"))
    splits = namespace["baseline_definition"]()
    assert len(splits) == 30
    assert {key for key, value in splits.items() if value == "held_out"} == {
        "Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "R05", "R06"
    }
    definition = json.loads((base / "baseline.json").read_text())
    previous = json.loads((package / "experiments/configs/sol_max.json").read_text())
    assert definition["variants"] == previous["variants"]
    assert definition["repetitions"] == 3
    dataset = json.loads((base / "dataset.json").read_text())
    assert all(item["input"].startswith("frozen/corpus/inputs/") for item in dataset["cases"])


def test_probe_limit_is_per_invocation_and_resumes_without_resending(setup, monkeypatch):
    config, args = setup
    requests = []
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: requests.append(1) or Response())
    first = run_resumable_experiment(config, **args, workers=4, max_new_trials=1)
    assert len(requests) == 1
    assert first.report["scheduler"]["submitted_this_invocation"] == 1
    assert first.report["scheduler"]["stop_reasons"][0]["reason"] == "max_new_trials_reached"
    assert [t["status"] for t in first.report["trials"]] == ["complete"] + ["not_run"] * 5
    final = run_resumable_experiment(config, **args, workers=2)
    assert final.status == "complete" and len(requests) == 6


def test_stop_file_drains_http_retries_and_stops_new_trials(setup, monkeypatch):
    config, args = setup
    stop_path = config.parent / "operator-stop"
    requests = []

    def respond(request, timeout):
        requests.append(request)
        if len(requests) == 1:
            stop_path.touch()
            raise urllib.error.HTTPError(request.full_url, 500, "retry", {"Retry-After": "0"}, io.BytesIO(b"retry"))
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_resumable_experiment(config, **args, workers=1, stop_file=stop_path)
    assert len(requests) == 2
    assert [t["status"] for t in result.report["trials"]] == ["complete"] + ["not_run"] * 5
    assert result.report["scheduler"]["stop_reasons"][0]["reason"] == "stop_file_present"
    assert result.report["trials"][0]["http_retries"] == 1


def test_existing_default_stop_file_prevents_all_requests(setup):
    config, args = setup
    args["run_directory"].mkdir()
    (args["run_directory"] / "STOP").touch()
    result = run_resumable_experiment(config, **args)
    assert all(t["status"] == "not_run" for t in result.report["trials"])
    assert result.report["scheduler"]["submitted_this_invocation"] == 0


def test_consecutive_infrastructure_errors_stop_and_degraded_resets_counter(setup, monkeypatch):
    config, args = setup
    responses = iter(["error", "not JSON", "not JSON", "error", "error"])
    requests = []

    def respond(request, timeout):
        requests.append(request)
        content = next(responses)
        if content == "error":
            raise urllib.error.HTTPError(request.full_url, 403, "denied", {}, io.BytesIO(b"denied"))
        return Response(content)

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_resumable_experiment(config, **args, workers=1, max_consecutive_errors=2)
    assert [t["status"] for t in result.report["trials"]] == ["error", "degraded", "error", "error", "not_run", "not_run"]
    assert len(requests) == 5
    assert result.report["scheduler"]["consecutive_errors"] == 2
    assert result.report["scheduler"]["stop_reasons"][0]["reason"] == "consecutive_infrastructure_errors"


def test_resolved_validation_runs_before_any_output_or_network(setup):
    config, args = setup

    def reject(resolved):
        raise ValueError("wrong resolved dataset")

    with pytest.raises(ValueError, match="wrong resolved dataset"):
        run_resumable_experiment(config, **args, validate_resolved=reject)
    assert not args["run_directory"].exists()
