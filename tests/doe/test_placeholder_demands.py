"""Check the source-backed symbolic operation across propagation, demand and DOE."""
import pytest

from skillflow.doe.constraint_engine import ConstraintEngine
from tests.doe.test_demand_engine import candidate, evidence, fixture, inp, literal, local, solve, input_demands
from tests.doe.test_reviewed_input_necessity import assessed, compute, operation_key, row, rule, solve as reviewed
from tests.doe.test_sensitivity_engine import review, rows


def placeholder(inputs, *, output=None):
    op = {"op": "placeholder", "inputs": inputs, "kind": "effect" if output is None else "value", "evidences": [evidence()],
          "reason": "The callback implementation is unavailable in this source file."}
    return op if output is None else {**op, "output": output}


def test_symbolic_result_only_blocks_the_report_field_that_demands_it():
    values = fixture([
        {"op": "select_part", "input": inp(), "path": ["token"], "output": "secret"},
        placeholder([local("secret")], output="callback"),
        {"op": "build", "container": "object", "parts": [
            {"path": ["known"], "value": literal(1)}, {"path": ["unknown"], "value": local("callback")}],
         "output": "report"}], expected_status="incomplete")
    for field in ("known", "unknown"):
        engine, result = solve(values, path=[field])
        assert result["coverage"]["upstream"]["ir_filter"] == "processed_with_placeholder"
        assert result["coverage"]["upstream"]["ir_return"] == "processed"
        diagnostic = [d for d in result["diagnostics"] if d["code"] == "input_contract_placeholder"]
        inputs = input_demands(engine, result, "placeholder")
        if field == "known":
            assert not diagnostic and not inputs
            assert result["status"] == "complete"
        else:
            assert diagnostic and diagnostic[0]["affected_instruction_ids"] == ["ir_filter"]
            assert inputs and all(d["conservative"] for d in inputs)
            assert {tuple(d["path"]) for d in input_demands(engine, result, "select_part")} == {("token",)}
            assert result["status"] == "partial"


def test_unknown_logging_does_not_disable_reviewed_three_input_deletion():
    values = fixture([placeholder([inp()]),
        compute([inp(), literal({"b": 2}), literal({"c": 3})],
                [rule([], [row(0, ["a"]), row(1, ["b"]), row(2)])])],
        mode="model", expected_status="incomplete")
    engine, result = reviewed(values)
    key = operation_key(engine)
    assert len(engine.ops[key]["record"]["inputs"]) == 3
    assert all(any(r["status"] == "required" for r in assessed(result, key, slot)["ranges"]) for slot in (0, 1))
    assert any(r["status"] == "deletable" and not r["excluded_paths"] for r in assessed(result, key, 2)["ranges"])
    assert not any(d["code"] == "input_contract_placeholder" for d in result["diagnostics"])


def test_possible_value_influence_never_implies_copied_original_content():
    values = fixture([placeholder([inp()], output="maybe")], mode="local", returned=[local("maybe")],
                     expected_status="incomplete")
    examined = rows(review(values, requested=candidate(values[3])))
    assert examined and {r["relation"] for r in examined} == {"possible"}
    assert all(r["conclusion"] != "excess_supported" for r in examined)


@pytest.mark.parametrize("overwrite", [False, True])
def test_read_only_depends_on_symbolic_write_while_its_version_reaches_it(overwrite):
    def configure(prepared, raw, ev):
        raw["locations"]["cache"] = {"kind": "storage", "name": "cache", "operand_refs": [],
                                     "access_scope": "task", "retention": "persistent"}
        raw["location_evidences"]["cache"] = ev
        write = {"op": "write", "input": literal("baseline"), "mode": "replace", "target": "cache"}
        weak = {**placeholder([inp()]), "may_write": True, "location": "cache"}
        operations = [("fs_write", write), (None, weak)]
        if overwrite:
            operations.append(("fs_write", {**write, "input": literal("fresh")}))
        operations.append(("fs_read", {"op": "read", "location": "cache", "output": "last"}))
        segment = raw["ir_semantics"]["ir_filter"]["events"][0]
        segment["events"] = [{"effect": effect, "evidences": ev if effect else [],
                              "atomic_ops": [{"evidences": ev, **op}]} for effect, op in operations]
    values = fixture([{"op": "select_part", "input": inp(), "path": ["token"], "output": "last"}],
                     custom=configure, expected_status="incomplete")
    engine, demand = solve(values)
    key = operation_key(engine, "placeholder")
    links = [link for link in engine.index.links.values() if link["source"] == key]
    assert bool(links) != overwrite
    if links:
        assert set(links[0]["data_ids"]) == set(engine.ops[key]["record"]["possible_writes"])
    inputs = input_demands(engine, demand, "placeholder")
    assert bool(inputs) != overwrite and all(row["conservative"] for row in inputs)
    assert all(sink["boundary"]["op_index"] != engine.ops[key]["position"]["op_index"]
               or sink["boundary"]["event_index"] != engine.ops[key]["position"]["event_index"]
               for sink in demand["sinks"] if sink["boundary"]["instruction_id"] == "ir_filter")


def test_possible_receiver_blocks_only_a_constraint_at_its_declared_endpoint():
    def configure(prepared, raw, ev):
        for name in ("logger", "other"):
            raw["locations"][name] = {"kind": "remote", "name": name, "access_scope": "recipient",
                                      "retention": None, "operand_refs": []}
            raw["location_evidences"][name] = ev
    values = fixture([{**placeholder([inp()]), "location": "logger"},
                      {"op": "select_part", "input": inp(), "path": ["body"], "output": "last"}],
                     custom=configure, expected_status="incomplete")
    engine, _ = solve(values)
    for name in ("other", "logger"):
        constraint = {"kind": "forbid_information", "scope": {"kind": "task"}, "events": None,
                      "receivers": {"kind": "locations", "ids": [name]},
                      "source": {"instruction_id": "ir_filter", "scope_path": [], "value": inp()},
                      "path": ["token"]}
        engine.raw["realizations"][0]["constraints"] = [constraint]
        engine.compiled["realizations"][0]["constraints"] = [constraint]
        check, = ConstraintEngine(engine).check().values()
        if name == "other":
            assert check["status"] == "satisfied"
        else:
            assert check["status"] in {"potential_violation", "not_established"}
            assert any("possible" in reason for reason in check["reasons"])
