"""Seven real local stages retain independent DOE beside an unknown write."""
from copy import deepcopy
import json

import pytest

from skillflow.document_guided import runner
from skillflow.document_guided.fragments import split_fragments
from skillflow.document_guided.online import read
from skillflow.graph.extraction.compiler import compile_candidate
from tests.document_guided.test_parallel_runner import _flat, _cfg_wire, freeze_producer
from tests.doe.test_processing_limits import authored


def fixture(shared_cache=False):
    material, raw = authored(shared_cache=shared_cache)
    cfg = material["cfg"]
    candidate = {"entry_block_ref": cfg["entry_block_id"], "blocks": [], "edges": [],
                 "constraints": cfg.get("constraints", [])}
    for key, block in cfg["blocks"].items():
        candidate["blocks"].append({"block_ref": key, "block_name": block["block_name"],
            "data_source_kind": block["data_source_kind"], "constraints": block["constraints"],
            "instructions": [{"instruction_ref": ir["id"],
                              **{k: deepcopy(v) for k, v in ir.items() if k != "id"}}
                             for ir in block["instructions"]]})
    for edge in cfg["edges"]:
        candidate["edges"].append({"source_block_ref": edge["source_block_id"],
            "target_block_ref": edge["target_block_id"], "condition_text": edge["condition_text"]})
    compiled = compile_candidate(candidate)
    assert compiled.ok, compiled.diagnostics
    before = [ir["id"] for block in cfg["blocks"].values() for ir in block["instructions"]]
    after = [ir.id for block in compiled.cfg.blocks.values() for ir in block.instructions]
    identities = dict(zip(before, after))

    def remap(value):
        if isinstance(value, dict):
            return {identities.get(k, k): remap(v) for k, v in value.items()}
        if isinstance(value, list):
            return [remap(item) for item in value]
        return identities.get(value, value) if isinstance(value, str) else value

    raw = remap(raw)
    wire = _flat(raw)
    wire["processing_gaps"] = raw["processing_gaps"]
    task = {key: material["task"][key] for key in ("purpose", "requirements", "issues")}
    return material["source"], _cfg_wire(candidate), task, split_fragments(wire), identities


@pytest.mark.parametrize("shared_cache", [False, True])
def test_source_gap_seven_text_answers_saved_backend_and_replay(tmp_path, monkeypatch, shared_cache):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    source, graph, task, fragments, identities = fixture(shared_cache)
    package, directory = tmp_path / "package", tmp_path / "run"
    package.mkdir()
    for row in source["files"]:
        target = package / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(row["content"].encode("utf-8"))
    runner.prepare(package, run_dir=directory, config={"reasoning_effort": "high"})
    calls = []

    class Client:
        def __init__(self, name):
            self.name = name

        def complete(self, prompt):
            calls.append(self.name)
            if self.name == "flow":
                return "# Flow\nKeep the independent return and unsupported cache write. skill/SKILL.md:1-5"
            value = task if self.name == "task" else graph if self.name == "graph" else (
                {"outcome": "completed", "findings": []} if self.name == "review" else fragments[self.name])
            return json.dumps(value, ensure_ascii=False)

    result = runner.run(directory, client_factory=lambda name, owner: Client(name))
    assert result["status"] == "partial", result
    assert len(calls) == result["counts"]["logical_calls"] == 7
    assert not result["repair_used"] and result["counts"]["structural_corrections"] == 0
    assert (directory / "doe/doe-result.json").exists()
    propagation = read(directory / "propagation/manifest.json")
    assert propagation["status"] == "incomplete"
    # The saved deterministic report contains the same substantive result as
    # the solver-only regression: no reduction beside a shared unknown write.
    reviews = []
    for path in (directory / "doe").rglob("*.json"):
        value = read(path)
        for sink in value.get("sinks", []):
            if sink.get("boundary", {}).get("instruction_id") == identities["ir_filter"]:
                reviews.extend(sink.get("data_reviews", []))
    assert reviews
    assert any(row["conclusion"] == "excess_supported" for row in reviews) is (not shared_cache)
    before = {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("response.json")}
    assert runner.replay(directory) == result
    assert len(calls) == 7
    assert before == {str(path.relative_to(directory)): path.read_bytes() for path in directory.rglob("response.json")}
