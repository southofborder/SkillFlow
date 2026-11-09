"""Prepare, run or replay one whole-Skill document-guided analysis.

The core owns the steps. The current entry supplies the lightweight isolated
CLI client without confirmation calls, historical harness pins or probes.
"""
import argparse
import json
from pathlib import Path
import sys

from skillflow.document_guided.runner import prepare, run, replay
from tools.doe.document_guided_metrics import transport_metrics


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("prepare", help="Freeze one source package without model calls")
    create.add_argument("--input", required=True)
    create.add_argument("--effort", choices=("max", "high"), default="max",
        help="Reasoning effort frozen for every analysis stage; the default remains max")
    execute = commands.add_parser("run", help="Execute or resume the fixed isolated request sequence")
    execute.add_argument("--executable", type=Path, help="Optional local Codex CLI executable; otherwise resolve the installation")
    execute.add_argument("--timeout", type=float, default=2700, help="Per-process timeout in seconds")
    execute.add_argument("--retries", type=int, choices=(0, 1, 2), default=2,
        help="Maximum extra attempts for exited transient network failures without an answer")
    offline = commands.add_parser("replay", help="Rebuild decisions from saved responses with zero calls")
    for command in (create, execute, offline):
        command.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = prepare(args.input, run_dir=args.run_dir, config={"reasoning_effort": args.effort})
    elif args.command == "replay":
        result = replay(args.run_dir)
    else:
        from tools.doe.document_guided_client import Client, read
        from skillflow.common.artifacts import ArtifactWriter
        config = read(args.run_dir / "manifest.json")["config"]
        result = run(args.run_dir,
            client_factory=lambda name, owner: Client(args.run_dir / "transport" / name, owner=owner,
                executable=args.executable, timeout=args.timeout, retries=args.retries, config=config),
            progress=lambda value: print(value["stage"], value["stages"].get(value["stage"]), flush=True))
        try:
            ArtifactWriter(()).json(args.run_dir / "metrics.json", transport_metrics(args.run_dir))
        except (OSError, ValueError, TypeError, KeyError) as error:
            print("CLI monitoring could not be written: " + str(error), file=sys.stderr, flush=True)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0 if result.get("status", "prepared") in {"prepared", "complete", "partial", "diagnostic_complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
