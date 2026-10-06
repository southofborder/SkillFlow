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
        prog="skillflow", description="Construct and inspect SkillFlow graphs."
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
    for command in (analyze, render, experiment):
        command.add_argument("--env-file", default=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
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
