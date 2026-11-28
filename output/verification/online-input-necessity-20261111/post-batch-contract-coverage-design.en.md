# Post-batch contract coverage and review design

Date: 2026-11-11. Status: concrete offline implementation proposal only. Production, prompts, controllers and transport remain frozen for batch `20261111-173347`. This note incorporates coordination with the input-requirement schema agent and the separate known-source-input-error design owner.

## Preconditions and fixed boundaries

Before changing production, close all four original analyses and their sole zero-call replays. Complete and save the original closed-case cost/provenance audits while the current files still match the frozen snapshot. Preserve original selected materials, responses, diagnostics, costs, failures and replay receipts. A later corrected implementation must have separate identities and offline evidence; no new live run follows implicitly.

Keep seven normal semantic requests, two workers, existing structural correction and shared semantic repair budgets, Task/mapping/sensitivity isolation, and actual forward operands. Do not infer an action from a payload field goal. The five-case `payload-only-tool-contract-reproduction.en.md` establishes why this is a separate preservation property, not a missing transfer fix.

This work has three distinct targets: mandatory attachment coverage; structurally explicit, localized review uncertainty; and the separately designed typed known-source wrong/missing-input findings. They share review and receipt versioning but must not be conflated.

## 1. Deterministic expected obligations

Add a pure helper alongside the existing normalizer in `src/skillflow/propagation/contracts/input_requirements.py`:

```python
expected_input_contract_obligations(
    targets, locations, *, exact_expression_targets
) -> list[dict]

enforce_current_input_contract_coverage(
    obligations, compiled_contracts
) -> None  # located StructuralValidationError on mismatch
```

The helper reads actual processing targets and resolved location kinds, not Task goals, sensitivities or observed payload usefulness. The existing target index already traverses supported operation scopes/cases. Run after flat calls expand to their real paired deliver/receive operations; preserve projection back to the original wire operation through `mapping.wire_paths`.

Each obligation contains a deterministic ID, `kind`, instruction ID, raw operation path, expected attachment pointer, actual input count, and existing request-pair/scope coordinates where applicable. The ID can be `input_obligation_` plus a canonical hash of kind/instruction/raw-path. It must not include supplied contract content, so a missing attachment still has an identity. The selected annotation hash prevents an ID from becoming an assertion of cross-version equivalence.

Expected obligation rules:

- Every tool/remote deliver and receive operation needs `input_contract`, including the two products of a flat call and explicit authored forms. Resolve the location kind; do not infer a tool from its name. Include zero-input operations with explicit `inputs: []`, reason and evidence. Empty declared inputs are a vacuous input-row inventory, not evidence that hidden reads or source-required omitted arguments do not exist.
- Every compute without the existing supported exact expression mechanism needs `demand_transfer`, including a zero-input compute. Exact-expression exemptions must match the actual operation/output coordinates used by the engine. Validate expression grammar, references and source evidence first. An expression at one instruction or sibling operation must not exempt all nested computes.
- Reuse the engine's exact expression target-resolution semantics. It currently stores expressions by `(instruction_id, target.raw_path)` and looks them up by the actual operation raw path (`demand_engine.py:236`, `:773`). Do not add a new instruction-to-compute inference to make an exemption pass.
- Preserve identical request/response contracts, complete per-input row checks, and existing output selector rules. Attachment presence does not prove complete output semantics. A whole-output rule must still not match a narrower selector; several field rules do not silently form a closed decomposition. Do not infer required selectors from Task in this processing-only check.

The obligation inventory is separate from compiled contract entries. Supplied contracts continue to carry their existing content-based IDs. A reconciliation table records obligation ID to actual contract ID, or a missing attachment. Unexpected or duplicate attachment mappings remain structural errors. Precise expression targets may be recorded as an exemption inventory for audit, but do not need a new contract or model check merely to restate the existing validated expression.

## 2. Current guided validation and repair ownership

Call the helper from current `annotation_wire._validate_processing_backend` after ordinary spec and exact-expression validation. Missing/null attachments produce located diagnostics at the actual expected attachment pointer. A declared `processing_gap` must not excuse a missing attachment on an operation that is still represented as modeled.

These are processing-owned representation failures. The normal processing response enters the existing structural correction; semantic source-review defects enter the existing processing repair and its established dependency rebuild. Do not add calls, retries or a second repair round. If budgets expire, retain the failed/isolated scope and ordinary partial provenance. Never fabricate input requirements, remove the actual operand, or reword a missing attachment as a source ambiguity.

