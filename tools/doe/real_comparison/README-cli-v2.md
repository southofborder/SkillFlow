# Approved fresh CLI engineering transport v2

This is a separate, versioned adapter. Existing v1 Python modules, protocol,
material seals, evaluation rules, original stopped collaboration calibration and
successful one-request feasibility probe are preserved. The effective
`cli-protocol.json` governs the new transport. `inherited-v1/` is historical
provenance and does not impose collaboration-spawn semantics on CLI receipts.

The new run is permanently `calibration_only: true`. It contains the three
familiar packages `gh-fix-ci`, `netlify-deploy`, and `transcribe`, copied from the
frozen baseline inputs. It imports no v1 case selection, source reference,
human submission, target answer, graph, or completed native output. Every
calibration begins with the current unchanged native `_native_pipeline` and a
fresh workflow identity. A failed or interrupted workflow is retained; this API
does not retry it or select a replacement. Native downstream semantic repair
retains the existing at-most-one-round policy.

Formal requests are unconditionally rejected in this run, including when a
`gate.json` claims approval. The prospective long-source comparison needs its
own cohort, materials, references, actual human confirmations, implementation
binding and formal adapter/gate. These calibration APIs cannot open that gate.

## Preparation and execution

Run these from the project root with the project's Python environment. Only
`dispatch-next` starts a target process. Preparation, verification, pending and
summary commands make zero model calls. `worker` runs local native orchestration
and waits for the separate dispatcher to satisfy its mailbox requests.

```powershell
python -m tools.doe.real_comparison.cli_amendment prepare --run-dir D:\projects\SkillFlow\experiments\doe\runs\real-same-model-v2-cli-TIMESTAMP --original-run D:\projects\SkillFlow\experiments\doe\runs\real-same-model-v1-20261020-090239Z --decision-record PATH_TO_ACTUAL_ADOPTION_RECORD.json --executable C:\Users\24831\AppData\Local\OpenAI\Codex\bin\896a0166b774037a\codex.exe
python -m tools.doe.real_comparison.cli_amendment verify --run-dir NEW_RUN
python -m tools.doe.real_comparison.cli_amendment worker --run-dir NEW_RUN --case-id gh-fix-ci
```

While that worker is active, a separate supervisor uses:

```powershell
python -m tools.doe.real_comparison.cli_amendment pending --run-dir NEW_RUN
python -m tools.doe.real_comparison.cli_amendment dispatch-next --run-dir NEW_RUN
```

Dispatch each newly queued request once. Continue servicing the same worker
until its native terminal result exists. Then run `netlify-deploy` and
`transcribe` through the same commands. The `--sessions-dir` option selects a
receipt directory when the default local Codex sessions directory differs.
`dispatch-next` returns `no_pending_request` while no request is queued, or
`dispatch_closed` after a retained failure. It never replaces the failed request.

```powershell
python -m tools.doe.real_comparison.cli_amendment summary --run-dir NEW_RUN
python -m tools.doe.real_comparison.cli_amendment replay --run-dir NEW_RUN
python -m pytest tests/doe/test_real_comparison_cli_adapter.py tests/doe/test_real_comparison_cli_amendment.py -q
```

Equivalent Python APIs are:

```python
prepare_calibration_run(run_dir, original_run=old_run,
                        decision_record=actual_adoption_record, executable=inspected_executable)
run_calibration_worker(run_dir, "gh-fix-ci")
dispatch_next_once(run_dir)
summarize_calibrations(run_dir)
replay_calibrations(run_dir)
```

The worker and dispatcher must run concurrently, for example in separate local
processes. `dispatch_next_once` is synchronous for one actual process, with
individual supervision waits of at most 30 seconds and a 45-minute hard timeout.
The parent supervisor can execute it in a managed terminal session and inspect
progress while the process runs. An exclusive `dispatcher.lock` prevents
concurrent launch of the same request. A supervisor crash leaves the lock and
raw request intact for explicit investigation; deleting a lock does not permit
reuse of a request that already has a dispatch record.

The adoption record must already contain `state: "adopted"` and
`user_authorized: true`, grounded in the actual conversation. Preparation copies
and binds its exact bytes. It does not create a human statement or source
reference confirmation.

## Actual launch and evidence

Every semantic request uses exactly this argv shape, with a unique output path,
an empty per-request working directory, and the complete UTF-8 request on stdin:

```text
INSPECTED_CODEX_EXE exec --ignore-user-config --ignore-rules --skip-git-repo-check --sandbox read-only --color never --json --model gpt-6.1-sol -c model_reasoning_effort="ultra" -c model_provider="openai" -c project_doc_max_bytes=0 --output-last-message UNIQUE_LAST_MESSAGE_PATH -
```

The executable SHA-256 is
`f6dbf48cb70f62649c645f26c87dc9bf84cc36986202dfad8e12fb5b8ca70312`;
the receipt must identify CLI `0.163.0-alpha.10.2`, source `exec`, originator
`codex_exec`, the expected model/provider/literal effort, exactly one fresh turn
and no inherited parent/fork history. This is recorded as an actual CLI process,
never as `spawn_agent`, `fork_turns`, or a collaboration child.

Inspection scans the entire actual session, including the common base
instructions, pinned runtime developer envelopes and environment context before
`turn_context`. Exactly one ordinary environment envelope and the exact complete
stdin task are allowed. Their visible hashes, byte counts and order are retained.
The environment's cwd/root must match the launch, and its date must be a launch
date within the 45-minute window. Unexpected input or changed runtime envelopes
stop the run.

Actual response items and attributed completion events must agree on final text,
item identity, thread and turn. Complete final text must also equal both stdout
and the last-message file. Tools, retrieval, delegation, extra turns and unknown
activity items are rejected. The isolated protocol forbids tools, but it is not
a hard tool sandbox or a proof of absent unseen activity.

Each request retains exact argv, executable/version/hash, complete stdin
hash/length, PID, unique session and turn, final item and response IDs, response
duration, every supervisor wait and elapsed duration. Raw CLI stdout/stderr are
retained. Only visible final text and allowlisted metadata are exported from the
persisted rollout; its path and hash bind the original receipt without copying
hidden reasoning into experiment artifacts.

Per-response usage requires all six nonnegative integer counters with exact
session/thread/turn/root attribution. Identical rows for the same response ID
are deduplicated; conflicting counters, reused identities or unknown counters
close further dispatch. Cumulative stdout usage is not per-response accounting.
No monetary charge is inferred.

Each native workflow is capped at 64 actual CLI request attempts, 8,000,000
reported tokens, six hours elapsed, 45 minutes outstanding per request and
300,000 delivered `o200k_base` reference tokens. Reference tokens are a size
measurement, not runtime usage. No prompt/source clipping, quality resampling,
adapter retry, replacement or final uncounted polishing call is performed. CLI
internal provider transport behavior is not independently controlled by this
adapter; all observed response identities/counters are retained and unknown
accounting stops the run.

The engineering summary reports local/native completion and transport integrity.
It requires all three workflows to reach their native finished stage, complete
actual accounting, and matching native/receipt replay before an engineering pass.
It never treats a report, completed propagation, a review pass, or a partial
native result as proof of semantic completeness, task preservation, absence of
DOE, or comparative accuracy. A transport failure remains distinct from a
native semantic failure. Earlier historical attempts remain separately disclosed.
