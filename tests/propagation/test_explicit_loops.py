"""Finite explicit loops. Fixtures are authored offline, never executed Skills."""
from copy import deepcopy
import pytest

from examples.propagation.propagation_demo import fixture_annotation, instruction, operand, input_ref, local, literal
from skillflow.propagation import propagate


def explicit_loop_fixture(values=("a", "a")):
    def block(name, instructions):
        return {"block_id": name, "block_name": name, "instructions": instructions}
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("seed", outputs=["items", "initial"]), instruction("start", opcode="dispatch")]),
        "head": block("head", [instruction("merge", [operand("initial"), operand("next")], ["acc"]),
                                 instruction("guard", [operand("items")], opcode="dispatch")]),
        "body": block("body", [instruction("member", [operand("items")], ["item"]),
            instruction("fetch", [operand("item")], ["response"]),
            instruction("append", [operand("acc"), operand("response")], ["next"]),
            instruction("back", opcode="dispatch")]),
        "exit": block("exit", [instruction("return", [operand("acc")], opcode="return")])},
        "edges": [{"source_block_id": a, "target_block_id": b}
                  for a, b in [("entry", "head"), ("head", "body"), ("head", "exit"), ("body", "head")]]}
    plans = {
        "seed": ([], [], [literal(list(values)), literal([])]),
        "merge": ([], [(None, [{"op": "merge", "incoming": [
            {"predecessor": "entry", "value": input_ref(0)},
            {"predecessor": "body", "value": input_ref(1)}], "output": "selected"}])], [local("selected")]),
        "guard": ([], [(None, [{"op": "branch", "input": input_ref(), "predicate": "has_member",
            "true_target": "body", "false_target": "exit"}])], []),
        "member": ([], [(None, [{"op": "member", "input": input_ref(), "output": "row"}])], [local("row")]),
        "fetch": (["net_receive"], [(0, [{"op": "receive", "location": "api", "inputs": [input_ref()], "output": "reply"}])], [local("reply")]),
        "append": ([], [(None, [{"op": "append", "input": input_ref(), "value": input_ref(1), "mode": "item", "output": "collected"}])], [local("collected")]),
    }
    return fixture_annotation(cfg, plans, {"api": ("remote", "api")})


def test_explicit_merge_member_response_accumulation_converges():
    cfg, annotation = explicit_loop_fixture()
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.coverage["ir_return"] == "processed"
    assert result.stats["block_evaluations"] < 30
    member = result.records.get("ir_member").events[0].atomic_ops[0]
    assert len(member.outputs[0]) == 2  # Equal source values retain two occurrences.
    assert len({tuple(item.bindings.items()) for item in member.alternatives}) == 2
    assert any(entry["data"]["content"]["form"] == "loop_summary" for entry in result.registry.to_dict()["records"])
    result.registry.validate()


def test_known_empty_traversal_never_records_member_or_acquisition():
    cfg, annotation = explicit_loop_fixture(())
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.coverage["ir_fetch"] == "not_reached"
    assert result.coverage["ir_return"] == "processed"
    assert not any(entry["data"]["origin"].get("acquired_from") == "remote:api" for entry in result.registry.to_dict()["records"])


def test_explicit_loop_fifo_lifo_same_sealed_facts():
    cfg, annotation = explicit_loop_fixture()
    fifo = propagate(cfg, annotation)
    lifo = propagate(cfg, annotation, schedule="lifo")
    assert fifo.registry.to_dict() == lifo.registry.to_dict()
    assert fifo.records.records_dict() == lifo.records.records_dict()


def test_boolean_guard_never_uses_python_truthiness_for_empty_array():
    cfg, annotation = explicit_loop_fixture(())
    annotation = deepcopy(annotation)
    annotation["ir_semantics"]["ir_guard"]["events"][0]["atomic_ops"][0]["predicate"] = "truthy"
    result = propagate(cfg, annotation)
    assert result.status == "incomplete"
    assert any("Boolean" in item["reason"] for item in result.diagnostics)


