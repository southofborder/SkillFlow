"""Closed source projection of the fresh 626-IR GA4 failure (two public calls, shared report body)."""

from copy import deepcopy
import json

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.document_guided.fragments import assemble_fragments, validate_fragment
from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.propagation.annotation.services import to_payload
from tests.document_guided.ga4_entry_occurrence_case import (
    REPORTS,
    SNAPSHOT,
    canonical,
    evidence,
    inp,
    jump,
    literal,
    load_material,
    local,
    result,
    segment,
    span,
    spec,
)
from tests.document_guided.test_ga4_entry_occurrence_trace import active_ops, ancestors, concrete_run, one
from tests.propagation.annotation.helpers import prepared_material


def projection(saved):
    blocks = {b["ref"]: deepcopy(b) for b in saved["blocks"] if not b["ref"].startswith("site.")}
    joined = blocks["report.merge"]
    joined["operations"][0]["inputs"] = [result("pageViews.options"), result("sources.options")]
    # Both wrappers omit limit and save. Restrict the body to the object-range, no-limit, default-save path.
    joined["exit"] = jump("report.withoutLimit", span(REPORTS, 97))
    parsed = joined["operations"][-1]
    parsed.update(opcode="value", source=span(REPORTS, 53, 54))
    blocks["report.request.merge"]["operations"][0]["inputs"] = [result("report.request.unlimited")]
    blocks["report.acquire"]["exit"] = jump("report.save", span(REPORTS, 102))
    saved_op = blocks["report.save"]["operations"][-1]
    blocks["report.save"]["operations"] = [saved_op]
    saved_op.update(opcode="write", inputs=[result("report.response")])
    return {"entry": "pageViews.entry", "blocks": list(blocks.values())}


def replies(graph, saved):
    sdk_ir = canonical(graph, "report.acquire", "report.api")
    receiver = deepcopy(saved["receiver_location"])
    receiver["operand_refs"][0]["instruction_id"] = sdk_ir
    locations = {"ga_report": receiver}
    for label, kind, line in [
        ("get_client", "tool", 88),
        ("get_property", "tool", 89),
        ("saved", "storage", 105),
    ]:
        locations[label] = {
            "name": label,
            "kind": kind,
            "evidences": [evidence(span(REPORTS, line), "Sourced helper or save.")],
        }
    records = {}
    for block in graph.facts["blocks"]:
        ref = block["ref"]
        records[canonical(graph, ref)] = spec(block["exit"]["source"])
        for op in block["operations"]:
            name, at = op["ref"], op["source"]
            row = spec(at)
            if ref.endswith(".entry"):
                row = spec(at, output=inp())
            elif ref in {"pageViews.bind", "sources.bind"}:
                row = deepcopy(saved["initial_wrapper"])
                row["evidences"] = [evidence(at, "Bind this actual caller date to its options.")]
            elif name == "report.options":
                incoming = [
                    {"predecessor": graph.id_map["blocks"][caller], "value": inp(i)}
                    for i, caller in enumerate(["pageViews.bind", "sources.bind"])
                ]
                row = spec(
                    at,
                    segments=[segment([{"op": "merge", "incoming": incoming, "output": "options"}])],
                    output=local("options"),
                )
            elif name == "report.destructure":
                fields = ["dimensions", "metrics", "dateRange"]
                ops = [
                    {"op": "select_part", "input": inp(), "path": [field], "output": field}
                    for field in fields
                ]
                row = spec(at, segments=[segment(ops)])
                row["output_bindings"] = [
                    {"output_index": i, "value": v}
                    for i, v in enumerate([*(local(f) for f in fields), literal(None), literal(True)])
                ]
            elif name in {"report.client", "report.property"}:
                label = "get_client" if name == "report.client" else "get_property"
                row = spec(
                    at,
                    segments=[
                        segment(
                            [
                                {
                                    "op": "call",
                                    "location": label,
                                    "inputs": [],
                                    "output": label,
                                    "input_contract": {
                                        "inputs": [],
                                        "reason": "Source invokes this getter with no arguments.",
                                        "evidences": [evidence(at, "No arguments at this call.")],
                                    },
                                }
                            ]
                        )
                    ],
                    output=local(label),
                )
            elif name in {"report.range", "report.request"}:
                row = spec(at, output=inp())
            elif name == "report.request.unlimited":
                row = spec(
                    at,
                    segments=[
                        segment(
                            [
                                {
                                    "op": "build",
                                    "container": "list",
                                    "parts": [{"path": [0], "value": inp(1)}],
                                    "output": "ranges",
                                },
                                {
                                    "op": "build",
                                    "container": "object",
                                    "parts": [
                                        {"path": [field], "value": v}
                                        for field, v in [
                                            ("property", inp()),
                                            ("dateRanges", local("ranges")),
                                            ("dimensions", inp(2)),
                                            ("metrics", inp(3)),
                                        ]
                                    ],
                                    "output": "request",
                                },
                            ]
                        )
                    ],
                    output=local("request"),
                )
            elif name == "report.api":
                row = deepcopy(saved["initial_sdk"])
            elif name == "report.save.call":
                row = spec(at, segments=[segment([{"op": "write", "target": "saved", "input": inp()}])])
            else:
                raise AssertionError(name)
            records[canonical(graph, ref, name)] = row
    return {"locations": locations, "ir_semantics": records}


