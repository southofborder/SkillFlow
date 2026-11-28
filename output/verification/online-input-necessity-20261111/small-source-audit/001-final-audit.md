# 001 selected-run source and input-necessity audit

001 closed **partial**, with complete static propagation and partial DOE. All **17/17 generated IR** have records and all **3/3 finite source boundary sites** are represented and reached in that static model. The selected bundle is `revision/annotation`; the sole controller replay matched in 5.9443 seconds with zero new native starts. No Skill was executed.

| Saved result | Count |
| --- | ---: |
| All-input assessments | 53: 22 IR inputs, 30 operation inputs, 1 acquisition output |
| Assessment coverage | 53 processed; 0 not reached |
| Range derivation rows | 451: 393 required, 58 unresolved, 0 deletable |
| Assessment status combinations | 38 required + unresolved; 15 unresolved only |
| Input semantic findings | 0 |
| Sinks | 13: 11 model observations, 1 tool delivery, 1 storage write |
| Sensitive comparisons | 18 no_excess_established; 0 reductions |
| Input contract checks | 1 accepted tool contract; 1 unresolved count contract |

These are row and comparison counts, not unique fields, execution events or leaks. Every assessment has an unresolved range. The 18 comparisons explicitly say limitations prevent a conclusion; they do not establish safety.

## Source boundary crosswalk

| Original source | Selected CFG | Recorded operation | Meaning |
| --- | --- | --- | --- |
| SKILL.md:8, read events.json | ir_001; /blocks/block_001/instructions/0 | op_ir_001:e0:a0 read | Complete acquisition remains recorded. Its subsequent model observation is also retained. |
| SKILL.md:11–12, notify.send | ir_013; /blocks/block_006/instructions/2 | op_ir_013:e0:a0 deliver | Both actual arguments share one recorded member binding; no concrete runtime call count is measured. |
| SKILL.md:16, write count.txt | ir_016; /blocks/block_007/instructions/1 | op_ir_016:e0:a0 write | Static normal-exhaustion path reaches the write; the count meaning remains ambiguous. |

The selected receipt was revalidated using the pure `checked_input_contract_review` loader, without solving, replay or another semantic call. Its internal SHA is `37a3e01e24b450407e7d872685fb3327b4846780770afe5af239a06f83e30d64` and matches demand support. The DOE manifest separately matches the complete receipt's canonical SHA `50be53b8e7c943817910998a3df1e296177a09ffa7376431569ae32c15265e2c`. Source, CFG, Task, raw/compiled annotation, mapping and contract binding checks passed. `review_status=complete` means the review call completed; `source_review_complete=false` retains its material findings.

## Source-supported necessary inputs

The accepted notify contract requires **whole recipient** in input 0 and **whole original summary** in input 1, with source evidence at lines 11–12. Both come from the same selected record. The saved demand graph connects `notify_once` to its action seed and then, through `reviewed_input_contract`, to both whole-value input ranges. Separate `recipient_from_record` and `original_summary_body` goals retain their exact expected relations. Internal summary fields are not deletable under this obligation.

The acquisition assessment shows field-level demands for `each.recipient`, `each.summary`, `each.opted_out`, `each.urgent`, and `each.value`, plus collection shape/cardinality. Deterministic equality/threshold expressions preserve real selection dependencies; they were not overridden by a semantic contract. This demonstrates field-level demand propagation in the actual run, while its unresolved ranges prevent a complete minimality claim.

## Remaining correctness and precision limits

The final source review retains three findings. F001 says `skip_unselected` lacks an explicit supported `only_if` constraint even though the CFG has the two selection routes. F002 says the access_token prohibition covers only `notify`, omitting recipient-scoped model observations of the acquired collection and whole records. F003 retains the count contract as unresolved: all traversed occurrences require cardinality, while selected occurrences require membership/multiplicity and the selection conditions.

The single saved token constraint is **satisfied only within its authored notify-only scope**. It does not establish the source-wide any-recipient prohibition. No reduction preservation results were produced. Possible sensitivity propagation to the count is also preserved; it is not proof that the numeric count contains a plaintext token.

The count review explicitly says recipient, summary, record_id and access_token are unnecessary for the count, but its decision still disables the whole count contract. The saved compute retains a conservative whole-collection requirement. This confirms the provisional field-precision concern: known independent field relationships did not become usable local deletion conclusions. It is separate from global Task/realization barriers, which also affect all assessments. The source count ambiguity and the additional literal 'only when' selection ambiguity are recorded; unspecified send-failure continuation adds a control limitation. Therefore, not every unresolved assessment is caused by the count contract, and none is an unreached-IR coverage gap.

## Deletion examples and cost

**No certified deletion example is available from this selected run.** Source semantics and the final review support considering `record_id` and `access_token` unnecessary for the listed positive uses, but the saved result does not certify removing them. Original acquisition/observations must remain facts. No read-side field projection capability is established, and no source rewrite is proposed here.

The separate final cost audit records **12 native starts**: 7 normal, 4 semantic-repair, 1 structural-correction; **337,253 public tokens** (305,110 input + 32,143 output). All 12 requests have complete public usage. There were zero outer retries and two internal reconnect notices; provider HTTP attempt counts and billing remain unknown. Analysis took 923.249 seconds. The deterministic DOE report's 'zero API calls' line applies to that backend component, not the complete run.

This is a finite audit against seven prewritten source expectations, not a gold benchmark or a precision/recall claim. The adjacent JSON includes each expectation, exact assessment IDs, compact ranges, evidence chains, diagnostics, contract decisions, original source spans, full artifact hashes, and the source-boundary crosswalk. Earlier provisional snapshots are preserved. No production, prompt, source or run artifact was changed.
