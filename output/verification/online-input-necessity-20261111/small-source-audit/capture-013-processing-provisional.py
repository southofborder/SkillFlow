"""Inspect initial 013 processing/CFG contracts; never run or replay analysis."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-013-input-necessity-high-20261111-173347"
def read(rel):
    return json.loads((RUN / rel).read_text(encoding="utf-8"))
paths = ["steps/graph/value.json", "steps/processing/value.json", "annotation/audit/compiled-response.json", "annotation/audit/compilation-map.json", "source/inputs/package/SKILL.md"]
artifacts = [{"path": str((RUN / rel).relative_to(ROOT)).replace("\\", "/"),
    "sha256": hashlib.sha256((RUN / rel).read_bytes()).hexdigest()} for rel in paths]
assert artifacts[-1]["sha256"] == "90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495"
p = read("steps/processing/value.json")
g = read("steps/graph/value.json")
c = read("annotation/audit/compiled-response.json")
m = read("annotation/audit/compilation-map.json")
ops = [{"instruction_id": ir, "wire_pointer": f"/ir_semantics/{ir}/segments/{si}/ops/{oi}", "operation": op}
    for ir, semantics in p["ir_semantics"].items() for si, segment in enumerate(semantics.get("segments", []))
    for oi, op in enumerate(segment.get("ops", []))]
contracts = []
omissions = []
for row in ops:
    op = row["operation"]
    key = "input_contract" if op["op"] == "call" else "demand_transfer" if op["op"] == "compute" and not op.get("expression") else None
    if key:
        if key not in op:
            omissions.append({"instruction_id": row["instruction_id"], "wire_pointer": row["wire_pointer"], "missing": key})
            continue
        rules = [op[key]] if key == "input_contract" else op[key]["rules"]
        checks = [{"rule_index": index, "actual_slot_count": len(op.get("inputs", [])), "authored_input_indices": [v["input_index"] for v in rule["inputs"]],
                   "all_actual_slots_accounted_for": sorted(v["input_index"] for v in rule["inputs"]) == list(range(len(op.get("inputs", []))))}
                  for index, rule in enumerate(rules)]
        contracts.append({"instruction_id": row["instruction_id"], "wire_pointer": row["wire_pointer"] + "/" + key,
            "kind": key, "actual_inputs": op.get("inputs", []), "contract": op[key], "slot_checks": checks,
            "compiled_contract_ids": [x["contract_id"] for x in m["input_contracts"] if x["wire_pointer"] == row["wire_pointer"] + "/" + key]})
assert len(contracts) == 8 and len(c["input_contracts"]) == 11 and not omissions
assert all(check["all_actual_slots_accounted_for"] for x in contracts for check in x["slot_checks"])

questions = [
    {"id": "013-outcome-discriminator-representation", "kind": "processing_interface_relation", "irs": ["ir_006", "ir_010", "ir_012"],
     "source_lines": [9, 14], "finding": "The three success tests have truth-output contracts with unresolved whole response inputs because an outcome discriminator field is not supplied. The source's success/failure routing obligation itself is clear. A concrete encoding relation is missing in this chosen ordinary-call representation; this is not evidence that the Task purpose is unclear. Supported bounded call cases may express the semantic alternatives without guessing a response field.",
     "affected_scope": "Outcome selector/control relation, not the required source_id/FAST_KEY call inputs or the unchanged success body relation."},
    {"id": "013-transient-classification-representation", "kind": "processing_interface_relation", "irs": ["ir_008"],
     "source_lines": [10, 11], "finding": "The transient-error predicate contract names the missing criterion/error information and is source-anchored. The task still unambiguously requires exactly one retry on a transient first failure and no retry on a non-transient first failure. Which error fields implement this predicate is distinct from the natural-language retry obligation.",
     "affected_scope": "First-failure classification and routes dependent on it; no whole-task ambiguity is inferred by this audit."},
    {"id": "013-error-field-selector", "kind": "representation_evidence_concern", "irs": ["ir_007", "ir_019"],
     "source_lines": [10, 14], "finding": "Processing selects path ['error'] from ordinary call outputs. Source establishes the failing call's error but does not specify an object field named error. The cited evidence gives a semantic failure component, not its wire representation. This selected-field relation needs review or an explicit outcome representation; do not relabel it a wrong-field bug in the original Skill.",
     "affected_scope": "First-error classification input and terminal archive-error value."},
    {"id": "013-final-status-sufficiency", "kind": "source_output_ambiguity_and_contract_evidence_concern", "irs": ["ir_022", "ir_023", "ir_024"],
     "source_lines": [13, 16], "finding": "The source leaves final-status contents/encoding unspecified, which is a genuine local observable-output ambiguity. The authored contract requires the whole success/failure category and says that category suffices 'in this CFG'. The CFG's sole existing operand alone does not independently establish semantic sufficiency for the unspecified status. Review must distinguish this output ambiguity from the clear append action/order and from missing response encodings.",
     "affected_scope": "Status value only; append-before-return, successful body and archive-error obligations remain explicit."},
    {"id": "013-hypothetical-later-output", "kind": "no_source_obligation", "irs": ["ir_024"],
     "source_lines": [13, 16], "finding": "The processing gap additionally mentions linkage to a separately saved result. No such linkage/output/analysis is required by the source. It must not create new data demands or make explicit fetch/return semantics globally unresolved.",
     "affected_scope": "No additional required source output is established."},
]
report = {
    "schema_version": "skillflow-provisional-source-comparison-v1", "case": "013", "observed_at": datetime.now(timezone.utc).isoformat(),
    "status": "initial_processing_not_final_selected_material", "artifacts": artifacts,
    "scope": "Finite independent source audit during the frozen run, with no pipeline feedback. Later revisions and selected receipt need a separate audit.",
    "inventory": {"cfg_blocks": len(g["blocks"]), "cfg_ir": sum(len(x["instructions"]) for x in g["blocks"]), "cfg_edges": len(g["edges"]),
        "processing_ir_rows": len(p["ir_semantics"]), "explicit_operations": len(ops), "operation_counts": dict(Counter(x["operation"]["op"] for x in ops)),
        "authored_contracts": len(contracts), "authored_tool_contracts": 3, "authored_opaque_compute_contracts": 5,
        "compiled_contracts": len(c["input_contracts"]), "compiled_tool_contracts": 6, "compiled_compute_contracts": 5,
        "contract_multiplicity_notice": "Three authored calls expand into six actual paired request/response tool contracts; these are not six source call sites."},
    "contracts": contracts, "mandatory_contract_omissions_observed": omissions,
    "coverage_notice": "All eight required authored contracts are present and account for all actual operation slots. This finite inventory is not a proof that the frozen validator enforces omissions globally.",
    "needed_ranges": [
        {"irs": ["ir_001", "ir_003", "ir_004"], "source_lines": [8, 9], "relation": "Deterministic source_id and FAST_KEY projections, followed by a structured presence test for the key. Presence is not equated to key plaintext."},
        {"irs": ["ir_005", "ir_009"], "source_lines": [9, 10], "relation": "Each fast contract requires complete source_id and complete FAST_KEY values, accounting for its two actual operation operands. The CFG tool-resource operand is not a fabricated request argument."},
        {"irs": ["ir_011"], "source_lines": [12, 15], "relation": "The archive contract requires complete source_id as its sole actual argument. No key argument is authored; future extra fields would still need assessment."},
        {"irs": ["ir_013", "ir_015", "ir_017", "ir_021", "ir_025"], "source_lines": [13, 14], "relation": "Three deterministic body projections feed a predecessor-specific merge with the archive error. Each successful returned body remains whole and is paired to its own attempt; correctness of error representation is separately questioned."},
        {"irs": ["ir_024", "ir_025"], "source_lines": [16, 16], "relation": "The single final block appends to status.txt before the return. No later fetch site or third fast attempt is authored."}],
    "source_judgments": questions, "processing_gaps": p.get("processing_gaps", []),
    "bounded_shape": {"fast_call_sites": ["ir_005", "ir_009"], "archive_call_sites": ["ir_011"], "append_sites": ["ir_024"], "return_sites": ["ir_025"],
        "notice": "Authored CFG shape preserves finite branch routes; static propagation has not been audited in this snapshot, and no concrete call counts are measured."},
    "coverage": {"source_review": "in_progress_not_adopted", "selected_receipt": "not_available_at_snapshot", "propagation": "not_audited", "doe": "not_audited", "validated_deletions": []},
    "limits": ["No accepted semantic contract or deletion conclusion is inferred solely from authored contracts.", "Task purpose, source output ambiguity, and missing processing/interface relations are separate categories in this audit.", "No production, prompt, source or run artifact was changed; no model, Skill or replay was launched."]
}
destination = OUT / "013-processing-provisional.json"
if destination.exists():
    raise RuntimeError("Preserve the initial processing audit; use new filenames for later evidence.")
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "013-processing-provisional.md").write_text("""# 013 initial processing contract audit

