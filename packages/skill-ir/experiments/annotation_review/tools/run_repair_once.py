"""Seven bounded annotation repairs and three single CFG audits; no extraction."""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import sys
from threading import Event

PACKAGE = Path(__file__).resolve().parents[3]
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from repair_candidates import reconstruct, verify_prechange
from skill_ir.annotation_review.refinement import prepare_refinement_run, run_refinement, replay_refinement
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.feedback.runner import refine_skill, replay_run as replay_cfg
from skill_ir.inputs.snapshot import read_snapshot
from skill_ir.propagation.runner import save_propagation_run, run_propagation, replay_propagation, load_propagation_run
from skill_ir.propagation.solver import propagate
from skill_ir.recording import canonical_sha256, implementation_provenance, now, read_json, sha_file, streaming_factory
from skill_ir.security_profile.config import annotation_config
from skill_ir.security_profile.services import compile_response, to_payload

IDENTITY = "skill-ir-annotation-repair-pilot-v1"
CASE_IDS = ("001-base", "010-base", "013-base", "013-local", "013-field", "010-source", "001-version")
POLICY = {"max_logical_calls": 24, "review_cases": 7, "max_calls_per_review_case": 3,
          "cfg_audits": 3, "cfg_extractions": 0, "cfg_repairs": 0,
          "annotation_repairs_per_case": 1, "automatic_quality_rerun": False,
          "workers": 1, "automatic_resend_after_acceptance": False}


def public_config():
    variant = read_json(PACKAGE / "experiments/semantics_baseline/deepseek-v4-flash.json")["variants"][0]
    value = {key: variant[key] for key in ("endpoint", "model", "reasoning_effort", "timeout_ms",
                                         "max_retries", "retry_base_ms", "retry_max_backoff_ms")}
    value["timeout_ms"] = 600000
    if value["endpoint"] != "https://api.deepseek.com/chat/completions" or value["model"] != "deepseek-v4-flash":
        raise ValueError("Pilot requires the pinned official DeepSeek configuration")
    return annotation_config(value)


def implementation():
    return {"package": implementation_provenance(), "driver": sha_file(Path(__file__)),
            "fixtures": sha_file(Path(__file__).with_name("repair_candidates.py"))}


def _seal(value):
    return {**value, "manifest_sha256": canonical_sha256(value)}


def checked_run(path):
    directory = Path(path).resolve()
    allowed = PACKAGE / "experiments/annotation_review/runs"
    if directory.parent != allowed or not directory.name.startswith("repair-once-v1-"):
        raise ValueError("Pilot directory must be a new repair-once-v1-* child of annotation_review/runs")
    return directory


def manifest(directory):
    value = read_json(directory / "manifest.json")
    unsigned = {key: item for key, item in value.items() if key != "manifest_sha256"}
    if (value.get("identity") != IDENTITY or canonical_sha256(unsigned) != value.get("manifest_sha256")
            or value.get("implementation") != implementation() or value.get("policy") != POLICY
            or value.get("config") != public_config()):
        raise ValueError("Pilot implementation, policy, configuration or identity changed")
    verify_prechange(directory)
    for relative, digest in value["prepared_files"].items():
        if sha_file(directory / relative) != digest:
            raise ValueError("Pilot reconstruction material changed: " + relative)
    return value


