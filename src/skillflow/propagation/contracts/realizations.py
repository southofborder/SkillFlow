"""Grounding of an immutable source Task; expression is not enforcement."""
from __future__ import annotations

from typing import Literal
from pydantic import Field, model_validator, model_serializer, ValidationError
from skillflow.propagation.contracts.task import _Strict, TaskBinding, TaskEvidence
from skillflow.common.source_evidence import Text, extract_source_lines
from skillflow.propagation.contracts.references import resolve_cfg_target, target_key
from skillflow.common.validation import StructuralValidationError, structural_error, schema_error
from skillflow.propagation.contracts.constraints import TaskConstraint


class RealizationGap(_Strict):
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)


class TaskRealization(_Strict):
    requirement_id: Text
    status: Literal["expressed", "partial", "retained_only", "unmapped"]
    bindings: list[TaskBinding]
    gaps: list[RealizationGap]
    constraints: list[TaskConstraint] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def omit_empty_constraints(self, handler):
        result = handler(self)
        if not result.get("constraints"):
            result.pop("constraints", None)
        return result

    @model_validator(mode="after")
    def honest_expression(self):
        if self.status == "expressed" and self.gaps:
            raise ValueError("expressed realization cannot hide remaining gaps")
        if self.status != "expressed" and not self.gaps:
            raise ValueError("incomplete realization must describe its remaining limitation")
        if self.status == "unmapped" and self.bindings:
            raise ValueError("unmapped realization cannot claim graph bindings")
        keys = [target_key(binding.target) for binding in self.bindings]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate realization bindings")
        from skillflow.common.recording import canonical_sha256
        constraints = [canonical_sha256(item.model_dump(mode="json")) for item in self.constraints]
        if len(constraints) != len(set(constraints)):
            raise ValueError("duplicate realization constraints")
        return self


def validate_realizations(values, *, task, cfg, source_files, goals, invalid_seed_requirements=()):
    rows, diagnostics = [], []
    for index, value in enumerate(values):
        try:
            rows.append(TaskRealization.model_validate(value))
        except ValidationError as error:
            diagnostics.extend(schema_error(error, f"/realizations/{index}", candidate=value,
                                            schema=TaskRealization.model_json_schema()).diagnostics)
    if diagnostics:
        # The row grammar is prerequisite to coverage/seed checks.
        raise StructuralValidationError(diagnostics)
    known = {item.id for item in task.requirements}
    ids = [row.requirement_id for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != known:
        diagnostics.extend(structural_error("realization_coverage", "/realizations",
            "Realizations must cover every Task requirement exactly once.",
            missing=sorted(known - set(ids)), unexpected=sorted(set(ids) - known)).diagnostics)
    seeded = {goal.requirement_id for goal in goals}
    for index, row in enumerate(rows):
        prefix = f"/realizations/{index}"
        # One short syntax lesson per diagnostic batch, never a proposed seed.
        seed_hint = {} if any(item["code"] == "realization_seed" for item in diagnostics) else {
            "format_example": (
                'Status fragments: {"status":"expressed","gaps":[]} requires a supported positive demand or constraint; '
                '{"status":"partial"} requires an executable demand or constraint and nonempty gaps; '
                '{"status":"retained_only"} requires neither and nonempty gaps. '
                'These are fragments, not replacement realizations. Do not invent a demand or remove a supported demand to change status.')}
        seed_checkable = row.requirement_id not in invalid_seed_requirements
        has_expression = row.requirement_id in seeded or bool(row.constraints)
        if seed_checkable and row.requirement_id in known and row.status in {"expressed", "partial"} and not has_expression:
            diagnostics.extend(structural_error("realization_seed", prefix,
                "An expressed or partial requirement needs a real positive goal or supported constraint.",
                requirement_id=row.requirement_id, current=row.status,
                allowed="Supply a supported demand or constraint, or retain the remaining gap as retained_only/unmapped.",
                **seed_hint).diagnostics)
        if seed_checkable and row.status in {"retained_only", "unmapped"} and has_expression:
            diagnostics.extend(structural_error("realization_seed", prefix,
                "Retained-only or unmapped requirements cannot claim positive seeds or executable constraints.",
                requirement_id=row.requirement_id, current=row.status,
                allowed="Keep supported demands and choose expressed/partial consistently with remaining gaps.",
                **seed_hint).diagnostics)
        for binding_index, binding in enumerate(row.bindings):
            try:
                resolve_cfg_target(binding.target, cfg)
            except ValueError as error:
                diagnostics.extend(structural_error("realization_target",
                    prefix + f"/bindings/{binding_index}/target", str(error),
                    current=binding.target.model_dump(mode="json")).diagnostics)
        for gap_index, gap in enumerate(row.gaps):
            for evidence_index, evidence in enumerate(gap.evidences):
                pointer = prefix + f"/gaps/{gap_index}/evidences/{evidence_index}"
                if evidence.file not in source_files:
                    diagnostics.extend(structural_error("evidence_file", pointer + "/file",
                        "Gap evidence must cite a frozen source.", current=evidence.file,
                        allowed=sorted(source_files)).diagnostics)
                    continue
                try:
                    extract_source_lines(source_files[evidence.file], evidence.start_line, evidence.end_line)
                except ValueError as error:
                    diagnostics.extend(structural_error("evidence_span", pointer, str(error)).diagnostics)
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    return [row.model_dump(mode="json") for row in rows]
