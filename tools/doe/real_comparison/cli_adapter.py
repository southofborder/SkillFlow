"""Versioned fresh application-CLI transport; never a collaboration spawn.

This adapter starts no process on import. Its receipt inspector exports only
visible final output and allowlisted metadata, never raw session reasoning.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import xml.etree.ElementTree as ET

from .protocol import sha256, utc_now, write_json

SCHEMA = "skillflow-real-comparison-cli-v2"
TRANSPORT = "fresh_application_cli_exec_stdin"
EXPECTED = {"model": "gpt-6.1-sol", "effort": "ultra", "provider": "openai"}
PINNED_VERSION = "0.163.0-alpha.10.2"
PINNED_EXECUTABLE_SHA256 = "f6dbf48cb70f62649c645f26c87dc9bf84cc36986202dfad8e12fb5b8ca70312"
PINNED_BASE_INSTRUCTIONS_SHA256 = "e1bdd4f8f0df4b20f4a0ffc8a861ce819df45325d8cecdfb92e80379cf8d142e"
PINNED_DEVELOPER_SEGMENTS = (
    ("9fb6a9a2b72745ced78b613d15d8d5278e614dd3262f44548108e63e2f37483a",
     "4103287cd2f8e02c0c606bbbae018671bd04d7e7eeca9cbf862f8b53f9275313",
     "7f45d7d6986a761101d46d185824ce65c321ca0f02cea7497fc46d60ffae417b",
     "cc7bde87d79b0cdc7a2ca636787f652be6030b17320b87dffa22014bda59730a"),
    ("3edd51083129388f52e881435e93e4b981e00c5ee3d62ab5d32e22c428fd504b",),
    ("f7e90c3b4fe2212b77dd031adb8240c7e932abed003173f1e458cd2f66c395d8",),
)
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
                "output_tokens", "reasoning_output_tokens", "total_tokens")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_rows(path):
    rows = []
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"A CLI receipt row is not an object at line {number}")
                rows.append(row)
    return rows


def command(executable, output_dir):
    return [str(Path(executable).resolve()), "exec", "--ignore-user-config", "--ignore-rules",
            "--skip-git-repo-check", "--sandbox", "read-only", "--color", "never",
            "--json", "--model", EXPECTED["model"], "-c", 'model_reasoning_effort="ultra"',
            "-c", 'model_provider="openai"', "-c", "project_doc_max_bytes=0",
            "--output-last-message", str(Path(output_dir).resolve() / "last-message.txt"), "-"]


def prepare_launch(executable, prompt_path, output_dir, empty_workdir):
    executable, prompt = Path(executable).resolve(), Path(prompt_path).resolve()
    output, cwd = Path(output_dir).resolve(), Path(empty_workdir).resolve()
    raw = prompt.read_bytes()
    raw.decode("utf-8")
    if sha256(executable) != PINNED_EXECUTABLE_SHA256:
        raise ValueError("The CLI executable differs from the explicitly inspected executable")
    if not cwd.is_dir() or any(cwd.iterdir()):
        raise ValueError("A fresh CLI request requires its own empty working directory")
    date_start = datetime.now(timezone(timedelta(hours=8)))
    return {"schema_version": SCHEMA, "transport": TRANSPORT,
            "command": command(executable, output), "executable_sha256": sha256(executable),
            "expected_cli_version": PINNED_VERSION, "stdin_file": str(prompt),
            "stdin_sha256": sha256(prompt), "stdin_bytes": len(raw),
            "output_dir": str(output), "empty_workdir": str(cwd),
            "runtime_expectation": EXPECTED, "configuration_is_verified": False,
            "base_instructions_sha256": PINNED_BASE_INSTRUCTIONS_SHA256,
            "developer_segment_sha256": [list(row) for row in PINNED_DEVELOPER_SEGMENTS],
            "allowed_environment_dates": sorted({date_start.date().isoformat(),
                (date_start + timedelta(seconds=2700)).date().isoformat()})}


def execute_launch(prepared, *, timeout_seconds=2700, popen=None):
    """Start exactly one process and preserve every wait; no retry or replacement.

    The caller must authorize this exact request first. Individual supervision
    waits are at most 30 seconds. A process exit alone never verifies a response.
    """
    output, cwd = Path(prepared["output_dir"]), Path(prepared["empty_workdir"])
    if timeout_seconds <= 0 or timeout_seconds > 2700:
        raise ValueError("The actual CLI process timeout must be positive and at most 45 minutes")
    if output.exists():
        raise ValueError("A CLI request output directory cannot be reused")
    prompt = Path(prepared["stdin_file"])
    if (prepared["executable_sha256"] != PINNED_EXECUTABLE_SHA256
            or sha256(prompt) != prepared["stdin_sha256"]
            or sha256(prepared["command"][0]) != prepared["executable_sha256"]
            or prepared["command"] != command(prepared["command"][0], output)
            or any(cwd.iterdir())):
        raise ValueError("The pinned executable, command, stdin or empty working directory changed")
    output.mkdir(parents=True)
    launch = {**prepared, "started_at": utc_now()}
    write_json(output / "launch.json", launch, immutable=True)
    start, waits, status, process = time.perf_counter(), [], "launch_failed", None
    error = None
    with (output / "stdout.jsonl").open("wb") as stdout, (output / "stderr.txt").open("wb") as stderr:
        try:
            process = (popen or subprocess.Popen)(prepared["command"], cwd=cwd,
                stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
            write_json(output / "process-start.json", {"pid": process.pid, "started_at": utc_now(),
                       "actual_cli_process_started": True}, immutable=True)
            first = True
            while True:
                remaining = timeout_seconds - (time.perf_counter() - start)
                if remaining <= 0:
                    status = "timeout"
                    process.kill()
                    process.communicate(timeout=30)
                    break
                before = time.perf_counter()
                try:
                    process.communicate(input=prompt.read_bytes() if first else None,
                                        timeout=min(30, remaining))
                    waits.append({"wait_seconds": time.perf_counter() - before, "result": "process_exited"})
                    status = "process_exited"
                    break
                except subprocess.TimeoutExpired:
                    waits.append({"wait_seconds": time.perf_counter() - before, "result": "still_running"})
                finally:
                    first = False
        except BaseException as caught:
            error = f"{type(caught).__name__}: {caught}"
            if process is not None and process.poll() is None:
                process.kill()
                process.communicate(timeout=30)
            status = "process_error" if process is not None else "launch_failed"
    result = {"schema_version": SCHEMA, "status": status, "returncode": process.returncode if process else None,
              "error": error, "finished_at": utc_now(), "supervisor_waits": waits,
              "supervisor_elapsed_seconds": time.perf_counter() - start,
              "actual_cli_process_started": process is not None, "retries": 0,
              "launch_sha256": sha256(output / "launch.json")}
    write_json(output / "process-result.json", result, immutable=True)
    return result


def session_from_stdout(path):
    ids = [r.get("thread_id") for r in read_rows(path) if r.get("type") == "thread.started"]
    if len(ids) != 1 or not isinstance(ids[0], str) or not ids[0]:
        raise ValueError("CLI stdout must identify exactly one fresh exec session")
    return ids[0]


def _text_parts(payload, kind):
    parts = payload.get("content", [])
    if not isinstance(parts, list) or any(p.get("type") != kind or not isinstance(p.get("text"), str) for p in parts):
        raise ValueError("A visible CLI input has unsupported or encrypted content")
    return [p["text"] for p in parts]


def _environment(text, cwd, allowed_dates):
    """Only the observed standard CLI environment envelope is admissible."""
    try:
        date = ET.fromstring(text).findtext("current_date")
        datetime.strptime(date, "%Y-%m-%d")
    except (ET.ParseError, TypeError, ValueError):
        return False
    expected = ("<environment_context>\n  <cwd>" + str(cwd) + "</cwd>\n  <shell>powershell</shell>\n"
        "  <current_date>" + date + "</current_date>\n  <timezone>Asia/Shanghai</timezone>\n"
        "  <filesystem><workspace_roots><root>" + str(cwd) + "</root></workspace_roots>"
        '<permission_profile type="managed"><file_system type="restricted"><entry access="read">'
        "<special>:root</special></entry></file_system></permission_profile></filesystem>\n</environment_context>")
    return date in allowed_dates and text == expected


def inspect_receipt(path, session_id, prepared, *, stdout_path=None, last_message_path=None):
    """Verify actual fresh exec identity, full visible inputs, activity and usage.

    Legacy parsing supplies attribution, visible final extraction and per-response
    counters. The additional inspection covers the entire session, including
    runtime envelopes and inputs before the turn_context record.
    """
    from tools.doe.direct_baseline import parse_receipt
    rows = read_rows(path)
    answer, legacy = parse_receipt(path, session_id, expected_model=EXPECTED["model"], expected_effort=EXPECTED["effort"])
    violations = list(legacy["violations"])
    metas = [r["payload"] for r in rows if r.get("type") == "session_meta"]
    meta = metas[0] if len(metas) == 1 else {}
    if len(metas) != 1:
        violations.append("Exactly one primary CLI session metadata record is required")
    for key, wanted in (("id", session_id), ("session_id", session_id), ("source", "exec"), ("originator", "codex_exec"),
                        ("cli_version", prepared["expected_cli_version"]), ("model_provider", EXPECTED["provider"])):
        if meta.get(key) != wanted:
            violations.append("The actual CLI session metadata differs: " + key)
    for key in ("forked_from_id", "parent_thread_id", "parent_session_id"):
        if meta.get(key) is not None:
            violations.append("The CLI session declares inherited or parent history: " + key)
    if meta.get("cwd") != prepared["empty_workdir"]:
        violations.append("The CLI receipt working directory differs from the empty launch directory")
    if digest((meta.get("base_instructions") or {}).get("text", "")) != prepared["base_instructions_sha256"]:
        violations.append("The CLI base instructions differ from the inspected common harness")
    users, developers, tools, final_ids, prompt_index = [], [], [], [], None
    starts, completes, contexts_all, final_events, user_events = [], [], [], [], []
    for index, row in enumerate(rows):
        kind, payload = row.get("type"), row.get("payload", {})
        item_type = payload.get("type", "")
        if kind == "response_item":
            if item_type == "message" and payload.get("role") in {"user", "developer", "system"}:
                try:
                    parts = _text_parts(payload, "input_text")
                except ValueError as error:
                    violations.append(str(error))
                    parts = []
                if payload.get("role") == "developer":
                    developers.append([digest(p) for p in parts])
                elif payload.get("role") == "system":
                    violations.append("An additional system message was present in the CLI transcript")
                else:
                    text = "".join(parts)
                    environment = _environment(text, prepared["empty_workdir"], prepared["allowed_environment_dates"])
                    users.append({"sha256": digest(text), "bytes": len(text.encode("utf-8")),
                                  "is_environment_context": environment})
                    if digest(text) == prepared["stdin_sha256"]:
                        prompt_index = index
            elif item_type == "message" and payload.get("role") == "assistant":
                if prompt_index is None:
                    violations.append("Assistant output preceded the one fresh task message")
                if payload.get("phase") == "final_answer":
                    final_ids.append(payload.get("id"))
                    if payload.get("status") != "completed":
                        violations.append("The final assistant receipt item is not terminal and completed")
            elif item_type not in {"reasoning", "message"}:
                tools.append({"id": payload.get("id") or payload.get("call_id"),
                              "name": payload.get("name") or item_type, "kind": item_type})
        if kind in {"compacted", "context_compacted"}:
            violations.append("The session contains a history compaction record")
        if kind == "event_msg" and item_type in {"task_started", "task_complete"}:
            (starts if item_type == "task_started" else completes).append(payload)
        if kind == "turn_context":
            contexts_all.append(payload)
        if kind == "event_msg" and item_type == "item_completed":
            item = payload.get("item", {})
            if item.get("type") == "AgentMessage" and item.get("phase") == "final_answer":
                final_events.append(payload)
            elif item.get("type") == "UserMessage":
                user_events.append(payload)
            elif item.get("type") not in {"AgentMessage", "Reasoning"}:
                violations.append("A prohibited or unsupported attributed activity item is present")
        if kind == "token_usage_record":
            expected_ids = {"thread_id": session_id, "session_id": session_id,
                            "turn_id": legacy["turn_id"], "root_turn_id": legacy["turn_id"]}
            if any(payload.get(key) != wanted for key, wanted in expected_ids.items()):
                violations.append("A per-response usage record has inconsistent exact session, thread, turn or root attribution")
    if developers != prepared["developer_segment_sha256"]:
        violations.append("Runtime developer instructions differ from the pinned common CLI harness")
    if (len(users) != 2 or not users[0]["is_environment_context"] or users[1]["is_environment_context"]
            or users[1]["sha256"] != prepared["stdin_sha256"] or users[1]["bytes"] != prepared["stdin_bytes"]):
        violations.append("The complete visible CLI input is not exactly one ordinary environment and the exact full stdin task")
    if tools:
        violations.append("Forbidden tool use, retrieval or delegation was present anywhere in the CLI session")
    if len(starts) != 1 or len(completes) != 1:
        violations.append("The fresh CLI session must contain exactly one started and completed turn")
    if len(contexts_all) != 1:
        violations.append("The fresh CLI session must contain exactly one runtime turn context")
    for context in contexts_all:
        if (context.get("turn_id") != legacy["turn_id"] or context.get("root_turn_id") != legacy["turn_id"]
                or context.get("cwd") != prepared["empty_workdir"] or context.get("approval_policy") != "never"
                or context.get("sandbox_policy", {}).get("type") != "read-only"):
            violations.append("The actual runtime turn context differs from the approved launch or turn")
    for item in starts + completes:
        if item.get("turn_id") != legacy["turn_id"] or item.get("root_turn_id") != legacy["turn_id"]:
            violations.append("The actual CLI turn identity is inconsistent")
        if item.get("parent_turn_id") is not None or item.get("initiating_agent_path") is not None:
            violations.append("The CLI turn declares a parent or initiating agent")
    for item in starts:
        attribution = item.get("turn_attribution") or {}
        if (attribution.get("turn_id") != legacy["turn_id"] or attribution.get("root_turn_id") != legacy["turn_id"]
                or attribution.get("turn_trigger") != "exec" or attribution.get("parent_turn_id") is not None
                or attribution.get("initiating_agent_path") is not None):
            violations.append("The CLI turn lacks fresh exec attribution or declares inherited agent history")
    if len(final_events) != 1 or len(final_ids) != 1:
        violations.append("The visible final answer lacks exactly one attributed completion event")
    else:
        event, item = final_events[0], final_events[0]["item"]
        text = "".join(c.get("text", "") for c in item.get("content", []) if c.get("type") in {"Text", "text", "output_text"})
        if (event.get("thread_id") != session_id or event.get("turn_id") != legacy["turn_id"]
                or item.get("id") != final_ids[0] or text != answer):
            violations.append("The visible final answer conflicts with its exact-thread/turn completion event")
    if len(user_events) != 1:
        violations.append("The fresh task lacks exactly one attributed user-message completion")
    else:
        event = user_events[0]
        text = "".join(c.get("text", "") for c in event["item"].get("content", []) if c.get("type") in {"Text", "text", "input_text"})
        if (event.get("thread_id") != session_id or event.get("turn_id") != legacy["turn_id"]
                or digest(text) != prepared["stdin_sha256"]):
            violations.append("The task user-message completion differs from the exact stdin or turn")
    contexts = legacy["observed_configuration"]
    provider_verified = bool(contexts) and all(c.get("model_provider") == EXPECTED["provider"] for c in contexts)
    if not legacy["configuration_verified"] or not provider_verified:
        violations.append("The actual model, literal ultra effort or openai provider was not verified")
    usage = legacy["usage"]
    usage_known = bool(usage["by_response_id"]) and all(
        type(row.get(key)) is int and row[key] >= 0 for row in usage["by_response_id"].values() for key in TOKEN_FIELDS)
    if not usage_known or legacy["diagnostics"]:
        violations.append("Unknown or inconsistent per-response usage forbids further dispatch")
    if len(final_ids) != 1 or not final_ids[0]:
        violations.append("The visible final answer lacks one exact receipt item identity")
    if stdout_path is not None:
        stdout_rows = read_rows(stdout_path)
        if session_from_stdout(stdout_path) != session_id:
            violations.append("The stdout session differs from the actual receipt")
        messages = [r.get("item", {}).get("text") for r in stdout_rows if r.get("type") == "item.completed"
                    and r.get("item", {}).get("type") == "agent_message"]
        if messages != [answer]:
            violations.append("CLI stdout does not contain exactly the receipt's complete visible final answer")
        for row in stdout_rows:
            item = row.get("item", {})
            if item and item.get("type") not in {"agent_message", "reasoning"}:
                violations.append("CLI stdout contains a prohibited or unsupported tool/delegation item")
    if last_message_path is not None and (answer is None or Path(last_message_path).read_bytes() != answer.encode("utf-8")):
        violations.append("The CLI last-message file differs from the complete visible receipt answer")
    violations = list(dict.fromkeys(violations))
    record = {k: v for k, v in legacy.items() if k not in {"agent_session_id", "agent_path", "parent_thread_id", "prompt_delivery_audit"}}
    record.update(schema_version=SCHEMA, transport=TRANSPORT, cli_session_id=session_id,
        actual_cli_version=meta.get("cli_version"), actual_session_source=meta.get("source"),
        actual_originator=meta.get("originator"), provider_verified=provider_verified,
        protocol_status="violated" if violations else "conformant", violations=violations,
        usage_verified=usage_known, final_item_ids=final_ids,
        tools=legacy["tools"] + tools, runtime_developer_segment_sha256=developers,
        base_instructions_sha256=digest((meta.get("base_instructions") or {}).get("text", "")),
        prompt_delivery_audit={"status": "matches" if len(users) == 2 and users[0]["is_environment_context"]
            and users[1]["sha256"] == prepared["stdin_sha256"] else "mismatch",
            "planned_sha256": prepared["stdin_sha256"], "visible_user_messages": users,
            "additional_context": "Pinned common CLI harness and one ordinary environment context; observational isolation, not a hard tool sandbox."})
    return answer, record
