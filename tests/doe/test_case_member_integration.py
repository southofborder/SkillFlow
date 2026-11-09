"""Call candidates remain paired to occurrences in DOE and constraint facts."""
import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.solver import propagate
from skillflow.propagation.contracts.task import Task
from skillflow.doe.demand_material import prepare_demand_review
from skillflow.doe.sensitivity_material import prepare_sensitivity_review
from skillflow.doe.constraint_engine import ConstraintEngine
from skillflow.doe.material import _Index
from tests.doe.components import mutable_components
from tests.doe.test_constraints_engine import World, bounded
from tests.document_guided.test_case_summaries import case_fixture, solve_cases, local
from skillflow.propagation.annotation.binding_examples import evidence
from skillflow.propagation.models import FlowLocation


def case_member_facts():
    material, wire = case_fixture(state=False)
    loop = wire["ir_semantics"]["ir_call"]["segments"][0]
    loop["body"][0]["cases"][0]["segments"][0]["ops"][-1]["parts"][1]["path"] = ["value"]
    loop["sensitivity"] = [{"value": local("reply"), "label": "Private returned token",
        "path": ["token"], "evidences": [evidence()], "case_path": ["segments", 0, "body", 0, "cases", 0]}]
    tail = wire["ir_semantics"]["ir_call"]["segments"][1]["ops"]
    tail.insert(0, {"op": "build", "container": "object", "parts": [
        {"path": ["rows"], "value": local("batch")}], "output": "wrapped"})
    tail[-1]["input"] = local("wrapped")
    tail[-1]["demands"] = [{"requirement_id": "R1", "target": {"kind": "input", "index": 0},
        "preserve": "value", "path": ["rows", {"kind": "each"}, "url"],
        "reason": "Preserve each actual saved result's URL without requiring its private response."}]
    wire["ir_semantics"]["ir_call"]["output_bindings"][0]["value"] = local("wrapped")
    wire["demands"] = []
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete"
    facts = mutable_components(materials_from_result(solved, material=material,
        raw_annotation=raw, compiled_annotation=compiled, mapping=mapping, wire_annotation=saved))
    return facts, Task.model_validate(material["task"]), facts.annotation, {
        "goals": compiled["demands"], "expressions": compiled["expressions"]}


def test_prefixed_member_demand_keeps_success_error_alternatives_and_receivers_separate():
    facts, task, annotation, candidate = case_member_facts()
    demand = prepare_demand_review(facts, task, annotation, candidate).to_dict()
    assert demand["status"] == "complete"
    index = _Index(facts)
    selected = [row for row in demand["derivations"].values()
                if row["node"]["kind"] == "op_input"
                and index.operations[row["node"]["operation_id"]]["record"]["op"] == "build"
                and index.operations[row["node"]["operation_id"]].get("case")]
    assert {row["node"]["slot"] for row in selected} == {0}
    assert {index.operations[row["node"]["operation_id"]]["case"]["phase"] for row in selected} == {
        "normal", "pre_request_error"}
    sensitivity = prepare_sensitivity_review(facts, task, annotation, candidate).to_dict()
    saved = next(s for s in sensitivity["sinks"] if s["boundary"]["target"] == "saved")
    assert len(saved["data_reviews"]) == 2
    assert {row["conclusion"] for row in saved["data_reviews"]} == {"excess_supported"}
    assert {tuple(row["reduction"]["path"]) for row in saved["data_reviews"]} == {
        ("rows", 0, "value", "token"), ("rows", 1, "value", "token")}


def test_possible_state_update_is_not_a_producer_of_the_next_member_original_handle():
    material, saved, raw, compiled, mapping, solved = solve_cases()
    facts = mutable_components(materials_from_result(solved, material=material,
        raw_annotation=raw, compiled_annotation=compiled, mapping=mapping, wire_annotation=saved))
    index = _Index(facts)
    for key, operation in index.operations.items():
        if operation["record"].get("may_state"):
            record = operation["record"]
            actual = set().union(*(set(slot) for slot in record["inputs"]))
            assert index.written_values(key, ("runtime_context", "client_binding")) == actual
            assert not actual.intersection(record["changes"][0]["before"])
    links = [link for link in index.links.values() if link["kind"] == "saved_read"]
    assert not any(index.operations[link["source"]]["record"].get("may_state")
                   and index.operations[link["source"]]["position"]["instance_index"] !=
                       index.operations[link["target"]]["position"]["instance_index"] for link in links)


def test_known_duplicate_occurrences_are_scheduled_once_with_their_own_cases():
    world = World()
    refs = world.foreach(size=2, bodies=2, guards=[[True, True], [False, True]])
    for number, event in enumerate(world.semantics["members"]["events"][0]["body"]):
        event["case"] = {"group": "call", "id": str(number), "name": str(number),
            "phase": "normal" if number == 0 else "pre_request_error", "disposition": "return",
            "condition": "The normal or caught-error candidate is selected."}
    world.records["members"]["events"][0]["instances"] = [
        {"collection": "collection", "selector": number} for number in range(2)]
    result, = ConstraintEngine(world.engine(bounded([refs[0]], 1))).check().values()
    assert result["status"] == "satisfied"


def test_alternative_collection_candidates_do_not_mix_member_occurrences():
    world = World()
    refs = world.foreach(size=3, guards=[[True], [False], [True]])
    world.data["collection"]["content"]["value"] = ["same", "same"]
    world.add_data("alternative", {"form": "literal", "value": ["same"]})
    record = world.records["members"]["events"][0]
    record["collections"] = ["collection", "alternative"]
    record["instances"] = [{"collection": "collection", "selector": 0},
        {"collection": "collection", "selector": 1}, {"collection": "alternative", "selector": 0}]
    result, = ConstraintEngine(world.engine(bounded(refs, 1))).check().values()
    assert result["status"] == "satisfied"


