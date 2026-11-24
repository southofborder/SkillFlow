"""Strict record validation and evidenced isolation of a terminal review.

Isolation never repairs a candidate or accepts an invalid record. The complete
inventory and the exact candidate remain in the ledger; usable decisions are
derived from validated records minus explicit conflicts and barriers.
"""
from collections import defaultdict
from copy import deepcopy

from pydantic import TypeAdapter, ValidationError

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _json_object, json_pointer, resolve_pointer
from skillflow.common.validation import StructuralValidationError, schema_error
from skillflow.doe.input_contract_review import (
    ARCHIVED_SOURCE_REVIEW, ARCHIVED_V14_SOURCE_REVIEW, SOURCE_REVIEW_VERSION,
    InputContractCheck, InputScopeCheck, checked_contract_record, _evidence,
    check_contract_finding_consistency,
)
from skillflow.doe.source_input_findings import (
    SourceInputFindingCandidate, normalize_source_input_findings,
    source_operation_targets, _validate_pair, check_source_input_finding_consistency,
)

IDENTITY = "skillflow-source-review-isolation-v1"
TABLES = ("findings", "input_contract_checks", "input_projection_checks", "source_input_findings")


def _finding_model(material):
    from .source_review import ArchivedFragmentSourceFinding, V9FragmentSourceFinding, FragmentSourceFinding
    if material.get("identity") == SOURCE_REVIEW_VERSION:
        return FragmentSourceFinding
    return ArchivedFragmentSourceFinding if material.get("identity") == ARCHIVED_SOURCE_REVIEW else V9FragmentSourceFinding


def checked_finding(value, material, path):
    # Lazy import keeps the public source-review schema and legacy route in one
    # place while sharing exactly the same checks with strict and local paths.
    from .source_review import _check_targets, _check_source
    finding = _finding_model(material).model_validate(value).model_dump(mode="json", exclude_none=True)
    targets = _check_targets(finding["target_ids"], material, path + "/target_ids", domain=finding["domain"])
    _check_source(finding["source_refs"], material, path + "/source_refs")
    partial_target = any(target["domain"] == finding["domain"] and (
        target["kind"] == "stage_failures" or
        finding["domain"] == "annotation" and target["kind"] == "fragments") for target in targets)
    if not material["availability"][finding["domain"]] and not partial_target:
        raise ValueError("The candidate object is absent and remains unreviewed")
    if not any(target["domain"] == finding["domain"] for target in targets):
        raise ValueError("Finding must locate its own domain")
    if any(target["kind"] == "stage_failures" and target["domain"] != finding["domain"] for target in targets):
        raise ValueError("Failed-stage finding domain must match its exact target policy")
    if any(target.get("requires_source") for target in targets) and not finding["source_refs"]:
        raise ValueError("A missing-stage semantic finding requires original source references")
    if finding["domain"] == "annotation":
        owners = {target["owner"] for target in targets if target["domain"] == "annotation"}
        if finding.get("owner") is not None and finding["owner"] not in owners:
            raise ValueError("Finding owner must match an actual annotation target origin")
        if finding.get("owner") is None:
            finding["owner"] = next(owner for owner in
                ("processing", "task-correspondence", "sensitivity") if owner in owners)
    if finding["domain"] == "task":
        if any(target["domain"] != "task" for target in targets):
            raise ValueError("Task findings may target only Task")
        objection = finding["task_objection"]
        _check_source(objection["source_spans"], material, path + "/task_objection/source_spans")
        known = {row["id"] for row in (material.get("task") or {}).get("requirements", [])}
        if not set(objection["requirement_ids"]) <= known:
            raise ValueError("Unknown existing Task requirement")
    return finding


def checked_projection_record(value, inventory, files):
    row = InputScopeCheck.model_validate(value).model_dump(mode="json", exclude_none=True)
    expected = {p["id"] for p in inventory["projections"]}
    if not set(row["scope_ids"]) <= expected:
        raise ValueError("Review projection references an unknown finite scope")
    if row["affected_scope_ids"]:
        raise ValueError("Projection decisions cannot declare input-scope barriers")
    _evidence(row["evidences"], files)
    if row.get("gap"):
        _evidence(row["gap"]["evidences"], files)
    return row


