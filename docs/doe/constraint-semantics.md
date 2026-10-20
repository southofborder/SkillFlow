# General constraint semantics and DOE integration v1

Semantic baseline and first implementation: 2026-10-19. **Implemented for the
bounded fragment documented below; unsupported relations remain explicit.**

This document specifies four constraint families and their integration with
task-preservation demands. The current implementation adds five typed
declarations to fixed-Task realizations, reviews them in the existing declaration
axis, checks the frozen model, and gates otherwise eligible field reductions.
The [implementation reference](constraint-implementation.md) records the exact
interfaces, versions, evidence, and current limits. The companion
[acceptance matrix](constraint-acceptance.md) separates intended semantic
expectations from their executable baseline counterparts and preservation tests.
No historical run has been upgraded or recomputed by this change.

The [DOE goal baseline](SkillFlow-DOE目标与设计原则.md), immutable
[Task](task-evidence.md), [backward demands](backward-demand.md), and
[sensitivity comparison](sensitivity.md) remain the starting point. This design
does not prove natural-language completeness, irreplacability, global
minimality, or the absence of all sensitive exposure.

## 1. Responsibilities and distinct conclusions

Positive demands describe information and actions that must be preserved.
Constraints describe relationships that must be respected. Both restrict a
field reduction at a sink; neither assigns necessity to every IR.

| Question | Required basis | What it does not establish |
|---|---|---|
| Is the requirement expressed? | Supported semantics and bindings covering all applicable objects, with any remainder recorded as a gap. | The implementation satisfies it. |
| Does the current model satisfy it? | A complete check over the relevant abstract behaviors, or a supported counterexample candidate or explicit limitation. | A proposed reduction preserves it; real execution has occurred. |
| Does a specific reduction preserve it? | A rule showing that the reduction introduces no violation, does not enlarge an existing violation, and preserves related positive requirements. | The baseline Skill is compliant. |

These are separate judgments, not three new model-authored flags. Fully
expressed constraints can be violated. An unrelated reduction can preserve a
constraint whose baseline is violated or not established, if its independence
is actually proved. That baseline result must remain visible and unchanged.

The only reduction considered here is the existing `exclude_field` at a
specific payload slot, data version, element scope, and boundary. It does not
delete an action, alter a receiver, move processing, or execute a reduced Skill.
It does not mutate the shared source object or remove earlier observations.
Candidate eligibility and ordinary DOE prerequisites remain in force: a
prohibition alone is not a field-removal certificate.

## 2. Shared interpretation rules

### 2.1 Complete scope and event identity

The model must express the source requirement's scope using existing identities
and supported semantic parameters. The program resolves that scope to applicable
operations. A list of convenient local bindings is not evidence that all
required occurrences are covered.

An event means an occurrence of a declared action, not an array entry in a
propagation record. A source-level call may compile into a request delivery,
response acquisition, and model observation. These are separate analysis steps
but do not become three call attempts. The existing request/response relation
can establish the correspondence; an ambiguous correspondence is a limitation.

Operation identity, request identity, value version, and element scope must be
kept distinct. Equal Data IDs do not make two recipients or call occurrences
interchangeable. Repeated values do not collapse distinct iterations.

V1 supports task scope and the existing single-level per-element scope. It does
not support cross-task counters, arbitrary group keys, nested quantification,
or unbounded cross-occurrence matching state. Unsupported source requirements
remain present as gaps.

### 2.2 Execution and evidence boundaries

Checks start at the CFG's actual task entry. Additional roots used by propagation
to cover disconnected regions are not additional real task entries. A complete
check must account for all relevant supported paths, versions, and permitted
local orders from that entry.

Joined candidate facts are not a trace. An abstract bad path supports a
potential violation. The current result vocabulary uses `potential_violation`
for both direct static violation candidates and abstract bad paths; reasons and
operation witnesses retain the distinction, without claiming a feasible or
observed execution. `satisfied` is a model-relative conclusion only when the
supported check completes over its declared scope. Missing scope, unsupported
semantics, or an exhausted bound produces `not_established`.

No match is not automatically success. If the program proves that there are no
applicable events in a completely identified scope, a universal constraint can
hold vacuously. An unresolved selector, missing records, or an incomplete
analysis cannot use that argument. A separate requirement that an action must
occur remains a positive `action` obligation.

Source spans support the meaning of the requirement. CFG references support
real graph facts. Annotation positions locate declared processing relations.
True references do not prove the translation is semantically sufficient. The
source-only Task and its evidence are not rewritten to match the analysis.

## 3. Four families: the five-question matrix

