# Source-only reference workspaces

`reference_epoch.py` is an offline workspace tool for completing and personally
checking the existing source-reference ledgers. It introduces no model client,
target dispatch command, transport protocol, execution gate, calibration route,
new scoring algorithm or automatic human approval. Tool availability does not
authorize creating a real workspace, importing actual human records, resuming
the paused CLI-v3 calibration, or starting a comparison. Those remain separate
user decisions. Do not remove the paused calibration's locks.

The implementation is prospective. Its tests create synthetic temporary
workspaces and synthetic declarations. They establish engineering behavior;
they are not real people, completed semantic references, experimental outcomes
or permission to run an experiment.

## Existing contracts and material preservation

The parent long preparation is read and verified, then copied into a new sibling
directory. It is never updated in place. The exact ordered cohort remains 24
selected cases and six reserves, `real-001` through `real-030`. The native source,
source-tree and numbered-bundle identities must match their fixed case manifests.
The source packets, selection records, roster template and existing common
rubric/grading rules are copied byte for byte. No source, prompt, threshold,
random seed, replacement selection or production algorithm is changed.

Every initial partial ledger is preserved as
`reference-history/<case_id>/v0000.json`. A complete revision is explicitly
imported from a separate file with a source-grounded reason and a new hash.
Each accepted revision is preserved byte for byte as a new numbered history
member before updating the active `references/<case_id>.json` pointer. An
unversioned edit to an active ledger or any preserved history member causes
verification to fail.

Revision imports use `assessment.validate_reference_evidence`, including the
existing grading-contract and semantic-grading reference validators. They check
the exact case/canonical/source/bundle identities, declared-purpose basis,
complete-for-verification state, required reference lists, normalized exposure
identities and exact physical source quotations. Every item in every existing
`assessment.REFERENCE_FIELDS` group needs a unique nonempty ID within that group.
The importer retains `human_verified: false` and pending embedded human slots;
personal approval exists only in separate imported submissions.

These checks do not decide whether a quotation supports its interpretation or
whether a semantically complete reference has actually been written. Empty
optional lists are not automatically evidence that there is no sensitive use,
uncertainty, preservation issue or excess.

## Current source-selection readiness

A historical hash seal establishes preserved historical bytes. It does not
establish that those source proofs pass the maintained selector after its
connector-evidence checks change. New workspaces therefore start with
`source_selection_readiness: pending_current_selector_validation` even when the
historical preparation's own byte checks pass.

The explicit `validate-selection` action calls the shared
`selection_readiness.inspect_current_selection(proposal_dir, corpus_root,
expected_selection)` helper. This recomputes the existing
`long_selection.select_long_cases(..., write=False)` without writing outputs.
It requires a complete unchanged ordered 24+6 selection, identical canonical,
version, native-source, source-tree and bundle identities, and the frozen rules
and candidate-queue hashes. No relaxed threshold or reshuffled order is accepted.
The stored binding includes maintained selector/dependency code hashes, the
rules and evidence inputs, all review/history/supersession inputs, all queued
candidate source/view bytes, the Python runtime and the tokenizer package
version. Full dependency/runtime/code snapshots are taken before and after the
selector call; a concurrent change rejects the binding.

`verify_saved_binding` rechecks this entire closure without repeating proof
analysis and tokenization. Changes or omissions require fresh validation. A
failed current selector is an unresolved source-readiness issue; this tool does
not repair historical reviews, move selection pointers, change the fixed cohort
or infer permission to obtain new inputs. Human-reference sealing remains
closed until the exact cohort has current valid source evidence.

## Actual human registration and personal submissions

Roster registration copies an explicitly supplied file into `human-roster.json`
and preserves the source/copy hashes in `roster-import.json`. The existing roster
schema uses distinct `reviewer_id` values, `human: true`, a role and a
timezone-qualified `declared_at` timestamp. The two actual reference verifiers
map to `H1` and `H2`. Optional independent timed reviewers must use all of
`R1`, `R2`, `R3`. These names are prospective slots; software does not establish
the existence, independence or personhood of the people declaring those roles.

