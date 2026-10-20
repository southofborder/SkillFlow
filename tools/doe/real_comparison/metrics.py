"""Observed request and workflow costs; unknown counters stay unknown."""
from __future__ import annotations

from datetime import datetime
from collections import Counter
import json
import math
from pathlib import Path
from statistics import median

from .execution import usage_summary
from .protocol import SCHEMA, sha256, write_json


def _read(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _epoch(value):
    if isinstance(value, (float, int)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    return None


def combine_usage(summaries):
    rows, missing, conflicts = {}, set(), set()
    fields = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
              "reasoning_output_tokens", "total_tokens")
    for summary in summaries:
        missing.update(summary.get("missing_requests", []))
        conflicts.update(summary.get("conflicting_response_ids", []))
        for key, value in summary.get("by_response_id", {}).items():
            if key in rows and rows[key] != value:
                conflicts.add(key)
            rows[key] = value
    totals = {field: sum(r[field] for r in rows.values())
              if rows and not missing and not conflicts and all(type(r.get(field)) is int for r in rows.values())
              else None for field in fields}
    return {"by_response_id": rows, "totals": totals, "response_count": len(rows),
            "missing_requests": sorted(missing), "conflicting_response_ids": sorted(conflicts),
            "basis": "Observed per-response counters only; deduplicated across constituent requests; unknown remains unknown."}


def preparation_usage(run_dir, *, session_ids, since):
    """Export only attributed per-response counters from explicit prep sessions.

    The captured window is a reported subtotal, not a claim that all historical
    design work or the still-running supervisor's final response was observed.
    """
    from tools.doe.direct_baseline import find_receipt
    run = Path(run_dir)
    start = _epoch(since)
    fields = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens",
              "reasoning_output_tokens", "total_tokens")
    rows, conflicts, sessions = {}, set(), []
    for session_id in session_ids:
        path = find_receipt(session_id)
        ids = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("type") != "token_usage_record":
                continue
            payload = row.get("payload", {})
            if payload.get("thread_id") != session_id or (_epoch(row.get("timestamp")) or 0) < start:
                continue
            response_id = payload.get("response_id")
            if not response_id:
                continue
            raw = payload.get("usage", {})
            values = {f: raw.get(f) if type(raw.get(f)) is int else None for f in fields}
            if response_id in rows and rows[response_id] != values:
                conflicts.add(response_id)
            rows[response_id] = values
            ids.add(response_id)
        sessions.append({"session_id": session_id, "reported_response_ids": sorted(ids)})
    observed = combine_usage([{"by_response_id": rows, "conflicting_response_ids": sorted(conflicts)}])
    record = {"schema_version": SCHEMA, "since": since, "sessions": sessions,
              "observed": observed, "complete_preparation_cost": None,
              "limitations": "A windowed reported subtotal only. Earlier research, unregistered sessions, unreceipted work, and the live supervisor's final response may be missing. No hidden reasoning or session-cumulative counters are exported.",
              "model_calls": 0}
    write_json(run / "preparation-cost.json", record)
    return record


def _active_seconds(record):
    value = record.get("active_seconds")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError("A human active-time record must be a finite nonnegative number or unknown")
    return value


def _human_imports(run, relative, folder, people, expected_role):
    """Only manifested, unchanged, explicitly human submissions are evidence."""
    result, seen = [], set()
    manifest = _read(run / relative, {"records": []})
    for entry in manifest.get("records", []):
        path = (run / entry["path"]).resolve()
        if (not path.is_relative_to((run / folder).resolve()) or not path.is_file()
                or sha256(path) != entry.get("sha256") or entry.get("import_source") != "human_user_submission"):
            raise ValueError("A human work record changed, escaped its directory or lacks a human import")
        identity = (entry["path"], entry["sha256"])
        if identity in seen:
            continue
        seen.add(identity)
        record = _read(path)
        person = people.get(record.get("reviewer_id"), {})
        if (person.get("human") is not True or person.get("role") != expected_role
                or entry.get("reviewer_id") != record.get("reviewer_id")):
            raise ValueError("Human work cost requires the exact registered human role and imported reviewer")
        _active_seconds(record)
        result.append((entry, record))
    return result


