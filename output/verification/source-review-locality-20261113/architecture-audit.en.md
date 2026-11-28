# Strict source-review validation with local isolation

This is a read-only architecture audit and implementation proposal. The baseline is the closed shared-v2 GA4 run `document-guided-ga4-review-shared-v2-high-20261112-221242`, accepted implementation `b3eba2da9823ac8a38620d7a5a728d7b8c66b4f3a5fe14fd7980997923330387`. No model call, replay, Skill execution, backend computation, validator execution against the historical candidate or production change was performed for this audit. The new user authorization permits a general fix and offline acceptance, followed by one fresh root-owned GA4 run; the prior run remains immutable.

## Observed failure chain

The final merged review candidate contains 15 ordinary findings, 271 contract checks, no projection checks and three source-input findings. The authored contract statuses are 227 accepted, 43 rejected and one unresolved. These are candidate counts, **not independently validated or reusable decisions**.

All three malformed source-input findings have `kind=missing_field`, `actual.input_index=0` and `actual.path=[]`. All three target the same actual wire operation, `annotation:/ir_semantics/ir_119/segments/0/ops/0`. Two declare action and `rows` output impacts; one declares an action impact. The strict nonempty-path requirement is appropriate and must stay.

The current loss of independent checks happens at several separate boundaries:

1. `document_guided/source_review.py:578` validates the entire `CompletedFragmentSourceReview` with one Pydantic adapter. The three invalid source-input records raise before `checked_contract_checks` or source normalization runs. A successful transport answer therefore never becomes a validated review.
2. `common/structural_correction.py:522` retains the merged `last_candidate`, records structural-invalid validation and raises when the existing one-correction budget is exhausted. It does not accept the invalid candidate. `source_review.py:759` catches that failure but leaves `review=None`; it does not isolate valid records.
3. `document_guided/runner.py:480` permits semantic repair only when review status is `complete`. With `review=None`, neither the 15 candidate findings nor the 43 authored contract rejections can route repair. Their independent validity has not been established.
4. `doe/input_contract_review.py:214` consumes tables only when status is `complete`. Otherwise it deliberately replaces checks, scopes, projections and source findings with empty tables. The receipt still preserves the complete expected inventory, but no individual review decisions survive.
5. `doe/input_contract_scopes.py:144` and `:168` also gate all contract/projection decisions on `core.status == complete`; `InputContracts.accepted` has the same global condition. Changing only the source-review result shape would not enable local consumption.
6. `DemandEngine._source_input_errors` already handles validated native source defects before action/output dependency transfer and preserves conservative dependencies without synthesizing corrected inputs. Losing all source findings also loses that explicit source-defect evidence.

The fix must address these boundaries together. Simply allowing `partial` wherever `complete` is accepted would bypass coverage, reference and conflict validation.

## Recommended separation of decisions

Keep the existing strict whole-response validator and mechanical correction budget. After that budget is exhausted, perform a separate deterministic isolation pass over the exact terminal `ResponseChain.last_candidate`. Never select an earlier candidate because its answers look better. Keep the strict chain terminal status, accepted-call identity, raw response, merged candidate and diagnostics unchanged; a separate partial-review result may expose validated independent material.

The isolation result should distinguish three facts:

- **Authored candidate record:** the original slot and value, bound by pointer and hash.
- **Strictly validated record:** schema, selected-object references, evidence and all applicable consistency rules passed.
- **Effective usability:** a validated record may still be unusable because a located conflicting or unvalidated allegation overlaps its premises.

An invalid record must not be silently removed or converted into a semantic `rejected` or `unresolved` check. Store a validation quarantine record with its exact diagnostics and conservative affected range. This is a representation failure, not a model-established semantic conclusion.

Suggested deterministic result fields are `validated_records`, `record_coverage`, `validation_barriers`, `conflicts`, and exact candidate/material bindings. Every expected obligation and every finite scope remains in the original inventory and receives an effective coverage entry: validated decision, rejected/unresolved authored decision, omitted, duplicated, malformed or blocked by a specified conflict/barrier. A missing check is never acceptance, irrelevance or an invented model reason.

## Strict validation units

Validate the envelope independently: exact supported outcome, expected table names and list types, no forbidden extra keys. An absent or wrongly typed table is not equivalent to an empty table. Invalid JSON, an unsupported outcome or an envelope that cannot be attributed to the selected review material yields no positive review acceptance.

For valid list containers, retain original indices and validate each record independently using the existing schema and contextual checks. Factor the existing checks into reusable helpers if necessary; their allowed values, required fields and rejection conditions must remain identical.

