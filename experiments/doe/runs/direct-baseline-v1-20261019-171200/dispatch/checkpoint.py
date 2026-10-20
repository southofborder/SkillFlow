"""Source-free dispatcher checkpoints; never read target reasoning or references."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path("D:/projects/SkillFlow")
sys.path.insert(0, str(REPO))
from tools.doe.direct_baseline import TOKEN_FIELDS, find_receipt, resolve_agent_session
from tools.doe.direct_experiment import effective_schedule, write_once

RUN = REPO / "experiments/doe/runs/direct-baseline-v1-20261019-171200"
AGENT = "/root/target_dispatch"
ROOT_SESSION = "01a15352-5503-7013-acc2-4d49afef8767"

schedule = effective_schedule(RUN)["heldout"]
receipt = find_receipt(resolve_agent_session(AGENT, root_session_id=ROOT_SESSION))
dispatches = []
for line in receipt.read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    payload = row.get("payload", {})
    if row.get("type") != "response_item" or payload.get("type") != "function_call" or payload.get("name") != "spawn_agent":
        continue
    args = json.loads(payload["arguments"])
    trial_id = args.get("task_name", "")
    prompt = RUN / "trials" / trial_id / "prompt.txt"
    if not prompt.is_file():
        continue
    message = args["message"]
    encrypted = message.startswith("gAAAAA")
    actual = None if encrypted else hashlib.sha256(message.encode("utf-8")).hexdigest()
    registered = hashlib.sha256(prompt.read_bytes()).hexdigest()
    audit = {
        "trial_id": trial_id, "dispatch_index": len(dispatches) + 1,
        "agent_path": AGENT + "/" + trial_id, "fork_turns": args.get("fork_turns"),
        "model_override": args.get("model"), "reasoning_effort_override": args.get("reasoning_effort"),
        "registered_prompt_sha256": registered, "spawn_message_sha256": actual,
        "exact_prompt_match": None if encrypted else actual == registered,
        "audit_status": "unavailable_encrypted" if encrypted else "matches" if actual == registered else "mismatch",
        "evidence_basis": "Dispatcher own spawn_agent function-call arguments only; encrypted message payload cannot prove prompt equality.",
        "call_id": payload.get("call_id"),
    }
    write_once(RUN / "dispatch" / (trial_id + ".delivery-audit.json"), audit)
    dispatches.append(trial_id)

started = [trial_id for trial_id in dispatches if trial_id in schedule]
decisions = []
for trial_id in schedule:
    path = RUN / "trials" / trial_id / "decision.json"
    if path.is_file():
        decisions.append(json.loads(path.read_text(encoding="utf-8")))
imported = {d["trial_id"] for d in decisions}
by_response = {}
conflicts = []
for decision in decisions:
    for response_id, usage in decision["usage"]["by_response_id"].items():
        if response_id in by_response and by_response[response_id] != usage:
            conflicts.append(response_id)
        by_response.setdefault(response_id, usage)

checkpoint = {
    "stage": "heldout", "scheduled_calls": len(schedule), "started_count": len(started),
    "imported_count": len(decisions), "start_order_matches_schedule": started == schedule[:len(started)],
    "started_trial_ids": started, "imported_trial_ids": [d["trial_id"] for d in decisions],
    "started_not_imported": [trial_id for trial_id in started if trial_id not in imported],
    "next_scheduled_trial": next((trial_id for trial_id in schedule if trial_id not in started), None),
    "protocol_status_counts": dict(Counter(d["protocol_status"] for d in decisions)),
    "configuration_verified_count": sum(d["configuration_verified"] for d in decisions),
    "tool_call_count": sum(len(d["tools"]) for d in decisions),
    "violation_count": sum(len(d["violations"]) for d in decisions),
    "unique_response_count": len(by_response), "usage_conflict_response_ids": sorted(set(conflicts)),
    "usage_totals": {key: sum(u[key] for u in by_response.values()) if by_response and all(u[key] is not None for u in by_response.values()) else None for key in TOKEN_FIELDS},
    "trials_with_unknown_usage": [d["trial_id"] for d in decisions if not d["usage"]["response_count"]],
    "monetary_cost": None,
}
write_once(RUN / "dispatch/heldout-checkpoints" / f"{len(started):03}-{len(decisions):03}.json", checkpoint)
print(json.dumps({key: checkpoint[key] for key in (
    "started_count", "imported_count", "next_scheduled_trial", "started_not_imported",
    "start_order_matches_schedule", "protocol_status_counts", "tool_call_count", "violation_count", "usage_totals",
)}))
