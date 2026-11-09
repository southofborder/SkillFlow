# 001 conditional-notification: backend-r3 online assessment

Propagation completed for all 24 generated IR, and all three inventoried source boundary sites have saved records. The result provides useful source, member and receiver lineage. **DOE remains partial: all 38 sensitive comparisons are explicitly unresolved, with no established excess finding or actionable reduction.** This is successful propagation, not a complete semantic/DOE success.

This fresh run used `gpt-6.1-sol / high / openai`, two workers and the unchanged frozen source. One shared semantic repair rebuilt CFG, processing, task-correspondence and sensitivity, then repeated the unified source review. The selected result is `graph/revision.json` with `revision/annotation`. Both controller and its sole zero-call replay have closed. Historical answers were not imported.

## Actual coverage and source correspondence

| Scope | Result |
|---|---|
| Generated IR | 24/24 processed; 0 cutoff, blocked, not-reached or not-solved |
| Inventoried acquisition | events.json read at `ir_001`, recorded |
| Inventoried notification | notify.send at `ir_018`, recorded |
| Inventoried persistence | count.txt write at `ir_023`, recorded |
| Source boundary sites | 3/3; static site coverage, not dynamic invocation counts |
| Sink positions | 18: 16 contract-default model observations, 1 tool delivery, 1 storage write |
| Sensitive declaration | 1/1 resolved: each record's access_token |
| DOE comparisons | 38/38 unresolved; raw label `no_excess_established` |
| Actionable reductions | 0 |

The most useful checked relation is actual notification pairing. Recipient selection at `ir_016` and original-summary selection at `ir_017` share the same member Data ID and identical member binding. The request built at `ir_018` has only `recipient` and `body`; body references the original summary without an intervening rewrite. No access_token field was added to this request. Exact IDs and JSON pointers are in the [independent source audit](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/001-source-audit/source-audit.json).

The source's opted-out/urgent/value condition is represented with actual operands and normalized expressions. Runtime values are unknown. The source says eligibility is necessary but does not explicitly say every eligible record must be selected. The generated selection abstraction preserves this uncertainty. An unknown collection uses a symbolic member; this single run does not dynamically establish exactly-once handling or test duplicate concrete records.

The count write consumes an abstract count version; nine candidate values are alternatives, not nine actual records. The source leaves “processed records” ambiguous between examined, selected and notified records. That ambiguity remains explicit. Possible credential influence in an abstract count dependency is not claimed to be credential plaintext in count.txt. A summary could contain unknown runtime content, so the absence of an added access_token field is not a universal guarantee about arbitrary summary text.

## Why useful propagation has not become a useful DOE verdict

The saved DOE explicitly says the comparisons are unresolved. `no_excess_established` must not be read as “all data are necessary” or “no issue exists.” No notifier data review was generated for the declared token field, while other model/count-related comparisons remain limited. Default model observations are static runtime-contract possibilities, separate from actual notify.send arguments.

There is a specific avoidable annotation defect. Realization R6 retains the token prohibition as a gap and claims a suitable selector cannot be expressed without lexical `for_each`. The frozen interface already provides task-scope `forbid_information`, with a source reference to `ir_001`, local `original_records`, and an `each/access_token` path. The claimed interface incapability is contradicted by that schema. This audit did not compile or evaluate a replacement, so it does not claim adding that one declaration would resolve every comparison.

Final review F001 correctly notices the missing prohibition but assigns owner `sensitivity`. The sensitivity declaration type has value/scope/property/label/evidence fields, not recipient prohibitions. The restriction belongs to task-correspondence/realizations. This is a review repair-ownership defect. The shared repair budget was already used; no additional repair was launched.

Remaining limitations also include genuine source ambiguity and global demand/constraint gaps. Saved diagnostics contain three requirement-expression gaps, two task-source issues, three processing gaps and one unbound requirement. These are not propagation cutoffs: propagation itself completed. The final graph review is `audit_passed`, annotation review `incomplete`, and DOE demand status `partial`.

The source audit splits six original criteria into 17 explanatory observations: 10 supported, 5 unresolved and 2 contradicted contract/ownership claims. These are not independent samples or a general accuracy denominator. There are zero published excess claims to contradict; the 38 unresolved comparisons provide no precision or recall estimate.

## Actual calls, public tokens and time

| Call group | Starts | Input | Cached input subset | Output | Total |
|---|---:|---:|---:|---:|---:|
| Normal semantic stages | 7 | 151,413 | 86,016 | 18,740 | 170,153 |
| Shared semantic repair | 5 | 134,946 | 61,440 | 16,167 | 151,113 |
| Structural corrections | 2 | 51,964 | 24,576 | 1,524 | 53,488 |
| Total | 14 | 338,323 | 172,032 | 36,431 | 374,754 |

The two corrections belong to initial and revised task-correspondence. Extra transport attempts: 0. All 14 final answers have complete public usage; no unknown or partial final-response usage was recorded. Public thread/turn-or-order identities are distinct. Provider-internal HTTP attempts and unreported internal failed-attempt usage are unknown. Cached input is included in input and must not be added again.

| Timing | Seconds |
|---|---:|
| Main analysis | 1,107.930 (18 min 27.93 s) |
| Public native start-to-finish span, including overlap and gaps | 1,091.410 |
| Propagation compute | 2.977 |
| Propagation save | 2.019 |
| Propagation total | 5.641 |
| DOE load | 1.817 |
| DOE compute | 5.000 |
| DOE post-compute publication interval | 1.697 |
| DOE total | 8.654 |
| Sole replay, matched with 0 new starts | 36.737 |
| Controller wall including replay | 1,146.121 |

Component intervals are nested and nonadditive. Stage wall times, including correction and validation, are stored individually in [run-summary.json](run-summary.json); parallel Task/flow and mapping/sensitivity stages overlap. Request duration sum is not total analysis wall time. No monetary amount or human-review time is inferred.

## Comparison and evidence

The old v8 001 result processed 2/13 IR and reached acquisition only, leaving notify and count write unresolved. It used 14 starts, 343,524 public tokens and 937.318 s. This new run reaches all three boundary sites at greater token/time cost and resolves the generated propagation graph. It therefore demonstrates improved completion scope in this sample, not a full-flow speedup or complete DOE accuracy. Fresh generated graphs differ. Paused v9 has no terminal online result to substitute into this comparison.

- [Structured assessment and detailed stage costs](run-summary.json).
- [Independent source audit](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/001-source-audit/source-audit.md), with evidence IDs and source ambiguity.
- [Saved propagation](propagation/records.json), [saved DOE](doe/doe-result.json), [final review](revision/review/result.json).
- [Public metrics](metrics.json), [component timing](component-timing.json), [sole replay](replay-check.json).

The implementation check is unchanged. Python SHA is `5ccbc1941be908ff20b15d7a56a631e678285b42a255031d29505ec6a0495637`; broader provenance SHA is `9ae31392bf97b0ae8c5ae75c48d1994e8b303b68cda6d532eb4b96f508c56703`. Frozen source SHA is `d7548162e5d4de62ee90bd1763b1a701bcbe731c723d675d9d2e0dd8e5c989a6`. This assessment used saved JSON/text only and added no model calls, Skill execution or replay.
