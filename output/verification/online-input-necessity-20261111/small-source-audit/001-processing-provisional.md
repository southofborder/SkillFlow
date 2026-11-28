# 001 processing provisional source comparison

Observed: 2026-11-11T12:10:05.357081+00:00

The initial processing fragment accounts for 17 IR rows and 17 explicit operations. It contains one opaque compute contract and one tool-interface input contract. Both account for all their actual input slots. No mandatory contract omission was observed in this finite fragment. Three structured comparisons and five field projections correctly rely on deterministic transfer rules; the file read and write are storage operations.

The `notify.send` contract at `/ir_semantics/ir_013/segments/0/ops/0/input_contract` requires the whole recipient and whole original summary values. Its evidence is source lines 11–12, which independently specify the two parameters. The same-record projections are explicit and no extra record field is introduced into these two arguments. An independent remainder alongside a whole-value requirement does not make internal recipient or summary fields deletable.

The count contract at `/ir_semantics/ir_015/segments/0/ops/0/demand_transfer` names a genuine source gap: which occurrences count as processed. Its gap is backed by line 16 and does not rely merely on black-box execution. Its scope is nevertheless broad: all of the input collection remainder is unresolved and no irrelevant field range is declared. The source-only inventory identified record_id, access_token and summary content as unnecessary to either all-evaluated or selected-record cardinality. This is a field-precision concern for final review, not a claim that a downstream demand result already failed.

The normal notification/control relationships remain explicit. A separate processing gap concerns unspecified send-failure continuation. It is distinct from a wrong or missing source argument and must be evaluated at its actual affected control scope. Complete acquisition and possible model observations remain facts; no audit observation erases access_token from the acquired value.

No contract has been verified by source review in this snapshot. Propagation reach, demand ranges, preservation checks and DOE deletion examples remain unavailable. No capability to project fields at the events.json read interface is established. Only a later completed result can support concrete removal recommendations.

Exact operation/contract inventories, source spans and hashes are in the adjacent JSON. The running pipeline receives no audit feedback. Production and run artifacts are unchanged.
