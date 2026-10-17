"""Content precision and task preservation gate deterministic sink conclusions."""
from copy import deepcopy

import pytest

from skillflow.doe.sensitivity_material import prepare_sensitivity_review, validate_sensitivity_result
from skillflow.doe.sensitivity_engine import SensitivityEngine, demand_overlap, select, cut
from skillflow.doe.sensitivity_results import resolve_data_review
from tests.doe.test_demand_engine import fixture, candidate, solve, inp, local, literal, evidence, set_operator, target_id


def declarations(path=("token",), *, value=None, property="value", ir="ir_filter"):
    return {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": [{
        "instruction_id": ir, "scope_path": [], "declarations": [{
            "value": value or inp(), "path": list(path), "property": property,
            "label": "credential", "evidences": [evidence()]}]}]}


def review(values, sensitivity=None, requested=None):
    return prepare_sensitivity_review(values[0], values[1], values[2],
        requested or candidate(values[3]), sensitivity or declarations()).to_dict()


def rows(result):
    return [resolve_data_review(row, sink, result["derivations"]["sensitivity"])
            for sink in result["sinks"] for row in sink["data_reviews"]]


def raw_rows(result):
    return [row for sink in result["sinks"] for row in sink["data_reviews"]]


def validate(result, values, sensitivity=None, requested=None):
    request = requested or candidate(values[3])
    expected = solve(values, request)[1]
    return validate_sensitivity_result(result, values[0], values[1], values[2], request,
        sensitivity or declarations(), demand_result=expected)


def test_direct_extra_field_at_model_input_has_supported_comparison_not_whole_deletion():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    original = deepcopy(values)
    result = review(values)
    token = rows(result)
    assert token and all(r["path"] == ["token"] and r["relation"] == "direct" for r in token)
    assert {r["conclusion"] for r in token} == {"excess_supported"}
    assert result["status"] == "complete"
    assert values == original  # No registry refinement or annotation mutation.
    assert review(values) == result
    lifo = prepare_sensitivity_review(values[0], values[1], values[2], candidate(values[3]), declarations(), queue_order="lifo")
    assert lifo.to_dict() == result


def test_required_field_and_whole_opaque_demand_block_excess():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "computed"}], mode="model")
    result = review(values)
    assert rows(result) and all(r["conclusion"] == "no_excess_established" for r in rows(result))
    values = fixture([{"op": "select_part", "input": inp(), "path": ["token"], "output": "token"}], mode="model")
    assert all(r["conclusion"] == "no_excess_established" for r in rows(review(values)))


def test_local_exclusion_and_replacement_do_not_resurrect_old_secret():
    values = fixture([
        {"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"},
        {"op": "update_fields", "input": local("clean"), "updates": [{"path": ["token"], "value": literal("public")}], "output": "new"}
    ], mode="local", returned=[local("new")])
    result = review(values)
    assert result["sinks"] and not rows(result)
    assert result["coverage"]["resolved_declarations"] == 1


def test_exposure_before_cleanup_retains_original_version():
    values = fixture([{"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"}], mode="model")
    result = review(values)
    assert rows(result)
    assert all(r["path"] == ["token"] for r in rows(result))


def test_derived_output_is_influence_unless_output_explicitly_declared():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "digest"}],
                     mode="local", returned=[local("digest")])
    result = review(values)
    assert rows(result) and {r["relation"] for r in rows(result)} == {"possible"}
    explicit = review(values, declarations((), value=local("digest")))
    assert rows(explicit) and {r["relation"] for r in rows(explicit)} == {"direct"}
    assert all(r["conclusion"] != "excess_supported" for r in rows(explicit))


@pytest.mark.parametrize("relation", ["possible", "derived"])
def test_descriptive_refinement_of_opaque_result_keeps_original_influence(relation):
    operations = [{"op": "compute", "inputs": [inp()], "dependencies": [relation], "output": "response"}]
    after = fixture([*operations, {"op": "select_part", "input": local("response"),
                                  "path": ["body"], "output": "body"}],
                    mode="local", returned=[local("response"), local("body")])
    engine, demand = solve(after)
    output = next(op["record"]["outputs"][0][0] for op in engine.ops.values()
                  if op["position"]["instruction_id"] == "ir_filter" and op["spec"]["op"] == "compute")
    refined = engine.index.data[output]
    assert refined["content"]["form"] == "known_parts" and not refined["content"]["parts_complete"]
    # Remove descriptive detail only in a separate core snapshot: ID, origin
    # and all operation references are the exact same ones before/after.
    opaque_engine = deepcopy(engine)
    opaque_engine.index.data[output]["content"] = {"form": "opaque"}
    initial = SensitivityEngine(opaque_engine, demand, {})
    described = SensitivityEngine(engine, demand, {})
    source = refined["origin"]["dependencies"][0]["data"]
    assert (output, relation, None) in initial.edges[source]
    assert (output, relation, None) in described.edges[source]
    refined_result = review(after)
    assert {r["relation"] for r in rows(refined_result) if r["data_id"] == output} == {relation}
    assert rows(refined_result) and all(r["relation"] != "direct" for r in rows(refined_result))
    assert all(r["conclusion"] != "excess_supported" for r in rows(refined_result))


