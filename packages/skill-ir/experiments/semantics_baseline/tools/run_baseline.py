"""Run the jointly confirmed 30 × 3 baseline using only frozen Skill inputs.

This command never reads annotation bodies into a model prompt. It verifies the
external freeze, delegates loading and extraction to the existing production
APIs, and keeps every record outside the frozen package tree. --check is offline.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import sys

BASE = Path(__file__).resolve().parents[1]
PACKAGE = BASE.parents[1]
sys.path.insert(0, str(PACKAGE / "src"))

from skill_ir.experiments.config import resolve_experiment
from skill_ir.experiments.resumable import experiment_identity, run_resumable_experiment
from skill_ir.inputs.skill_package import load_skill_package
from freeze import corpus_root, verify_freeze


def baseline_definition(base: Path = BASE):
    root = corpus_root(base)
    corpus = json.loads((root / "corpus.json").read_text(encoding="utf-8"))
    samples = corpus["samples"]
    if len(samples) != 30 or Counter(item["split"] for item in samples) != {
        "development": 22, "held_out": 8
    }:
        raise ValueError("Baseline requires all 30 samples in the confirmed 22/8 split")
    dataset = json.loads((base / "dataset.json").read_text(encoding="utf-8"))
    expected = [
        {"id": item["id"], "input": f"frozen/corpus/{item['package_path']}"}
        for item in samples
    ]
    if dataset != {"cases": expected}:
        raise ValueError("dataset.json differs from the frozen input-only case inventory")
    for item in samples:
        source = (root / item["package_path"]).resolve()
        if not source.is_relative_to((root / "inputs").resolve()) or not source.is_dir():
            raise ValueError(f"Unsafe or missing frozen Skill input: {item['id']}")
        if (root / item["annotation_path"]).resolve().is_relative_to(source):
            raise ValueError(f"Annotation inside Skill input: {item['id']}")
    return {item["id"]: item["split"] for item in samples}


def runtime_provenance(base: Path = BASE) -> dict:
    """Bind resumptions to the same contract, loader, pipeline and runner code."""
    import pydantic

    package = base.parents[1]
    return {
        "contract": "constraints-v2",
        "prompt_variant": "baseline-contract-adaptation-only",
        "freeze_manifest_sha256": hashlib.sha256((base / "freeze_manifest.json").read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "pydantic": pydantic.__version__},
        "source_sha256": {
            path.relative_to(package).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((package / "src/skill_ir").rglob("*.py"))
        },
        "entrypoint_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def validate_baseline_resolved(resolved, base: Path = BASE):
    """Validate the inputs actually scheduled, including their normalized bytes."""
    root = corpus_root(base).resolve()
    if resolved.definition.dataset != "dataset.json" or resolved.dataset_path != (base / "dataset.json").resolve():
        raise ValueError("Baseline dataset redirection is forbidden")
    samples = json.loads((root / "corpus.json").read_text(encoding="utf-8"))["samples"]
    frozen_files = json.loads((base / "freeze_manifest.json").read_text(encoding="utf-8"))["files"]
    expected = [(item["id"], (root / item["package_path"]).resolve()) for item in samples]
    if [(case.id, case.source) for case in resolved.cases] != expected:
        raise ValueError("Resolved cases differ from the frozen Skill input inventory")
    for case in resolved.cases:
        prefix = "corpus/" + case.source.relative_to(root).as_posix() + "/"
        expected_files = {name[len(prefix):]: item["sha256"] for name, item in frozen_files.items() if name.startswith(prefix)}
        actual_files = {
            path.relative_to(case.source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in case.source.rglob("*") if path.is_file()
        }
        if actual_files != expected_files or any(path.is_symlink() for path in case.source.rglob("*")):
            raise ValueError(f"Frozen Skill source bytes changed: {case.id}")
        package = load_skill_package(case.source)
        canonical = json.dumps(package.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if case.package != package or case.sha256 != hashlib.sha256(canonical.encode("utf-8")).hexdigest():
            raise ValueError(f"Resolved extraction input hash differs from frozen package: {case.id}")


def restart_provenance(source: Path, destination: Path) -> dict:
    """Reference a failed run without rewriting or inheriting any of its trials."""
    source, destination = source.expanduser().resolve(), destination.expanduser().resolve()
    if source == destination or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("A restart requires a separate new run directory")
    report_path, identity_path = source / "report.json", source / "experiment.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    # Successful generation responses, even if their CFG failed, must not be
    # silently discarded through this zero-output restart path.
    successful_generations = 0
    for trial in report["trials"]:
        trace = (source / trial["artifacts"] / "trace.json").resolve()
        if not trace.is_relative_to(source):
            raise ValueError("Unsafe prior trial artifact path")
        if trace.is_file():
            successful_generations += sum(call.get("status") == "complete" for call in json.loads(trace.read_text(encoding="utf-8"))["calls"])
    if successful_generations or any(trial["status"] in {"complete", "degraded"} for trial in report["trials"]):
        raise ValueError("Restart provenance requires zero successful prior outputs")
    return {
        "run_directory": str(source), "run_id": source.name,
        "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
        "experiment_sha256": hashlib.sha256(identity_path.read_bytes()).hexdigest(),
        "prior_status_counts": dict(Counter(trial["status"] for trial in report["trials"])),
        "successful_generations": successful_generations, "inherited_trials": 0,
        "policy": "New authorized execution; prior uncertain requests and all old records remain unchanged.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=BASE / "runs/baseline-sol-max-v1")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-new-trials", type=int, help="Limit newly scheduled trials in this invocation, e.g. 1 for a full-input probe")
    parser.add_argument("--stop-file", type=Path, help="Drain in-flight trials when this file exists; default: RUN_DIR/STOP")
    parser.add_argument("--max-consecutive-errors", type=int, default=4, help="Stop scheduling after this many infrastructure errors; degraded CFGs do not count")
    parser.add_argument("--restart-of", type=Path, help="Read-only provenance link to an older run with zero successful outputs; use a new run directory")
    parser.add_argument("--split", choices=("all", "development", "holdout", "held_out"), default="all")
    parser.add_argument("--check", action="store_true", help="Verify the frozen corpus and safe effective settings without sending a request")
    args = parser.parse_args(argv)
    verify_freeze(BASE)
    splits = baseline_definition()
    config = BASE / "baseline.json"
    resolved = resolve_experiment(config, env_file=args.env_file)
    validate_baseline_resolved(resolved)
    if resolved.definition.repetitions != 3 or len(resolved.variants) != 1:
        raise ValueError("The baseline requires one variant with exactly three repetitions")
    provenance = runtime_provenance()
    if args.restart_of:
        provenance["restart_of"] = restart_provenance(args.restart_of, args.run_dir)
    identity = experiment_identity(resolved, splits, provenance)
    selected = "held_out" if args.split == "holdout" else args.split
    selected_count = sum(selected == "all" or value == selected for value in splits.values()) * 3
    if args.check:
        print(json.dumps({
            "mode": "offline_preflight", "planned": 90, "selected": selected_count,
            "split": selected, "split_counts": dict(Counter(splits.values())),
            "variants": identity["variants"], "contract": provenance["contract"],
            "semantic_review_status": "pending_joint_review",
            "freeze_manifest_sha256": provenance["freeze_manifest_sha256"],
        }, ensure_ascii=False, indent=2))
        return 0
    previous = None

    def progress(report):
        nonlocal previous
        counts = dict(Counter(trial["status"] for trial in report["trials"]))
        current = json.dumps([report["status"], counts, report["scheduler"]["stop_reasons"]], sort_keys=True)
        if current != previous:
            print(json.dumps({"status": report["status"], "trials": counts, "scheduler": report["scheduler"]}, ensure_ascii=False), flush=True)
            previous = current

    result = run_resumable_experiment(
        config, run_directory=args.run_dir, case_splits=splits, split=selected,
        workers=args.workers, provenance=provenance, env_file=args.env_file,
        on_progress=progress,
        max_new_trials=args.max_new_trials, stop_file=args.stop_file,
        max_consecutive_errors=args.max_consecutive_errors,
        validate_resolved=validate_baseline_resolved,
    )
    print(json.dumps({"run_directory": str(result.run_directory), "status": result.status}, ensure_ascii=False))
    return 0 if result.status in {"complete", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
