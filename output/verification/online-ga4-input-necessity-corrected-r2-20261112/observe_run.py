"""Passive local run observation; no analysis, model calls or replay."""
from datetime import datetime, timezone
from pathlib import Path
import json
import time
import sys

BASE = Path(__file__).resolve().parent


def read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def observe():
    prepared = read(BASE / "prepared-run.json")
    run = Path(prepared["run_directory"])
    result = read(run / "result.json")
    attempts = []
    for marker in sorted((run / "transport").rglob("started.json")):
        directory = marker.parent
        process = read(directory / "process.json")
        public_errors = []
        stdout = directory / "stdout.jsonl"
        if stdout.is_file():
            for line in stdout.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("type") in {"error", "turn.failed"}:
                    public_errors.append(event.get("message", event.get("error")))
        attempts.append({"path": directory.relative_to(run).as_posix(),
            "pid": read(directory / "pid.json").get("pid"),
            "status": process.get("status", "running"),
            "elapsed_seconds": process.get("elapsed_seconds"),
            "public_errors": public_errors})
    started = read(run / "controller-started.json")
    finished = read(run / "controller-finished.json")
    state = {"observed_at": datetime.now(timezone.utc).isoformat(),
        "status": result.get("status"), "stage": result.get("stage"),
        "stages": {key: value.get("status") for key, value in result.get("stages", {}).items()},
        "repair_used": result.get("repair_used"), "native_starts": len(attempts),
        "attempts": attempts, "controller": started, "finished": finished,
        "analysis_finished": read(run / "analysis-finished.json")}
    temporary = BASE / "observation.tmp"
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(BASE / "observation.json")
    brief = {key: state[key] for key in ("status", "stage", "stages", "repair_used", "native_starts")}
    brief["running_requests"] = [row["path"].split("/")[1] for row in attempts if row["status"] == "running"]
    errors = [error for row in attempts for error in row["public_errors"]]
    brief["public_error_events"] = len(errors)
    brief["latest_public_error"] = errors[-1] if errors else None
    brief["analysis_finished"] = bool(state["analysis_finished"])
    brief["controller_closed"] = bool(finished)
    if finished:
        brief["replay"] = finished.get("replay")
    return state, brief


def main():
    watch = "--watch" in sys.argv
    previous = None
    while True:
        state, brief = observe()
        if brief != previous:
            print(json.dumps({"observed_at": state["observed_at"], **brief}), flush=True)
            previous = brief
        if not watch or state["finished"]:
            break
        time.sleep(10)


if __name__ == "__main__":
    main()
