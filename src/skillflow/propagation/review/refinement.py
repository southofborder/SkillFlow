"""Bounded annotation refinement: review, at most one replacement, fresh review.

Only annotation candidates change. CFG and source are frozen once. This module
uses the existing recorded annotation and review runners, not another transport.
"""
from __future__ import annotations

from copy import deepcopy
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
from skillflow.common.recording import streaming_factory
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.source_evidence import _json_object
from skillflow.propagation.material import checked_material
from skillflow.propagation.annotation.services import compile_response
from skillflow.propagation.review.material import prepare_review_material
from skillflow.propagation.review.prompts import build_prompt
from skillflow.propagation.review.services import validate_response
from skillflow.propagation.review.runner import RunIdentityError
from skillflow.propagation.review.runner import _seal
from skillflow.propagation.review.runner import _unseal
from skillflow.propagation.review.runner import _config
from skillflow.propagation.review.runner import _files
from skillflow.propagation.review.runner import prepare_candidate_run
from skillflow.propagation.review.runner import run_review

IDENTITY = "skill-ir-annotation-refinement-v3"
FORMAT_VERSION = 3


def _result():
    return {"identity": IDENTITY, "schema_version": FORMAT_VERSION,
            "status": "interrupted", "stage": "initial_review", "reason": "尚未完成。",
            "initial_review": None, "repair": None, "final_review": None,
            "selected": "original", "counts": {"logical_calls": 0, "http_attempts": 0,
            "http_retries": 0}, "interrupt_point": None, "local_failure": None,
            "notice": "最多完整修复一次；审查未提出问题不等于语义正确性证明。"}


def refine_annotation(material, raw_annotation, *, review_client, repair_client):
    """Injected, in-memory service. Durable callers use run_refinement below."""
    from skillflow.propagation.annotation.requests import build_repair_context
    from skillflow.propagation.annotation.prompts import build_prompt as annotation_prompt
    material = checked_material(material)
    compile_response(raw_annotation, material)
    result = _result()
    result["raw_annotation"] = deepcopy(raw_annotation)
    try:
        initial_material = prepare_review_material(material, raw_annotation)
        result["counts"]["logical_calls"] += 1
        initial = validate_response(review_client.complete(build_prompt(initial_material)), initial_material)
        result["initial_review"] = initial.model_dump(mode="json")
        if not initial.findings:
            result.update(status="review_passed", reason="初审未发现实质问题；未调用修复。")
            return result
        result["stage"] = "repair"
        context = build_repair_context(material, raw_annotation, initial_material,
                                       initial.model_dump(mode="json"))
        result["counts"]["logical_calls"] += 1
        raw = _json_object(repair_client.complete(annotation_prompt(material, repair_context=context)))
        checked, compiled, mapping = compile_response(raw, material)
        result.update(raw_annotation=checked, selected="repair", repair={"status": "complete"})
        result["stage"] = "final_review"
        final_material = prepare_review_material(material, checked)
        result["counts"]["logical_calls"] += 1
        final = validate_response(review_client.complete(build_prompt(final_material)), final_material)
        result["final_review"] = final.model_dump(mode="json")
        result.update(status="repair_limit" if final.findings else "review_passed",
                      reason="一次修复后仍有明确问题；不再修复。" if final.findings else "一次修复后复审未发现实质问题。")
    except SemanticFailure as error:
        result.update(status="semantic_failure", reason=error.reason, failure=error.failure)
    except KeyboardInterrupt:
        result.update(status="interrupted", reason="用户中断；未启动后续调用。")
    except (ValueError, TypeError, KeyError) as error:
        result.update(status="invalid_response", reason=f"{type(error).__name__}: {error}")
    except Exception as error:
        result.update(status="execution_error", reason=f"{type(error).__name__}: {error}")
    return result


def prepare_refinement_run(input, analysis, material, raw_annotation, *, run_dir,
                           provenance, config=None, secrets=()):
    """Freeze current materials and explicit candidate authorship, without APIs.

    Historical candidates must be reconstructed and audited by the experiment;
    this entry point never calls a legacy loader or invents an accepted response.
    """
    directory = Path(run_dir).resolve()
    source_path, analysis_path = Path(input).resolve(), Path(analysis).resolve()
    if source_path.is_dir() and (directory.is_relative_to(source_path) or source_path.is_relative_to(directory)):
        raise ValueError("Refinement directory must not overlap the Skill input")
    if analysis_path.is_relative_to(directory):
        raise ValueError("Analysis input must be outside the new refinement run")
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("Candidate reconstruction provenance is required")
    material = checked_material(material)
    compile_response(raw_annotation, material)
    public, writer = _config(config), ArtifactWriter(tuple(secrets))
    for value in (material, raw_annotation, provenance):
        if writer.clean(value) != value:
            raise ValueError("A credential overlaps refinement input")
    actual = _json_object(analysis_path.read_text(encoding="utf-8-sig"))
    if actual.get("cfg", actual) != material["cfg"]:
        raise RunIdentityError("Selected analysis differs from supplied actual CFG")
    directory.mkdir(parents=True, exist_ok=True)
    with exclusive_run(directory):
        if any(p.name != ".runner.lock" for p in directory.iterdir()):
            raise RunIdentityError("Prepare requires a new or empty refinement directory")
        freeze_input(source_path, directory, writer)
        _, source, metadata = read_snapshot(directory)
        if source != material["source"]:
            raise RunIdentityError("Frozen readable source differs from annotation material")
        writer.json(directory / "inputs/analysis.json", {"cfg": material["cfg"]})
        writer.json(directory / "inputs/material.json", material)
        writer.json(directory / "inputs/candidate.json", raw_annotation)
        writer.json(directory / "inputs/provenance.json", provenance)
        manifest = _seal({"identity": IDENTITY, "schema_version": FORMAT_VERSION,
                         "created_at": now(), "run_id": directory.name,
                         "config": public, "implementation": implementation_provenance(),
                         "material_sha256": canonical_sha256(material),
                         "candidate_sha256": canonical_sha256(raw_annotation),
                         "files": _files(directory), "preparation_status": "ready",
                         "policy": {"max_repairs": 1, "max_logical_calls": 3,
                                    "automatic_resend_after_acceptance": False}})
        writer.json(directory / "manifest.json", manifest)
    return manifest


