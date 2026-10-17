"""Authored boundary seeds verify engineering rules, not model detection rates.

These small label-routing fixtures are independent of the online pilot Skills.
No absent seed is filled automatically: a structurally valid omission remains a
semantic review obligation. Equal Data IDs do not join different receiver slots.
"""
import pytest

from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.demand_index import build_demand_target_index
from skillflow.doe.sensitivity_material import joint_demands
from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, goal, inp, instruction, literal, local,
    result, segment, semantics,
)
from skillflow.propagation.annotation.compiler import compile_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import Task
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate


SOURCE = (
    "The controller uses an explicitly local label formatter with no content "
    "returned to the agent. Read the display field of the supplied calibration "
    "packet and send that original value to the label receiver. A requested "
    "storage operation saves only its stated new value, not old file contents."
)


def declared_goal(kind, *, index=None, preserve="value", path=()):
    target = {"kind": kind}
    if index is not None:
        target["index"] = index
    return goal(target, preserve, path=list(path))


def synthetic_fixture(operations, *, output="formatted", inputs=None,
                      return_demand=False, gap=False, source=SOURCE,
                      processing_mode="local", extra_locations=None, registry_namespace=None):
    """Build one explicitly authored source-only Task and checked annotation."""
    events = []
    for operation in operations:
        effect = "context_read" if operation["op"] == "read" else "fs_write" if operation["op"] == "write" else (
            None if operation["op"] in {"deliver", "receive"} else "transform")
        event = segment([operation], effect)
        event["mode"] = processing_mode
        if effect is None:
            event["events"][0]["evidences"] = []
        events.append(event)
    example = _fixture("label receiver seeds", "Explicit receiving inputs matter.", source,
        [instruction("ir_format", "format_label", inputs or [literal({"display": "CAL-7", "service_note": "internal"})], "formatted"),
         instruction("ir_finish", "return", [result("formatted")])],
        {"ir_format": semantics(events, output), "ir_finish": semantics()})
    material = example_material(example)
    raw = example["annotation"]
    raw["task_revision_id"] = material["task"]["task_sha256"]
    has_seed = return_demand or any(operation.get("demands") for operation in operations)
    raw["realizations"] = [{"requirement_id": "R1",
        "status": ("partial" if gap else "expressed") if has_seed else "retained_only",
        "bindings": [], "gaps": [{"reason": "次数限制仍没有可执行表达。" if gap else "尚未给定正向需求起点。",
                                    "evidences": [evidence()]}] if gap or not has_seed else []}]
    if return_demand:
        raw["demands"] = [{"requirement_id": "R1", "preserve": "value",
            "target": {"instruction_id": "ir_finish", "side": "input", "index": 0},
            "reason": "保留真实返回输入，不虚构公开输出。"}]
    for identity, kind in (("label_receiver", "tool"), ("journal", "storage")):
        raw["locations"][identity] = {"kind": kind, "name": identity,
            "operand_refs": [], "access_scope": "recipient" if kind == "tool" else "task",
            "retention": None if kind == "tool" else "persistent"}
        raw["location_evidences"][identity] = [evidence()]
    for identity, location in (extra_locations or {}).items():
        raw["locations"][identity] = location
        raw["location_evidences"][identity] = [evidence()]
    checked, compiled, mapping = compile_response(raw, material)
    from skillflow.propagation.data import DataRegistry
    solved = propagate(material["cfg"], to_payload(compiled),
        initial_registry=DataRegistry(registry_namespace) if registry_namespace else None)
    assert solved.status == "complete", solved.diagnostics
    facts = materials_from_result(solved, material=material, raw_annotation=checked,
        compiled_annotation=compiled, mapping=mapping)
    return material, checked, facts


