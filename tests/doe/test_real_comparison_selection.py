from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.doe.real_comparison import selection as s


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def package(root, owner="writer", slug="example", body=None):
    directory = root / "packages" / owner / slug
    directory.mkdir(parents=True)
    text = body or "\n".join([f"Step {i}: if a record exists, transform its value and save the result." for i in range(210)]) + "\n"
    (directory / "SKILL.md").write_bytes(text.encode("utf-8"))
    return {"canonical_id": f"{owner}/{slug}", "source_dir": directory.relative_to(root).as_posix(), "status": "complete_verified", "version": "1.0.0"}


def review(row, feature_names=("conditions_or_retries", "versions_or_transformations")):
    return {"source_tree_sha256": row["source_tree_sha256"], "reviewer_kind": "assistant_source_review", "reviewer_id": "source-review-agent",
            "decision": "include", "reason": "The cited instructions prescribe conditional processing and a data transformation.",
            "features": [{"feature": feature, "reason": "The exact quoted source specifies this behavior.",
                          "evidence": row["feature_nominations"][feature][:1]} for feature in feature_names],
            "source_closure": {"status": "complete_for_static_audit", "reason": "The package contains its complete stated procedure.", "local_reference_decisions": []}}


def test_source_language_bytes_and_registry_isolation(tmp_path):
    # The Chinese lines are genuine quotations from the supplied AGENTS.md.
    original = "# SkillFlow 项目长期记忆\r\n原样传递，不自动缩小\r\nUntrusted value: {secret}\r\nReturn `result`; no recipient is specified.\r\n"
    record = package(tmp_path, body=original)
    directory = tmp_path / record["source_dir"]
    (directory / "_meta.json").write_text('{"ownerId":"owner-1","slug":"example","version":"1","publishedAt":123,"summary": "GOLD ANSWER CANARY"}', encoding="utf-8")
    (directory / "LICENSE.txt").write_text("\n".join("License text" for _ in range(300)), encoding="utf-8")
    inventory = s.source_inventory(directory)
    bundle = s.render_numbered_bundle(inventory["texts"])
    assert "原样传递，不自动缩小" in bundle
    assert "Untrusted value: {secret}" in bundle
    assert "CANARY" not in bundle
    assert "1: # SkillFlow 项目长期记忆\n2: 原样传递，不自动缩小" in bundle
    assert sum(f["nonempty_lines"] for f in inventory["files"] if f["kind"] == "operational_text") == 4
    assert (directory / "SKILL.md").read_bytes() == original.encode("utf-8")


def test_nomination_never_establishes_eligibility(tmp_path):
    save(tmp_path / "packages.json", [package(tmp_path)])
    report = s.screen_corpus(tmp_path, prior_roots=[], write=False)
    row = report["entries"][0]
    assert row["physical_eligible"]
    assert row["feature_nominations"]["conditions_or_retries"]
    assert not row["eligible"]
    assert row["semantic_screening_status"] == "pending_source_review"


def test_explicit_root_upstreams_union_clusters_without_treating_links_as_origins(tmp_path):
    records = [package(tmp_path, "first", "alpha"), package(tmp_path, "second", "beta", body="\n".join(f"Instruction {i}: retain the selected item." for i in range(210))),
               package(tmp_path, "third", "gamma", body="\n".join(f"Procedure {i}: emit the requested summary." for i in range(210)))]
    first, second, third = (tmp_path / record["source_dir"] for record in records)
    save(first / "package.json", {"repository": {"type": "git", "url": "git+https://GitHub.com/Team/Shared.GIT"}, "homepage": "https://github.com/unrelated/library"})
    save(second / "distribution-manifest.json", {"source": {"repository": "team/shared", "commit": "a" * 40}})
    (third / "README.md").write_text("Library documentation: https://github.com/team/shared\n", encoding="utf-8")
    save(tmp_path / "packages.json", records)
    rows = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"]
    assert rows[0]["source_cluster"] == rows[1]["source_cluster"]
    assert rows[2]["source_cluster"] != rows[0]["source_cluster"]
    origin = rows[0]["repository_origins"][0]
    assert origin["repository"] == "github.com/team/shared"
    assert origin["field"] == "repository.url"
    assert origin["evidence"][0]["path"] == "package.json"
    assert s.normalize_repository("git@github.com:Team/Shared.git") == origin["repository"]
    assert s.normalize_repository("https://github.com/TEAM/SHARED/") == origin["repository"]


