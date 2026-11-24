import json
from copy import deepcopy

import pytest

from skillflow.common.structural_correction import StructuralCorrectionLimitReached
from skillflow.document_guided.accepted_stage_reader import checked_task_artifacts
from skillflow.task.runner import load_task_run, prepare_task_run, run_task
from skillflow.task.services import revise_task
from tests.task.test_protocol import Client, candidate, seal, source


def revision():
    return {"previous_task": seal().model_dump(mode="json"),
            "objections": [{"code": "condition_scope", "requirement_ids": ["R1"],
                            "source_spans": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}]}]}


def wrong_bracket():
    task = candidate()
    task["requirements"][0]["text"] = "Return the original label."
    wire = json.dumps(task, ensure_ascii=False)
    end = wire.index('}], "issues"')
    return task, wire[:end] + wire[end + 1:]


def test_direct_and_recorded_task_revision_bind_the_same_mechanical_fix(tmp_path):
    wanted, raw = wrong_bracket()
    baseline = revision()
    task = revise_task(source(), client=Client(raw), **baseline)
    assert task["requirements"] == wanted["requirements"]
    prepare_task_run(tmp_path, source(), revision=baseline, max_corrections=0)
    result = run_task(tmp_path, client=Client(raw))
    assert result["task"] == task
    assert result["revision_slots"]["repairs"][0]["character"] == "}"
    assert result["revision_slots"]["diagnostics"] == []
    assert json.loads((tmp_path / "calls/task/a001/response.json").read_bytes()) == raw
    assert load_task_run(tmp_path) == result


def test_unnamed_requirement_sharing_a_source_line_stays_read_only(tmp_path):
    task = candidate()
    task["requirements"][0]["text"] = "Return the original label."
    task["requirements"][1]["text"] = "Send the serial."
    previous = revision()
    prepare_task_run(tmp_path, source(), revision=previous)
    outcome = run_task(tmp_path, client=Client(task))
    assert outcome["task"]["requirements"][0] == task["requirements"][0]
    assert outcome["task"]["requirements"][1] == previous["previous_task"]["requirements"][1]
    assert outcome["revision_slots"]["retained_prior"] == ["/requirements/R2"]
    assert [d["code"] for d in outcome["revision_slots"]["diagnostics"]] == ["task_revision_scope"]
    assert load_task_run(tmp_path) == outcome


def test_local_invalid_new_requirement_never_disappears_as_an_accepted_task(tmp_path):
    raw = candidate()
    addition = deepcopy(raw["requirements"][0])
    addition.update(id="extra", evidences=[])
    raw["requirements"].append(addition)
    prepare_task_run(tmp_path, source(), revision=revision(), max_corrections=0)
    outcome = run_task(tmp_path, client=Client(raw))
    assert outcome["status"] == "structural_failure" and outcome["task"] is None
    assert any(d["path"].startswith("/requirements/2") and d["context"]["id"] == "extra"
               for d in outcome["failure"]["diagnostics"])


def test_task_local_correction_preserves_independent_revision(tmp_path):
    raw = candidate()
    raw["requirements"][0]["text"] = "Return the original label."
    new_claim = {**deepcopy(raw["requirements"][0]), "id": "R3"}
    raw["requirements"].append({**new_claim, "evidences": []})
    prepare_task_run(tmp_path, source(), revision=revision(), max_corrections=1, allow_cannot_assess=False)
    client = Client(raw, {"replacements": [{"record_id": "/requirements/2", "value": new_claim}]})
    result = run_task(tmp_path, client=client)
    assert result["status"] == "complete", result["failure"]
    assert result["task"]["requirements"] == [*raw["requirements"][:2], new_claim]
    assert len(client.prompts) == 2 and load_task_run(tmp_path) == result