### 3.1 Information-delivery prohibition

Meaning: information range **S must not reach boundary L through the forbidden
information relationship** in the complete applicable scope.

| Question | Design |
|---|---|
| What relationship is required? | Original information from a specified whole or field range must be absent from the specified deliveries, saves, or observations. Original content, derived information, and any causal influence are distinct prohibitions. V1 supports explicit original-value and field-content prohibitions. |
| What can be reused? | `ValueRef`, field paths and `each`, data versions, location identities, actual payload slots, scopes, and existing selection, construction, exclusion, overwrite, and subset relations. Task supplies the requirement and source evidence. |
| How does the program check it? | Resolve the complete applicable operation set and track the prohibited range into each actual payload. Direct content supports a static violation candidate. `derived/possible` supports possible violation or inability to exclude it, not plaintext containment. Model-relative nonviolation requires complete scope and supported absence at every relevant boundary. |
| How can a reduction preserve it? | A content-subset rule can show that removing a field from an otherwise unchanged terminal delivery cannot add prohibited content. A no-influence rule can preserve other relevant occurrences. Both require accounting for request/response effects, conditions, and later deliveries; direct payload subtraction alone is insufficient. |
| What prevents a conclusion? | Unknown information range, receiver identity, applicable scope, unsupported relation, incomplete propagation, or a source prohibition stronger than original-content tracking. An empty unresolved match set does not discharge the requirement. |

Prohibition and sensitivity are independent. Explicitly forbidden information
can be checked without a sensitivity label. A sensitivity label does not create
a prohibition. DOE still requires its own sensitivity, exposure, and
task-preservation basis.

The checker must inspect applicable internal operations as well as DOE sinks.
For example, a prohibition on task-internal storage still matters when the
operation has exposure level 0 and is excluded from the DOE sink list. The sink
inclusion rules do not change.

Range membership must use neutral information semantics. The sensitivity rule
that classifying a whole does not independently classify every child cannot be
used to weaken an explicit ban on content within that whole. Conversely, common
provenance or `possible` influence cannot resurrect an excluded or overwritten
original value. Original and replacement versions are checked separately.
Conversely, naming an explicitly selected child as the prohibited source does
not make its original parent whole clean. That whole, including an earlier
observation, still contains the child under the declared selection relation;
this is content identity, not reverse execution.

If a positive requirement demands the same information at the same prohibited
boundary, preserve the conflict. The program cannot silently prefer the ban or
the delivery, nor claim that deletion preserves both.

### 3.2 Execution condition

Meaning: every occurrence of **E implies C**, evaluated for that occurrence's
specified version, time, and element: `E => C`.

| Question | Design |
|---|---|
| What relationship is required? | Identify the event, the condition, its evaluation point, and its value and element identity. A condition from another attempt or element does not authorize this occurrence. |
| What can be reused? | CFG edges, actual dispatch inputs, existing Boolean/comparison expressions, direct CFG references, compiler mappings, and data versions. Reuse an existing expression by its location instead of copying its AST. |
| How does the program check it? | Give supported expressions their edge-enabling meaning and check whether every relevant abstract path reaching E guarantees C. Initially support Boolean relationships, constants, and same-version predicates. Do not parse natural-language conditions or provide arbitrary program path solving. |
| How can a reduction preserve it? | Preserve information controlling C, event reachability, element selection, and receiver identity. Follow indirect request-to-response dependencies when they can affect those quantities. A complete disjoint influence closure supports a local no-influence rule. |
| What prevents a conclusion? | Missing expression-to-edge interpretation, ambiguous time or version, unsupported expression, or incomplete dependencies. Model-provided proximity or bindings cannot establish independence. |

An opaque business test can remain an abstract Boolean predicate when its
identity and edge interpretation are explicit. The checker may reason about
that same predicate and its negation. It must not invent a taxonomy of concrete
results, equate two tests merely because their text matches, or treat unknown
values as true or false. An existing expression's syntax alone is not a proof
that the corresponding control edge enforces it.

Known invalid operands must remain invalid through nested comparisons and
Boolean expressions: a scalar/object count or invalid field access cannot
become a passing abstract tautology. `present` distinguishes a missing field
from existing null, false and zero. Supported transparent container facts retain
their types, while a genuine opaque alternative remains unknown even beside a
known candidate.

### 3.3 Occurrence upper bound

Meaning: within an explicit counting and reset scope, occurrences of **E are
at most k**.

