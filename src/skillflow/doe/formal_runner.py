"""Formal, deterministic DOE from one verified accepted joint annotation.

Upstream calls remain in the selected annotation. This stage binds its verified
propagation dependency and stores only its own analysis and restoration facts.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath
import re

from skillflow.common.artifact_io import atomic_write_text
from skillflow.common.recording import canonical_sha256, implementation_provenance, sha_file
from skillflow.common.runs import exclusive_run
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.common.source_evidence import _json_object
from skillflow.propagation.contracts.joint import joint_source_files
from skillflow.propagation.contracts.sensitivity import extract_sensitivity_candidate
from skillflow.propagation.runner import load_propagation_materials

from .demand_material import checked_demand_material, validate_demand_result
from .sensitivity_material import (SensitivityReview, build_sensitivity_index,
    prepare_joint_sensitivity_review, validate_sensitivity_result, joint_demands)
from .sensitivity_report import render_html, render_markdown


IDENTITY = "skillflow-doe-run-v4"
FORMAT_VERSION = 4
_MARKER = ".preparing.json"
_ARTIFACTS = frozenset({"audit/index.json",
    "audit/demand-support.json", "doe-result.json", "report.html", "report.md"})
_POLICY = {"offline": True, "model_calls": 0, "execute_skill": False,
    "candidate_origin": "model_annotation", "declaration_coverage": "explicit_declarations_only",
    "global_minimality_proof": False, "indispensability_proof": False}
_SHARED_SINK_FIELDS = frozenset({"id", "boundary", "actual_payload", "related_requirements"})


def _read(path):
    return _json_object(Path(path).read_bytes().decode("utf-8"))


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _signed(value):
    return {**value, "manifest_sha256": canonical_sha256(value)}


def _check_signed(value, label):
    if value.get("manifest_sha256") != canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"}):
        raise ValueError(label + " digest mismatch")


def _is_link(path):
    return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)


def _directory(run_dir):
    path = Path(run_dir).expanduser().absolute()
    for item in (path, *path.parents):
        if (item.exists() or item.is_symlink()) and _is_link(item):
            raise ValueError("Formal DOE does not follow directory links")
    if path.exists() and not path.is_dir():
        raise ValueError("Formal DOE run must be a directory")
    path = path.resolve()
    if path.exists() and any(_is_link(item) for item in path.rglob("*")):
        raise ValueError("Formal DOE does not follow artifact links")
    return path


def _check_implementation(value) -> None:
    if (not isinstance(value, dict) or set(value) != {"files", "sha256", "python"}
            or not isinstance(value["files"], dict) or not isinstance(value["python"], str)
            or any(not isinstance(name, str) or not isinstance(digest, str)
                   or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                   for name, digest in value["files"].items())
            or value["sha256"] != canonical_sha256(value["files"])):
        raise ValueError("DOE preparation implementation provenance differs")


def _inventory(directory, *, resumable):
    allowed = _ARTIFACTS | {_MARKER, ".runner.lock"} if resumable else {".runner.lock"}
    parents = {parent.as_posix() for name in allowed for parent in PurePosixPath(name).parents
               if parent.as_posix() != "."}
    for path in directory.rglob("*"):
        relative = path.relative_to(directory).as_posix()
        if _is_link(path):
            raise ValueError("Formal DOE does not follow artifact links")
        if path.is_dir():
            if relative not in parents:
                raise ValueError("Formal DOE requires a new or matching interrupted directory")
            continue
        temporary = re.fullmatch(r"\.(.+)\.[0-9a-f]{32}\.tmp", path.name)
        owner = (path.parent / temporary.group(1)).relative_to(directory).as_posix() if temporary else None
        if relative not in allowed and not (resumable and owner in allowed):
            raise ValueError("Formal DOE requires a new or matching interrupted directory")


def _write_matching(path, text):
    if path.exists() and path.read_bytes() != text.encode("utf-8"):
        raise ValueError("Interrupted formal DOE artifact differs: " + path.name)
    atomic_write_text(path, text)


def _model_bundle(run_dir):
    loaded = load_propagation_materials(run_dir)
    if (loaded.provenance.get("kind") != "model_annotation"
            or not loaded.upstream_identity.get("accepted_response_sha256")):
        raise ValueError("Formal DOE requires an accepted model annotation, not an offline candidate")
    return loaded


def _demand_support(demand, result):
    """Keep only demand-specific checks; shared derivations/payloads live once."""
    return {key: deepcopy(value) for key, value in demand.items()
            if key not in {"goals", "derivations", "sinks"}} | {
        "extra_derivations": {key: deepcopy(value) for key, value in demand["derivations"].items()
                              if key not in result["derivations"]["demand"]},
        "sinks": [{key: deepcopy(value) for key, value in sink.items()
                   if key not in _SHARED_SINK_FIELDS - {"id"}} for sink in demand["sinks"]]}


def _restore_demand(result, support, annotation):
    if set(support) != {"schema_version", "status", "coverage", "diagnostics", "sinks", "extra_derivations", "traceability"}:
        raise ValueError("Formal DOE demand support fields differ")
    sinks = {sink["id"]: sink for sink in result["sinks"]}
    if ([sink["id"] for sink in support["sinks"]] != [sink["id"] for sink in result["sinks"]]
            or any(set(sink) != {"id", "demanded_information", "conservative_retention",
                                "unestablished_ranges", "limitations"} for sink in support["sinks"])):
        raise ValueError("Formal DOE demand support coverage differs")
    if set(support["extra_derivations"]) & set(result["derivations"]["demand"]):
        raise ValueError("Formal DOE demand support duplicates shared derivations")
    value = {**{key: deepcopy(value) for key, value in support.items() if key != "extra_derivations"},
        "goals": deepcopy(annotation["compiled_annotation"]["demands"]),
        "derivations": {**deepcopy(support["extra_derivations"]), **deepcopy(result["derivations"]["demand"])},
        "sinks": [{**{key: deepcopy(sinks[row["id"]][key]) for key in _SHARED_SINK_FIELDS},
                   **deepcopy(row)} for row in support["sinks"]]}
    return validate_demand_result(value)


def _index_snapshot(index):
    """Persist generated coordinates; declarations remain in the raw annotation."""
    return {"declarations": {identifier: {key: deepcopy(row[key]) for key in
            ("instruction_id", "scope_path", "declaration_index")}
            for identifier, row in index["declarations"].items()}}


def _validate(result, index, support, facts, annotation):
    task = annotation["task"]
    demands = joint_demands(annotation)
    candidate = extract_sensitivity_candidate(annotation["raw_annotation"])
    facts, _task, annotation, _files = checked_demand_material(facts, task, annotation)
    full_index = build_sensitivity_index(annotation, candidate)
    if canonical_sha256(index) != canonical_sha256(_index_snapshot(full_index)):
        raise ValueError("Formal DOE declaration index differs from joint annotation")
    demand = _restore_demand(result, support, annotation)
    validate_sensitivity_result(result, facts, task, annotation, demands, candidate, demand_result=demand)
    return SensitivityReview(deepcopy(result), full_index, demand)


def _checked_task_provenance(annotation, provenance):
    """Keep processing acceptance distinct from the sealed Task's origin."""
    expected_sha = annotation["task"]["task_sha256"]
    value = deepcopy(provenance.get("task_provenance", {
        "kind": "unknown", "task_sha256": expected_sha}))
    if (not isinstance(value, dict) or set(value) != {"kind", "task_sha256"}
            or value["kind"] not in {"independent_task_run", "authored_fixture", "unknown"}
            or value["task_sha256"] != expected_sha):
        raise ValueError("DOE Task provenance differs from its sealed Task")
    return value


