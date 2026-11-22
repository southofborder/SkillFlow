"""Source-backed semantic input requirements, separate from forward influence.

These contracts describe information needed to preserve a selected output or
fulfil a tool interface. Structural validation checks coordinates and evidence;
acceptance by source review is a separate, immutable input to DOE.
"""
from __future__ import annotations

from copy import deepcopy
import re
from typing import Annotated, Literal

from pydantic import Field, model_validator, model_serializer

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import extract_source_lines, json_pointer
from skillflow.common.validation import StructuralValidationError, structural_error
from skillflow.propagation.contracts.demand import GoalPath
from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.values import StrictSpec, Text, Index


class InformationRequirement(StrictSpec):
    property: Literal["value", "presence", "cardinality", "shape", "truth"]
    path: GoalPath = Field(default_factory=list)


class InputInformationRequirement(InformationRequirement):
    """Source-supported optionality applies only to input information."""
    if_present: bool = False

    @model_serializer(mode="wrap")
    def omit_unconditional_default(self, handler):
        result = handler(self)
        if not self.if_present:
            result.pop("if_present", None)
        return result


class InputRequirementGap(StrictSpec):
    code: Literal["missing_source", "missing_interface", "ambiguous_semantics",
                  "conflicting_evidence", "unsupported_relation", "unmatched_output"]
    reason: Text
    missing: Text
    resolution: Text
    evidences: list[TaskEvidence] = Field(min_length=1)

    @model_validator(mode="after")
    def concrete_barrier(self):
        generic = {"opaque", "unknown", "unresolved", "not known", "black box",
                   "blackbox", "opaque computation", "insufficient information",
                   "more information", "review source", "inspect source", "clarify",
                   "resolve ambiguity", "check the source", "check source"}
        def vague(text):
            value = text.strip().lower().rstrip(".!")
            value = re.sub(r"^(?:the|this|an?)\s+", "", value)
            value = re.sub(r"^(?:computation|operation|function|calculation|implementation)\s+(?:is|remains)\s+", "", value)
            return value in generic
        if any(vague(text) for text in (self.reason, self.missing, self.resolution)):
            raise ValueError("An input-requirement gap must identify the specific missing fact and its resolution; generic opacity is not a reason")
        return self


class UnresolvedInputRange(StrictSpec):
    information: InformationRequirement
    gap: InputRequirementGap


def _selector_prefix(left, right):
    """Test intersecting selector prefixes, including each/index matches."""
    def step_overlap(a, b):
        return (a == b or a == {"kind": "each"} and type(b) is int
                or b == {"kind": "each"} and type(a) is int)
    return len(left) <= len(right) and all(step_overlap(a, b) for a, b in zip(left, right))


class InputRequirement(StrictSpec):
    input_index: Index
    required: list[InputInformationRequirement]
    remainder: Literal["independent", "unresolved"]
    reason: Text
    gap: InputRequirementGap | None = None
    unresolved_ranges: list[UnresolvedInputRange] = Field(default_factory=list)

    @model_validator(mode="after")
    def complete_accounting(self):
        if (self.remainder == "unresolved") != (self.gap is not None):
            raise ValueError("Only unresolved input remainders require a concrete gap")
        keys = [canonical_sha256({key: value for key, value in row.model_dump(mode="json").items()
                                  if key in {"property", "path"}}) for row in self.required]
        if len(keys) != len(set(keys)):
            raise ValueError("Required input information must not repeat")
        unknown = [canonical_sha256(row.information.model_dump(mode="json")) for row in self.unresolved_ranges]
        if len(unknown) != len(set(unknown)) or set(keys) & set(unknown):
            raise ValueError("Unresolved input ranges must be distinct from each other and from required ranges")
        # Two claims about the same property must not overlap by ancestry.
        # Different properties are independent coordinates, not equivalent
        # information merely because they have the same path.
        for left in self.unresolved_ranges:
            for right in [*self.required, *(x.information for x in self.unresolved_ranges if x is not left)]:
                a, b = left.information.model_dump(mode="json"), right.model_dump(mode="json")
                if a["property"] == b["property"] and (_selector_prefix(a["path"], b["path"]) or _selector_prefix(b["path"], a["path"])):
                    raise ValueError("Unresolved input ranges must not overlap required or other unresolved ranges")
        return self

    @model_serializer(mode="wrap")
    def omit_absent_gap(self, handler):
        result = handler(self)
        if self.gap is None:
            result.pop("gap", None)
        if not self.unresolved_ranges:
            result.pop("unresolved_ranges", None)
        return result


