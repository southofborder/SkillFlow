import pytest
from pydantic import ValidationError

from skillflow.graph import BasicBlock
from skillflow.graph import IRInstruction
from skillflow.graph import Operand
from skillflow.graph import OperandType
from skillflow.graph.extraction.candidate import CandidateBlock


def make_result(identifier: str, semantic_name: str | None = None) -> Operand:
    return Operand(
        type=OperandType.RESULT, identifier=identifier, semantic_name=semantic_name
    )


def context(identifier: str) -> Operand:
    return Operand(type=OperandType.CONTEXT_KEY, identifier=identifier)


def resource(identifier: str) -> Operand:
    return Operand(type=OperandType.EXTERNAL_RESOURCE, identifier=identifier)


def definition(instruction_id: str, output_name: str) -> IRInstruction:
    return IRInstruction(
        id=instruction_id,
        opcode="assign",
        outputs=[make_result(output_name)],
    )


def test_valid_ordered_dependencies_and_json() -> None:
    block = BasicBlock(
        block_id="b1",
        block_name="测试块",
        instructions=[
            definition("ir_001", "first_v1"),
            IRInstruction(
                id="ir_002",
                opcode="call_llm",
                inputs=[make_result("first_v1")],
                outputs=[make_result("second_v1")],
            ),
            IRInstruction(
                id="ir_003", opcode="return", inputs=[make_result("second_v1")]
            ),
        ],
    )

    assert block.validate_dataflow() is True
    assert '"block_id": "b1"' in block.to_json()
    assert block.produced_result_ids() == ["first_v1", "second_v1"]
    assert block.cross_block_result_ids() == []


def test_values_defined_elsewhere_are_reported_as_external_uses() -> None:
    block = BasicBlock(
        block_id="b1",
        block_name="测试块",
        instructions=[
            IRInstruction(
                id="ir_001",
                opcode="call_llm",
                inputs=[make_result("upstream_v1"), make_result("upstream_v1")],
                outputs=[make_result("answer_v1")],
            ),
            IRInstruction(
                id="ir_002", opcode="return", inputs=[make_result("answer_v1")]
            ),
        ],
    )

    # Nothing in this block defines upstream_v1, and that is not a block-scope
    # error: whether it arrives is a question about paths through the graph.
    assert block.validate_dataflow() is True
    assert block.cross_block_result_ids() == ["upstream_v1"]
    assert block.read_context_keys() == []


def test_json_omits_non_literal_null_payloads_but_keeps_literal_none() -> None:
    block = BasicBlock(
        block_id="b1",
        block_name="测试块",
        instructions=[
            IRInstruction(
                id="ir_001",
                opcode="assign",
                inputs=[Operand(type=OperandType.LITERAL, literal_value=None)],
                outputs=[make_result("result_v1", semantic_name="结果")],
            ),
            IRInstruction(
                id="ir_002", opcode="return", inputs=[make_result("result_v1")]
            ),
        ],
    )

    rendered = block.to_json()
    assert '"literal_value": null' in rendered
    assert '"semantic_name": "结果"' in rendered


def test_value_read_before_its_own_definition_is_rejected() -> None:
    with pytest.raises((ValidationError, ValueError), match="is read before"):
        BasicBlock(
            block_id="b1",
            block_name="测试块",
            instructions=[
                IRInstruction(
                    id="ir_001",
                    opcode="call_llm",
                    inputs=[make_result("later_v1")],
                ),
                definition("ir_002", "later_v1"),
                IRInstruction(
                    id="ir_003", opcode="return", inputs=[make_result("later_v1")]
                ),
            ],
        )


def test_duplicate_ssa_output_is_rejected() -> None:
    with pytest.raises((ValidationError, ValueError), match="already defined"):
        BasicBlock(
            block_id="b1",
            block_name="测试块",
            instructions=[
                definition("ir_001", "same_v1"),
                definition("ir_002", "same_v1"),
                IRInstruction(
                    id="ir_003", opcode="return", inputs=[make_result("same_v1")]
                ),
            ],
        )


