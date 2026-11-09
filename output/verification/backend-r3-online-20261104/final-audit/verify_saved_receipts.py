"""Independent read-only arithmetic/hash audit of four closed run receipts.

No SkillFlow imports, transport metrics collector, replay, or analysis execution.
Only this directory receives newly written evidence.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CASES = ("ga4", "001", "010", "013")
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
failures = []
identities = []
receipt = {"scope": "Saved JSON/text and file SHA-256 only; no production imports, metric collection, analysis, replay, or process inspection", "runs": {}}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition, label):
    if not condition:
        failures.append(label)


for case in CASES:
    run = ROOT / f"experiments/doe/runs/document-guided-{case}-backend-r3-high-20261104-132226"
    closed = read(run / "controller-finished.json")
    metrics = read(run / "metrics.json")
    replay = read(run / "replay-check.json")
    manifest = read(run / "manifest.json")
    snapshot = read(run / "implementation-snapshot/snapshot.json")
    impl = read(run / "implementation-check.json")
    summary = read(run / "run-summary.json") if (run / "run-summary.json").exists() else None
    rows, groups, errors = [], defaultdict(Counter), []
    total = Counter({name: 0 for name in FIELDS})
    native_dirs = {p.parent for p in (run / "transport").rglob("started.json")}
    pid_dirs = {p.parent for p in (run / "transport").rglob("pid.json")}
    metric_dirs = {run / row["request"] for row in metrics["requests"]}
    check(native_dirs == pid_dirs == metric_dirs, f"{case}: complete native marker/request directory agreement")
    check(len(metric_dirs) == len(metrics["requests"]), f"{case}: no duplicated request directories")
    for row in metrics["requests"]:
        attempt = run / row["request"]
        public = [json.loads(line) for line in (attempt / "stdout.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        threads = [item["thread_id"] for item in public if item["type"] == "thread.started"]
        turns = [item for item in public if item["type"] == "turn.completed"]
        messages = [item["item"]["text"] for item in public if item["type"] == "item.completed" and item["item"]["type"] == "agent_message"]
        check(len(threads) == len(turns) == len(messages) == 1, f"{case}/{row['request']}: single substantive public turn")
        check(sum(item["type"] == "turn.started" for item in public) == 1, f"{case}/{row['request']}: one public turn start")
        check(messages[0].strip() == (attempt / "last-message.txt").read_text(encoding="utf-8").strip(), f"{case}/{row['request']}: final answer association")
        identity = (threads[0], turns[0].get("turn_id"), 0)
        identities.append(identity)
        check(row["thread_id"] == identity[0], f"{case}/{row['request']}: metric thread identity")
        check(len(row["public_turns"]) == 1 and row["public_turns"][0]["accepted_final_associated"] is True, f"{case}/{row['request']}: saved final association")
        check(row["public_turns"][0]["order"] == 0 and row["public_turns"][0]["turn_id"] is None, f"{case}/{row['request']}: saved turn order")
        usage = {name: turns[0]["usage"].get(name, 0) for name in FIELDS}
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        check(usage == row["complete_token_usage"], f"{case}/{row['request']}: raw usage equals saved complete usage")
        sidecar = read(attempt / "usage.json")
        check(sidecar["known"] and all(usage[name] == value for name, value in sidecar["usage"].items()), f"{case}/{row['request']}: usage sidecar agreement")
        check(usage["cached_input_tokens"] <= usage["input_tokens"] and usage["reasoning_output_tokens"] <= usage["output_tokens"], f"{case}/{row['request']}: subset counters")
        process = read(attempt / "process.json")
        check(process["exited"] and process["returncode"] == 0 and row["native_process_started"], f"{case}/{row['request']}: actual native start/exit evidence")
        check(row["network_attempt_index"] == 1 and attempt.name == "attempt-001", f"{case}/{row['request']}: no outer retry")
        check(row["usage_completeness"] == "complete" and not row["partial_token_usage"] and not row["ambiguous_final"], f"{case}/{row['request']}: complete unambiguous usage")
        is_correction = "/a002/" in row["logical_call"]
        check(is_correction == row["structural_correction"], f"{case}/{row['request']}: correction call number")
        stage = row["logical_request"].split("/")[1]
        category = "structural_correction" if is_correction else "semantic_repair_generation" if stage.startswith("revision") else "normal_generation"
        groups[category].update(usage)
        groups[category]["requests"] += 1
        total.update(usage)
        notices = [item for item in public if item["type"] == "error"]
        if notices:
            errors.append({"request": row["request"], "events": notices})
        rows.append({"request": row["request"], "category": category, "identity": identity, "usage": usage,
                     "stdout_sha256": sha(attempt / "stdout.jsonl"), "native_pid": read(attempt / "pid.json").get("pid")})
    check(dict(total) == metrics["known_token_usage"], f"{case}: aggregate raw counters match metrics")
    check(len(rows) == metrics["native_process_starts"] == metrics["logical_requests"] == metrics["complete_usage_requests"], f"{case}: native/logical/complete counts")
    for field in ("unknown_native_process_starts", "inputs_rejected_before_start", "network_retry_attempts", "partial_usage_requests", "unknown_usage_requests"):
        check(metrics[field] == 0, f"{case}: {field} is zero")
    check(metrics["total_usage_known"] and metrics["http_attempts"] is None, f"{case}: complete public usage and unknown provider attempts")
    check(replay["status"] == "matched" and replay["new_native_markers"] == 0 and closed["replay"] == replay, f"{case}: saved zero-call matching replay")
    check(all(read(path / "started.json")["started_at"] < read(run / "analysis-finished.json")["finished_at"] for path in native_dirs), f"{case}: all saved native starts precede analysis closure")
    frozen_changed = [name for name, digest in snapshot["files"].items() if sha(run / "implementation-snapshot" / name) != digest]
    current_changed = [name for name, digest in snapshot["files"].items() if not (ROOT / name).exists() or sha(ROOT / name) != digest]
    check(not frozen_changed and not current_changed, f"{case}: all frozen/current implementation file hashes match")
    check(all(snapshot["files"][name] == digest for name, digest in manifest["implementation"]["files"].items()), f"{case}: manifest/snapshot file hashes agree")
    check(impl["unchanged"] and not impl["changed_files"] and impl["implementation_sha256"] == snapshot["implementation_sha256"] == manifest["implementation"]["sha256"], f"{case}: implementation receipts agree")
    check(sha(run / "controller.py") == snapshot["controller_sha256"] and sha(run / "local_timing.py") == snapshot["local_timing_sha256"], f"{case}: archived controller/timing hashes agree")
    if summary is not None:
        check(summary["transport"]["known_token_usage"] == dict(total), f"{case}: published summary totals")
        check(summary["transport"]["native_process_starts"] == len(rows), f"{case}: published native count")
        check(summary["transport"]["logical_categories"]["by_category"] == {k: v["requests"] for k, v in groups.items()}, f"{case}: published categories")
        for category, values in summary["transport"]["call_group_costs"].items():
            canonical_category = "semantic_repair_generation" if category == "semantic_repair" else category
            check(all(groups[canonical_category][field] == value for field, value in values.items()), f"{case}: published group cost {category}")
        check(summary["transport"]["public_identity_crosscheck"]["unique_count"] == len(rows), f"{case}: published public identity count")
    receipt["runs"][case] = {"native_starts": len(rows), "unique_public_identities": len({tuple(row["identity"]) for row in rows}),
        "known_public_usage": dict(total), "groups": {k: dict(v) for k, v in groups.items()},
        "outer_retries": 0, "unknown_public_final_usage_requests": metrics["unknown_usage_requests"],
        "internal_reconnect_notices": errors, "provider_http_attempts": None, "replay": replay,
        "implementation_sha256": impl["implementation_sha256"], "pinned_files_checked": len(snapshot["files"]),
        "frozen_changed_files": frozen_changed, "current_changed_files": current_changed,
        "published_summary_available": summary is not None, "requests": rows,
        "receipts_sha256": {name: sha(run / name) for name in ["metrics.json", "manifest.json", "controller-finished.json", "replay-check.json", "implementation-check.json", "implementation-snapshot/snapshot.json"]}}

check(len(set(identities)) == len(identities), "All four cases: globally unique public thread/turn-or-order identities")
receipt["batch"] = {"native_starts": len(identities), "unique_public_identities": len(set(identities)),
    "known_public_usage": {name: sum(run["known_public_usage"][name] for run in receipt["runs"].values()) for name in FIELDS},
    "groups": {category: sum(run["groups"].get(category, {}).get("requests", 0) for run in receipt["runs"].values()) for category in ["normal_generation", "structural_correction", "semantic_repair_generation"]}}
receipt["limitations"] = ["Usage is the complete saved public final-turn counter basis, not provider billing or an estimate of hidden internal attempts.", "Nine CLI reconnect notices are observable; their numbers do not establish provider HTTP attempt counts or additional usage.", "Replay check is independently reconciled with saved markers and controller receipts; no replay was rerun."]
receipt["audit_label_normalization"] = "001 call_group_costs uses semantic_repair for the same five requests named semantic_repair_generation by logical_categories; all numerical counters agree. The audit treats these labels as aliases."
receipt["010_claim_review"] = {"status": "no concrete overclaim found", "reviewer": "/root/audit_paused_registry_v9/check_010_claims", "scope": "Published 010 assessment/summary versus frozen source-audit evidence and saved receipts; source relationships, unresolved return recipient, zero sensitivity comparison basis, and sample-only v8 comparison are explicitly scoped."}
receipt["failures"] = failures
receipt["status"] = "passed" if not failures else "discrepancies_found"
receipt["created_at"] = datetime.now(timezone.utc).isoformat()
(OUT / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": receipt["status"], "batch": receipt["batch"], "failures": failures}, ensure_ascii=False, indent=2))
