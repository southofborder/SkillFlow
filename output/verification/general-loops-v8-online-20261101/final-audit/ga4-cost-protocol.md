# GA4 v8: final cost and protocol audit

Run: `D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322`

The controller closed with **partial** analysis. It made **18 native starts** and used **2,309,177 reported public tokens** across accepted final responses. Main analysis took **3 h 34 m 44.53 s**; its sole zero-model replay matched in **0 h 54 m 10.07 s**. Controller wall time was **4 h 28 m 55.26 s**. These costs did not buy complete propagation or a complete semantic result.

## Calls and reported usage

| Category | Calls | Input | Cached input (subset) | Output | Total |
|---|---:|---:|---:|---:|---:|
| normal_semantic | 7 | 643,074 | 333,440 | 136,414 | 779,488 |
| semantic_repair | 6 | 742,721 | 374,912 | 145,883 | 888,604 |
| structural_correction | 5 | 595,346 | 220,160 | 45,739 | 641,085 |
| **Total** | **18** | **1,981,141** | **928,512** | **328,036** | **2,309,177** |

The output total contains 62,953 reported reasoning-output tokens; these are a subset, not an additional total. No reasoning text was inspected or exported. Cache-write input is reported as zero. All 18 accepted finals have complete public usage; none has partial or missing final-response usage. Summation from request receipts and public `turn.completed` input/cache/output counters matches saved metrics. Initial outputs that required correction and all repair requests remain in the accounting. Corrections plus semantic repair account for 1,529,689 tokens (66.24% of the reported total); that allocation alone does not say those requests were all avoidable.

There were 18 logical requests, 18 recorded native starts, no input rejection before start and **zero outer transport retries**. Six public reconnect errors occurred: both initial review and revised review emitted `2/5`, `3/5` and `4/5` reconnect messages with OS error 10054. Both later produced a substantive final. These labels do not establish the exact number of underlying HTTP attempts. Provider-internal attempt count and any additional unreported failed-attempt usage remain **unknown**. Complete public final-response usage therefore does not imply that every provider-side charge is known. No currency conversion is made.

## Identity and configuration evidence

The audit found 18 distinct `(CLI thread_id, public turn order)` identities, one accepted final and one completion per identity. Each accepted-answer hash matches the saved answer bytes, and each request-delivery hash matches its launch stdin hash. Public logs do not expose provider response IDs, so this audit does not invent them or claim deduplication by unavailable IDs.

Every saved request and launch command requests `gpt-6.1-sol / high / openai`. Every launch disables the plugin features and external project instructions and uses the read-only sandbox. Public JSONL contains 18 `agent_message` completed items and no recorded tool or delegation item. Request flags establish requested configuration; they do not independently attest a backend model configuration absent from public metadata. No new configuration probe was made.

The implementation check is unchanged at `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. The sole full replay is `matched` with **0 new native starts**. Original outputs, failures and archived implementation were not changed by this audit.

## Timing

| Stage | Result | Wall time |
|---|---|---:|
| task | complete | 0 h 09 m 33.30 s |
| flow | complete | 0 h 01 m 52.49 s |
| graph | complete | 0 h 14 m 39.58 s |
| processing | complete | 0 h 16 m 18.52 s |
| task-correspondence | partial | 0 h 10 m 36.81 s |
| sensitivity | complete | 0 h 05 m 34.91 s |
| assembly | partial | 0 h 08 m 14.99 s |
| review | complete | 0 h 12 m 18.58 s |
| revision/task | complete | 0 h 03 m 49.77 s |
| revision-graph | complete | 0 h 14 m 27.32 s |
| revision-processing | complete | 0 h 22 m 56.12 s |
| revision-task-correspondence | complete | 0 h 07 m 14.43 s |
| revision-sensitivity | complete | 0 h 05 m 59.06 s |
| revision/assembly | partial | 0 h 16 m 09.92 s |
| revision/review | complete | 0 h 07 m 19.25 s |
| propagation | incomplete | 0 h 38 m 51.87 s |
| doe | partial | 0 h 43 m 39.58 s |

The sum of public native-request durations is 2 h 05 m 38.96 s. The span from first native start to last native finish is 2 h 12 m 10.14 s; it includes gaps and overlap and is not active-only inference time. Stage clocks include local validation, reconstruction, saving and scheduling. In particular, propagation (0 h 38 m 51.87 s) and DOE (0 h 43 m 39.58 s) are stage durations, not measurements of loop fixed-point work alone. Parallel Task/flow, correspondence/sensitivity and repair stages overlap; summing all stages does not yield run wall time.

## Scope-aware comparison

| Run | Calls | Public tokens | Main analysis | Generated-IR outcome | DOE/replay outcome |
|---|---:|---:|---:|---|---|
| v5 | 17 | 1,757,935 | 1 h 18 m 08.21 s | 8 processed / 126; 2 cutoffs, 116 blocked | Partial DOE; replay matched |
| v7 | 17 | 2,184,745 | 2 h 11 m 42.34 s | 262 not solved / 262 | DOE failed; full replay failed |
| v8 | 18 | 2,309,177 | 3 h 34 m 44.53 s | 29 processed / 420; 5 cutoffs, 386 blocked | Partial DOE; replay matched |

Compared with v7, v8 used 5.70% more reported tokens and 63.05% more main-analysis wall time. Compared with v5, the increases were 31.36% and 174.83%. The frozen 16-file source is the same, but generated graphs and completed analysis scopes differ. These descriptive costs do not establish acceleration, cost effectiveness, general accuracy or superiority to direct GPT. Generated-IR denominators are not source-boundary denominators. Read the separate source/DOE correctness audit for substantive conclusions.

## Audit boundary and evidence

Only saved run artifacts and public transport metadata were read. No target, Skill, expensive loader, solver, replay or profiler was launched. This report accounts for this target run; historical runs and post-run assistant review overhead remain separate. Human review time and currency cost remain null.

Primary artifacts: `metrics.json`, each `transport/**/attempt-001/launch.json` and `stdout.jsonl`, accepted-answer receipts, `stage-events.jsonl`, `analysis-finished.json`, `controller-finished.json`, `replay-check.json`, `implementation-check.json`, and the exact closed v5/v7 `run-summary.json` files. The companion JSON contains per-request identities, accounting, reconnect messages, timestamps and evidence-file hashes.
