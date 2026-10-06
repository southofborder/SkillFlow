from skillflow.graph.analysis.availability import analyze_availability
import pytest

from skillflow.graph import CandidateBlock
from skillflow.graph import CandidateEdge
from skillflow.graph import CandidateInstruction
from skillflow.graph import IRAnalysisCandidate
from skillflow.graph import Operand
from skillflow.graph import OperandType
from skillflow.graph import compile_candidate


def make_result(identifier: str, semantic_name: str | None = None) -> Operand:
    return Operand(
        type=OperandType.RESULT, identifier=identifier, semantic_name=semantic_name
    )


def context(identifier: str) -> Operand:
    return Operand(type=OperandType.CONTEXT_KEY, identifier=identifier)


def resource(identifier: str) -> Operand:
    return Operand(type=OperandType.EXTERNAL_RESOURCE, identifier=identifier)


def valid_candidate() -> IRAnalysisCandidate:
    """A context source followed by a block that reads the value it produced."""

    return IRAnalysisCandidate(
        entry_block_ref="start",
        declared_context_keys=["user_input"],
        blocks=[
            CandidateBlock(
                block_ref="start",
                block_name="读入用户输入",
                data_source_kind="context",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="read_input",
                        opcode="read_context",
                        inputs=[context("user_input")],
                        outputs=[make_result("input_value")],
                    ),
                    CandidateInstruction(
                        instruction_ref="start_jump", opcode="dispatch"
                    ),
                ],
            ),
            CandidateBlock(
                block_ref="compute",
                block_name="提取城市并格式化结果",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="extract_city",
                        opcode="extract_city",
                        inputs=[make_result("input_value")],
                        outputs=[make_result("city")],
                    ),
                    CandidateInstruction(
                        instruction_ref="format_answer",
                        opcode="format_answer",
                        inputs=[make_result("city")],
                        outputs=[make_result("answer")],
                    ),
                    CandidateInstruction(
                        instruction_ref="return_answer",
                        opcode="return",
                        inputs=[make_result("answer")],
                    ),
                ],
            ),
        ],
        edges=[CandidateEdge(source_block_ref="start", target_block_ref="compute")],
    )


def test_compile_candidate_normalizes_ids_ssa_and_keeps_block_name() -> None:
    result = compile_candidate(valid_candidate())

    assert result.ok is True
    assert result.cfg is not None
    source = result.cfg.blocks["block_001"]
    assert source.data_source_kind == "context"
    assert source.read_context_keys() == ["user_input"]
    assert source.produced_result_ids() == ["result_001"]

    block = result.cfg.blocks["block_002"]
    assert block.block_name == "提取城市并格式化结果"
    assert [instruction.id for instruction in block.instructions] == [
        "ir_003",
        "ir_004",
        "ir_005",
    ]
    assert block.instructions[0].draft_instruction_id == "extract_city"
    assert block.instructions[1].opcode == "format_answer"
    # The value produced two blocks away is referenced directly, and the
    # extractor's own wording survives the rename so the reference can be
    # backtranslated into a sentence.
    assert block.instructions[0].inputs[0].identifier == "result_001"
    assert block.instructions[0].inputs[0].semantic_name == "input_value"
    assert block.instructions[0].outputs[0].identifier == "result_002"
    assert block.instructions[1].inputs[0].identifier == "result_002"
    assert block.instructions[1].outputs[0].identifier == "result_003"
    assert block.cross_block_result_ids() == ["result_001"]


def test_open_opcode_is_accepted_by_final_instruction() -> None:
    candidate = valid_candidate()
    candidate.blocks[1].instructions[1].opcode = "custom_black_box_operation"

    result = compile_candidate(candidate)

    assert result.ok is True
    assert (
        result.cfg.blocks["block_002"].instructions[1].opcode
        == "custom_black_box_operation"
    )


def test_value_produced_by_no_instruction_is_rejected() -> None:
    candidate = valid_candidate()
    candidate.blocks[1].instructions[0].inputs = [make_result("not_produced_anywhere")]

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(item.code == "RESULT_NOT_DEFINED" for item in result.diagnostics)


