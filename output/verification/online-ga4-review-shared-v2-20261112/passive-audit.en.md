# Passive cost and provenance audit

Run the local auditor once when a snapshot is needed:

```powershell
& 'C:/Users/admin/AppData/Local/Temp/skillflow-input-contracts-20261111-venv/Scripts/python.exe' 'output/verification/online-ga4-review-shared-v2-20261112/audit_cost_provenance.py' --write
```

The only target comes from this directory's root-owned `prepared-run.json`. The helper refuses a missing receipt or a target outside the new `document-guided-ga4-review-shared-v2-high-` namespace. It has no run-path override and never searches historical runs. Root alone owns the real controller, analysis and its sole replay.

The auditor uses the standard library and reads saved public request, process, completion and usage records. It does not import the analysis or transport, invoke subprocesses, contact a model, execute Skill code, read authentication/private session files, rerender requests, or replay analysis. Without `--write`, it prints a report. With `--write`, it exclusively creates a new timestamped JSON report beneath this directory's `cost-provenance-audit/`; it never changes a run file. Repeated invocations are new observations, not additional experiment attempts.

The report includes:

- PID-confirmed native process starts, launch errors and unconfirmed launches. A start marker alone does not establish a process start. A PID receipt without its start marker still counts and produces a warning.
- The seven named normal stages, structural correction, semantic repair and outer network retry categories. Categories are exclusive for counting; separate repair/correction axes retain overlap. Internal reconnect notices do not become additional native starts or inferred HTTP requests.
- Complete public final usage bound to accepted final-answer hashes; partial/unattributed counters and missing usage remain separate. Strong response identities deduplicate reports, and conflicting identities cannot remain complete. Input plus output gives total; cached input and reasoning output remain subsets. Provider billing, unreported internal attempts and their usage remain unknown.
- Every persisted source-review delivery, including structural corrections, repair rereviews and pre-start input rejection. Sizes use Unicode codepoints and include the actual transport envelope. The cap is read from the frozen adapter text without importing or executing it. Each delivery is bound to its saved hash.
- Returned model names only from explicit public completion/response metadata. Requested configuration does not establish the actual returned model. Missing metadata remains unknown.
- Frozen/current implementation, helper and executable hashes; source package raw/decoded hashes, staged bytes and snapshot seals; protocol and manifest identity; passive reconciliation with saved metrics and replay receipts when present.

Published output includes neither response content nor per-token text. Public session/turn/response identifiers, launch commands and unrestricted raw notices are replaced by hashes; notice categories and source line numbers remain. Source and implementation reads are only for byte hashing.

An observation during execution is always provisional. The helper declares a final observation only after a stable controller closure (or an independently evidenced operator stop). A matched replay is not presumed; its actual saved outcome is retained, with an independent check for launch markers after its recorded start.

The synthetic checks are in `test_audit_cost_provenance.py`; they exercise counter completeness, duplication/conflicts, native-start confirmation, corrections/retries, closed and cancelled receipts, target restrictions, review-delivery rejection, returned-model attribution and output redaction. They create temporary synthetic files only and perform no model or analysis work.
