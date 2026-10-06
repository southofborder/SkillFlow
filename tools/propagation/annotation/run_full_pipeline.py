"""Re-extract all 30 frozen Skills, run bounded semantic feedback, then annotate.

This is a new experiment, not a resume or reinterpretation of the pinned graph
annotation batch. Saved stage runners own API recovery and offline replay.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import importlib.util
import json
from pathlib import Path
import sys
import threading

from skillflow.common.paths import project_root, resolve_material_path

HERE = Path(__file__).resolve()
PACKAGE_ROOT = project_root()
REPOSITORY_ROOT = project_root()
from tools.propagation.annotation import run_review_set as _sources
build_plan = _sources.build_plan

def public_config():
    """Use the official baseline identity with the newly requested longer wait.

    The historical baseline config stays immutable. This experiment version
    records its own timeout rather than silently inheriting the old three minutes.
    """
    return {**_sources.base_config(), "timeout_ms": 600000}

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.graph.semantic_contract import contract_binding
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.annotation.config import annotation_config

IDENTITY = "skill-ir-full-feedback-security-profile-review30-v10"
LIMITS = {"max_semantic_revisions": 3, "max_structural_repairs": 3,
          "max_audit_execution_retries": 2,
          "extraction_logical_calls_per_case": 16, "audit_logical_calls_per_case": 4,
          "annotation_logical_calls_per_case": 1, "logical_calls_per_case": 21,
          "logical_calls_total": 630, "audit_execution_calls_per_case": 12,
          "execution_calls_per_case": 29, "execution_calls_total": 870}


def _renderer_identity(renderer):
    from skillflow.graph.audit.controlled import _executable
    path = _executable(renderer).resolve()
    return {"path": str(path), "sha256": sha_file(path)}


def _source_case(item):
    """The old selector supplies packages only. Its CFG is deliberately unused."""
    source = resolve_material_path(item["package_path"]).resolve()
    inventory = {p.relative_to(source).as_posix(): {"bytes": p.stat().st_size, "sha256": sha_file(p)}
                 for p in sorted(source.rglob("*")) if p.is_file()}
    return {"case_id": f"{item['index']:03}", "sample_id": item["sample_id"], "basename": item["basename"],
            "package_path": source.relative_to(REPOSITORY_ROOT).as_posix(),
            "source_inventory": inventory, "source_inventory_sha256": canonical_sha256(inventory),
            "run_dir": f"cases/{item['index']:03}"}


def _manifest(directory, plan, config, workers, renderer, writer):
    expected = {"schema_version": 10, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION, **contract_binding(),
                "driver": {"path": HERE.relative_to(REPOSITORY_ROOT).as_posix(), "sha256": sha_file(HERE)},
                "source_selector": {"review_driver_sha256": sha_file(HERE.with_name("run_review_set.py")),
                                    "selector_sha256": sha_file(REPOSITORY_ROOT / "tools/graph/baseline/review_set_source.py")},
                "implementation": implementation_provenance(), "config": config,
                "annotation_config": annotation_config(config), "workers": workers,
                "renderer": _renderer_identity(renderer), "limits": LIMITS,
                "cases": [_source_case(item) for item in plan],
                "policy": {"initial_analysis": None, "selection": "last_valid_cfg_from_current_feedback_only",
                           "annotation_requires_audit_passed": False, "old_cfg_fallback": False,
                           "completed_response_automatic_resend": False,
                           "running_or_interrupted_automatic_resend": False,
                           "confirmed_transient_audit_failure_retries": 2,
                           "review_and_oracle_in_model_input": False}}
    path = directory / "manifest.json"
    if path.exists():
        if read_json(path).get("identity") != IDENTITY or read_json(path).get("schema_version") != 10:
            raise ValueError("Unsupported full pipeline run version; use a new directory for the semantic contract")
        if read_json(path) != expected:
            raise ValueError("Full pipeline input/config/source/driver identity mismatch")
    else:
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise ValueError("New full pipeline experiment requires an empty directory")
        writer.json(path, expected)
    return expected


def _missing(reason, *, status="not_run"):
    return {"status": status, "reason": reason, "profiles": {}, "locations": {}, "transfer_specs": {}, "sink_boundaries": [], "counts": {}}


def _selection(feedback):
    graph = feedback.get("last_valid_cfg")
    if graph is None:
        return None
    digest = canonical_sha256(graph)
    rounds = [row for row in feedback.get("rounds", []) if row.get("graph_sha256") == digest
              and row.get("structural", {}).get("status") == "passed"]
    if not rounds:
        raise ValueError("Last valid CFG has no matching structurally checked feedback round")
    row = rounds[-1]
    return {"policy": "last_valid_cfg_from_current_feedback_only", "revision": row["revision"],
            "graph_sha256": digest, "feedback_status": feedback["status"],
            "auditor_passed": feedback["status"] == "audit_passed",
            "representation_summary": feedback.get("representation_summary", {"represented_ids": [], "conservative_ids": []}),
            **contract_binding(),
            "source_sha256": feedback["source_sha256"],
            "notice": "结构有效的末次图；只有 auditor_passed=true 表示本轮核对器通过。保守依赖仍存在精度损失，不保证语义等价。"}


def _source_binding(feedback_dir, annotation_dir, case):
    """Require identical file bytes and decoded text at the stage boundary."""
    _, feedback_source, first = read_snapshot(feedback_dir)
    _, annotation_source, second = read_snapshot(annotation_dir)
    inventory = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]}
                 for entry in first["files"]}
    if inventory != case["source_inventory"]:
        raise ValueError("Feedback source snapshot differs from the frozen corpus inventory")
    if (feedback_source != annotation_source or first["files"] != second["files"]
            or first["package_bytes_sha256"] != second["package_bytes_sha256"]):
        raise ValueError("Feedback and annotation source bytes or decoded text differ")
    return {"status": "passed", "source_sha256": first["source_sha256"],
            "package_bytes_sha256": first["package_bytes_sha256"],
            "file_count": len(first["files"]), "checked_fields": ["path", "size", "raw_sha256", "decoded_sha256", "kind"]}


def _stable_json(path, value, writer, *, replay=False):
    if path.exists():
        if read_json(path) != value:
            raise ValueError("Committed full pipeline artifact differs: " + path.name)
    elif replay:
        raise ValueError("Missing committed full pipeline artifact: " + path.name)
    else:
        writer.json(path, value)


def _counts(feedback, annotation):
    f = feedback.get("counts", {})
    a = annotation.get("counts", {})
    def number(values, field, stage):
        value = values.get(field, 0 if stage.get("status") == "not_run" else None)
        return value if type(value) is int else None
    def add(*values):
        return sum(values) if all(type(value) is int for value in values) else None
    counts = {"extraction_logical_calls": number(f, "extraction_logical_calls", feedback),
              "audit_logical_calls": number(f, "audit_logical_calls", feedback),
              "audit_execution_calls": number(f, "audit_execution_calls", feedback),
              "audit_execution_retries": number(f, "audit_execution_retries", feedback),
              "annotation_logical_calls": number(a, "logical_calls", annotation),
              "semantic_revisions": number(f, "semantic_revisions", feedback),
              "structural_repairs": number(f, "structural_repairs", feedback),
              "http_attempts": add(number(f, "http_attempts", feedback), number(a, "http_attempts", annotation)),
              "http_retries": add(number(f, "http_retries", feedback), number(a, "http_retries", annotation)),
              "http_attempts_observed": f.get("http_attempts_observed", False) and
                  (a.get("http_attempts_observed", False) if a else annotation["status"] == "not_run"),
              "returned_models": sorted(set(f.get("returned_models", []) + a.get("returned_models", [])))}
    counts["total_logical_calls"] = add(*(counts[key] for key in
        ("extraction_logical_calls", "audit_logical_calls", "annotation_logical_calls")))
    counts["total_execution_calls"] = add(*(counts[key] for key in
        ("extraction_logical_calls", "audit_execution_calls", "annotation_logical_calls")))
    for field, maximum in (("extraction_logical_calls", 16), ("audit_logical_calls", 4),
                           ("annotation_logical_calls", 1), ("total_logical_calls", 21),
                           ("audit_execution_calls", 12), ("audit_execution_retries", 8),
                           ("total_execution_calls", 29)):
        if counts[field] is not None and counts[field] > maximum:
            raise AssertionError("Full pipeline logical call budget exceeded: " + field)
    return counts


def _case(directory, case, *, config, renderer, factory, annotation_factory, secrets, stop_event, replay=False):
    from skillflow.graph.feedback.runner import refine_skill
    from skillflow.graph.feedback.runner import replay_run as replay_feedback
    from skillflow.propagation.annotation.runner import prepare_run
    from skillflow.propagation.annotation.runner import verify_prepared
    from skillflow.propagation.annotation.runner import run_annotation
    from skillflow.propagation.annotation.runner import replay_run as replay_annotation
    profile_config = annotation_config(config)
    writer = ArtifactWriter(secrets)
    root = directory / case["run_dir"]
    output = root / "replay" if replay else root
    feedback_dir, annotation_dir = root / "feedback", root / "annotation"
    progress = lambda message: print(f"{case['case_id']}：{message}", flush=True)
    feedback = _missing("未开始提取")
    annotation = _missing("未开始标注")
    selected = binding = None
    phase = "feedback"
    try:
        if replay:
            if not (feedback_dir / "manifest.json").exists():
                prior = read_json(root / "result.json") if (root / "result.json").exists() else None
                if (prior is None or prior["feedback"]["status"] != "not_run"
                        or prior["annotation"]["status"] != "not_run" or prior["selection"] is not None
                        or prior["source_binding"] is not None or feedback_dir.exists() or annotation_dir.exists()):
                    raise ValueError("Missing feedback manifest for a case that was started or cannot be verified")
                return prior
            feedback = replay_feedback(feedback_dir, renderer=renderer)
        else:
            feedback = refine_skill(resolve_material_path(case["package_path"], base=REPOSITORY_ROOT), run_dir=feedback_dir,
                                    initial_analysis=None, max_semantic_revisions=3, max_structural_repairs=3,
                                    max_audit_execution_retries=LIMITS["max_audit_execution_retries"],
                                    extraction_factory=factory, audit_factory=factory, config=config, secrets=secrets,
                                    renderer=renderer, stop_event=stop_event, progress=progress)
        phase = "selection"
        _, frozen_source, frozen_metadata = read_snapshot(feedback_dir)
        inventory = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]}
                     for entry in frozen_metadata["files"]}
        if inventory != case["source_inventory"] or feedback["source_sha256"] != frozen_source["source_sha256"]:
            raise ValueError("Feedback source snapshot differs from the frozen corpus inventory")
        selected = _selection(feedback)
        boundary_path = root / "execution-boundary.json"
        boundary = read_json(boundary_path) if boundary_path.exists() else None
        if boundary is not None:
            unsigned = {key: value for key, value in boundary.items() if key != "sha256"}
            if (boundary.get("sha256") != canonical_sha256(unsigned)
                    or unsigned.get("kind") not in {"none", "before_annotation"}
                    or (unsigned["kind"] == "none" and unsigned != {"kind": "none", "selection": None})
                    or (replay and unsigned["kind"] == "before_annotation"
                        and unsigned != {"kind": "before_annotation", "selection": selected})):
                raise ValueError("Full pipeline stage interruption boundary changed")
        paused_before_annotation = replay and boundary is not None and boundary["kind"] == "before_annotation"
        if selected is None:
            annotation = _missing("本次反馈流程没有结构有效图；不回退历史 CFG")
        elif feedback["status"] == "interrupted" or paused_before_annotation or (not replay and stop_event.is_set()):
            annotation = _missing("用户中断；不启动后续标注调用")
            stop_event.set()
            if not replay:
                boundary = {"kind": "before_annotation", "selection": selected}
                writer.json(boundary_path, {**boundary, "sha256": canonical_sha256(boundary)})
        else:
            if not replay:
                # An explicit live resume supersedes a previous interruption
                # boundary. Replay must follow the new durable terminal state.
                boundary = {"kind": "none", "selection": None}
                writer.json(boundary_path, {**boundary, "sha256": canonical_sha256(boundary)})
            _stable_json(root / "selection.json", selected, writer, replay=replay)
            analysis = {"cfg": feedback["last_valid_cfg"]}
            _stable_json(root / "selected-analysis.json", analysis, writer, replay=replay)
            phase = "annotation_prepare"
            if (annotation_dir / "manifest.json").exists():
                prepared = verify_prepared(annotation_dir, config=profile_config, replay=replay)
            elif replay:
                annotation = _missing("保存的运行尚未启动标注；离线重放不创建新调用")
                prepared = None
            else:
                prepared = prepare_run(feedback_dir / "inputs/package", root / "selected-analysis.json",
                                       run_dir=annotation_dir, config=profile_config, secrets=secrets)
            if prepared is not None:
                if prepared["preparation_status"] != "ready":
                    annotation = replay_annotation(annotation_dir) if replay else read_json(annotation_dir / "result.json")
                else:
                    binding = _source_binding(feedback_dir, annotation_dir, case)
                    if prepared["graph_sha256"] != selected["graph_sha256"] or prepared["source_sha256"] != selected["source_sha256"]:
                        raise ValueError("Prepared annotation does not match selected feedback graph/source")
                    _stable_json(root / "source-binding.json", binding, writer, replay=replay)
                    phase = "annotation"
                    progress(f"{'重放' if replay else '开始'}第 {selected['revision']} 轮 CFG 的唯一标注；反馈状态 {feedback['status']}")
                    annotation = replay_annotation(annotation_dir) if replay else run_annotation(
                        annotation_dir, client_factory=annotation_factory, config=profile_config, secrets=secrets,
                        stop_event=stop_event, progress=progress)
        if feedback["status"] == "interrupted" or annotation["status"] == "interrupted":
            stop_event.set()
        error = None
    except KeyboardInterrupt:
        stop_event.set()
        error = {"phase": phase, "type": "KeyboardInterrupt", "message": "用户中断；后续调用不启动"}
        if phase == "feedback":
            feedback = _missing(error["message"], status="interrupted")
        else:
            annotation = _missing(error["message"], status="interrupted")
    except Exception as exc:
        error = {"phase": phase, "type": type(exc).__name__, "message": writer.clean(str(exc))}
        if phase == "feedback":
            feedback = _missing(error["message"], status="execution_error")
        else:
            annotation = _missing(error["message"], status="execution_error")
    result = {"feedback": feedback, "selection": selected, "source_binding": binding, "annotation": annotation,
              "counts": _counts(feedback, annotation), "scheduler_error": error}
    if replay and (root / "result.json").exists():
        original = read_json(root / "result.json")
        if result != original:
            raise ValueError("Offline full pipeline replay differs from saved stages or selection: " + case["case_id"])
    writer.json(output / "result.json", result)
    return result


def _summary(outcomes):
    totals = Counter()
    for result in outcomes.values():
        for field, value in result["counts"].items():
            if type(value) is int:
                totals[field] += value
    return {"cases": len(outcomes), "feedback_statuses": dict(Counter(item["feedback"]["status"] for item in outcomes.values())),
            "annotation_statuses": dict(Counter(item["annotation"]["status"] for item in outcomes.values())),
            "selected_graphs": sum(item["selection"] is not None for item in outcomes.values()),
            "profiles": sum(len(item["annotation"].get("profiles", {})) for item in outcomes.values()),
            "partial_order_ir_count": sum(_sources.partial_order_count(item["annotation"]) for item in outcomes.values()),
            "counts": dict(totals), "unavailable_count_cases": [key for key, value in outcomes.items()
                if any(item is None for item in value["counts"].values())]}


def render_report(result, manifest):
    summary = result["summary"]
    clean = lambda value: str(value).replace("|", "\\|").replace("\n", "<br>")
    prefix = "../" if result["mode"] == "replay" else ""
    stage = "/replay" if result["mode"] == "replay" else ""
    lines = ["# 30 个 Skill 重新提取、语义反馈与安全语义标注", "",
             "本轮从冻结 Skill 源包重新提取，不采用历史 CFG。每例最多 3 次语义修复，每轮最多 3 次结构修复，随后对本轮末次结构有效图标注一次。", "",
             "核对遇到可识别的暂态传输失败时，最多额外重试 2 次；语义核对轮次、执行尝试与 HTTP 尝试分别计数。完整响应、无效语义核对 JSON、未决、用户中断或状态不确定的请求不因本策略自动重发。远程阻塞读取超时为 600 秒。", "",
             "核对器通过仅记为 audit_passed；其他停止状态仍明确保留。标注记录完整不保证分类正确。本轮没有进行数据传播、风险、必要性或 DOE 判断。", "",
             f"模式：{result['mode']}；反馈状态：{clean(summary['feedback_statuses'])}；标注状态：{clean(summary['annotation_statuses'])}。", "",
             f"有效保存 {summary['profiles']} 份 profile，{summary['partial_order_ir_count']} 条部分顺序 IR。调用计数：{clean(summary['counts'])}。", "",
             f"计数仅汇总已观测值，计数不完整的案例：{', '.join(summary['unavailable_count_cases']) or '无'}。未知不视为零。", "",
             "| 编号／样例 | 反馈停止状态 | 选图轮次 | 标注状态 | profile 数 | 未决数 | 原因 |",
             "|---|---|---:|---|---:|---:|---|"]
    for case in manifest["cases"]:
        identifier = case["case_id"]
        row = result["cases"][identifier]
        selected, annotation = row["selection"], row["annotation"]
        selected_round = selected["revision"] if selected else "无"
        feedback_link = f"{prefix}cases/{identifier}/feedback{stage}/report.md"
        annotation_link = f"{prefix}cases/{identifier}/annotation{stage}/report.md"
        annotation_status = (f"[{annotation['status']}]({annotation_link})" if annotation["status"] != "not_run" else "not_run")
        lines.append(f"| {identifier} · {case['sample_id']} · {case['basename']} | [{row['feedback']['status']}]({feedback_link}) | "
                     f"{selected_round} | {annotation_status} | {len(annotation.get('profiles', {}))} | {_sources.partial_order_count(annotation)} | "
                     f"{clean(annotation.get('reason', '') or row['feedback'].get('reason', ''))} |")
    lines += ["", "每例 selection.json 记录当前末次有效图的轮次、摘要与反馈停止状态；source-binding.json 校验两个阶段的文件字节与解码文本一致。", "",
              "没有有效图的案例不进行标注，不回退历史基线图。来源、配置、源码、打印器及各次响应均保留；恢复先消费已保存响应。只对已经明确以暂态传输失败结束的核对调用创建有界的新尝试，失败与重试决定分别留存。", "",
              "助手逐例复核另存；本自动报告不能替代复核，不将运行或格式校验通过当成语义正确性结论。", ""]
    return "\n".join(lines)


def execute(directory, *, mode="run", env_file=None, workers=None, renderer=None):
    if mode not in {"run", "replay"}:
        raise ValueError("mode must be run or replay")
    if workers is not None and (type(workers) is not int or not 1 <= workers <= 8):
        raise ValueError("workers must be an integer from 1 through 8")
    if mode == "replay" and env_file is not None:
        raise ValueError("Offline replay does not read environment files")
    directory = Path(directory).resolve()
    plan = build_plan()
    protected = [REPOSITORY_ROOT / name for name in ("dataset", "result")]
    protected += [resolve_material_path(address) for address in ("experiments/graph/baseline", "experiments/corpus/semantics_review", "experiments/graph/feedback")]
    protected += [Path(case["package_path"]).resolve() for case in plan]
    if any(directory == root or directory.is_relative_to(root) for root in protected):
        raise ValueError("Experiment output must not overlap frozen input or historical delivery directories")
    if mode == "replay" and not (directory / "manifest.json").is_file():
        raise ValueError("Offline replay requires an existing full pipeline manifest")
    directory.mkdir(parents=True, exist_ok=True)
    stop_event = threading.Event()
    with exclusive_run(directory):
        prior = read_json(directory / "manifest.json") if (directory / "manifest.json").exists() else None
        if prior is not None and (prior.get("schema_version") != 10 or prior.get("identity") != IDENTITY
                                  or prior.get("profile_schema_version") != SCHEMA_VERSION):
            raise ValueError("Unsupported full pipeline run version; use a new directory for the semantic contract")
        selected_workers = workers if workers is not None else (prior["workers"] if prior else 3)
        config = prior["config"] if mode == "replay" else public_config()
        if renderer is None and prior:
            renderer = prior["renderer"]["path"]
        writer = ArtifactWriter(())
        manifest = _manifest(directory, plan, config, selected_workers, renderer, writer)
        renderer = manifest["renderer"]["path"]
        output = directory / "replay" if mode == "replay" else directory
        outcomes = {}
        factory, profile_factory, secrets = None, None, ()
        if mode == "run":
            from skillflow.common.recording import streaming_factory
            factory, secrets = streaming_factory(config, env_file=env_file)
            profile_factory, profile_secrets = streaming_factory(manifest["annotation_config"], env_file=env_file)
            secrets = tuple(dict.fromkeys((*secrets, *profile_secrets)))
            writer = ArtifactWriter(secrets)

        def save():
            writer.json(output / "progress.json", {key: outcomes[key] for key in sorted(outcomes)})

        def work(case):
            print(f"{case['case_id']} {case['sample_id']}：{'离线重放完整流程' if mode == 'replay' else '从冻结源包开始提取及反馈'}", flush=True)
            try:
                return _case(directory, case, config=config, renderer=renderer, factory=factory, annotation_factory=profile_factory, secrets=secrets,
                             stop_event=stop_event, replay=mode == "replay")
            except Exception as error:
                if mode == "replay":
                    raise
                # A stage can finish its calls and then fail during final local
                # persistence. Keep its actual records and let other cases finish.
                message = writer.clean(f"{type(error).__name__}: {error}")
                root = directory / case["run_dir"]
                def saved(stage):
                    try:
                        return read_json(root / stage / "result.json")
                    except (OSError, ValueError):
                        return _missing(message, status="execution_error")
                feedback, annotation = saved("feedback"), saved("annotation")
                try:
                    counts = _counts(feedback, annotation)
                except Exception:
                    counts = {"total_logical_calls": None, "http_attempts_observed": False}
                return {"feedback": feedback, "selection": None, "source_binding": None, "annotation": annotation,
                        "counts": counts, "scheduler_error": {"phase": "scheduler", "type": type(error).__name__, "message": message}}

        if mode == "replay":
            for case in manifest["cases"]:
                outcomes[case["case_id"]] = work(case)
                save()
        else:
            remaining = iter(manifest["cases"])
            pending = {}
            with ThreadPoolExecutor(max_workers=selected_workers) as executor:
                def fill():
                    while len(pending) < selected_workers and not stop_event.is_set():
                        case = next(remaining, None)
                        if case is None:
                            break
                        pending[executor.submit(work, case)] = case
                fill()
                while pending:
                    try:
                        finished, _ = wait(pending, return_when=FIRST_COMPLETED, timeout=0.2)
                    except KeyboardInterrupt:
                        stop_event.set()
                        save()
                        continue
                    for future in finished:
                        case = pending.pop(future)
                        outcomes[case["case_id"]] = future.result()
                        save()
                    fill()
        for case in manifest["cases"]:
            identifier = case["case_id"]
            if identifier not in outcomes:
                missing = _missing("用户中断；未启动此案例")
                row = {"feedback": missing, "selection": None, "source_binding": None, "annotation": missing,
                       "counts": _counts(missing, missing), "scheduler_error": None}
                outcomes[identifier] = row
                writer.json(directory / case["run_dir"] / "result.json", row)
        outcomes = {case["case_id"]: outcomes[case["case_id"]] for case in manifest["cases"]}
        result = {"schema_version": 10, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION, **contract_binding(), "mode": mode, "cases": outcomes,
                  "summary": _summary(outcomes), "assistant_review": "pending", "user_confirmed": False}
        writer.json(output / "experiment-result.json", result)
        writer.text(output / "report.md", render_report(result, manifest))
        save()
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "replay"):
        command = commands.add_parser(name)
        command.add_argument("--run-dir", type=Path, required=True)
        command.add_argument("--renderer", type=Path)
        if name == "run":
            command.add_argument("--env-file", type=Path)
            command.add_argument("--workers", type=int)
    args = parser.parse_args(argv)
    result = execute(args.run_dir, mode=args.command, env_file=getattr(args, "env_file", None),
                     workers=getattr(args, "workers", None), renderer=args.renderer)
    print(json.dumps(result["summary"], ensure_ascii=False), flush=True)
    return int(any(item["annotation"]["status"] not in {"complete"} for item in result["cases"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
