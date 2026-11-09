"""Independent r3 failure fixtures; no historic controller or replay is invoked."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from skillflow.common.abstraction import BOUNDARY_GRANULARITY
from skillflow.common.inputs.snapshot import _describe
from skillflow.common.inputs.skill_package import load_skill_package
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.graph.extraction.prompt import build_whole_skill_prompt
from skillflow.propagation import propagate, FlowLocation
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.task import validate_task_candidate, task_source_files
from skillflow.propagation.material import prepare_material
from skillflow.propagation.runner import save_propagation_run, load_propagation_materials
from skillflow.doe.formal_runner import run_doe
from tests.propagation.component_helpers import accepted_annotation


FIXTURE = Path(__file__).parents[1] / "fixtures/online_interface_r4/013"
APPENDS = ("ir_014", "ir_018", "ir_022", "ir_026")
RETURNS = ("ir_015", "ir_019", "ir_023", "ir_027")


@pytest.fixture(autouse=True)
def fixed_test_producer(monkeypatch):
    # Freeze the current producer only inside this new offline fixture, so
    # concurrent implementation edits cannot masquerade as a changed producer.
    from tests.document_guided.test_parallel_runner import freeze_producer
    from skillflow.common.recording import implementation_provenance
    frozen = implementation_provenance()
    freeze_producer(monkeypatch)
    monkeypatch.setattr("skillflow.propagation.annotation.runner.implementation_provenance",
                        lambda: deepcopy(frozen))


def read(name):
    return json.loads((FIXTURE / name).read_text(encoding="utf-8"))


def material_for(cfg, source_bytes, declaration):
    _, source, _ = _describe({"original_path": str(FIXTURE / "source"),
        "storage": "authored-offline-regression", "root_name": "013",
        "archive_sha256": None}, [("SKILL.md", source_bytes)])
    task = validate_task_candidate(declaration, source_files=task_source_files(source),
                                   source_sha256=source["source_sha256"])
    return prepare_material(source, cfg, task_baseline=task)


def candidate(*, corrected=True):
    suffix = "corrected" if corrected else "failed"
    material = material_for(read(f"cfg.{suffix}.json")["cfg"],
        (FIXTURE / "source/SKILL.md").read_bytes(), read("task.candidate.json"))
    return material, read(f"annotation.{suffix}.json")


def ops(solved, identity, kind):
    return [op for event in solved.records.get(identity).events
            for op in event.atomic_ops if op.op == kind]


def test_independent_fixture_preserves_failure_bytes_and_only_removes_unused_slots():
    for name, row in read("provenance.json")["copied_files"].items():
        assert hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() == row["sha256"]
    failed, corrected = read("cfg.failed.json")["cfg"], read("cfg.corrected.json")["cfg"]
    for block_id, block in failed["blocks"].items():
        for original, current in zip(block["instructions"], corrected["blocks"][block_id]["instructions"]):
            expected = deepcopy(original)
            if original["id"] in APPENDS:
                names = {item["identifier"] for item in original["outputs"]}
                assert names and not any(item.get("identifier") in names
                    for b in failed["blocks"].values() for ir in b["instructions"] for item in ir["inputs"])
                expected["outputs"] = []
            assert current == expected
    assert corrected["edges"] == failed["edges"]


def test_old_contract_conflict_remains_explicit_and_no_output_is_automatically_pruned():
    material, wire = candidate(corrected=False)
    _, _, compiled, _ = compile_flat_response(wire, material)
    failed = propagate(material["cfg"], to_payload(compiled))
    assert failed.status == "incomplete"
    assert all(failed.coverage[ir] == "unmodeled" for ir in APPENDS)
    assert all(failed.coverage[ir] == "blocked" for ir in RETURNS)
    # Reinstating append alone must not fabricate bindings for whole-file slots.
    _, fixed_wire = candidate()
    with pytest.raises(StructuralValidationError, match="output bindings"):
        compile_flat_response(fixed_wire, material)


def test_013_corrected_fixture_compiles_propagates_saves_and_publishes_doe(tmp_path):
    material, wire = candidate()
    _, raw, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    assert len(solved.coverage) == 27
    assert set(solved.coverage.values()) == {"processed"}
    receives = {ir: ops(solved, ir, "receive")[0] for ir in ("ir_005", "ir_008", "ir_010")}
    assert len({next(iter(op.outputs[0])) for op in receives.values()}) == 3
    first, retry, archive = [ops(solved, ir, "deliver")[0] for ir in receives]
    assert first.inputs == retry.inputs and len(first.inputs) == 2
    assert archive.inputs == first.inputs[:1]
    assert [op.endpoints[0].name for op in (first, retry, archive)] == ["fast.fetch", "fast.fetch", "archive.fetch"]
    for projection, status, append, returning, call in zip(
            ("ir_012", "ir_016", "ir_020", "ir_024"),
            ("ir_013", "ir_017", "ir_021", "ir_025"), APPENDS, RETURNS,
            ("ir_005", "ir_008", "ir_010", "ir_010")):
        selected = ops(solved, projection, "select_part")[0]
        assert selected.inputs[0] == receives[call].outputs[0]
        status_op = ops(solved, status, "compute")[0]
        assert status_op.inputs[0] == receives[call].outputs[0]
        write = ops(solved, append, "write")[0]
        assert write.inputs[0] == status_op.outputs[0]
        assert write.outputs == [] and not ops(solved, append, "read")
        assert write.endpoints[0] == FlowLocation(kind="storage", name="local.status.txt")
        assert write.changes[0].before and write.changes[0].after
        assert write.changes[0].before.isdisjoint(write.changes[0].after)
        for data_id in write.changes[0].after:
            assert set(solved.registry.get(data_id).origin.inputs) == (
                write.changes[0].before | write.inputs[0])
        return_ir = next(ir for b in material["cfg"]["blocks"].values()
                         for ir in b["instructions"] if ir["id"] == returning)
        actual = solved.records.get(returning).entry_state.get(
            FlowLocation(kind="result", name=return_ir["inputs"][0]["identifier"]))
        assert actual == selected.outputs[0]
    annotation = accepted_annotation(tmp_path / "annotation", material, raw)
    saved = save_propagation_run(tmp_path / "propagation", annotation_run=annotation, solved=solved)
    loaded = load_propagation_materials(tmp_path / "propagation")
    assert loaded.records == saved.records and loaded.status == "complete"
    run_doe(tmp_path / "propagation", run_dir=tmp_path / "doe")
    doe = json.loads((tmp_path / "doe/doe-result.json").read_text(encoding="utf-8"))
    assert {sink["boundary"]["instruction_id"] for sink in doe["sinks"]
            if sink["boundary"]["sink_type"] == "storage_write"} == set(APPENDS)
    assert doe["status"] == "partial"  # Unrelated source/task limitations remain honest.
    assert not any(row["code"] in {"upstream_coverage", "upstream_diagnostic"}
                   for row in doe["diagnostics"])
    assert any(row["code"] == "task_source_issue" for row in doe["diagnostics"])


def test_shared_generation_guidance_reaches_graph_prompt_without_special_case_rules():
    prompt = build_whole_skill_prompt(load_skill_package(FIXTURE / "source"))
    assert BOUNDARY_GRANULARITY in prompt
    text = " ".join(BOUNDARY_GRANULARITY.split())
    assert "Storage side effects have no public result by default" in text
    assert "actual source-returned path, receipt or handle" in text
    assert "later source-supported content read as its own acquisition" in text
    assert "not permission to prune real outputs" in text
    assert "status.txt" not in BOUNDARY_GRANULARITY and "GA4" not in BOUNDARY_GRANULARITY


def test_actual_returned_path_and_later_content_read_keep_their_values():
    # Independent generic source: the wrapper really returns its path, and the
    # next action actually reads the updated file. Neither is auto-pruned.
    text = b'Append "ok" to log.txt; the wrapper returns its original path "log.txt". Then read that file and return its content.\n'
    evidence = {"file": "skill/SKILL.md", "start_line": 1, "end_line": 1,
                "reason": "The independent fixture explicitly returns the path and later reads its file."}
    cfg = {"entry_block_id": "b", "blocks": {"b": {"block_id": "b", "block_name": "append_read", "instructions": [
        {"id": "ir_append", "opcode": "append_and_return_path", "inputs": [
            {"type": "literal", "literal_value": "log.txt"},
            {"type": "literal", "literal_value": "ok"},
            {"type": "external_resource", "identifier": "log.txt"}],
         "outputs": [{"type": "result", "identifier": "returned_path"}]},
        {"id": "ir_read", "opcode": "read_file", "inputs": [{"type": "result", "identifier": "returned_path"}],
         "outputs": [{"type": "result", "identifier": "contents"}]},
        {"id": "ir_return", "opcode": "return", "inputs": [{"type": "result", "identifier": "contents"}], "outputs": []}]}}, "edges": []}
    declaration = {"purpose": {"text": text.decode(), "evidences": [evidence]},
        "requirements": [{"id": "R1", "text": text.decode(), "evidences": [evidence]}], "issues": []}
    material = material_for(cfg, text, declaration)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}], "demands": [
        {"requirement_id": "R1", "target": {"instruction_id": "ir_return", "side": "input", "index": 0},
         "preserve": "value", "reason": "Return the actual content read after appending."}],
        "locations": {"log": {"kind": "storage", "name": "log.txt", "evidences": [evidence]}},
        "ir_semantics": {
            "ir_append": {"evidences": [evidence], "segments": [{"mode": "local", "returns": [], "ops": [
                {"op": "write", "mode": "append", "target": "log", "input": {"kind": "input", "index": 1}}]}],
                "output_bindings": [{"output_index": 0, "value": {"kind": "input", "index": 0}}]},
            "ir_read": {"evidences": [evidence], "segments": [{"mode": "local", "returns": [], "ops": [
                {"op": "read", "location": "log", "output": "contents"}]}],
                "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "contents"}}]},
            "ir_return": {"evidences": [evidence]}}}
    _, _, compiled, _ = compile_flat_response(wire, material)
    solved = propagate(material["cfg"], to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    path = solved.records.get("ir_append").exit_state.get(FlowLocation(kind="result", name="returned_path"))
    assert path and {solved.registry.get(x).content.value for x in path} == {"log.txt"}
    write = ops(solved, "ir_append", "write")[0]
    assert ops(solved, "ir_read", "read")[0].outputs[0] == write.changes[0].after
    assert solved.records.get("ir_return").entry_state.get(FlowLocation(kind="result", name="contents")) == write.changes[0].after
