"""Reusable, serial execution of case × configuration × repetition experiments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import time
from uuid import uuid4

from skillflow.graph.artifacts.analysis_json import serialize_analysis_result
from skillflow.graph.artifacts.mermaid import render_mermaid
from skillflow.graph.extraction.pipeline import analyze_skill
from skillflow.common.llm.client import LlmClient
from skillflow.graph.experiments.config import resolve_experiment
from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.artifacts import call_metrics
from skillflow.graph.experiments.report import write_progress


@dataclass(frozen=True)
class ExperimentRunResult:
    run_directory: Path
    status: str
    report: dict


def run_experiment(
    config_path: str | Path,
    *,
    output_dir: str | Path | None = None,
    env_file: str | Path | None = None,
    environ: dict[str, str] | None = None,
) -> ExperimentRunResult:
    """Run a validated experiment. Preflight errors raise before any API call.

    Runtime failures belong to individual trials; interruption leaves unfinished
    combinations explicitly not_run. No network requests occur on import.
    """
    resolved = resolve_experiment(config_path, env_file=env_file, environ=environ)
    started = datetime.now(timezone.utc)
    run_id = started.strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8]
    root = (
        Path(output_dir).expanduser().resolve()
        if output_dir is not None
        else Path.cwd() / "results/skill-ir"
    )
    directory = root / resolved.definition.name / run_id
    directory.mkdir(parents=True, exist_ok=False)
    writer = ArtifactWriter(resolved.secrets)
    writer.json(
        directory / "experiment.json",
        {
            "name": resolved.definition.name,
            "config_file": str(resolved.config_path),
            "dataset": str(resolved.dataset_path),
            "repetitions": resolved.definition.repetitions,
            "variants": [variant.snapshot() for variant in resolved.variants],
        },
    )
    writer.json(
        directory / "dataset.json",
        {
            "cases": [
                {
                    "id": case.id,
                    "input": str(case.source),
                    "extraction_input_sha256": case.sha256,
                    "files": [
                        {
                            "path": file.path,
                            "kind": file.kind,
                            "size": file.size,
                            "text_sha256": (
                                hashlib.sha256(file.content.encode()).hexdigest()
                                if file.content is not None
                                else None
                            ),
                        }
                        for file in case.package.files
                    ],
                }
                for case in resolved.cases
            ]
        },
    )
    combinations = [
        (case, variant, repetition)
        for case in resolved.cases
        for variant in resolved.variants
        for repetition in range(1, resolved.definition.repetitions + 1)
    ]
    trials = [
        {
            "case": case.id,
            "variant": variant.id,
            "repetition": repetition,
            "status": "not_run",
        }
        for case, variant, repetition in combinations
    ]
    report = {
        "mode": "online",
        "name": resolved.definition.name,
        "run_id": run_id,
        "started_at": started.isoformat(),
        "status": "running",
        "trials": trials,
    }
    write_progress(directory, report, writer)
    active = None
    try:
        for trial, (case, variant, repetition) in zip(trials, combinations):
            active = trial
            trial_dir = directory / "trials" / case.id / variant.id / str(repetition)
            trial["status"] = "running"
            trial["started_at"] = datetime.now(timezone.utc).isoformat()
            trial["artifacts"] = trial_dir.relative_to(directory).as_posix()
            trial_start = time.perf_counter()
            trace = {
                "case": case.id,
                "variant": variant.id,
                "repetition": repetition,
                "calls": [],
            }

            def checkpoint(calls):
                trace["calls"] = calls
                trial.update(call_metrics(calls))
                writer.json(trial_dir / "trace.json", trace)
                write_progress(directory, report, writer)

            client = LlmClient(variant.config, record_calls=True, on_record=checkpoint)
            try:
                checkpoint([])
                result = analyze_skill(
                    case.package,
                    client=client,
                    max_repair_rounds=variant.max_repair_rounds,
                )
                writer.json(
                    trial_dir / "analysis.json", serialize_analysis_result(result)
                )
                if result.raw_candidate:
                    writer.json(trial_dir / "candidate.json", result.raw_candidate)
                if result.cfg is not None:
                    writer.text(trial_dir / "graph.mmd", render_mermaid(result.cfg))
                trial.update(
                    status=result.status,
                    diagnostics=result.diagnostics,
                    attempts=result.attempts,
                    blocks=len(result.cfg.blocks) if result.cfg else None,
                    edges=len(result.cfg.edges) if result.cfg else None,
                    prompt_sha256=hashlib.sha256(result.prompt.encode()).hexdigest(),
                )
            except KeyboardInterrupt:
                trial["status"] = "interrupted"
                raise
            except Exception as error:
                trial.update(
                    status="error", error=str(error), error_type=type(error).__name__
                )
            finally:
                trial["elapsed_seconds"] = time.perf_counter() - trial_start
                trial["finished_at"] = datetime.now(timezone.utc).isoformat()
                checkpoint(client.call_records)
            active = None
        report["status"] = (
            "complete"
            if all(trial["status"] == "complete" for trial in trials)
            else "failed"
        )
    except KeyboardInterrupt:
        if active is not None and active["status"] == "running":
            active["status"] = "interrupted"
        report["status"] = "interrupted"
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        write_progress(directory, report, writer)
    return ExperimentRunResult(directory, report["status"], writer.clean(report))
