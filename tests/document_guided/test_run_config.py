"""Saved per-run effort reaches every stage and CLI flag without real model calls."""
from copy import deepcopy
import json

import pytest

from skillflow.common.structural_correction import ResponseChain
from skillflow.document_guided import runner
from skillflow.document_guided.online import CONFIG, analysis_config, read, run_step
from tests.document_guided.test_client import fake_processes, message, pending
from tests.document_guided.test_parallel_runner import Harness, freeze_producer
from tools.doe import document_guided_client as transport


@pytest.fixture
def observed_configs(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    seen = []

    class ObservedChain(ResponseChain):
        def __init__(self, directory, **kwargs):
            seen.append((directory, deepcopy(kwargs["config"])))
            super().__init__(directory, **kwargs)

    for module in ("skillflow.document_guided.online", "skillflow.task.runner",
                   "skillflow.document_guided.source_review"):
        monkeypatch.setattr(module + ".ResponseChain", ObservedChain)
    return seen


def prepared(harness, package, effort):
    package.mkdir()
    source = harness.example["source"] + "\nOriginal quotation: 保留原文。\r\n"
    (package / "SKILL.md").write_bytes(source.encode("utf-8"))
    config = {"reasoning_effort": effort} if effort is not None else None
    manifest = runner.prepare(package, run_dir=harness.directory, config=config)
    if config is not None:
        config["reasoning_effort"] = "max"  # A caller cannot mutate frozen preparation.
    return manifest


@pytest.mark.parametrize("effort", [None, "high"])
def test_default_max_and_high_seven_steps_full_backend_and_offline_replay(tmp_path, effort, observed_configs):
    harness = Harness(tmp_path / "run")
    expected = analysis_config({"reasoning_effort": effort} if effort is not None else None)
    assert prepared(harness, tmp_path / "package", effort)["config"] == expected
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert len(harness.calls) == result["counts"]["logical_calls"] == 7
    assert read(harness.directory / "annotation/manifest.json")["config"] == expected
    assert observed_configs and all(config == expected for _, config in observed_configs)
    assert runner.replay(harness.directory) == result
    assert runner.run(harness.directory, client_factory=lambda *args: pytest.fail("No repeat call")) == result
    assert len(harness.calls) == 7
    assert all(config == expected for _, config in observed_configs)


def test_high_shared_mixed_repair_and_each_structural_correction_keep_config(tmp_path, observed_configs):
    harness = Harness(tmp_path / "run", domains=("task", "cfg", "annotation"))
    expected = analysis_config({"reasoning_effort": "high"})
    prepared(harness, tmp_path / "package", "high")
    attempts = {}

    def factory(stage, owner):
        class InvalidOnce:
            def complete(self, prompt):
                attempts[stage] = attempts.get(stage, 0) + 1
                if attempts[stage] == 1:
                    return {"unexpected": True}  # Empty sensitivity is valid; this object is invalid in every stage.
                return harness.complete(stage, prompt)
        return InvalidOnce()

    def before_backend(state):
        if state["stage"] == "propagation":
            raise KeyboardInterrupt("Stop this configuration-routing fixture before backend work")

    result = runner.run(harness.directory, client_factory=factory, progress=before_backend)
    assert result["status"] == "interrupted", result
    assert result["repair_used"] and result["selected_annotation"] == "revision/annotation"
    assert len(harness.calls) == 13 and set(attempts.values()) == {2}
    assert result["counts"]["logical_calls"] == 26
    assert result["counts"]["structural_corrections"] == 13
    for path in harness.directory.rglob("manifest.json"):
        manifest = read(path)
        if "config" in manifest:
            assert manifest["config"] == expected, path
    assert observed_configs and all(config == expected for _, config in observed_configs)
    assert runner.replay(harness.directory) == result
    assert all(config == expected for _, config in observed_configs)
    with pytest.raises(ValueError, match="configuration differs"):
        run_step(harness.directory / "steps/flow", config=CONFIG,
                 client=object())


@pytest.mark.parametrize("config", [{"reasoning_effort": "ultra"}, {"model": "other"},
                                   {"response_format": "text"}, {"provider": "openai"}])
def test_invalid_config_is_rejected_before_preparation(tmp_path, config):
    source = tmp_path / "SKILL.md"
    source.write_text("A source declaration.", encoding="utf-8")
    with pytest.raises(ValueError, match="configuration"):
        runner.prepare(source, run_dir=tmp_path / "run", config=config)
    assert not (tmp_path / "run").exists()


@pytest.mark.parametrize("effort", ["max", "high"])
def test_native_cli_flags_and_saved_transport_identity_match_run_effort(tmp_path, effort):
    owner = tmp_path / "owner"
    prompt = "Analyze the supplied declaration. 原文\r\n"
    pending(owner, prompt)
    config = analysis_config({"reasoning_effort": effort})
    (owner / "manifest.json").write_text(json.dumps({"config": config}), encoding="utf-8")
    executable = tmp_path / "codex.exe"
    executable.write_bytes(b"offline fixture; never executable")
    launches = []
    client = transport.Client(tmp_path / "transport", owner=owner, executable=executable,
        config=config, popen=fake_processes([{"rows": [message("answer")]}], launches))
    assert client.complete(prompt) == "answer"
    assert client.complete(prompt) == "answer"
    assert len(launches) == 1
    argv = launches[0]["argv"]
    assert argv[argv.index("--model") + 1] == "gpt-6.1-sol"
    assert f'model_reasoning_effort="{effort}"' in argv
    assert 'model_provider="openai"' in argv
    identity = read(next((tmp_path / "transport").rglob("request.json")))
    assert identity["runtime"] == {"model": "gpt-6.1-sol", "effort": effort, "provider": "openai"}
    wrong = transport.Client(tmp_path / "transport", owner=owner, config={"reasoning_effort":
        "high" if effort == "max" else "max"}, popen=lambda *a, **k: pytest.fail("No mismatched launch"))
    with pytest.raises(ValueError, match="configuration differs"):
        wrong.complete(prompt)


def test_pilot_freezes_high_at_prepare_and_reads_it_at_run(tmp_path, monkeypatch):
    from tools.doe import document_guided_pilot as pilot
    config = analysis_config({"reasoning_effort": "high"})
    seen = []

    def prepare(source, *, run_dir, config):
        assert config == {"reasoning_effort": "high"}
        (run_dir / "manifest.json").write_text(json.dumps({"config": analysis_config(config)}), encoding="utf-8")
        return {"status": "prepared"}

    class Client:
        def __init__(self, directory, **kwargs):
            seen.append(kwargs["config"])

    def run(directory, *, client_factory, progress):
        client_factory("task", directory / "task")
        client_factory("review", directory / "review")
        return {"status": "complete"}

    monkeypatch.setattr(pilot, "prepare", prepare)
    monkeypatch.setattr(pilot, "run", run)
    monkeypatch.setattr(pilot, "transport_metrics", lambda directory: {})
    monkeypatch.setattr(transport, "Client", Client)
    assert pilot.main(["prepare", "--input", "source", "--run-dir", str(tmp_path), "--effort", "high"]) == 0
    assert pilot.main(["run", "--run-dir", str(tmp_path)]) == 0
    assert seen == [config, config]
    with pytest.raises(SystemExit):
        pilot.main(["run", "--run-dir", str(tmp_path), "--effort", "max"])
