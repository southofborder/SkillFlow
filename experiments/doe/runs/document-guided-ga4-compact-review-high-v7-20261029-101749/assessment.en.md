# GA4 compact-review v7: one real run

Final assessment. Main analysis and the sole scheduled replay have ended; the controller exited. No additional target request or second replay was performed.

## Outcome

This run has not established complete, useful DOE. Its selected CFG contains 262 instructions. Propagation committed `unsupported_feedback` with all 262 instructions marked `not_solved`. The rejected feedback is the generated batch-loop cursor increment at `ir_214`; it is not a transport limit, an unavailable model answer, or evidence of no sensitive exposure. Main analysis ended with status `failed` in DOE: `ValueError: Demand collection output has no recorded member scope`. No `doe-result.json` was produced. The demand-result validator expected a recorded member scope although the globally rejected propagation had no execution records. The demand engine creates collection-output nodes from declarations and has a missing-record diagnostic, but its result validator requires an evaluated member record. This is an additional failure-handling defect: absent propagation support was not delivered as an unresolved DOE result. It does not justify inventing a member scope or an empty exposure.

Both source-review requests completed. Removing the two mechanical coordinate inventories resolved the observed review-input size failure: complete submitted texts were 636,534 and 768,678 Unicode characters, including the delivery envelope, below the client's 1,048,576-character limit. This limit is an interface text limit, not a measurement of the model's token context window. Passing it on this source does not establish support for arbitrarily large Skills.

## Identity and execution policy

