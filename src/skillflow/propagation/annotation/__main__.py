"""Prepare, structurally correct, or replay an independent joint annotation."""
from __future__ import annotations

import argparse
from pathlib import Path

from skillflow.propagation.annotation.config import annotation_public_config


def main(argv=None):
    parser = argparse.ArgumentParser(description="Independent security-semantic annotation of the complete Skill and original CFG; no propagation or risk judgment")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="Freeze inputs, validate the graph and prepare annotation offline")
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--analysis", type=Path, required=True)
    prepare.add_argument("--run-dir", type=Path, required=True)
    prepare.add_argument("--task-run", type=Path, required=True, help="Completed independent source-only Task extraction run")
    prepare.add_argument("--env-file", type=Path, help="Read only public configuration for identity binding; no API calls")
    prepare.add_argument("--request-file", type=Path, help="Optional independent user-request text")
    run = sub.add_parser("run", help="Run or resume annotation with unlimited structural correction; semantic review is separate")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--env-file", type=Path)
    replay = sub.add_parser("replay", help="Replay saved responses only, with zero API calls")
    replay.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    from skillflow.propagation.annotation.runner import prepare_run
    from skillflow.propagation.annotation.runner import run_annotation
    from skillflow.propagation.annotation.runner import replay_run
    if args.command == "replay":
        result = replay_run(args.run_dir)
    else:
        from skillflow.common.llm.config import LlmConfig
        config = LlmConfig.from_env(env_file=args.env_file)
        public = annotation_public_config(config)
        secrets = (config.api_key,) if config.api_key else ()
        if args.command == "prepare":
            manifest = prepare_run(args.input, args.analysis, run_dir=args.run_dir, config=public, secrets=secrets, task_run=args.task_run,
                user_request=None if args.request_file is None else args.request_file.read_bytes().decode("utf-8-sig"))
            print(f"{manifest['preparation_status']}; {args.run_dir.resolve()}")
            return 0 if manifest["preparation_status"] == "ready" else 1
        from skillflow.common.recording import streaming_factory
        # Binding is checked before an online client is instantiated by its factory.
        factory, secrets = streaming_factory(public, env_file=args.env_file)
        result = run_annotation(args.run_dir, client_factory=factory, config=public, secrets=secrets,
                                progress=lambda text: print(text, flush=True))
    print(f"{result['status']}; {result['reason']}; {args.run_dir.resolve()}", flush=True)
    return 0 if result["status"] in {"complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
