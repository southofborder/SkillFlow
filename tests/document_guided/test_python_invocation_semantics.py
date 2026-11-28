"""Source-derived Python handler membership and omission-only parameter defaults."""
from hashlib import sha256

import pytest

from skillflow.common.source_evidence import _digest
from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.graph_facts import assemble_graph_facts, from_accepted_cfg
from skillflow.document_guided.python_handlers import handler_transfers
from skillflow.document_guided.fragments import validate_fragment, assemble_fragments, salvage_fragment
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent, OpaqueContent
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.selectors import selector_outcomes
from skillflow.propagation.solver import propagate
from tests.propagation.annotation.helpers import prepared_material

FILE = "skill/program.py"
CODE = """def run(err, limit=5):
    before()
    try:
        a()
        b()
        c()
        d()
        e()
    except Exception as caught:
        report(caught)
"""


def pos(line):
    return {"file": FILE, "start_line": line, "end_line": line}


def ret(name, line):
    return {"kind": "return", "values": [{"result": name}], "source": pos(line)}


def operation(ref, inputs, outputs, line):
    return {"ref": ref, "opcode": "value", "source": pos(line), "inputs": inputs, "outputs": outputs}


def packet(code):
    row = {"path": "program.py", "content": code, "sha256": sha256(code.encode()).hexdigest()}
    return {"files": [row], "source_sha256": _digest([{"path": row["path"], "sha256": row["sha256"]}])}


def facts():
    args = {"ref": "args", "opcode": "receive", "source": pos(1),
            "inputs": [{"context_key": "err"}, {"context_key": "limit"}], "outputs": ["args.err", "args.limit"]}
    blocks = [{"ref": "entry", "source_kind": "context", "operations": [args],
               "exit": {"kind": "jump", "target": "pre", "source": pos(1)}}]
    labels = ["pre", "a", "b", "c", "d", "e", "report"]
    for index, (label, line) in enumerate(zip(labels, [2, 4, 5, 6, 7, 8, 10])):
        is_handler = label == "report"
        inp = "caught" if is_handler else "args.err"
        op = operation("action", [{"result": inp}], [label + ".normal", label + ".throw"], line)
        ops = [op]
        if is_handler:
            ops.insert(0, operation("bind", [{"result": c + ".throw"} for c in labels[1:-1]], ["caught"], 9))
        blocks.append({"ref": label, "source_kind": "normal", "operations": ops, "exit": {
            "kind": "outcome_dispatch", "producer": "action", "source": pos(line),
            "on_return": "done" if label in {"e", "report"} else labels[index+1],
            "on_throw": "escape" if label in {"pre", "report"} else "report"}})
    outer = operation("outer", [{"result": "pre.throw"}, {"result": "report.throw"}], ["unhandled"], 10)
    blocks.extend([{"ref": "escape", "source_kind": "normal", "operations": [outer], "exit": ret("unhandled", 10)},
                   {"ref": "done", "source_kind": "normal", "operations": [], "exit": ret("args.limit", 10)}])
    return {"entry": "entry", "blocks": blocks}


def prepared(code=CODE, raw=None):
    files = {FILE: code}
    built = assemble_graph_facts(facts() if raw is None else raw, files=files)
    assert built.cfg is not None, built.gaps
    return built, prepared_material(packet(code), built.cfg)


def test_five_protected_edges_match_and_other_throws_bypass():
    built, _ = prepared()
    by_name = {b["block_name"]: b for b in built.cfg["blocks"].values()}
    gate = by_name["report.exception_match"]
    for name in "abcde":
        assert by_name[name]["instructions"][-1]["metadata"]["outcome_dispatch"]["on_throw"] == gate["block_id"]
    for name in ["pre", "report"]:
        assert by_name[name]["instructions"][-1]["metadata"]["outcome_dispatch"]["on_throw"] == by_name["escape"]["block_id"]
    kinds = handler_transfers(built.cfg, {FILE: CODE})
    branch = kinds[gate["instructions"][-1]["id"]]["segments"][0]["ops"][0]
    assert branch["selector"] == {"path": [], "tests": [{"kind": "python_exception", "classes": ["Exception"]}], "outcome": 0}
    assert branch["true_target"] == by_name["report"]["block_id"] and branch["false_target"] == by_name["escape"]["block_id"]
    assert len(kinds[gate["instructions"][0]["id"]]["segments"][0]["ops"][0]["incoming"]) == 5
    assert from_accepted_cfg(built.cfg, files={FILE: CODE}).cfg == built.cfg


