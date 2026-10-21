"""Prospective selection uses synthetic sources and no target or reference data."""
from copy import deepcopy
import json
from pathlib import Path
import random
import re

import pytest

from tools.doe.real_comparison import long_selection as selector
from tools.doe.real_comparison import selection as old
from tools.doe.real_comparison.protocol import sha256, write_json


FEATURES = ["conditions_or_retries", "versions_or_transformations", "persistence_or_cross_session"]


@pytest.fixture
def build(tmp_path, monkeypatch):
    class Encoding:
        def encode(self, text, disallowed_special=()):
            return range(int(re.search(r"tokens=(\d+)", text)[1]))
    monkeypatch.setattr(old, "reference_tokenizer", lambda: (Encoding(), {"synthetic": True}))

    def make(count=35, reviewed=None, *, tokens=None, selected=24, reserves=6, minimum_clusters=8,
             groups=None, extra_files=False, code=None):
        corpus, proposal = tmp_path / "corpus", tmp_path / "prospective"
        rows = []
        for index in range(count):
            root = corpus / "items" / f"source-{index:03d}"
            source = root / "files"
            source.mkdir(parents=True)
            token_count = (tokens or {}).get(index, 20000)
            text = (f"# Synthetic entry tokens={token_count}\nRead scripts/main.py for the actual operation.\n"
                "If the input is present, retain its source reference.\nNormalize the requested value before output.\nPersist the selected result only when requested.\n")
            if extra_files:
                text += "\n".join(f"Use guide{n}.md for operation {n}." for n in range(7)) + "\n"
            (source / "SKILL.md").write_text(text, encoding="utf-8")
            (source / "scripts").mkdir()
            (source / "scripts/main.py").write_text(code or "\n".join(f"value_{n} = {n}" for n in range(600)) + "\n", encoding="utf-8")
            if extra_files:
                for n in range(7):
                    (source / f"guide{n}.md").write_text(f"# Operation {n}\nRead the input and preserve its required value.\n", encoding="utf-8")
            members = [{"path": p.relative_to(source).as_posix(), "sha256": sha256(p), "size": p.stat().st_size,
                "provenance": "source", "include_in_source": True, "reason": "Synthetic original member."}
                for p in sorted(source.rglob("*")) if p.is_file()]
            view = root / "source-view.json"
            write_json(view, {"files": members})
            inventory = old.source_inventory(source, {"files": members})
            bundle = old.render_numbered_bundle(inventory["texts"], inventory["files"]).encode("utf-8")
            cluster, fork = (groups or {}).get(index, (f"cluster-{index}", f"fork-{index}"))
            rows.append({"canonical_id": f"synthetic/source-{index:03d}", "version": "1.0.0", "rank": index + 1,
                "eligible": True, "source_dir": source.relative_to(corpus).as_posix(),
                "source_view_path": view.relative_to(corpus).as_posix(), "source_dir_absolute": str(source),
                "source_sha256": old.native_source_sha256(inventory["texts"]),
                "source_tree_sha256": inventory["source_tree_sha256"], "bundle_sha256": old._sha(bundle),
                "reference_tokens": token_count, "bundle_bytes": len(bundle), "source_cluster": cluster, "near_fork_group": fork})
        screening = corpus / "screening-report.json"
        previous = corpus / "selection-manifest.json"
        write_json(screening, {"entries": rows})
        write_json(previous, {"state": "Historical manifest must remain unchanged.", "selected": []})
        queue = sorted([r for r in rows if 20000 <= r["reference_tokens"] <= 64000 and r["bundle_bytes"] <= 262144], key=lambda r: r["canonical_id"])
        random.Random(20261020).shuffle(queue)
        queue = [{**r, "queue_index": n} for n, r in enumerate(queue, 1)]
        rules = {"seed": 20261020, "candidate_gate": {"minimum_reference_tokens_inclusive": 20000,
            "maximum_reference_tokens_inclusive": 64000, "maximum_numbered_bundle_bytes_inclusive": 262144},
            "feature_criterion": {"allowed_features": FEATURES, "minimum_source_confirmed_distinct_features": 3},
            "selection_plan": {"requested_cases": selected, "requested_reserves": reserves,
                "max_per_near_fork_group": 1, "max_per_source_cluster": 3, "minimum_selected_source_clusters": minimum_clusters},
            "evidence_inputs": [{"path": str(path), "sha256": sha256(path)} for path in (screening, previous)]}
        write_json(proposal / "rules.json", rules)
        write_json(proposal / "candidate-queue.json", {"candidate_count": len(queue), "candidates": queue})
        write_json(proposal / "rules-freeze.json", {"files": {name: sha256(proposal / name) for name in ("rules.json", "candidate-queue.json")}})
        reviews = []
        for item in queue[:len(queue) if reviewed is None else reviewed]:
            root = corpus / item["source_dir"]
            inventory = old.source_inventory(root)
            lines = inventory["texts"]["scripts/main.py"].splitlines()
            numbers, _ = selector.conservative_lines(inventory["texts"]["scripts/main.py"], "scripts/main.py")
            evidence = [{"path": "SKILL.md", "start_line": n, "end_line": n,
                "quote": inventory["texts"]["SKILL.md"].splitlines()[n - 1]} for n in (3, 4, 5)]
            reviews.append({"queue_index": item["queue_index"], "canonical_id": item["canonical_id"], "decision": "include",
                "reason": "Synthetic source-only positive operative and feature proof.",
                "reviewed_files": [{"path": f["path"], "sha256": f["sha256"]} for f in inventory["files"]],
                "source_closure": {"status": "complete_for_static_audit"},
                "features": [{"feature": feature, "reason": "The exact synthetic source clause establishes this feature.",
                    "evidence": [evidence[n]]} for n, feature in enumerate(FEATURES)],
                "complexity_basis": {"nonempty_lines": len(numbers), "counted_spans": [{"path": "scripts/main.py",
                    "start_line": 1, "end_line": len(lines), "operative_nonempty_lines": len(numbers),
                    "counted_physical_line_numbers": sorted(numbers)}]}})
        write_json(proposal / "reviews/batch-a.json", reviews)
        return proposal, corpus, queue, reviews, previous
    return make


