# Processing timeout investigation and the sole fresh GA4 result

The general implementation passed the final affected-scope regression (788/788,
no failures or skips), but the fresh online experiment **failed before an
accepted initial processing fragment existed**. It does not establish that the
previous revision-processing timeout has been solved. The new input presentation
retained the complete source and reduced the same-material initial processing
prompt by 12.53%. The attempted shared output was invalid; its one allowed
structural correction encountered three internal sampling retries and reached
the unchanged 2700-second native-process deadline.

This is the sole fresh run
`document-guided-ga4-processing-shared-high-20261116-225414`, launched on
2026-11-16 at 22:54 China time and closed on 2026-11-17 at 00:39. Analysis took
6287.714 seconds. Its sole controller-owned offline replay matched in 7.031
seconds with **zero new native starts**. All six native exits were confirmed;
the wrapper, controller and six recorded native PIDs were absent in the root's
separate process check. No second experiment or replay was started.

The frozen implementation is
`8ed018204232f0fc5ed2a26ae9c86d0d3055b900aee3583b5c8b17723d9316ed`.
All 206 pinned implementation/runtime files, controller helpers, executables,
and 16 source files remained unchanged. The source totals 155,170 UTF-8 bytes.
Requested model/provider/effort remained `gpt-6.1-sol/high/openai`; returned model
identity was not exposed in public response metadata. Seven normal semantic
requests and two workers remained the configured schedule; early failure meant
that only four normal requests actually started. Per-stage correction, shared
repair, timeout and outer transient-retry budgets were unchanged. Task v5
isolation and strict validation were preserved.

The previous closed revision-processing failure was a native total deadline,
not an input-cap rejection or a demonstrated connection-establishment timeout.
Its delivered input was 810,919 characters, below the 1,048,576 limit. Relative
to initial processing, the prompt grew by 270,953 characters; 239,300 (88.32%) of
that growth came from the prior fragment and repair context. The current CFG
grew from 679 to 770 IR, requiring a complete processing replacement. The source
section itself was unchanged. Three internal retry records show a prematurely
closed WebSocket, OS 10054 reset and request timeout. Initial processing answers
had required 1564.117 and 1679.002 seconds, with 62,249 and 66,789 public output
tokens. These are end-to-end native durations, not pure generation time.
Neither the old failed request nor the new failed correction exposes complete
output or final usage. TTFT, provider generation time, discarded output and the
allocation of time between network and computation remain unknown. See the
[original evidence audit](../processing-timeout-20261116/timeout-evidence.en.md).

The implemented remedy consists of exact shared processing input presentation,
an optional self-contained output representation with strict expansion checks,
passive public-event observation, and retention of the entire original bound
bundle after a confirmed failed semantic-repair delivery. It also makes early
concurrent request failure replayable through bound terminal-stage evidence.
There is no implicit reuse of old IR, truncated source, relaxed contract check,
extra model stage or enlarged budget. The complete offline implementation and
boundaries are described in [the design](../../../docs/doe/processing-timeout.md).
The 788-case execution is a scoped regression, not a whole-repository result.
Injected semantic replies exercised the successful pipeline and retained-bundle
failure behavior; this fresh online run did not reach semantic repair, so it
provides no online confirmation of that recovery path.

The new experiment separates three observed problems:

| Observed operation | Prompt characters | Complete answer characters | Native seconds | Result |
| --- | ---: | ---: | ---: | --- |
| Initial graph | 212,612 | 164,162 | 985.053 | Two read-before-definition roots and cascading graph errors |
| Graph correction | 376,241 | 164,092 | 934.197 | Structurally accepted: 237 blocks, 521 IR, 217 edges |
| Initial processing | 425,423 | 212,300 | 1535.208 | Duplicate `shared_values`; strict JSON rejection |
| Processing correction | 675,293 | unavailable | 2700.039 | Native timeout after internal reconnects |

Prompt values exclude the fixed 212-character delivery envelope. No input was
rejected before native start. The actual processing deliveries were 425,635 and
675,505 characters. The comparison is not a controlled latency benchmark:
generated CFGs and outputs differ across historical runs, and network events
intervened.

