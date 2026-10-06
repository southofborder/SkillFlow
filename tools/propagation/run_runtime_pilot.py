"""Three pinned existing CFGs: one joint annotation each, then offline propagation.

The historical selection is checked as provenance, never reinterpreted using a
new semantic or annotation contract. No extraction or feedback service is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
import sys
from threading import Event

from skillflow.common.paths import project_root, resolve_material_path

PACKAGE = project_root()
ROOT = project_root()

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import now
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import streaming_factory
from skillflow.propagation.contracts.runtime_contract import execution_model
from skillflow.propagation.contracts.runtime_contract import execution_model_binding
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION as PROFILE_VERSION
from skillflow.propagation.annotation.config import annotation_config
from skillflow.propagation.annotation.runner import prepare_run
from skillflow.propagation.annotation.runner import run_annotation
from skillflow.propagation.annotation.runner import replay_run
from skillflow.propagation.annotation.runner import verify_prepared
from skillflow.propagation.annotation.runner import _counts as annotation_counts
from skillflow.propagation.runner import load_propagation_run
from skillflow.propagation.runner import run_propagation
from skillflow.propagation.runner import replay_propagation
from skillflow.graph.artifacts.analysis_json import load_analysis_cfg
from skillflow.graph.artifacts.mermaid import render_mermaid
import json

IDENTITY = "skill-ir-processing-pilot3-v4"
FORMAT_VERSION = 4
ORIGIN = PACKAGE / "experiments/propagation/runs/source-boundaries-v1-20260928-112118"
PINS = {
    "001": {"sample_id": "N01", "revision": 2,
            "package_bytes_sha256": "b2711f0818fec26693097dca06b9d5b10bdfbda5763cfdda2e47fe022efeb782",
            "source_sha256": "6c0561338e81f9706b4a30b1f9ed4fffac663c7f7bb3a144e01a8f2a8e1c59ab",
            "graph_sha256": "494d8330cd4f0f9fca0171b45a40d3dc4d082f9bb16cdc450e79edcaeb03a7e2",
            "analysis_sha256": "e4dc09d5e597c4ce87634343aa8e4aae9b0150a39122b584eb887ec3e94fcddc",
            "selection_sha256": "058005caac8f3069c7f0df3bb5353a534c3550215bfdba782382cb3cb0278c02"},
    "010": {"sample_id": "Q04", "revision": 0,
            "package_bytes_sha256": "98e3b818265587ee4b04b566e9280a08b110512610c054500a7d4174929951a0",
            "source_sha256": "66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c",
            "graph_sha256": "cdce0c44bb6531ac4058788c2510029e079e628fec77e691e7b54d24d2e59144",
            "analysis_sha256": "1812750e77d42599058579cc295595b237c2a390d93a7677d4f2bd32d1c3e58e",
            "selection_sha256": "365872ca9a9bde370a9db64ca024c7a77b51f20f15b6efa3a043427ddbcd72fe"},
    "013": {"sample_id": "F01", "revision": 0,
            "package_bytes_sha256": "05262444daaee62622a2b7b745611bba60f0cf5e13a733d81e4da773e58d9ea2",
            "source_sha256": "fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da",
            "graph_sha256": "47c39ad7606ed9050aedf8b5322768a40b32a22abca1b762acdc7e4ea66a5244",
            "analysis_sha256": "0eec4c18ca72bef85f00366e598ebcefa0e53e0b0d32272d301def8efd4e5489",
            "selection_sha256": "806a44b5db93af9d89278638872d5cb542d8e2cc4c43690ad8a70ea6de59a757"},
}
POLICY = {"extract_cfg": False, "feedback_calls": 0, "planned_logical_calls": 3,
          "annotation_calls_per_case": 1, "propagation_calls": 0, "workers": 1,
          "automatic_quality_rerun": False, "uncertain_request_automatic_resend": False}


def plan():
    """Verify raw historical inputs without loading their old model responses."""
    prior_manifest = read_json(ORIGIN / "manifest.json")
    if prior_manifest.get("identity") != "skill-ir-source-boundaries-pilot3-v1":
        raise ValueError("unexpected historical input run identity")
    prior_cases = {case["case_id"]: case for case in prior_manifest["cases"]}
    if len(prior_manifest["cases"]) != 3 or set(prior_cases) != set(PINS):
        raise ValueError("historical input case inventory differs")
    cases = []
    for number, pin in PINS.items():
        base = ORIGIN / "cases" / number
        analysis, selection = base / "selected-analysis.json", base / "selection.json"
        selected = read_json(selection)
        cfg = read_json(analysis)["cfg"]
        _, source, metadata = read_snapshot(base / "source")
        round_cfg = base / "feedback/rounds" / f"r{pin['revision']:03d}" / "cfg.json"
        prior = prior_cases[number]
        inventory = {item["path"]: {"bytes": item["size"], "sha256": item["raw_sha256"]}
                     for item in metadata["files"]}
        if (sha_file(analysis) != pin["analysis_sha256"]
                or sha_file(selection) != pin["selection_sha256"]
                or canonical_sha256(cfg) != pin["graph_sha256"]
                or read_json(round_cfg) != cfg
                or selected["revision"] != pin["revision"]
                or selected["graph_sha256"] != pin["graph_sha256"]
                or selected["source_sha256"] != pin["source_sha256"]
                or source["source_sha256"] != pin["source_sha256"]
                or metadata["package_bytes_sha256"] != pin["package_bytes_sha256"]
                or prior["source_sha256"] != pin["source_sha256"]
                or inventory != prior["source_inventory"]
                or metadata["package_bytes_sha256"] != prior["package_bytes_sha256"]):
            raise ValueError("historical source/selection/graph binding differs: " + number)
        cases.append({"case_id": number, **pin, "input": str(base / "source/inputs/package"),
                      "analysis": str(analysis), "selection": str(selection),
                      "source_inventory": inventory, "package_bytes_sha256": metadata["package_bytes_sha256"],
                      "prior_feedback_status": selected["feedback_status"],
                      "historical_round_cfg": str(round_cfg), "historical_round_cfg_sha256": sha_file(round_cfg)})
    return cases


def public_config():
    variant = read_json(PACKAGE / "experiments/graph/baseline/deepseek-v4-flash.json")["variants"][0]
    value = {key: variant[key] for key in ("endpoint", "model", "reasoning_effort", "timeout_ms",
                                          "max_retries", "retry_base_ms", "retry_max_backoff_ms")}
    value["timeout_ms"] = 600000
    if value["endpoint"] != "https://api.deepseek.com/chat/completions" or value["model"] != "deepseek-v4-flash":
        raise ValueError("pilot requires the official pinned DeepSeek endpoint and model")
    return annotation_config(value)


def expected_manifest():
    return {"schema_version": FORMAT_VERSION, "identity": IDENTITY, "profile_schema_version": PROFILE_VERSION,
            "execution_model": execution_model_binding(execution_model()), "cases": plan(),
            "config": public_config(), "implementation": implementation_provenance(),
            "driver_sha256": sha_file(Path(__file__)), "policy": POLICY}


def checked_output(path):
    directory = Path(path).resolve()
    protected = [ROOT / "dataset", ROOT / "result", PACKAGE / "src", ORIGIN]
    if any(directory == p or directory.is_relative_to(p) or p.is_relative_to(directory) for p in protected):
        raise ValueError("pilot output overlaps protected inputs, historical run or source")
    if not directory.name.startswith("processing-v1-"):
        raise ValueError("new pilot directory must start with processing-v1-")
    return directory


def verify_case(directory, case, config):
    base = directory / "cases" / case["case_id"]
    if sha_file(base / "selected-analysis.json") != case["analysis_sha256"]:
        raise ValueError("selected analysis copy changed")
    if sha_file(base / "selection.json") != case["selection_sha256"]:
        raise ValueError("historical selection copy changed")
    manifest = verify_prepared(base / "annotation", config=config, replay=True)
    _, source, metadata = read_snapshot(base / "annotation")
    inventory = {item["path"]: {"bytes": item["size"], "sha256": item["raw_sha256"]}
                 for item in metadata["files"]}
    if (manifest["preparation_status"] != "ready" or manifest["graph_sha256"] != case["graph_sha256"]
            or source["source_sha256"] != case["source_sha256"]
            or metadata["package_bytes_sha256"] != case["package_bytes_sha256"]
            or inventory != case["source_inventory"]):
        raise ValueError("new annotation differs from pinned source and CFG")


def verify_prepare_skeleton(directory, cases):
    """Accept only an empty directory or a deliberately cleaned frozen skeleton.

    This function never removes files. Accepted calls/results/manifests cannot
    be mistaken for permission to overwrite a prior run.
    """
    existing = [path for path in directory.iterdir() if path.name != ".runner.lock"]
    if not existing:
        return
    if {path.name for path in existing} != {"cases"}:
        raise ValueError("prepare requires a new empty directory or only the verified frozen CFG skeleton")
    expected = {case["case_id"]: case for case in cases}
    case_root = directory / "cases"
    if not case_root.is_dir() or {path.name for path in case_root.iterdir()} != set(expected):
        raise ValueError("refreshed case inventory differs from pinned cases")
    for path in [case_root, *case_root.rglob("*")]:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
        if path.is_symlink() or attributes & 0x400:
            raise ValueError("prepare must not follow links or reparse points")
    for identifier, case in expected.items():
        base = case_root / identifier
        names = {path.name for path in base.iterdir()}
        if not {"selected-analysis.json", "selection.json"} <= names <= {
                "selected-analysis.json", "selection.json", "cfg-review.md"}:
            raise ValueError("refresh still contains previous calls, results or unrecognized files")
        if any(not path.is_file() for path in base.iterdir()):
            raise ValueError("refresh skeleton may contain only frozen files")
        if (sha_file(base / "selected-analysis.json") != case["analysis_sha256"]
                or sha_file(base / "selection.json") != case["selection_sha256"]):
            raise ValueError("retained source selection or CFG differs from pinned inputs")


def prepare(directory):
    directory = checked_output(directory)
    expected = expected_manifest()
    directory.mkdir(parents=True, exist_ok=True)
    writer = ArtifactWriter(())
    with exclusive_run(directory):
        verify_prepare_skeleton(directory, expected["cases"])
        for case in expected["cases"]:
            base = directory / "cases" / case["case_id"]
            base.mkdir(parents=True, exist_ok=True)
            for name, original in (("selected-analysis.json", case["analysis"]), ("selection.json", case["selection"])):
                if not (base / name).exists():
                    (base / name).write_bytes(Path(original).read_bytes())
            manifest = prepare_run(case["input"], base / "selected-analysis.json", run_dir=base / "annotation",
                                   config=expected["config"])
            if manifest["preparation_status"] != "ready":
                raise ValueError("annotation preparation failed: " + str(manifest["preparation_error"]))
            verify_case(directory, case, expected["config"])
            graph = load_analysis_cfg(base / "selected-analysis.json")
            lines = ["# 当前冻结 CFG：" + case["case_id"], "",
                     "本图直接读取选定的 analysis.json，不增加传播层的处理段、观察或逐元素回边。", "",
                     "```mermaid", render_mermaid(graph), "```", "",
                     "## 原始操作及限制", ""]
            for block in graph.blocks.values():
                for instruction in block.instructions:
                    lines += ["### " + instruction.id, "", "```json",
                              json.dumps(instruction.model_dump(mode="json"), ensure_ascii=False, indent=2), "```", ""]
            writer.text(base / "cfg-review.md", "\n".join(lines))
        # Commit only a complete offline preparation.
        expected = {**expected, "prepared_at": now()}
        writer.json(directory / "manifest.json", expected)
        summarize(directory, writer)
    return expected


def _missing():
    return {"status": "not_run", "reason": "未启动模型调用。", "counts": {"logical_calls": 0, "http_attempts": 0}}


def run_case(directory, case, *, config, factory, secrets, stopping, replay=False):
    base = directory / "cases" / case["case_id"]
    annotation_dir = base / "annotation"
    writer = ArtifactWriter(secrets)
    outcome_path = base / ("replay/result.json" if replay else "result.json")
    call_exists = (annotation_dir / "calls/annotation/a001/call.json").exists()
    old_result = read_json(annotation_dir / "result.json") if (annotation_dir / "result.json").exists() else None
    if replay and old_result is None and not call_exists:
        annotation = _missing()
    elif replay or (old_result and old_result["status"] in {"input_error", "execution_error", "invalid_response", "semantic_failure"} and not call_exists):
        # A recorded local failure is not a reason to start a fresh request.
        annotation = replay_run(annotation_dir)
    else:
        annotation = run_annotation(annotation_dir, client_factory=factory, config=config, secrets=secrets,
                                    stop_event=stopping, progress=lambda text: print(case["case_id"], text, flush=True))
    if annotation["status"] == "interrupted":
        stopping.set()
    outcome = {"annotation": annotation, "propagation": "not_run", "propagation_error": None}
    writer.json(outcome_path, outcome)
    propagation_dir = base / "propagation"
    if annotation["status"] in {"complete"} and (replay or not stopping.is_set()):
        try:
            if (propagation_dir / "manifest.json").exists():
                doe = replay_propagation(propagation_dir) if replay else load_propagation_run(propagation_dir)
            elif replay:
                raise ValueError("no committed propagation run; offline replay cannot create one")
            else:
                doe = run_propagation(annotation_dir, run_dir=propagation_dir)
            outcome["propagation"] = doe["status"]
        except Exception as error:
            outcome.update(propagation="execution_error", propagation_error=writer.clean(f"{type(error).__name__}: {error}"))
        writer.json(outcome_path, outcome)
    return outcome


def summarize(directory, writer, *, replay=False):
    manifest = read_json(directory / "manifest.json")
    rows = []
    for case in manifest["cases"]:
        base = directory / "cases" / case["case_id"]
        saved = base / ("replay/result.json" if replay else "result.json")
        annotation_result = base / "annotation" / ("replay/result.json" if replay else "result.json")
        outcome = read_json(saved) if saved.exists() else {
            "annotation": read_json(annotation_result) if annotation_result.exists() else _missing(), "propagation": "not_run"}
        annotation = outcome["annotation"]
        failure_path = base / ("replay/driver-error.json" if replay else "driver-error.json")
        failure = read_json(failure_path) if failure_path.exists() else None
        driver_path = base / ("replay/driver-status.json" if replay else "driver-status.json")
        driver_status = read_json(driver_path) if driver_path.exists() else {"status": "not_run"}
        row = {"case_id": case["case_id"], "sample_id": case["sample_id"],
               "annotation": annotation["status"], "annotation_reason": annotation.get("reason"),
               "propagation": outcome["propagation"], "propagation_error": outcome.get("propagation_error"),
               "driver_status": driver_status["status"], "driver_error": failure,
               "counts": annotation_counts(base / "annotation"),
               "partial_order_ir_ids": [key for key, spec in annotation.get("transfer_specs", {}).items() if spec.get("order") == "partial"]}
        rows.append(row)
    summary = {"identity": IDENTITY, "execution_model": manifest["execution_model"], "mode": "replay" if replay else "run",
               "cases": rows, "logical_calls": sum(row["counts"].get("logical_calls", 0) for row in rows),
               "http_attempts": sum(row["counts"].get("http_attempts", 0) for row in rows),
               "annotation_statuses": dict(Counter(row["annotation"] for row in rows)),
               "propagation_statuses": dict(Counter(row["propagation"] for row in rows))}
    output, prefix = (directory / "replay", "../") if replay else (directory, "")
    writer.json(output / "summary.json", summary)
    notice = "这是统一契约下的静态可能行为，不是执行日志。复用冻结源包和既有 CFG；每例一次联合标注，传播和重放零 API。完成不证明标注正确或不存在 DOE。"
    lines = ["# 字段关系与观察编译：三例复测", "", notice, "", "契约：`" + manifest["execution_model"]["version"] + "`。", "",
             "| 样例 | 调度 | 标注 | 传播 | 逻辑调用 | 审查材料 |", "|---|---|---|---|---:|---|"]
    html = ["<h1>字段关系与观察编译：三例复测</h1><p>" + notice + "</p><p>契约：" + escape(manifest["execution_model"]["version"]) + "</p>",
            "<table><tr><th>样例</th><th>调度</th><th>标注</th><th>传播</th><th>逻辑调用</th><th>审查材料</th></tr>"]
    error_lines = []
    for row in rows:
        number = row["case_id"]
        links, html_links = [], []
        for relative, title in ((f"cases/{number}/selected-analysis.json", "既有 CFG"),
                                (f"cases/{number}/cfg-review.md", "CFG 图与动作详情"),
                                (f"cases/{number}/annotation/report.md", "联合标注"),
                                (f"cases/{number}/annotation/audit/raw-annotation.json", "原始处理段"),
                                (f"cases/{number}/annotation/audit/compilation-map.json", "观察编译映射"),
                                (f"cases/{number}/propagation/doe-input.json", "DOE 原始事实"),
                                (f"cases/{number}/propagation/report.html", "传播审查"),
                                (f"cases/{number}/assistant-review.md", "助手复核")):
            if "/propagation/" in relative and not (directory / "cases" / number / "propagation/manifest.json").exists():
                continue
            if (directory / relative).exists():
                links.append(f"[{title}]({prefix}{relative})")
                html_links.append(f"<a href='{prefix}{relative}'>{title}</a>")
        counts = row["counts"].get("logical_calls", 0)
        lines.append(f"| {number} / {row['sample_id']} | {row['driver_status']} | {row['annotation']} | {row['propagation']} | {counts} | {' · '.join(links)} |")
        html.append(f"<tr><td>{number} / {row['sample_id']}</td><td>{escape(row['driver_status'])}</td><td>{escape(row['annotation'])}</td><td>{escape(row['propagation'])}</td><td>{counts}</td><td>{' · '.join(html_links)}</td></tr>")
        if row["driver_error"]:
            message = row["driver_error"]["error"]
            error_lines.append(f"{number} 调度记录：{message}")
            html.append("<tr><td colspan='6'>调度记录：" + escape(message) + "</td></tr>")
    lines += ["", *error_lines, "", "重点核对：筛选是否保留成员原值；同一元素的接收者和正文是否配对；原始处理段及程序生成的观察；局部机制及观察版本是否正确。", "",
              "本次最多三次计划内逻辑模型调用；HTTP 传输尝试另计。未决、无效响应和助手发现的错误均保留，不按质量补跑。", ""]
    html.append("</table><p><a href='summary.json'>完整状态</a> · <a href='report.md'>中文报告</a></p>")
    writer.text(output / "report.md", "\n".join(lines))
    writer.text(output / "index.html", "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>观察编译三例复测</title><style>body{font:16px/1.6 'Microsoft YaHei',sans-serif;max-width:1200px;margin:40px auto}td,th{padding:12px;border:1px solid #ccc}table{border-collapse:collapse}a{color:#176ac1}</style><body>" + "".join(html) + "</body></html>")
    return summary


def execute(directory, *, replay=False, env_file=None, client_factory=None, secrets=()):
    directory = checked_output(directory)
    expected = expected_manifest()
    saved = read_json(directory / "manifest.json")
    prepared_at = saved.pop("prepared_at", None)
    if not isinstance(prepared_at, str) or datetime.fromisoformat(prepared_at).tzinfo is None:
        raise ValueError("pilot preparation timestamp missing or invalid")
    if saved != expected:
        raise ValueError("pilot source/config/contract/implementation identity changed")
    if replay and (env_file is not None or client_factory is not None):
        raise ValueError("offline replay does not accept environment files or online clients")
    with exclusive_run(directory):
        for case in expected["cases"]:
            verify_case(directory, case, expected["config"])
        if not replay and client_factory is None:
            client_factory, secrets = streaming_factory(expected["config"], env_file=env_file)
        writer, stopping = ArtifactWriter(tuple(secrets)), Event()
        for case in expected["cases"]:
            if stopping.is_set() and not replay:
                break
            base = directory / "cases" / case["case_id"]
            stage_output = base / "replay" if replay else base
            try:
                writer.json(stage_output / "driver-status.json", {"status": "running"})
                if replay:
                    stopping.clear()
                outcome = run_case(directory, case, config=expected["config"], factory=None if replay else client_factory,
                                   secrets=tuple(secrets), stopping=stopping, replay=replay)
                writer.json(stage_output / "driver-status.json", {"status": "interrupted" if outcome["annotation"]["status"] == "interrupted" else "completed"})
            except KeyboardInterrupt as error:
                stopping.set()
                writer.json(stage_output / "driver-status.json", {"status": "interrupted"})
                writer.json(stage_output / "driver-error.json", {"error": writer.clean(f"KeyboardInterrupt: {error}")})
            except Exception as error:
                writer.json(stage_output / "driver-status.json", {"status": "execution_error"})
                writer.json(stage_output / "driver-error.json", {"error": writer.clean(f"{type(error).__name__}: {error}")})
                print(case["case_id"], "execution failure:", writer.clean(str(error)), flush=True)
            summarize(directory, writer, replay=replay)
        result = summarize(directory, writer, replay=replay)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="001/010/013 既有图：统一契约下一次联合标注及离线传播，不重新建图")
    parser.add_argument("command", choices=["prepare", "run", "replay"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    if args.command != "run" and args.env_file is not None:
        raise ValueError("offline prepare/replay does not read environment files")
    if args.command == "prepare":
        prepare(args.run_dir)
        print("prepared 3 frozen CFGs; model calls: 0", flush=True)
        return 0
    result = execute(args.run_dir, replay=args.command == "replay", env_file=args.env_file)
    print("logical calls:", result["logical_calls"], result["annotation_statuses"], result["propagation_statuses"], flush=True)
    return 0 if all(row["driver_status"] == "completed" and row["annotation"] in {"complete"}
                    and row["propagation"] == "complete" for row in result["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
