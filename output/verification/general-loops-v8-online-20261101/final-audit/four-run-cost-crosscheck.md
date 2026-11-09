# Four-run v8 cost and closure cross-check

**58 actual native starts produced 3,363,332 known public tokens.** All four controllers closed with `partial` analysis results; each sole replay matched with zero new native starts. These are closure/accounting facts, not semantic-success claims.

| Run | Normal / repair / correction | Starts | Public tokens | Main analysis | Sole replay | Controller wall |
|---|---:|---:|---:|---:|---:|---:|
| GA4 | 7 / 6 / 5 | 18 | 2,309,177 | 3 h 34 m 44.53 s | 0 h 54 m 10.07 s | 4 h 28 m 55.26 s |
| 001 | 7 / 4 / 3 | 14 | 343,524 | 0 h 15 m 37.32 s | 0 h 0 m 45.75 s | 0 h 16 m 24.47 s |
| 010 | 7 / 5 / 1 | 13 | 334,706 | 0 h 15 m 14.98 s | 0 h 1 m 30.83 s | 0 h 16 m 47.38 s |
| 013 | 7 / 4 / 2 | 13 | 375,925 | 0 h 15 m 40.26 s | 0 h 1 m 51.36 s | 0 h 17 m 33.14 s |

## Public usage and request categories

| Category | Starts | Input | Cached input (subset) | Output | Total tokens |
|---|---:|---:|---:|---:|---:|
| normal semantic | 28 | 1,091,541 | 591,488 | 201,326 | 1,292,867 |
| semantic repair | 19 | 1,088,857 | 530,432 | 175,275 | 1,264,132 |
| structural correction | 11 | 752,064 | 293,888 | 54,269 | 806,333 |

The total is **2,932,462 input + 430,870 output = 3,363,332 tokens**. Cached input (1,415,808) is contained in input. Reasoning output (104,238) is contained in output; neither is an extra chargeable-token total. Public cache-write input is zero.

All 58 accepted finals have complete public usage. There were zero outer retries and zero inputs rejected before process launch. Six public reconnect events occurred in GA4: three in each of the initial and revised review. All other three runs have zero public reconnect/error events. Exact provider HTTP attempts and any extra unreported internal failed-attempt usage remain unknown. No monetary amount is inferred.

## Identity, protocol and implementation

The audit independently parsed all 58 saved `stdout.jsonl` streams, with 58 unique CLI thread/turn-order identities across all four runs and no duplicates. Public provider response IDs are absent. Identical answer text from distinct completed requests is retained as distinct cost; answer hashes are not a response-identity substitute. Every accepted-answer hash and request/prompt/launch delivery hash matched. Public events contain 58 agent-message completions and zero recorded tool/delegation items.

Each official implementation check records unchanged files and SHA-256 `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. Every transport request records `gpt-6.1-sol / high / openai`. This is requested configuration, not independent provider attestation. No model probe was added. Each of the four existing replay receipts says `matched` with zero new native markers; no additional replay was run.

## Time accounting

The four main analyses sum to **4 h 21 m 17.09 s** (15677.0945008 s), and the four replays sum to **0 h 58 m 18.01 s** (3498.0123335 s). Controllers together occupy **5 h 19 m 40.25 s** (19180.249150 s). The complete sequential interval, from 2026-11-01 21:44:56.449800 to 2026-11-02 03:05:07.575185 China time, is **5 h 20 m 11.13 s** (19211.125385 s), including 30.876235 s between controllers.

The difference between summed controller wall time and main-plus-replay counters is 5.1423157 s of controller overhead and clock-boundary differences. Per-request durations and parallel-stage durations must not be added to controller wall time. Local propagation/DOE clocks include validation, reconstruction and saving; this ledger does not relabel them as solver-only or model-inference-only measurements.

## Cost scope and limits

The ledger includes all original answers later corrected/replaced, structural corrections and the one shared semantic-repair round in each of these four runs. It excludes prior experiments and separately conducted assistant source auditing/report preparation, whose usage is not metered here and must not be treated as zero. Human review minutes remain unknown. The combined elapsed interval ends at controller closure, before report delivery.

[Structured ledger, all request identities and evidence hashes](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/four-run-cost-crosscheck.json). Individual cost audits: [GA4](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-cost-protocol.md), [001](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small001-cost.md), [010](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small010-cost.md). The 013 individual audit is being prepared independently; this cross-check parsed its saved transport directly.
