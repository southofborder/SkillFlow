"""Semia + complete-source: bounded file-inclusion adaptation, no model calls.

Only the package.json/package-lock.json skip policy differs from upstream.
The official renderer, semantic-unit extraction, prompt, SDL and checker remain
unchanged. Inputs must exactly match the frozen experiment input manifest.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath
import threading
from typing import Any, Callable

BASE = Path(__file__).resolve().parents[1]
VARIANT = "semia-379bc25f-complete-source-v1"
ALLOWLIST = frozenset({"package.json", "package-lock.json"})
_POLICY_LOCK = threading.RLock()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _modules():
    prepare = importlib.import_module("semia_core.prepare")
    pipeline = importlib.import_module("semia_core.pipeline")
    loop = importlib.import_module("semia_cli.synthesis_loop")
    pins = json.loads((BASE / "source-manifest.json").read_text("utf-8"))
    if pins["commit"] != "379bc25fe99833eb185efe56a38fe15f0235799c":
        raise ValueError("Unsupported Semia commit")
    files = {item["path"]: item["sha256"] for item in pins["files"]}
    for module, relative in (
        (prepare, "packages/semia-core/src/semia_core/prepare.py"),
        (pipeline, "packages/semia-core/src/semia_core/pipeline.py"),
        (loop, "packages/semia-cli/src/semia_cli/synthesis_loop.py"),
    ):
        if _sha(Path(module.__file__).read_bytes()) != files[relative]:
            raise ValueError(f"Pinned upstream module mismatch: {relative}")
    return prepare, pipeline, loop


def _case(case_id: str) -> dict[str, Any]:
    manifest = json.loads((BASE / "input-manifest.json").read_text("utf-8"))
    matches = [case for case in manifest["cases"] if case["case_id"] == case_id]
    if len(matches) != 1:
        raise ValueError(f"Case is not uniquely bound: {case_id}")
    return matches[0]


def verify_input(input_root: str | Path, case_id: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Reject drift, additional files, path escapes, symlinks and undecodable data."""
    root = Path(input_root).resolve()
    case = _case(case_id)
    expected = {item["path"] for item in case["files"]}
    if len(expected) != len(case["files"]):
        raise ValueError("Duplicate manifest file path")
    actual = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlink input is not supported: {path}")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    if actual != expected:
        raise ValueError(f"Input file inventory mismatch: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    texts = {}
    for item in case["files"]:
        relative = PurePosixPath(item["path"])
        if relative.is_absolute() or ".." in relative.parts or ":" in str(relative):
            raise ValueError("Unsafe manifest path")
        path = root / str(relative)
        if not path.resolve().is_relative_to(root):
            raise ValueError("Input path escapes package")
        data = path.read_bytes()
        if _sha(data) != item["sha256"] or len(data) != item["size"]:
            raise ValueError(f"Input integrity mismatch: {relative}")
        text = data.decode("utf-8", errors="strict")
        # Upstream .rstrip() is retained; admit only our pinned corpus where it
        # removes terminal line breaks, not meaningful spaces or other content.
        if text.rstrip("\r\n") != text.rstrip():
            raise ValueError(f"Upstream normalization would remove trailing content: {relative}")
        texts[str(relative)] = text
    return case, texts


@contextmanager
def complete_source_policy(case_id: str, input_root: str | Path):
    """Temporarily enable only known metadata files during official prepare.

    Use in one isolated experiment process. The lock serializes this helper's
    prepare calls; it does not make unrelated upstream calls thread-safe.
    """
    prepare, _, _ = _modules()
    case, _ = verify_input(input_root, case_id)
    requested = {PurePosixPath(item["path"]).name for item in case["files"]}
    with _POLICY_LOCK:
        original = prepare._SKIP_FILES_ALWAYS
        remove = original.intersection(requested)
        if not remove <= ALLOWLIST:
            raise ValueError(f"Unsupported default-excluded input files: {sorted(remove-ALLOWLIST)}")
        prepare._SKIP_FILES_ALWAYS = original.difference(remove)
        try:
            yield sorted(remove)
        finally:
            prepare._SKIP_FILES_ALWAYS = original


def verify_prepared(input_root: str | Path, run_dir: str | Path, case_id: str) -> dict[str, Any]:
    """Prove each input line survives and the actual upstream prompt contains it."""
    _, _, loop = _modules()
    case, texts = verify_input(input_root, case_id)
    target = Path(run_dir).resolve()
    metadata = json.loads((target / "prepare_metadata.json").read_text("utf-8"))
    units = json.loads((target / "prepare_units.json").read_text("utf-8"))
    source = metadata["source"]
    inventory = source["file_inventory"]
    if len(inventory) != len(texts) or {x["path"] for x in inventory} != set(texts):
        raise ValueError("Prepared inventory omits or adds files")
    if any(x["disposition"] not in {"inlined", "inlined_source"} for x in inventory):
        raise ValueError("Prepared inventory contains excluded input files")
    prepared_bytes = (target / "prepared_skill.md").read_bytes()
    prepared = prepared_bytes.decode("utf-8")
    if _sha(prepared_bytes) != metadata["prepared_skill_sha256"]:
        raise ValueError("Prepared artifact digest mismatch")
    lines = prepared.splitlines()
    recovered: dict[str, dict[int, str]] = {name: {} for name in texts}
    for entry in source["source_map"]:
        if entry["source_line_start"] == 0:
            continue
        name = entry["source_file"]
        if name not in texts:
            raise ValueError(f"Unbound mapped source: {name}")
        count = entry["enriched_line_end"] - entry["enriched_line_start"] + 1
        if count != entry["source_line_end"] - entry["source_line_start"] + 1:
            raise ValueError("Nonlinear source line mapping")
        for offset in range(count):
            number = entry["source_line_start"] + offset
            if number in recovered[name]:
                raise ValueError("Duplicated source line mapping")
            recovered[name][number] = lines[entry["enriched_line_start"] - 1 + offset]
    file_receipts = []
    for item in case["files"]:
        name = item["path"]
        expected_lines = texts[name].rstrip().splitlines()
        expected = {i: line for i, line in enumerate(expected_lines, 1)}
        if recovered[name] != expected:
            raise ValueError(f"Source line loss or rewriting: {name}")
        file_receipts.append({
            **item, "body_lines": len(expected_lines), "mapped_lines": len(recovered[name]),
            "body_sha256": _sha("\n".join(expected_lines).encode("utf-8")),
            "line_content_and_identity_verified": True,
        })
    if units["file_inventory"] != inventory or units["source_map"] != source["source_map"]:
        raise ValueError("Semantic-unit source metadata differs from prepare metadata")
    nonce = metadata.get("hostile_input_nonce")
    if not isinstance(nonce, str) or not nonce:
        raise ValueError("Missing hostile-input fence nonce")
    begin, end = f"<<<SEMIA_HOSTILE_INPUT id={nonce}>>>", f"<<<SEMIA_END id={nonce}>>>"
    if begin in prepared or end in prepared:
        raise ValueError("Source collides with hostile-input fence")
    prompt = loop._prompt(target)
    expected_block = f"{begin}\n{prepared.rstrip()}\n{end}"
    if prompt.count(expected_block) != 1:
        raise ValueError("Complete prepared source absent from final synthesis prompt")
    loop._enforce_doc_size(target, 2 * 1024 * 1024)
    return {
        "variant": VARIANT, "case_id": case_id, "files": file_receipts,
        "all_files_present": True, "file_count": len(texts),
        "prepared_bytes": len(prepared_bytes), "prepared_sha256": _sha(prepared_bytes),
        "synthesis_prompt_bytes": len(prompt.encode("utf-8")),
        "synthesis_prompt_sha256": _sha(prompt.encode("utf-8")),
        "complete_body_in_final_prompt": True, "semantic_unit_count": units["total_units"],
        "normalization": "Official LF rendering and terminal-line-break trimming retained; every source body line checked against its original file and line number.",
        "model_calls": 0, "skill_executions": 0,
    }


def prepare_complete_source(input_root: str | Path, run_dir: str | Path, case_id: str) -> dict[str, Any]:
    """Prepare using official APIs, fail before synthesis if coverage is incomplete."""
    _, pipeline, _ = _modules()
    target = Path(run_dir).resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"Refusing to overwrite existing prepared artifacts: {target}")
    with complete_source_policy(case_id, input_root) as added_names:
        result = pipeline.prepare(input_root, out_dir=target)
    receipt = verify_prepared(input_root, target, case_id)
    receipt["default_skip_names_removed"] = added_names
    (target / "complete-source-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def make_complete_source_preparer(case_id: str) -> Callable[..., dict[str, Any]]:
    """Bind to semia_cli.core_adapter.prepare in a new controlled runner only."""
    def prepare(skill_path, out_dir=None, run_dir=None):
        target = out_dir or run_dir
        if target is None:
            raise ValueError("Complete-source comparison requires an explicit output directory")
        return prepare_complete_source(skill_path, target, case_id)
    return prepare
