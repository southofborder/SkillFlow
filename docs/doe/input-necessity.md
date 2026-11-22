# Semantic input necessity and field-level backward demand

Status: **POST-BATCH CORRECTIVE OFFLINE ACCEPTANCE IN PROGRESS**, 2026-11-11.
The original input-necessity GA4 → 001 → 010 → 013 batch and its four sole
zero-call replays are closed. GA4 failed during revision processing; the three
small cases produced partial DOE results. The original implementation, answers,
costs and verdicts remain sealed in the [closed batch assessment](../../output/verification/online-input-necessity-20261111/assessment.en.md).
The current correction has no new real validation. Its offline receipts are
under [input-necessity-completeness-20261111](../../output/verification/input-necessity-completeness-20261111/).
See [current-version navigation](../current-version.md) for final acceptance
status; individual passing receipts are not an aggregate acceptance claim.

## Purpose and demand starting points

The analysis checks unnecessary inputs, including accidental wrong inputs and
deliberate collection beyond the declared purpose. It does not classify an
author's intent or introduce a malicious-Skill detector. It retains the
[DOE objective](SkillFlow-DOE目标与设计原则.md): unnecessary sensitive payloads in
necessary actions and sensitive exposure caused by unnecessary actions both
remain in scope.

The backward starting point is not the current input list of an IR. The existing
seven-request workflow establishes it in three separate steps:

1. Task extraction reads only the complete frozen Skill and seals its declared
   purposes, requirements, issues and source references. It does not see CFG,
   processing, sensitivity or DOE results.
2. Task correspondence maps each sealed requirement to actual result, action,
   delivery or condition locations. Positive demands use `value`, `presence`,
   `cardinality`, `shape`, `truth` or `action`, with explicit paths and references.
   Supported constraints remain separate and create no positive demand seeds.
3. Source review checks that this mapping preserves the declared requirement.
   The deterministic engine then propagates each seed backward through actual
   processing, versions, conditions and recipient-specific uses.

A requirement to return a customer's name can therefore seed the actual return
value at path `["name"]`; a whole-record input does not turn that requirement
into a demand for every record field. A requirement for an entire result remains
a whole-result demand unless a supported decomposition preserves it. Source
ambiguity or missing task correspondence remains visible; the engine does not
invent precise requirements merely because fields are available.

A payload `input_use` demand preserves that information at that use. It does
not invent an `action` seed or imply that every argument of the surrounding
call is necessary. Tool interface transfer runs when the actual action or
response is demanded. This separation preserves the declared Task meaning.
Missing implementation, interface-field or serialization details alone do not
make an otherwise clear source-stated duty ambiguous. Genuine competing
source interpretations and representation-sensitive output obligations still
retain their Task issues and existing global policy.

## Semantic contracts for opaque computation

Structural operations and supported expressions already provide deterministic
transfer rules. This extension adds `compute.demand_transfer` for computations
whose semantics are not represented by those rules. Processing authors this
contract from source without receiving Task or downstream demands. It describes
which input information is needed to preserve a selected output; it does not
change the actual forward input list or remove existing possible observations.

For example, a computation declares inputs `a`, `b`, `c`, but its output `y`
depends only on `a.a` and `b.b`. A source-supported rule for `y` must account for
all three actual inputs:

| Input index | Required information | Remainder |
| --- | --- | --- |
| 0 (`a`) | `value` at `["a"]` | `independent` |
| 1 (`b`) | `value` at `["b"]` | `independent` |
| 2 (`c`) | Empty list | `independent` |

After review, demanding `y` transfers demands only to those two fields. If no
other requirement, consumer or applicable constraint retains `c`, its input use
is `deletable`. Independence is output-specific: an input unused by `y` may still
be needed by a different output or another consumer.

The maintained contract shapes are:

| Attachment | Fields and meaning |
| --- | --- |
| `compute.demand_transfer` | Nonempty `rules`; optional `output_parts`. Cannot coexist with `expression`. |
| Each rule | `output: {property, path}`, `inputs`, `reason`, nonempty source `evidences`. |
| Each input row | `input_index`, `required: [{property, path, if_present?}]`, optional `unresolved_ranges`, `remainder: independent / unresolved`, `reason`, optional remainder `gap`. Every actual input index appears exactly once per rule. |
| Explicit unresolved range | `{information: {property, path}, gap}`. It locates a semantic barrier within one actual input. |
| Unresolved `gap` | `code`, specific `reason`, exact `missing` fact/conflict, concrete `resolution`, nonempty source `evidences`. A remainder gap exists exactly when that remainder is unresolved. |
| Tool `input_contract` | The same input rows plus contract `reason`, `evidences`, and optional `acquisition_projections`. Applies to flat `call` and explicit tool/remote `deliver` and `receive`. |

