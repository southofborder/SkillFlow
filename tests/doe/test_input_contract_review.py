"""Contract acceptance is explicit, source-evidenced and bound to selection."""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.common.validation import StructuralValidationError
from skillflow.doe.input_contract_review import (
    build_input_contract_review, checked_input_contract_review,
)
from skillflow.document_guided.source_review import prepare_review_material, validate_source_review
from tests.document_guided.test_source_review import fixture


def bundle():
    from tests.doe.test_demand_engine import fixture as analysis_fixture, inp, evidence
    from skillflow.propagation.contracts.joint import joint_source_files
    from tests.document_guided.test_parallel_runner import _flat
    from tests.doe.input_review_helpers import checks_for_inventory
    contract = {"rules": [{"output": {"property": "value", "path": []}, "inputs": [
        {"input_index": 0, "required": [{"property": "value", "path": ["label"]}],
         "remainder": "independent", "reason": "Other request fields do not determine the label."}],
        "reason": "The output is the original label field.", "evidences": [evidence()]}]}
    facts, task, annotation, _ = analysis_fixture([{"op": "compute", "inputs": [inp()],
        "dependencies": ["possible"], "output": "label", "demand_transfer": contract}])
    cfg = facts.cfg
    files = joint_source_files(annotation["material"])
    raw, compiled = annotation["raw_annotation"], annotation["compiled_annotation"]
    wire = deepcopy(raw)
    mapping = annotation["mapping"]
    for item in mapping["events"]:
        if item.get("kind") == "observation":
            item["wire_path"] = deepcopy(item["raw_path"])
    mapping["fragment_origins"] = {"/ir_semantics": "processing"}
    material = prepare_review_material(files=files, task=task, cfg=cfg, annotation=wire,
        raw_annotation=raw, compiled=compiled, mapping=mapping, generation="fragment-v1")
    checks = checks_for_inventory(material["input_contract_inventory"], [evidence()])
    assert len(checks) == 1
    check = checks[0]
    return files, cfg, annotation, material, check


def review_for(material, check, findings=None):
    result = validate_source_review({"outcome": "completed", "findings": findings or [],
                                    "input_contract_checks": [check], "input_projection_checks": [], "source_input_findings": []}, material)
    return {"status": "complete", "review": result, "availability": material["availability"],
            "diagnostic_only": bool(result["findings"])}


def test_explicit_accepted_receipt_binds_all_selected_materials():
    files, cfg, annotation, material, check = bundle()
    receipt = build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
        review=review_for(material, check), review_material=material)
    assert receipt["source_review_complete"]
    assert checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation) == receipt
    for key in ("task", "raw_annotation", "compiled_annotation", "mapping"):
        changed = deepcopy(annotation)
        changed[key]["changed"] = True
        with pytest.raises(ValueError, match="another selected bundle"):
            checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=changed)
    with pytest.raises(ValueError, match="another selected bundle"):
        checked_input_contract_review(receipt, files={**files, "skill/extra.md": "extra"}, cfg=cfg, annotation=annotation)
    with pytest.raises(ValueError):
        checked_input_contract_review(receipt, files=files, cfg={**cfg, "changed": True}, annotation=annotation)