def test_damaged_purpose_keeps_the_sealed_purpose_and_valid_claim(tmp_path):
    baseline = revision()
    proposed = candidate()
    proposed["requirements"][0]["text"] = "Return the original label."
    raw = ('{\n"purpose":{"text":???},\n"requirements":'
           + json.dumps(proposed["requirements"]) + ',\n"issues":[]\n}')
    direct = Client(raw)
    task = revise_task(source(), client=direct, **baseline)
    prepare_task_run(tmp_path, source(), revision=baseline, max_corrections=1, allow_cannot_assess=False)
    recorded = Client(raw)
    result = run_task(tmp_path, client=recorded)
    assert result["task"] == task
    assert task["requirements"] == proposed["requirements"]
    assert task["purpose"] == baseline["previous_task"]["purpose"]
    receipt = result["revision_slots"]
    assert receipt["retained_prior"] == ["/purpose"]
    assert [(d["code"], d["path"]) for d in receipt["diagnostics"]] == [("revision_record_json", "/purpose")]
    assert len(direct.prompts) == len(recorded.prompts) == 1
    assert load_task_run(tmp_path) == result


def test_absent_purpose_still_fails_the_full_task_envelope(tmp_path):
    raw = candidate()
    del raw["purpose"]
    prepare_task_run(tmp_path, source(), revision=revision(), max_corrections=0)
    result = run_task(tmp_path, client=Client(raw))
    assert result["status"] == "structural_failure"
    assert result["failure"]["diagnostics"][0]["code"] == "task_revision_envelope"


def test_mechanically_repaired_task_keeps_record_correction_coordinates(tmp_path):
    proposed = candidate()
    proposed["requirements"][0]["text"] = "Return the original label."
    new_claim = {**deepcopy(proposed["requirements"][0]), "id": "R3"}
    proposed["requirements"].append({**new_claim, "evidences": []})
    wire = json.dumps(proposed)
    end = wire.index('}], "issues"')
    raw = wire[:end] + wire[end + 1:]
    fix = json.dumps({"replacements": [{"record_id": "/requirements/2", "value": new_claim}]})
    fix = fix[:-3] + fix[-2:]  # The correction row also lacks one unambiguous closer.
    baseline = revision()
    manifest = prepare_task_run(tmp_path, source(), revision=baseline, max_corrections=1,
                                allow_cannot_assess=False, self_check=True)
    direct, recorded = Client(raw, fix), Client(raw, fix)
    result = run_task(tmp_path, client=recorded)
    assert result["status"] == "complete", result["failure"]
    assert revise_task(source(), client=direct, **baseline) == result["task"]
    assert result["task"]["requirements"] == [*proposed["requirements"][:2], new_claim]
    assert len(direct.prompts) == len(recorded.prompts) == 2
    for prompt in (direct.prompts[1], recorded.prompts[1]):
        assert "MECHANICAL RECORD CORRECTION" in prompt and '"/requirements/2"' in prompt
    assert result["revision_slots"]["correction"]["repairs"][0]["character"] == "}"
    validation = json.loads((tmp_path / "calls/task/a001/validation.json").read_bytes())
    assert validation["status"] == "structural_invalid" and validation["revision_slots_sha256"]
    assert result["response_chain"]["correction_strategy"] == "skillflow-task-revision-correction-v1"
    assert load_task_run(tmp_path) == result
    checked_task_artifacts(tmp_path, manifest, result, source=source())


def test_direct_task_revision_stops_after_one_failed_correction(tmp_path):
    raw = candidate()
    bad = {**deepcopy(raw["requirements"][0]), "id": "R3", "evidences": []}
    raw["requirements"].append(bad)
    correction = {"replacements": [{"record_id": "/requirements/2", "value": bad}]}
    direct, recorded = Client(raw, correction), Client(raw, correction)
    baseline = revision()
    with pytest.raises(StructuralCorrectionLimitReached):
        revise_task(source(), client=direct, **baseline)
    prepare_task_run(tmp_path, source(), revision=baseline, max_corrections=1)
    result = run_task(tmp_path, client=recorded)
    assert result["status"] == "structural_failure" and len(direct.prompts) == len(recorded.prompts) == 2
    assert run_task(tmp_path, replay=True, read_only=True) == result
