"""Export the 30 frozen Skill packages and their earliest accepted CFGs offline.

Only ZIPs are published to dataset/skills and PNGs to result/ir-IPP. Rendering
intermediates and verification evidence stay under tmp/skill-ir-review-set.
No credentials, annotations, model client, or Skill execution are involved.

Example (from repository root):
    python -X utf8 -m tools.graph.baseline.export_review_set --node-modules <bundled-node-modules>
    python -X utf8 -m tools.graph.baseline.export_review_set --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import zlib

from tools.graph.baseline.review_set_source import build_export_plan, verify_skill_zip, write_skill_zip

from skillflow.common.paths import project_root, resolve_material_path

BASE = project_root() / "experiments/graph/baseline"
REPO = project_root()
DEFAULT_RUN = BASE / "runs/baseline-deepseek-v4-flash-max-20260910"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IDENTITY_KEY = b"SkillIR-Source"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph_counts(cfg: dict) -> dict:
    blocks = list(cfg["blocks"].values())
    instructions = [instruction for block in blocks for instruction in block["instructions"]]
    return {
        "blocks": len(blocks), "edges": len(cfg["edges"]),
        "instructions": len(instructions),
        "inputs": sum(len(item["inputs"]) for item in instructions),
        "outputs": sum(len(item["outputs"]) for item in instructions),
        "skill_constraints": len(cfg.get("constraints", [])),
        "block_constraints": sum(len(item.get("constraints", [])) for item in blocks),
        "instruction_constraints": sum(len(item.get("constraints", [])) for item in instructions),
    }


def png_chunks(data: bytes):
    """Validate the PNG container without changing any image pixels."""
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Not a PNG")
    offset = len(PNG_SIGNATURE)
    seen_end = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + length + 12
        if end > len(data):
            raise ValueError("Truncated PNG chunk body")
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:end - 4]
        crc = struct.unpack(">I", data[end - 4:end])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise ValueError("PNG chunk CRC mismatch")
        yield kind, payload, data[offset:end]
        offset = end
        if kind == b"IEND":
            if offset != len(data):
                raise ValueError("Data after PNG IEND")
            seen_end = True
    if not seen_end:
        raise ValueError("PNG has no IEND")


def source_identity(item: dict, zip_path: Path) -> dict:
    return {"schema_version": 1, "sample_id": item["sample_id"],
            "basename": item["basename"], "repetition": item["repetition"],
            "run_id": item["run_id"], "analysis_sha256": item["analysis_sha256"],
            "zip_sha256": sha(zip_path), "counts": graph_counts(item["cfg"])}


def bind_png_source(path: Path, identity: dict) -> None:
    chunks = list(png_chunks(path.read_bytes()))
    value = IDENTITY_KEY + b"\0" + json.dumps(identity, sort_keys=True, ensure_ascii=True).encode("ascii")
    encoded = struct.pack(">I", len(value)) + b"tEXt" + value + struct.pack(">I", zlib.crc32(b"tEXt" + value) & 0xFFFFFFFF)
    result = [PNG_SIGNATURE]
    for kind, payload, raw in chunks:
        if kind == b"tEXt" and payload.startswith(IDENTITY_KEY + b"\0"):
            continue
        if kind == b"IEND":
            result.append(encoded)
        result.append(raw)
    path.write_bytes(b"".join(result))


def inspect_png(path: Path) -> dict:
    chunks = list(png_chunks(path.read_bytes()))
    if not chunks or chunks[0][0] != b"IHDR" or len(chunks[0][1]) != 13:
        raise ValueError("PNG must start with a valid IHDR")
    width, height = struct.unpack(">II", chunks[0][1][:8])
    if not width or not height or not any(kind == b"IDAT" for kind, _, _ in chunks):
        raise ValueError("PNG has no image content")
    identities = [json.loads(payload.split(b"\0", 1)[1]) for kind, payload, _ in chunks
                  if kind == b"tEXt" and payload.startswith(IDENTITY_KEY + b"\0")]
    if len(identities) != 1:
        raise ValueError("PNG must have exactly one SkillIR source identity")
    return {"width": width, "height": height, "source": identities[0]}


def check_inventory(directory: Path, expected: set[str], exact: bool = True) -> None:
    if directory.is_symlink():
        raise ValueError(f"Output directory cannot be a symlink: {directory}")
    children = list(directory.iterdir()) if directory.exists() else []
    if any(not item.is_file() or item.is_symlink() for item in children):
        raise ValueError(f"Unexpected subdirectory or link in {directory}")
    actual = {item.name for item in children}
    if actual - expected or (exact and actual != expected):
        raise ValueError(f"Delivery inventory differs: {directory}; extra={sorted(actual - expected)}, missing={sorted(expected - actual)}")


def validate_delivery(plan: list[dict], skills_dir: Path, images_dir: Path) -> list[dict]:
    names = [item["basename"] for item in plan]
    if len(names) != 30 or len(set(names)) != 30:
        raise ValueError("Exactly 30 distinct paired names are required")
    check_inventory(skills_dir, {name + ".zip" for name in names})
    check_inventory(images_dir, {name + ".png" for name in names})
    verified = []
    for item in plan:
        package = skills_dir / (item["basename"] + ".zip")
        picture = images_dir / (item["basename"] + ".png")
        verify_skill_zip(item, package)
        info = inspect_png(picture)
        if info["source"] != source_identity(item, package):
            raise ValueError(f"PNG/ZIP/source pairing mismatch: {item['basename']}")
        verified.append({"basename": item["basename"], "sample_id": item["sample_id"],
                         "repetition": item["repetition"], "width": info["width"],
                         "height": info["height"], "png_sha256": sha(picture),
                         "source": info["source"]})
    return verified


def check_render_audit(plan: list[dict], audit: dict) -> None:
    rows = audit["samples"]
    by_name = {item["basename"]: item for item in rows}
    if len(rows) != len(plan) or set(by_name) != {item["basename"] for item in plan}:
        raise ValueError("Rendered sample inventory differs")
    for item in plan:
        row = by_name[item["basename"]]
        if row["counts"] != graph_counts(item["cfg"]):
            raise ValueError(f"Rendered CFG counts differ: {item['basename']}")
        if not row["text_checks_passed"] or not row["bounds_checks_passed"]:
            raise ValueError(f"Rendered text or bounds verification failed: {item['basename']}")


def export(plan: list[dict], repo: Path, node: str, modules: Path, browser: str | None) -> dict:
    skills = repo / "dataset/skills"
    images = repo / "result/ir-IPP"
    # Never clear old data here. Any requested old-results deletion is a separate,
    # explicitly scoped PowerShell operation, not part of reproducible generation.
    check_inventory(skills, {item["basename"] + ".zip" for item in plan}, exact=False)
    check_inventory(images, {item["basename"] + ".png" for item in plan}, exact=False)
    work = repo / "tmp/skill-ir-review-set"
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="export-", dir=work) as temporary:
        staging = Path(temporary)
        staged_skills, staged_images = staging / "skills", staging / "ir-IPP"
        staged_skills.mkdir()
        staged_images.mkdir()
        payload = staging / "render-input.json"
        payload.write_text(json.dumps({"samples": plan}, ensure_ascii=False), encoding="utf-8")
        for item in plan:
            write_skill_zip(item, staged_skills / (item["basename"] + ".zip"))
        audit_path = staging / "render-audit.json"
        command = [node, str(Path(__file__).with_name("render_review_cfg.mjs")), "--input", str(payload),
                   "--output-dir", str(staged_images), "--audit", str(audit_path), "--node-modules", str(modules)]
        if browser:
            command.extend(["--browser", browser])
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            if audit_path.is_file():
                shutil.copyfile(audit_path, work / "last-failed-render-audit.json")
            raise
        render_audit = json.loads(audit_path.read_text(encoding="utf-8"))
        check_render_audit(plan, render_audit)
        for item in plan:
            bind_png_source(staged_images / (item["basename"] + ".png"),
                            source_identity(item, staged_skills / (item["basename"] + ".zip")))
        validate_delivery(plan, staged_skills, staged_images)
        # Check once more immediately before publishing; never overwrite an
        # unrelated file or publish a partially rendered batch.
        for directory, extension in ((skills, ".zip"), (images, ".png")):
            check_inventory(directory, {item["basename"] + extension for item in plan}, exact=False)
            directory.mkdir(parents=True, exist_ok=True)
        for item in plan:
            for source, destination, extension in ((staged_skills, skills, ".zip"), (staged_images, images, ".png")):
                os.replace(source / (item["basename"] + extension), destination / (item["basename"] + extension))
        verified = validate_delivery(plan, skills, images)
        result = {"schema_version": 1, "status": "passed", "packages": 30, "images": 30,
                  "selection": "earliest structurally accepted repetition, not semantic score",
                  "render_audit": render_audit, "verified_pairs": verified,
                  "visual_review": "pending_full_image_inspection"}
        (work / "export-audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--node-executable", default=shutil.which("node"))
    parser.add_argument("--node-modules", type=Path)
    parser.add_argument("--browser")
    parser.add_argument("--check", action="store_true", help="Verify existing ZIP/PNG pairs offline without rendering")
    args = parser.parse_args()
    plan = build_export_plan(REPO, args.run_dir.resolve())
    if args.check:
        result = validate_delivery(plan, REPO / "dataset/skills", REPO / "result/ir-IPP")
        print(json.dumps({"status": "passed", "verified_pairs": len(result)}, ensure_ascii=False))
        return
    if not args.node_executable or not args.node_modules:
        parser.error("Rendering requires --node-executable (or node in PATH) and --node-modules")
    result = export(plan, REPO, args.node_executable, args.node_modules.resolve(), args.browser)
    print(json.dumps({key: result[key] for key in ("status", "packages", "images", "visual_review")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
