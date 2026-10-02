"""Offline acceptance checks for the phase-one, human-review-only corpus.

These checks exercise the real package loader and prompt builder, but never the
extractor, an LLM, or any script distributed inside a sample Skill package.
"""

from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

import pytest

from skill_ir.extraction.prompt import build_whole_skill_prompt
from skill_ir.inputs.skill_package import load_skill_package


CORPUS_ROOT = Path(__file__).resolve().parents[2] / "experiments" / "semantics_review"
PINNED_COMMIT = "49f948faa9258a0c61caceaf225e179651397431"
CONTROLLED_GROUPS = {
    "N": ("notification", "zh", "development"),
    "Q": ("query", "en", "held_out"),
    "F": ("fallback", "en", "development"),
    "D": ("documents", "zh", "development"),
}
EXPRESSIONS = (
    "numbered", "prose", "table", "mixed", "purpose_delta", "semantic_delta"
)
UPSTREAM_NAMES = (
    "pdf", "playwright", "gh-fix-ci", "netlify-deploy", "linear", "transcribe"
)
CONTROLLED_IDS = tuple(f"{prefix}{n:02}" for prefix in CONTROLLED_GROUPS for n in range(1, 7))
UPSTREAM_IDS = tuple(f"R{n:02}" for n in range(1, 7))
SAMPLE_IDS = CONTROLLED_IDS + UPSTREAM_IDS
ANNOTATION_CANARY = "EXTERNAL_REVIEW_ONLY_9e90ccba_DO_NOT_INCLUDE_IN_SKILL_INPUT"


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _inside(root: Path, relative: str) -> Path:
    """Accept only an explicit, portable member of the named corpus/package."""
    assert isinstance(relative, str) and relative
    assert "\\" not in relative
    posix = PurePosixPath(relative)
    assert not posix.is_absolute() and ".." not in posix.parts
    assert ":" not in relative
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve()), relative
    assert path.exists(), relative
    assert not (root / relative).is_symlink(), relative
    return path


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _fact_key(fact: dict) -> str:
    # Fact ids carry the sample prefix; the suffix identifies the corresponding
    # fact across all six variants of one controlled scenario.
    return fact["id"].split("-", 1)[-1]


def _semantic_facts(annotation: dict) -> dict[str, tuple]:
    return {
        _fact_key(fact): (fact["kind"], fact["statement"], fact["scope"])
        for fact in annotation["facts"]
    }


@pytest.fixture(scope="module")
def catalog():
    return _read_json(CORPUS_ROOT / "corpus.json")


@pytest.fixture(scope="module")
def samples(catalog):
    return {sample["id"]: sample for sample in catalog["samples"]}


@pytest.fixture(scope="module")
def annotations(samples):
    return {
        sample_id: _read_json(_inside(CORPUS_ROOT, sample["annotation_path"]))
        for sample_id, sample in samples.items()
    }


def test_inventory_has_exactly_the_planned_30_samples_and_group_splits(catalog, samples):
    assert catalog["schema_version"] == 1
    assert catalog["upstream_commit"] == PINNED_COMMIT
    assert len(catalog["samples"]) == len(samples) == 30
    assert set(samples) == set(SAMPLE_IDS)
    assert Counter(s["kind"] for s in samples.values()) == {"controlled": 24, "upstream": 6}
    assert Counter(s["split"] for s in samples.values()) == {"development": 22, "held_out": 8}
    for prefix, (group, language, split) in CONTROLLED_GROUPS.items():
        for number, expression in enumerate(EXPRESSIONS, 1):
            sample = samples[f"{prefix}{number:02}"]
            assert (sample["kind"], sample["group"], sample["language"], sample["split"], sample["expression"]) == (
                "controlled", group, language, split, expression
            )
    for number, name in enumerate(UPSTREAM_NAMES, 1):
        sample = samples[f"R{number:02}"]
        assert sample["kind"] == "upstream"
        assert sample["group"] == "upstream"
        assert sample["expression"] == "original"
        assert sample["split"] == ("development" if number <= 4 else "held_out")
        assert PurePosixPath(sample["package_path"]).name == name


