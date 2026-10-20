# Case 013 independent assistant assessment

The selected repaired annotation produced complete deterministic propagation and DOE artifacts, but semantic refinement ended at `repair_limit`. There is no approved reduction. The final model review's reported operand problem is contradicted by the frozen CFG and propagated records, while separate concerns about the transient predicate, success-trigger timing, and diagnostic coverage remain. This is an external assessment, not a pipeline input or replacement terminal result.

The [terminal case result](result.json) records `diagnostic`, with the repaired annotation selected, `repair_limit` retained, and propagation and DOE calculation complete. Local finalization ended at 09:42:41 UTC. No additional model request or semantic repair was made after the independent final review.

## Evidence and assessment boundary

The source is [the frozen SKILL.md](inputs/package/SKILL.md). The [Task](task/task.json) was extracted independently and accepted on its first response. The [initial annotation](annotation/audit/raw-annotation.json) was accepted after two structural corrections; the [repaired annotation](refinement/repair/audit/raw-annotation.json) was accepted after one structural correction. [Refinement](refinement/result.json) selects `repair` and records `repair_limit` following the final review.

This assessment uses the actual saved source, CFG, declarations, reviews, and deterministic artifacts. The earlier [source checklist](../../verification/source-obligations.assistant.md), [invalid-candidate note](../../verification/013-a001-interim.assistant.md), and [accepted-initial note](../../verification/013-accepted-initial.assistant.md) were external assistant review material. They were not model inputs, candidate annotations, or expected answers. No source, frozen input, model response, annotation, or pipeline result was edited for this assessment; no remote call was made.

## Source and Task

The Task preserves the principal source obligations across its 16 requirements:

| Requirements | Source obligation preserved |
|---|---|
| R1–R2 | Acquire the request's source ID and the environment key. |
| R3–R4 | Try the preferred tool first with source ID and key when the key is present; bypass it and use archive when the key is absent. |
| R5–R7 | Retry the preferred tool exactly once only after a transient first failure; do not retry a non-transient first failure; use archive after a non-transient first failure or any failed retry. |
| R8–R9 | Call archive at most once, passing source ID as its sole argument. |
| R10–R13 | Return the corresponding successful body's value unchanged and make no further fetches; on archive failure return its error and do not retry archive. |
| R14–R15 | Never send the key to archive or diagnostic output anywhere in the workflow. |
| R16 | Append final status before returning on every success or failure path. |

This comparison found no omitted principal obligation or invented processing requirement in the Task. The source does not specify the representation of transient classification or final status, nor an exhaustive inventory of what constitutes diagnostic output. The Task's empty issue list does not resolve those interpretations.

## Semantic-review findings and repair quality

The [initial review](refinement/initial-review/calls/review/a001/response.json) reported two findings. They have different evidential strength.

**The asserted missing sensitivity route was incorrect under the current backend.** The initial annotation selected `FAST_KEY` from `environment_snapshot` into `fast_key` and labeled the selected value as a credential. The reviewer claimed that this failed to identify the credential in the earlier whole-snapshot model observation, and requested an additional snapshot-field label while retaining the child label. Existing sensitivity propagation embeds a selected child into its exact parent field through `part_of`; this preserves the original content identity and reaches the earlier observation. It does not propagate execution backward or label unrelated environment members. The [independent sensitivity assessment](../../verification/013-initial-sensitivity-finding.assistant.md) checked that mechanism in the backend and a synthetic example. The added snapshot and retained child declarations therefore describe the same sensitive content, rather than repairing the claimed missing route.

**The initial transient-predicate finding was supported.** The accepted initial condition was a plain reference to the general first-attempt outcome. Nothing defined that general classification result as the Boolean “the first attempt failed with a transient error.” A truth demand, output name, and explanatory reason could not establish that meaning.

The suggested repair options were not all compatible with the constraint contract as stated. The first repair removed the expression while keeping the R5/R6 `only_if` references, producing [two `constraint_expression` errors](refinement/repair/calls/annotation/a001/validation.json). An opaque computation alone cannot supply the normalized expression those retained references require.

