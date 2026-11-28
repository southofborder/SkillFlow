"""Verify or run the prepared Semia comparison through its native report."""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import time
from unittest.mock import patch

import prepare


COMPARISON = Path(__file__).resolve().parents[2]
STRONG_RUNNER = COMPARISON / "methods/strong-model/run.py"
STRONG = runpy.run_path(str(STRONG_RUNNER))
ARTIFACTS = (
    "prepare_metadata.json", "prepare_units.json", "prepare_units.dl", "prepared_skill.md",
    "run_manifest.json", "synthesis_prompt.md", "preparation-receipt.json",
    "initial-synthesis-prompt.txt",
)
REQUEST_TIMEOUT_SECONDS = 2700
NATIVE_START_CAP = 60


def verify_cli(strong):
    executable = Path(strong["cli_executable"])
    if not executable.is_absolute() or prepare.sha256(executable) != strong["cli_sha256"]:
        raise ValueError("CLI differs from the strong-model executable pin")


def preflight(preparation_path, strong_path):
    from semia_cli import synthesis_loop

    prepared = prepare.read_json(preparation_path)
    strong = prepare.read_json(strong_path)
    cohort_path = prepare.REPOSITORY / prepared["cohort"]
    cohort = prepare.read_json(cohort_path)
    cohort_sha = prepare.sha256(cohort_path)
    if (
        strong["method"] != "strong-model"
        or strong["cohort_sha256"] != cohort_sha
        or strong["runner_sha256"] != prepare.sha256(STRONG_RUNNER)
        or (strong["model"], strong["reasoning_effort"], strong["provider"])
        != (STRONG["MODEL"], STRONG["EFFORT"], STRONG["PROVIDER"])
    ):
        raise ValueError("Strong-model transport or cohort does not match")
    verify_cli(strong)
    disabled = set(strong["disabled_features"])
    isolation = set(strong["enabled_isolation_features"])
    if not {"shell_tool", "unified_exec"} <= disabled or not set(STRONG["SOURCE_ISOLATION"]) <= isolation:
        raise ValueError("Pinned strong-model transport did not bind source and tool isolation")
    if (
        prepared["status"] != "offline_preparation_complete"
        or prepared["cohort_sha256"] != cohort_sha
        or prepared["upstream_commit"] != prepare.COMMIT
        or prepared["variant"] != prepare.VARIANTS["complete-source"]
        or prepared["preparation_entry_point_sha256"] != prepare.sha256(Path(prepare.__file__))
    ):
        raise ValueError("Semia preparation identity does not match")
    rows = prepared["cases"]
    cases = cohort["cases"]
    if len(cases) != 100 or [row["case_id"] for row in rows] != [case["case_id"] for case in cases]:
        raise ValueError("Semia preparation does not cover the ordered 100-case cohort")
    bound_cases = []
    seen = set()
    for case, row in zip(cases, rows, strict=True):
        case_id = case["case_id"]
        relative = f"cases/{case_id}/raw/preparation-receipt.json"
        if not re.fullmatch(r"clawhub-[0-9]{4}", case_id) or case_id in seen or row["receipt"] != relative:
            raise ValueError(f"Semia case path is not uniquely bound: {case_id}")
        seen.add(case_id)
        source = (preparation_path.parent / relative).parent
        receipt = prepare.read_json(source / "preparation-receipt.json")
        pins = {name: prepare.sha256(source / name) for name in ARTIFACTS}
        if (
            pins["preparation-receipt.json"] != row["receipt_sha256"]
            or receipt["case_id"] != case_id
            or receipt["status"] != "prepared_offline"
            or receipt["manifest_sha256"] != cohort_sha
            or receipt["package_bytes_sha256"] != case["package_bytes_sha256"]
            or not receipt["source_body_complete_after_upstream_normalization"]
            or pins["initial-synthesis-prompt.txt"] != receipt["initial_prompt_sha256"]
            or pins["prepared_skill.md"] != receipt["native_prepared_source_sha256"]
            or STRONG["sha"](synthesis_loop._prompt(source).encode("utf-8")) != receipt["initial_prompt_sha256"]
        ):
            raise ValueError(f"Semia preparation artifact mismatch: {case_id}")
        STRONG["read_sources"](case)
        bound_cases.append({
            "case_id": case_id, "preparation_root": str(source), "prepared_sha256": pins,
            "package_bytes_sha256": case["package_bytes_sha256"],
        })
    return strong, cohort_sha, bound_cases


def native_command(strong, response):
    flags = [piece for mode, key in (("--disable", "disabled_features"),
                                      ("--enable", "enabled_isolation_features"))
             for feature in strong[key] for piece in (mode, feature)]
    argv = STRONG["command"](strong["cli_executable"], flags, response, "")
    # Share the isolated CLI invocation while preserving Semia's native Datalog response format.
    schema_index = argv.index("--output-schema")
    del argv[schema_index:schema_index + 2]
    return argv


