"""Backend behavior after the immutable receipt boundary has been checked."""
from copy import deepcopy

from skillflow.doe.constraint_preservation import ForwardInfluence, ConstraintAnalysis
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.input_contract_review import reviewed_contract_scopes, reviewed_acquisition_projections
from skillflow.doe.review_barriers import ReviewValidationBarriers
from tests.doe.test_demand_engine import fixture, inp, literal, candidate
from tests.doe.test_reviewed_input_necessity import receipt, compute, rule, row, assessed


def barrier(*references, domain="operation"):
    return {"id": "review_validation_fixture", "record_path": "/source_input_findings/0",
        "code": "schema", "reason": "A missing field has an empty actual field path.",
        "resolution": "Locate the missing field within the existing actual input operand.",
        "domain": domain, "operation_refs": [
            {"instruction_id": ir, "raw_path": list(path)} for ir, path in references]}


def engine_for(values, *, requested=None):
    facts, task, annotation, targets = values
    return DemandEngine(facts, task, annotation, requested or candidate(targets), targets,
                        input_contract_review=receipt(values))


def key_for(engine, output):
    return next(key for key, info in engine.ops.items() if info["spec"].get("output") == output)


def inject_verified_core(engine, barriers, blocked=()):
    """Unit-test only the consumer, using the output of the receipt boundary.

    Receipt validation/forgery tests belong to its owner. No altered receipt is
    presented to that public verifier as though it were authentic.
    """
    core = engine.contracts.receipt["review_core"]
    core.update(status="partial", validation_barriers=deepcopy(barriers),
                blocked_obligation_ids=list(blocked), blocked_projection_ids=[])
    engine.review_validation_barriers = ReviewValidationBarriers(engine.contracts.receipt)
    engine.contracts.scopes = {entry["id"]: reviewed_contract_scopes(engine.contracts.receipt, entry["id"])
                              for entry in engine.contracts.entries.values()}


def at(engine, key):
    info = engine.ops[key]
    return info["position"]["instruction_id"], info["raw_op"]


def deterministic_values():
    return fixture([
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "ignored"},
        {"op": "select_part", "input": inp(), "path": ["token"], "output": "answer"}])


def test_barrier_index_preserves_exact_pair_occurrences_and_global_scope():
    local = barrier(("ir", ["events", 0]), ("ir", ["events", 1]))
    index = ReviewValidationBarriers({"review_core": {"validation_barriers": [local]}})
    assert index.for_operation("ir", ["events", 0]) == [local]
    assert index.for_operation("ir", ["events", 1]) == [local]
    assert index.for_operation("other", ["events", 0]) == []
    assert index.for_operation("ir", ["events", 2]) == []
    found = index.for_operation("ir", ["events", 0])
    found[0]["reason"] = "Mutation"
    assert index.for_operation("ir", ["events", 0])[0]["reason"] != "Mutation"
    global_barrier = barrier(domain="all_operations")
    assert ReviewValidationBarriers({"review_core": {"validation_barriers": [global_barrier]}}).for_operation(
        "unlisted_ir", ["events", 8]) == [global_barrier]


def test_partial_contract_scope_stays_usable_only_with_complete_own_coverage():
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    engine = engine_for(values)
    entry = next(iter(engine.contracts.entries.values()))
    inject_verified_core(engine, [])
    assert engine.contracts.accepted(entry)
    core = engine.contracts.receipt["review_core"]
    scope_id = core["inventory"]["contracts"][0]["scopes"][0]["id"]
    core["scope_decisions"].pop(scope_id)
    assert not reviewed_contract_scopes(engine.contracts.receipt, entry["id"])["available"]


def test_partial_contract_blocked_obligation_is_unavailable():
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    engine = engine_for(values)
    entry = next(iter(engine.contracts.entries.values()))
    obligation = engine.contracts.receipt["review_core"]["inventory"]["obligations"][0]["id"]
    inject_verified_core(engine, [], [obligation])
    assert not engine.contracts.accepted(entry)


def test_partial_projection_requires_exact_pair_and_is_not_usable_when_blocked():
    request = {"instruction_id": "ir", "raw_path": ["events", 0]}
    response = {"instruction_id": "ir", "raw_path": ["events", 1]}
    projection = {"id": "projection", "scope_id": "projection", "request": request, "response": response}
    core = {"status": "partial", "inventory": {"projections": [projection]},
        "projection_decisions": {"projection": {"status": "accepted"}}, "blocked_projection_ids": []}
    receipt_value = {"review_core": core}
    assert len(reviewed_acquisition_projections(receipt_value, "ir", ["events", 0], "ir", ["events", 1])) == 1
    assert reviewed_acquisition_projections(receipt_value, "ir", ["events", 1], "ir", ["events", 0]) == []
    core["blocked_projection_ids"] = ["projection"]
    assert reviewed_acquisition_projections(receipt_value, "ir", ["events", 0], "ir", ["events", 1]) == []


