"""Ingress regression from actual saved model responses; never import the analyzed Skill."""
from copy import deepcopy

import pytest

from skillflow.common.structural_correction import StructuralValidationError
from skillflow.document_guided.fragments import assemble_fragments, fragment_correction_strategy, validate_fragment
from skillflow.document_guided.graph_facts import assemble_graph_facts
from skillflow.document_guided.graph_slots import apply_graph_updates, plan_graph_repair
from skillflow.propagation.annotation.services import to_payload
from skillflow.propagation.data import DataRegistry, LiteralContent
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from tests.document_guided.ga4_entry_occurrence_case import (
    canonical, evidence, filled_processing, load_material, occurrence_update, original_projection, signature, SIGNATURES)
from tests.propagation.annotation.helpers import prepared_material


@pytest.fixture(scope="module")
def frozen(tmp_path_factory):
    return load_material(tmp_path_factory.mktemp("ga4-occurrences"))


def test_archived_entry_and_processing_conflict_are_real(frozen):
    saved, source, files = frozen
    blocks = {b["ref"]: b for b in saved["graph_excerpt"]["blocks"]}
    entry = blocks["public_entry"]["operations"][0]
    assert len(entry["inputs"]) == len(entry["outputs"]) == 18
    assert entry["inputs"][-2:] == [{"context_key": "runtime.argv1"}, {"context_key": "runtime.importMetaUrl"}]
    assert "getPageViews,getTrafficSources" in blocks["select.reports"]["exit"]["arms"][0]["condition"]
    args = blocks["reports.prepare"]["operations"][0]
    assert {"result": "entry.dateRange"} in args["inputs"]
    for b in ["public_entry", "select.reports", "reports.prepare"]:
        rows = blocks[b]["operations"] or [blocks[b]["exit"]]
        for row in rows:
            assert row["source"]["file"] in files
    for owner, (file, line) in SIGNATURES.items():
        assert "function " + owner + "(dateRange?:" in files[file].splitlines()[line - 1]
    # Include exact grouped route and its real users in preflight. The excerpt
    # retains unselected targets as read-only boundaries with empty continuations.
    excerpt = deepcopy(saved["graph_excerpt"])
    targets = {arm["target"] for b in blocks.values() for arm in b["exit"].get("arms", [])}
    targets.update(b["exit"]["target"] for b in blocks.values() if b["exit"]["kind"] == "jump")
    for target in sorted(targets - blocks.keys()):
        excerpt["blocks"].append({"ref": target, "source_kind": "normal", "operations": [],
                                  "exit": {"kind": "return", "values": [], "source": None}})
    draft = assemble_graph_facts(excerpt, files=files)
    repairs = plan_graph_repair(draft, files=files)
    groups = [slot for slot in repairs["slots"].values() if slot["kind"] == "occurrence_region"]
    assert len(groups) == 1, draft.gaps
    visible = str(groups[0])
    assert all(name in visible for name in ("entry.acquire", "select.reports", "reports.arguments"))
    raw = saved["processing_excerpt"]
    assert len(raw["locations"]["entry"]["operand_refs"]) == 18
    assert len(raw["ir_semantics"]["ir_001"]["output_bindings"]) == 18
    assert raw["processing_gaps"][0]["instruction_id"] == "ir_001"
    assert raw["processing_gaps"][0]["unmodeled"] is True