def test_each_input_is_disjoint_from_annotations_and_other_skill_inputs(samples):
    packages = [_inside(CORPUS_ROOT, s["package_path"]) for s in samples.values()]
    assert len(packages) == len(set(packages)) == 30
    assert {path.parent.resolve() for path in (CORPUS_ROOT / "inputs").rglob("SKILL.md")} == set(packages)
    metadata = [_inside(CORPUS_ROOT, s["annotation_path"]) for s in samples.values()]
    assert {path.resolve() for path in (CORPUS_ROOT / "annotations").glob("*.json")} == set(metadata)
    metadata += [_inside(CORPUS_ROOT, s["provenance_path"]) for s in samples.values() if "provenance_path" in s]
    assert len(metadata) == len(set(metadata))
    for package in packages:
        assert package.is_dir()
        assert (package / "SKILL.md").is_file()
        for other in packages:
            assert other == package or not other.is_relative_to(package)
        assert all(not path.is_relative_to(package) for path in metadata)
        for path in package.rglob("*"):
            assert not path.is_symlink(), path
            assert path.name not in {"__pycache__", "corpus.json", "coverage_matrix.json"}
        # Production loading is recursive. A misplaced sidecar is input even if
        # it is JSON or lives below an innocuous-looking subdirectory.
        for member in load_skill_package(package).readable_files():
            for marker in ('"coverage_targets"', '"acceptable_variants"', '"must_not_infer"', "待共同复核"):
                assert marker not in member.content, (package, member.path, marker)


@pytest.mark.parametrize("sample_id", SAMPLE_IDS)
def test_annotations_are_pending_facts_with_exact_source_evidence(sample_id, samples, annotations):
    sample = samples[sample_id]
    annotation = annotations[sample_id]
    assert annotation["schema_version"] == 1
    assert annotation["sample_id"] == sample_id
    for key in ("group", "expression", "language", "split"):
        assert annotation[key] == sample[key]
    assert isinstance(annotation["acceptable_variants"], list)
    assert isinstance(annotation["open_questions"], list)
    if sample["expression"] not in {"purpose_delta", "semantic_delta"}:
        assert annotation["minimal_pair"] is None
    assert annotation["facts"]
    fact_ids = [fact["id"] for fact in annotation["facts"]]
    assert len(fact_ids) == len(set(fact_ids))
    assert all(fact_id.startswith(sample_id + "-") for fact_id in fact_ids)
    package_path = _inside(CORPUS_ROOT, sample["package_path"])
    readable = {member.path: member.content for member in load_skill_package(package_path).readable_files()}
    covered_targets = set()
    for fact in annotation["facts"]:
        assert fact["kind"] in {"behavior", "condition", "data_flow", "constraint", "must_not_infer"}
        assert fact["statement"].strip()
        assert fact["status"] == "待共同复核"
        assert fact["scope"]["level"] in {"skill", "block", "operation", "unresolved"}
        assert isinstance(fact["scope"]["target"], str) and fact["scope"]["target"].strip()
        assert isinstance(fact["coverage_tags"], list)
        assert len(fact["coverage_tags"]) == len(set(fact["coverage_tags"]))
        covered_targets.update(fact["coverage_tags"])
        assert fact["evidence"], fact["id"]
        for evidence in fact["evidence"]:
            _inside(package_path, evidence["file"])
            assert evidence["file"] in readable, evidence
            lines = readable[evidence["file"]].splitlines()
            start, end = evidence["start_line"], evidence["end_line"]
            assert type(start) is int and type(end) is int
            assert 1 <= start <= end <= len(lines), (fact["id"], evidence)
            assert evidence["quote"] == "\n".join(lines[start - 1:end]), (fact["id"], evidence)
        _assert_table_headers_present(fact, readable)
    assert len(annotation["coverage_targets"]) == len(set(annotation["coverage_targets"]))
    assert set(annotation["coverage_targets"]) == covered_targets


