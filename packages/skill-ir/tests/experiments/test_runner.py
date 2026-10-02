import csv
import io
import json
from pathlib import Path
import urllib.error
import zipfile

import pytest

from skill_ir import run_experiment
from skill_ir.cli import main
from skill_ir.experiments.config import resolve_experiment
from skill_ir.llm import LlmConfigError


def test_optional_json_output_is_only_in_explicit_experiment_snapshot():
    from dataclasses import replace
    from skill_ir.experiments.config import ResolvedVariant
    from skill_ir.llm import LlmConfig

    base = ResolvedVariant("baseline", LlmConfig(api_key="fixture"), "LLM_API_KEY", 3)
    assert "response_format" not in base.snapshot()
    explicit = replace(base, config=replace(base.config, response_format="json_object"))
    assert explicit.snapshot() == {**base.snapshot(), "response_format": "json_object"}
    assert "api_key" not in explicit.snapshot()


CANDIDATE = {
    "entry_block_ref": "answer",
    "blocks": [
        {
            "block_ref": "answer",
            "block_name": "Return answer",
            "instructions": [
                {
                    "instruction_ref": "answer",
                    "opcode": "return",
                    "inputs": [{"type": "literal", "literal_value": "ok"}],
                }
            ],
        }
    ],
    "edges": [],
}


class Response:
    status = 200

    def __init__(self, content=None, *, usage=None):
        self.headers = {"x-request-id": "request-123"}
        self.payload = {
            "model": "returned-model",
            "choices": [
                {
                    "message": {
                        "content": json.dumps(CANDIDATE) if content is None else content
                    }
                }
            ],
        }
        if usage is not None:
            self.payload["usage"] = usage

    def read(self):
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def definitions(tmp_path, *, repetitions=2, variants=2):
    data = tmp_path / "data"
    skill = data / "folder"
    skill.mkdir(parents=True)
    # No SKILL.md is needed; both existing loader formats remain accepted.
    (skill / "notes.txt").write_text("original source", encoding="utf-8")
    with zipfile.ZipFile(data / "archive.zip", "w") as archive:
        archive.writestr("wrapped/notes.txt", "zip source")
    dataset = data / "dataset.json"
    write_json(
        dataset,
        {
            "cases": [
                {"id": "folder", "input": "folder"},
                {"id": "zip", "input": "archive.zip"},
            ]
        },
    )
    config = tmp_path / "configs/experiment.json"
    write_json(
        config,
        {
            "name": "comparison",
            "dataset": "../data/dataset.json",
            "repetitions": repetitions,
            "variants": [
                {
                    "id": f"variant{i}",
                    "model": f"model-{i}",
                    "reasoning_effort": "high" if i else "max",
                    "endpoint": f"https://provider{i}.example/v1/chat/completions",
                    "api_key_env": f"KEY_{i}",
                    "max_repair_rounds": 1,
                }
                for i in range(variants)
            ],
        },
    )
    environment = {f"KEY_{i}": f"secret-{i}" for i in range(variants)}
    environment.update(
        LLM_MODEL="env-model", LLM_MAX_RETRIES="1", LLM_RETRY_BASE_MS="1"
    )
    return config, dataset, environment


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("Experiment unit tests must never use the network")

    monkeypatch.setattr("urllib.request.urlopen", unexpected)


