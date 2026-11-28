"""Frozen selected-material audit only; no solving, model, Skill or replay."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from skillflow.common.recording import canonical_sha256
from skillflow.doe.input_contract_review import checked_input_contract_review

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-013-input-necessity-high-20261111-173347"
COST = OUT.parent / "cost-provenance-audit/013-20261111T125654863065Z.json"
def read(rel):
    return json.loads((RUN / rel).read_text(encoding="utf-8"))
def artifact(path):
    content = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
rels = ["result.json", "selection.json", "controller-finished.json", "replay-check.json", "source/inputs/package/SKILL.md", "task/task.json", "graph/initial.json", "revision/annotation/audit/raw-annotation.json", "revision/annotation/audit/compiled-response.json", "revision/annotation/audit/compilation-map.json", "revision/annotation/audit/wire-annotation.json", "revision/review/result.json", "propagation/records.json", "doe/audit/input-contract-review.json", "doe/audit/demand-support.json", "doe/manifest.json", "doe/doe-result.json", "doe/report.md"]
artifacts = [artifact(RUN / rel) for rel in rels] + [artifact(COST)]
assert artifact(RUN / "source/inputs/package/SKILL.md")["sha256"] == "90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495"
task = read("task/task.json"); cfg = read("graph/initial.json")["cfg"]
raw = read("revision/annotation/audit/raw-annotation.json"); compiled = read("revision/annotation/audit/compiled-response.json"); mapping = read("revision/annotation/audit/compilation-map.json")
receipt = checked_input_contract_review(read("doe/audit/input-contract-review.json"),
    files={"skill/SKILL.md": (RUN / "source/inputs/package/SKILL.md").read_text(encoding="utf-8")}, cfg=cfg,
    annotation={"task": task, "raw_annotation": raw, "compiled_annotation": compiled, "mapping": mapping})
d = read("doe/audit/demand-support.json"); s = read("doe/doe-result.json"); records = read("propagation/records.json"); review = read("revision/review/result.json")
assert d["input_contract_review_sha256"] == receipt["receipt_sha256"]
assert read("doe/manifest.json")["input_contract_review_sha256"] == canonical_sha256(receipt)
cost = json.loads(COST.read_text(encoding="utf-8"))
a = d["input_assessments"]; rr = [p for x in a for p in x["ranges"]]; comparisons = [x for sink in s["sinks"] for x in sink["data_reviews"]]
counts = {"generated_ir": sum(len(x["instructions"]) for x in cfg["blocks"].values()), "propagation_records": len(records), "upstream_statuses": dict(Counter(d["coverage"]["upstream"].values())),
    "assessments": len(a), "node_kinds": dict(Counter(x["node_kind"] for x in a)), "coverage": dict(Counter(x["coverage"] for x in a)),
    "range_rows": len(rr), "range_statuses": dict(Counter(x["status"] for x in rr)), "assessment_status_sets": dict(Counter("+".join(sorted({p["status"] for p in x["ranges"]})) for x in a)),
    "input_findings": len(d["input_findings"]), "sinks": len(s["sinks"]), "sink_types": dict(Counter(x["boundary"]["sink_type"] for x in s["sinks"])),
    "sensitive_comparisons": len(comparisons), "sensitive_conclusions": dict(Counter(x["conclusion"] for x in comparisons)), "reductions": sum(x["reduction"] is not None for x in comparisons),
    "constraint_statuses": dict(Counter(x["status"] for x in s["constraints"]["checks"].values())), "constraint_preservation_results": len(s["constraints"]["preservation"]),
    "contract_statuses": dict(Counter(x["status"] for x in receipt["checks"])), "diagnostic_codes": dict(Counter(x["code"] for x in d["diagnostics"])),
    "requirement_statuses": dict(Counter(x["status"] for x in d["coverage"]["requirements"].values()))}
assert counts["assessments"] == 92 and counts["range_statuses"] == {"unresolved": 1004, "required": 318}
assert counts["contract_statuses"] == {"unresolved": 4, "accepted": 7} and counts["reductions"] == 0

compact = []
for x in a:
    grouped = {}
    for p in x["ranges"]:
        selector = {k: p[k] for k in ["status", "property", "path", "excluded_paths"]}; key = canonical_sha256(selector)
        grouped.setdefault(key, {**selector, "rows": 0, "demand_refs": [], "contract_refs": [], "diagnostic_refs": []})
        grouped[key]["rows"] += 1
        for field in ["demand_refs", "contract_refs", "diagnostic_refs"]:
            grouped[key][field] = sorted(set(grouped[key][field] + p.get(field, [])))
    compact.append({k: x[k] for k in ["id", "node_kind", "instruction_id", "operation_id", "input_index", "data_ids", "coverage"]} | {"ranges": list(grouped.values())})

crosswalk = []
for ir, lines, expected, role in [("ir_001", [8,8], ["read"], "request acquisition"), ("ir_003", [8,8], ["read"], "environment acquisition"),
        ("ir_005", [9,9], ["deliver","receive"], "first fast invocation"), ("ir_009", [10,10], ["deliver","receive"], "single fast retry site"),
        ("ir_011", [11,12], ["deliver","receive"], "single archive invocation site"), ("ir_024", [16,16], ["write"], "status append")]:
    bid, index, instruction = next((bid,i,irv) for bid,b in cfg["blocks"].items() for i,irv in enumerate(b["instructions"]) if irv["id"] == ir)
    actual = [{"operation_id": f"op_{ir}:e{ei}:a{oi}", "op": op["op"], "inputs": op["inputs"], "outputs": op["outputs"], "alternatives": op.get("alternatives", [])}
              for ei,e in enumerate(records[ir]["events"]) for oi,op in enumerate(e["atomic_ops"]) if op["op"] in expected]
    assert set(expected) <= {x["op"] for x in actual}
    crosswalk.append({"role": role, "source_file": "skill/SKILL.md", "source_lines": lines, "instruction_id": ir,
        "cfg_pointer": f"/blocks/{bid}/instructions/{index}", "upstream_status": d["coverage"]["upstream"][ir], "recorded_operations": actual})
contracts = {x["id"]: x for x in compiled["input_contracts"]}
contract_inventory = [{"contract": contracts[x["contract_id"]], "review": x, "targets": receipt["review_core"]["contract_targets"][x["contract_id"]]} for x in receipt["checks"]]
comparative = [
    {"id": "013-acquisition", "status": "field_demands_present_deletion_unresolved", "source_lines": [8,8], "finding": "Request acquisition retains source_id; environment acquisition retains FAST_KEY presence and value. All five acquisition outputs have unresolved ranges. No source/interface projection capability is established."},
    {"id": "013-fast-first", "status": "represented_with_potential_constraint_findings", "source_lines": [9,9], "finding": "CFG has a structured key-presence gate and preserves the first fast call's inputs. Two saved only_if checks nevertheless return abstract potential_violation. These witnesses do not establish a feasible real call with an absent key or a source defect."},
    {"id": "013-fast-interface", "status": "accepted_required_relation", "source_lines": [9,10], "finding": "All four compiled first/retry request-response contracts are accepted. Whole original source_id and FAST_KEY values are required; each response is tied to its own request/attempt."},
    {"id": "013-retry-control", "status": "constraint_mapping_incomplete_and_local_interface_gap", "source_lines": [10,10], "finding": "At-most-one retry and prior first-attempt/classification constraints are satisfied in the static model. F001 retains a missing true-classification only_if restriction. The classification criterion/error information remains a local unresolved interface relation; the natural retry duty is clear."},
    {"id": "013-fallback-control", "status": "represented_with_unresolved_outcome_relations", "source_lines": [9,11], "finding": "Absent key, first non-transient failure and failed retry have distinct CFG routes to archive. First/retry success discriminator relations remain unresolved. Concrete wire encodings are not supplied; this is not ambiguity about the required fallback behavior."},
    {"id": "013-archive-interface", "status": "accepted_required_relation", "source_lines": [12,15], "finding": "The archive request and paired response contracts are accepted with one whole source_id argument and no FAST_KEY argument. Archive at-most-one and key-forbid constraints are satisfied in the supported model."},
    {"id": "013-success-output", "status": "whole_body_relation_retained_control_unresolved", "source_lines": [13,13], "finding": "Each successful response body remains a whole required value and follows its own predecessor merge. No post-success-fetch constraint violation is established. Outcome discrimination remains an unresolved processing/interface relation."},
    {"id": "013-archive-failure", "status": "semantic_error_identity_clear_physical_selector_unestablished", "source_lines": [14,14], "finding": "Terminal archive error and no further fetch behavior are represented. The selected annotation still reads a concrete error field from ordinary call output; source says the call's error but does not supply this wire layout. Final review did not flag that independent representation concern. It is not a wrong-field defect in the original Skill."},
    {"id": "013-key-ban", "status": "archive_supported_diagnostic_scope_incomplete", "source_lines": [15,15], "finding": "Archive key exclusion is checked satisfied. F002 retains incomplete diagnostic-output scope: the authored restriction covers status.txt only. That narrow satisfied check cannot prove the workflow-wide diagnostic prohibition. Model observations remain recorded and control dependence does not establish plaintext inclusion."},
    {"id": "013-status-append", "status": "action_order_supported_exact_encoding_unspecified", "source_lines": [16,16], "finding": "Append mode and prior-write ordering are represented and checked. Review accepts whole terminal category as sufficient for abstract final status; this is not proof of a concrete serialized status or source-defined extra fields. The exact output encoding remains a genuine local source ambiguity. The selected processing gap no longer mentions an unrelated saved-result association."},
]
chains = {ref for x in a if x["node_kind"] == "op_input" and x["instruction_id"] in {"ir_005","ir_009","ir_011"} for p in x["ranges"] if p["status"] == "required" and p.get("contract_refs") for ref in p["demand_refs"]}
report = {"schema_version": "skillflow-selected-source-comparison-v1", "case": "013", "observed_at": datetime.now(timezone.utc).isoformat(),
    "audit_status": "final_closed_run_read_only", "scope": "Ten source expectations from the finite 26-item small-case inventory. No gold labels, actual execution or new replay.",
    "run_directory": str(RUN).replace("\\", "/"), "result": read("result.json"), "controller": read("controller-finished.json"), "selection": read("selection.json"), "artifacts": artifacts, "counts": counts,
    "receipt": {"pure_load_validation": "passed", "solving_performed": False, "internal_sha256": receipt["receipt_sha256"], "complete_receipt_sha256": canonical_sha256(receipt), "demand_internal_digest_matches": True, "doe_manifest_complete_digest_matches": True, "review_status": receipt["review_status"], "source_review_complete": receipt["source_review_complete"], "binding": receipt["review_core"]["binding"]},
    "source_boundary_crosswalk": crosswalk, "boundary_coverage": {"operation_boundary_sites": 6, "operation_sites_recorded": 6, "return_terminator": {"instruction_id": "ir_025", "source_lines": [13,16], "coverage": d["coverage"]["upstream"]["ir_025"], "record": records["ir_025"], "notice": "The return is a processed CFG terminator with four possible selected values, not an extra tool/sink atomic operation."}},
    "expectation_comparisons": comparative, "contracts": contract_inventory, "review_findings": review["review"]["findings"], "input_assessments_compact": compact,
    "required_contract_derivations": {k:s["derivations"]["demand"][k] for k in sorted(chains)}, "constraints": s["constraints"], "diagnostics": d["diagnostics"],
    "deletion_conclusions": {"certified_ranges": [], "certified_reductions": [], "reason": "Every assessment contains unresolved information. No saved deletable range or reduction exists. Source-independent extra request/environment/response content can remain assessable in principle, but no concrete deletion is certified by this run."},
    "independent_semantic_limits": ["Retry/fallback purpose is explicit; unknown response discrimination/transient classification implementation is an interface relation, not whole-task purpose ambiguity.", "Final-status serialization is a genuine local observable-output ambiguity. Accepted category dependence establishes only the recorded abstract status relation.", "Concrete ['error'] selection remains insufficiently grounded as a physical response path; the semantic identity of the failing call's error is clear.", "Two potential_violation witnesses are abstract behaviors, not actual executed violations or known source-input defects.", "Task source issues and six requirement-expression gaps introduce separate global limitations. Do not blame every unresolved assessment solely on a single local contract gap.", "No field-projection API capability is established and no Skill rewrite is performed."],
    "cost": {"artifact": str(COST.relative_to(ROOT)).replace("\\", "/"), **{k:cost[k] for k in ["status","counts","known_public_usage","categories","timing","http_attempts","provider_billing_cost","usage_notice"]}},
    "limits": ["1322 range entries are derivation rows, not unique fields; 14 sensitive comparisons are not unique leaks.", "Static propagation completion does not prove source semantics, constraint completeness or deletion safety.", "Zero input_findings does not establish that all possible wrong/missing source arguments can be detected.", "No production, prompt, source or run artifact was edited, and no model, Skill or replay was launched by this audit."]}
assert artifacts == [artifact(RUN / rel) for rel in rels] + [artifact(COST)]
report["artifact_stability"] = "All listed artifacts remained byte-identical during this audit."
dest = OUT / "013-final-audit.json"
if dest.exists(): raise RuntimeError("Preserve final audit; use a new filename for corrections")
dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
md = """# 013 selected-run source and input-necessity audit

