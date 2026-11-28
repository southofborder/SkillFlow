"""Backward evidence follows an actual protected call's separate public slots."""

from copy import deepcopy

import pytest

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation.annotation.binding_examples import inp, literal, local
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from tests.propagation.test_protected_outcomes import protected_call


def interpreted(material, wire):
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    return materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)


def demand(material, wire, *, queue_order="fifo"):
    facts = interpreted(material, wire)
    return prepare_joint_sensitivity_review(facts, facts.annotation, queue_order=queue_order).demand_dict()


@pytest.mark.parametrize("choice", [True, False])
def test_dispatch_demand_uses_recorded_completion_and_real_predicate(choice):
    material, wire = protected_call(choice)
    wire["demands"][0].update(target={"instruction_id": "ir_route", "side": "input", "index": 0})
    result = demand(material, wire)
    assert result == demand(material, wire, queue_order="lifo")
    scoped = [row for row in result["derivations"].values() if row.get("outcome_data_ids")]
    assert any(row["node"]["instruction_id"] == "ir_call" and row["node"]["slot"] == 2 for row in scoped)
    controls = [row for row in result["derivations"].values() if "typed_case_selector" in row["rules"]]
    assert controls and all(row["node"]["instruction_id"] == "ir_call" and row["node"]["slot"] == 0
                            and not row["conservative"] for row in controls)
    assert not any(row["code"] == "unresolved_outcome_dependency" for row in result["diagnostics"])


@pytest.mark.parametrize(("choice", "outcome", "field_slot"), [(True, "normal", 1), (False, "raised", 2)])
def test_result_field_demand_uses_only_matching_normal_or_throw_producer(choice, outcome, field_slot):
    material, wire = protected_call(choice)
    call = material["cfg"]["blocks"]["sample"]["instructions"][0]
    call["inputs"] += [literal("return detail"), literal("exception detail"), literal("private sibling")]
    cases = wire["ir_semantics"]["ir_call"]["segments"][0]["cases"]
    for idx, case in enumerate(cases, start=1):
        case["segments"] += [{"mode": "local", "returns": [], "ops": [{"op": "build", "container": "object",
            "parts": [{"path": ["detail"], "value": inp(idx)}, {"path": ["private"], "value": inp(3)}],
            "output": "result"}]}]
        case["yield" if idx == 1 else "raise"] = local("result")
    wire["demands"][0].update(target={"instruction_id": "ir_read_" + outcome, "side": "input", "index": 0},
                              path=["detail"])
    result = demand(material, wire)
    assert result == demand(material, deepcopy(wire), queue_order="lifo")
    required = [row for row in result["derivations"].values() if not row["conservative"]
                and row["node"]["instruction_id"] == "ir_call" and row["node"]["kind"] == "ir_input"]
    assert {row["node"]["slot"] for row in required} == {0, field_slot}
    assert any("protected_outcome_value" in row["rules"] and row["path"] == ["detail"]
               for row in result["derivations"].values())


def test_intrinsic_exception_yields_local_uncertainty_without_aliasing_normal_return():
    material, wire = protected_call(False)
    wire["demands"][0].update(target={"instruction_id": "ir_read_raised", "side": "input", "index": 0})
    result = demand(material, wire)
    assert any(row["code"] == "unresolved_outcome_dependency" and row["instruction_id"] == "ir_call"
               for row in result["diagnostics"])
    assert not any("protected_outcome_value" in row["rules"] for row in result["derivations"].values())


def test_saved_outcome_demand_cannot_drop_a_version_of_the_consumed_completion():
    from skillflow.doe.demand_results import validate_result_references
    from skillflow.propagation.contracts.demand_index import build_demand_target_index

    material, wire = protected_call()
    wire["demands"][0].update(target={"instruction_id": "ir_route", "side": "input", "index": 0})
    facts = interpreted(material, wire)
    report = prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()
    selection = next(row for row in report["derivations"].values() if len(row.get("outcome_data_ids", [])) == 2)
    selection["outcome_data_ids"] = selection["outcome_data_ids"][:1]
    targets = build_demand_target_index(facts.cfg, facts.annotation["raw_annotation"])
    with pytest.raises(ValueError, match="Outcome result selection differs from the consuming operand"):
        validate_result_references(report, facts, targets)


