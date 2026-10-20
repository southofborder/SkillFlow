"""Evidence-backed sensitivity declarations over lexical values and ranges.

Declarations describe source information, not actual disclosure or a DOE
verdict. ``each`` is a member-range selector, never a generated Data identity.
An empty declaration list does not establish that the content is nonsensitive.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, StrictStr, field_validator, model_validator

from skillflow.common.source_evidence import _json_object, _require_json, extract_source_lines
from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.values import (
    StrictSpec, Text, Index, ValueRef, InputRef, LocalRef, AlternativesRef,
)
from skillflow.propagation.data.models import _require_list
from skillflow.common.source_evidence import json_pointer
from skillflow.common.validation import structural_error, validation_at

SENSITIVITY_CANDIDATE_VERSION = "skillflow-sensitivity-candidate-v1"
SensitivityProperty = Literal["value", "presence", "cardinality", "shape", "truth"]


class EachStep(StrictSpec):
    kind: Literal["each"]


SensitivityPath = Annotated[list[StrictStr | Index | EachStep], BeforeValidator(_require_list)]


class SensitivityDeclaration(StrictSpec):
    value: ValueRef
    path: SensitivityPath = Field(default_factory=list)
    property: SensitivityProperty = "value"
    label: Text
    evidences: Annotated[list[TaskEvidence], BeforeValidator(_require_list), Field(min_length=1)]

    @model_validator(mode="after")
    def distinct_evidence(self):
        spans = [(e.file, e.start_line, e.end_line) for e in self.evidences]
        if len(spans) != len(set(spans)):
            raise ValueError("duplicate sensitivity evidence span")
        return self


class SensitivityScope(StrictSpec):
    instruction_id: Text
    scope_path: Annotated[list[StrictStr | Index], BeforeValidator(_require_list)]
    declarations: Annotated[list[SensitivityDeclaration], BeforeValidator(_require_list)]

    @field_validator("scope_path")
    @classmethod
    def lexical_scope(cls, value):
        if value and not (len(value) == 2 and value[0] == "events" and type(value[1]) is int):
            raise ValueError("sensitivity scope must be the IR or one existing for_each")
        return value


class SensitivityCandidate(StrictSpec):
    schema_version: Literal["skillflow-sensitivity-candidate-v1"] = SENSITIVITY_CANDIDATE_VERSION
    scopes: Annotated[list[SensitivityScope], BeforeValidator(_require_list)]

    @model_validator(mode="after")
    def unique_scopes(self):
        positions = [(scope.instruction_id, tuple(scope.scope_path)) for scope in self.scopes]
        if len(positions) != len(set(positions)):
            raise ValueError("duplicate sensitivity scope")
        return self


def _scope_definitions(spec, scope_path):
    """Collect declaration targets, not runtime uses or inferred acquisitions."""
    def operation_names(events):
        result = set()
        for event in events:
            if event.get("kind") == "processing":
                result.update(operation_names(event["events"]))
            elif event.get("kind") != "for_each":
                result.update(op["output"] for op in event.get("atomic_ops", []) if "output" in op)
        return result

    events = spec["events"]
    if not scope_path:
        return operation_names(events)
    index = scope_path[1]
    if index >= len(events) or events[index].get("kind") != "for_each":
        raise structural_error("sensitivity_scope", "", "sensitivity scope does not reference a for_each")
    scope = events[index]
    return operation_names(events[:index]) | {scope["item"]} | operation_names(scope["body"])


def validate_scope_sensitivity(declarations, instruction, definitions, source_files):
    """Validate references and source spans, without asserting semantic truth."""
    parsed = [value if isinstance(value, SensitivityDeclaration) else SensitivityDeclaration.model_validate(value)
              for value in declarations]

    def check_ref(ref):
        if isinstance(ref, InputRef):
            inputs = instruction.get("inputs", [])
            if ref.index >= len(inputs):
                raise structural_error("sensitivity_input", "/value", "sensitivity references an absent input operand")
            if inputs[ref.index]["type"] == "external_resource":
                raise structural_error("sensitivity_resource", "/value", "resource identity is not sensitivity content; use the acquired local value")
        elif isinstance(ref, LocalRef):
            if ref.name not in definitions:
                raise structural_error("sensitivity_local", "/value", "sensitivity local is absent or escapes its lexical scope: " + ref.name)
        elif isinstance(ref, AlternativesRef):
            for item in ref.items:
                check_ref(item)

    identities = set()
    for index, declaration in enumerate(parsed):
        with validation_at(f"/{index}"):
            check_ref(declaration.value)
        from skillflow.common.recording import canonical_sha256
        identity = canonical_sha256(declaration.model_dump(mode="json", exclude={"evidences"}))
        if identity in identities:
            raise structural_error("sensitivity_duplicate", f"/{index}", "duplicate sensitivity declaration in one scope")
        identities.add(identity)
        for evidence_index, evidence in enumerate(declaration.evidences):
            pointer = f"/{index}/evidences/{evidence_index}"
            if evidence.file not in source_files:
                raise structural_error("evidence_file", pointer, "sensitivity evidence file is not frozen: " + evidence.file)
            try:
                extract_source_lines(source_files[evidence.file], evidence.start_line, evidence.end_line)
            except ValueError as error:
                raise structural_error("evidence_span", pointer, str(error)) from error
    return parsed


def validate_sensitivity_candidate(candidate, cfg, raw, source_files) -> SensitivityCandidate:
    if hasattr(candidate, "model_dump"):
        candidate = candidate.model_dump(mode="json")
    if isinstance(candidate, dict):
        _require_json(candidate, "")
    parsed = SensitivityCandidate.model_validate(_json_object(candidate))
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump(mode="json")
    instructions = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    for scope_index, scope in enumerate(parsed.scopes):
        if scope.instruction_id not in instructions or scope.instruction_id not in raw["ir_semantics"]:
            raise structural_error("sensitivity_scope", f"/scopes/{scope_index}/instruction_id", "sensitivity scope references an absent instruction")
        with validation_at(json_pointer("ir_semantics", scope.instruction_id, *scope.scope_path, "sensitivity")):
            definitions = _scope_definitions(raw["ir_semantics"][scope.instruction_id], scope.scope_path)
            validate_scope_sensitivity(scope.declarations, instructions[scope.instruction_id], definitions, source_files)
    return parsed


def extract_sensitivity_candidate(raw) -> dict[str, Any]:
    """Preserve declared empty scopes; absence never means nonsensitivity."""
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump(mode="json")
    scopes = []
    for ir_id, spec in raw["ir_semantics"].items():
        scopes.append({"instruction_id": ir_id, "scope_path": [],
                       "declarations": deepcopy(spec.get("sensitivity", []))})
        for index, event in enumerate(spec["events"]):
            if event.get("kind") == "for_each":
                scopes.append({"instruction_id": ir_id, "scope_path": ["events", index],
                               "declarations": deepcopy(event.get("sensitivity", []))})
    return SensitivityCandidate.model_validate({"schema_version": SENSITIVITY_CANDIDATE_VERSION,
                                                "scopes": scopes}).model_dump(mode="json")
