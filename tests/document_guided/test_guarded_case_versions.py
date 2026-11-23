"""Source-backed shared selections survive wire lowering and real propagation."""
import pytest
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.binding_examples import (
    _fixture, evidence, example_material, inp, instruction, literal, local, result)
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.solver import propagate
from skillflow.propagation.loading import materials_from_result
from skillflow.doe.sensitivity_material import prepare_joint_sensitivity_review
from tests.doe.test_input_contract_preservation import accepted_receipt


def versions(shared=True, known=None, send=False, require_action=False, partitions=None, guard_path=(),
             payload_path=None, components=4):
    input_description = "the same supplied value" if shared else "its independently acquired value"
    source = (f"Each component returns object, text, or default according to {input_description}. "
              "A nonempty string is text; an empty string takes the default. Only the object case sends.")
    if partitions:
        source = f"Each component labels the first matching test in its ordered partition, otherwise the remainder. Partitions: {partitions!r}"
    names = ["v" + str(i) for i in range(components)]
    sources = [] if known is not None else (["source"] if shared else ["source_" + n for n in names])
    args = [literal(known) if known is not None else result(sources[0 if shared else i]) for i in range(components)]
    instructions = [instruction("ir_"+s, "acquire", [], s) for s in sources]
    instructions += [instruction("ir_"+n, "component", [arg], n) for n, arg in zip(names, args)]
    instructions += [instruction("ir_build", "compose", [result(n) for n in names], "report"),
                     instruction("ir_end", "return", [result("report")])]
    material = example_material(_fixture("typed_case_versions", source, source, instructions, {}))
    ev = [evidence()]
    semantics = {"ir_"+s: {"evidences":ev, "segments":[{"mode":"local", "returns":[],"ops":[{"op":"read",
        "location":s,"output":"value"}]}], "output_bindings":[{"output_index":0,"value":local("value")}]}
        for s in sources}
    for component, name in enumerate(names):
        cases = []
        tests = partitions[component] if partitions else [{"kind":"object"},{"kind":"nonempty_string"}]
        labels = [f"match_{i}" for i in range(len(tests))] + ["default"] if partitions else ["object", "text", "default"]
        for outcome, label in enumerate(labels):
            segments = []
            if send and outcome == 0:
                segments = [{"mode":"local", "returns":[], "ops":[{"op":"deliver", "target":"user", "inputs":[inp()]}]}]
                if require_action:
                    segments[0]["ops"][0]["demands"] = [{
                        "requirement_id": "R1", "target": {"kind": "self"}, "preserve": "action",
                        "reason": "Deliver when the supplied object selects the sending case."}]
            cases.append({"name":label, "phase":"normal", "disposition":"return", "condition":label,
                          "segments":segments, "yield":{"kind":"literal", "value":label},
                          "guard":{"input_index":0, "path":list(guard_path), "tests":tests,
                                   "outcome":outcome}})
        semantics["ir_"+name] = {"evidences":ev, "segments":[{"kind":"cases","cases":cases,"output":"chosen"}],
                                 "output_bindings":[{"output_index":0,"value":local("chosen")}]}
    semantics["ir_build"] = {"evidences":ev, "segments":[{"mode":"local", "returns":[], "ops":[{"op":"build","container":"object",
        "parts":[{"path":[name],"value":inp(i)} for i,name in enumerate(names)], "output":"assembled"}]}],
        "output_bindings":[{"output_index":0,"value":local("assembled")}]}
    semantics["ir_end"] = {"evidences":ev}
    wire = {"outcome":"completed", "realizations":[{"requirement_id":"R1"}], "ir_semantics":semantics,
            "locations":{**{s:{"kind":"runtime_context","name":s,"evidences":ev} for s in sources},
                         **({"user":{"kind":"user","name":"caller","evidences":ev}} if send else {})},
            "demands":[{"requirement_id":"R1", "target":{"instruction_id":"ir_build","side":"output","index":0},
                        "preserve":"value","reason":source}]}
    if require_action:
        wire["demands"] = []
    if payload_path is not None:
        wire["demands"].append({"requirement_id": "R1", "target": {"instruction_id": "ir_v0", "side": "input", "index": 0},
                                "preserve": "value", "path": list(payload_path), "reason": "Preserve the specified payload field."})
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    return material, raw, compiled, mapping, saved


