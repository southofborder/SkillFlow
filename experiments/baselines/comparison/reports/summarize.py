"""Join the three comparison arms by source package and report run coverage."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
from statistics import median
import time


REPORTS = Path(__file__).resolve().parent
COMPARISON = REPORTS.parent
METHODS = ("strong-model", "semia", "skillprivus")
SAFE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)+")
TERMINAL = {"completed", "partial"}


def read_json(path):
    return json.loads(path.read_bytes())


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(path):
    return {"path": path.relative_to(COMPARISON).as_posix(), "sha256": hash_file(path)}


def run_definition(method, run_id, cohort_sha256):
    directory = COMPARISON / "runs" / method / run_id
    manifest_path = directory / "manifest.json"
    manifest = read_json(manifest_path)
    if manifest["cohort_sha256"] != cohort_sha256:
        raise ValueError(f"Different cohort for {method}: {run_id}")
    if manifest["method"] != method or manifest["run_id"] != run_id:
        raise ValueError(f"Method mismatch in {manifest_path}")
    return directory, {
        "run_id": run_id,
        "manifest": reference(manifest_path),
        "variant": manifest.get("variant"),
        "model": manifest.get("model"),
        "reasoning_effort": manifest.get("reasoning_effort"),
        "provider": manifest.get("provider"),
        "workers": manifest.get("workers"),
        "cli_sha256": manifest.get("cli_sha256"),
        "controller_pid": manifest["controller_pid"],
    }


def controller_alive(pid):
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = kernel.OpenProcess(0x00100000, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error == 87:  # ERROR_INVALID_PARAMETER for a vanished PID.
            return False
        raise OSError(error, f"Cannot inspect run controller {pid}")
    try:
        wait = kernel.WaitForSingleObject(handle, 0)
        if wait not in (0, 258):
            raise OSError(ctypes.get_last_error(), f"Cannot check run controller {pid}")
        return wait == 258
    finally:
        kernel.CloseHandle(handle)


def terminal_summaries(runs, planned, wait):
    previous = None
    while True:
        summaries = []
        for directory, definition in runs.values():
            path = directory / "summary.json"
            summary = read_json(path)
            if wait and summary["status"] == "running" and not controller_alive(definition["controller_pid"]):
                summary = read_json(path)
                if summary["status"] == "running":
                    raise ValueError(f"Controller exited before writing a terminal summary: {path}")
            status = summary["status"]
            if summary["planned"] != planned or status not in TERMINAL | {"running"}:
                raise ValueError(f"Run requires attention: {path} ({status})")
            if status in TERMINAL and (summary["finished_cases"] != planned or summary["not_run"] != 0):
                raise ValueError(f"Terminal run lacks all case records: {path}")
            summaries.append(summary)
        if all(summary["status"] in TERMINAL for summary in summaries):
            return dict(zip(runs, summaries, strict=True))
        progress = {method: summary["finished_cases"] for method, summary in zip(runs, summaries, strict=True)}
        if not wait:
            raise ValueError(f"Runs are still in progress: {progress}")
        if progress != previous:
            print(json.dumps({"status": "waiting", "finished_cases": progress}), flush=True)
            previous = progress
        time.sleep(30)


def validated_screening(folder):
    path = folder / "records/screening.json"
    if not path.is_file():
        return None, None
    record = read_json(path)
    if (hash_file(folder / "requests/screening.json") != record["request_sha256"]
            or hash_file(folder / "raw/screening.json") != record["answer_sha256"]):
        raise ValueError(f"SkillPrivus screening evidence differs: {path}")
    return record["result"]["status"], reference(path)


def case_record(method, directory, case):
    folder = directory / "cases" / case["case_id"]
    path = folder / "result.json"
    result = read_json(path)
    if result["case_id"] != case["case_id"]:
        raise ValueError(f"Case mismatch: {path}")
    package = result.get("package_bytes_sha256")
    binding = None
    if method == "strong-model":
        receipt_path = folder / "requests/request.json"
        receipt = read_json(receipt_path)
        if receipt["case_id"] != case["case_id"] or result["request"] != "requests/request.json":
            raise ValueError(f"Request receipt does not belong to case: {path}")
        package = receipt["package_bytes_sha256"]
        binding = reference(receipt_path)
    if package != case["package_bytes_sha256"]:
        raise ValueError(f"Package mismatch: {path}")
    calls = result.get("native_starts")
    usage = result.get("known_usage_by_field", result.get("usage"))
    if calls is None and type(result.get("native_start")) is bool:
        calls = int(result["native_start"])
    missing_usage = result.get("native_starts_without_usage", result.get("starts_without_usage"))
    if method == "strong-model":
        missing_usage = int(result["native_start"] and usage is None)
        metrics = {key: result.get(key) for key in ("operation_count", "potential_excess_count", "unknown_count")}
        metrics["rejected_evidence_count"] = len(result["rejected_evidence"]) if "rejected_evidence" in result else None
        native_result = reference(folder / result["raw_output"]) if "raw_output" in result else None
    elif method == "semia":
        metrics = {key: result.get(key) for key in
                   ("synthesis_status", "detection_status", "native_finding_count", "validation_count")}
        native_result = reference(folder / result["native_detection"]) if "native_detection" in result else None
    else:
        semantic_path = folder / "method-result.json"
        details = read_json(semantic_path) if result.get("method_result") == "method-result.json" else {}
        screening, binding = validated_screening(folder)
        if details and (details["case_id"] != case["case_id"] or details["package_bytes_sha256"] != package
                        or details["status"] != result["status"] or details["native_status"] != result["native_status"]
                        or details["screening"] != screening):
            raise ValueError(f"SkillPrivus semantic result mismatch: {semantic_path}")
        metrics = {key: details.get(key) for key in ("move_count", "violation_count", "incomplete_judgments")}
        metrics["screening"] = screening
        native_result = reference(semantic_path) if details else None
    return {
        "status": result["status"],
        "native_status": result.get("native_status"),
        "failure": result.get("failure"),
        "failed_stage": result.get("failed_stage"),
        "native_starts": calls,
        "native_starts_without_usage": missing_usage,
        "elapsed_seconds": result.get("elapsed_seconds"),
        "known_usage_by_field": usage,
        "native_metrics": metrics,
        "result": reference(path),
        "native_result": native_result,
        "request_binding": binding,
    }


def count_metrics(cases, numeric, categories):
    counts = {}
    for name in numeric:
        values = [row["native_metrics"][name] for row in cases if type(row["native_metrics"][name]) is int]
        counts[name] = {"available_cases": len(values), "positive_cases": sum(value > 0 for value in values),
                        "total": sum(values) if values else None}
    for name in categories:
        counts[name] = dict(Counter(row["native_metrics"][name] or "unavailable" for row in cases))
    return counts


def arm_totals(rows, method, definition, run_summary, summary_path):
    cases = [row["methods"][method] for row in rows]
    usage = Counter()
    for case in cases:
        for key, value in (case.get("known_usage_by_field") or {}).items():
            if type(value) is int:
                usage[key] += value
    starts = sum(case["native_starts"] for case in cases)
    missing_usage = sum(case["native_starts_without_usage"] for case in cases)
    statuses = dict(Counter(case["status"] for case in cases))
    if (starts != run_summary["native_starts"] or missing_usage != run_summary["native_starts_without_usage"]
            or statuses != run_summary["case_status_counts"] or dict(usage) != run_summary["known_usage_by_field"]):
        raise ValueError(f"Case records disagree with terminal run summary: {summary_path}")
    metrics = {
        "strong-model": (("operation_count", "potential_excess_count", "unknown_count", "rejected_evidence_count"), ()),
        "semia": (("native_finding_count", "validation_count"), ("synthesis_status", "detection_status")),
        "skillprivus": (("move_count", "violation_count", "incomplete_judgments"), ("screening",)),
    }
    return {
        **definition,
        "summary": reference(summary_path),
        "status_counts": statuses,
        "native_status_counts": dict(Counter(case["native_status"] for case in cases if case["native_status"])),
        "failed_stage_counts": dict(Counter(case["failed_stage"] for case in cases if case["failed_stage"])),
        "native_starts": starts,
        "native_starts_without_usage": missing_usage,
        "known_usage_by_field": dict(usage),
        "known_input_output_tokens": (usage["input_tokens"] + usage["output_tokens"]
                                      if {"input_tokens", "output_tokens"} <= usage.keys() else None),
        "elapsed_seconds": run_summary["elapsed_seconds"],
        "median_case_seconds": median(case["elapsed_seconds"] for case in cases),
        "native_metrics": count_metrics(cases, *metrics[method]),
    }


def markdown(summary):
    lines = [
        "# ClawHub privacy audit comparison", "",
        f"The three runs started from the same {summary['case_count']} versioned source packages "
        f"and {summary['source_file_count']:,} files.", "",
        "| Method | Requested model / effort | Workers | Completed | Partial | Failed | Model starts | Starts without usage | Known input + output tokens | Wall hours |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for method, arm in summary["methods"].items():
        counts = arm["status_counts"]
        tokens = f"{arm['known_input_output_tokens']:,}" if arm["known_input_output_tokens"] is not None else "Unavailable"
        lines.append(f"| {method} | {arm['model']} / {arm['reasoning_effort']} | {arm['workers']} | "
                     f"{counts.get('completed', 0)} | {counts.get('partial', 0)} | "
                     f"{counts.get('failed', 0)} | {arm['native_starts']:,} | "
                     f"{arm['native_starts_without_usage']:,} | {tokens} | {arm['elapsed_seconds'] / 3600:.2f} |")
    lines.extend(["", "## Native outputs", "",
                  "| Method | Native measurement | Cases with output | Cases with at least one | Recorded total |",
                  "| --- | --- | ---: | ---: | ---: |"])
    for method, arm in summary["methods"].items():
        for key, metric in arm["native_metrics"].items():
            if "available_cases" in metric:
                total = f"{metric['total']:,}" if metric["total"] is not None else "Unavailable"
                lines.append(f"| {method} | {key.replace('_', ' ')} | {metric['available_cases']} | "
                             f"{metric['positive_cases']} | {total} |")
    skillprivus = summary["methods"]["skillprivus"]["native_status_counts"]
    semia = summary["methods"]["semia"]["native_metrics"]["detection_status"]
    lines.extend(["", f"SkillPrivus screened out {skillprivus.get('screened_out', 0)} cases, counted in its completed status. "
                  f"Semia left detection unrun in {semia.get('not_run', 0)} cases. "
                  f"All three reported their native finding or claim count for {summary['cases_with_three_native_measurements']} cases.",
                  "", "## Interpretation", "",
                  "- The direct baseline used one request per case. Its counts retain claims whose source path and line range passed structural checks.",
                  "- Semia used pinned upstream synthesis and the built-in detector. The complete-text renderer applied upstream normalization. The optional recommendation stage was outside this run.",
                  "- SkillPrivus used the controlled paper-based reimplementation. Screening, evidence checks and contextual-integrity judgments have separate outcomes.",
                  "- Direct excess claims, Semia detector findings and SkillPrivus contextual-integrity violations have different definitions. Accuracy, precision, recall and F1 were not evaluated because this cohort has no independent labels. Worker counts and model-call budgets affect wall hours.",
                  "- Cached input tokens are part of input tokens. Reasoning output tokens are part of output tokens.",
                  "", "[Summary data](summary.json) · [Case records and native artifact references](results.jsonl)", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for method in METHODS:
        parser.add_argument("--" + method, required=True, metavar="RUN_ID")
    parser.add_argument("--report-id", required=True)
    parser.add_argument("--wait", action="store_true", help="wait for all three runs to reach a terminal state")
    args = parser.parse_args()
    run_ids = {method: getattr(args, method.replace("-", "_")) for method in METHODS}
    if any(not SAFE_ID.fullmatch(value) for value in (args.report_id, *run_ids.values())):
        parser.error("Use lowercase, hyphenated run and report IDs.")
    study = read_json(COMPARISON / "study.json")
    cohort_path = COMPARISON / study["inputs"]
    cohort_sha256 = hash_file(cohort_path)
    definitions = {method: run_definition(method, run_ids[method], cohort_sha256) for method in METHODS}
    report = REPORTS / args.report_id
    if report.exists():
        parser.error(f"Report already exists: {report}")
    cases = read_json(cohort_path)["cases"]
    terminal = terminal_summaries(definitions, len(cases), args.wait)
    rows = []
    for case in cases:
        rows.append({
            "case_id": case["case_id"],
            "package_bytes_sha256": case["package_bytes_sha256"],
            "methods": {method: case_record(method, definitions[method][0], case) for method in METHODS},
        })
    summary = {
        "cohort_sha256": cohort_sha256,
        "case_count": len(rows),
        "source_file_count": sum(case["file_count"] for case in cases),
        "cases_with_three_native_measurements": sum(
            all(row["methods"][method]["native_metrics"][metric] is not None for method, metric in (
                ("strong-model", "potential_excess_count"), ("semia", "native_finding_count"), ("skillprivus", "violation_count")
            )) for row in rows
        ),
        "methods": {method: arm_totals(rows, method, definitions[method][1], terminal[method],
                                       definitions[method][0] / "summary.json") for method in METHODS},
        "precision_recall_f1": "not_evaluated",
    }
    staging = REPORTS / f".{args.report_id}.tmp"
    staging.mkdir(exist_ok=False)
    (staging / "results.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    (staging / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (staging / "summary.md").write_text(markdown(summary), encoding="utf-8")
    staging.rename(report)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
