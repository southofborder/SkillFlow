"""Record distinct latest offline test outcomes without hiding initial failures."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from skillflow.common.recording import implementation_provenance, canonical_sha256

DIRECTORY = Path(__file__).resolve().parent


def main():
    latest, receipts = {}, []
    parsed = [(path, ET.parse(path).getroot()) for path in DIRECTORY.glob("*.xml")]
    # A long initial run may close after a corrective fresh process. Its old
    # imported modules do not supersede the later-started frozen-source retest.
    for path, document in sorted(parsed, key=lambda item: (next(item[1].iter("testsuite")).get("timestamp", ""), item[0].name)):
        outcomes, failed, skipped = Counter(), [], []
        for case in document.iter("testcase"):
            error = case.find("failure")
            if error is None:
                error = case.find("error")
            status = "failed" if error is not None else "skipped" if case.find("skipped") is not None else "passed"
            identity = (case.get("classname", ""), case.get("name", ""))
            row = {"classname": identity[0], "name": identity[1], "status": status, "receipt": path.name}
            if error is not None:
                row["reason"] = error.get("message", "")
                failed.append(row)
            elif status == "skipped":
                row["reason"] = case.find("skipped").get("message", "")
                skipped.append(row)
            latest[identity] = row
            outcomes[status] += 1
        receipts.append({"path": path.name, "started_at": next(document.iter("testsuite")).get("timestamp"),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "outcomes": dict(outcomes), "failed_tests": failed, "skipped_tests": skipped})
    totals = Counter(row["status"] for row in latest.values())
    current = implementation_provenance()
    python_files = {name: digest for name, digest in current["files"].items() if name.startswith("src/") and name.endswith(".py")}
    acceptance = {"schema_version": "skillflow-input-necessity-offline-acceptance-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if totals["failed"] == 0 and totals["passed"] else "unresolved_failures",
        "distinct_latest_test_outcomes": dict(totals), "whole_repository_all_green_claim": False,
        "scope": "Latest-started per-classname/test-name union of saved scoped offline XML receipts; corrective fresh-process retests supersede earlier-started runs, including overlapping runs that close later; all initial failures retained.",
        "implementation_sha256": current["sha256"], "python_source_sha256": canonical_sha256(python_files),
        "real_model_calls": 0, "skill_executions": 0, "historical_replays": 0,
        "receipts": receipts, "latest_tests": [latest[key] for key in sorted(latest)],
        "limits": ["Semantic contract truth remains source-reviewed, not mechanically proved.",
                   "Optionality requires source/interface evidence.",
                   "Unsupported constraints and unmodeled source ranges remain explicit limitations.",
                   "No Skill source is automatically rewritten."]}
    target = DIRECTORY / "offline-acceptance.json"
    if target.exists():
        raise ValueError("Acceptance already exists; retain it and use a separately named revised receipt")
    target.write_text(json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in acceptance.items() if key not in {"receipts", "latest_tests"}}, indent=2))


if __name__ == "__main__":
    main()
