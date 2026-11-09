"""Prospective formal CLI comparison, isolated from calibration-only CLI-v3.

Import, inspection, preparation and replay never start a target. Only the
explicit dispatch_next_once entry point may start one already gated request.
No function creates a user authorization or an actual-human confirmation.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import time

from . import cli_adapter_v3 as cli
from . import cli_amendment_v3 as calibration
from . import execution as native
from . import reference_epoch
from .assessment import verify_human_reference_freeze
from .inputs import render_direct, render_review
from .long_preparation import verify_preparation
from .protocol import canonical_hash, sha256, utc_now, write_json

SCHEMA = "skillflow-real-comparison-formal-cli-v1"
AUTHORIZATION_SCHEMA = SCHEMA + "-authorization"
PROPOSAL_SCHEMA = SCHEMA + "-proposal"
ROOT = Path(__file__).resolve().parents[3]
LIMITS = dict(calibration.LIMITS)
IMPLEMENTATION = tuple("tools/doe/real_comparison/" + name + ".py" for name in (
    "formal_cli", "formal_cli_metrics", "cli_adapter_v3", "cli_amendment_v3",
    "execution", "inputs", "protocol", "reference_epoch", "long_preparation",
    "assessment", "artifacts", "results", "review", "metrics", "efficiency", "semantic_metrics",
    "selection_readiness", "corrigenda"))


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def inside(root, relative):
    root = Path(root).resolve()
    path = root / relative
    if (path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file()
            or any(p.is_symlink() for p in path.parents if p != root and p.is_relative_to(root))):
        raise native.ExecutionStop("A formal evidence file is missing, linked or outside its root: " + str(relative))
    return path.resolve()


def tree_hashes(root):
    root = Path(root).resolve()
    return {p.relative_to(root).as_posix(): sha256(inside(root, p.relative_to(root)))
            for p in sorted(root.rglob("*")) if p.is_file()}


def _verify_tree(root, files):
    for relative, digest in files.items():
        if sha256(inside(root, relative)) != digest:
            raise native.ExecutionStop("Frozen formal authority bytes changed: " + str(relative))


def effective_policy():
    result = calibration.effective_policy()
    result["schema_version"] = SCHEMA
    result["selection"].update(minimum_operational_nonempty_lines=600,
        alternative_cross_referenced_operational_files=8, minimum_source_evidenced_features=3,
        minimum_reference_tokens=20000, operative_file_rule="Apply the exact frozen 600-line/eight-operative-file/three-feature rules and source-only proofs. Entry-root reachability does not itself earn an operative-file count.")
    result["run_scope"] = {"formal_comparison": True, "calibration_only": False,
        "formal_dispatch": "requires_separate_exact_user_protocol_and_human_reference_gate",
        "calibration_v3_scope": "Permanently calibration-only; unchanged and never inherited as formal authority."}
    result["protocol_precedence"] = "This separately authorized formal CLI protocol governs this new run only. Comparative and human rules remain; historical collaboration and calibration authority grant no formal dispatch."
    return result


def _schedule(cohort):
    selection, schedule = read(cohort / "selection.json"), read(cohort / "schedule.json")
    cases = selection.get("selected", []) + selection.get("reserves", [])
    if (len(selection.get("selected", [])) != 24 or len(selection.get("reserves", [])) != 6
            or len({c.get("case_id") for c in cases}) != 30):
        raise native.ExecutionStop("The formal cohort requires exactly 24 cases and six reserves")
    expected = {(c["case_id"], m, r) for c in cases[:24] for m in ("skillflow", "audit", "chain") for r in (1, 2, 3)}
    reviews = {(c["case_id"], m, 1) for c in cases[:24] for m in ("audit", "chain")}
    identity = lambda rows: {(i.get("case_id"), i.get("method"), i.get("repeat")) for i in rows}
    main, fixed = schedule.get("main", []), schedule.get("reviews", [])
    if (len(main) != 216 or len(fixed) != 48 or identity(main) != expected or identity(fixed) != reviews
            or len({i.get("workflow_id") for i in main + fixed}) != 264
            or any(i.get("kind") != "main" for i in main) or any(i.get("kind") != "review" for i in fixed)):
        raise native.ExecutionStop("The complete fixed 216+48 schedule is required")
    by_id = {i["workflow_id"]: i for i in main}
    case_map = {c["case_id"]: c for c in cases}
    for item in main + fixed:
        expected_id = f"{item['case_id']}_{item['method']}_r{item['repeat']}" + ("_review" if item["kind"] == "review" else "")
        if item["workflow_id"] != expected_id:
            raise native.ExecutionStop("A fixed workflow identity differs from its case, method and repeat")
        if item.get("source_sha256") != case_map[item["case_id"]]["source_sha256"] or "user_request" in item:
            raise native.ExecutionStop("A scheduled case/source or declared-purpose identity differs")
        if item["kind"] == "review":
            original = by_id.get(item.get("original_workflow_id"), {})
            if (original.get("repeat") != 1 or any(original.get(k) != item.get(k)
                    for k in ("case_id", "source_sha256", "method", "repeat"))):
                raise native.ExecutionStop("A fixed review must bind the exact same-case/method first repetition")
    for item in main:
        if item["method"] != "skillflow":
            if inside(cohort, "prepared-prompts/" + item["workflow_id"] + ".txt").read_bytes() != render_direct(cohort, item["case_id"], item["method"]).encode("utf-8"):
                raise native.ExecutionStop("A complete direct prompt differs from frozen source and rules")
    return selection, schedule


def _replay_request(directory):
    """Read-only exact CLI evidence check; exports no reasoning or new answer."""
    request, dispatch = read(directory / "request.json"), read(directory / "dispatch.json")
    saved, response = read(directory / "receipt.json"), read(directory / "response.json")
    core = inside(directory, "core-prompt.txt").read_bytes().decode("utf-8")
    if (sha256(directory / "core-prompt.txt") != request["core_sha256"]
            or sha256(directory / "prompt.txt") != request["delivery_sha256"]
            or (directory / "prompt.txt").read_bytes() != native.ENVELOPE.replace("{core}", core).encode("utf-8")):
        raise native.ExecutionStop("The exact complete CLI material changed")
    launch = read(directory / "cli/launch.json")
    if (dispatch.get("command") != launch["command"]
            or launch["command"] != cli.command(launch["command"][0], directory / "cli")
            or launch.get("stdin_sha256") != request["delivery_sha256"]
            or saved.get("stdin_sha256") != request["delivery_sha256"]
            or Path(launch.get("stdin_file", "")).resolve() != (directory / "prompt.txt").resolve()
            or Path(launch.get("output_dir", "")).resolve() != (directory / "cli").resolve()
            or Path(launch.get("empty_workdir", "")).resolve() != (directory.parents[2] / "empty-cwd" / directory.name).resolve()
            or launch.get("runtime_expectation") != cli.EXPECTED
            or launch.get("expected_cli_version") != cli.PINNED_VERSION
            or launch.get("executable_sha256") != cli.PINNED_EXECUTABLE_SHA256
            or launch.get("base_instructions_sha256") != cli.PINNED_BASE_INSTRUCTIONS_SHA256
            or launch.get("developer_segment_sha256") != [list(p) for p in cli.PINNED_DEVELOPER_SEGMENTS]
            or saved.get("process_result_sha256") != sha256(directory / "cli/process-result.json")
            or saved.get("stdout_sha256") != sha256(directory / "cli/stdout.jsonl")):
        raise native.ExecutionStop("The exact CLI launch/process binding changed")
    process = read(directory / "cli/process-result.json")
    if (process.get("status") != "process_exited" or process.get("returncode") != 0
            or read(directory / "cli/process-start.json").get("actual_cli_process_started") is not True):
        raise native.ExecutionStop("No successful actual CLI process is proven")
    answer, fresh = cli.inspect_receipt(saved["raw_receipt_path"], saved["cli_session_id"], launch,
        stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
    if (any(saved.get(k) != v for k, v in fresh.items()) or response.get("accepted") is not True
            or fresh.get("protocol_status") != "conformant" or fresh.get("usage_verified") is not True
            or fresh.get("configuration_verified") is not True or fresh.get("provider_verified") is not True
            or fresh.get("completed") is not True or answer is None
            or response.get("answer") != answer or response.get("answer_sha256") != cli.digest(answer)):
        raise native.ExecutionStop("Allowlisted CLI receipt facts or saved answer differ on replay")
    if (not fresh.get("usage", {}).get("by_response_id")
            or any(type(v) is not int or v < 0 for v in fresh.get("usage", {}).get("totals", {}).values())
            or set(fresh.get("usage", {}).get("totals", {})) != set(cli.TOKEN_FIELDS)):
        raise native.ExecutionStop("Actual CLI response usage must be fully known and nonnegative")
    return saved


def _calibration_evidence(run):
    run = Path(run).resolve()
    if any((run / name).exists() for name in ("dispatch-stop.json", "user-pause.json", "pause-state.json", "dispatcher.lock")):
        raise native.ExecutionStop("A paused or stopped calibration cannot authorize formal execution")
    calibration.verify_run(run)
    summary = calibration.summarize_calibrations(run)
    if summary.get("status") != "passed_engineering_only" or summary.get("runtime") != cli.EXPECTED:
        raise native.ExecutionStop("All three complete replay-verified same-runtime CLI calibrations are required")
    replay = read(run / "replay/summary.json")
    requests = native._requests(run)
    plan = read(run / "calibration-plan.json")["cases"]
    if (len(plan) != 3 or {i["case_id"] for i in plan} != set(native.CALIBRATION)
            or len({i["workflow_id"] for i in plan}) != 3
            or {i.get("case_id") for i in replay.get("native_replays", []) if i.get("status") == "matched"} != set(native.CALIBRATION)
            or {i.get("request_id") for i in replay.get("request_replays", []) if i.get("status") == "matched"} != {p.name for p, _ in requests}
            or not requests or replay.get("status") != "passed" or replay.get("model_calls") != 0):
        raise native.ExecutionStop("The three native replay proofs and every actual request must be bound")
    required = {str((p / "request.json").relative_to(run)).replace("\\", "/") for p, _ in requests}
    required |= {"workflows/" + i["workflow_id"] + "/result.json" for i in plan}
    if not required.issubset(replay.get("bindings", {})):
        raise native.ExecutionStop("Calibration replay omits mandatory request/result bindings")
    _verify_tree(run, replay["bindings"])
    raw, sessions, responses = {}, set(), set()
    for directory, request in requests:
        if request.get("mode") != "calibration" or request.get("transport") != cli.TRANSPORT:
            raise native.ExecutionStop("Calibration request transport or scope differs")
        receipt = _replay_request(directory)
        ids = set(receipt["usage"]["by_response_id"])
        if receipt["cli_session_id"] in sessions or ids & responses:
            raise native.ExecutionStop("Calibration reused a CLI session or response identity")
        sessions.add(receipt["cli_session_id"])
        responses.update(ids)
        raw[receipt["raw_receipt_path"]] = sha256(receipt["raw_receipt_path"])
    from .artifacts import verify_candidate
    for item in plan:
        saved = read(run / "workflows" / item["workflow_id"] / "result.json")
        if (saved.get("status") not in {"complete", "diagnostic"}
                or saved.get("native", {}).get("analysis", {}).get("stage") != "finished"
                or saved.get("graph_reused") is not False or saved.get("native_core_modified") is not False
                or saved.get("attempts") != 1):
            raise native.ExecutionStop("Each calibration must be a complete fresh unchanged native pipeline")
        verify_candidate(run, item["workflow_id"], saved)
    usage = native.usage_summary(run)
    if usage["missing_requests"] or usage["conflicting_response_ids"] or any(v is None for v in usage["totals"].values()):
        raise native.ExecutionStop("Calibration usage must be complete and accountable")
    return {"files": tree_hashes(run), "raw_receipts": raw,
            "production_implementation": read(run / "production-code-freeze.json")["implementation"]}


def inspect_bindings(*, cohort_run, reference_workspace, calibration_run, executable):
    """Read-only prerequisite verification; returns authority for a future proposal."""
    cohort, epoch, cal = map(lambda p: Path(p).resolve(), (cohort_run, reference_workspace, calibration_run))
    origin = read(epoch / "reference-epoch-origin.json")
    if Path(origin["parent_preparation"]).resolve() != cohort:
        raise native.ExecutionStop("The reference epoch belongs to a different source preparation")
    if verify_preparation(cohort, origin["corpus_root"]).get("status") != "passed":
        raise native.ExecutionStop("The exact long-source preparation no longer verifies")
    current_selection = reference_epoch.current_selection_binding(epoch)
    selection, _ = _schedule(cohort)
    verified = reference_epoch.verify_reference_epoch(epoch)
    if (verified.get("integrity") != "verified" or verified.get("cases") != 30
            or verified.get("complete_draft_schema_and_quotes") != 30
            or verified.get("reference_epoch_sealed") is not True
            or verified.get("actual_active_confirmations") != 60
            or verified.get("actual_roster_imported") is not True):
        raise native.ExecutionStop("Thirty complete semantic ledgers and sixty actual current-version human confirmations are required")
    if sha256(epoch / "selection.json") != sha256(cohort / "selection.json"):
        raise native.ExecutionStop("The approved reference epoch uses a different case set")
    approved = read(epoch / "approved-source-set.json")["cases"]
    expected = [{"case_id": c["case_id"], "canonical_id": c["canonical_id"], "source_sha256": c["source_sha256"],
        "source_tree_sha256": c["source_tree_sha256"], "source_bundle_sha256": c["bundle_sha256"],
        "reference_sha256": sha256(epoch / "references" / (c["case_id"] + ".json"))}
        for c in selection["selected"] + selection["reserves"]]
    if approved != expected:
        raise native.ExecutionStop("Approved references must bind every exact final source and reference version")
    evidence = _calibration_evidence(cal)
    from skillflow.common.recording import implementation_provenance
    production = implementation_provenance()
    if production != evidence["production_implementation"]:
        raise native.ExecutionStop("Formal production differs from the replay-verified calibrations")
    executable = Path(executable).resolve()
    if not executable.is_file() or sha256(executable) != cli.PINNED_EXECUTABLE_SHA256:
        raise native.ExecutionStop("The formal CLI executable differs from its calibrated pin")
    return {"cohort_run": str(cohort), "reference_workspace": str(epoch), "calibration_run": str(cal),
        "cohort_freeze_sha256": sha256(cohort / "preparation-freeze.json"),
        "selection_sha256": sha256(cohort / "selection.json"), "schedule_sha256": sha256(cohort / "schedule.json"),
        "approved_source_set_sha256": sha256(epoch / "approved-source-set.json"),
        "reference_epoch_freeze_sha256": sha256(epoch / "reference-epoch-freeze.json"),
        "reference_freeze_sha256": sha256(epoch / "reference-freeze.json"),
        "reference_epoch_files": tree_hashes(epoch), "calibration_evidence": evidence,
        "current_source_selection": current_selection,
        "production_implementation": production, "executable": str(executable), "executable_sha256": sha256(executable),
        "implementation_files": {p: sha256(ROOT / p) for p in IMPLEMENTATION}, "protocol": effective_policy()}


def _authorization(decision_path, proposal_path, bindings):
    decision, proposal = read(decision_path), read(proposal_path)
    if (proposal.get("schema_version") != PROPOSAL_SCHEMA or proposal.get("bindings") != bindings
            or proposal.get("protocol") != effective_policy()):
        raise native.ExecutionStop("The formal proposal must bind exact final source, approved references, runtime, code and calibration evidence")
    required = {"schema_version": AUTHORIZATION_SCHEMA, "state": "adopted", "user_authorized": True,
        "formal_dispatch_permitted": True, "calibration_only": False, "automatic_retry": False,
        "proposal_sha256": sha256(proposal_path), "bindings_sha256": canonical_hash(bindings)}
    if any(type(decision.get(k)) is not type(v) or decision.get(k) != v for k, v in required.items()):
        raise native.ExecutionStop("New explicit exact formal protocol approval is required; calibration authorization is insufficient")
    confirmation = decision.get("user_confirmation", {})
    if not isinstance(confirmation, dict) or any(not isinstance(confirmation.get(k), str) or not confirmation[k].strip()
           for k in ("quotation", "conversation_reference")):
        raise native.ExecutionStop("Actual formal user approval needs its quotation and conversation reference")
    return decision


def inspect_readiness(**kwargs):
    """Report a blocked gate without creating any run, approval or request."""
    try:
        bindings = inspect_bindings(**{k: kwargs[k] for k in (
            "cohort_run", "reference_workspace", "calibration_run", "executable")})
        _authorization(kwargs["decision_record"], kwargs["protocol_proposal"], bindings)
        return {"schema_version": SCHEMA, "ready": True, "bindings_sha256": canonical_hash(bindings), "model_calls": 0}
    except (OSError, ValueError, KeyError, native.ExecutionStop) as error:
        reasons = [str(error)]
        # Independent blocked prerequisites remain visible even when an earlier
        # missing reference epoch prevented construction of complete bindings.
        try:
            _calibration_evidence(kwargs["calibration_run"])
        except (OSError, ValueError, KeyError, native.ExecutionStop) as calibration_error:
            if str(calibration_error) not in reasons:
                reasons.append(str(calibration_error))
        return {"schema_version": SCHEMA, "ready": False, "reason": reasons[0], "reasons": reasons,
                "model_calls": 0, "actual_cli_processes_started": 0}


def _copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def prepare_formal_run(new_run, *, cohort_run, reference_workspace, calibration_run,
                       protocol_proposal, decision_record, executable):
    """Future gated preparation only. No target process is started."""
    run = Path(new_run).resolve()
    for path in (cohort_run, reference_workspace, calibration_run):
        prior = Path(path).resolve()
        if run == prior or run.is_relative_to(prior) or prior.is_relative_to(run):
            raise native.ExecutionStop("Use a fresh nonoverlapping formal run; preserve prior workspaces")
    if run.exists():
        raise native.ExecutionStop("A formal run directory cannot already exist")
    bindings = inspect_bindings(cohort_run=cohort_run, reference_workspace=reference_workspace,
        calibration_run=calibration_run, executable=executable)
    _authorization(decision_record, protocol_proposal, bindings)
    cohort, epoch = Path(cohort_run).resolve(), Path(reference_workspace).resolve()
    run.mkdir(parents=True)
    # Only source/rules/schedule/assignment material is imported from preparation.
    for relative in read(cohort / "preparation-freeze.json")["files"]:
        if relative.startswith(("cases/", "prompts/", "prepared-prompts/", "review/")) or relative in (
                "selection.json", "schedule.json", "grading-contract.json", "common-assumptions.md",
                "common-runtime-contract.json", "rubric.md", "evaluation-rules-supplement-v1.md"):
            _copy(inside(cohort, relative), run / relative)
    for relative in tree_hashes(epoch):
        if relative.startswith(("references/", "approvals/")) or relative in (
                "references.json", "reference-freeze.json", "human-roster.json"):
            _copy(inside(epoch, relative), run / relative)
    _copy(Path(protocol_proposal), run / "authorization/proposal.json")
    _copy(Path(decision_record), run / "authorization/adoption.json")
    write_json(run / "formal-protocol.json", effective_policy(), immutable=True)
    native.snapshot_production_code(run)
    materials = tree_hashes(run)
    write_json(run / "materials-freeze.json", {"schema_version": SCHEMA, "files": materials,
        "references_and_scores_in_target_view": False}, immutable=True)
    gate = {"schema_version": SCHEMA, "state": "approved", "bindings": bindings,
        "materials_freeze_sha256": sha256(run / "materials-freeze.json"),
        "proposal_sha256": sha256(run / "authorization/proposal.json"),
        "adoption_sha256": sha256(run / "authorization/adoption.json"),
        "created_at": utc_now(), "formal_requests": 0, "automatic_retry": False}
    write_json(run / "formal-gate.json", gate, immutable=True)
    verify_formal_gate(run)
    return {"schema_version": SCHEMA, "state": "prepared_formal_cli", "main": 216,
            "fixed_reviews": 48, "formal_requests": 0, "model_calls": 0}


def verify_formal_gate(run_dir, *, generation=True):
    run = Path(run_dir).resolve()
    gate = read(run / "formal-gate.json")
    if gate.get("schema_version") != SCHEMA or gate.get("state") != "approved" or gate.get("automatic_retry") is not False:
        raise native.ExecutionStop("A separately approved formal CLI gate is required")
    if generation and any((run / name).exists() for name in ("dispatch-stop.json", "output-freeze.json", "user-pause.json", "pause-state.json")):
        raise native.ExecutionStop("Formal generation is stopped or closed")
    bindings = gate["bindings"]
    current = inspect_bindings(**{k: bindings[k] for k in (
        "cohort_run", "reference_workspace", "calibration_run", "executable")})
    if current != bindings:
        raise native.ExecutionStop("Formal source, reference, runtime, implementation or calibration authority changed")
    if (sha256(run / "materials-freeze.json") != gate["materials_freeze_sha256"]
            or sha256(run / "authorization/proposal.json") != gate["proposal_sha256"]
            or sha256(run / "authorization/adoption.json") != gate["adoption_sha256"]):
        raise native.ExecutionStop("The formal freeze or explicit approval changed")
    _authorization(run / "authorization/adoption.json", run / "authorization/proposal.json", current)
    _verify_tree(run, read(run / "materials-freeze.json")["files"])
    _schedule(run)
    verify_human_reference_freeze(run)
    native.verify_production_code(run)
    return gate


def _planned(run, workflow_id):
    workflow_id = native._name(workflow_id)
    schedule = read(Path(run) / "schedule.json")
    matches = [i for i in schedule["main"] + schedule["reviews"] if i["workflow_id"] == workflow_id]
    if len(matches) != 1:
        raise native.ExecutionStop("Only an exact prespecified formal workflow may run")
    return matches[0]


def _registration(run, workflow_id):
    item = _planned(run, workflow_id)
    registration = read(native._workflow(run, workflow_id) / "registration.json")
    if (any(registration.get(k) != v for k, v in item.items())
            or registration.get("mode") != "formal" or registration.get("runtime") != cli.EXPECTED
            or registration.get("transport") != cli.TRANSPORT
            or registration.get("source_path") != str((Path(run) / "cases" / item["case_id"] / "source").resolve())):
        raise native.ExecutionStop("Workflow registration differs from its fixed source/method/repeat/runtime")
    return registration


def _review_original(run, item):
    original_id = item.get("original_workflow_id")
    original = _planned(run, original_id)
    if (item["kind"] != "review" or original["kind"] != "main" or item["method"] not in {"audit", "chain"}
            or original["repeat"] != 1 or any(original[k] != item[k] for k in ("case_id", "method", "source_sha256", "repeat"))):
        raise native.ExecutionStop("A fixed review must bind its exact same-case/method R1 main answer")
    directory = native._workflow(run, original_id)
    if not (directory / "answer.txt").exists():
        return None
    _registration(run, original_id)
    result = read(directory / "result.json")
    if result.get("status") != "complete" or result.get("answer_sha256") != sha256(directory / "answer.txt"):
        raise native.ExecutionStop("The exact original R1 answer is incomplete or changed")
    from .artifacts import verify_candidate
    verify_candidate(run, original_id, result)
    return (directory / "answer.txt").read_bytes().decode("utf-8")


def _verify_prompt(run, registration, prompt):
    if registration["method"] == "skillflow":
        return
    item = _planned(run, registration["workflow_id"])
    if item["kind"] == "review":
        original = _review_original(run, item)
        if original is None:
            raise native.ExecutionStop("Missing original R1 is not reviewable; no replacement is permitted")
        expected = render_review(run, item["case_id"], item["method"], original)
        original_record = read(native._workflow(run, item["workflow_id"]) / "original.json")
        if original_record != {"original_workflow_id": item["original_workflow_id"], "answer_sha256": cli.digest(original)}:
            raise native.ExecutionStop("The fixed review's exact original-answer binding changed")
    else:
        expected = render_direct(run, item["case_id"], item["method"])
    if prompt != expected:
        raise native.ExecutionStop("The complete direct/review prompt differs from its frozen source, rules or R1 answer")


def _budget(run, workflow_id, *, dispatching=False, now=None):
    from .formal_cli_metrics import process_started, usage_summary
    now = time.time() if now is None else now
    started = read(native._workflow(run, workflow_id) / "state.json")["started_at"]
    if now - native._seconds(started) >= LIMITS["workflow_seconds"]:
        raise native.ExecutionStop("The six-hour workflow budget is exhausted")
    requests = native._requests(run, workflow_id)
    actual = [p for p, _ in requests if process_started(p)]
    if dispatching and len(actual) >= LIMITS["actual_cli_requests"]:
        raise native.ExecutionStop("The 64 actual CLI-process workflow budget is exhausted")
    for directory, _ in requests:
        if (directory / "stop.json").exists():
            raise native.ExecutionStop("A retained stopped request forbids workflow continuation")
        if (directory / "dispatch.json").exists():
            if not (directory / "response.json").exists():
                when = read(directory / "dispatch.json")["dispatched_at"]
                if now - native._seconds(when) >= LIMITS["outstanding_request_seconds"]:
                    raise native.ExecutionStop("The 45-minute outstanding request limit is exhausted")
                if dispatching:
                    raise native.ExecutionStop("A previous dispatch attempt remains unresolved")
            elif read(directory / "response.json").get("accepted") is not True:
                raise native.ExecutionStop("A rejected response forbids workflow continuation")
    usage = usage_summary(run, workflow_id)
    if usage["conflicting_response_ids"] or usage["reused_response_ids"]:
        raise native.ExecutionStop("Conflicting or reused response identities forbid dispatch")
    completed = all((p / "response.json").exists() for p in actual)
    if (actual or usage["unknown_process_start_requests"]) and (dispatching or completed) and (usage["missing_requests"] or any(v is None for v in usage["totals"].values())):
        raise native.ExecutionStop("Unknown per-response usage forbids further dispatch")
    total = usage["totals"]["total_tokens"]
    if total is not None and total >= LIMITS["reported_total_tokens"]:
        raise native.ExecutionStop("The reported eight-million-token workflow budget is exhausted")


def _stop(run, request_id, reason):
    directory = Path(run) / "mailbox/requests" / native._name(request_id)
    if not (directory / "stop.json").exists():
        write_json(directory / "stop.json", {"reason": str(reason), "stopped_at": utc_now()}, immutable=True)
    if not (Path(run) / "dispatch-stop.json").exists():
        write_json(Path(run) / "dispatch-stop.json", {"schema_version": SCHEMA, "request_id": request_id,
            "reason": str(reason), "stopped_at": utc_now(), "automatic_retry": False}, immutable=True)


def authorize_dispatch(run_dir, request_id):
    """Recheck every authority and exact request immediately before a launch."""
    run = Path(run_dir).resolve()
    verify_formal_gate(run)
    directory = run / "mailbox/requests" / native._name(request_id)
    request = read(directory / "request.json")
    if any((directory / p).exists() for p in ("dispatch.json", "response.json", "stop.json")):
        raise native.ExecutionStop("A request identity cannot be retried, replaced or dispatched twice")
    core = inside(directory, "core-prompt.txt").read_bytes().decode("utf-8")
    delivery = native.ENVELOPE.replace("{core}", core)
    count = native.reference_tokens(delivery)
    if (request.get("schema_version") != SCHEMA or request.get("mode") != "formal"
            or request.get("transport") != cli.TRANSPORT or request.get("runtime") != cli.EXPECTED
            or request.get("request_id") != request_id or type(request.get("sequence")) is not int
            or request_id != f"{request.get('workflow_id')}_q{request['sequence']:03d}"
            or request["sequence"] < 1 or request.get("core_sha256") != cli.digest(core)
            or request.get("delivery_sha256") != cli.digest(delivery)
            or inside(directory, "prompt.txt").read_bytes() != delivery.encode("utf-8")
            or request.get("reference_tokens") != count):
        raise native.ExecutionStop("The complete formal CLI request, source envelope or runtime binding changed")
    if count > LIMITS["delivered_reference_tokens"]:
        raise native.ExecutionStop("The complete delivery exceeds 300,000 reference tokens; clipping is forbidden")
    registration = _registration(run, request["workflow_id"])
    _verify_prompt(run, registration, core)
    ordered = native._requests(run, request["workflow_id"])
    if [r.get("sequence") for _, r in ordered] != list(range(1, len(ordered) + 1)):
        raise native.ExecutionStop("Formal workflow request sequences must be unique and contiguous from one")
    for other, _ in native._requests(run):
        if (other / "dispatch.json").exists():
            if not (other / "response.json").exists():
                raise native.ExecutionStop("Another dispatch attempt remains unresolved")
            _replay_request(other)
    _budget(run, request["workflow_id"], dispatching=True)
    return request


@contextmanager
def _dispatch_lock(run):
    lock = Path(run) / "dispatcher.lock"
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise native.ExecutionStop("An existing dispatcher lock forbids a duplicate launch; preserve it") from error
    try:
        with stream:
            stream.write(utc_now())
        yield
    finally:
        lock.unlink(missing_ok=True)


def dispatch_next_once(run_dir, *, process_factory=None, sessions_dir=None):
    """The sole target-process entry point; service one gated request without retry."""
    from tools.doe.direct_baseline import DEFAULT_SESSIONS, find_receipt
    run = Path(run_dir).resolve()
    # A historical calibration or incomplete state cannot even obtain a lock.
    gate = verify_formal_gate(run)
    with _dispatch_lock(run):
        pending = native.pending_requests(run)
        if not pending:
            return {"status": "no_pending_request", "actual_cli_process_started": False}
        request_id = pending[0]["request_id"]
        directory = run / "mailbox/requests" / request_id
        try:
            request = authorize_dispatch(run, request_id)
            cwd = run / "empty-cwd" / request_id
            cwd.mkdir(parents=True, exist_ok=False)
            prepared = cli.prepare_launch(gate["bindings"]["executable"], directory / "prompt.txt", directory / "cli", cwd)
            # This final check occurs after launch material is prepared and
            # before either a dispatch record or a target process exists.
            authorize_dispatch(run, request_id)
        except Exception as error:
            _stop(run, request_id, f"Predispatch validation failed: {type(error).__name__}: {error}")
            raise
        write_json(directory / "dispatch.json", {"schema_version": SCHEMA, "transport": cli.TRANSPORT,
            "request_id": request_id, "dispatched_at": utc_now(), "command": prepared["command"],
            "planned_prompt_sha256": request["delivery_sha256"], "protocol_conformant": True,
            "actual_process_evidence": "cli/process-start.json", "collaboration_spawn": False}, immutable=True)
        started = read(native._workflow(run, request["workflow_id"]) / "state.json")["started_at"]
        remaining = LIMITS["workflow_seconds"] - (time.time() - native._seconds(started))
        try:
            process = cli.execute_launch(prepared,
                timeout_seconds=min(LIMITS["outstanding_request_seconds"], remaining), popen=process_factory)
        except Exception as error:
            output = directory / "cli"
            output.mkdir(exist_ok=True)
            for name in ("stdout.jsonl", "stderr.txt"):
                (output / name).touch(exist_ok=True)
            process = {"status": "prelaunch_error", "returncode": None, "actual_cli_process_started": False,
                "supervisor_elapsed_seconds": 0., "error": f"{type(error).__name__}: {error}", "retries": 0}
            write_json(output / "process-result.json", process, immutable=True)
        answer = None
        receipt = {"protocol_status": "unverified", "configuration_verified": False, "provider_verified": False,
            "usage_verified": False, "completed": False, "violations": [],
            "usage": {"by_response_id": {}, "totals": {k: None for k in cli.TOKEN_FIELDS}}}
        try:
            session_id = cli.session_from_stdout(directory / "cli/stdout.jsonl")
            raw = find_receipt(session_id, sessions_dir or DEFAULT_SESSIONS)
            answer, receipt = cli.inspect_receipt(raw, session_id, prepared,
                stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
            receipt["raw_receipt_path"] = str(raw.resolve())
            for other, _ in native._requests(run):
                if not (other / "receipt.json").exists():
                    continue
                prior = read(other / "receipt.json")
                if session_id == prior.get("cli_session_id"):
                    receipt["violations"].append("An actual CLI session identity was reused")
                if set(prior.get("usage", {}).get("by_response_id", {})) & set(receipt["usage"]["by_response_id"]):
                    receipt["violations"].append("An actual response identity was reused")
        except Exception as error:
            receipt["violations"].append(f"Actual receipt inspection failed: {type(error).__name__}: {error}")
        if process["status"] != "process_exited" or process["returncode"] != 0:
            receipt["violations"].append("The actual CLI process did not exit successfully")
        receipt.update(request_id=request_id, process_result_sha256=sha256(directory / "cli/process-result.json"),
            stdout_sha256=sha256(directory / "cli/stdout.jsonl"), stdin_sha256=prepared["stdin_sha256"],
            executable_sha256=prepared["executable_sha256"])
        if receipt["violations"]:
            receipt["protocol_status"] = "violated"
        counters = receipt.get("usage", {}).get("totals", {})
        known_usage = (set(counters) == set(cli.TOKEN_FIELDS) and all(type(v) is int and v >= 0 for v in counters.values())
                       and bool(receipt.get("usage", {}).get("by_response_id")))
        accepted = (receipt.get("protocol_status") == "conformant" and receipt.get("usage_verified") is True and known_usage
            and receipt.get("configuration_verified") is True and receipt.get("provider_verified") is True
            and receipt.get("completed") is True and answer is not None)
        write_json(directory / "receipt.json", receipt, immutable=True)
        write_json(directory / "response.json", {"request_id": request_id, "accepted": accepted, "answer": answer,
            "answer_sha256": cli.digest(answer) if answer is not None else None, "imported_at": utc_now()}, immutable=True)
        native.assess_request_protocol(directory, persist=True)
        if not accepted:
            _stop(run, request_id, "A failed, nonconforming or unaccountable request forbids every further dispatch")
        else:
            try:
                _budget(run, request["workflow_id"])
            except native.ExecutionStop as error:
                _stop(run, request_id, str(error))
        from .formal_cli_metrics import process_started
        return {"request_id": request_id, "status": "accepted" if accepted else "stopped",
            "actual_cli_process_started": process_started(directory), "violations": receipt["violations"]}


class FormalCliClient:
    """Production complete(prompt) injection with fresh immutable CLI mailboxes."""
    def __init__(self, run, workflow_id, *, token_counter=None, stop_event=None, poll_seconds=.5):
        self.run, self.workflow_id = Path(run), workflow_id
        self.counter, self.stop_event = token_counter or native.reference_tokens, stop_event
        self.poll_seconds, self.cursor, self.wait_seconds = poll_seconds, 0, 0.

    def complete(self, prompt):
        if not isinstance(prompt, str):
            raise TypeError("The production semantic prompt must be text")
        verify_formal_gate(self.run)
        _verify_prompt(self.run, _registration(self.run, self.workflow_id), prompt)
        delivery = native.ENVELOPE.replace("{core}", prompt)
        tokens = self.counter(delivery)
        if type(tokens) is not int or tokens < 0 or tokens > LIMITS["delivered_reference_tokens"]:
            raise native.ExecutionStop("The complete delivery exceeds the reference-token limit; clipping is forbidden")
        _budget(self.run, self.workflow_id, dispatching=True)
        self.cursor += 1
        identity = f"{self.workflow_id}_q{self.cursor:03d}"
        directory = self.run / "mailbox/requests" / identity
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "core-prompt.txt").write_bytes(prompt.encode("utf-8"))
        (directory / "prompt.txt").write_bytes(delivery.encode("utf-8"))
        write_json(directory / "request.json", {"schema_version": SCHEMA, "request_id": identity,
            "workflow_id": self.workflow_id, "sequence": self.cursor, "mode": "formal", "created_at": utc_now(),
            "core_sha256": cli.digest(prompt), "delivery_sha256": cli.digest(delivery), "reference_tokens": tokens,
            "runtime": cli.EXPECTED, "transport": cli.TRANSPORT}, immutable=True)
        start = time.perf_counter()
        try:
            while not (directory / "response.json").exists():
                if self.stop_event is not None and self.stop_event.is_set():
                    _stop(self.run, identity, "Worker interrupted; pending request retained without resume or retry")
                    raise KeyboardInterrupt("Formal worker interrupted")
                if (self.run / "dispatch-stop.json").exists():
                    if not (directory / "dispatch.json").exists():
                        _stop(self.run, identity, "The retained global stop terminalized this unlaunched queued request")
                    raise native.ExecutionStop("A retained global dispatch stop forbids continuation")
                try:
                    _budget(self.run, self.workflow_id)
                except native.ExecutionStop as error:
                    _stop(self.run, identity, str(error))
                    raise
                time.sleep(self.poll_seconds)
            saved = _replay_request(directory)
            # A reported token/time boundary stops the next publication and
            # dispatch. It must not erase this already accepted conformant
            # response, including a workflow's final semantic stage.
            verify_formal_gate(self.run, generation=False)
            if (self.run / "output-freeze.json").exists():
                raise native.ExecutionStop("Closed output generation cannot consume a new response")
            if saved.get("usage_verified") is not True:
                raise native.ExecutionStop("Unknown actual response usage forbids continuation")
            return read(directory / "response.json")["answer"]
        finally:
            self.wait_seconds += time.perf_counter() - start


def run_planned_workflow(run_dir, workflow_id, *, renderer=None, stop_event=None, token_counter=None):
    """Run one fixed identity from source; no restart, semantic cache or extra polish."""
    from .artifacts import seal_candidate
    from .formal_cli_metrics import usage_summary
    run = Path(run_dir).resolve()
    verify_formal_gate(run)
    item = _planned(run, workflow_id)
    directory = native._workflow(run, workflow_id)
    if directory.exists():
        raise native.ExecutionStop("A planned workflow cannot be retried, resumed or replaced")
    original = _review_original(run, item) if item["kind"] == "review" else None
    directory.mkdir(parents=True)
    source = run / "cases" / item["case_id"] / "source"
    write_json(directory / "registration.json", {**item, "source_path": str(source.resolve()), "mode": "formal",
        "runtime": cli.EXPECTED, "transport": cli.TRANSPORT}, immutable=True)
    write_json(directory / "state.json", {"started_at": utc_now()}, immutable=True)
    if item["kind"] == "review" and original is None:
        result = {"workflow_id": workflow_id, "status": "not_reviewable", "reason": "Exact R1 answer unavailable; no replacement",
            "answer_sha256": None, "finished_at": utc_now(), "attempts": 0, "usage": usage_summary(run, workflow_id)}
        write_json(directory / "result.json", result, immutable=True)
        return result
    if original is not None:
        write_json(directory / "original.json", {"original_workflow_id": item["original_workflow_id"],
            "answer_sha256": cli.digest(original)}, immutable=True)
    attempt = directory / "attempts/001"
    attempt.mkdir(parents=True)
    client = FormalCliClient(run, workflow_id, token_counter=token_counter, stop_event=stop_event)
    result = {"schema_version": SCHEMA, "workflow_id": workflow_id, "status": "failed", "answer_sha256": None,
        "graph_reused": False, "native_core_modified": False, "attempts": 1}
    start = time.perf_counter()
    try:
        if item["method"] == "skillflow":
            result["artifact_root"] = attempt.relative_to(run).as_posix()
            result["native"] = native._native_pipeline(source, attempt, client, renderer=renderer)
            result["status"] = result["native"]["status"]
        else:
            prompt = (render_review(run, item["case_id"], item["method"], original) if original is not None
                      else render_direct(run, item["case_id"], item["method"]))
            answer = client.complete(prompt)
            (directory / "answer.txt").write_bytes(answer.encode("utf-8"))
            result.update(status="complete", answer_sha256=cli.digest(answer))
    except KeyboardInterrupt as error:
        result.update(status="failed", reason=f"Interrupted without automatic resume: {error}")
    except Exception as error:
        result.update(status="failed", reason=f"{type(error).__name__}: {error}")
    try:
        verify_formal_gate(run, generation=False)
        result.update(seal_candidate(run, workflow_id, artifact_root=result.get("artifact_root")))
    except Exception as error:
        result.update(status="failed", candidate_seal_error=f"{type(error).__name__}: {error}")
    finished, elapsed = utc_now(), time.perf_counter() - start
    result.update(finished_at=finished, usage=usage_summary(run, workflow_id), timing={
        "attempt_elapsed_seconds": elapsed, "mailbox_wait_seconds": client.wait_seconds,
        "workflow_elapsed_seconds": max(0., native._seconds(finished) - native._seconds(read(directory / "state.json")["started_at"])),
        "local_processing_seconds": max(0., elapsed - client.wait_seconds)})
    write_json(attempt / "worker-result.json", result, immutable=True)
    write_json(directory / "result.json", result, immutable=True)
    return result


def replay_formal(run_dir, *, include_native=True):
    """Recheck saved formal evidence, without a dispatcher or network client."""
    run, errors, requests, candidates = Path(run_dir).resolve(), [], [], []
    sessions, response_ids = set(), set()
    try:
        verify_formal_gate(run, generation=False)
    except (OSError, ValueError, KeyError, native.ExecutionStop) as error:
        return {"schema_version": SCHEMA, "status": "failed", "errors": [str(error)], "model_calls": 0,
                "actual_cli_processes_started_by_replay": 0}
    for directory, request in native._requests(run):
        status = "queued"
        try:
            registration = _registration(run, request["workflow_id"])
            core = inside(directory, "core-prompt.txt").read_bytes().decode("utf-8")
            if (request.get("core_sha256") != cli.digest(core)
                    or request.get("delivery_sha256") != sha256(inside(directory, "prompt.txt"))
                    or inside(directory, "prompt.txt").read_bytes() != native.ENVELOPE.replace("{core}", core).encode("utf-8")
                    or request.get("runtime") != cli.EXPECTED or request.get("transport") != cli.TRANSPORT):
                raise native.ExecutionStop("Exact queued source/prompt/runtime material changed")
            _verify_prompt(run, registration, core)
            if (directory / "response.json").exists() and read(directory / "response.json").get("accepted") is True:
                receipt = _replay_request(directory)
                identities = set(receipt["usage"]["by_response_id"])
                if receipt["cli_session_id"] in sessions or response_ids & identities:
                    raise native.ExecutionStop("Formal replay found a reused CLI session or response identity")
                sessions.add(receipt["cli_session_id"])
                response_ids.update(identities)
                status = "matched"
            elif (directory / "response.json").exists() or (directory / "stop.json").exists():
                status = "retained_failure"
            elif (directory / "dispatch.json").exists():
                status = "outstanding"
        except (OSError, ValueError, KeyError, native.ExecutionStop) as error:
            errors.append({"request_id": request["request_id"], "reason": str(error)})
            status = "mismatch"
        requests.append({"request_id": request["request_id"], "status": status})
    schedule = read(run / "schedule.json")
    for item in schedule["main"] + schedule["reviews"]:
        path = native._workflow(run, item["workflow_id"]) / "result.json"
        if not path.exists():
            candidates.append({"workflow_id": item["workflow_id"], "status": "not_started"})
            continue
        try:
            result = read(path)
            if result.get("artifact_manifest_sha256"):
                from .artifacts import verify_candidate
                verify_candidate(run, item["workflow_id"], result)
            if item["method"] == "skillflow" and result.get("native"):
                if not include_native:
                    raise native.ExecutionStop("Full formal replay requires the saved native stage replays")
                from skillflow.graph.feedback.runner import replay_run
                from skillflow.pipeline import replay_analysis
                attempt = run / result["artifact_root"]
                if replay_run(attempt / "graph") != result["native"]["graph"]:
                    raise native.ExecutionStop("Native graph stage decisions differ on replay")
                if result["native"].get("analysis") and replay_analysis(attempt / "analysis") != result["native"]["analysis"]:
                    raise native.ExecutionStop("Native downstream stage decisions differ on replay")
            candidates.append({"workflow_id": item["workflow_id"], "status": "matched"})
        except (OSError, ValueError, KeyError, native.ExecutionStop) as error:
            errors.append({"workflow_id": item["workflow_id"], "reason": str(error)})
    if (run / "output-freeze.json").exists():
        try:
            from .results import verify_output_freeze
            verify_output_freeze(run)
        except (OSError, ValueError, KeyError) as error:
            errors.append({"output_freeze": str(error)})
    incomplete = any(r["status"] in {"queued", "outstanding"} for r in requests) or any(r["status"] == "not_started" for r in candidates)
    return {"schema_version": SCHEMA, "status": "failed" if errors else "incomplete" if incomplete else "verified",
        "request_replays": requests, "candidate_replays": candidates, "errors": errors,
        "model_calls": 0, "actual_cli_processes_started_by_replay": 0,
        "semantic_accuracy": "Requires independent human scoring; replay is an integrity and execution check."}


def close_outputs(run_dir):
    """Close every fixed outcome, retaining failures and stopped unattempted work."""
    from .artifacts import verify_candidate
    from .formal_cli_metrics import process_started
    run = Path(run_dir).resolve()
    verify_formal_gate(run, generation=False)
    _, schedule = _schedule(run)
    if (run / "output-freeze.json").exists():
        from .results import verify_output_freeze
        return verify_output_freeze(run)
    stopped = (run / "dispatch-stop.json").exists()
    for directory, _ in native._requests(run):
        if process_started(directory) and not (directory / "cli/process-result.json").exists():
            raise native.ExecutionStop("An actual process without terminal supervision evidence prevents closure")
        if (directory / "dispatch.json").exists() and not (directory / "cli/process-result.json").exists():
            raise native.ExecutionStop("An attempted dispatch without terminal supervision evidence prevents closure")
        if not any((directory / name).exists() for name in ("response.json", "stop.json")):
            raise native.ExecutionStop("An outstanding or queued request prevents output closure")
    absent = []
    for item in schedule["main"] + schedule["reviews"]:
        directory = native._workflow(run, item["workflow_id"])
        path = directory / "result.json"
        if not path.exists():
            if not stopped or directory.exists():
                raise native.ExecutionStop("An active, incomplete or unattempted workflow prevents closure")
            absent.append((path, item))
            continue
        result = read(path)
        if result.get("status") in {None, "running", "pending", "interrupted"}:
            raise native.ExecutionStop("An active or resumable workflow prevents closure")
        if result.get("artifact_manifest_sha256"):
            verify_candidate(run, item["workflow_id"], result)
    for path, item in absent:
        write_json(path, {"schema_version": SCHEMA, "workflow_id": item["workflow_id"], "status": "failed",
            "reason": "Unattempted after retained global stop; no replacement answer", "attempts": 0,
            "answer_sha256": None, "finished_at": utc_now()}, immutable=True)
    files = {}
    for name in ("workflows", "mailbox"):
        for relative, digest in tree_hashes(run / name).items():
            files[name + "/" + relative] = digest
    freeze = {"schema_version": SCHEMA, "schedule_sha256": sha256(run / "schedule.json"), "files": files,
        "planned_results": 264, "regeneration_after_freeze": False, "all_planned_in_denominator": True,
        "actual_model_calls_during_closure": 0}
    write_json(run / "output-freeze.json", freeze, immutable=True)
    return freeze


def build_cost_ledger(run_dir):
    from .formal_cli_metrics import build_cost_ledger as collect
    return collect(run_dir)


def report(run_dir):
    """Route closed CLI outputs through the unchanged human/statistical contracts."""
    from .results import aggregate_scores, verify_output_freeze
    from .corrigenda import _root, resolve_grading_run
    run = _root(run_dir)
    grading_run = resolve_grading_run(run)
    verify_formal_gate(run, generation=False)
    verify_output_freeze(run)
    replay = replay_formal(run)
    if replay["status"] != "verified":
        raise native.ExecutionStop("Formal reporting requires complete zero-call replay of the closed outputs")
    scores = aggregate_scores(run)
    from .efficiency import efficiency_comparisons
    cost = build_cost_ledger(run)
    efficiency = efficiency_comparisons(read(grading_run / "scores.json"), cost)
    return {"schema_version": SCHEMA, "replay": replay, "scores": scores, "cost": cost, "efficiency": efficiency,
        "target_run": str(run), "grading_run": str(grading_run),
        "authority": "Separate formal CLI protocol and approved source references; calibration is engineering evidence only.",
        "interpretation": "All 264 planned outcomes remain in the denominator. Engineering completion and replay do not establish semantic accuracy or a method advantage.",
        "model_calls": 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("readiness", "prepare", "verify", "worker", "pending", "dispatch-next", "replay", "close", "cost", "report"))
    parser.add_argument("--run-dir")
    parser.add_argument("--cohort-run")
    parser.add_argument("--reference-workspace")
    parser.add_argument("--calibration-run")
    parser.add_argument("--protocol-proposal")
    parser.add_argument("--decision-record")
    parser.add_argument("--executable")
    parser.add_argument("--workflow-id")
    parser.add_argument("--sessions-dir")
    args = parser.parse_args(argv)
    fields = ("cohort_run", "reference_workspace", "calibration_run", "protocol_proposal", "decision_record", "executable")
    if args.command in {"readiness", "prepare"}:
        if not all(getattr(args, k) for k in fields):
            parser.error("readiness/prepare require exact source, reference, calibration, proposal, decision and executable paths")
        values = {k: getattr(args, k) for k in fields}
        if args.command == "readiness":
            result = inspect_readiness(**values)
        else:
            if not args.run_dir:
                parser.error("prepare requires --run-dir")
            result = prepare_formal_run(args.run_dir, **values)
    else:
        if not args.run_dir:
            parser.error("This command requires --run-dir")
        if args.command == "worker":
            if not args.workflow_id:
                parser.error("worker requires --workflow-id")
            result = run_planned_workflow(args.run_dir, args.workflow_id)
        elif args.command == "dispatch-next":
            result = dispatch_next_once(args.run_dir, sessions_dir=args.sessions_dir)
        elif args.command == "pending":
            verify_formal_gate(args.run_dir)
            result = native.pending_requests(args.run_dir)
        elif args.command == "verify":
            verify_formal_gate(args.run_dir, generation=False)
            result = {"status": "verified", "model_calls": 0}
        else:
            result = {"replay": replay_formal, "close": close_outputs, "cost": build_cost_ledger,
                      "report": report}[args.command](args.run_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
