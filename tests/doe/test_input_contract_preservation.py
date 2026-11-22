"""Reviewed input independence is shared by demand, change and DOE checks."""
from copy import deepcopy

import pytest

from skillflow.doe.constraint_preservation import ForwardInfluence
from skillflow.doe.demand_engine import DemandEngine
from skillflow.doe.input_contract_review import build_input_contract_review, input_contract_binding, SOURCE_REVIEW_VERSION
from skillflow.doe.sensitivity_material import prepare_sensitivity_review, validate_sensitivity_result
from skillflow.propagation.contracts.demand import validate_demand_candidate
from skillflow.propagation.contracts.joint import joint_source_files
from tests.doe.test_demand_engine import candidate, evidence, fixture, inp
from tests.doe.test_sensitivity_engine import declarations, rows


def accepted_receipt(facts, annotation):
    from tests.doe.test_reviewed_input_necessity import receipt
    return receipt((facts, None, annotation, None))



def reviewed_fixture(required, *, transfer=None, requested_path=(), constraints=None, custom=None):
    transfer = transfer or {"rules": [{"output": {"property": "value", "path": []},
        "inputs": [{"input_index": 0, "required": required,
            "remainder": "independent",
            "reason": "The output specification uses only the stated fields; all other input information is irrelevant."}],
        "reason": "The retained fields suffice for the specified output without the excluded information.",
        "evidences": [evidence()]}]}
    def attach_constraints(prepared, raw, evidences):
        if constraints:
            raw["realizations"][0]["constraints"] = deepcopy(constraints)
        if custom:
            custom(prepared, raw, evidences)
    values = fixture([{"op": "compute", "inputs": [inp()], "dependencies": ["possible"],
        "output": "answer", "demand_transfer": transfer}], mode="model", custom=attach_constraints)
    facts, task, annotation, targets = values
    files = joint_source_files(annotation["material"])
    receipt = accepted_receipt(facts, annotation)
    request = candidate(targets, path=requested_path)
    checked = validate_demand_candidate(request, task=task, source_files=files, targets=targets)
    engine = DemandEngine(facts, task, annotation, checked.model_dump(mode="json"), targets,
                          input_contract_review=receipt)
    return values, receipt, request, engine


def observation(engine):
    return next(key for key, info in engine.ops.items()
                if info["generated"] and info["position"]["instruction_id"] == "ir_filter")


def test_reviewed_independent_field_stops_forward_change_without_erasing_actual_observation():
    values, receipt, request, engine = reviewed_fixture([{"property": "value", "path": ["body"]}])
    original = deepcopy((values[0].records, values[0].data, values[0].sinks))
    graph = ForwardInfluence(engine)
    changed = graph.run(observation(engine), 0, ["token"])
    assert changed["complete"]
    assert not any(engine.nodes[row["node"]]["kind"] == "op_output" for row in changed["steps"].values())
    required = graph.run(observation(engine), 0, ["body"])
    assert any(row["rule"] == "reviewed_input_contract_change" for row in required["steps"].values())
    assert "ir_return" in required["instructions"]
    assert graph.run(observation(engine), 0, ["token"], queue_order="lifo") == changed
    assert (values[0].records, values[0].data, values[0].sinks) == original


def test_unreviewed_contract_does_not_suppress_forward_change():
    values, _, request, _ = reviewed_fixture([{"property": "value", "path": ["body"]}])
    facts, task, annotation, targets = values
    checked = validate_demand_candidate(request, task=task,
        source_files=joint_source_files(annotation["material"]), targets=targets)
    engine = DemandEngine(facts, task, annotation, checked.model_dump(mode="json"), targets)
    changed = ForwardInfluence(engine).run(observation(engine), 0, ["token"])
    assert any(row["rule"] == "conservative_processing_change" for row in changed["steps"].values())