def nested_loop_fixture(pages=None):
    def block(name, instructions):
        return {"block_id": name, "block_name": name, "instructions": instructions}
    pages = pages if pages is not None else [
        {"rows": [{"receiver": "A", "secret": "a0"}, {"receiver": "A", "secret": "a1"}]},
        {"rows": [{"receiver": "B", "secret": "b0"}, {"receiver": "B", "secret": "b1"}]}]
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("pages", outputs=["pages"]), instruction("start", opcode="dispatch")]),
        "outer": block("outer", [instruction("outer_guard", [operand("pages")], opcode="dispatch")]),
        "page": block("page", [instruction("page", [operand("pages")], ["page"]),
            instruction("rows", [operand("page")], ["rows"]), instruction("to_inner", opcode="dispatch")]),
        "inner": block("inner", [instruction("inner_guard", [operand("rows")], opcode="dispatch")]),
        "item": block("item", [instruction("row", [operand("rows")], ["row"]),
            instruction("select", [operand("row")], ["recipient", "payload"]),
            instruction("send", [operand("recipient"), operand("payload")]), instruction("inner_back", opcode="dispatch")]),
        "next_page": block("next_page", [instruction("outer_back", opcode="dispatch")]),
        "exit": block("exit", [instruction("return", opcode="return")])},
        "edges": [{"source_block_id": source, "target_block_id": target} for source, target in [
            ("entry", "outer"), ("outer", "page"), ("outer", "exit"), ("page", "inner"),
            ("inner", "item"), ("inner", "next_page"), ("item", "inner"), ("next_page", "outer")]]}
    def guard(input_, yes, no):
        return ([], [(None, [{"op": "branch", "input": input_, "predicate": "has_member", "true_target": yes, "false_target": no}])], [])
    plans = {
        "pages": ([], [], [literal(pages)]),
        "outer_guard": guard(input_ref(), "page", "exit"),
        "page": ([], [(None, [{"op": "member", "input": input_ref(), "output": "page"}])], [local("page")]),
        "rows": (["transform"], [(0, [{"op": "select_part", "input": input_ref(), "path": ["rows"], "output": "rows"}])], [local("rows")]),
        "inner_guard": guard(input_ref(), "item", "next_page"),
        "row": ([], [(None, [{"op": "member", "input": input_ref(), "output": "row"}])], [local("row")]),
        "select": (["transform"], [(0, [
            {"op": "select_part", "input": input_ref(), "path": ["receiver"], "output": "receiver"},
            {"op": "select_part", "input": input_ref(), "path": ["secret"], "output": "payload"}])], [local("receiver"), local("payload")]),
        "send": (["net_send"], [(0, [{"op": "deliver", "inputs": [input_ref(), input_ref(1)], "target": "api"}])], []),
    }
    return fixture_annotation(cfg, plans, {"api": ("remote", "api")})


def test_nested_page_member_pairs_never_form_cross_recipient_payload_products():
    from skillflow.propagation.data.summary import content_options
    cfg, annotation = nested_loop_fixture()
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    operation = result.records.get("ir_send").events[0].atomic_ops[0]
    pairs = set()
    for candidate in operation.alternatives:
        values = [content_options(result.registry, next(iter(slot))) for slot in candidate.inputs]
        for recipient in values[0]:
            for payload in values[1]:
                assert recipient["form"] == payload["form"] == "literal"
                pairs.add((recipient["value"], payload["value"]))
    assert pairs == {("A", "a0"), ("A", "a1"), ("B", "b0"), ("B", "b1")}
    assert len(operation.alternatives) == 4
    assert result.registry.to_dict() == propagate(cfg, annotation, schedule="lifo").registry.to_dict()


