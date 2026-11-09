"""Capture allowlisted preparation receipts across interrupted session segments.

Only primary session identity and attributed per-response token counters are
exported. This helper neither dispatches targets nor changes frozen cost code.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from .metrics import combine_usage
from .protocol import write_json

SCHEMA = "skillflow-preparation-receipt-capture-v2"
FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens", "total_tokens")
DEFAULT_SESSIONS = Path("C:/Users/24831/.codex/sessions")


def _time(value):
    if not isinstance(value, str):
        raise ValueError("Receipt window timestamps require explicit timezone strings")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Receipt window timestamps require an explicit timezone")
    return result.astimezone(timezone.utc)


def _primary_meta(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if '"session_meta"' not in line:
                continue
            row = json.loads(line)
            if row.get("type") == "session_meta":
                payload = row.get("payload", {})
                return {"id": payload.get("id"), "session_id": payload.get("session_id")}
    return {}


def capture_preparation_receipts(allowlist_path, output_path, *, sessions_dir=DEFAULT_SESSIONS,
                                 captured_at=None):
    """Persist one bounded snapshot; filename matches alone never authorize usage."""
    allowlist_path, output_path = Path(allowlist_path).resolve(), Path(output_path).resolve()
    if output_path.exists():
        raise ValueError("Preserve prior capture diagnostics; use a new output path")
    raw_allowlist = allowlist_path.read_bytes()
    allowlist = json.loads(raw_allowlist)
    session_ids = allowlist.get("session_ids", [])
    if (not session_ids or len(session_ids) != len(set(session_ids))
            or any(not isinstance(s, str) or not re.fullmatch(
                r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", s) for s in session_ids)):
        raise ValueError("Use a nonempty explicit allowlist of distinct exact session UUIDs")
    since = _time(allowlist.get("since"))
    end = _time(captured_at) if captured_at else datetime.now(timezone.utc)
    if end <= since:
        raise ValueError("Capture time must follow the beginning of its receipt window")
    rows, locations, conflicts, missing, sessions, rejected = {}, {}, {}, [], [], []
    usage_records = duplicates = 0
    for session_id in session_ids:
        segments = []
        for path in sorted(Path(sessions_dir).rglob("*" + session_id + "*.jsonl")):
            path = path.resolve()
            try:
                meta = _primary_meta(path)
            except (ValueError, UnicodeError):
                rejected.append({"path": str(path), "reason": "Unreadable primary session metadata"})
                continue
            if meta.get("id") != session_id:
                rejected.append({"path": str(path), "primary_session_meta": meta,
                                 "reason": "Primary session id does not equal this allowlisted session"})
                continue
            ids, digest = set(), hashlib.sha256()
            extent = path.stat().st_size
            remaining, line_number, consumed = extent, 0, 0
            with path.open("rb") as stream:
                while remaining:
                    raw = stream.readline(remaining)
                    if not raw:
                        break
                    remaining -= len(raw)
                    consumed += len(raw)
                    line_number += 1
                    digest.update(raw)
                    if b'"token_usage_record"' not in raw:
                        continue
                    marker = f"{session_id}:{path.name}:{line_number}"
                    try:
                        row = json.loads(raw)
                    except (ValueError, UnicodeError):
                        missing.append("unreadable_usage_record:" + marker)
                        continue
                    if row.get("type") != "token_usage_record":
                        continue
                    payload = row.get("payload", {})
                    if payload.get("thread_id") != session_id:
                        continue
                    try:
                        stamp = _time(row.get("timestamp"))
                    except (ValueError, TypeError):
                        missing.append("unbounded_usage_timestamp:" + marker)
                        continue
                    if not since <= stamp < end:
                        continue
                    response_id = payload.get("response_id")
                    if not isinstance(response_id, str) or not response_id:
                        missing.append("missing_response_id:" + marker)
                        continue
                    raw_usage = payload.get("usage", {})
                    if not isinstance(raw_usage, dict):
                        raw_usage = {}
                    values = {field: raw_usage.get(field) if type(raw_usage.get(field)) is int
                              and raw_usage[field] >= 0 else None for field in FIELDS}
                    location = {"session_id": session_id, "path": str(path), "line": line_number,
                                "timestamp": row["timestamp"]}
                    usage_records += 1
                    if response_id in rows:
                        duplicates += 1
                        if values != rows[response_id] or response_id in conflicts:
                            variants = conflicts.setdefault(response_id, [
                                {"counters": rows[response_id], "locations": locations[response_id].copy()}])
                            variant = next((v for v in variants if v["counters"] == values), None)
                            if variant is None:
                                variants.append({"counters": values, "locations": [location]})
                            else:
                                variant["locations"].append(location)
                    else:
                        rows[response_id] = values
                        locations[response_id] = []
                    locations[response_id].append(location)
                    ids.add(response_id)
            if remaining:
                missing.append("truncated_segment:" + str(path))
            segments.append({"path": str(path), "primary_session_meta": meta,
                             "captured_prefix_bytes": consumed, "size_at_open": extent,
                             "captured_prefix_sha256": digest.hexdigest(),
                             "reported_response_ids": sorted(ids)})
        if not segments:
            missing.append("no_verified_segment:" + session_id)
        sessions.append({"session_id": session_id, "segments": segments})
    # No arbitrarily selected conflicting variant is presented as an observed counter.
    safe_rows = {key: {field: None for field in FIELDS} if key in conflicts else value
                 for key, value in rows.items()}
    observed = combine_usage([{"by_response_id": safe_rows, "missing_requests": missing,
                               "conflicting_response_ids": sorted(conflicts)}])
    record = {"schema_version": SCHEMA, "captured_at": end.isoformat(), "since": allowlist["since"],
              "window": "since inclusive; captured_at exclusive; file prefixes fixed at open",
              "allowlist_path": str(allowlist_path),
              "allowlist_sha256": hashlib.sha256(raw_allowlist).hexdigest(), "session_allowlist": allowlist,
              "sessions": sessions, "rejected_paths": rejected, "observed": observed,
              "response_locations": locations, "counter_conflicts": conflicts,
              "usage_record_count": usage_records, "duplicate_response_records": duplicates,
              "complete_preparation_cost": None, "model_calls": 0,
              "limitations": "Windowed reported preparation subtotal only. The live root response still in progress at capture is excluded; later receipts, earlier research, unregistered sessions and unreceipted work may be missing. Missing counters and conflicting receipts remain unknown. Only exact thread-attributed per-response counters are used; no session-cumulative counters, hidden reasoning, message bodies or raw session exports are included."}
    write_json(output_path, record, immutable=True)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowlist", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sessions-dir", default=str(DEFAULT_SESSIONS))
    args = parser.parse_args(argv)
    record = capture_preparation_receipts(args.allowlist, args.output, sessions_dir=args.sessions_dir)
    print(json.dumps({"captured_at": record["captured_at"], "sessions": len(record["sessions"]),
                      "segments": sum(len(s["segments"]) for s in record["sessions"]),
                      "response_count": record["observed"]["response_count"],
                      "totals": record["observed"]["totals"],
                      "conflicts": len(record["counter_conflicts"]),
                      "missing_records": len(record["observed"]["missing_requests"]), "model_calls": 0}))


if __name__ == "__main__":
    main()
