# Provisional partial-processing audit of the fresh GA4 run

Run: `document-guided-ga4-cfg-recovery-high-20261117-135205`. This note inspects saved bytes from the accepted initial 489-IR CFG and the initial processing stage after its one correction. It does not execute validation, compilation, propagation, DOE, a Skill, a model call or replay. Production and run files remain frozen. `partial-processing-audit.json` records artifact hashes, exact inventories and selected evidence; `audit_partial_processing.py` uses only the Python standard library. These are provisional materials before source review, not final selected-analysis results.

## What was retained and what was isolated

The processing result has status `partial`, `accepted_call: null`, two logical responses, one stage request and one structural correction. The first response was rejected at `/shared_values/v601/evidences/1` because a marker object also contained another member. Its supplemental raw scanner reported that same definite format issue. The correction has a saved expanded candidate and reaches ordinary structural validation; this does not retroactively accept the first raw response.

| Saved inventory | Count / identity |
|---|---|
| Initial accepted CFG | 489 IR |
| Corrected candidate semantics | 486 IR |
| Retained independent records | 484 IR |
| Retained records with operation segments | 272 |
| Retained records without segments | 212, mostly structural/evidence records; not 212 demonstrated failures |
| Source-declared unmodeled IR | 3: `ir_140`, `ir_289`, `ir_295` |
| Additional source gap records | 13, not marked `unmodeled` |
| Validation-isolated IR | 2: `ir_001`, `ir_346` |
| Retained locations / atomic operations | 67 / 606 |

The corrected response's top-level validation stops at the two `ir_001` errors. The saved partial result additionally records the independent-record isolation error at `ir_346`; it must not be omitted from the account of this stage. The retained value has neither of these records. It preserves the 16 original source-gap records, including one explanatory source gap for `ir_346`, while the step result separately preserves the two validation gaps. These counts are therefore not all disjoint lists of IR.

`ir_140` explicitly declines a dense append substitute for JavaScript `Array.map`, whose holes, original indices and length matter to normalization and the bulk empty-input condition. `ir_289` and `ir_295` explicitly decline substituting JSON `null` for the source's missing optional mobile/rich-results `undefined`. The gap records identify actual semantic distinctions and source spans; they do not invent replacement values.

## Scope of the two validation quarantines

`ir_001` acquires the imported `dotenv.config` interface, sourced at `scripts/src/config/settings.ts:5`. Its candidate processing record is a local segment containing a `read`. Saved validation reports both “transform event lacks a data transformation” and “atomic operation/effect mismatch: read/transform” at `/ir_semantics/ir_001/segments/0/ops/0`. The record is removed, not replaced with empty operations. Its gap has `outputs: []`, `locations: []`, `control: false` and `unmodeled: true`: those empty subranges must not be described as a positive proof of no effect.

The initial CFG's sole direct operand consumer of `result_001` is `ir_005` (`initialize_environment`), alongside pre-environment, working directory and the dotenv file resource. This places the defect on module initialization and potentially on later environment-dependent configuration. It does **not** establish that every independent public entry is blocked. The retained `ir_005` also summarizes `config()` as a zero-explicit-argument local tool call with ambient environment/file reads; how that summary and module initialization interact with dependency propagation has not been executed or measured here. No whole-report invalidation or unaffected-output guarantee follows from the record count.

`ir_346` models the `checkIndexStatus` loop body at `scripts/src/index.ts:329–339`. In its successful case, operation 9 declares the local `verdict` as its sole compute input, but its expression refers to `{"kind":"input","index":0}` instead. That denotes an IR input rather than the declared local operand; the saved error says the expression introduces undeclared operation inputs. The actual source tests `result.indexStatus.verdict === 'PASS'` at line 334. The whole `ir_346` record is isolated, including all four authored cases: inspected, before-inspection, inspection-rejection and after-response. Its completion feeds dispatch `ir_347`, success accumulator `ir_348` and exception extraction `ir_350`, so loop outcome and subsequent aggregate/save obligations are concrete concerns. Actual downstream blocking and range counts await the backend; this audit does not infer them.