def _metadata(result, annotation, provenance):
    return {"candidate_origin": "model_annotation", "declaration_source": "accepted_joint_annotation",
        "task_provenance": _checked_task_provenance(annotation, provenance),
        "status": result["status"], "model_calls": 0, "sink_count": len(result["sinks"]),
        "declaration_count": result["coverage"]["declarations"],
        "diagnostic_count": len(result["diagnostics"]), "business_filename": "doe-result.json"}


def _report_metadata(result, annotation, demand, provenance):
    return {**_metadata(result, annotation, provenance), "task": deepcopy(annotation["task"]),
        "source_files": joint_source_files(annotation["material"]), "demand": deepcopy(demand)}


def run_doe(propagation_run, *, run_dir):
    """Freeze a checked model-derived propagation run and compute DOE once.

    No Task, demand or sensitivity override is accepted. Restarts re-use a
    matching committed result; interrupted saves can resume with identical input.
    """
    directory = _directory(run_dir)
    upstream = checked_run_path(propagation_run)
    if directory.is_relative_to(upstream) or upstream.is_relative_to(directory):
        raise ValueError("Formal DOE outputs cannot overlap propagation inputs")
    loaded = _model_bundle(upstream)
    facts, annotation = loaded, loaded.annotation
    expected = {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
        "upstream": make_run_reference(directory, upstream),
        "upstream_identity": loaded.upstream_identity,
        "implementation": implementation_provenance()}
    with exclusive_run(directory):
        if (directory / "manifest.json").exists():
            stored = load_doe_run(directory)
            if any(canonical_sha256(stored["manifest"].get(key)) != canonical_sha256(value)
                   for key, value in expected.items()):
                raise ValueError("Existing formal DOE input or implementation differs")
            return stored
        marker_path = directory / _MARKER
        if marker_path.exists():
            marker = _read(marker_path)
            _check_signed(marker, "Formal DOE preparation marker")
            if (set(marker) != set(expected) | {"created_at", "manifest_sha256"}
                    or any(canonical_sha256(marker.get(k)) != canonical_sha256(v)
                           for k, v in expected.items())):
                raise ValueError("Interrupted formal DOE input or implementation differs")
            _inventory(directory, resumable=True)
        else:
            _inventory(directory, resumable=False)
            marker = _signed({**expected, "created_at": _now()})
            atomic_write_text(marker_path, _json(marker))
        # One demand worklist, then sensitivity uses that same solved demand.
        review = prepare_joint_sensitivity_review(facts, annotation)
        result, index = review.to_dict(), _index_snapshot(review.index_dict())
        support = _demand_support(review.demand_dict(), result)
        _validate(result, index, support, facts, annotation)
        values = {"audit/index.json": index, "audit/demand-support.json": support, "doe-result.json": result}
        for name, value in values.items():
            _write_matching(directory / name, _json(value))
        metadata = _report_metadata(result, annotation, review.demand_dict(), loaded.provenance)
        _write_matching(directory / "report.html", render_html(review, metadata=metadata))
        _write_matching(directory / "report.md", render_markdown(review, metadata=metadata))
        fresh = _model_bundle(upstream)
        if canonical_sha256(fresh.upstream_identity) != canonical_sha256(loaded.upstream_identity):
            raise ValueError("Propagation material changed during formal DOE preparation")
        manifest = _signed({**expected, "created_at": marker["created_at"], "committed_at": _now(),
            "status": result["status"], "metadata": _metadata(result, annotation, loaded.provenance),
            "result_sha256": canonical_sha256(result), "index_sha256": canonical_sha256(index),
            "support_sha256": canonical_sha256(support),
            "artifacts": {name: sha_file(directory / name) for name in sorted(_ARTIFACTS)},
            "policy": deepcopy(_POLICY)})
        _load_materials(directory, manifest)
        atomic_write_text(directory / "manifest.json", _json(manifest))
        return load_doe_run(directory)


