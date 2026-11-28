# Mandatory input-contract coverage audit

Date: 2026-11-11. Scope: read-only inspection of the frozen implementation and the accepted GA4 processing fragment in the sole fresh batch `20261111-173347`. This is an implementation audit, not a completed-run assessment, replay, or new analysis of the Skill. No production file, prompt, controller, response, or historical artifact was changed.

## Finding

The current guided route has a real coverage-enforcement defect. It validates every input row of a **present** contract, but it permits an entire required contract to be omitted. The source-review contract table and its bound receipt enumerate only contracts that were supplied. An omitted tool contract therefore has no required explicit contract check and does not necessarily enter the existing correction or repair path.

This is distinct from a legitimate, source-supported semantic limitation. The approved representation for a missing interface fact is an explicit input row with an `unresolved` remainder and a concrete gap, including the missing fact and source evidence. Omitting the entire attachment supplies none of that evidence. Keeping optional fields in legacy/manual data models can be compatible with old artifacts; allowing the current guided route to accept their omission does not enforce the new route's mandatory coverage requirement.

The deterministic backend retains affected inputs conservatively **when a demand reaches a missing interface transfer**. That is useful containment, but not proof that every omitted contract becomes a diagnostic or that the frontend's complete-input audit has occurred. The distinction matters for the final interpretation of this frozen batch.

## Frozen evidence

Implementation SHA recorded for the running batch: `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`.

Accepted processing: `experiments/doe/runs/document-guided-ga4-input-necessity-high-20261111-173347/steps/processing/value.json`.

Its byte SHA-256 is `bc438b2cad3fd2f9572f05db74f9ae48d91b4cab4433edd544cf88120f22529c`, matching the selected result receipt. The receipt identifies `calls/a002`, step v9, one normal stage request and one structural correction. Its byte SHA-256 is `36a0b99dab02d6702f9c8217348c9a64d10d99054e9a13bd61f0b9f26548116d`.

Recursive inventory of the accepted authored operations, resolving their named locations against the same fragment:

| Authored form | Operations | Tool / remote | Operations with nonempty inputs | Actual input slots | Present input contracts |
| --- | ---: | --- | ---: | ---: | ---: |
| `call` | 109 | 96 / 13 | 67 | 70 | 0 |
| Explicit `deliver` | 88 | 86 / 2 | 87 | 156 | 0 |
| Combined | 197 | 182 / 15 | 154 | 226 | 0 |

These are authored operand slots, including literal arguments, before call expansion. They are neither unique data identities nor a count of final findings. Generated request/response pairs may duplicate the corresponding compiled contract obligations. The fragment also has 67 computes: 45 with `demand_transfer`, 22 with an inline expression, and none missing both. Its compute inventory does not expose the corresponding compute-presence defect in this particular fragment.

Examples include the `call` at `/ir_semantics/ir_012/segments/0/ops/0` and the explicit `deliver` at `/ir_semantics/ir_104/segments/0/ops/0`. The general inventory, rather than any claim about the necessity of these concrete argument values, supports this finding.

## Implementation path

All references below identify the frozen workspace sources and one-based line numbers at the time of inspection.

1. `src/skillflow/document_guided/annotation_wire.py:95` defines `FlatCall`; line 102 makes the entire `input_contract` optional. `src/skillflow/propagation/contracts/specs.py:117` and `:295` likewise make deliver/receive contracts optional and run input coverage checks only when a contract is present. Compute transfer presence is also optional at `:335`.

2. `src/skillflow/propagation/contracts/input_requirements.py:85` correctly requires every actual input index exactly once **inside a supplied rule/contract**. The gap model at `:40` requires concrete gap fields and source evidence. However, `normalize_input_contracts` at `:190`, specifically lines 204–205, skips absent attachments. Pair equality at lines 222–226 accepts two missing attachments as equal. Compiled validation at `:230` checks supplied entries, not an independently derived inventory of required operations.

3. `src/skillflow/document_guided/annotation_wire.py:678` validates the processing backend. It builds the actual target index and calls that normalizer at lines 728–731, without a separate presence/obligation check. `src/skillflow/document_guided/fragments.py:373` accepts processing after this expansion/validation succeeds. Consequently, whole-contract omission need not consume an existing correction or repair opportunity.

4. The processing prompt at `annotation_wire.py:50` expressly requires a transfer for each non-tool black-box compute. Line 51 describes tool contract contents and paired equality but does not unambiguously state the whole-attachment coverage obligation for every call, explicit deliver and explicit receive. Structural acceptance remains permissive regardless of the intended prompt meaning.

