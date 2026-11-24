"""Source-review receipts bound to one selected input-dependency contract set.

These receipts preserve semantic review evidence; their hashes and reference
checks establish identity, not the truth of an authored semantic judgment.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Literal

from pydantic import Field, TypeAdapter, model_validator

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import StrictRecord, Text, extract_source_lines, json_pointer
from skillflow.propagation.contracts.task import TaskEvidence
from skillflow.propagation.contracts.input_requirements import InputRequirementGap
from .input_contract_scopes import (
    input_contract_review_inventory, compact_review_inventory,
    reviewed_contract_scopes, reviewed_acquisition_projections,
)
from .source_input_findings import (
    normalize_source_input_findings, SourceInputMismatchIndex, check_source_input_finding_consistency,
)


VERSION = "skillflow-input-contract-review-v7"
SOURCE_REVIEW_VERSION = "skillflow-document-source-review-fragment-v10"
ARCHIVED_V14_RECEIPT = "skillflow-input-contract-review-v6"
ARCHIVED_V14_SOURCE_REVIEW = "skillflow-document-source-review-fragment-v9"
ARCHIVED_V13_RECEIPT = "skillflow-input-contract-review-v5"
ARCHIVED_V13_SOURCE_REVIEW = "skillflow-document-source-review-fragment-v8"
ARCHIVED_SOURCE_REVIEW = "skillflow-document-source-review-fragment-v7"
ARCHIVED_RECEIPT = "skillflow-input-contract-review-v4"


class InputScopeCheck(StrictRecord):
    scope_ids: list[Text] = Field(min_length=1)
    status: Literal["accepted", "rejected", "unresolved"]
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)
    gap: InputRequirementGap | None = None
    affected_scope_ids: list[Text] = Field(default_factory=list, description="Only wide rule/interface/output_parts subjects may list affected input scopes. Every subject of this group shares this list. Group narrow subjects separately.")

    @model_validator(mode="after")
    def concrete_scope(self):
        if (self.status == "unresolved") != (self.gap is not None):
            raise ValueError("Only unresolved review scopes require a concrete typed gap")
        if len(set(self.scope_ids)) != len(self.scope_ids) or len(set(self.affected_scope_ids)) != len(self.affected_scope_ids):
            raise ValueError("Review scope references must not repeat")
        if self.status == "accepted" and self.affected_scope_ids:
            raise ValueError("Accepted scopes cannot assert affected uncertain scopes")
        return self


class InputContractCheck(StrictRecord):
    obligation_id: Text
    contract_id: Text | None
    status: Literal["accepted", "rejected", "unresolved"]
    reason: Text
    evidences: list[TaskEvidence] = Field(min_length=1)
    scope_checks: list[InputScopeCheck] = Field(default_factory=list)


def input_contract_binding(*, files, cfg, task, raw_annotation, compiled, mapping):
    """The exact selected source, CFG and semantic bundle being reviewed."""
    return {
        "source_sha256": canonical_sha256(files),
        "cfg_sha256": canonical_sha256(cfg),
        "annotation_sha256": canonical_sha256({"task": task,
            "raw_annotation": raw_annotation, "compiled_annotation": compiled, "mapping": mapping}),
        "contracts_sha256": canonical_sha256((compiled or {}).get("input_contracts", [])),
        "obligations_sha256": canonical_sha256(input_contract_review_inventory(
            cfg=cfg, raw_annotation=raw_annotation, compiled=compiled, mapping=mapping)),
    }


def _binding(files, cfg, annotation):
    return input_contract_binding(files=files, cfg=cfg, task=annotation["task"],
        raw_annotation=annotation["raw_annotation"], compiled=annotation["compiled_annotation"],
        mapping=annotation["mapping"])


def _evidence(evidences, files):
    for evidence in evidences:
        if evidence["file"] not in files:
            raise ValueError("Input-contract review evidence is outside frozen source")
        extract_source_lines(files[evidence["file"]], evidence["start_line"], evidence["end_line"])


def _checked_groups(groups, scopes, files, *, archived_v7=False):
    parsed = TypeAdapter(list[InputScopeCheck]).validate_python(groups)
    values = [row.model_dump(mode="json", exclude_none=True) for row in parsed]
    expected = {row["id"]: row for row in scopes}
    actual = [identity for row in values for identity in row["scope_ids"]]
    if len(set(actual)) != len(actual) or set(actual) != set(expected):
        raise ValueError("Review scope decisions must cover the exact finite inventory once")
    decisions = {}
    for row in values:
        _evidence(row["evidences"], files)
        if row.get("gap"):
            _evidence(row["gap"]["evidences"], files)
        for identity in row["scope_ids"]:
            decisions[identity] = {"scope_id": identity, **{key: deepcopy(value) for key, value in row.items() if key != "scope_ids"}}
    wide = {"rule", "interface", "output_parts"}
    for identity, decision in decisions.items():
        for affected in decision["affected_scope_ids"]:
            subject, target = expected[identity], expected.get(affected)
            if archived_v7 and (subject["kind"] not in wide or target is None or target["kind"] in wide | {"missing_attachment", "projection"}):
                raise ValueError("Wide review barriers must reference actual input-information scopes")
            if subject["kind"] not in wide:
                raise ValueError(f"Subject {identity} ({subject['kind']}) cannot declare affected_scope_ids. Split narrow subjects from wide rule/interface/output_parts subjects and omit their affected list.")
            if target is None or target["kind"] in wide | {"missing_attachment", "projection"}:
                raise ValueError(f"Wide review barriers must reference actual input-information scopes; target {affected} is invalid for subject {identity}")
            if subject.get("output") is not None and target.get("output") != subject["output"]:
                raise ValueError("A wide review barrier references another output rule")
            if decisions[affected]["status"] == "accepted":
                raise ValueError("An affected input scope must have its own nonaccepted decision")
    return values, decisions


def checked_contract_record(check, *, inventory, files, archived_v7=False):
    """Validate one row against the full selected inventory, never a subset."""
    row = InputContractCheck.model_validate(check).model_dump(mode="json", exclude_none=True)
    obligations = {row["id"]: row for row in inventory["obligations"]}
    layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
    if row["obligation_id"] not in obligations:
        raise ValueError("Review references an unknown input-contract obligation")
    obligation, layout = obligations[row["obligation_id"]], layouts[row["obligation_id"]]
    row.setdefault("contract_id", None)
    if row["contract_id"] != obligation["contract_id"]:
        raise ValueError("Review references another supplied input-contract attachment")
    _evidence(row["evidences"], files)
    if row["status"] == "accepted":
        if row["contract_id"] is None:
            raise ValueError("A missing input-contract attachment cannot be accepted")
        if row["scope_checks"]:
            _, decisions = _checked_groups(row["scope_checks"], layout["scopes"], files, archived_v7=archived_v7)
            if any(d["status"] != "accepted" for d in decisions.values()):
                raise ValueError("Accepted summary contradicts a nonaccepted scope")
    else:
        row["scope_checks"], decisions = _checked_groups(row["scope_checks"], layout["scopes"], files, archived_v7=archived_v7)
        aggregate = "rejected" if any(d["status"] == "rejected" for d in decisions.values()) else (
            "unresolved" if any(d["status"] == "unresolved" for d in decisions.values()) else "accepted")
        if row["status"] != aggregate:
            raise ValueError("Contract summary differs from exhaustive scope decisions")
        if row["contract_id"] is None and row["status"] != "rejected":
            raise ValueError("A missing attachment is a representation rejection, not a semantic gap")
    return row


def checked_contract_checks(checks, *, inventory, files):
    values = [checked_contract_record(row, inventory=inventory, files=files) for row in checks]
    obligations = {row["id"]: row for row in inventory["obligations"]}
    actual = [row["obligation_id"] for row in values]
    if len(set(actual)) != len(actual) or set(actual) != set(obligations):
        raise ValueError("Input-contract review must cover every expected obligation exactly once")
    return sorted(values, key=lambda row: row["obligation_id"])


def contract_scope_decisions(checks, inventory, files):
    result = {}
    layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
    for row in checks:
        scopes = layouts[row["obligation_id"]]["scopes"]
        groups = row["scope_checks"] or [{"scope_ids": [s["id"] for s in scopes], "status": "accepted",
            "reason": row["reason"], "evidences": row["evidences"]}]
        _, decisions = _checked_groups(groups, scopes, files)
        result.update(decisions)
    return result


def checked_projection_checks(checks, *, inventory, files):
    return _checked_groups(checks, [{"id": row["id"], "kind": "projection"} for row in inventory["projections"]], files)


def contract_review_targets(*, contracts, cfg, mapping):
    """Canonical operation and CFG locations whose defects affect a contract."""
    mapped = {row["contract_id"]: row.get("wire_pointer") for row in (mapping or {}).get("input_contracts", [])}
    wire_paths = (mapping or {}).get("wire_paths", {})
    instructions = {ir["id"]: "cfg:" + json_pointer("blocks", block, "instructions", index)
        for block, body in (cfg or {}).get("blocks", {}).items()
        for index, ir in enumerate(body["instructions"])}
    result = {}
    for entry in contracts:
        pointer = mapped.get(entry.get("contract_id", entry["id"]))
        if not pointer:
            ancestors = [path for path in wire_paths if entry["raw_pointer"] == path
                         or entry["raw_pointer"].startswith(path + "/")]
            prefix = max(ancestors, key=len) if ancestors else None
            pointer = wire_paths[prefix] + entry["raw_pointer"][len(prefix):] if prefix is not None else entry["raw_pointer"]
        if pointer.endswith(("/input_contract", "/demand_transfer")):
            pointer = pointer.rsplit("/", 1)[0]
        if entry["instruction_id"] not in instructions:
            raise ValueError("Reviewed input contract has no actual CFG instruction")
        result[entry["id"]] = ["annotation:" + pointer, instructions[entry["instruction_id"]],
                               "fragment:processing:" + pointer]
    return result


def check_contract_finding_consistency(checks, findings, targets):
    """A local acceptance cannot contradict an overlapping known defect."""
    for check in checks:
        supported = check["status"] == "accepted" or any(row["status"] == "accepted" for row in check["scope_checks"])
        if not supported:
            continue
        for finding in findings:
            if finding.get("input_projection_scope_ids"):
                # Capability support is independent from input necessity.
                continue
            if finding.get("input_contract_obligation_id"):
                # A program-generated scoped repair finding. The finite
                # decisions, not its operation parent, bound its effect. Two
                # lowered call obligations may share that same wire parent.
                continue
            domain = finding.get("domain")
            if domain not in {"annotation", "cfg"}:
                continue
            for actual in finding.get("target_ids", []):
                if not (actual.startswith(domain + ":") or domain == "annotation" and actual.startswith("fragment:processing:")):
                    continue
                for protected in targets.get(check["obligation_id"], []):
                    if (actual == protected or actual.startswith(protected + "/")
                            or protected.startswith(actual + "/")):
                        raise ValueError("Accepted input-contract scope " + check["obligation_id"]
                            + " conflicts with a finding at its operation or CFG location: " + actual)


def source_input_findings_for_operation(receipt, instruction_id, raw_path):
    return SourceInputMismatchIndex(receipt).for_operation(instruction_id, raw_path)


def _isolation_material(*, files, cfg, annotation, context):
    """Rebuild validators' actual targets from the selected bundle, not a ledger."""
    from skillflow.document_guided.source_review import prepare_review_material
    if (not isinstance(context, dict) or set(context) - {"revision_rechecks"} != {"annotation_view", "partial", "fragments", "stage_failures"}
            or type(context["partial"]) is not bool):
        raise ValueError("Invalid isolated review material context")
    if not isinstance(context["annotation_view"], str) or context["annotation_view"] not in {"wire_annotation", "raw_annotation"}:
        raise ValueError("Unknown isolated review annotation view")
    view = annotation.get(context["annotation_view"])
    if view is None:
        raise ValueError("Isolated review view is absent from the selected annotation")
    fragments = context["fragments"]
    if not isinstance(fragments, dict):
        raise ValueError("Isolated review fragments must be actual selected projections")
    if not isinstance(context["stage_failures"], dict):
        raise ValueError("Isolated review stage failures must be a stage-name table")
    if fragments:
        from skillflow.document_guided.fragments import split_fragments
        projected = split_fragments(view)
        for owner, fragment in fragments.items():
            if (owner not in projected or not isinstance(fragment, dict)
                    or fragment.get("outcome", "completed") != "completed"
                    or any(key != "outcome" and (key not in projected[owner] or projected[owner][key] != value)
                           for key, value in fragment.items())):
                raise ValueError("Isolated review fragment differs from the selected annotation projection")
    return prepare_review_material(files=files, cfg=cfg, task=annotation["task"],
        annotation=view, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"],
        generation="fragment-v1", partial=context["partial"], fragments=fragments,
        stage_failures=context["stage_failures"],
        **({"revision_rechecks": context["revision_rechecks"]} if context.get("revision_rechecks") else {}))


