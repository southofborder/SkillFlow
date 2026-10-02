"""One portable DOE fact file, separately sealed audit materials, and offline replay."""
from __future__ import annotations

import json
from pathlib import Path

from skill_ir.data import DataRegistry, export_identity_index, restore_registry
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.inputs.snapshot import read_snapshot
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.recording import (SavedResponseClient, canonical_sha256, implementation_provenance,
                                sha_file, verify_request_identity)
from skill_ir.runtime_contract import execution_model_binding, validate_execution_model_binding
from skill_ir.security_profile.evidence import checked_material
from skill_ir.security_profile.models import SCHEMA_VERSION as PROFILE_VERSION
from skill_ir.security_profile.prompts import build_prompt
from skill_ir.security_profile.loading import load_annotation_run
from skill_ir.security_profile.requests import validate_repair_context
from skill_ir.representation_contract import binding as representation_binding
from skill_ir.security_profile.runner import (
    IDENTITY as ANNOTATION_IDENTITY, FORMAT_VERSION as ANNOTATION_FORMAT_VERSION, verify_prepared,
    compilation_certificate,
)
from skill_ir.security_profile.services import to_payload, validate_response, validate_compiled_response, compile_response

from .handoff import build_doe_input, load_doe_input
from .models import FlowState
from .records import PropagationRecords
from .report import write_reports

IDENTITY = "skill-ir-propagation-v10"
FORMAT_VERSION = 10
AUDIT_NAMES = frozenset({
    "material", "source-metadata", "annotation", "location-evidences", "requested-data", "requested-state",
    "initial-data", "initial-state", "data-identities", "record-materials", "stats", "provenance",
    "raw-annotation", "compilation-map", "compilation", "repair-context",
})