Information properties are `value`, `presence`, `cardinality`, `shape` and
`truth`; `action` is not an information selector. Paths support fields, indices
and existing nested `each` selectors. `remainder` accounts for the complement of
the required and explicit unresolved ranges. Required and unresolved ranges
must not overlap for the same property, including overlapping `each`/index
selectors. Thus one object can have required `x`, unresolved `y`, and an
independent remainder containing `z`. An empty required list and no explicit
unresolved ranges, with an independent remainder, excludes that input from
this output's requirements.

Input required selectors may additionally set `if_present: true` when the
physical source or interface explicitly makes that field optional. The flag is
omitted when false and is forbidden on output selectors and `output_parts`.
Optionality preserves presence unconditionally and the requested information
when present; known absence does not create a missing-input error or a value.
The compact review scope descriptor exposes both effective rules. A redundant
separate presence row is unnecessary. An absent field
in a particular payload is not evidence that the interface makes it optional.
Source review independently checks this condition.

Gap codes distinguish `missing_source`, `missing_interface`,
`ambiguous_semantics`, `conflicting_evidence`, `unsupported_relation` and
`unmatched_output`. Generic explanations such as "The computation is opaque"
are insufficient. A valid limitation names the missing source/interface fact or
unsupported relationship, its resolution condition and its evidence. The
generic-wording rejection is only a structural floor. It does not establish
that a longer explanation is semantically specific; the independent source
review must check whether the missing fact really blocks that exact scope.

Output rules match exact property/path selectors. A whole-output rule is not a
precise rule for an arbitrary child, and a set of child rules does not implicitly
cover the whole output. Optional `output_parts` explicitly claims an exhaustive
decomposition, including required structure. Its entries are unique, nonempty,
match authored output rules and exclude recursive whole-value `[]`. Review must
check completeness. The engine may union those rules for a whole output and
subtract completely excluded components; an unmatched selector or partial
exclusion inside a component produces a located gap.

## Trusted tool interfaces and extra payload

The user-approved tool assumption applies to **source/interface-supported
required fields**, which are treated as sufficient and necessary for the
interface contract. It does not apply to every field actually passed. If an API
requires `record_id` but the Skill sends `{record_id, internal_note}`, the actual
payload still includes both fields while the tool contract retains only the
supported required field. Extra fields remain available for necessity and DOE
analysis. Tool names or existing payloads do not establish interface requirements.

The flat call attachment is copied to the paired raw request/receive operations;
explicit request pairing must preserve identical contracts. Compilation stores
contracts in `compiled_annotation.input_contracts`, separate from forward atomic
operations, with generated IDs, instruction IDs, raw operation paths and source
attachment pointers. Compilation mapping also preserves the authored wire
pointer. No new model stage or runtime tool execution is introduced.

## Complete expected-contract inventory

The current guided processing and flat-annotation entry points require an
explicit contract for every modeled opaque compute and every actual tool/remote
request or receive, including zero-input interfaces. A zero-input contract has
`inputs: []` plus its source-supported reason and evidence; it is not evidence
that the implementation has no hidden reads. A declared processing gap cannot
excuse a missing attachment on an operation that is still modeled.

The program derives `expected_input_contract_obligations` from actual operations
and validated locations, independently of Task and supplied attachments. Each
row has a stable obligation ID, actual IR/raw operation coordinates, expected
attachment pointer, input count and any exact request-pair identity. A compute
is exempt only when a successfully validated exact expression targets that
same operation. An expression on its CFG instruction does not exempt unrelated
nested computes. Supplied contracts are reconciled with these obligations.

Missing attachments are pointer-local processing representation failures and
use the existing structural-correction budget. Semantic review uses the existing
shared repair round. Neither path invents a contract, drops an actual input, or
turns missing annotation into a semantic source gap. Legacy/manual standalone
backend compilation remains able to represent absent contracts; demanded opaque
relations then fail closed locally. Old artifacts retain their own identities.

## Review and immutable evidence

The existing source-review request receives the complete frozen source,
selected material and a compact program-derived obligation/scope inventory.
Contract bodies remain in the annotation rather than being repeated in a
separate review table. The response explicitly includes four tables:
`findings`, `input_contract_checks`, `input_projection_checks` and
`source_input_findings`, including empty tables where appropriate.

Each expected obligation has exactly one contract check with `obligation_id`,
the actual `contract_id` (null when absent), `status`, `reason`, `evidences` and
`scope_checks`. A missing attachment must be rejected. An accepted check is a
shortcut certifying all its finite scopes. A rejected or unresolved check must
partition every scope exactly once into explicit accepted/rejected/unresolved
groups. Each group names `scope_ids`, its status, reason and evidence;
unresolved groups additionally require the typed concrete gap. Omitted or
duplicate scopes cannot pass validation.

