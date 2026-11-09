"""Focused fictional workflows; no process or model is allowed in these tests."""
from copy import deepcopy
from pathlib import Path

import pytest

from tools.doe.real_comparison import exploratory_cli as runner
from tools.doe.real_comparison import controlled_cli as cli
from tools.doe.real_comparison import cli_adapter_v3 as v3
from tools.doe.real_comparison import execution as native
from tools.doe.real_comparison.protocol import utc_now, write_json


@pytest.fixture
def fictional(tmp_path, monkeypatch):
    run = tmp_path / "exploratory"
    run.mkdir()
    rows = [{"workflow_id": "real-001_" + method + "_r" + str(repeat), "case_id": "real-001",
             "method": method, "repeat": repeat, "kind": "main", "source_sha256": "frozen-source"}
            for repeat in (1, 2, 3) for method in ("skillflow", "audit", "chain")]
    reviews = [{**item, "workflow_id": item["workflow_id"] + "_review", "kind": "review", "original_workflow_id": item["workflow_id"]}
               for item in rows if item["method"] != "skillflow" and item["repeat"] == 1]
    write_json(run / "schedule.json", {"seed": 20261020, "main": rows, "reviews": reviews})
    write_json(run / "plan.json", {"created_at": utc_now(), "parallel_workers": 6})
    manifest = {"executable": "never-executed", "base_instructions_sha256": "exact-base", "developer_segment_sha256": [["exact-developer"]]}
    monkeypatch.setattr(runner, "verify_run", lambda *a, **k: deepcopy(manifest))
    monkeypatch.setattr(runner, "render_direct", lambda *args: 'Complete prompt with original quotation "原文" and {braces}.\r\n')
    def forbidden(*a, **k):
        pytest.fail("An offline exploratory test attempted a real process")
    monkeypatch.setattr(cli.subprocess, "Popen", forbidden)
    monkeypatch.setattr(native, "reference_tokens", lambda value: 10)
    return run, rows, reviews


@pytest.fixture
def callback(fictional, tmp_path, monkeypatch):
    run, rows, reviews = fictional
    item = next(i for i in rows if i["method"] == "audit")
    write_json(run / "workflows" / item["workflow_id"] / "state.json", {"started_at": utc_now()})
    raw = tmp_path / "fictional-receipt.jsonl"
    raw.write_text("Fictional metadata only, never an actual target", encoding="utf-8")
    calls = []
    def prepare(executable, prompt, output, cwd, **pins):
        assert pins == {"base_instructions_sha256": "exact-base", "developer_segment_sha256": [["exact-developer"]]}
        return {"command": ["never-executed"], "output_dir": str(output), "stdin_file": str(prompt)}
    def execute(prepared, **kwargs):
        calls.append(prepared)
        output = Path(prepared["output_dir"])
        write_json(output / "process-start.json", {"actual_cli_process_started": True})
        process = {"status": "process_exited", "returncode": 0, "actual_cli_process_started": True}
        write_json(output / "process-result.json", process)
        (output / "stdout.jsonl").write_text("Fictional stdout", encoding="utf-8")
        (output / "last-message.txt").write_text("Visible answer", encoding="utf-8")
        return process
    tokens = {key: 10 for key in v3.TOKEN_FIELDS}
    receipt = {"cli_session_id": "fictional-session", "protocol_status": "conformant", "violations": [], "tools": [],
        "configuration_verified": True, "provider_verified": True, "usage_verified": True, "completed": True,
        "usage": {"by_response_id": {"fictional-response": tokens}, "totals": tokens}, "diagnostics": []}
    monkeypatch.setattr(cli, "prepare_launch", prepare)
    monkeypatch.setattr(cli, "execute_launch", execute)
    monkeypatch.setattr(cli, "inspect_receipt", lambda *a, **k: ("Visible answer", deepcopy(receipt)))
    monkeypatch.setattr(v3, "session_from_stdout", lambda p: "fictional-session")
    import tools.doe.direct_baseline as baseline
    monkeypatch.setattr(baseline, "find_receipt", lambda *args: raw)
    return run, item, calls, receipt


def test_accepted_last_response_can_cross_budget_without_a_second_launch(callback):
    run, item, calls, receipt = callback
    receipt["usage"]["by_response_id"]["fictional-response"]["total_tokens"] = 8000001
    client = runner.ExploratoryClient(run, item)
    core = runner.render_direct(None)
    assert client.complete(core) == "Visible answer"
    assert Path(calls[0]["stdin_file"]).read_bytes() == native.ENVELOPE.replace("{core}", core).encode("utf-8")
    with pytest.raises(native.ExecutionStop, match="eight-million"):
        client.complete(core)
    assert len(calls) == 1 and not (run / "dispatch-stop.json").exists()