@pytest.mark.parametrize("producer_reached", [True, False])
def test_missing_cfg_outcome_producer_has_only_a_scoped_control_gap(producer_reached):
    from skillflow.doe.demand_results import validate_result_references
    from skillflow.propagation.annotation.binding_examples import instruction
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.material import prepare_material
    from tests.propagation.test_protected_outcomes import use_outcome_dispatch

    material, wire = protected_call()
    use_outcome_dispatch(material, wire)
    producer = wire["ir_semantics"].pop("ir_call")
    wire["processing_gaps"] = [{"instruction_id": "ir_call", "unmodeled": True,
        "reason": "The protected producer has no executable semantics.", "evidences": producer["evidences"]}]
    if not producer_reached:
        material["cfg"]["blocks"]["sample"]["instructions"].insert(0, instruction("ir_prior", "parse", []))
        wire["processing_gaps"].append({"instruction_id": "ir_prior", "unmodeled": True,
            "reason": "An earlier operation cannot execute.", "evidences": producer["evidences"]})
    material = prepare_material(material["source"], material["cfg"], task_baseline=material["task"])
    facts = interpreted(material, wire)
    assert facts.coverage["ir_call"] == ("unmodeled" if producer_reached else "blocked")
    assert facts.coverage["ir_route"] == "blocked"
    report = prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()
    diagnostic = next(row for row in report["diagnostics"] if row["code"] == "unavailable_outcome_dependency")
    assert diagnostic["instruction_id"] == "ir_call" and diagnostic["affected_instruction_ids"] == ["ir_call"]
    assert diagnostic["blocking"] and diagnostic["operation_id"] is None
    targets = build_demand_target_index(facts.cfg, facts.annotation["raw_annotation"])
    changes = [
            {"instruction_id": "ir_route", "affected_instruction_ids": ["ir_route"]},
            {"code": "unresolved_outcome_dependency"}, {"blocking": False},
            {"reason": "The requested protected outcome has no matching recorded version."}]
    if not producer_reached:
        changes.append({"instruction_id": "ir_prior", "affected_instruction_ids": ["ir_prior"]})
    for change in changes:
        forged = deepcopy(report)
        next(row for row in forged["diagnostics"] if row["id"] == diagnostic["id"]).update(change)
        with pytest.raises(ValueError, match="Outcome diagnostic must identify a declared protected outcome"):
            validate_result_references(forged, facts, targets)


@pytest.mark.parametrize("direct", [False, True])
def test_editing_case_input_cannot_certify_an_opaque_outcome_as_unchanged(direct):
    from skillflow.doe.constraint_preservation import ForwardInfluence
    from skillflow.doe.demand_engine import DemandEngine
    from skillflow.propagation.contracts.demand_index import build_demand_target_index
    from skillflow.propagation.contracts.task import Task

    material, wire = protected_call()
    if direct:
        from tests.propagation.test_protected_outcomes import use_outcome_dispatch
        use_outcome_dispatch(material, wire)
    facts = interpreted(material, wire)
    annotation = facts.annotation
    targets = build_demand_target_index(facts.cfg, annotation["raw_annotation"])
    candidate = {"goals": annotation["compiled_annotation"]["demands"], "expressions": []}
    engine = DemandEngine(facts, Task.model_validate(annotation["task"]), annotation, candidate, targets)
    operation = next(key for key, op in engine.ops.items() if op["spec"]["op"] == "write")
    closure = ForwardInfluence(engine).run(operation, 0, [])
    assert not closure["complete"]
    assert any("unresolved protected outcome" in reason for reason in closure["limitations"])
    if direct:
        assert any("unresolved selection at ir_route" in reason for reason in closure["limitations"])


def test_only_an_exact_typed_route_view_matches_the_original_outcome_version():
    from types import SimpleNamespace

    from skillflow.doe.outcome_demands import OutcomeDemands
    from skillflow.propagation.loop_domain import key as producer_key

    site = producer_key(["selector-route", "recorded"])

    def route(path, bindings, *, producer=site):
        return {"origin": {"at": producer, "inputs": ["recorded"]}, "content": {
            "form": "loop_summary", "scope": "selector-route:recorded",
            "producer": producer, "bindings": bindings,
            "variants": [{"inputs": ["recorded"],
                          "content": {"form": "selection", "base": "recorded", "path": path}}]}}

    original = {"content": {"form": "opaque"}}
    data = {"recorded": original, "other": original, "route": route([], {"shape": "object"}),
            "projected": route(["field"], {"shape": "object"}),
            "refined": route([], {"shape": "object", "status": "ready"}),
            "conflicting": route([], {"shape": "object", "status": "failed"}),
            "wrong_site": route([], {"shape": "object"}, producer="typed branch selector")}
    engine = SimpleNamespace(compiled={"ir_semantics": {}}, ops={}, index=SimpleNamespace(records={}, data=data))
    outcomes = OutcomeDemands(engine)
    assert outcomes.matching_versions(["route"], ["recorded", "other"]) == ["recorded"]
    assert outcomes.matching_versions(["projected", "wrong_site"], ["recorded", "other"]) == []
    assert outcomes.matching_versions(["refined"], ["route", "conflicting"]) == ["route"]
    assert outcomes.partition_versions(["other", "refined"], ["route", "recorded", "other"]) == (
        ["other"], {"refined"})
