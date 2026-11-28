# Generic review display: GA4 online assessment

The general lossless source-review fix is implemented and offline accepted. This one fresh GA4 run and its sole zero-call replay are **closed**. Both actual source-review requests fit the unchanged input cap and retained complete material. The analysis nevertheless remains **partial** because the review's source-input defect records failed structural validation after its one correction. No deletable input or DOE reduction was established.

## Implementation and scope

The default guided run v12 / shared-v2 presentation applies to every Skill. It selects exact shared JSON values and inventory column tables only when the complete presentation, including its explanation, is shorter. There are no GA4-name, path or IR-count branches. Full source is unchanged. Semantic contracts, actual forward inputs, Task v5 isolation, seven normal requests, two workers and existing budgets remain unchanged.

The accepted implementation is `b3eba2da9823ac8a38620d7a5a728d7b8c66b4f3a5fe14fd7980997923330387`. Final offline acceptance passed **511 scoped tests, zero skips/failures** in one integrated execution; it was not a whole-repository run. Only review_display.py, source_review.py and runner.py changed in the production inventory. See [design](../../../docs/doe/review-input-size.md), [Chinese design](../../../docs/doe/review-input-size.zh.md) and [acceptance](../review-input-size-20261112/offline-acceptance.json).

## Input-size result and preservation

The prior rejected request had 1,079,505 Unicode codepoints: logical JSON 874,402, complete numbered source 180,825 and instructions/schema/envelope/delimiters 24,278. Annotation (403,839) and the mandatory inventory (244,455) dominated the logical JSON. Local audit metadata was already excluded; there was no duplicate full-fragment delivery. This was an adapter pre-start character-cap rejection, not a connection timeout.

| Material and comparison | Original display | New complete delivery | Saving / headroom |
| --- | ---: | ---: | --- |
| Same historical failed material, offline rendering only | 1,079,505 | 903,775 | 175,730 saved; 144,801 below cap |
| Same fresh material, normal real review | 1,038,128 | 861,152 | 176,976 saved; 187,424 below cap |
| Actual bounded review correction | — | 867,125 | 181,451 below cap |

The cap remains 1,048,576 codepoints. Both real deliveries retained all **271 physical review obligations, 1,045 scopes and 16 complete source files**. Exact expansion matched the original logical payload, including ordering, field types, contract bodies, identities and evidence. The correction retained the complete base prompt and changed only three response records. Initial assembly's 16 gaps, including four unmodeled IR, remained visible; they were not compression omissions. [Delivery proof](review-delivery-audit.en.md), [both-request audit](final-review-audit.en.md).

The fresh material also narrowly fit the old display, so this run's admission alone does not show that the old format would have rejected it. The separate same-material historical rendering regression demonstrates that the original overflow was fixed. Neither roundtrip nor a model process launch proves semantic correctness. Irreducibly large complete material can still exceed a finite cap; it is never truncated.

## Why review was not accepted

The first response proposed 271 contract checks (227 accepted labels, 43 rejected labels, one unresolved), 15 ordinary findings and three source-input findings concerning filters, orderBy and limit at ir_119. These are **raw model proposals, not accepted review evidence**.

Each source finding declared missing_field but used absent_argument. The sole structural correction replaced those records with input_index 0 and an empty field path. The remaining diagnostic was `A missing field must locate its nonempty path within an actual operand`. The stage exhausted its existing one-correction budget and ended structural_failure. Its authoritative receipt contains **zero accepted contract checks and zero accepted source-review findings**. Semantic repair requires an accepted completed review with findings, so it did not run. No extra request, repair budget or resampling was added. [Exact records and hashes](final-review-audit.json).

The terminal failure was therefore a response-location schema failure, not an input-length rejection or a 2,700-second native timeout. Reconnection events did occur separately, as recorded below.

## Coverage and input necessity