The accepted repair uses:

```text
field(fast_fetch_first_outcome, ["transient"]) == true
```

This is not evidence of an invented external API response schema: the field is read from a locally computed classification result. Such an internal representation could be legitimate. However, the artifact never defines it. Its producer remains opaque, and no constructor, normalized producer definition, source statement, or CFG metadata establishes a `transient` member or what it means. Structural acceptance establishes valid expression syntax and references, not equivalence to the source's transient-failure predicate. The zero-gap realization remains insufficiently supported.

**The final review's only finding was factually wrong.** The [final response](refinement/final-review/calls/review/a001/response.json) claimed all four status-write IRs had only input 0 and that their input 1 references were invalid. The [frozen CFG](inputs/cfg.json) gives each two inputs:

| Instruction | IR input 0 | IR input 1 |
|---|---|---|
| `ir_019` | External resource `status.txt` | First preferred-attempt outcome |
| `ir_021` | External resource `status.txt` | Preferred-retry outcome |
| `ir_023` | External resource `status.txt` | Archive outcome on the success path |
| `ir_025` | External resource `status.txt` | Archive outcome on the failure path |

Each write correctly takes IR input 1. Its nested demand targets operation input 0, which is the write operation's sole payload slot. These are different coordinate systems. The suggested change to IR input 0 would select the file resource identifier instead of the status content. The pipeline did not apply that suggestion: its single semantic repair round had been used, so it retained the repaired candidate with `repair_limit`. This incorrect final finding explains that recorded review outcome; it does not eliminate the separate semantic concerns identified here.

## Constraint fidelity and remaining scope limits

The repaired candidate retains 16 constraints. All use task scope over the existing acyclic first-attempt, retry, and archive sites. No member scope or invented reset is needed. Counts select actual deliveries, so request, response, and generated observations are not triple-counted.

- The key-presence condition references the correct preceding atomic computation and uses `present` on the acquired key input. However, no normalized edge expressions connect this condition to CFG routing. English branch descriptions are not executable predicates.
- The retry and archive attempt limits each correctly select their respective delivery and use an upper bound of one. Positive action demands remain separate from these bounds.
- The repaired retry condition has the unresolved local representation assumption described above. Neither field existence nor its classification meaning is established by the source.
- R11 still uses the three terminal success returns as `forbid_after` triggers. The source starts the prohibition at success, before return. The selected triggers do not cover that interval and have no subsequent execution in this graph. Existing success-branch topology may support a separate argument; the declarations alone do not establish it.
- R13 prohibits further archive delivery after archive-result classification, including success as well as failure. That is broader than R13 alone, but consistent with the combined Task's archive-at-most-once and no-fetch-after-success requirements.
- R14 selects the archive receiver and the original key content, with all applicable events. It does not incorrectly prohibit the source-required key arguments to the preferred tool.
- R15 selects only the shared status-file receiver. It covers all four status writes but does not explain whether the returned archive error is diagnostic output, or otherwise establish a complete diagnostic-boundary account. This is an unresolved semantic coverage question, not a claim that the error contains the key.
- R16 has four correctly paired write-before-return rules, one for each branch alternative. It does not require all four writes in a single invocation.

All 16 realizations still claim `expressed` with no gaps. Structural validation and complete declaration accounting cannot establish that claim's semantic correctness.

## Positive demands, acquisition, and sensitive content

The repaired annotation retains 24 raw demands, including nested declarations:

| Demand group | Count | What is preserved |
|---|---:|---|
| Acquisition | 2 | Selected source ID and selected key value |
| Conditions | 2 | Key presence and the purported transient predicate |
| Preferred deliveries | 6 | Action, original source ID, and original key at each of two sites |
| Archive delivery | 2 | Action and original source ID |
| Terminal returns | 4 | Each successful body and the archive error |
| Status writes | 8 | Action and payload value at each of four appends |

