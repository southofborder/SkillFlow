import json

import pytest

from skill_ir import (
    BasicBlock,
    CFGEdge,
    ControlFlowGraph,
    IRInstruction,
    Operand,
    OperandType,
    render_mermaid,
)
from skill_ir.cli import main as cli_main


def main(argv):
    return cli_main(["render", *argv])


def operand(
    kind: OperandType,
    identifier: str | None = None,
    literal_value=None,
    semantic_name: str | None = None,
) -> Operand:
    if kind is OperandType.LITERAL:
        return Operand(type=kind, literal_value=literal_value)
    return Operand(type=kind, identifier=identifier, semantic_name=semantic_name)


def make_cfg() -> ControlFlowGraph:
    return ControlFlowGraph(
        entry_block_id="entry/block",
        declared_context_keys=["user_input"],
        blocks={
            "entry/block": BasicBlock(
                block_id="entry/block",
                block_name='Read "input" <safely>',
                data_source_kind="context",
                instructions=[
                    IRInstruction(
                        id="ir_001",
                        opcode="read_context",
                        inputs=[operand(OperandType.CONTEXT_KEY, "user_input")],
                        outputs=[operand(OperandType.RESULT, "raw_message")],
                    ),
                    IRInstruction(
                        id="ir_002",
                        opcode="dispatch",
                    ),
                ],
            ),
            "decision": BasicBlock(
                block_id="decision",
                block_name="Check urgency",
                instructions=[
                    IRInstruction(
                        id="ir_003",
                        opcode="is_urgent",
                        inputs=[operand(OperandType.RESULT, "raw_message")],
                        outputs=[operand(OperandType.RESULT, "urgent")],
                    ),
                    IRInstruction(
                        id="ir_004",
                        opcode="dispatch",
                        inputs=[operand(OperandType.RESULT, "urgent")],
                    ),
                ],
            ),
            "send:alert": BasicBlock(
                block_id="send:alert",
                block_name="Send alert",
                data_source_kind="external",
                instructions=[
                    IRInstruction(
                        id="ir_005",
                        opcode="post_alert",
                        inputs=[
                            operand(OperandType.EXTERNAL_RESOURCE, "alerts|api"),
                            operand(OperandType.RESULT, "raw_message"),
                            operand(
                                OperandType.LITERAL, literal_value={"kind": "urgent"}
                            ),
                        ],
                        outputs=[operand(OperandType.RESULT, "response")],
                    ),
                    IRInstruction(
                        id="ir_006",
                        opcode="return",
                        inputs=[operand(OperandType.RESULT, "response")],
                    ),
                ],
            ),
            "fallback": BasicBlock(
                block_id="fallback",
                block_name="Fallback",
                instructions=[
                    IRInstruction(
                        id="ir_007",
                        opcode="log_skipped_alert",
                        inputs=[operand(OperandType.EXTERNAL_RESOURCE, "alerts|api")],
                    ),
                    IRInstruction(
                        id="ir_008",
                        opcode="assign",
                        inputs=[
                            operand(
                                OperandType.LITERAL, literal_value="No alert needed"
                            )
                        ],
                        outputs=[operand(OperandType.RESULT, "fallback_value")],
                    ),
                    IRInstruction(
                        id="ir_009",
                        opcode="return",
                        inputs=[operand(OperandType.RESULT, "fallback_value")],
                    ),
                ],
            ),
        },
        edges=[
            CFGEdge(
                source_block_id="entry/block",
                target_block_id="decision",
            ),
            CFGEdge(
                source_block_id="decision",
                target_block_id="send:alert",
                condition_text="urgent | yes",
            ),
            CFGEdge(
                source_block_id="decision",
                target_block_id="fallback",
                condition_text="not urgent",
            ),
        ],
    )


def box(rendered: str, node_id: str) -> str:
    """Return the single Mermaid line holding one block's box."""

    return next(line for line in rendered.splitlines() if f'{node_id}["' in line)