def solve_fixture(fixture):
    material, raw, facts = fixture
    targets = build_demand_target_index(facts.cfg, raw)
    candidate = joint_demands(facts.annotation)
    task = Task.model_validate(material["task"])
    engine = DemandEngine(facts, task, facts.annotation, candidate, targets)
    solved = engine.solve()
    assert solved == DemandEngine(facts, task, facts.annotation, candidate, targets).solve(queue_order="lifo")
    return engine, solved


def boundary_rows(solved, kind="external_tool", *, node_kind="op_input"):
    return [solved["derivations"][key]
        for sink in solved["sinks"] if sink["boundary"]["sink_type"] == kind
        for key in sink["demanded_information"] + sink["conservative_retention"]
        if solved["derivations"][key]["node"]["kind"] == node_kind]


def label_operations(producer="select_part", *, producer_seed=False,
                     receiver_seed=False, action_seed=False):
    selected = {"op": "select_part", "input": inp(), "path": ["display"], "output": "formatted"}
    if producer == "build":
        selected = {"op": "build", "parts": [{"path": ["label"], "value": inp()}],
                    "container": "object", "output": "formatted"}
    if producer_seed:
        selected["demands"] = [declared_goal("output")]
    delivery = {"op": "deliver", "inputs": [local("formatted")], "target": "label_receiver"}
    if receiver_seed or action_seed:
        delivery["demands"] = ([declared_goal("self", preserve="action")] if action_seed else []) + (
            [declared_goal("input", index=0)] if receiver_seed else [])
    return [selected, delivery]


@pytest.mark.parametrize("producer", ["select_part", "build"])
def test_producer_output_seed_does_not_establish_the_receiver_input(producer):
    fixture = synthetic_fixture(label_operations(producer, producer_seed=True))
    engine, solved = solve_fixture(fixture)
    assert solved["status"] == "complete"
    assert any(row["node"]["kind"] == "op_output" for row in solved["derivations"].values())
    assert not boundary_rows(solved)
    # The actual delivered Data is exactly the producer output; matching its ID
    # must not make it a new receiving-side demand.
    producer_op = next(op for op in engine.ops.values() if op["spec"]["op"] == producer)
    receiver = next(op for op in engine.ops.values() if op["spec"]["op"] == "deliver")
    assert producer_op["record"]["outputs"][0] == receiver["record"]["inputs"][0]
    assert all(sink["unestablished_ranges"] for sink in solved["sinks"])


def test_delivery_action_preserves_occurrence_without_preserving_payload():
    _, solved = solve_fixture(synthetic_fixture(label_operations(action_seed=True)))
    assert boundary_rows(solved, node_kind="action")
    assert not boundary_rows(solved)
    assert solved["sinks"][0]["unestablished_ranges"][0]["scope"] == "whole_slot"


def test_actual_delivery_input_seed_reaches_only_its_original_field():
    engine, solved = solve_fixture(synthetic_fixture(label_operations(receiver_seed=True)))
    rows = boundary_rows(solved)
    assert rows and all(not row["conservative"] and row["node"]["slot"] == 0 for row in rows)
    original = [row for row in solved["derivations"].values() if row["node"]["kind"] == "op_input"
        and engine.ops[row["node"]["operation_id"]]["spec"]["op"] == "select_part"]
    assert original and {tuple(row["path"]) for row in original} == {("display",)}
    trace = solved["traceability"]["requirements"][0]["seeds"]
    assert all("/demands/" in seed["raw_pointer"] for seed in trace)


def test_same_value_in_a_second_phase_or_repeated_slot_does_not_inherit_seed():
    operations = label_operations(receiver_seed=True)
    operations[-1]["inputs"].append(local("formatted"))
    operations.append({"op": "deliver", "inputs": [local("formatted")], "target": "label_receiver"})
    engine, solved = solve_fixture(synthetic_fixture(operations))
    deliveries = [op for op in engine.ops.values() if op["spec"]["op"] == "deliver"]
    assert len(deliveries) == 2
    seeded = next(op for op in deliveries if len(op["record"]["inputs"]) == 2)
    unseeded = next(op for op in deliveries if len(op["record"]["inputs"]) == 1)
    assert seeded["record"]["inputs"][0] == seeded["record"]["inputs"][1] == unseeded["record"]["inputs"][0]
    rows = boundary_rows(solved)
    assert rows and {(row["node"]["operation_id"], row["node"]["slot"]) for row in rows} == {(seeded["key"], 0)}


