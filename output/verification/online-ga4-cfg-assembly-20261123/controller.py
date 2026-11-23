"""Prepare, verify or execute the single full GA4 CFG assembly experiment."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
sys.path[:0] = [str(PROJECT / "src"), str(PROJECT)]

from skillflow.common.artifact_io import atomic_write_text, file_sha256
from skillflow.common.inputs.snapshot import inspect_input, read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided import runner
from skillflow.lean_renderer import renderer_path
from tools.doe.document_guided_client import Client, resolve_executable
from tools.doe.document_guided_metrics import transport_metrics

RUNS = PROJECT / "experiments/doe/runs"
DONOR = RUNS / "document-guided-ga4-action-alignment-high-20261123-214712" / "source/inputs/package"
SOURCE = "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"
PREFIX = "document-guided-ga4-cfg-assembly-high-"
NORMAL = ("task", "flow", "graph", "processing", "sensitivity", "task-correspondence", "review")
REVISIONS = ("revision/task", "revision-graph", "revision-processing", "revision-sensitivity",
             "revision-task-correspondence", "revision/review")
TRANSPORT = ("document_guided_client.py", "document_guided_metrics.py", "document_guided_observation.py")
CONFIG = {"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"}
TERMINAL = {"complete", "partial", "failed", "diagnostic_complete"}


def read(path):
    return json.loads(path.read_bytes())


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, record):
    atomic_write_text(path, json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def claim(path, record):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def fixed_policy():
    if runner.IDENTITY != "skillflow-document-guided-run-v22":
        raise ValueError("Expected the guided CFG assembly protocol v22")
    if tuple(runner.POLICY[k] for k in ("normal_semantic_calls", "workers", "structural_corrections", "semantic_repairs")) != (7, 2, 1, 1):
        raise ValueError("Expected seven normal stages, two workers, one correction and one shared repair")


def verify_sync(acceptance, sync, impl, paths):
    certificate, remote = read(acceptance), read(sync)
    if (certificate.get("status") != "passed" or certificate.get("implementation_sha256") != impl["sha256"]
            or remote.get("status") != "pushed_verified" or remote.get("local_and_remote_tree_equal") is not True
            or remote.get("implementation_sha256") != impl["sha256"]):
        raise ValueError("Offline acceptance and the verified GitHub tree must bind this implementation")
    commit = remote["commit"]
    if not re.fullmatch("[a-fA-F0-9]{40,64}", commit):
        raise ValueError("Expected the complete synced commit ID")
    def git(*args):
        return subprocess.check_output(["git", "-C", str(PROJECT), *args], text=True).strip()
    if git("rev-parse", commit + "^{tree}") != remote["tree"]:
        raise ValueError("Synced Git tree disagrees with its commit")
    selected = sorted({*impl["files"], *(p.relative_to(PROJECT).as_posix() for p in paths)})
    tracked = set(git("ls-tree", "-r", "--name-only", commit).splitlines())
    if not set(selected) <= tracked:
        raise ValueError("Runtime files missing from synced commit: " + str(sorted(set(selected) - tracked)))
    git("diff", "--quiet", "--no-ext-diff", commit, "--", *selected)


def prepare(args):
    fixed_policy()
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}", args.suffix):
        raise ValueError("Expected YYYYMMDD-HHMMSS for the fresh run")
    run = RUNS / (PREFIX + args.suffix)
    if run.exists() or any((VERIFY / n).exists() for n in ("preparation-intent.json", "prepared-run.json")):
        raise ValueError("The run or its sole preparation namespace already exists")
    acceptance, sync = args.acceptance.resolve(), args.sync.resolve()
    source = args.source.resolve()
    _, readable, physical = inspect_input(source)
    if readable["source_sha256"] != SOURCE or len(readable["files"]) != 16 or len(physical["files"]) != 16:
        raise ValueError("Expected the complete authorized sixteen-file GA4 source")
    implementation = implementation_provenance()
    helpers = [Path(__file__).resolve(), VERIFY / "assess.py",
               VERIFY.parent / "online-ga4-action-alignment-20261123/assess.py",
               *(VERIFY.parent / "online-ga4-entry-review-20261122" / name
                 for name in ("source_correctness.py", "sensitivity_observations.py")),
               *(PROJECT / "tools/doe" / n for n in TRANSPORT)]
    verify_sync(acceptance, sync, implementation, helpers)
    python, cli, renderer = Path(sys.executable).resolve(), resolve_executable(args.cli), renderer_path(args.renderer)
    pins = [*helpers, acceptance, sync, python, cli, renderer]
    build_receipt = renderer.parents[3] / "build.json"
    if build_receipt.is_file():
        if read(build_receipt).get("binary_sha256") != file_sha256(renderer):
            raise ValueError("Local Lean build receipt disagrees with its executable")
        pins.append(build_receipt)
    protocol = {"run_directory": str(run), "source_donor": str(source), "source_sha256": SOURCE,
        "package_bytes_sha256": physical["package_bytes_sha256"], "source_files": 16,
        "guided_identity": runner.IDENTITY, "config": CONFIG, "policy": runner.POLICY,
        "fresh_normal_stages": list(NORMAL), "inherited_stages": [], "timeout_seconds": 2700, "extra_transient_attempts": 2,
        "maximum_runs": 1, "maximum_replays": 1, "implementation_sha256": implementation["sha256"],
        "git_commit": read(sync)["commit"], "git_tree": read(sync)["tree"], "python": str(python),
        "cli": str(cli), "renderer": str(renderer), "pins": {str(p): file_sha256(p) for p in pins}}
    claim(VERIFY / "preparation-intent.json", {"owner": args.owner, "at": now(), "run_directory": str(run)})
    runner.prepare(source, run_dir=run, config=CONFIG)
    protocol["manifest_sha256"] = file_sha256(run / "manifest.json")
    write(run / "run-protocol.json", protocol)
    receipt = {"run_directory": str(run), "protocol_sha256": file_sha256(run / "run-protocol.json"),
               "intent_sha256": file_sha256(VERIFY / "preparation-intent.json"), "owner": args.owner}
    claim(VERIFY / "prepared-run.json", receipt)
    verify(fresh=True)
    return receipt


def verify(*, fresh=False):
    fixed_policy()
    receipt, intent = read(VERIFY / "prepared-run.json"), VERIFY / "preparation-intent.json"
    run = Path(receipt["run_directory"]).resolve()
    if (run.parent != RUNS.resolve() or not re.fullmatch(PREFIX + r"[0-9]{8}-[0-9]{6}", run.name)
            or receipt["owner"] != "/root" or file_sha256(intent) != receipt["intent_sha256"]
            or read(intent)["run_directory"] != str(run) or read(intent)["owner"] != "/root"
            or file_sha256(run / "run-protocol.json") != receipt["protocol_sha256"]):
        raise ValueError("The sole prepared run does not match its recorded intent and protocol")
    p = read(run / "run-protocol.json")
    if (Path(p["python"]).resolve() != Path(sys.executable).resolve() or p["run_directory"] != str(run)
            or implementation_provenance()["sha256"] != p["implementation_sha256"] or p["config"] != CONFIG
            or p["guided_identity"] != runner.IDENTITY or p["policy"] != runner.POLICY
            or p["fresh_normal_stages"] != list(NORMAL) or p["inherited_stages"]
            or (p["timeout_seconds"], p["extra_transient_attempts"], p["maximum_runs"], p["maximum_replays"]) != (2700, 2, 1, 1)
            or file_sha256(run / "manifest.json") != p["manifest_sha256"]
            or any(file_sha256(Path(name)) != digest for name, digest in p["pins"].items())):
        raise ValueError("Prepared runtime, executables, GitHub receipt or budget changed")
    _, source, raw = read_snapshot(run / "source")
    if (p["source_sha256"] != SOURCE or source["source_sha256"] != SOURCE or len(source["files"]) != 16
            or raw["package_bytes_sha256"] != p["package_bytes_sha256"]
            or any((run / name).exists() for name in ("accepted-upstream.json", "inherited-inputs.json", "inherited"))):
        raise ValueError("The complete original source and seven fresh stages are required")
    if fresh and (read(run / "result.json")["status"] != "prepared"
            or any((run / n).exists() for n in ("controller-started.json", "replay-started.json", "transport", "steps", "task", "review"))):
        raise ValueError("The run has already started")
    return run, p


def native_inventory(run):
    return {p.relative_to(run).as_posix(): file_sha256(p) for name in ("started.json", "pid.json")
            for p in (run / "transport").rglob(name)}


def run_once():
    directory, protocol = verify(fresh=True)
    claim(directory / "controller-started.json", {"pid": os.getpid(), "at": now(), "owner": "/root"})
    class FrozenClient(Client):
        def _execute(self, attempt, delivery):
            verify()
            return super()._execute(attempt, delivery)

    def factory(name, owner):
        if name not in (*NORMAL, *REVISIONS):
            raise ValueError("Unexpected semantic stage: " + name)
        return FrozenClient(directory / "transport" / name, owner=owner, executable=protocol["cli"],
            timeout=protocol["timeout_seconds"], retries=protocol["extra_transient_attempts"], config=CONFIG)

    def progress(event):
        row = {"at": now(), "stage": event["stage"], "state": event["stages"].get(event["stage"]),
               "counts": event["counts"]}
        with (directory / "stage-events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False), flush=True)

    start = time.monotonic()
    error = None
    try:
        result = runner.run(directory, client_factory=factory, renderer=protocol["renderer"], progress=progress)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        result = read(directory / "result.json")
    analysis = {"status": result.get("status"), "finished_at": now(), "seconds": time.monotonic() - start,
                "reason": error or result.get("reason"), "counts": result.get("counts")}
    write(directory / "analysis-finished.json", analysis)
    try:
        write(directory / "metrics.json", transport_metrics(directory))
    except Exception as exc:
        write(directory / "metrics.json", {"status": "unavailable", "reason": f"{type(exc).__name__}: {exc}"})
    before = native_inventory(directory)
    attempts = {(directory / name).parent for name in before}
    pending = sorted(str(p.relative_to(directory)) for p in attempts
                     if not (p / "process.json").is_file() or not read(p / "process.json").get("exited"))
    replay_check = {"status": "not_attempted", "reason": "No terminal analysis or native exits are unconfirmed"}
    if analysis["status"] in TERMINAL and not pending:
        start = time.monotonic()
        try:
            verify()
            claim(directory / "replay-started.json", {"controller_pid": os.getpid(), "at": now()})
            restored = runner.replay(directory, renderer=protocol["renderer"])
            verify()
            replay_check = {"status": "matched" if restored == result else "different"}
        except Exception as exc:
            replay_check = {"status": "failed", "reason": f"{type(exc).__name__}: {exc}"}
        after = native_inventory(directory)
        replay_check.update(seconds=time.monotonic() - start, native_inventory_unchanged=after == before,
                            new_native_starts=len([p for p in after.keys() - before.keys() if p.endswith("/started.json")]))
        if after != before:
            replay_check["status"] = "failed"
    write(directory / "replay-check.json", replay_check)
    summary = {"finished_at": now(), "analysis": analysis, "native_exit_unconfirmed": pending, "replay": replay_check}
    write(directory / "controller-finished.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("prepare")
    setup.add_argument("--suffix", required=True)
    setup.add_argument("--acceptance", required=True, type=Path)
    setup.add_argument("--sync", required=True, type=Path)
    setup.add_argument("--source", default=DONOR, type=Path)
    setup.add_argument("--cli", type=Path)
    setup.add_argument("--renderer", type=Path)
    for command in (setup, commands.add_parser("run")):
        command.add_argument("--owner", required=True, choices=["/root"])
    commands.add_parser("verify")
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args)
    elif args.command == "verify":
        directory, _ = verify(fresh=True)
        result = {"verified": str(directory)}
    else:
        result = run_once()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 1 if args.command == "run" and (result["analysis"]["status"] == "failed"
        or result["replay"]["status"] != "matched") else 0


if __name__ == "__main__":
    raise SystemExit(main())
