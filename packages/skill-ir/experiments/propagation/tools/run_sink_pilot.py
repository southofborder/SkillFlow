"""Three verified base CFGs: one boundary annotation each and offline propagation.

The bootstrap receipt was made with the previous supported loaders before any
contract update. This driver consumes frozen bytes, never migrates old responses.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html import escape
from pathlib import Path
import sys
from threading import Event

PACKAGE = Path(__file__).resolve().parents[3]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE / "src"))

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.inputs.snapshot import read_snapshot
from skill_ir.recording import canonical_sha256, implementation_provenance, now, read_json, sha_file, streaming_factory
from skill_ir.runtime_contract import execution_model, execution_model_binding
from skill_ir.representation_contract import binding as representation_binding
from skill_ir.security_profile.models import SCHEMA_VERSION as PROFILE_VERSION
from skill_ir.security_profile.runner import prepare_run, verify_prepared, _counts

# Share the existing single-case dispatch, accepted-response and zero-API replay
# orchestration. Its historical plan()/output selection is never called here.
from run_runtime_pilot import public_config, run_case

IDENTITY = "skill-ir-sink-boundaries-pilot3-v1"
POLICY = {"planned_logical_calls": 3, "annotation_calls_per_case": 1,
          "extract_cfg": False, "feedback_calls": 0, "review_calls": 0,
          "propagation_calls": 0, "automatic_quality_rerun": False,
          "uncertain_request_automatic_resend": False}


def checked_directory(path):
    directory = Path(path).resolve()
    root = PACKAGE / "experiments/propagation/runs"
    if directory.parent != root.resolve() or not directory.name.startswith("sink-boundaries-v1-"):
        raise ValueError("sink pilot must use a new sink-boundaries-v1-* experiment directory")
    for item in [directory, *directory.rglob("*")]:
        if item.is_symlink() or getattr(item.lstat(), "st_file_attributes", 0) & 0x400:
            raise ValueError("sink pilot cannot follow links or reparse points")
    return directory


def inputs(directory):
    receipt = read_json(directory / "bootstrap.json")
    if receipt.get("status") != "verified" or receipt.get("model_calls") != 0:
        raise ValueError("previous-loader verification receipt missing")
    cases = receipt["cases"]
    if [(item["case_id"], item["sample_id"]) for item in cases] != [("001", "N01"), ("010", "Q04"), ("013", "F01")]:
        raise ValueError("frozen base case inventory differs")
    for case in cases:
        frozen = directory / "frozen" / case["case_id"]
        actual = {path.relative_to(frozen).as_posix(): sha_file(path)
                  for path in frozen.rglob("*") if path.is_file()}
        if actual != case["frozen_files"]:
            raise ValueError("frozen input bytes changed: " + case["case_id"])
        material = read_json(frozen / "material.json")
        if (canonical_sha256(read_json(frozen / "analysis.json")["cfg"]) != case["graph_sha256"]
                or canonical_sha256(material["cfg"]) != case["graph_sha256"]
                or material["source"]["source_sha256"] != case["source_sha256"]):
            raise ValueError("frozen source or graph binding differs")
        # The historical DOE is checked as unchanged bytes, not loaded under
        # this new format. Its successful prior load is in the receipt.
        if sha_file(Path(case["prior_run"]) / "propagation/doe-input.json") != case["prior_doe_sha256"]:
            raise ValueError("historical input changed since bootstrap")
    return receipt, cases


def expected_manifest(directory):
    receipt, cases = inputs(directory)
    return {"schema_version": 1, "identity": IDENTITY,
            "bootstrap_sha256": canonical_sha256(receipt), "cases": cases,
            "profile_schema_version": PROFILE_VERSION,
            "execution_model": execution_model_binding(execution_model()),
            "representation_contract": representation_binding(),
            "config": public_config(), "implementation": implementation_provenance(),
            "driver_sha256": sha_file(Path(__file__)),
            "shared_driver_sha256": sha_file(Path(__file__).with_name("run_runtime_pilot.py")),
            "policy": POLICY}


def verify_case(directory, case, config):
    base = directory / "cases" / case["case_id"]
    frozen = directory / "frozen" / case["case_id"]
    if sha_file(base / "selected-analysis.json") != case["frozen_files"]["analysis.json"]:
        raise ValueError("selected graph copy changed")
    manifest = verify_prepared(base / "annotation", config=config, replay=True)
    _, source, metadata = read_snapshot(base / "annotation")
    prior_metadata = read_json(frozen / "source-metadata.json")
    # The physical snapshot path changes; byte inventory and content identity
    # must remain identical. Each producer separately seals its actual path.
    package_fields = ("files", "package_bytes_sha256", "source_sha256", "boundaries", "storage", "archive_sha256")
    if (manifest["preparation_status"] != "ready"
            or manifest["graph_sha256"] != case["graph_sha256"]
            or source != read_json(frozen / "material.json")["source"]
            or any(metadata[key] != prior_metadata[key] for key in package_fields)):
        raise ValueError("new annotation is not bound to the frozen package and graph")


def prepare(directory):
    directory = checked_directory(directory)
    expected = expected_manifest(directory)
    with _exclusive_run(directory):
        names = {p.name for p in directory.iterdir() if p.name != ".runner.lock"}
        if names != {"bootstrap.json", "frozen"}:
            raise ValueError("prepare needs only the verified bootstrap and frozen inputs")
        for case in expected["cases"]:
            frozen = directory / "frozen" / case["case_id"]
            base = directory / "cases" / case["case_id"]
            base.mkdir(parents=True)
            (base / "selected-analysis.json").write_bytes((frozen / "analysis.json").read_bytes())
            prepare_run(frozen / "package", base / "selected-analysis.json",
                        run_dir=base / "annotation", config=expected["config"])
            verify_case(directory, case, expected["config"])
        ArtifactWriter(()).json(directory / "manifest.json", {**expected, "prepared_at": now()})
        return summarize(directory)


def summarize(directory, *, replay=False):
    manifest = read_json(directory / "manifest.json")
    writer, rows = ArtifactWriter(()), []
    for case in manifest["cases"]:
        base = directory / "cases" / case["case_id"]
        path = base / ("replay/result.json" if replay else "result.json")
        result = read_json(path) if path.exists() else {"annotation": {"status": "not_run"}, "propagation": "not_run"}
        doe_path = base / "propagation/doe-input.json"
        committed = (base / "propagation/manifest.json").exists()
        doe = read_json(doe_path) if committed else {}
        rows.append({"case_id": case["case_id"], "sample_id": case["sample_id"],
                     "annotation": result["annotation"]["status"], "annotation_reason": result["annotation"].get("reason"),
                     "propagation": result["propagation"], "propagation_error": result.get("propagation_error"),
                     "sink_count": len(doe.get("sink_boundaries", [])),
                     "sink_types": dict(Counter(sink["sink_type"] for sink in doe.get("sink_boundaries", []))),
                     "counts": _counts(base / "annotation")})
    summary = {"identity": IDENTITY, "mode": "replay" if replay else "run", "cases": rows,
               "logical_calls": sum(row["counts"].get("logical_calls", 0) for row in rows),
               "http_attempts": sum(row["counts"].get("http_attempts", 0) for row in rows),
               "annotation_statuses": dict(Counter(row["annotation"] for row in rows)),
               "propagation_statuses": dict(Counter(row["propagation"] for row in rows))}
    target, prefix = (directory / "replay", "../") if replay else (directory, "")
    notice = "本次只使用冻结源文和既有 CFG，每例一次联合标注；sink 类型和等级由程序生成，传播及重放不调用 API。等级不是敏感度、必要性或 DOE 结论；任务内部等级 0 和删除仍保留传播关系。"
    lines = ["# Sink 边界三例验证", "", notice, "", "| 样例 | 标注 | 传播 | Sink 位置 | 逻辑调用 | 审查入口 |", "|---|---|---|---:|---:|---|"]
    html = ["<h1>Sink 边界三例验证</h1><p>" + notice + "</p>", "<table><tr><th>样例</th><th>标注</th><th>传播</th><th>Sink 位置</th><th>调用</th><th>审查入口</th></tr>"]
    for row in rows:
        number = row["case_id"]
        links = []
        for name, title in (("selected-analysis.json", "既有 CFG"), ("annotation/report.md", "标注和位置属性"),
                            ("annotation/audit/raw-annotation.json", "原始响应"), ("annotation/sink-boundaries.json", "编译 sink 清单"),
                            ("propagation/report.html", "数据与边界审查"), ("propagation/doe-input.json", "DOE 原始事实"),
                            ("assistant-review.md", "助手复核")):
            if (directory / "cases" / number / name).is_file() and (not name.startswith("propagation/") or (directory / "cases" / number / "propagation/manifest.json").is_file()):
                links.append((prefix + "cases/" + number + "/" + name, title))
        cells = [number + " / " + row["sample_id"], row["annotation"], row["propagation"], str(row["sink_count"]), str(row["counts"].get("logical_calls", 0))]
        lines.append("| " + " | ".join(cells + [" · ".join(f"[{title}]({path})" for path, title in links)]) + " |")
        html.append("<tr>" + "".join("<td>" + escape(cell) + "</td>" for cell in cells) + "<td>" + " · ".join('<a href="' + escape(path, quote=True) + '">' + title + '</a>' for path, title in links) + "</td></tr>")
        reason = row["annotation_reason"] or row["propagation_error"]
        if reason:
            lines += ["", number + "：" + str(reason).replace("\n", " ")]
            html.append('<tr><td colspan="6">' + escape(number + "：" + str(reason)) + '</td></tr>')
    lines += ["", "审查表分别展示纳入／排除、位置范围与留存、固定等级、当前操作的数据版本。工具默认 recipient 是契约保留的外部接收可能性，不是已测得的网络事实。", ""]
    writer.json(target / "summary.json", summary)
    writer.text(target / "report.md", "\n".join(lines))
    writer.text(target / "index.html", '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sink 边界三例验证</title><style>body{font:16px/1.7 "Microsoft YaHei",sans-serif;max-width:1400px;margin:32px auto;padding:20px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd7df;padding:12px;overflow-wrap:anywhere}a{color:#09667a}</style><body>' + "".join(html) + '</table><p><a href="summary.json">调用与状态</a> · <a href="report.md">中文报告</a></p></body></html>')
    return summary


def execute(directory, *, replay=False, env_file=None):
    directory = checked_directory(directory)
    saved = read_json(directory / "manifest.json")
    expected = expected_manifest(directory)
    if not saved.get("prepared_at") or {key: value for key, value in saved.items() if key != "prepared_at"} != expected:
        raise ValueError("sink pilot input/config/implementation identity changed")
    if replay and env_file is not None:
        raise ValueError("offline replay cannot read credentials")
    with _exclusive_run(directory):
        for case in expected["cases"]:
            verify_case(directory, case, expected["config"])
        factory, secrets = (None, ()) if replay else streaming_factory(expected["config"], env_file=env_file)
        stopping = Event()
        for case in expected["cases"]:
            if stopping.is_set() and not replay:
                break
            try:
                run_case(directory, case, config=expected["config"], factory=factory,
                         secrets=secrets, stopping=stopping, replay=replay)
            except KeyboardInterrupt:
                stopping.set()
                raise
            except Exception as error:
                base = directory / "cases" / case["case_id"]
                ArtifactWriter(secrets).json(base / ("replay/driver-error.json" if replay else "driver-error.json"),
                                            {"error": f"{type(error).__name__}: {error}"})
                print(case["case_id"], "driver failure:", type(error).__name__, flush=True)
            summarize(directory, replay=replay)
        return summarize(directory, replay=replay)


def main(argv=None):
    parser = argparse.ArgumentParser(description="冻结三例：一次 sink 联合标注及离线传播，不重新建图")
    parser.add_argument("command", choices=["prepare", "run", "replay", "summarize"])
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    if args.command != "run" and args.env_file:
        raise ValueError("only online run accepts an environment file")
    result = prepare(args.run_dir) if args.command == "prepare" else summarize(args.run_dir) if args.command == "summarize" else execute(args.run_dir, replay=args.command == "replay", env_file=args.env_file)
    print(result["logical_calls"], result["annotation_statuses"], result["propagation_statuses"], flush=True)
    return 0 if args.command in {"prepare", "summarize"} or all(row["annotation"] == "complete" and row["propagation"] == "complete" for row in result["cases"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
