"""Recorded fatal semantic-phase frontier, independent of worker completion order.

Only new, confirmed-ended request failures with no selected annotation use this
receipt. It never supplies a stage value or permits backend continuation.
"""
from copy import deepcopy

from skillflow.common.recording import SavedCallFailure, SavedResponseClient, canonical_sha256, sha_file, validated_trace
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.structural_correction import StructuralCorrectionLimitReached
from .online import file_reference, read, resolve_file, resolve_run_reference, run_step


IDENTITY = "skillflow-fatal-semantic-frontier-v3"
PATH = "audit/fatal-semantic-frontier.json"
_STEPS = {"flow", "graph", "processing", "task-correspondence", "sensitivity"}
_SEMANTIC_NAMES = {"task", "revision/task", *_STEPS, *("revision-" + name for name in _STEPS - {"flow"})}


def _owners(run):
    owners = {}
    for name in ("task", "revision/task", "review", "revision/review"):
        owner = run / name
        if (owner / "manifest.json").is_file():
            owners[name] = owner
    for path in sorted((run / "steps").glob("*/manifest.json")):
        name = path.parent.name
        if name not in _SEMANTIC_NAMES:
            raise ValueError("Fatal frontier has an unknown prepared semantic stage: " + name)
        owners[name] = path.parent
    return owners


def _inventory(run):
    result = {}
    for name, owner in sorted(_owners(run).items()):
        result[name] = {key: file_reference(run, owner / key) if (owner / key).is_file() else None
                       for key in ("manifest.json", "result.json", "execution-boundary.json")}
        result[name]["calls"] = {path.relative_to(owner).as_posix(): file_reference(run, path)
                                 for path in sorted((owner / "calls").rglob("*")) if path.is_file()}
    return result


def _recovery_inventory(run):
    paths = [*sorted((run / "audit/failed-stages").glob("*.json"))]
    decision = run / "audit/shared-repair-decision.json"
    if decision.is_file():
        paths.append(decision)
    return {path.relative_to(run).as_posix(): file_reference(run, path) for path in paths}


def _primary_failure(run, stage):
    from .runner import WRITER, _confirmed_request_failure, _failure_reason, _recorded_task_request_failure
    if not isinstance(stage, str):
        return None
    if stage in {"task", "revision/task"}:
        owner = run / stage
        if not (owner / "result.json").is_file():
            return None
        error = _recorded_task_request_failure(owner, read(owner / "result.json"))
        # The ordinary fatal Task path retains its independent result protocol
        # and reports its execution_error through this existing wrapper.
        return "RuntimeError: " + str(error) if error is not None else None
    if stage.removeprefix("revision-") not in _STEPS:
        return None
    owner = run / "steps" / stage
    chain_path = owner / "calls/chain.json"
    if not chain_path.is_file():
        return None
    chain = read(chain_path)
    if chain.get("accepted_call") is not None or not chain.get("attempts"):
        return None
    row = chain["attempts"][-1]
    call = (owner / row["call"]).resolve()
    if not call.is_relative_to(owner.resolve()) or not (call / "call.json").is_file():
        raise ValueError("Fatal frontier call is outside its stage or missing")
    if row.get("call_sha256") != sha_file(call / "call.json"):
        raise ValueError("Fatal frontier failed call differs from its bound chain")
    if not (call / "transport.json").is_file():
        raise ValueError("Fatal frontier failed call is missing its transport receipt")
    record, trace = read(call / "call.json"), validated_trace(call / "transport.json")
    if (record.get("status") != "error" or record.get("recording_failed") or record.get("response_rejected")
            or len(trace) != 1 or trace[0].get("status") != "error" or trace[0].get("recording_failed")
            or trace[0].get("error_type") != record.get("error_type")
            or trace[0].get("error") != record.get("error") or trace[0].get("prompt") != record.get("prompt")):
        raise ValueError("Fatal frontier failed call and transport disagree")
    try:
        SavedResponseClient(call, WRITER).complete((call / "prompt.txt").read_bytes().decode("utf-8"))
    except SavedCallFailure as error:
        return _failure_reason(error) if _confirmed_request_failure(error) else None
    return None


