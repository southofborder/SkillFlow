"""The protocol validates provenance/coverage, not model semantic accuracy."""
from copy import deepcopy
import hashlib
import json
from threading import Event

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.contracts.task import (
    CandidateTask, TaskRepairObjection, checked_task, task_reference,
    validate_task_candidate, task_source_files,
)
from skillflow.task.material import prepare_task_material, validate_revision
from skillflow.task.prompts import build_task_prompt
from skillflow.task.services import extract_task
from skillflow.task.runner import prepare_task_run, run_task, load_task_run, TaskRunIdentityError


def source(files=None):
    files = files or {"SKILL.md": "Return label unchanged. Never send serial.\n\nTool can send JSON.\n"}
    rows = [{"path": path, "content": text, "sha256": hashlib.sha256(text.encode()).hexdigest()}
            for path, text in files.items()]
    return {"files": rows, "source_sha256": canonical_sha256([
        {key: row[key] for key in ("path", "sha256")} for row in rows])}


def span(file="skill/SKILL.md", start=1, end=1):
    return {"file": file, "start_line": start, "end_line": end, "reason": "源文明示该义务。"}


def candidate():
    return {"purpose": {"text": "返回 label。", "evidences": [span()]},
            "requirements": [
                {"id": "R1", "text": "返回 label 原值。", "evidences": [span()]},
                {"id": "R2", "text": "禁止发送 serial。", "evidences": [span()]}],
            "source_accounting": [
                {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                 "disposition": "requirement", "requirement_ids": ["R1", "R2"], "issue_ids": [], "reason": "同一行包含两项可独立遗漏的义务。"},
                {"file": "skill/SKILL.md", "start_line": 3, "end_line": 3,
                 "disposition": "capability", "requirement_ids": [], "issue_ids": [], "reason": "能力描述不自动形成要求。"}],
            "issues": []}


def seal(value=None, src=None, request=None):
    src = source() if src is None else src
    return validate_task_candidate(candidate() if value is None else value,
        source_files=task_source_files(src, user_request=request),
        basis="declared_skill" if request is None else "user_request", source_sha256=src["source_sha256"])


class Client:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return deepcopy(value)


def inventory(directory):
    return {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("*") if path.is_file()}


def test_same_physical_line_supports_independent_requirements_and_no_graph_binding():
    task = seal()
    assert task.source_accounting[0].requirement_ids == ["R1", "R2"]
    assert task.schema_version == "skillflow-task-v3"
    assert "bindings" not in task.requirements[0].model_dump()
    assert checked_task(task) == task
    assert task_reference(task)["task_sha256"] == task.task_sha256
    for name, value in (("bindings", []), ("necessary", True), ("minimal_fields", [])):
        bad = candidate()
        bad["requirements"][0][name] = value
        with pytest.raises(StructuralValidationError):
            seal(bad)


@pytest.mark.parametrize("mutation", ["missing", "repeated", "unknown_requirement", "unknown_issue", "missing_requirement_reference"])
def test_physical_accounting_missing_duplicate_and_dangling_references_rejected(mutation):
    bad = candidate()
    if mutation == "missing":
        bad["source_accounting"].pop()
    elif mutation == "repeated":
        bad["source_accounting"].append(deepcopy(bad["source_accounting"][0]))
    elif mutation == "unknown_requirement":
        bad["source_accounting"][0]["requirement_ids"].append("R404")
    elif mutation == "unknown_issue":
        bad["source_accounting"][0]["issue_ids"].append("I404")
    else:
        bad["source_accounting"][0]["requirement_ids"].remove("R2")
    with pytest.raises(StructuralValidationError):
        seal(bad)


def test_ranges_can_include_blank_lines_and_requirements_can_have_cross_file_evidence():
    src = source({"SKILL.md": "Return label.\n\nNever send serial.\n", "reference/rules.md": "Keep label unchanged.\n"})
    value = candidate()
    value["requirements"][0]["evidences"].append(span("skill/reference/rules.md"))
    value["source_accounting"] = [
        {**value["source_accounting"][0], "end_line": 3},
        {**value["source_accounting"][0], "file": "skill/reference/rules.md", "requirement_ids": ["R1"]}]
    assert seal(value, src).requirements[0].evidences[1].file == "skill/reference/rules.md"