def save_reviews(proposal, reviews):
    write_json(proposal / "reviews/batch-a.json", reviews)


def test_fixed_order_selects_24_and_six_without_sealing_or_changing_sources(build):
    proposal, corpus, queue, _, previous = build()
    before = {p: p.read_bytes() for p in corpus.rglob("*") if p.is_file()}
    first = selector.select_long_cases(proposal, corpus)
    second = selector.select_long_cases(proposal, corpus)
    assert first == second and first["status"] == "selection_complete_pending_human_reference"
    assert len(first["selected"]) == 24 and len(first["reserves"]) == 6
    assert [r["canonical_id"] for r in first["selected"] + first["reserves"]] == [r["canonical_id"] for r in queue[:30]]
    assert {p: p.read_bytes() for p in before} == before
    assert previous.read_bytes() == before[previous]
    assert first["formal_target_calls"] == 0 and first["final_seal"] is False and first["root_audit_required"]


def test_inclusive_length_bounds_and_long_source_byte_gate(build):
    proposal, corpus, queue, _, _ = build(count=6, tokens={0: 19999, 1: 20000, 2: 64000, 3: 64001})
    assert {r["rank"] for r in queue} == {2, 3, 5, 6}
    result = selector.select_long_cases(proposal, corpus)
    assert result["accepted_count"] == 4 and result["status"] == "insufficient_eligible_candidates"


def test_missing_prefix_review_cannot_be_skipped_for_later_completed_reviews(build):
    proposal, corpus, queue, reviews, _ = build()
    save_reviews(proposal, [r for r in reviews if r["queue_index"] != 4])
    result = selector.select_long_cases(proposal, corpus)
    assert result["status"] == "needs_more_review" and result["first_blocked_queue_index"] == 4
    assert result["accepted_count"] == 3 and result["shortfall"] == 27
    assert result["available_review_count"] == 34