def test_duplicate_outputs_within_instruction_are_rejected() -> None:
    with pytest.raises(
        (ValidationError, ValueError), match="duplicates result identifier"
    ):
        IRInstruction(
            id="ir_001",
            opcode="assign",
            outputs=[make_result("same_v1"), make_result("same_v1")],
        )


def test_outputs_must_be_value_references() -> None:
    with pytest.raises((ValidationError, ValueError), match="must have type RESULT"):
        IRInstruction(
            id="ir_001",
            opcode="assign",
            outputs=[resource("handle")],
        )


def test_operand_source_rules_and_extra_fields() -> None:
    with pytest.raises((ValidationError, ValueError), match="requires a non-empty"):
        Operand(type=OperandType.CONTEXT_KEY)
    with pytest.raises(
        (ValidationError, ValueError), match="must not define 'literal_value'"
    ):
        Operand(type=OperandType.RESULT, identifier="x", literal_value=1)
    with pytest.raises(
        (ValidationError, ValueError), match="must not define 'semantic_name'"
    ):
        Operand(type=OperandType.LITERAL, literal_value=1, semantic_name="x")
    with pytest.raises(ValidationError):
        Operand(type=OperandType.LITERAL, literal_value=1, typo=True)


def test_operand_whitespace_normalization_covers_both_names() -> None:
    operand = Operand(type=OperandType.RESULT, identifier=" x ", semantic_name=" 城市 ")
    assert (operand.identifier, operand.semantic_name) == ("x", "城市")
    assert (
        Operand(
            type=OperandType.RESULT, identifier="x", semantic_name="   "
        ).semantic_name
        is None
    )


def test_duplicate_instruction_ids_and_return_without_output() -> None:
    with pytest.raises((ValidationError, ValueError), match="duplicate instruction id"):
        BasicBlock(
            block_id="b1",
            block_name="测试块",
            instructions=[
                IRInstruction(id="ir_001", opcode="return"),
                IRInstruction(id="ir_001", opcode="return"),
            ],
        )

    block = BasicBlock(
        block_id="b2",
        block_name="测试块",
        instructions=[IRInstruction(id="ir_001", opcode="return")],
    )
    assert block.validate_dataflow() is True


def test_terminator_must_be_the_final_instruction() -> None:
    with pytest.raises(
        (ValidationError, ValueError), match="must be the final instruction"
    ):
        BasicBlock(
            block_id="b1",
            block_name="测试块",
            instructions=[
                IRInstruction(id="ir_001", opcode="return"),
                IRInstruction(id="ir_002", opcode="return"),
            ],
        )


def make_context_source(**overrides) -> BasicBlock:
    fields = {
        "block_id": "source",
        "block_name": "读入用户请求和配置",
        "data_source_kind": "context",
        "instructions": [
            IRInstruction(
                id="ir_001",
                opcode="read_context",
                inputs=[context("user_input"), context("locale")],
                outputs=[
                    make_result("request_v1", semantic_name="user_input"),
                    make_result("locale_v1", semantic_name="locale"),
                ],
            ),
            IRInstruction(id="ir_002", opcode="dispatch"),
        ],
    }
    fields.update(overrides)
    return BasicBlock(**fields)


def test_multi_value_context_source_binds_raw_keys_and_roundtrips() -> None:
    block = make_context_source()

    # The raw keys stay visible as the boundary of the caller's namespace; the
    # values they were bound to are what every later block references.
    assert block.read_context_keys() == ["user_input", "locale"]
    assert block.produced_result_ids() == ["request_v1", "locale_v1"]
    assert block.validate_dataflow()
    restored = BasicBlock.model_validate_json(block.to_json())
    assert restored == block


def test_raw_context_keys_are_deduplicated_without_merging_distinct_entries() -> None:
    block = make_context_source(
        instructions=[
            IRInstruction(
                id="ir_001",
                opcode="read_context",
                inputs=[
                    context(" user_input "),
                    context("user_input"),
                    context("locale"),
                ],
                outputs=[make_result("request_v1")],
            ),
            IRInstruction(id="ir_002", opcode="dispatch"),
        ]
    )
    assert block.read_context_keys() == ["user_input", "locale"]


