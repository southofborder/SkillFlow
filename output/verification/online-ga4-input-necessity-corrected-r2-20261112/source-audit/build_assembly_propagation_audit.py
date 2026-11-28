"""Read saved JSON only; no SkillFlow imports, validation, analysis, or replay."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[3]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (BASE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def without_attached_annotations(value):
    if isinstance(value, dict):
        return {k: without_attached_annotations(v) for k, v in value.items() if k not in {"sensitivity", "demands"}}
    if isinstance(value, list):
        return [without_attached_annotations(v) for v in value]
    return value


def walk(value, path=""):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, path + "/" + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + "/" + str(index))


def recorded_ops(record):
    return [(ei, oi, e, op) for ei, e in enumerate(record.get("events", []))
            for oi, op in enumerate(e.get("atomic_ops", []))]


def op_summary(record):
    return [{"event_index": ei, "op_index": oi, "effect": e.get("effect"), "operation": op["op"],
             "case": e.get("case"), "endpoints": op.get("endpoints", []),
             "input_slots": len(op.get("inputs", [])), "output_slots": len(op.get("outputs", [])),
             "alternative_count": len(op.get("alternatives", [])),
             "binding_keys": sorted({k for a in op.get("alternatives", []) for k in a.get("bindings", {})})}
            for ei, oi, e, op in recorded_ops(record)]


def main():
    now = datetime.now(timezone.utc).isoformat()
    processing = read(RUN / "steps/processing/value.json")
    wire = read(RUN / "annotation/audit/wire-annotation.json")
    compiled = read(RUN / "annotation/audit/compiled-response.json")
    compilation = read(RUN / "annotation/audit/compilation-map.json")
    inputs = read(RUN / "review/inputs.json")
    review = read(RUN / "review/result.json")
    receipt = read(RUN / "audit/input-contract-review.json")
    inventory = inputs["input_contract_inventory"]
    obligations = inventory["obligations"]
    contracts = compiled["input_contracts"]
    raw_changes = [ir for ir, spec in processing["ir_semantics"].items()
                   if without_attached_annotations(spec) != without_attached_annotations(wire["ir_semantics"][ir])]
    assert not raw_changes
    assert processing["processing_gaps"] == wire["processing_gaps"]
    assert len({x["id"] for x in contracts}) == len(contracts)
    assert {x["contract_id"] for x in obligations} == {x["id"] for x in contracts}
    demand_paths = [path + "/demands" for path, obj in walk(wire["ir_semantics"]) if "demands" in obj]
    contract_scopes = [s for x in inventory["contracts"] for s in x["scopes"]]
    assembly = {
        "identity": "ga4-r2-saved-assembly-review-audit-v1", "created_at": now,
        "run_directory": str(RUN), "status": "unreviewed_diagnostic_material",
        "method": "Read saved JSON and frozen implementation text only; no compiler, validator, analysis, replay, model, or Skill executed.",
        "artifacts": {f: sha(RUN / f) for f in ["annotation/audit/wire-annotation.json", "annotation/audit/raw-annotation.json",
                      "annotation/audit/compiled-response.json", "annotation/audit/compilation-map.json", "review/result.json",
                      "review/inputs.json", "audit/input-contract-review.json"]},
        "assembly": {
            "status": "partial", "reason": "runner.py:424 marks assembly partial when accepted raw_annotation has any processing_gaps; this is not a new assembly validation rejection.",
            "modeled_ir": len(compiled["ir_semantics"]), "processing_gaps": len(compiled["processing_gaps"]),
            "explicit_unmodeled_ir": [g["instruction_id"] for g in compiled["processing_gaps"] if g["unmodeled"]],
            "validation_origin_gap_count": sum(g["origin"] == "validation" for g in compiled["processing_gaps"]),
            "same_processing_gaps_as_selected_fragment": True,
            "processing_changes_excluding_sensitivity_and_demands": raw_changes,
            "operation_demand_attachments": len(demand_paths),
            "ir_with_operation_demand_attachments": len({x.split('/')[1] for x in demand_paths}),
            "operation_demand_attachment_paths": demand_paths,
            "realizations": len(compiled["realizations"]), "compiled_demands": len(compiled["demands"]),
            "compiled_expressions": len(compiled["expressions"]), "compiler_events": len(compilation["events"]),
            "constraints": len(compilation["constraints"]), "locations": len(compiled["locations"]),
            "sink_boundaries": len(compiled["sink_boundaries"]), "processing_gap_records": compiled["processing_gaps"],
        },
        "contract_inventory": {
            "available": inventory["available"], "obligations": len(obligations), "compiled_contracts": len(contracts),
            "contract_ir": len({x["instruction_id"] for x in contracts}),
            "kinds": dict(Counter(x["kind"] for x in contracts)),
            "operations": dict(Counter(x["operation"] for x in obligations)),
            "obligation_contract_id_sets_match": True,
            "scope_counts": dict(Counter(x["kind"] for x in contract_scopes)),
            "projection_rows": len(inventory["projections"]),
            "binding": inputs["input_contract_binding"],
            "obligations_by_ir": {ir: [{k: x[k] for k in ["id", "kind", "operation", "raw_pointer", "contract_id", "input_count"]}
                                      for x in obligations if x["instruction_id"] == ir]
                                  for ir in sorted({x["instruction_id"] for x in obligations})},
            "note": "92 compute contracts plus 146 deliveries and 106 receives. Each of 106 wire calls lowers to a request/response pair; 40 wire deliveries remain delivery-only. The 344 compiled entries are not 344 independent source operations.",
        },
        "review": {
            "status": review["status"], "error_type": review["error_type"], "reason": review["reason"],
            "input_characters": 1079505, "limit_characters": 1048576, "excess_characters": 30929,
            "native_process_started": False, "review_content": review["review"],
            "source_review_complete": receipt["source_review_complete"], "check_count": len(receipt["checks"]),
            "receipt_sha256": receipt["receipt_sha256"], "material_binding": {k: v for k, v in receipt.items() if k.endswith("_sha256")},
            "reviewed_contracts": 0,
            "interpretation": "Every compiled obligation lacks a completed source-review check. Structural inventory coverage does not establish sufficiency, necessity, source fidelity, or field deletability. The downstream demand engine must retain review failures; this audit does not assert its unfinished output.",
        },
    }
    write("assembly-review-audit.json", assembly)
    (BASE / "assembly-review-audit.en.md").write_text(
        "# GA4 r2 selected assembly and failed review audit\n\n"
        "The selected assembly is structurally assembled but unreviewed. Assembly `partial` is triggered by the existing 13 processing gaps; it is not a new assembly validation rejection (`runner.py:424`). It retains 561 modeled IR and two explicit unmodeled IR, `ir_419` and `ir_423`, with zero validation-origin gaps. Processing operators and contract bodies are unchanged from selected processing; assembly adds sensitivity and 40 operation-demand attachments across 38 IR. The compiled material contains 616 events, 191 demands, 9 expressions and 3 constraints.\n\n"
        "The actual inventory has 344 obligations linked one-to-one by ID to 344 compiled contracts over 209 IR: 92 compute, 146 delivery and 106 receipt obligations. The 106 wire calls expand to request/response pairs. Review scope rows comprise 252 interface, 513 required, 337 remainder, 92 rule and one unresolved-range scope. These are structural counts, not accepted semantic relationships.\n\n"
        "Unified review failed before a CLI process started: the input was 1,079,505 characters, above the 1,048,576-character limit by 30,929. The immutable receipt binds source, CFG, annotation, contracts, obligations and failed review, and explicitly records `source_review_complete:false`, `review_status:request_failure` and zero checks. None of the 344 contracts is source-reviewed. This is an input-size failure, not a connection timeout.\n\n"
        "The selected-processing source concerns remain open: all 13 API call summaries omit the actual client handle from processing operands/receiver bindings, all 25 saveResult sites use a task-retained local-tool delivery without their per-call persistent write effect, and helper summaries do not by themselves reproduce source internal reads/writes. The failed review supplied no acceptance or correction for them. See `selected-processing-audit.en.md`; no automatic repair was made.\n\n"
        "Exact bindings, identities, gaps and per-IR obligations are in `assembly-review-audit.json`. This audit reads saved artifacts only and makes no completed DOE claim.\n", encoding="utf-8")

    propagation = read(RUN / "propagation/manifest.json")
    records = read(RUN / "propagation/records.json")
    data = {x["id"]: x for x in read(RUN / "propagation/data.json")}
    sinks = read(RUN / "propagation/sinks.json")
    graph_audit = read(BASE / "selected-graph-audit.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    irs = {i["id"]: i for b in cfg["blocks"].values() for i in b["instructions"]}
    api_rows, save_rows = [], []
    for category, target in [("api_sites", api_rows), ("save_sites", save_rows)]:
        for site in graph_audit[category]:
            ir = site["representation"]["canonical_ir_id"]
            ops = op_summary(records.get(ir, {}))
            target.append({"site_id": site["site_id"], "source": site["source"], "instruction_id": ir,
                           "coverage": propagation["coverage"][ir], "record_exists": ir in records,
                           "operations": ops, "sink_records": [s for s in sinks if s["instruction_id"] == ir]})
    loops = []
    for site, prefix, child, appends in zip(graph_audit["url_loops"], ["batch", "reindex", "status"],
                                           ["ir_436", "ir_531", "ir_551"], [["ir_437"], ["ir_540"], ["ir_560"]]):
        block_rows = [{"block_id": bid, "block_name": b["block_name"],
                       "instructions": [{"id": i["id"], "opcode": i["opcode"], "coverage": propagation["coverage"][i["id"]]}
                                        for i in b["instructions"]]}
                      for bid, b in cfg["blocks"].items() if b["block_name"].startswith(prefix + "_")]
        loops.append({"site_id": site["site_id"], "source": site["source"], "blocks": block_rows,
                      "child_instruction_id": child, "child_operations": op_summary(records[child]),
                      "append_records": {ir: op_summary(records[ir]) for ir in appends},
                      "scope_evidence": "The member transfer binding appears in child alternatives; append records retain alternatives. This is finite static summary evidence, not executed iteration counts or full semantic equivalence."})
    failed_data_id = "data_f2cacc707b8c7d48ee596cb8cb82e35b079ab2339b9af78d9fe36c29141ada99"
    failure_alternative = [a for _, _, _, op in recorded_ops(records["ir_087"]) for a in op.get("alternatives", [])
                           if failed_data_id in sum(a.get("inputs", []), [])]
    propagation_audit = {
        "identity": "ga4-r2-saved-propagation-source-audit-v1", "created_at": now,
        "run_directory": str(RUN), "status": "incomplete_unreviewed_diagnostic_propagation",
        "artifact_hashes": {f: sha(RUN / f) for f in ["propagation/manifest.json", "propagation/records.json", "propagation/data.json", "propagation/sinks.json"]},
        "coverage": dict(Counter(propagation["coverage"].values())),
        "nonprocessed": {k: v for k, v in propagation["coverage"].items() if v != "processed"},
        "diagnostics": propagation["diagnostics"], "api_sites": api_rows, "save_sites": save_rows, "url_loops": loops,
        "site_counts": {"api_total": len(api_rows), "api_processed": sum(r["coverage"] == "processed" for r in api_rows),
                        "save_total": len(save_rows), "save_processed": sum(r["coverage"] == "processed" for r in save_rows),
                        "save_persistent_write_records_at_call_site": sum(any(o["operation"] == "write" for o in r["operations"]) for r in save_rows),
                        "explicit_url_loops": len(loops), "url_loop_scopes_with_all_listed_ir_processed": sum(all(i["coverage"] == "processed" for b in row["blocks"] for i in b["instructions"]) for row in loops),
                        "sink_records": len(sinks), "storage_sink_records": sum(s["sink_type"] == "storage_write" for s in sinks),
                        "network_sink_records": sum(s["sink_type"] == "network_send" for s in sinks)},
        "parse_diagnostic": {
            "instruction_id": "ir_087", "coverage": propagation["coverage"]["ir_087"],
            "source": irs["ir_087"].get("metadata", {}).get("_source_span"),
            "failed_data": data[failed_data_id], "failed_alternative": failure_alternative,
            "preceding_branch_operations": op_summary(records["ir_086"]),
            "finding": "The error-case wrapper produced by ir_085 has complete fields ok:false and error, without value. ir_086 records its false flag targeting block_042, but success-block ir_087 still receives the wrapper and selects value, producing an empty alternative and missing_part. Other alternatives succeed, so ir_087 remains counted processed. This is a generated-wrapper propagation/correlation issue, not a source access to a missing .value field.",
        },
        "semantic_limits": [
            "All 13 original API sites have request/response records; processing still omits each actual CFG client receiver binding. Source credential/client identity fidelity is not established.",
            "24 save sites have local-tool delivery records; ir_426 is blocked by ir_419. None has a persistent write record at that call site. The standalone public saver has a separate fs_write record at ir_077; that does not establish 25 per-call persistent writes.",
            "All three URL loop skeletons have member/child/append records, including bounded normal and exceptional cases. Clock fallback and protected side-effect gaps persist; propagation does not prove source-level loop semantic equivalence.",
            "The 20 selected sinks consist of one standalone storage write and 19 network sends, including six normal/exceptional loop-child sends. The 25 saveResult source sites are not 25 selected storage sinks.",
            "Processing, source coverage and contract inventory are unreviewed. No required/deletable input, DOE absence, correctness, or source-semantic completeness conclusion follows from these diagnostic records alone.",
        ],
        "execution": "Saved-artifact read only; no production changes, compiler/validator calls, model calls, Skill execution, analysis rerun, or replay.",
    }
    write("propagation-source-audit.json", propagation_audit)
    (BASE / "propagation-source-audit.en.md").write_text(
        "# GA4 r2 saved propagation source audit\n\n"
        "Diagnostic propagation is incomplete: 553 of 563 generated IR are marked processed, one (`ir_419`) is unmodeled, and nine (`ir_420` through `ir_428`) are blocked. This is generated-IR coverage over unreviewed materials, not a semantic acceptance result.\n\n"
        "All 13 original API sites have recorded request delivery and response acquisition. 24 of 25 saveResult call sites have records; the inspection save at `ir_426` is blocked. Each processed save site is a delivery to `Local saveResult`, with no persistent write operation at that site. The separately represented public saver has the one selected storage sink at `ir_077`; it cannot substitute for 25 per-call persistence records. All three explicit URL loops have processed member, child-call and append structures with occurrence bindings and bounded cases. The clock and protected side-effect gaps remain.\n\n"
        "Two diagnostics remain. The first is `missing_part` at `ir_087`: the complete generated error wrapper `{ok:false,error:...}` from `ir_085` reaches the success-block projection of `value`, although `ir_086` records the false flag going to the failure block. Six other projection alternatives return values, so this IR remains marked processed. This identifies a generated-wrapper correlation problem, not a corresponding source access to a nonexistent field. The second is the explicit undefined-value representation gap at `ir_419`, which stops the inspection projection/save tail; the later `ir_423` unmodeled gap is therefore blocked rather than reached.\n\n"
        "Selected sinks number 20: one standalone storage write and 19 network sends (13 original API sites plus six normal/exceptional loop-child sends). All 13 original client receiver bindings remain omitted in the processing summaries, and all 25 save-site persistent effects remain unmaterialized. These source fidelity concerns were not adjudicated because review never started.\n\n"
        "No field deletion or DOE conclusion is established by this audit. Exact site mappings, records, scopes, failures and hashes are in `propagation-source-audit.json`. This audit only reads the saved run; it does not rerun analysis, execute a Skill, or change active materials.\n", encoding="utf-8")
    print(json.dumps({"assembly_report": str(BASE / "assembly-review-audit.json"), "assembly_sha256": sha(BASE / "assembly-review-audit.json"),
                      "propagation_report": str(BASE / "propagation-source-audit.json"), "propagation_sha256": sha(BASE / "propagation-source-audit.json"),
                      "contract_inventory": {k: assembly["contract_inventory"][k] for k in ["obligations", "compiled_contracts", "kinds", "operations", "scope_counts"]},
                      "coverage": propagation_audit["coverage"], "site_counts": propagation_audit["site_counts"]}, indent=2))


if __name__ == "__main__":
    main()
