"""Inspect closed-run JSON and source text only; no SkillFlow/Skill execution."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
VERIFY = OUT.parent
RUN = ROOT / "experiments/doe/runs/document-guided-010-interface-r4-high-20261104-173522"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


graph = read(RUN / "graph/initial.json")["cfg"]
wire = read(RUN / "annotation/audit/wire-annotation.json")
compiled = read(RUN / "annotation/audit/compiled-response.json")
records = read(RUN / "propagation/records.json")
data = {v["id"]: v for v in read(RUN / "propagation/data.json")}
manifest = read(RUN / "propagation/manifest.json")
doe = read(RUN / "doe/doe-result.json")
instructions = {i["id"]: i for b in graph["blocks"].values() for i in b["instructions"]}
source_case = next(v for v in read(VERIFY / "source-audit/small-cases/source-packages.json")["cases"] if v["case"] == "010")
source_checks = []
for item in source_case["files"]:
    path = RUN / "source/inputs/package" / item["path"]
    actual = digest(path)
    source_checks.append({**item, "actual_sha256": actual, "matches": actual == item["sha256"],
        "lines": {str(i): line for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)}})
assert all(v["matches"] for v in source_checks)

artifact_names = ["selection.json", "result.json", "graph/initial.json", "annotation/audit/wire-annotation.json",
    "annotation/audit/compiled-response.json", "propagation/manifest.json", "propagation/data.json",
    "propagation/records.json", "propagation/sinks.json", "doe/doe-result.json", "doe/audit/demand-support.json",
    "review/result.json", "steps/task-correspondence/prompt.txt", "steps/task-correspondence/value.json",
    "steps/task-correspondence/calls/a001/validation.json", "steps/graph/calls/a001/validation.json",
    "steps/graph/calls/a002/validation.json", "steps/sensitivity/value.json", "replay-check.json", "implementation-check.json"]
hashes = {p: digest(RUN / p) for p in artifact_names}


def op(ir, event):
    return records[ir]["events"][event]["atomic_ops"][0]


def recorded_fields(identifier, seen=()):
    """Unwrap stored composition descriptors; do not evaluate instructions/expressions."""
    assert identifier not in seen, identifier
    return descriptor_fields(data[identifier]["content"], seen + (identifier,))


def descriptor_fields(content, seen):
    form = content["form"]
    if form == "known_parts":
        assert content["parts_complete"]
        assert all(len(v["path"]) == 1 for v in content["parts"])
        return {v["path"][0]: v["data"] for v in content["parts"]}
    if form == "field_updates":
        result = recorded_fields(content["base"], seen)
        assert all(len(v["path"]) == 1 for v in content["updates"])
        return {**result, **{v["path"][0]: v["data"] for v in content["updates"]}}
    if form == "selection":
        assert content["path"] == []
        return recorded_fields(content["base"], seen)
    if form == "loop_summary":
        assert len(content["variants"]) == 1
        return descriptor_fields(content["variants"][0]["content"], seen)
    raise AssertionError((form, content))


request_root = op("ir_001", 0)["outputs"][0][0]
term = op("ir_003", 1)["outputs"][0][0]
date = op("ir_006", 1)["outputs"][0][0]
limit = op("ir_010", 1)["outputs"][0][0]
for item, path in [(term, ["term"]), (date, ["from_date"]), (limit, ["limit"])]:
    assert data[item]["origin"]["part_of"] == request_root
    assert data[item]["origin"]["path"] == path

send, receive = op("ir_014", 0), op("ir_014", 1)
assert send["inputs"] == receive["inputs"]
assert send["endpoints"] == receive["endpoints"]
compiled_call_ops = [v for e in compiled["ir_semantics"]["ir_014"]["events"] for v in e.get("atomic_ops", [])]
assert compiled_call_ops[0]["request_id"] == compiled_call_ops[1]["request_id"]
send_by_input = {v["inputs"][0][0]: v for v in send["alternatives"]}
total_by_response = {v["inputs"][0][0]: v for v in op("ir_016", 1)["alternatives"]}
items_by_response = {v["inputs"][0][0]: v for v in op("ir_018", 1)["alternatives"]}
write = op("ir_017", 0)
write_by_total = {v["inputs"][0][0]: v for v in write["alternatives"]}
return_ids = next(v["data_ids"] for v in records["ir_019"]["entry_state"]["bindings"] if v["location"]["name"] == "result_010")
variants = []
for alternate in receive["alternatives"]:
    request = alternate["inputs"][0][0]
    response = alternate["outputs"][0][0]
    fields = recorded_fields(request)
    has_date = alternate["bindings"]["predecessor:block_004"] == "block_003"
    has_limit = alternate["bindings"]["predecessor:block_006"] == "block_005"
    expected = {"query": term}
    if has_date:
        expected["from_date"] = date
    if has_limit:
        expected["limit"] = limit
    assert fields == expected
    assert alternate["bindings"] == send_by_input[request]["bindings"]
    total_alt, items_alt = total_by_response[response], items_by_response[response]
    total_value, items_value = total_alt["outputs"][0][0], items_alt["outputs"][0][0]
    assert alternate["bindings"] == total_alt["bindings"] == items_alt["bindings"] == write_by_total[total_value]["bindings"]
    assert items_value in return_ids
    for value, field in [(total_value, "total"), (items_value, "items")]:
        selection = data[value]["content"]["variants"][0]["content"]
        assert selection == {"form": "selection", "base": response, "path": [field]}
    variants.append({"from_date_present": has_date, "limit_present": has_limit,
        "request_data_id": request, "recorded_fields": fields, "response_data_id": response,
        "total_data_id_written": total_value, "items_data_id_returned": items_value,
        "matching_bindings": alternate["bindings"], "checks": {
            "exact_expected_argument_fields": True, "original_field_versions_preserved": True,
            "send_receive_request_and_bindings_match": True,
            "total_and_items_from_same_response": True, "write_retains_total_binding": True,
            "return_retains_items_identity": True}})
assert len(variants) == 4
assert {(v["from_date_present"], v["limit_present"]) for v in variants} == {(False, False), (False, True), (True, False), (True, True)}
assert set(return_ids) == set(op("ir_018", 1)["outputs"][0])
assert set(write["inputs"][0]) == set(op("ir_016", 1)["outputs"][0])
assert instructions["ir_017"]["outputs"] == [] and write["outputs"] == []
assert records["ir_019"]["events"] == []

prompt_lines = (RUN / "steps/task-correspondence/prompt.txt").read_text(encoding="utf-8").splitlines()
references_index = prompt_lines.index("EXISTING EXPRESSION REFERENCES (program-generated from processing)")
references = json.loads(prompt_lines[references_index + 1])
conditions = [v["condition"] for realization in wire["realizations"] for v in realization.get("constraints", []) if "condition" in v]
assert len(conditions) == 2
assert all(v in [r["target"] for r in references] for v in conditions)
compiled_conditions = [v["condition"] for realization in compiled["realizations"] for v in realization.get("constraints", []) if "condition" in v]
assert all(v in [e["target"] for e in compiled["expressions"]] for v in compiled_conditions)
all_ops = [(ir, ei, oi, v) for ir, r in records.items() for ei, e in enumerate(r["events"]) for oi, v in enumerate(e["atomic_ops"])]
nonmodel_receivers = [{"instruction_id": ir, "event_index": ei, "op_index": oi, "op": v["op"], "endpoints": v["endpoints"]}
    for ir, ei, oi, v in all_ops if v["op"] in ("deliver", "write") and any(e["kind"] != "model_context" for e in v["endpoints"])]
assert len(nonmodel_receivers) == 2

evidence = {
    "identity": "catalog-query-interface-r4-source-audit-v1", "created_at": datetime.now(timezone.utc).isoformat(),
    "reviewer": "/root/audit_paused_registry_v9", "run": RUN.relative_to(ROOT).as_posix(),
    "method": "Frozen-source and saved-JSON inspection with standard library only. Unwrap recorded object composition and compare saved IDs/bindings; do not evaluate SkillFlow instructions or expressions. No production import, loader, solver, model, replay, Skill execution, process control or active-run inspection.",
    "criteria": "output/verification/online-interface-r4-20261104/source-audit/small-cases/correctness-checklist.json",
    "source_checks": source_checks, "original_artifact_sha256": hashes,
    "selection": read(RUN / "selection.json"), "result": read(RUN / "result.json"),
    "counts": {"source_files": len(source_checks), "blocks": len(graph["blocks"]), "ir": len(instructions),
        "coverage": dict(Counter(manifest["coverage"].values())), "propagation_diagnostics": len(manifest["diagnostics"]),
        "processing_gaps": len(wire.get("processing_gaps", [])), "data_records": len(data),
        "call_positions": 1, "paired_request_response_alternatives": len(variants),
        "count_write_positions": 1, "return_positions": 1, "model_observe_positions": sum(any(e["kind"] == "model_context" for e in v["endpoints"]) for _, _, _, v in all_ops),
        "sensitivity_declarations": len(read(RUN / "steps/sensitivity/value.json")["declarations"]),
        "doe_sinks": len(doe["sinks"]), "doe_data_reviews": sum(len(v["data_reviews"]) for v in doe["sinks"])},
    "source_field_origins": {"request": request_root, "term": data[term], "from_date": data[date], "limit": data[limit]},
    "four_optional_combinations": sorted(variants, key=lambda v: (v["from_date_present"], v["limit_present"])),
    "missing_vs_null": "Presence predicates are present(field(request,...)), independent of field truthiness. Included values reuse the original selected field Data IDs; missing branches lack those argument keys. No null replacement is introduced. No concrete request/null value was supplied or executed, so this is a representation/identity finding, not a runtime null experiment or date-format proof.",
    "compiled_call_request_id": compiled_call_ops[0]["request_id"],
    "nonmodel_receivers": nonmodel_receivers,
    "write": {"cfg": instructions["ir_017"], "wire": wire["ir_semantics"]["ir_017"], "record": records["ir_017"],
        "note": "Source leaves write mode unspecified; replace is the declared runtime abstraction. No append request, fabricated public whole-file output, count calculation or conversion is introduced."},
    "return": {"cfg": instructions["ir_019"], "record": records["ir_019"],
        "note": "No extra user/caller delivery sink is invented; the ordinary return retains its actual input under the shared contract."},
    "expression_reference_checks": {"prompt_line": references_index + 1, "supplied_references": references,
        "wire_conditions": conditions, "compiled_conditions": compiled_conditions,
        "compiled_expressions": compiled["expressions"], "wire_targets_exactly_match_supplied_references": True,
        "compiled_targets_match_real_expressions": True,
        "mapping_validation": read(RUN / "steps/task-correspondence/calls/a001/validation.json")},
    "graph_correction": {"initial": read(RUN / "steps/graph/calls/a001/validation.json"), "corrected": read(RUN / "steps/graph/calls/a002/validation.json"),
        "note": "The sole graph correction supplied the search-response dependency to a guarded dispatch. It is separate from mapping-reference validation."},
    "doe": {"status": doe["status"], "coverage": doe["coverage"], "diagnostics": doe["diagnostics"], "constraints": doe["constraints"],
        "note": "See independent-doe-review.json for requirement-specific scope, receiver demand resolution and interpretation limits."},
    "review": read(RUN / "review/result.json"),
    "four_fix_behavior": [
        {"id": "optional_case_body", "assessment": "not_exercised", "reason": "This 010 processing has no cases segment with omitted segments; successful 010 processing does not exercise the GA4-specific optional-body path."},
        {"id": "write_output_relation", "assessment": "supported_for_ordinary_write; explicit_append_not_exercised", "reason": "ir_017 uses replace, has no CFG/public output and no recorded output. The actual count state changes and later items return remain. The explicit terminal-append case belongs to 013."},
        {"id": "condition_references", "assessment": "supported_interface_behavior; constraint_satisfaction_mixed", "reason": "Both supplied self-slot references are copied exactly, normalized to existing compiled expression targets, and accepted on the first mapping attempt. The separate only_if checks report potential_violation; reference validity is not proof of satisfaction."},
        {"id": "review_owner", "assessment": "routing_not_exercised", "reason": "Final review has no findings and no semantic repair. Thus no wrong-owner finding appears, but this run does not exercise ownership routing or its repair behavior. R8 remains a task-correspondence realization gap; zero sensitivity declarations are separate."},
    ],
    "all_saved_data": list(data.values()), "selected_records": records,
    "limits": ["One single-call CFG position with four alternatives is not four actual index.search calls.",
        "No concrete input content, service response, runtime call success, date validity or unknown sensitive category was established.",
        "Static model-observation boundaries are contract-supplied possibilities, not measured observations or automatically user-facing deliveries.",
        "Zero declared sensitivity and zero data reviews do not establish nonsensitivity, safety, minimization or absence of DOE.",
        "Replay matching and review_passed establish neither semantic equivalence nor complete requirement satisfaction."],
}
assert hashes == {p: digest(RUN / p) for p in artifact_names}
evidence["original_artifacts_unchanged_during_extraction"] = True
(OUT / "source-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(evidence["counts"]))
