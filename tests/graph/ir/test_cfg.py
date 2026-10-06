from skillflow.graph.analysis.availability import analyze_availability
import pytest
from pydantic import ValidationError

from skillflow.graph import BasicBlock
from skillflow.graph import CFGEdge
from skillflow.graph import ControlFlowGraph
from skillflow.graph import IRInstruction
from skillflow.graph import Operand
from tests.fixtures.demo_cfg import build_demo_cfg


def make_result(identifier: str, semantic_name: str | None = None) -> Operand:
    return Operand(type="result", identifier=identifier, semantic_name=semantic_name)


def block(
    block_id: str,
    *,
    reads: list[str] | None = None,
    writes: list[str] | None = None,
    opcode: str = "compute",
    terminator: str = "dispatch",
) -> BasicBlock:
    sequence = []
    if reads or writes:
        sequence.append(
            IRInstruction(
                id=f"ir_{block_id}_work",
                opcode=opcode,
                inputs=[make_result(identifier) for identifier in reads or []],
                outputs=[make_result(identifier) for identifier in writes or []],
            )
        )
    sequence.append(
        IRInstruction(
            id=f"ir_{block_id}_end",
            opcode=terminator,
            inputs=[Operand(type="literal", literal_value=True)],
        )
    )
    return BasicBlock(
        block_id=block_id,
        block_name=f"语义块 {block_id}",
        instructions=sequence,
    )


def source(block_id: str = "A", key: str = "x", produces: str = "x_v1") -> BasicBlock:
    return BasicBlock(
        block_id=block_id,
        block_name=f"读取 {key}",
        data_source_kind="context",
        instructions=[
            IRInstruction(
                id=f"ir_{block_id}_read",
                opcode="read_context",
                inputs=[Operand(type="context_key", identifier=key)],
                outputs=[make_result(produces, key)],
            ),
            # The branch condition of a source block depends on what it read, so
            # the terminator names that value rather than an opaque literal.
            IRInstruction(
                id=f"ir_{block_id}_end",
                opcode="dispatch",
                inputs=[make_result(produces, key)],
            ),
        ],
    )


def cfg(
    blocks: dict[str, BasicBlock],
    edges: list[CFGEdge],
    *,
    entry: str = "A",
    initial: list[str] | None = None,
) -> ControlFlowGraph:
    return ControlFlowGraph(
        entry_block_id=entry,
        blocks=blocks,
        edges=edges,
        declared_context_keys=initial or [],
    )


def edge(start: str, end: str, condition_text: str | None = None) -> CFGEdge:
    return CFGEdge(
        source_block_id=start, target_block_id=end, condition_text=condition_text
    )


def test_end_to_end_demo_passes_and_reports_the_branch_only_read() -> None:
    graph = build_demo_cfg()

    assert graph.validate_integrity() is True
    rendered = graph.to_json()
    assert '"ctx.user_input"' in rendered
    assert "weather_type == 'sunny'" in rendered
    assert "weather_type == 'rainy'" in rendered

    analysis = analyze_availability(graph)
    # ``sunshine_v1`` exists only on the sunny branch, and the merge block reads
    # it anyway. That is what a branch looks like, so it is described, not refused.
    assert [(use.block_id, use.result_id) for use in analysis.path_dependent_reads] == [
        ("E", "sunshine_v1")
    ]
    assert analysis.unavailable_reads == ()


def test_value_names_report_what_the_extractor_called_each_value() -> None:
    """An audit reading the graph needs more than the IDs compilation assigned."""

    names = build_demo_cfg().result_semantic_names()

    assert names["city_v1"] == "city"
    assert names["weather_type_v1"] == "weather_type"
    assert names["sunshine_v1"] == "sunshine_data"
    # Only value references are named; a resource already carries its own identifier.
    assert "https://weather.example/sunshine" not in names


def test_value_names_prefer_the_definition_site_over_a_reader() -> None:
    """A value is what its definition says it is, however a reader worded it."""

    graph = cfg(
        {
            "A": BasicBlock(
                block_id="A",
                block_name="读入",
                data_source_kind="context",
                instructions=[
                    IRInstruction(
                        id="ir_a_read",
                        opcode="read_context",
                        inputs=[Operand(type="context_key", identifier="x")],
                        outputs=[make_result("x_v1", "城市名")],
                    ),
                    IRInstruction(
                        id="ir_a_end",
                        opcode="dispatch",
                        inputs=[make_result("x_v1", "城市名")],
                    ),
                ],
            ),
            "B": BasicBlock(
                block_id="B",
                block_name="使用",
                instructions=[
                    IRInstruction(
                        id="ir_b_use",
                        opcode="compute",
                        inputs=[make_result("x_v1", "那个城市")],
                        outputs=[make_result("y_v1")],
                    ),
                    IRInstruction(
                        id="ir_b_end", opcode="return", inputs=[make_result("y_v1")]
                    ),
                ],
            ),
        },
        [edge("A", "B")],
        initial=["x"],
    )

    assert graph.validate_integrity() is True
    names = graph.result_semantic_names()
    assert names["x_v1"] == "城市名"
    # A value nobody worded differently is left out, so callers can print the
    # extra identifier exactly when there is one to print.
    assert "y_v1" not in names


