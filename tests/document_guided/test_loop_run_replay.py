"""Seven injected text answers exercise saved loop propagation and zero-call replay."""
from copy import deepcopy
import json

from skillflow.document_guided import runner
from skillflow.document_guided.fragments import split_fragments
from skillflow.document_guided.online import read
from skillflow.graph.extraction.compiler import compile_candidate
from tests.document_guided.test_ga4_explicit_loops import batch_projection
from tests.document_guided.test_parallel_runner import _cfg_wire, freeze_producer


def loop_answers():
    material, wire = batch_projection(["https://one.example", "https://two.example"])
    cfg = material["cfg"]
    candidate = {"entry_block_ref": cfg["entry_block_id"], "blocks": [], "edges": [],
                 "constraints": cfg.get("constraints", [])}
    for key, block in cfg["blocks"].items():
        candidate["blocks"].append({"block_ref": key, "block_name": block["block_name"],
            "data_source_kind": block.get("data_source_kind"), "constraints": block.get("constraints", []),
            "instructions": [{"instruction_ref": ir["id"],
                **{k: deepcopy(v) for k, v in ir.items() if k != "id"}}
                for ir in block["instructions"]]})
    candidate["edges"] = [{"source_block_ref": edge["source_block_id"],
        "target_block_ref": edge["target_block_id"], "condition_text": edge.get("condition_text")}
        for edge in cfg["edges"]]
    result = compile_candidate(candidate)
    assert result.ok, result.diagnostics
    identities = dict(zip(cfg["blocks"], result.cfg.blocks))
    identities.update(zip(
        [ir["id"] for block in cfg["blocks"].values() for ir in block["instructions"]],
        [ir.id for block in result.cfg.blocks.values() for ir in block.instructions]))

    def remap(value):
        if isinstance(value, dict):
            return {identities.get(key, key): remap(item) for key, item in value.items()}
        if isinstance(value, list):
            return [remap(item) for item in value]
        return identities.get(value, value) if isinstance(value, str) else value

    task = {key: material["task"][key] for key in ("purpose", "requirements", "issues")}
    return material["source"], _cfg_wire(candidate), task, split_fragments(remap(wire))


def test_loop_seven_calls_saved_outputs_and_zero_model_replay(tmp_path, monkeypatch):
    freeze_producer(monkeypatch)
    monkeypatch.setattr(runner, "_certificate", lambda *args, **kwargs: None)
    source, graph, task, fragments = loop_answers()
    package, directory = tmp_path / "package", tmp_path / "run"
    package.mkdir()
    for row in source["files"]:
        path = package / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(row["content"].encode("utf-8"))
    runner.prepare(package, run_dir=directory, config={"reasoning_effort": "high"})
    calls = []

    class Client:
        def __init__(self, stage):
            self.stage = stage

        def complete(self, prompt):
            calls.append(self.stage)
            if self.stage == "flow":
                return "# Flow\nTraverse the supplied URL occurrences, call the API, and collect normal results."
            value = task if self.stage == "task" else graph if self.stage == "graph" else (
                {"outcome": "completed", "findings": []} if self.stage == "review" else fragments[self.stage])
            return json.dumps(value, ensure_ascii=False)

    result = runner.run(directory, client_factory=lambda stage, owner: Client(stage))
    assert result["status"] in {"complete", "partial"}, result
    assert len(calls) == result["counts"]["logical_calls"] == 7
    assert result["counts"]["structural_corrections"] == 0
    assert not result["repair_used"]
    assert read(directory / "propagation/manifest.json")["status"] == "complete"
    assert (directory / "doe/doe-result.json").exists()
    responses = {str(path.relative_to(directory)): path.read_bytes()
                 for path in directory.rglob("response.json")}
    assert runner.replay(directory) == result
    assert len(calls) == 7
    assert responses == {str(path.relative_to(directory)): path.read_bytes()
                         for path in directory.rglob("response.json")}
