"""Offline task-driven demand candidates, without necessity verdicts.

Reference validation establishes where a claim points, not that the source
supports its semantics. These types never execute a Skill or call a model.
"""
from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, JsonValue, StrictStr, TypeAdapter, ValidationError, field_validator, model_validator

from skillflow.common.source_evidence import _json_object, _require_json, extract_source_lines
from skillflow.propagation.contracts.values import ValueRef, InputRef, LocalRef, LiteralRef, AlternativesRef, Text
from skillflow.propagation.contracts.task import Task, TaskEvidence
from skillflow.propagation.contracts.references import (CFGTarget, DemandTarget, SelfTarget, InputTarget, OutputTarget, target_key)
from skillflow.propagation.data.models import _check_json_value, _require_list
from skillflow.common.validation import StructuralValidationError, structural_error, validation_at, schema_error


DemandProperty = Literal["value", "presence", "cardinality", "shape", "truth", "action"]
DemandPath = Annotated[list[StrictStr | Annotated[int, Field(strict=True, ge=0)]],
                       BeforeValidator(_require_list)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, revalidate_instances="always")


class RefExpression(_Strict):
    op: Literal["ref"]
    value: ValueRef


class LiteralExpression(_Strict):
    op: Literal["literal"]
    value: JsonValue

    @field_validator("value", mode="before")
    @classmethod
    def json_value(cls, value):
        _check_json_value(value)
        return value


class FieldExpression(_Strict):
    op: Literal["field"]
    arg: "DemandExpression"
    path: DemandPath

    @field_validator("path")
    @classmethod
    def nonempty_path(cls, path):
        if not path:
            raise ValueError("field expression needs a nonempty path")
        return path


class UnaryExpression(_Strict):
    op: Literal["present", "count", "not"]
    arg: "DemandExpression"

    @model_validator(mode="after")
    def known_operand_type(self):
        literals = _known_literals(self.arg)
        if self.op == "not" and any(type(value) is not bool for value in literals):
            raise ValueError("not requires Boolean input, without implicit truth conversion")
        if self.op == "count" and any(type(value) is not list for value in literals):
            raise ValueError("count requires a list; it is not a success-count inference")
        return self


class ComparisonExpression(_Strict):
    op: Literal["eq", "ne", "lt", "le", "gt", "ge"]
    left: "DemandExpression"
    right: "DemandExpression"


class BooleanExpression(_Strict):
    op: Literal["and", "or"]
    args: list["DemandExpression"]

    @field_validator("args", mode="before")
    @classmethod
    def strict_args(cls, value):
        return _require_list(value)

    @field_validator("args")
    @classmethod
    def minimum_arity(cls, args):
        if len(args) < 2:
            raise ValueError("and/or requires at least two operands")
        return args

    @model_validator(mode="after")
    def known_operand_type(self):
        if any(type(value) is not bool for arg in self.args for value in _known_literals(arg)):
            raise ValueError("and/or requires Boolean inputs, without implicit truth conversion")
        return self


DemandExpression = Annotated[
    RefExpression | LiteralExpression | FieldExpression | UnaryExpression | ComparisonExpression | BooleanExpression,
    Field(discriminator="op"),
]


def _known_literals(expression):
    if isinstance(expression, LiteralExpression):
        return [expression.value]
    if isinstance(expression, RefExpression):
        return [ref.value for ref in _ref_leaves(expression.value) if isinstance(ref, LiteralRef)]
    if isinstance(expression, FieldExpression):
        result = []
        for value in _known_literals(expression.arg):
            try:
                for step in expression.path:
                    if isinstance(step, str) and type(value) is not dict or type(step) is int and type(value) is not list:
                        raise KeyError(step)
                    value = value[step]
                result.append(value)
            except (KeyError, IndexError, TypeError):
                pass
        return result
    if isinstance(expression, UnaryExpression):
        return [0 if expression.op == "count" else True]
    if isinstance(expression, (ComparisonExpression, BooleanExpression)):
        return [True]
    return []


for _expression_type in (FieldExpression, UnaryExpression, ComparisonExpression, BooleanExpression):
    _expression_type.model_rebuild()


class RawDemandGoal(_Strict):
    requirement_id: Text
    target: CFGTarget
    preserve: DemandProperty
    path: DemandPath = Field(default_factory=list)
    expected: ValueRef | None = None
    expected_path: DemandPath = Field(default_factory=list)
    reason: Text

    @model_validator(mode="after")
    def expected_path_has_value(self):
        if self.expected is None and self.expected_path:
            raise ValueError("expected_path requires an expected symbolic value")
        if self.preserve == "action" and (self.path or self.expected is not None):
            raise ValueError("behavior/restriction goals cannot silently carry unused value selections")
        return self


class DemandGoal(RawDemandGoal):
    """Canonical goal identity is generated during joint normalization."""
    id: Text
    target: DemandTarget


