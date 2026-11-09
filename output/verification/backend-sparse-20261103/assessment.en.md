# Offline backend simplification assessment — 2026-11-03

The backend changes are implemented and the scoped offline regressions pass. The measured new backend returned propagation in **1,052.546 seconds**, with **326/347 generated IR processed (93.95%), 2 unmodeled and 19 blocked**. It did **not** produce a completed DOE result within the single 30-minute full-pipeline allowance. The old backend timed out during propagation; the measured new r2 backend timed out during DOE. A stack sample identified repeated whole-record copying during DOE initialization at the sampled moment. Therefore neither complete GA4 coverage nor a useful completed GA4 DOE conclusion is established by this experiment.

After that timeout, a remaining repeated-record-copy path in DOE was removed in r3 and tested separately. **r3 has not been run again on full GA4.** The two full-computation allowances are exhausted. All results here are offline derivatives; the paused online v9 run remains paused and is not reclassified as complete.

## Implementation delivered

- Internal registry computation reuses accepted objects. Unchanged typed registrations and duplicate family candidates do not change versions or wake consumers. Whole-registry validation is absent from the repeated-registration hot path. Required local input, identity, collection-operand and member compatibility checks remain.
- Work items are basic-block correlation partitions. Actual Data/field reads, including negative and recursive reads, register consumers. Only changed dependencies and changed incoming rows schedule work. A recomputation replaces current diagnostics, records and outgoing contributions. SCC withdrawals rederive current rows from surviving external inputs, including withdrawals inside the component; pure growth does not trigger this rebuild.
- Backward liveness projects working states using computation and evidence needs, never Task necessity. Public operands, outputs, boundary evidence and historical deliveries remain recorded. Definite overwrite can kill an old live location; possible updates retain it.
- Joins preserve complete relation rows and member/candidate bindings. Inputs are joined incrementally by compatibility rather than building all incompatible tuples first. The existing finite family/collection representation and resource bounds remain in use.
- Record v16 / propagation v21 describe projected snapshots. Omitted locations do not mean deletion or safety. Coherent old v15/v20 artifacts remain readable without migration.
- Post-cap r3 gives each DOE index one detached CFG/Data/records view and indexes state bindings and operand references. Internal consumers reuse it; public getters and published results retain isolation. Task-review binding projection uses one local CFG snapshot. No persistent cache, new model field, prompt or model stage was added.

The engineering approach uses dependency-driven dataflow, liveness and relational partitioning. It does not import a new language executor or claim IFDS complexity guarantees for these multi-input, stateful transfer functions. See the [design](../../../docs/doe/backend-sparse-design.zh.md) and [English computation contract](../../../docs/propagation/backend-computation-contract.md).

## Fixed input and revision identity

