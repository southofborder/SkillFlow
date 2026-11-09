"""Read-only mechanical metrics for this exact four-case batch, after closure.

Usage: python -B extract_closed_metrics.py ga4 > ga4-mechanical.json
Only stdout is written. No SkillFlow imports, loaders, replay, or subprocesses.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
CASES = ("ga4", "001", "010", "013")
TAG = "20261104-132226"
STATUSES = ("processed", "unmodeled", "unresolved_binding", "blocked", "not_reached", "not_solved")


def _stage(row):
    value = row.get("logical_request")
    if not isinstance(value, str):
        return None
    parts = value.replace("\\", "/").split("/")
    if "transport" not in parts:
        return None
    return "/".join(parts[parts.index("transport") + 1:-1]) or None


def _call_categories(metrics):
    groups, stages = defaultdict(set), Counter()
    rows = metrics.get("requests")
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict) or not row.get("logical_request"):
            continue
        stage = _stage(row)
        correction = row.get("structural_correction")
        category = "unknown"
        if correction is True:
            category = "structural_correction"
        elif correction is False and stage is not None:
            category = "semantic_repair_generation" if stage.startswith(("revision/", "revision-")) else "normal_generation"
        groups[row["logical_request"]].add((category, stage))
    counts = Counter()
    for values in groups.values():
        category, stage = next(iter(values)) if len(values) == 1 else ("unknown", None)
        counts[category] += 1
        stages[stage or "unknown"] += 1
    return {"unique_logical_request_count": len(groups), "by_category": dict(counts),
            "by_stage": dict(stages),
            "attempt_rows_without_identity": sum(not row.get("logical_request") for row in rows if isinstance(row, dict)),
            "scope": "Unique saved logical_request identities; correction requests are separate from normal/repair generation. Network attempts are reported separately."}


def _elapsed(start, end):
    try:
        return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()
    except (TypeError, ValueError):
        return None


def _summarize_closed(run):
    """JSON-only core; also usable on closed old/synthetic files for offline tests."""
    run = Path(run).resolve()
    # Check before opening any candidate, result, propagation, DOE, or metrics.
    if not (run / "controller-finished.json").is_file():
        raise ValueError("Refusing unfinished run: controller-finished.json is absent")
    evidence, warnings = {}, []

    def read(relative):
        path = (run / relative).resolve()
        if not path.is_relative_to(run):
            raise ValueError("Artifact reference leaves this run: " + str(relative))
        if not path.is_file():
            return None
        try:
            raw = path.read_bytes()
            evidence[path.relative_to(run).as_posix()] = hashlib.sha256(raw).hexdigest()
            value = json.loads(raw.decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("Expected a JSON object")
            return value
        except (OSError, UnicodeError, ValueError) as error:
            warnings.append(str(relative) + ": " + str(error))
            return None

    finished = read("controller-finished.json")
    if not finished:
        raise ValueError("Refusing unreadable/empty controller-finished marker")
    result = read("result.json") or {}
    analysis = read("analysis-finished.json") or {}
    replay = read("replay-check.json") or finished.get("replay") or {}
    propagation = read("propagation/manifest.json")
    records = read("propagation/records.json")
    doe = read("doe/doe-result.json")
    metrics = read("metrics.json")
    timing = read("component-timing.json")
    cfg_ids = None
    selected = result.get("selected_annotation")
    if isinstance(selected, str):
        refs = read(Path(selected) / "inputs/references.json") or {}
        cfg_ref = refs.get("cfg", {}).get("path")
        if isinstance(cfg_ref, str):
            graph = read(Path(selected) / cfg_ref) or {}
            cfg = graph.get("cfg", {})
            blocks = cfg.get("blocks", {})
            if isinstance(blocks, dict):
                cfg_ids = [ir["id"] for block in blocks.values()
                           for ir in block.get("instructions", []) if "id" in ir]

    coverage = propagation.get("coverage") if propagation else None
    counts = Counter(coverage.values()) if isinstance(coverage, dict) else None
    denominator = len(cfg_ids) if cfg_ids is not None else len(coverage) if isinstance(coverage, dict) else None
    if cfg_ids is not None and isinstance(coverage, dict) and set(cfg_ids) != set(coverage):
        warnings.append("Selected CFG identities and propagation coverage differ; counts remain separate.")
    generated = {"total": denominator, "denominator_source": "selected_cfg" if cfg_ids is not None else "propagation_coverage" if counts is not None else None,
        "coverage_entries": len(coverage) if isinstance(coverage, dict) else None,
        "by_status": {key: counts[key] for key in (*STATUSES, *sorted(set(counts) - set(STATUSES)))} if counts is not None else None,
        "cutoff_count": counts["unmodeled"] + counts["unresolved_binding"] if counts is not None else None,
        "cutoff_definition": "Visited unmodeled or unresolved_binding IR; blocked/not_solved/not_reached remain separate.",
        "processed_fraction": counts["processed"] / denominator if counts is not None and denominator else None,
        "recorded_ir_count": len(records) if records is not None else None,
        "scope": "Generated-IR bookkeeping only, not source-boundary coverage. Not-reached IR is not counted as processed."}
    doe_summary = None
    if doe is not None:
        sinks = doe.get("sinks")
        comparisons = [review for sink in sinks for review in sink.get("data_reviews", [])] if isinstance(sinks, list) else None
        declared = doe.get("coverage", {})
        doe_summary = {"status": doe.get("status"), "sinks": len(sinks) if isinstance(sinks, list) else None,
            "comparisons": len(comparisons) if comparisons is not None else None,
            "engine_conclusions": dict(Counter(row.get("conclusion", "unknown") for row in comparisons)) if comparisons is not None else None,
            "coverage": {key: declared.get(key) for key in ("declared_scopes", "declarations", "resolved_declarations", "expected_sinks", "demand_status", "sensitivity_basis")},
            "unresolved_boundaries": len(declared["unresolved_boundaries"]) if isinstance(declared.get("unresolved_boundaries"), list) else None,
            "diagnostic_codes": dict(Counter(row.get("code", "unknown") for row in doe.get("diagnostics", []))),
            "scope": "Raw engine conclusions and sensitivity-declaration counts; no source-supported/contradicted label or semantic accuracy claim. Zero comparisons does not establish safety."}
    transport = None
    if metrics is not None:
        fields = ("status", "reason", "launch_attempts", "cli_dispatches", "cli_dispatches_scope", "native_process_starts",
            "unknown_native_process_starts", "inputs_rejected_before_start", "logical_requests", "network_retry_attempts",
            "known_token_usage", "partial_token_usage", "complete_usage_requests", "partial_usage_requests",
            "unknown_usage_requests", "total_usage_known", "known_request_seconds", "unknown_duration_requests",
            "wall_clock_seconds", "wall_clock_scope", "http_attempts", "monitor_warnings", "notice")
        transport = {key: metrics.get(key) for key in fields}
        transport["logical_categories"] = _call_categories(metrics)
        transport["scope"] = "Copied saved deduplicated public metrics, including all attempts. Cached input is a subset of input; reasoning output is a subset of output. Partial usage is separate, not a complete cost estimate. unknown_usage_requests can include partial-usage attempts. No transport recount or currency estimate."
    component_records = [{key: row.get(key) for key in ("phase", "component", "elapsed_seconds", "returned")}
                         for row in timing.get("records", [])] if timing else None
    return {"kind": "closed_run_mechanical_evidence", "run_directory": str(run),
        "analysis": {"status": result.get("status"), "controller_status": finished.get("status"),
            "controller_error": finished.get("controller_error"), "reason": result.get("reason"),
            "selected_annotation": selected, "repair_used": result.get("repair_used"), "recorded_counts": result.get("counts"),
            "stages": result.get("stages"), "graph_review": result.get("graph_review"), "annotation_review": result.get("annotation_review")},
        "propagation": {"available": propagation is not None, "status": propagation.get("status") if propagation else None,
            "generated_ir": generated, "diagnostic_codes": dict(Counter(row.get("code", "unknown") for row in propagation.get("diagnostics", []))) if propagation else None},
        "doe": doe_summary, "transport": transport,
        "timing": {"analysis_seconds": analysis.get("analysis_seconds", finished.get("analysis_seconds")),
            "controller_wall_seconds": _elapsed(analysis.get("started_at"), finished.get("finished_at")),
            "replay": replay, "component_records": component_records,
            "doe_post_compute_publication": timing.get("doe_post_compute_publication") if timing else None,
            "scope": "Component intervals are nested and nonadditive; no summed component total. Request durations can overlap; native span includes gaps. Missing measurements stay null."},
        "source_assessment": "Not performed by this extractor; generated coverage and engine conclusions require independent source review.",
        "evidence_sha256": evidence, "warnings": warnings}


def extract(case):
    if case not in CASES:
        raise ValueError("Case is outside this authorized batch")
    queue = json.loads((VERIFY / "prepared-runs.json").read_text(encoding="utf-8"))
    row = next(item for item in queue["run_order"] if item["case_id"] == case)
    run = Path(row["run_directory"]).resolve()
    expected = PROJECT / "experiments/doe/runs" / f"document-guided-{case}-backend-r3-high-{TAG}"
    if run != expected.resolve():
        raise ValueError("Prepared path differs from the exact authorized new run")
    return {"case_id": case, **_summarize_closed(run)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    try:
        print(json.dumps(extract(args.case), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, StopIteration) as error:
        parser.exit(2, "Closed-run extraction refused: " + str(error) + "\n")
