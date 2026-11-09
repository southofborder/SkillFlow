"""Canonical paths shared by annotation, compilation and deterministic analysis."""
from __future__ import annotations

from skillflow.common.source_evidence import json_pointer

ROOT = "ir_semantics"


def semantics_path(instruction_id, *parts):
    if type(instruction_id) is not str or not instruction_id:
        raise ValueError("semantic path requires an actual instruction ID")
    if any(not (type(part) is str or type(part) is int and part >= 0) for part in parts):
        raise ValueError("semantic path has an invalid component")
    return [ROOT, instruction_id, *parts]


def semantics_pointer(instruction_id, *parts):
    return json_pointer(*semantics_path(instruction_id, *parts))


def split_semantics_path(path):
    if not isinstance(path, (list, tuple)) or len(path) < 2 or path[0] != ROOT:
        raise ValueError("path is not inside IR semantics")
    canonical = semantics_path(path[1], *path[2:])
    return canonical[1], canonical[2:]


def processing_segment_path(path):
    """Locate a raw segment from its event, operation, or returns mapping."""
    ir_id, parts = split_semantics_path(path)
    if len(parts) < 2 or parts[0] != "events" or type(parts[1]) is not int:
        raise ValueError("path does not belong to a processing segment")
    if len(parts) >= 3 and parts[2] == "body":
        if len(parts) < 4 or type(parts[3]) is not int:
            raise ValueError("member processing path lacks its segment position")
        return semantics_path(ir_id, *parts[:4])
    return semantics_path(ir_id, *parts[:2])


def element_scope_path(path):
    """Return the IR-relative enclosing member scope, or None for outer work."""
    _, parts = split_semantics_path(path)
    if len(parts) >= 3 and parts[0] == "events" and type(parts[1]) is int and parts[2] == "body":
        return parts[:2]
    return None


def compiled_event_position(path):
    """Resolve an ordinary/member compiled event coordinate without offsets."""
    _, parts = split_semantics_path(path)
    if len(parts) == 2 and parts[0] == "events" and type(parts[1]) is int:
        return parts[1], None
    if (len(parts) == 4 and parts[0] == "events" and parts[2] == "body"
            and type(parts[1]) is int and type(parts[3]) is int):
        return parts[1], parts[3]
    raise ValueError("path does not identify a compiled effect event")
