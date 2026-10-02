"""Independent tests for optional availability analysis.

Compilation and integrity checks never invoke this module. These graph shapes
exercise its possible/guaranteed result sets, loops, dominance, and purity.
"""

from skill_ir import BasicBlock, CFGEdge, ControlFlowGraph, IRInstruction, Operand
from skill_ir.analysis.availability import analyze_availability


def make_result(identifier: str, semantic_name: str | None = None) -> Operand:
    return Operand(type="result", identifier=identifier, semantic_name=semantic_name)


def block(
    block_id: str,
    *,
    reads: list[str] | None = None,
    writes: list[str] | None = None,
    opcode: str = "assign",
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
        block_id=block_id, block_name=f"语义块 {block_id}", instructions=sequence
    )


def source(
    block_id: str = "A", key: str = "ctx.request", produces: str = "req_v1"
) -> BasicBlock:
    """A context source whose terminator names what it just read."""

    return BasicBlock(
        block_id=block_id,
        block_name=f"读取 {key}",
        data_source_kind="context",
        instructions=[
            IRInstruction(
                id=f"ir_{block_id}_read",
                opcode="read_context",
                inputs=[Operand(type="context_key", identifier=key)],
                outputs=[make_result(produces, "request")],
            ),
            IRInstruction(
                id=f"ir_{block_id}_end",
                opcode="dispatch",
                inputs=[make_result(produces, "request")],
            ),
        ],
    )


def graph(
    blocks: list[BasicBlock],
    edges: list[tuple[str, str]] | list[tuple[str, str, str]],
    *,
    entry: str = "A",
    initial: list[str] | None = None,
) -> ControlFlowGraph:
    return ControlFlowGraph(
        entry_block_id=entry,
        blocks={item.block_id: item for item in blocks},
        edges=[
            CFGEdge(
                source_block_id=item[0],
                target_block_id=item[1],
                condition_text=item[2] if len(item) > 2 else None,
            )
            for item in edges
        ],
        declared_context_keys=initial if initial is not None else ["ctx.request"],
    )


def test_straight_line_accumulates_and_derives_passthrough() -> None:
    analysis = analyze_availability(
        graph(
            [source(), block("B"), block("C", reads=["req_v1"], terminator="return")],
            [("A", "B"), ("B", "C")],
        )
    )

    assert analysis.entry_block_ids == ("A",)
    assert analysis.reachable_block_ids == frozenset({"A", "B", "C"})
    assert analysis.predecessors == {"A": (), "B": ("A",), "C": ("B",)}
    assert analysis.possible_results_on_entry == {
        "A": frozenset(),
        "B": frozenset({"req_v1"}),
        "C": frozenset({"req_v1"}),
    }
    assert analysis.possible_results_on_exit["A"] == frozenset({"req_v1"})
    # With no branch anywhere, "could be here" and "is always here" coincide
    # everywhere except the entry, which is entered from outside.
    assert analysis.guaranteed_results_on_entry == analysis.possible_results_on_entry
    # B never mentions the value; that it survives B is derived, not declared.
    assert analysis.untouched_results == {
        "A": frozenset(),
        "B": frozenset({"req_v1"}),
        "C": frozenset(),
    }
    assert analysis.dominators["C"] == frozenset({"A", "B", "C"})
    assert analysis.back_edges == frozenset()
    assert analysis.unavailable_reads == ()
    assert analysis.path_dependent_reads == ()


def test_a_value_defined_earlier_in_the_same_block_never_crosses_a_boundary() -> None:
    """Straight-line code cannot branch around its own definition."""

    only = BasicBlock(
        block_id="A",
        block_name="独块",
        instructions=[
            IRInstruction(
                id="ir_A_make", opcode="assign", outputs=[make_result("draft_v1")]
            ),
            IRInstruction(
                id="ir_A_send",
                opcode="call_llm",
                inputs=[make_result("draft_v1")],
                outputs=[make_result("reply_v1")],
            ),
            IRInstruction(
                id="ir_A_end", opcode="return", inputs=[make_result("reply_v1")]
            ),
        ],
    )

    analysis = analyze_availability(graph([only], [], initial=[]))

    assert analysis.unavailable_reads == ()
    # ``avail_in`` describes what crosses the block boundary, and nothing does.
    assert analysis.possible_results_on_entry["A"] == frozenset()
    assert analysis.untouched_results["A"] == frozenset()
    assert analysis.entry_availability("A", "draft_v1") == "no_paths"
    assert analysis.path_dependent_reads == ()


