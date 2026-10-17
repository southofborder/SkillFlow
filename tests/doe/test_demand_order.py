"""Backward storage demand follows may order and reaching versions."""
from copy import deepcopy

from tests.doe.test_demand_engine import fixture, inp, literal, local, solve
from tests.doe.test_demand_engine import set_operator


def memory_case(*, partial=False, weak=False, delete=False):
    def change(prepared, raw, evidence):
        raw["locations"]["cache"] = {"kind": "storage", "name": "cache", "operand_refs": [],
                                      "access_scope": "task", "retention": "persistent"}
        raw["location_evidences"]["cache"] = deepcopy(evidence)
        second_target = "cache"
        if weak:
            second_target = "dynamic"
            raw["locations"]["dynamic"] = {"kind": "storage", "name": "symbolic:destination", "operand_refs": [],
                                            "access_scope": "task", "retention": "persistent"}
            raw["location_evidences"]["dynamic"] = deepcopy(evidence)
        operations = [
            {"op": "write", "mode": "replace", "target": "cache", "input": inp()},
            ({"op": "write", "mode": "delete", "target": "cache"} if delete else
             {"op": "write", "mode": "replace", "target": second_target,
              "input": literal({"body": "new", "secret": "not a task payload"})})]
        effects = ["fs_write", "fs_write"]
        if not delete:
            operations.append({"op": "read", "location": "cache", "output": "saved"})
            effects.append("fs_read")
        set_operator(raw, prepared, "ir_filter", ["agent_runtime"])
        spec = raw["ir_semantics"]["ir_filter"]
        spec["order"] = "partial" if partial else "fixed"
        # Separate segments preserve only each segment's local order. A partial
        # timeline must not manufacture cross-segment write-before-read edges.
        spec["events"] = [{"kind": "processing", "mode": "local", "returns": [], "evidences": deepcopy(evidence),
                           "events": [{"effect": effects[i], "evidences": deepcopy(evidence), "atomic_ops": [{**op, "evidences": deepcopy(evidence)}]}]}
                          for i, op in enumerate(operations)]
        spec["output_bindings"][0]["value"] = literal("done") if delete else local("saved")
    return fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "unused"}],
                   mode="local", custom=change)


def storage_sinks(result):
    return [sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "storage_write"]


def test_partial_order_keeps_both_possible_writes_instead_of_last_array_write():
    values = memory_case(partial=True)
    engine, result = solve(values, path=["body"])
    sinks = storage_sinks(result)
    assert len(sinks) == 2
    assert all(sink["demanded_information"] or sink["conservative_retention"] for sink in sinks)
    read = next(op for op in engine.ops.values() if op["position"]["instruction_id"] == "ir_filter" and op["spec"]["op"] == "read")
    assert len(read["record"]["outputs"][0]) >= 2
    assert values[0].records["ir_filter"]["order"] == "partial"


def test_weak_alias_write_keeps_old_and_new_saved_value_demands():
    values = memory_case(weak=True)
    engine, result = solve(values, path=["body"])
    sinks = storage_sinks(result)
    assert len(sinks) == 2
    for sink in sinks:
        op = engine.ops[sink["actual_payload"][0]["operation_id"]]
        rows = [result["derivations"][key] for key in sink["demanded_information"] + sink["conservative_retention"]]
        assert rows and all(row["path"] == ["body"] for row in rows)
        if op["spec"]["target"] == "dynamic":
            assert all(row["conservative"] for row in rows)
            assert any(change["update"] == "weak" and change["location"]["name"] == "cache"
                       for change in op["record"]["changes"])


def test_definite_delete_kills_prior_reaching_write_without_deleting_registry_data():
    values = memory_case(delete=True)
    engine, result = solve(values)
    assert ("storage", "cache") not in engine.index.entry_writes["ir_return"]
    writes = [op for op in engine.ops.values() if op["spec"]["op"] == "write"]
    original_ids = next(op["record"]["inputs"][0] for op in writes if op["spec"]["mode"] == "replace")
    assert set(original_ids) <= {data["id"] for data in values[0].data}
    assert any(change["update"] == "delete" and not change["after"]
               for op in writes for change in op["record"]["changes"])
    sinks = storage_sinks(result)
    assert len(sinks) == 1  # Removal does not become a content-save sink.
    assert not sinks[0]["demanded_information"] and not sinks[0]["conservative_retention"]
