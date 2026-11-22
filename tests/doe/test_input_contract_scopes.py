"""Finite local review decisions are complete, evidence-bound and independent."""
from copy import deepcopy
import json

import pytest

from skillflow.doe.input_contract_review import (
    build_input_contract_review, checked_contract_checks, checked_input_contract_review,
    checked_projection_checks, compact_review_inventory, input_contract_binding,
    input_contract_review_inventory, reviewed_contract_scopes, reviewed_acquisition_projections,
    SOURCE_REVIEW_VERSION,
    check_contract_finding_consistency,
)
from skillflow.document_guided.source_review import build_source_review_prompt
from skillflow.propagation.contracts.joint import joint_source_files
from tests.doe.input_review_helpers import checks_for_inventory, projection_checks
from tests.doe.test_demand_engine import fixture, inp, evidence
from tests.doe.test_reviewed_input_necessity import compute, rule, row


def materials(operation=None):
    operation = operation or compute([inp()], [rule([], [row(0, ["body"])])])
    facts, _, annotation, _ = fixture([operation])
    files = joint_source_files(annotation["material"])
    inventory = input_contract_review_inventory(cfg=facts.cfg, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    return files, facts.cfg, annotation, inventory


def sealed(values, checks=None, projections=None):
    files, cfg, annotation, inventory = values
    checks = checks if checks is not None else checks_for_inventory(inventory, [evidence()])
    response = {"schema_version": SOURCE_REVIEW_VERSION, "outcome": "completed", "findings": [],
        "input_contract_checks": checks, "input_projection_checks": projections or [], "source_input_findings": []}
    binding = input_contract_binding(files=files, cfg=cfg, task=annotation["task"],
        raw_annotation=annotation["raw_annotation"], compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    return build_input_contract_review(files=files, cfg=cfg, annotation=annotation,
        review={"status": "complete", "availability": dict.fromkeys(("task", "cfg", "annotation"), True), "review": response},
        review_material={"partial": False, "input_contract_binding": binding, "input_contract_inventory": inventory})


def local_groups(inventory):
    check = checks_for_inventory(inventory, [evidence()], status="unresolved")[0]
    scopes = inventory["contracts"][0]["scopes"]
    uncertain = next(scope["id"] for scope in scopes if scope["kind"] == "remainder")
    group = check["scope_checks"][0]
    group["scope_ids"] = [uncertain]
    check["scope_checks"].append({"scope_ids": [scope["id"] for scope in scopes if scope["id"] != uncertain],
        "status": "accepted", "reason": "The declared body range is independently source-supported.", "evidences": [evidence()]})
    return check


def test_missing_attachment_is_an_expected_rejected_obligation_not_vacuous_acceptance():
    values = materials({"op": "compute", "inputs": [inp()], "output": "answer", "dependencies": ["possible"]})
    files, _, _, inventory = values
    assert len(inventory["obligations"]) == 1
    assert inventory["obligations"][0]["contract_id"] is None
    with pytest.raises(ValueError, match="every expected obligation"):
        checked_contract_checks([], inventory=inventory, files=files)
    check = checks_for_inventory(inventory, [evidence()])[0]
    assert check["status"] == "rejected"
    receipt = sealed(values, [check])
    assert receipt["checks"][0]["contract_id"] is None
    check.update(status="accepted", scope_checks=[])
    with pytest.raises(ValueError, match="missing.*cannot be accepted"):
        checked_contract_checks([check], inventory=inventory, files=files)


@pytest.mark.parametrize("change", ["omitted", "duplicate", "invented", "gap_missing", "resolution_missing", "generic"])
def test_nonaccepted_scope_partition_and_concrete_gap_are_mandatory(change):
    files, _, _, inventory = materials()
    check = local_groups(inventory)
    group = check["scope_checks"][0]
    if change == "omitted":
        check["scope_checks"].pop()
    elif change == "duplicate":
        group["scope_ids"].append(group["scope_ids"][0])
    elif change == "invented":
        group["scope_ids"][0] = "invented_scope"
    elif change == "gap_missing":
        group.pop("gap")
    elif change == "resolution_missing":
        group["gap"].pop("resolution")
    else:
        group["gap"]["reason"] = "The computation is opaque"
    with pytest.raises(ValueError):
        checked_contract_checks([check], inventory=inventory, files=files)


def test_local_review_gap_keeps_independently_accepted_required_range():
    values = materials()
    check = local_groups(values[-1])
    receipt = sealed(values, [check])
    view = reviewed_contract_scopes(receipt, check["contract_id"])
    assert view["available"] and view["rules"][0]["decision"]["status"] == "accepted"
    input_row = view["rules"][0]["inputs"][0]
    assert input_row["required"][0]["decision"]["status"] == "accepted"
    assert input_row["remainder"]["decision"]["status"] == "unresolved"
    assert input_row["remainder"]["decision"]["gap"]["resolution"]
    assert checked_input_contract_review(receipt, files=values[0], cfg=values[1], annotation=values[2]) == receipt


def test_conflicting_assertions_can_share_one_physical_source_span():
    files, _, _, inventory = materials()
    check = local_groups(inventory)
    check["scope_checks"][0]["gap"].update(code="conflicting_evidence",
        reason="The cited source statements require both keeping and discarding the secondary label.",
        missing="The precedence between the two opposing label-handling obligations.",
        resolution="Resolve whether the secondary label must be retained or discarded.")
    checked_contract_checks([check], inventory=inventory, files=files)


def test_wide_barrier_must_name_only_explicitly_nonaccepted_actual_input_scopes():
    files, _, _, inventory = materials()
    check = local_groups(inventory)
    scopes = inventory["contracts"][0]["scopes"]
    wide = next(scope["id"] for scope in scopes if scope["kind"] == "rule")
    check["scope_checks"][1]["scope_ids"].remove(wide)
    check["scope_checks"][0]["scope_ids"].append(wide)
    # The group also contains the input remainder, so a shared affected list
    # cannot masquerade as a wide-only relation.
    check["scope_checks"][0]["affected_scope_ids"] = [check["scope_checks"][1]["scope_ids"][0]]
    with pytest.raises(ValueError, match="affected|barriers"):
        checked_contract_checks([check], inventory=inventory, files=files)


def test_if_present_descriptor_exposes_existing_presence_semantics_without_extra_claim():
    operation = compute([inp()], [rule([], [{**row(0), "required": [
        {"property": "value", "path": ["optional"], "if_present": True}]}])])
    values = materials(operation)
    inventory = values[-1]
    compact = compact_review_inventory(inventory, {o["id"]: "annotation:/actual" for o in inventory["obligations"]})
    scope = next(s for s in compact["obligations"][0]["scopes"] if s["kind"] == "required")
    assert scope["effective"] == [{"property": "presence", "path": ["optional"], "when": "always"},
                                  {"property": "value", "path": ["optional"], "when": "present"}]
    assert len([s for s in compact["obligations"][0]["scopes"] if s["kind"] == "required"]) == 1
    assert sealed(values)["source_review_complete"]


def test_explicit_unresolved_range_and_independent_remainder_have_separate_review_scopes():
    gap = checks_for_inventory(materials()[-1], [evidence()], status="unresolved")[0]["scope_checks"][0]["gap"]
    input_row = {**row(0, ["x"]), "unresolved_ranges": [{"information": {"property": "value", "path": ["y"]}, "gap": gap}]}
    values = materials(compute([inp()], [rule([], [input_row])]))
    receipt = sealed(values)
    view = reviewed_contract_scopes(receipt, receipt["checks"][0]["contract_id"])["rules"][0]["inputs"][0]
    assert view["unresolved_ranges"][0]["information"]["path"] == ["y"]
    assert view["unresolved_ranges"][0]["authored_gap"] == gap
    assert view["remainder"]["authored"]["status"] == "independent"


def test_review_prompt_explains_optional_presence_and_keeps_contract_body_once_in_inventory():
    from tests.doe.test_input_contract_review import bundle
    _, _, _, material, _ = bundle()
    prompt = build_source_review_prompt(material)
    assert "if_present already preserves presence unconditionally" in prompt
    assert "no redundant separate presence row" in prompt
    assert "qualitative duty" in prompt
    from tests.doe.input_review_helpers import review_prompt_payload
    payload = review_prompt_payload(prompt)
    assert "input_contracts" not in payload
    assert all("contract" not in row for row in payload["input_contract_inventory"]["obligations"])


def test_paired_projection_has_one_review_decision_and_exact_lookup():
    from skillflow.propagation.annotation.binding_examples import evidence as interface_evidence
    from tests.doe.test_sink_payload_seeds import synthetic_fixture
    cited = [interface_evidence()]
    capability = {"selection_input_index": 0, "selection_parameter_path": ["fields"],
        "returned_range": {"property": "value", "path": ["profile", "label"]},
        "reason": "The fields selector independently requests the profile label.", "evidences": cited}
    contract = {"inputs": [{"input_index": 0, "required": [{"property": "value", "path": ["fields"]}],
        "remainder": "independent", "reason": "Only the selection parameter is required."}],
        "reason": "The source documents the selection parameter and returned profile label.",
        "evidences": cited, "acquisition_projections": [capability]}
    _, _, facts = synthetic_fixture([
        {"op": "deliver", "target": "label_receiver", "inputs": [inp()], "request_id": "query",
         "input_contract": contract},
        {"op": "receive", "location": "label_receiver", "inputs": [inp()], "request_id": "query",
         "output": "receipt", "input_contract": contract}], output="receipt", return_demand=True,
        source="The fields request parameter independently selects profile.label from the response.")
    annotation = facts.annotation
    inventory = input_contract_review_inventory(cfg=facts.cfg, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    assert len(inventory["obligations"]) == 2 and len(inventory["projections"]) == 1
    files = joint_source_files(annotation["material"])
    checks = projection_checks(inventory, cited)
    with pytest.raises(ValueError, match="exact finite inventory"):
        checked_projection_checks(checks + checks, inventory=inventory, files=files)
    with pytest.raises(ValueError, match="exact finite inventory"):
        checked_projection_checks([], inventory=inventory, files=files)
    receipt = sealed((files, facts.cfg, annotation, inventory), checks_for_inventory(inventory, cited), checks)
    relation = inventory["projections"][0]
    request, response = relation["request"], relation["response"]
    found = reviewed_acquisition_projections(receipt, request["instruction_id"], request["raw_path"],
        response["instruction_id"], response["raw_path"])
    assert len(found) == 1 and found[0]["decision"]["status"] == "accepted"
    assert found[0]["capability"]["returned_range"]["path"] == ["profile", "label"]
    assert reviewed_acquisition_projections(receipt, request["instruction_id"], request["raw_path"],
        response["instruction_id"], response["raw_path"] + ["invented"]) == []


def test_scoped_request_repair_does_not_revoke_response_at_shared_wire_call_parent():
    check = {"obligation_id": "response", "status": "accepted", "scope_checks": []}
    generated = {"domain": "annotation", "target_ids": ["annotation:/call"],
                 "input_contract_obligation_id": "request"}
    check_contract_finding_consistency([check], [generated], {"response": ["annotation:/call"]})
    generated.pop("input_contract_obligation_id")
    with pytest.raises(ValueError, match="conflicts with a finding"):
        check_contract_finding_consistency([check], [generated], {"response": ["annotation:/call"]})