def _assert_table_headers_present(fact, readable):
    """A body cell alone loses its meaning; evidence must also retain its header."""
    locations = {}
    for evidence in fact["evidence"]:
        locations.setdefault(evidence["file"], set()).update(
            range(evidence["start_line"], evidence["end_line"] + 1)
        )
    for name, covered in locations.items():
        lines = readable[name].splitlines()
        for i in range(1, len(lines)):
            separator = lines[i].strip()
            if not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", separator):
                continue
            if not lines[i - 1].strip().startswith("|"):
                continue
            end = i + 1
            while end < len(lines) and lines[end].strip().startswith("|"):
                end += 1
            body_lines = set(range(i + 2, end + 1))
            if covered & body_lines:
                assert {i, i + 1} <= covered, (fact["id"], name, "missing table header")


@pytest.mark.parametrize("prefix", tuple(CONTROLLED_GROUPS))
def test_first_four_variants_preserve_core_facts_and_mixed_file_evidence(prefix, samples, annotations):
    expected = _semantic_facts(annotations[prefix + "01"])
    for number in (2, 3, 4):
        assert _semantic_facts(annotations[f"{prefix}{number:02}"]) == expected
    mixed_id = prefix + "04"
    package = _inside(CORPUS_ROOT, samples[mixed_id]["package_path"])
    assert len(load_skill_package(package).readable_files()) > 1
    assert any(
        len({e["file"] for e in fact["evidence"]}) > 1
        and any(e["file"] == "SKILL.md" for e in fact["evidence"])
        for fact in annotations[mixed_id]["facts"]
    ), "Cross-file evidence must retain the entry-point reference and referenced content."


@pytest.mark.parametrize("sample_id", tuple(f"{prefix}{n:02}" for prefix in CONTROLLED_GROUPS for n in (5, 6)))
def test_minimal_pairs_change_one_source_line_and_identify_changed_facts(sample_id, samples, annotations):
    annotation = annotations[sample_id]
    pair = annotation["minimal_pair"]
    base_id = sample_id[0] + "01"
    assert pair["base_id"] == base_id
    assert pair["change"].strip()
    before = _files(_inside(CORPUS_ROOT, samples[base_id]["package_path"]))
    after = _files(_inside(CORPUS_ROOT, samples[sample_id]["package_path"]))
    assert before.keys() == after.keys()
    assert [name for name in before if before[name] != after[name]] == ["SKILL.md"]
    before_lines = before["SKILL.md"].decode("utf-8-sig").splitlines()
    after_lines = after["SKILL.md"].decode("utf-8-sig").splitlines()
    changes = [op for op in SequenceMatcher(a=before_lines, b=after_lines).get_opcodes() if op[0] != "equal"]
    assert len(changes) == 1
    tag, i1, i2, j1, j2 = changes[0]
    assert tag == "replace" and i2 - i1 == j2 - j1 == 1
    base_facts = _semantic_facts(annotations[base_id])
    variant_facts = _semantic_facts(annotation)
    assert base_facts.keys() == variant_facts.keys()
    changed = {fact["id"] for fact in annotation["facts"] if base_facts[_fact_key(fact)] != variant_facts[_fact_key(fact)]}
    unchanged = {fact["id"] for fact in annotation["facts"]} - changed
    assert changed and unchanged
    assert set(pair["changed_fact_ids"]) == changed
    assert set(pair["unchanged_fact_ids"]) == unchanged


