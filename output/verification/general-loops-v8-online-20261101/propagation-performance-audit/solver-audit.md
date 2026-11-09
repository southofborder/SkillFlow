# Read-only GA4 v8 propagation cost audit

Scope: the frozen `solver.py`, `interpreter.py` and `runner.py` under `experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/implementation-snapshot/src/skillflow/propagation/`, plus the selected CFG and compiled annotation metadata. No solver, compilation, replay, debugger, target request or Skill execution was started. No running process or production file was changed.

## What can and cannot be concluded

The frozen code contains a concrete scalability risk: **any registry revision change requeues every already evaluated block**, rather than just the consumers of the changed fact. This can cause substantial repeated work across a large graph. It is an implementation risk directly visible in code, not an observed stack hotspot. The existing stage-level files do not distinguish pre-solver verification, worklist computation, result sealing or final validation. CPU activity alone does not identify which is consuming the time.

The current candidate is not expensive because it requests partial-order permutations: **all 372 modeled IRs declare fixed order**. Nor does the code execute GA4 or repeatedly ask the model while propagating. It is deterministic local analysis.

## Selected candidate size

Counts read directly from `graph/selected.json` and `revision/annotation/audit/compiled-response.json`:

| Item | Count |
|---|---:|
| Blocks / CFG edges / total IR | 194 / 285 / 420 |
| Modeled IR / fixed-order IR | 372 / 372 |
| Compiled events / case groups | 379 / 18 |
| Merge / member / branch / append operations | 23 / 5 / 30 / 12 |
| Compact `for_each` events | 0 |
| Largest individual IR operation counts | 29 each in `ir_169` and `ir_287` |

These counts are input size, not processed coverage or measured iteration counts. The 48 explicitly unmodeled IRs stop their affected block when reached; they do not establish that only 48 instructions are affected downstream.

## Worklist and convergence

References below are one-based lines in the archived files, not the live implementation.

1. `solver.py:462–559` runs a FIFO worklist. Each block is interpreted for its incoming environments; a changed outgoing edge schedules successors (`541–548`). If `registry.revision` changed during that block, **all blocks in `evaluated` are also scheduled** (`554–559`). Deduplicating the queue prevents simultaneous duplicate entries, but does not avoid repeated reevaluation across passes.
2. Blocks in a loop, or containing a merge, retain separate predecessor environments (`467–477`), and the entire block is evaluated for each environment (`487–524`). This preserves correlation but costs more than one transfer per block. Other multi-predecessor blocks join inputs, which can still leave sets of candidate values for later operations.
3. Every block reevaluation reconstructs records and diagnostics (`478–486`); state alternatives are sorted and deduplicated using the whole location/value-set signature (`541–545`). IR record merges also combine and hash operation alternatives (`44–64`). Thus repeated passes do more than compare a small counter.
4. The worklist terminates when the queue empties. There is **no explicit maximum total block-evaluation count or wall-clock deadline** in this loop. `block_evaluations` is collected as a result statistic (`553`) rather than used as a stop threshold. This observation does not establish nontermination; it means the local relation limits are not a practical elapsed-time bound.
5. Before the worklist, the solver computes dominators to a fixed point and derives loop regions (`424–453`). After it, it seals loop summaries, constructs records and validates the complete record set (`577–601`). None has a separate stage-progress publication here.

## Candidate products and resource guards

The default `max_variants` is 100,000 (`solver.py:376`, `interpreter.py:77`). The runner invokes propagation without overriding it (`runner.py:51–54`). It is used in several local checks:

- Ordinary operand tuples use a Cartesian product of candidate sets; the size is checked before enumeration (`interpreter.py:232–254`). Correlation checks reject incompatible tuples, but do not make the initial product free.
- Conditional object construction enumerates condition choices and selected value tuples, with checks on condition-product and total build variants (`325–384`). Many independent uncertain optional fields can be costly despite fixed execution order.
- Ambient member contexts combine compatible bindings and hash/deduplicate them (`256–286`). Typed guard routing scans state and candidate bindings, then deduplicates routes (`solver.py:67–117`). Incoming edge-state alternatives have another local 100,000 limit (`541–544`).
- Partial-order arrangement attempts have a limit (`interpreter.py:687–690`), reset for each IR evaluation (`779–794`). The current candidate has fixed order, so schedule-permutation explosion is not supported by its metadata; fixed execution still traverses its operations and their value alternatives.
- When loop operations are present, the solver installs `LoopFactRegistry` and assigns its `max_facts` the same budget (`solver.py:408–413`). This note does not inspect that class's internal counting or claim a total allocation/time bound from this assignment.

These safeguards prevent some oversized local relations; they do **not** bound the sum of many sub-limit operations repeated across environments and worklist passes. Hitting `PropagationLimitError` yields `resource_limit`, rather than successful truncation (`solver.py:571–573`). No such result has been observed in the artifacts inspected for this note.

## Verification and publication can also consume the stage

`runner.py:166–178` first calls `verify_prepared(origin, replay=True)`, reloads the annotation, then calculates. Inside `propagate`, CFG integrity, annotation typing, transfer-spec validation, annotation consistency, payload hashing and initial record construction precede the worklist (`solver.py:386–419`). This establishes that checks occur before solving; their individual cost has not been measured here.

After calculation, `save_propagation_run` reloads annotation material, builds components, calculates component hashes, writes artifacts, checks the annotation again and verifies saved hashes before committing the manifest (`runner.py:103–159,179–183`). A missing propagation directory is consistent with work still occurring before the save begins. It does not prove that the worklist itself is stalled or progressing.

## Practical interpretation

The leading code-level suspect is broad invalidation combined with repeated environment/value-alternative processing. A larger IR count increases the work affected by that policy. The evidence does **not** yet isolate a measured bottleneck, demonstrate exponential behavior in this run, or show failure to converge. With no per-pass statistics or current stack samples, the honest current statement is: the process may be actively computing, but its stage metadata cannot reveal completed coverage, remaining passes or the exact hot function. This audit changes nothing while the authorized run continues.
