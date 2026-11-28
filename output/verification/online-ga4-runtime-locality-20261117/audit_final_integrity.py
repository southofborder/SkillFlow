"""Passive terminal byte/receipt audit; never executes a project stage or process."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prepared = read(BASE / "prepared-run.json")
    run = Path(prepared["run_directory"]).resolve()
    if run.parent != (ROOT / "experiments/doe/runs").resolve():
        raise ValueError("Unexpected prepared run directory")
    if run.name != "document-guided-ga4-runtime-locality-high-20261117-205158":
        raise ValueError("Only the sole authorized new run may be audited")
    finished = read(run / "controller-finished.json")
    replay = read(run / "replay-check.json")
    exits = read(run / "native-exit-check.json")
    implementation = read(run / "implementation-check.json")
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    protocol = read(run / "run-protocol.json")
    historical = read(ROOT / "output/verification/runtime-locality-20261117/historical-pins.json")
    historical_changed = [name for name, digest in historical["files"].items()
        if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    runtime_changed = [name for name, digest in snapshot["files"].items()
        if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    executables = {}
    for name in ("cli_executable", "renderer_executable", "python_executable"):
        path = Path(protocol[name])
        actual = sha(path) if path.is_file() else None
        executables[name] = {"path": str(path), "sha256": actual,
            "unchanged": actual == protocol[name + "_sha256"]}
    native_pids = sorted({read(p).get("pid") for p in (run / "transport").rglob("pid.json")
        if type(read(p).get("pid")) is int})
    process_observation = read(BASE / "process-closure-observation.json")
    expected_pids = sorted(set(native_pids + [finished["pid"], read(BASE / "dispatch-started.json")["wrapper_pid"]]))
    observed_pids = sorted(process_observation["requested_pids"])
    if observed_pids != expected_pids:
        raise ValueError("Process observation does not cover every recorded PID")
    observed_time = datetime.fromisoformat(process_observation["observed_at"].replace("Z", "+00:00"))
    finished_time = datetime.fromisoformat(finished["finished_at"].replace("Z", "+00:00"))
    if observed_time < finished_time:
        raise ValueError("Process observation predates controller completion")
    critical_names = ["manifest.json", "run-protocol.json", "accepted-upstream.json", "inherited-inputs.json",
        "controller-started.json", "analysis-finished.json", "controller-finished.json", "replay-started.json",
        "replay-check.json", "implementation-check.json", "native-exit-check.json", "restart-accounting.json",
        "metrics.json", "component-timing.json", "result.json", "selection.json", "graph/initial.json",
        "graph/selected.json", "review/result.json", "revision/review/result.json", "propagation/manifest.json",
        "propagation/records.json", "doe/doe-result.json", "doe/audit/demand-support.json"]
    critical = {name: sha(run / name) for name in critical_names if (run / name).is_file()}
    value = {"identity": "skillflow-runtime-locality-terminal-integrity-v1",
        "observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(run),
        "implementation_sha256": prepared["implementation_sha256"],
        "runtime_pins": {"count": len(snapshot["files"]), "changed": runtime_changed},
        "historical_pins": {"count": len(historical["files"]), "changed": historical_changed},
        "executables": executables, "controller_check": implementation,
        "native_exit_receipt": exits, "replay": replay,
        "recorded_pids": expected_pids, "process_observation": process_observation,
        "all_recorded_pids_absent": (process_observation.get("remaining_recorded_processes") == 0
            and process_observation.get("processes") == []),
        "critical_artifacts_sha256": critical,
        "method": "Read-only JSON receipt and byte hash audit. No project imports, models, stages, tests, Skill execution, subprocess or replay."}
    value["integrity_passed"] = (not runtime_changed and not historical_changed
        and all(row["unchanged"] for row in executables.values())
        and implementation.get("unchanged") is True
        and exits.get("all_attempt_exits_confirmed") is True
        and value["all_recorded_pids_absent"]
        and replay.get("new_native_markers") == 0
        and replay.get("native_inventory_unchanged") is True)
    with (BASE / "final-integrity.json").open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({key: value[key] for key in ("integrity_passed", "all_recorded_pids_absent", "runtime_pins", "historical_pins")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
