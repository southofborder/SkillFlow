# Initial processing correction: public network, size and timing evidence

Provisional observation, 2026-11-16 16:10:49–16:12:35 UTC (2026-11-17 00:10:49–00:12:35 China). This concerns the first processing stage's single structural correction, not a semantic repair round or `revision-processing`. The request remains active; there is no final outcome or native deadline receipt yet.

The native stderr reports two sampling retries inside the same correction process:

| Public UTC timestamp | Time since native start | Ordinal | Recorded cause | Reported backoff |
|---|---:|---|---|---:|
| 2026-11-16 16:09:40.309444 | 899.753 seconds | 1/5 | Connection reset, OS error 10054 | 196 ms |
| 2026-11-16 16:09:55.533043 | 914.977 seconds | 2/5 | Request timed out | 377 ms |

The sole public stdout error reports reconnect ordinal 2/5 with a request timeout. Its host observation interval is 16:09:40.794849–16:10:10.806635 UTC, which contains the second stderr timestamp. It is overlapping evidence, not a third independently established retry or another native launch. The ordinal describes CLI-internal sampling retry bookkeeping; it does not establish a complete provider HTTP-attempt count.

Nine auxiliary model-list refresh timeout lines are recorded across the six native processes. The active correction's refresh timeout is at 15:54:45.862713 UTC, only 5.306 seconds after native start. This auxiliary request is separate from the two later sampling retries. No connection-wait retry lines or other completed public tool/command item types were observed in this snapshot.

The correction process began at 15:54:40.556330 UTC. Its configured total native deadline remains 2,700 seconds. The public text `request timed out` at approximately 915 seconds is not a receipt that this total deadline expired, and it does not establish a connection-establishment timeout. Public evidence does not partition the elapsed request time into provider generation, server wait, network wait or reconnect work.

The complete initial processing request and correction delivery sizes are:

| Request | Delivery characters | Delivery UTF-8 bytes | Completed answer characters | Completed answer UTF-8 bytes | Native elapsed |
|---|---:|---:|---:|---:|---:|
| processing a001 | 425,635 | 426,062 | 212,300 | 212,302 | 1,535.208 seconds |
| processing a002 structural correction | 675,505 | 675,934 | Not yet observed | Not yet observed | Active; final duration unknown |

The initial processing final message was first observed between 15:54:34.524652 and 15:54:39.376724 UTC. Its public usage is 141,467 input plus 60,888 output tokens, totaling 202,355; 2,519 reasoning output tokens are a subset. The native answer completed, but the saved structural validator rejected it with `duplicate JSON member: shared_values`. A completed transport answer and a semantically accepted processing fragment are different facts.

The new sidecars expose whole public event observations, not token deltas. The interval above is therefore not time to first token or the duration of output generation. The absence of a completed final message for a002 does not prove that the provider has generated no output. Time to first token, provider generation duration and unreported usage remain unknown.

At the 16:10:49 UTC cost snapshot, six confirmed native starts comprise four normal requests and two structural corrections. No semantic repair or outer retry has started. Five complete public usage receipts total 670,215 tokens: 508,646 input and 161,569 output. The 39,936 cached input and 15,588 reasoning output tokens are subsets of those totals. The active correction's usage is unknown and is not counted as zero.

All 206 pinned implementation files, all 16 source files, controller/timing helper and CLI/Python/renderer executables still match the frozen run identities. The v14 passive auditor reports no issues. The earlier v13 auditor assertion remains preserved with its explicit reconciliation; no frozen runtime or original audit snapshot was changed.

Evidence:

- `cost-provenance-audit/ga4-20261116T161049055774Z.json`: cost, protocol and frozen provenance snapshot.
- `cost-provenance-audit/public-surface-20261116T161046798545Z.json`: public types and sampling retry causes.
- `cost-provenance-audit/public-observation-20261116T161140042631Z.json`: complete delivery sizes, final-message metadata and host observation intervals.
- `cost-provenance-audit/public-network-20261116T161235661817Z.json`: native retry timestamps, start-relative offsets and separately classified auxiliary notices.
- Run-local `steps/processing/calls/a001/validation.json`: structural rejection evidence.

This passive audit read no private sessions or reasoning bodies and performed no model call, Skill execution, replay, process control or runtime edit. The controller retains sole ownership of the authorized replay. Further cost and timing claims require the final receipts.
