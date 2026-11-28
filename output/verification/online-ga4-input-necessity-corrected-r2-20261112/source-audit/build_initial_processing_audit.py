"""Summarize saved processing records with stdlib only; no analysis replay."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[3]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209"
CALL = RUN / "steps/processing/calls/a001"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value, path):
    if isinstance(value, dict):
        yield path, value
        for name, child in value.items():
            yield from walk(child, path + "/" + str(name))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + "/" + str(index))


def main():
    processing = read(CALL / "response.json")
    processing = json.loads(processing) if isinstance(processing, str) else processing
    validation = read(CALL / "validation.json")
    cfg = read(RUN / "graph/initial.json")["cfg"]
    irs = {i["id"]: i for b in cfg["blocks"].values() for i in b["instructions"]}
    diagnostics = validation["diagnostics"]
    mechanisms = [d for d in diagnostics if d["code"] == "mechanism_evidence_reference"]
    mechanism_rows = []
    for d in mechanisms:
        ir = d["path"].split("/")[2]
        spec = processing["ir_semantics"][ir]
        evidences = spec.get("evidences", [])
        assert evidences and all(set(e) == {"rule_id"} for e in evidences)
        mechanism_rows.append({"instruction_id": ir, "opcode": irs[ir]["opcode"],
            "path": d["path"], "evidences": evidences,
            "reason": "The local mechanism cites only a generic runtime rule. The current interface requires a source-file or CFG-target mechanism reference in addition to any rule citation."})
    coverage = next(d["context"] for d in diagnostics if d["code"] == "instruction_coverage")
    modeled, isolated, allowed = (set(coverage["current"]["modeled"]),
        set(coverage["current"]["unmodeled"]), set(coverage["allowed"]))
    raw_unmodeled = {g["instruction_id"] for g in processing["processing_gaps"] if g.get("unmodeled")}
    raw_specs = set(processing["ir_semantics"])
    raw_walk = list(walk(processing["ir_semantics"], "/ir_semantics"))
    ops = [(path, item) for path, item in raw_walk if "op" in item]
    attachments = [(path + "/" + name, item[name]) for path, item in raw_walk
        for name in ("demand_transfer", "input_contract") if name in item]
    transfer_rows = [(path, item) for path, item in attachments if path.endswith("/demand_transfer")]
    tool_rows = [(path, item) for path, item in attachments if path.endswith("/input_contract")]
    raw_inputs_mismatched = []
    for path, op in ops:
        if "demand_transfer" in op:
            for index, rule in enumerate(op["demand_transfer"]["rules"]):
                if sorted(i["input_index"] for i in rule["inputs"]) != list(range(len(op.get("inputs", [])))):
                    raw_inputs_mismatched.append(path + f"/demand_transfer/rules/{index}")
        if "input_contract" in op and sorted(i["input_index"] for i in op["input_contract"]["inputs"]) != list(range(len(op.get("inputs", [])))):
            raw_inputs_mismatched.append(path + "/input_contract")
    carry_rows = []
    for ir in ("ir_103", "ir_126"):
        spec = processing["ir_semantics"][ir]
        assert irs[ir]["opcode"] == "carry_filter_accumulator"
        assert not spec.get("segments")
        assert spec["output_bindings"] == [{"output_index": 0, "value": {"kind": "input", "index": 0}}]
        carry_rows.append({"instruction_id": ir, "cfg_opcode": irs[ir]["opcode"], "processing": spec,
            "assessment": "direct_identity_binding_no_compute_or_observation_added"})
    schema_findings = [
        {"instruction_id": "ir_114", "opcode": irs["ir_114"]["opcode"], "count": 1,
            "path": "/ir_semantics/ir_114/segments/0/ops/0/demand_transfer/rules/0/inputs/0/reason",
            "diagnosis": "The first input-requirement row omits its mandatory reason. It does contain a separate concrete gap explaining dynamic slice indices; that gap's reason does not fill the row-level reason field.",
            "classification": "contract_record_schema_error", "source_relation": "storage.ts:141-143 slices the sorted paths with a dynamic limit; the semantic dynamic-selection claim still requires review."},
        {"instruction_id": "ir_119", "opcode": irs["ir_119"]["opcode"], "count": 3,
            "path": "/ir_semantics/ir_119/segments/0/cases/1/segments/1",
            "diagnosis": "The listed branch nests a second cases object inside its segments list. That list admits ordinary processing segments, so kind/output/cases are three forbidden keys of the same misplaced nested-case object.",
            "classification": "segment_shape_error", "source_relation": "storage.ts:123-145 and155-159 describe listing/filtering/joining/sorting; these three diagnostics do not establish three separate source defects."},
        {"instruction_id": "ir_173", "opcode": irs["ir_173"]["opcode"], "count": 1,
            "path": "/ir_semantics/ir_173/segments/0/ops/1/demand_transfer/rules/0/inputs/0",
            "diagnosis": "The row declares remainder=unresolved but supplies only an unresolved_ranges/value gap and no row-level gap. The schema requires a concrete gap for an unresolved remainder; scoped ranges are a separate coordinate.",
            "classification": "inconsistent_gap_scope_record", "source_relation": "reports.ts:104 conditionally preserves only a string dateRange as the save label. Its supplied gap is specifically type-conditioned value dependence, not generic black-box uncertainty; validity of that claimed expressiveness limit is a later semantic-review question."}]
    compact_diagnostics = [{key: d[key] for key in ("code", "path", "message")} for d in diagnostics]
    report = {"identity": "ga4-r2-initial-processing-audit-v1", "status": "provisional_invalid_initial_processing",
        "created_at": datetime.now(timezone.utc).isoformat(), "run_directory": str(RUN),
        "identities": {"saved_response_identity": validation["response_sha256"],
            "response_file_sha256": sha(CALL / "response.json"), "validation_file_sha256": sha(CALL / "validation.json"),
            "canonical_cfg_file_sha256": sha(RUN / "graph/initial.json")},
        "saved_validation_status": validation["status"],
        "diagnostic_counts": dict(Counter(d["code"] for d in diagnostics)),
        "schema_findings": schema_findings, "mechanism_findings": mechanism_rows,
        "mechanism_counts": {"by_rule": dict(Counter(row["evidences"][0]["rule_id"] for row in mechanism_rows)),
            "by_cfg_opcode": dict(Counter(row["opcode"] for row in mechanism_rows))},
        "coverage": {"actual_cfg_ir": len(irs), "raw_specifications": len(raw_specs),
            "raw_processing_gaps": len(processing["processing_gaps"]),
            "raw_explicit_unmodeled_ids": sorted(raw_unmodeled),
            "raw_missing_spec_ids": sorted(set(irs)-raw_specs), "raw_extra_spec_ids": sorted(raw_specs-set(irs)),
            "raw_modeled_unmodeled_overlap": sorted(raw_specs & raw_unmodeled),
            "saved_normalized_modeled_count": len(modeled), "saved_normalized_unmodeled_ids": sorted(isolated),
            "saved_modeled_unmodeled_overlap": sorted(modeled & isolated),
            "saved_uncovered_ids": sorted(allowed-modeled-isolated),
            "diagnosis": "ir_179 is both a modeled evidence-only placeholder and an explicit unmodeled gap. The invalid ir_114/ir_119/ir_173 records are additionally isolated by validation. Every actual IR occurs in the modeled/unmodeled union, but exact-one coverage fails at ir_179; it is not simply a missing two-row problem."},
        "raw_contract_inventory": {"note": "Counts are syntactic inspection of invalid raw JSON, not accepted inventory or contract-review coverage.",
            "compute_operations": sum(op["op"] == "compute" for _, op in ops),
            "inline_expression_compute_operations": sum(op["op"] == "compute" and "expression" in op for _, op in ops),
            "demand_transfer_attachments": len(transfer_rows),
            "demand_transfer_rules": sum(len(item["rules"]) for _, item in transfer_rows),
            "tool_input_contract_attachments": len(tool_rows),
            "ir_with_contract_attachments": len({path.split("/")[2] for path, _ in attachments}),
            "raw_missing_compute_attachment_without_expression": [path for path, op in ops if op["op"] == "compute" and "expression" not in op and "demand_transfer" not in op],
            "raw_missing_call_deliver_attachment": [path for path, op in ops if op["op"] in {"call", "deliver"} and "input_contract" not in op],
            "raw_input_index_coverage_mismatches": raw_inputs_mismatched,
            "official_inventory_status": "not_completed_because_prior_validation_diagnostics_exist"},
        "carry_bindings": carry_rows,
        "id_clarification": {ir: irs[ir]["opcode"] for ir in ("ir_100", "ir_103", "ir_114", "ir_119", "ir_122", "ir_123", "ir_126", "ir_136", "ir_173")},
        "explicit_unmodeled_claims": [g for g in processing["processing_gaps"] if g.get("unmodeled")],
        "compact_saved_diagnostics": compact_diagnostics,
        "limitations": ["The 63 rule-only evidence errors do not establish 63 incorrect semantic mechanisms.",
            "Contract attachment presence and input-index enumeration do not establish necessity, sufficiency, source fidelity or correct local gaps.",
            "Explicit unmodeled claims identify a helper expansion gap and absent optional values; the source review must assess whether these are genuine supported limits or repairable representation errors.",
            "The allowed structural correction can supersede this candidate. No selected processing, propagation, input assessment or DOE conclusion is established here."],
        "execution": {"model_calls": 0, "skill_executions": 0, "analysis_function_invocations": 0,
            "renderer_or_backend_runs": 0, "replays": 0, "production_or_run_edits": 0}}
    with (BASE / "initial-processing-audit.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    markdown = """# Initial processing candidate audit (provisional)