@pytest.fixture(scope="module")
def material(tmp_path_factory):
    _, source, files = load_material(tmp_path_factory.mktemp("invoked-report"))
    saved = json.loads(SNAPSHOT.with_name("call-results.json").read_bytes())
    assert source["source_sha256"] == saved["source_sha256"]
    raw = projection(saved)
    g = assemble_graph_facts(raw, files=files)
    assert g.cfg and not g.gaps, g.gaps
    m = prepared_material(source, g.cfg)
    return saved, source, files, raw, g, m


def test_source_sdk_projection_requires_same_bound_receiver_request_and_result(material):
    saved, _, _, _, g, m = material
    sdk = canonical(g, "report.acquire", "report.api")
    good = replies(g, saved)
    validate_fragment("processing", good, m)
    for mistake in ("receiver", "request", "path", "tuple", "output", "double_binding"):
        q = deepcopy(good)
        rec = q["ir_semantics"][sdk]
        call, select = rec["segments"][0]["ops"]
        if mistake == "receiver":
            q["locations"]["ga_report"]["operand_refs"][0]["index"] = 1
        elif mistake == "request":
            call["inputs"] = [inp(0)]
        elif mistake == "path":
            select["path"] = [1]
        elif mistake == "tuple":
            select["input"] = inp(1)
        elif mistake == "output":
            rec["output_bindings"][0]["value"] = local("tuple")
        else:
            rec["action_bindings"]["firstResponse"].append(["segments", 0, "ops", 0])
        with pytest.raises(StructuralValidationError) as invalid:
            validate_fragment("processing", q, m)
        assert any(d["code"] == "source_action_binding" for d in invalid.value.diagnostics), mistake


def test_repeated_wrapper_summary_fails_with_exact_archived_call(material):
    saved, _, _, _, g, m = material
    candidate = replies(g, saved)
    ir = canonical(g, "pageViews.bind", "pageViews.runReport")
    candidate["locations"]["report_function"] = {
        "kind": "tool",
        "name": "runReport",
        "evidences": [evidence(span(REPORTS, 115, 119), "The wrapper invokes the local function.")],
    }
    candidate["ir_semantics"][ir] = saved["selected_wrapper"]
    with pytest.raises(StructuralValidationError, match="Repeating that invocation"):
        validate_fragment("processing", candidate, m)


