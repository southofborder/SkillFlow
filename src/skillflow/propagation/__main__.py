"""Offline propagation command; it never creates a model client."""
from __future__ import annotations

import argparse
from pathlib import Path

from skillflow.propagation.runner import replay_propagation
from skillflow.propagation.runner import run_propagation


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run basic data propagation or replay saved records offline")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Load current-format annotation and propagate offline")
    run.add_argument("--annotation-run", type=Path, required=True)
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--seed-data", type=Path)
    run.add_argument("--seed-state", type=Path, help="Optional FlowState JSON; an explicitly empty state is not replaced by automatic sources")
    replay = commands.add_parser("replay", help="Validate saved inputs and solve again with zero API calls")
    replay.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = (run_propagation(args.annotation_run, run_dir=args.run_dir, seed_data=args.seed_data,
                                  initial_state=args.seed_state)
                  if args.command == "run" else replay_propagation(args.run_dir))
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + "\n")
    print(result.status)
    return 0 if result.status == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
