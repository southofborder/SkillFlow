"""Offline, verified staging export of the new thirty-case full pipeline.

This tool never publishes, contacts a model, executes a Skill, or borrows an old
graph. Only a completed experiment-result is accepted. PNGs, profiles and review
notes are staged for a separate explicit publication step.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile

from skillflow.common.paths import project_root, resolve_material_path

HERE = Path(__file__).resolve()
PACKAGE_ROOT = project_root()
REPOSITORY_ROOT = project_root()
BASELINE_TOOLS = REPOSITORY_ROOT / "tools/graph/baseline"
from tools.graph.baseline import export_review_set as _png

from skillflow.common.artifact_io import atomic_write_text
from skillflow.graph.audit.controlled import verify_controlled
from skillflow.graph.audit.models import AuditResult
from skillflow.graph.audit.models import Finding
from skillflow.graph.audit.models import Suggestion
from skillflow.graph.audit.models import ConservativeRepresentation
from skillflow.graph.audit.services import validate_audit
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.inputs.skill_package import load_skill_package
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.graph.feedback.policy import decide
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import sha_file
from skillflow.propagation.material import checked_cfg
from skillflow.propagation.material import prepare_material
from skillflow.propagation.annotation.loading import load_annotation_run
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.common.source_evidence import source_units
from skillflow.graph.semantic_contract import contract_binding

IDENTITY = "skill-ir-full-feedback-security-profile-review30-v10"
EXPORT_IDENTITY = "skill-ir-full-pipeline-delivery-v5"
SAMPLE_IDS = tuple(f"{group}{number:02}" for group in "NQFDR" for number in range(1, 7))
ANNOTATION_STATUSES = {"complete", "input_error", "invalid_response", "execution_error", "semantic_failure", "interrupted", "not_run"}


def read_json(path: Path):
    def pairs(entries):
        value = {}
        for key, item in entries:
            if key in value:
                raise ValueError(f"Duplicate JSON key: {key}")
            value[key] = item
        return value
    def constant(value):
        raise ValueError(f"Non-JSON constant: {value}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def write_json(path: Path, value):
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def reason_summary(reason: str, *, limit: int = 600) -> str:
    """Display-only summary from actual diagnostic lines, never a new judgment.

    Full diagnostics remain untouched in the run and review payload. In long
    Pydantic diagnostics, repeated instances of the same error need not bury the
    operation list. The original heading and up to two distinct error messages
    identify the failure without quoting enormous input_value representations.
    """
    if not isinstance(reason, str):
        raise ValueError("Execution reason must be text")
    if len(reason) <= limit and len(reason.splitlines()) <= 4:
        return reason
    def short(text, length):
        text = text.strip()
        return text if len(text) <= length else text[:length - 1] + "…"
    lines = [line for line in reason.splitlines() if line.strip()]
    if not lines:
        return ""
    header = short(lines[0], 200)
    details, seen = [], set()
    previous = lines[0].strip()
    for line in lines[1:]:
        text = line.strip()
        if text.startswith("For further information visit"):
            continue
        if line[:1].isspace():
            # Pydantic appends input_value and links after the actual message.
            message = text.split(" [type=", 1)[0]
            if message not in seen:
                details.append(short(previous, 80) + "：" + short(message, 170))
                seen.add(message)
                if len(details) == 2:
                    break
        else:
            previous = text
    if not details:
        details = [short(line, 170) for line in lines[1:3]]
    result = header + ("；代表错误：" + "；".join(details) if details else "")
    suffix = "；完整诊断保留于原始运行记录及审查页展开区。"
    return short(result, limit - len(suffix)) + suffix


def child(root: Path, relative: str) -> Path:
    candidate = PurePosixPath(relative)
    if (not relative or candidate.is_absolute() or ".." in candidate.parts
            or "\\" in relative or ":" in relative or "\0" in relative):
        raise ValueError(f"Unsafe relative artifact path: {relative!r}")
    result = root.joinpath(*candidate.parts)
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError("Artifact path escapes its root")
    for current in [result, *result.parents]:
        if current == root.parent:
            break
        if current.exists() and (current.is_symlink() or getattr(current.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("Artifact path cannot contain links or reparse points")
    return result


def verified_zip(path: Path, inventory: dict) -> dict:
    """Compare every original byte, including non-readable files; never extract."""
    actual = {}
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = info.filename
            member = PurePosixPath(name)
            if (member.is_absolute() or ".." in member.parts or "\\" in name or ":" in name
                    or "\0" in name or str(member) != name.rstrip("/")
                    or stat.S_ISLNK(info.external_attr >> 16)):
                raise ValueError("Unsafe ZIP member")
            if info.is_dir():
                continue
            if name in actual:
                raise ValueError("Duplicate ZIP member")
            raw = archive.read(info)
            actual[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if "SKILL.md" not in actual or actual != inventory:
        raise ValueError("Skill ZIP differs from frozen source inventory")
    return {"status": "passed", "zip_sha256": sha_file(path), "files": len(actual),
            "source_inventory_sha256": canonical_sha256(actual)}


def _source(case, feedback_dir, zip_path):
    if (feedback_dir / "inputs/snapshot.json").exists():
        _, source, snapshot = read_snapshot(feedback_dir)
        inventory = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]}
                     for entry in snapshot["files"]}
        if inventory != case["source_inventory"]:
            raise ValueError("Feedback snapshot differs from corpus source inventory")
        return source, snapshot
    # This is only a source display fallback for cases that never got a graph.
    package = load_skill_package(zip_path)
    files = [{"path": entry.path, "content": entry.content,
              "sha256": hashlib.sha256(entry.content.encode("utf-8")).hexdigest()}
             for entry in package.readable_files()]
    return {"files": files, "source_sha256": canonical_sha256([
        {key: item[key] for key in ("path", "sha256")} for item in files])}, None


def _raw_audit(audit):
    raw = {key: deepcopy(audit[key]) for key in AuditResult.model_fields}
    raw["findings"] = [{key: deepcopy(item[key]) for key in Finding.model_fields if key in item}
                       for item in audit["findings"]]
    for item in raw["findings"]:
        item["suggestions"] = [{key: value[key] for key in Suggestion.model_fields} for value in item["suggestions"]]
        if item.get("conservative") is not None:
            item["conservative"] = {key: item["conservative"][key] for key in ConservativeRepresentation.model_fields}
    return raw


def _selected_audit(feedback_dir, row, graph, source, renderer):
    audit = row.get("audit")
    if audit is None:
        return None
    round_dir = feedback_dir / "rounds" / f"r{row['revision']:03}"
    if read_json(round_dir / "audit.json") != audit:
        raise ValueError("Selected round audit differs from committed audit")
    document = read_json(round_dir / "controlled.json")
    model = ControlFlowGraph.model_validate_json(json.dumps(graph, ensure_ascii=False))
    verify_controlled(document, model, executable=renderer)
    validated = validate_audit(_raw_audit(audit), source, document)
    if validated != audit:
        raise ValueError("Selected audit evidence, graph mapping or source binding differs")
    return validated


def _annotation(root, annotation, selection, graph, source, snapshot, binding):
    status = annotation["status"]
    if status not in ANNOTATION_STATUSES:
        raise ValueError("Nonterminal or unsupported annotation status")
    directory = root / "annotation"
    if (directory / "result.json").exists() and read_json(directory / "result.json") != annotation:
        raise ValueError("Annotation result differs from case result")
    material = None
    manifest_path = directory / "manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
        if manifest.get("manifest_sha256") != canonical_sha256(unsigned):
            raise ValueError("Annotation manifest digest mismatch")
        if (manifest.get("identity") != "skill-ir-security-profile-v11" or manifest.get("schema_version") != 11
                or manifest.get("profile_schema_version") != SCHEMA_VERSION):
            raise ValueError("Unsupported annotation manifest")
        files = {p.relative_to(directory).as_posix(): sha_file(p)
                 for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}
        if files != manifest["files"]:
            raise ValueError("Annotation frozen input inventory changed")
        if manifest["preparation_status"] == "ready":
            _, second_source, second = read_snapshot(directory)
            if (snapshot is None or second_source != source or second["files"] != snapshot["files"]
                    or second["package_bytes_sha256"] != snapshot["package_bytes_sha256"]):
                raise ValueError("Feedback and annotation sources differ")
            expected_binding = {"status": "passed", "source_sha256": snapshot["source_sha256"],
                "package_bytes_sha256": snapshot["package_bytes_sha256"], "file_count": len(snapshot["files"]),
                "checked_fields": ["path", "size", "raw_sha256", "decoded_sha256", "kind"]}
            if binding != expected_binding or read_json(root / "source-binding.json") != binding:
                raise ValueError("Source binding differs from verified stage snapshots")
            material = prepare_material(source, graph)
            if (read_json(directory / "inputs/cfg.json") != graph
                    or read_json(directory / "inputs/material.json") != material
                    or manifest["material_sha256"] != canonical_sha256(material)
                    or manifest["source_sha256"] != source["source_sha256"]
                    or manifest["graph_sha256"] != canonical_sha256(graph)):
                raise ValueError("Annotation material differs from selected source or graph")
    if status in {"complete"}:
        if (annotation.get("profile_schema_version") != SCHEMA_VERSION
                or annotation.get("schema_version") != 11
                or annotation.get("identity") != "skill-ir-security-profile-v11"):
            raise ValueError("Unsupported profile result schema")
        if material is None or selection is None:
            raise ValueError("A successful annotation requires a verified selected graph and material")
        if (annotation.get("graph_sha256") != selection["graph_sha256"]
                or annotation.get("source_sha256") != source["source_sha256"]):
            raise ValueError("Profile result does not bind to selected source and graph")
        # The shared loader owns request, evidence, saved projections and
        # compilation checks. Export only adds its source/selection binding.
        verified_run = load_annotation_run(directory)
        if (verified_run["manifest"] != manifest or verified_run["material"] != material
                or verified_run["result"] != annotation):
            raise ValueError("Export annotation differs from the verified selected run")
    elif any(annotation.get(key) for key in ("profiles", "locations", "transfer_specs", "sink_boundaries")):
        raise ValueError("Failed annotation must not export unvalidated business records")
    return material


def load_case(run_dir: Path, case: dict, result: dict, skills_dir: Path, *, renderer=None) -> dict:
    """Verify one terminal case and its saved calls offline, without network access."""
    root = child(run_dir, case["run_dir"])
    if case["run_dir"] != f"cases/{case['case_id']}" or read_json(root / "result.json") != result:
        raise ValueError("Case result or location differs from experiment result")
    if case["source_inventory_sha256"] != canonical_sha256(case["source_inventory"]):
        raise ValueError("Corpus inventory digest mismatch")
    zip_path = child(skills_dir, case["basename"] + ".zip")
    zip_check = verified_zip(zip_path, case["source_inventory"])
    feedback, annotation, selection = result["feedback"], result["annotation"], result["selection"]
    if feedback.get("status") not in {"audit_passed", "semantic_failure", "revision_limit", "extraction_error",
            "fidelity_error", "audit_error", "execution_error", "interrupted", "not_run"}:
        raise ValueError("Feedback must have a terminal stop status")
    feedback_dir = root / "feedback"
    if (feedback_dir / "result.json").exists() and read_json(feedback_dir / "result.json") != feedback:
        raise ValueError("Feedback result differs from case result")
    source, snapshot = _source(case, feedback_dir, zip_path)
    graph, selected_round, audit = feedback.get("last_valid_cfg"), None, None
    if graph is not None:
        checked_cfg(graph)
        if snapshot is None or feedback.get("source_sha256") != source["source_sha256"]:
            raise ValueError("Selected graph requires matching frozen source snapshot")
        digest = canonical_sha256(graph)
        rounds = [row for row in feedback["rounds"] if row.get("graph_sha256") == digest
                  and (row.get("structural") or {}).get("status") == "passed"]
        if not rounds:
            raise ValueError("Selected graph has no structurally checked round")
        selected_round = rounds[-1]
        if (selection is None or selection.get("policy") != "last_valid_cfg_from_current_feedback_only"
                or selection["revision"] != selected_round["revision"] or selection["graph_sha256"] != digest
                or selection["source_sha256"] != source["source_sha256"]
                or selection["feedback_status"] != feedback["status"]
                or selection["auditor_passed"] != (feedback["status"] == "audit_passed")):
            raise ValueError("Selection differs from current last valid feedback graph")
        for key, value in contract_binding().items():
            if selection.get(key) != value:
                raise ValueError("Selection semantic contract mismatch")
        round_dir = feedback_dir / "rounds" / f"r{selected_round['revision']:03}"
        if read_json(round_dir / "cfg.json") != graph:
            raise ValueError("Selected graph differs from committed round CFG")
        audit = _selected_audit(feedback_dir, selected_round, graph, source, renderer)
        if feedback["status"] == "audit_passed" and (audit is None or selected_round.get("status") != "audit_passed"
                or decide(audit, selected_round["revision"], 3)["status"] != "audit_passed"):
            raise ValueError("Auditor-passed feedback lacks a current valid passing audit")
        if (root / "selected-analysis.json").exists() and read_json(root / "selected-analysis.json") != {"cfg": graph}:
            raise ValueError("Selected analysis differs from current feedback graph")
        if (root / "selection.json").exists() and read_json(root / "selection.json") != selection:
            raise ValueError("Committed selection differs")
    elif selection is not None or annotation["status"] in {"complete"}:
        raise ValueError("No-CFG case cannot borrow a historical graph or successful profile")
    material = _annotation(root, annotation, selection, graph, source, snapshot, result["source_binding"])
    if snapshot:
        boundaries = snapshot["boundaries"]
    else:
        package = load_skill_package(zip_path)
        boundaries = {"binary_files": [entry.path for entry in package.files if entry.content is None],
                      "uninterpreted_code_files": [entry.path for entry in package.files if entry.kind == "code"],
                      "notice": "本例未完成反馈快照；源文仅从已核验 ZIP 解码展示，不表示脚本已执行或二进制已理解。"}
    provenance = {"schema_version": 5, "identity": EXPORT_IDENTITY, "profile_schema_version": SCHEMA_VERSION, "run_id": run_dir.name,
        "case_id": case["case_id"], "sample_id": case["sample_id"], "basename": case["basename"],
        "selected_revision": selection["revision"] if selection else None,
        "graph_sha256": canonical_sha256(graph) if graph is not None else None,
        "source_sha256": source["source_sha256"], "zip_sha256": zip_check["zip_sha256"],
        "feedback_status": feedback["status"], "annotation_status": annotation["status"],
        "kind": "cfg" if graph is not None else "failure"}
    basename = case["basename"]
    return {**provenance, "skill_name": basename.split("-", 1)[1], "provenance": provenance,
        "feedback_reason": feedback.get("reason", ""), "annotation_reason": annotation.get("reason", ""),
        "feedback_reason_summary": reason_summary(feedback.get("reason", "")),
        "annotation_reason_summary": reason_summary(annotation.get("reason", "")),
        "diagnostic_sources": {"feedback": str(feedback_dir / "result.json") if (feedback_dir / "result.json").exists() else str(root / "result.json"),
                               "annotation": str(root / "annotation/result.json") if (root / "annotation/result.json").exists() else str(root / "result.json")},
        "cfg": graph, "source": {**source, "units": source_units(source)}, "audit": audit,
        "profiles": annotation["profiles"], "locations": annotation["locations"],
        "transfer_specs": annotation["transfer_specs"],
        "sink_boundaries": annotation["sink_boundaries"],
        "annotation_audit": ({"file": f"audit/{basename}/location-evidences.json",
                              "sha256": annotation["location_evidences_sha256"],
                              "source_file": str(root / "annotation/audit/location-evidences.json")}
                             if annotation["status"] in {"complete"} else None),
        "validation": annotation.get("validation", {}), "source_binding": result["source_binding"],
        "source_validation": {"zip": zip_check, "snapshot": snapshot is not None},
        "annotation_evidence_index": {key: material[key] for key in
            ("source_index", "graph_index", "instruction_index", "execution_model")} if material else None,
        "boundaries": boundaries,
        "scheduler_error": result.get("scheduler_error"),
        "png_file": f"ir-IPP/{basename}.png", "svg_file": f"render/{basename}.svg",
        "suggestions_file": f"suggestions/{basename}.md"}


def _assistant_review(directory: Path | None, run_dir: Path, case: dict, result: dict, row: dict) -> dict:
    base = {"reviewer": "assistant", "human_confirmed": False, "status": "pending", "reviews": []}
    if directory is None:
        return base
    path = child(Path(directory).resolve(), case["case_id"] + ".json")
    if not path.exists():
        return base
    value = read_json(path)
    if (set(value) != {"run_id", "case_id", "reviews"} or value["run_id"] != run_dir.name
            or value["case_id"] != case["case_id"] or not isinstance(value["reviews"], list)):
        raise ValueError("Assistant review belongs to a different run/case or has unsupported fields")
    records = []
    for review in value["reviews"]:
        if (set(review) != {"revision", "graph_sha256", "assessment", "observations"}
                or not (type(review["revision"]) is int or review["revision"] is None)
                or not isinstance(review["assessment"], str)
                or not review["assessment"].strip() or not isinstance(review["observations"], list)
                or any(not isinstance(text, str) or not text.strip() for text in review["observations"])):
            raise ValueError("Invalid assistant review record")
        if review["revision"] is None or review["graph_sha256"] is None:
            if (review["revision"] is not None or review["graph_sha256"] is not None
                    or row.get("cfg") is not None or row.get("selected_revision") is not None
                    or row.get("graph_sha256") is not None or result.get("selection") is not None
                    or result["feedback"].get("last_valid_cfg") is not None):
                raise ValueError("Execution-only review requires no selected or valid graph")
            if records:
                raise ValueError("Duplicate or mixed execution-only assistant review")
            records.append({**review, "scope": "execution_only", "matches_selected_graph": False})
            continue
        if any(entry["scope"] == "execution_only" for entry in records):
            raise ValueError("Cannot mix graph and execution-only assistant reviews")
        matches = [round_ for round_ in result["feedback"].get("rounds", [])
                   if round_.get("revision") == review["revision"] and round_.get("graph_sha256") == review["graph_sha256"]]
        if len(matches) != 1 or review["graph_sha256"] is None:
            raise ValueError("Assistant review graph does not belong to this case revision")
        graph_path = child(run_dir, case["run_dir"]) / "feedback/rounds" / f"r{review['revision']:03}" / "cfg.json"
        if canonical_sha256(read_json(graph_path)) != review["graph_sha256"]:
            raise ValueError("Assistant review graph digest differs from saved revision")
        if any(existing["revision"] == review["revision"] for existing in records):
            raise ValueError("Duplicate assistant review revision")
        records.append({**review, "scope": "graph", "matches_selected_graph": review["revision"] == row["selected_revision"]
                        and review["graph_sha256"] == row["graph_sha256"]})
    review_status = "execution_only" if records and all(entry["scope"] == "execution_only" for entry in records) else "reviewed" if records else "pending"
    return {**base, "status": review_status, "reviews": records,
            "source_file": str(path), "source_sha256": sha_file(path)}


def build_export_plan(run_dir: Path, skills_dir: Path, *, renderer=None, assistant_reviews=None) -> dict:
    run_dir, skills_dir = run_dir.resolve(), skills_dir.resolve()
    manifest, result = read_json(run_dir / "manifest.json"), read_json(run_dir / "experiment-result.json")
    for value in (manifest, result):
        if (value.get("schema_version") != 10 or value.get("identity") != IDENTITY
                or value.get("profile_schema_version") != SCHEMA_VERSION):
            raise ValueError("Only the current complete full-pipeline experiment is supported")
        if any(value.get(key) != item for key, item in contract_binding().items()):
            raise ValueError("Semantic contract identity mismatch")
    cases = manifest["cases"]
    if len(cases) != 30 or set(result["cases"]) != {f"{i:03}" for i in range(1, 31)}:
        raise ValueError("Completed thirty-case manifest and results are required")
    for index, case in enumerate(cases, 1):
        if (case["case_id"] != f"{index:03}" or case["sample_id"] != SAMPLE_IDS[index - 1]
                or not re.fullmatch(rf"{index:03}-[A-Za-z0-9][A-Za-z0-9._-]*", case["basename"])):
            raise ValueError("Fixed numbering, sample identity or safe basename differs")
    origins = execution_origins(run_dir, cases)
    names = {case["basename"] + ".zip" for case in cases}
    _png.check_inventory(skills_dir, names)
    rows = []
    for case in cases:
        value = result["cases"][case["case_id"]]
        row = load_case(run_dir, case, value, skills_dir, renderer=renderer or manifest["renderer"]["path"])
        row["assistant_review"] = _assistant_review(assistant_reviews, run_dir, case, value, row)
        if origins:
            row["execution_origin"] = origins[case["case_id"]]
        rows.append(row)
    return {"schema_version": 5, "identity": EXPORT_IDENTITY, "profile_schema_version": SCHEMA_VERSION, "run_id": run_dir.name,
        "run_dir": str(run_dir), "manifest_sha256": sha_file(run_dir / "manifest.json"),
        "experiment_result_sha256": sha_file(run_dir / "experiment-result.json"), "cases": rows,
        "notice": "核对器通过不等于已证明语义等价；标注记录完整不等于安全标注正确。导出未经人工确认。"}


def execution_origins(run_dir: Path, cases: list[dict]) -> dict:
    """Validate the display lineage without inspecting any call or transport."""
    run_dir = run_dir.resolve()
    path = run_dir / "rerun-provenance.json"
    if not path.exists():
        return {}
    value = read_json(path)
    unsigned = {key: item for key, item in value.items() if key != "provenance_sha256"}
    if (value.get("schema_version") != 4 or value.get("identity") != "skill-ir-explicit-failed-case-rerun-v4"
            or value.get("provenance_sha256") != canonical_sha256(unsigned)):
        raise ValueError("Execution origin provenance seal mismatch")
    child, parent = value.get("child_run", {}), value.get("parent_run", {})
    if (child.get("run_id") != run_dir.name or Path(child.get("path", "")).resolve() != run_dir
            or not isinstance(parent.get("run_id"), str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", parent["run_id"])
            or Path(parent.get("path", "")).resolve().name != parent["run_id"]
            or parent["run_id"] == run_dir.name
            or parent.get("manifest_sha256") != sha_file(run_dir / "manifest.json")):
        raise ValueError("Execution origin run or manifest binding mismatch")
    all_cases = {f"{index:03}" for index in range(1, 31)}
    expected_rerun = {"008", "009"} | {f"{index:03}" for index in range(18, 31)}
    rerun, reused = value.get("rerun_cases"), value.get("reused_cases")
    if (len(cases) != 30 or {case["case_id"] for case in cases} != all_cases
            or not isinstance(rerun, list) or not isinstance(reused, list)
            or any(not isinstance(case, str) for case in rerun + reused)
            or len(rerun) != len(set(rerun)) or len(reused) != len(set(reused))
            or set(rerun) & set(reused) or set(rerun) | set(reused) != all_cases
            or set(rerun) != expected_rerun):
        raise ValueError("Execution origin rerun/reuse partition mismatch")
    return {case: {"kind": "rerun" if case in expected_rerun else "reused",
                   "parent_run_id": parent["run_id"],
                   "source_run_id": run_dir.name if case in expected_rerun else parent["run_id"],
                   "provenance_sha256": value["provenance_sha256"]}
            for case in sorted(all_cases)}


def suggestions(row: dict) -> str:
    feedback_reason = row.get("feedback_reason_summary", reason_summary(row["feedback_reason"]))
    annotation_reason = row.get("annotation_reason_summary", reason_summary(row["annotation_reason"]))
    lines = [f"# {row['basename']} · 当前图核对意见", "",
        "本文件由当前运行的合法核对记录自动整理；不是助手或人工确认，不修改原图。", "",
        f"- 样例：{row['sample_id']}；运行：{row['run_id']}；选图轮次：{row['selected_revision']}",
        f"- 反馈停止：{row['feedback_status']}；原因：{feedback_reason}",
        f"- 安全标注：{row['annotation_status']}；原因：{annotation_reason}",
        f"- 图 SHA-256：{row['graph_sha256']}；源文 SHA-256：{row['source_sha256']}", "",
        "未填写保守说明不代表精确保留；覆盖记录不证明语义完整。"]
    origin = row.get("execution_origin")
    if origin:
        label = "本次重新执行" if origin["kind"] == "rerun" else "复用父运行记录（本次未重新调用模型）"
        lines[5:5] = [f"- 执行来源：{label}；父运行：`{origin['parent_run_id']}`；实际执行运行：`{origin['source_run_id']}`"]
    for stage, label in (("feedback", "反馈"), ("annotation", "安全标注")):
        location = row.get("diagnostic_sources", {}).get(stage)
        if location:
            target = Path(location).as_posix().replace("<", "%3C").replace(">", "%3E")
            lines += ["", f"{label}完整执行诊断：[原始运行记录](<{target}>)；本地审查页也可展开全文。"]
    if row["cfg"] is None:
        lines += ["", "**本次没有可用 CFG。配对 PNG 是失败状态卡；没有借用旧图，也没有生成安全 profile。**"]
    audit = row["audit"]
    if audit is None:
        lines += ["", "当前所选图没有合法的完整语义核对记录。不能由结构有效或其他轮次的发现推定通过。"]
    else:
        findings = sorted(audit["findings"], key=lambda value: value["status"] == "represented")
        for finding in findings:
            lines += ["", f"## {finding['id']} · {finding['kind']} · {finding['status']}", "",
                f"原文要求：{finding['source_requirement']}", "", f"当前表示：{finding['actual_representation']}",
                "", f"比较理由：{finding['reason']}"]
            if finding.get("conservative"):
                lines += ["", "明确保守依赖说明：" + json.dumps(finding["conservative"], ensure_ascii=False)]
            for ref in finding["source_refs"]:
                lines += ["", f"源文 `{ref['unit_id']}` · `{ref['file']}:{ref['start_line']}-{ref['end_line']}`：",
                          "", *["> " + line for line in ref["quote"].splitlines()]]
            for ref in finding["graph_refs"]:
                lines += ["", "图位置：" + json.dumps(ref, ensure_ascii=False)]
            for advice in finding["suggestions"]:
                lines += ["", f"修改建议：{advice['change']}", "", f"依据：{advice['reason']}", "",
                    "当前目标：" + json.dumps(advice["graph_refs"], ensure_ascii=False)]
    partial = [ir_id for ir_id, spec in row["transfer_specs"].items() if spec["order"] == "partial"]
    if partial:
        lines += ["", "## 部分顺序关系", "", "以下 IR 按必要先后约束计算候选次序：" + ", ".join(partial)]
    review = row.get("assistant_review", {})
    lines += ["", "## 助手事后复核", "", "此部分独立于模型核对记录，未经人工确认，不追溯修改模型判定。"]
    if not review.get("reviews"):
        lines += ["", "尚无已保存的助手逐例复核。"]
    for entry in review.get("reviews", []):
        if entry.get("scope") == "execution_only":
            lines += ["", "### 仅执行记录复核，无可用图", "",
                      "没有进行该例的图语义或安全标注正确性复核，不计作语义复核成功。", "",
                      entry["assessment"], "", *["- " + observation for observation in entry["observations"]]]
            continue
        scope = "当前所选图" if entry["matches_selected_graph"] else "历史轮次，不能作为当前图结论"
        lines += ["", f"### 修复轮次 {entry['revision']} · {scope}", "",
                  f"图 SHA-256：{entry['graph_sha256']}", "", entry["assessment"], "",
                  *["- " + observation for observation in entry["observations"]]]
    lines += ["", "本阶段不判断数据传播、敏感数据泄露、必要性或 DOE。", ""]
    return "\n".join(lines)


def render_samples(plan):
    samples = []
    for row in plan["cases"]:
        sample = {"index": int(row["case_id"]), "sample_id": row["sample_id"], "basename": row["basename"],
            "skill_name": row["skill_name"], "repetition": row["selected_revision"],
            "run_id": row["run_id"], "analysis_sha256": row["graph_sha256"], "cfg": row["cfg"],
            "provenance_lines": [f"运行：{row['run_id']} | 案例：{row['case_id']} / {row['sample_id']} | 修复轮次：{row['selected_revision']}",
                f"反馈：{row['feedback_status']} | 标注：{row['annotation_status']}",
                "CFG SHA-256：" + (row["graph_sha256"] or "无可用 CFG"),
                "源文 SHA-256：" + row["source_sha256"],
                "核对器通过不等于语义等价证明；标注完整不等于安全结论。"]}
        if row["cfg"] is None:
            sample["failure"] = {"reason": row.get("feedback_reason_summary", reason_summary(row["feedback_reason"])), "feedback_status": row["feedback_status"],
                                 "annotation_status": row["annotation_status"]}
        samples.append(sample)
    return {"samples": samples}


def _staging_directory(path, run_dir, skills_dir):
    path = Path(path).resolve()
    protected = [Path(run_dir).resolve(), Path(skills_dir).resolve(), REPOSITORY_ROOT / "result",
                 REPOSITORY_ROOT / "dataset", PACKAGE_ROOT / "src", PACKAGE_ROOT / "experiments"]
    if any(path == target or path.is_relative_to(target) or target.is_relative_to(path) for target in protected):
        raise ValueError("Staging cannot overlap source, runs, repository deliveries or code")
    if path.exists() and any(path.iterdir()):
        raise ValueError("Staging requires a new or empty directory; no implicit overwrite")
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_staging(plan, staging):
    names = {row["basename"] for row in plan["cases"]}
    for folder, extension in (("ir-IPP", ".png"), ("security-profiles", ".json"), ("suggestions", ".md")):
        _png.check_inventory(staging / folder, {name + extension for name in names})
    audit = read_json(staging / "render/audit.json")
    if (audit["input_sha256"] != sha_file(staging / "render/input.json")
            or read_json(staging / "render/input.json") != render_samples(plan)
            or read_json(staging / "review-data.json") != plan):
        raise ValueError("Rendered input or review material differs from verified plan")
    rows = {entry["basename"]: entry for entry in audit["samples"]}
    if len(rows) != len(names) or len(audit["samples"]) != len(names) or set(rows) != names or audit["status"] != "passed":
        raise ValueError("Rendered case inventory or status differs")
    checks = []
    for row in plan["cases"]:
        entry = rows[row["basename"]]
        expected_counts = _png.graph_counts(row["cfg"]) if row["cfg"] is not None else {key: 0 for key in
            ("blocks", "edges", "instructions", "inputs", "outputs", "skill_constraints", "block_constraints", "instruction_constraints")}
        if (entry.get("kind") != row["kind"] or entry["counts"] != expected_counts
                or not all(entry.get(key) for key in ("counts_checks_passed", "text_checks_passed", "bounds_checks_passed", "identity_checks_passed", "png_dimensions_checked"))):
            raise ValueError("Renderer counts, text or bounds validation failed")
        png_path = staging / row["png_file"]
        info = _png.inspect_png(png_path)
        original_png = _png.PNG_SIGNATURE + b"".join(raw for kind, payload, raw in _png.png_chunks(png_path.read_bytes())
            if not (kind == b"tEXt" and payload.startswith(_png.IDENTITY_KEY + b"\0")))
        if hashlib.sha256(original_png).hexdigest() != entry["png_sha256"]:
            raise ValueError("PNG image bytes differ from verified renderer output")
        if info["source"] != row["provenance"] or (info["width"], info["height"]) != (entry["width"], entry["height"]):
            raise ValueError("PNG provenance or canvas dimensions differ")
        if sha_file(staging / row["svg_file"]) != entry["svg_sha256"]:
            raise ValueError("SVG bytes differ from actual rendered graph")
        profile = read_json(staging / "security-profiles" / (row["basename"] + ".json"))
        if (profile.get("schema_version") != 5 or profile.get("identity") != EXPORT_IDENTITY
                or profile.get("profile_schema_version") != SCHEMA_VERSION
                or profile["provenance"] != row["provenance"]
                or any(profile[key] != row[key] for key in ("profiles", "locations", "transfer_specs", "sink_boundaries"))
                or profile.get("annotation_audit") != row.get("annotation_audit")):
            raise ValueError("Exported profiles differ from bound annotation")
        if row.get("annotation_audit"):
            evidence_audit = row["annotation_audit"]
            if canonical_sha256(read_json(child(staging, evidence_audit["file"]))) != evidence_audit["sha256"]:
                raise ValueError("Exported location evidence audit differs from bound annotation")
        checks.append({"basename": row["basename"], "kind": row["kind"], "png_sha256": sha_file(png_path),
                       "svg_sha256": entry["svg_sha256"], "width": info["width"], "height": info["height"]})
    return checks


def export(run_dir: Path, staging: Path, *, skills_dir=None, node="node", node_modules: Path, browser=None, renderer=None,
           assistant_reviews=None):
    skills_dir = Path(skills_dir or REPOSITORY_ROOT / "dataset/skills").resolve()
    plan = build_export_plan(Path(run_dir), skills_dir, renderer=renderer, assistant_reviews=assistant_reviews)
    staging = _staging_directory(staging, run_dir, skills_dir)
    write_json(staging / "review-data.json", plan)
    write_json(staging / "render/input.json", render_samples(plan))
    for row in plan["cases"]:
        if row.get("annotation_audit"):
            evidence_audit = row["annotation_audit"]
            table = read_json(resolve_material_path(evidence_audit["source_file"]))
            if canonical_sha256(table) != evidence_audit["sha256"]:
                raise ValueError("Location evidence audit changed after export preparation")
            write_json(child(staging, evidence_audit["file"]), table)
        profile = {"schema_version": 5, "identity": EXPORT_IDENTITY, "profile_schema_version": SCHEMA_VERSION, "provenance": row["provenance"],
            "status": row["annotation_status"], "reason": row["annotation_reason"],
            "source_binding": row["source_binding"], "profiles": row["profiles"],
            "locations": row["locations"], "transfer_specs": row["transfer_specs"],
            "sink_boundaries": row["sink_boundaries"],
            "annotation_audit": row.get("annotation_audit"),
            "validation": row["validation"], "evidence_index": row["annotation_evidence_index"],
            "notice": "四字段标注与符号传播说明；未执行传播、风险或必要性判断。失败状态不补造 profile。"}
        write_json(staging / "security-profiles" / (row["basename"] + ".json"), profile)
        atomic_write_text(staging / row["suggestions_file"], suggestions(row))
    command = [str(node), str(BASELINE_TOOLS / "render_review_cfg.mjs"), "--input", str(staging / "render/input.json"),
        "--output-dir", str(staging / "ir-IPP"), "--svg-output-dir", str(staging / "render"),
        "--audit", str(staging / "render/audit.json"), "--node-modules", str(node_modules)]
    if browser:
        command += ["--browser", str(browser)]
    subprocess.run(command, check=True)
    for row in plan["cases"]:
        _png.bind_png_source(staging / row["png_file"], row["provenance"])
    checks = validate_staging(plan, staging)
    manifest = {"schema_version": 5, "identity": EXPORT_IDENTITY, "profile_schema_version": SCHEMA_VERSION, "run_id": plan["run_id"],
        "manifest_sha256": plan["manifest_sha256"], "experiment_result_sha256": plan["experiment_result_sha256"],
        "generators": {"exporter_sha256": sha_file(HERE),
                       "renderer_sha256": sha_file(BASELINE_TOOLS / "render_review_cfg.mjs")},
        "render_command": command,
        "checks": checks, "status": "passed", "visual_review": "pending", "published": False,
        "files": {p.relative_to(staging).as_posix(): sha_file(p) for p in sorted(staging.rglob("*")) if p.is_file()}}
    write_json(staging / "export-manifest.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--skills-dir", type=Path, default=REPOSITORY_ROOT / "dataset/skills")
    parser.add_argument("--node", default="node")
    parser.add_argument("--node-modules", type=Path, required=True)
    parser.add_argument("--browser", type=Path)
    parser.add_argument("--renderer", type=Path, help="Lean verifier, not an alternative graph renderer")
    parser.add_argument("--assistant-reviews", type=Path, help="External post-hoc assistant reviews, keyed by 001.json through 030.json")
    args = parser.parse_args()
    result = export(args.run_dir, args.staging, skills_dir=args.skills_dir, node=args.node,
                    node_modules=args.node_modules, browser=args.browser, renderer=args.renderer,
                    assistant_reviews=args.assistant_reviews)
    print(json.dumps({"status": result["status"], "cases": len(result["checks"]), "staging": str(args.staging)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
