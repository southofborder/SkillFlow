"""Three focused offline guards; fictional process artifacts, never a target."""
from copy import deepcopy
from pathlib import Path

import pytest

from tools.doe.real_comparison import current_harness_calibration as current
from tools.doe.real_comparison import cli_adapter_v3 as cli
from tools.doe.real_comparison import execution as native
from tools.doe.real_comparison.protocol import utc_now, write_json


@pytest.fixture
def callback(tmp_path, monkeypatch):
    run = tmp_path / "new-calibration"
    write_json(run / "workflows/gh-fix-ci/state.json", {"started_at": utc_now()})
    write_json(run / "current-harness-manifest.json", {"fictional": True})
    raw = tmp_path / "fictional-raw.jsonl"
    raw.write_text("Fictional receipt, never a model call", encoding="utf-8")
    manifest = {"executable": "never-executed", "base_instructions_sha256": "new-base",
                "developer_segment_sha256": [["new-common-developer"]]}
    monkeypatch.setattr(current, "verify_run", lambda *a: deepcopy(manifest))
    monkeypatch.setattr(native, "reference_tokens", lambda p: 10)
    def forbidden(*a, **k):
        pytest.fail("A focused offline check attempted a real process")
    monkeypatch.setattr(cli.subprocess, "Popen", forbidden)
    def prepare(executable, prompt, output, cwd):
        return {"command": ["never-executed"], "output_dir": str(output), "stdin_file": str(prompt),
            "base_instructions_sha256": cli.PINNED_BASE_INSTRUCTIONS_SHA256,
            "developer_segment_sha256": [list(p) for p in cli.PINNED_DEVELOPER_SEGMENTS]}
    calls = []
    def execute(prepared, **kwargs):
        assert prepared["base_instructions_sha256"] == "new-base"
        assert prepared["developer_segment_sha256"] == [["new-common-developer"]]
        calls.append(prepared)
        output = Path(prepared["output_dir"])
        write_json(output / "process-start.json", {"actual_cli_process_started": True})
        process = {"status": "process_exited", "returncode": 0}
        write_json(output / "process-result.json", process)
        (output / "stdout.jsonl").write_text("Fictional stdout", encoding="utf-8")
        return process
    counters = {key: 10 for key in cli.TOKEN_FIELDS}
    receipt = {"cli_session_id": "fictional-session", "protocol_status": "conformant", "violations": [],
        "configuration_verified": True, "provider_verified": True, "usage_verified": True, "completed": True,
        "usage": {"by_response_id": {"fictional-response": counters}, "totals": counters}}
    monkeypatch.setattr(cli, "prepare_launch", prepare)
    monkeypatch.setattr(cli, "execute_launch", execute)
    monkeypatch.setattr(cli, "session_from_stdout", lambda p: "fictional-session")
    monkeypatch.setattr(cli, "inspect_receipt", lambda *a, **k: ("Complete visible final answer", deepcopy(receipt)))
    import tools.doe.direct_baseline as baseline
    monkeypatch.setattr(baseline, "find_receipt", lambda *a: raw)
    return run, calls, receipt


def test_explicit_manifest_overrides_only_prepared_hashes_and_last_response_is_retained(callback):
    run, calls, receipt = callback
    old_base, old_developers = cli.PINNED_BASE_INSTRUCTIONS_SHA256, cli.PINNED_DEVELOPER_SEGMENTS
    receipt["usage"]["by_response_id"]["fictional-response"]["total_tokens"] = 8000001
    receipt["usage"]["totals"]["total_tokens"] = 8000001
    client = current.CurrentHarnessClient(run, "gh-fix-ci")
    core = 'Full production prompt.\r\nPreserved user quotation: "原文".\n'
    assert client.complete(core) == "Complete visible final answer"
    assert Path(calls[0]["stdin_file"]).read_bytes() == native.ENVELOPE.replace("{core}", core).encode("utf-8")
    assert cli.PINNED_BASE_INSTRUCTIONS_SHA256 == old_base and cli.PINNED_DEVELOPER_SEGMENTS == old_developers
    with pytest.raises(native.ExecutionStop, match="eight-million"):
        client.complete("Forbidden next request")
    assert len(calls) == 1


@pytest.mark.parametrize("failure", ("harness_drift", "tools", "unknown_usage"))
def test_bad_actual_receipt_retains_failure_and_blocks_all_next_calls(callback, failure):
    run, calls, receipt = callback
    receipt["protocol_status"] = "violated"
    receipt["violations"] = ["Synthetic " + failure]
    if failure == "unknown_usage":
        receipt["usage_verified"] = False
    client = current.CurrentHarnessClient(run, "gh-fix-ci")
    with pytest.raises(native.ExecutionStop, match="receipt failed"):
        client.complete("Complete first prompt")
    assert (run / "dispatch-stop.json").exists()
    with pytest.raises(native.ExecutionStop, match="subsequent"):
        current.CurrentHarnessClient(run, "netlify-deploy").complete("Never dispatched")
    assert len(calls) == 1


def test_shared_stop_prevents_fresh_case_or_request_without_touching_history(callback):
    run, calls, _ = callback
    old = run.parent / "paused-history/dispatcher.lock"
    old.parent.mkdir()
    old.write_bytes(b"Retained interrupted lock")
    current._stop(run, "Another case stopped this phase")
    with pytest.raises(native.ExecutionStop, match="stopped phases"):
        current.run_case(run, "transcribe")
    assert not (run / "workflows/transcribe").exists() and calls == []
    assert old.read_bytes() == b"Retained interrupted lock"


def test_unknown_process_start_keeps_unknown_cost_until_proven_prelaunch(callback):
    run = callback[0]
    directory = run / "workflows/gh-fix-ci/requests/q001"
    write_json(directory / "request.json", {"fictional": True})
    assert current.usage(run)["totals"]["total_tokens"] == 0
    write_json(directory / "dispatch.json", {"attempted_at": utc_now()})
    assert current.usage(run)["totals"]["total_tokens"] is None
    assert current.usage(run)["missing_requests"] == [directory.as_posix()]
    write_json(directory / "cli/process-result.json", {"actual_cli_process_started": False, "status": "launch_failed"})
    assert current.usage(run)["totals"]["total_tokens"] == 0
