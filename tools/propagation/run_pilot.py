"""Rebuild three frozen Skills, audit with bounded feedback, annotate once, propagate."""
from __future__ import annotations

import argparse
from collections import Counter
from html import escape
import importlib.util
from pathlib import Path
import sys
from threading import Event

from skillflow.common.paths import project_root, resolve_material_path

PACKAGE = project_root()
ROOT = project_root()

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.common.inputs.snapshot import freeze_input
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import streaming_factory
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION as PROFILE_VERSION
from skillflow.propagation.annotation.config import annotation_config
from skillflow.graph.semantic_contract import contract_binding
from skillflow.propagation.runner import load_propagation_run
from skillflow.propagation.runner import run_propagation
from skillflow.propagation.runner import replay_propagation

from tools.propagation.annotation import run_full_pipeline as _shared
SHARED_DRIVER = Path(_shared.__file__)

IDENTITY = "skill-ir-source-boundaries-pilot3-v4"
FORMAT_VERSION = 4
ORIGIN = PACKAGE / "experiments/propagation/annotation/runs/full-pipeline-v4-20260918-rerun-failed/cases"
PINS = {
    "001": ("N01", "836d34ef584eff7f9543661958c2d23614132db613fbaccf077fac57f7e50c56", "6c0561338e81f9706b4a30b1f9ed4fffac663c7f7bb3a144e01a8f2a8e1c59ab"),
    "010": ("Q04", "419ebdfa305fb171533662ca807f6e399ab21faafe087065dff05f9bc5711c24", "66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c"),
    "013": ("F01", "ae396cd3a04cb0cd861f7fa4fe399b363a31edef3ba8595061315719f9710a64", "fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da"),
}
POLICY = {
    "initial_analysis": None, "old_cfg_fallback": False,
    "selection": "last_valid_cfg_from_current_feedback_only",
    "annotation_requires_audit_passed": False, "workers": 1,
    "max_semantic_revisions": 3, "max_structural_repairs": 3,
    "max_audit_execution_retries": 2,
    "logical_calls_per_case": 21, "planned_logical_calls": 63,
    "annotation_logical_calls_per_case": 1, "planned_annotation_calls": 3,
    "execution_calls_per_case": 29, "execution_calls_total": 87,
    "selection_retries": 0, "propagation_calls": 0,
    "completed_response_automatic_resend": False,
    "running_or_interrupted_automatic_resend": False,
}


def plan():
    """The historical graph is comparison material only, never an extraction input."""
    cases = []
    for number, (sample, graph_hash, source_hash) in PINS.items():
        prior = ORIGIN / number
        analysis = prior / "selected-analysis.json"
        cfg = read_json(analysis)["cfg"]
        _, source, snapshot = read_snapshot(prior / "annotation")
        if canonical_sha256(cfg) != graph_hash or source["source_sha256"] != source_hash:
            raise ValueError(f"pinned source/comparison CFG differs: {number}")
        inventory = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]}
                     for entry in snapshot["files"]}
        cases.append({"case_id": number, "sample_id": sample,
                      "input": str(prior / "annotation/inputs/package"),
                      "source_sha256": source_hash, "source_inventory": inventory,
                      "package_bytes_sha256": snapshot["package_bytes_sha256"],
                      "comparison": {"analysis": str(analysis), "analysis_sha256": sha_file(analysis),
                                     "graph_sha256": graph_hash}})
    return cases


def public_config():
    variant = read_json(PACKAGE / "experiments/graph/baseline/deepseek-v4-flash.json")["variants"][0]
    config = {key: variant[key] for key in ("endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries", "retry_base_ms", "retry_max_backoff_ms")}
    config["timeout_ms"] = 600000
    if config["endpoint"] != "https://api.deepseek.com/chat/completions" or config["model"] != "deepseek-v4-flash":
        raise ValueError("pilot requires the pinned official DeepSeek configuration")
    return config


def expected_manifest(renderer=None):
    return {"schema_version": FORMAT_VERSION, "identity": IDENTITY,
            "profile_schema_version": PROFILE_VERSION, **contract_binding(), "cases": plan(),
            "config": public_config(), "annotation_config": annotation_config(public_config()),
            "implementation": implementation_provenance(),
            "renderer": _shared._renderer_identity(renderer),
            "driver_sha256": sha_file(Path(__file__)), "shared_case_driver_sha256": sha_file(SHARED_DRIVER),
            "policy": POLICY}


