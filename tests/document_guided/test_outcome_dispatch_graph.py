"""A protected source action routes each disposition through its declared CFG exit."""
from copy import deepcopy

import pytest
from pydantic import ValidationError

from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.graph.extraction.compiler import compile_candidate
from skillflow.graph.ir.cfg import ControlFlowGraph


FILES = {"skill/script.txt": "Open the resource.\nContinue on success.\nRecord the exception.\n"}


def span(line):
    return {"file": "skill/script.txt", "start_line": line, "end_line": line}


def example(*, ports=False):
    outputs = ["response", "exception"] if ports else []
    call = {"ref": "open", "opcode": "call", "inputs": [{"literal": "resource"}],
            "outputs": outputs, "source": span(1)}
    route = {"kind": "outcome_dispatch", "producer": "open", "source": span(1),
             "on_return": "ok", "on_throw": "handler"}
    if ports:
        route["inputs"] = [{"result": name} for name in outputs]
    return {"entry": "start", "blocks": [
        {"ref": "start", "source_kind": "normal", "operations": [call], "exit": route},
        *[{"ref": name, "source_kind": "normal", "operations": [],
           "exit": {"kind": "return", "values": [{"result": outputs[i]}] if ports else [],
                    "source": span(i + 2)}} for i, name in enumerate(("ok", "handler"))]]}


@pytest.mark.parametrize("ports", [True, False])
def test_typed_route_preserves_ports_and_recompiles_with_assigned_ids(ports):
    assembled = assemble_graph_facts(example(ports=ports), files=FILES)
    assert not assembled.gaps
    cfg = assembled.cfg
    call, dispatch = cfg["blocks"]["block_001"]["instructions"]
    assert dispatch["inputs"] == call["outputs"] and dispatch["outputs"] == []
    assert dispatch["metadata"]["outcome_dispatch"] == {
        "producer": call["id"], "on_return": "block_002", "on_throw": "block_003"}
    assert compile_candidate(assembled.candidate).cfg.to_json() == compile_candidate(
        assembled.candidate, canonical_ids=assembled.id_map).cfg.to_json()
    cfg["edges"].reverse()
    for edge in cfg["edges"]:
        edge["condition_text"] = "source description"
    assert from_accepted_cfg(cfg, files=FILES).cfg == cfg


@pytest.mark.parametrize(("field", "value", "diagnostic"), [
    ("producer", "another", "outcome_producer"), ("on_throw", "absent", "target_not_found"),
    ("on_throw", "ok", "outcome_targets"), ("inputs", [{"result": "unknown"}], "outcome_operand"),
    ("metadata", {"outcome_dispatch": {}}, "generated_metadata")])
def test_invalid_typed_routes_expose_local_repair_slots(field, value, diagnostic):
    raw = example()
    raw["blocks"][0]["exit"][field] = value
    draft = assemble_graph_facts(raw, files=FILES)
    assert draft.cfg is None
    assert any(row["code"] == diagnostic and row["slot_id"] in draft.slots for row in draft.gaps)


def test_canonical_validation_rejects_wrong_producer_extra_edges_and_metadata_on_an_action():
    cfg = assemble_graph_facts(example(), files=FILES).cfg
    for change in ("producer", "edges", "nonterminal", "ordinary", "null"):
        invalid = deepcopy(cfg)
        call, terminal = invalid["blocks"]["block_001"]["instructions"]
        route = terminal["metadata"]["outcome_dispatch"]
        if change == "producer":
            route["producer"] = terminal["id"]
        elif change == "edges":
            invalid["edges"].pop()
        elif change == "nonterminal":
            call["metadata"]["outcome_dispatch"] = route
        elif change == "null":
            terminal["metadata"]["outcome_dispatch"] = None
        else:
            del terminal["metadata"]["outcome_dispatch"]
        with pytest.raises(ValidationError):
            ControlFlowGraph.model_validate(invalid)


