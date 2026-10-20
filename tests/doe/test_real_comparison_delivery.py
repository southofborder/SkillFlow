import json
from pathlib import Path

import pytest

from tools.doe.real_comparison.artifacts import seal_candidate, verify_candidate
from tools.doe.real_comparison.assessment import validate_reference_evidence
from tools.doe.real_comparison.inputs import render_direct, render_review
from tools.doe.real_comparison.protocol import write_json, sha256
from tools.doe.real_comparison.reporting import report, corpus_manifest
from tools.doe.real_comparison.review import write_timed_packet
from tools.doe.real_comparison.results import aggregate_scores, freeze_outputs


def test_original_multilingual_source_and_literal_markers_are_not_resubstituted(tmp_path):
    case = tmp_path / "cases/C1"
    case.mkdir(parents=True)
    source = "原始引用 {user_request} {original_answer} __ANSWER__\n"
    (case / "source-bundle.txt").write_text(source, encoding="utf8")
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    (prompts / "audit.txt").write_text("TASK:{user_request}\nSOURCE:{source_bundle}", encoding="utf8")
    (prompts / "review.txt").write_text("{original_task}\nANSWER:{original_answer}", encoding="utf8")
    (tmp_path / "references").mkdir()
    (tmp_path / "references/C1.json").write_text('{"gold_secret":"DO_NOT_LEAK"}', encoding="utf8")
    answer = "Exact first answer {source_bundle} 原样"
    main = render_direct(tmp_path, "C1", "audit")
    reviewed = render_review(tmp_path, "C1", "audit", answer)
    assert source in main and source in reviewed and answer in reviewed
    assert "DO_NOT_LEAK" not in main + reviewed
    assert "No independent user task" in main


def test_timed_review_escapes_source_scripts_and_preserves_marker_literals(tmp_path):
    path = tmp_path / "review.html"
    assignment = {"assignment_id": "A1", "reviewer_id": "R1", "method": "audit", "repeat": 1}
    write_timed_packet(path, assignment, '<script>alert("bad")</script> __ANSWER__ 原文', "__SOURCE__")
    text = path.read_text(encoding="utf8")
    assert '<script>alert("bad")' not in text
    assert "&lt;script&gt;" in text and "__ANSWER__ 原文" in text
    assert '"method"' not in text and '"repeat"' not in text
    assert "visibilitychange" in text and "1800" in text
    assert "pending_independent_adjudication" in text


def test_native_candidate_has_byte_seal_and_unrewritten_reading_view(tmp_path):
    native = tmp_path / "workflows/W1/attempts/001/analysis"
    native.mkdir(parents=True)
    (native / "report.md").write_text("Native result 原文\n", encoding="utf8")
    write_json(native / "doe-result.json", {"findings": [], "status": "partial"})
    (native / "calls").mkdir()
    (native / "calls/prompt.txt").write_text("Raw transport retained", encoding="utf8")
    result = seal_candidate(tmp_path, "W1", artifact_root="workflows/W1/attempts/001")
    assert verify_candidate(tmp_path, "W1", result)
    view = (tmp_path / "workflows/W1/candidate-view.txt").read_text(encoding="utf8")
    assert "Native result 原文\n" in view and '"status": "partial"' in view
    assert "Raw transport retained" not in view
    (native / "calls/prompt.txt").write_text("Changed", encoding="utf8")
    with pytest.raises(ValueError, match="artifact changed"):
        verify_candidate(tmp_path, "W1", result)


def test_reference_confirmation_rejects_changed_quotes_and_pending_coverage(tmp_path):
    source = tmp_path / "cases/C1/source"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_bytes("用途\r\nKeep values.\r\n".encode("utf8"))
    evidence = [{"path": "SKILL.md", "start_line": 1, "end_line": 2, "quote": "用途\nKeep values."}]
    ref = {"case_id": "C1", "user_request": None, "purpose_basis": "skill_declared_purpose_only",
           "coverage_state": "complete_for_human_verification",
           "declared_purpose": [{"id": "P1", "evidence": evidence}], "required_behavior": [],
           "receiving_points": [{"id": "B1", "evidence": evidence}], "necessary_sensitive_uses": [],
           "supported_excesses": [], "unknowns": [], "preservation_checks": [],
           "mandatory_checks": [{"id": "M1", "evidence": evidence}]}
    validate_reference_evidence(tmp_path, ref)
    ref["coverage_state"] = "source_facts_only_pending_semantic_reference"
    with pytest.raises(ValueError, match="coverage"):
        validate_reference_evidence(tmp_path, ref)
    ref["coverage_state"] = "complete_for_human_verification"
    evidence[0]["quote"] = "Translated purpose"
    with pytest.raises(ValueError, match="quotation differs"):
        validate_reference_evidence(tmp_path, ref)


def test_first_delivery_reports_actual_acquisition_progress_not_comparative_results(tmp_path):
    corpus, run = tmp_path / "corpus", tmp_path / "run"
    write_json(corpus / "roster/entries.json", [{"identity": "a/s"}, {"identity": "b/s"}])
    write_json(corpus / "acquisition-index.json", {"items": [{"status": "integrity_or_format_failure"}]})
    value = report(run, corpus)
    assert value["acquisition"]["attempted"] == 1
    assert value["acquisition"]["not_yet_attempted"] == 1
    assert value["formal_requests_created"] == 0
    assert value["semantic_comparison"] == "not_yet_measured"


