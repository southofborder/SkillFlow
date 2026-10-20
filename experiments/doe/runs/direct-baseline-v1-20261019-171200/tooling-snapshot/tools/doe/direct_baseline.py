"""Source-only direct-model experiment records, with no model or network calls.

Only explicitly selected source bytes and the optional user request enter prompts.
Receipt imports export visible answers and an allowlist of execution metadata;
reasoning items, tool arguments, cumulative usage and account data are discarded.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable


IDENTITY = "skillflow-direct-baseline-v1"
DEFAULT_SESSIONS = Path("C:/Users/24831/.codex/sessions")
EXPECTED_MODEL = "gpt-6.1-sol"
EXPECTED_EFFORT = "ultra"
TOKEN_FIELDS = (
    "input_tokens", "cached_input_tokens", "cache_write_input_tokens",
    "output_tokens", "reasoning_output_tokens", "total_tokens",
)
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
_TOOL_ITEMS = {
    "CommandExecution", "McpToolCall", "CustomToolCall", "FunctionCall",
    "DynamicToolCall", "WebSearch", "ImageGeneration", "CollabAgentSpawn",
    "CollabAgentInteraction", "FileChange", "ToolCall", "BrowserToolCall",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def _name(value: str) -> str:
    if not _NAME.fullmatch(value) or value in {".", ".."}:
        raise ValueError("Record identifiers must contain only letters, digits, dots, dashes or underscores")
    return value


def _relative(value: str) -> str:
    rel = PurePosixPath(value.replace("\\", "/"))
    if rel.is_absolute() or ":" in str(rel) or any(p in {"", ".", ".."} for p in rel.parts):
        raise ValueError("Source paths must be safe relative paths")
    return str(rel)


def _inside(root: Path, relative: str) -> Path:
    path = root.joinpath(*PurePosixPath(_relative(relative)).parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Source path escapes its package")
    return path


def render_source_bundle(source_dir: Path | str, source_files: Iterable[str]) -> str:
    """Render only the selected UTF-8 sources with physical-line references."""
    root = Path(source_dir)
    paths = sorted({_relative(s) for s in source_files})
    if not paths:
        raise ValueError("At least one explicit source file is required")
    blocks = []
    for relative in paths:
        text = _inside(root, relative).read_bytes().decode("utf-8")
        # splitlines preserves blank physical lines without inventing a final line.
        numbered = "\n".join(f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1))
        blocks.append(f"FILE {relative}\n{numbered}")
    return "\n\n".join(blocks) + "\n"


def package_bundle(
    source_dir: Path | str, run_dir: Path | str, case_id: str, *,
    source_files: Iterable[str], user_request: str | None = None,
) -> dict:
    """Freeze selected file bytes; never discover analysis files or overwrite."""
    source = Path(source_dir)
    paths = sorted({_relative(s) for s in source_files})
    if not paths:
        raise ValueError("At least one explicit source file is required")
    blobs = [(rel, _inside(source, rel).read_bytes()) for rel in paths]
    for _, data in blobs:
        data.decode("utf-8")
    target = Path(run_dir) / "cases" / _name(case_id)
    if target.exists():
        raise FileExistsError(f"Case already exists: {target}")
    entries = []
    for relative, data in blobs:
        _write_new(_inside(target / "inputs", relative), data)
        entries.append({"path": relative, "sha256": sha256(data), "bytes": len(data)})
    bundle = render_source_bundle(target / "inputs", paths).encode("utf-8")
    _write_new(target / "source_bundle.txt", bundle)
    request_bytes = user_request.encode("utf-8") if user_request is not None else None
    if request_bytes is not None:
        _write_new(target / "user_request.txt", request_bytes)
    manifest = {
        "schema": IDENTITY, "case_id": case_id, "sources": entries,
        "source_bundle_sha256": sha256(bundle),
        "user_request_sha256": sha256(request_bytes) if request_bytes is not None else None,
        "source_selection": "Explicit caller-selected source files only; no recursive analysis discovery.",
    }
    _write_new(target / "manifest.json", _json_bytes(manifest))
    return manifest


def render_prompt(
    template_path: Path | str, source_bundle: str, user_request: str | None = None, *,
    shared_rules: str = "", original_answer: str | None = None,
    arm_instruction: str | None = None,
) -> str:
    """Replace known template tokens once, without interpreting source braces."""
    template = Path(template_path).read_bytes().decode("utf-8")
    values = {
        "shared_rules": shared_rules, "source_bundle": source_bundle,
        "user_request": user_request if user_request is not None else "No independent user request was supplied.",
        "original_answer": original_answer, "arm_instruction": arm_instruction,
    }
    # Split on original template tokens: inserted source/user text is never processed.
    token = re.compile(r"\{(shared_rules|source_bundle|user_request|original_answer|arm_instruction)\}")
    def replace(match: re.Match) -> str:
        value = values[match.group(1)]
        if value is None:
            raise ValueError(f"Missing required prompt input: {match.group(1)}")
        return value
    return token.sub(replace, template)


def prepare_trial(
    run_dir: Path | str, trial_id: str, case_id: str, template_path: Path | str, *,
    shared_path: Path | str | None = None,
    original_answer_path: Path | str | None = None, arm_instruction: str | None = None,
    metadata: dict | None = None,
) -> dict:
    root = Path(run_dir)
    case = root / "cases" / _name(case_id)
    manifest = _read_json(case / "manifest.json")
    bundle = (case / "source_bundle.txt").read_bytes().decode("utf-8")
    request_path = case / "user_request.txt"
    request = request_path.read_bytes().decode("utf-8") if request_path.exists() else None
    shared = Path(shared_path).read_bytes().decode("utf-8") if shared_path else ""
    original = Path(original_answer_path).read_bytes().decode("utf-8") if original_answer_path else None
    prompt = render_prompt(template_path, bundle, request, shared_rules=shared,
                           original_answer=original, arm_instruction=arm_instruction)
    target = root / "trials" / _name(trial_id)
    if target.exists():
        raise FileExistsError(f"Trial already exists: {target}")
    _write_new(target / "template.txt", Path(template_path).read_bytes())
    _write_new(target / "shared.txt", shared.encode("utf-8"))
    if original is not None:
        _write_new(target / "original_answer.txt", original.encode("utf-8"))
    _write_new(target / "prompt.txt", prompt.encode("utf-8"))
    record = {
        "schema": IDENTITY, "trial_id": trial_id, "case_id": case_id,
        "case_manifest_sha256": sha256(_json_bytes(manifest)),
        "prompt_sha256": sha256(prompt.encode("utf-8")),
        "template_sha256": sha256(Path(template_path).read_bytes()),
        "shared_sha256": sha256(shared.encode("utf-8")),
        "original_answer_sha256": sha256(original.encode("utf-8")) if original is not None else None,
        "arm_instruction": arm_instruction,
        "expected_model": EXPECTED_MODEL, "expected_effort": EXPECTED_EFFORT,
        "agent_session_id": None, "turn_id": None, "metadata": metadata or {},
    }
    _write_new(target / "registration.json", _json_bytes(record))
    return record


def _rows(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid receipt JSON at line {number}") from error
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _primary_meta(rows: list[dict]) -> dict:
    return next((r.get("payload", {}) for r in rows if r.get("type") == "session_meta"), {})


def find_receipt(agent_session_id: str, sessions_dir: Path | str = DEFAULT_SESSIONS) -> Path:
    """Match primary session identity; filenames alone are not authoritative."""
    candidates = []
    for path in Path(sessions_dir).rglob(f"*{_name(agent_session_id)}*.jsonl"):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row.get("type") == "session_meta":
                    if row.get("payload", {}).get("id") == agent_session_id:
                        candidates.append(path)
                    break
    if len(candidates) != 1:
        raise ValueError(f"Expected one receipt for exact child session; found {len(candidates)}")
    return candidates[0]


def resolve_agent_session(
    agent_name: str, sessions_dir: Path | str = DEFAULT_SESSIONS, *,
    root_session_id: str | None = None,
) -> str:
    """Resolve an exact canonical agent path from primary metadata only."""
    matches = []
    for path in Path(sessions_dir).rglob("*.jsonl"):
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row.get("type") != "session_meta":
                    continue
                meta = row.get("payload", {})
                source = meta.get("source")
                spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
                agent_path = meta.get("agent_path") or spawn.get("agent_path")
                if agent_path == agent_name and (root_session_id is None or meta.get("session_id") == root_session_id):
                    matches.append(meta["id"])
                break
    unique = set(matches)
    if len(unique) != 1:
        raise ValueError(f"Expected one exact agent path in the selected session scope; found {len(unique)}")
    return next(iter(unique))


def _exact_child_turns(rows: list[dict], child_id: str) -> set[str]:
    turns = set()
    for row in rows:
        pl = row.get("payload", {})
        if row.get("type") == "token_usage_record" or (
            row.get("type") == "event_msg" and pl.get("type") == "item_completed"
        ):
            if pl.get("thread_id") == child_id and isinstance(pl.get("turn_id"), str):
                turns.add(pl["turn_id"])
    return turns


def parse_receipt(
    path: Path | str, agent_session_id: str, turn_id: str | None = None, *,
    expected_model: str = EXPECTED_MODEL, expected_effort: str = EXPECTED_EFFORT,
    expected_prompt_sha256: str | None = None,
) -> tuple[str | None, dict]:
    """Extract an exact child turn without exporting reasoning or raw rollouts."""
    path = Path(path)
    rows = _rows(path)
    meta = _primary_meta(rows)
    if meta.get("id") != agent_session_id:
        raise ValueError("Receipt primary session does not match the requested child session")
    turns = _exact_child_turns(rows, agent_session_id)
    if turn_id is None:
        if len(turns) != 1:
            raise ValueError(f"Exact child has {len(turns)} proven turns; supply turn_id")
        turn_id = next(iter(turns))
    elif turn_id not in turns:
        raise ValueError("Requested turn lacks exact child thread attribution")

    contexts, final_items, tool_items, usage_by_id = [], {}, {}, {}
    incoming_messages = []
    active_turn = None
    timing = {}
    issues = []
    for index, row in enumerate(rows):
        kind, pl = row.get("type"), row.get("payload", {})
        event_type = pl.get("type")
        if kind == "turn_context":
            active_turn = pl.get("turn_id")
            if active_turn == turn_id:
                context = {k: pl.get(k) for k in ("model", "effort", "model_provider")}
                context["effort"] = context["effort"] or pl.get("reasoning_effort")
                context["model_provider"] = context["model_provider"] or meta.get("model_provider")
                if context not in contexts:
                    contexts.append(context)
        if kind == "event_msg" and event_type == "task_started":
            active_turn = pl.get("turn_id")
            if active_turn == turn_id:
                timing["started_at"] = pl.get("started_at")
        if kind == "event_msg" and event_type == "task_complete" and pl.get("turn_id") == turn_id:
            timing.update({k: pl.get(k) for k in (
                "started_at", "completed_at", "duration_ms", "time_to_first_token_ms",
            )})
        if kind == "token_usage_record" and pl.get("thread_id") == agent_session_id and pl.get("turn_id") == turn_id:
            response_id = pl.get("response_id")
            if not response_id:
                issues.append("A per-response usage receipt lacks response_id; it was not counted.")
                continue
            raw = pl.get("usage") or {}
            usage = {k: raw.get(k) if isinstance(raw.get(k), int) and not isinstance(raw.get(k), bool) else None for k in TOKEN_FIELDS}
            if response_id in usage_by_id and usage_by_id[response_id] != usage:
                issues.append(f"Conflicting usage receipts for response {response_id}.")
            else:
                usage_by_id[response_id] = usage
        if kind == "response_item" and active_turn == turn_id:
            item_id = pl.get("id") or pl.get("call_id") or f"row-{index}"
            if event_type == "message" and pl.get("role") == "assistant" and pl.get("phase") == "final_answer":
                contents = pl.get("content", [])
                text = "".join(c.get("text", "") for c in contents if c.get("type") == "output_text")
                final_items[item_id] = text
            if event_type in {"function_call", "custom_tool_call", "web_search_call", "computer_call", "image_generation_call", "local_shell_call"}:
                tool_items[item_id] = {"id": item_id, "name": pl.get("name") or event_type, "kind": event_type}
            if event_type == "agent_message":
                contents = pl.get("content", [])
                encrypted = any(c.get("type") == "encrypted_content" for c in contents)
                visible = "".join(c.get("text", "") for c in contents if c.get("type") in {"input_text", "output_text"})
                payload = visible.split("\nPayload:\n", 1)[1] if "\nPayload:\n" in visible else None
                incoming_messages.append({"encrypted": encrypted, "payload_sha256": sha256(payload.encode("utf-8")) if payload is not None and not encrypted else None})
        if kind == "event_msg" and event_type == "item_completed" and pl.get("thread_id") == agent_session_id and pl.get("turn_id") == turn_id:
            item = pl.get("item", {})
            item_type = item.get("type", "")
            if item_type in _TOOL_ITEMS:
                item_id = item.get("id") or item.get("call_id") or f"row-{index}"
                # Prefer the response-item name when both records share an ID.
                tool_items.setdefault(item_id, {"id": item_id, "name": item.get("name") or item_type, "kind": item_type})

    violations = []
    if meta.get("forked_from_id") is not None:
        violations.append("The child session inherited a prior transcript rather than starting without turn history.")
    if tool_items:
        violations.append("Forbidden tool use or delegation was observed.")
    if len(turns) > 1:
        violations.append("The child session contains additional attributed turns.")
    if any(c.get("model") is not None and c["model"] != expected_model for c in contexts):
        violations.append("Observed model differs from the registered expected model.")
    if any(c.get("effort") is not None and c["effort"] != expected_effort for c in contexts):
        violations.append("Observed reasoning effort differs from the registered expected effort.")
    if len(final_items) > 1:
        violations.append("Multiple final-answer messages were observed; none was selected as the answer.")
    if any(s.startswith("Conflicting usage") for s in issues):
        violations.append("Per-response usage receipts conflict.")
    if len(incoming_messages) > 1:
        violations.append("Additional incoming agent messages were observed during the target turn.")
    delivered_hash = incoming_messages[0]["payload_sha256"] if len(incoming_messages) == 1 else None
    delivery_audit = "unavailable_encrypted" if any(m["encrypted"] for m in incoming_messages) else "unavailable"
    if expected_prompt_sha256 is not None and delivered_hash is not None:
        delivery_audit = "matches" if delivered_hash == expected_prompt_sha256 else "mismatch"
        if delivery_audit == "mismatch":
            violations.append("Visible delivered task payload differs from the registered prompt.")
    answer = next(iter(final_items.values())) if len(final_items) == 1 else None
    verified_config = bool(contexts) and all(c.get("model") == expected_model and c.get("effort") == expected_effort for c in contexts)
    complete = answer is not None and timing.get("completed_at") is not None
    status = "violated" if violations else "conformant" if verified_config and complete else "unverified"
    totals = {
        key: sum(u[key] for u in usage_by_id.values()) if usage_by_id and all(u[key] is not None for u in usage_by_id.values()) else None
        for key in TOKEN_FIELDS
    }
    source = meta.get("source")
    spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
    result = {
        "schema": IDENTITY, "agent_session_id": agent_session_id, "turn_id": turn_id,
        "agent_path": spawn.get("agent_path"), "parent_thread_id": meta.get("parent_thread_id") or spawn.get("parent_thread_id"),
        "observed_configuration": contexts, "expected_model": expected_model, "expected_effort": expected_effort,
        "protocol_status": status, "violations": violations, "diagnostics": issues,
        "configuration_verified": verified_config, "completed": complete,
        "prompt_delivery_audit": {"status": delivery_audit, "incoming_message_count": len(incoming_messages),
                                  "delivered_payload_sha256": delivered_hash},
        "timing": timing, "tools": list(tool_items.values()),
        "usage": {"by_response_id": usage_by_id, "totals": totals,
                  "response_count": len(usage_by_id), "basis": "Per-response usage only; response IDs deduplicated. Missing values remain unknown."},
        "output_sha256": sha256(answer.encode("utf-8")) if answer is not None else None,
        "receipt_sha256": sha256(path.read_bytes()),
        "limitations": ["Tools are forbidden by protocol, not disabled by a hard sandbox.",
                        "Only visible final-answer text and allowlisted metadata are exported.",
                        "No per-call monetary amount is inferred."],
    }
    return answer, result


def import_trial(
    run_dir: Path | str, trial_id: str, *, agent_session_id: str | None = None,
    turn_id: str | None = None, sessions_dir: Path | str = DEFAULT_SESSIONS,
    receipt_path: Path | str | None = None,
    agent_name: str | None = None, root_session_id: str | None = None,
) -> dict:
    target = Path(run_dir) / "trials" / _name(trial_id)
    registration = _read_json(target / "registration.json")
    child = agent_session_id or registration.get("agent_session_id")
    name = agent_name or registration.get("agent_name") or registration.get("metadata", {}).get("agent_name")
    if not child and name:
        child = resolve_agent_session(name, sessions_dir, root_session_id=root_session_id)
    if not child:
        raise ValueError("An exact child agent_session_id is required")
    selected_turn = turn_id or registration.get("turn_id")
    path = Path(receipt_path) if receipt_path else find_receipt(child, sessions_dir)
    answer, record = parse_receipt(path, child, selected_turn,
                                   expected_model=registration.get("expected_model", EXPECTED_MODEL),
                                   expected_effort=registration.get("expected_effort", EXPECTED_EFFORT),
                                   expected_prompt_sha256=registration["prompt_sha256"])
    record.update({"trial_id": trial_id, "case_id": registration["case_id"],
                   "prompt_sha256": registration["prompt_sha256"]})
    if (target / "decision.json").exists() or (target / "answer.txt").exists():
        raise FileExistsError("Imported trial records are immutable; use a new trial ID")
    if answer is not None:
        _write_new(target / "answer.txt", answer.encode("utf-8"))
    _write_new(target / "decision.json", _json_bytes(record))
    return record


def exposure_identity(exposure: dict) -> str:
    """Canonicalize an already adjudicated exposure identity, not natural language.

    Callers supply source, payload_scope, version, condition and recipient. Order
    within JSON objects does not affect identity; no model-based merging occurs.
    """
    fields = ("source", "payload_scope", "version", "condition", "recipient")
    missing = [key for key in fields if key not in exposure]
    if missing:
        raise ValueError("Exposure identity is missing: " + ", ".join(missing))
    return sha256(_json_bytes({key: exposure[key] for key in fields}))


def deduplicate_exposures(exposures: Iterable[dict]) -> list[dict]:
    unique = {}
    for exposure in exposures:
        unique.setdefault(exposure_identity(exposure), exposure)
    return list(unique.values())


def verify(run_dir: Path | str, *, sessions_dir: Path | str | None = None) -> dict:
    """Replay hashes/prompts and optionally re-import allowlisted receipt decisions."""
    root = Path(run_dir)
    errors = []
    reference_count = 0
    for seal_path in sorted(root.glob("*-reference-freeze.json")):
        try:
            for name, expected_hash in _read_json(seal_path)["files"].items():
                reference = _inside(root / "references", name)
                if not reference.is_file() or sha256(reference.read_bytes()) != expected_hash:
                    errors.append(f"Reference hash mismatch: {name}")
                reference_count += 1
        except (OSError, ValueError, KeyError) as error:
            errors.append(f"Reference freeze replay failed: {seal_path.name}: {error}")
    cases = list((root / "cases").glob("*/manifest.json"))
    for manifest_path in cases:
        case = manifest_path.parent
        manifest = _read_json(manifest_path)
        for source in manifest["sources"]:
            path = _inside(case / "inputs", source["path"])
            if not path.is_file() or sha256(path.read_bytes()) != source["sha256"]:
                errors.append(f"Source hash mismatch: {manifest['case_id']}/{source['path']}")
        request = case / "user_request.txt"
        actual_request = sha256(request.read_bytes()) if request.exists() else None
        if actual_request != manifest["user_request_sha256"]:
            errors.append(f"User-request hash mismatch: {manifest['case_id']}")
        try:
            regenerated = render_source_bundle(case / "inputs", [s["path"] for s in manifest["sources"]]).encode("utf-8")
            saved = (case / "source_bundle.txt").read_bytes()
            if regenerated != saved or sha256(saved) != manifest["source_bundle_sha256"]:
                errors.append(f"Source-bundle mismatch: {manifest['case_id']}")
        except (OSError, ValueError) as error:
            errors.append(f"Source-bundle replay failed: {manifest['case_id']}: {error}")
    registrations = list((root / "trials").glob("*/registration.json"))
    receipt_replays = 0
    for path in registrations:
        trial = path.parent
        registration = _read_json(path)
        case = root / "cases" / registration["case_id"]
        request_path = case / "user_request.txt"
        original_path = trial / "original_answer.txt"
        try:
            if sha256((case / "manifest.json").read_bytes()) != registration["case_manifest_sha256"]:
                errors.append(f"Case-manifest hash mismatch: {registration['trial_id']}")
            for filename, key in (("template.txt", "template_sha256"), ("shared.txt", "shared_sha256")):
                if sha256((trial / filename).read_bytes()) != registration[key]:
                    errors.append(f"Prompt-input hash mismatch: {registration['trial_id']}/{filename}")
            original = original_path.read_bytes().decode("utf-8") if original_path.exists() else None
            if (sha256(original.encode("utf-8")) if original is not None else None) != registration["original_answer_sha256"]:
                errors.append(f"Original-answer hash mismatch: {registration['trial_id']}")
            metadata = registration.get("metadata", {})
            if metadata.get("review"):
                parent = root / "trials" / _name(metadata["parent_trial_id"])
                parent_registration = _read_json(parent / "registration.json")
                parent_metadata = parent_registration.get("metadata", {})
                if sha256((parent / "answer.txt").read_bytes()) != registration["original_answer_sha256"]:
                    errors.append(f"Review original differs from its registered parent: {registration['trial_id']}")
                if parent_registration["case_id"] != registration["case_id"] or any(
                    parent_metadata.get(key) != metadata.get(key) for key in ("arm", "repeat")
                ) or parent_metadata.get("review"):
                    errors.append(f"Review parent belongs to a different case, deliverable, repeat or review: {registration['trial_id']}")
                if metadata.get("stage") == "heldout" and metadata.get("repeat") != 1:
                    errors.append(f"Held-out review is not the preselected first repeat: {registration['trial_id']}")
            rendered = render_prompt(
                trial / "template.txt", (case / "source_bundle.txt").read_bytes().decode("utf-8"),
                request_path.read_bytes().decode("utf-8") if request_path.exists() else None,
                shared_rules=(trial / "shared.txt").read_bytes().decode("utf-8"), original_answer=original,
                arm_instruction=registration.get("arm_instruction"),
            ).encode("utf-8")
            if rendered != (trial / "prompt.txt").read_bytes() or sha256(rendered) != registration["prompt_sha256"]:
                errors.append(f"Prompt replay mismatch: {registration['trial_id']}")
            decision_path = trial / "decision.json"
            if decision_path.exists():
                decision = _read_json(decision_path)
                answer_path = trial / "answer.txt"
                answer = answer_path.read_bytes().decode("utf-8") if answer_path.exists() else None
                if (sha256(answer.encode("utf-8")) if answer is not None else None) != decision["output_sha256"]:
                    errors.append(f"Output hash mismatch: {registration['trial_id']}")
                if sessions_dir is not None:
                    receipt = find_receipt(decision["agent_session_id"], sessions_dir)
                    _, fresh = parse_receipt(receipt, decision["agent_session_id"], decision["turn_id"],
                                             expected_model=registration["expected_model"], expected_effort=registration["expected_effort"],
                                             expected_prompt_sha256=registration["prompt_sha256"])
                    # A receipt can grow after import; only allowlisted selected-turn facts must match.
                    expected = {k: v for k, v in decision.items() if k not in {"trial_id", "case_id", "prompt_sha256", "receipt_sha256"}}
                    actual = {k: v for k, v in fresh.items() if k != "receipt_sha256"}
                    if expected != actual:
                        errors.append(f"Receipt decision replay mismatch: {registration['trial_id']}")
                    receipt_replays += 1
        except (OSError, ValueError, KeyError) as error:
            errors.append(f"Trial replay failed: {registration['trial_id']}: {error}")
    return {"schema": IDENTITY, "verified": not errors, "errors": errors,
            "case_count": len(cases), "trial_count": len(registrations),
            "reference_count": reference_count,
            "receipt_replay_count": receipt_replays, "model_calls": 0}


def summarize(run_dir: Path | str) -> dict:
    root = Path(run_dir)
    decisions = [_read_json(p) for p in sorted((root / "trials").glob("*/decision.json"))]
    registrations = [_read_json(p) for p in sorted((root / "trials").glob("*/registration.json"))]
    by_response = {}
    conflicts = []
    for decision in decisions:
        for response_id, usage in decision["usage"]["by_response_id"].items():
            if response_id in by_response and by_response[response_id] != usage:
                conflicts.append(response_id)
            by_response.setdefault(response_id, usage)
    total_usage = {key: sum(u[key] for u in by_response.values()) if by_response and all(u[key] is not None for u in by_response.values()) else None for key in TOKEN_FIELDS}
    return {
        "schema": IDENTITY, "prepared_trials": len(registrations), "imported_trials": len(decisions),
        "protocol_status_counts": dict(Counter(d["protocol_status"] for d in decisions)),
        "completed_trials": sum(d["completed"] for d in decisions),
        "unique_response_count": len(by_response), "usage_totals": total_usage,
        "usage_conflict_response_ids": sorted(set(conflicts)),
        "trials_with_unknown_usage": [d["trial_id"] for d in decisions if not d["usage"]["response_count"]],
        "semantic_scores": "Semantic scoring is an independent assistant review; protocol conformity is not semantic success.",
        "monetary_cost": None,
    }


def report(run_dir: Path | str) -> str:
    summary = summarize(run_dir)
    return "\n".join([
        "# Direct-model experiment execution records", "",
        f"Prepared trials: {summary['prepared_trials']}. Imported trials: {summary['imported_trials']}. Completed trials: {summary['completed_trials']}.", "",
        "Protocol status: " + json.dumps(summary["protocol_status_counts"], sort_keys=True) + ".", "",
        "Usage totals deduplicate per-response receipts by response ID. Unknown usage remains unknown. No billing amount is inferred.", "",
        "```json", json.dumps(summary["usage_totals"], indent=2), "```", "",
        summary["semantic_scores"], "",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    package = commands.add_parser("package")
    package.add_argument("--run-dir", required=True)
    package.add_argument("--case-id", required=True)
    package.add_argument("--source-dir", required=True)
    package.add_argument("--source-file", action="append", required=True)
    package.add_argument("--user-request-file")
    prepare = commands.add_parser("prepare")
    prepare.add_argument("--run-dir", required=True)
    prepare.add_argument("--trial-id", required=True)
    prepare.add_argument("--case-id", required=True)
    prepare.add_argument("--template", required=True)
    prepare.add_argument("--shared")
    prepare.add_argument("--original-answer")
    prepare.add_argument("--arm-instruction-file")
    imported = commands.add_parser("import")
    imported.add_argument("--run-dir", required=True)
    imported.add_argument("--trial-id", required=True)
    imported.add_argument("--agent-session-id")
    imported.add_argument("--agent-name")
    imported.add_argument("--root-session-id")
    imported.add_argument("--turn-id")
    imported.add_argument("--sessions-dir", default=str(DEFAULT_SESSIONS))
    imported.add_argument("--receipt-path")
    replay = commands.add_parser("replay")
    replay.add_argument("--run-dir", required=True)
    replay.add_argument("--sessions-dir")
    output = commands.add_parser("report")
    output.add_argument("--run-dir", required=True)
    output.add_argument("--output")
    args = parser.parse_args(argv)
    if args.command == "package":
        request = Path(args.user_request_file).read_bytes().decode("utf-8") if args.user_request_file else None
        result = package_bundle(args.source_dir, args.run_dir, args.case_id, source_files=args.source_file, user_request=request)
    elif args.command == "prepare":
        arm = Path(args.arm_instruction_file).read_bytes().decode("utf-8") if args.arm_instruction_file else None
        result = prepare_trial(args.run_dir, args.trial_id, args.case_id, args.template, shared_path=args.shared,
                               original_answer_path=args.original_answer, arm_instruction=arm)
    elif args.command == "import":
        result = import_trial(args.run_dir, args.trial_id, agent_session_id=args.agent_session_id,
                              turn_id=args.turn_id, sessions_dir=args.sessions_dir, receipt_path=args.receipt_path,
                              agent_name=args.agent_name, root_session_id=args.root_session_id)
    elif args.command == "replay":
        result = verify(args.run_dir, sessions_dir=args.sessions_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["verified"] else 1
    else:
        rendered = report(args.run_dir)
        if args.output:
            _write_new(Path(args.output), rendered.encode("utf-8"))
        else:
            print(rendered, end="")
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
