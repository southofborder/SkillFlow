"""Run one complete-source static audit per case in a new comparison run."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time


METHOD = Path(__file__).resolve().parent
COMPARISON = METHOD.parents[1]
REPO = COMPARISON.parents[2]
PROMPT = METHOD / "prompt.txt"
SCHEMA = METHOD / "response.schema.json"
MODEL = "gpt-6.1-sol"
EFFORT = "high"
PROVIDER = "openai"
DISABLED = (
    "plugins", "remote_plugin", "recommended_plugins", "shell_tool", "unified_exec",
    "apps", "browser_use", "browser_use_external", "computer_use", "in_app_browser",
    "image_generation", "view_image", "multi_agent", "multi_agent_v2", "hooks",
    "skill_search", "skill_mcp_dependency_install", "code_mode_host", "memories",
    "sleep_tool", "tool_suggest", "incremental_exec_tools",
)
SOURCE_ISOLATION = ("skip_host_skill_discovery", "omit_skill_descriptions")
TOOL_EVENTS = {
    "command_execution", "mcp_tool_call", "web_search", "function_call", "file_change",
    "collab_tool_call", "dynamic_tool_call", "external_tool_call", "computer_call",
    "tool_call", "image_generation", "image_view",
}


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, allow_nan=False, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def save(path, data):
    pending = path.with_suffix(path.suffix + ".tmp")
    pending.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def read_sources(case):
    source = REPO / case["source_directory"]
    if not source.resolve().is_relative_to(REPO) or not source.is_dir():
        raise ValueError(f"Invalid source directory: {source}")
    paths = sorted(source.rglob("*"), key=lambda path: path.relative_to(source).as_posix())
    if any(path.is_symlink() or getattr(path, "is_junction", lambda: False)() for path in paths):
        raise ValueError(f"Source contains a link: {source}")
    files = {path.relative_to(source).as_posix(): path.read_bytes() for path in paths if path.is_file()}
    expected = sorted(case["files"], key=lambda entry: entry["path"])
    actual = [{"path": path, "size": len(raw), "sha256": sha(raw)} for path, raw in files.items()]
    raw_identity = [{"path": row["path"], "size": row["size"], "raw_sha256": row["sha256"]}
                    for row in actual]
    if (actual != expected or len(actual) != case["file_count"]
            or sum(row["size"] for row in actual) != case["total_bytes"]
            or sha(canonical(raw_identity)) != case["package_bytes_sha256"]):
        raise ValueError(f"Source manifest mismatch: {case['case_id']}")
    for raw in files.values():
        raw.decode("utf-8", errors="strict")
        if b"\x00" in raw:
            raise ValueError(f"NUL byte in source: {case['case_id']}")
    return files


def render(template, case, files):
    nonce = case["package_bytes_sha256"].encode("ascii")
    marker = b"SKILLFLOW_SOURCE_" + nonce
    if any(marker in raw for raw in files.values()):
        raise ValueError(f"Source marker collision: {case['case_id']}")
    chunks = [template, b"\n\n", marker + b" BEGIN_PACKAGE\n"]
    for path, raw in files.items():
        label = canonical({"path": path, "bytes": len(raw), "sha256": sha(raw)})
        chunks.extend((marker + b" BEGIN_FILE " + label + b"\n", raw,
                       b"\n" + marker + b" END_FILE\n"))
    chunks.append(marker + b" END_PACKAGE\n")
    return b"".join(chunks)


def command(executable, flags, response, schema):
    return [executable, *flags, "-a", "never", "exec", "--ignore-user-config", "--ignore-rules",
            "--skip-git-repo-check", "--ephemeral", "--sandbox", "read-only", "--color", "never",
            "--json", "--model", MODEL, "-c", f'model_reasoning_effort="{EFFORT}"',
            "-c", f'model_provider="{PROVIDER}"', "-c", "project_doc_max_bytes=0",
            "-c", 'web_search="disabled"', "--output-schema", str(schema),
            "--output-last-message", str(response), "-"]


def read_events(path):
    usages, tools, errors = [], set(), []
    for line in path.read_text("utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        item = event.get("item")
        item_type = item.get("type") if isinstance(item, dict) else None
        if item_type in TOOL_EVENTS or event_type in TOOL_EVENTS:
            tools.add(item_type if item_type in TOOL_EVENTS else event_type)
        if event_type == "turn.completed" and isinstance(event.get("usage"), dict):
            usages.append(event["usage"])
        if event_type in ("error", "turn.failed"):
            errors.append(event.get("message") or event.get("error"))
    # A noninteractive call admits one completed turn. Multiple usage records are ambiguous.
    return usages[0] if len(usages) == 1 else None, sorted(tools), errors


def accepted_evidence(response, files):
    if response["status"] not in ("completed", "partial"):
        raise ValueError("Unexpected response status")
    lengths = {path: len(raw.decode("utf-8").splitlines()) for path, raw in files.items()}
    rejected = []
    for group in ("data_operations", "potential_excess"):
        for index, row in enumerate(response[group]):
            evidence = row["evidence"]
            if not evidence or not all(
                1 <= range_["start_line"] <= range_["end_line"] <= lengths.get(range_["path"], 0)
                for range_ in evidence
            ):
                rejected.append({"group": group, "index": index, "reason": "missing_or_invalid_source_range"})
    return rejected


def run_case(run, executable, flags, template, case):
    case_id = case["case_id"]
    folder = run / "cases" / case_id
    request_dir = folder / "requests"
    raw_dir = folder / "raw"
    request_dir.mkdir(parents=True)
    raw_dir.mkdir()
    response_path = raw_dir / "response.json"
    events_path = raw_dir / "events.jsonl"
    stderr_path = raw_dir / "stderr.txt"
    receipt = {"case_id": case_id, "package_bytes_sha256": case["package_bytes_sha256"],
               "source_files": case["file_count"], "native_start": False, "usage": None,
               "started_at": stamp()}
    result = {"case_id": case_id, "status": "failed", "request": "requests/request.json"}
    started = time.monotonic()
    try:
        files = read_sources(case)
        request = render(template, case, files)
        (request_dir / "prompt.txt").write_bytes(request)
        argv = command(executable, flags, response_path, run / "response.schema.json")
        receipt.update(argv=argv, prompt_bytes=len(request), prompt_sha256=sha(request))
        save(request_dir / "request.json", receipt)
        with events_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(argv, cwd=run / "isolated", stdin=subprocess.PIPE,
                                       stdout=stdout, stderr=stderr,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            receipt.update(native_start=True, pid=process.pid)
            save(request_dir / "request.json", receipt)
            process.communicate(input=request)
        usage, tool_events, errors = read_events(events_path)
        receipt.update(returncode=process.returncode, usage=usage, tool_events=tool_events,
                       reported_errors=errors)
        if tool_events:
            result["failure"] = "unexpected_tool_activity"
        elif process.returncode:
            result["failure"] = "provider_or_cli_failure"
        else:
            response = json.loads(response_path.read_text("utf-8"))
            rejected = accepted_evidence(response, files)
            rejected_counts = Counter(entry["group"] for entry in rejected)
            result.update(status="partial" if rejected else response["status"],
                          raw_output="raw/response.json", rejected_evidence=rejected,
                          operation_count=len(response["data_operations"]) - rejected_counts["data_operations"],
                          potential_excess_count=len(response["potential_excess"]) - rejected_counts["potential_excess"],
                          unknown_count=len(response["unknowns"]))
    except (OSError, ValueError, KeyError, TypeError) as error:
        result["failure"] = "response_validation" if receipt["native_start"] else "input_or_launch"
        result["error"] = str(error)
    receipt["elapsed_seconds"] = time.monotonic() - started
    receipt["finished_at"] = stamp()
    save(request_dir / "request.json", receipt)
    result.update(elapsed_seconds=receipt["elapsed_seconds"], usage=receipt["usage"],
                  native_start=receipt["native_start"])
    save(folder / "result.json", result)
    return result


def summary(run, planned, results, started, status):
    totals = Counter(result["status"] for result in results)
    usage_totals = Counter()
    for result in results:
        for key, value in (result.get("usage") or {}).items():
            if type(value) is int:
                usage_totals[key] += value
    record = {"status": status, "planned": planned, "finished_cases": len(results),
              "case_status_counts": dict(totals), "not_run": planned - len(results),
              "native_starts": sum(result["native_start"] for result in results),
              "known_usage_by_field": dict(usage_totals),
              "native_starts_without_usage": sum(result["native_start"] and result["usage"] is None
                                                  for result in results),
              "elapsed_seconds": time.monotonic() - started, "updated_at": stamp(),
              "cases": sorted(results, key=lambda result: result["case_id"])}
    save(run / "summary.json", record)
    print(json.dumps({key: value for key, value in record.items() if key != "cases"}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=COMPARISON / "inputs/clawhub-complex.json")
    parser.add_argument("--run-id", default="direct-audit-01")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--prepare-only", action="store_true")
    options = parser.parse_args()
    if not re.fullmatch(r"direct-audit-[0-9]{2,}", options.run_id) or options.workers < 1:
        parser.error("Use an ordinal direct-audit ID and at least one worker.")
    raw_manifest = options.manifest.read_bytes()
    cohort = json.loads(raw_manifest)
    cases = cohort["cases"]
    ids = [case["case_id"] for case in cases]
    if (len(ids) != 100 or len(set(ids)) != len(ids)
            or any(not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", case_id) for case_id in ids)):
        parser.error("Expected exactly 100 distinct, portable case IDs.")
    template = PROMPT.read_bytes()
    sizes = [len(render(template, case, read_sources(case))) for case in cases]
    if options.prepare_only:
        print(json.dumps({"verified_cases": len(cases), "max_prompt_bytes": max(sizes),
                          "total_prompt_bytes": sum(sizes), "native_starts": 0}))
        return
    executable = shutil.which("codex")
    if not executable:
        parser.error("The authenticated Codex CLI is required.")
    feature_rows = subprocess.check_output([executable, "features", "list"], text=True, encoding="utf-8")
    available = {row.split()[0] for row in feature_rows.splitlines() if row.split()}
    features = [feature for feature in DISABLED if feature in available]
    if not {"shell_tool", "unified_exec"}.issubset(features):
        parser.error("This CLI cannot disable both command execution entry points.")
    isolation = [feature for feature in SOURCE_ISOLATION if feature in available]
    flags = [flag for feature in features for flag in ("--disable", feature)]
    flags.extend(flag for feature in isolation for flag in ("--enable", feature))
    run = COMPARISON / "runs/strong-model" / options.run_id
    run.mkdir(parents=True, exist_ok=False)
    (run / "isolated").mkdir()
    (run / "cohort.json").write_bytes(raw_manifest)
    shutil.copyfile(SCHEMA, run / "response.schema.json")
    shutil.copyfile(PROMPT, run / "prompt-template.txt")
    save(run / "manifest.json", {
        "method": "strong-model", "variant": "direct_source_only_audit", "run_id": options.run_id,
        "cohort_sha256": sha(raw_manifest), "model": MODEL, "reasoning_effort": EFFORT,
        "provider": PROVIDER, "model_settings_evidence": "requested_cli_settings",
        "workers": options.workers, "requests_per_case": 1, "experiment_deadline_seconds": None,
        "cli_executable": executable, "cli_sha256": sha(Path(executable).read_bytes()),
        "disabled_features": features, "enabled_isolation_features": isolation,
        "started_at": stamp(), "controller_pid": os.getpid(),
        "runner_sha256": sha(Path(__file__).read_bytes()), "prompt_sizes_bytes": dict(zip(ids, sizes)),
        "prompt_template_sha256": sha(template), "response_schema_sha256": sha(SCHEMA.read_bytes()),
    })
    started = time.monotonic()
    results = []
    summary(run, len(cases), results, started, "running")
    # Use the first scheduled case to verify the provider can process this exact configuration.
    first = run_case(run, executable, flags, template, cases[0])
    results.append(first)
    if first.get("failure") in {"provider_or_cli_failure", "unexpected_tool_activity", "input_or_launch"}:
        summary(run, len(cases), results, started, "blocked_first_case")
        return 1
    summary(run, len(cases), results, started, "running")
    with ThreadPoolExecutor(max_workers=options.workers) as pool:
        pending = [pool.submit(run_case, run, executable, flags, template, case) for case in cases[1:]]
        for done in as_completed(pending):
            results.append(done.result())
            summary(run, len(cases), results, started, "running")
    status = "completed" if all(result["status"] == "completed" for result in results) else "partial"
    summary(run, len(cases), results, started, status)


if __name__ == "__main__":
    raise SystemExit(main())
