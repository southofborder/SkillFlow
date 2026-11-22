"""Source-established input defects, without repairing actual operation inputs.

The source review establishes the semantic claim. These pure helpers validate
its evidence and actual coordinates and preserve one identity across a paired
request/response. They never allocate Data, create a demand or infer a fix.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import ConfigDict, Field, RootModel, TypeAdapter, field_validator, model_validator

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import extract_source_lines, json_pointer
from skillflow.propagation.contracts.demand import GoalPath, _check_goal_path, _validate_ref
from skillflow.propagation.contracts.demand_index import build_demand_target_index
from skillflow.propagation.contracts.input_requirements import InformationRequirement
from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.values import Index, StrictSpec, Text, ValueRef
from skillflow.propagation.contracts.specs import RawAtomicOp
from skillflow.propagation.contracts.uses import value_uses


class AbsentArgument(StrictSpec):
    kind: Literal["absent_argument"]


class ActualInputRange(StrictSpec):
    kind: Literal["input_range"]
    input_index: Index
    path: GoalPath
    _path = field_validator("path")(_check_goal_path)


class MissingFieldInputRange(ActualInputRange):
    path: GoalPath = Field(min_length=1)


class NamedParameter(StrictSpec):
    kind: Literal["named"]
    name: Text


class PositionalParameter(StrictSpec):
    kind: Literal["positional"]
    position: Index


class SourceRole(StrictSpec):
    kind: Literal["source_role"]
    description: Text


class ExistingLexicalValue(StrictSpec):
    value: ValueRef
    path: GoalPath
    _path = field_validator("path")(_check_goal_path)


class ExpectedInput(StrictSpec):
    parameter: Annotated[NamedParameter | PositionalParameter | SourceRole, Field(discriminator="kind")]
    information: InformationRequirement
    source_value: ExistingLexicalValue | None
    description: Text


class ActionImpact(StrictSpec):
    kind: Literal["action"]


class OutputImpact(InformationRequirement):
    kind: Literal["output"]
    _path = field_validator("path")(_check_goal_path)


NativeImpact = Annotated[ActionImpact | OutputImpact, Field(discriminator="kind")]


class _SourceInputFindingFields(StrictSpec):
    target_id: Text
    expected: ExpectedInput
    impacts: list[NativeImpact] = Field(min_length=1)
    requirement_evidences: list[TaskEvidence] = Field(min_length=1)
    occurrence_evidences: list[TaskEvidence] = Field(min_length=1)
    reason: Text

    @model_validator(mode="after")
    def native_information(self):
        _check_goal_path(self.expected.information.path)
        keys = [canonical_sha256(x.model_dump(mode="json")) for x in self.impacts]
        if len(keys) != len(set(keys)):
            raise ValueError("Source-input impacts must not repeat")
        return self


class MissingArgumentFinding(_SourceInputFindingFields):
    kind: Literal["missing_argument"]
    actual: AbsentArgument


class MissingFieldFinding(_SourceInputFindingFields):
    kind: Literal["missing_field"]
    actual: MissingFieldInputRange


class WrongFieldFinding(_SourceInputFindingFields):
    kind: Literal["wrong_field"]
    actual: ActualInputRange


SourceInputFindingVariant = Annotated[
    MissingArgumentFinding | MissingFieldFinding | WrongFieldFinding,
    Field(discriminator="kind"),
]
_FindingValue = TypeVar("_FindingValue")


class _FindingRecord(RootModel[_FindingValue], Generic[_FindingValue]):
    """Keep flat wire records and the existing model validation/access API."""

    model_config = ConfigDict(strict=True, frozen=True)

    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            if name.startswith("_"):
                raise
            return getattr(object.__getattribute__(self, "root"), name)


class SourceInputFindingCandidate(_FindingRecord[SourceInputFindingVariant]):
    pass


class SourceOperationReference(StrictSpec):
    instruction_id: Text
    raw_path: list[str | Index]
    impacts: list[NativeImpact] = Field(min_length=1)


class NormalizedMissingArgumentFinding(MissingArgumentFinding):
    id: Text
    operation_refs: list[SourceOperationReference] = Field(min_length=1)


class NormalizedMissingFieldFinding(MissingFieldFinding):
    id: Text
    operation_refs: list[SourceOperationReference] = Field(min_length=1)


class NormalizedWrongFieldFinding(WrongFieldFinding):
    id: Text
    operation_refs: list[SourceOperationReference] = Field(min_length=1)


class NormalizedSourceInputFinding(_FindingRecord[Annotated[
    NormalizedMissingArgumentFinding | NormalizedMissingFieldFinding | NormalizedWrongFieldFinding,
    Field(discriminator="kind"),
]]):
    pass


SOURCE_INPUT_FINDING_GUIDANCE = """SOURCE INPUT FINDING LOCATORS
Use the finding kind and its matching actual form together:
- missing_argument: actual={"kind":"absent_argument"}, only when an entire
  source-required argument is absent. Do not invent an actual input slot.