@pytest.mark.parametrize(("shared", "components", "expected"), [
    pytest.param(True, 4, 3, id="True-3"),
    pytest.param(False, 2, 9, id="False-9"),
    pytest.param(False, 4, 81, id="four-independent-81"),
])
def test_shared_version_and_distinct_versions_have_different_compatible_products(shared, components, expected):
    material, _, compiled, _, _ = versions(shared, components=components)
    records = []
    for schedule in ("fifo","lifo"):
        solved = propagate(material["cfg"], to_payload(compiled), schedule=schedule)
        assert solved.status == "complete", solved.diagnostics
        operation = solved.records.get("ir_build").events[0].atomic_ops[0]
        assert len(operation.alternatives) == len(operation.outputs[0]) == expected
        assert len(operation.inputs) == components
        records.append(solved.records.records_dict())
    assert records[0] == records[1]


def test_different_predicates_and_reordered_partitions_join_on_the_same_immutable_value():
    partitions = [
        [{"kind": "object"}, {"kind": "nonempty_string"}],
        [{"kind": "nonempty_string"}, {"kind": "object"}],
        [{"kind": "string"}, {"kind": "equals", "value": ""}],
        [{"kind": "equals", "value": "named"}, {"kind": "nonempty_string"}],
    ]
    material, _, compiled, _, _ = versions(partitions=partitions)
    records = []
    for order in ("fifo", "lifo"):
        solved = propagate(material["cfg"], to_payload(compiled), schedule=order)
        assert solved.status == "complete", solved.diagnostics
        # The five possible classes are object, empty string, named, other text, and remainder.
        build = solved.records.get("ir_build").events[0].atomic_ops[0]
        assert len(build.alternatives) == len(build.outputs[0]) == 5
        records.append(solved.records.records_dict())
    assert records[0] == records[1]


def test_empty_string_selects_default_and_does_not_deliver():
    material, raw, compiled, mapping, wire = versions(known="", send=True)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    op = solved.records.get("ir_v0").events[0].atomic_ops[0]
    assert op.skipped_case_inputs and not op.inputs and not op.endpoints
    assert len(solved.records.get("ir_build").events[0].atomic_ops[0].outputs[0]) == 1
    solved.records.validate(require_complete=True)
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    review = prepare_joint_sensitivity_review(facts, facts.annotation,
        input_contract_review=accepted_receipt(facts, facts.annotation))
    assert not review.to_dict()["sinks"]


def test_required_outputs_retain_case_controls_and_original_observation():
    material, raw, compiled, mapping, wire = versions(send=True)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    facts.record_store.validate(require_complete=True)
    assert solved.records.get("ir_v0").events[0].atomic_ops[0].alternatives[0].bindings
    review = prepare_joint_sensitivity_review(facts, facts.annotation,
        input_contract_review=accepted_receipt(facts, facts.annotation))
    tracked = [row for row in review.demand_dict()["derivations"].values() if "typed_case_selector" in row["rules"]]
    assert {row["node"]["instruction_id"] for row in tracked} == {f"ir_v{i}" for i in range(4)}
    assert all(row["node"]["kind"] == "ir_input" and row["node"]["slot"] == 0 for row in tracked)


@pytest.mark.parametrize("known, active", [(None, True), ("", False)])
def test_conditional_required_delivery_retains_its_selector_only_when_applicable(known, active):
    material, raw, compiled, mapping, wire = versions(known=known, send=True, require_action=True)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    review = accepted_receipt(facts, facts.annotation)
    by_order = [
        prepare_joint_sensitivity_review(facts, facts.annotation,
            input_contract_review=review, queue_order=order).demand_dict()
        for order in ("fifo", "lifo")]
    demand, other = by_order
    assert demand == other
    selectors = [row for row in demand["derivations"].values() if "typed_case_selector" in row["rules"]]
    actions = [row for row in demand["derivations"].values() if "task_action" in row["rules"]]
    if active:
        assert len(actions) == len(selectors) == 4
        assert {row["seed_goal_id"] for row in selectors} == {row["seed_goal_id"] for row in actions}
    else:
        assert selectors == actions == []
        assert any(row["code"] == "inactive_goal" for row in demand["diagnostics"])


