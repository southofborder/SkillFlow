# Selected GA4 r2 generation and assembly: independent source audit

Run: `D:\Projects\SkillFlow\experiments\doe\runs\document-guided-ga4-input-necessity-corrected-r2-high-20261112-183209`

The selected graph represents all 13 enumerated remote API sites, 25 saveResult sites and three explicit URL loops. This is representation coverage only. Backend outcomes are deliberately outside this audit.

The mandatory source review failed before a native process started: 1,079,505 input characters exceeded 1,048,576. A bound failure receipt exists, but source_review_complete is false and all 344 obligations have zero accepted checks. This assistant audit does not replace that review.

Selected mapping has 45 realizations (21 expressed, 23 partial, one retained only), compiled to 191 demands. Sensitivity has 177 declarations across 135 IR. These are descriptive counts, not semantic acceptance.

## ASSEMBLY-01: Fourteen documented default or batch save sites lack a demand seed

Status: `source_supported_missing_action_seed_concern`. IR: ir_249, ir_387, ir_440, ir_404, ir_426, ir_348, ir_360, ir_370, ir_306, ir_316, ir_326, ir_336, ir_174, ir_276.

All 25 saveResult sites are represented and deliver their actual operands. Only the 11 high-level aggregate sites have any directly targeted compiled demand, all action demands. The 14 low-level/default/outer-batch save sites have no compiled demand target. Task analysis_persistence requires default saving, and mapping prose acknowledges these writes; binding the independent public saver ir_077 does not itself seed each helper invocation. A required response does not by itself preserve a separate save action.

The mapping needs an action obligation at each applicable save boundary, with its existing control path and opt-outs. This is an unreviewed missing-seed concern, not a deletion recommendation or a claim that this run deleted anything.

Source: skill/SKILL.md:55-64; skill/scripts/src/api/reports.ts:102-108; skill/scripts/src/api/metadata.ts:46-54; skill/scripts/src/api/indexing.ts:89-104.

## ASSEMBLY-02: Metadata wrappers lack rules for their actually demanded subfields

Status: `concrete_demanded_selector_contract_gap`. IR: ir_346, ir_358.

Selected mapping asks each opaque wrapper output for collection cardinality and each entry apiName, uiName and description. Each selected compute has only a whole-value output rule. There is no deterministic select/build expression inside these opaque operations that supplies those exact rules.

Even with a subsequently accepted review, these exact selectors need matching semantic rules or a supported exhaustive decomposition; the whole-value rule cannot stand in for them. In this run missing review is the earlier blocker. No error is inferred from scalar whole-value rules or the aggregate count of whole rules.

Source: skill/scripts/src/api/metadata.ts:46-48; skill/scripts/src/api/metadata.ts:68-70; skill/references/api-reference.md:165-183.

## ASSEMBLY-03: Bulk save-label contract requires nonstring contents that its formula ignores

Status: `source_supported_conditional_necessity_concern`. IR: ir_248.

The selected rule demands the whole present dateRange value while its reason says nonstring contents are irrelevant. The source copies a string but emits the literal custom for every nonstring date range. A nonstring object needs its type distinction for this output, not its startDate/endDate contents.

This local contract overstates necessity for this consumer. Date parsing and other consumers can still require the object fields; no global deletion follows.

Source: skill/scripts/src/api/bulk-lookup.ts:169-188.

## ASSEMBLY-04: Ignored filters and ordering remain recorded as a source mismatch

Status: `source_mismatch_preserved_but_typed_review_unavailable`. IR: ir_150, ir_166, ir_167, ir_171.

Task retains documented filter/order obligations. Mapping explicitly records that filters and orderBy are bound with no downstream request slot; sensitivity retains the actual supplied filter and sort values. Mapping only demands the actual limit inclusion test and supplied request.limit. It does not invent correct forwarding.

The source input problem is visible in prose, but no source review completed and the receipt contains zero source_input_findings. Absence of typed findings is unavailable review evidence, not evidence that no semantic input error exists.

Source: skill/references/api-reference.md:35-43; skill/scripts/src/api/reports.ts:77-100.

## ASSEMBLY-05: Validation truth and authentication values are distinguished

Status: `positive_scope_distinction_with_helper_boundary_limit`. IR: ir_024, ir_040, ir_049, ir_050, ir_059, ir_060.

Mapping demands only truth of propertyId, clientEmail and privateKey for the missing-setting check, but actual email/key values for the GA4 credentials constructor. Sensitivity distinguishes fixed missing-setting messages and authentication capabilities from plaintext credentials. The compact GoogleAuth calls have zero explicit credential arguments; mapping explicitly records that limitation rather than fabricating operand slots.

These selected distinctions are source supported. They do not establish complete environment-to-authentication demand propagation through the summarized zero-argument helper boundaries.

Source: skill/scripts/src/config/settings.ts:40-74; skill/scripts/src/core/client.ts:67-79.

## ASSEMBLY-06: Status rows retain their original URL and selected inspection projection

Status: `positive_consumer_and_occurrence_distinctions`. IR: ir_436, ir_531, ir_551, ir_553, ir_557, ir_562.