def check_input_coverage(rows, input_count):
    indexes = [row.input_index if hasattr(row, "input_index") else row["input_index"] for row in rows]
    if sorted(indexes) != list(range(input_count)):
        raise ValueError("Input requirements must account for every actual input index exactly once")


class DemandTransferRule(StrictSpec):
    output: InformationRequirement
    inputs: list[InputRequirement]
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)

    @model_validator(mode="after")
    def distinct_inputs(self):
        if len({row.input_index for row in self.inputs}) != len(self.inputs):
            raise ValueError("A demand-transfer rule cannot repeat an input index")
        return self


class DemandTransfer(StrictSpec):
    rules: list[DemandTransferRule] = Field(min_length=1)
    output_parts: list[InformationRequirement] | None = None

    @model_validator(mode="after")
    def exact_output_selectors(self):
        selectors = [canonical_sha256(rule.output.model_dump(mode="json")) for rule in self.rules]
        if len(set(selectors)) != len(selectors):
            raise ValueError("Demand-transfer output selectors must be distinct")
        if self.output_parts is not None:
            parts = [canonical_sha256(part.model_dump(mode="json")) for part in self.output_parts]
            if not parts or len(parts) != len(set(parts)) or not set(parts) <= set(selectors):
                raise ValueError("Closed output parts must be nonempty, distinct and match authored output rules")
            if any(part.property == "value" and not part.path for part in self.output_parts):
                raise ValueError("Closed output parts cannot include the recursive whole-output value")
        return self

    @model_serializer(mode="wrap")
    def omit_absent_parts(self, handler):
        result = handler(self)
        if self.output_parts is None:
            result.pop("output_parts", None)
        return result


class AcquisitionReturnedRange(InformationRequirement):
    property: Literal["value"]


class AcquisitionProjectionCapability(StrictSpec):
    selection_input_index: Index
    selection_parameter_path: GoalPath
    returned_range: AcquisitionReturnedRange
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)


class ToolInputContract(StrictSpec):
    inputs: list[InputRequirement]
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)
    acquisition_projections: list[AcquisitionProjectionCapability] = Field(default_factory=list)

    @model_validator(mode="after")
    def distinct_inputs(self):
        if len({row.input_index for row in self.inputs}) != len(self.inputs):
            raise ValueError("A tool-input contract cannot repeat an input index")
        slots = {row.input_index for row in self.inputs}
        identities = []
        for capability in self.acquisition_projections:
            if capability.selection_input_index not in slots:
                raise ValueError("An acquisition projection must bind an actual request input index")
            identities.append(canonical_sha256({key: value for key, value in capability.model_dump(mode="json").items()
                                               if key not in {"reason", "evidences"}}))
        if len(identities) != len(set(identities)):
            raise ValueError("Acquisition projection coordinates must not repeat")
        return self

    @model_serializer(mode="wrap")
    def omit_absent_projections(self, handler):
        result = handler(self)
        if not self.acquisition_projections:
            result.pop("acquisition_projections", None)
        return result


