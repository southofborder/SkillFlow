"""Controlled Semia complete-source comparison. Default: read-only preflight.

--run requires the first pilot's terminal receipt and a root-reviewed closeout.
The upstream prompt, checker, synthesis loop and detector are not modified.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time
from typing import Any

BASE = Path(__file__).resolve().parent
COMMIT = "379bc25fe99833eb185efe56a38fe15f0235799c"
MODEL = "gpt-6.1-sol"
VARIANT = "semia-379bc25f-controlled-complete-source-v1"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_path(root: Path, relative: str) -> Path:
    rel = PurePosixPath(relative)
    if rel.is_absolute() or ".." in rel.parts or ":" in str(rel):
        raise ValueError(f"Unsafe manifest path: {relative}")
    path = root / str(rel)
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Manifest path escapes root: {relative}")
    return path


def verify_sources() -> dict[str, str]:
    pins = json.loads((BASE / "source-manifest.json").read_text("utf-8"))
    first = json.loads((BASE / "pilot/001/runtime.json").read_text("utf-8"))
    expected = {row["path"]: row["sha256"] for row in pins["files"]}
    if pins["commit"] != COMMIT or len(expected) != 360 or len(pins["files"]) != 360:
        raise ValueError("Official source manifest identity mismatch")
    if expected != first["source_file_hashes"]:
        raise ValueError("Source manifest differs from first pilot's fixed source")
    source = BASE / "source"
    actual = {p.relative_to(source).as_posix() for p in source.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    if actual != set(expected):
        raise ValueError("Source inventory drift")
    for relative, digest in expected.items():
        if sha(safe_path(source, relative)) != digest:
            raise ValueError(f"Source hash mismatch: {relative}")
    return expected


def verify_inputs(case_id: str) -> dict:
    first = json.loads((BASE / "pilot/001/runtime.json").read_text("utf-8"))
    if sha(BASE / "input-manifest.json") != first["input_manifest_sha256"]:
        raise ValueError("Input manifest changed since the first pilot")
    manifest = json.loads((BASE / "input-manifest.json").read_text("utf-8"))
    matches = [case for case in manifest["cases"] if case["case_id"] == case_id]
    if len(matches) != 1:
        raise ValueError("Case must be uniquely present in input manifest")
    case = matches[0]
    root = safe_path(BASE, case["path"])
    expected = {item["path"] for item in case["files"]}
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    if len(expected) != len(case["files"]) or expected != actual:
        raise ValueError("Input file inventory drift")
    for item in case["files"]:
        path = safe_path(root, item["path"])
        if sha(path) != item["sha256"] or path.stat().st_size != item["size"]:
            raise ValueError(f"Input hash/size mismatch: {item['path']}")
    return case


def verify_closeout() -> dict:
    finished = BASE / "pilot/001/finished.json"
    closeout = BASE / "analysis/001-closeout.json"
    if not finished.is_file() or not closeout.is_file():
        raise ValueError("001 terminal receipt and root-reviewed analysis closeout are required")
    terminal = json.loads(finished.read_text("utf-8"))
    receipt = json.loads(closeout.read_text("utf-8"))
    if not all(k in terminal for k in ("exit_code", "finished_at_utc", "native_starts")):
        raise ValueError("First pilot receipt is not terminal")
    required = {"status": "complete", "pilot_finished_sha256": sha(finished),
                "input_manifest_sha256": sha(BASE / "input-manifest.json"), "source_commit": COMMIT}
    if any(receipt.get(key) != value for key, value in required.items()):
        raise ValueError("Root analysis closeout is missing or is bound to different evidence")
    # A failed first pipeline is legitimate baseline evidence and does not block later cases.
    return receipt


def verify_imported_upstream(expected: dict[str, str]) -> None:
    source = (BASE / "source").resolve()
    for name, module in tuple(sys.modules.items()):
        if not name.startswith(("semia_core", "semia_cli")) or not getattr(module, "__file__", None):
            continue
        path = Path(module.__file__).resolve()
        if not path.is_relative_to(source):
            raise ValueError(f"Upstream module imported outside pinned source: {name}")
        relative = path.relative_to(source).as_posix()
        if relative not in expected or sha(path) != expected[relative]:
            raise ValueError(f"Imported upstream module is not pinned: {name}")


def command(executable: str, directory: Path) -> list[str]:
    disabled = ("plugins", "remote_plugin", "recommended_plugins", "shell_tool", "unified_exec",
                "apps", "browser_use", "browser_use_external", "computer_use", "in_app_browser",
                "image_generation", "view_image", "multi_agent", "multi_agent_v2", "hooks",
                "skill_search", "skill_mcp_dependency_install", "code_mode_host", "memories")
    flags = [part for name in disabled for part in ("--disable", name)]
    return [executable, *flags, "exec", "--ignore-user-config", "--ignore-rules",
            "--skip-git-repo-check", "--sandbox", "read-only", "--color", "never", "--json",
            "--model", MODEL, "-c", 'model_reasoning_effort="high"',
            "-c", 'model_provider="openai"', "-c", "project_doc_max_bytes=0",
            "-c", 'web_search="disabled"', "--output-last-message", str(directory / "response.txt"), "-"]


class Transport:
    def __init__(self, run: Path, executable: str, provider: Any, timeout: float = 2700):
        self.run, self.executable, self.provider, self.timeout = run, executable, provider, timeout
        self.phase = "cgrs"
        self.calls: list[dict] = []

    def __call__(self, root: Path, prompt: str, model: str | None) -> str:
        cap = {"cgrs": 60, "recommendation": 3}[self.phase]
        if model != MODEL or len(self.calls) >= 63 or sum(c["phase"] == self.phase for c in self.calls) >= cap:
            raise self.provider.LlmSynthesisConfigError("Model/phase/call budget mismatch")
        directory = self.run / "transport" / f"call-{len(self.calls)+1:03d}"
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "prompt.txt").write_bytes(prompt.encode("utf-8"))
        record = {"id": directory.name, "phase": self.phase, "argv": command(self.executable, directory),
                  "prompt_bytes": len(prompt.encode("utf-8")), "started_at_utc": utc(),
                  "native_start": False, "returncode": None, "usage": None, "error": None}
        self.calls.append(record)
        save(directory / "request.json", record)
        started = time.monotonic()
        try:
            try:
                receipt = json.loads((root / "complete-source-receipt.json").read_text("utf-8"))
                metadata = json.loads((root / "prepare_metadata.json").read_text("utf-8"))
                prepared_path = root / "prepared_skill.md"
                if not receipt.get("all_files_present") or sha(prepared_path) != receipt["prepared_sha256"]:
                    raise ValueError("Prepared complete-source receipt mismatch")
                nonce = metadata["hostile_input_nonce"]
                if not isinstance(nonce, str) or not nonce:
                    raise ValueError("Missing hostile-input fence nonce")
                begin = re.escape(f"<<<SEMIA_HOSTILE_INPUT id={nonce}>>>")
                end = re.escape(f"<<<SEMIA_END id={nonce}>>>")
                bodies = re.findall(begin + r"\n(.*?)\n" + end, prompt, flags=re.DOTALL)
                body = prepared_path.read_text("utf-8").rstrip("\r\n")
                if sum(block.rstrip("\r\n") == body for block in bodies) != 1:
                    raise ValueError("Actual outgoing prompt omits or duplicates complete source body")
                record["source_payload_verified"] = True
                record["complete_source_receipt_sha256"] = sha(root / "complete-source-receipt.json")
            except (OSError, ValueError, KeyError) as exc:
                raise self.provider.LlmSynthesisConfigError(str(exc)) from exc
            with (directory / "stdout.jsonl").open("wb") as stdout, (directory / "stderr.txt").open("wb") as stderr:
                child = subprocess.Popen(record["argv"], stdin=subprocess.PIPE, stdout=stdout, stderr=stderr,
                                         cwd=directory, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                record.update(native_start=True, pid=child.pid)
                save(directory / "request.json", record)
                try:
                    child.communicate(input=prompt.encode("utf-8"), timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    record["timed_out"] = True
                    killed = subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"],
                                            capture_output=True, timeout=30)
                    record["tree_cleanup_returncode"] = killed.returncode
                    try:
                        child.wait(timeout=30)
                    except subprocess.TimeoutExpired as exc:
                        record["tree_cleanup_unresolved"] = True
                        raise self.provider.LlmSynthesisConfigError("Timed-out process did not exit; refusing retries") from exc
                record["returncode"] = child.returncode
            usages, unexpected = [], []
            for line in (directory / "stdout.jsonl").read_text("utf-8", errors="replace").splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(event, dict):
                    continue
                if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
                    usages.append(event["usage"])
                item = event.get("item", {})
                if isinstance(item, dict) and item.get("type") in ("command_execution", "mcp_tool_call", "web_search", "function_call"):
                    unexpected.append(item.get("type"))
            record["public_turn_usages"] = usages
            if usages:
                record["usage"] = {key: sum(u.get(key, 0) for u in usages)
                                   for key in set().union(*(u.keys() for u in usages))
                                   if all(isinstance(u.get(key, 0), (int, float)) for u in usages)}
            record["unexpected_tool_events"] = unexpected
            if unexpected:
                raise self.provider.LlmSynthesisConfigError("Unexpected tool activity; see recorded public events")
            if record.get("timed_out") or record["returncode"] != 0:
                raise self.provider.LlmSynthesisError(f"Native request failed; see {directory}")
            response = directory / "response.txt"
            if not response.is_file():
                raise self.provider.LlmSynthesisError(f"Missing response; see {directory}")
            record["response_sha256"] = sha(response)
            return response.read_text("utf-8")
        except OSError as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise self.provider.LlmSynthesisError(record["error"]) from exc
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 3)
            save(directory / "request.json", record)
            save(self.run / "calls.json", self.calls)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("010", "013", "ga4"), required=True)
    parser.add_argument("--run", action="store_true", help="Launch only after first-pilot closeout")
    parser.add_argument("--dry-run", action="store_true", help="Explicit read-only preflight (the default)")
    args = parser.parse_args(argv)
    if args.run and args.dry_run:
        parser.error("--run and --dry-run are mutually exclusive")
    expected = verify_sources()
    case = verify_inputs(args.case)
    first = json.loads((BASE / "pilot/001/runtime.json").read_text("utf-8"))
    executable = Path(first["cli_executable"])
    if not executable.is_file() or sha(executable) != first["cli_sha256"]:
        raise ValueError("The first pilot's pinned CLI is missing or changed")
    sys.path[:0] = [str(BASE), *(str(BASE / f"source/packages/{p}/src") for p in ("semia-core", "semia-cli"))]
    helper_path = BASE / "adapters/complete_source.py"
    helper_spec = importlib.util.spec_from_file_location("semia_comparison_complete_source", helper_path)
    if helper_spec is None or helper_spec.loader is None:
        raise ValueError("Complete-source helper cannot be loaded")
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    helper_validation = json.loads((BASE / "analysis/full-source-preflight/manifest.json").read_text("utf-8"))
    if helper_validation.get("adapter_sha256") != sha(Path(helper.__file__)):
        raise ValueError("Complete-source helper differs from its offline validated version")
    validation = helper_validation.get("validation", {})
    checked_cases = [row for row in helper_validation.get("cases", []) if row.get("case_id") == args.case]
    if (validation.get("failures") != 0 or validation.get("errors") != 0 or validation.get("tests", 0) <= 0
            or len(checked_cases) != 1 or checked_cases[0].get("complete_body_in_final_prompt") is not True
            or checked_cases[0].get("file_count") != len(case["files"])):
        raise ValueError("Complete-source helper has no passing offline coverage receipt for this case")
    helper.verify_input(BASE / case["path"], args.case)
    provider = importlib.import_module("semia_cli.llm_providers")
    core = importlib.import_module("semia_cli.core_adapter")
    cli = importlib.import_module("semia_cli.main")
    recommendation = importlib.import_module("semia_cli.recommendation")
    verify_imported_upstream(expected)
    runtime = {"variant": VARIANT, "case_id": args.case, "source_commit": COMMIT,
               "model": MODEL, "reasoning_effort": "high", "model_provider": "openai", "detector": "builtin",
               "synthesis_iterations": 5, "structural_retries_per_iteration": 3,
               "provider_error_retries": 2, "provider_retry_scope": "all LlmSynthesisError except configuration errors",
               "recommendation_enabled": True, "cgrs_max_native_starts": 60,
               "recommendation_max_native_starts": 3, "max_native_starts": 63,
               "request_timeout_seconds": 2700, "cli_executable": str(executable), "cli_sha256": sha(executable),
               "source_manifest_sha256": sha(BASE / "source-manifest.json"),
               "input_manifest_sha256": sha(BASE / "input-manifest.json"),
               "adapter_sha256": sha(Path(__file__)), "full_source_helper_sha256": sha(Path(helper.__file__)),
               "source_file_count": len(expected), "input_files": len(case["files"]),
               "accuracy_evaluated": False, "equal_budget_claim": False}
    if not args.run:
        print(json.dumps(runtime, ensure_ascii=False, indent=2))
        return 0
    verify_closeout()
    run = BASE / "comparison" / args.case
    run.mkdir(parents=True, exist_ok=False)
    runtime.update(started_at_utc=utc(), controller_pid=os.getpid(),
                   first_analysis_closeout_sha256=sha(BASE / "analysis/001-closeout.json"),
                   first_pipeline_exit_code=json.loads((BASE / "pilot/001/finished.json").read_text("utf-8"))["exit_code"])
    save(run / "runtime.json", runtime)
    os.chdir(run)
    for key in list(os.environ):
        if key.startswith("SEMIA_"):
            del os.environ[key]
    os.environ.update({"SEMIA_DETECTOR_BACKEND": "builtin", "SEMIA_LLM_PROVIDER": "codex",
                       "SEMIA_LLM_MODEL": MODEL, "SEMIA_LLM_TIMEOUT": "2700",
                       "SEMIA_SYNTHESIS_N_ITERATIONS": "5", "SEMIA_SYNTHESIS_MAX_RETRIES": "3",
                       "SEMIA_LLM_MAX_RETRIES": "2", "PYTHONUTF8": "1"})
    transport = Transport(run, str(executable), provider)
    provider._run_codex = transport
    core.prepare = helper.make_complete_source_preparer(args.case)
    original_check, original_recommend = core.check, recommendation.recommend
    checks = 0

    def check_with_receipt(*check_args, **check_kwargs):
        nonlocal checks
        checks += 1
        output = run / "validations" / f"check-{checks:03d}"
        output.mkdir(parents=True)
        facts_path = Path(check_kwargs.get("facts_path") or (check_args[1] if len(check_args) > 1 else run / "artifacts/synthesized_facts.dl"))
        invocation = {"started_at_utc": utc(), "facts_path": str(facts_path), "returned": False, "error": None}
        if facts_path.is_file():
            shutil.copyfile(facts_path, output / "submitted-facts.dl")
            invocation["submitted_facts_sha256"] = sha(output / "submitted-facts.dl")
        try:
            result = original_check(*check_args, **check_kwargs)
            save(output / "return-payload.json", result)
            invocation["returned"] = True
            return result
        except Exception as exc:
            invocation["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            for name in ("synthesis_check.json", "synthesis_evidence_alignment.json", "synthesized_facts.dl"):
                source = run / "artifacts" / name
                if source.is_file():
                    shutil.copyfile(source, output / name)
            invocation["snapshot_note"] = "Shared artifacts at return; if check raised, these may predate this invocation. Submitted facts are independently preserved."
            save(output / "invocation.json", invocation)

    def recommendation_with_phase(*rec_args, **rec_kwargs):
        transport.phase = "recommendation"
        try:
            return original_recommend(*rec_args, **rec_kwargs)
        finally:
            transport.phase = "cgrs"

    core.check, recommendation.recommend = check_with_receipt, recommendation_with_phase
    start, exit_code, error = time.monotonic(), 1, None
    try:
        with (run / "console-stdout.txt").open("w", encoding="utf-8", buffering=1) as stdout, \
             (run / "console-stderr.txt").open("w", encoding="utf-8", buffering=1) as stderr, \
             redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = cli.main(["scan", str(BASE / case["path"]), "--out", str(run / "artifacts"),
                                  "--provider", "codex", "--model", MODEL])
        return exit_code
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        integrity_error = None
        try:
            verify_sources()
            verify_inputs(args.case)
        except Exception as exc:
            integrity_error = f"{type(exc).__name__}: {exc}"
        save(run / "finished.json", {"exit_code": exit_code, "error": error,
             "elapsed_seconds": round(time.monotonic()-start, 3), "finished_at_utc": utc(),
             "native_starts": sum(c["native_start"] for c in transport.calls),
             "cgrs_native_starts": sum(c["native_start"] and c["phase"] == "cgrs" for c in transport.calls),
             "recommendation_native_starts": sum(c["native_start"] and c["phase"] == "recommendation" for c in transport.calls),
             "calls_with_visible_usage": sum(c["usage"] is not None for c in transport.calls),
             "source_and_input_unchanged": integrity_error is None, "integrity_error": integrity_error,
             "validation_receipts": checks, "accuracy_evaluated": False,
             "unexpected_tool_events": sum(len(c.get("unexpected_tool_events", [])) for c in transport.calls),
             "recommendation_completed": (run / "artifacts/recommendation.md").exists(),
             "note": "CLI may catch synthesis errors; inspect console-stderr and exit_code. Recommendation failure is nonfatal upstream."})


if __name__ == "__main__":
    raise SystemExit(main())
