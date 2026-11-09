"""Recorded Task extraction/revision with sealed source ownership and zero-call replay."""
from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from threading import Event
from uuid import uuid4

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import (
    canonical_sha256, implementation_provenance, injected_factory, now, sha_file,
    ResponseIntegrityError, SavedCallFailure,
)
from skillflow.common.runs import exclusive_run
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import _json_object
from skillflow.common.structural_correction import (
    ResponseChain, ResponseChainError, VERSION as STRUCTURAL_VERSION, chain_counts,
    StructuralCorrectionLimitReached,
)
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.propagation.annotation.config import annotation_config, PUBLIC_CONFIG_FIELDS
from skillflow.propagation.contracts.task import checked_task, task_reference, TASK_SCHEMA_VERSION
from skillflow.task.material import prepare_task_material, validate_revision
from skillflow.task.prompts import build_task_prompt
from skillflow.task.services import validate_task_response

IDENTITY = "skillflow-task-extraction-v3"
FORMAT_VERSION = 3
CALL_PREFIX = "calls/task"
POLICY = {"source_only": True, "semantic_repairs": 0, "structural_correction": STRUCTURAL_VERSION,
          "automatic_resend_after_acceptance": False}


def _policy(max_corrections=None, *, allow_cannot_assess=True, self_check=False):
    if max_corrections is not None and (type(max_corrections) is not int or max_corrections < 0):
        raise ValueError("max_corrections must be a nonnegative integer or None")
    if type(allow_cannot_assess) is not bool:
        raise ValueError("allow_cannot_assess must be Boolean")
    if type(self_check) is not bool:
        raise ValueError("self_check must be Boolean")
    return {**deepcopy(POLICY), **({"max_corrections": max_corrections} if max_corrections is not None else {}),
            **({"allow_cannot_assess": False} if not allow_cannot_assess else {}),
            **({"self_check": True} if self_check else {})}


class TaskRunIdentityError(ValueError):
    """Task run inputs, accepted response, or saved identities have changed."""


def _validate_task_candidate(raw, material, policy):
    if not policy.get("allow_cannot_assess", True):
        from skillflow.common.validation import structural_error
        try:
            value = _json_object(raw)
        except (ValueError, TypeError):
            value = None
        if isinstance(value, dict) and value.get("outcome") == "cannot_assess":
            raise structural_error("whole_failure_forbidden", "/outcome",
                "Submit source-supported requirements and unresolved source issues instead of a whole-analysis refusal")
    return validate_task_response(raw, material)


def _read(path):
    return _json_object(checked_run_path(path).read_bytes().decode("utf-8"))


def _seal(value):
    return {**deepcopy(value), "manifest_sha256": canonical_sha256(value)}


def _unseal(value):
    unsigned = {k: v for k, v in value.items() if k != "manifest_sha256"}
    if canonical_sha256(unsigned) != value.get("manifest_sha256"):
        raise TaskRunIdentityError("Task run manifest digest differs")
    return unsigned


def _config(config):
    config = {} if config is None else config
    if type(config) is not dict or set(config) - set(PUBLIC_CONFIG_FIELDS):
        raise ValueError("Only public LLM configuration may be recorded")
    return annotation_config(config)


def _files(directory):
    return {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
            for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}


def _owner_source(owner):
    owner = checked_run_path(owner)
    manifest = _unseal(_read(owner / "manifest.json"))
    if manifest.get("files") is not None and _files(owner) != manifest["files"]:
        raise TaskRunIdentityError("Task source owner frozen input inventory differs")
    if (owner / "inputs/snapshot.json").is_file():
        return read_snapshot(owner)[1]
    return _read(owner / "inputs/source.json")


