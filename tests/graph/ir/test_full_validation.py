"""Integrity checks the current object, including changes after construction."""

from copy import deepcopy
import json

import pytest
from pydantic import BaseModel, ValidationError
from pydantic_core import SchemaValidator, core_schema

from skillflow.graph import BasicBlock
from skillflow.graph import CFGEdge
from skillflow.graph import ControlFlowGraph
from skillflow.graph import IRInstruction
from skillflow.graph import Operand
from skillflow.graph.ir.operand import OperandType
from skillflow.graph.ir.validation import CFGIntegrityError
from skillflow.graph.ir.validation import _cfg_field_schema_validator
from skillflow.graph.ir.validation import _schema_without_structure


def make_graph():
    return ControlFlowGraph(
        entry_block_id="A",
        declared_context_keys=["request"],
        blocks={
            "A": BasicBlock(
                block_id="A",
                block_name="Read request",
                data_source_kind="context",
                instructions=[
                    IRInstruction(
                        id="ir_read",
                        opcode="acquire",
                        inputs=[Operand(type="context_key", identifier="request")],
                        outputs=[Operand(type="result", identifier="seed")],
                    ),
                    IRInstruction(
                        id="ir_jump",
                        opcode="dispatch",
                        inputs=[Operand(type="result", identifier="seed")],
                    ),
                ],
            ),
            "B": BasicBlock(
                block_id="B",
                block_name="Compute answer",
                instructions=[
                    IRInstruction(
                        id="ir_work",
                        opcode="arbitrary_business_operation",
                        inputs=[
                            Operand(type="result", identifier="seed"),
                            Operand(type="literal", literal_value={"flags": [True, None]}),
                            Operand(type="external_resource", identifier="service"),
                        ],
                        outputs=[Operand(type="result", identifier="answer")],
                    ),
                    IRInstruction(
                        id="ir_done",
                        opcode="return",
                        inputs=[Operand(type="result", identifier="answer")],
                    ),
                ],
            ),
        },
        edges=[CFGEdge(source_block_id="A", target_block_id="B", condition_text="ready")],
    )


def state(value):
    """Include field provenance and actual fields, without using serialization."""
    if isinstance(value, BaseModel):
        return type(value), frozenset(value.model_fields_set), state(value.__dict__)
    if isinstance(value, dict):
        return type(value), [(key, state(item)) for key, item in value.items()]
    if isinstance(value, (list, tuple)):
        return type(value), [state(item) for item in value]
    return type(value), value


def replace(graph, path, value):
    owner = graph
    for key in path[:-1]:
        owner = getattr(owner, key) if isinstance(owner, BaseModel) else owner[key]
    if isinstance(owner, BaseModel):
        setattr(owner, path[-1], value)
    else:
        owner[path[-1]] = value


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("entry_block_id",), 4),
        (("constraints",), [None]),
        (("declared_context_keys",), ["request", "request"]),
        (("declared_context_keys",), ["request", 1]),
        (("blocks", "A"), None),
        (("blocks", "B", "block_id"), []),
        (("blocks", "B", "block_name"), ""),
        (("blocks", "B", "constraints"), [False]),
        (("blocks", "B", "data_source_kind"), "unknown"),
        (("blocks", "B", "instructions"), [None]),
        (("blocks", "B", "instructions", 0, "id"), "invalid_id"),
        (("blocks", "B", "instructions", 0, "opcode"), ""),
        (("blocks", "B", "instructions", 0, "constraints"), [1]),
        (("blocks", "B", "instructions", 0, "metadata"), {2: "bad key"}),
        (("blocks", "B", "instructions", 0, "draft_instruction_id"), 8),
        (("blocks", "B", "instructions", 0, "inputs", 0, "type"), "result"),
        (("blocks", "B", "instructions", 0, "inputs", 0, "identifier"), 2),
        (("blocks", "B", "instructions", 0, "inputs", 0, "semantic_name"), []),
        (("blocks", "B", "instructions", 0, "inputs", 1, "semantic_name"), "bad"),
        (("blocks", "B", "instructions", 0, "outputs", 0, "identifier"), None),
        (("edges", 0, "source_block_id"), None),
        (("edges", 0, "target_block_id"), {}),
        (("edges", 0, "condition_text"), True),
    ],
)
def test_deep_schema_mutations_raise_located_integrity_errors_without_changes(path, value):
    graph = make_graph()
    replace(graph, path, value)
    before = deepcopy(state(graph))

    with pytest.raises(CFGIntegrityError) as caught:
        graph.validate_integrity()

    assert {issue.code for issue in caught.value.issues} == {"CFG_SCHEMA_INVALID"}
    assert "cfg" in str(caught.value)
    assert repr(path[0]) in str(caught.value)
    assert state(graph) == before


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("entry_block_id",), " A "),
        (("declared_context_keys",), [" request "]),
        (("blocks", "B", "block_id"), " B "),
        (("blocks", "B", "block_name"), " Compute answer "),
        (("blocks", "B", "instructions", 0, "opcode"), " compute "),
        (("blocks", "B", "instructions", 0, "draft_instruction_id"), " "),
        (("blocks", "B", "instructions", 0, "inputs", 0, "identifier"), " seed "),
        (("blocks", "B", "instructions", 0, "inputs", 0, "semantic_name"), " "),
        (("edges", 0, "source_block_id"), " A "),
        (("edges", 0, "target_block_id"), " B "),
        (("edges", 0, "condition_text"), " "),
    ],
)
def test_normalizable_mutations_are_rejected_without_normalizing_in_place(path, value):
    graph = make_graph()
    replace(graph, path, value)
    before = deepcopy(state(graph))
    with pytest.raises(CFGIntegrityError, match="requires normalization"):
        graph.validate_integrity()
    assert state(graph) == before


