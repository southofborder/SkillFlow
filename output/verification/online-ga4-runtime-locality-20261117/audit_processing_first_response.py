"""Passive a001 response/correction snapshot; no project imports or validators."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from audit_processing_material_v12 import ROOT, VERIFY, RUN, compact, expand, read, sha, unique


def response_value(raw):
    value = json.loads(raw, object_pairs_hook=unique) if isinstance(raw, str) else raw
    if value.get("format") != "skillflow-processing-json-v1":
        return value, {"shared": False, "definition_count": 0}
    definitions, seen = value["shared_values"], set()

    def visit(item):
        if isinstance(item, list):
            return [visit(child) for child in item]
        if not isinstance(item, dict):
            return item
        if set(item) == {"$ref"}:
            name = item["$ref"]
            assert name not in seen
            seen.add(name)
            result = visit(definitions[name])
            seen.remove(name)
            return result
        if set(item) == {"$literal_object"}:
            return unique((key, visit(child)) for key, child in item["$literal_object"])
        return {key: visit(child) for key, child in item.items()}

    return visit(value["payload"]), {"shared": True, "definition_count": len(definitions),
        "root_key_order": list(value), "raw_compact_wire_chars": len(compact(value))}


def walk(value, path=""):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, path + "/" + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + "/" + str(index))


def prompt_payload(prompt):
    marker = "\nPROCESSING_INPUT_JSON\n"
    start = prompt.index(marker) + len(marker)
    envelope, length = json.JSONDecoder(object_pairs_hook=unique).raw_decode(prompt[start:])
    value = expand(envelope["display"])
    assert sha(compact(value).encode()) == envelope["logical_sha256"]
    return value, length


def main():
    step = RUN / "steps/processing"
    raw = read(step / "calls/a001/response.json")
    candidate, wire = response_value(raw)
    validation = read(step / "calls/a001/validation.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    actual = {ir["id"] for block in cfg["blocks"].values() for ir in block["instructions"]}
    irs = {ir["id"]: ir for block in cfg["blocks"].values() for ir in block["instructions"]}
    modeled = set(candidate["ir_semantics"])
    gaps = candidate.get("processing_gaps", [])
    gap_ids = {row["instruction_id"] for row in gaps if row.get("unmodeled") is True}
    operation_names = {"read", "receive", "deliver", "write", "select_part", "exclude_parts", "update_fields", "build", "compute", "filter_items", "merge", "member", "branch", "append", "call"}
    operations = [(path, item) for path, item in walk(candidate["ir_semantics"], "/ir_semantics")
        if isinstance(item, dict) and item.get("op") in operation_names]
    transfers = [(path, item) for path, item in operations if "demand_transfer" in item]
    call_contracts = [(path, item) for path, item in operations if "input_contract" in item]
    locations = candidate["locations"]
    diagnostic_rows = []
    for row in validation["diagnostics"]:
        owner = row.get("context", {}).get("record_id")
        ir = owner.rsplit("/", 1)[-1] if owner else None
        diagnostic_rows.append({"code": row["code"], "path": row["path"], "message": row["message"],
            "record_id": owner, "actual_evidences": candidate["ir_semantics"][ir].get("evidences") if ir else None,
            "opcode": irs[ir]["opcode"] if ir else None})
    correction_bytes = (step / "calls/a002/prompt.txt").read_bytes()
    correction_prompt = correction_bytes.decode()
    original_prompt = (step / "prompt.txt").read_bytes().decode()
    old_input, _ = prompt_payload(original_prompt)
    correction_input, correction_envelope_chars = prompt_payload(correction_prompt)
    correction = correction_input["correction"]
    source = lambda text: text.split("RELATED SOURCE\n", 1)[1].split("\n\nOUTPUT REQUIREMENTS\n", 1)[0]
    report = {"audit": "passive_initial_processing_response", "created_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": RUN.relative_to(ROOT).as_posix(),
        "status": validation["status"], "semantic_acceptance": "not_established",
        "bindings": {name: sha((step / path).read_bytes()) for name, path in {
            "raw_response_file_sha256": "calls/a001/response.json", "validation_file_sha256": "calls/a001/validation.json",
            "correction_prompt_sha256": "calls/a002/prompt.txt"}.items()},
        "response_size": {"model_text_chars": len(raw) if isinstance(raw, str) else None,
            "response_json_file_bytes": (step / "calls/a001/response.json").stat().st_size,
            "expanded_compact_payload_chars": len(compact(candidate)), **wire},
        "coverage_claims": {"actual_ir_count": len(actual), "modeled_count": len(modeled),
            "unmodeled_count": len(gap_ids), "overlap": sorted(modeled & gap_ids),
            "missing": sorted(actual - modeled - gap_ids), "unexpected": sorted((modeled | gap_ids) - actual),
            "processing_gap_count": len(gaps), "unmodeled_records": [row for row in gaps if row.get("unmodeled") is True],
            "processing_gaps": gaps},
        "diagnostics": diagnostic_rows, "diagnostic_counts": dict(Counter(row["code"] for row in validation["diagnostics"])),
        "authored_operations": {"op_counts": dict(Counter(item["op"] for _, item in operations)),
            "demand_transfer_count": len(transfers), "tool_input_contract_count": len(call_contracts),
            "transfer_rule_count": sum(len(item["demand_transfer"].get("rules", [])) for _, item in transfers),
            "transfer_rules_with_nonempty_output_path": sum(bool(rule.get("output", {}).get("path"))
                for _, item in transfers for rule in item["demand_transfer"].get("rules", [])),
            "transfer_output_properties": dict(Counter(rule.get("output", {}).get("property")
                for _, item in transfers for rule in item["demand_transfer"].get("rules", []))),
            "demand_transfers": [{"path": path, "contract": item["demand_transfer"]} for path, item in transfers],
            "tool_input_contracts": [{"path": path, "contract": item["input_contract"]} for path, item in call_contracts]},
        "locations": {"count": len(locations),
            "address_kinds": dict(Counter(item.get("address_kind", "identified(default)") for item in locations.values())),
            "declarations": locations},
        "correction": {"stage_prompt_chars": len(correction_prompt), "stage_prompt_utf8_bytes": len(correction_bytes),
            "input_envelope_chars": correction_envelope_chars, "expanded_input_chars": len(compact(correction_input)),
            "context_fields": list(correction), "instructions": {key: value for key, value in correction.items() if key not in {"candidate", "diagnostics", "current_records", "record_catalog"}},
            "candidate_equals_expanded_first_response": correction.get("candidate") == candidate,
            "original_inputs_unchanged": {key: correction_input[key] for key in old_input} == old_input,
            "complete_source_unchanged": source(correction_prompt) == source(original_prompt),
            "diagnostics_equal_saved": correction.get("diagnostics") == validation["diagnostics"],
            "diagnostic_count": len(correction.get("diagnostics", []))},
        "limits": ["Raw output and saved validation are preserved; this report does not accept the rejected candidate.",
            "Counts describe authored records in a structurally invalid response, not propagated or reviewed coverage.",
            "Only saved JSON and display encodings were parsed; no project stage/compiler/backend/Skill/model/replay was invoked."]}
    (VERIFY / "processing-a001-response-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(compact({"response_size": report["response_size"], "coverage_claims": {key: value for key, value in report["coverage_claims"].items() if key not in {"unmodeled_records", "processing_gaps"}},
        "diagnostic_counts": report["diagnostic_counts"], "operation_counts": report["authored_operations"]["op_counts"],
        "transfers": len(transfers), "call_contracts": len(call_contracts), "address_kinds": report["locations"]["address_kinds"],
        "correction": report["correction"]}))


if __name__ == "__main__":
    main()
