# Case 013: source-only Task ambiguity versus representation gaps

Status: read-only assessment and narrow post-batch wording proposal. No source, prompt, Task, review, controller or current-run artifact was changed. This note is not feedback to the running case.

## Assessment

A small clarification is warranted. Existing guidance already protects source-only extraction and allows faithful open descriptions, but does not explicitly distinguish a clear qualitative Task duty from missing interface/classifier fields or serialization when deciding whether to create an unresolved Task issue. This is therefore an underspecified guidance boundary, not a reason to introduce a new Task schema or weaken the existing global treatment of genuine Task issues.

The current Task workflow in `src/skillflow/task/prompts.py:15` requires obligations including conditions and applicability. Line 18 asks for ambiguity/conflict issues, allows faithfully retained open descriptions, and prohibits invented encoding, mechanism or implementation. These principles are useful but do not state when an open implementation detail is merely an implementation detail rather than a Task ambiguity.

The source-review instructions at `src/skillflow/document_guided/source_review.py:356` correctly route CFG and processing representation defects and keep Task objections source-only at lines 366–371. They do not explicitly ask the reviewer to distinguish ambiguity about the duty from absent encoding of an otherwise clear duty. There is no need to repeat the existing isolation rules; the clarification should address only this missing classification boundary.

## Concrete source and selected interpretation

The frozen source in `document-guided-013-input-necessity-high-20261111-173347/source/inputs/package/SKILL.md` states:

- Lines 10–11: retry exactly once only after a transient first failure; do not retry a non-transient first failure; route a non-transient first failure or failed retry to the archive.
- Lines 13–14: return the successful response body unchanged, or terminate with the archive error on archive failure.
- Line 16: append the final status to the local status file before every return.

The source byte SHA-256 is `90cc786cd8bb72c6881c2d27a95157d4bad8363bd533f2383d02ee8678c61495`. The initial Task response byte SHA-256 is `3030a4d448e783af862964134818a420632901cdbee152a98da49173984fdccf` (`task/calls/task/a001/response.json`).

That Task correctly retains the retry count, transient/non-transient condition and archive fallback. It also creates unresolved issues:

- `transient_error_classification`: the source gives no criteria identifying which errors qualify as transient.
- `final_status_representation`: the append and timing are explicit, but status values and representation are unspecified.

The initial source review contains no Task findings. It separately records four processing-contract uncertainties about the actual success/failure discriminator and transient-classification relation. Those local questions include which returned member/tag/signaling rule supplies the distinction and which error properties a classifier examines. The review also accepts an abstract final-status transfer while explicitly declining to determine its text or file encoding.

This demonstrates the relevant boundary. A source can prescribe a conditional retry/fallback duty without supplying its executable predicate or error object layout. It can require a final-status append without requiring a particular byte encoding. Missing implementation mappings alone do not require converting those qualitative duties into an unresolved global purpose question. Retain the duty at the abstraction supplied by the source and let later processing/interface analysis identify the unsupported executable relation.

This conclusion is deliberately narrow. If the source gives conflicting definitions of transient errors, materially different interpretations of the condition, or competing required status contents, a genuine Task issue remains appropriate. Missing serialization is not automatically harmless when the source requires exact representation or when ambiguity changes the information that must be returned or saved. This note does not choose an undocumented classifier, error field, status value or file format.

## Minimal wording proposal

Add a brief clarification next to the existing Task workflow's open-description rule:

> Preserve a clear source-stated duty at the abstraction in which it is specified. Missing implementation, interface-field or serialization details alone do not create a Task ambiguity; do not invent those details. Record an unresolved Task issue when competing source-supported interpretations change the required obligation, condition, applicability or information, including genuine conflicts about exact output representation when it matters.

Add a corresponding source-review instruction near ownership and Task-objection routing:

> Distinguish ambiguity about what the Skill requires from a missing executable representation of a clear requirement. An unknown discriminator field, classifier implementation or encoding belongs to the actual processing/interface representation when the qualitative duty is clear; it is not by itself grounds to broaden a Task issue. Preserve genuine source conflicts and output-content ambiguities, and keep any Task objection limited to the existing source-only code/spans/requirement IDs.

These sentences clarify ownership and abstraction; they do not create a new pipeline mechanism. Task extraction still receives only the complete frozen source and emits the existing CandidateTask. It does not emit processing gaps or receive CFG, annotations, payloads or review prose. The later processing stage independently reads the source and records concrete missing relations. If source review identifies a real Task-issue misclassification, use the existing finite source-only objection protocol and isolated revision budget; do not change the global policy after the fact.

## Offline checks and limits

After all four original controllers and sole replays close, add narrow prompt/interface tests confirming the clarification is delivered to both initial Task extraction and isolated Task revision, with no new input channel or schema field. Retain examples of a clear conditional duty with unspecified implementation and a genuine conflicting condition/output interpretation. Preserve existing multilingual source and evidence checks. Unit tests can verify wording and isolation, not prove that a future model will apply the distinction correctly.

Do not edit the measured case's Task/issues, reclassify its saved DOE result, run a corrective replay, or claim that this wording alone completes analysis. The original evidence and its global/local limitations remain part of the frozen batch report.
