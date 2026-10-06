"""Safe, lossless-enough loading of Skill directories and ZIP archives."""

from __future__ import annotations

import os
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SkillPackageError(ValueError):
    """Raised when a Skill package cannot be safely loaded."""


class SkillFile(BaseModel):
    """One package member and its decoded content, when it is readable text."""

    model_config = ConfigDict(extra="forbid")

    path: str
    kind: Literal["markdown", "code", "text", "binary"]
    content: str | None = None
    size: int = Field(ge=0)

    @field_validator("path")
    @classmethod
    def normalize_path(cls, value: str) -> str:
        value = value.replace("\\", "/").strip("/")
        if not value or "\x00" in value:
            raise ValueError("file path must be a non-empty relative path")
        return value


class SkillPackage(BaseModel):
    """A normalized Skill package independent of its original storage format."""

    model_config = ConfigDict(extra="forbid")

    root_name: str
    files: list[SkillFile]

    @field_validator("root_name")
    @classmethod
    def normalize_root_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("root_name must not be empty")
        return value

    @field_validator("files")
    @classmethod
    def validate_unique_paths(cls, values: list[SkillFile]) -> list[SkillFile]:
        paths = [item.path for item in values]
        if len(paths) != len(set(paths)):
            raise ValueError("package contains duplicate file paths")
        return values

    def readable_files(self) -> list[SkillFile]:
        """Return files whose complete content can be sent to the LLM."""

        return [item for item in self.files if item.content is not None]


_MARKDOWN_EXTENSIONS = {".md", ".markdown", ".mdx"}
_CODE_EXTENSIONS = {
    ".bash",
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".fish",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".js",
    ".jsx",
    ".kts",
    ".kt",
    ".lua",
    ".m",
    ".mm",
    ".php",
    ".pl",
    ".ps1",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".zsh",
}


def _classify_file(path: str, raw: bytes) -> tuple[str, str | None]:
    suffix = Path(path).suffix.lower()
    if b"\x00" in raw:
        return "binary", None
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "binary", None
    if suffix in _MARKDOWN_EXTENSIONS:
        return "markdown", content
    if suffix in _CODE_EXTENSIONS:
        return "code", content
    return "text", content


def _normalize_relative_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    if "\x00" in normalized or normalized.startswith("/"):
        raise SkillPackageError(f"unsafe package path: {value!r}")
    drive, _ = os.path.splitdrive(normalized)
    if drive:
        raise SkillPackageError(f"unsafe package path: {value!r}")
    parts = PurePosixPath(normalized).parts
    if not parts or parts == (".",) or any(part in {"", ".", ".."} for part in parts):
        raise SkillPackageError(f"unsafe package path: {value!r}")
    return "/".join(parts)


def _strip_single_wrapper(paths: list[str]) -> tuple[str | None, list[str]]:
    if not paths:
        return None, []
    first_parts = [PurePosixPath(path).parts for path in paths]
    first = first_parts[0][0]
    if all(len(parts) > 1 and parts[0] == first for parts in first_parts):
        return first, ["/".join(parts[1:]) for parts in first_parts]
    return None, paths


def _build_file(path: str, raw: bytes) -> SkillFile:
    kind, content = _classify_file(path, raw)
    return SkillFile(path=path, kind=kind, content=content, size=len(raw))


def _load_directory(source: Path) -> SkillPackage:
    members: list[SkillFile] = []
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(source).as_posix()
        members.append(_build_file(relative, path.read_bytes()))
    return SkillPackage(root_name=source.name, files=members)


def _is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def _load_zip(source: Path) -> SkillPackage:
    raw_members: list[tuple[str, bytes]] = []
    seen: set[str] = set()
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            if _is_zip_symlink(info):
                raise SkillPackageError(
                    f"ZIP symlink is not supported: {info.filename!r}"
                )
            path = _normalize_relative_path(info.filename)
            if path in seen:
                raise SkillPackageError(f"duplicate ZIP member: {path!r}")
            seen.add(path)
            raw_members.append((path, archive.read(info)))

    raw_members.sort(key=lambda item: item[0])
    wrapper, normalized_paths = _strip_single_wrapper([path for path, _ in raw_members])
    members = [
        _build_file(path, raw) for path, (_, raw) in zip(normalized_paths, raw_members)
    ]
    return SkillPackage(
        root_name=wrapper or source.stem,
        files=members,
    )


def load_skill_package(source: str | os.PathLike[str]) -> SkillPackage:
    """Load a directory or ZIP without executing any package content."""

    path = Path(source).expanduser().resolve()
    if path.is_dir():
        return _load_directory(path)
    if path.is_file() and zipfile.is_zipfile(path):
        return _load_zip(path)
    raise SkillPackageError(f"input is neither a directory nor a ZIP file: {source}")
