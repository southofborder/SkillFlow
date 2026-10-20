"""Formal deterministic DOE from a verified propagation run."""
from __future__ import annotations
import argparse
from pathlib import Path
from skillflow.common.artifact_io import ArtifactWriteError
from .formal_runner import run_doe, replay_doe


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Analyze verified propagation facts without model calls")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Compute DOE from the accepted joint annotation and propagation")
    run.add_argument("--propagation-run", type=Path, required=True)
    run.add_argument("--run-dir", type=Path, required=True)
    replay = commands.add_parser("replay", help="Validate and recompute the recorded formal DOE run offline")
    replay.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            result = run_doe(args.propagation_run, run_dir=args.run_dir)
            status = result["manifest"]["status"]
        else:
            status = replay_doe(args.run_dir)["status"]
    except (OSError, ValueError, TypeError, ArtifactWriteError) as error:
        parser.exit(2, str(error) + "\n")
    except KeyboardInterrupt:
        parser.exit(130, "Interrupted; resume with the same recorded inputs.\n")
    print(status)
    return 0 if status in {"matched", "complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