def _load_materials(directory, manifest):
    if (manifest.get("identity") != IDENTITY or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] != FORMAT_VERSION):
        raise ValueError("Unsupported formal DOE run version")
    _check_signed(manifest, "Formal DOE manifest")
    if set(manifest) != {"identity", "schema_version", "upstream", "upstream_identity",
        "implementation", "created_at", "committed_at", "status", "metadata",
        "result_sha256", "index_sha256", "support_sha256", "artifacts", "policy", "manifest_sha256"}:
        raise ValueError("Formal DOE manifest fields differ")
    _check_implementation(manifest["implementation"])
    if (canonical_sha256(manifest["policy"]) != canonical_sha256(_POLICY)
            or set(manifest["artifacts"]) != _ARTIFACTS):
        raise ValueError("Formal DOE policy or artifact inventory differs")
    for name, digest in manifest["artifacts"].items():
        if sha_file(directory / name) != digest:
            raise ValueError("Formal DOE artifact digest mismatch: " + name)
    result, index = _read(directory / "doe-result.json"), _read(directory / "audit/index.json")
    support = _read(directory / "audit/demand-support.json")
    for key, value in (("result", result), ("index", index), ("support", support)):
        if canonical_sha256(value) != manifest[key + "_sha256"]:
            raise ValueError("Formal DOE " + key + " digest mismatch")
    # Upstream owns accepted call recovery. Never relabel an authored fixture as
    # a model response, and never silently substitute another propagation run.
    upstream = _model_bundle(resolve_run_reference(directory, manifest["upstream"]))
    if canonical_sha256(upstream.upstream_identity) != canonical_sha256(manifest["upstream_identity"]):
        raise ValueError("Formal DOE input differs from verified propagation material")
    facts, annotation = upstream, upstream.annotation
    review = _validate(result, index, support, facts, annotation)
    metadata = _metadata(result, annotation, upstream.provenance)
    if "task_provenance" not in manifest["metadata"]:
        # Existing current-format runs stay byte-for-byte intact. Their missing
        # field never means independent extraction; the checked origin is
        # exposed in the read-only return view below.
        metadata.pop("task_provenance")
    if (manifest["status"] != result["status"]
            or canonical_sha256(manifest["metadata"]) != canonical_sha256(metadata)):
        raise ValueError("Formal DOE status or metadata differs")
    return {"manifest": deepcopy(manifest), "materials": facts, "annotation": annotation,
            "result": result, "review": review, "support": support,
            "upstream_identity": deepcopy(upstream.upstream_identity),
            "task_provenance": _checked_task_provenance(annotation, upstream.provenance)}


