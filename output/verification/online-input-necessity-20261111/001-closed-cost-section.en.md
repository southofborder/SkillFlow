# Case 001 closed-run cost, timing and provenance

The conditional-notification run `document-guided-001-input-necessity-high-20261111-173347` closed **partial**: propagation completed, while DOE retained limitations. It made 12 PID-confirmed native process starts: seven normal requests, one structural correction, and four requests in the shared semantic repair phase. All twelve requests produced complete public token counters; no request has missing or partial public usage.

The exact public total is **337,253 tokens: 305,110 input plus 32,143 output**. Cached input is 125,696 tokens, already included in input; reasoning output is 16,774 tokens, already included in output. Neither subset is added again. The public events report zero cache-write input tokens. Complete reported request usage does not establish a provider HTTP-attempt count, separately billed internal-attempt usage, or monetary billing.

| Request category | Native starts | Complete-usage requests | Input | Output | Public total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal stages | 7 | 7 | 164,561 | 20,383 | 184,944 |
| Structural correction | 1 | 1 | 25,725 | 457 | 26,182 |
| Semantic repair | 4 | 4 | 114,824 | 11,303 | 126,127 |
| Total | 12 | 12 | 305,110 | 32,143 | 337,253 |

There were **zero outer transport retries**, no unconfirmed starts and no pre-start input rejections. A completed public answer is not itself evidence that the generated semantic material was accepted; the task-correspondence structural correction and four repair-phase calls are included in the total.

## Per-request reconciliation

| Stage | Category | PID | Process seconds | Public tokens |
| --- | --- | ---: | ---: | ---: |
| Task | Normal | 21804 | 79.455 | 19,192 |
| Flow | Normal | 12640 | 48.478 | 18,224 |
| Graph | Normal | 26012 | 88.581 | 23,188 |
| Processing | Normal | 28068 | 151.308 | 37,696 |
| Sensitivity | Normal | 13872 | 70.157 | 22,559 |
| Task correspondence | Normal | 21260 | 184.968 | 29,759 |
| Task-correspondence correction | Structural | 13040 | 27.582 | 26,182 |
| Source review | Normal | 28244 | 106.570 | 34,326 |
| Revised processing | Semantic repair | 26032 | 113.371 | 38,396 |
| Revised sensitivity | Semantic repair | 6924 | 31.799 | 22,610 |
| Revised task correspondence | Semantic repair | 22024 | 77.297 | 29,938 |
| Revised source review | Semantic repair | 15100 | 111.308 | 35,183 |

Independent standard-library inspection reread all twelve launch/PID/process receipts, public stdout events and usage sidecars, then compared their integer sums and timing with the saved metrics. Each request has one completed public turn; all reported sidecar counters match the corresponding raw public event. All 13 independent checks passed. The reconciliation preserves actual public thread identities and hashes of its source records.

## Timing and internal notices

Controller PID 14792 started at **20:02:49.514336 China time** and closed at **20:18:19.355720** on 2026-11-11. Marker elapsed time, including replay and controller overhead, was **929.841384 seconds** (15 min 29.841 s). The controller separately recorded **923.2486224 seconds** for analysis. The first-native-start to last-native-finish span was **919.55016494 seconds**; the sum of individual request durations was **1,090.8734833 seconds**. The latter includes overlapping workers and is not additional elapsed time.

The original task-correspondence process, PID 21260, public thread `01a1ca81-bda5-7ff3-b257-86503f068438`, emitted **two stdout reconnect notices**: a workspace-routing discovery timeout and a disconnected stream with OS error 10054. It subsequently completed and reported usage.

Its public stderr contains **three `responses_retry` log lines**, covering two routing-discovery timeouts and the disconnected stream. These are observations inside the same native process, from a different logging layer. They overlap the stdout notices: do not add the two counts, infer actual provider HTTP attempts from ordinal labels, count extra native starts, or invent token amounts. Every outer transport directory remains at `attempt-001`.

## Sole replay and provenance

The sole replay started at **20:18:13.402444 China time**, took **5.9443219 seconds**, and returned `matched` with **zero new native launch markers**. Independent timestamp inspection found no marker at or after replay start. Replay consistency does not remove the source-review or DOE limitations recorded in the partial result.

The closed provenance audit checked 194 pinned files and the one frozen source file. It found no snapshot/current implementation changes, no source/staging changes, and no controller/helper/CLI/renderer mismatch. Implementation SHA remains `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`; source SHA remains `d7548162e5d4de62ee90bd1763b1a701bcbe731c723d675d9d2e0dd8e5c989a6`. Both the closed audit and independent reconciliation report `verified`, with no recorded discrepancy.

Evidence:

- Original closed audit: `cost-provenance-audit/001-20261111T121904653264Z.json`.
- Independent raw-record reconciliation: `001-closed-cost-independent-reconciliation-20261111T122025565668Z.json`.
- Recount utility: `reconcile_closed_public_records.py`, which uses only the standard library, reads the fixed fresh batch, requires closure/replay receipts, and creates a new verification artifact without importing project runtime or executing a process.

This audit changed no run artifact or production file and launched no model, Skill, replay or controller. The batch remains frozen until all four original cases and their sole replays close and their original cost/provenance records have been preserved.