@pytest.mark.parametrize("include_payload", [False, True])
@pytest.mark.parametrize("mode", ["replace", "append"])
def test_write_action_and_new_payload_never_require_previous_file(include_payload, mode):
    operations = [
        {"op": "select_part", "input": inp(), "path": ["display"], "output": "formatted"},
        {"op": "write", "mode": "replace", "target": "journal", "input": {"kind": "literal", "value": "old entry"}},
        {"op": "write", "mode": mode, "target": "journal", "input": local("formatted"),
         "demands": [declared_goal("self", preserve="action")] + (
             [declared_goal("input", index=0)] if include_payload else [])}]
    engine, solved = solve_fixture(synthetic_fixture(operations))
    saves = [sink for sink in solved["sinks"] if sink["boundary"]["sink_type"] == "storage_write"]
    assert len(saves) == 2
    previous = next(sink for sink in saves if engine.ops[sink["actual_payload"][0]["operation_id"]]["spec"]["input"]["kind"] == "literal")
    appended = next(sink for sink in saves if engine.ops[sink["actual_payload"][0]["operation_id"]]["spec"]["input"]["kind"] == "local")
    assert not previous["demanded_information"] and not previous["conservative_retention"]
    payload = boundary_rows(solved, "storage_write")
    assert bool(payload) is include_payload
    actual = appended["actual_payload"][0]["inputs"]
    assert len(actual) == 1 and actual != previous["actual_payload"][0]["inputs"]
    assert all(engine.ops[row["node"]["operation_id"]]["spec"]["mode"] == mode for row in payload)


def optional_request(*, explicit_parameters):
    build = {"op": "build", "container": "object", "parts": [
        {"path": ["label"], "value": inp(0)},
        {"path": ["alignment"], "value": inp(2), "when": inp(1)}], "output": "formatted"}
    delivery = {"op": "deliver", "inputs": [local("formatted")], "target": "label_receiver"}
    if explicit_parameters:
        delivery["demands"] = [declared_goal("input", index=0, path=["label"]),
                               declared_goal("input", index=0, path=["alignment"])]
    return synthetic_fixture([build, delivery,
        {"op": "receive", "location": "label_receiver", "inputs": [local("formatted")], "output": "receipt"}],
        output="receipt", inputs=[literal("CAL-7"), literal(True), literal("center")], return_demand=True,
        source="The local label formatter sends the supplied label and optional alignment unchanged. Alignment is included exactly when its presence flag is true; return the receiver's receipt unchanged.")


def test_receive_request_retention_is_not_an_exact_parameter_requirement():
    _, solved = solve_fixture(optional_request(explicit_parameters=False))
    rows = boundary_rows(solved)
    assert rows and all(row["conservative"] and row["path"] == [] for row in rows)
    assert not any(row["path"] in (["label"], ["alignment"]) and not row["conservative"] for row in rows)


def test_explicit_request_parameters_keep_conditions_out_of_receiver_payload():
    engine, solved = solve_fixture(optional_request(explicit_parameters=True))
    exact = [row for row in boundary_rows(solved) if not row["conservative"]]
    assert {tuple(row["path"]) for row in exact} == {("label",), ("alignment",)}
    build = next(op for op in engine.ops.values() if op["spec"]["op"] == "build")
    assert build["record"]["members"][1] == {"path": ["alignment"], "value_input_index": 2, "when_input_index": 1}
    truth = [row for row in solved["derivations"].values() if row["node"]["operation_id"] == build["key"]
             and row["node"]["kind"] == "op_input" and row["node"]["slot"] == 1]
    assert truth and all(row["property"] == "truth" for row in truth)
    delivery = next(op for op in engine.ops.values() if op["spec"]["op"] == "deliver")
    assert len(delivery["record"]["inputs"]) == 1
    assert build["record"]["inputs"][1] not in delivery["record"]["inputs"]