@pytest.mark.parametrize("test, expected", [("object", "truth"), ("missing", "presence")])
@pytest.mark.parametrize("with_payload", [False, True])
def test_decision_on_field_does_not_require_its_contents_or_erase_another_actual_demand(test, expected, with_payload):
    material, raw, compiled, mapping, wire = versions(
        known={"subject": {"audit": "internal", "keep": "required elsewhere"}},
        partitions=[[{"kind": test}]] * 4, guard_path=["subject"],
        payload_path=["subject", "keep"] if with_payload else None)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=wire)
    demand = prepare_joint_sensitivity_review(facts, facts.annotation,
        input_contract_review=accepted_receipt(facts, facts.annotation)).demand_dict()
    ranges = next(row["ranges"] for row in demand["input_assessments"]
                  if row["instruction_id"] == "ir_v0" and row["node_kind"] == "ir_input")
    claims = {(row["property"], tuple(row["path"]), row["status"]) for row in ranges}
    assert (expected, ("subject",), "required") in claims
    assert ("value", ("subject",), "required") not in claims
    assert ("value", ("subject",), "deletable") not in claims
    assert ("value", ("subject", "audit"), "deletable") in claims
    assert ("value", ("subject", "keep"), "required" if with_payload else "deletable") in claims
    decision = next(row for row in ranges if row["property"] == expected and row["status"] == "required")
    assert "skill/SKILL.md" in decision["reason"]
    assert all(demand["derivations"][ref]["selector_ref"] for ref in decision["demand_refs"])


@pytest.mark.parametrize("schedule", ["fifo", "lifo"])
def test_success_edge_refines_same_version_of_tagged_wrapper(schedule):
    from examples.propagation.propagation_demo import fixture_annotation, instruction as ir, operand
    def block(name, instructions):
        return {"block_id":name, "block_name":name, "instructions":instructions}
    cfg = {"entry_block_id":"entry", "blocks":{
        "entry":block("entry", [ir("wrapper",outputs=["r"]), ir("route",[operand("r")], opcode="dispatch")]),
        "success":block("success",[ir("get",[operand("r")], ["v"]),ir("stop",[operand("v")],opcode="return")]),
        "failed":block("failed",[ir("error",opcode="return")])},
        "edges":[{"source_block_id":"entry","target_block_id":k} for k in ("success","failed")]}
    values = [{"kind":"literal","value":v} for v in ({"status":"fulfilled","value":7},{"status":"rejected","reason":"failure"})]
    plans = {"wrapper":([],[],[{"kind":"alternatives","items":values}]),
             "route":([],[(None,[{"op":"branch","input":inp(),"predicate":"truthy",
                                 "true_target":"success","false_target":"failed"}])],[]),
             "get":(["transform"],[(0,[{"op":"select_part","input":inp(),"path":["value"],"output":"v"}])],[local("v")])}
    cfg, annotation = fixture_annotation(cfg, plans)
    branch = annotation["ir_semantics"]["ir_route"]["events"][0]["atomic_ops"][0]
    branch.update(predicate="selector", selector={"path":["status"],"tests":[{"kind":"equals","value":"fulfilled"}],"outcome":0},
                  evidences=[evidence()])
    solved = propagate(cfg, annotation, schedule=schedule)
    assert solved.status == "complete", solved.diagnostics
    assert not any(d["code"]=="missing_part" for d in solved.diagnostics)
    routes = solved.records.get("ir_route").events[0].atomic_ops[0].alternatives
    assert sorted(row.branch_targets for row in routes) == [["failed"],["success"]]


def test_repeated_cfg_test_on_unknown_root_excludes_contradictory_route():
    from examples.propagation.propagation_demo import fixture_annotation, instruction as ir, operand
    def block(name, instructions):
        return {"block_id":name, "block_name":name, "instructions":instructions}
    cfg = {"entry_block_id":"start","blocks":{
        "start":block("start",[ir("read",outputs=["r"]),ir("route",[operand("r")],opcode="dispatch")]),
        "again":block("again",[ir("retest",[operand("r")],opcode="dispatch")]),
        **{name:block(name,[ir(name,opcode="return")]) for name in ["other","good","contradiction"]}},
        "edges":[{"source_block_id":s,"target_block_id":t} for s,t in [
            ("start","again"),("start","other"),("again","good"),("again","contradiction")]]}
    plans = {"read":(["context_read"],[(0,[{"op":"read","location":"src","output":"input"}])],[local("input")])}
    for name,pos,neg in [("route","again","other"),("retest","good","contradiction")]:
        plans[name]=([],[(None,[{"op":"branch","predicate":"truthy","input":inp(),
                                 "true_target":pos,"false_target":neg}])],[])
    cfg,annotation=fixture_annotation(cfg,plans,{"src":("runtime_context","input")})
    for name in ("ir_route","ir_retest"):
        annotation["ir_semantics"][name]["events"][0]["atomic_ops"][0].update(predicate="selector",
            selector={"path":["status"],"tests":[{"kind":"equals","value":"fulfilled"}],"outcome":0},evidences=[evidence()])
    solved = propagate(cfg,annotation)
    assert solved.status == "complete", solved.diagnostics
    assert solved.coverage["ir_contradiction"] == "infeasible"
    assert solved.coverage["ir_good"] == solved.coverage["ir_other"] == "processed"
    solved.records.validate(require_complete=True)


