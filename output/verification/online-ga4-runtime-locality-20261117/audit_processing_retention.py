"""Passive comparison of saved processing answers and retained fragment."""
from collections import Counter, deque
from datetime import datetime, timezone
import json
from audit_processing_first_response import response_value, walk
from audit_processing_material_v12 import ROOT, VERIFY, RUN, read, sha, compact


def summary(value):
    operations = [(path, item) for path, item in walk(value.get("ir_semantics", {}), "/ir_semantics")
        if isinstance(item, dict) and "demand_transfer" in item and item["demand_transfer"] is not None]
    contracts = [(path, item) for path, item in walk(value.get("ir_semantics", {}), "/ir_semantics")
        if isinstance(item, dict) and item.get("input_contract") is not None]
    gaps = value.get("processing_gaps", [])
    return {"modeled_ir": len(value["ir_semantics"]), "source_gap_count": len(gaps),
        "source_unmodeled_ir": sorted({row["instruction_id"] for row in gaps if row.get("unmodeled")}),
        "demand_transfer_count": len(operations),
        "demand_transfer_rule_count": sum(len(item["demand_transfer"]["rules"]) for _, item in operations),
        "nonempty_output_selector_rules": sum(bool(rule["output"].get("path")) for _, item in operations for rule in item["demand_transfer"]["rules"]),
        "interface_input_contracts": len(contracts), "locations": len(value["locations"]),
        "address_kind_counts": dict(Counter(row.get("address_kind", "identified(default)") for row in value["locations"].values()))}


