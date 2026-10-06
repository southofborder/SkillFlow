"""One sidecar semantic review; original annotations are never written."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.artifacts import call_metrics
from skillflow.common.runs import exclusive_run
from skillflow.common.recording import RecordingClient
from skillflow.common.recording import SavedResponseClient
from skillflow.common.recording import SavedCallFailure
from skillflow.common.recording import ResponseIntegrityError
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import injected_factory
from skillflow.common.recording import now
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import streaming_factory
from skillflow.common.recording import validated_trace
from skillflow.common.recording import verify_request_identity
from skillflow.propagation.annotation.config import annotation_config
from skillflow.propagation.annotation.config import PUBLIC_CONFIG_FIELDS
from skillflow.propagation.annotation.loading import load_annotation_run
from skillflow.propagation.annotation.runner import _text
from skillflow.propagation.annotation.runner import compilation_certificate
from skillflow.propagation.annotation.services import compile_response
from skillflow.common.source_evidence import _json_object
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.material import checked_review_material
from skillflow.propagation.review.models import SCHEMA_VERSION
from skillflow.propagation.review.models import review_summary
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.review.services import resolve_findings

IDENTITY = "skill-ir-annotation-review-v4"
FORMAT_VERSION = 4
CALL_PATH = "calls/review/a001"


class RunIdentityError(ValueError):
    """Frozen review materials or implementation no longer match."""


def _seal(value):
    return {**deepcopy(value), "integrity_sha256": canonical_sha256(value)}


def _unseal(value):
    copied = deepcopy(value)
    saved = copied.pop("integrity_sha256", None)
    if canonical_sha256(copied) != saved:
        raise RunIdentityError("Review artifact digest mismatch")
    return copied


def _config(value):
    value = {} if value is None else value
    if not isinstance(value, dict) or set(value) - set(PUBLIC_CONFIG_FIELDS):
        raise ValueError("Review configuration accepts public LLM parameters only")
    return annotation_config(value)


def _files(directory):
    return {p.relative_to(directory).as_posix(): sha_file(p)
            for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}


def _call_files(directory):
    return {p.relative_to(directory).as_posix(): sha_file(p)
            for p in sorted(directory.rglob("*")) if p.is_file()}


def prepare_run(annotation_run, *, run_dir, config=None, secrets=(),
                raw_annotation=None, authored_metadata=None):
    """Freeze a verified current run, or an explicitly authored candidate based on it.

    Authorship/mutations are outside model material. A candidate never replaces
    the accepted upstream response. No model client is constructed here.
    """
    source = Path(annotation_run).resolve()
    directory = Path(run_dir).resolve()
    if directory == source or directory.is_relative_to(source) or source.is_relative_to(directory):
        raise ValueError("Review and upstream run directories must not overlap")
    if (raw_annotation is None) != (authored_metadata is None):
        raise ValueError("Authored candidates require explicit external authorship metadata")
    original = load_annotation_run(source)
    public = _config(config)
    writer = ArtifactWriter(tuple(secrets))
    candidate = original["raw_annotation"] if raw_annotation is None else deepcopy(raw_annotation)
    raw, compiled, mapping = compile_response(candidate, original["material"])
    material = prepare_review_material(original["material"], candidate)
    prompt = build_prompt(material)
    if writer.clean(material) != material:
        raise ValueError("A credential overlaps review input")
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise RunIdentityError("Prepare requires a new or empty review directory")
        # Preserve original bytes, accepted calls and producer hashes separately.
        shutil.copytree(source, directory / "inputs/upstream", ignore=lambda path, names: (
            set(names) & {".runner.lock", "replay", "report.md", "report.html"}
            if Path(path).resolve() == source else set()))
        frozen = load_annotation_run(directory / "inputs/upstream")
        if frozen["upstream_identity"] != original["upstream_identity"]:
            raise RunIdentityError("Upstream annotation changed while being frozen")
        writer.json(directory / "inputs/candidate.json", candidate)
        writer.json(directory / "inputs/candidate-compilation.json", {
            "compiled": compiled, "mapping": mapping,
            "certificate": compilation_certificate(raw, compiled, mapping)})
        writer.json(directory / "inputs/material.json", material)
        _text(directory / "inputs/prompt.txt", prompt, writer)
        manifest = _seal({
            "identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "review_schema_version": SCHEMA_VERSION, "run_id": directory.name,
            "created_at": now(), "config": public,
            "implementation": implementation_provenance(),
            "upstream_identity": original["upstream_identity"],
            "upstream_path": str(source),
            "candidate_origin": "accepted_annotation" if raw_annotation is None else "authored_candidate",
            "authored_metadata": deepcopy(authored_metadata),
            "material_sha256": canonical_sha256(material), "prompt_sha256": canonical_sha256(prompt),
            "candidate_sha256": canonical_sha256(candidate), "files": _files(directory),
            "preparation_status": "ready",
            "policy": {"planned_logical_calls": 1, "automatic_repairs": 0,
                       "sidecar_only": True, "automatic_resend_after_acceptance": False},
        })
        writer.json(directory / "manifest.json", manifest)
        return manifest


def prepare_candidate_run(material, raw_annotation, *, run_dir, provenance,
                          config=None, secrets=()):
    """Freeze a new explicitly authored/reconstructed candidate, never a fake call.

    Provenance remains external to the model prompt. The caller supplies audited
    history/reconstruction metadata; normal production does not reinterpret old
    accepted responses through this entry point.
    """
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("Explicit candidate requires nonempty provenance")
    directory = Path(run_dir).resolve()
    public = _config(config)
    writer = ArtifactWriter(tuple(secrets))
    prepared = prepare_review_material(material, raw_annotation)
    raw, compiled, mapping = compile_response(raw_annotation, material)
    prompt = build_prompt(prepared)
    if writer.clean(prepared) != prepared or writer.clean(provenance) != provenance:
        raise ValueError("A credential overlaps review input or provenance")
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise RunIdentityError("Prepare requires a new or empty review directory")
        writer.json(directory / "inputs/annotation-material.json", material)
        writer.json(directory / "inputs/provenance.json", provenance)
        writer.json(directory / "inputs/candidate.json", raw_annotation)
        writer.json(directory / "inputs/candidate-compilation.json", {
            "compiled": compiled, "mapping": mapping,
            "certificate": compilation_certificate(raw, compiled, mapping)})
        writer.json(directory / "inputs/material.json", prepared)
        _text(directory / "inputs/prompt.txt", prompt, writer)
        manifest = _seal({
            "identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "review_schema_version": SCHEMA_VERSION, "run_id": directory.name,
            "created_at": now(), "config": public,
            "implementation": implementation_provenance(),
            "upstream_identity": {"material_sha256": canonical_sha256(material),
                                  "provenance_sha256": canonical_sha256(provenance)},
            "upstream_path": None, "candidate_origin": "explicit_candidate",
            "authored_metadata": deepcopy(provenance),
            "material_sha256": canonical_sha256(prepared),
            "prompt_sha256": canonical_sha256(prompt),
            "candidate_sha256": canonical_sha256(raw_annotation),
            "files": _files(directory), "preparation_status": "ready",
            "policy": {"planned_logical_calls": 1, "automatic_repairs": 0,
                       "sidecar_only": True, "automatic_resend_after_acceptance": False},
        })
        writer.json(directory / "manifest.json", manifest)
        return manifest


def _verify(directory, config):
    manifest = read_json(directory / "manifest.json")
    _unseal(manifest)
    if (manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION
            or manifest.get("review_schema_version") != SCHEMA_VERSION):
        raise RunIdentityError("Unsupported annotation-review run version")
    if manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Review implementation identity changed; use a new run")
    if manifest["config"] != _config(config):
        raise RunIdentityError("Review request configuration changed")
    if manifest["files"] != _files(directory):
        raise RunIdentityError("Frozen review input inventory or bytes changed")
    if manifest["candidate_origin"] == "explicit_candidate":
        upstream = {"material": read_json(directory / "inputs/annotation-material.json")}
        provenance = read_json(directory / "inputs/provenance.json")
        if canonical_sha256(provenance) != manifest["upstream_identity"]["provenance_sha256"]:
            raise RunIdentityError("Explicit candidate provenance changed")
        if manifest["authored_metadata"] != provenance:
            raise RunIdentityError("Candidate authorship changed")
    else:
        upstream = load_annotation_run(directory / "inputs/upstream")
        if upstream["upstream_identity"] != manifest["upstream_identity"]:
            raise RunIdentityError("Upstream material identity changed")
    candidate = read_json(directory / "inputs/candidate.json")
    if canonical_sha256(candidate) != manifest["candidate_sha256"]:
        raise RunIdentityError("Candidate annotation changed")
    if manifest["candidate_origin"] == "accepted_annotation":
        if candidate != upstream["raw_annotation"] or manifest["authored_metadata"] is not None:
            raise RunIdentityError("Accepted annotation was replaced by an authored candidate")
    elif manifest["candidate_origin"] not in {"authored_candidate", "explicit_candidate"} or manifest["authored_metadata"] is None:
        raise RunIdentityError("Invalid candidate provenance")
    raw, compiled, mapping = compile_response(candidate, upstream["material"])
    if read_json(directory / "inputs/candidate-compilation.json") != {
            "compiled": compiled, "mapping": mapping,
            "certificate": compilation_certificate(raw, compiled, mapping)}:
        raise RunIdentityError("Candidate compilation or observation mapping changed")
    material = checked_review_material(read_json(directory / "inputs/material.json"))
    if material != prepare_review_material(upstream["material"], candidate):
        raise RunIdentityError("Review material differs from the frozen candidate")
    prompt = build_prompt(material)
    if (canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(prompt) != manifest["prompt_sha256"]
            or prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")):
        raise RunIdentityError("Review prompt or observation inventory changed")
    return manifest, material, prompt


def _counts(directory):
    call = directory / CALL_PATH
    exists = (call / "call.json").is_file()
    counts = {"logical_calls": int(exists), "http_attempts": 0, "http_retries": 0,
              "returned_models": [], "known_token_usage": {}, "record_integrity_errors": []}
    if exists:
        try:
            trace = validated_trace(call / "transport.json")
            metrics = call_metrics(trace)
            counts.update({k: metrics[k] for k in ("http_attempts", "http_retries", "known_token_usage")})
            counts["http_attempts_observed"] = bool(trace) and all(
                t.get("http_attempts_observed") is not False for t in trace)
            counts["returned_models"] = sorted({t["returned_model"] for t in trace if t.get("returned_model")})
        except Exception as error:
            counts["record_integrity_errors"].append(str(error))
    return counts


def _base_result(manifest):
    return {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "review_schema_version": SCHEMA_VERSION, "run_id": manifest["run_id"],
            "upstream_identity": manifest["upstream_identity"],
            "material_sha256": manifest["material_sha256"],
            "status": "interrupted", "reason": "尚未完成审查。", "error_kind": None, "failure": None,
            "review": None, "summary": None, "resolved_findings": [],
            "request_validation": None, "validation": {"status": "not_run", "errors": []},
            "counts": {}, "notice": "旁置审查不改变原标注状态；未发现问题不等于语义正确性证明。"}


def run_review(run_dir, *, client=None, client_factory=None, config=None, env_file=None,
               secrets=(), stop_event=None, replay=False, progress=None):
    """Review once; a recorded accepted or uncertain request is never resent."""
    directory = Path(run_dir).resolve()
    if not (directory / "manifest.json").is_file():
        raise RunIdentityError("No prepared annotation-review manifest exists")
    if replay and (client is not None or client_factory is not None):
        raise ValueError("Offline replay does not accept an online client")
    if client is not None and client_factory is not None:
        raise ValueError("Inject either a client or a factory")
    config = read_json(directory / "manifest.json")["config"] if config is None else config
    writer = ArtifactWriter(tuple(secrets))
    stopping = stop_event or Event()
    with exclusive_run(directory):
        manifest, material, prompt = _verify(directory, config)
        config = manifest["config"]
        result = _base_result(manifest)
        boundary_path = directory / "execution-boundary.json"
        boundary = _unseal(read_json(boundary_path)) if replay and boundary_path.exists() else None
        existing = None
        if (directory / "result.json").is_file():
            existing = _unseal(read_json(directory / "result.json"))
        stage = "input"
        call_dir = directory / CALL_PATH
        local_failure = replay and boundary and boundary["kind"] == "local_error"
        try:
            if local_failure:
                # No request existed. Reproduce the saved local execution error,
                # not an invented missing-response interruption.
                result.update(boundary["result_fields"])
                raise _LocalFailureReplay()
            if replay and boundary and boundary["kind"] == "interrupted":
                if boundary.get("call_files") != _call_files(call_dir):
                    raise RunIdentityError("Interrupted call material changed")
                if boundary.get("request_validation") is not None:
                    check = verify_request_identity(call_dir, config, prompt=prompt)
                    if check != boundary["request_validation"]:
                        raise RunIdentityError("Interrupted request identity changed")
                    result["request_validation"] = check
                raise KeyboardInterrupt(boundary["reason"])
            if stopping.is_set():
                raise KeyboardInterrupt("用户中断；不启动新的审查调用。")
            if writer.clean(prompt) != prompt:
                raise ValueError("A credential overlaps review prompt")
            if not replay:
                writer.json(boundary_path, _seal({"kind": "running"}))
            exists = (call_dir / "call.json").is_file()
            if replay and not exists:
                raise KeyboardInterrupt("没有已保存调用；离线重放不会创建请求。")
            stage = "call"
            if exists:
                selected = SavedResponseClient(call_dir, writer)
            else:
                factory = client_factory or (injected_factory(client) if client is not None else None)
                if factory is None:
                    factory, loaded_secrets = streaming_factory(config, env_file=env_file)
                    writer = ArtifactWriter(tuple(set(secrets) | set(loaded_secrets)))
                selected = RecordingClient(call_dir, factory, writer)
            if progress:
                progress("读取已有审查响应" if exists else "开始唯一一次聚焦审查")
            if stopping.is_set():
                raise KeyboardInterrupt("用户中断；不启动新的审查调用。")
            response = selected.complete(prompt)
            recovered = SavedResponseClient(call_dir, writer).complete(prompt)
            if response != recovered:
                raise ResponseIntegrityError("Actual and saved review responses differ")
            result["request_validation"] = verify_request_identity(call_dir, config, prompt=prompt)
            if stopping.is_set():
                raise KeyboardInterrupt("用户中断；已接受响应保留，恢复时不重发。")
            stage = "parse"
            parsed = _json_object(recovered)
            stage = "validate"
            review = validate_response(parsed, material)
            result.update(status="complete", reason="聚焦审查响应的格式、定位、引文和声明覆盖校验通过。",
                          review=review.model_dump(mode="json"), summary=review_summary(review),
                          resolved_findings=resolve_findings(review, material),
                          validation={"status": "passed", "errors": []})
        except SemanticFailure as error:
            result.update(status="semantic_failure", reason=writer.clean(error.reason),
                          error_kind="semantic_failure", failure=writer.clean(error.failure),
                          validation={"status": "passed", "errors": []})
        except RunIdentityError:
            raise
        except _LocalFailureReplay:
            pass
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(str(error)), error_kind="interrupted")
            if (call_dir / "transport.json").exists():
                result["request_validation"] = verify_request_identity(call_dir, config, prompt=prompt)
        except Exception as error:
            if (call_dir / "transport.json").is_file() and result["request_validation"] is None:
                try:
                    result["request_validation"] = verify_request_identity(call_dir, config, prompt=prompt)
                except ResponseIntegrityError as identity_error:
                    if existing or replay:
                        raise RunIdentityError("Saved review request identity changed") from identity_error
                    error = identity_error
            typ = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
            interrupted = typ == "KeyboardInterrupt"
            kind = ("interrupted" if interrupted else "output_truncated" if typ == "OutputTruncatedError"
                    else "incomplete_transport" if str(error).startswith("Incomplete SSE response:")
                    else "request_identity" if typ == "ResponseIntegrityError"
                    else {"input": "input", "call": "execution", "parse": "json_format",
                          "validate": "structure_or_evidence"}[stage])
            result.update(status="interrupted" if interrupted else "invalid_response" if stage in {"parse", "validate"}
                          else "input_error" if stage == "input" else "execution_error",
                          error_kind=kind, reason=writer.clean(str(error)),
                          validation={"status": "failed", "errors": [writer.clean(str(error))]})
            if interrupted:
                result["validation"] = {"status": "not_run", "errors": []}
        result["counts"] = writer.clean(_counts(directory))
        if existing and (replay or existing["status"] == "complete") and existing != result:
            raise RunIdentityError("Saved review result differs from replayed accepted response")
        if not replay:
            saved_boundary = {"kind": "interrupted" if result["status"] == "interrupted" else "finished",
                              "reason": result["reason"], "request_validation": result["request_validation"]}
            if result["status"] == "interrupted":
                saved_boundary["call_files"] = _call_files(call_dir)
            if result["status"] in {"input_error", "execution_error"} and not (call_dir / "call.json").exists():
                saved_boundary.update(kind="local_error", result_fields={key: result[key] for key in (
                    "status", "reason", "error_kind", "validation", "request_validation")})
            writer.json(boundary_path, _seal(saved_boundary))
        output = directory / "replay" if replay else directory
        from skillflow.propagation.review.report import write_reports
        write_reports(output, result, material, writer=writer)
        writer.json(output / "result.json", _seal(result))
        if progress:
            progress(result["status"] + "：" + result["reason"])
        return result


def replay_run(run_dir):
    return run_review(run_dir, replay=True)


class _LocalFailureReplay(Exception):
    """Internal branch without constructing a client for a pre-request failure."""
