"""Offline approval/snapshot checks, independent of live production revisions."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from skill_ir.inputs.skill_package import load_skill_package


BASE = Path(__file__).resolve().parents[2] / "experiments" / "semantics_baseline"
SPEC = importlib.util.spec_from_file_location("semantics_freeze", BASE / "tools/freeze.py")
freeze = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freeze)


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _copy(tmp_path):
    destination = tmp_path / "archive"
    freeze.export_freeze(destination)
    return destination


def test_approved_reference_is_bound_to_297_facts_without_rewriting_initial_labels():
    manifest = freeze.verify_freeze()
    approval = _json(BASE / "approval.json")
    assert manifest["protocol"] == {
        "development_samples": 22, "held_out_samples": 8,
        "repeats_per_sample": 3, "extractions_per_version": 90,
    }
    assert approval["status"] == "jointly_confirmed_reference"
    assert "我已经共同确认" in approval["user_message"]
    assert sum(len(item["fact_ids"]) for item in approval["samples"]) == 297
    assert any(item["unresolved_fact_ids"] for item in approval["samples"])
    assert any(item["open_questions"] for item in approval["samples"])
    for item in approval["samples"]:
        annotation = _json(freeze.corpus_root() / "annotations" / (item["sample_id"] + ".json"))
        assert all(fact["status"] == "待共同复核" for fact in annotation["facts"])
        assert item["disposition"] == "approved_reference_with_documented_uncertainty"


def test_frozen_corpus_is_exactly_the_source_of_the_reviewed_pdf():
    """Tie the approved archive to the actual reviewed revision, not live files."""
    build = _json(BASE / "frozen/review/build_manifest.json")
    actual = freeze.tree_inventory(freeze.corpus_root())
    assert {path: info["sha256"] for path, info in actual.items()} == build["source_sha256"]
    assert freeze.sha256(freeze.production_root() / "inputs/skill_package.py") == build["production_loader_sha256"]
    source_files = [name for name in actual if name.startswith("inputs/")]
    assert len(source_files) == 82


def test_original_contract_has_source_and_rendered_prompt_snapshots():
    root = freeze.production_root()
    for name in (
        "extraction/prompt.py", "extraction/candidate.py", "extraction/compiler.py",
        "extraction/pipeline.py", "extraction/response_parser.py", "llm/client.py",
        "llm/config.py", "ir/cfg.py", "ir/basic_block.py", "ir/instruction.py",
        "ir/operand.py", "ir/validation.py", "inputs/skill_package.py",
    ):
        assert (root / name).is_file()
    schema = _json(BASE / "frozen/original_contract/candidate.schema.json")
    assert "constraints" not in schema["properties"]
    for name in ("CandidateInstruction", "CandidateBlock"):
        assert "constraints" not in schema["$defs"][name]["properties"]
    generation = _json(BASE / "frozen/original_contract/generation.json")
    assert generation["pydantic_version"]
    assert generation["online_calls"] == 0
    assert generation["sample_code_executed"] is False


def test_all_frozen_prompt_inputs_exclude_external_annotations():
    catalog = _json(freeze.corpus_root() / "corpus.json")
    prefix = (BASE / "frozen/original_contract/prompt-prefix.txt").read_bytes().decode("utf-8")
    prompt_dir = BASE / "frozen/original_contract/prompts"
    assert {path.stem for path in prompt_dir.glob("*.txt")} == set(freeze.SAMPLE_IDS)
    for sample in catalog["samples"]:
        package_path = freeze.corpus_root() / sample["package_path"]
        annotation_path = freeze.corpus_root() / sample["annotation_path"]
        assert not annotation_path.is_relative_to(package_path)
        package = load_skill_package(package_path)
        prompt = (prompt_dir / (sample["id"] + ".txt")).read_bytes().decode("utf-8")
        assert prompt.startswith(prefix)
        assert prompt.count("<skill-file path=") == len(package.files)
        for member in package.readable_files():
            assert member.content in prompt
        for marker in ('"coverage_targets"', '"acceptable_variants"', '"must_not_infer"', "待共同复核"):
            assert marker not in prompt


@pytest.mark.parametrize("change", ("input", "annotation", "original_prompt", "production", "add", "remove", "cache_annotation", "approval"))
def test_verifier_rejects_any_changed_archival_input_or_approval(tmp_path, change):
    base = _copy(tmp_path)
    targets = {
        "input": "frozen/corpus/inputs/controlled/N01/SKILL.md",
        "annotation": "frozen/corpus/annotations/N01.json",
        "original_prompt": "frozen/original_contract/prompts/N01.txt",
        "production": "frozen/production/src/skill_ir/extraction/prompt.py",
        "approval": "approval.json",
    }
    if change in targets:
        with (base / targets[change]).open("ab") as stream:
            stream.write(b" ")  # fact IDs may stay unchanged; exact bytes matter.
    elif change == "add":
        (base / "frozen/corpus/inputs/controlled/N01/extra.txt").write_text("new runtime instruction", encoding="utf-8")
    elif change == "remove":
        (base / "frozen/corpus/inputs/controlled/N01/SKILL.md").unlink()
    else:
        hidden = base / "frozen/corpus/inputs/controlled/N01/__pycache__/facts.json"
        hidden.parent.mkdir()
        hidden.write_text('{"annotation_canary":"never ignore input caches"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Frozen (content|approval) changed"):
        freeze.verify_freeze(base)


def test_export_is_self_contained_and_never_overwrites(tmp_path):
    first = _copy(tmp_path)
    expected = freeze.verify_freeze()
    assert freeze.verify_freeze(first) == expected
    assert not (first / "tools").exists()  # Verification needs no copied Skill scripts.
    with pytest.raises(ValueError, match="Refusing to overwrite"):
        freeze.export_freeze(first)


@pytest.mark.parametrize("path", ("../approval.json", "/absolute/path", "C:/Windows/file", "sub\\escape"))
def test_manifest_paths_cannot_escape_archive(tmp_path, path):
    with pytest.raises(ValueError, match="Unsafe frozen path"):
        freeze.safe_path(tmp_path, path)
