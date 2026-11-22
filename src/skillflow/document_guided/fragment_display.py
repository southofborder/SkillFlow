"""Exact shared inputs for downstream fragments and finite revision scopes."""
from __future__ import annotations

import json

from skillflow.common.prompt_format import compact_json
from skillflow.common.source_evidence import _json_object
from skillflow.common.structural_correction import correction_base_prompt
from .processing_display import (
    SUFFIX_MARKER, expand_display_material, pack_display_material,
)


IDENTITY = "skillflow-fragment-input-display-v1"
INPUT_MARKER = "\nFRAGMENT_INPUT_JSON\n"
_OWNERS = {"processing", "task-correspondence", "sensitivity", "cfg"}


def pack_fragment_material(payload):
    if not isinstance(payload, dict) or payload.get("owner") not in _OWNERS:
        raise ValueError("Fragment display requires an existing semantic owner")
    return pack_display_material(payload, identity=IDENTITY)


def expand_fragment_material(envelope):
    payload = expand_display_material(envelope, identity=IDENTITY)
    if not isinstance(payload, dict) or payload.get("owner") not in _OWNERS:
        raise ValueError("Fragment display requires an existing semantic owner")
    return payload


def fragment_display_instructions():
    return (
        "LOSSLESS FRAGMENT INPUT\n"
        "FRAGMENT_INPUT_JSON is the complete previous-work input for its owner. Its format is "
        "skillflow-fragment-input-display-v1 and logical_sha256 binds the exact expanded payload. "
        "An object containing only $ref names one exact JSON value in display.shared_values, recursively. "
        "An object containing only $rows is an ordered record array: each row begins with a zero-based "
        "display.record_columns index, then gives values in that column order. Distinct columns preserve "
        "missing fields and explicit null. An object containing only $literal_object forms an ordinary "
        "literal object from its ordered [key,value] pairs, including any marker-like keys. "
        "Read the complete expansion before interpreting documents, cfg, task, expression_references, "
        "scope, repair_context or correction when supplied. Shared text preserves independent operations, "
        "versions, inputs, conditions, members, evidence occurrences and receiver pairing. Every target "
        "and JSON pointer refers to the expanded logical objects, never the display tables or indexes. "
        "The separately specified output schema governs your response. The complete RELATED SOURCE "
        "section follows separately.\n"
    )


def render_fragment_material(owner, material):
    if not isinstance(material, dict) or "owner" in material:
        raise ValueError("Fragment material must have one program-owned owner")
    return (fragment_display_instructions() + INPUT_MARKER
            + compact_json(pack_fragment_material({"owner": owner, **material})))


def fragment_prompt_parts(prompt):
    """Recognize only the renderer's exact boundary before the source suffix."""
    try:
        start = prompt.index(INPUT_MARKER) + len(INPUT_MARKER)
        prefix = prompt[:start - len(INPUT_MARKER)]
        if fragment_display_instructions() not in prefix or SUFFIX_MARKER in prefix:
            return None
        _, length = json.JSONDecoder().raw_decode(prompt[start:])
        envelope = _json_object(prompt[start:start + length])
        suffix = prompt[start + length:]
        if not suffix.startswith(SUFFIX_MARKER):
            return None
        return prefix, expand_fragment_material(envelope), suffix
    except (ValueError, TypeError, RecursionError):
        return None


def compact_fragment_correction(base_prompt, fallback, context):
    """Share the exact base inputs and all finite or whole correction material."""
    base = correction_base_prompt(base_prompt)
    parts = fragment_prompt_parts(base)
    serialized = compact_json(context)
    if (parts is None or not fallback.startswith(base) or not fallback.endswith(serialized)
            or len(fallback) < len(base) + len(serialized)):
        return fallback
    prefix, payload, suffix = parts
    if "correction" in payload:
        return fallback
    instructions = fallback[len(base):len(fallback) - len(serialized)]
    notice = (
        "\nJOINT FRAGMENT CORRECTION MATERIAL\n"
        "The single FRAGMENT_INPUT_JSON retains every original logical input and adds correction. "
        "It includes the entire candidate or all selected records and every displayed diagnostic. "
        "Original record identities and logical pointers retain their meaning. Follow the correction "
        "response instructions above and the original source and output contract below.\n"
    )
    candidate = (prefix + instructions + notice + INPUT_MARKER
                 + compact_json(pack_fragment_material({**payload, "correction": context})) + suffix)
    return min((fallback, candidate), key=len)
