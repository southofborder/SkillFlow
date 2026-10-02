"""Optional result availability analysis, independent of first-stage validation.

This module computes possible/guaranteed result sets and graph relationships.
It is not invoked by compilation or rendering, does not classify opcodes, and
is not the future effect-aware data propagation or auditing stage.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..ir.basic_block import BasicBlock
from ..ir.operand import OperandType

if TYPE_CHECKING:  # pragma: no cover - import kept out of the runtime cycle
    from ..ir.cfg import ControlFlowGraph


def _max_block_evaluations(block_count: int, result_count: int) -> int:
    """Return a step cap that no converging graph can reach.

    Both transfer functions are monotone over a finite lattice, so the worklist
    always drains on its own.  The cap exists only so that a future change which
    breaks monotonicity fails loudly instead of hanging.
    """

    return 64 + 8 * (block_count + 1) * (result_count + 1)


@dataclass(frozen=True)
class ResultDefinition:
    """Which instruction produces a result."""

    result_id: str
    block_id: str
    instruction_id: str
    opcode: str
    semantic_name: str | None = None


@dataclass(frozen=True)
class ResultRead:
    """One result read, located by block, instruction, and input position."""

    result_id: str
    block_id: str
    instruction_id: str
    opcode: str
    input_index: int
    semantic_name: str | None = None


@dataclass(frozen=True)
class AvailabilityAnalysis:
    """Optional availability sets and graph relationships for one graph."""

    result_definitions: dict[str, ResultDefinition] = field(default_factory=dict)
    result_reads: tuple[ResultRead, ...] = ()
    predecessors: dict[str, tuple[str, ...]] = field(default_factory=dict)
    successors: dict[str, tuple[str, ...]] = field(default_factory=dict)
    entry_block_ids: tuple[str, ...] = ()
    reachable_block_ids: frozenset[str] = frozenset()
    #: Values that may be present on entry to / exit from each block.
    possible_results_on_entry: dict[str, frozenset[str]] = field(default_factory=dict)
    possible_results_on_exit: dict[str, frozenset[str]] = field(default_factory=dict)
    #: Values present on every path into / out of each block.
    guaranteed_results_on_entry: dict[str, frozenset[str]] = field(default_factory=dict)
    guaranteed_results_on_exit: dict[str, frozenset[str]] = field(default_factory=dict)
    #: Values that flow through a block untouched.  Derived, never declared.
    untouched_results: dict[str, frozenset[str]] = field(default_factory=dict)
    back_edges: frozenset[tuple[str, str]] = frozenset()
    dominators: dict[str, frozenset[str]] = field(default_factory=dict)
    #: Reads no path can satisfy.  No first-stage consumer depends on these optional findings.
    unavailable_reads: tuple[ResultRead, ...] = ()
    #: Reads satisfied on some but not all incoming paths.  Reported, never
    #: rejected: a merge that carries a value on one branch only is ordinary in
    #: prose, and refusing it would push the extractor towards omitting the read.
    path_dependent_reads: tuple[ResultRead, ...] = ()
    block_evaluation_count: int = 0

    def entry_availability(self, block_id: str, result_id: str) -> str:
        """Return ``"all_paths"``, ``"some_paths"``, or ``"no_paths"`` on entry to a block."""

        if result_id in self.guaranteed_results_on_entry.get(block_id, frozenset()):
            return "all_paths"
        if result_id in self.possible_results_on_entry.get(block_id, frozenset()):
            return "some_paths"
        return "no_paths"


def _graph_shape(
    graph: "ControlFlowGraph",
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Return predecessor and successor adjacency, ignoring dangling edges."""

    predecessors: dict[str, list[str]] = {block_id: [] for block_id in graph.blocks}
    successors: dict[str, list[str]] = {block_id: [] for block_id in graph.blocks}
    for edge in graph.edges:
        source = edge.source_block_id
        target = edge.target_block_id
        if source not in graph.blocks or target not in graph.blocks:
            continue
        # Parallel guarded edges between the same pair carry the same data, so
        # the adjacency is a set for propagation purposes.
        if target not in successors[source]:
            successors[source].append(target)
        if source not in predecessors[target]:
            predecessors[target].append(source)
    return predecessors, successors


def _entry_roots(
    graph: "ControlFlowGraph", predecessors: dict[str, list[str]]
) -> list[str]:
    """Return the blocks whose incoming state is empty.

    A block with no predecessor can only be entered from outside, and the
    declared entry is entered from outside on its first invocation even when a
    loop later points back at it.
    """

    entry_block_ids = [
        block_id for block_id, incoming in predecessors.items() if not incoming
    ]
    if (
        graph.entry_block_id in graph.blocks
        and graph.entry_block_id not in entry_block_ids
    ):
        entry_block_ids.append(graph.entry_block_id)
    return sorted(entry_block_ids)


