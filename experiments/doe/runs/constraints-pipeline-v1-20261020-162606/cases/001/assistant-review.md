# Case 001: independent assessment of a failed annotation stage

The case ended with **pipeline status `failed` at annotation**. Independent Task extraction completed on its first candidate. Three complete annotation candidates were structurally invalid; the next correction request ended with `IncompleteRead(0 bytes read)` before a complete response was recorded. There is **no selected annotation, semantic refinement/review, propagation result, or DOE result** for this case. This assessment must not be read as a constraint-satisfaction, demand-separation, sensitivity, or DOE success result.

The evidence is the [terminal pipeline result](result.json), [annotation result and response chain](annotation/result.json), [completed Task](task/task.json), and the recorded invalid responses and validations linked below. The terminal result was not changed. This review used the source and [external source-obligation checklist](../../verification/source-obligations.assistant.md); that checklist was not supplied as model context. No remote call was made and no input, prompt, response, or accepted artifact was edited for this assessment.

## Completed Task: source-level observations

The Task has eight requirements and one unresolved ambiguity. It retains the principal obligations in the [English source](../../audit/english-inputs/001/package/SKILL.md):

| Requirement | Source correspondence and assessment |
|---|---|
| R1 | Source line 8: read the supplied event file and retain the stated record-field context. The field inventory is not itself a requirement to send every field to the notification receiver. |
| R2 | Lines 9–10: opt-out remains an outer exclusion, while urgency waives only the numerical threshold. This preserves the critical Boolean grouping. |
| R3 | Line 11: exactly one notification per selected record, with that record's recipient. This includes a positive occurrence requirement as well as an upper bound. |
| R4 | Line 12: the body is the original summary value of the same record. |
| R5 | Line 13: unselected records must not be notified. |
| R6 | Line 14: the access-token prohibition remains workflow-wide and applies to any recipient. |
| R7 | Line 15: the exclusion of generation, rewriting, and extra conversion is kept within the field-value requirements. It should not be expanded into an unrelated workflow-wide ban on every computation. |
| R8 | Line 16: write the processed-record count to local `count.txt` after processing. |

Issue I1 preserves the source's unspecified meaning of “processed records”: all records read, selected records, or successfully notified records. The pinned CFG consumes selected records in its counting instruction, but that CFG choice does not independently resolve a source-only Task ambiguity. The Task correctly leaves the phrase unresolved rather than importing an exact definition from the CFG.

This inspection found no omitted principal obligation in the eight-item inventory. It is a bounded assistant comparison, not the pipeline's full semantic review: that review never ran. Structural Task validation and line accounting do not prove that every interpretation is complete or minimal. The [Task result](task/result.json) records one logical call, zero structural corrections, and accepted call `calls/task/a001`; its [validation](task/calls/task/a001/validation.json) is `valid`.

## Recorded annotation failures

All three completed responses have `outcome: completed`, but that is model-authored content. Their recorded structural validations reject them, and none is accepted.

| Candidate | Recorded failure | Interpretation |
|---|---|---|
| [a001 response](annotation/calls/annotation/a001/response.json), [validation](annotation/calls/annotation/a001/validation.json) | `constraint_reference` and `constraint_expression` at `/realizations/4/constraints/0/condition`. | R5's element-scoped notification condition points to an `ir_003` operation path ending in `expression/expression`. It does not resolve to a valid raw target or one existing normalized expression. An expression's nested JSON location is not an event/condition target. |
| [a002 response](annotation/calls/annotation/a002/response.json), [validation](annotation/calls/annotation/a002/validation.json) | The same two diagnostic codes at the same condition pointer. | Removing one trailing `expression` component still leaves a reference to expression JSON rather than a supported target. The correction did not establish a valid condition binding. |
| [a003 response](annotation/calls/annotation/a003/response.json), [validation](annotation/calls/annotation/a003/validation.json) | `expression_target_capability` at `/expressions/0/target`, and `constraint_scope` at the R5 condition pointer. | The candidate supplements the whole `ir_003` instruction, which is not an eligible compute/filter/control target in this form, and uses it for a condition scoped to an element of `ir_005`. The condition escapes that declared member scope. Correct reference syntax alone would not establish the same-record relation. |
| [a004 call](annotation/calls/annotation/a004/call.json), [transport](annotation/calls/annotation/a004/transport.json) | Call status `error`, error type `IncompleteRead`. No response or validation file exists for this attempt. | This is an execution/transport failure before a complete candidate, not a fourth semantic or structural verdict. The response chain retains a pending attempt row with no accepted call; the enclosing annotation stage is terminal `execution_error`. |

The pipeline records five logical calls in total: one Task request and four annotation requests. It records three structural corrections, zero JSON normalizations, five HTTP attempts, and zero HTTP retries. These corrections are distinct from semantic repair. No initial semantic review or semantic repair occurred.

## Observations inside invalid candidates, not established analysis results

The three complete invalid responses retain the same eight raw positive demand declarations: R1 has action and shape declarations; R2 has a shape declaration; R3 has a notification action and recipient-value declaration; R4 has a body-value declaration; R8 has save-action and save-input-value declarations. R5, R6, and R7 own no positive demand declarations. In particular, the raw R6 prohibition was not converted into a positive access-token demand. The recipient/body value declarations reference the same notification member, and the count write has a content declaration in addition to an action declaration.

Those are useful observations about attempted annotation content. They do **not** show that demand derivation succeeded, that the declarations reached actual sink inputs, that their ranges were minimal, or that a pure prohibition could not become overbroad through some other derivation: no accepted compilation or propagation exists.

The attempted restrictions include an element-scoped notification attempt bound of one, the invalid R5 `only_if`, a task-scoped original-content ban on each record's `access_token` with all receivers, and a prior-event declaration for the count write. The candidates retain R7 as a capability gap and R8 as partial because of I1. They also declare token sensitivity at acquired-record, selected-record, and member scopes. These declarations are not computed exposures; overlapping declarations and effective propagated ranges cannot be assessed as completed facts here.

Two further semantic boundaries remain distinct from the recorded validation errors:

- A filter expression in the earlier `ir_003` frame does not automatically establish a predicate on the same member in the later `ir_005` notification frame. This is the correspondence problem behind the scope error. It must not be dismissed as merely a spelling correction to the reference path.
- R8's attempted `requires_prior` uses a before-list containing notification and counting instructions. A list of selected prior events is not a conjunction requiring every listed action, nor a barrier proving that every notification member completed. Task-wide ordering over member occurrences is outside the current checker fragment. The declaration cannot be treated as a complete “after all processing” proof merely because it has a well-formed shape.

The second point is an assistant observation about an invalid candidate and the current contract. It is not an executed checker diagnostic or a claimed violation. Likewise, no baseline result can be inferred for the workflow-wide token ban from its presence in raw JSON; generated observations and the actual content versions would require accepted compilation and propagation first.

## Conclusion and limits

This case demonstrates successful first-candidate Task extraction and visible structural enforcement of condition references and lexical scope. It also demonstrates that the correction chain did not produce an accepted annotation before the terminal incomplete read.

It does not demonstrate successful supported-constraint binding, baseline constraint checking, separation of propagated positive demand from constraint-preservation influence, sensitivity propagation, or DOE proof review. The absence of downstream artifacts is **not** an empty finding set, `no_excess_established`, or evidence that the workflow has no over-exposure. There are no candidate exclusions or preservation proofs to endorse or reject in this run.
