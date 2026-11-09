# Sequential CLI-v3 calibration controller

The separate `calibration_supervisor.py` adopts the existing `gh-fix-ci` worker
and dispatcher and services subsequent pending requests through the unchanged
`cli_amendment_v3.dispatch_next_once`. It never restarts the first worker or an
existing semantic request. It waits while `dispatcher.lock` exists or an actual
request lacks a terminal response. A race with the root dispatcher yields to the
exclusive core lock without replacing or charging another request.

After the first full native workflow finishes, the controller starts exactly one
separate local worker process for `netlify-deploy`, followed by exactly one for
`transcribe`. It uses the already adopted v3 three-case plan, model configuration,
budgets and stop rules. It never changes the frozen v3 implementation or its
protocol. Importing the module starts nothing.

Preparation only writes a separately bound controller plan and starts no process.
Run these commands from the project root after checking the controller and its
offline tests:

```powershell
python -m tools.doe.real_comparison.calibration_supervisor prepare --run-dir experiments/doe/runs/real-same-model-v3-cli-20261020-1358Z --existing-worker-session 69874 --existing-dispatcher-session 61464
python -m tools.doe.real_comparison.calibration_supervisor verify --run-dir experiments/doe/runs/real-same-model-v3-cli-20261020-1358Z
python -m tools.doe.real_comparison.calibration_supervisor run --run-dir experiments/doe/runs/real-same-model-v3-cli-20261020-1358Z
```

The first two commands make zero model calls and start no worker. The `run`
command is the active supervisor; run it in a managed exec session and retain
that session identity. The adopted first worker may already be at any request
sequence when the controller starts. The recorded root exec sessions identify
the existing processes; they are not used to relaunch them.

The controller plan binds its own implementation SHA-256, the core protocol
freeze, calibration plan, amendment, local Python interpreter and exact future
worker commands. It lives under `controller/`, outside the core protocol seal.
An existing controller plan, lock, future workflow or local worker launch record
prevents automatic reuse. Repeating `run` after a terminal controller result
returns that saved result without dispatching or repeating finalization.

Controller evidence includes:

- `controller/plan.json` and `plan-freeze.json`.
- Minimal structured `events.jsonl`, containing identities and statuses rather
  than prompts, answers, raw receipts or hidden reasoning.
- New local worker launch/PID/exit records and exact stdout/stderr under
  `controller/workers/CASE/`.
- A separate `controller/controller-stop.json` when the controller stops. This
  never overwrites or invents the core `dispatch-stop.json`.
- Exactly one final call to the core zero-model replay, followed by exactly one
  summary, retained as `final-replay.json` and `final-summary.json`.

Existing worker/dispatcher streams remain in the root-owned exec sessions. A
controller cannot retroactively redirect an already running process's stdout
or stderr. It records that boundary explicitly. The first adopted worker and
dispatcher remain externally owned; the core dispatcher owns its actual CLI
timeout and termination. The controller never seizes or restarts those
processes. Its own later worker processes are closed after completion or stopped
after a controller failure, preserving their logs.

Any core global failure, rejected/unaccountable response, retained request stop,
45-minute outstanding limit, six-hour workflow limit or native workflow failure
prevents further dispatch and later cases. A diagnostic native result is allowed
only when the native analysis reached `finished`; it remains diagnostic rather
than semantic success. Offline replay/summary failure cannot become an
engineering pass. No retry, replacement, formal dispatch or semantic polishing
is introduced.

If failure occurs while an externally owned worker is still committing its
failure artifacts, the one final offline replay may report incomplete or failed
evidence. That result is retained; the controller does not rerun finalization or
replace it with a later success. Root inspection can assess the preserved state.

```powershell
python -m pytest tests/doe/test_calibration_supervisor.py -q
```

All controller tests use fictional process objects and mocked core dispatch,
replay and summary functions. They issue zero model requests.