def test_complete_output_decomposition_limits_change_to_the_affected_output_field():
    rules = [{"output": {"property": "value", "path": ["report", output]},
        "inputs": [{"input_index": 0, "required": [{"property": "value", "path": [source]}],
            "remainder": "independent", "reason": "This result field uses only its corresponding source field."}],
        "reason": "The result has two independent components with the stated field relationships.",
        "evidences": [evidence()]} for output, source in (("public", "body"), ("private", "token"))]
    _, _, _, engine = reviewed_fixture([], transfer={"rules": rules,
        "output_parts": [row["output"] for row in rules]}, requested_path=["report", "public"])
    changed = ForwardInfluence(engine).run(observation(engine), 0, ["token"])
    assert changed["complete"]
    paths = [row["path"] for row in changed["steps"].values()
             if engine.nodes[row["node"]]["kind"] == "op_output"]
    assert paths and all(path == ["report", "private"] for path in paths)


def test_independent_model_input_removal_preserves_ban_and_keeps_original_violation():
    from skillflow.doe.constraint_preservation import ConstraintAnalysis
    constraints = [{"kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_filter", "scope_path": [], "value": inp()},
        "path": ["token"], "receivers": {"kind": "kind", "value": "model_context"}}]
    values, _, _, engine = reviewed_fixture([{"property": "value", "path": ["body"]}],
                                            constraints=constraints)
    analysis = ConstraintAnalysis(engine)
    before = deepcopy(analysis.checks)
    assert {row["status"] for row in before.values()} == {"potential_violation"}
    observed = observation(engine)
    data_id = engine.ops[observed]["record"]["inputs"][0][0]
    references, preserved = analysis.evaluate(observed, 0, data_id, ["token"])
    assert preserved and references
    assert {analysis.preservation[ref]["rule"] for ref in references} == {"receiver_subset"}
    assert analysis.checks == before


def test_tool_interface_extra_field_does_not_change_paired_response():
    from skillflow.doe.demand_index import build_demand_target_index
    from skillflow.doe.sensitivity_material import joint_demands
    from skillflow.propagation.contracts.task import Task
    from skillflow.propagation.annotation.binding_examples import evidence as interface_evidence
    from tests.doe.test_sink_payload_seeds import synthetic_fixture
    contract = {"inputs": [{"input_index": 0,
        "required": [{"property": "value", "path": ["display"]}],
        "remainder": "independent", "reason": "The interface requires only display; service_note is not an interface input."}],
        "reason": "The tool returns the label computed solely from its display input.",
        "evidences": [interface_evidence()]}
    material, raw, facts = synthetic_fixture([
        {"op": "deliver", "target": "label_receiver", "inputs": [inp()], "input_contract": contract},
        {"op": "receive", "location": "label_receiver", "inputs": [inp()], "output": "receipt",
         "input_contract": contract}], output="receipt", return_demand=True,
        source="The label tool requires only the display field and returns that label; service_note is extra.")
    annotation = facts.annotation
    receipt = accepted_receipt(facts, annotation)
    engine = DemandEngine(facts, Task.model_validate(material["task"]), annotation,
        joint_demands(annotation), build_demand_target_index(facts.cfg, raw), input_contract_review=receipt)
    delivery = next(key for key, info in engine.ops.items() if info["spec"]["op"] == "deliver")
    response = next(key for key, info in engine.ops.items() if info["spec"]["op"] == "receive")
    graph = ForwardInfluence(engine)
    changed = graph.run(delivery, 0, ["service_note"])
    assert changed["complete"] and response not in changed["affected"]
    assert not any(row["rule"] == "request_response_change" for row in changed["steps"].values())
    required = graph.run(delivery, 0, ["display"])
    assert response in required["affected"]
    assert any(row["rule"] == "request_response_change" for row in required["steps"].values())


def test_no_demand_after_review_supports_whole_input_removal_and_keeps_original_exposure():
    values, receipt, request, _ = reviewed_fixture([])
    facts, task, annotation, _ = values
    original = deepcopy((facts.records, facts.data, facts.sinks))
    review = prepare_sensitivity_review(facts, task, annotation, request, declarations(),
                                       input_contract_review=receipt)
    result = review.to_dict()
    compared = rows(result)
    assert compared and {row["conclusion"] for row in compared} == {"excess_supported"}
    assert all(row["reduction"] == {"kind": "remove_input"} and row["assessment_refs"] for row in compared)
    assert all(not row["demand_refs"] for row in compared)
    assert (facts.records, facts.data, facts.sinks) == original
    assert validate_sensitivity_result(result, facts, task, annotation, request, declarations(),
        demand_result=review.demand_dict(), input_contract_review=receipt) == result