@pytest.mark.parametrize(
    "acquisition_input", [resource("weather_api"), make_result("endpoint_v1")]
)
def test_external_source_accepts_resource_or_previously_produced_value(
    acquisition_input,
) -> None:
    block = BasicBlock(
        block_id="external",
        block_name="查询天气",
        data_source_kind="external",
        instructions=[
            IRInstruction(
                id="ir_001",
                opcode="fetch_weather",
                inputs=[acquisition_input, make_result("city_v1")],
                outputs=[make_result("response_v1")],
            ),
            IRInstruction(id="ir_002", opcode="dispatch"),
        ],
    )

    assert block.produced_result_ids() == ["response_v1"]
    expected_uses = ["city_v1"]
    if acquisition_input.type is OperandType.RESULT:
        expected_uses = ["endpoint_v1", "city_v1"]
    assert block.cross_block_result_ids() == expected_uses


@pytest.mark.parametrize("data_source_kind", ["context", "external"])
@pytest.mark.parametrize("extra", [False, True])
def test_source_requires_one_acquisition_followed_by_terminator(
    data_source_kind, extra
) -> None:
    sequence = [IRInstruction(id="ir_001", opcode="return")]
    if extra:
        sequence = [
            IRInstruction(
                id="ir_002",
                opcode="read_context" if data_source_kind == "context" else "read_file",
                inputs=[
                    (
                        context("input")
                        if data_source_kind == "context"
                        else resource("disk")
                    )
                ],
                outputs=[make_result("raw_v1")],
            ),
            definition("ir_003", "transformed_v1"),
            *sequence,
        ]
    with pytest.raises(ValidationError, match="exactly one acquisition"):
        BasicBlock(
            block_id="source",
            block_name="source",
            data_source_kind=data_source_kind,
            instructions=sequence,
        )


@pytest.mark.parametrize("data_source_kind", ["context", "external"])
def test_source_acquisition_must_have_real_outputs(data_source_kind) -> None:
    with pytest.raises(
        ValidationError, match="must produce at least one result output"
    ):
        BasicBlock(
            block_id="source",
            block_name="source",
            data_source_kind=data_source_kind,
            instructions=[
                IRInstruction(
                    id="ir_001",
                    opcode=(
                        "read_context" if data_source_kind == "context" else "read_file"
                    ),
                    inputs=[
                        (
                            context("input")
                            if data_source_kind == "context"
                            else resource("disk")
                        )
                    ],
                ),
                IRInstruction(id="ir_002", opcode="return"),
            ],
        )


@pytest.mark.parametrize(
    "inputs",
    [
        [],
        [make_result("previous_v1")],
        [Operand(type=OperandType.LITERAL, literal_value="user")],
    ],
)
def test_context_source_requires_nonempty_raw_context_inputs(inputs) -> None:
    with pytest.raises(ValidationError, match="context_key-only raw inputs"):
        make_context_source(
            instructions=[
                IRInstruction(
                    id="ir_001",
                    opcode="read_context",
                    inputs=inputs,
                    outputs=[make_result("raw_v1")],
                ),
                IRInstruction(id="ir_002", opcode="return"),
            ]
        )


def test_external_source_requires_resource_or_value_input() -> None:
    with pytest.raises(
        ValidationError, match="external_resource or previously produced result"
    ):
        BasicBlock(
            block_id="external",
            block_name="external",
            data_source_kind="external",
            instructions=[
                IRInstruction(
                    id="ir_001",
                    opcode="read_file",
                    inputs=[Operand(type=OperandType.LITERAL, literal_value="a.txt")],
                    outputs=[make_result("raw_v1")],
                ),
                IRInstruction(id="ir_002", opcode="return"),
            ],
        )