def test_completion_cannot_be_changed_independently_of_bound_review_coverage():
    files, cfg, annotation, material, check = bundle()
    receipt = build_input_contract_review(files=files, cfg=cfg, annotation=annotation)
    assert not receipt["source_review_complete"] and receipt["checks"] == []
    assert receipt["review_core"]["scope_decisions"] == {}
    receipt["source_review_complete"] = True
    receipt["receipt_sha256"] = canonical_sha256({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    with pytest.raises(ValueError, match="completion differ"):
        checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation)


def test_checks_need_exact_contract_coverage_and_real_source_evidence():
    files, cfg, annotation, material, check = bundle()
    with pytest.raises(StructuralValidationError, match="required|Field required"):
        validate_source_review({"outcome": "completed", "findings": []}, material)
    bad = deepcopy(check)
    bad["evidences"][0]["end_line"] = 400
    with pytest.raises(StructuralValidationError):
        review_for(material, bad)
    with pytest.raises(StructuralValidationError):
        validate_source_review({"outcome": "completed", "findings": [],
            "input_contract_checks": [check, check]}, material)


def test_raw_annotation_contract_keeps_its_actual_operation_target():
    files, cfg, annotation, material, check = bundle()
    mapping = {"events": [], "fragment_origins": {"/ir_semantics": "processing"}}
    raw = annotation["raw_annotation"]
    reviewed = prepare_review_material(files=files, task=annotation["task"], cfg=cfg,
        annotation=raw, raw_annotation=raw, compiled=annotation["compiled_annotation"], mapping=mapping,
        generation="fragment-v1")
    expected = annotation["compiled_annotation"]["input_contracts"][0]["raw_pointer"].rsplit("/", 1)[0]
    assert reviewed["input_contract_obligation_targets"][check["obligation_id"]] == "annotation:" + expected


@pytest.mark.parametrize("status", ["rejected", "unresolved"])
def test_nonaccepted_contract_routes_to_existing_processing_repair(status):
    files, cfg, annotation, material, check = bundle()
    from tests.doe.input_review_helpers import checks_for_inventory
    check = checks_for_inventory(material["input_contract_inventory"], check["evidences"], status=status)[0]
    result = review_for(material, check)
    finding = result["review"]["findings"][0]
    assert finding["domain"] == "annotation" and finding["owner"] == "processing"
    assert finding["target_ids"] == [material["input_contract_obligation_targets"][check["obligation_id"]]]
    assert finding["source_refs"] and check["reason"] in finding["explanation"]


def test_unrelated_finding_does_not_revoke_accepted_local_contract():
    files, cfg, annotation, material, check = bundle()
    block = next(iter(cfg["blocks"]))
    finding = {"domain": "cfg", "target_ids": [f"cfg:/blocks/{block}/instructions/0"],
        "explanation": "A different source relation needs review.",
        "source_refs": [{"file": "skill/SKILL.md", "start_line": 2, "end_line": 2}],
        "suggestion": "Retain the separate prohibition relationship."}
    reviewed = review_for(material, check, [finding])
    receipt = build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
        review=reviewed, review_material=material)
    assert receipt["source_review_complete"]
    assert receipt["checks"][0]["status"] == "accepted"
    assert receipt["review_core"]["findings"]
    changed = deepcopy(material)
    changed["input_contract_binding"]["cfg_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="another selected bundle"):
        build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
            review=reviewed, review_material=changed)


@pytest.mark.parametrize("target", ["operation", "annotation_parent", "cfg_instruction", "cfg_parent"])
def test_accepted_contract_cannot_overlap_known_representation_finding(target):
    files, cfg, annotation, material, check = bundle()
    protected = material["input_contract_targets"][check["obligation_id"]]
    actual = {"operation": protected[0], "annotation_parent": protected[0].rsplit("/", 2)[0],
              "cfg_instruction": protected[1], "cfg_parent": "cfg:"}[target]
    finding = {"domain": actual.split(":", 1)[0], "target_ids": [actual],
        "explanation": "This represented operation reads a different source field.",
        "source_refs": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1}],
        "suggestion": "Correct the operation's field and recheck its input contract."}
    with pytest.raises(StructuralValidationError, match="conflicts with a finding"):
        review_for(material, check, [finding])
    receipt = build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
        review=review_for(material, check), review_material=material)
    receipt["review_core"]["findings"] = [finding]
    receipt["review_sha256"] = canonical_sha256(receipt["review_core"])
    receipt["receipt_sha256"] = canonical_sha256({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    with pytest.raises(ValueError, match="conflicts with a finding"):
        checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation)


def test_source_error_is_sealed_separately_without_repairing_actual_arguments():
    files, cfg, annotation, material, check = bundle()
    entry = annotation["compiled_annotation"]["input_contracts"][0]
    candidate = {"kind": "missing_argument",
        "target_id": "annotation:" + entry["raw_pointer"].rsplit("/", 1)[0],
        "actual": {"kind": "absent_argument"},
        "expected": {"parameter": {"kind": "named", "name": "required_label"},
            "information": {"property": "value", "path": []}, "source_value": None,
            "description": "The independently specified invocation requires a second label argument."},
        "impacts": [{"kind": "output", "property": "value", "path": []}],
        "requirement_evidences": check["evidences"], "occurrence_evidences": check["evidences"],
        "reason": "The synthetic source invocation omits the separately required label argument."}
    before = deepcopy(annotation)
    parsed = validate_source_review({"outcome": "completed", "findings": [], "input_contract_checks": [check],
        "input_projection_checks": [], "source_input_findings": [candidate]}, material)
    assert parsed["source_input_findings"][0]["expected"]["source_value"] is None
    assert parsed["findings"] == []
    receipt = build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
        review={"status": "complete", "review": parsed, "availability": material["availability"]},
        review_material=material)
    assert receipt["checks"][0]["status"] == "accepted"
    assert len(receipt["review_core"]["source_input_findings"]) == 1
    assert checked_input_contract_review(receipt, files=files, cfg=cfg, annotation=annotation) == receipt
    assert annotation == before
