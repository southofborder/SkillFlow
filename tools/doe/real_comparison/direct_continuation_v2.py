"""Prospective remaining-output epoch with a separately verified CLI profile.

Frozen runner functions are dependency-injected into private namespaces. Their
code objects and original globals remain unchanged; only verification and the
experimental transport are supplied here. No scoring or SkillFlow is scheduled.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
from types import FunctionType

from . import exploratory_cli as base
from . import controlled_cli_v4 as transport
from .artifacts import verify_candidate
from .formal_cli import tree_hashes
from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-direct-remaining-outputs-v2"
USER_QUOTE = "先把强模型所有结果跑出来，后面等skillflow结果出来后一并审计"
MODULE = "tools/doe/real_comparison/direct_continuation_v2.py"
TRANSPORT_MODULE = "tools/doe/real_comparison/controlled_cli_v4.py"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(value, reason):
    if not value:
        raise ValueError(reason)


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def verify_archived_production(run):
    """Direct methods use no live semantic pipeline; retain its old snapshot."""
    record = read(run / "production-code-freeze.json")
    base.verify_files(run, record["files"])


def verify_donor(donor):
    """Verify sealed bytes without pretending the removed old executable exists."""
    seal = read(donor / "freeze.json")
    base.verify_files(donor, seal["files"])
    base.verify_files(base.ROOT, seal["implementation"])
    verify_archived_production(donor)
    output = read(donor / "output-freeze.json")
    base.verify_files(donor, output["files"])
    require((donor / "controller-finished.json").is_file(), "The donor must be terminal")
    rows = base.planned(donor)
    require(len(rows) == 192 and all((donor / "workflows" / x["workflow_id"] / "result.json").is_file()
            and read(donor / "workflows" / x["workflow_id"] / "result.json")["status"]
            in {"complete", "failed", "protocol_aborted", "not_reviewable"} for x in rows),
            "The donor must preserve all192 terminal outcomes")
    require(read(donor / "plan.json")["runtime"] == transport.EXPECTED,
            "The donor model identity must remain exact")
    return output


def prepare(run_dir, donor_dir, steering_path, profile_path):
    run, donor = Path(run_dir).resolve(), Path(donor_dir).resolve()
    require(not run.exists() and not run.is_relative_to(donor) and not donor.is_relative_to(run),
            "A new independent run directory is required")
    verify_donor(donor)
    steering, profile = read(steering_path), read(profile_path)
    require(steering.get("user_quotation") == USER_QUOTE and steering.get("semantic_grading_paused") is True,
            "The latest exact generation-first instruction is required")
    require(profile.get("runtime") == transport.EXPECTED and profile.get("controlled_transport") is True
            and profile.get("engineering_checks_passed") is True,
            "A verified prospective transport profile is required")
    require(profile.get("executable_sha256") == transport.PINNED_EXECUTABLE_SHA256
            and sha256(profile["executable"]) == transport.PINNED_EXECUTABLE_SHA256
            and profile.get("cli_version") == transport.PINNED_VERSION
            and profile.get("disabled_features") == list(transport.DISABLED_FEATURES),
            "The new executable must match its explicit prospective identity")
    schedule = read(donor / "schedule.json")
    rows = schedule["main"] + schedule["reviews"]
    require(len(schedule["main"]) == 144 and len(schedule["reviews"]) == 48
            and len({x["workflow_id"] for x in rows}) == 192
            and all(x["method"] in {"audit", "chain"} for x in rows),
            "The full fixed direct-only schedule is required")
    retained, pending = [], []
    for item in rows:
        directory = donor / "workflows" / item["workflow_id"]
        result = read(directory / "result.json")
        requests = list(directory.glob("requests/q*"))
        if requests:
            require(item["kind"] == "main" and len(requests) == 1 and result["status"] in {"complete", "failed"},
                    "Previously attempted targets may never be regenerated")
            if result["status"] == "complete":
                verify_candidate(donor, item["workflow_id"], result)
                require(sha256(directory / "answer.txt") == result["answer_sha256"]
                        and read(requests[0] / "response.json").get("accepted") is True,
                        "A completed donor must bind its exact accepted answer")
            retained.append({"workflow_id": item["workflow_id"], "status": result["status"],
                             "files": tree_hashes(directory), "new_target_requests": 0})
        else:
            require(result.get("attempts", 0) == 0
                    and result["status"] in {"protocol_aborted", "not_reviewable"},
                    "Only never-launched target identities may enter the new queue")
            pending.append(item["workflow_id"])
    require(sum(x["status"] == "complete" for x in retained) == 75
            and sum(x["status"] == "failed" for x in retained) == 6
            and len(pending) == 111
            and sum(x["workflow_id"] in pending for x in schedule["main"]) == 63
            and sum(x["workflow_id"] in pending for x in schedule["reviews"]) == 48,
            "Expected exact donor partition 75 complete,6 failed,63 new mains,48 new reviews")
    run.mkdir(parents=True)
    old = read(donor / "freeze.json")
    for name in old["files"]:
        copy(donor / name, run / name)
    for name in ("freeze.json", "plan.json", "current-harness-manifest.json", "output-freeze.json", "dispatch-stop.json"):
        copy(donor / name, run / ("prior-epoch-" + name))
    for item in retained:
        shutil.copytree(donor / "workflows" / item["workflow_id"],
                        run / "workflows" / item["workflow_id"], dirs_exist_ok=True)
    copy(Path(steering_path), run / "generation-first-user-steering.json")
    copy(Path(profile_path), run / "current-harness-manifest.json")
    write_json(run / "schedule.json", schedule)
    lineage = {"schema_version": SCHEMA, "created_at": utc_now(), "user_quotation": USER_QUOTE,
        "donor_run": str(donor), "donor_output_freeze_sha256": sha256(donor / "output-freeze.json"),
        "donor_input_freeze_sha256": sha256(donor / "freeze.json"),
        "retained_workflows": retained, "new_workflow_ids": pending,
        "retained_complete": 75, "retained_failed": 6, "new_main_workflows": 63, "new_fixed_r1_reviews": 48,
        "paused_methods": ["skillflow"], "semantic_scoring_paused": True,
        "target_resampling": False, "other_user_process_controlled": False,
        "transport_epoch_changed": True, "old_delivery_equivalence_proved": False,
        "production_scope": "Only archived production snapshot is verified. Live semantic source may evolve independently and is never executed by this direct-only allowlist. Frozen experiment utilities and rendered core inputs remain verified.",
        "unchanged": ["source", "direct core prompts", "review core prompts", "runtime model/effort/provider",
                      "full delivery envelope", "fixed schedule", "limits", "six workers", "receipt/global-stop policy"],
        "accounting": "Imported successes and failures retain original response IDs and unknown usages; count no imported request as a new launch.",
        "inference_limit": "New prospective transport epoch; no completed same-epoch three-method comparison is claimed."}
    write_json(run / "remaining-output-lineage.json", lineage, immutable=True)
    plan = read(donor / "plan.json")
    plan.update(created_at=utc_now(), scope=SCHEMA, inherited_completed_workflows=75,
                inherited_failed_workflows=6, new_planned_workflows=111,
                continuation_manifest_sha256=sha256(run / "remaining-output-lineage.json"),
                semantic_scoring_paused=True)
    write_json(run / "plan.json", plan)
    implementation = {**old["implementation"], MODULE: sha256(base.ROOT / MODULE),
                      TRANSPORT_MODULE: sha256(base.ROOT / TRANSPORT_MODULE)}
    write_json(run / "freeze.json", {"schema_version": SCHEMA, "files": tree_hashes(run),
        "implementation": implementation, "reference_and_scores_enter_target_inputs": False}, immutable=True)
    verify(run)
    return summary(run)


def verify(run_dir, *, generation=True):
    run = Path(run_dir).resolve()
    seal, plan, lineage = read(run / "freeze.json"), read(run / "plan.json"), read(run / "remaining-output-lineage.json")
    require(seal.get("schema_version") == SCHEMA and plan.get("scope") == SCHEMA,
            "Unexpected remaining-output epoch")
    base.verify_files(run, seal["files"])
    base.verify_files(base.ROOT, seal["implementation"])
    verify_archived_production(run)
    base._amendment(read(run / "user-amendment.json"))
    require(sha256(run / "remaining-output-lineage.json") == plan["continuation_manifest_sha256"],
            "The prospective lineage changed")
    rows = base.planned(run)
    imported = {x["workflow_id"] for x in lineage["retained_workflows"]}
    pending = set(lineage["new_workflow_ids"])
    require(len(imported) == 81 and len(pending) == 111 and not imported & pending
            and {x["workflow_id"] for x in rows} == imported | pending
            and all(x["method"] in {"audit", "chain"} for x in rows),
            "The fixed direct-only allowlist changed")
    manifest = read(run / "current-harness-manifest.json")
    require(manifest["runtime"] == transport.EXPECTED
            and manifest["executable_sha256"] == transport.PINNED_EXECUTABLE_SHA256
            and sha256(manifest["executable"]) == transport.PINNED_EXECUTABLE_SHA256,
            "The prospective runtime or executable changed")
    require(not generation or not (run / "output-freeze.json").exists(), "Output generation is permanently closed")
    return manifest


def injected(function, **dependencies):
    """Rebind explicit experiment dependencies, never mutate frozen globals."""
    namespace = {**function.__globals__, **dependencies}
    value = FunctionType(function.__code__, namespace, function.__name__, function.__defaults__, function.__closure__)
    value.__kwdefaults__ = function.__kwdefaults__
    return value


class RemainingClient(base.ExploratoryClient):
    complete = injected(base.ExploratoryClient.complete, verify_run=verify, cli=transport)


run_workflow = injected(base.run_workflow, verify_run=verify, ExploratoryClient=RemainingClient)


def summary(run_dir):
    run = Path(run_dir).resolve()
    result = base.summary(run)
    lineage = read(run / "remaining-output-lineage.json")
    imported = {x["workflow_id"] for x in lineage["retained_workflows"]}
    result.update(schema_version=SCHEMA, planned_denominator=192, planned_main_denominator=144,
        planned_review_denominator=48, inherited_completed_outputs=75, inherited_failed_outputs=6,
        new_planned_workflows=111, semantic_scoring_paused=True, paused_method="skillflow",
        new_actual_cli_starts=sum((p / "cli/process-start.json").is_file()
            and read(p / "cli/process-start.json").get("actual_cli_process_started") is True
            for wid in lineage["new_workflow_ids"] for p in base.requests(run, wid)),
        new_closed_workflows=sum(x["workflow_id"] not in imported and x["status"] != "not_generated"
                                 for x in result["outcomes"]))
    return result


def run_batch(run_dir):
    run = Path(run_dir).resolve()
    verify(run)
    allowed = set(read(run / "remaining-output-lineage.json")["new_workflow_ids"])
    def guarded(directory, workflow_id):
        require(workflow_id in allowed and base.planned(directory, workflow_id)["method"] in {"audit", "chain"},
                "Only previously unlaunched direct identities may dispatch")
        return run_workflow(directory, workflow_id)
    engine = injected(base.run_batch, verify_run=verify, summary=summary)
    return engine(run, workers=6, runner=guarded)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "verify", "summary", "run-batch"))
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--donor-dir")
    parser.add_argument("--steering")
    parser.add_argument("--profile")
    args = parser.parse_args()
    if args.command == "prepare":
        value = prepare(args.run_dir, args.donor_dir, args.steering, args.profile)
    elif args.command == "verify":
        verify(args.run_dir)
        value = {"status": "verified", "target_calls": 0}
    elif args.command == "run-batch":
        value = run_batch(args.run_dir)
    else:
        value = summary(args.run_dir)
    print(json.dumps({k: v for k, v in value.items() if k not in {"outcomes", "usage"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
