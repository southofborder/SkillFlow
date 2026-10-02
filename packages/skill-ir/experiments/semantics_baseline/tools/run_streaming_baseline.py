"""Run a separate SSE transport experiment with the frozen baseline semantics.

Always supply a new --run-dir; non-streaming identities cannot be resumed here.
Use --check for an offline preflight and --max-new-trials 1 for one full-input
probe. This entrypoint must run in its own otherwise single-threaded process.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from run_baseline import (
    BASE, baseline_definition, experiment_identity, resolve_experiment,
    restart_provenance, run_resumable_experiment, runtime_provenance,
    validate_baseline_resolved, verify_freeze,
)
import stream_transport


def streaming_provenance():
    provenance = runtime_provenance()
    provenance["transport"] = deepcopy(stream_transport.TRANSPORT_POLICY)
    provenance["transport"]["source_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (Path(__file__), Path(stream_transport.__file__))
    }
    return provenance


def validate_streaming_baseline(resolved):
    validate_baseline_resolved(resolved)
    if resolved.definition.repetitions != 3 or len(resolved.variants) != 1:
        raise ValueError("The baseline requires one variant and exactly three repetitions")


def require_streaming_directory(path: Path):
    identity = path.expanduser().resolve() / "experiment.json"
    if identity.exists():
        previous = json.loads(identity.read_text(encoding="utf-8"))
        if previous.get("provenance", {}).get("transport", {}).get("protocol") != stream_transport.TRANSPORT_POLICY["protocol"]:
            raise ValueError("SSE requires a new run directory; non-streaming results cannot be mixed")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--restart-of", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-new-trials", type=int)
    parser.add_argument("--max-consecutive-errors", type=int, default=1)
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--split", choices=("all", "development", "holdout", "held_out"), default="development")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require_streaming_directory(args.run_dir)
    verify_freeze(BASE)
    splits = baseline_definition()
    config = BASE / "baseline.json"
    resolved = resolve_experiment(config, env_file=args.env_file)
    validate_streaming_baseline(resolved)
    provenance = streaming_provenance()
    if args.restart_of:
        provenance["restart_of"] = restart_provenance(args.restart_of, args.run_dir)
    identity = experiment_identity(resolved, splits, provenance)
    selected = "held_out" if args.split == "holdout" else args.split
    if args.check:
        print(json.dumps({
            "mode": "offline_sse_preflight", "planned": 90,
            "selected": sum(selected == "all" or value == selected for value in splits.values()) * 3,
            "variants": identity["variants"], "transport": provenance["transport"],
            "semantic_review_status": "pending_joint_review",
        }, ensure_ascii=False, indent=2))
        return 0
    previous = None

    def progress(report):
        nonlocal previous
        current = json.dumps({
            "status": report["status"],
            "trials": dict(Counter(item["status"] for item in report["trials"])),
            "scheduler": report["scheduler"], "transport": "chat-completions-sse-v1",
        }, ensure_ascii=False, sort_keys=True)
        if current != previous:
            print(current, flush=True)
            previous = current

    with stream_transport.isolated_streaming_client():
        result = run_resumable_experiment(
            config, run_directory=args.run_dir, case_splits=splits, split=selected,
            workers=args.workers, provenance=provenance, env_file=args.env_file,
            max_new_trials=args.max_new_trials, max_consecutive_errors=args.max_consecutive_errors,
            stop_file=args.stop_file, validate_resolved=validate_streaming_baseline,
            on_progress=progress,
        )
    print(json.dumps({"run_directory": str(result.run_directory), "status": result.status}, ensure_ascii=False))
    return 0 if result.status in {"complete", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
