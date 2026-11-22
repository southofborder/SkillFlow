"""Lossless input presentation for complete processing requests and corrections.

Only program-constructed inputs enter this encoder. Model answers retain their
separate strict response codec and validators. Source is never passed through
this module: the prompt's complete related-source suffix remains unchanged.
"""
from __future__ import annotations

import hashlib
import json

from skillflow.common.prompt_format import compact_json
from skillflow.common.source_evidence import _json_object
from skillflow.common.structural_correction import correction_base_prompt
from .review_display import (
    DISPLAY_IDENTITY, _shared_values, expand_review_payload, pack_review_payload,
)


IDENTITY = "skillflow-processing-input-display-v1"
INPUT_MARKER = "\nPROCESSING_INPUT_JSON\n"
SUFFIX_MARKER = "\n\nGLOBAL REQUIREMENTS AND LIMITATIONS\n"
_FIELDS = {"format", "logical_sha256", "display"}
_MARKERS = {"$ref", "$rows", "$literal_object"}


def _digest(value):
    return hashlib.sha256(compact_json(value).encode("utf-8")).hexdigest()


def _table_display(payload):
    """Apply the existing exact column grammar to any repeated record array."""
    columns, shapes = [], {}

    def encode(value):
        if isinstance(value, list):
            if len(value) > 1 and all(isinstance(row, dict) for row in value):
                rows = []
                for record in value:
                    shape = tuple(record)
                    if shape not in shapes:
                        shapes[shape] = len(columns)
                        columns.append(list(shape))
                    rows.append([shapes[shape], *[encode(item) for item in record.values()]])
                return {"$rows": rows}
            return [encode(item) for item in value]
        if isinstance(value, dict):
            if _MARKERS.intersection(value):
                return {"$literal_object": [[key, encode(item)] for key, item in value.items()]}
            return {key: encode(item) for key, item in value.items()}
        return value

    prepared = encode(payload)
    shared, definitions = _shared_values(prepared)
    options = [{"format": DISPLAY_IDENTITY, "record_columns": columns,
                "shared_values": values, "payload": value}
               for value, values in ((prepared, {}), (shared, definitions))]
    return min(options, key=lambda value: len(compact_json(value)))


def pack_display_material(payload, *, identity):
    """Pack a logical input with the existing exact shared-value codec."""
    display = min((pack_review_payload(payload), _table_display(payload)),
                  key=lambda value: len(compact_json(value)))
    if compact_json(expand_review_payload(display)) != compact_json(payload):
        raise ValueError("Shared input display changed its complete logical payload")
    return {"format": identity, "logical_sha256": _digest(payload), "display": display}


def expand_display_material(envelope, *, identity):
    if (not isinstance(envelope, dict) or set(envelope) != _FIELDS
            or envelope["format"] != identity):
        raise ValueError("Unsupported shared input display envelope")
    value = expand_review_payload(envelope["display"])
    if envelope["logical_sha256"] != _digest(value):
        raise ValueError("Shared input display logical identity differs")
    return value


def pack_processing_material(payload):
    """Pack every logical input and fail closed if exact expansion differs."""
    return pack_display_material(payload, identity=IDENTITY)


def expand_processing_material(envelope):
    return expand_display_material(envelope, identity=IDENTITY)


def processing_display_instructions():
    return (
        "LOSSLESS PROCESSING INPUT\n"
        "PROCESSING_INPUT_JSON contains the complete logical inputs in one exact shared presentation. "
        "Its format is skillflow-processing-input-display-v1; logical_sha256 binds the expanded input. "
        "Within display, payload contains documents, cfg, runtime_contract and any repair_context or correction. "
        "An object containing only $ref names the exact JSON value in display.shared_values, recursively. "
        "An object containing only $rows is an ordered record array: each row starts with a zero-based "
        "display.record_columns index, then one value per field in that exact order. Distinct columns preserve "
        "absent fields versus explicit null. An object containing only $literal_object forms the literal object "
        "from ordered [key,value] pairs; resulting marker-like keys are ordinary data. Every occurrence remains "
        "independent: shared text never merges operations, inputs, conditions, members, contracts or evidence. "
        "Read the fully expanded logical inputs before interpreting semantics. CFG/record/diagnostic pointers "
        "refer to logical cfg or the candidate, never to table indexes, shared definitions or this envelope. "
        "All source text follows separately as RELATED SOURCE, unchanged. The response uses the separately "
        "specified fragment format, not this input envelope.\n"
    )


def render_processing_material(payload):
    return processing_display_instructions() + INPUT_MARKER + compact_json(pack_processing_material(payload))


def _parts(prompt):
    """Parse only the renderer's boundary before the complete source suffix."""
    try:
        start = prompt.index(INPUT_MARKER) + len(INPUT_MARKER)
        prefix = prompt[:start - len(INPUT_MARKER)]
        if "LOSSLESS PROCESSING INPUT\n" not in prefix:
            return None
        _, length = json.JSONDecoder().raw_decode(prompt[start:])
        envelope = _json_object(prompt[start:start + length])
        suffix = prompt[start + length:]
        if not suffix.startswith(SUFFIX_MARKER):
            return None
        payload = expand_processing_material(envelope)
        if (not isinstance(payload, dict) or not {"documents", "cfg", "runtime_contract"} <= payload.keys()
                or not isinstance(payload["documents"], dict) or set(payload["documents"]) != {"flow"}):
            return None
        return prefix, payload, suffix
    except (ValueError, TypeError, RecursionError):
        return None


def compact_processing_correction(base_prompt, fallback, context):
    """Share the complete old input, candidate and errors in the existing call.

    Unrecognized/custom prompts keep the complete caller-provided fallback.
    All response instructions and the entire source/output-schema suffix survive.
    No selected correction record or diagnostic is inferred, removed or merged.
    """
    base = correction_base_prompt(base_prompt)
    parts = _parts(base)
    serialized = compact_json(context)
    if (parts is None or not fallback.startswith(base) or not fallback.endswith(serialized)
            or len(fallback) < len(base) + len(serialized)):
        return fallback
    prefix, payload, suffix = parts
    if "correction" in payload:
        return fallback
    instructions = fallback[len(base):len(fallback) - len(serialized)]
    logical = {**payload, "correction": context}
    notice = (
        "\nJOINT PROCESSING CORRECTION MATERIAL\n"
        "The single PROCESSING_INPUT_JSON retains every original logical input and adds correction, "
        "including the complete candidate or explicitly selected records and every displayed diagnostic. "
        "Original CFG pointers and candidate record paths keep their logical meaning. Apply the correction "
        "response instructions above; source and original output instructions remain below unchanged.\n"
    )
    candidate = (prefix + instructions + notice + INPUT_MARKER
                 + compact_json(pack_processing_material(logical)) + suffix)
    return min((fallback, candidate), key=len)
