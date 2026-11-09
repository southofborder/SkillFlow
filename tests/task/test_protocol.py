"""The compact protocol validates provenance and references, not model semantic accuracy."""
from copy import deepcopy
import hashlib
import json
from threading import Event

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import extract_source_lines
from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.contracts.task import (
    CandidateTask, TaskReference, TaskRepairObjection, checked_task, task_reference,
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
            "issues": []}


def seal(value=None, src=None):
    src = source() if src is None else src
    return validate_task_candidate(candidate() if value is None else value,
        source_files=task_source_files(src),
        source_sha256=src["source_sha256"])


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
    assert task.requirements[0].evidences == task.requirements[1].evidences
    assert "source_accounting" not in task.model_dump()
    assert task.schema_version == "skillflow-task-v5"
    assert task_reference(task)["schema_version"] == "skillflow-task-reference-v3"
    assert "basis" not in task.model_dump()
    assert "basis" not in task_reference(task)
    assert "user_request_sha256" not in task.model_dump()
    assert "user_request_sha256" not in task_reference(task)
    assert "bindings" not in task.requirements[0].model_dump()
    assert checked_task(task) == task
    assert task_reference(task)["task_sha256"] == task.task_sha256
    for name, value in (("bindings", []), ("necessary", True), ("minimal_fields", [])):
        bad = candidate()
        bad["requirements"][0][name] = value
        with pytest.raises(StructuralValidationError):
            seal(bad)


@pytest.mark.parametrize("legacy", [[], [{"file": "skill/SKILL.md", "start_line": 1,
    "end_line": 1, "disposition": "requirement", "requirement_ids": ["R1"],
    "issue_ids": [], "reason": "A retired line-accounting entry."}]])
def test_retired_source_accounting_is_strictly_rejected(legacy):
    bad = {**candidate(), "source_accounting": legacy}
    with pytest.raises(StructuralValidationError, match="source_accounting"):
        seal(bad)


def test_unreferenced_context_does_not_require_duplicate_model_registration():
    task = seal()
    assert all(e.end_line == 1 for requirement in task.requirements for e in requirement.evidences)
    assert set(CandidateTask.model_fields) == {"purpose", "requirements", "issues"}
    prompt = build_task_prompt(prepare_task_material(source()))
    assert "Tool can send JSON." in prompt
    assert "source_accounting" not in prompt
    assert "every nonempty" not in prompt
    assert "prohibitions" in prompt


@pytest.mark.parametrize("mutation", ["unknown_requirement", "duplicate_issue", "unknown_file", "invalid_span"])
def test_issue_references_and_source_spans_remain_checked(mutation):
    bad = candidate()
    issue = {"id": "I1", "kind": "ambiguity", "evidences": [span()],
             "requirement_ids": ["R1"], "resolution": "unresolved", "reason": "Unresolved interpretation."}
    bad["issues"] = [issue]
    if mutation == "unknown_requirement":
        issue["requirement_ids"] = ["R404"]
    elif mutation == "duplicate_issue":
        bad["issues"].append(deepcopy(issue))
    elif mutation == "unknown_file":
        issue["evidences"][0]["file"] = "skill/missing.md"
    else:
        issue["evidences"][0]["end_line"] = 100
    with pytest.raises(StructuralValidationError):
        seal(bad)


@pytest.mark.parametrize("field,value", [("start_line", True), ("start_line", 0),
    ("start_line", 3), ("end_line", 99), ("file", "skill/missing.md")])
def test_requirement_spans_remain_strict(field, value):
    bad = candidate()
    bad["requirements"][0]["evidences"][0][field] = value
    with pytest.raises(StructuralValidationError):
        seal(bad)


def test_ranges_can_include_blank_lines_and_requirements_can_have_cross_file_evidence():
    src = source({"SKILL.md": "Return label.\n\nNever send serial.\n", "reference/rules.md": "Keep label unchanged.\n"})
    value = candidate()
    value["requirements"][0]["evidences"].append(span("skill/reference/rules.md"))
    value["requirements"][1]["evidences"] = [span(start=1, end=3)]
    assert seal(value, src).requirements[0].evidences[1].file == "skill/reference/rules.md"


def test_unsupported_interpretation_can_still_be_structurally_valid():
    value = candidate()
    value["requirements"][0]["text"] = "发送整个记录及所有凭据。"
    task = seal(value)
    assert task.requirements[0].text == value["requirements"][0]["text"]
    assert "semantically_valid" not in task.model_dump()


def test_task_and_source_identity_tampering_rejected():
    task = seal().model_dump(mode="json")
    task["requirements"][0]["text"] = "已篡改"
    with pytest.raises(ValueError, match="sealed identity"):
        checked_task(task)
    with pytest.raises(ValueError, match="source identity"):
        checked_task(seal(), source_sha256="0" * 64)


