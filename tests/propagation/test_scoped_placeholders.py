"""Source-located unknown relations preserve independent values and continuation."""
from copy import deepcopy

import pytest

from examples.propagation.propagation_demo import fixture_annotation, input_ref, instruction, literal, local, operand
from skillflow.propagation import propagate
from skillflow.propagation.contracts.specs import PlaceholderOp
from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts
from tests.propagation.test_runtime_failure_locality import block, check_facts, fixture


SOURCE = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
          "reason": "This example leaves the operation's payload conversion unspecified."}


def placeholder(kind, *inputs, **fields):
    return {"op": "placeholder", "kind": kind, "inputs": list(inputs), "reason": SOURCE["reason"],
            "evidences": [SOURCE], **fields}


def read(location):
    return (["context_read"], [(0, [{"op": "read", "location": location, "output": "v"}])], [local("v")])


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_field_placeholder_preserves_sibling_and_possible_edges(schedule):
    cfg, ann = fixture([
        instruction("source", outputs=["raw"]), instruction("map", [operand("raw")], ["out"]),
        instruction("pick", [operand("out")], ["known", "unknown"]),
        instruction("finish", [operand("known"), operand("unknown")], opcode="return")
    ], {
        "source": read("raw"),
        "map": (["transform"], [(0, [
            {"op": "select_part", "input": input_ref(), "path": ["maybe"], "output": "candidate"},
            placeholder("value", local("candidate"), output="uncertain"),
            {"op": "build", "container": "object", "output": "out", "parts": [
                {"path": ["known"], "value": literal(4)}, {"path": ["unknown"], "value": local("uncertain")}]},
        ])], [local("out")]),
        "pick": (["transform"], [(0, [
            {"op": "select_part", "input": input_ref(), "path": ["known"], "output": "known"},
            {"op": "select_part", "input": input_ref(), "path": ["unknown", "nested"], "output": "nested"}
        ])], [local("known"), local("nested")]),
    }, {"raw": ("runtime_context", "raw")})
    solved = propagate(cfg, ann, schedule=schedule)
    check_facts(cfg, ann, solved)
    assert solved.coverage == {"ir_source": "processed", "ir_map": "processed_with_placeholder",
                               "ir_pick": "processed", "ir_finish": "processed"}
    records = solved.records.records_dict()
    value = records["ir_map"]["events"][0]["atomic_ops"][1]
    assert value["placeholder_kind"] == "value"
    output, = value["outputs"][0]
    origin = solved.registry.get(output).origin
    assert origin.acquired_from is None
    assert [(d.data, d.relation) for d in origin.dependencies] == [(value["inputs"][0][0], "possible")]
    known, unknown = records["ir_pick"]["events"][0]["atomic_ops"]
    assert solved.registry.get(known["outputs"][0][0]).content.value == 4
    assert unknown["outputs"][0]
    assert not resolved_sink_boundaries(ann["locations"], records)
    broken_coverage = {**solved.coverage, "ir_map": "processed"}
    with pytest.raises(ValueError, match="placeholder coverage"):
        validate_propagation_facts(cfg=cfg, annotation=ann,
            data=[row["data"] for row in solved.registry.to_dict()["records"]], records=records, sinks=[],
            status=solved.status, coverage=broken_coverage, diagnostics=solved.diagnostics)


@pytest.mark.parametrize("unknown_address", [False, True])
def test_weak_effect_has_precise_footprint_and_no_sink(unknown_address):
    cfg, ann = fixture([
        instruction("update"), instruction("read_a", outputs=["a"]), instruction("read_b", outputs=["b"]),
        instruction("finish", [operand("a"), operand("b")], opcode="return")
    ], {
        "update": ([], [(None, [placeholder("effect", literal("possible"), location="a", may_write=True),
                                placeholder("effect", location="remote")])], []),
        "read_a": read("a"), "read_b": read("b"),
    }, {"a": ("runtime_context", "a"), "b": ("runtime_context", "b"),
        "remote": ("remote", "service"), "disk": ("storage", "disk")})
    if unknown_address:
        ann["locations"]["a"].update(address_kind="unidentified", address_reason="The address comes from the caller.")
    solved = propagate(cfg, ann)
    check_facts(cfg, ann, solved)
    records = solved.records.records_dict()
    alias_write, unknown_effect = records["ir_update"]["events"][0]["atomic_ops"]
    version, = alias_write["possible_writes"]
    assert {change["location"]["name"] for change in alias_write["changes"]} == ({"a", "b"} if unknown_address else {"a"})
    assert all(change["update"] == "weak" and set(change["after"]) == {*change["before"], version}
               for change in alias_write["changes"])
    assert not unknown_effect["changes"] and unknown_effect["endpoints"] == [{"kind": "remote", "name": "service"}]
    assert not resolved_sink_boundaries(ann["locations"], records)
    assert version in records["ir_read_a"]["events"][0]["atomic_ops"][0]["outputs"][0]
    assert (version in records["ir_read_b"]["events"][0]["atomic_ops"][0]["outputs"][0]) == unknown_address
    forged = deepcopy(records)
    forged["ir_update"]["events"][0]["atomic_ops"][1]["endpoints"] = []
    with pytest.raises(ValueError, match="declared endpoint"):
        validate_propagation_facts(cfg=cfg, annotation=ann, data=[r["data"] for r in solved.registry.to_dict()["records"]],
            records=forged, sinks=[], status=solved.status, coverage=solved.coverage, diagnostics=solved.diagnostics)


