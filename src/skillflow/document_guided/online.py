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

STEP_IDENTITY = "skillflow-document-step-v20"
PREVIOUS_STEP_IDENTITY = "skillflow-document-step-v19"
READABLE_STEP_IDENTITIES = {STEP_IDENTITY, PREVIOUS_STEP_IDENTITY, "skillflow-document-step-v18"}
ANNOTATION_IDENTITY = "skillflow-document-annotation-v14"
ARCHIVED_ANNOTATION_IDENTITY = "skillflow-document-annotation-v11"
READABLE_ANNOTATION_IDENTITIES = frozenset({ANNOTATION_IDENTITY, "skillflow-document-annotation-v13",
                                          "skillflow-document-annotation-v12", ARCHIVED_ANNOTATION_IDENTITY})
FRAGMENT_KINDS = {name + "_fragment": name for name in
                  ("processing", "task-correspondence", "sensitivity")}
_SCOPED = ("processing_revision", "sensitivity_revision", "correspondence_revision")
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


def processing_revision_evidence(owner):
    """Recover rejected rows from the bound terminal attempt, never as executable input."""
    result = read(owner / "result.json")
    gaps = result.get("validation_gaps", [])
    if not gaps:
        return [], {}
    from skillflow.common.json_normalization import normalize_response
    from skillflow.common.recording import read_json
    from .fragment_wire import expand_processing_response
    chain = read(owner / "calls/chain.json")
    if (result.get("response_chain_sha256") != canonical_sha256(chain) or not chain["attempts"]
            or result.get("status") != "partial" or result.get("accepted_call") is not None):
        raise ValueError("Rejected processing records require a bound partial processing decision")
    attempt = chain["attempts"][-1]
    if attempt["status"] != "structural_invalid" or attempt["call"] != f"calls/a{len(chain['attempts']):03d}":
        raise ValueError("Rejected processing attempt does not match the terminal validation")
    folder = owner / attempt["call"]
    validation = read(folder / "validation.json")
    response = read_json(folder / "response.json")
    if (canonical_sha256(validation) != attempt["validation_sha256"]
            or canonical_sha256(response) != validation["response_sha256"]):
        raise ValueError("Rejected processing response or diagnostics differ from the terminal chain")
    merged = folder / "merged-candidate.json"
    candidate = read_json(merged) if merged.is_file() else normalize_response(response)[0]
    if canonical_sha256(candidate) != validation["candidate_sha256"]:
        raise ValueError("Rejected processing candidate differs from its terminal validation")
    records = expand_processing_response(candidate).get("ir_semantics", {})
    ids = {gap["instruction_id"] for gap in gaps}
    return gaps, {ir: record for ir, record in records.items() if ir in ids}


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


def scoped_dependencies(run, kind):
    graph, review = run / "graph/initial.json", run / "review/result.json"
    step = run / "steps" / kind / "result.json"
    prefix = [step] + ([run / "steps/processing/result.json"]
                      if kind in {"sensitivity", "task-correspondence"} else [])
    return [*prefix, graph, review, run / "revision" / (kind + "-scope.json")]


