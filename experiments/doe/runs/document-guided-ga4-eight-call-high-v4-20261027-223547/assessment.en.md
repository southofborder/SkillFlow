# GA4 eight-call High run: actual outcome, cost and blockers

Run: `document-guided-ga4-eight-call-high-v4-20261027-223547`. Date: 2026-10-27. Requested and observed launch settings: **gpt-6.1-sol / high / openai**.

## Outcome

**The run did not produce an accepted annotation, propagation facts or DOE.** Final status is `cannot_assess`, not a safe/no-DOE finding. The one shared semantic repair round was exhausted. The initial annotation returned a legal capability failure; the revised annotation supplied two complete-looking drafts but neither passed validation. Final partial review still found two CFG fidelity issues. No additional target run or manual answer patch was performed.

The source is the same complete frozen **16-file, 155,170-byte** GA4 package used by the old Max run. Source SHA-256: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. Task, CFG, documents and answers were regenerated. Old model results were not target inputs. [Protocol](run-protocol.json) records authorization and policy; [implementation snapshot](implementation-snapshot/snapshot.json) preserves 178 source/tool files. Analysis source bytes match launch. All 18 observed target launch commands request High; no configuration-confirmation model call was made. Public traces contain no unexpected tool items. The Skill was not executed.

## Actual calls, time and tokens

| Measure | New High run |
|---|---:|
| Normal semantic steps | 8 |
| Additional semantic steps in one mixed Task/CFG repair | 7 |
| Structural correction requests | 3 |
| Total logical requests / proven native starts | **18 / 18** |
| Explicit transport retry attempts | 0 |
| Analysis wall time | **1h 5m 56.43s** |
| Sum of native request durations, including overlap | 1h 18m 48.67s |
| Input tokens | **1,271,474** |
| Cached input, a subset | 361,856 |
| Output tokens, including reported reasoning | **253,527** |
| Reported reasoning output, a subset | 56,383 |
| Reported total input + output | **1,525,001** |
| Complete / partial / unknown usage attempts | **18 / 0 / 0** |
| Zero-call replay | matched; 13.01s; 0 new native markers |

Analysis ran from 22:36:32 to 23:42:29 China time. Closure including local metrics/replay ended at 23:42:42. Engineering configuration preparation and this post-run assessment are outside the analysis timer. One local CLI `exec --help` checked flags; it was not a model request. Native process count is not a claim about all provider HTTP attempts, which remain unobserved. Tokens are public CLI-turn counters associated with substantive final answers, not a billing invoice. Cache/reasoning subsets are not added twice; no currency amount is inferred.

| Stage | Native requests | Input | Output | Total tokens | Request seconds |
|---|---:|---:|---:|---:|---:|
| task | 1 | 77,424 | 20,587 | 98,011 | 504.62 |
| flow | 1 | 77,543 | 3,430 | 80,973 | 87.01 |
| graph | 2 | 80,137 | 49,898 | 130,035 | 901.45 |
| processing | 1 | 52,057 | 2,113 | 54,170 | 77.77 |
| task-correspondence | 1 | 54,337 | 4,333 | 58,670 | 120.57 |
| sensitivity | 1 | 48,380 | 1,486 | 49,866 | 54.12 |
| annotation | 1 | 67,946 | 11,333 | 79,279 | 515.98 |
| review | 1 | 131,640 | 5,073 | 136,713 | 214.92 |
| revision/task | 1 | 83,590 | 10,873 | 94,463 | 176.29 |
| revision-graph | 2 | 135,558 | 47,025 | 182,583 | 508.97 |
| revision-processing | 1 | 53,770 | 2,749 | 56,519 | 88.66 |
| revision-task-correspondence | 1 | 55,434 | 4,383 | 59,817 | 112.69 |
| revision-sensitivity | 1 | 48,831 | 1,402 | 50,233 | 60.49 |
| revision-annotation | 2 | 171,480 | 83,487 | 254,967 | 1093.10 |
| revision/review | 1 | 133,347 | 5,355 | 138,702 | 212.05 |

The revised annotation alone used **0h 18m 13.10s**, output 83,487 tokens, of which 6,943 were reported reasoning and 76,544 were the output remainder. Large complete-object generation/correction remains a material cost; this case cannot be explained solely as excessive Max reasoning.

## Comparison with the old serial Max run

| Measure | Old Max | New eight-call High |
|---|---:|---:|
| DOE produced | No | No |
| Native starts | 15, including 1 model confirmation and 1 retry | 18; no confirmation or retry |
| Structural corrections / semantic repair rounds | 2 / 1 | 3 / 1 |
| Sum of execution-process times | 3h 00m 04.78s across four segments | 1h 5m 56.43s in one continuous run |
| First-start to final-stop span | 3h 17m 46.90s, including resume gaps | 1h 5m 56.43s |
| Sum of native durations | 2h 59m 04.50s | 1h 18m 48.67s |
| Fully attributed reported tokens | 1,447,028 | 1,525,001 |
| Additional partial reported counters | 134,051 | 0 |
| Exact old/new whole-run token total known | Old: no | New public CLI usage: yes |

