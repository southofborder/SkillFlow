"""The single shared repair round has explicit upstream and review barriers.

These tests construct only synthetic program-owned material. No historical
candidate, project compiler, backend, response replay or model is executed.
"""
from copy import deepcopy

import pytest

from skillflow.common.recording import canonical_sha256
from skillflow.document_guided.shared_repair import repair_decision


def admission_material():
    files = {"skill/SKILL.md": "Collect matching names and return the completed list.\n"}
    response = {"blocks": ["synthetic rejected CFG"]}
    validation = {"status": "structural_invalid", "candidate_sha256": canonical_sha256(response),
        "response_sha256": canonical_sha256(response), "normalization_sha256": None,
        "diagnostics": [{"code": "read_before_definition", "path": "/blocks/1/instructions/0/inputs/1",
                         "message": "The retained collection has no preceding definition."}]}
    def artifact(path):
        return {"path": path, "sha256": "a" * 64}
    material = {"attempt": "graph", "accepted": False,
        "artifacts": {name: artifact("synthetic/" + name + ".json") for name in
                      ["run_manifest", "source_manifest", "stage_manifest", "stage_result", "response_chain"]},
        "attempts": [{"ordinal": ordinal, "status": "structural_invalid", "validation": deepcopy(validation),
                      "validation_sha256": canonical_sha256(validation),
                      "artifacts": {name: artifact(f"steps/graph/calls/a{ordinal:03d}/" + name) for name in
                                    ["request.json", "prompt.txt", "call.json", "transport.json", "response.json", "validation.json"]}}
                     for ordinal in (1, 2)],
        "response": response, "candidate_source": "response",
        "validation": validation}
    evidence = {"identity": "skillflow-failed-stage-material-v1", "stage": "graph", "status": "structural_failure",
        "source_sha256": canonical_sha256(files), "material": material, "material_sha256": canonical_sha256(material)}
    return {"files": files, "values": {"task": {"value": {"accepted": "source-only Task"}},
                                       "flow": {"value": "accepted source flow"}},
        "errors": {"graph": {"status": "structural_failure", "reason": "Rejected terminal graph", "evidence": evidence}},
        "reviewed": {"status": "complete", "review": {"findings": []}}, "selected": None}


def rebind_material(args):
    evidence = args["errors"]["graph"]["evidence"]
    evidence["material_sha256"] = canonical_sha256(evidence["material"])


def finding(domain="cfg", owner=None):
    row = {"domain": domain, "target_ids": ["stage:graph" if domain == "cfg" else domain + ":"],
           "explanation": "An independently source-supported representation defect."}
    if owner is not None:
        row["owner"] = owner
    return row


def assert_barrier(args, phrase):
    decision = repair_decision(**args)
    assert decision["eligible"] is False
    assert decision["mode"] == "not_admitted" and decision["domains"] == []
    assert "recovery_failure" not in decision
    assert any(phrase in reason for reason in decision["barriers"])
    assert decision["budget_rounds"] == 1
    return decision


def test_bound_required_cfg_can_use_the_existing_shared_round_without_inventing_a_finding_or_value():
    args = admission_material()
    original = deepcopy(args)
    decision = repair_decision(**args)
    assert args == original
    assert decision["eligible"] is True and decision["mode"] == "missing_cfg_rebuild"
    assert decision["budget_rounds"] == 1 and decision["domains"] == ["cfg"]
    assert decision["finding_count"] == 0 and "graph" not in args["values"]
    assert decision["accepted_stages"] == ["flow", "task"]
    assert decision["graph_failure_sha256"] == canonical_sha256(args["errors"]["graph"])
    assert decision["source_sha256"] == canonical_sha256(args["files"])
    assert decision["review_sha256"] == canonical_sha256(args["reviewed"])
    assert decision["graph_failure_material_sha256"] == args["errors"]["graph"]["evidence"]["material_sha256"]
    assert "recovery_failure" not in decision
    assert args == original


@pytest.mark.parametrize("missing", [("task",), ("flow",), ("task", "flow")])
def test_missing_cfg_cannot_be_repaired_without_accepted_task_and_flow(missing):
    args = admission_material()
    args["reviewed"]["review"]["findings"] = [finding()]
    for key in missing:
        args["values"].pop(key)
    assert_barrier(args, "accepted source-only Task and flow")


@pytest.mark.parametrize("status", ["semantic_failure", "request_failure", "skipped", "partial", "failed", "interrupted"])
def test_nonstructural_graph_failure_does_not_authorize_another_sample(status):
    args = admission_material()
    args["errors"]["graph"]["status"] = status
    args["errors"]["graph"]["evidence"]["status"] = status
    args["reviewed"]["review"]["findings"] = [finding()]
    assert_barrier(args, "No source-bound terminal structural rejection")


@pytest.mark.parametrize("change", ["failure_absent", "evidence_absent", "evidence_null", "wrong_identity",
    "wrong_stage", "wrong_status", "stale_source", "stale_material", "stale_material_hash"])
def test_missing_or_stale_failure_bindings_block_recovery(change):
    args = admission_material()
    failure = args["errors"]["graph"]
    evidence = failure["evidence"]
    if change == "failure_absent":
        args["errors"].clear()
    elif change == "evidence_absent":
        failure.pop("evidence")
    elif change == "evidence_null":
        failure["evidence"] = None
    elif change == "wrong_identity":
        evidence["identity"] = "invented-material"
    elif change == "wrong_stage":
        evidence["stage"] = "processing"
    elif change == "wrong_status":
        evidence["status"] = "semantic_failure"
    elif change == "stale_source":
        args["files"]["skill/SKILL.md"] += "An independent source change.\n"
    elif change == "stale_material":
        evidence["material"]["response"] = {"changed": True}
    else:
        evidence["material_sha256"] = "0" * 64
    assert_barrier(args, "No source-bound terminal structural rejection")