def requires_fatal_frontier(run, result):
    """The new policy must not silently fall back if its receipt is removed."""
    if (result.get("status") != "failed" or result.get("selected_annotation") is not None
            or any((run / name).exists() for name in ("propagation", "doe"))
            or any("assembly" in name for name in result.get("stages", {}))):
        return False
    reason = _primary_failure(run, result["stage"])
    if reason is None or reason != result.get("reason"):
        return False
    return True


def capture_fatal_frontier(run, result, *, writer, error):
    """Freeze actual owners after worker shutdown; never rewrite an old receipt."""
    from .runner import _confirmed_request_failure
    if result.get("stage") not in {"task", "revision/task"} and not _confirmed_request_failure(error):
        return None
    if not requires_fatal_frontier(run, result):
        return None
    if any((run / name).exists() for name in ("selection.json", "graph/selected.json",
                                             "annotation/manifest.json", "revision/annotation/manifest.json")):
        raise ValueError("Fatal frontier without a selected bundle contains selected annotation artifacts")
    receipt = {"identity": IDENTITY, "guided_state": deepcopy(result),
               "run_manifest": file_reference(run, run / "manifest.json"),
               "owners": _inventory(run),
               "recovery": _recovery_inventory(run),
               "graphs": {name: file_reference(run, run / "graph" / (name + ".json"))
                          for name in ("initial", "revision") if (run / "graph" / (name + ".json")).is_file()}}
    path = run / PATH
    if path.exists():
        if read(path) != receipt:
            raise ValueError("Fatal semantic frontier already exists with different evidence")
    else:
        writer.json(path, receipt)
    return file_reference(run, path)


def _check_step_binding(run, name, owner, owners, inherited=None):
    """A valid standalone step must also belong to this guided dependency graph."""
    manifest = read(owner / "manifest.json")
    inherited = inherited or {}
    key, revised = name.removeprefix("revision-"), name.startswith("revision-")
    expected = {"source_owner": (run / "source").resolve()}
    dependencies = [(run / "source/manifest.json").resolve()]
    if key == "graph":
        dependencies.append(inherited.get("flow", {}).get("path", run / "steps/flow/result.json").resolve())
        if revised:
            from .graph_steps import revision_paths
            paths = tuple(path.resolve() for path in revision_paths(run))
            expected["graph_repair_path"] = paths[-1]
            dependencies.extend(paths)
    elif key != "flow":
        cfg = run / "graph" / ("revision.json" if revised and "revision-graph" in owners else "initial.json")
        expected["cfg_path"] = cfg.resolve()
        upstream = (inherited.get("flow", {}).get("step", run / "steps/flow") if key == "processing" else
                    run / "steps" / ("revision-processing" if revised and "revision-processing" in owners else "processing"))
        dependencies.extend((cfg.resolve(), (upstream / "result.json").resolve()))
        if key != "processing":
            expected["processing_step"] = upstream.resolve()
        if key == "task-correspondence":
            task = (run / "revision/task" if revised and "revision/task" in owners else
                    inherited.get("task", {}).get("owner", run / "task"))
            expected["task_run"] = task.resolve()
            dependencies.append((task / "task.json").resolve())
    context = manifest.get("context", {})
    scope_key = key + "_scope_path"
    if revised and key in {"processing", "sensitivity", "task-correspondence"} and scope_key in context:
        from .online import scoped_dependencies
        paths = [item.resolve() for item in scoped_dependencies(run, key)]
        expected[scope_key] = paths[-1]
        dependencies.extend(paths)
    if set(context) != set(expected):
        raise ValueError("Fatal frontier stage dependency ownership differs: " + name)
    for key, target in expected.items():
        resolved = (resolve_file(owner, context[key]) if key in {"cfg_path", "graph_repair_path", scope_key}
                    else resolve_run_reference(owner, context[key]))
        if resolved != target:
            raise ValueError("Fatal frontier stage belongs to another upstream owner: " + name)
    if [resolve_file(owner, item) for item in manifest["dependencies"]] != dependencies:
        raise ValueError("Fatal frontier stage dependency references differ: " + name)