def analysis_payload(cfg: ControlFlowGraph, *, status: str = "complete") -> dict:
    return {"status": status, "cfg": json.loads(cfg.to_json())}


def test_render_mermaid_uses_one_multiline_box_per_block() -> None:
    rendered = render_mermaid(make_cfg())

    assert (
        'block_node_001["<b>entry/block</b>: Read &quot;input&quot; &lt;safely&gt;'
        in rendered
    )
    assert "ir_001</code>: <code>read_context</code>" in rendered
    assert "ir_002</code>: <code>dispatch</code>" in rendered
    assert rendered.count('["<b>') == 4


def test_render_mermaid_renders_guarded_cfg_edges() -> None:
    rendered = render_mermaid(make_cfg())

    assert "block_node_001 --> block_node_002" in rendered
    assert "block_node_002 -->|urgent &#124; yes| block_node_003" in rendered
    assert "block_node_002 -->|not urgent| block_node_004" in rendered


def test_render_mermaid_deduplicates_external_resource_nodes() -> None:
    rendered = render_mermaid(make_cfg())

    assert rendered.count("external_resource: alerts&#124;api") == 1
    assert (
        rendered.count("resource_node_001 -.->|external_resource| block_node_003") == 1
    )
    assert (
        rendered.count("resource_node_001 -.->|external_resource| block_node_004") == 1
    )
    assert "资源标识" in rendered
    assert "alerts|api" not in rendered


def test_render_mermaid_formats_operand_types_and_literal_values() -> None:
    rendered = render_mermaid(make_cfg())

    assert "读取上下文：context_key:user_input" in rendered
    assert (
        "输入：external_resource:alerts&#124;api, raw_message, "
        "literal:{&quot;kind&quot;:&quot;urgent&quot;}" in rendered
    )
    assert "产出：response" in rendered
    assert "local_dep" not in rendered


def test_render_mermaid_distinguishes_sources_and_value_references() -> None:
    rendered = render_mermaid(make_cfg())

    assert "source · context（上下文读入）" in rendered
    assert "source · external（外部数据读入）" in rendered
    # The source produces a value and references none; its consumers reference
    # it by the identifier of that definition point.
    entry = box(rendered, "block_node_001")
    assert "产出：raw_message" in entry
    assert "引用其他块的结果：" not in entry
    assert "引用其他块的结果：raw_message" in box(rendered, "block_node_002")
    assert "引用其他块的结果：raw_message" in box(rendered, "block_node_003")
    assert "class block_node_001,block_node_003 source;" in rendered
    assert "class block_node_001 entry;" in rendered


def test_render_mermaid_says_nothing_about_a_value_a_block_never_touches() -> None:
    """A block between definition and use relays nothing, so it shows nothing."""

    cfg = make_cfg()
    decision = cfg.blocks["decision"]
    decision.instructions = [
        IRInstruction(
            id="ir_003",
            opcode="dispatch",
            inputs=[operand(OperandType.LITERAL, literal_value=True)],
        )
    ]

    rendered = render_mermaid(cfg)

    decision_line = box(rendered, "block_node_002")
    assert "raw_message" not in decision_line
    assert "引用其他块的结果：" not in decision_line
    assert "产出：" not in decision_line
    # The value still crosses it: the block that reads it two hops later is
    # unaffected by the fact that nothing carried it.
    assert "引用其他块的结果：raw_message" in box(rendered, "block_node_003")