class Transport:
    def __init__(self, folder, raw, strong, isolated):
        self.folder, self.raw, self.strong, self.isolated = folder, raw, strong, isolated
        self.calls = []
        self.preparation = prepare.read_json(raw / "preparation-receipt.json")
        self.prepared = (raw / "prepared_skill.md").read_text(encoding="utf-8").rstrip()
        self.nonce = prepare.read_json(raw / "prepare_metadata.json")["hostile_input_nonce"]

    def __call__(self, root, prompt, model):
        from semia_cli.llm_config import LlmSynthesisConfigError, LlmSynthesisError

        if root != self.raw or model != self.strong["model"] or len(self.calls) >= NATIVE_START_CAP:
            raise LlmSynthesisConfigError("Semia call exceeded its configured case, model or budget")
        target = self.folder / "requests" / f"call-{len(self.calls) + 1:03d}"
        target.mkdir(parents=True, exist_ok=False)
        request = prompt.encode("utf-8")
        (target / "prompt.txt").write_bytes(request)
        response_path = target / "response.txt"
        argv = native_command(self.strong, response_path)
        call = {
            "call": target.name, "argv": argv, "native_start": False, "usage": None,
            "prompt_bytes": len(request), "prompt_chars": len(prompt),
            "prompt_sha256": STRONG["sha"](request), "started_at": STRONG["stamp"](),
            "complete_source_fence_verified": False,
        }
        self.calls.append(call)
        started = time.monotonic()
        try:
            block = f"<<<SEMIA_HOSTILE_INPUT id={self.nonce}>>>\n{self.prepared}\n<<<SEMIA_END id={self.nonce}>>>"
            if prompt.count(block) != 1 or (
                len(self.calls) == 1 and call["prompt_sha256"] != self.preparation["initial_prompt_sha256"]
            ):
                raise LlmSynthesisConfigError("Outgoing Semia request differs from prepared source")
            call["complete_source_fence_verified"] = True
            STRONG["save"](target / "request.json", call)
            events_path = target / "events.jsonl"
            with events_path.open("wb") as stdout, (target / "stderr.txt").open("wb") as stderr:
                process = subprocess.Popen(
                    argv, cwd=self.isolated, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                call.update(native_start=True, pid=process.pid)
                STRONG["save"](target / "request.json", call)
                try:
                    process.communicate(input=request, timeout=REQUEST_TIMEOUT_SECONDS)
                except subprocess.TimeoutExpired:
                    call["timed_out"] = True
                    try:
                        if process.poll() is None:
                            cleanup = subprocess.run(
                                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                timeout=30, capture_output=True,
                            )
                            call["cleanup_returncode"] = cleanup.returncode
                        process.wait(timeout=30)
                    except (OSError, subprocess.TimeoutExpired) as error:
                        raise LlmSynthesisConfigError("Timed-out Semia CLI did not cleanly exit") from error
            usage, tools, errors = STRONG["read_events"](events_path)
            call.update(returncode=process.returncode, usage=usage, tool_events=tools, reported_errors=errors)
            if tools:
                raise LlmSynthesisConfigError("Unexpected tool activity in Semia request")
            if call.get("timed_out") or process.returncode or not response_path.is_file():
                raise LlmSynthesisError("Semia CLI request failed")
            call["response_sha256"] = prepare.sha256(response_path)
            return response_path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as error:
            call["error"] = str(error)
            raise LlmSynthesisError(str(error)) from error
        except LlmSynthesisError as error:
            call["error"] = str(error)
            raise
        finally:
            call.update(elapsed_seconds=time.monotonic() - started, finished_at=STRONG["stamp"]())
            STRONG["save"](target / "request.json", call)


def run_case(run, case, strong):
    from semia_cli import core_adapter, llm_adapter, llm_providers

    folder = run / "cases" / case["case_id"]
    raw = folder / "raw"
    raw.mkdir(parents=True, exist_ok=False)
    validations = raw / "validations"
    validations.mkdir()
    result = {
        "case_id": case["case_id"], "package_bytes_sha256": case["package_bytes_sha256"],
        "status": "failed", "synthesis_status": "not_run", "detection_status": "not_run",
        "recommendation_status": "not_requested",
    }
    started = time.monotonic()
    checks = 0
    transport = None

    def validate(run_dir, facts_path=None):
        nonlocal checks
        checks += 1
        attempted = facts_path or raw / "synthesized_facts.dl"
        record = {"submitted_facts_sha256": prepare.sha256(attempted)}
        try:
            record["payload"] = core_adapter.check(run_dir, facts_path)
            return record["payload"]
        except Exception as error:
            record["error"] = f"{type(error).__name__}: {error}"
            raise
        finally:
            STRONG["save"](validations / f"check-{checks:03d}.json", record)

    try:
        for name, digest in case["prepared_sha256"].items():
            shutil.copyfile(Path(case["preparation_root"]) / name, raw / name)
            if prepare.sha256(raw / name) != digest:
                raise ValueError(f"Semia prepared artifact changed: {name}")
        transport = Transport(folder, raw, strong, run / "isolated")
        result["synthesis_status"] = "failed"
        with patch.object(llm_providers, "_run_codex", transport):
            synthesis = llm_adapter.synthesize_facts(
                raw, provider="codex", model=strong["model"], validator=validate,
            )
        final_check = validate(raw, raw / "synthesized_facts.dl")
        if not final_check["program_valid"] or final_check["errors"] != 0:
            raise ValueError("Selected Semia program did not pass native validation")
        result.update(synthesis_status="validated", synthesis=synthesis, detection_status="failed")
        detection = core_adapter.detect(raw)
        result["detection_status"] = detection["status"]
        core_adapter.report(raw, "md")
        core_adapter.report(raw, "json")
        result["native_detection"] = "raw/detection_result.json"
        if detection["status"] == "ok":
            result.update(status="completed", native_finding_count=detection["findings"])
        else:
            result["status"] = "partial"
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
        if result["synthesis_status"] == "validated":
            result["status"] = "partial"
    calls = transport.calls if transport else []
    result.update(
        elapsed_seconds=time.monotonic() - started,
        native_starts=sum(call["native_start"] for call in calls),
        native_starts_without_usage=sum(call["native_start"] and call["usage"] is None for call in calls),
        validation_count=checks,
    )
    usage = Counter()
    for call in calls:
        usage.update({key: value for key, value in (call["usage"] or {}).items() if type(value) is int})
    result["known_usage_by_field"] = dict(usage)
    STRONG["save"](folder / "result.json", result)
    return result


def worker_setup(isolated, strong):
    prepare.verify_runtime()
    verify_cli(strong)
    for name in list(os.environ):
        if name.startswith("SEMIA_"):
            del os.environ[name]
    os.environ["SEMIA_DETECTOR_BACKEND"] = "builtin"
    os.chdir(isolated)


def summary(run, results, planned, started, status):
    counts = Counter(row["status"] for row in results)
    usage = Counter()
    for row in results:
        usage.update(row["known_usage_by_field"])
    STRONG["save"](run / "summary.json", {
        "status": status, "planned": planned, "finished_cases": len(results),
        "not_run": planned - len(results), "case_status_counts": dict(counts),
        "native_starts": sum(row["native_starts"] for row in results),
        "native_starts_without_usage": sum(row["native_starts_without_usage"] for row in results),
        "known_usage_by_field": dict(usage),
        "elapsed_seconds": time.monotonic() - started,
        "cases": sorted(results, key=lambda row: row["case_id"]),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preparation", type=Path, default=COMPARISON / "runs/semia/complete-source-01/manifest.json")
    parser.add_argument("--strong-manifest", type=Path,
                        default=COMPARISON / "runs/strong-model/direct-audit-01/manifest.json")
    parser.add_argument("--run-id", help="Explicit ordinal ID to launch, such as semia-audit-01")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if args.workers < 1 or (args.run_id and not re.fullmatch(r"semia-audit-[0-9]{2,}", args.run_id)):
        parser.error("Use an ordinal semia-audit ID and at least one worker")
    prepare.verify_runtime()
    preparation = args.preparation.resolve()
    strong_path = args.strong_manifest.resolve()
    strong, cohort_sha, cases = preflight(preparation, strong_path)
    if args.run_id is None:
        print(json.dumps({"verified_cases": len(cases), "cohort_sha256": cohort_sha,
                          "cli_sha256": strong["cli_sha256"], "native_starts": 0}))
        return

    run = COMPARISON / "runs/semia" / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    (run / "isolated").mkdir()
    STRONG["save"](run / "manifest.json", {
        "method": "semia", "variant": "semia-379bc25f-controlled-complete-utf8-source-v1",
        "run_id": args.run_id, "cohort_sha256": cohort_sha, "upstream_commit": prepare.COMMIT,
        "preparation_manifest_sha256": prepare.sha256(preparation),
        "strong_transport_manifest_sha256": prepare.sha256(strong_path),
        "runner_sha256": prepare.sha256(Path(__file__)), "workers": args.workers,
        "model": strong["model"], "reasoning_effort": strong["reasoning_effort"],
        "provider": strong["provider"], "cli_executable": strong["cli_executable"],
        "cli_sha256": strong["cli_sha256"], "disabled_features": strong["disabled_features"],
        "enabled_isolation_features": strong["enabled_isolation_features"],
        "detector": "builtin", "recommendation_status": "not_requested",
        "synthesis_iterations": 5, "structural_retries": 3, "provider_retries": 2,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS, "max_native_starts_per_case": NATIVE_START_CAP,
        "experiment_deadline_seconds": None, "controller_pid": os.getpid(),
        "started_at": STRONG["stamp"](), "cases": cases,
    })
    started = time.monotonic()
    results = []
    summary(run, results, len(cases), started, "running")
    try:
        with ProcessPoolExecutor(max_workers=args.workers, initializer=worker_setup,
                                 initargs=(run / "isolated", strong)) as pool:
            pending = [pool.submit(run_case, run, case, strong) for case in cases]
            for done in as_completed(pending):
                results.append(done.result())
                summary(run, results, len(cases), started, "running")
    except Exception:
        summary(run, results, len(cases), started, "controller_error")
        raise
    completed = all(row["status"] == "completed" for row in results)
    summary(run, results, len(cases), started, "completed" if completed else "partial")
    return 0 if completed else 2


if __name__ == "__main__":
    raise SystemExit(main())