def _reachable_from(
    entry_block_ids: list[str], successors: dict[str, list[str]]
) -> set[str]:
    """Return every block reachable_block_ids from any entry root."""

    reached: set[str] = set()
    pending = list(entry_block_ids)
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(
            target for target in successors.get(current, ()) if target not in reached
        )
    return reached


def _back_edges(
    entry_block_ids: list[str], successors: dict[str, list[str]]
) -> set[tuple[str, str]]:
    """Return the edges that close a cycle, found by an iterative DFS.

    An edge is a back edge when its target is still on the DFS stack, which is
    the standard criterion and the reason the search has to be depth-first
    rather than a plain reachability sweep.
    """

    found: set[tuple[str, str]] = set()
    finished: set[str] = set()
    on_stack: set[str] = set()

    for root in entry_block_ids:
        if root in finished:
            continue
        # Each frame keeps its own cursor into the successor list so the walk
        # can pause mid-block, which is what makes the stack meaningful.
        stack: list[tuple[str, int]] = [(root, 0)]
        on_stack.add(root)
        while stack:
            block_id, cursor = stack[-1]
            children = successors.get(block_id, ())
            if cursor >= len(children):
                stack.pop()
                on_stack.discard(block_id)
                finished.add(block_id)
                continue
            stack[-1] = (block_id, cursor + 1)
            child = children[cursor]
            if child in on_stack:
                found.add((block_id, child))
            elif child not in finished:
                stack.append((child, 0))
                on_stack.add(child)
    return found


def _dominators(
    entry_block_ids: list[str],
    predecessors: dict[str, list[str]],
    reachable_block_ids: set[str],
) -> dict[str, frozenset[str]]:
    """Return the dominator set of each reachable_block_ids block.

    Roots are dominated only by themselves; every other block is dominated by
    itself plus what all of its reachable_block_ids predecessors have in common.  With
    several entry_block_ids this is still well defined: a block reachable_block_ids from two
    independent entries simply shares fewer dominators.
    """

    root_set = set(entry_block_ids)
    order = [block_id for block_id in sorted(reachable_block_ids)]
    dominators: dict[str, set[str]] = {
        block_id: ({block_id} if block_id in root_set else set(order))
        for block_id in order
    }

    changed = True
    while changed:
        changed = False
        for block_id in order:
            if block_id in root_set:
                continue
            incoming = [
                predecessor
                for predecessor in predecessors.get(block_id, ())
                if predecessor in reachable_block_ids
            ]
            if not incoming:
                # Unreachable-from-root predecessors were filtered out; treat
                # the block as its own entry rather than inventing dominators.
                updated = {block_id}
            else:
                shared: set[str] | None = None
                for predecessor in incoming:
                    shared = (
                        set(dominators[predecessor])
                        if shared is None
                        else shared & dominators[predecessor]
                    )
                updated = (shared or set()) | {block_id}
            if updated != dominators[block_id]:
                dominators[block_id] = updated
                changed = True

    return {block_id: frozenset(values) for block_id, values in dominators.items()}


@dataclass(frozen=True)
class _BlockDataflowFacts:
    """The local dataflow facts of one block, read straight off its instructions."""

    defined: frozenset[str]
    used: frozenset[str]
    #: Values defined earlier in the same block, keyed by instruction id.  A use
    #: covered here needs no path argument at all: the definition precedes it in
    #: straight-line code, so no branch can skip it.
    defined_before: dict[str, frozenset[str]]


def _block_facts(block: BasicBlock) -> _BlockDataflowFacts:
    """Return what a single block defines and reads, in instruction order."""

    defined: list[str] = []
    used: set[str] = set()
    defined_before: dict[str, frozenset[str]] = {}
    seen: set[str] = set()

    for instruction in block.instructions:
        defined_before[instruction.id] = frozenset(seen)
        for operand in instruction.inputs:
            if operand.type is OperandType.RESULT and operand.identifier is not None:
                used.add(operand.identifier)
        for operand in instruction.outputs:
            if operand.type is OperandType.RESULT and operand.identifier is not None:
                if operand.identifier not in seen:
                    seen.add(operand.identifier)
                    defined.append(operand.identifier)

    return _BlockDataflowFacts(
        defined=frozenset(defined),
        used=frozenset(used),
        defined_before=defined_before,
    )


