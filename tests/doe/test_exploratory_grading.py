"""Synthetic offline guards; these tests never open a research-run answer."""
from copy import deepcopy
from pathlib import Path

import pytest

from tools.doe.real_comparison import exploratory_grading as grading
from tools.doe.real_comparison.protocol import sha256, write_json


def _seal(root):
    return {p.relative_to(root).as_posix(): sha256(p) for p in root.rglob("*") if p.is_file()}


@pytest.fixture(scope="module")
def closed_packets(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("exploratory-grading")
    run = tmp_path / "generation"
    run.mkdir()
    schedule = {"main": [], "reviews": []}
    reference = {"human_verified": False, "supported_excesses": [],
        "receiving_points": [{"id": "receiver-1"}], "mandatory_checks": [{"id": "check-1"}]}
    for case in range(24):
        case_id = "synthetic-" + str(case).zfill(2)
        source = run / "cases" / case_id
        (source / "source").mkdir(parents=True)
        (source / "source" / "skill.txt").write_text("Keep the required result.\n", encoding="utf-8")
        (source / "source-bundle.txt").write_text("1 Keep the required result.\n", encoding="utf-8")
        write_json(run / "references" / (case_id + ".json"), reference)
        for method in ("skillflow", "audit", "chain"):
            for repeat in (1, 2, 3):
                workflow_id = f"{case_id}_{method}_{repeat}"
                schedule["main"].append({"workflow_id": workflow_id, "case_id": case_id,
                    "method": method, "repeat": repeat, "kind": "main"})
        for method in ("audit", "chain"):
            schedule["reviews"].append({"workflow_id": f"{case_id}_{method}_review",
                "case_id": case_id, "method": method, "repeat": 1, "kind": "review"})
    write_json(run / "schedule.json", schedule)
    for name in grading.COMMON_RULES:
        path = run / name
        path.write_text("{}\n" if path.suffix == ".json" else "Synthetic preserved rule.\n", encoding="utf-8")
    write_json(run / "freeze.json", {"schema_version": grading.OUTPUT_SCHEMA, "files": _seal(run)})
    for number, item in enumerate(schedule["main"] + schedule["reviews"]):
        workflow = run / "workflows" / item["workflow_id"]
        request = workflow / "requests" / "q001"
        request.mkdir(parents=True)
        (workflow / "answer.txt").write_text("Retain the required result.\n", encoding="utf-8")
        (request / "answer.txt").write_text("Retain the required result.\n", encoding="utf-8")
        # The first result is a native failure with valid, substantively usable
        # output. The second has identical content but invalid transport.
        write_json(workflow / "result.json", {"status": "failed" if number == 0 else "complete"})
        write_json(request / "response.json", {"accepted": number != 1})
        write_json(request / "receipt.json", {"protocol_status": "violated" if number == 1 else "conformant",
            "configuration_verified": True, "provider_verified": True, "completed": True,
            "violations": ["Synthetic invalid configuration"] if number == 1 else []})
    write_json(run / "output-freeze.json", {"schema_version": grading.OUTPUT_SCHEMA,
        "planned_outputs": 264, "files": {"workflows/" + p: h for p, h in _seal(run / "workflows").items()}})
    out = tmp_path / "grading"
    grading.prepare_packets(run, out)
    return run, out


def _pass(packet):
    grade = grading.read(packet / "grade.template.json")
    text = (packet / "candidate.txt").read_text(encoding="utf-8")
    line = text.splitlines().index("Retain the required result.") + 1
    source_evidence = [{"path": "skill.txt", "start_line": 1, "end_line": 1,
                        "quote": "Keep the required result."}]
    candidate_evidence = [{"start_line": line, "end_line": line, "quote": "Retain the required result."}]
    grade.update(reviewer_id="assistant-test", agent_id="fresh-agent-test", judgment="satisfies_reference")
    grade["check_results"][0].update(status="pass", reason="The required result is retained.",
        source_evidence=source_evidence, candidate_evidence=candidate_evidence)
    grade["receiving_point_coverage"][0].update(status="covered", reason="The receiving point is covered.",
        source_evidence=source_evidence, candidate_evidence=candidate_evidence)
    return grade


def test_unclosed_run_is_rejected_before_other_reads(tmp_path, monkeypatch):
    seen = []
    original = grading.read
    def tracked(path):
        seen.append(Path(path).name)
        return original(path)
    monkeypatch.setattr(grading, "read", tracked)
    with pytest.raises(FileNotFoundError):
        grading.prepare_packets(tmp_path / "unclosed", tmp_path / "out")
    assert seen == ["output-freeze.json"]
    assert not (tmp_path / "out").exists()


def test_packets_keep_all_outcomes_and_distinct_cases_per_fresh_batch(closed_packets):
    run, out = closed_packets
    assignments = grading.read(out / "assignments.json")["assignments"]
    private = grading.read(out / "private-map.json")["assignments"]
    assert len(assignments) == len(private) == 264
    batches = {}
    for row in private:
        batches.setdefault(row["primary_batch"], []).append(row["case_id"])
    assert len(batches) == 33
    assert all(len(cases) == len(set(cases)) == 8 for cases in batches.values())
    assert sum(row["chain_secondary_required"] for row in private) == 168
    assert all(not {"method", "repeat", "kind", "workflow_id"}.intersection(row) for row in assignments)
    packet = out / assignments[0]["packet"]
    original_path = next(r for r in private if r["candidate_id"] == assignments[0]["candidate_id"])["original_output_paths"][0]
    assert (packet / "artifacts/a0001.txt").read_bytes() == (run / original_path).read_bytes()
    assert grading.read(packet / "reference.json")["human_verified"] is False


def test_content_and_workflow_eligibility_are_separate(closed_packets, tmp_path):
    _, out = closed_packets
    rows = grading.read(out / "private-map.json")["assignments"]
    by_workflow = {r["workflow_id"]: r for r in rows}
    for suffix, expected in (("1", "satisfies_reference"), ("2", "workflow_failure")):
        row = by_workflow["synthetic-00_skillflow_" + suffix]
        packet = out / row["packet"]
        submission = tmp_path / (suffix + ".json")
        write_json(submission, _pass(packet))
        result = grading.validate_submission(out, submission)
        assert result["content_judgment"] == "satisfies_reference"
        assert result["workflow_primary_judgment"] == expected
        assert result["human_verified"] is False
    assert grading.read(out / by_workflow["synthetic-00_skillflow_1"]["packet"] / "execution.json")["status"] == "failed"


def test_assignment_tampering_rejected(closed_packets, tmp_path):
    _, out = closed_packets
    rows = grading.read(out / "assignments.json")
    original = deepcopy(rows)
    packet = out / rows["assignments"][0]["packet"]
    submission = tmp_path / "grade.json"
    write_json(submission, _pass(packet))
    rows["assignments"][0]["packet"] = rows["assignments"][1]["packet"]
    write_json(out / "assignments.json", rows)
    try:
        with pytest.raises(ValueError, match="assignment map changed"):
            grading.validate_submission(out, submission)
    finally:
        write_json(out / "assignments.json", original)


def test_mandatory_evidence_and_disputes_cannot_bypass_primary_guards(closed_packets):
    _, out = closed_packets
    row = grading.read(out / "assignments.json")["assignments"][0]
    packet = out / row["packet"]
    grade = _pass(packet)
    invalid = deepcopy(grade)
    invalid["check_results"][0]["source_evidence"][0].update(start_line=0, end_line=0, quote="")
    args = {"source_root": packet / "source", "candidate_text": (packet / "candidate.txt").read_text(encoding="utf-8")}
    with pytest.raises(ValueError, match="physical lines"):
        grading.validate_assistant_grade(invalid, grading.read(packet / "reference.json"), **args)
    grade.update(judgment="substantive_error", findings=[{"severity": "disputed"}])
    with pytest.raises(ValueError, match="remain indeterminate"):
        grading.validate_assistant_grade(grade, grading.read(packet / "reference.json"), **args)
