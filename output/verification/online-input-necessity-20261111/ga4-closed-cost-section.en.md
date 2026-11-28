# GA4 closed-run cost, timing and provenance

The GA4 run `document-guided-ga4-input-necessity-high-20261111-173347` closed **failed at revision-processing**, not as a completed DOE analysis. It made 12 PID-confirmed native process starts: seven normal requests, two structural corrections, and three requests in the shared semantic repair phase. Eleven requests reported complete public token counters. The final revision-processing request reported no complete answer or public usage; its consumed tokens and any unreported internal-attempt usage remain **unknown**, not zero.

The exact known public total is **1,919,852 tokens: 1,649,821 input plus 270,031 output**. This is the sum of the eleven observed public completion records, not a complete provider billing total. Cached input is 199,936 tokens, already included in input; reasoning output is 36,993 tokens, already included in output. These subset counters must not be added again. The public events report zero cache-write input tokens. Provider HTTP-attempt counts, additional unreported attempt usage and monetary billing remain unavailable.

| Request category | Native starts | Complete-usage requests | Known input | Known output | Known total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal stages | 7 | 7 | 1,013,533 | 176,607 | 1,190,140 |
| Structural corrections | 2 | 2 | 408,945 | 28,771 | 437,716 |
| Semantic repair | 3 | 2 | 227,343 | 64,653 | 291,996, plus one unknown request |
| Total | 12 | 11 | 1,649,821 | 270,031 | 1,919,852, plus unknown usage |

The seven normal requests include responses that later required correction; a public final response is not evidence that its semantic content was accepted. All launch markers have matching PID records. There were no unconfirmed starts, pre-start input rejections or additional outer transport attempts.

## Per-request reconciliation

| Stage | Category | PID | Process seconds | Known public tokens |
| --- | --- | ---: | ---: | ---: |
| Flow | Normal | 21492 | 161.970 | 85,034 |
| Task | Normal | 27624 | 601.048 | 101,047 |
| Graph | Normal | 27556 | 1,521.554 | 128,259 |
| Processing | Normal | 27152 | 1,396.184 | 204,718 |
| Processing correction | Structural | 13008 | 317.066 | 180,366 |
| Sensitivity | Normal | 20012 | 296.807 | 198,167 |
| Task correspondence | Normal | 20712 | 587.317 | 223,553 |
| Source review | Normal | 13744 | 539.597 | 249,362 |
| Source-review correction | Structural | 13508 | 448.631 | 257,350 |
| Revised graph | Semantic repair | 2404 | 1,145.136 | 183,109 |
| Revised Task | Semantic repair | 25640 | 525.605 | 108,887 |
| Revised processing | Semantic repair | 14984 | 2,700.030 | Unknown |

The independent reconciliation reread `started.json`, PID/process receipts, every public `stdout.jsonl`, usage sidecars, saved metrics and replay markers. All eleven complete requests have one public completed-turn usage event; their integer sums agree with `metrics.json`. The failed request has no completed-turn event, an empty usage sidecar with `known=false`, and no substantive final answer. Source files and historical answers were not used to reconstruct missing usage.

## Timing and failure classification

The controller marker identifies PID 26552. It started at **17:34:28.720542 China time** and closed at **20:02:38.449316** on 2026-11-11. Marker elapsed time, including the sole replay and controller overhead, is **8,889.728774 seconds** (2 h 28 min 9.729 s).

The controller separately recorded **8,857.0556281 seconds** for analysis. The saved native activity span is **8,855.694890975952 seconds**, measured from the earliest native start to the latest native finish, including gaps and overlapping requests. The sum of individual process durations is **10,240.9438916 seconds**. That sum is larger because the two workers overlap; it is not additional elapsed controller time.

Revision-processing ran from **19:17:05.387430** to **20:02:05.417566 China time** in PID 14984, public thread `01a1ca53-65af-74d1-8a4c-24eb5a5c69af`. Its process receipt records `status=timeout`, exit code 1, and `CLI process exceeded its timeout`, after 2,700.0295512 seconds. The saved guided result preserves:

> CLI produced no complete answer; this is not an eligible transient network retry.

This classification was not changed by the audit. **Outer network retries were zero**, and the transport contains no `attempt-002`. No extra request was launched to recover this failed stage. The failed process's duration is known while its token usage is unknown.

## Internal reconnect evidence

The public standard-output streams contain **five `Reconnecting...` notices**: one in the original graph process and four in revision-processing. The graph process eventually completed; revision-processing did not. Its visible notices include request timeout, a disconnected stream with OS error 10054, and socket-access errors with OS error 10013.

A separate inspection of public standard-error logs found **seven `responses_retry` log lines**: two in the graph process and five in revision-processing. These are different observability layers for activity inside the same native processes. They overlap the stdout notices and must **not** be added together, counted as extra native starts, or converted from their ordinal labels into a provider HTTP-attempt count. No additional token amount can be inferred from either log stream. The exact logs and their hashes remain in the audit records.

## Sole replay and frozen provenance

The controller's sole replay started at **20:02:06.397818 China time**, took **32.0744694 seconds**, and returned `matched` with **zero new native launch markers**. Independent timestamp inspection found no marker at or after replay start. This verifies replay of the recorded failed workflow; it does not turn that workflow into successful propagation, DOE, or semantic validation.

The original closed-case provenance audit checked 194 pinned files and all 16 frozen source files. It found no current or snapshot implementation changes, no source/staging changes, and no helper or executable mismatch. The implementation SHA remains `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`; the source SHA remains `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. The audit status is `verified_with_usage_limitations`, with no run discrepancy recorded.

## Evidence and audit-helper correction

- Original closed audit: `cost-provenance-audit/ga4-20261111T120314320227Z.json`.
- Independent raw-record reconciliation: `ga4-closed-cost-independent-reconciliation-final.json`, including request/thread identities, direct counters, exact reconnect/retry logs, and hashes of the underlying public receipts.
- Initial independent recount: `ga4-closed-cost-independent-reconciliation.json`, preserved unchanged. Its strict dictionary comparison incorrectly flagged usage sidecars that omit the optional public `cache_write_input_tokens=0` key. Every counter actually present in those sidecars matches the raw event. The final reconciliation corrects only that helper comparison; both recounts already agree on token sums, starts, durations, unknown usage and replay. No run artifact or production code was changed.

These closed GA4 records were audited while the four-case implementation remained frozen. The later cases and their sole replays must also close and receive their original provenance audits before any post-batch implementation correction. No additional GA4 run or replay is authorized by this report.
