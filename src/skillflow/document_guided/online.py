"""Recorded document steps and complete-object submissions.

The active route accepts one complete CFG and one complete annotation. The
legacy batch helpers remain isolated for offline fixtures; no connections or
demands are inferred by this recording layer.
"""
from copy import deepcopy
from pathlib import Path
import os
import json
import re

from pydantic import ValidationError

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256, implementation_provenance, sha_file, now, injected_factory
from skillflow.common.runs import exclusive_run
from skillflow.common.source_evidence import _json_object
from skillflow.common.structural_correction import ResponseChain, chain_counts, StructuralCorrectionLimitReached
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.common.validation import StructuralValidationError, structural_error, schema_error
from skillflow.common.semantic_failure import SemanticFailure
from .batches import validate_batch, batch_model, combine_annotation

STEP_IDENTITY = "skillflow-document-step-v8"
ANNOTATION_IDENTITY = "skillflow-document-annotation-v8"
FRAGMENT_KINDS = {name + "_fragment": name for name in
                  ("processing", "task-correspondence", "sensitivity")}
CONFIG = {"model": "gpt-6.1-sol", "reasoning_effort": "max", "response_format": "json_object"}


def analysis_config(config=None):
    """Resolve the saved public configuration without consulting the environment."""
    if config is not None and (type(config) is not dict or set(config) - set(CONFIG)):
        raise ValueError("Document-guided configuration accepts only model, reasoning_effort, and response_format")
    resolved = {**CONFIG, **({} if config is None else config)}
    if (resolved["model"] != CONFIG["model"] or resolved["response_format"] != "json_object"
            or resolved["reasoning_effort"] not in ("max", "high")):
        raise ValueError("Document-guided configuration requires gpt-6.1-sol, JSON output, and max or high effort")
    return resolved


def _local_counts(directory, prefix):
    try:
        return chain_counts(directory, prefix)
    except Exception:
        return {"status": "unavailable"}


def _same_decision(left, right):
    return (canonical_sha256({key: value for key, value in left.items() if key != "counts"})
            == canonical_sha256({key: value for key, value in right.items() if key != "counts"}))


def read(path):
    return _json_object(checked_run_path(path).read_bytes().decode("utf-8"))


def inventory(directory):
    return {p.relative_to(directory).as_posix(): sha_file(checked_run_path(p))
            for p in sorted(Path(directory).rglob("*")) if p.is_file() and p.name != ".runner.lock"}


def seal(value):
    return {**deepcopy(value), "manifest_sha256": canonical_sha256(value)}


def checked_manifest(directory, identity, *, recompute=False):
    directory = checked_run_path(directory)
    value = read(directory / "manifest.json")
    if value.get("identity") != identity or seal({k: v for k, v in value.items() if k != "manifest_sha256"}) != value:
        raise ValueError("Document-guided run identity mismatch")
    producer = value.get("implementation", {})
    if not producer.get("files") or canonical_sha256(producer["files"]) != producer.get("sha256"):
        raise ValueError("Invalid producer identity")
    if recompute and producer != implementation_provenance():
        raise ValueError("Document-guided recomputation requires its original implementation")
    for relative, digest in value.get("files", {}).items():
        path = checked_run_path(directory / relative)
        if not path.is_relative_to(directory) or sha_file(path) != digest:
            raise ValueError("Frozen document-guided input changed: " + relative)
    return value


def file_reference(owner, path):
    path = checked_run_path(path)
    return {"path": Path(os.path.relpath(path, owner)).as_posix(), "sha256": sha_file(path)}


def resolve_file(owner, ref):
    if set(ref) != {"path", "sha256"}:
        raise ValueError("Invalid explicit artifact reference")
    path = checked_run_path(Path(owner) / ref["path"])
    if sha_file(path) != ref["sha256"]:
        raise ValueError("Referenced artifact changed: " + ref["path"])
    return path


def _step_context(directory, manifest):
    """Resolve explicit owners; never copy the full material into a step."""
    context = manifest.get("context", {})
    value = {}
    for name in ("source_owner", "task_run", "processing_step"):
        if name in context:
            value[name] = resolve_run_reference(directory, context[name])
    for name in ("cfg_path", "controlled_path"):
        if name in context:
            value[name] = resolve_file(directory, context[name])
    if "source_owner" in value:
        value["source"] = read_snapshot(value["source_owner"])[1]
        value["files"] = {"skill/" + row["path"]: row["content"] for row in value["source"]["files"]}
    if "task_run" in value:
        from skillflow.task.runner import load_task_run
        value["task"] = load_task_run(value["task_run"])["task"]
    if "cfg_path" in value:
        graph = read(value["cfg_path"])
        value["cfg"] = graph.get("cfg", graph)
    if "processing_step" in value:
        value["processing"] = load_step(value["processing_step"])
        value["validation_gaps"] = read(value["processing_step"] / "result.json").get("validation_gaps", [])
    if manifest["kind"] in {"full_annotation", "flat_annotation"}:
        from skillflow.propagation.material import prepare_material
        value["material"] = prepare_material(value["source"], value["cfg"],
            task_baseline=value["task"])
    if manifest["kind"] == "graph_audit":
        from skillflow.common.source_evidence import _checked_source
        from skillflow.graph.audit.services import _checked_document
        value["source"] = _checked_source(value["source"])
        value["controlled"] = _checked_document(read(value["controlled_path"]))
    return value