def test_zero_demand_invalid_deterministic_use_is_unresolved_without_new_seed():
    values = deterministic_values()
    requested = candidate(values[3]); requested["goals"] = []
    engine = engine_for(values, requested=requested)
    blocked = key_for(engine, "ignored"); other = key_for(engine, "answer")
    inject_verified_core(engine, [barrier(at(engine, blocked))])
    before = deepcopy((values[0].records, values[0].data, values[2]["raw_annotation"]))
    result = engine.solve()
    assert result["derivations"] == {}
    assert not any(item["origin"] == "source_review" for item in result["input_findings"])
    assert not any(item["kind"] in {"missing_input", "wrong_input"} for item in result["input_findings"])
    assert all(item["status"] == "unresolved" for item in assessed(result, blocked, 0)["ranges"])
    other_refs = {identity for item in assessed(result, other, 0)["ranges"] for identity in item["diagnostic_refs"]}
    assert not any(item["id"] in other_refs and item["code"] == "input_contract_review_validation"
                   for item in result["diagnostics"])
    operand = next(item for item in result["input_assessments"] if item["node_kind"] == "ir_input"
                   and item["instruction_id"] == "ir_filter" and item["input_index"] == 0)
    assert all(item["status"] != "deletable" for item in operand["ranges"])
    assert any("/source_input_findings/0" in item["reason"] for item in result["diagnostics"])
    assert before == (values[0].records, values[0].data, values[2]["raw_annotation"])


def test_unused_blocked_operation_does_not_taint_a_different_use_in_same_ir():
    values = deterministic_values()
    engine = engine_for(values)
    blocked = key_for(engine, "ignored"); other = key_for(engine, "answer")
    inject_verified_core(engine, [barrier(at(engine, blocked))])
    result = engine.solve()
    assert all(item["status"] == "unresolved" for item in assessed(result, blocked, 0)["ranges"])
    assert any(item["status"] == "required" for item in assessed(result, other, 0)["ranges"])
    assert any(item["status"] == "deletable" for item in assessed(result, other, 0)["ranges"])


def test_native_output_barrier_retains_all_actual_input_fields_fifo_lifo():
    values = deterministic_values()
    results = []
    for order in ("fifo", "lifo"):
        engine = engine_for(values)
        blocked = key_for(engine, "answer")
        inject_verified_core(engine, [barrier(at(engine, blocked))])
        result = engine.solve(queue_order=order)
        result_rows = assessed(result, blocked, 0)["ranges"]
        assert any(item["status"] == "unresolved" and item["path"] == [] for item in result_rows)
        assert not any(item["status"] == "deletable" for item in result_rows)
        results.append(result)
    assert results[0] == results[1]


def test_contract_independence_cannot_clear_an_operation_validation_barrier():
    values = fixture([compute([inp(), literal({"extra": 3})],
        [rule([], [row(0, ["body"]), row(1)])])])
    engine = engine_for(values); blocked = key_for(engine, "answer")
    assert engine.contracts.influenced_outputs(blocked, 1, ["extra"]) == []
    inject_verified_core(engine, [barrier(at(engine, blocked))])
    assert engine.contracts.influenced_outputs(blocked, 1, ["extra"]) is None
    result = engine.solve()
    assert all(item["status"] != "deletable" for item in assessed(result, blocked, 1)["ranges"])


def test_deterministic_deletion_influence_uses_same_operation_barrier():
    values = deterministic_values()
    engine = engine_for(values); blocked = key_for(engine, "answer")
    initial = ForwardInfluence(engine).run(blocked, 0, ["unselected"])
    assert initial["complete"]
    inject_verified_core(engine, [barrier(at(engine, blocked))])
    forward = ForwardInfluence(engine)
    changed = forward.run(blocked, 0, ["unselected"])
    assert not changed["complete"]
    assert changed["review_validation_barriers"] == ["review_validation_fixture"]
    assert any("/source_input_findings/0" in reason for reason in changed["limitations"])
    assert any(row["rule"] == "review_validation_barrier" for row in changed["steps"].values())


def test_unlocatable_barrier_protects_all_processed_input_uses_without_seeds():
    values = deterministic_values()
    requested = candidate(values[3]); requested["goals"] = []
    engine = engine_for(values, requested=requested)
    inject_verified_core(engine, [barrier(domain="all_operations")])
    result = engine.solve()
    assert not result["derivations"]
    assert all(not any(row["status"] == "deletable" for row in item["ranges"])
               for item in result["input_assessments"] if item["coverage"] == "processed")