def test_outside_try_exception_cannot_be_admitted():
    raw = facts()
    pre = raw["blocks"][1]
    pre["exit"]["on_throw"] = "report"
    target = next(b for b in raw["blocks"] if b["ref"] == "report")
    target["operations"][0]["inputs"].append({"result": "pre.throw"})
    built = assemble_graph_facts(raw, files={FILE: CODE})
    assert any(r["code"] == "python_handler_admission" for r in built.gaps)


@pytest.mark.parametrize(("cls", "outcomes"), [("ValueError", {0}), ("KeyboardInterrupt", {1}),
                                               ("UnresolvedCustomClass", {0, 1}), (None, {0, 1})])
def test_exception_selector_uses_actual_type_only(cls, outcomes):
    data = DataRegistry("exceptions")
    raised = data.register_source("raised", acquired_from="runtime",
                                  content=OpaqueContent(python_exception_type=cls))
    test = {"path": [], "tests": [{"kind": "python_exception", "classes": ["Exception"]}], "outcome": 0}
    assert selector_outcomes(data, raised.id, test) == outcomes
    fake = data.register_source("error_text", acquired_from="runtime",
                                content=LiteralContent(value={"type": "ValueError", "message": "ValueError"}))
    assert selector_outcomes(data, fake.id, test) == {0, 1}


def processing_records(code=CODE, raw=None):
    built, material = prepared(code, raw)
    by_name = {b["block_name"]: b for b in built.cfg["blocks"].values()}
    template = handler_transfers(built.cfg, {FILE: code})
    records = {}
    for b in by_name.values():
        for ir in b["instructions"]:
            if ir["id"] in template or ir["metadata"].get("outcome_dispatch"):
                continue  # These records are generated by the normal frontend.
            evidence = [{**ir["metadata"]["source_span"], "reason": "The source executes this action."}]
            row = {"evidences": evidence}
            records[ir["id"]] = row
            if b["block_name"] == "entry" and ir["opcode"] == "receive":
                row["output_bindings"] = [{"output_index": i, "value": {"kind": "input", "index": i}} for i in range(2)]
            elif len(ir["outputs"]) == 2:
                row["segments"] = [{"kind": "cases", "outcome": {"return_index": 0, "exception_index": 1},
                    "evidences": evidence, "cases": [
                        {"name": "normal", "phase": "normal", "disposition": "return", "condition": "returns",
                         "yield": {"kind": "input", "index": 0}, "evidences": evidence},
                        {"name": "failure", "phase": "local_error", "disposition": "throw", "condition": "throws",
                         "raise": {"kind": "input", "index": 0}, "evidences": evidence}]}]
    return built, material, by_name, {"locations": {}, "processing_gaps": [], "ir_semantics": records}


@pytest.mark.parametrize(("syntax", "expected"), [("raise ValueError", "ValueError"),
                                                 ('raise KeyboardInterrupt("stop")', "KeyboardInterrupt"),
                                                 ("raise factory()", None), ("raise OSError(2, 'file')", None),
                                                 ("raise", None), ("raise TypeError from cause()", None),
                                                 ("raise ValueError(dynamic())", None)])
def test_only_exact_unshadowed_builtin_raise_is_typed(syntax, expected):
    code = CODE.replace("        a()", "        " + syntax)
    g = assemble_graph_facts(facts(), files={FILE: code})
    assert g.cfg, g.gaps
    instructions = next(b for b in g.cfg["blocks"].values() if b["block_name"] == "a")["instructions"]
    assert instructions[0]["metadata"].get("python_raised_class") == expected
    assert not any(i.get("metadata", {}).get("python_raised_class") for b in g.cfg["blocks"].values()
                   for i in b["instructions"] if i["id"] != instructions[0]["id"])
    if expected:
        shadowed = code + "\n" + expected + " = factory()\n"
        alternate = assemble_graph_facts(facts(), files={FILE: shadowed})
        assert alternate.cfg
        assert not any(i.get("metadata", {}).get("python_raised_class") for b in alternate.cfg["blocks"].values()
                       for i in b["instructions"])


