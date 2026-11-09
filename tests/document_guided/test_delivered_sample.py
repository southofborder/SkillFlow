"""Validate the delivered objects, not a repaired copy of the example."""
import json

from skillflow.common.paths import project_root
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.document_guided.cfg_wire import CFGWire, normalize_cfg_wire
from skillflow.document_guided.annotation_wire import compile_flat_response
from skillflow.document_guided.fragments import assemble_fragments, fragment_adapter, validate_fragment
from skillflow.document_guided.source_review import validate_source_review, FRAGMENT_RESPONSE_ADAPTER
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from tools.doe.prepare_document_guided_sample import synthetic_material


def test_delivered_whole_objects_compile_and_match_saved_outputs():
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
    assert read("context.json")["runtime_contract"] == runtime_contract()
    fragments = {name: read(name + ".json") for name in ("processing", "task-correspondence", "sensitivity")}
    for name, fragment in fragments.items():
        fragment_adapter(name).validate_python(fragment)
        assert read(name + "-schema.json") == fragment_adapter(name).json_schema()
        assert validate_fragment(name, fragment, read("context.json"), processing=fragments["processing"]) == fragment
    saved, raw, compiled, mapping = assemble_fragments(fragments["processing"], fragments["task-correspondence"],
        fragments["sensitivity"], read("context.json"))
    assert saved == read("assembled-annotation.json") == read("flat-annotation.json")
    assert raw == read("annotation.json") == read("backend-annotation.json")
    assert compiled == read("compiled-annotation.json")
    assert mapping == read("compilation-map.json")
    assert mapping["wire_paths"]
    assert mapping["fragment_origins"]["/realizations"] == "task-correspondence"
    assert mapping["fragment_origins"]["/ir_semantics"] == "processing"
    assert compile_flat_response(read("assembled-annotation.json"), read("context.json")) == (saved, raw, compiled, mapping)
    assert read("source-review-schema.json") == FRAGMENT_RESPONSE_ADAPTER.json_schema()
    assert validate_source_review(read("source-review-wire.json"), read("source-review-input.json")) == read("source-review.json")


def test_delivered_synthetic_material_is_reproducible_without_network(tmp_path, monkeypatch):
    import socket
    def unexpected(*args, **kwargs):
        raise AssertionError("Offline sample must not open a network connection")
    monkeypatch.setattr(socket.socket, "connect", unexpected)
    monkeypatch.setattr("tools.doe.document_guided_client.Client", unexpected)
    result = synthetic_material(tmp_path)
    assert result["annotation_compilation"] == result["graph_compilation"] == "passed"
    root = project_root() / "examples/document-guided/synthetic"
    for actual in sorted((tmp_path / "synthetic").iterdir()):
        assert actual.read_bytes() == (root / actual.name).read_bytes()
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
