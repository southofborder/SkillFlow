# Public transport observability audit

Status: read-only diagnosis and implementation proposal, 2026-11-16. No production file, closed artifact, model request, Skill execution, replay, or process probe was changed or started for this audit.

## What the present client can establish

`tools/doe/document_guided_client.py` preserves the complete delivered prompt, a request identity and digest, native launch arguments, a start timestamp, PID, public stdout and stderr, native exit status and elapsed time. Accepted final text and optional public token usage are retained. `tools/doe/document_guided_metrics.py` separately distinguishes native starts, structural corrections, outer retry attempts, final-associated usage, partial counters and unknown counters.

The native process writes directly to `stdout.jsonl` and `stderr.txt` (`Client._execute`, currently lines 206-209). Its `communicate()` loop checks the existing deadline in intervals of at most 30 seconds (lines 212-224). The client only parses public stdout after `_execute` has returned (lines 286-292). Consequently, the existing artifacts do not record when the host first received a public stdout event or how much output was present before each reconnect. Start-to-exit time is measurable; actual prefill duration, time to first generated token, uninterrupted generation duration and provider-side retry duration are not.

The public CLI event interface accepted by this client exposes completed `agent_message` items, not a proven token-delta stream. A long delay before the first completed message must not be labeled time to first token. Dividing final output tokens by the entire native elapsed time gives an end-to-end effective rate, not a measured decoding rate. File modification time is not a substitute for arrival timestamps.

Public stderr reconnect timestamps are useful evidence of reported disruptions, but they do not apportion the total request duration. Auxiliary model-list refresh failures must remain separate from sampling failures. A stdout reconnect notice and a stderr retry line may describe the same event; neither is an additional native process start. An outer native deadline is separate from a specific connection-establishment timeout.

## Minimal general instrumentation

Add an optional public-observation sidecar to every new native attempt. Sample at the existing `communicate` polling boundary and once after confirmed exit or attempted termination. Do not change the native command, request count, retry eligibility, timeout, analysis worker count, response acceptance or validation. A monitoring error must never cause a resend or invalidate a completed answer.

For each sample retain the host UTC observation time, monotonic elapsed time, previous sample time, stdout/stderr byte positions, newly completed public stdout line positions and event types. For a completed final `agent_message`, additionally retain only its phase, Unicode character count, UTF-8 byte count and SHA-256. Record public `turn.completed` presence without treating it as complete accepted-answer usage; the existing metrics association remains authoritative. Record partial-line byte counts and terminal file sizes so output without a final complete JSON line is distinguishable from no public output. Raw stdout and stderr remain byte-identical.

These are host observation intervals, normally no wider than the existing 30-second poll interval plus local scheduling/monitoring delay. Preserve both interval endpoints and never advertise them as exact provider event times or a guaranteed 30-second bound. Lines that lack a trailing newline are only classified when the native attempt ends. No private session, hidden reasoning, provider network trace or additional process is needed. Ignore all other item bodies; do not place source text, model text, command strings or reasoning text into the sidecar.

Store complete delivery character and UTF-8 byte sizes in separate optional monitoring metadata alongside the existing immutable prompt digest. Store final answer sizes only when a completed final exists. Do not invent a token count from characters. Observability for legacy attempts remains unavailable; do not create sidecars retrospectively in closed runs.

Have passive metrics expose the observation availability, terminal observed file sizes, first-public-event and first-completed-final intervals, and count of observed complete stdout lines. Keep `provider_generation_seconds`, `first_token_seconds` and `http_attempts` unknown unless a future public protocol actually supplies those quantities. An optional monitoring sidecar should have its own small format identity; the transport request and acceptance protocol need not change merely to add monitoring.

## Implementation locations and tests

Implement the incremental observer in a small new helper such as `tools/doe/document_guided_observation.py`; call it from `Client._execute` without replacing the current file redirection or retry loop. Extend `document_guided_metrics.py` with optional sidecar loading. Existing client and metrics tests already use fake processes and public fixture events exclusively.

Add fake-process tests for normal completion, public events arriving across two existing poll intervals, deadline expiry, interruption and launch failure. Assert the original command, exact delivered bytes, timeout, outer retry count, native start count and accepted answer remain identical. Verify a native timeout does not become an eligible outer retry merely because stderr contains a reconnect.

Add parser tests for a UTF-8 character split across reads, a JSON line split across reads, a terminal valid line without newline, malformed rows, repeated polls with no extra bytes, final-message phase filtering, an unrelated item body, and size distinctions between Unicode characters and UTF-8 bytes. Sidecar rows must contain no original message text or reasoning text, and file contents must be unchanged after monitoring.

Add monitoring-failure tests for an unwritable sidecar, unavailable stdout snapshot and a malformed optional record: completed answers must still be accepted, failed requests must preserve their original failure, and no extra process may start. Add passive metrics tests that old attempts without sidecars remain unknown, incomplete observations never claim exact token timing or zero missing work, and optional observations cannot upgrade partial usage to complete usage.

Instrumentation improves attribution for the next authorized run; it cannot itself make the request complete faster or guarantee that the unchanged 2700-second budget will suffice. Reducing repeated input and emitted processing syntax while preserving source, contracts and strict validation is a separate implementation decision owned by the processing design audit.