class CompiledInputContract(StrictSpec):
    id: Text
    kind: Literal["compute", "tool"]
    instruction_id: Text
    raw_pointer: Text
    raw_path: list[str | Index]
    contract: DemandTransfer | ToolInputContract

    @model_validator(mode="after")
    def identity_and_kind(self):
        if (self.kind == "compute") != isinstance(self.contract, DemandTransfer):
            raise ValueError("Input contract kind differs from its payload")
        attachment = "demand_transfer" if self.kind == "compute" else "input_contract"
        if self.raw_pointer != json_pointer("ir_semantics", self.instruction_id, *self.raw_path, attachment):
            raise ValueError("Input contract pointer differs from its raw operation coordinate")
        expected = input_contract_id(self.kind, self.instruction_id, self.raw_path, self.contract.model_dump(mode="json"))
        if self.id != expected:
            raise ValueError("Input contract identity differs from its coordinates and content")
        return self


def input_contract_id(kind, instruction_id, raw_path, contract):
    return "input_contract_" + canonical_sha256([kind, instruction_id, raw_path, contract])[:20]


def _evidences(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidences":
                for index, evidence in enumerate(child):
                    yield [*path, key, index], evidence
            else:
                yield from _evidences(child, [*path, key])
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _evidences(child, [*path, index])


def validate_contract_evidence(contract, source_files, pointer=""):
    for path, evidence in _evidences(contract):
        target = pointer + json_pointer(*path)
        if evidence["file"] not in source_files:
            raise structural_error("input_contract_evidence", target + "/file", "Input requirements must cite a frozen source file")
        try:
            extract_source_lines(source_files[evidence["file"]], evidence["start_line"], evidence["end_line"])
        except ValueError as error:
            raise structural_error("input_contract_evidence", target, str(error)) from error


def expected_input_contract_obligations(targets, locations, *, exact_expression_targets):
    """Inventory actual operation obligations, independent of Task and demands.

    Expression keys must come from already validated expressions. A CFG or
    output-slot expression key never exempts a different operation. The caller
    validates pairing; equal operands are not a request/response identity.
    """
    exact = set(exact_expression_targets)
    rows = []
    for key, target in targets.items():
        if target.get("domain") != "transfer" or target.get("kind") != "operation":
            continue
        operation = target["value"]
        boundary = operation.get("target", operation.get("location"))
        if operation["op"] == "compute" and key not in exact:
            kind, attachment = "compute", "demand_transfer"
        elif operation["op"] in {"deliver", "receive"} and locations.get(boundary, {}).get("kind") in {"tool", "remote"}:
            kind, attachment = "tool", "input_contract"
        else:
            continue
        ir, path = target["instruction_id"], target["raw_path"]
        scope = target.get("scope_path") or []
        row = {"id": "input_obligation_" + canonical_sha256([kind, ir, path])[:20],
               "kind": kind, "instruction_id": ir, "raw_path": deepcopy(path),
               "raw_pointer": json_pointer("ir_semantics", ir, *path, attachment),
               "attachment": attachment, "input_count": len(operation["inputs"]),
               "scope_path": deepcopy(scope), "operation": operation["op"]}
        if kind == "tool":
            row["location_id"] = boundary
            if operation.get("request_id") is not None:
                row["request_id"] = operation["request_id"]
                row["request_pair_id"] = "input_request_pair_" + canonical_sha256([ir, scope, operation["request_id"]])[:20]
        if operation.get(attachment) is not None:
            row["contract_id"] = input_contract_id(kind, ir, path, operation[attachment])
        rows.append(row)
    return sorted(rows, key=lambda row: row["id"])


def validate_required_input_contract_coverage(obligations, supplied_contracts):
    """Strict current-route completeness, separate from legacy normalization."""
    supplied = {row["raw_pointer"]: row for row in supplied_contracts}
    diagnostics = []
    for row in obligations:
        contract = supplied.get(row["raw_pointer"])
        if contract is None or contract["kind"] != row["kind"] or contract["id"] != row.get("contract_id"):
            diagnostics.extend(structural_error("input_contract_required", row["raw_pointer"],
                "This actual operation requires an explicit source-backed " + row["attachment"]
                + "; account for every actual input, including zero-input interfaces. Missing facts require a specific scoped gap.",
                obligation_id=row["id"], input_count=row["input_count"]).diagnostics)
    if diagnostics:
        raise StructuralValidationError(diagnostics)


def normalize_input_contracts(targets, source_files, locations, *, exact_expression_targets=()):
    """Compile source-owned attachments without consulting Task or demands."""
    result = []
    request_contracts = {}
    exact = set(exact_expression_targets)
    for key, target in targets.items():
        if target.get("domain") != "transfer" or target.get("kind") != "operation":
            continue
        operation = target["value"]
        ir, path = target["instruction_id"], target["raw_path"]
        if operation["op"] in {"deliver", "receive"} and operation.get("request_id") is not None:
            pair = (ir, canonical_sha256(target.get("scope_path", [])), operation["request_id"])
            request_contracts.setdefault(pair, []).append((path, operation.get("input_contract"), operation["op"]))
        for field, kind, model in (("demand_transfer", "compute", DemandTransfer),
                                   ("input_contract", "tool", ToolInputContract)):
            if operation.get(field) is None:
                continue
            pointer = json_pointer("ir_semantics", ir, *path, field)
            if kind == "compute" and (operation["op"] != "compute" or operation.get("expression") is not None or key in exact):
                raise structural_error("input_contract_target", pointer, "Demand transfer requires a compute without an overlapping expression")
            if kind == "tool":
                boundary = operation.get("target", operation.get("location"))
                if operation["op"] not in {"deliver", "receive"} or locations.get(boundary, {}).get("kind") not in {"tool", "remote"}:
                    raise structural_error("input_contract_target", pointer, "Tool input contracts require an actual tool or remote request/response boundary")
            typed = model.model_validate(operation[field])
            if kind == "tool" and typed.acquisition_projections and operation.get("request_id") is None:
                raise structural_error("acquisition_projection_pair", pointer + "/acquisition_projections",
                    "An acquisition projection requires an existing exact request/response pair")
            rows = [rule.inputs for rule in typed.rules] if kind == "compute" else [typed.inputs]
            for inputs in rows:
                check_input_coverage(inputs, len(operation["inputs"]))
            contract = typed.model_dump(mode="json")
            validate_contract_evidence(contract, source_files, pointer)
            result.append({"id": input_contract_id(kind, ir, path, contract), "kind": kind,
                           "instruction_id": ir, "raw_pointer": pointer, "raw_path": deepcopy(path),
                           "contract": contract})
    for (ir, _, _), items in request_contracts.items():
        if len({canonical_sha256(contract) for _, contract, _ in items}) > 1:
            raise structural_error("input_contract_request_pair",
                json_pointer("ir_semantics", ir, *items[-1][0], "input_contract"),
                "The paired request and response must carry the same input contract")
        if any(contract and contract.get("acquisition_projections") for _, contract, _ in items):
            if sorted(op for _, _, op in items) != ["deliver", "receive"]:
                raise structural_error("acquisition_projection_pair",
                    json_pointer("ir_semantics", ir, *items[-1][0], "input_contract", "acquisition_projections"),
                    "An acquisition projection requires one delivery and its exact paired response")
    return sorted(result, key=lambda row: row["id"])


def validate_compiled_input_contracts(rows, source_files, instruction_ids):
    parsed = [CompiledInputContract.model_validate(row).model_dump(mode="json") for row in rows]
    if len({row["id"] for row in parsed}) != len(parsed) or len({row["raw_pointer"] for row in parsed}) != len(parsed):
        raise ValueError("Compiled input contract identities and source coordinates must be unique")
    for index, row in enumerate(parsed):
        if row["instruction_id"] not in instruction_ids:
            raise ValueError("Compiled input contract references an absent instruction")
        validate_contract_evidence(row["contract"], source_files, f"/input_contracts/{index}/contract")
    return parsed
