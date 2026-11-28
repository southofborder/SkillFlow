# Source-review locality regression plan

This is a read-only design plan. No production/test changes, model requests, Skill execution, validator/backend run or historical replay were performed for this plan. Root will choose the interfaces and assign implementation/tests. Tests must exercise generic operation/field scopes rather than GA4-specific names.

## Concrete closed-run failure evidence

Evidence belongs to the closed run `experiments/doe/runs/document-guided-ga4-review-shared-v2-high-20261112-221242`; it is a regression source, not a reusable accepted answer for a new experiment.

| Saved record | First response | Sole correction's merged candidate | Intended source claim and impacts |
|---|---|---|---|
| `/source_input_findings/0` | `kind=missing_field`, `actual.kind=absent_argument` | `actual={kind:input_range,input_index:0,path:[]}` | A request filter derived from `options.filters`; semantic `source_role`, unknown SDK encoding; action and output `rows` |
| `/source_input_findings/1` | Same discriminator mismatch | Same empty actual path | Ordering derived from `options.orderBy`; semantic `source_role`, unknown SDK encoding; action and output `rows` |
| `/source_input_findings/2` | Same discriminator mismatch | Same empty actual path | Named `limit`, expected information path `["limit"]`; action only; zero is omitted by the source truthiness spread, while the SDK's treatment of zero is explicitly unresolved |

All three target `annotation:/ir_semantics/ir_119/segments/0/ops/0`. The correction replaced only these three records. The merged candidate still held 15 ordinary findings and 271 contract checks. The stage rejected all three at their own record paths and produced `structural_failure`, no accepted review and no semantic repair. The 271 checks are preserved candidates, **not 271 established valid decisions**: inventory, evidence and overlapping-finding consistency must still be checked independently.

The saved original prompt's `ActualInputRange` definition permits an empty array syntactically. Its prose permits an existing actual range or explicit `absent_argument`, without stating the conditional missing-field/nonempty-path rule. That rule lives in `SourceInputFindingCandidate.actual_not_invented`; the initial prompt does not contain its diagnostic sentence. The correction supplies that diagnostic but the two semantic source roles cannot acquire a concrete SDK field name from these citations alone. This is both a schema/guidance regression and a locator expressiveness case; tests must not fix it by guessing a request key or accepting the malformed old representation.

Evidence paths relative to the closed run's `review/`:

- `prompt.txt`: SHA-256 `0b3e56a7e4fe121c40da417a23977eaa650bc83363c4d81bbcf7310deb9ef085`.
- `calls/review/a001/response.json`: `7fa702ae4bd4bad8a19ec8279e52ed60cb2b7f7bd69c87dd1ff504cd9158d77a`.
- `calls/review/a002/response.json`: `55b2abab53ece2d4f2887098ec106c9e28ef1b68c2640ec174c986b4dcc1d914`.
- `calls/review/a002/merged-candidate.json`: `c75245b12f6b8bee195019bf668f08002a50b570c9bc98607fe6d591c6a94a14`.
- `calls/review/a002/validation.json`: `2af64587f458d7164bf2ce76e6929fdb58bc8b70c98a89bbf9a4120f350309c0`.

Use small authored synthetic fixtures mirroring those two response shapes and three distinct semantics. Do not replay the closed run to obtain test outcomes or treat the third claim's SDK semantics as proven.

## Existing reusable coverage and boundaries

- `tests/doe/test_source_input_findings.py`: actual operand versus absent argument, missing child location, invalid source/slot/parent/literal, paired request/action and response/output mapping, source-error/representation-error conflicts, no invented inputs and no demand seeds, disjoint output independence.
- `tests/doe/test_input_contract_scopes.py`: mandatory obligation inventory, exact finite scope partitions, concrete gaps, accepted local scopes alongside unresolved remainder, explicit wide-gap impacts, paired projection decisions, request rejection independent from response at a shared wire parent.
- `tests/doe/test_input_contract_review.py`: complete selected-bundle binding, receipt completion tampering, source/evidence/contract coverage, source errors separate from contract repair, overlapping representation findings versus unrelated accepted contracts.
- `tests/doe/test_reviewed_input_necessity.py`: field-specific output rules, independence without erasing actual reads, multiple consumers, rejected/unreviewed contracts cannot authorize deletion, scoped uncertainty and partial review.
- `tests/common/test_record_correction.py`: one correction, immutable raw answer and merged candidate, `ResponseChain.last_candidate` after exhaustion, rejected/empty replacements retain earlier candidate, read-only replay, changed-candidate/strategy rejection.
- `tests/document_guided/test_typed_record_correction.py`: review record/outcome correction without modifying other records; existing replacement grammar and replay identity.
- `tests/document_guided/test_input_contract_review_flow.py` and `test_parallel_runner.py`: selected-review sealing, dependency-closure repair, seven normal requests, two-worker barriers, Task/mapping/sensitivity isolation and injected zero-call replay.
- `tests/document_guided/test_shared_source_review.py`: complete source and contract delivery, original target coordinates, adaptive display and exact request limit; retain this coverage when prompt guidance changes.

Current failure boundaries to change deliberately: whole response schema validation precedes all table validation; the exhausted review handler records no `review`; `_build_core` accepts scopes only for status `complete`; `reviewed_contract_scopes` also requires a complete core. A partial/local result needs explicit protocol support across these consumers, not an exception swallowed in one layer.

