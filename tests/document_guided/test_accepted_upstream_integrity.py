"""Synthetic accepted artifacts retain complete source and actual response proof."""
from copy import deepcopy
import json
import shutil

import pytest

from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256, sha_file
from skillflow.document_guided import accepted_upstream, runner
from skillflow.document_guided.online import inventory, prepare_step, read, run_step, seal
from tests.document_guided.test_accepted_upstream import Downstream, parent_run
from tests.document_guided.test_parallel_runner import Harness, freeze_producer, graph_facts_fixture, prompt_scope


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)


def write(path, value):
    runner.WRITER.json(path, value)


def reseal_manifest(path, change):
    value = read(path)
    value.pop("manifest_sha256")
    change(value)
    write(path, seal(value))


def reseal_chain(owner):
    chain = read(owner / "calls/chain.json")
    for row in chain["attempts"]:
        call = owner / row["call"]
        row["request_sha256"] = canonical_sha256(read(call / "request.json"))
        row["call_sha256"] = sha_file(call / "call.json")
        row["validation_sha256"] = canonical_sha256(read(call / "validation.json"))
    write(owner / "calls/chain.json", chain)
    result = read(owner / "result.json")
    result["response_chain_sha256"] = canonical_sha256(chain)
    write(owner / "result.json", result)


def old_stage(owner):
    reseal_manifest(owner / "manifest.json", lambda value: value.update(identity="skillflow-document-step-v13"))
    chain = read(owner / "calls/chain.json")
    if "correction_strategy" in chain:
        chain["correction_strategy"] = chain["correction_strategy"].replace("fragments-v9:", "fragments-v8:")
    write(owner / "calls/chain.json", chain)
    for row in chain["attempts"]:
        path = owner / row["call"] / "request.json"
        value = read(path)
        if "correction_strategy" in value:
            value["correction_strategy"] = chain["correction_strategy"]
        write(path, value)
    result = read(owner / "result.json")
    result["identity"] = "skillflow-document-step-v13"
    write(owner / "result.json", result)
    reseal_chain(owner)


def stage(tmp_path, *, corrected=False, normalized=False, kind="graph_facts_v1"):
    harness = Harness(tmp_path / "donor")
    harness.prepare(tmp_path / "package")
    source = read_snapshot(harness.directory / "source")[1]
    owner = harness.directory / "steps" / ("flow" if kind == "flow_document" else "graph")
    prepare_step(owner, "Complete synthetic source and operation specification.", kind=kind,
        context={"source_owner": harness.directory / "source"},
        dependencies=[harness.directory / "source/manifest.json"], max_corrections=1)
    if kind == "flow_document":
        answers = ["Complete source-supported flow."]
    else:
        initial = graph_facts_fixture(harness.graph) if kind == "graph_facts_v1" else deepcopy(harness.graph)
        if corrected:
            if kind == "graph_facts_v1":
                initial["entry"] = "missing_block"
                def correction(prompt):
                    plan = prompt_scope(prompt)
                    slot, = plan["slots"].values()
                    return {"plan_sha256": plan["plan_sha256"], "updates": [
                        {"slot_id": slot["slot_id"], "value": harness.graph["entry_block_ref"]}]}
                answers = [json.dumps(initial), correction]
            else:
                initial["entry_block_ref"] = "missing_block"
                answers = [json.dumps(initial), json.dumps({"replacements": [{"record_id": "/entry_block_ref", "value": harness.graph["entry_block_ref"]}]})]
        else:
            answers = [json.dumps(initial) + ("}" if normalized else "")]
    class Client:
        def complete(self, prompt):
            answer = answers.pop(0)
            return answer(prompt) if callable(answer) else answer
    expected = run_step(owner, client=Client())
    assert not answers
    return owner, source, expected


@pytest.mark.parametrize("old", [False, True])
@pytest.mark.parametrize("mode", ["first", "corrected", "normalized", "flow"])
def test_supported_old_and_current_accepted_chains_are_pure_readers(tmp_path, monkeypatch, old, mode):
    kind = "flow_document" if mode == "flow" else "cfg_wire_v5" if old else "graph_facts_v1"
    owner, source, expected = stage(tmp_path, corrected=mode == "corrected", normalized=mode == "normalized", kind=kind)
    if old:
        old_stage(owner)
    before = inventory(owner)
    monkeypatch.setattr("skillflow.document_guided.online.run_step", lambda *args, **kwargs: pytest.fail("Saved stage runner invoked"))
    monkeypatch.setattr("skillflow.common.structural_correction.ResponseChain.run", lambda *args, **kwargs: pytest.fail("Response chain runner invoked"))
    assert accepted_upstream._accepted_step(owner, kind=kind, config=read(owner / "manifest.json")["config"], source=source) == expected
    assert inventory(owner) == before


