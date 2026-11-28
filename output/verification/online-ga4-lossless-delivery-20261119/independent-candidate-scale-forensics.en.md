# Independent candidate-scale forensics

Run: `document-guided-ga4-lossless-delivery-high-20261122-211742`. Parent: closed `document-guided-ga4-runtime-locality-high-20261117-205158`.

This inspection read only saved processing, sensitivity, compiled annotation, propagation records/data, frozen source, and implementation files. It did not load the 266 MB DOE result, import an analysis engine, execute a Skill, or issue model/network requests. Machine-readable evidence and exact input hashes are in `independent-candidate-scale-forensics.json`; its standard-library-only extractor is `independent_candidate_scale_audit.py`.

## Why the candidate count grew

The independent backend distribution audit counted 83,442 unique review tuples, with no exact duplicate rows and no candidate-by-demand Cartesian join. Its largest sink, `sink_e7831a4ea55a7b83b98d` at `ir_416`, contains **81 payload Data variants × 428 nondominated sensitivity signals = 34,668 reviews**. Of those, 34,344 have `possible` relation and 324 have `direct` relation. These are candidate comparisons, not 34,668 proven disclosures or deletion findings.

The small-artifact inspection independently confirms the two main multipliers:

1. **Repeated declaration identities share one value.** The current sensitivity answer has 209 declarations, versus 177 in the parent. It contains 51 pairs labeled service-account private key and identity “at this handle's creation.” These 102 field-specific declarations refer to `creation_env`, `creation_sc_env`, or `creation_ix_env` in 51 IRs; they do not declare invented fields on opaque SDK handles. The compiled references are correctly case-scoped. Of these, 100 declarations have recorded producers, all resolving to the same opaque live-environment Data ID, `data_12838c6ebe4539a87e80caa3cecb5a7d50fcd481d71b18177ea3229bf35e59e8`. The remaining pair at `ir_168` has no forward producer record. This does not establish 100 distinct credentials. `sensitivity_engine.py:45` intentionally preserves different declaration identities even when they label the same Data and path.

2. **The report construction multiplies three alternatives across four components.** Saved `ir_411`–`ir_414` each produce three Data alternatives from object, string, and default date-range cases. At `ir_415`, the saved build record has four input slots of cardinality `[3,3,3,3]`, 81 output Data IDs, and 81 alternatives. `ir_416` writes those 81 payload candidates. This is an actual saved propagation result, not a count inferred solely from a static loop. The existing interpreter constructs the product at `interpreter.py:426–481`.

The same opaque environment also supplies the modeled site and default-date-range computations. Their compiled `compute` operations use `possible` dependency relations. Sensitivity tracking keeps opaque dependency influence (`sensitivity_engine.py:424–432`) and transforms its field path into a whole-output possible influence (`:597–603`); structured expressions can restrict this influence, but these operations are opaque computes. Thus many distinct credential declaration identities can reach modeled report outputs as **possible influence**. This is not evidence that the real response or stored report contains credential plaintext, and not evidence of an actual SDK receiver observation.

The operation's `demand_transfer` names the narrower fields needed for backward necessity (for example `SEARCH_CONSOLE_SITE_URL` and `GA4_DEFAULT_DATE_RANGE`). That table intentionally does **not** rewrite actual forward reads or observation provenance. Using it automatically to erase the existing possible forward flows would violate the accepted plan. The correct distinction is between a broad forward approximation and an audited backward necessity relation.

## Source correlation and its current limit

The source `scripts/src/index.ts:235–249` passes the same `dateRange` argument to all four overview helpers. `scripts/src/api/searchConsole.ts:51–59` decides the object/falsy/default route from that argument; the helper wrappers at `:127–164` pass it through. All four recorded object alternatives use the identical original Data ID, `data_7e8f1c269fec9bc4340e8643c5b989cc2d05cac11f31cc6382342f81665a7be2`.

The generated processing contract expresses these route conditions in prose. The compiled final operation receives an `alternatives` reference containing the three yields, with no shared typed discriminator. Saved per-case compute alternatives already have empty `bindings`; the final component compute and the four-component build do too. Therefore this is not evidence that the build alone discarded a previously recorded shared typed decision.

The saved product contains 78 mixed **branch-category** combinations and three uniform combinations. A concrete recorded witness combines an object-pass-through `topQueries` with default-branch outputs in other fields; its full Data record and component links are in the JSON receipt. Those categories are incompatible for the same unchanged argument's type/truthiness. This establishes a source-correlation gap. It does **not** establish that all 81 candidates are invalid or that the real program has exactly three concrete outcomes: clock reads, default settings, and remote results may differ across calls. Equal case names alone must never be used as a correlation heuristic.

## This was not a changed candidate-join algorithm

Current versus parent snapshot hashes show identical propagation interpreter, Data registry, annotation compiler, sensitivity material builder, and sensitivity report renderer. The only textual difference in `sensitivity_engine.py` is the result schema identity, `skillflow-sensitivity-review-v9` to `v10`. Its candidate loop is unchanged: sink → actual payload slot → recorded Data ID → nondominated sensitivity signal (`:680–720`); matching demand references are attached to the row, not multiplied into additional rows.

The current and parent model outputs differ materially. In particular, the parent represented the Search Console query helper using local getter calls, an explicit remote `scQuery` call, and response-data selection; the current answer expands cache/date cases and coarsens part of the query result into an opaque compute. This is a model-output difference. The separately verified lossless normal-input equality rules out attributing it to omitted fields during shared encoding; it does not make the fresh semantic output correct.

## Report scale and follow-up boundaries

The unchanged HTML renderer expands each review's limitations and input-assessment evidence and also includes a full comparison record for each sink (`sensitivity_report.py:214–235`). Large candidate sets and repeatedly expanded support therefore amplify publication size beyond the compact DOE JSON. This code inspection does not claim a measured per-component allocation breakdown or an out-of-memory failure.

Result-based proposals, **not implemented here**:

- Preserve raw forward facts and source-site provenance. Where source expressions explicitly select environment fields, model those selections and constructions faithfully rather than treating the whole environment as an opaque operand for unrelated field computations.
- Validate sensitive declarations against their actual source fields and creation results. If grouping repeated equivalent declarations for presentation or computation, retain every source location and declaration identity in the proof record; do not merge merely because labels match.
- Introduce verified typed selector/guard provenance, or preserve real existing decision bindings, to express source-established correlations. Do not execute case-condition prose or infer correlation from strings.
- If an additional audited semantic-influence view is desired, give it its own proof and identity; do not silently overwrite the raw forward relation with backward demand transfer.
- Keep shared support records and page/group large reports without dropping candidate or evidence coverage. Formatting improvements alone do not repair semantic overapproximation.

Production, prompts, controller, frozen histories, and existing reports were not modified by this audit.
