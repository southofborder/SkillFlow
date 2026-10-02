"""Independent offline checks of the actual baseline budget and retry bounds."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
import io
import json
from pathlib import Path
import threading
import urllib.error
import runpy

import pytest

from skill_ir.experiments.resumable import run_resumable_experiment
from skill_ir.experiments.config import resolve_experiment


BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
ENV = {
    "LLM_API_KEY": "offline-audit-credential-7321",
    "LLM_ENDPOINT": "https://offline.invalid/v1",
    "LLM_MODEL": "offline-test-model",
    "LLM_REASONING_EFFORT": "max",
    "LLM_MAX_RETRIES": "1",
    "LLM_RETRY_BASE_MS": "1",
    "LLM_RETRY_MAX_BACKOFF_MS": "1",
}
CANDIDATE = {
    "entry_block_ref": "finish",
    "blocks": [{
        "block_ref": "finish", "block_name": "Return declared constant",
        "instructions": [{
            "instruction_ref": "finish", "opcode": "return",
            "inputs": [{"type": "literal", "literal_value": "offline test"}],
        }],
    }],
    "edges": [],
}


class Response:
    status = 200
    headers = {"x-request-id": "offline-audit"}

    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({
            "model": "offline-test-model",
            "choices": [{"message": {"content": self.content}}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3},
        }).encode("utf-8")


def _write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def test_baseline_resolves_exactly_the_input_inventory_checked_by_the_entrypoint():
    """Prevent a config dataset redirect escaping the separate inventory check."""
    definition = json.loads((BASE / "baseline.json").read_text(encoding="utf-8"))
    assert definition["dataset"] == "dataset.json"
    resolved = resolve_experiment(BASE / "baseline.json", environ=ENV)
    corpus = json.loads((BASE / "frozen/corpus/corpus.json").read_text(encoding="utf-8"))
    assert [(case.id, case.source) for case in resolved.cases] == [
        (sample["id"], (BASE / "frozen/corpus" / sample["package_path"]).resolve())
        for sample in corpus["samples"]
    ]


@pytest.mark.parametrize("mutation", ["none", "dataset", "source", "hash", "package"])
def test_entrypoint_checks_actual_resolved_inputs(monkeypatch, mutation):
    monkeypatch.syspath_prepend(str(BASE / "tools"))
    namespace = runpy.run_path(str(BASE / "tools/run_baseline.py"))
    resolved = resolve_experiment(BASE / "baseline.json", environ=ENV)
    if mutation == "dataset":
        resolved = replace(resolved, definition=resolved.definition.model_copy(update={"dataset": "redirect.json"}))
    elif mutation in {"source", "hash", "package"}:
        case = resolved.cases[0]
        updates = {
            "source": {"source": BASE / "frozen/corpus/annotations"},
            "hash": {"sha256": "0" * 64},
            "package": {"package": case.package.model_copy(update={"root_name": "different"})},
        }
        resolved = replace(resolved, cases=(replace(case, **updates[mutation]), *resolved.cases[1:]))
    if mutation == "none":
        namespace["validate_baseline_resolved"](resolved)
    else:
        with pytest.raises(ValueError):
            namespace["validate_baseline_resolved"](resolved)


def test_restart_provenance_is_read_only_and_forbids_successful_output(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(BASE / "tools"))
    namespace = runpy.run_path(str(BASE / "tools/run_baseline.py"))
    old = tmp_path / "old"
    trial = old / "trials/N01/sol-max/1"
    trial.mkdir(parents=True)
    _write(old / "experiment.json", {"identity": "original"})
    _write(old / "report.json", {"trials": [{"status": "uncertain", "artifacts": "trials/N01/sol-max/1"}]})
    _write(trial / "trace.json", {"calls": [{"status": "error"}]})
    before = {path: path.read_bytes() for path in old.rglob("*") if path.is_file()}
    result = namespace["restart_provenance"](old, tmp_path / "new")
    assert result["successful_generations"] == result["inherited_trials"] == 0
    assert all(path.read_bytes() == content for path, content in before.items())
    with pytest.raises(ValueError, match="separate"):
        namespace["restart_provenance"](old, old)
    _write(trial / "trace.json", {"calls": [{"status": "complete"}]})
    with pytest.raises(ValueError, match="zero successful"):
        namespace["restart_provenance"](old, tmp_path / "new")


def test_actual_30_sample_baseline_spends_66_then_24_and_never_resends(tmp_path, monkeypatch):
    """Exercise the actual frozen 30-case inventory with a fully stubbed transport."""
    corpus = json.loads((BASE / "frozen/corpus/corpus.json").read_text(encoding="utf-8"))
    splits = {sample["id"]: sample["split"] for sample in corpus["samples"]}
    requests = []
    guard = threading.Lock()

    def respond(request, timeout):
        payload = json.loads(request.data)
        prompt = payload["messages"][0]["content"]
        assert '"coverage_targets"' not in prompt
        assert '"acceptable_variants"' not in prompt
        assert '"annotation_sha256"' not in prompt
        assert "待共同复核" not in prompt
        with guard:
            requests.append(payload)
        return Response(json.dumps(CANDIDATE))

    monkeypatch.setattr("urllib.request.urlopen", respond)
    arguments = dict(run_directory=tmp_path / "run", case_splits=splits, workers=4, environ=ENV)
    first = run_resumable_experiment(BASE / "baseline.json", **arguments, split="development")
    assert Counter(trial["status"] for trial in first.report["trials"]) == {"complete": 66, "not_run": 24}
    assert len(requests) == 66
    second = run_resumable_experiment(BASE / "baseline.json", **arguments, split="held_out")
    assert second.status == "complete" and len(requests) == 90
    assert len({(trial["case"], trial["variant"], trial["repetition"]) for trial in second.report["trials"]}) == 90
    third = run_resumable_experiment(BASE / "baseline.json", **arguments)
    assert third.status == "complete" and len(requests) == 90
    assert third.report["summary"]["generation_attempts"] == 90
    assert third.report["summary"]["repair_attempts"] == 0
    assert third.report["summary"]["http_attempts"] == 90
    assert third.report["summary"]["http_retries"] == 0


def test_maximum_repairs_and_http_retries_are_separate_bounded_counts(tmp_path, monkeypatch):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("Return an answer.", encoding="utf-8")
    _write(tmp_path / "dataset.json", {"cases": [{"id": "case", "input": "skill"}]})
    config = tmp_path / "config.json"
    _write(config, {
        "name": "retry-audit", "dataset": "dataset.json", "repetitions": 3,
        "variants": [{"id": "variant", "max_repair_rounds": 3}],
    })
    requests = []

    def respond(request, timeout):
        requests.append(request)
        if len(requests) % 2:
            raise urllib.error.HTTPError(request.full_url, 500, "retry", {"Retry-After": "0"}, io.BytesIO(b"retry"))
        return Response("not valid candidate JSON")

    monkeypatch.setattr("urllib.request.urlopen", respond)
    args = dict(run_directory=tmp_path / "run", case_splits={"case": "development"}, workers=1, environ=ENV)
    result = run_resumable_experiment(config, **args)
    assert result.status == "failed"
    assert [trial["status"] for trial in result.report["trials"]] == ["degraded"] * 3
    summary = result.report["summary"]
    assert (summary["planned"], summary["attempted"]) == (3, 3)
    assert (summary["generation_attempts"], summary["repair_attempts"]) == (12, 9)
    assert (summary["http_attempts"], summary["http_retries"]) == (24, 12)
    assert len(requests) == 24
    again = run_resumable_experiment(config, **args)
    assert again.status == "failed" and len(requests) == 24