The sole new run is `document-guided-ga4-compact-review-high-v7-20261029-101749`. It started at 2026-10-29 10:18:12.831 China time. Configuration was `gpt-6.1-sol / high / openai`, with at most two workers. The complete 16-file frozen source contains 155,170 UTF-8 bytes and has source identity `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. The implementation recorded at preparation has identity `8a7dfb5f2c1dc4d03aa4778816aaa3cf4e0118d0ba373dcc70d35c780c687d78`.

Task remained source-only. Task correspondence received Task and processing; sensitivity received processing and source, without Task or correspondence. Annotation was assembled by the program. The run did not execute the Skill, continue a historical experiment, add monitoring prompts, or launch a second controller. All original responses, corrections and unsuccessful records remain archived.

## Why the IR count grew

The input source did not grow. These are counts of the selected CFG, not a sum of model stages or runtime loop iterations:

| Candidate | Blocks | IR | Dispatch | Return | Other actions |
|---|---:|---:|---:|---:|---:|
| Earlier v5 selected candidate | 63 | 126 | 7 | 56 | 63 |
| Earlier v6 candidate | 140 | 349 | 83 | 57 | 209 |
| Current v7 initial candidate | 98 | 239 | 55 | 43 | 141 |
| Current v7 selected repair candidate | 106 | 262 | 63 | 43 | 156 |

Some growth retains real relationships previously hidden inside coarse calls: acquisition and initialization, credential reads and client creation, requests and responses, conditional saving, file existence and parsing, and independent report results. Such separation can improve traceability. It does not by itself establish coverage or correctness.

The generated batch-loop mechanics are a different issue. The selected graph encodes `loop_phi`, a cursor, an explicit cursor increment and backedges. `ir_214` computes `advance_for_of_cursor` from `result_185` into `result_189`. The feedback component spans `block_077` through `block_083`. The propagation backend rejects data-generating cyclic feedback because it cannot collapse an unbounded sequence of versions into one identity. It therefore marks every instruction `not_solved`, including independent parts of the graph. The supported single-level `for_each` member summary was not used for this batch representation.

This is an integration mismatch between graph abstraction and propagation capability. Structural validity does not imply that the chosen feedback representation is solvable. The shared granularity prompt asks for source boundaries and opaque pure local computation, but does not explicitly align this graph representation with the supported member-summary form. More IR was not a successful substitute for that alignment.

## Annotation and review evidence

The initial processing fragment had 209 modeled IR and 30 explicitly unmodeled IR, with 18 additional source limitations. The initial task-correspondence correction still had ten invalid constraint-expression references; validated material was retained as partial. The first source review returned seven concrete findings: two CFG issues, four processing issues and one task-correspondence issue. These included import/initialization routes, per-URL console deliveries, missing API/save summaries, whole-settings reads, internal returns incorrectly treated as observations, save-path identity, and receiver-specific analytical content requirements.

The shared repair rebuilt CFG, processing, task correspondence and sensitivity, then performed one independent rereview. It did not rebuild Task or flow. The selected processing fragment contains 197 modeled IR, 59 source-declared unmodeled IR and six records isolated after structural correction. The 69 source gaps consist of 59 unmodeled gaps and ten other limitations. These are annotation coverage counts; none should be reported as successfully propagated instructions.

The repair processing response first failed JSON parsing. Its sole correction still produced 64 schema diagnostics, including empty processing segments inside cases. Repair sensitivity first referred to unmodeled IR; its correction attempted to change an existing record identity. The program preserved the responses and isolated invalid records instead of silently retargeting them. Repair correspondence was valid on its first response.

The rereview completed with three remaining processing findings: missing storage-write summaries, missing normal/thrown or caught-call outcome summaries, and a file filter whose actual needle operand appears only in predicate prose. The review's statement that particular boundaries are expressible is a review judgment; it is not a substitute for a successfully compiled and propagated implementation. A completed review means that review ran, not that the candidate passed semantic review. The root result's `graph_review: audit_passed` is derived from the absence of CFG findings in the last review; it did not establish solver compatibility and did not prevent the feedback rejection.

## Recorded cost and latency

All model generation is closed: 17 native process starts yielded 17 complete transport answers. A complete transport answer can still fail structural validation. The count comprises seven normal semantic requests, five requests in the shared semantic repair, and five structural corrections. There were no outer transport retries or rejected-before-start inputs. All 17 requests have complete public usage records.

| Request category | Actual starts | Recorded total tokens |
|---|---:|---:|
| Normal semantic requests | 7 | 820,196 |
| Shared semantic repair, excluding corrections | 5 | 740,596 |
| Structural corrections | 5 | 623,953 |
| Total | 17 | 2,184,745 |

Repair and correction requests account for about 62.5% of this run's recorded tokens. This is observed overhead, not a prediction that removing review would preserve quality.

| Recorded usage | Tokens |
|---|---:|
| Input | 1,802,022 |
| Cached input, included in input | 288,768 |
| Output | 382,723 |
| Total input plus output | 2,184,745 |

Reasoning-output usage is included in output; no hidden reasoning is exported. No currency amount or human review time is inferred. These are the public per-request receipts, not an estimate of unreported provider-internal work.

Initial program assembly took 556.19 seconds and repair assembly 431.81 seconds. Propagation, including material loading and save verification, took 1,044.35 seconds. These are stage wall times; concurrent model-stage durations must not be added to obtain overall elapsed time. Main analysis took 7,902.34 seconds (2 h 11 min 42.34 s), ending at 2026-10-29 12:29:55.551 China time. The DOE stage ended in error after 263.89 seconds. The single replay took 1549.35 seconds (25 min 49.35 s). Controller wall time including replay and closure was 9452.43 seconds (2 h 37 min 32.43 s).

Read-only code inspection identified repeated full fragment assembly on load: `document_guided.online.load_annotation` calls `_assembled_values` even with `recompute=False`, and propagation loading/save verification calls this loader repeatedly. Compiled audit artifacts are already persisted, yet the loader still reconstructs the full assembly. This is concrete redundant work in the current path. It is not a measured profile proving a particular percentage of total time. No implementation was changed during the run.

The v5 baseline used 17 requests, 1,757,935 known public tokens and 4,688.21 seconds of main analysis, but processed only 8 of 126 IR and left its 14 comparisons unresolved. The v6 baseline used eight starts, 874,398 known tokens plus one unknown rejected request, and failed at review input capacity before propagation. The current run consumed about 24.28% more known tokens than v5. Because completion scopes differ and current propagation failed, none of these comparisons establishes full-workflow acceleration or improved DOE accuracy.

## Implementation acceptance and limits

Offline acceptance covered 485 unique selected cases, with the one observed legacy-fixture regression repaired and its focused tests rerun. The generic compact view preserves complete source and semantic content while removing only the model-facing expanded `target_index` and `_fragment_origins`; both remain local. Invalid-target corrections use bounded parent context. Pre-submit self-checks add no model requests. The client checks the entire submitted text before launch. Recorded review-request failures preserve legal candidates for deterministic analysis with an explicit incomplete-review status. Historical run bytes and failure identities were not migrated.

The real run validates transport feasibility for both reviews and preservation of limited correction/repair budgets. It does not validate semantic coverage or establish that self-checking improved correctness. The independent source review and its repair did not eliminate the graph/backend mismatch or the remaining processing gaps.

The next small engineering changes suggested by this evidence are to align single-level loop generation with the existing member-summary representation, diagnose unsupported feedback before expensive downstream generation, correct the documented cases/empty-segment contract and recurring missing-boundary modeling, and reuse compiled in-memory materials during one analysis instead of repeatedly reassembling them. These are follow-up recommendations, not changes made to this frozen run. A general cache executor, generic exception engine or new model-monitoring layer is not implied.

## Closure evidence

Main status is failed, propagation coverage is 0 solved / 262 not solved, and no DOE result was published. There are zero evaluated propagation records and sinks; this is missing analysis, not zero source boundaries or evidence of no exposure. A complete unresolved-boundary count is unavailable because formal DOE did not commit.

The propagation-only replay matched with no differences and zero model calls. The whole guided replay failed with `ValueError: Replayed guided decisions differ from saved results`, after 1,549.35 seconds, with zero new native starts. Code-path inspection identifies a failed-DOE replay gap: replay asks for a committed DOE manifest, but the live DOE failed before producing one. The saved top-level replay receipt reports the decision mismatch; this explanation is based on the missing manifest and the recorded replay path, not an invented passing receipt. No second replay was used to replace it.

The final implementation check is unchanged, with no modified files. Native starts remain 17. The controller closed at 2026-10-29 12:55:45.262 China time. All seven normal requests and all correction/repair costs are retained. No practical advantage over direct GPT can be inferred from this one unsuccessful system run.


## Evidence files

- [Machine-readable result and cost summary](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/run-summary.json).
- [Original root failure](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/result.json), [main timing](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/analysis-finished.json), and [controller closure](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/controller-finished.json).
- [Selected CFG](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/graph/selected.json) and [selected annotation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/revision/annotation/manifest.json).
- [Initial source review](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/review/result.json) and [remaining review findings](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/revision/review/result.json).
- [Propagation status and instruction coverage](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/propagation/manifest.json).
- [Original public-usage ledger](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/metrics.json).
- [Propagation replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/propagation/replay/summary.json), [failed full replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/replay-check.json), and [unchanged implementation check](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-compact-review-high-v7-20261029-101749/implementation-check.json).
- [Chinese implementation and offline acceptance report](D:/projects/SkillFlow/docs/doe/compact-review-v7-offline.zh.md).

Stage originals remain in `task/` and `steps/*/calls/*/response.json`; source-review originals remain in each review's recorded calls. These final semantic responses are distinct from transport transcripts. No hidden reasoning is exported in this report.
