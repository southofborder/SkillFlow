"""One whole-graph annotation, durable recording, and offline replay.

This runner neither repairs graphs nor propagates data. A complete record is
not a proof that its model-generated semantic labels are correct.
"""
from __future__ import annotations
from skillflow.propagation.contracts.references import cfg_instructions

from copy import deepcopy
from contextlib import nullcontext
import hashlib
import os
from pathlib import Path
from threading import Event
from uuid import uuid4

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.common.artifacts import call_metrics
from skillflow.common.runs import exclusive_run
from skillflow.common.inputs.snapshot import freeze_input
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.inputs.snapshot import verify_original_input
from skillflow.common.recording import RecordingClient
from skillflow.common.recording import SavedResponseClient
from skillflow.common.recording import SavedCallFailure
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import injected_factory
from skillflow.common.recording import now
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import validated_trace
from skillflow.common.recording import verify_request_identity
from skillflow.common.recording import ResponseIntegrityError
from skillflow.common.source_evidence import _json_object
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.json_normalization import NORMALIZATION_VERSION
from skillflow.common.structural_correction import (
    ResponseChain, ResponseChainError, VERSION as STRUCTURAL_VERSION, chain_counts,
)
from skillflow.propagation.contracts.runtime_contract import runtime_contract
from skillflow.propagation.contracts.runtime_contract import runtime_contract_binding
from skillflow.propagation.contracts.runtime_contract import validate_runtime_contract
from skillflow.propagation.contracts.runtime_contract import validate_runtime_contract_binding
from skillflow.propagation.contracts.specs import iter_spec_evidence
from skillflow.propagation.contracts.specs import iter_effect_events
from skillflow.propagation.material import prepare_material
from skillflow.propagation.contracts.profiles import AnnotationResponse
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION
from skillflow.propagation.annotation.prompts import build_prompt
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.annotation.config import annotation_config
from skillflow.propagation.annotation.config import PUBLIC_CONFIG_FIELDS
from skillflow.propagation.annotation.requests import (validate_repair_context, load_repair_context,
    repair_context_from_upstream)
from skillflow.propagation.annotation.inputs import (write_material_parts, load_prepared_material,
    read_component, resolve_material_owner)

IDENTITY = "skill-ir-security-profile-v18"
FORMAT_VERSION = 18
CALL_PREFIX = "calls/annotation"
CALL_PATH = CALL_PREFIX + "/a001"
POLICY = {"structural_correction": STRUCTURAL_VERSION, "structural_attempt_limit": None,
          "json_normalization": NORMALIZATION_VERSION,
          "semantic_repairs": 0, "raw_cfg_input": True, "controlled_text_input": False,
          "propagation": False, "joint_ir_semantics": True, "risk_judgment": False,
          "automatic_resend_after_acceptance": False}


class RunIdentityError(ValueError):
    """Frozen input, configuration, or implementation does not match this run."""


def _seal(value):
    result = deepcopy(value)
    result["manifest_sha256"] = canonical_sha256(value)
    return result


def _unseal(value):
    unsigned = deepcopy(value)
    digest = unsigned.pop("manifest_sha256", None)
    if canonical_sha256(unsigned) != digest:
        raise RunIdentityError("Security-profile manifest digest mismatch")
    return unsigned


def _config(value):
    value = {} if value is None else value
    if not isinstance(value, dict) or set(value) - set(PUBLIC_CONFIG_FIELDS):
        raise ValueError("Only public LLM configuration fields may be recorded")
    return annotation_config(value)


def _files(directory):
    return {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
            for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}