def verify_source(directory, case):
    _, source, snapshot = read_snapshot(directory / "cases" / case["case_id"] / "source")
    inventory = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]}
                 for entry in snapshot["files"]}
    if (source["source_sha256"] != case["source_sha256"]
            or snapshot["package_bytes_sha256"] != case["package_bytes_sha256"]
            or inventory != case["source_inventory"]):
        raise ValueError("prepared source differs from frozen source pin: " + case["case_id"])


def _case_plan(directory, case):
    return {"case_id": case["case_id"], "sample_id": case["sample_id"],
            "run_dir": "cases/" + case["case_id"],
            "package_path": str(directory / "cases" / case["case_id"] / "source/inputs/package"),
            "source_inventory": case["source_inventory"]}


def _sum_known(rows, field):
    values = [row["call_counts"].get(field) for row in rows]
    return sum(values) if all(type(value) is int for value in values) else None


def _stage_after_save_failure(base, stage, replay):
    directory = base / stage
    path = directory / ("replay/result.json" if replay else "result.json")
    if path.exists():
        return read_json(path)
    if (directory / "manifest.json").exists():
        return _shared._missing("阶段已启动但未保存可核验结果；调用计数未知", status="execution_error")
    return _shared._missing("未开始")


def summarize(directory, writer, *, replay=False):
    rows = []
    for number, (sample, _, _) in PINS.items():
        base = directory / "cases" / number
        stage_path = base / ("replay/result.json" if replay else "result.json")
        stages = read_json(stage_path) if stage_path.exists() else {
            "feedback": _stage_after_save_failure(base, "feedback", replay),
            "annotation": _stage_after_save_failure(base, "annotation", replay),
        }
        feedback = stages.get("feedback", {})
        annotation = stages.get("annotation", {})
        counts = stages.get("counts", _shared._counts(feedback, annotation))
        committed = (base / "propagation/manifest.json").is_file()
        propagation, propagation_error = {}, None
        if committed:
            try:
                propagation = load_propagation_run(base / "propagation")
            except Exception as error:
                committed = False
                propagation_error = f"{type(error).__name__}: {error}"
        unfinished = (base / "propagation").exists() and not committed
        failure_path = base / ("replay/driver-error.json" if replay else "driver-error.json")
        failure = read_json(failure_path) if failure_path.exists() else None
        rows.append({"case_id": number, "sample_id": sample,
                     "feedback": feedback.get("status", "not_run"), "feedback_reason": feedback.get("reason"),
                     "selection": stages.get("selection"), "source_binding": stages.get("source_binding"),
                     "annotation": annotation.get("status", "not_run"),
                     "propagation": propagation.get("status", "execution_error" if failure or propagation_error else "uncommitted" if unfinished else "not_run"),
                     "propagation_committed": committed, "propagation_error": propagation_error,
                     "driver_error": failure, "scheduler_error": stages.get("scheduler_error"),
                     "logical_calls": counts.get("total_logical_calls"), "call_counts": counts,
                     "annotation_reason": annotation.get("reason"),
                     "partial_order_ir_ids": [key for key, spec in annotation.get("transfer_specs", {}).items() if spec.get("order") == "partial"], "diagnostics": propagation.get("diagnostics", [])})
    summary = {"identity": IDENTITY, "profile_schema_version": PROFILE_VERSION, "mode": "replay" if replay else "run",
               "cases": rows, "logical_calls": _sum_known(rows, "total_logical_calls"),
               "annotation_calls": _sum_known(rows, "annotation_logical_calls"),
               "feedback_statuses": dict(Counter(r["feedback"] for r in rows)),
               "annotation_statuses": dict(Counter(r["annotation"] for r in rows)),
               "propagation_statuses": dict(Counter(r["propagation"] for r in rows))}
    output = directory / "replay" if replay else directory
    prefix = "../" if replay else ""
    writer.json(output / "summary.json", summary)
    notice = "从冻结源包重新建图及有界反馈；每例只标注一次，传播和重放离线。不回退历史图，不按质量补跑。核对未通过的末次结构有效图仅用于诊断。"
    questions = ["来源是什么？", "读取范围是什么？", "模型观察哪个版本？", "最终取出什么？", "实际传给谁？"]
    lines = ["# 三例来源范围、工具返回与模型观察实测", "", notice, "", "审查顺序：" + " → ".join(questions), "",
             "核对器通过、标注记录完整及传播完成都不是语义等价或无 DOE 的证明。", "",
             "| 样例 | 反馈 | 标注 | 传播 | 逻辑调用 | 审查材料 |", "|---|---|---|---|---:|---|"]
    html = ["<h1>来源范围与工具返回：三例审查</h1><p>" + notice + "</p><ol>" + "".join("<li>" + q + "</li>" for q in questions) + "</ol>",
            "<p>核对器通过、标注记录完整及传播完成都不是语义等价或无 DOE 的证明。</p>",
            "<table><tr><th>样例</th><th>反馈</th><th>标注</th><th>传播</th><th>调用</th><th>审查</th></tr>"]
    for row in rows:
        n = row["case_id"]
        links, html_links = [], []
        for relative, title in ((f"cases/{n}/feedback/report.md", "建图与核对"),
                                (f"cases/{n}/selection.json", "实际选图与停止状态"),
                                (f"cases/{n}/annotation/report.md", "联合标注"),
                                (f"cases/{n}/propagation/report.html", "传播审查"),
                                (f"cases/{n}/propagation/doe-input.json", "DOE 原始事实"),
                                (f"cases/{n}/assistant-review.md", "助手复核")):
            if "/propagation/" in relative and not row["propagation_committed"]:
                continue
            if (directory / relative).exists():
                links.append(f"[{title}]({prefix}{relative})")
                html_links.append(f"<a href='{prefix}{relative}'>{title}</a>")
        lines.append(f"| {n} / {row['sample_id']} | {row['feedback']} | {row['annotation']} | {row['propagation']} | {row['logical_calls']} | {' · '.join(links) or '尚未生成'} |")
        html.append(f"<tr><td>{n} / {row['sample_id']}</td><td>{escape(row['feedback'])}</td><td>{escape(row['annotation'])}</td><td>{escape(row['propagation'])}</td><td>{row['logical_calls']}</td><td>{' · '.join(html_links) or '尚未生成'}</td></tr>")
    lines += ["", "计划内逻辑调用最多 63 次，其中联合标注最多 3 次；暂态核对执行重试和 HTTP 尝试分别统计。", "",
              "对照旧结果按源文动作和关系核对，不按旧 IR 编号认定同一动作。完整模型响应、证据及用量保存在各例阶段调用记录中。", ""]
    html.append("</table><p><a href='" + prefix + "assistant-review.md'>助手总复核</a> · <a href='summary.json'>完整状态</a></p>")
    writer.text(output / "report.md", "\n".join(lines))
    writer.text(output / "index.html", "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>来源范围实测审查</title><style>body{font:16px/1.6 'Microsoft YaHei',sans-serif;max-width:1200px;margin:40px auto}td,th{padding:12px;border:1px solid #ccc}table{border-collapse:collapse}a{color:#176ac1}</style><body>" + "".join(html) + "</body></html>")
    return summary


