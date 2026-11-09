# 013 source-fetch-with-fallback: v8 online assessment

**The run did not complete every required path, and it did not establish a substantive DOE conclusion. It did produce useful partial provenance:** the first preferred-tool request, the independent direct-to-archive route, and both archive terminal outcomes were propagated. The first-outcome dispatch prevented the retry and the two preferred-tool success paths from completing. The sole zero-model replay matched.

This is the fresh authorized development case 013, requested as `gpt-6.1-sol / high / openai`, with two workers, seven normal semantic requests and the existing correction/repair budgets. It is not a held-out comparison against direct GPT. Source criteria below are independent assistant judgments, not human gold. The audit read saved JSON, the frozen one-file source and archived interface code only; it did not execute the Skill, targets, loaders, compilers, the solver or another replay.

## Actual propagation and boundary coverage

| Measure | Actual result |
|---|---:|
| Selected CFG | 26 IR, 9 blocks, 11 edges |
| Compiled processing present | 25 / 26 IR |
| Actually processed | **15 / 26 IR — 57.69%** |
| Reached source-unmodeled cutoff | **1**, ir_006 |
| Downstream blocked | **10 IR** |
| Saved propagation records / Data objects | 15 / 15 |
| Resolved sink coordinates | 14: 10 model observations, 2 tool deliveries, 2 storage writes |
| Unresolved declared boundary coordinates | 9 |
| Sensitivity declarations resolved | 1 / 1 |
| Computed sensitive-data comparisons | 4, **all unresolved** |

Generated-IR coverage is not source coverage. The corresponding source actions and outcome branches are:

| Source relation | Propagated coverage | Remaining scope |
|---|---:|---|
| request.source_id acquisition | 1 / 1 | Runtime value remains unknown |
| environment.FAST_KEY acquisition | 1 / 1 | Presence/absence classification remains an abstract condition |
| Initial fast.fetch request/response | 1 / 1 | Its outcome cannot pass the next dispatch |
| Retried fast.fetch request/response | 0 / 1 | Blocked by first-outcome dispatch |
| Archive call family | 1 / 1, **partial entry coverage** | Direct credential-absent entry propagates; both failed-fast entries are unresolved |
| Required terminal outcome branches | 2 / 4 | Archive success/error propagate; first-fast/retry-fast success do not |
| Required status-append outcome branches | 2 / 4 | Archive success/error appends propagate; fast-success appends do not |

The four terminal branches are a source outcome denominator, not four physical return statements in the short source. An ordinary return is not automatically a user-delivery sink. The fourteen generated sink coordinates also are not fourteen source actions or DOE findings.

The useful provenance is concrete. The first fast request sends the selected source_id plus the selected FAST_KEY. Archive sends only that same source_id, without the key or either preferred-tool response. The archive response has its own acquisition identity, distinct from the fast response. Its `body` and `error` selections remain tied to that response, and the two corresponding return inputs retain those exact selected identities. Both reached status writes append the matching opaque final-status value to the prior status.txt version; they do not replace the file or substitute the whole response as a claimed literal status.

Those relations are saved static possibilities. They do not prove exact runtime branch feasibility, exact call counts or global credential-prohibition compliance. Status content/encoding remains a local limitation, and possible dependence on a response does not imply that the response is literally stored in the status string.

[Seven source-criterion checks and exact Data/IR evidence](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small013-source-audit.json).

## Concrete blocker and repair ownership

The blocker is **CFG/processing interface alignment**, not a validation rejection of the selected record and not backend nonconvergence.

The source requires three alternatives after the first fast call: success, transient failure and non-transient failure. The generated `block_003` terminator `ir_006` therefore has three CFG successors: `block_006`, `block_004` and `block_005`. However, the frozen executable `BranchOp` has only `true_target` and `false_target`, and its validator requires those two targets to equal **all** actual outgoing successors. A branch within that unchanged three-successor block cannot satisfy the contract.

The initial source review correctly identified absent typed outcome routing but assigned the repair to processing. The repair changed the terminator to an explicit source-unmodeled cutoff while retaining its real input and all three CFG edges. The final review retained one finding and suggested two binary decisions, again with processing ownership. That suggestion requires a CFG split: the intermediate decision needs a real block/edge and a matching outcome input. It cannot be implemented by processing alone under this frozen contract. The problem does not establish a need for a generic exception or loop engine; a CFG compatible with the existing binary interface could express this bounded retry.

