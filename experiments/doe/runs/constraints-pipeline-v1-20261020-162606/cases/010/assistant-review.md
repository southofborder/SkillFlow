# Case 010: assistant semantic and deterministic-result review

**The selected candidate preserves the actual search parameters, optional request shapes, response acquisition, saved total, and returned items. Two restrictions receive supported structural checks. The run still contains demand-placement and redundant expected-source concerns that the model review did not report. DOE is partial, with no sensitivity declarations or eligible reductions; this is not a safety result.**

This assessment uses the current run's frozen source and actual accepted artifacts. It does not edit the Task, annotation, review, propagation facts, or DOE result. It makes no additional model call and is not an independent human-expert gold standard.

## Selected material and execution

[Pipeline result](result.json) records:

- Initial annotation response a001 was structurally invalid.
- Structural correction a002 was accepted and remains the selected original annotation.
- [Initial semantic review](refinement/initial-review/result.json) returned no findings; no semantic repair or re-review was requested.
- Propagation completed with 12 sinks.
- DOE is `partial`; the pipeline is `diagnostic`.
- Four logical requests and four HTTP attempts: Task extraction, annotation, one structural correction, and initial review. There was no HTTP retry or JSON normalization.

The raw a001-to-a002 response difference is limited to adding the two build-output presence demands for R4/R6. [The earlier audit](../../verification/010-initial-annotation-audit.assistant.md) records that distinction. The authoritative selected candidate is [raw-annotation.json](annotation/audit/raw-annotation.json), with [compiled-response.json](annotation/audit/compiled-response.json) and [compilation-map.json](annotation/audit/compilation-map.json).

## Source obligations and actual behavior

[The frozen workflow](inputs/package/references/workflow.md), [missing-argument configuration](inputs/package/query.yaml), and [new Task](task/task.json) retain the relevant obligations. I found no concrete omitted source obligation in the nine-requirement Task.

| Obligation | Actual selected representation and evidence |
|---|---|
| Read the supplied request | R1 has a read action demand. There is no source-wide content demand merely because the entire request is acquired. Whole-source observations remain in the actual propagation facts. |
| One search, original query | R2 has an actual delivery action and input-slot-0 `value` demand at path `["query"]`, with the original term relationship. It also declares an at-most-one attempt restriction. |
| Optional original values | R3/R5 have actual delivery input-slot-0 `value` demands at `["from_date"]` and `["limit"]`. Explicit field selections preserve their source identities. |
| Omit missing optional values | The build has separate `when` references to presence flags. a002 adds R4/R6 presence demands at the build output. Their boundary-attribution limitation is discussed below. |
| Never invoke deletion | R7 remains a source-backed `retained_only` gap. No deletion operation is fabricated and no positive demand is created for it. |
| Save the response total after search | R8 has both the write action and its actual payload-value demand, plus a search-before-write restriction. |
| Return original items | R9 is seeded at the real return input, and the response's `items` field is explicitly selected. No fake user-output sink or public return output is introduced. |

[Propagation records](propagation/records.json), at `ir_007`, contain a build followed by a tool delivery and its paired acquisition. Delivery and acquisition use the **same ordered request candidate set**. [Data](propagation/data.json) contains four request shapes:

1. `query`;
2. `query, from_date`;
3. `query, limit`;
4. `query, from_date, limit`.

These are abstract alternatives, not four executed searches. All four preserve the same original query value and the respective original optional values. Presence flags are control slots, not members of those request objects. The compiled conditional observations also distinguish their payload and controlling input.

The response candidates have acquisition origin `tool:index.search`; they are not represented as computed copies of the request. Each saved payload is a `total` part of its corresponding response candidate. The response `items` selections remain separate. [Sink records](propagation/sinks.json) classify the search as `external_tool`, level 2, without inventing network communication.

## Demand derivations: established and remaining

The complete support is in [demand-support.json](doe/audit/demand-support.json), including `traceability`, `extra_derivations`, and per-sink comparisons.

The search receiver is `sink_f5e30d631911b0c8db08`, operation `op_ir_007:e4:a0`. Actual precise content demands reach its input slot 0:

| Requirement | Path | Derivation | Seed |
|---|---|---|---|
| R2 | `["query"]` | `demand_b8c556f810395df679cc` | `goal_b9704dcab72933209f08` |
| R3 | `["from_date"]` | `demand_590b42ebda7587a7fd51` | `goal_c25263b0b7055126cef1` |
| R5 | `["limit"]` | `demand_d33e6a25921fbd47190c` | `goal_99915fbe3f62e1af0426` |

Thus parameter-content preservation is present at the receiver; it is not being inferred solely from upstream construction. R8's write-input demand also exists independently of its write action.

Two limitations remain visible in the actual derivation:

**1. R4/R6 omission requirements are still attached upstream.** Their roots are:

- R4: `demand_85e7a4931aa93fb6b1e6`, build output `op_ir_007:e3:a0`, presence of `from_date`.
- R6: `demand_c73b1e4863ac33e110b4`, the same build output, presence of `limit`.

