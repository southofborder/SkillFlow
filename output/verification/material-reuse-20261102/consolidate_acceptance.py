"""Consolidate this offline acceptance's receipts; never execute analysis or tests."""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PHASE1 = ROOT / "output/verification/general-loops-v8-online-20261101/final-audit"
EXPECTED_ROOT = ("integration-tests.xml", "integration-runner-recheck.xml")
INITIAL = {"review-partial-mapping-test.xml"}
LEGACY_FIX = "tests/propagation/test_runner.py::test_annotation_changes_during_freezing_rejected_even_if_json_equal["


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def node_id(case):
    parts = case.get("classname", "").split(".")
    for end in range(len(parts), 0, -1):
        module = "/".join(parts[:end]) + ".py"
        if (ROOT / module).is_file():
            return "::".join([module, *parts[end:], case.get("name", "")])
    return case.get("classname", "") + "::" + case.get("name", "")


def tests():
    attempts, receipts, pending = defaultdict(list), [], []
    for name in EXPECTED_ROOT:
        if not (HERE / name).is_file():
            pending.append("Missing root receipt: " + name)
    for path in sorted(HERE.glob("*.xml")):
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as error:
            pending.append(f"Incomplete JUnit receipt {path.name}: {error}")
            continue
        phase = 0 if path.name in INITIAL else 3 if "recheck" in path.stem else 1
        suites = list(root.iter("testsuite"))
        timestamp = min((s.get("timestamp", "") for s in suites), default="")
        outcomes = Counter()
        for case in root.iter("testcase"):
            identity = node_id(case)
            issue = next((x for x in case if x.tag in ("failure", "error", "skipped")), None)
            outcome = "passed" if issue is None else "skipped" if issue.tag == "skipped" else "failed"
            outcomes[outcome] += 1
            case_phase = phase
            if path.name == "integration-tests.xml":
                # Only these six failures are already explained by the old
                # imported runner. Other integration failures need a recheck.
                case_phase = 0 if identity.startswith(LEGACY_FIX) else 2 if outcome == "failed" else 1
            attempts[identity].append({"receipt": path.name, "outcome": outcome,
                "logical_phase": case_phase, "suite_started_at_local": timestamp,
                "seconds": float(case.get("time", "0")),
                "message": None if issue is None else issue.get("message", issue.text)})
        receipts.append({"path": path.name, "sha256": sha(path),
            "logical_phase": phase, "suites": [s.attrib for s in suites], "outcomes": dict(outcomes)})

    # The earlier console-only DOE run passed all 78 cases. Its exact collected
    # identities permit a union with XML results; collection itself is no test run.
    doe = read(HERE / "doe-reuse-validation.json")
    collected = read(HERE / "doe-collected-nodeids.json")
    ids = collected["node_ids"]
    if len(set(ids)) != len(ids) or len(ids) != doe["tests"]["passed"] or doe["tests"]["failed"]:
        pending.append("DOE console receipt and collected node identities disagree")
    else:
        for identity in ids:
            attempts[identity].append({"receipt": "doe-reuse-validation.json", "outcome": "passed",
                "logical_phase": 1, "suite_started_at_local": "", "seconds": None,
                "message": "All-pass console receipt, identities from collect-only; per-test time unavailable"})
    receipts.append({"path": "doe-reuse-validation.json", "sha256": sha(HERE / "doe-reuse-validation.json"),
        "collection_receipt": "doe-collected-nodeids.json", "collection_sha256": sha(HERE / "doe-collected-nodeids.json"),
        "logical_phase": 1, "execution": doe["tests"]})

    guided = read(HERE / "guided-material-verification.json")
    fragment = read(HERE / "fragment-acceptance.json")
    initial = HERE / "guided-materials-focused-initial.txt"
    if initial.exists():
        for identity in re.findall(r"^FAILED (tests/\S+)", initial.read_text(encoding="utf-8"), re.MULTILINE):
            attempts[identity].append({"receipt": initial.name, "outcome": "failed", "logical_phase": 0,
                "suite_started_at_local": "", "seconds": None, "message": "Pre-fix legacy commit check; see preserved console receipt"})
        receipts.append({"path": initial.name, "sha256": sha(initial), "logical_phase": 0,
            "execution": guided["verification"][1], "counting": "Only named failures enter the node union; 102 unnamed passes are not added"})
    results, failures = {}, []
    for identity, history in sorted(attempts.items()):
        history.sort(key=lambda x: (x["logical_phase"], x["suite_started_at_local"], x["receipt"]))
        results[identity] = {"latest_outcome": history[-1]["outcome"], "latest_receipt": history[-1]["receipt"], "attempts": history}
        failures.extend({"node_id": identity, **x} for x in history if x["outcome"] == "failed")
    counts = Counter(row["latest_outcome"] for row in results.values())
    return {"unique_test_ids": len(results), "latest_outcomes": dict(counts), "receipts": receipts,
        "nodes": results, "preserved_identified_failures": failures,
        "development_history_without_complete_node_receipts": {
            "guided": guided["development_attempts_preserved"], "fragment": fragment["initial_new_test_run"],
            "scope": "Preserved as development provenance, not added to distinct passing test counts"},
        "ordering": "Explicit logical correction phase precedes timestamps; only six known legacy root failures inherit pre-fix rank; other root failures require a recheck receipt",
        "initial_integration_note": "Session 52928 imported the pre-fix runner; its outcomes and timings remain visible",
        "final_runner_note": "Session 88682 reruns the affected module against independently reviewed runner adb83f6808f99711662acf61974bb96f5f731802a95f60b79743a537a32d5484",
        "pending": pending}