def test_value_read_before_its_own_definition_is_a_block_error() -> None:
    """Reordering inside one block is wrong no matter what the graph looks like."""

    candidate = valid_candidate()
    compute = candidate.blocks[1].instructions
    compute[0], compute[1] = compute[1], compute[0]

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(
        item.code == "RESULT_READ_BEFORE_DEFINITION" for item in result.diagnostics
    )
    assert any(
        "is read before instruction" in item.message for item in result.diagnostics
    )
    early_read = next(
        item
        for item in result.diagnostics
        if item.code == "RESULT_READ_BEFORE_DEFINITION"
    )
    assert "result_003" in early_read.message and "'city'" in early_read.message
    assert candidate.blocks[1].block_name in early_read.message


def test_duplicate_value_name_across_blocks_is_rejected() -> None:
    """One identifier, two definition points: the reference would be ambiguous."""

    candidate = valid_candidate()
    candidate.blocks[1].instructions[0].outputs = [
        make_result("city"),
        make_result("input_value"),
    ]

    result = compile_candidate(candidate)

    assert result.ok is False
    duplicates = [
        item
        for item in result.diagnostics
        if item.code == "DUPLICATE_RESULT_IDENTIFIER"
    ]
    assert len(duplicates) == 1
    assert "input_value" in duplicates[0].message
    assert "blocks[0].instructions[0].outputs[0]" in duplicates[0].message


def test_output_that_is_not_a_value_reference_is_rejected() -> None:
    candidate = valid_candidate()
    candidate.blocks[1].instructions.insert(
        2,
        CandidateInstruction(
            instruction_ref="log_answer",
            opcode="log_answer",
            inputs=[make_result("answer")],
            outputs=[Operand(type=OperandType.LITERAL, literal_value="ok")],
        ),
    )

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(item.code == "OUTPUT_NOT_RESULT" for item in result.diagnostics)


def test_dispatch_requires_an_outgoing_edge() -> None:
    candidate = valid_candidate()
    candidate.blocks[1].instructions[-1].opcode = "dispatch"
    candidate.blocks[1].instructions[-1].inputs = []

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(item.code == "CFG_STRUCTURE_INVALID" for item in result.diagnostics)


def test_terminator_outputs_are_reported_as_compile_diagnostic() -> None:
    candidate = valid_candidate()
    candidate.blocks[1].instructions[-1].outputs = [make_result("invalid")]

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(item.code == "IR_INSTRUCTION_INVALID" for item in result.diagnostics)
    assert any(
        "return must not produce outputs" in item.message for item in result.diagnostics
    )


def test_cross_block_value_reference_compiles() -> None:
    """The read no longer needs a shared key: it names the definition point."""

    candidate = IRAnalysisCandidate(
        entry_block_ref="a",
        blocks=[
            CandidateBlock(
                block_ref="a",
                block_name="生产值",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="produce",
                        opcode="produce",
                        outputs=[make_result("payload")],
                    ),
                    CandidateInstruction(instruction_ref="jump", opcode="dispatch"),
                ],
            ),
            CandidateBlock(
                block_ref="b",
                block_name="消费值",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="consume",
                        opcode="consume",
                        inputs=[make_result("payload")],
                    ),
                    CandidateInstruction(instruction_ref="finish", opcode="return"),
                ],
            ),
        ],
        edges=[CandidateEdge(source_block_ref="a", target_block_ref="b")],
    )

    result = compile_candidate(candidate)

    assert result.ok is True, result.diagnostics
    consumer = result.cfg.blocks["block_002"]
    assert consumer.instructions[0].inputs[0].identifier == "result_001"
    assert consumer.cross_block_result_ids() == ["result_001"]
    analysis = analyze_availability(result.cfg)
    assert analysis.entry_availability("block_002", "result_001") == "all_paths"


def test_missing_block_name_is_a_candidate_schema_error() -> None:
    raw = valid_candidate().model_dump(mode="json", exclude_none=True)
    del raw["blocks"][0]["block_name"]

    result = compile_candidate(raw)

    assert result.ok is False
    assert any(item.code == "CANDIDATE_SCHEMA_INVALID" for item in result.diagnostics)


@pytest.mark.parametrize(
    "legacy_field",
    ["context_exports", "context_passthrough", "context_requires", "context_provides"],
)
def test_candidate_rejects_the_retired_shared_context_contract(
    legacy_field: str,
) -> None:
    """A block may not declare what other blocks can read; paths decide that."""

    raw = valid_candidate().model_dump(mode="json", exclude_none=True)
    raw["blocks"][1][legacy_field] = ["user_input"]

    result = compile_candidate(raw)

    assert result.ok is False
    assert any(
        item.code == "CANDIDATE_SCHEMA_INVALID" and legacy_field in item.path
        for item in result.diagnostics
    )