def test_missing_workflows_remain_in_denominator_and_prevent_scoring_freeze(tmp_path):
    from tools.doe.real_comparison.execution import prepare_schedule
    cases = [{"case_id": f"C{i:02d}", "source_sha256": str(i), "source_cluster": str(i // 3)} for i in range(24)]
    prepare_schedule(tmp_path, cases)
    write_json(tmp_path / "selection.json", {"selected": cases})
    value = aggregate_scores(tmp_path)
    assert value["planned_results"] == 264 and value["complete"] is False
    assert sum(counts.get("not_generated", 0) for counts in value["groups"].values()) == 264
    assert value["primary_comparisons"] == []
    with pytest.raises(ValueError, match="All planned outputs"):
        freeze_outputs(tmp_path)
    schedule = json.loads((tmp_path / "schedule.json").read_text(encoding="utf8"))
    first = schedule["main"][0]["workflow_id"]
    write_json(tmp_path / "workflows" / first / "result.json", {"status": "failed", "answer_sha256": None})
    value = aggregate_scores(tmp_path)
    rows = json.loads((tmp_path / "scores.json").read_text(encoding="utf8"))["rows"]
    row = next(r for r in rows if r["workflow_id"] == first)
    assert row["technical_failure"] and not row["human_verification_complete"]
    assert value["complete"] is False and value["primary_comparisons"] == []


def test_proposed_cli_stdin_is_exact_and_not_a_formal_dispatch(tmp_path, monkeypatch):
    from tools.doe.real_comparison.stdin_transport import prepare_launch, execute_calibration_probe
    executable, prompt = tmp_path / "codex.exe", tmp_path / "prompt.txt"
    executable.write_bytes(b"inert test executable")
    raw = 'Original source 原文\r\nrun_id = result.get("run_id")\n{source_bundle}'.encode("utf8")
    prompt.write_bytes(raw)
    prepared = prepare_launch(executable, prompt, tmp_path / "probe")
    assert prepared["formal_approved"] is False
    assert 'model_reasoning_effort="ultra"' in prepared["command"]
    assert "resume" not in prepared["command"] and "fork" not in prepared["command"]
    observed = {}
    class InertProcess:
        returncode = 0
        def __init__(self, command, **kwargs):
            observed.update(command=command, cwd=kwargs["cwd"])
        def communicate(self, input=None, timeout=None):
            observed.update(stdin=input, timeout=timeout)
    monkeypatch.setattr("tools.doe.real_comparison.stdin_transport.subprocess.Popen", InertProcess)
    cwd = tmp_path / "empty"
    cwd.mkdir()
    result = execute_calibration_probe(prepared, empty_workdir=cwd)
    assert observed["stdin"] == raw and observed["timeout"] == 2700
    assert result["formal_requests"] == 0 and result["per_response_usage"] is None
    assert result["receipt_configuration"] == "not_yet_verified"


def test_combined_original_plus_review_usage_deduplicates_and_preserves_unknowns():
    from tools.doe.real_comparison.metrics import combine_usage
    row = {"input_tokens": 10, "cached_input_tokens": 0, "cache_write_input_tokens": 0,
           "output_tokens": 5, "reasoning_output_tokens": 2, "total_tokens": 15}
    known = {"by_response_id": {"r1": row}, "missing_requests": []}
    assert combine_usage([known, known])["totals"]["total_tokens"] == 15
    missing = {"by_response_id": {}, "missing_requests": ["failed_original"]}
    value = combine_usage([known, missing])
    assert value["totals"]["total_tokens"] is None and value["response_count"] == 1
    bad = {"by_response_id": {"r1": {**row, "total_tokens": 20}}}
    assert combine_usage([known, bad])["conflicting_response_ids"] == ["r1"]


def test_corpus_manifest_keeps_missing_roster_identity_and_original_version(tmp_path):
    roster = [{"rank": i, "identity": f"owner/skill{i}", "ownerHandle": "owner", "slug": f"skill{i}",
               "downloads": 100 - i, "version_pin": "1.0.0", "observed_page": 1, "observed_position": i} for i in (1, 2)]
    write_json(tmp_path / "roster/entries.json", roster)
    write_json(tmp_path / "roster/manifest.json", {"entries_sha256": sha256(tmp_path / "roster/entries.json"),
               "started_at": "2026-10-20T00:00:00Z", "ended_at": "2026-10-20T00:01:00Z"})
    result = tmp_path / "items/attempt/result.json"
    write_json(result, {"source_kind": "hosted", "errors": ["Public download blocked"], "version_pin": "1.0.0"})
    write_json(tmp_path / "acquisition-index.json", {"items": [{"identity": "owner/skill1", "status": "public_download_blocked",
               "result_path": "items/attempt/result.json", "result_sha256": sha256(result)}]})
    corpus_manifest(tmp_path)
    manifest = json.loads((tmp_path / "source-manifest.json").read_text(encoding="utf8"))
    assert len(manifest["entries"]) == 2
    assert manifest["entries"][1]["acquisition_status"] == "not_yet_attempted"
    assert manifest["entries"][0]["version_pin"] == "1.0.0"
