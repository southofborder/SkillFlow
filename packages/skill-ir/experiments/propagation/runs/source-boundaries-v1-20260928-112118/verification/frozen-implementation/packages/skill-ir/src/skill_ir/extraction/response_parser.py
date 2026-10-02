"""Parse candidate JSON returned by the model."""

from __future__ import annotations

import json
import re
from typing import Any


_FENCED_JSON = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def response_text(raw: Any) -> str:
    if isinstance(raw, str):
        return raw
    try:
        return json.dumps(raw, ensure_ascii=False)
    except TypeError:
        return str(raw)


def _json_candidates(raw: Any) -> list[Any]:
    if isinstance(raw, dict):
        return [raw]
    text = response_text(raw).strip()
    if not text:
        return []

    candidates: list[str] = [text]
    candidates.extend(match.group(1).strip() for match in _FENCED_JSON.finditer(text))
    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character != "{":
            continue
        try:
            _, end = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        candidates.append(text[index : index + end])
    parsed: list[Any] = []
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value not in parsed:
            parsed.append(value)
    return parsed


def parse_candidate_response(raw: Any) -> dict[str, Any] | None:
    """Parse a strict candidate object with small Markdown-tolerant fallbacks."""

    candidates = _json_candidates(raw)
    return candidates[0] if candidates else None