013 closed **partial** with **25/25 generated IR processed** and partial DOE. All **6/6 finite acquisition/call/append source boundary sites** have static operation records: request read, environment read, first fast call, retry fast call, archive call and status append. The shared return terminator is also processed and has four possible selected values. These are static records, not real Skill executions.

| Saved result | Count |
| --- | ---: |
| Input assessments | 92: 32 IR inputs, 55 operation inputs, 5 acquisition outputs |
| Coverage | 92 processed; 0 not reached |
| Range derivation rows | 1,322: 318 required, 1,004 unresolved, 0 deletable |
| Assessment status combinations | 59 required + unresolved; 33 unresolved only |
| Sinks | 22: 18 model observations, 3 tool deliveries, 1 storage write |
| Sensitive comparisons | 14 no_excess_established; 0 reductions |
| Contract decisions | 7 accepted, 4 unresolved; 0 rejected |
| Constraint decisions | 9 satisfied, 2 potential_violation |
| Input semantic findings | 0 |

All assessments include unresolved information. There is **no certified field/slot deletion example** from this selected run, and the 14 sensitive comparisons are unresolved rather than safe verdicts. Counts are derivation/comparison rows, not distinct fields or leaks.

## Bound receipt and required inputs

The pure receipt loader passed against selected source, CFG, Task, raw/compiled annotation and mapping, without solving or replay. Demand support matches internal receipt SHA `3e7a0af1f811427835cb420531f7c074dfdc557268026fd59d015bfeb67edc50`; the DOE manifest matches the full receipt SHA `86dd841c646ac6699ae69a8a7661044b7d121d59aa4fa626d0667a2f9bfbe0d2`. `source_review_complete=false` remains explicit. All listed input files remained byte-identical during audit.

