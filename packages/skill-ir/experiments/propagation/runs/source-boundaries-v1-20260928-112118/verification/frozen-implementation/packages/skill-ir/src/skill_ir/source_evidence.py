"""Shared source contracts, location indexes, and strict evidence parsing.

This module interprets no Skill requirement or graph semantics. All quotes are
checked against the original decoded content; digest identities retain order.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


Text = Annotated[str, StringConstraints(min_length=1, pattern=r"\S")]
Digest = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SourceFile(StrictRecord):
    path: Text
    content: str
    sha256: Digest


class SourceBundle(StrictRecord):
    files: list[SourceFile] = Field(min_length=1)
    source_sha256: Digest


class SourceRef(StrictRecord):
    unit_id: Text
    file: Text
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    quote: Text

    @model_validator(mode="after")
    def ordered_lines(self) -> "SourceRef":
        if self.end_line < self.start_line:
            raise ValueError("source reference end_line precedes start_line")
        return self


class ResponseValidationError(ValueError):
    """The response cannot be accepted as a completed review record."""


def _fail(message: str) -> None:
    raise ResponseValidationError(message)


def _unique(values: list[str], label: str) -> set[str]:
    result = set(values)
    if len(result) != len(values):
        _fail(f"{label}: duplicate identifiers/references")
    return result


def _exact(values: list[str], expected: set[str], label: str) -> None:
    actual = _unique(values, label)
    if actual != expected:
        _fail(f"{label}: missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}")


def _json_object(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        raw = json.dumps(raw, ensure_ascii=False, allow_nan=False)
    if not isinstance(raw, str):
        _fail("response must be a JSON object or JSON text")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                _fail(f"duplicate JSON member: {key}")
            result[key] = value
        return result

    def constant(value: str) -> None:
        _fail(f"non-JSON constant: {value}")

    try:
        parsed = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (json.JSONDecodeError, TypeError) as error:
        raise ResponseValidationError(f"invalid JSON response: {error}") from error
    if not isinstance(parsed, dict):
        _fail("response JSON root must be an object")
    return parsed


def _checked_source(source: dict[str, Any]) -> dict[str, Any]:
    parsed = SourceBundle.model_validate(source).model_dump(mode="json")
    _unique([entry["path"] for entry in parsed["files"]], "source file paths")
    for item in parsed["files"]:
        if hashlib.sha256(item["content"].encode("utf-8")).hexdigest() != item["sha256"]:
            _fail(f"source file digest mismatch: {item['path']}")
    identities = [{key: item[key] for key in ("path", "sha256")} for item in parsed["files"]]
    if _digest(identities) != parsed["source_sha256"]:
        _fail("source bundle digest mismatch")
    return parsed


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validate_source_ref(ref: dict[str, Any], paragraphs: dict[str, dict[str, Any]]) -> None:
    unit = paragraphs.get(ref["unit_id"])
    if unit is None:
        _fail(f"source unit does not exist: {ref['unit_id']}")
    if ref["file"] != unit["file"]:
        _fail(f"source reference file does not match unit: {ref['unit_id']}")
    if ref["start_line"] < unit["start_line"] or ref["end_line"] > unit["end_line"]:
        _fail(f"source reference lines are outside unit: {ref['unit_id']}")
    lines = unit["text"].splitlines()
    a, b = ref["start_line"] - unit["start_line"], ref["end_line"] - unit["start_line"] + 1
    quote = ref["quote"].replace("\r\n", "\n").replace("\r", "\n")
    if quote not in "\n".join(lines[a:b]):
        _fail(f"source quote does not match specified lines: {ref['unit_id']}")


def source_units(source: dict[str, Any]) -> list[dict[str, Any]]:
    """Index blank-line separated paragraphs, preserving fenced-code blocks.

All original files remain in the prompt. This is only a location index: it does
not identify which paragraphs are requirements or what their semantics are.
"""
    units: list[dict[str, Any]] = []
    for entry in source["files"]:
        lines = entry["content"].splitlines()
        start: int | None = None
        fence: str | None = None
        for number, line in enumerate(lines, 1):
            stripped = line.lstrip()
            marker = re.match(r"(`{3,}|~{3,})", stripped)
            if start is None and line.strip():
                start = number
            if marker:
                value = marker.group(1)
                if fence is None:
                    fence = value
                elif value[0] == fence[0] and len(value) >= len(fence):
                    fence = None
            if not line.strip() and fence is None and start is not None:
                units.append({"id": f"src_{len(units) + 1:03d}", "file": entry["path"],
                              "start_line": start, "end_line": number - 1,
                              "text": "\n".join(lines[start - 1:number - 1])})
                start = None
        if start is not None:
            units.append({"id": f"src_{len(units) + 1:03d}", "file": entry["path"],
                          "start_line": start, "end_line": len(lines),
                          "text": "\n".join(lines[start - 1:])})
    return units