def test_source_backed_cross_block_repair_reconnects_actual_and_return(material):
    _, _, files, raw, _, _ = material
    wrong = deepcopy(raw)
    blocks = {b["ref"]: b for b in wrong["blocks"]}
    blocks["report.merge"]["operations"][0]["inputs"][1] = result("pageViews.options")
    blocks["report.return"]["exit"]["values"] = [result("report.request")]
    g = assemble_graph_facts(wrong, files=files)
    assert not g.cfg and {d["code"] for d in g.gaps} == {"call_return_binding"}
    plan = plan_graph_repair(g, files=files)
    slot = one(s for s in plan["slots"].values() if s["kind"] == "call_region")
    assert {"pageViews.bind", "sources.bind", "report.merge", "report.return"} <= slot[
        "editable_actions"
    ].keys()
    repaired = {b["ref"]: b for b in raw["blocks"]}
    rows = [repaired["report.merge"], repaired["report.return"]]

    def apply(updates):
        return apply_graph_updates(
            g,
            plan,
            {"plan_sha256": plan["plan_sha256"], "updates": [{"slot_id": slot["slot_id"], "value": updates}]},
            files=files,
        )

    assert apply(rows).cfg
    illicit = deepcopy(rows)
    illicit[0]["operations"][2]["opcode"] = "write"
    bad = apply(illicit)
    assert not bad.cfg and bad.patch_diagnostics


def test_shared_report_from_independent_dates_through_sdk_save_and_return(material):
    saved, _, _, _, g, m = material
    processing = validate_fragment("processing", replies(g, saved), m)
    req = {
        "realizations": [{"requirement_id": "R001"}],
        "demands": [
            {
                "requirement_id": "R001",
                "target": {"instruction_id": canonical(g, "report.return"), "side": "input", "index": 0},
                "preserve": "value",
                "reason": "Preserve the returned report.",
            }
        ],
    }
    _, _, ann, _ = assemble_fragments(processing, req, {"declarations": []}, m)
    values = {
        "invoke." + who + ".dateRange": {"startDate": period + "-01", "endDate": period + "-21"}
        for who, period in [("getPageViews", "2026-03"), ("getTrafficSources", "2026-04")]
    }
    solved, seeds = concrete_run(g, to_payload(ann), values)
    sdk = canonical(g, "report.acquire", "report.api")
    ops = active_ops(solved, sdk)
    sent = one(op for op in ops if op.op == "deliver")
    received = one(op for op in ops if op.op == "receive")
    selected = one(op for op in ops if op.op == "select_part")
    assert received.inputs == sent.inputs and received.outputs[0] == selected.inputs[0]
    from skillflow.propagation.models import FlowLocation

    ends = solved.records.get(canonical(g, "report.return")).entry_state
    versions = ends.get(FlowLocation(kind="result", name=g.id_map["results"]["report.response"]))
    saved_ops = active_ops(solved, canonical(g, "report.save", "report.save.call"))
    assert versions == selected.outputs[0] == one(op for op in saved_ops if op.op == "write").inputs[0]
    fields = []

    def member(identity, key):
        data = solved.registry.get(identity).content
        variants = [c.content for c in data.variants] if data.form == "loop_summary" else [data]
        return {part.data for content in variants for part in content.parts if part.path == [key]}

    for variant in sent.alternatives:
        request = one(variant.inputs[0])
        for ranges in member(request, "dateRanges"):
            for date in member(ranges, 0):
                who = {seeds[k] for k in values} & ancestors(solved.registry, date)
                assert len(who) == 1
                fields.append(one(who))
    assert set(fields) == {seeds[k] for k in values}


