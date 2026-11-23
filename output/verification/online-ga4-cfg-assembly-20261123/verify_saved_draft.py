"""Inject the closed 117-block GA4 answer in a temporary offline guided run."""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

VERIFY = Path(__file__).resolve().parent
PROJECT = VERIFY.parents[2]
sys.path[:0] = [str(PROJECT / "src"), str(PROJECT)]

from skillflow.common.artifact_io import atomic_write_text, file_sha256
from skillflow.common.recording import canonical_sha256, implementation_provenance
from skillflow.document_guided.graph_facts import instruction_ref
from tests.document_guided.cfg_assembly_acceptance import read, run_to_processing, split_at_acquisition, split_ingress


HISTORY = PROJECT / "experiments/doe/runs/document-guided-ga4-action-alignment-high-20261123-214712"


def search_blocks(block):
    first, *rest = block["operations"]
    assert block["constraints"] == ["No explicit sorting is sent."]
    assert [op["ref"] for op in rest if op["ref"] == "search.invoke"] == ["search.invoke"]
    query = next(op for op in rest if op["ref"] == "search.invoke")
    assert query["source"] == {"file": "skill/scripts/src/api/searchConsole.ts", "start_line": 102, "end_line": 111}
    query["constraints"] = block.pop("constraints")
    return split_at_acquisition(block, first, rest)


def workflow_blocks(block):
    """Read each original raw input where it was consumed, including the later selected-file input."""
    chunks = []
    for op in deepcopy(block["operations"]):
        keyed = [v["context_key"] for v in op["inputs"] if "context_key" in v]
        if keyed:
            acquired = {key: f"fixture.{key}" for key in keyed}
            chunks.extend([("context", [{"ref": op["ref"] + ".input", "opcode": "receive",
                "inputs": [{"context_key": key} for key in keyed], "outputs": list(acquired.values()),
                "source": deepcopy(op["source"])}]), ("normal", [])])
            op["inputs"] = [{"result": acquired[v["context_key"]]} if "context_key" in v else v for v in op["inputs"]]
        chunks[-1][1].append(op)
    assert [kind for kind, _ in chunks] == ["context", "normal", "context", "normal"]
    names = [block["ref"], *(block["ref"] + f".part{i}" for i in range(2, len(chunks) + 1))]
    rows = []
    for i, (kind, ops) in enumerate(chunks):
        exit = (block["exit"] if i == len(chunks) - 1 else
                {"kind": "jump", "target": names[i + 1], "source": ops[-1]["source"]})
        rows.append({**deepcopy(block), "ref": names[i], "source_kind": kind, "operations": ops, "exit": exit})
    return rows


