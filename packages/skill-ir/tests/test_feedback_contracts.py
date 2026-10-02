"""Pure feedback policy, exact input snapshots, and actual-graph feedback."""

from copy import deepcopy
import hashlib
import json
import stat
import zipfile

import pytest
from pydantic import ValidationError

from skill_ir.backtrace.evidence import canonical_graph_sha256, normalize_cfg
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.extraction.compiler import compile_candidate
from skill_ir.extraction.prompt import _EXAMPLES, build_whole_skill_prompt
from skill_ir.feedback.models import FeedbackLimits
from skill_ir.feedback.policy import decide
from skill_ir.feedback.prompts import FEEDBACK_INSTRUCTIONS, build_feedback_prompt
from skill_ir.inputs.snapshot import freeze_input, read_snapshot, verify_original_input
from skill_ir.inputs.skill_package import SkillPackage, SkillFile, SkillPackageError
from skill_ir.semantic_contract import contract_binding


def finding(status="represented", *, kind="semantic", number=1):
    return {"id": f"j{number}", "kind": kind, "status": status,
            **({"unknown_reason": "证据不足"} if status == "unknown" else {})}


@pytest.mark.parametrize("revision", range(4))
def test_represented_business_can_pass_only_without_unknown_or_difference(revision):
    audit = {"outcome": "completed", "findings": [finding(), finding(kind="context", number=2)]}
    assert decide(audit, revision)["status"] == "audit_passed"


@pytest.mark.parametrize("status", ["omitted", "mistranslated", "unsupported_addition", "internal_conflict"])
@pytest.mark.parametrize("revision", range(4))
def test_all_explicit_differences_get_the_same_bounded_policy(status, revision):
    audit = {"outcome": "completed", "findings": [finding(status), finding(number=2)]}
    decision = decide(audit, revision)
    assert decision["status"] == ("revision_limit" if revision == 3 else "revise")
    assert decision["actionable_ids"] == ["j1"]
    assert "unknown_ids" not in decision


def test_unknown_and_all_context_never_pass():
    with pytest.raises(ValueError):
        decide({"outcome": "completed", "findings": [finding("unknown")]}, 0)
    assert decide({"outcome": "completed", "findings": [finding(kind="context")]}, 0)["status"] == "semantic_failure"
    with pytest.raises(ValueError):
        decide({"outcome": "cannot_assess", "failure": {}}, 3)
    assert decide({"outcome": "completed", "findings": [finding("omitted")]}, 0, 0)["status"] == "revision_limit"


def conservative_finding():
    return {**finding(), "conservative": {
        "rule_id": "DEP-MERGE", "candidate_fact_ids": ["left", "right"],
        "lost_distinctions": ["无法区分各路径实际使用哪个结果"], "reason": "两个分支均有源文依据"}}


def test_conservative_dependency_passes_with_explicit_loss_not_revision():
    decision = decide({"outcome": "completed", "findings": [conservative_finding()]}, 0)
    assert decision["status"] == "audit_passed"
    assert decision["representation_summary"] == {"represented_ids": ["j1"], "conservative_ids": ["j1"]}
    assert not decision["actionable_ids"] and "unknown_ids" not in decision


@pytest.mark.parametrize("change", [
    {"status": "mistranslated"},
    {"conservative": {}},
    {"conservative": {"rule_id": "automatic-pass", "candidate_fact_ids": ["a"], "lost_distinctions": ["x"], "reason": "x"}},
])
def test_conservative_label_cannot_bypass_decision_contract(change):
    with pytest.raises(ValueError):
        decide({"outcome": "completed", "findings": [{**conservative_finding(), **change}]}, 0)


@pytest.mark.parametrize("reason", ["原文存在歧义", "原文自相矛盾", "语义未定义", "证据不足"])
def test_real_unknown_still_blocks_even_with_conservative_dependencies(reason):
    legacy = {**finding("unknown", number=2), "unknown_reason": reason}
    with pytest.raises(ValueError):
        decide({"outcome": "completed", "findings": [conservative_finding(), legacy]}, 0)