def test_matrix_outputs_requests_and_no_overwrite(tmp_path, monkeypatch):
    config, dataset, environment = definitions(tmp_path)
    requests = []

    def respond(request, timeout):
        requests.append(request)
        return Response(
            usage={"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}
        )

    monkeypatch.setattr("urllib.request.urlopen", respond)
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    result = run_experiment(config, environ=environment)
    assert result.status == "complete"
    assert result.run_directory.is_relative_to(outside / "results/skill-ir")
    trials = result.report["trials"]
    assert [(t["case"], t["variant"], t["repetition"]) for t in trials] == [
        (case, variant, repeat)
        for case in ("folder", "zip")
        for variant in ("variant0", "variant1")
        for repeat in (1, 2)
    ]
    assert len(requests) == 8
    for request, trial in zip(requests, trials):
        i = int(trial["variant"][-1])
        assert request.full_url == f"https://provider{i}.example/v1/chat/completions"
        assert request.get_header("Authorization") == f"Bearer secret-{i}"
        body = json.loads(request.data)
        assert body["model"] == f"model-{i}"
        assert body["reasoning_effort"] == ("high" if i else "max")
        directory = result.run_directory / trial["artifacts"]
        assert {p.name for p in directory.iterdir()} == {
            "analysis.json",
            "candidate.json",
            "graph.mmd",
            "trace.json",
        }
        trace = json.loads((directory / "trace.json").read_text())
        assert trace["calls"][0]["returned_model"] == "returned-model"
        assert trace["calls"][0]["request_id"] == "request-123"
    assert result.report["summary"]["known_token_usage"]["total_tokens"] == 104
    assert result.report["summary"]["structural_pass_rate"] == 1
    assert result.report["summary"]["first_pass_rate"] == 1
    assert (
        len(
            list(
                csv.DictReader(
                    (result.run_directory / "summary.csv").open(encoding="utf-8")
                )
            )
        )
        == 8
    )
    before = {p: p.read_bytes() for p in result.run_directory.rglob("*") if p.is_file()}
    again = run_experiment(config, environ=environment)
    assert again.run_directory != result.run_directory
    assert all(p.read_bytes() == content for p, content in before.items())


def test_retry_repair_and_missing_usage_are_distinct(tmp_path, monkeypatch):
    config, _, env = definitions(tmp_path, repetitions=1, variants=1)
    responses = [
        urllib.error.HTTPError(
            "https://provider0.example",
            500,
            "retry",
            {"Retry-After": "0"},
            io.BytesIO(b"retry"),
        ),
        Response("not JSON"),
        Response(),
        Response(),
    ]

    def respond(*args, **kwargs):
        item = responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    trial = result.report["trials"][0]
    assert trial["generation_attempts"] == 2
    assert trial["repair_attempts"] == 1
    assert trial["http_attempts"] == 3
    assert trial["http_retries"] == 1
    assert trial["known_token_usage"] == {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }
    trace = json.loads(
        (result.run_directory / trial["artifacts"] / "trace.json").read_text()
    )
    assert trace["calls"][0]["response"] == "not JSON"
    assert "Repair the previous candidate" in trace["calls"][1]["prompt"]
    assert trace["calls"][0]["http_attempts"][0]["http_status"] == 500
    assert result.report["summary"]["first_pass_rate"] == 0.5


def test_failure_preserves_prior_calls_continues_and_redacts_secrets(
    tmp_path, monkeypatch, capsys
):
    config, _, env = definitions(tmp_path, repetitions=1, variants=1)
    responses = [
        Response("not JSON secret-0"),
        urllib.error.HTTPError(
            "https://provider0.example", 403, "denied", {}, io.BytesIO(b"secret-0")
        ),
        Response(),
    ]

    def respond(*args, **kwargs):
        item = responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert [t["status"] for t in result.report["trials"]] == ["error", "complete"]
    trace_path = (
        result.run_directory / result.report["trials"][0]["artifacts"] / "trace.json"
    )
    calls = json.loads(trace_path.read_text())["calls"]
    assert len(calls) == 2
    assert calls[0]["status"] == "complete" and calls[1]["status"] == "error"
    for path in result.run_directory.rglob("*"):
        if path.is_file():
            assert "secret-0" not in path.read_text(encoding="utf-8")
    assert "secret-0" not in str(result)
    assert "secret-0" not in str(capsys.readouterr())


def test_interrupt_marks_active_trial_and_preserves_pending(tmp_path, monkeypatch):
    config, _, env = definitions(tmp_path)

    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr("urllib.request.urlopen", interrupt)
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert result.status == "interrupted"
    assert [trial["status"] for trial in result.report["trials"]] == ["interrupted"] + [
        "not_run"
    ] * 7
    trace = json.loads(
        (
            result.run_directory
            / result.report["trials"][0]["artifacts"]
            / "trace.json"
        ).read_text()
    )
    assert trace["calls"][0]["status"] == "interrupted"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_key",
        "missing_input",
        "duplicate_id",
        "case_collision",
        "traversal_id",
        "zero_repetitions",
        "negative_timeout",
        "blank_model",
        "blank_effort",
        "invalid_port",
        "unknown_field",
    ],
)
def test_preflight_rejects_entire_experiment_before_network(tmp_path, mutation):
    config, dataset, env = definitions(tmp_path)
    definition = json.loads(config.read_text())
    data = json.loads(dataset.read_text())
    if mutation == "missing_key":
        env.pop("KEY_1")
    elif mutation == "missing_input":
        data["cases"][1]["input"] = "missing"
    elif mutation == "duplicate_id":
        data["cases"].append(data["cases"][0])
    elif mutation == "case_collision":
        data["cases"][1]["id"] = "FOLDER"
    elif mutation == "traversal_id":
        definition["variants"][0]["id"] = "../escape"
    elif mutation == "zero_repetitions":
        definition["repetitions"] = 0
    elif mutation == "negative_timeout":
        definition["variants"][0]["timeout_ms"] = -1
    elif mutation == "blank_model":
        definition["variants"][0]["model"] = "   "
    elif mutation == "blank_effort":
        definition["variants"][0]["reasoning_effort"] = "   "
    elif mutation == "invalid_port":
        definition["variants"][0]["endpoint"] = "https://provider.example:invalid/v1"
    else:
        definition["variants"][0]["api_key"] = "literal-secret"
    write_json(config, definition)
    write_json(dataset, data)
    with pytest.raises((ValueError, OSError, LlmConfigError)):
        run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert not (tmp_path / "out").exists()


