"""Fresh native calibration under a probed, frozen controlled CLI harness.

This is a separate calibration-only phase, not an amendment to immutable CLI-v3
records or a formal/human-reference gate. Only run_calibrations executes targets.
The manifest records an assistant technical adoption under the user's execution
instruction; it never claims individual hash approval or reuses a prior answer.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil
import time

from . import controlled_cli as cli
from . import cli_adapter_v3 as v3
from . import current_harness_calibration as common
from .current_harness_calibration import read, requests, usage, counts, _stop
from . import cli_amendment_v3 as previous
from . import execution as native
from .artifacts import seal_candidate, verify_candidate
from .metrics import combine_usage
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-controlled-native-calibration-v1"
MANIFEST = "skillflow-current-common-harness-manifest-v1"
ROOT = Path(__file__).resolve().parents[3]
LIMITS = dict(previous.LIMITS)
CODE = ("controlled_calibration.py", "controlled_cli.py", "current_harness_calibration.py", "cli_adapter_v3.py", "cli_amendment_v3.py", "execution.py", "metrics.py", "artifacts.py", "protocol.py")




def verify_manifest(path):
    manifest = common.verify_manifest(path)
    if manifest.get("controlled_transport") is not True or manifest.get("disabled_features") != list(cli.DISABLED_FEATURES):
        raise native.ExecutionStop("The controlled transport and exact three disabled features are required")
    decision = manifest["controlled_harness_decision"]
    if sha256(decision["path"]) != decision["sha256"]:
        raise native.ExecutionStop("The prospective controlled-harness technical decision changed")
    probe = manifest["engineering_probe"]
    for key in ("result", "raw_receipt"):
        if sha256(probe[key + "_path"]) != probe[key + "_sha256"]:
            raise native.ExecutionStop("The completed engineering probe binding changed")
    result, root = read(probe["result_path"]), Path(probe["result_path"]).parent
    launch, process = read(root / "cli/launch.json"), read(root / "cli/process-result.json")
    plan = read(root / "probe-plan.json")
    if (probe.get("semantic_acceptance") is not False or result.get("semantic_acceptance") is not False
            or result.get("engineering_checks_passed") is not True or result.get("process_status") != "process_exited"
            or result.get("cli_session_id") != probe["session_id"] or process.get("returncode") != 0
            or process.get("status") != "process_exited" or process.get("actual_cli_process_started") is not True
            or read(root / "cli/process-start.json").get("actual_cli_process_started") is not True
            or process.get("launch_sha256") != sha256(root / "cli/launch.json")
            or launch["command"] != cli.command(manifest["executable"], root / "cli")
            or {k: v for k, v in launch.items() if k != "started_at"} != plan["prepared"]):
        raise native.ExecutionStop("A complete separate controlled engineering probe is required")
    for filename, digest in plan["implementation"].items():
        if sha256(filename) != digest:
            raise native.ExecutionStop("The controlled probe implementation changed")
    fresh = cli.discover_harness(probe["raw_receipt_path"], probe["session_id"], plan["prepared"],
        stdout_path=root / "cli/stdout.jsonl", last_message_path=root / "cli/last-message.txt")
    if any(result.get(k) != value for k, value in fresh.items()) or any(manifest[key] != fresh[key] for key in (
            "base_instructions_sha256", "developer_segment_sha256", "disabled_features")):
        raise native.ExecutionStop("The prospective manifest differs from the verified engineering probe")
    return manifest


def prepare(run_dir, manifest_path):
    run, manifest_path = Path(run_dir).resolve(), Path(manifest_path).resolve()
    manifest = verify_manifest(manifest_path)
    if run.exists() or run.is_relative_to(manifest_path.parent):
        raise native.ExecutionStop("Use a fresh separate short calibration directory")
    run.mkdir(parents=True)
    shutil.copyfile(manifest_path, run / "current-harness-manifest.json")
    cases = []
    from skillflow.common.inputs.snapshot import inspect_input
    for name in native.CALIBRATION:
        source = previous.CALIBRATION_SOURCE_ROOT / name
        native._calibration_source(source)
        shutil.copytree(source, run / "inputs" / name)
        cases.append({"case_id": name, "source_path": "inputs/" + name,
            "source_sha256": inspect_input(run / "inputs" / name)[2]["source_sha256"]})
    write_json(run / "plan.json", {"schema_version": SCHEMA, "calibration_only": True,
        "formal_dispatch_permitted": False, "created_at": utc_now(), "cases": cases,
        "runtime": manifest["runtime"], "limits": LIMITS, "automatic_retry": False,
        "authority": "Current common-harness technical adoption; not the immutable CLI-v3 protocol or a human-reference gate."}, immutable=True)
    native.snapshot_production_code(run)
    files = {p.relative_to(run).as_posix(): sha256(p) for p in sorted(run.rglob("*")) if p.is_file()}
    implementation = {"tools/doe/real_comparison/" + name: sha256(Path(__file__).parent / name) for name in CODE}
    implementation["tools/doe/direct_baseline.py"] = sha256(ROOT / "tools/doe/direct_baseline.py")
    write_json(run / "freeze.json", {"schema_version": SCHEMA, "files": files, "implementation": implementation}, immutable=True)
    verify_run(run)
    return {"status": "prepared_controlled_calibration_only", "cases": 3, "actual_cli_requests": 0, "formal_requests": 0}


def verify_run(run):
    run = Path(run).resolve()
    for root, values in ((run, read(run / "freeze.json")["files"]), (ROOT, read(run / "freeze.json")["implementation"])):
        for relative, digest in values.items():
            path = root / relative
            if path.is_symlink() or not path.resolve().is_relative_to(root) or sha256(path) != digest:
                raise native.ExecutionStop("Frozen calibration source, code or manifest changed: " + relative)
    native.verify_production_code(run)
    return verify_manifest(run / "current-harness-manifest.json")










class CurrentHarnessClient:
    def __init__(self, run, case_id, *, process_factory=None, sessions_dir=None):
        self.run, self.case_id = Path(run), case_id
        self.process_factory, self.sessions_dir, self.wait_seconds = process_factory, sessions_dir, 0.

    def complete(self, core):
        from tools.doe.direct_baseline import DEFAULT_SESSIONS, find_receipt
        manifest = verify_run(self.run)
        if (self.run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("A retained failure stopped every subsequent calibration call")
        elapsed = time.time() - native._seconds(read(self.run / "workflows" / self.case_id / "state.json")["started_at"])
        prior = requests(self.run, self.case_id)
        totals = usage(self.run, self.case_id)["totals"]
        if elapsed >= LIMITS["workflow_seconds"] or len(prior) >= LIMITS["actual_cli_requests"]:
            raise native.ExecutionStop("The six-hour or 64-request workflow budget is exhausted")
        if prior and (any(v is None for v in totals.values()) or totals["total_tokens"] >= LIMITS["reported_total_tokens"]):
            raise native.ExecutionStop("Unknown usage or the eight-million-token workflow budget forbids a next request")
        delivery = native.ENVELOPE.replace("{core}", core)
        tokens = native.reference_tokens(delivery)
        if tokens > LIMITS["delivered_reference_tokens"]:
            raise native.ExecutionStop("Complete delivery exceeds 300,000 reference tokens; no clipping is permitted")
        directory = self.run / "workflows" / self.case_id / "requests" / f"q{len(prior) + 1:03d}"
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "core-prompt.txt").write_bytes(core.encode("utf-8"))
        (directory / "prompt.txt").write_bytes(delivery.encode("utf-8"))
        write_json(directory / "request.json", {"schema_version": SCHEMA, "created_at": utc_now(), "reference_tokens": tokens,
            "core_sha256": v3.digest(core), "delivery_sha256": v3.digest(delivery), "manifest_sha256": sha256(self.run / "current-harness-manifest.json")}, immutable=True)
        cwd = self.run / "empty-cwd" / self.case_id / directory.name
        cwd.mkdir(parents=True, exist_ok=False)
        prepared = cli.prepare_launch(manifest["executable"], directory / "prompt.txt", directory / "cli", cwd,
            base_instructions_sha256=manifest["base_instructions_sha256"],
            developer_segment_sha256=manifest["developer_segment_sha256"])
        # Explicit prospective per-request expectations; old global pins and
        # rejected records remain unchanged and are never monkeypatched.
        prepared["base_instructions_sha256"] = manifest["base_instructions_sha256"]
        prepared["developer_segment_sha256"] = deepcopy(manifest["developer_segment_sha256"])
        verify_run(self.run)
        if (self.run / "dispatch-stop.json").exists():
            raise native.ExecutionStop("A shared failure stopped this request before dispatch")
        write_json(directory / "dispatch.json", {"attempted_at": utc_now(), "command": prepared["command"],
            "scope": SCHEMA, "manifest_sha256": sha256(self.run / "current-harness-manifest.json")}, immutable=True)
        start = time.perf_counter()
        try:
            process = cli.execute_launch(prepared, timeout_seconds=min(LIMITS["outstanding_request_seconds"], LIMITS["workflow_seconds"] - elapsed), popen=self.process_factory)
            session = v3.session_from_stdout(directory / "cli/stdout.jsonl")
            raw = find_receipt(session, self.sessions_dir or DEFAULT_SESSIONS)
            answer, receipt = cli.inspect_receipt(raw, session, prepared, stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
            receipt.update(assessment_scope=SCHEMA, raw_receipt_path=str(raw.resolve()), raw_receipt_sha256=sha256(raw),
                process_result_sha256=sha256(directory / "cli/process-result.json"), stdout_sha256=sha256(directory / "cli/stdout.jsonl"))
            for other in requests(self.run):
                if (other / "receipt.json").exists():
                    saved = read(other / "receipt.json")
                    if session == saved.get("cli_session_id") or set(receipt["usage"]["by_response_id"]) & set(saved.get("usage", {}).get("by_response_id", {})):
                        receipt["violations"].append("A CLI session or response identity was reused")
            if process.get("status") != "process_exited" or process.get("returncode") != 0:
                receipt["violations"].append("The actual CLI process failed or timed out")
            accepted = (not receipt["violations"] and receipt.get("protocol_status") == "conformant"
                and receipt.get("configuration_verified") is True and receipt.get("provider_verified") is True
                and receipt.get("usage_verified") is True and receipt.get("completed") is True and answer is not None)
            write_json(directory / "receipt.json", receipt, immutable=True)
            write_json(directory / "response.json", {"accepted": accepted, "answer_sha256": v3.digest(answer) if answer is not None else None,
                "imported_at": utc_now()}, immutable=True)
            if answer is not None:
                (directory / "answer.txt").write_bytes(answer.encode("utf-8"))
            if not accepted:
                raise native.ExecutionStop("Current-manifest receipt failed: " + "; ".join(receipt["violations"]))
            # Preserve this accepted response even when it crosses a budget;
            # the next complete() applies the reported-token/time limit.
            return answer
        except BaseException as error:
            _stop(self.run, f"{type(error).__name__}: {error}")
            raise
        finally:
            self.wait_seconds += time.perf_counter() - start


def replay(run):
    run = Path(run).resolve()
    manifest = verify_run(run)
    errors, seen_sessions, seen_responses = [], set(), set()
    for directory in requests(run):
        try:
            request, launch = read(directory / "request.json"), read(directory / "cli/launch.json")
            core = (directory / "core-prompt.txt").read_bytes().decode("utf-8")
            if (sha256(directory / "core-prompt.txt") != request["core_sha256"]
                    or (directory / "prompt.txt").read_bytes() != native.ENVELOPE.replace("{core}", core).encode("utf-8")
                    or sha256(directory / "prompt.txt") != request["delivery_sha256"]
                    or launch["command"] != cli.command(manifest["executable"], directory / "cli")
                    or read(directory / "dispatch.json")["command"] != launch["command"]
                    or launch["stdin_sha256"] != request["delivery_sha256"]
                    or read(directory / "cli/process-result.json").get("launch_sha256") != sha256(directory / "cli/launch.json")
                    or read(directory / "cli/process-start.json").get("actual_cli_process_started") is not True
                    or launch["base_instructions_sha256"] != manifest["base_instructions_sha256"]
                    or launch["developer_segment_sha256"] != manifest["developer_segment_sha256"]):
                raise native.ExecutionStop("Exact source/core/delivery/manifest binding changed")
            saved = read(directory / "receipt.json")
            if sha256(saved["raw_receipt_path"]) != saved["raw_receipt_sha256"]:
                raise native.ExecutionStop("The saved raw receipt changed")
            answer, fresh = cli.inspect_receipt(saved["raw_receipt_path"], saved["cli_session_id"], launch,
                stdout_path=directory / "cli/stdout.jsonl", last_message_path=directory / "cli/last-message.txt")
            if any(saved.get(k) != v for k, v in fresh.items()) or read(directory / "response.json")["accepted"] is not True:
                raise native.ExecutionStop("Receipt facts or accepted status differ on replay")
            if saved["cli_session_id"] in seen_sessions or seen_responses & set(saved["usage"]["by_response_id"]):
                raise native.ExecutionStop("A session or response identity was reused")
            seen_sessions.add(saved["cli_session_id"])
            seen_responses.update(saved["usage"]["by_response_id"])
            if (directory / "answer.txt").read_bytes() != answer.encode("utf-8") or v3.digest(answer) != read(directory / "response.json")["answer_sha256"]:
                raise native.ExecutionStop("The complete visible answer changed")
            if saved["process_result_sha256"] != sha256(directory / "cli/process-result.json") or saved["stdout_sha256"] != sha256(directory / "cli/stdout.jsonl"):
                raise native.ExecutionStop("Process or stdout evidence changed")
        except Exception as error:
            errors.append({"request": directory.relative_to(run).as_posix(), "reason": str(error)})
    for case in native.CALIBRATION:
        path = run / "workflows" / case / "result.json"
        if not path.exists():
            errors.append({"case_id": case, "reason": "Native calibration is not finished"})
            continue
        result = read(path)
        try:
            verify_candidate(run, case, result)
            from skillflow.graph.feedback.runner import replay_run
            from skillflow.pipeline import replay_analysis
            attempt = run / result["artifact_root"]
            if replay_run(attempt / "graph") != result["native"]["graph"] or replay_analysis(attempt / "analysis") != result["native"]["analysis"]:
                raise native.ExecutionStop("Native saved decisions differ on replay")
        except Exception as error:
            errors.append({"case_id": case, "reason": str(error)})
    return {"schema_version": SCHEMA, "status": "passed_engineering_only" if not errors else "failed_or_incomplete",
        "errors": errors, "usage": usage(run), "model_calls": 0, "semantic_accuracy": "not_evaluated"}


def run_case(run_dir, case_id, *, process_factory=None, sessions_dir=None, renderer=None):
    run = Path(run_dir).resolve()
    verify_run(run)
    if case_id not in native.CALIBRATION or (run / "workflows" / case_id).exists() or (run / "dispatch-stop.json").exists():
        raise native.ExecutionStop("Only one fresh planned case is permitted; stopped phases cannot dispatch")
    for item in [i for i in read(run / "plan.json")["cases"] if i["case_id"] == case_id]:
        case, directory = item["case_id"], run / "workflows" / item["case_id"]
        write_json(directory / "state.json", {"started_at": utc_now()}, immutable=True)
        attempt = directory / "attempts/001"
        attempt.mkdir(parents=True)
        client = CurrentHarnessClient(run, case, process_factory=process_factory, sessions_dir=sessions_dir)
        result = {"schema_version": SCHEMA, "workflow_id": case, "status": "failed", "calibration_only": True,
            "formal_requests": 0, "artifact_root": attempt.relative_to(run).as_posix(), "graph_reused": False, "native_core_modified": False}
        start = time.perf_counter()
        try:
            result["native"] = native._native_pipeline(run / item["source_path"], attempt, client, renderer=renderer)
            result["status"] = result["native"]["status"]
            if result["status"] not in {"complete", "diagnostic"} or result["native"].get("analysis", {}).get("stage") != "finished":
                raise native.ExecutionStop("The full native calibration did not finish")
            verify_run(run)
        except BaseException as error:
            result.update(status="failed", reason=f"{type(error).__name__}: {error}")
            _stop(run, result["reason"])
        try:
            result.update(seal_candidate(run, case, artifact_root=result["artifact_root"]))
        except Exception as error:
            result.update(status="failed", candidate_seal_error=str(error))
            _stop(run, result["candidate_seal_error"])
        elapsed = time.perf_counter() - start
        result.update(finished_at=utc_now(), usage=usage(run, case), counts=counts(run, case), timing={"elapsed_seconds": elapsed,
            "cli_wait_seconds": client.wait_seconds, "local_processing_seconds": max(0., elapsed - client.wait_seconds)})
        write_json(directory / "result.json", result, immutable=True)
        return result


def finalize(run_dir):
    run = Path(run_dir).resolve()
    verify_run(run)
    if any(not (p / "result.json").exists() for p in (run / "workflows").glob("*")):
        raise native.ExecutionStop("Wait for every started case worker before finalizing")
    outcomes = [{"case_id": name, "status": read(run / "workflows" / name / "result.json")["status"]
                 if (run / "workflows" / name / "result.json").exists() else "unattempted_after_stop"} for name in native.CALIBRATION]
    if not (run / "dispatch-stop.json").exists() and any(o["status"] == "unattempted_after_stop" for o in outcomes):
        raise native.ExecutionStop("All three planned cases must finish before successful finalization")
    replay_result = replay(run)
    write_json(run / "replay.json", replay_result, immutable=True)
    summary = {"schema_version": SCHEMA, "status": replay_result["status"], "cases": outcomes,
        "usage": usage(run), "counts": counts(run), "calibration_only": True, "formal_requests": 0, "semantic_accuracy": "not_evaluated"}
    write_json(run / "summary.json", summary, immutable=True)
    return summary


def run_calibrations(run_dir, **kwargs):
    for case in native.CALIBRATION:
        run_case(run_dir, case, **kwargs)
        if (Path(run_dir) / "dispatch-stop.json").exists():
            break
    return finalize(run_dir)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "run-case", "finalize", "verify", "replay"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--case-id", choices=native.CALIBRATION)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        if not args.manifest:
            parser.error("prepare requires --manifest")
        result = prepare(args.run_dir, args.manifest)
    elif args.command == "run":
        result = run_calibrations(args.run_dir)
    elif args.command == "run-case":
        if not args.case_id:
            parser.error("run-case requires --case-id")
        saved = run_case(args.run_dir, args.case_id)
        result = {k: v for k, v in saved.items() if k != "native"}
    elif args.command == "finalize":
        result = finalize(args.run_dir)
    elif args.command == "replay":
        result = replay(args.run_dir)
    else:
        verify_run(args.run_dir)
        result = {"status": "verified", "model_calls": 0}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