def test_true_whole_value_requirement_remains_legal_and_precise():
    ops = [{"op": "build", "container": "object", "parts": [{"path": ["label"], "value": inp()}], "output": "formatted"},
           {"op": "deliver", "inputs": [local("formatted")], "target": "label_receiver", "demands": [declared_goal("input", index=0)]}]
    _, solved = solve_fixture(synthetic_fixture(ops,
        source="The local formatter wraps the complete supplied packet as label and sends the complete wrapped value unchanged to the receiver."))
    assert boundary_rows(solved) and all(row["path"] == [] and not row["conservative"] for row in boundary_rows(solved))


def test_field_return_needs_no_redundant_expected_or_receiver_seed():
    fixture = synthetic_fixture(label_operations()[:1], return_demand=True)
    assert fixture[1]["demands"][0]["expected"] is None
    engine, solved = solve_fixture(fixture)
    assert not solved["sinks"]
    rows = [row for row in solved["derivations"].values() if row["node"]["kind"] == "op_input"]
    assert rows and all(row["path"] == ["display"] for row in rows)


def test_opaque_whole_input_retention_and_global_gap_are_not_eraseable():
    fixture = synthetic_fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "formatted"},
        {"op": "deliver", "inputs": [local("formatted")], "target": "label_receiver", "demands": [declared_goal("input", index=0)]}], gap=True)
    engine, solved = solve_fixture(fixture)
    compute = next(op for op in engine.ops.values() if op["spec"]["op"] == "compute")
    retained = [row for row in solved["derivations"].values() if row["node"]["kind"] == "op_input"
                and row["node"]["operation_id"] == compute["key"]]
    assert retained and all(row["conservative"] and row["path"] == [] for row in retained)
    gap = next(row for row in solved["diagnostics"] if row["code"] == "requirement_expression_gap")
    assert gap["instruction_id"] is None and gap["blocking"]
    assert solved["status"] == "partial" and all(gap["id"] in sink["limitations"] for sink in solved["sinks"])
    assert not any("necessary" in row for row in solved["derivations"].values())


def request_operations(*, endpoint_paths=(), receiver_shape=False, repeated_receiver=False):
    """Independent test fixture: construction-use seeds are not receiver seeds."""
    build = {"op": "build", "container": "object", "parts": [
        {"path": ["display_code"], "value": inp(0)},
        {"path": ["spacing"], "value": inp(1)}], "output": "formatted",
        "demands": [declared_goal("input", index=0), declared_goal("input", index=1)]}
    deliver = {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")],
        "demands": [declared_goal("self", preserve="action")]}
    if receiver_shape:
        deliver["demands"].append(declared_goal("input", index=0, preserve="shape"))
    deliver["demands"].extend(declared_goal("input", index=0, path=path) for path in endpoint_paths)
    operations = [build, deliver]
    if repeated_receiver:
        operations.append({"op": "deliver", "target": "secondary_receiver", "inputs": [local("formatted")]})
    return operations


def test_construction_input_values_and_receiver_action_shape_do_not_imply_receiver_values():
    fixture = synthetic_fixture(request_operations(receiver_shape=True),
        inputs=[literal("board-C"), literal("wide")],
        source="An isolated local renderer constructs display_code and spacing from the supplied original values and delivers the request to the label receiver; it returns no content to the agent.")
    engine, solved = solve_fixture(fixture)
    receiver = boundary_rows(solved)
    assert receiver and {row["property"] for row in receiver} == {"shape"}
    assert boundary_rows(solved, node_kind="action")
    build = next(op for op in engine.ops.values() if op["spec"]["op"] == "build")
    upstream = [row for row in solved["derivations"].values()
        if row["node"]["kind"] == "op_input" and row["node"]["operation_id"] == build["key"]]
    assert {row["node"]["slot"] for row in upstream if row["property"] == "value"} == {0, 1}
    assert not any(row["property"] == "value" for row in receiver)


