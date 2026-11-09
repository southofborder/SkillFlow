# Independent solver review

Date: 2026-11-03. This review inspected source while the root-owned bounded baseline benchmark was running. No tests, propagation calculations, DOE calculations, paused-process reads, or benchmark controls were performed. Root subsequently authorized the small candidate edit and unrun counterexample tests described below. The running baseline imports its archived implementation and is unaffected by these workspace edits.

## Finding: internal withdrawal can retain unsupported cyclic rows

The original `replace_edge` condition in `src/skillflow/propagation/solver.py` around lines 537-541 scheduled component reconstruction only when a shrinking edge entered a different static strongly connected component. An internal gate can remove the only supported entry to a subcycle without changing the static component's external incoming edge. The old subcycle then keeps supplying its own rows, so its records and outgoing effects remain present.

A concrete source-derived counterexample extends `loop_with_external_entries` in `tests/propagation/test_partition_retraction.py` by adding `head -> left`. The existing edges include `left -> head`, `head -> body`, `body -> head`, and `body -> exit`; the added edge places `left`, `head`, and `body` in one static component while keeping the dispatch fanout at two. The existing test's captured prerequisite refinement then makes `gate_left` fail. `left -> head` is withdrawn internally, so the original condition skips reconstruction. The stale `head <-> body` rows still support each other even though every admitted seed-to-head route through `left` is now blocked.

The surviving-entry variant adds the existing independent `right -> head` route carrying `"surviving"`. Both loop blocks remain reachable through that row, while the withdrawn `"withdrawn"` row can still circulate on their old backedge. Therefore block reachability alone is insufficient: pruning only wholly unreachable blocks cannot remove the unsupported row when another row supports the same block.

## Candidate change authorized by root

The candidate reuses the existing finite component reconstruction. An actual removed relation-row key on an edge entering a cyclic component now schedules that component, including an internal edge. Pure row growth does not schedule reconstruction. A small `rebuilding` set suppresses recursive scheduling caused by clearing that same component's internal edges; withdrawal into a different component still propagates. Reconstruction retains external incoming relations and root seeds, detaches previous subscriptions/records/outgoing contributions, and leaves ordinary Data and family history intact.

This is limited to `replace_edge` and `rebuild_component` in `solver.py`; it introduces no generic provenance-retraction or cache framework. Four new cases in `test_partition_retraction.py` cover FIFO/LIFO and absent/surviving independent entry. Each has an assertion limit of 200 interpreter attempts so an unintended rebuild cycle fails promptly rather than hanging its test. They have been added but **not run** while the baseline benchmark is active.

Retained registry refinements preserve the cause of the illustrated withdrawal during reconstruction. That supports this correction for the concrete counterexample, but is not a proof that every possible internal row replacement converges after restart. Focused tests must confirm this candidate and the existing ordinary-growth/non-repeated-rebuild cases before the root freezes a revised current implementation or starts its sole full current benchmark.

## Other inspected paths

- Dependency notifications retain first-read versions, replace subscriptions after each attempt, and enqueue only changed-key readers whose version differs. Pending-value attempts retain the reads that can later unblock them. No additional concrete missed-notification defect was established by this inspection.
- Relation rows remain separate even when grouped under a common partition binding footprint. Merge-sensitive partitions retain predecessor identity; backedge status remains a distinct key. Empty projected rows remain reachable rows because the outer relation contains their empty tuple key.
- A partition's latest attempt replaces its records, failures and outgoing contribution. Missing-path diagnostics remain when another row succeeds at the same IR. Removing a partition detaches its subscriptions and removes its outcome before publication.
- Liveness retains explicit operands, future state reads, alias reads, write before/after evidence, implicit dominating-member controls and block-exit guard locations. Strong-write kills apply only to unconditional fixed-order exact targets; uses still retain the prior value needed by published change evidence. No additional concrete under-projection defect was established.

These are bounded source-review conclusions, not a replacement for the recorded offline acceptance or a semantic-equivalence claim. The new internal-withdrawal finding remains pending focused execution; the already completed test counts should not be relabelled as covering it.