def test_unresolved_decision_is_retained_without_consuming_group_slots(build):
    proposal, corpus, queue, reviews, _ = build(count=3, selected=2, reserves=1, minimum_clusters=1)
    reviews[0]["decision"] = "unresolved"
    reviews[0]["reason"] = "The current positive scope is incomplete; an old minimum is not a failure proof."
    reviews[0]["complexity_basis"] = {"reason": reviews[0]["reason"]}
    save_reviews(proposal, reviews)
    result = selector.select_long_cases(proposal, corpus)
    assert result["accepted_count"] == 2 and result["shortfall"] == 1
    assert result["prefix_decisions"][0]["decision"] == "unresolved"


def test_combined_group_caps_apply_to_reserves_without_reshuffling(build):
    proposal, corpus, queue, reviews, _ = build(count=8, selected=3, reserves=2, minimum_clusters=1)
    # Update the frozen synthetic screen and queue together before the test run.
    for item in queue:
        item["source_cluster"] = "cluster-a" if item["queue_index"] <= 4 else "cluster-b"
    queue[1]["near_fork_group"] = queue[0]["near_fork_group"]
    queue[4]["near_fork_group"] = queue[0]["near_fork_group"]
    screening = selector.read(corpus / "screening-report.json")
    by_id = {r["canonical_id"]: r for r in queue}
    for item in screening["entries"]:
        item.update(source_cluster=by_id[item["canonical_id"]]["source_cluster"], near_fork_group=by_id[item["canonical_id"]]["near_fork_group"])
    write_json(corpus / "screening-report.json", screening)
    rules = selector.read(proposal / "rules.json")
    rules["evidence_inputs"][0]["sha256"] = sha256(corpus / "screening-report.json")
    write_json(proposal / "rules.json", rules)
    write_json(proposal / "candidate-queue.json", {"candidate_count": len(queue), "candidates": queue})
    write_json(proposal / "rules-freeze.json", {"files": {n: sha256(proposal / n) for n in ("rules.json", "candidate-queue.json")}})
    result = selector.select_long_cases(proposal, corpus)
    assert [r["queue_index"] for r in result["selected"] + result["reserves"]] == [1, 3, 4, 6, 7]
    assert result["prefix_decisions"][1]["decision"] == "near_fork_group_cap"
    assert result["prefix_decisions"][4]["decision"] == "near_fork_group_cap"


@pytest.mark.parametrize("change", ["nested_quote", "file_hash", "identity", "missing_positive_proof", "duplicate_feature"])
def test_tampered_quotes_identity_hashes_and_missing_positive_proof_stop_the_prefix(build, change):
    proposal, corpus, _, reviews, _ = build(count=2)
    if change == "nested_quote":
        reviews[0]["source_closure"]["nested"] = {"path": "SKILL.md", "start_line": 3, "end_line": 3, "quote": "An invented quotation."}
    elif change == "file_hash":
        reviews[0]["reviewed_files"][0]["sha256"] = "invented-hash"
    elif change == "identity":
        reviews[0]["canonical_id"] = "synthetic/different-source"
    elif change == "missing_positive_proof":
        reviews[0]["complexity_basis"] = {"old_minimum": 200}
    else:
        reviews[0]["features"][2] = deepcopy(reviews[0]["features"][0])
    save_reviews(proposal, reviews)
    result = selector.select_long_cases(proposal, corpus)
    assert result["status"] == "needs_review_correction" and result["first_blocked_queue_index"] == 1
    assert result["accepted_count"] == 0


def test_source_byte_tamper_is_rejected_even_when_the_review_quote_is_unchanged(build):
    proposal, corpus, queue, _, _ = build(count=1)
    path = corpus / queue[0]["source_dir"] / "scripts/main.py"
    path.write_bytes(path.read_bytes() + b"unreviewed_value = 1\n")
    result = selector.validate_reviews(proposal, corpus)
    assert result["status"] == "needs_review_correction"
    assert "acquisition view" in result["errors"][0]["errors"][0]