def test_endpoint_query_is_preserved_and_absent_request_id_is_null(
    tmp_path, monkeypatch
):
    config, _, env = definitions(tmp_path, repetitions=1, variants=1)
    definition = json.loads(config.read_text())
    endpoint = "https://provider.example/v1/chat/completions?api-version=example"
    definition["variants"][0]["endpoint"] = endpoint
    write_json(config, definition)
    requests = []

    def respond(request, timeout):
        requests.append(request.full_url)
        response = Response()
        response.headers = None
        return response

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert result.status == "complete"
    assert requests == [endpoint, endpoint]
    for trial in result.report["trials"]:
        trace = json.loads(
            (result.run_directory / trial["artifacts"] / "trace.json").read_text()
        )
        assert trace["calls"][0]["request_id"] is None


def test_fourth_case_requires_only_dataset_edit(tmp_path, monkeypatch):
    config, dataset, env = definitions(tmp_path, repetitions=1, variants=1)
    data = json.loads(dataset.read_text())
    data["cases"] += [
        {"id": "third", "input": "folder"},
        {"id": "fourth", "input": "archive.zip"},
    ]
    write_json(dataset, data)
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: Response())
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert result.report["summary"]["complete"] == 4


def test_inputs_and_settings_are_frozen_before_first_request(tmp_path, monkeypatch):
    config, dataset, env = definitions(tmp_path)
    requests = []

    def respond(request, timeout):
        requests.append(json.loads(request.data))
        (dataset.parent / "folder/notes.txt").write_text("changed after preflight")
        env["LLM_MODEL"] = "changed-model"
        env["KEY_0"] = "changed-secret"
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", respond)
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert result.status == "complete"
    assert all(
        "changed after preflight" not in item["messages"][0]["content"]
        for item in requests
    )
    assert all(item["model"] != "changed-model" for item in requests)


def test_cli_explicit_env_file_from_unrelated_directory(tmp_path, monkeypatch):
    config, _, env = definitions(tmp_path, repetitions=1, variants=1)
    env_path = tmp_path / "settings.env"
    env_path.write_text("\n".join(f"{key}={value}" for key, value in env.items()))
    other = tmp_path / "other"
    other.mkdir()
    (other / ".env").write_text("LLM_REASONING_EFFORT=invalid")
    monkeypatch.chdir(other)
    for key in (*env, "LLM_REASONING_EFFORT"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: Response())
    assert (
        main(["experiment", "--config", str(config), "--env-file", str(env_path)]) == 0
    )


def test_invalid_config_never_echoes_literal_secret(tmp_path, capsys):
    config, _, _ = definitions(tmp_path)
    definition = json.loads(config.read_text())
    definition["variants"][0]["api_key"] = "mistaken-literal-secret"
    write_json(config, definition)
    assert main(["experiment", "--config", str(config)]) == 2
    output = capsys.readouterr().err
    assert "api_key" in output
    assert "mistaken-literal-secret" not in output


def test_explicit_variant_overrides_invalid_environment_default(tmp_path):
    config, _, env = definitions(tmp_path)
    env["LLM_REASONING_EFFORT"] = "invalid-but-unused"
    resolved = resolve_experiment(config, environ=env)
    assert [variant.config.reasoning_effort for variant in resolved.variants] == [
        "max",
        "high",
    ]


def test_degraded_trial_is_not_reported_as_passed(tmp_path, monkeypatch):
    config, _, env = definitions(tmp_path, repetitions=1, variants=1)
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **kw: Response("not JSON"))
    result = run_experiment(config, output_dir=tmp_path / "out", environ=env)
    assert result.status == "failed"
    assert [trial["status"] for trial in result.report["trials"]] == [
        "degraded",
        "degraded",
    ]
    assert result.report["summary"]["structural_pass_rate"] == 0
    for trial in result.report["trials"]:
        directory = result.run_directory / trial["artifacts"]
        assert (directory / "analysis.json").exists()
        assert not (directory / "graph.mmd").exists()
        assert len(json.loads((directory / "trace.json").read_text())["calls"]) == 2