def prepare(directory):
    directory = checked_run(directory)
    if (directory / "manifest.json").exists():
        raise ValueError("Pilot already prepared; accepted runs are never recreated")
    candidates = reconstruct(directory)
    writer = ArtifactWriter(())
    with _exclusive_run(directory):
        allowed = {"upstream", "upstream-verification.json", ".runner.lock"}
        if set(p.name for p in directory.iterdir()) - allowed:
            raise ValueError("Preparation requires only the pre-change frozen inputs")
        expectations, files = {}, {}
        for sample in ("001", "010", "013"):
            item = next(c for c in candidates if c["case_id"] == sample + "-base")
            writer.json(directory / "selected" / (sample + ".json"), {"cfg": item["material"]["cfg"]})
        for item in candidates:
            key, sample = item["case_id"], item["sample"]
            prepare_refinement_run(directory / "upstream" / sample / "inputs/package",
                directory / "selected" / (sample + ".json"), item["material"], item["raw_annotation"],
                run_dir=directory / "cases" / key / "refinement", provenance=item["provenance"], config=public_config())
            writer.json(directory / "reconstruction" / (key + ".json"), item["provenance"])
            expectations[key] = item["expectation"]
        writer.json(directory / "evaluation/expectations.json", {
            "boundary": "仅用于调用后的受控缺陷评测，不进入模型输入；原始三例没有预设零问题答案。",
            "cases": expectations})
        for name in ("selected", "reconstruction", "evaluation"):
            files.update({p.relative_to(directory).as_posix(): sha_file(p)
                          for p in (directory / name).rglob("*") if p.is_file()})
        value = _seal({"identity": IDENTITY, "schema_version": 1, "created_at": now(),
                       "implementation": implementation(), "policy": POLICY, "config": public_config(),
                       "cases": list(CASE_IDS), "prepared_files": files})
        writer.json(directory / "manifest.json", value)
    summarize(directory)
    return value


def _selected_propagation(directory, key, result):
    case = directory / "cases" / key
    target = case / "propagation"
    refinement = case / "refinement"
    if (target / "manifest.json").exists():
        load_propagation_run(target)
        expected_raw = read_json(refinement / ("repair/audit/raw-annotation.json" if result["selected"] == "repair" else "inputs/candidate.json"))
        if (read_json(target / "audit/raw-annotation.json") != expected_raw
                or read_json(target / "audit/material.json") != read_json(refinement / "inputs/material.json")):
            raise ValueError("Saved propagation does not belong to the selected current candidate")
        return replay_propagation(target)
    if target.exists() and any(target.iterdir()):
        raise ValueError("Uncommitted propagation files exist; do not replace or pretend success")
    if result["selected"] == "repair":
        run_propagation(refinement / "repair", run_dir=target)
    else:
        material = read_json(refinement / "inputs/material.json")
        raw = read_json(refinement / "inputs/candidate.json")
        raw, compiled, mapping = compile_response(raw, material)
        payload = to_payload(compiled)
        solved = propagate(material["cfg"], payload)
        save_propagation_run(target, material=material, source_metadata=read_snapshot(refinement)[2],
            annotation=payload, location_evidences=compiled["location_evidences"], solved=solved,
            raw_annotation=raw, compilation_map=mapping,
            provenance={"kind": "hand_authored_specification", "candidate_origin": "explicit_reconstruction",
                        "candidate_sha256": canonical_sha256(raw),
                        "reconstruction": read_json(refinement / "inputs/provenance.json"),
                        "review_status": result["status"],
                        "notice": "最后有效原候选；并不表示已修复。"})
    return replay_propagation(target)