def test_punctuation_count_discrepancy_is_reported_without_rewriting_the_review(build):
    code = "\n".join(f"value_{n} = {n}" for n in range(600)) + "\n(\n)\n"
    proposal, corpus, _, reviews, _ = build(count=1, code=code)
    proof = reviews[0]["complexity_basis"]
    proof["nonempty_lines"] = 602
    proof["counted_spans"][0].update(operative_nonempty_lines=602, counted_physical_line_numbers=list(range(1, 603)))
    save_reviews(proposal, reviews)
    before = (proposal / "reviews/batch-a.json").read_bytes()
    result = selector.validate_reviews(proposal, corpus)
    assert result["reviews"][0]["review_decision"] == "include"
    discrepancy = result["reviews"][0]["count_discrepancies"][0]
    assert discrepancy["declared"] == 602 and discrepancy["mechanically_confirmed"] == 600
    assert [r["reason"] for r in discrepancy["rejected_nominated_lines"]] == ["syntax_only_punctuation"] * 2
    assert (proposal / "reviews/batch-a.json").read_bytes() == before


def test_second_count_format_and_value_definitions_are_preserved(build):
    code = '"""Module documentation.\nNo operational count.\n"""\n# Standalone comment.\n\n' + "\n".join(f"value_{n} = {n}" for n in range(600)) + '\noutput = """\nPreserve this required output definition.\n"""\n'
    proposal, corpus, _, reviews, _ = build(count=1, code=code)
    count, _ = selector.conservative_lines(code, "scripts/main.py")
    reviews[0]["basis"] = {"operative_nonempty_lines": len(count), "counted_spans": [{"path": "scripts/main.py",
        "start_line": 1, "end_line": len(code.splitlines()), "operative_nonempty_lines": len(count),
        "excluded_all_blank_lines": True, "excluded_docstring_spans": [{"start_line": 1, "end_line": 3}],
        "excluded_comment_line_numbers": [4]}]}
    del reviews[0]["complexity_basis"]
    save_reviews(proposal, reviews)
    result = selector.validate_reviews(proposal, corpus)
    assert result["reviews"][0]["eligible"]
    assert result["reviews"][0]["line_proof"]["confirmed_operative_nonempty_lines"] == 602


def test_eight_file_proof_requires_entry_connected_paths_and_exact_local_edges(build):
    proposal, corpus, queue, reviews, _ = build(count=1, extra_files=True)
    text = (corpus / queue[0]["source_dir"] / "SKILL.md").read_text(encoding="utf-8").splitlines()
    basis = {"confirmed_file_count": 8, "operative_files": ["SKILL.md"] + [f"guide{n}.md" for n in range(7)],
        "reference_edges": [{"source": "SKILL.md", "target": f"guide{n}.md", "evidence": [{"path": "SKILL.md",
            "start_line": n + 6, "end_line": n + 6, "quote": text[n + 5]}]} for n in range(7)]}
    reviews[0]["complexity_basis"] = basis
    save_reviews(proposal, reviews)
    assert selector.validate_reviews(proposal, corpus)["reviews"][0]["eligible"]
    basis["reference_edges"][-1]["target"] = "missing-guide.md"
    save_reviews(proposal, reviews)
    assert selector.validate_reviews(proposal, corpus)["reviews"][0]["errors"]


def test_hash_bound_supersession_is_required_and_preserves_every_version(build):
    proposal, corpus, _, reviews, _ = build(count=1)
    replacement = {"reviews": reviews, "recounts_prior_review": "batch-a.json"}
    write_json(proposal / "reviews/batch-b.json", replacement)
    with pytest.raises(ValueError, match="exact predecessor"):
        selector.validate_reviews(proposal, corpus)
    replacement["recounts_prior_review_sha256"] = sha256(proposal / "reviews/batch-a.json")
    write_json(proposal / "reviews/batch-b.json", replacement)
    result = selector.validate_reviews(proposal, corpus)
    assert result["reviews"][0]["effective_review_file"] == "reviews/batch-b.json"
    assert len(result["reviews"][0]["review_versions"]) == 2
    assert (proposal / "reviews/batch-a.json").exists()


