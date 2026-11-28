"""Passive local snapshots of the sole authorized queue; never starts work."""
from datetime import datetime, timezone
from pathlib import Path
import json

BASE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def main():
    queue = read(BASE / "queue-live.json")
    planned = read(BASE / "prepared-runs.json")
    cases = []
    for item in planned["run_order"]:
        run = Path(item["run_directory"])
        result = read(run / "result.json")
        attempts = []
        for marker in sorted((run / "transport").rglob("started.json")):
            directory = marker.parent
            stdout = directory / "stdout.jsonl"
            events = []
            if stdout.is_file():
                for line in stdout.read_text(encoding="utf-8", errors="replace").splitlines():
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            attempts.append({"path": directory.relative_to(run).as_posix(),
                "started": read(marker), "pid": read(directory / "pid.json"),
                "exit": read(directory / "exit.json"),
                "stdout_bytes": stdout.stat().st_size if stdout.is_file() else 0,
                "event_types": sorted({event.get("type", "unknown") for event in events}),
                "public_error_event_count": sum(event.get("type") == "error" for event in events),
                "last_event_type": events[-1].get("type") if events else None})
        cases.append({"case_id": item["case_id"], "status": result.get("status"), "stage": result.get("stage"),
            "stages": result.get("stages", {}), "repair_used": result.get("repair_used"),
            "native_starts": len(attempts), "attempts": attempts,
            "finished": read(run / "controller-finished.json")})
    value = {"observed_at": datetime.now(timezone.utc).isoformat(), "queue": queue, "cases": cases}
    target = BASE / "observation.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    concise = {"observed_at": value["observed_at"], "phase": queue.get("phase"), "current_case": queue.get("case_id"),
        "cases": [{"case_id": row["case_id"], "status": row["status"],
                   "active_stages": [key for key, stage in row["stages"].items() if stage.get("status") == "running"],
                   "completed_stages": [key for key, stage in row["stages"].items() if stage.get("status") == "complete"],
                   "native_starts": row["native_starts"],
                   "public_error_events": sum(a["public_error_event_count"] for a in row["attempts"]),
                   "repair_used": row["repair_used"], "closed": bool(row["finished"])}
                  for row in cases if row["status"] != "prepared"]}
    print(json.dumps(concise, indent=2))


if __name__ == "__main__":
    main()
