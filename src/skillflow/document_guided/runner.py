"""Seven isolated semantic requests and deterministic annotation assembly."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
from html import escape
from queue import Empty, Queue
from threading import Event
import json

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.inputs.snapshot import freeze_input, read_snapshot
from skillflow.common.llm.request_errors import ModelRequestFailure
from skillflow.common.recording import (canonical_sha256, implementation_provenance, now,
                                       SavedCallFailure, SavedResponseClient, sha_file, validated_trace)
from skillflow.common.runs import exclusive_run
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.structural_correction import chain_counts, StructuralCorrectionLimitReached
from skillflow.common.upstream import checked_run_path
from .online import (analysis_config, checked_manifest, file_reference, inventory, prepare_step,
                     read, resolve_file, run_step, save_assembled_annotation, seal)

IDENTITY = "skillflow-document-guided-run-v20"
SOURCE_IDENTITY = "skillflow-document-source-v6"
POLICY = {"independent_requests": True, "whole_objects": True, "normal_semantic_calls": 7,
          "annotation_assembly": "program", "whole_analysis_refusal": False,
          "workers": 2, "semantic_repairs": 1, "structural_corrections": 1,
          "source_only_task": True, "task_mapping_reads_sensitivity": False,
          "abstraction": "finite_loop_summaries", "member_demand_markers": "scoped_nested",
          "semantic_source_view": "complete_frozen_source",
          "downstream_presentation": "exact-shared-fragment-input-v1",
          "delivery_preflight": "final-adapter-prefix-and-sections-v1",
          "dispatch_successors": "binary", "ordinary_write_default": "replace",
          "review_protocol": "shared-v2", "review_request_failure": "bound_prior_record_retention_v1",
          "review_correction_scope": "known_slots_conflict_closure_v1",
          "address_identity": "typed_value_address_separation_v1",
          "execution_failure_scope": "actual_dependency_rows_v1",
          "accepted_upstream": "immutable_selected_cfg_v1",
          "review_validation": "strict-record-isolation-v1",
          "processing_presentation": "exact-shared-values-v1",
          "processing_wire_guidance": "complete-grammar-v1",
          "processing_format_diagnostics": "bounded-raw-pairs-v1",
          "cfg_correction_scope": "program-facts-finite-slots-v1",
          "cfg_assembly": "program",
          "cfg_validation": "aggregate_preflight_compiler_v1",
          "failed_stage_review": "bound_failure_targets_v1",
          "shared_repair_admission": "bound_validation_and_cfg_v2",
          "repair_request_failure": "retain_original_bound_bundle_v1",
          "fatal_phase_replay": "recorded_artifact_bound_frontier_v3",
          "input_contract_review": "required_obligations_scoped_checks_v2",
          "submission_self_check": True,
          "monitor_model_calls": 0, "usage_required": False}
WRITER = ArtifactWriter(())
NAMES = ("task", "flow", "graph", "processing", "task-correspondence", "sensitivity")
DEPS = {"task": (), "flow": (), "graph": ("flow",),
        "processing": ("flow", "graph"), "task-correspondence": ("task", "graph", "processing"),
        "sensitivity": ("graph", "processing")}


def _initial():
    return {"status": "prepared", "stage": "task", "repair_used": False, "graph_review": None,
            "annotation_review": None, "repair_review": None,
            "selected_annotation": None, "diagnostic_only": True,
            "limitations": [], "stages": {}}


def _failure_reason(error):
    """Replay preserves the original request failure, not its saved-call wrapper."""
    kind = error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__
    return kind + ": " + str(error)


def _confirmed_request_failure(error):
    """Known-ended delivery failures only; never process or record uncertainty."""
    return (not getattr(error, "recording_failed", False)
            and (isinstance(error, ModelRequestFailure)
                 or (isinstance(error, SavedCallFailure)
                     and error.error_type in {"ModelRequestFailure", "InputTooLarge"})))


def _recorded_task_request_failure(owner, outcome):
    """Recover a typed delivery failure from Task v5's verified failure receipt.

    Task keeps its independent result protocol. Its error_kind alone cannot
    authorize continuation: require the bound failed call and intact transport,
    then use the existing saved-response reader without creating a live client.
    """
    if (outcome.get("status") != "execution_error"
            or outcome.get("error_kind") not in {"ModelRequestFailure", "InputTooLarge"}
            or outcome.get("accepted_call") is not None):
        return None
    attempts = (outcome.get("response_chain") or {}).get("attempts", [])
    if not attempts:
        return None
    last = attempts[-1]
    directory = (owner / last["call"]).resolve()
    if not directory.is_relative_to(owner.resolve()):
        raise ValueError("Task failure receipt is outside its owner")
    path = directory / "call.json"
    if not path.is_file() or last.get("call_sha256") != sha_file(path):
        return None
    record = read(path)
    trace = validated_trace(directory / "transport.json")
    if (record.get("status") != "error" or record.get("recording_failed")
            or record.get("response_rejected") or len(trace) != 1
            or trace[0].get("status") != "error" or trace[0].get("recording_failed")
            or record.get("error_type") != outcome["error_kind"]
            or trace[0].get("error_type") != outcome["error_kind"]
            or record.get("error") != outcome.get("reason")
            or trace[0].get("error") != outcome.get("reason")
            or trace[0].get("prompt") != record.get("prompt")):
        return None
    try:
        SavedResponseClient(directory, WRITER).complete((directory / "prompt.txt").read_bytes().decode("utf-8"))
    except SavedCallFailure as error:
        if _confirmed_request_failure(error):
            return error
        raise
    raise ValueError("Task failure receipt unexpectedly contains a completed answer")


def _counts(run):
    counts = {"logical_calls": 0, "structural_corrections": 0, "json_normalizations": 0}
    try:
        for path in sorted(run.rglob("chain.json")):
            if "transport" in path.relative_to(run).parts:
                continue
            observed = chain_counts(path.parent.parent, path.parent.name)
            for key in counts:
                counts[key] += observed.get(key, 0)
    except Exception:
        return {"status": "unavailable"}
    return counts


def _save(run, result, *, replay=False):
    value = {**deepcopy(result), "identity": IDENTITY, "counts": _counts(run)}
    if replay:
        saved = read(run / "result.json")
        if canonical_sha256({key: item for key, item in saved.items() if key != "counts"}) != canonical_sha256({
                key: item for key, item in value.items() if key != "counts"}):
            raise ValueError("Replayed guided decisions differ from saved results")
        return saved
    WRITER.json(run / "result.json", value)
    try:
        lines = ["# Document-guided analysis", "", f"Status: {value['status']}; stage: {value['stage']}.",
                 "", "Seven normal analysis calls; program-assembled annotation; two dependency-aware workers; no model monitoring calls.",
                 "", "| Stage | Status |", "|---|---|"]
        lines += [f"| {name} | {row['status']} |" for name, row in sorted(value["stages"].items())]
        lines += ["", "Retained limitations:", *["- " + item for item in value["limitations"]],
                  "", "Local call counts: " + str(value["counts"]),
                  "Unreported findings are not per-item acceptance; missing annotation is not evidence of no DOE."]
        if value.get("reason"):
            lines += ["", "Reason: " + value["reason"]]
        if (value.get("repair_review") or {}).get("status") == "unconfirmed":
            lines += ["", "The semantic repair remains unconfirmed; original review findings remain in review/result.json."]
        text = "\n".join(lines) + "\n"
        (run / "report.md").write_text(text, encoding="utf-8")
        links = [("selection.json", "Selected bundle"), ("graph/selected.json", "Complete CFG"),
                 ("review/result.json", "Independent source review"), ("revision/review/result.json", "Repair re-review"),
                 ("doe/report.html", "DOE")]
        html = "".join(f'<li><a href="{path}">{label}</a></li>' for path, label in links if (run / path).exists())
        (run / "index.html").write_text("<!doctype html><meta charset='utf-8'><title>Document-guided analysis</title>"
            "<style>body{max-width:1100px;margin:32px auto;font:17px/1.7 system-ui}pre{white-space:pre-wrap}</style>"
            + "<pre>" + escape(text) + "</pre><ul>" + html + "</ul>", encoding="utf-8")
    except OSError:
        pass
    return value


def prepare(input, *, run_dir, config=None):
    """Freeze source and policy without any client, probe or profile."""
    config = analysis_config(config)
    run, source = checked_run_path(run_dir), checked_run_path(input)
    if source.is_dir() and (run.is_relative_to(source) or source.is_relative_to(run)):
        raise ValueError("Run and source directories must not overlap")
    run.mkdir(parents=True, exist_ok=True)
    with exclusive_run(run):
        if any(path.name != ".runner.lock" for path in run.iterdir()):
            raise ValueError("Preparation requires a new empty directory")
        freeze_input(source, run / "source", WRITER)
        WRITER.json(run / "source/manifest.json", seal({"identity": SOURCE_IDENTITY,
            "implementation": implementation_provenance(), "files": inventory(run / "source")}))
        manifest = seal({"identity": IDENTITY, "created_at": now(), "policy": POLICY,
            "implementation": implementation_provenance(), "config": config, "files": {},
            "source": file_reference(run, run / "source/manifest.json")})
        WRITER.json(run / "manifest.json", manifest)
        _save(run, _initial())
    return manifest


def prepare_from_accepted_cfg(parent, *, run_dir, config=None):
    """Prepare a separate run from bound accepted upstream values, without new calls."""
    from .accepted_upstream import prepare_from_accepted_cfg as prepare_accepted
    return prepare_accepted(parent, run_dir=run_dir, config=config)


def _verify(run):
    manifest = checked_manifest(run, IDENTITY, recompute=True)
    config = analysis_config(manifest["config"])
    if manifest["policy"] != POLICY or manifest["config"] != config:
        raise ValueError("Document-guided policy or configuration differs")
    resolve_file(run, manifest["source"])
    checked_manifest(run / "source", SOURCE_IDENTITY)
    read_snapshot(run / "source")
    return config


def _stable(path, value, replay):
    if path.exists():
        if read(path) != value:
            raise ValueError("Saved candidate differs: " + str(path))
    elif replay:
        raise ValueError("Missing candidate during replay: " + str(path))
    else:
        WRITER.json(path, value)
    return path


def _certificate(run, label, graph, replay, renderer, certificate_origin=None):
    from skillflow.graph.audit.controlled import recertify_inherited, render_controlled, verify_controlled
    from skillflow.graph.ir.cfg import ControlFlowGraph
    target = run / "graph" / label / "controlled.json"
    cfg = ControlFlowGraph.model_validate(graph)
    if certificate_origin is not None:
        local = recertify_inherited(target.read_bytes(), expected_sha256=certificate_origin["sha256"],
                                    cfg=cfg, executable=renderer)
        receipt = {
            "identity": "skillflow-inherited-controlled-verification-v1",
            "inherited_document": certificate_origin, "local_certificate": local,
        }
        receipt_path = target.with_name("local-verification.json")
        if receipt_path.exists():
            if canonical_sha256(read(receipt_path)) != canonical_sha256(receipt):
                raise ValueError("Local graph verification receipt differs from the reproduced proof")
        elif replay:
            raise ValueError("Missing local graph verification receipt")
        else:
            WRITER.json(receipt_path, receipt)
    elif target.exists():
        verify_controlled(read(target), cfg=cfg, executable=renderer)
    elif replay:
        raise ValueError("Missing graph certificate")
    else:
        # Rendering already performs the complete certified roundtrip.
        WRITER.json(target, render_controlled(cfg, executable=renderer))


def _replay_interrupted(run, saved, config):
    """Verify recorded stage cursors without replaying a nondeterministic schedule."""
    from skillflow.task.runner import run_task
    from .online import load_annotation
    from .source_review import replay_saved_review
    for owner in (run / "task", run / "revision/task"):
        if (owner / "manifest.json").exists():
            run_task(owner, config=config, replay=True, max_corrections=1)
    for manifest in sorted((run / "steps").glob("*/manifest.json")):
        owner = manifest.parent
        expected = read(owner / "result.json") if (owner / "result.json").exists() else {}
        try:
            run_step(owner, replay=True, config=config)
        except KeyboardInterrupt:
            if expected.get("status") != "interrupted":
                raise ValueError("Unrecorded stage interruption")
        except SemanticFailure:
            if expected.get("status") != "semantic_failure":
                raise
        except StructuralCorrectionLimitReached:
            if expected.get("status") != "structural_failure":
                raise
        except Exception as error:
            if (isinstance(error, SavedCallFailure) and error.error_type == "KeyboardInterrupt"
                    and expected.get("status") == "interrupted"
                    and not getattr(error, "recording_failed", False)):
                continue
            retained = saved.get("stages", {}).get(owner.name, {})
            if not (owner.name.startswith("revision-")
                    and retained.get("status") == "request_failure"
                    and saved.get("selected_annotation") == "annotation"
                    and _confirmed_request_failure(error)
                    and retained.get("reason") == _failure_reason(error)):
                raise
    for owner in (run / "annotation", run / "revision/annotation"):
        if (owner / "manifest.json").exists():
            load_annotation(owner)
    for owner in (run / "review", run / "revision/review"):
        if (owner / "manifest.json").exists():
            if read(owner / "manifest.json")["config"] != config:
                raise ValueError("Source-review configuration differs from the saved run")
            replay_saved_review(owner)
    if (run / "selection.json").exists():
        for reference in read(run / "selection.json").values():
            resolve_file(run, reference)
    return saved


class _StageFailure(Exception):
    def __init__(self, status, reason, failure=None):
        super().__init__(reason)
        self.status, self.failure = status, failure


def _fragment_repair_findings(review, owner):
    """Locate source rechecks without leaking another layer's interpretations."""
    return [{"target_ids": deepcopy(row["target_ids"]), "source_refs": deepcopy(row["source_refs"])}
            for row in review["findings"]
            if row["domain"] == "annotation" and row.get("owner", "processing") == owner]


