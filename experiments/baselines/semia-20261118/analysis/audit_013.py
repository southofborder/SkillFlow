"""Read only comparison/013 and pinned source; write derived analysis only."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "comparison/013"
OUT = BASE / "analysis"
READ_ISSUES: list[dict] = []
TOKEN_FIELDS = ("input_tokens", "output_tokens", "cached_input_tokens", "cache_write_input_tokens", "reasoning_output_tokens")


def digest(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        READ_ISSUES.append({"path":str(path),"error":type(exc).__name__})
        return None


def read(path: Path, default=None):
    try:
        return json.loads(path.read_text("utf-8-sig"))
    except (OSError, UnicodeError, ValueError) as exc:
        READ_ISSUES.append({"path":str(path),"error":type(exc).__name__})
        return default


def read_text(path: Path) -> str | None:
    try:
        return path.read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        READ_ISSUES.append({"path":str(path),"error":type(exc).__name__})
        return None


def numeric(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def usage_audit(stdout: str | None, record: dict) -> dict:
    """Raw completion events are authoritative; absent fields never become zero."""
    completions, event_errors, malformed = [], [], []
    item_types = Counter()
    for number, line in enumerate((stdout or "").splitlines(), 1):
        try:
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("non-object event")
        except ValueError:
            malformed.append(number)
            continue
        if event.get("type") == "turn.completed":
            completions.append(event.get("usage") if isinstance(event.get("usage"),dict) else None)
        if event.get("type") in {"error","turn.failed"}:
            event_errors.append(event)
        if event.get("type") == "item.completed":
            item_types[event.get("item",{}).get("type","unknown")] += 1
    request_usage = record.get("usage")
    fields = set(TOKEN_FIELDS)
    for usage in completions:
        if usage:
            fields.update(usage)
    if isinstance(request_usage,dict):
        fields.update(request_usage)
    sums, comparisons = {}, {}
    for key in sorted(fields):
        values = [u.get(key) if u else None for u in completions]
        known = [v for v in values if numeric(v)]
        missing = len(values)-len(known)
        exact = sum(known) if values and missing == 0 and not malformed else None
        sums[key] = {"known_sum":sum(known),"missing_event_count":missing,
                     "events_with_field":len(known),"exact_sum":exact}
        recorded = request_usage.get(key) if isinstance(request_usage,dict) else None
        comparisons[key] = {"raw_exact_sum":exact,"request_value":recorded,
            "status":"unknown_raw" if exact is None else "missing_request_field" if not numeric(recorded)
                     else "match" if recorded==exact else "mismatch"}
    raw_dict_usages = [u for u in completions if u is not None]
    public = record.get("public_turn_usages")
    public_status = ("unknown_raw" if stdout is None or malformed else
                     "missing_request_field" if not isinstance(public,list) else
                     "match" if public==raw_dict_usages else "mismatch")
    return {"stdout_available":stdout is not None,"completion_event_count":len(completions),
        "completion_events_missing_usage":sum(u is None for u in completions),
        "raw_turn_usages":completions,"fields":sums,"request_usage_comparison":comparisons,
        "request_public_turn_usages_comparison":public_status,"malformed_event_lines":malformed,
        "public_error_events":event_errors,"public_item_types":dict(item_types),
        "input_plus_output_exact":(sums["input_tokens"]["exact_sum"]+sums["output_tokens"]["exact_sum"])
            if all(sums[k]["exact_sum"] is not None for k in ("input_tokens","output_tokens")) else None}


def aggregate_usage(calls: list[dict]) -> dict:
    started = [c for c in calls if c.get("native_start")]
    unknown_starts = sum(c.get("native_start") is None for c in calls)
    fields = {}
    for key in TOKEN_FIELDS:
        entries = [c["raw_usage_audit"]["fields"][key] for c in started]
        missing_calls = sum(e["exact_sum"] is None for e in entries)+unknown_starts
        fields[key] = {"known_sum":sum(e["known_sum"] for e in entries),
                       "missing_event_count":sum(e["missing_event_count"] for e in entries),
                       "calls_with_unknown_total":missing_calls,
                       "exact_sum":sum(e["exact_sum"] for e in entries) if not missing_calls else None}
    fields["input_plus_output_tokens"] = {
        "known_sum":fields["input_tokens"]["known_sum"]+fields["output_tokens"]["known_sum"],
        "exact_sum":fields["input_tokens"]["exact_sum"]+fields["output_tokens"]["exact_sum"]
            if all(fields[k]["exact_sum"] is not None for k in ("input_tokens","output_tokens")) else None}
    return fields


def prompt_binding(prompt: str | None, prepared: str | None, nonce: str | None,
                   prepared_sha: str | None, receipt: dict | None,
                   actual_receipt_sha: str | None, request_receipt_sha: str | None) -> dict:
    complete_count = body_occurrences = None
    if prompt is not None and prepared is not None and isinstance(nonce,str) and nonce:
        body = prepared.rstrip("\r\n")
        begin = re.escape(f"<<<SEMIA_HOSTILE_INPUT id={nonce}>>>")
        end = re.escape(f"<<<SEMIA_END id={nonce}>>>")
        blocks = re.findall(begin+r"\n(.*?)\n"+end,prompt,flags=re.DOTALL)
        complete_count = sum(block.rstrip("\r\n")==body for block in blocks)
        body_occurrences = prompt.count(body) if body else 0
    checks = {"receipt_hash_matches_request":bool(actual_receipt_sha) and actual_receipt_sha==request_receipt_sha,
              "prepared_hash_matches_receipt":bool(prepared_sha) and isinstance(receipt,dict) and prepared_sha==receipt.get("prepared_sha256"),
              "receipt_all_files_present":isinstance(receipt,dict) and receipt.get("all_files_present") is True,
              "unique_complete_fenced_body":complete_count==1,"unique_body_occurrence":body_occurrences==1}
    return {"checks":checks,"verified":all(checks.values()),"complete_fenced_body_count":complete_count,
            "source_body_occurrence_count":body_occurrences,"actual_receipt_sha256":actual_receipt_sha}


def argv_binding(argv, runtime: dict, directory: Path) -> dict:
    args=argv if isinstance(argv,list) else []
    def values(flag):
        return [args[i+1] for i,a in enumerate(args[:-1]) if a==flag]
    config=[s for s in values("-c") if isinstance(s,str)]
    checks={"executable":bool(args) and args[0]==runtime["cli_executable"],
            "model":values("--model")==[runtime["model"]],
            "effort":[s for s in config if s.startswith("model_reasoning_effort=")]==[f'model_reasoning_effort="{runtime["reasoning_effort"]}"'],
            "provider":[s for s in config if s.startswith("model_provider=")]==[f'model_provider="{runtime["model_provider"]}"'],
            "response_destination":values("--output-last-message")==[str(directory/"response.txt")],
            "ignore_user_config":"--ignore-user-config" in args,"ignore_rules":"--ignore-rules" in args}
    return {"verified":all(checks.values()),"checks":checks}


def offline_check(source: str, threshold: float) -> tuple[dict, dict]:
    """Only original deterministic parser/checker/alignment; no pipeline entry point."""
    sys.dont_write_bytecode = True
    source_root=str(BASE/"source/packages/semia-core/src")
    if source_root not in sys.path:
        sys.path.insert(0,source_root)
    from semia_core.artifacts import CheckIssue, CheckResult
    from semia_core.checker import CheckOptions, check_program, compute_ssa_input_availability
    from semia_core.evidence import align_evidence_text
    from semia_core.facts import parse_facts
    from semia_core.pipeline import _load_prepare_units, _check_payload, _alignment_payload
    program=parse_facts(source)
    check=check_program(program,options=CheckOptions(require_include=True))
    evidence=align_evidence_text(program,_load_prepare_units(RUN/"artifacts"))
    if threshold > 0 and evidence.evidence_match_rate < threshold:
        issue=CheckIssue(code="EVD020",line=0,severity="error",message=(
            f"evidence_match_rate {evidence.evidence_match_rate:.3f} below taint threshold "
            f"{threshold:.3f}; facts reference text not present in prepared_skill.md "
            "(possible hallucination or prompt-injection-induced facts)"))
        check=CheckResult(issues=check.issues+(issue,),program_valid=False,evidence_support_coverage=check.evidence_support_coverage)
    return (_check_payload(check,ssa_input_availability=compute_ssa_input_availability(program),
                           evidence_taint_threshold=threshold,evidence_match_rate=evidence.evidence_match_rate),
            _alignment_payload(evidence))


def validation_binding(actual_sha, invocation, payload, check, copied_sha,
                       recomputed_check, alignment, recomputed_alignment) -> dict:
    invocation=invocation if isinstance(invocation,dict) else {}
    payload=payload if isinstance(payload,dict) else {}
    check=check if isinstance(check,dict) else {}
    expected_return={"program_valid":check.get("program_valid"),
                     "errors":len(check["errors"]) if isinstance(check.get("errors"),list) else None,
                     "warnings":len(check["warnings"]) if isinstance(check.get("warnings"),list) else None}
    for key in ("evidence_match_rate","evidence_support_coverage","ssa_input_availability","evidence_taint_threshold"):
        expected_return[key]=check.get(key)
    expected_return["reference_unit_coverage"]=recomputed_alignment.get("reference_unit_coverage") if isinstance(recomputed_alignment,dict) else None
    checks={"invocation_returned":invocation.get("returned") is True and invocation.get("error") is None,
            "actual_equals_invocation_sha":bool(actual_sha) and actual_sha==invocation.get("submitted_facts_sha256"),
            "actual_equals_return_payload_sha":bool(actual_sha) and actual_sha==payload.get("synthesized_facts_sha256"),
            "copied_synthesized_facts_equal_submitted":bool(actual_sha) and copied_sha==actual_sha,
            "complete_check_matches_submitted_recompute":bool(check) and recomputed_check==check,
            "alignment_matches_submitted_recompute":isinstance(alignment,dict) and recomputed_alignment==alignment,
            "check_payload_fields_agree":all(value is not None and payload.get(key)==value for key,value in expected_return.items()),
            "status_agrees":payload.get("status")==("checked" if check.get("program_valid") is True else "check_failed")}
    usable=all(checks.values())
    return {"checks":checks,"usable":usable,"accepted_valid":usable and check.get("program_valid") is True}


def fresh_process_observation(runtime: dict, calls: list[dict], finished: dict) -> dict:
    recorded=[{"pid":runtime["controller_pid"],"role":"controller","started_at_utc":runtime["started_at_utc"]}]
    recorded += [{"pid":c["pid"],"role":c["id"],"started_at_utc":c.get("started_at_utc")} for c in calls if c.get("native_start") and c.get("pid")]
    observation={"observed_at_utc":datetime.now(timezone.utc).isoformat(),"finished_sha256":digest(RUN/"finished.json"),
                 "finished_at_utc":finished.get("finished_at_utc"),"recorded_processes":recorded,
                 "scope":"fresh recorded PIDs plus observable direct children and descendants; no termination; wrapper session not independently observed"}
    observation["native_records_missing_pid"]=[c["id"] for c in calls if c.get("native_start") and not c.get("pid")]
    observation["observation_after_finished"]=(datetime.fromisoformat(observation["observed_at_utc"])>=datetime.fromisoformat(finished["finished_at_utc"])) if finished.get("finished_at_utc") else None
    query=("[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); "
           "@(Get-CimInstance Win32_Process -ErrorAction Stop | Select-Object ProcessId,ParentProcessId,Name,"
           "@{Name='created_utc';Expression={$_.CreationDate.ToUniversalTime().ToString('o')}},CommandLine) | ConvertTo-Json -Compress")
    try:
        completed=subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-Command",query],capture_output=True,timeout=30,
                                 creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        if completed.returncode != 0:
            raise RuntimeError(f"process inspection exit {completed.returncode}")
        processes=json.loads(completed.stdout.decode("utf-8-sig"))
        if not isinstance(processes,list):
            processes=[processes]
        by_pid={p["ProcessId"]:p for p in processes}
        ids={p["pid"] for p in recorded}
        observations=[]
        for item in recorded:
            live=by_pid.get(item["pid"])
            state="absent"
            if live:
                expected=datetime.fromisoformat(item["started_at_utc"])
                actual=datetime.fromisoformat(live["created_utc"])
                delta=(actual-expected).total_seconds()
                state="present_matching_start" if -2<=delta<=10 else "pid_reused_or_start_unconfirmed"
            observations.append(item|{"state":state,"current_name":live.get("Name") if live else None,
                                       "current_created_utc":live.get("created_utc") if live else None,
                                       "current_parent_pid":live.get("ParentProcessId") if live else None})
        direct_children=[{"pid":p["ProcessId"],"parent_pid":p["ParentProcessId"],"name":p["Name"],
                          "created_utc":p["created_utc"],"also_recorded_pid":p["ProcessId"] in ids,
                          "run_path_in_commandline":str(RUN).lower() in (p.get("CommandLine") or "").lower()}
                         for p in processes if p["ParentProcessId"] in ids]
        descendants=[]
        seen=set(ids)
        frontier=set(ids)
        depth=1
        while frontier:
            new=[p for p in processes if p["ParentProcessId"] in frontier and p["ProcessId"] not in seen]
            for p in new:
                descendants.append({"pid":p["ProcessId"],"parent_pid":p["ParentProcessId"],"depth":depth,
                                    "name":p["Name"],"created_utc":p["created_utc"],
                                    "run_path_in_commandline":str(RUN).lower() in (p.get("CommandLine") or "").lower(),
                                    "ownership":"ancestry_match_requires_PID_reuse_review"})
            frontier={p["ProcessId"] for p in new}
            seen.update(frontier)
            depth+=1
        observation.update(status="observed",recorded_process_observations=observations,
                           direct_children=direct_children,observable_descendants=descendants,
                           all_recorded_absent=all(p["state"]=="absent" for p in observations) and not observation["native_records_missing_pid"],
                           no_observable_descendants=not descendants)
    except Exception as exc:
        observation.update(status="inspection_failed",error=f"{type(exc).__name__}: {exc}",all_recorded_absent=None)
    observation["completed_at_utc"]=datetime.now(timezone.utc).isoformat()
    return observation


def output_snapshot(path: Path) -> dict:
    content=read_text(path)
    return {"exists":path.exists(),"path":str(path),"sha256":digest(path) if path.exists() else None,
            "content":content,"nonempty":bool(content and content.strip())}


def downstream_outcomes(finished, detection, report, recommendation, calls, terminal_text) -> dict:
    pipeline="in_progress" if finished is None else "completed" if finished.get("exit_code")==0 else "failed"
    rec_calls=[c for c in calls if c.get("phase")=="recommendation"]
    rec_skipped="recommendation skipped" in terminal_text
    rec_status=("failed_nonfatal" if rec_skipped else "completed_content_requires_review" if recommendation["nonempty"] else
                "in_progress" if rec_calls and finished is None else
                "failed" if rec_calls and finished is not None else "not_run" if pipeline=="failed" else
                "pending" if finished is None else "unknown_missing_output")
    return {"pipeline":pipeline,"pipeline_exit_code":finished.get("exit_code") if finished else None,
            "detector":"not_run" if detection is None and pipeline=="failed" else "pending" if detection is None and finished is None else
                "unknown_missing_output" if detection is None else "completed" if detection.get("status")=="ok" else detection.get("status","unknown"),
            "report":"completed" if report["nonempty"] else "not_run" if pipeline=="failed" else "pending" if finished is None else "unknown_missing_output",
            "recommendation":rec_status,"recommendation_failure_is_nonfatal_upstream":True,
            "recommendation_evidence_conflict":rec_skipped and recommendation["nonempty"],
            "recommendation_content_review":"not_reached" if not recommendation["nonempty"] else "requires_source_and_detector_review",
            "recommendation_is_independent_model_opinion":True}


def main() -> None:
    READ_ISSUES.clear()
    runtime = read(RUN / "runtime.json")
    finished=read(RUN/"finished.json") if (RUN/"finished.json").exists() else None
    pins=read(BASE/"source-manifest.json")
    source_changed=[row["path"] for row in pins["files"] if digest(BASE/"source"/row["path"])!=row["sha256"]]
    expected_source={row["path"] for row in pins["files"]}
    actual_source={p.relative_to(BASE/"source").as_posix() for p in (BASE/"source").rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts and p.suffix!=".pyc"}
    source_inventory={"missing":sorted(expected_source-actual_source),"extra":sorted(actual_source-expected_source)}
    prepared=read_text(RUN/"artifacts/prepared_skill.md")
    receipt=read(RUN/"artifacts/complete-source-receipt.json")
    receipt_sha=digest(RUN/"artifacts/complete-source-receipt.json")
    metadata=read(RUN/"artifacts/prepare_metadata.json") or {}
    synthesis_metadata=read(RUN/"artifacts/synthesis_metadata.json") if (RUN/"artifacts/synthesis_metadata.json").exists() else None
    candidate_paths = sorted((RUN / "artifacts").glob("synthesis_attempt_*.dl"))
    candidate_by_sha = {}
    for path in candidate_paths:
        candidate_by_sha.setdefault(digest(path), []).append(path.name)
    validations = []
    aggregate = Counter()
    arity_totals = Counter()
    for folder in sorted((RUN / "validations").glob("check-*")):
        invocation = read(folder / "invocation.json")
        submitted = folder / "submitted-facts.dl"
        # invocation.json is written last. Pending snapshots may be incomplete.
        if invocation is None:
            validations.append({"id":folder.name,"state":"pending_snapshot"})
            continue
        sha = digest(submitted) if submitted.exists() else None
        check = read(folder / "synthesis_check.json") if invocation.get("returned") else None
        payload = read(folder / "return-payload.json") if invocation.get("returned") else None
        alignment = read(folder / "synthesis_evidence_alignment.json") if invocation.get("returned") else None
        errors = check.get("errors") if isinstance(check,dict) else None
        warnings = check.get("warnings") if isinstance(check,dict) else None
        recomputed_check=recomputed_alignment=None
        recheck_error=None
        source=read_text(submitted)
        try:
            if source is not None and check is not None and not source_changed and not any(source_inventory.values()):
                threshold=check.get("evidence_taint_threshold")
                if not numeric(threshold):
                    raise ValueError("missing numeric taint threshold")
                recomputed_check,recomputed_alignment=offline_check(source,threshold)
        except Exception as exc:
            recheck_error=f"{type(exc).__name__}: {exc}"
        binding=validation_binding(sha,invocation,payload,check,digest(folder/"synthesized_facts.dl"),
                                   recomputed_check,alignment,recomputed_alignment)
        if binding["usable"]:
            aggregate.update(x["code"] for x in errors)
            arity_totals.update(x["message"] for x in errors if x["code"]=="SDL003")
        validations.append({
            "id":folder.name,"state":"bound_returned" if binding["usable"] else "unbound_returned" if invocation.get("returned") else "check_exception",
            "submitted_facts_sha256":sha,
            "submitted_hash_matches_receipt":bool(sha) and sha==invocation.get("submitted_facts_sha256"),
            "matching_candidate_files":candidate_by_sha.get(sha, []),
            "invocation":invocation,"return_payload":payload,
            "binding":binding,"recheck_error":recheck_error,"independent_check":recomputed_check,
            "reported_program_valid":check.get("program_valid") if check else None,
            "program_valid":check.get("program_valid") if binding["usable"] else None,
            "errors":errors,"warnings":warnings,
            "bound_error_count":len(errors) if binding["usable"] else None,
            "bound_warning_count":len(warnings) if binding["usable"] else None,
            "error_codes":dict(Counter(x["code"] for x in errors)) if isinstance(errors,list) else None,
            "arity_messages":dict(Counter(x["message"] for x in errors if x["code"]=="SDL003")) if isinstance(errors,list) else None,
            "evidence_match_rate":check.get("evidence_match_rate") if check else None,
            "evidence_support_coverage":check.get("evidence_support_coverage") if check else None,
            "reference_unit_coverage":payload.get("reference_unit_coverage") if payload else None,
            "alignment_present":alignment is not None,
        })
    calls = []
    for path in sorted((RUN / "transport").glob("call-*/request.json")):
        record=read(path)
        if not isinstance(record,dict):
            calls.append({k:None for k in ("phase","native_start","pid","returncode","elapsed_seconds","usage","error","timed_out","prompt_sha256")}
                         | {"id":path.parent.name,"request_read_issue":True,"classification":"unknown_request_unreadable",
                            "raw_usage_audit":usage_audit(read_text(path.parent/"stdout.jsonl"),{}),"sampling_retry_lines":[]})
            continue
        stderr=read_text(path.parent/"stderr.txt")
        stdout=read_text(path.parent/"stdout.jsonl")
        accounting=usage_audit(stdout,record)
        prompt=read_text(path.parent/"prompt.txt")
        prompt_check=prompt_binding(prompt,prepared,metadata.get("hostile_input_nonce"),digest(RUN/"artifacts/prepared_skill.md"),
                                    receipt,receipt_sha,record.get("complete_source_receipt_sha256"))
        classification=("prestart_failure" if not record.get("native_start") and record.get("error") else
                        "prestart_pending" if not record.get("native_start") else "native_timeout" if record.get("timed_out") else
                        "native_in_progress" if record.get("returncode") is None else "native_failed" if record["returncode"]!=0 else
                        "native_completed_adapter_error" if record.get("error") else "native_completed")
        calls.append({k:record.get(k) for k in ("id","phase","native_start","pid","started_at_utc","returncode","elapsed_seconds","usage","error","timed_out","tree_cleanup_returncode","tree_cleanup_unresolved","source_payload_verified","unexpected_tool_events")}
                     | {"prompt_sha256":digest(path.parent/"prompt.txt"),
                        "classification":classification,"raw_usage_audit":accounting,
                        "prompt_binding":prompt_check,"argv_binding":argv_binding(record.get("argv"),runtime,path.parent),
                        "response_sha256_actual":digest(path.parent/"response.txt") if (path.parent/"response.txt").exists() else None,
                        "response_sha256_recorded":record.get("response_sha256"),
                        "public_error_events":accounting["public_error_events"],"public_item_types":accounting["public_item_types"],
                        "sampling_retry_lines":[line for line in (stderr or "").splitlines() if "retrying sampling request" in line]})
    raw_accounting=aggregate_usage(calls)
    totals={k:v["known_sum"] for k,v in raw_accounting.items()}
    phase_accounting={phase:aggregate_usage([c for c in calls if c.get("phase")==phase]) for phase in ("cgrs","recommendation")}
    retry_edges=[]
    for previous,current in zip(calls,calls[1:]):
        if (previous.get("error","") or "").startswith("LlmSynthesisError:") and previous.get("phase")==current.get("phase") and previous.get("prompt_sha256") and previous.get("prompt_sha256")==current.get("prompt_sha256"):
            retry_edges.append({"failed_request":previous["id"],"next_request":current["id"],"basis":"explicit LlmSynthesisError plus adjacent same phase and prompt; consistent with original provider retry; structural-attempt identity not inferred"})
    valid_sha=sorted({v["submitted_facts_sha256"] for v in validations if v.get("program_valid") is True})
    inputs=read(BASE/"input-manifest.json")
    input_case=next(c for c in inputs["cases"] if c["case_id"]=="013")
    input_changed=[row["path"] for row in input_case["files"] if digest(BASE/input_case["path"]/row["path"])!=row["sha256"]]
    input_root=BASE/input_case["path"]
    actual_input={p.relative_to(input_root).as_posix() for p in input_root.rglob("*") if p.is_file()}
    expected_input={row["path"] for row in input_case["files"]}
    input_inventory={"missing":sorted(expected_input-actual_input),"extra":sorted(actual_input-expected_input),
        "size_mismatches":[row["path"] for row in input_case["files"] if not (input_root/row["path"]).is_file() or (input_root/row["path"]).stat().st_size!=row["size"]]}
    first_runtime=read(BASE/"pilot/001/runtime.json") or {}
    report_snapshot=output_snapshot(RUN/"artifacts/report.md")
    recommendation_snapshot=output_snapshot(RUN/"artifacts/recommendation.md")
    detection=read(RUN/"artifacts/detection_result.json") if (RUN/"artifacts/detection_result.json").exists() else None
    terminal_text=read_text(RUN/"console-stderr.txt") or ""
    outcomes=downstream_outcomes(finished,detection,report_snapshot,recommendation_snapshot,calls,terminal_text)
    process_observation=fresh_process_observation(runtime,calls,finished) if finished else {"status":"not_terminal_not_observed","observed_at_utc":None}
    if finished:
        (OUT/"013-process-observation.json").write_text(json.dumps(process_observation,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    observed_counts={"native_starts":sum(bool(c.get("native_start")) for c in calls),
        "cgrs_native_starts":sum(bool(c.get("native_start")) and c.get("phase")=="cgrs" for c in calls),
        "recommendation_native_starts":sum(bool(c.get("native_start")) and c.get("phase")=="recommendation" for c in calls),
        "calls_with_visible_usage":sum(any(isinstance(u,dict) for u in c["raw_usage_audit"]["raw_turn_usages"]) for c in calls),
        "validation_receipts":sum(v.get("state")!="pending_snapshot" for v in validations)}
    finished_reconciliation={key:{"observed":value,"recorded":finished.get(key),"match":finished.get(key)==value}
                             for key,value in observed_counts.items()} if finished else None
    wrapper_exit=read(OUT/"013-wrapper-exit.json") if (OUT/"013-wrapper-exit.json").exists() else None
    wrapper_binding={"source":"root-supplied tools.write_stdin receipt; not independently re-polled by audit",
                     "receipt":wrapper_exit,
                     "finished_hash_matches":bool(finished) and isinstance(wrapper_exit,dict) and wrapper_exit.get("finished_sha256")==digest(RUN/"finished.json"),
                     "pipeline_exit_agrees":bool(finished) and isinstance(wrapper_exit,dict) and wrapper_exit.get("upstream_pipeline_exit_code")==finished.get("exit_code")}
    selected_sha=digest(RUN/"artifacts/synthesized_facts.dl") if synthesis_metadata and synthesis_metadata.get("selected_iteration") is not None else None
    seen_sha=set()
    for index,validation in enumerate(validations):
        sha=validation.get("submitted_facts_sha256")
        validation["identity_kind"]=("selected_facts_final_recheck" if finished and selected_sha is not None and index==len(validations)-1 and sha==selected_sha and sha in seen_sha and synthesis_metadata.get("completed") else
            "repeated_validation_of_same_hash" if sha in seen_sha else "first_validation_of_candidate_hash" if validation.get("matching_candidate_files") else "unmatched_validation")
        seen_sha.add(sha)
    rec_responses=[]
    for call in calls:
        if call.get("phase")=="recommendation":
            snap=output_snapshot(RUN/"transport"/call["id"]/"response.txt")
            rec_responses.append({"call":call["id"],"returncode":call.get("returncode"),"error":call.get("error"),
                                  "successful_transport":call.get("classification")=="native_completed",
                                  "response_sha_matches_request":bool(snap["sha256"]) and snap["sha256"]==call.get("response_sha256_recorded")}|snap)
    rec_output_bound=any(s["successful_transport"] and s["response_sha_matches_request"] and s["content"] is not None and recommendation_snapshot["content"] is not None and s["content"].strip()==recommendation_snapshot["content"].strip() for s in rec_responses)
    if recommendation_snapshot["nonempty"] and not rec_output_bound and outcomes["recommendation"]!="failed_nonfatal":
        outcomes["recommendation"]="unknown_unbound_output"
    input_prepared_match=prepared==read_text(input_root/"SKILL.md")
    integrity={"source_manifest_matches_runtime":digest(BASE/"source-manifest.json")==runtime["source_manifest_sha256"],
               "source_manifest_matches_first_pilot_file_hashes":{row["path"]:row["sha256"] for row in pins["files"]}==first_runtime.get("source_file_hashes"),
               "input_manifest_matches_runtime":digest(BASE/"input-manifest.json")==runtime["input_manifest_sha256"],
               "input_manifest_matches_first_pilot":runtime["input_manifest_sha256"]==first_runtime.get("input_manifest_sha256"),
               "source_inventory_exact":not any(source_inventory.values()) and len(expected_source)==360 and len(pins["files"])==360,
               "source_hashes_unchanged":not source_changed,
               "input_inventory_and_sizes_exact":not any(input_inventory.values()),"input_hashes_unchanged":not input_changed,
               "prepared_013_body_matches_pinned_single_input":input_prepared_match,
               "cli_unchanged":digest(Path(runtime["cli_executable"]))==runtime["cli_sha256"],
               "adapter_unchanged":digest(BASE/"run_comparison.py")==runtime["adapter_sha256"],
               "helper_unchanged":digest(BASE/"adapters/complete_source.py")==runtime["full_source_helper_sha256"]}
    integrity_reconciliation={"independent_checks":integrity,"all_independent_checks_pass":all(integrity.values()),
        "runner_source_and_input_unchanged":finished.get("source_and_input_unchanged") if finished else None,
        "runner_integrity_error":finished.get("integrity_error") if finished else None,
        "runner_agrees_with_independent_source_input_checks":(finished.get("source_and_input_unchanged") is True and finished.get("integrity_error") is None and all(integrity[k] for k in ("source_manifest_matches_runtime","source_inventory_exact","source_hashes_unchanged","input_manifest_matches_runtime","input_inventory_and_sizes_exact","input_hashes_unchanged"))) if finished else None}
    result={
        "schema":"semia-013-readonly-analysis-v2","observed_at_utc":datetime.now(timezone.utc).isoformat(),
        "status":"finished" if finished else "in_progress","runtime":runtime,"finished":finished,
        "candidate_file_count":len(candidate_paths),"validation_count":len(validations),
        "valid_validation_count":sum(v.get("program_valid") is True for v in validations),
        "unique_valid_candidate_count":len(valid_sha),"valid_candidate_sha256":valid_sha,
        "candidate_inventory":[{"file":p.name,"sha256":digest(p),"bytes":p.stat().st_size} for p in candidate_paths],
        "unique_candidate_hash_count":len(candidate_by_sha),"selected_facts_sha256":selected_sha,
        "unbound_validation_count":sum(v.get("state")!="bound_returned" for v in validations),
        "validations":validations,"aggregate_error_counts":dict(aggregate),"calls":calls,
        "aggregate_arity_messages":dict(arity_totals),
        "rejected_without_arity_errors":[v['id'] for v in validations if v.get('program_valid') is False and not v['arity_messages']],
        "calls_identical_to_initial_prompt":[c['id'] for c in calls if c.get('prompt_sha256') and c['prompt_sha256']==calls[0].get('prompt_sha256')],
        "native_requests_over_600_seconds":[c['id'] for c in calls if c.get('elapsed_seconds') is not None and c['elapsed_seconds']>600],
        "native_starts":sum(bool(c["native_start"]) for c in calls),
        "known_public_usage":totals,"public_usage_accounting":raw_accounting,"public_usage_by_phase":phase_accounting,
        "usage_missing_count":sum(bool(c.get("native_start")) and c["raw_usage_audit"]["input_plus_output_exact"] is None for c in calls),
        "finished_counter_reconciliation":finished_reconciliation,
        "wrapper_exit_observation":wrapper_binding,
        "native_returncode_counts":dict(Counter(str(c.get("returncode")) for c in calls if c.get("native_start"))),
        "outer_provider_retry_edges":retry_edges,"outer_retry_grouping_limit":"Only explicit failed adjacent same-prompt requests are grouped; native minus candidate counts is never used.",
        "timeout_cleanup_records":[{k:c.get(k) for k in ("id","timed_out","tree_cleanup_returncode","tree_cleanup_unresolved","returncode","error")} for c in calls if c.get("timed_out") or c.get("tree_cleanup_returncode") is not None or c.get("tree_cleanup_unresolved") is not None],
        "sampling_retry_log_count":sum(len(c["sampling_retry_lines"]) for c in calls),
        "phase_counts":dict(Counter(c["phase"] for c in calls if c["native_start"])),
        "synthesis_metadata":synthesis_metadata,"detection_result":detection,
        "report":report_snapshot,"recommendation":recommendation_snapshot,"recommendation_raw_responses":rec_responses,
        "recommendation_bound_to_raw_response":rec_output_bound if recommendation_snapshot["exists"] else None,
        "recommendation_exists":recommendation_snapshot["exists"],"stage_outcomes":outcomes,
        "terminal_messages":terminal_text.splitlines(),
        "source_files_verified":len(pins["files"]),"source_changed":source_changed,
        "source_manifest_unchanged":digest(BASE/"source-manifest.json")==runtime["source_manifest_sha256"],
        "cli_executable_unchanged":digest(Path(runtime["cli_executable"]))==runtime["cli_sha256"],
        "adapter_unchanged":digest(BASE/"run_comparison.py")==runtime["adapter_sha256"],
        "helper_unchanged":digest(BASE/"adapters/complete_source.py")==runtime["full_source_helper_sha256"],
        "input_manifest_unchanged":digest(BASE/"input-manifest.json")==runtime["input_manifest_sha256"],
        "input_013_sha256":digest(BASE/"inputs/013/SKILL.md"),
        "changed_input_files":input_changed,
        "source_inventory":source_inventory,"input_inventory":input_inventory,"integrity_reconciliation":integrity_reconciliation,
        "process_observation":process_observation,
        "semantic_notes":read(OUT/"013-semantic-notes.json"),
        "read_issues":READ_ISSUES,
        "new_model_calls_by_audit":0,"skill_executions_by_audit":0,
        "accuracy":"not_evaluated","recall":"not_evaluated",
    }
    (OUT/"013-analysis.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    vrows="\n".join(f"| {v['id']} | {', '.join(v.get('matching_candidate_files',[])) or '待核验'} | {v.get('program_valid') if v.get('program_valid') is not None else '未知/未绑定'} | {v.get('bound_error_count') if v.get('bound_error_count') is not None else '未知'} | {v.get('bound_warning_count') if v.get('bound_warning_count') is not None else '未知'} | {(v.get('error_codes') or '无') if v.get('binding',{}).get('usable') else '未绑定'} |" for v in validations)
    crows="\n".join(f"| {c['id']} | {c.get('phase')} | {c.get('returncode')} | {c.get('elapsed_seconds')} | {c['raw_usage_audit']['input_plus_output_exact'] if c['raw_usage_audit']['input_plus_output_exact'] is not None else '未知'} |" for c in calls)
    semantic=result["semantic_notes"]
    semantic_text=semantic["analysis_zh"] if semantic else "尚无已完成的有效候选语义核查；不能从结构校验通过或引文匹配率推出源约束正确。"
    terminal_summary=(f"Semia管线exit={finished.get('exit_code')}，耗时{finished.get('elapsed_seconds')}秒；原生exit分布{result['native_returncode_counts']}。"
                      f"检测/报告/推荐状态分别为{outcomes['detector']}/{outcomes['report']}/{outcomes['recommendation']}。"
                      f"root提供的外层PowerShell会话回收exit={wrapper_exit.get('wrapper_exit_code') if wrapper_exit else '未知'}，与Semia管线exit分别记录；回执绑定finished SHA={wrapper_binding['finished_hash_matches']}。"
                      f"新鲜PID观察：记录{len(process_observation.get('recorded_processes',[]))}条，all_recorded_absent={process_observation.get('all_recorded_absent')}，"
                      f"直接子进程{len(process_observation.get('direct_children',[])) if process_observation.get('status')=='observed' else '未知'}、额外可观察后代{len(process_observation.get('observable_descendants',[])) if process_observation.get('status')=='observed' else '未知'}，"
                      f"观察晚于finished={process_observation.get('observation_after_finished')}。" if finished else "尚无终态回执。")
    report=f'''# SEMIA 013 只读跟进分析

观察时间：{result['observed_at_utc']}。状态：**{'已终止' if finished else 'in_progress：运行中，以下为中途观察'}**。

本分析读取 `comparison/013` 原始记录及固定源码，只向独立analysis目录写派生报告。没有模型调用、Skill执行、重跑scan、修改active artifacts或修改001已绑定审计。

本例为 `semia-379bc25f-controlled-complete-source-v1`，gpt-6.1-sol/high/openai、builtin检测器；5轮、每轮3次结构重试、2次provider错误重试，2700秒原生期限。源码/提示/checker/检测规则保持固定；完整源适配、无工具文本调用、独立请求目录及600→2700秒与原版差异均属于实验条件，不是原封不动论文或原生Codex路径复现。无独立gold，accuracy/F1/recall未评估。

## 运行与校验

完成回执：`{finished}`。

{terminal_summary}

观察到 {result['native_starts']} 次原生启动、{len(candidate_paths)} 个候选文件、{len(validations)} 份validation快照；经提交身份和完整check内容绑定后有效validation {result['valid_validation_count']} 份，按提交facts哈希去重为 {len(valid_sha)} 个有效候选（重复检查不重复计数）。直接读取所有stdout的turn.completed事件所得已知input小计={totals['input_tokens']}、output小计={totals['output_tokens']}，合计已知 **{totals['input_plus_output_tokens']} tokens**。全请求精确公开合计={raw_accounting['input_plus_output_tokens']['exact_sum'] if raw_accounting['input_plus_output_tokens']['exact_sum'] is not None else 'unknown'}；未能获得完整input/output用量的已启动请求 {result['usage_missing_count']} 个。逐字段缺失保留unknown，未填零；cached与reasoning是子计数，不再次相加，provider内部未披露用量仍未知。内部sampling retry日志 {result['sampling_retry_log_count']} 条，独立于native starts和上游provider retries。CGRS和recommendation成本分别保留在机器记录public_usage_by_phase中。

| 请求 | 阶段 | native exit | 秒 | input+output tokens |
| --- | --- | ---: | ---: | ---: |
{crows}

| validation | 对应提交候选 | program_valid | errors | warnings | 代码 |
| --- | --- | --- | ---: | ---: | --- |
{vrows}

完整逐条诊断、提交facts SHA及对应候选保存在 `013-analysis.json`。必须同时满足实际submitted SHA=invocation SHA=return-payload SHA、复制facts一致、返回字段一致，并用固定源码纯函数重核完整check及alignment一致，才把validation计为可用。未绑定/异常/缺失的有效性和计数保持未知；未绑定validation数={result['unbound_validation_count']}。未调用check_facts、scan或模型，也不修改原始候选。SDL003是参数schema错误；其他SDL项须按原消息区分模型协议；检测label、原生传输错误分别记录。

没有arity错误但仍被拒绝的validation：{result['rejected_without_arity_errors']}。与初次prompt逐字节相同的请求：{result['calls_identical_to_initial_prompt']}。已完成原生耗时超过上游默认600秒的请求：{result['native_requests_over_600_seconds']}；这里只记录观测，不模拟另一超时策略的反事实结果。

绑定候选中的诊断累计为{dict(aggregate)}；具体arity消息累计为{dict(arity_totals)}。这是多份候选中的重复诊断次数，不是独立漏洞数量。

源码核验 {len(pins['files'])} 文件，变更 {len(source_changed)}；输入变更 {len(input_changed)} 个文件。独立manifest/精确清单/输入大小/CLI/runner/helper核验全部通过={all(integrity.values())}。每次实际prompt的完整源唯一性、receipt SHA和实际argv均独立核对，不能仅依赖runner自己的source_payload_verified标记。

各阶段状态：{outcomes}。实际读取report.md、recommendation.md及推荐原始回答；推荐是可非致命失败的独立模型阶段，pipeline exit=0不等于推荐成功。没有检测artifact不能记成零发现或安全；已有推荐内容也须逐条语义审阅，不能冒充gold。终态计数对账={finished_reconciliation}。进程观察={process_observation.get('status')}，仅在终态新查询记录controller/native PID及可观察直接子进程/后代，绑定finished SHA及观察时间，不导入旧PID快照。timeout清理记录数={len(result['timeout_cleanup_records'])}。

## 与013源约束对应

源文要求：FAST_KEY决定首选工具是否可调用；fast.fetch仅首次transient失败可再试一次；非transient或重试失败转archive，archive至多一次且只接收source_id；任一成功后返回原body且停止取数；archive失败返回其error；FAST_KEY不可送archive或诊断；每条终止路径先追加status.txt。这些是源约束清单，不是人工gold标注。

{semantic_text}

SDL的风险label与完整工作流正确性是不同目标。控制边和条件value存在，并不自动证明重试次数、错误分类、原body返回、每终止路径日志义务均已语义验证；需逐条对照事实和检测规则。recommendation是单独模型阶段，不计入确定性检测或CGRS候选成功数。
'''
    (OUT/"013-analysis.zh.md").write_text(report,encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("status","candidate_file_count","validation_count","valid_validation_count","native_starts","known_public_usage","aggregate_error_counts")},ensure_ascii=False))


if __name__=="__main__":
    main()
