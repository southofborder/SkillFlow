"""Isolated Semia transport adaptation. No online work without --run.

Semia prompts, validation, candidate selection and detector are unchanged.
Only Codex process configuration and public request accounting are replaced.
This is an engineering pilot, not a paper reproduction or scored comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
MODEL = "gpt-6.1-sol"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
            "-c", 'web_search="disabled"',
            "--output-last-message", str(directory / "response.txt"), "-"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["001", "010", "013", "ga4"], default="001")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    executable = shutil.which("codex.exe") or shutil.which("codex")
    if not executable:
        raise RuntimeError("Codex executable missing")
    source = HERE / "source"
    input_manifest = json.loads((HERE / "input-manifest.json").read_text("utf-8"))
    selected = next(x for x in input_manifest["cases"] if x["case_id"] == args.case)
    for item in selected["files"]:
        if digest(HERE / selected["path"] / item["path"]) != item["sha256"]:
            raise RuntimeError("Input integrity mismatch")
    sys.path[:0] = [str(source / f"packages/{p}/src") for p in ("semia-core", "semia-cli")]
    import semia_cli.llm_providers as provider
    from semia_cli.main import main as semia_main

    runtime = {
        "variant": "semia-379bc25f-controlled-codex-transport-v1",
        "model": MODEL, "reasoning_effort": "high", "model_provider": "openai",
        "detector": "builtin", "case_id": args.case,
        "synthesis_iterations": 5, "structural_retries_per_iteration": 3,
        "transient_provider_retries": 2, "request_timeout_seconds": 2700,
        "max_native_starts": 60,
        "comparison": "same_model_same_source_engineering_pilot_not_equal_budget_claim",
        "cli_executable": executable, "cli_sha256": digest(Path(executable)),
        "adapter_sha256": digest(Path(__file__)),
        "source_file_hashes": {
            p.relative_to(source).as_posix(): digest(p)
            for p in sorted(source.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        },
        "input_manifest_sha256": digest(HERE / "input-manifest.json"),
    }
    if not args.run:
        print(json.dumps({k: v for k, v in runtime.items() if k != "source_file_hashes"}, indent=2))
        return 0

    # Refuse accidental resumption or overwriting a previous attempt.
    run = HERE / "pilot" / args.case
    run.mkdir(parents=True, exist_ok=False)
    runtime["started_at_utc"] = datetime.now(timezone.utc).isoformat()
    save(run / "runtime.json", runtime)
    os.chdir(run)
    # Deliberately set upstream defaults instead of inheriting unrelated SEMIA settings.
    for key in list(os.environ):
        if key.startswith("SEMIA_"):
            del os.environ[key]
    os.environ.update({
        "SEMIA_DETECTOR_BACKEND": "builtin", "SEMIA_LLM_PROVIDER": "codex",
        "SEMIA_LLM_MODEL": MODEL, "SEMIA_LLM_TIMEOUT": "2700",
        "SEMIA_SYNTHESIS_N_ITERATIONS": "5", "SEMIA_SYNTHESIS_MAX_RETRIES": "3",
        "SEMIA_LLM_MAX_RETRIES": "2", "PYTHONUTF8": "1",
    })
    calls: list[dict] = []

    def controlled_codex(root: Path, prompt: str, model: str | None) -> str:
        if model != MODEL or len(calls) >= 60:
            raise provider.LlmSynthesisConfigError("Model or total call budget mismatch")
        directory = run / "transport" / f"call-{len(calls)+1:03d}"
        directory.mkdir(parents=True)
        (directory / "prompt.txt").write_bytes(prompt.encode("utf-8"))
        cmd = command(executable, directory)
        record = {"id": directory.name, "argv": cmd, "prompt_bytes": len(prompt.encode("utf-8")),
                  "started_at_utc": datetime.now(timezone.utc).isoformat(), "usage": None,
                  "native_start": False, "returncode": None}
        calls.append(record)
        save(directory / "request.json", record)
        started = time.monotonic()
        try:
            with (directory / "stdout.jsonl").open("wb") as stdout, (directory / "stderr.txt").open("wb") as stderr:
                child = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, cwd=directory)
                record.update(native_start=True, pid=child.pid)
                save(directory / "request.json", record)
                try:
                    child.communicate(input=prompt.encode("utf-8"), timeout=2700)
                except subprocess.TimeoutExpired:
                    subprocess.run(["taskkill", "/PID", str(child.pid), "/T", "/F"], capture_output=True, timeout=30)
                    child.wait(timeout=30)
                    record["timed_out"] = True
                record["returncode"] = child.returncode
            for line in (directory / "stdout.jsonl").read_text("utf-8", errors="replace").splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("type") == "turn.completed":
                    record["usage"] = event.get("usage")
            if record.get("timed_out") or record["returncode"] != 0:
                raise provider.LlmSynthesisError(f"Native request failed; see {directory}")
            if not (directory / "response.txt").exists():
                raise provider.LlmSynthesisError(f"Missing native response; see {directory}")
            return (directory / "response.txt").read_text("utf-8")
        finally:
            record["elapsed_seconds"] = round(time.monotonic() - started, 3)
            save(directory / "request.json", record)
            save(run / "calls.json", calls)

    provider._run_codex = controlled_codex
    start = time.monotonic()
    exit_code, error = 1, None
    try:
        exit_code = semia_main(["scan", str(HERE / selected["path"]), "--out", str(run / "artifacts"),
                               "--provider", "codex", "--model", MODEL])
        return exit_code
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        save(run / "finished.json", {
            "exit_code": exit_code, "error": error, "elapsed_seconds": round(time.monotonic()-start, 3),
            "native_starts": sum(c["native_start"] for c in calls),
            "calls_with_visible_usage": sum(c["usage"] is not None for c in calls),
            "accuracy_evaluated": False, "skill_executions": 0,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_unchanged": all(digest(source/p) == h for p,h in runtime["source_file_hashes"].items()),
            "input_unchanged": all(digest(HERE/selected["path"]/f["path"]) == f["sha256"] for f in selected["files"]),
        })


if __name__ == "__main__":
    raise SystemExit(main())
