# Independent CFG correction review

Read-only production review covered compiler causal annotations,
`CFGIssue` endpoint context, `cfg_correction.py`, strategy prompt/merge handling,
the online raw-candidate binding and the new integration tests. No actionable
acceptance, causal ownership, identity or topology-permission defect was found.

The compiler supplements an actual constructor failure only when its complete
structural issue list consists of endpoints belonging to blocks actually rejected
earlier. The exact constructor error is compared with that issue list. The
diagnostic-only projected CFG is not returned or used for acceptance. A missing
entry, unrelated global defect or genuinely absent authored endpoint prevents
this explanation from authorizing dependency-scoped repair.

The online adapter binds the normalized/compiler diagnostics back to the original
wire candidate. The correction selector binds that candidate and the complete
diagnostic list, checks owner positions/messages/references and re-derives every
explained endpoint. The merger recomputes the selection and compares the complete
scope before editing. Dependency mode permits only existing selected blocks and
preserves their block identities; edges, entry and all unlisted records remain
unchanged. New instructions inside permitted blocks are still subjected to the
ordinary complete graph validator after merge.

Dependency scope deliberately grants editing permission to the affected control
components and direct producer/predecessor records. More distant upstream
producers and outside consumers remain explicit read-only boundaries, with the
entire candidate available for reference. This is not a claim that every upstream
record must be editable, or that structural validation proves source correctness.

Four independent synthetic peer regressions were added in
`tests/document_guided/test_cfg_correction_peer.py`:

- A transitive producer remains an explicit data/control boundary; its record
  cannot be edited, while a valid local repair still passes full validation.
- A locally repaired selected component that changes an outside consumer's
  producer identity fails the ordinary whole-graph check at that consumer.
- Source-span copying changes compiler material but preserves exact original-wire
  ownership; changing the original source span invalidates the saved repair scope.
- A rejected entry or an unrelated global structural error requires complete
  replacement instead of gaining local topology permission.

`peer-cfg-and-wire-final.xml` passed 40/40: these four cases plus all 36 raw-wire
diagnostic tests. The tests use new injected synthetic material only, with no
model, Skill or historical validation/replay. No CFG production file was edited
by this reviewer.

Separately, the root-authorized final wording correction in the owned
`fragment_wire.py` makes local output guidance match the existing accepted merge:
only the selected allowed records actually being replaced must appear;
unlisted records remain unchanged, each replacement value is complete and final
merged coverage is checked. Wire acceptance and identity are unchanged.
Owned production edits are now stable for broad acceptance.