def test_retired_request_material_basis_and_identity_fields_are_rejected():
    from skillflow.task.material import checked_task_material
    material = prepare_task_material(source())
    assert set(material) == {"version", "source"}
    assert material["version"] == "skillflow-task-material-v3"
    with pytest.raises(ValueError, match="source-only fields"):
        checked_task_material({**material, "user_request": None})
    with pytest.raises(ValueError, match="source-only fields"):
        checked_task_material({**material, "basis": "declared_skill"})
    for field, value in (("basis", "user_request"), ("basis", "declared_skill"), ("user_request_sha256", None)):
        task = seal().model_dump(mode="json")
        task[field] = value
        task["task_sha256"] = canonical_sha256({k: v for k, v in task.items() if k != "task_sha256"})
        with pytest.raises(ValueError):
            checked_task(task)
    for field, value in (("basis", "declared_skill"), ("user_request_sha256", None)):
        with pytest.raises(ValueError):
            TaskReference.model_validate({**task_reference(seal()), field: value})


@pytest.mark.parametrize("retired_request", [None, "Return label.", "", False])
def test_retired_user_request_argument_is_rejected_before_calls_or_files(tmp_path, retired_request):
    from skillflow.task.services import revise_task
    client = Client(candidate())
    for call in (
        lambda: task_source_files(source(), user_request=retired_request),
        lambda: prepare_task_material(source(), user_request=retired_request),
        lambda: extract_task(source(), client=client, user_request=retired_request),
        lambda: revise_task(source(), previous_task=seal(), objections=[], client=client, user_request=retired_request),
        lambda: prepare_task_run(tmp_path / "task", source(), user_request=retired_request),
    ):
        with pytest.raises(TypeError, match="user_request"):
            call()
    assert client.prompts == []
    assert not (tmp_path / "task").exists()


def test_retired_task_namespace_and_non_skill_purpose_are_rejected():
    value = candidate()
    value["purpose"]["evidences"] = [span("task/user-request.txt")]
    with pytest.raises(StructuralValidationError, match="frozen Skill file"):
        seal(value)
    files = {**task_source_files(source()), "task/user-request.txt": "Return label."}
    with pytest.raises(ValueError, match="only accepts frozen Skill"):
        validate_task_candidate(candidate(), source_files=files)
    with pytest.raises(TypeError, match="basis"):
        validate_task_candidate(candidate(), source_files=task_source_files(source()), basis="user_request")


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
    for code in ("arbitrary_instructions", "source_disposition"):
        with pytest.raises(ValueError):
            TaskRepairObjection.model_validate({**objection, "code": code})
    with pytest.raises(ValueError):
        TaskRepairObjection.model_validate({**objection, "source_spans": [span()]})
    prompt = build_task_prompt(material, revision)
    assert "COMPLETE_ORIGINAL_SOURCE" in prompt and "ISOLATED_REVISION_DATA" in prompt
    data = json.JSONDecoder().raw_decode(prompt.split("COMPLETE_ORIGINAL_SOURCE\n\n", 1)[1])[0]
    assert set(data) == {"source_files"}


def test_structural_correction_preserves_source_reference_validation():
    bad = candidate()
    bad["requirements"][0]["evidences"][0]["end_line"] = 100
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
    assert run_task(directory, replay=True)["task"] == result["task"]
    assert "source_accounting" not in (directory / "report.md").read_text(encoding="utf-8")
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
        # Counts are passive observer data. Program-owned decision fields still
        # compare JSON types exactly, even where Python considers 3 == 3.0.
        value["schema_version"] = float(value["schema_version"])
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


@pytest.mark.parametrize("ending", ["\n", "\r\n", ""])
def test_physical_evidence_preserves_original_multilingual_text(ending):
    text = "返回原字段。" + (ending or "\n") + "\n" + "Do not disclose the credential." + ending
    src = source({"SKILL.md": text})
    value = candidate()
    value["requirements"][0]["evidences"] = [span(start=1, end=3)]
    task = seal(value, src)
    evidence = task.requirements[0].evidences[0]
    assert extract_source_lines(text, evidence.start_line, evidence.end_line) == text
    material = prepare_task_material(src)
    prompt_data = json.JSONDecoder().raw_decode(
        build_task_prompt(material).split("COMPLETE_ORIGINAL_SOURCE\n\n", 1)[1])[0]
    assert "".join(prompt_data["source_files"][0]["lines"]) == text


@pytest.mark.parametrize("task_version,reference_version", [("skillflow-task-v3", "skillflow-task-reference-v1"),
    ("skillflow-task-v4", "skillflow-task-reference-v2")])
def test_old_task_and_reference_versions_are_not_reinterpreted(task_version, reference_version):
    value = seal().model_dump(mode="json")
    value["schema_version"] = task_version
    value.pop("task_sha256")
    value["task_sha256"] = canonical_sha256(value)
    with pytest.raises(ValueError):
        checked_task(value)
    reference = task_reference(seal())
    reference["schema_version"] = reference_version
    with pytest.raises(ValueError):
        TaskReference.model_validate(reference)


@pytest.mark.parametrize("run_version", [1, 2])
def test_old_task_run_identity_rejected_without_call(tmp_path, run_version):
    directory = tmp_path / "task"
    prepare_task_run(directory, source())
    path = directory / "manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop("manifest_sha256")
    value.update(identity=f"skillflow-task-extraction-v{run_version}", schema_version=run_version)
    path.write_text(json.dumps({**value, "manifest_sha256": canonical_sha256(value)}), encoding="utf-8")
    client = Client(candidate())
    with pytest.raises(TaskRunIdentityError, match="protocol"):
        run_task(directory, client=client)
    assert client.prompts == []
