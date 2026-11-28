"""Prepare the sole new GA4 after this fix's offline acceptance; no model calls."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
import skillflow
from skillflow.common.inputs.snapshot import inspect_input, read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY, prepare
from tools.doe.document_guided_client import resolve_executable

VERIFY = Path(__file__).resolve().parent
OFFLINE = VERIFY.parent / "review-input-size-20261112"
PRIOR = VERIFY.parent / "online-ga4-input-necessity-corrected-r2-20261112"
OLD_RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"
AUTHORIZATION = ("User requested a general lossless source-review input-size fix, retaining complete source and every contract, "
                 "seven normal requests and two workers; after offline acceptance root alone may run exactly one fresh GA4 "
                 "with the complete verified source, existing budgets and its sole controller-owned zero-call replay.")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def create(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    current = implementation_provenance()
    accepted = read(OFFLINE / "offline-acceptance.json")
    old = read(OLD_RUN / "run-protocol.json")
    if accepted["status"] != "passed" or accepted["implementation_sha256"] != current["sha256"]:
        raise ValueError("Current implementation differs from this fix's offline acceptance")
    if read(OLD_RUN / "continuation-state.json")["status"] != "generation_closed":
        raise ValueError("The previous run is not closed")
    if not (OLD_RUN / "controller-finished.json").is_file():
        raise ValueError("Previous controller has no closure receipt")
    if IDENTITY != "skillflow-document-guided-run-v12" or POLICY["review_protocol"] != "shared-v2":
        raise ValueError("Current review identity differs from accepted generic display")
    if (POLICY["normal_semantic_calls"], POLICY["workers"], POLICY["structural_corrections"], POLICY["semantic_repairs"]) != (7, 2, 1, 1):
        raise ValueError("Authorized schedule or budgets changed")
    module = Path(skillflow.__file__).resolve()
    if module != (PROJECT / "src/skillflow/__init__.py").resolve():
        raise ValueError("Imported package is not the current workspace implementation")
    cli = resolve_executable()
    renderer = Path(old["renderer_executable"])
    if sha(renderer) != old["renderer_executable_sha256"]:
        raise ValueError("Verified renderer changed")
    if sha(cli) != old["cli_executable_sha256"]:
        raise ValueError("Installed CLI changed since verified local transport setup")
    tag = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    run = PROJECT / f"experiments/doe/runs/document-guided-ga4-review-shared-v2-high-{tag}"
    create(VERIFY / "preparation-intent.json", {"authorization": AUTHORIZATION,
        "run_directory": str(run), "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "maximum_new_runs": 1})
    source = Path(old["source_donor"])
    staged = VERIFY / "source-package"
    staged.mkdir(exist_ok=False)
    source_files = old["source_file_sha256"]
    for name, digest in source_files.items():
        original, target = source / name, staged / name
        if sha(original) != digest:
            raise ValueError("Original source changed: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    _, readable, _ = inspect_input(staged)
    if readable["source_sha256"] != old["source_sha256"] or len(readable["files"]) != 16:
        raise ValueError("The complete source package differs from the verified input")
    prepare(staged, run_dir=run, config={"reasoning_effort": "high"})
    frozen = read_snapshot(run / "source")[1]
    frozen_files = {p.relative_to(run / "source/inputs/package").as_posix(): sha(p)
                    for p in (run / "source/inputs/package").rglob("*") if p.is_file()}
    if frozen != readable or frozen_files != source_files:
        raise ValueError("Frozen source is not byte-identical to the verified complete input")
    manifest = read(run / "manifest.json")
    if manifest["config"] != {"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"} or manifest["policy"] != POLICY:
        raise ValueError("Prepared configuration differs from the authorization")
    inventory = dict(current["files"])
    for name in ("tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
                 "tools/doe/document_guided_pilot.py", "formal/.lake/build/bin/skill_ir_retell.exe"):
        inventory[name] = sha(PROJECT / name)
    for name in inventory:
        target = run / "implementation-snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / name, target)
    shutil.copyfile(VERIFY / "controller-template.py", run / "controller.py")
    shutil.copyfile(VERIFY / "local_timing.py", run / "local_timing.py")
    create(run / "implementation-snapshot/snapshot.json", {"files": inventory,
        "implementation_sha256": current["sha256"], "controller_sha256": sha(run / "controller.py"),
        "local_timing_sha256": sha(run / "local_timing.py")})
    protocol = {
        "authorization": AUTHORIZATION, "case_id": "ga4",
        "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
        "normal_semantic_requests": 7, "workers": 2, "semantic_repairs": 1,
        "structural_corrections_per_stage": 1, "native_timeout_seconds": 2700,
        "native_extra_transient_attempts": 2, "semantic_source_view": "complete_frozen_source",
        "interface_revision": "generic_lossless_source_review_shared_v2",
        "guided_run_identity": IDENTITY, "review_protocol": "shared-v2",
        "implementation_sha256": current["sha256"], "source_sha256": frozen["source_sha256"],
        "source_file_sha256": source_files, "readable_files": 16,
        "source_utf8_bytes": old["source_utf8_bytes"], "source_donor": str(source), "source_staging": str(staged),
        "source_byte_identical": True, "historical_answers_imported": False,
        "cli_executable": str(cli), "cli_executable_sha256": sha(cli),
        "renderer_executable": str(renderer), "renderer_executable_sha256": sha(renderer),
        "python_executable": sys.executable, "python_executable_sha256": sha(Path(sys.executable)),
        "imported_skillflow_module": str(module),
        "model_probe_calls": 0, "model_monitor_calls": 0, "skill_execution": False,
        "offline_acceptance": str(OFFLINE / "offline-acceptance.json"),
        "queue_policy": "Root owns one new GA4 controller and its sole zero-call replay. No additional cases or resampling.",
        "freeze_policy": "Freeze accepted implementation, prompts, transport, controller, timing helper and executables through analysis and replay.",
        "previous_run_reference_only": str(OLD_RUN)}
    create(run / "run-protocol.json", protocol)
    item = {"case_id": "ga4", "run_directory": str(run), "source_root": str(source),
        "source_staging": str(staged), "source_sha256": frozen["source_sha256"], "files": 16}
    state = {"status": "prepared_not_started", "authorization": AUTHORIZATION, **item,
        "implementation_sha256": current["sha256"], "maximum_new_runs": 1,
        "instructions": "Root alone dispatches this fresh controller once. No historical resume/replay, Skill execution, probes, duplicate controllers or frozen code changes."}
    create(run / "continuation-state.json", state)
    create(VERIFY / "continuation-state.json", state)
    create(VERIFY / "prepared-run.json", {**item, "implementation_sha256": current["sha256"],
        "model": "gpt-6.1-sol", "effort": "high", "provider": "openai", "workers": 2,
        "normal_semantic_calls": 7, "native_timeout_seconds": 2700, "sole_owner": "/root"})
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
