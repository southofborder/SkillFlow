"""Capture the new 001 processing fragment without running analysis or a replay."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-001-input-necessity-high-20261111-173347"
path = RUN / "steps/processing/value.json"
payload = path.read_bytes()
processing = json.loads(payload)
receipt = json.loads((RUN / "steps/processing/result.json").read_text(encoding="utf-8"))
assert hashlib.sha256(payload).hexdigest() == receipt["value_sha256"]
source_hash = hashlib.sha256((RUN / "source/inputs/package/SKILL.md").read_bytes()).hexdigest()
assert source_hash == "3e7a80d7f513ffb2e0851b3a1828e5c45854172bf14095514817f02c225401a6"

ops = []
for ir, semantics in processing["ir_semantics"].items():
    for si, segment in enumerate(semantics.get("segments", [])):
        for oi, op in enumerate(segment.get("ops", [])):
            ops.append({"instruction_id": ir, "pointer": f"/ir_semantics/{ir}/segments/{si}/ops/{oi}", "operation": op})

inventory = []
omissions = []
deterministic = []
for row in ops:
    op = row["operation"]
    base = {"instruction_id": row["instruction_id"], "pointer": row["pointer"], "op": op["op"]}
    if "input_contract" in op or "demand_transfer" in op:
        key = "input_contract" if "input_contract" in op else "demand_transfer"
        contract = op[key]
        rules = [contract] if key == "input_contract" else contract["rules"]
        arity = len(op.get("inputs", []))
        inventories = []
        for ri, rule in enumerate(rules):
            indices = [x["input_index"] for x in rule["inputs"]]
            inventories.append({"rule_index": ri, "actual_input_arity": arity, "authored_input_indices": indices,
                                "all_actual_slots_accounted_for": sorted(indices) == list(range(arity))})
        inventory.append({**base, "contract_kind": key, "contract": contract, "slot_coverage": inventories})
    opaque = op["op"] == "compute" and not op.get("expression")
    location_key = op.get("target", op.get("location"))
    tool_bound = op["op"] in {"call", "deliver", "receive"} and processing["locations"].get(location_key, {}).get("kind") == "tool"
    if opaque and "demand_transfer" not in op:
        omissions.append({**base, "expected": "demand_transfer"})
    if tool_bound and "input_contract" not in op:
        omissions.append({**base, "expected": "input_contract"})
    if op["op"] == "select_part" or (op["op"] == "compute" and op.get("expression")):
        deterministic.append({**base, "path": op.get("path"), "expression": op.get("expression"),
                              "needs_semantic_transfer_contract": False})

report = {
    "schema_version": "skillflow-provisional-source-comparison-v1",
    "case": "001", "observed_at": datetime.now(timezone.utc).isoformat(),
    "status": "provisional_initial_processing_not_final_selection",
    "run_directory": str(RUN).replace("\\", "/"),
    "previous_snapshot": "001-initial-provisional.json",
    "artifact": {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": receipt["value_sha256"], "bytes": len(payload), "accepted_call": receipt["accepted_call"]},
    "source_sha256": source_hash,
    "operation_inventory": {"ir_rows": len(processing["ir_semantics"]), "explicit_operations": len(ops), "op_counts": dict(Counter(x["operation"]["op"] for x in ops)), "opaque_computes": 1, "tool_deliveries": 1, "storage_reads": 1, "storage_writes": 1},
    "contracts": inventory,
    "mandatory_contract_omissions": omissions,
    "mandatory_coverage_interpretation": "No missing contract was observed among this fragment's one opaque compute and one tool-bound delivery. Deterministic expressions/projections and storage read/write operations are separately classified. This finite audit is not the current program's missing-contract completeness guarantee and does not substitute for selected-material source review.",
    "deterministic_field_transfers": deterministic,
    "source_comparisons": [
        {"expectation_ids": ["001-selection", "001-per-record-action"], "status": "represented_pending_review_and_execution", "source_lines": [9, 13], "operation_refs": ["ir_003", "ir_004", "ir_005", "ir_006", "ir_007", "ir_008", "ir_009", "ir_010", "ir_013"], "reason": "Member identity is preserved; opted_out and urgent use deterministic equality with true, and value uses deterministic greater-than-or-equal 100. No semantic transfer can remove these real expression dependencies."},
        {"expectation_ids": ["001-notify-recipient", "001-notify-body"], "status": "source_supported_contract_pending_review", "source_lines": [11, 15], "operation_refs": ["ir_011", "ir_012", "ir_013"], "reason": "The interface contract accounts for both actual operands. Each requires its complete original value. Its independent remainder does not permit deleting descendants of either whole required value. Necessity cites the independent source parameter requirements, not merely the existence of the current two arguments."},
        {"expectation_ids": ["001-count-output", "001-acquired-result"], "status": "precision_concern_pending_review", "source_lines": [8, 16], "operation_refs": ["ir_015"], "reason": "The count contract cites a real local ambiguity and names its missing membership rule, but marks the entire actual collection remainder unresolved with no independently irrelevant field ranges. The prewritten inventory identifies record_id/access_token/summary content as unnecessary to either stated count-population interpretation. Review should assess whether that local count-scope gap can be confined without blocking proven independent fields. No actual downstream blocking result is claimed yet."},
        {"expectation_ids": ["001-token-ban", "001-acquired-result"], "status": "actual_acquisition_preserved_pending_forward_checks", "source_lines": [8, 14], "operation_refs": ["ir_001", "ir_013"], "reason": "The complete events acquisition remains modeled, with possible model routing in processing evidence. The explicit notification delivery takes only projected recipient and summary. This does not erase acquired tokens or prove that every generated model observation complies with the any-recipient prohibition."}
    ],
    "local_gaps": [{"instruction_id": "ir_015", "output": {"property": "value", "path": []}, "input_scope": {"input_index": 0, "path": [], "range_kind": "remainder"}, "reason": "Which records count as processed is unspecified.", "specific_missing_relation": "All evaluated occurrences versus selected notification occurrences.", "evidence": {"file": "skill/SKILL.md", "start_line": 16, "end_line": 16}, "audit": "Concrete source gap; authored input scope is broader than the positively established ambiguity."}],
    "processing_gaps": processing.get("processing_gaps", []),
    "processing_gap_audit": "The additional ir_013 gap concerns send-failure continuation. The source does not specify failure handling. It must not be confused with unknown ordinary recipient/body values, or treated as a source-established missing/wrong argument. Its actual runtime and demand impact await final results.",
    "coverage": {"source_review": "not_available_at_snapshot", "propagation": "not_available_at_snapshot", "doe": "not_available_at_snapshot", "validated_deletion_examples": [], "tool_contracts_present": 1, "opaque_contracts_present": 1, "mandatory_contract_omissions_observed": len(omissions)},
    "acquisition_projection": {"status": "unestablished", "reason": "No source/interface field-selection capability is supplied for the storage read. Later post-acquisition field-use minimization must not be described as read-side projection support."},
    "limits": ["The processing fragment has not yet been finally selected or source-reviewed.", "A source-backed contract authored by a model is not an accepted receipt or proof of semantic minimality.", "Count-scope precision concern is audit-only; no feedback is sent to the running pipeline.", "No production, prompt, source or run artifact was modified; no model, Skill or replay was started."]
}
destination = OUT / "001-processing-provisional.json"
if destination.exists():
    raise RuntimeError("Preserve the initial processing snapshot; later audits need new filenames.")
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
text = f"""# 001 processing provisional source comparison

