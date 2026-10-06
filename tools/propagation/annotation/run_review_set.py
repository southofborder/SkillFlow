"""Annotate the 30 pinned CFGs once each, with isolated contexts and offline replay."""

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

ROOT = project_root() / "experiments/propagation/annotation"
PACKAGE_ROOT = project_root()
REPOSITORY_ROOT = project_root()

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.propagation.contracts.profiles import EFFECTS
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.annotation.config import annotation_config


IDENTITY = "skill-ir-security-profile-review30-v6"
BASELINE = PACKAGE_ROOT / "experiments/graph/baseline"
BASELINE_RUN = BASELINE / "runs/baseline-deepseek-v4-flash-max-20260910"
SAMPLE_IDS = tuple(f"{group}{index:02}" for group in "NQFDR" for index in range(1, 7))
STATUS_LABELS = {
    "prepared": "离线准备完成", "complete": "标注记录完整", "semantic_failure": "无法完成必要判断",
    "input_error": "输入错误", "invalid_response": "响应无效", "execution_error": "执行错误",
    "interrupted": "已中断", "not_run": "未执行",
}


def base_config():
    """Reuse only public fields from the already-pinned official configuration."""
    variant = read_json(BASELINE / "deepseek-v4-flash.json")["variants"][0]
    fields = ("endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
              "retry_base_ms", "retry_max_backoff_ms")
    config = {field: variant[field] for field in fields}
    if config["endpoint"] != "https://api.deepseek.com/chat/completions" or config["model"] != "deepseek-v4-flash":
        raise ValueError("The experiment requires the pinned official DeepSeek endpoint and deepseek-v4-flash")
    return config


def public_config():
    return annotation_config(base_config())


def build_plan():
    """Use the same source/byte verification and selection as the ZIP/PNG corpus."""
    from tools.graph.baseline import review_set_source as module
    plan = module.build_export_plan(REPOSITORY_ROOT, BASELINE_RUN)
    if (len(plan) != 30 or tuple(item["sample_id"] for item in plan) != SAMPLE_IDS
            or [item["index"] for item in plan] != list(range(1, 31))):
        raise ValueError("Expected the fixed ordered 001–030 N/Q/F/D/R corpus")
    for item in plan:
        if item["repetition"] != (3 if item["sample_id"] == "F03" else 1):
            raise ValueError("Pinned selection changed: require F03 repetition 3 and all other repetition 1")
    return plan


def _case_identity(item):
    source = resolve_material_path(item["package_path"]).resolve()
    inventory = {path.relative_to(source).as_posix(): {"bytes": path.stat().st_size, "sha256": sha_file(path)}
                 for path in sorted(source.rglob("*")) if path.is_file()}
    cfg = item["cfg"]
    return {
        "case_id": f"{item['index']:03}", "sample_id": item["sample_id"], "basename": item["basename"],
        "repetition": item["repetition"], "baseline_run_id": item["run_id"],
        "package_path": source.relative_to(REPOSITORY_ROOT).as_posix(),
        "analysis_path": resolve_material_path(item["analysis_path"]).resolve().relative_to(REPOSITORY_ROOT).as_posix(),
        "analysis_sha256": item["analysis_sha256"], "graph_sha256": canonical_sha256(cfg),
        "source_inventory": inventory, "source_inventory_sha256": canonical_sha256(inventory),
        "instruction_count": sum(len(block["instructions"]) for block in cfg["blocks"].values()),
        "run_dir": f"cases/{item['index']:03}",
        "background": "Earliest structurally complete baseline; this batch does not assert prior semantic audit success.",
    }


