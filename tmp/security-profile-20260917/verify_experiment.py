"""Post-run acceptance only: no online operation is permitted."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import urllib.request

from skill_ir.inputs.snapshot import read_snapshot, verify_original_input
from skill_ir.llm.config import load_environment
from skill_ir.recording import canonical_sha256, read_json
import skill_ir.recording as recording
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.prompts import build_prompt

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "packages/skill-ir/experiments/security_profile/runs/security-profile-20260917"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden(*args, **kwargs):
    raise AssertionError("Offline acceptance forbids networking and online client construction")


def main():
    manifest = read_json(RUN / "manifest.json")
    original = read_json(RUN / "experiment-result.json")
    assert original["mode"] == "run"
    assert len(original["cases"]) == 30
    assert tuple(c["case_id"] for c in manifest["cases"]) == tuple(f"{i:03}" for i in range(1, 31))
    calls_before = {p.relative_to(RUN).as_posix(): digest(p)
                    for p in RUN.glob("cases/*/calls/**/*") if p.is_file()}
    socket.create_connection = forbidden
    socket.socket.connect = forbidden
    urllib.request.urlopen = forbidden
    recording.streaming_factory = forbidden
    path = ROOT / "packages/skill-ir/experiments/security_profile/tools/run_review_set.py"
    spec = importlib.util.spec_from_file_location("security_acceptance_driver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    replayed = module.execute(RUN, mode="replay")
    assert replayed["cases"] == original["cases"], "Offline replay changed a case outcome"
    assert replayed["summary"] == original["summary"]
    calls_after = {p.relative_to(RUN).as_posix(): digest(p)
                   for p in RUN.glob("cases/*/calls/**/*") if p.is_file()}
    assert calls_before == calls_after, "Offline replay changed original call artifacts"
    cases = []
    readable = 0
    binary = 0
    all_ir = 0
    for case in manifest["cases"]:
        directory = RUN / case["run_dir"]
        _, source, metadata = read_snapshot(directory)
        verify_original_input(None, metadata)
        material = read_json(directory / "inputs/material.json")
        cfg = read_json(ROOT / case["analysis_path"])["cfg"]
        assert material == prepare_material(source, cfg)
        assert material["cfg"] == cfg
        assert material["source"] == source
        assert set(material) == {"version", "source", "cfg", "source_index", "graph_index",
                                 "instruction_index", "execution_model"}
        prompt = (directory / "inputs/prompt.txt").read_bytes().decode("utf-8")
        assert prompt == build_prompt(material)
        call = read_json(directory / "calls/annotation/a001/call.json")
        assert call["prompt"] == prompt
        assert case["repetition"] == (3 if case["sample_id"] == "F03" else 1)
        outcome = original["cases"][case["case_id"]]
        assert outcome["counts"]["logical_calls"] == 1
        assert not outcome["counts"]["record_integrity_errors"]
        expected_ids = set(material["instruction_index"])
        if outcome["status"] in {"complete", "incomplete"}:
            assert set(outcome["profiles"]) == expected_ids
            assert all(set(p) == {"actor", "roles", "effects", "evidences"}
                       for p in outcome["profiles"].values())
        readable += len(source["files"])
        binary += len(metadata["boundaries"]["binary_files"])
        all_ir += len(expected_ids)
        cases.append({"case_id": case["case_id"], "sample_id": case["sample_id"],
                      "status": outcome["status"], "actual_ir": len(expected_ids),
                      "accepted_profiles": len(outcome["profiles"]),
                      "prompt_sha256": canonical_sha256(prompt),
                      "replay_identical": True, "full_source_and_cfg": True})
    baseline = read_json(ROOT / "tmp/security-profile-20260917/protected-before.json")
    changed = [p for p, before in baseline.items() if not (ROOT / p).is_file() or digest(ROOT / p) != before]
    assert not changed, f"Protected files changed: {changed}"
    secret = load_environment(env_file=ROOT / ".env").get("LLM_API_KEY", "").strip()
    assert secret
    credential_hits = [p.relative_to(RUN).as_posix() for p in RUN.rglob("*")
                       if p.is_file() and secret.encode() in p.read_bytes()]
    assert not credential_hits, "A runtime credential appeared in an artifact"
    result = {
        "cases": cases, "full_source_and_raw_cfg_cases": 30,
        "readable_files": readable, "binary_files_recorded_as_boundary": binary,
        "actual_ir": all_ir, "summary": original["summary"],
        "offline_replay": {"network_and_client_construction_disabled": True,
                           "identical_case_results": 30, "original_call_artifacts_unchanged": True},
        "protected_files": {"count": len(baseline), "changed": changed},
        "credentials_present_in_artifacts": False,
        "note": "工程检查不证明模型推断或安全标注语义正确。",
    }
    (RUN / "engineering-checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "cases"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