A genuine source/interface limitation uses an explicit per-input unresolved row with a concrete fact, source evidence and affected range. The new presence rule does not require pretending that the missing fact is known.

Keep `RawDeliverOp`, `RawReceiveOp` and other legacy/manual attachment fields optional unless a separate serialized format change is required. Standalone/manual parsing retains the existing conservative, demand-triggered interface boundary. The stricter presence invariant is a property of the new guided entry, not a migration of old artifacts.

## 3. Review inventory independent of supplied contracts

Recompute expected obligations from the selected raw annotation and existing exact expressions when preparing source-review material. Bind the reconciliation table and projected actual review targets. Projection must use the ordinary wire-path map; it cannot depend on an existing `mapping.input_contracts` entry, because missing attachments have none.

The new review protocol should retain one finite `input_contract_checks` entry per expected obligation, with:

```json
{
  "obligation_id": "input_obligation_...",
  "contract_id": "input_contract_... or null",
  "status": "accepted | rejected | unresolved",
  "reason": "Source-backed review conclusion",
  "evidences": [],
  "scope_checks": []
}
```

`contract_id` must match the deterministic reconciliation; it cannot be null for acceptance. A wholly absent attachment is a representation rejection with the actual operation target, not a legal unresolved semantic contract. Source spans remain nonempty and valid. The new current schema should require the check list explicitly, even when the expected inventory is empty. Supplied optional contracts, if any outside mandatory obligations, still require their own deterministic review obligation so none escape review.

Partial/unavailable processing is not a way to assert complete expected coverage. Preserve existing processing gaps and stage availability in review material. Do not infer absent operation details from Task or source prose mechanically. The review can complete locally available checks while global source completion remains accurately partial. Unrelated findings must not revoke an independently supported local contract.

## 4. Confirmed review-level unresolved structure gap

The frozen `InputContractCheck` at `src/skillflow/doe/input_contract_review.py:22` has only contract ID, status, reason and evidence. `checked_contract_checks` at line 46 validates exact supplied IDs and source spans. It does not require a missing/conflicting fact, resolution condition or affected input/output scope. `source_review.py:480` asks for specificity, but lines 557–566 accept the structure and turn any nonaccepted free-text check into a processing finding. This is a confirmed structural validation gap.

The processing `InputRequirementGap` is stronger: it requires a code, missing fact and evidence. Its generic-text guard at `input_requirements.py:48` is still only a normalized finite blacklist; longer vague wording can pass. Reuse that lexical floor, without presenting it as proof of semantic specificity or adding a natural-language classifier.

For review-level uncertainty, require typed scope and gap records. Proposed minimal gap contents:

```json
{
  "code": "missing_source | missing_interface | ambiguous_semantics | conflicting_evidence | unsupported_relation | unmatched_output",
  "reason": "Why this particular fact blocks the identified relation",
  "missing": "Exact fact or unresolved conflict",
  "resolution": "The source/interface fact or relation needed to settle this scope",
  "evidences": []
}
```

Every unresolved scope must have such a gap; accepted scopes must not. Conflicting-evidence records must identify the conflicting source spans/claims, not merely name the code. Validate original source files and inclusive line ranges. Reject generic-only reason/missing/resolution text using a narrow documented lexical guard. Independent source review still judges whether the claimed absence or conflict actually prevents resolution.

### Finite local scope accounting

A contract-wide unresolved flag cannot both withhold an uncertain claim and certify unrelated claims. Derive a finite scope inventory from the present contract, rather than allowing arbitrary unbound reviewer paths. Scope identities cover each exact output-rule/input requirement range and its remainder; tool scopes have no invented output selector. Include the explicitly authored output decomposition assertion when present. A whole-rule/interface scope may identify a genuinely wider missing relation, but must enumerate the affected actual input scopes; zero inputs do not justify an invented slot.

For `accepted`, the check explicitly certifies the complete enumerated contract scope. For any partially unresolved check, `scope_checks` must form an exhaustive, duplicate-free partition of the actual scope IDs into supported and unresolved/rejected decisions. Each uncertain decision includes the typed gap and evidence. Do not treat an omitted scope as accepted. An implementation may compact supported scope IDs into one group with shared evidence; it must expand to the same finite checked partition.

Validate the output selector against the contract's actual rule or output-parts assertion, the input index against actual operands, and the information range against the referenced authored claim/remainder. Preserve field/index/member-scope types. Whole absent arguments cannot be represented by an out-of-range index; they belong to the separate known-source-input-error channel. If reviewers identify an unmodeled narrower relation, they must reject/repair the relevant authored claim, not silently invent a new contract rule in the review.

### Backend use of localized decisions

