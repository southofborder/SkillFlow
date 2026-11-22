"""Optional host observations of public CLI files, never provider token timing.

The existing process poll calls this observer; it starts no thread or process.
Raw files and answer acceptance are independent of these monitoring sidecars.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time


IDENTITY = "skillflow-public-observation-v1"
FILENAME = "public-observations.jsonl"
TIMING_SCOPE = ("Host observation intervals at existing process polls, not provider token times; "
                "local scheduling and monitoring can widen intervals beyond 30 seconds")


def _event(raw, start, end, number, terminated):
    result = {"line_number": number, "start_byte": start, "end_byte": end,
              "newline_terminated": terminated}
    try:
        row = json.loads(raw)
    except (ValueError, UnicodeError):
        return {**result, "event_type": None, "parse_status": "malformed"}
    if not isinstance(row, dict):
        return {**result, "event_type": None, "parse_status": "non_object"}
    event_type = row.get("type")
    result.update(event_type=event_type if isinstance(event_type, str) else None, parse_status="object")
    if event_type == "item.completed":
        item = row.get("item")
        if (isinstance(item, dict) and item.get("type") == "agent_message"
                and item.get("phase") in (None, "final", "final_answer")):
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                encoded = text.encode("utf-8")
                result["completed_final"] = {"phase": item.get("phase"), "characters": len(text),
                    "utf8_bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest()}
    # No other item body, message text, error text, or usage is copied or interpreted.
    return result


class PublicObserver:
    def __init__(self, directory, start, delivery):
        self.directory, self.start = Path(directory), start
        self.delivery = {"characters": len(delivery), "utf8_bytes": len(delivery.encode("utf-8")),
                         "sha256": hashlib.sha256(delivery.encode("utf-8")).hexdigest()}
        self.position = self.line_start = self.lines = self.samples = 0
        self.pending, self.previous_elapsed, self.disabled = b"", 0.0, False

    def observe(self, warnings, *, terminal=False):
        """Best-effort append; any monitoring failure leaves native behavior alone."""
        if self.disabled:
            return
        try:
            observation_start = time.perf_counter() - self.start
            stdout = self.directory / "stdout.jsonl"
            with stdout.open("rb") as handle:
                if handle.seek(0, 2) < self.position:
                    raise ValueError("Public stdout was truncated between observations")
                handle.seek(self.position)
                data = handle.read()
                self.position = handle.tell()
            stderr_bytes = (self.directory / "stderr.txt").stat().st_size
            pieces = (self.pending + data).split(b"\n")
            complete, self.pending = pieces[:-1], pieces[-1]
            events = []
            for raw in complete:
                end = self.line_start + len(raw) + 1
                self.lines += 1
                events.append(_event(raw, self.line_start, end, self.lines, True))
                self.line_start = end
            tail_bytes = len(self.pending)
            if terminal and self.pending:
                self.lines += 1
                events.append(_event(self.pending, self.line_start, self.position, self.lines, False))
                self.pending, self.line_start = b"", self.position
            elapsed = time.perf_counter() - self.start
            row = {"identity": IDENTITY, "sample": self.samples + 1,
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "elapsed_seconds": elapsed, "observation_started_elapsed_seconds": observation_start,
                "previous_elapsed_seconds": self.previous_elapsed,
                "terminal": terminal, "stdout_bytes": self.position, "stderr_bytes": stderr_bytes,
                "stdout_lines": self.lines, "partial_line_bytes": tail_bytes, "events": events}
            if self.samples == 0:
                row.update(delivery=self.delivery, timing_scope=TIMING_SCOPE)
            with (self.directory / FILENAME).open("xb" if self.samples == 0 else "ab") as handle:
                handle.write((json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
            self.samples += 1
            # Start of the previous read is a conservative lower bound: bytes
            # may arrive between its final read and completion timestamp.
            self.previous_elapsed = observation_start
        except Exception as error:
            self.disabled = True
            warnings.append("Public observation unavailable: " + type(error).__name__ + ": " + str(error))


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def observation_summary(directory, warnings):
    """Read optional observations without creating or upgrading usage evidence."""
    result = {"status": "missing", "sample_count": 0, "timing_scope": TIMING_SCOPE,
        "delivery": None, "last_elapsed_seconds": None, "observed_stdout_lines": None,
        "terminal_stdout_bytes": None, "terminal_stderr_bytes": None, "terminal_tail_bytes": None,
        "first_stdout_bytes_interval_seconds": None, "first_public_event_interval_seconds": None,
        "first_completed_final_interval_seconds": None,
        "first_token_seconds": None, "provider_generation_seconds": None}
    path = Path(directory) / FILENAME
    try:
        if not path.is_file():
            return result
        previous = 0.0
        previous_bytes = previous_lines = previous_line_end = 0
        terminal = False
        with path.open("rb") as handle:
            for raw in handle:
                row = json.loads(raw)
                elapsed, lower = row.get("elapsed_seconds"), row.get("previous_elapsed_seconds")
                observation_start = row.get("observation_started_elapsed_seconds")
                if (row.get("identity") != IDENTITY or terminal
                        or row.get("sample") != result["sample_count"] + 1
                        or not _number(elapsed) or lower != previous or elapsed < lower
                        or not _number(observation_start) or not lower <= observation_start <= elapsed
                        or type(row.get("terminal")) is not bool
                        or any(type(row.get(key)) is not int or row[key] < 0 for key in
                               ("stdout_bytes", "stderr_bytes", "stdout_lines", "partial_line_bytes"))
                        or row["stdout_bytes"] < previous_bytes or row["stdout_lines"] < previous_lines
                        or not isinstance(row.get("events"), list)):
                    raise ValueError("Invalid public observation sequence")
                interval = [lower, elapsed]
                for index, event in enumerate(row["events"], previous_lines + 1):
                    if (not isinstance(event, dict) or event.get("line_number") != index
                            or type(event.get("start_byte")) is not int or event["start_byte"] != previous_line_end
                            or type(event.get("end_byte")) is not int
                            or not event["start_byte"] <= event["end_byte"] <= row["stdout_bytes"]
                            or type(event.get("newline_terminated")) is not bool
                            or event.get("parse_status") not in {"object", "malformed", "non_object"}
                            or not (event.get("event_type") is None or isinstance(event["event_type"], str))):
                        raise ValueError("Invalid public observation event position")
                    final = event.get("completed_final")
                    if final is not None and (not isinstance(final, dict)
                            or event.get("event_type") != "item.completed"
                            or final.get("phase") not in (None, "final", "final_answer")
                            or any(type(final.get(key)) is not int or final[key] <= 0 for key in ("characters", "utf8_bytes"))
                            or final["utf8_bytes"] < final["characters"]
                            or not isinstance(final.get("sha256"), str) or len(final["sha256"]) != 64
                            or any(char not in "0123456789abcdef" for char in final["sha256"])):
                        raise ValueError("Invalid public completed-final observation")
                    previous_line_end = event["end_byte"]
                if row["stdout_lines"] != previous_lines + len(row["events"]):
                    raise ValueError("Invalid public observation line count")
                if result["sample_count"] == 0:
                    delivery = row.get("delivery")
                    if (isinstance(delivery, dict) and all(type(delivery.get(key)) is int and delivery[key] >= 0
                            for key in ("characters", "utf8_bytes")) and isinstance(delivery.get("sha256"), str)):
                        result["delivery"] = {key: delivery[key] for key in ("characters", "utf8_bytes", "sha256")}
                result.update(status="partial", sample_count=row["sample"], last_elapsed_seconds=elapsed,
                              observed_stdout_lines=row["stdout_lines"])
                if row["stdout_bytes"] and result["first_stdout_bytes_interval_seconds"] is None:
                    result["first_stdout_bytes_interval_seconds"] = interval
                if result["first_public_event_interval_seconds"] is None and any(
                        isinstance(event.get("event_type"), str) for event in row["events"]):
                    result["first_public_event_interval_seconds"] = interval
                if result["first_completed_final_interval_seconds"] is None and any(
                        isinstance(event.get("completed_final"), dict) for event in row["events"]):
                    result["first_completed_final_interval_seconds"] = interval
                terminal = row["terminal"]
                if terminal:
                    result.update(status="terminal", terminal_stdout_bytes=row["stdout_bytes"],
                        terminal_stderr_bytes=row["stderr_bytes"], terminal_tail_bytes=row["partial_line_bytes"])
                previous, previous_bytes, previous_lines = observation_start, row["stdout_bytes"], row["stdout_lines"]
    except Exception as error:
        result.update(status="partial" if result["sample_count"] else "unavailable",
                      terminal_stdout_bytes=None, terminal_stderr_bytes=None, terminal_tail_bytes=None)
        warnings.append("Unavailable public observations: " + str(path) + ": " + type(error).__name__ + ": " + str(error))
    return result
