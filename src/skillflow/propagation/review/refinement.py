"""Review, one isolated Task revision or annotation repair, then fresh review.

Task revisions only use the source-only interface and invalidate old annotation.
CFG and source remain frozen. Each stage uses the existing recorded runners.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import nullcontext
from html import escape
from pathlib import Path
from threading import Event

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.common.inputs.snapshot import freeze_input
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import now
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import streaming_factory
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.structural_correction import correct_response
from skillflow.common.json_normalization import NORMALIZATION_VERSION
from skillflow.common.source_evidence import _json_object
from skillflow.common.upstream import checked_run_path, make_run_reference, resolve_run_reference
from skillflow.propagation.material import checked_material
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.review.runner import RunIdentityError
from skillflow.propagation.review.runner import _config
from skillflow.propagation.review.runner import _files
from skillflow.propagation.review.runner import prepare_candidate_run
from skillflow.propagation.review.runner import run_review

IDENTITY = "skill-ir-annotation-refinement-v9"
FORMAT_VERSION = 9
POLICY = {"max_semantic_repairs": 1, "max_semantic_stages": 4, "isolated_task_revision": True,
          "structural_corrections": "unlimited", "json_normalization": NORMALIZATION_VERSION,
          "automatic_resend_after_acceptance": False}


def _seal(value):
    return {**deepcopy(value), "manifest_sha256": canonical_sha256(value)}


def _unseal(value):
    unsigned = {key: item for key, item in value.items() if key != "manifest_sha256"}
    if value.get("manifest_sha256") != canonical_sha256(unsigned):
        raise RunIdentityError("Refinement artifact digest mismatch")
    return unsigned


def _result():
    return {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "status": "interrupted", "stage": "initial_review", "reason": "Not completed.",
            "initial_review": None, "task_revision": None, "repair": None, "final_review": None,
            "selected": "original", "counts": {"logical_calls": 0, "http_attempts": 0,
            "http_retries": 0, "stage_calls": 0, "structural_corrections": 0,
            "json_normalizations": 0}, "interrupt_point": None, "local_failure": None,
            "notice": "At most one semantic repair; mechanical response correction has no attempt limit. No reported review issue is not proof of semantic correctness."}


def refine_annotation(material, raw_annotation, *, review_client, repair_client, task_repair_client=None):
    """Injected, in-memory service. Durable callers use run_refinement below."""
    from skillflow.propagation.annotation.requests import build_repair_context
    from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
    material = checked_material(material)
    compile_response(raw_annotation, material)
    result = _result()
    result["raw_annotation"] = deepcopy(raw_annotation)
    def stage_response(prompt, client, validate):
        calls = 0
        def complete(current_prompt):
            nonlocal calls
            result["counts"]["logical_calls"] += 1
            result["counts"]["structural_corrections" if calls else "stage_calls"] += 1
            calls += 1
            return client.complete(current_prompt)
        def normalized(_number, _raw, _receipt):
            result["counts"]["json_normalizations"] += 1
        return correct_response(prompt, complete=complete, validate=validate, on_normalization=normalized)
    try:
        initial_material = prepare_review_material(material, raw_annotation)
        initial = stage_response(build_prompt(initial_material), review_client,
                                 lambda value: validate_response(value, initial_material))
        result["initial_review"] = initial.model_dump(mode="json")
        if not initial.findings:
            result.update(status="review_passed", reason="Initial review raised no material issue; repair was not called.")
            return result
        result["stage"] = "repair"
        from skillflow.propagation.review.models import task_objections
        objections = task_objections(initial)
        if objections:
            from skillflow.task.material import prepare_task_material
            from skillflow.task.prompts import build_task_prompt
            from skillflow.task.services import validate_task_response
            from skillflow.propagation.material import prepare_material
            tm=prepare_task_material(material["source"],user_request=material["user_request"])
            revised=stage_response(build_task_prompt(tm,{"previous_task":material["task"],"objections":objections}),
                task_repair_client or repair_client,lambda value:validate_task_response(value,tm))
            material=prepare_material(material["source"],material["cfg"],task_baseline=revised,user_request=material["user_request"])
            result["task_revision"]={"status":"complete"}
            repair_prompt=annotation_prompt(material)
        else:
            context = build_repair_context(material, raw_annotation, initial_material,initial.model_dump(mode="json"))
            repair_prompt=annotation_prompt(material,repair_context=context)
        checked, compiled, mapping = stage_response(repair_prompt,repair_client,lambda value:compile_response(value,material))
        result["material"]=deepcopy(material)
        result.update(raw_annotation=checked, selected="repair", repair={"status": "complete"})
        result["stage"] = "final_review"
        final_material = prepare_review_material(material, checked)
        final = stage_response(build_prompt(final_material), review_client,
                               lambda value: validate_response(value, final_material))
        result["final_review"] = final.model_dump(mode="json")
        result.update(status="repair_limit" if final.findings else "review_passed",
                      reason="Issues remain after one repair; no further repair is attempted." if final.findings else "Re-review raised no material issue after one repair.")
    except SemanticFailure as error:
        result.update(status="semantic_failure", reason=error.reason, failure=error.failure)
    except KeyboardInterrupt:
        result.update(status="interrupted", reason="User interrupted; no later call was started.")
    except Exception as error:
        result.update(status="execution_error", reason=f"{type(error).__name__}: {error}")
    return result


def prepare_refinement_run(input, analysis, material, raw_annotation, *, run_dir,
                           provenance, config=None, secrets=(), upstream_run=None):
    """Reference accepted inputs, or freeze one explicitly authored candidate."""
    from skillflow.propagation.annotation.inputs import write_material_parts
    from skillflow.propagation.annotation.loading import load_annotation_run
    directory = checked_run_path(run_dir)
    material = checked_material(material)
    compile_response(raw_annotation, material)
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("Candidate reconstruction provenance is required")
    public, writer = _config(config), ArtifactWriter(tuple(secrets))
    for value in (material, raw_annotation, provenance):
        if writer.clean(value) != value:
            raise ValueError("A credential overlaps refinement input")
    reference = None
    if upstream_run is not None:
        origin = checked_run_path(upstream_run)
        if directory == origin or directory.is_relative_to(origin) or origin.is_relative_to(directory):
            raise ValueError("Refinement cannot overlap its accepted annotation run")
        loaded = load_annotation_run(origin)
        if (canonical_sha256(loaded["material"]) != canonical_sha256(material)
                or canonical_sha256(loaded["raw_annotation"]) != canonical_sha256(raw_annotation)):
            raise RunIdentityError("Refinement differs from the accepted upstream candidate")
        reference = make_run_reference(directory, origin)
    else:
        source_path, analysis_path = checked_run_path(input), checked_run_path(analysis)
        if source_path.is_dir() and (directory.is_relative_to(source_path) or source_path.is_relative_to(directory)):
            raise ValueError("Refinement directory must not overlap the Skill input")
        if analysis_path.is_relative_to(directory):
            raise ValueError("Analysis input must be outside the new refinement run")
        actual = _json_object(analysis_path.read_text(encoding="utf-8-sig"))
        if canonical_sha256(actual.get("cfg", actual)) != canonical_sha256(material["cfg"]):
            raise RunIdentityError("Selected analysis differs from supplied actual CFG")
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise RunIdentityError("Prepare requires a new or empty refinement directory")
        if reference is None:
            freeze_input(source_path, directory, writer)
            _, source, _ = read_snapshot(directory)
            if source != material["source"]:
                raise RunIdentityError("Frozen readable source differs from annotation material")
            write_material_parts(directory, material, writer, include_source=False, authored_task=True)
            writer.json(directory / "inputs/candidate.json", raw_annotation)
        writer.json(directory / "inputs/provenance.json", provenance)
        from skillflow.propagation.annotation.inputs import resolve_task_owner
        task_reference = None if reference is None else make_run_reference(directory,resolve_task_owner(upstream_run))
        manifest = _seal({"identity": IDENTITY, "schema_version": FORMAT_VERSION,
                         "created_at": now(), "run_id": directory.name,
                         "config": public, "implementation": implementation_provenance(),
                         "upstream": reference, "task_run_ref": task_reference,
                         "task_origin": "authored_fixture" if reference is None else "independent_extraction",
                         "material_sha256": canonical_sha256(material),
                         "candidate_sha256": canonical_sha256(raw_annotation),
                         "files": _files(directory), "preparation_status": "ready",
                         "policy": POLICY})
        writer.json(directory / "manifest.json", manifest)
    return manifest


def _verify(directory, config, *, check_implementation=True):
    from skillflow.propagation.annotation.inputs import load_prepared_material
    from skillflow.propagation.annotation.loading import load_annotation_run
    directory = checked_run_path(directory)
    manifest = _json_object(checked_run_path(directory / "manifest.json").read_bytes().decode("utf-8"))
    _unseal(manifest)
    if (manifest.get("identity") != IDENTITY or type(manifest.get("schema_version")) is not int
            or manifest["schema_version"] != FORMAT_VERSION
            or canonical_sha256(manifest.get("policy")) != canonical_sha256(POLICY)):
        raise RunIdentityError("Unsupported annotation refinement run")
    if check_implementation and manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Refinement implementation identity changed")
    if manifest["config"] != _config(config) or manifest["files"] != _files(directory):
        raise RunIdentityError("Refinement configuration or frozen inputs changed")
    material = load_prepared_material(directory)
    if manifest["upstream"] is None:
        raw = _json_object(checked_run_path(directory / "inputs/candidate.json").read_bytes().decode("utf-8"))
    else:
        upstream = load_annotation_run(resolve_run_reference(directory, manifest["upstream"]))
        raw = upstream["raw_annotation"]
        if canonical_sha256(upstream["material"]) != canonical_sha256(material):
            raise RunIdentityError("Refinement material differs from accepted upstream annotation")
    if (canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(raw) != manifest["candidate_sha256"]):
        raise RunIdentityError("Refinement material or candidate identity changed")
    compile_response(raw, material)
    return manifest, material, raw


def load_refinement_inputs(run_dir):
    """Validate the prepared owner and candidate without replaying its stages."""
    directory = checked_run_path(run_dir)
    manifest, material, raw = _verify(directory, read_json(directory / "manifest.json")["config"],
                                      check_implementation=False)
    return {"manifest": manifest, "material": material, "raw_annotation": raw,
            "provenance": _json_object(checked_run_path(directory / "inputs/provenance.json").read_bytes().decode("utf-8"))}


def _counts(result):
    counts = {"logical_calls": 0, "http_attempts": 0, "http_retries": 0,
              "stage_calls": 0, "structural_corrections": 0, "json_normalizations": 0}
    for name in ("initial_review", "task_revision", "repair", "final_review"):
        for key in counts:
            counts[key] += (result.get(name) or {}).get("counts", {}).get(key, 0)
    return counts


def result_snapshot(directory, result):
    """Persist decisions and exact stage receipts, never stage business output."""
    directory = checked_run_path(directory)
    snapshot = deepcopy(result)
    for field, folder in (("initial_review", "initial-review"), ("task_revision", "task-revision"), ("repair", "repair"),
                          ("final_review", "final-review")):
        stage = result.get(field)
        if stage is None:
            continue
        snapshot[field] = {
            "path": folder,
            "manifest_sha256": sha_file(checked_run_path(directory / folder / "manifest.json")),
            "result_sha256": sha_file(checked_run_path(directory / folder / "result.json")),
            "status": stage["status"], "reason": stage["reason"],
            "counts": deepcopy(stage["counts"]),
        }
    return snapshot


def _save(directory, result, writer, replay=False):
    output = checked_run_path(directory / "replay" if replay else directory)
    writer.json(checked_run_path(output / "result.json"), _seal(result_snapshot(directory, result)))
    lines = ["# One-repair joint annotation refinement", "", f"Status: `{result['status']}`; stage: `{result['stage']}`", "",
             result["reason"], "", result["notice"], "",
             "Last structurally valid candidate: " + result["selected"], ""]
    links = []
    for field, folder, label in (("initial_review", "initial-review", "Initial review"),
                                  ("task_revision", "task-revision", "Isolated Task revision"),
                                  ("repair", "repair", "Complete repair"),
                                  ("final_review", "final-review", "Independent re-review")):
        stage = result.get(field)
        if stage:
            prefix = "../" if replay else ""
            lines += [f"- {label}: `{stage['status']}`; [Stage report]({prefix}{folder}/report.md)", ""]
            page = "report.md" if field == "repair" else "report.html"
            links.append(f"<li>{label}: {escape(stage['status'])} · <a href='{prefix}{folder}/{page}'>Stage report</a></li>")
            for finding in stage.get("resolved_findings", []):
                lines += ["  " + finding["explanation"], ""]
    writer.text(checked_run_path(output / "report.md"), "\n".join(lines))
    writer.text(checked_run_path(output / "report.html"), "<!doctype html><html lang='en'><meta charset='utf-8'><title>One-repair annotation refinement</title>"
                "<style>body{max-width:1000px;margin:40px auto;font:16px/1.8 system-ui}p{white-space:pre-wrap}</style><body>"
                f"<h1>One-repair joint annotation refinement</h1><p><b>{escape(result['status'])}</b> · {escape(result['stage'])}</p>"
                f"<p>{escape(result['reason'])}</p><p>{escape(result['notice'])}</p><ul>{''.join(links)}</ul>"
                "<p><a href='result.json'>Full refinement result</a></p></body></html>")


def run_refinement(run_dir, *, review_client=None, repair_client=None,
                   review_client_factory=None, repair_client_factory=None,
                   task_repair_client=None, task_repair_client_factory=None,
                   config=None, env_file=None, secrets=(), stop_event=None,
                   replay=False, progress=None):
    """Run or replay with strict producer implementation identity."""
    return _run_refinement(run_dir, review_client=review_client, repair_client=repair_client,
        review_client_factory=review_client_factory, repair_client_factory=repair_client_factory,
        task_repair_client=task_repair_client,task_repair_client_factory=task_repair_client_factory,
        config=config, env_file=env_file, secrets=secrets, stop_event=stop_event, replay=replay, progress=progress)


def _run_refinement(run_dir, *, review_client=None, repair_client=None,
                   review_client_factory=None, repair_client_factory=None,
                   task_repair_client=None, task_repair_client_factory=None,
                   config=None, env_file=None, secrets=(), stop_event=None,
                   replay=False, progress=None, read_only=False):
    """Resume accepted stages; offline replay never creates an online client."""
    from skillflow.propagation.annotation import runner as annotation_runner
    from skillflow.propagation.annotation.inputs import load_prepared_material
    from skillflow.propagation.annotation.requests import build_repair_context, load_repair_context
    if read_only and not replay:
        raise ValueError("Read-only verification requires saved-response replay")
    directory = checked_run_path(run_dir)
    if replay and any(x is not None for x in (review_client, repair_client, review_client_factory, repair_client_factory, task_repair_client, task_repair_client_factory, env_file)):
        raise ValueError("Offline refinement replay does not accept online configuration")
    if review_client is not None and review_client_factory is not None:
        raise ValueError("Inject only one review client or factory")
    if repair_client is not None and repair_client_factory is not None:
        raise ValueError("Inject only one repair client or factory")
    config = read_json(directory / "manifest.json")["config"] if config is None else config
    writer, stopping = ArtifactWriter(tuple(secrets)), stop_event or Event()
    with (nullcontext() if read_only else exclusive_run(directory)):
        manifest, material, raw = _verify(directory, config, check_implementation=not read_only)
        config = manifest["config"]
        existing = _unseal(read_json(directory / "result.json")) if (directory / "result.json").exists() else None
        if existing is not None and existing["status"] != "interrupted" and not replay:
            # A terminal parent decision is verified from saved child receipts.
            # In particular, a prepared request whose client factory failed is
            # not an invitation to create that client again on continuation.
            # Interrupted runs still resume normally from accepted responses.
            replay = True
            review_client = repair_client = task_repair_client = None
            review_client_factory = repair_client_factory = task_repair_client_factory = None
            env_file = None
        result = _result()
        result.update(run_id=manifest["run_id"], material_sha256=manifest["material_sha256"])
        provenance = read_json(directory / "inputs/provenance.json")
        point = "before_initial"
        def stop(where):
            nonlocal point
            point = where
            if stopping.is_set() or (replay and existing and existing["status"] == "interrupted"
                                     and existing.get("interrupt_point") == where):
                raise KeyboardInterrupt("User interrupted; retain started stages and do not start later calls.")
        def review_stage(folder, candidate, origin, *, accepted_run=None):
            from skillflow.propagation.review import runner as reviews
            target = directory / folder
            if not (target / "manifest.json").exists():
                if replay:
                    raise RunIdentityError("Replay requires the previously prepared review stage")
                if accepted_run is not None:
                    reviews.prepare_run(accepted_run, run_dir=target, config=config, secrets=secrets)
                else:
                    prepare_candidate_run(material, candidate, run_dir=target, provenance=origin,
                                          config=config, secrets=secrets, upstream_run=directory)
            stage_manifest, stage_material, _ = reviews._verify(target, config, check_implementation=not read_only)
            expected_material = prepare_review_material(material, candidate)
            expected_upstream = make_run_reference(target, accepted_run if accepted_run is not None else directory)
            if (canonical_sha256(stage_material) != canonical_sha256(expected_material)
                    or stage_manifest["upstream"] != expected_upstream
                    or (accepted_run is not None and stage_manifest["candidate_origin"] != "accepted_annotation")
                    or (accepted_run is None and stage_manifest["authored_metadata"] != origin)):
                raise RunIdentityError("Review stage no longer corresponds to current candidate")
            if read_only:
                from skillflow.propagation.review.runner import load_review_run
                return load_review_run(target)["result"]
            return run_review(target, client=review_client, client_factory=review_client_factory,
                              config=config, env_file=env_file, secrets=secrets, stop_event=stopping,
                              replay=replay, progress=progress)
        def fail(stage):
            result.update(status=stage["status"], reason=stage["reason"])
        try:
            stop("before_initial")
            accepted = (resolve_run_reference(directory, manifest["upstream"])
                        if manifest["upstream"] is not None else None)
            result["initial_review"] = review_stage("initial-review", raw, provenance, accepted_run=accepted)
            initial = result["initial_review"]
            if initial["status"] != "complete":
                fail(initial)
            elif not initial["review"]["findings"]:
                result.update(status="review_passed", reason="Initial review raised no material issue; repair was not called.")
            else:
                stop("after_initial")
                result["stage"] = "repair"
                from skillflow.propagation.review.models import ReviewResponse, task_objections
                from skillflow.propagation.annotation.inputs import resolve_task_owner,resolve_material_owner
                from skillflow.task.runner import prepare_task_run,run_task,load_task_run
                objections=task_objections(ReviewResponse.model_validate(initial["review"]))
                task_run=None
                context=None
                if objections:
                    result["stage"]="task_revision"
                    task_run=directory/"task-revision"
                    if not (task_run/"manifest.json").exists():
                        if replay: raise RunIdentityError("Missing recorded source-only Task revision")
                        prepare_task_run(task_run,source_owner=resolve_material_owner(directory),
                            user_request=material["user_request"],config=config,secrets=secrets,
                            revision={"previous_task":material["task"],"objections":objections})
                    # Reconstruct the source-only feedback and validate its exact identity.
                    from skillflow.task.runner import _verify as verify_task
                    from skillflow.task.material import validate_revision,prepare_task_material
                    task_manifest,_,_=verify_task(task_run,config=config,check_implementation=not read_only)
                    expected_revision=validate_revision({"previous_task":material["task"],"objections":objections},
                        prepare_task_material(material["source"],user_request=material["user_request"]))
                    if task_manifest["revision_sha256"]!=canonical_sha256(expected_revision):
                        raise RunIdentityError("Task revision differs from source-only review objections")
                    stop("before_task_revision")
                    # Once a child starts, replay must hydrate its saved receipt
                    # before reproducing an interruption within that child.
                    point = "during_task_revision"
                    provider=None
                    task_factory=task_repair_client_factory
                    if not replay and task_repair_client is None and task_factory is None:
                        def provider(call_writer):
                            factory,extra=streaming_factory(config,env_file=env_file)
                            call_writer.secrets=tuple(set(call_writer.secrets)|set(extra))
                            return factory
                    revised=run_task(task_run,client=task_repair_client,client_factory=task_factory,
                        factory_provider=provider,config=config,secrets=secrets,stop_event=stopping,
                        replay=replay,read_only=read_only,progress=progress)
                    result["task_revision"]=revised
                    if revised["status"]!="complete":
                        fail(revised)
                        if revised["status"]=="interrupted": raise KeyboardInterrupt(revised["reason"])
                        raise _TaskRevisionFailure()
                    from skillflow.propagation.material import prepare_material
                    material=prepare_material(material["source"],material["cfg"],task_baseline=revised["task"],
                                              user_request=material["user_request"])
                    stop("after_task_revision")
                else:
                    review_material=prepare_review_material(material,raw)
                    context=build_repair_context(material,raw,review_material,initial["review"])
                    task_run=resolve_task_owner(directory) if manifest.get("task_run_ref") is not None else None
                target=directory/"repair"
                result["stage"]="repair"
                if not (target/"manifest.json").exists():
                    if replay: raise RunIdentityError("Missing recorded complete annotation repair")
                    annotation_runner.prepare_run(None,None,run_dir=target,config=config,secrets=secrets,
                        repair_context=context,upstream_run=directory,task_run=task_run)
                if load_prepared_material(target)!=material:
                    raise RunIdentityError("Rebuilt annotation uses a different Task or frozen source")
                if context is not None and load_repair_context(target,material=material)!=context:
                    raise RunIdentityError("Annotation repair feedback changed")
                stop("before_repair")
                point = "during_repair"
                if read_only:
                    from skillflow.propagation.annotation.loading import load_annotation_attempt
                    result["repair"]=load_annotation_attempt(target)["result"]
                else:
                    factory=repair_client_factory
                    provider=None
                    if not replay and repair_client is None and factory is None:
                        def provider(call_writer):
                            selected,extra=streaming_factory(config,env_file=env_file)
                            call_writer.secrets=tuple(set(call_writer.secrets)|set(extra))
                            return selected
                    result["repair"]=annotation_runner.run_annotation(target,client=repair_client,
                        client_factory=factory,factory_provider=provider,config=config,secrets=secrets,
                        stop_event=stopping,replay=replay,progress=progress)
                repaired=result["repair"]
                if repaired["status"]!="complete":
                    fail(repaired)
                    if repaired["status"]=="interrupted": raise KeyboardInterrupt(repaired["reason"])
                else:
                    candidate=read_json(target/"audit/raw-annotation.json")
                    compile_response(candidate,material)
                    result["selected"]="repair"
                    stop("after_repair")
                    result["stage"]="final_review"
                    origin={"kind":"accepted_repair","raw_sha256":canonical_sha256(candidate)}
                    result["final_review"]=review_stage("final-review",candidate,origin,accepted_run=target)
                    final=result["final_review"]
                    if final["status"]!="complete": fail(final)
                    elif final["review"]["findings"]:
                        result.update(status="repair_limit",reason="Issues remain after the single semantic repair round.")
                    else:
                        result.update(status="review_passed",reason="Fresh full-chain review raised no material issue after one repair.")
        except _TaskRevisionFailure:
            pass
        except RunIdentityError:
            raise
        except _LocalPreparationFailure as error:
            result.update(status="execution_error", reason=error.failure["reason"],
                          local_failure=error.failure)
        except KeyboardInterrupt as error:
            result.update(status="interrupted", reason=writer.clean(str(error)), interrupt_point=point)
        except SemanticFailure as error:
            result.update(status="semantic_failure", reason=writer.clean(error.reason), failure=writer.clean(error.failure))
        except Exception as error:
            result.update(status="execution_error", reason=writer.clean(f"{type(error).__name__}: {error}"))
        result["counts"] = _counts(result)
        if (existing and (replay or existing["status"] != "interrupted")
                and canonical_sha256(existing) != canonical_sha256(result_snapshot(directory, result))):
            raise RunIdentityError("Refinement replay/continuation differs from the saved decision")
        if not read_only:
            _save(directory, result, writer, replay)
        return result


def replay_refinement(run_dir):
    return run_refinement(run_dir, replay=True)


def load_refinement_run(run_dir):
    """Verify stages and selection read-only; continuation still requires source identity."""
    from skillflow.propagation.annotation.loading import _read
    from skillflow.propagation.annotation.inputs import load_prepared_material
    from skillflow.propagation.review.runner import _readonly_inventory
    directory = checked_run_path(run_dir)
    before = _readonly_inventory(directory)
    manifest = _read(directory / "manifest.json")
    saved = _unseal(_read(directory / "result.json"))
    producer = manifest.get("implementation", {})
    if (not producer.get("files") or canonical_sha256(producer["files"]) != producer.get("sha256")):
        raise RunIdentityError("Saved refinement producer identity is invalid")
    result = _run_refinement(directory, replay=True, read_only=True)
    if (canonical_sha256(result_snapshot(directory, result)) != canonical_sha256(saved)
            or _readonly_inventory(directory) != before):
        raise RunIdentityError("Saved refinement decision or files differ from checked stages")
    prepared = load_refinement_inputs(directory)
    candidate = (_read(directory / "repair/audit/raw-annotation.json") if result["selected"] == "repair"
                 else prepared["raw_annotation"])
    return {"manifest": manifest, "result": result, "selected": result["selected"],
            "raw_annotation": candidate,
            "material": (load_prepared_material(directory / "repair") if result["selected"] == "repair" else prepared["material"]),
            "upstream_identity": {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
                                  "implementation": producer, "files": before}}


class _LocalPreparationFailure(Exception):
    def __init__(self, failure):
        self.failure = deepcopy(failure)
        super().__init__(failure["reason"])


class _TaskRevisionFailure(Exception):
    """Stop the single repair round after a recorded source-only failure."""