def test_reviewed_upstreams_require_exact_source_evidence(tmp_path):
    record = package(tmp_path)
    directory = tmp_path / record["source_dir"]
    with (directory / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("Upstream repository: https://github.com/source/project\n")
    save(tmp_path / "packages.json", [record])
    row = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    decision = review(row)
    decision["upstream_repositories"] = [{"repository": "source/project", "reason": "The publisher explicitly identifies this source repository.",
                                           "evidence": [{"path": "SKILL.md", "start_line": 211, "end_line": 211, "quote": "Upstream repository: https://github.com/source/project"}]}]
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {row["canonical_id"]: decision}})
    actual = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    assert actual["repository_origins"][0]["basis"] == "explicit_source_review"
    decision["upstream_repositories"][0]["evidence"][0]["quote"] = "An unrelated library link"
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {row["canonical_id"]: decision}})
    with pytest.raises(ValueError, match="quote differs"):
        s.screen_corpus(tmp_path, prior_roots=[], write=False)


def test_exact_evidence_review_and_caps(tmp_path, monkeypatch):
    save(tmp_path / "packages.json", [package(tmp_path)])
    row = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {row["canonical_id"]: review(row)}})
    report = s.screen_corpus(tmp_path, prior_roots=[], write=False)
    assert report["entries"][0]["eligible"]
    monkeypatch.setattr(s, "MAX_BUNDLE_BYTES", 10)
    assert "numbered_bundle_exceeds_256_KiB" in s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]["exclusion_reasons"]
    monkeypatch.setattr(s, "MAX_BUNDLE_BYTES", 999999)
    monkeypatch.setattr(s, "MAX_REFERENCE_TOKENS", 2)
    assert "numbered_bundle_exceeds_64000_reference_tokens" in s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]["exclusion_reasons"]


def test_evidence_tamper_rejected(tmp_path):
    save(tmp_path / "packages.json", [package(tmp_path)])
    row = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    decision = review(row)
    decision["features"][0]["evidence"][0]["quote"] = "Invented protective mechanism"
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {row["canonical_id"]: decision}})
    with pytest.raises(ValueError, match="quote differs"):
        s.screen_corpus(tmp_path, prior_roots=[], write=False)


def test_missing_source_requires_explicit_review(tmp_path):
    record = package(tmp_path)
    directory = tmp_path / record["source_dir"]
    with (directory / "SKILL.md").open("a", encoding="utf-8") as stream:
        stream.write("Read [the policy](references/policy.md) before sending records.\n")
    save(tmp_path / "packages.json", [record])
    row = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {row["canonical_id"]: review(row)}})
    actual = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    assert not actual["eligible"]
    assert "unreviewed_local_references" in actual["exclusion_reasons"]


def test_prior_identical_entry_excluded_even_if_extra_files(tmp_path):
    corpus, prior = tmp_path / "corpus", tmp_path / "prior"
    record = package(corpus)
    package(prior)
    (corpus / record["source_dir"] / "extra.md").write_text("New file", encoding="utf-8")
    save(corpus / "packages.json", [record])
    row = s.screen_corpus(corpus, prior_roots=[prior], write=False)["entries"][0]
    assert "prior_development_or_evaluation_exact_or_near_replica" in row["exclusion_reasons"]


def screening_rows(n=50):
    return [{"canonical_id": f"publisher{i:02d}/skill", "eligible": True, "physical_eligible": True,
             "semantic_screening_status": "source_reviewed", "near_fork_group": f"fork{i:02d}",
             "source_cluster": f"cluster{i // 3:02d}", "confirmed_features": list(s.FEATURES[:2])} for i in range(n)]


def test_seed_selection_constraints_and_no_relaxation(tmp_path):
    rows = screening_rows()
    rows[2]["near_fork_group"] = rows[1]["near_fork_group"]
    path = tmp_path / "screening.json"
    save(path, {"entries": rows})
    first = s.select_cases(tmp_path, path, write=False)
    second = s.select_cases(tmp_path, path, write=False)
    assert first == second
    assert first["status"] == "selection_complete_pending_human_reference"
    assert len(first["selected"]) == 24
    assert len(first["reserves"]) == 6
    assert len({r["near_fork_group"] for r in first["selected"] + first["reserves"]}) == 30
    assert len({r["source_cluster"] for r in first["selected"]}) >= 8
    assert max(__import__("collections").Counter(r["source_cluster"] for r in first["selected"] + first["reserves"]).values()) <= 3
    save(path, {"entries": rows[:5]})
    missing = s.select_cases(tmp_path, path, write=False)
    assert missing["status"] == "selection_incomplete"
    assert missing["automatic_relaxation"] is False
    assert "insufficient_eligible_cases" in missing["errors"]


def test_unreviewed_physical_candidates_prevent_final_selection(tmp_path):
    rows = screening_rows()
    rows[0].update(eligible=False, semantic_screening_status="pending_source_review")
    path = tmp_path / "screening.json"
    save(path, {"entries": rows})
    manifest = s.select_cases(tmp_path, path, write=False)
    assert len(manifest["selected"]) == 24
    assert manifest["status"] == "selection_incomplete"
    assert manifest["pending_source_reviews"] == [rows[0]["canonical_id"]]


