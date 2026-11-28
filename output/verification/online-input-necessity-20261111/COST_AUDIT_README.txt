Passive cost and provenance audit for batch 20261111-173347

Entry point: audit_cost_provenance.py
Synthetic checks: test_audit_cost_provenance.py

Run from D:/Projects/SkillFlow after a controller closes:
  python -B output/verification/online-input-necessity-20261111/audit_cost_provenance.py ga4 --write
Choose any prepared case (ga4, 001, 010, 013), or omit the case list for all four.
Use the existing temporary test environment if a Python executable is needed.
The utility itself uses only the standard library.

Without --write, the complete audit goes to stdout. With --write, each invocation
creates uniquely named JSON reports inside cost-provenance-audit/. Existing reports
and every run artifact remain unchanged. Live or queued cases are provisional;
only an unchanged controller-finished receipt permits a final observation.

Accounting distinctions:
- started.json counts launch attempts. A valid pid.json confirms a native process.
  Launch errors and indeterminate starts remain separate.
- Public turn events and accepted final-message identity/order determine whether
  counters are complete, partial, or unavailable. Missing counters are not zero.
- Strong response IDs are deduplicated globally. Local turn/event IDs are scoped
  to the observed thread or native attempt. Conflicting counters stay partial.
- Total tokens equal input plus output. Cached input and reasoning output are
  subsets, never extra totals. Unreported optional counter fields remain explicit.
- unknown_usage_requests includes partial and completely unknown requests, matching
  the saved metrics convention. no_public_usage_requests identifies the latter.
- Primary categories are mutually exclusive: network retry, structural correction,
  semantic repair, normal request. Independent repair flags remain on every row,
  so a retry during a repair is not lost or counted twice in category totals.
- Durations may overlap. Native durations are not added to controller wall time.
- Provider billing and internal HTTP attempts remain unknown.
- Public internal reconnect notices have a separate per-process and aggregate
  inventory. Their message ordinals (for example 2/5) are not translated into HTTP
  attempt counts, extra native starts, or additional token usage. They are separate
  from outer launch retries; any unreported usage remains unknown.

The audit independently checks metrics arithmetic, source bytes and decoded hashes,
current and frozen implementation/transport/renderer hashes, helper identities,
logical/native prompt bindings, and the recorded sole replay's zero new launch
markers. A failed analysis or failed zero-call replay remains a recorded failure;
it is not itself a cost-audit mismatch and never authorizes another attempt.

No production or transport module is imported. The utility never starts a native
process, model request, Skill, controller, or replay, and never reads private session
records. It does not read historical answers or the source-donor package. Every
report identifies the current audit utility by SHA-256.

Preserved initial audit-helper correction:
The provisional ga4-20261111T094401098417Z.json report compared a canonical JSON
prompt digest directly with the transport's UTF-8 text digest. Those are different
documented representations of the same prompt. This helper-only check was corrected;
the original report was preserved. The subsequent 20261111T094524302957Z GA4 report
has no discrepancies. These initial observations are not final case cost reports.
Frozen run files, model inputs, and production implementation were not changed.

Nine synthetic checks cover subset arithmetic, absent final events, partial usage,
deduplication, conflicting identities, retry categories, failed/unknown/PID-confirmed
launches, closed metrics reconciliation, independent post-replay marker detection,
and internal reconnect notices without inferred attempts or unreported usage.
