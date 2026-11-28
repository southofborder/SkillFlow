# Initial processing response and complete correction: passive audit

Observed from saved current-run material at 2026-11-16 15:59 UTC. Run:
`experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414`.
This report reads saved bytes and uses only JSON forensics and the presentation
codecs. It does not invoke a stage validator, model, backend, Skill, or replay.
Production, prompts and run artifacts remain frozen.

The initial processing request returned a complete native response, then failed
strict JSON parsing. It did not time out. Its saved native process elapsed time
was 1,535.208 seconds, ending at `2026-11-16T15:54:39.378042+00:00`, with exit code
0. This is process elapsed time, not separately measured generation time. Network
and cost accounting are covered by the separate transport audit.

## Actual output and rejection

The model attempted the optional `skillflow-processing-json-v1` shared output
format. The raw response contains 212,300 characters. Its root member order is
`format`, `shared_values`, `payload`, `shared_values`: it emits a second table
after the payload. The saved validation contains exactly one diagnostic:
`json_format`, root path `""`, `duplicate JSON member: shared_values`.

The two tables cannot be collapsed as an identical repetition or a lossless
additive extension:

| Forensic inventory | Result |
| --- | ---: |
| First table entries | 266 |
| Second table entries | 310 |
| Names present in both | 241 |
| Overlapping definitions with identical exact values | 160 |
| Overlapping definitions with unequal exact values | 81 |
| Names only in the first table | 25 |
| Names only in the second table | 69 |
| Duplicate names within either individual table | 0 |

These are exact-value differences, not 81 proven semantic contradictions. Some
are differing evidence explanations or reason strings. Neither first-wins nor
last-wins is a lossless interpretation of this response. The audit preserved
both tables as ordered object pairs and never merged them into an accepted
fragment. Pair fingerprints and complete name inventories are saved in
`processing-initial-rejected-pair-forensics.json`.

There are 2,287 raw reference objects using 313 distinct names across both tables
and the payload. The payload references 41 names absent from the first table;
all its reference names occur in the second table. This is consistent with an
attempt to supply a later revised/extended table, but model intent is not
observable. It does not establish that the second table is semantically correct
or sufficient after recursive expansion.

There is a second static protocol mismatch, not an additional executed validator
result: all 266 first-table names and all 310 second-table names are mnemonic
identifiers, such as `AUTH` and `readReq`. The frozen codec requires `v0`, `v1`,
etc. using the exact pattern `v(?:0|[1-9][0-9]*)`. The prompt shows `v0` in one
example but does not explicitly state that identifier grammar. Strict parsing
stopped at duplicate JSON members before this subsequent rule could be checked.

There is **no accepted compact or expanded response size**, no accepted IR
coverage, and no completed contract validation from a001. A lossless
whitespace-only forensic serialization, still retaining the duplicate members,
is 205,695 characters (first table 44,488; payload 89,245; second table 71,876).
These are rejected-text size measurements, not a usable logical response or a
compression benefit. The saved source-review stage has not judged this response.

The earlier passive snapshot `presentation-audit/20261116T155518247953Z.json`
retains an ordinary-parser compact measurement produced before its strict codec
rejection. That number used a last-wins projection and must not be used as a
canonical size or conclusion. The audit helper has been corrected to reject
duplicates before such measurements; the original snapshot is preserved. The
new snapshot `presentation-audit/20261116T155938870153Z.json` records only the raw
size and duplicate-key error for this response.

## Complete correction presentation

At observation, a002 had a saved prompt and no saved complete response. Its
675,293-character prompt contains the entire 425,423-character initial prompt
as an exact prefix. The complete 16-file source still appears exactly, all 521
current CFG IR remain in the structured input, and the logical input digest is
unchanged:
`3a3d40f6f5084b49b548c28be8f737ffcaf623b9ddc6833ca84258c94d22dbcc`.

The appended correction context contains the entire exact raw response as a
string, the one duplicate-key diagnostic, and `format_examples: []`. JSON
escaping expands that 212,300-character raw candidate to a 248,702-character
string literal. Complete context is 248,883 characters; total prompt growth is
249,870 characters. No table or candidate field was dropped or selected by a
last-wins parser.

The whole-response correction is appropriate for this malformed representation:
the duplicate tables leave the intended exact values ambiguous before a unique
logical fragment exists. The prompt explicitly requests a complete replacement;
it does not claim that repairing two records would suffice.

The absence of `JOINT PROCESSING CORRECTION MATERIAL` is not a compaction bug in
this case. Applying the pure display codec to the same complete input and raw
candidate yields a 438,992-character joint body and a 675,723-character complete
alternative prompt. That is 430 characters longer than the actual fallback, so
the existing shortest-complete-form selection chose the fallback. Both exact
expansion and the complete source suffix match. The malformed candidate remains
one opaque string; exact repeated-subtree sharing cannot deduplicate its internal
JSON text. No alternative prompt was dispatched. See
`processing-initial-correction-codec-size.json`.

## General follow-up proposal after this frozen run

The same output guidance appears exactly once in a001 and a002. The added
correction instructions are generic; they add no explicit output-wire name,
envelope or table-uniqueness rules. The sole diagnostic identifies duplicate
`shared_values`, but the correction gives no new wire format example.

1. Publish one complete wire grammar alongside the codec and use it in initial,
   structural correction, local replacement, full fallback and semantic revision
   processing prompts. It must explicitly state exact root keys, one occurrence
   of each JSON member, one definition table, unique `vN` names with the exact
   accepted pattern, exact-reference objects, literal marker escaping, finite
   acyclic references, validation of unused definitions, complete expanded
   payload obligations and the absence of implicit previous-fragment reuse.
   Keep all current duplicate/name/reference and fragment checks.
2. Add generation-order guidance supported by the existing grammar: emit the
   complete payload with explicit forward references, then one final
   `shared_values` table containing every chosen definition once. Root key order
   is not semantically significant to the current codec. A concrete multi-value
   example should show this order, nested references and a literal escape. State
   that a later definition change requires replacing its one entry in the final
   answer, never appending a second table. This is a proposed error-prevention
   measure, not evidence of future time savings.
3. Make the full correction retain the same complete wire grammar and supply
   typed, actionable wire examples when wire parsing fails. Do not auto-merge
   duplicate tables, invent a choice between unequal definitions, or reinterpret
   mnemonic names as valid ones. The model remains responsible for delivering a
   complete strictly valid replacement within the existing correction budget.
4. Before a later run, add offline prompt-contract tests that assert the actual
   grammar across every relevant path, rather than only checking for a `v0`
   example. Add strict regressions for identical, disjoint and conflicting
   duplicate tables; duplicate definitions; invalid and leading-zero identifiers;
   payload-first forward references; escapes; nested references; and complete
   malformed-candidate preservation through correction. Verify the seven normal
   requests, two workers, unchanged budgets, unchanged logical validation and
   plain/shared equivalence with injected answers. Existing tests should remain
   required; these cases close the newly observed prompt/codec mismatch.

This audit establishes a failed representation attempt and complete corrective
delivery, not semantic success or a latency improvement. The valid input display
still has the exact, source-complete reductions documented separately in
`graph-correction-and-processing-input.en.md`. The outcome of a002 and later
stages remains pending at this snapshot.
