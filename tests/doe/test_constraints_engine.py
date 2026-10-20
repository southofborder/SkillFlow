"""Executable baseline counterparts of the independent constraint design cases.

These tests exercise bounded semantic inputs. They do not claim source-language
extraction completeness, candidate eligibility, or reduced-task equivalence.
The preservation half of the matrix is tested by the integration suite.
"""
from copy import deepcopy
from types import SimpleNamespace

import pytest
from pydantic import TypeAdapter, ValidationError

from skillflow.doe.constraint_engine import ConstraintEngine
from skillflow.propagation.contracts.constraints import TaskConstraint
from skillflow.propagation.contracts.references import target_key


def literal(value):
    return {"op": "literal", "value": value}


class World:
    """Small immutable-index fixture: alternatives remain alternatives."""
    def __init__(self):
        self.data, self.ops, self.targets, self.expressions = {}, {}, {}, {}
        self.nodes, self.locals, self.elements, self.definitions = {}, {}, {}, {}
        self.instructions, self.blocks, self.edges, self.records = {}, {}, [], {}
        self.coverage, self.semantics, self.raw_semantics, self.links = {}, {}, {}, {}
        self.mapping, self.constraints = [], []
        self.entry = None
        self.locations = {"panel": {"kind": "tool", "name": "Display"},
                          "archive": {"kind": "storage", "name": "Archive"},
                          "model": {"kind": "model_context", "name": "Model"}}
        self.add_data("source", {"form": "literal", "value": {"grid": "private", "label": "public"}})

    def add_data(self, name, content, **origin):
        self.data[name] = {"id": name, "content": content,
                           "origin": {"inputs": [], "dependencies": [], **origin}}
        return name

    def ir(self, name, *, order="fixed"):
        if name in self.instructions:
            return name
        self.instructions[name] = {"id": name, "inputs": [{"type": "context", "identifier": name}], "outputs": []}
        self.blocks[name] = {"instructions": [self.instructions[name]]}
        self.entry = self.entry or name
        self.coverage[name] = "processed"
        self.semantics[name] = {"order": order, "events": [], "precedence": [], "output_bindings": []}
        self.raw_semantics[name] = {"events": []}
        self.records[name] = {"events": []}
        self.bind(name, "input", "source")
        self.target({"instruction_id": name, "path": []}, [], name)
        return name

    def target(self, ref, path, ir):
        self.targets[target_key(ref)] = {"raw_path": path, "instruction_id": ir}
        return ref

    def bind(self, ir, name, data, scope=None):
        key = f"node:{ir}:{scope}:{name}"
        self.nodes[key] = {"data_ids": [data] if isinstance(data, str) else data}
        self.locals[(ir, scope, name)] = key
        return key

    def node_at(self, kind, ir, op=None, slot=None):
        return self.locals.get((ir, None, "input")) if kind == "ir_input" else None

    def op(self, ir, name, *, payload="source", action="deliver", target="panel", when=None,
           generated=False, raw_index=None):
        self.ir(ir)
        e = len(self.semantics[ir]["events"])
        spec = {"op": action, "inputs": [{"kind": "input", "index": 0}], "target": target}
        if when is not None:
            spec["when"] = when
        path = ["events", 0, "events", e if raw_index is None else raw_index, "atomic_ops", 0]
        record = {"op": action, "inputs": [[payload]], "outputs": []}
        self.semantics[ir]["events"].append({"atomic_ops": [spec]})
        self.records[ir]["events"].append({"atomic_ops": [record]})
        self.ops[name] = {"position": {"instruction_id": ir, "event_index": e, "op_index": 0,
                            "body_event_index": None, "instance_index": None},
                          "spec": spec, "record": record, "scope": None,
                          "raw_op": None if generated else tuple(path), "segment": ("events", 0),
                          "generated": generated}
        self.mapping.append({"kind": "observation" if generated else "retained", "instruction_id": ir,
            "compiled_path": ["ir_semantics", ir, "events", e],
            "raw_path": ["ir_semantics", ir, *path[:-2]], "raw_atomic_range": [0, 1]})
        return self.target({"instruction_id": ir, "operation_path": path, "slot": {"kind": "self"}}, path, ir)

    def expression(self, ir, expr=None, *, path=None):
        self.ir(ir)
        path = path or ["events", 0, "events", 100, "atomic_ops", 0]
        ref = self.target({"instruction_id": ir, "operation_path": path, "slot": {"kind": "self"}}, path, ir)
        if expr is not None:
            self.expressions[(ir, tuple(path))] = expr
        return ref

    def edge(self, source, target, expr=None):
        self.ir(source)
        self.ir(target)
        index = len(self.edges)
        self.edges.append({"source_block_id": source, "target_block_id": target})
        if expr is not None:
            self.target({"path": ["edges", index]}, ["edges", index], source)
            self.expressions[(source, ("edges", index))] = expr

    def foreach(self, *, size=2, bodies=1, guards=None, order="fixed"):
        ir = self.ir("members", order=order)
        content = {"form": "opaque"} if size is None else {"form": "literal", "value": ["equal"] * size}
        self.add_data("collection", content)
        self.raw_semantics[ir]["events"] = [{"kind": "for_each"}]
        self.semantics[ir]["events"] = [{"kind": "for_each", "body": [{"atomic_ops": [{"op": "deliver", "inputs": [], "target": "panel"}]} for _ in range(bodies)]}]
        count = 1 if size is None else size
        self.records[ir]["events"] = [{"collections": ["collection"], "instances": [{} for _ in range(count)]}]
        refs = []
        for b in range(bodies):
            path = ["events", 0, "body", 0, "events", b, "atomic_ops", 0]
            ref = self.target({"instruction_id": ir, "operation_path": path, "slot": {"kind": "self"}}, path, ir)
            refs.append(ref)
            for member in range(count):
                spec = deepcopy(self.semantics[ir]["events"][0]["body"][b]["atomic_ops"][0])
                if guards is not None:
                    spec["when"] = {"kind": "literal", "value": guards[member][b]}
                key = f"member:{member}:{b}"
                self.ops[key] = {"position": {"instruction_id": ir, "event_index": 0, "op_index": 0,
                    "body_event_index": b, "instance_index": member}, "spec": spec,
                    "record": {"op": "deliver", "inputs": [["source"]], "outputs": []},
                    "scope": (0, member), "raw_op": tuple(path), "segment": ("events", 0, "body", 0), "generated": False}
        return refs

    def information(self, *, source="main", events=None, path=None, receivers=None):
        self.ir(source)
        return {"kind": "forbid_information", "scope": {"kind": "task"},
                "source": {"instruction_id": source, "scope_path": [], "value": {"kind": "input", "index": 0}},
                "path": ["grid"] if path is None else path, "events": events,
                "receivers": receivers or {"kind": "locations", "ids": ["panel"]}}

    def engine(self, constraint):
        realizations = [{"requirement_id": "R", "constraints": [constraint]}]
        raw = {"ir_semantics": self.raw_semantics, "realizations": realizations}
        compiled = {"ir_semantics": self.semantics, "realizations": realizations, "locations": self.locations,
                    "task_ref": {"task_sha256": "a" * 64}}
        facts = SimpleNamespace(cfg={"entry_block_id": self.entry, "blocks": self.blocks, "edges": self.edges},
                                records=self.records, coverage=self.coverage)
        return SimpleNamespace(facts=facts, raw=raw, compiled=compiled, ops=self.ops, targets=self.targets,
            expressions=self.expressions, nodes=self.nodes, locals=self.locals, elements=self.elements,
            definitions=self.definitions, node_at=self.node_at,
            annotation={"mapping": {"events": self.mapping}},
            index=SimpleNamespace(data=self.data, instructions=self.instructions, links=self.links))


