"""Assemble a source-only Task revision using its original claim IDs and evidence."""
from __future__ import annotations

from pydantic import ValidationError

from skillflow.common.recording import canonical_sha256
from skillflow.common.revision_slots import decode_revision_slots, read_revision_object
from skillflow.common.source_evidence import json_pointer
from skillflow.common.validation import StructuralValidationError, schema_error, structural_error
from skillflow.propagation.contracts.task import (
    TaskIssue, TaskPurpose, TaskRequirement, _check_span, task_source_files, validate_task_candidate,
)


def _related(evidences, spans):
    return any(e["file"] == span["file"] and e["start_line"] <= span["end_line"]
               and span["start_line"] <= e["end_line"] for e in evidences for span in spans)


def assemble_task_revision(decoded, material, revision):
    """Allow source-backed additions and replacements within the finite objections.

    The previous Task is already sealed against precisely this source. A rejected
    replacement can retain its original claim. Its objection stays open for the
    independent review. An unbound new claim has no prior meaning to substitute.
    """
    previous = revision["previous_task"]
    damaged_purpose = any(d["code"] == "revision_record_json" and d["path"] == "/purpose"
                          for d in decoded.diagnostics)
    supplied = set(decoded.value) | ({"purpose"} if damaged_purpose else set())
    if supplied != {"purpose", "requirements", "issues"}:
        raise structural_error("task_revision_envelope", "", "Return purpose, requirements and issues.")
    files = task_source_files(material["source"])
    spans = [span for objection in revision["objections"] for span in objection["source_spans"]]
    challenged = {identity for objection in revision["objections"] for identity in objection["requirement_ids"]}
    unspecified = [span for objection in revision["objections"] if not objection["requirement_ids"]
                   for span in objection["source_spans"]]
    affected = challenged | {row["id"] for row in previous["requirements"] if _related(row["evidences"], unspecified)}
    retired = {identity for objection in revision["objections"] if objection["code"] == "unsupported_requirement"
               for identity in objection["requirement_ids"]}
    diagnostics = list(decoded.diagnostics)
    kept, assembled = [], {}
    requirement_ids = set()

    def claim(model, row, path):
        try:
            obj = model.model_validate(row)
        except ValidationError as exc:
            raise schema_error(exc, path, candidate=row, schema=model.model_json_schema()) from exc
        for i, evidence in enumerate(obj.evidences):
            _check_span(evidence, files, path + json_pointer("evidences", i))
        return obj.model_dump(mode="json")

    try:
        if damaged_purpose:
            raise StructuralValidationError([d for d in decoded.diagnostics if d["path"] == "/purpose"])
        purpose = claim(TaskPurpose, decoded.value["purpose"], "/purpose")
        if (purpose != previous["purpose"] and not _related(purpose["evidences"], spans)
                and not _related(previous["purpose"]["evidences"], spans)):
            raise structural_error("task_revision_scope", "/purpose", "The changed purpose has no cited objection.")
        assembled["purpose"] = purpose
    except StructuralValidationError as exc:
        diagnostics.extend(d for d in exc.diagnostics if d not in diagnostics)
        assembled["purpose"] = previous["purpose"]
        kept.append("/purpose")

    for field, model in (("requirements", TaskRequirement), ("issues", TaskIssue)):
        old = {row["id"]: row for row in previous[field]}
        collection = decode_revision_slots(decoded, field=field, owner="id", authorized=bool, required=False,
            siblings={"purpose", "requirements", "issues"} - {field})
        diagnostics.extend(d for d in collection.diagnostics if d not in diagnostics)
        values = {}
        damaged_indices = {int(d["path"].rsplit("/", 1)[1]) for d in decoded.diagnostics
                           if d["code"] == "revision_record_json" and d["path"].startswith(f"/{field}/")
                           and d["path"].rsplit("/", 1)[1].isdigit()}
        physical_indices = (i for i in range(len(decoded.value[field]) + len(damaged_indices))
                            if i not in damaged_indices)
        authored = {row["id"]: index for index, row in zip(physical_indices, decoded.value[field])
                    if isinstance(row, dict) and isinstance(row.get("id"), str)}
        def writable(row):
            if field == "requirements" and row["id"] in old:
                return row["id"] in affected
            return _related(row["evidences"], spans) or bool(affected.intersection(row.get("requirement_ids", ())))
        for identity, record in collection.rows.items():
            path = json_pointer(field, authored[identity])
            try:
                value = claim(model, record, path)
                if value != old.get(identity) and not writable(old.get(identity, value)):
                    raise structural_error("task_revision_scope", path, "Claim is outside the source-only objection.")
                if field == "issues" and not set(value["requirement_ids"]) <= requirement_ids:
                    raise structural_error("requirement_reference", path + "/requirement_ids", "Unknown revised requirement.")
                values[identity] = value
            except StructuralValidationError as exc:
                for d in exc.diagnostics:
                    diagnostics.append({**d, "context": {**d.get("context", {}), "id": identity}})
        rejected_ids = {d.get("context", {}).get("id") for d in diagnostics
                        if d["path"].startswith("/" + field + "/")}
        for identity, prior in old.items():
            if identity in values:
                continue
            if field == "requirements" and writable(prior) and identity not in retired:
                # A full replacement can split or rename an objection's claim.
                # A missing row with no replacement is still a missing obligation.
                replacement = any(key not in old and _related(v["evidences"], prior["evidences"])
                                  for key, v in values.items())
            else:
                replacement = field == "issues" or identity in retired
            if identity in rejected_ids or not writable(prior) or not replacement:
                if identity not in rejected_ids:
                    diagnostics.append({"code": "task_revision_missing", "path": json_pointer(field, identity),
                        "message": "The complete revision omitted a retained claim without a source-backed replacement."})
                if field == "issues" and not set(prior["requirement_ids"]) <= requirement_ids:
                    diagnostics.append({"code": "requirement_reference", "path": json_pointer(field, identity),
                        "message": "The prior issue references a retired requirement and cannot be retained."})
                    continue
                kept.append(json_pointer(field, identity))
                values[identity] = prior
        assembled[field] = list(values.values())
        if field == "requirements":
            requirement_ids = set(values)
    # No semantic substitute exists for a rejected new claim. Carry the good
    # rows through the finite correction, but never publish a Task missing it.
    for diagnostic in diagnostics:
        parts = diagnostic["path"].split("/")
        if len(parts) < 3 or parts[1] not in {"issues", "requirements"}:
            continue
        identity = diagnostic.get("context", {}).get("id")
        if identity is None and diagnostic["code"] == "task_revision_missing":
            continue
        if identity is None or not any(row["id"] == identity for row in previous[parts[1]]):
            raise StructuralValidationError(diagnostics)
    task = validate_task_candidate(assembled, source_files=files,
        source_sha256=material["source"]["source_sha256"]).model_dump(mode="json")
    receipt = {"scope_sha256": canonical_sha256(revision),
               "repairs": decoded.repairs, "diagnostics": diagnostics, "retained_prior": sorted(kept)}
    return task, receipt