def test_known_nonempty_exit_uses_post_write_state_and_keeps_prior_observation():
    from skillflow.propagation import FlowLocation
    cfg, annotation = explicit_loop_fixture(("once",))
    evidence = deepcopy(annotation["ir_semantics"]["ir_fetch"]["events"][0]["atomic_ops"][0]["evidences"])
    annotation["locations"]["state"] = {"kind": "runtime_context", "name": "state", "operand_refs": [], "access_scope": "task", "retention": "task"}
    annotation["ir_semantics"]["ir_append"]["events"][:0] = [
        {"effect": "context_read", "evidences": evidence, "atomic_ops": [{"op": "read", "location": "state", "output": "prior", "evidences": evidence}]},
        {"effect": "net_send", "evidences": evidence, "atomic_ops": [{"op": "deliver", "target": "api", "inputs": [local("prior")], "evidences": evidence}]}]
    # A local overwrite in the body must not resurrect the entry state at exit.
    annotation["ir_semantics"]["ir_append"]["events"].append({"effect": "context_write", "evidences": evidence,
        "atomic_ops": [{"op": "write", "target": "state", "mode": "replace", "input": literal("new"), "evidences": evidence}]})
    # The projected snapshot retains the version because this path really reads
    # it, rather than requiring dead historical storage in every later snapshot.
    annotation["ir_semantics"]["ir_return"]["events"].append({"effect": "context_read", "evidences": evidence,
        "atomic_ops": [{"op": "read", "location": "state", "output": "final_state", "evidences": evidence}]})
    from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
    annotation["sink_boundaries"] = [item.model_dump(mode="json") for item in derive_sink_boundaries(annotation["locations"], annotation["ir_semantics"])]
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    binding = result.records.get("ir_return").entry_state.get(FlowLocation(kind="runtime_context", name="state"))
    assert binding
    assert all(result.registry.get(identity).content.model_dump(mode="json") == {"form": "literal", "value": "new"} for identity in binding)
    observed = result.records.get("ir_append").events[1].atomic_ops[0].inputs[0]
    assert any(result.registry.get(identity).origin.acquired_from == "runtime_context:state" for identity in observed)


def test_nested_empty_member_views_skip_all_inner_effects():
    cfg, annotation = nested_loop_fixture([{"rows": []}, {"rows": []}])
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    assert result.coverage["ir_send"] == "not_reached"
    assert result.coverage["ir_return"] == "processed"
    assert result.records.is_complete


def test_ancestor_field_update_never_reuses_empty_old_parent_for_guard():
    from skillflow.propagation.data import DataRegistry, LiteralContent, FieldUpdatesContent, DataPart, Origin, SelectionContent
    from skillflow.propagation.loop_guards import guard_values
    registry = DataRegistry("ancestor-update")
    old = registry.register_source("old", acquired_from="source", content=LiteralContent(value={"rows": []}))
    item = registry.register_source("item", acquired_from="source", content=LiteralContent(value={"value": "new"}))
    updated = registry.create_result("update", content=FieldUpdatesContent(base=old.id, updates=[DataPart(path=["rows", 0], data=item.id)]), origin=Origin(at="update"))
    view = registry.create_result("view", content=SelectionContent(base=updated.id, path=["rows"]), origin=Origin(at="view"))
    assert guard_values(registry, [view.id], "nonempty") == {False, True}


def test_loop_resource_limit_is_not_reported_as_convergence():
    cfg, annotation = explicit_loop_fixture(tuple(str(index) for index in range(8)))
    result = propagate(cfg, annotation, max_variants=5)
    assert result.status == "resource_limit"
    assert any(row["code"] == "resource_limit" for row in result.diagnostics)


@pytest.mark.parametrize("arguments", [[], [literal("identical parameter")]])
def test_response_identity_includes_control_member_without_invented_request_payload(arguments):
    cfg, annotation = explicit_loop_fixture(("same", "same"))
    next(ir for ir in cfg["blocks"]["body"]["instructions"] if ir["id"] == "ir_fetch")["inputs"] = []
    operation = annotation["ir_semantics"]["ir_fetch"]["events"][0]["atomic_ops"][0]
    operation["inputs"] = arguments
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    received = result.records.get("ir_fetch").events[0].atomic_ops[0]
    assert len(received.outputs[0]) == 2
    assert len(received.alternatives) == 2
    assert len({tuple(candidate.bindings.items()) for candidate in received.alternatives}) == 2
    for identity in received.outputs[0]:
        value = result.registry.get(identity)
        assert len(value.origin.inputs) == len(arguments)
        assert all(item.relation == "possible" for item in value.origin.dependencies)
    member_ids = result.records.get("ir_member").events[0].atomic_ops[0].outputs[0]
    assert not set().union(*(set(result.registry.get(identity).origin.inputs) for identity in received.outputs[0])) & member_ids


