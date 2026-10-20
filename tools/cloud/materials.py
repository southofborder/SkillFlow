"""Seal and verify the exact submitted material files for cloud preparation.

Creation reads Git's index, including newly staged files, within explicit roots.
It never stages files, rewrites frozen artifacts, resumes a run, or calls models.
Verification reads exact paths and bytes without requiring Git or old producers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

from skillflow.common.paths import project_root


SCHEMA = "skillflow-cloud-materials-v1"
DEFAULT_MANIFEST = "experiments/configs/cloud-materials-v1.json"


def _relative(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value or "\x00" in value:
        raise ValueError("A material path must be an exact repository-relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError(f"Unsafe material path: {value!r}")
    return path


def _unique_paths(values: list[str]) -> None:
    if len(values) != len(set(values)):
        raise ValueError("Duplicate material paths are forbidden")
    spelling = {}
    for value in values:
        path = _relative(value)
        for length in range(1, len(path.parts) + 1):
            prefix = "/".join(path.parts[:length])
            previous = spelling.setdefault(prefix.casefold(), prefix)
            if previous != prefix:
                raise ValueError(f"Case-colliding material paths: {previous!r}, {prefix!r}")


def _checked(root: Path, value: str, *, file: bool = False) -> Path:
    path = root
    for part in _relative(value).parts:
        path = path / part
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(
            stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400,
        ):
            raise ValueError(f"Material links and reparse points are forbidden: {value}")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"A material path leaves the project: {value}")
    if file and not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"A material entry is not a regular file: {value}")
    return path


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_manifest(root: Path, roots: list[str], output: Path) -> dict:
    """Freeze working-tree bytes for exactly the Git-index files in the roots."""
    root = root.resolve()
    output = output.absolute()
    if not output.is_relative_to(root):
        raise ValueError("The material manifest must remain within the project")
    _relative(output.relative_to(root).as_posix())
    if output.parent != root:
        _checked(root, output.parent.relative_to(root).as_posix())
    if not roots:
        raise ValueError("At least one explicit material root is required")
    _unique_paths(roots)
    for value in roots:
        _checked(root, value)
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--", *roots],
        check=True, capture_output=True, stdin=subprocess.DEVNULL,
    )
    names = sorted(name for name in result.stdout.decode("utf-8").split("\x00") if name)
    _unique_paths(names)
    _unique_paths(list(dict.fromkeys(roots + names)))
    if any(not any(PurePosixPath(name).is_relative_to(PurePosixPath(value)) for value in roots)
           for name in names):
        raise ValueError("An indexed file is outside the requested roots")
    if not names or any(not any(PurePosixPath(name).is_relative_to(PurePosixPath(value))
                               for name in names) for value in roots):
        raise ValueError("Every material root must contain at least one indexed file")
    files = []
    for name in names:
        path = _checked(root, name, file=True)
        if path.resolve() == output.resolve():
            raise ValueError("A material manifest cannot include itself")
        files.append({"path": name, "bytes": path.stat().st_size, "sha256": _digest(path)})
    manifest = {"schema_version": SCHEMA, "roots": sorted(roots), "files": files}
    # Exclusive creation prevents replacing an existing seal. No input is edited.
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    return manifest


def _load(path: Path) -> dict:
    def unique(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError(f"Duplicate manifest key: {key}")
            value[key] = item
        return value

    def invalid(value):
        raise ValueError(f"Invalid JSON constant in manifest: {value}")

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=invalid)
    if not isinstance(value, dict) or set(value) != {"schema_version", "roots", "files"}:
        raise ValueError("Unexpected cloud material manifest structure")
    if value["schema_version"] != SCHEMA:
        raise ValueError("Unsupported cloud material manifest version")
    roots, files = value["roots"], value["files"]
    if not isinstance(roots, list) or not roots or any(not isinstance(item, str) for item in roots):
        raise ValueError("Material roots must be a nonempty path list")
    if not isinstance(files, list) or not files:
        raise ValueError("Material files must be a nonempty list")
    _unique_paths(roots)
    names = []
    for item in files:
        if not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"}:
            raise ValueError("Unexpected material file entry")
        _relative(item["path"])
        if type(item["bytes"]) is not int or item["bytes"] < 0:
            raise ValueError("Material byte count must be a nonnegative integer")
        if not isinstance(item["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None:
            raise ValueError("Material SHA-256 must contain 64 lowercase hexadecimal characters")
        names.append(item["path"])
    _unique_paths(names)
    _unique_paths(list(dict.fromkeys(roots + names)))
    if any(not any(PurePosixPath(name).is_relative_to(PurePosixPath(value)) for value in roots)
           for name in names):
        raise ValueError("A material file is outside all declared roots")
    if any(not any(PurePosixPath(name).is_relative_to(PurePosixPath(value)) for name in names)
           for value in roots):
        raise ValueError("A material root has no declared files")
    return value


def verify_manifest(root: Path, manifest_path: Path) -> dict:
    manifest = _load(manifest_path)
    errors = []
    total = 0
    for item in manifest["files"]:
        try:
            path = _checked(root.resolve(), item["path"], file=True)
            size = path.stat().st_size
            if size != item["bytes"] or _digest(path) != item["sha256"]:
                errors.append({"path": item["path"], "error": "content_mismatch"})
            total += size
        except FileNotFoundError:
            errors.append({"path": item["path"], "error": "missing_file"})
        except (OSError, ValueError) as error:
            errors.append({"path": item["path"], "error": str(error)})
    return {
        "status": "passed" if not errors else "failed",
        "file_count": len(manifest["files"]),
        "actual_bytes": total,
        "errors": errors,
        "model_requests": 0,
        "scope": "Exact submitted material bytes only; no historical resume or semantic validation.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, help="A path within the SkillFlow checkout")
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="Check declared bytes without model calls")
    verify.add_argument("--manifest", default=DEFAULT_MANIFEST)
    create = commands.add_parser("create", help="Seal indexed files under explicit roots; never overwrite")
    create.add_argument("--root", action="append", required=True, dest="roots")
    create.add_argument("--manifest", default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    try:
        root = project_root(args.project if args.project is not None else Path(__file__))
        target = root.joinpath(*_relative(args.manifest).parts)
        # Validate each existing parent without following links, including outputs.
        if target.parent != root:
            _checked(root, target.parent.relative_to(root).as_posix())
        if target.exists() or target.is_symlink():
            _checked(root, args.manifest, file=True)
        if args.command == "create":
            create_manifest(root, args.roots, target)
        report = verify_manifest(root, target)
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "passed" else 1
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({"status": "failed", "error": str(error), "model_requests": 0}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
