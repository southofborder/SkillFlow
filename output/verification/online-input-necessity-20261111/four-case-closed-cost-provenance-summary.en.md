# Four-case closed cost and provenance summary

All four original controllers and their sole zero-call replays are closed. The measured implementation is preserved: **GA4 failed at revision-processing; 001, 010 and 013 completed propagation but retained partial DOE results**. Replay matching does not change these outcomes.

The batch made **47 PID-confirmed native starts**. Forty-six requests reported complete public usage; one GA4 revision-processing request reported none. The exact known public total is **2,967,050 tokens: 2,584,495 input plus 382,555 output**. The failed request's consumption and any additional unreported internal-attempt usage remain unknown, not zero. This is not a complete monetary billing total.

| Case | Saved outcome | Starts | Complete / unknown public usage | Known public tokens | Analysis seconds | Sole replay seconds |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| GA4 | Failed, revision-processing | 12 | 11 / 1 | 1,919,852 | 8,857.056 | 32.074 |
| 001 | Partial DOE | 12 | 12 / 0 | 337,253 | 923.249 | 5.944 |
| 010 | Partial DOE | 11 | 11 / 0 | 316,571 | 923.444 | 6.739 |
| 013 | Partial DOE | 12 | 12 / 0 | 393,374 | 1,317.207 | 9.515 |
| Total | One failed; three partial | 47 | 46 / 1 | 2,967,050 | 12,020.956 | 54.272 |

All 47 start markers have PID confirmation and distinct public thread identities. There were no unconfirmed starts or pre-start input rejections. All four replay receipts are `matched`, each permits only its sole replay, and their combined **new native start count is zero**. Independent marker timestamps corroborate that result.

## Request categories and token accounting

| Category | Starts | Complete / unknown public usage | Known input | Known output | Known public total |
| --- | ---: | --- | ---: | ---: | ---: |
| Seven normal requests per case | 28 | 28 / 0 | 1,521,792 | 248,528 | 1,770,320 |
| Structural corrections | 4 | 4 / 0 | 467,799 | 29,559 | 497,358 |
| Shared semantic repair phase | 15 | 14 / 1 | 594,904 | 104,468 | 699,372, plus unknown usage |
| Total | 47 | 46 / 1 | 2,584,495 | 382,555 | 2,967,050, plus unknown usage |

Cached input totals **638,720**, already included in input. Reasoning output totals **90,157**, already included in output. Public cache-write input counters total zero. Subset counters are not added to the input/output total. Normal requests include responses that subsequently needed correction; public answer completion is not semantic acceptance.

**Outer network retries were zero.** Every outer attempt stayed at `attempt-001`. The GA4 failed process hit its 2,700-second limit without a complete answer; its saved classification remains "not an eligible transient network retry." No extra recovery request or replay was launched.

Public logs contain **nine stdout reconnect notices** across the batch (GA4 5; 001 2; 010 1; 013 1). Independently inspected stderr contains **fourteen sampling-retry log lines** (7; 3; 2; 2). These are overlapping logging layers inside existing native processes. They must not be added together or translated from their ordinal labels into additional starts, provider HTTP attempts or token usage. Provider HTTP-attempt counts and monetary billing remain unknown.

## Timing

The first controller began at **17:34:28.720542 China time**, and the final controller closed at **20:56:17.879502** on 2026-11-11. That batch controller span is **12,109.158960 seconds** (3 h 21 min 49.159 s), including gaps between the sequential controllers.

The sum of individual controller elapsed times is **12,077.691688 seconds**. Recorded analysis durations sum to **12,020.9560491 seconds**, and the four sole replays sum to **54.2722025 seconds**. Individual native request durations sum to **13,923.1264997 seconds** because workers overlap. These quantities have different scopes and must not be added as independent elapsed costs.

## Frozen provenance and independent reconciliation

The last original closed-case audits, taken before post-batch production edits, checked the same 194 pinned implementation files for each case, all frozen source files (16, 1, 3 and 1), controller/helper identities and CLI/renderer executables. No current/snapshot implementation change, source/staging change, unpinned current file or executable mismatch was found.

The shared implementation SHA is `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`; the broader snapshot SHA is `74922a9625638534aa6ed5e852593c7ae398060d4ede90869afcb3f5beefcdee`. Each case retains its own source hash and original selected materials. This summary does not relabel them as evidence for the later corrected implementation.

Separate standard-library recounts reread each case's raw public launch/PID/process/usage/replay records. Their token sums, request inventory, public completion/unknown counts and timing match the saved metrics. All final independent checks pass. GA4's audit is `verified_with_usage_limitations`; the other three are `verified` for the public records available.

The machine-readable seal is `four-case-closed-cost-provenance-seal.json`, with canonical seal SHA-256 **`9aaad6c38a9027c0af8912e1584fa61e62e87fecd8c016c040679e46f58745cc`**. It records final audit references/hashes, independent reconciliation references/hashes, per-case report hashes, exact counters, original run outcomes and preserved helper discrepancies.

Final frozen audit receipts:

- GA4: `cost-provenance-audit/ga4-20261111T125649521750Z.json`.
- 001: `cost-provenance-audit/001-20261111T125651369692Z.json`.
- 010: `cost-provenance-audit/010-20261111T125653177498Z.json`.
- 013: `cost-provenance-audit/013-20261111T125654863065Z.json`.

Detailed English cost sections are `ga4-closed-cost-section.en.md`, `001-closed-cost-section.en.md`, `010-closed-cost-section.en.md` and `013-closed-cost-section.en.md`. Their independent raw-record receipts are named and hashed in the seal.

The initial helper discrepancy receipts remain preserved. One early provisional helper compared canonical prompt JSON and UTF-8 text digests directly; another initial GA4 recount compared usage dictionaries without allowing an omitted optional zero counter. Subsequent final receipts document the corrected checks. Neither helper issue changed a run artifact, invalidated the directly matching token sums, or supplied missing usage.

This closes the original batch's cost/provenance audit before any production correction. It authorizes no new model call, Skill execution, controller, probe or replay. Semantic/source-correctness conclusions belong to the separate selected-material assessments; public usage completeness and clean provenance are not semantic success.
