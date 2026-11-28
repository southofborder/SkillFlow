# Payload-only tool-contract reproduction

Date: 2026-11-11. This follow-up resolves the static caveat in `mandatory-contract-coverage-audit.en.md`. The parent explicitly authorized fresh isolated offline synthetic propagation and demand analysis. The reproduction changed only its new verification script and artifacts. It used no model, Skill execution, historical answers, run replay or controller action, and changed no production code or prompt.

## Result

The missing-contract diagnostic is demand-triggered, as the static audit predicted. However, the reproduction does **not** establish that direct payload demands must also create action demands. The observed behavior implements the existing distinction between preserving information at an input and preserving the invocation itself.

The synthetic payload contains `display`, `token`, and `service_note`. Its supplied interface contract requires `display` and `token` for a required invocation, and declares `service_note` independent. The payload goal preserves only `input_use[0].display`. The comparison adds an explicit `action` goal, without changing the payload or contract. Accepted reviews are deliberately injected fixture evidence, not claims of a model's semantic review accuracy.

| Case | Demand status | Diagnostics | Action derivations | `display` deletable | `token` deletable | `service_note` deletable |
| --- | --- | --- | ---: | --- | --- | --- |
| Missing contract; payload only | complete | none | 0 | no | yes | yes |
| Accepted contract; payload only | complete | none | 0 | no | yes | yes |
| Present but unreviewed contract; payload only | complete | none | 0 | no | yes | yes |
| Missing contract; action and payload | partial | `input_contract_unavailable` | 1 | no | no | no |
| Accepted contract; action and payload | complete | none | 1 | no | no | yes |

The yes entries are actual `deletable_reduction` results of `exclude_field`, supported by the generated input assessments. All five fresh symbolic propagations completed. Original data and operation records remained unchanged in every case. Full candidates, receipts, assessments, diagnostics, derivations and demand results are retained in `payload-only-tool-contract-reproduction.json`.

## Interpretation

`goal_target_capability` in `src/skillflow/propagation/contracts/demand.py:295` treats `preserve=action` and an ordinary `input_use` information demand as different capabilities. `DemandEngine.seed` at `src/skillflow/doe/demand_engine.py:489` creates an action node for the former, while line 495 selects an operand node for the latter. The corresponding transfer branches at lines 739 and 756 remain separate. A required response output also triggers the interface path at line 822.

This matches the active processing prompt at `src/skillflow/document_guided/annotation_wire.py:51`: a required invocation preserves the interface-required fields; a tool contract does not create a new Task purpose or make an otherwise unused call required. Existing synthetic boundary-seed tests explicitly preserve receiver/slot-specific demands without filling absent seeds (`tests/doe/test_sink_payload_seeds.py:1`, `:154`, `:165`).

Therefore, the accepted payload-only case is the decisive control. Even an accepted interface contract does not preserve `token` when no action or response obligation reaches the interface. Changing only the missing-contract fallback would not change that action policy. Automatically creating an action seed for every field seed would add a Task requirement that the current mapping has not declared, and would exceed the narrow contract-coverage correction.

The result is conditional on the authored Task correspondence. If real source text requires a successful send or invocation, a correspondence declaring only input-field preservation may be semantically incomplete. That is a source-review/mapping defect to repair through existing ownership and budgets. The engine should not infer the missing action merely from a tool location or from the fact that a field is currently passed. This synthetic reproduction intentionally specifies the two alternative preservation obligations; it does not establish that a payload-only mapping is adequate for any real Skill.

## Smallest post-batch correction

The already established mandatory active-route material/review correction remains necessary: derive required contract obligations independently, reject omitted attachments in current guided processing, explicitly reconcile source-review coverage, and bind/recheck that expected coverage in the receipt. The missing payload-only case currently even admits a mechanically complete, empty-contract receipt; that is another demonstration of inventory incompleteness, not a justification for inventing an interface demand.

No additional demand-transfer or local-assessment production change is justified solely by these five results. Preserve the following semantics in the post-batch regression matrix:

- A payload-only obligation stays payload-only; attaching an accepted contract must not manufacture an action seed or promote interface fields into Task demands.
- A required action or response with an unavailable contract remains conservatively unresolved for the affected inputs.
- A required action with an accepted contract retains exactly the interface-required information and permits independently unnecessary remainder.
- Current guided material must not use missing contracts or an empty review table to claim its mandatory input-contract coverage is complete.
- If the original source requires an invocation, source review must examine whether the selected mapping expresses that action/response requirement, and route a demonstrated omission to the existing mapping repair. Contract coverage does not by itself prove Task correspondence completeness.

For standalone/manual material, retain its explicit preservation-property semantics and the existing transfer-triggered conservative boundary. A universal local block or new action seed for every uncontracted input would change the meaning of otherwise valid unused/payload-only inputs. Such a policy needs a separate demonstrated requirement; this reproduction supplies none.

The previous audit's universal-safety caution is now precise: missing contracts do **not** always produce partial results, but the shown payload-only behavior is consistent with the chosen action separation. It is not an independently confirmed backend correctness bug. The frontend and review coverage omission remains a confirmed defect.

## Reproduction evidence

- Script: `reproduce_payload_only_tool_contract.py`.
- Successful result: `payload-only-tool-contract-reproduction.json`; five synthetic cases, successful command exit code 0.
- The JSON records hashes of the relevant frozen implementation files, the reused synthetic fixture helper, and the final script.
- Initial helper-construction failure: `payload-only-reproduction-initial-helper-error.json`. The first script accidentally used a CFG literal constructor in processing references and failed validation before propagation/demand. The verification script was corrected to use literal ValueRefs; no production change was involved.
- The output writer uses exclusive creation to preserve this result; do not rerun it over the existing artifact. Any future regression belongs to the separately authorized post-batch offline correction.

All four live controllers and their sole zero-call replays remain under the original freeze. This reproduction neither changes their measured implementation nor authorizes another real batch.
