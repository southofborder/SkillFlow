"""Archived v15 graph corrections keep their original display and evidence."""
import json

import pytest

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.prompt_format import compact_json, render_prompt_format
from skillflow.common.recording import canonical_sha256
from skillflow.document_guided import accepted_stage_reader, graph_steps, online
from skillflow.document_guided.graph_slots import GRAPH_UPDATES_SCHEMA
from skillflow.document_guided.prompts import _render, build_graph_facts_prompt
from skillflow.document_guided.source import source_packet
from tests.document_guided.test_accepted_upstream_integrity import reseal_chain, write
from tests.document_guided.test_parallel_runner import (
    Harness, freeze_producer, graph_facts_fixture, prompt_scope,
)


def archived_v15_prompt(strategy, base_prompt, candidate, diagnostics):
    """Author the fixture with the exact renderer shipped for v15."""
    plan = strategy._plan(candidate)["plan"]
    return _render("Supply only the listed, missing or challenged graph facts.",
        "AUTHORIZED GRAPH SLOTS\n" + compact_json(plan),
        "Inputs, outputs, conditions and effects at the region boundary are frozen. Check the complete source. "
        "Return updates only for facts supported by the source. Leave unsupported slots unfilled; never rewrite "
        "the graph, change an unlisted slot, or invent an effect.",
        source_packet(strategy.files), "GRAPH UPDATES FORMAT\n" + render_prompt_format(GRAPH_UPDATES_SCHEMA))


def corrected_stage(tmp_path, monkeypatch, *, archived):
    freeze_producer(monkeypatch)
    harness = Harness(tmp_path / "donor")
    harness.prepare(tmp_path / "package")
    source = read_snapshot(harness.directory / "source")[1]
    files = {"skill/" + row["path"]: row["content"] for row in source["files"]}
    base = build_graph_facts_prompt(files=files, documents={"flow": "Read and return the source value."},
        global_requirements="Preserve source-supported control and data references.")
    owner = harness.directory / "steps/graph"
    initial = graph_facts_fixture(harness.graph)
    initial["entry"] = "missing-block"
    calls = []

    class Client:
        def complete(self, prompt):
            calls.append(prompt)
            if len(calls) == 1:
                return json.dumps(initial)
            if archived:
                marker = "AUTHORIZED GRAPH SLOTS\n"
                plan = json.JSONDecoder().raw_decode(prompt.split(marker, 1)[1])[0]
            else:
                plan = prompt_scope(prompt)
            slot, = plan["slots"].values()
            return {"plan_sha256": plan["plan_sha256"], "updates": [
                {"slot_id": slot["slot_id"], "value": harness.graph["entry_block_ref"]}]}

    with monkeypatch.context() as producing:
        if archived:
            producing.setattr(online, "STEP_IDENTITY", "skillflow-document-step-v15")
            producing.setattr(graph_steps.GraphFactsCorrection, "build_prompt", archived_v15_prompt)
        online.prepare_step(owner, base, kind=graph_steps.FACTS,
            context={"source_owner": harness.directory / "source"},
            dependencies=[harness.directory / "source/manifest.json"], max_corrections=1)
        expected = online.run_step(owner, client=Client())
    assert len(calls) == 2
    marker = "AUTHORIZED GRAPH SLOTS\n" if archived else "FRAGMENT_INPUT_JSON\n"
    assert marker in calls[1]
    return owner, source, expected


def forbid_execution(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("An accepted artifact reader must only read its recorded evidence")

    monkeypatch.setattr(online, "run_step", fail)
    monkeypatch.setattr("skillflow.common.structural_correction.ResponseChain.run", fail)


@pytest.mark.parametrize("archived", [True, False])
def test_archived_and_current_graph_correction_displays_are_exact_pure_reads(tmp_path, monkeypatch, archived):
    owner, source, expected = corrected_stage(tmp_path, monkeypatch, archived=archived)
    before = online.inventory(owner)
    forbid_execution(monkeypatch)
    if not archived:
        monkeypatch.setattr(accepted_stage_reader, "_v15_graph_correction_prompt",
            lambda *args: pytest.fail("The current stage must keep its current renderer"))
    assert accepted_stage_reader.accepted_stage_value(owner, online.read(owner / "manifest.json"), source=source) == expected
    assert online.inventory(owner) == before


def test_rehashed_altered_v15_correction_prompt_is_rejected(tmp_path, monkeypatch):
    owner, source, _ = corrected_stage(tmp_path, monkeypatch, archived=True)
    call_dir = owner / "calls/a002"
    prompt = (call_dir / "prompt.txt").read_bytes().decode("utf-8") + "\nAltered instruction."
    (call_dir / "prompt.txt").write_bytes(prompt.encode("utf-8"))
    call = online.read(call_dir / "call.json")
    call.update(prompt=prompt, prompt_sha256=canonical_sha256(prompt))
    write(call_dir / "call.json", call)
    trace = json.loads((call_dir / "transport.json").read_bytes())
    for record in trace:
        record["prompt"] = prompt
        record.pop("record_sha256", None)
        record["record_sha256"] = canonical_sha256(record)
    write(call_dir / "transport.json", trace)
    request = online.read(call_dir / "request.json")
    request["prompt_sha256"] = canonical_sha256(prompt)
    write(call_dir / "request.json", request)
    reseal_chain(owner)
    before = online.inventory(owner)
    forbid_execution(monkeypatch)
    with pytest.raises(ValueError, match="correction prompt is unsupported or changed"):
        accepted_stage_reader.accepted_stage_value(owner, online.read(owner / "manifest.json"), source=source)
    assert online.inventory(owner) == before