def test_unsupported_interpretation_can_still_be_structurally_valid():
    value = candidate()
    value["requirements"][0]["text"] = "发送整个记录及所有凭据。"
    task = seal(value)
    assert task.requirements[0].text == value["requirements"][0]["text"]
    assert "semantically_valid" not in task.model_dump()


def test_task_and_request_identity_tampering_rejected():
    task = seal().model_dump(mode="json")
    task["requirements"][0]["text"] = "已篡改"
    with pytest.raises(ValueError, match="sealed identity"):
        checked_task(task)
    with pytest.raises(ValueError, match="source identity"):
        checked_task(seal(), source_sha256="0" * 64)
    value = candidate()
    value["purpose"]["evidences"] = [span("task/user-request.txt")]
    value["source_accounting"].append({**value["source_accounting"][0], "file": "task/user-request.txt"})
    with pytest.raises(StructuralValidationError, match="purpose must cite"):
        seal(request="Return label.")
    task = seal(value, request="Return label.")
    assert task.user_request_sha256 == hashlib.sha256(b"Return label.").hexdigest()
    with pytest.raises(ValueError, match="request identity"):
        checked_task(task, source_files=task_source_files(source(), user_request="Return summary."))


def test_source_material_closed_and_revision_rejects_free_text_graph_and_payload():
    material = prepare_task_material(source())
    objection = {"code": "missing_requirement", "source_spans": [
        {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}], "requirement_ids": []}
    revision = {"previous_task": seal().model_dump(mode="json"), "objections": [objection]}
    assert validate_revision(revision, material) == revision
    for key in ("reason", "recommendation", "cfg", "payload", "sink", "context"):
        with pytest.raises(ValueError):
            TaskRepairObjection.model_validate({**objection, key: "review free text"})
        with pytest.raises(ValueError):
            validate_revision({**revision, key: {}}, material)
    with pytest.raises(ValueError):
        TaskRepairObjection.model_validate({**objection, "code": "arbitrary_instructions"})
    with pytest.raises(ValueError):
        TaskRepairObjection.model_validate({**objection, "source_spans": [span()]})
    prompt = build_task_prompt(material, revision)
    assert "COMPLETE_ORIGINAL_SOURCE" in prompt and "ISOLATED_REVISION_DATA" in prompt
    data = json.JSONDecoder().raw_decode(prompt.split("COMPLETE_ORIGINAL_SOURCE\n\n", 1)[1])[0]
    assert set(data) == {"basis", "source_files"}


def test_structural_correction_does_not_turn_missing_coverage_into_accepted_task():
    bad = candidate()
    bad["source_accounting"].pop()
    client = Client(bad, candidate())
    result = extract_task(source(), client=client)
    assert len(client.prompts) == 2
    assert "STRUCTURAL_CORRECTION_CONTEXT" in client.prompts[1]
    assert result["task_sha256"] == seal().task_sha256


def test_cannot_assess_is_a_semantic_failure_without_correction_loop():
    client = Client({"outcome": "cannot_assess", "failure": {"reason": "存在无法解释的来源。", "evidences": [span()]}})
    with pytest.raises(SemanticFailure):
        extract_task(source(), client=client)
    assert len(client.prompts) == 1


def test_durable_task_owner_readonly_replay_and_tamper_detection(tmp_path):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    client = Client(candidate())
    result = run_task(directory, client=client)
    assert result["status"] == "complete", result
    assert len(client.prompts) == 1
    assert result["counts"]["stage_calls"] == 1
    assert "task" not in json.loads((directory / "result.json").read_text(encoding="utf-8"))
    before = inventory(directory)
    assert load_task_run(directory) == result
    assert inventory(directory) == before
    assert run_task(directory, client=Client())["task"] == result["task"]
    changed = json.loads((directory / "task.json").read_text(encoding="utf-8"))
    changed["requirements"][0]["text"] = "被修改的解释"
    (directory / "task.json").write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(TaskRunIdentityError, match="differs from accepted"):
        load_task_run(directory)


