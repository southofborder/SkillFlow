# Static loop/performance audit of selected GA4 v8 candidate

**The present evidence does not support blaming loop fixed-point iteration for the observed delay.** All five explicit cyclic SCCs are behind preserved unmodeled cutoffs. This is a static diagnosis, not a runtime profile or propagation result.

| Structural measure | Count |
|---|---:|
| Blocks / edges / IR | 194 / 285 / 420 |
| SCCs / cyclic SCCs | 177 / 5 |
| Blocks / IR in cycles | 22 / 52 |
| Natural regions / strict nesting pairs | 5 / 0 |
| Source-unmodeled IR | 48 |
| Blocks reached by cutoff-only static traversal | 22 |
| Modeled prefix IR / atomic operations upper bound | 29 / 29 |
| Cyclic blocks reached before cutoffs | 0 |

The two solver roots are block_001 and block_029. The first cutoffs are `ir_019`, `ir_035`, `ir_039`, `ir_053`, `ir_419`. This traversal ignores typed guard pruning and pending data, so29is an upper bound, not measured successful propagation. It intentionally does not execute the solver.

| Cyclic component | Blocks | IR | Reached before cutoff |
|---|---:|---:|---:|
| normalize_header | 4 | 10 | 0 |
| list_filter_header | 4 | 9 | 0 |
| list_map_header | 2 | 6 | 0 |
| url_loop_header | 8 | 18 | 0 |
| latest_filter_header | 4 | 9 | 0 |

The reachable prefix has one typed `branch` and no `merge`, `member` or `append`. There are zero compiled `for_each` events in the whole selected annotation. Five static member sites occur in the explicit cyclic CFG regions.

## F1: Current explicit loops are behind preserved unmodeled cutoffs

**Evidence level:** proven static property; actual completed coverage remains unknown.

Ignoring typed guard pruning and data-resolution failures, a graph walk from the two solver roots that stops at the first unmodeled IR can reach only22blocks and29modeled prefixIR. No block of any cyclic SCC is reached. Therefore iterative execution of these five loop SCCs is not established as the current delay cause. This is an upper bound for admissible prefix work, not a reported propagation result.

- [solver.py:158](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/solver.py:158): All predecessor-free blocks plus declared entry are solver roots.
- [solver.py:498](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/solver.py:498): The first unmodeled instruction stops its block; no complete OUT is published.

## F2: Loop-aware registry activates globally, even when every cycle is cut off

**Evidence level:** proven code behavior; runtime share not measured.

Loop scope detection uses graph reachability before gap cutoffs. It also activates on any merge/member/branch/append declaration. This run therefore selects LoopFactRegistry even though the prefix contains only one branch and no merge/member/append. Costs of its ordinary record path can still apply outside loops.

- [solver.py:402](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/solver.py:402): Registry selection precedes per-block unmodeled cutoffs.

## F3: Finite identity safeguards are present; unbounded per-iteration IDs are not demonstrated

**Evidence level:** code evidence, not a whole-domain termination proof.

Family identity uses static scope/producer/bindings rather than the full input Data chain. Loop-summary-as-content is reduced to an opaque relation instead of nested embedding. Member identities use a static scope and family producer/selector; carried bindings use incoming/unresolved markers. The code therefore has real mechanisms against recursive ID growth. These do not imply small finite state space or prove every interacting path bounded.

- [loop_domain.py:153](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/loop_domain.py:153): Family key, variant key and summary-content guard.
- [loop_domain.py:88](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/loop_domain.py:88): Carried relation state retains finite incoming/unresolved markers.
- [interpreter.py:447](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/interpreter.py:447): Member scope and selector pairing derive from static sites/producer.

## F4: Relation-variant growth can be expensive without identity divergence

**Evidence level:** potential general risk; not demonstrated for this run.

Each new variant hashes concrete inputs/content/dependencies and scans all families to count facts; max_facts uses the100000default. Stable family IDs still permit many input/shape/binding alternatives. A new fact globally requeues all evaluated blocks, not only consumers, and there is no independent block-evaluation/time bound in this loop. Current cutoffs prevent the declared SCC iterations, so this is not evidence of present variant expansion.

- [loop_domain.py:153](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/loop_domain.py:153): Variant storage/hash/counting and fact_revision.
- [solver.py:375](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/solver.py:375): Default max_variants100000.
- [solver.py:553](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/solver.py:553): Any registry revision reschedules all evaluated blocks.

## F5: Repeated summary shape walks can duplicate finite work

**Evidence level:** potential general risk; no measured active stack.

content_options recursively expands every variant into a list; _select can traverse repeated relation paths. Seen identities stop cycles but there is no memoization/deduplication of equivalent shape options. Guards and projections invoke this work repeatedly. A shared finite DAG with many alternatives can therefore incur large repeated traversal despite finite identities. Current reachable-prefix branch has no loop input, so actual applicability to this run is unproven.

- [summary.py:9](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/data/summary.py:9): Cycle guard and variant list expansion.
- [summary.py:25](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/data/summary.py:25): Recursive shape selection through relations.
- [loop_guards.py:5](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/loop_guards.py:5): Guard asks for all content_options.
- [loop_domain.py:190](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/loop_domain.py:190): Projection and iteration query shapes repeatedly.

## F6: Whole-registry validation and detached copies are available non-loop cost amplifiers

**Evidence level:** proven code path; contribution to delay unmeasured.

LoopFactRegistry._commit reconstructs every current loop fact and validates the whole registry for an ordinary update. DataRegistry._register calls _commit even for re-registration, and get returns a deep detached copy. _entry rebuilds summary Data from all variants. Even without executed loop families, repeated ordinary registration validates the whole ordinary registry. This is a candidate for profiling, not a confirmed root cause.

- [loop_domain.py:122](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/loop_domain.py:122): All-entry materialization and full validation on commits.
- [registry.py:240](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/data/registry.py:240): Deep get and unconditional commit for registration.
- [registry.py:763](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/data/registry.py:763): Whole registry identity/reference/acyclicity validation.

No family counter, variant counter, actual block-evaluation count or total elapsed attribution was obtained. None is invented. The running controller and queue were not touched. Full structural counts, component membership and exact frozen artifact hashes are in [loop-audit.json](loop-audit.json).


## Parent-collected live samples distinguish the current layer

This auditor subsequently read the parent's existing nonblocking stack samples; it did not attach to the process. Both show `save_propagation_run:110 -> load_annotation_run -> load_annotation -> _assembled_values -> assemble_fragments -> validate_fragment:375`. Thus the calculation call has already returned before this save path, and the main thread was doing annotation reassembly/validation at the sampled instants, not loop worklist iteration. The saved calculation result is not yet evidence of complete propagation or useful DOE.

- [stack-sample-002.json](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/propagation-performance-audit/stack-sample-002.json), observed at `2026-11-01T16:15:59.273103+00:00`.
- [stack-sample-004.json](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/propagation-performance-audit/stack-sample-004.json), observed at `2026-11-01T16:16:01.538714+00:00`.

These point samples locate the current work; they do not attribute the whole preceding delay or prove nontermination. The static loop risks above remain general potential costs, not the measured hotspot for this run.