def run(run_dir, *, client_factory=None, replay=False, renderer=None, progress=None):
    from skillflow.task.runner import prepare_task_run, run_task, load_task_run
    from skillflow.propagation.contracts.runtime_contract import runtime_contract
    from skillflow.propagation.material import prepare_material
    from .prompts import (build_flow_prompt, build_graph_facts_prompt,
                          build_graph_updates_prompt, build_fragment_prompt,
                          build_processing_revision_prompt, build_sensitivity_revision_prompt,
                          build_correspondence_revision_prompt)
    from .graph_steps import FACTS, UPDATES, rejected_facts, repair_input, repair_slots
    from .source_review import run_source_review
    run = checked_run_path(run_dir)
    if replay and client_factory is not None:
        raise ValueError("Offline replay cannot accept a live client")
    with exclusive_run(run):
        config = _verify(run)
        from .accepted_upstream import load_accepted_upstream
        inherited_values = load_accepted_upstream(run)
        saved = read(run / "result.json")
        if saved["status"] not in {"prepared", "running", "interrupted"} and not replay:
            replay, client_factory = True, None
        if inherited_values:
            graph = inherited_values["graph"]
            _certificate(run, "initial", graph["value"], replay, renderer, graph["certificate_origin"])
        if replay and saved["status"] == "interrupted":
            return _replay_interrupted(run, saved, config)
        if replay and saved.get("fatal_frontier_error"):
            raise ValueError("The terminal failure lacks a complete fatal frontier: " + saved["fatal_frontier_error"])
        if replay and saved.get("status") == "failed":
            from .fatal_frontier import replay_fatal_frontier, requires_fatal_frontier
            if (saved.get("fatal_frontier") is not None or (run / "audit/fatal-semantic-frontier.json").exists()
                    or requires_fatal_frontier(run, saved)):
                return replay_fatal_frontier(run, saved, config, renderer=renderer)
        result, stopping, events = _initial(), Event(), Queue()
        result["status"] = "running"
        source = read_snapshot(run / "source")[1]
        files = {"skill/" + row["path"]: row["content"] for row in source["files"]}
        rules = ("Preserve source obligations, actual input versions and recipient pairing. "
                 "Retain conflicts without unsupported precedence. A local excerpt cannot override the Skill. "
                 "Do not infer saved-file ownership from names or a shared analysis label.")

        def mark(name, status="running", **extra):
            result["stage"], result["stages"][name] = name, {"status": status, **extra}
            if replay and saved["status"] == "interrupted" and saved["stage"] == name and status != "running":
                if saved["stages"].get(name, {}).get("status") == status:
                    raise KeyboardInterrupt(saved.get("reason", "Recorded user interruption"))
            if not replay:
                _save(run, result)
            if progress is not None:
                try:
                    progress(deepcopy(result))
                except KeyboardInterrupt:
                    raise
                except Exception:
                    pass

        def finish_running(status, reason, *, current_status=None):
            # Stage observers must not mistake a terminal run for an active call.
            # This does not claim that aborted independent branches were invalid.
            for name, row in result["stages"].items():
                if row["status"] == "running":
                    terminal = current_status if name == result["stage"] and current_status else status
                    result["stages"][name] = {"status": terminal, "reason": reason}

        def client(name, owner):
            if replay:
                return None
            if client_factory is None:
                raise ValueError("A live run requires an explicit isolated client factory")
            return client_factory(name, owner)

        def step(name, prompt, *, kind="document", context=None, dependencies=(), max_corrections=1, program=False):
            target = run / "steps" / name
            if not (target / "manifest.json").exists():
                if replay:
                    raise ValueError("Missing prepared stage: " + name)
                prepare_step(target, prompt, kind=kind,
                    context={"source_owner": run / "source", **(context or {})},
                    dependencies=[run / "source/manifest.json", *dependencies],
                    max_corrections=max_corrections, config=config)
            elif (target / "prompt.txt").read_bytes().decode("utf-8") != prompt:
                raise ValueError("Prepared stage differs from current upstream: " + name)
            value = run_step(target, client=None if program else client(name, target), replay=replay,
                             stop_event=stopping, config=config)
            return {"value": value, "path": target / "result.json", "step": target,
                    "partial": read(target / "result.json").get("status") == "partial"}

        def phase(base=None, domains=(), feedback=None, prior_errors=None, validation_targets=(),
                  retain_prior_on_request_failure=False):
            values = dict(inherited_values if base is None else base)
            revision = base is not None
            invalid = set() if revision else set(NAMES) - set(values)
            if not revision:
                for inherited_name in values:
                    mark(inherited_name, "complete", origin="accepted_upstream")
            values.pop("annotation", None)
            if revision:
                invalid.add("assembly")
            if "annotation" in domains:
                invalid.update(row.get("owner", "processing") for row in (feedback.get("review") or {}).get("findings", [])
                               if row["domain"] == "annotation")
                if validation_targets:
                    invalid.add("processing")
            if "cfg" in domains:
                invalid.add("graph")
            if "task" in domains:
                invalid.update(("task", "task-correspondence"))
            errors = {name: deepcopy(detail) for name, detail in (prior_errors or {}).items()
                      if name not in invalid}
            for key in invalid:
                values.pop(key, None)

            def stage_name(key):
                return ("revision/task" if key == "task" else "revision-" + key) if revision else key

            def job(key):
                name = stage_name(key)
                events.put((name, "running", {}))
                if stopping.is_set():
                    raise KeyboardInterrupt("User interrupted before stage")
                if key == "task":
                    owner = run / ("revision/task" if revision else "task")
                    if not (owner / "manifest.json").exists():
                        if replay:
                            raise ValueError("Missing Task preparation")
                        revise = {"previous_task": base["task"]["value"], "objections": feedback["objections"]} if revision else None
                        prepare_task_run(owner, source_owner=run / "source", config=config,
                            revision=revise, resume_preparation=True, max_corrections=1,
                            allow_cannot_assess=False, self_check=POLICY["submission_self_check"])
                    outcome = run_task(owner, client=client(name, owner), config=config,
                        replay=replay, max_corrections=1, stop_event=stopping)
                    if outcome["status"] == "interrupted":
                        raise KeyboardInterrupt(outcome.get("reason", "Task interrupted"))
                    if outcome["status"] != "complete":
                        if outcome["status"] not in {"semantic_failure", "structural_failure"}:
                            if revision and retain_prior_on_request_failure:
                                failure = _recorded_task_request_failure(owner, outcome)
                                if failure is not None:
                                    raise failure
                            raise RuntimeError(outcome.get("reason", "Task execution failed"))
                        raise _StageFailure(outcome["status"], outcome.get("reason", "Task failed"), outcome.get("failure"))
                    return {"value": load_task_run(owner)["task"], "path": owner / "task.json", "owner": owner}
                if key == "flow":
                    return step(name, build_flow_prompt(files=files, global_requirements=rules,
                        self_check=POLICY["submission_self_check"]), kind="flow_document")
                if key == "graph":
                    graph_dependencies = [values["flow"]["path"]]
                    if revision:
                        old = base.get("graph")
                        if old is not None:
                            previous, previous_path = old["value"], old["path"]
                        else:
                            from .failed_stage_material import checked_structural_failure
                            failure = (prior_errors or {}).get("graph", {})
                            if not checked_structural_failure(failure.get("evidence"), stage="graph", files=files):
                                raise ValueError("Missing-CFG revision has no bound rejected original material")
                            previous = rejected_facts(failure["evidence"])
                            previous_path = run / "audit/failed-stages/graph.json"
                        repair = repair_input(files=files, previous=previous, accepted=old is not None,
                            findings=[row for row in feedback["review"]["findings"] if row["domain"] == "cfg"])
                        path = _stable(run / "graph/revision-input.json", {"repair": repair}, replay)
                        if repair is None or not repair_slots(repair["plan"]):
                            return {"deferred": True, "prior": old,
                                    "reason": "No source-bound editable graph slots for the recorded findings"}
                        item = step(name, build_graph_updates_prompt(files=files, plan=repair["plan"]),
                            kind=UPDATES, context={"graph_repair_path": path},
                            dependencies=[*graph_dependencies, previous_path, run / "review/result.json", path],
                            max_corrections=0)
                    else:
                        item = step(name, build_graph_facts_prompt(files=files,
                            documents={"flow": values["flow"]["value"]}, global_requirements=rules,
                            self_check=POLICY["submission_self_check"]), kind=FACTS, dependencies=graph_dependencies)
                    graph = item["value"]["cfg"]
                    patch_diagnostics = item["value"]["assembly"].get("patch_diagnostics", [])
                    local_gap = ("Graph updates quarantined: " + "; ".join(
                        f"{row['path']} {row['message']}" for row in patch_diagnostics)) if patch_diagnostics else None
                    if revision and repair["plan"].get("unaddressable_findings"):
                        text = "Graph findings without a finite slot: " + ", ".join(
                            repair["plan"]["unaddressable_findings"])
                        local_gap = (local_gap + "; " if local_gap else "") + text
                    footprint = {"local_gap": local_gap} if local_gap else {}
                    if revision and old is not None and graph == old["value"]:
                        return {**old, **footprint}
                    label = "revision" if revision else "initial"
                    _certificate(run, label, graph, replay, renderer)
                    path = _stable(run / "graph" / (label + ".json"), {"cfg": graph}, replay)
                    return {"value": graph, "path": path, **footprint}
                graph = values["graph"]
                if key in {"processing", "task-correspondence", "sensitivity"}:
                    docs = ({"flow": values["flow"]["value"]} if key == "processing"
                            else {"processing": values["processing"]["value"]})
                    dependencies = [graph["path"], values["flow" if key == "processing" else "processing"]["path"]]
                    extra, context = {}, {"cfg_path": graph["path"]}
                    if key == "processing":
                        extra["runtime_contract"] = runtime_contract()
                        if revision and "processing" in base and "graph" in base:
                            from .fragment_revision import processing_scope
                            old = base["processing"]
                            from .online import processing_revision_evidence
                            previous_gaps, rejected = processing_revision_evidence(old["step"])
                            scope = processing_scope(base["graph"]["value"], graph["value"],
                                (feedback.get("review") or {}).get("findings", []), old["value"],
                                validation_gaps=previous_gaps, rejected_records=rejected)
                            if scope is not None and scope["slots"]:
                                path = _stable(run / "revision/processing-scope.json", scope, replay)
                                item = step(name, build_processing_revision_prompt(files=files,
                                    flow=values["flow"]["value"], runtime_contract=extra["runtime_contract"],
                                    scope=scope, global_requirements=rules), kind="processing_fragment",
                                    context={**context, "processing_scope_path": path},
                                    dependencies=[*dependencies, old["path"], base["graph"]["path"],
                                                  run / "review/result.json", path], max_corrections=0)
                                if (not scope.get("unresolved_targets")
                                        and graph["value"] == base["graph"]["value"]
                                        and item["value"] == old["value"]
                                        and read(item["path"]).get("validation_gaps", []) == previous_gaps):
                                    return old
                                if scope.get("unresolved_targets"):
                                    item["local_gap"] = "No finite processing scope for: " + ", ".join(
                                        scope["unresolved_targets"])
                                return item
                            return {"deferred": True, "prior": (old if graph["path"] == base["graph"]["path"] else None),
                                    "reason": "The challenged processing dependencies have no verified finite revision scope"}
                    if key == "task-correspondence":
                        extra["task"] = values["task"]["value"]
                        dependencies.append(values["task"]["path"])
                        context["task_run"] = values["task"]["owner"]
                    if key != "processing":
                        context["processing_step"] = values["processing"]["step"]
                    if key == "task-correspondence" and revision and {"task-correspondence", "processing", "task", "graph"} <= base.keys():
                        from .fragment_revision import correspondence_scope
                        old, prior = base["task-correspondence"], base["processing"]
                        current = values["processing"]
                        scope = correspondence_scope(base["graph"]["value"], graph["value"], prior["value"],
                            current["value"], base["task"]["value"], values["task"]["value"],
                            feedback["review"]["findings"], old["value"],
                            old_validation_gaps=read(prior["path"]).get("validation_gaps", []),
                            new_validation_gaps=read(current["path"]).get("validation_gaps", []))
                        if scope is not None:
                            if (not scope["slots"] and not scope["removed_requirement_ids"] and
                                    all(values[dep]["path"] == base[dep]["path"] for dep in DEPS[key])):
                                return old
                            path = _stable(run / "revision/task-correspondence-scope.json", scope, replay)
                            prompt = (build_correspondence_revision_prompt(files=files, scope=scope, cfg=graph["value"],
                                processing=current["value"], global_requirements=rules) if scope["slots"]
                                else "Program-carried Task correspondence; no semantic request.")
                            item = step(name, prompt, kind="task-correspondence_fragment", program=not scope["slots"],
                                context={**context, "task-correspondence_scope_path": path},
                                dependencies=[*dependencies, old["path"], prior["path"], base["graph"]["path"],
                                              run / "review/result.json", path], max_corrections=0)
                            if (item["value"] == old["value"] and
                                    all(values[dep]["path"] == base[dep]["path"] for dep in DEPS[key])):
                                return old
                            return item
                        if all(values[dep]["path"] == base[dep]["path"] for dep in DEPS[key]):
                            return {"deferred": True, "prior": old,
                                    "reason": "The Task correspondence finding has no exact requirement owner"}
                    if key == "sensitivity" and revision and {"sensitivity", "processing", "graph"} <= base.keys():
                        from .fragment_revision import sensitivity_scope
                        old, prior = base["sensitivity"], base["processing"]
                        scope = sensitivity_scope(base["graph"]["value"], graph["value"], prior["value"],
                            values["processing"]["value"], feedback["review"]["findings"], old["value"])
                        if not scope["slots"] and not scope["removed_instruction_ids"] and graph["path"] == base["graph"]["path"] and prior["path"] == values["processing"]["path"]:
                            if scope["unresolved_targets"]:
                                return {"deferred": True, "prior": old,
                                        "reason": "The challenged sensitivity declarations have no exact retained owner"}
                            return old
                        path = _stable(run / "revision/sensitivity-scope.json", scope, replay)
                        prompt = (build_sensitivity_revision_prompt(files=files, scope=scope, global_requirements=rules)
                                  if scope["slots"] else "Program-carried sensitivity; no semantic request.")
                        item = step(name, prompt, kind="sensitivity_fragment", program=not scope["slots"],
                            context={**context, "sensitivity_scope_path": path},
                            dependencies=[*dependencies, old["path"], prior["path"], base["graph"]["path"],
                                          run / "review/result.json", path], max_corrections=0)
                        if scope["unresolved_targets"]:
                            item["local_gap"] = "No finite sensitivity scope for: " + ", ".join(scope["unresolved_targets"])
                        return item
                    if revision:
                        extra["repair_context"] = {"previous_fragment": base.get(key, {}).get("value"),
                            "source_rechecks": _fragment_repair_findings(feedback["review"], key)}
                    return step(name, build_fragment_prompt(key, files=files, documents=docs,
                        cfg=graph["value"], global_requirements=rules,
                        self_check=POLICY["submission_self_check"], **extra),
                        kind=key + "_fragment", context=context, dependencies=dependencies)
                raise ValueError("Unknown semantic stage: " + key)

            futures, attempted = {}, set(values) | set(errors)
            with ThreadPoolExecutor(max_workers=2) as pool:
                try:
                    while True:
                        for key in NAMES:
                            if key not in attempted and all(dep in values for dep in DEPS[key]):
                                attempted.add(key)
                                futures[pool.submit(job, key)] = key
                        while True:
                            try:
                                name, status, extra = events.get_nowait()
                                if result["stages"].get(name, {}).get("status") not in {
                                        "complete", "partial", "semantic_failure", "structural_failure", "request_failure", "deferred"}:
                                    mark(name, status, **extra)
                            except Empty:
                                break
                        if not futures:
                            break
                        done, _ = wait(futures, timeout=0.1, return_when=FIRST_COMPLETED)
                        for future in done:
                            key = futures.pop(future)
                            try:
                                value = future.result()
                                if value.get("deferred"):
                                    errors[key] = {"status": "deferred", "reason": value["reason"]}
                                    if value["prior"] is not None:
                                        values[key] = value["prior"]
                                    mark(stage_name(key), **errors[key])
                                    continue
                                if (key == "graph" and revision
                                        and value["path"] != base.get("graph", {}).get("path")):
                                    for child in ("processing", "task-correspondence", "sensitivity"):
                                        values.pop(child, None)
                                        errors.pop(child, None)
                                        attempted.discard(child)
                                if (key == "processing" and revision
                                        and value["path"] != base.get("processing", {}).get("path")):
                                    for child in ("task-correspondence", "sensitivity"):
                                        values.pop(child, None)
                                        errors.pop(child, None)
                                        attempted.discard(child)
                                values[key] = value
                                partial = values[key].get("partial", False) or bool(value.get("local_gap"))
                                if partial:
                                    errors[key] = {"status": "partial", "reason": value.get("local_gap") or
                                                   "Invalid records retained as explicit local validation gaps"}
                                mark(stage_name(key), "partial" if partial else "complete")
                            except (SemanticFailure, StructuralCorrectionLimitReached, _StageFailure) as error:
                                status = ("semantic_failure" if isinstance(error, SemanticFailure) else
                                          "structural_failure" if isinstance(error, StructuralCorrectionLimitReached) else error.status)
                                detail = {"status": status, "reason": str(error)}
                                if getattr(error, "failure", None) is not None:
                                    detail["failure"] = error.failure
                                if getattr(error, "diagnostics", None) is not None:
                                    detail["diagnostics"] = error.diagnostics
                                from .failed_stage_material import capture_failed_stage
                                evidence = capture_failed_stage(run, stage=key, attempt=stage_name(key),
                                    files=files, failure=detail)
                                _stable(run / "audit/failed-stages" / (stage_name(key).replace("/", "-") + ".json"),
                                    evidence, replay)
                                detail["evidence"] = evidence
                                errors[key] = detail
                                mark(stage_name(key), status, reason=str(error))
                            except KeyboardInterrupt as error:
                                mark(stage_name(key), "interrupted", reason=str(error))
                                raise
                            except Exception as error:
                                if (revision and retain_prior_on_request_failure
                                        and _confirmed_request_failure(error)):
                                    # No failed stage value is synthesized. Its dependent
                                    # stages remain unavailable; the caller can retain only
                                    # the complete original bundle and its original review.
                                    detail = {"status": "request_failure", "reason": _failure_reason(error)}
                                    errors[key] = detail
                                    mark(stage_name(key), **detail)
                                    continue
                                mark(stage_name(key), "failed", reason=_failure_reason(error))
                                raise
                except BaseException:
                    stopping.set()
                    for future in futures:
                        future.cancel()
                    raise
            for key in NAMES:
                if key not in attempted:
                    mark(stage_name(key), "skipped", reason="A required upstream object is unavailable")
            assembly_inputs = {"task", "graph", "processing", "task-correspondence", "sensitivity"}
            if (revision and "annotation" in base and assembly_inputs <= values.keys()
                    and all(values[key]["path"] == base[key]["path"] for key in assembly_inputs)):
                values["annotation"] = base["annotation"]
                mark("revision/assembly", "skipped", reason="The published assembly inputs are unchanged")
            elif assembly_inputs <= values.keys():
                name = "revision/assembly" if revision else "assembly"
                mark(name)
                owner = run / ("revision/annotation" if revision else "annotation")
                try:
                    accepted = save_assembled_annotation(owner, source_owner=run / "source",
                        cfg_path=values["graph"]["path"], task_run=values["task"]["owner"],
                        fragment_steps={key: values[key]["step"] for key in
                                        ("processing", "task-correspondence", "sensitivity")})
                    values["annotation"] = {"value": accepted, "path": owner / "manifest.json", "owner": owner}
                    mark(name, "partial" if accepted["raw_annotation"].get("processing_gaps") else "complete")
                except Exception as error:
                    errors["assembly"] = {"status": "structural_failure", "reason": type(error).__name__ + ": " + str(error)}
                    mark(name, "structural_failure", reason=str(error))
            return values, errors

        review_materials = {}

        def source_review(values, errors, revision=False):
            name = "revision/review" if revision else "review"
            mark(name)
            annotation = values.get("annotation", {}).get("value")
            reviewed = run_source_review(run / name, files=files,
                task=values.get("task", {}).get("value"), cfg=values.get("graph", {}).get("value"),
                annotation=None if annotation is None else annotation["wire_annotation"],
                raw_annotation=None if annotation is None else annotation["raw_annotation"],
                compiled=None if annotation is None else annotation["compiled_annotation"],
                mapping=None if annotation is None else annotation["mapping"], runtime_contract=runtime_contract(),
                stage_failures=errors, client=client(name, run / name),
                replay=replay, max_corrections=1, stop_event=stopping, config=config,
                generation="fragment-v1", prompt_view=POLICY["review_protocol"],
                partial=bool(errors) or annotation is None,
                fragments=None if annotation is not None else {
                    key: values[key]["value"] for key in ("processing", "task-correspondence", "sensitivity") if key in values})
            review_materials[id(reviewed)] = read(run / name / "inputs.json")
            if reviewed["status"] == "interrupted":
                raise KeyboardInterrupt(reviewed.get("reason", "Source review interrupted"))
            mark(name, reviewed["status"], **({"reason": reviewed["reason"]} if reviewed.get("reason") else {}))
            return reviewed

        def select(values):
            selected = values["annotation"]["owner"]
            selection = {"task": file_reference(run, values["task"]["path"]),
                         "cfg": file_reference(run, values["graph"]["path"]),
                         "annotation": file_reference(run, selected / "manifest.json")}
            if not replay:
                WRITER.json(run / "selection.json", selection)
                WRITER.json(run / "graph/selected.json", {"cfg": values["graph"]["value"]})
            result["selected_annotation"] = selected.relative_to(run).as_posix()
            return selected

        try:
            values, errors = phase()
            reviewed = source_review(values, errors)
            chosen, selected = values, None
            if "annotation" in values:
                selected = select(values)
            findings = (reviewed.get("review") or {}).get("findings", [])
            from .shared_repair import repair_decision
            processing_gaps = (read(values["processing"]["path"]).get("validation_gaps", [])
                               if "processing" in values else [])
            decision = repair_decision(files=files, values=values, errors=errors,
                reviewed=reviewed, selected=selected, graph_facts_only=True, processing_gaps=processing_gaps)
            _stable(run / "audit/shared-repair-decision.json", decision, replay)
            if decision["eligible"]:
                result["repair_used"] = True
                prior_errors = dict(errors)
                if decision["deferred_cfg"]:
                    prior_errors.setdefault("graph", {"status": "deferred",
                        "reason": "The original CFG findings have no source-bound writable slot"})
                revised, repair_errors = phase(base=values, domains=set(decision["domains"]),
                    feedback={**reviewed, "review": reviewed.get("review") or {"findings": []}}, prior_errors=prior_errors,
                    validation_targets=decision["processing_validation_targets"],
                    retain_prior_on_request_failure=selected is not None)
                unchanged = (selected is not None and revised.get("annotation") is values["annotation"])
                if unchanged:
                    reason = "No assembly input changed; the original source review and its findings remain bound."
                    mark("revision/review", "skipped", reason=reason)
                    revised_review = {"status": "not_run"}
                    result["repair_review"] = {"status": "unconfirmed", "prior_review": "review/result.json",
                        "rereview": None, "prior_finding_count": len(findings), "reason": reason}
                    result["limitations"].append(reason)
                elif "annotation" not in revised and selected is not None:
                    reason = ("The shared repair did not produce a consistent revised "
                              "annotation. The original Task, CFG, annotation and their bound review "
                              "remain selected together; all original findings remain unresolved by this repair.")
                    mark("revision/review", "skipped", reason=reason)
                    revised_review = {"status": "not_run"}
                    result["repair_review"] = {"status": "unconfirmed", "prior_review": "review/result.json",
                        "rereview": None, "prior_finding_count": len(findings), "reason": reason}
                    result["limitations"].append(reason)
                else:
                    revised_review = source_review(revised, repair_errors, revision=True)
                if revised_review["status"] != "complete":
                    if revised_review["status"] != "not_run":
                        result["repair_review"] = {"status": "unconfirmed", "prior_review": "review/result.json",
                            "rereview": "revision/review/result.json", "prior_finding_count": len(findings)}
                    result["limitations"].append("The shared repair was not confirmed by a completed source re-review; "
                        "prior findings remain recorded in review/result.json and are not marked resolved.")
                if unchanged:
                    errors = {**errors, **repair_errors}
                elif "annotation" in revised:
                    chosen, selected, reviewed = revised, select(revised), revised_review
                    errors = repair_errors
                else:
                    result["limitations"].append("The shared repair did not form a consistent new annotation; retaining the original candidate."
                        if selected is not None else "The shared repair did not form a complete annotation; partial materials remain unselected.")
                    errors = {**errors, **repair_errors}
            findings = (reviewed.get("review") or {}).get("findings", [])
            result["graph_review"] = ("audit_passed" if reviewed["status"] == "complete"
                and not any(row["domain"] == "cfg" for row in findings)
                and "graph" in chosen and "graph" not in errors else "incomplete")
            result["annotation_review"] = ("review_passed" if selected is not None
                and reviewed["status"] == "complete" and not findings and not reviewed.get("diagnostic_only") else "incomplete")
            result["limitations"] += [name + ": " + detail["reason"] for name, detail in sorted(errors.items())]
            if reviewed["status"] != "complete":
                result["limitations"].append("Unified source review did not complete ("
                    + reviewed.get("error_type", reviewed["status"]) + "): "
                    + reviewed.get("reason", "No validated review is available")
                    + ("; independently validated records are retained with explicit local validation barriers."
                       if reviewed["status"] == "partial" else "; the selected candidate remains unreviewed."))
            elif reviewed.get("diagnostic_only"):
                result["limitations"].append("Unified source review is partial or retains material issues.")
            result["diagnostic_only"] = bool(result["limitations"])
            if selected is None:
                result.update(status="failed", reason="No executable annotation could be assembled; source review and valid fragments remain available")
            else:
                if replay:
                    expected = {"task": file_reference(run, chosen["task"]["path"]),
                                "cfg": file_reference(run, chosen["graph"]["path"]),
                                "annotation": file_reference(run, selected / "manifest.json")}
                    if read(run / "selection.json") != expected or read(run / "graph/selected.json") != {"cfg": chosen["graph"]["value"]}:
                        raise ValueError("Replayed selected bundle differs")
                mark("propagation")
                from skillflow.propagation.runner import run_propagation, replay_propagation, load_propagation_materials
                if replay:
                    facts = replay_propagation(run / "propagation")
                elif not (run / "propagation/manifest.json").exists():
                    facts = run_propagation(selected, run_dir=run / "propagation")
                else:
                    facts = load_propagation_materials(run / "propagation")
                from skillflow.common.upstream import make_run_reference
                if facts.manifest["upstream"] != make_run_reference(run / "propagation", selected):
                    raise ValueError("Propagation belongs to another selected annotation")
                mark("propagation", facts.status)
                if facts.status != "complete":
                    result["limitations"].append("Propagation is incomplete: " + facts.status)
                    result["diagnostic_only"] = True
                mark("doe")
                from skillflow.doe.formal_runner import run_doe, replay_doe, verify_uncommitted_doe
                from skillflow.doe.input_contract_review import build_input_contract_review
                receipt = build_input_contract_review(files=files, cfg=facts.cfg, annotation=facts.annotation,
                    review=reviewed, review_material=review_materials[id(reviewed)])
                _stable(run / "audit/input-contract-review.json", receipt, replay)
                if replay and not (run / "doe/manifest.json").exists():
                    if saved.get("status") != "failed" or saved.get("stage") != "doe":
                        raise ValueError("Missing DOE manifest without a recorded DOE failure")
                    verify_uncommitted_doe(run / "propagation", run_dir=run / "doe", input_contract_review=receipt)
                    raise ValueError("Previously failed DOE computation now succeeds")
                elif replay:
                    replay_doe(run / "doe")
                else:
                    run_doe(run / "propagation", run_dir=run / "doe", input_contract_review=receipt)
                doe_status = read(run / "doe/doe-result.json")["status"]
                mark("doe", doe_status)
                if doe_status != "complete":
                    result["limitations"].append("DOE retains analysis limitations: " + doe_status)
                    result["diagnostic_only"] = True
                result["status"] = "partial" if result["diagnostic_only"] else "complete"
        except KeyboardInterrupt as error:
            stopping.set()
            finish_running("interrupted", str(error))
            result.update(status="interrupted", reason=str(error))
        except Exception as error:
            stopping.set()
            reason = _failure_reason(error)
            finish_running("aborted", reason, current_status="failed")
            result.update(status="failed", reason=reason)
            if not replay:
                from .fatal_frontier import capture_fatal_frontier
                try:
                    frontier = capture_fatal_frontier(run, result, writer=WRITER, error=error)
                except Exception as frontier_error:
                    # Preserve the actual primary failure even if its audit
                    # receipt cannot be completed. This boundary is explicitly
                    # non-replayable; it never authorizes backend continuation.
                    result["fatal_frontier_error"] = _failure_reason(frontier_error)
                else:
                    if frontier is not None:
                        result["fatal_frontier"] = frontier
        return _save(run, result, replay=replay)


def replay(run_dir, *, renderer=None):
    return run(run_dir, replay=True, renderer=renderer)
