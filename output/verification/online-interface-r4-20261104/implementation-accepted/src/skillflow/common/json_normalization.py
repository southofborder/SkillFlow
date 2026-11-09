"""Auditable, deliberately narrow normalization of completed model responses.

This module makes no transport or schema acceptance decision. It removes only
one superfluous object closer following an otherwise complete strict JSON
object. Callers must still validate the candidate and retain the raw response.
"""

from __future__ import annotations

import json
import math
from typing import Any

from skillflow.common.recording import canonical_sha256


NORMALIZATION_VERSION = "skillflow-json-normalization-v1"
TRAILING_CLOSER_RULE = "trailing_single_object_closer"
_JSON_WHITESPACE = " \t\r\n"


class _NotStrictJSON(ValueError):
    """A decoder callback rejected a non-JSON or ambiguous value."""


def _unique_members(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise _NotStrictJSON("duplicate JSON member")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise _NotStrictJSON("non-JSON numeric constant")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise _NotStrictJSON("non-finite JSON number")
    return number


def _integer(value: str) -> int:
    try:
        return int(value)
    except ValueError as error:
        # Python's integer digit limit is an input limitation, not permission to
        # alter a number. Other decoder/implementation failures are not caught.
        raise _NotStrictJSON("JSON integer exceeds the decoder limit") from error


def _decoder() -> json.JSONDecoder:
    return json.JSONDecoder(
        object_pairs_hook=_unique_members,
        parse_constant=_reject_constant,
        parse_float=_finite_float,
        parse_int=_integer,
    )


def _after_whitespace(text: str, offset: int) -> int:
    while offset < len(text) and text[offset] in _JSON_WHITESPACE:
        offset += 1
    return offset


def normalize_response(raw: Any) -> tuple[Any, dict[str, Any] | None]:
    """Return the unchanged response or a one-character deletion and receipt.

    Dictionary injection remains untouched. Text must begin with one complete
    object (apart from JSON whitespace), contain unique keys and finite JSON
    numbers, and have exactly one ``}`` after it, surrounded only by JSON
    whitespace. The receipt uses Unicode code-point offsets and canonical
    digests of the raw and normalized *strings*, not parsed objects.

    Ineligible text is returned unchanged so the existing validation/correction
    path diagnoses it. This function must only be called after a completed,
    non-truncated response has been established by the caller.
    """
    if not isinstance(raw, str):
        return raw, None

    decoder = _decoder()
    try:
        value, end = decoder.raw_decode(raw, _after_whitespace(raw, 0))
    except (json.JSONDecodeError, _NotStrictJSON):
        return raw, None
    if not isinstance(value, dict):
        return raw, None

    offset = _after_whitespace(raw, end)
    if (offset == len(raw) or raw[offset] != "}"
            or _after_whitespace(raw, offset + 1) != len(raw)):
        return raw, None

    candidate = raw[:offset] + raw[offset + 1:]
    try:
        # A full decode checks that no content was discarded beyond the single
        # recorded character. It also repeats the same strict member/number rules.
        normalized = decoder.decode(candidate)
    except (json.JSONDecodeError, _NotStrictJSON):
        return raw, None
    if not isinstance(normalized, dict):
        return raw, None

    return candidate, {
        "version": NORMALIZATION_VERSION,
        "rule": TRAILING_CLOSER_RULE,
        "raw_sha256": canonical_sha256(raw),
        "normalized_sha256": canonical_sha256(candidate),
        "removed_offset": offset,
        "removed_character": "}",
    }
