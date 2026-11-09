"""Optional case segments reach real expansion/compilation without normalization of the answer."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from skillflow.common.source_evidence import _digest
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response, expand_processing
from skillflow.document_guided.fragments import assemble_fragments, split_fragments, validate_fragment
from skillflow.propagation.annotation.binding_examples import (
    _fixture, example_material, evidence, instruction, literal, result,
)
from skillflow.propagation.contracts.task import task_source_files, validate_task_candidate
from skillflow.propagation.material import prepare_material


FIXTURE = Path(__file__).parents[1] / "fixtures/online_interface_r4/ga4"


def existing_value_fixture(nested):
    source = "Return each supplied value unchanged when preparation succeeds; preparation may throw without a normal result."
    fixture = _fixture("optional_case_segments", source, source,
        [instruction("ir_call", "prepare", [literal(["kept"] if nested else "kept")], "value"),
         instruction("ir_return", "return", [result("value")])], {})
    value = {"kind": "local", "name": "item"} if nested else {"kind": "input", "index": 0}
    summary = {"kind": "cases", "output": "chosen", "cases": [
        {"name": "ready", "phase": "normal", "disposition": "return", "condition": "Preparation succeeds.",
         "segments": [], "yield": value},
        {"name": "failure", "phase": "local_error", "disposition": "throw", "condition": "Preparation throws.",
         "segments": []}]}
    segment = {"kind": "for_each", "collection": {"kind": "input", "index": 0}, "item": "item",
               "body": [summary], "yield": {"kind": "local", "name": "chosen"}, "output": "batch"} if nested else summary
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}], "locations": {},
        "demands": [{"requirement_id": "R1", "target": {"instruction_id": "ir_call", "side": "output", "index": 0},
                     "preserve": "value", "reason": "Preserve the supplied value on returning candidates."}],
        "ir_semantics": {"ir_call": {"evidences": [evidence()], "segments": [segment],
            "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "batch" if nested else "chosen"}}]},
            "ir_return": {"evidences": [evidence()]}}}
    return example_material(fixture), wire, summary


@pytest.mark.parametrize("nested", [False, True], ids=["top-level", "for-each-body"])
@pytest.mark.parametrize("omitted", [(0,), (1,), (0, 1)], ids=["direct-yield", "throw", "both"])
def test_omitted_case_segments_equal_explicit_empty_through_compilation_and_assembly(nested, omitted):
    material, explicit, _ = existing_value_fixture(nested)
    wire = deepcopy(explicit)
    selected = wire["ir_semantics"]["ir_call"]["segments"][0]
    if nested:
        selected = selected["body"][0]
    for index in omitted:
        selected["cases"][index].pop("segments")
    before = deepcopy(wire)
    saved, backend, compiled, _ = compile_flat_response(wire, material)
    _, expected_backend, expected_compiled, _ = compile_flat_response(explicit, material)
    assert saved == wire == before
    assert backend == expected_backend
    assert compiled == expected_compiled

    fragments = split_fragments(wire)
    fragment_before = deepcopy(fragments)
    source_only = {key: value for key, value in material.items() if key != "task"}
    assert validate_fragment("processing", fragments["processing"], source_only) == fragments["processing"]
    _, expanded, _ = expand_processing({"outcome": "completed", "realizations": [], **fragments["processing"]}, source_only)
    assert expanded["ir_semantics"] == backend["ir_semantics"]
    _, assembled_backend, assembled, _ = assemble_fragments(
        fragments["processing"], fragments["task-correspondence"], fragments["sensitivity"], material)
    assert assembled_backend == backend
    assert assembled == compiled
    assert fragments == fragment_before
    assert wire == before

    carriers = backend["ir_semantics"]["ir_call"]["events"]
    if nested:
        assert carriers[0]["yield"] == {"kind": "local", "name": "item"}
        assert carriers[0]["completion_groups"]
        carriers = carriers[0]["body"]
    assert [row["case"]["disposition"] for row in carriers] == ["return", "throw"]
    assert all(row["mode"] == "local" and row["returns"] == [] for row in carriers)
    assert all(row["events"][0]["atomic_ops"] == [] for row in carriers)


def ga4_processing_fixture():
    provenance = json.loads((FIXTURE / "provenance.json").read_text(encoding="utf-8"))
    for name, digest in provenance["fixture_files"].items():
        assert hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() == digest
    files = []
    for entry in provenance["source_files"]:
        payload = (FIXTURE / entry["fixture_path"]).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"]
        files.append({"path": entry["path"], "content": payload.decode("utf-8"), "sha256": entry["sha256"]})
    source = {"files": files, "source_sha256": _digest([{"path": row["path"], "sha256": row["sha256"]} for row in files])}
    processing = json.loads((FIXTURE / "processing.json").read_text(encoding="utf-8"))
    ir = json.loads((FIXTURE / "instruction.json").read_text(encoding="utf-8"))
    graph = {"entry_block_id": "get_client", "constraints": [], "edges": [], "declared_context_keys": [],
        "blocks": {"get_client": {"block_id": "get_client", "block_name": "Extracted getClient boundary",
            "instructions": [ir, instruction("ir_return", "return", [result("result_017")])],
            "constraints": [], "data_source_kind": None}}}
    citation = {**processing["ir_semantics"]["ir_027"]["evidences"][0],
                "reason": "The source returns a cached or newly constructed GA4 client; failures throw."}
    purpose = "Return the existing cached or newly constructed GA4 client on success."
    task = validate_task_candidate({"purpose": {"text": purpose, "evidences": [citation]},
        "requirements": [{"id": "R1", "text": purpose, "evidences": [citation]}], "issues": []},
        source_files=task_source_files(source), source_sha256=source["source_sha256"])
    material = prepare_material(source, graph, task_baseline=task)
    wire = {"outcome": "completed", "realizations": [{"requirement_id": "R1"}], **processing,
        "demands": [{"requirement_id": "R1", "target": {"instruction_id": "ir_027", "side": "output", "index": 0},
                     "preserve": "value", "reason": "Preserve the existing or created client handle on normal return."}]}
    wire["ir_semantics"]["ir_return"] = {"evidences": [citation]}
    return material, wire


def test_exact_ga4_failed_case_compiles_without_editing_extracted_answer():
    material, wire = ga4_processing_fixture()
    before = deepcopy(wire)
    cases = wire["ir_semantics"]["ir_027"]["segments"][0]["cases"]
    assert "segments" not in cases[2]
    assert cases[2]["disposition"] == "throw"
    saved, backend, compiled, _ = compile_flat_response(wire, material)
    explicit = deepcopy(wire)
    explicit["ir_semantics"]["ir_027"]["segments"][0]["cases"][2]["segments"] = []
    assert compile_flat_response(explicit, material)[1:3] == (backend, compiled)
    fragments = split_fragments(wire)
    assert assemble_fragments(fragments["processing"], fragments["task-correspondence"], fragments["sensitivity"], material)[1:3] == (backend, compiled)
    failure = next(row for row in backend["ir_semantics"]["ir_027"]["events"] if row["case"]["name"] == "failure")
    assert failure["events"][0]["atomic_ops"] == []
    assert saved == wire == before


@pytest.mark.parametrize("invalid", ["throw-yield", "empty-processing", "null-segments"])
def test_real_case_validation_errors_remain_structural(invalid):
    material, wire, summary = existing_value_fixture(False)
    summary["cases"][0].pop("segments")
    summary["cases"][1].pop("segments")
    if invalid == "throw-yield":
        summary["cases"][1]["yield"] = {"kind": "input", "index": 0}
        message = "throwing cases cannot yield"
    elif invalid == "empty-processing":
        summary["cases"][0]["segments"] = [{"mode": "local", "returns": []}]
        message = "processing requires operations"
    else:
        summary["cases"][0]["segments"] = None
        message = "valid list"
    with pytest.raises(StructuralValidationError, match=message):
        compile_flat_response(wire, material)