def test_valid_graph_defaults_and_explicit_literal_null_are_unchanged():
    graph = make_graph()
    literal = graph.blocks["B"].instructions[0].inputs[1]
    literal.literal_value = None
    result = graph.blocks["B"].instructions[0].inputs[0]
    assert result.literal_value is None
    assert "literal_value" not in result.model_fields_set
    before = deepcopy(state(graph))
    assert graph.validate_integrity() is True
    assert graph.validate_integrity() is True
    assert state(graph) == before


@pytest.mark.parametrize("kind", ["result", "context_key", "external_resource"])
@pytest.mark.parametrize("value", [None, 0, {"payload": [1]}])
def test_explicit_non_literal_value_is_never_removed_from_validation_input(kind, value):
    graph = make_graph()
    operand = (
        graph.blocks["A"].instructions[0].inputs[0]
        if kind == "context_key"
        else graph.blocks["B"].instructions[0].inputs[0 if kind == "result" else 2]
    )
    operand.literal_value = value
    before = deepcopy(state(graph))
    with pytest.raises(CFGIntegrityError, match="must not define 'literal_value'"):
        graph.validate_integrity()
    assert state(graph) == before


def test_in_place_changes_do_not_depend_on_fields_set():
    graph = make_graph()
    result = graph.blocks["B"].instructions[0].inputs[0]
    assert "literal_value" not in result.model_fields_set
    result.__dict__["literal_value"] = {"hidden": True}
    assert "literal_value" not in result.model_fields_set
    with pytest.raises(CFGIntegrityError, match="literal_value"):
        graph.validate_integrity()

    graph = make_graph()
    assert "constraints" not in graph.model_fields_set
    graph.constraints.append(1)
    with pytest.raises(CFGIntegrityError, match="constraints.*0"):
        graph.validate_integrity()

    graph = make_graph()
    graph.declared_context_keys.append("request")
    with pytest.raises(CFGIntegrityError, match="duplicate declared context key"):
        graph.validate_integrity()


@pytest.mark.parametrize("depth", ["graph", "block", "instruction", "operand", "edge"])
def test_unknown_actual_fields_are_not_hidden_by_model_serialization(depth):
    graph = make_graph()
    owner = {
        "graph": graph,
        "block": graph.blocks["B"],
        "instruction": graph.blocks["B"].instructions[0],
        "operand": graph.blocks["B"].instructions[0].inputs[0],
        "edge": graph.edges[0],
    }[depth]
    owner.__dict__["unexpected_field"] = 3
    with pytest.raises(CFGIntegrityError, match="unexpected_field.*Extra inputs"):
        graph.validate_integrity()
    assert owner.__dict__["unexpected_field"] == 3


def test_missing_fields_and_raw_nested_dicts_cannot_be_silently_reconstructed():
    graph = make_graph()
    del graph.blocks["B"].instructions[0].inputs[0].__dict__["literal_value"]
    with pytest.raises(CFGIntegrityError, match="literal_value.*reconstruction"):
        graph.validate_integrity()

    graph = make_graph()
    graph.edges[0] = {"source_block_id": "A", "target_block_id": "B"}
    with pytest.raises(CFGIntegrityError, match="edges.*reconstruction"):
        graph.validate_integrity()

    graph = make_graph()
    del graph.__dict__["entry_block_id"]
    with pytest.raises(CFGIntegrityError, match="entry_block_id.*Field required"):
        graph.validate_integrity()