def test_conservative_dependency_never_exempts_separate_explicit_difference():
    decision = decide({"outcome": "completed", "findings": [conservative_finding(), finding("mistranslated", number=2)]}, 0)
    assert decision["status"] == "revise" and decision["actionable_ids"] == ["j2"]


def test_optional_conservative_absence_never_claims_precision():
    decision = decide({"outcome": "completed", "findings": [finding()]}, 0)
    assert decision["representation_summary"] == {"represented_ids": ["j1"], "conservative_ids": []}
    assert "precision_summary" not in decision
    assert "不代表精确保留" in decision["reason"]


@pytest.mark.parametrize("reason", [None, "", "  "])
def test_unknown_requires_reason_without_cause_enum(reason):
    with pytest.raises(ValueError, match="invalid finding"):
        decide({"outcome": "completed", "findings": [{**finding("unknown"), "unknown_reason": reason}]}, 0)


@pytest.mark.parametrize("audit", [
    {}, {"outcome": "completed", "findings": []}, {"outcome": "completed", "findings": [finding("complete")]},
    {"outcome": "completed", "findings": [finding("unknown", kind="context")]},
])
def test_invalid_audit_shape_is_not_treated_as_success(audit):
    with pytest.raises(ValueError):
        decide(audit, 0)


def test_separate_logical_budgets_and_semantic_upper_bound():
    limits = FeedbackLimits()
    assert limits.logical_call_bounds(initial_graph=False) == {"extraction": 16, "audit": 4, "total": 20}
    assert limits.logical_call_bounds(initial_graph=True) == {"extraction": 12, "audit": 4, "total": 16}
    assert FeedbackLimits(max_semantic_revisions=1, max_structural_repairs=0).logical_call_bounds(
        initial_graph=False) == {"extraction": 2, "audit": 2, "total": 4}
    for invalid in [-1, 4, True, "3"]:
        with pytest.raises(ValidationError):
            FeedbackLimits(max_semantic_revisions=invalid)
    with pytest.raises(ValueError):
        decide({"outcome": "completed", "findings": [finding()]}, 4)


def make_source(tmp_path):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "SKILL.md").write_bytes(b"\xef\xbb\xbf# Skill\r\n\r\nReturn the input.\r\n")
    (source / "scripts").mkdir()
    (source / "scripts" / "never_execute.py").write_bytes(b"raise RuntimeError('must not execute')\n")
    (source / "blob.bin").write_bytes(b"\x00\xffbinary")
    return source


def test_snapshot_raw_and_decoded_hashes_and_boundaries(tmp_path):
    source = make_source(tmp_path)
    raw_before = (source / "SKILL.md").read_bytes()
    directory = tmp_path / "run"
    metadata = freeze_input(source, directory, ArtifactWriter(()))
    package, bundle, recovered = read_snapshot(directory)
    assert recovered == metadata
    assert package.root_name == "skill"
    assert [f.path for f in package.files] == ["SKILL.md", "blob.bin", "scripts/never_execute.py"]
    entry = metadata["files"][0]
    assert entry["raw_sha256"] == hashlib.sha256(raw_before).hexdigest()
    assert entry["decoded_sha256"] == hashlib.sha256(raw_before.decode("utf-8-sig").encode("utf-8")).hexdigest()
    assert entry["raw_sha256"] != entry["decoded_sha256"]
    assert bundle["files"][0]["content"] == raw_before.decode("utf-8-sig")
    assert metadata["boundaries"]["binary_files"] == ["blob.bin"]
    assert metadata["boundaries"]["uninterpreted_code_files"] == ["scripts/never_execute.py"]
    assert (source / "SKILL.md").read_bytes() == raw_before
    verify_original_input(source, metadata)


def test_read_snapshot_never_accesses_original_and_resume_checks_raw_identity(tmp_path):
    source = make_source(tmp_path)
    run = tmp_path / "run"
    metadata = freeze_input(source, run, ArtifactWriter(()))
    # Same decoded text, changed raw BOM: offline replay remains possible, but
    # continuing online must reject the changed original byte identity.
    original = source / "SKILL.md"
    original.write_bytes(original.read_bytes()[3:])
    read_snapshot(run)
    with pytest.raises(ValueError, match="original Skill identity changed"):
        verify_original_input(source, metadata)
    original.unlink()
    read_snapshot(run)