def test_crossed_callers_and_wrong_routes_cannot_validate_each_other(frozen):
    """All formal ports exist and dominate their consumers, but both wrapper identities are wrong."""
    saved, source, files = frozen
    raw = original_projection(saved)
    draft = assemble_graph_facts(raw, files=files)
    plan = plan_graph_repair(draft, files=files)
    slot = one(s for s in plan["slots"].values() if s["kind"] == "occurrence_region")
    rows = occurrence_update(raw)
    blocks = {row["ref"]: row for row in rows}
    for root, wrong_call, actual_parameter in [
        ("public_entry", "getTrafficSources", "getPageViews.suppliedRange"),
        ("select.reports", "getPageViews", "getTrafficSources.suppliedRange"),
    ]:
        blocks[root]["exit"]["target"] = wrong_call
        blocks[wrong_call]["operations"][0]["inputs"] = [{"result": actual_parameter}]
    wrong = assemble_graph_facts({"entry": raw["entry"], "blocks": rows}, files=files)
    assert wrong.cfg is None and any("occurrence" in g["code"] for g in wrong.gaps), wrong.gaps
    repaired = apply_graph_updates(draft, plan, {"plan_sha256": plan["plan_sha256"],
        "updates": [{"slot_id": slot["slot_id"], "value": rows}]}, files=files)
    assert repaired.cfg is None, "Checking only that all three formal ports exist admits swapped callers."


@pytest.fixture(scope="module")
def solved_material(frozen):
    saved, source, files = frozen
    raw = original_projection(saved)
    draft = assemble_graph_facts(raw, files=files)
    plan = plan_graph_repair(draft, files=files)
    assert draft.cfg is None, "The original pooled acquisition must not be admitted."
    slots = [s for s in plan["slots"].values() if s["kind"] == "occurrence_region"]
    assert len(slots) == 1, draft.gaps
    repaired = apply_graph_updates(draft, plan, {"plan_sha256": plan["plan_sha256"], "updates": [{
        "slot_id": slots[0]["slot_id"], "value": occurrence_update(raw)}]}, files=files)
    assert repaired.cfg and not repaired.gaps and not repaired.patch_diagnostics, (
        repaired.gaps, repaired.patch_diagnostics)
    material = prepared_material(source, repaired.cfg)
    reply = filled_processing(repaired)
    first = canonical(repaired, "public_entry", "receive")
    # Exercise the actual historical processing record as a stale model answer
    # after re-binding. Its eighteen outputs cannot stand for one invocation.
    stale = deepcopy(reply)
    prior = deepcopy(saved["processing_excerpt"])
    stale["ir_semantics"][first] = prior["ir_semantics"]["ir_001"]
    stale["locations"].update(prior["locations"])
    for ref in stale["locations"]["entry"]["operand_refs"]:
        ref["instruction_id"] = first
    stale["processing_gaps"] = [{**prior["processing_gaps"][0], "instruction_id": first}]
    with pytest.raises(StructuralValidationError) as failure:
        validate_fragment("processing", stale, material)
    diagnostics = failure.value.diagnostics
    assert {r["code"] for r in diagnostics} >= {"entry_acquisition", "entry_output_binding"}
    strategy = fragment_correction_strategy("processing")
    strategy.build_prompt("Reconcile the entry and its actual source location.", stale, diagnostics)
    scope = strategy.processing_scope
    assert set(scope["coverage_slots"]) == {first} and set(scope["records"]) == {"/locations/entry"}
    location = {"kind": "runtime_context", "name": "getPageViews.dateRange",
                "operand_refs": [{"instruction_id": first, "side": "input", "index": 0}],
                "evidences": [evidence(signature("getPageViews"), "The parameter belongs to this invocation.")]}
    merged = strategy.merge(stale, {"coverage_slots": [{"instruction_id": first, "modeled": reply["ir_semantics"][first]}],
                                    "replacements": [{"record_id": "/locations/entry", "value": location}]})
    assert merged["locations"]["entry"] == location
    assert all(merged["ir_semantics"][ir] == row for ir, row in stale["ir_semantics"].items() if ir != first)
    reply = validate_fragment("processing", merged, material)
    assert len(reply["ir_semantics"][first]["output_bindings"]) == 1
    assert not any(g.get("unmodeled") and g.get("instruction_id") == first
                   for g in reply.get("processing_gaps", []))
    m = {"realizations": [{"requirement_id": "R001"}], "demands": [{
        "requirement_id": "R001", "target": {"instruction_id": canonical(repaired, "site"),
        "side": "input", "index": 0}, "preserve": "value", "reason": "Preserve the returned overview fields."}]}
    _, _, compiled, mapping = assemble_fragments(reply, m, {"declarations": []}, material)
    return repaired, to_payload(compiled)


