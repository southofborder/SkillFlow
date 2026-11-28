# Final necessity and DOE audit

This passive audit reads the completed fresh run `document-guided-ga4-review-shared-v2-high-20261112-221242`. It does not execute analysis, validation, models, replay, Skills, or tests. Artifact byte hashes and exact evidence coordinates are recorded in `final-necessity-audit.json`.

## Recorded outcome

The controller closed with `partial`; its sole replay matched with zero new native markers. Demand and DOE remain partial. There are **zero deletable range records, zero input modifications, and zero DOE reductions**. All **121** data comparisons across **68** sinks conclude `no_excess_established`. This is neither a safe verdict nor proof that every original input is necessary.

| Saved assessment measure | Count |
|---|---:|
| Input assessments | 1,517 |
| Operation-input / IR-input / acquisition-output assessments | 740 / 661 / 116 |
| Required / unresolved / deletable range entries | 1,113 / 2,809 / 0 |
| Processed / blocked / unmodeled assessments | 1,484 / 24 / 9 |
| Processed / blocked / unmodeled upstream IR | 487 / 20 / 4 |
| Explicit `unreached` status entries | 0 |

These counts describe saved range entries; they are not disjoint unique physical fields. One input assessment can contain both required and unresolved ranges. There are 33 nonprocessed input assessments across 24 nonprocessed IR; they are explicitly classified as blocked or unmodeled rather than `unreached`.

## Review failure and scoped effects

The bound input-contract receipt is `structural_failure`, `source_review_complete=false`. Demand binds the same receipt digest, `bbc675305ff189930d28c655e9fcad60f869509f1b52b801ea50b74637f0ca96`. There are **271 expected physical contract obligations and zero accepted checks**. Both rejected review responses proposed 271 checks (227 labeled accepted, 43 rejected, one unresolved); those candidate labels do not establish accepted semantics. The three raw `missing_field` source-input candidates were also not accepted. No semantic repair occurred after the structural-correction budget was exhausted; details remain in the separate immutable `final-review-audit`.

The demand report records **177** `input_contract_unavailable` diagnostics across **64 IR and 103 operations**. Every such diagnostic has an explicit affected-IR boundary and is blocking for its applicable transfer. They are cited by **1,272** unresolved range records. The number 177 counts demanded-transfer diagnostic records, not inventory obligations. Their reasons identify the demanded output property/path and exact contract coordinate. Required results from supported deterministic relations still exist; the audit does not treat the rejected review as accepted guidance.

The unresolved outcomes cannot all be attributed to source review. The exact mutually exclusive buckets based on saved diagnostic references are:

| Unresolved range reference bucket | Count |
|---|---:|
| Contract-unavailable diagnostics only | 1,272 |
| Global Task/mapping diagnostics only | 774 |
| Global Task/mapping plus other local diagnostics | 656 |
| No diagnostic references | 107 |

There are **34 global diagnostics** with no IR boundary: 29 `requirement_expression_gap`, three `task_source_issue`, and two `unbound_requirement`. They occur in **1,430** unresolved range records. The two unbound requirements are `result_directories` and `markdown_summary`. The Task issues concern clicks versus impressions for top pages, a joint query/device breakdown versus separate reports, and metadata array versus object representation. Requirement coverage is 29 expressed, 27 partial, two retained-only. These global limits are distinct from local contract unavailability. Other overlapping diagnostic families include processing gaps, expected-relation mismatches, upstream coverage, and missing local records; exact counts are in the JSON.

Among the **107** unresolved records without diagnostic references, **87** name an exact CFG operand and an unestablished operand-to-location/path/selector metadata binding. The remaining **20** carry demand references and conservative-transfer reasons: public result (nine), retained control operands (nine), actual operand (one), and accumulation yield (one). Their absence of diagnostic references is not the absence of a recorded reason; representative IDs and coordinates are preserved in the JSON. No diagnostic reference points to a missing diagnostic ID.

## Source-input findings, acquisition, and constraints

The final demand report has **30 `wrong_input` findings**, all originating in `demand_analysis`, with no source-review references and no attached accepted source finding. Their recorded reason is failure to establish the Task's expected original-value relation. They must remain distinct from the three unaccepted source-review candidates; they are not confirmed missing-field defects from source review.

All **116 acquisition-output assessments** show an `unestablished` retrieval projection and no accepted capability entries. The report explains that no reviewed projection relation exists for the exact acquisition pair; this is not evidence that the interface is incapable of field projection.

The constraint report has 19 `satisfied` checks and one `potential_violation`, for the `entry_points` `only_if` constraint at `/realizations/4/constraints/0`. Its abstract witness does not assert feasible or actual execution. There are no modification-preservation or influence results because no reduction was proposed. Constraints remain separate from positive demand seeds.

The result supports a precise partial-analysis statement: the input-size delivery fix succeeded in the separately audited review requests, but this run establishes no deletion or DOE reduction. Accepted source-semantic review, Task/mapping limitations, and local processing/coverage/binding limitations remain separate boundaries.
