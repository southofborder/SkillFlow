"""Read a Skill once, bind raw bytes separately from decoded model input.

The snapshot contains only the original package. It is not an executable staging
area. Symlinks and Windows reparse points are rejected rather than followed.
"""

from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import stat
from typing import Any
from uuid import uuid4
import zipfile

from skill_ir.source_evidence import _checked_source, _digest, _json_object
from skill_ir.experiments.report import ArtifactWriter
from skill_ir.inputs.skill_package import (
    SkillPackage, SkillPackageError, _build_file, _is_zip_symlink,
    _normalize_relative_path, _strip_single_wrapper, load_skill_package,
)


SNAPSHOT_VERSION = 1


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _no_link(path: Path) -> None:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(
        stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400
    ):
        raise SkillPackageError(f"snapshot does not follow symlinks or reparse points: {path}")


def _member_path(value: str) -> str:
    path = _normalize_relative_path(value)
    # ZIPs are portable inputs, but this snapshot must also be safe on Windows:
    # avoid alternate streams, device names, and aliases caused by trailing dots.
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    for part in PurePosixPath(path).parts:
        if (any(character in '<>:"|?*' or ord(character) < 32 for character in part)
                or part.endswith((".", " "))
                or part.split(".", 1)[0].upper() in reserved):
            raise SkillPackageError(f"unsafe portable package path: {value!r}")
    return path


def _collect(input_path: str | Path) -> tuple[dict[str, Any], list[tuple[str, bytes]]]:
    original = Path(input_path).expanduser().absolute()
    _no_link(original)
    original = original.resolve(strict=True)
    members: list[tuple[str, bytes]] = []
    if original.is_dir():
        # Walk without following links, and reject links even when they are
        # directories that os.walk would otherwise silently skip.
        for directory, folders, files in os.walk(original, followlinks=False):
            for name in folders + files:
                _no_link(Path(directory) / name)
            for name in files:
                file = Path(directory) / name
                if not file.is_file():
                    raise SkillPackageError(f"unsupported non-regular package member: {file}")
                members.append((_member_path(file.relative_to(original).as_posix()), file.read_bytes()))
        storage = "directory"
        root_name = original.name
        archive_sha256 = None
    elif original.is_file():
        raw_archive = original.read_bytes()
        archive_sha256 = _sha(raw_archive)
        storage = "zip"
        seen: set[str] = set()
        try:
            with zipfile.ZipFile(io.BytesIO(raw_archive)) as archive:
                for info in archive.infolist():
                    path = _member_path(info.filename.rstrip("/"))
                    if _is_zip_symlink(info):
                        raise SkillPackageError(f"ZIP symlink is not supported: {info.filename!r}")
                    if info.is_dir():
                        continue
                    if path in seen:
                        raise SkillPackageError(f"duplicate ZIP member: {path!r}")
                    seen.add(path)
                    members.append((path, archive.read(info)))
        except zipfile.BadZipFile as error:
            raise SkillPackageError("input is neither a directory nor a valid ZIP file") from error
        members.sort(key=lambda item: item[0])
        wrapper, paths = _strip_single_wrapper([path for path, _ in members])
        members = [(path, raw) for path, (_, raw) in zip(paths, members)]
        root_name = wrapper or original.stem
    else:
        raise SkillPackageError("input is neither a directory nor a ZIP file")
    members.sort(key=lambda item: item[0])
    folded: set[str] = set()
    for path, _ in members:
        folded_path = path.casefold()
        if folded_path in folded:
            raise SkillPackageError(f"case-insensitive package path collision: {path!r}")
        folded.add(folded_path)
    for path in folded:
        if any(parent.as_posix() in folded for parent in PurePosixPath(path).parents if str(parent) != "."):
            raise SkillPackageError(f"package file/directory collision: {path!r}")
    return {"original_path": str(original), "storage": storage, "root_name": root_name,
            "archive_sha256": archive_sha256}, members


