"""Repair the four-parameter binding without editing other callers or source evidence."""
from copy import deepcopy

import pytest

from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair


FILE = "skill/search.py"
FILES = {FILE: """def helper(query, key):
    endpoint = 'https://example.test'
    return query, key

def caller(query, key):
    result = helper(query, key)
    return result
"""}


def span(first, last=None):
    return {"file": FILE, "start_line": first, "end_line": last or first}


def result(name):
    return {"result": name}


def jump(target, line):
    return {"kind": "jump", "target": target, "source": span(line)}


def block(ref, operations, exit):
    return {"ref": ref, "source_kind": "normal", "operations": operations, "exit": exit}


def fixture():
    facts = {"entry": "caller", "blocks": [
        block("caller", [{"ref": "args", "opcode": "value", "source": span(6),
              "inputs": [{"literal": "query"}, {"literal": "key"}], "outputs": ["arg.query", "arg.key"]}],
              jump("body", 6)),
        block("body", [{"ref": "formals", "opcode": "value", "source": span(1, 2),
              "source_actions": [{"ref": "parameters", "kind": "value", "source": span(1)},
                                 {"ref": "endpoint", "kind": "value", "source": span(2)}],
              "inputs": [result("arg.query"), result("arg.key")], "outputs": ["query", "key"],
              "metadata": {"predecessor_bindings": {"caller": {"query": "arg.key", "key": "arg.query"}},
                           "producers": {"query": "parameters", "key": "parameters"}}}],
              jump("return", 3)),
        block("return", [], {"kind": "return", "source": span(7), "values": [result("query"), result("key")]}),
    ]}
    g = assemble_graph_facts(facts, files=FILES)
    assert g.cfg is None and [d["code"] for d in g.gaps] == ["call_return_binding"], g.gaps
    assert g.gaps[0]["path"] == "/blocks/1/operations/0/metadata/predecessor_bindings/caller"
    plan = plan_graph_repair(g, files=FILES)
    slot, = [s for s in plan["slots"].values() if s["kind"] == "call_region"]
    updated = deepcopy(next(b for b in slot["old_value"] if b["ref"] == "body"))
    updated["operations"][0]["metadata"]["predecessor_bindings"]["caller"] = {
        "query": "arg.query", "key": "arg.key"}
    return g, plan, slot, updated


def apply(g, plan, slot, value):
    return apply_graph_updates(g, plan, {"plan_sha256": plan["plan_sha256"], "updates": [
        {"slot_id": slot["slot_id"], "value": [value]}]}, files=FILES)


def test_parameter_row_repair_keeps_all_real_child_source_spans():
    g, plan, slot, row = fixture()
    repaired = apply(g, plan, slot, row)
    assert repaired.cfg and not repaired.patch_diagnostics and not repaired.gaps


@pytest.mark.parametrize("changed", ["wrong_order", "new_row", "new_parameter", "child_span", "metadata", "delete_row"])
def test_parameter_row_grant_keeps_its_source_and_caller_scope(changed):
    g, plan, slot, row = fixture()
    op = row["operations"][0]
    bindings = op["metadata"]["predecessor_bindings"]
    if changed == "wrong_order":
        bindings["caller"] = {"query": "arg.key", "key": "arg.query"}
    elif changed == "new_row":
        bindings["other_caller"] = dict(bindings["caller"])
    elif changed == "new_parameter":
        bindings["caller"]["route"] = {"literal": "caller"}
    elif changed == "child_span":
        op["source_actions"][0]["source"] = span(1, 2)
    elif changed == "metadata":
        op["metadata"]["producers"]["key"] = "endpoint"
    elif changed == "delete_row":
        del bindings["caller"]
    failed = apply(g, plan, slot, row)
    assert failed.cfg is None and failed.patch_diagnostics