Evidence: [selected CFG](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/graph/initial.json); [selected compiled annotation](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/revision/annotation/audit/compiled-response.json); [archived BranchOp fields, line 256](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/implementation-snapshot/src/skillflow/propagation/contracts/specs.py:256); [exact-successor validation, line 759](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/implementation-snapshot/src/skillflow/propagation/contracts/specs.py:759); [final source review](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/revision/review/result.json).

The selected cutoff has `origin:source`, `unmodeled:true` and no validation errors. Four additional processing gaps concern unspecified final-status details and do not themselves stop propagation. The backend saved the first-call prefix before the cutoff and continued the independent direct-to-archive branch. The result remains explicitly partial; the final review did not clear its finding.

## DOE usefulness and correctness limits

FAST_KEY is a source-grounded credential, explicitly named in the preferred request and forbidden at archive/diagnostic output. Its declaration resolves to the actual selected environment-field version. The DOE has three sensitivity derivations and 691 demand derivations. Four sensitive-data comparisons occur at:

1. The possible model observation of acquired environment content containing FAST_KEY.
2. The possible model observation of the selected key for credential-presence processing.
3. The initial fast.fetch request's key argument.
4. The possible model observation of the first fast response, whose key dependence is only `possible`.

All four are `no_excess_established` with an explicit reason that relevant limitations leave them unresolved. **They are neither safe verdicts nor established excess-data findings.** In particular, the fourth comparison does not claim that the response contains the key in plaintext. The resolved archive payload contains no key identity, but the global prohibition check still remains unresolved because required paths are missing.

There are zero supported positive DOE findings and zero contradicted positive DOE findings, with four unresolved comparisons. No usable accuracy, precision or recall denominator is established. All eleven constraint checks are `not_established`; preservation and influence result sets are empty. The 32 diagnostic records overlap affected relations and are not 32 independent defects. No fabricated diagnostic-output operation is added merely to instantiate the prohibition.

The result is useful for locating source versions, recipients, response pairing, the independent archive branch and the exact routing defect. It does not yet supply a complete actionable sensitive-payload minimization conclusion for the Skill.

[Actual DOE result](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/doe/doe-result.json); [actual propagation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/propagation/manifest.json); [source audit](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small013-source-audit.json).

## Actual cost and timing

| Category | Actual CLI starts | Public tokens |
|---|---:|---:|
| Normal semantic requests | 7 | 180,153 |
| Shared semantic repair and dependent rebuilding | 4 | 128,768 |
| Structural corrections | 2 | 67,004 |
| **Total** | **13** | **375,925** |

Public input usage is **335,585**, including **159,744 cached-input tokens**. Output is **40,340**, including **12,242 reasoning-output tokens**. Cache and reasoning counters are subsets, not additional totals. All thirteen accepted final responses have complete public usage; raw public turn counters, accepted-answer hashes and complete delivered-input hashes reconcile. Original outputs later corrected remain included in the cost.

| Time measure | Actual duration |
|---|---:|
| Main analysis | **15 min 40.26 s** — 940.2633461 s |
| Propagation stage, included above | 53.712383 s |
| DOE stage, included above | 92.062570 s |
| Sole replay | **1 min 51.36 s** — 111.3602313 s |
| Controller start through closure | **17 min 33.14 s** — 1,053.142802 s |

The replay matched with **zero new native starts**. Stage clocks include validation, reconstruction and saving, and parallel-stage durations overlap. There were no recorded outer retries, prelaunch input rejections, public reconnect/error events, tool events or delegation items.

The thirteen unique public CLI thread/turn identities are not invented provider response IDs. Request records and launch flags consistently request the configured model/effort/provider; public logs do not independently attest backend configuration. Exact provider HTTP attempts, any unreported internal work, currency cost and human review minutes remain unknown. Post-run assistant auditing is a separate unmetered cost here.

[Full cost and protocol evidence](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small013-cost.md); [structured accounting](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small013-cost.json).

## Preservation and delivery

The one frozen source file and implementation check match their recorded hashes. The implementation SHA-256 is `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. Original answers, corrections, source reviews, unmodeled records and replay receipt remain unchanged. No target resampling or second replay occurred.

This is one of the four authorized validation reports. The separate offline simplification was not used in this run and is authorized only after the four-run result/cost delivery. These results do not establish general accuracy, full analysis coverage or superiority over direct GPT.

[Structured run summary](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/run-summary.json); [sole replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/replay-check.json); [implementation check](D:/projects/SkillFlow/experiments/doe/runs/document-guided-013-general-loops-high-v8-20261101-214748/implementation-check.json).
