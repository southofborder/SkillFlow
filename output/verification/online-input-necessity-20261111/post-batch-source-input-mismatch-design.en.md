# Typed known-source input mismatches: post-batch proposal

Status: design only. Do not implement before all four frozen controllers and their sole replays close. This proposal does not authorize another real model batch, a Skill execution, a historical replay, or modification of current-run artifacts.

The required addition is a small typed channel from the existing seventh source review to the existing immutable receipt and `input_findings`. It reports an independently source-established defect in the Skill's actual inputs. It is separate from representation repair findings and from uncertainty about a dependency contract. No additional semantic request, worker, retry budget, general exception mechanism, or substitute argument is needed.

The current gap is reproduced in `../input-necessity-20261111/missing-slot-audit/`: a documented two-argument interface called with one actual argument produces `input_contract_rejected`, but no `missing_input`. The actual-record invariant correctly prevents appending an invented slot. Keep that invariant.

## 1. Review schema

Add required `source_input_findings: []` to the **new** source-review fragment protocol. Old fragments retain their original schema and are not reinterpreted. An empty table means the reviewer reported no established source-input defect; it is not a completeness certificate.

Each authored entry uses this exact proposed shape. Program-generated IDs and compiled operation IDs are deliberately absent from the model response.

```text
SourceInputFindingCandidate {
  kind: "missing_argument" | "missing_field" | "wrong_field",
  target_id: ExistingOperationTargetId,
  actual: AbsentArgument | ActualInputRange,
  expected: ExpectedInput,
  impacts: NativeImpact[1..],
  requirement_evidences: TaskEvidence[1..],
  occurrence_evidences: TaskEvidence[1..],
  reason: nonempty string
}

AbsentArgument {
  kind: "absent_argument"
}

ActualInputRange {
  kind: "input_range",
  input_index: nonnegative integer,
  path: existing GoalPath
}

ExpectedInput {
  parameter: NamedParameter | PositionalParameter | SourceRole,
  information: InformationRequirement,
  source_value: ExistingLexicalValue | null,
  description: nonempty string
}

NamedParameter     { kind: "named", name: nonempty string }
PositionalParameter{ kind: "positional", position: nonnegative integer }
SourceRole         { kind: "source_role", description: nonempty string }

InformationRequirement {
  property: "value" | "presence" | "cardinality" | "shape" | "truth",
  path: existing GoalPath
}

ExistingLexicalValue {
  value: existing ValueRef,
  path: existing GoalPath
}

NativeImpact =
  { kind: "action" }
  | { kind: "output", property: InformationRequirement.property,
      path: existing GoalPath }
```

`parameter.position` is an interface/source position, **not** a CFG input index. A name or position must be explicitly supported by the requirement evidence. Use `source_role` only when the source establishes a necessary role without defining a formal parameter name. It is descriptive evidence, not a new lexical binding.

`expected.information.path` is relative to that described interface parameter or source role, never a CFG slot. For a `missing_field`, validate the real parent operand and the field-path grammar; do not require the missing field itself to exist, because its absence is the reported defect.

`expected.source_value` is optional. When present, its `ValueRef` must already be in the actual operation's validated lexical environment. Its path describes an intended relationship only: do not create Data, append a CFG operand, or issue a demand for it. When no correct value was actually acquired or represented, use `null` and retain the sourced description. Do not turn an expected source term into a Data identity by matching its name.

For `missing_argument`, `actual` must be `absent_argument`; no nonexistent `input_index` is accepted. For `missing_field`, `actual` identifies the supplied object slot and the missing field path. For `wrong_field`, `actual` identifies the actual consumed range; `expected` describes the distinct required source relation. If the call already passes a selected scalar, the actual slot path is `[]`, while its original wrong source-field expression is established by the occurrence evidence.

The table contains established semantic errors only. It has no `unresolved` subtype. A missing interface, ambiguous intended field, unavailable source binding, or uncertain error relation goes into the separately proposed typed review barrier, with its concrete missing fact and local scope. A rejected necessity claim alone is never sufficient to populate this table.

For example, a missing named tool argument uses `kind="missing_argument"`, `actual={"kind":"absent_argument"}`, `expected.parameter={"kind":"named","name":"b"}`, an expected whole-value selector and `expected.source_value=null` when no correct value exists. A source implementation selecting `request.c` where the source obligation requires `request.b` uses a real input slot/range for `c` and, only if available in that operation's lexical environment, an expected lexical reference to the original request with path `["b"]`. That reference describes the error; it does not select or manufacture the corrected value.

## 2. Evidence and semantic classification