def run_case(directory, case, *, config, renderer, factory, annotation_factory=None, secrets, stopping, replay=False):
    outcome = _shared._case(directory, _case_plan(directory, case), config=config, renderer=renderer,
                            factory=factory, annotation_factory=annotation_factory, secrets=secrets, stop_event=stopping, replay=replay)
    if replay:
        # The shared service intentionally returns an untouched not_run case
        # early. Persist that verified outcome for this pilot's replay summary;
        # this records no model attempt and creates no missing stage material.
        replay_result = directory / "cases" / case["case_id"] / "replay/result.json"
        if not replay_result.exists():
            if (outcome["feedback"]["status"] != "not_run"
                    or outcome["annotation"]["status"] != "not_run"):
                raise ValueError("shared case replay did not persist its started-stage result")
            ArtifactWriter(secrets).json(replay_result, outcome)
    if outcome["feedback"]["status"] == "interrupted" or outcome["annotation"]["status"] == "interrupted":
        stopping.set()
    if not stopping.is_set() and outcome["annotation"]["status"] in {"complete"}:
        base = directory / "cases" / case["case_id"]
        prop_dir = base / "propagation"
        if replay and not (prop_dir / "manifest.json").is_file():
            raise ValueError("propagation run has no committed manifest; replay cannot create a new run")
        propagated = (replay_propagation(prop_dir) if (prop_dir / "manifest.json").exists()
                      else run_propagation(base / "annotation", run_dir=prop_dir))
        print(case["case_id"], "propagation", propagated["status"], flush=True)
    return outcome


