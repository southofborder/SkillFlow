"""Explicit failed-stage target policy, exact bindings and strict locality."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.failed_stage_targets import (
    IDENTITY, correction_guard,
)
from skillflow.document_guided.source_review import (
    build_source_review_prompt, isolate_source_review, prepare_review_material,
    run_source_review, validate_source_review,
)
from tests.document_guided.test_source_review import Client, fixture, finding
from tests.doe.input_review_helpers import review_prompt_payload


def failure_evidence(files, stage="graph", *, status="structural_failure"):
    material = {"attempt_name": stage, "candidate": {"actual": "synthetic rejected representation"},
                "validation": {"status": status, "diagnostics": [{"code": "example", "path": "", "message": "Original failure"}]}}
    return {"status": status, "reason": "No accepted stage object", "diagnostics": material["validation"]["diagnostics"],
            "evidence": {"identity": "skillflow-failed-stage-material-v1", "stage": stage, "status": status,
                "source_sha256": canonical_sha256(files), "material_sha256": canonical_sha256(material),
                "material": material}}


def material_for(stage="graph", *, evidence=True, status="structural_failure"):
    files, task, cfg = fixture()
    failure = failure_evidence(files, stage, status=status)
    if not evidence:
        failure.pop("evidence")
    return prepare_review_material(files=files, task=None if stage == "task" else task,
        cfg=None if stage in {"task", "flow", "graph"} else cfg,
        stage_failures={stage: failure}, generation="fragment-v1")


def response(*findings):
    return {"outcome": "completed", "findings": list(findings), "input_contract_checks": [],
            "input_projection_checks": [], "source_input_findings": []}


def stage_finding(stage="graph"):
    domain = "task" if stage == "task" else "cfg" if stage in {"flow", "graph"} else "annotation"
    row = finding(domain)
    row["target_ids"] = ["stage:" + stage]
    if domain == "task":
        row["task_objection"] = {"code": "missing_requirement", "source_spans": deepcopy(row["source_refs"]),
                                 "requirement_ids": []}
    return row


@pytest.mark.parametrize("stage", ["task", "flow", "graph", "processing", "task-correspondence", "sensitivity"])
def test_actual_failed_stage_policy_matches_inventory_prompt_and_validator(stage):
    material = material_for(stage)
    targets = material["failed_stage_targets"]["targets"]
    assert len(targets) == 1 and targets[0]["id"] == "stage:" + stage
    assert targets[0] in material["target_index"]
    assert targets[0]["binding"]["source_sha256"] == canonical_sha256(material["files"])
    assert targets[0]["binding"]["failure_sha256"] == canonical_sha256(material["stage_failures"][stage])
    prompt = build_source_review_prompt(material)
    assert review_prompt_payload(prompt)["failed_stage_targets"] == material["failed_stage_targets"]
    assert "a key in stage_failures alone does not authorize a target" in prompt
    checked = validate_source_review(response(stage_finding(stage)), material)
    assert checked["findings"][0]["target_ids"] == ["stage:" + stage]
    assert material["cfg"] is None if stage in {"task", "flow", "graph"} else material["cfg"] is not None
    assert material["annotation"] is None
    if stage in {"processing", "task-correspondence", "sensitivity"}:
        assert checked["findings"][0]["owner"] == stage
    else:
        assert "owner" not in checked["findings"][0]


@pytest.mark.parametrize("stage", ["task", "flow", "graph"])
def test_upstream_stage_without_bound_original_material_is_explicitly_unavailable(stage):
    material = material_for(stage, evidence=False)
    assert material["failed_stage_targets"]["targets"] == []
    assert "lacks bound original-stage material" in material["failed_stage_targets"]["unavailable"][0]["reason"]
    with pytest.raises(StructuralValidationError):
        validate_source_review(response(stage_finding(stage)), material)


@pytest.mark.parametrize("stage", ["processing", "task-correspondence", "sensitivity"])
def test_existing_annotation_failure_material_keeps_strict_bound_compatibility(stage):
    material = material_for(stage, evidence=False)
    assert validate_source_review(response(stage_finding(stage)), material)["findings"]
    assert material["failed_stage_targets"]["targets"][0]["binding"]["failure_sha256"]


@pytest.mark.parametrize("status", ["partial", "skipped", "running", "complete", "request_failure", "interrupted", "failed"])
def test_nonsemantic_failure_states_never_create_a_failed_stage_target(status):
    material = material_for(status=status)
    assert material["failed_stage_targets"]["targets"] == []
    with pytest.raises(StructuralValidationError):
        validate_source_review(response(stage_finding()), material)


@pytest.mark.parametrize("key", ["identity", "stage", "status", "source_sha256", "material_sha256", "material"])
def test_supplied_failure_evidence_binding_is_checked_at_material_preparation(key):
    files, task, _ = fixture()
    failure = failure_evidence(files)
    failure["evidence"][key] = {} if key == "material" else "wrong"
    with pytest.raises(ValueError, match="Failed-stage review evidence"):
        prepare_review_material(files=files, task=task, stage_failures={"graph": failure}, generation="fragment-v1")


def test_accepted_object_and_present_fragment_suppress_failed_object_targets():
    files, task, cfg = fixture()
    material = prepare_review_material(files=files, task=task, cfg=cfg,
        stage_failures={"graph": failure_evidence(files)}, generation="fragment-v1")
    assert material["failed_stage_targets"]["targets"] == []
    with pytest.raises(StructuralValidationError):
        validate_source_review(response(stage_finding()), material)
    material = prepare_review_material(files=files, task=task, cfg=cfg, fragments={"processing": {}},
        stage_failures={"processing": failure_evidence(files, "processing")}, generation="fragment-v1")
    assert material["failed_stage_targets"]["targets"] == []


@pytest.mark.parametrize("name", ["cfg", "revision-graph", "Graph", "invented", "graph/child"])
def test_unknown_stage_spellings_are_rejected_without_alias_inference(name):
    material = material_for()
    row = stage_finding()
    row["target_ids"] = ["stage:" + name]
    with pytest.raises(StructuralValidationError) as caught:
        validate_source_review(response(row), material)
    context = caught.value.diagnostics[0]["context"]
    assert context["correction_scope"] == "same_domain_target"
    assert context["allowed_failed_stage_targets"] == [{"id": "stage:graph", "domain": "cfg", "stage": "graph"}]
    assert context["nearest_parent"] is None
    row["target_ids"] = ["stage:graph"]
    assert validate_source_review(response(row), material)["findings"]


@pytest.mark.parametrize("change", ["failure", "source", "target", "inventory", "material"])
def test_stale_bound_stage_target_is_rejected_without_losing_valid_task_siblings(change):
    material = material_for()
    target = next(row for row in material["target_index"] if row["id"] == "stage:graph")
    if change == "failure":
        material["stage_failures"]["graph"]["reason"] = "Changed failure"
    elif change == "source":
        material["files"]["skill/SKILL.md"] += "Another source line.\n"
    elif change == "target":
        target["binding"]["failure_sha256"] = "0" * 64
    elif change == "inventory":
        material["failed_stage_targets"]["targets"][0]["domain"] = "task"
    else:
        material["stage_failures"]["graph"]["evidence"]["material"]["candidate"] = {}
    valid = stage_finding("task")
    valid["target_ids"] = ["task:/requirements"]
    siblings = [{**deepcopy(valid), "explanation": f"Source-supported independent task omission {i}"} for i in range(5)]
    isolated = isolate_source_review(response(stage_finding(), *siblings), material)
    assert len(isolated["review"]["findings"]) == 5
    assert [row["status"] for row in isolated["validation"]["records"]] == ["invalid", *("validated" for _ in range(5))]
    assert isolated["validation"]["diagnostics"][0]["code"] == "review_target_binding"


def test_five_valid_task_findings_and_one_actual_graph_failure_are_all_reviewable():
    material = material_for()
    task = stage_finding("task")
    task["target_ids"] = ["task:/requirements"]
    rows = [{**deepcopy(task), "explanation": f"Independent requirement omission {i}"} for i in range(5)]
    checked = validate_source_review(response(stage_finding(), *rows), material)
    assert len(checked["findings"]) == 6
    assert material["availability"]["cfg"] is False
    assert material["input_contract_inventory"]["available"] is False


@pytest.mark.parametrize("change", ["domain", "owner", "source", "mixed_domain", "task_requirement"])
def test_failed_stage_findings_keep_domain_source_owner_and_task_isolation(change):
    material = material_for()
    row = stage_finding()
    if change == "domain":
        row = stage_finding("task")
        row["target_ids"] = ["stage:graph"]
    elif change == "owner":
        row["owner"] = "processing"
    elif change == "source":
        row["source_refs"] = []
    elif change == "mixed_domain":
        row = stage_finding("task")
        row["target_ids"] = ["task:", "stage:graph"]
    else:
        material = material_for("task")
        row = stage_finding("task")
        row["task_objection"]["requirement_ids"] = ["fabricated"]
    with pytest.raises(StructuralValidationError):
        validate_source_review(response(row), material)


def unrepresentable_case():
    files, task, _ = fixture()
    material = prepare_review_material(files=files, task=task, generation="fragment-v1")
    original = response(stage_finding())
    with pytest.raises(StructuralValidationError) as caught:
        validate_source_review(original, material)
    diagnostics = caught.value.diagnostics
    assert diagnostics[0]["context"]["correction_scope"] == "unrepresentable_domain"
    return original, diagnostics


@pytest.mark.parametrize("form", ["local_retarget", "local_replace", "whole_drop", "whole_retarget"])
def test_unrepresentable_allegation_cannot_disappear_or_become_an_unrelated_task(form):
    original, diagnostics = unrepresentable_case()
    task = stage_finding("task")
    task["target_ids"] = ["task:/requirements"]
    if form == "local_retarget":
        correction = {"replacements": [{"record_id": "/findings/0", "value": task}]}
    elif form == "local_replace":
        correction = {"replacements": [{"record_id": "/findings/0", "value": {**original["findings"][0], "explanation": "Different claim"}}]}
    elif form == "whole_drop":
        correction = response()
    else:
        correction = response(task)
    with pytest.raises(StructuralValidationError) as caught:
        correction_guard(original, diagnostics, correction)
    assert caught.value.diagnostics[0]["code"] == "review_target_unrepresentable"
    assert caught.value.diagnostics[0]["context"]["original_record"] == original["findings"][0]


def test_unrepresentable_record_can_remain_explicit_while_sibling_records_change():
    original, diagnostics = unrepresentable_case()
    correction_guard(original, diagnostics, {"replacements": []})
    correction_guard(original, diagnostics, deepcopy(original))
    correction_guard(original, diagnostics, {"replacements": [{"record_id": "/findings/1", "value": {"unrelated": "sibling"}}]})
    representable = deepcopy(diagnostics)
    representable[0]["context"]["correction_scope"] = "same_domain_target"
    correction_guard(original, representable, response())


def _stable_producer(monkeypatch):
    files = {"tests/document_guided/test_failed_stage_review_targets.py": "synthetic offline policy test"}
    monkeypatch.setattr("skillflow.document_guided.source_review.implementation_provenance",
                        lambda: {"files": files, "sha256": canonical_sha256(files)})


def test_exact_failed_graph_target_can_be_corrected_once_and_replayed_without_alias_acceptance(tmp_path, monkeypatch):
    _stable_producer(monkeypatch)
    files, task, _ = fixture()
    bad, corrected = stage_finding(), stage_finding()
    bad["target_ids"] = ["stage:cfg"]
    client = Client(response(bad), {"replacements": [{"record_id": "/findings/0", "value": corrected}]})
    args = {"files": files, "task": task, "stage_failures": {"graph": failure_evidence(files)},
            "generation": "fragment-v1"}
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "complete" and result["counts"]["structural_corrections"] == 1
    assert result["review"]["findings"][0]["target_ids"] == ["stage:graph"]
    assert result["availability"]["cfg"] is False
    assert len(client.prompts) == 2
    assert '"allowed_failed_stage_targets":[{"id":"stage:graph","domain":"cfg","stage":"graph"}]' in client.prompts[1]
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert len(client.prompts) == 2


@pytest.mark.parametrize("correction", ["empty", "unrelated_task"])
def test_unrepresentable_failure_survives_exhaustion_and_valid_task_siblings_remain_usable(tmp_path, monkeypatch, correction):
    _stable_producer(monkeypatch)
    files, task, _ = fixture()
    row = stage_finding("task")
    row["target_ids"] = ["task:/requirements"]
    siblings = [{**deepcopy(row), "explanation": f"Independent source-backed omission {i}"} for i in range(5)]
    original = response(stage_finding(), *siblings)
    replacement = {"replacements": [] if correction == "empty" else [{"record_id": "/findings/0", "value": row}]}
    client = Client(original, replacement)
    args = {"files": files, "task": task, "generation": "fragment-v1"}
    result = run_source_review(tmp_path, **args, client=client)
    assert result["status"] == "partial" and len(result["review"]["findings"]) == 5
    assert result["counts"]["structural_corrections"] == 1 and len(client.prompts) == 2
    records = result["validation"]["records"]
    assert [row["status"] for row in records] == ["invalid", *["validated"] * 5]
    assert records[0]["record_sha256"] == canonical_sha256(original["findings"][0])
    assert result["validation"]["diagnostics"][0]["context"]["correction_scope"] == "unrepresentable_domain"
    assert run_source_review(tmp_path, **args, replay=True) == result
    assert len(client.prompts) == 2


@pytest.mark.parametrize("stale_version", ["v5", "v6"])
def test_previous_review_generation_cannot_be_used_for_current_contract_acceptance(stale_version):
    from skillflow.doe.input_contract_review import build_input_contract_review, SOURCE_REVIEW_VERSION
    from tests.doe.test_input_contract_scopes import materials
    assert SOURCE_REVIEW_VERSION == "skillflow-document-source-review-fragment-v7"
    files, cfg, annotation, _ = materials()
    stale = {"schema_version": "skillflow-document-source-review-fragment-" + stale_version, **response()}
    with pytest.raises(ValueError, match="explicit current source-review protocol"):
        build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
            review={"status": "complete", "availability": dict.fromkeys(("task", "cfg", "annotation"), True),
                    "review": stale})