def _step_context(directory, manifest):
    """Resolve explicit owners; never copy the full material into a step."""
    context = manifest.get("context", {})
    value = {}
    if manifest.get("kind") in {"graph_facts_v1", "graph_updates_v1"}:
        value["normalize_blocks"] = manifest.get("identity") in {PREVIOUS_STEP_IDENTITY, STEP_IDENTITY}
        value["check_occurrences"] = manifest.get("identity") == STEP_IDENTITY
    if manifest.get("kind") in {"graph_facts_v1", "graph_updates_v1"} and manifest.get("identity") in {
            "skillflow-document-step-v15", "skillflow-document-step-v16", "skillflow-document-step-v17"}:
        value["archived_graph"] = True
    for name in ("source_owner", "task_run", "processing_step"):
        if name in context:
            value[name] = resolve_run_reference(directory, context[name])
    for name in ("cfg_path", "controlled_path", "graph_repair_path", "processing_scope_path",
                 "sensitivity_scope_path", "task-correspondence_scope_path"):
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
    if "graph_repair_path" in value:
        from .graph_steps import load_revision_input
        value["graph_repair"] = load_revision_input(directory, value["graph_repair_path"], value["files"],
            [resolve_file(directory, ref) for ref in manifest["dependencies"]], archived=value.get("archived_graph", False),
            normalize_blocks=value["normalize_blocks"], check_occurrences=value["check_occurrences"])
    if "processing_scope_path" in value:
        from .fragment_revision import processing_scope
        run = directory.parent.parent
        old_step = run / "steps/processing"
        expected_paths = scoped_dependencies(run, "processing")
        _, old_graph, review, path = expected_paths
        if (directory.name != "revision-processing" or value["processing_scope_path"] != path
                or [resolve_file(directory, ref) for ref in manifest["dependencies"][-4:]]
                   != expected_paths):
            raise ValueError("Scoped processing does not bind its original record owners")
        previous = load_step(old_step)
        findings = (read(review).get("review") or {}).get("findings", [])
        gaps, rejected = processing_revision_evidence(old_step)
        expected = processing_scope(read(old_graph)["cfg"], value["cfg"], findings, previous,
            validation_gaps=gaps, rejected_records=rejected, current_joins=manifest["identity"] == STEP_IDENTITY)
        if expected is None or expected != read(path):
            raise ValueError("Processing revision scope differs from its bound dependency proof")
        value["processing_revision"] = {"scope": expected, "previous": previous}
        value["validation_gaps"] = expected["retained_validation_gaps"]
    if "processing_step" in value:
        value["processing"] = load_step(value["processing_step"])
        value["validation_gaps"] = read(value["processing_step"] / "result.json").get("validation_gaps", [])
    if "sensitivity_scope_path" in value:
        from .fragment_revision import sensitivity_scope
        run = directory.parent.parent
        old_step, old_processing = run / "steps/sensitivity", run / "steps/processing"
        expected_paths = scoped_dependencies(run, "sensitivity")
        _, _, old_graph, review, path = expected_paths
        if (directory.name != "revision-sensitivity" or value["sensitivity_scope_path"] != path
                or [resolve_file(directory, ref) for ref in manifest["dependencies"][-5:]]
                   != expected_paths):
            raise ValueError("Scoped sensitivity does not bind its original record owners")
        previous = load_step(old_step)
        findings = (read(review).get("review") or {}).get("findings", [])
        expected = sensitivity_scope(read(old_graph)["cfg"], value["cfg"], load_step(old_processing),
                                     value["processing"], findings, previous)
        if expected != read(path):
            raise ValueError("Sensitivity revision scope differs from its bound dependency proof")
        value["sensitivity_revision"] = {"scope": expected, "previous": previous}
    if "task-correspondence_scope_path" in value:
        from .fragment_revision import correspondence_scope
        run = directory.parent.parent
        old_step = run / "steps/task-correspondence"
        expected_paths = scoped_dependencies(run, "task-correspondence")
        _, _, old_graph, review, path = expected_paths
        if (directory.name != "revision-task-correspondence" or value["task-correspondence_scope_path"] != path
                or [resolve_file(directory, ref) for ref in manifest["dependencies"][-5:]] != expected_paths):
            raise ValueError("Scoped Task correspondence does not bind its original record owners")
        previous = load_step(old_step)
        old_context = _step_context(old_step, checked_manifest(old_step, manifest["identity"]))
        findings = (read(review).get("review") or {}).get("findings", [])
        expected = correspondence_scope(read(old_graph)["cfg"], value["cfg"], old_context["processing"],
            value["processing"], old_context["task"], value["task"], findings, previous,
            old_validation_gaps=old_context["validation_gaps"], new_validation_gaps=value["validation_gaps"])
        if expected is None or expected != read(path):
            raise ValueError("Task correspondence revision scope differs from its bound dependency proof")
        value["correspondence_revision"] = {"scope": expected, "previous": previous}
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


