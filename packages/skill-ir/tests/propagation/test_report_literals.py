"""Real CFG literals may retain identifier:null; reports must use literal_value."""
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import runpy
import socket

import pytest

from skill_ir.propagation import propagate
from skill_ir.propagation.handoff import load_doe_input
from skill_ir.propagation.report import _operands, render_html, render_markdown
from skill_ir.propagation.runner import load_propagation_run, replay_propagation, save_propagation_run
from skill_ir.recording import read_json
from skill_ir.security_profile.evidence import prepare_material
from skill_ir.security_profile.services import compile_response, to_payload


LITERALS = [None, True, False, 0, [], {}, "recipient", '中文 <tag> & "quote" | \\ newline\nnext']


@pytest.mark.parametrize("value", LITERALS)
@pytest.mark.parametrize("include_identifier", [False, True])
def test_literal_operand_uses_json_value_even_when_identifier_is_explicit_null(value, include_identifier):
    operand = {"type": "literal", "literal_value": value}
    if include_identifier:
        operand["identifier"] = None
    before = deepcopy(operand)
    assert _operands([operand]) == "0: " + json.dumps(value, ensure_ascii=False)
    assert operand == before


def test_operand_display_preserves_reference_identifier_and_repeated_positions():
    values = [{"type": "result", "identifier": "result_017"},
              {"type": "external_resource", "identifier": "archive.fetch"},
              {"type": "context_key", "identifier": "caller_request"},
              {"type": "result", "identifier": "result_017"}]
    assert _operands(values) == "0: result_017, 1: archive.fetch, 2: caller_request, 3: result_017"


def literal_run_inputs():
    example = runpy.run_path(str(Path(__file__).resolve().parents[2] / "examples/propagation_demo.py"))
    instruction, input_ref = example["instruction"], example["input_ref"]
    cfg = {"entry_block_id": "main", "blocks": {"main": {"block_id": "main", "block_name": "literal values", "instructions": [
        instruction("literals", [{"type": "literal", "identifier": None, "literal_value": value} for value in LITERALS],
                    ["value_" + str(i) for i in range(len(LITERALS))]),
        instruction("return", opcode="return")]}}, "edges": []}
    cfg, response = example["fixture_annotation"](
        cfg, {"literals": ([], [], [input_ref(i) for i in range(len(LITERALS))])}, return_response=True)
    source, metadata = example["demo_source"]()
    annotation = to_payload(response)
    material = prepare_material(source, cfg)
    solved = propagate(cfg, annotation)
    assert solved.status == "complete"
    return material, metadata, response, annotation, solved


def test_literal_null_identifiers_survive_full_save_load_and_zero_api_replay(tmp_path, monkeypatch):
    import skill_ir.recording as recording

    def forbidden(*args, **kwargs):
        pytest.fail("literal report save/load/replay attempted a network operation")
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(recording, "streaming_factory", forbidden)
    material, metadata, response, annotation, solved = literal_run_inputs()
    authored_raw = deepcopy(response)
    authored_raw.pop("sink_boundaries")
    for spec in authored_raw["transfer_specs"].values():
        spec.pop("precedence")
    raw, compiled, compilation_map = compile_response(authored_raw, material)
    assert compiled == response
    directory = tmp_path / "literal-report-run"
    result = save_propagation_run(
        directory, material=material, source_metadata=metadata, annotation=annotation,
        location_evidences=response["location_evidences"], solved=solved,
        raw_annotation=raw, compilation_map=compilation_map,
        provenance={"kind": "hand_authored_specification", "notice": "Explicit offline regression fixture."},
    )
    assert (directory / "manifest.json").is_file()
    assert load_doe_input(directory / "doe-input.json") == result
    assert load_propagation_run(directory) == result
    assert replay_propagation(directory) == result
    receipt = read_json(directory / "replay/summary.json")
    assert receipt["status"] == "matched" and receipt["model_calls"] == 0
    assert not (directory / "replay/doe-input.json").exists()
    for ir in result["cfg"]["blocks"]["main"]["instructions"]:
        if ir["id"] == "ir_literals":
            assert [operand["literal_value"] for operand in ir["inputs"]] == LITERALS
            assert all("identifier" in operand and operand["identifier"] is None for operand in ir["inputs"])
    text = _operands(result["cfg"]["blocks"]["main"]["instructions"][0]["inputs"])
    assert "0: null, 1: true, 2: false, 3: 0, 4: [], 5: {}" in text
    assert '<tag>' in text
    for name, render in (("report.html", render_html), ("report.md", render_markdown)):
        rendered = render(result)
        expected = escape(text) if name.endswith("html") else escape(text).replace("|", "&#124;").replace("\n", " ")
        assert expected in rendered
        assert "<tag>" not in rendered and "&lt;tag&gt;" in rendered
        assert (directory / name).is_file() and (directory / "replay" / name).is_file()