| Section | Required independent validation | Coverage and cross-record checks |
| --- | --- | --- |
| Ordinary findings | Existing finding schema, real target IDs, domain, owner, source spans, Task isolation and finite objection | Duplicate finding detection; all target/prefix conflicts retained |
| Contract checks | Existing `InputContractCheck`, exact obligation and attachment identity, evidence, scope inventory, summary/scoped status consistency | Full expected-obligation ledger, duplicate IDs, exact scope coverage; no projected or shortened saved inventory |
| Projection checks | Existing `InputScopeCheck`, exact projection IDs and evidence | Each expected projection once; paired request/response identity preserved |
| Source-input findings | Existing candidate schema and `normalize_source_input_findings` against actual operation/input coordinates, lexical values, evidence and exact call pairing | Duplicate semantic finding identities and conflicts with claims that the actual operation was mistranscribed |

For a malformed contract row, the smallest immediately safe atomic isolation unit is that obligation, because its summary and exhaustive scope decisions are coupled. Independently validated scope groups can be retained only if their own coordinates and necessary parent rule/interface/decomposition premises pass, with a separate explicit coverage state for the malformed remainder. Do not use a valid-looking `accepted` summary to fill a missing or invalid group. Do not make same-field-name guesses across different output rules.

A refactored strict whole-response validator should call the same record helpers and then enforce every existing global invariant. Isolation calls those helpers and records the failures. It must not call an easier validator or manufacture a reduced inventory merely to make the old exact-coverage validator pass.

## Locating an invalid allegation without accepting it

Use a small, independently validated locator projection strictly for conservative blocking. It is not a normalized source finding and cannot become a semantic error report or an input-demand seed.

1. Resolve an exact `target_id` through `source_operation_targets` using the selected CFG/raw annotation/mapping. Check actual operation type and the exact request/response association. Wire aliases may represent the paired deliver/receive operation, not an arbitrary similar operation.
2. Validate any input index against actual `value_uses`; validate any usable output/action selectors against the native operation. A syntactically valid substring or a free-text reason is not a locator.
3. If the field path is invalid or absent, do not copy `expected.information.path` into it, invent a field, change `missing_field` into `missing_argument`, or replace the path with whole-value acceptance. Bound the uncertainty by the exact actual operation/input and its paired native effects. Narrower selectors require independently validated scope relations; otherwise keep an operation-level barrier.
4. For an unknown or malformed target, use a larger bound only when existing material proves it: a validated real parent/IR location or a validated source-to-operation mapping may establish such a bound. Do not find a target by parsing explanatory prose or matching similar IDs. If no sound local bound is available, record an explicitly unlocated barrier for the affected section/domain; this can block all relevant contracts, with the exact failed reference and required missing information as its reason.

For the observed three findings, one exact wire operation is supplied by all three. After independently verifying that operation and its pairing, the missing field coordinates justify a barrier at that operation's actual input/native effects. They do not justify discarding checks for every other operation. This does **not** establish that all other 268 or 269 checks are valid: every record, duplicate, coverage rule and cross-section conflict still needs validation.

Missing or wrongly typed `source_input_findings`/ordinary-finding sections require explicit section-wide uncertainty. An absent section could conceal defects; treating it as an authored empty list would improperly clear those defects. A malformed individual record with an unlocatable target requires a similarly explicit broader bound. This is a concrete localization failure, not a generic black-box excuse.

## Conflicts and genuine source-defect effects

Preserve the current target-prefix overlap rule between an ordinary CFG/processing finding and an accepted contract. Mark the overlapping decisions unusable with a pairwise conflict entry; keep the validated finding available for the existing semantic repair. Never drop the finding to retain acceptance. Where current contracts lack finer proof, the operation-level conflict still affects the full corresponding contract. Task-correspondence/sensitivity ownership and projection-specific exceptions remain as currently defined.

A valid source-input defect remains a normalized semantic finding, including exact impacts, even when another record is quarantined. It must still reach `SourceInputMismatchIndex`, the native action/output gate in `DemandEngine._source_input_errors`, and `source_input_semantic_findings`/saved-result validation. Accepted necessity contracts do not prove that a broken source operation can produce its claimed native output.

An invalid source-input allegation instead contributes a **validation barrier**. Apply it at native action/output demand processing, including deterministic operations with no input-contract entry. Restricting the new protection to `InputContracts` would let a deterministic operation bypass quarantine. Use the same barrier ranges in deletion-impact/constraint checks and input assessments so an affected field cannot become deletable because its source-defect record failed schema validation. Unaffected uses, versions, fields and paired occurrences remain independent.

