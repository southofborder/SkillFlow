"""Persist propagation facts once and resolve checked semantic inputs upstream."""
from __future__ import annotations

import json
from pathlib import Path

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.paths import project_root
from skillflow.common.recording import canonical_sha256, implementation_provenance, sha_file
from skillflow.common.runs import exclusive_run
from skillflow.common.source_evidence import _require_json
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.propagation.data import DataRegistry, export_identity_index, restore_registry
from skillflow.propagation.annotation.loading import load_annotation_run
from skillflow.propagation.annotation.runner import verify_prepared
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION as PROFILE_VERSION
from skillflow.propagation.loading import materials_from_result
from skillflow.propagation.facts import _normalized_cfg
from skillflow.propagation.models import FlowState
from skillflow.propagation.records import PropagationRecords, SCHEMA_VERSION as RECORD_VERSION
from skillflow.propagation.report import write_reports

IDENTITY = "skill-ir-propagation-v14"
FORMAT_VERSION = 14
POLICY = {"offline": True, "model_calls": 0, "execute_skill": False}
ARTIFACTS = frozenset({"data.json", "records.json", "sinks.json", "audit/requested-data.json",
    "audit/requested-state.json", "audit/initial-data.json", "audit/initial-state.json",
    "audit/data-identities.json", "audit/stats.json"})
MANIFEST_FIELDS = frozenset({"schema_version", "identity", "profile_schema_version", "records_schema_version",
    "upstream", "accepted_response_sha256", "implementation", "status", "coverage", "diagnostics",
    "artifacts", "policy", "manifest_sha256"})


def _read(path):
    checked_run_path(path)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f"Non-JSON number: {value}")
    result = json.loads(Path(path).read_bytes().decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid)
    _require_json(result, "")
    return result


def _calculate(cfg, annotation, seed, state):
    from skillflow.propagation.solver import propagate
    return propagate(cfg, annotation, initial_registry=DataRegistry.from_dict(seed) if seed is not None else None,
        initial_state=FlowState.model_validate(state) if state is not None else None)


def _task_provenance(loaded):
    """Derive Task origin from the verified annotation owner's binding.

    A descriptive task_origin label alone never establishes an independent
    extraction. load_annotation_run has already verified the referenced Task
    run or explicit authored owner, its accepted response and sealed Task.
    """
    binding = loaded["manifest"]
    if binding.get("task_run_ref") is not None:
        kind = "independent_task_run"
    elif binding.get("task_origin") in {"authored_fixture", "authored_fixture_reference"}:
        kind = "authored_fixture"
    else:
        kind = "unknown"
    return {"kind": kind, "task_sha256": loaded["material"]["task"]["task_sha256"]}


def _components(loaded, solved, *, manifest=None):
    return materials_from_result(solved, material=loaded["material"], raw_annotation=loaded["raw_annotation"],
        compiled_annotation=loaded["compiled_annotation"], mapping=loaded["mapping"],
        source_metadata=loaded["source_metadata"], manifest=manifest,
        provenance={"kind": "model_annotation", "task_provenance": _task_provenance(loaded),
                    "accepted_response_sha256": loaded["upstream_identity"]["accepted_response_sha256"]})


def _artifacts(facts, requested_data, requested_state):
    return {"data.json": facts.data, "records.json": facts.records, "sinks.json": facts.sinks,
        "audit/requested-data.json": requested_data, "audit/requested-state.json": requested_state,
        "audit/initial-data.json": facts.initial_data, "audit/initial-state.json": facts.initial_state,
        "audit/data-identities.json": export_identity_index(facts.registry), "audit/stats.json": facts.stats}


def _output_path(origin, run_dir):
    directory = checked_run_path(run_dir)
    if directory == origin or directory.is_relative_to(origin) or origin.is_relative_to(directory):
        raise ValueError("Propagation output cannot overlap its annotation input")
    repository = project_root()
    if any(directory == root or directory.is_relative_to(root)
           for root in (repository / "dataset", repository / "result")):
        raise ValueError("Propagation output cannot overwrite frozen inputs or delivery artifacts")
    return directory


