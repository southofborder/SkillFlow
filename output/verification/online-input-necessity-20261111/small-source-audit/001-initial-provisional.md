# 001 initial provisional source comparison

Observed: 2026-11-11T12:06:29.519422+00:00

Read-only comparison with seven prewritten 001 expectations. The total three-case inventory contains 26 expectations; this snapshot audits only 001. Not a gold benchmark or controller/replay execution.

Task, flow and the first CFG are present. The generated CFG contains 7 blocks, 17 IR instructions and 10 edges. All three source boundary sites (events.json read, notify.send, count.txt write) are represented; none has a measured propagation reach count in this snapshot.

| Expectation | Snapshot assessment |
| --- | --- |
| 001-selection | CFG checks opted_out before urgency, evaluates value >= 100 only after urgent is not true, and never waives opted_out. Task additionally records necessary-versus-sufficient selection ambiguity from 'only when'; flow/CFG implement the ordinary filter reading. This source-backed judgment is additional to the prewritten inventory and awaits review; it is not silently counted as agreement or as a generic black-box gap. |
| 001-per-record-action | One notify.send site lies in the selected-member branch and returns to the loop header. Both arguments derive from the same current_record. No deduplication or record_id identity use is authored. Per-occurrence/member execution coverage is not yet evaluated. |
| 001-notify-recipient | The recipient argument is the selected current_record.recipient projection, not the entire record. No reviewed interface-input contract or reverse demand exists yet in this snapshot. |
| 001-notify-body | The body argument is the original current_record.summary projection from the same record. Task explicitly forbids generation, rewriting and conversion. Retention of the complete summary must still be checked in final demand results. |
| 001-token-ban | Task/CFG state the any-recipient ban. The acquisition still includes access_token in the stated record schema, while no token argument is authored at notify.send. This is not an executed flow or proof that every later generated observation is safe. |
| 001-count-output | The count write follows traversal exit. Task/flow/CFG retain the actual ambiguity between all evaluated records and selected notification records. CFG authors a count operation over event_records with an unspecified counting rule; no necessary fields or count correctness are established yet. |
| 001-acquired-result | The source acquisition and five useful field projections are present. record_id and access_token have no authored positive field use in this first CFG. Their post-acquisition removability, retained structural demands, constraints and acquisition projection capability remain unevaluated. |

The count-population ambiguity matches the prewritten source inventory. Task also raises a narrower literal-reading issue about whether 'only when' requires every eligible record to be selected. The initial inventory used the ordinary procedural filter reading; final review must resolve or explicitly retain this judgment. It is not counted as an established model error here.

No deletion examples are established yet. In particular, the lack of an authored record_id/access_token positive use does not by itself certify removal until actual contracts, demands, constraints and observations are reviewed. Source acquisition remains an observed action; a later field-use recommendation must not be described as established server/read-side projection support.

This snapshot is preserved separately from later selected-artifact audits. Artifact hashes and exact Task/CFG references are in the adjacent JSON. No production, prompt, source or run artifact was edited.