def test_coverage_matrix_is_a_complete_traceable_projection_of_external_facts(samples, annotations):
    matrix = _read_json(CORPUS_ROOT / "coverage_matrix.json")
    assert matrix["schema_version"] == 1
    expected = {}
    for sample_id, annotation in annotations.items():
        for fact in annotation["facts"]:
            for target in fact["coverage_tags"]:
                expected[(target, sample_id, fact["id"])] = [
                    {key: evidence[key] for key in ("file", "start_line", "end_line")}
                    for evidence in fact["evidence"]
                ]
    actual = {}
    for row in matrix["rows"]:
        key = (row["target"], row["sample_id"], row["fact_id"])
        assert key not in actual, key
        actual[key] = row["evidence"]
    assert actual == expected
    assert {key[1] for key in actual} == set(samples)
    # The requested format dimensions must have actual fact/evidence links;
    # listing a target in a document without a covered sample is insufficient.
    assert {
        "table_headers", "parameter_table", "step_table", "nested_list",
        "blockquote", "code_block", "yaml", "json", "cross_file",
        "prohibition", "exception",
    } <= {key[0] for key in actual}
    assert (CORPUS_ROOT / "coverage_matrix.csv").is_file()
    assert (CORPUS_ROOT / "coverage_matrix.md").is_file()