def _fragment_material(context):
    if "task" in context:
        from skillflow.propagation.material import prepare_material
        return prepare_material(context["source"], context["cfg"], task_baseline=context["task"])
    value = {key: context[key] for key in ("source", "cfg", "task") if key in context}
    return value


def _correction_strategy(kind):
    if kind == "cfg_wire_v5":
        from .fragments import fragment_correction_strategy
        return fragment_correction_strategy("cfg")
    if kind in FRAGMENT_KINDS:
        from .fragments import fragment_correction_strategy
        return fragment_correction_strategy(FRAGMENT_KINDS[kind])
    return None


def _run_candidate(chain, kind, context):
    """Keep validated independent records without accepting a failed whole answer."""
    try:
        return chain.run(), None
    except StructuralCorrectionLimitReached:
        if kind not in FRAGMENT_KINDS:
            raise
        from .fragments import salvage_fragment
        value, gaps = salvage_fragment(FRAGMENT_KINDS[kind], chain.last_candidate,
            _fragment_material(context), processing=context.get("processing"),
            validation_gaps=context.get("validation_gaps", []))
        if value is None:
            raise
        return value, gaps


def _full_graph(value, context):
    from skillflow.graph.extraction.candidate import IRAnalysisCandidate
    from skillflow.graph.extraction.compiler import compile_candidate
    from skillflow.task.material import prepare_task_material
    from skillflow.task.services import validate_task_response
    from .source import copy_script_content
    if value.get("outcome") == "cannot_assess":
        validate_task_response(value, prepare_task_material(context["source"]))
    try:
        candidate = IRAnalysisCandidate.model_validate(value).model_dump(mode="json", exclude_unset=True)
    except ValidationError as error:
        raise schema_error(error, candidate=value, schema=IRAnalysisCandidate.model_json_schema()) from error
    copies = []
    for block_index, block in enumerate(candidate["blocks"]):
        for index, instruction in enumerate(block.get("instructions", [])):
            span = instruction.get("metadata", {}).pop("_source_span", None)
            if span is not None:
                copies.append((instruction["instruction_ref"], span,
                    f"/blocks/{block_index}/instructions/{index}/metadata/_source_span"))
    for instruction, span, path in copies:
        try:
            candidate = copy_script_content(candidate, instruction, span, files=context["files"])
        except (ValueError, TypeError) as error:
            raise structural_error("source_copy", path, str(error)) from error
    result = compile_candidate(candidate)
    if not result.ok:
        raise StructuralValidationError([{"code": row.code,
            "path": "" if row.path in {"candidate", "cfg"} else "/" + "/".join(
                part.replace("~", "~0").replace("/", "~1")
                for part in re.findall(r"[^.\[\]]+", row.path)),
            "message": row.message} for row in result.diagnostics])
    return candidate