def test_structural_constraint_shortcut_does_not_clear_unvalidated_native_behavior():
    def attach(prepared, raw, evidence):
        raw["realizations"][0]["constraints"] = [{
            "kind": "at_most", "scope": {"kind": "task"},
            "events": [{"instruction_id": "ir_filter", "path": []}], "limit": 1, "unit": "attempt"}]
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "answer"}],
                     custom=attach)
    engine = engine_for(values); blocked = key_for(engine, "answer")
    data_id = engine.ops[blocked]["record"]["inputs"][0][0]
    before = ConstraintAnalysis(engine)
    assert before.evaluate(blocked, 0, data_id, ["unselected"])[1]
    inject_verified_core(engine, [barrier(at(engine, blocked))])
    after = ConstraintAnalysis(engine)
    refs, preserved = after.evaluate(blocked, 0, data_id, ["unselected"])
    assert refs and not preserved
    assert all("/source_input_findings/0" in after.preservation[ref]["reason"] for ref in refs)


def test_public_partial_review_demand_and_doe_preserve_local_barriers_and_actual_observations():
    from skillflow.document_guided.source_review import isolate_source_review
    from skillflow.doe.demand_material import prepare_demand_review
    from skillflow.doe.input_assessments import InputReviewBarrierIndex
    from skillflow.doe.review_barriers import barrier_diagnostic_value
    from skillflow.doe.sensitivity_material import prepare_sensitivity_review
    from skillflow.doe.sensitivity_report import render_html, render_markdown
    from tests.document_guided.test_source_review_locality import (
        review_material, candidate_with_errors, partial_receipt,
    )

    values = fixture([
        {"op": "select_part", "input": inp(), "path": ["token"], "output": "unused"},
        compute([inp(), literal({"extra": 3})], [rule([], [row(0, ["body"]), row(1)])])], mode="model")
    facts, task, annotation, targets = values
    material = review_material(values)
    blocked_target = next(target for target in targets.values()
        if target.get("kind") == "operation" and target["value"].get("output") == "unused")
    proposed = candidate_with_errors(material, "annotation:" + blocked_target["pointer"])
    isolated = isolate_source_review(proposed, material)
    reviewed = partial_receipt(values, material, isolated)
    assert reviewed["review_status"] == "partial"
    assert len(reviewed["review_core"]["validation_barriers"]) == 3
    original = deepcopy((facts.records, facts.data, facts.sinks, annotation))
    requested = candidate(targets)
    engine = DemandEngine(facts, task, annotation, requested, targets, input_contract_review=reviewed)
    blocked = key_for(engine, "unused"); independent = key_for(engine, "answer")
    demand = prepare_demand_review(facts, task, annotation, requested, input_contract_review=reviewed).to_dict()
    blocked_input = assessed(demand, blocked, 0)
    assert all(item["status"] == "unresolved" for item in blocked_input["ranges"])
    removable = assessed(demand, independent, 1)
    assert removable["ranges"] and all(item["status"] == "deletable" for item in removable["ranges"])
    assert all(not item["demand_refs"] for item in removable["ranges"])
    assert any(item["status"] == "required" for item in assessed(demand, independent, 0)["ranges"])
    # The shared read-only lookup also supplies the stored-result validator.
    lookup = InputReviewBarrierIndex(engine)
    diagnostics_before = deepcopy(engine.diagnostics)
    barriers = lookup.for_assessment(blocked_input)
    assert len(barriers) == 3 and not lookup.for_assessment(removable)
    assert engine.diagnostics == diagnostics_before
    expected = [barrier_diagnostic_value(item, "ir_filter", blocked) for item in barriers]
    assert all(item in demand["diagnostics"] for item in expected)
    assert not any(item["origin"] == "source_review" for item in demand["input_findings"])

    # These are the same public result and report paths used by persisted runs.
    doe = prepare_sensitivity_review(facts, task, annotation, requested,
        {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": []},
        input_contract_review=reviewed)
    assert doe.demand_dict() == demand
    expected_doe = [{key: value for key, value in item.items() if key != "requirement_id"} for item in expected]
    assert all(item in doe.to_dict()["diagnostics"] for item in expected_doe)
    for report in (render_html(doe), render_markdown(doe)):
        assert "input_contract_review_validation" in report
        assert "/source_input_findings/0" in report
        assert blocked_input["id"] in report and removable["id"] in report
    assert facts.sinks and original == (facts.records, facts.data, facts.sinks, annotation)