def test_latest_site_overview_keeps_two_results_of_one_input(material):
    from skillflow.document_guided.action_bindings import action_coordinates
    from tests.document_guided.ga4_entry_occurrence_case import INDEX, report_record
    from tests.document_guided.test_ga4_entry_occurrence_trace import built_member

    saved, source, files, *_ = material
    blocks = {b["ref"]: deepcopy(b) for b in saved["blocks"] if b["ref"].startswith("site.")}
    body = blocks["site.run"]
    body["operations"] = [
        op
        for op in body["operations"]
        if op["ref"] in {"site.pageViews", "site.trafficSources", "site.aggregate"}
    ]
    aggregate = body["operations"][-1]
    aggregate["inputs"] = [result("site.pageViews.response"), result("site.trafficSources.response")]
    aggregate["outputs"] = ["site.aggregate"]
    g = assemble_graph_facts({"entry": "site.entry", "blocks": list(blocks.values())}, files=files)
    assert g.cfg and not g.gaps
    m = prepared_material(source, g.cfg)
    loc = {}
    for key, kind, line in [
        ("configured_range", "runtime_context", 47),
        ("property", "runtime_context", 89),
        ("analytics", "remote", 100),
        ("saved", "storage", 105),
    ]:
        loc[key] = {
            "name": key,
            "kind": kind,
            "evidences": [evidence(span(REPORTS, line), "Actual source boundary.")],
        }
    loc["console"] = {
        "name": "console",
        "kind": "user",
        "evidences": [evidence(span(INDEX, 59, 63), "Logs each acquisition.")],
    }
    records = {canonical(g, b["ref"]): spec(b["exit"]["source"]) for b in blocks.values()}
    entry = blocks["site.entry"]["operations"][0]
    records[canonical(g, "site.entry", entry["ref"])] = spec(entry["source"], output=inp())
    for op, wrapper in zip(body["operations"][:2], ("getPageViews", "getTrafficSources")):
        row = report_record(wrapper, op["source"])
        row["segments"].insert(
            0, segment([{"op": "deliver", "target": "console", "inputs": [literal("report progress")]}])
        )
        paths = [list(p) for p, _ in action_coordinates(row)]
        row["action_bindings"] = {"log": [paths[0]], "invoke": paths[1:-1], "assign": [paths[-1]]}
        records[canonical(g, "site.run", op["ref"])] = row
    fields = ("pageViews", "trafficSources")
    records[canonical(g, "site.run", "site.aggregate")] = spec(
        aggregate["source"],
        segments=[
            segment(
                [
                    {
                        "op": "build",
                        "container": "object",
                        "output": "overview",
                        "parts": [{"path": [k], "value": inp(i)} for i, k in enumerate(fields)],
                    }
                ]
            )
        ],
        output=local("overview"),
    )
    processing = validate_fragment("processing", {"ir_semantics": records, "locations": loc}, m)
    req = {
        "realizations": [{"requirement_id": "R001"}],
        "demands": [
            {
                "requirement_id": "R001",
                "target": {"instruction_id": canonical(g, "site.run"), "side": "input", "index": 0},
                "preserve": "value",
                "reason": "Preserve the two returned overview members.",
            }
        ],
    }
    _, _, compiled, _ = assemble_fragments(processing, req, {"declarations": []}, m)
    key = entry["inputs"][0]["context_key"]
    solved, seeds = concrete_run(
        g, to_payload(compiled), {key: {"startDate": "2026-01-08", "endDate": "2026-01-12"}}
    )
    combined = one(
        o for o in active_ops(solved, canonical(g, "site.run", "site.aggregate")) if o.op == "build"
    )
    outputs = []
    for k in fields:
        ops = active_ops(solved, canonical(g, "site.run", "site." + k))
        send = one(o for o in ops if o.op == "deliver" and any(e.name == "analytics" for e in o.endpoints))
        recv = one(o for o in ops if o.op == "receive")
        assert send.inputs == recv.inputs
        req = one(send.inputs[0])
        date = built_member(ops, built_member(ops, req, ["dateRanges"]), [0])
        assert seeds[key] in ancestors(solved.registry, date)
        projection = one(o for o in ops if o.op == "select_part")
        assert projection.inputs[0] == recv.outputs[0]
        returned = one(projection.outputs[0])
        assert saved_response(ops) == returned == built_member([combined], one(combined.outputs[0]), [k])
        outputs.append(returned)
    assert len(set(outputs)) == 2


def saved_response(ops):
    return one(one(o for o in ops if o.op == "write").inputs[0])


