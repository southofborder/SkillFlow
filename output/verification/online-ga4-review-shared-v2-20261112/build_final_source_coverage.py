"""Passive source/CFG/record correspondence; no SkillFlow analysis is executed."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parents[2]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242"


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path, text):
    raw = text.encode("utf-8")
    if path.exists() and path.read_bytes() != raw:
        raise ValueError("Preserve the existing final coverage audit: " + str(path))
    if not path.exists():
        path.write_bytes(raw)


def main():
    initial_path = OUTPUT / "generated-cfg-audit.json"
    initial = read(initial_path)
    run_result = read(RUN / "result.json")
    references = read(RUN / "annotation/inputs/references.json")
    graph_path = (RUN / "annotation" / references["cfg"]["path"]).resolve()
    graph_hash = sha(graph_path)
    if graph_hash != references["cfg"]["sha256"] or graph_hash != initial["graph_file_sha256"]:
        raise ValueError("Final annotation uses a changed CFG; a new source mapping is required")
    if run_result.get("repair_used") or run_result.get("selected_annotation") != "annotation":
        raise ValueError("This audit expects the unchanged selected initial annotation")
    prop_path = RUN / "propagation"
    manifest = read(prop_path / "manifest.json")
    if manifest["status"] not in {"incomplete", "complete"}:
        raise ValueError("Propagation artifacts are not finalized")
    for name in ("records.json", "sinks.json", "data.json", "audit/stats.json"):
        if sha(prop_path / name) != manifest["artifacts"][name]:
            raise ValueError("Propagation artifact does not match its finalized manifest: " + name)
    records = read(prop_path / "records.json")
    sinks = read(prop_path / "sinks.json")
    compiled = read(RUN / "annotation/audit/compiled-response.json")
    mapping = read(RUN / "annotation/audit/compilation-map.json")
    status = manifest["coverage"]
    cfg = read(graph_path)["cfg"]
    ir_index = {instruction["id"]: (block, instruction) for block in cfg["blocks"].values()
                for instruction in block["instructions"]}
    diagnostics = manifest["diagnostics"]
    gaps = mapping["processing_gaps"]

    def operation_records(identity):
        result = []
        for event_index, event in enumerate(records.get(identity, {}).get("events", [])):
            for op_index, operation in enumerate(event.get("atomic_ops", [])):
                result.append({"event_index": event_index, "op_index": op_index,
                    "effect": event.get("effect"), "case": event.get("case"),
                    "op": operation["op"], "endpoints": operation.get("endpoints", []),
                    "inputs": operation.get("inputs", []), "outputs": operation.get("outputs", []),
                    "alternative_count": len(operation.get("alternatives", []))})
        return result

    def map_site(site, expected_type):
        identity = site["instruction_id"]
        row = {key: site[key] for key in ("site_id", "file", "start_line", "end_line", "function", "callee", "instruction_id", "block_id", "block_name", "opcode")}
        actual_sinks = [sink for sink in sinks if sink["instruction_id"] == identity]
        operations = operation_records(identity)
        matched = [sink for sink in actual_sinks if sink["sink_type"] == expected_type]
        if matched:
            boundary = "expected_boundary_recorded"
        elif status[identity] in {"unmodeled", "blocked"}:
            boundary = status[identity]
        else:
            boundary = "local_tool_substitution_without_expected_boundary"
        row.update(propagation_status=status[identity], has_operation_record=identity in records,
            expected_boundary=expected_type, boundary_status=boundary,
            expected_boundary_records=matched, all_sink_records=actual_sinks,
            operation_records=operations,
            source_processing_gaps=[gap for gap in gaps if gap["instruction_id"] == identity],
            diagnostics=[diagnostic for diagnostic in diagnostics if diagnostic.get("instruction_id") == identity])
        if status[identity] == "blocked":
            # The four isolated function regions and their explicit unmodeled
            # acquisition are identified from this same finalized CFG/coverage.
            owner = {"ir_214": "ir_212", "ir_223": "ir_219", "ir_232": "ir_228", "ir_239": "ir_237"}[identity]
            row["blocking_acquisition"] = owner
            row["blocking_gap"] = [gap for gap in gaps if gap["instruction_id"] == owner]
        return row

    remote = [map_site(site, "network_send") for site in initial["remote_api_mappings"]]
    saves = [map_site(site, "storage_write") for site in initial["save_result_mappings"]]
    loops = []
    for loop in initial["loop_boundaries"]:
        ids = [instruction["instruction_id"] for instruction in loop["instructions"]]
        loops.append({"name": loop["name"], "source_ref": loop["source_ref"], "head_block": loop["head_block"],
            "instruction_statuses": {identity: status[identity] for identity in ids},
            "all_mapped_instructions_processed": all(status[identity] == "processed" for identity in ids),
            "all_mapped_records_present": all(identity in records for identity in ids),
            "processing_gaps": [gap for gap in gaps if gap["instruction_id"] in ids],
            "diagnostics": [diagnostic for diagnostic in diagnostics if diagnostic.get("instruction_id") in ids],
            "sink_records": [sink for sink in sinks if sink["instruction_id"] in ids]})
    unprocessed = []
    for identity, value in status.items():
        if value == "processed":
            continue
        block, instruction = ir_index[identity]
        unprocessed.append({"instruction_id": identity, "status": value, "block_id": block["block_id"],
            "block_name": block["block_name"], "opcode": instruction["opcode"],
            "has_operation_record": identity in records,
            "processing_gaps": [gap for gap in gaps if gap["instruction_id"] == identity]})
    loop_calls = [{"instruction_id": identity, "operations": operation_records(identity),
        "sink_records": [sink for sink in sinks if sink["instruction_id"] == identity]}
        for identity in ("ir_331", "ir_416", "ir_428")]
    option_selections = [operation.get("path") for event in compiled["ir_semantics"]["ir_098"]["events"]
                         for operation in event.get("atomic_ops", []) if operation["op"] == "select_part"]
    concerns = [
        {"id": "realtime_remote_substitution", "instruction_ids": ["ir_191", "ir_198", "ir_205"],
         "source_refs": [{"file": "skill/scripts/src/api/realtime.ts", "start_line": 24, "end_line": 78}],
         "observation": "Three processed physical runRealtimeReport sites contain only deliver/receive operations to task-local getActiveUsers/getRealtimeEvents/getRealtimePages tools. Their locations have task access and task retention. They have no network_send sink or concrete remote request at these coordinates.",
         "impact": "These processed IR cannot be counted as faithfully modeled remote exposure sites; the standalone source contains real Google client calls."},
        {"id": "save_call_persistence_omitted", "instruction_ids": [row["instruction_id"] for row in saves if row["propagation_status"] == "processed"],
         "observation": "All 21 processed saveResult call sites contain a delivery to the save location, declared kind=tool, access_scope=task and retention=task. No storage_write sink appears at any of these callers. Four additional save sites are blocked. The separate public saveResult utility has directory creation at ir_442 and file write at ir_454.",
         "impact": "A standalone public storage write does not instantiate persistence for each caller's report/aggregate/member version. Therefore 21 processed saves are not 21 source-supported persisted-result boundaries."},
        {"id": "successful_loop_remote_effects_omitted", "instruction_ids": ["ir_331", "ir_416", "ir_428"],
         "source_refs": [{"file": "skill/scripts/src/api/indexing.ts", "start_line": 94, "end_line": 98},
                         {"file": "skill/scripts/src/index.ts", "start_line": 305, "end_line": 340}],
         "observation": "The ordinary indexing-batch member call ir_331 is only a task-local toolkit requestIndexing tool. The normal submitted/inspected cases at ir_416/ir_428 also use local toolkit tools. Their explicit network_send records occur only in after_publish_entry/after_inspect_entry post_request_error cases (event 8/event 13).",
         "impact": "All ten loop structures process, but successful per-member network effects are not faithfully expanded. Separate standalone API functions do not establish these callers' member/request provenance."},
        {"id": "summary_writer_still_absent", "instruction_ids": ["ir_511"],
         "source_refs": [{"file": "skill/SKILL.md", "start_line": 53, "end_line": 64}],
         "observation": "The unchanged CFG has no summary generation or Markdown writer IR. The selected processing gap at ir_511 explicitly states that source analysis entry points discard save paths and there is no binding from a particular analysis invocation to selected saved content, summary writer or user delivery.",
         "impact": "The narrative summarize stage is not established by the physical 13/25 site counts or by standalone file reads."},
        {"id": "unused_original_option_reads_not_preserved_as_field_operations", "instruction_ids": ["ir_098"],
         "source_refs": [{"file": "skill/scripts/src/api/reports.ts", "start_line": 77, "end_line": 85}],
         "observation": "The original destructuring reads filters and orderBy, and CFG metadata retains them as unused. Selected compiled processing only selects dimensions, metrics, dateRange and limit plus computes save; it contains no select_part for filters/orderBy and no explicit model-observation operation at this IR.",
         "impact": "A claim that unused input reads were preserved at field level is not supported for these two source fields. Their documentation/implementation mismatch remains distinct from a task-preserving deletion conclusion."},
        {"id": "local_diagnostics_despite_processed_status", "instruction_ids": ["ir_453", "ir_460", "ir_462"],
         "observation": "The finalized manifest records unresolved_path for one predecessor path at wrapper construction ir_453 and missing_part diagnostics for content/value on literal candidates at ir_460/ir_462. All three IR nevertheless have overall processed status and operation records.",
         "impact": "Processed means the abstract solver produced a record, not that every predecessor/candidate path or source relationship is fully established."},
    ]
    artifact_names = ["result.json", "annotation/inputs/references.json", "annotation/manifest.json",
        "annotation/audit/compiled-response.json", "annotation/audit/compilation-map.json",
        "propagation/manifest.json", "propagation/records.json", "propagation/sinks.json", "propagation/audit/stats.json"]
    result = {"identity": "skillflow-final-source-record-coverage-audit-v1",
        "run": str(RUN), "scope": "Selected unchanged CFG and finalized propagation records; passive audit, not a new analysis or runtime execution.",
        "selected_graph": {"path": str(graph_path), "sha256": graph_hash,
            "same_as_initial_pre_review_snapshot": True, "initial_audit_sha256": sha(initial_path),
            "annotation_reference": references["cfg"]},
        "selection": {"selected_annotation": run_result["selected_annotation"], "repair_used": run_result["repair_used"],
            "review_status": run_result["stages"]["review"], "graph_review": run_result["graph_review"],
            "annotation_review": run_result["annotation_review"]},
        "artifact_sha256": {name: sha(RUN / name) for name in artifact_names},
        "counts": {"generated_ir": len(status), "propagation_status": manifest["status"],
            "ir_statuses": dict(Counter(status.values())), "operation_records": len(records),
            "remote_source_sites": len(remote), "remote_site_ir_statuses": dict(Counter(row["propagation_status"] for row in remote)),
            "remote_site_boundary_statuses": dict(Counter(row["boundary_status"] for row in remote)),
            "save_source_sites": len(saves), "save_site_ir_statuses": dict(Counter(row["propagation_status"] for row in saves)),
            "save_site_boundary_statuses": dict(Counter(row["boundary_status"] for row in saves)),
            "explicit_loop_headers": len(loops), "loop_groups_all_ir_processed": sum(row["all_mapped_instructions_processed"] for row in loops),
            "all_recorded_sink_types": dict(Counter(row["sink_type"] for row in sinks))},
        "remote_source_sites": remote, "save_source_sites": saves, "unprocessed_instructions": unprocessed,
        "loop_coverage": loops, "loop_call_effects": loop_calls,
        "standalone_storage_sink_records": [sink for sink in sinks if sink["sink_type"] == "storage_write"],
        "standalone_storage_operation_records": {identity: operation_records(identity) for identity in ("ir_442", "ir_453", "ir_454")},
        "relevant_location_declarations": {key: value for key, value in compiled["locations"].items()
            if key in {"save", "liveUsers", "liveEvents", "livePages", "requestIndex", "inspect", "fileWrite", "dir"}},
        "original_option_selected_paths": option_selections,
        "diagnostics": diagnostics, "concerns": concerns,
        "limitations": ["The review had no accepted response after its one structural correction, so no semantic repair ran; source/contract semantic completeness remains unreviewed.",
            "Recorded static possible operations and sink positions are not executed Skill events or proof of feasible runtime paths.",
            "Counts distinguish CFG representation, solver processing and faithful source boundary instantiation; they must not be conflated.",
            "This audit reads finalized propagation artifacts only and does not compute or validate DOE conclusions."]}
    write_once(OUTPUT / "final-source-coverage.json", json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    lines = ["# Final selected GA4 source and propagation coverage", "",
        "The final annotation references the exact initial accepted CFG: `graph/initial.json`, SHA-256 `" + graph_hash + "`. There was no semantic repair. Source review ended with structural_failure and has no accepted review, so the graph and annotation remain semantically unreviewed. Initial source/CFG audit files are preserved separately.", "",
        "Finalized propagation has **487/511 processed IR, 4 unmodeled IR and 20 blocked IR**. These are static record statuses, not executed source coverage.", "",
        "| Source denominator | CFG represented | IR processed | Expected boundary recorded | Important remainder |",
        "|---|---:|---:|---:|---|",
        "| 13 explicit remote API sites | 13 | 9 | 6 network_send sites | 3 processed sites replaced by local tools; 4 unmodeled |",
        "| 25 explicit saveResult sites | 25 | 21 | 0 caller storage_write sites | 21 processed local-tool deliveries; 4 blocked |", "",
        "The standalone storage utility separately records two storage_write positions: directory creation at ir_442 and file writing at ir_454. Neither proves that the 25 caller-specific payloads were persisted in the recorded model. Total recorded sinks are 58 model_observe, 8 network_send and 2 storage_write; the two additional network sends occur only in loop post-request-error cases.", "",
        "## Remote physical sites", "", "| Source | Function | IR | Solver | Recorded boundary |", "|---|---|---|---|---|"]
    for row in remote:
        lines.append(f"| `{row['file']}:{row['start_line']}` | {row['function']} | `{row['instruction_id']}` | {row['propagation_status']} | {row['boundary_status']} |")
    lines.extend(["", "## saveResult physical sites", "", "| Source | Function | IR | Solver | Recorded boundary |", "|---|---|---|---|---|"])
    for row in saves:
        lines.append(f"| `{row['file']}:{row['start_line']}` | {row['function']} | `{row['instruction_id']}` | {row['propagation_status']} | {row['boundary_status']} |")
    lines.extend(["", "## Exact unmodeled and blocked regions", "",
        "- Realtime sources: unmodeled ir_212; blocked ir_213–ir_216, including save ir_214 at realtime.ts:95.",
        "- Available dimensions: unmodeled ir_219; blocked ir_220–ir_225, including save ir_223 at metadata.ts:51.",
        "- Available metrics: unmodeled ir_228; blocked ir_229–ir_234, including save ir_232 at metadata.ts:73.",
        "- Full metadata: unmodeled ir_237; blocked ir_238–ir_241, including save ir_239 at metadata.ts:91.", "",
        "Each unmodeled gap explicitly cites absent receiver/property request bindings in the grouped CFG acquisition. They are labeled source-origin processing gaps in the saved material; the underlying explanation concerns this CFG's representation. No IR is labeled failed in the finalized coverage table. All exact gap reasons, source citations and 24 nonprocessed positions are retained in the JSON audit.", "",
        "## Loop and semantic fidelity caveats", ""])
    for concern in concerns:
        lines.extend(["### " + concern["id"], "", concern["observation"], "", concern["impact"], ""])
    lines.extend(["## Loop processing status", "", "| Source loop | Header | All mapped IR processed |", "|---|---|---|"])
    for loop in loops:
        lines.append(f"| {loop['name']} | `{loop['head_block']}` | {loop['all_mapped_instructions_processed']} |")
    lines.extend(["", "All ten structural loop groups have records, but this does not repair the omitted normal per-item remote effects described above. Each loop's exact instruction statuses, gaps, sink coordinates and relevant recorded case phases are retained in final-source-coverage.json.", "",
        "This passive audit used only selected current artifacts and preserved earlier audits. It ran no validator, backend analysis, model, Skill, test or replay, and it makes no independent DOE deletion or necessity conclusion.", ""])
    write_once(OUTPUT / "final-source-coverage.en.md", "\n".join(lines))
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