Each actual reference verifier must explicitly submit one personal record for
each exact active reference. The wrapper requires all existing assessment
attestation fields (`case_id`, `reviewer_id`, `source_sha256`,
`reference_sha256`, `attestation_id`, timezone-qualified `attested_at`, role,
human/approval flags and the exact existing personal confirmation). It additionally
requires `source_only_attestation: true`, the exact
`reference_epoch.SOURCE_ONLY_CONFIRMATION` text, and `per_item_checks` covering
every `(group, id)` in every `REFERENCE_FIELDS` group exactly once with
`checked: true`. The source-only declaration covers the complete frozen source
and declared-purpose rules, without target outputs or registry safety summaries.
The software records that declaration and checks its structure and identities;
it cannot observe how a human actually conducted the review.

Original submitted bytes are retained in `human-submission-history/` before the
existing `assessment.import_human_attestation` importer runs. Every import
manifest version is preserved in `import-manifest-history/`, with ordered events
in `human-import-history.json` and original-to-imported payload provenance in
`human-import-provenance.json`. Reusing an old attestation ID or replacing a
person's current active confirmation is rejected. All originally submitted and
imported records remain available for audit.

If H1 confirms a draft and H2 then finds a source error, import the corrected
complete draft with an explicit reason and
`--invalidate-case-confirmations`. This preserves the previous reference,
original submissions, full prior import manifest and provenance. It removes
only that case's active confirmations, retaining other cases' active approvals.
Both H1 and H2 must submit new IDs confirming the new exact reference hash.
Old confirmations never transfer to the new version. Revision without explicit
invalidation is rejected when that case already has active confirmations.

## Reference-only sealing

`freeze-references` first requires current selection readiness and exactly 60
valid active submissions: two distinct registered actual-human slots for each
of all 30 current reference hashes, including the reserves. The wrapper then
uses the unchanged `assessment.finalize_human_references` and
`assessment.verify_human_reference_freeze` contracts. It creates the existing
reference index/freeze, an `approved-source-set.json` identity table and a
`reference-epoch-freeze.json` covering all workspace files.

Sealing records the supplied personal evidence. It does not prove semantic
completeness, reference correctness, source closure, personhood or absence of
DOE. The sealed workspace still has `execution_enabled: false` and cannot
contain protocol/gate records, calibration plans, target mailboxes or workflow
outputs. A later reference error requires a separate explicit corrigendum;
this tool rejects reference edits, invalidation and further human imports after
the full reference freeze.

Finalization writes several immutable artifacts. A process interruption can
leave an intermediate reference index or freeze without the complete epoch
seal. This remains closed to imports, revisions and automatic retry. Preserve
every file and require a separate explicit offline recovery decision; do not
delete intermediate freeze records or human evidence to reopen the workspace.
The tool does not claim an atomic multi-file transaction or automatic crash
recovery.

## Offline command interface

The module accepts `prepare`, `verify`, `validate-selection`,
`import-reference`, `import-roster`, `import-human` and `freeze-references`.
Each command requires `--epoch-dir`. Preparation additionally requires
`--preparation-run` and `--corpus-root`; selection validation requires
`--selection-proposal-dir`; revision import requires `--submission` and
`--reason`. Human imports require an explicit `--submission` file and the
`--actual-human-submission` flag. The flag does not itself verify personhood or
authorize an agent to manufacture human declarations.

`verify_reference_epoch` reports byte/history integrity, case count, the count
of structurally complete exact-quote drafts, active imported confirmations,
actual-roster import state, source-selection readiness and sealing state. Its
`model_calls` count is zero and `execution_enabled` remains false. Draft schema
and quotation coverage is an engineering count, not semantic completeness.
