"""Partial facts and explicit expected values cannot bypass demand tracing."""
from copy import deepcopy

from skillflow.doe.demand_material import prepare_demand_review
from skillflow.propagation.facts import resolved_sink_boundaries
from tests.doe.test_demand_engine import fixture, inp, candidate, literal
from tests.doe.test_demand_engine import local, solve, target_id, sink_demands
from tests.doe.test_demand_engine import set_operator


def test_missing_producer_does_not_reuse_a_downstream_original_output():
    facts, task, annotation, targets = fixture([
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])
    facts = deepcopy(facts)
    del facts.records["ir_filter"]
    facts.coverage["ir_filter"] = "unresolved_binding"
    facts.status = "incomplete"
    facts.diagnostics = [{"code": "unresolved_binding", "instruction_id": "ir_filter",
                              "reason": "The producer did not form a resolved record."}]
    facts.sinks = resolved_sink_boundaries(facts.locations, facts.records)
    result = prepare_demand_review(facts, task, annotation, candidate(targets)).to_dict()
    assert result["status"] == "partial"
    assert any(row["code"] == "missing_local_record" for row in result["diagnostics"])
    assert not any(row["node"]["kind"] == "op_input" and row["node"]["instruction_id"] == "ir_filter"
                   for row in result["derivations"].values())


def test_expected_relation_on_real_return_operand_is_checked():
    facts, task, annotation, targets = fixture([
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])
    requested = candidate(targets)
    requested["goals"][0]["expected"] = literal("different required value")
    result = prepare_demand_review(facts, task, annotation, requested).to_dict()
    assert result["status"] == "partial"
    assert any(row["code"] == "expected_relation_mismatch" for row in result["diagnostics"])
    assert not any(row["node"]["kind"] == "ir_input" and row["node"]["instruction_id"] == "ir_return"
                   for row in result["derivations"].values())


def test_unchanged_public_local_return_keeps_its_declared_observation():
    def copy_output(prepared, raw, ev):
        raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = inp()
    facts, task, annotation, targets = fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "unused"}],
        mode="local", returned=[inp()], custom=copy_output)
    result = prepare_demand_review(facts, task, annotation, candidate(targets, path=["body"])).to_dict()
    observations = [s for s in result["sinks"] if s["boundary"]["sink_type"] == "model_observe"]
    assert observations and all(s["demanded_information"] for s in observations)
    assert all(result["derivations"][k]["path"] == ["body"]
               for s in observations for k in s["demanded_information"])
    assert not any("opaque_computation" in d["rules"] for d in result["derivations"].values())


def test_element_demand_through_a_constructed_list_reaches_original_member():
    def deliver_each(prepared, raw, ev):
        set_operator(raw, prepared, "ir_filter", ["llm"])
        raw["locations"]["notify"] = {"kind": "tool", "name": "notify", "operand_refs": [],
                                       "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["notify"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"].append({"kind": "for_each", "collection": local("rows"), "item": "row",
            "evidences": deepcopy(ev), "body": [{"kind": "processing", "mode": "model", "returns": [], "evidences": deepcopy(ev),
                "events": [{"effect": "transform", "evidences": deepcopy(ev), "atomic_ops": [{"op": "select_part", "input": local("row"),
                    "path": ["body"], "output": "body", "evidences": deepcopy(ev)}]},
                    {"effect": None, "evidences": [], "atomic_ops": [{"op": "deliver", "inputs": [local("body")], "target": "notify", "evidences": deepcopy(ev)}]}]}]})
    values = fixture([{"op": "build", "parts": [{"path": [0], "value": inp()}], "container": "list", "output": "rows"}],
                     mode="model", custom=deliver_each)
    requested = candidate(values[3], goal_target=target_id(values[3], "input_use", op="deliver", slot=0))
    engine, result = solve(values, requested)
    rows = [row for row in sink_demands(result) if engine.ops[row["node"]["operation_id"]]["scope"] is None]
    assert rows and any(row["path"] == ["body"] and not row["each"] for row in rows)


def test_actual_whole_argument_does_not_become_the_required_original_field():
    def send_whole(prepared, raw, ev):
        raw["locations"]["notify"] = {"kind": "tool", "name": "notify", "operand_refs": [],
                                       "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["notify"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"][0]["events"].append({"effect": None, "evidences": [], "atomic_ops": [
            {"op": "deliver", "inputs": [inp()], "target": "notify", "evidences": deepcopy(ev)}]})
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "unused"}], custom=send_whole)
    requested = candidate(values[3], goal_target=target_id(values[3], "input_use", op="deliver", slot=0))
    requested["goals"][0].update(expected=inp(), expected_path=["body"])
    _, result = solve(values, requested)
    rows = sink_demands(result, "external_tool")
    assert rows and all(row["path"] == ["body"] for row in rows)
    assert result["status"] == "partial"
    assert any(row["code"] == "expected_relation_projection" for row in result["diagnostics"])
