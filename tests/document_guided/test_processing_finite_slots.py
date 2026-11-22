"""Processing repairs use concrete IR slots and preserve independent records."""
from copy import deepcopy
import json

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import injected_factory, read_json
from skillflow.common.structural_correction import ResponseChain, StructuralCorrectionLimitReached
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import fragment_correction_strategy, salvage_fragment, validate_fragment
from skillflow.document_guided.online import CONFIG
from tests.document_guided.test_fragments import fixture


def inputs():
    material, _, fragments = fixture()
    good = fragments["processing"]
    material = {key: value for key, value in material.items() if key != "task"}
    instructions = next(iter(material["cfg"]["blocks"].values()))["instructions"]
    instructions[0]["inputs"].append({"type": "external_resource", "identifier": "sdk"})
    for ir in ("ir_other_call", "ir_unfilled", "ir_unaffected"):
        spec = deepcopy(instructions[0])
        spec["id"] = ir
        spec["outputs"][0]["identifier"] = ir + "_response"
        instructions.insert(-1, spec)
        good["ir_semantics"][ir] = deepcopy(good["ir_semantics"]["ir_call"])
    gap = {"instruction_id": "ir_return", "reason": "The declared runtime interface cannot represent this return.",
           "unmodeled": True, "evidences": deepcopy(good["ir_semantics"]["ir_return"]["evidences"])}
    # A distinct precision gap is not an alternative coverage claim.
    good["processing_gaps"] = [{**gap, "reason": "Independent precision note.", "unmodeled": False}]
    bad = deepcopy(good)
    bad["processing_gaps"].append(gap)
    del bad["ir_semantics"]["ir_unfilled"]
    bad["ir_semantics"]["ir_call"]["output_bindings"][0]["value"] = {"kind": "input", "index": 1}
    del bad["ir_semantics"]["ir_other_call"]["segments"][0]["ops"][0]["input_contract"]
    return material, good, bad


def test_one_injected_correction_groups_coverage_and_independent_compiler_errors(tmp_path):
    material, good, bad = inputs()
    assert validate_fragment("processing", good, material) == good
    correction = {"coverage_slots": [{"instruction_id": "ir_return", "keep": "modeled"},
                   {"instruction_id": "ir_unfilled", "modeled": good["ir_semantics"]["ir_unfilled"]}],
        "fields": [{"path": "/ir_semantics/ir_call/output_bindings/0/value",
                    "value": good["ir_semantics"]["ir_call"]["output_bindings"][0]["value"]},
                   {"path": "/ir_semantics/ir_other_call/segments/0/ops/0/input_contract",
                    "value": good["ir_semantics"]["ir_other_call"]["segments"][0]["ops"][0]["input_contract"]}]}
    replies = iter((json.dumps(bad), json.dumps(correction)))
    sent = []

    class Client:
        def complete(self, prompt):
            sent.append(prompt)
            return next(replies)

    params = dict(prefix="calls", base_prompt="Complete frozen source and contracts.",
        request_kind="processing_fragment", config=CONFIG, writer=ArtifactWriter(()),
        validate=lambda raw: validate_fragment("processing", raw, material), max_corrections=1)
    strategy = fragment_correction_strategy("processing")
    result = ResponseChain(tmp_path, **params, correction_strategy=strategy,
        client_factory=injected_factory(Client())).run()
    diagnostics = read_json(tmp_path / "calls/a001/validation.json")["diagnostics"]
    assert {row["path"] for row in diagnostics if row["code"] == "instruction_coverage"} == {
        "/ir_semantics/ir_return", "/ir_semantics/ir_unfilled"}
    assert any(row["path"] == "/ir_semantics/ir_call/output_bindings/0/value"
        and "resource identity" in row["message"] for row in diagnostics)
    assert any(row["path"].startswith("/ir_semantics/ir_other_call/")
        and "contract" in row["code"] for row in diagnostics)
    assert len(sent) == 2 and "MECHANICAL RECORD CORRECTION" in sent[1]
    scope = json.loads(sent[1].split("\nSCOPED_PROCESSING_CORRECTION_JSON\n")[-1])
    assert scope["records"] == {}
    assert set(scope["field_slots"]) == {patch["path"] for patch in correction["fields"]}
    assert "/ir_semantics/ir_unaffected" not in scope["read_only_records"]
    assert result == good
    assert result["ir_semantics"]["ir_unaffected"] == bad["ir_semantics"]["ir_unaffected"]
    assert ResponseChain(tmp_path, **params, correction_strategy=fragment_correction_strategy("processing"),
                         replay=True).run() == result
    assert len(sent) == 2 and not (tmp_path / "calls/a003").exists()


