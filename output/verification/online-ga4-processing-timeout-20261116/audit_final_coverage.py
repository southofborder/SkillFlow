"""Read terminal public artifacts only; no SkillFlow imports or execution."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414"
READS = {}


def read(path):
    raw = path.read_bytes()
    READS[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
    return raw


def load(path):
    return json.loads(read(path))


def main():
    result = load(RUN / "result.json")
    protocol = load(RUN / "run-protocol.json")
    controller = load(RUN / "controller-finished.json")
    replay = load(RUN / "replay-check.json")
    native_exits = load(RUN / "native-exit-check.json")
    freeze = load(RUN / "implementation-check.json")
    analysis = load(RUN / "analysis-finished.json")
    state = load(RUN / "continuation-state.json")
    frontier = load(RUN / result["fatal_frontier"]["path"])
    assert READS[(RUN / result["fatal_frontier"]["path"]).relative_to(ROOT).as_posix()] == result["fatal_frontier"]["sha256"]
    assert frontier["guided_state"]["status"] == result["status"] == "failed"
    assert frontier["guided_state"]["stage"] == result["stage"] == "processing"
    assert frontier["guided_state"]["stages"] == result["stages"]
    assert state["status"] == "generation_closed"
    assert replay["status"] == "matched" and replay["new_native_markers"] == 0
    assert native_exits["all_attempt_exits_confirmed"] and native_exits["attempt_markers"] == 6
    assert freeze["unchanged"] and freeze["implementation_sha256"] == protocol["implementation_sha256"]

    bound_count = 0
    def receipt_refs(value):
        nonlocal bound_count
        if isinstance(value, dict):
            if set(value) == {"path", "sha256"}:
                target = RUN / value["path"]
                digest = hashlib.sha256(read(target)).hexdigest()
                assert digest == value["sha256"], value["path"]
                bound_count += 1
            else:
                for member in value.values():
                    receipt_refs(member)
        elif isinstance(value, list):
            for member in value:
                receipt_refs(member)
    receipt_refs(frontier)

    graph = load(RUN / "graph/initial.json")["cfg"]
    graph_result = load(RUN / "steps/graph/result.json")
    graph_validation = load(RUN / "steps/graph/calls/a002/validation.json")
    task = load(RUN / "task/task.json")
    source_inventory = load(OUT / "source-physical-inventory.json")
    graph_audit = load(OUT / "initial-cfg-source-audit.json")
    validation = load(RUN / "steps/processing/calls/a001/validation.json")
    chain = load(RUN / "steps/processing/calls/chain.json")
    assert validation["status"] == "structural_invalid"
    assert chain["accepted_call"] is None
    assert validation["diagnostics"] == [{"code": "json_format", "path": "", "message": "duplicate JSON member: shared_values"}]
    failed_call = load(RUN / "steps/processing/calls/a002/call.json")
    failed_call_summary = {key: failed_call.get(key) for key in ("status", "started_at", "finished_at", "error_type", "error")}
    native_processing = []
    for path in sorted((RUN / "transport/processing").rglob("process.json")):
        native_processing.append({"path": path.relative_to(RUN).as_posix(), **load(path)})
    timeout = next(row for row in native_processing if row["status"] == "timeout")
    assert timeout["exited"] is True

    paths = {
        "initial_task": "task/task.json", "flow_document": "steps/flow/document.md",
        "accepted_initial_cfg": "graph/initial.json", "selected_cfg": "graph/selected.json",
        "selected_bundle": "selection.json", "annotation": "annotation", "revision": "revision",
        "accepted_processing_result": "steps/processing/result.json", "accepted_processing_value": "steps/processing/value.json",
        "task_correspondence_stage": "steps/task-correspondence", "sensitivity_stage": "steps/sensitivity",
        "source_review": "review", "bound_input_contract_review": "audit/input-contract-review.json",
        "propagation": "propagation", "doe": "doe",
        "processing_correction_response": "steps/processing/calls/a002/response.json",
    }
    presence = {key: {"path": path, "exists": (RUN / path).exists()} for key, path in paths.items()}
    for key, row in presence.items():
        assert row["exists"] == (key in {"initial_task", "flow_document", "accepted_initial_cfg"}), key
    assert result["selected_annotation"] is None and result["repair_used"] is False
    assert graph_result["accepted_call"] == "calls/a002" and graph_validation["status"] == "valid"
    assert len(graph["blocks"]) == 237 and len(graph["edges"]) == 217
    assert sum(len(block["instructions"]) for block in graph["blocks"].values()) == 521

    source_checks = []
    for row in source_inventory["files"]:
        path = RUN / "source/inputs/package" / row["path"]
        actual = hashlib.sha256(read(path)).hexdigest()
        source_checks.append({"path": row["path"], "sha256": actual, "matches_initial_inventory_and_protocol":
                              actual == row["sha256"] == protocol["source_file_sha256"][row["path"]]})
    assert len(source_checks) == 16 and all(row["matches_initial_inventory_and_protocol"] for row in source_checks)
    absent = {"status": "not_run", "value": None}
    output = {
        "version": "fresh-ga4-final-source-coverage-audit-v1", "observed_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(RUN), "status": "closed_failed_initial_processing_correction",
        "implementation_sha256": protocol["implementation_sha256"], "source_sha256": protocol["source_sha256"],
        "fatal_frontier": {"path": result["fatal_frontier"]["path"], "sha256": result["fatal_frontier"]["sha256"],
                           "referenced_artifact_hashes_match": True, "reference_count": bound_count,
                           "observed_stage_statuses": result["stages"]},
        "closure": {"controller": controller, "replay": replay, "native_exits": native_exits,
                    "freeze": freeze, "analysis": analysis},
        "requests": {"configured_normal_requests": 7, "workers": 2, "actual_native_starts": 6,
                     "actual_normal_stage_requests": 4, "structural_correction_requests": 2,
                     "shared_semantic_repair_used": False,
                     "meaning": "Task, flow, graph and processing started. Graph and processing each used one correction. No task-correspondence, sensitivity or source-review request started."},
        "failure": {"stage": "initial_processing", "attempt": "structural_correction_a002",
                    "first_answer_status": "rejected_before_semantic_validation",
                    "first_answer_diagnostics": validation["diagnostics"],
                    "first_answer_semantic_coverage": None, "accepted_processing_call": chain["accepted_call"],
                    "correction_call": failed_call_summary, "native_timeout": timeout,
                    "correction_complete_output": None,
                    "qualification": "This is not revision-processing: the normal processing request produced malformed shared JSON, and its one structural correction hit the native total deadline before a complete answer. Shared semantic repair was never reached."},
        "available_generated_material": {
            "task": {"status": "complete_source_only_extraction", "requirements": len(task["requirements"]),
                     "issues": len(task["issues"]), "task_sha256": task["task_sha256"],
                     "whole_chain_source_review": None},
            "flow": {"status": "complete"},
            "initial_cfg": {"status": "accepted_initial_candidate_not_selected_bundle", "accepted_call": "calls/a002",
                            "blocks": 237, "instructions": 521, "edges": 217,
                            "source_span_copies_exact": graph_audit["counts"]["source_span_copies_exact"],
                            "remote_source_sites_represented": 13, "save_result_source_sites_represented": 25,
                            "iteration_source_sites_represented": 11,
                            "remote_explicit_receiver_and_request_operands": 6, "remote_composite_effect_summaries": 7}},
        "unavailable_results": {
            "selected_annotation": None, "selected_cfg": None, "selected_bundle": None,
            "accepted_processing_coverage": {"status": "not_available", "value": None},
            "task_correspondence": absent, "sensitivity": absent, "source_review": absent,
            "bound_input_contract_review": absent, "propagation_processed_ir": absent,
            "propagation_unmodeled_ir": absent, "propagation_blocked_ir": absent,
            "source_faithful_remote_boundaries": absent, "caller_to_filesystem_boundaries": absent,
            "demand_preparation": absent, "input_assessments": absent,
            "required_ranges": absent, "deletable_ranges": absent, "unresolved_ranges": absent,
            "doe_comparisons": absent, "doe_reductions": absent,
            "meaning": "Null denotes unavailable/not-run, not numeric zero, no_excess_established, or evidence that no input is deletable. No Skill was executed."},
        "artifact_presence": presence, "source_hash_checks": source_checks,
        "source_risks_not_final_findings": graph_audit["pending_source_questions"],
        "next_plan_evidence": [
            "The immediate delivery bottleneck is now initial processing wire validity followed by structural-correction completion. Inspect the preserved duplicate-key response and correction workload before proposing further prompt/serialization changes; do not normalize duplicate keys or claim its apparent records as validated coverage.",
            "There was no original complete annotation bundle, so retaining a previously reviewed bundle could not apply. The failure does not test the later shared-repair retention path online.",
            "Remote internal dependencies, actual filters/orderBy reads, caller storage transfer, summary provenance and loop pairing remain source-supported audit targets; this run did not produce final processing/review/DOE evidence to resolve them.",
            "No field-necessity precision or DOE improvement is established by generated graph coverage or a successful zero-call replay. Any further implementation or online run needs its own explicit authorized scope; this sole run and replay are closed."
        ],
        "audit_scope": "Read-only stdlib parsing and file-hash comparisons of this run's saved public artifacts. No validator, renderer, model, Skill, backend or replay invocation.",
        "bound_artifact_sha256": READS,
    }
    (OUT / "final-source-coverage.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = f"""# Final GA4 source and coverage assessment

