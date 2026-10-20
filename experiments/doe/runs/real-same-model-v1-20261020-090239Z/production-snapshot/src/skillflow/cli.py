"""Unified command-line interface; execution lives in reusable services."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from skillflow.graph.artifacts.analysis_json import load_analysis_cfg
from skillflow.graph.artifacts.analysis_json import load_candidate_file
from skillflow.graph.artifacts.analysis_json import serialize_analysis_result
from skillflow.graph.artifacts.mermaid import render_mermaid
from skillflow.graph.extraction.pipeline import analyze_skill
from skillflow.common.llm import LlmClient
from skillflow.common.llm import LlmClientError
from skillflow.common.llm import LlmConfig


def _write_or_print(text: str, output: str | None) -> None:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
        print(f"[ok] wrote {path}", file=sys.stderr)
    else:
        print(text.rstrip("\n"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillflow", description="Construct graphs and run recorded SkillFlow analysis."
    )
    parser.add_argument(
        "--env-file",
        help="Explicit environment file; process variables take precedence",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    analyze = commands.add_parser("analyze", help="Analyze one Skill directory or ZIP")
    analyze.add_argument("--input", required=True)
    analyze.add_argument("--output", "-o")
    analyze.add_argument("--candidate", help="Compile a fixed candidate offline")
    analyze.add_argument("--max-repair-rounds", type=int, default=3)
    render = commands.add_parser(
        "render", help="Render an accepted analysis as Mermaid"
    )
    render.add_argument("--input", required=True)
    render.add_argument("--output", "-o")
    experiment = commands.add_parser("experiment", help="Run a versioned experiment")
    experiment.add_argument("--config", required=True)
    experiment.add_argument("--output-dir")
    pipeline = commands.add_parser("pipeline", help="Source-only Task extraction, fixed-Task annotation, bounded review, propagation and DOE")
    stages = pipeline.add_subparsers(dest="pipeline_command", required=True)
    prepare = stages.add_parser("prepare", help="Freeze a Skill and an existing CFG without model calls")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--analysis", required=True)
    prepare.add_argument("--run-dir", required=True)
    prepare.add_argument("--request-file", type=Path)
    execute = stages.add_parser("run", help="Execute or resume the prepared chain")
    execute.add_argument("--run-dir", required=True)
    replay = stages.add_parser("replay", help="Rebuild saved stage decisions with zero API calls")
    replay.add_argument("--run-dir", required=True)
    for command in (prepare, execute):
        command.add_argument("--env-file", default=argparse.SUPPRESS)
    for command in (analyze, render, experiment):
        command.add_argument("--env-file", default=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.command == "pipeline":
            from skillflow.pipeline import prepare_analysis_run, run_analysis, replay_analysis
            if args.pipeline_command == "replay":
                if args.env_file is not None:
                    parser.error("Offline pipeline replay does not accept --env-file")
                result = replay_analysis(args.run_dir)
            else:
                from skillflow.propagation.annotation.config import annotation_public_config
                config = LlmConfig.from_env(env_file=args.env_file)
                public = annotation_public_config(config)
                secrets = (config.api_key,) if config.api_key else ()
                if args.pipeline_command == "prepare":
                    result = prepare_analysis_run(args.input, args.analysis, run_dir=args.run_dir,
                        config=public, secrets=secrets,
                        user_request=None if args.request_file is None else args.request_file.read_bytes().decode("utf-8-sig"))
                    print(result["preparation_status"], Path(args.run_dir).resolve())
                    return 0 if result["preparation_status"] == "ready" else 1
                from skillflow.common.recording import streaming_factory
                factory, secrets = streaming_factory(public, env_file=args.env_file)
                result = run_analysis(args.run_dir, config=public, client_factory=factory, secrets=secrets,
                                      progress=lambda message: print(message, flush=True))
            print(result["status"], result["reason"], Path(args.run_dir).resolve(), flush=True)
            return 0 if result["status"] == "complete" else 130 if result["status"] == "interrupted" else 1
        if args.command == "render":
            _write_or_print(render_mermaid(load_analysis_cfg(args.input)), args.output)
            return 0
        if args.command == "experiment":
            from skillflow.graph.experiments.runner import run_experiment

            result = run_experiment(
                args.config, output_dir=args.output_dir, env_file=args.env_file
            )
            print(f"[{result.status}] {result.run_directory / 'report.json'}")
            return (
                0
                if result.status == "complete"
                else 130 if result.status == "interrupted" else 1
            )
        candidate = load_candidate_file(args.candidate) if args.candidate else None
        client = (
            None
            if candidate is not None
            else LlmClient(LlmConfig.from_env(env_file=args.env_file))
        )
        result = analyze_skill(
            args.input,
            client=client,
            candidate=candidate,
            max_repair_rounds=args.max_repair_rounds,
        )
        _write_or_print(
            json.dumps(serialize_analysis_result(result), ensure_ascii=False, indent=2),
            args.output,
        )
        return 0 if result.status == "complete" else 1
    except (LlmClientError, OSError, ValueError, TypeError) as error:
        print(f"[error] {error}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("[interrupted]", file=sys.stderr)
        return 130
