"""Recorded joint analysis after graph construction, with one bounded repair.

This application layer composes stage services; it contains no transfer, demand,
sensitivity or model-transport rules. A successful calculation is not a proof of
semantic correctness, and review status remains independent of analysis status.
"""
from __future__ import annotations

from copy import deepcopy
from html import escape
from pathlib import Path
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.paths import project_root
from skillflow.common.recording import canonical_sha256, implementation_provenance, now, sha_file
from skillflow.common.runs import exclusive_run
from skillflow.common.source_evidence import _json_object
from skillflow.common.upstream import checked_run_path
from skillflow.common.json_normalization import NORMALIZATION_VERSION
from skillflow.propagation.annotation.config import annotation_config, PUBLIC_CONFIG_FIELDS


IDENTITY = "skillflow-analysis-run-v7"
FORMAT_VERSION = 7
POLICY = {"structural_corrections": "unlimited", "max_repairs": 1, "reextract_cfg": False,
          "json_normalization": NORMALIZATION_VERSION,
          "review": True, "source_only_task": True, "diagnostic_analysis_on_review_failure": True,
          "automatic_resend_after_acceptance": False}


class PipelineIdentityError(ValueError):
    """The saved chain no longer matches its inputs or selected stage."""


def _read(path):
    return _json_object(_directory(path).read_bytes().decode("utf-8"))


def _seal(value):
    return {**deepcopy(value), "manifest_sha256": canonical_sha256(value)}


def _unseal(value):
    unsigned = {k: v for k, v in value.items() if k != "manifest_sha256"}
    if value.get("manifest_sha256") != canonical_sha256(unsigned):
        raise PipelineIdentityError("Pipeline record digest mismatch")
    return unsigned


def _config(config):
    config = {} if config is None else config
    if not isinstance(config, dict) or set(config) - set(PUBLIC_CONFIG_FIELDS):
        raise ValueError("Only public model configuration may enter the pipeline")
    return annotation_config(config)


def _no_links(path):
    _directory(path)


def _directory(path):
    try:
        return checked_run_path(path)
    except ValueError as error:
        raise PipelineIdentityError("Pipeline paths must not contain links or reparse points") from error


def _safe_output(directory, source, analysis):
    if (source.is_dir() and (directory.is_relative_to(source) or source.is_relative_to(directory))
            or analysis.is_relative_to(directory)):
        raise ValueError("Pipeline output must not overlap its source or CFG input")
    root = project_root()
    for protected in (root / "dataset", root / "result"):
        if directory == protected or directory.is_relative_to(protected):
            raise ValueError("Pipeline output cannot overwrite frozen inputs or deliveries")