@pytest.mark.parametrize("order", ["fixed", "partial"])
def test_root_case_reaching_writes_join_normal_branches_and_exclude_throw_only_version(order):
    material, wire = case_fixture(state=False)
    candidates = []
    for name, disposition in [("first", "return"), ("second", "return"), ("failed", "throw")]:
        value = {"kind": "literal", "value": name}
        candidates.append({"name": name, "phase": "normal" if disposition == "return" else "pre_request_error",
            "condition": "The source-supported " + name + " candidate is selected.", "disposition": disposition,
            "segments": [{"mode": "local", "returns": [], "ops": [
                {"op": "write", "target": "saved", "mode": "replace", "input": value}]}],
            **({"yield": value} if disposition == "return" else {})})
    spec = wire["ir_semantics"]["ir_call"]
    spec["order"] = order
    spec["segments"] = [{"kind": "cases", "cases": candidates, "output": "result"},
        {"mode": "local", "returns": [], "ops": [{"op": "read", "location": "saved", "output": "readback"}]}]
    spec["output_bindings"] = [{"output_index": 0, "value": local("readback")}]
    if order == "partial":
        # This combination is an explicit interface limitation; do not bypass
        # the compiler and present invented accepted facts as a real case.
        with pytest.raises(StructuralValidationError, match="fixed summary order"):
            compile_flat_response(wire, material)
        return
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete"
    facts = mutable_components(materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved))
    index = _Index(facts)
    links = [link for link in index.links.values() if link["kind"] == "saved_read"]
    assert len(links) == 2
    assert {index.operations[link["source"]]["case"]["name"] for link in links} == {"first", "second"}


def test_throw_only_may_write_does_not_define_normal_read_or_implicit_context_input():
    material, wire = case_fixture(catch=False, state=False)
    failed = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][1]
    failed["segments"][0]["ops"].extend([
        {"op": "compute", "inputs": [local("error")], "output": "failed_handle"},
        {"op": "write", "target": "cache", "mode": "replace", "input": local("failed_handle"), "may": True}])
    wire["ir_semantics"]["ir_call"]["segments"][1]["ops"].insert(0,
        {"op": "read", "location": "cache", "output": "normal_handle", "demands": [
            {"requirement_id": "R1", "target": {"kind": "output"}, "preserve": "value",
             "reason": "Preserve the actual handle available after normal completion."}]})
    material["cfg"]["declared_context_keys"] = ["client_binding"]
    material["cfg"]["blocks"]["sample"]["instructions"][1] = {
        "id": "ir_dispatch", "opcode": "dispatch", "inputs": [], "outputs": []}
    material["cfg"]["blocks"]["context"] = {"block_id": "context", "block_name": "Acquire normal handle",
        "data_source_kind": "context", "instructions": [
            {"id": "ir_context", "opcode": "acquire_context", "inputs": [
                {"type": "context_key", "identifier": "client_binding"}],
             "outputs": [{"type": "result", "identifier": "normal_context"}]},
            {"id": "ir_return", "opcode": "return", "inputs": [
                {"type": "result", "identifier": "normal_context"}], "outputs": []}]}
    material["cfg"]["edges"] = [{"source_block_id": "sample", "target_block_id": "context", "condition_text": None}]
    wire["ir_semantics"]["ir_dispatch"] = {"evidences": [evidence()]}
    wire["ir_semantics"]["ir_context"] = {"evidences": [evidence()], "output_bindings": [
        {"output_index": 0, "value": {"kind": "input", "index": 0}}]}
    wire["locations"]["cache"]["operand_refs"] = [
        {"instruction_id": "ir_context", "side": "input", "index": 0}]
    wire["demands"] = [{"requirement_id": "R1", "target": {
        "instruction_id": "ir_context", "side": "input", "index": 0}, "preserve": "value",
        "reason": "Preserve only the normal continuation's current handle."}]
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete"
    record = solved.records.get("ir_call")
    cache = FlowLocation(kind="runtime_context", name="client_binding")
    assert record.entry_state.get(cache) == record.exit_state.get(cache)
    facts = mutable_components(materials_from_result(solved, material=material, raw_annotation=raw,
        compiled_annotation=compiled, mapping=mapping, wire_annotation=saved))
    index = _Index(facts)
    thrown_writes = {key for key, op in index.operations.items()
                     if op.get("case", {}).get("disposition") == "throw" and op["record"]["op"] == "write"}
    assert len(thrown_writes) == 2  # Failure-prefix evidence is preserved.
    assert not any(link["kind"] == "saved_read" and link["source"] in thrown_writes
                   for link in index.links.values())
    assert not any(thrown_writes & definitions for definitions in index.entry_writes["ir_return"].values())
    normal_read = next(key for key, op in index.operations.items()
                       if op["record"]["op"] == "read" and op.get("requires_completion"))
    assert all(not index.may_before(key, normal_read) for key in thrown_writes)
    candidate = {"goals": compiled["demands"], "expressions": compiled["expressions"]}
    demand = prepare_demand_review(facts, Task.model_validate(material["task"]), facts.annotation, candidate).to_dict()
    assert not any(row["node"]["operation_id"] in thrown_writes
                   and row["node"]["kind"] == "op_input" for row in demand["derivations"].values())
