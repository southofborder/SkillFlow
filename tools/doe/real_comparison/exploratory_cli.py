"""Prospective assistant-reference comparison; generation is explicitly authorized.

This separate runner never creates human attestations, changes historical gates,
retries a workflow, or scores a target before the complete output cohort closes.
Only run-workflow and run-batch launch models; preparation and replay are offline.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import json
from pathlib import Path
import shutil
import threading
import time

from . import controlled_cli as cli
from . import cli_adapter_v3 as v3
from . import controlled_calibration as calibration
from . import execution as native
from .artifacts import seal_candidate, verify_candidate
from .assessment import validate_reference_evidence
from .formal_cli import _schedule, inside, tree_hashes
from .inputs import render_direct, render_review
from .metrics import combine_usage
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-real-comparison-exploratory-cli-v1"
AMENDMENT = "skillflow-exploratory-user-amendment-v1"
USER_QUOTATION = "允许先做探索性对照，尽快产出真实结果"
ROOT = Path(__file__).resolve().parents[3]
LIMITS = dict(calibration.LIMITS)
CODE = ("exploratory_cli", "controlled_cli", "cli_adapter_v3", "controlled_calibration",
        "current_harness_calibration", "cli_amendment_v3", "execution", "artifacts",
        "assessment", "formal_cli", "inputs", "metrics", "protocol", "semantic_metrics", "selection")
_IMPORT_LOCK = threading.Lock()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_files(root, files):
    for relative, digest in files.items():
        if sha256(inside(root, relative)) != digest:
            raise native.ExecutionStop("Frozen exploratory material changed: " + relative)


def _copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _amendment(value):
    if (value.get("schema_version") != AMENDMENT or value.get("user_quotation") != USER_QUOTATION
            or value.get("exploratory") is not True
            or value.get("human_reference_confirmation_required_before_generation") is not False):
        raise native.ExecutionStop("The exact user amendment must expressly permit exploratory assistant-reference generation")
    return value


def prepare(run_dir, *, cohort, manifest, references, amendment, calibration_audit, source_selection):
    """Seal all inputs before generation; no model launch and no fabricated approval."""
    run, cohort, package = map(lambda p: Path(p).resolve(), (run_dir, cohort, references))
    if run.exists():
        raise native.ExecutionStop("Use a fresh exploratory run; previous identities are never replaced")
    manifest = Path(manifest).resolve()
    calibration.verify_manifest(manifest)
    _amendment(read(amendment))
    audit = read(calibration_audit)
    if (audit.get("schema_version") != "skillflow-calibration-engineering-audit-v1"
            or audit.get("engineering_ready_for_exploratory_comparison") is not True):
        raise native.ExecutionStop("A source-independent engineering audit must permit exploratory execution")
    selection, schedule = _schedule(cohort)
    current_root = Path(source_selection).resolve()
    current = read(current_root / "current-selection-validation.json")
    result = read(current_root / "current-selection-result.json")
    adoption = read(current_root / "source-evidence-adoption.json")
    identities = lambda rows: [{k: item.get(k) for k in ("canonical_id", "version", "source_sha256", "source_tree_sha256", "bundle_sha256")} for item in rows]
    expected = identities(selection["selected"] + selection["reserves"])
    if (current.get("state") != "validated_current_selector"
            or expected != current.get("expected_case_identities")
            or expected != identities(result["selected"] + result["reserves"])
            or adoption.get("state") != "adopted_for_new_prospective_source_selection_only"
            or any(item.get("differences") for item in adoption.get("fixed_30_identity_comparisons", []))
            or len(adoption.get("fixed_30_identity_comparisons", [])) != 30):
        raise native.ExecutionStop("The current selector proof must preserve all 24 cases and six reserves exactly")
    from .selection import verify_reference_packets
    packets = verify_reference_packets(current["corpus_root"], cohort / "cases")
    if packets.get("verified") is not True or packets.get("packet_count") != 30:
        raise native.ExecutionStop("All actual source bytes and their complete numbered views must verify before freezing")
    for case in selection["selected"] + selection["reserves"]:
        packet = read(cohort / "cases" / case["case_id"] / "source-manifest.json")
        if (packet.get("source_sha256") != case["source_sha256"]
                or packet.get("source_tree_sha256") != case["source_tree_sha256"]
                or packet.get("source_bundle_sha256") != case["bundle_sha256"]):
            raise native.ExecutionStop("A source packet differs from its exact fixed source identity")
    verify_files(ROOT, current["implementation_files"])
    for path, digest in current["input_files"].items():
        if sha256(path) != digest:
            raise native.ExecutionStop("A source eligibility proof input changed: " + path)
    refseal = read(package / "freeze.json")
    if refseal.get("evidence_level") != "assistant_exploratory_not_human_gold":
        raise native.ExecutionStop("The reference package must disclose assistant exploratory evidence")
    verify_files(package, refseal["files"])
    entries = {r["case_id"]: r for r in refseal["references"]}
    selected = {c["case_id"]: c for c in selection["selected"]}
    if set(entries) != set(selected):
        raise native.ExecutionStop("Exactly the 24 fixed source-only assistant references must be sealed")
    for case_id, item in entries.items():
        path = inside(package, item["path"])
        reference = validate_reference_evidence(cohort, read(path))
        case = selected[case_id]
        if (sha256(path) != item["reference_sha256"] or reference.get("human_verified") is not False
                or reference.get("case_id") != case_id or reference.get("source_sha256") != case["source_sha256"]
                or item.get("source_tree_sha256") != case.get("source_tree_sha256")
                or item.get("source_bundle_sha256") != case.get("bundle_sha256")
                or any(reference.get(k) not in (None, item.get(k)) for k in ("source_tree_sha256", "source_bundle_sha256"))):
            raise native.ExecutionStop("An exploratory ledger identity changed or claims human confirmation")
    run.mkdir(parents=True)
    for folder in ("cases", "prompts", "prepared-prompts"):
        shutil.copytree(cohort / folder, run / folder, symlinks=False)
    for name in ("selection.json", "schedule.json", "grading-contract.json", "common-assumptions.md",
                 "common-runtime-contract.json", "rubric.md", "evaluation-rules-supplement-v1.md"):
        _copy(inside(cohort, name), run / name)
    # Verify again after copying, before sealing a byte. This checks the same
    # actual source tree given to native analysis and direct numbered views.
    copied = verify_reference_packets(current["corpus_root"], run / "cases")
    if copied.get("verified") is not True or copied.get("packet_count") != 30:
        raise native.ExecutionStop("Copied complete source packets differ from the fixed cohort")
    shutil.copytree(package, run / "reference-package", symlinks=False)
    for name in ("current-selection-validation.json", "current-selection-result.json", "source-evidence-adoption.json"):
        _copy(current_root / name, run / "source-selection-current" / name)
    for source, name in ((manifest, "current-harness-manifest.json"), (Path(amendment), "user-amendment.json"),
                         (Path(calibration_audit), "calibration-engineering-audit.json")):
        _copy(source, run / name)
    for case_id, item in entries.items():
        _copy(inside(package, item["path"]), run / "references" / (case_id + ".json"))
    # Re-rendering checks source/rules and all 144 prepared direct requests. The
    # reference directory is separate and is never passed to a target client.
    _schedule(run)
    native.snapshot_production_code(run)
    write_json(run / "plan.json", {"schema_version": SCHEMA, "created_at": utc_now(), "runtime": v3.EXPECTED,
        "evidence_level": "assistant_exploratory", "human_reference_confirmations": 0,
        "human_scoring_observed": False, "human_review_work_seconds": None,
        "planned_main_workflows": 216, "planned_reviews": 48, "planned_outputs": 264,
        "limits": LIMITS, "schedule_seed": schedule["seed"], "parallel_workers": 6, "automatic_retry": False,
        "no_original_review_policy": "not_reviewable_no_replacement",
        "scope": "The user waived human-first reference confirmation for this exploratory run only. Human timing and confirmation remain unobserved; semantic/native failure is a planned method outcome.",
        "origin": {"cohort": str(cohort), "reference_package": str(package)},
        "protocol_limit": "Post-hoc no-tool audit and fresh CLI contexts are observational isolation, not a hard tool sandbox. No hidden reasoning is exported."}, immutable=True)
    implementation = {"tools/doe/real_comparison/" + name + ".py": sha256(ROOT / "tools/doe/real_comparison" / (name + ".py")) for name in CODE}
    implementation["tools/doe/direct_baseline.py"] = sha256(ROOT / "tools/doe/direct_baseline.py")
    write_json(run / "freeze.json", {"schema_version": SCHEMA, "files": tree_hashes(run), "implementation": implementation,
        "reference_and_scores_enter_target_inputs": False}, immutable=True)
    verify_run(run)
    return {"status": "sealed_exploratory_ready", "planned_outputs": 264, "target_calls": 0,
            "human_reference_confirmations": 0, "evidence_level": "assistant_exploratory"}


def verify_run(run, *, generation=True):
    run = Path(run).resolve()
    seal = read(run / "freeze.json")
    if seal.get("schema_version") != SCHEMA:
        raise native.ExecutionStop("Unexpected exploratory freeze schema")
    verify_files(run, seal["files"])
    verify_files(ROOT, seal["implementation"])
    native.verify_production_code(run)
    _amendment(read(run / "user-amendment.json"))
    manifest = read(run / "current-harness-manifest.json")
    if (manifest.get("runtime") != v3.EXPECTED or manifest.get("controlled_transport") is not True
            or manifest.get("disabled_features") != list(cli.DISABLED_FEATURES)
            or sha256(manifest["executable"]) != v3.PINNED_EXECUTABLE_SHA256):
        raise native.ExecutionStop("The fixed controlled runtime/executable identity changed")
    if generation and (run / "output-freeze.json").exists():
        raise native.ExecutionStop("All exploratory output generation is permanently closed")
    return manifest


def planned(run, workflow_id=None):
    schedule = read(Path(run) / "schedule.json")
    rows = schedule["main"] + schedule["reviews"]
    if workflow_id is None:
        return rows
    native._name(workflow_id)
    matches = [r for r in rows if r["workflow_id"] == workflow_id]
    if len(matches) != 1:
        raise native.ExecutionStop("The workflow is outside the fixed 264-item schedule")
    return matches[0]


def requests(run, workflow_id=None):
    return sorted((Path(run) / "workflows").glob((workflow_id or "*") + "/requests/q*"))


def usage(run, workflow_id=None):
    parts = []
    for directory in requests(run, workflow_id):
        receipt = read(directory / "receipt.json") if (directory / "receipt.json").exists() else {}
        process = read(directory / "cli/process-result.json") if (directory / "cli/process-result.json").exists() else {}
        started = read(directory / "cli/process-start.json") if (directory / "cli/process-start.json").exists() else {}
        prelaunch = process.get("actual_cli_process_started") is False and process.get("status") in {"prelaunch_error", "launch_failed"}
        if started.get("actual_cli_process_started") is True or ((directory / "dispatch.json").exists() and not prelaunch):
            parts.append({**receipt.get("usage", {}), "missing_requests": [] if receipt.get("usage_verified") is True else [directory.as_posix()]})
    result = combine_usage(parts)
    if not parts:
        result["totals"] = {key: 0 for key in v3.TOKEN_FIELDS}
    return result


def _stop(run, reason):
    try:
        with (Path(run) / "dispatch-stop.json").open("x", encoding="utf-8") as stream:
            json.dump({"schema_version": SCHEMA, "stopped_at": utc_now(), "reason": str(reason), "automatic_retry": False}, stream, indent=2)
            stream.write("\n")
    except FileExistsError:
        pass


def _is_protocol_failure(receipt, process=None):
    # Fail closed on every actual invariant violation. A precisely identified
    # missing cost or timeout-induced missing final is a workflow failure; it
    # does not prove another workflow used a different model or tools.
    local = {"Unknown or inconsistent per-response usage forbids further dispatch"}
    if process and process.get("status") != "process_exited":
        local.update({"The fresh CLI session must contain exactly one started and completed turn",
            "The visible final answer lacks exactly one attributed completion event",
            "The visible final answer lacks one exact receipt item identity",
            "CLI stdout does not contain exactly the receipt's complete visible final answer"})
    if receipt.get("tools") or any("Conflicting usage" in d for d in receipt.get("diagnostics", [])):
        return True
    return any(reason not in local for reason in receipt.get("violations", []))


class ExploratoryClient:
    def __init__(self, run, item, *, process_factory=None, sessions_dir=None, token_counter=None):
        self.run, self.item = Path(run), item
        self.workflow_id = item["workflow_id"]
        self.process_factory, self.sessions_dir = process_factory, sessions_dir
        self.token_counter = token_counter or native.reference_tokens
        self.wait_seconds = 0.

    def complete(self, core):
        from tools.doe.direct_baseline import DEFAULT_SESSIONS, find_receipt
        try:
            manifest = verify_run(self.run)
        except Exception as error:
            _stop(self.run, "Frozen input/configuration failure: " + str(error))
            raise
        if (self.run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("A retained global protocol/configuration failure forbids dispatch")
        directory = self.run / "workflows" / self.workflow_id
        elapsed = time.time() - native._seconds(read(directory / "state.json")["started_at"])
        prior, totals = requests(self.run, self.workflow_id), usage(self.run, self.workflow_id)
        if elapsed >= LIMITS["workflow_seconds"] or len(prior) >= LIMITS["actual_cli_requests"]:
            raise native.ExecutionStop("The six-hour or 64-request workflow budget is exhausted")
        if totals["conflicting_response_ids"]:
            _stop(self.run, "Conflicting per-response usage identities")
            raise native.ExecutionStop("Conflicting response identities forbid all further dispatch")
        if prior and (totals["missing_requests"] or any(v is None for v in totals["totals"].values())):
            raise native.ExecutionStop("Unknown per-response usage forbids this workflow's next request")
        if prior and totals["totals"]["total_tokens"] >= LIMITS["reported_total_tokens"]:
            raise native.ExecutionStop("The reported eight-million-token workflow budget is exhausted")
        if self.item["method"] != "skillflow":
            expected = (render_review(self.run, self.item["case_id"], self.item["method"], original_answer(self.run, self.item))
                        if self.item["kind"] == "review" else render_direct(self.run, self.item["case_id"], self.item["method"]))
            if core != expected:
                _stop(self.run, "A direct/review target input differs from frozen source and rules")
                raise native.ExecutionStop("Direct/review input mismatch")
        delivery = native.ENVELOPE.replace("{core}", core)
        tokens = self.token_counter(delivery)
        if tokens > LIMITS["delivered_reference_tokens"]:
            raise native.ExecutionStop("Complete delivery exceeds 300,000 reference tokens; material is never clipped")
        request = directory / "requests" / f"q{len(prior) + 1:03d}"
        request.mkdir(parents=True, exist_ok=False)
        (request / "core-prompt.txt").write_bytes(core.encode("utf-8"))
        (request / "prompt.txt").write_bytes(delivery.encode("utf-8"))
        write_json(request / "request.json", {"schema_version": SCHEMA, "workflow_id": self.workflow_id,
            "created_at": utc_now(), "core_sha256": v3.digest(core), "delivery_sha256": v3.digest(delivery),
            "reference_tokens": tokens, "reference_tokens_are_actual_usage": False,
            "references_or_scores_supplied": False}, immutable=True)
        cwd = self.run / "empty-cwd" / self.workflow_id / request.name
        cwd.mkdir(parents=True, exist_ok=False)
        prepared = cli.prepare_launch(manifest["executable"], request / "prompt.txt", request / "cli", cwd,
            base_instructions_sha256=manifest["base_instructions_sha256"], developer_segment_sha256=manifest["developer_segment_sha256"])
        if (self.run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("A concurrent protocol failure stopped this request before dispatch")
        write_json(request / "dispatch.json", {"attempted_at": utc_now(), "command": prepared["command"],
            "workflow_id": self.workflow_id, "scope": SCHEMA, "retries": 0}, immutable=True)
        start = time.perf_counter()
        try:
            process = cli.execute_launch(prepared, timeout_seconds=min(LIMITS["outstanding_request_seconds"], LIMITS["workflow_seconds"] - elapsed), popen=self.process_factory)
            session = v3.session_from_stdout(request / "cli/stdout.jsonl")
            raw = find_receipt(session, self.sessions_dir or DEFAULT_SESSIONS)
            answer, receipt = cli.inspect_receipt(raw, session, prepared,
                stdout_path=request / "cli/stdout.jsonl",
                last_message_path=request / "cli/last-message.txt" if (request / "cli/last-message.txt").exists() else None)
            receipt.update(assessment_scope=SCHEMA, raw_receipt_path=str(raw.resolve()), raw_receipt_sha256=sha256(raw),
                process_result_sha256=sha256(request / "cli/process-result.json"), stdout_sha256=sha256(request / "cli/stdout.jsonl"))
            # Serial import prevents simultaneous workers accepting the same
            # response identity. Responses remain deduplicated for costs.
            with _IMPORT_LOCK:
                for other in requests(self.run):
                    if (other / "receipt.json").exists():
                        saved = read(other / "receipt.json")
                        if session == saved.get("cli_session_id") or set(receipt["usage"]["by_response_id"]) & set(saved.get("usage", {}).get("by_response_id", {})):
                            receipt["violations"].append("A CLI session or response identity was reused")
                accepted = (not receipt["violations"] and receipt.get("protocol_status") == "conformant"
                    and all(receipt.get(k) is True for k in ("configuration_verified", "provider_verified", "usage_verified", "completed"))
                    and answer is not None and process.get("status") == "process_exited" and process.get("returncode") == 0)
                write_json(request / "receipt.json", receipt, immutable=True)
                write_json(request / "response.json", {"accepted": accepted, "answer_sha256": v3.digest(answer) if answer is not None else None,
                    "imported_at": utc_now(), "process_status": process.get("status")}, immutable=True)
            if answer is not None:
                (request / "answer.txt").write_bytes(answer.encode("utf-8"))
            if not accepted:
                if _is_protocol_failure(receipt, process):
                    _stop(self.run, "Actual target protocol/configuration mismatch: " + "; ".join(receipt["violations"]))
                raise native.ExecutionStop("Target receipt was not accepted: " + "; ".join(receipt["violations"]))
            return answer
        except Exception as error:
            # The launch evidence is retained even when parsing fails. No
            # unknown cost is filled from cumulative usage or character count.
            write_json(request / "failure.json", {"failed_at": utc_now(), "reason": f"{type(error).__name__}: {error}",
                "automatic_retry": False, "unknown_usage_blocks_workflow": True}, immutable=True)
            if not (request / "receipt.json").exists():
                # Parsing/attribution failure cannot prove a matched runtime
                # and exact input. Preserve evidence and stop globally rather
                # than treating an unverified transport as a native failure.
                _stop(self.run, "Actual target receipt could not be verified: " + str(error))
            raise
        finally:
            self.wait_seconds += time.perf_counter() - start


def original_answer(run, item):
    if item["kind"] != "review" or item["method"] not in {"audit", "chain"} or item["repeat"] != 1:
        raise native.ExecutionStop("Only the fixed first direct answer may be independently reviewed")
    original = planned(run, item["original_workflow_id"])
    if any(original[k] != item[k] for k in ("case_id", "method", "repeat", "source_sha256")):
        raise native.ExecutionStop("The first-answer binding differs from the fixed schedule")
    directory = Path(run) / "workflows" / original["workflow_id"]
    if not (directory / "result.json").exists():
        raise native.ExecutionStop("The fixed original workflow must close before its review")
    result = read(directory / "result.json")
    if result.get("status") != "complete" or not (directory / "answer.txt").exists():
        return None
    if result.get("answer_sha256") != sha256(directory / "answer.txt"):
        raise native.ExecutionStop("The first visible answer changed")
    verify_candidate(run, original["workflow_id"], result)
    return (directory / "answer.txt").read_bytes().decode("utf-8")


def run_workflow(run_dir, workflow_id, *, renderer=None, process_factory=None, sessions_dir=None, token_counter=None):
    """Exactly one planned result, preserving native failure without a resample."""
    run = Path(run_dir).resolve()
    verify_run(run)
    item = planned(run, workflow_id)
    directory = run / "workflows" / workflow_id
    if directory.exists():
        raise native.ExecutionStop("A started workflow cannot be retried, resumed or replaced")
    original = original_answer(run, item) if item["kind"] == "review" else None
    directory.mkdir(parents=True)
    write_json(directory / "registration.json", {**item, "mode": "exploratory", "runtime": v3.EXPECTED,
        "transport": v3.TRANSPORT, "source_path": str((run / "cases" / item["case_id"] / "source").resolve())}, immutable=True)
    write_json(directory / "state.json", {"started_at": utc_now()}, immutable=True)
    if item["kind"] == "review" and original is None:
        result = {"schema_version": SCHEMA, "workflow_id": workflow_id, "status": "not_reviewable", "attempts": 0,
            "reason": "Exact R1 answer unavailable; no replacement repetition", "finished_at": utc_now(), "usage": usage(run, workflow_id)}
        write_json(directory / "result.json", result, immutable=True)
        return result
    if original is not None:
        write_json(directory / "original.json", {"original_workflow_id": item["original_workflow_id"], "answer_sha256": v3.digest(original)}, immutable=True)
    attempt = directory / "attempts/001"
    attempt.mkdir(parents=True)
    client = ExploratoryClient(run, item, process_factory=process_factory, sessions_dir=sessions_dir, token_counter=token_counter)
    result = {"schema_version": SCHEMA, "workflow_id": workflow_id, "status": "failed", "attempts": 1,
        "answer_sha256": None, "graph_reused": False, "native_core_modified": False}
    start = time.perf_counter()
    try:
        if (run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("A global protocol/configuration stop forbids this planned workflow")
        if item["method"] == "skillflow":
            result["artifact_root"] = attempt.relative_to(run).as_posix()
            result["native"] = native._native_pipeline(run / "cases" / item["case_id"] / "source", attempt, client, renderer=renderer)
            result["status"] = result["native"]["status"]
        else:
            core = (render_review(run, item["case_id"], item["method"], original) if original is not None
                    else render_direct(run, item["case_id"], item["method"]))
            answer = client.complete(core)
            (directory / "answer.txt").write_bytes(answer.encode("utf-8"))
            result.update(status="complete", answer_sha256=v3.digest(answer))
    except (Exception, KeyboardInterrupt) as error:
        result.update(status="failed", reason=f"{type(error).__name__}: {error}")
    try:
        verify_run(run, generation=False)
        result.update(seal_candidate(run, workflow_id, artifact_root=result.get("artifact_root")))
    except Exception as error:
        result.update(status="failed", candidate_seal_error=str(error))
        _stop(run, "Frozen material/candidate seal failure: " + str(error))
    elapsed = time.perf_counter() - start
    state = read(directory / "state.json")
    result.update(finished_at=utc_now(), usage=usage(run, workflow_id), timing={
        "workflow_elapsed_seconds": elapsed, "cli_wait_seconds": client.wait_seconds,
        "local_processing_seconds": max(0., elapsed - client.wait_seconds),
        "schedule_wait_seconds": max(0., native._seconds(state["started_at"]) - native._seconds(read(run / "plan.json")["created_at"]))})
    write_json(directory / "result.json", result, immutable=True)
    return result


def run_batch(run_dir, *, workers=6, runner=None):
    """Managed bounded workers; a restart skips closed identities, never replays them."""
    run = Path(run_dir).resolve()
    verify_run(run)
    if workers != read(run / "plan.json").get("parallel_workers"):
        raise ValueError("The six-worker concurrency is fixed before generation for all methods and reviews")
    lock = run / "controller.lock"
    try:
        with lock.open("x", encoding="utf-8") as stream:
            json.dump({"started_at": utc_now(), "workers": workers}, stream)
    except FileExistsError as error:
        raise native.ExecutionStop("A retained controller lock forbids a duplicate controller") from error
    runner = runner or run_workflow
    try:
        # Main order is the presealed case/repeat-balanced randomized order;
        # reviews retain their fixed identities and execute after all mains.
        for kind in ("main", "review"):
            queue = [i for i in planned(run) if i["kind"] == kind]
            active = {}
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="exploratory") as pool:
                while queue or active:
                    while queue and len(active) < workers and not (run / "dispatch-stop.json").exists():
                        item = queue.pop(0)
                        directory = run / "workflows" / item["workflow_id"]
                        if directory.exists():
                            if (directory / "result.json").exists():
                                continue
                            raise native.ExecutionStop("A prior interrupted workflow lacks a closed result; retain it and decide explicitly")
                        active[pool.submit(runner, run, item["workflow_id"])] = item["workflow_id"]
                    if not active:
                        break
                    finished, _ = wait(active, timeout=30, return_when=FIRST_COMPLETED)
                    for future in finished:
                        identity = active.pop(future)
                        try:
                            future.result()
                        except Exception as error:
                            _stop(run, "Managed worker could not retain its result: " + identity + ": " + str(error))
            if (run / "dispatch-stop.json").exists():
                break
        if (run / "dispatch-stop.json").exists():
            terminalize_after_stop(run)
        return summary(run)
    finally:
        # Preserve ownership evidence; a finished controller is not a request
        # to resume an abandoned in-flight process.
        write_json(run / "controller-finished.json", {"finished_at": utc_now(), "target_retries": 0}, immutable=True)


def terminalize_after_stop(run_dir):
    """Close unlaunched identities after all managed workers have terminated.

    No calls, replacement answers, or removal of failed/partial artifacts. The
    full fixed denominator can be scored after a protocol halt.
    """
    run = Path(run_dir).resolve()
    if not (run / "dispatch-stop.json").exists():
        raise native.ExecutionStop("Terminalization requires a retained global stop")
    reason = read(run / "dispatch-stop.json")["reason"]
    for item in planned(run):
        directory = run / "workflows" / item["workflow_id"]
        if (directory / "result.json").exists():
            continue
        directory.mkdir(parents=True, exist_ok=True)
        if not (directory / "registration.json").exists():
            write_json(directory / "registration.json", {**item, "mode": "exploratory", "runtime": v3.EXPECTED,
                "transport": v3.TRANSPORT, "source_path": str((run / "cases" / item["case_id"] / "source").resolve())}, immutable=True)
        missing_original = item["kind"] == "review" and original_answer(run, item) is None
        write_json(directory / "result.json", {"schema_version": SCHEMA, "workflow_id": item["workflow_id"],
            "status": "not_reviewable" if missing_original else "protocol_aborted",
            "reason": "Exact fixed R1 unavailable after global stop" if missing_original else reason,
            "finished_at": utc_now(), "attempts": int(bool(requests(run, item["workflow_id"]))),
            "target_calls_replaced": False, "usage": usage(run, item["workflow_id"])}, immutable=True)
    return summary(run)


def summary(run_dir):
    run = Path(run_dir).resolve()
    outcomes = []
    for item in planned(run):
        path = run / "workflows" / item["workflow_id"] / "result.json"
        result = read(path) if path.exists() else {}
        outcomes.append({**item, "status": result.get("status", "not_generated"), "reason": result.get("reason")})
    return {"schema_version": SCHEMA, "evidence_level": "assistant_exploratory", "planned_denominator": 264,
        "planned_main_denominator": 216, "planned_review_denominator": 48,
        "closed_results": sum(i["status"] != "not_generated" for i in outcomes),
        "outcomes": outcomes, "usage": usage(run), "global_stop": (run / "dispatch-stop.json").exists(),
        "human_reference_confirmations": 0, "human_review_work_seconds": None,
        "semantics_scored": False, "money": None}


def replay(run_dir, *, include_native=True):
    """Recheck every saved visible answer/receipt and native result; zero launches."""
    run = Path(run_dir).resolve()
    manifest = verify_run(run, generation=False)
    errors, sessions, response_ids = [], set(), set()
    for directory in requests(run):
        try:
            req = read(directory / "request.json")
            core = (directory / "core-prompt.txt").read_bytes().decode("utf-8")
            if (sha256(directory / "core-prompt.txt") != req["core_sha256"]
                    or (directory / "prompt.txt").read_bytes() != native.ENVELOPE.replace("{core}", core).encode("utf-8")
                    or sha256(directory / "prompt.txt") != req["delivery_sha256"]):
                raise native.ExecutionStop("Complete request bytes changed")
            if not (directory / "receipt.json").exists():
                if not (directory / "failure.json").exists():
                    raise native.ExecutionStop("Unfinished request lacks retained failure evidence")
                continue
            saved, launch = read(directory / "receipt.json"), read(directory / "cli/launch.json")
            if (sha256(saved["raw_receipt_path"]) != saved["raw_receipt_sha256"]
                    or launch["command"] != cli.command(manifest["executable"], directory / "cli")
                    or launch["base_instructions_sha256"] != manifest["base_instructions_sha256"]
                    or launch["developer_segment_sha256"] != manifest["developer_segment_sha256"]
                    or launch["stdin_sha256"] != req["delivery_sha256"]
                    or saved["stdout_sha256"] != sha256(directory / "cli/stdout.jsonl")
                    or saved["process_result_sha256"] != sha256(directory / "cli/process-result.json")):
                raise native.ExecutionStop("Frozen launch/receipt evidence changed")
            answer, fresh = cli.inspect_receipt(saved["raw_receipt_path"], saved["cli_session_id"], launch,
                stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
            if any(saved.get(k) != v for k, v in fresh.items()):
                raise native.ExecutionStop("Saved receipt facts differ from raw replay")
            if saved["cli_session_id"] in sessions or response_ids & set(saved["usage"]["by_response_id"]):
                raise native.ExecutionStop("A CLI session or response ID was reused")
            sessions.add(saved["cli_session_id"])
            response_ids.update(saved["usage"]["by_response_id"])
            if answer is not None and ((directory / "answer.txt").read_bytes() != answer.encode("utf-8")
                    or read(directory / "response.json")["answer_sha256"] != v3.digest(answer)):
                raise native.ExecutionStop("The complete visible answer changed")
        except Exception as error:
            errors.append({"request": directory.relative_to(run).as_posix(), "reason": str(error)})
    for item in planned(run):
        directory = run / "workflows" / item["workflow_id"]
        if not (directory / "result.json").exists():
            continue
        result = read(directory / "result.json")
        try:
            if result.get("artifact_manifest_sha256"):
                verify_candidate(run, item["workflow_id"], result)
            if include_native and result.get("native"):
                from skillflow.graph.feedback.runner import replay_run
                from skillflow.pipeline import replay_analysis
                attempt = run / result["artifact_root"]
                if replay_run(attempt / "graph") != result["native"]["graph"]:
                    raise native.ExecutionStop("Native graph result changed on replay")
                if "analysis" in result["native"] and replay_analysis(attempt / "analysis") != result["native"]["analysis"]:
                    raise native.ExecutionStop("Native downstream result changed on replay")
        except Exception as error:
            errors.append({"workflow_id": item["workflow_id"], "reason": str(error)})
    return {"schema_version": SCHEMA, "status": "matched" if not errors else "errors", "model_calls": 0,
            "errors": errors, "usage": usage(run), "semantics_scored": False}


def close_outputs(run_dir):
    run = Path(run_dir).resolve()
    verify_run(run)
    result = summary(run)
    if result["closed_results"] != 264:
        raise native.ExecutionStop("All 264 planned outputs must close before scoring or output sealing")
    replayed = replay(run)
    if replayed["errors"]:
        raise native.ExecutionStop("Saved outputs must replay before closing")
    files = tree_hashes(run / "workflows")
    write_json(run / "output-freeze.json", {"schema_version": SCHEMA, "closed_at": utc_now(),
        "planned_outputs": 264, "files": {"workflows/" + k: v for k, v in files.items()},
        "failed_results_remain_in_denominator": True}, immutable=True)
    write_json(run / "summary.json", result, immutable=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify", "run-workflow", "run-batch", "summary", "replay", "close"))
    parser.add_argument("--run-dir", required=True)
    for name in ("cohort", "manifest", "references", "amendment", "calibration-audit", "source-selection", "workflow-id"):
        parser.add_argument("--" + name)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        names = ("cohort", "manifest", "references", "amendment", "calibration_audit", "source_selection")
        if any(getattr(args, name) is None for name in names):
            parser.error("prepare requires cohort, manifest, references, amendment, calibration-audit and source-selection")
        result = prepare(args.run_dir, **{name: getattr(args, name) for name in names})
    elif args.command == "run-workflow":
        if not args.workflow_id:
            parser.error("run-workflow requires --workflow-id")
        result = run_workflow(args.run_dir, args.workflow_id)
    elif args.command == "run-batch":
        result = run_batch(args.run_dir, workers=args.workers)
    elif args.command == "summary":
        result = summary(args.run_dir)
    elif args.command == "replay":
        result = replay(args.run_dir)
    elif args.command == "close":
        result = close_outputs(args.run_dir)
    else:
        verify_run(args.run_dir)
        result = {"status": "verified", "model_calls": 0}
    # Raw final answers are saved to files, never hidden reasoning or a full
    # native object in the controller's routine stdout.
    if args.command == "run-workflow":
        result = {k: v for k, v in result.items() if k != "native"}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
