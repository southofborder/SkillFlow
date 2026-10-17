"""Exact, digest-bound run references that survive moving a run directory tree."""
from __future__ import annotations

import os
from pathlib import Path

from skillflow.common.recording import canonical_sha256
from skillflow.common.source_evidence import _json_object


def checked_run_path(value) -> Path:
    """Resolve an explicitly supplied path without following links or junctions."""
    path = Path(value).expanduser().absolute()
    for candidate in (path, *path.parents):
        try:
            status = candidate.lstat()
        except FileNotFoundError:
            continue
        if candidate.is_symlink() or getattr(status, "st_file_attributes", 0) & 0x400:
            raise ValueError("Run references cannot follow links or reparse points")
    return path.resolve()


def _manifest(path):
    file = path / "manifest.json"
    checked_run_path(file)
    value = _json_object(file.read_bytes().decode("utf-8"))
    digest = value.get("manifest_sha256")
    if (type(digest) is not str or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
            or canonical_sha256({k: v for k, v in value.items() if k != "manifest_sha256"}) != digest):
        raise ValueError("Upstream run manifest identity is invalid")
    return value


def make_run_reference(owner, upstream) -> dict:
    """Bind a run by its sealed manifest; the locator is not content identity."""
    owner, upstream = checked_run_path(owner), checked_run_path(upstream)
    manifest = _manifest(upstream)
    try:
        address = Path(os.path.relpath(upstream, owner)).as_posix()
    except ValueError:  # Explicit references on different Windows drives.
        address = upstream.as_posix()
    return {"path": address, "manifest_sha256": manifest["manifest_sha256"]}


def resolve_run_reference(owner, reference) -> Path:
    """Resolve only this address and verify its manifest; never search by name."""
    if (type(reference) is not dict or set(reference) != {"path", "manifest_sha256"}
            or type(reference["path"]) is not str or not reference["path"]
            or "\\" in reference["path"]):
        raise ValueError("Invalid upstream run reference")
    address = Path(reference["path"])
    target = checked_run_path(address if address.is_absolute() else checked_run_path(owner) / address)
    manifest = _manifest(target)
    if manifest["manifest_sha256"] != reference["manifest_sha256"]:
        raise ValueError("Upstream run identity differs from the saved reference")
    return target
