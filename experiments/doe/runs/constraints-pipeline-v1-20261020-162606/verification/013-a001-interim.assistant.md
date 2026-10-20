# Case 013: interim review of invalid annotation a001

This external assistant note reviews only the completed first annotation candidate. It is not a model input, corrected annotation, accepted result, or DOE verdict. The candidate failed structural validation; a later correction must be assessed independently. No source, frozen input, call record, or candidate was edited, and no remote call was made for this review.

Evidence: [candidate response](../cases/013/annotation/calls/annotation/a001/response.json), [saved validation](../cases/013/annotation/calls/annotation/a001/validation.json), [Task](../cases/013/task/task.json), [source](../cases/013/inputs/package/SKILL.md), and [independent checklist](source-obligations.assistant.md).

## Recorded structural result

The saved validation reports 12 `validate_ref` diagnostics. Cross-IR values are incorrectly named as locals in the presence computation (`ir_005`), response classification/extraction (`ir_009`, `ir_013`, `ir_017`), and four status writes (`ir_019`, `ir_021`, `ir_023`, `ir_025`). Those locals are not defined in their receiving IR frames. The diagnostics are binding failures, not evidence that the intended source workflow uses unavailable future values.

The candidate contains 24 raw demands, 16 constraint declarations, and one sensitivity declaration. All 16 realizations claim `expressed`, with empty gaps. These are counts and claims in an invalid response; no compiled goals, propagated demand coverage, constraint checks, or accepted reductions follow from them.

## Positive demands and sensitivity

The endpoint declarations include useful distinctions:

- Each preferred call has an action demand and separate exact-value demands for its `source_id` and `FAST_KEY` delivery inputs. The original IR inputs are used as expected values.
- Archive delivery has an action demand owned by R7 and an exact `source_id` input demand owned by R9. Its raw delivery contains one input. This does not, by itself, prove the exclusive-argument restriction or all conditional action obligations.
- Three successful returns preserve the corresponding response body; the failure return preserves the archive error.
- Each of the four status writes has both an action demand and a payload-value demand owned by R16. The write modes are `append`. Their current input references are among the recorded structural failures.
- Acquisition demands preserve the selected source ID and key; two truth demands cover key presence and transient first failure.

R14 and R15 own no positive demands. Their prohibitions do not manufacture a key-preservation seed. R2 and the preferred-call requirements legitimately own positive key demands for different purposes. This syntactic separation still needs accepted compilation and per-seed propagation before making an analysis claim.

The sole sensitivity declaration marks the selected `ir_003` local `fast_key` as a credential value. It is grounded in the credential-gated purpose and disclosure prohibition. No unrelated field is invented. This is one source declaration, not a measured exposure or proof about subsequent plaintext containment.

## Constraint correspondence and remaining concerns

All declarations use task scope; the pinned workflow has separate, acyclic first-attempt and retry sites. Counts select only delivery operations, avoiding request/receive double counting. The retry and archive attempt limits are each one. Four separate precedence rules correctly pair each status-write site with its own terminal return, without requiring all four branch-alternative writes in one invocation.

The following concerns are independent of the 12 diagnostics already recorded:

1. **Retry expression binding is missing.** R5 and R6 reference `ir_009` atomic computation 1's output as their `only_if` condition. That computation has inputs and a derived dependency but no normalized expression; the top-level expression list is empty. A computation's name or explanatory reason is not the required Boolean expression binding. This is a direct inspection of the invalid response, not an additional saved validator outcome.
2. **Presence-to-edge correlation is not expressed.** R3 and R4 both restrict the first preferred delivery with the presence output from `ir_005`. Its computation includes a `present` expression, but uses the undefined local reported by validation. No normalized edge expressions connect that predicate to the present/absent branches. The checker treats an unexpressed branch predicate nondeterministically; it cannot infer predicate truth from English edge text. No baseline status was computed here.
3. **R11 starts too late.** Its three `forbid_after` triggers are the terminal success returns. The source prohibits further fetches starting at success, before those returns. The selected triggers do not cover that interval; no outgoing execution follows a terminal return. The existing graph's success branches can separately support an ordering argument, but these declarations alone do not justify the claimed complete realization.
4. **R15 narrows diagnostics to the status file.** Its receiver set contains only `status_file`. The response does not explain whether the returned archive error is diagnostic output or how every diagnostic boundary is accounted for. The source does not settle this classification automatically; the empty gap list is stronger than the supplied account.

R13 uses unconditional archive-result classification as its no-further-archive trigger. That is broader than archive failure alone, but the combined Task also requires archive at most once and prohibits further fetches after success. It is therefore not independently contradictory to the full Task; it should not be described as a failure-specific trigger.

The candidate avoids an archive guard that would require unavailable first-attempt or retry outcomes on the key-absent path. Its archive obligation instead relies on CFG bindings and the actual delivery demand. That leaves source-faithful routing and the missing R4-owned positive action account for whole-chain review; it is not evidence of complete constraint preservation.

The structural correction may change these declarations. This note supplies interim development evidence only and must not be substituted for review of the finally selected annotation and actual deterministic results.
