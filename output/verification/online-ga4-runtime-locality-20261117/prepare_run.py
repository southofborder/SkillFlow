"""Prepare the sole new GA4 after this fix's offline acceptance; no model calls."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
import skillflow
from skillflow.common.inputs.snapshot import inspect_input, read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY, prepare_from_accepted_cfg
from skillflow.document_guided.online import STEP_IDENTITY
from skillflow.document_guided.fragments import VERSION as FRAGMENTS_IDENTITY
from skillflow.document_guided.fragment_wire import PROCESSING_WIRE_IDENTITY
from skillflow.document_guided.source_review import FRAGMENT_IDENTITY as SOURCE_REVIEW_FRAGMENT_IDENTITY
from lifecycle_guard import (HELPERS, IDENTITIES, POLICY_FIELDS, PINNED_CLI, PINNED_CLI_SHA256, SOURCE_SHA256,
    authorized_run, require_owner, validate_acceptance, validate_prepared,
    PARENT_NAME, INHERITED_STAGES, parent_binding, validate_inheritance)

VERIFY = Path(__file__).resolve().parent
OFFLINE = VERIFY.parent / "runtime-locality-20261117"
OLD_RUN = PROJECT / "experiments/doe/runs" / PARENT_NAME
PINNED_TOOLS = {"tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
                "tools/doe/document_guided_pilot.py", "tools/doe/document_guided_observation.py"}
LIFECYCLE_NAMES = HELPERS
AUTHORIZATION = ("User authorized the general runtime dependency-locality and verified-infeasibility fixes on 2026-11-17, "
                 "then one fresh GA4 with the exact accepted source, Task, flow and 489-IR initial CFG from the closed processing-restart run. "
                 "Use the new offline-accepted implementation; seven-stage policy with three inherited initial stages, "
                 "two workers and existing correction/shared-repair/transport budgets. Root alone may prepare and dispatch "
                 "this fresh descendant and its sole terminal zero-call replay; never resume or replay the parent.")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def create(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--suffix", required=True, help="Root-selected YYYYMMDD-HHMMSS; no automatic reservation")
    args = parser.parse_args(argv)
    require_owner(args.owner)
    run = authorized_run(PROJECT, PROJECT / ("experiments/doe/runs/document-guided-ga4-runtime-locality-high-" + args.suffix))
    if run.exists() or any((VERIFY / name).exists() for name in (
            "preparation-intent.json", "prepared-run.json", "source-package",
            "dispatch-intent.json", "dispatch-started.json", "continuation-state.json")):
        raise ValueError("Fresh preparation namespace is already claimed; no overwrite or resume is allowed")
    current = implementation_provenance()
    accepted = validate_acceptance(PROJECT, VERIFY, current)
    inherited = accepted["restart_parent"]
    if inherited != parent_binding(PROJECT) or Path(inherited["run_directory"]).resolve() != OLD_RUN.resolve():
        raise ValueError("Restart parent differs from the fixed accepted upstream")
    old = read(OLD_RUN / "run-protocol.json")
    expected_helpers = {(VERIFY / name).relative_to(PROJECT).as_posix() for name in LIFECYCLE_NAMES}
    if (set(accepted["tool_file_sha256"]) != PINNED_TOOLS
            or set(accepted["lifecycle_file_sha256"]) != expected_helpers):
        raise ValueError("Offline acceptance must bind every current transport and lifecycle helper")
    for name, digest in {**accepted["tool_file_sha256"], **accepted["lifecycle_file_sha256"]}.items():
        if sha(PROJECT / name) != digest:
            raise ValueError("Transport or lifecycle helper differs from this fix acceptance: " + name)
    if accepted["status"] != "passed" or accepted["implementation_sha256"] != current["sha256"]:
        raise ValueError("Current implementation differs from this fix's offline acceptance")
    if read(OLD_RUN / "continuation-state.json")["status"] != "generation_closed":
        raise ValueError("The previous run is not closed")
    if not (OLD_RUN / "controller-finished.json").is_file():
        raise ValueError("Previous controller has no closure receipt")
    if ({"guided_run_identity": IDENTITY, "step_identity": STEP_IDENTITY,
            "fragments_identity": FRAGMENTS_IDENTITY, "processing_wire_identity": PROCESSING_WIRE_IDENTITY,
            "source_review_fragment_identity": SOURCE_REVIEW_FRAGMENT_IDENTITY} != IDENTITIES
            or POLICY["review_protocol"] != "shared-v2"
            or POLICY.get("review_validation") != "strict-record-isolation-v1"
            or POLICY.get("processing_presentation") != "exact-shared-values-v1"
            or POLICY.get("repair_request_failure") != "retain_original_bound_bundle_v1"):
        raise ValueError("Current processing or review identity differs from the accepted implementation")
    if any(POLICY.get(key) != value for key, value in POLICY_FIELDS.items()):
        raise ValueError("Current processing correction guidance or diagnostics differ from acceptance")
    if (POLICY["normal_semantic_calls"], POLICY["workers"], POLICY["structural_corrections"], POLICY["semantic_repairs"]) != (7, 2, 1, 1):
        raise ValueError("Authorized schedule or budgets changed")
    module = Path(skillflow.__file__).resolve()
    if module != (PROJECT / "src/skillflow/__init__.py").resolve():
        raise ValueError("Imported package is not the current workspace implementation")
    # Keep the previously verified executable despite the desktop update.
    cli = Path(old["cli_executable"])
    renderer = Path(old["renderer_executable"])
    if cli.resolve() != PINNED_CLI.resolve() or old["cli_executable_sha256"] != PINNED_CLI_SHA256:
        raise ValueError("Previously verified CLI pin differs; explicit root resolution is required")
    if sha(renderer) != old["renderer_executable_sha256"]:
        raise ValueError("Verified renderer changed")
    if not cli.is_file() or sha(cli) != old["cli_executable_sha256"]:
        raise ValueError("Previously verified pinned CLI is unavailable or changed")
    # Verify every source byte before the sole preparation claim or mutation.
    source = OLD_RUN / "source/inputs/package"
    source_files = old["source_file_sha256"]
    if len(source_files) != 16 or old["source_sha256"] != SOURCE_SHA256:
        raise ValueError("Previous verified complete source identity or inventory changed")
    for name, digest in source_files.items():
        if not (source / name).resolve().is_relative_to(source.resolve()) or sha(source / name) != digest:
            raise ValueError("Original source changed or escapes its package: " + name)
    create(VERIFY / "preparation-intent.json", {"authorization": AUTHORIZATION,
        "run_directory": str(run), "created_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "maximum_new_runs": 1, "owner": args.owner})
    staged = VERIFY / "source-package"
    staged.mkdir(exist_ok=False)
    for name, digest in source_files.items():
        original, target = source / name, staged / name
        if sha(original) != digest:
            raise ValueError("Original source changed: " + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
    _, readable, _ = inspect_input(staged)
    if readable["source_sha256"] != old["source_sha256"] or len(readable["files"]) != 16:
        raise ValueError("The complete source package differs from the verified input")
    prepare_from_accepted_cfg(OLD_RUN, run_dir=run,
        config={"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"})
    create(run / "inherited-inputs.json", inherited)
    validate_inheritance(PROJECT, run, inherited)
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
                 "tools/doe/document_guided_pilot.py", "tools/doe/document_guided_observation.py",
                 "formal/.lake/build/bin/skill_ir_retell.exe"):
        inventory[name] = sha(PROJECT / name)
    for name in inventory:
        target = run / "implementation-snapshot" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT / name, target)
    shutil.copyfile(VERIFY / "controller-template.py", run / "controller.py")
    shutil.copyfile(VERIFY / "local_timing.py", run / "local_timing.py")
    shutil.copyfile(VERIFY / "lifecycle_guard.py", run / "lifecycle_guard.py")
    create(run / "implementation-snapshot/snapshot.json", {"files": inventory,
        "implementation_sha256": current["sha256"], "controller_sha256": sha(run / "controller.py"),
        "local_timing_sha256": sha(run / "local_timing.py"),
        "lifecycle_guard_sha256": sha(run / "lifecycle_guard.py")})
    protocol = {
        "authorization": AUTHORIZATION, "case_id": "ga4",
        "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
        "normal_semantic_requests": 7, "workers": 2, "semantic_repairs": 1,
        "structural_corrections_per_stage": 1, "native_timeout_seconds": 2700,
        "native_extra_transient_attempts": 2, "semantic_source_view": "complete_frozen_source",
        "interface_revision": "runtime_locality_accepted_upstream_v1",
        "inherited_initial_stages": list(INHERITED_STAGES),
        "fresh_normal_stages": ["processing", "task-correspondence", "sensitivity", "review"],
        "inherited_inputs_sha256": sha(run / "inherited-inputs.json"),
        "accepted_upstream_sha256": sha(run / "accepted-upstream.json"),
        "inherited_initial_request_count": 3,
        "cost_scope": "Only native processes recorded under this new run's transport directory count as new cost; inherited upstream calls retain parent origin and timestamps.",
        "processing_presentation": POLICY["processing_presentation"],
        "repair_request_failure": POLICY["repair_request_failure"],
        "public_observation": "host_poll_intervals_only",
        **IDENTITIES, **POLICY_FIELDS, "review_protocol": "shared-v2",
        "review_validation": "strict-record-isolation-v1",
        "implementation_sha256": current["sha256"], "source_sha256": frozen["source_sha256"],
        "source_file_sha256": source_files, "readable_files": 16,
        "source_utf8_bytes": old["source_utf8_bytes"], "source_donor": str(source), "source_staging": str(staged),
        "source_byte_identical": True, "historical_answers_imported": True,
        "cli_executable": str(cli), "cli_executable_sha256": sha(cli),
        "renderer_executable": str(renderer), "renderer_executable_sha256": sha(renderer),
        "python_executable": sys.executable, "python_executable_sha256": sha(Path(sys.executable)),
        "imported_skillflow_module": str(module),
        "model_probe_calls": 0, "model_monitor_calls": 0, "skill_execution": False,
        "offline_acceptance": str(OFFLINE / "offline-acceptance.json"),
        "offline_acceptance_sha256": sha(OFFLINE / "offline-acceptance.json"),
        "verification_directory": str(VERIFY),
        "queue_policy": "Root owns one new GA4 controller and its sole zero-call replay. No additional cases or resampling.",
        "freeze_policy": "Freeze accepted implementation, prompts, transport, controller, timing and lifecycle helpers, acceptance and executables through analysis and replay.",
        "accepted_upstream_parent": str(OLD_RUN)}
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
        "normal_semantic_calls": 7, "native_timeout_seconds": 2700, "sole_owner": args.owner,
        "offline_acceptance_sha256": sha(OFFLINE / "offline-acceptance.json"),
        "preparation_intent_sha256": sha(VERIFY / "preparation-intent.json"),
        "run_protocol_sha256": sha(run / "run-protocol.json"),
        "run_manifest_sha256": sha(run / "manifest.json"),
        "inherited_inputs_sha256": sha(run / "inherited-inputs.json"),
        "accepted_upstream_sha256": sha(run / "accepted-upstream.json"),
        "snapshot_sha256": sha(run / "implementation-snapshot/snapshot.json")})
    validate_prepared(PROJECT, VERIFY, current=current)
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
