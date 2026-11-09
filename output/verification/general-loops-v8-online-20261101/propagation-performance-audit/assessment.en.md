# Passive diagnosis of GA4 v8 propagation-stage latency

The current measured hotspot is repeated annotation reconstruction and validation during result saving. Four successful nonblocking stack snapshots at 2026-11-01 16:15:59–16:16:52 UTC (2026-11-02 00:15:59–00:16:52 China time) all show `run_propagation:182 → save_propagation_run:110 → load_annotation → assemble_fragments → validate_fragment`. The `_calculate` call precedes that save invocation and had therefore already returned in these samples. This rules out an actively unfinished loop fixed point as the location of the sampled work. It does not prove that calculation returned a complete result; partial/failure coverage remains possible until committed artifacts are available.

## Measured evidence

The first two valid samples caught complete-processing deep copies and source/CFG evidence type validation. The later two caught sensitivity projection rebuilding the full processing backend and CFG/demand target index. None of the four was inside the solver worklist or a member/candidate transfer loop.

The controller is actively consuming approximately one CPU core, with resident memory around 200 MB and an observed peak working set about 284 MB. The observations do not show an ongoing large-memory explosion. Modest memory does not by itself rule out expensive combinatorial CPU work; the stack evidence provides the more specific attribution. Between the two saved process snapshots at 16:16:31 and 16:18:01 UTC, CPU time grew while file I/O counters remained unchanged, consistent with in-memory validation/index computation rather than waiting for model or disk output.

The stage label is broader than the core solver. `run_propagation` verifies/loads input before calculation, then `save_propagation_run` loads and reconstructs the annotation again before even creating its output directory. Additional consistency checks occur before the committed manifest. Thus an absent propagation directory does not imply the core calculation is still running.

## Concrete amplification in the frozen implementation

The selected annotation has 372 modeled IR and 57 sensitivity declarations. Thirteen declarations refer to case-bearing instructions. For each such declaration, `project_sensitivity` deep-copies and expands the entire processing fragment to locate one declaration's compiled target. Each expansion validates evidence, operations and expressions and builds the full target index.

| Static accepted-path work | Count |
|---|---:|
| Full processing expansions per successful assemble_fragments | 18 |
| Full expansions per load_annotation, including revalidation of fragment chains and dependencies | At least 37 |
| Full annotation loads on a normal propagation-and-save path | 5 |
| Conditional lower bound if that path completes normally | 185 full expansions |

These are code-derived path counts, not traced runtime invocation counts or a claim that all 185 have already happened. Revalidating rejected original answers and corrections can add work. The code is repeating expensive verification of the same accepted material; this cost is not inherently required by source loop semantics.

The CFG target-index builder walks 9,843 JSON positions. Of these, 7,514 use IR anchors, and resolving each anchor scans all 420 IR. One rebuilt index therefore entails 3,155,880 IR ID comparisons, before type checks, data copying and other index work. This exact index-building path appeared in live samples 005 and 006.

Relevant frozen locations:

- `implementation-snapshot/src/skillflow/document_guided/fragments.py:428–453`: per-declaration sensitivity validation/projection.
- `implementation-snapshot/src/skillflow/document_guided/annotation_wire.py:743–756`: copying and re-expanding the entire processing for one sensitivity projection.
- `implementation-snapshot/src/skillflow/document_guided/online.py:521–526,620–624`: reconstruction on annotation loading.
- `implementation-snapshot/src/skillflow/propagation/contracts/references.py:130–179`: repeated global IR lookup while building the target index.
- `implementation-snapshot/src/skillflow/propagation/runner.py:110,165–182`: save-time reload after calculation.

## What the loop and state checks do and do not show

Static inspection found 194 blocks, 285 edges and 420 IR, including five cyclic SCCs with 22 blocks/52 IR. A lightweight graph traversal that stops at the first explicitly unmodeled IR reaches none of those cyclic blocks. Its maximum modeled prefix is 29 IR; that is only a static upper bound, not measured coverage. The selected front-end cutoffs occur before the loops can receive their required input paths.

All 372 modeled specifications have fixed order. Factorial enumeration of partial-order schedules is consequently not an explanation for this candidate. There are still potential solver costs: candidate products, registry validation and whole-worklist requeue whenever registry revision changes. Finite loop families also do not guarantee small numbers of variants. These are documented implementation risks, but they are not what the successful samples caught, and the calculation had returned by those observations. The absence of a total worklist time/iteration cap should not be confused with evidence that this run is looping forever.

The audit cannot reconstruct how all earlier stage time was apportioned because no detailed timing instrumentation was present. It provides a direct current hotspot and static reasons why that hotspot is expensive. No replacement benchmark or candidate solve was run.

## Method and preservation

Only the authorized controller PID22512 was sampled, after checking its command line. An isolated py-spy0.4.2 executable was extracted from its official PyPI wheel, verified against the published SHA256, and used with `dump --nonblocking --json --full-filenames`. It was not installed into the project/Python environment. No locals, target code injection, process suspension, native debugging or subprocess scan was requested. The [maintainer documentation](https://github.com/benfred/py-spy/blob/master/README.md#how-can-i-avoid-pausing-the-python-program) describes nonblocking sampling and its potential torn-read failures.

Six single-shot reads produced four complete stack snapshots and two read errors. Both errors are retained; they are diagnostic sampler errors, not controller failures. No target/model call, solver replay, Skill execution or production/prompt edit was added. The six sampled project source files remain byte-identical to their frozen snapshot. Sparse read-only sampling still has some observation overhead; no zero-overhead claim is made.

## Run and queue status

At the last saved observation (2026-11-02 00:18 China), the controller remained alive under the broad propagation stage; neither propagation nor DOE had committed. The existing 001/010/013 queue supervisor remained alive and waiting for GA4 plus its original controller-owned zero-model replay. There were still18 accepted target requests and2,309,177 public known tokens. No extra request was dispatched by this audit. Source/DOE correctness, actual propagated coverage and final timing remain pending.

The next implementation priority suggested by this evidence is removing redundant reconstruction within one unchanged run, using already validated material and a single existing lookup rather than re-expanding the whole graph per declaration. This is a diagnosis, not a change request or implementation: current code remains frozen. Broad loop-engine changes should not be made on the strength of this latency observation.

## Artifacts

- [Structured finding and stack summary](performance-summary.json)
- [Static annotation cost audit](annotation-cost-audit.md) and [counts](annotation-cost-stats.json)
- [Loop/static reachability audit](loop-audit.md) and [counts](loop-audit.json)
- [Solver mechanism audit](solver-audit.md)
- [Nonblocking stack002](stack-sample-002.json), [004](stack-sample-004.json), [005](stack-sample-005.json), [006](stack-sample-006.json)
- [Process samples](process-samples.jsonl), [source integrity](sampled-source-integrity.json), [tool provenance](tooling/provenance.json)
