"""Local uncertainty preserves only the reviewed information and output scope."""
from copy import deepcopy

import pytest

from skillflow.doe.input_contract_review import input_contract_review_inventory
from skillflow.propagation.contracts.joint import joint_source_files
from tests.doe.input_review_helpers import checks_for_inventory
from tests.doe.test_input_contract_scopes import sealed
from tests.doe.test_reviewed_input_necessity import (
    fixture, compute, rule, row, inp, evidence, solve, operation_key, assessed,
)


def gap():
    return {"code": "ambiguous_semantics",
        "reason": "The source does not specify whether the secondary member count appears in the result.",
        "missing": "Whether the secondary collection's count is included in the output label.",
        "resolution": "Specify whether the label includes the secondary collection count.",
        "evidences": [evidence()]}


def custom_receipt(values, select_kind, status="unresolved"):
    facts, _, annotation, _ = values
    files = joint_source_files(annotation["material"])
    inventory = input_contract_review_inventory(cfg=facts.cfg, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    checks = checks_for_inventory(inventory, [evidence()])
    scopes = inventory["contracts"][0]["scopes"]
    chosen = [s["id"] for s in scopes if select_kind(s)]
    assert chosen
    checks[0].update(status=status, scope_checks=[
        {"scope_ids": chosen, "status": status, "reason": gap()["reason"], "evidences": [evidence()],
         **({"gap": gap()} if status == "unresolved" else {}), "affected_scope_ids": []},
        {"scope_ids": [s["id"] for s in scopes if s["id"] not in chosen], "status": "accepted",
         "reason": "The other output and input relations are independently supported.", "evidences": [evidence()]},
    ])
    return sealed((files, facts.cfg, annotation, inventory), checks)


def test_required_x_uncertain_y_and_independent_z_share_one_real_input():
    r = {**row(0, ["x"]), "unresolved_ranges": [
        {"information": {"property": "value", "path": ["y"]}, "gap": gap()}]}
    values = fixture([compute([inp()], [rule([], [r])])], mode="model")
    before = deepcopy((values[0].data, values[0].records, values[0].sinks))
    engine, result = solve(values)
    key = operation_key(engine)
    ranges = assessed(result, key, 0)["ranges"]
    assert any(r["status"] == "required" and r["path"] == ["x"] for r in ranges)
    assert any(r["status"] == "unresolved" and r["path"] == ["y"] for r in ranges)
    assert any(r["status"] == "deletable" and sorted(r["excluded_paths"]) == [["x"], ["y"]] for r in ranges)
    assert engine.contracts.influenced_outputs(key, 0, ["z"]) == []
    assert (values[0].data, values[0].records, values[0].sinks) == before


@pytest.mark.parametrize("property,path", [("cardinality", ["rows"]), ("presence", ["rows", {"kind": "each"}])])
def test_reviewed_structural_uncertainty_does_not_retain_member_payload(property, path):
    r = {**row(0), "unresolved_ranges": [{"information": {"property": property, "path": path}, "gap": gap()}]}
    values = fixture([compute([inp()], [rule([], [r])])])
    engine, result = solve(values)
    key = operation_key(engine)
    from skillflow.doe.sensitivity_engine import demand_overlap
    scoped = [d for d in result["derivations"].values() if d["node"]["operation_id"] == key
              and d["node"]["kind"] == "op_input"]
    assert scoped and all(d["conservative"] and d["information_bound"] for d in scoped)
    payload = {"property": "value", "path": ["rows", {"kind": "each"}, "payload"], "excluded_paths": []}
    member = {"property": "value", "path": ["rows", {"kind": "each"}], "excluded_paths": []}
    assert all(demand_overlap(payload, d) == "none" for d in scoped)
    assert any(demand_overlap(member, d) != "none" for d in scoped)
    assert engine.contracts.influenced_outputs(key, 0, payload["path"]) == []
    assert engine.contracts.influenced_outputs(key, 0, member["path"]) != []
    ancestors = [d for d in result["derivations"].values() if d["node"]["kind"] == "ir_input"
                 and d["node"]["instruction_id"] == "ir_filter"]
    assert any(d.get("information_bound") for d in ancestors)


def test_generic_conservatism_does_not_gain_a_reviewed_information_bound():
    from skillflow.doe.sensitivity_engine import demand_overlap
    signal = {"property": "value", "path": ["rows", 0, "payload"], "excluded_paths": []}
    demand = {"property": "cardinality", "path": ["rows"], "each": False,
              "excluded_paths": [], "conservative": True}
    assert demand_overlap(signal, demand) == "retain"


@pytest.mark.parametrize("status", ["rejected", "unresolved"])
@pytest.mark.parametrize("kind", ["required", "unresolved_range"])
@pytest.mark.parametrize("property,path", [("cardinality", ["rows"]), ("presence", ["rows", {"kind": "each"}])])
def test_nonaccepted_structural_scope_does_not_certify_payload_independence(status, kind, property, path):
    information = {"property": property, "path": path}
    input_row = {**row(0), **({"required": [information]} if kind == "required" else
        {"unresolved_ranges": [{"information": information, "gap": gap()}]})}
    values = fixture([compute([inp()], [rule([], [input_row])])])
    review = custom_receipt(values, lambda scope: scope["kind"] == kind, status=status)
    engine, result = solve(values, review=review)
    operation = operation_key(engine)
    payload = {"property": "value", "path": ["rows", {"kind": "each"}, "payload"], "excluded_paths": []}
    from skillflow.doe.sensitivity_engine import demand_overlap
    scopes = [d for d in result["derivations"].values() if d["node"]["kind"] == "op_input"
              and d["node"]["operation_id"] == operation]
    assert scopes and all(d["conservative"] and not d.get("information_bound", False) for d in scopes)
    assert any(demand_overlap(payload, demand) == "retain" for demand in scopes)
    # Forward preservation cannot use an unaccepted structural selector as an
    # upper bound when backward necessity correctly keeps it conservative.
    assert engine.contracts.influenced_outputs(operation, 0, payload["path"]) != []


def test_wide_review_gap_does_not_create_unjustified_input_retention():
    values = fixture([compute([inp()], [rule([], [row(0, ["x"])])])])
    review = custom_receipt(values, lambda s: s["kind"] == "rule")
    engine, result = solve(values, review=review)
    ranges = assessed(result, operation_key(engine), 0)["ranges"]
    assert any(d["code"] == "input_contract_review_gap" for d in result["diagnostics"])
    assert any(r["status"] == "required" and r["path"] == ["x"] for r in ranges)
    assert any(r["status"] == "deletable" and r["excluded_paths"] == [["x"]] for r in ranges)
    assert not any(r["status"] == "unresolved" for r in ranges)


def test_uncertain_output_rule_does_not_widen_independent_output_change():
    rules = [rule(["x"], [row(0, ["a"])]), rule(["z"], [row(0, ["b"])])]
    values = fixture([compute([inp()], rules, output_parts=[r["output"] for r in rules])])
    review = custom_receipt(values, lambda s: s["kind"] == "required" and s["output"]["path"] == ["x"])
    engine, result = solve(values, path=["z"], review=review)
    assert not any(d["code"] == "input_contract_review_gap" for d in result["diagnostics"])
    key = operation_key(engine)
    assert engine.contracts.influenced_outputs(key, 0, ["a"]) == [{"property": "value", "path": ["x"]}]


def test_rejected_output_decomposition_cannot_certify_output_independence():
    rules = [rule(["x"], [row(0, ["a"])])]
    values = fixture([compute([inp()], rules, output_parts=[r["output"] for r in rules])])
    review = custom_receipt(values, lambda s: s["kind"] == "output_parts", status="rejected")
    engine, _ = solve(values, path=["x"], review=review)
    assert engine.contracts.influenced_outputs(operation_key(engine), 0, ["unlisted"]) is None


def test_distinct_missing_attachments_keep_their_own_evidence_reason():
    from tests.doe.test_reviewed_input_necessity import local
    values = fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "first"},
        {"op": "compute", "inputs": [local("first")], "dependencies": ["possible"], "output": "answer"},
    ])
    facts, _, annotation, _ = values
    inventory = input_contract_review_inventory(cfg=facts.cfg, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    checks = checks_for_inventory(inventory, [evidence()])
    assert len(checks) == 2 and all(c["contract_id"] is None for c in checks)
    for i, check in enumerate(checks):
        check["reason"] = f"Operation {i} lacks its separately required output dependency contract."
    review = sealed((joint_source_files(annotation["material"]), facts.cfg, annotation, inventory), checks)
    engine, result = solve(values, review=review)
    reasons = [d["reason"] for d in result["diagnostics"] if d["code"] == "input_contract_rejected"]
    assert all(any(c["reason"] in reason for reason in reasons) for c in checks)
