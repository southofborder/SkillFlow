"""Run a separate DeepSeek V4 Flash baseline over the same frozen 30 x 3 inputs.

The provider/model switch is explicit experimental provenance, never an implicit
resume of a Sol trial. Production Prompt, IR, compiler and extraction stay intact.
Use --check without an API key for a no-network preflight. Execute this entrypoint
in a dedicated process; the already audited SSE transport is reused unchanged.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from tools.graph.baseline.run_baseline import (
    BASE, baseline_definition, experiment_identity, resolve_experiment,
    run_resumable_experiment, runtime_provenance, validate_baseline_resolved,
    verify_freeze,
)
from skillflow.common.llm import stream_transport


CONFIG = BASE / "deepseek-v4-flash.json"
CHANGE_MANIFEST = BASE / "deepseek_provider_change.json"
PROVIDER_ID = "deepseek-official-v4-flash-max-v1"
EXPECTED_VARIANT = {
    "id": "deepseek-v4-flash-max", "api_key_env": "LLM_API_KEY",
    "max_repair_rounds": 3, "endpoint": "https://api.deepseek.com/chat/completions",
    "model": "deepseek-v4-flash", "reasoning_effort": "max",
    "timeout_ms": 180000, "max_retries": 2,
    "retry_base_ms": 500, "retry_max_backoff_ms": 8000,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_deepseek_baseline(resolved):
    validate_baseline_resolved(resolved)
    if resolved.config_path != CONFIG.resolve():
        raise ValueError("DeepSeek config redirection is forbidden")
    if resolved.definition.repetitions != 3 or len(resolved.variants) != 1:
        raise ValueError("DeepSeek baseline requires one variant and exactly three repetitions")
    if resolved.variants[0].snapshot() != EXPECTED_VARIANT:
        raise ValueError("DeepSeek baseline requires the pinned official provider settings")


def provider_provenance(resolved, splits):
    """Verify the unchanged input/Prompt/runtime boundary against the prior run."""
    change = json.loads(CHANGE_MANIFEST.read_text(encoding="utf-8"))
    if change["provider_change_id"] != PROVIDER_ID or change["target_variant"] != EXPECTED_VARIANT:
        raise ValueError("Provider change manifest differs from the declared variant")
    for entry in change["provider_checks"]:
        check_path = (BASE / entry["path"]).resolve()
        if not check_path.is_relative_to((BASE / "provider_checks").resolve()) or _sha(check_path) != entry["sha256"]:
            raise ValueError("Provider availability preflight provenance changed")
    current = runtime_provenance()
    current_identity = experiment_identity(resolved, splits)
    prior = []
    for entry in change["prior_runs"]:
        directory = (BASE / entry["directory"]).resolve()
        if not directory.is_relative_to((BASE / "runs").resolve()):
            raise ValueError("Provider change references an unsafe prior run path")
        for filename in ("experiment.json", "report.json"):
            if _sha(directory / filename) != entry[filename.replace(".json", "_sha256")]:
                raise ValueError(f"Prior run provenance changed: {directory.name}/{filename}")
        prior.append(json.loads((directory / "experiment.json").read_text(encoding="utf-8")))
    reference = prior[change["semantic_reference_index"]]
    if current_identity["cases"] != reference["cases"]:
        raise ValueError("Provider switch changed the frozen case or exact Prompt identity")
    for key in ("contract", "prompt_variant", "freeze_manifest_sha256", "source_sha256"):
        if current[key] != reference["provenance"][key]:
            raise ValueError(f"Provider switch changed locked semantic/runtime sources: {key}")
    current["provider_change"] = {
        **change,
        "manifest_sha256": _sha(CHANGE_MANIFEST),
        "config_sha256": _sha(CONFIG),
        "entrypoint_sha256": _sha(Path(__file__)),
        "case_and_prompt_identity_equal": True,
        "production_source_identity_equal": True,
        "inherited_trials": 0,
    }
    current["transport"] = {
        **deepcopy(stream_transport.TRANSPORT_POLICY),
        "source_sha256": {"stream_transport.py": _sha(Path(stream_transport.__file__))},
    }
    return current


def require_deepseek_directory(path: Path):
    directory = path.expanduser().resolve()
    # No run output may ever be written into frozen inputs or earlier runs.
    if directory.is_relative_to((BASE / "frozen").resolve()):
        raise ValueError("Run artifacts must stay outside the frozen corpus")
    change = json.loads(CHANGE_MANIFEST.read_text(encoding="utf-8"))
    for entry in change["prior_runs"]:
        prior = (BASE / entry["directory"]).resolve()
        if directory == prior or directory.is_relative_to(prior) or prior.is_relative_to(directory):
            raise ValueError("DeepSeek requires a separate new run directory; prior runs stay immutable")
    identity = directory / "experiment.json"
    if identity.is_file():
        previous = json.loads(identity.read_text(encoding="utf-8"))
        if previous.get("provenance", {}).get("provider_change", {}).get("provider_change_id") != PROVIDER_ID:
            raise ValueError("DeepSeek requires a separate new run directory; model results cannot be mixed")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-new-trials", type=int)
    parser.add_argument("--max-consecutive-errors", type=int, default=1)
    parser.add_argument("--stop-file", type=Path)
    parser.add_argument("--split", choices=("all", "development", "holdout", "held_out"), default="development")
    parser.add_argument("--check", action="store_true", help="No network and no credential discovery; verify all frozen inputs and identities")
    args = parser.parse_args(argv)
    require_deepseek_directory(args.run_dir)
    verify_freeze(BASE)
    splits = baseline_definition()
    # Offline verification neither needs nor reads real credentials. Every
    # effective non-secret setting is explicitly pinned in CONFIG.
    resolved = resolve_experiment(CONFIG, environ={"LLM_API_KEY": "offline-deepseek-preflight"}) if args.check else resolve_experiment(CONFIG, env_file=args.env_file)
    validate_deepseek_baseline(resolved)
    provenance = provider_provenance(resolved, splits)
    identity = experiment_identity(resolved, splits, provenance)
    selected = "held_out" if args.split == "holdout" else args.split
    if args.check:
        print(json.dumps({
            "mode": "offline_deepseek_preflight", "planned": 90,
            "selected": sum(selected == "all" or value == selected for value in splits.values()) * 3,
            "variants": identity["variants"], "provider_change": provenance["provider_change"],
            "transport": provenance["transport"], "semantic_review_status": "pending_joint_review",
        }, ensure_ascii=False, indent=2))
        return 0
    previous = None

    def progress(report):
        nonlocal previous
        current = json.dumps({
            "status": report["status"], "trials": dict(Counter(item["status"] for item in report["trials"])),
            "scheduler": report["scheduler"], "provider_change_id": PROVIDER_ID,
        }, ensure_ascii=False, sort_keys=True)
        if current != previous:
            print(current, flush=True)
            previous = current

    result = run_resumable_experiment(
        CONFIG, run_directory=args.run_dir, case_splits=splits, split=selected,
        workers=args.workers, provenance=provenance, env_file=args.env_file,
        max_new_trials=args.max_new_trials, max_consecutive_errors=args.max_consecutive_errors,
        stop_file=args.stop_file, validate_resolved=validate_deepseek_baseline,
        on_progress=progress,
        client_factory=stream_transport.StreamingReplayClient,
    )
    print(json.dumps({"run_directory": str(result.run_directory), "status": result.status}, ensure_ascii=False))
    return 0 if result.status in {"complete", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