| Question | Design |
|---|---|
| What relationship is required? | State the counting unit, nonnegative finite bound, and reset scope. Attempts, successful responses, and collection cardinality are different quantities. Counting success additionally needs the supported success condition and its response identity. |
| What can be reused? | CFG control and loops, atomic operation identities, request/response pairing, `for_each` collection and element scope, and compiled ordering constraints. |
| How does the program check it? | Propagate finite saturated counter states `0 ... k, overflow` through the supported control model. Alternative branches retain alternative states rather than adding mutually exclusive occurrences. Loops reach a finite-state fixed point; bounded unrolling is not a satisfaction proof. |
| How can a reduction preserve it? | Preserve information governing invocation, retry, loop continuation, selected elements, reset, and any success predicate. A request field can affect response and retry behavior even when no CFG node was removed. |
| What prevents a conclusion? | Unclear unit, reset or success semantics; unknown collection length without a supported bound; unsupported loop/data recurrence or cross-scope matching. Resource exhaustion means incomplete analysis. |

Three shortcuts are invalid: treating `count(collection)` as an event count;
counting request, response, and observation as three calls; and using the number
of stored records or symbolic `for_each.instances` as an execution count.

An unknown collection length may permit overflow in the task-wide abstraction;
it does not establish an actual collection size or feasible violating run. A
per-element limit resets for each element occurrence in the declared scope. It
cannot establish a task-wide limit. Finite counter state does not by itself
solve unsupported stateful loops in the underlying processing model.

### 3.4 Ordering

V1 has two distinct forms: **B requires an earlier matching A**, and **after T,
E must not occur** in the specified scope.

| Question | Design |
|---|---|
| What relationship is required? | Identify the events, matching unit, scope, and reset. An A for another element or call version cannot discharge B. Specify what occurrence counts as T; a name suggesting completion is insufficient. |
| What can be reused? | CFG order, compiled `precedence`, element and request identities, conditions, and ordinary return identity. |
| How does the program check it? | Propagate finite seen-A or seen-T state for supported matching units. At B, require an appropriate earlier A; after T, reject E. Cover every allowed arrangement of a partial order. `may_before` is not guaranteed precedence. |
| How can a reduction preserve it? | Preserve event occurrence, termination conditions, matching identity, and branch selection. An unchanged operation sequence alone does not show that the same events will occur. |
| What prevents a conclusion? | Unknown pairing, termination or reset; order expressed only in natural language; unsupported matching state; or a partial order that cannot establish the required precedence. One satisfying arrangement is insufficient. |

The first form means an appropriate prior occurrence exists; it does not
silently add one-to-one consumption, freshness, or an unbounded queue. If the
source requires those stronger properties, the available call/element matching
must express them or the remainder stays unsupported. Mere seen-A state is not
enough for arbitrary cross-occurrence matching.

These are safety relationships among occurrences. They do not require B or T
to happen or prove termination. A required action remains an independent
positive demand even when an ordering constraint is vacuously satisfied.

## 4. Minimal semantic addition and reuse boundary

### 4.1 Model-owned meaning, program-owned resolution

The immutable source-only Task remains unchanged. In fixed-Task annotation,
the realization correspondence layer has an optional `constraints` list,
omitted when empty. Each expression supplies only its family-specific meaning:

| Family | Semantic parameters that cannot be inferred from ordinary data flow |
|---|---|
| Information prohibition | Existing value and information range; forbidden original-content relationship; receiver and applicable operation scope. |
| Execution condition | Event selection; existing condition expression; evaluation/version relationship and applicable element scope. |
| Occurrence bound | Counted event unit; bound; task/per-element reset scope; a success predicate only when success is the counted unit. |
| Ordering | One of the two ordering forms; event selection, matching unit, and reset scope. |

