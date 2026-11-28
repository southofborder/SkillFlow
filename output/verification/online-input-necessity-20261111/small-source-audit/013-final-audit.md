# 013 selected-run source and input-necessity audit

013 closed **partial** with **25/25 generated IR processed** and partial DOE. All **6/6 finite acquisition/call/append source boundary sites** have static operation records: request read, environment read, first fast call, retry fast call, archive call and status append. The shared return terminator is also processed and has four possible selected values. These are static records, not real Skill executions.

| Saved result | Count |
| --- | ---: |
| Input assessments | 92: 32 IR inputs, 55 operation inputs, 5 acquisition outputs |
| Coverage | 92 processed; 0 not reached |
| Range derivation rows | 1,322: 318 required, 1,004 unresolved, 0 deletable |
| Assessment status combinations | 59 required + unresolved; 33 unresolved only |
| Sinks | 22: 18 model observations, 3 tool deliveries, 1 storage write |
| Sensitive comparisons | 14 no_excess_established; 0 reductions |
| Contract decisions | 7 accepted, 4 unresolved; 0 rejected |
| Constraint decisions | 9 satisfied, 2 potential_violation |
| Input semantic findings | 0 |

All assessments include unresolved information. There is **no certified field/slot deletion example** from this selected run, and the 14 sensitive comparisons are unresolved rather than safe verdicts. Counts are derivation/comparison rows, not distinct fields or leaks.

## Bound receipt and required inputs

The pure receipt loader passed against selected source, CFG, Task, raw/compiled annotation and mapping, without solving or replay. Demand support matches internal receipt SHA `3e7a0af1f811427835cb420531f7c074dfdc557268026fd59d015bfeb67edc50`; the DOE manifest matches the full receipt SHA `86dd841c646ac6699ae69a8a7661044b7d121d59aa4fa626d0667a2f9bfbe0d2`. `source_review_complete=false` remains explicit. All listed input files remained byte-identical during audit.

The six accepted tool contracts are the three actual request/response pairs, not six source calls. Each fast attempt requires whole original source_id and FAST_KEY; archive requires whole source_id only. The pairings retain separate first, retry and archive responses. The seventh accepted contract transfers the abstract final status's whole value to its scalar terminal category. It does not define the serialized status.

Acquisition assessments visibly retain request.source_id, environment.FAST_KEY presence and value, and whole body values from successful responses. The first and archive error selectors remain in the saved annotation. Original reads, tool arguments, response versions and model observations remain facts. No read/server field-projection capability is established.

## Source correctness and limitations

The retry/fallback **Task obligation is clear**. The four unresolved contracts concern concrete first/retry/archive outcome discrimination and transient-error classification. Those are local processing/interface relations, distinct from uncertainty about task purpose. Supported semantic outcome cases need not invent a response discriminator field. The existing Task marks transient classification as an issue, and its global policy plus six requirement-expression gaps contribute additional global barriers; the unresolved range count must not be attributed to one local contract alone.

Final review F001 retains a missing true-transient `only_if` restriction for the retry: at-most-one and prior classification alone do not express which classification outcome permits retry. F002 retains incomplete diagnostic-output prohibition: only status.txt is covered. Four further findings preserve the unresolved contracts. The saved archive-key prohibition is satisfied in its modeled scope; the status-only check does not prove the workflow-wide diagnostic ban.

The nine satisfied constraints cover modeled bounds/order/forbidden flows. Two key-presence `only_if` checks return **potential_violation** with abstract witnesses despite the authored CFG gate. They do not demonstrate a feasible real invocation with an absent key, and must not be reported as actual Skill violations. No deletion preservation checks exist because no reduction was emitted.

Two independent provisional concerns remain relevant. The selected annotation still uses a concrete `['error']` field for a semantically described call error without a supplied physical response schema; final review does not flag this mapping concern. The source's final-status contents/serialization remain a genuine local output ambiguity even though the abstract category transfer is accepted. Append mode and append-before-return remain explicit. The revised processing gap removed the hypothetical unrelated saved-result association.

## Closure and cost

The sole replay matched in **9.5149 seconds**, with **zero new native starts**. The final separate cost audit records **12 native starts** (7 normal + 4 semantic-repair + 1 structural-correction), all with complete public usage, totaling **393,374 tokens** (344,678 input + 48,696 output). Outer retries were zero; one internal reconnect notice was observed. Provider HTTP attempts and billing remain unknown. Analysis took 1,317.207 seconds.

The adjacent JSON covers all ten prewritten source expectations, exact contract decisions and references, input range summaries, source-boundary crosswalk, constraints, diagnostics and artifact hashes. This finite comparison is not a gold benchmark or precision/recall result. Earlier provisional files are preserved; no production or run material was changed.