The preferred-call payloads and archive source ID have their own exact demands at the delivery boundary. All four status writes have payload demands; this directly contradicts the final review's claim of an absent status binding. The return demands retain branch/version correspondence. No exact status string or external API error taxonomy was invented as a positive requirement.

Neither R14 nor R15 owns a positive demand. Positive key demands instead belong to its acquisition and authorized preferred-tool uses. Necessary key use there does not authorize it at archive, status, or arbitrary later receivers. The archive site is shared by the no-key and failure-fallback paths; its action demand is owned by R7. A missing duplicate R4-owned seed alone does not establish an omission, but the absent-key obligation still needs a complete routing account.

Acquisition is modeled as reading request and environment snapshots and then selecting the named fields. Compilation inserts model observations of those snapshots before selection. These are static contract possibilities, not measured execution or proof of minimal acquisition. Later selection cannot erase an earlier observation of its containing version.

The repaired sensitivity list has two credential declarations: `environment_snapshot["FAST_KEY"]` and the selected `fast_key`. They refer to the same source content. Possible dependencies from requests to responses and classifications do not establish credential plaintext in every resulting body, outcome, or status.

## Deterministic results and DOE proof assessment

The [propagation manifest](propagation/manifest.json) records completion for all 26 IRs with no diagnostics. [Data](propagation/data.json), [records](propagation/records.json), and [sinks](propagation/sinks.json) contain 21 Data objects and 16 sinks: nine model observations, three external-tool deliveries, and four storage writes.

Both preferred deliveries carry the same exact `source_id` and `FAST_KEY` child Data identities. Archive's delivery carries only the source-ID child. The four write records bind respectively to the outcome computed in `ir_009`, `ir_013`, and `ir_017` (the latter shared by the two archive terminal paths). This independently confirms the correct status payload bindings and contradicts the final review at the propagated-fact level as well as the CFG level.

The [DOE result](doe/doe-result.json) records `status: complete`, zero diagnostics, and all 16 expected sinks. Its declared-range basis resolves both sensitivity declarations. The [demand-support audit](doe/audit/demand-support.json) also records `complete`, with no diagnostics. These completion labels describe computation over the selected declarations; they do not upgrade `repair_limit` to semantic acceptance.

### Baseline constraints

| Declarations | Count | Saved status | Interpretation |
|---|---:|---|---|
| R3/R4 first-call presence conditions | 2 | `potential_violation` | The abstract traversal can reach the call without establishing the required predicate. No normalized edge expressions correlate the condition with the branch. This is not a demonstrated no-key execution. |
| R5 retry upper bound and R8 archive upper bound | 2 | `satisfied`, structural | Each selected attempt site occurs at most once in the supported task-entry model. |
| R5/R6 transient retry conditions | 2 | `potential_violation` | The declared atom can be false on an abstract path reaching retry. This neither validates the local `transient` representation nor proves an actual forbidden retry. |
| R11 no fetch after success return | 3 | `satisfied`, structural | The narrower terminal-return-trigger declarations pass. This does not establish the source's earlier success boundary. |
| R13 no archive after result classification | 1 | `satisfied`, structural | No later archive delivery follows the selected classification site. |
| R14 original key content to archive | 1 | `satisfied`, nonstructural | The actual archive payload contains the source-ID value, with no supported key-content route in the selected model. |
| R15 original key content to status file | 1 | `potential_violation` | Only possible or derived influence reaches candidate payloads. The witness names the first-attempt and retry status writes; the result explicitly does not establish original plaintext inclusion. |
| R16 status-write precedence | 4 | `satisfied`, structural | Each corresponding write precedes its terminal return. |

Totals are **11 `satisfied`, five `potential_violation`, and zero `not_established`**. Ten satisfied checks are marked structural. The five potential results are abstract-model warnings, not measured violations or proofs that their witness paths are feasible. The absence of a `not_established` result does not answer the independent semantic correspondence objections.

