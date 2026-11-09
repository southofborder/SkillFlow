# GA4 v8 final source-boundary coverage audit

**GA4 did not achieve complete or useful end-to-end propagation.** The saved calculation closes as `incomplete`: 29 of 420 generated IR were processed (6.90%), 5 reached explicit unmodeled cutoffs and 386 were blocked. None of the 13 remote API source sites, 25 `saveResult` callsites or 3 explicit source loops has a resolved propagated boundary. This is a source-coverage result, distinct from generated-IR coverage. It is not an overall accuracy estimate.

Run: `D:\projects\SkillFlow\experiments\doe\runs\document-guided-ga4-general-loops-high-v8-20261101-214322`. Audit uses the selected revised CFG and annotation and already-saved propagation files. No target, public loader, compiler, solver or replay was run for this audit. The 16 current frozen source files were SHA-256 checked against the pre-run source inventory; all match. The inventory is assistant source review, not human gold. [Machine-readable audit with every source site, candidate coordinate, coverage state and artifact hash](ga4-coverage.json).

## What was actually calculated

| Measure | Final saved evidence |
|---|---:|
| Generated IR |420|
| Compiled processing declarations |372|
| Explicit source-unmodeled declarations |48|
| Processed IR |29/420(6.90%) |
| Reached unmodeled cutoffs |5|
| Blocked IR |386|
| Saved Data objects |35|
| Data with sensitivity labels |0|
| Declared compiled sink positions |14|
| Resolved saved sinks |0/14|

The 29 records are `ir_001`–`ir_018` and `ir_024`–`ir_034`. They cover invocation construction, setup shell operations, module/dependency handling, singleton initialization, CLI/help checks and return/dispatch mechanics. Dispatches and empty returns count as processed IR, so 6.90% must not be presented as a fraction of useful API analysis.18 Data objects have no analyzed origin position; initial or otherwise source-position-free objects do not prove that a source acquisition ran. All 35 objects have empty sensitivity labels because the credential and API-response acquisitions never propagated; that is not evidence that GA4 data are nonsensitive.

The saved records contain 5 `deliver` and 4 `receive` operations for shell setup, dependency loading and static console output. They are represented as `effect:null` rather than compiled exposure boundaries. Thus “zero sinks” does not mean that the records contain no delivery-like operations. All 14 compiled sink positions are at blocked IR:043, 045, 048, 050, 171, 173, 175, 287 (six candidate positions) and 343. Their payloads were not resolved.

## Source boundaries and candidate mapping

| Source positions | Candidate representation | Actual propagated coverage |
|---|---|---:|
| 9 GA4 report/realtime/metadata/bulk remote sites |Shared definition list `ir_133`, request assembly 169, GA4 request 171 |0/9|
| 2 Indexing publish sites |Shared request assembly 169, publish 175; per-URL summary 287 also applies to updates |0/2|
| 2 Search Console analytics/inspection sites |Shared request assembly 169, Search Console request 173; per-URL summary 287 also applies to inspection |0/2|
| 13 single API saves |Shared call 219 and shared file write 343 |0/13|
| 8 orchestration aggregate saves |Shared call 247 and shared file write 343 |0/8|
| 1 date-comparison save |Call 266 and shared file write 343 |0/1|
| 3 URL-batch saves |Shared call 299 and shared file write 343 |0/3|
| 3 explicit `for...of` sites |Shared URL loop 275–302, member 281, child summary 287, accumulation 290/296 |0/3|

These matches establish where the candidate intended to represent the source sites. They do not certify complete modeling. The four save-call families 219/247/266/299 are themselves explicitly unmodeled even though the shared `writeFileSync` body 343 has processing semantics. Source inventory denominators count static sites, not dynamic calls. The single `core/storage.ts:92` implementation is not an additional 26th save callsite.

Other relevant boundaries are also unresolved: `settings.ts:9` dotenv initialization(ir 019); actual environment/credential projection at `settings.ts:40–48`(ir 055); credential-bound client construction at `client.ts:23–43`(ir 092); the declared analysis→read JSON→summarize→save workflow in `SKILL.md:39–64`(ir 039/043/045/048/050); file acquisition and parsed return at `core/storage.ts:103–113`(ir 350/353/356/357); returned save filepath(ir 345); and latest-file loading/return(ir 415/418). The missing analysis-to-saved-file ownership relationship remains a real source limitation. Control ordering alone cannot supply it.

