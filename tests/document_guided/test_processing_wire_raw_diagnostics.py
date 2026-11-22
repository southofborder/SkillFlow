"""A rejected pair tree yields bounded evidence, never a repaired interpretation."""
from copy import deepcopy
import hashlib
import json

import pytest

from skillflow.document_guided import processing_wire_diagnostics as diagnostics
from skillflow.document_guided.fragment_wire import (
    DEFINITION_NAME_PATTERN, PROCESSING_WIRE_IDENTITY, WIRE_ROOT_FIELDS,
    expand_processing_response, output_wire_example, output_wire_instructions, valid_definition_name,
)


def envelope(payload, definitions=None):
    return {"format": PROCESSING_WIRE_IDENTITY, "payload": payload,
            "shared_values": {} if definitions is None else definitions}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def groups(report):
    return {row["rule"]: row for row in report["groups"]}


def test_complete_shared_grammar_and_example_match_unchanged_codec():
    text = output_wire_instructions()
    for phrase in (DEFINITION_NAME_PATTERN, "Every JSON object member name", "only one shared_values",
                   "unused definitions", "no other members", "Forward references", "cycles",
                   "$literal_object", "numbers must be finite", "before allocation",
                   "complete expanded fragment", 'complete {"replacements":[...]}',
                   "final merged coverage is rechecked", "Plain complete JSON", "no templates"):
        assert phrase.lower() in text.lower()
    assert "v01" in text and "mnemonic names" in text
    example = output_wire_example()
    assert list(example) == ["format", "payload", "shared_values"]
    assert set(example) == WIRE_ROOT_FIELDS
    assert json.loads(text.splitlines()[-1]) == example
    expected = {"example_left": {"nested": ["exact", "value"]},
                "example_right": {"nested": ["exact", "value"]},
                "example_literal": {"$ref": "ordinary literal text", "nested": ["exact", "value"]}}
    assert expand_processing_response(example) == expected
    assert diagnostics.scan_processing_wire(encoded(example))["groups"] == []
    example["payload"].clear()
    assert output_wire_example()["payload"]  # no mutable global template


@pytest.mark.parametrize("name", ["AUTH", "v01", "v-1", "v", "0", "v١", "v0\n"])
def test_definition_and_reference_grammar_violations_are_reported_together(name):
    raw = encoded(envelope({"x": {"$ref": name}}, {name: {}}))
    assert not valid_definition_name(name)
    with pytest.raises(ValueError, match="vN"):
        expand_processing_response(raw)
    result = groups(diagnostics.scan_processing_wire(raw))
    assert result["definition_name"]["count"] == result["reference_name"]["count"] == 1
    for row in (result["definition_name"], result["reference_name"]):
        start, end = row["examples"][0]["span"]
        assert json.loads(raw[start:end]) == name


def test_real_failure_shape_keeps_both_tables_and_reports_independent_errors():
    # Independent synthetic fixture shaped like the observed failure; no saved
    # historical response, CFG or model execution is imported into this test.
    raw = ('{"format":"skillflow-processing-json-v1",'
           '"shared_values":{"AUTH":{"reason":"first"},"readReq":{"$ref":"AUTH"}},'
           '"payload":{"one":{"$ref":"readReq"},"two":{"$ref":"late"}},'
           '"shared_values":{"AUTH":{"reason":"different"},"late":{"$ref":"AUTH"}}}')
    before = raw.encode()
    with pytest.raises(ValueError, match="duplicate JSON member: shared_values"):
        expand_processing_response(raw)
    report = diagnostics.scan_processing_wire(raw)
    findings = groups(report)
    assert report["recognized_wire_format"] and report["coverage"]["complete"]
    assert report["raw_sha256"] == hashlib.sha256(before).hexdigest()
    assert report["raw_characters"] == len(raw)
    assert findings["duplicate_member"]["count"] == findings["root_members"]["count"] == 1
    assert findings["definition_name"]["count"] == findings["reference_name"]["count"] == 4
    example = findings["duplicate_member"]["examples"][0]
    assert raw[slice(*example["span"])] == raw[slice(*example["first_span"])] == '"shared_values"'
    assert example["occurrence_path"] == [{"member_index": 3, "occurrence": 2}]
    assert example["span"][0] > example["first_span"][0]
    rows = diagnostics.processing_wire_diagnostics(raw)
    assert len(rows) == 1 and rows[0]["path"] == ""
    assert rows[0]["context"]["raw_wire_scan"] == report
    assert not {"candidate", "payload", "shared_values", "expanded"}.intersection(report)
    assert raw.encode() == before
    with pytest.raises(ValueError, match="duplicate JSON member"):
        expand_processing_response(raw)