def validate_step(kind, response, *, context=None):
    if kind in FRAGMENT_KINDS:
        from .fragments import validate_fragment
        return validate_fragment(FRAGMENT_KINDS[kind], response, _fragment_material(context or {}),
                                 processing=(context or {}).get("processing"),
                                 validation_gaps=(context or {}).get("validation_gaps", []))
    if kind in {"document", "flow_document"}:
        if isinstance(response, dict) or (isinstance(response, str) and response.lstrip().startswith('{')):
            try:
                failure = _json_object(response) if isinstance(response, str) else response
            except (ValueError, TypeError):
                failure = None
            if isinstance(failure, dict) and failure.get("outcome") == "cannot_assess" and kind == "flow_document":
                raise structural_error("whole_failure_forbidden", "/outcome",
                    "Return supported flow and source-located unresolved relationships, not a whole-analysis refusal")
            if isinstance(failure, dict) and failure.get("outcome") == "cannot_assess" and context and "source" in context:
                from skillflow.task.material import prepare_task_material
                from skillflow.task.services import validate_task_response
                validate_task_response(failure, prepare_task_material(context["source"]))
        if not isinstance(response, str) or not response.strip():
            raise structural_error("document", "", "Return a nonempty Markdown working document")
        return response
    try:
        value = _json_object(response)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error
    context = context or {}
    if kind in {"cfg_wire", "cfg_wire_v5"}:
        if kind == "cfg_wire_v5" and value.get("outcome") == "cannot_assess":
            raise structural_error("whole_failure_forbidden", "/outcome",
                "Preserve supported CFG relationships and explicit diagnostics; no whole-analysis refusal")
        if value.get("outcome") == "cannot_assess":
            return _full_graph(value, context)
        from .cfg_wire import CFGWire, normalize_cfg_wire
        try:
            canonical = normalize_cfg_wire(value)
        except ValidationError as error:
            raise schema_error(error, candidate=value, schema=CFGWire.model_json_schema()) from error
        return _full_graph(canonical, context)
    if kind == "full_graph":
        return _full_graph(value, context)
    if kind == "full_annotation":
        from skillflow.propagation.annotation.services import compile_response
        return compile_response(value, context["material"])[0]
    if kind == "flat_annotation":
        from .annotation_wire import compile_flat_response
        return compile_flat_response(value, context["material"])[0]
    if kind == "graph_audit":
        from skillflow.graph.audit.services import validate_audit
        from skillflow.graph.audit.models import AuditResult, CannotAssessAudit
        from skillflow.common.source_evidence import ResponseValidationError
        model = CannotAssessAudit if value.get("outcome") == "cannot_assess" else AuditResult
        try:
            return validate_audit(value, context["source"], context["controlled"])
        except ValidationError as error:
            raise schema_error(error, candidate=value, schema=model.model_json_schema()) from error
        except ResponseValidationError as error:
            raise structural_error("audit_reference", "", str(error)) from error
    try:
        return validate_batch(kind, value)
    except ValidationError as error:
        raise schema_error(error, candidate=value, schema=batch_model(kind).model_json_schema()) from error
    except ValueError as error:
        # validate_batch's remaining value checks are explicit candidate rules.
        raise structural_error("batch", "", str(error)) from error


def prepare_step(directory, prompt, *, kind, dependencies=(), context=None, max_corrections=None, config=None):
    directory, writer = checked_run_path(directory), ArtifactWriter(())
    config = analysis_config(config)
    context = context or {}
    allowed = {"source_owner", "cfg_path", "task_run", "controlled_path", "processing_step"}
    if set(context) - allowed:
        raise ValueError("Unknown document-step context")
    required = {"full_graph": {"source_owner"}, "cfg_wire": {"source_owner"},
        "full_annotation": {"source_owner", "cfg_path", "task_run"},
        "flat_annotation": {"source_owner", "cfg_path", "task_run"},
        "graph_audit": {"source_owner", "controlled_path"},
        "cfg_wire_v5": {"source_owner"},
        "processing_fragment": {"source_owner", "cfg_path"},
        "task-correspondence_fragment": {"source_owner", "cfg_path", "task_run", "processing_step"},
        "sensitivity_fragment": {"source_owner", "cfg_path", "processing_step"}}.get(kind, set())
    if not required <= set(context):
        raise ValueError("Missing document-step context: " + ", ".join(sorted(required-set(context))))
    refs = {}
    if kind in {"processing_fragment", "sensitivity_fragment"} and "task_run" in context:
        raise ValueError("Processing and sensitivity steps must not receive the Task")
    for name in ("source_owner", "task_run", "processing_step"):
        if name in context:
            refs[name] = make_run_reference(directory, context[name])
    for name in ("cfg_path", "controlled_path"):
        if name in context:
            refs[name] = file_reference(directory, context[name])
    directory.mkdir(parents=True, exist_ok=True)
    existing = {path.name for path in directory.iterdir()}
    if existing:
        if existing != {"prompt.txt"} or (directory / "prompt.txt").read_bytes() != prompt.encode("utf-8"):
            raise ValueError("Step preparation requires an empty directory or the identical prompt-only interruption")
    else:
        (directory / "prompt.txt").write_bytes(prompt.encode("utf-8"))
    manifest = seal({"identity": STEP_IDENTITY, "created_at": now(), "kind": kind,
        "max_corrections": max_corrections,
        "config": config, "implementation": implementation_provenance(),
        "context": refs,
        "dependencies": [file_reference(directory, path) for path in dependencies],
        "files": {"prompt.txt": sha_file(directory / "prompt.txt")}})
    writer.json(directory / "manifest.json", manifest)
    return manifest


