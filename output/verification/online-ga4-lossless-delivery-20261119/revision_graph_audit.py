"""Read-only audit of saved graph-revision artifacts. No SkillFlow imports."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parents[2]
RUN = PROJECT / "experiments/doe/runs/document-guided-ga4-lossless-delivery-high-20261122-211742"


def read(path):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    return json.loads(value) if isinstance(value, str) else value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts(cfg):
    return {"blocks": len(cfg["blocks"]), "instructions": sum(len(b["instructions"]) for b in cfg["blocks"].values()),
            "edges": len(cfg["edges"])}


def main():
    plan = read(RUN / "graph/revision-input.json")["repair"]["plan"]
    patch = read(RUN / "steps/revision-graph/calls/a001/response.json")
    validation = read(RUN / "steps/revision-graph/calls/a001/validation.json")
    value = read(RUN / "steps/revision-graph/value.json")
    initial = read(RUN / "graph/initial.json")["cfg"]
    selected = read(RUN / "graph/selected.json")["cfg"]
    scope = read(RUN / "revision/processing-scope.json")
    processing_manifest = read(RUN / "steps/revision-processing/manifest.json")
    call = read(RUN / "steps/revision-graph/calls/a001/call.json")
    preflight = read(next((RUN / "transport/revision-graph").rglob("preflight.json")))
    decision = read(RUN / "audit/shared-repair-decision.json")
    run_result = read(RUN / "result.json")
    source_audit = read(BASE / "initial-source-correctness-audit.json")
    source_audit_checks = [{"path": path, "recorded_sha256": digest, "actual_sha256": sha(RUN / path),
                            "matches": sha(RUN / path) == digest} for path, digest in source_audit["artifact_sha256"].items()]
    source_file_checks = [{"path": path, "matches": sha(RUN / "source/inputs/package" / path) == digest}
                          for path, digest in source_audit["source_file_sha256"].items()]
    assert all(row["matches"] for row in source_audit_checks + source_file_checks)
    assert patch["plan_sha256"] == plan["plan_sha256"]
    assert initial == value["cfg"] == selected
    assert scope["old_cfg_sha256"] == scope["new_cfg_sha256"] == value["assembly"]["cfg_sha256"]
    assert len(plan["slots"]) == 13 and len(patch["updates"]) == 2
    assert len(value["assembly"]["patch_diagnostics"]) == 2
    assert all(not slot["changed_cfg"] for slot in scope["slots"].values())
    assert processing_manifest["context"]["cfg_path"]["path"] == "../../graph/initial.json"
    rows = []
    for index, update in enumerate(patch["updates"]):
        slot = plan["slots"][update["slot_id"]]
        blocks = update["value"]["blocks"]
        rows.append({"update_index": index, "slot_id": update["slot_id"], "target": slot["target"],
                     "value_type": "object", "value_keys": list(update["value"]),
                     "proposed_blocks": [{"ref": b["ref"], "operations": [{"ref": op["ref"], "opcode": op["opcode"]} for op in b["operations"]],
                                           "exit_kind": b["exit"]["kind"]} for b in blocks],
                     "observed_result": "rejected_before_region_block_validation",
                     "diagnostic": value["assembly"]["patch_diagnostics"][index],
                     "static_action_preservation_check": {
                         "root_operations_equal_old": blocks[0]["operations"] == slot["old_value"]["operations"],
                         "added_block_operation_counts": [len(b["operations"]) for b in blocks[1:]],
                         "interpretation": "Even a correctly shaped array with these actions would violate graph_slots.py:281-284. This is a direct comparison against the frozen rule, not an executed alternate patch or validation replay."}})
    report = {
        "identity": "lossless-delivery-saved-revision-graph-audit-v1", "observed_at": datetime.now(timezone.utc).isoformat(),
        "run_directory": str(RUN), "run_stage_at_observation": run_result["stage"],
        "method": "Read saved JSON and implementation text only; no model, Skill, pipeline, renderer, validation function, probe, replay, or runtime mutation.",
        "artifact_hashes": {f: sha(RUN / f) for f in ["graph/initial.json", "graph/selected.json", "graph/revision-input.json",
                         "steps/revision-graph/value.json", "steps/revision-graph/result.json", "steps/revision-graph/calls/a001/response.json",
                         "steps/revision-graph/calls/a001/validation.json", "revision/processing-scope.json", "steps/revision-processing/manifest.json"]},
        "plan": {"identity": plan["identity"], "plan_sha256": plan["plan_sha256"], "slot_count": len(plan["slots"]),
                 "slot_kinds": dict(Counter(v["kind"] for v in plan["slots"].values())),
                 "slots": [{k: v[k] for k in ["slot_id", "kind", "target", "finding_ids"]} for v in plan["slots"].values()],
                 "findings": plan["remaining_findings"], "unaddressable_findings": plan["unaddressable_findings"]},
        "response": {"plan_identity_matches": True, "outer_validation": validation, "updates_returned": len(rows),
                     "updates_applied": 0, "updates": rows,
                     "unchanged_field_slots": [k for k, v in plan["slots"].items() if v["kind"] == "field"],
                     "interpretation": "There is no requirement to fill all 13 slots. Eleven field slots were untouched; two region updates were locally rejected. In particular F001 received no update. No signed-scope or identity violation occurred."},
        "partial_reason": {
            "observed": "Both value objects wrap a blocks array, while _region_changes requires the value itself to be a nonempty list. The errors are quarantined into assembly.patch_diagnostics; the accepted CFG remains available. Runner reports partial from local_gap.",
            "locations": ["src/skillflow/document_guided/graph_slots.py:260", "src/skillflow/document_guided/graph_slots.py:386", "src/skillflow/document_guided/runner.py:462", "src/skillflow/document_guided/runner.py:614"],
            "outer_valid_is_not_patch_success": True,
            "max_corrections": 0,
            "source_findings_resolved_by_graph_patch": 0},
        "static_contract_limit": {
            "finding": "The region contract only permits topology changes preserving original root actions exactly and no operations in added blocks. F002 asks to split one mapping into a guarded clock read, ISO conversion and predecessor-selected timestamp. The returned decomposition cannot pass that contract merely by removing its object wrapper.",
            "rule": "src/skillflow/document_guided/graph_slots.py:281-284",
            "prompt_gap": "The actual graph-update prompt renders only Update.value:JSON, the signed plan and boundary prose. It does not describe the required array shape, the Block grammar, or the rule prohibiting new/moved actions.",
            "prompt_builder": "src/skillflow/document_guided/prompts.py:291-299",
            "field_slot_limit": "For each challenged instruction, field slots permit only opcode, inputs, outputs, constraints and source. They cannot add a producer, guarded acquisition, conversion or merge operation, add blocks, or change the exit. Relabeling the old operation or its runtime-clock resource cannot implement the requested source control/data split.",
            "action_preserving_cfg_only_alternative": "No action-preserving topology-only edit can satisfy F002's exact requested decomposition: the old mapping remains executed in the root before its exit; new blocks may contain no operations, and the field slots cannot insert operations or split effects. This conclusion is specific to the issued slots and the explicit F002 requirements, not a claim that no alternative overall representation exists.",
            "processing_ownership_alternative": {
                "available_scope": ["ir_260", "ir_272"],
                "existing_location": "clock",
                "current_processing": "Both selected records currently use only response and URL in opaque compute, then overwrite type; neither reads the existing clock location. Their demand-transfer prose calls the time fallback a limitation.",
                "possible_owner": "Processing owns the internal operation effects and already has case segments, read, compute and build/update primitives. Both IR are writable in the 27-IR processing revision scope, and the existing task-local runtime clock location can be referenced without creating a shared location. A producer could describe source-backed nonfallback and fallback cases and place an actual clock read/conversion only in the fallback case, preserving its source, output version and demand contract.",
                "qualification": "This is a representational option from static inspection, not an implemented/validated fix or prediction of the running response. Whether the finite case model captures the needed guard/quality relationship must still be checked. It does not itself satisfy the reviewer's separate demand for exposed CFG nodes or authorize clearing F002 without source re-review."},
            "evidence_status": "Static inspection of the submitted patch and frozen code; no alternate patch was tested or applied."},
        "cfg": {"before": counts(initial), "revision_output": counts(value["cfg"]), "selected_at_observation": counts(selected),
                "all_three_objects_equal": True, "canonical_cfg_sha256": value["assembly"]["cfg_sha256"],
                "selected_file_sha256": sha(RUN / "graph/selected.json"), "initial_file_sha256": sha(RUN / "graph/initial.json"),
                "selection": read(RUN / "selection.json"),
                "provenance": "Retained inherited initial CFG; this run's graph revision generated no accepted change. Revision-processing subsequently failed structurally, so the original Task/CFG/annotation/review bundle remains selected for backend analysis."},
        "initial_source_audit_binding": {
            "audit_path": "initial-source-correctness-audit.json", "audit_sha256": sha(BASE / "initial-source-correctness-audit.json"),
            "artifact_checks": source_audit_checks, "source_file_checks": source_file_checks,
            "all_eight_artifacts_and_sixteen_source_files_match": True,
            "selection": read(RUN / "selection.json"), "repair_review": run_result.get("repair_review"),
            "conclusion": "The prior source-correctness audit still refers to the actual selected initial graph and annotation, with unchanged processing/mapping and source evidence. This is an identity/binding confirmation, not a new semantic acceptance review."},
        "downstream": {
            "shared_repair_decision": decision,
            "processing_cfg_reference": processing_manifest["context"]["cfg_path"],
            "scope_sha256": scope["scope_sha256"], "processing_slot_count": len(scope["slots"]),
            "processing_ir": sorted(scope["slots"]), "changed_cfg_ir": [], "removed_instruction_ids": scope["removed_instruction_ids"],
            "retained_validation_gap_ir": sorted(g["instruction_id"] for g in scope["retained_validation_gaps"]),
            "unresolved_targets": scope["unresolved_targets"],
            "why_run": "The existing shared round is eligible for 46 findings in cfg and annotation. A valid unchanged CFG remains available. The 27 processing slots are anchored annotation findings, with no CFG-change closure. Scheduler readiness requires dependency objects to exist, not every upstream status to be complete. Processing can therefore repair these independent annotation findings on the retained CFG.",
            "dependent_stage_policy": "A changed processing fragment invalidates/rebuilds task-correspondence and sensitivity (runner.py:607-612), then assembly and source re-review. This is dependency consistency, not evidence that F001/F002 have been fixed. If the revision produces no consistent annotation, the original complete bound bundle remains selected.",
            "code_references": ["src/skillflow/document_guided/runner.py:470", "src/skillflow/document_guided/runner.py:484", "src/skillflow/document_guided/runner.py:577", "src/skillflow/document_guided/fragment_revision.py:134", "src/skillflow/document_guided/runner.py:742"]},
        "delivery": {"prompt_characters": len(call["prompt"]), "preflight": preflight,
                     "call_wall_seconds": (datetime.fromisoformat(call["finished_at"]) - datetime.fromisoformat(call["started_at"])).total_seconds()},
        "policy": {"normal_stages": 7, "inherited_normal_stages": 3, "fresh_normal_stages": 4, "workers": 2,
                   "shared_repair_rounds": 1, "policy_changed_by_audit": False},
    }
    (BASE / "revision-graph-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (BASE / "revision-graph-audit.en.md").write_text(
        "# Saved GA4 graph revision audit\n\n"
        "The graph revision applied zero changes. Before, returned, and selected CFG objects are identical: 215 blocks, 489 IR and 192 edges; canonical CFG SHA `2d3b4f0972b724d14e1ff9aa9d5ca2b98a88032df51f9a8698819df9a8cd0e9e`. Revision-processing subsequently failed structurally; the original Task, CFG, annotation and bound review remain selected together for backend analysis.\n\n"
        "The signed plan offered 13 slots: 11 field slots and two region slots. The response supplied only the two region updates for the notification mappings. Both returned `value:{blocks:[...]}`; the region validator requires `value:[...]`. They were locally rejected at `/updates/0` and `/updates/1` with `cfg_region_boundary`. Envelope validation was valid because the envelope and plan identity were correct and the retained graph remained valid. The runner marks the stage partial from these quarantined errors. This shared graph-revision call has zero further structural corrections by its existing policy. Leaving other slots unfilled is permitted; it is not the immediate format error.\n\n"
        "F001 (module initialization versus index help evaluation) received no update. F002 (conditional notification clock acquisition) received proposed decompositions, but neither was applied. Both source findings therefore remain unresolved by this graph revision.\n\n"
        "There is a deeper representational limit. The frozen region contract requires the original root operations to remain exactly equal and forbids operations in added blocks (`graph_slots.py:281-284`). The proposed reads/conversion/merge/receipt assembly violate that rule even if their array wrapper is fixed. The five field slots per instruction allow opcode/inputs/outputs/constraints/source edits, but no new producer, operation, block or exit. No action-preserving CFG-only edit through these slots can satisfy F002's explicit guarded-read/conversion/merge decomposition: the original mapping still executes before the root exit. This is a direct static comparison, not a tested alternate patch. The delivered prompt exposes `value:JSON` plus the plan and boundary prose, without the region-array shape, Block grammar, or action-preservation restriction (`prompts.py:291-299`). The observed first rejection is a format error; the requested action decomposition is also beyond that region capability.\n\n"
        "Processing offers a different possible owner for internal clock semantics. Both `ir_260` and `ir_272` are authorized revision slots, and a task-local `clock` location already exists. Source-backed case segments can describe a nonfallback value and a fallback case containing an actual clock read and conversion, with the appropriate output/demand relationships. The current selected records omit that read. This is only a static representational option, not an implemented or validated fix; guard/quality fidelity still needs validation and source review. It also does not automatically resolve the separate CFG-level F002 finding.\n\n"
        "Continuing processing is consistent with the existing dependency policy. The saved shared-repair decision admitted 46 CFG/annotation findings, and a valid unchanged CFG remains available. `revision/processing-scope.json` authorizes 27 IR anchored to annotation findings, with zero changed CFG IR and no removed IR; its manifest points explicitly to `graph/initial.json`. Four prior validation gaps (`ir_167`, `ir_311`, `ir_329`, `ir_346`) remain outside that scope. A changed processing fragment will cause dependent mapping/sensitivity material to be rebuilt and re-reviewed. This does not establish that the two CFG findings were repaired.\n\n"
        "After the processing revision failed, all eight artifact hashes and all 16 source-file hashes recorded by `initial-source-correctness-audit.json` still match. The selected annotation manifest is `9a869bec8876fa458509193aa232118aab34f9c5b5710268eda9a6d07f26a2ab`, and the selected original CFG file is `fb083f7eb0d9b70e333efa259f3c3c2ad0d80d92d343f6712c37a3051d1b8c39`. The existing source-correctness findings therefore remain bound to the selected bundle; the failed revision has not corrected or displaced them.\n\n"
        "The seven-stage policy (three inherited plus four fresh normal stages), two workers and existing budgets remain unchanged. This audit only reads saved artifacts and implementation text. Exact slots, diagnostics, references, delivery preflight and hashes are in `revision-graph-audit.json`; no runtime material was changed and no analysis, validation, model, Skill or replay was executed.\n", encoding="utf-8")
    print(json.dumps({"audit": str(BASE / "revision-graph-audit.json"), "sha256": sha(BASE / "revision-graph-audit.json"),
                      "counts": report["cfg"]["before"], "patch_updates_applied": 0, "processing_slots": len(scope["slots"])}))


if __name__ == "__main__":
    main()
