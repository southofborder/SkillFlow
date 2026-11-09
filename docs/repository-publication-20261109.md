# Current repository publication — 2026-11-09

This publication captures the current `D:/projects/SkillFlow` implementation,
tests, examples, tools, documentation and recorded verification evidence. It
does not merge the separate `SkillFlow-staged` worktree, change analysis
behavior, or authorize a new model call, Skill execution, experiment or replay.
The current analysis entry and its actual limits are in [current-version.md](current-version.md).

The implementation is the November 4 interface-r4 version. Its four real cases
completed generated-IR propagation and their sole zero-model-call replays, but
all DOE results remain partial. The scoped 591-case offline acceptance is an
existing receipt union, not a new whole-repository test execution. Repository
publication checks source syntax, selected file scope, hashes and whitespace;
it does not regenerate evidence or rerun analysis.

## What is included

- Current source, tests, authored fixtures, examples, maintained tools and docs.
- Existing `output/verification/` records, including initial failures, corrective
  receipts, source audits, acceptance summaries and previously archived snapshots.
- Small root-level experiment reports, manifests, cost/timing summaries and
  completion/replay receipts selected from the existing run directories.
- A compressed SHA-256 inventory of the previously untracked historical
  experiment/verification files, recording which files this update publishes.

See [publication inventory](verification/git-publication-20261109.json) and
[per-file history inventory](verification/git-publication-20261109-history.jsonl.gz).
The inventory contains paths, sizes and hashes, not replacement content.

## What remains at its original local location

The untracked research history is approximately 8.26 GB and 111,000 files before
this publication. It includes large raw model transcripts, generated graph and
DOE material, diagnostic scratch and sixteen renderer executable snapshots
larger than 100 MiB each. Those full run closures are not all uploaded in this
code publication. They are neither deleted nor rewritten, and existing tracked
history stays tracked. The inventory makes the remote/local boundary explicit.

A selected report or receipt directory is **not a complete replayable run**.
Its links to unuploaded source closures, transcripts or large records may only
resolve in the original workspace. Recovering an experiment on another computer
requires transferring its complete frozen dependency closure with original
bytes; do not reconstruct it by mixing versions or rerunning old calls.

The unrelated bill templates, figures and paper draft remain local and unstaged.
No `.env`, credential configuration, build cache or external worktree is added.
The existing `* -text` attribute remains in force so Git does not normalize
frozen source or evidence bytes. No cleanup, history rewrite or force-push is
part of this publication.