The independent fixed input contains 177 blocks, 347 IR, 345 modeled IR and two source-unmodeled IR. Its SHA-256 is `9c75db1428450c1bb5593b75b40b17d6c9e3d47d1efbcaca793f2fc026a960a4`. It derives from the selected v9 materials for the same frozen 16-file source package, source SHA `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. No historical target answers were regenerated or changed.

| Revision | Python-source manifest SHA-256 | Measurement scope |
|---|---|---|
| Frozen old backend | `db43f649967f34f2a88fa6547fd045de7eaff3edbc52de3a32e31c9b19993d04` | One capped full computation and small fixtures |
| New measured r2 | `c263e0b0954d7d2b7c1190709fa493b0906605a30e5f9eb64ccb3571477d7602` | One capped full computation and small fixtures |
| Delivered r3 | `5ccbc1941be908ff20b15d7a56a631e678285b42a255031d29505ec6a0495637` | Focused regression and operand-query micro only |

The old donor's broader implementation identity is `e5c8d5ffce9f94b02f103b284a2b366c32d9bd386727bfad8b78d6df79842154`; it is a different manifest scope from the Python-source digest above. r3 differs from r2 in exactly seven DOE files. All propagation files are byte-identical between r2 and r3. The final [source manifest](implementation-final-r3/manifest.json) and [input provenance check](final-provenance-check.json) retain the exact files and hashes.

## Full GA4 bounded comparison

Both versions ran serially on this machine, using the same fixed input and benchmark harness. Each parent enforced 1,800 seconds including preparation, propagation, DOE and saving. It stopped only its own benchmark child at the cap. No controller, historical replay, Skill execution or model call was started.

| Metric | Frozen old | New measured r2 |
|---|---:|---:|
| Parent wall time at timeout | 1,800.110682 s | 1,800.066149 s |
| Child CPU time | 1,791.453125 s | 1,789.640625 s |
| Sampled peak private memory | 552,902,656 bytes (527.29 MiB) | 319,455,232 bytes (304.66 MiB) |
| Stage at timeout | Propagation | DOE |
| Propagation | Not returned; last retained active interval 1,796.069833 s | Returned in 1,052.546024 s; status `incomplete` |
| Generated-IR final coverage | Unavailable | 326 processed / 2 unmodeled / 19 blocked |
| DOE | Not reached | Not returned; last retained active interval 740.063800 s |
| Completed full output save | No | No |
| Whole registry validation during propagation | 12,546 calls, 8,836,479 cumulative rows | 0 calls |
| IR evaluations observed | 15,841, visiting 320 distinct IR | 79,334, visiting 326 distinct IR |

The old 320 visited identities are instrumentation entries, **not completed coverage**. Nested validator counters are not added together. New lightweight reference checks remain separate from whole validation. Peak-memory observations and work counts cover different reached scopes; they do not establish a complete-pipeline memory reduction or speedup. Both full pipelines timed out, so no complete end-to-end acceleration ratio is reported.

The measured new propagation performed 2,842 partition evaluations, 428 dependency wakeups, 2,414 edge wakeups, 383,127 compatible candidate evaluations and 1,062 registry-key changes. It retained 959 Data identities, including 352 families and 421 family relation facts. Maximum active relation rows were 7,650; maximum rows in one partition were 107. `block_115` reached 1,486 rows and `block_125` 1,485; `block_116/118/119/122` reached 716 each. The remaining work is concentrated in the reindex loop's still-distinct live relations, not repeated whole-registry validation. These counts do not prove every retained relation is semantically necessary, or that full-GA4 relation cardinality fell relative to the unfinished old run.

Receipts: [bounded comparison](bounded-comparison-summary.json), [old parent](performance/baseline/parent-result.json), [new parent](performance/current/parent-result.json). The harness saves complete propagation/DOE JSON only after DOE returns; therefore the retained new evidence is returned coverage/statistics/diagnostics in progress receipts, not a complete published propagation record or DOE file.

## Why coverage is still incomplete

The two original unmodeled items were preserved:

1. `ir_029`, the analyst-selected analysis boundary, lacks the actual selected function instantiation and saved-result relationship. It blocks `ir_030–047`: the downstream result-selection, saved-JSON reading and Markdown-summary route. High generated-IR coverage therefore does not mean the user-facing GA4 workflow is complete.
2. `ir_301`, `mkdirSync` on the missing-directory branch, remains unmodeled and blocks `ir_302`. The existing-directory path is separate; this does not mean every save operation is blocked.

The original annotation also has 36 processing gaps; 47 of 50 Task realizations carry gaps. The `ir_238` normal notification-helper case retains caller/state precision limitations. Backend optimization cannot repair those source-model choices. See [frozen-model limitations with source references](frozen-model-limitations.en.md) and [observed IR identities](observed-ir-coverage.json).

Two additional `missing_part` diagnostics at `ir_312` concern selecting `value` from completion candidates. The preceding model has a normal `{normal:true,value:...}` wrapper and two `{normal:false,error:...}` wrappers. This is structurally consistent with the two error candidates lacking `value`; it is not evidence that source JSON lacked a required business field. Exact Data-ID lineage cannot be confirmed without the unpublished complete records. These diagnostics are nonfatal and are distinct from the two unmodeled cutoffs.

No source-boundary percentage, GA4 DOE accuracy, absence of excess, or advantage over direct GPT is inferred. The prior 13 API / 25 save / 3 loop criteria were not converted into a new completed source-boundary audit from these summary counters.

## Completed small comparisons

Each timed variant has three serial repetitions. Medians apply only to the named timed operation; preparation, fact auditing and saving are excluded where the receipts specify that scope.

| Fixture / timed operation | Old median | New median | Narrow ratio / work change |
|---|---:|---:|---|
| 959 ordinary records, 1,486 duplicate registrations | 45.151000 s | 0.408714 s | 110.47×; whole validations 1,486 → 0 |
| Loop with an independent root, propagation | 0.478626 s | 0.101417 s | 4.72×; independent IR executions 3 → 1; total IR 55 → 32 |
| Nested receiver/payload pairs, propagation | 0.751787 s | 0.096451 s | 7.79×; total IR 66 → 21 |
| Post-cap 1,200 operand queries, r2 method vs r3 | 0.265700 s | 0.001891 s | records getter 1,200 → 0 after one constructor read |

The registration fixture reconstructs the observed scale; it is not a recovered snapshot of the paused process. It has no loop-family variants. Its source subset is separately pinned in [micro-summary](micro-summary.json). The two propagation fixtures use frozen old/r2 code and identical inputs; see [old results](small-propagation-v1-baseline.json) and [new results](small-propagation-v1-current.json).

Both versions retain the same Data in those fixtures. The nested case retains exactly `(A,a0)`, `(A,a1)`, `(B,b0)`, `(B,b1)` and all 13 IR. Its raw operation-facts hashes differ only because two complete alternatives in `ir_rows` changed enumeration order. Reversing only that list restores exact equality; normalizing complete alternative rows yields common hash `98615db84dbcbbb10e24a85c5e4b89553e1bab4efbbb3b538f7689d9fe1c3bfd`. Event order, operand-slot order and pairings are unchanged. Two separate hash-seed exports also preserve the raw r2 result for this fixture. See the [independent difference audit](nested-operation-facts-audit/assessment.md).

## DOE initialization omission and r3 correction

One nonblocking stack sample of the owned r2 benchmark child showed `copy.deepcopy → PropagationMaterials.records → DemandEngine._operand_data → _setup`. This identifies an actual repeated-copy path at that moment, not a complete runtime profile. Reading source confirmed that each operand lookup fetched another detached copy of the whole records object.

The delivered r3 changes the internal owner, not the public getter contract: one detached snapshot and local indexes are reused by the current DOE calculation. On the six-operand synthetic query fixture, each variant ran 1,200 queries three times; candidate hashes agree in all six measurements. r3 construction reads CFG/Data/records once each, with zero records-getter calls during those queries. See [query receipt](doe-r3-operand-query-micro.json) and [r3 acceptance](doe-r3-offline-checks.json).

This resolves the identified repeated-copy implementation path. It does **not** establish that full GA4 DOE now finishes, what its final latency is, or what conclusions it produces. No extra full run was used to replace the timeout receipt.

## Regression evidence and limits

The current scoped XML union contains **892 distinct cases whose latest recorded result is passed**, with zero unresolved failures. This is not one all-green whole-repository run. [Final receipt index](offline-test-receipts-final.json) retains each original run, its failures and its corrective reruns. Recorded earlier failures include projected-snapshot expectations, fixture prerequisites and provenance guards during concurrent edits. Functional corrections include the required local collection-operand check and internal-SCC withdrawal handling.

r3's affected union has 316 passing cases. Its initial 188-pass/60-fail run remains: 59 failures came from simplified test indexes lacking the new internal views, and one from a fixture swapping outer input slots without swapping its paired alternative slots. The latter also failed under frozen r2. Fixture corrections did not relax semantic assertions or alter historical input. The final 68-case run includes actual material-owner isolation, Task helper/persistence checks and both injected seven-call flows.

The suite covers missing/recursive dependency wakeups, updates during evaluation, independent branches, replace/append/delete, lost incoming rows and branch shrinkage, FIFO/LIFO results, duplicate occurrences, nested members, receiver/payload and credential-version pairing, `compute(x,x)`, local returns and positive/necessary-sensitive DOE fixtures. Actual GA4 regression input covers `block_115–125` and a standalone `ir_238` evaluation with explicit authored entry values; it does not reproduce the full paused memory state. No mixing was found in these covered fixtures. This is not a general correctness proof or an audited claim about every GA4 candidate.

## Cost and completion boundary

New analysis-model calls and model tokens: **0**. Skill executions and historical replays: **0**. The two capped full computations used approximately 3,600.177 seconds of parent wall time in total and 3,581.094 seconds of child CPU time; the small measurements and scoped tests have separate receipts. No monetary cost, hidden reasoning usage or full-engineering-effort total is inferred.

The implementation, regression evidence and offline report are delivered. The remaining empirical questions are full-GA4 r3 DOE completion and the original source-model gaps. The old controllers, queue and automation stay paused. Further real runs or another full fixed-input computation require a subsequent decision; none was silently added here.