def _collect_values(
    graph: "ControlFlowGraph",
) -> tuple[
    dict[str, ResultDefinition], list[ResultRead], dict[str, _BlockDataflowFacts]
]:
    """Return every definition, every use, and the per-block local facts.

    Value names are unique across the whole graph, so a identifier colliding between
    two blocks is a structural defect rather than a redefinition; the first
    definition wins here and the structural checks report the collision.
    """

    result_definitions: dict[str, ResultDefinition] = {}
    result_reads: list[ResultRead] = []
    facts: dict[str, _BlockDataflowFacts] = {}

    for block_id, block in graph.blocks.items():
        facts[block_id] = _block_facts(block)
        for instruction in block.instructions:
            for index, operand in enumerate(instruction.inputs):
                if (
                    operand.type is OperandType.RESULT
                    and operand.identifier is not None
                ):
                    result_reads.append(
                        ResultRead(
                            result_id=operand.identifier,
                            block_id=block_id,
                            instruction_id=instruction.id,
                            opcode=instruction.opcode,
                            input_index=index,
                            semantic_name=operand.semantic_name,
                        )
                    )
            for operand in instruction.outputs:
                if (
                    operand.type is OperandType.RESULT
                    and operand.identifier is not None
                ):
                    result_definitions.setdefault(
                        operand.identifier,
                        ResultDefinition(
                            result_id=operand.identifier,
                            block_id=block_id,
                            instruction_id=instruction.id,
                            opcode=instruction.opcode,
                            semantic_name=operand.semantic_name,
                        ),
                    )

    return result_definitions, result_reads, facts


def _compute_availability(
    entry_block_ids: list[str],
    reachable_block_ids: set[str],
    predecessors: dict[str, list[str]],
    successors: dict[str, list[str]],
    facts: dict[str, _BlockDataflowFacts],
    all_result_ids: frozenset[str],
) -> tuple[
    dict[str, frozenset[str]],
    dict[str, frozenset[str]],
    dict[str, frozenset[str]],
    dict[str, frozenset[str]],
    int,
]:
    """Compute possible and guaranteed result sets until neither changes.

    Results are single-assignment and globally named, so nothing is ever killed
    and both transfer functions reduce to adding what the block defines.  The
    two lattices move in opposite directions -- ``avail`` starts empty and grows,
    ``must`` starts full and shrinks -- which is why ``must`` has to be seeded
    with all result IDs rather than with an empty set.
    """

    root_set = set(entry_block_ids)
    possible_results_on_entry = {
        block_id: frozenset[str]() for block_id in reachable_block_ids
    }
    possible_results_on_exit = {
        block_id: frozenset[str]() for block_id in reachable_block_ids
    }
    guaranteed_results_on_entry = {
        block_id: (frozenset[str]() if block_id in root_set else all_result_ids)
        for block_id in reachable_block_ids
    }
    guaranteed_results_on_exit = {
        block_id: (facts[block_id].defined if block_id in root_set else all_result_ids)
        for block_id in reachable_block_ids
    }

    budget = _max_block_evaluations(len(reachable_block_ids), len(all_result_ids))
    pending = deque(sorted(reachable_block_ids))
    queued = set(pending)
    block_evaluation_count = 0

    while pending:
        block_evaluation_count += 1
        if (
            block_evaluation_count > budget
        ):  # pragma: no cover - guards against non-monotonicity
            raise RuntimeError(
                "optional availability analysis did not converge after "
                f"{budget} steps over {len(reachable_block_ids)} blocks"
            )
        block_id = pending.popleft()
        queued.discard(block_id)

        incoming = [
            predecessor
            for predecessor in predecessors.get(block_id, ())
            if predecessor in reachable_block_ids
        ]
        new_avail_in = (
            frozenset[str]().union(*(possible_results_on_exit[p] for p in incoming))
            if incoming
            else frozenset[str]()
        )
        if block_id in root_set or not incoming:
            # An entry block is reached from outside on its first invocation, so
            # nothing is guaranteed on the way in even when a loop edge returns
            # to it later.  ``avail`` above still counts that loop edge.
            new_must_in = frozenset[str]()
        else:
            new_must_in = frozenset[str].intersection(
                *(guaranteed_results_on_exit[p] for p in incoming)
            )

        defined = facts[block_id].defined
        new_avail_out = new_avail_in | defined
        new_must_out = new_must_in | defined

        possible_results_on_entry[block_id] = new_avail_in
        guaranteed_results_on_entry[block_id] = new_must_in
        if (
            new_avail_out == possible_results_on_exit[block_id]
            and new_must_out == guaranteed_results_on_exit[block_id]
        ):
            continue
        possible_results_on_exit[block_id] = new_avail_out
        guaranteed_results_on_exit[block_id] = new_must_out
        for target in successors.get(block_id, ()):
            if target in reachable_block_ids and target not in queued:
                pending.append(target)
                queued.add(target)

    return (
        possible_results_on_entry,
        possible_results_on_exit,
        guaranteed_results_on_entry,
        guaranteed_results_on_exit,
        block_evaluation_count,
    )


