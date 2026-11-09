"""Close one finished exploratory cohort after a narrowly bound replay discrepancy.

This separate engineering verifier never launches, resumes, retries, scores, patches,
or replaces a target. The original full zero-call replay remains unmodified and its
one error is retained. Only the generation/replay absent-last-message argument
difference may be explained; the incomplete timeout remains rejected and violated.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path

from . import exploratory_cli as frozen
from .formal_cli import inside, tree_hashes
from .protocol import canonical_hash, sha256, utc_now

SCHEMA = "skillflow-exploratory-closure-compatibility-v1"
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/doe/runs/rx-20261022-0231Z"
AUDIT = ROOT / "experiments/doe/runs/execute-20261021-042102Z/closure-audit-20261022"
PROGRESS = AUDIT.parent / "progress"
REQUEST = "workflows/real-013_skillflow_r2/requests/q001"
REPLAY_ERROR = {"request": REQUEST, "reason": "Saved receipt facts differ from raw replay"}
LAST_MESSAGE_VIOLATION = "The CLI last-message file differs from the complete visible receipt answer"
VIOLATIONS = [
    "The fresh CLI session must contain exactly one started and completed turn",
    "The visible final answer lacks exactly one attributed completion event",
    "Unknown or inconsistent per-response usage forbids further dispatch",
    "The visible final answer lacks one exact receipt item identity",
    "CLI stdout does not contain exactly the receipt's complete visible final answer",
    "CLI stdout contains a prohibited or unsupported tool/delegation item",
]
AUGMENTATION_KEYS = {"assessment_scope", "raw_receipt_path", "raw_receipt_sha256",
                     "process_result_sha256", "stdout_sha256"}
INDEX_SHA256 = "ff1c5ab03b9642399a9ec2d5550de5e7bb95af637307abf3944d394ccac818c0"
DIAGNOSTIC = "closure-replay-diagnostic-20261022-0703Z.json"
DIAGNOSTIC_SHA256 = "7e4949dd5f6b155dc9fb504a86b9cc1fe65fdf802be91626d5c99781cbff57f8"
DIFFERENCE = "closure-receipt-difference-20261022-0710Z.json"
DIFFERENCE_SHA256 = "e185e76662ccb4f9de544faffc2437099f67dad0008c535a487dd9875a538ef0"
PINS = {
    "freeze.json": "c363b7d1086a5ff340fbb880a92b65358d0df806a3e1a2446eaf96a2f82f8820",
    "plan.json": "e9ac3830e41203b871ced663a3e81ce14906986367c934cb8aa1ae56fd724b93",
    "schedule.json": "4d2de9c6b16e1cf1cbdd4198c648cb327f59dfabd3a302a2e5632484de9fe0a7",
    "dispatch-stop.json": "73ab8e9cdd6342a4e8b03a4d69d63947a796e4fa7778c2bce649208cfe700799",
    "controller-finished.json": "3da190a6826fe9d07278266d3305f964e5ea13676988b8c4d42ab4c30f90113f",
    REQUEST + "/receipt.json": "5d68c123494b7d4f0c44966ed55b8a8fefb2c934295dec367ff8cb3c770cb719",
    REQUEST + "/response.json": "6e88779a903b752a9ae976eb64bb1ed2fb061dc04574b715e985a0ffac6d7ca2",
    REQUEST + "/request.json": "732347c0ab1cd23e3e100f9bbb006191f0de530528ada959549f9ae5d60cc25c",
    REQUEST + "/cli/launch.json": "8c40b39a71a5a1a0c92649e3938c49679cbc7d47488fbe9f4a0f9af5385df655",
    REQUEST + "/cli/process-result.json": "1c54f9447b9500d2072a83d0154b4b988ccdd2b4866eb7d98abc7f957c2a11b5",
    REQUEST + "/cli/stdout.jsonl": "2fc4c01be4a70769097aced185fd6c4153efcfcb171f2032626e7a906c0169c0",
}
CODE_PINS = {
    "tools/doe/real_comparison/exploratory_cli.py": "259c6c38e5a305087478c3fe59b7e241431381f5f43afe40a0a0a3047cb9ad60",
    "tools/doe/real_comparison/cli_adapter_v3.py": "d169eb921052f75cb5f6f287626f3659ed0c4ded4d7007ad6fa91dc36bdd31c7",
}


class CompatibilityError(ValueError):
    """An unapproved engineering difference prevents closure."""


def require(condition, message):
    if not condition:
        raise CompatibilityError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_pins(root, pins):
    for relative, expected in pins.items():
        require(sha256(inside(root, relative)) == expected,
                "Pinned engineering evidence changed: " + relative)


def validate_replay_report(report):
    """Reject even an extra error, a missing error, or a changed replay claim."""
    require(report.get("schema_version") == frozen.SCHEMA
            and report.get("status") == "errors"
            and type(report.get("model_calls")) is int and report["model_calls"] == 0
            and report.get("semantics_scored") is False
            and report.get("errors") == [REPLAY_ERROR],
            "The frozen full replay must retain exactly the documented single error")


def validate_timeout_compatibility(saved, response, process, generation, replayed, *,
                                   generation_answer, replayed_answer,
                                   last_message_exists, answer_exists):
    """Pure comparison predicate; it cannot change any receipt or acceptance."""
    require(generation_answer is None and replayed_answer is None
            and last_message_exists is False and answer_exists is False,
            "Compatibility is limited to an absent answer and absent last-message file")
    require(set(saved) - set(generation) == AUGMENTATION_KEYS
            and {k: v for k, v in saved.items() if k not in AUGMENTATION_KEYS} == generation,
            "Generation-equivalent inspection must reproduce every saved receipt fact")
    require(saved.get("assessment_scope") == frozen.SCHEMA
            and saved.get("protocol_status") == "violated"
            and saved.get("violations") == VIOLATIONS
            and saved.get("completed") is False
            and saved.get("usage_verified") is False
            and saved.get("configuration_verified") is True
            and saved.get("provider_verified") is True
            and saved.get("tools") == [] and saved.get("diagnostics") == []
            and saved.get("final_item_ids") == [] and saved.get("output_sha256") is None,
            "The original six violations and incomplete rejected timeout must be preserved")
    usage = saved.get("usage", {})
    require(usage.get("by_response_id") == {} and usage.get("response_count") == 0
            and usage.get("totals") == {key: None for key in frozen.v3.TOKEN_FIELDS},
            "The timeout's unobserved usage must remain unknown")
    elapsed = process.get("supervisor_elapsed_seconds")
    require(process.get("status") == "timeout"
            and process.get("actual_cli_process_started") is True
            and process.get("returncode") == 1 and process.get("error") is None
            and process.get("retries") == 0
            and type(elapsed) in (int, float) and math.isfinite(elapsed)
            and 2700 <= elapsed < 2705,
            "Only the preserved single 45-minute process timeout is compatible")
    require(response.get("accepted") is False and response.get("answer_sha256") is None
            and response.get("process_status") == "timeout",
            "The saved timeout response must remain unaccepted")
    expected = deepcopy(generation)
    expected["violations"] = VIOLATIONS + [LAST_MESSAGE_VIOLATION]
    require(replayed == expected,
            "Only the one appended absent-last-message violation may differ")
    return {"request": REQUEST, "generation_equivalent_receipt": "exact_saved_match",
            "frozen_replay_difference": {"field": "violations", "appended": LAST_MESSAGE_VIOLATION},
            "preserved_violations": list(VIOLATIONS), "response_accepted": False,
            "completed": False, "protocol_status": "violated", "usage_verified": False,
            "usage_remains_unknown": True, "answer_present": False, "last_message_present": False}


def verify_timeout_request(run):
    directory = run / REQUEST
    saved, launch = read(directory / "receipt.json"), read(directory / "cli/launch.json")
    process, response = read(directory / "cli/process-result.json"), read(directory / "response.json")
    require(sha256(saved["raw_receipt_path"]) == saved["raw_receipt_sha256"]
            == saved["receipt_sha256"]
            and sha256(directory / "cli/stdout.jsonl") == saved["stdout_sha256"]
            and sha256(directory / "cli/process-result.json") == saved["process_result_sha256"]
            and sha256(directory / "cli/launch.json") == process["launch_sha256"],
            "The exact timeout raw receipt, stdout, launch and process evidence must match")
    last_message, answer = directory / "cli/last-message.txt", directory / "answer.txt"
    require(not last_message.exists() and not answer.exists(), "The timeout has acquired a visible answer")
    # These are the exact generation 295-297 and frozen replay 528-529 arguments.
    # The frozen adapter and runner functions are never replaced or monkeypatched.
    gen_answer, generation = frozen.cli.inspect_receipt(
        saved["raw_receipt_path"], saved["cli_session_id"], launch,
        stdout_path=directory / "cli/stdout.jsonl", last_message_path=None)
    old_answer, replayed = frozen.cli.inspect_receipt(
        saved["raw_receipt_path"], saved["cli_session_id"], launch,
        stdout_path=directory / "cli/stdout.jsonl", last_message_path=last_message)
    result = validate_timeout_compatibility(saved, response, process, generation, replayed,
        generation_answer=gen_answer, replayed_answer=old_answer,
        last_message_exists=last_message.exists(), answer_exists=answer.exists())
    result["evidence_sha256"] = {name: sha256(directory / name) for name in (
        "receipt.json", "response.json", "request.json", "cli/launch.json",
        "cli/process-result.json", "cli/stdout.jsonl")}
    result["raw_receipt_sha256"] = saved["raw_receipt_sha256"]
    return result


def verify_accounting(run):
    """Cover all terminal identities, including the request skipped by old replay."""
    schedule = read(run / "schedule.json")
    items = schedule["main"] + schedule["reviews"]
    require(len(schedule["main"]) == 216 and len(schedule["reviews"]) == 48
            and len({row["workflow_id"] for row in items}) == 264,
            "The exact 216 main and 48 review terminal identities are required")
    require({p.name for p in (run / "workflows").iterdir() if p.is_dir()}
            == {row["workflow_id"] for row in items}, "The workflow cohort differs from the fixed schedule")
    statuses, attempted, native_count, candidate_count = Counter(), 0, 0, 0
    for item in items:
        workflow = run / "workflows" / item["workflow_id"]
        result = read(workflow / "result.json")
        require(result.get("schema_version") == frozen.SCHEMA
                and result.get("workflow_id") == item["workflow_id"]
                and result.get("status") in {"complete", "failed", "not_reviewable", "protocol_aborted"},
                "A planned workflow lacks an unambiguous terminal result")
        statuses[result["status"]] += 1
        attempted += bool(frozen.requests(run, item["workflow_id"]))
        native_count += bool(result.get("native"))
        if result.get("artifact_manifest_sha256"):
            frozen.verify_candidate(run, item["workflow_id"], result)
            candidate_count += 1
    require(statuses == Counter(complete=28, failed=15, not_reviewable=36, protocol_aborted=185)
            and attempted == 43, "The preserved terminal cohort accounting changed")
    sessions, response_ids, accepted, timed_out = set(), set(), 0, 0
    request_dirs = frozen.requests(run)
    require(len(request_dirs) == 140, "Exactly 140 preserved CLI requests are required")
    for directory in request_dirs:
        receipt, response = read(directory / "receipt.json"), read(directory / "response.json")
        process = read(directory / "cli/process-result.json")
        start = read(directory / "cli/process-start.json")
        require(start.get("actual_cli_process_started") is True
                and process.get("actual_cli_process_started") is True,
                "Every retained target request must preserve its actual process-start evidence")
        require(sha256(receipt["raw_receipt_path"]) == receipt["raw_receipt_sha256"],
                "A preserved external raw receipt changed")
        session, identities = receipt["cli_session_id"], set(receipt["usage"]["by_response_id"])
        require(session not in sessions and not response_ids.intersection(identities),
                "A saved CLI session or response identity is duplicated")
        sessions.add(session)
        response_ids.update(identities)
        answer = directory / "answer.txt"
        has_answer = receipt.get("output_sha256") is not None
        require(answer.is_file() == has_answer
                and response.get("answer_sha256") == receipt.get("output_sha256")
                and (not has_answer or sha256(answer) == receipt["output_sha256"])
                and response.get("process_status") == process.get("status"),
                "A saved answer hash or process/response attribution changed")
        expected_accepted = (not receipt["violations"] and receipt.get("protocol_status") == "conformant"
            and all(receipt.get(k) is True for k in ("configuration_verified", "provider_verified", "usage_verified", "completed"))
            and has_answer and process.get("status") == "process_exited" and process.get("returncode") == 0)
        require(response.get("accepted") is expected_accepted,
                "A saved response acceptance decision differs from generation's predicate")
        accepted += expected_accepted
        timed_out += process.get("status") == "timeout"
    usage = frozen.usage(run)
    require(accepted == 139 and timed_out == 1 and len(response_ids) == 139
            and usage.get("response_count") == 139 and usage.get("conflicting_response_ids") == []
            and usage.get("missing_requests") == [(run / REQUEST).as_posix()]
            and usage.get("totals") == {key: None for key in frozen.v3.TOKEN_FIELDS},
            "The 139 accepted responses and one unknown-cost timeout must remain distinct")
    return {"planned_outputs": 264, "terminal_results": 264, "statuses": dict(statuses),
            "attempted_workflows": attempted, "unlaunched_workflows": 264 - attempted,
            "actual_cli_starts": 140, "accepted_responses": accepted,
            "timed_out_unknown_usage": timed_out, "unique_observed_response_ids": len(response_ids),
            "native_workflows_replayed_by_frozen_full_replay": native_count,
            "candidate_manifests_verified": candidate_count}


def exclusive_json(path, value):
    """Publish only a new file; existing receipts, outputs and audits are immutable."""
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_engineering_binding(path, digest):
    path = Path(path).resolve()
    require(path.is_relative_to(AUDIT.resolve()) and not path.is_symlink() and sha256(path) == digest,
            "The exact engineering preparation record must be bound under this closure audit")
    value = read(path)
    require(value.get("schema_version") == "skillflow-exploratory-closure-engineering-preparation-v1"
            and value.get("model_calls") == 0 and value.get("actual_cohort_replay_invoked") is False
            and value.get("semantic_grading_participation") is False
            and value.get("preserved_index_sha256") == INDEX_SHA256,
            "The engineering preparation identity or isolation claim differs")
    verify_pins(ROOT, value["implementation_and_tests"])
    require(value["implementation_and_tests"].get(Path(__file__).relative_to(ROOT).as_posix()) == sha256(__file__),
            "The reviewed compatibility verifier bytes changed")
    verify_pins(AUDIT, value["test_evidence"])
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest,
            "implementation_and_tests": value["implementation_and_tests"], "test_evidence": value["test_evidence"]}


def close_outputs(run_dir, *, engineering_audit, engineering_audit_sha256):
    """Perform one full frozen zero-call replay, then publish truthful new seals."""
    run = Path(run_dir).resolve()
    require(run == RUN.resolve(), "This verifier is bound to one finished exploratory run only")
    destinations = [run / "output-freeze.json", run / "summary.json",
                    AUDIT / "frozen-replay-final.json", AUDIT / "compatibility-verification.json"]
    require(not any(path.exists() for path in destinations), "Closure never replaces an existing output or audit")
    binding = load_engineering_binding(engineering_audit, engineering_audit_sha256)
    verify_pins(ROOT, CODE_PINS)
    verify_pins(run, PINS)
    verify_pins(PROGRESS, {DIAGNOSTIC: DIAGNOSTIC_SHA256, DIFFERENCE: DIFFERENCE_SHA256})
    previous = read(PROGRESS / DIAGNOSTIC)
    validate_replay_report(previous)
    index_path = AUDIT / "preserved-evidence-index.json"
    require(sha256(index_path) == INDEX_SHA256, "The preserved whole-run evidence index changed")
    index = read(index_path)
    require(index.get("file_count") == len(index["files"]) == 5523
            and index.get("files_canonical_sha256") == canonical_hash(index["files"]),
            "The preserved whole-run index is internally inconsistent")
    require(tree_hashes(run) == index["files"], "Finished generation evidence changed before verification")
    frozen.verify_run(run, generation=False)
    accounting = verify_accounting(run)
    timeout = verify_timeout_request(run)
    started = utc_now()
    # The only full replay invocation. include_native cannot be disabled.
    report = frozen.replay(run, include_native=True)
    validate_replay_report(report)
    require(report == previous, "The full frozen replay differs from its retained diagnostic")
    require(tree_hashes(run) == index["files"],
            "Frozen replay changed existing evidence, including derived replay files; no files are excluded")
    frozen.verify_run(run, generation=False)
    require(verify_accounting(run) == accounting, "Terminal or acceptance accounting changed during replay")
    require(verify_timeout_request(run) == timeout, "Timeout evidence changed during replay")
    result = frozen.summary(run)
    require(result["closed_results"] == 264 and result["global_stop"] is True
            and result["semantics_scored"] is False, "The completed stopped cohort must remain unscored")
    exclusive_json(AUDIT / "frozen-replay-final.json", report)
    verification = {"schema_version": SCHEMA, "started_at": started, "finished_at": utc_now(),
        "run_directory": str(run), "status": "compatible_closure_verified",
        "model_calls": 0, "semantic_grading_participation": False,
        "original_frozen_replay_status": report["status"], "original_frozen_replay_errors": report["errors"],
        "original_replay_was_matched": False, "original_full_replay_includes_native": True,
        "final_frozen_replay": {"path": "frozen-replay-final.json", "sha256": sha256(AUDIT / "frozen-replay-final.json")},
        "previous_diagnostic": {"path": str(PROGRESS / DIAGNOSTIC), "sha256": DIAGNOSTIC_SHA256},
        "previous_receipt_difference": {"path": str(PROGRESS / DIFFERENCE), "sha256": DIFFERENCE_SHA256},
        "engineering_preparation": binding, "verifier_sha256": sha256(__file__),
        "preserved_index_sha256": INDEX_SHA256, "preserved_file_count": index["file_count"],
        "preserved_files_canonical_sha256": index["files_canonical_sha256"],
        "pre_and_post_replay_whole_tree": "identical", "excluded_files": [],
        "derived_replay_policy": "All existing native replay derivations are also required byte-identical. Any new, removed or changed file fails closure.",
        "code_argument_binding": {"path": "tools/doe/real_comparison/exploratory_cli.py",
            "sha256": CODE_PINS["tools/doe/real_comparison/exploratory_cli.py"],
            "generation_lines": [295, 297], "generation_absent_last_message_argument": None,
            "frozen_replay_lines": [528, 529], "frozen_replay_absent_last_message_argument": "nonexistent Path",
            "adapter_path": "tools/doe/real_comparison/cli_adapter_v3.py", "adapter_lines": [318, 319],
            "adapter_sha256": CODE_PINS["tools/doe/real_comparison/cli_adapter_v3.py"]},
        "compatibility_exception": timeout, "accounting": accounting,
        "scope": "Engineering byte integrity and closure only. All original failures, protocol violations, unknown usage and planned denominators remain; no semantic success, compliance or method advantage is established."}
    exclusive_json(AUDIT / "compatibility-verification.json", verification)
    provenance = {"schema_version": SCHEMA, "verifier_path": Path(__file__).relative_to(ROOT).as_posix(),
        "verifier_sha256": sha256(__file__), "audit_path": str(AUDIT / "compatibility-verification.json"),
        "audit_sha256": sha256(AUDIT / "compatibility-verification.json"),
        "original_frozen_replay_status": "errors", "original_frozen_replay_errors": [REPLAY_ERROR],
        "compatibility_status": "compatible_closure_verified", "accepted_timeout": False,
        "model_calls": 0, "semantic_grading_participation": False}
    result["closure_compatibility"] = provenance
    # Summary and audits are complete before the permanent generation-closure marker.
    exclusive_json(run / "summary.json", result)
    files = tree_hashes(run / "workflows")
    require({"workflows/" + k: v for k, v in files.items()}
            == {k: v for k, v in index["files"].items() if k.startswith("workflows/")},
            "The workflow evidence changed before output publication")
    expected_with_summary = {**index["files"], "summary.json": sha256(run / "summary.json")}
    require(tree_hashes(run) == expected_with_summary,
            "Existing run evidence changed before permanent closure publication")
    verify_pins(ROOT, binding["implementation_and_tests"])
    frozen.verify_run(run, generation=False)
    exclusive_json(run / "output-freeze.json", {"schema_version": frozen.SCHEMA, "closed_at": utc_now(),
        "planned_outputs": 264, "files": {"workflows/" + k: v for k, v in files.items()},
        "failed_results_remain_in_denominator": True, "closure_compatibility": provenance,
        "summary_sha256": sha256(run / "summary.json")})
    return {"schema_version": SCHEMA, "status": "closed_with_disclosed_compatibility_exception",
            "model_calls": 0, "semantics_scored": False, "accounting": accounting,
            "original_frozen_replay_status": "errors", "original_frozen_replay_errors": [REPLAY_ERROR],
            "output_freeze_sha256": sha256(run / "output-freeze.json"),
            "summary_sha256": sha256(run / "summary.json"), "closure_compatibility": provenance}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--engineering-audit", required=True)
    parser.add_argument("--engineering-audit-sha256", required=True)
    args = parser.parse_args(argv)
    result = close_outputs(args.run_dir, engineering_audit=args.engineering_audit,
                           engineering_audit_sha256=args.engineering_audit_sha256)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
