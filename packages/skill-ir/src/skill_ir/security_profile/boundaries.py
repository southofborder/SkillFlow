"""Deterministic sink classification from explicit operations and boundaries.

The model supplies evidenced boundary properties, never numeric grades.  A
grade reflects receiving scope and retention, not sensitivity or necessity.
This module is shared by compiled specifications and resolved DOE records.
"""
from __future__ import annotations

from typing import Annotated, Literal, Mapping

from pydantic import Field, model_validator

from skill_ir.propagation.compatibility import validate_operation_boundary
from skill_ir.propagation.specs import (
    StrictSpec, Text, Index, LocationSpec, IRTransferSpec, ForEachSpec,
    DeliverOp, WriteOp, iter_scoped_events,
)

SinkType = Literal[
    "network_send", "storage_write", "context_save", "model_observe",
    "external_tool", "user_output",
]


class SinkBoundary(StrictSpec):
    instruction_id: Text
    event_index: Index
    op_index: Index
    body_event_index: Index | None = None
    scope: Literal["element"] | None = None
    target: Text
    sink_type: SinkType
    exposure_level: Annotated[int, Field(strict=True, ge=1, le=3)]

    @model_validator(mode="after")
    def member_coordinates(self) -> "SinkBoundary":
        if (self.body_event_index is None) != (self.scope is None):
            raise ValueError("member sink requires both body position and element scope")
        return self


def exposure_level(location: LocationSpec | dict) -> int:
    """Compute the fixed 0--3 grade, taking the highest applicable property."""
    location = location if isinstance(location, LocationSpec) else LocationSpec.model_validate(location)
    if location.access_scope == "public":
        return 3
    if location.access_scope in {"recipient", "shared"}:
        return 2
    if location.retention == "persistent":
        return 1
    return 0


def classify_sink(
    operation: str, effect: str | None, location: LocationSpec | dict,
    *, write_mode: str | None = None,
) -> tuple[SinkType, int] | None:
    """Classify one explicit deliver/write; other operations are not sinks.

    A resolved record can call this same function with its operation, effect,
    declared location and write mode.  No opcode or inference prose is read.
    """
    if operation not in {"deliver", "write"}:
        return None
    location = location if isinstance(location, LocationSpec) else LocationSpec.model_validate(location)
    validate_operation_boundary(operation, effect, location.kind)
    if operation == "write":
        if write_mode not in {"replace", "append", "delete"}:
            raise ValueError("sink write classification requires its actual write mode")
        if write_mode == "delete":
            return None
        sink_type: SinkType = "storage_write" if location.kind == "storage" else "context_save"
    else:
        sink_type = {
            "net_send": "network_send", "model_observe": "model_observe",
            "user_output": "user_output", None: "external_tool",
        }[effect]
    level = exposure_level(location)
    return None if level == 0 else (sink_type, level)


def derive_sink_boundaries(
    locations: Mapping[str, LocationSpec | dict],
    transfer_specs: Mapping[str, IRTransferSpec | dict],
    profiles: Mapping[str, object],
) -> list[SinkBoundary]:
    """Collect sinks in stable IR-key order and actual within-IR array order.

    Repeated effects remain distinct.  A member body carries its outer event,
    body event and element scope so recipient/payload pairing is preserved.
    """
    typed_locations = {
        key: value if isinstance(value, LocationSpec) else LocationSpec.model_validate(value)
        for key, value in locations.items()
    }
    boundaries = []
    for ir_id in sorted(transfer_specs):
        spec = transfer_specs[ir_id]
        spec = spec if isinstance(spec, IRTransferSpec) else IRTransferSpec.model_validate(spec)
        profile = profiles[ir_id]
        effects = profile["effects"] if isinstance(profile, dict) else profile.effects
        for event_index, body_index, event in iter_scoped_events(spec):
            effect = None if event.effect_index is None else effects[event.effect_index]
            for op_index, operation in enumerate(event.atomic_ops):
                if not isinstance(operation, (DeliverOp, WriteOp)):
                    continue
                classification = classify_sink(operation.op, effect, typed_locations[operation.target],
                    write_mode=operation.mode if isinstance(operation, WriteOp) else None)
                if classification is None:
                    continue
                sink_type, level = classification
                scope = "element" if isinstance(spec.events[event_index], ForEachSpec) else None
                boundaries.append(SinkBoundary(
                    instruction_id=ir_id, event_index=event_index, op_index=op_index,
                    body_event_index=body_index, scope=scope, target=operation.target,
                    sink_type=sink_type, exposure_level=level,
                ))
    return boundaries
