# Final processing presentation and output assessment

The sole fresh GA4 failed during the initial processing stage's structural
correction. It did not reach semantic repair or `revision-processing`. There is
no accepted processing fragment, source contract review, propagation, input
assessment or DOE result from this run. The final selected annotation is null.

Run: `experiments/doe/runs/document-guided-ga4-processing-shared-high-20261116-225414`.
Accepted implementation stayed frozen at
`8ed018204232f0fc5ed2a26ae9c86d0d3055b900aee3583b5c8b17723d9316ed`.
All conclusions below come from saved current-run bytes, passive parsing and
presentation codecs. This audit invoked no validator, backend, Skill or replay.

## What the new presentation actually achieved

The initial processing stage prompt is 425,423 characters. Its complete
structured body expands exactly from 190,095 to 252,386 logical characters,
saving 62,291 characters, or 24.68% of that body. The same current logical
material in the previous plain input sections, with the same source and output
guidance, would be 486,361 characters: actual stage-prompt savings are 60,938
characters, or 12.53%. This is same-material character accounting, not another
request, a historical latency comparison or token savings.

All 16 source files and 155,170 raw source bytes match their saved identities.
The full 180,825-character line-numbered source appears exactly. All 521 current
CFG IR appear in the structured logical input. The exact input expansion is
distinct from equality to the raw CFG artifact: the existing source display
omits 294 duplicate `script_content` fields whose code is already in the complete
source. Removing only those repeated metadata fields reproduces the displayed
CFG exactly. No source or contract obligation was truncated to achieve the new
shared input reduction.

The correction keeps the complete initial prompt as an exact prefix and adds the
entire rejected raw response. Its stage prompt is 675,293 characters. Complete
native deliveries, including the separate 212-character transport suffix, are
425,635 and 675,505 characters respectively; the transport audit measures those
delivery sizes. These two measurement boundaries must not be mixed.

## Why the two processing attempts failed

| Attempt | Saved outcome | Native process elapsed |
| --- | --- | ---: |
| a001 | Complete 212,300-character shared-format attempt; rejected at JSON parsing for duplicate root `shared_values` | 1,535.208 seconds |
| a002 | No complete answer; native process timeout, exited true, return code 1 | 2,700.039 seconds |

In a001, the root order is `format`, `shared_values`, `payload`, `shared_values`.
The two tables have 266 and 310 entries. Their 241 overlapping names include 160
identical values and 81 unequal exact values; there are 25 first-only and 69
second-only names. The unequal values include prose differences and must not be
called 81 proven semantic contradictions. Neither an automatic merge nor
first-/last-wins selection is lossless. Strict duplicate rejection was correct.

The raw names also expose a prompt/codec mismatch: every definition name in both
tables violates the codec's required `v(?:0|[1-9][0-9]*)` grammar. The initial
output instructions show `v0` but do not explicitly state this rule. a002 repeats
that guidance unchanged and adds only generic full correction instructions plus
the duplicate-key diagnostic, with no wire-format examples. This static mismatch
is not an additional executed validator finding: the authoritative validation
stopped at the duplicate key.

There is no accepted expanded a001 response or valid output-compression ratio.
The raw pair-tree inventory is forensic only. No fragment schema, IR coverage,
contract completeness or source correctness was established by that attempt.

The correction preserves the exact raw candidate as a string. Escaping it for
JSON contributes 248,702 characters; complete correction context is 248,883
characters. Joint input packing would yield a 675,723-character prompt, 430
characters longer than the saved fallback. Choosing the existing full fallback
was therefore correct; repeated subtrees inside an invalid opaque string cannot
be deduplicated as an accepted logical fragment.

a002's saved process receipt is `status=timeout` with the explicit error
`CLI process exceeded its timeout`. Its call ends at
`2026-11-16T16:39:40.609049+00:00` with `ModelRequestFailure` and no saved response,
validation or normalization artifact. The process receipt records elapsed
2,700.039 seconds. The public network audit independently records a connection
reset, a request timeout and a server-closed WebSocket during this same process.
Those events establish connection trouble; they do not apportion the 2,700
seconds into generation, server waiting, networking and retry work. The final
cause recorded by the host is the total native deadline, not a demonstrated
connection-establishment deadline. Complete output size and failed-request usage
remain unknown. A larger correction prompt is measured; its causal contribution
to the timeout is not separately measured.

## Graph correction also increased whole-response work

Before processing, graph a001 had two read-before-definition errors in loop
heads. The compiler omitted those rejected blocks while retaining their declared
edges, causing a root missing-endpoint diagnostic. That root diagnostic defeated
the local two-record selection and caused complete graph regeneration. Graph
prompt sizes rose from 212,612 to 376,241 characters. Native graph response sizes
were 164,162 and 164,092 characters, with elapsed times 985.053 and 934.197 seconds.

The two offending raw head records total 1,250 compact characters, but this is
not a sufficient repair scope or a savings estimate. The original rejected graph
lacked distinct carry producers on the reject backedges. The accepted structural
correction changed both heads and both bodies, adding retained-accumulator
producers. Its 110 changed block objects also include 105 metadata-only changes
and one constraint paraphrase. Global constraints rose from five to six. Strict
structural acceptance of the corrected 521-IR CFG does not prove source
correctness of those changes; source review was never reached.

## Terminal evidence and limits

The saved analysis ended at `2026-11-16T16:39:40.920918+00:00` after 6,287.714
seconds. The controller ended at `16:39:48.628006+00:00`. Actual native starts were
six: four normal requests and two structural corrections. The intended seven
normal requests, two workers and all existing budgets were unchanged; later
normal stages were not reached. No shared semantic repair was used.

The controller-owned sole replay reports `matched`, 7.0309 seconds, zero new
native markers. All six native exits are confirmed and the implementation check
reports unchanged. These facts are read from receipts, not a replay initiated by
this audit. The final result binds the fatal frontier receipt with SHA-256
`6f5fb3dc13b46aee430150907a277ff1fc03b355d99ef547ff426ce9e10e8b89`.
The complete artifact hash inventory and selected final fields are in
`processing-final-receipt-bindings.json`.

The result supports exact source-complete input-size improvement, correct strict
rejection and successful terminal replay. It does not demonstrate successful
output compression, lower elapsed time, semantic contract accuracy or completed
DOE. Ranked follow-up changes are proposal-only in
`processing-result-followup-proposal.en.md`.

Supporting detail: `graph-correction-and-processing-input.en.md`,
`graph-correction-preliminary.en.md`, `processing-initial-response-audit.en.md`,
`processing-initial-rejected-pair-forensics.json`,
`processing-initial-correction-codec-size.json`, and the separate public network
and cost audit. The latest passive presentation snapshot is
`presentation-audit/20261116T164046689069Z.json`.
