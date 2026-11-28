"""Read-only compact progress for the existing pilot and authorized comparison."""
from pathlib import Path
from datetime import datetime, timezone
import json

BASE = Path(__file__).resolve().parents[1]


def read(path):
    try:
        return json.loads(path.read_text("utf-8"))
    except (FileNotFoundError, ValueError):
        return None


for name in ("pilot/001", "comparison/010", "comparison/013", "comparison/ga4"):
    run = BASE / name
    if not run.exists():
        continue
    paths = sorted((run / "transport").glob("call-*/request.json"))
    requests = [read(path) for path in paths]
    requests = [r for r in requests if r]
    terminal = read(run / "finished.json")
    metadata = read(run / "artifacts/synthesis_metadata.json") or {}
    known = [r["usage"] for r in requests if r.get("usage")]
    last = requests[-1] if requests else {}
    row = {"run": name, "finished": terminal, "requests": len(requests),
           "known_tokens": sum(u.get("input_tokens", 0) + u.get("output_tokens", 0) for u in known),
           "usage_missing": sum(r.get("native_start", False) and not r.get("usage") for r in requests),
           "last_request": last.get("id"), "last_exit": last.get("returncode"),
           "selected_iteration": metadata.get("selected_iteration"),
           "completed_iterations": len(metadata.get("iterations", []))}
    if last.get("started_at_utc") and last.get("returncode") is None:
        row["last_elapsed_seconds"] = round((datetime.now(timezone.utc) - datetime.fromisoformat(last["started_at_utc"])).total_seconds())
    if paths:
        stderr = paths[-1].parent / "stderr.txt"
        if stderr.exists():
            row["last_internal_retries"] = stderr.read_text("utf-8", errors="replace").count("retrying sampling request")
    print(json.dumps(row, ensure_ascii=False))
