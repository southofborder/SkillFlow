"""Publish a new comparison view after all 94 Semia recovery cases are terminal."""

import argparse
from collections import Counter
import json

from summarize import (
    COMPARISON, REPORTS, SAFE_ID, TERMINAL, case_record, count_metrics,
    hash_file, read_json, reference,
)


CLI_FAILURE = "LlmSynthesisError: Semia CLI request failed"
SETTINGS = ("variant", "model", "reasoning_effort", "provider")
MEASUREMENTS = {"strong-model": "potential_excess_count", "semia": "native_finding_count",
                "skillprivus": "violation_count"}


def check_reference(ref):
    path = (COMPARISON / ref["path"]).resolve(strict=True)
    if not path.is_relative_to(COMPARISON) or hash_file(path) != ref["sha256"]:
        raise ValueError(f"Archived artifact changed: {path}")
    return path


def work_totals(records):
    usage = Counter()
    starts = missing = 0
    for record in records:
        starts += record["native_starts"]
        missing += record["native_starts_without_usage"]
        usage.update(record.get("known_usage_by_field") or {})
    return {
        "native_starts": starts,
        "native_starts_without_usage": missing,
        "known_usage_by_field": dict(usage),
        "known_input_output_tokens": (usage["input_tokens"] + usage["output_tokens"]
                                      if {"input_tokens", "output_tokens"} <= usage.keys() else None),
    }


def terminal_check(summary, count):
    if (summary["status"] not in TERMINAL or summary["planned"] != count
            or summary["finished_cases"] != count or summary["not_run"] != 0
            or summary.get("pending_case_ids") or summary.get("claimed_unclosed_case_ids")):
        raise ValueError(f"Recovery requires all {count} terminal case records")


def verify_run_totals(cases, summary):
    work = work_totals(cases)
    if (any(work[key] != summary[key] for key in (
            "native_starts", "native_starts_without_usage", "known_usage_by_field"))
            or dict(Counter(case["status"] for case in cases)) != summary["case_status_counts"]):
        raise ValueError("Semia case records disagree with the terminal run summary")
    return work


def load_base(base_report, cohort_path):
    summary_path = base_report / "summary.json"
    results_path = base_report / "results.jsonl"
    summary = read_json(summary_path)
    if summary["cohort_sha256"] != hash_file(cohort_path):
        raise ValueError("Base audit uses a different cohort")
    cohort = read_json(cohort_path)["cases"]
    cohort_ids = {case["case_id"]: case["package_bytes_sha256"] for case in cohort}
    lines = results_path.read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in lines]
    archived_ids = {row["case_id"]: row["package_bytes_sha256"] for row in rows}
    if (len(cohort) != len(rows) or len(cohort_ids) != len(rows) or len(rows) != summary["case_count"]
            or archived_ids != cohort_ids):
        raise ValueError("Base report case inventory differs from the frozen cohort")
    for arm in summary["methods"].values():
        check_reference(arm["manifest"])
        check_reference(arm["summary"])
    affected = {}
    for row in rows:
        for arm in row["methods"].values():
            check_reference(arm["result"])
            for key in ("native_result", "request_binding"):
                if arm.get(key) is not None:
                    check_reference(arm[key])
        semia = row["methods"]["semia"]
        original = read_json(COMPARISON / semia["result"]["path"])
        if original.get("error") == CLI_FAILURE:
            if original["status"] != "failed" or original["detection_status"] != "not_run":
                raise ValueError(f"Unexpected state for CLI-affected case {row['case_id']}")
            affected[row["case_id"]] = row
    if len(affected) != 94 or len(rows) - len(affected) != 6:
        raise ValueError("Expected the 94 CLI-affected rows and six retained original rows")
    return summary, lines, rows, affected


