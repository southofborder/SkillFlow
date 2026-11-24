"""Source-review findings retain independent argument, response, and receiver ranges."""
import json
from pathlib import Path

import pytest

from skillflow.document_guided.sensitivity_entries import ingress_gap_rechecks
from skillflow.document_guided.source_review import isolate_source_review
from skillflow.doe.constraint_preservation import ForwardInfluence
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.input_contract_review import checked_input_contract_review, check_contract_finding_consistency
from skillflow.doe.review_ranges import FindingRanges, overlap_information
from tests.document_guided.test_source_review_locality import two_operations, partial_receipt
from tests.doe.input_review_helpers import source_review_response, checks_for_inventory
from tests.doe.test_demand_engine import candidate, evidence
from tests.doe.test_reviewed_input_necessity import assessed


def defect(target, role, path, *, slot=None):
    ref = {k: v for k, v in evidence().items() if k != "reason"}
    return {"domain": "annotation", "owner": "processing", "target_ids": [target],
        "source_refs": [ref], "explanation": "The selected operation lacks the cited field relation.",
        "suggestion": "Rebind the selected field to the source operation.",
        "affected_ranges": [{"operation": target, "role": role, "information": {"property": "value", "path": path},
                             **({"input_index": slot} if slot is not None else {})}]}


def test_narrow_review_conflict_isolated_through_seal_demand_and_deletion():
    values, material, operations = two_operations()
    facts, task, annotation, targets = values
    target = "annotation:" + operations[0]["pointer"]
    answer = source_review_response(material, [defect(target, "argument", ["token"], slot=0)])
    answer["input_contract_checks"] = checks_for_inventory(material["input_contract_inventory"], [evidence()])
    evaluated = isolate_source_review(answer, material)
    ledger = evaluated["validation"]
    assert not ledger["blocked_obligation_ids"]
    assert len(ledger["conflicts"]) == 1 and len(ledger["conflicts"][0]["scope_ids"]) == 1
    barrier, = ledger["validation_barriers"]
    assert barrier["range"] == {"role": "argument", "input_index": 0, "information": {"property": "value", "path": ["token"]}}
    receipt = partial_receipt(values, material, evaluated)
    assert checked_input_contract_review(receipt, files=material["files"], cfg=facts.cfg, annotation=annotation) == receipt
    requested = candidate(targets)
    result = prepare_demand_review(facts, task, annotation, requested, input_contract_review=receipt).to_dict()
    engine = DemandEngine(facts, task, annotation, requested, targets, input_contract_review=receipt)
    key = next(k for k, v in engine.ops.items() if v["spec"].get("output") == "unused")
    ranges = assessed(result, key, 0)["ranges"]
    assert any(r["status"] == "unresolved" and r["path"] == ["token"] for r in ranges)
    assert any(r["status"] == "deletable" and (r["path"] == ["body"] or r["excluded_paths"] == [["token"]]) for r in ranges)
    forward = ForwardInfluence(engine)
    assert forward.run(key, 0, ["token"])["review_validation_barriers"] == [barrier["id"]]
    assert not forward.run(key, 0, ["body"])["review_validation_barriers"]


def test_real_ga4_zero_argument_interface_and_internal_ingress_have_distinct_subjects():
    sample = json.loads((Path(__file__).parents[1] / "fixtures/ga4_entry_occurrences/review-ranges.json").read_bytes())
    assert len(sample["overlaps"]) == 132 and len({x[0] for x in sample["overlaps"]}) == 55
    for record in sample["affected"]:
        ir = record["ir"]
        index = [{"id": "annotation:/ir_semantics/" + ir}]
        limitation, = ingress_gap_rechecks({"sensitivity_entry_gaps": [record["gap"]], "target_index": index}, bind=True)
        assert limitation["source_refs"] and limitation["sensitivity_entry_gap_id"]
        # The accepted payload judgments here are actual saved obligations,
        # including the separate zero-operand deliver, paired receive and log.
        obligations = record["obligations"]
        inv = {"obligations": obligations, "contracts": [{"obligation_id": row["id"],
            "scopes": [{"id": "interface", "kind": "interface"}]} for row in obligations]}
        matcher = FindingRanges(inv, record["targets"], {}, None, {})
        for row in obligations:
            check = {"obligation_id": row["id"], "status": "accepted", "scope_checks": []}
            with pytest.raises(ValueError, match="conflicts"):
                check_contract_finding_consistency([check], [limitation], record["targets"])
            assert matcher.conflicts(check, limitation) == []
        if ir == "ir_093":
            assert sorted(r["input_count"] for r in obligations) == [0, 0, 1]
            assert {r["location_id"] for r in obligations} == {"rt_events_function", "console"}


def test_response_claim_preserves_independent_action_inputs_and_rejects_bad_argument_locator():
    values, material, operations = two_operations()
    target = "annotation:" + operations[0]["pointer"]
    proposed = source_review_response(material, [defect(target, "response", ["rows"])])
    result = isolate_source_review(proposed, material)
    barrier, = result["validation"]["validation_barriers"]
    assert barrier["range"]["role"] == "response"
    assert not result["validation"]["blocked_obligation_ids"]
    proposed["findings"] = [defect(target, "argument", [], slot=47)]
    bad = isolate_source_review(proposed, material)
    assert any("outside" in d["message"] for d in bad["validation"]["diagnostics"])
    assert not any(f.get("affected_ranges") for f in bad["review"]["findings"])