def test_packets_do_not_mix_reference_and_source(tmp_path):
    save(tmp_path / "packages.json", [package(tmp_path)])
    first = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {first["canonical_id"]: review(first)}})
    s.screen_corpus(tmp_path, prior_roots=[])
    manifest = s.select_cases(tmp_path, case_count=1, reserve_count=0, min_clusters=1)
    packets = s.prepare_reference_packets(tmp_path, manifest)
    case = tmp_path / "reference-packets/real-001"
    reference = json.loads((case / "reference.template.json").read_text(encoding="utf-8"))
    draft = json.loads((case / "reference.source-facts-draft.json").read_text(encoding="utf-8"))
    assert reference["user_request"] is None
    assert reference["human_verified"] is False
    assert all(v["status"] == "pending" for v in reference["human_verifications"])
    assert draft["human_verified"] is False
    assert draft["implementation_choices"]
    assert draft["required_behavior"] == []
    assert "not assertions" in draft["draft_limitations"][0]
    assert draft["coverage_state"] == "source_facts_only_pending_semantic_reference"
    assert "human_verifications" not in (case / "source-bundle.txt").read_text(encoding="utf-8")
    assert packets["formal_target_model_calls"] == 0
    assert s.verify_reference_packets(tmp_path)["verified"]
    (case / "source/SKILL.md").write_text("Mutated", encoding="utf-8")
    assert not s.verify_reference_packets(tmp_path)["verified"]


def test_acquisition_source_view_excludes_generated_card(tmp_path):
    attempt = tmp_path / "items/0001-owner-skill/attempts/first"
    source = attempt / "files"
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("Original genuine source", encoding="utf-8")
    (source / "CARD.md").write_text("Generated scanner verdict GOLD CANARY", encoding="utf-8")
    save(attempt / "source-view.json", {"files": [
        {"path": "SKILL.md", "provenance": "source", "include_in_source": True},
        {"path": "CARD.md", "provenance": "registry_generated", "include_in_source": False}]})
    save(attempt / "result.json", {"status": "complete_verified", "identity": "owner/skill", "version_pin": "1.0"})
    save(tmp_path / "acquisition-index.json", [{"identity": "owner/skill", "status": "complete_verified", "result_path": (attempt / "result.json").relative_to(tmp_path).as_posix()}])
    report = s.screen_corpus(tmp_path, prior_roots=[], write=False)
    row = report["entries"][0]
    assert row["version"] == "1.0"
    assert next(f for f in row["inventory"] if f["path"] == "CARD.md")["kind"] == "registry_generated_metadata"


def test_source_bom_digest_matches_native_and_source_bytes(tmp_path):
    from skillflow.common.inputs.snapshot import inspect_input
    package(tmp_path)
    directory = tmp_path / "packages/writer/example"
    raw = b"\xef\xbb\xbf# Genuine source\r\nReturn {value}.\r\n"
    (directory / "SKILL.md").write_bytes(raw)
    inventory = s.source_inventory(directory)
    assert s.native_source_sha256(inventory["texts"]) == inspect_input(directory)[2]["source_sha256"]
    assert (directory / "SKILL.md").read_bytes() == raw


def test_screening_batch_conflicts_and_exclusion_evidence(tmp_path):
    batch = tmp_path / "selection/review-batches"
    save(batch / "a.json", {"decisions": {"owner/skill": {"decision": "include"}}})
    save(batch / "b.json", {"decisions": {"owner/skill": {"decision": "exclude"}}})
    with pytest.raises(ValueError, match="Conflicting"):
        s.merge_screening_batches(tmp_path)
    save(tmp_path / "packages.json", [package(tmp_path)])
    row = s.screen_corpus(tmp_path, prior_roots=[], write=False)["entries"][0]
    decision = review(row)
    decision["decision"] = "exclude"
    save(tmp_path / "selection/screening-decisions.json", {"decisions": {row["canonical_id"]: decision}})
    with pytest.raises(ValueError, match="exact source evidence"):
        s.screen_corpus(tmp_path, prior_roots=[], write=False)


def test_acquisition_incomplete_blocks_selection(tmp_path):
    path = tmp_path / "screening.json"
    save(path, {"entries": screening_rows(), "roster_coverage": {"complete": False}})
    manifest = s.select_cases(tmp_path, path, write=False)
    assert "acquisition_roster_not_fully_accounted" in manifest["errors"]
    with pytest.raises(ValueError, match="complete source screening"):
        s.prepare_reference_packets(tmp_path, manifest)


