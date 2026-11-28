"""Synthetic standard-library tests for passive cost arithmetic; no real runs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("passive_cost_audit", Path(__file__).with_name("audit_cost_provenance.py"))
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def row(events, *, answer="answer", name="attempt-one", exited=True):
    public = AUDIT.public_turns("\n".join(json.dumps(item) for item in events).encode(),
        None if answer is None else AUDIT.sha(answer.encode()), name, [])
    return {"request": name, "thread_id": public["thread_ids"][0] if len(public["thread_ids"]) == 1 else None,
            "exit_confirmed": exited, "ambiguous_final": public["ambiguous_final"], "_public": public}


def events(*, response_id="response-one", usage=None):
    return [{"type": "thread.started", "thread_id": "thread-one"},
            {"type": "turn.started", "turn_id": "turn-one"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "answer"}},
            {"type": "turn.completed", "turn_id": "turn-one", "response_id": response_id,
             "usage": usage if usage is not None else {"input_tokens": 100, "cached_input_tokens": 70,
                                                        "output_tokens": 12, "reasoning_output_tokens": 4}}]


class PublicAccountingTests(unittest.TestCase):
    def test_complete_final_uses_input_plus_output_without_adding_subsets(self):
        item = row(events())
        complete, partial, identities = AUDIT.finalize_usage([item])
        self.assertEqual(complete["total_tokens"], 112)
        self.assertEqual(complete["cached_input_tokens"], 70)
        self.assertEqual(partial, {})
        self.assertTrue(item["usage_known"])
        self.assertEqual(len(identities), 1)
        self.assertEqual(item["unreported_counter_fields"], ["cache_write_input_tokens"])

    def test_no_completion_never_implies_zero_tokens(self):
        item = row(events()[:2], answer=None, exited=False)
        complete, partial, identities = AUDIT.finalize_usage([item])
        self.assertEqual((complete, partial, identities), ({}, {}, []))
        self.assertEqual(item["usage_completeness"], "unknown")
        self.assertFalse(item["usage_known"])

    def test_unattributed_reported_usage_stays_partial(self):
        item = row(events(), answer=None)
        complete, partial, _ = AUDIT.finalize_usage([item])
        self.assertEqual(complete, {})
        self.assertEqual(partial["total_tokens"], 112)
        self.assertEqual(item["usage_completeness"], "partial")

    def test_duplicate_public_response_is_counted_once_across_attempts(self):
        first, duplicate = row(events()), row(events(), name="attempt-two")
        complete, partial, identities = AUDIT.finalize_usage([first, duplicate])
        self.assertEqual(complete["total_tokens"], 112)
        self.assertEqual(partial, {})
        self.assertEqual(len(identities), 1)
        self.assertEqual(duplicate["duplicate_usage_events"], 1)

    def test_conflicting_response_identity_cannot_remain_complete(self):
        first = row(events())
        conflict = row(events(usage={"input_tokens": 101, "output_tokens": 12}), name="attempt-two")
        complete, partial, identities = AUDIT.finalize_usage([first, conflict])
        self.assertEqual(complete, {})
        self.assertEqual(partial["total_tokens"], 112)
        self.assertTrue(identities[0]["conflict"])
        self.assertFalse(first["usage_known"])

    def test_network_retry_is_counted_separately_but_retains_repair_axes(self):
        self.assertEqual(AUDIT.classify("flow", "calls/a001/call.json", "attempt-001")["category"], "normal")
        self.assertEqual(AUDIT.classify("flow", "calls/a002/call.json", "attempt-001")["category"], "structural_correction")
        self.assertEqual(AUDIT.classify("revision/review", "calls/review/a001/call.json", "attempt-001")["category"], "semantic_repair")
        value = AUDIT.classify("revision-processing", "calls/a002/call.json", "attempt-002")
        self.assertEqual(value["category"], "network_retry")
        self.assertTrue(value["semantic_repair"] and value["structural_correction"])

    def test_internal_reconnect_notice_does_not_infer_attempts_or_missing_usage(self):
        notice = {"type": "error", "message": "Reconnecting... 2/5 (request timed out)"}
        pending = row(events()[:2] + [notice], answer=None, exited=False)
        internal = AUDIT.reconnect_notices(pending["_public"]["public_notices"])
        self.assertEqual(len(internal), 1)
        self.assertEqual(internal[0]["message"], notice["message"])
        self.assertIsNone(internal[0]["underlying_http_attempts"])
        self.assertIsNone(internal[0]["additional_unreported_usage"])
        complete, partial, _ = AUDIT.finalize_usage([pending])
        self.assertEqual((complete, partial), ({}, {}))
        self.assertEqual(pending["usage_completeness"], "unknown")
        finished = row(events()[:2] + [notice] + events()[2:])
        complete, partial, _ = AUDIT.finalize_usage([finished])
        self.assertEqual(complete["total_tokens"], 112)
        self.assertEqual(partial, {})
        self.assertEqual(AUDIT.classify("graph", "calls/a001/call.json", "attempt-001")["category"], "normal")

    def test_launch_marker_is_not_pid_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            attempt = root / "transport/task/request/attempt-001"
            attempt.mkdir(parents=True)
            logical = root / "task/calls/task/a001/call.json"
            logical.parent.mkdir(parents=True)
            core = "Complete supplied prompt."
            logical.write_text(json.dumps({"prompt": core, "prompt_sha256": AUDIT.digest(core)}), encoding="utf-8")
            delivery = b"complete supplied prompt"
            (attempt.parent / "prompt.txt").write_bytes(delivery)
            fixtures = {
                attempt.parent / "request.json": {"logical_call": "calls/task/a001/call.json", "core_sha256": AUDIT.sha(core.encode()),
                    "delivery_sha256": AUDIT.sha(delivery), "network_retries": 2},
                attempt / "launch.json": {"stdin_sha256": AUDIT.sha(delivery), "command": []},
                attempt / "started.json": {"started_at": "2026-11-11T00:00:00+00:00"},
                attempt / "process.json": {"status": "launch_error", "exited": False},
            }
            for path, value in fixtures.items():
                path.write_text(json.dumps(value), encoding="utf-8")
            warnings, issues = [], []
            failed = AUDIT.attempt_record(root, attempt / "started.json", warnings, issues, False)
            self.assertIs(failed["native_process_started"], False)
            (attempt / "process.json").unlink()
            pending = AUDIT.attempt_record(root, attempt / "started.json", warnings, issues, False)
            self.assertIsNone(pending["native_process_started"])
            (attempt / "pid.json").write_text('{"pid": 123}', encoding="utf-8")
            confirmed = AUDIT.attempt_record(root, attempt / "started.json", warnings, issues, False)
            self.assertIs(confirmed["native_process_started"], True)
            self.assertEqual(issues, [])

    def test_closed_audit_reconciles_metrics_and_independently_checks_replay_starts(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            run = project / "experiments/doe/runs/fresh-fixture"
            attempt = run / "transport/task/request/attempt-001"
            attempt.mkdir(parents=True)
            owner = attempt.parent
            core, answer = "Complete supplied prompt.", b"answer"
            def save(path, value):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value), encoding="utf-8")
            executable = str(project / "codex.exe")
            command = [executable, "exec", "--ignore-user-config", "--ignore-rules", "-c",
                       'model_reasoning_effort="high"', "-c", 'model_provider="openai"']
            (owner / "prompt.txt").write_text(core, encoding="utf-8")
            (owner / "answer.txt").write_bytes(answer)
            save(owner / "request.json", {"logical_call": "calls/task/a001/call.json", "core_sha256": AUDIT.sha(core.encode()),
                "delivery_sha256": AUDIT.sha(core.encode()), "network_retries": 2,
                "runtime": {"model": "gpt-6.1-sol", "effort": "high", "provider": "openai"}})
            save(owner / "accepted.json", {"attempt": 1, "answer_sha256": AUDIT.sha(answer)})
            save(run / "task/calls/task/a001/call.json", {"prompt": core, "prompt_sha256": AUDIT.digest(core)})
            save(attempt / "started.json", {"started_at": "2026-11-11T00:00:00+00:00"})
            save(attempt / "pid.json", {"pid": 123})
            save(attempt / "launch.json", {"command": command, "stdin_sha256": AUDIT.sha(core.encode())})
            save(attempt / "process.json", {"exited": True, "status": "exited", "returncode": 0})
            (attempt / "stdout.jsonl").write_text("\n".join(json.dumps(item) for item in events()), encoding="utf-8")
            save(attempt / "usage.json", {"known": True, "usage": events()[-1]["usage"]})
            save(run / "run-protocol.json", {"case_id": "ga4", "cli_executable": executable,
                "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai"},
                "normal_semantic_requests": 7, "workers": 2, "semantic_repairs": 1,
                "structural_corrections_per_stage": 1, "implementation_sha256": "fixture"})
            manifest = {"implementation": {"sha256": "fixture"}}
            save(run / "manifest.json", {**manifest, "manifest_sha256": AUDIT.digest(manifest)})
            replay = {"status": "failed", "reason": "Preserve the actual failed replay.", "new_native_markers": 0}
            save(run / "replay-check.json", replay)
            save(run / "replay-started.json", {"maximum_replays": 1, "started_at": "2026-11-11T00:01:00+00:00"})
            save(run / "controller-finished.json", {"status": "partial", "replay": replay})
            usage = {**events()[-1]["usage"], "total_tokens": 112}
            metrics = {"native_process_starts": 1, "unknown_native_process_starts": 0, "logical_requests": 1,
                "network_retry_attempts": 0, "complete_usage_requests": 1, "partial_usage_requests": 0,
                "unknown_usage_requests": 0, "launch_attempts": 1, "known_token_usage": usage,
                "inputs_rejected_before_start": 0, "known_request_seconds": 0,
                "unknown_duration_requests": 1, "wall_clock_seconds": None,
                "partial_token_usage": {}, "requests": [{"request": "transport/task/request/attempt-001",
                    "complete_token_usage": usage, "partial_token_usage": {}, "thread_id": "thread-one",
                    "usage_completeness": "complete", "duplicate_usage_events": 0,
                    "native_process_started": True, "structural_correction": False}]}
            save(run / "metrics.json", metrics)
            prepared = {"run_directory": str(run)}
            with patch.object(AUDIT, "PROJECT", project), patch.object(AUDIT, "provenance", lambda *args: {}):
                result = AUDIT.audit("ga4", prepared)
                self.assertEqual(result["issues"], [])
                self.assertEqual(result["status"], "verified")
                self.assertTrue(result["replay"]["zero_new_launch_markers_established"])
                self.assertEqual(result["replay"]["receipt"]["status"], "failed")
                metrics["known_token_usage"] = {**usage, "total_tokens": 111}
                save(run / "metrics.json", metrics)
                result = AUDIT.audit("ga4", prepared)
                self.assertIn("Saved metrics disagree with independently read public records", result["issues"])
                save(attempt / "started.json", {"started_at": "2026-11-11T00:02:00+00:00"})
                result = AUDIT.audit("ga4", prepared)
                self.assertFalse(result["replay"]["zero_new_launch_markers_established"])
                self.assertEqual(result["replay"]["markers_at_or_after_replay"], ["transport/task/request/attempt-001"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
