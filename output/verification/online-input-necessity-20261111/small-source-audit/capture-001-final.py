"""Audit saved selected 001 materials; no analysis, replay, model or Skill calls."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

from skillflow.doe.input_contract_review import checked_input_contract_review
from skillflow.common.recording import canonical_sha256

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-001-input-necessity-high-20261111-173347"
COST = OUT.parent / "cost-provenance-audit/001-20261111T121904653264Z.json"

def read(rel):
    return json.loads((RUN / rel).read_text(encoding="utf-8"))

def artifact(path):
    data = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}

rels = ["result.json", "selection.json", "controller-finished.json", "replay-check.json",
        "source/inputs/package/SKILL.md", "task/task.json", "graph/initial.json",
        "revision/annotation/audit/raw-annotation.json", "revision/annotation/audit/compiled-response.json",
        "revision/annotation/audit/compilation-map.json", "revision/annotation/audit/wire-annotation.json",
        "revision/review/result.json", "doe/audit/input-contract-review.json",
        "propagation/records.json", "propagation/audit/stats.json", "doe/doe-result.json",
        "doe/audit/demand-support.json", "doe/report.md"]
artifacts = [artifact(RUN / rel) for rel in rels] + [artifact(COST)]
source = (RUN / "source/inputs/package/SKILL.md").read_text(encoding="utf-8")
assert hashlib.sha256((RUN / "source/inputs/package/SKILL.md").read_bytes()).hexdigest() == "3e7a80d7f513ffb2e0851b3a1828e5c45854172bf14095514817f02c225401a6"
task = read("task/task.json")
cfg = read("graph/initial.json")["cfg"]
raw = read("revision/annotation/audit/raw-annotation.json")
compiled = read("revision/annotation/audit/compiled-response.json")
mapping = read("revision/annotation/audit/compilation-map.json")
receipt = checked_input_contract_review(read("doe/audit/input-contract-review.json"),
    files={"skill/SKILL.md": source}, cfg=cfg,
    annotation={"task": task, "raw_annotation": raw, "compiled_annotation": compiled, "mapping": mapping})
demand = read("doe/audit/demand-support.json")
doe = read("doe/doe-result.json")
records = read("propagation/records.json")
review = read("revision/review/result.json")
cost = json.loads(COST.read_text(encoding="utf-8"))
assert demand["input_contract_review_sha256"] == receipt["receipt_sha256"]
assert read("doe/manifest.json")["input_contract_review_sha256"] == canonical_sha256(receipt)
assert all(v == "processed" for v in demand["coverage"]["upstream"].values())

assessments = demand["input_assessments"]
ranges = [part for assessment in assessments for part in assessment["ranges"]]
comparisons = [item for sink in doe["sinks"] for item in sink["data_reviews"]]
compact_assessments = []
for assessment in assessments:
    unique = {}
    for part in assessment["ranges"]:
        selector = {key: part[key] for key in ("status", "property", "path", "excluded_paths")}
        key = json.dumps(selector, sort_keys=True)
        unique.setdefault(key, {**selector, "derivation_rows": 0, "demand_refs": [], "contract_refs": [], "diagnostic_refs": []})
        unique[key]["derivation_rows"] += 1
        for ref in ("demand_refs", "contract_refs", "diagnostic_refs"):
            unique[key][ref] = sorted(set(unique[key][ref] + part.get(ref, [])))
    compact_assessments.append({key: assessment[key] for key in ("id", "node_kind", "instruction_id", "operation_id", "input_index", "data_ids", "coverage")} | {"range_rows": len(assessment["ranges"]), "unique_selectors": list(unique.values())})

contracts_by_id = {x["id"]: x for x in compiled["input_contracts"]}
contract_inventory = [{"contract_id": check["contract_id"], "kind": contracts_by_id[check["contract_id"]]["kind"],
    "instruction_id": contracts_by_id[check["contract_id"]]["instruction_id"],
    "raw_pointer": contracts_by_id[check["contract_id"]]["raw_pointer"],
    "target_ids": receipt["review_core"]["contract_targets"][check["contract_id"]],
    "review": check, "contract": contracts_by_id[check["contract_id"]]["contract"]} for check in receipt["checks"]]

crosswalk = []
for line, ir, opcode, operation, op_id in [(8, "ir_001", "read_event_records", "read", "op_ir_001:e0:a0"),
        (11, "ir_013", "notify.send", "deliver", "op_ir_013:e0:a0"),
        (16, "ir_016", "write_file", "write", "op_ir_016:e0:a0")]:
    cfg_row = [(bid, index, value) for bid, block in cfg["blocks"].items() for index, value in enumerate(block["instructions"]) if value["id"] == ir][0]
    actual = [{"event_index": ei, "op_index": oi, "op": op["op"], "inputs": op["inputs"], "outputs": op["outputs"], "alternatives": op.get("alternatives", [])}
              for ei, event in enumerate(records[ir]["events"]) for oi, op in enumerate(event["atomic_ops"]) if op["op"] == operation]
    assert actual
    crosswalk.append({"source_file": "skill/SKILL.md", "start_line": line, "end_line": 12 if ir == "ir_013" else line,
        "instruction_id": ir, "cfg_opcode": opcode, "cfg_pointer": f"/blocks/{cfg_row[0]}/instructions/{cfg_row[1]}",
        "operation_id": op_id, "propagation_status": demand["coverage"]["upstream"][ir], "recorded_operations": actual,
        "sink_ids": [s["id"] for s in doe["sinks"] if s["boundary"]["instruction_id"] == ir],
        "meaning": "A generated static record reaches this source boundary. No real Skill action or concrete event execution occurred."})

counts = {"generated_ir": sum(len(x["instructions"]) for x in cfg["blocks"].values()), "propagation_records": len(records),
    "upstream_statuses": dict(Counter(demand["coverage"]["upstream"].values())), "finite_source_boundary_sites": len(crosswalk), "source_boundary_sites_with_records": len(crosswalk),
    "input_assessments": len(assessments), "assessment_node_kinds": dict(Counter(a["node_kind"] for a in assessments)),
    "assessment_coverage": dict(Counter(a["coverage"] for a in assessments)),
    "range_rows": len(ranges), "range_statuses": dict(Counter(p["status"] for p in ranges)),
    "assessment_status_sets": dict(Counter("+".join(sorted({p["status"] for p in a["ranges"]})) for a in assessments)),
    "input_findings": len(demand["input_findings"]), "sinks": len(doe["sinks"]), "sink_types": dict(Counter(s["boundary"]["sink_type"] for s in doe["sinks"])),
    "sensitive_comparisons": len(comparisons), "sensitive_conclusions": dict(Counter(x["conclusion"] for x in comparisons)),
    "nonnull_reductions": sum(x.get("reduction") is not None for x in comparisons), "constraint_checks": len(doe["constraints"]["checks"]),
    "constraint_preservation_results": len(doe["constraints"]["preservation"]), "diagnostics": len(demand["diagnostics"]),
    "requirement_statuses": dict(Counter(x["status"] for x in demand["coverage"]["requirements"].values())),
    "contract_review_statuses": dict(Counter(x["status"] for x in receipt["checks"]))}
assert counts["input_assessments"] == 53 and counts["range_statuses"] == {"unresolved": 58, "required": 393}
assert counts["nonnull_reductions"] == 0 and not [x for x in ranges if x["status"] == "deletable"]

expectations = [
    {"expectation_id": "001-selection", "source_lines": [9, 10], "assessment": "The CFG and deterministic processing preserve the opt-out gate before urgency and the numeric threshold. Field-specific demands for opted_out, urgent and value are present. The Task retains the additional necessary-versus-sufficient selection interpretation; final review does not reject it. The separate only_if constraint is missing, so this is represented control behavior, not complete preservation coverage.", "status": "partially_supported", "review_refs": ["F001"], "diagnostic_codes": ["task_source_issue", "requirement_expression_gap"]},
    {"expectation_id": "001-per-record-action", "source_lines": [11, 13], "assessment": "One notification operation is recorded with the same member-scope binding for both argument alternatives. Repeated occurrences are modeled by the member family. Failure continuation remains source-unspecified and no concrete runtime call count is measured.", "status": "supported_normal_static_path_with_limit", "record_ref": "propagation/records.json#/ir_013/events/0/atomic_ops/0/alternatives", "diagnostic_codes": ["processing_gap", "requirement_expression_gap"]},
    {"expectation_id": "001-notify-recipient", "source_lines": [11, 11], "assessment": "The accepted interface contract requires the complete original selected recipient value in slot 0. Required ranges trace both to notify_once through reviewed_input_contract and to recipient_from_record through task_expected_relation.", "status": "supported_required_relation", "assessment_id": "input_assessment_b7cde5a66a90d5a41f77", "demand_refs": ["demand_2cd7c030c0d342dfec4a", "demand_3001c6cc2e29d3559f02"]},
    {"expectation_id": "001-notify-body", "source_lines": [12, 15], "assessment": "The accepted interface contract requires the complete original summary in slot 1 from the same occurrence. No internal summary range is declared removable. The saved demanded property is whole value with path [].", "status": "supported_required_relation", "assessment_id": "input_assessment_d3974d18ad8d10f48fe3", "demand_refs": ["demand_1fabaacc2770e0cbef29", "demand_19452edcfe87be8e5004"]},
    {"expectation_id": "001-token-ban", "source_lines": [14, 14], "assessment": "The final review identifies incomplete receiver coverage: the authored forbid_information constraint covers notify only, omitting recipient-scoped model observations of acquired collections and whole records. Its saved satisfied result is valid only for that narrow authored scope. It does not establish the source-wide prohibition. Whole input observations and possible count sensitivity remain recorded.", "status": "source_constraint_mapping_incomplete", "review_refs": ["F002"], "constraint_refs": ["constraint_0584eecf2cdd55555b6c"]},
    {"expectation_id": "001-count-output", "source_lines": [16, 16], "assessment": "The count write is reached in static propagation, but its contributing population is unresolved. Final review explicitly distinguishes all-traversed cardinality from selected-occurrence membership/multiplicity and says recipient/summary/record_id/access_token are unnecessary for the count. The saved contract is unresolved as a whole and the backend retains a conservative whole-collection range. Thus the source-supported independent fields did not become certified deletions.", "status": "known_local_ambiguity_with_coarse_input_barrier", "review_refs": ["F003"], "contract_refs": ["input_contract_e15a58bc08046c8d6390"], "diagnostic_refs": ["diagnostic_68e37d5f6b43b139611b"]},
    {"expectation_id": "001-acquired-result", "source_lines": [8, 16], "assessment": "The acquisition assessment retains each.recipient, each.summary, each.opted_out, each.urgent and each.value plus root shape/cardinality. It also has unresolved whole-value rows. No deletable record_id/access_token range is emitted. The actual acquisition and generated model observations survive unchanged. The source supplies no established read-side projection capability.", "status": "field_demands_visible_deletion_unresolved", "assessment_id": "input_assessment_16121bb3d6499f9773e5"},
]

chain_ids = {"demand_009346bb17ef04f90af6", "demand_2cd7c030c0d342dfec4a", "demand_3001c6cc2e29d3559f02", "demand_1fabaacc2770e0cbef29", "demand_19452edcfe87be8e5004"}
report = {
    "schema_version": "skillflow-selected-source-comparison-v1", "case": "001", "observed_at": datetime.now(timezone.utc).isoformat(),
    "audit_status": "final_closed_run_read_only", "run_directory": str(RUN).replace("\\", "/"),
    "scope": "Source-supported finite audit of the selected new 001 run against seven of the 26 prewritten small-case expectations. Not a gold benchmark, actual Skill execution, empirical precision/recall estimate, or new replay.",
    "result": read("result.json"), "controller": read("controller-finished.json"), "selection": read("selection.json"),
    "artifacts": artifacts, "counts": counts, "source_boundary_crosswalk": crosswalk,
    "receipt": {"read_only_validation": "passed", "validation_function": "checked_input_contract_review", "solving_performed": False,
        "receipt_sha256": receipt["receipt_sha256"], "review_status": receipt["review_status"], "source_review_complete": receipt["source_review_complete"],
        "demand_internal_receipt_digest_matches": True,
        "doe_manifest_complete_receipt_digest_matches": True,
        "doe_manifest_complete_receipt_sha256": canonical_sha256(receipt),
        "binding": {key: receipt[key] for key in ("source_sha256", "cfg_sha256", "annotation_sha256", "contracts_sha256", "review_sha256")},
        "notice": "Receipt identity/reference validation passed. Demand support binds the internal receipt_sha256; the DOE manifest binds canonical_sha256 of the complete receipt including that internal digest. One accepted local contract is usable despite incomplete global review; identity is not semantic proof."},
    "contracts": contract_inventory, "review_findings": review["review"]["findings"],
    "expectation_comparisons": expectations, "input_assessment_inventory": compact_assessments,
    "selected_required_evidence_chains": {key: doe["derivations"]["demand"][key] for key in sorted(chain_ids)},
    "deletion_conclusions": {"certified_deletable_ranges": [], "certified_sensitive_reductions": [],
        "reason": "No deletable range or reduction is present in the saved selected result. Every assessment contains an unresolved range; 38 also retain positive requirements. The report must not relabel absence of a field-specific positive demand as a completed deletion proof.",
        "source_supported_opportunities_not_certified": [{"source_file": "skill/SKILL.md", "source_lines": [8, 16],
            "fields": ["record_id", "access_token"], "scope": "Post-acquisition or individual consuming-use minimization, preserving actual original read/observations.",
            "basis": "Neither field is positively used by the stated notification/selection/count semantics; the final count review explicitly excludes both. No concrete rewrite or server projection capability is established.",
            "blockers": ["Global Task/realization limitations block deletion in all 53 assessments.", "The local unresolved count contract is retained as a whole-collection conservative range.", "The any-recipient token restriction is not fully represented."]}]},
    "constraints": doe["constraints"], "constraint_interpretation": "One narrow notify-only token constraint is saved satisfied. F002 establishes incomplete source receiver coverage. No local reduction preservation result exists because no reduction was emitted.",
    "diagnostics": demand["diagnostics"],
    "limitation_scope_audit": {"task_and_mapping_global_diagnostics": [x for x in demand["diagnostics"] if x["instruction_id"] is None],
        "local_contract_diagnostic": "diagnostic_68e37d5f6b43b139611b", "processing_control_gap": "diagnostic_d75c06f55f3cc3e368df",
        "interpretation": "The count contract diagnostic is anchored at ir_015; separate pre-existing Task issue/requirement gap policies create global material barriers. Consequently it would be inaccurate to attribute all 53 unresolved assessments solely to the count contract or to unvisited CFG positions."},
    "cost": {"audit_artifact": str(COST.relative_to(ROOT)).replace("\\", "/"), "status": cost["status"], "counts": cost["counts"], "known_public_usage": cost["known_public_usage"], "categories": cost["categories"], "timing": cost["timing"], "http_attempts": cost["http_attempts"], "provider_billing_cost": cost["provider_billing_cost"], "usage_notice": cost["usage_notice"]},
    "limits": ["393 required and 58 unresolved entries are derivation rows, not unique fields or unique leaks.", "All 17 generated IR and all 3 finite source boundary sites have static records; this does not prove all source semantics or concrete paths.", "The 18 sensitivity comparisons arise from two credential declarations at nine sinks; all are unresolved no_excess_established, not safe verdicts.", "No source-established wrong/missing input defect was found in this source-only inventory; zero saved input_findings does not prove complete source-error detection.", "No source rewrite or acquisition projection is recommended as executable by this audit.", "The report's phrase Offline preparation; zero API calls refers to the deterministic DOE component; the complete real-model run used 12 native starts."]
}
assert artifacts == [artifact(RUN / rel) for rel in rels] + [artifact(COST)], "Input artifacts changed during audit"
report["artifact_stability"] = "All listed selected source/run/audit files remained byte-identical during capture."
destination = OUT / "001-final-audit.json"
if destination.exists():
    raise RuntimeError("Preserve the completed audit; corrections must use a distinct filename.")
destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
markdown = """# 001 selected-run source and input-necessity audit

