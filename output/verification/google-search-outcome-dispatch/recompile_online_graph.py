"""Recompile the unedited first online GraphFacts after the handler fix, offline."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from skillflow.common.recording import implementation_provenance
from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.python_handlers import handler_transfers
from skillflow.document_guided.python_arguments import argument_transfers

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "google-search-call-routing-20261125"))
from check_entry_paths import describe


def read(path):
    return json.loads(path.read_bytes())


def write(name, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    dispatch = read(HERE / "dispatch.json")
    run = Path(dispatch["run"])
    source_path = run / "steps/graph/calls/a001/response.json"
    pin = sha256(source_path.read_bytes()).hexdigest()
    raw = read(source_path)
    facts = json.loads(raw) if isinstance(raw, str) else raw
    files = {}
    for name, signature in dispatch["files"].items():
        data = (run / "source/inputs/package" / name).read_bytes()
        assert sha256(data).hexdigest() == signature["sha256"]
        files["skill/" + name] = data.decode("utf-8")
    b = assemble_graph_facts(facts, files=files)
    assert b.cfg and not b.gaps, b.gaps
    assert from_accepted_cfg(b.cfg, files=files).cfg == b.cfg
    summary = describe(b.cfg)
    assert summary["all_checks_match"], summary["checks"]
    records = handler_transfers(b.cfg, files)
    gate = b.id_map["blocks"]["cli.catch_exception"]
    caught = b.id_map["blocks"]["cli.render_and_print_error"]
    outer = b.id_map["blocks"]["cli.unmatched_exception"]
    block = b.cfg["blocks"][gate]
    branch = records[block["instructions"][-1]["id"]]["segments"][0]["ops"][0]
    assert branch["true_target"] == caught and branch["false_target"] == outer
    assert branch["selector"]["tests"][0]["classes"] == ["Exception"]
    assert b.cfg["blocks"][outer]["instructions"][-1]["inputs"][0]["identifier"] == block["instructions"][0]["outputs"][0]["identifier"]
    assert len({edge["source_block_id"] for edge in b.cfg["edges"] if edge["target_block_id"] == gate}) == 5
    argument_records = argument_transfers(b.cfg)
    count_guard = b.id_map["instructions"]["/blocks/public.check_optional_argument/exit"]
    count_test = argument_records[count_guard]["segments"][0]["ops"][0]
    assert count_test["selector"] == {"path": [], "tests": [{"kind": "missing"}], "outcome": 1}
    assert count_test["true_target"] == b.id_map["blocks"]["public.supplied_count"]
    assert count_test["false_target"] == b.id_map["blocks"]["public.default_count"]
    entry = b.cfg["blocks"][b.id_map["blocks"]["public.acquire_arguments"]]["instructions"][0]
    assert 3 in entry["metadata"]["optional_context_inputs"] and not entry["metadata"].get("python_argument_defaults")
    counts = Counter(ir["opcode"] for bl in b.cfg["blocks"].values() for ir in bl["instructions"])
    assert len(facts["blocks"]) == len(b.cfg["blocks"]) == 50
    assert sum(1 + len(bl["operations"]) for bl in facts["blocks"]) == sum(counts.values()) == 84
    assert sha256(source_path.read_bytes()).hexdigest() == pin
    write("recompiled-online-cfg.json", b.cfg)
    write("recompiled-online-graph-verification.json", {
        "source": str(source_path), "response_file_sha256": pin, "model": read(run / "manifest.json")["config"],
        "original_implementation": read(run / "manifest.json")["implementation"]["sha256"],
        "compiler": implementation_provenance()["sha256"], "original_online_stage": "structural_failure",
        "category": "Unedited first online GraphFacts compiled offline with the corrected frontend; no online annotation selected.",
        "blocks": len(b.cfg["blocks"]), "IR": sum(counts.values()), "edges": len(b.cfg["edges"]),
        "typed_outcomes": sum("outcome_dispatch" in ir.get("metadata", {}) for bl in b.cfg["blocks"].values()
                              for ir in bl["instructions"]), "handler_predecessors": 5,
        "source_derived_handler_annotations": records, "source_derived_argument_annotations": argument_records,
        "source_entry_checks": summary,
        "roundtrip_equal": True, "fresh_model_calls": 0})
    print("Original first response compiled and round-tripped;", len(b.cfg["blocks"]), "blocks,", sum(counts.values()), "IR.")


if __name__ == "__main__":
    main()
