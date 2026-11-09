"""Opt-in record replacement preserves full candidates and recorded replies."""
from copy import deepcopy
import json
from threading import Event

import pytest

from skillflow.common.artifacts import ArtifactWriter
from skillflow.common.recording import canonical_sha256, injected_factory, read_json
from skillflow.common.source_evidence import _json_object
from skillflow.common.structural_correction import (
    ResponseChain, ResponseChainError, StructuralCorrectionLimitReached, correction_prompt,
)
from skillflow.common.validation import StructuralValidationError, structural_error
from skillflow.propagation.annotation.config import annotation_config


class Client:
    def __init__(self, values, stop=None):
        self.values, self.prompts, self.stop = list(values), [], stop

    def complete(self, prompt):
        self.prompts.append(prompt)
        result = deepcopy(self.values.pop(0))
        if self.stop is not None and len(self.prompts) == 2:
            self.stop.set()
        return result


class Records:
    """Test strategy; the production fragment module owns its record format."""
    identity = "test-record-replacement-v1"

    def build_prompt(self, base_prompt, candidate, diagnostics):
        return base_prompt + "\nREPLACE_EXISTING_RECORDS\n" + json.dumps({
            "candidate": candidate, "diagnostics": diagnostics}, sort_keys=True)

    def merge(self, previous_candidate, raw_correction):
        correction = _json_object(raw_correction)
        try:
            previous = _json_object(previous_candidate)
        except (ValueError, TypeError):
            return correction
        if set(correction) != {"replacements"} or not isinstance(correction["replacements"], dict):
            raise structural_error("replacement_shape", "", "Return replacements by an existing record ID")
        result = deepcopy(previous)
        for record_id, value in correction["replacements"].items():
            if record_id not in previous["records"]:
                raise structural_error("replacement_id", "/replacements", "Unknown existing record ID")
            result["records"][record_id] = deepcopy(value)
        return result


def validate(candidate):
    try:
        value = _json_object(candidate)
    except (ValueError, TypeError) as error:
        raise structural_error("json_format", "", str(error)) from error
    errors = []
    for name, record in value["records"].items():
        if not record.get("ok"):
            errors.extend(structural_error("record_shape", "/records/" + name,
                                           "This record requires true ok").diagnostics)
    if errors:
        raise StructuralValidationError(errors)
    return value


def chain(directory, client=None, **kwargs):
    return ResponseChain(directory, prefix="calls/fragment", base_prompt="Source and fragment schema.",
        request_kind="fragment", config=annotation_config({}), writer=ArtifactWriter(()),
        validate=validate, client_factory=injected_factory(client) if client else None,
        correction_strategy=kwargs.pop("correction_strategy", Records()), max_corrections=1, **kwargs)


def initial():
    return {"records": {"kept": {"ok": True, "untouched": {"b": [3, 2], "a": "original"}},
                        "bad1": {"ok": False}, "bad2": {"ok": False}}}


def test_generic_correction_never_invents_a_whole_failure_branch():
    prompt = correction_prompt('RESPONSE = {"outcome":"completed","records":[]}', {}, [
        {"code": "missing", "path": "/records", "message": "Required records are absent"}])
    assert "Use only branches actually allowed by the supplied stage format" in prompt
    assert "existing validated failure branch" not in prompt
    assert "cannot_assess" not in prompt


def test_aggregated_record_replacements_save_full_candidate_and_reuse_answer(tmp_path):
    original = initial()
    replacement = {"replacements": {"bad1": {"ok": True}, "bad2": {"ok": True}}}
    client = Client([json.dumps(original), json.dumps(replacement)])
    live = chain(tmp_path, client)
    accepted = live.run()
    assert len(client.prompts) == 2
    assert '/records/bad1' in client.prompts[1] and '/records/bad2' in client.prompts[1]
    assert accepted["records"]["kept"] == original["records"]["kept"]
    assert live.last_candidate == accepted
    call_dir = tmp_path / "calls/fragment/a002"
    assert read_json(call_dir / "response.json") == json.dumps(replacement)
    assert read_json(call_dir / "merged-candidate.json") == accepted
    receipt = read_json(call_dir / "validation.json")
    assert receipt["candidate_sha256"] == canonical_sha256(accepted)
    assert receipt["response_sha256"] != receipt["candidate_sha256"]
    assert live.snapshot()["correction_strategy"] == Records.identity
    for kwargs in ({}, {"replay": True, "read_only": True}):
        saved = chain(tmp_path, **kwargs)
        assert saved.run() == accepted
        assert saved.last_candidate == accepted
        assert saved.snapshot() == live.snapshot()
    with pytest.raises(ResponseChainError):
        chain(tmp_path, correction_strategy=None)
    altered = Records()
    altered.identity = "changed"
    with pytest.raises(ResponseChainError):
        chain(tmp_path, correction_strategy=altered)


@pytest.mark.parametrize("replacement", [
    {"replacements": {"bad1": {"ok": True}}},
    {"replacements": {}},
    {"replacements": {"unknown": {"ok": True}}},
    {"records": {}},
])
def test_one_correction_exhaustion_exposes_full_candidate_for_salvage(tmp_path, replacement):
    original = initial()
    client = Client([original, replacement, {"records": {}}])
    live = chain(tmp_path, client)
    with pytest.raises(StructuralCorrectionLimitReached):
        live.run()
    assert len(client.prompts) == 2
    assert not (tmp_path / "calls/fragment/a003").exists()
    assert live.last_candidate["records"]["kept"] == original["records"]["kept"]
    assert set(live.last_candidate["records"]) == set(original["records"])
    saved = chain(tmp_path, replay=True, read_only=True)
    with pytest.raises(StructuralCorrectionLimitReached):
        saved.run()
    assert saved.last_candidate == live.last_candidate
    assert saved.snapshot() == live.snapshot()


def test_unparseable_top_level_can_use_complete_replacement(tmp_path):
    complete = {"records": {"new": {"ok": True}}}
    live = chain(tmp_path, Client(["{broken", json.dumps(complete)]))
    assert live.run() == complete
    assert live.last_candidate == complete
    assert chain(tmp_path, replay=True, read_only=True).run() == complete


def test_interrupted_correction_reuses_completed_raw_answer_before_merging(tmp_path):
    stopping = Event()
    client = Client([initial(), {"replacements": {"bad1": {"ok": True}, "bad2": {"ok": True}}}], stopping)
    live = chain(tmp_path, client, stop_event=stopping)
    with pytest.raises(KeyboardInterrupt):
        live.run()
    assert live.cursor == {"point": "after_call", "call": "calls/fragment/a002"}
    assert not (tmp_path / "calls/fragment/a002/merged-candidate.json").exists()
    replay = chain(tmp_path, replay=True, read_only=True, interruption=live.cursor)
    with pytest.raises(KeyboardInterrupt):
        replay.run()
    resumed = chain(tmp_path)
    assert all(row["ok"] for row in resumed.run()["records"].values())
    assert len(client.prompts) == 2
    assert chain(tmp_path, replay=True, read_only=True).run() == resumed.value


def test_changed_merged_candidate_is_not_reaccepted(tmp_path):
    live = chain(tmp_path, Client([initial(), {"replacements": {"bad1": {"ok": True}, "bad2": {"ok": True}}}]))
    live.run()
    path = tmp_path / "calls/fragment/a002/merged-candidate.json"
    value = read_json(path)
    value["records"]["kept"]["untouched"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ResponseChainError):
        chain(tmp_path, replay=True, read_only=True).run()
