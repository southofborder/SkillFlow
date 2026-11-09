"""Sole sequential owner of the four newly prepared backend r3 controllers."""
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


def read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save(value):
    value.update(observed_at=datetime.now(timezone.utc).isoformat(), supervisor_pid=os.getpid())
    path = VERIFY / "queue-live.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")
    temp.replace(path)


def main():
    with (VERIFY / "queue-started.json").open("x",encoding="utf-8") as handle:
        json.dump({"pid":os.getpid(),"started_at":datetime.now(timezone.utc).isoformat()},handle)
    queue = read(VERIFY / "prepared-runs.json")
    completed = []
    try:
        if [item["case_id"] for item in queue["run_order"]] != ["ga4","001","010","013"]:
            raise RuntimeError("Prepared case order differs from authorization")
        for item in queue["run_order"]:
            if (VERIFY / "queue-stop.json").exists():
                raise RuntimeError("Queue stop retained; no new controller launched")
            if implementation_provenance()["sha256"] != queue["implementation_sha256"]:
                raise RuntimeError("Frozen implementation changed; no new controller launched")
            run = Path(item["run_directory"])
            if (run / "controller-started.json").exists():
                raise RuntimeError("Controller already started; refusing duplicate/resume")
            protocol = read(run / "run-protocol.json")
            cli = Path(protocol["cli_executable"])
            if not cli.is_file() or hashlib.sha256(cli.read_bytes()).hexdigest() != protocol["cli_executable_sha256"]:
                raise RuntimeError("The prepared CLI installation changed; no new controller launched")
            with (run / "controller-output.log").open("xb") as output:
                child = subprocess.Popen([sys.executable,"-B","-u",str(run / "controller.py")],
                    cwd=PROJECT,stdout=output,stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
                save({"phase":"running_case","case_id":item["case_id"],"run_directory":str(run),
                      "controller_pid":child.pid,"completed":completed})
                while child.poll() is None:
                    time.sleep(10)
            finished = read(run / "controller-finished.json")
            completed.append({"case_id":item["case_id"],"run_directory":str(run),
                              "returncode":child.returncode,"controller_finished":finished})
            terminal = {"complete", "partial", "failed", "diagnostic_complete"}
            if (not finished or finished.get("status") not in terminal
                    or read(run / "result.json").get("status") not in terminal
                    or (finished.get("controller_error") or {}).get("type") == "KeyboardInterrupt"):
                raise RuntimeError("Controller lacks a terminal analysis result or was interrupted; remaining cases not launched")
            if read(run / "implementation-check.json").get("unchanged") is not True:
                raise RuntimeError("Frozen run dependencies changed; remaining cases not launched")
        save({"phase":"all_four_closed","completed":completed,"reports_pending":True})
    except BaseException as error:
        save({"phase":"queue_stopped","completed":completed,"error_type":type(error).__name__,"error":str(error)})
        (VERIFY / "queue-error.txt").write_text(traceback.format_exc(),encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
