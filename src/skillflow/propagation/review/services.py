"""One semantic review, with unlimited mechanical response correction."""

from __future__ import annotations
from skillflow.propagation.contracts.references import CFG_TARGET, cfg_instructions

from copy import deepcopy
from typing import Any, Protocol
from pydantic import ValidationError

from skillflow.propagation.material import evidence_reference
from skillflow.common.source_evidence import _exact
from skillflow.common.source_evidence import _json_object, validate_source_ref
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.validation import StructuralValidationError, structural_error, schema_error, validation_at

from skillflow.propagation.review.material import checked_review_material
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.material import resolve_targets
from skillflow.propagation.review.models import ReviewResponse
from skillflow.propagation.review.models import CannotAssessResponse
from skillflow.propagation.review.models import RESPONSE_ADAPTER
from skillflow.propagation.review.models import NORMALIZED_ADAPTER
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.models import task_objections


class CompletionClient(Protocol):
    def complete(self, prompt: str) -> Any: ...


def check_review_evidence(evidence, material):
    """Extract the referenced original text; no model-repeated quotation."""
    return evidence_reference(evidence.model_dump(mode="json"), material)["text"]


def _evidence_diagnostics(error, evidence):
    """Keep typed resolver errors and explain only their reference namespace.

    The original resolver diagnostic remains audit material. Presentation hints
    do not choose a different citation, modify a candidate, or validate meaning.
    """
    rows = deepcopy(error.diagnostics)
    for row in rows:
        if row["code"] != "evidence_target":
            continue
        original = deepcopy(row)
        schema = CFG_TARGET.json_schema()
        forms = [schema["$defs"][item["$ref"].rsplit("/", 1)[-1]] for item in schema["anyOf"]]
        row.setdefault("audit", {"raw_diagnostics": [original]})
        row.setdefault("context", {}).update({
            "current": evidence.target.model_dump(mode="json"),
            "allowed_forms": [{key: deepcopy(value) for key, value in form.items()
                               if key not in {"title", "description"}} for form in forms],
            "format_example": (
                "Two reference namespaces: findings[].target_ids (or failure.target_ids) select "
                "existing review target_index IDs for the sealed Task, candidate annotations or compiled observations; "
                "evidences[].target resolves only against the supplied cfg. For example, if the CFG "
                "contains an instruction ir_sample with a real input[0], a CFG citation is "
                '{"target":{"instruction_id":"ir_sample","side":"input","index":0},'
                '"reason":"The CFG defines this input."}. A finding about a generated annotation '
                "event instead uses its existing target_index ID in target_ids. Do not copy an "
                "annotation events/atomic_ops path into a CFG citation. A path is valid only if it "
                "exists at that CFG anchor, including genuine metadata fields. A source-only "
                "evidence list is allowed when the source supports the claim. These are syntax "
                "and namespace examples, not replacement evidence for this finding."
            ),
        })
    return rows


def validate_response(raw: Any, material: dict[str, Any], *, normalized=False) -> ReviewResponse:
    material = checked_review_material(material)
    try:
        value = _json_object(raw)
    except ValueError as error:
        raise structural_error("json_object", "", str(error)) from error
    try:
        response = (NORMALIZED_ADAPTER if normalized else RESPONSE_ADAPTER).validate_python(value)
    except ValidationError as error:
        raise schema_error(error, candidate=value,
                           schema=(NORMALIZED_ADAPTER if normalized else RESPONSE_ADAPTER).json_schema()) from error
    diagnostics = []
    def references(claim, path):
        known = {item["id"] for item in material["target_index"]}
        for index, target_id in enumerate(claim.target_ids):
            if target_id not in known:
                diagnostics.append({"code": "review_target", "path": path + f"/target_ids/{index}",
                    "message": f"review target does not exist: {target_id}",
                    "context": {"allowed": sorted(known)}})
        for index, evidence in enumerate(claim.evidences):
            try:
                with validation_at(path + f"/evidences/{index}"):
                    check_review_evidence(evidence, material)
            except StructuralValidationError as error:
                diagnostics.extend(_evidence_diagnostics(error, evidence))
    if isinstance(response, CannotAssessResponse):
        references(response.failure, "/failure")
        if diagnostics:
            raise StructuralValidationError(diagnostics)
        raise SemanticFailure(response.failure.model_dump(mode="json"))
    try:
        _exact(response.reviewed_ir_ids, set(cfg_instructions(material["cfg"])), "reviewed IR coverage")
    except ValueError as error:
        diagnostics.append({"code": "review_coverage", "path": "/reviewed_ir_ids", "message": str(error),
                            "context": {"required": sorted(cfg_instructions(material["cfg"]))}})
    for index, finding in enumerate(response.findings):
        references(finding, f"/findings/{index}")
        target_kinds = {item["id"]: item["kind"] for item in material["target_index"]}
        # Domain compatibility depends on resolved targets. Unknown references
        # are already diagnosed above; do not infer their eventual categories.
        targets_known = all(target in target_kinds for target in finding.target_ids)
        if finding.domain == "task":
            known_requirements = {item["id"] for item in material["task"]["requirements"]}
            objection = finding.task_objection
            if not set(objection.requirement_ids) <= known_requirements:
                diagnostics.append({"code": "task_objection_requirement", "path": f"/findings/{index}/task_objection",
                                    "message": "task objection refers to an unknown requirement"})
            from skillflow.propagation.contracts.joint import joint_source_files
            for span_index, span in enumerate(objection.source_spans):
                try:
                    validate_source_ref(span.model_dump(mode="json"), joint_source_files(material))
                except ValueError as error:
                    diagnostics.append({"code": "task_objection_source", "path": f"/findings/{index}/task_objection/source_spans/{span_index}",
                                        "message": str(error)})
            if targets_known and any(target_kinds[target] != "task" for target in finding.target_ids):
                diagnostics.append({"code": "task_finding_target", "path": f"/findings/{index}/target_ids",
                                    "message": "task findings must target the sealed Task or its existing parent containers"})
        elif targets_known and not any(target_kinds[target] in {"annotation", "observation"} for target in finding.target_ids):
            diagnostics.append({"code": "annotation_finding_target", "path": f"/findings/{index}/target_ids",
                                "message": "annotation findings require a real annotation or observation target; Task targets may only add context"})
    _check_axes(response, material, diagnostics, normalized=normalized)
    if diagnostics:
        raise StructuralValidationError(diagnostics)
    if normalized:
        return response
    payload = response.model_dump(mode="json")
    payload["findings"] = [{**finding, "id": f"F{index + 1:03d}"}
                           for index, finding in enumerate(payload["findings"])]
    for axis in ("source_checks", "requirement_checks", "declaration_checks"):
        for check in payload[axis]:
            check["finding_ids"] = [f"F{index + 1:03d}" for index in check.pop("finding_indexes")]
    return ReviewResponse.model_validate(payload)