def _text(path, value, writer):
    """Write exact UTF-8 model text, without platform newline translation."""
    if writer.clean(value) != value:
        raise ValueError("A credential overlaps exact model text")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_bytes(value.encode("utf-8"))
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_run(input, analysis, *, run_dir, config=None, secrets=(), repair_context=None,
                user_request=None, upstream_run=None, task_run=None):
    """Freeze an input once and prepare a single annotation, without networking."""
    directory = checked_run_path(run_dir)
    source_path = Path(input).resolve() if input is not None else None
    # Reject before acquiring a lock or creating anything inside the source.
    if source_path is not None and source_path.is_dir() and directory.is_relative_to(source_path):
        raise ValueError("run directory must not be nested inside the Skill input")
    analysis_path = Path(analysis).resolve() if analysis is not None else None
    if analysis_path is not None and (analysis_path == directory or directory in analysis_path.parents):
        raise ValueError("analysis input must be outside the new run directory")
    public = _config(config)
    writer = ArtifactWriter(tuple(secrets))
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise RunIdentityError("Prepare requires a new or empty run directory")
        manifest = {
            "schema_version": FORMAT_VERSION, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION,
            "run_id": directory.name,
            "created_at": now(), "config": public, "implementation": implementation_provenance(),
            "original_analysis": {"path": str(analysis_path), "sha256": None} if upstream_run is None else None,
            "upstream": None, "task_run_ref": None, "task_owner_ref": None,
            "source_sha256": None, "graph_sha256": None, "preparation_status": "input_error",
            "runtime_contract": runtime_contract_binding(runtime_contract()),
            "request_kind": "base" if repair_context is None else "repair",
            "repair_context_sha256": None,
            "preparation_error": None, "material_sha256": None, "prompt_sha256": None,
            "boundaries": {}, "files": {},
            "policy": deepcopy(POLICY),
        }
        try:
            from skillflow.task.runner import load_task_run
            if task_run is None and upstream_run is not None:
                from skillflow.propagation.annotation.inputs import resolve_task_owner
                task_run = resolve_task_owner(upstream_run)
            if task_run is None and upstream_run is not None and read_component(checked_run_path(upstream_run)/"manifest.json").get("task_origin") == "authored_fixture":
                baseline = load_prepared_material(upstream_run)["task"]
                manifest["task_origin"] = "authored_fixture_reference"
                manifest["task_owner_ref"] = make_run_reference(directory,checked_run_path(upstream_run))
            elif task_run is None:
                raise ValueError("A sealed independent Task run is required before annotation preparation")
            else:
                baseline = load_task_run(task_run)["task"]
                manifest["task_run_ref"] = make_run_reference(directory, checked_run_path(task_run))
            if upstream_run is None:
                if repair_context is not None:
                    raise ValueError("Persistent repair requires an explicit refinement owner")
                if source_path is None or analysis_path is None:
                    raise ValueError("Base preparation requires Skill and analysis paths")
                raw = analysis_path.read_bytes()
                manifest["original_analysis"]["sha256"] = hashlib.sha256(raw).hexdigest()
                candidate = _json_object(raw.decode("utf-8-sig"))
                if not isinstance(candidate.get("cfg"), dict):
                    raise ValueError("analysis.json must contain the actual cfg object")
                cfg = candidate["cfg"]
                if writer.clean(cfg) != cfg:
                    raise ValueError("A credential overlaps the actual graph")
                metadata = freeze_input(source_path, directory, writer)
                _, source, _ = read_snapshot(directory)
                material = prepare_material(source, cfg, task_baseline=baseline, user_request=user_request)
            else:
                if input is not None or analysis is not None or user_request is not None:
                    raise ValueError("Referenced preparation must not also supply copied input components")
                upstream = checked_run_path(upstream_run)
                if directory == upstream or upstream.is_relative_to(directory):
                    raise ValueError("Repair preparation cannot contain its material owner")
                material = load_prepared_material(upstream, task_baseline=baseline)
                manifest["upstream"] = make_run_reference(directory, upstream)
                source, cfg = material["source"], material["cfg"]
                _, _, metadata = read_snapshot(resolve_material_owner(upstream))
            checked_repair = validate_repair_context(material, repair_context)
            if upstream_run is not None and repair_context is not None:
                actual_repair = repair_context_from_upstream(upstream, material)
                if canonical_sha256(checked_repair) != canonical_sha256(actual_repair):
                    raise ValueError("Repair context differs from the accepted initial review")
                checked_repair = actual_repair
            prompt = build_prompt(material, checked_repair)
            if writer.clean(material) != material:
                raise ValueError("A credential overlaps annotation input")
            if upstream_run is None:
                write_material_parts(directory, material, writer)
            _text(directory / "inputs/prompt.txt", prompt, writer)
            manifest.update(
                preparation_status="ready", source_sha256=source["source_sha256"],
                graph_sha256=canonical_sha256(cfg), material_sha256=canonical_sha256(material),
                prompt_sha256=canonical_sha256(prompt), boundaries=metadata["boundaries"],
                repair_context_sha256=canonical_sha256(checked_repair),
            )
        except Exception as error:
            manifest["preparation_error"] = writer.clean(f"{type(error).__name__}: {error}")
        manifest["files"] = _files(directory)
        manifest = _seal(manifest)
        writer.json(directory / "manifest.json", manifest)
        if manifest["preparation_status"] == "input_error":
            result = _base_result(manifest)
            result.update(status="input_error", reason=manifest["preparation_error"])
            result["counts"] = _counts(directory)
            _save_result(directory, result, None, writer)
        return manifest