def test_shared_rule_bundle_groups_rewritten_entry_forks(tmp_path):
    records = [package(tmp_path, "author-a", "first", "\n".join(f"Alpha original instruction {i}" for i in range(210))),
               package(tmp_path, "author-b", "second", "\n".join(f"Beta rewritten procedure {i}" for i in range(210)))]
    for record in records:
        directory = tmp_path / record["source_dir"] / "rules"
        directory.mkdir()
        for index in range(8):
            (directory / f"rule-{index}.md").write_text((f"Shared operation source {index}. " * 20), encoding="utf-8")
    save(tmp_path / "packages.json", records)
    report = s.screen_corpus(tmp_path, prior_roots=[], write=False)
    a, b = report["entries"]
    assert a["entry_sha256"] != b["entry_sha256"]
    assert a["near_fork_group"] == b["near_fork_group"]
    assert a["source_cluster"] == b["source_cluster"]
    assert report["near_replica_pairs"][0]["source_file_hash_jaccard"] >= .8


def test_other_marketplace_metadata_requires_content_evidence(tmp_path):
    record = package(tmp_path)
    directory = tmp_path / record["source_dir"]
    path = directory / "_skillhub_meta.json"
    path.write_text('{"source":"marketplace","installedAt":123,"skillId":"skill-1","examples_en":["ANSWER CANARY"]}', encoding="utf-8")
    inventory = s.source_inventory(directory)
    assert "ANSWER CANARY" not in s.render_numbered_bundle(inventory["texts"])
    entry = next(f for f in inventory["files"] if f["path"] == "_skillhub_meta.json")
    assert entry["derived_view_exclusion"]["evidence"]["source"] == "marketplace"
    path.write_text('{"operational_parameter":"Preserve this value"}', encoding="utf-8")
    assert "Preserve this value" in s.render_numbered_bundle(s.source_inventory(directory)["texts"])


def test_binary_inventory_is_visible_without_binary_content(tmp_path):
    record = package(tmp_path)
    directory = tmp_path / record["source_dir"]
    (directory / "input.bin").write_bytes(b"\x00BINARY-CONTENT-CANARY")
    save(tmp_path / "packages.json", [record])
    inventory = s.source_inventory(directory)
    bundle = s.render_numbered_bundle(inventory["texts"], inventory["files"])
    assert "FILE input.bin | kind=binary | size=22 bytes | [binary content omitted]" in bundle
    assert "BINARY-CONTENT-CANARY" not in bundle
    report = s.screen_corpus(tmp_path, prior_roots=[], write=False)
    assert report["entries"][0]["bundle_bytes"] == len(bundle.encode("utf-8"))
    assert report["entries"][0]["bundle_sha256"] == s._sha(bundle.encode("utf-8"))


def test_verified_original_meta_referenced_by_source_is_not_filename_filtered(tmp_path):
    record = package(tmp_path)
    directory = tmp_path / record["source_dir"]
    (directory / "reader.py").write_text("Read '_meta.json' for the exact installed version.\n", encoding="utf-8")
    (directory / "_meta.json").write_text('{"ownerId":"o","slug":"example","version":"1","publishedAt":1}', encoding="utf-8")
    view = {"files": [{"path": name, "provenance": "source", "include_in_source": True}
                       for name in ("SKILL.md", "reader.py", "_meta.json")]}
    inventory = s.source_inventory(directory, view)
    assert "_meta.json" in inventory["texts"]
    assert next(f for f in inventory["files"] if f["path"] == "_meta.json")["derived_view_inclusion"]
    (directory / "_meta.json").write_text('{"operational_setting":"Keep this genuine source"}', encoding="utf-8")
    assert "Keep this genuine source" in s.render_numbered_bundle(s.source_inventory(directory, view)["texts"])


def test_root_frontmatter_upstreams_are_uniform_exact_and_source_preserving():
    entry = "\n".join([
        "---", "name: genuine-source", "homepage: 'https://github.com/Owner/Repo.git#readme'",
        'metadata: {"clawdbot":{"repository":"https://github.com/Other/Origin"}}',
        "source: https://github.com/Library/Docs/blob/main/example.md", "---",
        "Original 中文 source.", "homepage: https://github.com/Body/Unrelated",
        "Read https://github.com/Dependency/Library documentation.",
    ])
    texts = {"SKILL.md": entry}
    origins = s.repository_origins(texts, {})
    assert {o["repository"] for o in origins} == {"github.com/owner/repo", "github.com/other/origin"}
    assert all(o["basis"] == "author_declared_root_frontmatter" for o in origins)
    assert {o["field"] for o in origins} == {"homepage", "metadata.clawdbot.repository"}
    for origin in origins:
        s.validate_evidence(texts, origin["evidence"])
    assert texts["SKILL.md"] == entry
    assert not s.repository_origins({"SKILL.md": "---\nhomepage: https://github.com/Owner/Repo/tree/main\n---\n"}, {})
