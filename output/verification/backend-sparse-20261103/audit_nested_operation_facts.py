"""Untimed, offline-only export of the fixed tiny nested-receiver fixture."""
from __future__ import annotations

import argparse
from copy import deepcopy
import inspect
import json
import os
from pathlib import Path

from compare_small_propagation import (
    HERE, canonical, fact_check, file_sha, new_output, offline_only,
    save_new, select_source, sha, source_identity,
)


CASE = "nested_receiver_pairs"


def export(args):
    output = new_output(args.output)
    receipt_path = Path(args.receipt).resolve()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    selected = select_source(receipt["implementation"]["source_directory"])
    before = source_identity(selected)
    if before != receipt["implementation"]:
        raise ValueError("The selected frozen source differs from its original receipt")
    input_path = Path(receipt["input"])
    if input_path.resolve() != HERE / "small-propagation-v1-input.json":
        raise ValueError("Only the already prepared tiny input is authorized")
    if file_sha(input_path) != receipt["input_sha256"]:
        raise ValueError("The fixed tiny input differs from its original receipt")
    prepared = json.loads(input_path.read_text(encoding="utf-8"))
    if prepared["schema_version"] != "authored-propagation-micro-input-v1":
        raise ValueError("Unexpected tiny input schema")
    from skillflow.propagation.solver import propagate
    if not Path(inspect.getfile(propagate)).resolve().is_relative_to(selected):
        raise ValueError("Propagation was imported outside the selected source")
    item = prepared["cases"][CASE]
    result = propagate(deepcopy(item["cfg"]), deepcopy(item["payload"]))
    checked = fact_check(CASE, result)
    for original in receipt["cases"][CASE]:
        for key in ("data_sha256", "operation_facts_sha256", "coverage", "receiver_payload_pairs"):
            if canonical(checked[key]) != canonical(original["fact_check"][key]):
                raise ValueError("Untimed export differs from original receipt: " + key)
    records = result.records.records_dict()
    facts = {identity: {key: row[key] for key in ("order", "precedence", "events")}
             for identity, row in records.items()}
    value = {
        "schema_version": "untimed-tiny-operation-facts-audit-v1",
        "policy": {"offline_derived": True, "case": CASE, "propagation_evaluations": 1,
                   "timed_sample": False, "full_doe": False, "model_calls": 0,
                   "historical_replay": False, "execute_skill": False},
        "python_hash_seed": os.environ.get("PYTHONHASHSEED", "unset: interpreter-selected seed"),
        "original_receipt": str(receipt_path), "original_receipt_sha256": file_sha(receipt_path),
        "input_sha256": file_sha(input_path), "implementation": before,
        "normalization": "The exact fact_check projection: IR identity -> order, precedence, events; canonical object keys, preserved list order.",
        "fact_check": checked, "operation_facts": facts,
        "registry": result.registry.to_dict(),
        "source_unchanged": source_identity(selected) == before,
    }
    if not value["source_unchanged"] or not checked["passed"]:
        raise ValueError("The source changed or the tiny fact check failed")
    save_new(output, value)
    print(canonical({"output": str(output), "fact_check": checked}))


def differences(before, after, path=""):
    if type(before) is not type(after):
        return [{"path": path, "baseline": before, "current": after}]
    if isinstance(before, dict):
        rows = []
        for key in sorted(before.keys() | after.keys()):
            child = path + "/" + key.replace("~", "~0").replace("/", "~1")
            if key not in before or key not in after:
                rows.append({"path": child, "baseline_present": key in before,
                             "current_present": key in after,
                             "baseline": before.get(key), "current": after.get(key)})
            else:
                rows.extend(differences(before[key], after[key], child))
        return rows
    if isinstance(before, list):
        if len(before) != len(after):
            return [{"path": path, "baseline": before, "current": after}]
        return [row for index, (left, right) in enumerate(zip(before, after))
                for row in differences(left, right, path + "/" + str(index))]
    return [] if before == after else [{"path": path, "baseline": before, "current": after}]