def save_propagation_run(run_dir, *, annotation_run, solved, requested_data=None, requested_state=None,
                         writer=None, before_commit=None):
    """Commit validated components, keeping annotation and call-chain ownership upstream.

    An interrupted save has a preparation marker but no committed manifest. The
    same inputs may resume the save; existing mismatched artifacts are rejected.
    """
    origin = checked_run_path(annotation_run)
    directory = _output_path(origin, run_dir)
    loaded = load_annotation_run(origin)
    facts = _components(loaded, solved)
    values = _artifacts(facts, requested_data, requested_state)
    writer = writer or ArtifactWriter(())
    if writer.clean(values) != values:
        raise ValueError("Redaction would change checked propagation facts")
    upstream = make_run_reference(directory, origin)
    implementation = implementation_provenance()
    preparation = {"identity": IDENTITY, "upstream": upstream, "implementation": implementation,
        "accepted_response_sha256": facts.provenance["accepted_response_sha256"],
        "components": {name: canonical_sha256(value) for name, value in values.items()},
        "outcome": {"status": facts.status, "coverage": facts.coverage, "diagnostics": facts.diagnostics}}
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        marker = directory / "preparation.json"
        if (directory / "manifest.json").exists():
            raise ValueError("Propagation run is already committed")
        names = {path.name for path in directory.iterdir()} - {".runner.lock"}
        if marker.exists():
            if canonical_sha256(_read(marker)) != canonical_sha256(preparation):
                raise ValueError("Interrupted propagation preparation differs")
        elif names:
            raise ValueError("Propagation requires a new directory or its matching preparation")
        else:
            writer.json(checked_run_path(marker), preparation)
        for name, value in values.items():
            target = checked_run_path(directory / name)
            if target.exists():
                if canonical_sha256(_read(target)) != canonical_sha256(value):
                    raise ValueError("Interrupted propagation artifact differs: " + name)
            else:
                writer.json(target, value)
        write_reports(directory, facts, writer, annotation_run=origin)
        if before_commit is not None:
            before_commit()
        if make_run_reference(directory, origin) != upstream or load_annotation_run(origin)["upstream_identity"] != loaded["upstream_identity"]:
            raise ValueError("Annotation input changed during propagation save")
        for name, value in values.items():
            if canonical_sha256(_read(directory / name)) != canonical_sha256(value):
                raise ValueError("Saved propagation artifact changed before commit: " + name)
        manifest = {"schema_version": FORMAT_VERSION, "identity": IDENTITY,
            "profile_schema_version": PROFILE_VERSION, "records_schema_version": RECORD_VERSION,
            "upstream": upstream, "accepted_response_sha256": facts.provenance["accepted_response_sha256"],
            "implementation": implementation, "status": facts.status, "coverage": facts.coverage,
            "diagnostics": facts.diagnostics, "artifacts": {name: sha_file(directory / name) for name in sorted(ARTIFACTS)},
            "policy": POLICY}
        manifest["manifest_sha256"] = canonical_sha256(manifest)
        writer.json(checked_run_path(directory / "manifest.json"), manifest)
        marker.unlink()
    return _components(loaded, solved, manifest=manifest)


def run_propagation(annotation_run, *, run_dir, seed_data=None, initial_state=None):
    """Calculate using the current implementation and a checked accepted annotation."""
    origin = checked_run_path(annotation_run)
    _output_path(origin, run_dir)
    verified = verify_prepared(origin, replay=True)
    loaded = load_annotation_run(origin)
    if verified != loaded["manifest"] or verified["preparation_status"] != "ready":
        raise ValueError("Annotation changed or its preparation is incomplete")
    if isinstance(seed_data, (str, Path)):
        seed_data = _read(seed_data)
    seed = seed_data.to_dict() if isinstance(seed_data, DataRegistry) else seed_data
    if seed is not None:
        seed = DataRegistry.from_dict(seed).to_dict()
    if isinstance(initial_state, (str, Path)):
        initial_state = _read(initial_state)
    state = None if initial_state is None else FlowState.model_validate(initial_state).model_dump(mode="json")
    solved = _calculate(loaded["material"]["cfg"], to_payload(loaded["compiled_annotation"]), seed, state)
    def unchanged():
        if verify_prepared(origin, replay=True) != verified:
            raise ValueError("Annotation changed while calculating propagation")
    return save_propagation_run(run_dir, annotation_run=origin, solved=solved,
        requested_data=seed, requested_state=state, before_commit=unchanged)


