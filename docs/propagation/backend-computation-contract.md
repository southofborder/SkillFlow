# Backend computation and projected records

This is an internal deterministic-backend contract. It adds no model fields,
semantic requests, or user options.

## Accepted inputs and internal computation

External CFG, annotation, and initial Data are checked at the computation
boundary. Typed operation specifications are reused. Internal registry updates
check the identities, origins, and references required by that update; unchanged
typed values and duplicate loop candidates do not publish changes. `true`, `1`,
and `1.0` remain distinct values.

The strict registry and record validators remain available for external imports
and explicit offline verification. They are not repeated on each computed
registration or record publication. Operation-specific requirements still apply:
for example, a known scalar or object cannot be the collection operand of
`filter_items`. An unknown collection does not need a known size.

## Dependencies and relation rows

A work item is a basic-block correlation partition. It records actual Data and
field reads, including missing fields and recursively accessed descriptions.
Only committed changes wake readers. A partition replaces its current records,
diagnostics, and outgoing contribution when recomputed. Missing inputs retain
their dependencies. Static member metadata is prepared before solving.

Incoming states are relation rows, not independent unions of each location.
Projection removes locations that are not needed by subsequent computation or
evidence. Equal projected rows can be deduplicated; distinct member, candidate,
receiver, and version associations remain distinct. Candidate construction joins
compatible bindings before counting complete candidates against the existing
limit.

When an edge entering an SCC loses rows, that SCC's current work items and edge
contributions are rebuilt from the remaining external inputs. This includes
internal withdrawals: an old backedge cannot support a withdrawn row on its own.
Pure row growth and the component's own clearing do not reschedule that rebuild.
Previously recorded Data and loop-family
may-facts remain available; this is not arbitrary precise fact retraction.

## Published evidence

`skillflow-propagation-record-v16` entry and exit states are projections of
locations needed for computation and evidence. They are not full environment
snapshots. Public operands, outputs, actual operations, alternatives, member
relations, endpoints, and write evidence remain available to downstream DOE.
Omission of a location is not evidence of deletion, empty content, unreachability,
or safety. Actual writes and removals use explicit operation evidence.

Current propagation runs use identity `skill-ir-propagation-v21`, format 21.
Coherent saved v20 runs with v15 records remain readable with their old full-state
meaning. They are not rewritten or replayed through the new version.

The dependency and liveness calculations do not use Task necessity to discard
data. A necessary action can still expose unnecessary sensitive content. A
completed fixed point does not prove source-model completeness or absence of DOE.

## Measurement terms

`partition_evaluations` and the current `block_evaluations` count partition
attempts; the latter is retained for compatibility with existing statistics.
They are not one-to-one comparisons with old whole-block attempts. IR evaluation
counts provide a separate common measurement. Maximum relation rows, compatible
candidates, registry changes, and validator counts describe different work and
must not be added as if they were durations. Nested intervals are not additive.

The frozen GA4 comparison uses an independent copied input and direct backend
calls. It neither resumes the paused online controller nor updates its results.

## Downstream material ownership

Public `PropagationMaterials` getters continue to return detached copies. A DOE
index takes one such CFG, Data, and records snapshot for its own lifetime, then
reuses it for operand, state-binding, demand, sensitivity, and constraint queries.
It does not repeatedly call a whole-record getter inside each operand lookup.
Query results and published coverage remain detached from those internal indexes.
Task-review preparation similarly uses one local CFG snapshot for all bindings.
There is no persistent cache or shared mutable index across analysis instances.

The full fixed-GA4 timing receipts cover frozen r2. The later r3 material-reuse
fix has focused regression and small-query measurements only; it has not received
another full-GA4 computation within this authorization.