@pytest.mark.parametrize("second", ['{"v0":1}', '{"v1":1}', '{"v0":2}'])
def test_identical_disjoint_and_conflicting_tables_remain_equally_rejected(second):
    raw = ('{"format":"skillflow-processing-json-v1","shared_values":{"v0":1},'
           '"payload":{"x":{"$ref":"v0"}},"shared_values":' + second + '}')
    with pytest.raises(ValueError, match="duplicate JSON member"):
        expand_processing_response(raw)
    report = diagnostics.scan_processing_wire(raw)
    assert set(groups(report)) == {"duplicate_member", "root_members"}
    assert report["status"] == "complete"


def test_duplicate_names_inside_definition_and_payload_objects_have_exact_occurrences():
    raw = ('{"format":"skillflow-processing-json-v1","payload":{"x":1,"x":2},'
           '"shared_values":{"v0":1,"v0":2}}')
    report = diagnostics.scan_processing_wire(raw)
    examples = groups(report)["duplicate_member"]["examples"]
    assert groups(report)["duplicate_member"]["count"] == 2
    assert [raw[slice(*row["span"])] for row in examples] == ['"x"', '"v0"']
    assert examples[0]["occurrence_path"][-1]["occurrence"] == 2
    assert examples[1]["occurrence_path"][0] == {"member_index": 2, "occurrence": 1}


def test_raw_positions_are_code_points_and_escaped_member_names_are_compared_decoded():
    raw = ('{"format":"skillflow-processing-json-v1","payload":{"中文😀":1,"\\u4e2d文😀":2},'
           '"shared_values":{}}')
    report = diagnostics.scan_processing_wire(raw)
    example = groups(report)["duplicate_member"]["examples"][0]
    assert report["offset_unit"] == "unicode_code_points_zero_based_end_exclusive"
    assert raw[slice(*example["span"])] == '"\\u4e2d文😀"'
    assert raw[slice(*example["first_span"])] == '"中文😀"'
    assert report["raw_sha256"] == hashlib.sha256(raw.encode()).hexdigest()


def test_literal_keys_are_data_and_only_encoded_value_positions_are_scanned():
    value = envelope({"literal": {"$literal_object": [["$ref", "AUTH"],
                        ["$literal_object", {"$ref": "bad_name"}]]}})
    findings = groups(diagnostics.scan_processing_wire(encoded(value)))
    assert findings["reference_name"]["count"] == 1
    assert set(findings) == {"reference_name"}
    valid = envelope({"literal": {"$literal_object": [["$ref", "AUTH"], ["$rows", []]]}})
    assert diagnostics.scan_processing_wire(encoded(valid))["groups"] == []
    assert expand_processing_response(valid)["literal"] == {"$ref": "AUTH", "$rows": []}


@pytest.mark.parametrize("value,code", [
    ({"$ref": "v0", "other": True}, "marker_shape"),
    ({"$literal_object": {}}, "literal_pairs"),
    ({"$literal_object": [[1, "value"]]}, "literal_pairs"),
    ({"$literal_object": [["x", 1, 2]]}, "literal_pairs"),
    ({"$literal_object": [["x", 1], ["x", 2]]}, "literal_duplicate"),
    ({"$ref": 7}, "reference_name"),
])
def test_locally_definite_marker_errors_are_evidence_only(value, code):
    raw = encoded(envelope({"x": value}))
    with pytest.raises(ValueError):
        expand_processing_response(raw)
    assert groups(diagnostics.scan_processing_wire(raw))[code]["count"] == 1


@pytest.mark.parametrize("raw", [
    '{"format":"skillflow-processing-json-v1","payload":',
    '{"format":"skillflow-processing-json-v1",}',
    '{"format":"skillflow-processing-json-v1","payload":NaN}',
    '{"format":"skillflow-processing-json-v1","payload":"\\q"}',
    '{"format":"skillflow-processing-json-v1"} trailing',
])
def test_broken_syntax_reports_precise_incomplete_diagnostic_coverage(raw):
    report = diagnostics.scan_processing_wire(raw)
    assert report["status"] == "invalid_json"
    assert not report["coverage"]["complete"] and report["coverage"]["limitation"]
    assert 0 <= report["coverage"]["scanned_characters"] <= len(raw)
    assert report["groups"] == []
    assert diagnostics.processing_wire_diagnostics(raw)[0]["path"] == ""