def prepare_analysis_run(input, analysis, *, run_dir, config=None, user_request=None, secrets=()):
    """Freeze source/CFG once; prepare a genuinely source-only first call."""
    from skillflow.common.inputs.snapshot import freeze_input, read_snapshot
    from skillflow.graph.validation import checked_cfg
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    from skillflow.task.runner import prepare_task_run
    directory, source, graph = _directory(run_dir), _directory(input), _directory(analysis)
    public, writer = _config(config), ArtifactWriter(tuple(secrets))
    if user_request is not None and (type(user_request) is not str or not user_request.strip()):
        raise ValueError("user_request must be nonempty text or null")
    if (directory / "manifest.json").is_file():
        with exclusive_run(directory):
            manifest = _verify(directory, config=public, recompute=True)
            request = _unseal(_read(directory / "preparing.json"))
            if (manifest["preparation_status"] != "ready"
                    or (directory / "task/manifest.json").exists()):
                raise PipelineIdentityError("Prepare requires a new pipeline directory")
            supplied = {"input": str(source), "analysis": str(graph),
                        "user_request_sha256": canonical_sha256(user_request), "config": public}
            if any(canonical_sha256(supplied[key]) != canonical_sha256(request[key]) for key in supplied):
                raise PipelineIdentityError("Interrupted Task preparation has different inputs")
            _ensure_task_preparation(directory, manifest, secrets=secrets, allow_recovery=True)
            return manifest
    _safe_output(directory, source, graph)
    request = {"input": str(source), "analysis": str(graph), "analysis_sha256": sha_file(graph),
               "user_request_sha256": canonical_sha256(user_request), "config": public,
               "implementation": implementation_provenance()}
    if writer.clean(request) != request:
        raise ValueError("A credential overlaps pipeline preparation")
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if (directory / "manifest.json").exists():
            raise PipelineIdentityError("Prepare requires a new pipeline directory")
        marker = directory / "preparing.json"
        if marker.exists():
            if _unseal(_read(marker)) != request:
                raise PipelineIdentityError("Interrupted preparation has different inputs")
        else:
            if any(p.name != ".runner.lock" for p in directory.iterdir()):
                raise PipelineIdentityError("Unknown files in pipeline directory")
            writer.json(marker, _seal(request))
        status, error = "ready", None
        try:
            candidate = _json_object(graph.read_bytes().decode("utf-8-sig"))
            cfg = checked_cfg(candidate["cfg"])
            if not (directory / "inputs/snapshot.json").exists():
                freeze_input(source, directory, writer)
            _, frozen, metadata = read_snapshot(directory)
            for name,value in (("cfg.json",cfg),("runtime-contract.json",runtime_contract()),("user-request.json",user_request)):
                target = directory / "inputs" / name
                if target.exists():
                    import json
                    if canonical_sha256(json.loads(target.read_bytes().decode("utf-8"))) != canonical_sha256(value):
                        raise PipelineIdentityError("Interrupted frozen component differs")
                writer.json(target,value)
            if sha_file(graph) != request["analysis_sha256"]:
                raise PipelineIdentityError("CFG changed during preparation")
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            status,error = "input_error", writer.clean(f"{type(exc).__name__}: {exc}")
        files = {p.relative_to(directory).as_posix():sha_file(p) for p in sorted((directory/"inputs").rglob("*")) if p.is_file()}
        manifest = _seal({"identity":IDENTITY,"schema_version":FORMAT_VERSION,"run_id":directory.name,
            "created_at":now(),"config":public,"implementation":request["implementation"],"policy":POLICY,
            "preparation_status":status,"preparation_error":error,"preparation_sha256":canonical_sha256(request),
            "files":files,"upstream":None})
        writer.json(directory/"manifest.json",manifest)
        if status == "ready":
            prepare_task_run(directory/"task",source_owner=directory,user_request=user_request,config=public,secrets=secrets,
                             resume_preparation=True)
    return manifest