def test_receiver_path_demands_have_own_seeds_and_do_not_move_to_another_receiver():
    receiver = {"kind": "tool", "name": "secondary board", "operand_refs": [],
                "access_scope": "recipient", "retention": None}
    fixture = synthetic_fixture(request_operations(endpoint_paths=[["display_code"], ["spacing"]], repeated_receiver=True),
        inputs=[literal("board-C"), literal("wide")], extra_locations={"secondary_receiver": receiver},
        source="The isolated local renderer sends the two original parameters to two distinct boards. Parameter demands must be represented at each actual receiving boundary; no contents are returned to the agent.")
    engine, solved = solve_fixture(fixture)
    deliveries = {op["spec"]["target"]: op for op in engine.ops.values() if op["spec"]["op"] == "deliver"}
    assert deliveries["label_receiver"]["record"]["inputs"] == deliveries["secondary_receiver"]["record"]["inputs"]
    rows = boundary_rows(solved)
    assert {tuple(row["path"]) for row in rows} == {("display_code",), ("spacing",)}
    assert {row["node"]["operation_id"] for row in rows} == {deliveries["label_receiver"]["key"]}
    seeds = {row["goal_id"]: row["raw_pointer"] for row in solved["traceability"]["requirements"][0]["seeds"]}
    assert len({row["seed_goal_id"] for row in rows}) == 2
    for row in rows:
        assert "/events/1/events/0/atomic_ops/0/demands/" in seeds[row["seed_goal_id"]]
    build_seed_ids = {seed for seed, pointer in seeds.items() if "/events/0/events/0/atomic_ops/0/demands/" in pointer}
    assert build_seed_ids.isdisjoint({row["seed_goal_id"] for row in rows})
    unseeded = next(sink for sink in solved["sinks"]
        if sink["actual_payload"][0]["operation_id"] == deliveries["secondary_receiver"]["key"])
    assert unseeded["unestablished_ranges"] and not unseeded["demanded_information"]


@pytest.mark.parametrize("condition", [True, False, "abstract"])
def test_conditional_request_values_and_presence_controls_remain_separate(condition):
    from skillflow.propagation.conditions import guard_truths, payload_inputs
    operations = []
    guard = inp(1)
    if condition == "abstract":
        operations.append({"op": "compute", "inputs": [inp(1)], "dependencies": ["possible"], "output": "flag"})
        guard = local("flag")
    operations += [
        {"op": "build", "container": "object", "parts": [
            {"path": ["display_code"], "value": inp(0)},
            {"path": ["spacing"], "value": inp(2), "when": guard}], "output": "formatted"},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")],
         "demands": [declared_goal("input", index=0)]}]
    fixture = synthetic_fixture(operations, inputs=[literal("board-C"), literal(condition if type(condition) is bool else "unresolved condition"), literal("wide")],
        source="An isolated local renderer delivers a complete request containing the original display_code and spacing exactly when the Boolean condition holds; the condition itself is not a request member and no content is returned to the agent.")
    engine, solved = solve_fixture(fixture)
    build = next(op for op in engine.ops.values() if op["spec"]["op"] == "build")
    delivery = next(op for op in engine.ops.values() if op["spec"]["op"] == "deliver")
    member = build["record"]["members"][1]
    control_slot = member["when_input_index"]
    control_ids = set(build["record"]["inputs"][control_slot])
    truths = guard_truths(fixture[2].data, control_ids)
    assert truths == ({False, True} if condition == "abstract" else {condition})
    assert len(payload_inputs(delivery["record"])) == 1
    assert control_ids.isdisjoint({value for slot in payload_inputs(delivery["record"]) for value in slot})
    propagated = {data["id"]: data for data in fixture[2].data}
    shapes = set()
    for value in delivery["record"]["inputs"][0]:
        content = propagated[value]["content"]
        if content["form"] == "known_parts":
            shapes.add(tuple(sorted(part["path"][0] for part in content["parts"])))
        else:
            assert content["form"] == "literal"
            shapes.add(tuple(sorted(content["value"])))
    expected_shapes = {("display_code", "spacing")} if condition is True else {("display_code",)}
    if condition == "abstract": expected_shapes.add(("display_code", "spacing"))
    assert shapes == expected_shapes
    control_demands = [row for row in solved["derivations"].values()
        if row["node"]["kind"] == "op_input" and row["node"]["operation_id"] == build["key"] and row["node"]["slot"] == control_slot]
    assert control_demands and {row["property"] for row in control_demands} == {"truth"}
    assert (member["value_input_index"] is None) is (condition is False)