@pytest.mark.parametrize("data_source_kind", [None, "external"])
def test_context_key_requires_context_source_structure(data_source_kind) -> None:
    with pytest.raises(
        ValidationError, match="only allowed in a context source acquisition"
    ):
        make_context_source(data_source_kind=data_source_kind)


@pytest.mark.parametrize(
    "opcode", ["read_context", "read_request", "http_get", "read_db"]
)
def test_context_source_category_is_independent_of_opcode(opcode) -> None:
    source = make_context_source()
    source.instructions[0].opcode = opcode
    assert source.validate_dataflow() is True
    assert source.read_context_keys() == ["user_input", "locale"]


@pytest.mark.parametrize("position", [0, 1])
def test_context_ref_outside_the_acquisition_is_rejected(position) -> None:
    # A raw key names a slot in the caller's namespace.  Allowing it after the
    # acquisition would reintroduce the shared mutable slot that value
    # references replace, so it is refused wherever the acquisition cannot see.
    sequence = [
        IRInstruction(
            id="ir_001", opcode="compute", outputs=[make_result("result_v1")]
        ),
        IRInstruction(id="ir_002", opcode="return", inputs=[make_result("result_v1")]),
    ]
    sequence[position].inputs.insert(0, context("locale"))
    with pytest.raises(
        ValidationError, match="only allowed in a context source acquisition"
    ):
        BasicBlock(block_id="b1", block_name="测试块", instructions=sequence)


def test_context_source_terminator_may_not_read_raw_keys() -> None:
    with pytest.raises(
        ValidationError, match="only allowed in a context source acquisition"
    ):
        make_context_source(
            instructions=[
                IRInstruction(
                    id="ir_001",
                    opcode="read_context",
                    inputs=[context("user_input")],
                    outputs=[make_result("request_v1")],
                ),
                IRInstruction(
                    id="ir_002", opcode="dispatch", inputs=[context("user_input")]
                ),
            ]
        )


@pytest.mark.parametrize(
    "opcode", ["http_get", "read_db", "read_context", "my_custom_operation"]
)
def test_business_opcode_spelling_has_no_special_source_rule(opcode) -> None:
    block = BasicBlock(
        block_id="operation",
        block_name="operation",
        instructions=[
            IRInstruction(
                id="ir_001",
                opcode=opcode,
                inputs=[resource("resource")],
                outputs=[make_result("response")],
            ),
            IRInstruction(
                id="ir_002", opcode="return", inputs=[make_result("response")]
            ),
        ],
    )
    assert block.validate_dataflow() is True


@pytest.mark.parametrize("opcode", ["dispatch", "return"])
def test_dataflow_revalidation_rejects_fabricated_terminator_outputs(opcode) -> None:
    block = BasicBlock(
        block_id="mutated",
        block_name="mutated",
        instructions=[IRInstruction(id="ir_001", opcode=opcode)],
    )
    block.instructions[0].outputs.append(make_result("fabricated_v1"))
    with pytest.raises(ValueError, match="must not produce outputs"):
        block.validate_dataflow()


@pytest.mark.parametrize(
    "legacy_field",
    ["context_requires", "context_provides", "context_exports", "context_passthrough"],
)
@pytest.mark.parametrize("model", [BasicBlock, CandidateBlock])
def test_retired_shared_context_fields_are_rejected(model, legacy_field) -> None:
    # Nothing declares availability any more, so a candidate still carrying the
    # shared-context contract is stale rather than merely redundant.
    identity = (
        {"block_id": "test", "block_name": "test"}
        if model is BasicBlock
        else {"block_ref": "test", "block_name": "test"}
    )
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        model(**identity, **{legacy_field: ["x"]})


def test_candidate_block_normalizes_names_and_keeps_source_kind() -> None:
    candidate = CandidateBlock(
        block_ref=" test ", block_name=" 读入请求 ", data_source_kind="external"
    )
    assert (candidate.block_ref, candidate.block_name) == ("test", "读入请求")
    assert candidate.data_source_kind == "external"
    assert candidate.instructions == []
