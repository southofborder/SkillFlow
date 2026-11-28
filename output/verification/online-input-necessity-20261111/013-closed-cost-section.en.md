# Case 013 closed-run cost, timing and provenance

The source-fetch-with-fallback run `document-guided-013-input-necessity-high-20261111-173347` closed **partial**: propagation completed, while DOE and the selected source review retained limitations. It made 12 PID-confirmed native process starts: seven normal requests, one structural correction, and four requests in the shared semantic repair phase. All twelve requests reported complete public token counters.

The exact public total is **393,374 tokens: 344,678 input plus 48,696 output**. Cached input is 145,408 tokens, already included in input; reasoning output is 20,785 tokens, already included in output. Neither subset is added again. Public events report zero cache-write input tokens. No request has missing or partial public usage. Provider HTTP-attempt counts, separately unreported internal-attempt usage and monetary billing remain unavailable.

| Request category | Native starts | Complete-usage requests | Input | Output | Public total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal stages | 7 | 7 | 177,494 | 30,607 | 208,101 |
| Structural correction | 1 | 1 | 33,129 | 331 | 33,460 |
| Semantic repair | 4 | 4 | 134,055 | 17,758 | 151,813 |
| Total | 12 | 12 | 344,678 | 48,696 | 393,374 |

There were **zero outer transport retries**, no unconfirmed starts and no pre-start input rejections. Process completion and public usage completeness do not establish semantic review or DOE completeness.

## Per-request reconciliation

| Stage | Category | PID | Process seconds | Public tokens |
| --- | --- | ---: | ---: | ---: |
| Flow | Normal | 11160 | 34.525 | 17,739 |
| Task | Normal | 3860 | 73.146 | 19,667 |
| Graph | Normal | 20208 | 134.484 | 24,497 |
| Processing | Normal | 2392 | 231.177 | 41,475 |
| Processing correction | Structural | 26576 | 28.370 | 33,460 |
| Sensitivity | Normal | 26488 | 48.678 | 25,552 |
| Task correspondence | Normal | 24600 | 212.903 | 36,497 |
| Source review | Normal | 11384 | 152.769 | 42,674 |
| Revised processing | Semantic repair | 28108 | 173.063 | 43,603 |
| Revised sensitivity | Semantic repair | 13120 | 74.515 | 25,353 |
| Revised task correspondence | Semantic repair | 19432 | 162.789 | 37,900 |
| Revised source review | Semantic repair | 19876 | 171.238 | 44,957 |

An independent standard-library recount checked all launch/PID/process receipts, raw completed-turn usage, sidecars, metrics and replay markers. Each request has one completed public usage event. Integer token sums, all reported sidecar counters, process durations and launch inventory match the saved metrics. All 13 independent checks passed. Public thread identities and hashes of the underlying records are preserved in the reconciliation artifact.

## Timing and internal notices

Controller PID 26640 started at **20:34:10.544947 China time** and closed at **20:56:17.879502** on 2026-11-11. Marker elapsed time, including replay and controller overhead, was **1,327.334555 seconds** (22 min 7.335 s). The controller separately recorded **1,317.2073239 seconds** for analysis. The first-native-start to last-native-finish span was **1,312.27054906 seconds**; individual request durations sum to **1,497.6573951 seconds** because two workers overlap.

Revised sensitivity, PID 13120, public thread `01a1caa8-e00f-7e52-8997-1ebf98ba64de`, emitted **one stdout reconnect notice** for a request timeout. Its stderr contains **two `responses_retry` log lines**, both reporting a request timeout. The same native process completed and reported usage.

These stdout/stderr records describe overlapping internal logging layers. They must not be added, converted from ordinal labels into provider HTTP-attempt counts, counted as extra native starts, or used to invent additional token usage. Every outer transport directory remained at `attempt-001`; **outer retries were zero**.

## Sole replay and provenance

The sole replay started at **20:56:08.393501 China time**, took **9.5148754 seconds**, and returned `matched` with **zero new native launch markers**. Independent timestamp inspection found no native marker at or after replay start. Replay consistency does not remove the Task, interface or DOE limitations recorded in the partial result.

The original closed provenance audit checked 194 pinned files and the one frozen source file. It found no snapshot/current implementation change, no source/staging change, and no controller/helper/CLI/renderer mismatch. Implementation SHA remains `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`; source SHA remains `fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da`. Both cost audits report `verified`, with no recorded discrepancy.

Evidence:

- Original closed audit: `cost-provenance-audit/013-20261111T125654863065Z.json`.
- Independent raw-record reconciliation: `013-closed-cost-independent-reconciliation-20261111T125722872916Z.json`.
- Read-only standard-library recount: `reconcile_closed_public_records.py`.

This audit changed no production or run artifact and launched no model, Skill, replay or controller. The original measured implementation and partial result remain unchanged; subsequent offline corrections require separate evidence and identities.
