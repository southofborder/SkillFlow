"""Complete native deliveries are measured before any process starts."""
from copy import deepcopy

import pytest

from skillflow.common.delivery_size import inspect_delivery
from tests.document_guided.test_client import client, message, pending
from tools.doe import document_guided_client as transport


def prompt():
    return ("STEP RESPONSIBILITY\nAnalyze.\n\nPREVIOUS WORK\n{}\n\n"
            "GLOBAL REQUIREMENTS AND LIMITATIONS\nPreserve fields.\n\n"
            "RELATED SOURCE\n原文😀\r\nsource line\r\n\n\n"
            "OUTPUT REQUIREMENTS\nReturn JSON.")


def test_exact_unicode_delivery_sections_and_prefix():
    text = prompt()
    result = inspect_delivery(text, prefix="adapter\n", max_characters=len(text) + 8)
    assert result["status"] == "within_limit"
    assert result["characters"] == len("adapter\n" + text)
    assert result["utf8_bytes"] == len(("adapter\n" + text).encode("utf-8"))
    assert sum(row["characters"] for row in result["sections"].values()) == result["characters"]
    assert sum(row["utf8_bytes"] for row in result["sections"].values()) == result["utf8_bytes"]
    assert "原文😀\r\nsource line\r\n" in text
    assert set(result["sections"]) == {"adapter_prefix", "step_responsibility", "previous_work",
        "global_requirements_and_limitations", "related_source", "output_requirements"}


@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_pure_inspection_has_no_owner_or_transport_side_effects(tmp_path, monkeypatch, offset):
    text = prompt()
    value = transport.Client(tmp_path / "transport", owner=tmp_path / "missing")
    monkeypatch.setattr(transport, "MAX_INPUT_CHARS", len(transport.ENVELOPE + text) + offset)
    report = value.preflight(text)
    assert report["excess_characters"] == max(0, -offset)
    assert not list(tmp_path.rglob("*"))


@pytest.mark.parametrize("kind", ["sensitivity", "task-correspondence", "revision-sensitivity",
                                 "revision-task-correspondence", "review", "graph"])
def test_every_stage_rejection_has_bound_complete_size_report_before_launch(tmp_path, monkeypatch, kind):
    value, _, launches = client(tmp_path, [{"rows": [message("unused")]}])
    text = prompt()
    pending(value.owner, text, f"calls/{kind}/a001")
    monkeypatch.setattr(transport, "MAX_INPUT_CHARS", len(transport.ENVELOPE + text) - 1)
    with pytest.raises(transport.InputTooLarge):
        value.complete(text)
    report = transport.read(next((tmp_path / "transport").rglob("preflight.json")))
    rejection = transport.read(next((tmp_path / "transport").rglob("input-rejection.json")))
    assert report == value.preflight(text)
    assert report["excess_characters"] == 1
    assert rejection["process_started"] is False and rejection["preflight_sha256"]
    saved = next((tmp_path / "transport").rglob("prompt.txt")).read_bytes().decode("utf-8")
    assert saved == transport.ENVELOPE + text
    assert not launches and not list((tmp_path / "transport").rglob("started.json"))


def test_correction_rechecks_actual_prompt_and_rejects_modified_preflight(tmp_path, monkeypatch):
    value, text, launches = client(tmp_path, [{"rows": [message("first")]}])
    assert value.complete(text) == "first"
    preflight = next((tmp_path / "transport").rglob("preflight.json"))
    assert transport.read(preflight) == value.preflight(text)
    correction = prompt()
    pending(value.owner, correction, "calls/graph/a002")
    monkeypatch.setattr(transport, "MAX_INPUT_CHARS", len(transport.ENVELOPE + correction) - 1)
    with pytest.raises(transport.InputTooLarge):
        value.complete(correction)
    assert len(launches) == 1
    current = [p for p in (tmp_path / "transport").rglob("preflight.json") if p != preflight][0]
    changed = deepcopy(transport.read(current))
    changed["characters"] -= 1
    transport._write(current, changed)
    with pytest.raises(ValueError, match="preflight differs"):
        value.complete(correction)
    assert len(launches) == 1
