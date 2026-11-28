# Replacement-run passive cost audit

`audit_cost_provenance.py` is restricted to the new replacement GA4 run `document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209`. It uses only the standard library to read public output, process receipts and pinned file hashes. It does not import analysis code, create a model client, launch processes, read private sessions, execute the Skill or perform replay.

After root confirms final closure:

```powershell
python -B output/verification/online-ga4-input-necessity-corrected-r2-20261112/audit_cost_provenance.py --write
```

Each invocation creates a uniquely named receipt under `cost-provenance-audit/`; previous receipts and run files are never overwritten. Live observations are provisional. Normal closure requires the controller receipt and sole replay evidence. Explicit cancellation, if requested, instead requires the stop receipt and an independent zero-process observation; it never fabricates a terminal result or replay.

The audit reconciles PID-confirmed starts, normal/structural/semantic/outer-retry categories, complete and partial public counters, unknown usage, duplicate/conflicting response identities, per-request timing, replay boundaries, current and archived implementation/transport/renderer hashes, native CLI identity, and the complete frozen/staged source package.

Sampling-retry lines, connection-wait backoff lines and auxiliary model-list/MCP logs remain separate. Stdout reconnect notices overlap stderr retry/wait logs and must not be added. Missing usage is unknown, not zero; cached-input and reasoning-output counters are subsets. No provider HTTP-attempt total or monetary charge is inferred.

No new metadata-only CLI invocations were made for this replacement. The three metadata-only invocations were part of the interrupted predecessor's prelaunch and remain there.

The predecessor's **four confirmed starts, 306,246 known public tokens and one unknown-usage request are excluded** from this run's counts. Its independent report remains at `../online-ga4-input-necessity-corrected-20261112/aborted-cost-provenance.en.md`, with raw audit `../online-ga4-input-necessity-corrected-20261112/cost-provenance-audit/ga4-20261112T103306940146Z.json`. The replacement does not reuse its answers or relabel its costs.

The helper is derived from the inspected predecessor audit logic and preserves all eleven synthetic arithmetic, classification, replay-boundary and cancellation checks. The local receipt is `cost-audit-tests.log`; helper checks are not a SkillFlow analysis or implementation acceptance run.