def repair_findings(checks, projections, material):
    result = []
    for check in checks:
        if check["status"] != "accepted":
            result.append({"domain": "annotation", "owner": "processing",
                "target_ids": [material["input_contract_obligation_targets"][check["obligation_id"]]],
                "input_contract_obligation_id": check["obligation_id"],
                "explanation": "Input contract obligation " + check["obligation_id"] + " is " + check["status"] + ": " + check["reason"],
                "source_refs": [{k: e[k] for k in ("file", "start_line", "end_line")} for e in check["evidences"]],
                "suggestion": "Recheck this operation's input contract against the cited source: " + check["reason"]})
    inventory = material["input_contract_inventory"]
    by_projection = {row["id"]: row for row in inventory["projections"]}
    obligations = {row["contract_id"]: row for row in inventory["obligations"] if row["contract_id"] is not None}
    for check in projections:
        if check["status"] != "accepted":
            targets = sorted({material["input_contract_obligation_targets"][obligations[c]["id"]]
                for scope in check["scope_ids"] for c in by_projection[scope]["contract_ids"]})
            result.append({"domain": "annotation", "owner": "processing", "target_ids": targets,
                "input_projection_scope_ids": check["scope_ids"],
                "explanation": "The authored acquisition projection is " + check["status"] + ": " + check["reason"],
                "source_refs": [{k: e[k] for k in ("file", "start_line", "end_line")} for e in check["evidences"]],
                "suggestion": "Recheck the source-backed projection relation without changing actual request operands: " + check["reason"]})
    return result


