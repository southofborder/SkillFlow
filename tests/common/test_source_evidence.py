"""Shared evidence contracts retain the original audit and snapshot behavior."""

from copy import deepcopy
import hashlib
import json

import pytest
from pydantic import ValidationError

from skillflow.common import source_evidence as shared


def source(content="首段\r\n\r\n```text\r\n甲\r\n\r\n乙\r\n```\r\n"):
    files = [{"path": "SKILL.md", "content": content,
              "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}]
    return {"files": files, "source_sha256": shared._digest(
        [{key: item[key] for key in ("path", "sha256")} for item in files])}


def test_audit_uses_shared_evidence_contracts_and_validation():
    from skillflow.graph.audit import models
    from skillflow.graph.audit import prompts
    from skillflow.graph.audit import services

    assert issubclass(models.Finding, shared.StrictRecord)
    assert models.Finding.model_fields["source_refs"].annotation == list[shared.SourceRef]
    for name in ("_fail", "_unique", "_exact", "_json_object",
                 "_checked_source", "_digest", "_validate_source_ref"):
        assert getattr(services, name) is getattr(shared, name)
    assert prompts.source_units is shared.source_units
    with pytest.raises(shared.ResponseValidationError):
        services._json_object('{"duplicate": 1, "duplicate": 2}')


def test_feedback_uses_shared_snapshot_implementation_directly():
    from skillflow.graph.feedback import runner
    from skillflow.common.inputs import snapshot as current

    for name in ("freeze_input", "read_snapshot", "verify_original_input"):
        assert getattr(runner, name) is getattr(current, name)


def test_canonical_digest_retains_snapshot_identity():
    from skillflow.graph.audit.evidence import canonical_graph_sha256

    values = [{"文": [None, {}, [], "引号\"\\\n", True, 1, 1.5]}, [],
              [{"path": "SKILL.md", "size": 4, "raw_sha256": "a" * 64}]]
    for value in values:
        assert shared._digest(value) == canonical_graph_sha256(value)


def test_frozen_source_is_validated_without_mutating_content():
    original = source()
    before = deepcopy(original)
    assert shared._checked_source(original) == before
    assert original == before
    units = shared.source_units(original)
    assert [(u["start_line"], u["end_line"]) for u in units] == [(1, 1), (3, 7)]
    assert units[1]["text"] == "```text\n甲\n\n乙\n```"
    assert original["files"][0]["content"].count("\r\n") == 7


@pytest.mark.parametrize("tamper", ["file_digest", "bundle_digest", "duplicate_file"])
def test_source_integrity_errors_are_shared_validation_errors(tamper):
    value = source()
    if tamper == "file_digest":
        value["files"][0]["content"] += "被改动"
    elif tamper == "bundle_digest":
        value["source_sha256"] = "0" * 64
    else:
        value["files"].append(deepcopy(value["files"][0]))
    with pytest.raises(shared.ResponseValidationError):
        shared._checked_source(value)


@pytest.mark.parametrize("raw", ['{"x": 1, "x": 2}', '{"nested": {"a": 1, "a": 2}}',
                                  '{"value": NaN}', '{"value": Infinity}', '[]',
                                  '```json\n{}\n```', '{} trailing'])
def test_strict_json_rejects_ambiguous_or_non_json_responses(raw):
    with pytest.raises(shared.ResponseValidationError):
        shared._json_object(raw)


def test_quote_validation_uses_exact_file_lines_and_normalized_newlines():
    units = {unit["id"]: unit for unit in shared.source_units(source())}
    valid = {"unit_id": "src_002", "file": "SKILL.md", "start_line": 4,
             "end_line": 6, "quote": "甲\r\n\r\n乙"}
    shared._validate_source_ref(valid, units)
    for key, value in (("quote", "丙"), ("file", "other.md"), ("start_line", 2),
                       ("end_line", 8), ("unit_id", "missing")):
        invalid = {**valid, key: value}
        with pytest.raises(shared.ResponseValidationError):
            shared._validate_source_ref(invalid, units)


def test_source_contracts_remain_strict_and_preserve_order():
    parsed = shared.SourceBundle.model_validate(source())
    assert shared._checked_source(json.loads(parsed.model_dump_json())) == source()
    with pytest.raises(ValidationError):
        shared.SourceBundle.model_validate({**source(), "oracle": "do not accept"})
    with pytest.raises(ValidationError):
        shared.SourceRef.model_validate({"unit_id": "src_001", "file": "SKILL.md",
                                         "start_line": 3, "end_line": 1, "quote": "甲"})