The first processing response was rejected with **69 diagnostics: five schema, one instruction coverage and 63 mechanism-evidence references**. Response identity: `c7e575530a7399cb264a15d9581786968bfc34a82e4914c40d5fe828d8f48465`. The following describes this rejected candidate only.

## Local diagnostic causes

| Location | Cause | Interpretation |
| --- | --- | --- |
| `ir_114`, slice input requirement | Missing mandatory row-level `reason`; a separate dynamic-slice gap exists. | One contract schema error, not proof of missing source semantics. |
| `ir_119`, listed case's second segment | A nested `cases` object sits in a list of ordinary processing segments; `kind`, `output`, `cases` are rejected. | Three diagnostics for one segment-shape error. |
| `ir_173`, save-label input requirement | `remainder=unresolved` lacks its required row-level gap; only a scoped value gap is supplied. | One inconsistent gap-scope record. The supplied type-conditioned rationale is concrete but still needs semantic review. |
| `ir_179` coverage | Both an evidence-only modeled placeholder and explicit unmodeled gap. | Exact-one coverage fails; no CFG IR is wholly absent from the saved modeled/unmodeled union. |

All 63 mechanism-reference errors cite only runtime rules: **40 EM17, 22 EM16 and one EM14**. A local mechanism additionally needs a source-file or CFG-target reference. The affected CFG opcodes are **26 dispatch, 21 merge, ten member and six append**. These are traceability failures; they do not by themselves establish 63 wrong semantic operations.

