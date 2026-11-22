"""Processing input packing preserves all logical inputs and source boundaries."""
from copy import deepcopy
import json

import pytest

from skillflow.common.prompt_format import compact_json
from skillflow.common.structural_correction import correction_prompt, _current_diagnostics, VERSION
from skillflow.document_guided.processing_display import (
    INPUT_MARKER, SUFFIX_MARKER, _parts, _table_display, compact_processing_correction,
    expand_processing_material, pack_processing_material, render_processing_material,
)
from skillflow.document_guided.review_display import expand_review_payload, pack_review_payload


def materials():
    evidence = {"file": "skill/example.ts", "start_line": 4, "end_line": 7,
                "reason": "This exact source span specifies the source-backed input/output relationship."}
    semantics = {f"ir_{i}": {"evidences": [evidence], "output_bindings": [
        {"output_index": 0, "value": {"kind": "input", "index": 0}}]} for i in range(80)}
    return {"documents": {"flow": "Use the supplied input. skill/example.ts:4-7.\n"},
            "cfg": {"blocks": {"b1": {"instructions": [
                {"id": key, "opcode": "compute", "metadata": {"evidence": evidence}}
                for key in semantics]}}},
            "runtime_contract": {"rules": [{"text": evidence["reason"], "evidence": evidence}]},
            "repair_context": {"previous_fragment": {"locations": {}, "ir_semantics": semantics,
                                                       "processing_gaps": []},
                               "source_rechecks": [{"target_id": key, "evidences": [evidence]}
                                                   for key in semantics]}}


def prompt(value, source="1: Original source.\n2: 中文原文 😀\n3: PROCESSING_INPUT_JSON\n4: $ref is literal.\n"):
    return ("STEP RESPONSIBILITY\nProcessing.\n\nPREVIOUS WORK\n" + render_processing_material(value)
            + SUFFIX_MARKER + "Preserve source.\n\nRELATED SOURCE\n" + source
            + "\n\nOUTPUT REQUIREMENTS\nReturn the complete strict fragment.")


def test_complete_material_roundtrip_is_deterministic_immutable_and_smaller():
    value = materials()
    before = compact_json(value)
    packed = pack_processing_material(value)
    assert compact_json(expand_processing_material(packed)) == before
    assert compact_json(value) == before
    assert pack_processing_material(value) == packed
    assert len(compact_json(packed)) < len(before)
    expanded = expand_processing_material(packed)
    expanded["repair_context"]["previous_fragment"]["ir_semantics"]["ir_0"]["evidences"][0]["reason"] = "changed"
    assert expanded["repair_context"]["previous_fragment"]["ir_semantics"]["ir_1"]["evidences"][0]["reason"] != "changed"
    assert compact_json(value) == before


def test_generic_tables_preserve_order_optional_fields_numbers_and_literal_markers():
    rows = [{"$ref": "v0", "value": False}, {"value": 0, "$rows": []},
            {"value": 0.0}, {"value": None}, {"$literal_object": [["x", 1]]}]
    value = {"rows": rows * 4, "nested": {"$ref": "literal", "other": {"$rows": [1]}}}
    display = _table_display(value)
    assert display["record_columns"]
    assert compact_json(expand_review_payload(display)) == compact_json(value)
    assert compact_json(expand_processing_material(pack_processing_material(value))) == compact_json(value)


