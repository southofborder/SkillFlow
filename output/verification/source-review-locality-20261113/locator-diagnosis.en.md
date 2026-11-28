# Missing-field locator diagnosis and strict schema fix

The historical review failed for a real protocol violation, but the model was not shown the full rule. This is not an input truncation or transport problem. The three source-input records were received intact in both attempts. The new patch preserves strict validation and makes its alternatives visible to the model.

## Why the bounded correction failed

The frozen `SourceInputFindingCandidate` had one `kind` enum and an independent `actual` union. Its after-validator required `missing_argument` to use `absent_argument`, while `missing_field` and `wrong_field` had to use `input_range`. A second after-validator branch required a nonempty path for `missing_field`. Neither dependency appeared in the delivered JSON Schema; the rendered `ActualInputRange.path` also lacked `minItems=1`.

Attempt a001 used `missing_field` plus `absent_argument` for all three records. That is invalid because a whole argument was supplied. The first guard raised before the second guard was evaluated, so the sole correction received only the first rule. The correction kept the complete source/base prompt but could replace only those three existing records. It changed each actual locator to `input_range`, input index 0, path `[]`; the second hidden invariant then rejected all three. An empty path denotes the entire operand, not a missing child field.

The original schema lines, both diagnostic arrays, exact prompt hashes and raw proposals are preserved in `locator-diagnosis.json`.

## Actual coordinates and semantic boundaries

At `annotation:/ir_semantics/ir_119/segments/0/ops/0`, the native call has one actual operand: CFG input 1, `report_request_actual`. Its **operation-relative input index is 0**, so a002 did not choose the wrong slot. CFG input 0 is the client, whose relationship was separately reported missing in processing.

| Candidate | Source-established relation | Valid concrete locator at the SDK call |
|---|---|---|
| filters | An option documented as dimension filters is destructured and unused by request/result construction. | No concrete SDK field path is established in the frozen source. Do not invent `["filters"]`. |
| orderBy | An option documented as sort order is destructured and unused by request/result construction. | No concrete SDK field path is established. Do not infer the SDK spelling from the option name. |
| limit | The request explicitly constructs `limit` only through a truthiness spread. A supplied zero takes the omission path. | `{"kind":"input_range","input_index":0,"path":["limit"]}` fixes the locator only. |

Evidence is `reports.ts:20-27`, `reports.ts:77-108`, and `api-reference.md:31-45` within the frozen `skill/` source. The source establishes the conditional request omission for zero; it does not establish the SDK's treatment of zero or a consequent output defect. No correct value or missing input is synthesized.

The first two candidates have a concrete expressivity limit under the current missing-field protocol: expected `source_role` can describe a logical purpose but does not supply a native request-field encoding. This patch does not add a broad accepted omission kind. Guidance directs an actual representation concern to an evidenced ordinary finding, or the unestablished relationship to a scoped typed barrier. Faithful transcription of a Skill defect must not be mislabeled as a representation error.

The native call returns `tuple`; the following `select_part` chooses element 0 as `r`. Therefore the candidates' native output impact `["rows"]` refers to the wrong output level. Source-supported first-reply rows use `[0,"rows"]`. Generic shape validation was not added because every native output shape is not programmatically established; the guidance makes the coordinate convention explicit.

## Why fixing these paths alone would not accept the old response

The whole-response schema parse happens before independent contract-table validation. After the single correction failed, the source-review result contained `review=null`; the receipt builder intentionally emitted zero accepted checks, and the runner did not enter semantic repair. That explains why a local record failure made all 271 physical obligations unavailable.

There are further consistency issues in the same raw response. Ordinary finding index 3 targets `cfg:/blocks`, describing missing direct-import entry routes. The old prefix rule overlaps it with **all 269 contract records containing any accepted scope**: 227 aggregate accepted records plus 42 mixed records. This is a static comparison with the frozen rule, not a replay or newly accepted result. Any local-acceptance mechanism must distinguish global structural coverage concerns from an assertion that every local transfer is incorrect, while retaining explicit unsupported scope.

Ordinary finding index 8 targets the exact ir_119 call because its receiver/client relationship is omitted. The old source-input consistency rule also rejects a source-defect claim at an operation simultaneously declared unfaithfully represented. Consequently even the concrete `["limit"]` locator cannot make the old complete candidate valid. Raw accepted labels must never be promoted merely because the first locator errors were removed.

## Implemented changes and offline checks

Only `src/skillflow/doe/source_input_findings.py` and `tests/doe/test_source_input_findings.py` were changed by this agent.

- Discriminated variants expose the exact kind/actual combinations. `MissingFieldInputRange.path` has schema-visible `minItems=1`; wrong-field whole operands remain expressible, and absent arguments remain distinct.
- Immutable Candidate and Normalized records preserve `model_validate`, `model_dump`, ordinary field reads, and the existing flat serialized wire format. Current callers need no migration.
- Exported English `SOURCE_INPUT_FINDING_GUIDANCE` explains native operands/output paths, the source-role encoding limit, faithful representation, and the prohibition against invented SDK paths.
- Existing source-input tests plus the new schema/locator regressions passed **23/23**. The subsequent focused source-input and existing contract-receipt integration passed **35/35**, with XML receipts retained. These are scoped offline checks, not whole-repository acceptance.

The new tests cover both rejected locator forms, visible schema coupling and nonempty paths, valid whole-operand wrong-field records, immutable/flat normalized records, native operand indexing, source-role limits, and existing evidence/identity/demand behavior.

Root owns review isolation, aggregation and repair integration. Recommended checks there include collecting independent errors for the same correction budget; retaining raw invalid records with exact local barriers; independently verifying contract identity, coverage, source references and conflicts; rejecting stale identities after repair; and preventing unsafe automatic acceptance of overlapping claims. Seven normal requests, two workers and existing budgets remain unchanged. Historical files were read only; no historical validator, backend, replay, model or Skill was executed.