## Coverage and contract inventory

The raw response has **561 IR specifications and 13 processing gaps** for the 563-IR graph. Three gaps explicitly mark `ir_179`, `ir_419`, `ir_423` unmodeled. Only `ir_419`/`ir_423` lack raw specification rows; `ir_179` is duplicated across modeled/unmodeled coverage. Validation also isolates the three malformed records `ir_114`, `ir_119`, `ir_173`, yielding 558 modeled IDs and six unmodeled IDs with the same one-ID overlap. Do not report either count as successful backend coverage.

Raw syntax contains **124 compute operations: nine inline expressions and 115 demand-transfer attachments containing 117 rules**. It also contains **26 tool-input contract attachments**, for **123 distinct IR with any contract attachment**. Every raw compute has an attachment or inline expression, and every raw call/deliver has an attachment. The JSON receipt reports input-index enumeration checks. These counts do not establish valid or complete semantic contracts: the official obligation inventory is gated behind the current validation errors and has not completed.

The explicitly unmodeled claims concern a fresh helper-call expansion at `ir_179`, and absent JavaScript undefined values on optional inspection-result branches at `ir_419`/`ir_423`. They contain specific output/input representational reasons, rather than generic opacity; review must still distinguish genuine supported limits from repairable representation errors.

## Carry instructions

The actual added carry IRs are **`ir_103` and `ir_126`**. Both bind output 0 directly to input 0, with no compute or observation operation, satisfying the identity-binding concern from the selected-graph audit at the submitted syntax level. `ir_100`/`ir_123` are the header merges; `ir_114` is slice, `ir_122` dispatch, and `ir_136` an input-range acquisition. No outcome is inferred from stale pre-correction instruction numbers.

The structural correction is still allowed to supersede this response. This audit used only saved JSON and implementation/source text, without calling validation/analysis functions, a model, Skill, renderer, backend or replay. It changed no production or active-run file. Exact diagnostics, local evidence, hashes and counts are in `initial-processing-audit.json`.
"""
    with (BASE / "initial-processing-audit.en.md").open("x", encoding="utf-8") as handle:
        handle.write(markdown)
    print(json.dumps({"diagnostic_counts": report["diagnostic_counts"], "coverage": report["coverage"],
        "raw_contract_inventory": report["raw_contract_inventory"], "audit_sha256": sha(BASE / "initial-processing-audit.json")}, indent=2))


if __name__ == "__main__":
    main()
