"""Prepare and audit one Semia input package offline."""

import argparse
from contextlib import ExitStack
import hashlib
from importlib import import_module
import importlib.util
import json
import os
from pathlib import Path
import sys
import sysconfig
from unittest.mock import patch


HISTORICAL = Path(__file__).resolve().parents[3] / "semia-20261118"
REPOSITORY = HISTORICAL.parents[2]
COMMIT = "379bc25fe99833eb185efe56a38fe15f0235799c"
VARIANTS = {
    "native": "semia-379bc25f-native",
    "complete-source": "semia-379bc25f-complete-utf8-source-v1",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    with path.open("rb") as content:
        return hashlib.file_digest(content, "sha256").hexdigest()


def write_json(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def verify_runtime():
    sys.dont_write_bytecode = True
    setup_path = HISTORICAL / "setup-report.json"
    setup = read_json(setup_path)
    if setup["upstream"]["commit"] != COMMIT:
        raise ValueError("Unexpected Semia runtime commit")
    library = Path(sysconfig.get_path("purelib")).resolve()
    if not library.is_relative_to(HISTORICAL / ".venv"):
        raise ValueError("Run with the pinned Semia virtual environment")
    for item in setup["environment"]["installed_code_files"]:
        if sha256(library / item["path"]) != item["sha256"]:
            raise ValueError(f"Semia runtime digest mismatch: {item['path']}")
    for name in ("semia_cli", "semia_core"):
        spec = importlib.util.find_spec(name)
        if spec is None or Path(spec.origin).resolve() != library / name / "__init__.py":
            raise ValueError(f"Semia module resolves outside the pinned installation: {name}")
    return sha256(setup_path)


def inventory(root):
    entries = {}
    for path in sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix()):
        if path.is_symlink() or path.is_junction():
            raise ValueError(f"Linked source is unsupported: {path}")
        if path.is_dir():
            continue
        relative = path.relative_to(root).as_posix()
        if not path.is_file():
            raise ValueError(f"Source is not a regular file: {relative}")
        entries[relative] = {"path": relative, "size": path.stat().st_size, "sha256": sha256(path)}
    if not entries:
        raise ValueError("Source directory contains no files")
    return entries


def select_source(args):
    if args.manifest is None:
        return args.input_dir, None, None
    if args.case_id is None:
        raise ValueError("--manifest requires --case-id")
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    cases = [case for case in manifest["cases"] if case["case_id"] == args.case_id]
    if len(cases) != 1:
        raise ValueError(f"Expected one manifest entry for {args.case_id}")
    case = cases[0]
    root = REPOSITORY / case["source_directory"]
    if not root.resolve().is_relative_to(REPOSITORY):
        raise ValueError("Manifest source directory escapes the repository")
    return root, case, hashlib.sha256(manifest_bytes).hexdigest()


def verify_rendered(root, target, files, synthesis_loop):
    metadata = read_json(target / "prepare_metadata.json")
    units = read_json(target / "prepare_units.json")
    source = metadata["source"]
    if units["file_inventory"] != source["file_inventory"] or units["source_map"] != source["source_map"]:
        raise ValueError("Semia prepare artifacts disagree on source mapping")

    prepared_path = target / "prepared_skill.md"
    if sha256(prepared_path) != metadata["prepared_skill_sha256"]:
        raise ValueError("Semia prepared source digest mismatch")
    prepared = prepared_path.read_bytes().decode("utf-8")
    compiled_lines = prepared.splitlines()
    mapping = {name: {} for name in files}
    upstream = {item["path"]: item["disposition"] for item in source["file_inventory"]}
    if upstream.keys() - files.keys():
        raise ValueError("Semia inventory contains unbound files")
    for record in source["source_map"]:
        if record["source_line_start"] == 0:
            continue
        name = record["source_file"]
        start = record["source_line_start"]
        end = record["source_line_end"]
        lines = compiled_lines[record["enriched_line_start"] - 1:record["enriched_line_end"]]
        if name not in mapping or len(lines) != end - start + 1:
            raise ValueError("Semia source mapping contains an unbound or invalid range")
        target_lines = mapping[name]
        if any(number in target_lines for number in range(start, end + 1)):
            raise ValueError(f"Semia source mapping repeats lines in {name}")
        target_lines.update(enumerate(lines, start))

    coverage = []
    for name, identity in files.items():
        disposition = upstream.get(name, "omitted_by_upstream")
        evidence = {**identity, "disposition": disposition, "source_body_verified": False}
        if disposition in {"inlined", "inlined_source"}:
            data = (root / name).read_bytes()
            text = data.decode("utf-8", errors="replace")
            if text.encode("utf-8") == data:
                expected = dict(enumerate(text.rstrip().splitlines(), 1))
                evidence["source_body_verified"] = mapping[name] == expected
                evidence["mapped_lines"] = len(mapping[name])
                evidence["trimmed_trailing_non_newline_whitespace"] = text.rstrip("\r\n") != text.rstrip()
        coverage.append(evidence)

    nonce = metadata["hostile_input_nonce"]
    begin = f"<<<SEMIA_HOSTILE_INPUT id={nonce}>>>"
    end = f"<<<SEMIA_END id={nonce}>>>"
    prompt = synthesis_loop._prompt(target)
    if begin in prepared or end in prepared or prompt.count(f"{begin}\n{prepared.rstrip()}\n{end}") != 1:
        raise ValueError("Initial synthesis prompt does not bind the prepared source")
    prompt_path = target / "initial-synthesis-prompt.txt"
    prompt_bytes = prompt.encode("utf-8")
    prompt_path.write_bytes(prompt_bytes)
    return {
        "files": coverage,
        "source_body_complete_after_upstream_normalization": all(item["source_body_verified"] for item in coverage),
        "native_source_sha256": source["source_hash"],
        "native_prepared_source_sha256": metadata["prepared_skill_sha256"],
        "initial_prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "initial_prompt_bytes": len(prompt_bytes),
        "initial_prompt_chars": len(prompt),
        "semantic_units": units["total_units"],
    }


def prepare(args):
    root_path, case, manifest_sha = select_source(args)
    if root_path.is_symlink() or root_path.is_junction() or not root_path.is_dir():
        raise ValueError("Input must be a real source directory")
    root = root_path.resolve()
    output = args.out.resolve()
    if output.is_relative_to(root) or output.is_relative_to(HISTORICAL):
        raise ValueError("New output must be outside the input directory and historical Semia workspace")
    if output.exists():
        raise ValueError(f"Refusing to overwrite existing output: {output}")
    files = inventory(root)
    identities = [
        {"path": item["path"], "size": item["size"], "raw_sha256": item["sha256"]}
        for item in files.values()
    ]
    encoded_identity = json.dumps(identities, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    package_sha = hashlib.sha256(encoded_identity.encode("utf-8")).hexdigest()
    total_bytes = sum(item["size"] for item in files.values())
    if case is not None:
        if (
            sorted(case["files"], key=lambda item: item["path"]) != list(files.values())
            or case["file_count"] != len(files)
            or case["total_bytes"] != total_bytes
            or case["package_bytes_sha256"] != package_sha
        ):
            raise ValueError("Source files do not match the cohort manifest")
    setup_digest = verify_runtime()

    from semia_cli import llm_config, synthesis_loop
    from semia_core import pipeline
    upstream_prepare = import_module("semia_core.prepare")

    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "schema": "semia-comparison-offline-preparation-v1",
        "case_id": args.case_id or root.name,
        "source_directory": str(root),
        "manifest_sha256": manifest_sha,
        "package_bytes_sha256": package_sha,
        "source_file_count": len(files),
        "source_total_bytes": total_bytes,
        "files": list(files.values()),
        "variant": VARIANTS[args.variant],
        "upstream_commit": COMMIT,
        "upstream_setup_sha256": setup_digest,
        "upstream_limits_bytes": {
            "single_file": upstream_prepare._MAX_FILE_SIZE_BYTES,
            "inlined_source": upstream_prepare._DEFAULT_MAX_INLINED_BYTES,
            "synthesis_document": llm_config.DEFAULT_MAX_DOC_BYTES,
        },
        "model_calls": 0,
        "skill_executions": 0,
        "transport_status": "not_run",
        "detection_status": "not_run",
        "status": "prepare_failed",
    }
    try:
        with ExitStack() as options:
            # Keep upstream's default bundle size even if the host exports an override.
            options.enter_context(patch.object(os, "environ", {
                key: value for key, value in os.environ.items() if key != "SEMIA_PREPARE_MAX_TOTAL_BYTES"
            }))
            if args.variant == "complete-source":
                # Change only file admission. The upstream renderer and unit builder remain intact.
                for name in files:
                    (root / name).read_bytes().decode("utf-8")
                options.enter_context(patch.object(upstream_prepare, "_iter_visible_files", lambda _: list(files)))
                options.enter_context(patch.object(upstream_prepare, "_is_supported_text_file", lambda _: True))
            pipeline.prepare(root, out_dir=output)
        receipt.update(verify_rendered(root, output, files, synthesis_loop))
        if inventory(root) != files:
            raise ValueError("Input changed while preparing")
        if args.variant == "complete-source" and not receipt["source_body_complete_after_upstream_normalization"]:
            receipt["status"] = "incomplete_source"
        else:
            receipt["status"] = "synthesis_document_rejected"
            synthesis_loop._enforce_doc_size(output, llm_config.DEFAULT_MAX_DOC_BYTES)
            receipt["status"] = "prepared_offline"
    except (OSError, RuntimeError, ValueError, SyntaxError) as error:
        receipt["error"] = f"{type(error).__name__}: {error}"
    write_json(output / "preparation-receipt.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input-dir", type=Path)
    source.add_argument("--manifest", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--out", type=Path, required=True, help="New output directory")
    parser.add_argument("--variant", choices=VARIANTS, default="native")
    args = parser.parse_args()
    try:
        receipt = prepare(args)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"{receipt['case_id']}: {receipt['status']} ({args.out / 'preparation-receipt.json'})")
    return 0 if receipt["status"] == "prepared_offline" else 2


if __name__ == "__main__":
    raise SystemExit(main())