class DemandSupplement(_Strict):
    target: DemandTarget
    expression: DemandExpression
    evidences: Annotated[list[TaskEvidence], Field(min_length=1)]

    @field_validator("evidences", mode="before")
    @classmethod
    def strict_evidences(cls, value):
        return _require_list(value)

    @model_validator(mode="after")
    def unique_evidence(self):
        keys = [(e.file, e.start_line, e.end_line) for e in self.evidences]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate demand expression evidence span")
        return self


class RawDemandSupplement(DemandSupplement):
    """Top-level model expressions can only address the pre-existing CFG."""
    target: CFGTarget


class OperationTaskGoal(_Strict):
    """A task seed attached to its operation, without a predicted ID."""
    requirement_id: Text
    target: Annotated[SelfTarget | InputTarget | OutputTarget, Field(discriminator="kind")]
    preserve: DemandProperty
    path: DemandPath = Field(default_factory=list)
    expected: ValueRef | None = None
    expected_path: DemandPath = Field(default_factory=list)
    reason: Text

    @model_validator(mode="after")
    def value_fields(self):
        if self.expected is None and self.expected_path:
            raise ValueError("expected_path requires an expected symbolic value")
        if self.preserve == "action" and (self.path or self.expected is not None):
            raise ValueError("behavior/restriction goals cannot carry value selections")
        return self


class OperationExpression(_Strict):
    expression: DemandExpression
    evidences: Annotated[list[TaskEvidence], Field(min_length=1), BeforeValidator(_require_list)]


class CandidateDemand(_Strict):
    goals: list[DemandGoal]
    expressions: list[DemandSupplement] = Field(default_factory=list)

    @field_validator("goals", "expressions", mode="before")
    @classmethod
    def strict_lists(cls, value):
        return _require_list(value)

    @model_validator(mode="after")
    def unique_identifiers(self):
        identifiers = [goal.id for goal in self.goals]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("duplicate demand goal identifiers")
        targets = [target_key(item.target) for item in self.expressions]
        if len(targets) != len(set(targets)):
            raise ValueError("multiple expression supplements for one target")
        return self


def expression_refs(expression: DemandExpression):
    """Yield refs in syntax order without inferring a predicate's meaning."""
    if isinstance(expression, RefExpression):
        yield expression.value
    elif isinstance(expression, (FieldExpression, UnaryExpression)):
        yield from expression_refs(expression.arg)
    elif isinstance(expression, ComparisonExpression):
        yield from expression_refs(expression.left)
        yield from expression_refs(expression.right)
    elif isinstance(expression, BooleanExpression):
        for child in expression.args:
            yield from expression_refs(child)


def _validate_ref(ref: ValueRef, target: dict[str, Any]) -> None:
    if isinstance(ref, InputRef):
        if ref.index >= target.get("input_count", 0):
            raise structural_error("input_reference", "", "demand value references an absent IR input")
        if ref.index in target.get("resource_inputs", []):
            raise structural_error("resource_reference", "", "resource identity is not a demand value; use an explicit payload reference")
    elif isinstance(ref, LocalRef):
        if ref.name not in target.get("available_locals", []):
            raise structural_error("local_scope", "", f"demand value is undefined or escapes its scope: {ref.name}",
                                   available_locals=target.get("available_locals", []),
                                   input_count=target.get("input_count", 0))
    elif isinstance(ref, AlternativesRef):
        for child in ref.items:
            _validate_ref(child, target)


def _ref_leaves(ref):
    if isinstance(ref, AlternativesRef):
        for child in ref.items:
            yield from _ref_leaves(child)
    else:
        yield ref


def _literal_inputs(expression, literals):
    """Type-check explicit CFG literals without evaluating unknown functions."""
    if isinstance(expression, list):
        return [_literal_inputs(value, literals) for value in expression]
    if not isinstance(expression, dict):
        return expression
    if expression.get("kind") == "input" and str(expression["index"]) in literals:
        return {"kind": "literal", "value": literals[str(expression["index"])]}
    return {key: value if key == "value" and (expression.get("op") == "literal" or expression.get("kind") == "literal")
            else _literal_inputs(value, literals) for key, value in expression.items()}


def goal_target_capability(target: dict[str, Any], preserve: str) -> str | None:
    """The single mechanical seed capability used by validation and solving.

    Task.bindings deliberately does not use this restriction: it associates a
    requirement with any real CFG position, rather than creating a value demand.
    Missing task goals remain analysis diagnostics, not malformed candidates.
    """
    kind = target.get("kind")
    if preserve == "action":
        if target.get("domain") == "transfer" and kind in {"operation", "input_use", "local_output"}:
            return "operation_action"
        return "ir_action" if kind == "instruction" and target.get("instruction_id") else None
    if kind in {"input", "output"} and target.get("instruction_id"):
        return "ir_" + kind
    if kind == "input_use":
        return "operation_input"
    if kind == "local_output":
        return "operation_output"
    if kind == "operation" and "output" in target.get("value", {}):
        return "operation_output"
    if kind == "output_binding":
        return "output_binding"
    return None