@pytest.mark.parametrize(("exc","matched"), [("ValueError", True), ("KeyboardInterrupt", False)])
def test_source_originating_raise_reaches_only_the_compatible_route(exc, matched):
    code = CODE.replace("        a()", "        raise " + exc)
    fixture = facts()
    producer = next(b for b in fixture["blocks"] if b["ref"] == "a")
    producer["operations"][0]["outputs"] = ["a.throw"]
    built = assemble_graph_facts(fixture, files={FILE: code})
    material = prepared_material(packet(code), built.cfg)
    by_name = {b["block_name"]: b for b in built.cfg["blocks"].values()}
    _, _, _, raw = processing_records(code)
    # IDs for blocks/IR are stable even when one output port disappears.
    raising = by_name["a"]["instructions"][0]
    row = raw["ir_semantics"][raising["id"]]
    summary = row["segments"][0]
    summary["outcome"] = {"exception_index": 0}
    summary["cases"] = [summary["cases"][1]]
    summary["cases"][0]["raise"] = {"kind": "local", "name": "__raised__"}
    p = validate_fragment("processing", raw, material)
    end = by_name["done"]["instructions"][-1]["id"]
    t = {"realizations": [{"requirement_id": "R001"}], "demands": [{"requirement_id": "R001",
         "target": {"instruction_id": end, "side": "input", "index": 0}, "preserve": "value", "reason": "Keep bound value."}]}
    _, _, compiled, _ = assemble_fragments(p, t, {"declarations": []}, material)
    solved = propagate(built.cfg, to_payload(compiled))
    assert solved.status == "complete", solved.diagnostics
    gate = by_name["report.exception_match"]["instructions"][-1]["id"]
    guard_op = solved.records.get(gate).events[0].atomic_ops[0]
    assert set.union(*(set(row.branch_targets) for row in guard_op.alternatives)) == {
        by_name["report" if matched else "escape"]["block_id"]}
    from skillflow.propagation.data.summary import content_options
    for identity in guard_op.inputs[0]:
        assert all(option.get("python_exception_type") == exc for option in content_options(solved.registry, identity))


@pytest.mark.parametrize(("cls", "matched", "bypassed"), [("ValueError", True, False),
                                                           ("SystemExit", False, True), (None, True, True)])
def test_public_frontend_and_solver_route_the_real_exception(cls, matched, bypassed):
    built, material, by_name, raw = processing_records()
    processing = validate_fragment("processing", raw, material)
    end = by_name["done"]["instructions"][-1]["id"]
    correspondence = {"realizations": [{"requirement_id": "R001"}], "demands": [{"requirement_id": "R001",
        "target": {"instruction_id": end, "side": "input", "index": 0}, "preserve": "value", "reason": "Keep bound value."}]}
    _, _, compiled, _ = assemble_fragments(processing, correspondence, {"declarations": []}, material)
    data = DataRegistry("raise")
    item = data.register_source("err", acquired_from="runtime_context:err", content=OpaqueContent(python_exception_type=cls))
    state = FlowState.from_mapping({FlowLocation(kind="runtime_context", name="err"): frozenset([item.id])})
    solved = propagate(built.cfg, to_payload(compiled), initial_registry=data, initial_state=state)
    assert solved.status == "complete", solved.diagnostics
    dispatch = by_name["report.exception_match"]["instructions"][-1]
    observed = solved.records.get(dispatch["id"])
    from skillflow.propagation.data.summary import content_options
    targets = set()
    for e in observed.events:
        for op in e.atomic_ops:
            for alternative in op.alternatives:
                targets.update(alternative.branch_targets)
                for identity in alternative.inputs[0]:
                    assert all(opt.get("python_exception_type") == cls for opt in content_options(solved.registry, identity))
    assert (by_name["report"]["block_id"] in targets) is matched
    assert (by_name["escape"]["block_id"] in targets) is bypassed