def test_unknown_control_admits_both_existing_edges_and_same_schedule_facts():
    cfg, ann = fixture_annotation({"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("choose", outputs=["choice"]),
                                 instruction("gate", [operand("choice")], opcode="dispatch")]),
        "left": block("left", [instruction("left_return", opcode="return")]),
        "right": block("right", [instruction("right_return", opcode="return")]),
    }, "edges": [{"source_block_id": "entry", "target_block_id": name} for name in ("left", "right")]},
        {"choose": ([], [(None, [placeholder("value", output="choice")])], [local("choice")]),
         "gate": ([], [(None, [{"op": "branch", "input": input_ref(), "predicate": "truthy",
                                "true_target": "left", "false_target": "right"}])], [])})
    results = [propagate(cfg, ann, schedule=s) for s in ("fifo", "lifo")]
    for solved in results:
        check_facts(cfg, ann, solved)
        records = solved.records.records_dict()
        assert records["ir_gate"]["events"][0]["atomic_ops"][0]["branch_targets"] == ["left", "right"]
        assert solved.coverage["ir_left_return"] == solved.coverage["ir_right_return"] == "processed"
    assert results[0].records.records_dict() == results[1].records.records_dict()
    assert results[0].registry.to_dict() == results[1].registry.to_dict()


@pytest.mark.parametrize("op", [
    placeholder("value"), placeholder("effect", output="out"),
    placeholder("value", location="x", output="out"), placeholder("effect", may_write=True),
    {**placeholder("value", output="out"), "evidences": [{"rule_id": "EM08", "reason": "unknown"}]},
])
def test_placeholder_requires_actual_source_and_a_bounded_shape(op):
    with pytest.raises(ValueError):
        PlaceholderOp.model_validate(op)


def test_only_executed_member_placeholder_counts_and_each_occurrence_has_its_own_identity():
    from tests.propagation.test_map_collection import map_fixture

    cfg, ann = map_fixture()
    scope = ann["ir_semantics"]["ir_process"]["events"][0]
    scope["body"][2]["atomic_ops"].insert(0, placeholder("value", local("response"), output="uncertain"))
    scope["body"][2]["atomic_ops"][1]["parts"][1]["value"] = local("uncertain")
    for members in [[], ["aa", "aa"]]:
        scope["collection"] = literal(members)
        solved = propagate(cfg, ann)
        check_facts(cfg, ann, solved)
        record = solved.records.get("ir_process")
        instances = record.events[0].instances
        assert len(instances) == len(members)
        if members:
            assert solved.coverage["ir_process"] == "processed_with_placeholder"
            assert len({next(iter(i.body[2].atomic_ops[0].outputs[0])) for i in instances}) == 2
        else:
            assert solved.coverage["ir_process"] == "processed"


def test_value_placeholder_inside_feedback_loop_has_finite_schedule_independent_versions():
    from tests.propagation.test_explicit_loops import explicit_loop_fixture

    cfg, ann = explicit_loop_fixture()
    operation = ann["ir_semantics"]["ir_fetch"]["events"][0]
    operation["effect"] = "transform"
    operation["atomic_ops"] = [placeholder("value", input_ref(), output="reply")]
    fifo, lifo = [propagate(cfg, ann, schedule=order) for order in ("fifo", "lifo")]
    for solved in (fifo, lifo):
        check_facts(cfg, ann, solved)
        assert solved.coverage["ir_fetch"] == "processed_with_placeholder"
        assert solved.coverage["ir_return"] == "processed"
        assert not solved.diagnostics and solved.stats["block_evaluations"] < 30
        values = solved.records.get("ir_fetch").events[0].atomic_ops[0].outputs[0]
        for identity in values:
            data = solved.registry.get(identity)
            assert data.content.form == "loop_summary" and not data.origin.acquired_from
            assert {dep.relation for dep in data.origin.dependencies} == {"possible"}
    assert fifo.records.records_dict() == lifo.records.records_dict()
    assert fifo.registry.to_dict() == lifo.registry.to_dict()


@pytest.mark.parametrize("mode", ["default", "model"])
def test_possible_input_is_not_compiled_to_an_actual_model_observation(mode):
    from skillflow.propagation.annotation.compiler import compile_response
    from tests.propagation.annotation.test_processing_compiler import raw_fixture, set_operator

    material, raw = raw_fixture()
    spec = raw["ir_semantics"]["ir_filter"]
    spec["events"][0]["mode"] = mode
    if mode == "model":
        set_operator(spec, material, "ir_filter", ["llm"])
    event = spec["events"][0]["events"][0]
    event["atomic_ops"] = [placeholder("value", input_ref(), output="stage_0")]
    checked, compiled, mapping = compile_response(raw, material)
    assert checked["ir_semantics"]["ir_filter"]["events"][0]["events"][0]["atomic_ops"][0]["kind"] == "value"
    events = compiled["ir_semantics"]["ir_filter"]["events"]
    assert [op["op"] for event in events for op in event["atomic_ops"]] == ["placeholder"]
    assert mapping["compiler_version"].endswith("v16")
