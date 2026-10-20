# Case 010 initial annotation audit

This is an assistant review of the frozen source, accepted initial Task, structurally invalid annotation response a001, and the subsequently accepted structural correction a002. Acceptance here means structural acceptance before semantic review; a002 is not yet the final selected candidate. No production source, prompt, candidate, or running request was changed; this audit used no API.

## Source and Task

The [new Task](../cases/010/task/task.json) has nine requirements. Comparison with the three frozen source files found no concrete omitted operational requirement:

- Exactly one index search using the original term.
- Both optional parameters retain their original values when present and are omitted when missing, including the settings in `query.yaml`.
- The global `index.delete` prohibition remains R7.
- The response total is saved after the search, and response items are returned unchanged.

The fuzzy-matching capability is not promoted to a requested action. The source's clarification that parameter descriptions do not request validation or normalization remains in source accounting. This bounded inspection does not prove Task completeness.

## Why a001 was rejected

The [saved response](../cases/010/annotation/calls/annotation/a001/response.json) and [mechanical diagnostics](../cases/010/annotation/calls/annotation/a001/validation.json) distinguish two different questions.

**The processing relationship already exists.**

| Candidate location | Existing relationship |
|---|---|
| `ir_004/events/0/events/0/atomic_ops` | Selects the original `from_date` and computes `present(field(...,"from_date"))` separately. |
| `ir_005/events/0/events/0/atomic_ops` | Selects the original `limit` and computes its presence separately. |
| `ir_007/events/0/events/0/atomic_ops/0` | Builds `query` unconditionally; the optional members use their original value inputs with separate `when` controls. |
| `ir_007/events/0/events/1/atomic_ops` | `deliver` and `receive` both reference the same `search_request` local. Presence controls are not request members. |

**The per-requirement executable declaration is missing.**

R4 and R6 are the two omission requirements. Their realizations at `/realizations/3` and `/realizations/5` claim `status="expressed"`, with general CFG bindings and no gaps. Neither requirement ID appears on a positive demand or supported constraint. The `realization_seed` rejection is therefore an inconsistency between their declared expression status and executable requirement accounting. It does not mean the candidate omitted the conditional build.

This distinction matters: adding a field-selection operation, replacing a value with null, or forcing a whole-request demand would not follow from these diagnostics. General graph correspondence and actual processing alone do not establish the per-requirement demand declaration.

## Other observed relationships

The delivery has content demands at its actual input for `query`, `from_date`, and `limit`, linked respectively to R2, R3, and R5. The local write has both an action demand and an actual write-input value demand linked to R8. The ordinary return has a real CFG input demand for R9. These are concrete improvements over an upstream-only or action-only description, subject to later review and computation.

R7 remains `retained_only` with an explicit gap: the current CFG contains no deletion event, and the candidate does not invent one to attach a restriction. That gap must remain visible downstream; it does not establish that deletion is possible or that the prohibition has been exhaustively checked.

## Separate optional-value concern for later review

The optional receiver-value demands for R3 and R5 also supply `expected` references to the optional raw input values. The current [shared format rule](../../../../../src/skillflow/propagation/contracts/format_instructions.py) says that an independent expected-source demand does not inherit `build.when`; when explicit field selection and conditional construction already preserve the original value, redundant expected references should be omitted.

Accordingly, the presence of a correct conditional build alone is insufficient to conclude that these demands handle absence correctly. The accepted candidate and its derivation must be checked for unconditional expected-source retention or binding limitations. This is a semantic/analysis concern separate from the two mechanical `realization_seed` errors; this audit does not modify the model response or preempt the independent review.

## Pending

### Accepted a002 update

The [a002 response](../cases/010/annotation/calls/annotation/a002/response.json) changes exactly one area of the raw model response: it adds two demands to the existing request `build` operation:

- R4: output `presence`, path `["from_date"]`.
- R6: output `presence`, path `["limit"]`.

No processing operation, delivery seed, restriction, sensitivity declaration, or Task requirement changed between a001 and a002. The normalized saved annotation additionally contains ordinary schema defaults; these defaults are not extra model edits.

This resolves the mechanical realization-accounting errors. The two new seeds are still **upstream build-output** demands, not receiver-input demands. The final derivation must show what each requirement establishes at the actual delivery; an upstream seed does not automatically spread forward to that boundary. Other receiver-value requirements may also preserve build controls, so this audit does not infer the aggregate omission behavior solely from the seed placement.

The optional R3/R5 `expected` references remain unchanged. In the current demand engine, `_seed_expected` emits a `required_original_value` demand at each expected source independently; `_build` separately handles member conditions. The model therefore has not removed the previously identified redundant expected-source concern.

The accepted initial candidate also contains:

- R2: a positive delivery action and `at_most(...,limit=1,unit="attempt")`.
- R8: actual write action and payload value demands, with `requires_prior(search,write)`.
- R7: the retained deletion-prohibition gap.
- No sensitivity declarations. This does not establish that all possible contents are nonsensitive; no unmentioned sensitive response field should be invented.

Await the final selected candidate, semantic review/repair outcome, propagated records, demand derivations, and DOE result. Compare the same obligations and slots again rather than assuming that a structural correction preserved every relationship listed above.