def bounded(events, limit=1, scope=None, **extra):
    return {"kind": "at_most", "scope": scope or {"kind": "task"}, "events": events,
            "limit": limit, "unit": "attempt", **extra}


def prior(before, after, scope=None):
    return {"kind": "requires_prior", "scope": scope or {"kind": "task"},
            "before": before, "after": after, "matching": "scope"}


ELEMENT = {"kind": "element", "instruction_id": "members", "scope_path": ["events", 0]}
STATUSES = {
    "IP-A": "potential_violation", "IP-B": "potential_violation", "IP-C": "potential_violation",
    "IP-D": "potential_violation", "IP-E": "satisfied", "IP-F": "satisfied", "IP-G": "satisfied",
    "IP-H": "potential_violation", "IP-I": "potential_violation", "IP-J": "rejected",
    "EC-A": "satisfied", "EC-B": "potential_violation", "EC-C": "satisfied", "EC-D": "not_established",
    "EC-E": "satisfied", "EC-F": "potential_violation", "EC-G": "potential_violation",
    "OC-A": "satisfied", "OC-B": "potential_violation", "OC-C": "not_established", "OC-D": "satisfied",
    "OC-E": "not_established", "OC-F": "satisfied", "OC-G": "satisfied", "OC-H": "potential_violation",
    "OC-I": "potential_violation", "OR-A": "satisfied", "OR-B": "potential_violation", "OR-C": "potential_violation",
    "OR-D": "potential_violation", "OR-E": "satisfied", "OR-F": "satisfied", "X-A": "satisfied",
    "X-B": "not_established", "X-C": "not_established", "X-D": "not_established", "X-E": "not_established",
    "X-F": "rejected", "X-G": "not_established", "X-H": "not_established", "X-I": "potential_violation",
    "X-J": "satisfied", "X-K": "potential_violation", "X-L": "satisfied",
}


