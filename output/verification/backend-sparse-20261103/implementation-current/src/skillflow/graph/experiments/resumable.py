"""Resumable bounded-concurrency experiments, with no semantic pass inference.

Each trial's record.json is the durable commit point. Reports are derived from
those records; a lost report write cannot cause a completed trial to be repeated.
Successful generation responses can be replayed through the unchanged pipeline.
An interrupted request with an unknown outcome is never automatically resent.
"""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Callable

from skillflow.graph.artifacts.analysis_json import serialize_analysis_result
from skillflow.graph.artifacts.mermaid import render_mermaid
from skillflow.graph.extraction.pipeline import analyze_skill
from skillflow.graph.extraction.prompt import build_whole_skill_prompt
from skillflow.common.runs import exclusive_run, ReplayClient
from skillflow.graph.experiments.config import ResolvedExperiment
from skillflow.graph.experiments.config import resolve_experiment
from skillflow.common.artifacts import ArtifactWriter
from skillflow.graph.experiments.report import aggregate
from skillflow.common.artifacts import call_metrics
from skillflow.graph.experiments.report import write_progress
from skillflow.graph.experiments.runner import ExperimentRunResult


TERMINAL = {"complete", "degraded", "error", "uncertain"}
REVIEW_PENDING = "pending_joint_review"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def experiment_identity(
    resolved: ResolvedExperiment,
    case_splits: dict[str, str],
    provenance: dict | None = None,
) -> dict:
    """Hash inputs and the exact prompt, not annotations appended to a package."""
    return {
        "schema_version": 1,
        "name": resolved.definition.name,
        "repetitions": resolved.definition.repetitions,
        "variants": [variant.snapshot() for variant in resolved.variants],
        "provenance": provenance or {},
        "cases": [
            {
                "id": case.id,
                "split": case_splits[case.id],
                "extraction_input_sha256": case.sha256,
                "prompt_sha256": hashlib.sha256(
                    build_whole_skill_prompt(case.package).encode("utf-8")
                ).hexdigest(),
            }
            for case in resolved.cases
        ],
    }


def _execute_trial(case, variant, record, directory, writer, prior_calls, client_factory):
    trial_directory = directory / record["artifacts"]
    started = time.perf_counter()
    trace = {
        "case": case.id,
        "variant": variant.id,
        "repetition": record["repetition"],
        "split": record["split"],
        "calls": prior_calls,
    }

    def checkpoint(calls):
        trace["calls"] = calls
        writer.json(trial_directory / "trace.json", trace)

    client = client_factory(
        variant.config, prior_calls=prior_calls, writer=writer, on_record=checkpoint
    )
    try:
        checkpoint(client.call_records)
        result = analyze_skill(
            case.package, client=client, max_repair_rounds=variant.max_repair_rounds
        )
        writer.json(trial_directory / "analysis.json", serialize_analysis_result(result))
        if result.raw_candidate:
            writer.json(trial_directory / "candidate.json", result.raw_candidate)
        if result.cfg is not None:
            writer.text(trial_directory / "graph.mmd", render_mermaid(result.cfg))
        record.update(
            status=result.status,
            diagnostics=result.diagnostics,
            attempts=result.attempts,
            blocks=len(result.cfg.blocks) if result.cfg else None,
            edges=len(result.cfg.edges) if result.cfg else None,
            prompt_sha256=hashlib.sha256(result.prompt.encode("utf-8")).hexdigest(),
        )
    except KeyboardInterrupt:
        record.update(status="interrupted")
    except Exception as error:
        record.update(status="error", error=str(error), error_type=type(error).__name__)
    finally:
        checkpoint(client.call_records)
        record.update(call_metrics(client.call_records))
        record["elapsed_seconds"] = record.get("elapsed_seconds", 0) + time.perf_counter() - started
        record["finished_at"] = _now()
        record["replayed_generations"] = len(prior_calls)
        record["artifact_sha256"] = {
            name: _sha(trial_directory / name)
            for name in ("trace.json", "analysis.json", "candidate.json", "graph.mmd")
            if (trial_directory / name).is_file()
        }
    return record


