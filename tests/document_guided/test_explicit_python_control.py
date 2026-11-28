"""Producer-version and source checks for explicit exception and argument selectors."""
import pytest

from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.fragments import validate_fragment, assemble_fragments
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent, OpaqueContent
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from tests.document_guided.test_python_invocation_semantics import (
    CODE, FILE, facts, operation, pos, prepared, processing_records, ret)


def jump(target, line=1):
    return {"kind": "jump", "target": target, "source": pos(line)}


def branch(value, yes, no, line, predicate):
    return {"kind": "branch", "source": pos(line), "metadata": {"predicate": predicate},
            "conditions": [{"result": value}], "arms": [{"target": yes, "condition": "true"},
                                                      {"target": no, "condition": "false"}]}


def explicit_handler():
    doc = facts()
    blocks = {b["ref"]: b for b in doc["blocks"]}
    render = blocks["report"]
    incoming = render["operations"].pop(0)
    incoming["metadata"] = {"predecessor_bindings": {k: k + ".throw" for k in "abcde"}}
    distinguish = branch("caught", "report", "unmatched", 9, "exception_type_matches")
    distinguish["conditions"].append({"external_resource": "builtins.Exception"})
    for key in "abcde":
        blocks[key]["exit"]["on_throw"] = "match"
    # Keep the existing separate direct unmatched terminal, distinct from the handler's own failure.
    escape = {**ret("caught", 9), "metadata": {"disposition": "raise"}}
    doc["blocks"].extend([{"ref": "match", "source_kind": "normal", "operations": [incoming], "exit": distinguish},
                          {"ref": "unmatched", "source_kind": "normal", "operations": [], "exit": escape}])
    return doc


def compile_run(built, material, raw, terminal, data, state):
    p = validate_fragment("processing", raw, material)
    demands = {"realizations": [{"requirement_id": "R001"}], "demands": [{"requirement_id": "R001",
        "target": {"instruction_id": terminal, "side": "input", "index": 0}, "preserve": "value",
        "reason": "Preserve the value of this invocation."}]}
    _, _, compiled, _ = assemble_fragments(p, demands, {"declarations": []}, material)
    solved = propagate(built.cfg, to_payload(compiled), initial_registry=data, initial_state=FlowState.from_mapping(state))
    assert solved.status == "complete", solved.diagnostics
    return solved


@pytest.mark.parametrize(("cls", "expected"), [("ValueError", {"report"}), ("KeyboardInterrupt", {"unmatched"}),
                                              (None, {"report", "unmatched"})])
def test_existing_matching_and_escape_routes_reach_solver(cls, expected):
    built, material, blocks, raw = processing_records(CODE, explicit_handler())
    assert from_accepted_cfg(built.cfg, files={FILE: CODE}).cfg == built.cfg
    # Ordinary outer exception merge remains separate from the directly propagated mismatch.
    outer = blocks["escape"]["instructions"][0]
    raw["ir_semantics"][outer["id"]].update(segments=[{"mode": "local", "ops": [{"op": "merge",
        "incoming": [{"predecessor": blocks[key]["block_id"], "value": {"kind": "input", "index": i}}
                     for i, key in enumerate(["pre", "report"])], "output": "err"}], "returns": []}],
        output_bindings=[{"output_index": 0, "value": {"kind": "local", "name": "err"}}])
    registry = DataRegistry("explicit")
    data = registry.register_source("err", acquired_from="runtime_context:err", content=OpaqueContent(python_exception_type=cls))
    solved = compile_run(built, material, raw, blocks["done"]["instructions"][-1]["id"], registry,
                         {FlowLocation(kind="runtime_context", name="err"): frozenset([data.id])})
    dispatch = blocks["match"]["instructions"][-1]["id"]
    choices = solved.records.get(dispatch).events[0].atomic_ops[0].alternatives
    assert set.union(*(set(c.branch_targets) for c in choices)) == {blocks[key]["block_id"] for key in expected}


@pytest.mark.parametrize("fault", ["reversed", "missing", "guard_data", "class", "normal_exit", "wrong_throw", "rows"])
def test_wrong_handler_evidence_stays_rejected_at_its_own_field(fault):
    raw = explicit_handler()
    guard, escape = raw["blocks"][-2:]
    if fault == "reversed":
        guard["exit"]["arms"].reverse()
    elif fault == "missing":
        guard["exit"]["arms"].pop()
    elif fault == "guard_data":
        guard["exit"]["conditions"][0] = {"result": "a.normal"}
    elif fault == "class":
        guard["exit"]["conditions"][1] = {"external_resource": "builtins.KeyboardInterrupt"}
    elif fault == "normal_exit":
        escape["exit"]["metadata"] = {"disposition": "return"}
    elif fault == "wrong_throw":
        escape["exit"]["values"] = [{"result": "args.err"}]
    else:
        guard["operations"][0]["metadata"]["predecessor_bindings"]["a"] = "b.throw"
    result = assemble_graph_facts(raw, files={FILE: CODE})
    assert result.cfg is None
    assert any(row["code"] == "python_handler_admission" and
               row["path"].endswith("/metadata" if fault == "rows" else "/exit") for row in result.gaps)