def run_step(directory, *, client=None, replay=False, stop_event=None, config=None):
    directory, writer = checked_run_path(directory), ArtifactWriter(())
    if replay and client is not None:
        raise ValueError("Replay cannot accept a live client")
    with exclusive_run(directory):
        manifest = checked_manifest(directory, STEP_IDENTITY, recompute=True)
        saved_config = analysis_config(manifest["config"])
        if manifest["config"] != saved_config or (config is not None and analysis_config(config) != saved_config):
            raise ValueError("Document step configuration differs")
        context = _step_context(directory, manifest)
        for dep in manifest["dependencies"]:
            resolve_file(directory, dep)
        chain = ResponseChain(directory, prefix="calls", base_prompt=(directory / "prompt.txt").read_bytes().decode(),
            request_kind="document_guided_" + manifest["kind"], config=saved_config, writer=writer,
            validate=lambda raw: validate_step(manifest["kind"], raw, context=context),
            client_factory=None if client is None else injected_factory(client), replay=replay,
            max_corrections=manifest.get("max_corrections"), stop_event=stop_event,
            correction_strategy=_correction_strategy(manifest["kind"]),
            interruption=(read(directory / "result.json").get("interruption")
                          if replay and (directory / "result.json").exists() else None))
        try:
            value, salvage = _run_candidate(chain, manifest["kind"], context)
        except SemanticFailure as error:
            result = {"identity": STEP_IDENTITY, "status": "semantic_failure", "failure": error.failure,
                "response_chain_sha256": canonical_sha256(chain.snapshot()), "counts": _local_counts(directory, "calls")}
            if replay:
                if not _same_decision(read(directory / "result.json"), result):
                    raise ValueError("Replayed semantic failure differs")
            else:
                writer.json(directory / "result.json", result)
            raise
        except StructuralCorrectionLimitReached as error:
            result = {"identity": STEP_IDENTITY, "status": "structural_failure", "reason": str(error),
                "response_chain_sha256": canonical_sha256(chain.snapshot()), "counts": _local_counts(directory, "calls")}
            if replay:
                if not _same_decision(read(directory / "result.json"), result):
                    raise ValueError("Replayed structural failure differs")
            else:
                writer.json(directory / "result.json", result)
            raise
        except KeyboardInterrupt:
            result = {"identity": STEP_IDENTITY, "status": "interrupted", "interruption": chain.cursor,
                "response_chain_sha256": canonical_sha256(chain.snapshot()), "counts": _local_counts(directory, "calls")}
            if replay:
                if not _same_decision(read(directory / "result.json"), result):
                    raise ValueError("Replayed stage interruption differs")
            else:
                writer.json(directory / "result.json", result)
            raise
        encoded = value.encode("utf-8") if isinstance(value, str) else None
        name = "document.md" if encoded is not None else "value.json"
        if replay:
            saved = (directory / name).read_bytes().decode() if encoded is not None else read(directory / name)
            if saved != value:
                raise ValueError("Replayed document or batch differs")
        else:
            if encoded is not None:
                (directory / name).write_bytes(encoded)
            else:
                writer.json(directory / name, value)
        result = {"identity": STEP_IDENTITY, "accepted_call": chain.accepted_call,
            "value_file": name, "value_sha256": sha_file(directory / name),
            "response_chain_sha256": canonical_sha256(chain.snapshot()), "counts": _local_counts(directory, "calls")}
        if salvage is not None:
            result.update(status="partial", validation_gaps=salvage,
                          reason="Only independently validated records are available after the single correction")
        if replay:
            if not _same_decision(read(directory / "result.json"), result):
                raise ValueError("Replayed step selection or counts differ")
        else:
            writer.json(directory / "result.json", result)
        return value


