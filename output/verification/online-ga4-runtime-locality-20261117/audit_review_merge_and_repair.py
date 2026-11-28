"""Passive exact-record merge and saved repair-routing audit only."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from audit_processing_material_v12 import ROOT, VERIFY, RUN, compact, read, sha, unique
from audit_review_first_correction import canonical, prompt_parts


def claims(candidate, layouts):
    result = {}
    for row in candidate["input_contract_checks"]:
        for scope in layouts[row["obligation_id"]]["scopes"]:
            result[scope["id"]] = row["status"]
        for group in row.get("scope_checks", []):
            for identity in group["scope_ids"]:
                result[identity] = group["status"]
    return result


def main():
    owner = RUN / "review"
    material = read(owner / "inputs.json")
    prior = json.loads(read(owner / "calls/review/a001/response.json"), object_pairs_hook=unique)
    raw = read(owner / "calls/review/a002/response.json")
    patch = json.loads(raw, object_pairs_hook=unique)
    merged = read(owner / "calls/review/a002/merged-candidate.json")
    validation = read(owner / "calls/review/a002/validation.json")
    chain = read(owner / "calls/review/chain.json")
    selected_review = read(owner / "result.json")
    final = selected_review["review"]
    context = prompt_parts(owner / "calls/review/a002/prompt.txt")[2]["correction"]
    allowed = set(context["record_ids"])
    reconstructed = deepcopy(prior)
    replaced = []
    for row in patch["replacements"]:
        path = row["record_id"]
        table, index = path[1:].split("/")
        reconstructed[table][int(index)] = row["value"]
        replaced.append(path)
    changed = []
    unchanged = Counter()
    for table in ("findings", "input_contract_checks", "input_projection_checks", "source_input_findings"):
        assert len(prior[table]) == len(merged[table])
        for index, (before, after) in enumerate(zip(prior[table], merged[table])):
            path = f"/{table}/{index}"
            if before != after:
                changed.append(path)
            else:
                unchanged[table] += 1
    layouts = {row["obligation_id"]: row for row in material["input_contract_inventory"]["contracts"]}
    old_scopes, new_scopes = claims(prior, layouts), claims(merged, layouts)
    rejected = {row["obligation_id"] for row in final["input_contract_checks"] if row["status"] == "rejected"}
    generated = [row for row in final["findings"] if "input_contract_obligation_id" in row]
    original = [row for row in final["findings"] if "input_contract_obligation_id" not in row]
    decision = read(RUN / "audit/shared-repair-decision.json")
    selection = read(RUN / "selection.json")
    run_result = read(RUN / "result.json")
    task_request = read(RUN / "revision/task/inputs/request.json")
    graph_prompt = (RUN / "steps/revision-graph/prompt.txt").read_bytes().decode()
    marker = "\nCURRENT REVIEW FEEDBACK\n"
    feedback, _ = json.JSONDecoder(object_pairs_hook=unique).raw_decode(graph_prompt.split(marker, 1)[1])
    call = read(owner / "calls/review/a002/call.json")
    checks = {
        "a002_saved_validation_valid": validation["status"] == "valid",
        "accepted_call_a002": chain["accepted_call"] == "calls/review/a002",
        "all_replacements_within_allowed_set": set(replaced) <= allowed and len(replaced) == len(set(replaced)),
        "no_insertions": patch["insertions"] == [],
        "literal_record_replacements_reproduce_saved_merge": reconstructed == merged,
        "nothing_outside_allowed_set_changed": set(changed) <= allowed,
        "all_original_findings_unchanged": prior["findings"] == merged["findings"],
        "full_obligation_order_and_ids_retained": [x["obligation_id"] for x in prior["input_contract_checks"]] == [x["obligation_id"] for x in merged["input_contract_checks"]],
        "merged_candidate_hash_matches_validation": canonical(merged) == validation["candidate_sha256"],
        "raw_correction_hash_matches_validation": canonical(raw) == validation["response_sha256"],
        "original_findings_preserved_in_review_result": len(original) == len(merged["findings"]) and all(
            all(saved.get(k) == value for k, value in authored.items()) for saved, authored in zip(original, merged["findings"])),
        "one_generated_finding_per_rejected_check": len(generated) == len(rejected) and {x["input_contract_obligation_id"] for x in generated} == rejected,
        "repair_review_hash_exact": decision["review_sha256"] == canonical(selected_review),
        "repair_source_hash_exact": decision["source_sha256"] == canonical(material["files"]),
        "task_revision_only_previous_task_and_objections": set(task_request) == {"revision"} and set(task_request["revision"]) == {"previous_task", "objections"},
        "task_previous_value_exact": task_request["revision"]["previous_task"] == material["task"],
        "task_objections_exact": task_request["revision"]["objections"] == selected_review["objections"],
        "graph_feedback_only_cfg_findings": feedback["findings"] == [row for row in final["findings"] if row["domain"] == "cfg"],
    }
    assert all(checks.values()), checks
    refs = []
    for name in ("review/inputs.json", "review/calls/review/a001/response.json", "review/calls/review/a002/response.json",
                 "review/calls/review/a002/merged-candidate.json", "review/calls/review/a002/validation.json", "review/result.json",
                 "audit/shared-repair-decision.json", "revision/task/inputs/request.json", "steps/revision-graph/prompt.txt"):
        data = (RUN / name).read_bytes()
        refs.append({"path": (RUN / name).relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": sha(data)})
    scope_changes = []
    for index, row in enumerate(merged["input_contract_checks"]):
        for scope in layouts[row["obligation_id"]]["scopes"]:
            identity = scope["id"]
            if old_scopes[identity] != new_scopes[identity]:
                scope_changes.append({"check_index": index, "obligation_id": row["obligation_id"], "scope_id": identity,
                    "scope_kind": scope["kind"], "before": old_scopes[identity], "after": new_scopes[identity]})
    report = {"audit": "passive_valid_review_merge_and_shared_repair", "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_directory": RUN.relative_to(ROOT).as_posix(), "identity_checks": checks, "references": refs,
        "a002": {"response_text_chars": len(raw), "response_container_bytes": (owner / "calls/review/a002/response.json").stat().st_size,
            "public_call_elapsed_seconds": (datetime.fromisoformat(call["finished_at"])-datetime.fromisoformat(call["started_at"])).total_seconds(),
            "validation_status": validation["status"], "allowed_record_count": len(allowed), "actual_replacement_count": len(replaced),
            "insertion_count": len(patch["insertions"]), "changed_record_paths": changed, "unchanged_record_counts": dict(unchanged),
            "changed_obligation_statuses": dict(Counter(x["status"]+"->"+y["status"] for x,y in zip(prior["input_contract_checks"],merged["input_contract_checks"])))},
        "selected_initial_review": {"status": selected_review["status"], "diagnostic_only": selected_review["diagnostic_only"],
            "validation_gaps": final.get("validation_gaps", []), "obligations": len(final["input_contract_checks"]),
            "check_statuses": dict(Counter(x["status"] for x in final["input_contract_checks"])), "scopes": len(new_scopes),
            "scope_statuses": dict(Counter(new_scopes.values())),
            "scope_status_transitions": dict(Counter(old_scopes[x]+"->"+new_scopes[x] for x in old_scopes)),
            "scope_changes": scope_changes,
            "original_finding_count": len(original), "generated_contract_finding_count": len(generated), "finding_count": len(final["findings"]),
            "finding_routes": [{"domain": domain, "owner": owner_name, "count": count} for (domain,owner_name),count in Counter((x['domain'],x.get('owner')) for x in final['findings']).items()],
            "task_objections": selected_review["objections"], "projection_checks": len(final['input_projection_checks']), "source_input_findings": len(final['source_input_findings'])},
        "repair": {"decision": decision, "selection_at_snapshot": selection, "root_stage_statuses_at_snapshot": run_result['stages'],
            "prepared_task_request_fields": list(task_request['revision']), "graph_feedback_findings": len(feedback['findings']),
            "graph_feedback_ir_count": sum(len(b['instructions']) for b in feedback['cfg']['blocks'].values()),
            "dependency_closure_from_frozen_runner": ['task','graph','processing','task-correspondence','sensitivity','assembly','source-re-review'],
            "flow_reused": True, "next_downstream_work_is_complete": False},
        "limits": ["Saved strict validity means exact schema/reference/scope/conflict acceptance, not independent proof every semantic judgment is true.",
            "Initial material still has 25 rejected contracts and 44 routed findings; complete review is not a clean Skill/CFG/annotation verdict.",
            "1625 accepted/110 rejected scope decisions belong to this initial annotation; they cannot be applied to future changed contracts without a newly bound review.",
            "Revision dependency closure is the existing frozen plan; no new CFG, rebuilt annotation, repaired correctness, propagation or deletion success is asserted.",
            "Public call interval is not pure generation; output lengths are observed text/storage sizes, not same-answer compression or latency comparisons.",
            "No validators, backend, project stages, models, Skills, tests, replay or frozen writes occurred."]}
    path = VERIFY / 'source-review-merge-repair-audit.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(compact({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'checks':checks,'a002':report['a002'],
        'review':{k:v for k,v in report['selected_initial_review'].items() if k not in {'scope_changes','task_objections'}},
        'repair':{k:v for k,v in report['repair'].items() if k not in {'selection_at_snapshot','root_stage_statuses_at_snapshot'}}}))


if __name__ == '__main__':
    main()