def _duration_summary(records, *, planned, covered=None):
    values = [_active_seconds(record) for record in records]
    known = [v for v in values if v is not None]
    coverage = len(records) if covered is None else covered
    return {"planned_records": planned, "observed_records": len(records), "covered_planned_units": coverage,
            "uncollected_planned_units": max(0, planned - coverage) if planned is not None else None,
            "reported_duration_records": len(known), "unknown_duration_records": len(values) - len(known),
            "observed_active_seconds_subtotal": sum(known) if known else None,
            "reported_record_time_seconds": sum(known) if values and len(known) == len(values) else None,
            "planned_record_time_seconds": sum(known) if planned is not None and coverage == planned
                    and len(known) == len(values) and values else None}


def human_cost_summary(run_dir):
    """Separate source confirmation, scoring, practical review and adjudication.

    Imported personal attestations are study evidence, not personhood proof.
    Missing time is never filled from record count, elapsed wall time or a cap.
    """
    from .assessment import (CONFIRMATION, validate_reference_evidence, validate_grade,
                             verify_human_reference_freeze, validate_timed_record, second_review_sample)
    from .results import verify_output_freeze
    run = Path(run_dir)
    roster = _read(run / "human-roster.json", {"reviewers": []})
    people = {r["reviewer_id"]: r for r in roster.get("reviewers", [])}
    references = _human_imports(run, "approvals/import-manifest.json", "approvals", people, "reference_verifier")
    reference_units = set()
    for entry, record in references:
        case_id = record.get("case_id")
        if not isinstance(case_id, str) or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in case_id):
            raise ValueError("Unsafe human reference cost identity")
        path = run / "references" / (case_id + ".json")
        reference = validate_reference_evidence(run, _read(path))
        if (entry.get("case_id") != case_id or record.get("human") is not True or record.get("approved") is not True
                or record.get("role") != "reference_verifier" or record.get("confirmation") != CONFIRMATION
                or not record.get("attestation_id") or not record.get("attested_at")
                or record.get("reference_sha256") != sha256(path)
                or record.get("source_sha256") != reference.get("source_sha256")):
            raise ValueError("A source-confirmation cost record differs from its actual source/reference attestation")
        reference_units.add((case_id, record["reviewer_id"]))
    grades = _human_imports(run, "grades/import-manifest.json", "grades", people, "reference_verifier")
    timed = _human_imports(run, "review/import-manifest.json", "review/submissions", people, "timed_reviewer")
    adjudications = _human_imports(run, "review/adjudications/import-manifest.json", "review/adjudications", people, "reference_verifier")
    if grades or timed or adjudications:
        verify_output_freeze(run)
    if grades:
        verify_human_reference_freeze(run)
    score_map = {r["candidate_id"]: r for r in _read(run / "review/private-scoring-map.json", {"assignments": []})["assignments"]}
    primary, secondary, score_units = [], [], set()
    for entry, record in grades:
        role, workflow_id = record.get("scoring_role", "primary"), record.get("workflow_id")
        mapped = score_map.get(record.get("candidate_id"), {})
        unit = (workflow_id, role)
        if (role not in {"primary", "secondary"} or unit in score_units or mapped.get("workflow_id") != workflow_id
                or entry.get("workflow_id") != workflow_id or entry.get("scoring_role") != role
                or (role == "primary" and record["reviewer_id"] != mapped.get("primary_reviewer_id"))
                or (role == "secondary" and record["reviewer_id"] == mapped.get("primary_reviewer_id"))
                or record.get("confirmation") != "I personally checked this candidate against the source reference."
                or not record.get("submission_id") or not record.get("attested_at")):
            raise ValueError("Human scoring cost must match one prespecified independent human score")
        ref_path = run / "references" / (mapped["case_id"] + ".json")
        output = _read(run / "workflows" / workflow_id / "result.json")
        if (record.get("reference_sha256") != sha256(ref_path)
                or record.get("candidate_sha256") != (output.get("answer_sha256") or output.get("artifact_manifest_sha256"))):
            raise ValueError("Human scoring cost is bound to a different candidate or reference")
        validate_grade(record, _read(ref_path))
        score_units.add(unit)
        (primary if role == "primary" else secondary).append(record)
    known_secondary = {r["workflow_id"] for r in primary if r["judgment"] != "satisfies_reference"}
    secondary_planned = None
    if len(primary) == 264:
        known_secondary.update(second_review_sample([{**r, "candidate_id": r["workflow_id"]} for r in primary]))
        from .execution import assess_request_protocol
        for record in primary:
            workflow_id = record["workflow_id"]
            result = _read(run / "workflows" / workflow_id / "result.json")
            dispatched = [p for p in (run / "mailbox/requests").glob(workflow_id + "_q*") if (p / "dispatch.json").exists()]
            if (result.get("status") in {"failed", "budget_exhausted", "context_limit", "protocol_violation", "not_reviewable", "timeout"}
                    or not dispatched or any(assess_request_protocol(p)["status"] != "conformant" for p in dispatched)):
                known_secondary.add(workflow_id)
        secondary_planned = len(known_secondary)
    assignments = {a["assignment_id"]: a for a in _read(run / "review/private-assignment-map.json", {"assignments": []})["assignments"]}
    timed_by_id = {}
    for entry, record in timed:
        identifier = record.get("assignment_id")
        assigned = assignments.get(identifier, {})
        if (identifier in timed_by_id or entry.get("assignment_id") != identifier
                or record.get("case_id") != assigned.get("case_id") or record.get("human") is not True
                or record.get("reviewer_id") != assigned.get("reviewer_id")
                or record.get("attestation") != "I personally performed this timed review without consulting this case reference or another method answer."
                or not record.get("started_at") or not record.get("finished_at")
                or record.get("final_quality") != "pending_independent_adjudication"
                or record.get("status") not in {"finished", "timeout", "abandoned"}):
            raise ValueError("A practical human work record differs from its fixed independent timed assignment")
        if _active_seconds(record) is not None:
            validate_timed_record(record, assigned, [p["reviewer_id"] for p in people.values() if p.get("role") == "reference_verifier"])
        timed_by_id[identifier] = (entry, record)
    quality_by_id = {}
    for entry, record in adjudications:
        identifier = record.get("assignment_id")
        prior = timed_by_id.get(identifier)
        if (not prior or identifier in quality_by_id or entry.get("assignment_id") != identifier
                or record.get("reviewer_id") == prior[1]["reviewer_id"]
                or record.get("submission_sha256") != prior[0]["sha256"]
                or record.get("quality") not in {"correct", "incorrect", "unresolved"}
                or record.get("human_verified") is not True or not record.get("attested_at")
                or not record.get("evidence") or not record.get("reason")):
            raise ValueError("Timed quality cost requires an independent human judgment bound to the exact submitted record")
        quality_by_id[identifier] = record
    timed_rows = []
    for identifier, (entry, record) in timed_by_id.items():
        seconds, status = _active_seconds(record), record["status"]
        quality = quality_by_id.get(identifier, {}).get("quality", "pending_independent_adjudication")
        within_cap = (status == "finished" and seconds is not None and seconds <= 1800 and quality == "correct")
        timed_rows.append({"assignment_id": identifier, "case_id": record["case_id"], "method": assignments[identifier]["method"],
                           "reviewer_id": record["reviewer_id"], "status": status, "quality": quality,
                           "active_seconds": seconds, "right_censored": status != "finished", "active_time_cap_seconds": 1800,
                           "completion_time_lower_bound_seconds": seconds if status != "finished" else None,
                           "correct_within_cap": within_cap if quality not in {"unresolved", "pending_independent_adjudication"} and seconds is not None else None})
    methods = {}
    for method in ("skillflow", "audit", "chain"):
        group = [r for r in timed_rows if r["method"] == method]
        successful = [r["active_seconds"] for r in group if r["correct_within_cap"] is True]
        methods[method] = {"planned_records": 24, "observed_records": len(group),
                           "statuses": dict(Counter(r["status"] for r in group)),
                           "qualities": dict(Counter(r["quality"] for r in group)),
                           "correct_within_cap": sum(r["correct_within_cap"] is True for r in group),
                           "right_censored_records": sum(r["right_censored"] for r in group),
                           "correct_finished_active_seconds_median": median(successful) if successful else None}
    all_records = [r for _, r in references + grades + timed + adjudications]
    counts_complete = (len(reference_units) == 60 and len(primary) == 264 and secondary_planned is not None
                       and known_secondary.issubset({r["workflow_id"] for r in secondary})
                       and len(timed_rows) == 72 and len(quality_by_id) == 72)
    unknown_times = sum(_active_seconds(r) is None for r in all_records)
    reference_summary = _duration_summary([r for _, r in references], planned=60, covered=len(reference_units))
    reference_summary["scope_limit"] = "Personal source-reference confirmations only. Drafting, reconciliation and unreported preparation time are not inferred from these records."
    secondary_summary = _duration_summary(secondary, planned=secondary_planned,
                                         covered=sum(r["workflow_id"] in known_secondary for r in secondary))
    secondary_summary.update(required_so_far=len(known_secondary), required_workflows=sorted(known_secondary),
                             subset_finalized=len(primary) == 264,
                             subset_rule="All errors/disputes and technical/protocol failures plus seeded 20 percent of initial passes after all 264 primary scores.")
    known_times = [_active_seconds(r) for r in all_records if _active_seconds(r) is not None]
    return {"status": "awaiting_actual_human_records" if not all_records else "partial_human_records" if not counts_complete
            else "record_counts_complete_time_unknown" if unknown_times else "reported_record_counts_and_times_complete",
            "source_reference_work": reference_summary,
            "scoring_primary": _duration_summary(primary, planned=264), "scoring_secondary": secondary_summary,
            "practical_timed_review": {**_duration_summary([r for _, r in timed], planned=72), "rows": timed_rows, "by_method": methods,
                "censoring_limit": "Timeouts are censored at the 1,800-second cap. Abandonment is censored at its reported active time under the same cap; it is never replaced with 1,800 seconds or treated as a completed faster review.",
                "efficiency_conclusion": "Not inferred. Fast incorrect/unresolved work and censored records are not successful low-cost review; quality noninferiority requires separate analysis."},
            "independent_timed_quality_adjudication": _duration_summary([r for _, r in adjudications], planned=72),
            "unmanifested_adjudication_files": len([p for p in (run / "review/adjudications").glob("*.json") if p.name != "import-manifest.json"])
                    - len({entry["path"] for entry, _ in adjudications}),
            "observed_active_seconds_subtotal": sum(known_times) if known_times else None,
            "planned_record_time_seconds": sum(known_times) if counts_complete and not unknown_times else None,
            "complete_study_human_time_seconds": None, "currency": None,
            "identity_limit": "Roles and personal attestations are explicit submitted study records, not independently established personhood or proof of attention.",
            "duration_limit": "Only optional submitted active_seconds values are summed. Missing time remains unknown; no duration is inferred from record count, wall timestamps or monetary rates.",
            "model_calls": 0}


