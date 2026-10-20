"""Recorded source-only isolation and the three/five/six semantic-call paths."""
from copy import deepcopy
import hashlib
import json
import sys

import pytest

from skillflow import pipeline
from skillflow.common.recording import injected_factory
from skillflow.common.source_evidence import _digest
from skillflow.propagation.contracts.task import CandidateTask
from tests.propagation.annotation.helpers import graph, authored_task, FakeClient
from tests.propagation.review.test_runner import ReviewClient, material_from_prompt, response_for


@pytest.fixture(autouse=True)
def stable_offline_producer(monkeypatch):
    """Freeze the engineering test producer; saved input tamper checks stay live."""
    from skillflow.common import recording
    from skillflow.doe import formal_runner
    from skillflow.propagation import runner
    from skillflow.task import runner as task_runner
    from skillflow.propagation.review import refinement
    original = recording.implementation_provenance
    snapshot = original()
    for name, module in list(sys.modules.items()):
        if name.startswith("skillflow") and getattr(module, "implementation_provenance", None) is original:
            monkeypatch.setattr(module, "implementation_provenance", lambda: deepcopy(snapshot))


class TaskClient:
    def __init__(self, revised=False):
        self.prompts = []
        self.revised = revised

    def complete(self, prompt):
        self.prompts.append(prompt)
        payload = json.JSONDecoder().raw_decode(prompt.split("COMPLETE_ORIGINAL_SOURCE\n\n", 1)[1])[0]
        rows = []
        request = None
        for row in payload["source_files"]:
            content = "".join(row["lines"])
            if row["file"] == "task/user-request.txt":
                request = content
            else:
                rows.append({"path": row["file"][6:], "content": content,
                             "sha256": hashlib.sha256(content.encode()).hexdigest()})
        source = {"files": rows, "source_sha256": _digest([
            {key: row[key] for key in ("path", "sha256")} for row in rows])}
        task = authored_task(source, user_request=request).model_dump(mode="json")
        candidate = {key: task[key] for key in CandidateTask.model_fields}
        if self.revised:
            candidate["requirements"][0]["text"] = "Preserve the requested original result and every source limitation."
        return candidate


class FirstIssue(ReviewClient):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain

    def complete(self, prompt):
        self.prompts.append(prompt)
        material = material_from_prompt(prompt)
        if len(self.prompts) > 1:
            return response_for(material)
        if self.domain == "annotation":
            return response_for(material, finding=True)
        result = response_for(material)
        target = next(row for row in material["target_index"]
                      if row["kind"] == "task" and row["pointer"] == "/requirements/0")
        span = {key: material["source_line_universe"][0][key] for key in ("file",)}
        span.update(start_line=1, end_line=1)
        result["findings"] = [{"domain": "task", "target_ids": [target["id"]],
            "explanation": "人工故障注入：要求解释需要重新核对。",
            "evidences": [{**span, "reason": "原始源文应独立复核。"}],
            "suggestion": "重新读取源文核实要求，不使用当前载荷。",
            "task_objection": {"code": "condition_scope", "source_spans": [span],
                               "requirement_ids": [material["task"]["requirements"][0]["id"]]}}]
        result["source_checks"][0].update(status="issue", finding_indexes=[0])
        result["requirement_checks"][0].update(status="issue", finding_indexes=[0])
        return result


def prepared(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("Return the selected original value.\n", encoding="utf-8")
    cfg = tmp_path / "analysis.json"
    cfg.write_text(json.dumps({"cfg": graph()}), encoding="utf-8")
    run = tmp_path / "run"
    manifest = pipeline.prepare_analysis_run(source, cfg, run_dir=run)
    assert manifest["preparation_status"] == "ready", manifest
    return run


@pytest.mark.parametrize("domain,expected_calls", [(None, 3), ("annotation", 5), ("task", 6)])
def test_recorded_paths_and_readonly_replay(tmp_path, domain, expected_calls):
    run = prepared(tmp_path)
    extract, annotate, repair, task_repair = TaskClient(), FakeClient(), FakeClient(), TaskClient(revised=True)
    review = ReviewClient() if domain is None else FirstIssue(domain)
    result = pipeline.run_analysis(run, client_factory=injected_factory(annotate),
        task_client_factory=injected_factory(extract), review_client_factory=injected_factory(review),
        repair_client_factory=injected_factory(repair), task_repair_client_factory=injected_factory(task_repair))
    assert result["status"] == "diagnostic", result
    assert result["refinement"]["status"] == "review_passed", result
    assert result["counts"]["logical_calls"] == expected_calls, result
    assert len(extract.prompts) == 1
    source_input = json.JSONDecoder().raw_decode(extract.prompts[0].split("COMPLETE_ORIGINAL_SOURCE\n\n")[1])[0]
    assert set(source_input) == {"basis", "source_files"}
    if domain == "task":
        revision = json.JSONDecoder().raw_decode(task_repair.prompts[0].split("ISOLATED_REVISION_DATA\n\n")[1])[0]
        assert set(revision) == {"previous_task", "objections"}
        assert set(revision["objections"][0]) == {"code", "source_spans", "requirement_ids"}
        assert "REPAIR_CONTEXT" not in repair.prompts[0]
        assert "declaration_index" not in task_repair.prompts[0]
        old = json.loads((run / "task/task.json").read_text(encoding="utf-8"))
        new = json.loads((run / "refinement/task-revision/task.json").read_text(encoding="utf-8"))
        assert old["task_sha256"] != new["task_sha256"]
        raw = json.loads((run / "refinement/repair/audit/raw-annotation.json").read_text(encoding="utf-8"))
        assert raw["task_revision_id"] == new["task_sha256"]
    assert pipeline.load_analysis_run(run)["result"] == result
    assert pipeline.replay_analysis(run) == result
