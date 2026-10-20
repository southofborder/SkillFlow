"""One sidecar semantic review; original annotations are never written."""
from __future__ import annotations

from copy import deepcopy
from contextlib import nullcontext
from pathlib import Path
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
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
from skillflow.propagation.annotation.config import annotation_config
from skillflow.propagation.annotation.config import PUBLIC_CONFIG_FIELDS
from skillflow.propagation.annotation.loading import load_annotation_run
from skillflow.propagation.annotation.inputs import (read_component, write_material_parts,
    read_material_parts, load_prepared_material)
from skillflow.propagation.annotation.runner import _text
from skillflow.propagation.annotation.runner import compilation_certificate
from skillflow.propagation.annotation.services import compile_response
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.json_normalization import NORMALIZATION_VERSION
from skillflow.common.structural_correction import ResponseChain, ResponseChainError, chain_counts
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.material import checked_review_material
from skillflow.propagation.review.models import SCHEMA_VERSION
from skillflow.propagation.review.models import review_summary
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.review.services import resolve_findings

IDENTITY = "skill-ir-annotation-review-v11"
FORMAT_VERSION = 11
CALL_PATH = "calls/review/a001"
POLICY = {"semantic_reviews": 1, "semantic_repairs": 0, "structural_corrections": "unlimited",
          "json_normalization": NORMALIZATION_VERSION,
          "sidecar_only": True, "automatic_resend_after_acceptance": False}


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
    return {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
            for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}


def _call_files(directory):
    return {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
            for p in sorted(directory.rglob("*")) if p.is_file()}


def prepare_run(annotation_run, *, run_dir, config=None, secrets=(),
                raw_annotation=None, authored_metadata=None):
    """Freeze a verified current run, or an explicitly authored candidate based on it.

    Authorship/mutations are outside model material. A candidate never replaces
    the accepted upstream response. No model client is constructed here.
    """
    source = checked_run_path(annotation_run)
    directory = checked_run_path(run_dir)
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
        upstream_reference = make_run_reference(directory, source)
        if load_annotation_run(source)["upstream_identity"] != original["upstream_identity"]:
            raise RunIdentityError("Upstream annotation changed while being referenced")
        if raw_annotation is not None:
            writer.json(directory / "inputs/candidate.json", candidate)
        writer.json(directory / "inputs/targets.json", material["target_index"])
        writer.json(directory / "inputs/observations.json", material["observations"])
        _text(directory / "inputs/prompt.txt", prompt, writer)
        manifest = _seal({
            "identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "review_schema_version": SCHEMA_VERSION, "run_id": directory.name,
            "created_at": now(), "config": public,
            "implementation": implementation_provenance(),
            "upstream_identity": original["upstream_identity"],
            "upstream": upstream_reference,
            "candidate_origin": "accepted_annotation" if raw_annotation is None else "authored_candidate",
            "authored_metadata": deepcopy(authored_metadata),
            "material_sha256": canonical_sha256(material), "prompt_sha256": canonical_sha256(prompt),
            "candidate_sha256": canonical_sha256(candidate),
            "compilation": compilation_certificate(raw, compiled, mapping), "files": _files(directory),
            "preparation_status": "ready",
            "policy": POLICY,
        })
        writer.json(directory / "manifest.json", manifest)
        return manifest


def prepare_candidate_run(material, raw_annotation, *, run_dir, provenance,
                          config=None, secrets=(), upstream_run=None):
    """Freeze a new explicitly authored/reconstructed candidate, never a fake call.

    Provenance remains external to the model prompt. The caller supplies audited
    history/reconstruction metadata; normal production does not reinterpret old
    accepted responses through this entry point.
    """
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("Explicit candidate requires nonempty provenance")
    directory = checked_run_path(run_dir)
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
        upstream_reference = None
        if upstream_run is None:
            write_material_parts(directory, material, writer, authored_task=True)
        else:
            owner = checked_run_path(upstream_run)
            if load_prepared_material(owner) != material:
                raise RunIdentityError("Explicit review material differs from its owner")
            upstream_reference = make_run_reference(directory, owner)
        writer.json(directory / "inputs/provenance.json", provenance)
        writer.json(directory / "inputs/candidate.json", raw_annotation)
        writer.json(directory / "inputs/targets.json", prepared["target_index"])
        writer.json(directory / "inputs/observations.json", prepared["observations"])
        _text(directory / "inputs/prompt.txt", prompt, writer)
        manifest = _seal({
            "identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "review_schema_version": SCHEMA_VERSION, "run_id": directory.name,
            "created_at": now(), "config": public,
            "implementation": implementation_provenance(),
            "upstream_identity": {"material_sha256": canonical_sha256(material),
                                  "provenance_sha256": canonical_sha256(provenance)},
            "upstream": upstream_reference, "candidate_origin": "explicit_candidate",
            "task_origin": "authored_fixture" if upstream_run is None else "referenced",
            "authored_metadata": deepcopy(provenance),
            "material_sha256": canonical_sha256(prepared),
            "prompt_sha256": canonical_sha256(prompt),
            "candidate_sha256": canonical_sha256(raw_annotation),
            "compilation": compilation_certificate(raw, compiled, mapping),
            "files": _files(directory), "preparation_status": "ready",
            "policy": POLICY,
        })
        writer.json(directory / "manifest.json", manifest)
        return manifest


