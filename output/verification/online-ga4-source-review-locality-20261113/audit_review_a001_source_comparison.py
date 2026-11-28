"""Compare fresh unaccepted review with source audit; no runtime analysis."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"


def read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value) if isinstance(value, str) else value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    call = RUN / "review/calls/review/a001"
    response, validation = read(call / "response.json"), read(call / "validation.json")
    material = read(RUN / "review/inputs.json")
    task = read(RUN / "task/task.json")
    maps = [
        {"audit_issue": "bulk-dimension-double-wrapping-persists", "finding_indices": [3], "coverage": "overlap_not_exact_detection",
         "assessment": "Finding 3 requests explicit traversal coordinates and preserves fixed bulk dimension constants. It does not explicitly identify ir_173's existing {name:object} nested-name construction. Keep the concrete processing mismatch open until selected repaired semantics can be examined."},
        {"audit_issue": "all-save-wrappers-and-path-identities-still-unrepresented", "finding_indices": [12], "coverage": "explicitly_detected",
         "assessment": "The finding targets all 25 caller save operations and identifies raw result writes, absent serialized wrappers, per-invocation paths/settings/clock, and absent binding to the standalone saveResult function. Its suggestion also covers nested default saves."},
        {"audit_issue": "receiver-and-interface-evidence-limit", "finding_indices": [8], "coverage": "receiver_explicit_interface_necessity_partly_checked",
         "assessment": "Finding 8 targets all 13 direct remote SDK sites and separates the authenticated receiver from request arguments. Raw contract checks also reject whole-date-range necessity at some report calls. This is useful review evidence but not an accepted review or a full interface-necessity proof."},
        {"audit_issue": "loop-boundaries-improved-but-normal-helper-substitution-remains", "finding_indices": [9, 11], "coverage": "post_error_and_console_explicit_normal_helper_open",
         "assessment": "Finding 9 distinguishes successful acquisition followed by local failure from rejection, and finding 11 requests per-member console messages. Neither explicitly rejects the normal branch's local tool summary as a replacement for its child network effect. The normal helper interface checks remain accepted in this raw response."},
        {"audit_issue": "former-child-gaps-now-local-tools-plus-storage", "finding_indices": [12], "coverage": "nested_save_explicit_normal_network_open",
         "assessment": "Nested default save reconstruction is requested. The 25 high-level child helper summaries' normal network request/response effects are not explicitly identified as missing. An accepted child interface contract does not establish that external effect coverage."},
        {"audit_issue": "summary-still-an-explicit-gap", "finding_indices": [4, 13], "coverage": "explicitly_detected",
         "assessment": "The review distinguishes the prose summary requirement from absent executable consumer/write coordinates and rejects independent results-management example outputs as completed-analysis provenance."},
        {"audit_issue": "validation-isolation-extends-beyond-boundary-nodes", "finding_indices": [6, 7], "coverage": "cache_and_clocks_explicit_other_isolation_still_recorded",
         "assessment": "The review identifies cache-slot writes and all eight separate clock acquisitions. Other validation-isolated defaults, projections and runtime identity records remain structural facts; not every isolated record is separately described by an ordinary finding."},
    ]
    task_notes = [
        {"finding_index": 0, "assessment": "source_supported_scope_omission", "requirement_ids": ["ga4-live-snapshot"],
         "source_refs": [{"file": "skill/references/api-reference.md", "start_line": 119, "end_line": 147}],
         "detail": "The reference independently exposes getActiveUsers, getRealtimeEvents and getRealtimePages. The selected Task requirement is explicitly scoped to a real-time snapshot, even though its evidence cites the three independent APIs. That does not expressly preserve each standalone invocation obligation."},
        {"finding_index": 0, "assessment": "source_supported_output_scope_omission", "requirement_ids": ["ga4-field-metadata"],
         "source_refs": [{"file": "skill/references/api-reference.md", "start_line": 185, "end_line": 193}],
         "detail": "The reference says getPropertyMetadata returns the full metadata response. The Task asks for dimensions, metrics or both with API name/UI name/description, without explicitly preserving the full response. Those requirements are not interchangeable for field-level minimization."},
        {"finding_index": 1, "assessment": "source_supported_unresolved_conflict_omission", "requirement_ids": ["result-auto-save", "bulk-page-metrics"],
         "source_refs": [{"file": "skill/scripts/src/api/bulk-lookup.ts", "start_line": 153, "end_line": 188}, {"file": "skill/SKILL.md", "start_line": 55, "end_line": 64}],
         "detail": "When normalized URLs are empty, the implementation returns rows=[] and rowCount=0 before the remote request and save branch even with save=true. The Task automatic-save-scope issue resolves only explicit suppression and combined saves. It does not acknowledge this separate successful enabled-save no-file path."},
    ]
    helper_checks = []
    for index, check in enumerate(response["input_contract_checks"]):
        target = material["input_contract_obligation_targets"].get(check["obligation_id"], "")
        if any(fragment in target for fragment in ["ir_418/", "ir_428/", "ir_547/segments/0/cases/0/", "ir_566/segments/0/cases/0/"]):
            helper_checks.append({"record_index": index, "target": target, "check": check})
    source_files = sorted({reference["file"] for note in task_notes for reference in note["source_refs"]})
    source_bindings = {file: sha(RUN / "source/inputs/package" / file.removeprefix("skill/")) for file in source_files}
    result = {
        "kind": "fresh-unaccepted-review-source-comparison", "snapshot": "review_a001_before_full_structural_correction",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"review_response_file_sha256": sha(call / "response.json"), "review_validation_file_sha256": sha(call / "validation.json"),
                    "review_candidate_declared_sha256": validation["candidate_sha256"], "validation_status": validation["status"],
                    "task_file_sha256": sha(RUN / "task/task.json"), "task_declared_sha256": task["task_sha256"],
                    "processing_value_file_sha256": sha(RUN / "steps/processing/value.json"),
                    "initial_cfg_file_sha256": sha(RUN / "graph/initial.json"), "fresh_source_file_sha256": source_bindings},
        "counts": {"findings": len(response["findings"]), "contract_check_records": len(response["input_contract_checks"]),
                   "contract_record_statuses_raw_unaccepted": dict(Counter(check["status"] for check in response["input_contract_checks"])),
                   "source_input_findings": len(response["source_input_findings"]), "diagnostics": len(validation["diagnostics"])},
        "source_audit_comparison": maps, "task_source_reassessment": task_notes,
        "normal_helper_checks_raw_unaccepted": helper_checks,
        "findings": response["findings"],
        "limitations": ["This comparison is not an acceptance, new validation, repair instruction or backend result. The controller alone selects and routes the eventual review.",
                        "Raw accepted contract statuses are not usable verified contracts while candidate validation has failed or overlapping findings conflict.",
                        "The initial Task audit did not identify these three Task scope/conflict omissions; this fresh source comparison adds those supported limitations without rewriting the earlier snapshot.",
                        "No claim is made that repair will resolve the identified source mismatches. Final selected artifacts must be audited separately."]}
    (OUT / "review-a001-source-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Initial review a001 compared with source audit", "", "The candidate is structurally invalid; a002 is not selected by this audit.", "",
             f"Response file SHA-256: `{sha(call / 'response.json')}`.", "",
             "16 ordinary findings, 275 contract records (239 raw accepted, 35 rejected, 1 unresolved), no source-input finding records; seven recorded structural diagnostics.", ""]
    lines += [f"- **{row['audit_issue']}** ({row['coverage']}): {row['assessment']}" for row in maps]
    lines += ["", "## Task source reassessment", ""]
    lines += [f"- Finding {row['finding_index']}: {row['detail']}" for row in task_notes]
    lines += ["", *result["limitations"]]
    (OUT / "review-a001-source-comparison.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
