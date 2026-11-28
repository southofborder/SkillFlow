"""Passive audit of the accepted fresh revision CFG, before final selection."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
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
    step = RUN / "steps/revision-graph"
    result = read(step / "result.json")
    call = step / result["accepted_call"]
    wire, validation = read(call / "response.json"), read(call / "validation.json")
    cfg_path = RUN / "graph/revision.json"
    cfg, inventory = read(cfg_path)["cfg"], read(OUT / "source-physical-inventory.json")
    initial = read(OUT / "cfg-accepted-initial-audit.json")
    by_name = {block["block_name"]: block for block in cfg["blocks"].values()}
    instructions, span_checks = [], []
    alignment_errors = []
    for bi, block in enumerate(wire["blocks"]):
        compiled_block = by_name[block["block_ref"]]
        if len(block["instructions"]) != len(compiled_block["instructions"]):
            alignment_errors.append({"block": block["block_ref"], "error": "instruction_count"})
        for ii, raw in enumerate(block["instructions"]):
            compiled = compiled_block["instructions"][ii]
            if raw["opcode"] != compiled["opcode"]:
                alignment_errors.append({"block": block["block_ref"], "index": ii, "error": "opcode"})
            span = raw.get("metadata", {}).get("_source_span")
            instructions.append({"instruction_id": compiled["id"], "block_id": compiled_block["block_id"],
                                 "block_name": block["block_ref"], "raw_pointer": f"/blocks/{bi}/instructions/{ii}",
                                 "cfg_pointer": f"/blocks/{compiled_block['block_id']}/instructions/{ii}",
                                 "data_source_kind": compiled_block.get("data_source_kind"), "source_span": span,
                                 "raw_instruction": raw, "compiled_instruction": compiled})
            if span:
                source = RUN / "source/inputs/package" / span["file"].removeprefix("skill/")
                lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
                expected = "".join(lines[span["start_line"] - 1:span["end_line"]])
                span_checks.append({"instruction_id": compiled["id"], **span,
                                    "valid_range": 1 <= span["start_line"] <= span["end_line"] <= len(lines),
                                    "compiled_script_matches_source": compiled.get("metadata", {}).get("script_content") == expected})

    def mapping(sites, kind):
        initial_key = "remote_site_mapping" if kind == "remote" else "save_site_mapping" if kind == "save" else None
        old_ids = {(row["source_site"]["file"], row["source_site"]["line"]): [ir["instruction_id"] for ir in row["primary_instructions"]]
                   for row in initial[initial_key]} if initial_key else {}
        rows = []
        for site in sites:
            matches = [ir for ir in instructions if ir["source_span"] and ir["source_span"]["file"] == site["file"]
                       and ir["source_span"]["start_line"] <= site["line"] <= ir["source_span"]["end_line"]]
            primary = [ir for ir in matches if (
                ir["data_source_kind"] == "external" and ir["raw_instruction"]["opcode"].startswith("acquire_")
                if kind == "remote" else ir["raw_instruction"]["opcode"] == "call_saveResult" if kind == "save" else True)]
            rows.append({"source_site": site, "initial_instruction_ids": old_ids.get((site["file"], site["line"]), []),
                         "span_matches": matches, "primary_instructions": primary,
                         "coverage_status": "accepted_revision_cfg_candidate_only_processing_and_records_pending"})
        return rows

    remotes = mapping(inventory["remote_api_sites"], "remote")
    saves = mapping(inventory["save_result_sites"], "save")
    iterations = mapping(inventory["iteration_sites"], "iteration")
    storage = mapping(inventory["storage_implementation_sites"], "storage")
    heads = [block for block in cfg["blocks"].values() if block["block_name"].endswith("_head")]
    summary = [ir for ir in instructions if ir["block_name"].startswith("documented_summary_")]
    summary_actual = [ir for ir in summary if ir["raw_instruction"]["opcode"] not in {"dispatch", "return"}]
    modules = [ir for ir in instructions if ir["raw_instruction"]["opcode"] == "evaluate_static_dependencies_once"]
    cache = [ir for ir in instructions if ir["raw_instruction"]["opcode"] in {"initialize_client_slots", "write_module_state"}]
    maps = [ir for ir in instructions if ir["block_name"] in {"report_prepare", "report_dimension_head", "report_dimension_member", "report_metrics_init", "report_metric_head", "report_metric_member", "report_request", "bulk_metrics_init", "bulk_metric_head", "bulk_metric_member", "bulk_request"}]
    consumers = Counter(operand.get("identifier") for ir in instructions for operand in ir["raw_instruction"].get("inputs", []) if operand.get("type") == "result")
    module_names = {ir["block_name"] for ir in modules}
    module_blocks = {by_name[name]["block_id"] for name in module_names}
    dependency_edges = [edge for edge in cfg["edges"] if edge["source_block_id"] in module_blocks
                        and edge["target_block_id"] in {by_name[name]["block_id"] for name in {"settings_module", "client_module", "storage_module"}}]
    notes = [
        {"id": "revision-accepted-not-yet-final-selected", "detail": "Revision graph a001 is valid without structural correction. graph/revision.json has 302 blocks, 770 IR and 283 edges, versus initial 268/679/252. At this snapshot graph/selected.json remains byte-identical to graph/initial.json. The revision is a candidate for controller selection, not yet final evidence."},
        {"id": "physical-boundaries-retained-with-new-identities", "detail": "All 13 physical remote API calls and all 25 physical saveResult calls have exactly one matching primary CFG instruction. The mapping stores initial and revision identities separately. The remote IR explicitly retains an endpoint, method receiver and request argument. This does not establish correct executable processing or observed network/storage exposure."},
        {"id": "report-and-bulk-maps-now-separated", "instruction_ids": ["ir_126", "ir_128", "ir_130", "ir_131", "ir_133", "ir_135", "ir_137", "ir_138", "ir_140", "ir_221", "ir_223", "ir_225", "ir_226", "ir_228"],
         "detail": "The revised CFG has separate report dimension and metric traversals, plus the bulk metric traversal, with initialize/merge/member/collect coordinates. Report request ir_140 consumes mapped results. Bulk request ir_228 consumes fixed [{name:pagePath},{name:pageTitle}] dimensions and an already mapped metric result. This is the correct source-level separation; the earlier processing double-wrap cannot be declared fixed until the revised processing uses those values without rewrapping them."},
        {"id": "loop-and-sparse-array-fidelity-still-needs-processing", "detail": "Ten explicit iteration heads now include the three requested source maps in addition to the original seven. Metadata describes Array.map as visiting present slots in source order with original slot semantics. The executable processing must preserve index, holes, length and member association; explanatory metadata alone does not prove those properties."},
        {"id": "summary-workflow-coordinates-added", "instruction_ids": ["ir_765", "ir_767", "ir_769"],
         "detail": "A documentation-level independent entry now reads saved JSON, creates Markdown and writes under results/summaries/. The graph explicitly leaves file selection, invocation provenance, exact summary dependencies and basename unspecified. It does not claim that a TypeScript function invokes this workflow or wire the independent storage examples as its provenance. These are source-backed natural-language operations, not an actual new Skill implementation."},
        {"id": "module-import-routes-separated-as-call-coordinates", "detail": "Eleven evaluate_static_dependencies_once operations distinguish nine module routes (index, six direct API modules, storage and client) plus two documented examples importing index. Direct storage depends on settings without client initialization; direct API routes reach client/storage/settings without the index runtime guard. Only index evaluation leads to the argv/import.meta.url comparison. Dependencies are represented as instruction metadata and call-like coordinates, not CFG edges into the dependency bodies; executable state-sharing, once-per-module and abrupt-completion semantics remain obligations for processing."},
        {"id": "cache-and-environment-obligations-explicit", "instruction_ids": ["ir_026", "ir_032", "ir_073", "ir_087", "ir_098"],
         "detail": "The client module initializes distinct cache slots. Three getter miss paths explicitly write their freshly constructed handles to the corresponding slots; constraints retain creation-time credentials and independent newer target settings. Dotenv initialization explicitly associates the post-environment with config(), while preserving internal precedence uncertainty. None of these CFG declarations alone proves that later processing retains the state relations."},
        {"id": "source-behavior-not-repaired-to-match-task", "instruction_ids": ["ir_120", "ir_141", "ir_215"],
         "detail": "Custom filters and orderBy are still acquired but unused, the limit branch remains truthy, and empty bulk still returns zero rows before its API call/save. These source facts must coexist with the revised Task obligations/conflicts; the CFG correctly does not invent filtering, sorting or an empty-result write."},
        {"id": "save-summaries-remain-processing-obligations", "detail": "Each physical call still has actual payload/category/operation/optional label operands. Caller-site wrapper construction, save-time settings/clocks, dynamic storage address and conditional directory effects must be represented in revised processing. The standalone storage body does not by itself fulfill all 25 occurrence-specific write relations."},
    ]
    report = {
        "kind": "fresh-accepted-revision-cfg-source-audit", "snapshot": "accepted_revision_cfg_candidate_before_rereview_and_controller_selection",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "binding": {"cfg_file_sha256": sha(cfg_path), "graph_result_file_sha256": sha(step / "result.json"),
                    "accepted_call": result["accepted_call"], "accepted_response_file_sha256": sha(call / "response.json"),
                    "accepted_validation_file_sha256": sha(call / "validation.json"), "validation_status": validation["status"],
                    "candidate_declared_sha256": validation["candidate_sha256"], "value_declared_sha256": result["value_sha256"],
                    "initial_cfg_file_sha256": sha(RUN / "graph/initial.json"), "selected_cfg_file_sha256_at_snapshot": sha(RUN / "graph/selected.json"),
                    "selected_still_initial_at_snapshot": (RUN / "graph/selected.json").read_bytes() == (RUN / "graph/initial.json").read_bytes(),
                    "source_inventory_sha256": sha(OUT / "source-physical-inventory.json"),
                    "revision_task_declared_sha256": read(RUN / "revision/task/task.json")["task_sha256"]},
        "counts": {"blocks": len(cfg["blocks"]), "instructions": len(instructions), "edges": len(cfg["edges"]),
                   "remote_sites": len(remotes), "remote_sites_with_exactly_one_acquisition_ir": sum(len(row["primary_instructions"]) == 1 for row in remotes),
                   "save_sites": len(saves), "save_sites_with_exactly_one_call_ir": sum(len(row["primary_instructions"]) == 1 for row in saves),
                   "iteration_sites": len(iterations), "iteration_sites_with_span_matches": sum(bool(row["span_matches"]) for row in iterations),
                   "explicit_iteration_heads": len(heads), "summary_workflow_ir": len(summary), "summary_noncontrol_operations": len(summary_actual),
                   "module_dependency_evaluation_operations": len(modules), "dependency_body_cfg_edges": len(dependency_edges),
                   "source_span_checks": len(span_checks), "invalid_source_span_ranges": sum(not row["valid_range"] for row in span_checks),
                   "compiled_script_source_mismatches": sum(not row["compiled_script_matches_source"] for row in span_checks)},
        "raw_compiled_alignment_errors": alignment_errors, "source_span_checks": span_checks,
        "remote_site_mapping": remotes, "save_site_mapping": saves, "iteration_site_mapping": iterations,
        "storage_implementation_mapping": storage, "explicit_iteration_heads": heads, "source_map_operations": maps,
        "summary_operations": summary, "module_evaluation_operations": modules, "cache_state_operations": cache,
        "report_option_consumers": {name: consumers[name] for name in ("report_filters", "report_order", "report_limit")},
        "generator_diagnostics": wire.get("diagnostics", []), "audit_findings": notes,
        "limitations": ["Accepted graph syntax, matching source spans and physical-site presence are not semantic correctness, dynamic reachability or verified demand-transfer evidence.",
                        "Inspect selected revised processing, rereview and final propagation separately; immutable initial and revision-candidate snapshots remain distinct.",
                        "This helper reads saved JSON only and invokes no compiler, validator, tests, backend, model, Skill or replay."]}
    (OUT / "cfg-accepted-revision-initial-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Accepted revised CFG: source audit", "", "This is the accepted revision candidate before rereview and controller selection.", "",
             f"302 blocks, 770 IR, 283 edges. Bound graph/revision.json SHA-256: `{sha(cfg_path)}`.",
             f"All {len(span_checks)} source spans are valid and match compiled script text. The initial snapshot is preserved.", ""]
    lines += [f"- **{note['id']}**: {note['detail']}" for note in notes]
    for heading, rows in [("Remote source sites", remotes), ("Physical saveResult sites", saves)]:
        lines += ["", "## " + heading, ""]
        lines += [f"- {row['source_site']['file']}:{row['source_site']['line']}: " + ", ".join(row["initial_instruction_ids"]) + " → " + ", ".join(ir["instruction_id"] for ir in row["primary_instructions"]) for row in rows]
    lines += ["", *report["limitations"]]
    (OUT / "cfg-accepted-revision-initial-audit.en.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"counts": report["counts"], "alignment_errors": alignment_errors, "cfg_sha256": sha(cfg_path), "report_option_consumers": report["report_option_consumers"]}))


if __name__ == "__main__":
    main()
