# Replacement GA4 run after a user-confirmed network outage

The user explicitly requested a fresh redo on 2026-11-12 after confirming that the network had disconnected. Root stopped only the verified controller tree for `document-guided-ga4-input-necessity-corrected-high-20261112-174538` at 10:31:00 UTC. Its raw incomplete result and requests remain unchanged; separate operator-stop receipts establish cancellation. No replay was started for the interrupted run.

This replacement is `document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209`. Root dispatched it once at 10:32:29 UTC; the venv wrapper is PID 19396 and the actual controller is PID 10860, whose start receipt is 10:32:30.257553 UTC. The previous recorded controller and native-request PIDs were absent before replacement dispatch.

- Accepted corrected implementation: `796240619b140cbb2c521d1ef00fb1dcae81aa0eed7acc6b79f692c194e5f5fa`.
- Complete byte-identical GA4 source: 16 files, SHA `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.
- Same installed CLI as the interrupted attempt: SHA `83f5c2dd2ac2902e0d96ba5d8ccdd27d513f57df4a9ab73e06a5a518028e9a2f`; renderer and transport unchanged.
- `gpt-6.1-sol/high/openai`; seven normal requests, two workers, one structural correction per stage, one shared semantic repair, 2700-second native timeout and two eligible extra transient attempts.
- All Task, flow, CFG, annotations and review answers are generated afresh. No generated material from the interrupted attempt is imported.
- One controller-owned zero-call replay follows this replacement's terminal result. No small cases, model probes, extra resampling or Skill executions are authorized.
- No new metadata-only CLI invocations were made for this replacement; the three earlier local version/help invocations belong to the interrupted attempt's prelaunch record.

The interrupted predecessor cost remains separate: four confirmed model starts, 306,246 known public tokens, plus unknown usage for its incomplete graph-correction request. It ended by user cancellation after about 24 minutes 17 seconds for that request, not by the 45-minute timeout. See the predecessor verification directory's `aborted-cost-provenance.en.md`.
