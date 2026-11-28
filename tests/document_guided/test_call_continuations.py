"""Caller-specific normal and exceptional continuations using ordinary GraphFacts."""
from copy import deepcopy

import pytest

from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg


FILES = {"skill/work.py": """def fetch(x):
    a = provider(x)
    return convert(a)

def main(y):
    try:
        result = fetch(y)
        print(result)
    except Exception as exc:
        print(exc)
"""}


def span(start, end=None):
    return {"file": "skill/work.py", "start_line": start, "end_line": end or start}


def op(ref, line, inputs, outputs, **metadata):
    return {"ref": ref, "opcode": "value", "source": span(line), "inputs": inputs, "outputs": outputs,
            "metadata": metadata}


def val(name):
    return {"result": name}


def jump(line, dest):
    return {"kind": "jump", "source": span(line), "target": dest}


def end(line, *names):
    return {"kind": "return", "source": span(line), "values": list(map(val, names))}


def branch(line, key, left, right):
    return {"kind": "branch", "source": span(line), "conditions": [val(key)],
            "arms": [{"target": left, "condition": "first"}, {"target": right, "condition": "other"}]}


def block(ref, operations, exit, kind="normal"):
    return {"ref": ref, "source_kind": kind, "operations": operations, "exit": exit}


def draft():
    bindings = {"invoke": {"arg": "actual", "token": {"literal": "caller"}},
                "public": {"arg": "external", "token": {"literal": "external"}}}
    exceptions = {"get": {"error": "get.err"}, "convert": {"error": "cv.err"}}
    blocks = [
        block("main", [op("read", 5, [{"context_key": "main.y"}], ["y"])], jump(5, "invoke"), "context"),
        block("invoke", [op("arguments", 7, [val("y")], ["actual"])], jump(7, "formal")),
        block("public", [op("read", 1, [{"context_key": "fetch.x"}], ["external"])], jump(1, "formal"), "context"),
        block("formal", [op("formal", 1, [val("actual"), val("external")], ["arg", "token"],
                            predecessor_bindings=bindings)], jump(2, "get")),
        block("get", [op("get", 2, [val("arg")], ["response", "ready", "get.err"],
                         paired_response="response", note="response", parameter_fields={"response": "arg"})],
              branch(2, "ready", "convert", "errors")),
        block("convert", [op("decode", 3, [val("response")], ["value", "ok", "cv.err"])],
              branch(3, "ok", "done", "errors")),
        block("done", [], branch(3, "token", "public.result", "consumer")),
        block("errors", [op("err", 2, [val("get.err"), val("cv.err")], ["error"], predecessor_bindings=exceptions)],
              branch(3, "token", "public.exception", "handler")),
        block("public.result", [], end(3, "value")),
        block("public.exception", [], end(3, "error")),
        block("consumer", [op("use", 8, [val("value")], [])], end(8)),
        block("handler", [op("match", 9, [val("error")], [])], end(10)),
    ]
    return {"entry": "main", "blocks": blocks}


def index(facts):
    return {b["ref"]: b for b in facts["blocks"]}


def test_routes_are_control_edges_with_their_own_value_versions():
    facts = draft()
    # Neither an arm's order, its English label nor the predecessor's tag names
    # establish who gets a return or exception.
    for ref in ("done", "errors"):
        index(facts)[ref]["exit"]["arms"].reverse()
        for arm in index(facts)[ref]["exit"]["arms"]:
            arm["condition"] = "not an identifier"
    original = deepcopy(facts)
    result = assemble_graph_facts(facts, files=FILES)
    assert result.cfg and not result.gaps
    assert facts == original
    b = index(result.facts)
    for suffix, predecessor, result_dest, error_dest in (
        ("", "invoke", "consumer", "handler"), (".public", "public", "public.result", "public.exception")
    ):
        assert b[predecessor]["exit"]["target"] == "formal" + suffix
        assert b["done" + suffix]["exit"] == jump(3, result_dest)
        assert b["errors" + suffix]["exit"] == jump(3, error_dest)
        assert b["get" + suffix]["operations"][0]["inputs"] == [val("arg" + suffix)]
        formal = b["formal" + suffix]["operations"][0]
        assert formal["outputs"] == ["arg" + suffix]
        assert formal["inputs"] == [val("actual" if not suffix else "external")]
    assert b["public.result"]["exit"]["values"] == [val("value.public")]
    assert b["public.exception"]["exit"]["values"] == [val("error.public")]
    assert b["consumer"]["operations"][0]["inputs"] == [val("value")]
    assert b["handler"]["operations"][0]["inputs"] == [val("error")]
    copied = b["get.public"]["operations"][0]["metadata"]
    assert copied["note"] == "response" and copied["parameter_fields"] == {"response": "arg.public"}
    assert copied["paired_response"] == "response.public"
    assert result.to_receipt() == assemble_graph_facts(result.facts, files=FILES).to_receipt()
    assert from_accepted_cfg(result.cfg, files=FILES).cfg == result.cfg


@pytest.mark.parametrize("wrong", ["completion_as_return", "exception_as_return", "response_as_error",
                                   "real_data_as_route", "wrong_consumer", "unknown_source_handler"])
def test_an_unproved_shared_route_does_not_publish_a_cfg(wrong):
    facts = draft()
    b = index(facts)
    if wrong in {"completion_as_return", "exception_as_return"}:
        name = "ok" if wrong == "completion_as_return" else "cv.err"
        b["public.result"]["exit"]["values"] = b["consumer"]["operations"][0]["inputs"] = [val(name)]
    if wrong == "response_as_error":
        op = b["errors"]["operations"][0]
        op["inputs"][0] = val("response")
        op["metadata"]["predecessor_bindings"]["get"]["error"] = "response"
    if wrong == "real_data_as_route":
        rows = b["formal"]["operations"][0]["metadata"]["predecessor_bindings"]
        for row in rows.values():
            row["token"] = row["arg"]
    if wrong == "wrong_consumer":
        b["errors"]["exit"]["arms"][1]["target"] = "consumer"
        b["done"]["exit"]["arms"][1]["target"] = "handler"
    if wrong == "unknown_source_handler":
        b["handler"]["operations"][0]["source"] = span(2)
    result = assemble_graph_facts(facts, files=FILES)
    assert result.cfg is None
    assert any(gap["code"] == "call_return_binding" for gap in result.gaps)