def _correction_strategy(kind, context=None):
    from .graph_steps import FACTS, GraphFactsCorrection
    if kind == FACTS:
        return GraphFactsCorrection(context["files"], archived=context.get("archived_graph", False),
                                    normalize_blocks=context.get("normalize_blocks", True),
                                    check_occurrences=context.get("check_occurrences", True))
    if kind == "cfg_wire_v5":
        from .fragments import fragment_correction_strategy
        return fragment_correction_strategy("cfg")
    if kind in FRAGMENT_KINDS:
        if any((context or {}).get(key) for key in _SCOPED):
            return None
        from .fragments import fragment_correction_strategy
        return fragment_correction_strategy(FRAGMENT_KINDS[kind])
    return None


def _bind_strategy(kind, context):
    from .graph_steps import FACTS
    strategy = _correction_strategy(kind, context)
    if kind == FACTS:
        context["graph_facts_strategy"] = strategy
    return strategy


def _run_candidate(chain, kind, context):
    """Keep validated independent records without accepting a failed whole answer."""
    try:
        value = chain.run()
        return value, (context.get("validation_gaps") or None) if context.get("processing_revision") else None
    except StructuralCorrectionLimitReached:
        if kind not in FRAGMENT_KINDS or any(context.get(key) for key in _SCOPED):
            raise
        from .fragments import salvage_fragment
        raw, entry_gaps = chain.last_candidate, []
        if kind == "sensitivity_fragment":
            from .sensitivity_entries import retain_valid_entries
            raw, entry_gaps = retain_valid_entries(raw, context["cfg"], context["processing"], context["files"])
            if raw is None:
                raise
        value, gaps = salvage_fragment(FRAGMENT_KINDS[kind], raw,
            _fragment_material(context), processing=context.get("processing"),
            validation_gaps=context.get("validation_gaps", []))
        if value is None and kind == "sensitivity_fragment" and entry_gaps and raw == {"declarations": []}:
            # Every submitted record had a verified, localized rejection.
            # Preserve explicit partial coverage without declaring any seed.
            value = raw
        if value is None:
            raise
        return value, [*entry_gaps, *gaps]


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
            "message": row.message,
            **({"context": deepcopy(row.context)} if getattr(row, "context", None) else {})}
            for row in result.diagnostics])
    return candidate