def _read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError(f"non-JSON number: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=invalid)


def _calculate(cfg, annotation, seed, state):
    from .solver import propagate
    return propagate(cfg, annotation, initial_registry=DataRegistry.from_dict(seed) if seed is not None else None,
                     initial_state=FlowState.model_validate(state) if state is not None else None)


def _response(material, annotation, evidences):
    response = validate_compiled_response({"outcome": "completed", **annotation, "location_evidences": evidences}, material)
    if to_payload(response) != annotation:
        raise ValueError("annotation differs from validated business projection")
    return response


def _audit_view(audit):
    return {"annotation": audit["annotation"], "location_evidences": audit["location-evidences"],
            "stats": audit["stats"], "raw_annotation": audit["raw-annotation"],
            "compilation_map": audit["compilation-map"], "compilation": audit["compilation"]}


def _checked_compilation(material, raw_annotation, response, mapping):
    raw, compiled, actual_mapping = compile_response(raw_annotation, material)
    if raw != raw_annotation or compiled != response or actual_mapping != mapping:
        raise ValueError("raw annotation, compiled response or compilation mapping differs")
    return compilation_certificate(raw, compiled, actual_mapping)


def save_propagation_run(run_dir, *, material, source_metadata, annotation, location_evidences, solved,
                         raw_annotation, compilation_map,
                         requested_data=None, requested_state=None, provenance, accepted_files=None,
                         writer=None, before_commit=None, repair_context=None):
    """Common assembly/save path for authored examples and accepted model annotations.

    The manifest is the commit marker and is written last. A failed save leaves
    uncommitted files, never a loadable successful run. No model client is made.
    """
    directory = Path(run_dir).resolve()
    writer = writer or ArtifactWriter(())
    material = checked_material(material)
    repair_context = validate_repair_context(material, repair_context)
    response = _response(material, annotation, location_evidences)
    certificate = _checked_compilation(material, raw_annotation, response, compilation_map)
    if provenance.get("kind") not in {"model_annotation", "hand_authored_specification"}:
        raise ValueError("explicit propagation provenance kind required")
    if (provenance["kind"] == "model_annotation") != (accepted_files is not None):
        raise ValueError("model provenance requires the full accepted call")
    if accepted_files is not None and set(accepted_files) != {"call.json", "transport.json"}:
        raise ValueError("accepted call inventory differs")
    doe = build_doe_input(material["source"], material["cfg"], annotation, solved,
                          source_metadata=source_metadata, execution_model=material["execution_model"])
    snapshot = solved.records.to_dict()
    if (canonical_sha256(solved.initial_data) != snapshot["initial_data_sha256"]
            or canonical_sha256(solved.initial_state) != snapshot["initial_state_sha256"]):
        raise ValueError("solved seed differs from record-bound seed")
    audit = {
        "material": material, "source-metadata": source_metadata, "annotation": annotation,
        "location-evidences": location_evidences, "requested-data": requested_data, "requested-state": requested_state,
        "initial-data": solved.initial_data, "initial-state": solved.initial_state,
        "data-identities": export_identity_index(solved.registry),
        "record-materials": {key: value for key, value in snapshot.items() if key != "records"},
        "stats": solved.stats, "provenance": provenance,
        "raw-annotation": raw_annotation, "compilation-map": compilation_map, "compilation": certificate,
        "repair-context": repair_context,
    }
    if writer.clean({"doe": doe, "audit": audit, "calls": accepted_files}) != {"doe": doe, "audit": audit, "calls": accepted_files}:
        raise ValueError("redaction would change checked propagation material")
    directory.mkdir(parents=True, exist_ok=True)
    with _exclusive_run(directory):
        if any(path.name != ".runner.lock" for path in directory.iterdir()):
            raise ValueError("propagation run requires a new or empty directory")
        for name, value in audit.items():
            writer.json(directory / "audit" / (name + ".json"), value)
        for name, value in (accepted_files or {}).items():
            writer.json(directory / "audit/accepted-call" / name, value)
        if accepted_files is not None:
            accepted = SavedResponseClient(directory / "audit/accepted-call", writer).complete(build_prompt(material, repair_context))
            _check_request_provenance(directory / "audit/accepted-call", provenance, material, repair_context)
            if (validate_response(accepted, material) != response
                    or canonical_sha256(accepted) != provenance.get("accepted_response_sha256")):
                raise ValueError("frozen annotation differs from accepted response")
        writer.json(directory / "doe-input.json", doe)
        write_reports(directory, doe, writer, audit=_audit_view(audit))
        if before_commit is not None:
            before_commit()
        manifest = {
            "schema_version": FORMAT_VERSION, "identity": IDENTITY, "profile_schema_version": PROFILE_VERSION,
            "representation_contract": representation_binding(),
            "execution_model": doe["execution_model"],
            "implementation": implementation_provenance(),
            "audit": {name: canonical_sha256(value) for name, value in audit.items()},
            "accepted_call": {name: canonical_sha256(value) for name, value in (accepted_files or {}).items()},
            "doe_input_sha256": canonical_sha256(doe),
            "policy": {"offline": True, "model_calls": 0, "execute_skill": False},
        }
        # Verify persisted material before making the commit marker visible.
        for name, digest in manifest["audit"].items():
            if canonical_sha256(_read(directory / "audit" / (name + ".json"))) != digest:
                raise ValueError("saved audit material changed before commit")
        for name, digest in manifest["accepted_call"].items():
            if canonical_sha256(_read(directory / "audit/accepted-call" / name)) != digest:
                raise ValueError("saved accepted call changed before commit")
        if canonical_sha256(load_doe_input(directory / "doe-input.json")) != manifest["doe_input_sha256"]:
            raise ValueError("saved business material changed before commit")
        manifest["manifest_sha256"] = canonical_sha256(manifest)
        writer.json(directory / "manifest.json", manifest)
    return doe


def run_propagation(annotation_run, *, run_dir, seed_data=None, initial_state=None):
    """Freeze a validated current compilation and solve it without further calls."""
    origin, directory = Path(annotation_run).resolve(), Path(run_dir).resolve()
    if directory == origin or directory.is_relative_to(origin):
        raise ValueError("propagation outputs cannot overlap the annotation input")
    repository = Path(__file__).resolve().parents[5]
    if any(directory == root or directory.is_relative_to(root)
           for root in (repository / "dataset", repository / "result")):
        raise ValueError("propagation outputs cannot overwrite frozen inputs or delivery artifacts")
    verified = verify_prepared(origin, replay=True)
    if verified["preparation_status"] != "ready":
        raise ValueError("annotation input preparation did not complete")
    # Read-only verification owns accepted-response, projection and compilation
    # checks. Starting a new calculation additionally requires the strict
    # producer identity above and unchanged material through commit below.
    loaded = load_annotation_run(origin)
    if loaded["manifest"] != verified:
        raise ValueError("annotation manifest changed while loading propagation input")
    material, metadata = loaded["material"], loaded["source_metadata"]
    response = loaded["compiled_annotation"]
    annotation, evidences = to_payload(response), response["location_evidences"]
    raw_annotation, compilation_map = loaded["raw_annotation"], loaded["mapping"]
    repair_context = loaded["repair_context"]
    hashes = loaded["upstream_identity"]["files"]
    calls = {name: _read(origin / "calls/annotation/a001" / name) for name in ("call.json", "transport.json")}
    if isinstance(seed_data, (str, Path)):
        seed_data = _read(seed_data)
    seed = seed_data.to_dict() if isinstance(seed_data, DataRegistry) else seed_data
    if seed is not None:
        seed = DataRegistry.from_dict(seed).to_dict()
    if isinstance(initial_state, (str, Path)):
        initial_state = _read(initial_state)
    state = (None if initial_state is None else initial_state.model_dump(mode="json")
             if isinstance(initial_state, FlowState) else FlowState.model_validate(initial_state).model_dump(mode="json"))
    def unchanged():
        if (verify_prepared(origin, replay=True) != verified
                or any(sha_file(origin / name) != digest for name, digest in hashes.items())
                or read_snapshot(origin)[2] != metadata):
            raise ValueError("annotation inputs changed while freezing the propagation run")
    solved = _calculate(material["cfg"], annotation, seed, state)
    return save_propagation_run(directory, material=material, source_metadata=metadata, annotation=annotation,
                               raw_annotation=raw_annotation, compilation_map=compilation_map,
                               location_evidences=evidences, solved=solved, requested_data=seed, requested_state=state,
                               provenance={"kind": "model_annotation", "annotation_path": str(origin),
                                           "annotation_manifest": verified, "original_sha256": hashes,
                                           "request_validation": loaded["request_validation"],
                                           "accepted_response_sha256": loaded["upstream_identity"]["accepted_response_sha256"]},
                               accepted_files=calls, before_commit=unchanged, repair_context=repair_context)


def _check_request_provenance(call_directory, provenance, material, repair_context):
    original = provenance.get("annotation_manifest", {})
    validate_repair_context(material, repair_context)
    if (original.get("repair_context_sha256") != canonical_sha256(repair_context)
            or original.get("request_kind") != ("base" if repair_context is None else "repair")
            or original.get("representation_contract") != representation_binding()):
        raise ValueError("accepted annotation repair request or representation identity differs")
    config = original.get("config", {})
    if config.get("response_format") != "json_object":
        raise ValueError("accepted annotation did not bind JSON Output configuration")
    checked = verify_request_identity(call_directory, config, prompt=build_prompt(material, repair_context))
    if checked != provenance.get("request_validation"):
        raise ValueError("accepted annotation request identity differs")
    return checked


def _load_run(directory):
    manifest = _read(directory / "manifest.json")
    if (manifest.get("schema_version") != FORMAT_VERSION or manifest.get("identity") != IDENTITY
            or manifest.get("profile_schema_version") != PROFILE_VERSION):
        raise ValueError("unsupported propagation run version")
    if canonical_sha256({k: v for k, v in manifest.items() if k != "manifest_sha256"}) != manifest.get("manifest_sha256"):
        raise ValueError("propagation manifest digest mismatch")
    if set(manifest.get("audit", {})) != AUDIT_NAMES:
        raise ValueError("propagation audit inventory differs")
    audit = {name: _read(directory / "audit" / (name + ".json")) for name in AUDIT_NAMES}
    for name, value in audit.items():
        if canonical_sha256(value) != manifest["audit"][name]:
            raise ValueError(f"propagation audit digest mismatch: {name}")
    doe = load_doe_input(directory / "doe-input.json")
    if canonical_sha256(doe) != manifest.get("doe_input_sha256"):
        raise ValueError("propagation DOE input digest mismatch")
    material = checked_material(audit["material"])
    validate_execution_model_binding(manifest.get("execution_model"))
    if not (manifest["execution_model"] == doe["execution_model"]
            == execution_model_binding(material["execution_model"])):
        raise ValueError("propagation execution model binding differs from frozen material")
    if manifest.get("representation_contract") != representation_binding():
        raise ValueError("propagation representation contract identity differs")
    repair_context = validate_repair_context(material, audit["repair-context"])
    annotation = audit["annotation"]
    response = _response(material, annotation, audit["location-evidences"])
    if _checked_compilation(material, audit["raw-annotation"], response, audit["compilation-map"]) != audit["compilation"]:
        raise ValueError("propagation compilation certificate mismatch")
    provenance = audit["provenance"]
    kind = provenance.get("kind")
    required = {"call.json", "transport.json"} if kind == "model_annotation" else set()
    if kind not in {"model_annotation", "hand_authored_specification"} or set(manifest.get("accepted_call", {})) != required:
        raise ValueError("accepted annotation call inventory differs")
    if required:
        for name, digest in manifest["accepted_call"].items():
            if canonical_sha256(_read(directory / "audit/accepted-call" / name)) != digest:
                raise ValueError("accepted annotation call digest mismatch")
        accepted = SavedResponseClient(directory / "audit/accepted-call", ArtifactWriter(())).complete(build_prompt(material, repair_context))
        _check_request_provenance(directory / "audit/accepted-call", provenance, material, repair_context)
        if (canonical_sha256(accepted) != provenance.get("accepted_response_sha256")
                or validate_response(accepted, material) != response):
            raise ValueError("frozen annotation differs from accepted response")
        original = provenance["annotation_manifest"]
        if (original.get("identity") != ANNOTATION_IDENTITY or original.get("schema_version") != ANNOTATION_FORMAT_VERSION
                or original.get("execution_model") != manifest["execution_model"]
                or canonical_sha256({k: v for k, v in original.items() if k != "manifest_sha256"}) != original.get("manifest_sha256")
                or original.get("graph_sha256") != canonical_sha256(material["cfg"])
                or original.get("source_sha256") != material["source"]["source_sha256"]
                or original.get("material_sha256") != canonical_sha256(material)
                or original.get("prompt_sha256") != canonical_sha256(build_prompt(material, repair_context))):
            raise ValueError("frozen annotation provenance identity mismatch")
    registry = restore_registry(doe["data"], audit["data-identities"])
    normalized_cfg = json.loads(ControlFlowGraph.model_validate_json(json.dumps(material["cfg"])).to_json())
    records = PropagationRecords.from_dict({**audit["record-materials"], "records": doe["records"]},
                cfg=normalized_cfg, annotation=annotation, data_registry=registry,
                initial_data=audit["initial-data"], initial_state=audit["initial-state"])
    from .solver import PropagationResult
    saved = PropagationResult(doe["status"], registry, records, doe["coverage"], doe["diagnostics"], audit["stats"],
                              audit["initial-data"], audit["initial-state"])
    projected = build_doe_input(material["source"], material["cfg"], annotation, saved,
                                source_metadata=audit["source-metadata"], execution_model=material["execution_model"])
    if projected != doe:
        raise ValueError("DOE input differs from frozen business projection")
    if audit["requested-data"] is not None:
        DataRegistry.from_dict(audit["requested-data"])
    if audit["requested-state"] is not None:
        FlowState.model_validate(audit["requested-state"])
    return doe, manifest, audit


def load_propagation_run(run_dir):
    """Read and check a committed run, without requiring the current source hash."""
    return _load_run(Path(run_dir).resolve())[0]


def replay_propagation(run_dir):
    """Recompute from requested seed parameters; preserve only a comparison receipt."""
    directory = Path(run_dir).resolve()
    with _exclusive_run(directory):
        doe, manifest, audit = _load_run(directory)
        if manifest["implementation"] != implementation_provenance():
            raise ValueError("propagation implementation identity changed")
        solved = _calculate(audit["material"]["cfg"], audit["annotation"], audit["requested-data"], audit["requested-state"])
        rebuilt = build_doe_input(audit["material"]["source"], audit["material"]["cfg"], audit["annotation"], solved,
                                  source_metadata=audit["source-metadata"],
                                  execution_model=audit["material"]["execution_model"])
        differences = []
        for name, actual, expected in (
            ("doe-input", rebuilt, doe), ("initial-data", solved.initial_data, audit["initial-data"]),
            ("initial-state", solved.initial_state, audit["initial-state"]),
            ("data-identities", export_identity_index(solved.registry), audit["data-identities"]),
            ("record-materials", {k: v for k, v in solved.records.to_dict().items() if k != "records"}, audit["record-materials"]),
        ):
            if actual != expected:
                differences.append({"material": name, "saved_sha256": canonical_sha256(expected),
                                    "replayed_sha256": canonical_sha256(actual)})
        writer = ArtifactWriter(())
        writer.json(directory / "replay/summary.json", {"status": "matched" if not differences else "mismatch",
                    "model_calls": 0, "doe_input_sha256": canonical_sha256(rebuilt), "differences": differences})
        if differences:
            raise ValueError("offline propagation replay differs from saved result")
        write_reports(directory / "replay", doe, writer, audit=_audit_view(audit))
        return doe
