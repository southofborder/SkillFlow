"""Occurrence-local consumption of verified source-review validation barriers.

The receipt loader validates and binds these records. They are representation
failures, never semantic source findings, replacement values or demand seeds.
Field claims retain their source-backed role and coordinates. Unlocated
structural errors retain the complete operation scopes recorded by validation.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy


class ReviewValidationBarriers:
    def __init__(self, receipt=None):
        self.barriers = deepcopy((receipt or {}).get("review_core", {}).get("validation_barriers", []))
        self.global_barriers = []
        self.by_operation = defaultdict(list)
        self.receiver_inputs = None
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

    def for_receiver_input(self, engine, instruction, slot):
        if self.receiver_inputs is None:
            self.receiver_inputs = defaultdict(list)
            if any(b.get("range", {}).get("role") == "receiver" for b in self.barriers):
                for info in engine.ops.values():
                    ir = info["position"]["instruction_id"]
                    spec = info["spec"]
                    address = engine.compiled["locations"].get(spec.get("target", spec.get("location")), {})
                    for barrier in self.for_operation(ir, info["raw_op"]):
                        if barrier.get("range", {}).get("role") != "receiver":
                            continue
                        for ref in address.get("operand_refs", []):
                            if ref["instruction_id"] == ir and ref["side"] == "input":
                                self.receiver_inputs[(ir, ref["index"])].append(barrier)
        return self.receiver_inputs.get((instruction, slot), ())


def barrier_index(engine):
    index = getattr(engine, "review_validation_barriers", None)
    if index is None:
        index = ReviewValidationBarriers(getattr(getattr(engine, "contracts", None), "receipt", None))
        engine.review_validation_barriers = index
    return index


def operation_barriers(engine, operation, *, role=None, slot=None, information=None):
    from .review_ranges import overlap_information
    info = engine.ops[operation]
    rows = barrier_index(engine).for_operation(info["position"]["instruction_id"], info["raw_op"])
    return [b for b in rows if not b.get("range") or
            b["range"]["role"] == role and (role != "argument" or b["range"]["input_index"] == slot)
            and (information is None or overlap_information(b["range"]["information"], information))]


def barrier_reason(barrier):
    return ("Source-review validation barrier " + barrier["id"] + " at " + barrier["record_path"]
            + " (" + barrier["code"] + "): " + barrier["reason"]
            + " Required resolution: " + barrier["resolution"]
            + (" Affected " + str(barrier["range"]) + ". Source: " + str(barrier.get("source_refs", []))
               if barrier.get("range") else " No narrower operation input/output scope has been validated."))


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
