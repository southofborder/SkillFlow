"""Local preparation and integrity checks for the single approved GA4 descendant."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

VERIFY_NAME = "online-ga4-entry-review-20261122"
RUN_PREFIX = "document-guided-ga4-entry-review-high-"
PARENT = "document-guided-ga4-lossless-delivery-high-20261122-211742"
PARENT_REPORT = "online-ga4-lossless-delivery-20261119"
ACCEPTANCE = "output/verification/entry-review-20261122/offline-acceptance.json"
PORTABLE_CERTIFICATE = "output/verification/portable-renderer-20261123/accepted-certificate.json"

SOURCE = "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"
CONFIG = {"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"}
TOOLS = {f"tools/doe/document_guided_{name}.py" for name in ("client", "metrics", "pilot", "observation")}
EXECUTABLES = ("cli_executable", "renderer_executable", "python_executable")
AUTHORIZATION = "User authorized one new GA4 processing-onward after offline verification and GitHub synchronization of the generic revision, entry sensitivity, guard and DOE publication fixes on 2026-11-22. Retain original selected CFG, Task, flow and complete source, with one controller-owned zero-call replay."


def require_owner(owner):
    if owner != "/root":
        raise ValueError("Only the root owner may dispatch")


def authorized_run(project, run):
    run = Path(run).resolve()
    if run.parent != project / "experiments/doe/runs" or not re.fullmatch(RUN_PREFIX + r"\d{8}-\d{6}", run.name):
        raise ValueError("Unexpected run namespace")
    return run


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def create(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def sha(path):
    from skillflow.common.artifact_io import file_sha256
    return file_sha256(path)


def check_files(root, hashes):
    for name, digest in hashes.items():
        file = (root / name).resolve()
        if not file.is_relative_to(root.resolve()) or sha(file) != digest:
            raise ValueError("File pin mismatch: " + str(file))


def native_inventory(run):
    return {p.relative_to(run).as_posix(): sha(p)
            for name in ("started.json", "pid.json")
            for p in sorted((run / "transport").rglob(name))}


def validate_prepared(project, verify, *, current, fresh=True):
    if verify.resolve() != project / "output/verification" / VERIFY_NAME:
        raise ValueError("Unexpected verification owner")
    prepared = read(verify / "prepared-run.json")
    run = authorized_run(project, prepared["run_directory"])
    check_files(run, prepared["run_pins"])
    check_files(verify, prepared["verification_pins"])
    protocol = read(run / "run-protocol.json")
    if (current["sha256"] != protocol["implementation_sha256"] or current["sha256"] != read(project / ACCEPTANCE)["implementation_sha256"]
            or sha(project / ACCEPTANCE) != prepared["offline_acceptance_sha256"]
            or protocol["offline_acceptance_sha256"] != prepared["offline_acceptance_sha256"]):
        raise ValueError("Offline acceptance binding changed")
    if sha(project / PORTABLE_CERTIFICATE) != protocol["portable_certificate_sha256"]:
        raise ValueError("Offline local renderer proof changed")
    if sha(Path(protocol["renderer_build_receipt"])) != protocol["renderer_build_receipt_sha256"]:
        raise ValueError("Local renderer build receipt changed")
    for field in EXECUTABLES:
        if sha(Path(protocol[field])) != protocol[field + "_sha256"]:
            raise ValueError("Executable pin mismatch: " + field)
    upstream = read(run / "accepted-upstream.json")
    check_files(run, upstream["copied_files"])
    check_files(Path(upstream["parent_directory"]), upstream["files"])
    check_files(project, protocol["historical_terminal_pins"])
    package = run / "source/inputs/package"
    check_files(package, protocol["source_file_sha256"])
    if set(protocol["source_file_sha256"]) != {p.relative_to(package).as_posix() for p in package.rglob("*") if p.is_file()}:
        raise ValueError("Frozen source inventory changed")
    if fresh:
        expected = {name for name in upstream["copied_files"] if name.endswith("/call.json")}
        actual = {p.relative_to(run).as_posix() for p in run.rglob("call.json")}
        if (read(run / "result.json")["status"] != "prepared" or native_inventory(run) or expected != actual
                or any((run / name).exists() for name in ("controller-started.json", "controller-finished.json", "replay-started.json", "analysis-finished.json"))):
            raise ValueError("Analysis or replay evidence already exists")
    return run, protocol


def prepare(project, verify, current):
    from skillflow.common.inputs.snapshot import read_snapshot
    from skillflow.document_guided.accepted_upstream import describe_accepted_upstream
    from skillflow.document_guided.online import STEP_IDENTITY
    from skillflow.document_guided.runner import IDENTITY, POLICY, prepare_from_accepted_cfg
    import skillflow

    acceptance = read(project / ACCEPTANCE)
    sync = read(verify / "github-sync.json")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project,
                          capture_output=True, text=True, check=True, timeout=20).stdout.strip()
    if sync.get("status") != "pushed_verified" or sync.get("commit") != head:
        raise ValueError("The verified GitHub synchronization must precede preparation")
    if acceptance["status"] != "passed" or current["sha256"] != acceptance["implementation_sha256"]:
        raise ValueError("The current implementation does not match the offline acceptance")
    if (IDENTITY, STEP_IDENTITY) != (acceptance["guided_identity"], acceptance["step_identity"]):
        raise ValueError("The current guided protocol does not match the offline acceptance")
    if tuple(POLICY[k] for k in ("normal_semantic_calls", "workers", "structural_corrections", "semantic_repairs")) != (7, 2, 1, 1):
        raise ValueError("Authorized budgets changed")
    parent = project / "experiments/doe/runs" / PARENT
    terminal = project / "output/verification" / PARENT_REPORT / "report-closeout.json"
    if (read(terminal)["status"] != "closed" or read(parent / "continuation-state.json")["status"] != "generation_closed"
            or read(parent / "replay-check.json")["status"] != "matched"):
        raise ValueError("The selected upstream is not closed and sealed")
    historical_pins = {p.relative_to(project).as_posix(): sha(p) for p in (terminal, parent / "continuation-state.json",
                       parent / "controller-finished.json", parent / "replay-check.json", parent / "run-protocol.json")}
    old = read(parent / "run-protocol.json")
    local = json.loads((project / PORTABLE_CERTIFICATE).read_bytes())
    if (sha(project / PORTABLE_CERTIFICATE) != acceptance["portable_certificate_sha256"]
            or local["status"] != "passed" or local["implementation_sha256"] != current["sha256"]
            or local["parent"] != parent.name):
        raise ValueError("The accepted local proof belongs to a different build or parent")
    check_files(project, local["local_certificate"]["source_files"])
    renderer_receipt = Path(local["local_renderer"]).parents[3] / "build.json"
    if (sha(renderer_receipt) != local["local_build_receipt_sha256"]
            or read(renderer_receipt) != local["local_build"]):
        raise ValueError("The local renderer build differs from offline acceptance")
    executables = {"cli_executable": str(Path(os.environ.get("SKILLFLOW_GA4_CLI", old["cli_executable"])).resolve()),
                   "cli_executable_sha256": old["cli_executable_sha256"],
                   "renderer_executable": local["local_renderer"],
                   "renderer_executable_sha256": local["local_certificate"]["binary_sha256"],
                   "python_executable": sys.executable, "python_executable_sha256": local["python_sha256"]}
    for field in EXECUTABLES:
        if sha(Path(executables[field])) != executables[field + "_sha256"]:
            raise ValueError("Accepted executable digest differs: " + field)
    module = Path(skillflow.__file__).resolve()
    if module != project / "src/skillflow/__init__.py":
        raise ValueError("The imported SkillFlow package is outside the frozen workspace")
    bound = describe_accepted_upstream(parent, config=CONFIG)
    if (bound["certificate"] != local["certificate_file"]
            or bound["files"].get(local["certificate_file"]) != local["certificate_file_sha256"]
            or local["producer"]["binary_sha256"] != old["renderer_executable_sha256"]):
        raise ValueError("The selected upstream proof differs from the locally reverified donor")
    counts = read(parent / "result.json")["counts"]
    source_hashes = old["source_file_sha256"]
    check_files(parent / "source/inputs/package", source_hashes)
    if len(source_hashes) != 16 or bound["source_sha256"] != SOURCE or bound["inherited_logical_calls"] != 3:
        raise ValueError("Incorrect retained upstream source or requests")
    original_cfg = read(parent / "graph/selected.json")["cfg"]
    if sum(len(b["instructions"]) for b in original_cfg["blocks"].values()) != 489:
        raise ValueError("Incorrect retained CFG")
    now = datetime.now(timezone.utc)
    run = authorized_run(project, project / "experiments/doe/runs" / (RUN_PREFIX + now.astimezone(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")))
    if run.exists() or any((verify / name).exists() for name in ("prepared-run.json", "dispatch-intent.json", "dispatch-started.json")):
        raise ValueError("This one-time experiment was already reserved")
    create(verify / "preparation-intent.json", {"status": "preparing", "run_directory": str(run), "created_at": now.isoformat(),
           "owner": "/root", "authorization": AUTHORIZATION, "maximum_new_runs": 1})
    prepare_from_accepted_cfg(parent, run_dir=run, config=CONFIG)
    inherited = read(run / "accepted-upstream.json")
    if inherited["files"] != bound["files"] or read(run / "graph/initial.json")["cfg"] != original_cfg:
        raise ValueError("Prepared run did not retain the accepted upstream")
    if read_snapshot(run / "source")[1]["source_sha256"] != SOURCE:
        raise ValueError("Prepared run did not retain the complete source")
    create(run / "inherited-inputs.json", {"run_directory": str(parent), "upstream_stage_counts": counts,
           "inherited_parent_cost_not_new": {"known_public_tokens": 303082, "logical_calls": 3}})
    for a, b in (("controller-template.py", "controller.py"), ("lifecycle_guard.py", "lifecycle_guard.py"),
                 ("local_timing.py", "local_timing.py")):
        shutil.copyfile(verify / a, run / b)
    runtime = {**current["files"], **local["local_certificate"]["source_files"],
               **{name: sha(project / name) for name in TOOLS}}
    snapshot = run / "implementation-snapshot"
    snapshot.mkdir()
    for name in runtime:
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(project / name, target)
    check_files(snapshot, runtime)
    create(snapshot / "snapshot.json", {"files": runtime, "controller_sha256": sha(run / "controller.py"),
           "local_timing_sha256": sha(run / "local_timing.py")})
    protocol = {"authorization": AUTHORIZATION, "case_id": "ga4", "guided_run_identity": IDENTITY, "step_identity": STEP_IDENTITY,
                "runtime": {"model": CONFIG["model"], "reasoning_effort": CONFIG["reasoning_effort"], "provider": "openai"},
                "workers": 2, "normal_semantic_requests": 7, "semantic_repairs": 1, "structural_corrections_per_stage": 1,
                "native_timeout_seconds": 2700, "native_extra_transient_attempts": 2, "max_fresh_runs": 1, "max_zero_call_replays": 1,
                "inherited_initial_stages": inherited["inherited_stages"], "fresh_normal_stages": inherited["fresh_normal_stages"],
                "semantic_source_view": "complete_frozen_source", "source_sha256": SOURCE, "source_file_sha256": source_hashes,
                "readable_files": len(source_hashes), "selected_parent_cfg_instructions": 489,
                "implementation_sha256": current["sha256"], "imported_skillflow_module": str(module),
                "offline_acceptance_sha256": sha(project / ACCEPTANCE), "verification_directory": str(verify),
                "portable_certificate_sha256": acceptance["portable_certificate_sha256"],
                "renderer_build_receipt": str(renderer_receipt),
                "renderer_build_receipt_sha256": local["local_build_receipt_sha256"],
                "inherited_renderer_provenance": local["producer"],
                "historical_terminal_pins": historical_pins, "skill_execution": False, "model_probe_calls": 0,
                "github_commit": head, "github_sync_sha256": sha(verify / "github-sync.json"), **executables}
    create(run / "run-protocol.json", protocol)
    run_pins = {name: sha(run / name) for name in ("run-protocol.json", "manifest.json", "accepted-upstream.json",
                "inherited-inputs.json", "implementation-snapshot/snapshot.json", "controller.py", "local_timing.py", "lifecycle_guard.py")}
    verify_pins = {name: sha(verify / name) for name in ("preparation-intent.json", "lifecycle_guard.py", "dispatch_once.ps1",
                   "local_timing.py", "controller-template.py", "github-sync.json")}
    prepared = {"run_directory": str(run), "sole_owner": "/root", "offline_acceptance_sha256": protocol["offline_acceptance_sha256"],
                "run_protocol_sha256": run_pins["run-protocol.json"], "run_pins": run_pins, "verification_pins": verify_pins}
    create(verify / "prepared-run.json", prepared)
    validate_prepared(project, verify, current=current)
    check_files(project, runtime)
    print(json.dumps({"status": "prepared_not_started", "run_directory": str(run), "copied_files": len(inherited["copied_files"])}))


if __name__ == "__main__":
    from skillflow.common.recording import implementation_provenance
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    require_owner(args.owner)
    verify = Path(__file__).resolve().parent
    project = verify.parents[2]
    current = implementation_provenance()
    if args.prepare:
        prepare(project, verify, current)
    else:
        validate_prepared(project, verify, current=current)
