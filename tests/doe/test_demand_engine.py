"""Backward requirements stay attached to actual processing and receivers."""
from copy import deepcopy

import pytest

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.demand import validate_demand_candidate
from skillflow.propagation.contracts.task import Task, task_source_files
from skillflow.propagation.loading import materials_from_result
from tests.doe.components import mutable_components
from skillflow.propagation.solver import propagate
from skillflow.propagation.material import prepare_material
from tests.propagation.annotation.helpers import material, valid_raw_response


def set_operator(raw, prepared, instruction_id, operators):
    spec = raw["ir_semantics"][instruction_id]
    spec["operator"] = list(operators)
    spec["operator_evidences"] = [{"value": value,
        "target": {"instruction_id": instruction_id, "path": []},
        "reason": "The fixture explicitly assigns the processing participant."}
        for value in (operators or [None])]


def inp(index=0):
    return {"kind": "input", "index": index}


def local(name):
    return {"kind": "local", "name": name}


def literal(value):
    return {"kind": "literal", "value": value}


def evidence():
    return {"file": "skill/SKILL.md", "start_line": 3, "end_line": 3,
            "reason": "The offline fixture associates this expression with the frozen source."}


def fixture(operations, *, mode="default", returned=None, custom=None, graph_change=None):
    prepared = material()
    from tests.doe.helpers import source_task
    task = source_task(prepared["source"])
    prepared = prepare_material(prepared["source"], prepared["cfg"], task_baseline=task)
    if graph_change:
        cfg = deepcopy(prepared["cfg"])
        graph_change(cfg)
        prepared = prepare_material(prepared["source"], cfg, task_baseline=task)
    raw = valid_raw_response(prepared)
    raw["demands"] = [{"requirement_id": "R", "target": {"instruction_id": "ir_return", "side": "input", "index": 0},
        "preserve": "value", "reason": "独立算法样例显式保持真实返回值。"}]
    raw["realizations"] = [{"requirement_id": "R", "status": "expressed", "bindings": [], "gaps": []}]
    segment = raw["ir_semantics"]["ir_filter"]["events"][0]
    ev = deepcopy(segment["evidences"])
    operations = [{**op, "evidences": deepcopy(ev)} for op in operations]
    segment.update(mode=mode, returns=[] if returned is None else returned)
    segment["events"][0]["atomic_ops"] = operations
    set_operator(raw, prepared, "ir_filter", ["llm"] if mode == "model" else ["agent_runtime"])
    raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = local(operations[-1]["output"])
    if custom:
        custom(prepared, raw, ev)
    checked, compiled, mapping = compile_response(raw, prepared)
    payload = to_payload(compiled)
    solved = propagate(prepared["cfg"], payload)
    assert solved.status == "complete", solved.diagnostics
    metadata = {"files": [{"path": row["path"], "size": len(row["content"].encode()), "kind": "markdown",
                            "raw_sha256": row["sha256"], "decoded_sha256": row["sha256"]}
                           for row in prepared["source"]["files"]],
                "boundaries": {"binary_files": [], "uninterpreted_code_files": [], "notice": "Offline symbolic fixture."}}
    facts = mutable_components(materials_from_result(solved, material=prepared, raw_annotation=checked,
        compiled_annotation=compiled, mapping=mapping, source_metadata=metadata))
    annotation = facts.annotation
    targets = build_demand_target_index(facts.cfg, checked)
    return facts, task, annotation, targets


def target_id(targets, kind, *, ir="ir_filter", op=None, slot=None):
    for identity, target in targets.items():
        if target.get("instruction_id") != ir or target["kind"] != kind:
            continue
        if slot is not None and target.get("slot") != slot:
            continue
        if op is not None:
            path = target.get("operation_raw_path", target["raw_path"])
            operation = next((t["value"] for t in targets.values() if t["kind"] == "operation"
                             and t.get("instruction_id") == ir and t["raw_path"] == path), None)
            if operation is None or operation["op"] != op:
                continue
        return target["target"]
    raise AssertionError((kind, ir, op, slot))