def test_effect_only_match_body_needs_no_fabricated_receiver():
    code = CODE.replace("except Exception as caught:", "except Exception:").replace("report(caught)", "report()")
    raw = explicit_handler()
    match_body = next(b for b in raw["blocks"] if b["ref"] == "report")
    match_body["operations"][0]["inputs"] = []
    built = assemble_graph_facts(raw, files={FILE: code})
    assert built.cfg, built.gaps
    from skillflow.document_guided.python_handlers import handler_transfers
    transfers = handler_transfers(built.cfg, {FILE: code})
    original = next(b for b in built.cfg["blocks"].values() if b["block_name"] == "report")["instructions"][0]
    assert original["id"] not in transfers and not original["inputs"]


def explicit_count(name):
    doc = facts()
    entry = doc["blocks"][0]
    entry["operations"][0]["outputs"][1] = name
    entry["exit"] = jump("guard")
    doc["blocks"] = [entry, {"ref": "guard", "source_kind": "normal", "operations": [],
                             "exit": branch(name, "supplied", "omitted", 1, "argument_supplied")}]
    for key, inp in [("supplied", {"result": name}), ("omitted", {"literal": 5})]:
        doc["blocks"].append({"ref": key, "source_kind": "normal", "operations": [operation("value", [inp], [key], 1)],
                              "exit": jump("joined")})
    doc["blocks"].append({"ref": "joined", "source_kind": "normal", "operations": [
        operation("bind", [{"result": "supplied"}, {"result": "omitted"}], ["actual"], 1)], "exit": ret("actual", 1)})
    return doc


@pytest.mark.parametrize("defect", ["reversed", "wrong_literal", "changed_value", "unrelated_guard"])
def test_explicit_default_cannot_overwrite_supplied_or_use_another_operand(defect):
    raw = explicit_count("public.raw_argument")
    _, guard, supplied, omitted, _ = raw["blocks"]
    if defect == "reversed":
        guard["exit"]["arms"].reverse()
    elif defect == "wrong_literal":
        omitted["operations"][0]["inputs"] = [{"literal": 8}]
    elif defect == "changed_value":
        supplied["operations"][0]["inputs"] = [{"literal": 5}]
    else:
        guard["exit"]["conditions"] = [{"result": "args.err"}]
    result = assemble_graph_facts(raw, files={FILE: CODE})
    assert result.cfg is None and any(r["code"] == "python_argument_presence" for r in result.gaps)


@pytest.mark.parametrize("supplied", [..., None, 0, False, "", 7])
@pytest.mark.parametrize("name", ["public.limit", "public.raw_argument"])
def test_explicit_omission_test_sees_the_unmodified_snapshot(supplied, name):
    built, material = prepared(CODE, explicit_count(name))
    blocks = {b["block_name"]: b for b in built.cfg["blocks"].values()}
    entry = blocks["entry"]["instructions"][0]
    assert entry["metadata"]["optional_context_inputs"] == [1] and "python_argument_defaults" not in entry["metadata"]
    assert from_accepted_cfg(built.cfg, files={FILE: CODE}).cfg == built.cfg
    evidence = [{"file": FILE, "start_line": 1, "end_line": 1, "reason": "Bind invocation arguments."}]
    records = {}
    for key, b in blocks.items():
        if key != "guard":
            records[b["instructions"][-1]["id"]] = {"evidences": evidence}
    records[entry["id"]] = {"evidences": evidence, "output_bindings": [
        {"output_index": i, "value": {"kind": "input", "index": i}} for i in range(2)]}
    merge = blocks["joined"]["instructions"][0]["id"]
    records[merge] = {"evidences": evidence, "segments": [{"mode": "local", "ops": [{"op": "merge",
        "incoming": [{"predecessor": blocks[k]["block_id"], "value": {"kind": "input", "index": i}}
                     for i, k in enumerate(["supplied", "omitted"])], "output": "selected"}], "returns": []}],
        "output_bindings": [{"output_index": 0, "value": {"kind": "local", "name": "selected"}}]}
    data = DataRegistry("selected")
    err = data.register_source("err", acquired_from="runtime_context:err")
    state = {FlowLocation(kind="runtime_context", name="err"): frozenset([err.id])}
    if supplied is not ...:
        argument = data.register_source("limit", acquired_from="runtime_context:limit", content=LiteralContent(value=supplied))
        state[FlowLocation(kind="runtime_context", name="limit")] = frozenset([argument.id])
    solved = compile_run(built, material, {"ir_semantics": records, "locations": {}, "processing_gaps": []},
                         blocks["joined"]["instructions"][-1]["id"], data, state)
    chosen = "omitted" if supplied is ... else "supplied"
    branch_record = solved.records.get(blocks["guard"]["instructions"][0]["id"]).events[0].atomic_ops[0]
    assert set.union(*(set(v.branch_targets) for v in branch_record.alternatives)) == {blocks[chosen]["block_id"]}
    binding, = solved.records.get(merge).exit_state.bindings
    identity, = binding.data_ids
    from skillflow.propagation.data.summary import content_options
    values = content_options(solved.registry, identity)
    expected = 5 if supplied is ... else supplied
    assert values and all(v["form"] == "literal" and type(v["value"]) is type(expected) and v["value"] == expected for v in values)
    def original(node):
        content = solved.registry.get(node).content.model_dump(mode="json")
        variants = [v["content"] for v in content["variants"]] if content["form"] == "loop_summary" else [content]
        if all(v["form"] == "selection" and not v["path"] for v in variants):
            return set.union(*(original(v["base"]) for v in variants))
        return {node}
    if supplied is ...:
        assert all(solved.registry.get(node).origin.acquired_from is None for node in original(identity))
    else:
        assert original(identity) == {argument.id}