def test_narrower_task_seed_does_not_change_the_source_or_compiled_observation():
    source = "Read the request packet from session context and send only its original display field to the label receiver. No local isolation or key-only interface is specified."
    context = {"kind": "runtime_context", "name": "request packet", "operand_refs": [],
               "access_scope": "task", "retention": "task"}
    def analyze(path):
        operations = [
            {"op": "read", "location": "packet_context", "output": "packet",
             "demands": [declared_goal("output", path=path)]},
            {"op": "select_part", "input": local("packet"), "path": ["display"], "output": "formatted"},
            {"op": "deliver", "inputs": [local("formatted")], "target": "label_receiver",
             "demands": [declared_goal("input", index=0)]}]
        # Hold the analysis namespace fixed: different annotations normally
        # receive different run-scoped IDs even when their forward facts agree.
        fixture = synthetic_fixture(operations, source=source, processing_mode="default",
            extra_locations={"packet_context": context}, registry_namespace="source-scope-comparison")
        engine, solved = solve_fixture(fixture)
        return fixture, engine, solved
    broad, broad_engine, broad_solved = analyze([])
    narrow, narrow_engine, narrow_solved = analyze(["display"])
    assert broad[2].data == narrow[2].data
    assert broad[2].records == narrow[2].records
    assert broad[2].sinks == narrow[2].sinks
    broad_observations = [op for op in broad_engine.ops.values() if op["generated"]]
    narrow_observations = [op for op in narrow_engine.ops.values() if op["generated"]]
    assert broad_observations and [(o["position"], o["record"]) for o in broad_observations] == [(o["position"], o["record"]) for o in narrow_observations]
    read_broad = next(op for op in broad_engine.ops.values() if op["spec"]["op"] == "read")
    read_narrow = next(op for op in narrow_engine.ops.values() if op["spec"]["op"] == "read")
    def output_paths(solved, operation):
        return {tuple(row["path"]) for row in solved["derivations"].values()
            if row["node"]["kind"] == "op_output" and row["node"]["operation_id"] == operation["key"]}
    assert () in output_paths(broad_solved, read_broad)
    assert output_paths(narrow_solved, read_narrow) == {("display",)}
    def source_observation_paths(engine, solved, read):
        observed = {op["key"] for op in engine.ops.values() if op["generated"]
            and op["record"]["inputs"][0] == read["record"]["outputs"][0]}
        assert observed
        return {tuple(row["path"]) for row in boundary_rows(solved, "model_observe")
            if row["node"]["operation_id"] in observed}
    assert () in source_observation_paths(broad_engine, broad_solved, read_broad)
    assert source_observation_paths(narrow_engine, narrow_solved, read_narrow) == {("display",)}
    assert all(row["path"] == [] for row in boundary_rows(narrow_solved))