Scopes distinguish each output rule, interface claim, complete-output
decomposition, required input selector, explicit unresolved input range and
input remainder. An accepted review of an authored unresolved range confirms
the location and nature of the barrier; it does not turn uncertain necessity
into a required or deletable result. A review-level unresolved/rejected scope
does not certify its authored information upper bound.

Wide rule/interface/decomposition barriers have no implicit whole-input effect.
They may identify `affected_scope_ids`, but those actual input scopes must also
have their own nonaccepted decisions. An empty affected list creates a claim
diagnostic without inventing retention of all input slots. Independent accepted
input/output scopes remain usable. Forward preservation and backward transfer
must use the same local decisions. An unaccepted complete-output decomposition
cannot certify absence of influence on unlisted output information.

Ordinary source-review findings that contradict the faithful representation of
the same operation or CFG location cannot coexist with accepted affected
scopes. Unrelated Task, sensitivity or operation findings do not revoke local
acceptance. Program-generated scoped contract/projection repair findings are
governed by their explicit decisions; their shared operation parent does not
invalidate independent scopes or the paired response.

Rejected or unresolved contract/capability checks route to processing within the
existing shared repair budget and dependency closure. The final selected review
produces `audit/input-contract-review.json`, bound to exact source, CFG, Task,
raw/compiled annotation, compilation mapping, expected obligations and scope
inventory. It stores normalized local decisions and source-input findings.
Formal DOE persists the receipt and revalidates the selected binding and
references on load. Unavailable review is recorded as unavailable, not as
invented semantic gap evidence. Unrelated partial coverage does not erase an
accepted local relation; it also cannot establish whole-source completeness.

Hash and reference checks establish which materials were reviewed; they do not
prove the semantic judgment itself. The separate source-review stage provides
an explicit, inspectable semantic acceptance rather than allowing processing to
self-certify. The method remains relative to those reviewed assumptions, not a
formal proof of arbitrary natural-language equivalence or global minimality.

## Known source-input errors

`source_input_findings` is separate from representation findings and rejected
dependency claims. A known `missing_argument`, `missing_field` or `wrong_field`
requires an actual operation target, separate requirement/occurrence source
evidence, an expected source relationship, and native action/output impact
selectors. A wholly missing argument uses `actual: {kind: absent_argument}`;
field errors use an existing input index and path. An optional expected lexical
source binding must resolve to an existing value. No missing Data, slot or
corrected value is synthesized.

Normalization derives a stable finding ID and actual operation placements.
For a lowered call, action impact belongs to its request and output impact to
its response; both placements appear only when both are authored. One source
defect is not duplicated into unrelated equal-argument calls. A faithful
description of the actual inputs can coexist with a known source invocation
error. It is not a request to repair the Skill's arguments or an assertion that
the invocation succeeds. Overlapping known defects gate the affected output or
action conclusion locally, while the original facts and demand seeds remain
unchanged. Missing interface knowledge instead requires an explicit local gap.

## Optional acquisition projection capability

A tool contract may additionally author `acquisition_projections`, omitted when
empty. Each row identifies `selection_input_index`, `selection_parameter_path`,
an exact `returned_range: {property: value, path}`, a reason and source evidence.
The selection operand must really exist; a source-supported optional selector
field may be absent inside it. The program validates the exact request/response
pair and derives one capability ID per pair and authored row, even though the
contract is copied to both lowered operations.

The source reviewer makes one separate scoped capability decision. Accepting
necessity does not accept projection, and rejecting projection does not reject
necessity. A whole-output capability does not imply arbitrary child-field
selection, and separate capabilities do not imply a supported union mask.
Reports can identify exact supported selected ranges from accepted capabilities.
They do not construct queries, choose parameter encodings, infer new capability
from a tool name, change the acquisition, or create demands. No reviewed
capability means `unestablished`, not that the interface is incapable of it.

## Input assessments and DOE

The demand result adds `input_assessments` for IR inputs, operation inputs and
read/receive acquisition outputs, preserving input indices, operation identity,
Data candidates and coverage. Each assessed range carries its property, path,
excluded subpaths, demand/diagnostic/contract references and one status:

| Status | Meaning |
| --- | --- |
| `required` | A nonconservative task-preservation derivation requires this information. |
| `deletable` | Completed analysis leaves no demand covering the range and preserves applicable declared constraints. This is an actionable analysis conclusion, not merely a candidate. |
| `unresolved` | A concrete missing relation, review, coverage, task requirement or constraint-preservation basis prevents a conclusion for this range. |

