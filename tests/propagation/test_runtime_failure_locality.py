"""Expected operand faults cannot turn independent work into inactive paths."""
from copy import deepcopy

import pytest

from examples.propagation.propagation_demo import fixture_annotation, input_ref, instruction, literal, local, operand
from skillflow.propagation import propagate
from skillflow.propagation.data import DataRegistry, OpaqueContent
from skillflow.propagation.facts import validate_propagation_facts, resolved_sink_boundaries
from skillflow.propagation.interpreter import TransferInterpreter, PropagationLimitError
from skillflow.propagation.models import FlowLocation, FlowState


def block(name, rows):
    return {"block_id": name, "block_name": name, "instructions": rows}


def fixture(rows, plans, locations=None):
    return fixture_annotation({"entry_block_id": "b", "blocks": {"b": block("b", rows)}, "edges": []}, plans, locations)


def compute(value, output="value"):
    return {"op": "compute", "inputs": [value], "dependencies": ["possible"], "output": output}


def filtered(value, output="bad"):
    return {"op": "filter_items", "input": value, "predicate": "keep", "output": output}


def check_facts(cfg, annotation, solved):
    records = solved.records.records_dict()
    return validate_propagation_facts(cfg=cfg, annotation=annotation,
        data=[row["data"] for row in solved.registry.to_dict()["records"]],
        records=records, sinks=resolved_sink_boundaries(annotation["locations"], records),
        status=solved.status, coverage=solved.coverage, diagnostics=solved.diagnostics)


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_failure_blocks_only_used_result_and_preserves_independent_records(schedule):
    cfg, annotation = fixture([
        instruction("bad", outputs=["bad"]), instruction("dependent", [operand("bad")], ["dependent"]),
        instruction("independent", outputs=["good"]), instruction("return", [operand("good")], opcode="return"),
    ], {
        "bad": (["transform"], [(0, [filtered(literal({"object": 1}))])], [local("bad")]),
        "dependent": (["transform"], [(0, [compute(input_ref())])], [local("value")]),
        "independent": (["transform"], [(0, [compute(literal(7))])], [local("value")]),
    })
    result = propagate(cfg, annotation, schedule=schedule)
    assert result.status == "incomplete"
    assert result.coverage == {"ir_bad": "execution_error", "ir_dependent": "blocked",
                              "ir_independent": "processed", "ir_return": "processed"}
    failure, = [row for row in result.diagnostics if row["code"] == "operation_execution_error"]
    assert failure["affected_instruction_ids"] == ["ir_bad", "ir_dependent"]
    assert failure["event_index"] == failure["op_index"] == 0
    assert failure["input_data_ids"]
    assert all(failure["observed_data"][key]["content"]["value"] == {"object": 1}
               for key in failure["input_data_ids"])
    check_facts(cfg, annotation, result)


def test_failed_prefix_refinement_rolls_back_but_observation_evidence_survives():
    registry = DataRegistry("prefix-rollback")
    source = registry.register_source("source", acquired_from="fixture:source")
    cfg, annotation = fixture([
        instruction("acquire", outputs=["source"]), instruction("bad", [operand("source")], ["bad"]),
        instruction("read", outputs=["read"]), instruction("return", [operand("read")], opcode="return"),
    ], {
        "acquire": (["context_read"], [(0, [{"op": "read", "location": "context", "output": "source"}])], [local("source")]),
        "bad": (["transform"], [(0, [
            {"op": "select_part", "input": input_ref(), "path": ["speculative"], "output": "part"},
            filtered(literal({"wrong": "shape"})),
        ])], [local("bad")]),
        "read": (["context_read"], [(0, [{"op": "read", "location": "context", "output": "read"}])], [local("read")]),
    }, {"context": ("runtime_context", "context")})
    seed = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="context"): frozenset({source.id})})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=seed)
    assert isinstance(result.registry.get(source.id).content, OpaqueContent)
    assert registry.to_dict() == result.initial_data
    assert result.coverage["ir_read"] == result.coverage["ir_return"] == "processed"
    error = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert error["observed_operations"][0]["record"]["op"] == "select_part"
    assert any(row["content"]["form"] == "known_parts" for row in error["observed_data"].values())
    assert error["observed_operations"][0]["record"]["outputs"][0]
    check_facts(cfg, annotation, result)