def _saved_step_value(directory, manifest):
    """Read an already validated value without replaying semantic corrections.

    Bytes and terminal selection remain checked. Explicit recomputation below
    is responsible for reconstructing normalization, record replacement and
    semantic validation from the archived answers.
    """
    result = read(directory / "result.json")
    chain = read(directory / "calls/chain.json")
    expected_name = "document.md" if manifest["kind"] in {"document", "flow_document"} else "value.json"
    if (result.get("identity") != STEP_IDENTITY or result.get("value_file") != expected_name
            or result.get("value_sha256") != sha_file(directory / expected_name)
            or result.get("response_chain_sha256") != canonical_sha256(chain)
            or result.get("accepted_call") != chain.get("accepted_call")
            or chain.get("prefix") != "calls"
            or chain.get("request_kind") != "document_guided_" + manifest["kind"]):
        raise ValueError("Accepted document step differs from its request chain")
    attempts = chain.get("attempts", [])
    partial = result.get("status") == "partial"
    if (not attempts or (partial and (chain.get("accepted_call") is not None
            or attempts[-1].get("status") != "structural_invalid"
            or not isinstance(result.get("validation_gaps"), list)))
            or (not partial and (attempts[-1].get("status") != "valid"
                or attempts[-1].get("call") != chain.get("accepted_call")
                or "validation_gaps" in result))):
        raise ValueError("Saved validation coverage differs from its recorded terminal decision")
    for number, row in enumerate(attempts, 1):
        if row.get("call") != f"calls/a{number:03d}":
            raise ValueError("Saved request sequence differs")
        owner = directory / row["call"]
        for name, key in (("request.json", "request_sha256"), ("call.json", "call_sha256"),
                          ("validation.json", "validation_sha256")):
            digest = sha_file(owner / name) if name == "call.json" else canonical_sha256(read(owner / name))
            if digest != row.get(key):
                raise ValueError("Saved request artifact changed: " + row["call"] + "/" + name)
        call = read(owner / "call.json")
        if (call.get("status") != "complete"
                or canonical_sha256(call.get("response")) != call.get("response_sha256")
                or canonical_sha256(json.loads((owner / "response.json").read_bytes().decode("utf-8"))) != call.get("response_sha256")
                or canonical_sha256((owner / "prompt.txt").read_bytes().decode("utf-8")) != call.get("prompt_sha256")):
            raise ValueError("Saved request response or prompt changed: " + row["call"])
    return ((directory / expected_name).read_bytes().decode("utf-8")
            if expected_name == "document.md" else read(directory / expected_name))


def load_step(directory, *, recompute=False):
    directory = checked_run_path(directory)
    manifest = checked_manifest(directory, STEP_IDENTITY, recompute=recompute)
    config = analysis_config(manifest["config"])
    if manifest["config"] != config:
        raise ValueError("Document step configuration differs")
    context = _step_context(directory, manifest)
    for dep in manifest["dependencies"]:
        resolve_file(directory, dep)
    if not recompute:
        return _saved_step_value(directory, manifest)
    chain = ResponseChain(directory, prefix="calls", base_prompt=(directory / "prompt.txt").read_bytes().decode(),
        request_kind="document_guided_" + manifest["kind"], config=config, writer=ArtifactWriter(()),
        validate=lambda raw: validate_step(manifest["kind"], raw, context=context), replay=True, read_only=True,
        max_corrections=manifest.get("max_corrections"),
        correction_strategy=_correction_strategy(manifest["kind"]))
    value, salvage = _run_candidate(chain, manifest["kind"], context)
    result = read(directory / "result.json")
    if (result["value_sha256"] != sha_file(directory / result["value_file"])
            or result["accepted_call"] != chain.accepted_call
            or result["response_chain_sha256"] != canonical_sha256(chain.snapshot())):
        raise ValueError("Accepted document step differs from its request chain")
    saved = ((directory / result["value_file"]).read_bytes().decode() if manifest["kind"] in {"document", "flow_document"}
             else read(directory / result["value_file"]))
    if saved != value:
        raise ValueError("Saved batch differs from its actual response")
    if (result.get("validation_gaps") != salvage
            or (result.get("status") == "partial") != (salvage is not None)):
        raise ValueError("Saved validation coverage differs from its actual failed response")
    return value


def source_parts(directory):
    """Resolve separately owned source and CFG without duplicating their contents."""
    directory = checked_run_path(directory)
    refs = read(directory / "inputs/references.json")
    source_owner = resolve_run_reference(directory, refs["source_owner"])
    _, source, _ = read_snapshot(source_owner)
    cfg = read(resolve_file(directory, refs["cfg"]))
    return {"source": source, "cfg": cfg.get("cfg", cfg),
        "runtime_contract": read(directory / "inputs/runtime-contract.json")}


def save_annotation(directory, *, source_owner, cfg_path, task_run, location_step, ir_steps, global_step):
    from skillflow.task.runner import load_task_run
    from skillflow.propagation.material import prepare_material
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    directory, writer = checked_run_path(directory), ArtifactWriter(())
    _, source, _ = read_snapshot(source_owner)
    cfg = read(cfg_path)
    task = load_task_run(task_run)["task"]
    material = prepare_material(source, cfg.get("cfg", cfg), task_baseline=task)
    batches = [location_step, *ir_steps, global_step]
    values = [load_step(step) for step in batches]
    raw, compiled, mapping = combine_annotation(values[0], values[1:-1], values[-1], material=material)
    directory.mkdir(parents=True, exist_ok=False)
    writer.json(directory / "inputs/references.json", {
        "source_owner": make_run_reference(directory, source_owner), "cfg": file_reference(directory, cfg_path),
        "batch_steps": [make_run_reference(directory, step) for step in batches]})
    writer.json(directory / "inputs/runtime-contract.json", runtime_contract())
    for name, value in (("raw-annotation.json", raw), ("compiled-response.json", compiled), ("compilation-map.json", mapping)):
        writer.json(directory / "audit" / name, value)
    manifest = seal({"identity": ANNOTATION_IDENTITY, "schema_version": 1,
        "created_at": now(), "preparation_status": "ready", "config": CONFIG,
        "upstream": None, "task_run_ref": make_run_reference(directory, task_run),
        "task_origin": "independent_extraction", "candidate_origin": "explicit_model_batch_composition",
        "implementation": implementation_provenance(), "material_sha256": canonical_sha256(material),
        "files": {"inputs/" + name: digest for name, digest in inventory(directory / "inputs").items()},
        "artifacts": {"audit/" + name: digest for name, digest in inventory(directory / "audit").items()}})
    writer.json(directory / "manifest.json", manifest)
    return load_annotation(directory)


