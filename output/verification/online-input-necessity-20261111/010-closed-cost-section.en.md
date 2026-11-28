# Case 010 closed-run cost, timing and provenance

The catalog-query run `document-guided-010-input-necessity-high-20261111-173347` closed **partial**: propagation completed, while DOE and the selected source review retained limitations. It made 11 PID-confirmed native process starts: seven normal requests and four requests in the shared semantic repair phase. There were no structural correction requests or outer network retries. All eleven requests reported complete public token counters.

The exact public total is **316,571 tokens: 284,886 input plus 31,685 output**. Cached input is 167,680 tokens, already included in input; reasoning output is 15,605 tokens, already included in output. These subsets are not added again. Public events report zero cache-write input tokens. No request has missing or partial public usage, but provider HTTP-attempt counts, any unreported internal-attempt usage and monetary billing remain unknown.

| Request category | Native starts | Complete-usage requests | Input | Output | Public total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal stages | 7 | 7 | 166,204 | 20,931 | 187,135 |
| Structural corrections | 0 | 0 | 0 | 0 | 0 |
| Semantic repair | 4 | 4 | 118,682 | 10,754 | 129,436 |
| Total | 11 | 11 | 284,886 | 31,685 | 316,571 |

The zero counts above are observed category counts, not inferred usage for a missing request. Every launch marker has a PID receipt, every process returned exit code zero, and each request has one completed public usage event. Semantic acceptance and DOE completeness are separate from process/usage completeness.

## Per-request reconciliation

| Stage | Category | PID | Process seconds | Public tokens |
| --- | --- | ---: | ---: | ---: |
| Flow | Normal | 27596 | 51.057 | 17,740 |
| Task | Normal | 4584 | 81.629 | 19,536 |
| Graph | Normal | 9968 | 108.332 | 23,573 |
| Processing | Normal | 2028 | 131.105 | 37,200 |
| Sensitivity | Normal | 17496 | 50.396 | 23,640 |
| Task correspondence | Normal | 17524 | 158.019 | 31,319 |
| Source review | Normal | 26632 | 75.524 | 34,127 |
| Revised processing | Semantic repair | 15208 | 198.125 | 38,471 |
| Revised sensitivity | Semantic repair | 18440 | 50.984 | 24,213 |
| Revised task correspondence | Semantic repair | 23328 | 84.918 | 30,901 |
| Revised source review | Semantic repair | 3948 | 103.562 | 35,851 |

Independent standard-library inspection reread the public launch/PID/process receipts, raw usage events and sidecars, metrics and replay markers. Direct integer token sums, duration sums, launch inventory and every reported sidecar counter agree with the saved metrics. All 13 independent checks passed; the reconciliation retains each public thread identity and hashes of the underlying records.

## Timing and internal notices

Controller PID 2032 started at **20:18:30.005173 China time** and closed at **20:34:00.792148** on 2026-11-11. Marker elapsed time, including replay and controller overhead, was **930.786975 seconds** (15 min 30.787 s). The controller separately recorded **923.4444747 seconds** for analysis. The first-native-start to last-native-finish span was **919.7544241 seconds**; individual request durations sum to **1,093.6517297 seconds** because the two workers overlap.

Revised processing, PID 15208, public thread `01a1ca93-b89f-7c70-a49a-c45f4b27b85c`, emitted **one stdout reconnect notice** for a request timeout. Its stderr contains **two `responses_retry` log lines**, one for a disconnected stream with OS error 10054 and one for a request timeout. The same native process subsequently completed and reported usage.

The stdout and stderr counts describe overlapping internal logging layers. Do not add them, interpret retry ordinals as provider HTTP-attempt counts, count extra native starts, or infer additional token amounts. Every outer transport directory remained at `attempt-001`; **outer retries were zero**.

## Sole replay and provenance

The sole replay started at **20:33:54.104764 China time**, took **6.7385358 seconds**, and returned `matched` with **zero new native launch markers**. Independent timestamp inspection found no native marker at or after replay start. Matching the saved workflow does not remove its semantic review objections or DOE limitations.

The original closed audit checked 194 pinned files and all three frozen source files. It found no snapshot/current implementation change, no source/staging change, and no controller/helper/CLI/renderer mismatch. Implementation SHA remains `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`; source SHA remains `66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c`. Both cost audits report `verified`, with no recorded discrepancy.

Evidence:

- Original closed audit: `cost-provenance-audit/010-20261111T123441264245Z.json`.
- Independent raw-record reconciliation: `010-closed-cost-independent-reconciliation-20261111T123613819357Z.json`.
- Read-only standard-library recount: `reconcile_closed_public_records.py`.

The original source-review interpretation and partial DOE result remain preserved under the measured implementation. Any later correction to review guidance is separate from this cost record. This audit changed no production/run artifact and launched no model, Skill, replay or controller; the batch freeze continues through case 013 and its sole replay.
