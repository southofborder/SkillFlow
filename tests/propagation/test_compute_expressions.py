"""One accepted compute expression serves paired forward data and backward demand."""
from copy import deepcopy

import pytest

from skillflow.common.validation import StructuralValidationError
from skillflow.propagation.annotation.services import to_payload, validate_compiled_response
from skillflow.propagation.data import DataPart, DataRegistry, KnownPartsContent, LiteralContent, Origin, SelectionContent
from skillflow.propagation.expressions import evaluate_compute
from skillflow.propagation.interpreter import TransferInterpreter
from skillflow.propagation.loop_domain import LoopFactRegistry
from skillflow.propagation.models import FlowLocation, FlowState
from skillflow.propagation.solver import propagate
from tests.doe.test_demand_engine import evidence, fixture, inp, input_demands, literal, local, solve
from tests.doe.test_sensitivity_engine import declarations, review, rows
from tests.propagation.test_projected_states import ir, spec


def reference(value):
    return {"op": "ref", "value": value}


def field(value, *path):
    return {"op": "field", "arg": value, "path": list(path)}


def compute(inputs, expression, *, output="result"):
    return {"op": "compute", "inputs": inputs, "dependencies": ["derived"] * len(inputs),
        "output": output, "expression": {"expression": expression, "evidences": [evidence()]}}


def candidate(values):
    compiled = values[2]["compiled_annotation"]
    return {"goals": compiled["demands"], "expressions": compiled["expressions"]}


def output(engine, *, name="result"):
    operation, = [op for op in engine.ops.values() if op["spec"].get("output") == name]
    identity, = operation["record"]["outputs"][0]
    return engine.index.data[identity]


@pytest.mark.parametrize("damage, code", [
    ("event_outside", "expression_position"),
    ("body_outside", "expression_position"),
    ("step_outside", "expression_position"),
    ("observation", "expression_position"),
    ("duplicate_position", "expression_position"),
    ("duplicate_target", "expression_position"),
    ("other_compute", "expression_input"),
    ("unused_reference", "expression_input"),
    ("one_unused_alternative", "expression_input"),
])
def test_compiled_validation_and_solver_reject_the_same_expression_binding(damage, code):
    values = fixture([compute([inp()], reference(inp()), output="first"),
                      compute([local("first")], reference(local("first")))])
    material = values[2]["material"]
    compiled = deepcopy(values[2]["compiled_annotation"])
    first, second = compiled["expressions"]
    if damage.endswith("_outside"):
        axis = {"event": "event_index", "body": "body_event_index", "step": "op_index"}[damage.split("_")[0]]
        first["operation_position"][axis] = 999
    elif damage == "observation":
        first["operation_position"]["event_index"] = 0
    elif damage == "duplicate_position":
        second["operation_position"] = deepcopy(first["operation_position"])
    elif damage == "duplicate_target":
        second["target"] = deepcopy(first["target"])
    elif damage == "other_compute":
        first["operation_position"] = deepcopy(second["operation_position"])
        compiled["expressions"].pop()
    elif damage == "unused_reference":
        second["expression"] = reference(inp())  # available to the IR, not this operation
    else:
        second["expression"] = reference({"kind": "alternatives", "items": [local("first"), inp()]})
    with pytest.raises(StructuralValidationError) as candidate_error:
        validate_compiled_response(compiled, material)
    with pytest.raises(StructuralValidationError) as solver_error:
        propagate(material["cfg"], to_payload(compiled))
    diagnostics = candidate_error.value.diagnostics
    assert diagnostics == solver_error.value.diagnostics
    assert diagnostics[0]["code"] == code


def test_existing_supplement_without_position_remains_readable():
    values = fixture([compute([inp(), inp()], reference(inp()))])
    material = values[2]["material"]
    compiled = deepcopy(values[2]["compiled_annotation"])
    del compiled["expressions"][0]["operation_position"]
    checked = validate_compiled_response(compiled, material)
    assert checked["expressions"] == compiled["expressions"]
    assert propagate(material["cfg"], to_payload(checked)).status == "complete"


def test_compiled_projection_keeps_exact_content_and_only_selected_lexical_input():
    values = fixture([compute([inp(), literal("unrelated")], field(reference(inp()), "profile", "name"))])
    annotated, = candidate(values)["expressions"]
    engine, result = solve(values, candidate(values))
    position = annotated["operation_position"]
    ir_spec = values[2]["compiled_annotation"]["ir_semantics"]["ir_filter"]
    assert position["event_index"] > 0  # compiler generated an earlier model observation
    assert ir_spec["events"][position["event_index"]]["atomic_ops"][position["op_index"]]["op"] == "compute"
    data = output(engine)
    assert data["content"] == {"form": "selection", "base": data["origin"]["inputs"][0], "path": ["profile", "name"]}
    assert {tuple(item["path"]) for item in input_demands(engine, result, "compute")} == {("profile", "name")}
    assert not input_demands(engine, result, "compute", slot=1)