def test_property_only_demand_does_not_authorize_field_or_member_deletion():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["token"], "output": "token"}], mode="model")
    result = review(values, requested=candidate(values[3], property="presence"))
    assert rows(result) and all(r["conclusion"] == "no_excess_established" for r in rows(result))
    assert all("presence" in r["reason"] for r in rows(result))


def test_empty_declarations_cover_all_sinks_without_nonsensitive_assertion():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    result = review(values, {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": []})
    assert len(result["sinks"]) == len(values[0].sinks)
    assert not rows(result)
    assert result["coverage"]["sensitivity_basis"] == "declared_ranges_only"


def test_no_demand_is_not_a_certificate_and_missing_goals_are_partial():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    result = review(values, requested={"goals": [], "expressions": []})
    assert result["status"] == "partial"
    assert rows(result) and all(r["conclusion"] == "no_excess_established" for r in rows(result))


def test_result_loader_rejects_receiver_and_range_tampering_without_solving():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    result = review(values)
    altered = deepcopy(result)
    raw_rows(altered)[0]["input_index"] = 999
    with pytest.raises(ValueError, match="identity|payload"):
        validate(altered, values)
    altered = deepcopy(result)
    raw_rows(altered)[0]["path"] = ["body"]
    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        validate(altered, values)


def test_declaration_identity_and_scope_are_checked():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    with pytest.raises(ValueError, match="absent"):
        review(values, declarations(value=local("missing")))
    invalid = declarations()
    invalid["scopes"][0]["declarations"][0]["evidences"][0]["start_line"] = 999
    with pytest.raises(ValueError):
        review(values, invalid)


def test_range_projection_respects_each_field_names_and_exclusions():
    signal = {"path": [{"kind": "each"}, "token"], "property": "value", "excluded_paths": []}
    assert select(signal, [{"kind": "element", "scope": "scope-one"}])["path"] == ["token"]
    assert select(signal, ["*"]) is None
    assert cut(signal, [[{"kind": "each"}, "token"]]) is None
    whole = {"path": [], "property": "value", "excluded_paths": []}
    redacted = cut(whole, [[{"kind": "each"}, "token"]])
    assert select(redacted, [{"kind": "element", "scope": "scope-one"}, "token"]) is None


def test_demand_property_overlap_is_not_plain_value_membership():
    signal = {"path": ["token"], "property": "value", "excluded_paths": []}
    demand = {"path": [], "each": False, "excluded_paths": [["token"]], "property": "value", "conservative": False}
    assert demand_overlap(signal, demand) == "none"
    demand.update(excluded_paths=[], conservative=True)
    assert demand_overlap(signal, demand) == "retain"
    demand.update(path=["token"], property="presence", conservative=False)
    assert demand_overlap(signal, demand) == "structure"
    signal["property"] = "presence"
    assert demand_overlap(signal, demand) == "retain"


def test_whole_declaration_does_not_make_every_selected_field_sensitive_plaintext():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}],
                     mode="local", returned=[local("body")])
    result = review(values, declarations(()))
    assert rows(result) and {r["relation"] for r in rows(result)} == {"possible"}
    assert all(r["conclusion"] == "no_excess_established" for r in rows(result))


def test_specific_element_exclusion_does_not_remove_each_member_range():
    signal = {"path": [{"kind": "each"}, "token"], "property": "value", "excluded_paths": []}
    result = cut(signal, [[{"kind": "element", "scope": "one"}, "token"]])
    assert result is not None
    assert select(result, [{"kind": "element", "scope": "one"}, "token"]) is None
    assert select(result, [{"kind": "element", "scope": "two"}, "token"]) is not None