@pytest.mark.parametrize("tamper", ["change", "add", "delete", "source", "manifest"])
def test_snapshot_rejects_changed_bytes_inventory_or_source(tmp_path, tamper):
    source = make_source(tmp_path)
    run = tmp_path / "run"
    freeze_input(source, run, ArtifactWriter(()))
    if tamper == "change":
        (run / "inputs/package/SKILL.md").write_text("modified", encoding="utf-8")
    elif tamper == "add":
        (run / "inputs/package/annotation.json").write_text("{}", encoding="utf-8")
    elif tamper == "delete":
        (run / "inputs/package/blob.bin").unlink()
    elif tamper == "source":
        (run / "inputs/source.json").write_text("{}", encoding="utf-8")
    else:
        path = run / "inputs/snapshot.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["root_name"] = "changed"
        path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        read_snapshot(run)


def test_zip_snapshot_preserves_root_members_and_archive_identity(tmp_path):
    archive = tmp_path / "sample.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("wrapped/SKILL.md", "# 中文\n\n返回原值。")
        output.writestr("wrapped/bin.bin", b"\x00raw")
    metadata = freeze_input(archive, tmp_path / "run", ArtifactWriter(()))
    package, source, _ = read_snapshot(tmp_path / "run")
    assert package.root_name == "wrapped"
    assert source["files"][0]["path"] == "SKILL.md"
    assert metadata["archive_sha256"] == hashlib.sha256(archive.read_bytes()).hexdigest()
    verify_original_input(archive, metadata)
    # ZIP metadata is part of original archive identity even if entries agree.
    with zipfile.ZipFile(archive, "a") as output:
        output.comment = b"changed envelope"
    with pytest.raises(ValueError, match="original Skill identity changed"):
        verify_original_input(archive, metadata)


@pytest.mark.parametrize("name", [
    "../outside.txt", "/absolute.txt", "C:/drive.txt", "dir/name:stream", "dir/NUL",
    "dir/bad?.txt", "dir/char\x01.txt",
])
def test_snapshot_rejects_unsafe_zip_members(tmp_path, name):
    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("SKILL.md", "safe")
        output.writestr(name, "unsafe")
    with pytest.raises(SkillPackageError):
        freeze_input(archive, tmp_path / "run", ArtifactWriter(()))


def test_snapshot_rejects_zip_symlinks_and_case_aliases(tmp_path):
    archive = tmp_path / "link.zip"
    with zipfile.ZipFile(archive, "w") as output:
        info = zipfile.ZipInfo("outside")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        output.writestr(info, "../elsewhere")
    with pytest.raises(SkillPackageError, match="symlink"):
        freeze_input(archive, tmp_path / "run", ArtifactWriter(()))
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("SKILL.md", "one")
        output.writestr("skill.md", "two")
    with pytest.raises(SkillPackageError, match="collision"):
        freeze_input(archive, tmp_path / "run", ArtifactWriter(()))


def test_snapshot_refuses_redacted_content_and_input_nested_run(tmp_path):
    source = make_source(tmp_path)
    with pytest.raises(ValueError, match="credential"):
        freeze_input(source, tmp_path / "run", ArtifactWriter(("Return the input",)))
    assert not (tmp_path / "run/inputs").exists()
    with pytest.raises(ValueError, match="nested"):
        freeze_input(source, source / "run", ArtifactWriter(()))


def test_snapshot_refuses_silent_overwrite(tmp_path):
    source = make_source(tmp_path)
    freeze_input(source, tmp_path / "run", ArtifactWriter(()))
    with pytest.raises(ValueError, match="already exists"):
        freeze_input(source, tmp_path / "run", ArtifactWriter(()))