def replay_fatal_frontier(run, saved, config, *, renderer=None):
    """Verify every actual prepared sibling, then compare the exact bound state.

    Observed completion versus abort is an execution-frontier fact. A worker may
    finish after its sibling fails, so replay checks its own immutable receipt
    without pretending a different replay schedule observed that completion.
    """
    from skillflow.task.runner import run_task
    from skillflow.common.inputs.snapshot import read_snapshot
    from .source_review import replay_saved_review
    from .runner import _certificate, _confirmed_request_failure, _failure_reason, _initial, _save, DEPS
    reference = saved.get("fatal_frontier")
    if not isinstance(reference, dict):
        raise ValueError("A recorded fatal semantic frontier is required")
    if not (run / PATH).is_file():
        raise ValueError("The recorded fatal semantic frontier file is missing")
    path = resolve_file(run, reference)
    if path != (run / PATH).resolve():
        raise ValueError("Fatal semantic frontier reference has an unexpected owner")
    receipt = read(path)
    if set(receipt) != {"identity", "guided_state", "run_manifest", "owners", "graphs", "recovery"} or receipt["identity"] != IDENTITY:
        raise ValueError("Fatal semantic frontier protocol differs")
    if resolve_file(run, receipt["run_manifest"]) != (run / "manifest.json").resolve():
        raise ValueError("Fatal frontier belongs to another guided run manifest")
    state = receipt["guided_state"]
    expected = {key: value for key, value in saved.items() if key not in {"identity", "counts", "fatal_frontier"}}
    if canonical_sha256(state) != canonical_sha256(expected):
        raise ValueError("Final guided decisions differ from their bound fatal frontier")
    primary = state.get("stage")
    baseline = _initial()
    baseline.update(status="failed", stage=primary, reason=state.get("reason"),
                    repair_used=isinstance(primary, str) and primary.startswith("revision"), stages=state.get("stages"))
    if state != baseline or not isinstance(state.get("stages"), dict):
        raise ValueError("Fatal frontier does not describe an early semantic failure without a selected bundle")
    if any((run / name).exists() for name in ("selection.json", "graph/selected.json", "annotation/manifest.json",
                                             "revision/annotation/manifest.json", "propagation", "doe")):
        raise ValueError("Fatal frontier cannot authorize a selected or downstream bundle")
    if receipt["owners"] != _inventory(run):
        raise ValueError("Fatal frontier prepared owners or terminal receipts changed")
    if receipt["recovery"] != _recovery_inventory(run):
        raise ValueError("Fatal frontier failed-stage or repair-admission evidence changed")
    for binding in receipt["recovery"].values():
        resolve_file(run, binding)
    for entries in receipt["owners"].values():
        for binding in [*(item for key, item in entries.items() if key != "calls"), *entries["calls"].values()]:
            if binding is not None:
                resolve_file(run, binding)
    owners, outcomes, graphs, tasks, fragments, reviews = _owners(run), {}, {}, {}, {}, {}
    failures, stage_values = {}, {}
    from .accepted_upstream import load_accepted_upstream
    inherited = load_accepted_upstream(run)
    if inherited:
        graphs["initial"] = inherited["graph"]["value"]
        tasks["task"] = inherited["task"]["value"]
        stage_values["flow"] = inherited["flow"]["value"]
        outcomes.update({key:{"status":"complete"} for key in inherited})
        _certificate(run, "initial", graphs["initial"], True, renderer)
    for name, owner in sorted(owners.items()):
        if name in {"review", "revision/review"}:
            continue
        if name in {"task", "revision/task"}:
            task_manifest = read(owner / "manifest.json")
            if (task_manifest.get("source_owner") is None
                    or resolve_run_reference(owner, task_manifest["source_owner"]) != (run / "source").resolve()):
                raise ValueError("Fatal frontier Task belongs to another source owner")
            outcome = run_task(owner, config=config, replay=True, read_only=True, max_corrections=1)
            status = outcome["status"]
            if (status == "execution_error" and outcome.get("error_kind") in {"ModelRequestFailure", "InputTooLarge"}
                    and _primary_failure(run, name) != "RuntimeError: " + str(outcome.get("reason"))):
                raise ValueError("Fatal frontier Task failure lacks intact transport evidence")
            outcomes[name] = {"status": status, "reason": outcome.get("reason")}
            if status == "complete":
                tasks[name] = outcome["task"]
            elif status in {"semantic_failure", "structural_failure"}:
                failures[name] = {"status": status, "reason": outcome.get("reason", "Task failed")}
                if outcome.get("failure") is not None:
                    failures[name]["failure"] = outcome["failure"]
            continue
        _check_step_binding(run, name, owner, owners, inherited)
        expected_step = read(owner / "result.json") if (owner / "result.json").is_file() else {}
        try:
            value = run_step(owner, replay=True, config=config)
        except KeyboardInterrupt as error:
            if expected_step.get("status") != "interrupted":
                raise ValueError("Fatal frontier sibling has an unrecorded interruption") from error
            outcomes[name] = {"status": "interrupted", "reason": str(error)}
        except (SemanticFailure, StructuralCorrectionLimitReached) as error:
            receipt_status = "semantic_failure" if isinstance(error, SemanticFailure) else "structural_failure"
            if expected_step.get("status") != receipt_status:
                raise ValueError("Fatal frontier sibling failure differs from its stage receipt") from error
            outcomes[name] = {"status": receipt_status, "reason": str(error)}
            failures[name] = deepcopy(outcomes[name])
            for key in ("failure", "diagnostics"):
                if getattr(error, key, None) is not None:
                    failures[name][key] = deepcopy(getattr(error, key))
        except Exception as error:
            if not _confirmed_request_failure(error):
                raise
            if _primary_failure(run, name) != _failure_reason(error):
                raise ValueError("Fatal frontier sibling request failure lacks intact transport evidence") from error
            outcomes[name] = {"status": "execution_error", "reason": _failure_reason(error)}
        else:
            outcomes[name] = {"status": expected_step.get("status", "complete"), "reason": expected_step.get("reason")}
            stage_values[name] = value
            if outcomes[name]["status"] == "partial":
                failures[name] = {"status": "partial", "reason": "Invalid records retained as explicit local validation gaps"}
            if name.removeprefix("revision-") == "graph":
                label = "revision" if name.startswith("revision-") else "initial"
                graph = value["cfg"]
                if label == "revision" and graph == graphs.get("initial"):
                    continue
                if label not in receipt["graphs"] or read(resolve_file(run, receipt["graphs"][label])) != {"cfg": graph}:
                    raise ValueError("Fatal frontier selected graph bytes differ from the verified graph stage")
                _certificate(run, label, graph, True, renderer)
                graphs[label] = graph
            elif name.removeprefix("revision-") in {"processing", "task-correspondence", "sensitivity"}:
                fragments[name] = value
    if set(graphs) != set(receipt["graphs"]):
        raise ValueError("Fatal frontier has unverified graph artifacts")
    files = {"skill/" + row["path"]: row["content"] for row in read_snapshot(run / "source")[1]["files"]}
    from .failed_stage_material import capture_failed_stage
    expected_recovery = set()
    # Only observed failures were consumed by the scheduler. An aborted sibling
    # may have a terminal receipt, but must not retroactively become review input.
    for name, failure in failures.items():
        if state["stages"].get(name, {}).get("status") not in {"structural_failure", "semantic_failure"}:
            continue
        key = "task" if name == "revision/task" else name.removeprefix("revision-")
        evidence = capture_failed_stage(run, stage=key, attempt=name, files=files, failure=failure)
        relative = "audit/failed-stages/" + name.replace("/", "-") + ".json"
        if relative not in receipt["recovery"] or read(resolve_file(run, receipt["recovery"][relative])) != evidence:
            raise ValueError("Fatal frontier rejected-stage material differs from verified original calls")
        expected_recovery.add(relative)
        failure["evidence"] = evidence
    for name in ("review", "revision/review"):
        if name not in owners:
            continue
        material = read(owners[name] / "inputs.json")
        if read(owners[name] / "manifest.json")["config"] != config:
            raise ValueError("Fatal frontier source review configuration differs")
        revised = name.startswith("revision/")
        task = tasks.get("revision/task" if revised and "revision/task" in tasks else "task")
        graph = graphs.get("revision" if revised and "revision" in graphs else "initial")
        if material.get("files") != files or material.get("task") != task or material.get("cfg") != graph or material.get("annotation") is not None:
            raise ValueError("Fatal frontier review belongs to different source, Task, CFG or annotation")
        for key, fragment in (material.get("fragments") or {}).items():
            if fragments.get(("revision-" if revised else "") + key) != fragment:
                raise ValueError("Fatal frontier review fragment binding differs")
        if not revised:
            observed_failures = {key: value for key, value in failures.items()
                if not key.startswith("revision") and state["stages"].get(key, {}).get("status") == value["status"]}
            if material.get("stage_failures") != observed_failures:
                raise ValueError("Fatal frontier source review failure inputs differ from observed stage failures")
        reviewed = replay_saved_review(owners[name])
        reviews[name] = reviewed
        outcomes[name] = {"status": reviewed["status"], "reason": reviewed.get("reason")}
    if "review" in reviews:
        from .shared_repair import repair_decision
        values = {key: {"value": value} for key, value in stage_values.items()
                  if not key.startswith("revision")}
        if "task" in tasks:
            values["task"] = {"value": tasks["task"]}
        if "initial" in graphs:
            values["graph"] = {"value": graphs["initial"]}
        errors = {key: value for key, value in failures.items()
                  if not key.startswith("revision") and state["stages"].get(key, {}).get("status") == value["status"]}
        decision = repair_decision(files=files, values=values, errors=errors, reviewed=reviews["review"],
                                   selected=None, graph_facts_only=True)
        relative = "audit/shared-repair-decision.json"
        if relative not in receipt["recovery"] or read(resolve_file(run, receipt["recovery"][relative])) != decision:
            raise ValueError("Fatal frontier shared-repair admission differs from verified source review and failures")
        if primary.startswith("revision") and not decision["eligible"]:
            raise ValueError("Fatal frontier revision has no admissible shared repair")
        expected_recovery.add(relative)
    if set(receipt["recovery"]) != expected_recovery:
        raise ValueError("Fatal frontier contains unverified recovery evidence")
    for name in ("task", "revision/task"):
        if name not in owners:
            continue
        request = read(owners[name] / "inputs/request.json")
        revision = None if name == "task" else {
            "previous_task": tasks.get("task"), "objections": reviews.get("review", {}).get("objections")}
        if request != {"revision": revision} or name == "revision/task" and ("task" not in tasks or "review" not in reviews):
            raise ValueError("Fatal frontier Task revision differs from its original Task and source-review objections")
    reason = _primary_failure(run, primary)
    if reason is None or reason != state["reason"] or primary not in outcomes or outcomes[primary]["status"] != "execution_error":
        raise ValueError("Fatal frontier primary request failure was not independently reproduced")
    for name, row in state["stages"].items():
        if name in inherited:
            if row != {"status":"complete", "origin":"accepted_upstream"}:
                raise ValueError("Fatal frontier inherited-stage origin or status differs")
            continue
        if name not in _SEMANTIC_NAMES | {"review", "revision/review"} or not isinstance(row, dict) or set(row) - {"status", "reason"}:
            raise ValueError("Fatal frontier contains an unknown observed stage or status field")
        if name == primary:
            if row != {"status": "failed", "reason": reason}:
                raise ValueError("Fatal frontier primary stage decision differs")
        elif row.get("status") == "aborted":
            if (name not in _SEMANTIC_NAMES or name.startswith("revision") != primary.startswith("revision")
                    or row != {"status": "aborted", "reason": reason}):
                raise ValueError("Fatal frontier aborted sibling reason differs")
        elif row.get("status") == "skipped":
            key = name.removeprefix("revision-")
            if name in owners or key not in DEPS or row != {"status": "skipped", "reason": "A required upstream object is unavailable"}:
                raise ValueError("Fatal frontier skipped stage has an actual owner or wrong reason")
            prefix = "revision-" if name.startswith("revision-") else ""
            if all(outcomes.get(("revision/task" if prefix and dep == "task" else prefix + dep), {}).get("status") in {"complete", "partial"}
                   for dep in DEPS[key]):
                raise ValueError("Fatal frontier skipped stage has all required upstream values")
        else:
            outcome = outcomes.get(name)
            if outcome is None or row.get("status") != outcome["status"] or ("reason" in row and row["reason"] != outcome.get("reason")):
                raise ValueError("Fatal frontier observed stage differs from its verified terminal receipt: " + name)
    if primary.startswith("revision") and "review" not in outcomes:
        raise ValueError("Fatal repair frontier is missing its original source review")
    return _save(run, {**deepcopy(state), "fatal_frontier": reference}, replay=True)