def validate_step(kind, response, *, context=None):
    if kind in FRAGMENT_KINDS:
        from .fragments import validate_fragment
        revision = (context or {}).get("processing_revision")
        if revision:
            from .fragment_revision import merge_processing_revision
            response = merge_processing_revision(revision["previous"], revision["scope"], response, files=context.get("files"))
        revision = (context or {}).get("sensitivity_revision")
        if revision:
            from .fragment_revision import merge_sensitivity_revision
            response = merge_sensitivity_revision(revision["previous"], revision["scope"], response, files=context["files"])
        elif kind == "sensitivity_fragment":
            from .sensitivity_entries import entry_catalogue, resolve_labels
            from skillflow.propagation.contracts.references import cfg_instructions
            catalogue = entry_catalogue(context["cfg"], context["processing"])
            response = resolve_labels(response, catalogue, cfg_instructions(context["cfg"]), context["files"])
        revision = (context or {}).get("correspondence_revision")
        if revision:
            from .fragment_revision import merge_correspondence_revision
            response = merge_correspondence_revision(revision["previous"], revision["scope"], response)
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
    from .graph_steps import FACTS, UPDATES, validate_graph
    if kind in {FACTS, UPDATES}:
        return validate_graph(kind, value, context)
    if kind in {"cfg_wire", "cfg_wire_v5"}:
        if kind == "cfg_wire_v5" and value.get("outcome") == "cannot_assess":
            raise structural_error("whole_failure_forbidden", "/outcome",
                "Preserve supported CFG relationships and explicit diagnostics; no whole-analysis refusal")
        if value.get("outcome") == "cannot_assess":
            return _full_graph(value, context)
        from .cfg_wire import CFGWire, prepare_cfg_wire
        try:
            try:
                canonical, preflight = prepare_cfg_wire(value)
            except ValidationError as error:
                failure = schema_error(error, candidate=value, schema=CFGWire.model_json_schema())
                for row in failure.diagnostics:
                    row.setdefault("context", {})["cfg_validation_barrier"] = "candidate_schema"
                raise failure from error
            try:
                accepted = _full_graph(canonical, context)
            except StructuralValidationError as error:
                compiled = deepcopy(error.diagnostics)
                # Compiler owners refer to its own diagnostics. Prefixing the
                # independent application errors must retain that exact link.
                for row in compiled:
                    cause = row.get("context", {}).get("cfg_rejected_block_cascade")
                    if cause is not None:
                        for owner in cause["rejected_blocks"]:
                            owner["diagnostic_index"] += len(preflight)
                    if row["code"] == "source_copy":
                        row.setdefault("context", {})["cfg_validation_barrier"] = "source_copy"
                raise StructuralValidationError(preflight + compiled) from error
            if preflight:
                # A successful compiler cannot override an application rule.
                raise StructuralValidationError(preflight)
            return accepted
        except StructuralValidationError as error:
            # Compiler candidates include deterministic bookkeeping/source
            # copies. Bind corrective ownership back to the exact original
            # wire object, whose record positions have been preserved.
            rows = deepcopy(error.diagnostics)
            for row in rows:
                row.setdefault("context", {})["cfg_correction_candidate_sha256"] = canonical_sha256(value)
            raise StructuralValidationError(rows) from error
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
    allowed = {"source_owner", "cfg_path", "task_run", "controlled_path", "processing_step",
               "graph_repair_path", "processing_scope_path", "sensitivity_scope_path",
               "task-correspondence_scope_path"}
    if set(context) - allowed:
        raise ValueError("Unknown document-step context")
    required = {"full_graph": {"source_owner"}, "cfg_wire": {"source_owner"},
        "full_annotation": {"source_owner", "cfg_path", "task_run"},
        "flat_annotation": {"source_owner", "cfg_path", "task_run"},
        "graph_audit": {"source_owner", "controlled_path"},
        "cfg_wire_v5": {"source_owner"},
        "graph_facts_v1": {"source_owner"},
        "graph_updates_v1": {"source_owner", "graph_repair_path"},
        "processing_fragment": {"source_owner", "cfg_path"},
        "task-correspondence_fragment": {"source_owner", "cfg_path", "task_run", "processing_step"},
        "sensitivity_fragment": {"source_owner", "cfg_path", "processing_step"}}.get(kind, set())
    if not required <= set(context):
        raise ValueError("Missing document-step context: " + ", ".join(sorted(required-set(context))))
    if "processing_scope_path" in context and (kind != "processing_fragment" or max_corrections != 0):
        raise ValueError("A scoped processing repair uses one bounded request")
    if "sensitivity_scope_path" in context and (kind != "sensitivity_fragment" or max_corrections != 0):
        raise ValueError("A scoped sensitivity repair uses at most one bounded request")
    if "task-correspondence_scope_path" in context and (kind != "task-correspondence_fragment" or max_corrections != 0):
        raise ValueError("A scoped Task correspondence repair uses at most one bounded request")
    refs = {}
    if kind in {"processing_fragment", "sensitivity_fragment"} and "task_run" in context:
        raise ValueError("Processing and sensitivity steps must not receive the Task")
    for name in ("source_owner", "task_run", "processing_step"):
        if name in context:
            refs[name] = make_run_reference(directory, context[name])
    for name in ("cfg_path", "controlled_path", "graph_repair_path", "processing_scope_path",
                 "sensitivity_scope_path", "task-correspondence_scope_path"):
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


def _program_scope(context):
    revision = context.get("sensitivity_revision") or context.get("correspondence_revision")
    if revision is not None and not revision["scope"]["slots"]:
        return revision["scope"]
    return None