def save_whole_annotation(directory, *, step, source_owner, cfg_path, task_run):
    """Publish the actual single accepted response for existing downstream stages."""
    from skillflow.task.runner import load_task_run
    from skillflow.propagation.material import prepare_material
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    from skillflow.propagation.annotation.services import compile_response
    directory, step = checked_run_path(directory), checked_run_path(step)
    writer = ArtifactWriter(())
    stage = checked_manifest(step, STEP_IDENTITY)
    config = analysis_config(stage["config"])
    if stage["kind"] not in {"full_annotation", "flat_annotation"}:
        raise ValueError("A complete annotation step is required")
    context = _step_context(step, stage)
    _, source, _ = read_snapshot(source_owner)
    cfg = read(cfg_path)
    task = load_task_run(task_run)["task"]
    material = prepare_material(source, cfg.get("cfg", cfg), task_baseline=task)
    if canonical_sha256(context["material"]) != canonical_sha256(material):
        raise ValueError("Accepted annotation belongs to different frozen material")
    wire = None
    if stage["kind"] == "flat_annotation":
        from .annotation_wire import compile_flat_response
        wire, raw, compiled, mapping = compile_flat_response(load_step(step), material)
    else:
        raw, compiled, mapping = compile_response(load_step(step), material)
    if (directory / "manifest.json").exists():
        saved = load_annotation(directory)
        refs = read(directory / "inputs/references.json")
        if (saved["raw_annotation"] != raw or
                resolve_run_reference(directory, refs.get("annotation_step", {})) != step):
            raise ValueError("Existing annotation publication differs")
        return saved
    directory.mkdir(parents=True, exist_ok=True)
    # An interrupted publication is recoverable only if each existing output
    # matches the same accepted response; never overwrite unrelated material.
    outputs = {
        "inputs/references.json": {"source_owner": make_run_reference(directory, source_owner),
            "cfg": file_reference(directory, cfg_path),
            "annotation_step": make_run_reference(directory, step)},
        "inputs/runtime-contract.json": runtime_contract(),
        "audit/raw-annotation.json": raw, "audit/compiled-response.json": compiled,
        "audit/compilation-map.json": mapping,
    }
    if wire is not None:
        outputs["audit/wire-annotation.json"] = wire
    existing = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if existing - set(outputs):
        raise ValueError("Unknown files in annotation publication")
    for name, value in outputs.items():
        path = directory / name
        if path.exists() and canonical_sha256(read(path)) != canonical_sha256(value):
            raise ValueError("Interrupted annotation publication differs: " + name)
        writer.json(path, value)
    manifest = seal({"identity": ANNOTATION_IDENTITY, "schema_version": 3 if wire is not None else 2,
        "created_at": now(), "preparation_status": "ready", "config": config,
        "upstream": None, "task_run_ref": make_run_reference(directory, task_run),
        "task_origin": "independent_extraction", "candidate_origin": (
            "single_complete_flat_response" if wire is not None else "single_complete_model_response"),
        "implementation": implementation_provenance(), "material_sha256": canonical_sha256(material),
        "files": {"inputs/" + name: digest for name, digest in inventory(directory / "inputs").items()},
        "artifacts": {"audit/" + name: digest for name, digest in inventory(directory / "audit").items()}})
    writer.json(directory / "manifest.json", manifest)
    return load_annotation(directory)


def _assembled_values(steps, material, *, recompute=False):
    from .fragments import assemble_fragments
    values = {name: load_step(owner, recompute=recompute) for name, owner in steps.items()}
    gaps = [gap for owner in steps.values()
            for gap in read(owner / "result.json").get("validation_gaps", [])]
    return assemble_fragments(values["processing"], values["task-correspondence"],
                              values["sensitivity"], material, validation_gaps=gaps)


