"""Offline lineage accounting: originals once, explicitly new requests separately."""

from skillflow.common.paths import project_root, resolve_material_path
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = project_root() / "tools/propagation/annotation/summarize_rerun_costs.py"


@pytest.fixture(scope="module")
def tool():
    spec = importlib.util.spec_from_file_location("test_lineage_costs", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save_call(tool, root, relative, *, failed=False, attempts=1, usage=True, observed=True):
    prompt, response = "same prompt across runs", {"saved": "same response"}
    call = {"status": "error" if failed else "complete", "prompt": prompt,
            "prompt_sha256": tool.canonical_sha256(prompt)}
    trace = {"status": call["status"], "prompt": prompt,
             "http_attempts_observed": observed,
             "returned_model": "actual-model" if not failed else None,
             "usage": {"prompt_tokens": 999999, "completion_tokens": 999999, "total_tokens": 999999},
             "http_attempts": [{"status": "error" if failed else "complete", "http_status": None if failed else 200,
                 "returned_model": None if failed else "actual-model",
                 "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12} if usage and not failed else None}
                for _ in range(attempts)]}
    if not failed:
        call.update(response=response, response_sha256=tool.canonical_sha256(response))
        trace["response"] = response
    trace["record_sha256"] = tool.canonical_sha256(trace)
    path = root / relative
    tool.write_json(path, call)
    tool.write_json(path.with_name("transport.json"), [trace])
    path.with_name("prompt.txt").write_text(prompt, encoding="utf-8")
    return path


@pytest.fixture
def lineage(tool, tmp_path, monkeypatch):
    parent, child = tmp_path / "parent", tmp_path / "child"
    parent.mkdir()
    manifest = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": tool._prepare.PARENT_IDENTITY,
                "config": {"model": "requested-model"}, "cases": []}
    outcome = {"schema_version": 10, "profile_schema_version": "security-profile-v10", "identity": tool._prepare.PARENT_IDENTITY,
               "summary": {"cases": 30}, "cases": {}}
    for number in range(1, 31):
        identifier = f"{number:03}"
        manifest["cases"].append({"case_id": identifier, "run_dir": "cases/" + identifier, "package_path": "frozen/" + identifier})
        row = {"feedback": {"status": "audit_error" if identifier in tool._prepare.EXPECTED_RERUN_CASES else "audit_passed"},
               "annotation": {"status": "complete"}, "selection": {"fixture": True}, "scheduler_error": None}
        outcome["cases"][identifier] = row
        tool.write_json(parent / "cases" / identifier / "result.json", row)
    tool.write_json(parent / "manifest.json", manifest)
    tool.write_json(parent / "experiment-result.json", outcome)
    save_call(tool, parent, "cases/001/feedback/calls/r000/extraction/a001/call.json")
    save_call(tool, parent, "cases/008/feedback/calls/r000/audit/a001/call.json", failed=True, attempts=3)
    save_call(tool, parent, "cases/008/feedback/calls/r000/audit/a002/call.json")
    rerun, reuse = tool._prepare.classify_cases(manifest, outcome)
    monkeypatch.setattr(tool._prepare, "validate_parent", lambda _: (manifest, outcome, rerun, reuse))
    provenance = tool._prepare.prepare(parent, child)
    finished = deepcopy(outcome)
    for identifier in rerun:
        finished["cases"][identifier]["feedback"]["status"] = "audit_passed"
        tool.write_json(child / "cases" / identifier / "result.json", finished["cases"][identifier])
    save_call(tool, child, "cases/008/feedback/calls/r000/extraction/a001/call.json", usage=False)
    save_call(tool, child, "cases/008/feedback/calls/r000/audit/a001/call.json", failed=True)
    save_call(tool, child, "cases/008/feedback/calls/r000/audit/a002/call.json")
    tool.write_json(child / "experiment-result.json", finished)
    return SimpleNamespace(parent=parent, child=child, provenance=provenance, finished=finished)


def test_counts_parent_and_new_calls_without_reused_calls_or_usage_double_count(tool, lineage):
    result = tool.summarize(lineage.child)
    assert result["parent"]["execution_calls"] == 3
    assert result["child_new"]["execution_calls"] == 3
    assert result["lineage_unique"]["execution_calls"] == 6
    assert result["reused_execution_calls_excluded_from_child"] == 1
    # Two accepted audit executions in each run are one logical audit per run.
    assert result["lineage_unique"]["logical_by_task"] == {"extraction": 2, "audit": 2, "annotation": 0}
    assert result["lineage_unique"]["http_attempts"] == 8
    assert result["lineage_unique"]["usage"]["input_tokens"] == {
        "known_sum": 30, "known_attempts": 3, "unknown_attempts": 5, "unobserved_calls": 0, "complete": False}
    assert result["lineage_unique"]["returned_models_by_http_attempt"] == {"actual-model": 4}
    assert result["lineage_unique"]["requested_models_by_execution_call"] == {"requested-model": 6}
    assert len({row["origin_id"] for row in result["calls"]}) == 6
    # Equal response bytes across parent/child never turn a new request into reuse.
    child_complete = next(row for row in result["calls"] if row["origin_run"] == str(lineage.child) and row["status"] == "complete")
    assert result["calls"][0]["response_sha256"] == child_complete["response_sha256"]


@pytest.mark.parametrize("change", ["content", "missing", "extra"])
def test_reused_call_change_missing_or_extra_is_rejected(tool, lineage, change):
    path = lineage.child / "cases/001/feedback/calls/r000/extraction/a001/prompt.txt"
    if change == "content":
        path.write_text("changed")
    elif change == "missing":
        path.unlink()
    else:
        save_call(tool, lineage.child, "cases/001/feedback/calls/r001/extraction/a001/call.json")
    with pytest.raises(ValueError, match="Reused call artifacts"):
        tool.summarize(lineage.child)


@pytest.mark.parametrize("change", ["parent", "provenance"])
def test_parent_inventory_or_provenance_change_is_rejected(tool, lineage, change):
    if change == "parent":
        (lineage.parent / "added.txt").write_text("not in seal")
    else:
        path = lineage.child / "rerun-provenance.json"
        value = tool.read_json(path)
        value["rerun_cases"] = []
        tool.write_json(path, value)
    with pytest.raises(ValueError, match="inventory changed|provenance seal"):
        tool.summarize(lineage.child)


@pytest.mark.parametrize("condition", ["missing_final", "running_case"])
def test_pending_never_reads_calls_or_writes_final_output(tool, lineage, monkeypatch, condition):
    if condition == "missing_final":
        (lineage.child / "experiment-result.json").unlink()
    else:
        value = deepcopy(lineage.finished)
        value["cases"]["030"]["feedback"]["status"] = "interrupted"
        tool.write_json(lineage.child / "experiment-result.json", value)
        tool.write_json(lineage.child / "cases/030/result.json", value["cases"]["030"])
    def forbidden(*args, **kwargs):
        pytest.fail("An active batch must not read call or transport records")
    monkeypatch.setattr(tool, "verify_lineage", forbidden)
    assert tool.main(["--run-dir", str(lineage.child)]) == 2
    assert not (lineage.child / "lineage-summary.json").exists()
    assert not (lineage.child / "lineage-report.md").exists()


def test_unobserved_http_and_top_level_only_usage_remain_unknown(tool, lineage):
    save_call(tool, lineage.child, "cases/008/feedback/calls/r000/extraction/a001/call.json", usage=False, attempts=0, observed=False)
    result = tool.summarize(lineage.child)
    new = result["child_new"]
    assert new["http_attempts"] is None and new["http_attempt_records"] == 2
    assert len(new["unobserved_http_call_origins"]) == 1
    assert new["usage"]["input_tokens"]["known_sum"] == 10
    assert new["usage"]["input_tokens"]["unobserved_calls"] == 1


def test_orphan_transport_is_not_silently_counted_as_zero(tool, lineage):
    path = lineage.child / "cases/008/feedback/calls/r000/extraction/a001/call.json"
    path.unlink()
    with pytest.raises(ValueError, match="Orphan transport"):
        tool.summarize(lineage.child)


def test_report_is_separate_and_parent_is_not_modified(tool, lineage):
    before = tool._prepare.inventory(lineage.parent)
    (lineage.child / "report.md").write_text("existing driver report", encoding="utf-8")
    assert tool.main(["--run-dir", str(lineage.child)]) == 0
    assert (lineage.child / "report.md").read_text(encoding="utf-8") == "existing driver report"
    result = tool.read_json(lineage.child / "lineage-summary.json")
    unsigned = {key: value for key, value in result.items() if key != "summary_sha256"}
    assert result["summary_sha256"] == tool.canonical_sha256(unsigned)
    text = (lineage.child / "lineage-report.md").read_text(encoding="utf-8")
    assert "未知" in text and "不是服务商账单" in text
    assert tool._prepare.inventory(lineage.parent) == before


def save_running_call(tool, root, *, with_transport=True):
    """RecordingClient + streaming transport checkpoint shape after interruption."""
    path = root / "cases/030/feedback/calls/r001/audit/a002/call.json"
    prompt = "完整核对输入，尚未保存最终响应"
    call = {"status": "running", "started_at": "2026-09-18T13:06:02.703293+00:00",
            "prompt": prompt, "prompt_sha256": tool.canonical_sha256(prompt)}
    tool.write_json(path, call)
    path.with_name("prompt.txt").write_text(prompt, encoding="utf-8")
    if with_transport:
        wire = 'data: {"model":"deepseek-flash","choices":[{"delta":{"reasoning_content":"partial"}}]}\n\n'
        trace = {"generation": 1, "started_at": "2026-09-18T13:06:02.717288+00:00",
            "status": "running", "prompt": prompt, "returned_model": None, "usage": None, "request_id": None,
            "http_attempts": [{"status": "running", "http_status": 200, "request_id": None,
                "returned_model": "deepseek-flash", "usage": None, "raw_response": None,
                "stream": {"request_parameters": {"model": "deepseek-v4-flash", "stream": True},
                    "request_body_sha256": sha256(b"request").hexdigest(), "raw_sse": wire,
                    "wire_sha256": sha256(wire.encode()).hexdigest(), "received_bytes": len(wire.encode()),
                    "headers_received_at": "2026-09-18T13:06:03.144587+00:00",
                    "first_byte_at": "2026-09-18T13:06:03.156073+00:00",
                    "first_event_at": "2026-09-18T13:06:03.156073+00:00", "first_content_at": None,
                    "last_event_at": "2026-09-18T13:08:00.414936+00:00", "event_count": 1,
                    "done_received": False, "finish_reason": None, "partial_content": "",
                    "outcome": "pending", "response_content_type": "text/event-stream; charset=utf-8"}}]}
        trace["record_sha256"] = tool.canonical_sha256(trace)
        tool.write_json(path.with_name("transport.json"), [trace])
    return path


def test_terminal_experiment_counts_running_checkpoint_once_without_resend_or_mutation(tool, lineage):
    path = save_running_call(tool, lineage.child)
    save_call(tool, lineage.child, "cases/030/feedback/calls/r001/audit/a001/call.json", failed=True)
    # Like the real final experiment, the stage is terminal although one saved
    # execution remains running: recovery reports the unknown outcome as error.
    outcome = deepcopy(lineage.finished)
    outcome["cases"]["030"]["feedback"]["status"] = "audit_error"
    tool.write_json(lineage.child / "cases/030/result.json", outcome["cases"]["030"])
    tool.write_json(lineage.child / "experiment-result.json", outcome)
    before = tool._prepare.inventory(lineage.child)
    result = tool.summarize(lineage.child)
    new = result["child_new"]
    assert new["execution_calls"] == 5
    assert new["logical_by_task"] == {"extraction": 1, "audit": 2, "annotation": 0}
    assert new["http_attempts"] == 5
    assert new["nonterminal_saved_calls"] == 1
    assert new["execution_statuses"]["running"] == 1
    running = [row for row in result["calls"] if row["status"] == "running"]
    assert len(running) == 1 and running[0]["transport_status"] == "running"
    assert running[0]["response_sha256"] is None
    assert running[0]["attempts"] == [{"attempt": 1, "status": "running", "http_status": 200,
                                       "returned_model": "deepseek-flash", "usage": None}]
    assert new["returned_models_by_http_attempt"]["deepseek-flash"] == 1
    assert new["usage"]["input_tokens"]["known_sum"] == 10
    assert new["usage"]["input_tokens"]["unknown_attempts"] == 4
    assert new["usage"]["input_tokens"]["complete"] is False
    assert tool._prepare.inventory(lineage.child) == before
    assert tool.read_json(path)["status"] == "running"
    # Counting a completed child's checkpoint does not loosen parent preparation.
    with pytest.raises(ValueError, match="parent request is not terminal"):
        tool._prepare.call_ledger(lineage.child, before)


def test_running_call_without_transport_does_not_invent_zero_http_or_usage(tool, lineage):
    path = save_running_call(tool, lineage.child, with_transport=False)
    result = tool.summarize(lineage.child)
    running = next(row for row in result["calls"] if row["status"] == "running")
    assert running["transport_sha256"] is None
    assert running["http_attempts"] is None and running["attempts"] == []
    assert running["returned_model_at_call"] is None and running["usage_at_call_not_summed"] is None
    assert result["child_new"]["http_attempts"] is None
    assert result["child_new"]["usage"]["input_tokens"]["unobserved_calls"] == 1
    metrics = tool.metrics([running])
    assert metrics["execution_calls"] == 1 and metrics["logical_calls"] == 1
    assert metrics["usage"]["input_tokens"]["known_sum"] is None
    assert tool.read_json(path)["status"] == "running"


@pytest.mark.parametrize("change", ["prompt_digest", "transport_digest", "transport_identity", "orphan_transport"])
def test_running_request_binding_and_transport_tampering_are_rejected(tool, lineage, change):
    path = save_running_call(tool, lineage.child)
    if change == "prompt_digest":
        call = tool.read_json(path)
        call["prompt"] = "tampered"
        tool.write_json(path, call)
        expected = "prompt digest mismatch"
    elif change == "orphan_transport":
        path.unlink()
        expected = "Orphan transport"
    else:
        transport = path.with_name("transport.json")
        trace = tool.read_json(transport)[0]
        trace["prompt"] = "different request"
        if change == "transport_identity":
            trace.pop("record_sha256")
            trace["record_sha256"] = tool.canonical_sha256(trace)
        tool.write_json(transport, [trace])
        expected = "identity differ" if change == "transport_identity" else "digest mismatch"
    with pytest.raises(ValueError, match=expected):
        tool.summarize(lineage.child)
