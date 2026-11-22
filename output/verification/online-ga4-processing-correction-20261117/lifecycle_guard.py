"""Read-only, stdlib preflight for the sole root-owned fresh GA4 lifecycle.

An explicit owner is an accidental-dispatch guard, not operating-system access
control. This module never prepares, launches, resumes or replays anything.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

RUN_PREFIX = "document-guided-ga4-processing-correction-high-"
OFFLINE_NAME = "processing-correction-20261117"
VERIFY_NAME = "online-ga4-processing-correction-20261117"
TOOLS = {"tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
         "tools/doe/document_guided_pilot.py", "tools/doe/document_guided_observation.py"}
HELPERS = {"prepare_run.py", "controller-template.py", "dispatch_once.ps1",
           "local_timing.py", "lifecycle_guard.py"}
CONFIG = {"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"}
IDENTITIES = {"guided_run_identity": "skillflow-document-guided-run-v15",
              "step_identity": "skillflow-document-step-v12",
              "fragments_identity": "skillflow-document-fragments-v7",
              "processing_wire_identity": "skillflow-processing-json-v1"}
BUDGETS = {"normal_semantic_requests": 7, "workers": 2, "semantic_repairs": 1,
           "structural_corrections_per_stage": 1, "native_timeout_seconds": 2700,
           "native_extra_transient_attempts": 2}
POLICY_FIELDS = {"processing_presentation": "exact-shared-values-v1",
    "repair_request_failure": "retain_original_bound_bundle_v1",
    "processing_wire_guidance": "complete-grammar-v1",
    "processing_format_diagnostics": "bounded-raw-pairs-v1",
    "cfg_correction_scope": "causal-dependency-records-v1"}
RENDERER = "formal/.lake/build/bin/skill_ir_retell.exe"
PINNED_CLI = Path("C:/Users/admin/AppData/Local/OpenAI/Codex/bin/9e1da79431da526b/codex.exe")
PINNED_CLI_SHA256 = "83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f"
SOURCE_SHA256 = "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"


def read(path):
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object: " + str(path))
    return value


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_owner(owner):
    if owner != "/root":
        raise ValueError("Only the explicitly named /root owner may prepare or dispatch this fresh run")


def authorized_run(project, run):
    run = Path(run).resolve()
    if (run.parent != (Path(project) / "experiments/doe/runs").resolve()
            or re.fullmatch(re.escape(RUN_PREFIX) + r"[0-9]{8}-[0-9]{6}", run.name) is None):
        raise ValueError("Run is outside the exact fresh processing-correction namespace")
    return run


def native_inventory(run):
    """Bind both start and PID evidence, including orphan PID receipts."""
    return {p.relative_to(run).as_posix(): sha(p)
            for name in ("started.json", "pid.json")
            for p in sorted((Path(run) / "transport").rglob(name))}


def require_fresh(run):
    if read(run / "result.json").get("status") != "prepared":
        raise ValueError("Only a fresh prepared result can start")
    markers = ("controller-started.json", "controller-finished.json", "analysis-finished.json",
               "replay-started.json", "replay-check.json", "native-exit-check.json")
    if (any((run / name).exists() for name in markers) or native_inventory(run)
            or any(run.rglob("call.json"))):
        raise ValueError("Fresh namespace already contains an execution, semantic call or replay receipt")


def validate_acceptance(project, verify, current=None):
    project, verify = Path(project).resolve(), Path(verify).resolve()
    path = verify.parent / OFFLINE_NAME / "offline-acceptance.json"
    accepted = read(path)
    helper_names = {(verify / name).relative_to(project).as_posix() for name in HELPERS}
    if (set(accepted.get("tool_file_sha256", {})) != TOOLS
            or set(accepted.get("lifecycle_file_sha256", {})) != helper_names):
        raise ValueError("Offline acceptance must bind every transport and lifecycle helper, including public observation")
    if accepted.get("status") != "passed":
        raise ValueError("Offline acceptance is not passed")
    if current is not None and accepted.get("implementation_sha256") != current["sha256"]:
        raise ValueError("Current implementation differs from offline acceptance")
    for name, digest in {**accepted["tool_file_sha256"], **accepted["lifecycle_file_sha256"]}.items():
        if sha(project / name) != digest:
            raise ValueError("Accepted transport or lifecycle helper changed: " + name)
    return accepted


def _bound(path, digest, label):
    if not isinstance(digest, str) or sha(path) != digest:
        raise ValueError("Immutable preparation binding changed: " + label)


def validate_prepared(project, verify, *, fresh=True, current=None):
    project, verify = Path(project).resolve(), Path(verify).resolve()
    if verify != project / "output/verification" / VERIFY_NAME:
        raise ValueError("Verification directory is outside the new authorized namespace")
    prepared = read(verify / "prepared-run.json")
    require_owner(prepared.get("sole_owner"))
    run = authorized_run(project, prepared["run_directory"])
    intent_path = verify / "preparation-intent.json"
    intent = read(intent_path)
    if (intent.get("owner") != "/root" or intent.get("maximum_new_runs") != 1
            or Path(intent["run_directory"]).resolve() != run):
        raise ValueError("Sole preparation intent does not bind this run")
    _bound(intent_path, prepared.get("preparation_intent_sha256"), "preparation intent")
    for filename, key in (("run-protocol.json", "run_protocol_sha256"),
                          ("manifest.json", "run_manifest_sha256"),
                          ("implementation-snapshot/snapshot.json", "snapshot_sha256")):
        _bound(run / filename, prepared.get(key), filename)
    protocol = read(run / "run-protocol.json")
    if any(protocol.get(k) != v for k, v in {**IDENTITIES, **BUDGETS, **POLICY_FIELDS}.items()):
        raise ValueError("Authorized identities or budgets or correction policy changed")
    if protocol.get("runtime") != {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"}:
        raise ValueError("Authorized model, effort or provider changed")
    if Path(protocol["verification_directory"]).resolve() != verify:
        raise ValueError("Protocol verification owner changed")
    acceptance_path = verify.parent / OFFLINE_NAME / "offline-acceptance.json"
    if Path(protocol["offline_acceptance"]).resolve() != acceptance_path:
        raise ValueError("Offline acceptance owner changed")
    for owner in (prepared, protocol):
        _bound(acceptance_path, owner.get("offline_acceptance_sha256"), "offline acceptance")
    accepted = validate_acceptance(project, verify, current)
    if len({accepted["implementation_sha256"], protocol["implementation_sha256"], prepared["implementation_sha256"]}) != 1:
        raise ValueError("Implementation acceptance identity changed")
    manifest = read(run / "manifest.json")
    policy = manifest.get("policy", {})
    if (manifest.get("config") != CONFIG
            or any(policy.get(k) != v for k, v in POLICY_FIELDS.items())
            or tuple(policy.get(k) for k in ("normal_semantic_calls", "workers", "structural_corrections", "semantic_repairs")) != (7, 2, 1, 1)):
        raise ValueError("Prepared runtime configuration or budgets changed")
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    files = snapshot["files"]
    required = TOOLS | {RENDERER}
    if current is not None:
        required |= set(current["files"])
        if set(files) != required:
            raise ValueError("Frozen implementation inventory is not exact")
    elif not required <= set(files):
        raise ValueError("Frozen transport/renderer inventory is incomplete")
    if snapshot["implementation_sha256"] != accepted["implementation_sha256"]:
        raise ValueError("Snapshot implementation differs from acceptance")
    for name, digest in files.items():
        path = project / name
        if not path.resolve().is_relative_to(project):
            raise ValueError("Snapshot path escapes project")
        _bound(path, digest, name)
        _bound(run / "implementation-snapshot" / name, digest, "snapshot/" + name)
    for source_name, target_name, key in (("controller-template.py", "controller.py", "controller_sha256"),
            ("local_timing.py", "local_timing.py", "local_timing_sha256"),
            ("lifecycle_guard.py", "lifecycle_guard.py", "lifecycle_guard_sha256")):
        digest = accepted["lifecycle_file_sha256"][(verify / source_name).relative_to(project).as_posix()]
        if snapshot.get(key) != digest:
            raise ValueError("Snapshot helper differs from acceptance: " + target_name)
        _bound(run / target_name, digest, target_name)
    if (Path(protocol["cli_executable"]).resolve() != PINNED_CLI.resolve()
            or protocol["cli_executable_sha256"] != PINNED_CLI_SHA256):
        raise ValueError("Previously pinned CLI was substituted")
    for field in ("cli_executable", "renderer_executable", "python_executable"):
        _bound(Path(protocol[field]), protocol[field + "_sha256"], field)
    if protocol.get("source_sha256") != SOURCE_SHA256 or protocol.get("readable_files") != 16:
        raise ValueError("Authorized complete GA4 source identity changed")
    if (Path(protocol["source_staging"]).resolve() != verify / "source-package"
            or Path(prepared["source_staging"]).resolve() != verify / "source-package"
            or prepared.get("source_sha256") != SOURCE_SHA256):
        raise ValueError("Prepared source owner or identity changed")
    expected = protocol["source_file_sha256"]
    if len(expected) != 16:
        raise ValueError("Source inventory must contain all sixteen files")
    for source in (run / "source/inputs/package", Path(protocol["source_staging"])):
        actual = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob("*") if p.is_file()}
        if actual != expected:
            raise ValueError("Complete frozen/staged source file inventory changed")
    if fresh:
        require_fresh(run)
    return run, protocol


def validate_dispatch(project, verify, *, current=None):
    """Read-only before claiming the one dispatch; stale claims never permit retry."""
    if any((Path(verify) / name).exists() for name in ("dispatch-intent.json", "dispatch-started.json")):
        raise ValueError("This preparation already has a dispatch claim; no second launch is allowed")
    return validate_prepared(project, verify, current=current)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--verify", type=Path, required=True)
    args = parser.parse_args(argv)
    require_owner(args.owner)
    project = args.verify.resolve().parents[2]
    run, _ = validate_dispatch(project, args.verify)
    print(json.dumps({"status": "preflight_passed", "run_directory": str(run), "model_calls": 0}))


if __name__ == "__main__":
    main()
