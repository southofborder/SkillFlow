# Small Skill 010 v8: public cost and protocol audit

This audit covers the closed fresh `catalog-query` run only. It reads saved public metadata, without invoking a loader, compiler, solver, replay, target or Skill. The analysis returned `partial`; cost reconciliation does not imply semantic completion.

| Request category | Actual starts | Input tokens | Output tokens | Total tokens |
|---|---:|---:|---:|---:|
| Normal semantic requests | 7 | 150,088 | 19,995 | 170,083 |
| Shared semantic repair and dependent rebuilding | 5 | 128,077 | 10,887 | 138,964 |
| Structural correction | 1 | 25,123 | 536 | 25,659 |
| **Total** | **13** | **303,288** | **31,418** | **334,706** |

Input includes **155,520 cached-input tokens**. Output includes **12,792 reasoning-output tokens**. These are subsets and are not added again. Cache-write input was reported as zero. The single structural correction was the initial task-correspondence correction. The shared semantic repair rebuilt CFG, processing, task-correspondence and sensitivity, then performed the revised review; Task and flow were reused.

All 13 accepted final responses have complete public usage. Request-level usage, public `turn.completed` counters and `metrics.json` reconcile exactly. All 13 accepted-answer hashes and actual prompt/request/launch delivery hashes match. This includes costs for earlier answers that were later corrected or replaced.

| Timing measure | Seconds | Readable duration |
|---|---:|---|
| Main analysis | 914.9828548 | 15 min 14.98 s |
| Propagation stage, included in main | 39.144467 | 39.14 s |
| DOE stage, included in main | 77.327567 | 1 min 17.33 s |
| Sole replay | 90.8301103 | 1 min 30.83 s |
| Controller start through closure | 1007.377318 | 16 min 47.38 s |

The controller started at 2026-11-01 18:30:34.036078 UTC and closed at 18:47:21.413396 UTC (2026-11-02 02:30:34 through 02:47:21 China time). The main analysis finished at 18:45:49.005236 UTC. The saved analysis/replay durations use their recorded timers; subtracting timestamps can differ slightly. Stage durations include validation, reconstruction, saving and scheduling and are not solver-only times. Parallel stages overlap. Summed native-process duration is 836.3466471 seconds; the first-start-to-last-finish native span is 797.2992139 seconds, which also includes gaps and overlap.

The single replay **matched** and recorded **zero new native starts**. The implementation check is unchanged, with no changed files. The three frozen source-file hashes match the run protocol. No historical answer, Task or CFG was imported.

Public transport records contain 13 `thread.started`, 13 `turn.started`, 13 `item.completed` and 13 `turn.completed` events. All completed items are agent messages. There are **zero observed error/reconnect events, outer network retries, startup input rejections or tool/delegation items**. Each public CLI thread/turn-order pair is unique. Provider response IDs are not exposed and are not invented. Exact provider HTTP-attempt counts and any extra unreported work remain unknown; absence of a public error does not establish a complete provider billing ledger.

All request records and launch flags consistently requested **`gpt-6.1-sol / high / openai`**. These flags establish requested configuration, while public events provide no independent backend model/effort/provider confirmation. No configuration probe was made.

The public target cost above excludes the separate post-run assistant source/accounting audit and other runs. Unmetered audit work is not treated as zero. Currency cost, human review minutes and a complete research-cost total remain unknown. These descriptive costs do not establish accuracy, general efficiency or an advantage over direct GPT.

[Machine-readable reconciliation, per-request metadata, stage times and evidence hashes](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small010-cost.json). [Original metrics](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/metrics.json). [Replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/replay-check.json). [Implementation check](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/implementation-check.json).
