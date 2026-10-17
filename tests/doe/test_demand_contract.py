"""Demand candidates validate references, not task necessity or entailment."""
from copy import deepcopy
import json

import pytest
from pydantic import TypeAdapter

from skillflow.common.paths import project_root
from skillflow.doe.demand_index import build_demand_target_index, target_id_for
from skillflow.propagation.contracts.references import target_key
from skillflow.propagation.contracts.demand import CandidateDemand, DemandExpression, validate_demand_candidate
from skillflow.propagation.contracts.task import Task
from tests.doe.helpers import annotation_fixture


BASE = project_root() / "experiments/propagation/runs/sink-tightening-v1-20261002-205045/cases/001/annotation"


def inputs():
    cfg = json.loads((BASE / "inputs/cfg.json").read_text(encoding="utf-8"))
    raw = annotation_fixture(BASE)
    return cfg, raw


def span(**changes):
    return {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "reason": "This source states the required filtering relationship.", **changes}


def task():
    from skillflow.propagation.contracts.task import validate_task_candidate
    return validate_task_candidate({"purpose": {"text": "Filter and notify.", "evidences": [span()]},
        "requirements": [{"id": "R1", "text": "Send each selected summary unchanged.", "evidences": [span()]}],
        "source_accounting": [{"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
            "disposition": "requirement", "requirement_ids": ["R1"], "issue_ids": [],
            "reason": "独立契约测试的来源登记。"}], "issues": []},
        source_files={"skill/SKILL.md": "Filter and notify.\r\n"}, basis="declared_skill")


def goal(index):
    identity = next(identity for identity, target in index.items()
                    if target.get("instruction_id") == "ir_005" and target["kind"] == "input_use"
                    and target["slot"] == 1)
    return {"id": "G1", "requirement_id": "R1", "target": index[identity]["target"], "preserve": "value",
            "expected": {"kind": "local", "name": "event_record"}, "expected_path": ["summary"],
            "reason": "Preserve the current element's original summary."}


def index():
    return build_demand_target_index(*inputs())


def validate(candidate, targets):
    return validate_demand_candidate(candidate, task(), {"skill/SKILL.md": "Filter and notify.\r\n"}, targets)


def test_index_preserves_cfg_targets_and_raw_scopes_without_mutation():
    cfg, raw = inputs()
    original = deepcopy((cfg, raw))
    targets = build_demand_target_index(cfg, raw)
    assert (cfg, raw) == original
    assert targets[target_key({"path": []})]["kind"] == "graph"
    deliveries = [t for t in targets.values() if t.get("instruction_id") == "ir_005"
                  and t["kind"] == "input_use" and t["raw_path"][-4:-2] == ["atomic_ops", 0]]
    body = next(t for t in deliveries if t["slot"] == 1)
    assert body["scope_path"] == ["events", 0]
    assert body["segment_path"] == ["events", 0, "body", 0]
    assert body["ref"] == {"kind": "local", "name": "summary_value"}
    identity = target_id_for("ir_005", body["raw_path"])
    assert targets[identity] == body
    body["value"]["name"] = "changed"
    assert raw == original[1]


def test_index_deterministic_under_object_reordering_and_no_return_outputs():
    cfg, raw = inputs()
    reordered = json.loads(json.dumps(raw, sort_keys=True))
    assert build_demand_target_index(cfg, raw) == build_demand_target_index(cfg, reordered)
    assert not any(t.get("instruction_id") == "ir_010" and t["kind"] == "output_binding"
                   for t in build_demand_target_index(cfg, raw).values())


def test_goal_roundtrip_and_implicit_incomplete_coverage_is_not_filled():
    targets = index()
    parsed = validate({"goals": [goal(targets)], "expressions": []}, targets)
    assert CandidateDemand.model_validate_json(parsed.model_dump_json()) == parsed
    assert parsed.goals[0].path == []
    assert validate({"goals": []}, targets).goals == []


@pytest.mark.parametrize("field,value", [("id", " "), ("preserve", "necessary"),
    ("path", [True]), ("path", [-1]), ("expected_path", [0.1]), ("minimal_fields", [])])