def _verify(directory, *, config=None, recompute=False):
    from skillflow.propagation.annotation.inputs import read_component
    manifest=_read(directory/"manifest.json"); _unseal(manifest)
    if (manifest.get("identity")!=IDENTITY or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"]!=FORMAT_VERSION or canonical_sha256(manifest.get("policy"))!=canonical_sha256(POLICY)):
        raise PipelineIdentityError("Unsupported source/Task analysis protocol")
    preparation=_unseal(_read(directory/"preparing.json"))
    if canonical_sha256(preparation)!=manifest["preparation_sha256"]:
        raise PipelineIdentityError("Pipeline preparation changed")
    files={p.relative_to(directory).as_posix():sha_file(_directory(p)) for p in sorted((directory/"inputs").rglob("*")) if p.is_file()}
    if files!=manifest["files"]:
        raise PipelineIdentityError("Frozen source or graph changed")
    if config is not None and _config(config)!=manifest["config"]:
        raise PipelineIdentityError("Pipeline configuration changed")
    if recompute and manifest["implementation"]!=implementation_provenance():
        raise PipelineIdentityError("Pipeline implementation identity changed")
    return manifest


def _base_result(manifest):
    return {"identity": IDENTITY, "schema_version": FORMAT_VERSION, "run_id": manifest["run_id"],
        "pipeline_manifest_sha256": manifest["manifest_sha256"], "status": "interrupted",
        "stage": "task", "reason": "The pipeline has not completed.",
        "task": None,
        "annotation": None, "refinement": None, "selected_annotation": None,
        "propagation": None, "doe": None, "counts": {"logical_calls": 0, "structural_corrections": 0,
                                                     "json_normalizations": 0,
                                                     "http_attempts": 0, "http_retries": 0},
        "interrupt_point": None, "unfinished_outputs": None,
        "notice": "Static results depend on declared semantics and supported rules; review success is not proof of correctness."}


def verify_analysis_prepared(run_dir, *, config=None):
    directory = _directory(run_dir)
    manifest = _verify(directory,config=config,recompute=True)
    if manifest["preparation_status"] == "ready":
        _ensure_task_preparation(directory, manifest, allow_recovery=False)
    return manifest


def _ensure_task_preparation(directory, manifest, *, secrets=(), allow_recovery=False):
    """Recover only a missing Task preparation from the immutable source owner."""
    from skillflow.common.inputs.snapshot import read_snapshot
    from skillflow.common.upstream import make_run_reference
    from skillflow.task.material import prepare_task_material
    from skillflow.task.runner import prepare_task_run, verify_task_prepared
    target = directory / "task"
    request = _unseal(_read(directory / "preparing.json"))
    # This value is frozen orchestration input, not a second interpretation of Task.
    import json
    user_request = json.loads((directory / "inputs/user-request.json").read_bytes().decode("utf-8"))
    if canonical_sha256(user_request) != request["user_request_sha256"]:
        raise PipelineIdentityError("Frozen user request differs from pipeline preparation")
    _, source, _metadata = read_snapshot(directory)
    expected = prepare_task_material(source, user_request=user_request)
    if not (target / "manifest.json").is_file():
        if not allow_recovery:
            raise PipelineIdentityError("Task preparation is incomplete; resume prepare or run from frozen inputs")
        prepare_task_run(target, source_owner=directory, user_request=user_request,
                         config=manifest["config"], secrets=secrets, resume_preparation=True)
    prepared = verify_task_prepared(target, config=manifest["config"])
    if (canonical_sha256(prepared["source_owner"]) != canonical_sha256(make_run_reference(target,directory))
            or prepared["material_sha256"] != canonical_sha256(expected)
            or prepared["request_kind"] != "task_extraction"
            or prepared["revision_sha256"] != canonical_sha256(None)):
        raise PipelineIdentityError("Task preparation differs from the frozen pipeline source or request")


def _stage_summary(result):
    return {key: result.get(key) for key in ("status", "reason", "error_kind")}


def _counts(directory):
    """Count actual recorded stages, never estimate calls from stage names."""
    from skillflow.propagation.annotation.runner import _counts as annotation_counts
    from skillflow.propagation.review.runner import _counts as review_counts
    result = {"logical_calls": 0, "structural_corrections": 0, "json_normalizations": 0,
              "http_attempts": 0, "http_retries": 0}
    from skillflow.common.structural_correction import chain_counts
    for relative, counter in (("task", lambda path:chain_counts(path,"calls/task")),
                              ("refinement/task-revision",lambda path:chain_counts(path,"calls/task")),
                              ("annotation", annotation_counts),
                              ("refinement/initial-review", review_counts),
                              ("refinement/repair", annotation_counts),
                              ("refinement/final-review", review_counts)):
        if (directory / relative / "manifest.json").exists():
            for key, value in counter(directory / relative).items():
                if key in result:
                    result[key] += value
    return result


def _refinement_corresponds(directory, original):
    from skillflow.propagation.review.refinement import load_refinement_inputs
    from skillflow.common.upstream import make_run_reference
    target = directory / "refinement"
    prepared = load_refinement_inputs(target)
    if (prepared["material"] != original["material"]
            or prepared["raw_annotation"] != original["raw_annotation"]
            or prepared["manifest"]["upstream"] != make_run_reference(target, directory / "annotation")
            or prepared["provenance"] != {
                "kind": "accepted_annotation", "upstream_identity": original["upstream_identity"]}):
        raise PipelineIdentityError("Refinement no longer belongs to the accepted annotation")


def _selected(directory, original, refinement):
    from skillflow.propagation.annotation.loading import load_annotation_run
    name = "refinement/repair" if refinement["selected"] == "repair" else "annotation"
    if refinement["selected"] not in {"original", "repair"}:
        raise PipelineIdentityError("Unknown selected annotation stage")
    selected = original if name == "annotation" else load_annotation_run(directory / name)
    if any(selected["material"][key] != original["material"][key] for key in ("source","cfg","user_request","runtime_contract")):
        raise PipelineIdentityError("Selected annotation changed frozen source, CFG or request")
    receipt = {"path": name, "manifest_sha256": selected["manifest"]["manifest_sha256"],
               "raw_sha256": canonical_sha256(selected["raw_annotation"])}
    return selected, receipt


def _check_propagation(directory, selected):
    from skillflow.propagation.runner import load_propagation_materials
    try:
        loaded = load_propagation_materials(directory / "propagation")
    except (ValueError, OSError) as error:
        raise PipelineIdentityError(f"Propagation materials are invalid: {error}") from error
    if (loaded.provenance.get("kind") != "model_annotation"
            or loaded.provenance.get("accepted_response_sha256") != selected["upstream_identity"]["accepted_response_sha256"]
            or loaded.annotation != {key: selected[key] for key in
                                    ("material", "task", "raw_annotation", "compiled_annotation", "mapping")}):
        raise PipelineIdentityError("Propagation belongs to a different selected annotation")
    return loaded


def _propagation_summary(directory):
    from skillflow.propagation.runner import load_propagation_materials
    loaded = load_propagation_materials(directory / "propagation")
    return {"status": loaded.status, "manifest_sha256": loaded.manifest["manifest_sha256"],
            "sink_count": len(loaded.sinks)}


def _doe_summary(directory):
    manifest = _read(directory / "doe/manifest.json")
    result = _read(directory / "doe/doe-result.json")
    return {"status": result["status"], "manifest_sha256": manifest["manifest_sha256"]}


def _check_doe(directory, propagation):
    from skillflow.doe.formal_runner import load_doe_run
    try:
        loaded = load_doe_run(directory / "doe")
    except (ValueError, OSError) as error:
        raise PipelineIdentityError(f"DOE materials are invalid: {error}") from error
    if (loaded["upstream_identity"] != propagation.upstream_identity
            or loaded["annotation"] != propagation.annotation):
        raise PipelineIdentityError("DOE belongs to a different selected propagation run")
    return loaded


def _finish(result):
    complete = (result["refinement"]["status"] == "review_passed"
                and result["propagation"]["status"] == "complete" and result["doe"]["status"] == "complete")
    result.update(status="complete" if complete else "diagnostic", stage="finished",
        reason=("All stages completed; the bounded review reported no material issue."
                if complete else "Analysis is available with review findings, a review failure, or analysis limitations."))


def _validate_result(result, manifest):
    if set(result) != set(_base_result(manifest)):
        raise PipelineIdentityError("Pipeline result fields differ")
    if result["status"] not in {"complete", "diagnostic", "failed", "interrupted"}:
        raise PipelineIdentityError("Unknown pipeline status")
    if result["stage"] not in {"task", "annotation", "refinement", "propagation", "doe", "finished"}:
        raise PipelineIdentityError("Unknown pipeline stage")
    if (result["stage"] == "finished") != (result["status"] in {"complete", "diagnostic"}):
        raise PipelineIdentityError("Pipeline status conflicts with its completed stage prefix")
    if set(result["counts"]) != {"logical_calls", "structural_corrections", "json_normalizations", "http_attempts", "http_retries"} or any(
            type(v) is not int or v < 0 for v in result["counts"].values()):
        raise PipelineIdentityError("Invalid pipeline call counts")
    if result["annotation"] is not None and (result["task"] or {}).get("status") != "complete":
        raise PipelineIdentityError("Annotation requires an accepted source-only Task")
    if result["refinement"] is not None and (result["annotation"] or {}).get("status") != "complete":
        raise PipelineIdentityError("Review requires a completed annotation")
    if result["selected_annotation"] is not None and (
            result["refinement"] is None or result["refinement"]["status"] == "interrupted"):
        raise PipelineIdentityError("Candidate selection is premature")
    if result["propagation"] is not None and result["selected_annotation"] is None:
        raise PipelineIdentityError("Propagation requires an accepted selection")
    if result["doe"] is not None and result["propagation"] is None:
        raise PipelineIdentityError("DOE requires propagation")
    if result["stage"] == "finished" and any(result[k] is None for k in (
            "task", "annotation", "refinement", "selected_annotation", "propagation", "doe")):
        raise PipelineIdentityError("Completed pipeline lacks committed stages")
    if result["status"] != "interrupted" and (result["interrupt_point"] is not None or result["unfinished_outputs"] is not None):
        raise PipelineIdentityError("Only interruption records may carry interrupted stage state")


def _save(directory, result, writer, *, replay=False):
    target = _directory(directory / "replay" if replay else directory)
    lines = ["# Joint analysis pipeline", "", f"Status: `{result['status']}` · stage: `{result['stage']}`", "",
             result["reason"], "", result["notice"], "", f"Logical calls: {result['counts']['logical_calls']}; "
             f"structural corrections: {result['counts']['structural_corrections']} (unlimited); "
             f"JSON normalizations: {result['counts']['json_normalizations']}; "
             f"HTTP attempts: {result['counts']['http_attempts']}", ""]
    links = []
    for key, path, label in (("task", "task/report.md", "Independent Task extraction"), ("annotation", "annotation/report.md", "Joint annotation"),
                              ("refinement", "refinement/report.html", "Initial review / one repair / fresh review"),
                              ("propagation", "propagation/report.html", "Forward propagation"),
                              ("doe", "doe/report.html", "Task demand and sensitive exposure comparison")):
        if result[key] is not None:
            url = ("../" if replay else "") + path
            lines += [f"- {label}: `{result[key]['status']}` — [report]({url})"]
            links.append(f"<li>{escape(label)}: <b>{escape(result[key]['status'])}</b> · <a href='{url}'>report</a></li>")
    if result["selected_annotation"] is not None:
        lines += ["", "Selected accepted annotation: `" + result["selected_annotation"]["path"] + "`."]
    writer.text(_directory(target / "report.md"), "\n".join(lines))
    writer.text(_directory(target / "report.html"), "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<title>SkillFlow joint analysis</title><style>body{max-width:1050px;margin:40px auto;font:16px/1.7 system-ui;padding:0 20px}"
        "p{white-space:pre-wrap}code{overflow-wrap:anywhere}</style><h1>Joint analysis pipeline</h1>"
        f"<p><b>{escape(result['status'])}</b> · {escape(result['stage'])}</p><p>{escape(result['reason'])}</p>"
        f"<p>{escape(result['notice'])}</p><p>Logical calls: {result['counts']['logical_calls']}; "
        f"structural corrections: {result['counts']['structural_corrections']} (unlimited); "
        f"JSON normalizations: {result['counts']['json_normalizations']}; "
        f"HTTP attempts: {result['counts']['http_attempts']}</p><ul>{''.join(links)}</ul>"
        "<p><a href='result.json'>Stage decisions</a></p></html>")
    writer.json(_directory(target / "result.json"), _seal(result))


def _unfinished(directory, stage):
    if stage not in {"propagation", "doe"}:
        return None
    target = directory / stage
    if not target.exists() or (target / "manifest.json").exists():
        return None
    paths = list(target.rglob("*"))
    _no_links(target)
    for path in paths:
        _no_links(path)
    return {"stage": stage, "files": {p.relative_to(target).as_posix(): sha_file(p)
            for p in sorted(paths) if p.is_file()},
            "directories": sorted(p.relative_to(target).as_posix() for p in paths if p.is_dir())}


def _resume_unfinished(directory, receipt):
    if receipt is None:
        return
    stage = receipt["stage"]
    target = (directory / stage).resolve()
    if stage not in {"propagation", "doe"} or target.parent != directory:
        raise PipelineIdentityError("Interrupted output path is outside its pipeline")
    if _unfinished(directory, stage) != receipt:
        raise PipelineIdentityError("Uncommitted stage changed after interruption")
    # Only these exact owned, uncommitted bytes may be discarded for recomputation.
    for name in receipt["files"]:
        (target / name).unlink()
    for name in sorted(receipt["directories"], key=lambda p: len(Path(p).parts), reverse=True):
        (target / name).rmdir()
    target.rmdir()


def run_analysis(run_dir, *, client_factory=None, review_client_factory=None, repair_client_factory=None,
                 task_client_factory=None, task_repair_client_factory=None,
                 config=None, env_file=None, secrets=(), stop_event=None, replay=False, progress=None):
    """Execute recorded stages once; accepted calls are reused on recovery."""
    from skillflow.propagation.annotation import runner as annotations
    from skillflow.propagation.annotation.loading import load_annotation_run
    from skillflow.propagation.review.refinement import prepare_refinement_run, run_refinement
    from skillflow.propagation.runner import run_propagation, replay_propagation
    from skillflow.doe.formal_runner import run_doe, load_doe_run, replay_doe
    if replay and any(v is not None for v in (client_factory, review_client_factory, repair_client_factory, task_client_factory, task_repair_client_factory, env_file)):
        raise ValueError("Offline pipeline replay does not accept online clients or environment configuration")
    directory, stopping, writer = _directory(run_dir), stop_event or Event(), ArtifactWriter(tuple(secrets))
    with exclusive_run(directory):
        manifest = _verify(directory, config=config, recompute=True)
        public = manifest["config"]
        saved = _unseal(_read(directory / "result.json")) if (directory / "result.json").exists() else None
        local_task_preparation_failure = bool(saved and saved["status"] == "failed"
            and saved["stage"] == "task" and saved["task"] is None
            and saved["counts"]["logical_calls"] == 0 and not (directory/"task/manifest.json").exists())
        if saved and saved["status"] != "interrupted" and not replay and not local_task_preparation_failure:
            return load_analysis_run(directory)["result"]
        if saved and not replay:
            _resume_unfinished(directory, saved.get("unfinished_outputs"))
        result = _base_result(manifest)
        point = "before_task"
        def stop(where):
            nonlocal point
            point = where
            if stopping.is_set() or (replay and saved and saved["status"] == "interrupted" and saved["interrupt_point"] == where):
                raise KeyboardInterrupt(saved["reason"] if replay and saved else "Execution interrupted; no later stage was started.")
        try:
            stop("before_task")
            if manifest["preparation_status"] != "ready":
                result.update(status="failed",reason=manifest["preparation_error"])
                return _finalize(directory,result,saved,writer,replay=replay)
            _ensure_task_preparation(directory, manifest, secrets=secrets, allow_recovery=not replay)
            if not replay and client_factory is None:
                from skillflow.common.recording import streaming_factory
                client_factory, loaded_secrets = streaming_factory(public, env_file=env_file)
                secrets = tuple(set(secrets) | set(loaded_secrets)); writer=ArtifactWriter(secrets)
            from skillflow.task.runner import run_task,load_task_run
            extracted=run_task(directory/"task",client_factory=None if replay else task_client_factory or client_factory,
                config=public,secrets=secrets,stop_event=stopping,replay=replay,progress=progress)
            result["task"]=_stage_summary(extracted)
            if extracted["status"]=="interrupted":
                stop("task"); raise KeyboardInterrupt(extracted["reason"])
            if extracted["status"]!="complete":
                result.update(status="failed",reason="Task extraction failed: "+extracted["reason"])
                return _finalize(directory,result,saved,writer,replay=replay)
            stop("after_task"); result["stage"]="annotation"
            if not (directory/"annotation/manifest.json").exists():
                if replay: raise PipelineIdentityError("Missing recorded annotation preparation")
                annotations.prepare_run(None,None,run_dir=directory/"annotation",config=public,secrets=secrets,
                    upstream_run=directory,task_run=directory/"task")
            stop("before_annotation")
            stage = annotations.run_annotation(directory / "annotation", client_factory=client_factory,
                config=public, secrets=secrets, stop_event=stopping, replay=replay, progress=progress)
            result["annotation"] = _stage_summary(stage)
            if stage["status"] == "interrupted":
                stop("annotation")
                raise KeyboardInterrupt(stage["reason"])
            if stage["status"] != "complete":
                result.update(status="failed", reason="Joint annotation failed: " + stage["reason"])
            else:
                stop("after_annotation")
                original = load_annotation_run(directory / "annotation")
                result["stage"] = "refinement"
                target = directory / "refinement"
                if not (target / "manifest.json").exists():
                    if replay:
                        raise PipelineIdentityError("Missing recorded refinement preparation")
                    prepare_refinement_run(None, None,
                        original["material"], original["raw_annotation"], run_dir=target,
                        provenance={"kind": "accepted_annotation", "upstream_identity": original["upstream_identity"]},
                        config=public, secrets=secrets, upstream_run=directory / "annotation")
                _refinement_corresponds(directory, original)
                refined = run_refinement(target, review_client_factory=review_client_factory or client_factory,
                    repair_client_factory=repair_client_factory or client_factory, config=public,
                    env_file=env_file, secrets=secrets, stop_event=stopping, replay=replay, progress=progress,
                    task_repair_client_factory=task_repair_client_factory or task_client_factory or client_factory)
                result["refinement"] = {key: refined[key] for key in ("status", "selected", "reason")}
                if refined["status"] == "interrupted":
                    stop("refinement")
                    raise KeyboardInterrupt(refined["reason"])
                selected, result["selected_annotation"] = _selected(directory, original, refined)
                stop("after_refinement")
                result["stage"] = "propagation"
                stop("propagation")
                if replay:
                    if not (directory / "propagation/manifest.json").exists():
                        if saved and saved["stage"] == "propagation" and saved["status"] == "failed":
                            result.update(status="failed", reason=saved["reason"])
                            return _finalize(directory, result, saved, writer, replay=True)
                        stop("propagation")
                    replay_propagation(directory / "propagation")
                    if _read(directory / "propagation/replay/summary.json")["status"] != "matched":
                        raise PipelineIdentityError("Forward propagation replay differs")
                elif not (directory / "propagation/manifest.json").exists():
                    run_propagation(directory / result["selected_annotation"]["path"], run_dir=directory / "propagation")
                propagated = _check_propagation(directory, selected)
                result["propagation"] = _propagation_summary(directory)
                stop("after_propagation")
                result["stage"] = "doe"
                stop("doe")
                if replay:
                    if not (directory / "doe/manifest.json").exists():
                        if saved and saved["stage"] == "doe" and saved["status"] == "failed":
                            result.update(status="failed", reason=saved["reason"])
                            return _finalize(directory, result, saved, writer, replay=True)
                        stop("doe")
                    if replay_doe(directory / "doe")["status"] != "matched":
                        raise PipelineIdentityError("DOE replay differs")
                elif not (directory / "doe/manifest.json").exists():
                    run_doe(directory / "propagation", run_dir=directory / "doe")
                _check_doe(directory, propagated)
                result["doe"] = _doe_summary(directory)
                stop("after_doe")
                _finish(result)
        except PipelineIdentityError:
            raise
        except (annotations.RunIdentityError,) as error:
            raise PipelineIdentityError(str(error)) from error
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(str(error)), interrupt_point=point,
                          unfinished_outputs=_unfinished(directory, result["stage"]))
        except Exception as error:
            result.update(status="failed", reason=writer.clean(f"{type(error).__name__}: {error}"))
        return _finalize(directory, result, saved, writer, replay=replay)


