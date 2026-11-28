"""Passive saved-processing/source inventory for the authorized fresh descendant.

Uses only standard-library JSON/text/hash reads. Does not import SkillFlow,
execute helpers, reconstruct wire responses, validate semantics, run a Skill,
call a model, replay a stage or write inside the run. Invoke only when root asks
for a snapshot after processing settles. Each invocation creates a new report.
"""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
PREFIX = "document-guided-ga4-processing-restart-high-"
ALLOWED_STAGES = ("processing", "revision-processing")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def operations(value, path=""):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "ops" and isinstance(item, list):
                for index, operation in enumerate(item):
                    yield f"{path}/ops/{index}", operation
            else:
                yield from operations(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from operations(item, f"{path}/{index}")


def segments(value, path=""):
    if isinstance(value, dict):
        if "mode" in value or value.get("kind") in {"cases", "for_each"}:
            yield path, value
        for key, item in value.items():
            yield from segments(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from segments(item, f"{path}/{index}")


def local_refs(value, path=""):
    if isinstance(value, dict):
        if value.get("kind") == "local" and isinstance(value.get("name"), str):
            yield value["name"], path
        for key, item in value.items():
            yield from local_refs(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from local_refs(item, f"{path}/{index}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=ALLOWED_STAGES, default="processing")
    args = parser.parse_args(argv)
    prepared = read(VERIFY / "prepared-run.json")
    run = Path(prepared["run_directory"]).resolve()
    if run.parent != (PROJECT / "experiments/doe/runs").resolve() or not run.name.startswith(PREFIX):
        raise ValueError("The prepared owner is outside the sole new descendant namespace")
    owner = run / "steps" / args.stage
    required = [owner / "manifest.json", owner / "result.json", owner / "value.json"]
    if not all(path.is_file() for path in required):
        raise ValueError("No complete saved processing result/value is available for a passive snapshot")
    before = {str(path.relative_to(run)): sha(path) for path in required}
    manifest, result, value = (read(path) for path in required)
    if result.get("status") in {"running", "interrupted", "structural_failure", "semantic_failure"}:
        raise ValueError("This helper inventories retained values, not incomplete candidate answers")
    if result.get("value_file") != "value.json" or result.get("value_sha256") != sha(owner / "value.json"):
        raise ValueError("Saved selected value differs from its result reference")
    cfg_ref = manifest["context"]["cfg_path"]
    cfg_path = (owner / cfg_ref["path"]).resolve()
    if not cfg_path.is_relative_to(run) or sha(cfg_path) != cfg_ref["sha256"]:
        raise ValueError("Processing CFG does not resolve to its exact local bound bytes")
    cfg = read(cfg_path)["cfg"]
    before[str(cfg_path.relative_to(run))] = sha(cfg_path)
    protocol = read(run / "run-protocol.json")
    inheritance = read(run / "inherited-inputs.json")
    source = run / "source/inputs/package"
    source_hashes = {path.relative_to(source).as_posix(): sha(path) for path in source.rglob("*") if path.is_file()}
    if source_hashes != protocol["source_file_sha256"]:
        raise ValueError("The complete source inventory differs from the prepared owner")
    instructions = {row["id"]: row for block in cfg["blocks"].values() for row in block["instructions"]}
    semantic = value["ir_semantics"]
    ops = list(operations(semantic, "/ir_semantics"))
    transfers, interfaces, remote, acquisitions = [], [], [], []
    for path, op in ops:
        iid = path.split("/")[2]
        if "demand_transfer" in op:
            contract = op["demand_transfer"]
            rules = contract.get("rules", [])
            transfers.append({"path": path, "instruction_id": iid, "inputs": op.get("inputs", []),
                "output": op.get("output"), "output_selectors": [rule.get("output") for rule in rules],
                "whole_value_only": bool(rules) and all(rule.get("output", {}).get("property") == "value"
                    and not rule.get("output", {}).get("path") and not rule.get("output", {}).get("excluded_paths") for rule in rules),
                "rules_input_indices": [[row.get("input_index") for row in rule.get("inputs", [])] for rule in rules],
                "gap_rows": contract.get("gaps", []), "rules": rules})
        if "input_contract" in op:
            interfaces.append({"path": path, "op": op.get("op"), "location": op.get("location", op.get("target")),
                               "actual_input_count": len(op.get("inputs", [])), "contract": op["input_contract"]})
        location = value["locations"].get(op.get("location"), {})
        if op.get("op") == "call" and location.get("kind") == "remote":
            remote.append({"path": path, "instruction_id": iid, "location": location,
                           "operation": op, "cfg_inputs": instructions[iid].get("inputs", [])})
        if op.get("op") == "call" and location.get("kind") == "tool" and op.get("output"):
            refs = [{"operation": other_path, "reference_path": ref_path} for other_path, other in operations(semantic[iid])
                    for name, ref_path in local_refs(other) if name == op["output"]]
            acquisitions.append({"path": path, "location": location.get("name"), "output": op["output"],
                                 "syntactic_same_ir_local_references": refs,
                                 "notice": "Reference inventory only; equal local names in distinct case scopes are not proven dataflow."})
    cases = [{"path": path, "kind": seg.get("kind"), "mode": seg.get("mode"),
              "case_names": [row.get("name") for row in seg.get("cases", [])],
              "iterator_keys": sorted(set(seg) - {"ops", "body", "cases", "evidences"})}
             for path, seg in segments(semantic, "/ir_semantics") if seg.get("kind") in {"cases", "for_each"}]
    option_source = source / "scripts/src/api/reports.ts"
    option_lines = [{"line": number, "text": line} for number, line in enumerate(option_source.read_text(encoding="utf-8").splitlines(), 1)
                    if "filters" in line or "orderBy" in line] if option_source.is_file() else []
    source_gaps = value.get("processing_gaps", [])
    validation_gaps = result.get("validation_gaps", [])
    validation = []
    for path in sorted((owner / "calls").glob("a*/validation.json")):
        row = read(path)
        validation.append({"path": path.relative_to(run).as_posix(), "sha256": sha(path),
                           "status": row.get("status"), "diagnostics": row.get("diagnostics", [])})
    report = {
        "identity": "skillflow-passive-regenerated-processing-audit-v1",
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "run_directory": str(run),
        "stage": args.stage, "audit_helper_sha256": sha(Path(__file__)),
        "method": "Saved JSON, exact bytes, source text and syntactic inventory only; no project imports or stage/model/Skill/replay execution.",
        "source_file_count": len(source_hashes), "source_file_sha256": source_hashes,
        "selected_cfg_file": cfg_path.relative_to(run).as_posix(),
        "initial_cfg_equals_inherited_bytes": sha(run / "graph/initial.json") == inheritance["inherited_files"]["graph/initial.json"],
        "result": result, "validation_receipts": validation,
        "inventory": {"cfg_ir": len(instructions), "retained_records": len(semantic),
            "with_segments": sum(bool(row.get("segments")) for row in semantic.values()),
            "without_segments": sum(not row.get("segments") for row in semantic.values()),
            "source_unmodeled_ir": [row.get("instruction_id") for row in source_gaps if row.get("unmodeled")],
            "validation_isolated_ir": [row.get("instruction_id") for row in validation_gaps],
            "absent_semantics_ir": sorted(set(instructions) - set(semantic)),
            "operations": len(ops), "op_kinds": dict(collections.Counter(row["op"] for _, row in ops)),
            "demand_transfer_contracts": len(transfers), "whole_value_only_contracts": sum(row["whole_value_only"] for row in transfers),
            "interface_contracts": len(interfaces)},
        "demand_transfers": transfers, "interface_contracts": interfaces,
        "remote_operations_and_actual_cfg_inputs": remote,
        "local_call_output_reference_inventory": acquisitions, "case_loop_inventory": cases,
        "source_option_read_mentions": option_lines,
        "explicit_filter_order_selections": [{"path": path, "operation": op} for path, op in ops
                                              if op.get("op") == "select_part" and op.get("path") in (["filters"], ["orderBy"])],
        "source_gaps": source_gaps, "validation_gaps": validation_gaps,
        "artifact_sha256_before": before,
        "limits": ["Saved structural status is reported, not revalidated or certified as source-correct.",
                   "Whole-only contract counts describe authored output selectors, not actual task demand or semantic acceptance.",
                   "Receiver identity, control, paired members and source sufficiency require manual source inspection and the normal review.",
                   "No source-contract acceptance, deletion result, propagation reach or DOE conclusion is inferred from this inventory."]}
    after = {name: sha(run / name) for name in before}
    report["artifact_sha256_after"] = after
    report["stable_material_snapshot"] = before == after
    target = VERIFY / ("regenerated-processing-passive-" + args.stage + "-" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    with target.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"report": str(target), "stable_material_snapshot": before == after, "inventory": report["inventory"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
