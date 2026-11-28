"""Passive closure report from this fresh run's saved artifacts only."""
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


def main():
    terminal, selection = read(RUN / "result.json"), read(RUN / "selection.json")
    controller, replay = read(RUN / "controller-finished.json"), read(RUN / "replay-check.json")
    initial_cfg, revised_cfg = read(RUN / "graph/initial.json")["cfg"], read(RUN / "graph/revision.json")["cfg"]
    selected_task, revised_task = read(RUN / selection["task"]["path"]), read(RUN / "revision/task/task.json")
    compiled_path = RUN / "annotation/audit/compiled-response.json"
    compiled = read(compiled_path)
    processing = read(RUN / "steps/processing/value.json")
    processing_result = read(RUN / "steps/processing/result.json")
    processing_audit = read(OUT / "processing-selected-initial-audit.json")
    revision_graph_audit = read(OUT / "cfg-accepted-revision-initial-audit.json")
    inventory = read(OUT / "source-physical-inventory.json")
    review = read(RUN / "review/result.json")
    process_path = next((RUN / "transport/revision-processing").glob("*/attempt-001/process.json"))
    failed_process = read(process_path)
    source_final = [{**file, "current_sha256": sha(RUN / "source/inputs/package" / file["path"]),
                     "unchanged": sha(RUN / "source/inputs/package" / file["path"]) == file["sha256"]}
                    for file in inventory["files"]]
    bindings = {}
    for name in ["selection.json", "result.json", "analysis-finished.json", "controller-finished.json", "replay-check.json",
                 "graph/initial.json", "graph/selected.json", "graph/revision.json", "task/task.json", "revision/task/task.json",
                 "annotation/manifest.json", "annotation/inputs/references.json", "annotation/audit/compiled-response.json",
                 "annotation/audit/raw-annotation.json", "annotation/audit/wire-annotation.json", "annotation/audit/compilation-map.json",
                 "steps/processing/value.json", "steps/processing/result.json", "steps/revision-graph/result.json",
                 "review/result.json", "steps/revision-processing/calls/a001/call.json", str(process_path.relative_to(RUN)).replace("\\", "/")]:
        bindings[name] = sha(RUN / name)
    selected_bindings = [{"kind": kind, **reference, "actual_file_sha256": sha(RUN / reference["path"]),
                          "matches_selection": sha(RUN / reference["path"]) == reference["sha256"]}
                         for kind, reference in selection.items()]
    no_artifact_names = ["records.json", "propagation-result.json", "demand-result.json", "doe-result.json", "input-contract-review.json"]
    generated_files = [p for p in RUN.rglob("*") if p.is_file() and not any(part in {"implementation-snapshot", "source"} for part in p.relative_to(RUN).parts)]
    recorded_artifact_matches = {word: [str(p.relative_to(RUN)) for p in generated_files if word in p.name.lower()]
                                for word in ["record", "propagation", "demand", "doe", "input-contract-review"]}

    def closed_site_mapping(kind):
        new = {(row["source_site"]["file"], row["source_site"]["line"]): [ir["instruction_id"] for ir in row["primary_instructions"]]
               for row in revision_graph_audit[kind]}
        return [{**row, "final_selected_instruction_id": row["instruction_id"],
                 "unselected_revision_instruction_ids": new[(row["source_site"]["file"], row["source_site"]["line"])],
                 "coverage_status": "generated_in_selected_partial_annotation_propagation_not_run",
                 "recorded_processing_status": None, "reached_status": "not_measured", "record_reference": None}
                for row in processing_audit[kind]]

    remote, saves = closed_site_mapping("remote_site_mapping"), closed_site_mapping("save_site_mapping")
    source_unmodeled = sorted(g["instruction_id"] for g in compiled["processing_gaps"] if g.get("origin") == "source" and g.get("unmodeled"))
    validation_unmodeled = sorted(g["instruction_id"] for g in compiled["processing_gaps"] if g.get("origin") == "validation")
    notes = [
        {"id": "failed-before-backend", "detail": "The controller terminated at revision-processing after its native CLI exceeded the 2700-second process limit without a complete final answer. No revision processing value, revised annotation, rereview, propagation or DOE result was produced. The recorded failure is a process deadline, not an established connection timeout; this audit does not infer the provider-side reason for the unfinished answer."},
        {"id": "final-selection-is-initial-material", "detail": "selection.json retains the initial Task, initial 679-IR CFG and initial partial annotation. graph/selected.json is byte-identical to graph/initial.json. The accepted 58-requirement revised Task and accepted 770-IR revised CFG remain unselected repair candidates; their improved structures must not be reported as the final analyzed material."},
        {"id": "selected-fragment-counts", "detail": "The final selected annotation contains 633 modeled IR, two source-unmodeled IR (ir_395, ir_402) and 44 validation-isolated IR, covering all 679 CFG identities. Its 54 gap records comprise ten source-origin records (two unmodeled and eight ordinary limitations) plus 44 validation records. These are representation counts, not instructions processed by propagation."},
        {"id": "physical-source-coverage-is-not-record-coverage", "detail": "The selected CFG/partial annotation represents all 13 physical remote API sites and all 25 physical saveResult sites. There are no recorded propagation outcomes for them because the run stopped earlier. Recorded coverage is unmeasured, not a measured zero-of-13 or zero-of-25 result; no source boundary is certified as reached, safe or unnecessary."},
        {"id": "source-mismatches-survive-in-final-selection", "detail": "The selected initial processing still double-wraps bulk dimension objects at ir_173; all 25 physical save summaries write the raw result without the actual metadata wrapper/dynamic save address. Normal URL helper calls and higher child acquisitions use local tool summaries without establishing the child's occurrence-specific normal network effect. Direct remote calls omit the authenticated receiver relation, and summary operations are absent from the selected CFG. The source review identified several of these problems, but the incomplete repair supplies no selected fix."},
        {"id": "task-improvements-not-final-selected", "detail": "The revised candidate fixes standalone realtime scope, full-property metadata preservation and the empty-bulk save conflict, but the final selected Task remains the original 46-requirement interpretation. Both versions retain documented filters/orderBy duties despite their actual omission in the Skill request, and retain the row-limit obligation without claiming unknown SDK zero semantics."},
        {"id": "revision-graph-improvements-have-no-processing-evidence", "detail": "The accepted revision candidate adds separate report/bulk map coordinates, documentation-level summary read/compose/write, and distinct module dependency routes with explicit cache/state obligations. No completed revised processing answer exists, so these changes have no new executable annotation, verified field demand or propagation result. In particular the earlier bulk double-wrap and save-wrapper problems cannot be declared repaired."},
        {"id": "review-and-replay-do-not-establish-doe", "detail": "The initial source review retained independently valid records and routed the existing shared repair after structural correction exhaustion. Its partial status is not a completed whole-chain contract approval. The controller's sole replay matched with zero new native markers, reproducing the failed lifecycle; replay agreement is not source-semantic correctness or successful minimization."},
        {"id": "no-deletion-or-necessity-results", "detail": "No demand preparation, input assessment, deletion-impact result or DOE comparison was emitted. This run establishes no deletable input, no non-excess result, and no absence of DOE. Missing output artifacts must not be converted into zero findings or safe conclusions."},
    ]
    counts = {
        "source_files": len(source_final), "source_files_unchanged": sum(file["unchanged"] for file in source_final),
        "selected_task_requirements": len(selected_task["requirements"]), "revised_candidate_task_requirements": len(revised_task["requirements"]),
        "selected_cfg_blocks": len(initial_cfg["blocks"]), "selected_cfg_ir": sum(len(block["instructions"]) for block in initial_cfg["blocks"].values()),
        "revised_candidate_cfg_blocks": len(revised_cfg["blocks"]), "revised_candidate_cfg_ir": sum(len(block["instructions"]) for block in revised_cfg["blocks"].values()),
        "selected_modeled_ir": len(compiled["ir_semantics"]), "selected_source_unmodeled_ir": len(source_unmodeled),
        "selected_validation_isolated_ir": len(validation_unmodeled), "selected_gap_records": len(compiled["processing_gaps"]),
        "selected_gap_origin_counts": dict(Counter(g.get("origin") for g in compiled["processing_gaps"])),
        "selected_annotation_demands": len(compiled["demands"]), "selected_annotation_contracts": len(compiled["input_contracts"]),
        "remote_physical_sites_represented": len(remote), "save_physical_sites_represented": len(saves),
        "recorded_remote_sites_processed": None, "recorded_save_sites_processed": None,
        "propagation_processed_ir": None, "input_assessment_count": None, "doe_comparison_count": None,
    }
    report = {
        "kind": "fresh-ga4-source-coverage-closure-audit", "snapshot": "controller_closed_failed_before_propagation",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "run_status": terminal["status"], "failed_stage": terminal["stage"], "controller_finished_at": controller["finished_at"],
        "source_declared_sha256": selected_task["source_sha256"], "implementation_sha256": inventory["implementation_sha256"],
        "selected_bindings": selected_bindings, "artifact_file_sha256": bindings,
        "selected_task_declared_sha256": selected_task["task_sha256"], "revision_task_declared_sha256": revised_task["task_sha256"],
        "selected_graph_equals_initial": (RUN / "graph/selected.json").read_bytes() == (RUN / "graph/initial.json").read_bytes(),
        "compiled_annotation_task_matches_selected": compiled["task_ref"]["task_sha256"] == selected_task["task_sha256"],
        "processing_value_matches_preserved_initial_audit": sha(RUN / "steps/processing/value.json") == processing_audit["binding"]["selected_value_file_sha256"],
        "compiled_semantic_ids_match_processing_value": set(compiled["ir_semantics"]) == set(processing["ir_semantics"]),
        "counts": counts, "selected_source_unmodeled_ids": source_unmodeled, "selected_validation_isolated_ids": validation_unmodeled,
        "recorded_processing_state": "not_run", "record_coverage_measurement": "unavailable_not_measured_zero",
        "artifact_availability": {"revision_processing_value": (RUN / "steps/revision-processing/value.json").exists(),
                                  "revision_processing_response": (RUN / "steps/revision-processing/calls/a001/response.json").exists(),
                                  "revision_annotation": (RUN / "revision/annotation").exists(),
                                  "named_root_artifacts": {name: (RUN / name).exists() for name in no_artifact_names},
                                  "generated_artifact_filename_matches": recorded_artifact_matches,
                                  "terminal_stage_records": terminal["stages"]},
        "failed_native_process": {"path": str(process_path.relative_to(RUN)), **failed_process},
        "review_status": review["status"], "review_reason": review["reason"], "controller_replay": replay,
        "remote_site_mapping": remote, "save_site_mapping": saves, "final_source_file_checks": source_final,
        "audit_findings": notes,
        "preserved_prior_audits": {name: sha(OUT / name) for name in ["source-physical-inventory.json", "task-source-audit-initial.json",
                                      "cfg-accepted-initial-audit.json", "processing-a001-preliminary.json", "processing-selected-initial-audit.json",
                                      "review-a001-source-comparison.json", "task-source-audit-revision-initial.json", "cfg-accepted-revision-initial-audit.json"]},
        "limitations": ["This is a source/representation and artifact-closure audit, not a fresh execution or propagation/DOE analysis.",
                        "No compiler, validator, model, Skill, tests, backend or replay was invoked by this helper. The sole replay result is read from the controller's saved receipt.",
                        "Initial and revised artifacts remain preserved; no failed result is rewritten or promoted to accepted semantic evidence."]}
    (OUT / "final-source-coverage.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# GA4 source coverage at closure", "", "The run failed in revision-processing before propagation or DOE. There is no measured backend source-boundary coverage or minimization result.", "",
             f"Run: `{RUN.name}`. Controller closed at `{controller['finished_at']}`.",
             f"Native revision-processing status: `{failed_process['status']}`, elapsed {failed_process['elapsed_seconds']:.6f} seconds. Sole replay: `{replay['status']}`, {replay['new_native_markers']} new native markers.", "",
             "| Material | Final selected | Unselected repair candidate |", "|---|---|---|",
             f"| Task requirements | {len(selected_task['requirements'])} | {len(revised_task['requirements'])} |",
             "| CFG | 268 blocks / 679 IR | 302 blocks / 770 IR |",
             "| Processing | 633 modeled + 2 source-unmodeled + 44 validation-isolated | No completed answer |",
             "| Propagation / demand / DOE | Not run; no result records | Not run |", "",
             f"Selected CFG file SHA-256: `{sha(RUN / 'graph/initial.json')}`.",
             f"Unselected revised CFG file SHA-256: `{sha(RUN / 'graph/revision.json')}`.",
             f"Selected compiled annotation file SHA-256: `{sha(compiled_path)}`.", "",
             "All 16 frozen source files remain byte-identical. All 13 physical remote calls and 25 physical saveResult sites have generated selected representations. Their processed/reached counts are unavailable; this is not a measured 0/13 or 0/25 result.", ""]
    lines += [f"- **{note['id']}**: {note['detail']}" for note in notes]
    lines += ["", "## Physical source mappings", "", "The revision IDs below belong to an unselected candidate; every row has no propagation record.", "",
              "| Physical site | Final selected IR | Unselected revision IR |", "|---|---|---|"]
    lines += [f"| {row['source_site']['file']}:{row['source_site']['line']} | {row['final_selected_instruction_id']} | {', '.join(row['unselected_revision_instruction_ids'])} |" for row in remote + saves]
    lines += ["", *report["limitations"]]
    (OUT / "final-source-coverage.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": terminal["status"], "stage": terminal["stage"], "counts": counts,
                      "all_selected_bindings_match": all(b["matches_selection"] for b in selected_bindings),
                      "source_unchanged": all(f["unchanged"] for f in source_final), "replay": replay}))


if __name__ == "__main__":
    main()