This table is a responsibility inventory, not a general policy language. The
five discriminated variants are `forbid_information`, `only_if`, `at_most`,
`requires_prior`, and `forbid_after`; their exact fields are recorded in the
[implementation reference](constraint-implementation.md#declarations-and-references).
There is no catch-all object with every parameter optional.

The enclosing realization already identifies its requirement. Do not copy the
Task text, evidence, or source identity into each resolved constraint. Reuse
existing references and lexical scope; program-owned compilation supplies
operation coordinates, observation positions, Data candidates, and expanded
applicable operation sets. Direct instruction references and existing raw
`OperationTarget` references name declared actions, including response-receive
operations. References inside compiled realizations still address the raw
annotation; the mapping resolves generated observations. The model does not
predict compiled coordinates or introduce a second operation-ID system.

The model does not provide `safe_to_remove`, `constraint_satisfied`, proof
status, or affected-sink lists. It supplies semantic claims for the existing
reviewer to check; the program supplies the check and preservation results.

### 4.2 Reuse and required work

| Component | Reuse | Required semantic work |
|---|---|---|
| Task and evidence | Requirements, physical source spans, immutable task identity. | None in source-only Task; no new model call. |
| Positive demands | `value`, `presence`, `cardinality`, `shape`, `truth`, `action`; seed derivations. | Keep them positive. Do not restore `prohibit` as a demand property. |
| References and values | CFG references, `ValueRef`, paths, versions, existing element/request scope. | Resolve the restricted constraint parameters and validate full applicability. |
| Expressions | Existing supported AST and control target locations. | Interpret edge enabling and evaluation identity for checks, not just backward operand retention. |
| Data and operation records | Content relations, inputs/outputs, writes, reads, conditions, compiler order and mappings. | Establish sufficiency for each check. Add facts only after a concrete missing fact is demonstrated. |
| Locations and sinks | Receiver identity, visibility/retention and existing sink inclusion. | Check internal operations when required without promoting them to DOE sinks. |
| Realizations and gaps | One correspondence per Task requirement and explicit unsupported remainder. | Account for both positive demands and supported constraints. A pure prohibition must not need a fabricated positive seed; mixed requirements must cover both parts. |
| Result provenance | Existing operation references and shared derivations. | Store program-produced checks, candidate preservation rows, and shared change steps; refer to existing source, Task, Data and raw declarations without copying full runs. |

The implementation supplies constraint correspondence validation and mapping,
supported static checks, and preservation rules inside the existing analysis.
Structural validation cannot prove that a model-authored selector covers the
whole natural-language requirement: that remains a semantic-review obligation.
The checker does not turn merged propagation records into an execution trace
or create an independent reduce-and-run workflow.

### 4.3 Current implementation anchor points

The following modules implement the bounded responsibilities:

- [Constraint declarations](../../src/skillflow/propagation/contracts/constraints.py)
  and [realization validation](../../src/skillflow/propagation/contracts/realizations.py)
  allow a pure constraint without a positive seed and reject invalid raw references.
- [Demand expressions](../../src/skillflow/propagation/contracts/demand.py) and
  [target resolution](../../src/skillflow/propagation/contracts/demand_index.py)
  provide syntax and control locations; [Boolean interpretation](../../src/skillflow/doe/constraint_control.py)
  gives the supported fragment its checking semantics.
- [Demand analysis](../../src/skillflow/doe/demand_engine.py) retains unexpressed
  requirements and remaining realization gaps as global limitations.
- [Constraint checking](../../src/skillflow/doe/constraint_engine.py) uses actual
  task entry, neutral original-content ranges and finite temporal monitors.
- [Candidate preservation](../../src/skillflow/doe/constraint_preservation.py)
  follows possible change from the exact boundary slot and reuses the same gate
  during result validation.
- [Sensitivity comparison](../../src/skillflow/doe/sensitivity_engine.py) and
  [reduction results](../../src/skillflow/doe/sensitivity_results.py) currently
  constrain field-removal eligibility. Constraint checks do not broaden it.
- [Request pairing](../../src/skillflow/propagation/contracts/uses.py),
  [local order queries](../../src/skillflow/doe/material.py), and the
  [propagation solver](../../src/skillflow/propagation/solver.py) offer reusable
  facts, with the occurrence, may-order, and entry boundaries described above.

## 5. Preservation inside the same analysis

For a concrete eligible reduction r and each Task constraint c, the analysis
must establish a supported preservation judgment or retain its blocker.
Content-subset and independence arguments define the implementation boundary.
An independent structural guarantee is a separate stored rule:

| Rule | Required premises | Consequence |
|---|---|---|
| Content-subset monotonicity | The change removes only a named payload field; receiver, occurrence, other slots, conditions and demanded structure are preserved. A complete downstream account shows no new or enlarged prohibited occurrence. | The changed delivery's prohibited content cannot increase; baseline violations elsewhere remain. |
| No influence | A complete dependency and behavioral account proves the change cannot affect the constraint's content, conditions, event occurrence/count, matching, reset, or termination. | The constraint's relevant behavior and its baseline check remain unchanged. |
| Structural guarantee | A supported temporal constraint also passes a complete check with value guards abstracted away; event identity and task scope stay fixed. No changed collection can create or alter member occurrences. | The guarantee holds independently of the candidate's affected values. The baseline-only satisfaction flag is insufficient. |

The comparison is per candidate, not a global instruction to clear a gap. A
model binding, distant IR, different Data ID, or absence from a shallow slice
does not prove these premises. Unsupported effects remain conservative.

The influence account must include applicable value and `possible`
dependencies, public results, location reads/writes, control inputs, selection,
request/response relations, and event matching. Opaque operations retain
potential influence. Source or parent links explain origin; they do not become
new retrieval channels. A `possible` dependency matters for behavior while
still not proving plaintext content.

In particular, removing a request field can change the response, then a retry
guard, then the number or destination of later deliveries. Removing a model
input can change computation needed downstream. Saving less can change a later
read. A delivery is terminal for this rule only if the supported model provides
a complete basis for excluding such downstream influence; lack of a response
record by itself is not that basis.

The analysis preserves demanded field values, presence, shape, cardinality,
truth and actions. A field needed to evaluate a model-side condition must still
reach that model entrance. A local-only condition does not become a demand on
an external receiver. Information inspected by the checker to detect a
prohibition never becomes a positive demand that the receiver obtain it.

These are proof obligations for supported rules, not a request to run a changed
Skill, a second semantic model, or a separate optimization search. Where the
model cannot establish them, retain the limitation rather than claiming the
reduction is safe.

## 6. Analysis and reporting integration

```text
Sealed source-only Task
    -> fixed-Task annotation
       (positive demands + supported constraints + processing and sensitivity)
    -> existing semantic review and bounded semantic repair
    -> deterministic analysis
       (forward facts + backward demands + constraint checks + preservation rules)
    -> per-sink DOE comparison, with separate baseline constraint findings
```

There is no additional model role or call. The existing review checks the
requirement-to-constraint translation and applicable scope in the same
`declaration_checks` axis as positive demand declarations. Source, requirement
and IR coverage remain separate axes. Review acceptance is not deterministic
enforcement or proof of semantic completeness.

For each candidate, retain the ordinary positive-demand checks, check every
applicable preservation obligation, keep baseline violations visible, and
retain any gap lacking a proved non-influence boundary. Global blocking remains
the default for unsupported requirements. Release only the specific
constraint/candidate blocker for which a sufficient rule has been established;
other limitations remain active.

| Baseline constraint check | Candidate preservation | Reporting consequence |
|---|---|---|
| Model-relative nonviolation | Established | Candidate may proceed through all remaining DOE prerequisites. |
| Potential or supported static violation | Established without worsening | Keep the violation; an otherwise eligible independent reduction may proceed. Do not claim whole-task compliance or that all forbidden content has been removed. |
| Not established because a check is unsupported | Established by an independently complete no-influence account | Keep the unsupported baseline result; release only this candidate's corresponding blocker. An unknown influence scope cannot use this row. |
| Any baseline result | Not established | Retain the candidate blocker; missing proof is not permission to delete. |
| Task requirements conflict | No proof of joint preservation | Preserve the conflict and block affected reductions. Do not satisfy one requirement by silently discarding another. |

A constraint violation is not a substitute for DOE. DOE still needs declared
sensitivity, the actual exposure relationship, and supported task preservation
at that recipient and version. Conversely, absence of a sensitivity declaration
does not suppress an independently checkable prohibition. Existing DOE
conclusion kinds and boundary levels do not change in this design round.

Result explanations should reference shared facts and derivations: the original
requirement, compiled applicable scope, baseline witness or limitation, and the
rule for this particular reduction. Do not duplicate complete Task, source,
Data, or observation material. The shared result has separate `checks`,
`preservation`, and `influence` maps; the
[implementation reference](constraint-implementation.md) records their exact
ownership and version changes.

## 7. Acceptance and current capability boundary

The [independent synthetic matrix](constraint-acceptance.md) covers each family's
meaning, scope, baseline check, preservation premises, and unsupported boundary.
It includes baseline violation with an unrelated reduction and negative cases
where request deletion changes later behavior. Its 44 identities have executable
baseline counterparts. These bounded fixtures are not a corpus evaluation or
independent expert ground truth; some exercise only one component of a compound
semantic expectation. Preservation coverage is recorded separately.

Current limits include nested member quantification, task-wide ordering across
member occurrences, request pairing across repeated CFG invocations, changed
collection membership, unsupported success/condition expressions, and incomplete
facts or resource exhaustion. A syntactically valid declaration can still have
an unsupported check. In particular, no current member instances does not prove
that a candidate changing their collection cannot create future occurrences.

Unsupported source meaning remains a realization gap; unsupported deterministic
checking remains a visible baseline result. A candidate proceeds only when its
own complete preservation argument and all ordinary DOE prerequisites succeed.
Neither baseline satisfaction, a review pass, nor an offline regression run
establishes unrestricted source semantics or globally minimal exposure.