def _check_axes(response, material, diagnostics, *, normalized):
    """Exact mechanical accounting cannot establish the correctness of a check."""
    from skillflow.propagation.contracts.joint import joint_source_files
    files = joint_source_files(material)
    expected = {(item["file"], item["line"]) for item in material["source_line_universe"]}
    seen = set()
    for index, check in enumerate(response.source_checks):
        path = f"/source_checks/{index}"
        try:
            validate_source_ref({key: getattr(check, key) for key in ("file", "start_line", "end_line")}, files)
            covered = {(check.file, line) for line in range(check.start_line, check.end_line + 1)} & expected
            if not covered:
                raise ValueError("source check must cover at least one nonempty original line")
            if covered & seen:
                raise ValueError("source checks overlap at nonempty original lines")
            seen |= covered
        except ValueError as error:
            diagnostics.append({"code": "review_source_coverage", "path": path, "message": str(error)})
    if seen != expected:
        diagnostics.append({"code": "review_source_coverage", "path": "/source_checks",
                            "message": f"unreviewed nonempty source lines: {sorted(expected - seen)}"})
    for axis, key, required in (
            ("requirement_checks", "requirement_id", {item["id"] for item in material["task"]["requirements"]}),
            ("declaration_checks", "raw_pointer", {item["raw_pointer"] for item in material["declaration_index"]})):
        try:
            _exact([getattr(row, key) for row in getattr(response, axis)], required, axis)
        except ValueError as error:
            diagnostics.append({"code": "review_axis_coverage", "path": "/" + axis, "message": str(error),
                                "context": {"required": sorted(required)}})
    allowed = {finding.id for finding in response.findings} if normalized else set(range(len(response.findings)))
    referenced = set()
    for axis in ("source_checks", "requirement_checks", "declaration_checks"):
        for index, check in enumerate(getattr(response, axis)):
            links = check.finding_ids if normalized else check.finding_indexes
            referenced.update(links)
            if not set(links) <= allowed:
                diagnostics.append({"code": "review_finding_link", "path": f"/{axis}/{index}",
                                    "message": "check references a nonexistent finding"})
    # Task findings must be anchored by a source or requirement check; plain IR
    # accounting can never justify a source-to-Task correction.
    task_links = {link for axis in ("source_checks", "requirement_checks")
                  for check in getattr(response, axis)
                  for link in (check.finding_ids if normalized else check.finding_indexes)}
    for index, finding in enumerate(response.findings):
        link = finding.id if normalized else index
        if finding.domain == "task" and link not in task_links:
            diagnostics.append({"code": "review_task_finding_link", "path": f"/findings/{index}",
                                "message": "task finding requires an issue source or requirement check"})


def resolve_findings(response: ReviewResponse, material: dict[str, Any]) -> list[dict[str, Any]]:
    """Attach original values and IR/pointer locations without trusting model paths."""
    material = checked_review_material(material)
    response = validate_response(response.model_dump(mode="json"), material, normalized=True)
    return [{**finding.model_dump(mode="json"), "targets": resolve_targets(finding.target_ids, material)}
            for finding in response.findings]


def review_annotation(material: dict[str, Any], raw_annotation: dict[str, Any], *, client: CompletionClient) -> ReviewResponse:
    from skillflow.common.structural_correction import correct_response
    prepared = prepare_review_material(material, raw_annotation)
    return correct_response(build_prompt(prepared), complete=client.complete,
                            validate=lambda response: validate_response(response, prepared))