def test_branch_merge_keeps_the_common_value_must_and_the_one_sided_value_may() -> None:
    analysis = analyze_availability(
        graph(
            [
                source(),
                block("B", writes=["sun_v1"]),
                block("C"),
                block("E", reads=["req_v1", "sun_v1"], terminator="return"),
            ],
            [("A", "B", "晴天"), ("A", "C", "雨天"), ("B", "E"), ("C", "E")],
        )
    )

    assert analysis.possible_results_on_entry["E"] == frozenset({"req_v1", "sun_v1"})
    assert analysis.guaranteed_results_on_entry["E"] == frozenset({"req_v1"})
    assert analysis.entry_availability("E", "req_v1") == "all_paths"
    assert analysis.entry_availability("E", "sun_v1") == "some_paths"
    # Reported, not rejected: a merge reading a one-branch value is ordinary.
    assert [(use.block_id, use.result_id) for use in analysis.path_dependent_reads] == [
        ("E", "sun_v1")
    ]
    assert analysis.unavailable_reads == ()
    assert analysis.dominators["E"] == frozenset({"A", "E"})
    assert analysis.untouched_results["B"] == frozenset({"req_v1"})
    assert analysis.untouched_results["C"] == frozenset({"req_v1"})


def test_sibling_branches_never_reach_each_other() -> None:
    analysis = analyze_availability(
        graph(
            [
                source(),
                block("B", writes=["sun_v1"], terminator="return"),
                block("C", reads=["sun_v1"], terminator="return"),
            ],
            [("A", "B", "晴天"), ("A", "C", "雨天")],
        )
    )

    assert analysis.entry_availability("C", "sun_v1") == "no_paths"
    assert [(use.block_id, use.result_id) for use in analysis.unavailable_reads] == [
        ("C", "sun_v1")
    ]
    # The definition exists; what is missing is a path, so the pass still hands
    # the CFG layer the definition point to identifier in its message.
    assert analysis.result_definitions["sun_v1"].block_id == "B"


def test_a_loop_carries_values_backwards_but_not_into_the_first_pass() -> None:
    analysis = analyze_availability(
        graph(
            [
                source(),
                block("H", reads=["acc_v1"]),
                block("BODY", writes=["acc_v1"]),
                block("EXIT", reads=["req_v1"], terminator="return"),
            ],
            [("A", "H"), ("H", "BODY", "继续"), ("H", "EXIT", "结束"), ("BODY", "H")],
        )
    )

    assert analysis.back_edges == frozenset({("BODY", "H")})
    assert analysis.entry_availability("H", "acc_v1") == "some_paths"
    assert analysis.entry_availability("EXIT", "req_v1") == "all_paths"
    assert analysis.guaranteed_results_on_entry["H"] == frozenset({"req_v1"})
    assert analysis.possible_results_on_entry["H"] == frozenset({"req_v1", "acc_v1"})
    assert analysis.dominators["EXIT"] == frozenset({"A", "H", "EXIT"})
    assert analysis.dominators["BODY"] == frozenset({"A", "H", "BODY"})
    assert analysis.unavailable_reads == ()