def _verified_manifest(directory, plan, config, workers, writer):
    expected = {
        "schema_version": 6, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION,
        "driver": {"path": Path(__file__).resolve().relative_to(REPOSITORY_ROOT).as_posix(), "sha256": sha_file(Path(__file__))},
        "source_selector": {"path": (REPOSITORY_ROOT / "tools/graph/baseline/review_set_source.py").relative_to(REPOSITORY_ROOT).as_posix(),
                            "sha256": sha_file(REPOSITORY_ROOT / "tools/graph/baseline/review_set_source.py")},
        "config": config, "workers": workers,
        "limits": {"logical_calls_per_case": 1, "logical_calls_total": 30},
        "cases": [_case_identity(item) for item in plan],
        "review_policy": "Assistant review after execution; no oracle or past verdict is used as model input.",
    }
    path = directory / "manifest.json"
    if path.exists():
        if read_json(path) != expected:
            raise ValueError("Security-profile experiment input/config/driver identity mismatch")
    else:
        if any(path.name != ".runner.lock" for path in directory.iterdir()):
            raise ValueError("A new security-profile experiment requires an empty directory")
        writer.json(path, expected)
    return expected


def _missing(status, reason):
    return {"status": status, "reason": reason, "profiles": {}, "locations": {}, "transfer_specs": {}, "sink_boundaries": [],
            "validation": {"status": "not_run", "errors": []}, "counts": {}}


def partial_order_count(outcome):
    """Count typed partial-order IRs, not generic pending judgments."""
    return sum(spec.get("order") == "partial" for spec in outcome.get("transfer_specs", {}).values())


def _summary(outcomes):
    statuses = Counter(outcome["status"] for outcome in outcomes.values())
    effect_counts = Counter({effect: 0 for effect in EFFECTS})
    counts = Counter()
    unknown_counts = []
    for identifier, outcome in outcomes.items():
        for profile in outcome.get("profiles", {}).values():
            effect_counts.update(set(profile["effects"]))
        observed = outcome.get("counts", {})
        if not observed and outcome["status"] not in {"not_run", "prepared"}:
            unknown_counts.append(identifier)
        for field in ("logical_calls", "http_attempts", "http_retries"):
            value = observed.get(field)
            if type(value) is int:
                counts[field] += value
    return {"cases": len(outcomes), "statuses": dict(statuses), "effects": dict(effect_counts),
            "profiles": sum(len(item.get("profiles", {})) for item in outcomes.values()),
            "partial_order_ir_count": sum(partial_order_count(item) for item in outcomes.values()),
            "known_counts": dict(counts), "unavailable_count_cases": unknown_counts}


def experiment_report(result, manifest):
    summary = result["summary"]
    clean = lambda value: str(value).replace("|", "\\|").replace("\n", "<br>")
    lines = ["# 30 图 Security Profile 首次标注", "",
             "输入采用已冻结的 30 个 Skill 和既有选定 CFG：29 个第 1 轮，F03 第 3 轮。每例一次独立逻辑标注调用。", "",
             "标注只描述动作的执行主体（operator）、roles、effects 和 evidences；本轮不传播数据，不判断风险、必要性或 DOE。", "",
             "## 执行概况", "", f"模式：{result['mode']}；案例数：{summary['cases']}；状态分布：{clean(summary['statuses'])}。", "",
             f"有效保存的 profile 数：{summary['profiles']}；部分顺序 IR：{summary['partial_order_ir_count']}；已知调用计数：{clean(summary['known_counts'])}。", "",
             "计数只汇总已保存的观测值；缺少调用计数的案例不按零调用认定：" + (", ".join(summary["unavailable_count_cases"]) or "无") + "。", "",
             "## 逐例结果", "", "| 编号／样例 | 原轮次 | 状态 | profile／IR | 部分顺序 IR | 原因 |", "|---|---:|---|---:|---:|---|"]
    for case in manifest["cases"]:
        identifier = case["case_id"]
        outcome = result["cases"][identifier]
        link = f"cases/{identifier}/report.md"
        if result["mode"] == "replay":
            link = f"../cases/{identifier}/replay/report.md"
        lines.append(f"| [{identifier} · {case['sample_id']} · {case['basename']} ]({link}) | {case['repetition']} | "
                     f"{STATUS_LABELS.get(outcome['status'], outcome['status'])} | {len(outcome.get('profiles', {}))}/{case['instruction_count']} | "
                     f"{partial_order_count(outcome)} | {clean(outcome.get('reason', ''))} |")
    lines += ["", "## 效果分布", "", "一条 IR 可具有多个 effects；以下为各标签对应的 IR 数，不是数据量或风险分数。", "",
              "| effect | IR 数 |", "|---|---:|"]
    lines += [f"| {effect}" + ("（上下文写入）" if effect == "context_write" else "")
              + f" | {summary['effects'][effect]} |" for effect in EFFECTS]
    lines += ["", "## 复核边界", "",
              "effects=[] 表示没有已记录的适用效果，不等于空操作，也不表示入口与出口状态相同。程序只验证四字段契约、ID 覆盖、定位和引文。complete 表示标注记录完整，不保证模型的分类或推断正确。", "",
              "助手复核尚待逐例完成，记录应另外保存为 assistant-review.md；本自动报告不冒充人工确认。重点检查模型观察、多主体／多角色、网络双向效果及声明与实际变换的区别。", "",
              "源包内的可读代码只作为文本提供，没有执行。二进制及未解释内容边界见逐例记录。", ""]
    return "\n".join(lines)


