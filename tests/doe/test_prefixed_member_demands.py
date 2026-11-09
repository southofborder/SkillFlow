"""One member selector retains its field prefix across real data operations."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.sensitivity_material import prepare_sensitivity_review
from skillflow.doe.sensitivity_engine import demand_overlap
from skillflow.propagation.data import LiteralContent, OpaqueContent
from tests.doe.test_map_collection import fixture, local
from tests.doe.test_demand_engine import (
    fixture as operation_fixture, solve, input_demands, inp, literal,
)


EACH = {"kind": "each"}


def wrap_records(raw, citation):
    spec = raw["ir_semantics"]["ir_process"]
    tail = spec["events"][1]["events"][0]["atomic_ops"]
    write = tail[0]
    collection = deepcopy(write["input"])
    tail.insert(0, {"op": "build", "container": "object", "output": "response_wrapper",
        "parts": [{"path": ["rows"], "value": collection},
                  {"path": ["unrelated"], "value": {"kind": "literal", "value": "extra"}}],
        "evidences": [citation]})
    write["input"] = local("response_wrapper")
    spec["output_bindings"][0]["value"] = local("response_wrapper")


def test_prefixed_endpoint_demand_reaches_only_corresponding_yield_field():
    facts, task, annotation, candidate, engine = fixture(
        path=["rows", EACH, "url"], customize=wrap_records)
    result = engine.solve()
    member_inputs = [row for row in result["derivations"].values()
        if row["node"]["kind"] == "op_input"
        and engine.ops[row["node"]["operation_id"]]["scope"] is not None
        and engine.ops[row["node"]["operation_id"]]["spec"]["op"] == "build"]
    assert member_inputs and {row["node"]["slot"] for row in member_inputs} == {0}
    assert all(row["path"] == [] and not row["each"] for row in member_inputs)
    assert not any(row["node"]["kind"] == "op_output"
        and engine.ops[row["node"]["operation_id"]]["spec"]["op"] == "receive"
        for row in result["derivations"].values())
    assert prepare_demand_review(facts, task, annotation, candidate).to_dict() == result
    assert DemandEngine(facts, task, annotation, candidate, engine.targets).solve(queue_order="lifo") == result


def test_prefixed_sensitive_content_is_compared_in_the_same_receiver_frame():
    facts, task, annotation, candidate, _ = fixture(
        path=["rows", EACH, "url"], customize=wrap_records)
    reviewed = prepare_sensitivity_review(facts, task, annotation, candidate).to_dict()
    saved = next(s for s in reviewed["sinks"] if s["boundary"]["sink_type"] == "storage_write")
    assert len(saved["data_reviews"]) == 2
    assert {r["conclusion"] for r in saved["data_reviews"]} == {"excess_supported"}
    assert {tuple(r["reduction"]["path"]) for r in saved["data_reviews"]} == {
        ("rows", 0, "response", "token"), ("rows", 1, "response", "token")}


def test_prefixed_collection_cardinality_does_not_demand_member_content():
    _, _, _, _, engine = fixture(preserve="cardinality", path=["rows"], customize=wrap_records)
    result = engine.solve()
    assert not any(row["node"]["kind"] == "op_input"
        and engine.ops[row["node"]["operation_id"]]["scope"] is not None
        for row in result["derivations"].values())
    assert any(row["node"]["kind"] == "ir_input"
        and row["node"]["instruction_id"] == "ir_process"
        and row["property"] == "cardinality" and row["path"] == []
        for row in result["derivations"].values())


@pytest.mark.parametrize("content", [LiteralContent(value=[]), OpaqueContent(),
                                     LiteralContent(value=["same", "same"])])
def test_empty_unknown_and_repeated_members_preserve_collection_identity(content):
    facts, task, annotation, candidate, engine = fixture(
        path=["rows", EACH, "url"], customize=wrap_records, collection_content=content)
    result = engine.solve()
    assert not any(d["code"] in {"nested_collection_scope", "path_widening"}
                   for d in result["diagnostics"])
    assert prepare_demand_review(facts, task, annotation, candidate).to_dict() == result
    scopes = {tuple(row["node"]["scope"]) for row in result["derivations"].values()
              if row["node"]["kind"] == "element"}
    if isinstance(content, LiteralContent):
        assert len(scopes) == len(content.value)
    else:
        assert len(scopes) == 1  # One symbolic scope, not a known cardinality.


def test_member_selector_cannot_match_a_sibling_field_or_literal_star():
    demand = {"property": "value", "path": ["rows", EACH, "key"], "each": False,
              "excluded_paths": [], "conservative": False}
    def signal(path):
        return {"property": "value", "path": path, "excluded_paths": []}
    assert demand_overlap(signal(["rows", 0, "key"]), demand) == "retain"
    assert demand_overlap(signal(["rows", 1, "secret"]), demand) == "none"
    assert demand_overlap(signal(["other", 0, "key"]), demand) == "none"
    assert demand_overlap(signal(["rows", "*", "key"]), demand) == "none"


def test_selecting_collection_prepends_real_prefix_to_root_each():
    values = operation_fixture([
        {"op": "select_part", "input": inp(), "path": ["report", "rows"], "output": "rows"}])
    engine, result = solve(values, path=[EACH, "key"])
    rows = input_demands(engine, result, "select_part")
    assert rows and all(row["path"] == ["report", "rows", EACH, "key"]
                        and not row["each"] and not row["conservative"] for row in rows)


def test_nested_list_build_demands_each_known_member_without_sibling_payload():
    values = operation_fixture([
        {"op": "build", "container": "list", "output": "rows", "parts": [
            {"path": [0], "value": inp()}, {"path": [1], "value": literal({"key": 2})}]},
        {"op": "build", "container": "object", "output": "wrapped", "parts": [
            {"path": ["rows"], "value": local("rows")},
            {"path": ["private"], "value": literal("unused")}]},
    ])
    engine, result = solve(values, path=["rows", EACH, "key"])
    rows = input_demands(engine, result, "build")
    assert any(row["path"] == ["key"] and not row["each"] for row in rows)
    assert not any(row["node"]["slot"] == 1
                   and engine.ops[row["node"]["operation_id"]]["spec"].get("container") == "object"
                   for row in result["derivations"].values() if row["node"]["kind"] == "op_input")


def test_prefixed_each_update_keeps_other_occurrences_and_their_field_prefix():
    values = operation_fixture([
        {"op": "update_fields", "input": inp(), "updates": [
            {"path": ["rows", 0, "key"], "value": literal("replacement")}], "output": "changed"}])
    engine, result = solve(values, path=["rows", EACH, "key"])
    changed = input_demands(engine, result, "update_fields", slot=1)
    original = input_demands(engine, result, "update_fields")
    assert changed and all(r["path"] == [] and not r["each"] for r in changed)
    assert original and all(r["path"] == ["rows", EACH, "key"]
                           and ["rows", 0, "key"] in r["excluded_paths"] for r in original)
    assert demand_overlap({"path": ["rows", 0, "key"], "property": "value", "excluded_paths": []}, original[0]) == "none"
    assert demand_overlap({"path": ["rows", 1, "key"], "property": "value", "excluded_paths": []}, original[0]) == "retain"


def test_root_each_with_one_concrete_exclusion_retains_exact_exclusion():
    values = operation_fixture([
        {"op": "exclude_parts", "input": inp(), "paths": [[0, "secret"]], "output": "trimmed"}])
    engine, result = solve(values, path=[EACH])
    original = input_demands(engine, result, "exclude_parts")
    assert original and all(r["path"] == [EACH] and not r["each"]
                           and r["excluded_paths"] == [[0, "secret"]] for r in original)
    assert demand_overlap({"path": [0, "secret"], "property": "value", "excluded_paths": []}, original[0]) == "none"
    assert demand_overlap({"path": [1, "secret"], "property": "value", "excluded_paths": []}, original[0]) == "retain"


def test_known_output_index_returns_demand_to_only_the_same_input_occurrence():
    _, _, _, _, engine = fixture(path=["rows", 0, "url"], customize=wrap_records,
                                 collection_content=LiteralContent(value=["same", "same"]))
    result = engine.solve()
    value_inputs = [r for r in result["derivations"].values()
                   if r["node"]["kind"] == "ir_input" and r["node"]["instruction_id"] == "ir_process"
                   and r["property"] == "value"]
    assert value_inputs and all(r["path"] == [0] and not r["each"] for r in value_inputs)


def test_prefixed_demand_is_not_transferred_to_another_recipient_of_the_same_value():
    def two_recipients(raw, citation):
        wrap_records(raw, citation)
        raw["locations"]["archive"] = {**raw["locations"]["saved"], "name": "archive.json"}
        raw["location_evidences"]["archive"] = [citation]
        tail = raw["ir_semantics"]["ir_process"]["events"][1]["events"][0]["atomic_ops"]
        tail.append({"op": "write", "target": "archive", "mode": "replace",
                     "input": local("response_wrapper"), "evidences": [citation]})
    _, _, _, _, engine = fixture(path=["rows", EACH, "url"], customize=two_recipients)
    result = engine.solve()
    saved = next(s for s in result["sinks"] if s["boundary"]["target"] == "saved")
    archive = next(s for s in result["sinks"] if s["boundary"]["target"] == "archive")
    assert saved["actual_payload"][0]["inputs"] == archive["actual_payload"][0]["inputs"]
    assert saved["related_requirements"] == ["R"]
    assert archive["related_requirements"] == []
    assert archive["demanded_information"] == archive["conservative_retention"] == []