def test_initial_keys_do_not_allow_an_ordinary_block_to_bypass_source() -> None:
    candidate = valid_candidate()
    candidate.entry_block_ref = "compute"
    candidate.blocks = candidate.blocks[1:]
    candidate.edges = []

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(
        item.code == "RESULT_NOT_DEFINED" and "input_value" in item.message
        for item in result.diagnostics
    )


def test_context_key_outside_an_acquisition_is_rejected() -> None:
    """Naming a raw key mid-graph would reintroduce the shared mutable slot."""

    candidate = valid_candidate()
    candidate.blocks[1].instructions[0].inputs = [context("user_input")]

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(
        item.code == "BASIC_BLOCK_INVALID"
        and "only allowed in a context source acquisition" in item.message
        for item in result.diagnostics
    )


def test_raw_key_not_declared_in_initial_context_keys_is_rejected() -> None:
    candidate = valid_candidate()
    candidate.blocks[0].instructions[0].inputs = [context("undeclared_input")]

    result = compile_candidate(candidate)

    assert result.ok is False
    assert any(
        item.code == "CONTEXT_KEY_NOT_DECLARED" and "undeclared_input" in item.message
        for item in result.diagnostics
    )


def test_multivalue_source_and_external_read_with_existing_value() -> None:
    """A value crossing a block that never touches it is passthrough, and derived.

    ``language`` is read only by the last block, so the middle block relays
    nothing: the propagation pass observes that the value passes through it.
    """

    candidate = IRAnalysisCandidate(
        entry_block_ref="source",
        declared_context_keys=["city", "language"],
        blocks=[
            CandidateBlock(
                block_ref="source",
                block_name="读入查询参数",
                data_source_kind="context",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="read_params",
                        opcode="read_context",
                        inputs=[context("city"), context("language")],
                        outputs=[make_result("city_in"), make_result("language_in")],
                    ),
                    CandidateInstruction(
                        instruction_ref="query_jump", opcode="dispatch"
                    ),
                ],
            ),
            CandidateBlock(
                block_ref="weather",
                block_name="按城市查询天气",
                data_source_kind="external",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="read_weather",
                        opcode="call_weather_service",
                        inputs=[resource("weather_api"), make_result("city_in")],
                        outputs=[make_result("weather_result")],
                    ),
                    CandidateInstruction(
                        instruction_ref="render_jump", opcode="dispatch"
                    ),
                ],
            ),
            CandidateBlock(
                block_ref="render",
                block_name="返回指定语言的天气",
                instructions=[
                    CandidateInstruction(
                        instruction_ref="render_weather",
                        opcode="format_weather",
                        inputs=[
                            make_result("weather_result"),
                            make_result("language_in"),
                        ],
                        outputs=[make_result("answer")],
                    ),
                    CandidateInstruction(
                        instruction_ref="done",
                        opcode="return",
                        inputs=[make_result("answer")],
                    ),
                ],
            ),
        ],
        edges=[
            CandidateEdge(source_block_ref="source", target_block_ref="weather"),
            CandidateEdge(source_block_ref="weather", target_block_ref="render"),
        ],
    )

    result = compile_candidate(candidate)

    assert result.ok is True, result.diagnostics
    source, weather, render = result.cfg.blocks.values()
    assert source.read_context_keys() == ["city", "language"]
    assert source.produced_result_ids() == ["result_001", "result_002"]
    assert weather.data_source_kind == "external"
    assert weather.produced_result_ids() == ["result_003"]
    assert weather.cross_block_result_ids() == ["result_001"]
    # Reported in read order, which is the operand order of the instruction.
    assert render.cross_block_result_ids() == ["result_003", "result_002"]

    analysis = analyze_availability(result.cfg)
    assert analysis.untouched_results["block_002"] == frozenset({"result_002"})
    assert analysis.guaranteed_results_on_entry["block_003"] == frozenset(
        {"result_001", "result_002", "result_003"}
    )
    assert analysis.unavailable_reads == ()
    assert analysis.path_dependent_reads == ()