def main(argv=None):
    parser = argparse.ArgumentParser(description="001/010/013 从源包重新建图、反馈、一次联合标注及离线传播")
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--renderer", type=Path)
    args = parser.parse_args(argv)
    if args.command != "run" and args.env_file is not None:
        raise ValueError("offline prepare/replay does not read environment files")
    directory = args.run_dir.resolve()
    protected = [ROOT / "dataset", ROOT / "result", PACKAGE / "src", ORIGIN]
    if any(directory == path or directory.is_relative_to(path) for path in protected):
        raise ValueError("pilot output overlaps protected inputs or source code")
    if args.command != "prepare" and not (directory / "manifest.json").is_file():
        raise ValueError("prepare a new pilot run first")
    prior = read_json(directory / "manifest.json") if (directory / "manifest.json").exists() else None
    if prior is not None and (prior.get("schema_version") != FORMAT_VERSION or prior.get("identity") != IDENTITY):
        raise ValueError("unsupported pilot version; use a new directory")
    renderer = args.renderer or (prior["renderer"]["path"] if prior else None)
    expected = expected_manifest(renderer)
    writer = ArtifactWriter(())
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        manifest = directory / "manifest.json"
        if manifest.exists():
            if read_json(manifest) != expected:
                raise ValueError("pilot input/config/source identity changed")
        else:
            if any(p.name != ".runner.lock" for p in directory.iterdir()):
                raise ValueError("prepare requires a new empty directory")
            for case in expected["cases"]:
                freeze_input(case["input"], directory / "cases" / case["case_id"] / "source", writer)
                verify_source(directory, case)
            writer.json(manifest, expected)
        for case in expected["cases"]:
            verify_source(directory, case)
        if args.command == "prepare":
            print("prepared", len(expected["cases"]), "frozen sources; model calls: 0", flush=True)
            return 0
        factory, secrets = (streaming_factory(expected["config"], env_file=args.env_file)
                            if args.command == "run" else (None, ()))
        profile_factory, profile_secrets = (streaming_factory(expected["annotation_config"], env_file=args.env_file)
                                            if args.command == "run" else (None, ()))
        secrets = tuple(dict.fromkeys((*secrets, *profile_secrets)))
        writer, stopping = ArtifactWriter(secrets), Event()
        replay = args.command == "replay"
        for case in expected["cases"]:
            base = directory / "cases" / case["case_id"]
            if stopping.is_set() and not replay:
                if not (base / "result.json").exists():
                    missing = _shared._missing("用户中断；未启动此案例")
                    writer.json(base / "result.json", {"feedback": missing, "selection": None, "source_binding": None,
                                                       "annotation": missing, "counts": _shared._counts(missing, missing),
                                                       "scheduler_error": None})
                continue
            try:
                # Replay each case's saved interruption independently; it never starts calls.
                if replay:
                    stopping.clear()
                run_case(directory, case, config=expected["config"], renderer=expected["renderer"]["path"],
                         factory=factory, annotation_factory=profile_factory, secrets=secrets, stopping=stopping, replay=replay)
            except KeyboardInterrupt:
                stopping.set()
                summarize(directory, writer, replay=replay)
            except Exception as error:
                output = base / "replay" if replay else base
                writer.json(output / "driver-error.json", {"error": f"{type(error).__name__}: {error}"})
                print(case["case_id"], "execution failure:", writer.clean(str(error)), flush=True)
            summarize(directory, writer, replay=replay)
    summary = summarize(directory, writer, replay=replay)
    print("logical calls:", summary["logical_calls"], "; annotation calls:", summary["annotation_calls"], flush=True)
    return 130 if stopping.is_set() and not replay else 0


if __name__ == "__main__":
    raise SystemExit(main())