Mapping pairs success and error rows with the current original URL, describes ordered iteration, suppresses child saves, and retains the aggregate save. Sensitivity separately records pre-attempt and post-attempt exceptions and the full acquired inspection result. The successful checkIndexStatus row uses indexStatus and verdict === PASS, excluding link/mobile/rich sections from that row without claiming they were never acquired.

This is source-supported consumer-specific precision. Protected-call clock/error/effect gaps remain local and explicit. It is not a proof of complete loop execution or final deletability.

Source: skill/scripts/src/index.ts:304-345; skill/scripts/src/api/indexing.ts:149-192.

## ASSEMBLY-07: Empty bulk persistence exception is recognized downstream

Status: `task_scope_concern_partly_cleared_in_mapping`. IR: ir_223, ir_224, ir_249.

Task does not explicitly list the empty-bulk no-save exception. Selected mapping now explicitly says the empty branch precedes filter building, acquisition and saving and demands only rowCount and rows cardinality there. analysis_persistence records the bypass as a concrete source gap.

The earlier concern is partly cleared at mapping, but Task wording and its declared exception set remain less precise than the source. There is no justification to invent an empty-result save or create a universal persistence blocker.

Source: skill/scripts/src/api/bulk-lookup.ts:155-164.

## ASSEMBLY-08: Unused internal save returns are not promoted to required outputs

Status: `positive_public_return_and_workflow_gap_distinction`. IR: ir_077, ir_078, ir_083, ir_088, ir_134, ir_135.

storage_save demands the public saver action, destination, complete supplied wrapper, and its returned path. The 25 internal save sites still have no output. analysis_summary states the documented read-and-Markdown obligation and the missing executable successor, selected file association, input projection and writer; it adds no whole-file demand merely because a read could observe the whole object.

The summary gap has concrete source anchors and missing relationships. It is not an excuse to discard the documented summary obligation or claim the workflow has been completed.

Source: skill/SKILL.md:53-64; skill/scripts/src/core/storage.ts:79-95; skill/scripts/src/core/storage.ts:155-170.

## ASSEMBLY-09: Latest-result substring mismatch may be a source error rather than an ambiguous purpose

Status: `task_uncertainty_classification_concern`. IR: ir_127, ir_134, ir_135.

Task retains the operation restriction but marks latest_operation_matching unresolved. Mapping precisely describes sanitized substring matching against a full path and the possible longer-name, suffix or directory collision. The API describes filtering by operation; no public text promises prefix collisions.

The cited conflict is concrete, but a failed implementation of a clear operation filter should be considered a semantic mismatch before treating the purpose itself as undecidable. This independent audit cannot supply the missing source-review classification.

Source: skill/references/api-reference.md:393-403; skill/scripts/src/core/storage.ts:155-170.

## ASSEMBLY-10: Some local tool contracts cite actual operands without a necessary-interface argument

Status: `interface_evidence_needs_unavailable_review`. IR: ir_451, ir_456.

For example, ir_451 cites only the actual saver arguments at index.ts:71-76; ir_456 cites only actual report operands at index.ts:89-94. Those lines establish invocation facts. The separate saver/report definitions and public interfaces may support required scopes, but the attached evidence alone does not show why each listed input is necessary.

Do not certify these requirements solely from the fact that the implementation passes them. The absent source review was the step intended to check interface sufficiency/necessity, retained/excluded scopes and request/response pairing. No acquired-field narrowing capability is established: the receipt inventory has zero acquisition projections.

Source: skill/scripts/src/index.ts:71-76; skill/scripts/src/index.ts:89-94; skill/scripts/src/api/reports.ts:20-28; skill/scripts/src/core/storage.ts:58-64.

## Exact identities and limits

Selected processing file SHA256: `533595e3e761dc816c965817bcbe8497c1a8d9f5c505170bf09308b95376d8d0`.

Selected mapping file SHA256: `4691504e67d3e5fb732ec3504c3507388697546c0fea7fe781a6ae2e480a43d9`.

Selected sensitivity file SHA256: `afb788412267f597c6e84cdb7785d355a405711fe879a5e371ea4b07ae50e4f1`.

Failure receipt semantic SHA256: `6c6a02b8dcf29a783da3946cf52699219d6600dd4971c89ff188c7b230f143ca`.

The JSON companion contains every source quote, file hash, selected artifact hash, demanded metadata selector and all 25 save-seed checks. Canonical binding identities and file hashes are recorded separately.

- No backend report, input-assessment status, propagation reachability, DOE comparison, replay, cost or execution success is assessed here; root will bind their final artifacts separately.
- Thirteen API sites, 25 saves and three URL loops are finite source-boundary denominators. Representation is not processing, whole-source coverage, precision, recall or semantic correctness.
- Only selected r2 artifacts supply generated conclusions. Earlier rejected processing was not used as selected evidence.
- Positive findings and concerns are independent source-audit judgments, not model-review acceptance or a proof of minimal inputs.

Audit execution: zero model calls, Skill executions, backend runs, replays or production edits.