def save_assembled_annotation(directory, *, source_owner, cfg_path, task_run, fragment_steps):
    """Publish a deterministic composition of three independently saved fragments."""
    from skillflow.task.runner import load_task_run
    from skillflow.propagation.material import prepare_material
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    directory, writer = checked_run_path(directory), ArtifactWriter(())
    expected = {"processing", "task-correspondence", "sensitivity"}
    if set(fragment_steps) != expected:
        raise ValueError("Assembly requires exactly the three semantic owners")
    steps = {key: checked_run_path(owner) for key, owner in fragment_steps.items()}
    configs = [checked_manifest(owner, STEP_IDENTITY)["config"] for owner in steps.values()]
    if any(config != configs[0] for config in configs):
        raise ValueError("Fragment configurations differ")
    _, source, _ = read_snapshot(source_owner)
    graph = read(cfg_path)
    task = load_task_run(task_run)["task"]
    material = prepare_material(source, graph.get("cfg", graph), task_baseline=task)
    # Validate each recorded context against the same CFG/source/processing epoch.
    for name, owner in steps.items():
        manifest = checked_manifest(owner, STEP_IDENTITY)
        context = _step_context(owner, manifest)
        if (manifest["kind"] != name + "_fragment"
                or canonical_sha256(context["cfg"]) != canonical_sha256(material["cfg"])
                or canonical_sha256(context["source"]) != canonical_sha256(source)):
            raise ValueError("A fragment belongs to different source or CFG")
        if name != "processing" and context["processing_step"] != steps["processing"]:
            raise ValueError("A fragment consumes another processing version")
        if name == "task-correspondence" and context["task_run"] != checked_run_path(task_run):
            raise ValueError("Task correspondence belongs to another sealed Task")
    wire, raw, compiled, mapping = _assembled_values(steps, material)
    outputs = {
        "inputs/references.json": {"source_owner": make_run_reference(directory, source_owner),
            "cfg": file_reference(directory, cfg_path),
            "fragment_steps": {key: make_run_reference(directory, owner) for key, owner in steps.items()}},
        "inputs/runtime-contract.json": runtime_contract(),
        "audit/wire-annotation.json": wire, "audit/raw-annotation.json": raw,
        "audit/compiled-response.json": compiled, "audit/compilation-map.json": mapping,
    }
    if (directory / "manifest.json").exists():
        saved = load_annotation(directory)
        if saved["wire_annotation"] != wire or read(directory / "inputs/references.json") != outputs["inputs/references.json"]:
            raise ValueError("Existing program assembly differs")
        return saved
    directory.mkdir(parents=True, exist_ok=True)
    existing = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    if existing - set(outputs):
        raise ValueError("Unknown files in program assembly")
    for name, value in outputs.items():
        path = directory / name
        if path.exists() and canonical_sha256(read(path)) != canonical_sha256(value):
            raise ValueError("Interrupted program assembly differs: " + name)
        writer.json(path, value)
    manifest = seal({"identity": ANNOTATION_IDENTITY, "schema_version": 4,
        "created_at": now(), "preparation_status": "ready", "config": configs[0],
        "upstream": None, "task_run_ref": make_run_reference(directory, task_run),
        "task_origin": "independent_extraction", "candidate_origin": "program_assembled_fragments",
        "implementation": implementation_provenance(), "material_sha256": canonical_sha256(material),
        "files": {"inputs/" + name: digest for name, digest in inventory(directory / "inputs").items()},
        "artifacts": {"audit/" + name: digest for name, digest in inventory(directory / "audit").items()}})
    writer.json(directory / "manifest.json", manifest)
    return load_annotation(directory)


def _check_annotation_steps(directory, manifest, refs):
    """Check bound step bytes/dependencies; do not reconstruct their semantics."""
    origin = manifest["candidate_origin"]
    if origin in {"single_complete_model_response", "single_complete_flat_response"}:
        key, references = "annotation_step", [refs["annotation_step"]]
    elif origin == "program_assembled_fragments":
        if set(refs["fragment_steps"]) != {"processing", "task-correspondence", "sensitivity"}:
            raise ValueError("Assembly requires exactly the three semantic owners")
        key, references = "fragment_steps", refs["fragment_steps"].values()
    elif origin == "explicit_model_batch_composition":
        key, references = "batch_steps", refs["batch_steps"]
    else:
        raise ValueError("Unknown annotation candidate origin")
    for ref in references:
        load_step(resolve_run_reference(directory, ref))
    return {key: refs[key]}


