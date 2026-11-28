"""Root-dispatched sole queue: GA4, 001, 010, 013; no old-run resume."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance

VERIFY = Path(__file__).resolve().parent
ORDER = ["ga4", "001", "010", "013"]
TERMINAL = {"complete", "partial", "failed", "diagnostic_complete"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def save(value):
    atomic_json(VERIFY / "queue-live.json", {**value,
        "observed_at": datetime.now(timezone.utc).isoformat(), "supervisor_pid": os.getpid()})


def main():
    # Exclusive creation consumes the one queue start; complete marker publication
    # is atomic. A crash does not authorize deleting this marker and restarting.
    with (VERIFY / "queue-started.json").open("x", encoding="utf-8"):
        pass
    atomic_json(VERIFY / "queue-started.json", {"pid": os.getpid(),
        "started_at": datetime.now(timezone.utc).isoformat(), "python_executable": sys.executable})
    completed = []
    try:
        queue = read(VERIFY / "prepared-runs.json")
        if [item["case_id"] for item in queue["run_order"]] != ORDER or queue["global_analysis_workers"] != 2:
            raise RuntimeError("Prepared case order or worker count differs from authorization")
        directories = [Path(item["run_directory"]).resolve() for item in queue["run_order"]]
        if len(set(directories)) != 4 or any(not path.is_relative_to(PROJECT / "experiments/doe/runs") for path in directories):
            raise RuntimeError("Four distinct new run directories must belong to this workspace")
        for item, run in zip(queue["run_order"], directories):
            if (VERIFY / "queue-stop.json").exists():
                raise RuntimeError("Queue stop retained; no new controller launched")
            if implementation_provenance()["sha256"] != queue["implementation_sha256"]:
                raise RuntimeError("Frozen implementation changed; no new controller launched")
            if (run / "controller-started.json").exists() or (run / "replay-started.json").exists():
                raise RuntimeError("Controller or replay already started; refusing duplicate or resume")
            if read(run / "result.json").get("status") != "prepared":
                raise RuntimeError("The next case is not a fresh prepared run")
            protocol = read(run / "run-protocol.json")
            if (protocol["implementation_sha256"] != queue["implementation_sha256"]
                    or protocol["source_sha256"] != item["source_sha256"]):
                raise RuntimeError("Run protocol differs from the prepared queue")
            for field in ("cli_executable", "renderer_executable"):
                executable = Path(protocol[field])
                if (not executable.is_file()
                        or hashlib.sha256(executable.read_bytes()).hexdigest() != protocol[field + "_sha256"]):
                    raise RuntimeError("A frozen native executable changed; no controller launched")
            # Root copies exactly the reviewed scripts; do not execute stale helpers.
            for source, target in (("controller-template.py", "controller.py"), ("local_timing.py", "local_timing.py")):
                if (VERIFY / source).read_bytes() != (run / target).read_bytes():
                    raise RuntimeError("Prepared controller helper differs from the reviewed template")
            with (run / "controller-output.log").open("xb") as output:
                child = subprocess.Popen([sys.executable, "-B", "-u", str(run / "controller.py")],
                    cwd=PROJECT, stdout=output, stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                save({"phase": "running_case", "case_id": item["case_id"], "run_directory": str(run),
                      "controller_pid": child.pid, "completed": completed})
                while child.poll() is None:
                    time.sleep(10)
            finished = read(run / "controller-finished.json")
            completed.append({"case_id": item["case_id"], "run_directory": str(run),
                              "returncode": child.returncode, "controller_finished": finished})
            if (finished.get("status") not in TERMINAL or read(run / "result.json").get("status") not in TERMINAL
                    or (finished.get("controller_error") or {}).get("type") == "KeyboardInterrupt"):
                raise RuntimeError("No terminal analysis receipt or controller interrupted; remaining cases not launched")
            if read(run / "implementation-check.json").get("unchanged") is not True:
                raise RuntimeError("Frozen run dependencies changed; remaining cases not launched")
            replay_check = read(run / "replay-check.json")
            if not (run / "replay-started.json").is_file() or replay_check.get("new_native_markers") != 0:
                raise RuntimeError("Sole zero-call replay was not established; remaining cases not launched")
            # A recorded failed analysis or failed replay is retained as a result;
            # it never creates a second attempt or consumes another case's budget.
        save({"phase": "all_four_closed", "completed": completed, "reports_pending": True})
    except BaseException as error:
        save({"phase": "queue_stopped", "completed": completed,
              "error_type": type(error).__name__, "error": str(error)})
        (VERIFY / "queue-error.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
