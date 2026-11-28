"""Read-only fresh-run audit; no SkillFlow imports or analysis execution."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"


def read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value) if isinstance(value, str) else value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def operations(value, path=()):
    if isinstance(value, dict):
        if value.get("op") in {"call", "write", "deliver", "receive"}:
            yield {"path": list(path), "operation": value}
        for key, child in value.items():
            yield from operations(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from operations(child, (*path, index))


def main():
    step = RUN / "steps/processing"
    result = read(step / "result.json")
    value = read(step / "value.json")
    raw = read(step / "calls/a002/response.json")
    validation = read(step / "calls/a002/validation.json")
    graph_audit = read(OUT / "cfg-accepted-initial-audit.json")
    prior = read(OUT / "processing-a001-preliminary.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    instructions = {ir["id"]: {"block_id": block["block_id"], "block_name": block["block_name"], "instruction": ir}
                    for block in cfg["blocks"].values() for ir in block["instructions"]}
    retained = set(value["ir_semantics"])
    source_gaps = [gap for gap in value["processing_gaps"] if gap.get("unmodeled")]
    source_ids = {gap["instruction_id"] for gap in source_gaps}
    validation_ids = {gap["instruction_id"] for gap in result["validation_gaps"]}
    diagnostics = defaultdict(list)
    for diagnostic in validation["diagnostics"]:
        match = re.search(r"/ir_semantics/(ir_\d+)", diagnostic.get("path", ""))
        if match:
            diagnostics[match.group(1)].append(diagnostic)

    def state(identity):
        return ("retained_modeled" if identity in retained else "source_unmodeled" if identity in source_ids
                else "validation_isolated" if identity in validation_ids else "missing")

    def boundaries(identity):
        return [{**operation, "location": value["locations"].get(operation["operation"].get("location", operation["operation"].get("target")))}
                for operation in operations(value["ir_semantics"].get(identity))]

    def map_sites(key):
        return [{"source_site": original["source_site"], "instruction_id": item["instruction_id"],
                 "effective_processing_state": state(item["instruction_id"]),
                 "boundary_operations": boundaries(item["instruction_id"]),
                 "coverage_status": "selected_initial_fragment_only_no_propagation_evidence"}
                for original in graph_audit[key] for item in original["primary_instructions"]]

    remote, saves = map_sites("remote_site_mapping"), map_sites("save_site_mapping")
    previous_unmodeled = {gap["instruction_id"] for gap in prior["unmodeled"]}
    higher_ids = sorted(identity for identity in previous_unmodeled if 428 <= int(identity.split("_")[1]) <= 578)
    raw_only_saves = [row["instruction_id"] for row in saves if len(row["boundary_operations"]) == 1
                     and row["boundary_operations"][0]["operation"].get("op") == "write"
                     and row["boundary_operations"][0]["operation"].get("input") == {"kind": "input", "index": 0}]
    counts = {
        "cfg_instructions": len(instructions), "raw_a002_modeled": len(raw["ir_semantics"]),
        "retained_modeled": len(retained), "source_unmodeled_unique_ir": len(source_ids),
        "validation_isolated_unique_ir": len(validation_ids),
        "model_processing_gap_records": len(value["processing_gaps"]),
        "model_non_unmodeled_gap_records": len(value["processing_gaps"]) - len(source_gaps),
        "validation_gap_records": len(result["validation_gaps"]),
        "combined_processing_gap_records": len(value["processing_gaps"]) + len(result["validation_gaps"]),
        "a002_diagnostics": len(validation["diagnostics"]),
        "a002_diagnostics_by_code": dict(Counter(d["code"] for d in validation["diagnostics"])),
        "missing_ir": sorted(set(instructions) - retained - source_ids - validation_ids),
        "overlapping_state_ids": sorted((retained & source_ids) | (retained & validation_ids) | (source_ids & validation_ids)),
        "remote_physical_sites": len(remote), "remote_sites_retained": sum(row["effective_processing_state"] == "retained_modeled" for row in remote),
        "remote_sites_with_remote_call": sum(any(op["operation"]["op"] == "call" and (op["location"] or {}).get("kind") == "remote" for op in row["boundary_operations"]) for row in remote),
        "save_physical_sites": len(saves), "save_sites_retained": sum(row["effective_processing_state"] == "retained_modeled" for row in saves),
        "save_sites_with_raw_data_only_write": len(raw_only_saves),
        "previously_unmodeled_high_level_child_acquisitions_retained": sum(identity in retained for identity in higher_ids),
    }
    notes = [
        {"id": "partial-selection-is-not-accepted-a002", "classification": "recorded_lifecycle_limit",
         "detail": "The a002 response is structurally invalid and accepted_call is null. The selected step value is a program-isolated partial fragment retaining 633 modeled IR. Its 10 model gap records contain two unmodeled IR and eight ordinary limitations; the 44 validation-origin gaps in result.json produce 54 combined gap records. Those numbers describe different sets and must not be interchanged."},
        {"id": "source-unmodeled-only-undefined-values", "classification": "specific_source_representation_limit", "instruction_ids": sorted(source_ids),
         "detail": "The two source-declared unmodeled IR are absent mobile and rich-results sections yielding JavaScript undefined. The supplied reasons distinguish undefined from null and explain serialization consequences. They are separate from the 44 program-isolated records."},
        {"id": "ir111-coverage-corrected", "classification": "correction_observation", "instruction_ids": ["ir_111"],
         "detail": "The missing report-RPC dispatch now has a source-evidenced empty specification and is retained. The correction also represents 46 of the former 48 source-unmodeled IR. Passing record coverage does not establish their source semantics."},
        {"id": "all-save-wrappers-and-path-identities-still-unrepresented", "classification": "concrete_retained_source_representation_mismatch", "instruction_ids": raw_only_saves,
         "source_refs": [{"file": "skill/scripts/src/core/storage.ts", "start_line": 64, "end_line": 94}],
         "detail": "All 25 physical saveResult sites remain modeled as a direct write of input[0] to category-level symbolic storage. Actual saveResult creates a wrapper containing data and metadata, incorporates current settings/propertyId, time, category and labels, derives a concrete path, and serializes that wrapper. The selected summaries do not construct this wrapper or bind the dynamic path. The prose at ir_115 claims metadata wrapping while its operations still write input[0] only. The separate saveResult function body does not by itself connect those summaries to their physical call occurrences."},
        {"id": "bulk-dimension-double-wrapping-persists", "classification": "concrete_retained_source_representation_mismatch", "instruction_ids": ["ir_173"],
         "source_refs": [{"file": "skill/scripts/src/api/bulk-lookup.ts", "start_line": 174, "end_line": 181}],
         "detail": "CFG input[2] is already [{name:pagePath},{name:pageTitle}], but the retained processing for_each builds {name:item} for each existing object, producing nested names. The source passes the object array directly; only the metric-name strings require mapping. This is a source mismatch despite retention by structural validation."},
        {"id": "loop-boundaries-improved-but-normal-helper-substitution-remains", "classification": "retained_boundary_coverage_limit", "instruction_ids": ["ir_418", "ir_547", "ir_566"],
         "source_refs": [{"file": "skill/scripts/src/api/indexing.ts", "start_line": 95, "end_line": 98}, {"file": "skill/scripts/src/index.ts", "start_line": 305, "end_line": 340}],
         "detail": "The correction introduces separate pre-request and post-request error cases for the two high-level loops; post-request cases explicitly deliver publish/inspect requests. Normal branches and the low-level batch still invoke local tool locations update/inspection, rather than explicit remote events, and omit the per-URL console event inside the protected body. Separate standalone remote IR do not establish member-specific normal-path remote coverage. The ordinary gaps accurately retain uncertainty about response acquisition before a later exception."},
        {"id": "former-child-gaps-now-local-tools-plus-storage", "classification": "retained_boundary_coverage_limit", "instruction_ids": higher_ids,
         "detail": "All 25 formerly unmodeled high-level child acquisitions are now retained as local tool calls and separate category-storage writes. This recovers modeled records and explicit default-save effects, but does not by itself model the child invocation's actual network request/response, helper defaults, save wrapper, dynamic path or receiver identity. Do not equate the higher modeled count with those external boundaries being covered."},
        {"id": "receiver-and-interface-evidence-limit", "classification": "requires_source_review", "instruction_ids": [row["instruction_id"] for row in remote],
         "detail": "The 13 direct calls retain remote request/response operations. Their generic locations do not bind the CFG method receiver. The model now records this explicitly at ir_110, including the unknown SDK token-exchange relation. Several interface contracts cite actual request construction and say those fields select an operation; current supplied fields alone do not establish the interface's sufficient-and-necessary field requirements. This snapshot does not establish verified minimal contracts."},
        {"id": "summary-still-an-explicit-gap", "classification": "source_workflow_coverage_limit", "instruction_ids": ["ir_678"],
         "detail": "The ordinary gap still records absent summary reader binding, Markdown transform and Markdown write coordinates, plus the lack of invocation-to-file binding. Task analysis-summary remains a documented obligation, not a fulfilled source boundary."},
        {"id": "validation-isolation-extends-beyond-boundary-nodes", "classification": "effective_fragment_limit", "instruction_ids": sorted(validation_ids),
         "detail": "Isolation includes resource handles, client-cache writes, save defaults, response projections, clock reads, save filename/metadata clocks and load dispatch/projections. Although all direct remote and physical save-site IR survive, surrounding and upstream records do not. Only saved propagation records can later establish which concrete sites were actually processed."},
    ]
    report = {
        "kind": "fresh-selected-partial-processing-source-audit", "snapshot": "initial_pre_source_review_partial_selection",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"step_status": result["status"], "accepted_call": result["accepted_call"],
                    "step_result_file_sha256": sha(step / "result.json"), "selected_value_file_sha256": sha(step / "value.json"),
                    "declared_value_sha256": result["value_sha256"], "raw_a002_response_file_sha256": sha(step / "calls/a002/response.json"),
                    "a002_validation_file_sha256": sha(step / "calls/a002/validation.json"),
                    "a002_candidate_declared_sha256": validation["candidate_sha256"],
                    "initial_cfg_file_sha256": sha(RUN / "graph/initial.json"),
                    "source_inventory_file_sha256": sha(OUT / "source-physical-inventory.json")},
        "counts": counts, "retained_modeled_ids": sorted(retained),
        "source_unmodeled": [{**gap, "cfg": instructions[gap["instruction_id"]]} for gap in source_gaps],
        "validation_isolated": [{"instruction_id": identity, "cfg": instructions[identity], "diagnostics": diagnostics[identity]} for identity in sorted(validation_ids)],
        "non_unmodeled_model_gaps": [gap for gap in value["processing_gaps"] if not gap.get("unmodeled")],
        "prior_a001_unmodeled_reconciliation": [{"instruction_id": identity, "selected_state": state(identity)} for identity in sorted(previous_unmodeled)],
        "remote_site_mapping": remote, "save_site_mapping": saves,
        "high_level_child_mapping": [{"instruction_id": identity, "selected_state": state(identity), "boundary_operations": boundaries(identity)} for identity in higher_ids],
        "loop_boundary_specs": {identity: value["ir_semantics"].get(identity) for identity in ["ir_418", "ir_547", "ir_566"]},
        "bulk_dimension_evidence": {"cfg": instructions["ir_173"], "processing": value["ir_semantics"]["ir_173"]},
        "audit_findings": notes,
        "limitations": ["This is the initial selected partial fragment before source review and any semantic repair; final selected identities require a separate audit.",
                        "Retained or modeled is not processed, reached, source-equivalent, contract-verified or task-complete.",
                        "This helper reads saved JSON only and invokes no validator, compiler, backend, model, Skill, replay or tests."]}
    (OUT / "processing-selected-initial-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Initial selected partial processing: source coverage audit", "", "Snapshot before source review; not propagation coverage or final selected evidence.", "",
             f"Selected file: `{step / 'value.json'}`; SHA-256 `{sha(step / 'value.json')}`.",
             f"Initial CFG SHA-256: `{sha(RUN / 'graph/initial.json')}`.", "",
             "- 679 CFG IR = 633 retained modeled + 2 source-unmodeled + 44 validation-isolated; no missing or overlapping IDs.",
             "- 54 combined gap records = 10 model records (2 unmodeled + 8 ordinary limitations) + 44 validation-origin records.",
             "- 77 a002 diagnostics cover 44 isolated IR; a002 remains structurally invalid and has no accepted_call.",
             "- All 13 direct remote sites and 25 physical saveResult sites have retained boundary operations; backend reachability is not yet established.", ""]
    lines.extend(f"- **{note['id']}**: {note['detail']}" for note in notes)
    lines += ["", "## Validation-isolated instructions", ""]
    lines.extend(f"- {identity}: {instructions[identity]['block_name']} / {instructions[identity]['instruction']['opcode']}; {', '.join(sorted({d['code'] for d in diagnostics[identity]}))}." for identity in sorted(validation_ids))
    lines += ["", *report["limitations"]]
    (OUT / "processing-selected-initial-audit.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