def run(directory, *, env_file=None, replay=False):
    directory = checked_run(directory)
    value = manifest(directory)
    writer, stopping = ArtifactWriter(()), Event()
    with _exclusive_run(directory):
        for key in CASE_IDS:
            case = directory / "cases" / key
            try:
                print(key + "：" + ("离线重放" if replay else "审查及最多一次修复"), flush=True)
                if replay:
                    result = replay_refinement(case / "refinement")
                else:
                    result = run_refinement(case / "refinement", env_file=env_file,
                        config=value["config"], stop_event=stopping,
                        progress=lambda message: print(key + " " + message, flush=True))
                if result["status"] == "interrupted":
                    stopping.set()
                if not stopping.is_set():
                    if replay:
                        if (case / "propagation/manifest.json").exists():
                            replay_propagation(case / "propagation")
                    else:
                        _selected_propagation(directory, key, result)
                writer.json(case / ("pilot-replay.json" if replay else "pilot-status.json"),
                            {"status": "completed", "refinement": result["status"], "selected": result["selected"]})
            except KeyboardInterrupt:
                stopping.set()
            except Exception as error:
                # Raw accepted calls stay in their own stage; this is a driver
                # failure, never a synthesized model response or quality rerun.
                writer.json(case / ("pilot-replay.json" if replay else "pilot-status.json"),
                            {"status": "driver_error", "reason": f"{type(error).__name__}: {error}"})
                print(key + " driver_error: " + str(error), flush=True)
            summarize(directory)
            if stopping.is_set():
                break
        if not stopping.is_set():
            for sample in ("001", "010", "013"):
                target = directory / "cfg-reviews" / sample
                print(sample + " CFG：" + ("离线重放" if replay else "单次核对，无提取与修复"), flush=True)
                try:
                    if replay:
                        replay_cfg(target)
                    else:
                        factory, secrets = streaming_factory(value["config"], env_file=env_file)
                        checked = refine_skill(directory / "upstream" / sample / "inputs/package",
                            run_dir=target, initial_analysis=directory / "selected" / (sample + ".json"),
                            max_semantic_revisions=0, max_audit_execution_retries=0,
                            audit_factory=factory, config=value["config"], secrets=secrets,
                            stop_event=stopping, progress=lambda text: print(sample + " CFG " + text, flush=True))
                        if checked["status"] == "interrupted":
                            stopping.set()
                        else:
                            replay_cfg(target)
                except KeyboardInterrupt:
                    stopping.set()
                except Exception as error:
                    writer.json(directory / "cfg-reviews" / (sample + "-driver-error.json"),
                                {"reason": f"{type(error).__name__}: {error}"})
                summarize(directory)
                if stopping.is_set():
                    break
    return summarize(directory)