@pytest.mark.parametrize("change", ("annotation_text", "add_input", "remove_input", "loader"))
def test_pdf_verification_rejects_stale_sources_without_relying_on_fact_ids(tmp_path, change):
    """Changing a fact's meaning must invalidate the old PDF even with the same id."""
    spec = importlib.util.spec_from_file_location("review_pdf_verifier", CORPUS_ROOT / "tools/verify_pdfs.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    root = tmp_path / "skill-ir/experiments/semantics_review"
    root.mkdir(parents=True)
    annotation = root / "annotation.json"
    annotation.write_text('{"id":"D06-F06","statement":"delivery_path"}', encoding="utf-8")
    source = root / "SKILL.md"
    source.write_text("deliver the bundle", encoding="utf-8")
    loader = root.parents[1] / "src/skill_ir/inputs/skill_package.py"
    loader.parent.mkdir(parents=True)
    loader.write_text("# loader snapshot", encoding="utf-8")
    manifest = {"source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()},
                "production_loader_sha256": hashlib.sha256(loader.read_bytes()).hexdigest()}
    verifier.verify_build_sources(manifest, root)
    if change == "annotation_text":
        annotation.write_text('{"id":"D06-F06","statement":"archive_path"}', encoding="utf-8")
    elif change == "add_input":
        (root / "extra.md").write_text("new source", encoding="utf-8")
    elif change == "remove_input":
        source.unlink()
    else:
        loader.write_text("# changed loader", encoding="utf-8")
    with pytest.raises(ValueError, match="changed since PDF build"):
        verifier.verify_build_sources(manifest, root)


@pytest.mark.parametrize("sample_id", UPSTREAM_IDS)
def test_upstream_manifests_pin_complete_original_bytes_and_loader_boundaries(sample_id, samples):
    sample = samples[sample_id]
    manifest = _read_json(_inside(CORPUS_ROOT, sample["provenance_path"]))
    lock = _read_json(CORPUS_ROOT / "provenance" / "upstream-lock.json")
    assert manifest["schema_version"] == lock["schema_version"] == 1
    assert manifest["sample_id"] == sample_id
    assert manifest["repository"] == lock["repository"] == "https://github.com/openai/skills"
    assert manifest["commit"] == lock["commit"] == PINNED_COMMIT
    assert manifest["package_path"] == sample["package_path"]
    assert manifest["split"] == sample["split"]
    name = UPSTREAM_NAMES[int(sample_id[1:]) - 1]
    assert manifest["upstream_path"] == f"skills/.curated/{name}"
    assert manifest["source_url"] == f"https://github.com/openai/skills/tree/{PINNED_COMMIT}/skills/.curated/{name}"
    assert lock["tree_response_truncated"] is False
    assert set(lock["package_paths"]) == {f"skills/.curated/{name}" for name in UPSTREAM_NAMES}
    package_path = _inside(CORPUS_ROOT, sample["package_path"])
    actual_bytes = _files(package_path)
    manifest_files = {entry["path"]: entry for entry in manifest["files"]}
    assert len(manifest_files) == len(manifest["files"])
    locked_files = {
        entry["path"].removeprefix(manifest["upstream_path"] + "/"): entry
        for entry in lock["files"]
        if entry["path"].startswith(manifest["upstream_path"] + "/")
    }
    assert actual_bytes.keys() == manifest_files.keys() == locked_files.keys()
    loaded_files = {member.path: member for member in load_skill_package(package_path).files}
    assert loaded_files.keys() == actual_bytes.keys()
    for path, raw in actual_bytes.items():
        entry = manifest_files[path]
        locked = locked_files[path]
        assert entry["bytes"] == locked["size"] == len(raw)
        assert entry["sha256"] == hashlib.sha256(raw).hexdigest()
        git_blob_sha = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
        assert entry["git_blob_sha"] == locked["sha"] == git_blob_sha
        assert entry["git_mode"] == locked["mode"]
        assert locked["type"] == "blob"
        content = loaded_files[path].content
        assert entry["loader_readable"] is (content is not None)
        assert entry["line_count"] == (len(content.splitlines()) if content is not None else None)
    assert set(manifest["readable_files"]) == {path for path, member in loaded_files.items() if member.content is not None}
    assert set(manifest["omitted_files"]) == {path for path, member in loaded_files.items() if member.content is None}
    assert "LICENSE.txt" in manifest["license"]["package_files"]
    for license_file in manifest["license"]["package_files"]:
        assert license_file in actual_bytes
    assert manifest["license"]["repository_root_license"] is None
    assert lock["root_license_present"] is False
    readme = _inside(CORPUS_ROOT, manifest["license"]["repository_license_statement"]).read_bytes()
    readme_lock = next(entry for entry in lock["files"] if entry["path"] == "README.md")
    assert hashlib.sha1(f"blob {len(readme)}\0".encode("ascii") + readme).hexdigest() == readme_lock["sha"]
    for link in manifest["external_links"]:
        assert link["provided_as_input"] is False
        assert link["status"] == "not_fetched"
        content = loaded_files[link["file"]].content
        assert content is not None
        assert link["url"] in content.splitlines()[link["line"] - 1]


@pytest.mark.parametrize("sample_id", SAMPLE_IDS)
def test_directory_and_zip_prompts_include_all_input_but_no_external_annotations(sample_id, samples, tmp_path):
    sample = samples[sample_id]
    source = _inside(CORPUS_ROOT, sample["package_path"])
    expected_package = load_skill_package(source)
    expected_prompt = build_whole_skill_prompt(expected_package)
    isolated_package_path = tmp_path / "inputs" / source.name
    shutil.copytree(source, isolated_package_path)

    # Put a canary in a real copy of the external annotation, alongside a second
    # sidecar beside the package. No production filter is assumed: isolation is
    # guaranteed by selecting only the catalog's package_path as Skill input.
    annotation_dir = tmp_path / "annotations"
    annotation_dir.mkdir()
    external_annotation = _read_json(_inside(CORPUS_ROOT, sample["annotation_path"]))
    external_annotation["review_canary"] = ANNOTATION_CANARY
    (annotation_dir / f"{sample_id}.json").write_text(json.dumps(external_annotation), encoding="utf-8")
    (isolated_package_path.parent / "review-sidecar.json").write_text(ANNOTATION_CANARY, encoding="utf-8")
    archive_path = tmp_path / f"{sample_id}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member in sorted(isolated_package_path.rglob("*")):
            if member.is_file():
                archive.write(member, f"{source.name}/{member.relative_to(isolated_package_path).as_posix()}")

    for input_path in (isolated_package_path, archive_path):
        package = load_skill_package(input_path)
        prompt = build_whole_skill_prompt(package)
        assert package.files == expected_package.files
        assert prompt == expected_prompt
        assert ANNOTATION_CANARY not in prompt
        assert "review-sidecar.json" not in prompt
        for member in package.readable_files():
            assert member.content in prompt
        assert prompt.count("<skill-file path=") == len(package.files)
