"""Observe metadata only; never open live transport or call records."""
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "packages/skill-ir/experiments/semantic_backtrace/runs/controlled-v4-seven-20260918"
rows = []
for path in sorted((RUN / "calls").rglob("transport.json")):
    stat = path.stat()
    stage_path = RUN / "parsed" / (path.parent.parent.name + ".json")
    # Parsed records are installed only after the case has ended.
    stage = json.loads(stage_path.read_text(encoding="utf-8")) if stage_path.is_file() else {}
    rows.append({"call": path.parent.relative_to(RUN / "calls").as_posix(),
                 "case_status": stage.get("status", "pending"), "record_bytes": stat.st_size,
                 "record_updated_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()})
print(json.dumps({
    "ended": {row["call"].split("/")[0]: row["case_status"] for row in rows if row["case_status"] != "pending"},
    "active_records": [row for row in rows if row["case_status"] == "pending"],
}, ensure_ascii=False))