def summarize(directory):
    directory, writer = Path(directory), ArtifactWriter(())
    rows, calls = [], 0
    for key in CASE_IDS:
        base = directory / "cases" / key
        result = read_json(base / "refinement/result.json") if (base / "refinement/result.json").exists() else {}
        counts = result.get("counts", {})
        calls += counts.get("logical_calls", 0)
        initial = (result.get("initial_review") or {}).get("review")
        final = (result.get("final_review") or {}).get("review")
        row = {"case": key, "status": result.get("status", "prepared"), "selected": result.get("selected"),
               "initial_issues": len(initial["findings"]) if initial else None,
               "final_issues": len(final["findings"]) if final else None,
               "logical_calls": counts.get("logical_calls", 0), "reason": result.get("reason", "尚未调用"),
               "propagation": None, "propagation_error": None}
        doe = base / "propagation/doe-input.json"
        if (base / "propagation/manifest.json").exists():
            try:
                row["propagation"] = load_propagation_run(base / "propagation")["status"]
            except Exception as error:
                row.update(propagation="invalid_run", propagation_error=str(error))
        elif doe.exists() or (base / "propagation").exists():
            row.update(propagation="uncommitted", propagation_error="传播保存未提交；不展示为成功结果")
        driver = base / "pilot-status.json"
        row["driver"] = read_json(driver) if driver.exists() else None
        rows.append(row)
    audits = []
    for sample in ("001", "010", "013"):
        path = directory / "cfg-reviews" / sample / "result.json"
        result = read_json(path) if path.exists() else {}
        counts = result.get("counts", {})
        n = counts.get("audit_logical_calls", counts.get("audit", 0))
        # Count actual saved requests independently of report field naming.
        n = len(list((directory / "cfg-reviews" / sample / "calls").rglob("call.json")))
        calls += n
        error = directory / "cfg-reviews" / (sample + "-driver-error.json")
        audits.append({"sample": sample, "status": result.get("status", "driver_error" if error.exists() else "prepared"),
                       "logical_calls": n, "driver_error": read_json(error) if error.exists() else None})
    if calls > POLICY["max_logical_calls"]:
        raise ValueError("Pilot call budget exceeded")
    summary = {"identity": IDENTITY, "cases": rows, "cfg_reviews": audits, "logical_calls": calls,
               "max_logical_calls": POLICY["max_logical_calls"]}
    writer.json(directory / "summary.json", summary)
    lines = ["# 一次标注修复与 CFG 核对", "", "新实验保留七份重建候选及各次真实响应；未执行 Skill，不作 DOE 判断。", "",
             f"已记录逻辑调用：{calls} / {POLICY['max_logical_calls']}。", "",
             "| 案例 | 闭环状态 | 初审问题 | 复审问题 | 选定候选 | 传播 | 调用 |", "|---|---|---:|---:|---|---|---:|"]
    html_rows = []
    for row in rows:
        key = row["case"]
        lines.append(f"| [{key}](cases/{key}/refinement/report.md) | {row['status']} | {row['initial_issues']} | {row['final_issues']} | {row['selected']} | {row['propagation']} | {row['logical_calls']} |")
        links = [(f"cases/{key}/refinement/report.html", "闭环报告")]
        if row["propagation"] and row["propagation"] not in {"uncommitted", "invalid_run"}:
            links += [(f"cases/{key}/propagation/report.html", "传播"), (f"cases/{key}/propagation/doe-input.json", "DOE 原始事实")]
        existing = [(url, label) for url, label in links if (directory / url).exists()]
        html_rows.append("<tr>" + "".join("<td>" + escape(str(row[name])) + "</td>" for name in
            ("case", "status", "initial_issues", "final_issues", "selected", "propagation", "logical_calls")) +
            "<td>" + " · ".join(f'<a href="{escape(url, quote=True)}">{escape(label)}</a>' for url, label in existing) + "</td></tr>")
    lines += ["", "## CFG 单次核对", "", *[f"- {row['sample']}：{row['status']}，{row['logical_calls']} 次调用。" for row in audits],
              "", "## 各例停止原因", "", *[f"- {row['case']}：{row['reason']}；传播诊断：{row['propagation_error'] or '无'}" for row in rows], "",
              "复审无问题仅表示核对器未提出实质问题。受控缺陷修复、误改及漏检由 assistant-review.md 另行复核。", ""]
    writer.text(directory / "report.md", "\n".join(lines))
    writer.text(directory / "index.html", '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>一次标注修复</title>'
        '<style>body{font-family:system-ui,"Microsoft YaHei",sans-serif;margin:2rem;line-height:1.6}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:.6rem;text-align:left}code{word-break:break-all}</style>'
        '<h1>一次标注修复与 CFG 核对</h1><p>静态契约分析，不是运行日志；核对器未报问题不等于已经证明正确。</p>'
        f'<p>逻辑调用：{calls} / 24。问题数量 None 表示该阶段没有合法审查结论。<a href="report.md">总报告</a> · <a href="summary.json">执行摘要</a> · <a href="assistant-review.md">助手复核</a></p>'
        '<table><thead><tr><th>案例</th><th>闭环状态</th><th>初审问题</th><th>复审问题</th><th>选定候选</th><th>传播</th><th>调用</th><th>材料</th></tr></thead><tbody>' +
        ''.join(html_rows) + '</tbody></table><h2>CFG 单次核对</h2><ul>' +
        ''.join('<li>' + escape(row['sample'] + '：' + row['status']) +
                (f' · <a href="cfg-reviews/{row["sample"]}/report.md">报告</a>' if (directory / 'cfg-reviews' / row['sample'] / 'report.md').exists() else '') + '</li>' for row in audits) +
        '</ul><p>完整调用、编译与审计材料保存在各案例目录。助手复核在实测后单独提供。</p></html>')
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="七例最多一次标注修复，另三次 CFG 核对；不重新提取")
    parser.add_argument("command", choices=("prepare", "run", "replay", "summarize"))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        prepare(args.run_dir)
        return 0
    if args.command == "summarize":
        summarize(args.run_dir)
        return 0
    result = run(args.run_dir, env_file=args.env_file, replay=args.command == "replay")
    return int(any(row["status"] not in {"review_passed", "repair_limit"}
                   or row.get("propagation") != "complete"
                   or (row.get("driver") or {}).get("status") == "driver_error"
                   for row in result["cases"])
               or any(row["status"] not in {"audit_passed", "revision_limit"}
                      or row.get("driver_error") for row in result["cfg_reviews"]))


if __name__ == "__main__":
    raise SystemExit(main())
