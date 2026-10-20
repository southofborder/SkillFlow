"""Frozen input components and exact material ownership, without aggregate copies."""
from __future__ import annotations

from pathlib import Path
import json

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.common.upstream import checked_run_path, resolve_run_reference
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.material import checked_material


def read_component(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Non-JSON number: " + value)
    return json.loads(checked_run_path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=invalid)


def write_material_parts(directory, material, writer, *, include_source=True, authored_task=False):
    """Persist only components owned here; a byte snapshot already owns source."""
    directory = checked_run_path(directory)
    material = checked_material(material)
    if include_source and not (directory / "inputs/snapshot.json").is_file():
        writer.json(directory / "inputs/source.json", material["source"])
    for field, filename in (("cfg", "cfg.json"), ("runtime_contract", "runtime-contract.json"),
                            ("user_request", "user-request.json")):
        writer.json(directory / "inputs" / filename, material[field])
    if authored_task:
        writer.json(directory / "inputs/task.json", material["task"])


def read_source_parts(directory):
    """Read the one owner of source/graph/runtime/request, before Task resolution."""
    directory = checked_run_path(directory)
    source = (read_snapshot(directory)[1] if (directory / "inputs/snapshot.json").is_file()
              else read_component(directory / "inputs/source.json"))
    return {"source": source, "cfg": read_component(directory / "inputs/cfg.json"),
            "runtime_contract": read_component(directory / "inputs/runtime-contract.json"),
            "user_request": read_component(directory / "inputs/user-request.json")}


def read_material_parts(directory, *, task_baseline=None):
    parts = read_source_parts(directory)
    if task_baseline is None:
        manifest = read_component(checked_run_path(directory) / "manifest.json")
        reference = manifest.get("task_run_ref")
        if reference is None:
            if manifest.get("task_origin") != "authored_fixture":
                raise ValueError("Prepared annotation requires an explicit independent Task owner")
            task_baseline = read_component(checked_run_path(directory) / "inputs/task.json")
        else:
            from skillflow.task.runner import load_task_run
            task_baseline = load_task_run(resolve_run_reference(directory, reference))["task"]
    return checked_material({"version": SCHEMA_VERSION, **parts, "task": task_baseline})


def _material_chain(run_dir):
    directory, seen, chain = checked_run_path(run_dir), set(), []
    from skillflow.propagation.annotation.runner import IDENTITY as annotation_identity
    from skillflow.propagation.review.refinement import IDENTITY as refinement_identity
    from skillflow.pipeline import IDENTITY as pipeline_identity
    supported = {annotation_identity, refinement_identity, pipeline_identity}
    while True:
        if directory in seen:
            raise ValueError("Cyclic material ownership reference")
        seen.add(directory)
        manifest = read_component(directory / "manifest.json")
        if manifest.get("identity") not in supported:
            raise ValueError("Unsupported prepared material owner")
        if canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_sha256"}) != manifest.get("manifest_sha256"):
            raise ValueError("Material owner manifest identity differs")
        if manifest.get("preparation_status") != "ready":
            raise ValueError("Material owner preparation did not complete")
        inventory = {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
                     for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}
        if inventory != manifest.get("files"):
            raise ValueError("Material owner frozen inputs differ")
        chain.append((directory, manifest))
        if manifest.get("upstream") is None:
            return chain
        if any((directory / "inputs" / name).exists() for name in
               ("source.json", "snapshot.json", "package", "cfg.json", "runtime-contract.json", "user-request.json", "material.json", "task.json")):
            raise ValueError("Referenced source and graph must not be duplicated")
        directory = resolve_run_reference(directory, manifest["upstream"])


def resolve_material_owner(run_dir):
    return _material_chain(run_dir)[-1][0]


def load_prepared_material(run_dir, *, task_baseline=None):
    """Resolve each stage's Task separately; a revised Task never reuses old goals."""
    chain = _material_chain(run_dir)
    parts = read_source_parts(chain[-1][0])
    current = None
    for directory, manifest in chain:
        from skillflow.pipeline import IDENTITY as pipeline_identity
        if manifest["identity"] == pipeline_identity:
            continue
        reference = manifest.get("task_run_ref")
        if reference is None:
            if manifest.get("task_origin") == "authored_fixture_reference":
                owner = resolve_run_reference(directory, manifest["task_owner_ref"])
                source_manifest = read_component(owner / "manifest.json")
                if source_manifest.get("task_origin") != "authored_fixture":
                    raise ValueError("Authored Task reference must point to its explicit owner")
                task = read_component(owner / "inputs/task.json")
            elif manifest.get("task_origin") == "authored_fixture":
                task = read_component(directory / "inputs/task.json")
            else:
                raise ValueError("Missing independent Task run reference")
        else:
            from skillflow.task.runner import load_task_run
            task = load_task_run(resolve_run_reference(directory, reference))["task"]
        value = checked_material({"version": SCHEMA_VERSION, **parts, "task": task})
        if manifest.get("material_sha256") != canonical_sha256(value):
            raise ValueError("Prepared material content identity differs")
        if current is None:
            current = value
    if task_baseline is not None:
        return checked_material({"version": SCHEMA_VERSION, **parts, "task": task_baseline})
    if current is None:
        raise ValueError("Source-only owner has no selected Task; supply the sealed Task explicitly")
    return current


def resolve_task_owner(run_dir):
    directory = checked_run_path(run_dir)
    manifest = read_component(directory / "manifest.json")
    reference = manifest.get("task_run_ref")
    if reference is None:
        if manifest.get("task_origin") == "authored_fixture":
            return None
        raise ValueError("No independent Task owner is bound to this stage")
    return resolve_run_reference(directory, reference)
