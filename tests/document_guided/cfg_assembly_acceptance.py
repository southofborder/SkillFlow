"""Inject source-bound upstream answers and inspect the real processing handoff."""
from collections import Counter
from copy import deepcopy
import json

from skillflow.common.delivery_size import inspect_delivery
from skillflow.common.inputs.snapshot import read_snapshot
from skillflow.common.recording import canonical_sha256
from skillflow.document_guided import runner
from skillflow.document_guided.fragment_display import fragment_prompt_parts
from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.processing_display import _parts
from skillflow.document_guided.source import prompt_cfg, render_source, source_packet
from skillflow.lean_renderer import renderer_path
from tools.doe.document_guided_client import ENVELOPE, MAX_INPUT_CHARS


def read(path):
    return json.loads(path.read_bytes())


def split_ingress(old):
    """The fixture explicitly associates the selected value and incoming keys with its outputs."""
    first, *tail = deepcopy(old["operations"])
    selected, *keys = first["inputs"]
    selected_name, *acquired = first["outputs"]
    assert set(selected) == {"result"} and all(set(k) == {"context_key"} for k in keys)
    assert first["opcode"] == "receive" and len(keys) == len(acquired)
    first.update(inputs=keys, outputs=acquired)
    selector = {"ref": first["ref"] + ".selected", "opcode": "value", "inputs": [selected],
                "outputs": [selected_name], "source": deepcopy(first["source"])}
    return split_at_acquisition(old, first, [selector, *tail])


def split_at_acquisition(old, first, rest):
    body = {**deepcopy(old), "ref": old["ref"] + ".body", "source_kind": "normal", "operations": rest}
    entry = {**deepcopy(old), "operations": [first],
             "exit": {"kind": "jump", "target": body["ref"], "source": deepcopy(first["source"])}}
    return [entry, body]


def source_reads(facts):
    return Counter((p["context_key"], op["source"]["file"], op["source"]["start_line"], op["source"]["end_line"])
                   for block in facts["blocks"] for op in block["operations"] for p in op["inputs"]
                   if "context_key" in p)


def effect_trace(operations):
    """Expose inline/context receive reads once, at their original point in the effect sequence."""
    trace = []
    for op in operations:
        keys = [v["context_key"] for v in op["inputs"] if "context_key" in v]
        trace.extend(("context_key", key, op["source"]) for key in keys)
        if keys and (op.get("role") or op["opcode"]) == "receive":
            continue
        for action in op.get("source_actions") or [{"ref": op["ref"], "kind": op["opcode"],
                                                     "role": op.get("role"), "source": op["source"]}]:
            role = action.get("role") or action["kind"]
            if role in {"call", "read", "write", "deliver", "receive"}:
                trace.append((role, action["ref"], action["source"]))
    return trace


def run_to_processing(package, run, *, facts, task, flow, repair_blocks):
    """Stop at the injected processing client after verifying its actual delivered material."""
    runner.prepare(package, run_dir=run)
    _, source, _ = read_snapshot(run / "source")
    files = {"skill/" + row["path"]: row["content"] for row in source["files"]}
    assembly = assemble_graph_facts(facts, files=files)
    observed = {}
    calls = []
    original = {b["ref"]: b for b in facts["blocks"]}
    corrections = {ref: fn(deepcopy(original[ref])) for ref, fn in repair_blocks.items()}
    corrected_facts = {**facts, "blocks": [b for old in facts["blocks"]
                                           for b in corrections.get(old["ref"], [old])]}
    assert source_reads(corrected_facts) == source_reads(facts)
    for ref, rows in corrections.items():
        previous = original[ref]
        assert effect_trace(previous["operations"]) == effect_trace(op for row in rows for op in row["operations"])
        assert previous["exit"] == rows[-1]["exit"]
        for row, successor in zip(rows, rows[1:]):
            assert row["exit"]["kind"] == "jump" and row["exit"]["target"] == successor["ref"]

    class InjectedClient:
        def __init__(self, stage):
            self.stage = stage

        def complete(self, prompt):
            calls.append(self.stage)
            if self.stage == "task":
                return deepcopy(task)
            if self.stage == "flow":
                return flow
            if self.stage == "graph":
                if calls.count("graph") == 1:
                    return deepcopy(facts)
                assert calls.count("graph") == 2
                plan = fragment_prompt_parts(prompt)[1]["scope"]
                assert len(plan["slots"]) == len(corrections)
                assert {s["target"] for s in plan["slots"].values()} == set(corrections)
                assert all(s["kind"] == "action_region" for s in plan["slots"].values())
                return {"plan_sha256": plan["plan_sha256"], "updates": [
                    {"slot_id": sid, "value": deepcopy(corrections[s["target"]])}
                    for sid, s in plan["slots"].items()]}
            assert self.stage == "processing", self.stage
            cfg = read(run / "graph/initial.json")["cfg"]
            packet = source_packet(files)
            payload = _parts(prompt)[1]
            assert payload["cfg"] == prompt_cfg(cfg, packet=packet)
            assert render_source(packet) in prompt
            irs = [i["id"] for b in cfg["blocks"].values() for i in b["instructions"]]
            listed = json.loads(prompt.split("\nREQUIRED_IR_IDS\n", 1)[1].splitlines()[0])
            assert listed == irs
            delivery = inspect_delivery(prompt, prefix=ENVELOPE, max_characters=MAX_INPUT_CHARS)
            assert delivery["status"] == "within_limit", delivery
            observed.update(blocks=len(cfg["blocks"]), instructions=len(irs),
                            processing_delivery=delivery, cfg_sha256=canonical_sha256(cfg))
            raise KeyboardInterrupt("Offline fixture completed its processing-input assertions.")

    result = runner.run(run, client_factory=lambda stage, owner: InjectedClient(stage), renderer=renderer_path())
    assert result["status"] == "interrupted" and result["stages"]["graph"]["status"] == "complete", result
    assert Counter(calls) == {"task": 1, "flow": 1, "graph": 2, "processing": 1}
    assert (run / "steps/processing/calls/a001/request.json").is_file()
    value = read(run / "steps/graph/value.json")
    assert value["assembly"]["facts"] == corrected_facts
    assert not value["assembly"]["gaps"] and not value["assembly"]["patch_diagnostics"]
    certificate = read(run / "graph/initial/controlled.json")
    assert certificate["graph_sha256"] == observed["cfg_sha256"]
    return {**observed, "source_sha256": source["source_sha256"], "injected_calls": dict(Counter(calls)),
            "native_model_starts": 0, "processing_answer_requested_from_fixture": True,
            "processing_answer_provided": False, "source_files": len(files),
            "authored_blocks": len(facts["blocks"]), "authored_operations": sum(len(b["operations"]) for b in facts["blocks"]),
            "original_context_reads": sum(source_reads(facts).values()),
            "repaired_context_reads": sum(source_reads(corrected_facts).values()),
            "program_layout": assembly.block_layout, "injected_region_updates": list(corrections),
            "lean_units": len(certificate["units"]), "lean_derived_links": len(certificate["derived_links"]),
            "lean_graph_sha256": certificate["graph_sha256"], "lean_certificate_sha256": canonical_sha256(certificate["certificate"])}
