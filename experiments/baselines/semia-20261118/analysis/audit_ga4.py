"""Read GA4 comparison receipts only; never invoke a model or Semia pipeline."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "comparison/ga4"
OUT = BASE / "analysis"
ISSUES = []
LEXICAL_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[一-鿿]|[぀-ゟ]|[゠-ヿ]|[가-힯]")
TOKEN_KEYS = ("input_tokens", "output_tokens", "cached_input_tokens", "cache_write_input_tokens", "reasoning_output_tokens")


def reference(path):
    return path.relative_to(BASE).as_posix()


def read(path):
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, ValueError) as exc:
        ISSUES.append({"path": reference(path), "error": f"{type(exc).__name__}: {exc}"})
        return None


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_receipt(path):
    return {"path": reference(path), "exists": path.is_file(),
            "sha256": digest(path) if path.is_file() else None,
            "bytes": path.stat().st_size if path.is_file() else None}


def usage_summary(usages):
    """Missing/non-numeric fields never become zero, including empty usage objects."""
    result = {}
    for key in TOKEN_KEYS:
        values = [u.get(key) for u in usages if isinstance(u, dict)
                  and isinstance(u.get(key), (int, float)) and not isinstance(u.get(key), bool)]
        missing = len(usages) - len(values)
        result[key] = {"known_sum": sum(values) if values else None, "missing_events": missing,
                       "complete_value": sum(values) if usages and not missing else None}
    return {"event_count": len(usages), "fields": result}


def usage_reconciliation(raw, request):
    raw_summary = usage_summary(raw)
    stated_list = request.get("public_turn_usages")
    stated_summary = usage_summary(stated_list) if isinstance(stated_list, list) else None
    stated_usage = request.get("usage")
    comparisons = {}
    for key, item in raw_summary["fields"].items():
        actual = item["complete_value"]
        declared = stated_usage.get(key) if isinstance(stated_usage, dict) else None
        listed = stated_summary["fields"][key]["complete_value"] if stated_summary else None
        comparisons[key] = {"raw_complete_value": actual, "request_usage_value": declared,
                            "public_turn_usages_complete_value": listed,
                            "request_usage_matches": actual == declared if actual is not None and declared is not None else None,
                            "public_turn_usages_matches": actual == listed if actual is not None and listed is not None else None}
    return {"raw": raw_summary, "request_usage": stated_usage,
            "request_public_turn_usages": stated_list, "fields": comparisons,
            "public_event_list_matches": raw == stated_list if isinstance(stated_list, list) else None,
            "note": "Null comparison is unknown, not agreement. Public partial sums remain visible; internal unreported sampling usage is unknown."}


def phase_usage_summary(calls):
    summary = usage_summary([u for c in calls for u in c["raw_completed_event_usages"]])
    summary["native_starts"] = len(calls)
    summary["native_calls_without_completed_events"] = sum(not c["raw_completed_event_usages"] for c in calls)
    for key, row in summary["fields"].items():
        missing = sum(c["usage_reconciliation"]["raw"]["fields"][key]["complete_value"] is None for c in calls)
        row["calls_missing_field"] = missing
        row["complete_value_across_observed_events"] = row["complete_value"]
        # Event completeness cannot establish phase completeness when a native call has no receipt.
        row["complete_value"] = row["complete_value"] if calls and not missing else None
        row["status"] = "complete_public_fields" if row["complete_value"] is not None else "known_lower_bound_with_unknown" if row["known_sum"] is not None else "unknown"
    summary["note"] = "Known sums are public lower bounds. Missing native-call completions or fields keep phase totals unknown; internal unreported usage remains unknown regardless."
    return summary


def validation_identity(folder, invocation, payload, check):
    submitted, copied = folder / "submitted-facts.dl", folder / "synthesized_facts.dl"
    actual = digest(submitted) if submitted.is_file() else None
    inv_sha = invocation.get("submitted_facts_sha256") if isinstance(invocation, dict) else None
    payload_sha = payload.get("synthesized_facts_sha256") if isinstance(payload, dict) else None
    copied_sha = digest(copied) if copied.is_file() else None
    identity_ok = actual is not None and actual == inv_sha == payload_sha == copied_sha
    returned = isinstance(invocation, dict) and invocation.get("returned") is True and not invocation.get("error")
    valid_consistent = (isinstance(check, dict) and isinstance(payload, dict)
                        and isinstance(check.get("program_valid"), bool)
                        and check["program_valid"] is payload.get("program_valid"))
    counts_consistent = (isinstance(check, dict) and isinstance(payload, dict)
                         and isinstance(check.get("errors"), list) and isinstance(check.get("warnings"), list)
                         and len(check["errors"]) == payload.get("errors") and len(check["warnings"]) == payload.get("warnings"))
    return {"usable": bool(identity_ok and returned and valid_consistent and counts_consistent),
            "actual_submitted_sha256": actual, "invocation_sha256": inv_sha, "payload_sha256": payload_sha,
            "copied_facts_sha256": copied_sha, "all_facts_hashes_match": identity_ok,
            "returned_without_error": returned, "check_payload_validity_consistent": valid_consistent,
            "check_payload_counts_consistent": counts_consistent,
            "check_receipt": file_receipt(folder / "synthesis_check.json"),
            "invocation_receipt": file_receipt(folder / "invocation.json"),
            "payload_receipt": file_receipt(folder / "return-payload.json"),
            "note": "A failed or identity-unbound check may contain stale shared files; its validity/counts are not usable."}


def map_candidates(candidates, validations, selected_sha=None, synthesis_completed=False,
                   completed_metadata_receipt=None, final_facts_path=None):
    """Original attempt files define candidate count; later checks never add candidates."""
    used = set()
    canonical = lambda p: str((BASE / p).resolve()).replace("\\", "/").casefold() if p else None
    for validation in validations:
        sha = validation["submitted_facts_sha256"]
        matches = [c for c in candidates if c["sha256"] == sha and sha is not None]
        validation["matching_candidate_paths"] = [c["path"] for c in matches]
        inv_time = validation.get("invocation_started_at_utc")
        completed_time = (completed_metadata_receipt or {}).get("modified_at_utc")
        final_order = (synthesis_completed and sha is not None and sha == selected_sha
                       and canonical(validation.get("invocation_facts_path")) == canonical(final_facts_path)
                       and final_facts_path is not None and inv_time is not None and completed_time is not None
                       and datetime.fromisoformat(inv_time) > datetime.fromisoformat(completed_time))
        validation["assigned_candidate_path"] = None
        if final_order:
            validation["role"] = "selected_facts_final_recheck"
            validation["mapping_evidence"] = {"method": "Selected SHA + final facts invocation path + invocation after completed metadata file write",
                                               "completed_metadata": completed_metadata_receipt,
                                               "invocation_started_at_utc": inv_time,
                                               "limitation": "File-time ordering is observed provenance, not a model-call ID. Copied/reordered file times leave classification unknown."}
            continue
        direct = [c for c in matches if canonical(c["path"]) == canonical(validation.get("invocation_facts_path"))]
        unique = direct[0] if len(direct) == 1 else matches[0] if len(matches) == 1 else None
        if unique and unique["path"] not in used:
            candidate = unique
            used.add(candidate["path"])
            validation["role"] = "candidate_validation"
            validation["assigned_candidate_path"] = candidate["path"]
            validation["mapping_evidence"] = {"method": "actual invocation candidate path and SHA" if direct else "SHA unique among original attempt files"}
            candidate["primary_validation"] = validation["check"]
            candidate["program_valid"] = validation["program_valid"] if validation["identity"]["usable"] else None
        else:
            validation["role"] = "ambiguous_same_hash_attempts" if len(matches) > 1 else "repeated_or_unmapped_validation"
            validation["mapping_evidence"] = {"method": "unknown", "reason": "Same SHA does not identify a structural attempt; patch_unmatched can save an attempt without invoking checker. No greedy allocation."}
    return {"attempt_file_count": len(candidates), "unique_candidate_hash_count": len({c["sha256"] for c in candidates}),
            "valid_candidate_attempt_count": sum(c.get("program_valid") is True for c in candidates),
            "unknown_candidate_attempt_count": sum(c.get("program_valid") is None for c in candidates),
            "validation_count": len(validations),
            "usable_validation_count": sum(v["identity"]["usable"] for v in validations),
            "final_recheck_count": sum(v["role"] == "selected_facts_final_recheck" for v in validations),
            "ambiguous_same_hash_validation_count": sum(v["role"] == "ambiguous_same_hash_attempts" for v in validations),
            "candidates": candidates, "selected_facts_sha256": selected_sha,
            "mapping_method": "Final recheck identified independently by selected SHA/path/completed-metadata ordering; candidate association requires an actual candidate invocation path or a SHA unique among attempt files. Same-SHA ambiguity stays unknown; extra checks never count as new candidates."}


def inventory_check(root, expected, sizes=None, exclude_bytecode=False):
    all_paths = [p for p in root.rglob("*") if p.is_file()]
    ignored = [p for p in all_paths if exclude_bytecode and ("__pycache__" in p.parts or p.suffix == ".pyc")]
    actual = {p.relative_to(root).as_posix(): p for p in all_paths if p not in ignored}
    records = []
    for name, pin in expected.items():
        path = root / name
        safe = not path.is_symlink() and path.resolve().is_relative_to(root.resolve())
        receipt = file_receipt(path) if safe else {"path": str(path), "exists": None, "sha256": None, "bytes": None}
        size = sizes.get(name) if sizes else None
        records.append(receipt | {"safe_path": safe, "expected_sha256": pin, "expected_bytes": size,
                                  "sha256_matches": receipt["sha256"] == pin if receipt["sha256"] else False,
                                  "size_matches": receipt["bytes"] == size if size is not None else None})
    return {"actual_file_count": len(actual), "expected_file_count": len(expected),
            "inventory_matches": set(actual) == set(expected), "missing": sorted(set(expected)-set(actual)),
            "unexpected": sorted(set(actual)-set(expected)),
            "ignored_runtime_bytecode": [p.relative_to(root).as_posix() for p in ignored],
            "all_hashes_match": all(r["sha256_matches"] for r in records),
            "all_sizes_match": all(r["size_matches"] is True for r in records) if records else None,
            "records": records}


def inspect_pins(runtime, case):
    source_path, input_path = BASE / "source-manifest.json", BASE / "input-manifest.json"
    source = read(source_path) or {}
    first_path = BASE / "pilot/001/runtime.json"
    first = read(first_path) or {}
    expected = {r["path"]: r["sha256"] for r in source.get("files", [])}
    archive = BASE / "downloads/semia-379bc25f.zip"
    archive_ok = archive.is_file() and digest(archive) == source.get("archive_sha256")
    sizes = {}
    if archive_ok:
        with zipfile.ZipFile(archive) as package:
            sizes = {info.filename.split("/", 1)[1]: info.file_size for info in package.infolist()
                     if not info.is_dir() and "/" in info.filename}
    src = inventory_check(BASE / "source", expected, sizes, exclude_bytecode=True)
    inp = inventory_check(BASE / case["path"], {r["path"]: r["sha256"] for r in case["files"]},
                          {r["path"]: r["size"] for r in case["files"]})
    checks = {"source_manifest_matches_runtime": digest(source_path) == runtime.get("source_manifest_sha256"),
              "input_manifest_matches_runtime": digest(input_path) == runtime.get("input_manifest_sha256"),
              "input_manifest_matches_first_pilot": digest(input_path) == first.get("input_manifest_sha256"),
              "source_hash_inventory_matches_first_pilot": expected == first.get("source_file_hashes"),
              "source_commit_matches_runtime": source.get("commit") == runtime.get("source_commit"),
              "source_inventory_count_is_360": len(expected) == len(source.get("files", [])) == runtime.get("source_file_count") == 360,
              "input_inventory_count_matches_runtime": len(case["files"]) == len({r["path"] for r in case["files"]}) == runtime.get("input_files"),
              "source_archive_matches_manifest": archive_ok,
              "cli_identity_matches_first_pilot": all(runtime.get(k) == first.get(k) for k in ("cli_executable", "cli_sha256")),
              "model_configuration_matches_first_pilot": all(runtime.get(k) == first.get(k) for k in ("model", "reasoning_effort", "model_provider")),
              "model_configuration_matches_requested_control": (runtime.get("model"), runtime.get("reasoning_effort"), runtime.get("model_provider")) == ("gpt-6.1-sol", "high", "openai")}
    return {"checks": checks, "source": src, "input": inp,
            "source_and_input_verified": all(checks.values()) and all(src[k] is True and inp[k] is True for k in ("inventory_matches", "all_hashes_match", "all_sizes_match")),
            "size_reference": "Source sizes from the SHA-bound official ZIP; source manifest has no size field. Input sizes from the SHA-bound input manifest.",
            "evidence": [file_receipt(p) for p in (source_path, input_path, first_path, archive)]}


def inspect_argv(request, runtime):
    argv = request.get("argv")
    if not isinstance(argv, list):
        return {"matches_runtime": None, "reason": "argv missing"}
    models = [argv[i+1] for i, value in enumerate(argv[:-1]) if value == "--model"]
    configs = [argv[i+1] for i, value in enumerate(argv[:-1]) if value == "-c"]
    check = {"cli_path": bool(argv) and argv[0] == runtime.get("cli_executable"),
             "model": models == [runtime.get("model")],
             "reasoning_effort": [c for c in configs if c.startswith("model_reasoning_effort=")] == [f'model_reasoning_effort="{runtime.get("reasoning_effort")}"'],
             "provider": [c for c in configs if c.startswith("model_provider=")] == [f'model_provider="{runtime.get("model_provider")}"']}
    return {"matches_runtime": all(check.values()), "checks": check, "models": models, "configs": configs}


def coverage_denominator(old_units_path, full_units_path):
    """Count saved unit text using the pinned evidence.py lexical formula only."""
    old, full = read(old_units_path), read(full_units_path)
    if not old or not full:
        return None
    identity = lambda u: tuple(u[k] for k in ("source_file", "unit_type", "text", "line_start", "line_end"))
    old_counts = Counter(identity(u) for u in old["units"])
    full_counts = Counter(identity(u) for u in full["units"])
    weight = lambda key: max(1, len(LEXICAL_TOKEN_RE.findall(key[2])))
    shared, added, removed = old_counts & full_counts, full_counts - old_counts, old_counts - full_counts
    shared_weight = sum(weight(k) * n for k, n in shared.items())
    full_weight = sum(weight(k) * n for k, n in full_counts.items())
    added_by_source = {}
    for key, count in added.items():
        entry = added_by_source.setdefault(key[0], {"unit_count": 0, "lexical_weight": 0})
        entry["unit_count"] += count
        entry["lexical_weight"] += weight(key) * count
    formula_files = [BASE / "source/packages/semia-core/src/semia_core/evidence.py",
                     BASE / "source/packages/semia-cli/src/semia_cli/synthesis_loop.py"]
    return {
        "unit_identity_fields": ["source_file", "unit_type", "text", "line_start", "line_end"],
        "unit_ids_not_compared": "Insertion can renumber units; content and original source-line identities are compared as multisets.",
        "old_unit_count": sum(old_counts.values()), "full_unit_count": sum(full_counts.values()),
        "shared_unit_count": sum(shared.values()), "removed_or_changed_old_units": sum(removed.values()),
        "shared_lexical_weight": shared_weight, "full_lexical_weight": full_weight,
        "added_unit_count": sum(added.values()), "added_by_attributed_source": added_by_source,
        "new_generated_heading_units": [{"identity": list(k), "count": n, "lexical_weight": weight(k) * n}
                                        for k, n in added.items() if k[1] == "heading" and k[3] == 0],
        "reference_formula": "sum(max(1, lexical_tokens(unit.text)) for matched units) / sum(max(1, lexical_tokens(unit.text)) for all units)",
        "lexical_token_regex": LEXICAL_TOKEN_RE.pattern,
        "selection_score_formula": "0.5 * evidence_match_rate + 0.3 * evidence_support_coverage + 0.2 * reference_unit_coverage",
        "conditional_calculation": {
            "assumptions": ["All original shared units matched", "No added unit matched", "evidence_match_rate=1", "evidence_support_coverage=1"],
            "reference_coverage": shared_weight / full_weight,
            "selection_score": 0.5 + 0.3 + 0.2 * shared_weight / full_weight,
            "default_ceiling": 0.9,
            "interpretation": "Conditional calculation of an adaptation effect, not an observed candidate, measured failure cause, or original 14-file Semia result.",
        },
        "counts_are_not_model_billing_tokens": True,
        "evidence": [{"path": reference(p), "sha256": digest(p)} for p in [old_units_path, full_units_path, *formula_files]],
    }


def inspect_pids(pids, runtime=None, calls=None, finished=None):
    pids = sorted({int(pid) for pid in pids if isinstance(pid, int) and not isinstance(pid, bool) and pid > 0})
    observed = datetime.now(timezone.utc).isoformat()
    if not pids:
        return {"recorded_pids": [], "observed_processes": [], "all_recorded_pids_absent": None,
                "observed_at_utc": observed, "status": "no_pid_records"}
    script = ("$ErrorActionPreference='Stop'; $taskPids=@(" + ",".join(map(str, pids)) + "); "
              "$all=Get-CimInstance Win32_Process; $owned=@($taskPids); do { $before=$owned.Count; "
              "$owned=@($owned + @($all | Where-Object { $_.ParentProcessId -in $owned } | ForEach-Object { [int]$_.ProcessId }) | Select-Object -Unique) "
              "} while($owned.Count -gt $before); @($all | Where-Object { $_.ProcessId -in $owned } | ForEach-Object { "
              "[pscustomobject]@{ pid=[int]$_.ProcessId; parent_pid=[int]$_.ParentProcessId; name=$_.Name; "
              "start_time_utc=$_.CreationDate.ToUniversalTime().ToString('o') } }) | ConvertTo-Json -Compress")
    error = None
    try:
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=20)
        value = json.loads(result.stdout) if result.stdout.strip() else []
        value = value if isinstance(value, list) else [value]
        if result.returncode != 0:
            error = result.stderr
            value = None
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        value = None
        error = f"{type(exc).__name__}: {exc}"
    expected = {c["pid"]: c.get("started_at_utc") for c in calls or [] if isinstance(c.get("pid"), int)}
    if runtime and isinstance(runtime.get("controller_pid"), int):
        expected[runtime["controller_pid"]] = runtime.get("started_at_utc")
    for item in value or []:
        item["relation"] = "recorded_pid" if item["pid"] in pids else "observable_descendant"
        item["direct_child_of_recorded_pid"] = item["parent_pid"] in pids
        start = datetime.fromisoformat(item["start_time_utc"].replace("Z", "+00:00"))
        expected_time = expected.get(item["pid"])
        if finished and start > datetime.fromisoformat(finished["finished_at_utc"]):
            item["identity_assessment"] = "started_after_terminal_pid_reuse_or_new_process"
        elif expected_time and abs((start - datetime.fromisoformat(expected_time)).total_seconds()) < 120:
            item["identity_assessment"] = "start_time_consistent_with_recorded_process"
        else:
            item["identity_assessment"] = "ownership_unknown_check_ancestry_and_time"
    return {"recorded_pids": pids, "observed_processes": value,
            "observed_at_utc": observed, "finished_receipt": file_receipt(RUN / "finished.json"),
            "observation_after_terminal": observed >= finished.get("finished_at_utc", "~") if finished else None,
            "all_recorded_pids_absent": not any(v["pid"] in pids for v in value) if value is not None else None,
            "all_recorded_pids_and_observable_descendants_absent": not value if value is not None else None,
            "timeout_cleanup_records": [{k: c.get(k) for k in ("id", "pid", "timed_out", "tree_cleanup_returncode", "tree_cleanup_unresolved")} for c in calls or [] if c.get("timed_out") is True],
            "status": "observed" if value is not None else "inspection_uncertain", "error": error,
            "wrapper_session_exit": "unknown_root_owned_separate_receipt",
            "note": "One read-only CIM snapshot of recorded PIDs and currently observable descendants. PID reuse is distinguished by start times; orphan ancestry no longer observable cannot be certified. No process is stopped."}


def inspect_downstream(calls, finished, detection):
    report_path, rec_path = RUN / "artifacts/report.md", RUN / "artifacts/recommendation.md"
    report_text = report_path.read_text("utf-8") if report_path.is_file() else None
    rec_text = rec_path.read_text("utf-8") if rec_path.is_file() else None
    stderr = RUN / "console-stderr.txt"
    stderr_text = stderr.read_text("utf-8", errors="replace") if stderr.is_file() else ""
    skipped = [line for line in stderr_text.splitlines() if "recommendation skipped" in line]
    rec_calls = [c for c in calls if c.get("phase") == "recommendation"]
    successful = [c for c in rec_calls if c.get("returncode") == 0 and not c.get("error")]
    raw_matches = []
    for call in successful:
        path = RUN / "transport" / call["id"] / "response.txt"
        if path.is_file():
            raw_matches.append(file_receipt(path) | {"matches_recommendation_formatting": path.read_text("utf-8").rstrip() + "\n" == rec_text})
    if skipped:
        rec_state = "failed_nonfatal"
    elif rec_text is not None and rec_text.strip() and any(r["matches_recommendation_formatting"] for r in raw_matches):
        rec_state = "completed"
    elif rec_calls and not finished:
        rec_state = "in_progress"
    elif finished and not rec_calls and rec_text is None:
        rec_state = "not_run"
    else:
        rec_state = "unknown"
    detector_status = detection.get("status") if isinstance(detection, dict) else None
    return {"pipeline": {"status": "in_progress" if not finished else "completed" if finished.get("exit_code") == 0 else "failed",
                         "exit_code": finished.get("exit_code") if finished else None,
                         "source_and_input_unchanged_receipt": finished.get("source_and_input_unchanged") if finished else None,
                         "integrity_error": finished.get("integrity_error") if finished else None},
            "detector": {"status": detector_status or ("not_run" if finished and finished.get("exit_code") != 0 else "unknown"),
                         "finding_count": len(detection["findings"]) if isinstance(detection, dict) and isinstance(detection.get("findings"), list) else None,
                         "evidence": file_receipt(RUN / "artifacts/detection_result.json")},
            "report": {"status": "produced" if report_text and report_text.strip() else "unknown" if report_text is not None else "not_run" if finished else "unknown",
                       "content": report_text, "evidence": file_receipt(report_path)},
            "recommendation": {"status": rec_state, "content": rec_text, "evidence": file_receipt(rec_path),
                               "raw_response_comparisons": raw_matches, "nonfatal_error_lines": skipped,
                               "console_stderr_receipt": file_receipt(stderr),
                               "content_review": "pending_source_and_detector_claim_review" if rec_text else "not_available",
                               "meaning": "Separate model opinion/conditional advice; neither deterministic findings nor gold correctness. Pipeline exit 0 alone does not establish recommendation success."}}


def inspect_retry_delivery(calls):
    """Inspect captured payloads; reader access to full diagnostics is not model access."""
    result = []
    first_prompt = RUN / "transport/call-001/prompt.txt"
    base_prompt = first_prompt.read_text("utf-8") if first_prompt.is_file() else None
    checks = []
    for folder in sorted((RUN / "validations").glob("check-*")):
        invocation = read(folder / "invocation.json")
        if invocation and invocation.get("returned") is True:
            checks.append((folder, invocation))
    for call in calls:
        prompt_path = RUN / "transport" / call["id"] / "prompt.txt"
        prompt = prompt_path.read_text("utf-8") if prompt_path.is_file() else ""
        marker = "## Validation Feedback"
        if marker not in prompt:
            continue
        prefix, feedback = prompt.split(marker, 1)
        previous = [(folder, inv) for folder, inv in checks
                    if inv.get("started_at_utc", "~") < (call.get("started_at_utc") or "")]
        folder, invocation = max(previous, key=lambda item: item[1]["started_at_utc"]) if previous else (None, None)
        facts_path = folder / "submitted-facts.dl" if folder else None
        facts = facts_path.read_text("utf-8") if facts_path and facts_path.is_file() else None
        result.append({"request": call["id"], "prompt_sha256": digest(prompt_path),
                       "base_prompt_equal_before_validation_feedback": prefix.rstrip() == base_prompt.rstrip() if base_prompt else None,
                       "feedback_text": feedback.strip(), "previous_check": folder.name if folder else None,
                       "previous_submitted_facts_sha256": invocation.get("submitted_facts_sha256") if invocation else None,
                       "whole_previous_candidate_present": facts.strip() in prompt if facts else None,
                       "feedback_has_sdl_error_code": bool(re.search(r"SDL\d{3}", feedback)),
                       "evidence": [reference(prompt_path)] + ([reference(facts_path), reference(folder / "invocation.json")] if folder else [])})
    return result


def inspect_matched_source_units(folder, full_units):
    alignment_path = folder / "synthesis_evidence_alignment.json"
    alignment = read(alignment_path)
    old_units_path = BASE / "prepared/ga4/prepare_units.json"
    old = read(old_units_path)
    if not alignment or not full_units or not old:
        return None
    identity = lambda u: tuple(u[k] for k in ("source_file", "unit_type", "text", "line_start", "line_end"))
    old_counts = Counter(identity(u) for u in old["units"])
    matched_ids = {a["unit_id"] for a in alignment["alignments"]
                   if a.get("matched") is True and a.get("evidence_id") is not None and a.get("unit_id") is not None}
    by_file = {}
    matched_shared = matched_added = 0
    for unit in full_units["units"]:
        key = identity(unit)
        shared = old_counts[key] > 0
        if shared:
            old_counts[key] -= 1
        row = by_file.setdefault(unit["source_file"], {"units": 0, "matched_units": 0, "lexical_weight": 0, "matched_lexical_weight": 0})
        weight = max(1, len(LEXICAL_TOKEN_RE.findall(unit["text"])))
        row["units"] += 1
        row["lexical_weight"] += weight
        if unit["id"] in matched_ids:
            row["matched_units"] += 1
            row["matched_lexical_weight"] += weight
            if shared:
                matched_shared += weight
            else:
                matched_added += weight
    denominator = sum(v["lexical_weight"] for v in by_file.values())
    numerator = matched_shared + matched_added
    fraction = numerator / denominator if denominator else None
    reported = alignment.get("reference_unit_coverage")
    return {"by_attributed_source_file": by_file, "matched_shared_lexical_weight": matched_shared,
            "matched_added_lexical_weight": matched_added, "matched_total_lexical_weight": numerator,
            "all_units_lexical_weight": denominator, "recomputed_reference_unit_coverage": fraction,
            "matches_reported_coverage": abs(fraction - reported) < 1e-12 if fraction is not None and isinstance(reported, (int, float)) else None,
            "meaning": "Unique matched evidence units, not semantic source coverage or model billing tokens. A rejected candidate can still have evidence alignments.",
            "evidence": [{"path": reference(p), "sha256": digest(p)} for p in (alignment_path, old_units_path, RUN / "artifacts/prepare_units.json")]}


def inspect_first_candidate_resource():
    """Bind one human source/sidecar interpretation to the actual rejected candidate."""
    folder = RUN / "validations/check-001"
    facts_path = folder / "submitted-facts.dl"
    alignment_path = folder / "synthesis_evidence_alignment.json"
    if not facts_path.is_file() or not alignment_path.is_file():
        return None
    facts = facts_path.read_text("utf-8")
    alignment = read(alignment_path)
    units_path = RUN / "artifacts/prepare_units.json"
    units = read(units_path)
    identities = ("dotenvPath", "dotenvCredentials", "dotenvConfig")
    rows = [a for a in alignment["alignments"] if any(v in a.get("args", []) for v in identities)]
    ids = {a.get("evidence_id") for a in rows}
    source_path = BASE / "inputs/ga4/scripts/src/config/settings.ts"
    paths = [facts_path, alignment_path, units_path, source_path,
             BASE / "inputs/ga4/SKILL.md",
             BASE / "source/packages/semia-core/src/semia_core/checker.py",
             BASE / "source/packages/semia-core/src/semia_core/rules/sdl/skill_dl_static_analysis.dl"]
    return {"candidate": "check-001", "facts_sha256": digest(facts_path),
            "related_facts": [{"line": n, "text": line} for n, line in enumerate(facts.splitlines(), 1)
                              if any(f'"{v}"' in line for v in identities)],
            "alignments": rows, "matched_units": [u for u in units["units"] if u["evidence_id"] in ids],
            "interpretation": "dotenvPath is an invented identifier for the implicit .env resource/address: source settings.ts:8 describes a file and :9 calls config() without arguments. The candidate marks that region value sensitive_local, while modeling read contents separately as dotenvCredentials/secret. The address and contents are not merged into one ID.",
            "potential_abstraction_issue": "sensitive_local makes the resource identifier a value_sensitive_source under the pinned SDL rules. This is a candidate-level sensitivity abstraction; neither source-to-fact correctness nor a resulting data leak has been established.",
            "dotenvPath_used_as_call_input_or_output": bool(re.search(r'call_(?:input|output)\([^\n]*"dotenvPath"', facts)),
            "limits": "The whole candidate is rejected. SDL051 is a missing allowed-action policy validation error, not a detector finding. No propagation/leak claim or cross-version measured comparison is made.",
            "evidence": [{"path": reference(p), "sha256": digest(p)} for p in paths]}


def main():
    ISSUES.clear()
    now = datetime.now(timezone.utc)
    runtime = read(RUN / "runtime.json") or {}
    finished = read(RUN / "finished.json")
    metadata = read(RUN / "artifacts/synthesis_metadata.json")
    prepare = read(RUN / "artifacts/prepare_metadata.json")
    units = read(RUN / "artifacts/prepare_units.json")
    denominator = coverage_denominator(BASE / "prepared/ga4/prepare_units.json", RUN / "artifacts/prepare_units.json")
    full_receipt = read(RUN / "artifacts/complete-source-receipt.json")
    inputs = read(BASE / "input-manifest.json")
    case = next(c for c in inputs["cases"] if c["case_id"] == "ga4")
    pin_audit = inspect_pins(runtime, case)
    input_hashes_match = pin_audit["input"]["all_hashes_match"]
    old_prepare = read(BASE / "prepared/ga4/prepare_metadata.json")
    full_paths = prepare["source"]["files"] if prepare else None
    old_paths = old_prepare["source"]["files"] if old_prepare else None
    prepared_path = RUN / "artifacts/prepared_skill.md"
    prepared = prepared_path.read_text("utf-8") if prepared_path.is_file() else None
    prepared_hash_matches_receipt = digest(prepared_path) == full_receipt.get("prepared_sha256") if prepared_path.is_file() and isinstance(full_receipt, dict) else None
    prompt_body = prepared.rstrip("\r\n") if prepared is not None else None
    nonce = prepare.get("hostile_input_nonce") if prepare else None
    calls, pids = [], [runtime.get("controller_pid")]
    for request_path in sorted((RUN / "transport").glob("call-*/request.json")):
        request = read(request_path)
        if not isinstance(request, dict):
            continue
        pids.append(request.get("pid"))
        prompt_path = request_path.parent / "prompt.txt"
        prompt = prompt_path.read_text("utf-8") if prompt_path.is_file() else None
        actual_source_complete = None
        if prompt is not None and nonce and prompt_body is not None:
            blocks = re.findall(re.escape(f"<<<SEMIA_HOSTILE_INPUT id={nonce}>>>") + r"\n(.*?)\n" +
                                re.escape(f"<<<SEMIA_END id={nonce}>>>"), prompt, flags=re.DOTALL)
            actual_source_complete = sum(b.rstrip("\r\n") == prompt_body for b in blocks) == 1
        stdout_path = request_path.parent / "stdout.jsonl"
        events, usages, stdout_parse_errors = [], [], []
        if stdout_path.is_file():
            for line_number, line in enumerate(stdout_path.read_text("utf-8", errors="replace").splitlines(), 1):
                try:
                    event = json.loads(line)
                except ValueError as exc:
                    stdout_parse_errors.append({"line": line_number, "error": str(exc)})
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "turn.completed":
                    usages.append(event.get("usage"))
                if event.get("type") in {"error", "turn.failed"}:
                    events.append(event)
                elif event.get("type") == "item.completed" and event.get("item", {}).get("type") == "error":
                    events.append(event)
        else:
            ISSUES.append({"path": reference(stdout_path), "error": "missing public event stream; usage unknown"})
        usage_audit = usage_reconciliation(usages, request)
        usage = {k: v["complete_value"] for k, v in usage_audit["raw"]["fields"].items()}
        stderr = request_path.parent / "stderr.txt"
        stderr_lines = stderr.read_text("utf-8", errors="replace").splitlines() if stderr.is_file() else []
        if not stderr.is_file():
            ISSUES.append({"path": reference(stderr), "error": "missing stderr; transport-log counts unknown"})
        if not prompt_path.is_file():
            ISSUES.append({"path": reference(prompt_path), "error": "missing prompt; payload integrity unknown"})
        status = ("prestart_failed" if request.get("native_start") is False and request.get("error") else
                  "prestart_pending_or_unknown" if request.get("native_start") is not True else
                  "timed_out" if request.get("timed_out") else "native_failed" if request.get("error") or request.get("returncode") not in (None, 0) else
                  "native_completed" if request.get("returncode") == 0 else "in_progress")
        calls.append({key: request.get(key) for key in ("id", "phase", "pid", "started_at_utc", "native_start", "returncode", "elapsed_seconds", "timed_out", "tree_cleanup_returncode", "tree_cleanup_unresolved", "error", "source_payload_verified", "unexpected_tool_events")}
                     | {"usage": usage, "prompt_bytes": len(prompt.encode("utf-8")) if prompt is not None else None,
                        "prompt_characters": len(prompt) if prompt is not None else None,
                        "outcome_classification": status, "usage_reconciliation": usage_audit,
                        "raw_completed_event_usages": usages, "stdout_parse_errors": stdout_parse_errors,
                        "argv_verification": inspect_argv(request, runtime),
                        "complete_source_receipt_sha256_matches": request.get("complete_source_receipt_sha256") == digest(RUN / "artifacts/complete-source-receipt.json") if (RUN / "artifacts/complete-source-receipt.json").is_file() and request.get("complete_source_receipt_sha256") else None,
                        "prompt_sha256": digest(prompt_path) if prompt_path.is_file() else None,
                        "response_receipt": file_receipt(request_path.parent / "response.txt"),
                        "response_sha256_matches_request": digest(request_path.parent / "response.txt") == request.get("response_sha256") if (request_path.parent / "response.txt").is_file() and request.get("response_sha256") else None,
                        "independently_observed_complete_source_body": actual_source_complete,
                        "public_error_events": events,
                        "transport_log_indicators": {"model_catalog_refresh_timeout_lines": sum("failed to refresh available models" in l for l in stderr_lines) if stderr.is_file() else None,
                                                     "sampling_retry_lines": sum("retrying sampling request" in l for l in stderr_lines) if stderr.is_file() else None,
                                                     "tls_or_reconnect_lines": sum(any(w in l.lower() for w in ("tls", "reconnect", "connection reset")) for l in stderr_lines) if stderr.is_file() else None},
                        "artifact_receipts": [file_receipt(p) for p in (request_path, prompt_path, stdout_path, stderr)],
                        "evidence": [reference(request_path), reference(prompt_path), reference(stdout_path), reference(stderr)]})
    validations = []
    for folder in sorted((RUN / "validations").glob("check-*")):
        invocation = read(folder / "invocation.json")
        payload = read(folder / "return-payload.json")
        check = read(folder / "synthesis_check.json")
        identity = validation_identity(folder, invocation, payload, check)
        usable = identity["usable"]
        issues = check["errors"] if usable else None
        groups = Counter((i.get("code"), re.sub(r"'[^']*'", "'<id>'", i.get("message", ""))) for i in issues or [])
        validations.append({"check": folder.name, "returned": invocation.get("returned") if invocation else None,
                            "invocation_started_at_utc": invocation.get("started_at_utc") if invocation else None,
                            "invocation_facts_path": invocation.get("facts_path") if invocation else None,
                            "submitted_facts_sha256": identity["actual_submitted_sha256"], "identity": identity,
                            "program_valid": check.get("program_valid") if usable else None,
                            "error_count": len(issues) if issues is not None else None,
                            "warning_count": len(check.get("warnings", [])) if usable else None,
                            "errors": issues,
                            "errors_by_code_and_message": [{"code": c, "message_pattern": m, "count": n} for (c, m), n in groups.items()],
                            "evidence_match_rate": check.get("evidence_match_rate") if usable else None,
                            "evidence_support_coverage": check.get("evidence_support_coverage") if usable else None,
                            "reference_unit_coverage": payload.get("reference_unit_coverage") if usable else None,
                            "matched_source_units": inspect_matched_source_units(folder, units) if usable else None,
                            "evidence": [reference(folder / n) for n in ("invocation.json", "return-payload.json", "synthesis_check.json", "submitted-facts.dl")]})
    candidate_paths = sorted((RUN / "artifacts").glob("synthesis_attempt_*_*.dl"),
                             key=lambda p: tuple(map(int, re.findall(r"\d+", p.stem))))
    candidates = [file_receipt(p) for p in candidate_paths]
    selected_path = RUN / "artifacts" / f"synthesized_facts_{metadata.get('selected_iteration')}.dl" if metadata else None
    selected_sha = digest(selected_path) if selected_path and selected_path.is_file() else None
    metadata_path = RUN / "artifacts/synthesis_metadata.json"
    metadata_receipt = file_receipt(metadata_path)
    metadata_receipt["modified_at_utc"] = datetime.fromtimestamp(metadata_path.stat().st_mtime, timezone.utc).isoformat() if metadata_path.is_file() else None
    candidate_audit = map_candidates(candidates, validations, selected_sha, bool(metadata and metadata.get("completed")),
                                     metadata_receipt, str(RUN / "artifacts/synthesized_facts.dl"))
    retry_delivery = inspect_retry_delivery(calls)
    resource_review = inspect_first_candidate_resource()
    detection_path = RUN / "artifacts/detection_result.json"
    detection = read(detection_path)
    started = [c for c in calls if c["native_start"] is True]
    token_totals = {}
    for key in TOKEN_KEYS:
        rows = [c["usage_reconciliation"]["raw"]["fields"][key] for c in started]
        present = [r["known_sum"] for r in rows if r["known_sum"] is not None]
        token_totals[key] = {"known_sum": sum(present) if present else None,
                             "calls_missing_field": sum(r["complete_value"] is None for r in rows),
                             "completion_events_missing_field": sum(r["missing_events"] for r in rows)}
    known_io = [token_totals[k]["known_sum"] for k in ("input_tokens", "output_tokens") if token_totals[k]["known_sum"] is not None]
    source_unchanged = pin_audit["source_and_input_verified"]
    downstream = inspect_downstream(calls, finished, detection)
    observed_counters = {"native_starts": len(started), "cgrs_native_starts": sum(c["phase"] == "cgrs" for c in started),
                         "recommendation_native_starts": sum(c["phase"] == "recommendation" for c in started),
                         "calls_with_visible_usage": sum(any(isinstance(u, dict) for u in c["raw_completed_event_usages"]) for c in calls),
                         "validation_receipts": len(validations)}
    finished_counter_comparisons = {k: {"observed": v, "finished_value": finished.get(k) if finished else None,
                                      "matches": v == finished.get(k) if finished and k in finished else None} for k, v in observed_counters.items()}
    outer_retry_links = [{"previous": a["id"], "next": b["id"], "status": "inferred_same_payload_retry",
                          "evidence": a["evidence"] + b["evidence"]} for a, b in zip(calls, calls[1:])
                         if a["outcome_classification"] in {"native_failed", "timed_out", "prestart_failed"}
                         and a["phase"] == b["phase"] and a["prompt_sha256"] is not None and a["prompt_sha256"] == b["prompt_sha256"]]
    report = {
        "schema": "semia-ga4-read-only-analysis-v2", "observed_at_utc": now.isoformat(),
        "audit_script_receipt": file_receipt(Path(__file__)),
        "observed_at_shanghai": now.astimezone(timezone(timedelta(hours=8))).isoformat(),
        "state": "not_run" if not runtime else "completed" if finished and finished.get("exit_code") == 0 else "failed" if finished else "in_progress",
        "runtime": runtime, "finished": finished, "calls": calls, "validations": validations,
        "input_coverage": {"input_files": len(case["files"]), "input_hashes_match": input_hashes_match,
                           "upstream_default_file_paths": old_paths, "complete_variant_file_paths": full_paths,
                           "added_paths": sorted(set(full_paths) - set(old_paths)) if full_paths is not None and old_paths is not None else None,
                           "semantic_units_by_file": dict(Counter(u["source_file"] for u in units["units"])) if units else None,
                           "semantic_units_total": units.get("total_units") if units else None,
                           "prepared_bytes": prepared_path.stat().st_size if prepared_path.is_file() else None,
                           "prepared_hash_matches_complete_source_receipt": prepared_hash_matches_receipt,
                           "complete_source_receipt": full_receipt,
                           "evidence": ["input-manifest.json", "prepared/ga4/prepare_metadata.json", "comparison/ga4/artifacts/prepare_metadata.json", "comparison/ga4/artifacts/prepare_units.json", "comparison/ga4/artifacts/complete-source-receipt.json"]},
        "synthesis_metadata": metadata,
        "candidate_inventory_and_mapping": candidate_audit,
        "identity_audit": pin_audit,
        "finished_counter_reconciliation": finished_counter_comparisons,
        "downstream_outcomes": downstream,
        "outer_retry_inference": {"links": outer_retry_links, "unlinked_failure_grouping": "unknown", "method": "Only adjacent explicit failure plus identical phase/prompt hash. Never native-start count minus candidates; internal sampling retry log lines are not extra native calls."},
        "retry_feedback_delivery": retry_delivery,
        "first_candidate_resource_review": resource_review,
        "coverage_denominator_analysis": denominator,
        "accounting": {"native_starts_observed": len(started), "public_token_fields": token_totals,
                       "known_input_plus_output_tokens": sum(known_io) if known_io else None,
                       "native_calls_without_usage": sum(not any(isinstance(u, dict) and any(u.get(k) is not None for k in TOKEN_KEYS) for u in c["raw_completed_event_usages"]) for c in started),
                       "cgrs_starts": sum(c["phase"] == "cgrs" for c in started),
                       "recommendation_starts": sum(c["phase"] == "recommendation" for c in started),
                       "by_phase": {phase: phase_usage_summary([c for c in started if c["phase"] == phase]) for phase in ("cgrs", "recommendation")},
                       "basis": "Independent raw stdout turn.completed events, including partial/missing usage fields; request summaries are comparisons only.",
                       "evidence": [p for c in calls for p in c["evidence"]]},
        "detector": detection, "detector_evidence": reference(detection_path),
        "downstream_artifacts": {n: (RUN / "artifacts" / n).is_file() for n in ("detection_result.json", "report.md", "recommendation.md")},
        "source_unchanged": source_unchanged,
        "adapter_unchanged": digest(BASE / "run_comparison.py") == runtime.get("adapter_sha256") if runtime else None,
        "helper_unchanged": digest(BASE / "adapters/complete_source.py") == runtime.get("full_source_helper_sha256") if runtime else None,
        "cli_unchanged": digest(Path(runtime["cli_executable"])) == runtime.get("cli_sha256") if runtime and Path(runtime["cli_executable"]).is_file() else None,
        "pid_observation": inspect_pids(pids, runtime, calls, finished), "read_issues": ISSUES,
        "accuracy": "not_evaluated_no_independent_gold", "audit_model_calls": 0, "audit_pipeline_invocations": 0,
        "limits": ["Complete source delivery does not establish correct source-to-fact modeling or privacy judgments.",
                   "Program validity and evidence matching are upstream checks, not semantic correctness or gold accuracy.",
                   "The 14-file default and 16-file variant have different semantic-unit denominators; coverage scores are not directly comparable.",
                   "Public input+output excludes unknown internal usage; cached/reasoning subcounts are not added again."]}
    (OUT / "ga4-analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    value = lambda v: "unknown" if v is None else str(v)
    lines = ["# GA4 完整源变体：只读观察与结果分析", "", f"观察时点：{report['observed_at_shanghai']}（Asia/Shanghai）；pipeline状态：**{report['state']}**。终态以finished.json为准；没有终态回执时不将本稿称为最终结论。推荐层结果单独判断。", "",
             f"当前已观察 {len(started)} 次native starts，公开input+output合计 {value(report['accounting']['known_input_plus_output_tokens'])} tokens，{report['accounting']['native_calls_without_usage']} 次尚无用量回执。CGRS与recommendation分别为 {report['accounting']['cgrs_starts']}／{report['accounting']['recommendation_starts']} 次；cached和reasoning子计数不重复累加。", "",
             "## 输入与传输", "",
             f"完整源变体包含 {len(full_paths) if full_paths is not None else 'unknown'}/16 文件；相较原版14文件，补入scripts/package.json和scripts/package-lock.json。当前prepare共 {value(units.get('total_units') if units else None)} 语义单元（原版623），prepared为 {value(report['input_coverage']['prepared_bytes'])} 字节。两个版本的覆盖率分母不同，不能把分值变化直接理解为语义质量变化。", "",
             "每个实际请求均独立检查唯一完整的source围栏正文。输入进入prompt、请求成功返回、候选通过校验、产生正确安全判断是不同层次。大输入传输错误仅依据native返回/超时与公开事件判断；模型目录刷新超时等启动日志单独记录，不冒充主请求失败。", "",
             "| 请求 | phase | prompt字节 | 完整正文 | returncode | 秒 |", "|---|---|---:|---|---:|---:|"]
    for call in calls:
        lines.append(f"| {call['id']} | {call['phase']} | {value(call['prompt_bytes'])} | {value(call['independently_observed_complete_source_body'])} | {value(call['returncode'])} | {value(call['elapsed_seconds'])} |")
    lines += ["", "## 独立证据对账", "",
              "公开用量从每份stdout的全部turn.completed事件独立求和，并逐字段对照request.usage与public_turn_usages；缺字段保留unknown。已知input/output的部分和可报告，未知部分不填零；cached/reasoning子计数不重复计费。原生失败、预启动失败与内部采样重试分别记录，不能用native次数减候选数推算外层重试。", "",
              "| 用量字段 | 已知和 | 缺完整字段的native calls | completion缺字段数 |", "|---|---:|---:|---:|"]
    for key, row in token_totals.items():
        lines.append(f"| {key} | {value(row['known_sum'])} | {row['calls_missing_field']} | {row['completion_events_missing_field']} |")
    lines += ["", f"manifest对runtime及首例固定身份、精确inventory、哈希/大小联合核验：{pin_audit['source_and_input_verified']}。source共{pin_audit['source']['actual_file_count']}文件，输入共{pin_audit['input']['actual_file_count']}文件；source manifest未记录大小，独立使用同一SHA绑定官方ZIP的file_size核对。运行生成的pycache排除项逐路径记录。每份实际argv、prepare回执SHA、完整source正文也独立对照。", "",
              f"原始candidate attempt文件{candidate_audit['attempt_file_count']}份／唯一SHA {candidate_audit['unique_candidate_hash_count']}；通过且身份绑定的候选{candidate_audit['valid_candidate_attempt_count']}份，候选校验未知{candidate_audit['unknown_candidate_attempt_count']}份。validation共{candidate_audit['validation_count']}次，其中可用{candidate_audit['usable_validation_count']}次、独立识别最终selected facts复核{candidate_audit['final_recheck_count']}次、同SHA歧义校验{candidate_audit['ambiguous_same_hash_validation_count']}次。最终复核不会增加候选数。", "",
              "候选可先写入文件，再因patch_unmatched跳过checker。因此不按同SHA贪心配对：实际invocation候选路径或唯一SHA才归属；同SHA且无法唯一定位时保持unknown。最终复核另用selected SHA、final facts路径及completed metadata写入早于invocation的顺序证据识别；文件时序不可靠时不强判。阶段用量另记录无completion的native调用和各字段缺失调用数，事件字段齐全不冒充整个阶段用量齐全。", "",
              "每份validation要求实际submitted-facts SHA、invocation SHA、return-payload SHA、复制facts SHA一致，并核对returned无异常、check/payload合法性与错误/警告数；检查JSON自身SHA一并保存。不满足时program_valid及错误数保持unknown，陈旧共享文件不计有效。终态native/阶段/可见用量计数再与finished回执逐项对照。"]
    lines += ["", "## 候选校验与选择", "", "| 检查 | 原版program_valid | errors | warnings | 引文匹配 | 事实支持 | 源单元覆盖 |", "|---|---|---:|---:|---:|---:|---:|"]
    for check in validations:
        lines.append(f"| {check['check']} | {value(check['program_valid'])} | {value(check['error_count'])} | {value(check['warning_count'])} | {value(check['evidence_match_rate'])} | {value(check['evidence_support_coverage'])} | {value(check['reference_unit_coverage'])} |")
    if validations:
        lines += ["", "逐份sidecar还按唯一匹配单位重算reference覆盖率，并分开原14文件共享子集与新增子集；逐文件单位数、词项权重及SHA见JSON。它们是已保存引文的匹配统计，不代表代码操作/隐私语义覆盖，也不是模型计费tokens。"]
        for check in validations:
            matched = check["matched_source_units"]
            if matched:
                lines.append(f"- {check['check']}：匹配词项权重 {matched['matched_total_lexical_weight']} = 原共享子集 {matched['matched_shared_lexical_weight']} + 新增子集 {matched['matched_added_lexical_weight']}；分母 {matched['all_units_lexical_weight']}，重算覆盖率与原sidecar一致：{matched['matches_reported_coverage']}。")
    if retry_delivery:
        lines += ["", "### 实际重试反馈", "",
                  "下表只依据保存的实际payload。分析者可读取详细checker文件，不等于模型获得这些详情；每次原生调用也不是延续上次会话。完整反馈文本及prompt/candidate SHA绑定在机器报告中。", "",
                  "| 请求 | 对应前一检查 | 反馈含SDL错误码 | 含前一完整候选 | 初始prompt前缀相同 |", "|---|---|---|---|---|"]
        for row in retry_delivery:
            lines.append(f"| {row['request']} | {value(row['previous_check'])} | {row['feedback_has_sdl_error_code']} | {value(row['whole_previous_candidate_present'])} | {value(row['base_prompt_equal_before_validation_feedback'])} |")
    if resource_review:
        lines += ["", "### 首候选的策略错误与资源抽象", "",
                  "check-001的199项错误分为：call_evidence_text三参/应二参141项，action_evidence_text三参/应二参50项；5个secret缺value_secret_allowed_action（SDL050）；dotenvPath缺value_sensitive_allowed_action（SDL051）；loadRead和listRead同时标记untrusted与sensitive region（SDL060）2项。这些是候选合法性错误，不是199项安全风险。", "",
                  "call-002实际收到的新增反馈只有errors=199、warnings=382和三项覆盖率，没有详细错误码、出错ID或前一完整候选；其反馈前正文与call-001完全相同。这限制了可定位修复信息，不能以研究者读到完整诊断来声称模型已获完整反馈。", "",
                  "dotenvPath不是源中变量：settings.ts:8注释说从当前目录读取.env，:9为无参config()。候选用dotenvPath表示call_region并声明sensitive_local；内容另用dotenvCredentials/secret表示call_output。因此这是隐式文件地址/资源区域的敏感value抽象，不能说地址和内容已经被合并成同一ID。region引文在sidecar匹配su_3106（settings.ts:8）；内容引文GA4_PRIVATE_KEY=匹配su_9（SKILL.md:21），匹配分数仅1/6。", "",
                  "上游规则会由sensitive_local导出value_sensitive_source，因此该资源标识存在被按敏感value处理的抽象问题；但dotenvPath没有成为call_input或call_output，整份候选被拒，尚不能据此声称已发生资源-as-data传播错误或泄漏误报。SDL051只是在要求声明允许的action。本结论绑定check-001原始facts与sidecar，不与历史SkillFlow结果拼成跨版本实测比较。"]
    lines += ["", f"已记录 {len(validations)} 份逐次校验。selected_iteration={value(metadata.get('selected_iteration') if metadata else None)}；stop_reason={value(metadata.get('stop_reason') if metadata else None)}。具体错误消息、候选哈希及对应证据路径见机器报告。program_valid或evidence_match_rate通过均不能证明接收方、字段、条件和任务依据已经正确绑定。", "",
              "## 完整源适配对覆盖分母和停止条件的影响", "",
              "上游reference_unit_coverage按每个语义单元的词法词项数加权，不是简单的单位个数比例，更不是模型计费tokens。按(source_file, unit_type, text, line_start, line_end)多重集匹配，原14文件的623个单位全部保留、没有原单位消失或正文源行边界变化；它们的共同权重为3852。unit ID可随插入移动，因此没有用ID相等来冒充身份相等。", "",
              "完整16文件权重为12865。新增2532个单位的权重9013来自：package-lock.json的2513单位/8955权重，package.json的17单位/51权重，以及两个新增文件标题的7权重。标题scripts/package-lock.json与scripts/package.json由上游标为SKILL.md的heading、line0；它们是生成的包装标题，不是新增SKILL.md正文。", "",
              "条件计算：若原623单位全部匹配、新增单位完全未匹配，并且evidence_match_rate与evidence_support_coverage均为1，则评分为0.5+0.3+0.2×(3852/12865)≈0.8599，低于默认0.9提前停止阈值。这仅说明完整源适配会改变同一评分公式的分母及可能的停止行为，不是已观测候选、已经证明的失败原因或原版14文件Semia结果。本次未调整评分、阈值或重跑。两份单位文件及公式源码的SHA保存在机器报告。", "",
              "## 检测与终态", "",
              f"detector status：{value(detection.get('status') if isinstance(detection, dict) else None)}。未产出检测结果时，结论保持unknown；不能按零风险计数。报告与recommendation的实际产物状态见JSON。当前没有独立金标，不报告精度、召回、F1或SkillFlow优劣。", "",
              f"report.md状态：{downstream['report']['status']}；recommendation状态：{downstream['recommendation']['status']}。实际文本、原始response的格式化一致性和非致命skipped错误分别保存。pipeline exit 0不代表推荐层成功；推荐文本仍需按源和detector逐项审阅，属于模型意见/条件建议，不自动升级为检测事实。", "",
              f"源文件、输入哈希、适配器、helper、CLI的只读一致性观察分别为：{source_unchanged}、{input_hashes_match}、{report['adapter_unchanged']}、{report['helper_unchanged']}、{report['cli_unchanged']}。记录PID是否全部缺席：{report['pid_observation']['all_recorded_pids_absent']}；若有同PID进程，以启动时间区别PID重用。", "",
              f"进程观察时点：{report['pid_observation']['observed_at_utc']}；观察是否晚于终态：{value(report['pid_observation'].get('observation_after_terminal'))}。记录PID及当前可见子孙进程全部缺席：{value(report['pid_observation'].get('all_recorded_pids_and_observable_descendants_absent'))}。直接父子关系、启动时间、timeout cleanup flags及finished SHA随观察绑定；无法观察的已脱离祖先关系不宣称清零，root wrapper退出另需独立回执。", "",
              "所有字段的机器值和来源见 [ga4-analysis.json](ga4-analysis.json)。本脚本只读取产物和查询记录PID，不启动模型、pipeline或回放，也不停止进程。"]
    (OUT / "ga4-analysis.zh.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"state": report["state"], "native_starts": len(started), "validations": len(validations),
                      "valid_checks": sum(v["program_valid"] is True for v in validations), "complete_payloads": sum(c["independently_observed_complete_source_body"] is True for c in calls),
                      "known_tokens": report["accounting"]["known_input_plus_output_tokens"], "all_recorded_pids_absent": report["pid_observation"]["all_recorded_pids_absent"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