Run: `{RUN.name}`. Frozen implementation: `{protocol['implementation_sha256']}`.

The run **failed in the structural correction of initial processing**. It did not reach revision-processing, source review, propagation or DOE. There is **no selected annotation or selected CFG bundle**. The completed initial graph contains **521 IR in 237 blocks with 217 edges**; this is generated representation, not processed coverage.

## Terminal evidence

- Initial processing a001 was rejected at the JSON boundary: `duplicate JSON member: shared_values`. No processing semantic validation or accepted coverage was established from that answer. Its raw records remain preserved; duplicate keys were not normalized away.
- Processing correction a002 reached the 2,700-second native total deadline (`{timeout['elapsed_seconds']:.6f}` seconds), with confirmed process exit and no complete response. The controller's analysis elapsed time was `{analysis['analysis_seconds']:.6f}` seconds.
- Actual starts: **6 = 4 normal stage requests + 2 structural corrections**. Seven normal requests and two workers remained configured; only Task, flow, graph and processing were reached. Shared semantic repair was never used.
- The sole controller replay **matched in {replay['elapsed_seconds']:.6f} seconds with 0 new native starts**. This reproduces the recorded failed frontier; it does not establish semantic or DOE correctness.
- All six native attempt exits are confirmed by the saved exit receipts. The controller closed at `{controller['finished_at']}` and records unchanged frozen implementation/helpers/executables.
- The fatal-frontier receipt binds {bound_count} existing artifact references; this passive audit found their hashes matching. All 16 frozen source files still match the initial inventory and protocol.

