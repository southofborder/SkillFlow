"""Offline packets and truthful assistant labels for a closed exploratory cohort.

This is deliberately separate from the frozen human importers. No entry point
launches a model, registers a human, changes a reference, or aggregates scores.
Packet construction is forbidden until all 264 outcomes have an output seal.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import shutil

from .assessment import JUDGMENTS
from .protocol import SEED, canonical_hash, sha256, utc_now, write_json
from .semantic_metrics import (grading_template, validate_semantic_grade,
                               validate_grade_evidence, _evidence)

SCHEMA = "skillflow-exploratory-assistant-grading-v1"
OUTPUT_SCHEMA = "skillflow-real-comparison-exploratory-cli-v1"
EVIDENCE_LEVEL = "assistant_exploratory_not_human_gold"
COMMON_RULES = ("common-assumptions.md", "common-runtime-contract.json", "rubric.md",
                "evaluation-rules-supplement-v1.md", "grading-contract.json", "user-amendment.json")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def inside(root, relative):
    root = Path(root).resolve()
    raw = root / relative
    path = raw.resolve()
    if raw.is_symlink() or not path.is_relative_to(root):
        raise ValueError("A grading file escapes its sealed workspace")
    return path


def verify_closed_outputs(run_dir):
    """Check closure metadata before opening any candidate or reference text."""
    run = Path(run_dir).resolve()
    # Keep this first: an unclosed run must not expose even one target to grading.
    seal = read(run / "output-freeze.json")
    if seal.get("schema_version") != OUTPUT_SCHEMA or seal.get("planned_outputs") != 264:
        raise ValueError("Assistant grading requires the exploratory 264-output closure")
    prepared = read(run / "freeze.json")
    if prepared.get("schema_version") != OUTPUT_SCHEMA:
        raise ValueError("The grading run is not the frozen exploratory cohort")
    schedule_path = run / "schedule.json"
    if prepared.get("files", {}).get("schedule.json") != sha256(schedule_path):
        raise ValueError("The fixed exploratory schedule changed")
    schedule = read(schedule_path)
    entries = schedule["main"] + schedule["reviews"]
    if (len(schedule["main"]) != 216 or len(schedule["reviews"]) != 48
            or len({r["workflow_id"] for r in entries}) != 264):
        raise ValueError("All 216 main and 48 fixed review identities are required")
    files = seal.get("files", {})
    actual = {p.relative_to(run).as_posix() for p in (run / "workflows").rglob("*") if p.is_file()}
    if set(files) != actual:
        raise ValueError("The complete output tree differs from its closed file index")
    for item in entries:
        path = run / "workflows" / item["workflow_id"] / "result.json"
        relative = path.relative_to(run).as_posix()
        if relative not in files or sha256(path) != files[relative]:
            raise ValueError("A planned workflow lacks a sealed terminal result")
        if read(path).get("status") in {None, "running", "pending", "interrupted", "not_generated"}:
            raise ValueError("An active, ungenerated or resumable outcome cannot be graded")
    # Terminal metadata for every identity is verified before candidate payloads
    # are even opened for hashing.
    for relative, expected in files.items():
        if not relative.startswith("workflows/") or sha256(inside(run, relative)) != expected:
            raise ValueError("A closed exploratory output changed")
    # Inputs/references are checked only after complete output closure is known.
    for relative, expected in prepared["files"].items():
        if sha256(inside(run, relative)) != expected:
            raise ValueError("A frozen exploratory grading input changed")
    return entries, seal


def _copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _output_files(run, workflow):
    """Keep reports/results and every available visible response, without prompts.

    The full native manifest stays in the private archive. Its input snapshots,
    raw transport receipts and hidden reasoning are never added to grader panes.
    """
    paths = []
    manifest = workflow / "candidate-manifest.json"
    if manifest.exists():
        manifest_data = read(manifest)
        for relative in manifest_data.get("reading_view_files", []):
            path = inside(run, relative)
            if manifest_data.get("files", {}).get(relative) != sha256(path):
                raise ValueError("A reading-view member is absent from its native candidate seal")
            if (not path.is_relative_to(workflow / "attempts")
                    or {"inputs", "calls", "replay"}.intersection(path.relative_to(workflow).parts)
                    or path.name in {"manifest.json", "transport.json", "execution-boundary.json"}
                    or not (path.name == "report.md" or path.suffix == ".json")):
                # Direct answers are separately included below; a direct
                # manifest can legitimately list its workflow-level answer.
                if path != workflow / "answer.txt":
                    raise ValueError("A reading-view member is not an approved visible workflow artifact")
                continue
            paths.append(path)
    for name in ("candidate-view.txt", "answer.txt"):
        if (workflow / name).exists():
            paths.append(workflow / name)
    # A failed native stage can leave substantive visible output without a
    # parsed report. Rejected responses remain explicit artifacts, not passes.
    paths.extend(sorted(workflow.glob("requests/q*/answer.txt")))
    paths.extend(sorted(workflow.glob("requests/q*/cli/last-message.txt")))
    return list(dict.fromkeys(paths))


def prepare_packets(run_dir, out_dir):
    """Create immutable anonymous primary packets; do not execute on live runs."""
    run, out = Path(run_dir).resolve(), Path(out_dir).resolve()
    entries, closed = verify_closed_outputs(run)
    if out.exists() or out.is_relative_to(run) or run.is_relative_to(out):
        raise ValueError("Use a fresh grading directory outside the generation run")
    # Thirty-three fresh eight-packet batches: no assistant sees two outputs
    # from one case. Round numbers do not encode method, kind or repetition.
    rng = random.Random(SEED)
    by_case = defaultdict(list)
    for item in sorted(entries, key=lambda r: r["workflow_id"]):
        by_case[item["case_id"]].append(item)
    if len(by_case) != 24 or any(len(items) != 11 for items in by_case.values()):
        raise ValueError("Each of the 24 cases requires exactly eleven fixed outcomes")
    for items in by_case.values():
        rng.shuffle(items)
    order = []
    for round_index in range(11):
        cases = sorted(by_case)
        rng.shuffle(cases)
        order.extend((by_case[case_id][round_index], round_index, index % 3)
                     for index, case_id in enumerate(cases))
    mapping, public = [], []
    out.mkdir(parents=True)
    for name in COMMON_RULES:
        _copy(run / name, out / "common-rules" / name)
    for item, round_index, group in order:
        workflow = run / "workflows" / item["workflow_id"]
        candidate_id = canonical_hash({"workflow": item["workflow_id"], "seed": SEED})[:20]
        directory = out / "packets" / candidate_id
        directory.mkdir(parents=True)
        source = run / "cases" / item["case_id"]
        shutil.copytree(source / "source", directory / "source")
        _copy(source / "source-bundle.txt", directory / "source-bundle.txt")
        reference = run / "references" / (item["case_id"] + ".json")
        _copy(reference, directory / "reference.json")
        reference_data = read(reference)
        if reference_data.get("human_verified") is not False:
            raise ValueError("Exploratory packet references must retain false human verification")
        members, chunks = [], []
        for number, path in enumerate(_output_files(run, workflow), start=1):
            relative = "artifacts/a" + str(number).zfill(4) + path.suffix
            _copy(path, directory / relative)
            if path == workflow / "candidate-view.txt":
                role = "candidate_reading_view"
            elif path == workflow / "answer.txt":
                role = "final_answer"
            elif path.is_relative_to(workflow / "requests"):
                role = "archival_request_visible_response"
            else:
                role = "native_report_or_result"
            member = {"file": relative, "sha256": sha256(path), "bytes": path.stat().st_size,
                      "role": role}
            if role == "archival_request_visible_response":
                request = path.parent.parent if path.parent.name == "cli" else path.parent
                response = read(request / "response.json") if (request / "response.json").exists() else {}
                member.update(request_ordinal=request.name, accepted=response.get("accepted"),
                    disposition="Retained complete visible response. May be superseded, corrected, intermediate or rejected; never automatically attribute it to the selected candidate.")
            members.append(member)
            chunks.append("=== " + relative + " ===\n" + path.read_text(encoding="utf-8"))
        # No ellipses or size cap: exact original member files are linked, and
        # this concatenation supplies one stable physical-line evidence target.
        candidate = "\n\n".join(chunks)
        (directory / "candidate.txt").write_bytes(candidate.encode("utf-8"))
        result = read(workflow / "result.json")
        request_states = []
        for request in sorted((workflow / "requests").glob("q*")):
            response = read(request / "response.json") if (request / "response.json").exists() else {}
            receipt = read(request / "receipt.json") if (request / "receipt.json").exists() else {}
            request_states.append({"accepted": response.get("accepted"),
                "protocol_status": receipt.get("protocol_status"), "violation_count": len(receipt.get("violations", [])),
                "configuration_verified": receipt.get("configuration_verified"),
                "provider_verified": receipt.get("provider_verified"), "completed": receipt.get("completed")})
        execution = {"status": result.get("status"), "diagnostic_record_available": bool(result.get("reason")),
                     "available_output_files": len(members),
                     "nonempty_visible_output": any(p.read_text(encoding="utf-8").strip()
                                                    for p in _output_files(run, workflow)),
                     "request_states": request_states,
                     "content_policy": "Grade available substantive content independently of native completion status. Missing output and a protocol violation cannot pass."}
        write_json(directory / "execution.json", execution, immutable=True)
        write_json(directory / "artifacts.json", {"members": members,
            "complete_available_visible_responses_included": True,
            "blinding_limit": "Explicit method/repeat/workflow labels are masked in the packet wrapper; original content and artifact structure can reveal them."}, immutable=True)
        template = {"schema_version": SCHEMA, "evidence_level": EVIDENCE_LEVEL,
            "candidate_id": candidate_id, "candidate_sha256": sha256(directory / "candidate.txt"),
            "reference_sha256": sha256(reference), "output_freeze_sha256": sha256(run / "output-freeze.json"),
            "source_sha256": reference_data.get("source_sha256"),
            "source_bundle_sha256": sha256(directory / "source-bundle.txt"),
            "reviewer_id": "", "agent_id": "", "scoring_role": "primary",
            "human_verified": False, "actual_human_review_work_seconds": None,
            "judgment": "pending_assistant", "check_results": [
                {"check_id": c["id"], "status": "pending", "reason": "",
                 "source_evidence": [], "candidate_evidence": []} for c in reference_data["mandatory_checks"]],
            "matched_exposure_ids": [], "findings": [], "reference_correction_proposals": []}
        # Every primary packet has the same interface. Chain assessment is a
        # separate secondary assignment, after common primary labels are sealed.
        template.update(grading_template(reference_data, "audit"))
        write_json(directory / "grade.template.json", template, immutable=True)
        rows = {"candidate_id": candidate_id, "primary_batch": str(round_index + 1).zfill(2) + "-" + str(group + 1),
                "packet": "packets/" + candidate_id, "common_rules": "common-rules"}
        public.append(rows)
        mapping.append({**item, **rows, "chain_secondary_required": item["method"] != "audit",
                        "original_output_paths": [p.relative_to(run).as_posix() for p in _output_files(run, workflow)]})
    write_json(out / "private-map.json", {"schema_version": SCHEMA, "source_run": str(run),
        "assignments": mapping}, immutable=True)
    write_json(out / "assignments.json", {"schema_version": SCHEMA, "assignments": public,
        "planned_results": 264, "human_reference_confirmation": "pending", "actual_human_scoring": "pending",
        "actual_human_review_work_seconds": None, "evidence_level": EVIDENCE_LEVEL}, immutable=True)
    files = {p.relative_to(out).as_posix(): sha256(p) for p in out.rglob("*") if p.is_file()}
    write_json(out / "packet-freeze.json", {"schema_version": SCHEMA, "created_at": utc_now(),
        "source_output_freeze_sha256": sha256(run / "output-freeze.json"),
        "planned_outputs": closed["planned_outputs"], "files": files, "model_calls": 0}, immutable=True)
    return {"packets": 264, "model_calls": 0, "evidence_level": EVIDENCE_LEVEL}


def validate_assistant_grade(grade, reference, *, source_root, candidate_text):
    """Reuse v2 semantics without constructing a fake human flag even in memory.

    Identity/hash binding to packet-freeze.json is the caller's responsibility.
    This validator handles common primary content; chain secondaries are added
    later and validated with the private method by validate_semantic_grade.
    """
    if (grade.get("schema_version") != SCHEMA or grade.get("evidence_level") != EVIDENCE_LEVEL
            or grade.get("human_verified") is not False
            or grade.get("actual_human_review_work_seconds") is not None
            or not grade.get("reviewer_id") or not grade.get("agent_id")):
        raise ValueError("Assistant grades require explicit nonhuman exploratory provenance")
    if grade.get("judgment") not in JUDGMENTS:
        raise ValueError("Complete the assistant primary judgment")
    expected = {c["id"] for c in reference["mandatory_checks"]}
    checks = grade.get("check_results", [])
    ids = [c.get("check_id") for c in checks]
    if len(ids) != len(expected) or set(ids) != expected or any(
            c.get("status") not in {"pass", "fail", "disputed"} or not c.get("reason") for c in checks):
        raise ValueError("Every mandatory source check requires one reasoned assistant assessment")
    matched = grade.get("matched_exposure_ids", [])
    known = {u["id"] for u in reference["supported_excesses"]}
    if len(matched) != len(set(matched)) or not set(matched).issubset(known):
        raise ValueError("Exposure credit must use distinct frozen reference units")
    if grade["judgment"] == "satisfies_reference" and (not candidate_text.strip()
            or any(c["status"] != "pass" for c in checks) or set(matched) != known
            or any(f.get("severity") in {"substantive", "disputed"} for f in grade.get("findings", []))):
        raise ValueError("A passing judgment contradicts required source checks or available output")
    validate_semantic_grade(grade, reference, method=None)
    validate_grade_evidence(grade, source_root=source_root, candidate_text=candidate_text)
    # The semantic evidence helper also checks mandatory-check evidence when
    # provided through this projection; omissions may have empty candidate lists.
    projected = {"claim_units": [], "receiving_point_coverage": [],
                 "reduction_assessments": [], "error_records": checks, "chain_assessment": None}
    for check in checks:
        _evidence(check.get("source_evidence"), source=True)
        _evidence(check.get("candidate_evidence"), required=False)
    validate_grade_evidence(projected, source_root=source_root, candidate_text=candidate_text)
    records = (checks + grade["claim_units"] + grade["receiving_point_coverage"]
               + grade["reduction_assessments"] + grade["error_records"] + grade.get("findings", []))
    if (any(r.get("status") == "disputed" or r.get("assessment") == "disputed"
            or r.get("severity") == "disputed" or r.get("functionality_impact") == "disputed" for r in records)
            and grade["judgment"] != "indeterminate"):
        raise ValueError("Unresolved semantic disputes must remain indeterminate")
    if grade.get("reference_correction_proposals") and grade["judgment"] != "indeterminate":
        raise ValueError("A proposed source-reference correction must remain indeterminate until resolved")
    return grade


def validate_submission(grading_dir, submission_path):
    """Validate a label and return separate content/workflow judgments.

    A diagnostic content pass is not a planned-workflow pass when protocol or
    output eligibility fails. Native partial/failed status alone is not a gate.
    """
    root = Path(grading_dir).resolve()
    frozen = read(root / "packet-freeze.json")
    if frozen.get("schema_version") != SCHEMA or frozen.get("planned_outputs") != 264:
        raise ValueError("Assistant submissions require the complete grading packet freeze")
    for name in ("assignments.json", "private-map.json") + tuple("common-rules/" + n for n in COMMON_RULES):
        if sha256(root / name) != frozen.get("files", {}).get(name):
            raise ValueError("A frozen anonymous assignment map changed")
    grade = read(submission_path)
    candidate_id = grade.get("candidate_id")
    assignments = read(root / "assignments.json")["assignments"]
    private = read(root / "private-map.json")["assignments"]
    if (len(assignments) != 264 or len(private) != 264
            or len({r["candidate_id"] for r in assignments}) != 264
            or {r["candidate_id"] for r in assignments} != {r["candidate_id"] for r in private}):
        raise ValueError("The grading assignment map must preserve all 264 identities")
    matches = [r for r in assignments if r["candidate_id"] == candidate_id]
    if len(matches) != 1:
        raise ValueError("The assistant label does not identify one fixed anonymous packet")
    packet = inside(root, matches[0]["packet"])
    members = {p.relative_to(root).as_posix(): p for p in packet.rglob("*") if p.is_file()}
    expected = {k: v for k, v in frozen["files"].items() if k.startswith(matches[0]["packet"] + "/")}
    if set(members) != set(expected) or any(sha256(path) != expected[k] for k, path in members.items()):
        raise ValueError("An anonymous grading packet changed after sealing")
    if (grade.get("candidate_sha256") != sha256(packet / "candidate.txt")
            or grade.get("reference_sha256") != sha256(packet / "reference.json")
            or grade.get("source_sha256") != read(packet / "reference.json").get("source_sha256")
            or grade.get("source_bundle_sha256") != sha256(packet / "source-bundle.txt")
            or grade.get("output_freeze_sha256") != frozen["source_output_freeze_sha256"]):
        raise ValueError("The assistant grade binds a different candidate, reference or output cohort")
    if grade.get("scoring_role") not in {"primary", "secondary"}:
        raise ValueError("Unknown assistant scoring role")
    validate_assistant_grade(grade, read(packet / "reference.json"),
        source_root=packet / "source", candidate_text=(packet / "candidate.txt").read_text(encoding="utf-8"))
    execution = read(packet / "execution.json")
    requests = execution.get("request_states", [])
    protocol_eligible = bool(requests) and all(r.get("accepted") is True
        and r.get("protocol_status") == "conformant"
        and r.get("violation_count") == 0
        and all(r.get(k) is True for k in ("configuration_verified", "provider_verified", "completed"))
        for r in requests)
    return {"validated_grade": grade, "content_judgment": grade["judgment"],
        "protocol_eligible": protocol_eligible, "execution_status": execution.get("status"),
        "workflow_primary_judgment": (grade["judgment"] if protocol_eligible
            and execution.get("nonempty_visible_output") is True else "workflow_failure"),
        "human_verified": False, "evidence_level": EVIDENCE_LEVEL}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)
    print(json.dumps(prepare_packets(args.run_dir, args.out_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