def scenario(case):
    w, options = World(), {}
    if case.startswith("IP-") or case in {"X-B", "X-I", "X-K", "X-L", "X-E"}:
        op = w.op("main", "delivery", action="write" if case == "IP-I" else "deliver",
                  target="archive" if case in {"IP-E", "IP-I"} else "panel")
        c = w.information(receivers={"kind": "all"} if case == "IP-I" else None)
        if case == "IP-B":
            w.add_data("texture", {"form": "opaque"}, inputs=["source"])
            w.ops["delivery"]["record"]["inputs"] = [["texture"]]
        if case in {"IP-C", "IP-F"}:
            w.add_data("clean", {"form": "whole_except", "base": "source", "excluded_parts": [["grid"]]})
            if case == "IP-C":
                w.op("main", "clean-delivery", payload="clean")
            else:
                w.ops["delivery"]["record"]["inputs"] = [["clean"]]
        if case == "IP-G":
            w.add_data("replacement", {"form": "literal", "value": "replica"})
            w.add_data("new-version", {"form": "field_updates", "base": "source", "updates": [{"path": ["grid"], "data": "replacement"}]})
            w.ops["delivery"]["record"]["inputs"] = [["new-version"]]
        if case == "IP-J":
            c["property"] = "any_causal_influence"
        if case == "X-B":
            w.op("main", "third-delivery")
            w.coverage["main"] = "incomplete"
        if case == "X-E":
            c["events"] = [{"instruction_id": "absent", "path": []}]
        if case == "X-L":
            w.ir("entry")
            w.entry = "entry"
    elif case.startswith("EC-") or case in {"X-C", "X-D", "X-G"}:
        if case == "EC-G":
            refs = w.foreach()
            condition = w.expression("members", {"op": "ref", "value": {"kind": "local", "name": "clear"}},
                                     path=["events", 0, "body", 0, "events", 99, "atomic_ops", 0])
            for member, truth in enumerate((True, False)):
                w.add_data(f"truth-{member}", {"form": "literal", "value": truth})
                w.elements[("members", (0, member), "clear")] = w.bind("members", "clear", f"truth-{member}", (0, member))
            c = {"kind": "only_if", "scope": ELEMENT, "events": refs, "condition": condition}
        else:
            w.ir("entry")
            event = w.op("event", "illumination")
            p = {"op": "ref", "value": {"kind": "input", "index": 0}}
            condition = w.expression("event", None if case in {"EC-D", "X-C", "X-D", "X-G"} else p)
            c = {"kind": "only_if", "scope": {"kind": "task"}, "events": [event], "condition": condition}
            w.edge("entry", "event", p if case in {"EC-A", "EC-E"} else None)
            if case == "EC-B":
                w.expressions[("event", tuple(condition["operation_path"]))] = literal(False)
                w.edges.clear()
                w.edge("entry", "event", literal(True))
            elif case == "EC-C":
                w.edges.clear()
                w.edge("entry", "middle", p)
                w.edge("middle", "event", {"op": "not", "arg": p})
            elif case == "EC-F":
                w.expressions[("event", tuple(condition["operation_path"]))] = literal(False)
            w.add_data("flag", {"form": "opaque"})
            for ir in w.instructions:
                w.instructions[ir]["inputs"] = [{"type": "result", "identifier": "same-flag-version"}]
                w.bind(ir, "input", "flag")
    elif case.startswith("OC-") or case in {"X-A", "X-H", "X-J"}:
        if case in {"OC-D", "OC-E", "OC-G"}:
            refs = w.foreach(size=None if case == "OC-E" else 4 if case == "OC-D" else 2)
            c = bounded(refs, 4 if case != "OC-G" else 1, scope=ELEMENT if case == "OC-G" else None)
        elif case == "OC-A":
            w.ir("entry")
            one, two = w.op("left", "left-pulse"), w.op("right", "right-pulse")
            w.edge("entry", "left")
            w.edge("entry", "right")
            c = bounded([one, two])
        else:
            one = w.op("main", "attempt")
            refs = [one]
            if case in {"OC-B", "OC-C", "OC-I"}:
                refs += [w.op("main", f"attempt-{i}") for i in range(1, 2 if case == "OC-I" else 3)]
            if case == "OC-F":
                w.op("main", "response", action="receive")
                w.op("main", "observation", generated=True)
                refs = [{"instruction_id": "main", "path": []}]
            if case == "OC-H":
                w.edge("main", "main")
            if case == "X-A":
                refs.append(w.op("unreachable", "coverage-root-pulse"))
            c = bounded(refs, 2 if case in {"OC-B", "OC-C"} else 1)
            if case == "OC-C":
                c.update(unit="success", success=w.expression("main"))
            if case == "X-H":
                options["max_states"] = 1
            if case == "X-J":
                later = w.op("retry", "retry")
                w.edge("main", "retry", literal(False))
                c["events"].append(later)
    elif case == "X-F":
        event = w.op("main", "event")
        c = bounded([event], scope={"kind": "element", "instruction_id": "main", "scope_path": ["events", 0, "body", 0]})
    else:
        if case in {"OR-A", "OR-D"}:
            refs = w.foreach(bodies=2, guards=[[True, False], [False, True]] if case == "OR-D" else None)
            c = prior([refs[0]], [refs[1]], ELEMENT)
        else:
            w.ir("main", order="partial" if case == "OR-B" else "fixed")
            before = w.op("main", "registration")
            after = w.op("main", "seal")
            c = prior([before], [after])
            if case in {"OR-C", "OR-E"}:
                c = {"kind": "forbid_after", "scope": {"kind": "task"},
                     "triggers": [before], "events": [after]}
                if case == "OR-E":
                    c["triggers"], c["events"] = [after], [before]
            elif case == "OR-F":
                w.ir("entry")
                w.entry = "entry"
    return w, c, options