They correctly propagate backward to the respective build controls through `member_presence`. They do not propagate forward to the search receiver. R4/R6 are absent from that sink's `related_requirements` and demanded-information list. The model review accepted these declarations based on the existing conditional build and did not discuss the missing receiver-level attribution.

This does **not** mean the actual request incorrectly includes absent fields: the four propagated request shapes preserve omission, and R3/R5 receiver-value demands also retain the relevant controls. The concrete remaining issue is that the independently stated omission obligations are not explicitly connected to their receiving boundary in the per-requirement demand trace. The combined conservative demand set must not be presented as a precise repair of that attribution.

**2. Optional original-value declarations retain independent expected-source demands.** These are present in the saved derivation, not merely a hypothetical concern:

- R3: `demand_f0f265b2497e30deb0da`, `ir_007` input 2.
- R5: `demand_fb3898ec36137409560d`, `ir_007` input 4.

Both include `required_original_value` in their rules, independently emitted by `expected`; the build's condition is handled on a different reverse edge. The current shared Prompt explicitly warns that redundant expected-source demands do not inherit `build.when`. The model review nevertheless accepted the declarations by describing conditional member consumption, without addressing this independent source retention.

The current source is abstract, both optional values have possible candidates, and the recorded analysis has no `expected_relation_mismatch` diagnostic. Consequently, this run establishes redundant unconditioned provenance in the demand graph, but does not demonstrate a concrete missing-value execution failure. It should not be described as complete validation of absence behavior under every input.

R8/R9 additionally produce conservative whole-request retention through `external_request_retained`. Those derivations are explicitly conservative and arise from preserving returned information across an unspecified tool interface. They are not extra source-stated parameter requirements or evidence that every request field is indispensable.

## Forward restrictions

[DOE result](doe/doe-result.json), under `constraints.checks`, has two entries:

| Constraint | Requirement | Result | Assessment |
|---|---|---|---|
| `constraint_9009e15876bcfc82d8ad` (`at_most`) | R2 | `satisfied`, `structural=true` | Consistent with the actual task-entry CFG: one acyclic chain and one `index.search` instruction containing one delivery/acquisition pair. Compiler observations and the receive operation are not additional invocation attempts. The positive action demand separately states the required occurrence. |
| `constraint_35e3a6a8eec50bad5a08` (`requires_prior`) | R8 | `satisfied`, `structural=true` | The same acyclic task-entry chain reaches the search before the write. The raw and compiled order has no competing branch or loop. This supports the declared model's ordering restriction, not a claim that a real tool call succeeded. |

The result's operation lists include relevant compiler operations; their list lengths are not call counts. The four response/request alternatives are not counted as four attempts.

There are exactly **10 positive compiled demands** and **2 separately mapped constraints**. All 231 saved demand derivations refer to one of those 10 real positive goal IDs; no constraint ID appears as a positive seed and no constraint-generated demand rule appears. This supports the intended separation of forward restriction checks from backward Task demands for this case.

R7 is not among these supported constraints. Its retained prohibition produces two blocking demand diagnostics, both attributed to R7 in the support file:

- `requirement_expression_gap`;
- `unbound_requirement`.

The latter is a consequence of this unsupported retained requirement, not an invitation to create a positive deletion demand. The global limitation remains at every sink; absence of a modeled deletion event is not being advertised as a checked universal prohibition.

## Sensitivity and final DOE

The selected annotation contains **zero sensitivity declarations**. The result includes all **12 sinks**: ten model observations, one external tool delivery, and one storage write. Every `data_reviews` list is empty:

- `excess_supported`: 0 entries.
- `possible_excess`: 0 entries.
- `no_excess_established`: 0 entries.
- Supported reductions: 0.

These are empty classified-information results, not twelve safety findings. The source provides no basis to invent hidden credentials or sensitive fields in the unknown search-response remainder. Conversely, a missing sensitivity declaration does not prove that actual future request or response contents are nonsensitive.

`constraints.preservation` and `constraints.influence` are empty because no sensitivity-based reduction candidate was produced. This case therefore exercises the two baseline restriction checks and the no-seed separation, **not** successful local restriction-preservation proofs for an actual proposed reduction.

DOE and demand status remain `partial`, with R7's blocking diagnostics. Model-review acceptance, propagation completion, and two satisfied structural restrictions do not establish full Task compliance, globally minimal information, or absence of DOE.

## Overall assessment

The actual request/response identities and required content bindings are substantially represented, and the two new supported restrictions are checked without altering facts or creating demand seeds. The review missed the narrower issues around receiver-level omission attribution and independent optional expected-source retention. The result correctly retains its unsupported prohibition and avoids a global safety claim.

All conclusions above refer to the saved selected candidate and its existing analysis. No accepted artifact was patched, no quality rerun was started, and zero-API replay remains a separate engineering verification recorded at the run level.