Replace the all-or-nothing review gate for a transfer with a lookup of the selected contract's reviewed scopes. A selected output/input relation can use supported scope decisions; an unresolved relation conservatively retains only the affected actual input information, with exact diagnostic ancestry. A truly whole-rule gap retains every affected actual slot. Other output rules, input slots and independent operations keep their supported status.

Do not broaden tool requirements until a declared action or demanded response activates that interface. Do not let a local review gap create global demand or invalidate unrelated contracts. Continue existing constraint-preservation checks. Public `source_review_complete` describes bound material and review coverage, not the absence of findings; local decisions carry the semantic acceptance state.

This local decision structure is a refinement of the existing review response and deterministic contract lookup. It adds no semantic stage, source rewriting or extra inference mechanism. Final field names should be coordinated with the typed source-input-finding schema before implementation.

## 5. Immutable receipt and known-source input findings

Receipt v2 should seal the deterministic expected-obligation inventory, its supplied-contract reconciliation, derived review scopes, normalized decisions and the source-review core. Add an `obligations_sha256` binding or include the complete inventory in the already hashed core; always rederive and compare the inventory from the selected bound annotation when loading. A caller-provided completion Boolean is insufficient. Retain the existing source/CFG/Task/annotation/contract hashes and overlapping-finding consistency checks.

Receipt validation must reject an omitted obligation, mismatched contract ID, omitted/duplicate scope, accepted missing attachment, forged source span, out-of-range input reference or decision conflicting with a related representation finding. A valid hash only proves identity, not semantic truth.

The separate design owner proposes required `source_input_findings: []` in review v4 for source-established wrong-field and wholly missing-argument errors. Bind these typed findings in the same review core and receipt, but keep them separate from representation findings and uncertain contract claims. They refer to actual operations, actual argument references where present, and original source/interface evidence. A faithful contract can coexist with a source error in the actual Skill; do not automatically repair the Skill operand or reject every faithful contract because of that finding. Missing arguments use explicit absence, never fabricated Data or invalid indices. Coordinate native action/output impact selectors with the existing deterministic backend; no Task seeds are invented.

### Receipt query API agreed with backend ownership

The review/receipt implementation owns deterministic normalization; the backend owner retains output-selector matching, range intersection and demand propagation. The following helper returns a read-only projection of the checked receipt and the already bound contract, with no semantic inference:

```python
reviewed_contract_scopes(receipt, contract_id) -> dict
source_input_findings_for_operation(receipt, instruction_id, raw_path) -> list[dict]
```

`reviewed_contract_scopes` has this normalized shape; metadata/reasons/evidence may be deduplicated by scope ID in storage:

```text
{
  available: bool,
  obligation_id, contract_id, kind,
  rules: [                              # compute only
    { output: authored selector,
      decision: ScopeDecision,          # whole-rule sufficiency claim
      inputs: [ReviewedInputRow] }
  ],
  inputs: [ReviewedInputRow],            # tool only
  interface_decision: ScopeDecision,     # tool only
  output_parts: null | {parts: authored selectors, decision: ScopeDecision}
}

ReviewedInputRow {
  input_index: actual index,
  required: [{information: authored InformationRequirement, decision: ScopeDecision}],
  remainder: {
    authored: {status: independent | unresolved, reason, gap?},
    decision: ScopeDecision
  }
}

ScopeDecision {
  scope_id,
  status: accepted | rejected | unresolved,
  reason,
  evidences,
  gap?: typed review gap
}
```

Program-generated scope IDs derive from the actual contract ID and exact claim coordinates. The scope inventory includes whole-rule sufficiency (or the actual interface assertion), authored required ranges, each input remainder, and authored output decomposition when present. The reviewer can select existing scope IDs but cannot introduce a new input row, selector, rule or field requirement. Aggregate check status is a summary of the scope decisions, not a blanket backend acceptance gate.

`available` means a completed, correctly bound review with a complete decision partition for this actual contract. It must not depend on every unrelated contract being accepted or on the absence of unrelated findings. A missing/unavailable review has `available=false` and uses the existing conservative boundary. An absent contract returns an unavailable entry through its expected obligation; it cannot yield an accepted empty semantic relation.

An authored unresolved input remainder and a review-level unresolved decision are different. Review may accept that the authored source gap is accurately represented; the transfer still retains that authored unresolved remainder conservatively. Conversely, review uncertainty concerning one requirement/remainder must not invalidate a different independently accepted input scope. A genuinely nonaccepted whole-rule/interface decision prevents reliance on that entire affected rule/interface, while independent rules remain usable.