def test_source_owner_is_referenced_and_frozen_content_changes_rejected(tmp_path):
    owner, consumer = tmp_path / "source-owner", tmp_path / "task"
    (owner / "inputs").mkdir(parents=True)
    source_path = owner / "inputs/source.json"
    source_path.write_text(json.dumps(source()), encoding="utf-8")
    unsigned = {"identity": "test-frozen-owner", "files": {
        "inputs/source.json": hashlib.sha256(source_path.read_bytes()).hexdigest()}}
    (owner / "manifest.json").write_text(json.dumps({**unsigned, "manifest_sha256": canonical_sha256(unsigned)}), encoding="utf-8")
    prepare_task_run(consumer, source_owner=owner)
    assert not (consumer / "inputs/source.json").exists()
    assert run_task(consumer, client=Client(candidate()))["status"] == "complete"
    source_path.write_text(json.dumps(source({"SKILL.md": "Changed."})), encoding="utf-8")
    with pytest.raises(TaskRunIdentityError, match="inventory differs"):
        load_task_run(consumer)


def test_task_consumer_cannot_modify_its_source_owners_frozen_inputs(tmp_path):
    owner = tmp_path / "source-owner"
    (owner / "inputs").mkdir(parents=True)
    source_path = owner / "inputs/source.json"
    source_path.write_text(json.dumps(source()), encoding="utf-8")
    unsigned = {"identity": "test-frozen-owner", "files": {
        "inputs/source.json": hashlib.sha256(source_path.read_bytes()).hexdigest()}}
    (owner / "manifest.json").write_text(json.dumps({**unsigned, "manifest_sha256": canonical_sha256(unsigned)}), encoding="utf-8")
    before = inventory(owner)
    with pytest.raises(ValueError, match="frozen inputs"):
        prepare_task_run(owner / "inputs/task-consumer", source_owner=owner)
    assert inventory(owner) == before


def test_interruption_before_first_call_can_resume_without_inventing_a_response(tmp_path):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    stop = Event()
    stop.set()
    client = Client(candidate())
    result = run_task(directory, client=client, stop_event=stop)
    assert result["status"] == "interrupted" and client.prompts == []
    assert result["task"] is None
    assert run_task(directory, client=client)["status"] == "complete"


@pytest.mark.parametrize("field", ["schema_version", "policy"])
def test_resealed_manifest_does_not_coerce_boolean_into_integer(tmp_path, field):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    path = directory / "manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop("manifest_sha256")
    if field == "schema_version":
        value["schema_version"] = True
    else:
        value["policy"]["semantic_repairs"] = False
    path.write_text(json.dumps({**value, "manifest_sha256": canonical_sha256(value)}), encoding="utf-8")
    with pytest.raises(TaskRunIdentityError, match="protocol"):
        run_task(directory, client=Client(candidate()))


@pytest.mark.parametrize("target", ["task", "result"])
def test_saved_task_and_result_compare_json_types_not_python_equality(tmp_path, target):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    assert run_task(directory, client=Client(candidate()))["status"] == "complete"
    path = directory / ("task.json" if target == "task" else "result.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    if target == "task":
        value["requirements"][0]["evidences"][0]["start_line"] = True
    else:
        value["counts"]["logical_calls"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(TaskRunIdentityError):
        load_task_run(directory)


@pytest.mark.parametrize("mutation", ["empty_files", "bad_digest", "files_not_object", "producer_not_object"])
def test_readonly_loading_checks_saved_producer_self_consistency(tmp_path, mutation):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    assert run_task(directory, client=Client(candidate()))["status"] == "complete"
    path = directory / "manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop("manifest_sha256")
    if mutation == "empty_files":
        value["implementation"]["files"] = {}
        value["implementation"]["sha256"] = canonical_sha256({})
    elif mutation == "bad_digest":
        value["implementation"]["sha256"] = "0" * 64
    elif mutation == "files_not_object":
        value["implementation"]["files"] = ["not a saved producer inventory"]
    else:
        value["implementation"] = []
    path.write_text(json.dumps({**value, "manifest_sha256": canonical_sha256(value)}), encoding="utf-8")
    with pytest.raises(TaskRunIdentityError, match="producer identity"):
        load_task_run(directory)


def test_readonly_loading_does_not_require_current_producer_equality(tmp_path, monkeypatch):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    result = run_task(directory, client=Client(candidate()))
    assert result["status"] == "complete"
    monkeypatch.setattr("skillflow.task.runner.implementation_provenance", lambda: {"future": "implementation"})
    before = inventory(directory)
    assert load_task_run(directory) == result
    assert inventory(directory) == before
    with pytest.raises(TaskRunIdentityError, match="implementation differs"):
        run_task(directory, client=Client())
