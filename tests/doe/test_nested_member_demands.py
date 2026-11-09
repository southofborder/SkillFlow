"""Nested member demands retain source fields, receivers and cardinality."""
import pytest
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.sensitivity_engine import demand_overlap, range_presence
from skillflow.doe.sensitivity_material import prepare_sensitivity_review
from skillflow.propagation.data import Data, LiteralContent
from tests.doe.test_demand_engine import fixture, solve, input_demands, inp, local
from tests.doe.test_map_collection import fixture as map_fixture


EACH = {"kind": "each"}


def _wrap_nested(raw, citation):
    """Wrap each acquired record in an inner list, then in outer groups."""
    spec = raw["ir_semantics"]["ir_process"]
    body = spec["events"][0]["body"][0]["events"][-1]["atomic_ops"]
    body.append({"op": "build", "container": "list", "output": "inner_rows",
        "parts": [{"path": [0], "value": local("record")}], "evidences": [citation]})
    body.append({"op": "build", "container": "object", "output": "group",
        "parts": [{"path": ["rows"], "value": local("inner_rows")}], "evidences": [citation]})
    spec["events"][0]["yield"] = local("group")


def test_nested_output_demand_passes_only_selected_fields_to_each_yield():
    facts, task, annotation, candidate, engine = map_fixture(
        path=[EACH, "rows", EACH, "url"], customize=_wrap_nested)
    result = prepare_demand_review(facts, task, annotation, candidate).to_dict()
    assert result == DemandEngine(facts, task, annotation, candidate, engine.targets).solve(queue_order="lifo")
    assert not any(d["code"] in {"nested_member_demand", "path_widening"} for d in result["diagnostics"])
    rows = [r for r in result["derivations"].values() if r["node"]["kind"] == "op_input"
        and engine.ops[r["node"]["operation_id"]]["spec"].get("output") == "record"]
    assert rows and {r["node"]["slot"] for r in rows} == {0}
    assert not any(r["node"]["kind"] == "op_output"
        and engine.ops[r["node"]["operation_id"]]["spec"]["op"] == "receive"
        for r in result["derivations"].values())
    reviewed = prepare_sensitivity_review(facts, task, annotation, candidate).to_dict()
    saved = next(s for s in reviewed["sinks"] if s["boundary"]["sink_type"] == "storage_write")
    assert {tuple(r["reduction"]["path"]) for r in saved["data_reviews"]} == {
        (0, "rows", 0, "response", "token"), (1, "rows", 0, "response", "token")}
    assert {r["conclusion"] for r in saved["data_reviews"]} == {"excess_supported"}


def test_nested_cardinality_does_not_require_inner_payload():
    _, _, _, _, engine = map_fixture(
        preserve="cardinality", path=[EACH, "rows"], customize=_wrap_nested)
    result = engine.solve()
    assert not any(r["node"]["kind"] == "op_input"
        and engine.ops[r["node"]["operation_id"]]["spec"].get("output") == "record"
        for r in result["derivations"].values())


def test_two_member_levels_preserve_exclusion_identity():
    path = ["groups", EACH, "rows", EACH, "secret"]
    values = fixture([{"op": "exclude_parts", "input": inp(),
        "paths": [["groups", 0, "rows", 1, "secret"]], "output": "trimmed"}])
    engine, result = solve(values, path=path)
    rows = input_demands(engine, result, "exclude_parts")
    assert rows and all(row["path"] == path for row in rows)
    def overlap(group, row):
        return demand_overlap({"property": "value", "path": ["groups", group, "rows", row, "secret"],
            "excluded_paths": []}, rows[0])
    assert overlap(0, 1) == "none"
    assert overlap(0, 0) == "retain"
    assert overlap(1, 1) == "retain"


@pytest.mark.parametrize("coverage,unresolved", [("not_solved", True), ("not_reached", False)])
def test_declared_but_unevaluated_collection_does_not_fabricate_member_node(coverage, unresolved):
    facts, task, annotation, candidate, original = map_fixture()
    facts.records = {}
    facts.sinks = []
    facts.coverage = {ir: coverage for ir in facts.coverage}
    facts.status = "unsupported_feedback"
    result = prepare_demand_review(facts, task, annotation, candidate).to_dict()
    assert any(d["code"] == "missing_collection_record" for d in result["diagnostics"]) is unresolved
    assert all(r["node"]["kind"] != "collection_output" for r in result["derivations"].values())
    assert result["sinks"] == []


def test_nested_each_presence_distinguishes_empty_absent_and_present():
    def value(content):
        return {"x": Data(id="x", content=LiteralContent(value=content)).model_dump(mode="json")}
    path = [EACH, "rows", EACH, "token"]
    assert range_presence(value([]), "x", path) == "empty"
    assert range_presence(value([{"rows": []}]), "x", path) == "empty"
    assert range_presence(value([{"rows": [{"token": "one"}]}]), "x", path) == "present"
    assert range_presence(value([{"rows": [{"other": "one"}]}]), "x", path) == "absent"


def test_missing_collection_scope_keeps_independent_branch_excess_comparison():
    from tests.doe.test_processing_limits import authored, model_rows, segment, CITATION
    from skillflow.propagation.annotation.compiler import compile_response
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    material, raw = authored()
    blocked = raw["ir_semantics"]["ir_late"]
    blocked["events"] = [{"kind": "for_each", "collection": {"kind": "literal", "value": [{"token": "s"}]},
        "item": "entry", "evidences": [CITATION], "body": [segment("transform", {
            "op": "select_part", "input": local("entry"), "path": ["token"], "output": "token"})],
        "yield": local("token"), "output": "tokens"}]
    blocked["output_bindings"][0]["value"] = local("tokens")
    checked, compiled, mapping = compile_response(raw, material)
    result = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(result, material=material, raw_annotation=checked,
                                  compiled_annotation=compiled, mapping=mapping)
    reviewed = prepare_sensitivity_review(facts, annotation=facts.annotation)
    assert result.coverage["ir_late"] != "processed"
    assert any(row["code"] == "missing_collection_record" for row in reviewed.demand_dict()["diagnostics"])
    assert model_rows(reviewed) and {row["conclusion"] for row in model_rows(reviewed)} == {"excess_supported"}
