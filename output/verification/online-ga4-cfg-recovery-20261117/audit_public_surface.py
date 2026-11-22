"""Passive public item-type and transport-cause inventory for the sole new run.

No private session access, answer/reasoning bodies, process control, subprocess,
model calls, analysis or replay. Writes only new verification audit snapshots.
"""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from lifecycle_guard import authorized_run


VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]


def read(path):
    return json.loads(path.read_bytes().decode("utf-8")) if path.is_file() else {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def tag(value):
    return value if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", value) else "unrecognized_tag"


def main():
    prepared = read(VERIFY / "prepared-run.json")
    run = authorized_run(PROJECT, prepared["run_directory"])
    if (prepared.get("case_id") != "ga4" or run.parent != (PROJECT / "experiments/doe/runs").resolve()
            or not run.name.startswith("document-guided-ga4-cfg-recovery-high-")):
        raise ValueError("Prepared run is outside the sole fresh GA4 namespace")
    closed_before = read(run / "controller-finished.json")
    rows = []
    for directory in sorted({p.parent for p in (run / "transport").rglob("pid.json")}):
        pid = read(directory / "pid.json").get("pid")
        if type(pid) is not int or pid <= 0:
            continue
        stdout, stderr = directory / "stdout.jsonl", directory / "stderr.txt"
        raw_out = stdout.read_bytes() if stdout.is_file() else b""
        raw_err = stderr.read_bytes() if stderr.is_file() else b""
        events, items, malformed = Counter(), Counter(), 0
        for line in raw_out.decode("utf-8", errors="replace").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                malformed += 1
                continue
            if not isinstance(event, dict):
                malformed += 1
                continue
            events[tag(event.get("type"))] += 1
            if event.get("type") == "item.completed" and isinstance(event.get("item"), dict):
                items[tag(event["item"].get("type"))] += 1
        notices = []
        for number, line in enumerate(raw_err.decode("utf-8", errors="replace").splitlines(), 1):
            if "responses_retry" not in line:
                continue
            stamp = re.search(r"\d{4}-\d\d-\d\dT[0-9:.]+Z", line)
            retry = re.search(r"\((\d+)/(\d+) in (\d+)ms\)", line)
            cause = ("connection_reset_os_error_10054" if "os error 10054" in line else
                     "request_timed_out" if "request timed out" in line.lower() else
                     "stream_closed" if "stream closed" in line.lower() else
                     "other_public_responses_retry")
            notices.append({"line": number, "timestamp": stamp[0] if stamp else None,
                "cause": cause, "sampling_retry": "retrying sampling request" in line,
                "connection_wait": "stream connection failed; waiting to retry" in line,
                "retry_ordinal": int(retry[1]) if retry else None,
                "reported_retry_limit": int(retry[2]) if retry else None,
                "reported_backoff_ms": int(retry[3]) if retry else None,
                "public_line_sha256": sha(line.encode("utf-8"))})
        rows.append({"request": directory.relative_to(run).as_posix(), "pid": pid,
            "public_event_types": dict(events), "completed_item_types": dict(items),
            "other_completed_item_types": {name: count for name, count in items.items()
                                           if name not in {"reasoning", "agent_message"}},
            "malformed_public_lines": malformed, "transport_notices": notices,
            "stdout_sha256": sha(raw_out), "stderr_sha256": sha(raw_err),
            "process_status": read(directory / "process.json").get("status")})
    closed_after = read(run / "controller-finished.json")
    result = {"observed_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(run),
        "provisional": not bool(closed_before and closed_before == closed_after),
        "scope": "Public event/item types and bounded transport-cause classifications only",
        "confirmed_native_processes": len(rows), "requests": rows,
        "other_completed_item_types": dict(sum((Counter(row["other_completed_item_types"]) for row in rows), Counter())),
        "transport_cause_counts": dict(Counter(n["cause"] for row in rows for n in row["transport_notices"])),
        "notice": "Internal retry notices can overlap stdout errors and do not establish HTTP counts, additional usage or new processes. Public request timeout text is distinct from native process timeout receipts. Item-type absence establishes only the visible public event inventory; no item bodies or private sessions were inspected.",
        "prepared_run_sha256": sha((VERIFY / "prepared-run.json").read_bytes()),
        "audit_utility_sha256": sha(Path(__file__).read_bytes())}
    folder = VERIFY / "cost-provenance-audit"
    folder.mkdir(exist_ok=True)
    target = folder / ("public-surface-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with target.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2); handle.write("\n")
    print(json.dumps({"report": str(target), "provisional": result["provisional"],
        "confirmed_native_processes": len(rows), "transport_cause_counts": result["transport_cause_counts"],
        "other_completed_item_types": result["other_completed_item_types"]}))


if __name__ == "__main__":
    main()
