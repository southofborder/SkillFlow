"""Explicit, immutable reuse of accepted upstream material in a fresh owner.

This is material import, not replay or migration of an older guided protocol.
Old source, Task and stage artifacts retain their producer identities. Only the
new root and downstream stages belong to the current implementation.
"""
import json
import shutil
from pathlib import Path

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256, implementation_provenance, now, sha_file
from skillflow.common.upstream import checked_run_path, resolve_run_reference
from .online import (analysis_config, checked_manifest, file_reference, read, resolve_file, seal)
from .accepted_stage_reader import accepted_stage_value, checked_task_artifacts

IDENTITY = "skillflow-accepted-upstream-v1"
PATH = "accepted-upstream.json"
_PARENTS = {"skillflow-document-guided-run-v16", "skillflow-document-guided-run-v17", "skillflow-document-guided-run-v18",
            "skillflow-document-guided-run-v19", "skillflow-document-guided-run-v20", "skillflow-document-guided-run-v21",
            "skillflow-document-guided-run-v22", "skillflow-document-guided-run-v23"}
_STEPS = {"skillflow-document-step-v13", "skillflow-document-step-v14", "skillflow-document-step-v15",
          "skillflow-document-step-v16", "skillflow-document-step-v17", "skillflow-document-step-v18",
          "skillflow-document-step-v19", "skillflow-document-step-v20"}
_SOURCE = "skillflow-document-source-v6"
_EXCLUDED = {".runner.lock", "execution-boundary.json", "report.md"}
MAX_LINEAGE = 8


def _inside(root, path):
    path = checked_run_path(path)
    if not path.is_relative_to(root):
        raise ValueError("Accepted upstream reference escapes its declared owner")
    return path


def _relative(root, name):
    if (not isinstance(name, str) or not name or "\\" in name or Path(name).is_absolute() or Path(name).drive
            or any(part in {".", ".."} for part in name.split("/")) or Path(name).as_posix() != name):
        raise ValueError("Accepted upstream requires normalized relative artifact paths")
    return _inside(root, root / name)


def _receipt(root):
    manifest = read(root / "manifest.json")
    reference = manifest.get("accepted_upstream")
    if reference is None:
        return None
    path = _inside(root, resolve_file(root, reference))
    if path != root / PATH:
        raise ValueError("Accepted upstream receipt has an unexpected location")
    receipt = read(path)
    keys = {"identity", "parent_directory", "parent_identity", "parent_implementation", "config", "source_sha256",
        "files", "owners", "cfg_file", "certificate", "inherited_logical_calls", "inherited_stages", "fresh_normal_stages",
        "created_at", "copied_files"}
    if (set(receipt) != keys or receipt.get("identity") != IDENTITY
            or receipt["parent_identity"] not in _PARENTS or receipt["config"] != manifest["config"]
            or receipt["inherited_stages"] != ["task", "flow", "graph"]
            or receipt["fresh_normal_stages"] != ["processing", "task-correspondence", "sensitivity", "review"]
            or not isinstance(receipt["owners"], dict) or set(receipt["owners"]) != {"task", "flow", "graph"}):
        raise ValueError("Accepted upstream policy or identity differs")
    for table in (receipt["files"], receipt["copied_files"]):
        if not isinstance(table, dict) or not table:
            raise ValueError("Accepted upstream requires a complete copied file inventory")
        for name, digest in table.items():
            _relative(root, name)
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise ValueError("Accepted upstream artifact digest is malformed")
    for name, digest in receipt["copied_files"].items():
        if sha_file(_relative(root, name)) != digest:
            raise ValueError("Accepted upstream bytes changed: " + name)
    for name, digest in receipt["files"].items():
        if receipt["copied_files"].get("inherited/" + name) != digest:
            raise ValueError("Accepted upstream donor inventory is not copied completely")
    for name in receipt["owners"].values():
        if not isinstance(name, str) or not name.startswith("inherited/"):
            raise ValueError("Accepted upstream owner is outside its copied donor")
        _relative(root, name)
    return receipt


