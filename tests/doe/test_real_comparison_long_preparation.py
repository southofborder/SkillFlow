"""Fail-closed source preparation checks; no model or network calls."""
import json

import pytest

from tools.doe.real_comparison import long_preparation as prep


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def minimal_preparation(tmp_path, monkeypatch):
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "materials.txt"
    source.write_text("真实原文 {source_bundle} </script>\n", encoding="utf-8")
    dump(tmp_path / "preparation-freeze.json", {"files": {"materials.txt": prep.sha256(source)}})
    dump(tmp_path / "selection.json", {"selected": []})
    monkeypatch.setattr(prep, "verify_reference_packets", lambda *a: {"errors": [], "packet_count": 30})
    return tmp_path


def test_immutable_copy_preserves_multilingual_literal_source(tmp_path):
    original, copied = tmp_path / "original", tmp_path / "copy"
    original.write_bytes("原文 {source_bundle} ${not_a_command}\r\n".encode("utf-8"))
    prep._copy_bound(original, copied, prep.sha256(original))
    assert copied.read_bytes() == original.read_bytes()
    original.write_bytes(b"changed")
    with pytest.raises(ValueError, match="prior frozen input changed"):
        prep._copy_bound(original, tmp_path / "another", prep.sha256(copied))


def test_existing_copy_is_not_silently_replaced(tmp_path):
    original, copied = tmp_path / "original", tmp_path / "copy"
    original.write_bytes(b"frozen")
    copied.write_bytes(b"other")
    with pytest.raises(ValueError, match="immutable copy differs"):
        prep._copy_bound(original, copied, prep.sha256(original))
    assert copied.read_bytes() == b"other"


def test_verify_rejects_changed_prepared_bytes(tmp_path, monkeypatch):
    run = minimal_preparation(tmp_path, monkeypatch)
    (run / "materials.txt").write_bytes(b"changed")
    result = prep.verify_preparation(run, tmp_path)
    assert result["status"] == "failed"
    assert any("Prepared bytes changed" in error for error in result["errors"])
    assert result["model_calls"] == 0


def test_verify_rejects_a_dispatch_or_approval_protocol(tmp_path, monkeypatch):
    run = minimal_preparation(tmp_path, monkeypatch)
    dump(run / "protocol.json", {})
    dump(run / "mailbox/requests/unexpected/request.json", {})
    result = prep.verify_preparation(run, tmp_path)
    assert result["status"] == "failed"
    assert any("execution/approval record" in error for error in result["errors"])
    assert any("target requests or outputs" in error for error in result["errors"])
    assert result["execution_enabled"] is False


def test_preparation_refuses_a_forged_or_missing_root_source_audit(tmp_path):
    proposal, seal = tmp_path / "proposal.json", tmp_path / "seal.json"
    dump(proposal, {"status": "selection_complete_pending_human_reference"})
    dump(seal, {"selection_sha256": prep.sha256(proposal), "root_source_audit_complete": False, "formal_requests": 0})
    with pytest.raises(ValueError, match="Root source audit"):
        prep.prepare_long_cohort(tmp_path / "new", tmp_path, selection_path=proposal,
                                 selection_seal=seal, prior_run=tmp_path)
    assert not (tmp_path / "new").exists()


def test_verification_does_not_read_files_outside_its_run(tmp_path, monkeypatch):
    run = minimal_preparation(tmp_path / "run", monkeypatch)
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"not a run member")
    dump(run / "preparation-freeze.json", {"files": {"../outside.txt": prep.sha256(outside)}})
    result = prep.verify_preparation(run, tmp_path)
    assert result["status"] == "failed"
    assert any("outside its run" in error for error in result["errors"])


def test_empty_or_truncated_package_cannot_verify_as_complete(tmp_path, monkeypatch):
    run = minimal_preparation(tmp_path, monkeypatch)
    dump(run / "preparation-freeze.json", {"files": {}})
    result = prep.verify_preparation(run, tmp_path)
    assert result["status"] == "failed"
    assert any("omits required materials" in error for error in result["errors"])
    assert any("24 distinct selected" in error for error in result["errors"])