def candidate(targets, *, property="value", path=(), expression=None, expression_op="compute", goal_target=None):
    result = {"goals": [{"id": "G", "requirement_id": "R", "preserve": property,
                           "target": goal_target or target_id(targets, "input", ir="ir_return"),
                           "path": list(path), "reason": "Keep the required result under the declared operations."}],
              "expressions": []}
    if expression:
        result["expressions"].append({"target": target_id(targets, "operation", op=expression_op),
                                      "expression": expression, "evidences": [evidence()]})
    return result


def solve(values, requested=None, **kwargs):
    facts, task, annotation, targets = values
    requested = requested or candidate(targets, **kwargs)
    checked = validate_demand_candidate(requested, task, task_source_files(facts.source), targets)
    engine = DemandEngine(facts, task, annotation, checked.model_dump(mode="json"), targets)
    result = engine.solve()
    other = DemandEngine(facts, task, annotation, checked.model_dump(mode="json"), targets).solve(queue_order="lifo")
    assert result == other
    return engine, result


def input_demands(engine, result, op, *, ir="ir_filter", slot=0):
    return [row for row in result["derivations"].values()
            if row["node"]["kind"] == "op_input" and row["node"]["instruction_id"] == ir
            and row["node"]["slot"] == slot
            and engine.ops[row["node"]["operation_id"]]["spec"]["op"] == op]


def sink_demands(result, sink_type="model_observe"):
    return [result["derivations"][key] for sink in result["sinks"] if sink["boundary"]["sink_type"] == sink_type
            for key in sink["demanded_information"] + sink["conservative_retention"]]


def test_selected_field_reaches_model_without_promoting_parent_or_registry():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}], mode="model")
    before = deepcopy(values[0])
    engine, result = solve(values)
    assert {tuple(d["path"]) for d in input_demands(engine, result, "select_part")} == {("body",)}
    observed = sink_demands(result)
    assert observed and all(d["path"] == ["body"] for d in observed)
    assert values[0].data == before.data and values[0].records == before.records
    # Keeping the complete parent as a source explanation creates no extra
    # field demand and no additional receiver input channel.
    assert any(d["content"]["form"] == "known_parts" for d in values[0].data)
    public = prepare_demand_review(values[0], values[1], values[2], candidate(values[3])).to_dict()
    assert public == result


