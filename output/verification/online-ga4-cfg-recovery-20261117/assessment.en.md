# GA4 cfg-recovery run: closed, partial result

The sole run `document-guided-ga4-cfg-recovery-high-20261117-135205` is closed. It completed diagnostic propagation and DOE, but **did not establish any deletable input or field**. Source review failed when its correction delivery exceeded the adapter character limit. This was not a connection or native-generation timeout. The sole replay matched with zero new native starts, and all recorded processes exited.

This report concerns that closed parent only. The user's subsequent instruction to retain its accepted Task, flow and CFG and start a separate processing-onward run is recorded in the new restart namespace. It does not resume this parent, alter its evidence or change its conclusions.

## Scope and selection

The run used `gpt-6.1-sol/high/openai`, the complete 16-file GA4 package (155,170 source bytes), seven normal semantic requests, two workers and the existing correction, shared-repair and transport budgets. Implementation `694561928259d08c00492843a036ad0196460f785e6bd5d2fb1e07ba8ef59445`, prompts, transport, controller helpers and executables remained frozen. The final provenance audit checked 211 pinned files and their snapshots, all source files and three executable hashes without differences.

Pre-launch offline acceptance records 2,593 distinct latest scoped passes, one Windows symlink-privilege skip and no unresolved failures. This is a union of affected-scope receipts, not a single all-green whole-repository run. Earlier failures and their fixes remain preserved.

Task, flow and CFG were accepted on their first responses. Task contains 49 requirements and ten issues; three issues remain unresolved. The selected CFG is the initial **215-block, 489-IR, 192-edge** graph. No graph correction or shared semantic repair occurred. The final selection uses that initial Task/CFG and the original assembled partial annotation. The new mixed CFG-error aggregation and missing-CFG recovery were therefore not exercised by this online case; offline evidence must not be relabeled as online validation of those branches.

## Exact processing and review failures

Processing a001 used the shared response form but failed the marker grammar at `/shared_values/v601/evidences/1`. The bounded raw diagnostic identified a marker object with an additional member; the raw response remains rejected and preserved. Processing a002 fixed the representation issue and reached ordinary structural validation. Its local read at `ir_001` failed the read/transform boundary rules. Independent-record retention also detected an undeclared expression input in `ir_346`, whose successful inspection case declares local `verdict` but references IR input 0.

The partial processing value retains **484 IR records**: 272 with operation segments and 212 without segments. The remaining five comprise three source-declared unmodeled IR (`ir_140/289/295`) and two validation-isolated IR (`ir_001/346`). The three source gaps preserve sparse-array index/length behavior and JavaScript `undefined` distinctions rather than inventing dense arrays or `null`. All original source-gap records and both validation gaps remain available. Partial retention is not full response-chain acceptance.

Review a001 completed normally in **1,595.048 native-process seconds**. It received **883,238 delivered characters** and returned 225,754 answer characters. The response authored 17 findings and 451 checks, with 403 labeled accepted and 48 rejected by the model. Those labels did not pass validation. Saved validation contains 15 malformed scope-check records and 34 finding/check conflicts, grouped into three conflict diagnostics: 49 raw issues and 18 grouped diagnostics.

One concrete malformed shape groups a wide rule and an input remainder under the same `affected_scope_ids`. The link can apply to the wide rule; it cannot be inherited by the remainder subject. The target can exist and still have the wrong subject relationship. Conflict correction must also reconcile a finding with checks that simultaneously accept the implicated contract.

The existing strategy requested a complete review replacement. Its correction prompt retained the complete prior answer and all diagnostics, increasing the core prompt by **172,553 characters**. Exact sharing and column packing were already applied. Review a002 was **1,055,579 core characters + 212 adapter-envelope characters = 1,055,791 delivered characters**, exceeding 1,048,576 by **7,215**. The adapter rejected it before any native process started; no second review answer exists.

Both review prompts retain identical complete source suffixes and the same complete logical base material: 451 contracts/obligations (106 compute, 345 tool) and **1,738 scopes**. The failure was not caused by source truncation, omitted contracts or disabled compression. The request-failure path publishes `review=null`; it does not apply the record isolation used after structural-correction exhaustion to the preceding returned answer. As a result, **zero contract checks were accepted**, no validated findings entered shared repair, and the existing unavailable-review admission barrier correctly prevented that round. This differs from the preceding run's missing-CFG failure.

## Actual backend and source coverage