def _recover(record, directory):
    path = directory / record["artifacts"]
    if record["status"] in TERMINAL:
        for name, expected in record.get("artifact_sha256", {}).items():
            if not (path / name).is_file() or _sha(path / name) != expected:
                raise ValueError(f"Committed artifact changed: {record['case']}/{name}")
        return record, []
    if record["status"] not in {"not_run", "running", "interrupted"}:
        raise ValueError(f"Unknown trial status: {record['status']}")
    trace = path / "trace.json"
    calls = _read(trace)["calls"] if trace.exists() else []
    if any(call.get("status") != "complete" for call in calls):
        record.update(
            status="uncertain",
            error="A recorded request has no committed generation result; automatic resend is disabled.",
            semantic_review_status=REVIEW_PENDING,
            **call_metrics(calls),
        )
        record["artifact_sha256"] = {"trace.json": _sha(trace)}
        return record, []
    # The HTTP checkpoint is written before transmission. With no calls, no
    # request was sent; completed calls are replayable without another request.
    record["status"] = "not_run"
    return record, calls


def run_resumable_experiment(
    config_path: str | Path,
    *,
    run_directory: str | Path,
    case_splits: dict[str, str],
    split: str = "all",
    workers: int = 4,
    provenance: dict | None = None,
    env_file: str | Path | None = None,
    environ: dict[str, str] | None = None,
    on_progress: Callable[[dict], None] | None = None,
    max_new_trials: int | None = None,
    stop_file: str | Path | None = None,
    max_consecutive_errors: int = 4,
    validate_resolved: Callable[[ResolvedExperiment], None] | None = None,
    client_factory: Callable = ReplayClient,
) -> ExperimentRunResult:
    """Run/resume only pending trials; terminal failures remain visible.

    Changing split or worker count is safe. Changing inputs, effective model
    settings, prompts or supplied provenance requires a separate run directory.
    The caller supplies source/contract snapshots as provenance when applicable.
    """
    if type(workers) is not int or not 1 <= workers <= 32:
        raise ValueError("workers must be an integer between 1 and 32")
    if max_new_trials is not None and (type(max_new_trials) is not int or max_new_trials < 1):
        raise ValueError("max_new_trials must be a positive integer or None")
    if type(max_consecutive_errors) is not int or max_consecutive_errors < 1:
        raise ValueError("max_consecutive_errors must be a positive integer")
    if split not in {"all", "development", "held_out"}:
        raise ValueError("split must be all, development, or held_out")
    resolved = resolve_experiment(config_path, env_file=env_file, environ=environ)
    if validate_resolved:
        validate_resolved(resolved)
    if set(case_splits) != {case.id for case in resolved.cases} or any(
        value not in {"development", "held_out"} for value in case_splits.values()
    ):
        raise ValueError("Every case must have exactly one development/held_out split")
    directory = Path(run_directory).expanduser().resolve()
    stop_path = Path(stop_file).expanduser().resolve() if stop_file is not None else directory / "STOP"
    if any(
        directory.is_relative_to(case.source) or case.source.is_relative_to(directory)
        for case in resolved.cases
    ):
        raise ValueError("Run directory must be separate from every Skill input")
    if any(stop_path.is_relative_to(case.source) for case in resolved.cases):
        raise ValueError("Stop file must be outside every Skill input")
    writer = ArtifactWriter(resolved.secrets)
    identity = writer.clean(experiment_identity(resolved, case_splits, provenance))
    with exclusive_run(directory):
        identity_path = directory / "experiment.json"
        if identity_path.exists():
            if _read(identity_path) != identity:
                raise ValueError("Frozen experiment identity changed; use a new run directory")
        else:
            if set(directory.iterdir()) - {directory / ".runner.lock", stop_path}:
                raise ValueError("Refusing to initialize a nonempty run directory")
            writer.json(identity_path, identity)
            writer.json(
                directory / "dataset.json",
                {"cases": [
                    {
                        **next(item for item in identity["cases"] if item["id"] == case.id),
                        "input": str(case.source),
                        "files": [
                            {"path": file.path, "kind": file.kind, "size": file.size}
                            for file in case.package.files
                        ],
                    }
                    for case in resolved.cases
                ]},
            )
        trials, combinations, replay = [], [], {}
        for case in resolved.cases:
            for variant in resolved.variants:
                for repetition in range(1, resolved.definition.repetitions + 1):
                    artifacts = f"trials/{case.id}/{variant.id}/{repetition}"
                    record_path = directory / artifacts / "record.json"
                    expected = {
                        "case": case.id, "variant": variant.id,
                        "repetition": repetition, "split": case_splits[case.id],
                        "artifacts": artifacts,
                    }
                    record = _read(record_path) if record_path.exists() else {
                        **expected, "status": "not_run", "semantic_review_status": REVIEW_PENDING
                    }
                    if any(record.get(key) != value for key, value in expected.items()):
                        raise ValueError(f"Invalid trial identity in {artifacts}/record.json")
                    # Never inherit an automatic semantic-pass flag from an old report.
                    record["semantic_review_status"] = REVIEW_PENDING
                    record, calls = _recover(record, directory)
                    trials.append(record)
                    combinations.append((case, variant))
                    replay[len(trials) - 1] = calls
                    writer.json(record_path, record)
        report = {
            "schema_version": 1, "mode": "online", "name": resolved.definition.name,
            "run_id": directory.name, "status": "running", "started_at": _now(),
            "selected_split": split, "workers": workers, "trials": trials,
            "semantic_review_status": REVIEW_PENDING,
            "structural_status_notice": "complete and structural_pass_rate do not establish semantic correctness",
            "scheduler": {
                "max_new_trials": max_new_trials, "max_consecutive_errors": max_consecutive_errors,
                "stop_file": str(stop_path), "submitted_this_invocation": 0,
                "consecutive_errors": 0, "stop_reasons": [],
            },
        }

        def progress():
            report["by_split"] = {
                name: aggregate([trial for trial in trials if trial["split"] == name])
                for name in ("development", "held_out")
            }
            write_progress(directory, report, writer)
            if on_progress:
                on_progress(writer.clean(report))

        pending = iter([
            index for index, trial in enumerate(trials)
            if trial["status"] == "not_run" and (split == "all" or trial["split"] == split)
        ])
        active = {}
        interrupted = False

        def stop(reason):
            reasons = report["scheduler"]["stop_reasons"]
            if not any(item["reason"] == reason for item in reasons):
                reasons.append({"reason": reason, "observed_at": _now()})
                progress()

        def should_stop():
            if stop_path.exists():
                stop("stop_file_present")
            return interrupted or bool(report["scheduler"]["stop_reasons"])

        progress()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            def submit():
                if should_stop():
                    return False
                if max_new_trials is not None and report["scheduler"]["submitted_this_invocation"] >= max_new_trials:
                    stop("max_new_trials_reached")
                    return False
                index = next(pending, None)
                if index is None:
                    return False
                record = deepcopy(trials[index])
                record.update(status="running", started_at=record.get("started_at", _now()), resumed_at=_now())
                trials[index] = record
                writer.json(directory / record["artifacts"] / "record.json", record)
                case, variant = combinations[index]
                future = executor.submit(
                    _execute_trial, case, variant, deepcopy(record), directory, writer, replay[index], client_factory
                )
                active[future] = index
                report["scheduler"]["submitted_this_invocation"] += 1
                return True

            for _ in range(workers):
                if not submit():
                    break
            progress()
            while active:
                try:
                    done, _ = wait(active, timeout=1, return_when=FIRST_COMPLETED)
                except KeyboardInterrupt:
                    # Let in-flight workers persist their result; do not schedule
                    # additional requests after an interruption of the main thread.
                    interrupted = True
                    stop("keyboard_interrupt")
                    continue
                should_stop()
                for future in done:
                    index = active.pop(future)
                    record = future.result()
                    trials[index] = record
                    writer.json(directory / record["artifacts"] / "record.json", record)
                    if record["status"] == "interrupted":
                        interrupted = True
                        stop("worker_interrupted")
                    # Invalid candidate/CFG results are degraded, not transport
                    # failures; never count them toward the infrastructure stop.
                    report["scheduler"]["consecutive_errors"] = (
                        report["scheduler"]["consecutive_errors"] + 1
                        if record["status"] == "error" else 0
                    )
                    if report["scheduler"]["consecutive_errors"] >= max_consecutive_errors:
                        stop("consecutive_infrastructure_errors")
                    progress()
                if not interrupted:
                    while len(active) < workers and submit():
                        pass
        report["finished_at"] = _now()
        report["status"] = (
            "interrupted" if interrupted else
            "needs_attention" if any(trial["status"] == "uncertain" for trial in trials) else
            "partial" if any(trial["status"] == "not_run" for trial in trials) else
            "complete" if all(trial["status"] == "complete" for trial in trials) else "failed"
        )
        progress()
        return ExperimentRunResult(directory, report["status"], writer.clean(report))
