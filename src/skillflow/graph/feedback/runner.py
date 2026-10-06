"""Bounded full re-extraction with certified, independent source/text audits.

Saved calls are the durable boundary. Re-running the state machine first consumes
them; neither recovery nor offline replay can resend an uncertain request.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from threading import Event
from typing import Callable
from uuid import uuid4

from skillflow.graph.audit.controlled import _executable
from skillflow.graph.audit.controlled import render_controlled
from skillflow.graph.audit.controlled import verify_controlled
from skillflow.graph.audit.evidence import normalize_cfg
from skillflow.graph.audit.evidence import canonical_graph_sha256
from skillflow.graph.audit.services import audit_source_controlled
from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.runs import exclusive_run
from skillflow.graph.extraction.pipeline import analyze_skill_with_prompt
from skillflow.graph.extraction.prompt import build_whole_skill_prompt
from skillflow.graph.ir.cfg import ControlFlowGraph
from skillflow.graph.semantic_contract import contract_binding
from skillflow.common.semantic_failure import SemanticFailure
from skillflow.common.recording import RecordingClient
from skillflow.common.recording import SavedResponseClient
from skillflow.common.recording import SavedCallFailure
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import injected_factory
from skillflow.common.recording import now
from skillflow.common.recording import read_json
from skillflow.common.recording import sha_file
from skillflow.common.recording import validated_trace
from skillflow.common.recording import verify_request_identity
from skillflow.graph.feedback.models import FeedbackLimits
from skillflow.graph.feedback.models import FeedbackResult
from skillflow.graph.feedback.policy import decide
from skillflow.graph.feedback.prompts import build_feedback_prompt
from skillflow.common.inputs.snapshot import freeze_input
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.inputs.snapshot import verify_original_input
from skillflow.common.audit_execution import AUDIT_RETRY_POLICY
from skillflow.common.audit_execution import RetryingAuditClient
from skillflow.common.audit_execution import retry_delay_ms

IDENTITY = "skill-ir-semantic-feedback-v5"
CONFIG_KEYS = {"endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
               "retry_base_ms", "retry_max_backoff_ms", "response_format"}


class RunIdentityError(ValueError):
    """Refuse changed inputs, code, config, or previously committed artifacts."""


class MissingSavedCall(KeyboardInterrupt):
    """An interrupted run has no response for this call; replay cannot make one."""


def _config(config):
    if config is None:
        return {"extraction": {}, "audit": {}}
    roles = config if set(config) == {"extraction", "audit"} else {"extraction": config, "audit": config}
    for value in roles.values():
        if not isinstance(value, dict) or set(value) - CONFIG_KEYS:
            raise ValueError("Only public LLM configuration fields may be recorded")
        if value.get("response_format") not in (None, "json_object"):
            raise ValueError("response_format must be None or json_object")
    return deepcopy(roles)


def _printer_identity(renderer):
    try:
        path = _executable(renderer)
        return {"path": str(path), "sha256": sha_file(path)}
    except ValueError:
        return {"path": str(Path(renderer).resolve()) if renderer else None, "sha256": None}


def _seal(payload):
    result = deepcopy(payload)
    result["manifest_sha256"] = canonical_sha256(payload)
    return result


def _prepare(source, directory, initial_analysis, limits, config, writer, renderer):
    if any(path.name != ".runner.lock" for path in directory.iterdir()):
        raise RunIdentityError("A new feedback run requires an empty directory")
    freeze_input(source, directory, writer)
    _, source_bundle, _ = read_snapshot(directory)
    initial = None
    if initial_analysis is not None:
        path = Path(initial_analysis).resolve()
        raw = path.read_bytes()
        data = json.loads(raw)
        if not isinstance(data, dict) or not isinstance(data.get("cfg"), dict):
            raise ValueError("initial-analysis must contain the actual cfg object")
        if writer.clean(data["cfg"]) != data["cfg"]:
            raise ValueError("A credential overlaps the initial graph")
        # Only the actual CFG is an input. Stale raw_candidate is deliberately ignored.
        writer.json(directory / "inputs/initial-cfg.json", data["cfg"])
        initial = {"path": str(path), "raw_sha256": hashlib.sha256(raw).hexdigest()}
    files = {path.relative_to(directory).as_posix(): sha_file(path)
             for path in sorted((directory / "inputs").rglob("*")) if path.is_file()}
    manifest = _seal({
        "schema_version": 5, "identity": IDENTITY, "run_id": directory.name, **contract_binding(),
        "created_at": now(), "limits": limits.model_dump(), "config": config,
        "implementation": implementation_provenance(), "renderer": _printer_identity(renderer),
        "source_sha256": source_bundle["source_sha256"], "initial_analysis": initial,
        "files": files, "logical_call_bounds": limits.logical_call_bounds(initial_graph=initial is not None),
        "execution_call_bounds": limits.execution_call_bounds(initial_graph=initial is not None),
        "policy": {"previous_round_only": True, "auditor_has_feedback": False,
                   "audit_execution_retry": AUDIT_RETRY_POLICY,
                   "success_means": "auditor_passed_only"},
    })
    writer.json(directory / "manifest.json", manifest)
    return manifest


def _verify(directory, source, initial_analysis, limits, config, renderer, replay):
    manifest = read_json(directory / "manifest.json")
    if manifest.get("schema_version") != 5 or manifest.get("identity") != IDENTITY:
        raise RunIdentityError("Unsupported feedback run version; single-audit records are not feedback runs")
    unsigned = deepcopy(manifest)
    digest = unsigned.pop("manifest_sha256", None)
    if canonical_sha256(unsigned) != digest:
        raise RunIdentityError("Feedback manifest digest mismatch")
    if manifest["limits"] != limits.model_dump() or manifest["config"] != config:
        raise RunIdentityError("Feedback configuration changed; use a new run")
    if any(manifest.get(key) != value for key, value in contract_binding().items()):
        raise RunIdentityError("Semantic contract identity changed; use a new run")
    if manifest["policy"].get("audit_execution_retry") != AUDIT_RETRY_POLICY:
        raise RunIdentityError("Audit execution retry policy changed; use a new run")
    if manifest["implementation"] != implementation_provenance():
        raise RunIdentityError("Implementation identity changed; refusing continuation or reinterpretation")
    if manifest["renderer"] != _printer_identity(renderer):
        raise RunIdentityError("Lean printer identity changed")
    actual = {p.relative_to(directory).as_posix(): sha_file(p)
              for p in sorted((directory / "inputs").rglob("*")) if p.is_file()}
    if actual != manifest["files"]:
        raise RunIdentityError("Frozen feedback input inventory or bytes changed")
    _, bundle, metadata = read_snapshot(directory)
    if bundle["source_sha256"] != manifest["source_sha256"]:
        raise RunIdentityError("Frozen source text changed")
    initial = manifest["initial_analysis"]
    if not replay:
        verify_original_input(source, metadata)
        if initial_analysis is not None and initial is None:
            raise RunIdentityError("An initial analysis cannot be added to an existing run")
        if initial is not None:
            path = Path(initial_analysis or initial["path"]).resolve()
            if str(path) != initial["path"] or sha_file(path) != initial["raw_sha256"]:
                raise RunIdentityError("Initial analysis identity changed")
    return manifest


class _RoundClient:
    def __init__(self, runtime, revision, role, factory, maximum):
        self.runtime, self.revision, self.role = runtime, revision, role
        self.factory, self.maximum, self.calls = factory, maximum, 0

    def complete(self, prompt):
        state = self.runtime
        position = {"revision": self.revision, "role": self.role, "attempt": self.calls + 1}
        if state.should_pause("before_call", position):
            raise KeyboardInterrupt("Interrupted before next logical call")
        self.calls += 1
        if self.calls > self.maximum:
            raise ValueError("Logical call budget exceeded")
        relative = f"calls/r{self.revision:03}/{self.role}/a{self.calls:03}"
        directory = state.directory / relative
        exists = (directory / "call.json").exists()
        if not exists and state.replay:
            raise MissingSavedCall("No accepted saved response for " + relative)
        if not exists and self.factory is None:
            raise ValueError(f"An explicitly injected {self.role} client is required")
        # Check before creating records: model text must equal stored, verified text.
        if state.writer.clean(prompt) != prompt:
            raise ValueError("A credential overlaps the actual model input")
        state.used_calls.append((self.revision, self.role, directory))
        if state.progress:
            state.progress(f"第 {self.revision} 轮 {self.role} 调用 {self.calls}：{'读取已有响应' if exists else '开始'}")
        client = SavedResponseClient(directory, state.writer) if exists else RecordingClient(directory, self.factory, state.writer)
        try:
            response = client.complete(prompt)
        except KeyboardInterrupt as error:
            if not state.replay:
                state.writer.json(state.directory / "execution-boundary.json", _seal({
                    "kind": "after_call_interrupt", "position": position,
                    "message": state.writer.clean(str(error)),
                }))
            raise
        if (state.replay and state.boundary and state.boundary["kind"] == "after_call_interrupt"
                and state.boundary["position"] == position):
            raise KeyboardInterrupt(state.boundary["message"])
        # Use the very response whose durable transport/call identity was checked.
        recovered = SavedResponseClient(directory, state.writer).complete(prompt)
        if canonical_sha256(response) != canonical_sha256(recovered):
            raise ValueError("Actual and recorded responses differ")
        # Only explicitly requested JSON-output callers opt into wire-parameter
        # validation here. The ordinary extraction/audit configuration stays
        # unchanged; complete(prompt) injected clients declare no HTTP facts.
        role_config = state.config[self.role]
        if role_config.get("response_format") is not None:
            request_identity = verify_request_identity(directory, role_config, prompt=prompt)
            state.stable(relative + "/request-validation.json", request_identity)
        if state.progress:
            state.progress(f"第 {self.revision} 轮 {self.role} 调用 {self.calls}：响应已保存")
        return recovered


class _AuditClient:
    """One semantic audit unit, with bounded independent transport executions."""

    def __init__(self, runtime, revision, factory, retries, records):
        self.runtime, self.revision, self.retries, self.records = runtime, revision, retries, records
        self.client = _RoundClient(runtime, revision, "audit", factory, retries + 1)

    def _wait_for_retry(self, delay_ms, position):
        state = self.runtime
        if state.should_pause("before_audit_retry", position):
            raise KeyboardInterrupt("Interrupted before audit execution retry")
        if not state.replay and state.stopping.wait(delay_ms / 1000):
            state.should_pause("before_audit_retry", position)
            raise KeyboardInterrupt("Interrupted during audit execution retry backoff")

    def complete(self, prompt):
        state = self.runtime

        def call_path(attempt):
            relative = f"calls/r{self.revision:03}/audit/a{attempt:03}"
            return state.directory / relative, relative

        def persist(attempt, decision):
            self.records.append(decision)
            state.stable(f"rounds/r{self.revision:03}/audit-executions/a{attempt:03}.json", decision)

        def notify(decision):
            if state.progress:
                state.progress(f"第 {self.revision} 轮 audit 暂态执行失败（{decision['category']}）；"
                               f"准备额外重试 {decision['attempt']}/{self.retries}，保留本次失败记录")

        return RetryingAuditClient(
            execute=self.client.complete, retries=self.retries, call_path=call_path,
            persist=persist, notify=notify, delay=retry_delay_ms,
            wait_for_retry=lambda delay, attempt: self._wait_for_retry(
                delay, {"revision": self.revision, "attempt": attempt}),
        ).complete(prompt)


class _Runtime:
    def __init__(self, directory, writer, replay, stopping, progress):
        self.directory, self.writer, self.replay = directory, writer, replay
        self.output = directory / "replay" if replay else directory
        self.stopping, self.progress, self.used_calls = stopping, progress, []
        boundary_path = directory / "execution-boundary.json"
        self.boundary = read_json(boundary_path) if replay and boundary_path.exists() else None
        if self.boundary:
            unsigned = deepcopy(self.boundary)
            digest = unsigned.pop("manifest_sha256", None)
            if canonical_sha256(unsigned) != digest:
                raise RunIdentityError("Interruption boundary digest mismatch")
        if not replay:
            writer.json(boundary_path, _seal({"kind": "none", "position": {}}))

    def should_pause(self, kind, position):
        if self.replay:
            return bool(self.boundary and self.boundary["kind"] == kind and self.boundary["position"] == position)
        if self.stopping.is_set():
            self.writer.json(self.directory / "execution-boundary.json", _seal({"kind": kind, "position": position}))
            return True
        return False

    def stable(self, relative, value, *, text=False):
        """Compare committed material before reuse; replay writes its own derivations."""
        path = self.directory / relative
        if path.exists():
            saved = path.read_bytes().decode("utf-8") if text else read_json(path)
            if (saved != value if text else canonical_sha256(saved) != canonical_sha256(value)):
                raise RunIdentityError("Committed derived artifact changed: " + relative)
        if self.writer.clean(value) != value:
            raise ValueError("A credential overlaps a verified artifact")
        target = self.output / relative
        if text:
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
            try:
                temporary.write_bytes(value.encode("utf-8"))
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        else:
            self.writer.json(target, value)

    def counts(self):
        extraction = [(r, d) for r, role, d in self.used_calls if role == "extraction"]
        audit = [(r, d) for r, role, d in self.used_calls if role == "audit"]
        audit_units = len({r for r, _ in audit})
        http, retries, observable = 0, 0, True
        models, integrity_errors = set(), []
        for _, _, directory in self.used_calls:
            try:
                trace = validated_trace(directory / "transport.json")
            except (ValueError, OSError) as error:
                observable = False
                integrity_errors.append({"call": directory.relative_to(self.directory).as_posix(),
                                         "error": self.writer.clean(str(error))})
                continue
            if not trace:
                observable = False
            for call in trace:
                attempts = call.get("http_attempts", [])
                http += len(attempts)
                retries += max(0, len(attempts) - 1)
                if call.get("http_attempts_observed") is False:
                    observable = False
                if call.get("returned_model"):
                    models.add(call["returned_model"])
                for attempt in attempts:
                    if attempt.get("returned_model"):
                        models.add(attempt["returned_model"])
        revisions = [r for r, _ in extraction]
        return {"extraction_logical_calls": len(extraction), "audit_logical_calls": audit_units,
                "total_logical_calls": len(extraction) + audit_units,
                "audit_execution_calls": len(audit), "audit_execution_retries": len(audit) - audit_units,
                "total_execution_calls": len(extraction) + len(audit),
                "semantic_revisions": max(revisions, default=0),
                "structural_repairs": sum(max(0, sum(r == n for r, _ in extraction) - 1) for n in set(revisions)),
                "http_attempts": http, "http_retries": retries, "http_attempts_observed": observable,
                "returned_models": sorted(models), "record_integrity_errors": integrity_errors}


def _run(directory, manifest, *, extraction_factory, audit_factory, writer, renderer, replay, stop_event, progress):
    from skillflow.graph.feedback.report import render_report
    package, source, snapshot = read_snapshot(directory)
    if writer.clean(source) != source:
        raise ValueError("A credential overlaps the frozen source text")
    runtime = _Runtime(directory, writer, replay, stop_event or Event(), progress)
    runtime.config = manifest["config"]
    limits = FeedbackLimits.model_validate(manifest["limits"])
    result = {"schema_version": 5, "identity": IDENTITY, "run_id": manifest["run_id"], **contract_binding(),
              "representation_summary": {"represented_ids": [], "conservative_ids": []},
              "status": "interrupted", "reason": "尚未开始核对。", "rounds": [], "counts": {},
              "limits": {**manifest["limits"], "logical_call_bounds": manifest["logical_call_bounds"],
                         "execution_call_bounds": manifest["execution_call_bounds"]},
              "last_valid_cfg": None, "passed_cfg": None, "source_sha256": source["source_sha256"],
              "boundaries": ["核对器通过不等于已证明源文与图语义等价。", "受控文本仅保持图中明确记录的事实。",
                             "二进制或不透明内容不构成已完成行为理解或运行保证；见 inputs/snapshot.json。"]}
    previous_graph, previous_audit = None, None
    for revision in range(limits.max_semantic_revisions + 1):
        if runtime.should_pause("before_round", {"revision": revision}):
            result.update(status="interrupted", reason="用户中断；未启动后续调用。")
            break
        row = {"revision": revision, "status": "running", "extraction": None, "structural": None,
               "fidelity": None, "audit": None, "audit_execution": [], "decision": None, "feedback_prompt": None,
               "error": None, "graph_sha256": None}
        result["representation_summary"] = {"represented_ids": [], "conservative_ids": []}
        result["rounds"].append(row)
        prefix = f"rounds/r{revision:03}"
        phase = "extraction"
        try:
            if revision == 0 and manifest["initial_analysis"] is not None:
                graph = ControlFlowGraph.model_validate(read_json(directory / "inputs/initial-cfg.json"))
                row["extraction"] = {"status": "provided_graph", "attempts": 0,
                                     "notice": "仅加载实际 CFG，不使用已有 raw_candidate。"}
            else:
                prompt = (build_whole_skill_prompt(package) if revision == 0 else
                          build_feedback_prompt(package, previous_graph, previous_audit))
                if revision:
                    row["feedback_prompt"] = prompt
                    runtime.stable(prefix + "/feedback-prompt.txt", prompt, text=True)
                client = _RoundClient(runtime, revision, "extraction", extraction_factory, limits.max_structural_repairs + 1)
                def save_attempt(attempt):
                    runtime.stable(prefix + f"/extraction-attempts/a{attempt['attempt']:03}.json", attempt)
                analysis = analyze_skill_with_prompt(package, initial_prompt=prompt, client=client,
                                                     max_repair_rounds=limits.max_structural_repairs,
                                                     on_attempt=save_attempt)
                row["extraction"] = analysis.model_dump(mode="json")
                runtime.stable(prefix + "/analysis.json", row["extraction"])
                runtime.stable(prefix + "/candidate.json", analysis.raw_candidate)
                runtime.stable(prefix + "/structural-diagnostics.json", analysis.diagnostics)
                if analysis.status != "complete" or analysis.cfg is None:
                    raise ValueError("结构修复已耗尽；没有结构有效的完整候选。")
                graph = analysis.cfg
            graph.validate_integrity()
            current = normalize_cfg(graph)
            row["graph_sha256"] = canonical_graph_sha256(current)
            row["structural"] = {"status": "passed", "graph_sha256": row["graph_sha256"]}
            result["last_valid_cfg"] = deepcopy(current)
            runtime.stable(prefix + "/cfg.json", current)
            phase = "fidelity"
            document = render_controlled(graph, executable=renderer)
            verify_controlled(document, cfg=graph, executable=renderer)
            runtime.stable(prefix + "/controlled.json", document)
            runtime.stable(prefix + "/controlled.txt", document["text"], text=True)
            # The stored bytes, certificate and exact model payload are the same text.
            if (runtime.output / (prefix + "/controlled.txt")).read_bytes() != document["text"].encode("utf-8"):
                raise ValueError("Actual controlled text bytes differ from the certificate")
            row["fidelity"] = {"status": "passed", "certificate": document["certificate"]}
            runtime.stable(prefix + "/certificate.json", document["certificate"])
            phase = "audit"
            audit_client = _AuditClient(runtime, revision, audit_factory, limits.max_audit_execution_retries,
                                        row["audit_execution"])
            audit = audit_source_controlled(source, document, audit_client)
            row["audit"] = audit
            runtime.stable(prefix + "/audit.json", audit)
            decision = decide(audit, revision, limits.max_semantic_revisions)
            result["representation_summary"] = deepcopy(decision["representation_summary"])
            row["decision"], row["status"] = decision, decision["status"]
            runtime.stable(prefix + "/decision.json", decision)
            result.update(status=decision["status"], reason=decision["reason"])
            if decision["status"] == "audit_passed":
                result["passed_cfg"] = deepcopy(current)
            previous_graph, previous_audit = current, audit
        except SemanticFailure as error:
            row.update(status="semantic_failure", error={"type": "SemanticFailure",
                       "message": writer.clean(error.reason), "failure": writer.clean(error.failure)})
            runtime.stable(prefix + "/semantic-failure.json", row["error"]["failure"])
            result.update(status="semantic_failure", reason=row["error"]["message"])
        except (KeyboardInterrupt, SavedCallFailure) as error:
            interrupted = isinstance(error, KeyboardInterrupt) or getattr(error, "error_type", None) == "KeyboardInterrupt"
            status = "interrupted" if interrupted else phase + "_error"
            row.update(status=status, error={"type": getattr(error, "error_type", type(error).__name__),
                                            "message": writer.clean(str(error))})
            result.update(status=status, reason=row["error"]["message"])
            if interrupted:
                runtime.stopping.set()
        except Exception as error:
            status = phase + "_error"
            row.update(status=status, error={"type": type(error).__name__, "message": writer.clean(str(error))})
            result.update(status=status, reason=row["error"]["message"])
        finally:
            row["decision"] = row["decision"] or {"status": row["status"], "reason": result["reason"]}
            runtime.writer.json(runtime.output / (prefix + "/round.json"), row)
            result["counts"] = runtime.counts()
            runtime.writer.json(runtime.output / "result.json", result)
            runtime.writer.text(runtime.output / "report.md", render_report(result))
        if row["status"] != "revise":
            break
    result["counts"] = runtime.counts()
    bounds = manifest["logical_call_bounds"]
    if result["counts"]["extraction_logical_calls"] > bounds["extraction"] or result["counts"]["audit_logical_calls"] > bounds["audit"]:
        raise AssertionError("Feedback exceeded its deterministic logical call bound")
    if result["counts"]["audit_execution_calls"] > manifest["execution_call_bounds"]["audit"]:
        raise AssertionError("Feedback exceeded its deterministic audit execution bound")
    FeedbackResult.model_validate(result)
    runtime.writer.json(runtime.output / "result.json", result)
    runtime.writer.text(runtime.output / "report.md", render_report(result))
    if result["last_valid_cfg"] is not None:
        runtime.writer.json(runtime.output / "last-valid-cfg.json", result["last_valid_cfg"])
    else:
        (runtime.output / "last-valid-cfg.json").unlink(missing_ok=True)
    if result["passed_cfg"] is not None:
        runtime.writer.json(runtime.output / "passed-cfg.json", result["passed_cfg"])
    else:
        (runtime.output / "passed-cfg.json").unlink(missing_ok=True)
    return result


def refine_skill(source, *, run_dir, initial_analysis=None, max_semantic_revisions=3,
                 max_structural_repairs=3, max_audit_execution_retries=2, extraction_client=None, audit_client=None,
                 extraction_factory=None, audit_factory=None, config=None, secrets=(),
                 renderer=None, replay=False, stop_event=None, progress: Callable | None = None):
    """Run/resume a generic package. Clients are independent; no implicit API creation."""
    directory = Path(run_dir).resolve()
    # Validate before acquiring a lock: even a rejected run must not touch input.
    if source is not None:
        original = Path(source).expanduser().resolve()
        if original.is_dir() and directory.is_relative_to(original):
            raise ValueError("run directory must not be nested inside the Skill input")
    limits = FeedbackLimits(max_semantic_revisions=max_semantic_revisions,
                            max_structural_repairs=max_structural_repairs,
                            max_audit_execution_retries=max_audit_execution_retries)
    config = _config(config)
    writer = ArtifactWriter(tuple(secrets))
    if (extraction_client is not None and extraction_factory is not None) or (audit_client is not None and audit_factory is not None):
        raise ValueError("Inject either a client or a factory for each role")
    if replay and any(x is not None for x in (extraction_client, audit_client, extraction_factory, audit_factory)):
        raise ValueError("Offline replay does not accept online clients")
    extraction_factory = extraction_factory or (injected_factory(extraction_client) if extraction_client is not None else None)
    audit_factory = audit_factory or (injected_factory(audit_client) if audit_client is not None else None)
    with exclusive_run(directory):
        if not (directory / "manifest.json").exists():
            if replay:
                raise RunIdentityError("No feedback manifest to replay")
            manifest = _prepare(source, directory, initial_analysis, limits, config, writer, renderer)
        else:
            manifest = _verify(directory, source, initial_analysis, limits, config, renderer, replay)
        return _run(directory, manifest, extraction_factory=extraction_factory, audit_factory=audit_factory,
                    writer=writer, renderer=renderer, replay=replay, stop_event=stop_event, progress=progress)


def replay_run(run_dir, *, renderer=None):
    """Reparse/compile/print/check saved calls without creating a network client."""
    manifest = read_json(Path(run_dir) / "manifest.json")
    if manifest.get("identity") != IDENTITY or manifest.get("schema_version") != 5:
        raise RunIdentityError("Unsupported feedback run version")
    return refine_skill(None, run_dir=run_dir, config=manifest["config"], replay=True,
                        renderer=renderer, **manifest["limits"])
