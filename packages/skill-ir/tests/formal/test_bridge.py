"""The bridge is a trusted boundary; test facts that could hide graph failures."""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import sys

import pytest

FORMAL = Path(__file__).resolve().parents[2] / "formal"
sys.path.insert(0, str(FORMAL / "tools"))

from bridge import parse_fields, project_raw, python_accept
from cases import Case, fixtures, random_cases, recorded_cases, renamed, topology_cases
import cases as case_tools
import differential


FIXTURES = fixtures()
BY_NAME = {case.name: case for case in FIXTURES}


@pytest.mark.parametrize("case", FIXTURES, ids=lambda case: case.name)
def test_rule_fixture_is_independently_labeled(case):
    assert python_accept(case.cfg)[0] is case.expected
    if case.expected_domain == "schema":
        with pytest.raises(ValueError):
            parse_fields(case.cfg)
    else:
        # Structural rejection must not accidentally be hidden by a field gate.
        assert project_raw(case.cfg)["blocks"] or case.name == "empty-graph"


def test_projection_keeps_duplicate_result_and_instruction_occurrences():
    cfg = deepcopy(BY_NAME["local-result-order"].cfg)
    items = cfg["blocks"]["A"]["instructions"]
    items[0]["outputs"].append(deepcopy(items[0]["outputs"][0]))
    items[1]["id"] = items[0]["id"]
    projected = project_raw(cfg)["blocks"][0]["instructions"]
    assert len(projected) == 3
    assert len(projected[0]["outputs"]) == 2
    assert projected[0]["outputs"][0] == projected[0]["outputs"][1]
    assert projected[0]["id"] == projected[1]["id"]
    assert python_accept(cfg)[0] is False


def test_projection_keeps_dangling_references_distinct_and_block_key_mismatch():
    cfg = deepcopy(BY_NAME["cross-block-result"].cfg)
    cfg["blocks"]["A"]["block_id"] = "mismatched"
    cfg["blocks"]["B"]["instructions"][0]["inputs"] = [{"type": "result", "identifier": "undefined"}]
    cfg["edges"][0]["target_block_id"] = "dangling"
    projection = project_raw(cfg)
    a, b = projection["blocks"]
    assert len({a["key"], a["id"], b["key"], projection["edges"][0]["target"]}) == 4
    assert a["instructions"][0]["outputs"][0]["id"] != b["instructions"][0]["inputs"][0]["id"]


def test_projection_preserves_edge_multiplicity_and_normalized_conditions():
    cfg = deepcopy(BY_NAME["guard-with-input"].cfg)
    cfg["edges"] += [dict(cfg["edges"][0], condition_text=" yes "), dict(cfg["edges"][0], condition_text="no")]
    projection = project_raw(cfg)
    assert [edge["condition"] for edge in projection["edges"]] == ["yes", "yes", "no"]
    assert len(projection["edges"]) == 3
    assert python_accept(cfg)[0] is False


def test_instruction_order_remains_semantic_while_block_storage_order_does_not():
    cfg = deepcopy(BY_NAME["local-result-order"].cfg)
    items = cfg["blocks"]["A"]["instructions"]
    items[0], items[1] = items[1], items[0]
    projected = project_raw(cfg)["blocks"][0]["instructions"]
    assert projected[0]["inputs"] and not projected[0]["outputs"]
    assert projected[1]["outputs"] and not projected[1]["inputs"]
    assert python_accept(cfg)[0] is False
    cfg = deepcopy(BY_NAME["cross-block-result"].cfg)
    cfg["blocks"] = dict(reversed(list(cfg["blocks"].items())))
    projection = project_raw(cfg)
    assert projection["blocks"][0]["instructions"][-1]["opcode"] == "return"
    assert python_accept(cfg)[0] is True


def test_projection_contains_facts_and_no_python_rule_decisions():
    core = project_raw(BY_NAME["context-source"].cfg)
    assert set(core) == {"entry", "blocks", "edges", "contexts"}
    assert set(core["blocks"][0]) == {"key", "id", "source", "instructions"}
    assert core["contexts"] == ["request"]
    assert core["blocks"][0]["instructions"][0]["inputs"] == [{"kind": "context", "id": "request"}]