def test_loader_rejects_changed_assessment_reference_or_reduction_kind():
    values, receipt, request, _ = reviewed_fixture([])
    facts, task, annotation, _ = values
    review = prepare_sensitivity_review(facts, task, annotation, request, declarations(),
                                       input_contract_review=receipt)
    for change in ({"assessment_refs": ["missing_assessment"]},
                   {"reduction": {"kind": "exclude_field", "path": ["token"]}}):
        altered = review.to_dict()
        altered["sinks"][0]["data_reviews"][0].update(change)
        with pytest.raises(ValueError, match="assessment|reduction"):
            validate_sensitivity_result(altered, facts, task, annotation, request, declarations(),
                demand_result=review.demand_dict(), input_contract_review=receipt)


def test_report_includes_full_input_audit_without_any_sensitive_declarations():
    from skillflow.doe.sensitivity_report import build_view, render_html, render_markdown
    values, receipt, request, _ = reviewed_fixture([])
    facts, task, annotation, _ = values
    review = prepare_sensitivity_review(facts, task, annotation, request,
        {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": []}, input_contract_review=receipt)
    demand = review.demand_dict()
    view = build_view(review, metadata={"demand": {"input_assessments": [], "input_findings": []}})
    assert sum(view["counts"].values()) == 0
    assert view["input_assessments"] == demand["input_assessments"]
    assert view["input_findings"] == demand["input_findings"]
    assert view["input_findings"]
    for rendered in (render_html(review), render_markdown(review)):
        assert "All input assessments" in rendered and "Semantic findings" in rendered
        assert all(item["id"] in rendered for item in demand["input_assessments"])
        assert all(item["id"] in rendered for item in demand["input_findings"])


def test_unrelated_same_ir_contract_gap_does_not_contaminate_an_independent_sink():
    from skillflow.propagation.contracts.task import Task
    from skillflow.propagation.annotation.binding_examples import evidence as source_evidence
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, declared_goal
    transfer = {"rules": [{"output": {"property": "value", "path": ["body"]},
        "inputs": [{"input_index": 0, "required": [{"property": "value", "path": ["display"]}],
            "remainder": "independent", "reason": "The body copies only display; other input fields do not supply it."}],
        "reason": "The known body result is the source display field.", "evidences": [source_evidence()]}]}
    material, _, facts = synthetic_fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "good",
         "demand_transfer": transfer},
        {"op": "deliver", "target": "label_receiver", "inputs": [{"kind": "local", "name": "good"}],
         "demands": [declared_goal("input", index=0, path=["body"])]},
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "bad"}],
        output="bad", return_demand=True, processing_mode="default",
        source="Send only the display body from the first result; its token is sensitive. Return the separate second calculation.")
    annotation = facts.annotation
    declared = {"schema_version": "skillflow-sensitivity-candidate-v1", "scopes": [{
        "instruction_id": "ir_format", "scope_path": [], "declarations": [{
            "value": {"kind": "local", "name": "good"}, "path": ["token"], "property": "value",
            "label": "credential", "evidences": [source_evidence()]}]}]}
    reviewed = prepare_sensitivity_review(facts, Task.model_validate(material["task"]), annotation,
        sensitivity_candidate=declared, input_contract_review=accepted_receipt(facts, annotation))
    result = reviewed.to_dict()
    assert result["status"] == "partial"
    assert any(row["code"].startswith("input_contract_") for row in result["diagnostics"])
    receiver = [sink for sink in result["sinks"] if sink["boundary"]["sink_type"] == "external_tool"]
    assert len(receiver) == 1 and receiver[0]["data_reviews"]
    assert not receiver[0]["limitations"]
    assert {row["conclusion"] for row in receiver[0]["data_reviews"]} == {"excess_supported"}


