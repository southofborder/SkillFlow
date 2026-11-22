"""Preserve historical examples and validate newly generated current material."""
import json
import pytest

from skillflow.common.paths import project_root
from skillflow.common.validation import StructuralValidationError
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.document_guided.cfg_wire import CFGWire, normalize_cfg_wire
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import assemble_fragments, fragment_adapter, validate_fragment, split_fragments
from skillflow.document_guided.source_review import validate_source_review, FRAGMENT_RESPONSE_ADAPTER
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from skillflow.propagation.material import prepare_material
from tools.doe.prepare_document_guided_sample import synthetic_material


def test_delivered_whole_objects_compile_and_match_saved_outputs():
    """Check archived graph/assembly consistency without relabeling its producer."""
    root = project_root() / "examples/document-guided/synthetic"
    def read(name):
        return json.loads((root / name).read_text(encoding="utf-8"))
    wire = read("cfg-wire.json")
    CFGWire.model_validate(wire)
    candidate = normalize_cfg_wire(wire)
    assert candidate == read("graph-candidate.json")
    graph = compile_candidate(candidate)
    assert graph.ok, graph.diagnostics
    assert json.loads(graph.cfg.to_json()) == read("cfg.json")
    assert read("context.json")["cfg"] == read("cfg.json")
    historical_context = read("context.json")
    assert historical_context["runtime_contract"]["version"] == "skillflow-abstract-runtime-v11"
    assert historical_context["runtime_contract"] == read("source-review-input.json")["runtime_contract"]
    current_context = prepare_material(historical_context["source"], historical_context["cfg"],
                                       task_baseline=historical_context["task"])
    assert current_context["runtime_contract"] == runtime_contract()
    fragments = {name: read(name + ".json") for name in ("processing", "task-correspondence", "sensitivity")}
    for name, fragment in fragments.items():
        fragment_adapter(name).validate_python(fragment)
        # The delivered schema belongs to its original producer. New contract
        # fields are versioned additions, never rewritten into that receipt.
        assert read(name + "-schema.json")["type"] == "object"
    saved = read("assembled-annotation.json")
    assert saved == read("flat-annotation.json")
    assert split_fragments(saved) == fragments
    assert read("annotation.json") == read("backend-annotation.json")
    mapping = read("compilation-map.json")
    assert mapping["schema_version"] == "skillflow-processing-compilation-v12"
    assert mapping["compiler_version"] == "skillflow-processing-compiler-v12"
    assert mapping["wire_version"] == "skillflow-flat-annotation-v3"
    assert mapping["wire_paths"]
    assert mapping["fragment_origins"]["/realizations"] == "task-correspondence"
    assert mapping["fragment_origins"]["/ir_semantics"] == "processing"
    # The historical producer did not require the tool attachment. Preserve
    # that original receipt rather than implicitly certifying it under v5.
    for compile_current in (
        lambda: validate_fragment("processing", fragments["processing"], current_context),
        lambda: assemble_fragments(fragments["processing"], fragments["task-correspondence"],
                                   fragments["sensitivity"], current_context),
        lambda: compile_flat_response(saved, current_context),
    ):
        with pytest.raises(StructuralValidationError) as caught:
            compile_current()
        assert any(row["code"] == "input_contract_required" and row["path"].endswith("/input_contract")
                   for row in caught.value.diagnostics)
    assert read("source-review-schema.json")["type"] == "object"
    assert read("source-review-wire.json")["findings"] == read("source-review.json")["findings"] == []
    assert read("source-review.json")["schema_version"] == read("source-review-input.json")["identity"]


def test_delivered_synthetic_material_is_reproducible_without_network(tmp_path, monkeypatch):
    import socket
    def unexpected(*args, **kwargs):
        raise AssertionError("Offline sample must not open a network connection")
    monkeypatch.setattr(socket.socket, "connect", unexpected)
    monkeypatch.setattr("tools.doe.document_guided_client.Client", unexpected)
    root = project_root() / "examples/document-guided/synthetic"
    historical = {path: path.read_bytes() for path in root.iterdir() if path.is_file()}
    result = synthetic_material(tmp_path)
    assert result["annotation_compilation"] == result["graph_compilation"] == "passed"
    current = tmp_path / "synthetic"
    review_input = json.loads((current / "source-review-input.json").read_text(encoding="utf-8"))
    review_wire = json.loads((current / "source-review-wire.json").read_text(encoding="utf-8"))
    assert {"input_contract_checks", "input_projection_checks", "source_input_findings"} <= review_wire.keys()
    assert {row["obligation_id"] for row in review_wire["input_contract_checks"]} == {
        row["id"] for row in review_input["input_contract_inventory"]["obligations"]}
    assert review_wire["input_contract_checks"]
    assert all(row["status"] == "accepted" for row in review_wire["input_contract_checks"])
    assert review_wire["input_projection_checks"] == review_wire["source_input_findings"] == []
    second = tmp_path / "second"
    assert synthetic_material(second) == result
    for actual in sorted((tmp_path / "synthetic").iterdir()):
        assert actual.read_bytes() == (second / "synthetic" / actual.name).read_bytes()
    assert all(path.read_bytes() == before for path, before in historical.items())
    assert result["whole_graph_candidates"] == result["whole_annotations"] == 1
    assert result["program_assembled_annotations"] == 1
    assert result["semantic_fragments"] == 3 and result["annotation_model_calls"] == 0
    assert set(result["prompt_steps"]) == {"01-task", "02-flow", "03-cfg",
        "04-processing", "05-task-correspondence", "06-sensitivity", "07-source-review"}
    assert result["artifact_roles"]["backend-annotation.json"] == "program expansion"
    assert not (root / "02-relationships-prompt.txt").exists()
    assert not (root / "07-annotation-prompt.txt").exists()
    assert not (root / "08-source-review-prompt.txt").exists()
    assert "SEALED_TASK\n" not in (root / "04-processing-prompt.txt").read_text(encoding="utf-8")
    assert "SEALED_TASK\n" in (root / "05-task-correspondence-prompt.txt").read_text(encoding="utf-8")
    assert "SEALED_TASK\n" not in (root / "06-sensitivity-prompt.txt").read_text(encoding="utf-8")
    assert '"realizations"' not in (root / "04-processing-prompt.txt").read_text(encoding="utf-8")


def test_current_generator_cannot_overwrite_historical_sample():
    import pytest
    with pytest.raises(ValueError, match="historical sample is immutable"):
        synthetic_material(project_root() / "examples/document-guided", refresh=True)