@pytest.mark.parametrize("case,expected", list(STATUSES.items()), ids=[f"CA-{case}" for case in STATUSES])
def test_design_matrix_baseline(case, expected):
    world, declaration, options = scenario(case)
    if expected == "rejected":
        with pytest.raises(ValidationError):
            TypeAdapter(TaskConstraint).validate_python(declaration)
        return
    engine = world.engine(declaration)
    before = deepcopy((engine.raw, engine.compiled, engine.ops, engine.index.data, engine.nodes))
    checker = ConstraintEngine(engine, **options)
    result, = checker.check().values()
    assert result["status"] == expected, result
    assert set(result["operations"]) <= engine.ops.keys()
    assert set(result["witness"]) <= engine.ops.keys()
    assert before == (engine.raw, engine.compiled, engine.ops, engine.index.data, engine.nodes)
    assert checker.check() == checker.check()
    if case in {"EC-D", "X-C", "X-H"}:
        assert checker.complete_scope(next(iter(checker.constraints)))
    if case in {"X-B", "X-E"}:
        assert not checker.complete_scope(next(iter(checker.constraints)))
    if case.startswith("IP-") or case in {"X-I", "X-K", "X-L"}:
        assert not result["structural"]


def test_whole_original_content_ban_covers_selected_proper_part():
    world = World()
    world.add_data("part", {"form": "literal", "value": "private"}, part_of="source", path=["grid"])
    world.op("main", "delivery", payload="part")
    result, = ConstraintEngine(world.engine(world.information(path=[]))).check().values()
    assert result["status"] == "potential_violation"
    assert any("direct route" in reason for reason in result["reasons"])


def test_generated_observation_is_selected_by_original_processing_site():
    world = World()
    source = world.op("main", "read", action="read")
    world.op("main", "observe", target="model", generated=True, raw_index=0)
    c = world.information(events=[source], receivers={"kind": "kind", "value": "model_context"})
    result, = ConstraintEngine(world.engine(c)).check().values()
    assert result["operations"] == ["observe"]
    assert result["status"] == "potential_violation"


@pytest.mark.parametrize("form", ["whole_except", "field_updates"])
def test_edited_container_cannot_reuse_ancestor_literal_for_boolean_proof(form):
    from skillflow.doe.constraint_control import literal_at, UNKNOWN
    world = World()
    world.add_data("replacement", {"form": "literal", "value": "replica"})
    content = {"form": form, "base": "source"}
    if form == "whole_except":
        content["excluded_parts"] = [["grid"]]
    else:
        content["updates"] = [{"path": ["grid"], "data": "replacement"}]
    world.add_data("edited", content)
    assert literal_at(world.data, "edited") is UNKNOWN
    assert literal_at(world.data, "edited", ["label"]) == "public"


def test_zero_transfer_instruction_counts_once_and_has_no_invented_operation_key():
    world = World()
    world.ir("return")
    declaration = bounded([{"instruction_id": "return", "path": []}], 0)
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "potential_violation"
    assert result["operations"] == result["witness"] == []


@pytest.mark.parametrize("size", [0, 2])
def test_known_collection_task_bound_is_not_value_independent_structural_proof(size):
    world = World()
    declaration = bounded(world.foreach(size=size), 2)
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "satisfied"
    assert not result["structural"]


def test_loop_revisit_does_not_reset_an_existing_member_count():
    world = World()
    declaration = bounded(world.foreach(size=2), 1, scope=ELEMENT)
    world.edge("members", "members")
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "not_established"
    assert not result["structural"]


