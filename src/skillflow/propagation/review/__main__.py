"""Prepare, run once, and replay the sidecar annotation review."""
from __future__ import annotations

import argparse
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Focused joint-annotation review with at most one complete repair; CFG remains unchanged")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="Read-only validation of completed annotation and freezing of review materials")
    prepare.add_argument("--annotation-run", type=Path, required=True)
    prepare.add_argument("--run-dir", type=Path, required=True)
    prepare.add_argument("--env-file", type=Path)
    run = sub.add_parser("run", help="One independent review, or resume from accepted responses")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--env-file", type=Path)
    replay = sub.add_parser("replay", help="Strict offline replay of saved responses; no online client is created")
    replay.add_argument("--run-dir", type=Path, required=True)
    refine = sub.add_parser("refine", help="Initial review, one complete repair if issues are found, and independent final review")
    refine.add_argument("--annotation-run", type=Path, help="Current completed annotation for initial preparation")
    refine.add_argument("--run-dir", type=Path, required=True)
    refine.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    from skillflow.propagation.review.runner import prepare_run
    from skillflow.propagation.review.runner import run_review
    from skillflow.propagation.review.runner import replay_run
    if args.command == "replay":
        from skillflow.common.recording import read_json
        from skillflow.propagation.review.refinement import IDENTITY
        from skillflow.propagation.review.refinement import replay_refinement
        identity = read_json(args.run_dir / "manifest.json").get("identity")
        result = replay_refinement(args.run_dir) if identity == IDENTITY else replay_run(args.run_dir)
    else:
        from skillflow.common.llm.config import LlmConfig
        from skillflow.propagation.annotation.config import annotation_public_config
        config = LlmConfig.from_env(env_file=args.env_file)
        public = annotation_public_config(config)
        secrets = (config.api_key,) if config.api_key else ()
        if args.command == "refine":
            from skillflow.propagation.review.refinement import prepare_refinement_run
            from skillflow.propagation.review.refinement import run_refinement
            if not (args.run_dir / "manifest.json").exists():
                if args.annotation_run is None:
                    parser.error("Initial refine requires --annotation-run")
                from skillflow.propagation.annotation.loading import load_annotation_run
                original = load_annotation_run(args.annotation_run)
                prepare_refinement_run(None, None,
                    original["material"], original["raw_annotation"], run_dir=args.run_dir,
                    provenance={"kind": "accepted_annotation", "upstream_identity": original["upstream_identity"]},
                    config=public, secrets=secrets, upstream_run=args.annotation_run)
            result = run_refinement(args.run_dir, config=public, env_file=args.env_file, secrets=secrets,
                                    progress=lambda message: print(message, flush=True))
            print(result["status"], args.run_dir.resolve())
            return 0 if result["status"] == "review_passed" else 1
        if args.command == "prepare":
            manifest = prepare_run(args.annotation_run, run_dir=args.run_dir, config=public, secrets=secrets)
            print(manifest["preparation_status"], args.run_dir.resolve())
            return 0
        result = run_review(args.run_dir, config=public, env_file=args.env_file, secrets=secrets,
                            progress=lambda message: print(message, flush=True))
    print(result["status"], result.get("summary"), args.run_dir.resolve())
    return 0 if result["status"] in {"complete", "review_passed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
