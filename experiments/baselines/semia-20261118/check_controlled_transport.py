"""Offline mocked transport verification. Makes no model requests."""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

BASE = Path(__file__).resolve().parent
sys.path[:0] = [str(BASE / f"source/packages/{p}/src") for p in ("semia-cli", "semia-core")]
cli = importlib.import_module("semia_cli.main")
provider = importlib.import_module("semia_cli.llm_providers")
spec = importlib.util.spec_from_file_location("pilot", BASE / "run_controlled_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
original = provider._run_codex
prompt = "SOURCE DATA\n中文\n"
answer = 'action("a1", "read", "file").\n'
received = []


class Child:
    def __init__(self, cmd, **kwargs):
        self.pid, self.returncode = 12345, 0
        Path(cmd[cmd.index("--output-last-message") + 1]).write_text(answer, encoding="utf-8")
        kwargs["stdout"].write(b'{"type":"turn.completed","usage":{"input_tokens":12,"output_tokens":8}}\n')
        assert 'model_reasoning_effort="high"' in cmd
        assert 'model_provider="openai"' in cmd
        for feature in ("shell_tool", "unified_exec", "apps", "plugins", "hooks"):
            assert cmd[cmd.index(feature) - 1] == "--disable"

    def communicate(self, input, timeout):
        received.append(input)
        assert timeout == 2700


def fake_scan(argv):
    assert provider._run_codex(Path("."), prompt, pilot.MODEL) == answer
    return 0


cwd = Path.cwd()
try:
    with tempfile.TemporaryDirectory(dir=BASE) as td:
        here = Path(td)
        (here / "inputs/001").mkdir(parents=True)
        (here / "inputs/001/SKILL.md").write_bytes(b"test data")
        (here / "source").mkdir()
        manifest = {"cases": [{"case_id": "001", "path": "inputs/001", "files": [
            {"path": "SKILL.md", "sha256": hashlib.sha256(b"test data").hexdigest()}]}]}
        (here / "input-manifest.json").write_text(json.dumps(manifest))
        with patch.object(pilot, "HERE", here), patch.object(sys, "argv", ["pilot", "--run"]), \
             patch.object(pilot.shutil, "which", return_value=sys.executable), \
             patch.object(pilot.subprocess, "Popen", Child), patch.object(cli, "main", fake_scan), \
             patch.dict(os.environ, {}, clear=False):
            assert pilot.main() == 0
            assert received == [prompt.encode("utf-8")]
            summary = json.loads((here / "pilot/001/finished.json").read_text())
            assert summary["calls_with_visible_usage"] == 1
            assert summary["source_unchanged"] and summary["input_unchanged"]
            try:
                pilot.main()
            except FileExistsError:
                pass
            else:
                raise AssertionError("duplicate run allowed")
        os.chdir(cwd)
finally:
    os.chdir(cwd)
    provider._run_codex = original

checks = {"prompt_response_preserved": True, "public_usage_retained": True,
          "execution_tool_features_disabled": True, "duplicate_start_rejected": True,
          "model_calls": 0, "native_starts": 0,
          "kind": "mock_transport_only_not_semantic_test",
          "initial_harness_failure": "AttributeError from package main function shadowing module; fixed using importlib.import_module before any native start"}
(BASE / "transport-offline-check.json").write_text(json.dumps(checks, indent=2) + "\n")
print(json.dumps(checks))