def check_annotation_unchanged(directory, manifest):
    """Check persisted bindings before commit without loading compiled payloads."""
    from skillflow.propagation.annotation.inputs import load_prepared_material
    directory = checked_run_path(directory)
    if checked_manifest(directory, ANNOTATION_IDENTITY) != manifest:
        raise ValueError("Annotation input changed during calculation")
    if {"inputs/" + k: v for k, v in inventory(directory / "inputs").items()} != manifest["files"]:
        raise ValueError("Unexpected composition input")
    if {"audit/" + k: v for k, v in inventory(directory / "audit").items()} != manifest["artifacts"]:
        raise ValueError("Composition output changed")
    load_prepared_material(directory)
    _check_annotation_steps(directory, manifest, read(directory / "inputs/references.json"))


def load_annotation(directory, *, recompute=False):
    from skillflow.propagation.annotation.inputs import load_prepared_material
    directory = checked_run_path(directory)
    manifest = checked_manifest(directory, ANNOTATION_IDENTITY, recompute=recompute)
    if {"inputs/" + k: v for k, v in inventory(directory / "inputs").items()} != manifest["files"]:
        raise ValueError("Unexpected composition input")
    if {"audit/" + k: v for k, v in inventory(directory / "audit").items()} != manifest["artifacts"]:
        raise ValueError("Composition output changed")
    material = load_prepared_material(directory)
    refs = read(directory / "inputs/references.json")
    wire = None
    if not recompute:
        provenance = _check_annotation_steps(directory, manifest, refs)
        raw = read(directory / "audit/raw-annotation.json")
        compiled = read(directory / "audit/compiled-response.json")
        mapping = read(directory / "audit/compilation-map.json")
        if (directory / "audit/wire-annotation.json").is_file():
            wire = read(directory / "audit/wire-annotation.json")
    elif manifest["candidate_origin"] in {"single_complete_model_response", "single_complete_flat_response"}:
        from skillflow.propagation.annotation.services import compile_response
        step = resolve_run_reference(directory, refs["annotation_step"])
        step_manifest = checked_manifest(step, STEP_IDENTITY)
        context = _step_context(step, step_manifest)
        if (step_manifest["kind"] not in {"full_annotation", "flat_annotation"} or
                canonical_sha256(context["material"]) != canonical_sha256(material)):
            raise ValueError("Annotation step no longer matches the published material")
        if manifest["candidate_origin"] == "single_complete_flat_response":
            from .annotation_wire import compile_flat_response
            wire, raw, compiled, mapping = compile_flat_response(load_step(step, recompute=True), material)
            if canonical_sha256(read(directory / "audit/wire-annotation.json")) != canonical_sha256(wire):
                raise ValueError("Saved flat response differs from its genuine response chain")
        else:
            raw, compiled, mapping = compile_response(load_step(step, recompute=True), material)
        provenance = {"annotation_step": refs["annotation_step"]}
    elif manifest["candidate_origin"] == "program_assembled_fragments":
        steps = {name: resolve_run_reference(directory, ref) for name, ref in refs["fragment_steps"].items()}
        wire, raw, compiled, mapping = _assembled_values(steps, material, recompute=True)
        if canonical_sha256(read(directory / "audit/wire-annotation.json")) != canonical_sha256(wire):
            raise ValueError("Program assembly differs from its genuine fragment responses")
        provenance = {"fragment_steps": refs["fragment_steps"]}
    elif manifest["candidate_origin"] == "explicit_model_batch_composition":
        values = [load_step(resolve_run_reference(directory, ref), recompute=True) for ref in refs["batch_steps"]]
        raw, compiled, mapping = combine_annotation(values[0], values[1:-1], values[-1], material=material)
        provenance = {"batch_steps": refs["batch_steps"]}
    else:
        raise ValueError("Unknown annotation candidate origin")
    if recompute:
        for name, value in (("raw-annotation.json", raw), ("compiled-response.json", compiled), ("compilation-map.json", mapping)):
            if canonical_sha256(read(directory / "audit" / name)) != canonical_sha256(value):
                raise ValueError("Saved annotation differs from its accepted model response")
    _, _, metadata = read_snapshot(resolve_run_reference(directory, refs["source_owner"]))
    identity = {"identity": ANNOTATION_IDENTITY, "manifest_sha256": manifest["manifest_sha256"],
        "accepted_response_sha256": canonical_sha256(wire if wire is not None else raw), "candidate_origin": manifest["candidate_origin"],
        "implementation": manifest["implementation"], **provenance}
    return {"manifest": manifest, "material": material, "raw_annotation": raw,
        "wire_annotation": wire,
        "compiled_annotation": compiled, "mapping": mapping, "task": material["task"],
        "source_metadata": metadata, "upstream_identity": identity,
        "result": {"status": "complete", "candidate_origin": manifest["candidate_origin"]}}