When a valid source-input finding conflicts with an ordinary finding that says the operation was mistranscribed, retain both as conflicting evidence at that operation and block their effects. Do not choose which is correct automatically. Generated contract-only repair findings may coexist with valid source defects under the existing exceptions; a rejected dependency claim must not be recast as a source error.

## Repair routing and selection

The shared semantic repair may consume **strictly validated repair findings from a partial review**, with all existing owner/domain/Task-isolation rules. This includes program-generated processing findings from independently validated nonaccepted contract checks. Candidate records, malformed allegations, unsupported owner prose and validation barriers alone must not become semantic objections or consume a new quality-sampling round.

Preserve the existing dependency closure: processing rebuilds correspondence and sensitivity; CFG rebuilds downstream fragments; Task revision remains source-only and rebuilds correspondence. Keep seven normal requests, two workers, one structural correction per stage and the single existing semantic repair round. No per-IR calls, extra review stage or additional retry budget is required.

After a repair, bind any partial/complete rereview only to the newly selected source/CFG/annotation/contract inventory. If repair cannot assemble a candidate and the original selection is retained, use the original matching review receipt. Old acceptance and scope decisions cannot be copied into a new bundle, even when IDs look unchanged. Prior unresolved findings remain historical objections until a properly bound rereview actually confirms their resolution; a partial rereview must not mark the whole repair confirmed.

## Immutable receipts, consumption and replay

Introduce explicit new source-review result/receipt policy identities for isolation. The raw response grammar may remain strict, but its persisted consumption semantics changed; guided-run policy and downstream demand/DOE identities that depend on that material must distinguish the change. The shared-v2 display codec need not change. Do not relabel or migrate old artifacts or use the new result logic to rewrite the closed run.

Seal the complete original inventory, terminal candidate hash, strict validation/correction receipts, exact selected source/CFG/annotation binding, each validated record, each invalid raw-slot reference, complete coverage ledger, conflict pairs and locator/barrier proof. The receipt loader must reconstruct and compare these decisions from the bound material, rather than trusting status flags or an unsigned `usable=true` field. Cryptographic hashes establish identity, not the truth of semantic claims.

`source_review_complete` stays false for any quarantined/omitted/conflicted review material. Local contract/projection access should consult complete per-scope coverage and barriers from the verified receipt, not merely replace the old global `complete` check with `complete or partial`. Whole-contract acceptance also needs all of its own required scopes and parent premises usable.

All replay decisions must reproduce the same terminal merged candidate, isolated records, inventory coverage, conflicts, barriers and selected-bundle binding without model calls. Unknown/old protocol identities are rejected or handled only through their unchanged legacy path. A forged receipt that removes a quarantine entry, changes its scope, drops inventory rows, inserts a check, changes a source/annotation, or reuses a pre-repair review must fail verification.

## Offline acceptance cases

- Three invalid source-input records at one real operation plus valid independent contract checks: preserve full inventory and diagnostics; isolate that operation; do not label invalid records source-semantic errors; unrelated strictly validated checks remain usable.
- The same malformed finding on a deterministic operation: affected native demands and deletion claims remain blocked even without a contract entry.
- Missing table, missing obligation, duplicate obligation, malformed row, duplicate/conflicting scope and unknown target: retain explicit coverage failures; no silent accepted/default-empty result.
- Valid source defect and accepted contract at the same operation: preserve the defect and its action/output effects; another output/use remains independent only with a supported scope distinction.
- Ordinary CFG/processing defect overlapping an accepted check: quarantine only affected acceptance under the existing overlap rule and route the valid repair finding.
- Exact paired tool request/response mapping: do not collapse occurrences or let a request-only/response-only alias clear the other affected side.
- Partial review with valid repair findings: existing one repair round and dependency closure run; invalid-only review does not add a model call. New annotations reject old review bindings.
- Forged or incomplete local receipts, stale identities, missing quarantine records and altered barrier ranges fail immutable loading and zero-call replay comparison.
- General missing-field diagnostics identify the real missing child under its owning record, preserving raw validator provenance and correcting only the existing record slot; nonempty-path semantics are never relaxed.

This proposal establishes a route for retaining validated independent evidence. It does not pre-approve the closed GA4 candidate, prove natural-language review correctness, or predict deletable-field counts for a future run.