def _finalize(directory, result, saved, writer, *, replay=False):
    result["counts"] = _counts(directory)
    _validate_result(result, _read(directory / "manifest.json"))
    if replay and saved != result:
        raise PipelineIdentityError("Pipeline replay differs from saved stage decisions")
    _save(directory, result, writer, replay=replay)
    return deepcopy(result)


def load_analysis_run(run_dir):
    """Verify recorded selection and committed outputs without rerunning analysis."""
    from skillflow.propagation.annotation.loading import load_annotation_attempt, load_annotation_run
    from skillflow.propagation.review.refinement import load_refinement_run
    from skillflow.doe.formal_runner import load_doe_run
    directory = _directory(run_dir)
    manifest = _verify(directory)
    result = _unseal(_read(directory / "result.json"))
    _validate_result(result, manifest)
    if (result.get("pipeline_manifest_sha256") != manifest["manifest_sha256"]
            or result.get("identity") != IDENTITY or result.get("schema_version") != FORMAT_VERSION):
        raise PipelineIdentityError("Pipeline result belongs to another preparation")
    if result["task"] is not None:
        from skillflow.task.runner import run_task
        attempt=run_task(directory/"task",replay=True,read_only=True)
        if _stage_summary(attempt)!=result["task"]:
            raise PipelineIdentityError("Task stage summary changed")
    original = None
    if result["annotation"] is not None:
        attempt = load_annotation_attempt(directory / "annotation")
        if _stage_summary(attempt["result"]) != result["annotation"]:
            raise PipelineIdentityError("Annotation stage summary changed")
        if result["annotation"]["status"] == "complete":
            original = load_annotation_run(directory / "annotation")
    selected = None
    if result["refinement"] is not None:
        if original is None:
            raise PipelineIdentityError("Refinement has no valid initial annotation")
        _refinement_corresponds(directory, original)
        checked = load_refinement_run(directory / "refinement")["result"]
        if {key: checked[key] for key in ("status", "selected", "reason")} != result["refinement"]:
            raise PipelineIdentityError("Refinement stage summary changed")
        if result["selected_annotation"] is not None:
            selected, receipt = _selected(directory, original, checked)
            if receipt != result["selected_annotation"]:
                raise PipelineIdentityError("Selected candidate changed")
    propagated = None
    if result["propagation"] is not None:
        if selected is None:
            raise PipelineIdentityError("Propagation lacks an accepted selected candidate")
        propagated = _check_propagation(directory, selected)
        if _propagation_summary(directory) != result["propagation"]:
            raise PipelineIdentityError("Propagation summary changed")
    if result["doe"] is not None:
        if propagated is None:
            raise PipelineIdentityError("DOE lacks this pipeline's propagation")
        _check_doe(directory, propagated)
        if result["propagation"] is None or _doe_summary(directory) != result["doe"]:
            raise PipelineIdentityError("DOE summary changed")
    if result["counts"] != _counts(directory):
        raise PipelineIdentityError("Recorded pipeline call counts changed")
    if result["stage"] == "finished":
        expected = deepcopy(result)
        _finish(expected)
        if result != expected:
            raise PipelineIdentityError("Final status conceals a stage limitation")
    return {"manifest": deepcopy(manifest), "result": deepcopy(result)}


def replay_analysis(run_dir):
    return run_analysis(run_dir, replay=True)
