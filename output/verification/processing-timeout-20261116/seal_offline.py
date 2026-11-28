"""Seal current scoped offline evidence; never prepares or starts an experiment."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

PROJECT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.runner import IDENTITY, POLICY

VERIFY = Path(__file__).resolve().parent
ONLINE = VERIFY.parent / "online-ga4-processing-timeout-20261116"
TOOLS = ("document_guided_client.py", "document_guided_metrics.py",
         "document_guided_pilot.py", "document_guided_observation.py")
HELPERS = ("prepare_run.py", "controller-template.py", "dispatch_once.ps1", "local_timing.py")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path):
    xml = ET.parse(path).getroot()
    rows = []
    for case in xml.iter("testcase"):
        result = ("failed" if case.find("failure") is not None or case.find("error") is not None else
                  "skipped" if case.find("skipped") is not None else "passed")
        rows.append({"identity": case.attrib.get("classname", "") + "::" + case.attrib["name"], "status": result})
    return {"path": path.relative_to(PROJECT).as_posix(), "sha256": sha(path), "tests": len(rows),
            "passed": sum(row["status"] == "passed" for row in rows),
            "failed": sum(row["status"] == "failed" for row in rows),
            "skipped": sum(row["status"] == "skipped" for row in rows), "cases": rows}


def main():
    # This final full affected scope is produced only after all final corrections.
    final = receipt(VERIFY / "scoped-regression-final.xml")
    if not final["tests"] or final["failed"] or final["skipped"]:
        raise ValueError("Final affected-scope regression is not fully passing")
    if (POLICY["normal_semantic_calls"], POLICY["workers"], POLICY["structural_corrections"],
            POLICY["semantic_repairs"]) != (7, 2, 1, 1):
        raise ValueError("Authorized schedule or repair budget changed")
    if any((ONLINE / name).exists() for name in ("preparation-intent.json", "prepared-run.json", "dispatch-intent.json")):
        raise ValueError("Acceptance must be sealed before fresh preparation or dispatch")
    baseline = read(VERIFY / "baseline.json")
    changed = [name for name, expected in baseline["closed_verification_files"].items()
               if not (PROJECT / name).is_file() or sha(PROJECT / name) != expected]
    if changed:
        raise ValueError("Closed verification artifacts changed: " + str(changed))
    current = implementation_provenance()
    tested = read(VERIFY / "final-test-inputs.json")
    if current != tested["implementation"] or any(
            sha(PROJECT / name) != digest for name, digest in tested["other_file_sha256"].items()):
        raise ValueError("Implementation, transport or lifecycle helper changed during final verification")
    receipts = [receipt(path) for path in sorted(VERIFY.glob("*.xml"))]
    value = {"status": "passed", "sealed_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "implementation": current,
        "guided_run_identity": IDENTITY, "policy": POLICY,
        "final_affected_scope": {key: item for key, item in final.items() if key != "cases"},
        "distinct_current_scoped_tests": len({row["identity"] for row in final["cases"]}),
        "passed": final["passed"], "skipped": 0, "unresolved_failures": 0,
        "whole_repository_execution": False,
        "acceptance_statement": "The final affected scope passed in one execution. This is not an all-green whole-repository execution; all earlier failures and corrective receipts remain preserved.",
        "current_test_identities": [row["identity"] for row in final["cases"]],
        "receipts": [{key: item for key, item in row.items() if key != "cases"} for row in receipts],
        "tool_file_sha256": {"tools/doe/" + name: sha(PROJECT / "tools/doe" / name) for name in TOOLS},
        "lifecycle_file_sha256": {(ONLINE / name).relative_to(PROJECT).as_posix(): sha(ONLINE / name) for name in HELPERS},
        "historical_verification_files_checked": len(baseline["closed_verification_files"]),
        "historical_verification_files_changed": [],
        "model_calls": 0, "skill_executions": 0, "historical_replays": 0,
        "new_online_runs_started": 0,
        "limitations": ["Offline character savings do not establish online token or latency savings.",
            "Public event observation intervals are not provider generation time or first-token timing.",
            "The response codec is self-contained; it cannot reuse an omitted old IR or fill a new current IR.",
            "Retaining the original bundle after failed repair does not resolve its source-review findings."]}
    with (VERIFY / "offline-acceptance.json").open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": value["status"], "implementation_sha256": current["sha256"],
                      "tests": final["tests"], "passed": final["passed"]}))


if __name__ == "__main__":
    main()