@pytest.mark.parametrize("correction", [
    {"coverage_slots": [{"instruction_id": "ir_unaffected", "keep": "modeled"}]},
    {"coverage_slots": [{"instruction_id": "ir_return", "keep": "modeled"}] * 2},
    {"coverage_slots": [{"instruction_id": "ir_unfilled", "keep": "modeled"}]},
    {"coverage_slots": [{"instruction_id": "ir_return", "unmodeled_gaps": [{"instruction_id": "ir_unaffected", "unmodeled": True}]}]},
    {"replacements": [{"record_id": "/ir_semantics/ir_unaffected", "value": {}}]},
    {"replacements": [{"record_id": "/ir_semantics/ir_other_call", "value": {}}]},
    {"fields": [{"path": "/ir_semantics/ir_other_call/output_bindings/0/value", "value": {"kind": "input", "index": 0}}]},
    {"ir_semantics": {}},
])
def test_scope_rejects_invalid_or_unrelated_patches(correction):
    material, _, bad = inputs()
    before = deepcopy(bad)
    with pytest.raises(StructuralValidationError) as invalid:
        validate_fragment("processing", bad, material)
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Source.", bad, invalid.value.diagnostics)
    with pytest.raises(StructuralValidationError):
        strategy.merge(bad, correction)
    assert bad == before


def test_stale_candidate_is_rejected_and_unresolved_conflict_quarantines_both_sides():
    material, good, bad = inputs()
    with pytest.raises(StructuralValidationError) as invalid:
        validate_fragment("processing", bad, material)
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Source.", bad, invalid.value.diagnostics)
    changed = deepcopy(bad)
    changed["ir_semantics"]["ir_unaffected"]["order"] = "partial"
    with pytest.raises(StructuralValidationError, match="exact prior"):
        strategy.merge(changed, {"coverage_slots": [{"instruction_id": "ir_return", "keep": "modeled"}]})
    retained, gaps = salvage_fragment("processing", bad, material)
    assert retained["ir_semantics"] == {"ir_unaffected": good["ir_semantics"]["ir_unaffected"]}
    assert retained["processing_gaps"] == good["processing_gaps"]
    assert {gap["instruction_id"] for gap in gaps} == {"ir_call", "ir_other_call", "ir_unfilled", "ir_return"}


def test_known_scope_has_no_whole_replacement_when_no_record_is_editable(tmp_path):
    material, good, _ = inputs()
    good["unsupported_section"] = "Malformed unrelated root field."
    calls = 0

    class Client:
        def complete(self, prompt):
            nonlocal calls
            calls += 1
            return good

    chain = ResponseChain(tmp_path, prefix="calls", base_prompt="Complete source.",
        request_kind="processing_fragment", config=CONFIG, writer=ArtifactWriter(()),
        validate=lambda raw: validate_fragment("processing", raw, material), max_corrections=1,
        correction_strategy=fragment_correction_strategy("processing"), client_factory=injected_factory(Client()))
    with pytest.raises(StructuralCorrectionLimitReached):
        chain.run()
    assert calls == 1 and not (tmp_path / "calls/a002").exists()