001 closed **partial**, with complete static propagation and partial DOE. All **17/17 generated IR** have records and all **3/3 finite source boundary sites** are represented and reached in that static model. The selected bundle is `revision/annotation`; the sole controller replay matched in 5.9443 seconds with zero new native starts. No Skill was executed.

| Saved result | Count |
| --- | ---: |
| All-input assessments | 53: 22 IR inputs, 30 operation inputs, 1 acquisition output |
| Assessment coverage | 53 processed; 0 not reached |
| Range derivation rows | 451: 393 required, 58 unresolved, 0 deletable |
| Assessment status combinations | 38 required + unresolved; 15 unresolved only |
| Input semantic findings | 0 |
| Sinks | 13: 11 model observations, 1 tool delivery, 1 storage write |
| Sensitive comparisons | 18 no_excess_established; 0 reductions |
| Input contract checks | 1 accepted tool contract; 1 unresolved count contract |

These are row and comparison counts, not unique fields, execution events or leaks. Every assessment has an unresolved range. The 18 comparisons explicitly say limitations prevent a conclusion; they do not establish safety.

## Source boundary crosswalk

| Original source | Selected CFG | Recorded operation | Meaning |
| --- | --- | --- | --- |
| SKILL.md:8, read events.json | ir_001; /blocks/block_001/instructions/0 | op_ir_001:e0:a0 read | Complete acquisition remains recorded. Its subsequent model observation is also retained. |
| SKILL.md:11–12, notify.send | ir_013; /blocks/block_006/instructions/2 | op_ir_013:e0:a0 deliver | Both actual arguments share one recorded member binding; no concrete runtime call count is measured. |
| SKILL.md:16, write count.txt | ir_016; /blocks/block_007/instructions/1 | op_ir_016:e0:a0 write | Static normal-exhaustion path reaches the write; the count meaning remains ambiguous. |

