"""Check the new diagnostics against the original, unedited GA4 model responses."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
from skillflow.common.artifact_io import file_sha256
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.document_guided.fragment_revision import _current_joins
from skillflow.document_guided.fragment_wire import expand_processing_response
from skillflow.document_guided.graph_steps import GraphFactsCorrection
from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import plan_graph_repair
from skillflow.propagation.contracts.task import task_source_files
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS


def inspect(directory):
    graph_path = directory / "steps/graph/calls/a001/response.json"
    processing_path = directory / "steps/processing/calls/a001/response.json"
    fixture = json.loads((ROOT / "tests/fixtures/ga4_entry_occurrences/regression.json").read_bytes())
    graph_text = json.loads(graph_path.read_bytes())
    processing_text = json.loads(processing_path.read_bytes())
    assert hashlib.sha256(graph_text.encode()).hexdigest() == fixture["graph_reply_sha256"]
    assert hashlib.sha256(processing_text.encode()).hexdigest() == fixture["processing_reply_sha256"]
    raw = json.loads(graph_text)
    original_blocks = {b["ref"]: b for b in raw["blocks"]}
    assert all(original_blocks[b["ref"]] == b for b in fixture["graph_excerpt"]["blocks"])
    fragment = expand_processing_response(processing_text)
    for field, values in fixture["processing_excerpt"].items():
        if isinstance(values, dict):
            assert all(fragment[field][key] == val for key, val in values.items())
        else:
            assert all(val in fragment[field] for val in values)
    source = read_snapshot(directory / "source")[1]
    files = task_source_files(source)
    draft = assemble_graph_facts(raw, files=files)
    assert draft.cfg is None
    plan = plan_graph_repair(draft, files=files)
    region, = [slot for slot in plan["slots"].values() if slot["kind"] == "occurrence_region"]
    covered = [raw["blocks"][i]["ref"] for i in region["block_indices"]]
    assert {"public_entry", "select.reports", "reports.prepare"} <= set(covered)
    correction_size = len(ENVELOPE + GraphFactsCorrection(files).build_prompt("", raw, draft.gaps))
    assert correction_size <= MAX_INPUT_CHARS
    graph = json.loads((directory / "graph/revision.json").read_bytes())["cfg"]
    old = json.loads((directory / "revision/processing-scope.json").read_bytes())
    join = _current_joins(graph, old["slots"])["block_125"]
    assert join["input_producers"]["ir_262"]["1"]["reachable_predecessors"] == ["block_171"]
    return {"source_sha256": source["source_sha256"], "source_files": len(files),
            "graph_artifact_sha256": file_sha256(graph_path), "processing_artifact_sha256": file_sha256(processing_path),
            "original_blocks": len(raw["blocks"]), "correction_delivery_chars": correction_size,
            "diagnostics": [d["code"] for d in draft.gaps], "repair_blocks": covered,
            "original_revised_merge": "ir_262", "current_join": join, "new_model_calls": 0}


if __name__ == "__main__":
    previous = ROOT / "experiments/doe/runs/document-guided-ga4-cfg-assembly-high-20261123-234230"
    print(json.dumps(inspect(previous), indent=2))