def _verify(directory, config, *, check_implementation=True):
    manifest = read_json(directory / "manifest.json")
    _unseal(manifest)
    if (manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION
            or manifest.get("review_schema_version") != SCHEMA_VERSION or manifest.get("policy") != POLICY):
        raise RunIdentityError("Unsupported annotation-review run version")
    if check_implementation and manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Review implementation identity changed; use a new run")
    if manifest["config"] != _config(config):
        raise RunIdentityError("Review request configuration changed")
    if manifest["files"] != _files(directory):
        raise RunIdentityError("Frozen review input inventory or bytes changed")
    if manifest["candidate_origin"] == "explicit_candidate":
        upstream = {"material": (load_prepared_material(resolve_run_reference(directory, manifest["upstream"]))
                                 if manifest.get("upstream") is not None else read_material_parts(directory))}
        provenance = read_json(directory / "inputs/provenance.json")
        if canonical_sha256(provenance) != manifest["upstream_identity"]["provenance_sha256"]:
            raise RunIdentityError("Explicit candidate provenance changed")
        if manifest["authored_metadata"] != provenance:
            raise RunIdentityError("Candidate authorship changed")
    else:
        try:
            upstream = load_annotation_run(resolve_run_reference(directory, manifest["upstream"]))
        except (OSError, ValueError) as exc:
            raise RunIdentityError("Upstream annotation verification failed: " + str(exc)) from exc
        if upstream["upstream_identity"] != manifest["upstream_identity"]:
            raise RunIdentityError("Upstream material identity changed")
    candidate = (upstream["raw_annotation"] if manifest["candidate_origin"] == "accepted_annotation"
                 else read_component(directory / "inputs/candidate.json"))
    if manifest["candidate_origin"] == "accepted_annotation" and (directory / "inputs/candidate.json").exists():
        raise RunIdentityError("Accepted review must not duplicate its upstream candidate")
    if canonical_sha256(candidate) != manifest["candidate_sha256"]:
        raise RunIdentityError("Candidate annotation changed")
    if manifest["candidate_origin"] == "accepted_annotation":
        if candidate != upstream["raw_annotation"] or manifest["authored_metadata"] is not None:
            raise RunIdentityError("Accepted annotation was replaced by an authored candidate")
    elif manifest["candidate_origin"] not in {"authored_candidate", "explicit_candidate"} or manifest["authored_metadata"] is None:
        raise RunIdentityError("Invalid candidate provenance")
    raw, compiled, mapping = compile_response(candidate, upstream["material"])
    if manifest.get("compilation") != compilation_certificate(raw, compiled, mapping):
        raise RunIdentityError("Candidate compilation or observation mapping changed")
    material = prepare_review_material(upstream["material"], candidate)
    if (canonical_sha256(read_component(directory / "inputs/targets.json")) != canonical_sha256(material["target_index"])
            or canonical_sha256(read_component(directory / "inputs/observations.json")) != canonical_sha256(material["observations"])):
        raise RunIdentityError("Review targets or observations differ from the frozen candidate")
    prompt = build_prompt(material)
    if (canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(prompt) != manifest["prompt_sha256"]
            or prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")):
        raise RunIdentityError("Review prompt or observation inventory changed")
    return manifest, material, prompt


def load_prepared_review_material(run_dir):
    """Rebuild the reviewer view from its owner, candidate and checked coordinates."""
    directory = checked_run_path(run_dir)
    config = read_component(directory / "manifest.json")["config"]
    return _verify(directory, config, check_implementation=False)[1]


def _counts(directory):
    return chain_counts(directory, "calls/review")


def _base_result(manifest):
    return {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "review_schema_version": SCHEMA_VERSION, "run_id": manifest["run_id"],
            "upstream_identity": manifest["upstream_identity"],
            "material_sha256": manifest["material_sha256"],
            "status": "interrupted", "reason": "Review has not completed.", "error_kind": None, "failure": None,
            "review": None, "summary": None, "resolved_findings": [],
            "request_validation": None, "response_chain": None, "accepted_call": None,
            "validation": {"status": "not_run", "errors": []},
            "counts": {}, "notice": "Sidecar review does not change the annotation; no reported issue is not proof of semantic correctness."}


def result_snapshot(result):
    """Persist review findings once; resolved target values are a computed view."""
    return {key: deepcopy(value) for key, value in result.items() if key != "resolved_findings"}


def run_review(run_dir, *, client=None, client_factory=None, config=None, env_file=None,
               secrets=(), stop_event=None, replay=False, progress=None):
    """Run or replay with strict producer implementation identity."""
    return _run_review(run_dir, client=client, client_factory=client_factory, config=config, env_file=env_file,
        secrets=secrets, stop_event=stop_event, replay=replay, progress=progress)


def _run_review(run_dir, *, client=None, client_factory=None, config=None, env_file=None,
               secrets=(), stop_event=None, replay=False, progress=None, read_only=False):
    """Review once semantically; mechanically invalid responses are corrected.

    Each correction has its own durable request. Accepted and uncertain requests
    are read from storage, never resent, including during an interrupted chain.
    """
    if read_only and not replay:
        raise ValueError("Read-only verification requires saved-response replay")
    directory = checked_run_path(run_dir)
    if not (directory / "manifest.json").is_file():
        raise RunIdentityError("No prepared annotation-review manifest exists")
    if replay and (client is not None or client_factory is not None):
        raise ValueError("Offline replay does not accept an online client")
    if client is not None and client_factory is not None:
        raise ValueError("Inject either a client or a factory")
    config = read_json(directory / "manifest.json")["config"] if config is None else config
    writer = ArtifactWriter(tuple(secrets))
    stopping = stop_event or Event()
    with (nullcontext() if read_only else exclusive_run(directory)):
        manifest, material, prompt = _verify(directory, config, check_implementation=not read_only)
        config = manifest["config"]
        result = _base_result(manifest)
        boundary_path = directory / "execution-boundary.json"
        boundary = _unseal(read_json(boundary_path)) if replay and boundary_path.exists() else None
        existing = None
        if (directory / "result.json").is_file():
            existing = _unseal(read_json(directory / "result.json"))
        stage = "input"
        chain = None
        local_failure = replay and boundary and boundary["kind"] == "local_error"
        try:
            if local_failure:
                if boundary["result_fields"].get("response_chain") is not None:
                    paused = ResponseChain(directory, prefix="calls/review", base_prompt=prompt,
                        request_kind="review", config=config, writer=writer,
                        validate=lambda response: validate_response(response, material),
                        replay=True, read_only=True, interruption=boundary["cursor"])
                    try:
                        paused.run()
                    except KeyboardInterrupt:
                        pass
                    else:
                        raise RunIdentityError("Local failure boundary unexpectedly completed its response chain")
                    if paused.snapshot() != boundary["result_fields"]["response_chain"]:
                        raise RunIdentityError("Local failure response-chain preparation changed")
                result.update(boundary["result_fields"])
                raise _LocalFailureReplay()
            if replay and boundary and boundary["kind"] == "interrupted":
                if boundary.get("call_files") != _call_files(directory / "calls/review"):
                    raise RunIdentityError("Interrupted call material changed")
            if writer.clean(prompt) != prompt:
                raise ValueError("A credential overlaps review prompt")
            if not replay:
                writer.json(boundary_path, _seal({"kind": "running"}))
            stage = "call"
            factory = client_factory or (injected_factory(client) if client is not None else None)
            factory_provider = None
            if factory is None and not replay:
                def factory_provider(call_writer):
                    selected_factory, loaded_secrets = streaming_factory(config, env_file=env_file)
                    call_writer.secrets = tuple(set(call_writer.secrets) | set(loaded_secrets))
                    return selected_factory
            def validate_candidate(response):
                nonlocal stage
                stage = "validate"
                return validate_response(response, material)
            chain = ResponseChain(directory, prefix="calls/review", base_prompt=prompt,
                request_kind="review", config=config, writer=writer, validate=validate_candidate,
                client_factory=factory, factory_provider=factory_provider,
                stop_event=stopping, replay=replay, read_only=read_only,
                progress=progress, recording_client=RecordingClient, saved_client=SavedResponseClient,
                interruption=boundary.get("cursor") if replay and boundary and boundary["kind"] == "interrupted" else None)
            review = chain.run()
            result.update(status="complete", reason="Review structure, references, evidence and declared coverage passed validation.",
                          review=review.model_dump(mode="json"), summary=review_summary(review),
                          resolved_findings=resolve_findings(review, material),
                          validation={"status": "passed", "errors": []})
        except SemanticFailure as error:
            result.update(status="semantic_failure", reason=writer.clean(error.reason),
                          error_kind="semantic_failure", failure=writer.clean(error.failure),
                          validation={"status": "passed", "errors": []})
        except RunIdentityError:
            raise
        except ResponseChainError as error:
            raise RunIdentityError(str(error)) from error
        except _LocalFailureReplay:
            pass
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(str(error)), error_kind="interrupted")
        except Exception as error:
            if isinstance(error, ResponseIntegrityError) and (existing or replay):
                raise RunIdentityError("Saved review request identity changed") from error
            typ = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
            interrupted = typ == "KeyboardInterrupt"
            kind = ("interrupted" if interrupted else "output_truncated" if typ == "OutputTruncatedError"
                    else "incomplete_transport" if str(error).startswith("Incomplete SSE response:")
                    else "request_identity" if typ == "ResponseIntegrityError"
                    else "input" if stage == "input" else "execution")
            result.update(status="interrupted" if interrupted else "input_error" if stage == "input" else "execution_error",
                          error_kind=kind, reason=writer.clean(str(error)),
                          validation={"status": "failed", "errors": [writer.clean(str(error))]})
            if interrupted:
                result["validation"] = {"status": "not_run", "errors": []}
        if chain is not None:
            result["response_chain"] = chain.snapshot()
            result["accepted_call"] = chain.accepted_call
            result["request_validation"] = chain.request_validation
        result["counts"] = writer.clean(_counts(directory))
        if existing and (replay or existing["status"] == "complete") and canonical_sha256(existing) != canonical_sha256(result_snapshot(result)):
            raise RunIdentityError("Saved review result differs from replayed accepted response")
        if not replay:
            saved_boundary = {"kind": "interrupted" if result["status"] == "interrupted" else "finished",
                              "reason": result["reason"], "request_validation": result["request_validation"],
                              "cursor": chain.cursor if chain is not None else None}
            if result["status"] == "interrupted":
                saved_boundary["call_files"] = _call_files(directory / "calls/review")
            if result["status"] in {"input_error", "execution_error"} and (
                    chain is None or not (directory / chain.cursor["call"] / "call.json").exists()):
                saved_boundary.update(kind="local_error", result_fields={key: result[key] for key in (
                    "status", "reason", "error_kind", "validation", "request_validation", "response_chain", "accepted_call")})
            writer.json(boundary_path, _seal(saved_boundary))
        output = directory / "replay" if replay else directory
        from skillflow.propagation.review.report import write_reports
        if not read_only:
            write_reports(output, result, material, writer=writer)
            writer.json(output / "result.json", _seal(result_snapshot(result)))
        if progress:
            progress(result["status"] + "：" + result["reason"])
        return result