Each finding needs two evidence roles, which may share a span when that span actually supplies both facts:

1. `requirement_evidences` establishes what input/field is required for the stated native action or output.
2. `occurrence_evidences` establishes the actual source call/read and shows that the selected CFG/operation faithfully represents the missing or wrong input.

The reason connects those facts and explains the declared impact. Current arguments alone cannot establish interface necessity. A tool name, generic API familiarity, a possible dependency, or a missing runtime value does not establish a source error.

The review must distinguish these cases:

| Source and representation | Correct channel | Repair behavior |
|---|---|---|
| Source calls `f(a,b)`; generated operation contains only `a` | Existing CFG/processing representation finding | Repair the representation within the existing budget, then rebuild dependent fragments and review the selected revision. |
| Source/interface requires `b`; source actually calls `f(a)`; representation faithfully has one input | `source_input_findings` with `missing_argument` | Preserve the one actual input. Report the known source error. No repair that adds `b`. |
| Source requires `request.b`; source actually supplies `request.c`; representation faithfully supplies `c` | `source_input_findings` with `wrong_field` | Preserve the original wrong field. Report its sourced expected relationship. No substitution. |
| The contract wrongly calls an unrelated actual input necessary | Rejected input-contract check / existing processing repair | Correct the necessity contract; preserve the actual input and observation. |
| The interface or intended output relation is unavailable or genuinely ambiguous | Typed local review barrier | State the exact missing fact and resolution; do not assert a source defect. |
| Optional parameter is absent and the source permits omission | No missing-input finding | Preserve the established optional presence/value semantics. |

The actual operation's existing occurrence/member/condition scope is retained. A conditional bug is not promoted to an unconditional defect. If an existing validated condition target supports the condition, retain that scope in normalized provenance; otherwise a more specific conditional error requires a local barrier rather than an invented predicate DSL.

## 3. Structural validation and normalization

Add a pure helper with a narrow API:

```python
normalize_source_input_findings(
    candidates, *, files, cfg, raw_annotation, compiled, mapping, review_targets
) -> list[NormalizedSourceInputFinding]
```

It performs reference checks only; it does not claim to prove the natural-language reasons.

- Reject unknown fields, invalid discriminators, empty required evidence, duplicate identical findings, missing native impacts, and malformed selectors.
- Resolve `target_id` through the selected operation target inventory. Reject Task targets, a fabricated IR, a whole annotation root, and nonexistent operations.
- Resolve compact/wire targets using the program mapping. A wire call can map to its real request/response pair; retain one source finding with program-derived operation references. Do not count the same omitted argument twice merely because one call has two compiled contracts.
- Validate actual slot bounds against the real operation uses, including request/response agreement. Do not treat an absent argument as an out-of-range actual slot. A missing-field selector must be nonempty; a wrong-field scalar argument may use `[]`.
- Validate every optional lexical reference against the existing environment. No unavailable input/local is synthesized. Validate field-path syntax, member markers and scope with the existing selector validators.
- Require a native output for output impacts. Reuse the exact output/property/path vocabulary and call-case scope already present; do not introduce model-chosen Task IDs, requirement IDs, demand seeds or receiver IDs.
- Validate source file names and exact evidence spans against the selected frozen source. Parameter names/positions and semantic adequacy remain seventh-step source-review obligations.
- Reject a contradictory combination where an overlapping ordinary CFG/processing finding says the offending actual binding is not faithfully represented while the source-input finding claims that same binding is faithful. Repair and rereview the representation first. Independent sensitivity or unrelated output findings need not erase a source fact.
- Generate the stable finding ID from normalized content and operation coordinates. Bind it to the selected receipt; models never choose IDs or change source/CFG data to fit them.

Do **not** weaken `check_input_coverage`: every actual input still has exactly one contract row. There is no contract row, Data node, or input assessment for an absent argument.

## 4. Contract acceptance versus a known unsatisfied obligation

Keep accepted/rejected/unresolved necessity-check states separate from the source error table. A faithful actual output-to-input relationship may coexist with a source error in the required result. Acceptance of that relationship does not certify that the Skill satisfies its intended output or that an invalid interface invocation is valid.

For a tool that requires `a,b` but actually supplies only `a`, the combined reviewed material can describe the real requirement on supplied `a` **and** the unsatisfied requirement for absent `b`. The source-error impact prevents a sufficiency claim for the affected invocation/result. It must not be implemented as "the one actual input is sufficient because the contract table contains only one row."

