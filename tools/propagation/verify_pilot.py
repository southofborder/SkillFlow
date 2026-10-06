"""Read-only verification of a pilot's saved results and protected-file baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


from skillflow.common.paths import project_root, resolve_material_path

PACKAGE = project_root()
REPOSITORY = project_root()

from skillflow.propagation.runner import load_propagation_run
from skillflow.common.recording import canonical_sha256


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory):
    baseline_path = directory / "verification/protected-before.json"
    baseline = read(baseline_path)
    changed = [relative for relative, digest in baseline.items()
               if not (REPOSITORY / relative).is_file() or sha(REPOSITORY / relative) != digest]
    rows, case_counts = [], {}
    manifest = read(directory / "manifest.json")
    if manifest.get("identity") != "skill-ir-source-boundaries-pilot3-v4" or manifest.get("schema_version") != 4:
        raise ValueError("unsupported propagation pilot version")
    for case in manifest["cases"]:
        base = directory / "cases" / case["case_id"]
        annotation = feedback = None
        try:
            stages, stages_replay = read(base / "result.json"), read(base / "replay/result.json")
            annotation, feedback = stages["annotation"], stages["feedback"]
            case_counts[case["case_id"]] = stages.get("counts")
            rows.append({"case": case["case_id"], "stage": "case", "status": feedback.get("status"),
                         "equal": stages == stages_replay,
                         "selection": stages.get("selection"), "source_binding": stages.get("source_binding")})
        except (OSError, ValueError, KeyError) as error:
            rows.append({"case": case["case_id"], "stage": "case", "status": "verification_error",
                         "equal": False, "reason": f"{type(error).__name__}: {error}"})
        for stage, result in (("feedback", feedback), ("annotation", annotation)):
            original, replay = base / stage / "result.json", base / stage / "replay/result.json"
            if result is not None and result.get("status") == "not_run" and not original.exists():
                rows.append({"case": case["case_id"], "stage": stage, "status": "not_run", "equal": None,
                             "reason": result.get("reason")})
                continue
            try:
                saved, repeated = read(original), read(replay)
                rows.append({"case": case["case_id"], "stage": stage, "status": saved.get("status"),
                             "reason": saved.get("reason"), "equal": saved == repeated and saved == result,
                             "result_sha256": sha(original), "replay_sha256": sha(replay)})
            except (OSError, ValueError, KeyError) as error:
                rows.append({"case": case["case_id"], "stage": stage, "status": "verification_error",
                             "equal": False, "reason": f"{type(error).__name__}: {error}"})
        propagation = base / "propagation"
        if not (propagation / "manifest.json").is_file():
            expected_skip = annotation is not None and annotation.get("status") in {
                "input_error", "invalid_response", "execution_error", "semantic_failure", "interrupted", "not_run"}
            uncommitted = propagation.exists() and any(propagation.iterdir())
            rows.append({"case": case["case_id"], "stage": "propagation",
                         "status": "uncommitted" if uncommitted else "not_run",
                         "equal": None if expected_skip and not uncommitted else False,
                         "reason": ("标注未产生可用规格，未生成 DOE 业务结果：" + str(annotation.get("reason"))
                                    if expected_skip else "没有已提交的传播运行，不能声称重放通过")})
            continue
        try:
            business = load_propagation_run(propagation)
            checked = read(propagation / "replay/summary.json")
            propagation_manifest = read(propagation / "manifest.json")
            rows.append({"case": case["case_id"], "stage": "propagation", "status": business["status"], "equal":
                         checked.get("status") == "matched" and checked.get("model_calls") == 0
                         and checked.get("differences") == []
                         and checked.get("doe_input_sha256") == propagation_manifest["doe_input_sha256"]
                         and checked.get("doe_input_sha256") == canonical_sha256(business),
                         "result_sha256": sha(propagation / "doe-input.json"), "replay_summary": checked})
        except (OSError, ValueError, KeyError) as error:
            rows.append({"case": case["case_id"], "stage": "propagation", "status": "verification_error",
                         "equal": False, "reason": f"{type(error).__name__}: {error}"})
    credential_pattern = re.compile(rb"sk-[A-Za-z0-9]{16,}")
    credential_files = [str(path.relative_to(directory)) for path in directory.rglob("*")
                        if path.is_file() and path.suffix in {".json", ".txt", ".md", ".html"}
                        and credential_pattern.search(path.read_bytes())]
    visual = {}
    for name in ["offline-demo", *[f"cases/{case['case_id']}/propagation" for case in manifest["cases"]]]:
        path = directory / name / "visual-review/checks.json"
        if not path.is_file():
            visual[name] = {"status": "not_performed", "reason": "没有独立视觉检查记录；不将未检查算作视觉通过。"}
        else:
            try:
                visual[name] = read(path)
            except (OSError, ValueError) as error:
                visual[name] = {"status": "verification_error", "reason": f"{type(error).__name__}: {error}"}
    summary = read(directory / "summary.json")
    planned = manifest["policy"]["planned_logical_calls"]
    def bounded(value, maximum):
        return type(value) is int and 0 <= value <= maximum
    def within_case(row):
        counts = row.get("call_counts", {})
        return (bounded(row.get("logical_calls"), 21)
                and counts == case_counts.get(row["case_id"])
                and bounded(counts.get("extraction_logical_calls"), 16)
                and bounded(counts.get("audit_logical_calls"), 4)
                and bounded(counts.get("annotation_logical_calls"), 1)
                and bounded(counts.get("audit_execution_calls"), 12)
                and bounded(counts.get("audit_execution_retries"), 8)
                and bounded(counts.get("total_execution_calls"), 29)
                and bounded(counts.get("semantic_revisions"), 3)
                and bounded(counts.get("structural_repairs"), 12)
                and row["logical_calls"] == counts["total_logical_calls"]
                == counts["extraction_logical_calls"] + counts["audit_logical_calls"] + counts["annotation_logical_calls"]
                and counts["total_execution_calls"] == counts["extraction_logical_calls"]
                + counts["audit_execution_calls"] + counts["annotation_logical_calls"])
    listed_cases = [row.get("case_id") for row in summary["cases"]]
    expected_cases = [row["case_id"] for row in manifest["cases"]]
    call_budget_ok = (listed_cases == expected_cases and planned == 63 and bounded(summary.get("logical_calls"), planned)
                      and all(within_case(row) for row in summary["cases"])
                      and summary["logical_calls"] == sum(row["logical_calls"] for row in summary["cases"]))
    guard_path = directory / "verification/network-guard.json"
    guard = read(guard_path) if guard_path.is_file() else {"status": "not_performed"}
    guard_ok = guard.get("status") == "passed" and guard.get("network_attempts") == 0
    http = [row.get("call_counts", {}).get("http_attempts") for row in summary["cases"]]
    return {
        "protected_file_count": len(baseline), "protected_manifest_sha256": sha(baseline_path),
        "changed_protected_files": changed, "replay_comparisons": rows,
        "credential_pattern_files": credential_files, "visual_checks": visual,
        "logical_calls": summary["logical_calls"],
        "planned_logical_calls": planned, "call_budget_ok": call_budget_ok,
        "http_attempts": sum(http) if all(type(value) is int for value in http) else None,
        "offline_network_guard": guard, "offline_network_guard_passed": guard_ok,
        "passed": (not changed and not credential_files and all(row["equal"] is not False for row in rows)
                   and all(check.get("status") in {"passed", "not_performed"} for check in visual.values())
                   and call_budget_ok and guard_ok),
    }


def main():
    parser = argparse.ArgumentParser(description="离线检查重放结果、保护文件与凭据模式；不调用 API")
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.run_dir.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