The selected receipt was revalidated using the pure `checked_input_contract_review` loader, without solving, replay or another semantic call. Its internal SHA is `37a3e01e24b450407e7d872685fb3327b4846780770afe5af239a06f83e30d64` and matches demand support. The DOE manifest separately matches the complete receipt's canonical SHA `50be53b8e7c943817910998a3df1e296177a09ffa7376431569ae32c15265e2c`. Source, CFG, Task, raw/compiled annotation, mapping and contract binding checks passed. `review_status=complete` means the review call completed; `source_review_complete=false` retains its material findings.

## Source-supported necessary inputs

The accepted notify contract requires **whole recipient** in input 0 and **whole original summary** in input 1, with source evidence at lines 11–12. Both come from the same selected record. The saved demand graph connects `notify_once` to its action seed and then, through `reviewed_input_contract`, to both whole-value input ranges. Separate `recipient_from_record` and `original_summary_body` goals retain their exact expected relations. Internal summary fields are not deletable under this obligation.

The acquisition assessment shows field-level demands for `each.recipient`, `each.summary`, `each.opted_out`, `each.urgent`, and `each.value`, plus collection shape/cardinality. Deterministic equality/threshold expressions preserve real selection dependencies; they were not overridden by a semantic contract. This demonstrates field-level demand propagation in the actual run, while its unresolved ranges prevent a complete minimality claim.