GA4 has three explicit URL loops: `api/indexing.ts:95` (no per-member catch), `index.ts:305` and 328 (per-member catch and continue). All are blocked before any member record. This run therefore supplies no real-case evidence of loop-summary convergence, nested-loop precision or per-occurrence payload pairing, even though the backend returned and saved its partial result. It also does not demonstrate backend nonconvergence: no main loop record was reached.

## The stopping layer

| Reached cutoff | Exact selected-candidate defect |
|---|---|
|ir019, dotenv initialization |Processing declines the whole visible boundary because exact library loading/precedence is unknown. A source-bounded possible environment post-state was not represented.|
|ir035, selected exported call |The CFG uses a factored internal invocation; processing reports no callee-completion link and stops.|
|ir039, workflow analysis call |The same invocation-link mismatch stops the declared analysis workflow before read/summarize/save.|
|ir053, parameter binding |CFG has an empty input list for actual invocation binding; processing cannot obtain real caller values.|
|ir419, abrupt-completion merge |Several thrown-value origins are absent as operands; the candidate cannot preserve predecessor-specific failure linkage.|

The immediate coverage failure is the selected CFG/processing interface and modeling choices. Five declared gaps terminate their blocks as specified; the other 43 source-unmodeled declarations remain downstream and are not separately visited. This is not a structure-validation rejection of the final annotation: 372 records compiled and propagation completed its supported prefix. Nor does the saved evidence attribute the coverage failure to an active loop solver that never converged. Fixing local runtime serialization cost alone cannot make these blocked semantics propagate.

## Accuracy evidence and remaining review

The final independent source-review request completed, but it retained 10 findings: 2 CFG, 5 processing and 3 task-correspondence. “Review request completed” is not “semantic review passed.” This boundary audit independently checks the following source/candidate discrepancies:

- **F001, incorrect effect order:** `bulk-lookup.ts:166–172` builds its URL filter before client/property/date acquisition. Candidate ir142/146/154 precedes filter invocation 162, allowing effects before a failure that source orders earlier.
- **F003, unnecessary whole-boundary cutoff:** `settings.ts:5–9` visibly invokes zero-argument `config()`. Unknown library internals justify local uncertainty, but the candidate loses even the possible call-origin environment post-state by declaring 019 unmodeled.
- **F004, avoidable settings-call gaps:** `settings.ts:40–48` visibly reads five environment entries and current directory, projects fields and normalizes private-key newlines. Separate settings-function declarations do not connect blocked calls 057/086/098/107/323/359. Occurrence-specific boundary summaries would avoid requiring a new generic invocation engine.
- **F005, disconnected cache versions:** `client.ts:12–25,58–62` checks and updates the same named singleton bindings. Annotation 077 instead reads aggregate location `caches`, while initialization/construction/reset write separate `ga4_cache`, `search_cache` and `indexing_cache`, with no declared relation.

The already-delivered interim audit also found that downstream SOURCE views omitted some frozen file ranges; candidate metadata repeatedly calls available full-source behavior PREVIOUS WORK. The complete frozen package and the material actually delivered to a stage must therefore remain distinct when attributing these errors. See [interim input and interface audit](../unmodeled-ir-audit/assessment.en.md).

The retained review additionally identifies inspection requestBody shape (F002), missing per-URL client/cache and clock effects (F006), visible inspection-response fields treated as unavailable (F007), omitted GA4 measured row-value demands (F008), discovery demands overextended to arbitrary entry fields (F009), and missing ordered batch-result demand (F010). These are preserved as source-review findings rather than converted here into an invented global accuracy percentage. The companion DOE audit separately evaluates demand correctness and result usefulness.

**Practical reading:** a partial calculation and zero-call replay can be reproducible while failing the main analysis objective. Here, API responses, sensitive credential flow, saved payloads and loop members remain unresolved. Zero resolved sinks and zero sensitive Data labels cannot support a negative DOE or safety conclusion. No precision/recall, general accuracy, or advantage over direct GPT is established by this single stopped-coverage case.