def test_shortfall_and_insufficient_selected_clusters_do_not_relax_rules(build):
    proposal, corpus, _, _, _ = build(count=3, selected=2, reserves=1, minimum_clusters=4)
    result = selector.select_long_cases(proposal, corpus)
    assert result["status"] == "insufficient_selected_source_clusters"
    assert result["thresholds_relaxed"] is False and result["final_seal"] is False


def test_supporting_manifest_connector_is_rooted_but_never_receives_operative_credit():
    modules = [f"src/module{n}.js" for n in range(6)]
    operative = ["src/index.js", "hooks/request-before.js"] + modules
    texts = {"SKILL.md": "Read README.md for the current setup.\n", "README.md": "npm run setup\n",
        "package.json": json.dumps({"scripts": {"setup": "node setup.js"}, "main": "src/index.js",
            "hooks": {"before": "hooks/request-before.js"}}, indent=2),
        "hooks/request-before.js": "import { manager } from '../src/index.js';\n",
        "src/index.js": "\n".join(f"import {{ value{n} }} from './module{n}.js';" for n in range(6)) + "\n",
        **{path: f"export const value{n} = {n};\n" for n, path in enumerate(modules)}}
    def edge(source, target, number=1):
        return {"source": source, "target": target, "evidence": [{"path": source,
            "start_line": number, "end_line": number, "quote": texts[source].splitlines()[number - 1]}]}
    package_lines = texts["package.json"].splitlines()
    main_line = next(n for n, line in enumerate(package_lines, 1) if '"main"' in line)
    hook_line = next(n for n, line in enumerate(package_lines, 1) if '"before"' in line)
    edges = [edge("SKILL.md", "README.md"), edge("README.md", "package.json"),
        edge("package.json", "src/index.js", main_line), edge("package.json", "hooks/request-before.js", hook_line)]
    edges += [edge("src/index.js", path, n + 1) for n, path in enumerate(modules)]
    basis = {"operative_files": operative, "count": 8, "reference_edges": edges}
    inventory = {"texts": texts, "files": [{"path": path, "kind": "supporting_text" if path == "package.json" else "operational_text"} for path in texts]}
    selector._nested_quotes(basis, texts)
    result = selector._file_proof(basis, inventory)
    assert result["threshold_met"] and len(result["connected_operative_files"]) == 8
    assert result["supporting_connectors_without_operative_credit"] == ["README.md", "SKILL.md", "package.json"]
    wrong = deepcopy(basis)
    wrong["reference_edges"][1]["evidence"][0]["quote"] = "npm run missing-command"
    with pytest.raises(ValueError, match="local target"):
        selector._file_proof(wrong, inventory)
    detached = deepcopy(basis)
    detached["reference_edges"].pop()
    with pytest.raises(ValueError, match="disconnected"):
        selector._file_proof(detached, inventory)
    manifest_credit = deepcopy(basis)
    manifest_credit["operative_files"][-1] = "package.json"
    with pytest.raises(ValueError, match="support-only"):
        selector._file_proof(manifest_credit, inventory)


@pytest.mark.parametrize("source,target,supported", [
    ("README.md", "package.json", True),
    ("sub/README.md", "sub/package.json", True),
    ("README.md", "unrelated/package.json", False),
    ("sub/README.md", "package.json", False),
])
def test_npm_connector_requires_the_local_manifest_identity(source, target, supported):
    text = "npm run setup"
    inventory = {source: text, target: json.dumps({"scripts": {"setup": "node setup.js"}})}
    evidence = [{"path": source, "start_line": 1, "end_line": 1, "quote": text}]
    assert selector._edge_target_supported(source, target, evidence, inventory) is supported