The backend must consult this same projection in both backward `transfer` and forward `influenced_outputs`. Forward influence may exclude an output only when the queried range is covered by accepted independence. If the query intersects a nonaccepted required/remainder/whole-rule scope, retain the existing unknown-influence result for that scope. A gap concerning another input or output is not a reason to return whole-contract unknown. Whole-output decomposition is usable only when its own decision and the selected component decisions support it. This changes review-granularity lookup, not expression evaluation or Task seeding.

For within-object uncertainty, the schema owner's proposed optional `InputRequirement.unresolved_ranges` contains `{information: InformationRequirement, gap: InputRequirementGap}` rows. It is omitted when empty; gap selectors do not gain `if_present`. Derive one review scope for each authored explicit gap range. `ReviewedInputRow` correspondingly adds `unresolved_ranges: [{information, authored_gap, decision}]`. The independent/unresolved remainder describes the complement of required and explicit unresolved ranges. Validate property/path overlap and duplicates deterministically. This supports required `x`, uncertain `y`, and independent `z` without expanding a membership/cardinality uncertainty to unrelated member payload values. Transfer and influence queries must use the same finite range boundaries.

The source-error helper returns a canonical finding ID, its authored actual/expected relation and evidence, plus **only the requested operation placement's** native impacts. The sealed normalized finding has program-derived `operation_refs: [{instruction_id, raw_path, impacts}]`. For a flat call, an action impact maps to its real request deliver and an output impact to its real receive. Project both only when both impacts are authored; retain one finding ID rather than reporting the same source error twice. Do not copy a finding to unrelated calls with equal arguments. The receipt helper performs no demand intersection; the backend's `SourceInputMismatchIndex` uses these placements.

The coordinated source-error design is `post-batch-source-input-mismatch-design.en.md`; schema-side inventory recommendations are in `source-audit/post-batch-mandatory-contract-plan.md`. A source error may coexist with faithful actual transfer semantics, but its reviewed impacts must block affected sufficiency claims before deletion conclusions. This is independent of the partial-review decision table above.

### Lossless compact review input

Do not duplicate complete contract bodies in both the compact annotation and a new review table. Preserve the complete source and one authoritative representation of every selected claim. Emit only deterministic obligation/scope IDs, actual coordinates and references to that representation, or derive a shared compact skeleton that is equivalent after expansion. Full accepted-contract status may be a shortcut certifying all listed scopes. Partial or rejected decisions must still expand into an exhaustive, duplicate-free scope partition; compact groups cannot silently accept an omitted scope.

The parent observed 799,018 characters in the initial review against a 1,048,576-character cap, and the repaired graph grew from 535 to 658 IR. These are concrete planning constraints: adding mandatory tool contracts and scope inventories can increase the final material substantially. Measure exact serialized current inputs during offline acceptance. If compaction is necessary, verify a lossless expansion/identity round trip using the same selected material. Do not truncate source or claims, split review into extra model requests, add fallback calls, increase budgets, or treat over-limit input as successful review.

For an `if_present` required-information scope, include its compact program-derived effective semantics: unconditional presence preservation and conditional requested information at the same path. The flag already preserves known absence and needs no redundant presence row. This addresses the source-review misinterpretation preserved in `010-if-present-review-interpretation-note.en.md`; it changes guidance/visibility of the fixed rule, not raw facts or seeds. Source-supported optionality remains an independent review obligation.

### Optional acquisition-projection capability coordination

The parent additionally requested a design for source-backed acquisition projection, owned jointly by the schema and report agents. It is an optional authored relation between an existing request selection-parameter location and an existing returned information range. It does not follow merely from downstream result use, parameter names or an apparently filterable tool.

Each supplied capability becomes a deterministic **optional review scope** in the same review protocol. Its scope ID binds the actual request operation/input slot/parameter path, the actual response operation/returned selector, the existing lexical or occurrence scope, and the normalized authored relation. The program resolves the real request-response link; equal arguments, identical Data IDs or shared receiver names cannot establish the pair. An absent capability adds no mandatory contract obligation and creates no Task seed.

A flat call copies the authored contract to request and response, but its capability is one relation. Derive one capability ID and decision from the exact pair plus the authored capability row; reference that same scope from both placements. If storage retains two projected rows, require identical decisions and deduplicate them on normalization. Never accept contradictory request/response capability decisions or count one authored capability as two independent findings.

The capability's accepted/rejected/unresolved decision is independent of the necessity contract's decisions. Rejecting a capability must not revoke a valid input-transfer relation, and accepting a transfer must not certify projection support. Unresolved capability decisions use the same typed, locally referenced gap structure. The immutable receipt rederives pair identity and validates the selected input/output references on load.

