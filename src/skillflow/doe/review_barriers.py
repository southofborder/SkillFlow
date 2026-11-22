"""Occurrence-local consumption of verified source-review validation barriers.

The receipt loader validates and binds these records. They are representation
failures, never semantic source findings, replacement values or demand seeds.
Until narrower relationships are validated, each barrier covers its complete
actual operation, including every paired occurrence explicitly listed.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy


class ReviewValidationBarriers:
    def __init__(self, receipt=None):
        self.barriers = deepcopy((receipt or {}).get("review_core", {}).get("validation_barriers", []))
        self.global_barriers = []
        self.by_operation = defaultdict(list)
        for barrier in self.barriers:
            if barrier["domain"] == "all_operations":
                self.global_barriers.append(barrier)
            else:
                for reference in barrier["operation_refs"]:
                    self.by_operation[(reference["instruction_id"], tuple(reference["raw_path"]))].append(barrier)

    def for_operation(self, instruction_id, raw_path):
        local = self.by_operation.get((instruction_id, tuple(raw_path)), []) if raw_path is not None else []
        rows = {row["id"]: row for row in [
            *self.global_barriers, *local]}
        return [deepcopy(rows[key]) for key in sorted(rows)]


def barrier_index(engine):
    index = getattr(engine, "review_validation_barriers", None)
    if index is None:
        index = ReviewValidationBarriers(getattr(getattr(engine, "contracts", None), "receipt", None))
        engine.review_validation_barriers = index
    return index


def operation_barriers(engine, operation):
    info = engine.ops[operation]
    return barrier_index(engine).for_operation(info["position"]["instruction_id"], info["raw_op"])


def barrier_reason(barrier):
    return ("Source-review validation barrier " + barrier["id"] + " at " + barrier["record_path"]
            + " (" + barrier["code"] + "): " + barrier["reason"]
            + " Required resolution: " + barrier["resolution"]
            + " No narrower operation input/output scope has been validated.")


def barrier_diagnostic(engine, barrier, instruction_id, operation=None, requirement=None):
    value = barrier_diagnostic_value(barrier, instruction_id, operation, requirement)
    engine.diagnostics[value["id"]] = value
    return value["id"]


def barrier_diagnostic_value(barrier, instruction_id, operation=None, requirement=None):
    """Construct the exact diagnostic without mutating a demand engine."""
    from .material import _id
    value = {"code": "input_contract_review_validation", "reason": barrier_reason(barrier),
        "instruction_id": instruction_id, "requirement_id": requirement, "operation_id": operation,
        "blocking": True, "affected_instruction_ids": [instruction_id]}
    return {"id": _id("diagnostic_", value), **value}
