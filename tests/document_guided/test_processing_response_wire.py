"""Exact output sharing preserves existing processing validation and ownership."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory, read_json
from skillflow.common.structural_correction import ResponseChain, StructuralCorrectionLimitReached
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided import fragment_wire
from skillflow.document_guided.fragment_wire import expand_processing_response, PROCESSING_WIRE_IDENTITY
from skillflow.document_guided.fragments import (
    assemble_fragments, fragment_correction_strategy, salvage_fragment, validate_fragment,
)
from skillflow.document_guided.online import CONFIG
from tests.document_guided.test_fragments import fixture


def envelope(payload, definitions=None):
    return {"format": PROCESSING_WIRE_IDENTITY, "shared_values": {} if definitions is None else definitions, "payload": payload}


def shared_fragment(value):
    payload = deepcopy(value)
    definitions = {}
    for index, (ir, record) in enumerate(payload["ir_semantics"].items()):
        name = f"v{index}"
        definitions[name] = record
        payload["ir_semantics"][ir] = {"$ref": name}
    return envelope(payload, definitions)


def test_exact_values_order_types_omissions_and_independent_copies():
    definition = {"nullable": None, "flag": False, "integer": 0, "float": 0.0, "text": "原文\n\"quoted\""}
    raw = envelope({"first": {"$ref": "v0"}, "second": {"$ref": "v0"}, "empty": {}}, {"v0": definition})
    before = deepcopy(raw)
    expanded = expand_processing_response(json.dumps(raw, ensure_ascii=False))
    assert json.dumps(expanded, ensure_ascii=False) == json.dumps({"first": definition, "second": definition, "empty": {}}, ensure_ascii=False)
    assert type(expanded["first"]["integer"]) is int and type(expanded["first"]["float"]) is float
    expanded["first"]["integer"] = 42
    assert expanded["second"]["integer"] == 0 and raw == before


def test_nested_references_and_literal_markers_are_data_after_escape():
    raw = envelope({"x": {"$ref": "v1"}, "literal": {"$literal_object": [
        ["$ref", "ordinary data"], ["$literal_object", {"$ref": "v0"}], ["$rows", []]]}},
        {"v0": [1, 2], "v1": {"nested": {"$ref": "v0"}}})
    assert expand_processing_response(raw) == {"x": {"nested": [1, 2]},
        "literal": {"$ref": "ordinary data", "$literal_object": [1, 2], "$rows": []}}
    plain = {"ir_semantics": {}, "constant": {"$ref": "literal"}}
    assert expand_processing_response(plain) == plain


@pytest.mark.parametrize("raw", [
    {"format": "unknown", "shared_values": {}, "payload": {}},
    {"format": PROCESSING_WIRE_IDENTITY, "payload": {}},
    {"format": PROCESSING_WIRE_IDENTITY, "shared_values": {}, "payload": {}, "extra": True},
    envelope({}, []),
    envelope({}, {"old_ir": {}}),
    envelope({"$ref": "v0"}),
    envelope({"$ref": 0}, {"v0": {}}),
    envelope({"$ref": "v0", "extra": True}, {"v0": {}}),
    envelope({"$ref": "v0"}, {"v0": {"$ref": "v0"}}),
    envelope({"$ref": "v0"}, {"v0": {"$ref": "v1"}, "v1": {"$ref": "v0"}}),
    envelope({}, {"v0": {"$ref": "v1"}}),
    envelope({"$literal_object": {"a": 1}}),
    envelope({"$literal_object": [["a", 1], ["a", 2]]}),
    envelope({"$literal_object": [[0, 1]]}),
    envelope({"$literal_object": [["a"]]}),
    envelope({"$literal_object": [["a", 1, 2]]}),
    envelope([], {"v0": {}}),
])
def test_malformed_envelopes_and_unused_definitions_are_rejected(raw):
    with pytest.raises(ValueError):
        expand_processing_response(raw)


@pytest.mark.parametrize("raw", [
    '{"format":"skillflow-processing-json-v1","shared_values":{},"payload":{"x":1,"x":2}}',
    '{"format":"skillflow-processing-json-v1","shared_values":{},"payload":{"x":NaN}}',
    '{"format":"skillflow-processing-json-v1","shared_values":{},"payload":{"x":Infinity}}',
    '{"format":"skillflow-processing-json-v1","shared_values":{},"payload":{"x":1e400}}',
    envelope({"x": float("nan")}),
])
def test_duplicate_keys_and_nonfinite_values_are_not_normalized(raw):
    with pytest.raises(ValueError):
        expand_processing_response(raw)


@pytest.mark.parametrize("limit,value,payload", [
    ("MAX_EXPANDED_CHARS", 30, {"a": "x" * 50}),
    ("MAX_EXPANDED_NODES", 3, {"a": [1, 2, 3]}),
    ("MAX_EXPANDED_DEPTH", 3, {"a": {"b": {"c": 1}}}),
])
def test_expansion_limit_has_actionable_failure_before_expansion(monkeypatch, limit, value, payload):
    monkeypatch.setattr(fragment_wire, limit, value)
    with pytest.raises(ValueError, match="without omitting records"):
        expand_processing_response(envelope({"$ref": "v0"}, {"v0": payload}))


def test_exponential_reference_graph_is_rejected_without_materializing_it():
    definitions = {"v0": "source"}
    for index in range(1, 32):
        definitions[f"v{index}"] = [{"$ref": f"v{index-1}"}] * 2
    with pytest.raises(ValueError, match="supported limits"):
        expand_processing_response(envelope({"x": {"$ref": "v31"}}, definitions))


@pytest.mark.parametrize("dependency_first", [False, True])
def test_reference_indirection_depth_is_bounded_even_for_scalar_aliases(monkeypatch, dependency_first):
    monkeypatch.setattr(fragment_wire, "MAX_EXPANDED_DEPTH", 4)
    definitions = {f"v{i}": {"$ref": f"v{i+1}"} for i in range(6)}
    definitions["v6"] = "scalar"
    if dependency_first:
        definitions = dict(reversed(list(definitions.items())))
    with pytest.raises(ValueError, match="indirection"):
        expand_processing_response(envelope({"x": {"$ref": "v0"}}, definitions))


def test_plain_and_shared_processing_have_identical_assembly_and_mapping():
    material, _, fragments = fixture()
    original = deepcopy(fragments)
    wrapped = shared_fragment(fragments["processing"])
    no_task = {key: value for key, value in material.items() if key != "task"}
    assert validate_fragment("processing", wrapped, no_task) == fragments["processing"]
    assert assemble_fragments(wrapped, fragments["task-correspondence"], fragments["sensitivity"], material) == assemble_fragments(
        fragments["processing"], fragments["task-correspondence"], fragments["sensitivity"], material)
    assert fragments == original


def test_shared_output_does_not_weaken_ownership_or_coverage():
    material, _, fragments = fixture()
    processing = fragments["processing"]
    bad = {**deepcopy(processing), "task": {"purpose": "forbidden"}}
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", shared_fragment(bad), material)
    assert any(row["path"] == "/task" for row in caught.value.diagnostics)
    encoded = shared_fragment(processing)
    del encoded["payload"]["ir_semantics"]["ir_return"]
    # A complete old record remains in shared_values, but an omitted current IR
    # cannot be supplied implicitly from it.
    with pytest.raises(StructuralValidationError):
        validate_fragment("processing", encoded, material)


def test_semantic_errors_keep_expanded_coordinates_and_salvage_boundaries():
    material, _, fragments = fixture()
    bad = fragments["processing"]
    bad["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]["unknown"] = True
    errors = []
    for candidate in (bad, shared_fragment(bad)):
        with pytest.raises(StructuralValidationError) as caught:
            validate_fragment("processing", candidate, material)
        errors.append(caught.value.diagnostics)
    assert errors[0] == errors[1]
    assert all(not row["path"].startswith(("/payload", "/shared_values")) for row in errors[1])
    assert salvage_fragment("processing", bad, material) == salvage_fragment("processing", shared_fragment(bad), material)
    assert salvage_fragment("processing", envelope({}, {"v0": {"$ref": "v1"}}), material) == (None, [])


@pytest.mark.parametrize("invalid_again", [False, True])
def test_shared_response_record_correction_and_zero_call_replay(tmp_path, invalid_again):
    material, _, fragments = fixture()
    bad = fragments["processing"]
    bad["ir_semantics"]["ir_call"]["order"] = "invalid"
    corrected = deepcopy(bad["ir_semantics"]["ir_call"])
    corrected["order"] = "invalid" if invalid_again else "fixed"
    first = shared_fragment(bad)
    replacement = envelope({"replacements": [{"record_id": "/ir_semantics/ir_call", "value": {"$ref": "v0"}}]}, {"v0": corrected})
    answers = [json.dumps(first), json.dumps(replacement)]
    saved_answers = deepcopy(answers)

    class Client:
        def complete(self, prompt):
            if len(answers) == 1:
                assert "MECHANICAL RECORD CORRECTION" in prompt
                assert '"/ir_semantics/ir_call"' in prompt
            return answers.pop(0)

    args = dict(prefix="calls", base_prompt="Fill the complete processing fragment.", request_kind="processing_fragment",
        config=CONFIG, writer=ArtifactWriter(()), validate=lambda value: validate_fragment("processing", value, material),
        max_corrections=1)
    chain = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("processing"),
                          client_factory=injected_factory(Client()))
    if invalid_again:
        with pytest.raises(StructuralCorrectionLimitReached):
            chain.run()
    else:
        assert chain.run()["ir_semantics"]["ir_call"] == corrected
    assert chain.last_candidate["ir_semantics"]["ir_return"] == bad["ir_semantics"]["ir_return"]
    assert read_json(tmp_path / "calls/a001/response.json") == saved_answers[0]
    assert read_json(tmp_path / "calls/a002/response.json") == saved_answers[1]
    assert "format" not in read_json(tmp_path / "calls/a002/merged-candidate.json")
    replay = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("processing"), replay=True)
    if invalid_again:
        with pytest.raises(StructuralCorrectionLimitReached):
            replay.run()
    else:
        assert replay.run() == chain.value
    assert replay.snapshot() == chain.snapshot() and not answers
    assert not (tmp_path / "calls/a003").exists()


def test_shared_wire_diagnostic_requests_full_correction_without_salvage(tmp_path):
    material, _, fragments = fixture()
    bad = envelope({"$ref": "v0"})
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", bad, material)
    assert caught.value.diagnostics[0]["code"] == "processing_wire"
    strategy = fragment_correction_strategy("processing")
    prompt = strategy.build_prompt("Fill processing.", bad, caught.value.diagnostics)
    assert "MECHANICAL RECORD CORRECTION" not in prompt
    assert strategy.merge(bad, shared_fragment(fragments["processing"])) == fragments["processing"]


def test_missing_ir_requests_only_its_coverage_slot_and_keeps_all_base_material():
    from tests.document_guided.test_processing_display import materials, prompt
    from skillflow.document_guided.processing_display import _parts
    from skillflow.common.structural_correction import correction_prompt
    from skillflow.document_guided.processing_correction import coverage_diagnostics
    logical = materials()
    candidate = deepcopy(logical["repair_context"]["previous_fragment"])
    del candidate["ir_semantics"]["ir_0"]
    encoded = shared_fragment(candidate)
    before = deepcopy(encoded)
    diagnostics = coverage_diagnostics(candidate, set(logical["repair_context"]["previous_fragment"]["ir_semantics"]))
    strategy = fragment_correction_strategy("processing")
    base = prompt(logical)
    result = strategy.build_prompt(base, json.dumps(encoded), diagnostics)
    assert "MECHANICAL RECORD CORRECTION" in result
    assert len(result) < len(correction_prompt(base, candidate, diagnostics))
    _, expanded, suffix = _parts(result)
    correction = expanded.get("correction") or json.loads(result.split("\nSCOPED_PROCESSING_CORRECTION_JSON\n")[-1])
    assert set(correction["coverage_slots"]) == {"ir_0"}
    assert correction["records"] == {} and "candidate" not in correction
    assert correction["diagnostics"] == diagnostics
    assert {key: value for key, value in expanded.items() if key != "correction"} == logical
    from skillflow.document_guided.fragment_wire import output_wire_instructions
    assert suffix.startswith(_parts(base)[2]
        + "\n\nPROCESSING CORRECTION RESPONSE GRAMMAR\n" + output_wire_instructions())
    assert encoded == before


def test_fresh_shared_processing_seven_requests_real_backend_and_zero_call_replay(tmp_path, monkeypatch):
    from skillflow.document_guided import runner
    from skillflow.graph.extraction.compiler import compile_candidate
    from skillflow.propagation.annotation.loading import load_annotation_run
    from skillflow.document_guided.fragments import split_fragments
    from tests.document_guided.test_parallel_runner import Harness, freeze_producer, _cfg_wire
    from tests.document_guided.test_input_contract_completeness import call_sample

    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    material, call_wire = call_sample()
    block = material["cfg"]["blocks"]["sample"]
    candidate = {"entry_block_ref": "sample", "blocks": [{
        "block_ref": "sample", "block_name": block["block_name"],
        "data_source_kind": block["data_source_kind"], "constraints": block["constraints"],
        "instructions": [{"instruction_ref": ir["id"], **{key: value for key, value in ir.items() if key != "id"}}
                         for ir in block["instructions"]]}], "edges": []}
    current = compile_candidate(candidate)
    assert current.ok
    call_wire["ir_semantics"] = {
        new.id: call_wire["ir_semantics"][old["id"]]
        for old, new in zip(block["instructions"], current.cfg.blocks["block_001"].instructions)}

    class SharedHarness(Harness):
        def __init__(self, directory, shared):
            super().__init__(directory)
            self.shared = shared
            self.example["source"] = material["source"]["files"][0]["content"]
            self.example["task_candidate"] = {key: deepcopy(material["task"][key])
                                               for key in ("purpose", "requirements", "issues")}
            self.graph = _cfg_wire(candidate)
            self.wire = deepcopy(call_wire)
            self.fragments = split_fragments(call_wire)

        def complete(self, stage, prompt):
            value = super().complete(stage, prompt)
            return shared_fragment(value) if stage == "processing" and self.shared else value

    snapshots = []
    for shared in (False, True):
        name = "shared" if shared else "plain"
        harness = SharedHarness(tmp_path / name, shared)
        harness.prepare(tmp_path / (name + "-source"))
        result = runner.run(harness.directory, client_factory=harness.factory)
        assert result["status"] == "complete", result
        assert result["annotation_review"] == "review_passed"
        assert len(harness.calls) == result["counts"]["logical_calls"] == 7
        assert result["counts"]["structural_corrections"] == 0 and not result["repair_used"]
        assert runner.POLICY["workers"] == 2
        loaded = load_annotation_run(harness.directory / "annotation")
        assert loaded["compiled_annotation"]["input_contracts"]
        receipt = read_json(harness.directory / "audit/input-contract-review.json")
        assert receipt["source_review_complete"]
        assert read_json(harness.directory / "doe/doe-result.json")["status"] == "complete"
        snapshots.append((loaded["raw_annotation"], loaded["compiled_annotation"], loaded["mapping"],
                          {name: read_json(harness.directory / "propagation" / name)
                           for name in ("data.json", "records.json", "sinks.json")}))
        saved = {str(path.relative_to(harness.directory)): path.read_bytes()
                 for path in harness.directory.rglob("response.json")}
        assert runner.replay(harness.directory) == result
        assert len(harness.calls) == 7
        assert saved == {str(path.relative_to(harness.directory)): path.read_bytes()
                         for path in harness.directory.rglob("response.json")}
    assert snapshots[0] == snapshots[1]