def validate_demand_candidate(
    candidate: CandidateDemand | dict[str, Any] | str,
    task: Task | dict[str, Any],
    source_files: dict[str, str],
    targets: dict[str, dict[str, Any]],
) -> CandidateDemand:
    """Validate structure and references; missing task goals remain reportable.

    No requirement coverage is invented. A true quote with a mistaken
    interpretation can pass this structural check and remains a review concern.
    """
    if isinstance(candidate, CandidateDemand):
        candidate = candidate.model_dump(mode="json")
    if isinstance(candidate, dict):
        _require_json(candidate, "")
    try:
        candidate = _json_object(candidate)
        parsed = CandidateDemand.model_validate(candidate)
    except ValidationError as error:
        raise schema_error(error, candidate=candidate, schema=CandidateDemand.model_json_schema()) from error
    parsed_task = Task.model_validate(task.model_dump(mode="json") if isinstance(task, Task) else task)
    requirements = {item.id for item in parsed_task.requirements}
    errors = []
    for goal_index, goal in enumerate(parsed.goals):
        if goal.requirement_id not in requirements:
            errors.append({"code": "requirement_reference", "path": f"/goals/{goal_index}/requirement_id",
                           "message": f"unknown task requirement: {goal.requirement_id}"})
        if target_key(goal.target) not in targets:
            errors.append({"code": "demand_target_reference", "path": f"/goals/{goal_index}/target",
                           "message": f"unknown demand target: {target_key(goal.target)}"})
            continue
        target = targets[target_key(goal.target)]
        if goal_target_capability(target, goal.preserve) is None:
            errors.append({"code": "demand_target_capability", "path": f"/goals/{goal_index}/target",
                           "message": "The selected target cannot carry this executable preservation requirement.",
                           "context": {"target": goal.target.model_dump(mode="json"), "target_kind": target.get("kind"),
                                       "target_pointer": target.get("pointer"), "preserve": goal.preserve}})
        if goal.expected is not None:
            try:
                with validation_at(f"/goals/{goal_index}/expected"):
                    _validate_ref(goal.expected, target)
            except StructuralValidationError as error:
                errors.extend(error.diagnostics)
    for supplement_index, supplement in enumerate(parsed.expressions):
        if target_key(supplement.target) not in targets:
            errors.append({"code": "expression_target_reference", "path": f"/expressions/{supplement_index}/target",
                           "message": f"unknown expression target: {target_key(supplement.target)}"})
            continue
        target = targets[target_key(supplement.target)]
        if not target.get("supports_expression", False):
            errors.append({"code": "expression_target_capability", "path": f"/expressions/{supplement_index}/target",
                           "message": "expression supplements require compute, filter_items, or a control target",
                           "context": {"target": supplement.target.model_dump(mode="json"), "target_pointer": target.get("pointer")}})
            continue
        try:
            TypeAdapter(DemandExpression).validate_python(_literal_inputs(
                supplement.expression.model_dump(mode="json"), target.get("input_literals", {})))
        except ValidationError as error:
            errors.extend(schema_error(error, f"/expressions/{supplement_index}/expression",
                                       candidate=supplement.expression.model_dump(mode="json"),
                                       schema=TypeAdapter(DemandExpression).json_schema()).diagnostics)
        declared = target.get("declared_refs")
        for ref in expression_refs(supplement.expression):
            try:
                with validation_at(f"/expressions/{supplement_index}/expression"):
                    _validate_ref(ref, target)
            except StructuralValidationError as error:
                errors.extend(error.diagnostics)
            if declared is not None:
                for leaf in _ref_leaves(ref):
                    if not isinstance(leaf, LiteralRef) and leaf.model_dump(mode="json") not in declared:
                        errors.append({"code": "expression_input", "path": f"/expressions/{supplement_index}/expression",
                                       "message": "expression supplements cannot introduce undeclared operation inputs"})
        for evidence_index, evidence in enumerate(supplement.evidences):
            if evidence.file not in source_files:
                errors.append({"code": "evidence_file", "path": f"/expressions/{supplement_index}/evidences/{evidence_index}",
                               "message": f"evidence file is not in the frozen source table: {evidence.file}"})
                continue
            try:
                extract_source_lines(source_files[evidence.file], evidence.start_line, evidence.end_line)
            except ValueError as error:
                errors.append({"code": "evidence_span", "path": f"/expressions/{supplement_index}/evidences/{evidence_index}",
                               "message": str(error)})
    if errors:
        raise StructuralValidationError(errors)
    return parsed
