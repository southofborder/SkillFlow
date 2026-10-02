"""Hash-bound F01 cases; evaluation labels never become part of a CFG.

Paths are resolved from this package, independently of the working directory.
This module reads protected inputs and constructs fresh, in-memory variants.
It does not import an oracle or invoke a model service.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from skill_ir.ir.cfg import ControlFlowGraph


PACKAGE_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = PACKAGE_ROOT.parents[1]
MANIFEST_PATH = Path("packages/skill-ir/experiments/semantic_backtrace/f01/manifest.json")


class FixtureIntegrityError(ValueError):
    """A selected input no longer matches the reviewed, hash-bound fixture."""


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _repo_path(root: Path, relative: str | Path) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise FixtureIntegrityError(f"fixture path escapes repository: {relative}")
    return path


def _verified_bytes(root: Path, relative: str, expected: str) -> bytes:
    content = _repo_path(root, relative).read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    if actual != expected:
        raise FixtureIntegrityError(f"SHA-256 mismatch for {relative}: {actual} != {expected}")
    return content


def _one(values: list[Any], description: str) -> Any:
    if len(values) != 1:
        raise FixtureIntegrityError(f"expected one {description}, found {len(values)}")
    return values[0]


def _instructions(cfg: dict[str, Any]):
    for key, block in cfg["blocks"].items():
        for index, instruction in enumerate(block["instructions"]):
            yield key, index, instruction


def _has_resource(instruction: dict[str, Any], resource: str) -> bool:
    return any(
        operand["type"] == "external_resource" and operand["identifier"] == resource
        for operand in instruction["inputs"]
    )


def _result_output(instruction: dict[str, Any], suffix: str) -> dict[str, Any]:
    return _one(
        [
            operand for operand in instruction["outputs"]
            if operand["type"] == "result" and operand.get("semantic_name", "").endswith(suffix)
        ],
        f"{suffix} result of {instruction['id']}",
    )


def _return_reading(cfg: dict[str, Any], result_id: str):
    return _one(
        [
            item for item in _instructions(cfg)
            if item[2]["opcode"] == "return" and any(
                operand["type"] == "result" and operand["identifier"] == result_id
                for operand in item[2]["inputs"]
            )
        ],
        f"return reading {result_id}",
    )


def _anchors(cfg: dict[str, Any]) -> dict[str, Any]:
    items = list(_instructions(cfg))
    archive = _one([x for x in items if _has_resource(x[2], "archive.fetch")], "archive operation")
    fast = [x for x in items if _has_resource(x[2], "fast.fetch")]
    retry = _one([x for x in fast if "retry" in x[2]["opcode"]], "fast retry operation")
    first = _one([x for x in fast if x != retry], "first fast operation")
    key_read = _one(
        [x for x in items if any(
            o["type"] == "context_key" and o["identifier"] == "FAST_KEY" for o in x[2]["inputs"]
        )],
        "FAST_KEY acquisition",
    )
    key_result = _one([o for o in key_read[2]["outputs"] if o["type"] == "result"], "FAST_KEY result")
    first_error = _result_output(first[2], "error")
    failure_check = _one(
        [x for x in items if "transient" in x[2]["opcode"] and any(
            o["type"] == "result" and o["identifier"] == first_error["identifier"]
            for o in x[2]["inputs"]
        )],
        "failure-type check consuming first fast error",
    )
    return {
        "archive": archive,
        "first": first,
        "retry": retry,
        "key_result": key_result,
        "failure_check": failure_check,
        "archive_failure_return": _return_reading(cfg, _result_output(archive[2], "error")["identifier"]),
        "retry_success_return": _return_reading(cfg, _result_output(retry[2], "response_body")["identifier"]),
    }


def _mutate(cfg: dict[str, Any], case_id: str) -> None:
    if case_id == "c01":
        return
    anchors = _anchors(cfg)
    if case_id == "c02":
        anchors["archive"][2]["inputs"].append(deepcopy(anchors["key_result"]))
    elif case_id == "c03":
        key, return_index, _ = anchors["archive_failure_return"]
        block = cfg["blocks"][key]
        append_index = _one(
            [i for i, inst in enumerate(block["instructions"][:return_index])
             if _has_resource(inst, "status.txt") and "append" in inst["opcode"]],
            "failure status append before return",
        )
        del block["instructions"][append_index]
        # Intentionally retain the old block title and global constraint.
    elif case_id == "c04":
        key, _, instruction = anchors["retry_success_return"]
        original = _result_output(anchors["retry"][2], "response_body")["identifier"]
        first_body = _result_output(anchors["first"][2], "response_body")
        instruction["inputs"] = [
            deepcopy(first_body) if o["type"] == "result" and o["identifier"] == original else o
            for o in instruction["inputs"]
        ]
        cfg["blocks"][key]["block_name"] = (
            "Append success status and return the first fast.fetch response body after retry success"
        )
    elif case_id == "c05":
        key, check_index, _ = anchors["failure_check"]
        used = {instruction["id"] for _, _, instruction in _instructions(cfg)}
        suffix = 1
        while f"ir_wait_{suffix}" in used:
            suffix += 1
        block = cfg["blocks"][key]
        if check_index >= len(block["instructions"]) - 1:
            raise FixtureIntegrityError("failure-type check has no following terminator")
        block["instructions"].insert(check_index + 1, {
            "id": f"ir_wait_{suffix}",
            "opcode": "wait_for_seconds",
            "inputs": [{"type": "literal", "identifier": None, "literal_value": 2}],
            "outputs": [],
            "constraints": ["Wait for 2 seconds before continuing."],
            "metadata": {},
            "draft_instruction_id": None,
        })
    else:
        raise FixtureIntegrityError(f"unknown fixed fixture: {case_id}")


def prepare_cases(
    *, repository_root: Path | None = None, manifest_path: Path | None = None
) -> dict[str, Any]:
    """Load verified source and five independent, structurally valid CFGs.

    The optional paths support isolated fixture tests. The default always uses
    the package's own repository location, never the current working directory.
    ``oracle_key`` is routing metadata for the evaluator, not a model input.
    """
    root = (repository_root or REPOSITORY_ROOT).resolve()
    relative_manifest = manifest_path or MANIFEST_PATH
    manifest_bytes = _repo_path(root, relative_manifest).read_bytes()
    manifest = json.loads(manifest_bytes)
    selection = manifest["selection"]
    if (
        manifest.get("schema_version") != 1
        or manifest.get("path_base") != "repository"
        or (selection.get("sample_id"), selection.get("index"), selection.get("repetition")) != ("F01", 13, 1)
        or manifest.get("case_ids") != ["c01", "c02", "c03", "c04", "c05"]
    ):
        raise FixtureIntegrityError("unsupported manifest or F01 selection")
    review = json.loads(_verified_bytes(root, selection["manifest_path"], selection["manifest_sha256"]))
    sample = _one(
        [item for item in review["samples"] if item["sample_id"] == "F01"], "reviewed F01 selection"
    )
    if sample["index"] != 13 or sample["repetition"] != 1:
        raise FixtureIntegrityError("F01 must be reviewed item 013, repetition 1")
    analysis_info = manifest["analysis"]
    if (sample["analysis_path"], sample["analysis_sha256"]) != (
        analysis_info["path"], analysis_info["sha256"]
    ):
        raise FixtureIntegrityError("F01 analysis differs from the reviewed selection")
    analysis = json.loads(_verified_bytes(root, analysis_info["path"], analysis_info["sha256"]))
    original = analysis["cfg"]
    if canonical_sha256(original) != analysis_info["graph_sha256"]:
        raise FixtureIntegrityError("F01 graph canonical SHA-256 mismatch")
    source_info = manifest["source"]
    source_root = _repo_path(root, source_info["root"])
    inventory = sorted(path.relative_to(source_root).as_posix() for path in source_root.rglob("*") if path.is_file())
    expected_inventory = sorted(item["path"] for item in source_info["files"])
    if inventory != expected_inventory:
        raise FixtureIntegrityError("F01 source inventory differs from the manifest")
    files = []
    for item in sorted(source_info["files"], key=lambda row: row["path"]):
        raw = _verified_bytes(root, f"{source_info['root']}/{item['path']}", item["sha256"])
        files.append({"path": item["path"], "content": raw.decode("utf-8"), "sha256": item["sha256"]})
    source_sha = canonical_sha256([{key: item[key] for key in ("path", "sha256")} for item in files])
    if source_sha != source_info["source_sha256"]:
        raise FixtureIntegrityError("F01 source bundle canonical SHA-256 mismatch")
    cases = []
    for case_id in ("c01", "c02", "c03", "c04", "c05"):
        cfg = deepcopy(original)
        _mutate(cfg, case_id)
        # Validation is applied to a fresh object; the JSON used for model input
        # keeps exactly the original fields and the explicitly specified mutation.
        ControlFlowGraph.model_validate(deepcopy(cfg)).validate_integrity()
        cases.append({
            "case_id": case_id, "cfg": cfg, "graph_sha256": canonical_sha256(cfg),
            "oracle_key": case_id,
        })
    return {
        "source": {"files": files, "source_sha256": source_sha},
        "cases": cases,
        "provenance": {
            "fixture_manifest_path": Path(relative_manifest).as_posix(),
            "fixture_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "selection": deepcopy(selection),
            "analysis": deepcopy(analysis_info),
            "source_root": source_info["root"],
            "oracle_loaded": False,
            "model_calls_performed": 0,
        },
    }