def test_failed_state_write_is_blocked_until_definite_independent_overwrite():
    cfg, annotation = fixture([
        instruction("bad"), instruction("dependent_read", outputs=["old"]),
        instruction("reset"), instruction("new_read", outputs=["new"]),
        instruction("return", [operand("new")], opcode="return"),
    ], {
        "bad": (["context_write", "transform"], [
            (0, [{"op": "write", "target": "x", "mode": "replace", "input": literal("prefix") }]),
            (1, [filtered(literal(1))])], []),
        "dependent_read": (["context_read"], [(0, [{"op": "read", "location": "x", "output": "old"}])], [local("old")]),
        "reset": (["context_write"], [(0, [{"op": "write", "target": "x", "mode": "replace", "input": literal("reset") }])], []),
        "new_read": (["context_read"], [(0, [{"op": "read", "location": "x", "output": "new"}])], [local("new")]),
    }, {"x": ("runtime_context", "x")})
    result = propagate(cfg, annotation)
    assert result.coverage["ir_dependent_read"] == "blocked"
    assert result.coverage["ir_reset"] == result.coverage["ir_new_read"] == result.coverage["ir_return"] == "processed"
    error = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert error["affected_instruction_ids"] == ["ir_bad", "ir_dependent_read", "ir_reset"]
    assert error["observed_operations"][0]["record"]["op"] == "write"
    check_facts(cfg, annotation, result)


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_failed_branch_control_blocks_arms_but_releases_verified_reconvergence(schedule):
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("bad", outputs=["bad"]), instruction("gate", [operand("bad")], opcode="dispatch")]),
        "left": block("left", [instruction("left"), instruction("left_next", opcode="dispatch")]),
        "right": block("right", [instruction("right"), instruction("right_next", opcode="dispatch")]),
        "join": block("join", [instruction("return", opcode="return")]),
    }, "edges": [{"source_block_id": a, "target_block_id": b} for a,b in
                 [("entry", "left"),("entry", "right"),("left", "join"),("right", "join")]]}
    cfg, annotation = fixture_annotation(cfg, {
        "bad": (["transform"], [(0,[filtered(literal(0))])], [local("bad")]),
        "gate": ([], [(None,[{"op":"branch", "input":input_ref(), "predicate":"truthy", "true_target":"left", "false_target":"right"}])], []),
    })
    result = propagate(cfg, annotation, schedule=schedule)
    assert result.coverage["ir_bad"] == "execution_error"
    assert all(result.coverage[ir] == "blocked" for ir in ("ir_gate","ir_left","ir_right","ir_left_next","ir_right_next"))
    assert result.coverage["ir_return"] == "processed"
    check_facts(cfg, annotation, result)


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_selected_guard_narrows_only_its_own_wrapper_version(schedule):
    cfg, annotation = fixture_annotation({"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("load", outputs=["wrapper", "other"]),
            instruction("gate", [operand("wrapper")], opcode="dispatch")]),
        "ok": block("ok", [instruction("use", [operand("wrapper")], ["rows"]),
                            instruction("ok_return", [operand("rows"), operand("other")], opcode="return")]),
        "error": block("error", [instruction("error_return", opcode="return")]),
    }, "edges": [{"source_block_id": "entry", "target_block_id": target} for target in ("ok", "error")]}, {
        "load": (["context_read"], [(0, [{"op": "read", "location": "wrappers", "output": "both"}])],
                 [local("both"), local("both")]),
        "gate": (["transform"], [(0, [
            {"op": "select_part", "input": input_ref(), "path": ["ok"], "output": "test"},
            {"op": "branch", "input": local("test"), "predicate": "truthy",
             "true_target": "ok", "false_target": "error"},
        ])], []),
        "use": (["transform"], [(0, [{"op": "select_part",
            "input": input_ref(), "path": ["rows"], "output": "rows"}])], [local("rows")]),
    }, {"wrappers": ("runtime_context", "fixture-wrappers")})
    from skillflow.propagation.data import LiteralContent
    registry = DataRegistry("guard-wrapper")
    good = registry.register_source("good", acquired_from="fixture:good",
                                    content=LiteralContent(value={"ok": True, "rows": [1]}))
    bad = registry.register_source("bad", acquired_from="fixture:bad",
                                   content=LiteralContent(value={"ok": False, "message": "failed"}))
    seed = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="fixture-wrappers"):
                                  frozenset({good.id, bad.id})})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=seed, schedule=schedule)
    assert result.status == "complete", result.diagnostics
    assert not any(row["code"] == "missing_part" for row in result.diagnostics)
    used = result.records.records_dict()["ir_use"]["entry_state"]
    assert result.coverage["ir_use"] == "processed"
    other = next(row for row in used["bindings"] if row["location"]["name"] == "other")
    assert set(other["data_ids"]) == {good.id, bad.id}
    check_facts(cfg, annotation, result)


