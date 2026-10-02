"""Independent post-run acceptance: saved-response replay with networking disabled.

Call only after the online batch has stopped. Original call records and prior
deliveries are read-only. This script writes only engineering-checks.json and
the driver's explicitly separate replay directories in the supplied new run.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/skill-ir/src"))

from skill_ir.extraction.prompt import build_whole_skill_prompt
from skill_ir.backtrace.prompts import source_controlled_prompt
from skill_ir.inputs.snapshot import read_snapshot, verify_original_input
from skill_ir.llm.config import load_environment
from skill_ir.recording import canonical_sha256, read_json
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.prompts import build_prompt
import skill_ir.recording as recording


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calls_inventory(directory: Path) -> dict[str, str]:
    return {p.relative_to(directory).as_posix(): digest(p)
            for p in directory.rglob("*") if p.is_file()
            and "calls" in p.relative_to(directory).parts
            and "replay" not in p.relative_to(directory).parts}


def _without_mode(value):
    if isinstance(value, dict):
        return {key: _without_mode(item) for key, item in value.items() if key != "mode"}
    if isinstance(value, list):
        return [_without_mode(item) for item in value]
    return value


def load_driver():
    path = ROOT / "packages/skill-ir/experiments/security_profile/tools/run_full_pipeline.py"
    spec = importlib.util.spec_from_file_location("full_security_acceptance_driver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_case(run: Path, case: dict) -> dict:
    identifier = case["case_id"]
    directory = run / case.get("run_dir", f"cases/{identifier}")
    feedback_dir = directory / "feedback"
    annotation_dir = directory / "annotation"
    row = {"case_id": identifier, "sample_id": case["sample_id"]}
    if not (feedback_dir / "manifest.json").exists():
        row.update(feedback="not_prepared", annotation="not_prepared")
        return row
    feedback_manifest = read_json(feedback_dir / "manifest.json")
    assert feedback_manifest["initial_analysis"] is None, identifier + ": old initial CFG was supplied"
    assert feedback_manifest["logical_call_bounds"] == {"extraction": 16, "audit": 4, "total": 20}
    package, source, feedback_snapshot = read_snapshot(feedback_dir)
    verify_original_input(None, feedback_snapshot)
    assert feedback_manifest["source_sha256"] == source["source_sha256"]
    inventory = {entry["path"]: {"bytes": entry["size"], "sha256": entry["raw_sha256"]}
                 for entry in feedback_snapshot["files"]}
    assert inventory == case["source_inventory"]
    feedback = read_json(feedback_dir / "result.json")
    replayed_feedback = read_json(feedback_dir / "replay/result.json")
    assert _without_mode(feedback) == _without_mode(replayed_feedback), identifier + ": feedback replay differed"
    assert feedback["source_sha256"] == source["source_sha256"]
    counts = feedback["counts"]
    assert counts["extraction_logical_calls"] <= 16
    assert counts["audit_logical_calls"] <= 4
    assert counts["total_logical_calls"] <= 20
    assert counts["semantic_revisions"] <= 3
    first = feedback_dir / "calls/r000/extraction/a001/call.json"
    if first.exists():
        assert read_json(first)["prompt"] == build_whole_skill_prompt(package), identifier + ": first prompt changed"
    audit_prompts = 0
    for round_result in feedback["rounds"]:
        revision = round_result["revision"]
        audit_call = feedback_dir / f"calls/r{revision:03}/audit/a001/call.json"
        if audit_call.exists():
            document = read_json(feedback_dir / f"rounds/r{revision:03}/controlled.json")
            actual = read_json(audit_call)["prompt"]
            assert actual == source_controlled_prompt(source, document)
            payload = json.loads(actual.split("\nINPUT_JSON\n", 1)[1])
            assert set(payload) == {"source_files", "source_line_index", "source_units", "controlled_text",
                                    "controlled_units", "required_coverage"}
            assert payload["controlled_text"] == document["text"]
            audit_prompts += 1
    row.update(feedback=feedback["status"], source_sha256=source["source_sha256"],
               readable_files=len(source["files"]), binary_files=feedback_snapshot["boundaries"]["binary_files"],
               feedback_logical_calls=counts["total_logical_calls"], initial_graph_absent=True,
               feedback_replay_identical=True, independent_audit_prompts_checked=audit_prompts)
    if not (annotation_dir / "manifest.json").exists():
        row["annotation"] = "not_prepared"
        return row
    annotation_manifest = read_json(annotation_dir / "manifest.json")
    if annotation_manifest["preparation_status"] != "ready":
        row["annotation"] = "input_error"
        return row
    assert feedback["last_valid_cfg"] is not None, identifier + ": annotation lacks an actual fresh valid graph"
    _, annotation_source, annotation_snapshot = read_snapshot(annotation_dir)
    assert annotation_source == source, identifier + ": extraction and annotation source differ"
    assert annotation_snapshot["package_bytes_sha256"] == feedback_snapshot["package_bytes_sha256"]
    assert annotation_manifest["source_sha256"] == source["source_sha256"]
    material = read_json(annotation_dir / "inputs/material.json")
    assert set(material) == {"version", "source", "cfg", "source_index", "graph_index",
                             "instruction_index", "execution_model"}
    assert material == prepare_material(source, feedback["last_valid_cfg"])
    assert material["cfg"] == feedback["last_valid_cfg"]
    assert annotation_manifest["graph_sha256"] == canonical_sha256(feedback["last_valid_cfg"])
    prompt = (annotation_dir / "inputs/prompt.txt").read_bytes().decode("utf-8")
    assert prompt == build_prompt(material)
    call = annotation_dir / "calls/annotation/a001/call.json"
    if call.exists():
        assert read_json(call)["prompt"] == prompt
    if not (annotation_dir / "result.json").exists():
        row["annotation"] = "prepared"
        return row
    annotation = read_json(annotation_dir / "result.json")
    assert annotation == read_json(annotation_dir / "replay/result.json"), identifier + ": annotation replay differed"
    assert annotation["counts"].get("logical_calls", 0) <= 1
    if annotation["status"] in {"complete", "incomplete"}:
        assert set(annotation["profiles"]) == set(material["instruction_index"])
        assert all(set(profile) == {"actor", "roles", "effects", "evidences"}
                   for profile in annotation["profiles"].values())
    row.update(annotation=annotation["status"], annotation_replay_identical=True,
               same_source_and_last_valid_cfg=True, actual_ir=len(material["instruction_index"]),
               accepted_profiles=len(annotation["profiles"]), unresolved=len(annotation["unresolved"]),
               annotation_logical_calls=annotation["counts"].get("logical_calls", 0))
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    manifest = read_json(run / "manifest.json")
    original = read_json(run / "experiment-result.json")
    assert original["mode"] == "run"
    assert len(original["cases"]) == 30
    assert tuple(case["case_id"] for case in manifest["cases"]) == tuple(f"{i:03}" for i in range(1, 31))
    # Read credentials solely to scan new artifacts after the replay. They are
    # never passed into replay, printed, or included in the output report.
    secret = load_environment(env_file=ROOT / ".env").get("LLM_API_KEY", "").strip()
    assert secret, "Expected an existing runtime credential for the local non-disclosure check"
    calls_before = calls_inventory(run)
    denied = []

    def forbidden(*args, **kwargs):
        denied.append("network_or_online_factory")
        raise AssertionError("Offline acceptance forbids networking and online client construction")

    with ExitStack() as stack:
        stack.enter_context(patch.object(socket, "create_connection", forbidden))
        stack.enter_context(patch.object(socket.socket, "connect", forbidden))
        stack.enter_context(patch.object(socket.socket, "connect_ex", forbidden))
        stack.enter_context(patch.object(urllib.request, "urlopen", forbidden))
        stack.enter_context(patch.object(recording, "streaming_factory", forbidden))
        driver = load_driver()
        replayed = driver.execute(run, mode="replay")
    assert not denied, "Replay attempted an online operation"
    assert _without_mode(replayed) == _without_mode(original), "Offline replay changed a batch outcome"
    assert calls_before == calls_inventory(run), "Offline replay changed original call artifacts"
    rows = [check_case(run, case) for case in manifest["cases"]]
    protected = read_json(ROOT / "tmp/full-security-20260917/protected-before.json")
    changed = [name for name, before in protected.items()
               if not (ROOT / name).is_file() or digest(ROOT / name) != before]
    assert not changed, f"Protected files changed: {changed}"
    hits = [p.relative_to(run).as_posix() for p in run.rglob("*")
            if p.is_file() and secret.encode("utf-8") in p.read_bytes()]
    assert not hits, "Runtime credential appeared in an artifact"
    result = {
        "cases": rows, "batch_result_replay_identical_except_mode": True,
        "offline_replay": {"network_and_online_factory_disabled": True, "network_attempts": 0,
                           "original_call_file_count": len(calls_before), "original_calls_unchanged": True},
        "protected_files": {"count": len(protected), "changed": []},
        "credentials_present_in_artifacts": False,
        "notice": "工程验收不证明核对器判断正确、模型标注正确或已实现数据传播。",
    }
    (run / "engineering-checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