def test_unsupported_typed_guard_does_not_stop_independent_sink_root():
    from skillflow.propagation.contracts.boundaries import derive_sink_boundaries
    cfg, annotation = explicit_loop_fixture(())
    annotation["ir_semantics"]["ir_guard"]["events"][0]["atomic_ops"][0]["predicate"] = "truthy"
    cfg["blocks"]["independent"] = {"block_id": "independent", "block_name": "independent", "instructions": [
        instruction("independent", [{"type": "literal", "literal_value": "visible"}], opcode="return")]}
    spec = deepcopy(annotation["ir_semantics"]["ir_fetch"])
    evidence = spec["events"][0]["evidences"]
    spec["output_bindings"] = []
    spec["events"] = [{"effect": "net_send", "evidences": evidence, "atomic_ops": [
        {"op": "deliver", "target": "api", "inputs": [input_ref()], "evidences": evidence}]}]
    annotation["ir_semantics"]["ir_independent"] = spec
    annotation["sink_boundaries"] = [value.model_dump(mode="json") for value in derive_sink_boundaries(annotation["locations"], annotation["ir_semantics"])]
    result = propagate(cfg, annotation)
    assert result.status == "incomplete", result.diagnostics
    assert result.coverage["ir_guard"] == "unresolved_binding"
    assert result.coverage["ir_independent"] == "processed"
    assert result.records.get("ir_independent").events[0].atomic_ops[0].inputs[0]


def test_late_unresolved_input_withdraws_previous_block_out(monkeypatch):
    """A newly unavailable prerequisite cannot leave a cached successful OUT."""
    from collections import Counter
    from skillflow.propagation.interpreter import TransferInterpreter, UnsupportedLoopDomain
    from skillflow.propagation.data import DataRegistry, KnownPartsContent
    evaluate = TransferInterpreter.evaluate
    counts = Counter()
    registry = DataRegistry("late-prerequisite")
    prerequisite = registry.register_source("ready", acquired_from="test:prerequisite")

    def late_failure(self, ir, spec, state):
        counts[ir["id"]] += 1
        if ir["id"] == "ir_fetch":
            value = self.registry.get(prerequisite.id)
            if isinstance(value.content, KnownPartsContent):
                raise UnsupportedLoopDomain("A later relation exposed an unsupported prerequisite")
        result = evaluate(self, ir, spec, state)
        if ir["id"] == "ir_append":
            self.registry.resolve_part(prerequisite.id, ["unavailable"])
        return result

    monkeypatch.setattr(TransferInterpreter, "evaluate", late_failure)
    result = propagate(*explicit_loop_fixture(("once",)), initial_registry=registry)
    assert counts["ir_append"] >= 1  # A successful OUT really existed first.
    assert result.status == "incomplete", result.diagnostics
    assert result.coverage["ir_fetch"] == "unresolved_binding"
    assert result.coverage["ir_return"] == "blocked"
    with pytest.raises(KeyError):
        result.records.get("ir_return")


def test_operation_alternatives_cannot_invent_outputs_or_change_arity():
    from pydantic import ValidationError
    from skillflow.propagation.models import AtomicOpRecord
    result = propagate(*explicit_loop_fixture(("once",)))
    record = result.records.get("ir_fetch").events[0].atomic_ops[0].model_dump(mode="json")
    wrong = deepcopy(record)
    wrong["alternatives"][0]["outputs"][0] = ["not-a-recorded-value"]
    with pytest.raises(ValidationError, match="recorded output slot"):
        AtomicOpRecord.model_validate(wrong)
    wrong = deepcopy(record)
    wrong["alternatives"][0]["inputs"].append([])
    with pytest.raises(ValidationError, match="slot arity"):
        AtomicOpRecord.model_validate(wrong)


