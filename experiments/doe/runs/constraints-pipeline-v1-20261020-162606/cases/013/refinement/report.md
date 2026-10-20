# One-repair joint annotation refinement

Status: `repair_limit`; stage: `final_review`

Issues remain after the single semantic repair round.

At most one semantic repair; mechanical response correction has no attempt limit. No reported review issue is not proof of semantic correctness.

Last structurally valid candidate: repair

- Initial review: `complete`; [Stage report](initial-review/report.md)

  The raw annotation labels only the selected fast_key local. ir_003 reads the environment into environment_snapshot and obs_0002 places that whole snapshot in the model context, so the unlabelled snapshot still carries a possible FAST_KEY member. The source treats FAST_KEY as a credential and explicitly restricts its disclosure; omitting a credential sensitivity entry on the observed snapshot loses that supported sensitive content.

  The retry gates are declared through fast_fetch_first_transient, but its compute expression is a plain ref to fast_fetch_first_outcome. That aliases the whole outcome classification and does not test the source's transient-error condition; the truth demand and the R5/R6 only_if constraints are therefore unsupported.

- Complete repair: `complete`; [Stage report](repair/report.md)

- Independent re-review: `complete`; [Stage report](final-review/report.md)

  All four status-append write operations reference IR input index 1, but each enclosing instruction has a single input at index 0. The corresponding input demands resolve to the same nonexistent input index 1, so the required final-status payload is not linked to the actual outcome value on any return path. This leaves R16 only partially represented despite the otherwise correct append action and ordering.
