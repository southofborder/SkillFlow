"""Response normalizers — faithful port of shared/llm-utils.cjs pure functions.

Each function mirrors the JS behavior exactly (fallbacks, clamps, keyword maps,
rounding). The golden oracle replays cached LLM responses through both engines,
so any divergence here would surface as a DOE verdict flip — keep these locked
to the JS spec. Cross-checked against llm-utils.cjs lines 7-155.
"""

from __future__ import annotations

import json
import math
import re
from typing import Any


def js_round(value: float) -> int:
    """Match JS Math.round: round half toward +infinity (not banker's rounding).

    Python's built-in round() uses round-half-to-even, which diverges from JS on
    exact .5 boundaries (e.g. round(62.5)==62 but Math.round(62.5)==63). This
    port must match JS since normalizer outputs are compared against the JS
    engine's cached-response results.
    """
    return math.floor(value + 0.5)


def normalize_assistant_content(content: Any) -> str:
    """Port of normalizeAssistantContent (llm-utils.cjs:7-23)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
            elif isinstance(part, dict) and isinstance(part.get("content"), str):
                parts.append(part["content"])
            else:
                parts.append("")
        return "\n".join(parts)
    if isinstance(content, dict):
        # JS: JSON.stringify(content) — compact, no spaces.
        return json.dumps(content, separators=(",", ":"), ensure_ascii=False)
    return ""


_FENCED_RE = re.compile(r"```json\s*([\s\S]*?)```", re.IGNORECASE)
_OBJECT_RE = re.compile(r"\{[\s\S]*\}")


def parse_loose_json(raw: Any) -> Any:
    """Port of parseLooseJson (llm-utils.cjs:25-44).

    Returns a dict/list on success, or None. Mirrors the JS candidate order:
    whole text -> fenced ```json block -> first {...} object-like slice.
    """
    if isinstance(raw, dict):
        return raw
    text = normalize_assistant_content(raw).strip()
    if not text:
        return None

    candidates = [text]
    fenced = _FENCED_RE.search(text)
    if fenced:
        candidates.append(fenced.group(1).strip())
    object_like = _OBJECT_RE.search(text)
    if object_like:
        candidates.append(object_like.group(0))

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except (ValueError, TypeError):
            continue
    return None


_TRUE_TOKENS = {"true", "yes", "y", "1", "agree", "agrees"}
_FALSE_TOKENS = {"false", "no", "n", "0", "disagree", "disagrees"}


def normalize_boolean(value: Any, fallback: bool = False) -> bool:
    """Port of normalizeBoolean (llm-utils.cjs:46-56)."""
    if isinstance(value, bool):
        return value
    # Note: JS treats numbers before stringifying; 1->True, 0->False.
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False
    text = str(value if value is not None else "").strip().lower()
    if text in _TRUE_TOKENS:
        return True
    if text in _FALSE_TOKENS:
        return False
    return fallback


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _round6(value: Any) -> float:
    """Port of round6 (llm-utils.cjs:153-155): round to 6 decimals (JS Math.round)."""
    return js_round(float(value or 0) * 1_000_000) / 1_000_000


def normalize_scaled_number(value: Any, *, fallback: float = 0.0,
                            min: float = 0.0, max: float = 1.0,
                            map: dict | None = None) -> float:
    """Port of normalizeScaledNumber (llm-utils.cjs:58-81)."""
    map = map or {}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        # Number.isFinite equivalent.
        if value == value and value not in (float("inf"), float("-inf")):
            return _clamp(float(value), min, max)

    text = str(value if value is not None else "").strip().lower()
    if not text:
        return fallback

    if text in map:
        return _clamp(float(map[text]), min, max)

    try:
        numeric = float(text)
        if numeric == numeric and numeric not in (float("inf"), float("-inf")):
            return _clamp(numeric, min, max)
    except (ValueError, TypeError):
        pass

    return fallback


_SEVERITY = {
    "critical": {"critical", "crit", "severe"},
    "high": {"high", "major"},
    "medium": {"medium", "med", "moderate"},
    "low": {"low", "minor"},
}


def normalize_severity(value: Any) -> str:
    """Port of normalizeSeverity (llm-utils.cjs:83-91)."""
    text = str(value if value is not None else "").strip().lower()
    if not text:
        return ""
    for canonical, aliases in _SEVERITY.items():
        if text in aliases:
            return canonical
    return ""


def normalize_similarity_result(raw: Any) -> dict | None:
    """Port of normalizeSimilarityResult (llm-utils.cjs:93-117)."""
    parsed = parse_loose_json(raw)
    if not isinstance(parsed, dict):
        return None
    value = _first(parsed, "similarity", "score", "similarity_score")
    return {
        "similarity": _round6(normalize_scaled_number(
            value, fallback=0, map={
                "identical": 1,
                "very_high": 0.9,
                "very high": 0.9,
                "high": 0.8,
                "medium": 0.5,
                "low": 0.2,
                "none": 0,
            })),
        "reason": str(_first(parsed, "reason", "explanation") or "").strip(),
        "has_contradiction": normalize_boolean(parsed.get("has_contradiction"), False),
        "contradiction_reason": str(parsed.get("contradiction_reason") or "").strip(),
    }


def normalize_validation_result(raw: Any) -> dict | None:
    """Port of normalizeValidationResult (llm-utils.cjs:119-132)."""
    parsed = parse_loose_json(raw)
    if not isinstance(parsed, dict):
        return None
    return {
        "is_compatible": normalize_boolean(parsed.get("is_compatible"), False),
        "confidence": normalize_scaled_number(
            parsed.get("confidence"), fallback=0.5,
            map={"high": 0.85, "medium": 0.6, "low": 0.3}),
        "reason": str(parsed.get("reason") or "").strip() or "LLM semantic validation",
        "data_flow_description": str(parsed.get("data_flow_description") or "").strip()
        or "Data flows from source to target",
    }


def normalize_review_result(raw: Any) -> dict | None:
    """Port of normalizeReviewResult (llm-utils.cjs:134-147)."""
    parsed = parse_loose_json(raw)
    if not isinstance(parsed, dict):
        return None
    return {
        "agrees": normalize_boolean(parsed.get("agrees"), False),
        "confidence": normalize_scaled_number(
            parsed.get("confidence"), fallback=0,
            map={"high": 0.85, "medium": 0.6, "low": 0.3}),
        "reason": str(parsed.get("reason") or "").strip(),
        "suggested_severity": normalize_severity(parsed.get("suggested_severity")),
    }


def _first(obj: dict, *keys: str) -> Any:
    """JS `a ?? b ?? c` over dict keys: first value that is not None/absent."""
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return None