def _write_exact_text(path, value, writer):
    if writer.clean(value) != value:
        raise ValueError("A credential overlaps exact Task input")
    path.parent.mkdir(parents=True, exist_ok=True)
    # ArtifactWriter intentionally normalizes output newlines on some hosts;
    # model prompts retain their exact UTF-8 bytes for request verification.
    temporary = path.with_name("." + path.name + "." + uuid4().hex + ".tmp")
    try:
        temporary.write_bytes(value.encode("utf-8"))
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_task_run(run_dir, source=None, *, revision=None,
                     config=None, source_owner=None, secrets=(), resume_preparation=False,
                     max_corrections=None, allow_cannot_assess=True, self_check=False):
    """Prepare from an already frozen source; optionally reference its exact owner.

    An explicit owner must directly hold inputs/source.json or a byte snapshot.
    It is digest-bound by its sealed manifest. The consumer saves no source copy.
    """
    directory = checked_run_path(run_dir)
    public, writer = _config(config), ArtifactWriter(tuple(secrets))
    policy = _policy(max_corrections, allow_cannot_assess=allow_cannot_assess, self_check=self_check)
    owner = None if source_owner is None else checked_run_path(source_owner)
    if owner is not None:
        if owner == directory or owner.is_relative_to(directory):
            raise ValueError("Task run cannot contain its source owner")
        frozen_inputs = owner / "inputs"
        if directory == frozen_inputs or directory.is_relative_to(frozen_inputs):
            raise ValueError("Task consumer must not write inside its source owner's frozen inputs")
        owned = _owner_source(owner)
        if source is not None and canonical_sha256(source) != canonical_sha256(owned):
            raise ValueError("Supplied source differs from explicit source owner")
        source = owned
    material = prepare_task_material(source)
    revision = validate_revision(revision, material)
    prompt = build_task_prompt(material, revision, allow_cannot_assess=allow_cannot_assess, self_check=self_check)
    for value in (material, revision, prompt):
        if writer.clean(value) != value:
            raise ValueError("A credential overlaps verified Task input")
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if resume_preparation and (directory / "manifest.json").is_file():
            manifest, saved_material, saved_prompt = _verify(directory, config=public)
            expected_owner = None if owner is None else make_run_reference(directory, owner)
            if (canonical_sha256(saved_material) != canonical_sha256(material) or saved_prompt != prompt
                    or manifest["policy"] != policy
                    or canonical_sha256(manifest["source_owner"]) != canonical_sha256(expected_owner)
                    or manifest["revision_sha256"] != canonical_sha256(revision)):
                raise TaskRunIdentityError("Existing Task preparation belongs to a different request")
            return _read(directory / "manifest.json")
        if not resume_preparation and any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise TaskRunIdentityError("Task preparation requires a new or empty run directory")
        if resume_preparation:
            _check_preparation_prefix(directory, material, revision, prompt, owner)
        if owner is None:
            writer.json(directory / "inputs/source.json", material["source"])
        writer.json(directory / "inputs/request.json", {"revision": revision})
        _write_exact_text(directory / "inputs/prompt.txt", prompt, writer)
        manifest = {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "task_schema_version": TASK_SCHEMA_VERSION, "run_id": directory.name,
            "created_at": now(), "config": public, "implementation": implementation_provenance(),
            "preparation_status": "ready", "source_owner": None if owner is None else make_run_reference(directory, owner),
            "source_sha256": material["source"]["source_sha256"],
            "request_kind": "task_extraction" if revision is None else "task_revision",
            "material_sha256": canonical_sha256(material), "revision_sha256": canonical_sha256(revision),
            "prompt_sha256": canonical_sha256(prompt), "policy": policy, "files": _files(directory)}
        sealed = _seal(manifest)
        writer.json(directory / "manifest.json", sealed)
        return sealed


def _check_preparation_prefix(directory, material, revision, prompt, owner):
    """Accept only exact files this preparation would write, never model artifacts.

    No files are removed or rewritten before the entire prefix is checked. A
    partial prefix is justified by the caller's exact frozen input, not by names.
    """
    expected = {"inputs/request.json": {"revision": revision},
                "inputs/prompt.txt": prompt}
    if owner is None:
        expected["inputs/source.json"] = material["source"]
    for path in directory.rglob("*"):
        checked_run_path(path)
        relative = path.relative_to(directory).as_posix()
        if path.is_dir():
            if relative != "inputs":
                raise TaskRunIdentityError("Unknown directory in unfinished Task preparation: " + relative)
        elif path.is_file():
            if relative == ".runner.lock":
                continue
            if relative not in expected:
                raise TaskRunIdentityError("Unknown file in unfinished Task preparation: " + relative)
            if relative == "inputs/prompt.txt":
                matching = path.read_bytes() == prompt.encode("utf-8")
            else:
                matching = canonical_sha256(_read(path)) == canonical_sha256(expected[relative])
            if not matching:
                raise TaskRunIdentityError("Unfinished Task preparation input differs: " + relative)
        else:
            raise TaskRunIdentityError("Unsupported member in unfinished Task preparation: " + relative)


def verify_task_prepared(run_dir, *, config=None):
    """Check frozen Task preparation without locks, writes, clients, or responses."""
    directory = checked_run_path(run_dir)
    _verify(directory, config=config)
    return _read(directory / "manifest.json")