@pytest.mark.parametrize("operations,value", [
    ([{"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"}], local("clean")),
    ([{"op": "build", "parts": [], "container": "object", "output": "empty"}], local("empty")),
    ([{"op": "update_fields", "input": inp(), "updates": [{"path": ["nested"], "value": literal({})}], "output": "new"}], local("new")),
])
def test_known_absent_declared_range_is_partial_not_manufactured(operations, value):
    values = fixture(operations, mode="local", returned=[value])
    path = ["nested", "token"] if operations[0]["op"] == "update_fields" else ["token"]
    result = review(values, declarations(path, value=value))
    assert result["status"] == "partial" and not rows(result)
    assert any(d["code"] == "absent_sensitive_range" for d in result["diagnostics"])


def test_nested_each_reports_capability_limit_without_flattening():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    result = review(values, declarations([{"kind": "each"}, "rows", {"kind": "each"}, "token"]))
    assert result["status"] == "partial" and not rows(result)
    assert result["diagnostics"][0]["code"] == "unsupported_sensitivity_scope"


def test_influence_without_supported_demand_is_possible_not_plaintext_excess():
    def unchanged(prepared, raw, ev):
        raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = inp()
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "digest"}],
                     mode="local", returned=[local("digest")], custom=unchanged)
    result = review(values)
    assert rows(result) and all(r["relation"] == "derived" for r in rows(result))
    assert {r["conclusion"] for r in rows(result)} == {"possible_excess"}
    assert all(r["reduction"] is None for r in rows(result))


def test_false_member_is_not_observed_and_controls_are_not_payload():
    values = fixture([{"op": "build", "parts": [{"path": ["optional"], "value": inp(), "when": literal(False)}],
                       "container": "object", "output": "request"}])
    result = review(values)
    assert not rows(result)
    assert result["status"] == "complete"


def test_repeated_parameters_keep_receiver_slot_specific_demands():
    def change(prepared, raw, ev):
        raw["locations"]["pair"] = {"kind": "tool", "name": "pair boundary", "operand_refs": [],
                                     "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["pair"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"][0]["events"].append({"effect": None, "evidences": [], "atomic_ops": [
            {"op": "deliver", "inputs": [inp(), inp()], "target": "pair", "evidences": deepcopy(ev)}]})
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "unused"}],
                     mode="local", custom=change)
    cand = candidate(values[3], path=["body"], goal_target=target_id(values[3], "input_use", op="deliver", slot=1))
    result = review(values, requested=cand)
    delivery = [r for sink in result["sinks"] if sink["boundary"]["sink_type"] == "external_tool" for r in sink["data_reviews"]]
    assert {r["input_index"] for r in delivery} == {0, 1}
    assert {r["conclusion"] for r in delivery if r["input_index"] == 0} == {"no_excess_established"}
    assert {r["conclusion"] for r in delivery if r["input_index"] == 1} == {"excess_supported"}


def test_filter_and_element_scope_keep_member_field_sensitive_without_tool_expansion():
    def change(prepared, raw, ev):
        set_operator(raw, prepared, "ir_filter", ["llm"])
        raw["locations"]["notify"] = {"kind": "tool", "name": "notify", "operand_refs": [], "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["notify"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"].append({"kind": "for_each", "collection": local("selected"), "item": "row", "evidences": deepcopy(ev),
            "body": [{"kind": "processing", "mode": "model", "returns": [], "evidences": deepcopy(ev), "events": [
                {"effect": "transform", "evidences": deepcopy(ev), "atomic_ops": [{"op": "select_part", "input": local("row"), "path": ["summary"], "output": "summary", "evidences": deepcopy(ev)}]},
                {"effect": None, "evidences": [], "atomic_ops": [{"op": "deliver", "inputs": [local("summary")], "target": "notify", "evidences": deepcopy(ev)}]}]}]})
    values = fixture([{"op": "filter_items", "input": inp(), "predicate": "urgent is true", "output": "selected"}], mode="model", custom=change)
    cand = candidate(values[3], expression={"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["urgent"]},
                     expression_op="filter_items", goal_target=target_id(values[3], "input_use", op="deliver", slot=0))
    result = review(values, declarations([{"kind": "each"}, "token"]), cand)
    scoped = [resolve_data_review(r, s, result["derivations"]["sensitivity"]) for s in result["sinks"] if s["boundary"]["scope"] == "element" and s["boundary"]["sink_type"] == "model_observe" for r in s["data_reviews"]]
    assert scoped and any(r["path"] == ["token"] and r["relation"] == "direct" for r in scoped)
    assert not [r for s in result["sinks"] if s["boundary"]["sink_type"] == "external_tool" for r in s["data_reviews"]]


def test_request_influence_does_not_turn_acquired_response_into_copied_plaintext():
    def change(prepared, raw, ev):
        raw["locations"]["service"] = {"kind": "tool", "name": "lookup", "operand_refs": [], "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["service"] = deepcopy(ev)
        set_operator(raw, prepared, "ir_filter", ["tool"])
        raw["ir_semantics"]["ir_filter"]["events"][0]["events"][0] = {"effect": None, "evidences": [], "atomic_ops": [
            {"op": "receive", "inputs": [inp()], "location": "service", "output": "response", "evidences": deepcopy(ev)}]}
        raw["ir_semantics"]["ir_filter"]["empty_effect_evidences"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = local("response")
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "unused"}],
                     mode="local", returned=[local("response")], custom=change)
    result = review(values)
    assert rows(result) and {r["relation"] for r in rows(result)} == {"possible"}
    explicit = review(values, declarations(["token"], value=local("response")))
    assert rows(explicit) and {r["relation"] for r in rows(explicit)} == {"direct"}