- missing_field: actual={"kind":"input_range","input_index":N,"path":[...]},
  where N selects an existing operand of the targeted native operation and path
  is a nonempty, source-established concrete field path within that operand.
  The missing child need not exist; [] identifies the whole operand and is
  invalid for missing_field. For example, a source-established omitted limit
  in the first request operand uses input_index=0 and path=["limit"].
- wrong_field: actual={"kind":"input_range","input_index":N,"path":[...]}
  locates the actual wrong range. [] is allowed only for a whole-operand error.
Input indexes are relative to the targeted operation's actual operand list,
not its enclosing CFG instruction. Output impact paths are relative to that
native operation's output, not a later selected or returned value. If a call
returns a tuple and a later select_part selects element 0, its first reply's
rows have native output path [0,"rows"], not ["rows"]. Preserve request/response
pair identity and source-supported impacts; do not infer an SDK output shape.
expected.parameter.source_role describes meaning, not a concrete missing field
name. If the source establishes a missing logical role but not its native field
encoding, do not guess a path, use [], relabel it as an absent argument, or
invent a new mapping. Use an evidenced ordinary finding only for an actual
representation concern, or a typed local barrier for the unestablished
relationship. Do not call faithful transcription of a source defect a
representation error. Keep the missing relationship and its precise source scope
explicit; do not turn uncertainty about an encoding into a confirmed field
defect or erase the observed source behavior.
An exact locator is not proof of the semantic claim. A source-input defect
requires faithful representation of the actual use; do not simultaneously claim
that the same actual operation or its receiver/input relation is mistranscribed.
"""


def source_operation_targets(*, cfg, raw_annotation, mapping):
    """Resolve only exact actual operations; parent/container IDs are not uses."""
    index = build_demand_target_index(cfg, raw_annotation)
    result = defaultdict(list)
    for entry in index.values():
        if entry.get("domain") != "transfer" or entry.get("kind") != "operation":
            continue
        raw_pointer = entry["pointer"]
        result["annotation:" + raw_pointer].append(entry)
        wire_pointer = (mapping or {}).get("wire_paths", {}).get(raw_pointer)
        if wire_pointer is not None:
            if wire_pointer != raw_pointer:
                result["annotation:" + wire_pointer].append(entry)
            result["fragment:processing:" + wire_pointer].append(entry)
    return dict(result)


def _validate_pair(entries):
    if len(entries) == 1:
        return
    if len(entries) != 2 or {e["value"]["op"] for e in entries} != {"deliver", "receive"}:
        raise ValueError("Source-input target aliases unrelated actual operations")
    request = next(e for e in entries if e["value"]["op"] == "deliver")
    response = next(e for e in entries if e["value"]["op"] == "receive")
    a, b = request["value"], response["value"]
    if (request["instruction_id"] != response["instruction_id"]
            or request.get("scope_path") != response.get("scope_path")
            or a.get("request_id") is None or a.get("request_id") != b.get("request_id")
            or a["target"] != b["location"] or a["inputs"] != b["inputs"]):
        raise ValueError("Source-input call target lacks an exact request/response association")


def normalize_source_input_findings(candidates, *, files, cfg, raw_annotation, compiled, mapping, review_targets=None):
    """Check authored findings against the selected source and actual inputs.

    Semantic adequacy remains the source review's responsibility. In particular,
    a rejected dependency contract is never converted into a source defect.
    """
    parsed = TypeAdapter(list[SourceInputFindingCandidate]).validate_python(candidates)
    if not parsed:
        return []
    targets = source_operation_targets(cfg=cfg, raw_annotation=raw_annotation, mapping=mapping)
    allowed = None if review_targets is None else {r["id"] for r in review_targets}
    adapter = TypeAdapter(RawAtomicOp)
    normalized = {}
    for candidate in parsed:
        value = candidate.model_dump(mode="json")
        if candidate.target_id not in targets or allowed is not None and candidate.target_id not in allowed:
            raise ValueError("Source-input finding must target an actual selected operation")
        entries = targets[candidate.target_id]
        _validate_pair(entries)
        for evidence in candidate.requirement_evidences + candidate.occurrence_evidences:
            if evidence.file not in files:
                raise ValueError("Source-input evidence is outside the frozen source")
            extract_source_lines(files[evidence.file], evidence.start_line, evidence.end_line)
        operation_refs = []
        for entry in entries:
            operation = entry["value"]
            if isinstance(candidate.actual, ActualInputRange):
                uses = value_uses(adapter.validate_python(operation))
                if candidate.actual.input_index >= len(uses):
                    raise ValueError("Source-input finding refers to an absent actual operation input")
            expected = candidate.expected.source_value
            if expected is not None:
                _validate_ref(expected.value, entry)
                # Literals must already occur in this lexical environment;
                # an intended but absent constant belongs in the description.
                def check_literal(ref):
                    if ref.kind == "alternatives":
                        for item in ref.items:
                            check_literal(item)
                    elif ref.kind == "literal":
                        values = list(entry.get("input_literals", {}).values()) + [r["value"] for r in entry.get("declared_refs", []) if r["kind"] == "literal"]
                        if canonical_sha256(ref.value) not in {canonical_sha256(x) for x in values}:
                            raise ValueError("Expected lexical literal is not present at the actual operation")
                check_literal(expected.value)
            impacts = []
            for impact in value["impacts"]:
                if impact["kind"] == "action":
                    if len(entries) == 1 or operation["op"] == "deliver":
                        impacts.append(impact)
                elif "output" in operation:
                    impacts.append(impact)
            if impacts:
                operation_refs.append({"instruction_id": entry["instruction_id"], "raw_path": deepcopy(entry["raw_path"]), "impacts": deepcopy(impacts)})
        if any(not any(impact in ref["impacts"] for ref in operation_refs) for impact in value["impacts"]):
            raise ValueError("Source-input impact does not identify an actual native action or output")
        body = {**value, "operation_refs": sorted(operation_refs, key=canonical_sha256)}
        identity = "source_input_finding_" + canonical_sha256(body)[:20]
        if identity in normalized:
            raise ValueError("Duplicate source-input finding")
        normalized[identity] = NormalizedSourceInputFinding.model_validate({"id": identity, **body}).model_dump(mode="json")
    return [normalized[key] for key in sorted(normalized)]


class SourceInputMismatchIndex:
    """Occurrence index for an already identity-checked immutable receipt."""
    def __init__(self, receipt=None):
        self.findings = deepcopy((receipt or {}).get("review_core", {}).get("source_input_findings", []))
        self.by_operation = defaultdict(list)
        for finding in self.findings:
            for reference in finding["operation_refs"]:
                projected = {**deepcopy(finding), "impacts": deepcopy(reference["impacts"])}
                self.by_operation[(reference["instruction_id"], tuple(reference["raw_path"]))].append(projected)

    def for_operation(self, instruction_id, raw_path):
        return deepcopy(self.by_operation.get((instruction_id, tuple(raw_path)), []))


def check_source_input_finding_consistency(normalized_findings, representation_findings, *, mapping=None, cfg=None):
    """A known source defect requires a faithful representation of that use.

    Dependency/projection review repairs concern semantic claims, not the
    recorded actual operands. They can coexist with a separately known source
    defect. Ordinary overlapping processing/CFG repair findings cannot.
    """
    cfg_sites = {ir["id"]: "cfg:" + json_pointer("blocks", bid, "instructions", i)
                 for bid, block in (cfg or {}).get("blocks", {}).items()
                 for i, ir in enumerate(block["instructions"])}
    wire = (mapping or {}).get("wire_paths", {})
    for source in normalized_findings:
        protected = {source["target_id"]}
        for ref in source["operation_refs"]:
            pointer = json_pointer("ir_semantics", ref["instruction_id"], *ref["raw_path"])
            protected.add("annotation:" + pointer)
            if pointer in wire:
                protected.add("annotation:" + wire[pointer])
                protected.add("fragment:processing:" + wire[pointer])
            if ref["instruction_id"] in cfg_sites:
                protected.add(cfg_sites[ref["instruction_id"]])
        for finding in representation_findings:
            if (finding.get("input_contract_obligation_id") or finding.get("input_projection_scope_ids")
                    or finding.get("domain") not in {"cfg", "annotation"}
                    or finding.get("owner") in {"task-correspondence", "sensitivity"}):
                continue
            for actual in finding.get("target_ids", []):
                # A contract-only claim does not assert that the actual use is
                # mistranscribed; its own scoped review controls that claim.
                if any("/" + field in actual for field in ("demand_transfer", "input_contract", "sensitivity", "realizations")):
                    continue
                if any(actual == site or actual.startswith(site + "/") or site.startswith(actual + "/")
                       for site in protected):
                    raise ValueError("Source-input error conflicts with an unfaithful actual-operation representation at " + actual)
