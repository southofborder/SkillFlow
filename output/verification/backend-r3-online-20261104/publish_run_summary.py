"""Publish JSON-only closed-run assessments; never imports or executes SkillFlow."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

VERIFY = Path(__file__).resolve().parent
ROOT = VERIFY.parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def publish(case):
    run = ROOT / "experiments/doe/runs" / f"document-guided-{case}-backend-r3-high-20261104-132226"
    if not (run / "controller-finished.json").is_file():
        raise ValueError("Only closed results may be assessed")
    summary = read(run / "mechanical-evidence.json")
    spec = read(VERIFY / "case-assessments.json")[case]
    summary.update({
        "schema_version": "backend-r3-online-assessment-v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "kind": "independent_closed_run_assessment",
        "assessment": spec,
        "source_assessment": "Independent assistant source/artifact assessment, not human gold; see assessment and linked evidence.",
        "implementation_check": read(run / "implementation-check.json"),
        "runtime": {"model": "gpt-6.1-sol", "reasoning_effort": "high", "provider": "openai", "workers": 2},
        "normal_semantic_request_budget": 7,
        "report": str(run / "assessment.en.md"),
    })
    source = next(x for x in read(VERIFY / "prepared-runs.json")["run_order"] if x["case_id"] == case)
    summary["source"] = {k: source[k] for k in ("source_sha256", "files", "old_run")}
    metrics = read(run / "metrics.json")
    categories = defaultdict(lambda: {"requests": 0, "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    identities = []
    for row in metrics["requests"]:
        stage = row["logical_request"].split("/")[1:-1]
        category = "structural_correction" if row.get("structural_correction") else "semantic_repair" if stage[0].startswith("revision") else "normal_generation"
        categories[category]["requests"] += 1
        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "total_tokens"):
            categories[category][key] += (row.get("complete_token_usage") or {}).get(key, 0)
        for turn in row.get("public_turns", []):
            if turn.get("accepted_final_associated"):
                identities.append((row.get("thread_id"), turn.get("turn_id"), turn.get("order")))
    summary["transport"]["call_group_costs"] = dict(categories)
    summary["transport"]["public_identity_crosscheck"] = {
        "accepted_public_thread_turn_or_order_count": len(identities),
        "unique_count": len(set(identities)),
        "duplicate_count": len(identities) - len(set(identities)),
        "missing_thread_count": sum(x[0] is None for x in identities),
        "identities": identities,
        "scope": "Public thread plus turn ID/order; provider response IDs are not assumed to be exposed. Per-request complete counters were already deduplicated by saved transport metrics."
    }
    starts, intervals = {}, []
    for line in (run / "stage-events.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        stage, status = row["stage"], row["stage_state"]["status"]
        if status == "running":
            starts.setdefault(stage, row["observed_at"])
        elif stage in starts:
            begin = starts.pop(stage)
            intervals.append({"stage": stage, "status": status, "started_at": begin, "finished_at": row["observed_at"], "seconds": (datetime.fromisoformat(row["observed_at"]) - datetime.fromisoformat(begin)).total_seconds()})
    summary["timing"]["stage_intervals"] = intervals
    summary["timing"]["stage_interval_scope"] = "Observed stage transitions, including validation/correction and other local stage work. Parallel stages overlap; do not sum as wall time."
    for filename in spec.get("audit_evidence", []):
        path = ROOT / filename
        summary["evidence_sha256"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    old = read(ROOT / "output/verification/general-loops-v8-online-20261101/four-run-summary.json")
    comparison = next(x for x in old["runs"] if x["case"] == case)
    summary["comparison_v8"] = {k: comparison[k] for k in ("report", "status", "generated_ir_coverage", "source_boundary_coverage", "native_starts", "public_token_usage", "analysis_seconds", "replay")}
    summary["comparison_limit"] = "Fresh generations have different graphs and completion scope. No equivalent-work speedup, generic accuracy rate or advantage over direct GPT is inferred. Paused v9 has no terminal online result."
    (run / "run-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"case": case, "summary": str(run / "run-summary.json"), "stage_intervals": intervals, "call_group_costs": dict(categories)}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=("ga4", "001", "010", "013"))
    publish(parser.parse_args().case)