def test_possible_sensitive_each_on_known_scalar_is_not_silently_created():
    values = fixture([{"op": "build", "parts": [{"path": ["a"], "value": literal(3)}], "container": "object", "output": "wrapped"}],
                     mode="local", returned=[local("wrapped")])
    result = review(values, declarations(["a", {"kind": "each"}, "token"], value=local("wrapped")))
    assert result["status"] == "partial" and not rows(result)


def test_complete_json_and_declaration_evidence_are_rechecked_on_load():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    result = review(values)
    invalid = declarations()
    invalid["scopes"][0]["declarations"][0]["evidences"][0]["file"] = "skill/absent.md"
    with pytest.raises(ValueError, match="not frozen"):
        validate(result, values, invalid)
    changed = deepcopy(result)
    changed["sinks"][0]["actual_payload"][0]["inputs"][0] = []
    with pytest.raises(ValueError):
        validate(changed, values)


def test_review_copy_isolation_and_shared_derivation_references():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    result = prepare_sensitivity_review(values[0], values[1], values[2], candidate(values[3]), declarations())
    changed = result.to_dict()
    rows(changed)[0]["path"].append("mutated")
    assert rows(result.to_dict())[0]["path"] == ["token"]
    changed = result.index_dict()
    next(iter(changed["declarations"].values()))["declaration"]["path"].append("mutated")
    assert next(iter(result.index_dict()["declarations"].values()))["declaration"]["path"] == ["token"]


def test_supported_count_drops_member_value_influence_but_retains_declared_cardinality():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "n"}],
                     mode="local", returned=[local("n")])
    demand = candidate(values[3], expression={"op": "count", "arg": {"op": "ref", "value": inp()}})
    token = review(values, declarations([{"kind": "each"}, "token"]), demand)
    assert token["sinks"] and not rows(token)
    count = review(values, declarations((), property="cardinality"), demand)
    assert rows(count) and {r["property"] for r in rows(count)} == {"cardinality"}
    assert {r["relation"] for r in rows(count)} == {"derived"}
    assert all(r["conclusion"] == "no_excess_established" for r in rows(count))


def test_guard_influences_member_presence_without_becoming_plaintext_member():
    values = fixture([
        {"op": "select_part", "input": inp(), "path": ["flag"], "output": "flag"},
        {"op": "build", "parts": [{"path": ["optional"], "value": literal("public"), "when": local("flag")}],
         "container": "object", "output": "request"}], mode="local", returned=[local("request")])
    result = review(values, declarations(["flag"]))
    assert rows(result) and all(r["relation"] == "derived" and r["path"] == ["optional"] for r in rows(result))
    assert all(r["property"] == "value" for r in rows(result))  # Original declaration property.
    assert all("conditional_membership" in result["derivations"]["sensitivity"][r["derivation_id"]]["rules"] for r in rows(result))
    for row in rows(result):
        data = next(d for d in values[0].data if d["id"] == row["data_id"])
        assert not any(p["path"] == ["flag"] for p in data["content"].get("parts", []))


def test_filtered_collection_does_not_copy_original_cardinality():
    values = fixture([{"op": "filter_items", "input": inp(), "predicate": "enabled", "output": "selected"}],
                     mode="local", returned=[local("selected")])
    result = review(values, declarations((), property="cardinality"))
    assert rows(result) and all(r["relation"] == "possible" for r in rows(result))