def test_direct_projection_exposes_selected_field_without_sibling_influence():
    values = fixture([compute([inp()], field(reference(inp()), "profile", "name"))],
                     mode="local", returned=[local("result")])
    requested = candidate(values)
    selected = rows(review(values, declarations(["profile", "name"]), requested))
    assert selected and all(row["path"] == [] and row["relation"] == "direct" for row in selected)
    assert not rows(review(values, declarations(["profile", "token"]), requested))


def test_explicit_expression_literal_does_not_retain_equal_recorded_operand():
    values = fixture([compute([inp(), literal("same text")], reference(literal("same text")))])
    engine, result = solve(values, candidate(values))
    assert output(engine)["content"] == {"form": "literal", "value": "same text"}
    assert not input_demands(engine, result, "compute", slot=0)
    assert not input_demands(engine, result, "compute", slot=1)


def test_scalar_count_preserves_influence_on_size_without_copying_item_value():
    values = fixture([{"op": "build", "parts": [{"path": [0], "value": inp()}],
                        "container": "list", "output": "items"},
                      compute([local("items"), inp()], {"op": "count", "arg": reference(local("items"))})],
                     mode="local", returned=[local("result")])
    requested = candidate(values)
    engine, result = solve(values, requested)
    assert output(engine)["content"] == {"form": "literal", "value": 1}
    assert {row["property"] for row in input_demands(engine, result, "compute")} == {"cardinality"}
    assert not input_demands(engine, result, "compute", slot=1)
    sensitive_size = declarations((), value=local("items"), property="cardinality")
    sink = rows(review(values, sensitive_size, requested))
    assert sink and all(row["relation"] == "derived" and row["property"] == "cardinality" for row in sink)
    assert not rows(review(values, declarations(()), requested))


@pytest.mark.parametrize("member, expected", [("null", True), ("false", True), ("missing", False)])
def test_presence_distinguishes_closed_absence_from_null_and_false(member, expected):
    registry = DataRegistry("presence")
    item = registry.register_source("record", acquired_from="fixture", content=LiteralContent(value={"null": None, "false": False}))
    expression = {"op": "present", "arg": field(reference(inp()), member)}
    content = evaluate_compute(expression, registry, [inp()], [item.id])
    assert content == LiteralContent(value=expected)


def test_presence_of_opaque_field_uses_only_authoritative_closed_structure():
    registry = DataRegistry("known-membership")
    unknown = registry.register_source("unknown", acquired_from="fixture")
    part = DataPart(path=["opaque_member"], data=unknown.id)
    closed = registry.create_result("object", origin=Origin(at="fixture"),
        content=KnownPartsContent(parts=[part], parts_complete=True))
    expression = {"op": "present", "arg": field(reference(inp()), "opaque_member")}
    assert evaluate_compute(expression, registry, [inp()], [closed.id]) == LiteralContent(value=True)
    assert evaluate_compute(expression, registry, [inp()], [unknown.id]).form == "opaque"


def test_symbolic_projection_reuses_the_actual_paired_member_versions():
    registry = LoopFactRegistry(DataRegistry("paired-compute-expression"), {})

    def versions(name):
        versions_by_member = {}
        for member in ("first", "second"):
            item = registry.register_source(f"{name}-{member}", acquired_from="fixture")
            pair = registry.family("members", [name], [item.id], SelectionContent(base=item.id, path=[]),
                Origin(at="fixture", inputs=[item.id]), bindings={"member:rows": member})
            versions_by_member[member] = pair.id
        return versions_by_member

    left, right = versions("left"), versions("right")
    instruction = ir("compute", ("left", "right"), ("done",))
    op = {"op": "compute", "inputs": [inp(), inp(1)], "dependencies": ["derived", "possible"], "output": "out"}
    semantics = spec([op], [local("out")])
    annotation = {"locations": {}, "ir_semantics": {"compute": semantics.model_dump(mode="json")},
        "expressions": [{"target": {"instruction_id": "compute"}, "operation_position": {"event_index": 0, "op_index": 0},
                         "expression": field(reference(inp()), "payload")}]}
    interpreter = TransferInterpreter({"blocks": {"entry": {"instructions": [instruction]}}}, annotation, registry)
    state = FlowState.from_mapping({FlowLocation(kind="result", name="left"): frozenset(left.values()),
                                    FlowLocation(kind="result", name="right"): frozenset(right.values())})
    operation = interpreter.evaluate(instruction, semantics, state).events[0].atomic_ops[0]
    assert len(operation.alternatives) == 2
    for pairing in operation.alternatives:
        member = pairing.bindings["member:rows"]
        assert pairing.inputs == [frozenset({left[member]}), frozenset({right[member]})]
        paired_output, = pairing.outputs[0]
        value, = registry.get(paired_output).content.variants
        assert value.content == SelectionContent(base=left[member], path=["payload"])