def load_doe_run(run_dir):
    """Read frozen content and accepted upstream identity without solving."""
    directory = _directory(run_dir)
    return _load_materials(directory, _read(directory / "manifest.json"))


def replay_doe(run_dir):
    """Recompute once from frozen inputs; save no duplicate final result."""
    directory = _directory(run_dir)
    with exclusive_run(directory):
        loaded = load_doe_run(directory)
        current = implementation_provenance()
        if canonical_sha256(current) != canonical_sha256(loaded["manifest"]["implementation"]):
            raise ValueError("Formal DOE implementation identity changed")
        review = prepare_joint_sensitivity_review(loaded["materials"], loaded["annotation"])
        actual = {"result": review.to_dict(), "index": _index_snapshot(review.index_dict()),
                  "support": _demand_support(review.demand_dict(), review.to_dict())}
        differences = [key for key, value in actual.items()
                       if canonical_sha256(value) != loaded["manifest"][key + "_sha256"]]
        summary = {"identity": IDENTITY, "status": "mismatch" if differences else "matched",
            "replayed_at": _now(), "model_calls": 0, "differences": differences,
            "result_sha256": canonical_sha256(actual["result"]), "implementation_sha256": current["sha256"]}
        atomic_write_text(directory / "replay-summary.json", _json(summary))
        if differences:
            raise ValueError("Formal DOE replay differs; see replay-summary.json")
        return summary
