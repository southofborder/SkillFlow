"""Offline fragment isolation, pure assembly, bounded records and salvage."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory
from skillflow.common.structural_correction import ResponseChain
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.annotation_wire import compile_flat_response, normalize_flat_annotation
from skillflow.document_guided.cfg_wire import normalize_cfg_wire
from skillflow.document_guided.fragments import (
    assemble_fragments, fragment_adapter, fragment_correction_strategy,
    salvage_fragment, split_fragments, validate_fragment,
)
from skillflow.document_guided.online import CONFIG
from tests.document_guided.test_annotation_wire import sample


def fixture():
    material, wire = sample()
    return material, wire, split_fragments(wire)


def test_complete_processing_uses_no_task_and_assembly_preserves_inputs_and_replay():
    material, wire, fragments = fixture()
    original = deepcopy(fragments)
    p = fragments["processing"]
    source_only = {key: value for key, value in material.items() if key != "task"}
    assert validate_fragment("processing", p, source_only) == p
    assert validate_fragment("sensitivity", fragments["sensitivity"], source_only, p) == fragments["sensitivity"]
    result = assemble_fragments(p, fragments["task-correspondence"], fragments["sensitivity"], material)
    assert fragments == original
    saved, raw, compiled, mapping = result
    assert compile_flat_response(saved, material) == result
    assert compiled["demands"][0]["target"]["operation_path"][3] == 1
    assert raw["task_revision_id"] == material["task"]["task_sha256"]
    assert mapping["fragment_origins"]["/realizations"] == "task-correspondence"
    assert mapping["fragment_origins"]["/ir_semantics"] == "processing"
    assert "cannot_assess" not in str(fragment_adapter("processing").json_schema())


@pytest.mark.parametrize("kind,key,value", [
    ("processing", "demands", []), ("processing", "realizations", []),
    ("task-correspondence", "ir_semantics", {}), ("task-correspondence", "locations", {}),
    ("sensitivity", "demands", []), ("sensitivity", "task", {}),
])
def test_fragment_top_level_ownership_is_strict(kind, key, value):
    material, _, fragments = fixture()
    candidate = deepcopy(fragments[kind])
    candidate[key] = value
    with pytest.raises(StructuralValidationError):
        validate_fragment(kind, candidate, material, fragments["processing"])


def test_processing_forbids_hidden_operation_demands_and_sensitivity():
    material, _, fragments = fixture()
    p = fragments["processing"]
    p["ir_semantics"]["ir_call"]["segments"][0]["ops"][0]["demands"] = []
    p["ir_semantics"]["ir_call"]["sensitivity"] = []
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", p, material)
    assert any(row["path"].endswith("/sensitivity") for row in caught.value.diagnostics)
    assert any(row["path"].endswith("/demands") for row in caught.value.diagnostics)


def test_schema_failure_reports_source_and_local_returns_without_obsolete_order_each_rules():
    material, wire, _ = fixture()
    spec = wire["ir_semantics"]["ir_call"]
    spec["evidences"] = [{"target": {"instruction_id": "ir_call", "path": []}}]
    spec["sensitivity"] = [{"value": {"kind": "local", "name": "reply"}, "label": "Credential"}]
    spec["segments"].append({"mode": "local", "ops": [{"op": "compute", "inputs": [], "output": "unused"}]})
    wire["demands"] = [{"requirement_id": "R1", "target": {"instruction_id": "ir_call", "side": "output", "index": 0},
        "preserve": "value", "path": ["rows", {"kind": "each"}, "keys", {"kind": "each"}], "reason": "Preserve returned keys."}]
    with pytest.raises(StructuralValidationError) as caught:
        normalize_flat_annotation(wire, material)
    paths = {row["path"] for row in caught.value.diagnostics}
    assert "/ir_semantics/ir_call/sensitivity/0/evidences" in paths
    assert "/ir_semantics/ir_call/order" not in paths
    assert "/ir_semantics/ir_call/segments/1/returns" in paths
    assert not any(row["code"] == "each_scope" for row in caught.value.diagnostics)


def test_sensitivity_inherits_only_existing_source_and_keeps_exact_failure_pointer():
    material, _, fragments = fixture()
    p = fragments["processing"]
    s = {"declarations": [{"instruction_id": "ir_call", "value": {"kind": "local", "name": "reply"}, "label": "Credential"}]}
    assert validate_fragment("sensitivity", s, {k: v for k, v in material.items() if k != "task"}, p) == s
    saved, raw, _, mapping = assemble_fragments(p, fragments["task-correspondence"], s, material)
    assert raw["ir_semantics"]["ir_call"]["sensitivity"][0]["evidences"][0]["file"].startswith("skill/")
    assert mapping["fragment_origins"]["/ir_semantics/ir_call/sensitivity/0"] == "sensitivity"
    p["ir_semantics"]["ir_call"]["evidences"] = [{"target": {"instruction_id": "ir_call", "path": []}}]
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("sensitivity", s, material, p)
    assert caught.value.diagnostics[0]["path"] == "/declarations/0/evidences"


def test_cfg_reports_acquisition_and_dispatch_at_actual_wire_inputs():
    candidate = {"entry_block_ref": "a", "blocks": [
        {"block_ref": "a", "data_source_kind": "external", "instructions": [
            {"opcode": "acquire", "outputs": [{"type": "result", "identifier": "value"}]}, {"opcode": "dispatch"}]},
        {"block_ref": "b", "instructions": [{"opcode": "return"}]},
        {"block_ref": "c", "instructions": [{"opcode": "return"}]}], "edges": [
            {"source_block_ref": "a", "target_block_ref": "b", "condition_text": "if selected"},
            {"source_block_ref": "a", "target_block_ref": "c", "condition_text": "otherwise"}]}
    before = deepcopy(candidate)
    with pytest.raises(StructuralValidationError) as caught:
        normalize_cfg_wire(candidate)
    assert {row["path"] for row in caught.value.diagnostics} == {
        "/blocks/0/instructions/0/inputs", "/blocks/0/instructions/1/inputs"}
    assert candidate == before


def test_record_correction_real_chain_reuses_other_records_and_replays(tmp_path):
    material, _, fragments = fixture()
    p = fragments["processing"]
    p["ir_semantics"]["ir_call"]["segments"].append({"mode": "local", "ops": [{"op": "compute", "inputs": [], "output": "unused"}]})
    corrected = deepcopy(p["ir_semantics"]["ir_call"])
    corrected["segments"][-1]["returns"] = []
    replies = [json.dumps(p), json.dumps({"replacements": [{"record_id": "/ir_semantics/ir_call", "value": corrected}]})]
    class Client:
        def complete(self, prompt):
            if len(replies) == 1:
                assert "MECHANICAL RECORD CORRECTION" in prompt
                assert '"/ir_semantics/ir_call"' in prompt
            return deepcopy(replies.pop(0))
    args = dict(prefix="calls", base_prompt="Fill the processing fragment.", request_kind="processing_fragment",
        config=CONFIG, writer=ArtifactWriter(()), validate=lambda x: validate_fragment("processing", x, material), max_corrections=1)
    chain = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("processing"), client_factory=injected_factory(Client()))
    result = chain.run()
    assert result["ir_semantics"]["ir_return"] == p["ir_semantics"]["ir_return"]
    assert result["locations"] == p["locations"]
    assert result["ir_semantics"]["ir_call"] == corrected
    replay = ResponseChain(tmp_path, **args, correction_strategy=fragment_correction_strategy("processing"), replay=True)
    assert replay.run() == result and not replies
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Fill processing.", p, [{"code": "order", "path": "/ir_semantics/ir_call/order", "message": "Specify order."}])
    with pytest.raises(StructuralValidationError, match="existing identity"):
        strategy.merge(p, {"replacements": [{"record_id": "/ir_semantics/new", "value": corrected}]})


def test_salvage_invalid_processing_retains_valid_ir_without_fake_output():
    material, _, fragments = fixture()
    p = fragments["processing"]
    p["ir_semantics"]["ir_call"]["output_bindings"][0]["value"] = {"kind": "local", "name": "absent"}
    retained, gaps = salvage_fragment("processing", p, material)
    assert retained is not None and set(retained["ir_semantics"]) == {"ir_return"}
    assert gaps[0]["instruction_id"] == "ir_call" and gaps[0]["unmodeled"]
    assert gaps[0]["origin"] == "validation" and not gaps[0]["evidences"]
    assert validate_fragment("processing", retained, material, validation_gaps=gaps) == retained
    assert salvage_fragment("processing", {"outcome": "cannot_assess", "failure": {}}, material) == (None, [])


def test_salvage_sensitivity_never_drops_processing_and_mapping_keeps_task_gap():
    material, _, fragments = fixture()
    p = fragments["processing"]
    s = {"declarations": [{"instruction_id": "ir_call", "value": {"kind": "local", "name": "absent"}, "label": "Credential"}]}
    retained, gaps = salvage_fragment("sensitivity", s, material, p)
    assert retained == {"declarations": []} and len(gaps) == 1 and not gaps[0]["unmodeled"]
    result = assemble_fragments(p, fragments["task-correspondence"], retained, material, validation_gaps=gaps)
    assert set(result[1]["ir_semantics"]) == set(p["ir_semantics"])
    assert compile_flat_response(result[0], material) == result
    bad = {"realizations": [{"requirement_id": "R1", "bindings": [{"target": {"instruction_id": "absent", "path": []}, "reason": "Unsupported target."}]}]}
    mapping, barriers = salvage_fragment("task-correspondence", bad, material, p)
    assert mapping and mapping["realizations"][0]["gaps"]
    assert barriers == []
    assert validate_fragment("task-correspondence", mapping, material, p) == mapping


def test_processing_source_gap_has_real_citation_and_validation_origin_is_program_only():
    material, _, fragments = fixture()
    p = fragments["processing"]
    citation = deepcopy(p["ir_semantics"]["ir_call"]["evidences"][0])
    p["processing_gaps"] = [{"instruction_id": "ir_call", "reason": "A source-described internal state relationship remains opaque.",
                             "evidences": [citation], "unmodeled": True}]
    del p["ir_semantics"]["ir_call"]
    assert validate_fragment("processing", p, {k: v for k, v in material.items() if k != "task"}) == p
    p["processing_gaps"][0]["evidences"][0]["file"] = "skill/absent.txt"
    with pytest.raises(StructuralValidationError) as caught:
        validate_fragment("processing", p, material)
    assert any(row["path"] == "/processing_gaps/0/evidences/0/file" for row in caught.value.diagnostics)
    p["processing_gaps"][0]["origin"] = "validation"
    with pytest.raises(StructuralValidationError):
        validate_fragment("processing", p, material)


def test_salvage_does_not_return_upstream_barriers_again():
    from skillflow.propagation.contracts.limitations import validation_gap
    material, _, fragments = fixture()
    upstream = [validation_gap("ir_return", [{"code": "scope", "path": "/source", "message": "An upstream validation barrier."}], unmodeled=False)]
    s = {"declarations": [{"instruction_id": "ir_call", "value": {"kind": "local", "name": "absent"}, "label": "Credential"}]}
    retained, own = salvage_fragment("sensitivity", s, material, fragments["processing"], validation_gaps=upstream)
    assert retained == {"declarations": []}
    assert len(own) == 1 and own[0]["instruction_id"] == "ir_call"
