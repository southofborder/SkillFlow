"""Prepare an explicitly authorized fresh rerun of the 15 failed cases.

No model client, environment file, Skill script, or existing run is modified.
The sealed full-pipeline driver remains unchanged: copied successful cases use
their durable responses, while failed cases start from source in an empty case.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys

from skillflow.common.paths import project_root, resolve_material_path

HERE = Path(__file__).resolve()
PACKAGE_ROOT = project_root()
REPOSITORY_ROOT = project_root()

from skillflow.common.artifact_io import atomic_write_text
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from skillflow.common.recording import implementation_provenance
from skillflow.common.recording import sha_file
from skillflow.common.recording import validated_trace
from skillflow.graph.semantic_contract import contract_binding
from skillflow.propagation.contracts.profiles import SCHEMA_VERSION

PARENT_IDENTITY = "skill-ir-full-feedback-security-profile-review30-v10"
IDENTITY = "skill-ir-explicit-failed-case-rerun-v4"
AUTHORIZATION = "失败的全部重跑一下"
EXPECTED_RERUN_CASES = tuple(["008", "009"] + [f"{number:03}" for number in range(18, 31)])
FEEDBACK_ERRORS = {"extraction_error", "fidelity_error", "audit_error", "execution_error", "input_error", "semantic_failure"}
ANNOTATION_ERRORS = {"input_error", "invalid_response", "execution_error", "semantic_failure"}


def read_json(path):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError("Duplicate JSON key in saved record")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("Non-finite JSON number in saved record")
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def write_json(path, value):
    atomic_write_text(Path(path), json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def no_link(path):
    info = Path(path).lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ValueError("Rerun preparation must not follow links or reparse points")


def safe_child(root, relative):
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or ".." in path.parts or "\\" in relative
            or ":" in relative or "\0" in relative or str(path) != relative):
        raise ValueError("Unsafe relative recorded path")
    result = Path(root).joinpath(*path.parts)
    if not result.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("Recorded path escapes its root")
    return result


def inventory(directory):
    """Exclude only replay-derived trees and the exact runtime lock filename."""
    directory = Path(directory)
    no_link(directory)
    result = {}
    for current, directories, files in os.walk(directory, followlinks=False):
        directories[:] = sorted(name for name in directories if name != "replay")
        for name in directories:
            no_link(Path(current) / name)
        for name in sorted(files):
            if name == ".runner.lock":
                continue
            path = Path(current) / name
            no_link(path)
            if not path.is_file():
                raise ValueError("Unsupported non-regular run artifact")
            result[path.relative_to(directory).as_posix()] = sha_file(path)
    return dict(sorted(result.items()))


def classify_cases(manifest, outcome):
    expected = [f"{number:03}" for number in range(1, 31)]
    if ([case.get("case_id") for case in manifest["cases"]] != expected
            or set(outcome["cases"]) != set(expected)):
        raise ValueError("Exactly the fixed thirty terminal cases are required")
    rerun, reuse = [], []
    for case in manifest["cases"]:
        identifier = case["case_id"]
        if case["run_dir"] != "cases/" + identifier:
            raise ValueError("Case directory identity mismatch")
        row = outcome["cases"][identifier]
        feedback, annotation = row["feedback"]["status"], row["annotation"]["status"]
        if feedback not in FEEDBACK_ERRORS | {"audit_passed", "semantic_failure", "revision_limit"}:
            raise ValueError("Parent feedback is not a supported terminal result")
        if annotation not in ANNOTATION_ERRORS | {"complete", "not_run"}:
            raise ValueError("Parent annotation is not a supported terminal result")
        failed = feedback in FEEDBACK_ERRORS or annotation in ANNOTATION_ERRORS
        if not failed and (annotation == "not_run" or row.get("scheduler_error")):
            raise ValueError("Unfinished or ambiguous case cannot be treated as reusable")
        (rerun if failed else reuse).append(identifier)
    if tuple(rerun) != EXPECTED_RERUN_CASES:
        raise ValueError("Derived failed cases differ from the explicitly authorized fifteen cases")
    return rerun, reuse


def validate_parent(parent):
    parent = Path(parent)
    manifest, outcome = read_json(parent / "manifest.json"), read_json(parent / "experiment-result.json")
    for value in (manifest, outcome):
        if (value.get("schema_version") != 10 or value.get("identity") != PARENT_IDENTITY
                or value.get("profile_schema_version") != SCHEMA_VERSION):
            raise ValueError("Unsupported parent run identity")
        if any(value.get(key) != expected for key, expected in contract_binding().items()):
            raise ValueError("Parent semantic contract mismatch")
    if manifest["implementation"] != implementation_provenance():
        raise ValueError("Sealed implementation changed since the parent run")
    driver = safe_child(REPOSITORY_ROOT, manifest["driver"]["path"])
    if sha_file(driver) != manifest["driver"]["sha256"]:
        raise ValueError("Sealed full-pipeline driver changed")
    selectors = manifest["source_selector"]
    if (sha_file(HERE.with_name("run_review_set.py")) != selectors["review_driver_sha256"]
            or sha_file(REPOSITORY_ROOT / "tools/graph/baseline/review_set_source.py") != selectors["selector_sha256"]):
        raise ValueError("Frozen source selection implementation changed")
    if sha_file(Path(manifest["renderer"]["path"])) != manifest["renderer"]["sha256"]:
        raise ValueError("Frozen Lean renderer changed")
    rerun, reuse = classify_cases(manifest, outcome)
    for case in manifest["cases"]:
        directory = safe_child(parent, case["run_dir"])
        row = read_json(directory / "result.json")
        if row != outcome["cases"][case["case_id"]]:
            raise ValueError("Parent case differs from aggregate terminal result")
        if read_json(directory / "feedback/result.json") != row["feedback"]:
            raise ValueError("Parent feedback differs from case result")
        annotation = directory / "annotation/result.json"
        if annotation.exists() and read_json(annotation) != row["annotation"]:
            raise ValueError("Parent annotation differs from case result")
        if case["source_inventory_sha256"] != canonical_sha256(case["source_inventory"]):
            raise ValueError("Parent corpus inventory digest mismatch")
        _, source, snapshot = read_snapshot(directory / "feedback")
        files = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]} for entry in snapshot["files"]}
        if files != case["source_inventory"] or source["source_sha256"] != row["feedback"]["source_sha256"]:
            raise ValueError("Parent frozen snapshot differs from corpus source")
        package = safe_child(REPOSITORY_ROOT, case["package_path"])
        no_link(package)
        actual = inventory(package)
        if actual != {name: data["sha256"] for name, data in case["source_inventory"].items()}:
            raise ValueError("Original frozen Skill package changed")
    return manifest, outcome, rerun, reuse


def call_ledger(parent, files):
    ledger = []
    for relative in files:
        parts = PurePosixPath(relative).parts
        if len(parts) < 6 or parts[0] != "cases" or "calls" not in parts or parts[-1] != "call.json":
            continue
        path = safe_child(parent, relative)
        call = read_json(path)
        if call.get("status") not in {"complete", "error", "invalid_record"}:
            raise ValueError("A parent request is not terminal; explicit failed-case rerun cannot infer its status")
        if call.get("prompt_sha256") != canonical_sha256(call.get("prompt")):
            raise ValueError("Parent call prompt digest mismatch")
        trace_path = path.with_name("transport.json")
        trace = validated_trace(trace_path)
        if len(trace) != 1 or trace[0].get("prompt") != call["prompt"]:
            raise ValueError("Parent call and transport identity differ")
        if call["status"] == "complete":
            if (trace[0].get("status") != "complete" or call.get("response_rejected") or trace[0].get("response_rejected")
                    or "response" not in call or "response" not in trace[0]
                    or call.get("response_sha256") != canonical_sha256(call["response"])
                    or canonical_sha256(trace[0]["response"]) != call["response_sha256"]):
                raise ValueError("Complete parent response failed durable binding")
        attempts = trace[0].get("http_attempts")
        if not isinstance(attempts, list):
            raise ValueError("Parent transport lacks an explicit HTTP attempt inventory")
        observed = trace[0].get("http_attempts_observed") is not False and bool(attempts)
        ledger.append({"origin_id": parent.name + ":" + relative, "origin_run": str(parent),
            "relative_path": relative, "case_id": parts[1], "stage": parts[2],
            "status": call["status"], "call_sha256": files[relative],
            "transport_sha256": files[trace_path.relative_to(parent).as_posix()],
            "http_attempts": len(attempts) if observed else None,
            "http_retries": max(0, len(attempts) - 1) if observed else None,
            "http_attempts_observed": observed,
            "response_sha256": call.get("response_sha256"), "prompt_sha256": call["prompt_sha256"]})
    return ledger


def prepare(parent, destination):
    parent, destination = Path(parent).absolute(), Path(destination).absolute()
    no_link(parent)
    parent = parent.resolve()
    if destination.exists():
        raise ValueError("Rerun destination already exists; never overwrite or reuse it")
    for ancestor in destination.parents:
        if ancestor.exists():
            no_link(ancestor)
    destination = destination.resolve()
    if destination.name == parent.name:
        raise ValueError("Rerun must have a distinct run ID for unique call accounting")
    protected = [parent, REPOSITORY_ROOT / "dataset", REPOSITORY_ROOT / "result", PACKAGE_ROOT / "src"]
    protected += [resolve_material_path(address) for address in
                  ("experiments/graph/baseline", "experiments/corpus/semantics_review", "experiments/graph/feedback")]
    if any(destination == root or destination.is_relative_to(root) or root.is_relative_to(destination) for root in protected):
        raise ValueError("Rerun destination overlaps parent, frozen input or production artifacts")
    manifest, outcome, rerun, reuse = validate_parent(parent)
    package_roots = [safe_child(REPOSITORY_ROOT, case["package_path"]).resolve() for case in manifest["cases"]]
    if any(destination == root or destination.is_relative_to(root) or root.is_relative_to(destination) for root in package_roots):
        raise ValueError("Rerun destination overlaps a frozen Skill package")
    before = inventory(parent)
    ledger = call_ledger(parent, before)
    copies = {relative: digest for relative, digest in before.items()
              if relative == "manifest.json" or any(relative.startswith(f"cases/{identifier}/") for identifier in reuse)}
    if not all(any(relative.startswith(f"cases/{identifier}/") for relative in copies) for identifier in reuse):
        raise ValueError("A reusable case has no complete copied material")
    destination.mkdir(parents=True, exist_ok=False)
    try:
        # Manifest is copied last: the unchanged driver rejects an unprepared,
        # nonempty run instead of accidentally starting while files are copied.
        for relative, digest in copies.items():
            if relative == "manifest.json":
                continue
            target = safe_child(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe_child(parent, relative), target)
            if sha_file(target) != digest:
                raise ValueError("Copied successful artifact changed bytes")
        if inventory(parent) != before:
            raise ValueError("Parent run changed while preparing the rerun")
        provenance = {
            "schema_version": 4, "identity": IDENTITY,
            "authorization": {"user_request": AUTHORIZATION,
                "scope": "所有失败案例在新目录从源包完整重跑；此前已接受、格式错误或不确定的失败案例也在本次明确授权之内。",
                "quality_selection": False, "successful_cases_rerun": False},
            "parent_run": {"path": str(parent), "run_id": parent.name, "files": before,
                "files_sha256": canonical_sha256(before), "manifest_sha256": before["manifest.json"],
                "experiment_result_sha256": before["experiment-result.json"], "excluded_paths": ["**/replay/**", "**/.runner.lock"]},
            "child_run": {"path": str(destination), "run_id": destination.name},
            "rerun_cases": rerun, "reused_cases": reuse,
            "failure_definition": {"feedback": sorted(FEEDBACK_ERRORS), "annotation": sorted(ANNOTATION_ERRORS),
                                   "partial_order_alone_is_failure": False},
            "copied_files": copies, "copied_files_sha256": canonical_sha256(copies),
            "failed_case_policy": "不复制任何失败 case 目录、阶段、旧响应或派生产物；原驱动从同一冻结源包重新开始。",
            "parent_summary": deepcopy(outcome["summary"]), "parent_call_ledger": ledger,
            "reused_call_origins": {entry["relative_path"]: entry["origin_id"] for entry in ledger if entry["case_id"] in reuse},
            "cost_accounting": {
                "identity": "origin_run_id + relative call path；完整复制的成功调用沿用父origin_id，新失败案例调用使用子run的origin_id。",
                "unique_execution_calls": "父parent_call_ledger全部条目 + 子run仅rerun_cases的新calls条目；不能将子run30例总计再次全加。",
                "logical_units": "每个来源run内：extraction按call路径、audit按case+revision、annotation按case；不同run的新请求独立计数。",
                "http_attempts_and_usage": "每个唯一origin只汇总一次transport；父失败DNS/不完整流仍计入；未知用量保留未知，不能按prompt或response相同去重。",
                "parent_execution_calls": len(ledger),
                "parent_http_attempts": sum(entry["http_attempts"] for entry in ledger) if all(entry["http_attempts"] is not None for entry in ledger) else None,
                "unobserved_parent_call_origins": [entry["origin_id"] for entry in ledger if not entry["http_attempts_observed"]],
                "new_network_calls_during_preparation": 0,
            },
            "tool_sha256": sha_file(HERE), "status": "prepared", "online_started": False,
        }
        provenance["provenance_sha256"] = canonical_sha256(provenance)
        write_json(destination / "rerun-provenance.json", provenance)
        shutil.copyfile(parent / "manifest.json", destination / "manifest.json")
        if sha_file(destination / "manifest.json") != before["manifest.json"]:
            raise ValueError("Root manifest changed while copying")
        actual = inventory(destination)
        if actual != {**copies, "rerun-provenance.json": sha_file(destination / "rerun-provenance.json")}:
            raise ValueError("Prepared destination contains unexpected or missing files")
        if any((destination / "cases" / identifier).exists() for identifier in rerun):
            raise ValueError("Failed case material must never be copied")
        return provenance
    except BaseException:
        # Preserve a partial new directory for diagnosis. Never delete parent or
        # silently rebuild over it. Without a valid preparation return, do not run.
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-run", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.parent_run, args.run_dir)
    print(json.dumps({"status": result["status"], "run_dir": result["child_run"]["path"],
                      "rerun_cases": result["rerun_cases"], "reused_cases": result["reused_cases"],
                      "parent_execution_calls": result["cost_accounting"]["parent_execution_calls"],
                      "parent_http_attempts": result["cost_accounting"]["parent_http_attempts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