def cached_handle_loop_fixture():
    """Finite may-state reuse, without computing a concrete cache hit order."""
    def block(name, instructions):
        return {"block_id": name, "block_name": name, "instructions": instructions}
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("seed", outputs=["items", "initial"]),
            instruction("initial_handle", [{"type": "literal", "literal_value": "initial-credential"}], ["first"]),
            instruction("initial_save", [operand("first")]), instruction("start", opcode="dispatch")]),
        "head": block("head", [instruction("merge", [operand("initial"), operand("next")], ["acc"]),
            instruction("guard", [operand("items")], opcode="dispatch")]),
        "body": block("body", [instruction("member", [operand("items")], ["item"]),
            instruction("select", [operand("item")], ["receiver", "credential"]),
            instruction("cached", outputs=["cached"]),
            instruction("send", [operand("receiver"), operand("cached")]),
            instruction("fetch", [operand("credential")], ["new_handle"]),
            instruction("save", [operand("new_handle")]),
            instruction("append", [operand("acc"), operand("new_handle")], ["next"]),
            instruction("back", opcode="dispatch")]),
        "exit": block("exit", [instruction("return", [operand("acc")], opcode="return")])},
        "edges": [{"source_block_id": a, "target_block_id": b} for a, b in
            [("entry", "head"), ("head", "body"), ("head", "exit"), ("body", "head")]]}
    acquire = ([], [(None, [{"op": "receive", "location": "factory", "inputs": [input_ref()], "output": "handle"}])], [local("handle")])
    write = (["context_write"], [(0, [{"op": "write", "target": "cache", "mode": "replace", "input": input_ref()}])], [])
    plans = {
        "seed": ([], [], [literal([{"receiver": "A", "credential": "credential-A"},
            {"receiver": "B", "credential": "credential-B"}]), literal([])]),
        "initial_handle": acquire, "initial_save": write, "fetch": acquire, "save": write,
        "merge": ([], [(None, [{"op": "merge", "incoming": [{"predecessor": "entry", "value": input_ref()},
            {"predecessor": "body", "value": input_ref(1)}], "output": "merged"}])], [local("merged")]),
        "guard": ([], [(None, [{"op": "branch", "input": input_ref(), "predicate": "has_member",
            "true_target": "body", "false_target": "exit"}])], []),
        "member": ([], [(None, [{"op": "member", "input": input_ref(), "output": "row"}])], [local("row")]),
        "select": (["transform"], [(0, [
            {"op": "select_part", "input": input_ref(), "path": ["receiver"], "output": "receiver"},
            {"op": "select_part", "input": input_ref(), "path": ["credential"], "output": "credential"}])], [local("receiver"), local("credential")]),
        "cached": (["context_read"], [(0, [{"op": "read", "location": "cache", "output": "cached"}])], [local("cached")]),
        "send": (["net_send"], [(0, [{"op": "deliver", "target": "api", "inputs": [input_ref(), input_ref(1)]}])], []),
        "append": ([], [(None, [{"op": "append", "input": input_ref(), "value": input_ref(1), "mode": "item", "output": "collected"}])], [local("collected")]),
    }
    return fixture_annotation(cfg, plans, {"factory": ("tool", "factory"), "cache": ("runtime_context", "cache"), "api": ("remote", "api")})


def identity_bases(registry, identity):
    """Transparent identity views; does not follow possible handle inputs."""
    result, pending = set(), [identity]
    while pending:
        current = pending.pop()
        if current in result:
            continue
        result.add(current)
        content = registry.get(current).content.model_dump(mode="json")
        options = [value["content"] for value in content["variants"]] if content["form"] == "loop_summary" else [content]
        pending.extend(value["base"] for value in options if value["form"] == "selection" and not value["path"])
    return result


