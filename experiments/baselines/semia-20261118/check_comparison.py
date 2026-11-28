"""Mocked transport and evidence-gate checks; never starts a native model."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("semia_comparison_test_target", BASE / "run_comparison.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LlmError(RuntimeError):
    pass


class ConfigError(LlmError):
    pass


PROVIDER = SimpleNamespace(LlmSynthesisError=LlmError, LlmSynthesisConfigError=ConfigError)


class ComparisonChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=BASE / "analysis")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = self.root / "artifacts"
        self.artifacts.mkdir()
        self.body = "Frozen source data\n中文引用\n"
        (self.artifacts / "prepared_skill.md").write_bytes(self.body.encode())
        module.save(self.artifacts / "complete-source-receipt.json", {
            "all_files_present": True, "prepared_sha256": module.sha(self.artifacts / "prepared_skill.md")})
        module.save(self.artifacts / "prepare_metadata.json", {"hostile_input_nonce": "test_nonce"})
        self.prompt = f"prefix\n<<<SEMIA_HOSTILE_INPUT id=test_nonce>>>\n{self.body.rstrip()}\n<<<SEMIA_END id=test_nonce>>>\nsuffix"
        self.received = []
        self.transport = module.Transport(self.root, "pinned-codex.exe", PROVIDER, timeout=0.5)

    def popen(self, mode="success"):
        owner = self

        class Child:
            def __init__(self, cmd, **kwargs):
                self.pid = 87654
                self.returncode = 9 if mode == "nonzero" else 0
                if mode not in ("missing", "timeout", "unreaped"):
                    Path(cmd[cmd.index("--output-last-message") + 1]).write_text("facts\n中文\n", encoding="utf-8")
                if mode not in ("timeout", "unreaped", "unknown_usage"):
                    kwargs["stdout"].write(b'{"type":"turn.completed","usage":{"input_tokens":13,"output_tokens":7}}\n')
                if mode == "tool":
                    kwargs["stdout"].write(b'{"type":"item.completed","item":{"type":"command_execution"}}\n')
                self.cmd = cmd

            def communicate(self, input, timeout):
                owner.received.append(input)
                if mode in ("timeout", "unreaped"):
                    raise subprocess.TimeoutExpired(self.cmd, timeout)

            def wait(self, timeout):
                if mode == "unreaped":
                    raise subprocess.TimeoutExpired(self.cmd, timeout)
                self.returncode = -1
                return self.returncode

        return Child

    def record(self):
        return json.loads((self.root / "transport/call-001/request.json").read_text("utf-8"))

    def test_prompt_and_response_passthrough_and_public_usage(self):
        with patch.object(module.subprocess, "Popen", self.popen()):
            self.assertEqual(self.transport(self.artifacts, self.prompt, module.MODEL), "facts\n中文\n")
        self.assertEqual(self.received, [self.prompt.encode()])
        record = self.record()
        self.assertTrue(record["native_start"])
        self.assertTrue(record["source_payload_verified"])
        self.assertEqual(record["usage"], {"input_tokens": 13, "output_tokens": 7})

    def test_actual_prompt_source_omission_fails_before_native_start(self):
        with patch.object(module.subprocess, "Popen") as popen:
            with self.assertRaises(ConfigError):
                self.transport(self.artifacts, self.prompt.replace("中文引用", ""), module.MODEL)
            popen.assert_not_called()
        self.assertFalse(self.record()["native_start"])

    def test_prepared_source_tamper_fails_before_native_start(self):
        (self.artifacts / "prepared_skill.md").write_text("changed", encoding="utf-8")
        with patch.object(module.subprocess, "Popen") as popen:
            with self.assertRaises(ConfigError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
            popen.assert_not_called()

    def test_recommendation_body_newline_and_phase_budget(self):
        self.transport.phase = "recommendation"
        prompt = self.prompt.replace("\n<<<SEMIA_END", "\n\n<<<SEMIA_END")
        with patch.object(module.subprocess, "Popen", self.popen()):
            self.transport(self.artifacts, prompt, module.MODEL)
            self.transport(self.artifacts, prompt, module.MODEL)
            self.transport(self.artifacts, prompt, module.MODEL)
            with self.assertRaises(ConfigError):
                self.transport(self.artifacts, prompt, module.MODEL)
        self.assertEqual(len(self.transport.calls), 3)
        self.assertTrue(all(c["phase"] == "recommendation" for c in self.transport.calls))

    def test_nonzero_exit_keeps_raw_output_usage_and_failure(self):
        with patch.object(module.subprocess, "Popen", self.popen("nonzero")):
            with self.assertRaises(LlmError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
        self.assertEqual(self.record()["returncode"], 9)
        self.assertEqual(self.record()["usage"]["output_tokens"], 7)
        self.assertIsNotNone(self.record()["error"])

    def test_missing_response_is_failure(self):
        with patch.object(module.subprocess, "Popen", self.popen("missing")):
            with self.assertRaises(LlmError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
        self.assertIn("Missing response", self.record()["error"])

    def test_prestart_error_has_zero_native_starts(self):
        with patch.object(module.subprocess, "Popen", side_effect=OSError("launch failed")):
            with self.assertRaises(LlmError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
        self.assertFalse(self.record()["native_start"])
        self.assertIsNone(self.record()["usage"])

    def test_timeout_kills_owned_tree_and_preserves_unknown_usage(self):
        with patch.object(module.subprocess, "Popen", self.popen("timeout")), \
             patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as kill:
            with self.assertRaises(LlmError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
            self.assertEqual(kill.call_args.args[0], ["taskkill", "/PID", "87654", "/T", "/F"])
        self.assertTrue(self.record()["timed_out"])
        self.assertEqual(self.record()["tree_cleanup_returncode"], 0)
        self.assertIsNone(self.record()["usage"])

    def test_unreaped_timeout_is_nonretryable_configuration_failure(self):
        with patch.object(module.subprocess, "Popen", self.popen("unreaped")), \
             patch.object(module.subprocess, "run", return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(ConfigError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
        self.assertTrue(self.record()["tree_cleanup_unresolved"])

    def test_unexpected_tool_event_is_nonretryable(self):
        with patch.object(module.subprocess, "Popen", self.popen("tool")):
            with self.assertRaises(ConfigError):
                self.transport(self.artifacts, self.prompt, module.MODEL)
        self.assertEqual(self.record()["unexpected_tool_events"], ["command_execution"])

    def test_unknown_usage_remains_null(self):
        with patch.object(module.subprocess, "Popen", self.popen("unknown_usage")):
            self.transport(self.artifacts, self.prompt, module.MODEL)
        self.assertIsNone(self.record()["usage"])

    def test_failed_first_pilot_can_advance_only_with_bound_closeout(self):
        (self.root / "pilot/001").mkdir(parents=True)
        (self.root / "analysis").mkdir()
        module.save(self.root / "input-manifest.json", {"cases": []})
        finished = self.root / "pilot/001/finished.json"
        module.save(finished, {"exit_code": 2, "finished_at_utc": "2026-11-18T00:00:00Z", "native_starts": 20})
        with patch.object(module, "BASE", self.root):
            with self.assertRaises(ValueError):
                module.verify_closeout()
            receipt = {"status": "complete", "pilot_finished_sha256": module.sha(finished),
                       "input_manifest_sha256": module.sha(self.root / "input-manifest.json"),
                       "source_commit": module.COMMIT}
            module.save(self.root / "analysis/001-closeout.json", receipt)
            self.assertEqual(module.verify_closeout(), receipt)
            module.save(finished, {"exit_code": 0, "finished_at_utc": "changed", "native_starts": 1})
            with self.assertRaises(ValueError):
                module.verify_closeout()

    def test_source_drift_and_local_manifest_repin_are_rejected(self):
        source = self.root / "source"
        source.mkdir()
        (self.root / "pilot/001").mkdir(parents=True)
        files = []
        for number in range(360):
            path = source / f"file-{number:03d}.py"
            path.write_bytes(b"original\n")
            files.append({"path": path.name, "sha256": module.sha(path)})
        pins = {"commit": module.COMMIT, "files": files}
        module.save(self.root / "source-manifest.json", pins)
        module.save(self.root / "pilot/001/runtime.json", {"source_file_hashes": {x["path"]: x["sha256"] for x in files}})
        with patch.object(module, "BASE", self.root):
            self.assertEqual(len(module.verify_sources()), 360)
            changed = source / files[0]["path"]
            changed.write_bytes(b"altered\n")
            with self.assertRaises(ValueError):
                module.verify_sources()
            files[0]["sha256"] = module.sha(changed)
            module.save(self.root / "source-manifest.json", pins)
            with self.assertRaisesRegex(ValueError, "first pilot"):
                module.verify_sources()


if __name__ == "__main__":
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log = BASE / "analysis" / f"comparison-runner-tests-{stamp}.log"
    with log.open("w", encoding="utf-8") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ComparisonChecks))
    receipt = {"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "skips": len(result.skipped), "model_calls": 0, "native_starts": 0,
               "kind": "mock_transport_and_integrity_gates_not_live_process_timeout_test",
               "runner_sha256": module.sha(BASE / "run_comparison.py"),
               "test_sha256": module.sha(Path(__file__)), "log": log.relative_to(BASE).as_posix()}
    module.save(BASE / "analysis/comparison-runner-check.json", receipt)
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
