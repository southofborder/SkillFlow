"""Offline pairing checks with real frozen ZIPs and temporary synthetic PNGs.

The tiny PNG fixtures test the container and source binding only. They are never
published, and they do not pretend to render the actual CFG visually.
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
import shutil
import struct
import sys
import zlib

import pytest

BASE = Path(__file__).resolve().parents[2] / "experiments/semantics_baseline"
TOOLS = BASE / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("review_set_export_test", TOOLS / "export_review_set.py")
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)


def chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def synthetic_png() -> bytes:
    # Two RGBA pixels, one scanline, valid compressed image content split across
    # two IDAT chunks. Extra metadata exercises lossless source binding.
    raw_pixels = b"\x00\x10\x20\x30\xff\xaa\xbb\xcc\xff"
    compressed = zlib.compress(raw_pixels)
    return exporter.PNG_SIGNATURE + b"".join([
        chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 1, 8, 6, 0, 0, 0)),
        chunk(b"gAMA", struct.pack(">I", 45455)),
        chunk(b"tEXt", b"Software\x00synthetic offline test fixture"),
        chunk(b"iTXt", b"Comment\x00\x00\x00\x00\x00" + "仅临时测试图片".encode("utf-8")),
        chunk(b"IDAT", compressed[:5]),
        chunk(b"IDAT", compressed[5:]),
        chunk(b"IEND", b""),
    ])


@pytest.fixture(scope="module")
def real_plan():
    return exporter.build_export_plan(
        BASE.parents[3], BASE / "runs/baseline-deepseek-v4-flash-max-20260910"
    )


@pytest.fixture(scope="module")
def valid_delivery(real_plan, tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic-review-pairing")
    skills, images = root / "skills", root / "images"
    skills.mkdir()
    images.mkdir()
    for item in real_plan:
        archive = skills / (item["basename"] + ".zip")
        picture = images / (item["basename"] + ".png")
        exporter.write_skill_zip(item, archive)
        picture.write_bytes(synthetic_png())
        exporter.bind_png_source(picture, exporter.source_identity(item, archive))
    return skills, images


@pytest.fixture
def mutable_delivery(valid_delivery, tmp_path):
    skills, images = tmp_path / "skills", tmp_path / "images"
    shutil.copytree(valid_delivery[0], skills)
    shutil.copytree(valid_delivery[1], images)
    return skills, images


@pytest.fixture
def render_audit(real_plan):
    return {"samples": [{"basename": item["basename"],
                         "counts": exporter.graph_counts(item["cfg"]),
                         "text_checks_passed": True, "bounds_checks_passed": True}
                        for item in real_plan]}


def test_real_thirty_skill_zips_pair_with_synthetic_source_bound_pngs(real_plan, valid_delivery):
    verified = exporter.validate_delivery(real_plan, *valid_delivery)
    assert len(verified) == 30
    assert {row["sample_id"] for row in verified} == {item["sample_id"] for item in real_plan}
    assert [(row["sample_id"], row["repetition"]) for row in verified if row["repetition"] != 1] == [("F03", 3)]
    assert all(row["width"] == 2 and row["height"] == 1 for row in verified)
    for item, row in zip(real_plan, verified):
        assert row["source"] == exporter.source_identity(
            item, valid_delivery[0] / (item["basename"] + ".zip")
        )


@pytest.mark.parametrize("mutation", ["sample_id", "repetition", "zip_sha256", "analysis_sha256", "swap_picture"])
def test_mismatched_png_sample_repetition_and_zip_source_are_rejected(real_plan, mutable_delivery, mutation):
    skills, images = mutable_delivery
    first = real_plan[0]
    picture = images / (first["basename"] + ".png")
    if mutation == "swap_picture":
        other = images / (real_plan[1]["basename"] + ".png")
        picture.write_bytes(other.read_bytes())
    else:
        identity = deepcopy(exporter.inspect_png(picture)["source"])
        identity[mutation] = {"sample_id": "N02", "repetition": 2,
                              "zip_sha256": "0" * 64, "analysis_sha256": "0" * 64}[mutation]
        exporter.bind_png_source(picture, identity)
    with pytest.raises(ValueError, match="pairing mismatch"):
        exporter.validate_delivery(real_plan, skills, images)


@pytest.mark.parametrize("mutation", ["crc", "duplicate_identity", "missing_identity"])
def test_png_crc_and_exactly_one_source_identity_are_required(real_plan, mutable_delivery, mutation):
    skills, images = mutable_delivery
    picture = images / (real_plan[0]["basename"] + ".png")
    data = picture.read_bytes()
    chunks = list(exporter.png_chunks(data))
    if mutation == "crc":
        first_idat = next(raw for kind, _, raw in chunks if kind == b"IDAT")
        offset = data.index(first_idat) + 8
        damaged = bytearray(data)
        damaged[offset] ^= 1  # Keep the old CRC to simulate a corrupted image.
        picture.write_bytes(damaged)
    elif mutation == "duplicate_identity":
        identity = next(raw for kind, payload, raw in chunks if kind == b"tEXt"
                        and payload.startswith(exporter.IDENTITY_KEY + b"\0"))
        picture.write_bytes(data[:-12] + identity + data[-12:])
    else:
        picture.write_bytes(synthetic_png())
    with pytest.raises(ValueError, match="CRC mismatch|exactly one SkillIR source identity"):
        exporter.validate_delivery(real_plan, skills, images)


@pytest.mark.parametrize("directory", ["skills", "images"])
@pytest.mark.parametrize("mutation", ["extra_file", "subdirectory", "missing_file"])
def test_delivery_inventory_rejects_extra_files_directories_and_missing_pair(real_plan, mutable_delivery, directory, mutation):
    skills, images = mutable_delivery
    target = skills if directory == "skills" else images
    if mutation == "extra_file":
        (target / "external-annotation.json").write_text("not a deliverable", encoding="utf-8")
    elif mutation == "subdirectory":
        (target / "nested").mkdir()
    else:
        extension = ".zip" if directory == "skills" else ".png"
        (target / (real_plan[0]["basename"] + extension)).unlink()
    with pytest.raises(ValueError, match="inventory differs|Unexpected subdirectory"):
        exporter.validate_delivery(real_plan, skills, images)


def test_complete_render_audit_matches_all_graph_counts(real_plan, render_audit):
    exporter.check_render_audit(real_plan, render_audit)


@pytest.mark.parametrize("mutation", ["missing_sample", "duplicate_sample", "missing_count", "text_false", "bounds_false"])
def test_render_audit_rejects_missing_coverage_counts_or_failed_checks(real_plan, render_audit, mutation):
    if mutation == "missing_sample":
        render_audit["samples"].pop()
    elif mutation == "duplicate_sample":
        render_audit["samples"][-1] = deepcopy(render_audit["samples"][0])
    elif mutation == "missing_count":
        del render_audit["samples"][0]["counts"]["inputs"]
    elif mutation == "text_false":
        render_audit["samples"][0]["text_checks_passed"] = False
    else:
        render_audit["samples"][0]["bounds_checks_passed"] = False
    with pytest.raises(ValueError, match="inventory differs|counts differ|verification failed"):
        exporter.check_render_audit(real_plan, render_audit)


@pytest.mark.parametrize("count", ["blocks", "edges", "instructions", "inputs", "outputs",
                                   "skill_constraints", "block_constraints", "instruction_constraints"])
def test_each_rendered_graph_element_count_is_checked(real_plan, render_audit, count):
    render_audit["samples"][0]["counts"][count] -= 1
    with pytest.raises(ValueError, match="Rendered CFG counts differ"):
        exporter.check_render_audit(real_plan, render_audit)


def test_binding_preserves_every_image_and_unrelated_metadata_chunk(tmp_path):
    picture = tmp_path / "synthetic.png"
    original = synthetic_png()
    original_chunks = list(exporter.png_chunks(original))
    picture.write_bytes(original)
    identity = {"synthetic_fixture": True, "sample_id": "N01", "repetition": 1}
    exporter.bind_png_source(picture, identity)
    bound = picture.read_bytes()
    bound_chunks = list(exporter.png_chunks(bound))
    unrelated_chunks = [(kind, payload, raw) for kind, payload, raw in bound_chunks
                        if not (kind == b"tEXt" and payload.startswith(exporter.IDENTITY_KEY + b"\0"))]
    assert unrelated_chunks == original_chunks
    assert len(bound_chunks) == len(original_chunks) + 1
    assert exporter.inspect_png(picture) == {"width": 2, "height": 1, "source": identity}
    pixels = zlib.decompress(b"".join(payload for kind, payload, _ in bound_chunks if kind == b"IDAT"))
    assert pixels == b"\x00\x10\x20\x30\xff\xaa\xbb\xcc\xff"
    exporter.bind_png_source(picture, identity)
    assert picture.read_bytes() == bound  # Rebinding does not duplicate source metadata.
    changed = {**identity, "repetition": 2}
    exporter.bind_png_source(picture, changed)
    assert exporter.inspect_png(picture)["source"] == changed
    final_chunks = list(exporter.png_chunks(picture.read_bytes()))
    assert [raw for kind, payload, raw in final_chunks
            if not (kind == b"tEXt" and payload.startswith(exporter.IDENTITY_KEY + b"\0"))] == [
                raw for _, _, raw in original_chunks]