5. `src/skillflow/document_guided/source_review.py:277` builds the review inventory from `compiled.input_contracts`. Line 463 requires exactly one check for each **listed contract ID**. Lines 468–470 explicitly call out missing compute transfers, but there is no equally explicit missing-tool-contract inventory or required check. A general sparse finding could still notice such an omission; the finite contract table does not require it. Validation at `:548` checks the same supplied inventory.

6. `src/skillflow/doe/input_contract_review.py:46` compares check IDs only with supplied contract IDs. Its builder at `:123` binds the actual selected source, CFG, annotation and present contracts and checks completed review status, availability and partiality. This is valid identity checking, but it does not establish that all operations requiring contracts appear in that inventory. A receipt can therefore be correctly bound while the expected interface-contract coverage is absent. This audit does not claim a completed GA4 receipt already exists or passes.

## Backend containment and its limit

`src/skillflow/doe/input_contracts.py:86` returns `input_contract_unavailable` when a selected transfer has no accepted contract. `src/skillflow/doe/demand_engine.py:240` then records the gap and conservatively retains affected input ranges. Required tool actions invoke this path at lines 739–748; demanded receive outputs do so at lines 822–829. The existing action-only regression in `tests/doe/test_input_necessity_review_regressions.py:11` covers this situation.

The fallback is demand-triggered. A direct `input_use` goal is seeded on `op_input` at `demand_engine.py:495`; its step at `:756` propagates the demanded operand/observation without emitting the tool action. `_observe` at `:369` also creates operand demands, not action demands. If no other demand reaches that interface action or receive output, this path does not itself invoke the missing-contract fallback. `src/skillflow/doe/input_assessments.py:313` can classify uncovered ranges as deletable after the other checks succeed.

This is a static code-path concern, not an executed reproduction or an established finding in the still-running GA4 result. A targeted offline regression must determine the intended treatment of a required boundary payload whose invocation has no independent action goal. Do not report universal fail-closed coverage from the existing action-only regression. Conversely, a genuinely unused whole call need not become required merely because it has an interface contract; the approved no-demand deletion rule must remain intact.

## Smallest correction after the frozen batch closes

1. Derive a finite expected-contract obligation inventory from actual selected processing operations, resolved tool/remote location kinds, actual input slots and supported exact expressions. Cover flat calls and explicit deliver/receive forms in all supported scopes/cases. Cover non-tool computes without a supported exact expression, including valid expression supplements rather than only inline expressions. At minimum, every nonempty tool/remote input list needs its contract; explicitly settle the zero-input policy so it cannot introduce a fake input obligation.

2. Enforce that inventory at the **current guided processing** validation boundary. Missing/null required attachments are located processing-owned validation failures and use the existing structural correction and semantic repair budgets. Retain optional legacy/manual parsing and its conservative demand boundary. Never manufacture independence, mark all current payload fields necessary, or convert missing attachments into unsupported source gaps. Genuine unavailable interface facts remain explicit, evidence-backed per-input unresolved rows.

3. Reconcile the same independently derived inventory in source-review material and validation. Bind expected coverage as well as supplied contract identities in the new receipt protocol, or deterministically rederive and validate coverage from its bound selected annotation. Missing obligations must not disappear because no contract ID exists. Explicit rejected/unresolved checks and processing findings continue through the existing bounded repair. Preserve acceptance locality: unrelated findings must not revoke an independently reviewed contract.

4. Add focused offline negative tests for whole omitted/null contracts, all three tool/remote forms, both-missing and one-sided request/response contracts, nested supported scopes, missing compute transfer with no exact expression, review inventory omission and receipt coverage tampering. Keep positive tests for a source-supported explicit unresolved row, valid inline/supplemental exact expressions, zero-input policy, and legacy/manual material. Add the direct payload-only demand regression described above; repair the narrow action/coverage behavior only if that test demonstrates an unsound classification. Do not add a semantic stage, model request, inference mechanism or larger budget.

5. Give the corrected active route/receipt identities appropriate new versions, update current synthetic fixtures and acceptance evidence, and document the measured-versus-corrected distinction. Do not migrate, rewrite, replay again or relabel the original batch. No additional real run is implied.

## Execution boundary

The parent has recorded the required post-batch work in `post-batch-work.json`. All four controllers and their sole zero-call replays must close before any runtime or prompt correction. This audit created only this new verification report. It launched no tests, analyses, models, Skills, probes, controllers or replays.
