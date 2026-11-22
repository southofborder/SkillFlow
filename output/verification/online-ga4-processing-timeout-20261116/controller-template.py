"""One fresh authorized shared-processing GA4 and its sole zero-call replay.

Root copies this file to the new run's controller.py beside local_timing.py.
Nothing runs on import; this template does not prepare or resume a run.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import sys
import time
import traceback

PROJECT = Path("D:/Projects/SkillFlow")
sys.path.insert(0, str(PROJECT))

import skillflow
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import POLICY, run as analyze, replay
from tools.doe.document_guided_client import Client
from tools.doe.document_guided_metrics import transport_metrics
from local_timing import LocalTiming

RUN = Path(__file__).resolve().parent
TERMINAL = {"complete", "partial", "failed", "diagnostic_complete"}
CONFIG = {"model": "gpt-6.1-sol", "reasoning_effort": "high", "response_format": "json_object"}
TRANSPORT_FILES = {"tools/doe/document_guided_client.py", "tools/doe/document_guided_metrics.py",
                   "tools/doe/document_guided_pilot.py", "tools/doe/document_guided_observation.py"}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object: " + str(path))
    return value


def write(name, value):
    path = RUN / name
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def claim(name, value):
    # Exclusive creation owns this attempt even if the process dies immediately;
    # atomic replacement publishes the complete marker without allowing resume.
    with (RUN / name).open("x", encoding="utf-8"):
        pass
    write(name, value)


def dependency_report(protocol):
    snapshot = read(RUN / "implementation-snapshot/snapshot.json")
    current = implementation_provenance()
    files = snapshot["files"]
    required = set(current["files"]) | TRANSPORT_FILES
    missing = sorted(required - set(files))
    changed = [name for name, digest in files.items()
               if not (PROJECT / name).is_file()
               or hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() != digest]
    for field in ("cli_executable", "renderer_executable", "python_executable"):
        path = Path(protocol[field])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != protocol[field + "_sha256"]:
            changed.append(field)
    for name, key in (("controller.py", "controller_sha256"), ("local_timing.py", "local_timing_sha256")):
        path = RUN / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != snapshot[key]:
            changed.append(name)
    if Path(skillflow.__file__).resolve() != Path(protocol["imported_skillflow_module"]).resolve():
        changed.append("imported_skillflow_module")
    if Path(sys.executable).resolve() != Path(protocol["python_executable"]).resolve():
        changed.append("running_python_executable")
    if current["sha256"] != protocol["implementation_sha256"]:
        changed.append("implementation_provenance")
    return {"unchanged": not changed and not missing, "changed_files": sorted(changed),
            "missing_snapshot_files": missing, "implementation_sha256": current["sha256"]}


def require_frozen(protocol):
    report = dependency_report(protocol)
    if not report["unchanged"]:
        write("implementation-check.json", report)
        raise RuntimeError("Frozen production, transport or renderer changed; no fresh call or replay is allowed")
    return report


def native_exit_report():
    """A terminal controller outcome does not prove that a native child exited."""
    unconfirmed = []
    markers = sorted((RUN / "transport").rglob("started.json"))
    for marker in markers:
        receipt = marker.parent / "process.json"
        try:
            confirmed = read(receipt).get("exited") is True
        except (OSError, ValueError):
            confirmed = False
        if not confirmed:
            unconfirmed.append(marker.parent.relative_to(RUN).as_posix())
    return {"all_attempt_exits_confirmed": not unconfirmed,
            "attempt_markers": len(markers), "unconfirmed_attempts": unconfirmed}


def main():
    if not RUN.is_relative_to(PROJECT / "experiments/doe/runs"):
        raise RuntimeError("Copy this template into a root-prepared fresh run before dispatch")
    manifest, protocol = read(RUN / "manifest.json"), read(RUN / "run-protocol.json")
    if manifest["config"] != CONFIG or manifest["policy"] != POLICY:
        raise RuntimeError("Prepared configuration or current policy differs from the authorized batch")
    if (POLICY["workers"], POLICY["normal_semantic_calls"], POLICY["structural_corrections"],
            POLICY["semantic_repairs"]) != (2, 7, 1, 1):
        raise RuntimeError("The authorized worker/call/repair budgets changed")
    if read(RUN / "result.json").get("status") != "prepared":
        raise RuntimeError("Only a fresh prepared result can start; no old run or stage is resumed")
    if (RUN / "replay-started.json").exists() or any((RUN / "transport").rglob("started.json")):
        raise RuntimeError("This directory already contains a native attempt or replay")
    _, source, _ = read_snapshot(RUN / "source")
    if source["source_sha256"] != protocol["source_sha256"]:
        raise RuntimeError("Frozen source differs from the authorized package")
    require_frozen(protocol)
    started, counter = stamp(), time.perf_counter()
    marker = {"pid": os.getpid(), "started_at": started, "python_executable": sys.executable}
    claim("controller-started.json", marker)
    write("continuation-state.json", {**marker, "status": "running", "run_directory": str(RUN),
        "instructions": "Root owns this sole controller. Observe local artifacts only; do not launch duplicates, change frozen files or resume old runs."})

    def progress(value):
        event = {"observed_at": stamp(), "stage": value["stage"],
                 "stage_state": value["stages"].get(value["stage"]), "counts": value.get("counts", {}),
                 "repair_used": value.get("repair_used", False)}
        with (RUN / "stage-events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(json.dumps(event, ensure_ascii=False), flush=True)

    class FrozenClient(Client):
        def _execute(self, directory, delivery):
            # Check before the transport records a native-start marker, including
            # its existing retry attempts. A blocked launch must not inflate cost.
            require_frozen(protocol)
            return super()._execute(directory, delivery)

    timing = LocalTiming().install()
    outcome, crash = None, None
    try:
        outcome = analyze(RUN, client_factory=lambda name, owner: FrozenClient(
            RUN / "transport" / name, owner=owner, executable=protocol["cli_executable"],
            timeout=2700, retries=2, config=manifest["config"]),
            renderer=protocol["renderer_executable"], progress=progress)
    except BaseException as error:
        crash = {"type": type(error).__name__, "reason": str(error)}
        (RUN / "controller-traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
    elapsed = time.perf_counter() - counter
    write("analysis-finished.json", {"started_at": started, "finished_at": stamp(),
        "analysis_seconds": elapsed, "status": None if outcome is None else outcome["status"], "controller_error": crash})
    try:
        write("metrics.json", transport_metrics(RUN))
    except Exception as error:
        write("metrics.json", {"status": "unavailable", "reason": type(error).__name__ + ": " + str(error)})
    if outcome is None and (RUN / "result.json").is_file():
        saved = read(RUN / "result.json")
        if saved.get("status") in TERMINAL:
            outcome = saved
    checked = {"status": "not_attempted", "new_native_markers": None}
    if outcome is not None and outcome["status"] in TERMINAL and (crash or {}).get("type") != "KeyboardInterrupt":
        before = len(list((RUN / "transport").rglob("started.json")))
        replay_start = time.perf_counter()
        try:
            require_frozen(protocol)
            claim("replay-started.json", {"pid": os.getpid(), "started_at": stamp(), "maximum_replays": 1})
            timing.phase = "replay"
            restored = replay(RUN, renderer=protocol["renderer_executable"])
            checked = {"status": "matched" if restored == outcome else "different"}
        except Exception as error:
            checked = {"status": "failed", "reason": type(error).__name__ + ": " + str(error)}
        checked.update(elapsed_seconds=time.perf_counter() - replay_start,
            new_native_markers=len(list((RUN / "transport").rglob("started.json"))) - before)
        if checked["new_native_markers"] != 0:
            checked.update(status="failed", reason="The sole offline replay changed the native-start inventory")
    timing.restore()
    write("component-timing.json", timing.snapshot())
    write("replay-check.json", checked)
    write("implementation-check.json", dependency_report(protocol))
    exits = native_exit_report()
    write("native-exit-check.json", exits)
    write("controller-finished.json", {"pid": os.getpid(), "finished_at": stamp(),
        "status": None if outcome is None else outcome["status"], "analysis_seconds": elapsed,
        "controller_error": crash, "replay": checked, "native_exits": exits})
    write("continuation-state.json", {"status": "generation_closed" if exits["all_attempt_exits_confirmed"] else "native_exit_unconfirmed", "run_directory": str(RUN),
        "controller_pid": os.getpid(), "analysis_seconds": elapsed,
        "analysis_status": None if outcome is None else outcome["status"], "replay": checked, "native_exits": exits,
        "instructions": "Controller finished: preserve actual requests, failures, source and review receipts. Do not regenerate or resume. Check native_exits before claiming process closure; root reports coverage, correctness, DOE and full available cost."})
    print(json.dumps({"controller_closed": True, "status": None if outcome is None else outcome["status"],
                      "analysis_seconds": elapsed, "replay": checked}), flush=True)
    return 0 if outcome is not None and outcome["status"] in {"complete", "partial", "diagnostic_complete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
