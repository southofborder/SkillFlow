"""Passive saved-byte review/correction audit; never imports project stages."""
from collections import Counter
from datetime import datetime, timezone
import json
from audit_processing_material_v12 import ROOT, VERIFY, RUN, compact, expand, read, sha, unique


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def prompt_parts(path):
    data = path.read_bytes()
    text = data.decode("utf-8")
    start = text.index("\nINPUT_JSON\n") + len("\nINPUT_JSON\n")
    encoded, length = json.JSONDecoder(object_pairs_hook=unique).raw_decode(text[start:])
    logical = expand(encoded)
    return data, text, logical, length, text[start + length:]


def main():
    owner = RUN / "review"
    response_path = owner / "calls/review/a001/response.json"
    response_bytes = response_path.read_bytes()
    raw = read(response_path)
    candidate = json.loads(raw, object_pairs_hook=unique)
    validation = read(owner / "calls/review/a001/validation.json")
    material = read(owner / "inputs.json")
    request = read(owner / "calls/review/a002/request.json")
    first_bytes, first, before, first_size, first_source = prompt_parts(owner / "prompt.txt")
    second_bytes, second, after, second_size, second_source = prompt_parts(owner / "calls/review/a002/prompt.txt")
    correction = after["correction"]
    inventory = material["input_contract_inventory"]
    obligations = {row["id"]: row for row in inventory["obligations"]}
    layouts = {row["obligation_id"]: row for row in inventory["contracts"]}
    ids = [row["obligation_id"] for row in candidate["input_contract_checks"]]
    scope_claims, explicit, implicit, scope_mismatches = Counter(), 0, 0, []
    wide_errors = []
    for index, row in enumerate(candidate["input_contract_checks"]):
        scopes = {item["id"]: item for item in layouts[row["obligation_id"]]["scopes"]}
        groups = row.get("scope_checks", [])
        if not groups:
            implicit += len(scopes)
            scope_claims[row["status"]] += len(scopes)
        else:
            actual = [identity for group in groups for identity in group["scope_ids"]]
            explicit += len(actual)
            if len(actual) != len(set(actual)) or set(actual) != set(scopes):
                scope_mismatches.append(index)
            for group in groups:
                scope_claims[group["status"]] += len(group["scope_ids"])
        if any(d["code"] == "review_record" and d["path"] == f"/input_contract_checks/{index}" for d in validation["diagnostics"]):
            wide_errors.append({"record_path": f"/input_contract_checks/{index}",
                "instruction_id": obligations[row["obligation_id"]]["instruction_id"],
                "obligation_id": row["obligation_id"], "reason": row["reason"],
                "groups": [{"scope_kinds": [scopes[identity]["kind"] for identity in group["scope_ids"]],
                    "affected_scope_kinds": [scopes[identity]["kind"] for identity in group.get("affected_scope_ids", [])],
                    "status": group["status"]} for group in groups]})
    records = {}
    for path in correction["record_ids"]:
        table, number = path[1:].split("/")
        records[path] = candidate[table][int(number)]
    root_diagnostic_paths = {row["path"] for row in validation["diagnostics"]}
    direct = set(root_diagnostic_paths)
    for row in validation["diagnostics"]:
        direct.update(pair["record_path"] for pair in row.get("context", {}).get("conflicting_checks", []))
    extra = sorted(set(records) - direct)
    targets = material["input_contract_targets"]
    closure_links = []
    for path in extra:
        finding = records[path]
        linked = []
        for record_path, record in records.items():
            if not record_path.startswith("/input_contract_checks/"):
                continue
            overlap = sorted({actual for actual in finding["target_ids"]
                for protected in targets[record["obligation_id"]]
                if actual == protected or actual.startswith(protected + "/") or protected.startswith(actual + "/")})
            if overlap:
                linked.append({"record_path": record_path, "obligation_id": record["obligation_id"], "overlap_targets": overlap})
        closure_links.append({"extra_record": path, "linked_selected_checks": linked})
    source_parts = ["File navigation (not proof of semantic coverage):"]
    source_parts.extend(f"- {name} ({len(text.splitlines(keepends=True))} physical lines)" for name, text in material["files"].items())
    segments = []
    for name, text in material["files"].items():
        lines = text.splitlines(keepends=True)
        segments.append(f"\nSOURCE {name}:1-{len(lines)}\n" + "".join(f"{i}: {line}" for i, line in enumerate(lines, 1)))
    source_parts.extend(segments)
    source = "\n".join(source_parts)
    checks = {
        "all_original_logical_inputs_exactly_restored": {k: v for k, v in after.items() if k != "correction"} == before,
        "source_suffix_byte_identical": first_source == second_source,
        "complete_source_suffix_exact": second_source == "\nCOMPLETE SOURCE\n" + source,
        "all_source_segments_once": all(second.count(segment) == 1 for segment in segments),
        "selected_records_exact_prior_values": correction["records"] == list(records.values()),
        "all_displayed_diagnostics_exact": correction["diagnostics"] == validation["diagnostics"],
        "all_raw_diagnostics_mapped": sorted(row["raw_index"] for row in validation["diagnostic_mapping"]) == list(range(len(validation["raw_diagnostics"]))),
        "scope_candidate_hash_exact": correction["scope"]["candidate_sha256"] == canonical(candidate),
        "scope_material_hash_exact": correction["scope"]["material_sha256"] == canonical(material),
        "scope_records_hash_exact": correction["scope"]["records_sha256"] == canonical(records),
        "scope_inventory_hash_exact": correction["scope"]["inventory_sha256"] == canonical(inventory["obligations"]),
        "request_prior_response_hash_exact": request["previous"]["response_sha256"] == canonical(raw),
        "request_prior_validation_hash_exact": request["previous"]["validation_sha256"] == canonical(validation),
        "prior_response_unchanged_during_audit": response_path.read_bytes() == response_bytes,
        "no_missing_or_duplicate_obligations": len(ids) == len(set(ids)) and set(ids) == set(obligations),
        "all_authored_contract_ids_match": all(row["contract_id"] == obligations[row["obligation_id"]]["contract_id"] for row in candidate["input_contract_checks"]),
        "all_claimed_scope_inventories_exact": not scope_mismatches,
    }
    assert all(checks.values()), checks
    call = read(owner / "calls/review/a001/call.json")
    seconds = (datetime.fromisoformat(call["finished_at"]) - datetime.fromisoformat(call["started_at"])).total_seconds()
    references = []
    for name in ("inputs.json", "prompt.txt", "calls/review/a001/request.json", "calls/review/a001/response.json", "calls/review/a001/validation.json", "calls/review/a002/request.json", "calls/review/a002/prompt.txt"):
        data = (owner / name).read_bytes()
        references.append({"path": (owner / name).relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": sha(data)})
    report = {"audit": "passive_review_first_answer_and_finite_correction", "created_utc": datetime.now(timezone.utc).isoformat(),
        "run_directory": RUN.relative_to(ROOT).as_posix(), "snapshot": "a001 rejected; a002 correction running; no accepted merged review at this snapshot",
        "references": references, "identity_and_completeness_checks": checks,
        "a001": {"status": validation["status"], "response_container_bytes": len(response_bytes), "raw_model_text_chars": len(raw),
            "raw_model_text_utf8_bytes": len(raw.encode()), "compact_candidate_chars": len(compact(candidate)),
            "public_call_elapsed_seconds": seconds, "findings": len(candidate["findings"]),
            "finding_domains": dict(Counter(row["domain"] for row in candidate["findings"])),
            "obligations_returned": len(ids), "obligations_expected": len(obligations), "missing_obligation_ids": sorted(set(obligations) - set(ids)),
            "authored_check_statuses": dict(Counter(row["status"] for row in candidate["input_contract_checks"])),
            "scope_inventory_total": sum(len(row["scopes"]) for row in layouts.values()), "implicit_accepted_scope_claims": implicit,
            "explicit_scope_claims": explicit, "authored_scope_statuses": dict(scope_claims),
            "scope_counts_are_accepted_validation": False,
            "displayed_diagnostics": validation["diagnostics"], "raw_diagnostic_count": len(validation["raw_diagnostics"]),
            "raw_diagnostic_categories": dict(Counter(row["code"] for row in validation["raw_diagnostics"])),
            "wide_group_errors": wide_errors},
        "a002": {"strategy": request["correction_strategy"], "mode": "finite_existing_records", "core_prompt_chars": len(second),
            "core_prompt_utf8_bytes": len(second_bytes), "initial_core_prompt_chars": len(first), "increase_chars": len(second)-len(first),
            "adapter_limit": 1048576, "core_character_headroom": 1048576-len(second),
            "encoded_input_chars": second_size, "expanded_logical_input_chars": len(compact(after)),
            "same_prompt_literal_input_chars": len(second)-second_size+len(compact(after)),
            "all_source_file_count": len(material["files"]), "rendered_source_chars": len(source),
            "complete_obligations_in_input": len(after["input_contract_inventory"]["obligations"]),
            "complete_scope_count_in_input": sum(len(row["scopes"]) for row in after["input_contract_inventory"]["obligations"]),
            "allowed_existing_record_ids": list(records), "allowed_record_counts": dict(Counter(path.split('/')[1] for path in records)),
            "allowed_insertion_obligation_indices": correction["insertion_obligation_indices"],
            "retained_record_counts": correction["scope"]["retained_record_counts"],
            "extra_conflict_closure_links": closure_links, "scope": correction["scope"]},
        "limits": ["Coverage counts are authored judgments, not accepted semantic checks; saved strict validation rejected a001.",
            "25 is the permitted existing-record edit set, not the number of replacements a002 has returned; no a002 answer exists in this snapshot.",
            "All input material, source, contracts and scope inventory remain; prior unlisted response records are retained locally rather than repeated in full in the correction prompt.",
            "Character sizes are core prompts, not transport delivery bytes or pure generation time; no speed/output success claim is made.",
            "No project imports, validators, backend, replay, model or Skill execution; raw failures remain unchanged."]}
    out = VERIFY / "source-review-a001-correction-audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(compact({"report": out.relative_to(ROOT).as_posix(), "sha256": sha(out.read_bytes()), "checks": checks,
        "a001": {k: v for k, v in report["a001"].items() if k not in {"displayed_diagnostics", "wide_group_errors"}},
        "a002": {k: v for k, v in report["a002"].items() if k not in {"allowed_existing_record_ids", "scope"}}}))


if __name__ == "__main__":
    main()
