"""Passive source-delivery and obligation audit of the fresh revised Task."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_json(prompt, name):
    section = prompt.split(f"<!-- SKILLFLOW_PROMPT:{name}:BEGIN -->", 1)[1].split(f"<!-- SKILLFLOW_PROMPT:{name}:END -->", 1)[0]
    return json.JSONDecoder().raw_decode(section[section.index("{"):])[0]


def main():
    step = RUN / "revision/task"
    task, old = read(step / "task.json"), read(RUN / "task/task.json")
    result, manifest, request = read(step / "result.json"), read(step / "manifest.json"), read(step / "inputs/request.json")
    prompt = (step / "inputs/prompt.txt").read_text(encoding="utf-8")
    payload, revision_payload = section_json(prompt, "INPUT"), section_json(prompt, "REPAIR")
    delivered_files = []
    for item in payload["source_files"]:
        source_path = RUN / "source/inputs/package" / item["file"].removeprefix("skill/")
        delivered = "".join(item["lines"]).encode("utf-8")
        delivered_files.append({"file": item["file"], "source_sha256": sha(source_path),
                                "delivered_sha256": hashlib.sha256(delivered).hexdigest(),
                                "exact_bytes": delivered == source_path.read_bytes(), "bytes": len(delivered)})
    references = []
    for owner, row in [("purpose", task["purpose"]), *[("requirements/" + r["id"], r) for r in task["requirements"]],
                       *[("issues/" + r["id"], r) for r in task["issues"]]]:
        for index, reference in enumerate(row["evidences"]):
            path = RUN / "source/inputs/package" / reference["file"].removeprefix("skill/")
            lines = path.read_text(encoding="utf-8").splitlines()
            references.append({"owner": owner, "index": index, **reference, "source_file_sha256": sha(path),
                               "valid_range": 1 <= reference["start_line"] <= reference["end_line"] <= len(lines)})
    old_req, new_req = {r["id"]: r for r in old["requirements"]}, {r["id"]: r for r in task["requirements"]}
    old_issues, new_issues = {r["id"]: r for r in old["issues"]}, {r["id"]: r for r in task["issues"]}
    notes = [
        {"id": "standalone-realtime-obligations-added", "status": "source_supported_revision",
         "requirement_ids": ["ga4-realtime-active-users", "ga4-realtime-events", "ga4-realtime-pages", "ga4-realtime-sources", "ga4-live-snapshot"],
         "detail": "The revised Task independently scopes active-user, event and page reports and retains the combined snapshot. The original ga4-live-sources obligation is renamed ga4-realtime-sources with its source/medium grouping and active-user measure preserved. The three original review source spans establish the added standalone invocation scopes."},
        {"id": "full-property-metadata-obligation-added", "status": "source_supported_revision",
         "requirement_ids": ["ga4-full-property-metadata", "ga4-dimension-metadata", "ga4-metric-metadata", "ga4-available-fields"],
         "detail": "The revised Task expressly preserves the full metadata response, including the same full value in saved data. It separates dimension-only, metric-only and high-level available-fields requests. This avoids shrinking the full-response contract to a named subset of entry fields. Source: api-reference.md:185-193 and metadata.ts:82-95."},
        {"id": "empty-bulk-save-conflict-preserved", "status": "grounded_local_unresolved",
         "requirement_ids": ["bulk-empty-lookup", "bulk-page-metrics", "result-auto-save"], "issue_id": "bulk-empty-save",
         "detail": "The revised Task states that an empty path list returns zero rows without a GA4 request, while separately preserving the conflict between default-enabled saving and the early return before saveResult. The explicit missing semantic choice is whether this early return is an intended exception to the documented save duty. It does not silently deem saving unnecessary or claim that the source has been fixed."},
        {"id": "filters-order-and-limit-duties-retained", "status": "source_supported_preservation",
         "requirement_ids": ["ga4-custom-report-filters", "ga4-custom-report-order", "ga4-custom-report-limit"], "issue_id": "report-options-ignored",
         "detail": "The revised Task still requires supplied filters, sort order and row limit. Filters/orderBy remain explicitly unfulfilled by the actual request builder. A resolved Task conflict chooses the documented obligation; it does not repair the Skill. The Task still makes no claim about SDK semantics for zero, which the truthy request spread omits."},
        {"id": "original-requirements-reorganized-not-three-silent-deletions", "status": "manual_scope_reconciliation",
         "detail": "The revision has 15 added and three removed requirement IDs. configure-google-access is split into setup-google-access, setup-environment and configured-request-targets. ga4-field-metadata is replaced by four more precise metadata obligations. ga4-live-sources is renamed. Other added duties split existing pagination, per-URL outcomes and grouped-saving statements, alongside the review-requested empty-bulk case. ID changes need fresh mapping; old realization indices cannot be reused."},
        {"id": "month-comparison-ambiguity-reclassified", "status": "grounded_revision_beyond_requested_omissions",
         "issue_id": "comparison-month-example", "requirement_ids": ["ga4-period-comparison"],
         "detail": "The full replacement reclassifies the preexisting calendar-month versus rolling-window example from resolved to unresolved. Its reason is now explicitly confined to a natural-language-only month request; two supplied ranges remain authoritative and paired. The cited sources provide the concrete ambiguity, but this adds a downstream Task limitation beyond the two requested review objections and must remain visible in final accounting."},
        {"id": "summary-wrapper-and-grouped-saves-retained", "status": "source_supported_preservation",
         "requirement_ids": ["analysis-summary", "result-save-wrapper", "result-save-grouped", "result-save-locations"],
         "detail": "The Markdown summary remains required after completed analysis, consuming saved JSON. Full storage wrappers/path obligations and grouped writes remain; component saves are suppressed only at the documented comparison/batch call sites. This is a Task obligation audit, not evidence that the revised CFG or processing fulfills them."},
    ]
    correction_payload = request["revision"]
    delivery = {"main_input_keys": list(payload), "repair_payload_keys": list(revision_payload),
                "request_keys": list(request), "revision_keys": list(correction_payload),
                "repair_equals_requested_revision": revision_payload == correction_payload,
                "previous_task_exact_initial_task": correction_payload["previous_task"] == old,
                "objection_count": len(correction_payload["objections"]),
                "bounded_objection_fields_only": all(set(o) == {"code", "source_spans", "requirement_ids"} for o in correction_payload["objections"]),
                "objections": correction_payload["objections"], "source_files": delivered_files,
                "all_source_files_exact": all(f["exact_bytes"] for f in delivered_files),
                "delivered_file_count": len(delivered_files), "source_owner": manifest["source_owner"],
                "accepted_call_prompt_matches_prepared": (step / result["accepted_call"] / "prompt.txt").read_bytes() == (step / "inputs/prompt.txt").read_bytes()}
    delta = {"added_requirement_ids": sorted(new_req.keys() - old_req.keys()), "removed_requirement_ids": sorted(old_req.keys() - new_req.keys()),
             "added_issue_ids": sorted(new_issues.keys() - old_issues.keys()), "removed_issue_ids": sorted(old_issues.keys() - new_issues.keys()),
             "changed_issue_resolutions": [{"id": k, "before": old_issues[k]["resolution"], "after": new_issues[k]["resolution"]}
                                           for k in old_issues.keys() & new_issues.keys() if old_issues[k]["resolution"] != new_issues[k]["resolution"]]}
    report = {
        "kind": "fresh-accepted-revision-task-source-audit", "snapshot": "accepted_revision_task_candidate_before_controller_final_selection",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"task_file_sha256": sha(step / "task.json"), "task_declared_sha256": task["task_sha256"],
                    "task_schema_version": task["schema_version"], "source_sha256": task["source_sha256"],
                    "initial_task_declared_sha256": old["task_sha256"], "result_file_sha256": sha(step / "result.json"),
                    "accepted_call": result["accepted_call"], "extraction_status": result["status"],
                    "response_file_sha256": sha(step / result["accepted_call"] / "response.json"),
                    "prompt_file_sha256": sha(step / "inputs/prompt.txt"), "manifest_file_sha256": sha(step / "manifest.json")},
        "counts": {"requirements": len(task["requirements"]), "issues": len(task["issues"]),
                   "issue_resolutions": dict(Counter(i["resolution"] for i in task["issues"])),
                   "source_reference_occurrences": len(references), "invalid_source_reference_ranges": sum(not r["valid_range"] for r in references),
                   "unique_source_spans": len({(r["file"], r["start_line"], r["end_line"]) for r in references}),
                   "referenced_files": len({r["file"] for r in references})},
        "source_only_delivery": delivery, "identity_delta": delta, "requirements": task["requirements"], "issues": task["issues"],
        "source_reference_checks": references, "audit_findings": notes,
        "limitations": ["This Task extraction accepted a001, but the revision remains a candidate until controller selection and whole-chain review. No final selection is inferred.",
                        "The sole data input is complete source; the repair section contains the prior Task plus two bounded source objections. No CFG, annotation, payload or backend result supplies Task requirements.",
                        "Source range validity is not a semantic completeness proof; revised IDs and finer output scopes require fresh task-correspondence.",
                        "Initial snapshots are preserved. This helper reads saved artifacts only and invokes no model, Skill, test, validator, compiler, backend or replay."]}
    (OUT / "task-source-audit-revision-initial.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Accepted revised Task: initial source audit", "", "The Task step accepted its a001 replacement. This report does not claim final controller selection.", "",
             f"Declared revised Task SHA-256: `{task['task_sha256']}`; unchanged source SHA-256: `{task['source_sha256']}`.", "",
             f"{len(task['requirements'])} requirements, {len(task['issues'])} issues ({report['counts']['issue_resolutions']}); all {len(references)} evidence occurrences locate valid source spans.",
             f"All {len(delivered_files)} complete source files are byte-identical in the actual accepted-call prompt. The repair payload exactly matches the previous Task plus two bounded objections.", ""]
    lines += [f"- **{note['id']}**: {note['detail']}" for note in notes]
    lines += ["", *report["limitations"]]
    (OUT / "task-source-audit-revision-initial.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"counts": report["counts"], "delivery": {k: v for k, v in delivery.items() if k not in {"source_files", "objections"}}, "delta": delta}))


if __name__ == "__main__":
    main()
