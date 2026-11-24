"""One fresh full-source GA4 analysis and its controller-owned offline replay."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

VERIFY = Path(__file__).resolve().parent
ROOT = VERIFY.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from skillflow.common.artifact_io import atomic_write_text, file_sha256
from skillflow.common.inputs.snapshot import inspect_input
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided import runner
from skillflow.lean_renderer import renderer_path
from tools.doe.document_guided_client import Client, resolve_executable
from tools.doe.document_guided_metrics import transport_metrics

RUNS = ROOT / "experiments/doe/runs"
SOURCE = RUNS / "document-guided-ga4-cfg-assembly-high-20261123-234230/source/inputs/package"
SOURCE_SHA = "3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd"
CONFIG = {"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"}


def read(path):
    return json.loads(path.read_bytes())


def write(path, obj):
    atomic_write_text(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def starts(run):
    return {p.relative_to(run).as_posix(): file_sha256(p) for p in (run / "transport").rglob("started.json")}


def main():
    acceptance = read(VERIFY / "offline-acceptance.json")
    sync = read(VERIFY / "github-sync.json")
    implementation = implementation_provenance()["sha256"]
    head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD^{tree}"], text=True).strip()
    policy = runner.POLICY
    if (runner.IDENTITY != "skillflow-document-guided-run-v23" or
            (policy["normal_semantic_calls"], policy["workers"], policy["structural_corrections"],
             policy["semantic_repairs"]) != (7, 2, 1, 1)):
        raise ValueError("The protocol or seven-stage, two-worker budget differs")
    if (acceptance["status"] != "passed" or acceptance["totals"]["failed"] or sync["status"] != "pushed_verified"
            or not sync["local_and_remote_tree_equal"] or sync["commit"] != head or sync["tree"] != tree
            or not implementation == acceptance["implementation_sha256"] == sync["implementation_sha256"]):
        raise ValueError("The offline and GitHub receipts must bind the current implementation")
    _, source, physical = inspect_input(SOURCE)
    if source["source_sha256"] != SOURCE_SHA or len(physical["files"]) != 16:
        raise ValueError("Expected the complete original sixteen-file source")
    executable, lean = resolve_executable(), renderer_path(None)
    suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
    run = RUNS / ("document-guided-ga4-entry-occurrence-high-" + suffix)
    protocol = {"run": str(run), "started_at": datetime.now(timezone.utc).isoformat(), "controller_pid": os.getpid(),
                "source_sha256": SOURCE_SHA, "source_files": 16, "inherited_stages": [],
                "git_commit": head, "implementation_sha256": implementation, "config": CONFIG,
                "workers": 2, "normal_stages": 7, "timeout_seconds": 2700, "extra_transient_attempts": 2,
                "cli": str(executable), "lean": str(lean), "cli_sha256": file_sha256(executable),
                "lean_sha256": file_sha256(lean)}
    # One atomic claim covers preparation, all requests and the replay.
    with (VERIFY / "dispatch-started.json").open("x", encoding="utf-8") as file:
        json.dump(protocol, file, indent=2)
    runner.prepare(SOURCE, run_dir=run, config=CONFIG)
    write(run / "run-protocol.json", protocol)
    write(run / "controller-started.json", {"pid": os.getpid(), "at": protocol["started_at"], "owner": "/root"})

    def client(stage, owner):
        return Client(run / "transport" / stage, owner=owner, executable=executable,
                      timeout=2700, retries=2, config=CONFIG)

    def progress(event):
        print(event["stage"], event["stages"].get(event["stage"]), flush=True)

    started = time.monotonic()
    reason = None
    try:
        result = runner.run(run, client_factory=client, renderer=lean, progress=progress)
    except Exception as error:
        reason = f"{type(error).__name__}: {error}"
        result = read(run / "result.json")
    analysis = {"status": result["status"], "seconds": time.monotonic() - started,
                "counts": result.get("counts"), "reason": reason or result.get("reason")}
    write(run / "analysis-finished.json", analysis)
    write(run / "metrics.json", transport_metrics(run))
    before = starts(run)
    pending = [p for p in before if not (run / p).with_name("process.json").is_file()
               or not read((run / p).with_name("process.json")).get("exited")]
    replay = {"status": "not_attempted"}
    if not pending and result["status"] in {"complete", "partial", "diagnostic_complete", "failed"}:
        write(run / "replay-started.json", {"controller_pid": os.getpid(), "at": datetime.now(timezone.utc).isoformat()})
        started = time.monotonic()
        try:
            replay["status"] = "matched" if runner.replay(run, renderer=lean) == result else "different"
        except Exception as error:
            replay.update(status="failed", reason=f"{type(error).__name__}: {error}")
        replay["seconds"] = time.monotonic() - started
    after = starts(run)
    replay.update(new_native_starts=len(set(after) - set(before)), native_inventory_unchanged=before == after)
    write(run / "replay-check.json", replay)
    terminal = {"run": str(run), "analysis": analysis, "replay": replay, "native_exit_unconfirmed": pending,
                "finished_at": datetime.now(timezone.utc).isoformat(), "starts": len(before)}
    write(run / "controller-finished.json", terminal)
    write(VERIFY / "controller-finished.json", terminal)
    if replay["status"] != "matched" or before != after:
        raise ValueError("Zero-call replay did not match the terminal result")


if __name__ == "__main__":
    main()