@pytest.mark.parametrize("order,expected", [("fixed", "satisfied"), ("partial", "potential_violation")])
def test_request_pair_association_does_not_replace_prior_occurrence(order, expected):
    world = World()
    world.ir("main", order=order)
    request = world.op("main", "request")
    response = world.op("main", "response", action="receive")
    world.links["pair"] = {"kind": "request_response", "source": "request", "target": "response"}
    declaration = {**prior([request], [response]), "matching": "request"}
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == expected
    assert not result["structural"]


def test_other_request_cannot_satisfy_matched_request_precedence():
    world = World()
    first = world.op("main", "first-request")
    response = world.op("main", "response", action="receive")
    second = world.op("main", "matched-request")
    world.links["pair"] = {"kind": "request_response", "source": "matched-request", "target": "response"}
    declaration = {**prior([first, second], [response]), "matching": "request"}
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "potential_violation"


def test_count_selectors_cannot_double_count_a_paired_request_and_response():
    world = World()
    request = world.op("main", "request")
    response = world.op("main", "response", action="receive")
    world.links["pair"] = {"kind": "request_response", "source": "request", "target": "response"}
    result, = ConstraintEngine(world.engine(bounded([request, response]))).check().values()
    assert result["status"] == "not_established"
    assert any("single occurrence unit" in reason for reason in result["reasons"])
    whole = bounded([{"instruction_id": "main", "path": []}])
    result, = ConstraintEngine(world.engine(whole)).check().values()
    assert result["status"] == "satisfied"


def test_real_condition_cannot_reuse_a_local_produced_after_the_event():
    from tests.doe.test_demand_engine import fixture, inp, local, literal as value_literal, solve, candidate
    values = fixture([
        {"op": "select_part", "input": inp(), "path": ["body"], "output": "early"},
        {"op": "compute", "inputs": [value_literal(True)], "dependencies": ["derived"], "output": "later"},
        {"op": "compute", "inputs": [local("later")], "dependencies": ["derived"], "output": "condition"}])
    targets = values[3]
    operations = {entry["value"].get("output"): entry["target"] for entry in targets.values()
                  if entry["kind"] == "operation" and entry.get("instruction_id") == "ir_filter"}
    requested = candidate(targets)
    from tests.doe.test_demand_engine import evidence
    requested["expressions"] = [{"target": operations["condition"],
        "expression": {"op": "ref", "value": local("later")}, "evidences": [evidence()]}]
    engine, _ = solve(values, requested)
    declaration = {"kind": "only_if", "scope": {"kind": "task"},
                   "events": [operations["early"]], "condition": operations["condition"]}
    engine.raw["realizations"][0]["constraints"] = [deepcopy(declaration)]
    engine.compiled["realizations"][0]["constraints"] = [deepcopy(declaration)]
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == "not_established", result
    assert any("not established before" in reason for reason in result["reasons"])


def test_implementation_fault_is_not_reported_as_an_unsupported_constraint(monkeypatch):
    world = World()
    checker = ConstraintEngine(world.engine(bounded([world.op("main", "event")])))
    def fault(*args, **kwargs):
        raise KeyError("injected implementation fault")
    monkeypatch.setattr(checker, "_walk", fault)
    with pytest.raises(KeyError, match="injected implementation fault"):
        checker.check()


def test_success_count_can_use_the_counted_completion_output():
    world = World()
    completion = world.op("main", "completion", action="receive")
    world.add_data("successful", {"form": "literal", "value": True})
    world.ops["completion"]["spec"]["output"] = "response"
    world.ops["completion"]["record"]["outputs"] = [["successful"]]
    world.bind("main", "response", "successful")
    predicate = world.expression("main", {"op": "ref", "value": {"kind": "local", "name": "response"}})
    declaration = bounded([completion], 0, unit="success", success=predicate)
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "potential_violation", result


@pytest.mark.parametrize("reverse_branches", [False, True])
def test_branch_join_retains_the_path_without_the_required_value_version(reverse_branches):
    world = World()
    world.ir("entry")
    world.op("producer", "produce-flag", action="compute")
    world.ops["produce-flag"]["spec"]["output"] = "ready"
    world.add_data("true-value", {"form": "literal", "value": True})
    world.ops["produce-flag"]["record"]["outputs"] = [["true-value"]]
    world.bind("producer", "ready", "true-value")
    world.ir("bypass")
    event = world.op("join", "illumination")
    condition = world.expression("producer", {"op": "ref", "value": {"kind": "local", "name": "ready"}})
    for branch in (["bypass", "producer"] if reverse_branches else ["producer", "bypass"]):
        world.edge("entry", branch)
        world.edge(branch, "join")
    declaration = {"kind": "only_if", "scope": {"kind": "task"}, "events": [event], "condition": condition}
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "not_established"
    assert any("not established before" in reason for reason in result["reasons"])