@pytest.mark.parametrize("mode", ["default", "model"])
def test_model_filter_retains_predicate_field_while_count_needs_structure(mode):
    values = fixture([
        {"op": "filter_items", "input": inp(), "predicate": "enabled is true", "output": "selected"},
        {"op": "compute", "inputs": [local("selected")], "dependencies": ["derived"], "output": "n"}], mode=mode)
    cand = candidate(values[3], expression={"op": "count", "arg": {"op": "ref", "value": local("selected")}})
    cand["expressions"].append({"target": target_id(values[3], "operation", op="filter_items"),
        "expression": {"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["enabled"]}, "evidences": [evidence()]})
    _, result = solve(values, cand)
    observed = sink_demands(result)
    assert any(d["path"] == ["enabled"] and d["property"] == "truth" for d in observed)
    assert any(d["property"] == "cardinality" for d in observed)
    assert not any(d["path"] == ["token"] for d in observed)
    assert not any(d["property"] == "value" and d["path"] == [] for d in observed)


def test_local_filter_observes_only_returned_version():
    values = fixture([{"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"}],
                     mode="local", returned=[local("clean")])
    engine, result = solve(values)
    observed = sink_demands(result)
    assert len(observed) == 1
    actual = {d for sink in result["sinks"] for instance in sink["actual_payload"] for slot in instance["inputs"] for d in slot}
    original = next(op for op in engine.ops.values() if op["spec"]["op"] == "exclude_parts")["record"]["inputs"][0]
    assert not set(original) & actual
    source_needs = input_demands(engine, result, "exclude_parts")
    assert source_needs and all(["token"] in d["excluded_paths"] for d in source_needs)


def test_exclude_and_update_do_not_resurrect_old_fields():
    values = fixture([
        {"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"},
        {"op": "update_fields", "input": local("clean"), "updates": [{"path": ["body"], "value": literal("replacement")}], "output": "updated"}])
    engine, result = solve(values)
    originals = input_demands(engine, result, "exclude_parts")
    assert originals and all({("token",), ("body",)} <= {tuple(p) for p in d["excluded_paths"]} for d in originals)
    replacement = input_demands(engine, result, "update_fields", slot=1)
    assert replacement and all(d["property"] == "value" for d in replacement)


def test_update_demand_for_new_field_does_not_read_old_field():
    values = fixture([{"op": "update_fields", "input": inp(), "updates": [{"path": ["body"], "value": literal("replacement")}], "output": "updated"}])
    engine, result = solve(values, path=["body"])
    assert not input_demands(engine, result, "update_fields", slot=0)
    assert input_demands(engine, result, "update_fields", slot=1)


def test_build_keeps_only_requested_member_and_its_control():
    values = fixture([{"op": "build", "parts": [
        {"path": ["body"], "value": inp(), "when": literal(True)},
        {"path": ["other"], "value": literal("not requested")}], "container": "object", "output": "request"}])
    engine, result = solve(values, path=["body"])
    assert input_demands(engine, result, "build", slot=0)[0]["property"] == "truth"
    assert input_demands(engine, result, "build", slot=1)[0]["property"] == "value"
    assert not input_demands(engine, result, "build", slot=2)


@pytest.mark.parametrize("property,path,expected", [
    ("cardinality", ["rows"], []),
    ("shape", ["rows"], []),
    ("presence", ["rows", "secret"], ["secret"]),
])
def test_built_member_properties_flow_into_actual_member_value(property, path, expected):
    values = fixture([{"op": "build", "parts": [{"path": ["rows"], "value": inp()}],
                       "container": "object", "output": "wrapped"}])
    engine, result = solve(values, property=property, path=path)
    rows = input_demands(engine, result, "build")
    assert rows and all(row["property"] == property and row["path"] == expected for row in rows)
    assert sink_demands(result)


def test_count_does_not_require_every_member_value_or_authorize_integer_replacement():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "n"}])
    engine, result = solve(values, expression={"op": "count", "arg": {"op": "ref", "value": inp()}})
    needs = input_demands(engine, result, "compute")
    assert needs and {d["property"] for d in needs} == {"cardinality"}
    assert {d["property"] for d in sink_demands(result)} == {"cardinality"}
    assert all("replacement" not in d for d in result["derivations"].values())


def test_opaque_calculation_conservatively_retains_inputs_without_necessity_verdict():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "opaque"}])
    engine, result = solve(values)
    rows = input_demands(engine, result, "compute")
    assert rows and all(row["conservative"] and row["path"] == [] for row in rows)
    assert sink_demands(result) and all(row["conservative"] for row in sink_demands(result))
    assert not any("necessary" in row or "minimal_fields" in row for row in result["derivations"].values())