def cost_ledger(run_dir):
    from .corrigenda import _root, resolve_grading_run, lineage_human_cost
    run = _root(run_dir)
    current_grading = resolve_grading_run(run)
    calls, workflows = [], []
    for directory in sorted((run / "mailbox/requests").glob("*")):
        request = _read(directory / "request.json")
        if request is None:
            continue
        dispatch = _read(directory / "dispatch.json", {})
        receipt = _read(directory / "receipt.json", {})
        response = _read(directory / "response.json", {})
        timing = receipt.get("timing", {})
        created, dispatched = _epoch(request.get("created_at")), _epoch(dispatch.get("dispatched_at"))
        calls.append({"request_id": request["request_id"], "workflow_id": request["workflow_id"],
                      "mode": request["mode"], "actual_child_request": bool(dispatch),
                      "accepted": response.get("accepted"), "runtime": receipt.get("observed_configuration"),
                      "usage_by_response_id": receipt.get("usage", {}).get("by_response_id", {}),
                      "response_duration_seconds": timing["duration_ms"] / 1000
                          if isinstance(timing.get("duration_ms"), (float, int)) else None,
                      "response_started_at": timing.get("started_at"), "response_completed_at": timing.get("completed_at"),
                      "dispatch_wait_seconds": max(0, dispatched - created)
                          if created is not None and dispatched is not None else None,
                      "dispatch_wait_basis": "Request publication to dispatch-record time; includes supervisor scheduling and record delay.",
                      "protocol_assessment": _read(directory / "protocol-assessment.json"),
                      "stopped": _read(directory / "stop.json")})
    schedule = _read(run / "schedule.json", {"main": [], "reviews": []})
    planned = schedule["main"] + schedule["reviews"]
    registrations = {p.parent.name: _read(p) for p in (run / "workflows").glob("*/registration.json")}
    for item in planned + [r for key, r in sorted(registrations.items()) if key not in {i["workflow_id"] for i in planned}]:
        key = item["workflow_id"]
        directory = run / "workflows" / key
        result = _read(directory / "result.json", {})
        state = _read(directory / "state.json", {})
        started, finished = _epoch(state.get("started_at")), _epoch(result.get("finished_at"))
        attempt_results = [_read(p) for p in sorted((directory / "attempts").glob("*/worker-result.json"))]
        local = [r.get("timing", {}).get("local_processing_seconds") for r in attempt_results]
        workflow_calls = [c for c in calls if c["workflow_id"] == key]
        workflows.append({"workflow_id": key, "case_id": item.get("case_id"), "method": item.get("method"),
                          "kind": item.get("kind"), "repeat": item.get("repeat"),
                          "status": result.get("status", "not_started"),
                          "actual_child_requests": sum(c["actual_child_request"] for c in workflow_calls),
                          "usage": usage_summary(run, key),
                          "workflow_elapsed_seconds": finished - started
                              if finished is not None and started is not None else None,
                          "deterministic_processing_seconds": sum(local)
                              if local and all(isinstance(v, (float, int)) for v in local) else None,
                          "recorded_attempts": len(attempt_results)})
    enhancements = []
    for item in schedule["reviews"]:
        primary = item.get("original_workflow_id")
        matched = [w for w in workflows if w["workflow_id"] in {item["workflow_id"], primary}]
        elapsed = [w["workflow_elapsed_seconds"] for w in matched]
        enhancements.append({"workflow_id": item["workflow_id"], "original_workflow_id": primary,
                             "usage_original_plus_review": combine_usage([w["usage"] for w in matched]),
                             "additive_workflow_seconds": sum(elapsed)
                                 if len(matched) == 2 and all(isinstance(v, (float, int)) for v in elapsed) else None,
                             "basis": "The original answer and fixed review together, not the review alone; no extra actual request is created by this accounting view."})
    probe_dir = run / "transport-inspection/proposed-cli-probe"
    probe_launch = _read(probe_dir / "launch.json")
    probe_receipt = _read(probe_dir / "receipt.json", {})
    probe_usage = {**probe_receipt.get("usage", {}),
                   "missing_requests": [] if probe_receipt.get("usage", {}).get("by_response_id") else ["authorized_cli_feasibility_probe"]}
    total = combine_usage([usage_summary(run)] + ([probe_usage] if probe_launch else []))
    output = {"schema_version": SCHEMA, "requests": calls, "workflows": workflows,
              "enhanced_original_plus_review_cost": enhancements,
              "engineering_cli_probe": {"launch_present": bool(probe_launch), "status": _read(probe_dir / "process-result.json", {}).get("status", "running" if probe_launch else "not_started"),
                                        "receipt": probe_receipt or None, "formal_workflow": False},
              "target_usage": total,
              "unknowns": "Absent response receipts or fields remain unknown. No session-cumulative counters, character estimates or billing amounts are substituted.",
              "study_preparation_cost": {"status": "separate_not_fully_observed", "tokens": None,
                                         "observed_record": _read(run / "preparation-cost.json"),
                                         "reason": "Target-child receipts do not account for all orchestrator, acquisition, screening and reference-preparation work. Any separately captured prep window is a reported subtotal, not a complete historical total."},
              "human_cost": human_cost_summary(current_grading),
              "grading_epoch_human_work_history": lineage_human_cost(run) if current_grading != run else None,
              "target_cost_identity": "Original closed target cohort only; copied grading workspaces never create another target charge.",
              "billing_amount": None, "model_calls": 0}
    write_json(run / "cost-ledger.json", output)
    return output