def _build_core(*, files, cfg, annotation, reviewed, material, archived_v12=False, archived_v13=False, archived_v14=False):
    binding = _binding(files, cfg, annotation)
    inventory = input_contract_review_inventory(cfg=cfg, raw_annotation=annotation["raw_annotation"],
        compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    completed = reviewed.get("status") == "complete" and isinstance(reviewed.get("review"), dict)
    response = reviewed.get("review") or {}
    isolated = reviewed.get("status") in {"partial", "structural_failure"} and reviewed.get("validation") is not None
    if reviewed.get("status") == "partial" and not isolated:
        raise ValueError("Partial review requires its exact terminal candidate and validation ledger")
    validation, context = None, None
    if isolated:
        from skillflow.document_guided.source_review import isolate_source_review
        validation = reviewed.get("validation")
        if not isinstance(validation, dict) or "candidate" not in validation:
            raise ValueError("Partial review requires its exact terminal candidate and validation ledger")
        context = reviewed.get("isolation_context")
        if context is None:
            view = next((name for name in ("wire_annotation", "raw_annotation")
                         if annotation.get(name) is not None and material.get("annotation") == annotation[name]), None)
            if view is None:
                raise ValueError("Partial source review belongs to another selected annotation view")
            context = {"annotation_view": view, "partial": bool(material.get("partial", True)),
                "fragments": deepcopy(material.get("fragments", {})),
                "stage_failures": deepcopy(material.get("stage_failures", {})),
                **({"revision_rechecks": deepcopy(material["revision_rechecks"])} if material.get("revision_rechecks") else {})}
        rebuilt_material = _isolation_material(files=files, cfg=cfg, annotation=annotation, context=context)
        if archived_v14:
            rebuilt_material["identity"] = ARCHIVED_V14_SOURCE_REVIEW
        if archived_v12 or archived_v13:
            rebuilt_material["identity"] = ARCHIVED_SOURCE_REVIEW if archived_v12 else ARCHIVED_V13_SOURCE_REVIEW
            rebuilt_material.pop("processing_gap_inventory", None)
        if (material.get("input_contract_binding") != binding
                or material.get("input_contract_inventory") != inventory
                or validation.get("binding") != binding):
            raise ValueError("Input-contract source review belongs to another selected bundle or obligation inventory")
        rebuilt = isolate_source_review(validation["candidate"], rebuilt_material)
        if archived_v14 and rebuilt != {"review": response, "validation": validation}:
            # v9 was published with two wordings for the same invalid
            # placeholder/whole-gap shape. Verify the entire earlier ledger.
            rebuilt = isolate_source_review(validation["candidate"], {**rebuilt_material, "_archived_gap_messages": True})
        if rebuilt != {"review": response, "validation": validation}:
            raise ValueError("Isolated review records, barriers or complete coverage differ from strict revalidation")
        if not validation["diagnostics"]:
            raise ValueError("Partial source review has no recorded validation failure")
        retained = any(response.get(name) for name in ("gap_checks", "findings", "input_contract_checks", "input_projection_checks", "source_input_findings"))
        if (reviewed["status"] == "partial") != retained:
            raise ValueError("Isolated source-review status differs from its independently validated records")
        checks = deepcopy(response["input_contract_checks"])
        scopes = contract_scope_decisions(checks, inventory, files)
        projection_checks = deepcopy(response["input_projection_checks"])
        projections = {identity: {"scope_id": identity, **{k: deepcopy(v) for k, v in row.items() if k != "scope_ids"}}
                       for row in projection_checks for identity in row["scope_ids"]}
        candidates = deepcopy(response["source_input_findings"])
        source_findings = normalize_source_input_findings(candidates, files=files, cfg=cfg,
            raw_annotation=annotation["raw_annotation"], compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    if completed:
        expected_schema = ARCHIVED_SOURCE_REVIEW if archived_v12 else ARCHIVED_V13_SOURCE_REVIEW if archived_v13 else ARCHIVED_V14_SOURCE_REVIEW if archived_v14 else SOURCE_REVIEW_VERSION
        if response.get("schema_version") != expected_schema or response.get("outcome") != "completed":
            raise ValueError("Input-contract acceptance requires the explicit current source-review protocol")
        if material.get("input_contract_binding") != binding or material.get("input_contract_inventory") != inventory:
            raise ValueError("Input-contract source review belongs to another selected bundle or obligation inventory")
        for required in ("input_contract_checks", "input_projection_checks", "source_input_findings"):
            if required not in response:
                raise ValueError("Completed source review omits its required " + required + " table")
        checks = checked_contract_checks(response["input_contract_checks"], inventory=inventory, files=files)
        scopes = contract_scope_decisions(checks, inventory, files)
        projection_checks, projections = checked_projection_checks(response["input_projection_checks"], inventory=inventory, files=files)
        candidates = deepcopy(response["source_input_findings"])
        source_findings = normalize_source_input_findings(candidates, files=files, cfg=cfg,
            raw_annotation=annotation["raw_annotation"], compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])
    elif not isolated:
        checks, scopes, projection_checks, projections, candidates, source_findings = [], {}, [], {}, [], []
    targets = contract_review_targets(contracts=inventory["obligations"], cfg=cfg, mapping=annotation["mapping"])
    core = {"status": reviewed.get("status", "unavailable"), "schema_version": response.get("schema_version"),
        "availability": {key: reviewed.get("availability", {}).get(key) is True for key in ("task", "cfg", "annotation")},
        "partial": bool(material.get("partial", not completed)), "binding": binding, "inventory": inventory,
        "findings": deepcopy(response.get("findings", [])), "checks": checks, "scope_decisions": scopes,
        "projection_checks": projection_checks, "projection_decisions": projections, "contract_targets": targets,
        "source_input_candidates": candidates, "source_input_findings": source_findings,
        "review_validation": deepcopy(validation), "isolation_context": deepcopy(context),
        "validation_barriers": deepcopy((validation or {}).get("validation_barriers", [])),
        "blocked_obligation_ids": deepcopy((validation or {}).get("blocked_obligation_ids", [])),
        "blocked_projection_ids": deepcopy((validation or {}).get("blocked_projection_ids", []))}
    representation_findings = core["findings"]
    if not archived_v12 and not archived_v13:
        from skillflow.document_guided.gap_review import check_gaps, gap_inventory
        core["gap_checks"] = deepcopy(response.get("gap_checks", []))
        if completed:
            view_name = material.get("placeholder_review_view")
            if view_name is None:
                shown = material.get("annotation")
                view_name = ("raw_annotation" if shown is not None and shown == annotation.get("raw_annotation")
                             or not annotation.get("wire_annotation") else "wire_annotation")
            if view_name not in {"wire_annotation", "raw_annotation"} or not isinstance(annotation.get(view_name), dict):
                raise ValueError("Placeholder review requires the selected physical annotation view")
            view = annotation[view_name]
            if material.get("annotation") is not None and material["annotation"] != view:
                raise ValueError("Placeholder review representation differs from selected annotation")
            core["placeholder_review_view"] = view_name
            rows = gap_inventory({"processing_gaps": annotation["mapping"].get("processing_gaps", view.get("processing_gaps", [])),
                                  "annotation": view, "cfg": cfg})
            _, findings, errors = check_gaps(response, rows, files)
            saved = [{key: val for key, val in f.items() if key != "id"} for f in core["findings"]]
            if errors or any(finding not in saved for finding in findings):
                raise ValueError("Whole-instruction or local placeholder source review differs from the selected gaps or is missing its repair finding")
            # The separate CFG repair uses the enclosing instruction as its
            # writable address. Its exact defect is the paired placeholder,
            # whose operation-position finding still goes through both checks.
            scoped_cfg = [f for f in findings if f["domain"] == "cfg"]
            representation_findings = [f for f, normalized in zip(core["findings"], saved, strict=True)
                                       if normalized not in scoped_cfg]
    if not (archived_v12 or archived_v13 or archived_v14):
        from .review_ranges import FindingRanges
        from skillflow.document_guided.sensitivity_entries import ingress_gap_rechecks
        scoped = FindingRanges(inventory, targets, cfg, annotation["raw_annotation"], annotation["mapping"])
        if material.get("revision_rechecks"):
            from skillflow.document_guided.revision_rechecks import checked_retention_targets, pending_retention_findings
            retained = material["revision_rechecks"]
            view = annotation.get("wire_annotation") or annotation["raw_annotation"]
            core["revision_rechecks"] = checked_retention_targets(retained, {"files": files, "annotation": view,
                "target_index": [{"id": key} for row in retained for key in row["targets"]]})
            if pending_retention_findings({"revision_rechecks": retained}, checks, core["findings"]):
                raise ValueError("An unresolved retained processing objection is missing from the source review.")
        if completed or isolated:
            # An ingress gap is a source classification limitation, never a model-created
            # exemption from checking an actual argument or response.
            selected = annotation.get("wire_annotation") or annotation["raw_annotation"]
            gaps = annotation["mapping"].get("processing_gaps", selected.get("processing_gaps", []))
            sites = [{"id": key} for key in [
                *("annotation:" + json_pointer("ir_semantics", ir) for ir in selected["ir_semantics"]),
                *("annotation:" + json_pointer("processing_gaps", i) for i in range(len(selected.get("processing_gaps", [])))),
                *scoped.cfg_sites.values()]]
            expected = ingress_gap_rechecks({"cfg": cfg, "target_index": sites,
                "processing_gaps": gaps,
                "sensitivity_entry_gaps": annotation["mapping"].get("sensitivity_entry_gaps", [])}, bind=True)
            authored = [{k: v for k, v in f.items() if k != "id"} for f in core["findings"] if "sensitivity_entry_gap_id" in f]
            if sorted(map(canonical_sha256, expected)) != sorted(map(canonical_sha256, authored)):
                raise ValueError("Reviewed ingress findings differ from the selected source gap identities or evidence")
            if not isolated:
                for check in checks:
                    for finding in representation_findings:
                        hits = scoped.conflicts(check, finding)
                        if hits:
                            raise ValueError("Accepted input-contract scope conflicts with a finding at its operation or CFG location: "
                                             + str(finding["target_ids"]) + " " + str(hits))
                scoped.source_consistency(source_findings, representation_findings, mapping=annotation["mapping"], cfg=cfg)
                core["validation_barriers"] = scoped.barriers(core["findings"])
    elif not isolated:
        check_contract_finding_consistency(checks, representation_findings, targets)
        check_source_input_finding_consistency(source_findings, representation_findings, mapping=annotation["mapping"], cfg=cfg)
    return core


def build_input_contract_review(*, files, cfg, annotation, review=None, review_material=None):
    """Seal complete expected coverage and local decisions for selected material."""
    core = _build_core(files=files, cfg=cfg, annotation=annotation,
        reviewed=deepcopy(review or {"status": "unavailable", "review": None}), material=review_material or {})
    return _seal_core(core, VERSION)


def _seal_core(core, version):
    complete = core["status"] == "complete" and not core["partial"] and all(core["availability"].values()) and core["inventory"]["available"]
    value = {"schema_version": version, **core["binding"], "review_sha256": canonical_sha256(core),
        "review_core": core, "review_status": core["status"], "source_review_complete": complete, "checks": core["checks"]}
    return {**value, "receipt_sha256": canonical_sha256(value)}


def checked_input_contract_review(value, *, files, cfg, annotation, archived_v12=False, archived_v13=False, archived_v14=False):
    """Recheck saved identity, scope coverage and references without solving."""
    if not isinstance(value, dict):
        raise TypeError("Input-contract review receipt must be an object")
    fields = {"schema_version", "source_sha256", "cfg_sha256", "annotation_sha256", "contracts_sha256", "obligations_sha256",
        "review_sha256", "review_core", "review_status", "source_review_complete", "checks", "receipt_sha256"}
    version = ARCHIVED_RECEIPT if archived_v12 else ARCHIVED_V13_RECEIPT if archived_v13 else ARCHIVED_V14_RECEIPT if archived_v14 else VERSION
    if set(value) != fields or value.get("schema_version") != version:
        raise ValueError("Unsupported input-contract review receipt")
    if value["receipt_sha256"] != canonical_sha256({key: row for key, row in value.items() if key != "receipt_sha256"}):
        raise ValueError("Input-contract review receipt digest mismatch")
    binding = _binding(files, cfg, annotation)
    if any(value[key] != digest for key, digest in binding.items()):
        raise ValueError("Input-contract review receipt belongs to another selected bundle")
    core = value["review_core"]
    if not isinstance(core, dict) or type(core.get("partial")) is not bool or not isinstance(core.get("availability"), dict):
        raise ValueError("Input-contract source-review coverage is malformed")
    if set(core["availability"]) != {"task", "cfg", "annotation"} or any(type(item) is not bool for item in core["availability"].values()):
        raise ValueError("Input-contract source-review availability is malformed")
    response = {"schema_version": core.get("schema_version"), "outcome": "completed", "findings": core.get("findings", []),
        "input_contract_checks": core.get("checks", []), "input_projection_checks": core.get("projection_checks", []),
        "source_input_findings": core.get("source_input_candidates", [])}
    if not archived_v12 and not archived_v13:
        response["gap_checks"] = core.get("gap_checks", [])
    checked = _build_core(files=files, cfg=cfg, annotation=annotation, archived_v12=archived_v12, archived_v13=archived_v13, archived_v14=archived_v14,
        reviewed={"status": core.get("status"), "availability": core["availability"], "review": response,
                "validation": core.get("review_validation"), "isolation_context": core.get("isolation_context")},
        material={"partial": core["partial"], "placeholder_review_view": core.get("placeholder_review_view"),
              **({"revision_rechecks": core["revision_rechecks"]} if core.get("revision_rechecks") else {}),
              "input_contract_binding": binding, "input_contract_inventory":
            input_contract_review_inventory(cfg=cfg, raw_annotation=annotation["raw_annotation"],
                compiled=annotation["compiled_annotation"], mapping=annotation["mapping"])})
    if _seal_core(checked, version) != value:
        raise ValueError("Input-contract source-review decisions, inventory or completion differ from the selected bundle")
    return deepcopy(value)
