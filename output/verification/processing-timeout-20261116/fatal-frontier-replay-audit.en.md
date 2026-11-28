# Fatal semantic frontier: race diagnosis and offline acceptance

## Reproduced cause

The failure concerned fresh injected fixtures with no original assembled annotation. Initial processing failed structural validation; source review then requested Task/CFG repair. Revised Task and CFG ran concurrently. A fatal request failure stopped the phase, but replay scheduled their already recorded responses at different speeds.

Read-only inspection and diagnostic replay of the explicitly authorized synthetic `pytest-95` fixtures established the exact differences:

- With `revision-processing` as the primary failure, the saved run recorded `revision/task` as `complete`; the re-scheduled replay recorded it as `aborted` with the primary processing failure reason.
- With `revision/task` as the primary failure, the saved run recorded `revision-graph` as `complete`; the re-scheduled replay recorded it as `aborted` with the primary Task failure reason.

The primary failure reason and absence of selection were unchanged. These were execution-observation differences, not a different model answer or changed validation result. One synthetic run also contained a prepared `revision-processing` owner whose stage stopped at `before_call`, with zero calls, although the scheduler had not consumed its queued stage event before terminating. Sorting a set of completed futures cannot reproduce all such interleavings.

The failing receipt remains `repair-request-failure-task-03.xml` (19 passed, 2 failed). No historical GA4 process, artifact or replay was used in this diagnosis.

## Implemented boundary

New policy `fatal_phase_replay=recorded_artifact_bound_frontier_v1` belongs to the not-yet-launched guided v14 implementation. `fatal_frontier.py` records `audit/fatal-semantic-frontier.json` only after worker shutdown, and the final guided result binds its exact file digest. Existing artifacts are not migrated.

Eligibility is deliberately narrow: a confirmed recorded request failure during an early semantic phase, no selected annotation, no assembly-stage observation, and no propagation or DOE directory. Task keeps its v5 result protocol and existing fatal wrapper. This receipt never supplies a value, selects a partial revision, changes request budgets or enables backend continuation.

The receipt retains the observed guided state, current run-manifest binding, every actual prepared semantic owner, its manifest/result/execution-boundary references, every file in its call history, and the generated graph references. The call inventory covers failed transport receipts as well as successful requests and raw answers. A prepared but unobserved or zero-call sibling remains part of that inventory.

Replay verifies the execution evidence rather than sampling a second scheduling order:

1. Require the receipt and its exact final-result binding. Removing both the file and its reference does not restore scheduler replay for an otherwise eligible new failure.
2. Require the exact actual owner/call inventory, with no missing required owner, changed terminal receipt or missing transport. Require the bound run manifest to be this run's manifest.
3. Replay each actual Task and semantic-step owner using its recorded responses and unchanged validators. Validate each stage's source/CFG/processing/Task owner paths and dependency references against this guided run. Task revision input must equal this run's original Task and the original source-review objections.
4. Recompile/certify actual graph outputs. Replay actual source reviews with the same configuration and exact source, Task, CFG and available-fragment bindings. No stale review is attached to a revision or selected bundle.
5. Independently reproduce the primary recorded request failure. A failed call requires an intact transport trace matching its status, prompt, error type and reason, with no rejected-response or recording-failure marker. The same rule covers typed failed siblings.
6. Validate observed stage statuses against their reproduced terminal receipts. An `aborted` observer row remains an execution-frontier statement: its worker may have finished after the primary failure. Such rows are restricted to known semantic names in the same initial/revision phase, with the exact primary reason. They do not become accepted semantic values. Finally call the unchanged guided `_save(..., replay=True)` comparison over the complete bound state.

Successful runs retain their existing scheduler replay. Unknown failures, integrity errors and user interruption do not acquire original-bundle continuation through this mechanism. If frontier capture itself fails, the final result still records the original primary failure and adds `fatal_frontier_error`; this explicitly incomplete boundary cannot be replayed as verified. There is no model invocation in this helper.

## Offline results

- `fatal-frontier-existing-initial.xml`: all 24 existing request-failure cases passed, including both formerly intermittent no-original-annotation failures.
- `fatal-frontier-tests-initial.xml`: 12 passed and one failed test expectation; the implementation rejected a missing journal with `FileNotFoundError` while the test required an explicit `ValueError`. The later change adds the explicit missing-journal diagnostic. The original receipt is preserved.
- `fatal-frontier-tests-02.xml`: 16 passed after that diagnostic correction and integrity hardening.
- `fatal-frontier-tests-final.xml`: 19 passed, comprising the 16 new frontier tests plus the two no-original-annotation parameters and the initial-request-failure regression. This is the latest focused receipt after the final owner-binding changes.

Deterministic fixtures force both sibling-first and primary-failure-first observations for Task and processing failures. They preserve exact saved statuses, raw calls and zero new calls on replay. Additional cases verify a prepared zero-call interrupted sibling; missing journal/reference/both/owner/transport; changed final state; rebound forged primary reason, sibling status and unknown aborted stage; failed recording; and failed journal persistence retaining the true primary terminal result.

The latest distinct focused union is 40 passing cases: 24 existing request-failure cases plus 16 new frontier cases, with three existing cases also included in the final 19-case receipt. This is not a whole-repository all-green claim. Root owns the final broader affected regression, acceptance seal and sole fresh GA4 dispatch. All production/test edits for this subtask were frozen before root's final broad test.
