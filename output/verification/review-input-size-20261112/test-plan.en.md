# Offline test plan for complete source-review delivery

This is a read-only design review, before the presentation design is selected. It does not authorize a model call, Skill execution, historical replay, production edit or test change. The parent owns implementation and the single fresh GA4 dispatch after acceptance.

## Existing behavior and identity boundaries

Current `runner.IDENTITY` is `skillflow-document-guided-run-v11`; `POLICY.review_protocol` and the source-review default are `compact-v1`. The fragment review identity is `skillflow-document-source-review-fragment-v4`. Saved review inputs contain the complete local material, `prompt_view`, binding and inventory; their material hash, exact prompt hash, producer manifest and policy are checked on reload. The response-chain identity also binds its actual base prompt.

Use a new explicit presentation identity for changed model delivery, and a new guided-run policy/identity. Retain exact rendering of saved `compact-v1` and absent-view legacy materials. Simply changing the `COMPACT_VIEW` constant would also alter compact target-error diagnostics and request-failure continuation/replay handling, because those paths compare directly against the constant. Both supported compact generations must retain their appropriate behavior. An unknown view must fail closed.

If only delivery representation changes, Task v5, annotation, compiled contracts, demand/DOE and source-input finding semantics need not acquire new identities. If the saved review-material/result schema itself changes, give that schema a new identity as well; do not reuse a former identity with incompatible content. Keep the mandatory review inventory/check and immutable binding semantics unchanged. Historical artifacts remain untouched and are never relabeled as having used the new representation.

## Required regression cases

| Case | Meaningful assertions |
| --- | --- |
| Complete source preservation | Every file name and complete text survives, including CRLF, trailing newlines, empty lines, multilingual/non-BMP characters, quotes, marker-like text, and source containing candidate reference syntax. Compare exact UTF-8 bytes or exact decoded strings, not substring presence alone. The complete source section remains available without a model fetch/tool step. |
| Logical material round trip | For a factored representation, reconstruct the previous semantic display payload exactly and compare full objects/canonical digests. Include Task, CFG, annotation, observations, runtime rules, gaps, failures, availability, complete/partial fragments and all contract inventory fields. Ensure input material is not mutated. |
| Every contract occurrence retained | Match all obligation IDs, contract IDs, actual input slots, output selectors, information properties, scope IDs, remainders, unresolved ranges, evidence reasons/spans, request/response links, acquisition projections and target IDs. Identical bodies may share display definitions, but physical request/response obligations and separate occurrence identities must remain separate. |
| Distinct near-duplicates | Contracts differing only by a field, condition, version, receiver, `if_present`, literal value, evidence span/reason, or paired request must reconstruct distinctly. Equality must be structural/type-aware: `false` differs from `0`, `1` from `1.0` when exact JSON representation is relevant, and ordering of lists must remain intact. Do not infer sameness from names or hashes alone. |
| Literal/reference ambiguity | Large repeated literals may contain strings/objects identical to the proposed reference syntax, including dictionaries with `$ref`, `ref`, `id`, or presentation-envelope keys. They remain literal data. Explicit encoding tags or an unambiguous path table must distinguish genuine representation references from original content. Invalid, missing, cyclic or extra definitions fail closed if a public decoder is introduced. |
| Complete and partial review | Cover complete annotation, missing annotation with available processing/sensitivity/mapping fragments, failed-stage targets, unmodeled source gaps and validation-origin gaps. No absent object becomes an empty fabricated object. Available original fragments remain inspectable. |
| Original finding coordinates | Resolve findings against original annotation/fragment JSON pointers, including escaped `/` and `~` names, nested cases and loop bodies, parent targets and compiler observations. Presentation definitions must not become repair targets. The actual owner remains processing/task-correspondence/sensitivity; unknown targets still report only a valid nearest parent. |
| Contract check coverage | The new prompt still exposes all mandatory inventory entries/scopes. Omitted, duplicate or invented checks/scopes, stale contract IDs, invalid source references and generic unresolved reasons remain rejected. Empty findings never substitutes for contract coverage. |
| Review correction | A bounded record replacement for one invalid finding preserves the compact base delivery and source completeness, without expanding every saved local target again. Validate repair ownership and the final accepted check receipt; rejected initial output remains recorded. |
| Determinism and replay | Identical logical input yields identical presentation, independent of dictionary insertion order where the existing canonical format promises this. Fresh injected review recording plus its one zero-call replay matches, with unchanged saved answers/materials. Synthetic old-view reviews preserve the original exact prompt semantics. No historical run is replayed. |
| Exact delivery bound | Measure `ENVELOPE + prompt`, using Unicode codepoints as the existing transport does. Keep tests at limit minus one, exactly limit, and limit plus one; source remains complete and over-limit requests produce the existing pre-start rejection, with zero native starts. Do not raise the transport cap or change retry behavior to make the regression pass. |
| Frozen GA4 measurement | Read the rejected request and saved material as immutable evidence, without resuming/replaying analysis. Verify its recorded 1,079,505 characters, render the new view offline, show section/field savings, and demonstrate the complete new delivery is below 1,048,576 with its measured margin. Compare reconstructed semantic payload, all 16 source files, all 344 obligations and all scoped descriptors. Save new measurements under this verification directory, not the old run. |
| Seven-call integration | Use injected responses for exactly Task, flow, CFG, processing, mapping, sensitivity and review. Verify two-worker dependency barriers, Task/source and mapping/sensitivity isolation, unchanged correction/shared-repair budgets, complete propagation/DOE on the synthetic supported case, and zero-call replay. The review response must be generated from the actual delivered inventory after decoding the new presentation, so omission cannot pass vacuously. |

