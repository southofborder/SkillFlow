# Initial review and correction delivery audit

Snapshot: 2026-11-13T15:04:43.318462+00:00. This records saved initial a001 and actual correction a002 delivery while a002 is still running.

Initial a001 proposed 16 ordinary findings and all 275 contract checks: 239 labeled accepted, 35 rejected and one unresolved. These are **raw candidate labels**, not accepted review decisions. No source-input findings were proposed. Thus this attempt does not reproduce the former missing-field locator errors, but it also provides no real success example for that locator.

The saved validation marks a001 structural_invalid. There are five record errors: rows 47, 139, 165 and 182 mix wide and narrow scopes in a group with affected_scope_ids, applying a wide-only relation to each narrow scope too. Row 158 substitutes scope suffix `250b` for the actual `250f`, breaking exact inventory coverage. The former four need separate wide/narrow decisions; the latter needs its exact supplied ID.

There are also 27 cross-record conflicts: 25 checks overlap finding 8, which disputes the selected SDK receiver relation across 13 actual operation targets; two overlap finding 9, which disputes the protected post-attempt invocation/receipt relations. These are local operation targets, not an invented global rejection. All 32 raw diagnostics map to seven displayed diagnostics: five record errors and two groups retaining every one of the 27 conflict pairs and their original obligation IDs/record paths.

The actual complete-replacement correction delivery is **988,098 characters**, leaving **60,478** below the cap. Independent decoding proves exact preservation of the original logical input, all 275 obligations and 928 scopes, the complete original source section, and the entire a001 candidate. All seven displayed diagnostics and their 27 conflict relationships are delivered. The original instruction/schema prefix is preserved; correction guidance requests a full replacement and preservation of supported allegations.

No response or isolated ledger is accepted by this audit. No validator, backend, replay, model or Skill was invoked. The JSON companion binds physical receipts, exact correction context and the grouped conflict membership.