@pytest.mark.parametrize("path", [[0], [{"kind": "each"}], [{"kind": "element", "scope": "one-member"}]])
def test_information_only_member_removal_is_not_an_array_reindex_instruction(path):
    from skillflow.doe.input_assessments import deletable_reduction
    result = {"input_assessments": [{"id": "A", "node_kind": "op_input", "operation_id": "O",
        "input_index": 0, "data_ids": ["D"], "coverage": "processed",
        "ranges": [{"status": "deletable", "path": path, "excluded_paths": []}]}]}
    assert deletable_reduction(result, "O", 0, "D", path) == (None, [])
    result["input_assessments"][0]["ranges"][0]["path"] = []
    assert deletable_reduction(result, "O", 0, "D", path) == ({"kind": "remove_input"}, ["A"])


def test_nested_known_parts_use_the_recorded_child_data_identity():
    from skillflow.doe.input_assessments import _known_paths
    data = {"outer": {"content": {"form": "known_parts", "parts": [{"path": ["profile"], "data": "inner"}]}},
        "inner": {"content": {"form": "known_parts", "parts": [{"path": ["token"], "data": "token"}]}},
        "token": {"content": {"form": "literal", "value": "credential"}}}
    assert _known_paths(data, ["outer"]) == [["profile"], ["profile", "token"]]


def test_declared_opaque_field_candidates_are_exact_to_the_recorded_data_version():
    from skillflow.doe.input_assessments import _declared_paths, _reference_index
    def attach(prepared, raw, ev):
        raw["ir_semantics"]["ir_filter"]["sensitivity"] = [{"value": inp(), "path": ["credential"],
            "property": "value", "label": "credential", "evidences": [evidence()]}]
    _, _, _, engine = reviewed_fixture([{"property": "value", "path": ["body"]}], custom=attach)
    _, references, scopes, _ = _reference_index(engine)
    paths = _declared_paths(engine, references, scopes)
    source = next(iter(references(inp(), "ir_filter")))
    computed = next(info["record"]["outputs"][0][0] for info in engine.ops.values()
                    if info["spec"]["op"] == "compute")
    assert set(paths) == set(engine.nodes[source]["data_ids"])
    assert computed not in paths
    result = engine.solve()
    acquired = next(row for row in result["input_assessments"] if row["node_kind"] == "acquisition_output")
    assert any(row["path"] == ["credential"] and row["status"] == "deletable" for row in acquired["ranges"])
    assert all("interface" in row["reason"] for row in acquired["ranges"] if row["status"] == "deletable")


def test_constraint_named_field_remains_actionable_but_unknown_complement_has_exact_witness():
    from tests.doe.test_demand_engine import local
    constraints = [{"kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_filter", "scope_path": [], "value": inp()},
        "path": ["token"], "receivers": {"kind": "locations", "ids": ["checked_tool"]}}]
    def attach(prepared, raw, ev):
        raw["locations"]["checked_tool"] = {"kind": "tool", "name": "checked_tool", "operand_refs": [],
            "access_scope": "recipient", "retention": None}
        raw["location_evidences"]["checked_tool"] = deepcopy(ev)
        raw["ir_semantics"]["ir_filter"]["events"].append({"kind": "processing", "mode": "default",
            "returns": [], "evidences": deepcopy(ev), "events": [{"effect": None, "evidences": [], "atomic_ops": [
                {"op": "deliver", "target": "checked_tool", "inputs": [local("answer")], "evidences": deepcopy(ev)},
                {"op": "receive", "location": "checked_tool", "inputs": [local("answer")],
                 "output": "unused_receipt", "evidences": deepcopy(ev)}]}]})
    _, _, _, engine = reviewed_fixture([{"property": "value", "path": ["body"]}],
        constraints=constraints, custom=attach)
    result = engine.solve()
    acquired = next(row for row in result["input_assessments"]
                    if row["node_kind"] == "acquisition_output" and row["instruction_id"] == "ir_read")
    token = [row for row in acquired["ranges"] if row["path"] == ["token"]]
    assert token and {row["status"] for row in token} == {"deletable"}
    remainder = [row for row in acquired["ranges"] if row["status"] == "unresolved" and row["excluded_paths"]]
    assert len(remainder) == 1
    assert ["body"] in remainder[0]["excluded_paths"] and ["token"] in remainder[0]["excluded_paths"]
    assert "/realizations/0/constraints/0" in remainder[0]["reason"]
    assert "op_ir_filter" in remainder[0]["reason"]