def isolate_source_review(candidate, material):
    """Validate every record against original material; never run a model."""
    value = _json_object(candidate)
    inventory = material["input_contract_inventory"]
    input_material = material["input_review_material"]
    obligations = {row["id"]: row for row in inventory["obligations"]}
    layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
    projections = {row["id"]: row for row in inventory["projections"]}
    targets = source_operation_targets(cfg=material["cfg"], raw_annotation=input_material["raw_annotation"], mapping=input_material["mapping"]) if input_material["raw_annotation"] is not None and material["cfg"] is not None else {}
    all_ops = {canonical_sha256({"instruction_id": e["instruction_id"], "raw_path": e["raw_path"]}): e
               for entries in targets.values() for e in entries}
    cfg_sites = {ir["id"]: "cfg:" + json_pointer("blocks", bid, "instructions", i)
        for bid, block in (material["cfg"] or {}).get("blocks", {}).items() for i, ir in enumerate(block["instructions"])}
    from skillflow.doe.review_ranges import FindingRanges
    scoped = material.get("identity") == SOURCE_REVIEW_VERSION
    ranges = FindingRanges(inventory, material["input_contract_targets"], material["cfg"],
                          input_material["raw_annotation"], input_material["mapping"]) if scoped else None
    allowed = {row["id"] for row in material["target_index"]}
    records, diagnostics, barriers, conflicts = [], [], [], []
    valid = {table: [] for table in TABLES}
    raw_paths = {table: defaultdict(list) for table in TABLES}
    blocked, blocked_projection = set(), set()

    def refs(entries):
        return sorted({canonical_sha256({"instruction_id": e["instruction_id"], "raw_path": e["raw_path"]}):
            {"instruction_id": e["instruction_id"], "raw_path": deepcopy(e["raw_path"])} for e in entries}.values(), key=canonical_sha256)

    def locate(table, row):
        if not isinstance(row, dict):
            return None
        if table == "source_input_findings":
            entries = targets.get(row.get("target_id")) if isinstance(row.get("target_id"), str) else None
            if entries and row["target_id"] in allowed:
                try:
                    _validate_pair(entries)
                except ValueError:
                    return None
                return refs(entries)
        elif table == "input_contract_checks":
            identity = row.get("obligation_id")
            if isinstance(identity, str) and identity in obligations:
                return [{k: deepcopy(obligations[identity][k]) for k in ("instruction_id", "raw_path")}]
        elif table == "input_projection_checks":
            ids = row.get("scope_ids")
            if isinstance(ids, list) and ids and all(isinstance(i, str) and i in projections for i in ids):
                return sorted({canonical_sha256(projections[i][side]): deepcopy(projections[i][side])
                    for i in ids for side in ("request", "response")}.values(), key=canonical_sha256)
        elif table == "findings":
            ids = row.get("target_ids")
            if isinstance(ids, list) and ids and all(isinstance(i, str) and i in allowed for i in ids):
                if any(i.startswith("task:") or i.startswith("stage:") for i in ids):
                    return None
                selected = []
                for entry in all_ops.values():
                    sites = {site for site, entries in targets.items() if entry in entries}
                    sites.add(cfg_sites[entry["instruction_id"]])
                    if any(a == b or a.startswith(b + "/") or b.startswith(a + "/") for a in ids for b in sites):
                        selected.append(entry)
                if selected:
                    return refs(selected)
        return None

    def barrier(path, code, reason, operation_refs):
        if operation_refs is not None:
            expanded = {canonical_sha256(ref): ref for ref in operation_refs}
            for ref in operation_refs:
                entry = all_ops.get(canonical_sha256(ref))
                if entry is None or entry["value"]["op"] not in {"deliver", "receive"}:
                    continue
                for other in all_ops.values():
                    if other is entry or other["value"]["op"] not in {"deliver", "receive"}:
                        continue
                    try:
                        _validate_pair([entry, other])
                    except ValueError:
                        continue
                    for paired in refs([other]):
                        expanded[canonical_sha256(paired)] = paired
            operation_refs = [expanded[key] for key in sorted(expanded)]
        body = {"record_path": path, "code": code, "reason": reason,
            "resolution": "Correct this recorded review defect and revalidate it against the same selected source, operation and complete inventory.",
            "domain": "all_operations" if operation_refs is None else "operation", "operation_refs": operation_refs or []}
        item = {"id": "review_barrier_" + canonical_sha256(body)[:20], **body}
        if item not in barriers:
            barriers.append(item)

    def failure(path, table, row, error, schema=None, status="invalid"):
        if isinstance(error, StructuralValidationError):
            ds = deepcopy(error.diagnostics)
        elif isinstance(error, ValidationError):
            ds = schema_error(error, candidate=row, schema=schema or {}).diagnostics
            for d in ds:
                d["path"] = path + d["path"]
        else:
            ds = [{"code": "review_record", "path": path, "message": str(error)}]
        diagnostics.extend(ds)
        try:
            original = resolve_pointer(value, path)
        except (ValueError, KeyError, IndexError, TypeError):
            original = row
        records.append({"path": path, "status": status, "record_sha256": canonical_sha256(original), "diagnostics": ds})
        if table == "input_projection_checks":
            ids = row.get("scope_ids") if isinstance(row, dict) else None
            if isinstance(ids, list) and ids and all(isinstance(i, str) and i in projections for i in ids):
                blocked_projection.update(ids)
            else:
                blocked_projection.update(projections)
        else:
            barrier(path, "review_record_" + status, "; ".join(d["message"] for d in ds), locate(table, row))

    gap_protocol = "processing_gap_inventory" in material
    extras = set(value) - {"outcome", *TABLES} - ({"gap_checks"} if gap_protocol else set())
    envelope_ok = value.get("outcome") == "completed" and not extras
    if not envelope_ok:
        failure("" if extras else "/outcome", "envelope", value,
                ValueError("Review requires outcome=completed and only its declared tables; unexpected keys: " + str(sorted(extras))))
    schemas = {"findings": TypeAdapter(_finding_model(material)), "input_contract_checks": TypeAdapter(InputContractCheck),
               "input_projection_checks": TypeAdapter(InputScopeCheck), "source_input_findings": TypeAdapter(SourceInputFindingCandidate)}
    for table in TABLES:
        rows = value.get(table)
        if not isinstance(rows, list):
            failure("/" + table, table, rows, ValueError("A required review table must be present as an array"))
            continue
        if not envelope_ok:
            continue
        for i, row in enumerate(rows):
            path = json_pointer(table, i)
            if table == "input_contract_checks" and isinstance(row, dict) and isinstance(row.get("obligation_id"), str):
                raw_paths[table][row["obligation_id"]].append(path)
            if table == "input_projection_checks" and isinstance(row, dict) and isinstance(row.get("scope_ids"), list):
                for identity in row["scope_ids"]:
                    if isinstance(identity, str):
                        raw_paths[table][identity].append(path)
            try:
                if table == "findings":
                    parsed = checked_finding(row, material, path)
                    if scoped:
                        ranges.resolve(parsed)
                elif table == "input_contract_checks":
                    parsed = checked_contract_record(row, inventory=inventory, files=material["files"],
                        archived_v7=material.get("identity") == ARCHIVED_SOURCE_REVIEW)
                elif table == "input_projection_checks":
                    parsed = checked_projection_record(row, inventory, material["files"])
                else:
                    parsed = schemas[table].validate_python(row).model_dump(mode="json")
                    normalize_source_input_findings([parsed], files=material["files"], cfg=material["cfg"],
                        **input_material, review_targets=material["target_index"])
                valid[table].append((path, parsed))
                if table in {"findings", "source_input_findings"}:
                    raw_paths[table][canonical_sha256(parsed)].append(path)
            except (ValueError, ValidationError) as error:
                failure(path, table, row, error, schemas[table].json_schema())

    # Duplicate identities invalidate every occurrence, including an otherwise
    # well-formed row paired with a malformed duplicate. No winner is chosen.
    for table in TABLES:
        duplicates = {p for paths in raw_paths[table].values() if len(paths) > 1 for p in paths}
        retained = []
        for path, row in valid[table]:
            if path in duplicates:
                failure(path, table, row, ValueError("Duplicate review identity or scope"), status="duplicate")
            else:
                retained.append((path, row))
        valid[table] = retained

    ordinary = [row for _, row in valid["findings"]]
    checks = sorted([row for _, row in valid["input_contract_checks"]], key=lambda r: r["obligation_id"])
    projection_checks = [row for _, row in valid["input_projection_checks"]]
    repair = repair_findings(checks, projection_checks, material)
    findings = ordinary + repair
    gap_findings = []
    gap_checks = []
    gap_errors = []
    if gap_protocol and envelope_ok:
        from .gap_review import check_gaps
        gap_checks, gap_findings, gap_errors = check_gaps(value, material["processing_gap_inventory"], material["files"],
            historical_boundary_diagnostics=material.get("_archived_gap_messages") is True)
        if scoped:
            diagnostics.extend(gap_errors)
        for i, row in enumerate(value.get("gap_checks", []) if isinstance(value.get("gap_checks"), list) else []):
            path = f"/gap_checks/{i}"
            problems = [d for d in gap_errors if d["path"] == path]
            records.append({"path": path, "status": "invalid" if problems else "validated",
                            "record_sha256": canonical_sha256(row), "diagnostics": problems})
        findings.extend(gap_findings)
    if material.get("sensitivity_entry_gaps"):
        from .sensitivity_entries import ingress_gap_rechecks
        findings += ingress_gap_rechecks(material, bind=scoped)
    checked_findings = list(valid["findings"])
    if scoped:
        retained = []
        if material.get("revision_rechecks"):
            from .revision_rechecks import pending_retention_findings
            retained = pending_retention_findings(material, checks, findings)
        findings.extend(retained)
        checked_findings.extend(("/derived_findings", f) for f in repair + retained)
        checked_findings.extend(("/gap_checks", f) for f in gap_findings if f["domain"] != "cfg")
        checked_findings.extend(("/sensitivity_entry_gaps", f) for f in findings if f.get("sensitivity_entry_gap_id"))
    conflict_groups = defaultdict(list)
    for path, check in valid["input_contract_checks"]:
        for finding_path, finding in checked_findings:
            try:
                if scoped:
                    hits = ranges.conflicts(check, finding)
                    if not hits:
                        continue
                    raise ValueError("Accepted input-contract scopes conflict with the finding at "
                                     + ", ".join(finding["target_ids"]) + ": " + ", ".join(hits))
                check_contract_finding_consistency([check], [finding], material["input_contract_targets"])
            except ValueError as error:
                item = {"record_path": path, "finding_path": finding_path, "reason": str(error)}
                if scoped and ranges.resolve(finding):
                    item["scope_ids"] = hits
                else:
                    blocked.add(check["obligation_id"])
                    barrier(path, "input_contract_review_conflict", str(error), locate("input_contract_checks", check))
                conflicts.append(item)
                conflict_groups[(finding_path, tuple(finding["target_ids"]))].append({"record_path": path, "obligation_id": check["obligation_id"],
                    "diagnostic": {"code": "input_contract_review_conflict", "path": path, "message": str(error)}})
    for (finding_path, affected_targets), rows in sorted(conflict_groups.items()):
        diagnostics.append({"code": "input_contract_review_conflict", "path": finding_path,
            "message": "Each listed accepted input-contract scope conflicts with a finding at its operation or CFG location.",
            "context": {"target_ids": list(affected_targets), "conflicting_checks": [
                {key: row[key] for key in ("record_path", "obligation_id")} for row in rows]},
            "audit": {"raw_diagnostics": [row["diagnostic"] for row in rows]}})
    usable_sources = []
    for path, row in valid["source_input_findings"]:
        normalized = normalize_source_input_findings([row], files=material["files"], cfg=material["cfg"], **input_material)
        try:
            if scoped:
                ranges.source_consistency(normalized, [f for _, f in checked_findings],
                                          mapping=input_material["mapping"], cfg=material["cfg"])
            else:
                check_source_input_finding_consistency(normalized, ordinary, mapping=input_material["mapping"], cfg=material["cfg"])
        except ValueError as error:
            failure(path, "source_input_findings", row, error, status="conflict")
            conflicts.append({"record_path": path, "reason": str(error)})
        else:
            usable_sources.append((path, row))
    valid["source_input_findings"] = usable_sources

    by_id = {row["obligation_id"]: row for _, row in valid["input_contract_checks"]}
    coverage = []
    for identity, obligation in obligations.items():
        paths = raw_paths["input_contract_checks"].get(identity, [])
        state = "validated" if identity in by_id else ("duplicate" if len(paths) > 1 else "invalid" if paths else "missing")
        if state != "validated":
            blocked.add(identity)
            if state == "missing":
                path = "/input_contract_checks"
                message = "Input-contract review must cover every expected obligation exactly once; missing " + identity
                diagnostics.append({"code": "review_coverage", "path": path, "message": message})
                barrier(path, "review_coverage", message, locate("input_contract_checks", {"obligation_id": identity}))
        coverage.append({"obligation_id": identity, "scope_ids": [s["id"] for s in layouts[identity]["scopes"]],
                         "status": state, "record_paths": paths})
    projection_coverage = []
    valid_projection = {identity for _, row in valid["input_projection_checks"] for identity in row["scope_ids"]}
    for identity in projections:
        paths = raw_paths["input_projection_checks"].get(identity, [])
        state = "validated" if identity in valid_projection else ("duplicate" if len(paths) > 1 else "invalid" if paths else "missing")
        if state != "validated":
            blocked_projection.add(identity)
            if state == "missing":
                message = "Review scope decisions must cover the exact finite inventory once; missing " + identity
                diagnostics.append({"code": "review_coverage", "path": "/input_projection_checks", "message": message})
                # Missing projection review blocks capability only, not input
                # necessity or the actual acquired result.
        projection_coverage.append({"scope_id": identity, "status": state, "record_paths": paths})
    affected = {canonical_sha256(ref) for b in barriers for ref in b["operation_refs"]}
    global_barrier = any(b["domain"] == "all_operations" for b in barriers)
    for identity, obligation in obligations.items():
        if global_barrier or canonical_sha256({k: obligation[k] for k in ("instruction_id", "raw_path")}) in affected:
            blocked.add(identity)
    for identity, projection in projections.items():
        if global_barrier or any(canonical_sha256(projection[side]) in affected for side in ("request", "response")):
            blocked_projection.add(identity)
    for row in coverage:
        if row["obligation_id"] in blocked and row["status"] == "validated":
            row["status"] = "blocked"
    for row in projection_coverage:
        if row["scope_id"] in blocked_projection and row["status"] == "validated":
            row["status"] = "blocked"
    present_records = {r["path"] for r in records}
    for table, rows in valid.items():
        for path, row in rows:
            if path not in present_records:
                original = value[table][int(path.rsplit("/", 1)[1])]
                records.append({"path": path, "status": "validated", "record_sha256": canonical_sha256(original), "diagnostics": []})
    for i, finding in enumerate(findings):
        finding["id"] = f"F{i + 1:03d}"
    if scoped:
        barriers.extend(ranges.barriers(findings))
    else:
        diagnostics.extend(gap_errors)
    review = {"schema_version": material["identity"], "outcome": "completed", "findings": findings,
        "input_contract_checks": checks, "input_projection_checks": projection_checks,
        "source_input_findings": [row for _, row in valid["source_input_findings"]]}
    if gap_protocol:
        review["gap_checks"] = gap_checks
    validation = {"schema_version": ("skillflow-source-review-isolation-v2" if scoped else IDENTITY), "candidate": deepcopy(value), "candidate_sha256": canonical_sha256(value),
        "binding": deepcopy(material["input_contract_binding"]), "inventory": deepcopy(inventory),
        "records": sorted(records, key=lambda r: r["path"]), "diagnostics": diagnostics,
        "contract_coverage": coverage, "projection_coverage": projection_coverage,
        "validation_barriers": sorted(barriers, key=lambda b: b["id"]), "conflicts": conflicts,
        "blocked_obligation_ids": sorted(blocked), "blocked_projection_ids": sorted(blocked_projection)}
    return {"review": review, "validation": validation}