### Demand provenance and scope

The main result stores 959 demand derivations; the support audit stores another 109, for 1,068 combined derivations. All 24 compiled seed goals are represented. A read-only consistency check against the saved compilation map and raw annotation found no missing seed-goal reference, missing demand-parent reference, raw-pointer requirement mismatch, or traceability seed/requirement mismatch. Every review's demand and sensitivity references resolved in the saved material. This was an artifact-reference check, not a replay or a proof of semantic correctness.

The seven constraint-only requirement groups R4, R6, R8, R11, R13, R14, and R15 own no demand derivations. In particular, the two information prohibitions have no positive seeds. Constraint checks and positive-demand propagation remain separate in the actual persisted result.

Concrete endpoint derivations preserve both preferred-call inputs separately, archive's source-ID input, and each write's payload slot 0 as exact value demands. At the whole environment observation, the nonconservative demands concern `FAST_KEY` value or presence, rather than all environment fields. At the presence computation's observation, the nonconservative property is presence. Other overlapping retained ranges can be conservative consequences of downstream results, request/response dependence, controls, and opaque processing; their existence does not prove that the whole observed content is indispensable.

Three sink accounts retain `outside_listed_properties` ranges: the request snapshot observation, environment snapshot observation, and key-presence input observation. They explicitly say that only listed properties are constrained and no replacement execution was verified. These are unresolved minimization ranges, not accepted exclusion candidates. The saved per-sink `limitations` arrays and computation diagnostics are empty, but this does not remove those ranges or the semantic limitations discussed above.

### Sensitive-content rows and reductions

There are **20 data-review rows, all `no_excess_established`**, with **zero excess findings and zero reductions**. They form ten operation/range pairs, each repeated for the two credential declarations:

| Reviewed content and receiving sites | Distinct operation/range accounts | Stored rows | Sensitivity relation |
|---|---:|---:|---|
| Environment `FAST_KEY` field observed in `ir_003`; selected key observed in `ir_005`; key delivered at the two preferred calls | 4 | 8 | `direct` |
| First and retry responses observed after receipt and again for classification; first and retry outcomes written to status | 6 | 12 | `possible` |

The child declaration itself reaches the earlier environment observation through an `embed` derivation at `FAST_KEY`. This is direct evidence in the saved result that the initial review's claimed missing sensitivity route did not require a second label. The paired rows do not represent twice as much disclosure.

All 20 rows are retained because an overlapping task demand exists. The two preferred deliveries have explicit authorized-key value demands. The two sensitive-influence status accounts have exact R16 status-payload demands. Other result and observation accounts include conservative retention. `no_excess_established` therefore means no supported excess was established under these declarations and mechanisms; it does not mean the payload is globally minimal, irreplaceable, free of a baseline constraint concern, or safe under every interpretation of the source.

Six sinks have no sensitive data-review row under the declared credential ranges: the request observation, archive delivery, archive-response observation, archive classification observation, and the two archive status writes. These are not universal nonsensitivity certifications. Ordinary terminal returns are not automatically user-output sinks in this contract, although all four return values have Task demands.

The persisted `constraints.preservation` and `constraints.influence` maps are both empty, every data review has an empty `constraint_refs` list, and every `reduction` is null. Consequently, **this run exercises no candidate-level structural preservation, terminal-content-subset, or disjoint-forward-influence proof**. There is no supported reduction basis to endorse, and no failed preservation intersection to reinterpret as necessity. It would be incorrect to advertise the run as demonstrating that these reduction-proof mechanisms succeed merely because baseline constraints were checked.

The DOE artifact is complete rather than partial, and records no computational blocker. The enclosing semantic chain remains unaccepted at its single-repair limit; the limitations of the transient interpretation, late success triggers, diagnostic inventory, conservative relations, and outside-listed-property ranges remain material. Complete propagation and DOE computation do not establish full constraint faithfulness, all-path source satisfaction, or absence of DOE.