Observed: {report['observed_at']}

The initial processing fragment accounts for 17 IR rows and {len(ops)} explicit operations. It contains one opaque compute contract and one tool-interface input contract. Both account for all their actual input slots. No mandatory contract omission was observed in this finite fragment. Three structured comparisons and five field projections correctly rely on deterministic transfer rules; the file read and write are storage operations.

The `notify.send` contract at `/ir_semantics/ir_013/segments/0/ops/0/input_contract` requires the whole recipient and whole original summary values. Its evidence is source lines 11–12, which independently specify the two parameters. The same-record projections are explicit and no extra record field is introduced into these two arguments. An independent remainder alongside a whole-value requirement does not make internal recipient or summary fields deletable.

The count contract at `/ir_semantics/ir_015/segments/0/ops/0/demand_transfer` names a genuine source gap: which occurrences count as processed. Its gap is backed by line 16 and does not rely merely on black-box execution. Its scope is nevertheless broad: all of the input collection remainder is unresolved and no irrelevant field range is declared. The source-only inventory identified record_id, access_token and summary content as unnecessary to either all-evaluated or selected-record cardinality. This is a field-precision concern for final review, not a claim that a downstream demand result already failed.

The normal notification/control relationships remain explicit. A separate processing gap concerns unspecified send-failure continuation. It is distinct from a wrong or missing source argument and must be evaluated at its actual affected control scope. Complete acquisition and possible model observations remain facts; no audit observation erases access_token from the acquired value.

No contract has been verified by source review in this snapshot. Propagation reach, demand ranges, preservation checks and DOE deletion examples remain unavailable. No capability to project fields at the events.json read interface is established. Only a later completed result can support concrete removal recommendations.

Exact operation/contract inventories, source spans and hashes are in the adjacent JSON. The running pipeline receives no audit feedback. Production and run artifacts are unchanged.
"""
(OUT / "001-processing-provisional.md").write_text(text, encoding="utf-8")
print(json.dumps({"saved": str(destination), "operations": len(ops), "contracts": len(inventory), "omissions_observed": len(omissions)}))
