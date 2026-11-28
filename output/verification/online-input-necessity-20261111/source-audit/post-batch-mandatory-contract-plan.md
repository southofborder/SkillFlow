# Post-batch mandatory input-contract validation plan

Status: DESIGN ONLY. Production, prompts, transport and renderer remain frozen across the authorized four-case queue and sole replays. This note authorizes no implementation, model call, probe or replay. Implement only after all four controllers/replays close and the parent confirms the follow-up scope.

## Observed gap

The initial GA4 processing artifact has 109 `call` operations, including 13 direct remote operations, but no `input_contract`. It has 45 supplied compute transfers. Source review checks the supplied contract inventory, so a complete review of those 45 entries cannot establish that expected tool contracts exist.

Current code permits this: `document_guided/annotation_wire.py:95-102` makes `FlatCall.input_contract` optional; `propagation/contracts/input_requirements.py:190-227` normalizes only supplied attachments and skips missing fields at lines 204-205. Guided validation calls that normalizer at `annotation_wire.py:727-733`. This is distinct from semantic disagreement about a supplied contract.

## Minimal implementation recommendation

Add a deterministic obligation enumerator beside `normalize_input_contracts` in `propagation/contracts/input_requirements.py`:

`expected_input_contract_obligations(targets, locations, *, exact_expression_targets)`

Each item records operation kind, instruction ID, exact operation path/pointer, actual input count, expected attachment field, and request-pair/scope identity where applicable. Derive it from the selected, validated operation target index and location kinds. Never use Task, actual demand, sensitivity or current payload contents to decide whether an obligation exists.

Add a separate strict guided-route check such as:

`validate_required_input_contract_coverage(obligations, supplied_contracts)`

Apply it after ordinary syntax/reference validation and exact expression-target resolution, before accepting the processing fragment. Missing attachments produce pointer-local structural diagnostics owned by processing and use the existing correction/repair budget. They do not silently become accepted empty contracts, independent remainders, whole-value requirements or global opacity gaps. If semantics cannot be established, the author must supply the existing typed, source-backed unresolved row or a legitimate unmodeled processing gap for the affected instruction. A gap must state the concrete missing fact.

Enumerate opaque `compute` operations without a supported exact expression, and every actual tool/remote boundary produced by `call` lowering or authored as `deliver`/`receive`. Preserve cases, nested loops and local scopes. Paired request/response operations keep one logical interface obligation with exact coverage of both physical attachments; the existing equality check still applies. Storage/runtime-context reads and writes are not automatically tool obligations.

Require explicit contracts even for zero-input tool calls: `inputs: []` plus source/interface reason and evidence. This states that there are no declared request operands to classify. It does not certify the absence of hidden reads, implicit receiver state, cache effects or incorrect graph abstraction. Those remain source-review concerns. Omitting an entire argument also cannot be represented by inventing an actual-input row.

## Expression exemption

Inline compute expressions are exact operation supplements. Top-level expression supplements can address broader instruction/control targets; one such supplement must not exempt every compute nested in that instruction. Resolve validated supplements using existing target identities. Exempt a compute only when the existing resolver proves that the supplement supplies that same operation/output relation. `annotation_wire.py:811-840` already distinguishes exact inline operation coordinates; `contracts/joint.py:135-147` normalizes inline and top-level expressions. Reuse that resolution instead of matching by instruction ID alone.

## Guarantee and limits

The small fix guarantees that every eligible selected operation has an explicit contract obligation accounted for. It does not prove source semantics, output-rule completeness, every possible future child selector, or minimum data. Retain exact selector matching: a whole-value row does not match a narrower child. Do not infer closed decomposition from several rules. `output_parts` remains an explicit reviewed assertion.

The initial 45 compute contracts demonstrate why these guarantees must be separate: all have one rule and no `output_parts`; some composite values have only whole-output rows, and three error constructors cover only `message`. Mandatory presence alone cannot resolve those limitations. Tightening whole-output accounting is a separate decision, not silently part of this presence patch.

The existing `InputRequirementGap.concrete_barrier` check at `input_requirements.py:38-59` removes common generic prefixes and rejects a small exact set of generic phrases. It is a lexical floor, not a semantic-specificity proof. Review must decide whether a concrete missing fact actually blocks the named input/output scope. A follow-up review schema may reuse the gap object with reference-checked affected selectors; do not claim text validation proves the explanation.

## Review receipt and source mistakes

The review agent should bind the expected obligation inventory as well as supplied contracts into a new receipt version. Review checks cannot be vacuously complete when an expected contract is absent. Unaffected scopes should not be inferred accepted merely because an unresolved scope is omitted; scope-specific acceptance needs explicit review coverage.

Keep source mistakes separate from annotation defects. A source-backed missing required argument, missing field or wrong-field selection belongs in the separate proposed `source_input_findings` table, with requirement evidence, actual-occurrence evidence and scoped action/output impact. Existing actual-input contracts still account for real operands only. A rejected semantic contract is not by itself a source bug and must not automatically rewrite the CFG/source or create a Task requirement. This separation is coordinated with the review and constraint agents' design notes.

## Identity and compatibility

The current identities are flat annotation v4, fragments v4, document-guided run v10, document step/annotation v9, processing compiler v13 and security profile v22. The source-review fragment is v3. Bump current guided wire/fragments/run/step/annotation identities for tightened acceptance and bump the review/receipt identity when expected inventory is serialized or bound. Bump compiler/profile only if their compiled representation or meaning changes; do not edit frozen historical manifests. Keep legacy standalone optional parsing explicitly compatible unless the parent chooses a separate migration.

## Focused offline validation after the freeze

Use synthetic cases only: missing tool contract with nonempty inputs; explicit zero-input contract; paired request/receive mismatch; missing opaque-compute transfer; exact inline and top-level expression exemption; an instruction-level expression that must not exempt another nested compute; nested case/loop scope and same request ID in different scopes; local storage exclusion; typed unresolved contracts; omitted whole argument reported separately without mutating actual inputs; forged/omitted expected inventory in receipt; legacy standalone compatibility. These tests must verify acceptance/diagnostic semantics, not merely mirror the enumerator.

No test or model run was executed for this plan. No production file was changed.