def _verify(directory, config):
    manifest = read_json(directory / "manifest.json")
    _unseal(manifest)
    if manifest.get("identity") != IDENTITY or manifest.get("schema_version") != FORMAT_VERSION:
        raise RunIdentityError("Unsupported annotation refinement run")
    if manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Refinement implementation identity changed")
    if manifest["config"] != _config(config) or manifest["files"] != _files(directory):
        raise RunIdentityError("Refinement configuration or frozen inputs changed")
    _, source, _ = read_snapshot(directory)
    material = checked_material(read_json(directory / "inputs/material.json"))
    raw = read_json(directory / "inputs/candidate.json")
    if (source != material["source"] or read_json(directory / "inputs/analysis.json") != {"cfg": material["cfg"]}
            or canonical_sha256(material) != manifest["material_sha256"]
            or canonical_sha256(raw) != manifest["candidate_sha256"]):
        raise RunIdentityError("Refinement source, graph or candidate identity changed")
    compile_response(raw, material)
    return manifest, material, raw


def _counts(result):
    counts = {"logical_calls": 0, "http_attempts": 0, "http_retries": 0}
    for name in ("initial_review", "repair", "final_review"):
        for key in counts:
            counts[key] += (result.get(name) or {}).get("counts", {}).get(key, 0)
    return counts


def _save(directory, result, writer, replay=False):
    output = directory / "replay" if replay else directory
    writer.json(output / "result.json", _seal(result))
    lines = ["# 一次联合标注修复", "", f"状态：`{result['status']}`；阶段：`{result['stage']}`", "",
             result["reason"], "", result["notice"], "",
             "最后结构有效候选：" + result["selected"], ""]
    links = []
    for field, folder, label in (("initial_review", "initial-review", "初审"),
                                  ("repair", "repair", "完整修复"),
                                  ("final_review", "final-review", "独立复审")):
        stage = result.get(field)
        if stage:
            prefix = "../" if replay else ""
            lines += [f"- {label}：`{stage['status']}`；[阶段报告]({prefix}{folder}/report.md)", ""]
            page = "report.md" if field == "repair" else "report.html"
            links.append(f"<li>{label}: {escape(stage['status'])} · <a href='{prefix}{folder}/{page}'>阶段报告</a></li>")
            for finding in stage.get("resolved_findings", []):
                lines += ["  " + finding["explanation"], ""]
    writer.text(output / "report.md", "\n".join(lines))
    writer.text(output / "report.html", "<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>一次标注修复</title>"
                "<style>body{max-width:1000px;margin:40px auto;font:16px/1.8 system-ui}p{white-space:pre-wrap}</style><body>"
                f"<h1>一次联合标注修复</h1><p><b>{escape(result['status'])}</b> · {escape(result['stage'])}</p>"
                f"<p>{escape(result['reason'])}</p><p>{escape(result['notice'])}</p><ul>{''.join(links)}</ul>"
                "<p><a href='result.json'>完整闭环结果</a></p></body></html>")


