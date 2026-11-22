"""Semantic input contracts drive field-level deletion without erasing facts."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.input_contract_review import build_input_contract_review, input_contract_binding, input_contract_review_inventory, SOURCE_REVIEW_VERSION
from skillflow.doe.input_assessments import deletable_reduction
from skillflow.propagation.contracts.demand import validate_demand_candidate
from skillflow.propagation.contracts.joint import joint_source_files
from tests.doe.test_demand_engine import fixture, inp, local, literal, evidence, candidate
from tests.doe.input_review_helpers import checks_for_inventory, projection_checks


def row(index, *paths, gap=None):
    result = {"input_index": index, "required": [{"property": "value", "path": p} for p in paths],
        "remainder": "unresolved" if gap else "independent",
        "reason": "Only the listed fields determine this output; the remaining fields do not contribute."}
    if gap:
        result["gap"] = {"code": "ambiguous_semantics", "reason": gap,
            "missing": "Specify whether the request's fallback label is used when its primary label is absent.",
            "resolution": "Define which label is selected when the primary label is absent.",
            "evidences": [evidence()]}
    return result


def rule(path, inputs, property="value"):
    return {"output": {"property": property, "path": path}, "inputs": inputs,
            "reason": "The specified output is determined by exactly these input fields.", "evidences": [evidence()]}


def compute(inputs, rules, **contract):
    return {"op": "compute", "inputs": inputs, "dependencies": ["possible"] * len(inputs), "output": "answer",
            "demand_transfer": {"rules": rules, **contract}}


def receipt(values, *, status="accepted", partial=False):
    facts, task, annotation, targets = values
    files = joint_source_files(annotation["material"])
    inventory = input_contract_review_inventory(cfg=facts.cfg, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    entries = annotation["compiled_annotation"].get("input_contracts", [])
    cited = ((entries[0]["contract"].get("evidences") or entries[0]["contract"]["rules"][0]["evidences"])
             if entries else [{"file": next(iter(files)), "start_line": 1, "end_line": 1,
                                "reason": "The synthetic source defines the represented operation."}])
    checks = checks_for_inventory(inventory, cited, status=status)
    material = {"partial": partial, "input_contract_inventory": inventory, "input_contract_binding": input_contract_binding(files=files,
        cfg=facts.cfg, task=annotation["task"], raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])}
    review = {"status": "complete", "availability": {"task": True, "cfg": True, "annotation": True},
              "review": {"schema_version": SOURCE_REVIEW_VERSION, "outcome": "completed",
                         "findings": [], "input_contract_checks": checks,
                         "input_projection_checks": projection_checks(inventory, cited), "source_input_findings": []}}
    return build_input_contract_review(files=files, cfg=facts.cfg, annotation=annotation,
                                      review=review, review_material=material)


def solve(values, *, path=(), property="value", review=True, requested=None):
    facts, task, annotation, targets = values
    requested = requested or candidate(targets, path=path, property=property)
    parsed = validate_demand_candidate(requested, task, joint_source_files(annotation["material"]), targets)
    review = receipt(values) if review is True else review if review else None
    engines = [DemandEngine(facts, task, annotation, parsed.model_dump(mode="json"), targets,
                           input_contract_review=review) for _ in range(2)]
    result = engines[0].solve()
    assert result == engines[1].solve(queue_order="lifo")
    assert result == prepare_demand_review(facts, task, annotation, requested, input_contract_review=review).to_dict()
    return engines[0], result


def operation_key(engine, op="compute"):
    return next(key for key, info in engine.ops.items() if info["spec"]["op"] == op)


def assessed(result, key, index):
    return next(a for a in result["input_assessments"] if a["node_kind"] == "op_input"
                and a["operation_id"] == key and a["input_index"] == index)


def test_three_claimed_inputs_only_two_required_and_actual_observations_remain():
    values = fixture([compute([inp(), literal({"b": 2}), literal({"c": 3})],
        [rule([], [row(0, ["a"]), row(1, ["b"]), row(2)])])], mode="model")
    before = deepcopy(values[0].records)
    engine, result = solve(values)
    key = operation_key(engine)
    required = [d for d in result["derivations"].values() if d["node"]["operation_id"] == key
                and d["node"]["kind"] == "op_input"]
    assert {(d["node"]["slot"], tuple(d["path"])) for d in required} == {(0, ("a",)), (1, ("b",))}
    third = assessed(result, key, 2)
    assert any(r["status"] == "deletable" and r["path"] == [] and not r["excluded_paths"] for r in third["ranges"])
    assert values[0].records == before
    assert len(engine.ops[key]["record"]["inputs"]) == 3
    assert engine.contracts.influenced_outputs(key, 2, []) == []
    assert engine.contracts.influenced_outputs(key, 0, ["a"]) == [{"property": "value", "path": []}]


def test_object_remainder_is_deletable_but_required_field_and_whole_slot_are_not():
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    engine, result = solve(values)
    key = operation_key(engine)
    data = engine.ops[key]["record"]["inputs"][0][0]
    reduction, refs = deletable_reduction(result, key, 0, data, ["token"])
    assert reduction == {"kind": "exclude_field", "path": ["token"]} and refs
    assert deletable_reduction(result, key, 0, data, ["body"]) == (None, [])
    assert deletable_reduction(result, key, 0, data, []) == (None, [])


def test_output_field_rules_do_not_promote_unrequested_siblings():
    rules = [rule(["x"], [row(0, ["a"]), row(1)]), rule(["z"], [row(0), row(1, ["b"])])]
    parts = [{"property": "value", "path": [name]} for name in ("x", "z")]
    values = fixture([compute([inp(), literal({"b": 2})], rules, output_parts=parts)])
    engine, narrow = solve(values, path=["x"])
    key = operation_key(engine)
    assert any(r["status"] == "deletable" and not r["excluded_paths"] for r in assessed(narrow, key, 1)["ranges"])
    assert engine.contracts.influenced_outputs(key, 0, ["a"]) == [{"property": "value", "path": ["x"]}]
    _, whole = solve(values)
    assert all(any(r["status"] == "required" for r in assessed(whole, key, slot)["ranges"]) for slot in (0, 1))


def test_whole_output_rule_is_not_a_narrow_output_rule():
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    engine, result = solve(values, path=["x"])
    assert result["status"] == "partial"
    gap = next(d for d in result["diagnostics"] if d["code"] == "input_contract_output_gap")
    assert "selector" in gap["reason"] and "demand_transfer" in gap["reason"]
    assert not any(r["status"] == "deletable" for r in assessed(result, operation_key(engine), 0)["ranges"])


def test_concrete_uncertainty_does_not_block_independent_other_input():
    values = fixture([compute([inp(), literal({"c": 3})], [rule([], [
        row(0, ["body"], gap="The source does not define which fallback label is selected when body is absent."), row(1)])])])
    engine, result = solve(values)
    key = operation_key(engine)
    assert any(r["status"] == "unresolved" and r["diagnostic_refs"] for r in assessed(result, key, 0)["ranges"])
    assert any(r["status"] == "deletable" for r in assessed(result, key, 1)["ranges"])


@pytest.mark.parametrize("review", [False, "rejected"])
def test_unreviewed_or_rejected_contract_does_not_authorize_independence(review):
    values = fixture([compute([inp(), literal("extra")], [rule([], [row(0, ["body"]), row(1)])])])
    engine, result = solve(values, review=receipt(values, status=review) if review else False)
    assert not any(r["status"] == "deletable" for r in assessed(result, operation_key(engine), 1)["ranges"])
    assert any("contract:" in d["reason"] for d in result["diagnostics"])
    if review == "rejected":
        assert not any(f["kind"] == "wrong_input" for f in result["input_findings"])


def test_another_needed_consumer_retains_same_ir_input():
    first = compute([inp()], [rule([], [row(0)])])
    values = fixture([first, {"op": "select_part", "input": inp(), "path": ["token"], "output": "kept"},
        {"op": "build", "parts": [{"path": ["answer"], "value": local("answer")},
                                  {"path": ["kept"], "value": local("kept")}], "container": "object", "output": "both"}])
    engine, result = solve(values)
    ir_input = next(a for a in result["input_assessments"] if a["node_kind"] == "ir_input"
                    and a["instruction_id"] == "ir_filter" and a["input_index"] == 0)
    assert any(r["status"] == "required" and r["path"] == ["token"] for r in ir_input["ranges"])
    assert not any(r["status"] == "deletable" and not r["path"] and not r["excluded_paths"] for r in ir_input["ranges"])


def test_unrelated_partial_review_does_not_erase_accepted_contract():
    values = fixture([compute([inp()], [rule([], [row(0, ["body"])])])])
    _, result = solve(values, review=receipt(values, partial=True))
    assert not any(d["code"].startswith("input_contract_") for d in result["diagnostics"])


@pytest.mark.parametrize("payload,preserved", [({}, {"presence"}), ({"optional": 7}, {"presence", "value"})])
def test_optional_input_preserves_presence_and_only_existing_value(payload, preserved):
    optional = row(0, ["optional"])
    optional["required"][0]["if_present"] = True
    values = fixture([compute([literal(payload)], [rule([], [optional])])])
    engine, result = solve(values)
    key = operation_key(engine)
    requirements = [d for d in result["derivations"].values()
                    if d["node"]["kind"] == "op_input" and d["node"]["operation_id"] == key]
    assert {d["property"] for d in requirements if d["path"] == ["optional"]} == preserved
    assert not any(d["code"] == "input_contract_missing_input" for d in result["diagnostics"])
    assert result["input_contract_review_sha256"] == receipt(values)["receipt_sha256"]
