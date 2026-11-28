# Revision-processing timeout: public evidence and general remedies

Date: 2026-11-16. Closed run: `document-guided-ga4-source-review-locality-high-20261113-203902`.

The terminal failure was the configured **2,700-second native-process deadline**. Three public sampling reconnection events establish interruptions during the request. The available public artifacts do **not** establish that connection setup, model generation, or network waiting alone consumed the deadline. The revised request also carried more material and required a larger complete processing result; these are measured workload risks, not a measured causal allocation of the failure.

This audit used only saved public artifacts and read-only source inspection. It did not run a model, Skill, replay, validator or backend. The closed run, failed request and earlier reports remain unchanged. `timeout-evidence.json` binds the 37 artifacts read by SHA-256; `audit_timeout_evidence.py` records the exact counting procedure. Source locations below refer to the inspected source hash recorded in that JSON, rather than a future version of the file.

## Network events and deadline

The request began at **2026-11-13 15:41:00.352228 UTC**. Its native receipt ended at **16:26:00.385522 UTC**, reporting `status=timeout`, `exited=true`, `returncode=1`, and `elapsed_seconds=2700.03195959999`.

| Public event | UTC | Seconds after native start | Meaning |
|---|---|---:|---|
| Auxiliary model-list refresh timeout | 15:59:17.055329 | 1,096.703 | An auxiliary CLI operation failed; this is not a semantic request or sampling retry. |
| Auxiliary model-list refresh timeout | 16:03:52.075768 | 1,371.724 | Same classification. |
| Sampling retry 1/5 | 16:05:29.802676 | 1,469.450 | Server closed the WebSocket before `response.completed`; logged backoff 199 ms. |
| Sampling retry 2/5 | 16:09:39.612725 | 1,719.260 | Connection reset, OS error 10054; logged backoff 362 ms. |
| Sampling retry 3/5 | 16:09:54.995480 | 1,734.643 | Sampling request timed out; logged backoff 834 ms. |
| Native total deadline | 16:26:00.385522 | 2,700.032 | The wrapper stopped the native process at its existing total budget. |

Two stdout `error` records repeat the second and third reconnect notices; they are not additional retries. The logged backoffs sum to **1.395 seconds**, which measures only the announced waits, not the duration of failed requests, retransmission, reprocessing or server work. There are about **965.4 seconds** between the last logged sampling retry and the native deadline. No public event attributes that interval to a specific activity. The absence of an earlier sampling warning does not prove uninterrupted generation before the first warning.

The transport starts a monotonic native-process timer and repeatedly waits for at most 30 seconds, using the remaining part of the same total deadline (`tools/doe/document_guided_client.py`, lines 204, 213–218, 240). A timeout receipt is ineligible for the outer transient-retry branch (lines 286–303). Thus this request has **one native start and zero outer retries**, despite CLI-internal reconnects. The terminal generic `ModelRequestFailure` describes failure to obtain a complete answer; it should not be presented as a measured connection-establishment timeout.

The raw evidence is under the closed run's `transport/revision-processing/38bb1c0deb7a6ebcc944c7d167e0f4bd77ec9a250f41c7558a1ea98e7143c8ed/attempt-001/`: `started.json`, `process.json`, `stderr.txt` and `stdout.jsonl`.

## Input and output scale

Counts below use **Unicode code points**, matching the adapter check. UTF-8 byte counts and UTF-16 code-unit counts are separately recorded in JSON. Native delivery adds the same 212-character envelope to each prompt.

| Request | Prompt characters | Complete native delivery | Public input tokens | Complete answer characters | Public output tokens | Native elapsed seconds |
|---|---:|---:|---:|---:|---:|---:|
| Initial processing a001 | 539,754 | 539,966 | 161,172 | 222,846 | 62,249 | 1,564.117 |
| Initial processing correction a002 | 775,426 | 775,638 | 227,128 | 244,456 | 66,789 | 1,679.002 |
| Revision graph a001 | 485,075 | 485,287 | 148,430 | 215,228 | 50,022 | 1,258.504 |
| Revision processing a001 | 810,707 | 810,919 | Unknown | No completed answer | Unknown | 2,700.032, timeout |

The failed revision delivery was **237,657 characters below** the 1,048,576-character adapter limit. It passed that check and started the native process. This was not another source-review input-size rejection.

Compared with the initial processing prompt, the revision grew **270,953 characters / 50.20%**:

| Section | Initial characters | Revision characters | Increase |
|---|---:|---:|---:|
| Previous work: flow and CFG | 283,532 | 313,992 | 30,460 |
| Runtime contract | 22,039 | 22,413 | 374 |
| Source-review repair context | 0 | 239,300 | 239,300 |
| Related source | 180,842 | 180,842 | 0 |
| Required IR IDs | 6,129 | 6,948 | 819 |
| All remaining instructions and schema | 47,212 | 47,212 | 0 |

The repair section accounts for **88.32% of the prompt increase**. Its compact JSON values comprise the entire prior processing fragment (**228,473 characters**) and 41 source-recheck records (**10,763 characters**), plus keys and section delimiters. The complete source section is **exactly equal** between the two prompts. Source duplication or a changed source package did not explain this increase.

The CFG grew from **268 blocks / 679 IR / 252 edges** to **302 blocks / 770 IR / 283 edges**. The revised processing stage was asked to return complete coverage for all 770 current IR, **13.40% more IR**, while carrying the full old fragment as repair context. This is a general full-rebuild scaling issue; it is not specific to GA4 API names.

The initial correction also illustrates avoidable repeated payload: it includes the entire initial prompt as an exact prefix and adds **235,672 characters**, including a 222,118-character compact candidate and 12,469-character diagnostic context. A missing-IR coverage diagnostic required a complete replacement. Of the 630 earlier `ir_semantics` rows, **306 were exactly equal in the next answer**, 324 changed, and 47 new rows appeared. These equality counts establish repeated material; they do not establish that any particular row could safely have been accepted without validation.

Completed processing output contains exact structural repetition. In a002, `evidences` occurs 905 times; its values occupy 58,478 compact JSON characters, including 316 instances of the same 20-character reference. The same 56-character `output_bindings` list appears 263 times. `input_contract` values occupy 42,324 characters and `demand_transfer` values 24,584 characters. These nested aggregate statistics overlap and must not be added together. They identify opportunities for exact table/reference encoding, not source or contract omission. Character savings are not a token or elapsed-time measurement.

## What is known about generation time

The three completed native requests in the table contain only `thread.started`, `turn.started`, one final `item.completed` agent message and `turn.completed`. They contain **no token-delta events or event timestamps**. The failed revision has only the thread/turn starts and two reconnect notices, with no completed message or usage.

For the completed requests, public output tokens divided by total native wall time are approximately **39.798, 39.779 and 39.747 tokens/second**. These are **end-to-end completed-output throughput**, including server work, submission, network and process overhead. They are not measurements of model-only decoding speed, time to first token or reasoning duration. They cannot be used to reconstruct tokens generated or discarded during the failed revision.

The defensible conclusion is joint risk: a larger all-IR rebuild and a long response requirement coexist with documented sampling interruptions under a fixed 45-minute native deadline. The present artifacts cannot prove which factor dominated. Failed-request input/output usage, discarded generation, provider-internal retry work and billing remain unknown. The earlier batch total of 2,862,874 public tokens excludes unknown usage from this request.

## General remedies within the existing budget

1. **Use a strictly reversible processing representation on both sides of the request.** Share exact repeated evidence, binding and contract structures through a versioned table/reference format, including previous processing context and generated answers. Bind the dictionary and source/CFG/annotation identities, bound expansion, reject invalid references/cycles, expand completely, and run the existing validators unchanged. Preserve every source line, input observation, contract scope and local gap. Compressing only input does not address the already large output.
2. **Support complete validated correction/revision expressions with explicit reuse.** A correction should be able to retain eligible unchanged records and replace failed/new records without resending all values. Every current IR must still be covered exactly once after expansion. Same IR names are insufficient when the CFG has changed: reuse must validate operation bindings, evidence, location definitions and dependent identities. No invalid record may become accepted by omission. A broad semantic change may still require broad replacement.
3. **Record bounded public event-arrival times during the existing native call.** Distinguish native total-deadline failures, auxiliary refresh failures and sampling interruptions in diagnostics. This adds observability without an extra model call or larger budget. Local arrival time is not server generation time; if the CLI publishes no token delta, true TTFT remains unavailable. Do not collect private sessions or hidden reasoning to fill that gap.
4. **Verify offline, then evaluate the one newly authorized fresh GA4 run.** Keep seven normal semantic requests, two workers, the 2,700-second deadline and existing correction/shared-repair/transport retry budgets. Verify exact expansion, stale identity rejection, complete coverage, strict validation and review locality. Measure the fresh request and answer size, public timing, corrections, selected coverage and actual cost. Do not resume this closed run, add per-IR calls, truncate source, omit contracts or infer success from compression alone.

The parent agent owns implementation choices and fresh-run dispatch. These recommendations are a diagnosis and a constrained design proposal; they do not claim that the timeout has already been resolved.
