"""Synthetic temporary workspaces only: no real people, model calls or network."""
from copy import deepcopy
import json
import socket
import subprocess

import pytest

from tools.doe.real_comparison import assessment
from tools.doe.real_comparison import reference_epoch as epoch
from tools.doe.real_comparison.semantic_metrics import GRADING_SCHEMA_VERSION


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def evidence():
    return [{"path": "SKILL.md", "start_line": 1, "end_line": 1,
             "quote": "真实原文 ${literal} {source_bundle}"}]


def complete_reference(case):
    result = {"case_id": case["case_id"], "canonical_id": case["canonical_id"],
              "source_sha256": case["source_sha256"], "source_bundle_sha256": case["bundle_sha256"],
              "purpose_basis": "skill_declared_purpose_only",
              "grading_schema_version": GRADING_SCHEMA_VERSION, "state": "assistant_draft",
              "human_verified": False, "human_verifications": [],
              "coverage_state": "complete_for_human_verification"}
    for group in assessment.REFERENCE_FIELDS:
        result[group] = [{"id": group + "-1", "statement": "Synthetic test interpretation.", "evidence": evidence()}]
    result["supported_excesses"][0].update({name: "Synthetic " + name for name in assessment.EXPOSURE_FIELDS})
    return result


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Packet/preparation verifiers have their own suites; orchestration uses 30 fixed packets."""
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline reference operations must not use a network or subprocess")
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(epoch, "verify_preparation", lambda *a: {"status": "passed", "packet_count": 30})
    monkeypatch.setattr(epoch, "verify_reference_packets", lambda *a: {"verified": True, "packet_count": 30})
    parent, destination = tmp_path / "prepared", tmp_path / "epoch"
    cases = []
    for number in range(1, 31):
        case_id = f"real-{number:03d}"
        source = parent / "cases" / case_id / "source" / "SKILL.md"
        source.parent.mkdir(parents=True)
        source.write_bytes("真实原文 ${literal} {source_bundle}\r\n".encode("utf-8"))
        bundle = source.parent.parent / "source-bundle.txt"
        bundle.write_bytes(source.read_bytes())
        case = {"case_id": case_id, "canonical_id": f"test/skill-{number}", "version": "1.0",
                "source_sha256": epoch.sha256(source), "bundle_sha256": epoch.sha256(bundle),
                "source_tree_sha256": "test-tree-" + str(number)}
        cases.append(case)
        dump(source.parent.parent / "source-manifest.json", {"case_id": case_id,
             "canonical_id": case["canonical_id"], "source_sha256": case["source_sha256"],
             "source_bundle_sha256": case["bundle_sha256"], "source_tree_sha256": case["source_tree_sha256"]})
        partial = complete_reference(case)
        partial["coverage_state"] = "source_facts_only_pending_semantic_reference"
        partial["receiving_points"] = []
        dump(parent / "references" / (case_id + ".json"), partial)
    selection = {"selected": cases[:24], "reserves": cases[24:], "rules_sha256": "test-rules",
                 "candidate_queue_sha256": "test-queue"}
    for name in epoch.INHERITED:
        dump(parent / name, selection if name in {"selection.json", "source-selection.json"} else {})
    dump(parent / "grading-contract.json", {"grading_schema_version": GRADING_SCHEMA_VERSION})
    for name in ("preparation-freeze.json", "preparation-state.json", "preparation-verification.json"):
        dump(parent / name, {"synthetic": True})
    frozen = {p.relative_to(parent): p.read_bytes() for p in parent.rglob("*") if p.is_file()}
    result = epoch.prepare_reference_epoch(destination, preparation_run=parent, corpus_root=tmp_path / "corpus")
    assert result["model_calls"] == 0
    return destination, parent, cases, frozen


def import_draft(workspace, *, index=0, statement=None, invalidate=False):
    directory, _, cases, _ = workspace
    reference = complete_reference(cases[index])
    if statement:
        reference["declared_purpose"][0]["statement"] = statement
    path = dump(directory.parent / "explicit-draft.json", reference)
    return epoch.import_reference_revision(directory, path, reason="Synthetic source-grounded test revision.",
                                           invalidate_confirmations=invalidate)


def import_roster(workspace):
    directory = workspace[0]
    path = dump(directory.parent / "synthetic-roster.json", {"reviewers": [
        {"reviewer_id": reviewer, "human": True, "role": "reference_verifier", "declared_at": "2026-10-01T00:00:00Z"}
        for reviewer in ("H1", "H2")]})
    return epoch.import_actual_roster(directory, path)


def attestation(workspace, case_id="real-001", reviewer="H1", suffix=""):
    directory = workspace[0]
    path = directory / "references" / (case_id + ".json")
    reference = epoch.read(path)
    return {"case_id": case_id, "reviewer_id": reviewer, "human": True, "approved": True,
            "role": "reference_verifier", "confirmation": assessment.CONFIRMATION,
            "source_only_attestation": True, "source_only_confirmation": epoch.SOURCE_ONLY_CONFIRMATION,
            "source_sha256": reference["source_sha256"], "reference_sha256": epoch.sha256(path),
            "attestation_id": f"synthetic-{case_id}-{reviewer}-{suffix}", "attested_at": "2026-10-02T00:00:00Z",
            "per_item_checks": [{"group": group, "id": fact["id"], "checked": True}
                                for group in assessment.REFERENCE_FIELDS for fact in reference[group]]}


def import_confirmation(workspace, case_id="real-001", reviewer="H1", suffix=""):
    path = dump(workspace[0].parent / "synthetic-confirmation.json", attestation(workspace, case_id, reviewer, suffix))
    return epoch.import_actual_confirmation(workspace[0], path)


def bind_synthetic_current_selection(workspace, monkeypatch):
    directory = workspace[0]
    binding = {"state": "validated_current_selector", "corpus_root": str(directory.parent / "corpus")}
    monkeypatch.setattr(epoch, "inspect_current_selection", lambda *a: binding)
    monkeypatch.setattr(epoch, "verify_saved_binding", lambda saved, expected: saved)
    epoch.validate_current_selection(directory, directory.parent / "synthetic-proposal")


def test_preparation_preserves_all_original_bytes_and_stays_pending(workspace):
    directory, parent, _, frozen = workspace
    assert {p.relative_to(parent): p.read_bytes() for p in parent.rglob("*") if p.is_file()} == frozen
    status = epoch.verify_reference_epoch(directory)
    assert status["complete_draft_schema_and_quotes"] == 0
    assert status["source_selection_readiness"] == "pending_current_selector_validation"
    assert status["actual_active_confirmations"] == 0 and status["execution_enabled"] is False
    assert not (directory / "human-roster.json").exists()
    assert (directory / "reference-history/real-001/v0000.json").read_bytes() == frozen[next(
        relative for relative in frozen if relative.as_posix() == "references/real-001.json")]
    assert not any((directory / path).exists() for path in epoch.FORBIDDEN)


def test_actual_parent_and_child_or_existing_destination_are_never_replaced(workspace):
    directory, parent, _, frozen = workspace
    for invalid in (parent, parent / "child", directory):
        with pytest.raises(ValueError):
            epoch.prepare_reference_epoch(invalid, preparation_run=parent, corpus_root=parent.parent)
    assert (parent / "preparation-freeze.json").read_bytes() == frozen[next(
        relative for relative in frozen if relative.as_posix() == "preparation-freeze.json")]


@pytest.mark.parametrize("field", ["canonical_id", "source_sha256", "source_bundle_sha256", "case_id"])
def test_revision_rejects_any_source_identity_substitution(workspace, field):
    reference = complete_reference(workspace[2][0])
    reference[field] = "different"
    submission = dump(workspace[0].parent / "revision.json", reference)
    with pytest.raises(ValueError, match="identity|exact frozen case"):
        epoch.import_reference_revision(workspace[0], submission, reason="Test explicit revision.")
    assert epoch.read(workspace[0] / "reference-revisions.json")["cases"]["real-001"]["active_version"] == 0


@pytest.mark.parametrize("change, message", [
    (lambda r: r.update(human_verified=True), "manufacture human approval"),
    (lambda r: r.update(human_verifications=[{"status": "pending", "reviewer_id": "H1"}]), "manufacture human approval"),
    (lambda r: r.update(grading_schema_version="wrong"), "grading contract"),
    (lambda r: r["unknowns"][0]["evidence"][0].update(quote="Invented quotation"), "quotation differs"),
    (lambda r: r["preservation_checks"][0].update(id=""), "group/id"),
    (lambda r: r["supported_excesses"][0].pop("recipient"), "six material identity"),
])
def test_revision_rejects_forged_approval_and_invalid_evidence_or_grading(workspace, change, message):
    reference = complete_reference(workspace[2][0])
    change(reference)
    submission = dump(workspace[0].parent / "invalid-revision.json", reference)
    with pytest.raises(ValueError, match=message):
        epoch.import_reference_revision(workspace[0], submission, reason="Test explicit revision.")


def test_complete_revision_keeps_original_and_submission_bytes_without_creating_people(workspace):
    result = import_draft(workspace)
    directory = workspace[0]
    assert result["version"] == 1 and result["human_approval_created"] is False
    assert (directory / "reference-history/real-001/v0001.json").read_bytes() == (directory.parent / "explicit-draft.json").read_bytes()
    assert epoch.verify_reference_epoch(directory)["complete_draft_schema_and_quotes"] == 1
    assert not (directory / "human-roster.json").exists()


@pytest.mark.parametrize("change", [
    lambda a: a.update(source_only_attestation=False),
    lambda a: a.update(source_only_confirmation=""),
    lambda a: a.update(reference_sha256="stale"),
    lambda a: a.update(human=False),
    lambda a: a.update(reviewer_id="unregistered"),
    lambda a: a.update(attested_at="2026-10-02T00:00:00"),
    lambda a: a["per_item_checks"].pop(),
    lambda a: a["per_item_checks"].append(deepcopy(a["per_item_checks"][0])),
    lambda a: a["per_item_checks"][0].update(checked=False),
    lambda a: a["per_item_checks"][0].update(group="unknown"),
])
def test_confirmation_requires_current_source_only_personal_checks_for_every_group(workspace, change):
    import_draft(workspace)
    import_roster(workspace)
    submission = attestation(workspace)
    change(submission)
    path = dump(workspace[0].parent / "bad-personal-submission.json", submission)
    with pytest.raises(ValueError):
        epoch.import_actual_confirmation(workspace[0], path)
    assert epoch.verify_reference_epoch(workspace[0])["actual_active_confirmations"] == 0


def test_h1_confirmation_then_h2_error_invalidates_only_one_case_and_requires_both_again(workspace):
    directory = workspace[0]
    import_draft(workspace)
    import_draft(workspace, index=1)
    import_roster(workspace)
    import_confirmation(workspace)
    import_confirmation(workspace, "real-002", "H1")
    original = (directory / "references/real-001.json").read_bytes()
    prior_manifest = (directory / "approvals/import-manifest.json").read_bytes()
    prior_submissions = {p: p.read_bytes() for p in (directory / "approvals/submissions").glob("*.json")}
    stale = attestation(workspace, reviewer="H2")
    with pytest.raises(ValueError, match="explicitly invalidate"):
        import_draft(workspace, statement="Corrected after the second person's source check.")
    assert (directory / "references/real-001.json").read_bytes() == original
    import_draft(workspace, statement="Corrected after the second person's source check.", invalidate=True)
    assert all(p.read_bytes() == content for p, content in prior_submissions.items())
    archived = directory / "confirmation-history/real-001/before-v0002/approvals/import-manifest.json"
    assert archived.read_bytes() == prior_manifest
    records = epoch._active_imports(directory)["records"]
    assert [(r["case_id"], r["reviewer_id"]) for r in records] == [("real-002", "H1")]
    with pytest.raises(ValueError, match="current exact source and reference"):
        epoch.import_actual_confirmation(directory, dump(directory.parent / "stale.json", stale))
    import_confirmation(workspace, reviewer="H2", suffix="corrected")
    import_confirmation(workspace, reviewer="H1", suffix="corrected")
    assert epoch.verify_reference_epoch(directory)["actual_active_confirmations"] == 3
    assert len(epoch.read(directory / "human-import-history.json")["events"]) == 5


def test_duplicate_person_and_prior_attestation_id_are_rejected(workspace):
    import_draft(workspace)
    import_roster(workspace)
    import_confirmation(workspace)
    with pytest.raises(ValueError, match="already confirmed"):
        import_confirmation(workspace)
    import_draft(workspace, statement="Synthetic revision.", invalidate=True)
    with pytest.raises(ValueError, match="new personal attestation identity"):
        import_confirmation(workspace)


@pytest.mark.parametrize("relative", ["reference-history/real-001/v0000.json", "rubric.md",
    "human-submission-history", "import-manifest-history", "approvals/import-manifest.json"])
def test_changed_initial_or_submission_or_import_manifest_history_fails_closed(workspace, relative):
    import_draft(workspace)
    import_roster(workspace)
    import_confirmation(workspace)
    target = workspace[0] / relative
    if target.is_dir():
        target = next(target.rglob("*.json"))
    target.write_bytes(b"{}\n")
    with pytest.raises(ValueError):
        epoch.verify_reference_epoch(workspace[0])


def test_import_history_cannot_be_truncated_to_hide_an_original_submission(workspace):
    import_draft(workspace)
    import_roster(workspace)
    import_confirmation(workspace)
    directory = workspace[0]
    dump(directory / "human-import-history.json", {"events": []})
    dump(directory / "approvals/import-manifest.json", {"records": []})
    dump(directory / "human-import-provenance.json", {"records": []})
    with pytest.raises(ValueError, match="missing or unindexed"):
        epoch.verify_reference_epoch(directory)


def test_revision_index_cannot_hide_preserved_prior_versions(workspace):
    import_draft(workspace)
    directory = workspace[0]
    index = epoch.read(directory / "reference-revisions.json")
    entry = index["cases"]["real-001"]
    entry["history"] = entry["history"][:1]
    entry.update(active_version=0, active_sha256=entry["history"][0]["sha256"])
    dump(directory / "reference-revisions.json", index)
    (directory / "references/real-001.json").write_bytes((directory / "reference-history/real-001/v0000.json").read_bytes())
    with pytest.raises(ValueError, match="missing or unindexed"):
        epoch.verify_reference_epoch(directory)


@pytest.mark.parametrize("relative", ["protocol.json", "formal-gate.json", "formal-protocol.json",
                                     "mailbox/requests/x/request.json", "workflows/x/result.json"])
def test_dispatch_protocols_and_targets_are_rejected(workspace, relative):
    dump(workspace[0] / relative, {})
    with pytest.raises(ValueError, match="source-only reference epoch"):
        epoch.verify_reference_epoch(workspace[0])


def test_reference_freeze_requires_current_selection_validation(workspace):
    with pytest.raises(ValueError, match="Current source selection validation is pending"):
        epoch.freeze_reference_epoch(workspace[0])
    assert not (workspace[0] / "reference-freeze.json").exists()


def test_reference_freeze_requires_all_30_and_two_distinct_people(workspace, monkeypatch):
    import_draft(workspace)
    import_roster(workspace)
    import_confirmation(workspace)
    bind_synthetic_current_selection(workspace, monkeypatch)
    with pytest.raises(ValueError, match="All 30 exact references"):
        epoch.freeze_reference_epoch(workspace[0])
    assert not (workspace[0] / "reference-freeze.json").exists()


def test_all_30_current_pairs_freeze_and_later_revision_requires_separate_corrigendum(workspace, monkeypatch):
    directory = workspace[0]
    for index in range(30):
        import_draft(workspace, index=index)
    import_roster(workspace)
    bind_synthetic_current_selection(workspace, monkeypatch)
    for case in workspace[2]:
        for reviewer in ("H1", "H2"):
            import_confirmation(workspace, case["case_id"], reviewer)
    result = epoch.freeze_reference_epoch(directory)
    assert result["personal_confirmations"] == 60 and result["execution_enabled"] is False
    status = epoch.verify_reference_epoch(directory)
    assert status["reference_epoch_sealed"] is True and status["actual_active_confirmations"] == 60
    assert status["source_selection_readiness"] == "validated_current_selector"
    assert len(epoch.read(directory / "approved-source-set.json")["cases"]) == 30
    with pytest.raises(ValueError, match="separate corrigendum"):
        import_draft(workspace, statement="Error found after full freeze.", invalidate=True)
    assert not any((directory / path).exists() for path in epoch.FORBIDDEN)
    (directory / "human-import-provenance.json").write_bytes(b"{}")
    with pytest.raises(ValueError):
        epoch.verify_reference_epoch(directory)


def test_cli_requires_explicit_human_submission_flag_and_has_no_dispatch_command(workspace):
    with pytest.raises(SystemExit):
        epoch.main(["import-roster", "--epoch-dir", str(workspace[0]), "--submission", "synthetic.json"])
    with pytest.raises(SystemExit):
        epoch.main(["dispatch", "--epoch-dir", str(workspace[0])])