def load_recovery(directory, base, affected):
    manifest_path = directory / "manifest.json"
    summary_path = directory / "summary.json"
    manifest = read_json(manifest_path)
    recovery = read_json(summary_path)
    parent = base["methods"]["semia"]
    parent_manifest = read_json(COMPARISON / parent["manifest"]["path"])
    bindings = {
        "cohort_sha256": base["cohort_sha256"], "method": "semia", "run_id": directory.name,
        "parent_run_id": parent["run_id"], "parent_manifest_sha256": parent["manifest"]["sha256"],
        "parent_summary_sha256": parent["summary"]["sha256"],
        "upstream_commit": parent_manifest["upstream_commit"],
        "native_runner_sha256": parent_manifest["runner_sha256"],
        **{key: parent[key] for key in SETTINGS},
    }
    for key, expected in bindings.items():
        if manifest.get(key) != expected:
            raise ValueError(f"Recovery manifest differs from prescribed binding {key}")
    selection = manifest["cases"]
    if len(selection) != len(affected) or {case["case_id"] for case in selection} != set(affected):
        raise ValueError("Recovery selection differs from the 94 CLI-affected original cases")
    for case in selection:
        original_row = affected[case["case_id"]]
        original_result = original_row["methods"]["semia"]["result"]
        if (case["package_bytes_sha256"] != original_row["package_bytes_sha256"]
                or case["parent_result_sha256"] != original_result["sha256"]
                or case["parent_result"] != original_result):
            raise ValueError(f"Recovery case is unbound to its original result: {case['case_id']}")
    terminal_check(recovery, len(affected))
    summary_cases = {case["case_id"]: case for case in recovery["cases"]}
    if len(recovery["cases"]) != len(affected) or summary_cases.keys() != affected.keys():
        raise ValueError("Recovery summary does not enumerate all selected cases")
    results = {}
    for case in selection:
        case_id = case["case_id"]
        content = read_json(directory / "cases" / case_id / "result.json")
        if content != summary_cases[case_id]:
            raise ValueError(f"Recovery case differs from its terminal summary: {case_id}")
        if content["status"] not in {"completed", "partial", "failed"}:
            raise ValueError(f"Unexpected terminal recovery status: {case_id}")
        results[case_id] = case_record("semia", directory, case)
    measured = verify_run_totals(results.values(), recovery)
    return manifest, recovery, results, measured


def merge(base_report, recovery_dir, cohort_path):
    base, original_lines, rows, affected = load_base(base_report, cohort_path)
    manifest, recovery, measured, new_work = load_recovery(recovery_dir, base, affected)
    parent = base["methods"]["semia"]
    original = [row["methods"]["semia"] for row in rows]
    old_work = verify_run_totals(original, read_json(COMPARISON / parent["summary"]["path"]))
    superseded = work_totals(row["methods"]["semia"] for row in affected.values())

    selected, lines, matched_cases = [], [], []
    for line, row in zip(original_lines, rows, strict=True):
        case_id = row["case_id"]
        methods = row["methods"]
        if case_id in measured:
            recovered = {**measured[case_id], "superseded_original_result": methods["semia"]["result"]}
            methods = {**methods, "semia": recovered}
            line = (json.dumps({**row, "methods": methods}) + "\n").encode("utf-8")
        selected.append(methods["semia"])
        lines.append(line)
        if all(type(methods[method]["native_metrics"][key]) is int for method, key in MEASUREMENTS.items()):
            matched_cases.append(case_id)

    selected_work = work_totals(selected)
    cumulative = work_totals([old_work, new_work])
    if work_totals([selected_work, superseded]) != cumulative:
        raise ValueError("Selected and superseded accounting do not reconcile with total native work")
    parent_run = {"run_id": parent["run_id"], "manifest": parent["manifest"], "summary": parent["summary"],
                  "measured_case_count": len(rows), "workers": parent["workers"], "work": old_work,
                  "elapsed_seconds": parent["elapsed_seconds"]}
    recovery_run = {"run_id": manifest["run_id"], "manifest": reference(recovery_dir / "manifest.json"),
                    "summary": reference(recovery_dir / "summary.json"), "measured_case_count": len(measured),
                    "workers": manifest["workers"], "work": new_work, "elapsed_seconds": recovery["elapsed_seconds"],
                    "duration_scope": "controller_reported_elapsed_including_prior_active_segments"}
    semia = {
        **{key: parent[key] for key in SETTINGS},
        **selected_work,
        "outcome_basis": "94_recovery_case_results_and_6_unchanged_original_case_results",
        "status_counts": dict(Counter(case["status"] for case in selected)),
        "native_metrics": count_metrics(selected, ("native_finding_count", "validation_count"),
                                        ("synthesis_status", "detection_status")),
        "run_wall_seconds": None,
        "parent_run": parent_run, "recovery_run": recovery_run,
        "superseded_original_work": superseded, "cumulative_measured_work": cumulative,
    }
    methods = {**base["methods"], "semia": semia}
    report = {
        **base, "methods": methods, "cases_with_three_native_measurements": len(matched_cases),
        "case_ids_with_three_native_measurements": matched_cases,
        "base_report": {"summary": reference(base_report / "summary.json"),
                        "results": reference(base_report / "results.jsonl")},
        "recovered_case_count": len(measured), "retained_original_semia_case_count": len(rows) - len(measured),
        "all_arms_cumulative_measured_work": work_totals([methods["strong-model"], methods["skillprivus"], cumulative]),
    }
    return report, b"".join(lines)