def test_sensitive_presence_can_describe_absent_final_member_only():
    values = fixture([{"op": "build", "parts": [{"path": ["parent"], "value": literal({})}],
                       "container": "object", "output": "object"}], mode="local", returned=[local("object")])
    good = review(values, declarations(["parent", "absent"], value=local("object"), property="presence"))
    assert good["status"] == "complete" and rows(good)
    assert all(r["property"] == "presence" and r["relation"] == "direct" for r in rows(good))
    missing_parent = review(values, declarations(["absent", "child"], value=local("object"), property="presence"))
    assert missing_parent["status"] == "partial" and not rows(missing_parent)
    impossible = review(values, declarations(["parent", {"kind": "each"}], value=local("object"), property="presence"))
    assert impossible["status"] == "partial" and not rows(impossible)


def test_saved_result_cannot_drop_required_sensitive_field_demand_without_resolving(monkeypatch):
    from skillflow.doe.demand_engine import DemandEngine
    values = fixture([
        {"op": "select_part", "input": inp(), "path": ["token"], "output": "token"},
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    request = candidate(values[3])
    target = next(identity for identity, row in values[3].items() if row["kind"] == "local_output" and row["value"] == "token")
    request["goals"].append({**request["goals"][0], "id": "G2", "target": values[3][target]["target"]})
    expected = solve(values, request)[1]
    result = review(values, requested=request)
    assert all(row["conclusion"] == "no_excess_established" for row in rows(result))
    changed = deepcopy(result)
    row = raw_rows(changed)[0]
    row["demand_refs"] = [identity for identity in row["demand_refs"] if changed["derivations"]["demand"][identity]["path"] != ["token"]]
    assert row["demand_refs"]  # Retained body demand fooled the previous check.
    row["conclusion"] = "excess_supported"
    row["reduction"] = {"kind": "exclude_field", "path": ["token"]}
    monkeypatch.setattr(DemandEngine, "solve", lambda *args, **kwargs: pytest.fail("Read-only validation must not solve"))
    with pytest.raises(ValueError, match="complete verified demand set"):
        validate_sensitivity_result(changed, values[0], values[1], values[2], request, declarations(), demand_result=expected)
    missing = deepcopy(result)
    missing["sinks"][0]["data_reviews"] = []
    with pytest.raises(ValueError, match="tracked payload range"):
        validate_sensitivity_result(missing, values[0], values[1], values[2], request, declarations(), demand_result=expected)


def test_saved_result_cannot_hide_limitations_or_relabel_direct_as_possible(monkeypatch):
    from skillflow.doe.demand_engine import DemandEngine
    from skillflow.propagation.contracts.task import Task
    values = list(fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model"))
    from skillflow.propagation.annotation.services import compile_response, to_payload
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    raw = deepcopy(values[2]["raw_annotation"])
    raw["realizations"][0].update(status="partial", gaps=[{
        "reason": "尚有未形式化的次数限制。", "evidences": values[1].requirements[0].model_dump(mode="json")["evidences"]}])
    prepared = values[2]["material"]
    checked, compiled, mapping = compile_response(raw, prepared)
    values[0] = materials_from_result(propagate(prepared["cfg"], to_payload(compiled)),
        material=prepared, raw_annotation=checked, compiled_annotation=compiled, mapping=mapping)
    values[2] = values[0].annotation
    request = candidate(values[3])
    expected = solve(values, request)[1]
    result = review(values, requested=request)
    assert result["status"] == "partial" and rows(result)[0]["limitations"]
    monkeypatch.setattr(DemandEngine, "solve", lambda *args, **kwargs: pytest.fail("Read-only validation must not solve"))
    changed = deepcopy(result)
    changed["sinks"][0]["limitations"] = []
    raw_rows(changed)[0].update(conclusion="excess_supported", reduction={"kind": "exclude_field", "path": ["token"]})
    with pytest.raises(ValueError, match="drops a verified demand limitation|changes relevant saved analysis limitations"):
        validate_sensitivity_result(changed, values[0], values[1], values[2], request, declarations(), demand_result=expected)
    changed = deepcopy(result)
    raw_rows(changed)[0]["conclusion"] = "possible_excess"
    with pytest.raises(ValueError, match="supported comparison rule"):
        validate_sensitivity_result(changed, values[0], values[1], values[2], request, declarations(), demand_result=expected)