def test_resource_abort_is_not_a_verified_inactive_path(monkeypatch):
    cfg, annotation = fixture([instruction("first"), instruction("return", opcode="return")], {})
    def exhausted(*args, **kwargs):
        raise PropagationLimitError("explicit fixture resource exhaustion")
    monkeypatch.setattr(TransferInterpreter, "evaluate", exhausted)
    result = propagate(cfg, annotation)
    assert result.status == "resource_limit"
    assert set(result.coverage.values()) == {"not_solved"}
    check_facts(cfg, annotation, result)


@pytest.mark.parametrize("error", [ValueError("unexpected invariant"), KeyError("missing internal table")])
def test_unknown_implementation_errors_remain_fatal(monkeypatch, error):
    cfg, annotation = fixture([instruction("return", opcode="return")], {})
    def broken(*args, **kwargs):
        raise error
    monkeypatch.setattr(TransferInterpreter, "evaluate", broken)
    with pytest.raises(type(error), match=str(error).strip("'")):
        propagate(cfg, annotation)


def test_for_each_object_failure_has_collection_scope_and_keeps_independent_return():
    from tests.propagation.test_collection_scopes import fixture as collection_fixture
    from skillflow.propagation.data import LiteralContent
    cfg, annotation = collection_fixture()
    registry = DataRegistry("object-for-each")
    source = registry.register_source("items", acquired_from="fixture", content=LiteralContent(value={"field": 1}))
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset({source.id})})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.coverage["ir_process"] == "execution_error"
    assert result.coverage["ir_return"] == "processed"
    failure = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert failure["scope"] == "element" and failure["event_index"] == 0
    assert failure["input_data_ids"] == [source.id]
    check_facts(cfg, annotation, result)


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_bad_and_good_predecessor_rows_keep_separate_dependency_scopes(schedule):
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("start", [{"type":"literal", "literal_value":True}], opcode="dispatch")]),
        "left": block("left", [instruction("left"), instruction("left_next", opcode="dispatch")]),
        "right": block("right", [instruction("right"), instruction("right_next", opcode="dispatch")]),
        "join": block("join", [instruction("read", outputs=["items"]), instruction("filter", [operand("items")], ["filtered"]),
                                 instruction("consume", [operand("filtered")]), instruction("return", opcode="return")]),
    }, "edges": [{"source_block_id": a, "target_block_id": b} for a,b in
                 [("entry", "left"),("entry", "right"),("left", "join"),("right", "join")]]}
    cfg, annotation = fixture_annotation(cfg, {
        "left": (["context_write"], [(0,[{"op":"write","target":"items","mode":"replace","input":literal({"bad":1})}])], []),
        "right": (["context_write"], [(0,[{"op":"write","target":"items","mode":"replace","input":literal(["good"])}])], []),
        "read": (["context_read"], [(0,[{"op":"read","location":"items","output":"items"}])], [local("items")]),
        "filter": (["transform"], [(0,[filtered(input_ref(), "filtered")])], [local("filtered")]),
        "consume": (["net_send"], [(0,[{"op":"deliver","target":"api","inputs":[input_ref()]}])], []),
    }, {"items":("runtime_context","items"),"api":("remote","api")})
    result = propagate(cfg, annotation, schedule=schedule)
    assert result.coverage["ir_filter"] == result.coverage["ir_consume"] == result.coverage["ir_return"] == "processed"
    error = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert error["affected_instruction_ids"] == ["ir_consume", "ir_filter"]
    sent = result.records.get("ir_consume").events[0].atomic_ops[0].inputs[0]
    assert sent
    assert all(result.registry.get(identity).content.form == "subset_view" for identity in sent)
    check_facts(cfg, annotation, result)


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_local_failure_inside_loop_does_not_stop_independent_loop_work(schedule):
    from tests.propagation.test_explicit_loops import explicit_loop_fixture
    cfg, annotation = explicit_loop_fixture()
    bad_cfg, bad_annotation = fixture([instruction("bad"), instruction("return", opcode="return")],
        {"bad":(["transform"],[(0,[filtered(literal(1))])],[])})
    cfg["blocks"]["body"]["instructions"].insert(0, bad_cfg["blocks"]["b"]["instructions"][0])
    annotation["ir_semantics"]["ir_bad"] = bad_annotation["ir_semantics"]["ir_bad"]
    result = propagate(cfg, annotation, schedule=schedule)
    assert result.status == "incomplete"
    assert result.coverage["ir_bad"] == "execution_error"
    assert all(result.coverage[ir] == "processed" for ir in ("ir_member","ir_fetch","ir_append","ir_return"))
    assert result.stats["block_evaluations"] < 40
    check_facts(cfg, annotation, result)