The six accepted tool contracts are the three actual request/response pairs, not six source calls. Each fast attempt requires whole original source_id and FAST_KEY; archive requires whole source_id only. The pairings retain separate first, retry and archive responses. The seventh accepted contract transfers the abstract final status's whole value to its scalar terminal category. It does not define the serialized status.

Acquisition assessments visibly retain request.source_id, environment.FAST_KEY presence and value, and whole body values from successful responses. The first and archive error selectors remain in the saved annotation. Original reads, tool arguments, response versions and model observations remain facts. No read/server field-projection capability is established.

## Source correctness and limitations

The retry/fallback **Task obligation is clear**. The four unresolved contracts concern concrete first/retry/archive outcome discrimination and transient-error classification. Those are local processing/interface relations, distinct from uncertainty about task purpose. Supported semantic outcome cases need not invent a response discriminator field. The existing Task marks transient classification as an issue, and its global policy plus six requirement-expression gaps contribute additional global barriers; the unresolved range count must not be attributed to one local contract alone.

Final review F001 retains a missing true-transient `only_if` restriction for the retry: at-most-one and prior classification alone do not express which classification outcome permits retry. F002 retains incomplete diagnostic-output prohibition: only status.txt is covered. Four further findings preserve the unresolved contracts. The saved archive-key prohibition is satisfied in its modeled scope; the status-only check does not prove the workflow-wide diagnostic ban.