def reviewed_files():
    rows = []
    for item in read(HERE / "independent-reviewed-files.json"):
        path = ROOT / item["path"]
        actual = sha(path) if path.exists() else None
        rows.append({**item, "current_sha256": actual, "matches_review": actual == item["reviewed_sha256"]})
    return {"expected_count": 9, "checked_count": len(rows), "mismatches": [r for r in rows if not r["matches_review"]], "files": rows}


def history_hashes():
    assertions = defaultdict(list)
    audit_receipts = []
    def record(value, run, report):
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and isinstance(value.get("sha256"), str):
                path = Path(value["path"])
                path = path if path.is_absolute() else run / path
                assertions[path.resolve().as_posix()].append({"report": report, "expected_sha256": value["sha256"]})
            for child in value.values():
                record(child, run, report)
        elif isinstance(value, list):
            for child in value:
                record(child, run, report)
    for path in sorted(PHASE1.glob("*.json")):
        value = read(path)
        run = Path(value.get("run", ROOT))
        record(value, run, path.name)
        if path.name == "ga4-doe.json":
            for relative, digest in value["evidence_hashes"].items():
                record({"path": relative, "sha256": digest}, run, path.name)
        audit_receipts.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)})
    checked = []
    for name, references in sorted(assertions.items()):
        path = Path(name)
        actual = sha(path) if path.is_file() else None
        checked.append({"path": name, "actual_sha256": actual, "references": references,
            "matches_all_assertions": all(r["expected_sha256"] == actual for r in references)})
    return {"scope": "Read-only bytes from all final-audit path+sha256 objects and GA4 DOE evidence_hashes; no loader, compiler or replay",
        "checked_unique_files": len(checked), "checked_hash_assertions": sum(len(x["references"]) for x in checked),
        "mismatches": [x for x in checked if not x["matches_all_assertions"]], "files": checked, "audit_receipts": audit_receipts}


def main():
    test_result, production, historical = tests(), reviewed_files(), history_hashes()
    unresolved = [key for key, value in test_result["nodes"].items() if value["latest_outcome"] == "failed"]
    blocked = bool(unresolved or production["mismatches"] or production["checked_count"] != 9 or historical["mismatches"])
    benchmarks = [{"path": p.name, "sha256": sha(p)} for p in sorted(HERE.glob("*-benchmark.json"))]
    result = {"identity": "skillflow-material-reuse-offline-acceptance", "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "blocked" if blocked else "pending" if test_result["pending"] else "passed",
        "new_model_calls": 0, "new_test_executions_by_consolidation": 0, "historical_analysis_or_replay_executions": 0,
        "tests": test_result, "unresolved_identified_failures": unresolved, "independently_reviewed_production": production,
        "historical_artifact_verification": historical, "benchmark_receipts": benchmarks,
        "caveats": ["Deduplicated tests come from multiple executions and corrective reruns, not one wholly green run.",
            "Receipt timing is preserved per execution; parallel timings are not summed into a wall-clock performance claim.",
            "Synthetic benchmarks do not establish GA4 speed, source accuracy, or greater propagation coverage.",
            "Historical hash verification covers exactly the listed files, not every artifact in the four runs."]}
    (HERE / "acceptance.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "unique_tests": test_result["unique_test_ids"],
        "latest_outcomes": test_result["latest_outcomes"], "unresolved_failures": len(unresolved),
        "reviewed_files": production["checked_count"], "production_mismatches": len(production["mismatches"]),
        "historical_files": historical["checked_unique_files"], "historical_assertions": historical["checked_hash_assertions"],
        "historical_mismatches": len(historical["mismatches"]), "pending": test_result["pending"]}, indent=2))


if __name__ == "__main__":
    main()