def replay_run(run_dir):
    return run_review(run_dir, replay=True)


def _readonly_inventory(directory):
    """Bind protocol records, not generated reports or derivative replay output."""
    return {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
            for p in sorted(directory.rglob("*")) if p.is_file()
            and "replay" not in p.relative_to(directory).parts
            and p.name not in {".runner.lock", "report.html", "report.md"}}


def load_review_run(run_dir):
    """Read a supported review by revalidating its saved response, without writes."""
    from skillflow.propagation.annotation.loading import _read
    directory = checked_run_path(run_dir)
    before = _readonly_inventory(directory)
    manifest = _read(directory / "manifest.json")
    saved = _unseal(_read(directory / "result.json"))
    producer = manifest.get("implementation", {})
    if (not producer.get("files") or canonical_sha256(producer["files"]) != producer.get("sha256")):
        raise RunIdentityError("Saved review producer identity is invalid")
    result = _run_review(directory, replay=True, read_only=True)
    if canonical_sha256(result_snapshot(result)) != canonical_sha256(saved) or _readonly_inventory(directory) != before:
        raise RunIdentityError("Saved review decision or files differ from checked response")
    return {"manifest": manifest, "result": result,
            "material": load_prepared_review_material(directory),
            "upstream_identity": {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
                                  "implementation": producer, "files": before}}


class _LocalFailureReplay(Exception):
    """Internal branch without constructing a client for a pre-request failure."""
