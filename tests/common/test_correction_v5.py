"""v5 presentation is compact; raw responses and replay identity stay exact."""
from copy import deepcopy
import json
from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from skillflow.common.structural_correction import (
    ResponseChainError, correction_prompt, correction_base_prompt, correct_response,
)
from skillflow.common.validation import schema_error, diagnostic_materials, validation_at
from skillflow.common.recording import read_json
from tests.common.test_structural_correction import run, Script, validate


BASE = """frozen source, contract and format
<!-- SKILLFLOW_PROMPT:EXAMPLES:BEGIN -->
teaching only
<!-- SKILLFLOW_PROMPT:EXAMPLES:END -->
actual source, CFG and Task
<!-- SKILLFLOW_PROMPT:SELF_CHECK:BEGIN -->
checklist only
<!-- SKILLFLOW_PROMPT:SELF_CHECK:END -->
repair context remains
"""


def context(prompt):
    return json.loads(prompt.split("CURRENT_CANDIDATE_AND_DIAGNOSTICS\n", 1)[1])


def test_only_explicit_teaching_sections_removed_and_candidate_not_escaped():
    raw = ' { "bad": "an actual value", "list": [1,2] } '
    prompt = correction_prompt(BASE, raw, [{"code": "x", "path": "/bad", "message": "check"}])
    assert "teaching only" not in prompt and "checklist only" not in prompt
    for kept in ("frozen source, contract and format", "actual source, CFG and Task", "repair context remains"):
        assert kept in prompt
    assert context(prompt)["candidate"] == {"bad": "an actual value", "list": [1, 2]}
    assert context(prompt)["protocol"] == "skillflow-structural-correction-v5"
    assert raw == ' { "bad": "an actual value", "list": [1,2] } '


@pytest.mark.parametrize("raw", ['{"a":1,"a":2}', '{"a":1}}', '', '[1,2]'])
def test_unparseable_or_duplicate_candidate_stays_verbatim(raw):
    assert context(correction_prompt(BASE, raw, []))["candidate"] == raw


def test_unmarked_text_is_not_removed_and_bad_program_markers_stop():
    original = "User says EXAMPLES and SELF_CHECK are important."
    assert correction_base_prompt(original) == original
    with pytest.raises(ValueError, match="section markers"):
        correction_base_prompt(BASE.replace("<!-- SKILLFLOW_PROMPT:EXAMPLES:END -->", ""))


def test_compact_display_does_not_replace_raw_persisted_candidate(tmp_path):
    raw = ' { "bad": "preserved whitespace" } '
    client = Script([raw, {"ok": True}])
    chain = run(tmp_path, client)
    chain.run()
    assert read_json(tmp_path / "calls/annotation/a001/response.json") == raw
    assert context(client.prompts[1])["candidate"] == {"bad": "preserved whitespace"}
    assert run(tmp_path, replay=True, read_only=True).run() == chain.value


def test_injected_request_builder_works_in_memory_persist_and_replay(tmp_path):
    def builder(base, response, diagnostics):
        return correction_prompt(base, response, diagnostics) + "\nFrozen experiment variant"
    memory = Script([{"bad": 1}, {"ok": True}])
    assert correct_response("base", complete=memory.complete, validate=validate,
                            correction_builder=builder) == {"validated": True}
    persisted = Script([{"bad": 1}, {"ok": True}])
    chain = run(tmp_path, persisted, correction_builder=builder)
    chain.run()
    assert run(tmp_path, replay=True, read_only=True, correction_builder=builder).run() == chain.value
    with pytest.raises(ResponseChainError):
        run(tmp_path, replay=True, read_only=True).run()


class InRef(BaseModel):
    kind: Literal["input"]
    index: int


class LocalRef(BaseModel):
    kind: Literal["local"]
    name: str


class Example(BaseModel):
    refs: list[Annotated[InRef | LocalRef, Field(discriminator="kind")]]


def test_schema_locations_are_candidate_paths_with_missing_value_distinguished():
    raw = {"refs": [{"kind": "input", "index": "bad"}, {"kind": "local"}]}
    with pytest.raises(ValidationError) as caught:
        Example.model_validate(raw)
    rows = schema_error(caught.value, candidate=raw).diagnostics
    assert [row["path"] for row in rows] == ["/refs/0/index", "/refs/1/name"]
    assert rows[0]["context"]["current"] == "bad"
    assert rows[0]["context"]["expected"]
    assert rows[1]["context"]["present"] is False
    assert "current" not in rows[1]["context"]