def test_filter_requirement_reaches_model_but_not_notification_payload():
    def change(prepared, raw, ev):
        set_operator(raw, prepared, "ir_filter", ["llm"])
        raw["locations"]["notify"] = {"kind": "tool", "name": "notification boundary", "operand_refs": [],
                                       "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["notify"] = deepcopy(ev)
        spec = raw["ir_semantics"]["ir_filter"]
        spec["events"].append({"kind": "for_each", "collection": local("selected"), "item": "row", "evidences": deepcopy(ev),
            "body": [{"kind": "processing", "mode": "model", "returns": [], "evidences": deepcopy(ev), "events": [
                {"effect": "transform", "evidences": deepcopy(ev), "atomic_ops": [
                    {"op": "select_part", "input": local("row"), "path": ["recipient"], "output": "recipient", "evidences": deepcopy(ev)},
                    {"op": "select_part", "input": local("row"), "path": ["summary"], "output": "summary", "evidences": deepcopy(ev)}]},
                {"effect": None, "evidences": [], "atomic_ops": [{"op": "deliver", "inputs": [local("recipient"), local("summary")],
                     "target": "notify", "evidences": deepcopy(ev)}]}]}]})
    values = fixture([{"op": "filter_items", "input": inp(), "predicate": "urgent is true", "output": "selected"}], mode="model", custom=change)
    targets = values[3]
    cand = candidate(targets, expression={"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["urgent"]},
                     expression_op="filter_items", goal_target=target_id(targets, "input_use", op="deliver", slot=0))
    cand["goals"].append({**cand["goals"][0], "id": "G2", "target": target_id(targets, "input_use", op="deliver", slot=1)})
    _, result = solve(values, cand)
    observed = sink_demands(result)
    assert any(row["path"] == ["urgent"] for row in observed)
    notification = sink_demands(result, "external_tool")
    assert notification and not any(row["path"] == ["urgent"] for row in notification)
    assert not any(row["path"] == ["token"] for row in observed)


def test_removed_required_field_is_diagnostic_not_recovered_from_parent():
    values = fixture([{"op": "exclude_parts", "input": inp(), "paths": [["token"]], "output": "clean"}])
    engine, result = solve(values, path=["token"])
    assert result["status"] == "partial"
    assert any(item["code"] == "excluded_requirement" for item in result["diagnostics"])
    assert not input_demands(engine, result, "exclude_parts")


def test_unbound_task_does_not_seed_current_sink_payload_or_authorize_deletion():
    values = fixture([{"op": "select_part", "input": inp(), "path": ["body"], "output": "body"}])
    _, result = solve(values, {"goals": [], "expressions": []})
    assert result["status"] == "partial"
    assert result["derivations"] == {}
    assert result["sinks"] and all(sink["limitations"] for sink in result["sinks"])


def test_required_foreach_action_retains_occurrence_without_promoting_parameters():
    def change(prepared, raw, ev):
        raw["locations"]["signal"] = {"kind": "tool", "name": "signal boundary", "operand_refs": [],
                                       "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["signal"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"].append({
            "kind": "for_each", "collection": local("selected"), "item": "row", "evidences": deepcopy(ev),
            "body": [{"kind": "processing", "mode": "default", "returns": [], "evidences": deepcopy(ev),
                      "events": [{"effect": None, "evidences": [], "atomic_ops": [{"op": "deliver", "inputs": [],
                                    "target": "signal", "evidences": deepcopy(ev)}]}]}]})
    values = fixture([{"op": "filter_items", "input": inp(), "predicate": "urgent is true", "output": "selected"}],
                     mode="model", custom=change)
    cand = candidate(values[3], property="action", goal_target=target_id(values[3], "operation", op="deliver"),
                     expression={"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["urgent"]},
                     expression_op="filter_items")
    _, result = solve(values, cand)
    observed = sink_demands(result)
    assert any(row["path"] == ["urgent"] for row in observed)
    assert not any(row["path"] in [["recipient"], ["summary"]] for row in observed)
    assert all(not row["actual_payload"][0]["inputs"] for row in result["sinks"]
               if row["boundary"]["sink_type"] == "external_tool")


def test_repeated_parameter_target_keeps_its_original_slot():
    def change(prepared, raw, ev):
        raw["locations"]["pair"] = {"kind": "tool", "name": "pair boundary", "operand_refs": [],
                                     "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["pair"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"][0]["events"].append({"effect": None, "evidences": [], "atomic_ops": [
            {"op": "deliver", "inputs": [inp(), inp()], "target": "pair", "evidences": deepcopy(ev)}]})
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "unused"}], custom=change)
    cand = candidate(values[3], path=["body"], goal_target=target_id(values[3], "input_use", op="deliver", slot=1))
    _, result = solve(values, cand)
    rows = sink_demands(result, "external_tool")
    assert rows and {row["node"]["slot"] for row in rows} == {1}