An input with `not_reached` coverage remains an inventory entry without a deletion
claim. Contract gaps follow actual derivation ancestry and affected output/input
ranges; an unrelated field or branch does not inherit a gap merely because it
shares an IR. Remaining unexpressed Task requirements and Task issues retain
their existing global effect. Supported constraints are checked independently;
they do not create positive demands or erase baseline violations.

Uncertain necessity remains `conservative`. A distinct `information_bound`
flag can certify only the information upper bound of an independently accepted,
authored explicit unresolved range. For example, uncertainty about a collection's
cardinality need not retain unrelated fields inside its members. The flag is
propagated only through an explicit whitelist of exact transfers; generic or
opaque conservatism and path widening do not acquire or preserve that
certification. Saved-result validation requires the bound receipt and ancestry
to a scoped semantic gap. Nonaccepted structural scopes remain conservative
without this flag in both backward overlap and forward influence.

`input_findings` reports `excessive_input` and source-supported `wrong_input` or
`missing_input` inconsistencies. The latter rely on explicit expected relations
or diagnosed missing requirements; the analysis does not infer the intended
operand from an arbitrary variable name. Findings do not distinguish deliberate
overcollection from a mistake.

Every assessment includes actual CFG/raw/wire locations, source spans with their
direct/inherited resolution, generated-origin status, scope and downstream use
sites where available. IR operands bound only through location/path metadata are
accounted for explicitly; absence of an ordinary value use alone does not permit
argument deletion. Synthetic observation contexts remain distinct from editable
source arguments. An established reduction has a semantic modification recipe
(`remove_input`, `exclude_field`, `keep_ranges`, or `omit_result_range_at_use`) or
an explicit reason why no concrete edit site/structural recipe is established.
These are located analysis conclusions, not executable patches.

Sensitivity comparison can use an explicit completed assessment to support
`remove_input` or `exclude_field` reductions at the exact operation use. All
sinks, recipients, conditions, versions and source sensitivities remain in the
comparison. Possible influence is still not proof of plaintext inclusion.
Each comparison persists `limitation_refs`: generic applicable blockers remain,
while input-contract gaps apply only through overlapping demand ancestry. The
boundary retains its aggregate limitations for coverage reporting. A gap for
one field does not veto an independently deletable field at the same boundary;
saved-result validation recomputes this distinction from the bound records.
Deleting an array member is not automatically supported because it may reindex
later demanded members. An acquisition-output finding describes unused acquired
information and its downstream uses. Narrower retrieval support is reported
separately, only through the reviewed capability above. The analyzer reports
reductions; it does not rewrite or execute Skill code.

This rule supersedes older blanket wording that absence of demand can never
support deletion: **absence after completed, semantically reviewed demand
analysis supports deletion under the recorded assumptions**. Missing analysis,
missing requirements and unresolved preservation remain explicit blockers.
Earlier frozen runs and their verdicts are not recomputed or relabeled.

## Implementation and verification boundary

Primary implementation: `propagation/contracts/input_requirements.py`,
`propagation/annotation/compiler.py`, `document_guided/source_review.py`,
`doe/input_contract_review.py`, `doe/input_contract_scopes.py`,
`doe/input_contracts.py`, `doe/source_input_findings.py`,
`doe/input_assessments.py`, `doe/input_locations.py`, and the existing demand, constraint and sensitivity
engines under `src/skillflow/`.

The corrective protocol identities are:

| Interface | Version |
| --- | --- |
| Task | v5, unchanged |
| Security profile / standalone annotation | v23 |
| Processing compiler / compilation | v14 |
| Flat annotation / document fragments | v5 |
| Source-review fragment | v4 |
| Input-contract review receipt | v2 |
| Demand result | v9 |
| Sensitivity review result | v8 |
| Formal DOE run / format | v9 |
| Document-guided run | v11 |
| Document step / annotation | v10 |

The sensitivity v8 identity distinguishes the corrected result: nested demand
derivations, located input assessments and source-input findings differ from the
original measured v7 shape. Aggregate acceptance must use the final identities,
not relabel an earlier receipt.

Corrective offline acceptance passed 2,531 distinct current test identities,
with two skips and zero unresolved failures. Three obsolete identities have
explicit passing replacements; this is a union of scoped receipts, not one
all-green whole-repository execution. Final frozen lifecycle checks passed
37/37 with the implementation unchanged. Initial failures and exact corrective
reruns remain in [the acceptance record](../../output/verification/input-necessity-completeness-20261111/assessment.en.md).
Current prompt examples and synthetic fixtures express the required contracts;
frozen original runs and source artifacts retain their original identities. The
closed four-case authorization is exhausted. This corrective implementation
does not authorize another real run or replay.