@pytest.mark.parametrize("change", ["accepted_candidate", "no_attempt", "semantic_terminal", "empty_diagnostics"])
def test_rehashed_material_still_needs_an_unaccepted_terminal_structural_rejection(change):
    args = admission_material()
    material = args["errors"]["graph"]["evidence"]["material"]
    if change == "accepted_candidate":
        material["accepted"] = True
    elif change == "no_attempt":
        material["attempts"] = []
    elif change == "semantic_terminal":
        material["validation"]["status"] = "semantic_failure"
    else:
        material["validation"]["diagnostics"] = []
    rebind_material(args)
    assert_barrier(args, "No source-bound terminal structural rejection")


@pytest.mark.parametrize("change", ["validation_null", "validation_list", "attempts_string", "attempts_object",
    "attempts_nonrecord", "diagnostics_string", "diagnostics_object", "diagnostics_nonrecord",
    "terminal_status_mismatch", "terminal_validation_mismatch", "terminal_validation_digest_mismatch"])
def test_malformed_rehashed_failure_material_is_a_conservative_admission_barrier(change):
    args = admission_material()
    material = args["errors"]["graph"]["evidence"]["material"]
    if change == "validation_null":
        material["validation"] = None
    elif change == "validation_list":
        material["validation"] = [material["validation"]]
    elif change == "attempts_string":
        material["attempts"] = "present"
    elif change == "attempts_object":
        material["attempts"] = {"present": True}
    elif change == "attempts_nonrecord":
        material["attempts"] = ["present"]
    elif change == "diagnostics_string":
        material["validation"]["diagnostics"] = "structural failure"
    elif change == "diagnostics_object":
        material["validation"]["diagnostics"] = {"code": "structural failure"}
    elif change == "diagnostics_nonrecord":
        material["validation"]["diagnostics"] = ["structural failure"]
    elif change == "terminal_status_mismatch":
        material["attempts"][-1]["status"] = "validated"
    elif change == "terminal_validation_mismatch":
        material["attempts"][-1]["validation"]["diagnostics"][0]["path"] = "/different/current/candidate"
        material["attempts"][-1]["validation_sha256"] = canonical_sha256(material["attempts"][-1]["validation"])
    else:
        material["attempts"][-1]["validation_sha256"] = "0" * 64
    rebind_material(args)
    assert_barrier(args, "No source-bound terminal structural rejection")


@pytest.mark.parametrize("status", ["request_failure", "semantic_failure", "structural_failure", "interrupted", "not_run"])
def test_unavailable_review_blocks_recovery_even_with_bound_failure_and_prior_findings(status):
    args = admission_material()
    args["reviewed"] = {"status": status, "review": {"findings": [finding()]}}
    assert_barrier(args, "No completed or locally retained source review")


def test_locally_retained_task_findings_join_required_cfg_recovery_without_becoming_cfg_findings():
    args = admission_material()
    args["reviewed"] = {"status": "partial", "review": {"findings": [finding("task") for _ in range(5)]}}
    decision = repair_decision(**args)
    assert decision["eligible"] and decision["domains"] == ["cfg", "task"]
    assert decision["finding_count"] == 5 and decision["review_status"] == "partial"
    assert {row["domain"] for row in args["reviewed"]["review"]["findings"]} == {"task"}


@pytest.mark.parametrize("status", ["complete", "partial"])
@pytest.mark.parametrize("domain,owner", [("cfg", None), ("task", None), ("annotation", "processing"),
    ("annotation", "task-correspondence"), ("annotation", "sensitivity")])
def test_ordinary_original_bundle_retains_existing_reviewed_repair_behavior(status, domain, owner):
    args = admission_material()
    args["values"].update({name: {"value": "accepted original " + name} for name in
                           ["graph", "processing", "task-correspondence", "sensitivity", "annotation"]})
    args["errors"] = {}
    args["selected"] = "synthetic-original-annotation"
    args["reviewed"] = {"status": status, "review": {"findings": [finding(domain, owner)]}}
    decision = repair_decision(**args)
    assert decision["eligible"] and decision["mode"] == "reviewed_bundle"
    assert decision["domains"] == [domain] and decision["budget_rounds"] == 1
    assert "recovery_failure" not in decision and decision["barriers"] == []


def test_complete_original_bundle_with_no_findings_does_not_spend_shared_round():
    args = admission_material()
    args["values"]["graph"] = {"value": "accepted graph"}
    args["selected"] = "synthetic-original-annotation"
    decision = repair_decision(**args)
    assert decision["eligible"] is False and decision["mode"] == "not_admitted"
    assert "recovery_failure" not in decision


@pytest.mark.parametrize("domain,owner", [("cfg", None), ("task", None), ("annotation", "sensitivity")])
def test_available_upstream_and_partial_fragment_review_keep_prior_admission_without_selected_bundle(domain, owner):
    args = admission_material()
    args["values"].update(graph={"value": "accepted graph"}, processing={"value": "partial processing"})
    args["errors"] = {}
    args["reviewed"] = {"status": "partial", "review": {"findings": [finding(domain, owner)]}}
    decision = repair_decision(**args)
    assert decision["eligible"] and decision["mode"] == "reviewed_bundle"
    assert decision["domains"] == [domain] and "recovery_failure" not in decision
