"""Passive final saved-JSON inventory only: no project or stage imports."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-cfg-recovery-high-20261117-135205"


def read(path):
    return json.loads((RUN / path).read_text(encoding="utf-8"))


def ops(record):
    for event_index, event in enumerate(record.get("events", [])):
        for op_index, op in enumerate(event.get("atomic_ops", [])):
            yield event_index, op_index, op


def main():
    propagation = read("propagation/manifest.json")
    records = read("propagation/records.json")
    support = read("doe/audit/demand-support.json")
    doe = read("doe/doe-result.json")
    review = read("audit/input-contract-review.json")
    selection = read("selection.json")
    first = json.loads((OUT / "initial-cfg-source-audit.json").read_text(encoding="utf-8"))
    boundary = {}
    for family in ("remote_sites", "save_sites", "filesystem_sites"):
        boundary[family] = []
        for site in first[family]:
            ids = [row["instruction_id"] for row in site["cfg_records"]]
            actions = []
            for iid in ids:
                for ei, oi, op in ops(records.get(iid, {})):
                    if op.get("endpoints") or op.get("op") in ("write", "read"):
                        actions.append({"instruction_id": iid, "event_index": ei, "op_index": oi,
                                        "op": op["op"], "endpoints": op.get("endpoints", []),
                                        "inputs": op.get("inputs", []), "outputs": op.get("outputs", []),
                                        "alternative_count": len(op.get("alternatives", []))})
            boundary[family].append({"file": site["file"], "line": site["line"], "ir_ids": ids,
                                    "coverage": {iid: propagation["coverage"][iid] for iid in ids},
                                    "actions": actions})
    assessments = support["input_assessments"]
    inventory = review["review_core"]["inventory"]
    files = ["result.json", "selection.json", "controller-finished.json", "replay-check.json",
             "graph/initial.json", "annotation/manifest.json", "annotation/audit/compiled-response.json",
             "propagation/manifest.json", "propagation/records.json", "doe/doe-result.json",
             "doe/audit/demand-support.json", "audit/input-contract-review.json", "review/result.json",
             "audit/shared-repair-decision.json"]
    report = {
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "run": str(RUN.relative_to(ROOT)).replace("\\", "/"),
        "method": "Read-only standard-library parsing/counting/hashing of final saved JSON; no validation, compiler, backend, replay, model, Skill or tests.",
        "artifact_sha256": {p: hashlib.sha256((RUN / p).read_bytes()).hexdigest() for p in files},
        "selection": selection,
        "selection_file_hash_matches": {key: hashlib.sha256((RUN / item["path"]).read_bytes()).hexdigest() == item["sha256"] for key, item in selection.items()},
        "result": read("result.json"),
        "propagation": {"status": propagation["status"], "counts": dict(collections.Counter(propagation["coverage"].values())),
                        "unmodeled": [iid for iid, status in propagation["coverage"].items() if status == "unmodeled"],
                        "blocked": [iid for iid, status in propagation["coverage"].items() if status == "blocked"],
                        "diagnostics": propagation["diagnostics"], "record_count": len(records)},
        "source_boundaries": boundary,
        "review": {"status": review["review_status"], "source_review_complete": review["source_review_complete"],
                   "obligations": len(inventory["obligations"]), "obligation_kinds": dict(collections.Counter(row["kind"] for row in inventory["obligations"])),
                   "scope_count": sum(len(row["scopes"]) for row in inventory["contracts"]),
                   "scope_kinds": dict(collections.Counter(scope["kind"] for row in inventory["contracts"] for scope in row["scopes"])),
                   "accepted_checks": len(review["checks"]), "scope_decisions": len(review["review_core"]["scope_decisions"])},
        "demand": {"status": support["status"], "assessment_count": len(assessments),
                   "node_kinds": dict(collections.Counter(row["node_kind"] for row in assessments)),
                   "assessment_coverage": dict(collections.Counter(row["coverage"] for row in assessments)),
                   "range_statuses": dict(collections.Counter(item["status"] for row in assessments for item in row["ranges"])),
                   "range_statuses_by_node": {kind: dict(collections.Counter(item["status"] for row in assessments if row["node_kind"] == kind for item in row["ranges"])) for kind in ("op_input", "ir_input", "acquisition_output")},
                   "non_null_modifications": sum(item.get("modification") is not None for row in assessments for item in row["ranges"]),
                   "diagnostic_codes": dict(collections.Counter(row["code"] for row in support["diagnostics"])),
                   "unavailable_contract_ir_count": len({row["instruction_id"] for row in support["diagnostics"] if row["code"] == "input_contract_unavailable"}),
                   "input_findings": support["input_findings"],
                   "requirement_statuses": dict(collections.Counter(row["status"] for row in support["coverage"]["requirements"].values())),
                   "actual_child_output_gaps_ir285": [row for row in support["diagnostics"] if row.get("instruction_id") == "ir_285"]},
        "doe": {"status": doe["status"], "coverage": doe["coverage"], "sink_count": len(doe["sinks"]),
                "sinks_with_actual_payload": sum(bool(row["actual_payload"]) for row in doe["sinks"]),
                "comparison_conclusions": dict(collections.Counter(item["conclusion"] for row in doe["sinks"] for item in row["data_reviews"])),
                "diagnostic_codes": dict(collections.Counter(row["code"] for row in doe["diagnostics"])),
                "constraints": doe["constraints"]},
        "limits": ["Processed source-site operations are abstract records, not actual Skill execution or verified source-complete dependency coverage.",
                   "Remote endpoints name the service statically; they do not establish source client/credential receiver identity.",
                   "No source contract checks were accepted; required rows remain diagnostic results conditional on the generated mapping and deterministic relationships.",
                   "Range entry counts are not counts of unique fields; a field can recur across goals, properties, versions and scopes."]
    }
    with (OUT / "final-backend-source-audit.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"propagation": report["propagation"]["counts"], "assessment_ranges": report["demand"]["range_statuses"], "comparisons": report["doe"]["comparison_conclusions"], "selection_hash_matches": report["selection_file_hash_matches"]}))


if __name__ == "__main__":
    main()
