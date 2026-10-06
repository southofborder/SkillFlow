"""Offline provenance checks shared by result presentation tools.

Only trusted repository tools and JSON records are read. No Skill file is
imported or executed, and a checksum is a consistency lock, not an API signature.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

from skillflow.common.paths import project_root, resolve_material_path

from tools.graph.baseline import freeze


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_page_bodies(pages, margin=46):
    """Reject accidental pages containing only running headers and footers."""
    for number, page in enumerate(pages, 1):
        body = []
        height = float(page.mediabox.height)

        def visit(text, cm, tm, font, size):
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            if margin < y < height - margin and text.strip():
                body.append(text)

        page.extract_text(visitor_text=visit)
        if not body:
            raise ValueError(f"PDF page has no body content: {number}")


def transport_metadata(experiment):
    """Expose recorded transport details without inferring missing legacy fields."""
    transport = experiment.get("provenance", {}).get("transport")
    if not isinstance(transport, dict):
        return {"protocol": None, "parameters": None}
    return {"protocol": transport.get("protocol"), "parameters": transport.get("parameters")}


def model_return_observations(trace):
    """Keep provider-returned names literal and separate generations from HTTP attempts."""
    return [
        {"generation": call.get("generation"), "returned_model": call.get("returned_model"),
         "http_attempts": [
             {"attempt": number, "status": attempt.get("status"),
              "http_status": attempt.get("http_status"),
              "returned_model": attempt.get("returned_model")}
             for number, attempt in enumerate(call.get("http_attempts", []), 1)]}
        for call in (trace or {}).get("calls", [])
    ]


def select_result_variant(experiment, variant=None):
    """Use the recorded single variant when omitted, never a hard-coded model family."""
    matches = [item for item in experiment.get("variants", [])
               if variant is None or item.get("id") == variant]
    if len(matches) != 1:
        raise ValueError("Result variant must select exactly one recorded model configuration")
    return matches[0]["id"]


def model_identity_metadata(experiment, variant, trials):
    """Expose a safe recorded identity; never infer aliases or fill missing model names."""
    variant = select_result_variant(experiment, variant)
    selected = next(item for item in experiment["variants"] if item["id"] == variant)
    fields = ("id", "endpoint", "model", "reasoning_effort", "timeout_ms", "max_retries",
              "retry_base_ms", "retry_max_backoff_ms", "max_repair_rounds")
    requested = {key: selected.get(key) for key in fields}
    change = experiment.get("provenance", {}).get("provider_change")
    safe_change = None
    if isinstance(change, dict):
        change_fields = ("provider_change_id", "authorized_on", "reason", "comparability",
                         "thinking_mode", "inherited_trials", "case_and_prompt_identity_equal",
                         "production_source_identity_equal", "requested_returned_model_note",
                         "preflight_not_baseline", "manifest_sha256", "config_sha256")
        safe_change = {key: change.get(key) for key in change_fields}
        safe_change["prior_runs"] = [
            {key: item.get(key) for key in ("directory", "experiment_sha256", "report_sha256")}
            for item in change.get("prior_runs", [])]
    returned, missing = Counter(), 0
    for trial in trials:
        for call in model_return_observations(trial.get("trace")):
            for attempt in call["http_attempts"]:
                name = attempt["returned_model"]
                if name is None:
                    missing += 1
                else:
                    returned[name] += 1
    return {"requested": requested, "provider_change": safe_change,
            "http_returned_model_counts": dict(sorted(returned.items())),
            "http_attempts_without_returned_model": missing,
            "returned_names_differ_from_requested": sorted(name for name in returned if name != requested["model"])}


def remote_unknown_attempts(trace):
    """HTTP success headers do not imply a completed streamed model response."""
    return [{"generation": call.get("generation"), "http_attempt": number,
             "http_status": attempt.get("http_status")}
            for call in (trace or {}).get("calls", [])
            for number, attempt in enumerate(call.get("http_attempts", []), 1)
            if (attempt.get("stream") or {}).get("outcome") == "remote_outcome_unknown"]


def result_report_scope(materials, mode):
    """Choose honest detail coverage without inventing unrun assessments."""
    if mode not in {"final", "interim", "preview"}:
        raise ValueError("Unknown result report mode")
    if len(materials) != 30 or len({m["sample"]["id"] for m in materials}) != 30:
        raise ValueError("Result report must retain the complete 30-sample / 90-trial plan")
    selected, details, reviewed, assessments = [], [], [], 0
    terminal = {"complete", "degraded", "error", "uncertain"}
    for material in materials:
        sid = material["sample"]["id"]
        trials = material["trials"]
        if sorted(t["repetition"] for t in trials) != [1, 2, 3]:
            raise ValueError("Result report must retain the complete 30-sample / 90-trial plan")
        statuses = [t["record"].get("status", "not_run") for t in trials]
        ready = all(status in terminal for status in statuses)
        if mode == "final" and not ready:
            raise ValueError("Final result report requires all 90 terminal trials")
        if mode == "interim" and any(status not in terminal | {"not_run"} for status in statuses):
            raise ValueError("Interim result report requires stopped, committed trials")
        review = material.get("review")
        if mode != "preview" and ready and review is None:
            raise ValueError(f"Three-terminal sample requires a complete external review: {sid}")
        if mode == "interim" and not ready and review is not None:
            raise ValueError(f"Do not prefill a three-run fact review for unrun trials: {sid}")
        if mode != "interim" or any(status in terminal for status in statuses):
            selected.append(sid)
            details += [(sid, t["repetition"]) for t in trials
                        if mode != "interim" or t["record"].get("status") in terminal]
        if review is not None:
            reviewed.append(sid)
            assessments += sum(len(fact.get("assessments", [])) for fact in review.get("facts", []))
    if mode == "final" and assessments != 891:
        raise ValueError("Final result report requires all 891 frozen fact/run assessments")
    if mode == "interim" and (not details or len(details) == 90):
        raise ValueError("Interim report requires an attempted but incomplete baseline")
    return {"sample_ids": selected, "detail_trials": details,
            "reviewed_sample_ids": reviewed, "fact_assessments": assessments}


def accepted_cfg_count(trials):
    """Structural acceptance count only; it never assigns a semantic verdict."""
    return sum(t["record"].get("status") == "complete"
               and (t.get("analysis") or {}).get("status") == "complete"
               and bool(((t.get("analysis") or {}).get("cfg") or {}).get("blocks"))
               for t in trials)


def verify_result_sources(base, run, variant):
    """Check the frozen answers and run identity before presenting any result."""
    base, run = Path(base), Path(run)
    manifest = freeze.verify_freeze(base)
    experiment = read(run / "experiment.json")
    provenance = experiment.get("provenance", {})
    if (provenance.get("freeze_manifest_sha256") != sha(base / "freeze_manifest.json")
            or provenance.get("contract") != "constraints-v2"):
        raise ValueError("Result run is not bound to the verified constraints-v2 freeze")
    if experiment.get("repetitions") != 3 or variant not in {
        item["id"] for item in experiment.get("variants", [])
    }:
        raise ValueError("Result experiment repetition/variant mismatch")
    samples = read(base / "frozen/corpus/corpus.json")["samples"]
    cases = experiment.get("cases", [])
    by_id = {item["id"]: item for item in cases}
    if len(cases) != 30 or set(by_id) != {sample["id"] for sample in samples}:
        raise ValueError("Result experiment must cover the 30 frozen samples")
    dataset = read(run / "dataset.json").get("cases", [])
    if len(dataset) != 30 or len({item["id"] for item in dataset}) != 30:
        raise ValueError("Result dataset must cover the 30 frozen samples")
    for sample in samples:
        case = by_id[sample["id"]]
        if case.get("split") != sample["split"]:
            raise ValueError("Result split differs from the frozen split")
        for field in ("extraction_input_sha256", "prompt_sha256"):
            value = case.get(field)
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError(f"Missing result identity digest: {sample['id']} / {field}")
    for item in dataset:
        if item.get("id") not in by_id or any(item.get(key) != value for key, value in by_id[item["id"]].items()):
            raise ValueError("Dataset and experiment input identity disagree")
    return manifest, by_id


def verify_trial_record(record, report_record, path, identity):
    """Reject stale report rows, unbound artifacts and absent online traces."""
    path = Path(path)
    if report_record is None or record != report_record:
        raise ValueError("Persisted trial record and report row disagree")
    expected_relative = f"trials/{record['case']}/{record['variant']}/{record['repetition']}"
    if record.get("artifacts") != expected_relative:
        raise ValueError("Trial artifact directory does not match its sample identifier")
    digests = record.get("artifact_sha256", {})
    allowed = {"trace.json", "analysis.json", "candidate.json", "graph.mmd"}
    if not isinstance(digests, dict) or set(digests) - allowed:
        raise ValueError("Unexpected trial artifact inventory")
    present = {name for name in allowed if (path / name).is_file()}
    if present != set(digests):
        raise ValueError("Every persisted trial artifact requires its committed digest")
    for name, digest in digests.items():
        if sha(path / name) != digest:
            raise ValueError(f"Trial artifact hash mismatch: {path / name}")
    if record.get("status") not in {"complete", "degraded"}:
        return
    if not {"analysis.json", "trace.json"} <= present:
        raise ValueError("Completed extraction requires persisted analysis and online trace")
    if record.get("prompt_sha256") != identity["prompt_sha256"]:
        raise ValueError("Trial prompt digest differs from the frozen run identity")
    trace = read(path / "trace.json")
    if any(trace.get(key) != record[key] for key in ("case", "variant", "repetition", "split")):
        raise ValueError("Online trace sample identifier mismatch")
    calls = trace.get("calls", [])
    if not calls or any(call.get("status") != "complete" or call.get("response") is None for call in calls):
        raise ValueError("Accepted extraction has no complete online generation trace")
    prompt = calls[0].get("prompt")
    if not isinstance(prompt, str) or hashlib.sha256(prompt.encode("utf-8")).hexdigest() != identity["prompt_sha256"]:
        raise ValueError("Online first prompt does not match the run identity")
