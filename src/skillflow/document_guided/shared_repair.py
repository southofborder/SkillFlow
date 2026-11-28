"""An explicit decision for the existing single shared semantic repair round."""
from skillflow.common.recording import canonical_sha256
from .failed_stage_material import checked_structural_failure


IDENTITY = "skillflow-shared-repair-decision-v2"
FRAGMENTS = frozenset({"processing", "task-correspondence", "sensitivity"})
FIXED_UPSTREAM = frozenset({"task", "flow", "graph"})
DOWNSTREAM_REQUESTS = FRAGMENTS | {"review", "revision/review"} | {"revision-" + key for key in FRAGMENTS}


def fixed_findings(findings):
    """Keep each objection's bound review ID and exact source/edit locations."""
    return [{key: row[key] for key in ("id", "domain", "target_ids", "source_refs")}
            for row in findings if row["domain"] in {"cfg", "task"}]


def repair_decision(*, files, values, errors, reviewed, selected, graph_facts_only=False, processing_gaps=(),
                    normalize_blocks=True, check_occurrences=True, fixed_upstream=False):
    findings = (reviewed.get("review") or {}).get("findings", [])
    actionable = ([row for row in findings if row["domain"] == "annotation" and row.get("owner") in FRAGMENTS]
                  if fixed_upstream else findings)
    domains = {row["domain"] for row in actionable}
    reviewed_status = reviewed.get("status")
    review_available = reviewed_status in {"complete", "partial"}
    upstream = {"task", "graph"} <= set(values)
    validation_ids = sorted({row["instruction_id"] for row in processing_gaps
                             if row.get("origin") == "validation" and row.get("validation_errors")})
    validation_repair = bool(validation_ids) and upstream and "processing" in values
    usual = bool(actionable) and (selected is not None
        or upstream and bool(domains & {"cfg", "task"})
        or upstream and bool(FRAGMENTS & set(values)) and any(
            row["domain"] == "annotation" and row.get("owner") in FRAGMENTS for row in actionable))
    failure = errors.get("graph", {})
    evidence = failure.get("evidence")
    bound = (failure.get("status") == "structural_failure"
        and checked_structural_failure(evidence, stage="graph", files=files))
    missing_cfg = "graph" not in values
    prerequisites = {"task", "flow"} <= set(values)
    recovery = not fixed_upstream and missing_cfg and prerequisites and bound
    scoped_blocked = False
    if graph_facts_only and (recovery or "cfg" in domains and "graph" in values):
        from .graph_steps import rejected_facts, repair_input, repair_slots
        candidate = rejected_facts(evidence) if recovery else values["graph"]["value"]
        plan = repair_input(files=files, previous=candidate, accepted=not recovery, normalize_blocks=normalize_blocks,
                            check_occurrences=check_occurrences,
                            failure_evidence=evidence if recovery else None,
                            findings=[row for row in findings if row["domain"] == "cfg"])
        if plan is None or not repair_slots(plan["plan"]):
            scoped_blocked = True
            recovery = False
            domains.discard("cfg")
            usual = usual and bool(domains)
    barriers = []
    if not review_available and not validation_repair:
        barriers.append("No completed or locally retained source review is available for shared repair.")
    if scoped_blocked:
        barriers.append("The graph findings or rejected draft define no source-bound editable slot.")
    if missing_cfg and not fixed_upstream:
        if not prerequisites:
            barriers.append("Missing-CFG repair requires the accepted source-only Task and flow document.")
        if not bound:
            barriers.append("No source-bound terminal structural rejection of the current CFG is available; a request failure or capability gap does not authorize another sample.")
    eligible = (review_available and (usual or recovery)) or validation_repair
    if fixed_upstream and not all(values.get(key, {}).get("value") is not None for key in FIXED_UPSTREAM):
        eligible = False
        barriers.append("A downstream-only repair requires the verified inherited Task, flow and CFG.")
    if validation_repair:
        domains.add("annotation")
    if eligible and recovery:
        domains.add("cfg")
    return {"identity": IDENTITY, "eligible": eligible, "budget_rounds": 1,
        "mode": (("missing_cfg_slots" if graph_facts_only else "missing_cfg_rebuild") if eligible and recovery
                 else "reviewed_bundle" if eligible else "not_admitted"),
        "domains": sorted(domains) if eligible else [], "review_status": reviewed_status,
        "processing_validation_targets": validation_ids,
        "processing_validation_sha256": canonical_sha256(list(processing_gaps)),
        "finding_count": len(findings), "accepted_stages": sorted(values),
        "source_sha256": canonical_sha256(files), "review_sha256": canonical_sha256(reviewed),
        "graph_failure_sha256": canonical_sha256(failure) if failure else None,
        "graph_failure_material_sha256": evidence.get("material_sha256") if isinstance(evidence, dict) else None,
        **({"deferred_cfg": scoped_blocked} if graph_facts_only else {}),
        **({"fixed_upstream": sorted(FIXED_UPSTREAM), "fixed_upstream_findings": fixed_findings(findings)}
           if fixed_upstream else {}),
        "barriers": barriers,
        "basis": (("A required CFG has source-bound writable fact slots. Use the existing shared round only for those slots."
                  if graph_facts_only else
                  "A required CFG has a verified structural rejection. Spend the existing shared round rebuilding from complete source, accepted flow and rejected evidence; accept no failed value.")
                  if eligible and recovery else "The prior processing validation identifies concrete IR owners; include them in this shared round."
                  if eligible and validation_repair else "Use the existing shared source-review repair policy."
                  if eligible else "No admissible shared repair remains at this decision boundary.")}
