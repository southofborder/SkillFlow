"""Run the paper-based SkillPrivus variant with controlled Codex transport."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from functools import partial
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import time

import prepare as paper


VARIANT = f"{paper.VARIANT}-controlled-codex"
TRANSPORT = paper.COMPARISON / "methods" / "strong-model" / "run.py"
MODEL_SETTINGS = ("gpt-6.1-sol", "high", "openai")
WRAPPED_STAGES = {"judgment", "harm"}
TEXT = {"type": "string"}
MAYBE_TEXT = {"type": ["string", "null"]}


def obj(**fields):
    return {"type": "object", "properties": fields, "required": list(fields), "additionalProperties": False}


def array(items):
    return {"type": "array", "items": items}


def choices(values, *, nullable=False):
    return {**(MAYBE_TEXT if nullable else TEXT), "enum": sorted(values) + ([None] if nullable else [])}


def response_schemas():
    integer = {"type": "integer"}
    evidence = array(obj(path=TEXT, start_line=integer, end_line=integer, quote=TEXT))
    ci = obj(**{field: MAYBE_TEXT for field in paper.CI_REQUIRED},
             sensitive={"type": ["boolean", "null"]}, protection=MAYBE_TEXT,
             derivation=MAYBE_TEXT, consent_signal=MAYBE_TEXT)
    moves = array(obj(move_id=TEXT, operation=choices(paper.OPERATIONS), data=TEXT,
                      source=MAYBE_TEXT, recipient=MAYBE_TEXT, condition=MAYBE_TEXT, evidence=evidence))
    return {
        "screening": obj(status=choices({"included", "excluded", "unresolved"}), reason=TEXT, evidence=evidence),
        "extraction": obj(status=choices({"complete", "incomplete"}), reason=TEXT, claim=MAYBE_TEXT,
                          claim_evidence=evidence, moves=moves),
        "judgment": obj(rows=array(obj(move_id=TEXT, verdict=choices({"Violation", "Ok", "Incomplete"}),
                                       departed_param=choices(paper.DEPARTURES, nullable=True), reason=TEXT, ci=ci))),
        "harm": obj(rows=array(obj(move_id=TEXT, harm_type=choices(paper.HARMS, nullable=True), reason=TEXT))),
    }


def stamp():
    return datetime.now(timezone.utc).isoformat()


def render(stage: str, packet: dict) -> bytes:
    if packet["stage"] != stage:
        raise ValueError(f"Request stage differs: {stage}")
    instructions = packet["instructions"]
    if stage in WRAPPED_STAGES:
        instructions += '\nTransport format: place the requested array inside a JSON object under the key "rows".\n'
    return instructions.encode("utf-8") + b"\nAudit evidence (JSON):\n" + paper.json_bytes(packet["input"], compact=True)


def read_cohort(raw: bytes) -> list[dict]:
    cases = paper.parse(raw)["cases"]
    ids = [paper.safe_id(case["case_id"]) for case in cases]
    if len(ids) != 100 or len(set(ids)) != len(ids):
        raise ValueError("Expected exactly 100 distinct ClawHub cases")
    return cases


def setup_transport():
    executable = shutil.which("codex")
    if not executable:
        raise ValueError("The authenticated Codex CLI is required for the controlled variant")
    transport = runpy.run_path(str(TRANSPORT), run_name="strong_model_transport")
    arguments = tuple(transport[key] for key in ("MODEL", "EFFORT", "PROVIDER"))
    if arguments != MODEL_SETTINGS:
        raise ValueError("Strong-model transport settings differ from the pinned controlled settings")
    feature_rows = subprocess.check_output([executable, "features", "list"], text=True, encoding="utf-8")
    available = {row.split()[0] for row in feature_rows.splitlines() if row.split()}
    disabled = [name for name in transport["DISABLED"] if name in available]
    if not {"shell_tool", "unified_exec"}.issubset(disabled):
        raise ValueError("The CLI must support disabling both command execution features")
    enabled = [name for name in transport["SOURCE_ISOLATION"] if name in available]
    flags = [flag for name in disabled for flag in ("--disable", name)]
    flags.extend(flag for name in enabled for flag in ("--enable", name))
    return executable, transport, flags, disabled, enabled


def invoke(run_dir: Path, executable, transport, flags, case_dir: Path, stage: str, prompt: bytes) -> dict:
    request_dir, raw = case_dir / "requests", case_dir / "raw"
    wire = raw / f"{stage}.wire.json"
    events = raw / f"{stage}.events.jsonl"
    stderr = raw / f"{stage}.stderr.txt"
    receipt_path = request_dir / f"{stage}.receipt.json"
    argv = transport["command"](executable, flags, wire, run_dir / "schemas" / f"{stage}.json")
    started = time.monotonic()
    receipt = {
        "stage": stage, "argv": argv, "native_start": False, "usage": None,
        "prompt_bytes": len(prompt), "prompt_sha256": paper.digest(prompt), "started_at": stamp(),
    }
    transport["save"](receipt_path, receipt)
    try:
        with events.open("xb") as stdout, stderr.open("xb") as error:
            process = subprocess.Popen(argv, cwd=run_dir / "isolated", stdin=subprocess.PIPE,
                                       stdout=stdout, stderr=error,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            receipt.update(native_start=True, pid=process.pid)
            transport["save"](receipt_path, receipt)
            process.communicate(input=prompt)
        usage, tool_events, errors = transport["read_events"](events)
        receipt.update(returncode=process.returncode, usage=usage, tool_events=tool_events, reported_errors=errors)
        if tool_events:
            receipt["failure"] = "unexpected_tool_activity"
        elif process.returncode:
            receipt["failure"] = "provider_or_cli_failure"
        if wire.is_file():
            receipt["wire_sha256"] = paper.digest(wire.read_bytes())
    except OSError as error:
        receipt["failure"] = "provider_or_cli_failure" if receipt["native_start"] else "input_or_launch"
        receipt["error"] = str(error)
    receipt.update(elapsed_seconds=time.monotonic() - started, finished_at=stamp())
    transport["save"](receipt_path, receipt)
    return receipt


def run_case(run_dir: Path, case: dict, dispatch) -> dict:
    case_id = case["case_id"]
    case_dir = run_dir / "cases" / case_id
    stage = "screening"
    started = time.monotonic()
    receipts = []
    result = {"case_id": case_id, "status": "failed", "native_status": "stage_failure",
              "package_bytes_sha256": case["package_bytes_sha256"]}
    try:
        while stage != "finished":
            packet = paper.parse((case_dir / "requests" / f"{stage}.json").read_bytes())
            prompt = render(stage, packet)
            with (case_dir / "requests" / f"{stage}.txt").open("xb") as stream:
                stream.write(prompt)
            receipt = dispatch(case_dir, stage, prompt)
            receipts.append(receipt)
            if receipt.get("failure"):
                result.update(failure=receipt["failure"], failed_stage=stage)
                break
            wire = (case_dir / "raw" / f"{stage}.wire.json").read_bytes()
            answer = paper.parse(wire)
            if stage in WRAPPED_STAGES:
                answer = answer["rows"]
            paper.freeze_json(case_dir / "raw" / f"{stage}.json", answer)
            stage = paper.advance(run_dir, case_id, stage, result_file="method-result.json")
        if stage == "finished":
            method = paper.parse((case_dir / "method-result.json").read_bytes())
            result.update(status=method["status"], native_status=method["native_status"], method_result="method-result.json")
    except (OSError, ValueError, KeyError, TypeError) as error:
        result.update(failed_stage=stage, failure="stage_validation", error=str(error))
    usage = Counter()
    for receipt in receipts:
        for key, amount in (receipt["usage"] or {}).items():
            if type(amount) is int:
                usage[key] += amount
    result.update(native_starts=sum(r["native_start"] for r in receipts), known_usage_by_field=dict(usage),
                  starts_without_usage=sum(r["native_start"] and r["usage"] is None for r in receipts),
                  requests=[f"requests/{r['stage']}.receipt.json" for r in receipts],
                  elapsed_seconds=time.monotonic() - started)
    paper.freeze_json(case_dir / "result.json", result)
    return result


def summary(run_dir, results, planned, started, status, save):
    usage = Counter()
    for result in results:
        usage.update(result["known_usage_by_field"])
    record = {
        "status": status, "planned": planned, "finished_cases": len(results), "not_run": planned - len(results),
        "case_status_counts": dict(Counter(result["status"] for result in results)),
        "native_status_counts": dict(Counter(result["native_status"] for result in results)),
        "native_starts": sum(result["native_starts"] for result in results), "known_usage_by_field": dict(usage),
        "native_starts_without_usage": sum(result["starts_without_usage"] for result in results),
        "elapsed_seconds": time.monotonic() - started, "updated_at": stamp(),
    }
    save(run_dir / "summary.json", record)
    print(paper.json_bytes(record, compact=True).decode(), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", type=Path, default=paper.COMPARISON / "inputs" / "clawhub-complex.json")
    parser.add_argument("--run-id", default="paper-based-controlled-01")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--prepare-only", action="store_true", help="verify inputs and render screening in memory")
    args = parser.parse_args()
    if not re.fullmatch(r"paper-based-controlled-[0-9]{2,}", args.run_id) or args.workers < 1:
        parser.error("Use an ordinal paper-based-controlled ID and at least one worker")
    raw_cohort = args.cohort.read_bytes()
    cases = read_cohort(raw_cohort)
    schemas = response_schemas()
    if args.prepare_only:
        instructions = (paper.HERE / "prompts" / "screening.txt").read_text(encoding="utf-8")
        sizes = [len(render("screening", {"stage": "screening", "instructions": instructions,
                     "input": {"skill": case["slug"], "files": paper.source_files(case)}})) for case in cases]
        print(paper.json_bytes({"verified_cases": len(cases), "max_screening_bytes": max(sizes),
                               "schemas": len(schemas), "native_starts": 0}, compact=True).decode())
        return 0

    executable, transport, flags, disabled, enabled = setup_transport()
    run_dir = paper.COMPARISON / "runs" / "skillprivus" / args.run_id
    if not run_dir.resolve().is_relative_to(paper.COMPARISON):
        raise ValueError("Run path escapes comparison directory")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "isolated").mkdir()
    cohort_copy = run_dir / "cohort.json"
    cohort_copy.write_bytes(raw_cohort)
    templates = run_dir / "prompt-templates"
    templates.mkdir()
    prompt_hashes = {}
    for stage in paper.STAGES:
        name = f"{stage}.txt"
        data = (paper.HERE / "prompts" / name).read_bytes()
        (templates / name).write_bytes(data)
        prompt_hashes[stage] = paper.digest(data)
    schema_hashes = {stage: paper.freeze_json(run_dir / "schemas" / f"{stage}.json", schema)
                     for stage, schema in schemas.items()}
    paper.prepare(run_dir, cohort_copy, [], execution={
        "method": "skillprivus", "variant": VARIANT, "run_id": args.run_id, "status": "online_run",
        "model": MODEL_SETTINGS[0], "reasoning_effort": MODEL_SETTINGS[1], "provider": MODEL_SETTINGS[2],
        "model_settings_evidence": "requested_cli_settings", "experiment_deadline_seconds": None,
        "workers": args.workers, "requests_per_executed_stage": 1, "controller_pid": os.getpid(),
        "started_at": stamp(), "cli_executable": executable, "cli_sha256": paper.digest(Path(executable).read_bytes()),
        "transport_sha256": paper.digest(TRANSPORT.read_bytes()), "stage_schema_sha256": schema_hashes,
        "runner_sha256": paper.digest(Path(__file__).read_bytes()),
        "paper_runner_sha256": paper.digest(Path(paper.__file__).read_bytes()), "prompt_template_sha256": prompt_hashes,
        "disabled_features": disabled, "enabled_isolation_features": enabled,
    })
    dispatch = partial(invoke, run_dir, executable, transport, flags)
    report = partial(summary, run_dir, planned=len(cases), started=time.monotonic(), save=transport["save"])
    results = []
    report(results, status="running")
    first = run_case(run_dir, cases[0], dispatch)
    results.append(first)
    if first.get("failure") in {"input_or_launch", "unexpected_tool_activity", "provider_or_cli_failure"}:
        report(results, status="blocked_first_case")
        return 1
    report(results, status="running")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = [pool.submit(run_case, run_dir, case, dispatch) for case in cases[1:]]
        for task in as_completed(pending):
            results.append(task.result())
            report(results, status="running")
    status = "completed" if all(result["status"] == "completed" for result in results) else "partial"
    report(results, status=status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