def test_forged_infeasible_coverage_without_guard_proof_is_rejected():
    cfg, annotation = fixture([instruction("return", opcode="return")], {})
    result = propagate(cfg, annotation)
    result.coverage["ir_return"] = "infeasible"
    result.records._records.clear()
    with pytest.raises(ValueError, match="infeasible coverage requires"):
        check_facts(cfg, annotation, result)


@pytest.mark.parametrize("layout", ["untyped_empty", "sparse"])
def test_collection_layout_domain_errors_are_local_without_weakening_the_guard(layout):
    from tests.propagation.test_collection_scopes import fixture as collection_fixture
    from skillflow.propagation.data import KnownPartsContent, DataPart, LiteralContent
    cfg, annotation = collection_fixture()
    registry = DataRegistry("collection-layout-" + layout)
    element = registry.register_source("element", acquired_from="fixture", content=LiteralContent(value="x"))
    source = registry.register_source("items", acquired_from="fixture", content=KnownPartsContent(
        parts=[] if layout == "untyped_empty" else [DataPart(path=[1], data=element.id)], parts_complete=True))
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="collection"): frozenset({source.id})})
    result = propagate(cfg, annotation, initial_registry=registry, initial_state=state)
    assert result.coverage["ir_process"] == "execution_error"
    assert result.coverage["ir_return"] == "processed"
    error = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert error["error_type"] == "DataDomainError"
    assert "contiguous integer" in error["reason"]
    assert error["input_data_ids"] == [source.id]
    check_facts(cfg, annotation, result)