def test_cached_handle_created_by_a_remains_available_to_b_without_new_acquisition():
    from skillflow.propagation.data.summary import content_options
    cfg, annotation = cached_handle_loop_fixture()
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    created = result.records.get("ir_fetch").events[0].atomic_ops[0].outputs[0]
    handles = {}
    for identity in created:
        value = result.registry.get(identity)
        handles[content_options(result.registry, value.origin.inputs[0])[0]["value"]] = identity
        assert value.origin.acquired_from == "tool:factory"
        assert all(dependency.relation == "possible" for dependency in value.origin.dependencies)
    assert set(handles) == {"credential-A", "credential-B"}
    assert handles["credential-A"] != handles["credential-B"]
    original = next(iter(result.records.get("ir_initial_handle").events[0].atomic_ops[0].outputs[0]))
    sent = result.records.get("ir_send").events[0].atomic_ops[0]
    delivered_to_b = set()
    for candidate in sent.alternatives:
        receiver = next(iter(candidate.inputs[0]))
        if content_options(result.registry, receiver) == [{"form": "literal", "value": "B"}]:
            for handle in candidate.inputs[1]:
                delivered_to_b |= identity_bases(result.registry, handle)
                if handle not in created and handle != original:
                    assert result.registry.get(handle).origin.acquired_from is None
    assert {original, handles["credential-A"], handles["credential-B"]} <= delivered_to_b
    assert result.registry.to_dict() == propagate(cfg, annotation, schedule="lifo").registry.to_dict()
    # Persisted snapshots have the same alias/version relationships as the live
    # result. Validation does not require a read to fabricate a new source.
    from skillflow.propagation.data import DataRegistry
    from skillflow.propagation.records import PropagationRecords
    from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts
    sealed = DataRegistry.from_dict(result.registry.to_dict())
    restored = PropagationRecords.from_records(result.records.records_dict(), cfg=cfg, annotation=annotation,
        data_registry=sealed, initial_data=result.initial_data, initial_state=result.initial_state)
    restored.validate(require_complete=True)
    outcome = validate_propagation_facts(cfg=cfg, annotation=annotation,
        data=[entry["data"] for entry in sealed.to_dict()["records"]], records=restored.records_dict(),
        sinks=resolved_sink_boundaries(annotation["locations"], restored.records_dict()), status=result.status,
        coverage=result.coverage, diagnostics=result.diagnostics)
    assert outcome["status"] == "complete"


def paired_carry_fixture(*, higher_generation=False):
    def block(name, instructions):
        return {"block_id": name, "block_name": name, "instructions": instructions}
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("seed", outputs=["items", "x0", "y0"]), instruction("start", opcode="dispatch")]),
        "head": block("head", [instruction("merge_x", [operand("x0"), operand("next_x")], ["old_x"]),
            instruction("merge_y", [operand("y0"), operand("next_y")], ["old_y"]),
            instruction("guard", [operand("items")], opcode="dispatch")]),
        "body": block("body", [instruction("member", [operand("items")], ["item"]),
            instruction("receiver", [operand("item")], ["receiver"]),
            instruction("send", [operand("receiver"), operand("old_x"), operand("old_y")]),
            instruction("x", [operand("old_x"), operand("receiver")] if higher_generation else [operand("item")], ["next_x"]),
            instruction("y", [operand("old_y"), operand("receiver")] if higher_generation else [operand("item")], ["next_y"]),
            instruction("back", opcode="dispatch")]),
        "exit": block("exit", [instruction("return", opcode="return")])},
        "edges": [{"source_block_id": a, "target_block_id": b} for a, b in
            [("entry", "head"), ("head", "body"), ("head", "exit"), ("body", "head")]]}
    plans = {
        "seed": ([], [], [literal([{"receiver": "A", "x": "xA", "y": "yA"},
            {"receiver": "B", "x": "xB", "y": "yB"}]), literal("x0"), literal("y0")]),
        "guard": ([], [(None, [{"op": "branch", "input": input_ref(), "predicate": "has_member",
            "true_target": "body", "false_target": "exit"}])], []),
        "member": ([], [(None, [{"op": "member", "input": input_ref(), "output": "row"}])], [local("row")]),
        "receiver": (["transform"], [(0, [{"op": "select_part", "input": input_ref(), "path": ["receiver"], "output": "r"}])], [local("r")]),
        "send": (["net_send"], [(0, [{"op": "deliver", "target": "api", "inputs": [input_ref(), input_ref(1), input_ref(2)]}])], []),
    }
    for name in ("x", "y"):
        plans["merge_" + name] = ([], [(None, [{"op": "merge", "incoming": [
            {"predecessor": "entry", "value": input_ref()}, {"predecessor": "body", "value": input_ref(1)}], "output": "prior"}])], [local("prior")])
        operation = ({"op": "compute", "inputs": [input_ref(), input_ref(1)], "dependencies": ["possible", "possible"], "output": "next"}
                     if higher_generation else {"op": "select_part", "input": input_ref(), "path": [name], "output": "next"})
        plans[name] = (["transform"], [(0, [operation])], [local("next")])
    return fixture_annotation(cfg, plans, {"api": ("remote", "api")})


