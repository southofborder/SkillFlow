#!/usr/bin/env python3
"""Verify, or restore, the six byte-exact upstream snapshots (standard library only).

Default operation is offline. --fetch downloads only commit-pinned raw files listed
in upstream-lock.json, verifies Git blob IDs before writing, and never executes
package code or follows package links. --write-manifests rebuilds external metadata.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "49f948faa9258a0c61caceaf225e179651397431"
REPOSITORY = "https://github.com/openai/skills"
SELECTION = (
    ("R01", "pdf", "development"),
    ("R02", "playwright", "development"),
    ("R03", "gh-fix-ci", "development"),
    ("R04", "netlify-deploy", "development"),
    ("R05", "linear", "held_out"),
    ("R06", "transcribe", "held_out"),
)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def readable_text(raw: bytes) -> str | None:
    """Match the production loader's NUL and UTF-8-sig decoding boundary."""
    if b"\0" in raw:
        return None
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise ValueError(f"Unsafe upstream path: {value}")
    return path


def load_lock() -> dict:
    lock = json.loads((ROOT / "provenance/upstream-lock.json").read_text(encoding="utf-8"))
    if lock["commit"] != COMMIT or lock["repository"] != REPOSITORY:
        raise ValueError("Lock does not identify the fixed review snapshot")
    expected = {f"skills/.curated/{name}" for _, name, _ in SELECTION}
    if set(lock["package_paths"]) != expected:
        raise ValueError("Lock package selection differs from the six review samples")
    if len({entry["path"] for entry in lock["files"]}) != len(lock["files"]):
        raise ValueError("Duplicate lock path")
    for entry in lock["files"]:
        path = safe_relative(entry["path"])
        if entry["mode"] not in {"100644", "100755"} or entry["type"] != "blob":
            raise ValueError(f"Unsupported upstream member: {path}")
        if str(path) != "README.md" and not any(str(path).startswith(p + "/") for p in expected):
            raise ValueError(f"Unselected upstream member: {path}")
    return lock


def destination(entry: dict) -> Path:
    path = safe_relative(entry["path"])
    if str(path) == "README.md":
        return ROOT / "provenance/upstream-README.md"
    return ROOT / "inputs/upstream" / Path(*path.parts[2:])


def validate_bytes(entry: dict, raw: bytes) -> None:
    if len(raw) != entry["size"] or blob_sha(raw) != entry["sha"]:
        raise ValueError(f"Pinned Git blob verification failed: {entry['path']}")


def fetch_file(entry: dict) -> None:
    url = f"https://raw.githubusercontent.com/openai/skills/{COMMIT}/{entry['path']}"
    request = urllib.request.Request(url, headers={"User-Agent": "SkillFlow-semantics-review-vendor"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    validate_bytes(entry, raw)
    target = destination(entry)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def external_links(records: list[dict], package_dir: Path) -> list[dict]:
    """Inventory literal HTTP(S) links as unavailable context, never fetch them."""
    links = []
    for record in records:
        content = readable_text((package_dir / record["path"]).read_bytes())
        if content is None:
            continue
        for number, line in enumerate(content.splitlines(), 1):
            for url in sorted(set(re.findall(r"https?://[^\s<>\"'`]+", line))):
                links.append({"file": record["path"], "line": number,
                              "url": url.rstrip(".,;:)]}"),
                              "provided_as_input": False,
                              "status": "not_fetched"})
    return links


def metadata(lock: dict) -> tuple[list[dict], dict[str, dict]]:
    inventory = []
    manifests = {}
    for sample_id, name, split in SELECTION:
        upstream_path = f"skills/.curated/{name}"
        package_path = f"inputs/upstream/{name}"
        package_dir = ROOT / package_path
        records = []
        for entry in lock["files"]:
            if not entry["path"].startswith(upstream_path + "/"):
                continue
            path = entry["path"][len(upstream_path) + 1:]
            raw = (package_dir / path).read_bytes()
            validate_bytes(entry, raw)
            content = readable_text(raw)
            record = {"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                      "git_blob_sha": entry["sha"], "git_mode": entry["mode"], "loader_readable": content is not None,
                      "line_count": len(content.splitlines()) if content is not None else None}
            if content is None:
                record["omission_reason"] = "contains_nul_or_not_utf8"
            records.append(record)
        records.sort(key=lambda row: row["path"])
        actual = {p.relative_to(package_dir).as_posix() for p in package_dir.rglob("*") if p.is_file()}
        if actual != {row["path"] for row in records}:
            raise ValueError(f"Unexpected/missing files in {package_path}: {actual ^ {row['path'] for row in records}}")
        if any(p.is_symlink() for p in package_dir.rglob("*")):
            raise ValueError(f"Symlink in {package_path}")
        manifests[sample_id] = {
            "schema_version": 1, "sample_id": sample_id, "repository": REPOSITORY,
            "commit": COMMIT, "upstream_path": upstream_path,
            "source_url": f"{REPOSITORY}/tree/{COMMIT}/{upstream_path}",
            "package_path": package_path, "split": split,
            "snapshot_policy": "Exact original package bytes; no scripts executed; no links fetched.",
            "files": records,
            "readable_files": [row["path"] for row in records if row["loader_readable"]],
            "omitted_files": [row["path"] for row in records if not row["loader_readable"]],
            "external_links": external_links(records, package_dir),
            "license": {"package_files": [row["path"] for row in records
                                            if Path(row["path"]).name in {"LICENSE.txt", "NOTICE.txt"}],
                        "repository_root_license": None,
                        "repository_license_statement": "provenance/upstream-README.md",
                        "note": "Upstream has no root license; README directs readers to each Skill's LICENSE.txt."},
        }
        inventory.append({"id": sample_id, "title": name, "kind": "upstream", "group": "upstream",
                          "expression": "original", "language": "en", "split": split,
                          "package_path": package_path, "annotation_path": f"annotations/{sample_id}.json",
                          "provenance_path": f"provenance/{sample_id}.json"})
    return inventory, manifests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Restore only locked commit-pinned files from GitHub")
    parser.add_argument("--write-manifests", action="store_true", help="Regenerate external provenance and sample inventory")
    args = parser.parse_args()
    lock = load_lock()
    if args.fetch:
        with ThreadPoolExecutor(max_workers=6) as executor:
            list(executor.map(fetch_file, lock["files"]))
    for entry in lock["files"]:
        validate_bytes(entry, destination(entry).read_bytes())
    inventory, manifests = metadata(lock)
    expected = {ROOT / "upstream_samples.json": inventory}
    expected.update({ROOT / f"provenance/{sample_id}.json": value for sample_id, value in manifests.items()})
    for target, value in expected.items():
        encoded = json_bytes(value)
        if args.write_manifests:
            target.write_bytes(encoded)
        elif target.read_bytes() != encoded:
            raise ValueError(f"Metadata differs from the verified snapshot: {target.relative_to(ROOT)}")
    for sample_id, manifest in manifests.items():
        files = manifest["files"]
        print(f"{sample_id}: {len(files)} files, {sum(row['bytes'] for row in files)} bytes, "
              f"{len(manifest['readable_files'])} readable, {sum(row['line_count'] or 0 for row in files)} readable lines")
    print("Verified six pinned snapshots, package licenses, and external provenance.")


if __name__ == "__main__":
    main()