def markdown(report):
    def tokens(work):
        value = work["known_input_output_tokens"]
        return f"{value:,}" if value is not None else "Unavailable"

    methods = report["methods"]
    semia = methods["semia"]
    text = ["# ClawHub privacy audit comparison after Semia recovery", "",
            f"The three methods share {report['case_count']} versioned packages and {report['source_file_count']:,} files. "
            "The Semia outcome view uses 94 recovery results and six unchanged original results.", "",
            "| Method | Completed | Partial | Failed | Starts in selected results | Starts without usage | Known input + output tokens |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for method, arm in methods.items():
        status = arm["status_counts"]
        text.append(f"| {method} | {status.get('completed', 0)} | {status.get('partial', 0)} | "
                    f"{status.get('failed', 0)} | {arm['native_starts']:,} | "
                    f"{arm['native_starts_without_usage']:,} | {tokens(arm)} |")
    skillprivus = methods["skillprivus"]["native_status_counts"]
    text.extend(["", f"The controlled paper-based SkillPrivus arm recorded {skillprivus.get('analyzed', 0)} "
                 f"fully analyzed cases and {skillprivus.get('screened_out', 0)} screened-out cases in its completed total.",
                 "The Semia recovery bounded CLI connection retries for its own native requests. It retained the "
                 "original model and prompt material, synthesis settings, request deadline and built-in detector.",
                 "", "## Semia measured work", "",
                 "| Scope | Starts | Starts without usage | Known input + output tokens | Reported elapsed hours |",
                 "| --- | ---: | ---: | ---: | ---: |"])
    for label, work, seconds in (
        ("Original 100 cases", semia["parent_run"]["work"], semia["parent_run"]["elapsed_seconds"]),
        ("Recovery 94 cases", semia["recovery_run"]["work"], semia["recovery_run"]["elapsed_seconds"]),
        ("Superseded original attempts for the 94 cases", semia["superseded_original_work"], None),
        ("Cumulative original and recovery work", semia["cumulative_measured_work"], None),
    ):
        hours = "Unavailable" if seconds is None else f"{seconds / 3600:.2f}"
        text.append(f"| {label} | {work['native_starts']:,} | {work['native_starts_without_usage']:,} | {tokens(work)} | {hours} |")
    text.extend(["", "The cumulative total is original measured work plus recovery measured work. "
                 "The recovery duration uses the controller's elapsed time, which accumulates active segments after a resume. "
                 "The selected-result view combines cases from both runs and has no single observed wall duration.", "",
                 "## Native outputs", "",
                 "| Method | Native measurement | Cases with a recorded count | Cases with at least one | Recorded total |",
                 "| --- | --- | ---: | ---: | ---: |"])
    for method, arm in methods.items():
        for name, metric in arm["native_metrics"].items():
            if "available_cases" in metric:
                total = "Unavailable" if metric["total"] is None else f"{metric['total']:,}"
                text.append(f"| {method} | {name.replace('_', ' ')} | {metric['available_cases']} | "
                            f"{metric['positive_cases']} | {total} |")
    text.extend(["", f"All three methods produced native measurements for {report['cases_with_three_native_measurements']} shared cases. "
                 "Direct excess claims, Semia findings and SkillPrivus contextual-integrity violations have different definitions. "
                 "Accuracy, precision, recall and F1 remain unevaluated without independent labels.", "",
                 "[Summary data](summary.json) · [Case records](results.jsonl)", ""])
    return "\n".join(text)


def report_files(report, rows):
    return {
        "results.jsonl": rows,
        "summary.json": (json.dumps(report, indent=2) + "\n").encode("utf-8"),
        "summary.md": markdown(report).encode("utf-8"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-report", default="audit-01")
    parser.add_argument("--recovery-run", default="semia-recovery-01")
    parser.add_argument("--report-id", default="audit-02")
    args = parser.parse_args()
    if any(not SAFE_ID.fullmatch(value) for value in (args.base_report, args.recovery_run, args.report_id)):
        parser.error("Use lowercase, hyphenated IDs.")
    target = REPORTS / args.report_id
    if target.exists():
        parser.error(f"Report already exists: {target}")
    report, rows = merge(REPORTS / args.base_report, COMPARISON / "runs" / "semia" / args.recovery_run,
                         COMPARISON / read_json(COMPARISON / "study.json")["inputs"])
    staging = REPORTS / f".{args.report_id}.tmp"
    staging.mkdir(exist_ok=False)
    for name, content in report_files(report, rows).items():
        (staging / name).write_bytes(content)
    staging.rename(target)
    print(f"Published {target}")


if __name__ == "__main__":
    main()