The new analysis wall time is 63.4% below the old sum of execution-process times. This is a **shorter unsuccessful run**, not a demonstrated speedup to a successful DOE result. The old recorded counters total 1,581,079, but the old true total remains unknown. New tokens are close to that recorded amount and exceed the old fully attributed bucket; a precise whole-run token-reduction percentage is not established. Cache mix also differs substantially, so a cheaper bill cannot be inferred from totals.

High effort, eight-call orchestration, parallelism, graph granularity, prompts, source projections, backend capabilities and cache hits differ together. One case does not isolate High's causal effect or establish accuracy equivalence. Initial Task took 504.62s versus old 1,139.62s; flow 87.01s versus 826.16s; processing 77.77s versus 297.44s. The first new annotation, however, took 515.98s versus old 197.03s and still failed. Both wait and rework must remain in the cost.

## What actually blocked completion

### 1. A real representation boundary appeared in the first annotation

[The original failure](steps/annotation/calls/a001/response.json) cites module singleton caches at `scripts/src/core/client.ts:12-15`, conditional assignments/reuse at `84-100` and `109-122`, and the per-occurrence wrappers at `scripts/src/index.ts:305-313` and `328-340`. The current backend rejects shared writes inside `for_each` (`contracts/specs.py:727-728`; EM07/EM11). Acquisition and yield are now available, but shared cache mutation/reuse across members remains outside that extension. This is supported by source and code; it is not a network failure. It also does not prove that the entire privacy audit must be abandoned: complete-processing annotation is currently an all-or-nothing prerequisite, with no accepted scope-local unsupported-processing record that lets other branches proceed.

### 2. The revised annotation ultimately stopped at evidence inheritance/validation

The [first revised draft diagnostics](steps/revision-annotation/calls/a001/validation.json) contain seven schema errors: a nested `each` demand path and six missing explicit multi-segment/element-scope orders. The allowed correction addressed that layer. [The final diagnostic](steps/revision-annotation/calls/a002/validation.json) is `evidence_kind`: sensitivity/expression evidence must cite frozen source. Its emitted path is empty.

Read-only reproduction traced the first offending inherited evidence to IR `ir_001`: a sensitivity declaration on local `invocation.arguments` omitted its own evidence and inherited a CFG-target citation from the IR parent. [Diagnostic details](annotation-evidence-diagnostic.json) preserve this location. The wire helper allows general source/CFG/rule evidence and advertises parent inheritance, while the expander later enforces source-only evidence for sensitivity/expressions. That exception is insufficiently exposed in the model interface, and the empty diagnostic pointer is an engineering weakness. Removing the source requirement would not fix the underlying provenance problem. The original seven schema errors stopped expansion before this later check, so the one-correction policy encountered a second validation layer only after its budget was consumed.

No accepted annotation resulted. The revised drafts are not evidence that the shared-cache or exception relationships have been solved. A targeted read of the invalid draft also found failure-record computation from a call-result/URL and failure-log conditionality described in evidence prose; faithful exception/condition semantics were not established. No patched draft was substituted or propagated.

### 3. Source fidelity still had unresolved differences

The [first partial review](review/result.json) found missing `getSearchAppearance` Task coverage and omitted date-range/per-URL console outputs. Task was revised from 42 to 46 requirements; CFG contracts were revised while remaining 64 blocks, 106 IRs and 84 edges. Counts are not fidelity scores.

The [last partial review](revision/review/result.json) still found (a) the documentation-prescribed project-root `.env` creation omitted as an actual setup write and (b) the index help-printing condition incorrectly terminating a selected imported export invocation. The repair budget was not extended. Both reviews had `annotation=false` availability and cannot establish annotation correctness. These are assistant source reviews, not expert gold judgments.

## Interpretation and smallest next changes

This run establishes that the High configuration and real parallel pipeline work, with complete public usage accounting. It **does not establish a practical end-to-end completion advantage**: approximately 66 minutes and 1.525 million reported tokens still bought no DOE.

Prioritize removing the whole-analysis escape hatch: require supported facts/receivers and explicit, source-located unknown relations for unsupported regions, then continue unaffected analysis without interpreting unknown as safe. That is a bounded partial-analysis policy, not a demand to construct a general cache/exception execution engine. Align evidence grammar/inheritance with source-only requirements, provide precise wire pointers, and expose hidden cross-field rules before the single correction is spent. Reduce full-object retranscription where it is purely mechanical. Keep Task independence, real versions/conditions/receivers and deterministic checks; do not demand fictitious completeness.

No model, semantic prompt, backend or frozen-source changes were made after target start. No extra target run was launched after failure. [Machine summary](run-summary.json), [full passive metrics](metrics.json), [raw stage events](stage-events.jsonl), [final status](result.json), [replay](replay-check.json) and both invalid drafts remain available.