def test_validation_does_not_call_export_or_model_dump(monkeypatch):
    def unexpected_export(*args, **kwargs):
        pytest.fail("validation must not sanitize input with a serializer")

    graph = make_graph()
    monkeypatch.setattr(ControlFlowGraph, "to_json", unexpected_export)
    monkeypatch.setattr(ControlFlowGraph, "model_dump", unexpected_export)
    assert graph.validate_integrity()
    graph.blocks["B"].instructions[0].inputs[1].semantic_name = "bad"
    with pytest.raises(CFGIntegrityError, match="literal operand.*semantic_name"):
        graph.validate_integrity()


def test_any_payloads_remain_opaque_and_are_not_mutated_or_reconstructed():
    graph = make_graph()
    nested_model = Operand(type="literal", literal_value=None)
    recursive_list = []
    recursive_list.append(recursive_list)
    work = graph.blocks["B"].instructions[0]
    work.inputs[1].literal_value = nested_model
    work.metadata.update({"model": nested_model, "cycle": recursive_list})
    assert graph.validate_integrity()
    assert work.inputs[1].literal_value is nested_model
    assert work.metadata["cycle"] is recursive_list
    assert recursive_list[0] is recursive_list


def test_cyclic_model_containers_raise_integrity_error_with_a_location():
    graph = make_graph()
    graph.blocks["cycle"] = graph
    with pytest.raises(CFGIntegrityError, match=r"cfg.blocks\['cycle'\].*cyclic"):
        graph.validate_integrity()


def test_constructor_and_json_loading_keep_their_existing_normalization():
    payload = json.loads(make_graph().to_json())
    payload["entry_block_id"] = " A "
    payload["declared_context_keys"] = [" request "]
    payload["blocks"]["B"]["block_name"] = " Compute answer "
    payload["edges"][0]["condition_text"] = " "
    graph = ControlFlowGraph.model_validate(payload)
    assert graph.entry_block_id == "A"
    assert graph.edges[0].condition_text is None
    assert graph.validate_integrity()
    assert ControlFlowGraph.model_validate_json(graph.to_json()).validate_integrity()


def test_original_structure_issue_codes_remain_available_after_mutation():
    graph = make_graph()
    graph.blocks["B"].instructions[-1].opcode = "dispatch"
    graph.blocks["B"].instructions[0].outputs.append(
        Operand(type=OperandType.LITERAL, literal_value=1)
    )
    graph.blocks["B"].instructions[0].id = "ir_read"
    with pytest.raises(CFGIntegrityError) as caught:
        graph.validate_integrity()
    assert {issue.code for issue in caught.value.issues} >= {
        "DISPATCH_HAS_NO_TARGET", "BASIC_BLOCK_INVALID", "DUPLICATE_INSTRUCTION_ID"
    }


def test_field_schema_defers_only_graph_rules_and_does_not_change_constructors():
    payload = json.loads(make_graph().to_json())
    payload["blocks"]["B"]["instructions"][-1]["opcode"] = "dispatch"
    graph = _cfg_field_schema_validator().validate_python(payload)
    with pytest.raises(CFGIntegrityError, match="DISPATCH_HAS_NO_TARGET"):
        graph.validate_integrity()
    with pytest.raises(ValidationError, match="DISPATCH_HAS_NO_TARGET"):
        ControlFlowGraph.model_validate(payload)

    payload["blocks"]["B"]["instructions"][0]["inputs"][1]["semantic_name"] = "bad"
    with pytest.raises(ValidationError, match="literal operand.*semantic_name"):
        _cfg_field_schema_validator().validate_python(payload)


def test_schema_filter_keeps_an_unknown_after_validator():
    def additional_rule(value):
        raise ValueError("additional validator must still run")

    original = core_schema.no_info_after_validator_function(
        additional_rule, ControlFlowGraph.__pydantic_core_schema__
    )
    filtered = _schema_without_structure(original)
    assert original["function"]["function"] is additional_rule
    validator = SchemaValidator(filtered)
    with pytest.raises(ValidationError, match="additional validator must still run"):
        validator.validate_python(json.loads(make_graph().to_json()))
