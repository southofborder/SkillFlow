"""Passive saved-byte inventory; no SkillFlow imports or stage execution."""
import collections
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-cfg-recovery-high-20261117-135205"
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads((RUN / path).read_text(encoding="utf-8"))


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


def main():
    result = read("steps/processing/result.json")
    value = read("steps/processing/value.json")
    candidate = read("steps/processing/calls/a002/merged-candidate.json")
    graph = read("graph/initial.json")["cfg"]
    instructions = {
        row["id"]: (block_id, row)
        for block_id, block in graph["blocks"].items()
        for row in block["instructions"]
    }
    ops = list(operations(value["ir_semantics"], "/ir_semantics"))
    transfers = [(path, row["demand_transfer"]) for path, row in ops if "demand_transfer" in row]
    interfaces = [(path, row["input_contract"]) for path, row in ops if "input_contract" in row]
    initial_audit = json.loads((OUT / "initial-cfg-source-audit.json").read_text(encoding="utf-8"))
    physical = {}
    for family in ("remote_sites", "save_sites", "filesystem_sites"):
        physical[family] = [{
            "file": site["file"], "line": site["line"],
            "ir_ids": [row["instruction_id"] for row in site["cfg_records"]],
            "all_records_retained": all(row["instruction_id"] in value["ir_semantics"] for row in site["cfg_records"]),
        } for site in initial_audit[family]]
    artifacts = [
        "steps/processing/result.json", "steps/processing/value.json",
        "steps/processing/calls/a001/response.json", "steps/processing/calls/a001/validation.json",
        "steps/processing/calls/a002/response.json", "steps/processing/calls/a002/merged-candidate.json",
        "steps/processing/calls/a002/validation.json", "graph/initial.json",
    ]
    selected = ["ir_202", "ir_209", "ir_216", "ir_223", "ir_230", "ir_239", "ir_248"]
    data = {
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "run": str(RUN.relative_to(ROOT)).replace("\\", "/"),
        "status": "provisional_passive_partial_processing_inventory_before_source_review",
        "method": "Only standard-library JSON, text and hash inspection of this fresh run; no project imports, validators, compiler, backend, model, Skill, replay or tests.",
        "artifact_sha256": {path: hashlib.sha256((RUN / path).read_bytes()).hexdigest() for path in artifacts},
        "saved_step_result": result,
        "counts": {
            "cfg_ir": len(instructions), "candidate_ir_semantics": len(candidate["ir_semantics"]),
            "retained_ir_semantics": len(value["ir_semantics"]), "locations": len(value["locations"]),
            "retained_with_segments": sum(bool(row.get("segments")) for row in value["ir_semantics"].values()),
            "retained_without_segments": sum(not row.get("segments") for row in value["ir_semantics"].values()),
            "source_unmodeled_records": sum(bool(row.get("unmodeled")) for row in value["processing_gaps"]),
            "other_source_gap_records": sum(not row.get("unmodeled") for row in value["processing_gaps"]),
            "validation_isolated_records": len(result["validation_gaps"]),
            "atomic_operations": len(ops), "operation_kinds": dict(collections.Counter(row["op"] for _, row in ops)),
            "demand_transfer_contracts": len(transfers),
            "demand_transfer_rules": sum(len(contract.get("rules", [])) for _, contract in transfers),
            "demand_transfer_gap_rows": sum(len(contract.get("gaps", [])) for _, contract in transfers),
            "transfer_input_rows": sum(len(rule.get("inputs", [])) for _, contract in transfers for rule in contract.get("rules", [])),
            "input_contracts": len(interfaces),
            "interface_input_rows": sum(len(contract.get("inputs", [])) for _, contract in interfaces),
        },
        "unrepresented_ir": sorted(set(instructions) - set(value["ir_semantics"])),
        "source_gaps": value["processing_gaps"],
        "transfer_output_selectors": dict(collections.Counter(json.dumps(rule.get("output"), sort_keys=True) for _, contract in transfers for rule in contract.get("rules", []))),
        "compute_without_demand_transfer": [{"path": path, "has_expression": "expression" in row} for path, row in ops if row["op"] == "compute" and "demand_transfer" not in row],
        "source_site_record_presence": physical,
        "seven_collapsed_remote_processing": {iid: value["ir_semantics"][iid] for iid in selected},
        "remote_locations": {key: value["locations"][key] for key in ("getGa", "property", "gaRealtime", "gaMetadata")},
        "direct_cfg_consumers_of_result_001": [iid for iid, (_, row) in instructions.items() if any(item.get("identifier") == "result_001" for item in row.get("inputs", []))],
        "ir346_quarantined_case_names": [row["name"] for row in candidate["ir_semantics"]["ir_346"]["segments"][0]["cases"]],
        "ir346_rejected_operation": candidate["ir_semantics"]["ir_346"]["segments"][0]["cases"][0]["segments"][0]["ops"][9],
        "limits": [
            "Retained records are not accepted semantic contracts; source review has not certified this snapshot.",
            "Physical source-site presence is not propagation reach, exact dependency coverage, DOE or field deletability.",
            "No backend dependency closure was executed to estimate quarantine effects.",
            "Rule and input-row counts are syntactic inventory, not source-review scope counts.",
        ],
    }
    (OUT / "partial-processing-audit.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"report": "partial-processing-audit.json", "counts": data["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
