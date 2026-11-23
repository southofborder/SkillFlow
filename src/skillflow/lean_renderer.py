"""Build and check the controlled CFG printer/parser with the pinned Lean toolchain."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

from skillflow.common.paths import formal_root


BUILD_COMMAND = "python -m skillflow.lean_renderer"
RENDERER_ENV = "SKILLFLOW_LEAN_RENDERER"


def source_files(root: Path) -> dict[str, Path]:
    files = [root / name for name in ("lean-toolchain", "lakefile.toml", "lake-manifest.json")]
    files.extend(root.glob("*.lean"))
    files.extend((root / "SkillIR").rglob("*.lean"))
    return {path.relative_to(root).as_posix(): path for path in sorted(files)}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_id(files: dict[str, Path]) -> str:
    digests = {name: file_sha256(path) for name, path in files.items()}
    return hashlib.sha256(json.dumps(digests, sort_keys=True).encode()).hexdigest()


def _default_build(source_id: str) -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local"
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Caches"
    else:
        base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "skillflow/lean" / f"{sys.platform}-{platform.machine()}" / source_id


def _product(directory: Path) -> Path:
    name = "skill_ir_retell.exe" if os.name == "nt" else "skill_ir_retell"
    return directory / ".lake/build/bin" / name


def renderer_path(executable: str | Path | None = None) -> Path:
    selected = executable if executable is not None else os.environ.get(RENDERER_ENV)
    if selected is not None:
        path = Path(selected).expanduser().resolve()
    else:
        root = formal_root()
        source_id = _source_id(source_files(root))
        directory = _default_build(source_id)
        path = _checked_product(directory, source_id) if directory.exists() else _product(root)
    if not path.is_file():
        raise ValueError(f"Lean retelling executable does not exist at {path}. "
                         f"Build it with '{BUILD_COMMAND}' or set {RENDERER_ENV} to a verified build.")
    return path.resolve()


def launch_error(path: str | Path, error: OSError) -> str:
    code = getattr(error, "winerror", None)
    if code in {577, 1260, 4551}:
        return (f"Windows application control blocked {path} (WinError {code}). "
                "Use a toolchain and renderer approved for this device, or build and validate "
                "in an approved environment. Check the CodeIntegrity Operational log for the named file.")
    return f"Could not start {path}: {error}"


def _checked_product(directory: Path, source_id: str) -> Path:
    binary = _product(directory)
    try:
        receipt = json.loads((directory / "build.json").read_bytes())
        if (isinstance(receipt, dict) and receipt.get("source_sha256") == source_id
                and receipt.get("binary_sha256") == file_sha256(binary)):
            return binary
    except (OSError, ValueError):
        pass
    raise ValueError(f"Missing or mismatched Lean build receipt in {directory}. "
                     f"Use '{BUILD_COMMAND} --build-dir NEW_DIRECTORY' for a fresh build.")


def _run(command: list[str], cwd: Path, env: dict[str, str]) -> str:
    try:
        proc = subprocess.run(command, cwd=cwd, env=env, capture_output=True, check=False)
    except OSError as error:
        raise ValueError(launch_error(command[0], error)) from error
    messages = (proc.stdout + proc.stderr).decode("utf-8", errors="replace").strip()
    if proc.returncode:
        raise ValueError(f"{subprocess.list2cmdline(command)} exited {proc.returncode} in {cwd}.\n{messages}")
    return messages


def _tool_commands(toolchain_bin: Path | None, pin: str, env: dict[str, str]) -> tuple[list[str], list[str]]:
    if toolchain_bin is None:
        elan = shutil.which("elan")
        if elan:
            # Elan's 'run' requires an already-installed toolchain unless '--install' is passed.
            return [elan, "run", pin, "lean"], [elan, "run", pin, "lake"]
        lean = shutil.which("lean")
        if lean:
            toolchain_bin = Path(lean).parent
    if toolchain_bin is not None:
        directory = toolchain_bin.expanduser().resolve()
        suffix = ".exe" if os.name == "nt" else ""
        lean, lake = (directory / (name + suffix) for name in ("lean", "lake"))
        if lean.is_file() and lake.is_file():
            env["PATH"] = os.pathsep.join([str(directory), env.get("PATH", "")])
            return [str(lean)], [str(lake)]
    location = f" in {toolchain_bin}" if toolchain_bin is not None else ""
    raise ValueError(f"Lean and Lake for {pin} were not found{location}. "
                     f"Install it with 'elan toolchain install {pin}' or pass --toolchain-bin "
                     "pointing to the bin directory of an approved official toolchain.")


def _verify(binary: Path) -> dict:
    from skillflow.graph.audit.controlled import render_controlled, verify_controlled
    from skillflow.graph.ir.cfg import ControlFlowGraph

    cfg = ControlFlowGraph.model_validate({
        "entry_block_id": "entry",
        "blocks": {"entry": {"block_id": "entry", "block_name": "Renderer verification",
                             "instructions": [{"id": "ir_return", "opcode": "return"}]}},
    })
    document = render_controlled(cfg, executable=binary)
    return verify_controlled(document, cfg=cfg, executable=binary)


def build_renderer(toolchain_bin: Path | None = None, build_dir: Path | None = None) -> Path:
    root = formal_root()
    files = source_files(root)
    source_id = _source_id(files)
    directory = build_dir.expanduser().resolve() if build_dir is not None else _default_build(source_id)
    if directory.exists():
        binary = _checked_product(directory, source_id)
        _verify(binary)
        return binary

    pin = files["lean-toolchain"].read_text(encoding="utf-8").strip()
    release = re.fullmatch(r"leanprover/lean4:v([0-9]+\.[0-9]+\.[0-9]+(?:-rc[0-9]+)?)", pin)
    if not release:
        raise ValueError(f"Expected an exact official Lean release in lean-toolchain, found {pin!r}")
    env = os.environ.copy()
    lean, lake = _tool_commands(toolchain_bin, pin, env)
    version = _run([*lean, "--version"], root, env)
    if not re.search(r"^Lean \(version " + re.escape(release[1]) + r"[,)]", version, re.MULTILINE):
        raise ValueError(f"Expected {pin}, got {version!r}. Select the pinned compiler with --toolchain-bin.")
    lake_version = _run([*lake, "--version"], root, env)
    if f"(Lean version {release[1]})" not in lake_version:
        raise ValueError(f"Expected Lake built for {pin}, got {lake_version!r}.")

    directory.parent.mkdir(parents=True, exist_ok=True)
    # Only build with the source/configuration above. A copied checkout can contain old native objects.
    stage = Path(tempfile.mkdtemp(dir=directory.parent, prefix="build-"))
    try:
        for name, path in files.items():
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        if _source_id(source_files(stage)) != source_id:
            raise ValueError("Lean sources changed while preparing the build. Retry with a stable checkout.")
        _run([*lake, "build", "skill_ir_retell"], stage, env)
        product = _product(stage)
        if not product.is_file():
            raise ValueError(f"Lake succeeded without producing the expected renderer at {product}")
        certificate = _verify(product)
        if _source_id(source_files(root)) != source_id:
            raise ValueError("Lean sources changed during verification. Retry with a stable checkout.")
        receipt = {"toolchain": pin, "lean_version": version, "lake_version": lake_version,
                   "source_sha256": source_id, "binary_sha256": certificate["binary_sha256"],
                   "roundtrip_graph_sha256": certificate["graph_sha256"]}
        (stage / "build.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as error:
        raise ValueError(f"{error}\nUnpublished build kept at {stage} for inspection.") from error
    try:
        stage.rename(directory)
    except OSError:
        if not directory.exists():
            raise
        # A concurrent builder may have published its own complete verified product.
        binary = _checked_product(directory, source_id)
        _verify(binary)
        shutil.rmtree(stage)
        return binary
    return _checked_product(directory, source_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toolchain-bin", type=Path, help="bin directory of the installed pinned Lean release")
    parser.add_argument("--build-dir", type=Path, help="new build directory (default: per-user source and platform cache)")
    args = parser.parse_args(argv)
    try:
        print(build_renderer(args.toolchain_bin, args.build_dir))
    except (ValueError, OSError) as error:
        print(f"Lean renderer setup failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