def _program_fragment(directory, manifest, context, writer, replay):
    if (directory / "calls").exists():
        raise ValueError("A program-only fragment cannot contain model calls")
    value = validate_step(manifest["kind"], {"slots": []}, context=context)
    path = directory / "value.json"
    if replay:
        if read(path) != value:
            raise ValueError("Program-carried fragment differs")
    else:
        writer.json(path, value)
    result = {"identity": manifest["identity"], "value_file": "value.json", "value_sha256": sha_file(path),
              "program_revision_sha256": _program_scope(context)["scope_sha256"]}
    if replay:
        if read(directory / "result.json") != result:
            raise ValueError("Program-carried revision receipt differs")
    else:
        writer.json(directory / "result.json", result)
    return value


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
        if _program_scope(context) is not None:
            if client is not None:
                raise ValueError("A program-carried fragment does not take a model client")
            return _program_fragment(directory, manifest, context, writer, replay)
        chain = ResponseChain(directory, prefix="calls", base_prompt=(directory / "prompt.txt").read_bytes().decode(),
            request_kind="document_guided_" + manifest["kind"], config=saved_config, writer=writer,
            validate=lambda raw: validate_step(manifest["kind"], raw, context=context),
            client_factory=None if client is None else injected_factory(client), replay=replay,
            max_corrections=manifest.get("max_corrections"), stop_event=stop_event,
            correction_strategy=_bind_strategy(manifest["kind"], context),
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


def _saved_step_value(directory, manifest, *, expected_identity=STEP_IDENTITY):
    """Read an already validated value without replaying semantic corrections.

    Bytes and terminal selection remain checked. Explicit recomputation below
    is responsible for reconstructing normalization, record replacement and
    semantic validation from the archived answers.
    """
    result = read(directory / "result.json")
    chain = read(directory / "calls/chain.json")
    expected_name = "document.md" if manifest["kind"] in {"document", "flow_document"} else "value.json"
    if (result.get("identity") != expected_identity or result.get("value_file") != expected_name
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
    identity = read(directory / "manifest.json")["identity"] if not recompute else STEP_IDENTITY
    if identity not in READABLE_STEP_IDENTITIES:
        raise ValueError("Unsupported document step identity")
    manifest = checked_manifest(directory, identity, recompute=recompute)
    config = analysis_config(manifest["config"])
    if manifest["config"] != config:
        raise ValueError("Document step configuration differs")
    context = _step_context(directory, manifest)
    for dep in manifest["dependencies"]:
        resolve_file(directory, dep)
    if _program_scope(context) is not None:
        return _program_fragment(directory, manifest, context, ArtifactWriter(()), True)
    if not recompute:
        return _saved_step_value(directory, manifest, expected_identity=identity)
    chain = ResponseChain(directory, prefix="calls", base_prompt=(directory / "prompt.txt").read_bytes().decode(),
        request_kind="document_guided_" + manifest["kind"], config=config, writer=ArtifactWriter(()),
        validate=lambda raw: validate_step(manifest["kind"], raw, context=context), replay=True, read_only=True,
        max_corrections=manifest.get("max_corrections"),
        correction_strategy=_bind_strategy(manifest["kind"], context))
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
        step = resolve_run_reference(directory, ref)
        if manifest["identity"] != ANNOTATION_IDENTITY:
            _read_archived_step(step, manifest["identity"])
        else:
            load_step(step)
    return {key: refs[key]}


def _read_archived_step(directory, annotation_identity):
    """Read a terminal archived constituent with its recorded step/producer identity."""
    identity = read(directory / "manifest.json")["identity"]
    if annotation_identity == "skillflow-document-annotation-v13":
        if identity not in {"skillflow-document-step-v18", "skillflow-document-step-v19"}:
            raise ValueError("Unsupported step producer for archived annotation")
        return load_step(directory)
    v11 = annotation_identity == ARCHIVED_ANNOTATION_IDENTITY
    versions = range(13, 17) if v11 else (17,)
    if identity not in {f"skillflow-document-step-v{i}" for i in versions}:
        raise ValueError("Unsupported step producer for archived annotation")
    manifest = checked_manifest(directory, identity)
    if manifest["config"] != analysis_config(manifest["config"]):
        raise ValueError("Archived document step configuration differs")
    for reference in manifest["dependencies"]:
        resolve_file(directory, reference)
    for name, reference in manifest.get("context", {}).items():
        if name in {"source_owner", "task_run", "processing_step"}:
            resolve_run_reference(directory, reference)
        elif name.endswith("_path"):
            resolve_file(directory, reference)
    result = read(directory / "result.json")
    if "program_revision_sha256" not in result:
        return _saved_step_value(directory, manifest, expected_identity=identity)
    # Old zero-call carries only retired existing owners; verify the saved
    # scope, original candidate and output, without invoking the new compiler.
    kind = manifest["kind"].removesuffix("_fragment")
    if kind not in {"sensitivity", "task-correspondence"} or (directory / "calls").exists():
        raise ValueError("Archived program-carry owner or call inventory differs")
    run = directory.parent.parent
    expected_paths = scoped_dependencies(run, kind)
    owners = [resolve_file(directory, ref) for ref in manifest["dependencies"]]
    path = resolve_file(directory, manifest["context"][kind + "_scope_path"])
    if directory.name != "revision-" + kind or path != expected_paths[-1] or owners[-len(expected_paths):] != expected_paths:
        raise ValueError("Archived program carry has different scope dependencies")
    scope = read(path)
    before = _read_archived_step(run / "steps" / kind, annotation_identity)
    digest = canonical_sha256({key: value for key, value in scope.items() if key != "scope_sha256"})
    if (scope.get("slots") != {} or scope.get("scope_sha256") != digest
            or canonical_sha256(before) != scope.get("candidate_sha256")):
        raise ValueError("Archived program carry must bind a zero-slot plan and exact candidate")
    if kind == "sensitivity":
        if scope["identity"] != f"skillflow-sensitivity-revision-scope-v{1 if v11 else 2}":
            raise ValueError("Unsupported archived sensitivity scope")
        retired = set(scope["removed_instruction_ids"])
        carried = deepcopy(before)
        if "declarations" in before:
            carried["declarations"] = [row for row in before["declarations"] if row["instruction_id"] not in retired]
        if not v11 and "entry_gaps" in before:
            carried["entry_gaps"] = [row for row in before["entry_gaps"] if row["instruction_id"] not in retired]
    else:
        from .fragment_revision import merge_correspondence_revision
        carried = merge_correspondence_revision(before, scope, {"slots": []})
    file = directory / "value.json"
    if (read(file) != carried or result != {"identity": identity, "value_file": "value.json",
            "value_sha256": sha_file(file), "program_revision_sha256": digest}):
        raise ValueError("Archived program carry differs from its bound result")
    return carried


def check_annotation_unchanged(directory, manifest):
    """Check persisted bindings before commit without loading compiled payloads."""
    from skillflow.propagation.annotation.inputs import load_prepared_material
    directory = checked_run_path(directory)
    identity = manifest.get("identity")
    if identity not in READABLE_ANNOTATION_IDENTITIES or checked_manifest(directory, identity) != manifest:
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
    identity = read(directory / "manifest.json").get("identity")
    if identity not in READABLE_ANNOTATION_IDENTITIES or recompute and identity != ANNOTATION_IDENTITY:
        raise ValueError("Unsupported annotation protocol for this operation")
    manifest = checked_manifest(directory, identity, recompute=recompute)
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
    identity = {"identity": manifest["identity"], "manifest_sha256": manifest["manifest_sha256"],
        "accepted_response_sha256": canonical_sha256(wire if wire is not None else raw), "candidate_origin": manifest["candidate_origin"],
        "implementation": manifest["implementation"], **provenance}
    return {"manifest": manifest, "material": material, "raw_annotation": raw,
        "wire_annotation": wire,
        "compiled_annotation": compiled, "mapping": mapping, "task": material["task"],
        "source_metadata": metadata, "upstream_identity": identity,
        "result": {"status": "complete", "candidate_origin": manifest["candidate_origin"]}}
