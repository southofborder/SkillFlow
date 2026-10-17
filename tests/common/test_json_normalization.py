"""The syntax repair changes exactly one unambiguous trailing character."""

import json

import pytest

from skillflow.common import json_normalization as normalizer
from skillflow.common.json_normalization import normalize_response
from skillflow.common.recording import canonical_sha256


@pytest.mark.parametrize("raw", [
    "{}", '  {"a": [1, true, null]}\r\n',
    '{"nested": {"braces": "}}}"}, "escaped": "\\\"}"}',
])
def test_valid_response_is_returned_verbatim_without_receipt(raw):
    candidate, receipt = normalize_response(raw)
    assert candidate is raw
    assert receipt is None


@pytest.mark.parametrize("raw", [
    "{}}", '{} \t}\r\n', ' \r\n{"a":{"b":[1,2]}}\t}\n',
    '{"text":"braces }} and escaped quote \\\""}}',
    '{"number": -1.23e-10, "integer": 123456789012345678901234567890}}',
    '{"line": "\\r\\n", "utf16": "\\ud83d\\ude00"}}',
])
def test_single_trailing_closer_has_exact_audit_receipt(raw):
    candidate, receipt = normalize_response(raw)
    offset = len(raw.rstrip(" \t\r\n")) - 1
    assert candidate == raw[:offset] + raw[offset + 1:]
    assert len(candidate) == len(raw) - 1
    assert isinstance(json.loads(candidate), dict)
    assert receipt == {
        "version": "skillflow-json-normalization-v1",
        "rule": "trailing_single_object_closer",
        "raw_sha256": canonical_sha256(raw),
        "normalized_sha256": canonical_sha256(candidate),
        "removed_offset": offset,
        "removed_character": "}",
    }
    assert normalize_response(candidate) == (candidate, None)


def test_unicode_offsets_and_original_crlf_are_preserved():
    raw = '\r\n{\r\n  "text": "中文😀",\r\n  "n": 1\r\n}\r\n}\t\r\n'
    candidate, receipt = normalize_response(raw)
    assert receipt is not None
    offset = raw.rindex("}")
    assert receipt["removed_offset"] == offset
    assert offset != len(raw[:offset].encode("utf-8"))
    assert candidate == raw[:offset] + raw[offset + 1:]
    assert candidate.count("\r\n") == raw.count("\r\n")


@pytest.mark.parametrize("raw", [
    "", " \t\r\n", "{", '{"a":', '{"a":"unfinished}',
    '{"a": 1,}}', '{"a":1 "b":2}}', "{'a':1}}",
    "{}}}", "{} } }", "{}]", "{} } trailing", "{} text }",
    "{}{}", "{}{} }", "{} [] }", "```json\n{}\n```}",
    "prefix {}}", '\ufeff{}}', '\u00a0{}}', '{}\u00a0}',
    '{} }\u00a0', '{}\v}', '{}\f}', '{}\u2028}',
    "[]}", "null}", "true}", "1}", '"{}"}',
    '{"a":1,"a":2}}', '{"a":1,"\\u0061":2}}',
    '{"nested":[{"a":1,"a":2}]}}',
    '{"a":NaN}}', '{"a":Infinity}}', '{"a":-Infinity}}',
    '{"a":1e999}}', '{"a":-1e999}}', '{"nested":[{"a":1e999}]}}',
    '{"a":"unescaped\nnewline"}}',
])
def test_ambiguous_invalid_or_out_of_scope_text_is_not_repaired(raw):
    candidate, receipt = normalize_response(raw)
    assert candidate is raw
    assert receipt is None


@pytest.mark.parametrize("raw", [{"ok": True}, {"n": float("inf")}, [], None, 1, b"{}}"])
def test_non_text_input_is_unchanged_for_existing_validation(raw):
    candidate, receipt = normalize_response(raw)
    assert candidate is raw
    assert receipt is None


def test_over_limit_integer_does_not_trigger_format_repair():
    import sys

    limit = sys.get_int_max_str_digits()
    if limit == 0:
        pytest.skip("interpreter has no integer decoding digit limit")
    raw = '{"n":' + "1" * (limit + 1) + "}}"
    assert normalize_response(raw) == (raw, None)


def test_normalization_is_not_schema_acceptance():
    raw = '{"made_up_field":true}}'
    candidate, receipt = normalize_response(raw)
    assert candidate == '{"made_up_field":true}'
    assert receipt is not None
    # No business fields are inferred, removed, or corrected by this module.
    assert json.loads(candidate) == {"made_up_field": True}


def test_unexpected_implementation_failure_is_not_hidden(monkeypatch):
    class BrokenDecoder:
        def raw_decode(self, *args):
            raise RuntimeError("decoder implementation failure")

    monkeypatch.setattr(normalizer, "_decoder", BrokenDecoder)
    with pytest.raises(RuntimeError, match="decoder implementation failure"):
        normalize_response("{}}")


def test_depth_limit_is_not_disguised_as_a_format_correction(monkeypatch):
    class LimitedDecoder:
        def raw_decode(self, *args):
            raise RecursionError("decoder capacity exceeded")

    monkeypatch.setattr(normalizer, "_decoder", LimitedDecoder)
    with pytest.raises(RecursionError, match="decoder capacity exceeded"):
        normalize_response("{}}")