@pytest.mark.parametrize("defect", ["cached_value", "unknown_status", "partial_status", "producer", "request_previous", "transport_response", "validation_status", "normalization", "extra_call"])
def test_resealed_but_inconsistent_accepted_stage_is_rejected(tmp_path, defect):
    owner, source, _ = stage(tmp_path)
    if defect == "cached_value":
        value = read(owner / "value.json")
        value["cfg"]["blocks"]["block_001"]["block_name"] = "Changed cached name without a model answer"
        write(owner / "value.json", value)
        result = read(owner / "result.json"); result["value_sha256"] = sha_file(owner / "value.json"); write(owner / "result.json", result)
    elif defect.endswith("status") and defect != "validation_status":
        result = read(owner / "result.json"); result["status"] = "partial" if defect == "partial_status" else "request_failure"; write(owner / "result.json", result)
    elif defect == "producer":
        reseal_manifest(owner / "manifest.json", lambda value: value.update(identity="skillflow-document-step-v999"))
    elif defect == "request_previous":
        path = owner / "calls/a001/request.json"; value = read(path); value["previous"] = {"call": "another"}; write(path, value); reseal_chain(owner)
    elif defect == "transport_response":
        path = owner / "calls/a001/transport.json"; value = json.loads(path.read_text()); value[0]["response"] = "Changed response"; value[0].pop("record_sha256"); value[0]["record_sha256"] = canonical_sha256(value[0]); write(path, value)
    elif defect == "validation_status":
        path = owner / "calls/a001/validation.json"; value = read(path); value["status"] = "structural_invalid"; write(path, value); reseal_chain(owner)
    elif defect == "normalization":
        write(owner / "calls/a001/normalization.json", {"invented": True})
    else:
        (owner / "calls/a002").mkdir()
    with pytest.raises(ValueError):
        accepted_upstream._accepted_step(owner, kind="graph_facts_v1", config=read(owner / "manifest.json")["config"], source=source)


def test_graph_must_depend_on_exact_selected_flow_before_creating_child(tmp_path):
    parent = parent_run(tmp_path)
    other = parent.directory / "other-flow"
    shutil.copytree(parent.directory / "steps/flow", other)
    graph = parent.directory / "steps/graph/manifest.json"
    from skillflow.document_guided.online import file_reference
    reseal_manifest(graph, lambda value: value["dependencies"].__setitem__(1, file_reference(graph.parent, other / "result.json")))
    child = tmp_path / "child"
    with pytest.raises(ValueError, match="dependencies differ"):
        runner.prepare_from_accepted_cfg(parent.directory, run_dir=child)
    assert not child.exists()


def test_all_source_names_survive_infrastructure_exclusions(tmp_path):
    parent = Harness(tmp_path / "parent")
    package = tmp_path / "source"; package.mkdir()
    (package / "SKILL.md").write_text(parent.example["source"], encoding="utf-8")
    names = ["report.md", "execution-boundary.json", "replay/note.md"]
    for name in names:
        path = package / name; path.parent.mkdir(exist_ok=True, parents=True); path.write_text("Complete additional source evidence.", encoding="utf-8")
    runner.prepare(package, run_dir=parent.directory)
    assert runner.run(parent.directory, client_factory=parent.factory)["status"] == "complete"
    child = tmp_path / "child"
    runner.prepare_from_accepted_cfg(parent.directory, run_dir=child)
    for name in names:
        assert (child / "source/inputs/package" / name).read_bytes() == (package / name).read_bytes()


def test_source_copy_inventory_keeps_a_legitimate_nested_lock_filename(tmp_path):
    source = tmp_path / "source"
    path = source / "inputs/package/.runner.lock"
    path.parent.mkdir(parents=True); path.write_text("Source content, not an infrastructure lock.", encoding="utf-8")
    files = {}
    accepted_upstream._collect_tree(tmp_path, source, files, source=True)
    assert files == {"source/inputs/package/.runner.lock": sha_file(path)}


def test_descendant_copies_and_verifies_full_lineage_receipts(tmp_path):
    parent = parent_run(tmp_path)
    child = Downstream(tmp_path / "child")
    runner.prepare_from_accepted_cfg(parent.directory, run_dir=child.directory)
    assert runner.run(child.directory, client_factory=child.factory)["status"] == "complete"
    grandchild = tmp_path / "grandchild"
    runner.prepare_from_accepted_cfg(child.directory, run_dir=grandchild)
    assert (grandchild / "inherited/accepted-upstream.json").read_bytes() == (child.directory / "accepted-upstream.json").read_bytes()
    assert accepted_upstream.load_accepted_upstream(grandchild)
    receipt = read(grandchild / "accepted-upstream.json")
    assert "inherited/accepted-upstream.json" in receipt["copied_files"]


def test_donor_root_result_identity_must_match_its_manifest(tmp_path):
    parent = parent_run(tmp_path)
    result = read(parent.directory / "result.json")
    result["identity"] = "unsupported-guided-result"
    write(parent.directory / "result.json", result)
    with pytest.raises(ValueError, match="identity"):
        runner.prepare_from_accepted_cfg(parent.directory, run_dir=tmp_path / "child")
    assert not (tmp_path / "child").exists()
