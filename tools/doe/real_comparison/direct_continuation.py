"""Prospective direct-only continuation; preserves the stopped comparison intact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

from . import exploratory_cli as base
from .artifacts import verify_candidate
from .formal_cli import tree_hashes
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-direct-only-continuation-v1"
USER_QUOTE = "这里先暂停skillflow的请求，我在另一个进程开了。强模型不要断了"
MODULE_PATH = "tools/doe/real_comparison/direct_continuation.py"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def prepare(run_dir, donor_dir, steering_path):
    run, donor = Path(run_dir).resolve(), Path(donor_dir).resolve()
    if run.exists() or run.is_relative_to(donor) or donor.is_relative_to(run):
        raise ValueError("Use a fresh independent continuation directory")
    base.verify_run(donor, generation=False)
    if not (donor / "controller-finished.json").exists():
        raise ValueError("The donor controller must have stopped before continuation")
    steering = Path(steering_path).resolve()
    if USER_QUOTE not in json.dumps(read(steering), ensure_ascii=False):
        raise ValueError("The exact user instruction must authorize direct continuation and pause SkillFlow")
    original = read(donor / "schedule.json")
    schedule = {**original,
                "main": [x for x in original["main"] if x["method"] in {"audit", "chain"}],
                "reviews": [x for x in original["reviews"] if x["method"] in {"audit", "chain"}]}
    if len(schedule["main"]) != 144 or len(schedule["reviews"]) != 48:
        raise ValueError("Exactly 144 direct mains and 48 fixed R1 reviews are required")
    imports, pending = [], []
    for item in schedule["main"] + schedule["reviews"]:
        directory = donor / "workflows" / item["workflow_id"]
        result = read(directory / "result.json")
        requests = list(directory.glob("requests/q*"))
        if item["kind"] == "main" and result["status"] == "complete":
            verify_candidate(donor, item["workflow_id"], result)
            if sha256(directory / "answer.txt") != result["answer_sha256"] or len(requests) != 1:
                raise ValueError("A donor answer does not bind its exact one-shot delivery")
            response, receipt = read(requests[0] / "response.json"), read(requests[0] / "receipt.json")
            if not response.get("accepted") or receipt.get("protocol_status") != "conformant":
                raise ValueError("Imported direct output lacks an accepted conformant receipt")
            imports.append({"workflow_id": item["workflow_id"],
                "result_sha256": sha256(directory / "result.json"),
                "answer_sha256": result["answer_sha256"],
                "original_request_count": 1, "new_target_requests": 0})
        else:
            if requests or result.get("attempts", 0) != 0 or result["status"] not in {"protocol_aborted", "not_reviewable"}:
                raise ValueError("A previously attempted workflow must never be regenerated: " + item["workflow_id"])
            pending.append(item["workflow_id"])
    if len(imports) != 28 or len(pending) != 164:
        raise ValueError("The stopped donor must contribute 28 original outputs and 164 unlaunched identities")
    run.mkdir(parents=True)
    old_seal = read(donor / "freeze.json")
    for name in old_seal["files"]:
        copy(donor / name, run / name)
    copy(donor / "freeze.json", run / "donor-input-freeze.json")
    copy(donor / "plan.json", run / "donor-plan.json")
    copy(donor / "dispatch-stop.json", run / "donor-dispatch-stop.json")
    copy(steering, run / "direct-only-user-steering.json")
    for item in imports:
        shutil.copytree(donor / "workflows" / item["workflow_id"], run / "workflows" / item["workflow_id"])
    write_json(run / "schedule.json", schedule)
    lineage = {"schema_version": SCHEMA, "created_at": utc_now(), "user_quotation": USER_QUOTE,
        "donor_run": str(donor), "donor_freeze_sha256": sha256(donor / "freeze.json"),
        "donor_stop_sha256": sha256(donor / "dispatch-stop.json"),
        "paused_method": "skillflow", "other_user_process_controlled": False,
        "planned_direct_mains": 144, "planned_fixed_reviews": 48, "logical_outcomes": 192,
        "retained_original_outputs": imports, "new_workflow_ids": pending,
        "new_planned_workflows": 164, "new_planned_mains": 116, "new_planned_reviews": 48,
        "target_resampling": False, "target_extra_calibration_calls": 0,
        "protocol": "Unchanged frozen direct prompts, source, runtime, delivery wrapper, limits and global-stop policy. Only previously unlaunched direct identities may launch. No SkillFlow target call is scheduled.",
        "accounting": "Imported receipts are original calls, not new launches. Deduplicate response IDs across donor and continuation; preserve the donor timeout's unknown usage separately.",
        "inference_limit": "A prospective direct-only epoch cannot by itself complete the interrupted same-model three-way comparison. Do not merge an independently launched SkillFlow process without separate identity and protocol evidence."}
    write_json(run / "direct-continuation.json", lineage, immutable=True)
    plan = read(run / "plan.json")
    plan.update(created_at=utc_now(), planned_main_workflows=144, planned_reviews=48,
        planned_outputs=192, scope=SCHEMA, paused_methods=["skillflow"],
        inherited_completed_workflows=28, new_planned_workflows=164,
        continuation_manifest_sha256=sha256(run / "direct-continuation.json"))
    write_json(run / "plan.json", plan)
    implementation = dict(old_seal["implementation"])
    implementation[MODULE_PATH] = sha256(base.ROOT / MODULE_PATH)
    write_json(run / "freeze.json", {"schema_version": base.SCHEMA,
        "files": tree_hashes(run), "implementation": implementation,
        "reference_and_scores_enter_target_inputs": False}, immutable=True)
    verify(run)
    for item in imports:
        verify_candidate(run, item["workflow_id"], read(run / "workflows" / item["workflow_id"] / "result.json"))
    return summary(run)


def verify(run_dir):
    run = Path(run_dir).resolve()
    manifest = base.verify_run(run)
    plan, lineage, schedule = read(run / "plan.json"), read(run / "direct-continuation.json"), read(run / "schedule.json")
    rows = schedule["main"] + schedule["reviews"]
    if (lineage.get("schema_version") != SCHEMA or lineage.get("user_quotation") != USER_QUOTE
            or lineage.get("paused_method") != "skillflow" or plan.get("planned_outputs") != 192
            or len(schedule["main"]) != 144 or len(schedule["reviews"]) != 48
            or len({x["workflow_id"] for x in rows}) != 192
            or any(x["method"] not in {"audit", "chain"} for x in rows)
            or {x["workflow_id"] for x in rows} != set(lineage["new_workflow_ids"]) | {x["workflow_id"] for x in lineage["retained_original_outputs"]}
            or plan.get("continuation_manifest_sha256") != sha256(run / "direct-continuation.json")):
        raise ValueError("The immutable allowlist must contain only the fixed direct identities")
    return manifest


def summary(run_dir):
    run = Path(run_dir).resolve()
    raw = base.summary(run)
    lineage = read(run / "direct-continuation.json")
    inherited = {x["workflow_id"] for x in lineage["retained_original_outputs"]}
    raw.update(schema_version=SCHEMA, planned_denominator=192, planned_main_denominator=144,
        planned_review_denominator=48, inherited_completed_outputs=28,
        new_planned_workflows=164,
        new_closed_workflows=sum(x["workflow_id"] not in inherited and x["status"] != "not_generated" for x in raw["outcomes"]),
        new_actual_cli_starts=sum(
            (p / "cli/process-start.json").exists()
            and read(p / "cli/process-start.json").get("actual_cli_process_started") is True
            for wid in lineage["new_workflow_ids"] for p in base.requests(run, wid)),
        paused_method="skillflow", old_run_failures_retained=True)
    return raw


def run_batch(run_dir):
    run = Path(run_dir).resolve()
    verify(run)
    def guarded(directory, workflow_id):
        verify(directory)
        item = base.planned(directory, workflow_id)
        if item["method"] not in {"audit", "chain"}:
            raise ValueError("SkillFlow target requests are paused in this chat")
        return base.run_workflow(directory, workflow_id)
    # The unchanged worker engine enforces the retained lock, request limits,
    # exact transport and global stop. Its fixed-264 summary is not reported.
    base.run_batch(run, workers=6, runner=guarded)
    return summary(run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify", "summary", "run-batch"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--donor-dir")
    parser.add_argument("--steering")
    args = parser.parse_args()
    if args.command == "prepare":
        if not args.donor_dir or not args.steering:
            parser.error("prepare requires --donor-dir and --steering")
        value = prepare(args.run_dir, args.donor_dir, args.steering)
    elif args.command == "run-batch":
        value = run_batch(args.run_dir)
    elif args.command == "summary":
        value = summary(args.run_dir)
    else:
        verify(args.run_dir)
        value = {"status": "verified_direct_only", "target_calls": 0}
    if args.command == "prepare":
        value = {k: value[k] for k in ("schema_version", "planned_denominator", "inherited_completed_outputs", "new_planned_workflows", "new_actual_cli_starts", "paused_method")}
    print(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