def execute(directory, *, mode="run", env_file=None, workers=None):
    from skillflow.propagation.annotation.runner import prepare_run
    from skillflow.propagation.annotation.runner import run_annotation
    from skillflow.propagation.annotation.runner import replay_run
    from skillflow.propagation.annotation.runner import verify_prepared
    if mode not in {"prepare", "run", "replay"}:
        raise ValueError("mode must be prepare, run or replay")
    if workers is not None and (type(workers) is not int or not 1 <= workers <= 8):
        raise ValueError("workers must be an integer from 1 through 8")
    if mode == "replay" and env_file is not None:
        raise ValueError("Offline replay does not read an environment file")
    directory = Path(directory).resolve()
    plan = build_plan()
    protected = [REPOSITORY_ROOT / "dataset", REPOSITORY_ROOT / "result", BASELINE]
    if any(directory == root or directory.is_relative_to(root) for root in protected):
        raise ValueError("Experiment outputs cannot overlap frozen inputs or existing delivery directories")
    if mode == "replay" and not (directory / "manifest.json").is_file():
        raise ValueError("Offline replay requires an existing experiment manifest")
    directory.mkdir(parents=True, exist_ok=True)
    stop_event = threading.Event()
    with exclusive_run(directory):
        prior = read_json(directory / "manifest.json") if (directory / "manifest.json").exists() else None
        if prior is not None and (prior.get("schema_version") != 6 or prior.get("identity") != IDENTITY
                                  or prior.get("profile_schema_version") != SCHEMA_VERSION):
            raise ValueError("Unsupported security-profile experiment version; use a new directory")
        selected_workers = workers if workers is not None else (prior["workers"] if prior else 3)
        config = prior["config"] if mode == "replay" else public_config()
        # No client or credentials are needed to validate provenance or prepare all cases.
        writer = ArtifactWriter(())
        manifest = _verified_manifest(directory, plan, config, selected_workers, writer)
        outcomes = {}
        ready = []
        output = directory / "replay" if mode == "replay" else directory
        prior_outcomes = {}
        if mode == "replay":
            if (directory / "experiment-result.json").exists():
                prior_outcomes = read_json(directory / "experiment-result.json").get("cases", {})
            elif (directory / "progress.json").exists():
                prior_outcomes = read_json(directory / "progress.json")

        def save_progress():
            writer.json(output / "progress.json", {key: outcomes[key] for key in sorted(outcomes)})

        for case in manifest["cases"]:
            identifier = case["case_id"]
            if stop_event.is_set():
                outcomes[identifier] = _missing("not_run", "此前已中断，未启动后续案例")
                continue
            case_dir = directory / case["run_dir"]
            try:
                if mode == "replay":
                    if not (case_dir / "manifest.json").exists():
                        outcomes[identifier] = _missing("not_run", "不存在可重放的案例清单")
                        continue
                    if (prior_outcomes.get(identifier, {}).get("status") == "not_run"
                            and not any((case_dir / "calls").rglob("call.json"))):
                        verify_prepared(case_dir, config=config, replay=True)
                        outcomes[identifier] = prior_outcomes[identifier]
                        continue
                    print(f"{identifier} {case['sample_id']}：离线重放", flush=True)
                    outcomes[identifier] = replay_run(case_dir)
                    # Replay every saved case, including calls that were already
                    # running when another case interrupted the live scheduler.
                else:
                    if (case_dir / "manifest.json").exists():
                        prepared = verify_prepared(case_dir, config=config)
                    else:
                        prepared = prepare_run(resolve_material_path(case["package_path"], base=REPOSITORY_ROOT), resolve_material_path(case["analysis_path"], base=REPOSITORY_ROOT),
                                               run_dir=case_dir, config=config)
                    if prepared["preparation_status"] != "ready":
                        outcomes[identifier] = read_json(case_dir / "result.json") if (case_dir / "result.json").exists() else _missing(
                            "input_error", prepared.get("preparation_error", "输入准备失败"))
                    elif mode == "prepare":
                        outcomes[identifier] = _missing("prepared", "输入、结构和模型材料已离线准备")
                    else:
                        ready.append(case)
            except KeyboardInterrupt:
                stop_event.set()
                outcomes[identifier] = _missing("interrupted", "用户中断；后续案例不启动")
            except Exception as error:
                outcomes[identifier] = _missing("input_error" if mode != "replay" else "execution_error",
                                                f"{type(error).__name__}: {error}")
            save_progress()

        if mode == "run" and ready and not stop_event.is_set():
            from skillflow.common.recording import streaming_factory
            factory, secrets = streaming_factory(config, env_file=env_file)
            writer = ArtifactWriter(secrets)

            def work(case):
                identifier = case["case_id"]
                if stop_event.is_set():
                    return _missing("not_run", "此前已中断，未启动后续案例")
                print(f"{identifier} {case['sample_id']}：开始唯一标注调用", flush=True)
                try:
                    outcome = run_annotation(directory / case["run_dir"], client_factory=factory, config=config,
                                             secrets=secrets, stop_event=stop_event,
                                             progress=lambda message: print(f"{identifier}：{message}", flush=True))
                    if outcome["status"] == "interrupted":
                        stop_event.set()
                    return outcome
                except KeyboardInterrupt:
                    stop_event.set()
                    return _missing("interrupted", "用户中断；已开始调用保存在案例目录中")
                except Exception as error:
                    return _missing("execution_error", writer.clean(f"{type(error).__name__}: {error}"))

            remaining = iter(ready)
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
                        save_progress()
                        continue
                    for future in finished:
                        case = pending.pop(future)
                        outcomes[case["case_id"]] = future.result()
                        save_progress()
                    fill()
        for case in manifest["cases"]:
            if case["case_id"] not in outcomes:
                outcomes[case["case_id"]] = _missing("not_run", "此前已中断，未启动后续案例")
        outcomes = {case["case_id"]: outcomes[case["case_id"]] for case in manifest["cases"]}
        result = {"schema_version": 6, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION, "mode": mode, "cases": outcomes,
                  "summary": _summary(outcomes), "assistant_review": "pending", "user_confirmed": False}
        writer.json(output / "experiment-result.json", result)
        writer.text(output / "report.md", experiment_report(result, manifest))
        save_progress()
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "run", "replay"):
        command = commands.add_parser(name)
        command.add_argument("--run-dir", type=Path, required=True)
        if name != "replay":
            command.add_argument("--workers", type=int, default=None, help="并行案例上限，首次默认 3；恢复须保持一致")
        if name == "run":
            command.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    result = execute(args.run_dir, mode=args.command, env_file=getattr(args, "env_file", None),
                     workers=getattr(args, "workers", None))
    print(json.dumps(result["summary"], ensure_ascii=False), flush=True)
    errors = {"input_error", "invalid_response", "execution_error", "semantic_failure", "interrupted", "not_run"}
    return int(any(case["status"] in errors for case in result["cases"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
