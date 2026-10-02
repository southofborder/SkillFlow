"""Version 4: contract-bound, independent full-source audits and offline replay."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from threading import Event
from typing import Callable

from skill_ir.experiments.report import ArtifactWriter
from skill_ir.experiments.resumable import _exclusive_run
from skill_ir.ir.cfg import ControlFlowGraph
from skill_ir.semantic_contract import contract_binding
from skill_ir.recording import (
    RecordingClient, SavedResponseClient, SavedCallFailure, validated_trace,
    streaming_factory, now, read_json, sha_file, implementation_provenance,
)
from .fixtures import PACKAGE_ROOT, REPOSITORY_ROOT, canonical_sha256, prepare_cases

EXPERIMENT_ROOT = PACKAGE_ROOT / "experiments/semantic_backtrace"
PINNED_CONFIG = PACKAGE_ROOT / "experiments/semantics_baseline/deepseek-v4-flash.json"
IDENTITY = "skill-ir-controlled-source-audit-v4"
CASE_IDS = tuple(f"c{i:02}" for i in range(1, 6))
SUITES = {"f01-five": CASE_IDS, "semantics-v4-seven": CASE_IDS + ("c06", "c07")}
PAUSED_SELECTION = (
    ("c06", "001", "264ae43c23c7e72398ed95e248cb97046679116173f5adc6e8153bb6ee9291e5", "9cf38f34b39d44728ad7db673af082e992a3e7a86382049ba956aa77699ca0af"),
    ("c07", "010", "d2ca2e12e1887d7b87b99a589884d93164590a3d3e5fab7a96e0142ae83c0d0e", "e87b9aa12f4f57c92ad800ae05d5e30d2cd5579ce4566d51d37e8a49fc716796"),
)


def _prepared_suite(suite):
    if suite not in SUITES:
        raise ValueError("Unknown audit suite: " + suite)
    prepared = prepare_cases()
    for case in prepared["cases"]:
        case["source"] = deepcopy(prepared["source"])
        case["selection"] = {"sample_id": "F01", "index": 13, "repetition": 1}
    selections = []
    if suite == "semantics-v4-seven":
        for case_id, number, graph_sha, source_sha in PAUSED_SELECTION:
            base = PACKAGE_ROOT / "experiments/security_profile/runs/full-pipeline-20260917/cases" / number / "feedback"
            graph_path, source_path = base / "rounds/r000/cfg.json", base / "inputs/source.json"
            for path, digest in ((graph_path, graph_sha), (source_path, source_sha)):
                if sha_file(path) != digest:
                    raise ValueError("Paused-round fixture digest mismatch: " + str(path))
            cfg, source = read_json(graph_path), read_json(source_path)
            ControlFlowGraph.model_validate(deepcopy(cfg)).validate_integrity()
            selection = {"sample_index": number, "revision": 0,
                         "graph_path": graph_path.relative_to(REPOSITORY_ROOT).as_posix(),
                         "graph_file_sha256": graph_sha,
                         "source_path": source_path.relative_to(REPOSITORY_ROOT).as_posix(),
                         "source_file_sha256": source_sha}
            prepared["cases"].append({"case_id": case_id, "cfg": cfg, "source": source,
                                      "graph_sha256": canonical_sha256(cfg), "oracle_key": None,
                                      "selection": selection})
            selections.append(selection)
    prepared["provenance"]["additional_selections"] = selections
    return prepared

def public_config() -> dict:
    config = read_json(PINNED_CONFIG)["variants"][0]
    # Deliberate allowlist: no environment contents or credentials in artifacts.
    config = {name: config[name] for name in (
        "endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
        "retry_base_ms", "retry_max_backoff_ms",
    )}
    if config["endpoint"] != "https://api.deepseek.com/chat/completions" or config["model"] != "deepseek-v4-flash":
        raise ValueError("This first-round experiment requires the pinned official DeepSeek configuration")
    # Historical baseline configuration is immutable; this new suite uses the
    # already adopted, explicitly recorded 600 second timeout.
    config["timeout_ms"] = 600000
    return config


def prepare_run(directory: Path, *, executable: Path | None = None, review30: bool = True,
                suite: str = "f01-five", max_audit_execution_retries: int = 2) -> dict:
    from .controlled import render_controlled
    from skill_ir.audit_execution import AUDIT_RETRY_POLICY
    if type(max_audit_execution_retries) is not int or not 0 <= max_audit_execution_retries <= 5:
        raise ValueError("max_audit_execution_retries must be between 0 and 5")
    directory = directory.resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError(f"Prepare requires a new or empty run directory: {directory}")
    prepared = _prepared_suite(suite)
    writer = ArtifactWriter(())
    files = {}

    def save(relative, data):
        writer.json(directory / relative, data)
        files[relative] = sha_file(directory / relative)

    def save_document(relative, document):
        save(relative + ".json", document)
        (directory / (relative + ".txt")).write_bytes(document["text"].encode("utf-8"))
        files[relative + ".txt"] = sha_file(directory / (relative + ".txt"))

    save("inputs/source.json", prepared["source"])
    cases = []
    for case in prepared["cases"]:
        identifier = case["case_id"]
        save(f"inputs/{identifier}/cfg.json", case["cfg"])
        save(f"inputs/{identifier}/source.json", case["source"])
        item = {"case_id": identifier, "input_graph_sha256": case["graph_sha256"],
                "oracle_key": case["oracle_key"], "source_sha256": case["source"]["source_sha256"],
                "selection": case["selection"]}
        try:
            document = render_controlled(ControlFlowGraph.model_validate(deepcopy(case["cfg"])), executable=executable)
            save_document(f"inputs/{identifier}/controlled", document)
            item.update(fidelity_status="passed", graph_sha256=document["graph_sha256"])
        except Exception as error:
            item.update(fidelity_status="failed", preparation_error=str(error))
        cases.append(item)
    review_rows = []
    review_manifest = PACKAGE_ROOT / "formal/fixtures/review30.json"
    if review30:
        selection = read_json(review_manifest)
        if [s["index"] for s in selection["samples"]] != list(range(1, 31)):
            raise ValueError("Unexpected review30 inventory")
        for sample in selection["samples"]:
            original = (REPOSITORY_ROOT / sample["analysis_path"]).resolve()
            if not original.is_relative_to(REPOSITORY_ROOT) or sha_file(original) != sample["analysis_sha256"]:
                raise ValueError("Frozen review30 analysis digest mismatch")
            cfg = read_json(original)["cfg"]
            row = dict(sample)
            try:
                if sample["sample_id"] == "F01":
                    if cases[0]["fidelity_status"] != "passed":
                        raise ValueError("F01 conversion failed")
                    relative = "inputs/c01/controlled"
                    document = read_json(directory / (relative + ".json"))
                else:
                    relative = f"verification/review30/{sample['index']:03}-controlled"
                    document = render_controlled(ControlFlowGraph.model_validate(deepcopy(cfg)), executable=executable)
                    save_document(relative, document)
                row.update(status="passed", document=relative + ".json", graph_sha256=document["graph_sha256"])
            except Exception as error:
                row.update(status="failed", error=str(error))
            review_rows.append(row)
    save("verification/review30.json", {"enabled": review30, "manifest_sha256": sha_file(review_manifest), "samples": review_rows})
    manifest = {
        "schema_version": 4, "identity": IDENTITY, "created_at": now(), "run_id": directory.name,
        "suite": suite, **contract_binding(),
        "planned_logical_calls": len(cases), "config": public_config(),
        "implementation": implementation_provenance(), "input_provenance": prepared["provenance"],
        "source_sha256": prepared["source"]["source_sha256"], "cases": cases, "files": files,
        "oracle_sha256": sha_file(EXPERIMENT_ROOT / "f01/oracle.json"),
        "review30_manifest_sha256": sha_file(review_manifest),
        "policy": {"rounds_per_input": 1, "repair_calls": 0, "oracle_in_model_inputs": False,
                   "raw_graph_in_model_inputs": False, "accepted_response_automatic_resend": False,
                   "max_audit_execution_retries": max_audit_execution_retries,
                   "audit_execution_retry": AUDIT_RETRY_POLICY},
    }
    manifest["manifest_sha256"] = canonical_sha256(manifest)
    writer.json(directory / "manifest.json", manifest)
    writer.text(directory / "README.md", "# 受控语义回述与源文核对 v4\n\n完整原文与受控文本按统一契约核对。每案例一次逻辑调用，暂态传输执行重试单独计数。\n"
                "prepare 不联网；run 输出 report.md；replay 仅离线读取新版记录。\n")
    return manifest


def verify_run(directory: Path, *, live: bool) -> dict:
    from skill_ir.audit_execution import AUDIT_RETRY_POLICY
    manifest = read_json(directory / "manifest.json")
    if manifest.get("schema_version") != 4 or manifest.get("identity") != IDENTITY:
        raise ValueError("Unsupported run version; v4 does not replay or migrate historical records")
    unsigned = deepcopy(manifest)
    if unsigned.pop("manifest_sha256", None) != canonical_sha256(unsigned):
        raise ValueError("Prepared run manifest digest mismatch")
    if any(manifest.get(key) != value for key, value in contract_binding().items()):
        raise ValueError("Semantic contract changed since prepare")
    if manifest["policy"].get("audit_execution_retry") != AUDIT_RETRY_POLICY:
        raise ValueError("Audit retry policy changed since prepare")
    if sha_file(EXPERIMENT_ROOT / "f01/oracle.json") != manifest["oracle_sha256"]:
        raise ValueError("External evaluation oracle changed after prepare")
    for relative, digest in manifest["files"].items():
        target = (directory / relative).resolve()
        if not target.is_relative_to(directory.resolve()) or sha_file(target) != digest:
            raise ValueError(f"Prepared input changed: {relative}")
    fresh = _prepared_suite(manifest["suite"])
    if fresh["provenance"] != manifest["input_provenance"] or fresh["source"]["source_sha256"] != manifest["source_sha256"]:
        raise ValueError("Frozen input provenance changed")
    if implementation_provenance()["sha256"] != manifest["implementation"]["sha256"]:
        raise ValueError("Implementation changed since prepare; refusing continuation or reinterpretation")
    if manifest["planned_logical_calls"] != len(fresh["cases"]) or [c["case_id"] for c in manifest["cases"]] != list(SUITES[manifest["suite"]]):
        raise ValueError("Unexpected fixed experiment schedule")
    for actual, expected in zip(manifest["cases"], fresh["cases"], strict=True):
        if any(actual.get(key) != expected[key] for key in ("case_id", "oracle_key", "selection")) or actual["input_graph_sha256"] != expected["graph_sha256"] or actual["source_sha256"] != expected["source"]["source_sha256"]:
            raise ValueError("Per-case frozen selection changed")
    if manifest["config"] != public_config():
        raise ValueError("Pinned model configuration changed")
    review_path = PACKAGE_ROOT / "formal/fixtures/review30.json"
    if sha_file(review_path) != manifest["review30_manifest_sha256"]:
        raise ValueError("Review30 manifest changed")
    review = read_json(directory / "verification/review30.json")
    for sample in review["samples"]:
        path = (REPOSITORY_ROOT / sample["analysis_path"]).resolve()
        if not path.is_relative_to(REPOSITORY_ROOT) or sha_file(path) != sample["analysis_sha256"]:
            raise ValueError("Frozen review30 analysis changed")
    return manifest


def execute_run(directory: Path, *, client_factory=None, secrets=(), replay=False, workers=2,
                progress: Callable[[str], None] | None = None, stop_event: Event | None = None,
                executable: Path | None = None) -> dict:
    from .controlled import verify_controlled
    from .services import audit_source_controlled
    from .evaluation import evaluate
    from .report import render_report, render_suggestions
    from skill_ir.audit_execution import RetryingAuditClient

    directory = directory.resolve()
    manifest = verify_run(directory, live=not replay)
    if not replay and client_factory is None:
        raise ValueError("Live execution requires an explicitly injected client factory")
    writer = ArtifactWriter(tuple(secrets))
    output = directory / "replay" if replay else directory
    stages = {}
    identifiers = [case["case_id"] for case in manifest["cases"]]
    stopping = stop_event if stop_event is not None else Event()
    execution_state = {"not_started_case_ids": [], "case_interruptions": {}}
    execution_state_path = directory / "execution-state.json"
    if replay and execution_state_path.exists():
        execution_state = read_json(execution_state_path)
        unsigned = deepcopy(execution_state)
        if unsigned.pop("state_sha256", None) != canonical_sha256(unsigned):
            raise ValueError("Execution boundary digest mismatch")
        if execution_state.get("manifest_sha256") != sha_file(directory / "manifest.json"):
            raise ValueError("Execution boundary belongs to another prepared run")
        if execution_state.get("interrupted"):
            stopping.set()

    def case_work(case):
        identifier = case["case_id"]
        result = {"status": "blocked", "reason": "Interrupted before this case started"}
        fidelity = "not_checked"
        executions = []
        attempt_number = 0

        def call_path(attempt):
            relative = f"calls/{identifier}/a{attempt:03}"
            return directory / relative, relative

        def single_execution(prompt):
            nonlocal attempt_number
            if stopping.is_set() and not replay:
                raise KeyboardInterrupt("Interrupted before audit execution")
            attempt_number += 1
            artifact, relative = call_path(attempt_number)
            exists = (artifact / "call.json").exists()
            if replay and not exists:
                raise KeyboardInterrupt(execution_state["case_interruptions"].get(
                    identifier, "Offline replay has no saved audit execution: " + relative))
            boundary = directory / f"boundaries/{identifier}.json"
            try:
                client = SavedResponseClient(artifact, writer) if exists else RecordingClient(artifact, client_factory, writer)
                response = client.complete(prompt)
                if replay and boundary.exists():
                    saved_boundary = read_json(boundary)
                    if saved_boundary.get("pending") and saved_boundary.get("attempt") == attempt_number:
                        raise KeyboardInterrupt(saved_boundary["message"])
                recovered = SavedResponseClient(artifact, writer).complete(prompt)
                if canonical_sha256(recovered) != canonical_sha256(response):
                    raise ValueError("Actual and recorded audit responses differ")
                # Explicit live recovery has consumed this complete, verified
                # response even if its later semantic JSON parsing fails.
                if not replay and boundary.exists():
                    saved_boundary = read_json(boundary)
                    if saved_boundary.get("attempt") == attempt_number:
                        writer.json(boundary, {**saved_boundary, "pending": False})
                return recovered
            except KeyboardInterrupt as error:
                if not replay:
                    writer.json(boundary, {"attempt": attempt_number, "pending": True,
                                           "message": str(error), "prompt_sha256": canonical_sha256(prompt)})
                raise

        def persist(attempt, decision):
            relative = f"executions/{identifier}/a{attempt:03}.json"
            original = directory / relative
            if original.exists() and read_json(original) != decision:
                raise ValueError("Saved audit execution decision changed: " + relative)
            # A terminal call may reach disk immediately before interruption.
            # Replay can derive its decision without changing original records.
            writer.json(output / relative, decision)
            executions.append(decision)

        def wait_for_retry(delay_ms, next_attempt):
            if not replay and (stopping.is_set() or stopping.wait(delay_ms / 1000)):
                raise KeyboardInterrupt("Interrupted before audit execution retry")

        saved_calls = any((directory / "calls" / identifier).glob("a*/call.json"))
        replay_not_started = replay and identifier in execution_state["not_started_case_ids"] and not saved_calls
        if (replay and not replay_not_started) or (not replay and not stopping.is_set()):
            try:
                fidelity = "failed"
                if case["fidelity_status"] != "passed":
                    raise ValueError("Controlled conversion failed: " + case.get("preparation_error", ""))
                document = read_json(directory / f"inputs/{identifier}/controlled.json")
                source = read_json(directory / f"inputs/{identifier}/source.json")
                graph = ControlFlowGraph.model_validate(read_json(directory / f"inputs/{identifier}/cfg.json"))
                verify_controlled(document, cfg=graph, executable=executable)
                with (directory / f"inputs/{identifier}/controlled.txt").open(encoding="utf-8", newline="") as stream:
                    if stream.read() != document["text"]:
                        raise ValueError("Stored controlled text differs from checked model text")
                fidelity = "passed"
                # Redaction may not silently mutate the semantically checked input.
                if writer.clean(document["text"]) != document["text"] or writer.clean(source) != source:
                    raise ValueError("A credential overlaps review inputs; refusing to alter checked content")
                client = RetryingAuditClient(
                    execute=single_execution, retries=manifest["policy"]["max_audit_execution_retries"],
                    call_path=call_path, persist=persist, wait_for_retry=wait_for_retry,
                    notify=(lambda decision: progress(f"{identifier}: 暂态传输失败，执行重试 {decision['attempt']}")) if progress else None,
                )
                parsed = audit_source_controlled(source, document, client)
                result = {"status": "complete", "result": parsed, "fidelity_status": "passed"}
            except KeyboardInterrupt as error:
                stopping.set()
                result = {"status": "interrupted", "reason": writer.clean(str(error))}
            except Exception as error:
                if isinstance(error, SavedCallFailure) and error.error_type == "KeyboardInterrupt":
                    stopping.set()
                    result = {"status": "interrupted", "reason": writer.clean(str(error))}
                else:
                    result = {"status": "execution_error", "error_type": error.error_type if isinstance(error, SavedCallFailure) else type(error).__name__, "error": writer.clean(str(error))}
        result["fidelity_status"] = fidelity
        result["audit_executions"] = executions
        writer.json(output / "parsed" / f"{identifier}.json", result)
        stages[identifier] = result
        if progress:
            progress(f"{identifier}: {result['status']}")

    with _exclusive_run(directory):
        with ThreadPoolExecutor(max_workers=max(1, min(workers, len(identifiers)))) as pool:
            try:
                list(pool.map(case_work, manifest["cases"]))
            except KeyboardInterrupt:
                stopping.set()
                pool.shutdown(wait=True, cancel_futures=True)
        for case in manifest["cases"]:
            if case["case_id"] not in stages:
                case_work(case)
        ordered = {identifier: stages[identifier] for identifier in identifiers}
        calls = []
        for identifier, path in ((identifier, path) for identifier in identifiers
                                 for path in sorted((directory / "calls" / identifier).glob("a*/call.json"))):
            trace_path = path.with_name("transport.json")
            trace_error = None
            try:
                record = read_json(path)
                if not isinstance(record, dict) or not {"status", "prompt", "prompt_sha256"}.issubset(record):
                    raise ValueError("Call record is missing its required envelope")
                trace = validated_trace(trace_path)
                if canonical_sha256(record["prompt"]) != record["prompt_sha256"]:
                    raise ValueError("Recorded prompt digest mismatch")
                if record["status"] == "complete":
                    if canonical_sha256(record.get("response")) != record.get("response_sha256"):
                        raise ValueError("Recorded response digest mismatch")
                    if len(trace) != 1 or trace[0].get("status") != "complete" or trace[0].get("prompt") != record["prompt"] or trace[0].get("response") != record.get("response"):
                        raise ValueError("Call and transport response records disagree")
            except (ValueError, TypeError, KeyError) as error:
                record = {"status": "invalid_record"}
                trace, trace_error = [], str(error)
                ordered[identifier] = {**ordered[identifier], "status": "execution_error", "error_type": "ArtifactIntegrityError",
                                       "error": trace_error}
                ordered[identifier].pop("result", None)
                writer.json(output / "parsed" / f"{identifier}.json", ordered[identifier])
            calls.append({"case_id": identifier, "attempt": path.parent.name, "status": record["status"],
                          "prompt_sha256": record.get("prompt_sha256"), "response_sha256": record.get("response_sha256"),
                          "trace_sha256": sha_file(trace_path) if trace_path.exists() else None,
                          "trace_integrity_error": trace_error,
                          "returned_model": trace[-1].get("returned_model") if trace else None,
                          "usage": trace[-1].get("usage") if trace else None,
                          "http_attempts": len(trace[-1].get("http_attempts", [])) if trace else 0})
        logical_count = len({call["case_id"] for call in calls})
        result = {"schema_version": 4, "identity": IDENTITY, "run_id": manifest["run_id"],
                  "suite": manifest["suite"], **contract_binding(),
                  "mode": "replay" if replay else "run", "finished_at": now(),
                  "planned_logical_calls": len(identifiers), "recorded_logical_calls": logical_count,
                  "recorded_execution_calls": len(calls), "audit_execution_retries": len(calls) - logical_count,
                  "http_attempts": sum(call["http_attempts"] for call in calls),
                  "execution_status": "interrupted" if stopping.is_set() else (
                      "complete" if all(s["status"] == "complete" for s in ordered.values()) and not any(c["trace_integrity_error"] for c in calls)
                      else "completed_with_errors"),
                  "manifest_sha256": sha_file(directory / "manifest.json"), "config": manifest["config"],
                  "case_selections": {case["case_id"]: case["selection"] for case in manifest["cases"]},
                  "input_provenance": manifest["input_provenance"], "original_implementation": manifest["implementation"],
                  "replay_implementation": implementation_provenance() if replay else None,
                  "conversion": {key: stage["fidelity_status"] for key, stage in ordered.items()},
                  "review30": read_json(directory / "verification/review30.json"),
                  "stages": ordered, "calls": calls, "evaluation": evaluate(ordered, manifest)}
        if not replay:
            state = {"manifest_sha256": sha_file(directory / "manifest.json"),
                     "interrupted": stopping.is_set(),
                     "not_started_case_ids": [key for key, stage in ordered.items() if stage["status"] == "blocked"],
                     "case_interruptions": {key: stage["reason"] for key, stage in ordered.items()
                                            if stage["status"] == "interrupted"}}
            state["state_sha256"] = canonical_sha256(state)
            writer.json(execution_state_path, state)
        writer.json(output / "report.json", result)
        writer.text(output / "report.md", render_report(result))
        for identifier, stage in ordered.items():
            writer.text(output / "suggestions" / f"{identifier}.md", render_suggestions(identifier, stage))
        return result
