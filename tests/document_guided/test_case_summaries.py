"""Source-supported bounded call cases, without real requests or executions."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response, project_sensitivity
from skillflow.propagation.annotation.binding_examples import (
    _fixture, example_material, evidence, instruction, literal, result,
)
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.models import FlowLocation
from skillflow.propagation.solver import propagate


def local(name):
    return {"kind": "local", "name": name}


def case_fixture(values=None, *, catch=True, state=True):
    values = ["same", "same"] if values is None else values
    fixture = _fixture("cases", "Each member has a source-supported normal or caught-error outcome.",
        "For each URL, call the service. Catch failures and keep their actual error values. "
        "A successful local client creation may retain its handle. Save the completed collection.",
        [instruction("ir_call", "invoke", [literal(values)], "response"),
         instruction("ir_return", "return", [result("response")])], {})
    material = example_material(fixture)
    normal_ops = []
    if state:
        normal_ops += [
            {"op": "read", "location": "cache", "output": "old_handle"},
            {"op": "compute", "inputs": [{"kind": "literal", "value": "creation-credential"}], "output": "handle"},
            {"op": "write", "target": "cache", "mode": "replace", "input": local("handle"), "may": True}]
    normal_ops += [
        {"op": "call", "location": "service", "inputs": [local("url")], "output": "reply"},
        {"op": "build", "container": "object", "parts": [
            {"path": ["url"], "value": local("url")},
            {"path": ["value"], "value": local("reply")}], "output": "row"}]
    error_ops = [
        {"op": "receive", "location": "call_error", "inputs": [], "output": "error"},
        {"op": "build", "container": "object", "parts": [
            {"path": ["url"], "value": local("url")},
            {"path": ["error"], "value": local("error")}], "output": "row"}]
    cases = {"kind": "cases", "output": "member_result", "cases": [
        {"name": "success", "phase": "normal", "disposition": "return",
         "condition": "The call returns normally.", "segments": [{"mode": "local", "returns": [], "ops": normal_ops}],
         "yield": local("row")},
        {"name": "initialization_error", "phase": "pre_request_error", "disposition": "return" if catch else "throw",
         "condition": "Initialization throws before a network request.",
         "segments": [{"mode": "local", "returns": [], "ops": error_ops}],
         **({"yield": local("row")} if catch else {})}]}
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}],
        "demands": [{"requirement_id": "R1", "target": {"instruction_id": "ir_call", "side": "output", "index": 0},
                     "preserve": "value", "reason": "Preserve the per-occurrence result collection."}],
        "locations": {
            "service": {"kind": "remote", "name": "Service", "evidences": [evidence()]},
            "call_error": {"kind": "tool", "name": "Protected local call exception", "access_scope": "task", "evidences": [evidence()]},
            "cache": {"kind": "runtime_context", "name": "client_binding", "evidences": [evidence()]},
            "saved": {"kind": "storage", "name": "results.json", "evidences": [evidence()]}},
        "ir_semantics": {"ir_call": {"order": "fixed", "evidences": [evidence()], "segments": [
            {"kind": "for_each", "collection": {"kind": "input", "index": 0}, "item": "url", "body": [cases],
             "yield": local("member_result"), "output": "batch"},
            {"mode": "local", "returns": [], "ops": [{"op": "write", "target": "saved", "mode": "replace", "input": local("batch")}]}],
            "output_bindings": [{"output_index": 0, "value": local("batch")}]},
            "ir_return": {"evidences": [evidence()]}}}
    return material, wire


def solve_cases(values=None, *, catch=True, state=True):
    material, wire = case_fixture(values, catch=catch, state=state)
    saved, raw, compiled, mapping = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    return material, saved, raw, compiled, mapping, solved


def test_cases_keep_distinct_occurrences_results_and_exception_origins():
    _, wire, raw, compiled, mapping, solved = solve_cases()
    record = solved.records.get("ir_call")
    loop = record.events[0]
    assert len(loop.instances) == 2
    assert {instance.selector for instance in loop.instances} == {0, 1}
    assert all(len(instance.yielded) == 2 for instance in loop.instances)
    assert len({next(iter(op.outputs[0])) for instance in loop.instances for event in instance.body
                for op in event.atomic_ops if op.op == "receive" and event.case.phase == "normal"}) == 2
    assert all(event.effect not in {"net_send", "net_receive"} for instance in loop.instances
               for event in instance.body if event.case.phase == "pre_request_error")
    assert not any(event.effect == "model_observe" for instance in loop.instances for event in instance.body)
    assert any("/cases/0/segments/0/ops/" in row["wire_path"] for row in mapping["events"])
    solved.records.validate(require_complete=True)


def test_may_cache_effect_retains_original_handle_and_does_not_sequence_members():
    *_, solved = solve_cases()
    record = solved.records.get("ir_call")
    before = record.entry_state.get(FlowLocation(kind="runtime_context", name="client_binding"))
    after = record.exit_state.get(FlowLocation(kind="runtime_context", name="client_binding"))
    assert before and before < after
    reads = [op.outputs[0] for instance in record.events[0].instances for event in instance.body
             for op in event.atomic_ops if op.op == "read"]
    assert reads == [before, before]
    writes = [op for instance in record.events[0].instances for event in instance.body
              for op in event.atomic_ops if op.op == "write"]
    assert all(op.may_state and all(change.update == "weak" for change in op.changes) for op in writes)


def test_empty_scope_does_not_create_handles_or_requests_but_keeps_actual_final_save():
    *_, solved = solve_cases([])
    record = solved.records.get("ir_call")
    assert not record.events[0].instances
    cache = FlowLocation(kind="runtime_context", name="client_binding")
    assert record.entry_state.get(cache) == record.exit_state.get(cache)
    batch = solved.registry.get(next(iter(record.events[0].outputs)))
    assert batch.content.members == []
    assert record.events[1].atomic_ops[0].op == "write"


def test_symbolic_case_collection_keeps_unknown_count_and_alternative_member_yields():
    from skillflow.doe.constraint_control import collection_size
    material, wire = case_fixture(state=False)
    segments = wire["ir_semantics"]["ir_call"]["segments"]
    segments[0]["collection"] = local("unknown_urls")
    segments.insert(0, {"mode": "local", "returns": [], "ops": [
        {"op": "receive", "location": "call_error", "inputs": [], "output": "unknown_urls"}]})
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    loop = solved.records.get("ir_call").events[1]
    assert len(loop.instances) == 1 and len(loop.instances[0].yielded) == 2
    data = {entry["data"]["id"]: entry["data"] for entry in solved.registry.to_dict()["records"]}
    assert collection_size(data, next(iter(loop.outputs))) is None


def test_case_products_are_not_materialized_as_complete_arrays():
    *_, solved = solve_cases(["same"] * 18, state=False)
    loop = solved.records.get("ir_call").events[0]
    assert len(loop.outputs) == 1 and len(loop.instances) == 18
    mapped = solved.registry.get(next(iter(loop.outputs))).content
    assert len(mapped.members) == 18 and all(len(member.values) == 2 for member in mapped.members)


def test_zero_argument_case_calls_still_have_distinct_member_response_identities():
    material, wire = case_fixture(state=False)
    wire["locations"]["service"]["kind"] = "tool"
    normal = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][0]
    normal["segments"][0]["ops"][0]["inputs"] = []
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    responses = [next(iter(op.outputs[0])) for instance in solved.records.get("ir_call").events[0].instances
                 for event in instance.body for op in event.atomic_ops if event.case.phase == "normal" and op.op == "receive"]
    assert len(set(responses)) == 2


def test_uncaught_case_is_not_a_member_result_and_normal_save_is_conditioned():
    *_, compiled, _, solved = solve_cases(catch=False)
    record = solved.records.get("ir_call")
    assert all(len(instance.yielded) == 1 for instance in record.events[0].instances)
    assert record.events[0].completion_groups
    assert record.events[1].requires_completion == record.events[0].completion_groups
    assert compiled["ir_semantics"]["ir_call"]["events"][1]["requires_completion"]


def test_pre_request_error_cannot_claim_network_delivery():
    material, wire = case_fixture()
    wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][1]["segments"][0]["ops"].insert(
        0, {"op": "deliver", "target": "service", "inputs": [local("url")]})
    with pytest.raises(StructuralValidationError, match="pre-request"):
        compile_flat_response(wire, material)


def test_may_storage_writes_are_not_silently_allowed_in_member_scopes():
    material, wire = case_fixture()
    wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][0]["segments"][0]["ops"][2]["target"] = "saved"
    with pytest.raises(StructuralValidationError, match="task-local"):
        compile_flat_response(wire, material)


def test_case_sensitive_value_is_lowered_in_the_actual_member_scope():
    material, wire = case_fixture()
    processing = {key: wire[key] for key in ("locations", "ir_semantics")}
    declaration = {"value": local("reply"), "label": "Private report", "evidences": [evidence()],
        "case_path": ["segments", 0, "body", 0, "cases", 0]}
    scope, lowered = project_sensitivity(processing, "ir_call", ["segments", 0], declaration, material)
    assert scope == ["events", 0]
    assert lowered["value"]["name"].endswith("__reply")
    assert "case_path" not in lowered
    with pytest.raises(StructuralValidationError, match="member scope"):
        project_sensitivity(processing, "ir_call", [], declaration, material)


def test_all_throw_summary_is_rejected_instead_of_publishing_a_normal_out():
    material, wire = case_fixture()
    summary = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]
    summary.pop("output")
    for case in summary["cases"]:
        case["disposition"] = "throw"
        case.pop("yield", None)
    with pytest.raises(StructuralValidationError, match="at least one return candidate"):
        compile_flat_response(wire, material)


def test_thrown_prefix_state_remains_recorded_but_cannot_reach_normal_out():
    material, wire = case_fixture(catch=False, state=False)
    failed = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]["cases"][1]
    failed["segments"][0]["ops"].extend([
        {"op": "compute", "inputs": [local("error")], "output": "failed_handle"},
        {"op": "write", "target": "cache", "mode": "replace", "input": local("failed_handle"), "may": True}])
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    record = solved.records.get("ir_call")
    cache = FlowLocation(kind="runtime_context", name="client_binding")
    assert record.entry_state.get(cache) == record.exit_state.get(cache)
    failed_writes = [op for instance in record.events[0].instances for event in instance.body
                     for op in event.atomic_ops if op.may_state]
    assert failed_writes and all(op.changes[0].after > op.changes[0].before for op in failed_writes)


def ga4_fixture(path):
    """Small typed boundary projections cite byte-identical GA4 source files."""
    from skillflow.common.source_evidence import _digest
    from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files
    from skillflow.propagation.material import prepare_material

    material, wire = case_fixture(catch=path != "batch", state=False)
    root = Path(__file__).parents[1] / "fixtures" / "ga4_boundary_cases"
    manifest = json.loads((root / "provenance.json").read_text(encoding="utf-8-sig"))
    files = []
    for row in manifest["files"]:
        content = (root / row["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == row["sha256"]
        files.append({"path": "scripts/src/" + row["path"], "content": content.decode("utf-8"), "sha256": row["sha256"]})
    source = {"files": files, "source_sha256": _digest([{"path": row["path"], "sha256": row["sha256"]} for row in files])}
    filename, first, last = ("api/indexing.ts", 89, 105) if path == "batch" else ("index.ts", 301, 319) if path == "reindex" else ("index.ts", 324, 346)
    citation = {"file": "skill/scripts/src/" + filename, "start_line": first, "end_line": last,
                "reason": "The actual GA4 function determines per-member collection and catch behavior."}
    task = validate_task_candidate({"purpose": {"text": "Return the declared per-URL results.", "evidences": [citation]},
        "requirements": [{"id": "R1", "text": "Preserve the supported result collection and pairing.", "evidences": [citation]}], "issues": []},
        source_files=task_source_files(source), source_sha256=source["source_sha256"])
    material = prepare_material(source, material["cfg"], task_baseline=task)
    for location in wire["locations"].values():
        location["evidences"] = [citation]
    for spec in wire["ir_semantics"].values():
        spec["evidences"] = [citation]
    summary = wire["ir_semantics"]["ir_call"]["segments"][0]["body"][0]
    normal = summary["cases"][0]
    # These are summaries of the source-supported local helper boundary; the
    # fixture does not mislabel its result projection as a raw remote response.
    wire["locations"]["service"].update(kind="tool", name="inspectUrl" if path == "status" else "requestIndexing")
    normal["segments"][0]["ops"][0]["inputs"].append({"kind": "literal", "value": {"save": False}})
    normal["segments"][0]["ops"] = normal["segments"][0]["ops"][:1]
    if path == "batch":
        normal["yield"] = local("reply")
        summary["cases"][1]["segments"][0]["ops"] = summary["cases"][1]["segments"][0]["ops"][:1]
    elif path == "reindex":
        normal["segments"][0]["ops"].append({"op": "update_fields", "input": local("reply"),
            "updates": [{"path": ["status"], "value": {"kind": "literal", "value": "submitted"}}], "output": "row"})
        normal["yield"] = local("row")
    else:
        normal["segments"][0]["ops"].extend([
            {"op": "select_part", "input": local("reply"), "path": ["indexStatus"], "output": "status"},
            {"op": "build", "container": "object", "parts": [
                {"path": ["url"], "value": local("url")}, {"path": ["status"], "value": local("status")}], "output": "row"}])
        normal["yield"] = local("row")
    if path != "batch":
        failure = summary["cases"][1]["segments"][0]["ops"]
        failure[1:1] = [{"op": "compute", "inputs": [local("error")], "dependencies": ["derived"], "output": "error_string"}]
        failure[-1]["parts"] = [
            {"path": ["url"], "value": local("url")},
            {"path": ["error"] if path == "reindex" else ["status", "error"], "value": local("error_string")},
            {"path": ["status"] if path == "reindex" else ["indexed"], "value": {"kind": "literal", "value": "failed" if path == "reindex" else False}}]
    return material, wire, source


@pytest.mark.parametrize("path,expected_yields", [("batch", 1), ("reindex", 2), ("status", 2)])
def test_ga4_real_source_normal_batch_caught_errors_and_status_pairing(path, expected_yields):
    material, wire, source = ga4_fixture(path)
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    loop = solved.records.get("ir_call").events[0]
    assert len(loop.instances) == 2
    assert all(len(instance.yielded) == expected_yields for instance in loop.instances)
    assert bool(loop.completion_groups) is (path == "batch")
    for instance in loop.instances:
        for event in instance.body:
            for op in event.atomic_ops:
                if event.case.phase == "normal" and op.op == "build":
                    assert op.inputs[0] == frozenset([instance.element])
    original = next(row["content"] for row in source["files"] if row["path"] == "scripts/src/index.ts")
    assert "results.push({ url, status: 'failed', error: String(error) });" in original
    assert "status: result.indexStatus," in original