## Remaining correctness and precision limits

The final source review retains three findings. F001 says `skip_unselected` lacks an explicit supported `only_if` constraint even though the CFG has the two selection routes. F002 says the access_token prohibition covers only `notify`, omitting recipient-scoped model observations of the acquired collection and whole records. F003 retains the count contract as unresolved: all traversed occurrences require cardinality, while selected occurrences require membership/multiplicity and the selection conditions.

The single saved token constraint is **satisfied only within its authored notify-only scope**. It does not establish the source-wide any-recipient prohibition. No reduction preservation results were produced. Possible sensitivity propagation to the count is also preserved; it is not proof that the numeric count contains a plaintext token.

The count review explicitly says recipient, summary, record_id and access_token are unnecessary for the count, but its decision still disables the whole count contract. The saved compute retains a conservative whole-collection requirement. This confirms the provisional field-precision concern: known independent field relationships did not become usable local deletion conclusions. It is separate from global Task/realization barriers, which also affect all assessments. The source count ambiguity and the additional literal 'only when' selection ambiguity are recorded; unspecified send-failure continuation adds a control limitation. Therefore, not every unresolved assessment is caused by the count contract, and none is an unreached-IR coverage gap.

## Deletion examples and cost

**No certified deletion example is available from this selected run.** Source semantics and the final review support considering `record_id` and `access_token` unnecessary for the listed positive uses, but the saved result does not certify removing them. Original acquisition/observations must remain facts. No read-side field projection capability is established, and no source rewrite is proposed here.

The separate final cost audit records **12 native starts**: 7 normal, 4 semantic-repair, 1 structural-correction; **337,253 public tokens** (305,110 input + 32,143 output). All 12 requests have complete public usage. There were zero outer retries and two internal reconnect notices; provider HTTP attempt counts and billing remain unknown. Analysis took 923.249 seconds. The deterministic DOE report's 'zero API calls' line applies to that backend component, not the complete run.

This is a finite audit against seven prewritten source expectations, not a gold benchmark or a precision/recall claim. The adjacent JSON includes each expectation, exact assessment IDs, compact ranges, evidence chains, diagnostics, contract decisions, original source spans, full artifact hashes, and the source-boundary crosswalk. Earlier provisional snapshots are preserved. No production, prompt, source or run artifact was changed.
"""
(OUT / "001-final-audit.md").write_text(markdown, encoding="utf-8")
print(json.dumps({"saved": str(destination), "counts": counts, "receipt_validation": "passed", "inputs_unchanged": True}))