UNKNOWN = object()
OMITTED = object()
DEFAULT = {"startDate": "30daysAgo", "endDate": "today"}


def concrete_run(assembly, payload, values):
    registry = DataRegistry("ga4-entry-occurrence-e2e")
    state, ids = {}, {}
    for key, value in {**values, "configured_range": "30d", "property": "properties/test"}.items():
        if value is OMITTED:
            continue
        content = {} if value is UNKNOWN else {"content": LiteralContent(value=value)}
        identity = registry.register_source(key, acquired_from="fixture:" + key, **content).id
        state[FlowLocation(kind="runtime_context", name=key)] = frozenset([identity])
        ids[key] = identity
    seed = FlowState.from_mapping(state)
    fifo, lifo = (propagate(assembly.cfg, payload, initial_registry=registry, initial_state=seed,
                            schedule=schedule) for schedule in ("fifo", "lifo"))
    assert fifo.coverage == lifo.coverage and fifo.registry.to_dict() == lifo.registry.to_dict()
    assert fifo.records.records_dict() == lifo.records.records_dict()
    assert set(fifo.coverage.values()) <= {"processed", "processed_with_placeholder"}, (fifo.coverage, fifo.diagnostics)
    assert not fifo.diagnostics
    return fifo, ids


def active_ops(solved, ir):
    return [op for event in solved.records.get(ir).events for op in event.atomic_ops
            if not op.skipped_case_inputs and (op.inputs or op.outputs or op.op == "placeholder")]


def ancestors(registry, identity):
    """Chase operation/control versions, including the source behind a selected value."""
    seen, todo = set(), [identity]
    while todo:
        current = todo.pop()
        if current in seen:
            continue
        seen.add(current)
        value = registry.get(current)
        todo.extend(value.origin.inputs)
        if value.origin.part_of:
            todo.append(value.origin.part_of)
    return seen


def one(values):
    values = tuple(values)
    assert len(values) == 1, values
    return next(iter(values))


def built_member(ops, container, path):
    build = one(op for op in ops if op.op == "build" and container in op.outputs[0])
    part = one(member for member in build.members if member.path == path)
    return one(build.inputs[part.value_input_index])


def observed_call(solved, ir):
    ops = active_ops(solved, ir)
    send = one([op for op in ops if op.op == "deliver"])
    recv = one([op for op in ops if op.op == "receive"])
    assert [loc.name for loc in send.endpoints] == [loc.name for loc in recv.endpoints] == ["analytics"]
    assert send.inputs == recv.inputs
    project = one([op for op in ops if op.op == "select_part"])
    write = one([op for op in ops if op.op == "write"])
    assert project.inputs[0] == recv.outputs[0]
    assert project.outputs[0] == write.inputs[0]
    response = one(project.outputs[0])
    content = solved.registry.get(response).content
    choices = [v.content for v in content.variants] if content.form == "loop_summary" else [content]
    assert choices and all(c.form == "selection" and c.path == [0] and c.base in recv.outputs[0] for c in choices)
    request = one(send.inputs[0])
    date = built_member(ops, built_member(ops, request, ["dateRanges"]), [0])
    return date, response


