"""One correction keeps complete review inputs and exact candidate records."""
from copy import deepcopy
import json

import pytest

from skillflow.common.prompt_format import compact_json
from skillflow.common.structural_correction import correction_prompt, _current_diagnostics, VERSION
from skillflow.common.validation import StructuralValidationError, diagnostic_materials
from skillflow.document_guided.fragments import fragment_correction_strategy
from skillflow.document_guided.review_correction import (
    compact_review_correction, _correction_tables, INPUT_MARKER, SOURCE_MARKER,
)
from skillflow.document_guided.review_display import (
    pack_review_payload, expand_review_payload, display_instructions,
)


def candidate():
    return {"outcome": "completed", "findings": [], "input_contract_checks": [],
            "input_projection_checks": [], "source_input_findings": []}


def context(value, diagnostics):
    current, examples = _current_diagnostics(diagnostics)
    return {"protocol": VERSION, "candidate": value, "diagnostics": current, "format_examples": examples}


def prompt(payload, source="Original source.\n中文原文。\nINPUT_JSON\nLiteral source marker.\n"):
    return ("Review only these materials.\n" + display_instructions() + "\nRESPONSE FORMAT\n"
            + "Return the complete strict review.\n" + INPUT_MARKER
            + compact_json(pack_review_payload(payload)) + SOURCE_MARKER + source)


def split(value):
    start = value.index(INPUT_MARKER) + len(INPUT_MARKER)
    display, length = json.JSONDecoder().raw_decode(value[start:])
    return expand_review_payload(display), value[start + length:]


def test_joint_display_preserves_complete_original_candidate_diagnostics_and_source():
    evidence = {"file": "example/SKILL.md", "start_line": 2, "end_line": 3,
                "reason": "The complete source establishes this recorded scope and its original information."}
    original = {"task": {"purpose": "Keep result"}, "cfg": {"blocks": []}, "availability": {},
                "annotation": {"contracts": [{"id": f"C{i}", "evidences": [evidence]} for i in range(120)]}}
    value = candidate()
    value["input_contract_checks"] = [{"obligation_id": f"O{i}", "contract_id": f"C{i}",
        "status": "accepted", "reason": evidence["reason"], "evidences": [evidence], "scope_checks": []}
        for i in range(120)]
    diagnostics = [{"code": "schema", "path": "/source_input_findings/0/actual/path", "message": "Field required"}]
    before = deepcopy((original, value, diagnostics))
    base = prompt(original)
    packet = context(value, diagnostics)
    fallback = correction_prompt(base, value, diagnostics)
    result = compact_review_correction(base, fallback, packet)
    assert len(result) < len(fallback) and "JOINT CORRECTION MATERIAL" in result
    expanded, source = split(result)
    assert compact_json({k: v for k, v in expanded.items() if k != "correction"}) == compact_json(original)
    assert compact_json(expanded["correction"]) == compact_json(packet)
    assert source == split(base)[1]
    assert result.startswith(base[:base.index(INPUT_MARKER)])
    assert before == (original, value, diagnostics)
    assert result == compact_review_correction(base, fallback, packet)


def test_correction_tables_keep_literal_markers_key_order_types_and_occurrences():
    records = [{"$ref": "v0", "number": False}, {"number": 0, "$rows": []},
               {"x": 1, "nullable": None}, {"x": 1.0}, {"$literal_object": [["x", 1]]}]
    value = {"annotation": [{"a": 1}], "correction": {"records": records * 3}}
    before = compact_json(value)
    display = _correction_tables(value)
    expanded = expand_review_payload(display)
    assert compact_json(expanded) == before and compact_json(value) == before
    expanded["correction"]["records"][0]["number"] = "changed"
    assert expanded["correction"]["records"][5]["number"] is False


@pytest.mark.parametrize("base", ["Unknown prompt", "\nRESPONSE FORMAT\nx\nINPUT_JSON\n{invalid}",
    "\nRESPONSE FORMAT\nx\nINPUT_JSON\n{\"task\":{},\"cfg\":{},\"annotation\":{},\"availability\":{}}\nMissing source marker"])