A false sufficiency claim or incorrectly mapped field still gets the ordinary contract correction. The correction may faithfully describe the error; it must not silently repair the Skill. Do not automatically revoke unrelated accepted output selectors or route the source-error table itself into processing repair.

## 5. Receipt, identity and loaders

Use the coordinated new identities `skillflow-document-source-review-fragment-v4` and `skillflow-input-contract-review-v2`. Include both the normalized source-input findings and their operation-target mapping in `review_core`; include them in `review_sha256` and `receipt_sha256`. Existing source/CFG/annotation/contracts bindings remain mandatory.

Normalized receipt rows carry program-derived `operation_refs: [{instruction_id, raw_path, impacts}]`. One canonical source-finding ID is shared by any exact request/response placements. For a flat call, an action impact maps to the actual request delivery and an output impact maps to the actual response receive. Both are present only if the reviewed finding supplies both impacts. Do not copy a finding to unrelated calls with equal arguments or to both phases without the corresponding impact.

On receipt load, revalidate candidate structure, evidence spans, selected operation/slot references, normalized IDs and target mappings, and compare the rederived normalized table with the sealed one. A checksum alone is insufficient. A repaired CFG/annotation, changed source, or changed review cannot reuse the old source-error ledger.

The deterministic demand result continues to bind the complete selected receipt identity, including an empty table. A caller cannot drop the finding table while retaining the same demand result. Sensitivity validation continues to compare the exact passed receipt with the bound demand result and to reconstruct only the read-only constraint index.

At implementation time, bump affected demand/guided/DOE protocol identities consistently (current demand v8, guided run v10 and DOE format 8 are frozen). A demand v9 and DOE format 9 are reasonable next identities, coordinated with the mandatory-contract and typed-barrier work. Bump the sensitivity identity if its persisted finding/provenance shape changes. Do not migrate or rewrite existing results; the four-case batch remains evidence for the frozen original version only.

## 6. Deterministic demand and finding API

Normalize one read-only index owned by the selected receipt:

```python
# Receipt-owned projection; no demand inference or executable-op lookup.
source_input_findings_for_operation(
    receipt, instruction_id, raw_path
) -> list[validated normalized finding with only this placement's impacts]

# Backend wrapper resolves actual occurrences/instances and intersects demands.
SourceInputMismatchIndex(receipt, engine)

index.for_operation(operation_key) -> list[normalized finding]
index.intersect(operation_key, demanded_information) -> list[matching impact]
index.report_findings() -> list[InputSemanticFinding]
```

The receipt projection returns the stable source-finding ID, authored actual/expected/evidence fields, and only the native impacts for the requested raw operation coordinate. `SourceInputMismatchIndex` wraps that helper for actual recorded occurrences. The index resolves only actual operation identities; it does not parse free-text parameter names into bindings. Native output intersection uses the same field/property/member containment rules as demand transfer. An action-only impact applies only to a demanded action. An output impact is not automatically an action seed, and an action impact does not automatically poison every response field without a reviewed relationship.

Apply the mismatch overlay at the common demanded-operation/action boundary, not only inside `_contract_transfer`. A source can select the wrong field through a deterministic `select_part` or construction operation with no blackbox contract. Its deterministic actual relation must remain intact while its separately reviewed required-field mismatch is reported. The new source-error table therefore does not require a contract ID to exist for every target.

Extend the existing `InputSemanticFinding` representation rather than creating a second unrelated error report. Keep public kinds `missing_input` and `wrong_input`; add a typed source-error subtype and explicit provenance:

```text
origin: "source_review" | "deterministic_relation"
source_error_kind: "missing_argument" | "missing_field" | "wrong_field" | null
source_review_refs: [stable source-input finding ID]
expected_input: ExpectedInput | null
actual: AbsentArgument | ActualInputRange | null
affected_native_information: [NativeImpact]
```

The absent-argument report uses `input_index: null` and never claims an empty field path is an actual absent slot or a deletion command. Existing deterministic missing-field/type/expected-relation findings retain their original diagnostic references and are not retroactively relabeled as source-reviewed findings.

When a demanded output/action intersects a known mismatch:

- Emit a specifically typed known-error diagnostic/reference, such as `source_missing_required_argument` or `source_wrong_input_field`, linked to the receipt finding. The error is **established under the reviewed source relation**, not an unknown-semantic-gap reason.
- Preserve the actual forward input/output/observation facts and existing provenance. Never emit an input demand or Data value for the absent/corrected input.
- Do not claim that retaining the actual supplied fields is sufficient to satisfy the affected required result. Deletion-preservation checks for dependent actual ranges carry that exact known-error reference; they must not obtain a vacuous deletion proof because the required result cannot currently be fulfilled.
- Keep the known semantic error in `input_findings` even if a dependent deletion assessment has to remain `unresolved` about preservation. The report must say "known missing argument; preservation of this affected result is not established," not rename the known defect "blackbox uncertainty."
- Propagate blocking effect only through the intersecting native output/action and actual dependency ancestry, using the existing local gap machinery with a distinct known-error cause. An independent output selector, input use, recipient, member or unrelated operation remains assessable. A whole-contract block needs specific whole-contract impact evidence.

