"""Passive audit of the rejected fresh processing response; no compilation."""
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


def operations(value, path=()):
    rows = []
    if isinstance(value, dict):
        if "op" in value and isinstance(value["op"], str) and ("inputs" in value or value["op"] in {"write", "build", "select_part", "append"}):
            rows.append({"path": list(path), "operation": value})
        for key, child in value.items():
            rows.extend(operations(child, (*path, key)))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            rows.extend(operations(child, (*path, i)))
    return rows


def main():
    call = RUN / "steps/processing/calls/a001"
    candidate = read(call / "response.json")
    validation = read(call / "validation.json")
    graph_audit = read(OUT / "cfg-accepted-initial-audit.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    instructions = {ir["id"]: {"block_id": b["block_id"], "block_name": b["block_name"], "instruction": ir}
                    for b in cfg["blocks"].values() for ir in b["instructions"]}
    unmodeled = [{**g, "cfg": instructions[g["instruction_id"]]} for g in candidate["processing_gaps"] if g.get("unmodeled")]
    unmodeled_ids = {g["instruction_id"] for g in unmodeled}
    modeled = set(candidate["ir_semantics"])
    missing = sorted(set(instructions) - modeled - unmodeled_ids)
    by_ir = {identity: operations(spec) for identity, spec in candidate["ir_semantics"].items()}
    locations = candidate["locations"]

    def boundary_mapping(key):
        rows = []
        for original in graph_audit[key]:
            for ir in original["primary_instructions"]:
                identity = ir["instruction_id"]
                ops = by_ir.get(identity, [])
                boundaries = [{**op, "location": locations.get(op["operation"].get("location", op["operation"].get("target")))}
                              for op in ops if op["operation"]["op"] in {"call", "write", "deliver", "receive"}]
                rows.append({"source_site": original["source_site"], "instruction_id": identity,
                    "raw_candidate_state": "modeled" if identity in modeled else "unmodeled" if identity in unmodeled_ids else "missing",
                    "boundary_operations": boundaries, "specification": candidate["ir_semantics"].get(identity),
                    "coverage_status": "raw_candidate_unaccepted_no_propagation_evidence"})
        return rows

    remote, saves = boundary_mapping("remote_site_mapping"), boundary_mapping("save_site_mapping")
    higher = [g for g in unmodeled if 428 <= int(g["instruction_id"].split("_")[1]) <= 578]
    loop_ids = ["ir_418", "ir_547", "ir_566"]
    notes = [
        {"id": "ir111-dispatch-omission", "classification": "recorded_structural_failure", "instruction_ids": ["ir_111"],
         "detail": "ir_111 is the empty dispatch immediately after the runReport acquisition. A non-unmodeled processing_gap note exists, but no modeled specification or explicit unmodeled coverage exists, so the instruction coverage check correctly rejects a001."},
        {"id": "unmodeled-upstream-and-child-acquisitions", "classification": "raw_coverage_limit", "instruction_ids": sorted(unmodeled_ids),
         "detail": "48 explicit unmodeled IR comprise 25 high-level child acquisitions and 23 setup/helper/default/undefined cases. Several missing property/client/parser/default operations precede direct remote requests in their CFG blocks. Direct boundary operations being present does not establish those paths will be processed or their results usable. Many reasons describe required work the model did not represent, rather than a semantic relation missing from the supplied source."},
        {"id": "all-save-wrappers-and-path-identities-unrepresented", "classification": "concrete_raw_source_representation_mismatch",
         "instruction_ids": [r["instruction_id"] for r in saves],
         "source_refs": [{"file": "skill/scripts/src/core/storage.ts", "start_line": 64, "end_line": 94}],
         "detail": "Every raw saveResult summary writes only input[0] directly to a category-level symbolic storage location. The source instead constructs a wrapper containing data and save-time metadata, derives the path from category/operation/extraInfo/current settings/time, and writes serialized wrapper content. The prose at ir_115 claims wrapping, but its operations contain no wrapper construction, metadata acquisition or dynamic path binding. This is stronger boundary representation than a local-tool placeholder, but not the complete source save behavior."},
        {"id": "bulk-dimension-double-wrapping", "classification": "concrete_raw_source_representation_mismatch", "instruction_ids": ["ir_173"],
         "source_refs": [{"file": "skill/scripts/src/api/bulk-lookup.ts", "start_line": 174, "end_line": 181}],
         "detail": "CFG input[2] already contains [{name:pagePath},{name:pageTitle}]. Raw processing iterates those objects and builds {name:item}, producing nested name objects rather than the source's existing name strings. Metrics input[3] is a string array and is correctly the one that requires name-object mapping. The raw deterministic construction must not be treated as source-equivalent merely because its schema validates."},
        {"id": "loop-helper-tool-substitution", "classification": "raw_boundary_coverage_limit", "instruction_ids": loop_ids,
         "source_refs": [{"file": "skill/scripts/src/api/indexing.ts", "start_line": 95, "end_line": 98}, {"file": "skill/scripts/src/index.ts", "start_line": 305, "end_line": 340}],
         "detail": "The batch update and both protected high-level URL calls use in-process updateHelper/inspectHelper tool locations. Their raw normal/error operations do not contain the actual remote publish/inspect or per-URL console event. Error-split gaps acknowledge uncertainty but do not establish the normal-path remote action. Separate standalone remote definitions do not prove the same member invocation's boundary coverage."},
        {"id": "receiver-and-interface-evidence-check", "classification": "requires_whole_chain_source_review",
         "instruction_ids": [r["instruction_id"] for r in remote],
         "detail": "The direct remote calls pass the constructed request but omit the CFG's separate receiver-handle operand from the call inputs and use generic named remote locations without operand_refs. Check whether caller/receiver/authentication identities are preserved elsewhere in the final compilation. Contract evidence often cites constructed arguments themselves; those alone do not establish a tool interface's sufficient-and-necessary field requirements."},
        {"id": "summary-gap-is-recorded-not-implemented", "classification": "raw_coverage_limit", "instruction_ids": ["ir_678"],
         "detail": "The non-unmodeled gap at ir_678 explicitly notes no Markdown processing/write coordinate, the lack of invocation-to-saved-file binding, and conditional/empty paths without a saved file. This preserves a limitation; it is not an implementation or fulfillment of Task analysis-summary."},
    ]
    counts = {"cfg_instructions": len(instructions), "modeled": len(modeled), "explicit_unmodeled": len(unmodeled_ids),
        "processing_gap_records": len(candidate["processing_gaps"]), "missing": missing,
        "unmodeled_high_level_child_acquisitions": len(higher), "other_unmodeled": len(unmodeled) - len(higher),
        "remote_physical_sites_with_remote_call_ops": sum(any(b["operation"]["op"] == "call" and (b["location"] or {}).get("kind") == "remote" for b in r["boundary_operations"]) for r in remote),
        "save_physical_sites_with_storage_write_ops": sum(any(b["operation"]["op"] == "write" and (b["location"] or {}).get("kind") == "storage" for b in r["boundary_operations"]) for r in saves)}
    value = {"kind": "fresh-unaccepted-processing-preliminary-audit", "snapshot": "processing_a001_structural_invalid_not_selected",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"response_file_sha256": sha(call / "response.json"), "validation_file_sha256": sha(call / "validation.json"),
            "validation_status": validation["status"], "candidate_declared_sha256": validation["candidate_sha256"],
            "accepted_initial_cfg_file_sha256": sha(RUN / "graph/initial.json"),
            "accepted_cfg_audit_file_sha256": sha(OUT / "cfg-accepted-initial-audit.json")},
        "counts": counts, "unmodeled": unmodeled, "missing_instructions": [instructions[i] for i in missing],
        "non_unmodeled_processing_gaps": [g for g in candidate["processing_gaps"] if not g.get("unmodeled")],
        "remote_site_mapping": remote, "save_site_mapping": saves,
        "loop_boundary_specs": {i: candidate["ir_semantics"].get(i) for i in loop_ids},
        "bulk_dimension_evidence": {"cfg": instructions["ir_173"], "raw_processing": candidate["ir_semantics"]["ir_173"]},
        "audit_findings": notes,
        "limitations": ["This is not selected processing, successful compilation or propagation coverage. Recheck the accepted correction and any semantic repair separately.",
                        "The helper reads saved JSON only; it invokes no compiler, validator, model, Skill, backend or replay."]}
    (OUT / "processing-a001-preliminary.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Rejected processing a001: preliminary source audit", "", "This raw candidate is unaccepted. No backend coverage is inferred.", "", json.dumps(counts), ""]
    lines += ["- " + n["id"] + ": " + n["detail"] for n in notes]
    lines += ["", "## Explicit unmodeled instructions", ""]
    lines += [f"- {g['instruction_id']} / {g['cfg']['block_name']} / {g['cfg']['instruction']['opcode']}: {g['reason']}" for g in unmodeled]
    lines += ["", *value["limitations"]]
    (OUT / "processing-a001-preliminary.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