def test_acquired_output_checks_actual_consumers_before_claiming_constraint_preservation():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints
    from tests.doe.test_demand_engine import local, literal
    base = synthetic_fixture([
        {"op": "read", "location": "context", "output": "source"},
        {"op": "compute", "inputs": [local("source")], "dependencies": ["possible"], "output": "converted"},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("converted")]},
        {"op": "receive", "location": "label_receiver", "inputs": [local("converted")], "output": "receipt"},
        {"op": "build", "container": "object", "parts": [{"path": ["answer"], "value": literal(True)}],
         "output": "formatted"}], return_demand=True,
        extra_locations={"context": {"kind": "runtime_context", "name": "supplied", "operand_refs": [],
            "access_scope": "task", "retention": "task"}})
    constrained = with_constraints(base, [{"kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_format", "scope_path": [], "value": local("source")},
        "path": ["token"], "receivers": {"kind": "locations", "ids": ["label_receiver"]}}])
    engine, result = solve_fixture(constrained)
    source = next(key for key, info in engine.ops.items() if info["spec"]["op"] == "read")
    acquired = next(row for row in result["input_assessments"] if row["node_kind"] == "acquisition_output"
                    and row["operation_id"] == source)
    assert {row["status"] for row in acquired["ranges"]} == {"unresolved"}
    assert all("/realizations/0/constraints/0" in row["reason"] for row in acquired["ranges"])


def test_acquired_output_direct_control_expression_is_not_vacuously_preserved():
    from skillflow.propagation.annotation.binding_examples import (
        _fixture, example_material, evidence as ev, instruction, literal, result, segment, semantics)
    from skillflow.propagation.annotation.compiler import compile_response
    from skillflow.propagation.annotation.services import to_payload
    from skillflow.propagation.loading import materials_from_result
    from skillflow.propagation.solver import propagate
    from tests.doe.test_sink_payload_seeds import solve_fixture
    example = _fixture("acquired condition", "A direct condition remains a protected use.",
        "Read the readiness document. The finish action is permitted only when its token field is true.",
        [instruction("ir_read", "read_context", [], "document"),
         instruction("ir_gate", "dispatch", [result("document")])],
        {"ir_read": semantics([segment([{"op": "read", "location": "context", "output": "document"}],
            "context_read")], "document"), "ir_gate": semantics(), "ir_finish": semantics()})
    example["cfg"]["blocks"]["finish"] = {"block_id": "finish", "block_name": "Finish",
        "instructions": [instruction("ir_finish", "return", [literal("done")])],
        "constraints": [], "data_source_kind": None}
    example["cfg"]["edges"] = [{"source_block_id": "sample", "target_block_id": "finish", "condition_text": None}]
    material = example_material(example)
    raw = example["annotation"]
    raw["task_revision_id"] = material["task"]["task_sha256"]
    raw["locations"] = {"context": {"kind": "runtime_context", "name": "supplied", "operand_refs": [],
        "access_scope": "task", "retention": "task"}}
    raw["location_evidences"] = {"context": [ev()]}
    condition = {"instruction_id": "ir_gate", "path": []}
    raw["expressions"] = [{"target": condition,
        "expression": {"op": "field", "arg": {"op": "ref", "value": inp()}, "path": ["token"]},
        "evidences": [ev()]}]
    raw["realizations"] = [{"requirement_id": "R1", "status": "expressed", "bindings": [], "gaps": [],
        "constraints": [{"kind": "only_if", "scope": {"kind": "task"},
            "events": [{"instruction_id": "ir_finish", "path": []}], "condition": condition}]}]
    checked, compiled, mapping = compile_response(raw, material)
    forward = propagate(material["cfg"], to_payload(compiled))
    assert forward.status == "complete"
    facts = materials_from_result(forward, material=material, raw_annotation=checked,
        compiled_annotation=compiled, mapping=mapping)
    _, solved = solve_fixture((material, checked, facts))
    acquired = next(row for row in solved["input_assessments"] if row["node_kind"] == "acquisition_output")
    assert acquired["ranges"] and all(row["status"] == "unresolved" for row in acquired["ranges"])
    assert "directly reads ['token']" in acquired["ranges"][0]["reason"]
    assert "/realizations/0/constraints/0/condition" in acquired["ranges"][0]["reason"]