def test_snapshot_json_duplicate_keys_are_rejected_even_when_last_value_matches(tmp_path):
    source = make_source(tmp_path)
    run = tmp_path / "run"
    freeze_input(source, run, ArtifactWriter(()))
    path = run / "inputs/snapshot.json"
    raw = path.read_text(encoding="utf-8")
    path.write_text(raw.replace('"schema_version": 1,', '"schema_version": 9, "schema_version": 1,'), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON member"):
        read_snapshot(run)


def make_feedback():
    cfg = compile_candidate(deepcopy(_EXAMPLES[0][1])).cfg
    assert cfg is not None
    graph = normalize_cfg(cfg)
    block = next(iter(graph["blocks"]))
    pointer = "/blocks/" + block + "/instructions/0"
    package = SkillPackage(root_name="demo", files=[SkillFile(
        path="SKILL.md", kind="markdown", content="Full original source sentinel", size=29)])
    defect = {
        "id": "difference-1", "kind": "semantic", "status": "mistranslated",
        "source_requirement": "Use source value", "actual_representation": "Wrong input recorded",
        "reason": "Exact comparison", "source_refs": [{"quote": "source sentinel"}],
        "controlled_refs": [{"unit_id": "f1", "quote": None}], "basis": ["explicit_graph"],
        "graph_refs": [pointer],
        "suggestions": [{"target_ids": ["f1"], "change": "Use the original value",
                         "reason": "Source evidence", "graph_refs": [pointer]}],
    }
    audit = {"graph_sha256": canonical_graph_sha256(graph), "findings": [defect],
             "forbidden_history": "HISTORY MUST NOT LEAK", "oracle_key": "ORACLE MUST NOT LEAK"}
    return package, cfg, audit, pointer


def test_feedback_uses_fixed_prompt_actual_graph_positions_and_latest_differences():
    package, cfg, audit, pointer = make_feedback()
    prompt = build_feedback_prompt(package, cfg, audit)
    assert prompt.startswith(build_whole_skill_prompt(package) + "\n\n")
    payload = json.loads(prompt.split(FEEDBACK_INSTRUCTIONS + "\n\n", 1)[1])
    assert payload.keys() == {"previous_cfg", "explicit_differences", *contract_binding()}
    assert payload["previous_cfg"] == normalize_cfg(cfg)
    target = payload["explicit_differences"][0]["suggestions"][0]["suggestion_targets"][0]
    assert target["graph_pointer"] == pointer
    assert target["value"] == next(iter(normalize_cfg(cfg)["blocks"].values()))["instructions"][0]
    assert "unknown_reminders" not in payload
    assert "HISTORY MUST NOT LEAK" not in prompt
    assert "ORACLE MUST NOT LEAK" not in prompt
    assert "Full original source sentinel" in prompt


def test_feedback_instructions_are_english_while_quoted_evidence_is_unchanged():
    import re

    package, cfg, audit, _ = make_feedback()
    quote = "原文引文，不可翻译。"
    audit["findings"][0]["source_refs"][0]["quote"] = quote
    prompt = build_feedback_prompt(package, cfg, audit)
    instructions, payload_text = prompt.split(FEEDBACK_INSTRUCTIONS + "\n\n", 1)
    assert not re.search(r"[\u3400-\u9fff]", FEEDBACK_INSTRUCTIONS)
    assert not re.search(r"[\u3400-\u9fff]", instructions)
    assert "Write explanatory diagnostics in Chinese" in FEEDBACK_INSTRUCTIONS
    assert json.loads(payload_text)["explicit_differences"][0]["source_refs"][0]["quote"] == quote


def test_feedback_refuses_old_graph_hash_and_nonexistent_targets():
    package, cfg, audit, _ = make_feedback()
    cfg.constraints.append("A new current constraint")
    with pytest.raises(ValueError, match="actual previous CFG"):
        build_feedback_prompt(package, cfg, audit)
    audit["graph_sha256"] = canonical_graph_sha256(normalize_cfg(cfg))
    audit["findings"][0]["suggestions"][0]["graph_refs"] = ["/blocks/not_present"]
    with pytest.raises((KeyError, ValueError)):
        build_feedback_prompt(package, cfg, audit)


def test_feedback_unknown_only_does_not_force_reextraction():
    package, cfg, audit, _ = make_feedback()
    audit["findings"] = audit["findings"][1:]
    with pytest.raises(ValueError, match="without explicit differences"):
        build_feedback_prompt(package, cfg, audit)