Proposed read-only query helper:

```python
reviewed_acquisition_projections(
    receipt, request_instruction_id, request_raw_path,
    response_instruction_id, response_raw_path
) -> list[dict]  # authored normalized relation plus checked scope decision
```

The downstream report can intersect currently retained result information with a reviewed capability and report the supported selected range. The helper does not construct queries, rewrite request values, discover capabilities, execute tools or alter demand seeds. Where no reviewed capability exists, report the specific material boundary, such as "No reviewed projection relation is supplied for this actual request-response pair." This is not a claim that the interface is incapable of projection or a substitute source-semantic gap.

Keep the full capability payload once in the compact annotation and reference it by ID/coordinates in the review inventory. The coordinated schema recommendation is optional `ToolInputContract.acquisition_projections`, omitted when empty, with rows `{selection_input_index, selection_parameter_path, returned_range, reason, evidences}`. `returned_range.property` is restricted to `value`. Each row supports independent selection of its exact returned range: a whole `[]` range does not grant descendant-field projection, and multiple rows do not imply a supported union mask. A source-supported optional selector field may be absent inside an existing real request operand; the row never creates a new operand or concrete query encoding. Copy the authored call contract to its exact paired deliver/receive, bind the existing raw receive output wrapper, and derive operation/scope IDs in code.

## 6. Version changes

Minimum coordinated new current-route identities for this proposal:

| Surface | Frozen version | Proposed version |
| --- | --- | --- |
| Flat annotation wire | v4 | v5 |
| Fragment protocol | v4 | v5 |
| Guided run | v10 | v11 |
| Guided step / annotation | v9 / v9 | v10 / v10 |
| Fragment source review | v3 | v4 |
| Input-contract review receipt | v1 | v2 |
| Formal DOE run / format | v8 / 8 | v9 / 9 |

Update the guided policy's `input_contract_review` marker from its present v1 policy to the new mandatory-obligation/scoped-review policy. The standalone legacy source-review identity need not change unless its contract is deliberately changed.

Keep security profile v22, processing compiler/compilation v13, runtime v11 and forward record/propagation versions unchanged **if** their serialized formats and semantics are unchanged. Do not store a new inventory in compiled annotations merely to force a broad version bump: review can rederive it from bound existing fields. If implementation does change a serialized compiled shape, bump its owning profile/compiler identities explicitly. Demand/sensitivity result versions must change only if the coordinated typed source-input-findings/local-review work changes their schema or compatibility contract; their owners should settle that together. Never alter frozen snapshots or historical literals.

## 7. Offline acceptance matrix

Mandatory coverage: missing/null compute contract with no exact expression; valid inline and exact supplemental expression; sibling/instruction expression cannot exempt an unrelated compute; call, explicit deliver and explicit receive; paired both-missing and one-sided contracts; supported cases/for-each scopes; empty-input interface; unrelated non-tool observation; legacy/manual optional parsing.

Review/receipt: missing expected obligation; empty check list against nonempty inventory; wrong/duplicate contract binding; missing/malformed gap fields; generic-only gap; invalid source span; output selector not in the contract; invalid input index/member path; incomplete scope partition; accepted missing attachment; receipt tampering; selected CFG/annotation change; unrelated finding preserves local acceptance; related finding cannot coexist with accepted affected scope.

Locality: one output/input uncertainty retains its affected range while independent inputs and output rules remain usable; true whole-rule uncertainty retains all affected actual slots; accepted remainder remains distinguishable from uncertainty; no diagnostic leaks to an unrelated same-IR receiver. Preserve the existing five payload/action cases and constraint-preservation checks.

Known source errors: add the separately owned missing-argument and wrong-field tests, checking that actual records remain unchanged and source errors remain distinct from representation rejection and uncertainty. Use injected offline review responses only. Preserve initial failures and exact corrective receipts. Do not launch another real batch as part of this acceptance.

## Latest passive online audit

The separate provisional GA4 audit at `cost-provenance-audit/ga4-20261111T112239284605Z.json` observed 12 launch markers and 12 PID-confirmed starts at 19:22:39 China: 7 normal, 2 structural corrections, 3 semantic repairs. Eleven requests had complete public usage and one remained unknown. Known public usage was 1,919,852 tokens; outer retry count was zero and one public internal reconnect notice was retained separately. Source, implementation, helpers and executable hashes matched; no discrepancies were recorded. These are not final cost figures. Closed-case audits must still be saved before the production freeze is lifted.
