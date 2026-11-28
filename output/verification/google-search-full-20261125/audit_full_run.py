"""Read saved google-search artifacts and summarize verified request/error evidence.

Run with the closed online directory. Pass --offline-analysis only for a separately
published computation over that same run's selected annotation. The two statuses
are always reported separately. This script does not start or replay analysis.
"""

import argparse
from collections import Counter, defaultdict, deque
from hashlib import sha256
import json
from pathlib import Path
import re


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else None


def digest(value):
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def open_ref(root, ref):
    path = (root / ref["path"]).resolve()
    if not path.is_relative_to(root) or sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
        raise ValueError("Selection reference differs from saved bytes: " + ref["path"])
    return path


def focal_instructions(cfg):
    # Physical locations in the frozen two-file google-search package.
    anchors = {6: "parameter_binding", 9: "request_construction", 14: "request",
               15: "http_status_check", 19: "cli_argv_check", 35: "cli_helper_call",
               36: "success_output", 38: "error_output", 39: "error_exit"}
    result = {}
    for block in cfg.get("blocks", {}).values():
        for instruction in block["instructions"]:
            span = instruction.get("metadata", {}).get("source_span", {})
            if span.get("file", "").replace("\\", "/").endswith("scripts/search.py"):
                result[instruction["id"]] = [name for line, name in anchors.items()
                                             if span["start_line"] <= line <= span["end_line"]]
    return result


def operation_record(records, position):
    event = records[position["instruction_id"]]["events"][position["event_index"]]
    if position.get("instance_index") is not None:
        event = event["instances"][position["instance_index"]]["body"][position["body_event_index"]]
    return event["atomic_ops"][position["op_index"]]


def demand_step(identity, item):
    node = item["node"]
    return {"ref": identity, "ir": node["instruction_id"], "kind": node["kind"],
            "slot": node["slot"], "property": item["property"], "path": item["path"],
            "rules": item["rules"], "conservative": item["conservative"]}


def demand_ancestry(index, reference):
    seen, pending, chain = set(), [reference], []
    while pending:
        identity = pending.pop()
        if identity in seen:
            continue
        seen.add(identity)
        item = index[identity]
        chain.append(demand_step(identity, item))
        pending.extend(reversed(item["parents"]))
    return chain


def input_witness(index, derived, reference, focal):
    """Follow recorded reverse-propagation steps from this boundary to the formal input."""
    seen, pending = set(), deque([(reference,)])
    while pending:
        path = pending.popleft()
        identity = path[-1]
        if identity in seen:
            continue
        seen.add(identity)
        item = index[identity]
        node = item["node"]
        if node["kind"] == "ir_input" and "parameter_binding" in focal.get(node["instruction_id"], []):
            return [demand_step(item_id, index[item_id]) for item_id in path]
        pending.extend((*path, child) for child in derived[identity])
    return []


def focal_reviews(doe, support, records, focal):
    derivations = doe["derivations"]
    demand = derivations["demand"] | support["extra_derivations"]
    sensitivity = derivations["sensitivity"]
    derived = defaultdict(list)
    for identity, item in demand.items():
        if not item["conservative"]:
            for parent in item["parents"]:
                derived[parent].append(identity)
    limits = {item["id"]: item["code"] for item in doe["diagnostics"]}
    for sink in doe["sinks"]:
        boundary = sink["boundary"]
        role = focal.get(boundary["instruction_id"], [])
        if not any(value in role for value in ("request", "error_output", "success_output")):
            continue
        payloads = {item["operation_id"]: item for item in sink["actual_payload"]}
        findings = []
        for review in sink["data_reviews"]:
            signal = sensitivity[review["derivation_id"]]
            if "key" not in signal["path"] and not re.search(r"api.?key", signal["label"], re.I):
                continue
            op_id, slot = review["operation_id"], review["input_index"]
            op = operation_record(records, payloads[op_id]["position"])
            if slot == op.get("when_input_index") or signal["data_id"] not in op["inputs"][slot]:
                raise ValueError("Saved key comparison does not match the recorded payload slot: " + review["id"])
            if review.get("reduction") and review["conclusion"] != "excess_supported":
                raise ValueError("Reduction is present on an unsupported finding: " + review["id"])
            exact_key_demands = []
            for ref in review["demand_refs"]:
                item = demand[ref]
                if (item["node"]["operation_id"], item["node"]["slot"]) != (op_id, slot):
                    raise ValueError("Included demand belongs to another operation/slot: " + ref)
                if not item["conservative"] and item["path"] == signal["path"]:
                    exact_key_demands.append({"requirement_id": item["requirement_id"],
                                              "demand_ancestry": demand_ancestry(demand, ref),
                                              "input_witness": input_witness(demand, derived, ref, focal)})
            findings.append({"comparison_id": review["id"], "operation_id": op_id, "slot": slot,
                             "version": signal["data_id"], "path": signal["path"],
                             "sensitivity_relation": signal["relation"],
                             "sensitivity_derivation": review["derivation_id"],
                             "conclusion": review["conclusion"], "reduction": review["reduction"],
                             "limitation_codes": sorted({limits[ref] for ref in review.get("limitation_refs", [])}),
                             "constraint_refs": review["constraint_refs"], "exact_demands": exact_key_demands})
        yield {"boundary": boundary, "source_roles": role, "key_comparisons": findings,
               "decision_counts": Counter(item["conclusion"] for item in sink["data_reviews"])}


