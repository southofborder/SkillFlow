"""One whole-graph annotation, durable recording, and offline replay.

This runner neither repairs graphs nor propagates data. A complete record is
not a proof that its model-generated semantic labels are correct.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import os
from pathlib import Path
from threading import Event
from uuid import uuid4

from skill_ir.experiments.report import ArtifactWriter, call_metrics
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.inputs.snapshot import freeze_input, read_snapshot, verify_original_input
from skill_ir.recording import (
    RecordingClient, SavedResponseClient, SavedCallFailure, canonical_sha256,
    implementation_provenance, injected_factory, now, read_json, sha_file, validated_trace,
    verify_request_identity, ResponseIntegrityError,
)
from skill_ir.source_evidence import _json_object
from skill_ir.semantic_failure import SemanticFailure
from skill_ir.representation_contract import binding as representation_binding
from skill_ir.runtime_contract import (
    execution_model, execution_model_binding, validate_execution_model,
    validate_execution_model_binding,
)
from skill_ir.propagation.specs import iter_spec_evidence, iter_effect_events
from .evidence import prepare_material
from .models import AnnotationResponse, SCHEMA_VERSION
from .prompts import build_prompt
from .services import to_payload, compile_response
from .config import annotation_config, PUBLIC_CONFIG_FIELDS
from .requests import validate_repair_context

IDENTITY = "skill-ir-security-profile-v11"
FORMAT_VERSION = 11
CALL_PATH = "calls/annotation/a001"


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
    return {p.relative_to(directory).as_posix(): sha_file(p)
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


def prepare_run(input, analysis, *, run_dir, config=None, secrets=(), repair_context=None):
    """Freeze an input once and prepare a single annotation, without networking."""
    directory = Path(run_dir).resolve()
    source_path = Path(input).resolve()
    # Reject before acquiring a lock or creating anything inside the source.
    if source_path.is_dir() and directory.is_relative_to(source_path):
        raise ValueError("run directory must not be nested inside the Skill input")
    analysis_path = Path(analysis).resolve()
    if analysis_path == directory or directory in analysis_path.parents:
        raise ValueError("analysis input must be outside the new run directory")
    public = _config(config)
    writer = ArtifactWriter(tuple(secrets))
    directory.mkdir(parents=True, exist_ok=True)
    with _exclusive_run(directory):
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise RunIdentityError("Prepare requires a new or empty run directory")
        manifest = {
            "schema_version": FORMAT_VERSION, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION,
            "run_id": directory.name,
            "created_at": now(), "config": public, "implementation": implementation_provenance(),
            "original_analysis": {"path": str(analysis_path), "sha256": None},
            "source_sha256": None, "graph_sha256": None, "preparation_status": "input_error",
            "execution_model": execution_model_binding(execution_model()),
            "representation_contract": representation_binding(),
            "request_kind": "base" if repair_context is None else "repair",
            "repair_context_sha256": None,
            "preparation_error": None, "material_sha256": None, "prompt_sha256": None,
            "boundaries": {}, "files": {},
            "policy": {"planned_logical_calls": 1, "automatic_repairs": 0,
                       "raw_cfg_input": True, "controlled_text_input": False,
                       "propagation": False, "symbolic_transfer_specs": True, "risk_judgment": False,
                       "automatic_resend_after_acceptance": False},
        }
        try:
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
            material = prepare_material(source, cfg)
            checked_repair = validate_repair_context(material, repair_context)
            prompt = build_prompt(material, checked_repair)
            if writer.clean(material) != material:
                raise ValueError("A credential overlaps annotation input")
            writer.json(directory / "inputs/cfg.json", cfg)
            writer.json(directory / "inputs/material.json", material)
            writer.json(directory / "inputs/repair-context.json", checked_repair)
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


def _verify(directory, config, replay):
    manifest = read_json(directory / "manifest.json")
    if (manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION
            or manifest.get("profile_schema_version") != SCHEMA_VERSION):
        raise RunIdentityError("Unsupported security-profile run version")
    _unseal(manifest)
    if manifest.get("representation_contract") != representation_binding():
        raise RunIdentityError("Annotation representation contract identity differs")
    try:
        validate_execution_model_binding(manifest.get("execution_model"))
        if manifest["preparation_status"] == "ready":
            frozen_model = read_json(directory / "inputs/material.json").get("execution_model")
            validate_execution_model(frozen_model)
            if execution_model_binding(frozen_model) != manifest["execution_model"]:
                raise ValueError("frozen execution model binding differs")
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
        raise RunIdentityError("Abstract runtime contract identity mismatch; use a new run") from error
    if manifest["config"] != _config(config):
        raise RunIdentityError("Annotation configuration changed; use a new run")
    if manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Implementation identity changed; refusing continuation or reinterpretation")
    if manifest["files"] != _files(directory):
        raise RunIdentityError("Frozen annotation input inventory or bytes changed")
    if manifest["preparation_status"] != "ready":
        return manifest, None, None
    _, source, metadata = read_snapshot(directory)
    cfg = _json_object((directory / "inputs/cfg.json").read_text(encoding="utf-8"))
    if (source["source_sha256"] != manifest["source_sha256"]
            or canonical_sha256(cfg) != manifest["graph_sha256"]):
        raise RunIdentityError("Annotation graph or source identity changed")
    material = prepare_material(source, cfg)
    repair_context = read_json(directory / "inputs/repair-context.json")
    validate_repair_context(material, repair_context)
    if (manifest.get("repair_context_sha256") != canonical_sha256(repair_context)
            or manifest.get("request_kind") != ("base" if repair_context is None else "repair")):
        raise RunIdentityError("Annotation repair request identity differs")
    prompt = build_prompt(material, repair_context)
    if (canonical_sha256(material) != manifest["material_sha256"]
            or material != read_json(directory / "inputs/material.json")
            or canonical_sha256(prompt) != manifest["prompt_sha256"]
            or prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")):
        raise RunIdentityError("Prepared annotation material, rules or prompt changed")
    if not replay:
        verify_original_input(None, metadata)
        original = manifest["original_analysis"]
        if sha_file(Path(original["path"])) != original["sha256"]:
            raise RunIdentityError("Original analysis changed; refuse to continue")
    return manifest, material, prompt


def _base_result(manifest):
    return {
        "schema_version": FORMAT_VERSION, "identity": IDENTITY, "profile_schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "status": "interrupted", "reason": "尚未开始标注。",
        "error_kind": None, "request_validation": None,
        "source_sha256": manifest["source_sha256"], "graph_sha256": manifest["graph_sha256"],
        "execution_model": deepcopy(manifest["execution_model"]),
        "profiles": {}, "locations": {}, "transfer_specs": {}, "sink_boundaries": [], "boundaries": manifest["boundaries"],
        "failure": None,
        "location_evidences_sha256": None,
        "compilation": None,
        "validation": {"status": "not_run", "instruction_count": 0,
                       "profile_count": 0, "location_count": 0, "transfer_spec_count": 0,
                       "atomic_op_count": 0, "evidence_count": 0, "location_evidence_count": 0,
                       "sink_boundary_count": 0, "errors": []},
        "counts": {},
        "notice": "complete 仅表示标注记录完整；不是安全结论或模型标注正确性证明。",
    }


def verify_prepared(run_dir, *, config=None, replay=False):
    """Check an existing preparation without creating clients or rewriting it."""
    directory = Path(run_dir).resolve()
    if not (directory / "manifest.json").is_file():
        raise RunIdentityError("No prepared annotation manifest exists")
    if config is None:
        config = read_json(directory / "manifest.json")["config"]
    with _exclusive_run(directory):
        return _verify(directory, config, replay)[0]


def _counts(directory):
    call_dir = directory / CALL_PATH
    exists = (call_dir / "call.json").exists()
    result = {"logical_calls": int(exists), "http_attempts": 0, "http_retries": 0,
              "http_attempts_observed": not exists, "returned_models": [],
              "known_token_usage": {}, "record_integrity_errors": []}
    if not exists:
        return result
    try:
        trace = validated_trace(call_dir / "transport.json")
        metrics = call_metrics(trace)
        result.update({name: metrics[name] for name in
                       ("http_attempts", "http_retries", "known_token_usage")})
        result["http_attempts_observed"] = bool(trace) and all(
            c.get("http_attempts_observed") is not False for c in trace)
        names = {c.get("returned_model") for c in trace}
        names.update(a.get("returned_model") for c in trace for a in c.get("http_attempts", []))
        result["returned_models"] = sorted(n for n in names if n)
    except Exception as error:
        result["record_integrity_errors"].append(f"{type(error).__name__}: {error}")
    return result


def _verify_saved_projection(directory, payload, location_evidences, execution_model_identity, compilation=None,
                             request_validation=None):
    """A saved successful run must still agree with the complete accepted response."""
    path = directory / "result.json"
    if not path.exists():
        return
    try:
        saved = read_json(path)
    except (OSError, ValueError, TypeError) as error:
        raise RunIdentityError("Saved annotation payload or location evidence is unreadable") from error
    if not isinstance(saved, dict):
        raise RunIdentityError("Saved annotation payload or location evidence has an invalid shape")
    if saved.get("status") not in {"complete"}:
        return
    if saved.get("execution_model") != execution_model_identity:
        raise RunIdentityError("Saved annotation runtime contract identity mismatch")
    if request_validation is None or saved.get("request_validation") != request_validation:
        raise RunIdentityError("Saved annotation request identity differs")
    sidecar = directory / "audit/location-evidences.json"
    try:
        table = read_json(sidecar) if sidecar.is_file() else None
    except (OSError, ValueError, TypeError) as error:
        raise RunIdentityError("Saved annotation payload or location evidence is unreadable") from error
    if (saved.get("identity") != IDENTITY or saved.get("schema_version") != FORMAT_VERSION
            or saved.get("profile_schema_version") != SCHEMA_VERSION
            or any(saved.get(name) != value for name, value in payload.items())
            or not sidecar.is_file()
            or table != location_evidences
            or saved.get("location_evidences_sha256") != canonical_sha256(location_evidences)):
        raise RunIdentityError("Saved annotation payload or location evidence differs from the accepted response")
    if compilation is None or saved.get("compilation") != compilation_certificate(*compilation):
        raise RunIdentityError("Saved annotation compilation identity differs")
    try:
        if read_json(directory / "sink-boundaries.json") != payload["sink_boundaries"]:
            raise RunIdentityError("Saved annotation sink boundary projection differs")
    except (OSError, ValueError, TypeError) as error:
        raise RunIdentityError("Saved annotation sink boundary projection differs") from error
    for name, value in zip(("raw-annotation", "compiled-response", "compilation-map"), compilation):
        if read_json(directory / "audit" / (name + ".json")) != value:
            raise RunIdentityError("Saved annotation compilation material differs: " + name)


def compilation_certificate(raw, compiled, mapping):
    """Identity of the actual raw-to-compiled conversion, never a semantic proof."""
    return {"version": mapping["compiler_version"],
            "raw_sha256": canonical_sha256(raw), "compiled_sha256": canonical_sha256(compiled),
            "mapping_sha256": canonical_sha256(mapping),
            "sink_boundaries_sha256": canonical_sha256(compiled["sink_boundaries"])}


def _save_result(output, result, material, writer, location_evidences=None, compilation=None):
    from .report import render_report
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
    writer.json(output / "profiles.json", result["profiles"])
    writer.json(output / "locations.json", result["locations"])
    writer.json(output / "transfer-specs.json", result["transfer_specs"])
    writer.json(output / "sink-boundaries.json", result["sink_boundaries"])
    writer.json(output / "validation.json", result["validation"])
    writer.text(output / "report.md", render_report(result, material))
    writer.json(output / "result.json", result)


def run_annotation(run_dir, *, client=None, client_factory=None, config=None, secrets=(),
                   replay=False, stop_event=None, progress=None):
    """Consume one saved response or make exactly one new logical request."""
    directory = Path(run_dir).resolve()
    if not (directory / "manifest.json").exists():
        raise RunIdentityError("No prepared annotation manifest exists")
    if replay and (client is not None or client_factory is not None):
        raise ValueError("Offline replay does not accept an online client")
    if client is not None and client_factory is not None:
        raise ValueError("Inject either client or client_factory, not both")
    if config is None:
        config = read_json(directory / "manifest.json")["config"]
    writer = ArtifactWriter(tuple(secrets))
    stopping = stop_event or Event()
    with _exclusive_run(directory):
        manifest, material, prompt = _verify(directory, config, replay)
        result = _base_result(manifest)
        output = directory / "replay" if replay else directory
        if manifest["preparation_status"] != "ready":
            result.update(status="input_error", reason=manifest["preparation_error"])
            result["counts"] = _counts(directory)
            _save_result(output, result, material, writer)
            return result
        result["validation"]["instruction_count"] = sum(
            len(b["instructions"]) for b in material["cfg"]["blocks"].values())
        boundary_path = directory / "execution-boundary.json"
        boundary = _unseal(read_json(boundary_path)) if replay and boundary_path.exists() else {"kind": "none"}
        if not replay:
            writer.json(boundary_path, _seal({"kind": "none"}))

        def pause(kind):
            if (replay and boundary["kind"] == kind) or (not replay and stopping.is_set()):
                if not replay:
                    writer.json(boundary_path, _seal({"kind": kind}))
                raise KeyboardInterrupt("用户中断；保留已开始调用，不启动后续请求。")

        stage = "input"
        location_evidences = None
        compilation = None
        try:
            if replay and boundary["kind"] == "interrupted":
                if boundary.get("request_validation") is not None:
                    checked = verify_request_identity(directory / CALL_PATH, manifest["config"], prompt=prompt)
                    if checked != boundary["request_validation"]:
                        raise RunIdentityError("Interrupted request identity differs")
                    result["request_validation"] = checked
                raise KeyboardInterrupt(boundary["reason"])
            if replay and boundary["kind"] == "local_error":
                result.update(status=boundary["status"], reason=boundary["reason"],
                              error_kind=boundary.get("error_kind"))
                result["validation"] = boundary["validation"]
                result["counts"] = _counts(directory)
                _save_result(output, result, material, writer)
                return result
            if writer.clean(material) != material or writer.clean(prompt) != prompt:
                raise ValueError("A credential overlaps the verified annotation input")
            pause("before_call")
            call_dir = directory / CALL_PATH
            exists = (call_dir / "call.json").exists()
            if replay and not exists:
                raise KeyboardInterrupt("离线重放没有已保存的调用，不创建在线请求。")
            stage = "call"
            if exists:
                selected = SavedResponseClient(call_dir, writer)
            else:
                factory = client_factory or (injected_factory(client) if client is not None else None)
                if factory is None:
                    raise ValueError("An explicitly injected annotation client is required")
                selected = RecordingClient(call_dir, factory, writer)
            if progress:
                progress("读取已有响应" if exists else "开始整图安全标注（唯一逻辑调用）")
            pause("before_call")
            response = selected.complete(prompt)
            recovered = SavedResponseClient(call_dir, writer).complete(prompt)
            if canonical_sha256(response) != canonical_sha256(recovered):
                raise ValueError("Actual and saved model responses differ")
            try:
                result["request_validation"] = verify_request_identity(call_dir, manifest["config"], prompt=prompt)
            except ResponseIntegrityError as error:
                if exists or replay:
                    raise RunIdentityError("Saved annotation request identity differs") from error
                raise
            pause("after_call")
            stage = "parse"
            parsed_response = _json_object(recovered)
            stage = "validate"
            compilation = compile_response(parsed_response, material)
            annotation = compilation[1]
            payload = to_payload(annotation)
            location_evidences = annotation["location_evidences"]
            _verify_saved_projection(directory, payload, location_evidences, manifest["execution_model"], compilation,
                                     result["request_validation"])
            result.update(payload)
            result["compilation"] = compilation_certificate(*compilation)
            result["location_evidences_sha256"] = canonical_sha256(location_evidences)
            location_evidence_count = sum(len(items) for items in location_evidences.values())
            result["validation"].update(
                status="passed", profile_count=len(annotation["profiles"]),
                location_count=len(annotation["locations"]), transfer_spec_count=len(annotation["transfer_specs"]),
                sink_boundary_count=len(annotation["sink_boundaries"]),
                atomic_op_count=sum(len(event.atomic_ops) for spec in AnnotationResponse.model_validate(annotation).transfer_specs.values()
                                    for event in iter_effect_events(spec)),
                location_evidence_count=location_evidence_count,
                evidence_count=(sum(len(p["evidences"]) for p in annotation["profiles"].values())
                                + sum(1 for _ in iter_spec_evidence(AnnotationResponse.model_validate(annotation)))
                                + location_evidence_count),
            )
            result.update(status="complete",
                          reason="标注及符号传播说明完整；结构、操作覆盖与证据定位校验通过。")
        except RunIdentityError:
            raise
        except SemanticFailure as error:
            result.update(status="semantic_failure", reason=writer.clean(error.reason),
                          error_kind="cannot_assess", failure=writer.clean(error.failure))
            result["validation"].update(status="task_failed", errors=[result["reason"]])
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(str(error)), error_kind="interrupted")
            if not replay:
                writer.json(boundary_path, _seal({"kind": "interrupted", "reason": result["reason"],
                                                 "request_validation": result["request_validation"]}))
        except Exception as error:
            if result["request_validation"] is None and (directory / CALL_PATH / "transport.json").is_file():
                try:
                    result["request_validation"] = verify_request_identity(directory / CALL_PATH, manifest["config"], prompt=prompt)
                except ResponseIntegrityError as identity_error:
                    if replay or (directory / "result.json").exists():
                        raise RunIdentityError("Saved failed request identity differs") from identity_error
                    error = identity_error
            interrupted = isinstance(error, SavedCallFailure) and error.error_type == "KeyboardInterrupt"
            status = "interrupted" if interrupted else {
                "input": "input_error", "call": "execution_error", "parse": "invalid_response",
                "validate": "invalid_response"}[stage]
            message = writer.clean(str(error))
            error_type = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
            kind = ("interrupted" if interrupted else "output_truncated" if error_type == "OutputTruncatedError"
                    else "incomplete_transport" if message.startswith("Incomplete SSE response:")
                    else "request_identity" if error_type == "ResponseIntegrityError"
                    else {"input": "input", "call": "execution", "parse": "json_format",
                          "validate": "structure_or_evidence"}[stage])
            result.update(status=status, reason=message, error_kind=kind)
            if not interrupted:
                result["validation"].update(status="failed" if stage in {"parse", "validate"} else "not_run", errors=[message])
            if not replay and (stage == "input" or not (directory / CALL_PATH / "call.json").exists()):
                writer.json(boundary_path, _seal({"kind": "local_error", "status": status,
                                                 "reason": message, "error_kind": kind,
                                                 "validation": result["validation"]}))
        result["counts"] = writer.clean(_counts(directory))
        _save_result(output, result, material, writer, location_evidences, compilation)
        if progress:
            progress(f"{result['status']}：{result['reason']}")
        return result


def replay_run(run_dir):
    """Rebuild parsing, evidence checks and reports with zero online clients."""
    return run_annotation(run_dir, replay=True)
