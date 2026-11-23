"""Injected answers exercise the program-owned CFG and bounded repair path."""
from copy import deepcopy
import json

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.online import read
from .test_parallel_runner import Harness, freeze_producer, graph_facts_fixture, prompt_scope


SPAN = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}


@pytest.fixture(autouse=True)
def offline_producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


class ScopedHarness(Harness):
    def __init__(self, directory, mode):
        super().__init__(directory, domains=("cfg",) if mode in {"revision", "revision-change", "defer", "wrong-plan"}
                         else ("annotation",) if mode == "processing" else ())
        self.mode = mode

    def graph_reply(self, stage, prompt):
        with self.lock:
            self.calls.append(stage)
            self.prompts[stage] = prompt
            self.attempts[stage] = self.attempts.get(stage, 0) + 1
        self.graph_started.set()
        facts = graph_facts_fixture(self.graph)
        if self.attempts[stage] == 1 and stage == "graph":
            if self.mode in {"missing", "shared-missing"}:
                del facts["blocks"][0]["exit"]["values"]
            if self.mode == "unreadable":
                return {"unusable": True}
            return facts
        plan = prompt_scope(prompt)
        assert len(plan["slots"]) == 1
        slot = next(iter(plan["slots"].values()))
        value = (facts["blocks"][0]["exit"]["values"] if self.mode in {"missing", "shared-missing"}
                 else slot["old_value"])
        if self.mode == "shared-missing" and stage == "graph":
            return {"plan_sha256": plan["plan_sha256"], "updates": []}
        if self.mode == "revision-change":
            value = [*value, "Preserve the original field."]
        return {"plan_sha256": "0" * 64 if self.mode == "wrong-plan" else plan["plan_sha256"],
                "updates": [{"slot_id": slot["slot_id"], "value": value}]}

    def complete(self, stage, prompt):
        if stage in {"graph", "revision-graph"}:
            return self.graph_reply(stage, prompt)
        if stage == "revision-processing" and self.mode != "shared-missing":
            self.calls.append(stage)
            self.prompts[stage] = prompt
            plan = prompt_scope(prompt)
            assert "ir_001" in plan["slots"]
            if self.mode == "processing":
                assert set(plan["slots"]) == {"ir_001"}
            return {"coverage_slots": [{"instruction_id": identity,
                        "modeled": deepcopy(self.fragments["processing"]["ir_semantics"][identity])}
                        for identity in plan["slots"]]}
        if stage == "revision-sensitivity" and self.mode == "revision-change":
            self.calls.append(stage)
            self.prompts[stage] = prompt
            plan = prompt_scope(prompt)
            return {"slots": [{"instruction_id": identity, "declarations": slot["prior_entry_labels"]}
                              for identity, slot in plan["slots"].items()]}
        answer = super().complete(stage, prompt)
        if stage == "review" and self.mode in {"revision", "wrong-plan"}:
            answer["findings"][0]["target_ids"] = ["cfg:/blocks/block_001/instructions/0/constraints"]
        if stage == "review" and self.mode == "revision-change":
            answer["findings"][0]["target_ids"] = ["cfg:/blocks/block_001/instructions/0/constraints"]
        if stage == "review" and self.mode == "processing":
            answer["findings"][0]["target_ids"] = ["annotation:/ir_semantics/ir_001"]
        return answer


@pytest.mark.parametrize("mode", ["missing", "revision", "defer", "wrong-plan", "processing", "unreadable"])
def test_one_bounded_slot_request_and_zero_call_replay(tmp_path, mode):
    harness = ScopedHarness(tmp_path / "run", mode)
    harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    actual = list(harness.calls)
    if mode == "unreadable":
        assert result["status"] == "failed", result
        assert actual.count("graph") == 1 and "revision-graph" not in actual
        assert not (harness.directory / "graph/initial.json").exists()
    elif mode == "missing":
        assert result["status"] == "complete", result
        assert actual.count("graph") == 2 and len(actual) == 8
        value = read(harness.directory / "steps/graph/value.json")
        assert value["cfg"] == read(harness.directory / "graph/initial.json")["cfg"]
        base = harness.directory / "steps/graph/calls/a001/prompt.txt"
        correction = harness.directory / "steps/graph/calls/a002/prompt.txt"
        assert correction.stat().st_size < base.stat().st_size
        assert "保留原文，不翻译引文。" in correction.read_text(encoding="utf-8")
    else:
        assert result["status"] == "partial", result
        assert result["selected_annotation"] == "annotation"
        assert "revision/review" not in actual
        assert len(actual) == 7 + (mode != "defer")
        assert ("revision-graph" in actual) == (mode in {"revision", "wrong-plan"})
        assert ("revision-processing" in actual) == (mode == "processing")
        assert all(name not in actual for name in ("revision-task-correspondence", "revision-sensitivity"))
    assert runner.replay(harness.directory) == result
    assert harness.calls == actual


@pytest.mark.parametrize("mode", ["shared-missing", "revision-change"])
def test_valid_scoped_graph_change_publishes_new_bundle(tmp_path, mode):
    harness = ScopedHarness(tmp_path / "run", mode)
    harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    assert result["selected_annotation"] == "revision/annotation"
    actual = list(harness.calls)
    assert actual.count("revision-graph") == 1
    assert (harness.directory / "graph/revision.json").exists()
    assert (harness.directory / "graph/initial.json").exists() == (mode == "revision-change")
    assert runner.replay(harness.directory) == result
    assert harness.calls == actual