An unused call can still have a source-semantic error in the inventory; this fact does not make the call task-required or create a seed. Unreached source positions retain their separate coverage state. Reporting a source-level error is not a claim that the invalid call executed or leaked data.

## 7. Report requirements

The existing English semantic-findings section should display the actual operation/Skill location, source-error subtype, sourced expected argument/field, actual input binding or explicit absence, exact evidence in both roles, native affected output/action, scope/coverage and immutable receipt reference. Required/deletable ranges remain in the separate full input inventory, including nonsensitive data.

For the two-argument example, the minimum visible conclusion is:

> `missing_input / missing_argument`: The documented interface requires argument `b`; the source call supplies only `a`. No actual slot or value for `b` exists in this representation. The affected invocation/output obligation is unsatisfied. The recorded call remains unchanged.

Do not present an invented patch, infer where the missing value comes from, or say the correct value was read. If the source already provides the correct field relationship, the report may state it as an expected relation without applying it.

## 8. Focused regression matrix

All additions below run offline after the frozen batch closes. Use exact selected sources and injected semantic replies; no new model probes.

| Case | Required assertion |
|---|---|
| Documented mandatory named `a,b`; source and actual operation supply `a` only | Typed missing whole argument, `actual=absent_argument`, actual arity remains one, no synthesized `b` Data/node/demand, source/interface evidence retained. |
| Source actually supplies `a,b`; generated operation omits `b` | Existing CFG/processing repair, no established source error before faithful representation; repaired selected receipt invalidates old review identity. |
| Source specifies `request.b` but source implementation passes `request.c` | Typed wrong-field finding with actual existing slot/range and sourced expected relation; original `c` read/observation remains. |
| Required field absent inside an actual object | Typed missing-field finding remains distinct from missing whole argument; existing deterministic detection still works. |
| Wrong-field source relation unavailable or two source statements conflict | No invented correct field; typed local review barrier with exact conflict, not a source-error finding. |
| Optional parameter legitimately absent | No missing-input finding; presence and supplied values retain existing if_present behavior. |
| Necessity contract rejected for overstating dependency | No automatic missing/wrong source finding merely from rejection. |
| Faithful input transfer plus known mismatch affecting only `y.x` | `y.x` cannot claim task-preservation sufficiency; independent `y.z` demand, deletion and constraint paths remain usable. |
| Missing input in a tool call with a documented error response | Scope the source error to the supported invocation/result obligation; do not invent success or suppress an independently specified error-handling result. |
| Source error on a task-unused call | Finding present, no action/output demand seed created. |
| Source error in a not-reached branch/member | Source finding retains not-reached coverage; no runtime-event assertion. |
| Wrong target, stale CFG, nonexistent actual slot, invalid lexical reference or out-of-source evidence | Structural rejection before demand analysis; absent_argument never accepted as a fabricated actual index. |
| Same wire call produces request/response contracts | One source defect is bound to the exact pair, not double-counted or transferred to a different call with equal arguments. |
| Representation finding contradicts faithful-source-error assertion on the same binding | Reject the contradictory combined review; repair and rereview selected material. |
| Modified or dropped source-finding ledger with old receipt/demand | Receipt/loader identity mismatch; no old result migration. |
| FIFO/LIFO and saved result loading | Same normalized errors, scoped impacts and assessments; read/load does not re-solve or mutate facts. |
| Injected seventh-step source-error reply | Same seven normal requests and workers; a faithful source error does not itself consume a processing repair to add missing input. |

## 9. Coordination and boundaries

This proposal was coordinated with the review/receipt agent and the input-contract schema agent. The review agent owns the joint v4/v2 receipt design and the separate typed unresolved-scope proposal. The schema agent retains strict actual-slot accounting and the mandatory contract inventory. This document owns the known-source mismatch distinction and downstream report/local-impact requirements.

Implement these pieces together after closure so an accepted contract, a local review barrier and a known source error have unambiguous independent meanings. Keep the actual-source defect report small: it is not a general source-code repair engine, an unconstrained expected-value interpreter or a new model stage.
