"""A failed required CFG spends one existing shared round, with real backend replay."""
from copy import deepcopy
import json

import pytest

from skillflow.common.recording import canonical_sha256, read_json
from skillflow.document_guided import runner
from tests.document_guided.test_parallel_runner import Harness, _cfg_wire, freeze_producer, graph_facts_fixture, prompt_scope


class RecoveryHarness(Harness):
    def __init__(self, directory, *, finding=True, revision_bad=False, task_finding=False):
        super().__init__(directory)
        from tests.document_guided.test_input_contract_completeness import call_sample
        from skillflow.graph.extraction.compiler import compile_candidate
        from skillflow.document_guided.fragments import split_fragments
        material, wire = call_sample()
        block = material["cfg"]["blocks"]["sample"]
        candidate = {"entry_block_ref": "sample", "blocks": [{
            "block_ref": "sample", "block_name": block["block_name"],
            "data_source_kind": block["data_source_kind"], "constraints": block["constraints"],
            "instructions": [{"instruction_ref": ir["id"], **{key: value for key, value in ir.items() if key != "id"}}
                             for ir in block["instructions"]]}], "edges": []}
        compiled = compile_candidate(candidate)
        assert compiled.ok
        wire["ir_semantics"] = {new.id: wire["ir_semantics"][old["id"]]
            for old, new in zip(block["instructions"], compiled.cfg.blocks["block_001"].instructions)}
        self.example["source"] = material["source"]["files"][0]["content"]
        self.example["task_candidate"] = {key: deepcopy(material["task"][key]) for key in ("purpose", "requirements", "issues")}
        self.graph, self.wire, self.fragments = _cfg_wire(candidate), wire, split_fragments(wire)
        self.finding, self.revision_bad, self.task_finding = finding, revision_bad, task_finding

    def complete(self, stage, prompt):
        if stage in {"graph", "revision-graph", "review"}:
            with self.lock:
                self.attempts[stage] = self.attempts.get(stage, 0) + 1
                self.calls.append(stage)
                self.prompts[stage] = prompt
            assert self.attempts[stage] <= 2
            if stage in {"graph", "revision-graph"}:
                answer = graph_facts_fixture(self.graph)
                if stage == "graph" and self.attempts[stage] == 1:
                    answer["entry"] = "missing-entry"
                    return answer
                plan = prompt_scope(prompt)
                slot, = plan["slots"].values()
                assert slot["path"] == ["entry"] and slot["old_value"] == "missing-entry"
                if stage == "revision-graph":
                    assert plan["base"]["cfg_sha256"] is None
                    assert plan["base"]["origin"] == "model_facts"
                    assert "missing-entry" in prompt and "SEALED_TASK" not in prompt
                    assert self.attempts[stage] == 1
                return {"plan_sha256": plan["plan_sha256"], "updates": [
                    {"slot_id": slot["slot_id"],
                     "value": "missing-entry" if stage == "graph" or self.revision_bad else answer["entry"]}]}
            from tests.doe.input_review_helpers import review_prompt_payload
            material = review_prompt_payload(prompt)
            assert material["cfg"] is None and material["annotation"] is None
            assert not material["input_contract_inventory"]["available"]
            assert any(row["id"] == "stage:graph" for row in material["failed_stage_targets"]["targets"])
            findings = []
            if self.finding:
                findings.append({"domain": "cfg", "target_ids": ["stage:graph"],
                    "explanation": "The source requires calling Service and returning its response; the rejected graph has no entry to represent that required flow.",
                    "suggestion": "Rebuild the required source-supported flow with an actual entry and complete dependencies.",
                    "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]})
            if self.task_finding:
                findings.append({"domain": "task", "target_ids": ["task:"],
                    "explanation": "State the unchanged-response obligation atomically from the original source.",
                    "suggestion": "Preserve the required original response.",
                    "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
                    "task_objection": {"code": "atomicity", "requirement_ids": ["R1"],
                        "source_spans": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}})
            return {"outcome": "completed", "findings": findings, "input_contract_checks": [],
                    "input_projection_checks": [], "source_input_findings": []}
        return super().complete(stage, prompt)


@pytest.fixture(autouse=True)
def producer(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


@pytest.mark.parametrize("finding,task_finding", [(True, False), (False, False), (True, True)])
def test_missing_cfg_recovery_reaches_contracts_backend_and_same_replay(tmp_path, finding, task_finding):
    harness = RecoveryHarness(tmp_path / "run", finding=finding, task_finding=task_finding)
    source = harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == ("partial" if finding else "complete"), result
    assert result["repair_used"] and result["selected_annotation"] == "revision/annotation"
    assert result["counts"]["logical_calls"] == len(harness.calls) == 10 + task_finding
    assert result["counts"]["structural_corrections"] == 1
    assert harness.calls.count("graph") == 2 and harness.calls.count("revision-graph") == 1
    assert not {"processing", "task-correspondence", "sensitivity"} & set(harness.calls)
    assert {"revision-processing", "revision-task-correspondence", "revision-sensitivity", "revision/review"} <= set(harness.calls)
    assert runner.POLICY["normal_semantic_calls"] == 7 and runner.POLICY["workers"] == 2
    assert runner.POLICY["structural_corrections"] == runner.POLICY["semantic_repairs"] == 1
    assert not (harness.directory / "graph/initial.json").exists()
    evidence = read_json(harness.directory / "audit/failed-stages/graph.json")
    assert evidence["material"]["accepted"] is False
    assert canonical_sha256(evidence["material"]) == evidence["material_sha256"]
    decision = read_json(harness.directory / "audit/shared-repair-decision.json")
    assert decision["eligible"] and decision["mode"] == "missing_cfg_slots"
    assert decision["domains"] == (["cfg", "task"] if task_finding else ["cfg"])
    assert read_json(harness.directory / "audit/input-contract-review.json")["source_review_complete"] is not finding
    if finding:
        # Fixing the known entry slot does not certify a broader failed-stage finding.
        assert any("Graph findings without a finite slot: F001" in item for item in result["limitations"])
    assert read_json(harness.directory / "doe/doe-result.json")["status"] == "complete"
    assert "SEALED_TASK" not in harness.prompts["revision-processing"]
    assert source == (harness.directory / "source/inputs/package/SKILL.md").read_bytes().decode("utf-8")
    before = {str(p): p.read_bytes() for p in harness.directory.rglob("*.json")}
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 10 + task_finding
    after = {str(p): p.read_bytes() for p in harness.directory.rglob("*.json")}
    assert before == {name: after[name] for name in before}
    from pathlib import Path
    added = {Path(name).relative_to(harness.directory).as_posix() for name in after.keys() - before.keys()}
    assert added == {"task/replay/result.json", "propagation/replay/summary.json", "doe/replay-summary.json"} | (
        {"revision/task/replay/result.json"} if task_finding else set())


def test_failed_shared_rebuild_stays_unselected_and_has_no_second_round(tmp_path):
    harness = RecoveryHarness(tmp_path / "run", revision_bad=True)
    harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "failed" and result["repair_used"], result
    assert result["selected_annotation"] is None
    assert harness.calls.count("graph") == 2 and harness.calls.count("revision-graph") == 1
    assert len(harness.calls) == 7
    assert not (harness.directory / "selection.json").exists()
    assert not (harness.directory / "propagation").exists() and not (harness.directory / "doe").exists()
    assert not any("revision-revision" in name for name in harness.calls)
    assert runner.replay(harness.directory) == result
    assert len(harness.calls) == 7


@pytest.mark.parametrize("artifact", ["audit/failed-stages/graph.json", "audit/shared-repair-decision.json"])
def test_saved_recovery_evidence_cannot_be_replaced_before_replay(tmp_path, artifact):
    harness = RecoveryHarness(tmp_path / "run", finding=False)
    harness.prepare(tmp_path / "source")
    result = runner.run(harness.directory, client_factory=harness.factory)
    assert result["status"] == "complete", result
    path = harness.directory / artifact
    original = read_json(path)
    path.write_text(json.dumps({**original, "unexpected": "changed"}), encoding="utf-8")
    with pytest.raises(ValueError, match="Saved candidate differs|file.*digest|differ"):
        runner.replay(harness.directory)
    assert len(harness.calls) == 10