The nine satisfied constraints cover modeled bounds/order/forbidden flows. Two key-presence `only_if` checks return **potential_violation** with abstract witnesses despite the authored CFG gate. They do not demonstrate a feasible real invocation with an absent key, and must not be reported as actual Skill violations. No deletion preservation checks exist because no reduction was emitted.

Two independent provisional concerns remain relevant. The selected annotation still uses a concrete `['error']` field for a semantically described call error without a supplied physical response schema; final review does not flag this mapping concern. The source's final-status contents/serialization remain a genuine local output ambiguity even though the abstract category transfer is accepted. Append mode and append-before-return remain explicit. The revised processing gap removed the hypothetical unrelated saved-result association.

## Closure and cost

The sole replay matched in **9.5149 seconds**, with **zero new native starts**. The final separate cost audit records **12 native starts** (7 normal + 4 semantic-repair + 1 structural-correction), all with complete public usage, totaling **393,374 tokens** (344,678 input + 48,696 output). Outer retries were zero; one internal reconnect notice was observed. Provider HTTP attempts and billing remain unknown. Analysis took 1,317.207 seconds.

The adjacent JSON covers all ten prewritten source expectations, exact contract decisions and references, input range summaries, source-boundary crosswalk, constraints, diagnostics and artifact hashes. This finite comparison is not a gold benchmark or precision/recall result. Earlier provisional files are preserved; no production or run material was changed.
"""
(OUT / "013-final-audit.md").write_text(md,encoding="utf-8")
print(json.dumps({"saved":str(dest),"receipt_validation":"passed","counts":counts,"artifacts_unchanged":True}))