## Seven remote sites compressed in the CFG are made more explicit in processing

The four realtime records (`ir_202/209/216/223`) and three metadata records (`ir_230/239/248`) are retained. Each now contains a source-backed call to local `getClient`, a separate local `getPropertyId`, construction of the actual request, the remote call and first-tuple-element selection. Realtime requests retain property plus the appropriate fixed dimensions/metrics; metadata constructs the `/metadata` name. These are operations evidenced by `realtime.ts:24–99`, `metadata.ts:38–95` and `core/client.ts:23–53`, not fabricated new CFG input operands. The previously noted lack of explicit CFG operands is therefore partly addressed inside these operations.

Two limits remain visible in the saved representation:

1. Each `getGa` call produces a local `handle`, but none of these seven remote operations consumes or otherwise binds that handle. Remote locations are static named records. The source calls the method on the returned client. Explicit receiver/authentication identity is thus not established by the inspected operation links. Even ordinary report `ir_099` supplies only its request to the remote call, despite an explicit client operand in the CFG. No contract should turn this source receiver dependency into an allegedly unnecessary input merely because the generated operation omits it.
2. `getGa` and `property` are modeled as no-explicit-argument tools. Their location declarations provide source references, not links to the separately modeled getter/cache/settings bodies. The source-backed current-property request is visible, but field-level demand back into ambient settings and cached client creation is not demonstrated by this inventory. Source review must assess those relationships before any necessity or deletion claim.

All 13 direct remote sites, 25 save callers and seven physical filesystem sites matched by the initial source audit still have their corresponding IR record in the partial value. This is **record presence only**. It does not certify every call summary, actual propagation reach, receiver pairing, acquisition-side trimming or a field-level deletion conclusion.

## Contract coverage and source-fidelity findings to carry into review

The retained value contains 107 computes. One (`ir_010`) has a structured equality expression and needs no opaque transfer contract. The other 106 carry 106 `demand_transfer` contracts, with 142 input rows. All 141 calls and 63 deliveries carry `input_contract`, totaling 204 contracts and 223 input rows. These are syntactic counts, not the eventual source-review obligation/scope inventory.

Every one of the 106 opaque transfer contracts has exactly one output selector, `{"property":"value"}`, and no contract-level gap rows. They often name precise **input** fields, but supply no distinct **output-subfield** rule. This matters for composite outputs such as settings construction `ir_016` (credential/property/results-directory fields) and inspection mapping `ir_285` (link and multiple status fields). A whole-output rule cannot itself establish a precise dependency for just one demanded child field. Whether the task needs those narrower outputs, and whether source review supplies a correction or a justified local gap, remains open. Structural retention alone is not evidence that field-selective demand is complete.

There is also a positive source-fidelity detail relevant to the user's requirement: `ir_089` explicitly selects `filters` and `orderBy` into `unusedFilters`/`unusedOrder`, retaining the source's reads even though the request omits these options. The report interface contract likewise records that ordinary reports send neither. This preserves actual observation separately from later task necessity; it is not yet a deletion decision.

Other source gaps preserve meaningful limitations: sparse array positions, actual rejected exceptions, optional undefined fields, pre-request logging/cache effects, autosave exceptions, repeated filename replacement, the clicks/impressions documentation conflict and the absent invocation-to-saved-file/Markdown-summary implementation. This audit has not endorsed every reason. The concrete references and preserved actual behavior should be assessed in the scheduled source review without filling missing semantics with guessed inputs, receiver bindings or summary writes.

No accepted source-review scopes, task-conditioned input assessments, propagated boundary coverage, deletable field counts or DOE result are established by this provisional note. It ends at this saved partial-processing snapshot; the controller remains root-owned.
