"""Windowed per-response capture without messages, cumulative totals or targets."""
import json

import pytest

from tools.doe.real_comparison import preparation_receipts as receipts

SID = "00000000-0000-0000-0000-000000000001"
OTHER = "00000000-0000-0000-0000-000000000002"
SINCE = "2026-10-20T09:00:00Z"
END = "2026-10-20T10:00:00Z"


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def usage(response_id, *, thread=SID, timestamp="2026-10-20T09:30:00Z", **changes):
    values = dict(input_tokens=10, cached_input_tokens=2, cache_write_input_tokens=0,
                  output_tokens=5, reasoning_output_tokens=1, total_tokens=15)
    values.update(changes)
    return {"type": "token_usage_record", "timestamp": timestamp,
            "payload": {"thread_id": thread, "response_id": response_id, "usage": values}}


def segment(tmp_path, name, rows, *, primary=SID):
    path = tmp_path / "sessions" / f"rollout-{SID}-{name}.jsonl"
    write(path, [{"type": "session_meta", "payload": {"id": primary, "session_id": SID}}, *rows])
    return path


def capture(tmp_path):
    allowlist = tmp_path / "allowlist.json"
    allowlist.write_text(json.dumps({"session_ids": [SID], "since": SINCE}), encoding="utf-8")
    return receipts.capture_preparation_receipts(allowlist, tmp_path / "capture.json",
                                                 sessions_dir=tmp_path / "sessions", captured_at=END)


def test_multiple_exact_segments_deduplicate_without_exporting_session_content(tmp_path):
    first = segment(tmp_path, "original", [usage("r1"),
        {"type": "event_msg", "payload": {"total_token_usage": {"total_tokens": 999999},
                                          "hidden_reasoning": "DO_NOT_EXPORT"}}])
    second = segment(tmp_path, "resumed", [usage("r1"), usage("r2")])
    result = capture(tmp_path)
    assert result["observed"]["response_count"] == 2
    assert result["observed"]["totals"]["total_tokens"] == 30
    assert result["duplicate_response_records"] == 1
    assert {s["path"] for s in result["sessions"][0]["segments"]} == {str(first), str(second)}
    assert "DO_NOT_EXPORT" not in (tmp_path / "capture.json").read_text(encoding="utf-8")
    assert result["complete_preparation_cost"] is None and result["model_calls"] == 0


def test_conflicting_counters_are_unknown_and_both_variants_are_retained(tmp_path):
    segment(tmp_path, "a", [usage("r1")])
    segment(tmp_path, "b", [usage("r1", output_tokens=8, total_tokens=18), usage("r1")])
    result = capture(tmp_path)
    assert result["observed"]["conflicting_response_ids"] == ["r1"]
    assert all(value is None for value in result["observed"]["totals"].values())
    assert all(value is None for value in result["observed"]["by_response_id"]["r1"].values())
    assert len(result["counter_conflicts"]["r1"]) == 2
    assert sum(len(v["locations"]) for v in result["counter_conflicts"]["r1"]) == 3


def test_primary_metadata_and_exact_thread_and_time_all_bound_capture(tmp_path):
    segment(tmp_path, "wrong-meta", [usage("wrong-primary")], primary=OTHER)
    segment(tmp_path, "valid", [usage("wrong-thread", thread=OTHER),
        usage("before", timestamp="2026-10-20T08:59:59Z"),
        usage("at-end", timestamp=END), usage("retained", timestamp=SINCE)])
    result = capture(tmp_path)
    assert set(result["observed"]["by_response_id"]) == {"retained"}
    assert len(result["rejected_paths"]) == 1
    assert len(result["sessions"][0]["segments"]) == 1


def test_missing_counter_is_unknown_without_inferring_it_from_totals(tmp_path):
    row = usage("r1")
    del row["payload"]["usage"]["reasoning_output_tokens"]
    segment(tmp_path, "valid", [row])
    result = capture(tmp_path)
    assert result["observed"]["totals"]["reasoning_output_tokens"] is None
    assert result["observed"]["totals"]["total_tokens"] == 15


def test_no_verified_segment_is_unknown_and_existing_capture_is_preserved(tmp_path):
    segment(tmp_path, "wrong", [usage("r1")], primary=OTHER)
    result = capture(tmp_path)
    assert result["observed"]["response_count"] == 0
    assert result["observed"]["missing_requests"] == ["no_verified_segment:" + SID]
    assert all(value is None for value in result["observed"]["totals"].values())
    before = (tmp_path / "capture.json").read_bytes()
    with pytest.raises(ValueError, match="Preserve prior"):
        capture(tmp_path)
    assert (tmp_path / "capture.json").read_bytes() == before
