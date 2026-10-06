"""Verify/export the approved immutable review and pre-contract production baseline.

No network, extraction, or sample code is run.  This module is deliberately
stdlib-only so a verifier never imports executable files from a Skill input.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil


from skillflow.common.paths import project_root, resolve_material_path

BASE = project_root() / "experiments/graph/baseline"
SAMPLE_IDS = tuple(f"{prefix}{number:02}" for prefix in "NQFD" for number in range(1, 7)) + tuple(
    f"R{number:02}" for number in range(1, 7)
)
HELD_OUT = frozenset(f"Q{number:02}" for number in range(1, 7)) | {"R05", "R06"}


def corpus_root(base: Path = BASE) -> Path:
    return Path(base) / "frozen" / "corpus"


def production_root(base: Path = BASE) -> Path:
    return Path(base) / "frozen" / "production" / "src" / "skill_ir"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    """Manifest paths are portable relative POSIX paths; reject path escapes."""
    item = PurePosixPath(relative)
    if not relative or item.is_absolute() or ".." in item.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe frozen path: {relative!r}")
    path = root.joinpath(*item.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Frozen path escapes root: {relative!r}")
    return path


def tree_inventory(root: Path) -> dict[str, dict]:
    """Hash all archival bytes, excluding Python's interpreter-generated cache."""
    if not root.is_dir() or root.is_symlink():
        raise ValueError(f"Frozen tree missing or symlinked: {root}")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink in frozen tree: {path}")
        # The loader reads *all* members of an input package.  Never hide an
        # added annotation under an apparent cache directory in those inputs.
        relative = path.relative_to(root)
        in_skill_input = relative.parts[:2] == ("corpus", "inputs") or relative.parts[:1] == ("inputs",)
        if ("__pycache__" in relative.parts or path.suffix == ".pyc") and not in_skill_input:
            continue
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {
                "sha256": sha256(path), "bytes": path.stat().st_size
            }
    return result


def inventory_digest(files: dict) -> str:
    canonical = json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_freeze(base: Path = BASE) -> dict:
    """Return the manifest only if archival bytes and approval/splits agree.

    Current production files and the original review folder may evolve later;
    verification is against this self-contained snapshot, never against them.
    The manifest is a provenance lock, not a cryptographic signature.
    """
    base = Path(base)
    manifest = read_json(base / "freeze_manifest.json")
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported freeze manifest schema")
    expected = manifest["files"]
    for relative in expected:
        safe_path(base / "frozen", relative)
    actual = tree_inventory(base / "frozen")
    if actual != expected:
        changed = sorted(set(actual) ^ set(expected) | {
            name for name in set(actual) & set(expected) if actual[name] != expected[name]
        })
        raise ValueError("Frozen content changed: " + ", ".join(changed[:12]))
    if inventory_digest(actual) != manifest["content_sha256"]:
        raise ValueError("Frozen aggregate digest mismatch")
    approval = read_json(base / "approval.json")
    if sha256(base / "approval.json") != manifest["approval_sha256"]:
        raise ValueError("Frozen approval changed")
    if approval["status"] != "jointly_confirmed_reference" or approval["snapshot_id"] != manifest["snapshot_id"]:
        raise ValueError("Frozen approval is not bound to this snapshot")
    catalog = read_json(corpus_root(base) / "corpus.json")
    samples = catalog["samples"]
    if len(samples) != 30 or {sample["id"] for sample in samples} != set(SAMPLE_IDS):
        raise ValueError("Frozen corpus must contain exactly the approved 30 samples")
    if Counter(s["split"] for s in samples) != {"development": 22, "held_out": 8}:
        raise ValueError("Frozen development/held-out split changed")
    if manifest["protocol"] != {"development_samples": 22, "held_out_samples": 8,
                                "repeats_per_sample": 3, "extractions_per_version": 90}:
        raise ValueError("Frozen repetition protocol changed")
    approved = {item["sample_id"]: item for item in approval["samples"]}
    if len(approval["samples"]) != 30 or set(approved) != set(SAMPLE_IDS):
        raise ValueError("Approval does not cover all 30 samples exactly once")
    package_paths = []
    fact_ids = []
    for sample in samples:
        if sample["split"] != ("held_out" if sample["id"] in HELD_OUT else "development"):
            raise ValueError(f"Group split changed: {sample['id']}")
        package = safe_path(corpus_root(base), sample["package_path"])
        annotation_path = safe_path(corpus_root(base), sample["annotation_path"])
        if not package.is_dir() or not (package / "SKILL.md").is_file():
            raise ValueError(f"Missing frozen Skill package: {sample['id']}")
        if not package.is_relative_to(corpus_root(base) / "inputs"):
            raise ValueError("Only individual frozen inputs may be loaded")
        if annotation_path.is_relative_to(package):
            raise ValueError("Frozen annotation leaked inside a Skill input")
        package_paths.append(package)
        annotation = read_json(annotation_path)
        ids = [fact["id"] for fact in annotation["facts"]]
        fact_ids.extend(ids)
        record = approved[sample["id"]]
        if record["annotation_sha256"] != sha256(annotation_path) or record["fact_ids"] != ids:
            raise ValueError(f"Approval does not match frozen facts: {sample['id']}")
        if record["open_questions"] != annotation["open_questions"]:
            raise ValueError(f"Accepted uncertainty changed: {sample['id']}")
        if record["unresolved_fact_ids"] != [f["id"] for f in annotation["facts"] if f["scope"]["level"] == "unresolved"]:
            raise ValueError(f"Accepted unresolved scope changed: {sample['id']}")
    if len(package_paths) != len(set(package_paths)) or any(
        left != right and left.is_relative_to(right) for left in package_paths for right in package_paths
    ):
        raise ValueError("Frozen Skill input roots overlap")
    if len(fact_ids) != 297 or len(set(fact_ids)) != 297 or manifest["fact_count"] != 297:
        raise ValueError("Frozen approval must cover 297 unique facts")
    return manifest


def export_freeze(destination: Path, base: Path = BASE) -> dict:
    """Export the exact archive without recapturing possibly changed live sources."""
    manifest = verify_freeze(base)
    destination = Path(destination)
    if destination.exists():
        raise ValueError(f"Refusing to overwrite export: {destination}")
    if destination.resolve().is_relative_to(Path(base).resolve() / "frozen"):
        raise ValueError("Cannot export inside the immutable frozen tree")
    destination.mkdir(parents=True)
    shutil.copytree(Path(base) / "frozen", destination / "frozen",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in ("approval.json", "freeze_manifest.json"):
        shutil.copyfile(Path(base) / name, destination / name)
    verify_freeze(destination)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--export", type=Path, help="Export exact approved archive into a new directory")
    args = parser.parse_args()
    manifest = export_freeze(args.export, args.base) if args.export else verify_freeze(args.base)
    print(json.dumps({"status": "verified", "snapshot_id": manifest["snapshot_id"],
                      "content_sha256": manifest["content_sha256"],
                      "files": len(manifest["files"]), "facts": manifest["fact_count"],
                      "protocol": manifest["protocol"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