def test_two_header_merges_preserve_same_backedge_tuple_at_next_member():
    from skillflow.propagation.data.summary import content_options
    result = propagate(*paired_carry_fixture())
    assert result.status == "complete", result.diagnostics
    pairs = set()
    for candidate in result.records.get("ir_send").events[0].atomic_ops[0].alternatives:
        values = [content_options(result.registry, next(iter(slot))) for slot in candidate.inputs]
        assert all(len(value) == 1 and value[0]["form"] == "literal" for value in values)
        pairs.add(tuple(value[0]["value"] for value in values))
    assert pairs == {(receiver, x, y) for receiver in ("A", "B") for x, y in (("x0", "y0"), ("xA", "yA"), ("xB", "yB"))}
    from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts
    cfg, annotation = paired_carry_fixture()
    records = result.records.records_dict()
    operation = records["ir_send"]["events"][0]["atomic_ops"][0]
    x = next(identity for identity in operation["inputs"][1]
             if content_options(result.registry, identity) == [{"form": "literal", "value": "xA"}])
    y = next(identity for identity in operation["inputs"][2]
             if content_options(result.registry, identity) == [{"form": "literal", "value": "yB"}])
    operation["alternatives"][0].update(inputs=[operation["alternatives"][0]["inputs"][0], [x], [y]], bindings={})
    with pytest.raises(ValueError, match="incompatible incoming/member tuple"):
        validate_propagation_facts(cfg=cfg, annotation=annotation,
            data=[entry["data"] for entry in result.registry.to_dict()["records"]], records=records,
            sinks=resolved_sink_boundaries(annotation["locations"], records), status=result.status,
            coverage=result.coverage, diagnostics=result.diagnostics)


def test_higher_generation_correlation_stops_locally_without_guessing_pairs():
    result = propagate(*paired_carry_fixture(higher_generation=True))
    assert result.status == "incomplete", result.diagnostics
    assert any("correlation across multiple generations" in value["reason"] for value in result.diagnostics)
    assert result.coverage["ir_seed"] == "processed"
    assert result.records.get("ir_send").events[0].atomic_ops[0].alternatives
    assert result.stats["block_evaluations"] < 100


