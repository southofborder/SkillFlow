"""Zero-model dispatcher completion metadata; no semantic answer evaluation."""
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path("D:/projects/SkillFlow")
sys.path.insert(0, str(REPO))
from tools.doe.direct_baseline import TOKEN_FIELDS, verify
from tools.doe.direct_experiment import effective_schedule, write_once

RUN = REPO / "experiments/doe/runs/direct-baseline-v1-20261019-171200"
schedule = effective_schedule(RUN)
heldout = schedule["heldout"]
active = schedule["pilot"] + heldout
decisions = {
    trial_id: json.loads((RUN / "trials" / trial_id / "decision.json").read_text(encoding="utf-8"))
    for trial_id in active
}
assert len(heldout) == 96 and len(active) == len(set(active)) == 120
assert all(d["completed"] for d in decisions.values())
checkpoint = json.loads((RUN / "dispatch/heldout-checkpoints/096-096.json").read_text(encoding="utf-8"))
assert checkpoint["start_order_matches_schedule"]
assert checkpoint["started_trial_ids"] == heldout
assert not checkpoint["started_not_imported"]

def summarize(ids):
    rows = [decisions[trial_id] for trial_id in ids]
    responses = {}
    conflicts = []
    for d in rows:
        for response_id, usage in d["usage"]["by_response_id"].items():
            if response_id in responses and responses[response_id] != usage:
                conflicts.append(response_id)
            responses.setdefault(response_id, usage)
    times = [d["timing"] for d in rows]
    durations = [t.get("duration_ms") for t in times]
    starts = [t.get("started_at") for t in times]
    ends = [t.get("completed_at") for t in times]
    return {
        "planned_calls": len(ids),
        "imported_trials": len(rows),
        "completed_trials": sum(d["completed"] for d in rows),
        "protocol_status_counts": dict(Counter(d["protocol_status"] for d in rows)),
        "configuration_verified_count": sum(d["configuration_verified"] for d in rows),
        "tool_call_count": sum(len(d["tools"]) for d in rows),
        "violation_count": sum(len(d["violations"]) for d in rows),
        "unique_response_count": len(responses),
        "usage_conflict_response_ids": sorted(set(conflicts)),
        "usage_totals": {
            field: sum(u[field] for u in responses.values())
            if responses and all(u[field] is not None for u in responses.values()) else None
            for field in TOKEN_FIELDS
        },
        "trials_with_unknown_usage": [d["trial_id"] for d in rows if not d["usage"]["response_count"]],
        "timing": {
            "sum_target_duration_ms": sum(durations) if all(t is not None for t in durations) else None,
            "first_target_started_at": min(starts) if all(t is not None for t in starts) else None,
            "last_target_completed_at": max(ends) if all(t is not None for t in ends) else None,
            "wall_span_seconds": max(ends) - min(starts) if all(t is not None for t in starts + ends) else None,
        },
        "prompt_delivery_audit_status_counts": dict(Counter(d["prompt_delivery_audit"]["status"] for d in rows)),
        "trial_ids": ids,
        "monetary_cost": None,
    }

replay = verify(RUN, sessions_dir=Path("C:/Users/24831/.codex/sessions"))
write_once(RUN / "dispatch/heldout-replay.json", replay)
assert replay["verified"], replay["errors"]
assert replay["receipt_replay_count"] == 120
completion = {
    "stage": "heldout",
    **summarize(heldout),
    "main_calls": sum(not trial_id.endswith("_review") for trial_id in heldout),
    "review_calls": sum(trial_id.endswith("_review") for trial_id in heldout),
    "start_order_matches_schedule": True,
    "zero_model_replay": replay,
    "overall_active_experiment": summarize(active),
    "prompt_revision_budget_remaining": 0,
    "semantic_scoring_performed_by_dispatcher": False,
}
write_once(RUN / "dispatch/heldout-completion.json", completion)
print(json.dumps({key: value for key, value in completion.items() if key not in ("trial_ids", "overall_active_experiment")}))