def _lineage(root):
    """Bind every copied ancestor receipt; never follow an external parent path."""
    current, paths = root, []
    for depth in range(MAX_LINEAGE + 1):
        manifest = read(current / "manifest.json")
        if manifest.get("identity") not in _PARENTS:
            raise ValueError("Unsupported accepted upstream ancestor identity")
        checked_manifest(current, manifest["identity"])
        receipt = _receipt(current)
        if receipt is None:
            return paths
        if depth == MAX_LINEAGE:
            raise ValueError("Accepted upstream lineage exceeds the supported depth")
        paths.extend((current / PATH, current / "inherited/manifest.json"))
        paths.extend(_relative(current, name) for name in receipt["copied_files"])
        donor = current / "inherited"
        original = read(donor / "manifest.json")
        if original.get("identity") != receipt["parent_identity"] or original.get("implementation") != receipt["parent_implementation"]:
            raise ValueError("Accepted upstream declared producer differs from its copied manifest")
        current = donor
    raise AssertionError("Unreachable lineage bound")


def _owner(parent, name):
    direct = parent / "steps" / name
    if (direct / "manifest.json").is_file():
        return direct
    receipt = _receipt(parent)
    if receipt is None:
        raise ValueError("Accepted upstream stage owner is unavailable: " + name)
    return _inside(parent, parent / receipt["owners"][name])


def _accepted_step(owner, *, kind, config, source):
    identity = read(owner / "manifest.json").get("identity")
    if identity not in _STEPS:
        raise ValueError("Unsupported accepted document-step identity")
    manifest = checked_manifest(owner, identity)
    result = read(owner / "result.json")
    if (manifest.get("kind") != kind or manifest.get("config") != config
            or "status" in result or result.get("accepted_call") is None):
        raise ValueError("Inherited step must have a complete accepted value and matching configuration")
    return accepted_stage_value(owner, manifest, source=source)


def _accepted_graph(owner, *, config, source):
    kind = read(owner / "manifest.json")["kind"]
    if kind == "graph_facts_v1":
        return _accepted_step(owner, kind=kind, config=config, source=source)["cfg"]
    candidate = _accepted_step(owner, kind="cfg_wire_v5", config=config, source=source)
    from skillflow.graph.extraction.compiler import compile_candidate
    compiled = compile_candidate(candidate)
    if not compiled.ok:
        raise ValueError("Accepted upstream CFG no longer compiles")
    return json.loads(compiled.cfg.to_json())


def _collect_tree(parent, owner, files, *, source=False):
    _inside(parent, owner)
    for path in sorted(owner.rglob("*")):
        relative = path.relative_to(owner)
        if not path.is_file() or (not source and (path.name in _EXCLUDED or "replay" in relative.parts)):
            continue
        path = _inside(parent, path)
        files[path.relative_to(parent).as_posix()] = sha_file(path)


