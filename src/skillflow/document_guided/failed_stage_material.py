"""Source-bound evidence for a rejected stage, never an accepted stage value."""
from copy import deepcopy
import re

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.json_normalization import normalize_response
from skillflow.common.recording import (SavedResponseClient, canonical_sha256, read_json,
                                       sha_file, validated_trace, verify_request_identity)
from skillflow.common.structural_correction import ResponseChain
from skillflow.common.upstream import checked_run_path, resolve_run_reference
from .online import STEP_IDENTITY, _correction_strategy, checked_manifest, file_reference, read, resolve_file, scoped_dependencies


IDENTITY = "skillflow-failed-stage-material-v1"
STAGES = frozenset({"task", "flow", "graph", "processing", "task-correspondence", "sensitivity"})


def _checked_owner(run, owner, stage, attempt, files):
    """Verify ownership and frozen bytes, without validating any stage answer."""
    from .runner import IDENTITY as GUIDED_IDENTITY, SOURCE_IDENTITY
    guided = checked_manifest(run, GUIDED_IDENTITY)
    source_owner = run / "source"
    checked_manifest(source_owner, SOURCE_IDENTITY)
    source = read_snapshot(source_owner)[1]
    if files != {"skill/" + row["path"]: row["content"] for row in source["files"]}:
        raise ValueError("Failed-stage source files differ from this guided run's frozen source")
    revised = attempt.startswith("revision")
    if stage == "task":
        from skillflow.task.runner import verify_task_prepared
        from .fragments import fragment_correction_strategy
        manifest = verify_task_prepared(owner, config=guided["config"])
        if (resolve_run_reference(owner, manifest["source_owner"]) != source_owner
                or manifest["source_sha256"] != source["source_sha256"]):
            raise ValueError("Failed Task belongs to another source owner")
        return manifest, (owner / "inputs/prompt.txt").read_bytes().decode("utf-8"), (
            None if manifest["policy"].get("allow_cannot_assess", True)
            else fragment_correction_strategy("task"))
    manifest = checked_manifest(owner, STEP_IDENTITY)
    from .graph_steps import FACTS, UPDATES, revision_paths
    expected_kind = {"flow": "flow_document", "graph": UPDATES if revised else FACTS}.get(stage, stage + "_fragment")
    if manifest["kind"] != expected_kind or manifest["config"] != guided["config"]:
        raise ValueError("Failed stage kind or configuration differs from its guided owner")
    expected = {"source_owner": source_owner}
    dependencies = [source_owner / "manifest.json"]
    from .accepted_upstream import load_accepted_upstream
    inherited = load_accepted_upstream(run)
    if stage == "graph":
        dependencies.append(inherited.get("flow", {}).get("path", run / "steps/flow/result.json"))
        if revised:
            paths = revision_paths(run)
            expected["graph_repair_path"] = paths[-1]
            dependencies.extend(paths)
    elif stage != "flow":
        graph = run / "graph" / ("revision.json" if revised and (run / "graph/revision.json").is_file() else "initial.json")
        expected["cfg_path"] = graph
        upstream = (inherited.get("flow", {}).get("step", run / "steps/flow") if stage == "processing" else run / "steps" /
            ("revision-processing" if revised and (run / "steps/revision-processing/manifest.json").is_file() else "processing"))
        dependencies.extend((graph, upstream / "result.json"))
        if stage != "processing":
            expected["processing_step"] = upstream
        if stage == "task-correspondence":
            task = (run / "revision/task" if revised and (run / "revision/task/manifest.json").is_file()
                    else inherited.get("task", {}).get("owner", run / "task"))
            expected["task_run"] = task
            dependencies.append(task / "task.json")
    context = manifest.get("context", {})
    scope_key = stage + "_scope_path"
    scoped = revised and stage in {"processing", "sensitivity", "task-correspondence"} and scope_key in context
    if scoped:
        paths = scoped_dependencies(run, stage)
        expected[scope_key] = paths[-1]
        dependencies.extend(paths)
    if set(context) != set(expected):
        raise ValueError("Failed stage has unexpected source or dependency context")
    for key, target in expected.items():
        resolved = resolve_file(owner, context[key]) if key in {"cfg_path", "graph_repair_path", scope_key} else resolve_run_reference(owner, context[key])
        if resolved != target:
            raise ValueError("Failed stage belongs to another source or dependency owner")
    if [resolve_file(owner, ref) for ref in manifest["dependencies"]] != dependencies:
        raise ValueError("Failed stage dependencies differ from this guided phase")
    strategy = None if scoped else _correction_strategy(manifest["kind"], {"files": files})
    return manifest, (owner / "prompt.txt").read_bytes().decode("utf-8"), strategy