def test_real_second_read_is_a_distinct_invocation():
    from skillflow.document_guided.source_calls import bind_source_calls

    f = "skill/read.ts"
    lines = ["const [first] = await client.read(a);", "const [second] = await client.read(b);"]
    files = {f: "\n".join(lines)}
    ops = [
        {
            "ref": "read" + str(i),
            "opcode": "receive",
            "inputs": [result(arg)],
            "outputs": [label],
            "source": span(f, i),
        }
        for i, (arg, label) in enumerate([("a", "first"), ("b", "second")], start=1)
    ]
    g = {
        "blocks": [
            {"ref": "both", "operations": ops, "exit": {"kind": "return", "values": [result("second")]}}
        ]
    }
    bind_source_calls(g, files)
    assert [o["opcode"] for o in ops] == ["call", "call"]
    assert [a["ref"] for o in ops for a in o["source_actions"]] == [
        "read1",
        "read1.projection",
        "read2",
        "read2.projection",
    ]
    ambiguous = deepcopy(g)
    broad = span(f, 1, 2)
    ambiguous["blocks"][0]["operations"] = [
        {
            "ref": "bothReads",
            "opcode": "receive",
            "source": broad,
            "source_actions": [
                {"ref": "first", "kind": "call", "source": span(f, 1)},
                {"ref": "second", "kind": "receive", "source": span(f, 2)},
            ],
        }
    ]
    bind_source_calls(ambiguous, files)
    assert ambiguous["blocks"][0]["operations"][0]["source_actions"][1]["kind"] == "receive"


def test_real_callee_return_reaches_the_callers_consumer_and_lean_checks_the_repair():
    from skillflow.graph.audit.controlled import render_controlled
    from skillflow.graph.ir.cfg import ControlFlowGraph

    f = "skill/returns.ts"
    files = {f: """export function clientCall(arg) {
  const reply = helper(arg);
  return reply;
}
export function helper(arg) {
  const [response] = client.read(arg);
  return response;
}"""}

    def op(ref, role, line, inputs, outputs):
        return {"ref": ref, "opcode": role, "source": span(f, line), "inputs": inputs, "outputs": outputs}

    def block(ref, operations, exit, kind="normal"):
        return {"ref": ref, "source_kind": kind, "operations": operations, "exit": exit}

    def ret(name, line):
        return {"kind": "return", "values": [result(name)], "source": span(f, line)}

    facts = {
        "entry": "caller",
        "blocks": [
            block(
                "caller",
                [op("supplied", "receive", 1, [{"context_key": "arg"}], ["arg"])],
                jump("call", span(f, 1)),
                "context",
            ),
            block("call", [op("invoke", "call", 2, [result("arg")], ["actual"])], jump("enter", span(f, 2))),
            block(
                "enter",
                [op("parameter", "value", 5, [result("actual")], ["formal"])],
                jump("execute", span(f, 5)),
            ),
            block("execute", [op("read", "call", 6, [result("formal")], ["response"])], ret("response", 7)),
            block("consumer", [], ret("arg", 3)),
        ],
    }
    g = assemble_graph_facts(facts, files=files)
    assert any(d["code"] == "call_return_binding" for d in g.gaps)
    plan = plan_graph_repair(g, files=files)
    slot = one(s for s in plan["slots"].values() if s["kind"] == "call_region")
    assert slot["editable_actions"]["consumer"] == {"$exit": "consumer"}
    authorized = {b["ref"]: deepcopy(b) for b in slot["old_value"]}
    body, consumer = authorized["execute"], authorized["consumer"]
    body["exit"] = jump("consumer", span(f, 7))
    consumer["exit"] = ret("response", 3)
    ans = {
        "plan_sha256": plan["plan_sha256"],
        "updates": [{"slot_id": slot["slot_id"], "value": [body, consumer]}],
    }
    repaired = apply_graph_updates(g, plan, ans, files=files)
    assert repaired.cfg and not repaired.gaps and not repaired.patch_diagnostics, (
        repaired.gaps,
        repaired.patch_diagnostics,
    )
    render_controlled(ControlFlowGraph.model_validate(repaired.cfg))
    consumer["exit"] = ret("arg", 3)
    rejected = apply_graph_updates(g, plan, ans, files=files)
    assert not rejected.cfg


