"""Verified inactive paths do not masquerade as missing local producers."""
from copy import deepcopy

from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from skillflow.propagation import propagate, FlowLocation, FlowState
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.loading import materials_from_result
from tests.document_guided.small_alignment_cases import fallback_fixture, UNKNOWN


def checked_review(candidate):
    material, wire, seeds = candidate
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    registry = DataRegistry("inactive-goal-regression")
    state = {}
    for (kind, name), value in seeds.items():
        item = registry.register_source(kind + ":" + name, acquired_from=kind + ":" + name,
            **({} if value is UNKNOWN else {"content": LiteralContent(value=value)}))
        state[FlowLocation(kind=kind, name=name)] = frozenset([item.id])
    solved = propagate(material["cfg"], to_payload(compiled), initial_registry=registry,
                       initial_state=FlowState.from_mapping(state))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
                                 compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    return facts, prepare_joint_sensitivity_review(facts, facts.annotation).demand_dict()


def test_verified_inactive_demands_are_retained_without_missing_producer_errors():
    facts, demand = checked_review(fallback_fixture(first=True))
    assert facts.status == "complete"
    inactive = [row for row in demand["diagnostics"] if row["code"] == "inactive_goal"]
    assert inactive and all(not row["blocking"] for row in inactive)
    assert all(facts.coverage[row["instruction_id"]] == "not_reached" for row in inactive)
    assert demand["goals"]  # No Task/goal declarations are silently discarded.
    assert not [row for row in demand["diagnostics"]
                if row["code"] in {"unbound_goal", "missing_local_record"}
                and row.get("instruction_id") and facts.coverage[row["instruction_id"]] == "not_reached"]
    for req, row in demand["coverage"]["requirements"].items():
        if not row["has_applicable_goal"]:
            assert any(item["code"] == "unbound_requirement" and item["requirement_id"] == req
                       for item in demand["diagnostics"])


def test_unmodeled_and_blocked_operations_are_not_reclassified_as_inactive():
    material, wire, seeds = fallback_fixture(first=True)
    evidence = deepcopy(wire["ir_semantics"]["ir_fast"]["evidences"])
    wire["ir_semantics"].pop("ir_fast")
    wire.setdefault("processing_gaps", []).append({"instruction_id": "ir_fast", "unmodeled": True,
        "reason": "Regression-only missing protected-call semantics blocks its true dependent paths.", "evidences": evidence})
    facts, demand = checked_review((material, wire, seeds))
    assert facts.status != "complete"
    assert facts.coverage["ir_fast"] == "unmodeled"
    blocked = {ir for ir, status in facts.coverage.items() if status in {"blocked", "unmodeled", "unresolved_binding"}}
    assert blocked
    assert not any(row["code"] == "inactive_goal" and row["instruction_id"] in blocked for row in demand["diagnostics"])
    assert any(row["blocking"] and row["code"] == "upstream_coverage" and row["instruction_id"] in blocked
               for row in demand["diagnostics"])