def test_processing_cannot_send_normal_result_through_handler_as_exception():
    _, material, by_name, raw = processing_records()
    producer = by_name["a"]["instructions"][0]["id"]
    raw["ir_semantics"][producer]["segments"][0]["outcome"] = {"return_index": 1, "exception_index": 0}
    # Include the generated rows to check the public compiler's full port validation directly.
    raw["ir_semantics"].update(handler_transfers(material["cfg"], {FILE: CODE}))
    with pytest.raises(StructuralValidationError) as problem:
        validate_fragment("processing", raw, material)
    assert any(e["code"] == "python_handler_admission" and "exception output" in e["message"]
               for e in problem.value.diagnostics)


def test_conflicting_authored_branch_gets_local_correction_and_isolation():
    _, material, by_name, raw = processing_records()
    gate = by_name["report.exception_match"]["instructions"][-1]["id"]
    expected = handler_transfers(material["cfg"], {FILE: CODE})
    raw["ir_semantics"][gate] = expected[gate]
    op = raw["ir_semantics"][gate]["segments"][0]["ops"][0]
    op["true_target"], op["false_target"] = op["false_target"], op["true_target"]
    with pytest.raises(StructuralValidationError) as problem:
        validate_fragment("processing", raw, material)
    assert any(e["path"] == "/ir_semantics/" + gate for e in problem.value.diagnostics)
    salvaged, gaps = salvage_fragment("processing", raw, material)
    assert salvaged is not None and {g["instruction_id"] for g in gaps} == {gate}
    assert by_name["e"]["instructions"][0]["id"] in salvaged["ir_semantics"]


@pytest.mark.parametrize("supplied", [..., 0, False, None, "", 7])
def test_null_zero_false_and_empty_are_supplied_arguments(supplied):
    raw = facts()
    raw["blocks"] = [raw["blocks"][0]]
    raw["blocks"][0]["exit"] = ret("args.limit", 1)
    built = assemble_graph_facts(raw, files={FILE: CODE})
    material = prepared_material(packet(CODE), built.cfg)
    entry, end = next(iter(built.cfg["blocks"].values()))["instructions"]
    assert entry["metadata"]["python_argument_defaults"] == [{"input_index": 1, "output_index": 1, "value": 5}]
    evidence = [{**pos(1), "reason": "The signature binds the supplied arguments."}]
    record = {"evidences": evidence, "output_bindings": [
        {"output_index": i, "value": {"kind": "input", "index": i}} for i in range(2)]}
    p = validate_fragment("processing", {"ir_semantics": {entry["id"]: record, end["id"]: {"evidences": evidence}},
                                         "processing_gaps": [], "locations": {}}, material)
    correspondence = {"realizations": [{"requirement_id": "R001"}], "demands": [{"requirement_id": "R001",
        "target": {"instruction_id": end["id"], "side": "input", "index": 0}, "preserve": "value",
        "reason": "Return the bound value."}]}
    _, _, compiled, _ = assemble_fragments(p, correspondence, {"declarations": []}, material)
    data = DataRegistry("args")
    err = data.register_source("err", acquired_from="runtime_context:err")
    state = {FlowLocation(kind="runtime_context", name="err"): frozenset([err.id])}
    if supplied is not ...:
        passed = data.register_source("limit", acquired_from="runtime_context:limit", content=LiteralContent(value=supplied))
        state[FlowLocation(kind="runtime_context", name="limit")] = frozenset([passed.id])
    solved = propagate(built.cfg, to_payload(compiled), initial_registry=data, initial_state=FlowState.from_mapping(state))
    assert solved.status == "complete", solved.diagnostics
    ids = next(b.data_ids for b in solved.records.get(entry["id"]).exit_state.bindings
               if b.location.name == entry["outputs"][1]["identifier"])
    if supplied is ...:
        observed, = ids
        assert solved.registry.get(observed).content.value == 5
    else:
        assert set(ids) == {passed.id}
