"""Run the three pinned Skills through the public, durable analysis pipeline.

This scheduler has no annotation, review, propagation, or DOE implementation.
Historical receipts verify only the source/CFG identity; no old candidate is
imported as a fresh model response. Preparation and replay make zero API calls.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from threading import Event

from skillflow.common.artifact_io import atomic_write_text
from skillflow.common.llm.config import LlmConfig
from skillflow.common.paths import project_root
from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.common.runs import exclusive_run
from skillflow.common.source_evidence import _json_object
from skillflow.propagation.annotation.config import annotation_config, annotation_public_config


IDENTITY = "skillflow-joint-pipeline-pilot-v8"
BASELINE = "experiments/propagation/runs/sink-tightening-v1-20261002-205045"
RECEIPTS = "experiments/doe/inputs/sensitivity-v1"
CASES = ("001", "010", "013")
RECEIPT_SHA256 = {
    "001": "3dbcdee9a1e5df1d10776e4e07eebbf92475a3133b31f36d45322d8b0106c518",
    "010": "57b7da1fe9cede95972c153a9c8da47984711d35af96cf68b32ea1657bf26cea",
    "013": "60b2886ba57ef42742383e344183f2849a4f851712932eea0ccbfc56aa31511a",
}
CLAIM = (
    "A completed pipeline is conditional on its front-end declarations and supported rules. "
    "Review acceptance is not semantic proof, and an empty sensitivity set is not a safety conclusion."
)
LANGUAGE_CLAIM = (
    "Case 001 uses an explicitly translated source/CFG projection; comparison with historical Chinese runs also changes "
    "input language, so changes cannot be attributed entirely to prompting."
)


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _read(path):
    return _json_object(Path(path).read_bytes().decode("utf-8"))


def _no_links(path):
    for parent in (path, *path.parents):
        if parent.exists() or parent.is_symlink():
            info = parent.lstat()
            if parent.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("Pilot paths must not contain links or reparse points")


def _child(parent, relative):
    path = parent / relative
    _no_links(path)
    resolved = path.resolve()
    if not resolved.is_relative_to(parent.resolve()):
        raise ValueError("Pinned input path escapes its directory")
    return resolved


def verify_baseline(root=None):
    """Verify exact historical bytes without invoking an old format loader."""
    root = (project_root() if root is None else Path(root)).resolve()
    records, historical = {}, {}
    for case in CASES:
        receipt_path = _child(root, f"{RECEIPTS}/{case}.json")
        if sha_file(receipt_path) != RECEIPT_SHA256[case]:
            raise ValueError(f"Case {case}: pinned pre-upgrade receipt differs")
        historical[str(receipt_path)] = RECEIPT_SHA256[case]
        receipt = _read(receipt_path)
        case_dir = _child(root, f"{BASELINE}/cases/{case}")
        annotation_dir = case_dir / "annotation"
        identity = receipt["annotation_identity"]
        for relative, digest in identity["files"].items():
            path = _child(annotation_dir, relative)
            if sha_file(path) != digest:
                raise ValueError(f"Case {case}: historical annotation byte mismatch: {relative}")
            historical[str(path)] = digest
        manifest = _read(annotation_dir / "manifest.json")
        if manifest["manifest_sha256"] != identity["manifest_sha256"]:
            raise ValueError(f"Case {case}: historical manifest identity differs")
        analysis = case_dir / "selected-analysis.json"
        expected_analysis = manifest["original_analysis"]["sha256"]
        if sha_file(analysis) != expected_analysis:
            raise ValueError(f"Case {case}: selected CFG file differs")
        historical[str(analysis)] = expected_analysis
        cfg = _read(analysis)["cfg"]
        if (cfg != receipt["annotation"]["material"]["cfg"]
                or _read(annotation_dir / "inputs/cfg.json") != cfg):
            raise ValueError(f"Case {case}: selected graph differs from the verified receipt")
        source = _read(annotation_dir / "inputs/source.json")
        if source != receipt["annotation"]["material"]["source"]:
            raise ValueError(f"Case {case}: source differs from the verified receipt")
        package = annotation_dir / "inputs/package"
        expected_members = {name.removeprefix("inputs/package/")
                            for name in identity["files"] if name.startswith("inputs/package/")}
        actual_members = set()
        for path in package.rglob("*"):
            _no_links(path)
            if path.is_file():
                actual_members.add(path.relative_to(package).as_posix())
        if actual_members != expected_members:
            raise ValueError(f"Case {case}: source package inventory differs")
        records[case] = {
            "input": str(package), "analysis": str(analysis),
            "receipt_sha256": RECEIPT_SHA256[case],
            "historical_annotation_manifest_sha256": identity["manifest_sha256"],
            "source_sha256": identity["source_sha256"],
            "graph_sha256": identity["graph_sha256"],
            "selected_analysis_sha256": expected_analysis,
        }
    return records, historical


def _check_history(historical):
    for filename, digest in historical.items():
        path = Path(filename)
        _no_links(path)
        if sha_file(path) != digest:
            raise ValueError(f"Historical file changed: {filename}")


def _seal(value):
    return {**value, "manifest_sha256": canonical_sha256(value)}


def _load(directory, *, require_english_inputs=True):
    _no_links(directory)
    manifest = _read(directory / "manifest.json")
    unsigned = deepcopy(manifest)
    digest = unsigned.pop("manifest_sha256", None)
    if (unsigned.get("identity") != IDENTITY or unsigned.get("schema_version") != 8
            or digest != canonical_sha256(unsigned)):
        raise ValueError("Pilot identity or manifest digest differs")
    for relative, digest in manifest["files"].items():
        if sha_file(_child(directory, relative)) != digest:
            raise ValueError("Pilot frozen input inventory differs")
    _check_history(_read(directory / "audit/history-sha256.json"))
    if manifest.get("english_inputs") is None:
        if require_english_inputs:
            raise ValueError("Pilot English inputs are not fully prepared")
    else:
        from tools.doe.pilot_english import verify_english_inputs
        verify_english_inputs(manifest["cases"], _child(directory, "audit/english-inputs"), manifest["english_inputs"])
    return manifest


def _official_config(config):
    public = annotation_public_config(config)
    if (public["endpoint"].rstrip("/") != "https://api.deepseek.com/chat/completions"
            or public["model"] != "deepseek-v4-flash"):
        raise ValueError("This fixed pilot requires the official DeepSeek endpoint and deepseek-v4-flash")
    return public


def prepare_pilot(run_dir, *, config):
    from skillflow.pipeline import prepare_analysis_run, verify_analysis_prepared
    from tools.doe.pilot_english import prepare_english_inputs

    directory = Path(run_dir).expanduser().absolute()
    _no_links(directory)
    directory = directory.resolve()
    records, historical = verify_baseline()
    if any(directory == Path(path) or directory.is_relative_to(Path(path).parent)
           or Path(path).is_relative_to(directory) for path in historical):
        raise ValueError("Pilot output overlaps preserved inputs")
    public = _official_config(config)
    with exclusive_run(directory):
        manifest_path = directory / "manifest.json"
        if manifest_path.exists():
            manifest = _load(directory, require_english_inputs=False)
            if manifest["config"] != public or manifest["cases"] != records:
                raise ValueError("Pilot preparation inputs or configuration differ")
        else:
            if any(path.name != ".runner.lock" for path in directory.iterdir()):
                raise ValueError("Pilot preparation requires a new or matching directory")
            atomic_write_text(directory / "audit/history-sha256.json", _json(historical))
            manifest = _seal({
                "identity": IDENTITY, "schema_version": 8,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "config": public, "cases": records,
                "input_origin": "verified_historical_source_and_cfg_with_explicit_english_projection",
                "english_inputs": None,
                "policy": {"structural_corrections": "unlimited",
                           "reextract_cfg": False, "quality_reruns": False,
                           "task_source": "new_source_only_extraction_per_case",
                           "normal_semantic_calls_per_case": 3,
                           "annotation_repair_semantic_calls_per_case": 5,
                           "task_revision_semantic_calls_per_case": 6,
                           "maximum_repairs_per_case": 1, "automatic_resend_after_acceptance": False},
                "files": {"audit/history-sha256.json": sha_file(directory / "audit/history-sha256.json")},
            })
            atomic_write_text(manifest_path, _json(manifest))
        english_directory = _child(directory, "audit/english-inputs")
        if manifest["english_inputs"] is None:
            english = prepare_english_inputs(records, english_directory)
            unsigned = deepcopy(manifest)
            unsigned.pop("manifest_sha256")
            unsigned["english_inputs"] = english
            unsigned["files"].update({"audit/english-inputs/" + relative: digest
                                      for relative, digest in english["files"].items()})
            manifest = _seal(unsigned)
            atomic_write_text(manifest_path, _json(manifest))
        else:
            english = manifest["english_inputs"]
        prepared = {}
        for case in CASES:
            source = english["cases"][case]
            target = directory / "cases" / case
            if (target / "manifest.json").exists():
                prepared[case] = verify_analysis_prepared(target, config=public)
            else:
                prepared[case] = prepare_analysis_run(_child(english_directory, source["input"]), _child(english_directory, source["analysis"]),
                    run_dir=target, config=public, secrets=(config.api_key,))
        _check_history(historical)
        atomic_write_text(directory / "preparation.json", _json({
            "cases": {case: item["preparation_status"] for case, item in prepared.items()},
            "model_calls": 0,
        }))
        _write_reports(directory, manifest, {})
    return manifest


def _safe_failure(error, secrets):
    message = str(error)
    for secret in secrets:
        if secret:
            message = message.replace(secret, "[REDACTED]")
    return {"status": "failed", "stage": "pilot", "reason": message,
            "error_type": type(error).__name__}


def run_pilot(run_dir, *, config=None, env_file=None, stop_event=None,
              client_factory=None, review_client_factory=None, repair_client_factory=None,
              replay=False, progress=None):
    from skillflow.pipeline import replay_analysis, run_analysis

    directory = Path(run_dir).expanduser().absolute()
    _no_links(directory)
    directory = directory.resolve()
    stop_event = stop_event or Event()
    if not replay and config is None:
        config = annotation_config(LlmConfig.from_env(env_file=env_file))
    with exclusive_run(directory):
        manifest = _load(directory)
        if not replay and _official_config(config) != manifest["config"]:
            raise ValueError("Pilot execution configuration differs from preparation")
        results = {}
        secrets = () if config is None else (config.api_key,)
        if not replay and client_factory is None:
            from skillflow.common.recording import streaming_factory
            client_factory, secrets = streaming_factory(manifest["config"], env_file=env_file)
        for case in CASES:
            if stop_event.is_set():
                break
            case_dir = directory / "cases" / case
            if progress:
                progress({"case": case, "phase": "replay" if replay else "run"})
            try:
                if replay:
                    results[case] = replay_analysis(case_dir)
                else:
                    results[case] = run_analysis(case_dir, config=manifest["config"], env_file=env_file,
                        secrets=secrets, stop_event=stop_event, client_factory=client_factory,
                        review_client_factory=review_client_factory, repair_client_factory=repair_client_factory,
                        progress=None if progress is None else lambda message: progress({"case": case, "message": message}))
            except KeyboardInterrupt:
                stop_event.set()
                results[case] = {"status": "interrupted", "stage": "pilot",
                                 "reason": "User interruption; no later case was started."}
            except Exception as error:
                results[case] = _safe_failure(error, secrets)
            if results[case].get("status") == "interrupted":
                stop_event.set()
            summary = {"identity": IDENTITY, "replay": replay, "cases": results,
                       "interrupted": stop_event.is_set(), "not_started": [c for c in CASES if c not in results]}
            atomic_write_text(directory / ("replay-summary.json" if replay else "summary.json"), _json(summary))
            if not replay:
                _write_reports(directory, manifest, results)
        _check_history(_read(directory / "audit/history-sha256.json"))
        summary = {"identity": IDENTITY, "replay": replay, "cases": results,
                   "interrupted": stop_event.is_set(), "not_started": [c for c in CASES if c not in results],
                   "history_unchanged": True}
        if replay:
            summary["api_calls"] = 0
        atomic_write_text(directory / ("replay-summary.json" if replay else "summary.json"), _json(summary))
        if not replay:
            _write_reports(directory, manifest, results)
    return summary


def _write_reports(directory, manifest, results):
    rows = []
    for case in CASES:
        result = results.get(case, {})
        links = []
        for label, path in (
            ("Pipeline", f"cases/{case}/report.html"),
            ("Source-only Task", f"cases/{case}/task/report.html"),
            ("Initial Task", f"cases/{case}/task/task.json"),
            ("Isolated Task revision", f"cases/{case}/refinement/task-revision/report.html"),
            ("Revised Task", f"cases/{case}/refinement/task-revision/task.json"),
            ("Original annotation", f"cases/{case}/annotation/audit/raw-annotation.json"),
            ("Initial four-axis review", f"cases/{case}/refinement/initial-review/report.html"),
            ("Review and repair", f"cases/{case}/refinement/report.html"),
            ("Repaired annotation", f"cases/{case}/refinement/repair/audit/raw-annotation.json"),
            ("Independent re-review", f"cases/{case}/refinement/final-review/report.html"),
            ("Propagation", f"cases/{case}/propagation/report.html"),
            ("Facts", f"cases/{case}/propagation/data.json"),
            ("DOE review", f"cases/{case}/doe/report.html"),
            ("DOE result", f"cases/{case}/doe/doe-result.json"),
            ("Assistant review", f"cases/{case}/assistant-review.md"),
        ):
            if (directory / path).is_file():
                links.append((label, path))
        revised = (directory / f"cases/{case}/refinement/task-revision/manifest.json").is_file()
        repaired = (directory / f"cases/{case}/refinement/repair/manifest.json").is_file()
        selected = (result.get("selected_annotation") or {}).get("path", "none")
        route = ("Task revision and reannotation" if revised else "Fixed-Task annotation repair" if repaired else "None")
        selected_task = "Revised Task" if revised and selected == "refinement/repair" else "Initial Task" if selected != "none" else "none"
        rows.append({"case": case, "status": result.get("status", "prepared"),
                     "task": (result.get("task") or {}).get("status", "not run"),
                     "review": (result.get("refinement") or {}).get("status", "not run"),
                     "route": route, "selected_task": selected_task, "selected": selected,
                     "propagation": (result.get("propagation") or {}).get("status", "not run"),
                     "doe": (result.get("doe") or {}).get("status", "not run"),
                     "calls": (result.get("counts") or {}).get("logical_calls", 0),
                     "reason": result.get("reason", "Awaiting execution"), "links": links})
    md = ["# Formal joint pipeline: three-case pilot", "", CLAIM, "",
          "Verified historical sources and CFGs are retained. The pilot freezes an explicitly audited English projection without graph extraction; each Task is newly extracted from the English source only, then sealed for annotation and review. "
          "The normal path has 3 semantic calls; fixed-Task annotation repair has 5, while isolated Task revision and full reannotation has 6. "
          "The two repair paths share one semantic repair budget and end with independent rereview. Every response stage uses "
          "unlimited structural corrections; actual calls and transport attempts are recorded. "
          "No graph extraction, assistant-authored semantic candidates, or final DOE model call.", "", LANGUAGE_CLAIM, "",
          "| Case | Pipeline | Task | Review | Repair route | Selected Task | Selected annotation | Propagation | DOE | Logical calls | Materials |",
          "|---|---|---|---|---|---|---|---|---|---:|---|"]
    extra_links = [(label, path) for label, path in (("Actual calls, tokens and time", "metrics.md"),
                  ("Measurement records", "metrics.json"), ("Assistant semantic review", "assistant-review.md"),
                  ("Old/new prompt comparison", "comparison/report.html"),
                  ("Prompt organization and size comparison", "prompt-changes.md"),
                  ("Offline validation", "validation.md"),
                  ("Zero-API replay", "replay-summary.json")) if (directory / path).is_file()]
    extra_links += [(f"{case} English input projection", f"audit/english-inputs/{case}/projection.json")
                    for case in CASES if (directory / f"audit/english-inputs/{case}/projection.json").is_file()]
    if extra_links:
        md[4:4] = [" · ".join(f"[{label}]({path})" for label, path in extra_links), ""]
    html_rows = []
    for row in rows:
        md.append("| " + " | ".join(str(row[key]).replace("|", "\\|") for key in
            ("case", "status", "task", "review", "route", "selected_task", "selected", "propagation", "doe", "calls"))
            + " | " + ", ".join(f"[{label}]({path})" for label, path in row["links"]) + " |")
        html_rows.append("<tr>" + "".join(f"<td>{escape(str(row[key]))}</td>" for key in
            ("case", "status", "task", "review", "route", "selected_task", "selected", "propagation", "doe", "calls"))
            + "<td>" + " · ".join(f'<a href="{escape(path, quote=True)}">{escape(label)}</a>'
                                     for label, path in row["links"]) + "</td></tr>")
    for row in rows:
        md += ["", f"**{row['case']}:** {row['reason']}"]
    md += ["", "Review failure or repair_limit permits only explicitly diagnostic downstream analysis. "
           "Failed annotation never falls back to a historical successful response. "
           "Candidate and range counts are not counts of measured leaks.", ""]
    atomic_write_text(directory / "report.md", "\n".join(md))
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Formal joint pipeline pilot</title><style>body{font:16px/1.65 system-ui,sans-serif;'
        'max-width:1400px;margin:28px auto;padding:0 20px;color:#172d43}aside{background:#eef4fa;'
        'padding:16px;border-left:4px solid #35699d}table{border-collapse:collapse;width:100%;margin:24px 0}'
        'th,td{border:1px solid #cbd7e2;padding:9px;text-align:left;vertical-align:top}a{color:#12558c}'
        '</style></head><body><h1>Formal joint pipeline: three-case pilot</h1><aside>'
        + escape(CLAIM) + '</aside><p>Verified historical Skills and CFGs with an audited English input projection. New source-only Task extraction, then fixed-Task annotation and full-chain review. '
        'Normal / annotation-repair / Task-revision paths use 3 / 5 / 6 semantic calls. Unlimited structural corrections; '
        'no graph extraction, manual semantic completion, or final DOE model call.</p><p>' + escape(LANGUAGE_CLAIM) + '</p>'
        '<p><a href="report.md">Markdown</a> · <a href="manifest.json">Input identity and policy</a></p>'
        + '<p>' + ' · '.join(f'<a href="{escape(path, quote=True)}">{escape(label)}</a>' for label, path in extra_links)
        + '</p><table><thead><tr>' + ''.join(f'<th>{label}</th>' for label in
            ('Case', 'Pipeline', 'Task', 'Review', 'Repair route', 'Selected Task', 'Selected annotation', 'Propagation', 'DOE', 'Logical calls', 'Materials'))
        + '</tr></thead><tbody>' + ''.join(html_rows) + '</tbody></table>'
        + ''.join(f"<p><strong>{row['case']}:</strong> {escape(str(row['reason']))}</p>" for row in rows)
        + '<p>Diagnostic results retain unresolved review failures or reported issues. '
        'A failed annotation never displays an older successful DOE result.</p></body></html>')
    atomic_write_text(directory / "index.html", page)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "run", "replay"):
        stage = sub.add_parser(name)
        stage.add_argument("--run-dir", type=Path, required=True)
        if name != "replay":
            stage.add_argument("--env-file", type=Path)
    args = parser.parse_args(argv)
    if args.command == "replay":
        result = run_pilot(args.run_dir, replay=True)
    else:
        config = annotation_config(LlmConfig.from_env(env_file=args.env_file))
        if args.command == "prepare":
            result = prepare_pilot(args.run_dir, config=config)
        else:
            result = run_pilot(args.run_dir, config=config, env_file=args.env_file,
                               progress=lambda item: print(_json(item), flush=True))
    print(_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