@pytest.mark.parametrize("scripts", [None, [], "setup", {"setup": None}, {"setup": []},
                                     {"setup": True}, {"setup": ""}, {"setup": "  "}])
def test_npm_connector_rejects_malformed_or_empty_script_definitions(scripts):
    evidence = [{"path": "README.md", "start_line": 1, "end_line": 1, "quote": "npm run setup"}]
    texts = {"package.json": json.dumps({"scripts": scripts})}
    assert not selector._edge_target_supported("README.md", "package.json", evidence, texts)


@pytest.mark.parametrize("quote", ["cd unrelated && npm run setup", "Do not run npm run setup",
                                  "npm run setup.prod", "npm run setup --prefix unrelated"])
def test_implicit_npm_connector_requires_a_complete_isolated_command(quote):
    evidence = [{"path": "README.md", "start_line": 1, "end_line": 1, "quote": quote}]
    texts = {"package.json": json.dumps({"scripts": {"setup": "node setup.js"}})}
    assert not selector._edge_target_supported("README.md", "package.json", evidence, texts)


@pytest.mark.parametrize("source_directory", ["/unrelated/templates", "~/.tool/templates", "templates"])
def test_recursive_copy_directory_does_not_prove_individual_local_file_identity(source_directory):
    evidence = [{"path": "README.md", "start_line": 1, "end_line": 1,
                 "quote": f"cp -r {source_directory} destination"}]
    assert not selector._edge_target_supported("README.md", "templates/item.txt", evidence,
                                              {"templates/item.txt": "Unrelated source content."})


def test_text_asset_keywords_do_not_replace_explicit_operative_content_evidence():
    texts = {"SKILL.md": "Do not read assets/item.txt; it is illustrative only.\n",
             "assets/item.txt": "Use the supplied value in this output template.\n"}
    edge = {"source": "SKILL.md", "target": "assets/item.txt", "evidence": [{
        "path": "SKILL.md", "start_line": 1, "end_line": 1, "quote": texts["SKILL.md"].strip()}]}
    basis = {"operative_files": ["assets/item.txt"], "count": 1, "reference_edges": [edge]}
    inventory = {"texts": texts, "files": [{"path": path,
        "kind": "text_asset" if path.startswith("assets/") else "operational_text"} for path in texts]}
    selector._nested_quotes(basis, texts)
    with pytest.raises(ValueError, match="explicit operative"):
        selector._file_proof(basis, inventory)
    texts["SKILL.md"] = "Use assets/item.txt as the required output template.\n"
    edge["evidence"][0]["quote"] = texts["SKILL.md"].strip()
    basis["operative_content_evidence"] = [{"path": "assets/item.txt", "start_line": 1,
        "end_line": 1, "quote": texts["assets/item.txt"].strip()}]
    selector._nested_quotes(basis, texts)
    assert selector._file_proof(basis, inventory)["connected_operative_files"] == ["assets/item.txt"]


@pytest.mark.parametrize("change", [
    {"path": "./SKILL.md"}, {"path": "folder\\SKILL.md"}, {"path": "folder//SKILL.md"},
    {"start_line": True}, {"end_line": True},
])
def test_source_quote_coordinates_are_canonical_physical_references(change):
    evidence = {"path": "SKILL.md", "start_line": 1, "end_line": 1, "quote": "Original source."}
    evidence.update(change)
    with pytest.raises(ValueError, match="noncanonical"):
        selector._nested_quotes(evidence, {"SKILL.md": "Original source."})


@pytest.mark.parametrize("path", ["./main.py", "src\\main.py", "src//main.py"])
def test_counted_spans_reject_noncanonical_file_identity(path):
    span = {"path": path, "start_line": 1, "end_line": 1, "operative_nonempty_lines": 1,
            "counted_physical_line_numbers": [1]}
    with pytest.raises(ValueError, match="exact portable"):
        selector._count_proof({"counted_spans": [span]}, {"main.py": "value = 1"})