def test_unknown_usage_is_retained_and_blocks_only_its_workflow(callback):
    run, item, calls, receipt = callback
    receipt.update(protocol_status="violated", usage_verified=False,
        violations=["Unknown or inconsistent per-response usage forbids further dispatch"])
    client = runner.ExploratoryClient(run, item)
    with pytest.raises(native.ExecutionStop, match="not accepted"):
        client.complete(runner.render_direct(None))
    assert not (run / "dispatch-stop.json").exists()
    assert runner.usage(run, item["workflow_id"])["totals"]["total_tokens"] is None
    with pytest.raises(native.ExecutionStop, match="Unknown per-response"):
        client.complete(runner.render_direct(None))
    assert len(calls) == 1
    assert (run / "workflows" / item["workflow_id"] / "requests/q001/answer.txt").read_text() == "Visible answer"


@pytest.mark.parametrize("violation", ["Additional system message observed", "Multiple final-answer messages were observed; none was selected as the answer.",
    "Observed reasoning effort differs from the registered expected effort.", "A CLI session or response identity was reused"])
def test_every_actual_invariant_violation_stops_globally(callback, violation):
    run, item, calls, receipt = callback
    receipt.update(protocol_status="violated", violations=[violation])
    with pytest.raises(native.ExecutionStop, match="not accepted"):
        runner.ExploratoryClient(run, item).complete(runner.render_direct(None))
    assert (run / "dispatch-stop.json").exists() and len(calls) == 1


def test_native_failure_is_per_workflow_and_each_repeat_starts_from_source(fictional, monkeypatch):
    run, rows, _ = fictional
    observed = []
    def native_call(source, attempt, client, **kwargs):
        observed.append((source, attempt, client.workflow_id))
        return {"status": "failed", "stage": "graph", "graph": {"reason": "Fictional structural failure"}}
    monkeypatch.setattr(native, "_native_pipeline", native_call)
    for item in (i for i in rows if i["method"] == "skillflow"):
        result = runner.run_workflow(run, item["workflow_id"])
        assert result["status"] == "failed" and result["graph_reused"] is False
    assert len(observed) == 3 and len({a for _, a, _ in observed}) == 3
    assert all(s == run / "cases/real-001/source" for s, _, _ in observed)
    assert not (run / "dispatch-stop.json").exists()
    result = runner.summary(run)
    assert result["planned_denominator"] == 264 and result["closed_results"] == 3


def test_missing_first_answer_is_not_reviewed_using_another_repeat(fictional):
    run, rows, reviews = fictional
    review = reviews[0]
    write_json(run / "workflows" / review["original_workflow_id"] / "result.json", {"status": "failed"})
    second = next(i for i in rows if i["method"] == review["method"] and i["repeat"] == 2)
    write_json(run / "workflows" / second["workflow_id"] / "result.json", {"status": "complete"})
    answer = run / "workflows" / second["workflow_id"] / "answer.txt"
    answer.write_text("Another repetition must never replace R1", encoding="utf-8")
    result = runner.run_workflow(run, review["workflow_id"])
    assert result["status"] == "not_reviewable" and result["attempts"] == 0
    assert runner.requests(run) == []


def test_global_stop_terminalizes_every_remaining_identity_without_calls(fictional):
    run, rows, reviews = fictional
    runner._stop(run, "Fictional exact-harness mismatch")
    result = runner.terminalize_after_stop(run)
    assert result["closed_results"] == len(rows) + len(reviews)
    assert sum(i["status"] == "not_reviewable" for i in result["outcomes"]) == 2
    assert all(runner.read(run / "workflows" / i["workflow_id"] / "result.json")["attempts"] == 0 for i in rows + reviews)
    assert runner.requests(run) == []


def test_duplicate_usage_is_deduplicated_but_conflicting_counters_are_unknown(tmp_path):
    run = tmp_path / "run"
    counters = {key: 10 for key in v3.TOKEN_FIELDS}
    for index in (1, 2):
        request = run / "workflows" / ("w" + str(index)) / "requests/q001"
        write_json(request / "cli/process-start.json", {"actual_cli_process_started": True})
        write_json(request / "receipt.json", {"usage_verified": True, "usage": {"by_response_id": {"same": counters}}})
    assert runner.usage(run)["totals"]["total_tokens"] == 10
    changed = dict(counters, total_tokens=11)
    write_json(run / "workflows/w2/requests/q001/receipt.json", {"usage_verified": True, "usage": {"by_response_id": {"same": changed}}})
    assert runner.usage(run)["conflicting_response_ids"] == ["same"]
    assert runner.usage(run)["totals"]["total_tokens"] is None
