"""Hand-built CFG used only by tests."""

from __future__ import annotations

from typing import Any
from skillflow.graph import BasicBlock
from skillflow.graph import IRInstruction
from skillflow.graph import Operand
from skillflow.graph import OperandType
from skillflow.graph import CFGEdge
from skillflow.graph import ControlFlowGraph


def _operand_result(identifier: str, semantic_name: str | None = None) -> Operand:
    return Operand(
        type=OperandType.RESULT, identifier=identifier, semantic_name=semantic_name
    )


def _operand_context(key: str) -> Operand:
    return Operand(type=OperandType.CONTEXT_KEY, identifier=key)


def _operand_literal(value: Any) -> Operand:
    return Operand(type=OperandType.LITERAL, literal_value=value)


def build_demo_cfg(*, cross_branch_read: bool = False) -> ControlFlowGraph:
    """Build a weather graph with direct references to produced results.

    ``C`` and ``D`` read ``city_v1`` through ``B`` without any relay declaration.
    ``E`` reads ``sunshine_v1`` after the branches merge; the path from the sunny
    branch is enough to pass the reference check. With ``cross_branch_read``,
    the rainy branch also reads that result. No path connects the sunny branch
    to the rainy branch, so that reference fails validation.
    """

    rainfall_inputs = [
        Operand(
            type=OperandType.EXTERNAL_RESOURCE,
            identifier="https://weather.example/rainfall",
        ),
        _operand_result("city_v1", "city"),
    ]
    if cross_branch_read:
        rainfall_inputs.append(_operand_result("sunshine_v1", "sunshine_data"))

    blocks = {
        "input": BasicBlock(
            block_id="input",
            block_name="读入用户请求",
            data_source_kind="context",
            instructions=[
                IRInstruction(
                    id="ir_input_001",
                    opcode="read_context",
                    inputs=[_operand_context("ctx.user_input")],
                    outputs=[_operand_result("request_v1", "user_input")],
                ),
                IRInstruction(id="ir_input_002", opcode="dispatch"),
            ],
        ),
        "A": BasicBlock(
            block_id="A",
            block_name="提取城市",
            instructions=[
                IRInstruction(
                    id="ir_a_001",
                    opcode="extract_slot",
                    inputs=[_operand_result("request_v1", "user_input")],
                    outputs=[_operand_result("city_v1", "city")],
                    metadata={"slot_name": "city"},
                ),
                IRInstruction(id="ir_a_003", opcode="dispatch"),
            ],
        ),
        "B": BasicBlock(
            block_id="B",
            block_name="判断天气类型",
            instructions=[
                IRInstruction(
                    id="ir_b_001",
                    opcode="call_llm",
                    inputs=[_operand_result("city_v1", "city")],
                    outputs=[_operand_result("weather_type_v1", "weather_type")],
                    metadata={"task": "classify_weather"},
                ),
                IRInstruction(
                    id="ir_b_002",
                    opcode="dispatch",
                    inputs=[_operand_result("weather_type_v1", "weather_type")],
                ),
            ],
        ),
        "C": BasicBlock(
            block_id="C",
            block_name="查询晴天数据",
            data_source_kind="external",
            instructions=[
                IRInstruction(
                    id="ir_c_001",
                    opcode="http_get",
                    inputs=[
                        Operand(
                            type=OperandType.EXTERNAL_RESOURCE,
                            identifier="https://weather.example/sunshine",
                        ),
                        _operand_result("city_v1", "city"),
                    ],
                    outputs=[_operand_result("sunshine_v1", "sunshine_data")],
                ),
                IRInstruction(id="ir_c_003", opcode="dispatch"),
            ],
        ),
        "D": BasicBlock(
            block_id="D",
            block_name="查询降雨数据",
            data_source_kind="external",
            instructions=[
                IRInstruction(
                    id="ir_d_001",
                    opcode="http_get",
                    inputs=rainfall_inputs,
                    outputs=[_operand_result("rainfall_v1", "rainfall_data")],
                ),
                IRInstruction(id="ir_d_003", opcode="dispatch"),
            ],
        ),
        "E": BasicBlock(
            block_id="E",
            block_name="生成最终回复",
            instructions=[
                IRInstruction(
                    id="ir_e_001",
                    opcode="call_llm",
                    inputs=[
                        _operand_result("sunshine_v1", "sunshine_data"),
                        _operand_literal("Generate a concise natural-language reply."),
                    ],
                    outputs=[_operand_result("reply_v1", "reply")],
                ),
                IRInstruction(
                    id="ir_e_002",
                    opcode="return",
                    inputs=[_operand_result("reply_v1", "reply")],
                ),
            ],
        ),
    }

    return ControlFlowGraph(
        entry_block_id="input",
        blocks=blocks,
        declared_context_keys=["ctx.user_input"],
        edges=[
            CFGEdge(source_block_id="input", target_block_id="A"),
            CFGEdge(source_block_id="A", target_block_id="B"),
            CFGEdge(
                source_block_id="B",
                target_block_id="C",
                condition_text="weather_type == 'sunny'",
            ),
            CFGEdge(
                source_block_id="B",
                target_block_id="D",
                condition_text="weather_type == 'rainy'",
            ),
            CFGEdge(source_block_id="C", target_block_id="E"),
            CFGEdge(source_block_id="D", target_block_id="E"),
        ],
    )