def make_canonical_cfg() -> ControlFlowGraph:
    """Build the graph as compilation leaves it: canonical IDs plus wording.

    ``result_001`` says nothing on its own, so every place the ID appears is a
    place an audit cannot read without the identifier the extractor used.
    """

    return ControlFlowGraph(
        entry_block_id="block_001",
        declared_context_keys=["user_input"],
        blocks={
            "block_001": BasicBlock(
                block_id="block_001",
                block_name="读入用户消息",
                data_source_kind="context",
                instructions=[
                    IRInstruction(
                        id="ir_001",
                        opcode="read_context",
                        inputs=[operand(OperandType.CONTEXT_KEY, "user_input")],
                        outputs=[
                            operand(
                                OperandType.RESULT,
                                "result_001",
                                semantic_name="raw_message",
                            )
                        ],
                    ),
                    IRInstruction(id="ir_002", opcode="dispatch"),
                ],
            ),
            "block_002": BasicBlock(
                block_id="block_002",
                block_name="发送告警",
                instructions=[
                    IRInstruction(
                        id="ir_003",
                        opcode="post_alert",
                        inputs=[
                            operand(
                                OperandType.EXTERNAL_RESOURCE,
                                "alerts_api",
                                semantic_name="alerts_api",
                            ),
                            operand(
                                OperandType.RESULT,
                                "result_001",
                                semantic_name="raw_message",
                            ),
                        ],
                        outputs=[
                            operand(
                                OperandType.RESULT,
                                "result_002",
                                semantic_name="ack_status",
                            )
                        ],
                    ),
                    IRInstruction(
                        id="ir_004",
                        opcode="return",
                        inputs=[
                            operand(
                                OperandType.RESULT,
                                "result_002",
                                semantic_name="ack_status",
                            )
                        ],
                    ),
                ],
            ),
        },
        edges=[CFGEdge(source_block_id="block_001", target_block_id="block_002")],
    )


def test_render_mermaid_names_canonical_values_by_their_extractor_wording() -> None:
    rendered = render_mermaid(make_canonical_cfg())

    assert "产出：raw_message（result_001）" in rendered
    assert "输入：external_resource:alerts_api, raw_message（result_001）" in rendered
    # An operand keeps its own wording; the summary lines have no operand to read
    # it off and look it up on the graph instead.
    assert "产出：raw_message（result_001）" in box(rendered, "block_node_001")
    assert "引用其他块的结果：raw_message（result_001）" in box(
        rendered, "block_node_002"
    )
    assert "产出：ack_status（result_002）" in box(rendered, "block_node_002")


def test_render_mermaid_omits_a_wording_that_repeats_the_name() -> None:
    """A resource already carries its own identifier; printing it twice says nothing."""

    rendered = render_mermaid(make_canonical_cfg())

    assert "external_resource:alerts_api (alerts_api)" not in rendered
    # Same rule for a value the extractor named exactly as it was compiled.
    graph = make_canonical_cfg()
    graph.blocks["block_001"].instructions[0].outputs[0].semantic_name = "result_001"
    graph.blocks["block_002"].instructions[0].inputs[1].semantic_name = "result_001"
    other = render_mermaid(graph)
    assert "result_001（result_001）" not in other
    assert "产出：result_001（result_001）" not in other
    assert "产出：result_001" in other


def test_render_mermaid_escapes_an_extractor_wording() -> None:
    graph = make_canonical_cfg()
    graph.blocks["block_001"].instructions[0].outputs[0].semantic_name = 'raw|"<msg>'

    rendered = render_mermaid(graph)

    assert "产出：raw&#124;&quot;&lt;msg&gt;（result_001）" in rendered
    assert "产出：raw&#124;&quot;&lt;msg&gt;（result_001）" in rendered
    assert 'raw|"<msg>' not in rendered


def test_render_mermaid_escapes_value_names() -> None:
    cfg = make_cfg()
    acquisition = cfg.blocks["entry/block"].instructions[0]
    acquisition.outputs.append(operand(OperandType.RESULT, 'extra|"<key>'))

    rendered = render_mermaid(cfg)

    assert "产出：raw_message, extra&#124;&quot;&lt;key&gt;" in rendered


def test_render_mermaid_keeps_apostrophes_readable() -> None:
    graph = make_cfg()
    graph.blocks["entry/block"].block_name = "Read the user's message"
    rendered = render_mermaid(graph)
    assert "Read the user's message" in rendered
    assert "&#x27;" not in rendered