def main():
    step = RUN / "steps/processing"
    raw1, raw2 = (read(step / f"calls/{name}/response.json") for name in ("a001", "a002"))
    first, wire1 = response_value(raw1)
    second, wire2 = response_value(raw2)
    retained = read(step / "value.json")
    result = read(step / "result.json")
    validation = read(step / "calls/a002/validation.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    owners = {ir["id"]: block_id for block_id, block in cfg["blocks"].items() for ir in block["instructions"]}
    irs = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    changed = sorted(key for key in first["ir_semantics"].keys() & second["ir_semantics"].keys()
        if first["ir_semantics"][key] != second["ir_semantics"][key])
    removed = sorted(first["ir_semantics"].keys() - second["ir_semantics"].keys())
    added = sorted(second["ir_semantics"].keys() - first["ir_semantics"].keys())
    evidence_only, other = [], []
    for key in changed:
        if {k: v for k, v in first["ir_semantics"][key].items() if k != "evidences"} == {
                k: v for k, v in second["ir_semantics"][key].items() if k != "evidences"}:
            evidence_only.append(key)
        else:
            other.append(key)
    def without_evidences(value):
        if isinstance(value, dict):
            return {key: without_evidences(child) for key, child in value.items() if key != "evidences"}
        if isinstance(value, list):
            return [without_evidences(child) for child in value]
        return value
    substantive = [key for key in changed if without_evidences(first["ir_semantics"][key]) != without_evidences(second["ir_semantics"][key])]
    def changed_fields(left, right, path=""):
        if isinstance(left, dict) and isinstance(right, dict):
            rows = [{"path": path + "/" + key, "first": left.get(key), "second": right.get(key)}
                for key in sorted(left.keys() ^ right.keys())]
            for key in sorted(left.keys() & right.keys()):
                rows += changed_fields(left[key], right[key], path + "/" + key)
            return rows
        if isinstance(left, list) and isinstance(right, list) and len(left) == len(right):
            return [row for index, (a, b) in enumerate(zip(left, right)) for row in changed_fields(a, b, path + "/" + str(index))]
        return [] if left == right else [{"path": path, "first": left, "second": right}]
    # Compare every authored field, while recording typed defaults as additions.
    differences, default_additions = [], []
    def compare(source, target, path):
        if isinstance(source, dict) and isinstance(target, dict):
            default_additions.extend(path + "/" + key for key in target.keys() - source.keys())
            for key, child in source.items():
                if key not in target:
                    differences.append({"path": path + "/" + key, "change": "missing"})
                else:
                    compare(child, target[key], path + "/" + key)
        elif isinstance(source, list) and isinstance(target, list) and len(source) == len(target):
            for index, (left, right) in enumerate(zip(source, target)):
                compare(left, right, path + "/" + str(index))
        elif source != target:
            differences.append({"path": path, "change": "value", "before": source, "after": target})
    compare(second, retained, "")
    first_ir = irs["ir_001"]
    outputs = {item["identifier"] for item in first_ir["outputs"]}
    consumers = [{"instruction_id": ir["id"], "block": owners[ir["id"]], "input_index": index, "operand": operand}
        for ir in irs.values() for index, operand in enumerate(ir["inputs"])
        if operand.get("type") == "result" and operand.get("identifier") in outputs]
    following = cfg["blocks"][owners["ir_001"]]["instructions"]
    edges = cfg["edges"]
    successors = {}
    for edge in edges:
        successors.setdefault(edge["source_block_id"], set()).add(edge["target_block_id"])
    reachable, queue = set(), deque([owners["ir_001"]])
    while queue:
        block = queue.popleft()
        if block in reachable:
            continue
        reachable.add(block)
        queue.extend(successors.get(block, ()))
    report = {"audit": "passive_processing_a002_retention", "created_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": RUN.relative_to(ROOT).as_posix(), "stage_result": result, "validation": validation,
        "bindings": {name: sha((step / name).read_bytes()) for name in ("value.json", "result.json", "calls/a002/response.json", "calls/a002/validation.json")},
        "raw_a002": {"model_text_chars": len(raw2) if isinstance(raw2, str) else None,
            "saved_response_bytes": (step / "calls/a002/response.json").stat().st_size,
            "expanded_compact_chars": len(compact(second)), **wire2},
        "first_summary": summary(first), "second_summary": summary(second), "retained_summary": summary(retained),
        "answer_change": {"changed_existing_ir": changed, "changed_evidence_only_ir": evidence_only,
            "other_changed_ir": other, "removed_ir": removed, "added_ir": added,
            "ir001_identical_across_answers": first["ir_semantics"]["ir_001"] == second["ir_semantics"]["ir_001"],
            "ir001_original_record": first["ir_semantics"]["ir_001"],
            "nested_evidence_only_count": len(changed) - len(substantive),
            "changed_beyond_evidence_ir": substantive,
            "changed_beyond_evidence_fields": {key: changed_fields(without_evidences(first["ir_semantics"][key]), without_evidences(second["ir_semantics"][key])) for key in substantive},
            "locations_equal": first["locations"] == second["locations"],
            "locations_equal_without_evidence": without_evidences(first["locations"]) == without_evidences(second["locations"]),
            "gaps_equal": first.get("processing_gaps") == second.get("processing_gaps"),
            "gap_order_changed": [row["instruction_id"] for row in first.get("processing_gaps", [])] != [row["instruction_id"] for row in second.get("processing_gaps", [])],
            "gap_changes_by_ir": changed_fields({row["instruction_id"]: row for row in first.get("processing_gaps", [])},
                {row["instruction_id"]: row for row in second.get("processing_gaps", [])}),
            "other_changed_records": {key: {"first": first["ir_semantics"][key], "second": second["ir_semantics"][key]} for key in other}},
        "retention": {"authored_field_differences": differences, "typed_added_field_count": len(default_additions),
            "typed_added_field_examples": sorted(default_additions)[:30]},
        "ir001_impact": {"cfg_record": first_ir, "owner_block": owners["ir_001"],
            "entry_block": cfg["entry_block_id"], "direct_result_consumers": consumers,
            "same_block_instruction_ids": [ir["id"] for ir in following],
            "outgoing_edges": [edge for edge in edges if edge["source_block_id"] == owners["ir_001"]],
            "structurally_reachable_block_count": len(reachable),
            "structurally_reachable_ir_count": sum(len(cfg["blocks"][block]["instructions"]) for block in reachable),
            "limit": "Graph reachability is not actual propagation or evidence of a future blocked count. Source review/shared repair has not finished."},
        "limits": ["This is a partial retained fragment, not an accepted whole answer or accepted semantic contract review.",
            "No validators, compilers, backend, model, Skill or replay were invoked; only saved JSON records and graph edges were inspected."]}
    (VERIFY / "processing-a002-retention-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(compact({"raw_a002": report["raw_a002"], "retained_summary": report["retained_summary"],
        "changed_existing_ir_count": len(changed), "nested_evidence_only_count": len(changed)-len(substantive),
        "changed_beyond_evidence_count": len(substantive),
        "locations_equal_without_evidence": report["answer_change"]["locations_equal_without_evidence"],
        "gap_order_changed": report["answer_change"]["gap_order_changed"],
        "ir001_original_record": report["answer_change"]["ir001_original_record"]}))


if __name__ == "__main__":
    main()