The literal, near-duplicate and occurrence checks are semantic-preservation checks rather than tests that merely mirror a recursive implementation. A size reduction by itself is not acceptance. A deterministic decoder alone also does not prove that a model will follow the new representation; the authorized fresh GA4 run remains a separate online observation.

## Existing tests to reuse or extend

- `tests/document_guided/test_compact_source_review.py`: generic count-scaled material preservation; multilingual source; full/partial case coordinates; nearest-parent-only diagnostics; bounded record correction; typed request failures; old-view behavior and zero-call review replay.
- `tests/document_guided/test_source_review.py`: observation wire coordinates, fragment ownership, unavailable stages, partial fragments, source-reference validation, Task objection isolation and review lifecycle.
- `tests/document_guided/test_input_contract_review_flow.py`: processing-owned rejection, dependency-closure rebuild, changed contract identities, selected immutable review receipt and zero-call full replay.
- `tests/document_guided/test_input_contract_completeness.py`: mandatory tool/opaque-compute inventory, exact-expression exceptions, loop scope, unresolved range and acquisition relation coverage.
- `tests/doe/test_input_contract_scopes.py` and `test_input_contract_review.py`: complete nonaccepted scope partitioning, no vacuous missing-contract acceptance, stale identities, exact original source findings and evidence, paired acquisition projections.
- `tests/document_guided/test_parallel_runner.py`: seven injected requests, two-worker concurrency barriers, true deterministic backend, isolation canaries and no-client replay; prefer extending this Harness rather than creating another orchestration layer.
- `tests/document_guided/test_runner.py`, `test_runner_recovery.py`, `test_parallel_recovery.py`: terminal states, bounded repairs, recording boundaries, preservation of request-failure continuation and no extra calls.
- `tests/document_guided/test_client.py` and `test_transport.py`: complete envelope length, codepoint rather than byte/token measurement, exact source retention, pre-start rejection and saved-answer reuse. These should remain valid without changing the transport limit.
- `tests/common/test_prompt_format.py`: only required if the shared formatter changes; otherwise keep its existing schema-field/constraint/default preservation intact and avoid broad unrelated prompt churn.

Seven existing helpers/tests extract `INPUT_JSON` directly: `tests/doe/input_review_helpers.py`, `tests/doe/test_input_contract_scopes.py`, and document-guided `test_compact_source_review.py`, `test_input_contract_review_flow.py`, `test_parallel_runner.py`, `test_source_review.py`, `test_small_alignment_v9.py`. If the JSON payload gains a representation envelope, use one explicit presentation decoder for injected clients; keep at least one independent reconstruction assertion against expected logical data rather than trusting the encoder and decoder together without a reference fixture.

Explicit current identity assertions occur in `test_alignment_v9_orchestration.py` and `test_runner.py`. Update only assertions for new runs. Add preserved old-view expectations, rather than rewriting old fixtures to new labels.

## Suggested acceptance execution order

1. New focused representation/preservation and original-coordinate tests.
2. Existing compact-review/source-review and contract-scope/review tests, plus transport boundary checks.
3. Existing injected seven-call/full lifecycle and repair-route tests.
4. Independent immutable GA4 delivery measurement and complete-content audit against the rejected material.
5. Freeze accepted production/prompts/transport identity and record the single new GA4 run before root dispatches it.

Keep initial failures and exact corrective rerun receipts. Report the union of scoped tests accurately, without calling it a whole-repository all-green execution. Do not launch models, replay historical runs or execute Skills during offline acceptance.
# Generic adaptive delivery coverage

The shared-v2 display is a general presentation change, not a GA4-specific rule. New synthetic tests vary record counts (including zero and one), Skill/file/IR names and Unicode names, repeated exact values and near-duplicates, and complete/partial review materials. Logical object insertion order and every original occurrence remain intact. The display codec may retain its fixed marked envelope on tiny values; the production renderer chooses that envelope only when its complete encoded JSON plus explanatory legend is shorter than the ordinary logical JSON. The decision uses serialized size, never a Skill identity or record-count threshold.

An irreducible literal at each complete adapter boundary (-1, exact limit, +1) verifies that shared-v2 keeps the identical ordinary review prompt, source and material. The first two requests use fake processes only; the oversize case is rejected before any process starts, retains the complete rejected prompt, and does not retry or truncate. The measured GA4 request is a separate concrete regression for this generic mechanism, not evidence that arbitrary full Skills must fit the finite adapter limit.

