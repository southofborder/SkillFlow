"""Lazy project resources and exact, digest-checked historical material paths.

Historical addresses are resolved only by the sealed layout ledger. New explicit
paths keep their existing external-input behavior; stage-specific loaders remain
responsible for their input contracts.
"""
from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path, PurePosixPath
import stat
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 remains supported by the package.
    import tomli as tomllib


def project_root(start: str | Path | None = None) -> Path:
    """Find the nearest root pyproject identifying this project as skillflow.

    No import-time traversal or fixed parent depth is used. Installed clients can
    identify a checked-out project from the working directory.
    """
    starts = [Path(start)] if start is not None else [Path(__file__), Path.cwd()]
    visited: set[Path] = set()
    for beginning in starts:
        beginning = beginning.expanduser().resolve()
        beginning = beginning.parent if beginning.is_file() else beginning
        for candidate in (beginning, *beginning.parents):
            if candidate in visited:
                continue
            visited.add(candidate)
            marker = candidate / "pyproject.toml"
            if not marker.is_file():
                continue
            try:
                with marker.open("rb") as handle:
                    definition = tomllib.load(handle)
            except (OSError, tomllib.TOMLDecodeError) as error:
                raise ValueError(f"Cannot read project marker: {marker}") from error
            if definition.get("project", {}).get("name") == "skillflow":
                return candidate
    raise FileNotFoundError("No pyproject.toml with project.name='skillflow' identifies the project root")


def formal_root() -> Path:
    return project_root() / "formal"


def _address(value: str | Path) -> str:
    value = os.fspath(value)
    if not isinstance(value, str) or not value:
        raise ValueError("Material address must be nonempty text")
    # Ledger matching is exact except for portable path separators. Do not
    # collapse '..', guess prefixes, infer names, or change manifest identities.
    return value.replace("\\", "/").rstrip("/")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checked_target(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in {".", ".."} for part in path.parts):
        raise ValueError("Historical target is not a safe repository-relative path")
    if ":" in str(path):
        raise ValueError("Historical target contains a drive or alternate stream")
    target = root.joinpath(*path.parts)
    current = root
    for part in path.parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError as error:
            raise FileNotFoundError(f"Mapped material is missing: {current}") from error
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(
            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400,
        ):
            raise ValueError(f"Historical mapping does not follow links or reparse points: {current}")
    resolved = target.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Historical material target leaves the repository")
    return resolved


@lru_cache(maxsize=8)
def _read_ledger(manifest: Path, mtime_ns: int, size: int):
    # Identity metadata keys invalidate parsing caches; file bytes are always
    # rechecked by _checked_file, never replaced by this metadata cache.
    try:
        value = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read historical material ledger: {manifest}") from error
    if not isinstance(value, dict) or not isinstance(value.get("files"), list) or not isinstance(
        value.get("directories"), list,
    ):
        raise ValueError(f"Invalid historical material ledger: {manifest}")
    index = {}
    for category in ("files", "directories"):
        for item in value[category]:
            if not isinstance(item, dict):
                raise ValueError(f"Invalid historical material entry: {manifest}")
            try:
                addresses = {_address(item["old_relative"]), _address(item["old_absolute"])}
            except KeyError as error:
                raise ValueError(f"Historical entry lacks its exact original address: {manifest}") from error
            for address in addresses:
                index.setdefault(address, []).append((category, item))
    return value, index


def _ledgers(root: Path):
    for manifest in sorted((root / "experiments/migrations").glob("layout-v1-*/manifest.json")):
        info = manifest.stat()
        value, index = _read_ledger(manifest, info.st_mtime_ns, info.st_size)
        yield manifest, value, index


def _matches(root: Path, address: str):
    matches = []
    for manifest, ledger, index in _ledgers(root):
        matches.extend((manifest, ledger, category, item) for category, item in index.get(address, []))
    if len(matches) > 1:
        raise ValueError(f"Historical material address is ambiguous across ledgers: {address}")
    return matches[0] if matches else None


def _checked_file(root: Path, item: dict, expected: str | None) -> Path:
    target = _checked_target(root, item["new_relative"])
    if not target.is_file():
        raise ValueError("Mapped file is not a regular file")
    digest = item.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Historical file ledger lacks a valid SHA-256")
    actual = _sha(target)
    if actual != digest or (expected is not None and actual != expected):
        raise ValueError(f"Historical material digest mismatch: {target}")
    return target


def resolve_material_path(
    address: str | Path, *, base: str | Path | None = None, expected_sha256: str | None = None,
) -> Path:
    """Resolve an exact historical address or an explicit current material path.

    A mapped directory verifies every file in its sealed historical membership.
    It is not a prefix alias for unknown descendants. SHA arguments describe file
    bytes; directory package identities must still be checked by the package
    loader rather than inventing a second directory hash.
    """
    normalized = _address(address)
    explicit = Path(address).expanduser()
    if not explicit.is_absolute() and base is not None:
        explicit = Path(base).expanduser() / explicit
    if explicit.is_absolute() and explicit.exists():
        resolved = explicit.resolve()
        if expected_sha256 is not None and (not resolved.is_file() or _sha(resolved) != expected_sha256):
            raise ValueError(f"Material digest mismatch: {resolved}")
        return resolved
    root = project_root()
    match = _matches(root, normalized)
    if match is not None:
        _, ledger, category, item = match
        if category == "files":
            return _checked_file(root, item, expected_sha256)
        if expected_sha256 is not None:
            raise ValueError("A raw file SHA-256 cannot identify a mapped directory")
        target = _checked_target(root, item["new_relative"])
        if not target.is_dir():
            raise ValueError("Mapped directory is not a directory")
        old_directory = PurePosixPath(_address(item["old_relative"]))
        for member in ledger["files"]:
            original = PurePosixPath(_address(member["old_relative"]))
            if original.is_relative_to(old_directory):
                mapped = _checked_file(root, member, None)
                if not mapped.is_relative_to(target):
                    raise ValueError("Historical directory member maps outside its declared target")
        return target
    path = Path(address).expanduser()
    if not path.is_absolute():
        path = (Path(base) if base is not None else root) / path
    resolved = path.resolve()
    # Unknown old names must not be resolved by prefix substitution. Existing
    # user-supplied paths still work; missing paths raise without guessed lookup.
    if not resolved.exists():
        raise FileNotFoundError(f"Material address is missing and has no exact historical mapping: {address}")
    if expected_sha256 is not None:
        if not resolved.is_file() or _sha(resolved) != expected_sha256:
            raise ValueError(f"Material digest mismatch: {resolved}")
    return resolved