def test_each_invocation_uses_its_date_and_recovers_its_own_sdk_result(solved_material):
    assembly, payload = solved_material
    values = {name + ".dateRange": {"startDate": month + "-01", "endDate": month + "-20"}
              for name, month in zip(SIGNATURES, ("2026-01", "2026-02", "2026-03"))}
    solved, seeds = concrete_run(assembly, payload, values)
    returned = {}
    for block, operation, owner in [("getPageViews", "invoke", "getPageViews"),
                                    ("getTrafficSources", "invoke", "getTrafficSources"),
                                    ("site", "site.pageViews", "siteOverview"),
                                    ("site", "site.trafficSources", "siteOverview")]:
        ir = canonical(assembly, block, operation)
        range_id, response = observed_call(solved, ir)
        upstream = ancestors(solved.registry, range_id)
        assert {seeds[key] for key in values} & upstream == {seeds[owner + ".dateRange"]}
        output = assembly.id_map["results"][
            block + ".response" if block != "site" else operation + ".response"]
        assert solved.records.get(ir).exit_state.get(FlowLocation(kind="result", name=output)) == {response}
        if block == "site":
            assert solved.coverage[ir] == "processed_with_placeholder"
            returned[operation.removeprefix("site.")] = response
        else:
            final_ir = canonical(assembly, block)
            assert solved.records.get(final_ir).entry_state.get(FlowLocation(kind="result", name=output)) == {response}
    combined = one(op for op in active_ops(solved, canonical(assembly, "site", "site.assemble")) if op.op == "build")
    summary = one(combined.outputs[0])
    assert {field: built_member([combined], summary, [field]) for field in returned} == returned
    assert len(set(returned.values())) == 2


@pytest.mark.parametrize(("value", "choice"), [(OMITTED, "omitted"), (None, "null"), ("", "empty"), (UNKNOWN, "unknown")])
def test_optional_range_and_default_preserve_which_read_occurred(solved_material, value, choice):
    assembly, payload = solved_material
    values = {owner + ".dateRange": DEFAULT for owner in SIGNATURES}
    values["getPageViews.dateRange"] = value
    solved, seeds = concrete_run(assembly, payload, values)
    ir = canonical(assembly, "getPageViews", "invoke")
    record = solved.records.get(ir)
    active_cases = {ev.case.name for ev in record.events if ev.case and ev.atomic_ops
                    and any(not op.skipped_case_inputs and (op.inputs or op.outputs) for op in ev.atomic_ops)}
    if choice == "unknown":
        assert {"null", "other"} <= active_cases
        report_build = next(op for op in active_ops(solved, ir)
                            if op.op == "build" and [p.path for p in op.members] == [[0]])
        assert any(any(k.endswith(":object") and outcome == "1" for k, outcome in alt.bindings.items())
                   for alt in report_build.alternatives)
        assert "omitted" not in active_cases
    else:
        assert active_cases == {choice}
        range_id, _ = observed_call(solved, ir)
        assert seeds["configured_range"] in ancestors(solved.registry, range_id)
    acquired = solved.records.get(canonical(assembly, "public_entry", "receive"))
    if value is OMITTED:
        assert "getPageViews.dateRange" not in seeds
        value_loc = FlowLocation(kind="result", name=assembly.id_map["results"]["getPageViews.suppliedRange"])
        excluded = one(acquired.exit_state.get(value_loc))
        assert solved.registry.get(excluded).origin.acquired_from is None
        assert not any(op.op == "read" and op.outputs and any(op.outputs)
                       for ev in acquired.events for op in ev.atomic_ops)
    else:
        arg_loc = FlowLocation(kind="result", name=assembly.id_map["results"]["getPageViews.suppliedRange"])
        snapshot_id = one(acquired.exit_state.get(arg_loc))
        assert seeds["getPageViews.dateRange"] in ancestors(solved.registry, snapshot_id)


def test_without_concrete_invocation_keep_both_optional_routes(solved_material):
    assembly, payload = solved_material
    solved = propagate(assembly.cfg, payload)
    assert set(solved.coverage.values()) <= {"processed", "processed_with_placeholder"}
    ir = canonical(assembly, "getPageViews", "invoke")
    assert any(event.case and event.case.name == "omitted"
               and any(op.op == "read" and op.outputs for op in event.atomic_ops)
               for event in solved.records.get(ir).events)
    ranges = next(op for op in active_ops(solved, ir)
                  if op.op == "build" and [part.path for part in op.members] == [[0]])
    bindings = [choice.bindings for choice in ranges.alternatives]
    assert any(any(k.endswith(":missing") and v == "1" for k, v in row.items()) for row in bindings)
    assert any(any(k.endswith(":object") and v == "1" for k, v in row.items()) for row in bindings)