class OperandShape(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    instruction_id: str
    side: Literal["input", "output"]
    index: Annotated[int, Field(ge=0)]


class BlockShape(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    block_id: str
    path: list[str | Annotated[int, Field(ge=0)]]


class UnionExample(BaseModel):
    refs: list[OperandShape | BlockShape]


def union_error(raw):
    try:
        UnionExample.model_validate(raw)
    except ValidationError as error:
        return schema_error(error, candidate=raw, schema=UnionExample.model_json_schema())
    raise AssertionError("The test candidate must fail strict validation")


def test_object_union_errors_share_actual_parent_and_preserve_raw_mapping():
    raw = {"refs": [{"block_id": "block_calibration"}, {"block_id": "block_finish"}]}
    before = deepcopy(raw)
    error = union_error(raw)
    materials = diagnostic_materials(error.diagnostics)
    assert [row["path"] for row in materials["diagnostics"]] == ["/refs/0", "/refs/1"]
    assert len(materials["raw_diagnostics"]) > 2
    assert len(materials["diagnostic_mapping"]) == len(materials["raw_diagnostics"])
    assert {row["diagnostic_index"] for row in materials["diagnostic_mapping"]} == {0, 1}
    assert all("OperandShape" not in row["path"] and "BlockShape" not in row["path"]
               for row in materials["diagnostics"])
    assert any("OperandShape" in row["path"] for row in materials["raw_diagnostics"])
    prompt = context(correction_prompt(BASE, raw, error.diagnostics))
    assert len(prompt["format_examples"]) == 1
    assert all(row["context"]["format_example_index"] == 0 for row in prompt["diagnostics"])
    assert prompt["format_examples"][0]["syntax_examples"][1] == {
        "block_id": "<existing or supported string>", "path": []}
    assert "raw_diagnostics" not in json.dumps(prompt)
    assert raw == before and prompt["candidate"] == raw
    with pytest.raises(ValidationError):
        UnionExample.model_validate(raw)


def test_union_projection_prefix_keeps_raw_and_display_paths_traceable():
    with pytest.raises(type(union_error({"refs": [{"block_id": "b"}]}))) as caught:
        with validation_at("/candidate"):
            raise union_error({"refs": [{"block_id": "b"}]})
    material = diagnostic_materials(caught.value.diagnostics)
    assert material["diagnostics"][0]["path"] == "/candidate/refs/0"
    assert all(row["path"].startswith("/candidate/refs/0/") for row in material["raw_diagnostics"])


def _union_validator(raw):
    if raw == {"ok": True}:
        return {"validated": True}
    raise union_error(raw)


def _union_chain(directory, client=None, **kwargs):
    chain = run(directory, client, **kwargs)
    chain.validate = _union_validator
    return chain


def test_raw_union_diagnostics_and_mapping_are_saved_and_replayed(tmp_path):
    raw = {"refs": [{"block_id": "block_calibration"}]}
    client = Script([raw, {"ok": True}])
    chain = _union_chain(tmp_path, client)
    assert chain.run() == {"validated": True}
    receipt = read_json(tmp_path / "calls/annotation/a001/validation.json")
    assert receipt["version"] == "skillflow-structural-correction-v5"
    assert len(receipt["diagnostics"]) == 1
    assert len(receipt["raw_diagnostics"]) == len(receipt["diagnostic_mapping"]) > 1
    assert "audit" not in receipt["diagnostics"][0]
    assert read_json(tmp_path / "calls/annotation/a001/response.json") == raw
    assert _union_chain(tmp_path, replay=True, read_only=True).run() == chain.value
    unused = Script([])
    assert _union_chain(tmp_path, unused).run() == chain.value
    assert unused.prompts == []


@pytest.mark.parametrize("field", ["raw_diagnostics", "diagnostic_mapping", "diagnostics"])
def test_diagnostic_projection_audit_tampering_is_rejected(tmp_path, field):
    _union_chain(tmp_path, Script([{"refs": [{"block_id": "b"}]}, {"ok": True}])).run()
    path = tmp_path / "calls/annotation/a001/validation.json"
    receipt = read_json(path)
    receipt[field] = []
    path.write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ResponseChainError):
        _union_chain(tmp_path, replay=True, read_only=True).run()


@pytest.mark.parametrize("replay", [False, True])
def test_old_v4_chain_is_not_reinterpreted_by_v5(tmp_path, replay):
    run(tmp_path, Script([{"ok": True}])).run()
    path = tmp_path / "calls/annotation/chain.json"
    value = read_json(path)
    value["version"] = "skillflow-structural-correction-v4"
    path.write_text(json.dumps(value), encoding="utf-8")
    unused = Script([])
    with pytest.raises(ResponseChainError, match="protocol"):
        run(tmp_path, unused, replay=replay).run()
    assert unused.prompts == []


def test_only_current_diagnostic_family_selects_examples():
    first = union_error({"refs": [{"block_id": "b"}]}).diagnostics
    assert context(correction_prompt(BASE, {"refs": []}, first))["format_examples"]
    second = [{"code": "shape", "path": "/ok", "message": "A Boolean is required"}]
    latest = context(correction_prompt(BASE, {"bad": 2}, second))
    assert latest["format_examples"] == [] and latest["diagnostics"] == second