def test_end_to_end_demo_rejects_a_read_no_path_can_satisfy() -> None:
    graph = build_demo_cfg(cross_branch_read=True)

    with pytest.raises(
        ValueError,
        match=r"block 'D'.*'sunshine_v1'.*does not reach here along any path",
    ):
        graph.validate_integrity()


def test_dataflow_errors_name_what_the_extractor_wrote() -> None:
    """Compilation renames everything, so canonical IDs alone locate nothing.

    The error travels back to the extractor in a repair prompt whose only other
    content is the candidate it wrote, where ``result_00N`` never appears.
    """

    graph = build_demo_cfg(cross_branch_read=True)

    with pytest.raises(ValueError) as error:
        graph.validate_integrity()

    message = str(error.value)
    assert "result 'sunshine_v1' ('sunshine_data')" in message
    assert "block 'D' (查询降雨数据)" in message
    assert "block 'C' (查询晴天数据)" in message


def test_declaring_an_initial_context_key_makes_no_value_available() -> None:
    """The declaration authorizes an acquisition; it does not perform one."""

    graph = cfg(
        {"A": block("A", reads=["x_v1"], terminator="return")},
        [],
        initial=["x"],
    )

    with pytest.raises(
        ValueError,
        match=r"'x_v1' is not available; no instruction in the graph defines it",
    ):
        graph.validate_integrity()


def test_invalid_entry_and_edge_endpoints_are_rejected() -> None:
    with pytest.raises((ValidationError, ValueError), match="entry block"):
        cfg({"A": block("A", terminator="return")}, [], entry="missing")

    with pytest.raises((ValidationError, ValueError), match="source block"):
        cfg(
            {"A": block("A", terminator="dispatch")},
            [CFGEdge(source_block_id="missing", target_block_id="A")],
        )

    with pytest.raises((ValidationError, ValueError), match="target block"):
        cfg(
            {"A": block("A", terminator="dispatch")},
            [CFGEdge(source_block_id="A", target_block_id="missing")],
        )


def test_block_key_must_match_block_id() -> None:
    with pytest.raises((ValidationError, ValueError), match="does not match"):
        cfg({"wrong-key": block("A", terminator="return")}, [])


def test_terminator_and_edge_consistency() -> None:
    with pytest.raises((ValidationError, ValueError), match="RETURN.*outgoing"):
        cfg(
            {
                "A": block("A", terminator="return"),
                "B": block("B", terminator="return"),
            },
            [CFGEdge(source_block_id="A", target_block_id="B")],
        )

    with pytest.raises((ValidationError, ValueError), match="DISPATCH.*no outgoing"):
        cfg({"A": block("A", terminator="dispatch")}, [])

    with pytest.raises((ValidationError, ValueError), match="last instruction"):
        BasicBlock(
            block_id="A",
            block_name="测试块",
            instructions=[IRInstruction(id="ir_a_001", opcode="assign")],
        )


def test_value_defined_by_a_predecessor_is_available() -> None:
    graph = cfg(
        {
            "A": block("A", writes=["city_v1"]),
            "B": block("B", reads=["city_v1"], terminator="return"),
        },
        [edge("A", "B")],
    )

    assert graph.validate_integrity() is True
    assert analyze_availability(graph).entry_availability("B", "city_v1") == "all_paths"


def test_duplicate_edges_are_rejected_but_distinct_guards_are_allowed() -> None:
    with pytest.raises((ValidationError, ValueError), match="duplicate edge"):
        cfg(
            {"A": block("A"), "B": block("B", terminator="return")},
            [
                CFGEdge(source_block_id="A", target_block_id="B"),
                CFGEdge(source_block_id="A", target_block_id="B"),
            ],
        )

    graph = cfg(
        {"A": block("A"), "B": block("B", terminator="return")},
        [
            CFGEdge(source_block_id="A", target_block_id="B", condition_text="x == 1"),
            CFGEdge(source_block_id="A", target_block_id="B", condition_text="x == 2"),
        ],
    )
    assert graph.validate_integrity() is True


def test_raw_context_requires_declaration_and_real_import() -> None:
    graph = cfg(
        {"A": source(), "B": block("B", reads=["x_v1"], terminator="return")},
        [edge("A", "B")],
        initial=["x"],
    )
    assert graph.validate_integrity()
    graph.declared_context_keys = []
    with pytest.raises(ValueError, match="raw context key 'x'.*declared_context_keys"):
        graph.validate_integrity()


