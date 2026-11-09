"""Shared source contracts, location indexes, and strict evidence parsing.

This module interprets no Skill requirement or graph semantics. All quotes are
checked against the original decoded content; digest identities retain order.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
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
    file: Text
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

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


def json_pointer(*parts: str | int) -> str:
    """Encode locations with RFC 6901 escaping, including unusual block keys."""
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _require_json(value: Any, path: str, active: set[int] | None = None) -> None:
    """Reject non-JSON Any payloads before Pydantic can serialize them away."""
    active = set() if active is None else active
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"Non-JSON value at {path}: non-finite float")
        return
    if type(value) not in (dict, list):
        raise ValueError(f"Non-JSON value at {path}: {type(value).__name__}")
    if id(value) in active:
        raise ValueError(f"Non-JSON value at {path}: cyclic container")
    active.add(id(value))
    try:
        items = value.items() if type(value) is dict else enumerate(value)
        for key, item in items:
            if type(value) is dict and type(key) is not str:
                raise ValueError(f"Non-JSON object key at {path}: {type(key).__name__}")
            child = path + json_pointer(key)
            _require_json(item, child, active)
    finally:
        active.remove(id(value))


def canonical_graph_sha256(graph: dict[str, Any]) -> str:
    """Sort object keys, retain every list occurrence and its recorded order."""
    _require_json(graph, "")
    try:
        encoded = json.dumps(
            graph, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as error:
        raise ValueError(f"CFG cannot be represented as canonical UTF-8 JSON: {error}") from error
    return hashlib.sha256(encoded).hexdigest()



def resolve_pointer(document: Any, pointer: str) -> Any:
    """Strict RFC 6901 lookup for program-generated evidence positions."""
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("Invalid JSON pointer")
    current = document
    for encoded in pointer[1:].split("/"):
        index = 0
        while index < len(encoded):
            if encoded[index] == "~":
                if index + 1 >= len(encoded) or encoded[index + 1] not in "01":
                    raise ValueError("Invalid JSON pointer escape")
                index += 2
            else:
                index += 1
        part = encoded.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(current, list):
                if not part.isascii() or not part.isdigit() or (len(part) > 1 and part[0] == "0"):
                    raise ValueError("Invalid JSON pointer array index")
                current = current[int(part)]
            elif isinstance(current, dict):
                current = current[part]
            else:
                raise ValueError("JSON pointer traverses a scalar")
        except (IndexError, KeyError) as error:
            raise ValueError("JSON pointer does not exist") from error
    return current


def source_lines(text: str) -> list[str]:
    """Return source lines with original endings, using Python's splitlines boundary.

    This is a physical-text index, not sentence or requirement segmentation.
    A final newline terminates its line without introducing an extra empty line.
    """
    if type(text) is not str:
        raise ValueError("source text must be a string")
    return text.splitlines(keepends=True)


def extract_source_lines(text: str, start_line: int, end_line: int) -> str:
    """Extract an inclusive one-based span without normalizing its text or endings."""
    lines = source_lines(text)
    if (type(start_line) is not int or type(end_line) is not int
            or start_line < 1 or end_line < start_line or end_line > len(lines)):
        raise ValueError("source line range must be inclusive, one-based, and within the file")
    return "".join(lines[start_line - 1:end_line])


def validate_source_ref(ref: dict[str, Any], files: Mapping[str, str]) -> SourceRef:
    """Validate a file and inclusive physical-line range, without semantic claims.

    Ranges may span blank lines and paragraph boundaries. The same line
    definition is used for model input, evidence extraction and coverage.
    """
    parsed = SourceRef.model_validate(ref)
    if parsed.file not in files:
        _fail(f"source reference file does not exist: {parsed.file}")
    try:
        extract_source_lines(files[parsed.file], parsed.start_line, parsed.end_line)
    except ValueError as error:
        _fail(f"invalid source reference {parsed.file}:{parsed.start_line}-{parsed.end_line}: {error}")
    return parsed


def nonempty_source_lines(files: Mapping[str, str]) -> set[tuple[str, int]]:
    """Return physical locations requiring coverage; no paragraph IDs are created."""
    return {(path, number) for path, text in files.items()
            for number, line in enumerate(source_lines(text), 1) if line.strip()}