def test_previous_graph_reader_keeps_original_projection_ownership(material):
    from skillflow.document_guided.graph_steps import GraphFactsCorrection

    saved, _, files, raw, current, _ = material
    prior = assemble_graph_facts(raw, files=files, check_calls=False)
    assert prior.cfg and not prior.gaps

    def sdk(assembly):
        return next(
            o
            for b in assembly.cfg["blocks"].values()
            for o in b["instructions"]
            if o["id"] == canonical(assembly, "report.acquire", "report.api")
        )

    assert sdk(prior)["opcode"] == "receive"
    assert sdk(current)["opcode"] == "call"
    assert prior.to_receipt()["identity"] == "skillflow-graph-facts-v4"
    assert current.to_receipt()["identity"] == "skillflow-graph-facts-v5"
    assert GraphFactsCorrection(files, check_calls=False).identity == "skillflow-graph-facts-correction-v5"
    assert GraphFactsCorrection(files).identity == "skillflow-graph-facts-correction-v6"


def test_wrong_options_field_cannot_consume_another_source_version(material):
    saved, _, _, _, g, m = material
    q = replies(g, saved)
    ir = canonical(g, "pageViews.bind", "pageViews.runReport")
    update = q["ir_semantics"][ir]["segments"][0]["ops"][0]["updates"][0]
    update["value"] = inp(1)
    with pytest.raises(StructuralValidationError, match="source parameter"):
        validate_fragment("processing", q, m)


def test_duplicate_same_source_call_on_linear_path_is_scoped_and_removable(material):
    _, _, files, raw, _, _ = material
    candidate = deepcopy(raw)
    wrapper = next(b for b in candidate["blocks"] if b["ref"] == "pageViews.bind")
    duplicate = {**deepcopy(wrapper["operations"][0]), "ref": "repeat", "outputs": ["unused.reply"]}
    wrapper["operations"].insert(0, duplicate)
    invalid = assemble_graph_facts(candidate, files=files)
    assert any("duplicate at pageViews.bind/repeat" in g["message"] for g in invalid.gaps)
    plan = plan_graph_repair(invalid, files=files)
    slot = one(s for s in plan["slots"].values() if s["kind"] == "call_region")
    assert slot["editable_actions"]["pageViews.bind"]["repeat"] == "duplicate"
    corrected = deepcopy(next(row for row in slot["old_value"] if row["ref"] == "pageViews.bind"))
    corrected["operations"].pop(0)
    result = apply_graph_updates(
        invalid,
        plan,
        {"plan_sha256": plan["plan_sha256"], "updates": [{"slot_id": slot["slot_id"], "value": [corrected]}]},
        files=files,
    )
    assert result.cfg and not result.patch_diagnostics and not result.gaps


def test_ordered_shared_parameters_reject_transposed_actuals():
    from skillflow.document_guided.call_region import call_sites

    f = "skill/pair.ts"
    files = {
        f: "export function first(a,b) {\n  return pair(a,b);\n}\nexport function pair(left,right) {\n  return left;\n}"
    }
    call = {
        "ref": "actuals",
        "opcode": "value",
        "source": span(f, 2),
        "inputs": [result("a"), result("b")],
        "outputs": ["actual.a", "actual.b"],
    }
    formal = {
        "ref": "pair",
        "opcode": "value",
        "source": span(f, 4),
        "inputs": [result("actual.a"), result("actual.b")],
        "outputs": ["left", "right"],
    }
    points = {
        "blocks": [
            {"ref": "wrapper", "operations": [call], "exit": jump("body", span(f, 2))},
            {
                "ref": "body",
                "operations": [formal],
                "exit": {"kind": "return", "source": span(f, 5), "values": [result("left")]},
            },
        ]
    }
    assert not one(call_sites(points, files))["errors"]
    formal["inputs"].reverse()
    assert "source order" in one(one(call_sites(points, files))["errors"])