def test_strong_overwrite_stops_old_saved_content_demand():
    def change(prepared, raw, ev):
        raw["locations"]["cache"] = {"kind": "storage", "name": "cache", "operand_refs": [],
                                      "access_scope": "task", "retention": "persistent"}
        raw["location_evidences"]["cache"] = deepcopy(ev)
        set_operator(raw, prepared, "ir_filter", ["agent_runtime"])
        segment = raw["ir_semantics"]["ir_filter"]["events"][0]
        operations = [
            {"op": "write", "mode": "replace", "target": "cache", "input": literal("old")},
            {"op": "write", "mode": "replace", "target": "cache", "input": inp()},
            {"op": "read", "location": "cache", "output": "fresh"}]
        segment["events"] = [{"effect": ["fs_write", "fs_write", "fs_read"][i], "evidences": deepcopy(ev), "atomic_ops": [{**op, "evidences": deepcopy(ev)}]}
                             for i, op in enumerate(operations)]
        raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = local("fresh")
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "unused"}],
                     mode="local", custom=change)
    engine, result = solve(values, path=["body"])
    writes = [sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "storage_write"]
    assert len(writes) == 2
    for sink in writes:
        op = engine.ops[sink["actual_payload"][0]["operation_id"]]
        if op["spec"]["input"]["kind"] == "literal":
            assert not sink["demanded_information"] and not sink["conservative_retention"]
        else:
            assert sink["demanded_information"]
            assert all(result["derivations"][key]["path"] == ["body"] for key in sink["demanded_information"])


def test_exclusion_paths_translate_between_container_and_member_frames():
    values = fixture([
        {"op": "build", "parts": [{"path": ["payload"], "value": inp()}], "container": "object", "output": "wrapped"},
        {"op": "exclude_parts", "input": local("wrapped"), "paths": [["payload", "secret"]], "output": "clean"},
        {"op": "select_part", "input": local("clean"), "path": ["payload"], "output": "body"}])
    engine, result = solve(values)
    rows = input_demands(engine, result, "build")
    assert rows and all(row["path"] == [] and row["excluded_paths"] == [["secret"]] for row in rows)
    assert all(row["excluded_paths"] == [["secret"]] for row in sink_demands(result))


def test_nested_element_path_is_conservatively_retained_instead_of_flattened():
    def change(prepared, raw, ev):
        set_operator(raw, prepared, "ir_filter", ["llm"])
        raw["locations"]["notify"] = {"kind": "tool", "name": "notify", "operand_refs": [],
                                       "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["notify"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"].append({"kind": "for_each", "collection": local("rows"), "item": "row",
            "evidences": deepcopy(ev), "body": [{"kind": "processing", "mode": "model", "returns": [], "evidences": deepcopy(ev),
                "events": [{"effect": "transform", "evidences": deepcopy(ev), "atomic_ops": [{"op": "select_part", "input": local("row"),
                    "path": ["summary"], "output": "body", "evidences": deepcopy(ev)}]},
                    {"effect": None, "evidences": [], "atomic_ops": [{"op": "deliver", "inputs": [local("body")], "target": "notify", "evidences": deepcopy(ev)}]}]}]})
    values = fixture([{"op": "select_part", "input": inp(), "path": ["rows"], "output": "rows"}], mode="model", custom=change)
    cand = candidate(values[3], goal_target=target_id(values[3], "input_use", op="deliver", slot=0))
    engine, result = solve(values, cand)
    rows = [row for row in input_demands(engine, result, "select_part")
            if engine.ops[row["node"]["operation_id"]]["scope"] is None]
    assert any(row["conservative"] and row["property"] == "value" and row["path"] == ["rows"] and not row["each"] for row in rows)
    assert not any(row["each"] and row["path"] == ["rows", "summary"] for row in rows)
    assert any(d["code"] == "nested_collection_scope" and not d["blocking"] for d in result["diagnostics"])


def test_boolean_expression_rejects_count_without_truthiness_conversion():
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "predicate"}])
    expr = {"op": "not", "arg": {"op": "count", "arg": {"op": "ref", "value": inp()}}}
    with pytest.raises(ValueError, match="Boolean"):
        solve(values, expression=expr)