def test_render_mermaid_rejects_invalid_global_dataflow() -> None:
    cfg = make_cfg()
    cfg.blocks["send:alert"].instructions[0].inputs.append(
        operand(OperandType.RESULT, "missing_value")
    )

    with pytest.raises(ValueError, match="missing_value"):
        render_mermaid(cfg)


def test_flowchart_cli_writes_mermaid_for_complete_analysis(tmp_path, capsys) -> None:
    analysis_path = tmp_path / "analysis.json"
    output_path = tmp_path / "nested" / "result.mmd"
    analysis_path.write_text(
        json.dumps(analysis_payload(make_cfg()), ensure_ascii=False),
        encoding="utf-8",
    )

    assert main(["--input", str(analysis_path), "--output", str(output_path)]) == 0
    assert "flowchart TD" in output_path.read_text(encoding="utf-8")
    assert "wrote" in capsys.readouterr().err


def test_flowchart_cli_prints_to_stdout_without_output_path(tmp_path, capsys) -> None:
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(
        json.dumps(analysis_payload(make_cfg())),
        encoding="utf-8",
    )

    assert main(["--input", str(analysis_path)]) == 0
    assert capsys.readouterr().out.startswith("flowchart TD\n")


def test_flowchart_cli_rejects_literal_payload_on_a_reference(tmp_path) -> None:
    analysis_path = tmp_path / "invalid-analysis.json"
    payload = analysis_payload(make_cfg())
    first_block = next(iter(payload["cfg"]["blocks"].values()))
    first_block["instructions"][0]["inputs"][0]["literal_value"] = None
    analysis_path.write_text(json.dumps(payload), encoding="utf-8")
    assert main(["--input", str(analysis_path)]) == 2


def test_flowchart_cli_requires_regeneration_when_source_kind_is_missing(
    tmp_path, capsys
) -> None:
    analysis_path = tmp_path / "old-contract.json"
    output_path = tmp_path / "should-not-exist.mmd"
    payload = analysis_payload(make_cfg())
    del payload["cfg"]["blocks"]["entry/block"]["data_source_kind"]
    analysis_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--input", str(analysis_path), "--output", str(output_path)]) == 2
    error = capsys.readouterr().err
    assert "entry/block" in error
    assert "data_source_kind" in error
    assert "regenerate" in error
    assert not output_path.exists()


@pytest.mark.parametrize(
    "field, legacy_value",
    [
        ("context_exports", {"message": "raw_message"}),
        ("context_passthrough", ["message"]),
    ],
)
def test_flowchart_cli_refuses_the_retired_shared_context_contract(
    tmp_path, capsys, field, legacy_value
) -> None:
    """Its ``local_dep`` names are block-scoped, so reading them as value
    references could merge two unrelated values that happen to share a identifier."""

    analysis_path = tmp_path / "old-contract.json"
    output_path = tmp_path / "should-not-exist.mmd"
    payload = analysis_payload(make_cfg())
    payload["cfg"]["blocks"]["entry/block"][field] = legacy_value
    analysis_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--input", str(analysis_path), "--output", str(output_path)]) == 2
    error = capsys.readouterr().err
    assert "entry/block" in error
    assert field in error
    assert "regenerate" in error
    assert not output_path.exists()


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"status": "degraded", "cfg": None}, "degraded"),
        ({"status": "complete"}, "does not contain cfg"),
    ],
)
def test_flowchart_cli_rejects_unusable_analysis_results(
    tmp_path, capsys, payload, message
) -> None:
    analysis_path = tmp_path / "analysis.json"
    output_path = tmp_path / "should-not-exist.mmd"
    analysis_path.write_text(json.dumps(payload), encoding="utf-8")

    assert main(["--input", str(analysis_path), "--output", str(output_path)]) == 2
    assert message in capsys.readouterr().err
    assert not output_path.exists()
