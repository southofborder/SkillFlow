"""Fictional local human-record fixtures; no real approvals or model calls."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from tools.doe.real_comparison.__main__ import main
from tools.doe.real_comparison.artifacts import seal_candidate
from tools.doe.real_comparison.assessment import import_human_attestation, finalize_human_references
from tools.doe.real_comparison.execution import prepare_schedule
from tools.doe.real_comparison.protocol import SCHEMA, sha256, write_json
from tools.doe.real_comparison.results import freeze_outputs, aggregate_scores, import_grade, verify_output_freeze
from tools.doe.real_comparison.review import prepare_scoring_assignments, prepare_review_assignments


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evidence(line, quote):
    return [{"path": "SKILL.md", "start_line": line, "end_line": line, "quote": quote}]


@pytest.fixture
def closed_cohort(tmp_path):
    """Build 264 failed local result fixtures, not actual experimental runs."""
    run = tmp_path / "fictional-human-workflow"
    cases = []
    for i in range(24):
        case_id = f"case-{i:02d}"
        path = run / "cases" / case_id / "source/SKILL.md"
        path.parent.mkdir(parents=True)
        text = "# Fictional engineering fixture\nReturn only the approved summary.\nThe ordinary return caller is unspecified.\n<script>window.fixture = true;</script>\n"
        path.write_text(text, encoding="utf-8")
        (path.parent.parent / "source-bundle.txt").write_text(text, encoding="utf-8")
        case = {"case_id": case_id, "source_sha256": "fixture-source-" + case_id, "source_cluster": "cluster-" + str(i // 3)}
        cases.append(case)
        required = evidence(2, "Return only the approved summary.")
        unknown = evidence(3, "The ordinary return caller is unspecified.")
        reference = {"case_id": case_id, "source_sha256": case["source_sha256"], "state": "approved",
                     "coverage_state": "complete_for_human_verification", "purpose_basis": "skill_declared_purpose_only", "user_request": None,
                     "declared_purpose": [{"id": "P1", "reason": "Return the requested summary.", "evidence": required}],
                     "required_behavior": [{"id": "Q1", "reason": "Preserve the approved summary.", "evidence": required}],
                     "receiving_points": [{"id": "B1", "reason": "Ordinary return has an unspecified caller.", "evidence": unknown}],
                     "necessary_sensitive_uses": [], "supported_excesses": [],
                     "unknowns": [{"id": "U1", "reason": "No user-delivery boundary is established.", "evidence": unknown}],
                     "preservation_checks": [], "mandatory_checks": [{"id": "M1", "reason": "Do not invent the return recipient.", "evidence": unknown}]}
        write_json(run / "references" / (case_id + ".json"), reference)
    write_json(run / "selection.json", {"selected": cases, "reserves": []})
    people = [{"reviewer_id": p, "human": True, "role": "reference_verifier", "declared_at": "2026-10-20T00:00:00+00:00"} for p in ("H1", "H2")]
    people += [{"reviewer_id": p, "human": True, "role": "timed_reviewer"} for p in ("R1", "R2", "R3")]
    write_json(run / "human-roster.json", {"fixture_only": True, "reviewers": people})
    for case in cases:
        ref_path = run / "references" / (case["case_id"] + ".json")
        for person in ("H1", "H2"):
            attestation = {"case_id": case["case_id"], "reviewer_id": person, "source_sha256": case["source_sha256"],
                           "reference_sha256": sha256(ref_path), "human": True, "approved": True, "role": "reference_verifier",
                           "attestation_id": "fictional-" + person + "-" + case["case_id"], "attested_at": "2026-10-20T01:00:00+00:00",
                           "confirmation": "I personally verified this source reference."}
            submission = run / "fictional-submissions" / (person + "-" + case["case_id"] + ".json")
            write_json(submission, attestation)
            import_human_attestation(run, submission)
    finalize_human_references(run, cases)
    schedule = prepare_schedule(run, cases)
    assignments = prepare_scoring_assignments(run)
    prepare_review_assignments(run, [c["case_id"] for c in cases])
    first = next(a for a in assignments if a["method"] == "audit" and a["kind"] == "main" and a["repeat"] == 1)
    for item in schedule["main"] + schedule["reviews"]:
        directory = run / "workflows" / item["workflow_id"]
        result = {"workflow_id": item["workflow_id"], "status": "failed", "reason": "Fictional zero-model execution failure.", "answer_sha256": None}
        if item["workflow_id"] == first["workflow_id"]:
            answer = directory / "answer.txt"
            answer.parent.mkdir(parents=True, exist_ok=True)
            answer.write_text("The fictional execution failed before a source-grounded audit was available.", encoding="utf-8")
            result.update(answer_sha256=sha256(answer), **seal_candidate(run, item["workflow_id"]))
        write_json(directory / "result.json", result)
    freeze_outputs(run)
    return run, first


def grade_for(run, item):
    result = read(run / "workflows" / item["workflow_id"] / "result.json")
    return {"schema_version": SCHEMA, "candidate_id": item["candidate_id"], "reviewer_id": item["primary_reviewer_id"],
            "scoring_role": "primary", "human_verified": True, "submission_id": "fictional-score-1", "attested_at": "2026-10-20T02:00:00+00:00",
            "confirmation": "I personally checked this candidate against the source reference.", "candidate_sha256": result["answer_sha256"],
            "reference_sha256": sha256(run / "references" / (item["case_id"] + ".json")), "judgment": "substantive_error",
            "check_results": [{"check_id": "M1", "status": "fail", "reason": "The failed execution supplied no usable audit."}],
            "matched_exposure_ids": [], "findings": []}


def submit(run, value, name="fictional-grade.json"):
    path = run / name
    write_json(path, value)
    return path


def test_anonymous_cli_packets_import_and_all264_failure_denominator(closed_cohort, capsys):
    run, item = closed_cohort
    assert main(["prepare-scoring-packets", "--run-dir", str(run)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {"scoring_packets": 264, "model_calls": 0}
    packet = run / "review/scoring" / item["candidate_id"]
    template = read(packet / "grade.template.json")
    assert template["human_verified"] is False and template["judgment"] == "pending_human"
    assert not {"workflow_id", "method", "repeat"}.intersection(template)
    html = (packet / "index.html").read_text(encoding="utf-8")
    assert "&lt;script&gt;window.fixture" in html and "<script>window.fixture" not in html
    assert main(["import-grade", "--run-dir", str(run), "--submission", str(submit(run, grade_for(run, item)))]) == 0
    capsys.readouterr()
    result = aggregate_scores(run)
    assert result["planned_results"] == 264 and result["all_planned_in_denominator"] is True
    assert sum(sum(group.values()) for group in result["groups"].values()) == 264
    assert result["complete"] is False and result["primary_comparisons"] == []
    row = next(r for r in read(run / "scores.json")["rows"] if r["workflow_id"] == item["workflow_id"])
    assert row["judgment"] == "workflow_failure" and row["protocol_eligible"] is False


def test_human_scores_require_registered_assigned_person_and_personal_attestation(closed_cohort):
    run, item = closed_cohort
    proper = grade_for(run, item)
    broken = {**proper, "reviewer_id": "unregistered-agent"}
    with pytest.raises(ValueError, match="assignment|actual human"):
        import_grade(run, submit(run, broken))
    broken = {**proper, "human_verified": False}
    with pytest.raises(ValueError, match="human-verified"):
        import_grade(run, submit(run, broken))
    broken = {**proper, "confirmation": "An assistant proposed this score."}
    with pytest.raises(ValueError, match="personal confirmation"):
        import_grade(run, submit(run, broken))
    broken = {**proper, "scoring_role": "secondary"}
    with pytest.raises(ValueError, match="other human"):
        import_grade(run, submit(run, broken))
    assert not (run / "grades/import-manifest.json").exists()


def test_v2_import_checks_exact_evidence_and_replays_detailed_metrics(closed_cohort):
    from tools.doe.real_comparison.semantic_metrics import grading_template
    run, item = closed_cohort
    reference = read(run / "references" / (item["case_id"] + ".json"))
    grade = {**grade_for(run, item), **grading_template(reference, "audit")}
    coverage = grade["receiving_point_coverage"][0]
    coverage.update(status="missed", reason="The failed answer does not resolve the source boundary.",
                    source_evidence=evidence(3, "The ordinary return caller is unspecified."))
    wrong = deepcopy(grade)
    wrong["receiving_point_coverage"][0]["source_evidence"][0]["quote"] = "Invented source quote"
    with pytest.raises(ValueError, match="quotation"):
        import_grade(run, submit(run, wrong, "v2-wrong.json"))
    import_grade(run, submit(run, grade, "v2-valid.json"))
    aggregate_scores(run)
    scores = read(run / "scores.json")
    assert scores["semantic_metrics"]["groups"]["audit/main"]["planned_workflows"] == 72
    assert len(scores["semantic_metrics"]["rows"]) == 264
    assert scores["semantic_metrics"]["groups"]["audit/main"]["assessed_workflows"] == 1


def test_pending_reference_cannot_receive_a_passing_human_score(closed_cohort):
    run, item = closed_cohort
    reference_path = run / "references" / (item["case_id"] + ".json")
    reference = read(reference_path)
    reference.update(state="draft_pending", coverage_state="pending_human_verification")
    write_json(reference_path, reference)
    grade = grade_for(run, item)
    grade.update(judgment="satisfies_reference", check_results=[{"check_id": "M1", "status": "pass", "reason": "Fictional proposed pass."}])
    with pytest.raises((ValueError, OSError), match="reference|coverage|changed|approved"):
        import_grade(run, submit(run, grade))
    assert not (run / "grades/import-manifest.json").exists()


def test_output_freeze_rejects_missing_active_outstanding_and_changed_results(closed_cohort):
    run, item = closed_cohort
    (run / "output-freeze.json").unlink()
    path = run / "workflows" / item["workflow_id"] / "result.json"
    saved = read(path)
    path.unlink()
    with pytest.raises(ValueError, match="All planned outputs"):
        freeze_outputs(run)
    write_json(path, {**saved, "status": "interrupted"})
    with pytest.raises(ValueError, match="resumable"):
        freeze_outputs(run)
    write_json(path, saved)
    request = run / "mailbox/requests/unresolved"
    write_json(request / "request.json", {"request_id": "fictional"})
    with pytest.raises(ValueError, match="outstanding"):
        freeze_outputs(run)
    write_json(request / "stop.json", {"reason": "Fictional explicit terminal stop."})
    freeze_outputs(run)
    write_json(path, {**saved, "reason": "Changed after freeze"})
    with pytest.raises(ValueError, match="frozen candidate"):
        verify_output_freeze(run)


def test_timed_cli_packets_and_import_keep_quality_independently_pending(closed_cohort, capsys):
    run, _ = closed_cohort
    assert main(["prepare-timed-packets", "--run-dir", str(run)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["timed_packets"] == 72 and result["references_in_timed_packets"] is False
    assignment = read(run / "review/private-assignment-map.json")["assignments"][0]
    packet = (run / "review/timed-packets" / (assignment["assignment_id"] + ".html")).read_text(encoding="utf-8")
    assert "approved summary" in packet and "Frozen human source reference" not in packet
    assert "&lt;script&gt;window.fixture" in packet
    record = {"schema_version": SCHEMA, "assignment_id": assignment["assignment_id"], "case_id": assignment["case_id"],
              "reviewer_id": assignment["reviewer_id"], "human": True, "active_seconds": 30, "status": "finished",
              "started_at": "2026-10-20T03:00:00+00:00", "finished_at": "2026-10-20T03:00:30+00:00",
              "corrected_conclusion": "The ordinary return caller remains unspecified.", "final_quality": "pending_independent_adjudication",
              "attestation": "I personally performed this timed review without consulting this case reference or another method answer."}
    assert main(["import-timed", "--run-dir", str(run), "--submission", str(submit(run, record, "timed.json"))]) == 0
    imported = json.loads(capsys.readouterr().out)
    assert imported["quality"] == "pending_independent_adjudication"
    assert len(read(run / "review/import-manifest.json")["records"]) == 1
    invalid = {**record, "final_quality": "correct"}
    with pytest.raises(ValueError, match="pending quality"):
        main(["import-timed", "--run-dir", str(run), "--submission", str(submit(run, invalid, "timed-self-score.json"))])


def test_score_import_requires_output_closure_before_any_human_flags(closed_cohort):
    run, item = closed_cohort
    (run / "output-freeze.json").unlink()
    with pytest.raises(FileNotFoundError):
        import_grade(run, submit(run, grade_for(run, item)))
    assert not (run / "grades/import-manifest.json").exists()


def test_cli_replay_regenerates_derived_outputs_without_dispatch_or_hiding_protocol_failure(closed_cohort, capsys, monkeypatch):
    from tools.doe.real_comparison import execution
    from tools.doe.real_comparison.protocol import prepare_protocol
    run, _ = closed_cohort
    prepare_protocol(run)
    directory = run / "mailbox/requests/calibration_fixture_q001"
    core = "Fictional saved prompt; no target was dispatched."
    delivery = execution.ENVELOPE.replace("{core}", core)
    directory.mkdir(parents=True)
    (directory / "core-prompt.txt").write_text(core, encoding="utf-8", newline="")
    (directory / "prompt.txt").write_text(delivery, encoding="utf-8", newline="")
    write_json(directory / "request.json", {"request_id": directory.name, "workflow_id": "calibration_fixture",
               "mode": "calibration", "created_at": "2026-10-20T00:00:00+00:00",
               "core_sha256": execution._digest(core), "delivery_sha256": execution._digest(delivery)})
    write_json(directory / "dispatch.json", {"protocol_conformant": True,
               "dispatched_at": "2026-10-20T00:00:01+00:00", "actual_spawn": {"delivery_integrity": "violated"}})
    write_json(directory / "response.json", {"accepted": False, "answer": None, "answer_sha256": None})
    before = sha256(directory / "dispatch.json")
    def forbidden(*args, **kwargs):
        pytest.fail("Offline replay attempted target execution or dispatch")
    for name in ("run_workflow", "mark_dispatched", "authorize_dispatch"):
        monkeypatch.setattr(execution, name, forbidden)
    assert main(["replay", "--run-dir", str(run), "--corpus-root", str(run / "empty-offline-corpus")]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["model_calls"] == 0 and result["passed"] is False
    assert result["execution"]["byte_integrity"]["status"] == "passed"
    assert result["execution"]["protocol_conformance"]["status"] == "violated"
    assert result["derived_artifacts"]["scoring"]["planned_results"] == 264
    assert result["semantic_comparison_complete"] is False
    assert result["derived_artifacts"]["costs"]["usage_totals"]["total_tokens"] is None
    assert result["derived_artifacts"]["report"]["semantic_comparison"] == "incomplete"
    assert all(v["model_calls"] == 0 for v in result["derived_artifacts"].values())
    assert (run / "cost-ledger.json").is_file() and (run / "report.md").is_file()
    assert sha256(directory / "dispatch.json") == before
    assert len(list((run / "mailbox/requests").glob("*/dispatch.json"))) == 1


def test_timed_packet_hides_materials_and_disables_editing_outside_active_timer(tmp_path):
    from html.parser import HTMLParser
    import re
    import shutil
    import subprocess
    from tools.doe.real_comparison.review import write_timed_packet
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required to execute the timer UI state-transition regression")
    path = tmp_path / "timer.html"
    write_timed_packet(path, {"assignment_id": "fictional", "case_id": "case", "reviewer_id": "R1"},
                       "Original source <script>untrusted</script>", "Original answer")
    document = path.read_text(encoding="utf-8")
    class Elements(HTMLParser):
        def __init__(self):
            super().__init__()
            self.by_id = {}
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if attrs.get("id"):
                self.by_id[attrs["id"]] = attrs
    parsed = Elements()
    parsed.feed(document)
    assert "hidden" in parsed.by_id["materials"]
    assert "disabled" in parsed.by_id["conclusion"]
    scripts = re.findall(r"<script>([\s\S]*?)</script>", document)
    assert len(scripts) == 1
    exercise = """
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const script=JSON.parse(fs.readFileSync(0,'utf8'));let now=0,tick=null;
const els={materials:{hidden:true},conclusion:{disabled:true,value:''},identity:{},start:{},pause:{},finish:{},clock:{},outcome:{value:'finished'}};
const listeners={};const doc={hidden:false,getElementById:id=>els[id],addEventListener:(name,fn)=>listeners[name]=fn};
vm.runInNewContext(script,{document:doc,performance:{now:()=>now},setInterval:fn=>{tick=fn;},console});
assert.equal(els.materials.hidden,true);assert.equal(els.conclusion.disabled,true);
els.start.onclick();assert.equal(els.materials.hidden,false);assert.equal(els.conclusion.disabled,false);
now+=10000;els.pause.onclick();assert.equal(els.materials.hidden,true);assert.equal(els.conclusion.disabled,true);
els.start.onclick();doc.hidden=true;listeners.visibilitychange();assert.equal(els.materials.hidden,true);assert.equal(els.conclusion.disabled,true);
doc.hidden=false;els.start.onclick();now+=1790000;tick();assert.equal(els.materials.hidden,true);assert.equal(els.conclusion.disabled,true);
els.start.onclick();assert.equal(els.materials.hidden,true);assert.equal(els.conclusion.disabled,true);
"""
    completed = subprocess.run([node, "-e", exercise], input=json.dumps(scripts[0]), text=True, encoding="utf-8", capture_output=True, timeout=10)
    assert completed.returncode == 0, completed.stderr