@pytest.fixture
def complete_package(tmp_path, monkeypatch):
    """Exercise preparation orchestration; packet byte verification has its own suite."""
    prior, run = tmp_path / "prior", tmp_path / "prepared"
    for name in prep.COPIED_RULES:
        dump(prior / name, {"grading_schema_version": "test-grading", "literal": "原文 ${value}"})
    for name in prep.PROMPTS:
        path = prior / "prompts" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Original 中文 {source_bundle}", encoding="utf-8")
    dump(prior / "evaluation-rules-freeze.json",
         {"files": {name: prep.sha256(prior / name) for name in prep.COPIED_RULES}})
    dump(prior / "materials-freeze.json",
         {"files": {"prompts/" + name: prep.sha256(prior / "prompts" / name) for name in prep.PROMPTS}})
    items = [{"canonical_id": f"owner/skill-{n:03d}", "version": "1.0",
              "reference_tokens": 20000, "source_sha256": str(n), "bundle_sha256": f"bundle-{n}"}
             for n in range(1, 31)]
    proposal, seal = tmp_path / "proposal.json", tmp_path / "seal.json"
    dump(proposal, {"status": "selection_complete_pending_human_reference",
                    "selected": items[:24], "reserves": items[24:],
                    "root_audit_required": True, "final_seal": False})
    dump(seal, {"selection_sha256": prep.sha256(proposal), "root_source_audit_complete": True,
                "formal_requests": 0})

    def packets(corpus, manifest, target):
        rows = []
        for n, item in enumerate(manifest["selected"] + manifest["reserves"], 1):
            case_id = f"real-{n:03d}"
            case = target / case_id
            case.mkdir(parents=True)
            (case / "source-bundle.txt").write_text("真实原文 {source_bundle} </script>\n", encoding="utf-8")
            dump(case / "reference.source-facts-draft.json",
                 {"human_verified": False, "coverage_state": "source_facts_only_pending_semantic_reference",
                  "human_verifications": [{"slot": slot, "status": "pending"} for slot in ("A", "B")]})
            rows.append({"case_id": case_id, "canonical_id": item["canonical_id"]})
        dump(target / "index.json", {"packets": rows})

    monkeypatch.setattr(prep, "prepare_reference_packets", packets)
    monkeypatch.setattr(prep, "verify_reference_packets",
                        lambda *a: {"verified": True, "errors": [], "packet_count": 30})
    result = prep.prepare_long_cohort(run, tmp_path, selection_path=proposal,
                                     selection_seal=seal, prior_run=prior)
    return run, result


def _rebind_member(run, relative, value):
    """Bypass byte mismatch deliberately to test the semantic invariant itself."""
    dump(run / relative, value)
    freeze = prep.read(run / "preparation-freeze.json")
    freeze["files"][relative] = prep.sha256(run / relative)
    dump(run / "preparation-freeze.json", freeze)


def test_preparation_records_completed_source_audit_without_claiming_human_gold(complete_package):
    run, result = complete_package
    assert result["verification"]["status"] == "passed"
    assert result["formal_requests"] == 0 and result["dispatch_enabled"] is False
    assert prep.read(run / "source-selection.json")["root_audit_required"] is True
    selected = prep.read(run / "selection.json")
    assert selected["root_audit_required"] is False
    assert selected["selection_state"] == prep.SELECTION_STATE
    assert selected["final_seal"] is False
    assert "remain unsealed" in selected["final_seal_scope"]
    assert not any((run / name).exists() for name in prep.FORBIDDEN_RECORDS)
    assert "真实原文 {source_bundle} </script>" in (
        run / "prepared-prompts/real-001_audit_r1.txt").read_text(encoding="utf-8")


def test_verification_rejects_same_count_source_identity_substitution(complete_package):
    run, _ = complete_package
    selection = prep.read(run / "selection.json")
    selection["selected"][0]["version"] = "different-source-version"
    _rebind_member(run, "selection.json", selection)
    result = prep.verify_preparation(run, run.parent)
    assert result["status"] == "failed"
    assert any("root-audited source identity" in error for error in result["errors"])


def test_verification_rejects_gate_and_nested_execution_artifacts(complete_package):
    run, _ = complete_package
    dump(run / "gate.json", {"state": "approved"})
    dump(run / "workflows/unexpected/attempts/001/result.json", {"answer": "unexpected"})
    result = prep.verify_preparation(run, run.parent)
    assert result["status"] == "failed"
    assert any("execution/approval record" in error for error in result["errors"])
    assert any("target requests or outputs" in error for error in result["errors"])


def test_verification_rejects_completed_human_claim_in_partial_reference(complete_package):
    run, _ = complete_package
    draft = prep.read(run / "references/real-001.json")
    draft["human_verified"] = True
    _rebind_member(run, "references/real-001.json", draft)
    result = prep.verify_preparation(run, run.parent)
    assert result["status"] == "failed"
    assert any("completed semantic or human verification" in error for error in result["errors"])


def test_verification_rejects_truncated_human_allocation(complete_package):
    run, _ = complete_package
    allocation = prep.read(run / "review/private-assignment-map.json")
    allocation["assignments"].pop()
    _rebind_member(run, "review/private-assignment-map.json", allocation)
    result = prep.verify_preparation(run, run.parent)
    assert result["status"] == "failed"
    assert any("human assignment count differs" in error for error in result["errors"])