def test_unknown_or_unparseable_prompt_uses_complete_existing_fallback(base):
    packet = context(candidate(), [{"code": "schema", "path": "", "message": "Invalid"}])
    fallback = correction_prompt(base, candidate(), packet["diagnostics"])
    assert compact_review_correction(base, fallback, packet) == fallback


def test_reserved_correction_key_and_small_payload_never_increase_presentation():
    original = {"task": {}, "cfg": {}, "annotation": {}, "availability": {}, "correction": "literal"}
    base = prompt(original)
    packet = context(candidate(), [{"code": "schema", "path": "", "message": "Invalid"}])
    fallback = correction_prompt(base, candidate(), packet["diagnostics"])
    assert compact_review_correction(base, fallback, packet) == fallback
    del original["correction"]
    base = prompt(original)
    fallback = correction_prompt(base, candidate(), packet["diagnostics"])
    assert len(compact_review_correction(base, fallback, packet)) <= len(fallback)


def test_runtime_roundtrip_failure_is_a_program_error_not_a_model_correction(monkeypatch):
    from skillflow.document_guided import review_correction
    original = {"task": {}, "cfg": {}, "annotation": {"repeated": "large " * 80}, "availability": {}}
    base = prompt(original)
    packet = context(candidate(), [{"code": "schema", "path": "", "message": "Invalid"}])
    fallback = correction_prompt(base, candidate(), packet["diagnostics"])
    monkeypatch.setattr(review_correction, "_correction_tables", lambda payload: pack_review_payload({}))
    with pytest.raises(ValueError, match="changed its complete logical payload") as caught:
        compact_review_correction(base, fallback, packet)
    assert not isinstance(caught.value, StructuralValidationError)


@pytest.mark.parametrize("diagnostic", [
    {"code": "schema", "path": "/source_input_findings/0/actual/path", "message": "Field required"},
    {"code": "input_contract_review_conflict", "path": "/findings/0", "message": "Explicit conflict"},
])
def test_review_source_or_cross_record_errors_use_one_full_candidate_correction(diagnostic):
    value = candidate(); value["findings"] = [{"unsupported": True}]
    strategy = fragment_correction_strategy("review")
    rendered = strategy.build_prompt("Existing full review input", value, [diagnostic])
    assert "MECHANICAL OUTPUT CORRECTION" in rendered and "MECHANICAL RECORD CORRECTION" not in rendered
    assert "Preserve each source-supported prior allegation" in rendered
    assert strategy.selected == {} and strategy.identity.endswith(":review:review-correction-v2")
    corrected = candidate()
    assert strategy.merge(value, corrected) == corrected
    for bad in ({"replacements": []}, {"outcome": "completed"}, {**corrected, "findings": None}):
        with pytest.raises(StructuralValidationError, match="whole review correction"):
            strategy.merge(value, bad)
    # Inner semantic errors remain the terminal candidate for strict validation
    # and isolation; the merge guard validates only the exact reply grammar.
    assert strategy.merge(value, value) == value


def test_local_review_record_errors_remain_record_replacements_and_audit_is_not_duplicated():
    value = candidate(); value["findings"] = [{"text": "existing allegation"}]
    raw = {"code": "schema", "path": "/findings/0/source_refs", "message": "Invalid source range"}
    diagnostic = {**raw, "audit": {"raw_diagnostics": [raw, raw]}}
    strategy = fragment_correction_strategy("review")
    rendered = strategy.build_prompt("Existing complete review input", value, [diagnostic])
    assert "MECHANICAL RECORD CORRECTION" in rendered and '"audit"' not in rendered
    assert strategy.selected == {"/findings/0": value["findings"][0]}
    corrected = {"text": "corrected allegation"}
    result = strategy.merge(value, {"replacements": [{"record_id": "/findings/0", "value": corrected}]})
    assert result["findings"] == [corrected]
    assert value["findings"] == [{"text": "existing allegation"}]
    assert len(diagnostic_materials([diagnostic])["raw_diagnostics"]) == 2