def verify_semantic_inventory(cfg, assembly):
    ids = assembly["id_map"]
    instructions = {i["draft_instruction_id"]: i for b in cfg["blocks"].values() for i in b["instructions"]}
    expected = set()
    source_keys = Counter()
    expected_edges = Counter()
    layout = assembly.get("block_layout", {})
    for block in assembly["facts"]["blocks"]:
        local = layout.get(block["ref"], {})
        start = ids["blocks"][block["ref"]]
        end = ids["blocks"][local["continuation"]] if local.get("continuation") else start
        if end != start:
            expected_edges[start, end, None] += 1
        assert cfg["blocks"][start]["constraints"] == block.get("constraints", [])
        exit = block["exit"]
        if exit["kind"] == "jump":
            expected_edges[end, ids["blocks"][exit["target"]], None] += 1
        elif exit["kind"] == "branch":
            for arm in exit["arms"]:
                expected_edges[end, ids["blocks"][arm["target"]], arm["condition"]] += 1
        carried_ops = [i["draft_instruction_id"] for i in cfg["blocks"][start]["instructions"]]
        if end != start:
            carried_ops = carried_ops[:-1] + [i["draft_instruction_id"] for i in cfg["blocks"][end]["instructions"]]
        assert carried_ops == [*[instruction_ref(block["ref"], op["ref"]) for op in block["operations"]],
                               instruction_ref(block["ref"])]
        expected.add(instruction_ref(block["ref"]))
        for op in block["operations"]:
            ref = instruction_ref(block["ref"], op["ref"])
            expected.add(ref)
            actual = instructions[ref]
            assert actual["opcode"] == op["opcode"]
            assert actual["metadata"]["source_span"] == op["source"]
            if "source_actions" in op:
                assert actual["metadata"]["source_actions"] == op["source_actions"]
            assert actual["constraints"] == op.get("constraints", [])
            assert [v["identifier"] for v in actual["outputs"]] == [ids["results"][n] for n in op["outputs"]]
            assert len(actual["inputs"]) == len(op["inputs"])
            for value, witness in zip(op["inputs"], actual["inputs"]):
                kind, payload = next(iter(value.items()))
                assert kind == witness["type"]
                if kind == "literal":
                    assert witness["literal_value"] == payload
                elif kind == "result":
                    assert witness["identifier"] == ids["results"][payload]
                else:
                    assert witness["identifier"] == payload
                    if kind == "context_key":
                        source_keys[payload] += 1
    extra = instructions.keys() - expected
    assert expected_edges == Counter((e["source_block_id"], e["target_block_id"], e["condition_text"]) for e in cfg["edges"])
    assert all(r.endswith("/continuation") for r in extra)
    for ref in extra:
        op = instructions[ref]
        assert op["opcode"] == "dispatch" and not op["inputs"] and not op["outputs"] and not op["metadata"]
    return {"source_operations_verified": sum(len(b["operations"]) for b in assembly["facts"]["blocks"]),
            "implicit_unconditional_transfers_verified": len(extra), "control_edges_verified": sum(expected_edges.values()),
            "compiled_context_keys": dict(source_keys)}


def verify(history, target):
    implementation = implementation_provenance()["sha256"]
    graph = history / "steps/graph/calls/a001/response.json"
    facts = json.loads(read(graph))
    assert len(facts["blocks"]) == 117
    repairs = dict.fromkeys(("realtime_entry", "metadata_entry", "notification_entry", "other_export"), split_ingress)
    repairs.update(document_workflow=workflow_blocks, search_entry=search_blocks)
    task_path = history / "task/calls/task/a001/response.json"
    flow_path = history / "steps/flow/calls/a001/response.json"
    result = run_to_processing(history / "source/inputs/package", target, facts=facts,
                               task=json.loads(read(task_path)), flow=read(flow_path), repair_blocks=repairs)
    assert Counter(x["kind"] for x in result["program_layout"].values()) == {"control": 25, "split": 18}
    assert result["source_files"] == 16 and result["authored_operations"] == 223
    assert result["original_context_reads"] == result["repaired_context_reads"]
    final = read(target / "steps/graph/value.json")
    result.update(verify_semantic_inventory(final["cfg"], final["assembly"]))
    owners = {op["ref"]: op for b in final["assembly"]["facts"]["blocks"] for op in b["operations"]}
    assert owners["search.invoke"]["constraints"] == ["No explicit sorting is sent."]
    for block in facts["blocks"]:
        if block["ref"] == "document_workflow":
            rows = [b for b in final["assembly"]["facts"]["blocks"]
                    if b["ref"] == block["ref"] or b["ref"].startswith(block["ref"] + ".")]
            assert all(b["constraints"] == block["constraints"] for b in rows)
    assert implementation_provenance()["sha256"] == implementation
    return {"status": "passed", "scope": "Offline injected graph correction and delivery to the normal processing client.",
            "implementation_sha256": implementation,
            "history_run": history.name, "input_digests": {p.relative_to(history).as_posix(): file_sha256(p)
            for p in (graph, task_path, flow_path)}, "initial_facts_sha256": canonical_sha256(facts), **result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=Path, default=HISTORY)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="skillflow-cfg-handoff-") as temp:
        receipt = verify(args.history.resolve(), Path(temp) / "run")
    output = json.dumps(receipt, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    if args.receipt:
        atomic_write_text(args.receipt, output)
    else:
        print(output, end="")