def test_generators_are_deterministic_and_cover_all_small_directed_graphs():
    assert list(random_cases(seed=17, count=12)) == list(random_cases(seed=17, count=12))
    assert list(random_cases(seed=17, count=12)) != list(random_cases(seed=18, count=12))
    generated = list(topology_cases(2))
    assert len(generated) == 2 * (2 ** 1 + 2 ** 4)
    assert any(case.cfg["edges"] and case.cfg["edges"][0]["source_block_id"] == case.cfg["edges"][0]["target_block_id"] for case in generated)


@pytest.mark.parametrize("case", [c for c in FIXTURES if c.expected_domain == "core"], ids=lambda c: c.name)
def test_consistent_renaming_preserves_graph_decision(case):
    assert python_accept(renamed(case.cfg))[0] is case.expected


def test_recorded_source_uses_hash_bound_analysis_not_render_dump(tmp_path):
    manifest = {"samples": []}
    actual = BY_NAME["single-return"].cfg
    for index in range(1, 31):
        path = tmp_path / f"analysis-{index}.json"
        path.write_text(json.dumps({"cfg": actual}), encoding="utf-8")
        manifest["samples"].append({"index": index, "sample_id": "F03" if index == 15 else f"T{index}",
                                    "repetition": 3 if index == 15 else 1,
                                    "analysis_path": str(path), "analysis_sha256": differential.file_hash(path),
                                    "cfg": {"this": "must never be read as the actual CFG"}})
    path = tmp_path / "render-input.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    cases = recorded_cases(path)
    assert len(cases) == 30
    assert all(case.cfg == actual for case in cases)
    Path(manifest["samples"][0]["analysis_path"]).write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        recorded_cases(path)


def test_fixed_review_manifest_preserves_all_identities_repetitions_and_hashes():
    manifest_path = FORMAL / "fixtures" / "review30.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["path_base"] == "repository"
    expected_ids = [f"{prefix}{number:02d}" for prefix in "NQFDR" for number in range(1, 7)]
    assert [sample["index"] for sample in manifest["samples"]] == list(range(1, 31))
    assert [sample["sample_id"] for sample in manifest["samples"]] == expected_ids
    assert [sample["repetition"] for sample in manifest["samples"]] == [3 if index == 15 else 1 for index in range(1, 31)]
    assert all(set(sample) == {"index", "sample_id", "repetition", "analysis_sha256", "analysis_path", "basename"} for sample in manifest["samples"])
    assert all(not Path(sample["analysis_path"]).is_absolute() for sample in manifest["samples"])
    recorded = recorded_cases(manifest_path)
    for sample, case in zip(manifest["samples"], recorded):
        source = case_tools.REPOSITORY_ROOT / sample["analysis_path"]
        assert differential.file_hash(source) == sample["analysis_sha256"]
        assert case.cfg == json.loads(source.read_text(encoding="utf-8"))["cfg"]
        assert case.provenance["analysis_sha256"] == sample["analysis_sha256"]
        assert case.provenance["manifest_sha256"] == differential.file_hash(manifest_path)


def test_repository_manifest_resolves_in_a_different_checkout_and_working_directory(tmp_path, monkeypatch):
    alternate_root = tmp_path / "another-checkout"
    analysis = alternate_root / "records" / "analysis.json"
    analysis.parent.mkdir(parents=True)
    analysis.write_text(json.dumps({"cfg": BY_NAME["single-return"].cfg}), encoding="utf-8")
    manifest = json.loads((FORMAL / "fixtures" / "review30.json").read_text(encoding="utf-8"))
    for sample in manifest["samples"]:
        sample["analysis_path"] = "records/analysis.json"
        sample["analysis_sha256"] = differential.file_hash(analysis)
    selected = alternate_root / "formal" / "review30.json"
    selected.parent.mkdir()
    selected.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(case_tools, "REPOSITORY_ROOT", alternate_root)
    monkeypatch.chdir(tmp_path)
    recorded = recorded_cases(selected)
    assert len(recorded) == 30
    assert all(Path(case.provenance["analysis_path"]) == analysis for case in recorded)
    assert all(case.provenance["manifest_analysis_path"] == "records/analysis.json" for case in recorded)
    versions = differential.source_versions(None, ["portable-check"], [selected])
    assert versions["input_manifests"] == [{"path": str(selected), "sha256": differential.file_hash(selected)}]
    manifest["samples"][0]["analysis_path"] = "../outside.json"
    selected.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="stay inside repository"):
        recorded_cases(selected)