def test_invalid_goal_structure_rejected(field, value):
    targets = index()
    item = {**goal(targets), field: value}
    with pytest.raises(ValueError):
        validate({"goals": [item]}, targets)


def test_duplicate_and_missing_goal_references_rejected():
    targets = index()
    item = goal(targets)
    for candidate in [{"goals": [item, item]},
                      {"goals": [{**item, "target": "missing"}]},
                      {"goals": [{**item, "requirement_id": "R99"}]},
                      {"goals": [{**item, "expected": None}]}]:
        with pytest.raises(ValueError):
            validate(candidate, targets)


@pytest.mark.parametrize("ref", [{"kind": "local", "name": "undefined"},
    {"kind": "input", "index": 99}, {"kind": "input", "index": 0}])
def test_missing_values_and_resource_identity_rejected(ref):
    targets = index()
    with pytest.raises(ValueError):
        validate({"goals": [{**goal(targets), "expected": ref}]}, targets)


def test_element_local_cannot_escape_to_public_output():
    targets = index()
    output = next(k for k, t in targets.items() if t["kind"] == "output_binding")
    with pytest.raises(ValueError, match="scope"):
        validate({"goals": [{**goal(targets), "target": targets[output]["target"]}]}, targets)


def expression(targets):
    identity = next(identity for identity, t in targets.items()
                    if t["kind"] == "operation" and t["value"]["op"] == "filter_items")
    return {"target": targets[identity]["target"], "expression": {"op": "and", "args": [
        {"op": "not", "arg": {"op": "field", "arg": {"op": "ref", "value": {"kind": "input", "index": 0}},
                                     "path": ["opted_out"]}},
        {"op": "ge", "left": {"op": "field", "arg": {"op": "ref", "value": {"kind": "input", "index": 0}},
                                   "path": ["value"]}, "right": {"op": "literal", "value": 100}}]},
            "evidences": [span()]}


def test_recursive_expression_and_true_reference_do_not_prove_interpretation():
    targets = index()
    parsed = validate({"goals": [], "expressions": [expression(targets)]}, targets)
    assert parsed.expressions[0].expression.op == "and"
    assert parsed == CandidateDemand.model_validate_json(parsed.model_dump_json())
    # A differently interpreted but real source span passes structural validation.
    candidate = expression(targets)
    candidate["evidences"][0]["reason"] = "A questionable interpretation is still a claim."
    assert validate({"goals": [], "expressions": [candidate]}, targets)


@pytest.mark.parametrize("mutation", ["unsupported", "span", "duplicate", "extra_input"])
def test_expression_target_span_uniqueness_and_inputs(mutation):
    targets = index()
    expr = expression(targets)
    expressions = [expr]
    if mutation == "unsupported":
        expr["target"] = next(t["target"] for k, t in targets.items()
                                 if t["kind"] == "operation" and t["value"]["op"] == "select_part")
    elif mutation == "span":
        expr["evidences"][0]["end_line"] = 8
    elif mutation == "duplicate":
        expressions.append(deepcopy(expr))
    else:
        expr["expression"] = {"op": "ref", "value": {"kind": "local", "name": "filtered_events"}}
    with pytest.raises(ValueError):
        validate({"goals": [], "expressions": expressions}, targets)


@pytest.mark.parametrize("expr", [{"op": "and", "args": []},
    {"op": "field", "arg": {"op": "literal", "value": {}}, "path": []},
    {"op": "not", "arg": {"op": "literal", "value": True}, "reason": "not a field"},
    {"op": "literal", "value": float("nan")},
    {"op": "not", "arg": {"op": "literal", "value": "false"}},
    {"op": "count", "arg": {"op": "literal", "value": "records"}},
    {"op": "or", "args": [{"op": "literal", "value": 1}, {"op": "literal", "value": False}]},
    {"op": "ref", "value": {"kind": "input", "index": True}}])
def test_invalid_expression_shapes(expr):
    with pytest.raises(ValueError):
        TypeAdapter(DemandExpression).validate_python(expr)
