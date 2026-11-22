"""Check current scoped offline results before Git synchronization and GA4."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance

BASE = Path(__file__).resolve().parent
SUITES = ("common-task.junit.xml", "guided.junit.xml", "doe.junit.xml",
          "guided-recheck.junit.xml", "doe-recheck.junit.xml", "alignment-final.junit.xml",
          "encoding.junit.xml", "display-final.junit.xml", "codec-final.junit.xml", "compat-final.junit.xml")
IMPLEMENTATION = "6126c7ba84984aec0d20ead0693df291ea3978a4072056dbd6428321bdfd627b"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    current = implementation_provenance()
    if current["sha256"] != IMPLEMENTATION:
        raise ValueError("Production changed after offline checks")
    latest, suites = {}, {}
    for name in SUITES:
        states = Counter()
        for case in ET.parse(BASE / name).iter("testcase"):
            status = ("failed" if case.find("failure") is not None or case.find("error") is not None else
                      "skipped" if case.find("skipped") is not None else "passed")
            latest[(case.attrib["classname"], case.attrib["name"])] = status
            states[status] += 1
        suites[name] = {"sha256": sha(BASE / name), **states}
    counts = Counter(latest.values())
    if counts["failed"]:
        raise ValueError("The named scoped checks retain an unresolved failure")
    inputs = json.loads((BASE / "saved-inputs-accepted.json").read_text(encoding="utf-8"))
    if inputs["status"] != "passed" or inputs["implementation_sha256"] != IMPLEMENTATION:
        raise ValueError("The saved-material check is not bound to current production")
    helpers = PROJECT / "output/verification/online-ga4-lossless-delivery-20261119"
    helper_files = {p.relative_to(PROJECT).as_posix(): sha(p)
                    for p in sorted(helpers.iterdir()) if p.is_file()}
    for path in helpers.glob("*.py"):
        compile(path.read_bytes(), str(path), "exec")
    result = {"identity": "skillflow-lossless-delivery-offline-v1", "status": "passed",
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": IMPLEMENTATION, "implementation_files": len(current["files"]),
        "latest_distinct_scoped_results": dict(counts),
        "method": "Latest result per named test node across scoped scans and explicit final rechecks; not one whole-repository execution.",
        "original_failures_preserved": True, "suites": suites,
        "source_material_check": {"file": "saved-inputs-accepted.json",
                                  "sha256": sha(BASE / "saved-inputs-accepted.json")},
        "test_environment": {"lock": "requirements-lock-final.txt", "sha256": sha(BASE / "requirements-lock-final.txt")},
        "lifecycle_file_sha256": helper_files,
        "policy": {"normal_semantic_stages": 7, "workers": 2, "structural_corrections_per_stage": 1,
                   "shared_repair_rounds": 1, "native_deadline_seconds": 2700, "extra_transient_native_attempts": 2,
                   "source": "complete", "validation": "strict"},
        "offline_activity": {"native_model_calls": 0, "skill_executions": 0, "historical_run_replays": 0}}
    with (BASE / "offline-acceptance.json").open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"status": "passed", "latest": dict(counts), "implementation_sha256": IMPLEMENTATION}))


if __name__ == "__main__":
    main()
