"""Read recorded Semia artifacts and write an as-of cohort summary only.

No analyzer, provider, historical SkillFlow, or replay is executed. Missing
measurements remain null/unknown; observed partial sums are explicitly marked.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "analysis"
CASES = {"001": BASE / "pilot/001", **{c: BASE / "comparison" / c for c in ("010", "013", "ga4")}}
TOKEN_KEYS = ("input_tokens", "output_tokens", "cached_input_tokens", "cache_write_input_tokens", "reasoning_output_tokens")
READ_ISSUES: list[dict] = []
CALL_SNAPSHOTS: dict[str, list] = {}


def ref(path: Path) -> str:
    return path.relative_to(BASE).as_posix() if path.is_relative_to(BASE) else str(path)


def fact(value, *paths: Path, status="observed", note=None):
    result = {"value": value, "status": status, "evidence": [ref(p) for p in paths]}
    if note:
        result["note"] = note
    return result


def read(path: Path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, ValueError) as exc:
        READ_ISSUES.append({"path": ref(path), "issue": f"{type(exc).__name__}: {exc}"})
        return None


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_of(request: dict, prompt: Path, artifacts: Path):
    if request.get("phase") in {"cgrs", "recommendation"}:
        return fact(request["phase"], prompt.parent / "request.json")
    if not prompt.is_file():
        return fact(None, prompt, status="unknown")
    rec = artifacts / "recommendation_prompt.md"
    if rec.is_file() and sha(rec) == sha(prompt):
        return fact("recommendation", prompt, rec, status="inferred_from_equal_prompt_hash")
    text = prompt.read_text("utf-8")
    if text.startswith("You are the Semia synthesize step."):
        return fact("cgrs", prompt, status="inferred_from_upstream_prompt_header")
    if text.startswith("# Semia Recommendation"):
        return fact("recommendation", prompt, status="inferred_from_upstream_prompt_header")
    return fact(None, prompt, status="unknown")


def calls_for(run: Path):
    calls = []
    for path in sorted((run / "transport").glob("call-*/request.json")):
        request = read(path)
        if not isinstance(request, dict):
            calls.append({"id": path.parent.name, "record": {}, "request_path": path,
                          "usage": None, "usage_path": path,
                          "phase": fact(None, path, status="unknown")})
            continue
        usage, usage_path = request.get("usage"), path
        if not isinstance(usage, dict) or not usage:
            usages = []
            stdout = path.parent / "stdout.jsonl"
            if stdout.is_file():
                for line in stdout.read_text("utf-8", errors="replace").splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue  # A live final line may still be incomplete.
                    if isinstance(event, dict) and event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                        usages.append(event["usage"])
            if usages:
                # Never manufacture zero for a field absent from a public turn.
                keys = set.intersection(*(set(u) for u in usages))
                usage = {k: sum(u[k] for u in usages) for k in keys
                         if all(isinstance(u[k], (int, float)) and not isinstance(u[k], bool) for u in usages)}
                usage_path = stdout
            else:
                usage = None
        if usage == {}:
            usage = None
        calls.append({"id": path.parent.name, "record": request, "request_path": path,
                      "usage": usage, "usage_path": usage_path,
                      "phase": phase_of(request, path.parent / "prompt.txt", run / "artifacts")})
    return calls


def aggregate_calls(calls, run: Path):
    request_paths = [c["request_path"] for c in calls] or [run / "transport"]
    started = [c for c in calls if c["record"].get("native_start") is True]
    unknown_start = [c for c in calls if not isinstance(c["record"].get("native_start"), bool)]
    tokens = {}
    for key in TOKEN_KEYS:
        available = [c for c in started if isinstance(c["usage"], dict) and isinstance(c["usage"].get(key), (int, float))]
        tokens[key] = {
            "known_sum": fact(sum(c["usage"][key] for c in available) if available else None,
                              *([c["usage_path"] for c in available] or request_paths), status="known_partial_sum" if available else "unknown"),
            "native_calls_missing_field": fact(len(started) - len(available), *request_paths),
        }
    complete_pairs = [c for c in started if isinstance(c["usage"], dict)
                      and all(isinstance(c["usage"].get(k), (int, float)) for k in ("input_tokens", "output_tokens"))]
    tokens["input_plus_output_tokens"] = fact(
        sum(c["usage"]["input_tokens"] + c["usage"]["output_tokens"] for c in complete_pairs) if complete_pairs else None,
        *([c["usage_path"] for c in complete_pairs] or request_paths), status="known_partial_sum" if complete_pairs else "unknown",
        note="Cached input and reasoning output are subcounts; do not add them again.")
    durations = [c for c in calls if isinstance(c["record"].get("elapsed_seconds"), (int, float))]
    return {
        "native_starts_observed": fact(len(started), *request_paths),
        "native_start_state_unknown": fact(len(unknown_start), *request_paths),
        "native_calls_without_usage": fact(sum(c["usage"] is None for c in started), *request_paths),
        "native_calls_without_exit_receipt": fact(sum(c["record"].get("returncode") is None for c in started), *request_paths),
        "native_nonzero_exits_observed": fact(sum(isinstance(c["record"].get("returncode"), int) and c["record"]["returncode"] != 0 for c in started), *request_paths),
        "completed_request_elapsed_sum_seconds": fact(round(sum(c["record"]["elapsed_seconds"] for c in durations), 3) if durations else None,
                                                       *([c["request_path"] for c in durations] or request_paths), status="known_partial_sum" if durations else "unknown"),
        "public_usage": tokens,
    }


def candidate_summary(case_id: str, run: Path):
    paths = sorted((run / "artifacts").glob("synthesis_attempt_*.dl"),
                   key=lambda p: tuple(map(int, re.findall(r"\d+", p.stem))))
    checks = defaultdict(list)
    for invocation in sorted((run / "validations").glob("check-*/invocation.json")):
        info = read(invocation)
        check_path = invocation.parent / "synthesis_check.json"
        check = read(check_path)
        if isinstance(info, dict) and info.get("returned") is True and isinstance(check, dict):
            checks[info.get("submitted_facts_sha256")].append((check, check_path, "original_per_check_receipt"))
    rows, grouped = [], {}
    for path in paths:
        digest = sha(path)
        candidates = checks.get(digest, [])
        if case_id == "001":
            audit_path = OUT / "001-audit" / (path.stem + ".json")
            audit = read(audit_path)
            if isinstance(audit, dict) and audit.get("sha256") == digest:
                candidates.append((audit, audit_path, "offline_recheck_bound_to_original_facts_hash"))
        check, evidence, basis = candidates[-1] if candidates else (None, path, "unknown")
        errors = check.get("errors") if isinstance(check, dict) else None
        if not isinstance(errors, list):
            errors = None
        rows.append({"candidate": ref(path), "sha256": fact(digest, path),
                     "program_valid": fact(check.get("program_valid") if check else None, evidence, status=basis),
                     "error_count": fact(len(errors) if errors is not None else None, evidence, status=basis)})
        for issue in errors or []:
            message = str(issue.get("message", ""))
            match = re.match(r"([A-Za-z_]\w*) expects\b", message)
            predicate = match.group(1) if match else None
            pattern = re.sub(r"'[^']*'", "'<id>'", message)
            key = (issue.get("code"), predicate, pattern)
            if key not in grouped:
                grouped[key] = {"code": issue.get("code"), "predicate": predicate, "message_pattern": pattern,
                                "count": 0, "evidence": [], "basis": []}
            item = grouped[key]
            item["count"] += 1
            if ref(evidence) not in item["evidence"]:
                item["evidence"].append(ref(evidence))
            if basis not in item["basis"]:
                item["basis"].append(basis)
    meta_path = run / "artifacts/synthesis_metadata.json"
    metadata = read(meta_path)
    iterations = metadata.get("iterations") if isinstance(metadata, dict) else None
    valid_rows = [r for r in rows if isinstance(r["program_valid"]["value"], bool)]
    return {
        "candidate_files_observed": fact(len(paths), *paths or [run / "artifacts"]),
        "candidates_with_validation": fact(len(valid_rows), *([Path(BASE / p) for r in valid_rows for p in r["program_valid"]["evidence"]] or paths or [run / "artifacts"])),
        "structurally_valid_candidates_known": fact(sum(r["program_valid"]["value"] is True for r in valid_rows) if valid_rows else None,
                                                    *([Path(BASE / p) for r in valid_rows for p in r["program_valid"]["evidence"]] or paths or [run / "artifacts"]), status="known_partial_count" if valid_rows else "unknown"),
        "candidates_without_validation": fact(len(paths) - len(valid_rows), *paths or [run / "artifacts"]),
        "accepted_iteration_records": fact(sum(x.get("accepted") is True for x in iterations) if isinstance(iterations, list) else None,
                                           meta_path, status="observed" if isinstance(iterations, list) else "unknown",
                                           note="Upstream iteration metadata is distinct from candidate structural validity; a live iteration may not yet be recorded."),
        "selected_iteration": fact(metadata.get("selected_iteration") if metadata else None, meta_path,
                                   status="observed" if metadata else "unknown"),
        "synthesis_completed": fact(metadata.get("completed") if metadata else None, meta_path,
                                    status="observed" if metadata else "unknown"),
        "synthesis_stop_reason": fact(metadata.get("stop_reason") if metadata else None, meta_path,
                                      status="observed" if metadata else "unknown"),
        "candidates": rows, "validation_error_groups_known": list(grouped.values()),
    }


def one_case(case_id: str, run: Path, inputs: dict):
    runtime_path, finished_path = run / "runtime.json", run / "finished.json"
    if not run.exists():
        return {"case_id": case_id, "state": fact("not_run", run, status="observed_absence"),
                "measurement": fact(None, run, status="not_run", note="No run directory; missing cost, coverage and findings are not zero or safe."),
                "expected_input_files": fact(len(inputs["files"]), BASE / "input-manifest.json")}
    runtime, terminal = read(runtime_path), read(finished_path)
    state = "completed" if terminal and terminal.get("exit_code") == 0 else "failed" if terminal else "in_progress"
    calls = calls_for(run)
    CALL_SNAPSHOTS[case_id] = calls
    result = {"case_id": case_id, "state": fact(state, runtime_path, finished_path,
              note="Receipt-based state; absence of a terminal receipt does not independently prove process liveness."),
              "accounting": aggregate_calls(calls, run),
              "phases": {p: aggregate_calls([c for c in calls if c["phase"]["value"] == p], run) for p in ("cgrs", "recommendation", None)},
              "calls": [{"id": c["id"], "phase": c["phase"],
                         "native_start": fact(c["record"].get("native_start"), c["request_path"], status="observed" if "native_start" in c["record"] else "unknown"),
                         "usage": fact(c["usage"], c["usage_path"], status="observed" if c["usage"] is not None else "unknown")}
                        for c in calls],
              "candidates": candidate_summary(case_id, run)}
    # JSON object keys cannot be null; retain an explicit unknown phase bucket.
    result["phases"]["unknown"] = result["phases"].pop(None)
    result["elapsed_seconds"] = fact(terminal.get("elapsed_seconds") if terminal else None, finished_path,
                                      status="observed" if terminal else "unknown_until_terminal")
    result["exit_code"] = fact(terminal.get("exit_code") if terminal else None, finished_path,
                              status="observed" if terminal else "unknown_until_terminal")
    runtime = runtime if isinstance(runtime, dict) else {}
    result["identity"] = {key: fact(runtime.get(key), runtime_path, status="observed" if key in runtime else "unknown")
                          for key in ("variant", "model", "reasoning_effort", "model_provider", "detector", "cli_executable", "cli_sha256",
                                      "input_manifest_sha256", "adapter_sha256", "source_commit", "source_manifest_sha256", "full_source_helper_sha256")}
    if "source_file_hashes" in runtime:
        result["identity"]["source_file_hashes"] = fact(runtime["source_file_hashes"], runtime_path)
        pin_path = BASE / "source-manifest.json"
        pins = read(pin_path)
        if isinstance(pins, dict) and runtime["source_file_hashes"] == {r["path"]: r["sha256"] for r in pins.get("files", [])}:
            result["identity"]["source_commit"] = fact(pins.get("commit"), runtime_path, pin_path,
                                                        status="inferred_from_equal_source_hash_inventory")
    for key in ("source_unchanged", "input_unchanged", "source_and_input_unchanged"):
        result["identity"][key] = fact(terminal.get(key) if terminal else None, finished_path,
                                      status="observed" if terminal and key in terminal else "unknown")
    artifact = run / "artifacts"
    prepare_path = artifact / "prepare_metadata.json"
    prepared = read(prepare_path)
    inventory = prepared.get("source", {}).get("file_inventory") if isinstance(prepared, dict) else None
    included = [r["path"] for r in inventory if r.get("disposition") in {"inlined", "inlined_source"}] if isinstance(inventory, list) else None
    complete_path = artifact / "complete-source-receipt.json"
    complete = read(complete_path)
    result["input_coverage"] = {
        "expected_files": fact(len(inputs["files"]), BASE / "input-manifest.json"),
        "prepared_files": fact(len(included) if included is not None else None, prepare_path,
                               status="observed" if included is not None else "unknown"),
        "prepared_file_paths": fact(included, prepare_path, status="observed" if included is not None else "unknown"),
        "complete_source_receipt": fact(complete, complete_path, status="observed" if complete else "not_available"),
        "native_calls_with_explicit_payload_check": fact(sum(c["record"].get("source_payload_verified") is True for c in calls),
                                                         *[c["request_path"] for c in calls] or [run / "transport"],
                                                         note="001 has no such explicit per-request field; zero here is absence of this receipt, not proof of missing source.")}
    detection_path = artifact / "detection_result.json"
    detection = read(detection_path)
    missing_stage = "not_run" if not calls else "not_produced" if terminal else "not_yet_observed"
    result["stages"] = {
        "detect": fact(detection.get("status") if isinstance(detection, dict) else missing_stage, detection_path,
                       status="observed" if detection else "artifact_absent"),
        "finding_count": fact(len(detection["findings"]) if isinstance(detection, dict) and isinstance(detection.get("findings"), list) else None,
                              detection_path, status="observed" if isinstance(detection, dict) and isinstance(detection.get("findings"), list) else "unknown"),
    }
    for stage, name in (("report", "report.md"), ("recommendation", "recommendation.md")):
        path = artifact / name
        result["stages"][stage] = fact("artifact_present" if path.is_file() else missing_stage, path,
                                       status="observed" if path.is_file() else "artifact_absent")
    result["accuracy"] = fact(None, BASE / "input-manifest.json", status="not_evaluated_no_independent_gold")
    return result


def display(metric):
    value = metric.get("value") if isinstance(metric, dict) else metric
    return "unknown" if value is None else str(value)


def main():
    READ_ISSUES.clear()
    CALL_SNAPSHOTS.clear()
    manifest = read(BASE / "input-manifest.json")
    inputs = {c["case_id"]: c for c in manifest["cases"]}
    cases = [one_case(case_id, run, inputs[case_id]) for case_id, run in CASES.items()]
    observed = datetime.now(timezone.utc)
    all_calls = [call for calls in CALL_SNAPSHOTS.values() for call in calls]
    local_observed = observed.astimezone(timezone(timedelta(hours=8)))
    result = {"schema": "semia-cohort-as-of-v1", "observed_at_utc": observed.isoformat(),
              "observed_at_shanghai": local_observed.isoformat(),
              "source_paths_relative_to": str(BASE), "snapshot_is_final": all(c["state"]["value"] in {"completed", "failed"} for c in cases),
              "known_cohort_accounting": aggregate_calls(all_calls, BASE) if CALL_SNAPSHOTS else fact(None, BASE, status="not_run"),
              "cases_not_run": fact(sum(c["state"]["value"] == "not_run" for c in cases), *CASES.values(), status="observed_absence"),
              "cases": cases, "read_issues": READ_ISSUES,
              "limits": ["Controlled, tool-disabled text-analysis variants; no target Skill executed by this summarizer.",
                         "Missing/unknown/not_run is not zero, negative, or safe. Known usage sums may omit unfinished or unpublished provider use.",
                         "Cached input and reasoning output are subsets and are not added to input+output totals.",
                         "Historical SkillFlow runs use different implementations/CLI provenance and remain reference-only; no same-version paired advantage or F1 is computed.",
                         "This summarizer reads receipts only and never resumes, replays, calls models, or invokes analyzers."]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cohort-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Semia 对照批次观察汇总", "", f"观察时点（Asia/Shanghai）：{local_observed.isoformat()}。本表是 as-of 快照；终态仅以各运行 finished.json 为依据。", "",
             "这些运行属于受控、禁用工具的文本分析变体。历史 SkillFlow 的实现和 CLI 身份不同，仅作背景参考。无独立金标，不报告 F1 或方法胜负。", "",
             "| case | 状态 | 已观察 native starts | 已知 input+output tokens | 未知 usage 调用 | 候选 / 有效已知 / 校验未知 | 接受的 iteration 记录 | prepared 文件 |", "|---|---|---:|---:|---:|---|---:|---|"]
    for case in cases:
        cid = case["case_id"]
        if "accounting" not in case:
            lines.append(f"| {cid} | not_run | — | — | — | — | — | — |")
            continue
        accounting, candidates, coverage = case["accounting"], case["candidates"], case["input_coverage"]
        lines.append(f"| {cid} | {display(case['state'])} | {display(accounting['native_starts_observed'])} | {display(accounting['public_usage']['input_plus_output_tokens'])} | {display(accounting['native_calls_without_usage'])} | {display(candidates['candidate_files_observed'])} / {display(candidates['structurally_valid_candidates_known'])} / {display(candidates['candidates_without_validation'])} | {display(candidates['accepted_iteration_records'])} | {display(coverage['prepared_files'])}/{display(coverage['expected_files'])} |")
    lines += ["", "`—` 表示尚未运行；unknown 表示未得到测量。已知 token 总数不是最终总成本，cached/reasoning 子计数不重复相加。候选结构通过、被迭代接受和安全结论是不同指标。", "",
              "逐字段证据路径、CGRS/recommendation 分阶段用量、候选校验错误按谓词归类、输入覆盖回执、检测/报告状态及版本身份见 [机器汇总](cohort-summary.json)。", ""]
    for case in cases:
        cid, run = case["case_id"], CASES[case["case_id"]]
        if not run.is_dir():
            lines.append(f"- {cid}：未启动，无运行目录。")
        elif (run / "finished.json").is_file():
            lines.append(f"- {cid}：[运行目录](../{ref(run)})；[完成回执](../{ref(run / 'finished.json')})。")
        else:
            lines.append(f"- {cid}：[运行目录](../{ref(run)})；终止回执尚未生成。")
        if "candidates" in case:
            groups = case["candidates"]["validation_error_groups_known"]
            for group in sorted(groups, key=lambda g: (-g["count"], str(g["code"])))[:8]:
                lines.append(f"  - 已知校验错误 {group['code']}：{group['message_pattern']}，出现 {group['count']} 次。")
    if READ_ISSUES:
        lines += ["", f"读取时遇到 {len(READ_ISSUES)} 项不完整/不可解析记录，已保留为未知，详见JSON。"]
    (OUT / "cohort-summary.zh.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"observed_at_utc": result["observed_at_utc"], "states": {c["case_id"]: c["state"]["value"] for c in cases},
                      "read_issues": len(READ_ISSUES), "output": str(OUT / "cohort-summary.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