def test_boolean_expression_rejects_numeric_cfg_input():
    def graph_change(cfg):
        ir = cfg["blocks"]["entry"]["instructions"][1]
        ir["inputs"] = [{"type": "literal", "literal_value": 42}]
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "predicate"}],
                     graph_change=graph_change)
    with pytest.raises(ValueError, match="Boolean"):
        solve(values, expression={"op": "not", "arg": {"op": "ref", "value": inp()}})


def test_false_build_member_observation_has_no_payload_sink_or_value_demand():
    values = fixture([{"op": "build", "parts": [{"path": ["optional"], "value": inp(), "when": literal(False)}],
                       "container": "object", "output": "request"}])
    engine, result = solve(values)
    assert not input_demands(engine, result, "build", slot=1)
    observed_data = {data for sink in result["sinks"] for instance in sink["actual_payload"]
                     for slot in instance["inputs"] for data in slot}
    original = next(op for op in engine.ops.values() if op["spec"]["op"] == "read")["record"]["outputs"][0]
    assert not observed_data & set(original)
    conditional_keys = {key for key, op in engine.ops.items() if op["generated"] and op["spec"].get("when") is not None}
    assert conditional_keys
    actual_sink_keys = {entry["operation_id"] for sink in result["sinks"] for entry in sink["actual_payload"]}
    assert not actual_sink_keys & conditional_keys


def test_direct_context_operand_retains_reaching_write_without_read_operation():
    def graph_change(cfg):
        cfg["declared_context_keys"] = ["cache"]
        cfg["blocks"]["entry"]["instructions"][-1] = {"id": "ir_dispatch", "opcode": "dispatch", "inputs": [], "outputs": []}
        cfg["blocks"]["acquire"] = {"block_id": "acquire", "block_name": "Acquire saved context", "data_source_kind": "context", "instructions": [
            {"id": "ir_context", "opcode": "acquire_context", "inputs": [{"type": "context_key", "identifier": "cache"}],
             "outputs": [{"type": "result", "identifier": "cached"}]},
            {"id": "ir_return", "opcode": "return", "inputs": [{"type": "result", "identifier": "cached"}], "outputs": []}]}
        cfg["edges"] = [{"source_block_id": "entry", "target_block_id": "acquire", "condition_text": None}]
    def change(prepared, raw, ev):
        raw["locations"]["cache"] = {"kind": "runtime_context", "name": "cache",
            "operand_refs": [{"instruction_id": "ir_context", "side": "input", "index": 0}],
            "access_scope": "task", "retention": "persistent"}
        raw["location_evidences"]["cache"] = deepcopy(ev)
        set_operator(raw, prepared, "ir_filter", ["agent_runtime"])
        segment = raw["ir_semantics"]["ir_filter"]["events"][0]
        segment["events"] = [
            {"effect": "context_write", "evidences": deepcopy(ev), "atomic_ops": [{"op": "write", "target": "cache", "mode": "replace", "input": literal("old"), "evidences": deepcopy(ev)}]},
            {"effect": "context_write", "evidences": deepcopy(ev), "atomic_ops": [{"op": "write", "target": "cache", "mode": "replace", "input": inp(), "evidences": deepcopy(ev)}]}]
        raw["ir_semantics"]["ir_filter"]["output_bindings"][0]["value"] = inp()
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "unused"}],
                     mode="local", custom=change, graph_change=graph_change)
    engine, result = solve(values, path=["body"])
    saves = [sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "context_save"]
    assert len(saves) == 2
    for sink in saves:
        op = engine.ops[sink["actual_payload"][0]["operation_id"]]
        rows = [result["derivations"][key] for key in sink["demanded_information"]]
        if op["spec"]["input"]["kind"] == "literal":
            assert not rows
        else:
            assert rows and all(row["path"] == ["body"] for row in rows)
            assert any("context_reaching_write" in row["rules"] for row in rows)