def run_refinement(run_dir, *, review_client=None, repair_client=None,
                   review_client_factory=None, repair_client_factory=None,
                   config=None, env_file=None, secrets=(), stop_event=None,
                   replay=False, progress=None):
    """Resume accepted stages; offline replay never creates an online client."""
    from skillflow.propagation.annotation import runner as annotation_runner
    from skillflow.propagation.annotation.requests import build_repair_context
    directory = Path(run_dir).resolve()
    if replay and any(x is not None for x in (review_client, repair_client, review_client_factory, repair_client_factory, env_file)):
        raise ValueError("Offline refinement replay does not accept online configuration")
    if review_client is not None and review_client_factory is not None:
        raise ValueError("Inject only one review client or factory")
    if repair_client is not None and repair_client_factory is not None:
        raise ValueError("Inject only one repair client or factory")
    config = read_json(directory / "manifest.json")["config"] if config is None else config
    writer, stopping = ArtifactWriter(tuple(secrets)), stop_event or Event()
    with exclusive_run(directory):
        manifest, material, raw = _verify(directory, config)
        config = manifest["config"]
        existing = _unseal(read_json(directory / "result.json")) if (directory / "result.json").exists() else None
        result = _result()
        result.update(run_id=manifest["run_id"], material_sha256=manifest["material_sha256"])
        provenance = read_json(directory / "inputs/provenance.json")
        point = "before_initial"
        def stop(where):
            nonlocal point
            point = where
            if stopping.is_set() or (replay and existing and existing["status"] == "interrupted"
                                     and existing.get("interrupt_point") == where):
                raise KeyboardInterrupt("用户中断；保留已开始阶段，不启动后续调用。")
        def review_stage(folder, candidate, origin):
            target = directory / folder
            if not (target / "manifest.json").exists():
                if replay:
                    raise RunIdentityError("Replay requires the previously prepared review stage")
                prepare_candidate_run(material, candidate, run_dir=target, provenance=origin,
                                      config=config, secrets=secrets)
            else:
                if (read_json(target / "inputs/candidate.json") != candidate
                        or read_json(target / "inputs/annotation-material.json") != material
                        or read_json(target / "inputs/provenance.json") != origin):
                    raise RunIdentityError("Review stage no longer corresponds to current candidate")
            return run_review(target, client=review_client, client_factory=review_client_factory,
                              config=config, env_file=env_file, secrets=secrets, stop_event=stopping,
                              replay=replay, progress=progress)
        def fail(stage):
            result.update(status=stage["status"], reason=stage["reason"])
        try:
            stop("before_initial")
            result["initial_review"] = review_stage("initial-review", raw, provenance)
            initial = result["initial_review"]
            if initial["status"] != "complete":
                fail(initial)
            elif not initial["review"]["findings"]:
                result.update(status="review_passed", reason="初审未发现实质问题；未调用修复。")
            else:
                stop("after_initial")
                result["stage"] = "repair"
                review_material = prepare_review_material(material, raw)
                context = build_repair_context(material, raw, review_material, initial["review"])
                target = directory / "repair"
                if not (target / "manifest.json").exists():
                    if replay:
                        raise RunIdentityError("Replay requires the previously prepared repair stage")
                    annotation_runner.prepare_run(directory / "inputs/package", directory / "inputs/analysis.json",
                                                  run_dir=target, config=config, secrets=secrets,
                                                  repair_context=context)
                elif (read_json(target / "inputs/repair-context.json") != context
                      or read_json(target / "inputs/material.json") != material):
                    raise RunIdentityError("Repair input or exact feedback context changed")
                stop("before_repair")
                repair_factory, repair_secrets = repair_client_factory, secrets
                if existing and existing.get("local_failure"):
                    if (target / annotation_runner.CALL_PATH / "call.json").exists():
                        raise RunIdentityError("A request appeared after a recorded local setup failure")
                    annotation_runner.verify_prepared(target, config=config, replay=True)
                    raise _LocalPreparationFailure(existing["local_failure"])
                if (not replay and repair_client is None and repair_factory is None
                        and not (target / annotation_runner.CALL_PATH / "call.json").exists()):
                    try:
                        repair_factory, loaded_secrets = streaming_factory(config, env_file=env_file)
                    except Exception as error:
                        raise _LocalPreparationFailure({"stage": "repair",
                            "reason": writer.clean(f"{type(error).__name__}: {error}")}) from error
                    repair_secrets = tuple(set(secrets) | set(loaded_secrets))
                result["repair"] = annotation_runner.run_annotation(target, client=repair_client,
                    client_factory=repair_factory, config=config,
                    secrets=repair_secrets, stop_event=stopping, replay=replay, progress=progress)
                repaired = result["repair"]
                if repaired["status"] != "complete":
                    fail(repaired)
                else:
                    candidate = read_json(target / "audit/raw-annotation.json")
                    compile_response(candidate, material)
                    result["selected"] = "repair"
                    stop("after_repair")
                    result["stage"] = "final_review"
                    origin = {"kind": "accepted_repair", "raw_sha256": canonical_sha256(candidate),
                              "repair_request_sha256": canonical_sha256(context)}
                    result["final_review"] = review_stage("final-review", candidate, origin)
                    final = result["final_review"]
                    if final["status"] != "complete":
                        fail(final)
                    elif final["review"]["findings"]:
                        result.update(status="repair_limit", reason="一次修复后仍有明确问题；已到修复上限。")
                    else:
                        result.update(status="review_passed", reason="一次修复后独立复审未发现实质问题。")
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
        if result["counts"]["logical_calls"] > 3:
            raise RunIdentityError("Refinement exceeded its logical call budget")
        if existing and (replay or existing["status"] != "interrupted") and existing != result:
            raise RunIdentityError("Refinement replay/continuation differs from the saved decision")
        _save(directory, result, writer, replay)
        return result


def replay_refinement(run_dir):
    return run_refinement(run_dir, replay=True)


class _LocalPreparationFailure(Exception):
    def __init__(self, failure):
        self.failure = deepcopy(failure)
        super().__init__(failure["reason"])
