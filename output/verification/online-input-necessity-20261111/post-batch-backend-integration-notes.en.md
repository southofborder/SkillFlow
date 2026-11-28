# Backend integration notes after the frozen batch

Design only. Root owns `input_contracts.py` and `demand_engine.py` after all four controllers and sole replays close and original cost/provenance audits are saved. No production changes are authorized by this note during the batch.

## Local contract decisions

Consume the receipt owner's `reviewed_contract_scopes` projection. Exact output matching and closed output decomposition remain deterministic. An accepted whole-output rule still does not cover arbitrary subfields. The presence of a reviewed contract must never create an action or output seed.

Use the selected rule/interface decision, each required-information decision, explicit unresolved-range decisions, the independent/unresolved remainder decision, and any necessary output-decomposition decision. A local rejection or uncertainty must retain only its actual information range. A whole-rule/decomposition gap needs its own concrete cross-range reason; unrelated rules and inputs remain usable.

The coordinated schema extension permits one actual object input with required `x`, a specifically evidenced uncertain relationship for `y`, and an independent remainder containing `z`. Transfer must retain the explicit `y` range conservatively and leave `z` without demand. Do not broaden that gap to the entire input merely because both fields share a slot. Preserve exclusions and member paths in both reverse transfer and forward deletion influence.

`influenced_outputs` must query the same reviewed scopes. An uncertainty about an unrelated input range is not a reason to return unknown for removal of a proven independent range. Whole-input removal still intersects each contained affected range. Directional range containment is required for exclusions; an indexed member does not cover every member.

Keep `if_present` semantics: emit unconditional presence knowledge, then the supplied information if the value is present. Known absent/empty candidates can skip the value requirement, but absence is not evidence that the interface declares optionality. The original 010 reviewer incorrectly requested redundant presence rows; that is a review interpretation problem, not a missing backend presence transfer.

## Known source input errors

The source-error owner supplies a validated normalizer/index; the receipt owner binds exact raw-operation placements. Apply known-error impacts at the common demanded `action` or `op_output` boundary, including deterministic operations such as `select_part`. Do not place the hook only inside opaque contract transfer.

Intersect the authored native action/output impact with the actual demanded selector and exclusions. Report every independently reviewed source defect in the inventory, including task-unused or not-reached sites, while creating no demand seed for it. An absent argument never gains an actual input index, Data object, or substitute demand.

Demand derivation identity currently includes the `conservative` flag (`DemandEngine.emit`). Never mutate that flag on an existing derivation. A required affected operation can emit the corresponding conservative derivation with the known-error reference as a rule and then process the actual deterministic dependencies through it. Avoid infinite self-emission: an already conservative derivation records the reference and continues. Keep the nonconservative task obligation as an obligation; do not claim that its output is fulfilled.

Reuse the localized diagnostic ancestry machinery with a distinct known-error cause. Either keep a recognized local diagnostic prefix or extend every associated result/report/validation helper consistently; treating a new diagnostic as a generic IR-wide blocker would incorrectly invalidate independent output fields. Typed `missing_input`/`wrong_input` findings remain separate from uncertain preservation ranges.

Review existing deterministic missing-field/type diagnostics as well: they must not synthesize an absent value or silently certify affected output sufficiency. Preserve their deterministic origin rather than relabeling them as independently reviewed source errors.

## Verification boundaries

Add focused offline cases for partial accepted/unresolved/rejected review scopes, within-object `x/y/z` localization, exclusions/member selectors, same-object independent influence, known source errors through exact operations, no action seeds, optional presence, zero-input defects, FIFO/LIFO, and unchanged actual observations. Coordinate public result fields and versions with the reporting owner. Run integrated identity/replay tests only after concurrent production edits settle, so unrelated hash changes do not produce misleading failures.

Original batch reports and artifacts remain evidence for SHA `09f5f9d7798f37cceaa826726ed0a62df31b658ae38b91d950ac5203506c3ab0`. Later corrected code needs separate offline acceptance and must not be described as the code measured by these real runs. Do not rerun or relabel this batch.