def _verify(directory, config, replay, *, check_implementation=True):
    manifest = read_json(directory / "manifest.json")
    if (manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION
            or manifest.get("profile_schema_version") != SCHEMA_VERSION):
        raise RunIdentityError("Unsupported security-profile run version")
    _unseal(manifest)
    if manifest.get("policy") != POLICY:
        raise RunIdentityError("Annotation structural-correction policy changed")
    try:
        validate_runtime_contract_binding(manifest.get("runtime_contract"))
        if manifest["preparation_status"] == "ready":
            frozen_model = load_prepared_material(directory)["runtime_contract"]
            validate_runtime_contract(frozen_model)
            if runtime_contract_binding(frozen_model) != manifest["runtime_contract"]:
                raise ValueError("frozen execution model binding differs")
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
        raise RunIdentityError("Abstract runtime contract identity mismatch; use a new run") from error
    if manifest["config"] != _config(config):
        raise RunIdentityError("Annotation configuration changed; use a new run")
    if check_implementation and manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Implementation identity changed; refusing continuation or reinterpretation")
    if manifest["files"] != _files(directory):
        raise RunIdentityError("Frozen annotation input inventory or bytes changed")
    if manifest["preparation_status"] != "ready":
        return manifest, None, None
    material = load_prepared_material(directory)
    source, cfg = material["source"], material["cfg"]
    _, _, metadata = read_snapshot(resolve_material_owner(directory))
    if (source["source_sha256"] != manifest["source_sha256"]
            or canonical_sha256(cfg) != manifest["graph_sha256"]):
        raise RunIdentityError("Annotation graph or source identity changed")
    repair_context = load_repair_context(directory, material=material, manifest=manifest)
    if (manifest.get("repair_context_sha256") != canonical_sha256(repair_context)
            or manifest.get("request_kind") != ("base" if repair_context is None else "repair")):
        raise RunIdentityError("Annotation repair request identity differs")
    prompt = build_prompt(material, repair_context)
    if (canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(prompt) != manifest["prompt_sha256"]
            or prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")):
        raise RunIdentityError("Prepared annotation material, rules or prompt changed")
    if not replay and manifest.get("upstream") is None:
        verify_original_input(None, metadata)
        original = manifest["original_analysis"]
        if sha_file(Path(original["path"])) != original["sha256"]:
            raise RunIdentityError("Original analysis changed; refuse to continue")
    return manifest, material, prompt


def _base_result(manifest):
    return {
        "schema_version": FORMAT_VERSION, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "status": "interrupted", "reason": "Annotation has not started.",
        "error_kind": None, "request_validation": None,
        "source_sha256": manifest["source_sha256"], "graph_sha256": manifest["graph_sha256"],
        "runtime_contract": deepcopy(manifest["runtime_contract"]),
        "ir_semantics": {}, "locations": {}, "sink_boundaries": [], "boundaries": manifest["boundaries"],
        "task_ref": None, "realizations": [], "demands": [], "expressions": [],
        "failure": None,
        "response_chain": None, "accepted_call": None,
        "location_evidences_sha256": None,
        "compilation": None,
        "validation": {"status": "not_run", "instruction_count": 0,
                       "ir_semantics_count": 0, "location_count": 0,
                       "atomic_op_count": 0, "evidence_count": 0, "location_evidence_count": 0,
                       "sink_boundary_count": 0, "errors": []},
        "counts": {},
        "notice": "Complete means a complete annotation record, not a safety conclusion or proof of model semantics.",
    }


BUSINESS_FIELDS = frozenset({"task_ref", "realizations", "demands", "expressions", "ir_semantics", "locations", "sink_boundaries"})


def result_snapshot(result):
    """Persist only the run protocol; compiled-response owns the business facts."""
    return {key: deepcopy(value) for key, value in result.items() if key not in BUSINESS_FIELDS}


def _check_result_snapshot(saved, manifest):
    if (type(saved) is not dict or set(saved) != set(result_snapshot(_base_result(manifest)))
            or type(saved.get("schema_version")) is not int):
        raise RunIdentityError("Saved annotation result protocol has unexpected or missing fields")
    return saved


def verify_prepared(run_dir, *, config=None, replay=False):
    """Check an existing preparation without creating clients or rewriting it."""
    directory = checked_run_path(run_dir)
    if not (directory / "manifest.json").is_file():
        raise RunIdentityError("No prepared annotation manifest exists")
    if config is None:
        config = read_json(directory / "manifest.json")["config"]
    with exclusive_run(directory):
        return _verify(directory, config, replay)[0]


def _counts(directory):
    return chain_counts(directory, CALL_PREFIX)


def _verify_saved_projection(directory, payload, location_evidences, runtime_contract_identity, compilation=None,
                             request_validation=None):
    """A saved successful run must still agree with the complete accepted response."""
    path = directory / "result.json"
    if not path.exists():
        return
    try:
        saved = read_component(path)
    except (OSError, ValueError, TypeError) as error:
        raise RunIdentityError("Saved annotation payload or location evidence is unreadable") from error
    if not isinstance(saved, dict):
        raise RunIdentityError("Saved annotation payload or location evidence has an invalid shape")
    if saved.get("status") not in {"complete"}:
        return
    if canonical_sha256(saved.get("runtime_contract")) != canonical_sha256(runtime_contract_identity):
        raise RunIdentityError("Saved annotation runtime contract identity mismatch")
    if request_validation is None or canonical_sha256(saved.get("request_validation")) != canonical_sha256(request_validation):
        raise RunIdentityError("Saved annotation request identity differs")
    sidecar = directory / "audit/location-evidences.json"
    try:
        table = read_component(sidecar) if sidecar.is_file() else None
    except (OSError, ValueError, TypeError) as error:
        raise RunIdentityError("Saved annotation payload or location evidence is unreadable") from error
    if (saved.get("identity") != IDENTITY or saved.get("schema_version") != FORMAT_VERSION
            or saved.get("profile_schema_version") != SCHEMA_VERSION
            or BUSINESS_FIELDS.intersection(saved)
            or not sidecar.is_file()
            or canonical_sha256(table) != canonical_sha256(location_evidences)
            or saved.get("location_evidences_sha256") != canonical_sha256(location_evidences)):
        raise RunIdentityError("Saved annotation payload or location evidence differs from the accepted response")
    if compilation is None or canonical_sha256(saved.get("compilation")) != canonical_sha256(compilation_certificate(*compilation)):
        raise RunIdentityError("Saved annotation compilation identity differs")
    for name, value in zip(("raw-annotation", "compiled-response", "compilation-map"), compilation):
        if canonical_sha256(read_component(directory / "audit" / (name + ".json"))) != canonical_sha256(value):
            raise RunIdentityError("Saved annotation compilation material differs: " + name)


def compilation_certificate(raw, compiled, mapping):
    """Identity of the actual raw-to-compiled conversion, never a semantic proof."""
    return {"version": mapping["compiler_version"],
            "raw_sha256": canonical_sha256(raw), "compiled_sha256": canonical_sha256(compiled),
            "mapping_sha256": canonical_sha256(mapping),
            "sink_boundaries_sha256": canonical_sha256(compiled["sink_boundaries"])}


def _save_result(output, result, material, writer, location_evidences=None, compilation=None, *, replay=False):
    from skillflow.propagation.annotation.report import render_report
    if result["status"] in {"complete"}:
        if (location_evidences is None
                or canonical_sha256(location_evidences) != result["location_evidences_sha256"]):
            raise RunIdentityError("A successful annotation requires its checked location evidence table")
        if compilation is None or result.get("compilation") != compilation_certificate(*compilation):
            raise RunIdentityError("A successful annotation requires its checked compilation material")
    if location_evidences is not None:
        # Sidecar is durable before the final successful result is committed.
        writer.json(output / "audit/location-evidences.json", location_evidences)
    if compilation is not None:
        for name, value in zip(("raw-annotation", "compiled-response", "compilation-map"), compilation):
            writer.json(output / "audit" / (name + ".json"), value)
    writer.json(output / "validation.json", result["validation"])
    writer.text(output / "report.md", render_report(result, material, call_root="../" if replay else ""))
    writer.json(output / "result.json", result_snapshot(result))


def run_annotation(run_dir, *, client=None, client_factory=None, config=None, secrets=(),
                   replay=False, stop_event=None, progress=None, factory_provider=None):
    """Run or replay with strict producer implementation identity."""
    return _run_annotation(run_dir, client=client, client_factory=client_factory, config=config, secrets=secrets,
        replay=replay, stop_event=stop_event, progress=progress, factory_provider=factory_provider)


def _run_annotation(run_dir, *, client=None, client_factory=None, config=None, secrets=(),
                   replay=False, stop_event=None, progress=None, read_only=False, factory_provider=None):
    """Reach a valid candidate through unbounded mechanical corrections only."""
    if read_only and not replay:
        raise ValueError("Read-only verification requires saved-response replay")
    directory = checked_run_path(run_dir)
    if not (directory / "manifest.json").exists():
        raise RunIdentityError("No prepared annotation manifest exists")
    if replay and any(value is not None for value in (client, client_factory, factory_provider)):
        raise ValueError("Offline replay does not accept an online client")
    if sum(value is not None for value in (client, client_factory, factory_provider)) > 1:
        raise ValueError("Inject either client or client_factory, not both")
    if config is None:
        config = read_json(directory / "manifest.json")["config"]
    writer, stopping = ArtifactWriter(tuple(secrets)), stop_event or Event()
    with (nullcontext() if read_only else exclusive_run(directory)):
        manifest, material, prompt = _verify(directory, config, replay, check_implementation=not read_only)
        result, output = _base_result(manifest), directory / "replay" if replay else directory
        if manifest["preparation_status"] != "ready":
            result.update(status="input_error", reason=manifest["preparation_error"])
            result["counts"] = _counts(directory)
            if not read_only:
                _save_result(output, result, material, writer, replay=replay)
            return result
        result["validation"]["instruction_count"] = len(cfg_instructions(material["cfg"]))
        saved_path = directory / "result.json"
        try:
            existing = _check_result_snapshot(read_component(saved_path), manifest) if saved_path.is_file() else None
        except (ValueError, OSError) as error:
            raise RunIdentityError("Saved annotation payload or location evidence is unreadable") from error
        boundary_path = directory / "execution-boundary.json"
        boundary = _unseal(read_json(boundary_path)) if replay and boundary_path.is_file() else {"kind": "none"}
        if not replay:
            writer.json(boundary_path, _seal({"kind": "running"}))
        chain, location_evidences, compilation = None, None, None
        try:
            if replay and boundary["kind"] == "local_error":
                if boundary["result_fields"].get("response_chain") is not None:
                    paused = ResponseChain(directory, prefix=CALL_PREFIX, base_prompt=prompt,
                        request_kind=manifest["request_kind"], config=manifest["config"], writer=writer,
                        validate=lambda response: compile_response(response, material), replay=True, read_only=True,
                        interruption=boundary["cursor"])
                    try:
                        paused.run()
                    except KeyboardInterrupt:
                        pass
                    else:
                        raise RunIdentityError("Local failure boundary unexpectedly completed its response chain")
                    if paused.snapshot() != boundary["result_fields"]["response_chain"]:
                        raise RunIdentityError("Local failure response-chain preparation changed")
                result.update(deepcopy(boundary["result_fields"]))
                if existing is None or result_snapshot(result) != existing:
                    raise RunIdentityError("Saved local annotation failure changed")
                if not read_only:
                    _save_result(output, result, material, writer, replay=replay)
                return result
            if writer.clean(material) != material or writer.clean(prompt) != prompt:
                raise ValueError("A credential overlaps the verified annotation input")
            factory = client_factory or (injected_factory(client) if client is not None else None)
            chain = ResponseChain(directory, prefix=CALL_PREFIX, base_prompt=prompt,
                request_kind=manifest["request_kind"], config=manifest["config"], writer=writer,
                validate=lambda response: compile_response(response, material),
                client_factory=factory, stop_event=stopping, replay=replay, read_only=read_only,
                progress=progress, recording_client=RecordingClient, saved_client=SavedResponseClient,
                factory_provider=factory_provider,
                interruption=boundary.get("cursor") if boundary["kind"] == "interrupted" else None)
            compilation = chain.run()
            result["request_validation"] = chain.request_validation
            annotation = compilation[1]
            payload = to_payload(annotation)
            location_evidences = annotation["location_evidences"]
            _verify_saved_projection(directory, payload, location_evidences, manifest["runtime_contract"], compilation,
                                     result["request_validation"])
            result.update(payload)
            result["compilation"] = compilation_certificate(*compilation)
            result["location_evidences_sha256"] = canonical_sha256(location_evidences)
            location_evidence_count = sum(len(items) for items in location_evidences.values())
            typed = AnnotationResponse.model_validate(annotation)
            result["validation"].update(
                status="passed", ir_semantics_count=len(annotation["ir_semantics"]),
                location_count=len(annotation["locations"]),
                sink_boundary_count=len(annotation["sink_boundaries"]),
                atomic_op_count=sum(len(event.atomic_ops) for spec in typed.ir_semantics.values()
                                    for event in iter_effect_events(spec)),
                location_evidence_count=location_evidence_count,
                evidence_count=sum(1 for _ in iter_spec_evidence(typed)) + location_evidence_count)
            result.update(status="complete", reason="Joint annotation and symbolic transfer specifications are complete; structure, operation coverage and evidence references passed validation.")
        except (RunIdentityError, ResponseChainError) as error:
            raise RunIdentityError(str(error)) from error
        except SemanticFailure as error:
            result.update(status="semantic_failure", reason=writer.clean(error.reason),
                          error_kind="cannot_assess", failure=writer.clean(error.failure))
            result["validation"].update(status="task_failed", errors=[result["reason"]])
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(
                boundary.get("reason", str(error)) if replay and boundary["kind"] == "interrupted" else str(error)),
                          error_kind="interrupted")
        except Exception as error:
            if isinstance(error, ResponseIntegrityError) and (existing is not None or replay):
                raise RunIdentityError("Saved annotation request identity differs: " + str(error)) from error
            typ = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
            interrupted = typ == "KeyboardInterrupt"
            point = None if chain is None else chain.cursor["point"]
            kind = ("interrupted" if interrupted else "output_truncated" if typ == "OutputTruncatedError"
                    else "incomplete_transport" if str(error).startswith("Incomplete SSE response:")
                    else "request_identity" if typ == "ResponseIntegrityError"
                    else "input" if chain is None else "internal_validation" if point == "validate" else "execution")
            result.update(status="interrupted" if interrupted else "input_error" if chain is None else "execution_error",
                          reason=writer.clean(str(error)), error_kind=kind)
            if not interrupted:
                result["validation"].update(status="not_run", errors=[result["reason"]])
        if chain is not None:
            result.update(response_chain=chain.snapshot(), accepted_call=chain.accepted_call,
                          request_validation=chain.request_validation)
        result["counts"] = writer.clean(_counts(directory))
        if existing and (replay or existing.get("status") == "complete") and canonical_sha256(existing) != canonical_sha256(result_snapshot(result)):
            raise RunIdentityError("Saved annotation decision differs from replayed response chain")
        if not replay:
            marker = {"kind": "interrupted" if result["status"] == "interrupted" else "finished",
                      "cursor": None if chain is None else chain.cursor, "reason": result["reason"]}
            no_current_call = chain is None or not (directory / chain.cursor["call"] / "call.json").exists()
            if result["status"] in {"input_error", "execution_error"} and no_current_call:
                marker = {"kind": "local_error", "result_fields": result_snapshot(result),
                          "cursor": None if chain is None else {"point": "before_transport", "call": chain.cursor["call"]}}
            writer.json(boundary_path, _seal(marker))
        if not read_only:
            _save_result(output, result, material, writer, location_evidences, compilation, replay=replay)
        if progress:
            progress(f"{result['status']}：{result['reason']}")
        return result


def replay_run(run_dir):
    """Rebuild parsing, evidence checks and reports with zero online clients."""
    return run_annotation(run_dir, replay=True)