@pytest.mark.parametrize(
    "returned", [inp(0), inp(1), literal({"unrelated": "7d"}), literal({"dateRange": "7d"})]
)
def test_options_object_cannot_be_replaced_by_a_formal_or_known_constant(material, returned):
    saved, _, _, _, graph, m = material
    q = replies(graph, saved)
    ir = canonical(graph, "pageViews.bind", "pageViews.runReport")
    row = q["ir_semantics"][ir]
    row["segments"] = []
    row["output_bindings"][0]["value"] = returned
    with pytest.raises(StructuralValidationError, match="source parameter"):
        validate_fragment("processing", q, m)


def test_object_argument_follows_actual_returned_selection(material):
    saved, _, _, _, graph, m = material
    q = replies(graph, saved)
    ir = canonical(graph, "pageViews.bind", "pageViews.runReport")
    row = q["ir_semantics"][ir]
    ops = row["segments"][0]["ops"]
    ops.extend(
        [
            {
                "op": "build",
                "container": "object",
                "parts": [
                    {"path": ["options"], "value": local("x")},
                    {"path": ["constant"], "value": literal({"dateRange": "7d"})},
                ],
                "output": "wrapper",
            },
            {"op": "select_part", "input": local("wrapper"), "path": ["options"], "output": "returned"},
        ]
    )
    row["output_bindings"][0]["value"] = local("returned")
    validate_fragment("processing", q, m)
    ops[-1]["path"] = ["constant"]
    with pytest.raises(StructuralValidationError, match="source parameter"):
        validate_fragment("processing", q, m)


@pytest.mark.parametrize(
    "header, prelude, bound",
    [
        ("function caller(helper, options) {", "", False),
        ("function caller(options) {", "const helper = options.handler;", False),
        ("function caller(options) {", "", True),
    ],
)
def test_shadowed_callback_is_distinct_from_same_spelled_declaration(header, prelude, bound):
    from skillflow.document_guided.source_calls import bind_source_calls

    f = "skill/callbacks.ts"
    files = {
        f: "\n".join(
            [
                header,
                prelude,
                "  return helper(options);",
                "}",
                "function helper(options) {",
                "  return options;",
                "}",
                "function other(handler) {",
                "  const helper = handler;",
                "}",
            ]
        )
    }
    op = {
        "ref": "forward",
        "opcode": "call",
        "source": span(f, 3),
        "inputs": [result("options")],
        "outputs": ["actual"],
    }
    formal = {
        "ref": "parameter",
        "opcode": "value",
        "source": span(f, 5),
        "inputs": [result("actual")],
        "outputs": ["options"],
    }
    cfg = {
        "blocks": [
            {"ref": "call", "operations": [op], "exit": jump("body", span(f, 3))},
            {
                "ref": "body",
                "operations": [formal],
                "exit": {"kind": "return", "values": [result("options")], "source": span(f, 6)},
            },
        ]
    }
    bind_source_calls(cfg, files)
    assert (op["opcode"] == "value") == bound
    if bound:
        # This source forwards an already-constructed whole value. Both the
        # program-owned marker and the output expression must preserve it.
        from skillflow.document_guided.source_calls import _check_object_arguments, source_call

        ir = {"inputs": [{"type": "result", "identifier": "options"}], "outputs": [{"identifier": "actual"}]}
        assert not list(
            _check_object_arguments(
                ir,
                {"output_bindings": [{"output_index": 0, "value": inp()}]},
                source_call(op["source"], files),
                [],
                {"options": "options"},
            )
        )
    else:
        assert "source_actions" not in op


def test_a_later_spread_can_override_a_source_property():
    from skillflow.document_guided.source_calls import Call, _check_object_arguments

    ir = {"inputs": [{"type": "result", "identifier": "range"}], "outputs": [{"identifier": "options"}]}
    row = {"output_bindings": [{"output_index": 0, "value": literal({"dateRange": "7d"})}]}

    def result_for(arg):
        return list(_check_object_arguments(ir, row, Call("fn", None, (arg,)), [], {"range": "dateRange"}))

    assert result_for("{dateRange, ...overrides}") == []
    assert result_for("{...overrides, dateRange}")
