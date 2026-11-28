"""Passive current review input and task-mapping inventory; no project execution."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from audit_processing_material_v12 import ROOT, VERIFY, RUN, compact, expand, read, sha, unique


def main():
    owner = RUN / "review"
    material = read(owner / "inputs.json")
    prompt_bytes = (owner / "prompt.txt").read_bytes()
    prompt = prompt_bytes.decode()
    start = prompt.index("\nINPUT_JSON\n") + len("\nINPUT_JSON\n")
    encoded, length = json.JSONDecoder(object_pairs_hook=unique).raw_decode(prompt[start:])
    payload = expand(encoded) if encoded.get("format") == "skillflow-review-display-v1" else encoded
    checks = {}
    snapshot = read(RUN / "source/inputs/snapshot.json")
    frozen_files = {"skill/" + row["path"]: (RUN / "source/inputs/package" / row["path"]).read_bytes().decode("utf-8") for row in snapshot["files"]}
    checks["source_file_table_matches_current_frozen_bytes"] = material["files"] == frozen_files
    for key in ("task", "observations", "runtime_contract", "stage_failures", "availability", "processing_gaps", "partial", "fragments", "failed_stage_targets"):
        checks[key] = payload[key] == material[key]
    annotation = deepcopy(material["annotation"])
    annotation.pop("_fragment_origins", None)
    checks["annotation_without_duplicate_origins"] = payload["annotation"] == annotation
    cfg = deepcopy(material["cfg"])
    cfg.pop("declared_context_keys", None)
    for block in cfg["blocks"].values():
        block.pop("block_id", None)
        if block.get("data_source_kind") is None:
            block.pop("data_source_kind", None)
        if not block.get("constraints"):
            block.pop("constraints", None)
        for ir in block["instructions"]:
            ir.pop("draft_instruction_id", None)
            for direction in ("inputs", "outputs"):
                for operand in ir.get(direction, []):
                    if direction == "inputs" or operand.get("semantic_name") == operand.get("identifier"):
                        operand.pop("semantic_name", None)
                    if operand.get("type") != "literal":
                        operand.pop("literal_value", None)
            metadata = ir.get("metadata", {})
            code = metadata.get("script_content")
            if isinstance(code, str) and code and any(code in text for text in material["files"].values()):
                metadata.pop("script_content")
            for name in ("inputs", "outputs", "constraints", "metadata"):
                if not ir.get(name):
                    ir.pop(name, None)
    if not cfg.get("constraints"):
        cfg.pop("constraints", None)
    checks["cfg_exact_display_projection"] = payload["cfg"] == cfg
    inventory = material["input_contract_inventory"]
    layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
    expected_inventory = {"available": inventory["available"], "obligations": [{
        "id": row["id"], "kind": row["kind"], "contract_id": row["contract_id"],
        "target_id": material["input_contract_obligation_targets"][row["id"]],
        "attachment": row["attachment"], "input_count": row["input_count"], "scopes": layouts[row["id"]]["scopes"]}
        for row in inventory["obligations"]], "projections": [{key: row[key] for key in (
            "id", "contract_ids", "request", "response", "capability_index")} for row in inventory["projections"]]}
    checks["all_obligations_contract_ids_targets_and_scopes"] = payload["input_contract_inventory"] == expected_inventory
    source_parts = ["File navigation (not proof of semantic coverage):"]
    source_parts += [f"- {name} ({len(text.splitlines(keepends=True))} physical lines)" for name, text in material["files"].items()]
    for name, text in material["files"].items():
        lines = text.splitlines(keepends=True)
        source_parts.append(f"\nSOURCE {name}:1-{len(lines)}\n" + "".join(f"{index}: {line}" for index, line in enumerate(lines, 1)))
    source = "\n".join(source_parts)
    checks["complete_source_suffix"] = prompt.split("\nCOMPLETE SOURCE\n", 1)[1] == source
    assert all(checks.values()), checks
    mapping = read(RUN / "steps/task-correspondence/value.json")
    compiled = read(RUN / "annotation/audit/compiled-response.json")
    cfg_pointer = next(f"/blocks/{block_id}/instructions/{index}" for block_id, block in material["cfg"]["blocks"].items()
        for index, ir in enumerate(block["instructions"]) if ir["id"] == "ir_001")
    ir001 = {"cfg_visible": any(ir["id"] == "ir_001" for block in payload["cfg"]["blocks"].values() for ir in block["instructions"]),
        "modeled_annotation_present": "ir_001" in payload["annotation"]["ir_semantics"],
        "processing_gaps": [row for row in payload["processing_gaps"] if row.get("instruction_id") == "ir_001"],
        "annotation_validation_gaps": [row for row in payload["annotation"].get("_validation_gaps", []) if row.get("instruction_id") == "ir_001"],
        "cfg_instruction_pointer": cfg_pointer,
        "raw_cfg_instruction_target": [row for row in material["target_index"] if row.get("domain") == "cfg" and row.get("pointer") == cfg_pointer],
        "raw_annotation_record_target": [row for row in material["target_index"] if row.get("domain") == "annotation" and row.get("pointer") == "/ir_semantics/ir_001"],
        "failed_stage_target_inventory": payload["failed_stage_targets"]}
    def demands_summary(rows):
        return {"count": len(rows), "nonempty_path_count": sum(bool(row.get("path")) for row in rows),
            "preserve_counts": dict(Counter(row.get("preserve") for row in rows)),
            "requirements": sorted({row["requirement_id"] for row in rows}), "rows": rows}
    report = {"audit": "passive_review_input_runtime_v12", "created_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": RUN.relative_to(ROOT).as_posix(), "review_status": "running_at_snapshot",
        "bindings": {"prompt_sha256": sha(prompt_bytes), "inputs_sha256": sha((owner / "inputs.json").read_bytes()),
            "mapping_value_sha256": sha((RUN / "steps/task-correspondence/value.json").read_bytes())},
        "identity_checks": checks,
        "presentation": {"prompt_chars": len(prompt), "prompt_utf8_bytes": len(prompt_bytes),
            "encoded_json_chars": length, "expanded_payload_chars": len(compact(payload)),
            "same_prompt_literal_payload_chars": len(prompt)-length+len(compact(payload)),
            "complete_source_files": len(material["files"]), "complete_source_chars": len(source),
            "logical_payload_keys": list(payload), "runtime_version": payload["runtime_contract"]["version"]},
        "contract_inventory": {"obligations": len(inventory["obligations"]), "contract_layouts": len(layouts),
            "obligation_kinds": dict(Counter(row["kind"] for row in inventory["obligations"])),
            "missing_contract_obligations": [row["id"] for row in inventory["obligations"] if row["contract_id"] is None],
            "distinct_contract_ids": len({row["contract_id"] for row in inventory["obligations"] if row["contract_id"]}),
            "scope_count": sum(len(row["scopes"]) for row in layouts.values()),
            "scope_kinds": dict(Counter(scope["kind"] for row in layouts.values() for scope in row["scopes"])),
            "acquisition_projections": len(inventory["projections"])},
        "assembly": {"partial": material["partial"], "availability": material["availability"],
            "modeled_ir": len(annotation["ir_semantics"]), "processing_gap_count": len(payload["processing_gaps"]),
            "validation_gap_count": sum(row.get("origin") == "validation" for row in payload["processing_gaps"]),
            "compiled_top_keys": list(compiled),
            "compiled_realization_statuses": dict(Counter(row.get("status") for row in compiled.get("realizations", []))),
            "realizations": len(mapping["realizations"]), "realization_gap_counts": {row["requirement_id"]: len(row.get("gaps", [])) for row in mapping["realizations"]}},
        "task_mapping": {"demands": demands_summary(mapping.get("demands", [])),
            "operation_demands": demands_summary([{**demand, "instruction_id": group["instruction_id"],
                "operation_path": group["operation_path"]} for group in mapping.get("operation_demands", []) for demand in group["demands"]]),
            "operation_demand_group_count": len(mapping.get("operation_demands", [])),
            "realization_records": mapping["realizations"]},
        "ir001_visibility": ir001,
        "limits": ["Counts describe the actual review input and current assembly, not accepted review checks or propagated input necessity.",
            "All contract bodies remain in the exact annotation; the compact inventory retains complete scope descriptors and every obligation identity.",
            "CFG normalization and duplicated-origin omission are display rules, not raw artifact equality.",
            "No project stages, semantic validators, compiler, backend, model, Skill or replay were invoked."]}
    (VERIFY / "source-review-input-v12-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(compact({"presentation": report["presentation"], "contract_inventory": report["contract_inventory"],
        "assembly": report["assembly"], "task_demands": {key: {name: value for name, value in entry.items() if name != "rows"} for key, entry in report["task_mapping"].items() if key in {"demands", "operation_demands"}},
        "ir001_visibility": ir001}))


if __name__ == "__main__":
    main()