def _passthrough(
    possible_results_on_entry: dict[str, frozenset[str]],
    facts: dict[str, _BlockDataflowFacts],
) -> dict[str, frozenset[str]]:
    """Return, per block, the values that arrive and leave without being touched.

    This is the derived form of what used to be declared as a relay list: a
    value the block neither defines nor reads, yet which is still available to
    its successors.  Nothing has to carry it deliberately, so nothing has to
    say that it does.
    """

    return {
        block_id: incoming - (facts[block_id].defined | facts[block_id].used)
        for block_id, incoming in possible_results_on_entry.items()
    }


def _read_availability(
    use: ResultRead,
    facts: dict[str, _BlockDataflowFacts],
    possible_results_on_entry: dict[str, frozenset[str]],
    guaranteed_results_on_entry: dict[str, frozenset[str]],
) -> str:
    """Return how certainly the value read by ``use`` is present at that point.

    The block-local case is checked first and separately.  A value defined
    earlier in the same block needs no path argument -- straight-line code cannot
    branch around it -- and it deliberately does not appear in ``possible_results_on_entry``,
    which describes only what crosses the block boundary.
    """

    local = facts[use.block_id].defined_before.get(use.instruction_id, frozenset())
    if use.result_id in local:
        return "all_paths"
    if use.result_id in guaranteed_results_on_entry.get(use.block_id, frozenset()):
        return "all_paths"
    if use.result_id in possible_results_on_entry.get(use.block_id, frozenset()):
        return "some_paths"
    return "no_paths"


def analyze_availability(graph: "ControlFlowGraph") -> AvailabilityAnalysis:
    """Compute optional result availability across a whole control-flow graph.

    The result is a description, not a verdict.  Uses that no path can satisfy
    are collected in ``unavailable_reads`` for the CFG layer to turn into errors,
    and result_reads satisfied on only some paths are collected in ``path_dependent_reads`` to
    be reported as they are.
    """

    predecessors, successors = _graph_shape(graph)
    entry_block_ids = _entry_roots(graph, predecessors)
    reachable_block_ids = _reachable_from(entry_block_ids, successors)
    result_definitions, result_reads, facts = _collect_values(graph)

    all_result_ids = frozenset(result_definitions)
    (
        possible_results_on_entry,
        possible_results_on_exit,
        guaranteed_results_on_entry,
        guaranteed_results_on_exit,
        block_evaluation_count,
    ) = _compute_availability(
        entry_block_ids=entry_block_ids,
        reachable_block_ids=reachable_block_ids,
        predecessors=predecessors,
        successors=successors,
        facts=facts,
        all_result_ids=all_result_ids,
    )

    unresolved: list[ResultRead] = []
    may_only: list[ResultRead] = []
    for use in result_reads:
        if use.block_id not in reachable_block_ids:
            # An unreachable block has no path to reason about; the structural
            # checks already report the block itself.
            continue
        entry_availability = _read_availability(
            use, facts, possible_results_on_entry, guaranteed_results_on_entry
        )
        if entry_availability == "no_paths":
            unresolved.append(use)
            continue
        if entry_availability == "some_paths":
            may_only.append(use)
    return AvailabilityAnalysis(
        result_definitions=result_definitions,
        result_reads=tuple(result_reads),
        predecessors={
            block_id: tuple(sorted(incoming))
            for block_id, incoming in predecessors.items()
        },
        successors={
            block_id: tuple(sorted(outgoing))
            for block_id, outgoing in successors.items()
        },
        entry_block_ids=tuple(entry_block_ids),
        reachable_block_ids=frozenset(reachable_block_ids),
        possible_results_on_entry=possible_results_on_entry,
        possible_results_on_exit=possible_results_on_exit,
        guaranteed_results_on_entry=guaranteed_results_on_entry,
        guaranteed_results_on_exit=guaranteed_results_on_exit,
        untouched_results=_passthrough(possible_results_on_entry, facts),
        back_edges=frozenset(_back_edges(entry_block_ids, successors)),
        dominators=_dominators(entry_block_ids, predecessors, reachable_block_ids),
        unavailable_reads=tuple(unresolved),
        path_dependent_reads=tuple(may_only),
        block_evaluation_count=block_evaluation_count,
    )
