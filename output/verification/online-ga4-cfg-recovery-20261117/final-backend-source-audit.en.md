# Final passive backend and source audit

The sole run `document-guided-ga4-cfg-recovery-high-20261117-135205` ended **partial**, with diagnostic-only conclusions. Its selected materials remain the initial Task, `graph/initial.json` and `annotation/manifest.json`; their file hashes match `selection.json`. No shared repair occurred. This audit reads final saved JSON only. It does not rerun validation, compilation, propagation, DOE, a model, Skill or replay, and changes no frozen/run artifact. Prior provisional reports remain intact. `final-backend-source-audit.json` contains the full per-site evidence and hashes, produced by the standard-library-only `audit_final_backend.py`.

## Actual propagation

Of 489 generated IR, **463 were processed, five unmodeled and 21 blocked**. The five cutoffs are `ir_001`, `ir_140`, `ir_289`, `ir_295` and `ir_346`. These are the same three explicit source gaps and two isolated processing records described in the provisional audit. The blocked records are `ir_002–013`, `ir_141`, `ir_290`, `ir_296` and `ir_347–352`.

This observed localization is narrower than invalidating the entire graph: `ir_001` stops the module-entry chain, while independently represented public entries still produce records. Conversely, the inspection-loop body `ir_346` and its success/failure continuations remain absent. A later aggregate save (`ir_353`) has an abstract record; that does not prove that nonempty loop executions completed. Two additional saved propagation diagnostics at `ir_457` and `ir_459` report absent `value` parts in complete compositions. Their IR are counted processed despite those diagnostics, so “processed” is not equivalent to error-free source semantics.

## Source boundary reach versus semantic coverage

| Physical source sites | Represented in selected CFG | Have processed records and corresponding boundary operations |
|---|---:|---:|
| Direct remote calls | 13/13 | 13/13 request deliveries and response receives |
| `saveResult` callers | 25/25 | 25/25 local-call and symbolic storage-write records |
| Filesystem calls in storage | 7/7 | 7/7 matching Node filesystem boundary operations |

These counts come from the complete 16-file source and exact saved records, not inferred from mere graph presence. They remain **abstract boundary reach**, not real Skill execution, all-path coverage, field-precise correctness or successful DOE.

Every direct remote call uses a statically named service endpoint and the request as its sole delivered input. The seven compact realtime/metadata IR now explicitly acquire a local client and property and construct source-backed requests, but the acquired client handle does not bind the remote endpoint. The other six have explicit client operands in the CFG, yet their processing calls likewise omit that receiver relationship. Thus all 13 request/response boundaries are represented and reached, while **no explicit source-client/credential receiver-data binding is established at these 13 direct remote boundaries**. This is not a claim that the service names are wrong or that payload fields are all wrong. It limits authentication/receiver-sensitive demand conclusions.

Save callers retain the actual data contribution and a symbolic write, while the standalone storage callee separately models directory checks, serialization and writing. These records do not establish complete caller-to-callee path identity, timestamp collision behavior or wrapper-field necessity for every invocation. The source's saved-file-to-Markdown-summary obligation also remains without an implemented invocation-selection and summary-write chain. Boundary counts cannot fill those gaps.

## Contract review and field precision

Source review ended `request_failure`, and the immutable input-contract receipt has `source_review_complete: false`. It inventories **451 obligations** (106 compute and 345 compiled tool-operation obligations), **1,738 scopes**, **zero accepted checks** and zero scope decisions. The compiled tool count includes the call request/response operations; it is not 345 physical source calls. There are no accepted semantic input-necessity checks to reuse as deletion authority. The precise review delivery failure is documented separately by root.

The authored 106 opaque compute contracts still each have one whole-value output rule. Precise input field paths in those rules do not supply distinct output-subfield transfer rules. This limitation is now exercised by actual demand: `ir_285` is asked for `indexStatus.verdict`, `indexStatus.coverageState` and `indexStatus.lastCrawlTime`. The saved demand diagnostics say these exact output relationships have no accepted input-requirement review. Across the result there are **287 `input_contract_unavailable` diagnostics affecting 122 IR**.

Two facts must remain separate: review absence is the actual rejection reason recorded for these transfers; whole-output-only authoring is an additional visible precision limitation that a successful review/correction would still have to address. This run does not establish what the results would have been under a completed review. It would be unsound to treat a whole-value rule as an exact child-field rule to improve apparent coverage.

## Input assessments and DOE

The demand report contains **1,654 input-assessment rows**: 903 operation-input rows, 590 IR-input rows and 161 acquisition-output rows. Their coverage is 1,629 processed, 18 blocked and seven unmodeled rows. Range entries are:

| Row category | Required | Unresolved | Deletable |
|---|---:|---:|---:|
| Operation input | 276 | 1,819 | 0 |
| IR input | 399 | 1,318 | 0 |
| Acquisition output | 88 | 280 | 0 |
| Total | **763** | **3,417** | **0** |

These are range-entry counts, not unique fields: goals, versions, information properties and scopes can produce multiple entries. All 4,180 entries have null modification proposals. The `required` entries arise from task seeds and deterministic relationships such as object construction and incoming values; they are diagnostic results conditional on the generated Task correspondence, not a completed source-verified necessity verdict.

The report also has 13 `wrong_input` findings, all originating from demand-analysis `expected_relation_mismatch` and all without source-review references. They identify failure to establish expected original-value relations in the generated analysis. They must not be presented as 13 independently confirmed source Skill defects. Requirement correspondence is 23 expressed, 22 partial, three retained-only and one unmapped; these authored correspondence statuses also lack completed source review.

DOE lists **83 sinks**, all with recorded actual payloads, and **188 comparisons, all `no_excess_established`**. No reduction is established. This conclusion is explicitly unresolved under analysis limitations, not a safety verdict and not evidence that every fetched field is necessary. The sole recorded preservation constraint check (`date_comparison`, `requires_prior`) is `not_established`; its evidence cites incomplete propagation on the relevant path. There are no successful deletion-preservation witnesses or modifications.

The supported result is therefore improved observable boundary reach and a completed diagnostic backend pass over the retained model, with explicit local cutoffs and complete saved failure evidence. The user’s intended field-level deletion result remains unestablished for this run because semantic review did not complete and specific source/dependency gaps remain. No whole-source correctness or comparison-to-baseline accuracy claim is supported.