def test_minimizer_retains_predicate_and_reports_deletion_bound():
    cfg = deepcopy(BY_NAME["cross-block-result"].cfg)
    minimized, stats = differential.minimize(cfg, lambda value: "A" in value["blocks"])
    assert "A" in minimized["blocks"]
    assert minimized["edges"] == []
    assert len(minimized["blocks"]) == 1
    assert minimized["blocks"]["A"]["instructions"] == []
    assert stats["deletion_minimal"] is True
    _, bounded = differential.minimize(cfg, lambda value: True, max_checks=1)
    assert bounded["budget_exhausted"] is True


def test_schema_rejection_is_never_sent_to_or_counted_as_lean_rejection(tmp_path, monkeypatch):
    # This stub tests only report plumbing; it is explicitly not Lean evidence.
    stub = tmp_path / "plumbing-stub"
    stub.write_text("not a checker", encoding="utf-8")
    seen = []

    def responses(_checker, projections, timeout=60):
        seen.extend(projections)
        return [{"accept": True} for _ in projections]

    monkeypatch.setattr(differential, "checker_results", responses)
    report = differential.run([BY_NAME["single-return"], BY_NAME["explicit-nonliteral-null"]], tmp_path / "report", stub)
    assert len(seen) == 1
    assert report["counts"]["schema_rejected"] == 1
    assert report["counts"]["lean_evaluated"] == 1
    assert report["counts"]["lean_rejected"] == 0
    schema = report["records"][1]
    assert schema["lean_accept"] is None and schema["lean_evaluated"] is False


def test_mismatch_is_saved_with_replayable_reduction_and_attestation(tmp_path, monkeypatch):
    stub = tmp_path / "plumbing-stub"
    stub.write_text("not a checker", encoding="utf-8")
    monkeypatch.setattr(differential, "checker_results", lambda _checker, projections: [{"accept": False} for _ in projections])
    report = differential.run([BY_NAME["single-return"]], tmp_path / "out", stub)
    assert report["status"] == "failed"
    record = report["records"][0]
    assert record["comparison"] == "disagree"
    replay = json.loads(Path(record["counterexample_file"]).read_text(encoding="utf-8"))
    assert Case(**replay).family == "counterexample"
    assert replay["provenance"]["replay_command_argv"]
    assert replay["provenance"]["reduced_input_sha256"]
    attestation = json.loads((tmp_path / "out" / "attestation.json").read_text(encoding="utf-8"))
    assert attestation["report_sha256"] == differential.file_hash(tmp_path / "out" / "report.json")


def test_prepare_only_cannot_claim_differential_pass(tmp_path):
    report = differential.run([BY_NAME["single-return"]], tmp_path, None)
    assert report["status"] == "prepared-not-checked"
    assert report["counts"]["lean_evaluated"] == 0


def test_attestation_binds_build_configuration_and_pinned_toolchain():
    versions = differential.source_versions(None, ["test-attestation"])
    for filename in ("lakefile.toml", "lean-toolchain"):
        key = f"packages/skill-ir/formal/{filename}"
        assert versions["source_sha256"][key] == differential.file_hash(FORMAL / filename)
    assert versions["source_sha256"]["packages/skill-ir/formal/fixtures/review30.json"] == differential.file_hash(FORMAL / "fixtures" / "review30.json")


def test_lean_rule_fixtures_when_checker_is_available():
    configured = os.environ.get("SKILL_IR_LEAN_CHECKER")
    candidates = [Path(configured)] if configured else [FORMAL / ".lake" / "build" / "bin" / "skill_ir_check.exe", FORMAL / ".lake" / "build" / "bin" / "skill_ir_check"]
    checker = next((path for path in candidates if path.is_file()), None)
    if checker is None:
        pytest.skip("Lean optional integration: set SKILL_IR_LEAN_CHECKER or build the formal checker")
    core_cases = [case for case in FIXTURES if case.expected_domain == "core"]
    outcomes = differential.checker_results(checker, [project_raw(case.cfg) for case in core_cases])
    for case, outcome in zip(core_cases, outcomes):
        assert outcome == {"accept": case.expected}, case.name