def test_receiver_and_response_resolve_only_the_exact_call_and_interface_field_is_program_owned():
    from skillflow.doe.input_contract_review import contract_review_targets, input_contract_review_inventory
    from skillflow.propagation.annotation.binding_examples import inp, evidence as interface_evidence
    from tests.doe.test_sink_payload_seeds import synthetic_fixture
    contract = {"inputs": [{"input_index": 0, "required": [{"property": "value", "path": ["fields"]}],
        "remainder": "independent", "reason": "The request requires the fields selector."}],
        "reason": "The selected interface requires this query selector.", "evidences": [interface_evidence()]}
    operations = [{"op": "deliver", "target": "label_receiver", "inputs": [inp()], "request_id": "query",
                   "input_contract": contract},
                  {"op": "receive", "location": "label_receiver", "inputs": [inp()], "request_id": "query",
                   "output": "receipt", "input_contract": contract},
                  {"op": "deliver", "target": "label_receiver", "inputs": [inp()], "input_contract": contract}]
    _, _, facts = synthetic_fixture(operations, output="receipt", return_demand=True)
    a = facts.annotation
    inventory = input_contract_review_inventory(cfg=facts.cfg, raw_annotation=a["raw_annotation"],
        mapping=a["mapping"], compiled=a["compiled_annotation"])
    targets = contract_review_targets(contracts=inventory["obligations"], cfg=facts.cfg, mapping=a["mapping"])
    matcher = FindingRanges(inventory, targets, facts.cfg, a["raw_annotation"], a["mapping"])
    request = next(o for o in inventory["obligations"] if o.get("request_id") and o["operation"] == "deliver")
    response = next(o for o in inventory["obligations"] if o["operation"] == "receive")
    target = "annotation:" + request["raw_pointer"].rsplit("/", 1)[0]
    locations = {tuple(ref["raw_path"]) for ref, _ in matcher.resolve(defect(target, "receiver", []))}
    assert locations == {tuple(o["raw_path"]) for o in (request, response)}
    assert [ref["raw_path"] for ref, _ in matcher.resolve(defect(target, "response", ["rows"]))] == [response["raw_path"]]
    finding = defect(target, "argument", [], slot=0)
    del finding["affected_ranges"]
    finding["target_ids"] = [target + "/input_contract/inputs/0/required/0"]
    [(ref, affected)] = matcher.resolve(finding)
    assert ref["raw_path"] == request["raw_path"]
    assert affected == {"role": "argument", "input_index": 0, "information": {"property": "value", "path": ["fields"]}}
    assert not overlap_information({"property": "presence", "path": ["record"]},
                                   {"property": "value", "path": ["record", "fields"]})


def test_doe_does_not_publish_deletion_on_a_disputed_field_and_retains_sibling_reduction():
    from skillflow.doe.sensitivity_material import prepare_sensitivity_review, validate_sensitivity_result
    from tests.document_guided.test_source_review_locality import review_material
    from tests.doe.test_input_contract_preservation import reviewed_fixture
    from tests.doe.test_sensitivity_engine import declarations, rows

    values, _, request, _ = reviewed_fixture([{"property": "value", "path": ["body"]}])
    facts, task, annotation, targets = values
    material = review_material(values)
    op = next(t for t in targets.values() if t.get("kind") == "operation" and t["value"]["op"] == "compute")
    target = "annotation:" + op["pointer"]
    answer = source_review_response(material, [defect(target, "argument", ["y"], slot=0)])
    answer["input_contract_checks"] = checks_for_inventory(material["input_contract_inventory"], [evidence()])
    sealed = partial_receipt(values, material, isolate_source_review(answer, material))
    for path, allowed in ((["y"], False), (["token"], True)):
        sensitive = declarations(path)
        review = prepare_sensitivity_review(facts, task, annotation, request, sensitive, input_contract_review=sealed)
        result = review.to_dict()
        comparisons = rows(result)
        assert comparisons
        assert all((r["conclusion"] == "excess_supported") == allowed for r in comparisons)
        assert all(not r["limitations"] if allowed else r["limitations"] for r in comparisons)
        assert validate_sensitivity_result(result, facts, task, annotation, request, sensitive,
            demand_result=review.demand_dict(), input_contract_review=sealed) == result


def test_missing_source_only_limits_fields_carried_from_that_occurrence():
    from tests.doe.test_sensitivity_engine import independent_reads_and_receivers, declarations
    from skillflow.doe.sensitivity_material import prepare_sensitivity_review, validate_sensitivity_result

    facts, task, annotation, targets = independent_reads_and_receivers()
    annotation["mapping"]["sensitivity_entry_gaps"] = [{"instruction_id": "ir_read", "missing_from": "processing",
        "missing_entry": "The source behind the first read", "reason": "The adapter returns a cached record.",
        "evidences": [evidence()]}]
    request = candidate(targets)
    sensitive = declarations()
    review = prepare_sensitivity_review(facts, task, annotation, request, sensitive)
    result = review.to_dict()
    by_endpoint = {s["boundary"]["target"]: s for s in result["sinks"] if s["boundary"]["sink_type"] == "external_tool"}
    ref = next(r["id"] for r in result["diagnostics"] if r["code"] == "missing_sensitivity_ingress")
    from skillflow.doe.sensitivity_results import resolve_data_review
    def comparisons(endpoint):
        sink = by_endpoint[endpoint]
        return [resolve_data_review(r, sink, result["derivations"]["sensitivity"]) for r in sink["data_reviews"]]
    first = comparisons("first_receiver")
    second = comparisons("second_receiver")
    assert first and second
    assert all(ref in r["limitations"] for r in first)
    assert all(ref not in r["limitations"] for r in second)
    mixed = {tuple(r["path"]): r for r in comparisons("pair_receiver")}
    assert ref in mixed["selected", "token"]["limitations"]
    assert ref not in mixed["other", "token"]["limitations"]
    assert validate_sensitivity_result(result, facts, task, annotation, request, sensitive,
        demand_result=review.demand_dict()) == result
