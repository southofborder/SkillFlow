"""Summarize saved artifacts, without importing SkillFlow or executing a run."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


def canon(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                     allow_nan=False).encode("utf-8")).hexdigest()


def row_counts(rows, field):
    return dict(Counter(row.get(field, "unspecified") for row in rows))


def rows(value):
    return value if isinstance(value, list) else []


class Saved:
    def __init__(self, run):
        self.run = run.resolve(strict=True)
        self.cache = {}
        self.refs = {}
        self.read_errors = []

    def get(self, name):
        if name not in self.cache:
            path = (self.run / name).resolve()
            if not path.is_relative_to(self.run):
                raise ValueError("Artifact owner escapes the run: " + name)
            self.cache[name] = None
            try:
                content = path.read_bytes()
                self.cache[name] = json.loads(content.decode("utf-8-sig"))
                self.refs[name] = {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            except FileNotFoundError:
                pass
            except (OSError, UnicodeError, ValueError) as exc:
                self.read_errors.append({"path": name, "reason": str(exc)})
        return self.cache[name]

    def selection_record(self, selection, field):
        ref = selection.get(field)
        if not ref:
            return None
        value = self.get(ref["path"])
        return {"path": ref["path"], "sha256": ref["sha256"], "pin_matches":
                value is not None and self.refs[ref["path"]]["sha256"] == ref["sha256"]}


def cfg_ops(cfg):
    if cfg is None:
        return {}
    return {row["id"]: row for block in cfg["blocks"].values() for row in block["instructions"]}


def cfg_summary(saved, name):
    data = saved.get(name)
    if data is None:
        return None, None
    cfg = data["cfg"]
    return cfg, {"file": name, "file_sha256": saved.refs[name]["sha256"], "cfg_sha256": canon(cfg),
                 "blocks": len(cfg["blocks"]), "instructions": len(cfg_ops(cfg)), "edges": len(cfg["edges"])}


def record_diff(old, new):
    removed, added = old.keys() - new.keys(), new.keys() - old.keys()
    same_keys = old.keys() & new.keys()
    changed = sorted(key for key in same_keys if old[key] != new[key])
    return {"unchanged": len(same_keys) - len(changed), "changed": changed, "added": sorted(added),
            "removed": sorted(removed)}


def graph_repair(saved):
    material = saved.get("graph/revision-input.json")
    result = saved.get("steps/revision-graph/result.json")
    compiled = saved.get("steps/revision-graph/value.json")
    call = saved.get("steps/revision-graph/calls/a001/call.json")
    raw = saved.get("steps/revision-graph/calls/a001/response.json")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            raw = None
    plan = ((material or {}).get("repair") or {}).get("plan")
    diagnostics = (compiled or {}).get("assembly", {}).get("patch_diagnostics")
    submitted = raw.get("updates") if isinstance(raw, dict) else None
    if not any((plan, result, compiled, call)):
        return None
    return {
        "mode": (plan or {}).get("mode"), "plan_sha256": (plan or {}).get("plan_sha256"),
        "slots": len(plan["slots"]) if plan is not None else None,
        "slots_by_kind": row_counts(plan["slots"].values(), "kind") if plan is not None else None,
        "unaddressable_findings": (plan or {}).get("unaddressable_findings"),
        "plan_matches_reply": raw.get("plan_sha256") == plan["plan_sha256"]
        if plan and isinstance(raw, dict) and "plan_sha256" in raw else None,
        "call_status": (call or {}).get("status"), "compiled": compiled is not None,
        "submitted_update_rows": len(submitted) if isinstance(submitted, list) else None,
        "patch_diagnostics": diagnostics, "result_status": (result or {}).get("status"),
        "note": "Submitted updates may be rejected, be no-ops, or have no selected revised bundle.",
    }


def stage_result_status(result):
    if result is None:
        return "not_run_or_pending"
    return result.get("status") or ("complete" if result.get("accepted_call") else "unspecified")


def processing_summary(saved, stage):
    prefix = f"steps/{stage}"
    value, result = saved.get(f"{prefix}/value.json"), saved.get(f"{prefix}/result.json")
    if value is None:
        return None, None if result is None else {"status": stage_result_status(result)}
    gaps = rows(value.get("processing_gaps"))
    records = value.get("ir_semantics", {})
    return value, {
        "status": stage_result_status(result), "accepted_call": (result or {}).get("accepted_call"),
        "modeled_ir": len(records), "locations": len(value.get("locations", {})),
        "explicit_gap_rows": len(gaps), "explicit_unmodeled": sorted({row["instruction_id"] for row in gaps if row.get("unmodeled")}),
        "isolated_validation_gaps": (result or {}).get("validation_gaps"),
        "structural_corrections": (result or {}).get("counts", {}).get("structural_corrections"),
    }


def processing_diff(before, after, scope):
    if before is None or after is None:
        return None
    delta = record_diff(before["ir_semantics"], after["ir_semantics"])
    delta["locations_changed"] = before.get("locations") != after.get("locations")
    delta["expressions_changed"] = before.get("expressions") != after.get("expressions")
    if scope:
        slots = scope["slots"]
        tracked = set(slots) | set(scope["removed_instruction_ids"])
        delta["diff_outside_signed_or_retired_ir"] = sorted(
            set(delta["changed"] + delta["added"] + delta["removed"]) - tracked)
    return delta


def review_summary(saved, owner):
    value, material = saved.get(f"{owner}/result.json"), saved.get(f"{owner}/inputs.json")
    if value is None and material is None:
        return None
    payload = (value or {}).get("review") or {}
    inventory = (material or {}).get("input_contract_inventory")
    obligations = scopes = omitted = decisions = None
    checks = rows(payload.get("input_contract_checks"))
    if inventory is not None and inventory["available"]:
        obligations = {row["id"] for row in inventory["obligations"]}
        layouts = {row["obligation_id"]: {s["id"] for s in row["scopes"]} for row in inventory["contracts"]}
        scopes = set().union(*layouts.values())
        omitted = obligations - {row["obligation_id"] for row in checks}
        decisions = {}
        for row in checks:
            if row.get("scope_checks"):
                for group in row["scope_checks"]:
                    for sid in group["scope_ids"]:
                        decisions[sid] = group["status"]
            elif row["status"] == "accepted":
                for sid in layouts.get(row["obligation_id"], []):
                    decisions[sid] = "accepted"
    findings = rows(payload.get("findings"))
    review_material = (material or {}).get("input_contract_binding")
    return {
        "owner": owner, "status": stage_result_status(value), "diagnostic_only": (value or {}).get("diagnostic_only"),
        "obligations": len(obligations) if obligations is not None else None,
        "scopes": len(scopes) if scopes is not None else None,
        "checks": len(checks) if value is not None else None,
        "check_statuses": row_counts(checks, "status") if value is not None else None,
        "scope_statuses": dict(Counter(decisions.values())) if value is not None and decisions is not None else None,
        "missing_obligations": len(omitted) if value is not None and omitted is not None else None,
        "scopes_without_decision": len(scopes - decisions.keys()) if value is not None and scopes is not None else None,
        "findings": len(findings) if value is not None else None,
        "findings_by_domain": row_counts(findings, "domain") if value is not None else None,
        "source_input_findings": len(rows(payload.get("source_input_findings"))) if value is not None else None,
        "binding": review_material,
    }


def selected_review(saved, summaries, demand):
    receipt = saved.get("audit/input-contract-review.json")
    if receipt is None:
        return None
    core = receipt["review_core"]
    bound = []
    for summary in summaries:
        if summary is None or summary["binding"] != core["binding"]:
            continue
        value = saved.get(summary["owner"] + "/result.json") or {}
        review = value.get("review") or {}
        if (value.get("status") == core["status"] and review.get("findings", []) == core["findings"]
                and review.get("input_contract_checks", []) == core["checks"]):
            bound.append(summary["owner"])
    return {"status": receipt["review_status"], "complete_for_selected_bundle": receipt["source_review_complete"],
            "matching_review_owners": bound, "partial_material": core["partial"], "availability": core["availability"],
            "checks": len(receipt["checks"]), "check_statuses": row_counts(receipt["checks"], "status"),
            "scope_statuses": row_counts(core["scope_decisions"].values(), "status"), "findings": len(core["findings"]),
            "findings_by_domain": row_counts(core["findings"], "domain"),
            "barrier_count": len(core.get("validation_barriers", [])),
            "receipt_sha256": receipt["receipt_sha256"],
            "receipt_digest_matches": receipt["receipt_sha256"] == canon(
                {key: value for key, value in receipt.items() if key != "receipt_sha256"}),
            "demand_receipt_matches": demand is not None and demand.get("input_contract_review_sha256") == receipt["receipt_sha256"]
            if demand is not None else None}


def propagation_summary(saved):
    report = saved.get("propagation/manifest.json")
    if report is None:
        return None
    diags = rows(report.get("diagnostics"))
    records = saved.get("propagation/records.json")
    return {"status": report["status"], "coverage": dict(Counter(report["coverage"].values())),
            "nonprocessed": {key: status for key, status in report["coverage"].items() if status != "processed"},
            "diagnostics_by_code": row_counts(diags, "code"),
            "typed_operation_faults": [row for row in diags if row["code"] == "operation_execution_error"],
            "missing_part_cases": [row for row in diags if row["code"] == "missing_part"],
            "ir_with_record": len(records) if records is not None else None}


def demand_summary(demand):
    if demand is None:
        return None
    assessments = demand["input_assessments"]
    statuses = Counter(row["status"] for item in assessments for row in item["ranges"])
    per_kind = {k: row_counts((row for item in assessments if item["node_kind"] == k for row in item["ranges"]), "status")
                for k in sorted({item["node_kind"] for item in assessments})}
    diags = demand["diagnostics"]
    output_gaps = [row for row in diags if row["code"] == "input_contract_output_gap"]
    return {
        "status": demand["status"], "assessment_count": len(assessments),
        "assessment_node_kinds": row_counts(assessments, "node_kind"),
        "assessment_coverage": row_counts(assessments, "coverage"),
        "range_statuses": {"required": 0, "unresolved": 0, "deletable": 0, **statuses},
        "range_statuses_by_kind": per_kind, "input_findings": row_counts(demand["input_findings"], "kind"),
        "deletable_ranges": [{"assessment_id": item["id"], "instruction_id": item["instruction_id"], "range": row}
                            for item in assessments for row in item["ranges"] if row["status"] == "deletable"],
        "diagnostics_by_code": row_counts(diags, "code"),
        "global_blocking_by_code": row_counts((row for row in diags if row.get("blocking") and row.get("instruction_id") is None), "code"),
        "output_contract_gaps": len(output_gaps), "output_contract_gap_ir": sorted({row["instruction_id"] for row in output_gaps}),
        "requirement_statuses": row_counts(demand["coverage"]["requirements"].values(), "status"),
    }


def doe_summary(saved):
    result = saved.get("doe/doe-result.json")
    if result is None:
        return None
    comparisons = [row for sink in result["sinks"] for row in sink["data_reviews"]]
    return {"status": result["status"], "sinks": len(result["sinks"]), "comparison_count": len(comparisons),
            "comparison_conclusions": row_counts(comparisons, "conclusion"),
            "non_null_reductions": sum(row.get("reduction") is not None for row in comparisons),
            "diagnostics_by_code": row_counts(result["diagnostics"], "code")}


def report(run):
    saved = Saved(run)
    result = saved.get("result.json") or {}
    selected_pin = saved.get("selection.json") or {}
    initial, initial_stats = cfg_summary(saved, "graph/initial.json")
    revised, revised_stats = cfg_summary(saved, "graph/revision.json")
    selected, selected_stats = cfg_summary(saved, "graph/selected.json")
    before, before_stats = processing_summary(saved, "processing")
    after, after_stats = processing_summary(saved, "revision-processing")
    scope = saved.get("revision/processing-scope.json")
    reviews = [review_summary(saved, owner) for owner in ("review", "revision/review")]
    demand = saved.get("doe/audit/demand-support.json")
    return {
        "identity": "skillflow-saved-backend-audit-v1", "run_directory": str(saved.run),
        "status": result.get("status", "not_run"), "stage": result.get("stage"), "stages": result.get("stages"),
        "initial_cfg": initial_stats, "revised_cfg": revised_stats, "selected_cfg": selected_stats,
        "initial_cfg_published_unchanged": selected == initial if initial is not None and selected is not None else None,
        "selected_instruction_diff_vs_initial": record_diff(cfg_ops(initial), cfg_ops(selected))
        if initial is not None and selected is not None else None,
        "selection": {field: saved.selection_record(selected_pin, field) for field in ("cfg", "task", "annotation")},
        "shared_repair_used": result.get("repair_used"),
        "shared_repair_decision": saved.get("audit/shared-repair-decision.json"),
        "graph_repair": graph_repair(saved), "repair_review": result.get("repair_review"),
        "processing": {"original": before_stats, "revised": after_stats, "scope_slots": len(scope["slots"]) if scope else None,
                       "scope_sha256": (scope or {}).get("scope_sha256"), "scope_unresolved_targets": (scope or {}).get("unresolved_targets"),
                       "diff": processing_diff(before, after, scope)},
        "original_review": reviews[0], "revised_review": reviews[1],
        "selected_review_receipt": selected_review(saved, reviews, demand),
        "propagation": propagation_summary(saved), "demand": demand_summary(demand), "doe": doe_summary(saved),
        "interpretation": [
            "Null means no readable saved artifact. For an active run a null may be pending; explicit status is in the stage ledger.",
            "Processed IR or a boundary record denotes abstract reach. It does not establish source-semantic correctness.",
            "Input assessment ranges count use sites and properties; they do not count distinct fields. No excess established does not prove all inputs necessary.",
            "This analysis summarizes saved receipts only. It did not execute a Skill, call a model, or replay a run.",
        ],
        "evidence": saved.refs, "read_errors": saved.read_errors,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(report(args.run), indent=2, ensure_ascii=True, allow_nan=False), file=sys.stdout)