Propagation processed **463/489 IR**, with **five unmodeled and 21 blocked**. The blocked ranges are `ir_002–013`, `ir_141`, `ir_290`, `ir_296` and `ir_347–352`. Thus the local failures did not invalidate the entire graph, but the module-entry chain and inspection-loop outcomes remain incomplete. `ir_457` and `ir_459` additionally have missing-part diagnostics even though their IR count as processed.

| Source boundary | Matching processed boundary records |
|---|---:|
| Direct remote call sites | 13/13 |
| `saveResult` caller sites | 25/25 |
| Physical filesystem call sites | 7/7 |

These are abstract operation records, not actual Skill execution or a semantic-correctness score. The 13 remote boundaries have actual request-delivery and response-receive records, but all use static service names and request inputs without an explicit source-client/credential receiver-data binding. The seven compact realtime/metadata IR now reconstruct source-backed property requests inside processing, yet their acquired client handles remain unbound to the remote endpoint. Save summaries have symbolic writes; complete caller-to-callee path identity and wrapper-field necessity are not established for every invocation. A saved-file-to-Markdown-summary chain is still not implemented in the source model.

All 106 opaque compute contracts contain one whole-value output rule. Input field selectors do not substitute for distinct output-subfield rules. Actual demand requests `ir_285` fields `indexStatus.verdict`, `coverageState` and `lastCrawlTime`; the saved result reports unavailable reviewed transfers for those exact fields. There are **287 `input_contract_unavailable` diagnostics across 122 IR**. Missing review is the observed rejection reason; whole-output-only authoring is a separate precision limitation, not a measured counterfactual explanation of every unresolved range.

The demand report contains **1,654 assessment rows** and **763 required / 3,417 unresolved / 0 deletable range entries**. These are not unique-field counts. All modification proposals are null. Thirteen `wrong_input` findings originate from generated expected-value relation mismatches, without source-review confirmation; they are not thirteen proven Skill bugs. Required entries remain conditional diagnostic derivations from task seeds and deterministic relationships, not a complete source-verified necessity judgment.

DOE records **83 sinks with payloads** and **188 comparisons, all `no_excess_established`**. No reduction or deletion-preservation witness is established. This means insufficient evidence to establish excess, not safety and not that all fields are necessary. The recorded `date_comparison` preservation constraint is `not_established` under incomplete propagation.

## Actual cost, timing and closure

There were **eight native starts: seven normal plus one processing correction**. The ninth logical request was the review correction rejected before launch. Two logical corrections therefore do not mean two correction process starts. Shared repair starts and outer retries were zero. All eight native requests have complete final public usage: **1,375,851 input + 249,539 output = 1,625,390 tokens**. Cached input 49,152 and reasoning output 21,359 are included subsets. Provider billing and unreported provider-internal usage are not available.

| Request | Native seconds | Delivered input characters | Final answer characters |
|---|---:|---:|---:|
| Flow a001 | 143.333 | 186,460 | 14,341 |
| Task a001 | 483.844 | 187,967 | 42,101 |
| Graph a001 | 981.160 | 213,282 | 163,891 |
| Processing a001 | 1,242.849 | 424,727 | 159,665 |
| Processing a002 | 1,146.368 | 589,350 | 148,175 |
| Sensitivity a001 | 289.561 | 937,650 | 38,052 |
| Task correspondence a001 | 567.327 | 985,740 | 86,404 |
| Review a001 | 1,595.048 | 883,238 | 225,754 |

No native timeout, main sampling retry, connection-wait retry, stdout reconnect/error/failed-turn or outer retry was recorded. Auxiliary model-catalog/Apps MCP messages are separately inventoried and do not establish main model reconnects. Native process duration includes provider/network/host work; it does not isolate model-only generation time. Overlapping requests must not be summed into controller wall time, and this single case establishes no compression-induced speedup.

Analysis took **5,864.952 seconds**. The sole replay matched in **202.320 seconds**, with zero new native markers and unchanged inventory. The controller closed at **2026-11-17 07:33:50 UTC**. All eight native exit receipts are confirmed; root independently observed all ten recorded wrapper/controller/native PIDs absent at 09:08:06 UTC. The parent's launch and replay authorization is consumed. No parent resume, additional replay or Skill execution is part of this closure.

Detailed evidence is in [run-summary.json](run-summary.json), [backend/source audit](final-backend-source-audit.en.md), [review-delivery diagnosis](review-delivery-failure-final.en.md), [cost/provenance audit](final-cost-provenance.en.txt) and [proposal-only follow-up](followup-plan.zh.md). The separate processing restart is not evidence that any proposed code fix in this report has been implemented.