def _verify(directory, *, config=None, check_implementation=True):
    manifest = _unseal(_read(directory / "manifest.json"))
    saved_policy = manifest.get("policy")
    try:
        policy = _policy(saved_policy.get("max_corrections"),
            allow_cannot_assess=saved_policy.get("allow_cannot_assess", True),
            self_check=saved_policy.get("self_check", False)) if isinstance(saved_policy, dict) else None
    except ValueError as error:
        raise TaskRunIdentityError("Unsupported Task correction policy") from error
    if (manifest.get("identity") != IDENTITY or type(manifest.get("schema_version")) is not int
            or manifest.get("schema_version") != FORMAT_VERSION
            or manifest.get("task_schema_version") != TASK_SCHEMA_VERSION
            or manifest.get("preparation_status") != "ready"
            or canonical_sha256(saved_policy) != canonical_sha256(policy)):
        raise TaskRunIdentityError("Unsupported Task run protocol")
    if config is not None and _config(config) != manifest["config"]:
        raise TaskRunIdentityError("Task run configuration differs")
    producer = manifest.get("implementation")
    if (type(producer) is not dict or type(producer.get("files")) is not dict or not producer["files"]
            or canonical_sha256(producer["files"]) != producer.get("sha256")):
        raise TaskRunIdentityError("Saved Task producer identity is invalid")
    if check_implementation and manifest["implementation"] != implementation_provenance():
        raise TaskRunIdentityError("Task producer implementation differs")
    if _files(directory) != manifest["files"]:
        raise TaskRunIdentityError("Frozen Task inputs differ")
    owner = manifest["source_owner"]
    if owner is None:
        source = _read(directory / "inputs/source.json")
    else:
        if (directory / "inputs/source.json").exists() or (directory / "inputs/snapshot.json").exists():
            raise TaskRunIdentityError("Referenced source must not be copied")
        source = _owner_source(resolve_run_reference(directory, owner))
    request = _read(directory / "inputs/request.json")
    if set(request) != {"revision"}:
        raise TaskRunIdentityError("Task request contains unsupported fields")
    material = prepare_task_material(source)
    revision = validate_revision(request["revision"], material)
    prompt = build_task_prompt(material, revision,
                               allow_cannot_assess=manifest["policy"].get("allow_cannot_assess", True),
                               self_check=manifest["policy"].get("self_check", False))
    if (canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(revision) != manifest["revision_sha256"]
            or canonical_sha256(prompt) != manifest["prompt_sha256"]
            or prompt != (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")
            or material["source"]["source_sha256"] != manifest["source_sha256"]
            or manifest["request_kind"] != ("task_extraction" if revision is None else "task_revision")):
        raise TaskRunIdentityError("Task prepared request identity differs")
    return manifest, material, prompt


def _base_result(manifest):
    return {"identity": IDENTITY, "schema_version": FORMAT_VERSION, "run_id": manifest["run_id"],
            "status": "interrupted", "reason": "Task extraction has not completed.", "error_kind": None,
            "source_sha256": manifest["source_sha256"], "task_ref": None, "failure": None,
            "accepted_call": None, "response_chain": None, "request_validation": None, "counts": {}}


def _report(result, task):
    lines = ["# Task extraction record", "", f"Status: {result['status']}", "", result["reason"], "",
             "Structure and source-reference validation does not prove requirement completeness, demand minimality or absence of DOE.", ""]
    if task is not None:
        lines.extend([f"Task version: `{task['task_sha256']}`", "", task["purpose"]["text"], ""])
        for requirement in task["requirements"]:
            lines.extend([f"- {requirement['id']}：{requirement['text']}"])
            lines.extend(f"  - {e['file']}:{e['start_line']}-{e['end_line']} — {e['reason']}"
                         for e in requirement["evidences"])
        if task["issues"]:
            lines.extend(["", "Conflicts and ambiguities:", ""])
            lines.extend(f"- {issue['id']} ({issue['resolution']})：{issue['reason']}"
                         for issue in task["issues"])
    return "\n".join(lines) + "\n"


def run_task(run_dir, *, client=None, client_factory=None, factory_provider=None,
             config=None, secrets=(), stop_event=None, progress=None, replay=False, read_only=False,
             max_corrections=None):
    """Resume durable calls or replay accepted responses without online access."""
    directory = checked_run_path(run_dir)
    if read_only and not replay:
        raise ValueError("Read-only Task verification requires replay")
    if replay and any(x is not None for x in (client, client_factory, factory_provider)):
        raise ValueError("Task offline replay does not accept online clients")
    if sum(x is not None for x in (client, client_factory, factory_provider)) > 1:
        raise ValueError("Inject only one Task client source")
    writer, stopping = ArtifactWriter(tuple(secrets)), stop_event or Event()
    with (nullcontext() if read_only else exclusive_run(directory)):
        manifest, material, prompt = _verify(directory, config=config, check_implementation=not read_only)
        if max_corrections is not None and _policy(max_corrections,
                allow_cannot_assess=manifest["policy"].get("allow_cannot_assess", True),
                self_check=manifest["policy"].get("self_check", False)) != manifest["policy"]:
            raise TaskRunIdentityError("Task correction policy differs from preparation")
        if writer.clean(material) != material or writer.clean(prompt) != prompt:
            raise ValueError("A credential overlaps verified Task input")
        saved = _read(directory / "result.json") if (directory / "result.json").is_file() else None
        result, task, chain = _base_result(manifest), None, None
        marker_path = directory / "execution-boundary.json"
        marker = _unseal(_read(marker_path)) if replay and marker_path.is_file() else {"kind": "none"}
        if not replay:
            writer.json(marker_path, _seal({"kind": "running"}))
        try:
            factory = client_factory or (injected_factory(client) if client is not None else None)
            strategy = None
            if not manifest["policy"].get("allow_cannot_assess", True):
                # This imports the mechanical record strategy only; Task still
                # receives solely its frozen source and finite revision inputs.
                from skillflow.document_guided.fragments import fragment_correction_strategy
                strategy = fragment_correction_strategy("task")
            chain = ResponseChain(directory, prefix=CALL_PREFIX, base_prompt=prompt,
                request_kind=manifest["request_kind"], config=manifest["config"], writer=writer,
                validate=lambda raw: _validate_task_candidate(raw, material, manifest["policy"]), client_factory=factory,
                factory_provider=factory_provider, stop_event=stopping, progress=progress,
                replay=replay, read_only=read_only,
                correction_strategy=strategy,
                max_corrections=manifest["policy"].get("max_corrections"),
                interruption=marker.get("cursor") if marker["kind"] == "interrupted" else None)
            task = chain.run()
            reference = task_reference(task)
            task_path = directory / "task.json"
            if task_path.exists():
                if canonical_sha256(_read(task_path)) != canonical_sha256(task):
                    raise TaskRunIdentityError("Saved Task differs from accepted response")
            elif replay:
                raise TaskRunIdentityError("Accepted Task artifact is missing")
            else:
                writer.json(task_path, task)
            result.update(status="complete", reason="Independent Task extraction and source-evidence validation completed; semantics still require whole-chain review.",
                          task_ref=reference)
        except (TaskRunIdentityError, ResponseChainError, ResponseIntegrityError) as error:
            raise TaskRunIdentityError(str(error)) from error
        except SemanticFailure as error:
            result.update(status="semantic_failure", reason=writer.clean(error.reason),
                          error_kind="cannot_assess", failure=writer.clean(error.failure))
        except StructuralCorrectionLimitReached as error:
            result.update(status="structural_failure", reason=writer.clean(str(error)),
                          error_kind="correction_limit", failure={"diagnostics": error.diagnostics})
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(str(error)), error_kind="interrupted")
        except Exception as error:
            typ = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
            result.update(status="interrupted" if typ == "KeyboardInterrupt" else "execution_error",
                          reason=writer.clean(str(error)), error_kind=typ)
        if chain is not None:
            result.update(accepted_call=chain.accepted_call, response_chain=chain.snapshot(),
                          request_validation=chain.request_validation)
        try:
            result["counts"] = chain_counts(directory, CALL_PREFIX)
        except Exception:
            result["counts"] = {"status": "unavailable"}
        if saved is not None and (replay or saved.get("status") == "complete"):
            if (canonical_sha256({key: value for key, value in saved.items() if key != "counts"})
                    != canonical_sha256({key: value for key, value in result.items() if key != "counts"})):
                raise TaskRunIdentityError("Task result differs from saved response-chain decision")
            result["counts"] = saved["counts"]
        if not replay:
            writer.json(marker_path, _seal({"kind": "interrupted" if result["status"] == "interrupted" else "finished",
                "cursor": None if chain is None else chain.cursor}))
        if not read_only:
            output = directory / "replay" if replay else directory
            writer.json(output / "result.json", result)
            writer.text(output / "report.md", _report(result, task))
        return {**result, "task": task}


def replay_task(run_dir):
    return run_task(run_dir, replay=True)


def load_task_run(run_dir):
    """Verify the full accepted request chain without writes or live clients."""
    result = run_task(run_dir, replay=True, read_only=True)
    if result["status"] != "complete" or result["task"] is None:
        raise TaskRunIdentityError("Task owner did not produce a complete accepted baseline")
    checked_task(result["task"])
    return result
