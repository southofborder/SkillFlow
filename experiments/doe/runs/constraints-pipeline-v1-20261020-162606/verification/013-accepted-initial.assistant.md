# Case 013: review of the accepted initial annotation

This external assistant assessment concerns the initial annotation accepted from `calls/annotation/a003`. It does not assume that semantic review will select this annotation, and it does not report propagation, baseline constraint statuses, or DOE results. The assessment was made without remote calls or edits to source, inputs, annotations, or pipeline records.

Evidence: [source](../cases/013/inputs/package/SKILL.md), [Task](../cases/013/task/task.json), [annotation result](../cases/013/annotation/result.json), [a003 validation](../cases/013/annotation/calls/annotation/a003/validation.json), [accepted raw annotation](../cases/013/annotation/audit/raw-annotation.json), and [compiled response](../cases/013/annotation/audit/compiled-response.json). The [earlier a001 note](013-a001-interim.assistant.md) describes an invalid predecessor, not the current reference state.

## Identity and corrected bindings

The annotation stage reports `complete`, accepts a003, and records three logical calls with two structural corrections. The accepted raw hash is `0a39e99d9ff2762b0d557360fa96d19054c8e42c589d2b7264489247c70f6c62`. The raw annotation contains 24 demands including nested declarations, 16 constraints, and one credential sensitivity declaration. Every requirement is marked `expressed`, with no gaps.

The cross-IR references have been corrected to the corresponding IR input positions. In particular, the four status writes now use input 1, the prior outcome carried by their frozen CFG inputs. Presence and transient conditions now target the owning atomic computation's `self` slot. These repairs establish structurally resolvable references; they do not establish the meanings of those conditions.

All constraints use task scope. The pinned CFG has distinct first-attempt, retry, and archive sites in an acyclic workflow; no element scope, invented reset, or nested quantification is involved. The condition producers precede the selected delivery sites. The archive declaration does not require first-attempt or retry outcome values on the key-absent path.

## Condition and temporal correspondence

| Requirement | Accepted declaration | Independent assessment |
|---|---|---|
| R3/R4: preferred call only with a present key; bypass when absent | The first preferred delivery requires the atomic `present(input 0)` expression in `ir_005`. | The predicate itself matches presence and uses the acquired key version. However, there are no normalized edge expressions connecting it to the present/absent routing. English edge text is not an executable predicate. The declarations also express the prohibition component, not a complete positive fallback obligation by themselves. |
| R5/R6: transient-failure-only retry | Retry requires the expression owned by atomic computation 1 in `ir_009`. | **Semantic correspondence is not established.** That expression is only `ref(fast_fetch_first_outcome)`. The referenced preceding computation represents the general outcome used to distinguish success, transient failure, and non-transient failure. No declaration establishes that this general result is the Boolean “first attempt failed transiently,” and no comparison or other supported predicate performs that distinction. Naming the second output `fast_fetch_first_transient` does not supply the missing semantics. |
| R5: retry at most once; R8: archive at most once | Each limit is one attempt at its actual delivery operation. | The selectors and units match the upper-bound components. Neither count includes receipt or a compiler-generated observation. An upper bound alone does not require the conditional action; separate positive action demands are present. |
| R11: no fetch after either tool succeeds | Three `forbid_after` declarations use success-return instructions `ir_020`, `ir_022`, and `ir_024` as triggers. | **The declared starting point is later than success.** These terminal returns have no following execution. The rules do not cover the interval from successful result to return. Success-branch topology may support a separate argument, but these declarations do not constitute that argument or fully express the source restriction. |
| R13: no archive retry after failure | No archive delivery after whole `ir_017`, which classifies either archive outcome. | The trigger includes success as well as failure. This is stronger than R13 in isolation, but consistent with the combined Task's archive-at-most-once rule and prohibition of fetches after success. It should not be described as a failure-specific trigger. |
| R16: status append before every terminal return | Four separate `requires_prior` rules pair each status write with its corresponding return. | The pairing matches all four branch alternatives. Each rule has one prior event, avoiding an unintended interpretation that one of several unrelated writes is enough or that all four writes must occur together. |

The raw top-level `expressions` list is empty. The two inline expressions do not define the success/failure branch predicates. Missing branch correlation must remain an analysis limitation, rather than treating all abstract paths as demonstrated executions. No deterministic checker result is asserted in this note.

## Information prohibitions, acquisition, and sensitivity

R14 prohibits the whole selected key value from reaching the `archive_fetch` location. Its default all-event coverage does not narrow the ban to one manually listed delivery. This receiver is distinct from `fast_fetch`, where the source explicitly requires the key.

R15 uses the same key source but selects only `status_file`. It accounts for all four status writes through their shared location. **It does not explain whether the returned archive error is diagnostic output, or otherwise establish a complete diagnostic boundary inventory.** The source's diagnostic category cannot automatically be equated with the status file alone. This is an unresolved coverage account, not a claim that the error definitely contains the key.

The source acquisition is modeled as reading the request and environment snapshots and selecting `source_id` and `FAST_KEY`. Compilation inserts model-context deliveries of those snapshots before selection. Those are contract-generated static observation possibilities, not measured executions or source-proven minimal reads. The selected key's single credential declaration identifies the relevant content, rather than labeling the entire environment as a credential. Later selection cannot erase an earlier observation of its containing snapshot.

The classification computations preserve `possible` dependencies on responses. Those dependencies are not proof that outcome or status content contains credential plaintext. The information restrictions are original-content prohibitions; they must not be reported as bans on every possible influence.

## Positive demands and source separation

The 24 raw demands comprise:

- Two exact selected-value acquisition demands.
- Two truth demands for presence and the purported transient predicate.
- Three demands at each preferred delivery: action, original source ID value, and original key value.
- Archive action and original source ID value demands.
- Four exact return-input value demands: three corresponding bodies and the archive error.
- Action and payload-value demands at each of the four status appends.

The preferred-call and archive expected values reference the correct original IR inputs. Return demands preserve the existing branch-specific values. Every status write has its own content demand, with no invented exact status string. The candidate uses the existing outcome as that content; source fidelity of its representation still depends on the classification account.

Neither R14 nor R15 owns a positive demand. R2 and the preferred-call requirements legitimately demand key values for acquisition and authorized calls. This separation does not authorize the key at archive, status, or arbitrary later receivers.

R4's absent-key archive action has CFG bindings but no separately owned positive demand; the shared archive action demand is owned by R7 and explains the failure-fallback cases. The shared site may support both paths, so lack of a duplicate seed alone is not an omission verdict. Whole-chain review still needs to account for the absent-key obligation without claiming that a generic action demand proves the routing.

The initial annotation preserves concrete endpoint and status content demands, but its zero-gap claim is not supported by the retry-predicate account, the late R11 triggers, and the unresolved diagnostic receiver coverage. Final selection, any repair, actual constraint statuses, and candidate-preservation evidence require review of the later saved artifacts.