def test_nested_loops_converge_and_carry_the_inner_value_out() -> None:
    """The outer header can only see the inner value through the outer backedge."""

    analysis = analyze_availability(
        graph(
            [
                source(),
                block("H1", reads=["inner_v1"]),
                block("H2", reads=["req_v1"]),
                block("BODY", writes=["inner_v1"]),
                block("LATCH", writes=["outer_v1"]),
                block("EXIT", reads=["req_v1"], terminator="return"),
            ],
            [
                ("A", "H1"),
                ("H1", "H2", "外层继续"),
                ("H1", "EXIT", "外层结束"),
                ("H2", "BODY", "内层继续"),
                ("H2", "LATCH", "内层结束"),
                ("BODY", "H2"),
                ("LATCH", "H1"),
            ],
        )
    )

    assert analysis.back_edges == frozenset({("BODY", "H2"), ("LATCH", "H1")})
    assert analysis.possible_results_on_entry["H1"] == frozenset(
        {"req_v1", "inner_v1", "outer_v1"}
    )
    assert analysis.guaranteed_results_on_entry["H1"] == frozenset({"req_v1"})
    assert analysis.entry_availability("H1", "inner_v1") == "some_paths"
    assert analysis.entry_availability("H2", "req_v1") == "all_paths"
    assert analysis.guaranteed_results_on_entry["H2"] == frozenset({"req_v1"})
    assert analysis.dominators["BODY"] == frozenset({"A", "H1", "H2", "BODY"})
    assert analysis.dominators["EXIT"] == frozenset({"A", "H1", "EXIT"})
    assert analysis.unavailable_reads == ()
    assert [(use.block_id, use.result_id) for use in analysis.path_dependent_reads] == [
        ("H1", "inner_v1")
    ]


def test_two_independent_entries_share_only_what_both_establish() -> None:
    """A block reachable from two entries is dominated by neither alone."""

    analysis = analyze_availability(
        graph(
            [
                source(),
                source("S", "ctx.retry", "retry_v1"),
                block("M", reads=["req_v1"], terminator="return"),
            ],
            [("A", "M"), ("S", "M")],
            initial=["ctx.request", "ctx.retry"],
        )
    )

    assert analysis.entry_block_ids == ("A", "S")
    assert analysis.possible_results_on_entry["M"] == frozenset({"req_v1", "retry_v1"})
    assert analysis.guaranteed_results_on_entry["M"] == frozenset()
    assert analysis.dominators["M"] == frozenset({"M"})
    # Entering through S means arriving without ``req_v1``, so the read is a
    # may-only read even though nothing about M changed.
    assert analysis.entry_availability("M", "req_v1") == "some_paths"


def test_unreachable_blocks_are_skipped_rather_than_reported() -> None:
    """A rootless cycle has no invocation to reason about."""

    analysis = analyze_availability(
        graph(
            [
                block("A", terminator="return"),
                block("B", reads=["ghost_v1"]),
                block("C"),
            ],
            [("B", "C"), ("C", "B")],
            initial=[],
        )
    )

    assert analysis.reachable_block_ids == frozenset({"A"})
    assert "B" not in analysis.possible_results_on_entry
    # The structural checks report the block; the read inside it is not a second
    # finding about the same defect.
    assert analysis.unavailable_reads == ()


def test_dangling_edges_are_ignored_instead_of_raising() -> None:
    valid = graph(
        [source(), block("B", reads=["req_v1"], terminator="return")], [("A", "B")]
    )
    broken = ControlFlowGraph.model_construct(
        entry_block_id="A",
        blocks=valid.blocks,
        edges=[*valid.edges, CFGEdge(source_block_id="B", target_block_id="missing")],
        declared_context_keys=valid.declared_context_keys,
    )

    analysis = analyze_availability(broken)

    assert analysis.successors["B"] == ()
    assert analysis.reachable_block_ids == frozenset({"A", "B"})
    assert analysis.entry_availability("B", "req_v1") == "all_paths"


def test_parallel_guarded_edges_are_one_edge_for_dataflow() -> None:
    analysis = analyze_availability(
        graph(
            [source(), block("B", reads=["req_v1"], terminator="return")],
            [("A", "B", "x == 1"), ("A", "B", "x == 2")],
        )
    )

    assert analysis.predecessors["B"] == ("A",)
    assert analysis.successors["A"] == ("B",)
    assert analysis.entry_availability("B", "req_v1") == "all_paths"


def test_availability_analysis_is_a_pure_function_of_the_graph() -> None:
    subject = graph(
        [
            source(),
            block("H", reads=["acc_v1"]),
            block("BODY", writes=["acc_v1"]),
            block("EXIT", reads=["req_v1"], terminator="return"),
        ],
        [("A", "H"), ("H", "BODY", "继续"), ("H", "EXIT", "结束"), ("BODY", "H")],
    )

    first = analyze_availability(subject)
    second = analyze_availability(subject)

    assert first == second
    assert first.block_evaluation_count == second.block_evaluation_count