The selected CFG remains the initial accepted graph: 237 blocks, 222 edges and 511 IR. Static propagation processed **487/511**, with four unmodeled and 20 blocked positions. Processed status is not executed source coverage or proof of faithful boundary modeling.

| Physical source sites | Represented in CFG | IR processed | Correct boundary in records |
| --- | ---: | ---: | --- |
| 13 remote API calls | 13 | 9 | 6 network sends; 3 processed calls were local-tool substitutes, 4 unmodeled |
| 25 saveResult calls | 25 | 21 | 0 caller-specific persistence boundaries; 21 local-tool deliveries, 4 blocked |

Standalone storage records exist separately at ir_442 and ir_454; they do not instantiate each caller's payload/version. Ten loop structures processed, but successful per-member remote effects are missing in several cases. The Markdown summary writer remains absent. The original unused filters/orderBy reads appear in CFG metadata but are not preserved as distinct compiled field reads. Local diagnostics also remain at some processed positions. Thus this run does not validate complete boundary coverage or the original-read-preservation acceptance example on GA4. [Full source audit](final-source-coverage.en.md).

There are **1,517 input assessments and 3,922 emitted range records**: **1,113 required, 2,809 unresolved, zero deletable**. These are range entries, not disjoint unique fields. Coverage is 1,484 processed assessments, 24 blocked and nine unmodeled. All 116 acquisition projections remain unestablished. All 121 DOE comparisons are no_excess_established; there are no reductions or input modifications. This does not prove every input necessary or the Skill free of DOE.

Unresolved evidence is not attributed solely to review failure: 1,272 entries reference local contract-unavailability diagnostics; 1,430 reference global Task/mapping limitations (656 also reference local issues); 107 have no diagnostic_refs, comprising 87 explicit operand-to-metadata binding gaps and 20 conservative-transfer entries with demand references. There are 177 contract-unavailability diagnostics across 64 IR and 103 operations. Thirty wrong_input findings originate in demand_analysis as expected-original-value relation mismatches; they are not accepted versions of the three raw source findings. The precision and adequacy of these unresolved reasons are not established by compression or replay. [Necessity audit](final-necessity-audit.en.md).

Initial source-only processing audit also found root-only opaque transfer rules and current-argument-only interface evidence. Those quality concerns remain separate from complete delivery and were not repaired in this run. [Initial processing audit](processing-audit.en.md).

## Timing, cost and closure

Requested runtime was gpt-6.1-sol/high/openai, with two workers and the same complete source package. The run started 2026-11-12 22:13:21 China time; the controller closed 2026-11-13 00:33:52. Main analysis took **8,255.173 seconds**. Its sole replay matched in **174.913 seconds**, with **zero new native starts**.

Actual cost for this fresh run is **12 confirmed native starts = seven normal + five structural corrections**; semantic repair and outer retries were zero. Public final usage is complete for all 12: **2,296,735 tokens = 2,054,895 input + 241,840 output**. Cached input 924,416 and reasoning output 8,916 are subsets, not additions. No provider billing amount or public returned-model metadata is available; unreported provider-internal retry usage remains unknown. Prior attempts are not included in this total.

Ten internal CLI retry log lines comprise three TLS peer closes, one WebSocket close, three OS 10054 resets and three internal request timeouts. They are not ten extra native starts and cannot establish an HTTP-attempt total. All 12 native processes returned exit code 0 below the 2,700-second cap; final review failed validation after return. No public tool-execution events appeared. [Complete available cost, stage durations and provenance](final-cost-provenance.en.md).

The controller/wrapper exited. All 199 pinned implementation/transport/renderer files, 16 source files and additional executable/helper pins matched; historical tracked artifacts remain unchanged. No Skill was executed, old run resumed or historical analysis replayed. The generated DOE report's “Offline preparation; zero API calls” describes its deterministic DOE substage, not this 12-request online pipeline.

The single new-run and sole-replay authorizations are consumed. Preserve all failures and raw proposals. No further run or replay was launched. [Machine-readable summary](run-summary.json).