def _describe(identity: dict[str, Any], members: list[tuple[str, bytes]]) -> tuple[SkillPackage, dict, dict]:
    package = SkillPackage(root_name=identity["root_name"], files=[_build_file(path, raw) for path, raw in members])
    entries = []
    source_files = []
    for file, (path, raw) in zip(package.files, members):
        decoded = _sha(file.content.encode("utf-8")) if file.content is not None else None
        entries.append({"path": path, "size": len(raw), "kind": file.kind,
                        "raw_sha256": _sha(raw), "decoded_sha256": decoded})
        if file.content is not None:
            source_files.append({"path": path, "content": file.content, "sha256": decoded})
    source = {"files": source_files, "source_sha256": _digest(
        [{"path": item["path"], "sha256": item["sha256"]} for item in source_files])}
    _checked_source(source)
    raw_identity = [{key: entry[key] for key in ("path", "size", "raw_sha256")} for entry in entries]
    metadata = {
        "schema_version": SNAPSHOT_VERSION, **identity, "files": entries,
        "package_bytes_sha256": _digest(raw_identity),
        "source_sha256": source["source_sha256"],
        "boundaries": {
            "binary_files": [entry["path"] for entry in entries if entry["decoded_sha256"] is None],
            "uninterpreted_code_files": [entry["path"] for entry in entries if entry["kind"] == "code"],
            "notice": "提取和核对共享全部可读文件。二进制未进入文本语义核对；代码及嵌入内容不因此获得执行正确性或行为理解保证。",
        },
    }
    metadata["snapshot_sha256"] = _digest(metadata)
    return package, source, metadata


def _preserve_secrets(value: Any, writer: ArtifactWriter) -> None:
    if writer.clean(value) != value:
        raise ValueError("input contains a configured credential; redaction would change frozen source identity")


def freeze_input(input_path: str | Path, directory: str | Path, writer: ArtifactWriter) -> dict[str, Any]:
    """Save one byte snapshot, with the exact same readable input for both roles."""
    directory = Path(directory).resolve()
    inputs = directory / "inputs"
    if inputs.exists():
        raise ValueError("input snapshot already exists; read and verify it instead of overwriting")
    identity, members = _collect(input_path)
    if identity["storage"] == "directory" and directory.is_relative_to(Path(identity["original_path"])):
        raise ValueError("run directory must not be nested inside the Skill input")
    _, source, metadata = _describe(identity, members)
    _preserve_secrets(source, writer)
    _preserve_secrets(metadata, writer)
    for _, raw in members:
        if any(secret and secret.encode("utf-8") in raw for secret in writer.secrets):
            raise ValueError("raw package contains a configured credential; cannot persist changed bytes")
    for path, raw in members:
        target = inputs / "package" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
        try:
            temporary.write_bytes(raw)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    writer.json(inputs / "source.json", source)
    writer.json(inputs / "snapshot.json", metadata)
    read_snapshot(directory)
    return metadata


def _read_metadata(directory: Path) -> dict[str, Any]:
    metadata = _json_object((directory / "inputs" / "snapshot.json").read_text(encoding="utf-8"))
    if metadata.get("schema_version") != SNAPSHOT_VERSION:
        raise ValueError("unsupported input snapshot version")
    payload = {key: value for key, value in metadata.items() if key != "snapshot_sha256"}
    if metadata.get("snapshot_sha256") != _digest(payload):
        raise ValueError("input snapshot manifest digest mismatch")
    return metadata


def read_snapshot(directory: str | Path) -> tuple[SkillPackage, dict[str, Any], dict[str, Any]]:
    """Offline snapshot verification; never read the original path or use an API."""
    directory = Path(directory).resolve()
    metadata = _read_metadata(directory)
    package_path = directory / "inputs" / "package"
    _, members = _collect(package_path)
    identity = {key: metadata[key] for key in ("original_path", "storage", "root_name", "archive_sha256")}
    package, source, observed = _describe(identity, members)
    if observed != metadata:
        raise ValueError("frozen package bytes, source inventory, or decoded text digest changed")
    source_path = directory / "inputs" / "source.json"
    if _json_object(source_path.read_text(encoding="utf-8")) != source:
        raise ValueError("saved source bundle does not match the frozen package")
    # Reuse the public loader too: its normalized file contract must agree with
    # the exact byte snapshot used to derive the audit source bundle.
    loaded = load_skill_package(package_path)
    loaded.root_name = metadata["root_name"]
    if loaded != package:
        raise ValueError("snapshot loader and decoded source representation disagree")
    return package, source, metadata


def verify_original_input(input_path: str | Path | None, metadata: dict[str, Any]) -> None:
    """Online resume rejects changes in original raw bytes, archive, or inventory."""
    identity, members = _collect(input_path if input_path is not None else metadata["original_path"])
    _, _, observed = _describe(identity, members)
    if observed != metadata:
        raise ValueError("original Skill identity changed; refuse to continue this run")
