"""Fictional source-reference publication; no target calls or human approval."""
import json

import pytest

from tools.doe.real_comparison.protocol import sha256, write_json
from tools.doe.real_comparison.reference_drafts import publish_reference_drafts
from tools.doe.real_comparison.semantic_metrics import GRADING_SCHEMA_VERSION


@pytest.fixture
def drafts(tmp_path):
    cases = []
    write_json(tmp_path / "materials-freeze.json", {"fixture": True})
    write_json(tmp_path / "grading-contract.json", {"grading_schema_version": GRADING_SCHEMA_VERSION})
    for i in range(30):
        case = {"case_id": f"real-{i+1:03d}", "canonical_id": f"fictional/skill{i}", "source_sha256": f"source{i}"}
        cases.append(case)
        directory = tmp_path / "cases" / case["case_id"]
        path = directory / "source/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Fictional source 引文\nReturn the requested value.\n", encoding="utf-8")
        (directory / "source-bundle.txt").write_bytes(path.read_bytes())
        write_json(directory / "source-manifest.json", {"source_bundle_sha256": sha256(directory / "source-bundle.txt"),
                   "files": [{"path": "SKILL.md", "kind": "operational_text", "sha256": sha256(path)}]})
        evidence = [{"path": "SKILL.md", "start_line": 1, "end_line": 2, "quote": path.read_text(encoding="utf-8").strip()}]
        fact = {"id": "P1", "reason": "Preserve the declared output.", "evidence": evidence}
        ref = {**case, "state": "assistant_draft", "human_verified": False,
               "coverage_state": "complete_for_human_verification", "grading_schema_version": GRADING_SCHEMA_VERSION,
               "purpose_basis": "skill_declared_purpose_only", "user_request": None, "reviewed_files": ["SKILL.md"],
               "declared_purpose": [fact], "required_behavior": [fact], "receiving_points": [{**fact, "id": "B1"}],
               "necessary_sensitive_uses": [], "supported_excesses": [], "unknowns": [],
               "preservation_checks": [fact], "mandatory_checks": [{**fact, "id": "M1"}]}
        write_json(tmp_path / "reference-drafts/assistant-v1" / (case["case_id"] + ".json"), ref)
        write_json(tmp_path / "references" / (case["case_id"] + ".json"), {"initial_draft": True})
    write_json(tmp_path / "selection.json", {"selected": cases[:24], "reserves": cases[24:]})
    return tmp_path


def test_complete_cohort_preserves_initial_drafts_and_never_approves(drafts):
    original = (drafts / "references/real-001.json").read_bytes()
    result = publish_reference_drafts(drafts)
    assert len(result["entries"]) == 30 and result["actual_human_confirmations"] == 0
    assert result["formal_calls"] == 0
    assert (drafts / "reference-draft-history/source-facts-v0/real-001.json").read_bytes() == original
    assert not (drafts / "reference-freeze.json").exists()
    assert publish_reference_drafts(drafts) == result
    assert "H1 pending; H2 pending" in (drafts / "human-reference-package.html").read_text(encoding="utf-8")


def test_publication_validates_all_thirty_before_first_active_write(drafts):
    path = drafts / "reference-drafts/assistant-v1/real-030.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["reviewed_files"] = []
    write_json(path, value)
    with pytest.raises(ValueError, match="reviewed_files"):
        publish_reference_drafts(drafts)
    assert json.loads((drafts / "references/real-001.json").read_text(encoding="utf-8")) == {"initial_draft": True}
    assert not (drafts / "reference-draft-freeze-v1.json").exists()


def test_quote_tampering_and_human_freeze_prevent_replacement(drafts):
    source = drafts / "cases/real-030/source/SKILL.md"
    source.write_text("Changed source", encoding="utf-8")
    with pytest.raises(ValueError, match="quotation"):
        publish_reference_drafts(drafts)
    write_json(drafts / "reference-freeze.json", {"fixture": True})
    with pytest.raises(ValueError, match="corrigendum"):
        publish_reference_drafts(drafts)


def test_already_imported_human_attestation_prevents_silent_draft_update(drafts):
    write_json(drafts / "approvals/import-manifest.json", {"records": [{"fixture": True}]})
    with pytest.raises(ValueError, match="human confirmations"):
        publish_reference_drafts(drafts)
