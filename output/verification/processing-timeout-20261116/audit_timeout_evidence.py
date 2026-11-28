"""Read only closed public artifacts; do not import or execute SkillFlow."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "experiments/doe/runs/document-guided-ga4-source-review-locality-high-20261113-203902"
PRIOR = ROOT / "output/verification/online-ga4-source-review-locality-20261113"
READS = {}


def read(path):
    raw = path.read_bytes()
    READS[path.relative_to(ROOT).as_posix()] = {
        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    return raw.decode("utf-8")


def obj(path):
    return json.loads(read(path))


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def size(text):
    return {"unicode_codepoints": len(text), "utf8_bytes": len(text.encode("utf-8")),
            "utf16_code_units": len(text.encode("utf-16-le")) // 2,
            "sha256_utf8": hashlib.sha256(text.encode("utf-8")).hexdigest()}


HEADINGS = ["STEP RESPONSIBILITY", "PREVIOUS WORK", "RUNTIME_CONTRACT", "SOURCE REVIEW REPAIR",
            "GLOBAL REQUIREMENTS AND LIMITATIONS", "RELATED SOURCE", "OUTPUT REQUIREMENTS",
            "SHARED ABSTRACTION GRANULARITY", "COMPLETE PROCESSING COVERAGE", "REQUIRED_IR_IDS",
            "FRAGMENT FORMAT", "PRE-SUBMIT CHECK"]


def sections(prompt):
    marks = sorted((prompt.index(name + "\n"), name) for name in HEADINGS if name + "\n" in prompt)
    result = {}
    for index, (start, name) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(prompt)
        result[name] = {"offset_codepoints": start, "end_codepoints": end, **size(prompt[start:end])}
    assert sum(row["unicode_codepoints"] for row in result.values()) == len(prompt)
    return result


def output_stats(value):
    counts, lengths, repeated = Counter(), Counter(), Counter()

    def walk(value):
        if isinstance(value, dict):
            for key, member in value.items():
                counts[key] += 1
                lengths[key] += len(compact(member))
                if isinstance(member, (dict, list)):
                    repeated[key, compact(member)] += 1
                walk(member)
        elif isinstance(value, list):
            for member in value:
                walk(member)

    walk(value)
    return {
        "top_level": {key: {"compact_value_codepoints": len(compact(member)),
                            "members": len(member) if isinstance(member, (dict, list)) else None}
                      for key, member in value.items()},
        "key_occurrences": dict(counts.most_common()),
        "value_codepoints_by_key": dict(lengths.most_common()),
        "exact_repeated_container_values": [
            {"key": key, "occurrences": count, "compact_value_codepoints": len(text),
             "value_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
            for (key, text), count in repeated.most_common(30) if count > 1],
        "counting_notice": "Nested aggregate values overlap; value_codepoints_by_key must not be summed. Repetition is exact JSON-value equality, not semantic equivalence or token savings."
    }


cost = obj(PRIOR / "cost-provenance-audit/ga4-20261113T162801663200Z.json")
summary = obj(PRIOR / "run-summary.json")
stages = [("processing", "a001"), ("processing", "a002"), ("revision-graph", "a001"),
          ("revision-processing", "a001")]
rows = []
prompts, answers = {}, {}
for stage, attempt in stages:
    base = RUN / "steps" / stage / "calls" / attempt
    prompt = read(base / "prompt.txt")
    record = obj(base / "call.json")
    assert record["prompt"] == prompt
    req = next(row for row in cost["requests"]
               if row["stage"] == stage and row["logical_call"] == f"calls/{attempt}/call.json")
    native = RUN / req["request"]
    delivery = read(native.parent / "prompt.txt")
    assert delivery.endswith(prompt)
    process = obj(native / "process.json")
    obj(native / "started.json")
    stdout = read(native / "stdout.jsonl")
    stderr = read(native / "stderr.txt")
    events = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    answer = json.loads(read(base / "response.json")) if (base / "response.json").exists() else None
    row = {
        "stage": stage, "attempt": attempt, "category": req["category"],
        "prompt": size(prompt), "native_delivery": size(delivery),
        "adapter_headroom_codepoints": 1048576 - len(delivery),
        "started_at": req["started_at"], "finished_at": req["finished_at"],
        "process": process, "complete_public_usage": req["complete_token_usage"] or None,
        "public_event_type_counts": dict(Counter(event.get("type") for event in events)),
        "public_item_type_counts": dict(Counter(event.get("item", {}).get("type") for event in events if "item" in event)),
        "public_event_has_timestamps": any("timestamp" in event or "created_at" in event for event in events),
        "public_token_delta_count": sum("delta" in str(event.get("type", "")) for event in events),
        "answer": size(answer) if answer is not None else None,
        "end_to_end_public_output_tokens_per_second": (
            req["complete_token_usage"]["output_tokens"] / process["elapsed_seconds"]
            if req["complete_token_usage"] else None),
    }
    if stage in {"processing", "revision-processing"} and attempt == "a001":
        row["sections"] = sections(prompt)
        cfg = json.loads(prompt[prompt.index("\nCFG\n") + 5:prompt.index("\n\nRUNTIME_CONTRACT")])
        row["cfg"] = {"blocks": len(cfg["blocks"]), "edges": len(cfg["edges"]),
                      "instructions": sum(len(block["instructions"]) for block in cfg["blocks"].values()),
                      "compact_codepoints": len(compact(cfg)),
                      "components": {key: len(compact(member)) for key, member in cfg.items()}}
    if answer is not None and stage == "processing":
        answers[attempt] = json.loads(answer)
        row["output_statistics"] = output_stats(answers[attempt])
    prompts[stage, attempt] = prompt
    rows.append(row)

initial, revision = prompts["processing", "a001"], prompts["revision-processing", "a001"]
initial_sections, revision_sections = sections(initial), sections(revision)
repair_text = revision[revision.index("SOURCE REVIEW REPAIR\n") + len("SOURCE REVIEW REPAIR\n"):
                       revision.index("GLOBAL REQUIREMENTS AND LIMITATIONS")].strip()
repair = json.loads(repair_text)
correction = prompts["processing", "a002"]
assert correction.startswith(initial)
correction_value = json.loads(correction.split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])
rebuild = {
    "revision_prompt_growth_codepoints": len(revision) - len(initial),
    "revision_prompt_growth_percent": 100 * (len(revision) / len(initial) - 1),
    "section_growth_codepoints": {name: revision_sections.get(name, {}).get("unicode_codepoints", 0)
                                  - initial_sections.get(name, {}).get("unicode_codepoints", 0)
                                  for name in HEADINGS},
    "repair_components": {key: {"compact_codepoints": len(compact(value)), "members": len(value)}
                          for key, value in repair.items()},
    "repair_growth_fraction": revision_sections["SOURCE REVIEW REPAIR"]["unicode_codepoints"] / (len(revision) - len(initial)),
    "related_source_exactly_equal": (
        initial[initial_sections["RELATED SOURCE"]["offset_codepoints"]:initial_sections["RELATED SOURCE"]["end_codepoints"]]
        == revision[revision_sections["RELATED SOURCE"]["offset_codepoints"]:revision_sections["RELATED SOURCE"]["end_codepoints"]]),
    "initial_correction_full_base_prompt_prefix": True,
    "initial_correction_added_codepoints": len(correction) - len(initial),
    "initial_correction_context_components": {key: len(compact(value)) for key, value in correction_value.items()},
    "initial_correction_diagnostics": correction_value.get("diagnostics"),
    "initial_correction_exactly_unchanged_ir_rows": sum(
        value == answers["a002"]["ir_semantics"].get(key) for key, value in answers["a001"]["ir_semantics"].items()),
    "initial_correction_changed_existing_ir_rows": sum(
        key in answers["a002"]["ir_semantics"] and value != answers["a002"]["ir_semantics"][key]
        for key, value in answers["a001"]["ir_semantics"].items()),
    "initial_correction_new_ir_rows": len(set(answers["a002"]["ir_semantics"]) - set(answers["a001"]["ir_semantics"])),
    "notice": "The full replacement is measured. Reuse eligibility is not established by unchanged IDs; revised CFG bindings and all validation dependencies must be checked."
}

failed = rows[-1]
failed_request = next(row for row in cost["requests"] if row["stage"] == "revision-processing")
native = RUN / failed_request["request"]
start = datetime.fromisoformat(failed_request["started_at"])
stderr = read(native / "stderr.txt")
timeline = []
for line_number, line in enumerate(stderr.splitlines(), 1):
    if not line.strip():
        continue
    stamp = datetime.fromisoformat(line.split()[0].replace("Z", "+00:00"))
    kind = ("sampling_retry" if "retrying sampling request" in line else
            "auxiliary_model_refresh" if "failed to refresh available models" in line else "shell_snapshot_notice")
    match = re.search(r"\((\d+)/([0-9]+) in (\d+)ms\)", line)
    timeline.append({"line": line_number, "timestamp": stamp.isoformat(),
                     "seconds_after_native_start": (stamp - start).total_seconds(),
                     "kind": kind, "message": line,
                     "retry": int(match[1]) if match else None,
                     "declared_retry_limit": int(match[2]) if match else None,
                     "logged_backoff_milliseconds": int(match[3]) if match else None})
timeline.append({"kind": "native_total_deadline", "timestamp": failed_request["finished_at"],
                 "seconds_after_native_start": failed["process"]["elapsed_seconds"]})

transport_path = ROOT / "tools/doe/document_guided_client.py"
transport_text = read(transport_path)
prompt_path = ROOT / "src/skillflow/document_guided/prompts.py"
prompt_text = read(prompt_path)
runner_path = ROOT / "src/skillflow/document_guided/runner.py"
runner_text = read(runner_path)
read(ROOT / "src/skillflow/common/structural_correction.py")

result = {
    "version": "skillflow-processing-timeout-readonly-evidence-v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "closed_run": RUN.relative_to(ROOT).as_posix(),
    "scope": "Read-only stdlib parsing of closed public artifacts and current source; no replay, model, backend, validator, Skill or private session execution.",
    "accepted_prior_implementation_sha256": summary["implementation_sha256"],
    "request_rows": rows, "rebuild_scale": rebuild, "revision_processing_public_timeline": timeline,
    "network_evidence": {
        "sampling_retry_log_count": sum(row["kind"] == "sampling_retry" for row in timeline),
        "sampling_retry_logged_backoff_sum_milliseconds": sum(row.get("logged_backoff_milliseconds") or 0 for row in timeline),
        "auxiliary_refresh_errors": sum(row["kind"] == "auxiliary_model_refresh" for row in timeline),
        "outer_retries": 0,
        "terminal_timeout_kind": "2700-second native-process total deadline; not demonstrated to be a connection-establishment timeout",
        "causal_limit": "Disconnect/reset/request-timeout events establish network/service interruptions within the same native process. The logs cannot allocate total elapsed time to server prefill, reasoning, decoding, network waits or regenerated work. Retry backoff sum is not retry duration."
    },
    "generation_evidence_limits": [
        "No token delta timestamps or first-token timings are present in these public stdout JSONL artifacts.",
        "Completed request elapsed seconds include submission, model/server work, network and process overhead. Public output tokens divided by that duration are only end-to-end completed-output throughput.",
        "Failed revision-processing has no completed answer or complete usage. Generated/discarded tokens, TTFT, model-only generation duration and provider billing remain unknown.",
        "A larger prompt and a 770-IR complete-output obligation establish additional workload, not proof that output generation consumed the timeout.",
    ],
    "transport_source_evidence": {
        "path": transport_path.relative_to(ROOT).as_posix(),
        "native_deadline_lines": [204, 213, 215, 218, 240],
        "input_limit_lines": [24, 277, 285], "outer_retry_gate_lines": [286, 300, 303],
        "public_capture_lines": [206, 208, 289],
        "timeout_seconds": 2700, "max_input_unicode_codepoints": 1048576,
        "normal_calls": 7, "workers": 2, "outer_retry_limit": 2,
        "change_status": "Read-only inspected. Hash identifies the implementation read; later changes must not retroactively alter this evidence."
    },
    "general_recommendations": [
        {"priority": 1, "change": "Use a generic, exactly reversible processing wire representation on both input context and generated output.",
         "reason": "The revision includes the entire 228473-codepoint prior fragment; completed processing output contains repeated evidence, binding and contract structures.",
         "requirements": "Hash-bind dictionaries/material; reject wrong references, cycles and excess expansion; fully expand before existing strict validation; preserve all actual reads, evidence, contract scopes, local gaps and source text. Do not substitute lossless byte savings for measured token or runtime savings."},
        {"priority": 2, "change": "Allow a complete, validated correction/revision expression to explicitly reuse eligible unchanged records and supply changed/new records.",
         "reason": "The initial single missing-IR coverage error triggered full replacement and a large second output; revision again demands a full new 770-IR payload.",
         "requirements": "Bind exact source/CFG/annotation identities and dependency closure; same IR ID does not establish unchanged semantics. Every current IR must be covered exactly once; rejected/changed records remain ineligible for implicit reuse; Task isolation and every old validator remain."},
        {"priority": 3, "change": "Record bounded public event-arrival timing during the existing native request and classify terminal errors separately from observed internal network symptoms.",
         "reason": "Current final-only public JSONL cannot distinguish first output time or generation intervals; the terminal generic error obscures the native deadline.",
         "requirements": "No extra request, token stream/private reasoning capture or timeout/retry increase. Report unavailable TTFT/model generation time as unknown; recording observation time is not a server-side timestamp."},
        {"priority": 4, "change": "Offline verify exact expansion, strict failures, complete coverage, correction/revision identity and local isolation before the one newly authorized fresh GA4 run.",
         "reason": "Both workload and interruption risk need measurement under unchanged seven normal requests, two workers and existing transport/repair budgets.",
         "requirements": "Do not resume/replay this closed run, truncate source, omit contracts, increase budgets, split into per-IR model calls or execute Skills. New online results, not this audit, determine whether the proposed fix resolves the failure."}
    ],
    "bound_artifacts": READS,
}

OUT.mkdir(parents=True, exist_ok=True)
target = OUT / "timeout-evidence.json"
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"report": str(target), "bound_artifacts": len(READS),
                  "revision_prompt_codepoints": failed["prompt"]["unicode_codepoints"],
                  "sampling_retries": result["network_evidence"]["sampling_retry_log_count"]}))