def capture_failed_stage(run, *, stage, attempt, files, failure):
    """Read already-validated current-run receipts; do not replay or validate IR.

    ResponseChain has verified the immutable requests before reporting failure.
    Bind its terminal rejected candidate and all original attempt identities so
    a review or shared repair can name the failure without promoting that value.
    """
    if stage not in STAGES or failure.get("status") not in {"structural_failure", "semantic_failure"}:
        raise ValueError("Only an actual rejected semantic stage has failure material")
    run = checked_run_path(run)
    allowed = {stage} | ({"revision/task" if stage == "task" else "revision-" + stage} if stage != "flow" else set())
    if attempt not in allowed:
        raise ValueError("Failed-stage attempt does not belong to its semantic stage")
    owner = checked_run_path(run / attempt if stage == "task" else run / "steps" / attempt)
    manifest, base_prompt, strategy = _checked_owner(run, owner, stage, attempt, files)
    prefix = "calls/task" if stage == "task" else "calls"
    chain_path = owner / prefix / "chain.json"
    outcome, chain = read(owner / "result.json"), read(chain_path)
    scoped = stage + "_scope_path" in manifest.get("context", {})
    budget = 0 if scoped or (stage == "graph" and attempt == "revision-graph") else 1
    if (outcome.get("status") != failure["status"] or chain.get("accepted_call") is not None
            or not chain.get("attempts") or chain.get("max_corrections") != budget):
        raise ValueError("Failed-stage material requires the exact rejected terminal chain")
    if (outcome.get("response_chain") != chain if stage == "task" else
            outcome.get("response_chain_sha256") != canonical_sha256(chain)):
        raise ValueError("Failed-stage terminal result does not bind its exact response chain")
    request_kind = manifest["request_kind"] if stage == "task" else "document_guided_" + manifest["kind"]
    # Constructor-only verification checks immutable chain schema, call order,
    # correction budget and recorded inventory. It never invokes validate/run.
    ResponseChain(owner, prefix=prefix, base_prompt=base_prompt, request_kind=request_kind,
        config=manifest["config"], writer=ArtifactWriter(()), validate=None,
        replay=True, read_only=True, max_corrections=budget, correction_strategy=strategy)
    attempts, references = [], {
        "run_manifest": file_reference(run, run / "manifest.json"),
        "source_manifest": file_reference(run, run / "source/manifest.json"),
        "stage_manifest": file_reference(run, owner / "manifest.json"),
        "stage_result": file_reference(run, owner / "result.json"),
        "response_chain": file_reference(run, chain_path)}
    last_candidate = last_response = last_validation = None
    previous = None
    for ordinal, row in enumerate(chain["attempts"], 1):
        directory = (owner / row["call"]).resolve()
        if not directory.is_relative_to(owner.resolve()):
            raise ValueError("Failed-stage call escapes its actual stage owner")
        validation, call, request = (read(directory / name) for name in
                                     ("validation.json", "call.json", "request.json"))
        response = read_json(directory / "response.json")
        prompt = (directory / "prompt.txt").read_bytes().decode("utf-8")
        expected_request = {"version": chain["version"], "index": ordinal,
            "base_request_kind": request_kind, "kind": request_kind if ordinal == 1 else "structural_correction",
            "base_prompt_sha256": canonical_sha256(base_prompt), "prompt_sha256": canonical_sha256(prompt),
            "previous": previous}
        if strategy is not None:
            expected_request["correction_strategy"] = strategy.identity
        if request != expected_request or ordinal == 1 and prompt != base_prompt:
            raise ValueError("Failed-stage request does not bind its actual owner, prompt and predecessor")
        trace = validated_trace(directory / "transport.json")
        if (len(trace) != 1 or trace[0].get("status") != "complete"
                or trace[0].get("recording_failed") or call.get("recording_failed")):
            raise ValueError("Failed-stage response requires one intact completed transport record")
        saved_response = SavedResponseClient(directory, ArtifactWriter(())).complete(prompt)
        verify_request_identity(directory, manifest["config"], prompt=prompt)
        if canonical_sha256(saved_response) != canonical_sha256(response):
            raise ValueError("Failed-stage response file differs from its recorded transport response")
        if (row.get("call_sha256") != sha_file(directory / "call.json")
                or row.get("validation_sha256") != canonical_sha256(validation)
                or row.get("request_sha256") != canonical_sha256(request)
                or row.get("status") != validation.get("status")
                or call.get("status") != "complete" or call.get("response_rejected")
                or call.get("response_sha256") != canonical_sha256(response)
                or validation.get("response_sha256") != canonical_sha256(response)):
            raise ValueError("Failed-stage response, request, validation and chain bindings disagree")
        candidate, normalization = normalize_response(response)
        normalization_path = directory / "normalization.json"
        if (normalization_path.is_file() != (normalization is not None)
                or normalization is not None and read(normalization_path) != normalization
                or validation.get("normalization_sha256") != (
                    None if normalization is None else canonical_sha256(normalization))):
            raise ValueError("Failed-stage normalization evidence differs from the recorded response")
        merged = directory / "merged-candidate.json"
        if merged.is_file():
            candidate = read_json(merged)
        if validation.get("candidate_sha256") != canonical_sha256(candidate):
            raise ValueError("Failed-stage candidate differs from its rejected validation")
        record = {"ordinal": ordinal, "status": validation["status"], "validation": deepcopy(validation),
                  "validation_sha256": canonical_sha256(validation), "artifacts": {
            name: file_reference(run, directory / name) for name in
            ("request.json", "prompt.txt", "call.json", "transport.json", "response.json", "validation.json",
             "normalization.json", "merged-candidate.json") if (directory / name).is_file()}}
        attempts.append(record)
        last_candidate, last_response, last_validation = candidate, response, validation
        previous = {"call": row["call"], "response_sha256": canonical_sha256(response),
                    "validation_sha256": canonical_sha256(validation)}
    if last_validation["status"] not in {"structural_invalid", "semantic_failure"}:
        raise ValueError("Failed-stage terminal attempt is not a rejected candidate")
    material = {"attempt": attempt, "accepted": False, "artifacts": references,
        "attempts": attempts, "response": deepcopy(last_response),
        "candidate_source": "response" if last_candidate == last_response else "candidate",
        "validation": deepcopy(last_validation)}
    if last_candidate != last_response:
        material["candidate"] = deepcopy(last_candidate)
    return {"identity": IDENTITY, "stage": stage, "status": failure["status"],
        "source_sha256": canonical_sha256(files), "material": material,
        "material_sha256": canonical_sha256(material)}


