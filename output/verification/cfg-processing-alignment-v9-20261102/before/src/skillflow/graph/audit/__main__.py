"""CLI kept separate from all production Skill-IR entry points."""

import argparse
from datetime import datetime, timezone
from pathlib import Path

from skillflow.common.recording import streaming_factory
from skillflow.graph.audit.runner import experiment_root
from skillflow.graph.audit.runner import SUITES
from skillflow.graph.audit.runner import execute_run
from skillflow.graph.audit.runner import prepare_run
from skillflow.graph.audit.runner import public_config


def main(argv=None):
    parser = argparse.ArgumentParser(description="Controlled retelling and complete-source review v7: semantic comparison and fact checks, one logical call per case")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "run", "replay"):
        command = commands.add_parser(name)
        command.add_argument("--run-dir", type=Path, required=name == "replay")
        command.add_argument("--renderer", type=Path, help="Proven Lean controlled-printer executable")
        if name != "replay":
            command.add_argument("--suite", choices=tuple(SUITES), default=None,
                                 help="Default: f01-five; semantics-v5-seven also includes the paused-batch 001 and 010 round-zero graphs")
            command.add_argument("--max-audit-execution-retries", type=int, default=None)
        if name == "run":
            command.add_argument("--env-file", type=Path)
            command.add_argument("--workers", type=int, default=2)
    args = parser.parse_args(argv)
    directory = args.run_dir or experiment_root() / "runs" / ("controlled-v7-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if args.command == "prepare":
        manifest = prepare_run(directory, executable=args.renderer, suite=args.suite or "f01-five",
                               max_audit_execution_retries=2 if args.max_audit_execution_retries is None else args.max_audit_execution_retries)
        print(f"Offline preparation complete: {directory.resolve()}", flush=True)
        from skillflow.graph.audit.runner import read_json
        review = read_json(directory / "verification/review30.json")
        return 0 if all(c["fidelity_status"] == "passed" for c in manifest["cases"]) and all(s["status"] == "passed" for s in review["samples"]) else 1
    if args.command == "replay":
        result = execute_run(directory, replay=True, executable=args.renderer, progress=lambda value: print(value, flush=True))
    else:
        if not (directory / "manifest.json").exists():
            prepare_run(directory, executable=args.renderer, suite=args.suite or "f01-five",
                        max_audit_execution_retries=2 if args.max_audit_execution_retries is None else args.max_audit_execution_retries)
        from skillflow.graph.audit.runner import verify_run
        manifest = verify_run(directory, live=True)
        if args.suite is not None and manifest["suite"] != args.suite:
            parser.error("--suite differs from the prepared run")
        if args.max_audit_execution_retries is not None and manifest["policy"]["max_audit_execution_retries"] != args.max_audit_execution_retries:
            parser.error("--max-audit-execution-retries differs from the prepared run")
        factory, secrets = streaming_factory(public_config(), env_file=args.env_file)
        result = execute_run(directory, client_factory=factory, secrets=secrets, workers=args.workers, executable=args.renderer,
                             progress=lambda value: print(value, flush=True))
    print(f"{result['execution_status']}; recorded {result['recorded_logical_calls']}/{result['planned_logical_calls']} logical calls; "
          f"{result['recorded_execution_calls']} executions, {result['http_attempts']} HTTP attempts; {directory.resolve()}", flush=True)
    return 0 if result["execution_status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