@pytest.mark.parametrize("values,expected", [([7], "not_established"), ([True, 7], "not_established"), ([True], "satisfied")])
def test_real_boolean_tautology_does_not_booleanize_nonboolean_local_candidates(values, expected):
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints, raw_operation
    from skillflow.propagation.annotation.binding_examples import inp, local, literal as operand_literal, evidence
    value = {"op": "ref", "value": local("number")}
    expression = {"op": "or", "args": [value, {"op": "not", "arg": value}]}
    source = inp() if len(values) == 1 else {"kind": "alternatives", "items": [inp(i) for i in range(len(values))]}
    base = synthetic_fixture([
        {"op": "select_part", "input": source, "path": ["ready"], "output": "number"},
        {"op": "compute", "inputs": [local("number")], "dependencies": ["derived"], "output": "formatted",
         "expression": {"expression": expression, "evidences": [evidence()]}},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ], inputs=[operand_literal({"ready": item}) for item in values])
    case = with_constraints(base, [{"kind": "only_if", "scope": {"kind": "task"},
        "events": [raw_operation(2)], "condition": raw_operation(1)}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == expected, result
    if expected == "not_established":
        assert any("not Boolean" in reason for reason in result["reasons"])


@pytest.mark.parametrize("value", [{}, 7])
def test_real_boolean_field_tautology_cannot_turn_definite_absence_or_invalid_access_into_truth(value):
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints, raw_operation
    from skillflow.propagation.annotation.binding_examples import inp, local, literal as operand_literal, evidence
    field = {"op": "field", "arg": {"op": "ref", "value": local("selected")}, "path": ["missing"]}
    expression = {"op": "or", "args": [field, {"op": "not", "arg": field}]}
    base = synthetic_fixture([
        {"op": "select_part", "input": inp(), "path": ["ready"], "output": "selected"},
        {"op": "compute", "inputs": [local("selected")], "dependencies": ["derived"], "output": "formatted",
         "expression": {"expression": expression, "evidences": [evidence()]}},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ], inputs=[operand_literal({"ready": value})])
    case = with_constraints(base, [{"kind": "only_if", "scope": {"kind": "task"},
        "events": [raw_operation(2)], "condition": raw_operation(1)}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == "not_established", result
    assert any("definitely absent or invalid" in reason for reason in result["reasons"])


@pytest.mark.parametrize("version,expected", [("whole", "potential_violation"), ("excluded", "satisfied"), ("overwritten", "satisfied")])
def test_real_selected_child_prohibition_reaches_whole_without_reviving_removed_versions(version, expected):
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints
    from skillflow.propagation.annotation.binding_examples import inp, local
    operations = [{"op": "select_part", "input": inp(), "path": ["service_note"], "output": "note"}]
    payload = inp()
    if version == "excluded":
        operations.append({"op": "exclude_parts", "input": inp(), "paths": [["service_note"]], "output": "clean"})
        payload = local("clean")
    elif version == "overwritten":
        operations.append({"op": "update_fields", "input": inp(),
            "updates": [{"path": ["service_note"], "value": {"kind": "literal", "value": "replacement"}}], "output": "clean"})
        payload = local("clean")
    operations.append({"op": "deliver", "target": "label_receiver", "inputs": [payload]})
    base = synthetic_fixture(operations, output="note")
    case = with_constraints(base, [{"kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_format", "scope_path": [], "value": local("note")},
        "path": [], "receivers": {"kind": "locations", "ids": ["label_receiver"]}}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == expected, result


def test_real_selected_child_ban_also_covers_an_earlier_whole_model_observation():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints
    from skillflow.propagation.annotation.binding_examples import inp, local
    base = synthetic_fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["possible"], "output": "draft"},
        {"op": "select_part", "input": inp(), "path": ["service_note"], "output": "note"},
    ], output="note", processing_mode="default")
    case = with_constraints(base, [{"kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_format", "scope_path": [], "value": local("note")},
        "path": [], "receivers": {"kind": "kind", "value": "model_context"}}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    earliest = min((key for key, info in engine.ops.items() if info.get("generated")),
                   key=lambda key: engine.ops[key]["position"]["event_index"])
    assert result["status"] == "potential_violation", result
    assert earliest in result["witness"]


@pytest.mark.parametrize("case,values,expected", [
    ("count_scalar", [7], "not_established"),
    ("count_mixed", [[], 7], "not_established"),
    ("count_valid", [[1, 2]], "satisfied"),
    ("missing_comparison", [{}], "not_established"),
    ("present_missing", [{}], "potential_violation"),
    ("present_null", [{"missing": None}], "satisfied"),
    ("present_false", [{"missing": False}], "satisfied"),
    ("present_zero", [{"missing": 0}], "satisfied"),
    ("present_invalid", [7], "not_established"),
    ("order_mismatch", [7], "not_established"),
    ("order_boolean", [True], "not_established"),
    ("equality_boolean_integer", [True], "potential_violation"),
    ("equality_integer", [1], "satisfied"),
])
def test_real_recursive_expression_types_do_not_hide_known_invalid_operands(case, values, expected):
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints, raw_operation
    from skillflow.propagation.annotation.binding_examples import inp, local, literal as operand_literal, evidence
    reference = {"op": "ref", "value": local("selected")}
    field = {"op": "field", "arg": reference, "path": ["missing"]}
    if case.startswith("count_"):
        expression = {"op": "eq", "left": {"op": "count", "arg": reference}, "right": literal(2)}
    elif case == "missing_comparison":
        expression = {"op": "eq", "left": field, "right": literal(0)}
    elif case.startswith("present_"):
        expression = {"op": "present", "arg": field}
    elif case.startswith("order_"):
        expression = {"op": "gt", "left": reference, "right": literal("0" if case == "order_mismatch" else 0)}
    else:
        expression = {"op": "eq", "left": reference, "right": literal(1)}
    if expected == "not_established":
        expression = {"op": "or", "args": [expression, {"op": "not", "arg": expression}]}
    source = inp() if len(values) == 1 else {"kind": "alternatives", "items": [inp(i) for i in range(len(values))]}
    base = synthetic_fixture([
        {"op": "select_part", "input": source, "path": ["ready"], "output": "selected"},
        {"op": "compute", "inputs": [local("selected")], "dependencies": ["derived"], "output": "formatted",
         "expression": {"expression": expression, "evidences": [evidence()]}},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ], inputs=[operand_literal({"ready": value}) for value in values])
    case_material = with_constraints(base, [{"kind": "only_if", "scope": {"kind": "task"},
        "events": [raw_operation(2)], "condition": raw_operation(1)}])
    engine, _ = solve_fixture(case_material)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == expected, result


def test_unknown_opaque_count_operand_stays_abstract_instead_of_becoming_known_invalid():
    world = World()
    event = world.op("main", "event")
    world.add_data("opaque", {"form": "opaque"})
    world.bind("main", "input", "opaque")
    predicate = {"op": "gt", "left": {"op": "count", "arg": {"op": "ref", "value": {"kind": "input", "index": 0}}},
                 "right": literal(0)}
    condition = world.expression("main", {"op": "or", "args": [predicate, {"op": "not", "arg": predicate}]})
    declaration = {"kind": "only_if", "scope": {"kind": "task"}, "events": [event], "condition": condition}
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "satisfied", result


@pytest.mark.parametrize("reverse_candidates", [False, True])
def test_field_projection_preserves_an_opaque_alternative_to_a_known_true_value(reverse_candidates):
    world = World()
    event = world.op("main", "event")
    world.add_data("known", {"form": "literal", "value": {"ready": True}})
    world.add_data("unknown", {"form": "opaque"})
    world.bind("main", "input", ["unknown", "known"] if reverse_candidates else ["known", "unknown"])
    condition = world.expression("main", {"op": "field", "path": ["ready"],
        "arg": {"op": "ref", "value": {"kind": "input", "index": 0}}})
    declaration = {"kind": "only_if", "scope": {"kind": "task"}, "events": [event], "condition": condition}
    result, = ConstraintEngine(world.engine(declaration)).check().values()
    assert result["status"] == "potential_violation", result


def test_field_projection_honors_the_normalized_producer_type_before_opaque_facts():
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints, raw_operation
    from skillflow.propagation.annotation.binding_examples import inp, local, evidence
    field = {"op": "field", "arg": {"op": "ref", "value": local("ready")}, "path": ["missing"]}
    expression = {"op": "or", "args": [field, {"op": "not", "arg": field}]}
    base = synthetic_fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "ready",
         "expression": {"expression": literal(True), "evidences": [evidence()]}},
        {"op": "compute", "inputs": [local("ready")], "dependencies": ["derived"], "output": "formatted",
         "expression": {"expression": expression, "evidences": [evidence()]}},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ])
    case = with_constraints(base, [{"kind": "only_if", "scope": {"kind": "task"},
        "events": [raw_operation(2)], "condition": raw_operation(1)}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == "not_established", result
    assert any("definitely absent or invalid" in reason for reason in result["reasons"])


@pytest.mark.parametrize("producer_kind,consumer,expected", [
    ("exclude", "count", "not_established"),
    ("update", "count", "not_established"),
    ("build", "count", "not_established"),
    ("exclude", "boolean", "not_established"),
    ("update", "boolean", "not_established"),
    ("build", "boolean", "not_established"),
    ("filter", "boolean", "not_established"),
    ("filter", "count", "satisfied"),
    ("exclude", "order", "not_established"),
    ("build", "order", "not_established"),
    ("exclude", "equality", "potential_violation"),
])
def test_real_transparent_container_types_remain_known_without_inventing_values(producer_kind, consumer, expected):
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints, raw_operation
    from skillflow.propagation.annotation.binding_examples import inp, local, literal as operand_literal, evidence
    producers = {
        "exclude": {"op": "exclude_parts", "input": inp(), "paths": [["secret"]], "output": "ready"},
        "update": {"op": "update_fields", "input": inp(),
                   "updates": [{"path": ["secret"], "value": {"kind": "literal", "value": "replacement"}}], "output": "ready"},
        "build": {"op": "build", "container": "object", "parts": [
            {"path": ["label"], "value": {"kind": "literal", "value": "ok"}}], "output": "ready"},
        "filter": {"op": "filter_items", "input": inp(), "predicate": "enabled is true", "output": "ready"},
    }
    reference = {"op": "ref", "value": local("ready")}
    if consumer == "count":
        predicate = {"op": "gt", "left": {"op": "count", "arg": reference}, "right": literal(0)}
    elif consumer == "order":
        predicate = {"op": "gt", "left": reference, "right": literal(0)}
    elif consumer == "equality":
        predicate = {"op": "eq", "left": reference, "right": literal({"label": "ok"})}
    else:
        predicate = reference
    expression = predicate if consumer == "equality" else {"op": "or", "args": [predicate, {"op": "not", "arg": predicate}]}
    payload = [{"enabled": True}] if producer_kind == "filter" else {"label": "ok", "secret": "x"}
    base = synthetic_fixture([
        producers[producer_kind],
        {"op": "compute", "inputs": [local("ready")], "dependencies": ["derived"], "output": "formatted",
         "expression": {"expression": expression, "evidences": [evidence()]}},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ], inputs=[operand_literal(payload)])
    case = with_constraints(base, [{"kind": "only_if", "scope": {"kind": "task"},
        "events": [raw_operation(2)], "condition": raw_operation(1)}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == expected, result


@pytest.mark.parametrize("left,right,operation,expected", [
    ({"nested": [True]}, {"nested": [1]}, "eq", "potential_violation"),
    ([{"nested": False}], [{"nested": 0}], "eq", "potential_violation"),
    ({"nested": [True]}, {"nested": [1]}, "ne", "satisfied"),
    ([{"nested": True}], [{"nested": True}], "eq", "satisfied"),
])
def test_real_compound_equality_preserves_nested_json_types(left, right, operation, expected):
    from tests.doe.test_sink_payload_seeds import synthetic_fixture, solve_fixture
    from tests.doe.test_constraint_preservation import with_constraints, raw_operation
    from skillflow.propagation.annotation.binding_examples import inp, local, literal as operand_literal, evidence
    expression = {"op": operation, "left": {"op": "ref", "value": inp()}, "right": literal(right)}
    base = synthetic_fixture([
        {"op": "compute", "inputs": [inp()], "dependencies": ["derived"], "output": "formatted",
         "expression": {"expression": expression, "evidences": [evidence()]}},
        {"op": "deliver", "target": "label_receiver", "inputs": [local("formatted")]},
    ], inputs=[operand_literal(left)])
    case = with_constraints(base, [{"kind": "only_if", "scope": {"kind": "task"},
        "events": [raw_operation(1)], "condition": raw_operation(0)}])
    engine, _ = solve_fixture(case)
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == expected, result


@pytest.mark.parametrize("action", ["select_part", "exclude_parts"])
def test_real_compiled_demand_index_information_check(action):
    from tests.doe.test_demand_engine import fixture, inp, solve
    operation = {"op": action, "input": inp(), "output": "value"}
    operation["path" if action == "select_part" else "paths"] = ["body"] if action == "select_part" else [["body"]]
    values = fixture([operation], mode="model")
    engine, _ = solve(values)
    # The original compiled observation occurs before exclusion. This validates
    # the baseline boundary and ensures a later version cannot erase it.
    declaration = {"kind": "forbid_information", "scope": {"kind": "task"},
        "source": {"instruction_id": "ir_filter", "scope_path": [], "value": inp()},
        "path": ["body"], "events": None, "receivers": {"kind": "kind", "value": "model_context"}}
    engine.raw["realizations"][0]["constraints"] = [deepcopy(declaration)]
    engine.compiled["realizations"][0]["constraints"] = [deepcopy(declaration)]
    before = deepcopy((engine.index.data, engine.facts.records, engine.nodes, engine.derivations))
    result, = ConstraintEngine(engine).check().values()
    assert result["status"] == "potential_violation", result
    assert before == (engine.index.data, engine.facts.records, engine.nodes, engine.derivations)