class TaskRevisionCorrection:
    """Give the record correction the same decoded Task candidate used for validation."""

    identity = "skillflow-task-revision-correction-v1"

    def __init__(self):
        from skillflow.document_guided.fragments import fragment_correction_strategy
        self.records = fragment_correction_strategy("task")
        self.correction_evidence = None

    @staticmethod
    def _candidate(raw):
        try:
            decoded = read_revision_object(raw)
        except StructuralValidationError:
            # With no recoverable owner, the existing strategy requests a complete correction.
            return raw
        value = decoded.value
        for fault in decoded.diagnostics:
            path = fault["path"].strip("/").split("/")
            if path == ["purpose"]:
                value.setdefault("purpose", {})
            elif (len(path) == 2 and path[0] in {"requirements", "issues"} and path[1].isdigit()
                    and isinstance(value.get(path[0]), list)):
                owner = fault.get("context", {}).get("id")
                # A syntactically rejected body has no valid claim. Keep the
                # physical row coordinate and established ID for the correction.
                value[path[0]].insert(int(path[1]), {"id": owner} if isinstance(owner, str) else {})
        return value

    def build_prompt(self, base_prompt, candidate, diagnostics):
        return self.records.build_prompt(base_prompt, self._candidate(candidate), diagnostics)

    def merge(self, candidate, response):
        self.correction_evidence = None
        reply = read_revision_object(response)
        if "replacements" in reply.value and reply.diagnostics:
            raise StructuralValidationError(reply.diagnostics)
        # Retain the original bytes of a full replacement so its validation
        # receipt accounts for every recovered or rejected claim.
        if not self.records.selected:
            return response
        value = self.records.merge(self._candidate(candidate), reply.value)
        if reply.repairs:
            self.correction_evidence = {"raw_sha256": canonical_sha256(response), "repairs": reply.repairs}
        return value
