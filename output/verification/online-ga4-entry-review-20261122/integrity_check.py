"""Check process closure and pins without launching or replaying the analysis."""
import csv
import json
from pathlib import Path
import subprocess

from skillflow.common.recording import implementation_provenance
from lifecycle_guard import (ACCEPTANCE, PARENT, PARENT_REPORT, check_files, native_inventory,
                             read, sha, validate_prepared)

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]


def main():
    prepared = read(VERIFY / "prepared-run.json")
    dispatch = read(VERIFY / "dispatch-started.json")
    if (dispatch["prepared_run_sha256"] != sha(VERIFY / "prepared-run.json")
            or prepared["run_directory"] != dispatch["run_directory"]):
        raise ValueError("The sole dispatch does not match preparation")
    run, protocol = validate_prepared(PROJECT, VERIFY, current=implementation_provenance(), fresh=False)
    controller = read(run / "controller-finished.json")
    state = read(run / "continuation-state.json")
    replay = read(run / "replay-check.json")
    if state["status"] != "generation_closed" or controller["replay"] != replay:
        raise ValueError("The controller has not closed with matching receipts")
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    check_files(PROJECT, snapshot["files"])
    check_files(run / "implementation-snapshot", snapshot["files"])
    parent_report = PROJECT / "output/verification" / PARENT_REPORT
    parent_closeout = read(parent_report / "report-closeout.json")
    # These maps are the parent's explicit seal, not a claim about unsealed files.
    evidence = parent_closeout["run_evidence_sha256"]
    check_files(PROJECT, {name: digest for name, digest in evidence.items()
                          if name.startswith(("experiments/", "output/"))})
    check_files(parent_report, {name: digest for name, digest in evidence.items()
                                if not name.startswith(("experiments/", "output/"))})
    check_files(parent_report, parent_closeout["reports_and_helpers_sha256"])
    native = {read(p)["pid"] for p in (run / "transport").rglob("pid.json")}
    recorded = native | {dispatch["wrapper_pid"], controller["pid"]}
    processes = subprocess.run(["tasklist.exe", "/FO", "CSV", "/NH"],
                               capture_output=True, check=True, timeout=20).stdout
    active = {int(row[1]) for row in csv.reader(processes.decode("utf-8", errors="replace").splitlines())
              if len(row) >= 2 and row[1].isdecimal()}
    inherited = read(run / "accepted-upstream.json")
    print(json.dumps({"status": "closed" if not recorded & active else "recorded_pid_still_present",
        "run_directory": str(run), "runtime_pins_unchanged": len(snapshot["files"]),
        "executable_pins_unchanged": 3, "offline_acceptance_sha256": sha(PROJECT / ACCEPTANCE),
        "source_files_unchanged": len(protocol["source_file_sha256"]),
        "inherited_original_files_unchanged": len(inherited["files"]),
        "inherited_copies_unchanged": len(inherited["copied_files"]),
        "parent_sealed_report_files_unchanged": len(parent_closeout["reports_and_helpers_sha256"]),
        "parent_sealed_evidence_files_unchanged": len(evidence),
        "native_start_and_pid_inventory": native_inventory(run), "native_pid_count": len(native),
        "recorded_pid_count": len(recorded), "recorded_pids_still_present": sorted(recorded & active),
        "replay": replay}, indent=2))


if __name__ == "__main__":
    main()