For the initial processing request, the current exact logical input body shrank
from 252,386 to 190,095 serialized characters. Including presentation
instructions, the same-material plain prompt would have been 486,361 characters,
versus the actual 425,423: 60,938 fewer characters (12.53%). All 16 source files
were rendered in full. Exact codec expansion concerns the actual logical input;
the pre-existing CFG display also avoids repeating 294 `script_content` copies
already present exactly in that complete source. No other CFG difference was
found in this comparison. This establishes a character reduction, not measured
token or generation savings. See the [input audit](graph-correction-and-processing-input.en.md).

The initial processing answer used two root `shared_values` members, one before
and one after `payload`. The first table had 266 definitions; the second had 310.
Among 241 shared names, 81 had unequal exact values. They are not necessarily
81 semantic contradictions, but choosing or merging either table would not be
lossless. All names were mnemonic, although the codec requires the exact pattern
`v(?:0|[1-9][0-9]*)`. The prompt illustrated `v0` without explicitly stating that
grammar. The duplicate-key rejection prevented subsequent codec/semantic
validation; the name mismatch is a static forensic finding, not an additional
executed validation receipt. This is a real prompt/protocol gap missed by the
offline acceptance scope. It must be fixed without accepting ambiguous tables
or silently renaming model output.

The correction retained the original prompt and the entire rejected answer as
an exact string. Escaping that string required 248,702 characters. A complete
joint shared alternative was 430 characters longer, so choosing the shorter
complete fallback was correct. The correction supplied the duplicate-key
diagnostic but no additional explicit wire grammar. There is no valid expanded
output size or output-compression result from this experiment. See the
[rejected-answer audit](processing-initial-response-audit.en.md).

The failed correction's network evidence is:

| UTC event on 2026-11-16 | Seconds since native start | Public cause | Internal retry/backoff |
| --- | ---: | --- | --- |
| 16:09:40.309444 | 899.753 | Connection reset, OS 10054 | 1/5, 196 ms |
| 16:09:55.533043 | 914.977 | Request timed out | 2/5, 377 ms |
| 16:25:12.304769 | 1831.748 | Server closed WebSocket before response completion | 3/5, 802 ms |
| 16:39:40.596233 | 2700.039 | Native process exceeded its total timeout | Confirmed exit, return code 1 |

The two stdout reconnect notices overlap retries 2 and 3; they are not two
additional retries. Twelve auxiliary model-list refresh timeout lines are
separate from sampling. The three reported backoffs sum to 1.375 seconds, which
does not measure the duration or cost of the failed internal attempts. Intervals
near 900 seconds do not establish a fixed idle timeout. The public observer
records conservative host intervals for complete events; it cannot recover token
deltas or discarded responses. No outer retry was made, as total timeout remains
ineligible under the existing policy.

Actual cost is **6 native starts = 4 normal + 2 structural corrections**; there
were no semantic-repair starts. Five complete public usage receipts total
**670,215 tokens**: 508,646 input and 161,569 output. Cached input (39,936) and
reasoning output (15,588) are subsets, not additions. Usage for the failed
correction and any internally unreported work is unknown; no currency estimate
is available. The malformed complete answer still contributes its actual usage.

Only Task, flow and the initial graph were accepted. There is no selected
annotation, source review, task-correspondence fragment, sensitivity fragment,
semantic revision, propagation result, input assessment or DOE result. Those
downstream measures are **not run / unknown**, not zero required or deletable
fields. The generated graph represents all 13 direct remote source sites and
25 `saveResult` callers, but this is not actual propagation coverage. Seven
remote sites still describe some client/property dependencies in effect text;
caller-to-writer wrapping, unused `filters`/`orderBy` reads and summary/member
pairing remain unreviewed source concerns. See the [final source audit](final-source-coverage.en.md).

The result supports the prioritized [follow-up proposal](followup-plan.zh.md):
first synchronize the complete output grammar and generation examples with the
strict codec, then give the existing single correction all independently
definite representation diagnostics, and separately fix causal graph diagnostics
and dependency-scoped correction. The graph's two primary errors led to a full
replacement that changed four operational blocks and many descriptions; the
original two diagnostic records alone were not sufficient repair scope. Any
localized correction must preserve complete reference context and full
post-merge validation, with full replacement when needed. Network recovery
remains independently uncertain under the unchanged budget. These are proposals
based on this frozen run, not implemented or experimentally validated follow-ups.

The authoritative receipts and hashes are linked in [run-summary.json](run-summary.json).
All earlier failures, raw answers and closed runs remain preserved. This run and
its sole replay are closed; the one-run authorization is consumed.
