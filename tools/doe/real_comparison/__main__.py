"""Command line interface for the isolated real-Skill comparison.

No command installs a Skill or dispatches a model. Workers publish requests for
the supervising Codex dispatcher; formal execution requires actual human input.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .protocol import prepare_protocol, write_json

DEFAULT_CORPUS = "experiments/doe/inputs/clawhub-top1000-v1"


def _prepare_timed_packets(run_dir):
    """Build all anonymous timed panes after output closure, without a gold ledger."""
    from .results import verify_output_freeze
    from .review import write_timed_packet
    from .protocol import SCHEMA, sha256
    run = Path(run_dir)
    verify_output_freeze(run)
    assignments = json.loads((run / "review/private-assignment-map.json").read_text(encoding="utf-8"))["assignments"]
    if len(assignments) != 72 or len({r["assignment_id"] for r in assignments}) != 72:
        raise ValueError("Timed packets require all 72 prespecified independent assignments")
    files = {}
    for item in assignments:
        workflow = run / "workflows" / f"{item['case_id']}_{item['method']}_r1"
        candidate = workflow / "candidate-view.txt"
        answer = (candidate.read_text(encoding="utf-8") if candidate.exists()
                  else "No auditable candidate output was produced. Check the retained execution failure record.")
        source = (run / "cases" / item["case_id"] / "source-bundle.txt").read_text(encoding="utf-8")
        path = run / "review/timed-packets" / (item["assignment_id"] + ".html")
        write_timed_packet(path, item, source, answer)
        files[path.relative_to(run).as_posix()] = sha256(path)
    seal = {"schema_version": SCHEMA, "files": files,
            "assignment_map_sha256": sha256(run / "review/private-assignment-map.json"),
            "output_freeze_sha256": sha256(run / "output-freeze.json"),
            "references_in_timed_packets": False, "model_calls": 0}
    write_json(run / "review/timed-packet-freeze.json", seal, immutable=True)
    return {"timed_packets": len(files), "references_in_timed_packets": False, "model_calls": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("acquire", "verify-corpus", "manifest-corpus", "screen", "select", "prepare",
                                               "worker", "pending", "authorize", "import-response", "stop-request",
                                               "import-human", "freeze-references", "freeze-gate", "freeze-outputs",
                                               "prepare-scoring-packets", "prepare-timed-packets",
                                               "import-grade", "import-timed", "import-timed-adjudication",
                                               "prepare-corrigendum", "import-corrigendum", "activate-corrigendum",
                                               "grade", "costs", "report", "replay"))
    parser.add_argument("--corpus-root", default=DEFAULT_CORPUS)
    parser.add_argument("--run-dir")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--screening-path")
    parser.add_argument("--submission")
    parser.add_argument("--workflow-id")
    parser.add_argument("--request-id")
    parser.add_argument("--source-path")
    parser.add_argument("--prompt-path")
    parser.add_argument("--receipt-path")
    parser.add_argument("--original-workflow-id")
    parser.add_argument("--mode", choices=("formal", "calibration"), default="formal")
    parser.add_argument("--reason")
    parser.add_argument("--case-id")
    parser.add_argument("--corrigendum-id")
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args(argv)
    if args.command not in {"acquire", "verify-corpus", "manifest-corpus", "screen", "select"} and not args.run_dir:
        parser.error("--run-dir is required for this command")
    run = Path(args.run_dir) if args.run_dir else None
    if args.command in {"acquire", "verify-corpus"}:
        from .acquisition import collect_roster, acquire_corpus, verify_corpus
        if args.command == "acquire":
            collect_roster(args.corpus_root, target_count=1000)
            result = acquire_corpus(args.corpus_root, workers=args.workers, retry_failed=args.retry_failed)
        else:
            result = verify_corpus(args.corpus_root)
        # Keep a full local record while returning a concise console summary.
        output = {k: v for k, v in result.items() if k not in {"items", "not_attempted"}}
    elif args.command == "screen":
        from .selection import screen_corpus
        result = screen_corpus(args.corpus_root, screening_path=args.screening_path)
        output = {k: v for k, v in result.items() if k != "entries"}
    elif args.command == "manifest-corpus":
        from .reporting import corpus_manifest
        output = corpus_manifest(args.corpus_root)
    elif args.command == "select":
        from .selection import select_cases
        output = select_cases(args.corpus_root, screening_path=args.screening_path)
    elif args.command == "prepare":
        from .inputs import prepare_inputs
        output = prepare_inputs(run, args.corpus_root, screening_path=args.screening_path)
    elif args.command == "worker":
        from .execution import run_workflow
        if not args.workflow_id or not args.source_path:
            parser.error("worker requires --workflow-id and --source-path")
        result = run_workflow(run, args.workflow_id, source_path=args.source_path, mode=args.mode,
                              prompt=Path(args.prompt_path).read_text(encoding="utf-8") if args.prompt_path else None,
                              original_workflow_id=args.original_workflow_id)
        output = {k: v for k, v in result.items() if k != "native"}
    elif args.command in {"pending", "authorize", "import-response", "stop-request"}:
        from .execution import pending_requests, authorize_dispatch, import_response, stop_request
        if args.command == "pending":
            output = pending_requests(run)
        elif not args.request_id:
            parser.error("--request-id is required")
        elif args.command == "authorize":
            output = authorize_dispatch(run, args.request_id)
        elif args.command == "import-response":
            if not args.receipt_path:
                parser.error("--receipt-path is required")
            result = import_response(run, args.request_id, receipt_path=args.receipt_path)
            output = {k: v for k, v in result.items() if k != "answer"}
        else:
            output = stop_request(run, args.request_id, args.reason or "Explicit supervisor stop")
    elif args.command == "prepare-corrigendum":
        from .corrigenda import prepare_corrigendum
        if not args.case_id or not args.submission or not args.reason:
            parser.error("--case-id, --submission (proposed reference JSON) and --reason are required")
        output = prepare_corrigendum(run, case_id=args.case_id, new_reference_path=args.submission, reason=args.reason)
    elif args.command == "import-corrigendum":
        from .corrigenda import import_corrigendum_confirmation
        if not args.corrigendum_id or not args.submission:
            parser.error("--corrigendum-id and --submission (actual human confirmation) are required")
        output = import_corrigendum_confirmation(run, args.corrigendum_id, args.submission)
    elif args.command == "activate-corrigendum":
        from .corrigenda import activate_corrigendum
        if not args.corrigendum_id:
            parser.error("--corrigendum-id is required")
        output = activate_corrigendum(run, args.corrigendum_id)
    elif args.command == "import-human":
        from .assessment import import_human_attestation
        if not args.submission:
            parser.error("--submission is required for an actual human submission")
        output = import_human_attestation(run, args.submission)
    elif args.command == "freeze-references":
        from .assessment import finalize_human_references
        selection = json.loads((run / "selection.json").read_text(encoding="utf-8"))
        output = finalize_human_references(run, selection["selected"] + selection["reserves"])
    elif args.command == "grade":
        from .results import aggregate_scores
        output = aggregate_scores(run)
    elif args.command == "import-grade":
        from .results import import_grade
        if not args.submission:
            parser.error("--submission is required for an actual human score")
        output = import_grade(run, args.submission)
    elif args.command == "freeze-outputs":
        from .results import freeze_outputs
        result = freeze_outputs(run)
        output = {k: v for k, v in result.items() if k != "files"}
    elif args.command == "freeze-gate":
        from .execution import build_formal_gate
        output = build_formal_gate(run)
    elif args.command == "prepare-scoring-packets":
        from .review import prepare_scoring_packets
        output = prepare_scoring_packets(run)
    elif args.command == "prepare-timed-packets":
        output = _prepare_timed_packets(run)
    elif args.command == "costs":
        from .metrics import cost_ledger
        result = cost_ledger(run)
        output = {k: v for k, v in result.items() if k not in {"requests", "workflows"}}
    elif args.command in {"import-timed", "import-timed-adjudication"}:
        from .review import import_timed_submission, import_timed_adjudication
        if not args.submission:
            parser.error("--submission is required for an actual human record")
        output = (import_timed_submission if args.command == "import-timed" else import_timed_adjudication)(run, args.submission)
    elif args.command == "report":
        from .reporting import report
        result = report(run, args.corpus_root)
        output = {k: v for k, v in result.items() if k != "acquisition"}
    else:
        from .execution import replay_execution
        from .selection import verify_reference_packets
        from .protocol import sha256
        protocol = json.loads((run / "protocol-freeze.json").read_text(encoding="utf-8"))
        errors = [p for p, digest in protocol["files"].items() if sha256(run / p) != digest]
        output = {"protocol_errors": errors, "execution": replay_execution(run), "model_calls": 0}
        if (run / "cases" / "index.json").exists():
            output["packets"] = verify_reference_packets(args.corpus_root, run / "cases")
        derived = {}
        if (run / "schedule.json").exists() and (run / "selection.json").exists():
            from .results import aggregate_scores
            try:
                scores = aggregate_scores(run)
                derived["scoring"] = {"status": "regenerated", "complete": scores["complete"],
                                      "planned_results": scores["planned_results"],
                                      "all_planned_in_denominator": scores["all_planned_in_denominator"],
                                      "inferential_status": scores["inferential_status"], "model_calls": 0}
            except (ValueError, OSError, KeyError) as error:
                derived["scoring"] = {"status": "failed", "reason": str(error), "model_calls": 0}
        else:
            derived["scoring"] = {"status": "not_prepared", "complete": False,
                                  "reason": "The frozen schedule and selection are not both present; no human scores were created.", "model_calls": 0}
        from .metrics import cost_ledger
        try:
            costs = cost_ledger(run)
            derived["costs"] = {"status": "regenerated", "request_records": len(costs["requests"]),
                                "workflow_records": len(costs["workflows"]),
                                "observed_response_ids": costs["target_usage"]["response_count"],
                                "usage_totals": costs["target_usage"]["totals"], "model_calls": 0}
        except (ValueError, OSError, KeyError) as error:
            derived["costs"] = {"status": "failed", "reason": str(error), "model_calls": 0}
        if not any(result["status"] == "failed" for result in derived.values()):
            from .reporting import report
            try:
                readiness = report(run, args.corpus_root)
                derived["report"] = {"status": "regenerated", "semantic_comparison": readiness["semantic_comparison"],
                                     "selected_cases": readiness["selected_cases"], "formal_gate_state": readiness["formal_gate_state"],
                                     "advantage_conclusion": readiness["advantage_conclusion"], "model_calls": 0}
            except (ValueError, OSError, KeyError) as error:
                derived["report"] = {"status": "failed", "reason": str(error), "model_calls": 0}
        else:
            derived["report"] = {"status": "not_regenerated", "reason": "Invalid scoring or cost evidence prevents rendering a report from potentially stale derived artifacts.", "model_calls": 0}
        output["derived_artifacts"] = derived
        output["semantic_comparison_complete"] = derived["scoring"].get("complete", False)
        output["passed"] = (not errors and output["execution"]["status"] == "passed"
                            and output.get("packets", {}).get("verified", True)
                            and not any(result["status"] == "failed" for result in derived.values()))
        write_json(run / "replay.json", output)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