def checked_structural_failure(evidence, *, stage, files):
    """Admission uses bound structural rejection, not network or capability gaps."""
    try:
        return _structural_failure_shape(evidence, stage=stage, files=files)
    except (TypeError, ValueError, KeyError):
        # Rehashed but malformed envelopes remain inadmissible evidence.
        return False


def _structural_failure_shape(evidence, *, stage, files):
    try:
        if (stage not in STAGES or not isinstance(evidence, dict) or evidence.get("identity") != IDENTITY
            or evidence.get("stage") != stage or evidence.get("status") != "structural_failure"
            or evidence.get("source_sha256") != canonical_sha256(files)
            or not isinstance(evidence.get("material"), dict)
            or evidence.get("material_sha256") != canonical_sha256(evidence["material"])):
            return False
    except (ValueError, TypeError):
        return False
    material = evidence["material"]
    validation = material.get("validation", {})
    attempts = material.get("attempts")
    artifacts = material.get("artifacts")
    if (material.get("accepted") is not False or not isinstance(validation, dict)
            or validation.get("status") != "structural_invalid" or not isinstance(attempts, list) or len(attempts) != 2
            or material.get("attempt") not in {stage, "revision/task" if stage == "task" else "revision-" + stage}
            or not isinstance(artifacts, dict) or set(artifacts) != {
                "run_manifest", "source_manifest", "stage_manifest", "stage_result", "response_chain"}):
        return False
    candidate_source = material.get("candidate_source")
    if (candidate_source not in {"response", "candidate"} or "response" not in material
            or (candidate_source == "candidate") != ("candidate" in material)):
        return False
    try:
        if (validation.get("response_sha256") != canonical_sha256(material["response"])
                or validation.get("candidate_sha256") != canonical_sha256(
                    material["response"] if candidate_source == "response" else material["candidate"])):
            return False
    except (TypeError, ValueError):
        return False
    references = list(artifacts.values())
    for ordinal, attempt in enumerate(attempts, 1):
        if (not isinstance(attempt, dict) or set(attempt) != {"ordinal", "status", "validation", "validation_sha256", "artifacts"}
                or type(attempt.get("ordinal")) is not int or attempt["ordinal"] != ordinal
                or attempt.get("status") != "structural_invalid" or not isinstance(attempt.get("artifacts"), dict)
                or not isinstance(attempt.get("validation"), dict)
                or attempt["validation"].get("status") != attempt["status"]
                or attempt.get("validation_sha256") != canonical_sha256(attempt["validation"])
                or not isinstance(attempt["validation"].get("diagnostics"), list)
                or not attempt["validation"]["diagnostics"]
                or not all(isinstance(row, dict) and all(isinstance(row.get(key), str)
                    for key in ("code", "path", "message")) for row in attempt["validation"]["diagnostics"])
                or not {"request.json", "prompt.txt", "call.json", "transport.json", "response.json", "validation.json"}
                    <= set(attempt["artifacts"])):
            return False
        references.extend(attempt["artifacts"].values())
    if attempts[-1]["validation"] != validation:
        return False
    if any(not isinstance(ref, dict) or set(ref) != {"path", "sha256"}
           or not isinstance(ref["path"], str) or not ref["path"]
           or not re.fullmatch(r"[0-9a-f]{64}", str(ref["sha256"])) for ref in references):
        return False
    diagnostics = validation.get("diagnostics")
    return isinstance(diagnostics, list) and bool(diagnostics) and all(
        isinstance(row, dict) and all(isinstance(row.get(key), str) for key in ("code", "path", "message"))
        for row in diagnostics)
