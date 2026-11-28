# Passive cost, timing and provenance audit

`audit_cost_provenance.py` reads only the fresh GA4 run recorded in `prepared-run.json`. It does not import production analysis code, construct a model client, start subprocesses, read private session records or execute a replay. Its output is separate from the immutable run artifacts.

Run after the controller closes:

```powershell
python -B output/verification/online-ga4-input-necessity-corrected-20261112/audit_cost_provenance.py --write
```

The helper creates a uniquely named JSON receipt under `cost-provenance-audit/`, never overwriting previous observations. A live observation remains provisional. Closure requires either a stable controller-finished marker or an explicit operator-stop receipt accompanied by an independent zero-process observation matching the recorded wrapper, controller and native PIDs. Cancellation preserves the raw unfinished result and does not fabricate a normal failure, timeout, process-duration receipt or replay.

The audit independently rereads the public output and confirms:

- PID-backed native starts, launch errors, unknown starts, normal requests, structural corrections, semantic repairs and outer transport retries.
- Complete accepted-final usage, separately reported partial counters, missing usage, duplicate or conflicting public identities, and agreement with saved metrics. Total tokens are input plus output; cached input and reasoning output are subsets.
- Exact stdout reconnect notices and stderr sampling-retry lines, with network-wait notices and connection-wait backoff logs kept separate. These layers overlap and must not be added or converted into provider HTTP-attempt counts. Auxiliary available-model refresh and MCP startup, reconnect or shutdown errors have separate categories and do not establish a failed analysis request.
- Saved request durations, native activity span, analysis duration and the sole controller-owned replay. Start timestamps are checked against the replay boundary; a failed replay is preserved rather than relabeled as a match.
- Accepted corrected implementation identity, current versus archived production/transport/renderer bytes, native CLI identity, helper hashes, full frozen-source bytes and new source-staging bytes.

The previous CLI update is explicitly recorded. Three local metadata-only CLI invocations preceded the run (one root `exec --help`; the independent prelaunch auditor's `--version` and `exec --help`). These made zero model calls and are separate from analysis starts. Provider-internal HTTP attempts, unreported internal-attempt usage and currency billing remain unknown unless directly provided; the helper does not infer them.

The cost arithmetic and identity checks were adapted from the already-inspected previous audit utility, without reading historical answers. Nine initial synthetic standard-library checks pass, including missing-usage handling, subset counters, duplicated/conflicting response identities, PID confirmation, saved-metrics disagreement and replay-boundary detection. The exact initial receipt is `cost-audit-tests.log`. The newer CLI's connection-wait logs required two additional classification tests; all eleven checks pass in `cost-audit-log-classification-tests.log`. The closure test was then extended for explicit user cancellation, raw-result preservation and rejection of a nonzero remaining-process observation; all eleven checks pass in `cost-audit-aborted-run-tests.log`. These are helper validations, not another SkillFlow analysis or a new implementation acceptance run.

Final reporting should state the terminal analysis status separately from audit success; propagation/DOE coverage comes from the source/result audit, not token arithmetic. Report any audit discrepancy or unresolved counter explicitly and preserve the first observed failure receipt.
