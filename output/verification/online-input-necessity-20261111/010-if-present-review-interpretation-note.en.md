# Case 010: review interpretation of optional input presence

Status: read-only evidence and post-batch guidance design. Do not change the running batch or reinterpret its saved result. Case 010 remains partial under the frozen measured implementation.

## Observed objection

The initial source review rejected both tool contracts even while accepting that the exact query and optional `from_date`/`limit` values were correctly identified. It claimed that the missing cases were unspecified and that omission of the optional members was not preserved. The revised source review repeated that rejection, asking for separate presence requirements to preserve inclusion or omission.

Original evidence in `document-guided-010-input-necessity-high-20261111-173347`:

- `review/result.json`, SHA-256 `d65228ae2ef218bbbca7d69cadfcf6ba89863281aaf7e2561fc005b12866ae0b`, rejected contract IDs `input_contract_0de857b785cf99855ac4` and `input_contract_9a449c8076f1af44813d`.
- `revision/review/result.json`, SHA-256 `95a4e536b68c3cddbce5baa2cb80836789b6ecd62904cafb543aca4c121dae74`, rejected IDs `input_contract_9d0b261e769256e66966` and `input_contract_ebd81d03aaba2aef08fe`.

The final delivery check says the values are correctly conditional, but alleges omitted presence requirements. The paired receive check makes the same objection. Their cited source spans concern optional inclusion/omission; the objections do not identify a different unsupported interface field or a mandatory field incorrectly made optional.

## Actual frozen semantics

`src/skillflow/doe/demand_engine.py:248` handles every applicable accepted `if_present` requirement by first emitting `presence` at the same path, using rule `reviewed_optional_input_presence`. Only then does it inspect known absence/emptiness and skip the requested value/information when every recorded candidate is absent/empty. Otherwise the requested information follows at line 267. Presence preservation therefore includes known absence; the flag does not mean "ignore whether this field existed."

The processing prompt already describes this meaning at `src/skillflow/document_guided/annotation_wire.py:50` and `:51`: preserve presence and the requested value/information when present, while known absence is valid when supported by the physical source/interface.

The review prompt at `src/skillflow/document_guided/source_review.py:477` asks the reviewer to validate source-supported optionality, then says the contract must preserve presence knowledge. It does not explicitly tell the reviewer that the `if_present` flag already implements that presence requirement. This leaves an avoidable opportunity to judge the raw authored row as though it were the effective transfer.

The specific demand for redundant separate presence rows is consequently a **review semantic misinterpretation**, not a newly established omission in the implemented optional-input rule. The saved review is not edited or converted to acceptance. Other source-review and DOE limitations remain independent; correcting this guidance does not demonstrate complete DOE for case 010.

## Minimal correction after closure

For every authored required-information scope with `if_present=true`, publish a small program-derived effective-semantics descriptor alongside the compact scope ID/coordinates:

```text
authored: {property: P, path: X, if_present: true}
effective:
  - preserve presence(X) unconditionally
  - preserve P(X) when X is present
  - known absence does not require an invented value for X
```

This descriptor is derived from the fixed implementation rule; it is not a new model-authored condition, input field, propagation fact or Task seed. Keep the raw contract once in the compact annotation. The descriptor only exposes semantics already used by the backend and can reference its authored scope rather than duplicate the full contract.

State explicitly in review guidance that no separate duplicate presence row is needed for `if_present`. Review must still independently check that the original source/interface permits omission, that the selector and requested property are correct, and that mandatory inputs are not mislabeled optional. The descriptor proves neither the source interpretation nor the adequacy of the overall Task mapping.

Add focused offline regressions for descriptor derivation and prompt/interface consistency: known absent optional field retains presence without a value demand; present optional field retains both; a mandatory absent field remains a missing-input diagnostic; source-unsupported optionality remains a rejected claim. Preserve the established action-versus-payload separation and the new scoped-review receipt binding. Use injected synthetic review replies; do not replay the original case or launch a model to test the wording during the freeze.

This change uses the same source-review round, existing repair budgets and coordinated new protocol identities. Implement only after all four original controllers and sole replays close and their original cost/provenance audits are saved.
