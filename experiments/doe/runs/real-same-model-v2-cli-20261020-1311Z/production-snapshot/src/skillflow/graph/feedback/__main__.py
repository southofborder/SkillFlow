"""Explicit bounded semantic feedback CLI; the single-analysis CLI is unchanged."""

from __future__ import annotations

import argparse
from pathlib import Path


PUBLIC_CONFIG_FIELDS = (
    "endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
    "retry_base_ms", "retry_max_backoff_ms",
)


def _nonnegative(value):
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("The repair count must be a nonnegative integer")
    return parsed


def main(argv=None):
    parser = argparse.ArgumentParser(description="CFG semantic feedback v7: shared interpretation contract, semantic coverage review, evidence validation and bounded repair")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Start or resume the same run identity; do not automatically resend uncertain requests")
    run.add_argument("--input", type=Path, required=True, help="Skill directory or ZIP")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--initial-analysis", type=Path, help="Existing analysis.json containing a valid cfg")
    run.add_argument("--max-semantic-revisions", type=_nonnegative, default=3)
    run.add_argument("--max-structural-repairs", type=_nonnegative, default=3)
    run.add_argument("--max-audit-execution-retries", type=int, choices=range(6), default=2,
                     help="Additional execution retries for transient communication failures per review round (0-5; default 2); completed responses are not retried")
    run.add_argument("--env-file", type=Path)
    run.add_argument("--renderer", type=Path, help="Lean controlled-printer executable")
    replay = commands.add_parser("replay", help="Reparse, compile, check fidelity and review saved responses offline, with zero API calls")
    replay.add_argument("--run-dir", type=Path, required=True)
    replay.add_argument("--renderer", type=Path)
    args = parser.parse_args(argv)

    # In particular, replay neither loads credentials nor constructs a client.
    from skillflow.graph.feedback.runner import refine_skill
    from skillflow.graph.feedback.runner import replay_run
    if args.command == "replay":
        result = replay_run(args.run_dir, renderer=args.renderer)
    else:
        from skillflow.common.llm.config import LlmConfig
        from skillflow.common.recording import streaming_factory
        llm_config = LlmConfig.from_env(env_file=args.env_file)
        config = {field: getattr(llm_config, field) for field in PUBLIC_CONFIG_FIELDS}
        factory, secrets = streaming_factory(config, env_file=args.env_file)
        result = refine_skill(
            args.input, run_dir=args.run_dir, initial_analysis=args.initial_analysis,
            max_semantic_revisions=args.max_semantic_revisions,
            max_structural_repairs=args.max_structural_repairs,
            max_audit_execution_retries=args.max_audit_execution_retries,
            extraction_factory=factory, audit_factory=factory,
            config=config, secrets=secrets, renderer=args.renderer,
            progress=lambda message: print(message, flush=True),
        )
    print(f"{result['status']}; {result.get('reason', '')}; {args.run_dir.resolve()}", flush=True)
    return 0 if result["status"] == "audit_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
