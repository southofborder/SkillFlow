"""F01 experiment scheduling only; generic feedback never imports this file."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import threading

from skill_ir.backtrace.fixtures import REPOSITORY_ROOT, canonical_sha256, prepare_cases
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.feedback.report import STATUS_LABELS, audit_findings, finding_summary
from skill_ir.semantic_contract import contract_binding


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "skill-ir-semantic-feedback-f01-v5"
CASE_LABELS = {
    "c01": "F01 原图",
    "c02": "archive 增加密钥输入",
    "c03": "删除失败出口状态追加",
    "c04": "重试成功返回首次结果",
    "c05": "增加明确两秒等待",
}


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _verified_manifest(directory, config, writer):
    prepared = prepare_cases()
    expected = {
        "schema_version": 5,
        "identity": IDENTITY,
        **contract_binding(),
        "driver": {"path": Path(__file__).resolve().relative_to(REPOSITORY_ROOT).as_posix(),
                   "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        "source_provenance": prepared["provenance"],
        "source_sha256": prepared["source"]["source_sha256"],
        "config": config,
        "limits": {"max_semantic_revisions": 3, "max_structural_repairs": 3,
                   "max_logical_calls_per_case": 16, "max_logical_calls_total": 80},
        "cases": [{"case_id": case["case_id"], "graph_sha256": case["graph_sha256"],
                   "initial_analysis": f"inputs/{case['case_id']}-analysis.json",
                   "run_dir": f"cases/{case['case_id']}"} for case in prepared["cases"]],
        "evaluation_policy": "Oracle read only after model execution; old graph pointers never establish repair of a regenerated graph.",
    }
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        saved = _read(manifest_path)
        if saved.get("schema_version") != 5 or saved.get("identity") != IDENTITY:
            raise ValueError("Unsupported semantic feedback experiment version")
        if saved != expected:
            raise ValueError("F01 experiment manifest/input/config identity mismatch")
        for case in prepared["cases"]:
            seed = _read(directory / "inputs" / f"{case['case_id']}-analysis.json")
            if set(seed) != {"cfg"} or canonical_sha256(seed["cfg"]) != case["graph_sha256"]:
                raise ValueError("F01 actual variant seed changed")
    else:
        # The lock is the only file allowed before a fresh manifest is installed.
        unexpected = [path for path in directory.iterdir() if path.name != ".runner.lock"]
        if unexpected:
            raise ValueError("F01 run directory is non-empty and lacks a supported manifest")
        for case in prepared["cases"]:
            writer.json(directory / "inputs" / f"{case['case_id']}-analysis.json", {"cfg": case["cfg"]})
        writer.json(manifest_path, expected)
    return expected


def _overlap(pointer, target):
    return pointer == target or pointer.startswith(target + "/") or target.startswith(pointer + "/")


def _post_evaluation(manifest, cases):
    """Initial evidence candidates only; final correctness requires fresh review."""
    fixture = _read(REPOSITORY_ROOT / manifest["source_provenance"]["fixture_manifest_path"])
    oracle_path = REPOSITORY_ROOT / fixture["oracle_path"]
    raw = oracle_path.read_bytes()
    oracle = json.loads(raw)
    if oracle["source_sha256"] != manifest["source_sha256"]:
        raise ValueError("Post-evaluation oracle source identity mismatch")
    evaluation = {
        "usage": "post_execution_only",
        "oracle_path": fixture["oracle_path"],
        "oracle_sha256": hashlib.sha256(raw).hexdigest(),
        "matching_policy": "Initial status and evidence overlap produce candidates, not correctness judgments. Regenerated graph IDs are never matched against old oracle pointers.",
        "cases": {},
    }
    for case_id, outcome in cases.items():
        rounds = outcome.get("rounds", [])
        initial = audit_findings(rounds[0]) if rounds else []
        expectations = []
        for expected in oracle["cases"][case_id]["expected_findings"]:
            candidates = []
            for finding in initial:
                status_match = finding.get("kind") == "semantic" and finding["status"] in expected["acceptable_statuses"]
                graph_match = any(_overlap(pointer, target) for pointer in finding.get("graph_refs", []) for target in expected["graph_refs"])
                source_match = any(
                    ref["file"] == target["file"] and ref["start_line"] <= target["end_line"] and target["start_line"] <= ref["end_line"]
                    for ref in finding.get("source_refs", []) for target in expected["source_refs"]
                )
                if status_match and graph_match and source_match:
                    candidates.append(finding["id"])
            expectations.append({
                "oracle_finding_id": expected["oracle_finding_id"],
                "expected_statuses": expected["acceptable_statuses"],
                "expectation": expected["rationale"],
                "initial_evidence_candidates": candidates,
                "initial_detection": "assistant_review_pending",
                "final_repair": "assistant_review_pending" if rounds else "not_executed",
                "new_error_or_false_pass": "assistant_review_pending" if rounds else "not_executed",
            })
        evaluation["cases"][case_id] = {
            "expectations": expectations,
            "checker_stop_status": outcome["status"],
            "final_graph_evaluation": "No automatic repair claim; inspect the latest graph, latest evidence and full source.",
            "user_confirmed": False,
        }
    return evaluation


def experiment_report(result):
    lines = ["# F01 语义反馈首次对照实验", "",
             "五例分别以冻结原图或结构有效反例开始，每例最多三次语义修复；提取与核对上下文独立。下列名称仅用于事后报告，不进入模型输入。", "",
             "## 实际停止结果", "",
             "| 案例 | 停止状态 | 修复轮数 | 最后一轮业务核对 | 原因 |", "|---|---|---|---|---|"]
    total_extraction = total_audit = total_http = 0
    unavailable_counts = []
    for case_id, outcome in result["cases"].items():
        rounds = outcome.get("rounds", [])
        counts = outcome.get("counts", {})
        if not counts and outcome["status"] != "not_run":
            unavailable_counts.append(case_id)
        total_extraction += counts.get("extraction_logical_calls", 0)
        total_audit += counts.get("audit_logical_calls", 0)
        total_http += counts.get("http_attempts", 0)
        summary = finding_summary(rounds[-1]) if rounds else "未核对"
        clean = lambda text: str(text).replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"| [{case_id} · {CASE_LABELS[case_id]}](cases/{case_id}/report.md) | {STATUS_LABELS.get(outcome['status'], outcome['status'])} | {counts.get('semantic_revisions', 0)} | {clean(summary)} | {clean(outcome.get('reason', ''))} |")
    lines.extend(["", f"已知记录的提取逻辑调用：{total_extraction}；核对逻辑调用：{total_audit}；HTTP 尝试：{total_http}。五例默认逻辑调用上限为 80，HTTP 重试另计。", ""])
    if unavailable_counts:
        lines.extend(["以下案例没有可用的完整计数，不按零调用认定：" + ", ".join(unavailable_counts) + "；应查阅案例 calls 记录。", ""])
    lines.extend([
                  "## 外置预期与复核状态", "",
                  "仅在全部在线调度结束后读取外置预期。第 0 轮的类别与证据区域匹配只是复核候选；重新提取后不会使用旧图指针自动认定缺陷已修复。", "",
                  "| 案例 | 外置预期 | 初轮候选核对项 | 最终修复复核 |", "|---|---|---|---|"])
    for case_id, case in result["evaluation"]["cases"].items():
        for expected in case["expectations"]:
            lines.append(f"| {case_id} | {expected['oracle_finding_id']} | {', '.join(expected['initial_evidence_candidates']) or '无匹配候选'} | {expected['final_repair']} |")
    lines.extend(["", "## 方法判断边界", "",
                  "各案例 report.md 给出逐轮差异、未决、建议和停止原因。完整 result.json 及 rounds、calls 保存实际候选、图、受控文本、响应与证据。", "",
                  "工程结果是执行、保真、记录、恢复和停止控制是否符合规范；方法结果需进一步核查模型是否识别了真实问题、是否误改、是否引入新问题，以及是否出现核对器假通过。", "",
                  "生成报告不把‘核对器通过’自动视为修复正确；助手复核记录应另存 assistant-review.md，并明确尚未由用户确认。F01 五例不支持统计显著性或通用正确性结论。", ""])
    return "\n".join(lines)


def execute(directory, *, replay=False, env_file=None, renderer=None):
    from skill_ir.feedback.runner import refine_skill, replay_run
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    stop_event = threading.Event()
    with _exclusive_run(directory):
        if replay:
            writer = ArtifactWriter(())
            manifest = _read(directory / "manifest.json")
            if manifest.get("schema_version") != 5 or manifest.get("identity") != IDENTITY:
                raise ValueError("Unsupported semantic feedback experiment version")
            manifest = _verified_manifest(directory, manifest["config"], writer)
            factory = None
            secrets = ()
        else:
            from skill_ir.backtrace.runner import public_config
            from skill_ir.recording import streaming_factory
            config = public_config()
            factory, secrets = streaming_factory(config, env_file=env_file)
            writer = ArtifactWriter(secrets)
            manifest = _verified_manifest(directory, config, writer)
        outcomes = {}
        for case in manifest["cases"]:
            case_id = case["case_id"]
            case_dir = directory / case["run_dir"]
            if stop_event.is_set():
                outcomes[case_id] = {"status": "not_run", "reason": "此前已中断，未启动后续案例", "rounds": [], "counts": {}}
                continue
            print(f"{case_id}：{'离线重放' if replay else '执行反馈闭环'}", flush=True)
            try:
                if replay:
                    if not (case_dir / "manifest.json").exists():
                        outcomes[case_id] = {"status": "not_run", "reason": "不存在闭环运行清单", "rounds": [], "counts": {}}
                        continue
                    outcome = replay_run(case_dir, renderer=renderer)
                else:
                    outcome = refine_skill(
                        REPOSITORY_ROOT / manifest["source_provenance"]["source_root"],
                        run_dir=case_dir, initial_analysis=directory / case["initial_analysis"],
                        max_semantic_revisions=3, max_structural_repairs=3,
                        extraction_factory=factory, audit_factory=factory,
                        config=manifest["config"], secrets=secrets,
                        renderer=renderer, stop_event=stop_event,
                        progress=lambda text, identifier=case_id: print(f"{identifier}：{text}", flush=True),
                    )
                outcomes[case_id] = outcome
                if outcome["status"] == "interrupted":
                    stop_event.set()
            except KeyboardInterrupt:
                stop_event.set()
                outcomes[case_id] = {"status": "interrupted", "reason": "用户中断；已开始调用保存在案例目录中", "rounds": [], "counts": {}}
            except Exception as error:
                outcomes[case_id] = {"status": "execution_error", "reason": f"{type(error).__name__}: {error}", "rounds": [], "counts": {}}
            writer.json(directory / ("replay/progress.json" if replay else "progress.json"), outcomes)
        result = {
            "schema_version": 5, "identity": IDENTITY, **contract_binding(),
            "mode": "replay" if replay else "live",
            "cases": outcomes,
            "evaluation": _post_evaluation(manifest, outcomes),
        }
        output = directory / "replay" if replay else directory
        writer.json(output / "experiment-result.json", result)
        writer.text(output / "report.md", experiment_report(result))
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="F01 原图与四反例：每例最多三次语义修复，事后评测隔离")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "replay"):
        command = commands.add_parser(name)
        command.add_argument("--run-dir", type=Path, required=name == "replay")
        command.add_argument("--renderer", type=Path)
        if name == "run":
            command.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    directory = args.run_dir or ROOT / "runs" / ("f01-feedback-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    result = execute(directory, replay=args.command == "replay", env_file=getattr(args, "env_file", None), renderer=args.renderer)
    print(f"实验报告：{directory.resolve()}", flush=True)
    errors = {"extraction_error", "fidelity_error", "audit_error", "execution_error", "interrupted", "not_run"}
    return 1 if any(outcome["status"] in errors for outcome in result["cases"].values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
