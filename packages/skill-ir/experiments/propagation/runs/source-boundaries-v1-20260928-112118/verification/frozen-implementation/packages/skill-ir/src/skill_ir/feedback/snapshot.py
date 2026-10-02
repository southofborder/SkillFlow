"""Compatibility imports for the shared input snapshot implementation.

Feedback and independent analyses freeze inputs through the same implementation.
"""

from skill_ir.inputs.snapshot import (
    SNAPSHOT_VERSION, freeze_input, read_snapshot, verify_original_input,
)

__all__ = ["SNAPSHOT_VERSION", "freeze_input", "read_snapshot", "verify_original_input"]