def compare(args):
    output = new_output(args.output)
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    current = json.loads(Path(args.current).read_text(encoding="utf-8"))
    before, after = baseline["operation_facts"], current["operation_facts"]
    delta = differences(before, after)
    def normalized(value):
        if isinstance(value, dict):
            return {key: sorted((normalized(row) for row in item), key=canonical)
                    if key == "alternatives" else normalized(item) for key, item in value.items()}
        if isinstance(value, list):
            return [normalized(item) for item in value]
        return value
    before_normalized, after_normalized = normalized(before), normalized(after)
    before_rows = before["ir_rows"]["events"][0]["atomic_ops"][0]["alternatives"]
    after_rows = after["ir_rows"]["events"][0]["atomic_ops"][0]["alternatives"]
    swapped = deepcopy(after)
    swapped["ir_rows"]["events"][0]["atomic_ops"][0]["alternatives"] = list(reversed(after_rows))
    value = {"schema_version": "untimed-tiny-operation-facts-diff-v1",
        "baseline_export_sha256": file_sha(args.baseline),
        "current_export_sha256": file_sha(args.current),
        "input_equal": baseline["input_sha256"] == current["input_sha256"],
        "data_equal": baseline["registry"] == current["registry"],
        "coverage_equal": baseline["fact_check"]["coverage"] == current["fact_check"]["coverage"],
        "receiver_payload_pairs_equal": baseline["fact_check"]["receiver_payload_pairs"] == current["fact_check"]["receiver_payload_pairs"],
        "baseline_operation_facts_sha256": sha(before), "current_operation_facts_sha256": sha(after),
        "normalization": "Sort only complete operation alternatives by canonical JSON, without deduplication. Preserve every event, atomic operation, input/output slot, member, precedence and other list order.",
        "normalized_baseline_operation_facts_sha256": sha(before_normalized),
        "normalized_current_operation_facts_sha256": sha(after_normalized),
        "normalized_operation_facts_equal": before_normalized == after_normalized,
        "ir_rows_alternatives_are_exact_reverse": before_rows == list(reversed(after_rows)),
        "reversing_only_ir_rows_alternatives_recovers_exact_baseline": swapped == before,
        "ir_rows_baseline_alternative_hash_order": [sha(row) for row in before_rows],
        "ir_rows_current_alternative_hash_order": [sha(row) for row in after_rows],
        "ir_rows_baseline_input_order": [row["inputs"] for row in before_rows],
        "ir_rows_current_input_order": [row["inputs"] for row in after_rows],
        "changed_ir": sorted(identity for identity in before.keys() | after.keys()
                             if before.get(identity) != after.get(identity)),
        "difference_count": len(delta), "differences": delta}
    save_new(output, value)
    print(canonical(value))


def check_seeds(args):
    output = new_output(args.output)
    paths = [Path(args.initial), Path(args.seed_one), Path(args.seed_two)]
    exports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if [row.get("python_hash_seed") for row in exports[1:]] != ["1", "2"]:
        raise ValueError("Expected the separate seed 1 and seed 2 exports")
    value = {
        "scope": "Untimed fixed tiny nested-receiver fixture, frozen current-r2 only",
        "exports": [{"path": str(path.resolve()), "sha256": file_sha(path),
                     "python_hash_seed": row.get("python_hash_seed", "not recorded in the initial export"),
                     "data_sha256": row["fact_check"]["data_sha256"],
                     "operation_facts_sha256": row["fact_check"]["operation_facts_sha256"]}
                    for path, row in zip(paths, exports)],
        "raw_operation_facts_equal": all(row["operation_facts"] == exports[0]["operation_facts"] for row in exports),
        "raw_registry_equal": all(row["registry"] == exports[0]["registry"] for row in exports),
        "original_timing_receipt_unchanged": all(file_sha(row["original_receipt"]) == row["original_receipt_sha256"] for row in exports),
        "scope_limit": "Two explicit hash seeds plus the original untimed export; this is not exhaustive replay determinism evidence for all inputs.",
    }
    save_new(output, value)
    print(canonical(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("export")
    command.add_argument("--receipt", required=True)
    command.add_argument("--output", required=True)
    command = commands.add_parser("compare")
    command.add_argument("--baseline", required=True)
    command.add_argument("--current", required=True)
    command.add_argument("--output", required=True)
    command = commands.add_parser("check-seeds")
    command.add_argument("--initial", required=True)
    command.add_argument("--seed-one", required=True)
    command.add_argument("--seed-two", required=True)
    command.add_argument("--output", required=True)
    args = parser.parse_args()
    offline_only()
    {"export": export, "compare": compare, "check-seeds": check_seeds}[args.command](args)


if __name__ == "__main__":
    main()