def test_intermediate_blocks_relay_nothing_and_passthrough_is_derived() -> None:
    """No block between the definition and the read mentions the value at all."""

    graph = cfg(
        {
            "A": source(),
            "B": block("B"),
            "C": block("C"),
            "D": block("D", reads=["x_v1"], terminator="return"),
        },
        [edge("A", "B"), edge("B", "C"), edge("C", "D")],
        initial=["x"],
    )

    assert graph.validate_integrity() is True
    analysis = analyze_availability(graph)
    assert analysis.untouched_results["B"] == frozenset({"x_v1"})
    assert analysis.untouched_results["C"] == frozenset({"x_v1"})
    assert analysis.entry_availability("D", "x_v1") == "all_paths"


def test_updating_a_value_means_producing_a_new_name() -> None:
    """Both versions stay referable, and which one is meant is never ambiguous."""

    graph = cfg(
        {
            "A": source(),
            "B": block("B", reads=["x_v1"], writes=["x_v2"]),
            "C": block("C", reads=["x_v2"], terminator="return"),
        },
        [edge("A", "B"), edge("B", "C")],
        initial=["x"],
    )

    assert graph.validate_integrity() is True
    analysis = analyze_availability(graph)
    assert analysis.untouched_results["B"] == frozenset()
    assert analysis.untouched_results["C"] == frozenset({"x_v1"})
    assert analysis.guaranteed_results_on_entry["C"] == frozenset({"x_v1", "x_v2"})


def test_merge_of_a_one_branch_value_is_reported_as_may() -> None:
    graph = cfg(
        {
            "A": source(),
            "B": block("B", writes=["s_v1"]),
            "C": block("C"),
            "E": block("E", reads=["x_v1", "s_v1"], terminator="return"),
        },
        [
            edge("A", "B", "x == 1"),
            edge("A", "C", "x == 2"),
            edge("B", "E"),
            edge("C", "E"),
        ],
        initial=["x"],
    )

    assert graph.validate_integrity() is True
    analysis = analyze_availability(graph)
    assert analysis.entry_availability("E", "x_v1") == "all_paths"
    assert analysis.entry_availability("E", "s_v1") == "some_paths"
    assert [(use.block_id, use.result_id) for use in analysis.path_dependent_reads] == [
        ("E", "s_v1")
    ]
    assert analysis.dominators["E"] == frozenset({"A", "E"})


def test_a_loop_body_may_read_what_a_later_iteration_produces() -> None:
    """The backedge carries the value on the second pass, not on the first."""

    graph = cfg(
        {
            "A": source(),
            "B": block("B", reads=["y_v1"]),
            "C": block("C", writes=["y_v1"]),
            "D": block("D", reads=["x_v1"], terminator="return"),
        },
        [
            edge("A", "B"),
            edge("B", "C", "again"),
            edge("B", "D", "done"),
            edge("C", "B"),
        ],
        initial=["x"],
    )

    assert graph.validate_integrity() is True
    analysis = analyze_availability(graph)
    assert analysis.back_edges == frozenset({("C", "B")})
    assert analysis.entry_availability("B", "y_v1") == "some_paths"
    assert analysis.entry_availability("D", "x_v1") == "all_paths"


def test_entry_backedge_guarantees_nothing_on_the_first_invocation() -> None:
    graph = cfg(
        {"A": block("A", reads=["y_v1"]), "B": block("B", writes=["y_v1"])},
        [edge("A", "B"), edge("B", "A")],
    )

    assert graph.validate_integrity() is True
    analysis = analyze_availability(graph)
    assert analysis.entry_block_ids == ("A",)
    assert analysis.guaranteed_results_on_entry["A"] == frozenset()
    assert analysis.entry_availability("A", "y_v1") == "some_paths"


def test_rootless_cycle_rejected_but_independent_root_is_valid() -> None:
    graph = cfg(
        {"A": block("A", terminator="return"), "B": block("B"), "C": block("C")},
        [edge("B", "C"), edge("C", "B")],
    )
    with pytest.raises(ValueError, match="unreachable from any entry root"):
        graph.validate_integrity()
    independent = cfg(
        {
            "A": block("A", terminator="return"),
            "B": source("B"),
            "C": block("C", reads=["x_v1"], terminator="return"),
        },
        [edge("B", "C")],
        initial=["x"],
    )
    assert independent.validate_integrity()


def test_guard_dependencies_must_be_explicit_dispatch_inputs() -> None:
    empty_dispatch = BasicBlock(
        block_id="A",
        block_name="missing condition",
        instructions=[IRInstruction(id="ir_a", opcode="dispatch")],
    )
    with pytest.raises(ValueError, match="condition dependencies in inputs"):
        cfg(
            {"A": empty_dispatch, "B": block("B", terminator="return")},
            [
                CFGEdge(
                    source_block_id="A",
                    target_block_id="B",
                    condition_text="opaque condition",
                )
            ],
        )
