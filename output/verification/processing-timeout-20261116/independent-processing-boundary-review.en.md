# Independent processing boundary review

Review date: 2026-11-16. Read-only review of the new processing input presentation, response expansion, correction integration and guided repair-request fallback. No production `src` file or historical artifact was edited by this reviewer.

## Actionable finding

P2: a confirmed-ended request failure in the revised Task stage does not reach the new original-bundle retention path. `skillflow.task.runner.run_task` catches `ModelRequestFailure` or `InputTooLarge` and returns `status="execution_error"` with `error_kind` naming the original error. In the guided runner's Task job, that outcome is converted to a generic `RuntimeError`. `_confirmed_request_failure` therefore returns false, even when the original Task/CFG/annotation/review bundle is complete. The run terminates before analyzing that original bundle. This is the same delivery failure handled successfully for revision graph, processing, correspondence and sensitivity stages.

The focused fallback regression matrix currently names those four stages but omits `revision/task`. Extend it with a revised Task failure and zero-call replay. Preserve the Task interface and source isolation: recover the narrow error classification from the verified Task result and its durable failed-call record, including the `recording_failed` marker. Do not turn unknown native state, integrity errors, recording errors or user interruption into fallback eligibility.

Locations reviewed: `src/skillflow/document_guided/runner.py`, Task job around lines 325-343 and `_confirmed_request_failure` around line 56; `src/skillflow/task/runner.py`, exception-to-result conversion around lines 352-356; `tests/document_guided/test_repair_request_failure.py`, parametrized stage matrix.

## Other reviewed boundaries

The processing response shorthand is self-contained. It rejects malformed envelopes, duplicate JSON keys, missing or cyclic references, invalid unused definitions, literal-marker collisions and unsupported expansion sizes/depths. It creates independent copies and then runs the existing fragment schema, ownership, coverage and application validators. Plain complete responses remain accepted by their existing path.

Semantic correction diagnostics use expanded fragment coordinates. Existing-record corrections still validate exact allowed record identities; full corrections preserve the complete candidate. Raw model responses remain separate from merged expanded candidates, and replay rebuilds the same decisions. The response shorthand does not supply missing IR records from definitions or inherit records from an old fragment.

The input presentation encodes program-constructed complete logical inputs and verifies an exact expansion round trip. Its source suffix is separate and retained. Processing still receives only flow, CFG, runtime contract and applicable repair/correction material, without the sealed Task. Shared values do not merge semantic identities or mutable occurrences.

For the directly propagated typed repair failures, the guided fallback retains the complete original selected bundle and its original bound review. Revised fragments are not combined with original fragments to synthesize an annotation. Unknown-state errors and interruptions remain terminal. Replay consumes recorded calls without constructing a live client. I found no additional actionable issue in these inspected paths; this is a scoped code review, not a proof of semantic accuracy or a whole-repository audit.

## Telemetry setup follow-up

The reviewer-owned transport now also guards observer construction inside the existing process lifecycle try block. Optional setup failure records a warning and continues with the original native request. `KeyboardInterrupt` is not swallowed: it records an interrupted lifecycle and propagates. Three new fake-process tests cover completion, timeout and interruption at observer setup.

Latest transport evidence: `transport-setup-final.xml` passes 59 focused client/metrics/observer cases. Together with the earlier run-configuration coverage and final metrics case, the latest scoped union is 69 distinct passing tests with no unresolved failures. See `transport-offline-acceptance-r2.json`; earlier receipts remain preserved. No native/model process, Skill, probe or historical replay was started.