def _load_run(run_dir):
    directory = checked_run_path(run_dir)
    manifest = _read(directory / "manifest.json")
    if (type(manifest) is not dict or set(manifest) != MANIFEST_FIELDS
            or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != FORMAT_VERSION
            or manifest.get("identity") != IDENTITY or manifest.get("profile_schema_version") != PROFILE_VERSION
            or manifest.get("records_schema_version") != RECORD_VERSION):
        raise ValueError("Unsupported propagation run version or manifest fields")
    if canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_sha256"}) != manifest["manifest_sha256"]:
        raise ValueError("Propagation manifest digest mismatch")
    if (canonical_sha256(manifest["policy"]) != canonical_sha256(POLICY)
            or type(manifest["artifacts"]) is not dict or set(manifest["artifacts"]) != ARTIFACTS):
        raise ValueError("Propagation policy or artifact inventory differs")
    producer = manifest["implementation"]
    if (not isinstance(producer, dict) or not isinstance(producer.get("files"), dict) or not producer["files"]
            or canonical_sha256(producer["files"]) != producer.get("sha256")):
        raise ValueError("Invalid propagation producer identity")
    origin = resolve_run_reference(directory, manifest["upstream"])
    loaded = load_annotation_run(origin)
    if manifest["accepted_response_sha256"] != loaded["upstream_identity"]["accepted_response_sha256"]:
        raise ValueError("Propagation accepted annotation identity differs")
    values = {}
    for name, digest in manifest["artifacts"].items():
        target = checked_run_path(directory / name)
        if sha_file(target) != digest:
            raise ValueError("Propagation artifact digest mismatch: " + name)
        values[name] = _read(target)
    for name in ("requested-data", "initial-data"):
        if values[f"audit/{name}.json"] is not None:
            DataRegistry.from_dict(values[f"audit/{name}.json"])
    for name in ("requested-state", "initial-state"):
        if values[f"audit/{name}.json"] is not None:
            FlowState.model_validate(values[f"audit/{name}.json"])
    registry = restore_registry(values["data.json"], values["audit/data-identities.json"])
    records = PropagationRecords.from_records(values["records.json"], cfg=_normalized_cfg(loaded["material"]["cfg"]),
        annotation=to_payload(loaded["compiled_annotation"]), data_registry=registry,
        initial_data=values["audit/initial-data.json"], initial_state=values["audit/initial-state.json"])
    from skillflow.propagation.solver import PropagationResult
    solved = PropagationResult(manifest["status"], registry, records, manifest["coverage"], manifest["diagnostics"],
        values["audit/stats.json"], values["audit/initial-data.json"], values["audit/initial-state.json"])
    facts = _components(loaded, solved, manifest=manifest)
    if canonical_sha256(facts.sinks) != canonical_sha256(values["sinks.json"]):
        raise ValueError("Saved sink inventory differs from evaluated records")
    if canonical_sha256(facts.diagnostics) != canonical_sha256(manifest["diagnostics"]):
        raise ValueError("Saved diagnostics differ from their normalized contract")
    if (canonical_sha256(_read(directory / "manifest.json")) != canonical_sha256(manifest)
            or any(sha_file(checked_run_path(directory / name)) != digest for name, digest in manifest["artifacts"].items())
            or make_run_reference(directory, origin) != manifest["upstream"]):
        raise ValueError("Propagation materials changed during read-only loading")
    return facts, values, origin


def load_propagation_materials(run_dir):
    """Read checked components; no source-implementation equality or model call."""
    return _load_run(run_dir)[0]


def replay_propagation(run_dir):
    """Recalculate from requested seeds; write only comparison and display artifacts."""
    directory = checked_run_path(run_dir)
    with exclusive_run(directory):
        saved, values, origin = _load_run(directory)
        if saved.manifest["implementation"] != implementation_provenance():
            raise ValueError("Propagation implementation identity changed")
        solved = _calculate(saved.cfg, to_payload(saved.compiled_annotation),
            values["audit/requested-data.json"], values["audit/requested-state.json"])
        rebuilt = materials_from_result(solved, material=saved.material, raw_annotation=saved.raw_annotation,
            compiled_annotation=saved.compiled_annotation, mapping=saved.mapping, source_metadata=saved.source_metadata)
        actual = _artifacts(rebuilt, values["audit/requested-data.json"], values["audit/requested-state.json"])
        differences = [{"material": name, "saved_sha256": canonical_sha256(values[name]),
                        "replayed_sha256": canonical_sha256(value)}
                       for name, value in actual.items() if canonical_sha256(value) != canonical_sha256(values[name])]
        for name in ("status", "coverage", "diagnostics"):
            if canonical_sha256(getattr(rebuilt, name)) != canonical_sha256(getattr(saved, name)):
                differences.append({"material": name, "saved_sha256": canonical_sha256(getattr(saved, name)),
                                    "replayed_sha256": canonical_sha256(getattr(rebuilt, name))})
        writer = ArtifactWriter(())
        writer.json(checked_run_path(directory / "replay/summary.json"), {"status": "matched" if not differences else "mismatch",
            "model_calls": 0, "manifest_sha256": saved.manifest["manifest_sha256"], "differences": differences})
        if differences:
            raise ValueError("Offline propagation replay differs from saved result")
        write_reports(directory / "replay", saved, writer, annotation_run=origin)
        return saved
