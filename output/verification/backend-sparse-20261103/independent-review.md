# Independent backend boundary review

Date: 2026-11-03. Reviewer: `/root/review_backend_simplification_proposal`.

Scope: the other agents' registry, dependency-read, record-publication and persisted-run loading changes. This review did not assess the reviewer's own solver implementation as independent work. No model call, Skill execution, suspended-process control, historical replay or full GA4 benchmark was performed. A small authored in-memory filter example and focused local tests were run. The root explicitly authorized the local interpreter correction described below after the finding was reported.

## Confirmed finding and correction

**P1: removing whole-registry validation also removed a required `filter_items` operand error.** The trusted registry update path checked identity, origin and reference existence but no longer rejected a `SubsetViewContent` whose base was a known scalar or object. That check had previously lived in `DataRegistry._validate_data_values`.

The initial in-memory reproduction used one `filter_items` operation with `literal(7)` and predicate `keep`. `propagate` returned `complete` with no diagnostics. Immediately calling `result.registry.validate()` failed with `DataConflictError: subset_view requires a collection, not a known object or scalar`. Thus computation could publish a result that the strict external reader would reject; this was not merely an accepted loss of precision.

The authorized correction adds `TransferInterpreter._require_collection_operand` and calls it before creating a filter result. It reads only the actual candidate and structural bases through tracked registry reads. Known scalar literals, object fields and object field updates are rejected. Opaque values and recursive unknown summaries remain allowed without requiring a known size or enumerated members. Ordinary and loop-family candidates are covered. No full-registry validation was restored.

Verification:

- `test_filter_operand_checks.py`, `test_filtered_empty_guard.py`, and `test_conditional_flow.py`: **46 passed in 1.99 seconds**.
- The same tiny scalar reproduction now returns `execution_error` with an `execution_error` diagnostic; its remaining registry passes explicit deep validation.
- New cases cover scalar/object rejection, open known-object bases and dependency reads, unknown ordinary/family inputs, and stable repeated literal-list filtering.

## Other reviewed boundaries

- Trusted ordinary commits use changed-entry checks and local reference validation. They do not call `_all_entries` or `_validate_records` for an unchanged ordinary registration. Public imports and public registry validation retain the strict audit path.
- `DataView` resolves queried descriptors lazily. Structural traversal uses its tracked `__getitem__`/`contains` operations; closed-part lookup uses the indexed `(root, typed path)` key, including a tracked negative lookup. Ordinary part bindings follow and observe the parent chain. Family scope/producer and content reads observe the relevant Data identity, allowing same-ID descriptor changes to wake consumers.
- Transaction rollback journals changed records, part-index entries, versions and change notifications. It also restores loop fact counts/revisions and normalizes observed speculative versions after rollback. This is local calculation ownership, not a persistent cache.
- Trusted record construction/publication uses `from_computation`, `put_computed`, computed snapshots and final reference checks. Strict imported records still undergo model and cross-reference checks. Explicit full `validate()` remains available; it is not silently called for every computed record.
- `materials_from_result` compares the result's normalized CFG, accepted annotation payload and seed snapshots against their owners before accepting computed components. The loader checks manifest/artifact identities and strictly restores imported records.
- The persisted version table accepts the intended v21/v16 and v20/v15 pairs and rejects mixed pairs. Historical v20 replay is explicitly rejected before recalculation or replay output. The compatibility test is an authored fixture, not evidence that a frozen historical run was replayed or migrated.
- Projected snapshots retain public operand/state-change evidence. The report's change extraction no longer treats an entry binding omitted from the exit projection as a deletion; actual deletion still comes from explicit operation changes. DOE operand lookup continues to use retained public IR inputs/outputs.

No second concrete blocker was identified in this bounded review. In particular, generated mapped-collection membership is still derived from the checked collection iteration path, and ordinary part materialization retains local closed-content/path checks. This is not a proof that every producer invariant or every possible descriptor refinement is correct.

## Limits

The review did not establish a full-GA4 speedup, complete source coverage, general convergence, exact rollback of loop-family may-facts, semantic equivalence, or absence of DOE. Local read tracking and projection reduce repeated work while retaining the documented domain limitations. The full offline benchmark must pin the post-correction implementation; pre-correction microbenchmark hashes do not identify this corrected candidate.