## Focused acceptance matrix

1. **Strict, explicit locator variants.** Missing whole argument, known missing member path, and source-established logical member with unknown wire spelling must have unambiguous representations. Both historical malformed forms remain rejected. A known field requires its nonempty missing-member path; a semantic locator must bind an existing exact operand/container and separately evidenced logical role, never silently equate root `[]` with a known missing field. Preserve nested fields, integer/each paths, optional parents, source quotations and language. Reject invalid slots, parent operation targets, cross-operation aliases, fabricated lexical values, contradictory locator variants and missing evidence. Do not require the missing child to exist; validate the actual enclosing operand/reference.

2. **Guidance matches validation.** Render the new union/discriminators and cardinality restrictions in the schema, explain each cross-field rule in prompt guidance, and show a minimal valid example for each variant. Assert that a source role does not require an invented SDK parameter. The correction diagnostic must identify the faulty source-finding record/locator, not misattribute normalization errors to `/input_contract_checks`. The `limit` example must distinguish established omission from unresolved recipient semantics. Include arbitrary names, Unicode source and nested containers.

3. **Local failure preserves only independently valid material.** In one synthetic response, combine valid ordinary findings, valid contracts/projections, valid source findings and two malformed source findings. After the existing one correction is exhausted, retain original answers and the exact final merged candidate, reject the malformed rows, and publish explicit record-level diagnostics. Independently validate surviving tables/records before sealing any scope. Do not declare the complete source review successful. A valid source finding remains a source error; malformed records become evidenced validation barriers, never fabricated source errors or semantic acceptances.

4. **Locality inside one IR and one paired call.** Build a two-output compute (`x`/`y`) plus another operation in the same IR and an unrelated IR. A malformed, nevertheless locatable source claim affecting output `y` must block the corresponding transfer/deletion conclusions while `x` and the distinct operation remain usable when their independence is established. Test action-only, output-only, action+output, whole output, nested field/presence/cardinality and request/response pair variants. A shared wire call parent must not collapse independently reviewed request and response obligations. Another needed consumer of the same actual input still retains that input. Native side effects must remain protected even with no output demand.

5. **Unavailable locality never disappears.** Invalid/missing target, nonexistent input, malformed impact, malformed source-finding table or unparsable candidate must produce a concrete diagnostic identifying what could not be bound and why it prevents a narrower judgment. Use only independently validated target/impact fragments to bound effects; when exact localization is unavailable, preserve an explicitly scoped conservative review/material barrier. Do not discard an unlocatable row and then report all source input ranges accepted. A visible known target with unknown field spelling is different from a nonexistent target. Two invalid records may not overwrite one another's barriers.

6. **No weakened inventory or conflict checks.** Omit, duplicate or forge obligation/scope/projection IDs; mismatch contract IDs; change source spans; omit the entire table; contradict an accepted scope with an overlapping CFG/processing finding; mix unknown keys/types. Missing or invalid inventory members never become accepted by default. Keep the original complete inventory in partial receipts and report its actual unreviewed ranges. Source errors cannot assert faithful actual operands while ordinary findings say the same use is mistranscribed. Projection capability acceptance remains separate from input necessity.

7. **Receipt and replay integrity.** Bind partial decisions, rejected-record diagnostics, scope barriers and original candidate identity to the same selected source/CFG/Task/annotation/mapping/inventory and exact review chain. Tampering with any of them, changing review completeness independently, reusing pre-repair material, or replacing candidate/diagnostic hashes must fail. An unchanged saved synthetic run reproduces the same local decisions with zero calls and byte-identical raw answers. Old protocol fixtures retain their previous behavior/identity; no migration or new conclusion is written into historical artifacts. The new locator/partial-review identities must be explicit wherever their semantics are consumed.

8. **Backend consequences, not only schema acceptance.** With an independently accepted `a.a,b.b` relation and unused `c.c`, prove `c.c` remains deletable despite a disjoint malformed source finding, while an overlapping malformed claim prevents deletion only within its supported affected range. Check field and whole-slot modification types, actual forward reads/observations unchanged, no invented arguments/data/seeds, no accidental acquisition projection, action/constraint preservation, and the same final findings for FIFO/LIFO. Known valid missing/wrong source input remains an error rather than an unresolved validation record.

9. **Unchanged model-call architecture.** Use injected responses for one clean seven-request/two-worker integration and one persistently malformed review with exactly one structural correction (`a001`,`a002`, no `a003`). Local extraction/validation adds zero semantic calls. If existing ordinary findings trigger semantic repair, preserve the current one-round dependency closure, shared budget, Task source-only objection projection and isolated processing/mapping/sensitivity inputs. Changed processing invalidates old contract review identity. Reusing an already saved result must never create a client.

## Execution and evidence policy

After design/ownership approval, first run the focused new locator/locality tests, then affected receipt/demand/correction/runner suites. Preserve initial failing receipts and exact corrective reruns under this verification directory. A final injected integration must use the frozen accepted implementation and current identities. Report distinct scoped cases and limitations without calling a union of runs a whole-repository all-green execution. Only root may prepare and dispatch the separately authorized single fresh GA4 after offline acceptance; no historical run, Skill execution or extra model probe is part of these regressions.