def backend(root, selected_manifest, focal):
    propagation = read_json(root / "propagation/manifest.json")
    if not propagation:
        return None
    if propagation["upstream"]["manifest_sha256"] != selected_manifest["manifest_sha256"]:
        raise ValueError("Propagation was not produced from the online selection")
    result = {"propagation_status": propagation["status"],
              "coverage_counts": Counter(propagation["coverage"].values()),
              "focal_coverage": {ir: {"source_roles": roles, "status": propagation["coverage"].get(ir)}
                                 for ir, roles in focal.items() if roles},
              "doe": None}
    doe_manifest = read_json(root / "doe/manifest.json")
    if not doe_manifest:
        return result
    if doe_manifest["upstream"]["manifest_sha256"] != propagation["manifest_sha256"]:
        raise ValueError("DOE manifest belongs to another propagation run")
    doe = read_json(root / "doe/doe-result.json")
    support = read_json(root / "doe/audit/demand-support.json")
    records = read_json(root / "propagation/records.json")
    receipt = read_json(root / "doe/audit/input-contract-review.json")
    receipt_id = None if receipt is None else receipt["receipt_sha256"]
    if doe_manifest["input_contract_review_sha256"] != digest(receipt) or support["input_contract_review_sha256"] != receipt_id:
        raise ValueError("DOE and demand do not use the saved input-contract review receipt")
    if doe_manifest["result_sha256"] != digest(doe) or doe_manifest["support_sha256"] != digest(support):
        raise ValueError("Saved DOE result or demand support does not match its manifest")
    result["doe"] = {"status": doe["status"], "demand_status": support["status"],
                     "recorded_sink_count": len(doe["sinks"]),
                     "unresolved_boundaries": doe["coverage"].get("unresolved_boundaries", []),
                     "input_assessments": len(support["input_assessments"]),
                     "input_range_statuses": Counter(row["status"] for item in support["input_assessments"]
                                                     for row in item["ranges"]),
                     "decision_counts": Counter(row["conclusion"] for sink in doe["sinks"] for row in sink["data_reviews"]),
                     "review_complete": None if receipt is None else receipt["source_review_complete"],
                     "review_decisions": {} if receipt is None else Counter(row["status"] for row in receipt["checks"]),
                     "focal_boundaries": list(focal_reviews(doe, support, records, focal))}
    return result


def audit(run, offline):
    status = read_json(run / "result.json")
    result = {"run": str(run), "online": status, "selection": None,
              "selected_task_focus": None, "online_backend": None, "separate_offline_backend": None}
    if status is None or status["status"] in {"prepared", "running", "interrupted"}:
        return result
    metrics = read_json(run / "metrics.json")
    if metrics is not None:
        result["transport"] = {key: metrics[key] for key in ("native_process_starts", "known_token_usage",
                               "network_retry_attempts", "wall_clock_seconds") if key in metrics}
    selection = read_json(run / "selection.json")
    if selection is None:
        return result
    result["selection"] = selection
    paths = {key: open_ref(run, ref) for key, ref in selection.items()}
    selected_task = read_json(paths["task"])
    result["selected_task_focus"] = [row for row in selected_task["requirements"]
                                     if re.search(r"api.?key|error|exception|unsuccessful|failure|exit", row["text"], re.I)]
    result["task_issues"] = selected_task["issues"]
    cfg = read_json(paths["cfg"])
    focal = focal_instructions(cfg.get("cfg", cfg))
    manifest = read_json(paths["annotation"])
    result["online_backend"] = backend(run, manifest, focal)
    if offline:
        result["separate_offline_backend"] = backend(offline, manifest, focal)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--offline-analysis", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run.resolve(strict=True), args.offline_analysis), ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