@pytest.mark.parametrize("other_context,allowed", [
    ({}, True),
    ({"member:rows": "C"}, True),
    ({"incoming:member:other": "A"}, True),
    ({"incoming:member:rows": "A"}, False),
    ({"unresolved:member:rows": "multiple_generations"}, False),
])
def test_single_unresolved_value_only_requires_shared_historical_pairing(other_context, allowed):
    from skillflow.propagation.data import DataRegistry, LiteralContent, OpaqueContent, Origin
    from skillflow.propagation.loop_domain import LoopFactRegistry
    from skillflow.propagation.interpreter import TransferInterpreter, UnsupportedLoopDomain
    registry = LoopFactRegistry(DataRegistry("carried-choice-test"), {})
    cursor = registry.family("loop", ["cursor"], [], OpaqueContent(), Origin(at="cursor"), bindings={
        "member:rows": "C", "incoming:member:rows": "A", "unresolved:member:rows": "multiple_generations"}).id
    parameter = registry.family("loop", ["parameter"], [], LiteralContent(value=100), Origin(at="parameter"),
                                bindings=other_context).id
    interpreter = TransferInterpreter(*explicit_loop_fixture(), registry)
    if allowed:
        assert list(interpreter._tuples([{cursor}, {parameter}])) == [(cursor, parameter)]
    else:
        with pytest.raises(UnsupportedLoopDomain, match="correlation across multiple generations"):
            list(interpreter._tuples([{cursor}, {parameter}]))
    # Repeated references to the same value do not invent a second choice.
    assert list(interpreter._tuples([{cursor}, {cursor}])) == [(cursor, cursor)]
    incompatible = registry.family("loop", ["wrong-current-member"], [], LiteralContent(value=100),
        Origin(at="wrong-current-member"), bindings={"member:rows": "D", "incoming:member:rows": "A"}).id
    assert list(interpreter._tuples([{cursor}, {incompatible}])) == []


def test_repeated_cursor_with_fixed_parameter_and_current_receiver_converges():
    def block(name, instructions):
        return {"block_id": name, "block_name": name, "instructions": instructions}
    cfg = {"entry_block_id": "entry", "blocks": {
        "entry": block("entry", [instruction("seed", outputs=["items", "initial"]), instruction("start", opcode="dispatch")]),
        "head": block("head", [instruction("merge", [operand("initial"), operand("next")], ["cursor"]),
            instruction("guard", [operand("items")], opcode="dispatch")]),
        "body": block("body", [instruction("member", [operand("items")], ["receiver"]),
            instruction("request", [operand("cursor"), operand("receiver")]),
            instruction("advance", [operand("cursor"), operand("receiver")], ["next"]), instruction("back", opcode="dispatch")]),
        "exit": block("exit", [instruction("return", [operand("cursor")], opcode="return")])},
        "edges": [{"source_block_id": a, "target_block_id": b} for a, b in
            [("entry", "head"), ("head", "body"), ("head", "exit"), ("body", "head")]]}
    plans = {
        "seed": ([], [], [literal(["A", "B"]), literal("initial-cursor")]),
        "merge": ([], [(None, [{"op": "merge", "incoming": [
            {"predecessor": "entry", "value": input_ref()}, {"predecessor": "body", "value": input_ref(1)}], "output": "prior"}])], [local("prior")]),
        "guard": ([], [(None, [{"op": "branch", "input": input_ref(), "predicate": "has_member",
            "true_target": "body", "false_target": "exit"}])], []),
        "member": ([], [(None, [{"op": "member", "input": input_ref(), "output": "receiver"}])], [local("receiver")]),
        "request": (["net_send"], [(0, [{"op": "deliver", "target": "api", "inputs": [input_ref(), literal(100), input_ref(1)]}])], []),
        "advance": (["transform"], [(0, [{"op": "compute", "inputs": [input_ref(), input_ref(1)],
            "dependencies": ["possible", "possible"], "output": "next"}])], [local("next")]),
    }
    cfg, annotation = fixture_annotation(cfg, plans, {"api": ("remote", "api")})
    result = propagate(cfg, annotation)
    assert result.status == "complete", result.diagnostics
    requests = result.records.get("ir_request").events[0].atomic_ops[0].alternatives
    assert any(any(key.startswith("unresolved:") for key in candidate.bindings) for candidate in requests)
    assert result.stats["block_evaluations"] < 100
    assert result.registry.to_dict() == propagate(cfg, annotation, schedule="lifo").registry.to_dict()
    from skillflow.propagation.facts import resolved_sink_boundaries, validate_propagation_facts
    records = result.records.records_dict()
    outcome = validate_propagation_facts(cfg=cfg, annotation=annotation,
        data=[entry["data"] for entry in result.registry.to_dict()["records"]], records=records,
        sinks=resolved_sink_boundaries(annotation["locations"], records), status=result.status,
        coverage=result.coverage, diagnostics=result.diagnostics)
    assert outcome["status"] == "complete"