def describe_accepted_upstream(parent, *, config=None):
    """Read accepted receipts and validate the selected CFG, without stage execution."""
    parent = checked_run_path(parent)
    identity = read(parent / "manifest.json").get("identity")
    if identity not in _PARENTS:
        raise ValueError("Unsupported accepted guided producer identity")
    manifest = checked_manifest(parent, identity)
    lineage = _lineage(parent)
    config = analysis_config(config or manifest["config"])
    result, selection = read(parent / "result.json"), read(parent / "selection.json")
    if result.get("identity") != identity:
        raise ValueError("Accepted upstream parent result identity differs")
    if result.get("status") not in {"complete", "partial"} or manifest.get("config") != config:
        raise ValueError("Accepted upstream requires a terminal selected parent with matching configuration")
    source = parent / "source"
    if resolve_file(parent, manifest["source"]) != source / "manifest.json":
        raise ValueError("Parent source owner differs from its manifest")
    checked_manifest(source, _SOURCE)
    snapshot = read_snapshot(source)[1]
    task_path = _inside(parent, resolve_file(parent, selection["task"]))
    cfg_path = _inside(parent, resolve_file(parent, selection["cfg"]))
    if task_path.name != "task.json" or cfg_path not in {
            parent / "graph/initial.json", parent / "graph/revision.json"}:
        raise ValueError("Accepted upstream selection does not identify a supported Task/CFG owner")
    task_owner = task_path.parent
    task_manifest = checked_manifest(task_owner, "skillflow-task-extraction-v3")
    task_result = read(task_owner / "result.json")
    if (task_result.get("status") != "complete" or not task_result.get("accepted_call")
            or task_manifest.get("config") != config or task_manifest.get("identity") != "skillflow-task-extraction-v3"):
        raise ValueError("Inherited Task lacks a complete accepted source-only result")
    checked_task_artifacts(task_owner, task_manifest, task_result, source=snapshot)
    graph_owner = (_owner(parent, "graph") if cfg_path.name == "initial.json"
                   else parent / "steps/revision-graph")
    flow_owner = _owner(parent, "flow")
    files = {}
    _collect_tree(parent, source, files, source=True)
    for owner in (task_owner, flow_owner, graph_owner):
        _collect_tree(parent, owner, files)
    # Preserve each selected stage's original source owner and relative references.
    for owner in (task_owner, flow_owner, graph_owner):
        saved = read(owner / "manifest.json")
        source_ref = saved.get("source_owner", saved.get("context", {}).get("source_owner"))
        if source_ref is None:
            raise ValueError("Inherited semantic material lacks an explicit source owner")
        owner_source = _inside(parent, resolve_run_reference(owner, source_ref))
        checked_manifest(owner_source, _SOURCE)
        if read_snapshot(owner_source)[1] != snapshot:
            raise ValueError("Inherited semantic stages belong to different source snapshots")
        _collect_tree(parent, owner_source, files, source=True)
        if owner in (flow_owner, graph_owner):
            if set(saved.get("context", {})) != {"source_owner"}:
                raise ValueError("Inherited flow/graph has an unsupported context owner")
            expected_dependencies = [owner_source / "manifest.json"]
            if owner == graph_owner:
                expected_dependencies.append(flow_owner / "result.json")
                if len(saved.get("dependencies", [])) > 2:
                    raise ValueError("Accepted upstream does not support a selected graph with additional failed-stage recovery dependencies")
            if [_inside(parent, resolve_file(owner, ref)) for ref in saved.get("dependencies", [])] != expected_dependencies:
                raise ValueError("Inherited graph/flow dependencies differ from the selected source and flow")
        for ref in saved.get("dependencies", []):
            dependency = _inside(parent, resolve_file(owner, ref))
            files[dependency.relative_to(parent).as_posix()] = sha_file(dependency)
    _accepted_step(flow_owner, kind="flow_document", config=config, source=snapshot)
    graph = _accepted_graph(graph_owner, config=config, source=snapshot)
    if read(cfg_path) != {"cfg": graph} or read(parent / "graph/selected.json") != {"cfg": graph}:
        raise ValueError("Retained CFG differs from the accepted selected graph candidate")
    for path in lineage:
        files[path.relative_to(parent).as_posix()] = sha_file(path)
    for name in ("manifest.json", "result.json", "selection.json", "graph/selected.json"):
        files[name] = sha_file(parent / name)
    files[cfg_path.relative_to(parent).as_posix()] = sha_file(cfg_path)
    certificate = cfg_path.parent / cfg_path.stem / "controlled.json"
    if certificate.is_file():
        files[certificate.relative_to(parent).as_posix()] = sha_file(certificate)
    return {"identity": IDENTITY, "parent_directory": str(parent),
        "parent_identity": identity, "parent_implementation": manifest["implementation"],
        "config": config, "source_sha256": snapshot["source_sha256"], "files": files,
        "owners": {"task": task_owner.relative_to(parent).as_posix(),
                   "flow": flow_owner.relative_to(parent).as_posix(),
                   "graph": graph_owner.relative_to(parent).as_posix()},
        "cfg_file": cfg_path.relative_to(parent).as_posix(),
        "certificate": certificate.relative_to(parent).as_posix() if certificate.is_file() else None,
        "inherited_logical_calls": sum(name.endswith("/call.json") for name in files),
        "inherited_stages": ["task", "flow", "graph"],
        "fresh_normal_stages": ["processing", "task-correspondence", "sensitivity", "review"]}


