"""Seal the recorded offline checks; no target preparation or execution."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[2]
sys.path.insert(0, str(PROJECT))
from skillflow.common.recording import implementation_provenance


def read(name):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def main():
    # The two integrated runs began before four stale test expectations were
    # corrected. Their original failures remain; only exact corrective cases
    # below supersede their acceptance status.
    receipts = ["backend-integration.xml", "guided-integration.xml",
        "ga4-regressions/final-tests.xml", "independent-review-tests.xml",
        "independent-review-fixes.xml", "independent-review-013.xml",
        "cfg-correction.xml", "empty-guard.xml", "root-final-focused.xml",
        "inactive-observation.xml", "source-contract-recheck.xml",
        "review-failure-recheck.xml", "independent-review-final-observation.xml",
        "final-controller-observation.xml"]
    review = read("independent-review.json")
    retired = review["superseded_test_identity"]
    retired_id = (retired["classname"], retired["name"])
    cases, suites = {}, []
    for name in receipts:
        root = ET.parse(BASE / name).getroot()
        counts = {"passed": 0, "failed": 0, "skipped": 0}
        for node in root.iter("testcase"):
            status = "failed" if node.find("failure") is not None or node.find("error") is not None else "skipped" if node.find("skipped") is not None else "passed"
            counts[status] += 1
            key = (node.get("classname"), node.get("name"))
            if key != retired_id:
                cases[key] = {"status": status, "receipt": name}
        suites.append({"receipt": name, **counts,
            "seconds": sum(float(s.get("time", "0")) for s in root.iter("testsuite")),
            "sha256": hashlib.sha256((BASE / name).read_bytes()).hexdigest()})
    unresolved = [{"classname": k[0], "name": k[1], **v} for k, v in cases.items() if v["status"] == "failed"]
    assert not unresolved, unresolved
    current = implementation_provenance()
    assert current["sha256"] == read("candidate-implementation.json")["sha256"] == review["implementation_sha256"]
    assert all(f["status"] in ("resolved", "withdrawn") for f in review["findings"])
    for name, digest in review["reviewed_harness_sha256"].items():
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == digest, name
    assert not read("history-preservation.json")["mismatches"]
    result = {"status": "passed", "recorded_at": datetime.now(timezone.utc).isoformat(),
        "implementation_sha256": current["sha256"], "actual_model_starts": 0,
        "historical_replays": 0, "skill_executions": 0, "suites": suites,
        "distinct_cases": len(cases), "distinct_passed": sum(v["status"] == "passed" for v in cases.values()),
        "distinct_skipped": sum(v["status"] == "skipped" for v in cases.values()),
        "unresolved_failures": unresolved,
        "interpretation": "Scoped receipt union after exact corrective reruns; not one all-green whole-repository execution. Original failures and fixture corrections remain archived. Text-only agent receipts are additional evidence and are not counted in this XML union.",
        "superseded_test_identity": retired, "independent_review": "independent-review.json",
        "preserved_historical_evidence_files": 82,
        "fake_queue_scenarios_passed": review["standalone_fake_queue_scenarios_passed"],
        "scope": "Interface expressibility, propagation/save/DOE, input isolation, seven-call orchestration, one-replay behavior, and queue handoff. Actual model coverage, correctness, cost and speed are pending the authorized fresh batch."}
    with (BASE / "offline-acceptance.json").open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    state = read("continuation-state.json")
    state.update(phase="offline_accepted_not_prepared", updated_at=result["recorded_at"],
        root_test_sessions={}, offline_acceptance="offline-acceptance.json", model_starts=0)
    (BASE / "continuation-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "implementation_sha256", "distinct_cases", "distinct_passed", "distinct_skipped", "unresolved_failures")}))


if __name__ == "__main__":
    main()
