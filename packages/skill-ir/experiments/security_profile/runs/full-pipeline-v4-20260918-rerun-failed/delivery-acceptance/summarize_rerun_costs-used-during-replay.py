"""Offline, provenance-checked accounting of one explicitly authorized rerun.

This does not import an online client or inspect calls before the batch is fully
terminal. Reused calls retain their parent identity; fresh calls are distinct
even when prompt/response bytes happen to match an earlier call.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import os
from pathlib import Path, PurePosixPath
import re

HERE = Path(__file__).resolve()
_spec = importlib.util.spec_from_file_location("_cost_preparation", HERE.with_name("prepare_failed_case_rerun.py"))
_prepare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_prepare)
read_json, write_json = _prepare.read_json, _prepare.write_json
sha_file, canonical_sha256 = _prepare.sha_file, _prepare.canonical_sha256

IDENTITY = "skill-ir-rerun-lineage-costs-v1"
CASES = {f"{number:03}" for number in range(1, 31)}
CALL_PATH = re.compile(r"cases/(?P<case>\d{3})/(?:(?:feedback/calls/(?P<revision>r\d{3})/(?P<feedback_task>extraction|audit))|(?:annotation/calls/(?P<annotation_task>annotation)))/a\d{3}/call\.json")


class PendingRunError(ValueError):
    """No final accounting is permitted while a batch is still active."""


def terminal_material(directory):
    """Only root/case results are read here, never calls or transport files."""
    final = directory / "experiment-result.json"
    if not final.is_file():
        raise PendingRunError("pending：批次尚无最终 experiment-result.json；未读取调用记录")
    manifest, outcome = read_json(directory / "manifest.json"), read_json(final)
    for value in (manifest, outcome):
        if value.get("schema_version") != 4 or value.get("identity") != _prepare.PARENT_IDENTITY:
            raise ValueError("Unsupported pipeline identity")
    if ({row["case_id"] for row in manifest["cases"]} != CASES or len(manifest["cases"]) != 30
            or set(outcome["cases"]) != CASES):
        raise PendingRunError("pending：需要完整三十例终态，不读取调用记录")
    for identifier in sorted(CASES):
        path = directory / "cases" / identifier / "result.json"
        if not path.is_file():
            raise PendingRunError(f"pending：{identifier} 尚无终态")
        row = read_json(path)
        if row != outcome["cases"][identifier]:
            raise ValueError("Case result differs from final aggregate")
        feedback, annotation = row["feedback"]["status"], row["annotation"]["status"]
        if (feedback not in _prepare.FEEDBACK_ERRORS | {"audit_passed", "unresolved", "revision_limit"}
                or annotation not in _prepare.ANNOTATION_ERRORS | {"complete", "incomplete", "not_run"}):
            raise PendingRunError(f"pending：{identifier} 仍不是支持的终态")
        if annotation == "not_run" and (feedback not in _prepare.FEEDBACK_ERRORS or row.get("selection") is not None):
            raise PendingRunError(f"pending：{identifier} 的标注尚未完成")
    return manifest, outcome


def call_files(directory, cases):
    """Hash call artifacts only, excluding offline replay and runtime locks."""
    result = {}
    for identifier in sorted(cases):
        case = directory / "cases" / identifier
        _prepare.no_link(case)
        for current, directories, files in os.walk(case, followlinks=False):
            directories[:] = sorted(name for name in directories if name != "replay")
            for name in directories:
                _prepare.no_link(Path(current) / name)
            if "calls" not in Path(current).relative_to(case).parts:
                continue
            for name in sorted(files):
                if name == ".runner.lock":
                    continue
                path = Path(current) / name
                _prepare.no_link(path)
                result[path.relative_to(directory).as_posix()] = sha_file(path)
    return dict(sorted(result.items()))


def validated_ledger(directory, files):
    expected = set()
    for path in files:
        parts = PurePosixPath(path).parts
        if "calls" not in parts:
            continue
        if parts[-1] == "call.json":
            if CALL_PATH.fullmatch(path) is None:
                raise ValueError("Unrecognized execution call path")
            expected.add(path)
        if parts[-1] == "transport.json" and str(PurePosixPath(path).with_name("call.json")) not in files:
            raise ValueError("Orphan transport has no terminal call record; cost is not known zero")
    ledger = _prepare.call_ledger(directory, files)
    if {row["relative_path"] for row in ledger} != expected:
        raise ValueError("Recorded execution calls were omitted from the ledger")
    return ledger


def verify_lineage(directory, manifest):
    provenance = read_json(directory / "rerun-provenance.json")
    unsigned = {key: value for key, value in provenance.items() if key != "provenance_sha256"}
    if (provenance.get("schema_version") != 1 or provenance.get("identity") != _prepare.IDENTITY
            or provenance.get("provenance_sha256") != canonical_sha256(unsigned)):
        raise ValueError("Rerun provenance seal mismatch")
    child, recorded_parent = provenance["child_run"], provenance["parent_run"]
    parent = Path(recorded_parent["path"]).resolve()
    if (Path(child["path"]).resolve() != directory or child["run_id"] != directory.name
            or recorded_parent["run_id"] != parent.name or parent.name == directory.name):
        raise ValueError("Parent/child run identity mismatch")
    if recorded_parent["excluded_paths"] != ["**/replay/**", "**/.runner.lock"]:
        raise ValueError("Parent inventory exclusion policy changed")
    files = recorded_parent["files"]
    if canonical_sha256(files) != recorded_parent["files_sha256"] or _prepare.inventory(parent) != files:
        raise ValueError("Sealed parent inventory changed")
    if (files["manifest.json"] != recorded_parent["manifest_sha256"]
            or files["experiment-result.json"] != recorded_parent["experiment_result_sha256"]
            or sha_file(directory / "manifest.json") != files["manifest.json"]):
        raise ValueError("Parent/child manifest or result binding changed")
    parent_outcome = read_json(parent / "experiment-result.json")
    rerun, reuse = _prepare.classify_cases(manifest, parent_outcome)
    if (provenance["rerun_cases"] != rerun or provenance["reused_cases"] != reuse
            or provenance["parent_summary"] != parent_outcome["summary"]):
        raise ValueError("Rerun/reuse partition differs from sealed terminal results")
    copied = provenance["copied_files"]
    expected_copy = {path: digest for path, digest in files.items()
                     if path == "manifest.json" or any(path.startswith(f"cases/{case}/") for case in reuse)}
    if copied != expected_copy or canonical_sha256(copied) != provenance["copied_files_sha256"]:
        raise ValueError("Copied artifact seal mismatch")
    reused_calls = {path: digest for path, digest in copied.items() if "calls" in PurePosixPath(path).parts}
    if call_files(directory, reuse) != reused_calls:
        raise ValueError("Reused call artifacts changed, disappeared, or gained new calls")
    parent_ledger = validated_ledger(parent, files)
    if parent_ledger != provenance["parent_call_ledger"]:
        raise ValueError("Parent call ledger differs from sealed transport")
    expected_origins = {row["relative_path"]: row["origin_id"] for row in parent_ledger if row["case_id"] in reuse}
    if provenance["reused_call_origins"] != expected_origins:
        raise ValueError("Reused call origin binding changed")
    return provenance, parent, parent_ledger, call_files(directory, rerun)


def accounting_records(directory, ledger, requested_model):
    records = []
    for row in ledger:
        match = CALL_PATH.fullmatch(row["relative_path"])
        if match is None or match["case"] != row["case_id"]:
            raise ValueError("Unrecognized execution call path")
        task = match["feedback_task"] or match["annotation_task"]
        path = _prepare.safe_child(directory, row["relative_path"])
        trace = _prepare.validated_trace(path.with_name("transport.json"))[0]
        attempts = trace["http_attempts"]
        logical = (row["origin_id"] if task == "extraction" else
                   f"{directory.name}:cases/{row['case_id']}/{task}/{match['revision'] or 'annotation'}")
        records.append({**row, "task": task, "revision": match["revision"], "logical_id": logical,
            "requested_model": requested_model,
            "returned_model_at_call": trace.get("returned_model"),
            "usage_at_call_not_summed": trace.get("usage"),
            "attempts": [{"attempt": index, "status": attempt.get("status"),
                          "http_status": attempt.get("http_status"), "returned_model": attempt.get("returned_model"),
                          "usage": attempt.get("usage")} for index, attempt in enumerate(attempts, 1)]})
    return records


def metrics(records):
    attempts = [attempt for row in records for attempt in row["attempts"]]
    unobserved = [row["origin_id"] for row in records if not row["http_attempts_observed"]]
    aliases = {"input_tokens": ("input_tokens", "prompt_tokens"),
               "output_tokens": ("output_tokens", "completion_tokens"), "total_tokens": ("total_tokens",)}
    usage = {}
    for field, names in aliases.items():
        known = []
        for attempt in attempts:
            item = attempt.get("usage")
            if not isinstance(item, dict):
                continue
            value = next((item[name] for name in names if name in item), None)
            if type(value) is int and value >= 0:
                known.append(value)
        usage[field] = {"known_sum": sum(known) if known or not records else None,
                        "known_attempts": len(known), "unknown_attempts": len(attempts) - len(known),
                        "unobserved_calls": len(unobserved),
                        "complete": len(known) == len(attempts) and not unobserved}
    actual = Counter(attempt["returned_model"] for attempt in attempts if isinstance(attempt["returned_model"], str) and attempt["returned_model"])
    logical = {task: len({row["logical_id"] for row in records if row["task"] == task}) for task in ("extraction", "audit", "annotation")}
    return {"execution_calls": len(records), "execution_statuses": dict(Counter(row["status"] for row in records)),
            "logical_calls": sum(logical.values()), "logical_by_task": logical,
            "http_attempt_records": len(attempts), "http_attempts": len(attempts) if not unobserved else None,
            "http_retries_observed": sum(max(0, len(row["attempts"]) - 1) for row in records),
            "unobserved_http_call_origins": unobserved, "usage": usage,
            "requested_models_by_execution_call": dict(Counter(row["requested_model"] for row in records)),
            "returned_models_by_http_attempt": dict(actual), "unknown_returned_model_attempts": len(attempts) - sum(actual.values())}


def summarize(directory):
    directory = Path(directory).resolve()
    _prepare.no_link(directory)
    manifest, outcome = terminal_material(directory)  # Must precede any trace read.
    provenance, parent, parent_ledger, new_files = verify_lineage(directory, manifest)
    new_ledger = validated_ledger(directory, new_files)
    if any(row["case_id"] not in provenance["rerun_cases"] for row in new_ledger):
        raise ValueError("A reused case was counted as a new call")
    requested_model = manifest["config"].get("model")
    if not isinstance(requested_model, str) or not requested_model:
        raise ValueError("Requested model is not recorded in the sealed configuration")
    old = accounting_records(parent, parent_ledger, requested_model)
    new = accounting_records(directory, new_ledger, requested_model)
    records = old + new
    if len({row["origin_id"] for row in records}) != len(records):
        raise ValueError("Duplicate lineage execution origin")
    summary = {"schema_version": 1, "identity": IDENTITY, "status": "complete",
        "run_id": directory.name, "parent_run_id": parent.name,
        "rerun_provenance_sha256": provenance["provenance_sha256"],
        "parent_inventory_sha256": provenance["parent_run"]["files_sha256"],
        "parent_inventory_files": len(provenance["parent_run"]["files"]),
        "child_result_sha256": sha_file(directory / "experiment-result.json"),
        "child_call_files_sha256": canonical_sha256(new_files), "tool_sha256": sha_file(HERE),
        "preparation_helper_sha256": sha_file(HERE.with_name("prepare_failed_case_rerun.py")),
        "rerun_cases": provenance["rerun_cases"], "reused_cases": provenance["reused_cases"],
        "reused_execution_calls_excluded_from_child": len(provenance["reused_call_origins"]),
        "parent": metrics(old), "child_new": metrics(new), "lineage_unique": metrics(records),
        "final_batch_summary_not_added_to_costs": outcome["summary"], "calls": records,
        "boundaries": ["不同 run 的新调用即使文本相同也分别计数；复用调用只计父来源一次。",
            "每个来源 run 内，audit 按 case 与 revision 合并逻辑调用；执行重试与 HTTP 尝试另计。",
            "用量只累计实际 HTTP attempt 内的可观测整数；顶层用量保留但不重复相加，也不回填未知。",
            "缺失用量不是零成本；本表不是服务商账单，不估算金额。"]}
    summary["summary_sha256"] = canonical_sha256(summary)
    return summary


def report(summary):
    lines = ["# 重跑调用来源与成本记录", "", f"新运行：`{summary['run_id']}`；父运行：`{summary['parent_run_id']}`。", "",
             f"父运行 {summary['parent_inventory_files']} 个封印文件已核验；复用 {len(summary['reused_cases'])} 例、重新执行 {len(summary['rerun_cases'])} 例。",
             f"子运行复用的 {summary['reused_execution_calls_excluded_from_child']} 个执行调用不再计费式重复累计。", "",
             "| 来源 | 执行调用 | 逻辑调用 | HTTP 尝试 |", "| --- | ---: | ---: | ---: |"]
    for key, label in (("parent", "父运行全部"), ("child_new", "子运行新执行"), ("lineage_unique", "跨运行唯一总计")):
        value = summary[key]
        http = value["http_attempts"] if value["http_attempts"] is not None else f"未知（已记录 {value['http_attempt_records']}）"
        lines.append(f"| {label} | {value['execution_calls']} | {value['logical_calls']} | {http} |")
    lines += ["", "| 用量（跨运行） | 已观测合计 | 未知用量的 HTTP 尝试 | HTTP 次数未知的调用 |",
              "| --- | ---: | ---: | ---: |"]
    for field, value in summary["lineage_unique"]["usage"].items():
        lines.append(f"| {field} | {value['known_sum'] if value['known_sum'] is not None else '未知'} | {value['unknown_attempts']} | {value['unobserved_calls']} |")
    all_costs = summary["lineage_unique"]
    lines += ["", f"请求模型（按执行调用）：`{all_costs['requested_models_by_execution_call']}`。",
              f"实际返回模型（按 HTTP 尝试）：`{all_costs['returned_models_by_http_attempt']}`；未知 {all_costs['unknown_returned_model_attempts']} 次。", ""]
    lines += ["- " + item for item in summary["boundaries"]]
    lines += ["", "完整逐调用来源、摘要、模型及原始用量见同目录 `lineage-summary.json`。", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        summary = summarize(args.run_dir)
    except PendingRunError as error:
        print(str(error))
        return 2
    write_json(args.run_dir / "lineage-summary.json", summary)
    _prepare.atomic_write_text(args.run_dir / "lineage-report.md", report(summary))
    print(f"跨运行唯一调用 {summary['lineage_unique']['execution_calls']}；结果已写入 lineage-summary.json 与 lineage-report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