def prepare_from_accepted_cfg(parent, *, run_dir, config=None):
    """Create a new processing-onward run; never modify or execute the parent."""
    from .runner import IDENTITY as GUIDED, POLICY, WRITER, _initial, _save
    parent, run = checked_run_path(parent), checked_run_path(run_dir)
    if run.exists() or run.is_relative_to(parent) or parent.is_relative_to(run):
        raise ValueError("Accepted-upstream preparation requires a separate nonexistent directory")
    description = describe_accepted_upstream(parent, config=config)
    run.mkdir(parents=True, exist_ok=False)
    copies = {}
    for name, digest in description["files"].items():
        original, target = parent / name, run / "inherited" / name
        if sha_file(original) != digest:
            raise ValueError("Accepted upstream changed during copying")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        copies[target.relative_to(run).as_posix()] = digest
    for path in sorted((run / "inherited/source").rglob("*")):
        if path.is_file():
            target = run / "source" / path.relative_to(run / "inherited/source")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            copies[target.relative_to(run).as_posix()] = sha_file(path)
    cfg = run / "graph/initial.json"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(parent / description["cfg_file"], cfg)
    copies["graph/initial.json"] = sha_file(cfg)
    if description["certificate"] is not None:
        target = run / "graph/initial/controlled.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(parent / description["certificate"], target)
        copies[target.relative_to(run).as_posix()] = sha_file(target)
    receipt = {**description, "created_at": now(), "copied_files": copies,
        "owners": {key:"inherited/"+name for key,name in description["owners"].items()}}
    WRITER.json(run / PATH, receipt)
    manifest = seal({"identity": GUIDED, "created_at": now(), "policy": POLICY,
        "implementation": implementation_provenance(), "config": description["config"],
        "files": {PATH:sha_file(run / PATH)}, "source":file_reference(run,run / "source/manifest.json"),
        "accepted_upstream":file_reference(run,run / PATH)})
    WRITER.json(run / "manifest.json", manifest)
    _save(run, _initial())
    try:
        load_accepted_upstream(run)
    except Exception as error:
        failure = {"status": "failed", "phase": "accepted_upstream", "error_type": type(error).__name__, "reason": str(error)}
        WRITER.json(run / "preparation-failure.json", failure)
        _save(run, {**_initial(), "status": "failed", "stage": "accepted_upstream", "reason": str(error)})
        raise
    return manifest


def load_accepted_upstream(run):
    """Verify copied evidence and expose upstream values; never create clients."""
    run = checked_run_path(run)
    manifest = read(run / "manifest.json")
    reference = manifest.get("accepted_upstream")
    if reference is None:
        return {}
    receipt = _receipt(run)
    _lineage(run)
    donor = describe_accepted_upstream(run / "inherited", config=manifest["config"])
    for key, value in donor.items():
        if key == "parent_directory":
            continue
        expected = {name: "inherited/" + path for name, path in value.items()} if key == "owners" else value
        if receipt.get(key) != expected:
            raise ValueError("Accepted upstream receipt differs from its verified copied donor: " + key)
    source = read_snapshot(run / "source")[1]
    if source["source_sha256"] != receipt["source_sha256"]:
        raise ValueError("Accepted upstream source identity differs")
    owners = {key:_inside(run,run/name) for key,name in receipt["owners"].items()}
    if set(owners) != {"task","flow","graph"}:
        raise ValueError("Accepted upstream has incomplete stage owners")
    from skillflow.task.runner import load_task_run
    task = load_task_run(owners["task"])["task"]
    flow = _accepted_step(owners["flow"],kind="flow_document",config=manifest["config"],source=source)
    graph = _accepted_graph(owners["graph"], config=manifest["config"], source=source)
    if read(run / "graph/initial.json") != {"cfg":graph}:
        raise ValueError("Retained initial CFG differs from its accepted candidate")
    certificate_origin = None
    if donor["certificate"] is not None:
        name = donor["certificate"]
        digest = donor["files"][name]
        if receipt["copied_files"].get("graph/initial/controlled.json") != digest:
            raise ValueError("Retained graph certificate differs from its verified donor")
        certificate_origin = {"path": "inherited/" + name, "sha256": digest}
    return {"task":{"value":task,"path":owners["task"] / "task.json","owner":owners["task"]},
        "flow":{"value":flow,"path":owners["flow"] / "result.json","step":owners["flow"]},
        "graph":{"value":graph,"path":run / "graph/initial.json", "certificate_origin":certificate_origin}}