def test_required_action_on_typed_cfg_edge_needs_subject_decision_and_preserves_child_removal():
    from skillflow.doe.constraint_preservation import ForwardInfluence
    from skillflow.doe.demand_engine import DemandEngine
    from skillflow.doe.demand_index import build_demand_target_index
    from skillflow.doe.sensitivity_material import joint_demands
    from skillflow.propagation.contracts.task import Task
    source = "Deliver a fixed message when subject is an object. Its child note is not part of the condition."
    example = _fixture("conditional_delivery", source, source,
        [instruction("ir_route", "dispatch", [literal({"subject": {"note": "irrelevant"}})])], {})
    cfg = example["cfg"]
    for name, instructions in {"yes": [instruction("ir_send", "notify", []), instruction("ir_yes", "return", [])],
                               "no": [instruction("ir_no", "return", [])]}.items():
        cfg["blocks"][name] = {"block_id": name, "block_name": name, "instructions": instructions,
                               "constraints": [], "data_source_kind": None}
        cfg["edges"].append({"source_block_id": "sample", "target_block_id": name, "condition_text": None})
    material = example_material(example)
    ev = [evidence()]
    route = {"op": "branch", "predicate": "selector", "selector": {"tests": [{"kind": "object"}],
             "path": ["subject"], "outcome": 0}, "input": inp(), "true_target": "yes", "false_target": "no"}
    action = {"op": "deliver", "target": "user", "inputs": [{"kind": "literal", "value": "ready"}],
              "demands": [{"requirement_id": "R1", "target": {"kind": "self"}, "preserve": "action", "reason": source}]}
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}], "ir_semantics": {
        "ir_route": {"evidences": ev, "segments": [{"mode": "local", "ops": [route], "returns": []}]},
        "ir_send": {"evidences": ev, "segments": [{"mode": "local", "ops": [action], "returns": []}]},
        "ir_yes": {"evidences": ev}, "ir_no": {"evidences": ev}},
        "locations": {"user": {"kind": "user", "name": "caller", "evidences": ev}}, "demands": []}
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    facts = materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved)
    engine = DemandEngine(facts, Task.model_validate(material["task"]), facts.annotation,
        joint_demands(facts.annotation), build_demand_target_index(facts.cfg, facts.raw_annotation),
        input_contract_review=accepted_receipt(facts, facts.annotation))
    demand = engine.solve()
    assert solved.coverage["ir_no"] == "infeasible"
    for kind in ("op_input", "ir_input"):
        assessment = next(row for row in demand["input_assessments"] if
                          row["instruction_id"] == "ir_route" and row["node_kind"] == kind)
        assert any(row["property"] == "truth" and row["path"] == ["subject"] and row["status"] == "required"
                   for row in assessment["ranges"])
        assert any(row["path"] == ["subject", "note"] and row["status"] == "deletable" for row in assessment["ranges"])
    graph = ForwardInfluence(engine)
    branch = next(k for k, op in engine.ops.items() if op["spec"]["op"] == "branch")
    assert "ir_send" not in graph.run(branch, 0, ["subject", "note"])["control_instructions"]
    assert "ir_send" in graph.run(branch, 0, ["subject"])["control_instructions"]
    from copy import deepcopy
    from skillflow.doe.demand_results import validate_result_references
    corrupted = deepcopy(demand)
    proof = next(row for row in corrupted["derivations"].values() if row.get("selector_ref"))
    proof["selector_ref"] = "selector_missing"
    with pytest.raises(ValueError, match="selector reference"):
        validate_result_references(corrupted, facts, engine.targets,
                                   engine=engine, input_contract_review=engine.contracts.receipt)


def test_plain_truth_still_retains_content_and_an_earlier_array_edit_preserves_selector_address():
    from skillflow.doe.sensitivity_engine import demand_overlap
    demand = {"property": "truth", "path": ["rows", 1], "each": False, "excluded_paths": [], "conservative": False}
    descendant = {"property": "value", "path": ["rows", 1, "note"], "excluded_paths": []}
    assert demand_overlap(descendant, demand) == "retain"
    certified = {**demand, "selector_ref": "checked-through-reference-validation"}
    assert demand_overlap(descendant, certified) == "none"
    assert demand_overlap({**descendant, "path": ["rows", 0]}, certified) == "structure"
    assert demand_overlap({**descendant, "path": ["rows", 0, "note"]}, certified) == "none"
