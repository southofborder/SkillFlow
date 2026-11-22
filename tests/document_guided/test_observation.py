"""Public telemetry fixtures never start a native process or inspect sessions."""
import hashlib
import json
from pathlib import Path

import pytest

from tools.doe import document_guided_observation as observation


def final(text, phase=None):
    return {"type": "item.completed", "item": {"type": "agent_message", "phase": phase, "text": text}}


def encoded(row):
    return json.dumps(row, ensure_ascii=False).encode("utf-8")


def fixture(tmp_path, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(observation.time, "perf_counter", lambda: clock[0])
    (tmp_path / "stdout.jsonl").write_bytes(b"")
    (tmp_path / "stderr.txt").write_bytes(b"")
    return observation.PublicObserver(tmp_path, 0, "source🌍原文"), clock, []


def rows(path):
    return [json.loads(line) for line in (path / observation.FILENAME).read_bytes().splitlines()]


def test_split_utf8_and_json_are_observed_only_as_completed_lines(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    text = "answer🌍原文"
    raw = encoded(final(text)) + b"\n"
    split = raw.index("🌍".encode()) + 2
    (tmp_path / "stdout.jsonl").write_bytes(raw[:split])
    clock[0] = 30
    observer.observe(warnings)
    with (tmp_path / "stdout.jsonl").open("ab") as handle:
        handle.write(raw[split:])
    clock[0] = 60
    observer.observe(warnings)
    clock[0] = 65
    observer.observe(warnings, terminal=True)
    samples = rows(tmp_path)
    assert not warnings and samples[0]["events"] == []
    assert samples[0]["partial_line_bytes"] == split
    assert samples[1]["events"][0]["completed_final"] == {
        "phase": None, "characters": len(text), "utf8_bytes": len(text.encode()),
        "sha256": hashlib.sha256(text.encode()).hexdigest()}
    assert samples[2]["events"] == []
    assert (tmp_path / "stdout.jsonl").read_bytes() == raw
    summary = observation.observation_summary(tmp_path, warnings)
    assert summary["first_stdout_bytes_interval_seconds"] == [0, 30]
    assert summary["first_public_event_interval_seconds"] == [30, 60]
    assert summary["first_completed_final_interval_seconds"] == [30, 60]
    assert summary["first_token_seconds"] is summary["provider_generation_seconds"] is None
    assert summary["delivery"]["characters"] < summary["delivery"]["utf8_bytes"]


def test_terminal_line_without_newline_and_malformed_rows_preserve_raw_bytes(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    raw = b"not json\n42\n" + encoded(final("answer"))
    (tmp_path / "stdout.jsonl").write_bytes(raw)
    clock[0] = 30
    observer.observe(warnings)
    clock[0] = 31
    observer.observe(warnings, terminal=True)
    samples = rows(tmp_path)
    assert [event["parse_status"] for event in samples[0]["events"]] == ["malformed", "non_object"]
    assert samples[1]["events"][0]["newline_terminated"] is False
    assert samples[1]["partial_line_bytes"] == len(encoded(final("answer")))
    summary = observation.observation_summary(tmp_path, warnings)
    assert summary["status"] == "terminal" and summary["observed_stdout_lines"] == 3
    assert summary["first_completed_final_interval_seconds"] == [30, 31]
    assert summary["terminal_stdout_bytes"] == len(raw)
    assert (tmp_path / "stdout.jsonl").read_bytes() == raw and not warnings


@pytest.mark.parametrize("phase", ["commentary", "analysis", "unknown"])
def test_other_message_phases_and_item_bodies_never_enter_sidecar(tmp_path, monkeypatch, phase):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    events = [final("DO_NOT_COPY_MESSAGE", phase),
        {"type": "item.completed", "item": {"type": "reasoning", "text": "DO_NOT_COPY_PRIVATE_BODY"}},
        {"type": "error", "message": "DO_NOT_COPY_ERROR"},
        {"type": "turn.completed", "usage": {"output_tokens": 12345}}]
    raw = b"\n".join(encoded(event) for event in events)
    (tmp_path / "stdout.jsonl").write_bytes(raw)
    clock[0] = 5
    observer.observe(warnings, terminal=True)
    sidecar = (tmp_path / observation.FILENAME).read_text(encoding="utf-8")
    assert "DO_NOT_COPY" not in sidecar and "output_tokens" not in sidecar
    assert all("completed_final" not in event for event in rows(tmp_path)[0]["events"])
    assert (tmp_path / "stdout.jsonl").read_bytes() == raw


@pytest.mark.parametrize("phase", [None, "final", "final_answer"])
def test_final_phases_record_sizes_without_text(tmp_path, monkeypatch, phase):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    (tmp_path / "stdout.jsonl").write_bytes(encoded(final("DO_NOT_COPY_FINAL", phase)))
    clock[0] = 3
    observer.observe(warnings, terminal=True)
    assert rows(tmp_path)[0]["events"][0]["completed_final"]["phase"] == phase
    assert "DO_NOT_COPY_FINAL" not in (tmp_path / observation.FILENAME).read_text(encoding="utf-8")


def test_unchanged_polls_do_not_duplicate_events_and_preserve_incomplete_tail(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    raw = encoded({"type": "turn.started"}) + b"\n{"  # The terminal tail is malformed, not a final answer.
    (tmp_path / "stdout.jsonl").write_bytes(raw)
    for elapsed in (30, 60):
        clock[0] = elapsed
        observer.observe(warnings)
    clock[0] = 90
    observer.observe(warnings, terminal=True)
    assert [len(row["events"]) for row in rows(tmp_path)] == [1, 0, 1]
    summary = observation.observation_summary(tmp_path, warnings)
    assert summary["first_completed_final_interval_seconds"] is None
    assert summary["terminal_tail_bytes"] == 1


def test_observer_write_failure_is_optional_and_does_not_replace_existing_file(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    sidecar = tmp_path / observation.FILENAME
    sidecar.write_bytes(b"existing evidence")
    observer.observe(warnings)
    observer.observe(warnings, terminal=True)
    assert len(warnings) == 1 and observer.disabled
    assert sidecar.read_bytes() == b"existing evidence"


def test_missing_public_file_disables_observation_without_recreating_it(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    (tmp_path / "stdout.jsonl").unlink()
    observer.observe(warnings, terminal=True)
    assert len(warnings) == 1 and not (tmp_path / "stdout.jsonl").exists()
    assert not (tmp_path / observation.FILENAME).exists()


def test_truncated_public_file_cannot_create_false_arrival_intervals(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    (tmp_path / "stdout.jsonl").write_bytes(encoded({"type": "turn.started"}) + b"\n")
    clock[0] = 30
    observer.observe(warnings)
    (tmp_path / "stdout.jsonl").write_bytes(b"")
    clock[0] = 60
    observer.observe(warnings, terminal=True)
    assert any("truncated" in warning for warning in warnings)
    summary = observation.observation_summary(tmp_path, warnings)
    assert summary["status"] == "partial" and summary["terminal_stdout_bytes"] is None


def test_missing_and_malformed_optional_observations_remain_unknown(tmp_path):
    warnings = []
    missing = observation.observation_summary(tmp_path, warnings)
    assert missing["status"] == "missing" and not warnings
    (tmp_path / observation.FILENAME).write_bytes(b"not json\n")
    malformed = observation.observation_summary(tmp_path, warnings)
    assert malformed["status"] == "unavailable" and warnings
    assert malformed["first_completed_final_interval_seconds"] is None


def test_invalid_sequence_preserves_only_valid_prefix(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    clock[0] = 30
    observer.observe(warnings)
    bad = rows(tmp_path)[0]
    bad.update(sample=2, elapsed_seconds=20, previous_elapsed_seconds=30, terminal=True)
    with (tmp_path / observation.FILENAME).open("ab") as handle:
        handle.write(encoded(bad) + b"\n")
    summary = observation.observation_summary(tmp_path, warnings)
    assert summary["status"] == "partial" and summary["sample_count"] == 1
    assert summary["terminal_stdout_bytes"] is None and warnings


def test_interval_lower_bound_includes_previous_read_window(tmp_path, monkeypatch):
    observer, _, warnings = fixture(tmp_path, monkeypatch)
    times = iter([30, 35, 60, 65])
    monkeypatch.setattr(observation.time, "perf_counter", lambda: next(times))
    (tmp_path / "stdout.jsonl").write_bytes(encoded({"type": "turn.started"}) + b"\n")
    observer.observe(warnings)
    with (tmp_path / "stdout.jsonl").open("ab") as handle:
        handle.write(encoded(final("answer")))
    observer.observe(warnings, terminal=True)
    summary = observation.observation_summary(tmp_path, warnings)
    # Bytes can arrive after the previous read but before its timestamp (35).
    # The previous read start (30) is the conservative lower arrival bound.
    assert summary["first_completed_final_interval_seconds"] == [30, 65]
    assert not warnings


def test_malformed_final_metadata_does_not_claim_final_timing(tmp_path, monkeypatch):
    observer, clock, warnings = fixture(tmp_path, monkeypatch)
    (tmp_path / "stdout.jsonl").write_bytes(encoded(final("answer")))
    clock[0] = 2
    observer.observe(warnings, terminal=True)
    row = rows(tmp_path)[0]
    row["events"][0]["completed_final"] = {}
    (tmp_path / observation.FILENAME).write_bytes(encoded(row) + b"\n")
    summary = observation.observation_summary(tmp_path, warnings)
    assert summary["status"] == "unavailable" and summary["first_completed_final_interval_seconds"] is None
    assert warnings