def test_logical_identity_tampering_and_invalid_shared_reference_are_rejected():
    value = pack_processing_material(materials())
    altered = deepcopy(value)
    altered["logical_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="logical identity"):
        expand_processing_material(altered)
    altered = deepcopy(value)
    altered["display"]["payload"] = {"$ref": "v999999"}
    with pytest.raises(ValueError, match="reference"):
        expand_processing_material(altered)
    with pytest.raises(ValueError, match="envelope"):
        expand_processing_material({**value, "unknown": True})


def test_runtime_roundtrip_failure_is_not_silently_accepted(monkeypatch):
    from skillflow.document_guided import processing_display
    monkeypatch.setattr(processing_display, "_table_display", lambda value: pack_review_payload({}))
    with pytest.raises(ValueError, match="changed its complete logical payload"):
        pack_processing_material(materials())


@pytest.mark.parametrize("local", [False, True])
def test_joint_correction_preserves_every_input_candidate_diagnostic_and_suffix(local):
    value = materials()
    candidate = value["repair_context"]["previous_fragment"]
    diagnostics = [{"code": "schema", "path": "/ir_semantics/ir_0/output_bindings/0/value",
                    "message": "Input reference requires a payload."}]
    current, examples = _current_diagnostics(diagnostics)
    base = prompt(value)
    if local:
        context = {"records": [{"record_id": "/ir_semantics/" + key, "value": record}
                               for key, record in candidate["ir_semantics"].items()],
                   "diagnostics": current}
        fallback = base + "\nSTRUCTURAL_CORRECTION_CONTEXT\nReturn selected replacements.\n" + compact_json(context)
    else:
        context = {"protocol": VERSION, "candidate": candidate, "diagnostics": current, "format_examples": examples}
        fallback = correction_prompt(base, candidate, diagnostics)
    before = compact_json((value, candidate, diagnostics, context))
    result = compact_processing_correction(base, fallback, context)
    assert len(result) < len(fallback)
    prefix, logical, suffix = _parts(result)
    assert "JOINT PROCESSING CORRECTION MATERIAL" in prefix
    assert compact_json({k: v for k, v in logical.items() if k != "correction"}) == compact_json(value)
    assert compact_json(logical["correction"]) == compact_json(context)
    assert suffix == _parts(base)[2]
    assert compact_json((value, candidate, diagnostics, context)) == before
    assert result == compact_processing_correction(base, fallback, context)


@pytest.mark.parametrize("base", ["Unknown prompt", "\nPROCESSING_INPUT_JSON\n{invalid}",
    "LOSSLESS PROCESSING INPUT\nPROCESSING_INPUT_JSON\n{}\nWrong boundary"])
def test_unknown_prompts_preserve_complete_fallback(base):
    context = {"candidate": {"invalid": "keep"}}
    fallback = base + "\nCorrect.\n" + compact_json(context)
    assert compact_processing_correction(base, fallback, context) == fallback


def test_duplicate_json_or_reserved_correction_key_keeps_complete_fallback():
    value = materials()
    value["correction"] = "literal existing input"
    base = prompt(value)
    context = {"candidate": "{\"x\":1,\"x\":2}"}
    fallback = base + "\nCorrect.\n" + compact_json(context)
    assert compact_processing_correction(base, fallback, context) == fallback
    invalid = base.replace('"format":"skillflow-processing-input-display-v1"',
                           '"format":"wrong","format":"skillflow-processing-input-display-v1"', 1)
    assert _parts(invalid) is None


def test_small_correction_keeps_shortest_complete_representation():
    base = prompt(materials())
    context = {"records": [], "diagnostics": []}
    fallback = base + "\nCorrect supplied records.\n" + compact_json(context)
    result = compact_processing_correction(base, fallback, context)
    assert len(result) <= len(fallback)
    if result != fallback:
        assert _parts(result)[1]["correction"] == context


def test_builder_retains_source_and_explicit_current_cfg_coverage_without_task():
    from skillflow.document_guided.prompts import build_fragment_prompt
    from skillflow.document_guided.source import source_packet, render_source, prompt_cfg
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    from tests.document_guided.test_boundary_prompt_alignment import material_inputs
    material, fragments, files = material_inputs()
    files = {**files, "skill/unused.txt": "Unreferenced source remains complete. 中文😀\n"}
    flow = "Inspect skill/SKILL.md:1-1.\nPROCESSING_INPUT_JSON\nLiteral marker in source discussion."
    repair = {"previous_fragment": fragments["processing"], "source_rechecks": []}
    contract = runtime_contract()
    result = build_fragment_prompt("processing", files=files, documents={"flow": flow}, cfg=material["cfg"],
        runtime_contract=contract, global_requirements="Keep all source behavior.", repair_context=repair)
    _, logical, suffix = _parts(result)
    assert set(logical) == {"documents", "cfg", "runtime_contract", "repair_context"}
    assert logical["documents"] == {"flow": flow}
    assert logical["cfg"] == prompt_cfg(material["cfg"], packet=source_packet(files))
    assert logical["runtime_contract"] == contract
    assert logical["repair_context"] == repair
    assert "RELATED SOURCE\n" + render_source(source_packet(files)) + "\n\nOUTPUT REQUIREMENTS\n" in suffix
    assert "SEALED_TASK" not in result
    start = result.index("REQUIRED_IR_IDS\n") + len("REQUIRED_IR_IDS\n")
    ids, _ = json.JSONDecoder().raw_decode(result[start:])
    assert ids == [ir["id"] for block in material["cfg"]["blocks"].values() for ir in block["instructions"]]
