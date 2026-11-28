"""Passive source-grounding audit of this fresh run's accepted initial Task."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    task_path, result_path = RUN / "task/task.json", RUN / "task/result.json"
    task = json.loads(task_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "complete"
    assert task["task_sha256"] == result["task_ref"]["task_sha256"]
    references = []
    rows = [("purpose", task["purpose"])]
    rows += [("requirements/" + r["id"], r) for r in task["requirements"]]
    rows += [("issues/" + r["id"], r) for r in task["issues"]]
    for owner, row in rows:
        for index, ref in enumerate(row["evidences"]):
            path = RUN / "source/inputs/package" / ref["file"].removeprefix("skill/")
            lines = path.read_text(encoding="utf-8").splitlines()
            references.append({"owner": owner, "index": index, **ref, "source_file_sha256": sha(path),
                "valid_range": 1 <= ref["start_line"] <= ref["end_line"] <= len(lines)})
    assert all(r["valid_range"] for r in references)
    known = {r["id"] for r in task["requirements"]}
    assert len(known) == len(task["requirements"])
    assert all(set(i["requirement_ids"]) <= known for i in task["issues"])
    notes = [
        {"id": "source-supported-coverage", "status": "supported_in_manual_source_check",
         "detail": "The 46 requirements cover setup, GA4 custom and predefined/high-level reports, realtime, metadata, Search Console, URL normalization/filtering/bulk lookup, indexing/removal/inspection and batch outcomes, save/load/list/latest operations, and the Markdown summary workflow. The listed metric/dimension defaults, save overrides, member pairing and empty-list conditions were checked against the cited frozen documentation and implementation. This is a scoped manual assessment, not semantic equivalence or completeness proof."},
        {"id": "report-contract-implementation-divergence", "status": "correctly_retained_source_conflict",
         "requirement_ids": ["ga4-custom-report-filters", "ga4-custom-report-order"], "issue_id": "report-options-ignored",
         "detail": "The source reference promises filters and sort order, while reports.ts destructures filters/orderBy and omits both from the request. Task retains the documented obligations and explicitly says the supplied implementation does not fulfill them. Its resolved issue means the Task baseline is chosen, not that the Skill error is fixed. Later mapping/review must not mark these obligations fulfilled using existing response fields alone.",
         "source_refs": [{"file": "skill/references/api-reference.md", "start_line": 35, "end_line": 43}, {"file": "skill/scripts/src/api/reports.ts", "start_line": 77, "end_line": 100}]},
        {"id": "latest-operation-source-divergence", "status": "correctly_retained_source_conflict",
         "requirement_ids": ["result-latest"], "issue_id": "latest-operation-match",
         "detail": "Task preserves selection by the specified operation. The implementation uses a filename substring, which can match a different operation sharing that prefix. This is a concrete source/implementation divergence rather than a reason to widen the Task to any matching payload.",
         "source_refs": [{"file": "skill/references/api-reference.md", "start_line": 394, "end_line": 403}, {"file": "skill/scripts/src/core/storage.ts", "start_line": 155, "end_line": 170}]},
        {"id": "top-pages-unresolved-has-source-conflict", "status": "grounded_unresolved",
         "issue_id": "search-page-ranking", "requirement_ids": ["search-top-pages", "search-overview", "search-seo-page-performance"],
         "detail": "The reference says top pages by impressions; the SEO workflow and direct help say clicks. The query construction supplies page grouping and rowLimit=100 without an explicit ranking selector. Task records both sources and retains the expressly clicks-based SEO obligation. Settling the shared helper/overview ranking needs an authoritative source choice, not an assumption about unquoted SDK defaults."},
        {"id": "keyword-device-unresolved-has-granularity-conflict", "status": "grounded_unresolved",
         "issue_id": "keyword-device-granularity", "requirement_ids": ["search-keyword-analysis"],
         "detail": "The keyword workflow says queries with device breakdown, but implementation independently requests query-grouped and device-grouped reports. Task states the precise missing relation: per-query device breakdown versus two independent summaries. The declared source must settle that relation before the corresponding association can be preserved precisely."},
        {"id": "summary-and-storage-obligations-retained", "status": "supported_in_manual_source_check",
         "requirement_ids": ["analysis-summary", "result-auto-save", "result-save-locations", "result-save-wrapper"],
         "detail": "Task retains the Markdown summary obligation, default saving with explicit overrides, combined saves for comparison/high-level URL workflows, category/path behavior and metadata wrapper. No Markdown writer appears in the supplied TypeScript source; downstream CFG coverage must account for the natural-language step instead of declaring the requirement fulfilled merely because API calls or JSON writes are processed."},
        {"id": "limit-zero-not-decided-by-task", "status": "downstream_precision_check",
         "requirement_ids": ["ga4-custom-report-limit"],
         "detail": "Task correctly says to honor the supplied limit. The implementation's truthy spread drops zero. Task does not declare SDK zero behavior; a later source finding must distinguish the concrete omitted value from an unproved claim that the omission changes external service results.",
         "source_refs": [{"file": "skill/scripts/src/api/reports.ts", "start_line": 84, "end_line": 100}]},
        {"id": "field-level-output-scope-remains-a-mapping-obligation", "status": "downstream_precision_check",
         "requirement_ids": ["ga4-field-metadata", "indexing-inspect", "structured-analysis-results", "result-save-wrapper"],
         "detail": "These Task statements name output categories and some fields but are not themselves field-complete dependency contracts. For example metadata includes a full-response variant and URL inspection includes additional explicit index-state fields in the source type/construction. Task-correspondence and reviewed processing must explain preserved versus unnecessary field scopes; citation validity alone cannot justify dropping unmentioned fields or demanding every source field."},
    ]
    value = {"kind": "fresh-initial-task-source-audit", "snapshot": "accepted_initial_task_before_whole_chain_source_review",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"task_file": str(task_path.relative_to(ROOT)), "task_file_sha256": sha(task_path),
            "task_declared_sha256": task["task_sha256"], "task_schema_version": task["schema_version"],
            "source_sha256": task["source_sha256"], "result_file_sha256": sha(result_path),
            "accepted_call": result["accepted_call"], "accepted_response_file_sha256": sha(RUN / "task" / result["accepted_call"] / "response.json"),
            "delivery_audit_file_sha256": sha(OUT / "task-source-delivery.json")},
        "counts": {"requirements": len(task["requirements"]), "issues": len(task["issues"]),
            "issue_resolutions": dict(Counter(i["resolution"] for i in task["issues"])),
            "source_reference_occurrences": len(references),
            "unique_source_spans": len({(r["file"], r["start_line"], r["end_line"]) for r in references}),
            "referenced_files": len({r["file"] for r in references}), "invalid_reference_ranges": 0},
        "source_reference_checks": references, "requirements": task["requirements"], "issues": task["issues"],
        "audit_findings": notes, "conclusion": "No definite contradiction in the extracted Task obligations was identified by this scoped source check. Two unresolved issues have concrete source-level grounds. Known source implementation mismatches remain obligations to report, not evidence that they were repaired.",
        "limitations": ["Valid references and a completed extraction do not establish full semantic correctness or minimal field demand.",
            "The initial Task may be replaced by the single permitted semantic repair; preserve this snapshot and separately bind the final selected Task.",
            "No source review, processing, propagation or DOE conclusion is inferred from this Task audit."]}
    (OUT / "task-source-audit-initial.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    c = value["counts"]
    text = ["# Initial accepted Task source audit", "", value["conclusion"], "",
        f"The initial Task has {c['requirements']} requirements and {c['issues']} issues ({c['issue_resolutions']}). All {c['source_reference_occurrences']} reference occurrences locate real source spans; they cover {c['unique_source_spans']} distinct spans across {c['referenced_files']} files. Source-reference validity is not semantic proof.", "",
        "This snapshot binds task.json " + value["binding"]["task_file_sha256"] + " and declared Task identity " + task["task_sha256"] + ". It is the accepted initial Task, before whole-chain review or any semantic repair.", ""]
    text += ["- " + n["id"] + ": " + n["detail"] for n in notes]
    text += ["", "The independent Task input audit confirms byte-identical delivery of all 16 frozen files with source_files as the only data payload and revision=null. No CFG, annotation or backend artifacts supplied the Task's input.", "", *value["limitations"]]
    (OUT / "task-source-audit-initial.en.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print(json.dumps(value["counts"]))


if __name__ == "__main__":
    main()