@pytest.mark.parametrize("limit,budget,raw", [
    ("MAX_RAW_CHARACTERS", 20, encoded(envelope({}))),
    ("MAX_SCAN_NODES", 5, encoded(envelope({"x": list(range(100))}))),
    ("MAX_SCAN_DEPTH", 3, encoded(envelope({"x": [[[[0]]]]}))),
])
def test_scan_limits_do_not_change_acceptance_and_never_create_a_candidate(monkeypatch, limit, budget, raw):
    accepted_before = expand_processing_response(raw)
    monkeypatch.setattr(diagnostics, limit, budget)
    report = diagnostics.scan_processing_wire(raw)
    assert report["status"] == "limited" and not report["coverage"]["complete"]
    assert report["coverage"]["limitation"] and not report["groups"]
    assert expand_processing_response(raw) == accepted_before
    assert diagnostics.processing_wire_diagnostics(raw)[0]["path"] == ""


def test_many_violations_have_exact_counts_bounded_examples_and_deterministic_order():
    definitions = {f"invalid_{i}": {"$ref": f"invalid_{i}"} for i in range(600)}
    raw = encoded(envelope({}, definitions))
    report = diagnostics.scan_processing_wire(raw)
    assert report == diagnostics.scan_processing_wire(raw)
    assert report["coverage"]["complete"]
    for code in ("definition_name", "reference_name"):
        row = groups(report)[code]
        assert row["count"] == 600 and len(row["examples"]) == 3
        assert row["undisplayed_occurrences"] == 597
    assert len(encoded(report)) < 6000


def test_example_budget_omits_only_examples_not_counts_or_raw_identity(monkeypatch):
    monkeypatch.setattr(diagnostics, "MAX_EXAMPLE_CHARACTERS", 1)
    raw = encoded(envelope({"x": {"$ref": "bad"}}, {"bad": 1}))
    report = diagnostics.scan_processing_wire(raw)
    assert report["coverage"]["complete"] and report["raw_sha256"]
    for row in report["groups"]:
        assert row["count"] == row["undisplayed_occurrences"] == 1
        assert row["examples"] == []


def test_unused_definitions_are_scanned_but_reference_graphs_never_resolved():
    raw = encoded(envelope({}, {"unused_bad": {"$ref": "bad"}}))
    assert set(groups(diagnostics.scan_processing_wire(raw))) == {"definition_name", "reference_name"}
    for definition in ({"v0": {"$ref": "v0"}}, {"v0": {"$ref": "v1"}}):
        raw = encoded(envelope({}, definition))
        assert diagnostics.processing_wire_diagnostics(raw) == []
        with pytest.raises(ValueError):
            expand_processing_response(raw)


def test_unsupported_or_duplicate_format_does_not_infer_wire_grammar():
    raw = '{"format":"other","payload":{"$ref":"bad"},"shared_values":{"bad":1}}'
    report = diagnostics.scan_processing_wire(raw)
    assert not report["recognized_wire_format"] and report["groups"] == []
    raw = ('{"format":"skillflow-processing-json-v1","format":"other",'
           '"payload":{"$ref":"bad"},"shared_values":{"bad":1}}')
    report = diagnostics.scan_processing_wire(raw)
    assert not report["recognized_wire_format"]
    assert set(groups(report)) == {"duplicate_member"}


def test_nonstring_has_no_invented_raw_identity_and_unpaired_surrogate_is_safe():
    value = envelope({"x": {"$ref": "bad"}}, {"bad": 1})
    before = deepcopy(value)
    assert diagnostics.processing_wire_diagnostics(value) == [] and value == before
    report = diagnostics.scan_processing_wire(encoded(envelope({}, {"\ud800": 1})))
    assert report["status"] == "complete" and groups(report)["definition_name"]["count"] == 1
    json.dumps(report, ensure_ascii=False).encode("utf-8")


def test_nonfinite_exponent_is_reported_without_converting_arbitrary_integers():
    raw = '{"format":"skillflow-processing-json-v1","payload":{"x":1e9999},"shared_values":{}}'
    assert groups(diagnostics.scan_processing_wire(raw))["nonfinite_number"]["count"] == 1
    with pytest.raises(ValueError):
        expand_processing_response(raw)


def test_diagnostic_resource_failure_cannot_mask_the_original_rejection(monkeypatch):
    raw = '{"format":"skillflow-processing-json-v1","shared_values":{},"payload":{},"shared_values":{}}'
    with pytest.raises(ValueError, match="duplicate JSON member"):
        expand_processing_response(raw)
    def unavailable(self):
        raise MemoryError("diagnostic allocation unavailable")
    monkeypatch.setattr(diagnostics._Parser, "parse", unavailable)
    rows = diagnostics.processing_wire_diagnostics(raw)
    report = rows[0]["context"]["raw_wire_scan"]
    assert report["status"] == "limited" and report["groups"] == []
    assert "MemoryError" in report["coverage"]["limitation"]
    assert rows[0]["path"] == ""
    with pytest.raises(ValueError, match="duplicate JSON member"):
        expand_processing_response(raw)
