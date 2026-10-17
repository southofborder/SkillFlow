"""Task evidence validates text locations and graph references, never entailment."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from skillflow.common.paths import project_root
from skillflow.common.source_evidence import extract_source_lines, resolve_pointer
from skillflow.doe.task_material import prepare_task_review
from tests.doe.helpers import fact_fixture
from skillflow.propagation.contracts.task import (
    CandidateTask, Task, TaskEvidence, build_task_target_index, task_source_files,
    validate_task_candidate,
)


CASES = project_root() / "experiments/propagation/runs/sink-tightening-v1-20261002-205045/cases"


def _cfg():
    return {"entry_block_id": "main", "constraints": ["Never disclose credentials."],
            "blocks": {"main": {"block_id": "main", "block_name": "Result",
                "instructions": [
                    {"id": "ir_read", "opcode": "read", "inputs": [],
                     "outputs": [{"type": "result", "identifier": "r"}],
                     "constraints": ["Preserve the body value."],
                     "metadata": {"field/name~": ["body", None, {}]}},
                    {"id": "ir_return", "opcode": "return", "inputs": [
                        {"type": "result", "identifier": "r"}], "outputs": []}]}}, "edges": []}


def _span(file="skill/SKILL.md", start=1, end=1):
    return {"file": file, "start_line": start, "end_line": end,
            "reason": "The cited instruction states the required result."}


def _candidate(target=None):
    value = {"purpose": {"text": "Return the required value.", "evidences": [_span()]},
        "requirements": [{"id": "R1", "text": "Preserve the required return value.", "evidences": [_span()]}],
        "source_accounting": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "disposition": "requirement", "requirement_ids": ["R1"], "issue_ids": [],
            "reason": "独立来源契约样例。"}], "issues": []}
    if target is not None:
        value["requirements"][0]["bindings"] = [{"target": target, "reason": "Task 阶段禁止图绑定。"}]
    return value


def _index():
    return build_task_target_index(_cfg())


def _validate(candidate):
    return validate_task_candidate(candidate, source_files={"skill/SKILL.md": "Return body unchanged.\n"},
                                   basis="declared_skill")


def _id_at(index, pointer):
    return next(value["target"] for value in index.values() if value["pointer"] == pointer)


def test_candidate_has_only_claims_and_task_basis_is_program_derived():
    candidate = _candidate()
    task = _validate(candidate)
    assert set(task.model_dump()) == {"schema_version", "basis", "purpose", "requirements",
        "source_sha256", "user_request_sha256", "task_sha256", "source_accounting", "issues"}
    assert task.schema_version == "skillflow-task-v3"
    assert task.basis == "declared_skill"
    for key, value in [("basis", "user_request"), ("schema_version", "skillflow-task-v2")]:
        with pytest.raises(ValueError):
            _validate({**candidate, key: value})


def test_no_ref_id_quote_or_digest_in_evidence():
    for key in ["ref_id", "quote", "sha256", "source_id"]:
        with pytest.raises(ValueError):
            TaskEvidence.model_validate({**_span(), key: "not part of this contract"})


@pytest.mark.parametrize("field,value", [
    ("file", " "), ("reason", "\t"), ("start_line", True), ("end_line", False),
    ("start_line", 0), ("end_line", -1), ("start_line", "1"), ("end_line", 1.0),
])
def test_strict_evidence_fields(field, value):
    with pytest.raises(ValueError):
        TaskEvidence.model_validate({**_span(), field: value})


@pytest.mark.parametrize("span", [_span(start=2, end=1), _span(end=2),
    _span(file="SKILL.md"), _span(file="task/user-request.txt"),
    _span(file="skill/../SKILL.md"), _span(file="skill/missing.md")])
def test_invalid_spans_are_rejected(span):
    candidate = _candidate()
    candidate["requirements"][0]["evidences"] = [span]
    with pytest.raises(ValueError):
        _validate(candidate)


@pytest.mark.parametrize("mutation", ["evidence", "purpose_evidence", "binding", "requirement"])
def test_duplicate_references_and_ids_are_rejected(mutation):
    root = _id_at(_index(), "")
    candidate = _candidate(root)
    requirement = candidate["requirements"][0]
    if mutation == "evidence":
        requirement["evidences"].append({**_span(), "reason": "A different reason does not change the span."})
    elif mutation == "purpose_evidence":
        candidate["purpose"]["evidences"].append(_span())
    elif mutation == "binding":
        requirement["bindings"].append({"target": root, "reason": "Still the same target."})
    else:
        candidate["requirements"].append(deepcopy(requirement))
    with pytest.raises(ValueError):
        _validate(candidate)


@pytest.mark.parametrize("field", ["evidences", "text"])
def test_explicit_fields_are_required_but_unbound_requirement_is_valid(field):
    candidate = _candidate()
    assert not hasattr(_validate(candidate).requirements[0], "bindings")
    del candidate["requirements"][0][field]
    with pytest.raises(ValueError):
        _validate(candidate)


def test_empty_requirements_and_unsupported_future_fields_are_rejected():
    for key, value in [("necessary", True), ("minimal_fields", []), ("sensitivity", [])]:
        candidate = _candidate()
        candidate["requirements"][0][key] = value
        with pytest.raises(ValueError):
            _validate(candidate)
    candidate = _candidate()
    candidate["requirements"] = []
    with pytest.raises(ValueError):
        _validate(candidate)


def test_same_span_and_target_may_support_different_requirements():
    candidate = _candidate()
    candidate["requirements"].append({**deepcopy(candidate["requirements"][0]), "id": "R2"})
    candidate["source_accounting"][0]["requirement_ids"].append("R2")
    assert len(_validate(candidate).requirements) == 2


def test_real_quote_with_wrong_interpretation_is_not_misrepresented_as_semantic_validation():
    candidate = _candidate()
    candidate["requirements"][0]["text"] = "Return the complete response and all credentials."
    task = _validate(candidate)
    assert task.requirements[0].text == candidate["requirements"][0]["text"]
    assert not {"passed", "semantically_valid", "complete", "necessary"} & task.model_dump().keys()
    assert extract_source_lines("Return body unchanged.\n", 1, 1) == "Return body unchanged.\n"


def test_targets_cover_actual_structure_without_inventing_return_output():
    cfg, targets = _cfg(), _index()
    pointers = {value["pointer"] for value in targets.values()}
    for pointer in ["", "/constraints/0", "/blocks/main", "/blocks/main/instructions/0",
                    "/blocks/main/instructions/0/outputs/0", "/blocks/main/instructions/1/inputs/0",
                    "/blocks/main/instructions/0/metadata/field~1name~0/2"]:
        assert pointer in pointers
    assert "/blocks/main/instructions/1/outputs/0" not in pointers
    for item in targets.values():
        resolve_pointer(cfg, item["pointer"])
    return_input = _id_at(targets, "/blocks/main/instructions/1/inputs/0")
    assert targets[__import__("json").dumps(return_input,sort_keys=True,separators=(",",":"))]["kind"] == "input"
    assert targets[__import__("json").dumps(return_input,sort_keys=True,separators=(",",":"))]["instruction_id"] == "ir_return"
    with pytest.raises(ValueError):
        _validate(_candidate(return_input))  # Graph bindings are forbidden in source-only Task.


def test_invalid_operand_and_dangling_target_are_not_created():
    targets = _index()
    nonexistent = "/blocks/main/instructions/1/inputs/10"
    assert nonexistent not in {v["pointer"] for v in targets.values()}
    with pytest.raises(ValueError, match="bindings.*Extra inputs"):
        _validate(_candidate("target_nonexistent"))
    bad = _cfg()
    bad["blocks"]["main"]["instructions"][1]["outputs"] = [{"type": "result", "identifier": "illegal"}]
    with pytest.raises(ValueError):
        build_task_target_index(bad)


def test_target_identity_is_deterministic_and_object_order_invariant():
    cfg = _cfg()
    reordered = json.loads(json.dumps(cfg, sort_keys=True))
    assert build_task_target_index(cfg) == build_task_target_index(reordered)
    for entry in build_task_target_index(cfg).values():
        assert entry["target"] is not None  # transient lookup, never a model address table


@pytest.mark.parametrize("block_id", ["constraints", "metadata", "inputs"])
def test_target_kinds_follow_structure_not_free_block_or_metadata_names(block_id):
    cfg = _cfg()
    block = cfg["blocks"].pop("main")
    block["block_id"] = block_id
    block["constraints"] = ["A genuine block constraint."]
    cfg["blocks"][block_id] = block
    cfg["entry_block_id"] = block_id
    block["instructions"][0]["metadata"] = {
        "constraints": {"data": "opaque", "metadata": []},
        "metadata": {"inputs": ["body"]},
        "instructions": {"outputs": None},
    }
    kinds = {item["pointer"]: item["kind"] for item in build_task_target_index(cfg).values()}
    base = f"/blocks/{block_id}"
    ir = base + "/instructions/0"
    assert kinds[base] == "block"
    assert kinds[base + "/block_name"] == "field"
    assert kinds["/constraints"] == "constraints"
    assert kinds["/constraints/0"] == "constraint"
    assert kinds[base + "/constraints"] == "constraints"
    assert kinds[base + "/constraints/0"] == "constraint"
    assert kinds[ir + "/constraints"] == "constraints"
    assert kinds[ir + "/constraints/0"] == "constraint"
    assert kinds[ir + "/metadata"] == "metadata"
    for pointer, kind in kinds.items():
        if pointer.startswith(ir + "/metadata/"):
            assert kind == "metadata_value"
    assert kinds[ir + "/outputs"] == "container"
    assert kinds[ir + "/outputs/0"] == "output"
    assert kinds[ir + "/outputs/0/identifier"] == "operand_field"


def test_source_paths_are_namespaced_without_text_normalization():
    source = {"files": [{"path": "user-request.txt", "content": "Skill\r\n"},
                         {"path": "ref/workflow.md", "content": "Cross-file requirement."}]}
    original = deepcopy(source)
    files = task_source_files(source, user_request="User\r\n")
    assert files == {"skill/user-request.txt": "Skill\r\n", "skill/ref/workflow.md": "Cross-file requirement.",
                     "task/user-request.txt": "User\r\n"}
    assert source == original


@pytest.mark.parametrize("path", ["../SKILL.md", "/SKILL.md", "C:/SKILL.md", "a/../SKILL.md", "a\\b.md"])
def test_source_path_aliases_and_escapes_are_rejected(path):
    with pytest.raises(ValueError):
        task_source_files({"files": [{"path": path, "content": "Task"}]})


def test_duplicate_source_paths_and_empty_user_request_are_rejected():
    file = {"path": "SKILL.md", "content": "Task"}
    with pytest.raises(ValueError):
        task_source_files({"files": [file, file]})
    for task in ["", "  ", False, 1]:
        with pytest.raises(ValueError):
            task_source_files({"files": [file]}, user_request=task)


def test_user_request_selects_basis_and_must_support_purpose_but_skill_requirements_remain():
    files = {"skill/SKILL.md": "Return body unchanged.\n", "task/user-request.txt": "Give me the body.\r\n"}
    candidate = _candidate()
    with pytest.raises(ValueError, match="purpose must cite"):
        validate_task_candidate(candidate, source_files=files, basis="user_request")
    candidate["purpose"]["evidences"] = [_span(file="task/user-request.txt")]
    candidate["source_accounting"].append({"file": "task/user-request.txt", "start_line": 1, "end_line": 1,
        "disposition": "supporting_context", "requirement_ids": [], "issue_ids": [], "reason": "独立任务目的。"})
    result = validate_task_candidate(candidate, source_files=files, basis="user_request")
    assert result.basis == "user_request"
    assert result.requirements[0].evidences[0].file == "skill/SKILL.md"
    with pytest.raises(ValueError, match="source identity"):
        validate_task_candidate(candidate, source_files=files, basis="declared_skill")


def test_candidate_serialization_strict_json_and_isolation():
    candidate = _candidate()
    task = _validate(json.dumps(candidate))
    assert Task.model_validate_json(task.model_dump_json()) == task
    candidate["requirements"][0]["text"] = "Changed after validation"
    assert task.requirements[0].text != candidate["requirements"][0]["text"]
    with pytest.raises(ValueError, match="duplicate JSON member"):
        _validate('{"purpose":{},"purpose":{},"requirements":[]}')
    with pytest.raises(ValueError):
        _validate(json.dumps(_candidate()) + "}")
    candidate = _candidate()
    candidate["requirements"] = tuple(candidate["requirements"])
    with pytest.raises(ValueError):
        _validate(candidate)


@pytest.mark.parametrize("case", ["001", "010", "013"])
def test_fixed_cases_prepare_without_audit_dependencies_or_data_mutation(case, tmp_path):
    path = CASES / case / "propagation/doe-input.json"
    raw_bytes = path.read_bytes()
    raw = fact_fixture(path)
    baseline = deepcopy(raw)
    from tests.doe.fixtures.task_examples import authored_candidate
    candidate = authored_candidate(case, raw.cfg)
    first = prepare_task_review(raw, candidate)
    second = prepare_task_review(raw, CandidateTask.model_validate(candidate))
    assert first == second
    assert first.cfg == raw.cfg
    assert first.boundaries == raw.source_metadata
    assert first.task.basis == "declared_skill"
    assert first.realizations and first.index_dict()["targets"]
    assert all(set(entry) == {"file", "original_path", "origin", "line_count"}
               for entry in first.index_dict()["files"])
    assert set(first.files) == {"skill/" + value["path"] for value in raw.source["files"]}
    # Both results are independent of caller-owned or other review dictionaries.
    first.cfg["constraints"] = ["mutated isolated view"]
    first.targets.clear()
    first.files.clear()
    assert prepare_task_review(raw, candidate) == second
    assert path.read_bytes() == raw_bytes
    assert baseline == raw


def test_service_rejects_tampered_source_and_candidate_with_program_owned_basis():
    raw = fact_fixture(CASES / "001/propagation/doe-input.json")
    raw.source["files"][0]["content"] += "tampered"
    with pytest.raises(ValueError):
        prepare_task_review(raw, _candidate())
    raw = fact_fixture(CASES / "001/propagation/doe-input.json")
    with pytest.raises(ValueError):
        prepare_task_review(raw, {**_candidate(), "basis": "declared_skill"})