## Available material and unavailable results

| Item | Evidence |
|---|---|
| Task | Source-only extraction completed: {len(task['requirements'])} requirements, {len(task['issues'])} issues. No whole-chain source review followed. |
| Flow | Completed working document. |
| Initial graph | a002 accepted after one graph correction; 237 blocks / 521 IR / 217 edges. |
| Processing | a001 malformed; a002 incomplete; accepted_call is null and no processing value/result artifact exists. |
| Selected bundle, annotation, revised material | Absent. |
| Task correspondence, sensitivity, source review | Not run. |
| Bound contract-review receipt | Absent. |
| Propagation, demand preparation, input assessments | Not run. Counts are unavailable/null. |
| DOE comparisons, reductions or deletable ranges | Not run. Counts are unavailable/null. |

Unavailable is **not zero coverage, zero deletable inputs, or no_excess_established**. No final required/deletable/unresolved range classifications were computed. No actual Skill execution occurred.

## What the generated graph does and does not establish

The independent source inventory has 13 remote call sites, 25 saveResult caller sites and 11 loop/map/filter/sort sites. All have source-matched generated representations in the accepted initial graph, and all 294 copied source spans match exactly. This establishes source-location representation only.

Six remote IR carry explicit receiver results and request/body operands. Four realtime and three metadata operations instead describe getClient/getPropertyId inside composite effect text. Whether processing establishes the internal authentication, cached receiver and property routing dependencies is unknown because there is no accepted processing result.

All 25 saveResult call summaries and the independent filesystem writer ir_453 are present. Their presence does not prove caller-to-filesystem payload/receiver transfer. That eventual coverage count remains null.

The two initial graph filter-head errors were corrected by separate retained-accumulator values (ir_482 and ir_501), keeping the rejection and acceptance branches. This is a source-consistent generated state-flow correction; no backend loop completion or member-pairing result followed.

## Concrete source risks still awaiting analysis

1. **Actual unused reads:** `reports.ts:78-86` destructures filters/orderBy; the outgoing request omits both. ir_089 lists them only as unused_destructured_fields metadata, without distinct produced values. Actual read/observation retention and the documented filtering/sorting mismatch remain unverified. This is not a deletion verdict.
2. **Composite remote inputs:** the seven realtime/metadata boundaries need explicit processing evidence for receiver, credentials and routing. Physical source coverage cannot establish that evidence.
3. **Storage transfer and metadata:** each caller's data/category/operation/extraInfo must be connected to `storage.ts:79-92`, including conditional metadata, path identity and directory creation. No such propagation result exists.
4. **Summary provenance:** ir_517/519/520 represent the required saved-JSON read and Markdown summary/write. The graph explicitly leaves invocation-to-file provenance and concrete writer/filename unspecified. No mapping/review resolved those specific relationships.
5. **Loops and conditions:** filtering, sorting, optional limits, sequential URL/result pairing and caught-error alternatives remain requirements for subsequent processing and review. Their generated presence is not evidence of successful preservation checks.

The new result supports prioritizing strict shared-JSON output construction and completion within the existing correction budget. It does not support weakening duplicate-key validation or claiming the intended field-necessity improvement. The original-bundle retention fallback was inapplicable because this run never formed an initial bundle. Further proposals should keep these delivery failures separate from the untested source-semantic risks above.

This audit read saved public artifacts only. It did not invoke a validator, renderer, model, Skill, backend or replay. The sole authorized run and its controller replay are closed.
"""
    (OUT / "final-source-coverage.en.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status": output["status"], "initial_graph_ir": 521,
                      "selected_annotation": None, "propagation_coverage": None, "doe_results": None,
                      "frontier_reference_count": bound_count, "replay": replay}))


if __name__ == "__main__":
    main()