def test_unknown_data_identity_error_is_not_reclassified_as_operand_domain(monkeypatch):
    from skillflow.propagation.data import DataReferenceError
    cfg, annotation = fixture([instruction("bad"), instruction("return", opcode="return")],
        {"bad":(["transform"],[(0,[filtered(literal([]))])],[])})
    def corrupt_lookup(self, identity, seen=frozenset()):
        raise DataReferenceError("unknown data ID: corrupt-internal-reference")
    monkeypatch.setattr(TransferInterpreter, "_require_collection_operand", corrupt_lookup)
    with pytest.raises(DataReferenceError, match="unknown data ID"):
        propagate(cfg, annotation)


def test_failure_position_and_prefix_data_bindings_are_checked():
    cfg, annotation = fixture([instruction("bad"), instruction("return", opcode="return")],
        {"bad":(["transform"],[(0,[compute(literal(1)),filtered(literal(0))])],[])})
    original = propagate(cfg, annotation)
    altered = deepcopy(original.diagnostics)
    original.diagnostics[0]["op_index"] = 1000
    with pytest.raises(ValueError, match="operation is outside"):
        check_facts(cfg, annotation, original)
    original.diagnostics = altered
    prefix_output = original.diagnostics[0]["observed_operations"][0]["record"]["outputs"][0][0]
    original.diagnostics[0]["observed_data"].pop(prefix_output)
    with pytest.raises(ValueError, match="lacks its detached Data"):
        check_facts(cfg, annotation, original)


def test_known_false_result_guard_does_not_consume_an_unavailable_member_value():
    cfg, annotation = fixture([
        instruction("flag", outputs=["flag"]), instruction("bad", outputs=["bad"]),
        instruction("optional", [operand("bad"),operand("flag")], ["safe"]),
        instruction("return", [operand("safe")], opcode="return"),
    ], {
        "flag":([],[],[literal(False)]),
        "bad":(["transform"],[(0,[filtered(literal(1))])],[local("bad")]),
        "optional":(["transform"],[(0,[{"op":"build","container":"object","parts":[
            {"path":["optional"],"value":input_ref(),"when":input_ref(1)}],"output":"safe"}])],[local("safe")]),
    })
    result = propagate(cfg, annotation)
    assert result.coverage["ir_optional"] == result.coverage["ir_return"] == "processed"
    error = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert error["affected_instruction_ids"] == ["ir_bad"]
    record = result.records.get("ir_optional").events[0].atomic_ops[0]
    assert record.members[0].value_input_index is None
    check_facts(cfg, annotation, result)


def test_missing_part_diagnostic_retains_its_literal_evidence_after_unresolved_attempt():
    cfg, annotation = fixture([instruction("select", outputs=["missing"]), instruction("return", opcode="return")],
        {"select":(["transform"],[(0,[{"op":"select_part","input":literal({"present":1}),
                "path":["absent"],"output":"missing"}])],[local("missing")])})
    result = propagate(cfg, annotation)
    assert result.coverage["ir_select"] == "unresolved_binding"
    assert any(row["code"] == "missing_part" for row in result.diagnostics)
    check_facts(cfg, annotation, result)


def test_known_nonboolean_result_guard_is_a_local_domain_error():
    cfg, annotation = fixture([
        instruction("flag", outputs=["flag"]), instruction("conditional", [operand("flag")], ["bad"]),
        instruction("return", opcode="return"),
    ], {
        "flag":([],[],[literal("not-a-Boolean")]),
        "conditional":(["transform"],[(0,[{"op":"build","container":"object","parts":[
            {"path":["optional"],"value":literal("x"),"when":input_ref()}],"output":"bad"}])],[local("bad")]),
    })
    result = propagate(cfg, annotation)
    assert result.coverage["ir_conditional"] == "execution_error"
    assert result.coverage["ir_return"] == "processed"
    error = next(row for row in result.diagnostics if row["code"] == "operation_execution_error")
    assert error["error_type"] == "ConditionDomainError"
    assert error["input_data_ids"]
    assert all(error["observed_data"][key]["content"]["value"] == "not-a-Boolean" for key in error["input_data_ids"])
    check_facts(cfg, annotation, result)