def test_reviewed_source_can_assign_roles_to_two_existing_edges_and_retain_the_ports():
    raw = example(ports=True)
    block = raw["blocks"][0]
    typed = deepcopy(block["exit"])
    block["exit"] = {"kind": "branch", "source": span(1), "conditions": typed["inputs"],
                     "arms": [{"target": "ok", "condition": "the response is available"},
                              {"target": "handler", "condition": "the operation raised"}]}
    base = from_accepted_cfg(assemble_graph_facts(raw, files=FILES).cfg, files=FILES)
    plan = plan_graph_repair(base, files=FILES, findings=[{"domain": "cfg", "required_graph_edit": "topology",
        "target_ids": ["cfg:/blocks/block_001/instructions/1"], "source_refs": [span(1)]}])
    slot, = plan["slots"].values()
    replacement = deepcopy(slot["old_value"])
    old = replacement["exit"]
    replacement["exit"] = {"kind": "outcome_dispatch", "source": old["source"],
        "metadata": old["metadata"], "producer": "ir_001", "inputs": old["conditions"],
        "on_return": "block_002", "on_throw": "block_003"}
    reply = {"plan_sha256": plan["plan_sha256"], "updates": [{"slot_id": slot["slot_id"], "value": [replacement]}]}
    revised = apply_graph_updates(base, plan, reply, files=FILES)
    assert not revised.gaps and not revised.patch_diagnostics
    assert revised.cfg["edges"] == base.cfg["edges"]
    expected = deepcopy(base.cfg)
    expected["blocks"]["block_001"]["instructions"][1]["metadata"]["outcome_dispatch"] = {
        "producer": "ir_001", "on_return": "block_002", "on_throw": "block_003"}
    assert revised.cfg == expected
    repair = plan_graph_repair(revised, files=FILES, findings=[{"domain": "cfg", "required_graph_edit": "field",
        "target_ids": ["cfg:/edges/1"], "source_refs": [span(1)]}])
    field, = repair["slots"].values()
    assert field["path"] == ["blocks", 0, "exit", "on_throw"]


def test_straight_line_source_and_sibling_ports_require_source_authored_targets():
    raw = example(ports=True)
    site = {"file": "skill/code.py", "start_line": 1, "end_line": 1}
    files = {**FILES, site["file"]: "result = receive()\n"}
    block = raw["blocks"][0]
    block["operations"][0]["source"] = site
    block["exit"] = {"kind": "branch", "source": site, "conditions": block["exit"]["inputs"],
                     "arms": [{"target": "handler", "condition": "text A"}, {"target": "ok", "condition": "text B"}]}
    old = assemble_graph_facts(raw, files=files, check_outcome_routes=False)
    assert old.cfg and from_accepted_cfg(old.cfg, files=files).cfg == old.cfg
    draft = assemble_graph_facts(raw, files=files)
    assert [row["code"] for row in draft.gaps] == ["outcome_targets_required"]
    plan = plan_graph_repair(draft, files=files)
    slot, = plan["slots"].values()
    assert slot["kind"] == "outcome_targets" and draft.cfg is None
    def repair(targets):
        return apply_graph_updates(draft, plan, {"plan_sha256": plan["plan_sha256"],
            "updates": [{"slot_id": slot["slot_id"], "value": targets}]}, files=files)
    assert repair({"on_return": "ok", "on_throw": "ok"}).cfg is None
    fixed = repair({"on_return": "ok", "on_throw": "handler"})
    assert fixed.cfg and not fixed.gaps and not fixed.patch_diagnostics
    assert fixed.facts["blocks"][0]["exit"]["inputs"] == block["exit"]["conditions"]
    assert fixed.cfg["blocks"]["block_001"]["instructions"][-1]["metadata"]["outcome_dispatch"]["on_throw"] == "block_003"
    files[site["file"]] = "if receive(): continue_work()\n"
    assert assemble_graph_facts(raw, files=files).cfg == assemble_graph_facts(raw, files=files, check_outcome_routes=False).cfg
