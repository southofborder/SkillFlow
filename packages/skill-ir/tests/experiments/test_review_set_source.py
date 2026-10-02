"""Offline export selection and input isolation; fixtures never run model calls."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
SPEC = importlib.util.spec_from_file_location("review_set_source_test", BASE / "tools/review_set_source.py")
source = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def synthetic_run(tmp_path):
    repo = tmp_path / "repo"
    base = repo / "packages/skill-ir/experiments/semantics_baseline"
    run = base / "runs/synthetic-offline-run"
    corpus = base / "frozen/corpus"
    samples, identities, rows = [], [], []
    variant = "synthetic-model"
    cfg = {
        "entry_block_id": "block_001", "constraints": ["Synthetic constraint 中文"],
        "blocks": {"block_001": {
            "block_id": "block_001", "block_name": "Synthetic stop", "data_source_kind": None,
            "constraints": [], "instructions": [{
                "id": "ir_001", "opcode": "return", "inputs": [], "outputs": [],
                "constraints": [], "metadata": {}, "draft_instruction_id": "synthetic_return",
            }],
        }}, "edges": [], "declared_context_keys": [],
    }
    for sid in source.SAMPLE_IDS:
        family = "upstream" if sid.startswith("R") else "controlled"
        relative = f"inputs/{family}/{sid}"
        package = corpus / relative
        package.mkdir(parents=True)
        quoted = '"fixture-skill"' if sid == "R01" else "'fixture-skill'" if sid == "R06" else "fixture-skill"
        (package / "SKILL.md").write_bytes(f"---\nname: {quoted}\n---\n# Synthetic 中文 input\n".encode())
        if sid == "N04":
            (package / "references").mkdir()
            (package / "references/raw.bin").write_bytes(b"\x00\xff\x01\r\n")
            (package / "references/code.py").write_bytes(b"raise RuntimeError('DO NOT EXECUTE SKILL CODE')\r\n")
            (package / ".hidden").write_bytes(b"archival bytes\r\n")
            (package / "__pycache__").mkdir()
            (package / "__pycache__/input.bin").write_bytes(b"do not filter input members")
        samples.append({"id": sid, "split": "development", "package_path": relative,
                        "annotation_path": f"annotations/{sid}.json"})
        # Deliberately not parseable; selection and packing must not consult it.
        annotation = corpus / f"annotations/{sid}.json"
        annotation.parent.mkdir(exist_ok=True)
        annotation.write_bytes(b"EXTERNAL FACTS; NOT JSON; NEVER A SKILL INPUT")
        loaded = source.load_skill_package(package)
        canonical = json.dumps(loaded.model_dump(mode="json"), ensure_ascii=False,
                               sort_keys=True, separators=(",", ":")).encode()
        prompt = f"Synthetic offline prompt for {sid}"
        identity = {"id": sid, "split": "development", "prompt_sha256": digest(prompt.encode()),
                    "extraction_input_sha256": digest(canonical)}
        identities.append(identity)
        for repetition in (1, 2, 3):
            status = "error" if sid == "F03" and repetition == 1 else (
                "degraded" if sid == "F03" and repetition == 2 else "complete")
            record = {"case": sid, "variant": variant, "repetition": repetition,
                      "split": "development", "status": status,
                      "artifacts": f"trials/{sid}/{variant}/{repetition}",
                      "prompt_sha256": identity["prompt_sha256"], "artifact_sha256": {},
                      "blocks": 1, "edges": 0, "attempts": 1, "diagnostics": []}
            path = run / record["artifacts"]
            if status == "complete":
                write(path / "analysis.json", {"status": "complete", "cfg": cfg,
                                               "attempts": 1, "diagnostics": []})
                write(path / "trace.json", {
                    **{key: record[key] for key in ("case", "variant", "repetition", "split")},
                    "calls": [{"status": "complete", "prompt": prompt,
                               "response": {"synthetic_offline_fixture": True}}],
                })
                record["artifact_sha256"] = {name: source.integrity.sha(path / name)
                                             for name in ("analysis.json", "trace.json")}
            write(path / "record.json", record)
            rows.append(record)
    write(corpus / "corpus.json", {"samples": samples})
    inventory = {path.relative_to(base / "frozen").as_posix(): {
        "sha256": source.integrity.sha(path), "bytes": path.stat().st_size,
    } for path in (base / "frozen").rglob("*") if path.is_file()}
    write(base / "freeze_manifest.json", {
        "schema_version": 1, "files": inventory,
        "content_sha256": source.integrity.freeze.inventory_digest(inventory),
    })
    write(run / "experiment.json", {
        "name": "synthetic-review-export", "repetitions": 3, "variants": [{"id": variant}],
        "cases": identities, "provenance": {"contract": "constraints-v2",
            "freeze_manifest_sha256": source.integrity.sha(base / "freeze_manifest.json")},
    })
    write(run / "dataset.json", {"cases": identities})
    write(run / "report.json", {"name": "synthetic-review-export", "run_id": run.name,
                                "mode": "online", "trials": list(reversed(rows))})
    write(run / "reviews/N01.json", {"prefer_repetition": 3, "verdict": "unrelated"})
    return repo, base, run


def test_real_plan_uses_fixed_names_order_and_only_f03_third_repetition():
    repo = BASE.parents[3]
    run = BASE / "runs/baseline-deepseek-v4-flash-max-20260910"
    plan = source.build_export_plan(repo, run)
    assert [item["sample_id"] for item in plan] == list(source.SAMPLE_IDS)
    assert [item["index"] for item in plan] == list(range(1, 31))
    assert [item["sample_id"] for item in plan if item["repetition"] != 1] == ["F03"]
    assert plan[14]["repetition"] == 3
    assert [item["basename"] for item in plan[-6:]] == [
        "025-pdf", "026-playwright", "027-gh-fix-ci", "028-netlify-deploy", "029-linear", "030-transcribe",
    ]
    assert all(set(item) == {"index", "sample_id", "skill_name", "basename", "repetition",
                             "package_path", "analysis_path", "analysis_sha256", "cfg", "run_id"}
               for item in plan)
    for item in plan:
        assert Path(item["package_path"]).is_absolute() and Path(item["analysis_path"]).is_absolute()
        assert item["cfg"] == source.load_analysis_cfg(item["analysis_path"]).model_dump(mode="json")


def test_selection_ignores_report_order_reviews_and_external_annotation_bodies(synthetic_run, monkeypatch):
    repo, _, run = synthetic_run
    original_bytes, original_text = Path.read_bytes, Path.read_text

    def check_path(path):
        assert not {"annotations", "reviews", "review_packets", "provenance"}.intersection(path.parts)

    def read_bytes(path, *args, **kwargs):
        check_path(path)
        return original_bytes(path, *args, **kwargs)

    def read_text(path, *args, **kwargs):
        check_path(path)
        return original_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    monkeypatch.setattr(Path, "read_text", read_text)
    plan = source.build_export_plan(repo, run)
    assert len(plan) == 30
    assert [(item["sample_id"], item["repetition"]) for item in plan if item["repetition"] != 1] == [("F03", 3)]
    assert all(item["skill_name"] == "fixture-skill" for item in plan)
    assert len({item["basename"] for item in plan}) == 30


@pytest.mark.parametrize("mutation", ["analysis_bytes", "record_row", "summary", "invalid_cfg", "analysis_status", "trace_bytes"])
def test_tampered_earliest_complete_is_rejected_without_falling_back(synthetic_run, mutation):
    repo, _, run = synthetic_run
    report = source._read(run / "report.json")
    row = next(t for t in report["trials"] if t["case"] == "N01" and t["repetition"] == 1)
    path = run / row["artifacts"]
    record = source._read(path / "record.json")
    if mutation == "record_row":
        record["blocks"] = 99
        write(path / "record.json", record)
    elif mutation == "summary":
        row["blocks"] = 99
        write(path / "record.json", row)
        write(run / "report.json", report)
    elif mutation == "trace_bytes":
        (path / "trace.json").write_bytes(b"changed after commit")
    else:
        analysis = source._read(path / "analysis.json")
        if mutation == "invalid_cfg":
            analysis["cfg"]["entry_block_id"] = "missing-block"
        elif mutation == "analysis_status":
            analysis["status"] = "degraded"
        else:
            analysis["diagnostics"].append("changed after commit")
        write(path / "analysis.json", analysis)
        if mutation != "analysis_bytes":
            row["artifact_sha256"]["analysis.json"] = source.integrity.sha(path / "analysis.json")
            write(path / "record.json", row)
            write(run / "report.json", report)
    with pytest.raises(ValueError, match="hash mismatch|disagree|validation failed|not complete"):
        source.build_export_plan(repo, run)


def test_sample_without_complete_repetition_is_rejected(synthetic_run):
    repo, _, run = synthetic_run
    report = source._read(run / "report.json")
    for row in report["trials"]:
        if row["case"] == "N01":
            row["status"] = "error"
    write(run / "report.json", report)
    with pytest.raises(ValueError, match="No complete repetition available: N01"):
        source.build_export_plan(repo, run)


@pytest.mark.parametrize("mutation", ["extra_input", "changed_input", "changed_catalog", "extra_trial"])
def test_frozen_input_and_trial_inventories_cannot_drift(synthetic_run, mutation):
    repo, base, run = synthetic_run
    package = base / "frozen/corpus/inputs/controlled/N01"
    if mutation == "extra_input":
        (package / "annotations.json").write_bytes(b"not a frozen input")
    elif mutation == "changed_input":
        (package / "SKILL.md").write_bytes(b"changed after freeze")
    elif mutation == "changed_catalog":
        catalog = source._read(base / "frozen/corpus/corpus.json")
        catalog["samples"].reverse()
        write(base / "frozen/corpus/corpus.json", catalog)
    else:
        report = source._read(run / "report.json")
        report["trials"].append(deepcopy(report["trials"][0]))
        write(run / "report.json", report)
    with pytest.raises(ValueError, match="changed|trial plan"):
        source.build_export_plan(repo, run)


def test_zip_is_reproducible_complete_and_contains_only_one_skill_input(synthetic_run, tmp_path):
    repo, _, run = synthetic_run
    item = source.build_export_plan(repo, run)[3]
    first, second = tmp_path / "first.zip", tmp_path / "second.zip"
    source.write_skill_zip(item, first)
    source.write_skill_zip(item, second)
    assert first.read_bytes() == second.read_bytes()
    evidence = source.verify_skill_zip(item, first)
    expected = {"SKILL.md", ".hidden", "__pycache__/input.bin", "references/raw.bin", "references/code.py"}
    assert set(evidence["files"]) == expected
    assert evidence["file_count"] == 5
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == sorted(expected)
        for member in archive.infolist():
            assert member.date_time == source.ZIP_TIMESTAMP
            assert archive.read(member) == (Path(item["package_path"]) / member.filename).read_bytes()


@pytest.mark.parametrize("mutation", ["extra_annotation", "escape", "duplicate", "changed_bytes"])
def test_zip_verifier_rejects_foreign_paths_and_changed_bytes(synthetic_run, tmp_path, mutation):
    repo, _, run = synthetic_run
    item = source.build_export_plan(repo, run)[0]
    destination = tmp_path / "changed.zip"
    source.write_skill_zip(item, destination)
    if mutation == "changed_bytes":
        with zipfile.ZipFile(destination) as archive:
            members = [(info, archive.read(info)) for info in archive.infolist()]
        with zipfile.ZipFile(destination, "w") as archive:
            for info, raw in members:
                archive.writestr(info, raw + b"tamper")
    else:
        name = {"extra_annotation": "annotations/N01.json", "escape": "../outside.json",
                "duplicate": "SKILL.md"}[mutation]
        with zipfile.ZipFile(destination, "a") as archive:
            if mutation == "duplicate":
                with pytest.warns(UserWarning, match="Duplicate name"):
                    archive.writestr(name, b"external bytes")
            else:
                archive.writestr(name, b"external bytes")
    with pytest.raises(ValueError, match="inventory|bytes differ"):
        source.verify_skill_zip(item, destination)


def test_packaging_rechecks_source_bytes_after_plan_and_refuses_frozen_destination(synthetic_run, tmp_path):
    repo, _, run = synthetic_run
    item = source.build_export_plan(repo, run)[0]
    package = Path(item["package_path"])
    with pytest.raises(ValueError, match="frozen tree"):
        source.write_skill_zip(item, package / "output.zip")
    (package / "unexpected.json").write_bytes(b"external annotation")
    with pytest.raises(ValueError, match="inventory changed"):
        source.write_skill_zip(item, tmp_path / "rejected.zip")
    assert not (tmp_path / "rejected.zip").exists()