The first CFG contains 25 IR, 11 blocks and 15 edges. Processing supplies **8 authored contracts**: 3 tool calls and 5 opaque computes. All account for every actual operation input. Compilation expands the three calls into six paired request/response contracts, producing **11 compiled contracts** total. No mandatory contract omission was observed in this finite initial material.

The first and retry fast calls each require whole source_id and whole FAST_KEY. Archive requires whole source_id only. Source_id/FAST_KEY field selection and key presence are deterministic. Three original response.body projections feed the appropriate return alternative; append mode is explicitly append and its shared final block precedes the return. The graph contains two fast sites and one archive site, with no third fast call or post-success fetch route.

The **Task's retry and fallback obligations are clear**. Three truth-output contracts leave the response discriminator relation unresolved because the chosen ordinary-call representation lacks a concrete outcome encoding; the transient classifier also lacks its error-field criterion. These are processing/interface questions, not proof that the Task purpose is ambiguous. Supported bounded call cases could express stated semantic outcomes without inventing field names. This independent audit does not expand those questions into unrelated source_id/key/body scopes.

Two error extractions at ir_007 and ir_019 use path `['error']`, although the source establishes the call's error semantically rather than specifying a response object field. This is a generated-representation evidence concern for review, not an original Skill wrong-field finding.

Final-status contents/serialization are a genuine local output ambiguity. The ir_023 contract requires the whole merged success/failure category and says it suffices 'in this CFG'. The current input list alone does not establish semantic sufficiency for an underspecified output; final review should assess that reason. The append action/order remain explicit. Hypothetical association with a separately saved result is not a source obligation.

This snapshot adopts no in-progress review answer and makes no propagation, preservation or deletion claim. The adjacent JSON contains exact contracts, slot checks, compiled IDs, source spans and scoped audit questions. No feedback was sent to the active pipeline. All production and run materials remain untouched.
""", encoding="utf-8")
print(json.dumps({"saved": str(destination), "authored_contracts": len(contracts), "compiled_contracts": len(c["input_contracts"]), "missing_contracts": len(omissions)}))
