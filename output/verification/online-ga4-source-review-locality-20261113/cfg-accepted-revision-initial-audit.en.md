# Accepted revised CFG: source audit

This is the accepted revision candidate before rereview and controller selection.

302 blocks, 770 IR, 283 edges. Bound graph/revision.json SHA-256: `f5b9be024271521f251d94fbacf366f3f49736a430138e0831a239418a601a41`.
All 416 source spans are valid and match compiled script text. The initial snapshot is preserved.

- **revision-accepted-not-yet-final-selected**: Revision graph a001 is valid without structural correction. graph/revision.json has 302 blocks, 770 IR and 283 edges, versus initial 268/679/252. At this snapshot graph/selected.json remains byte-identical to graph/initial.json. The revision is a candidate for controller selection, not yet final evidence.
- **physical-boundaries-retained-with-new-identities**: All 13 physical remote API calls and all 25 physical saveResult calls have exactly one matching primary CFG instruction. The mapping stores initial and revision identities separately. The remote IR explicitly retains an endpoint, method receiver and request argument. This does not establish correct executable processing or observed network/storage exposure.
- **report-and-bulk-maps-now-separated**: The revised CFG has separate report dimension and metric traversals, plus the bulk metric traversal, with initialize/merge/member/collect coordinates. Report request ir_140 consumes mapped results. Bulk request ir_228 consumes fixed [{name:pagePath},{name:pageTitle}] dimensions and an already mapped metric result. This is the correct source-level separation; the earlier processing double-wrap cannot be declared fixed until the revised processing uses those values without rewrapping them.
- **loop-and-sparse-array-fidelity-still-needs-processing**: Ten explicit iteration heads now include the three requested source maps in addition to the original seven. Metadata describes Array.map as visiting present slots in source order with original slot semantics. The executable processing must preserve index, holes, length and member association; explanatory metadata alone does not prove those properties.
- **summary-workflow-coordinates-added**: A documentation-level independent entry now reads saved JSON, creates Markdown and writes under results/summaries/. The graph explicitly leaves file selection, invocation provenance, exact summary dependencies and basename unspecified. It does not claim that a TypeScript function invokes this workflow or wire the independent storage examples as its provenance. These are source-backed natural-language operations, not an actual new Skill implementation.
- **module-import-routes-separated-as-call-coordinates**: Eleven evaluate_static_dependencies_once operations distinguish nine module routes (index, six direct API modules, storage and client) plus two documented examples importing index. Direct storage depends on settings without client initialization; direct API routes reach client/storage/settings without the index runtime guard. Only index evaluation leads to the argv/import.meta.url comparison. Dependencies are represented as instruction metadata and call-like coordinates, not CFG edges into the dependency bodies; executable state-sharing, once-per-module and abrupt-completion semantics remain obligations for processing.
- **cache-and-environment-obligations-explicit**: The client module initializes distinct cache slots. Three getter miss paths explicitly write their freshly constructed handles to the corresponding slots; constraints retain creation-time credentials and independent newer target settings. Dotenv initialization explicitly associates the post-environment with config(), while preserving internal precedence uncertainty. None of these CFG declarations alone proves that later processing retains the state relations.
- **source-behavior-not-repaired-to-match-task**: Custom filters and orderBy are still acquired but unused, the limit branch remains truthy, and empty bulk still returns zero rows before its API call/save. These source facts must coexist with the revised Task obligations/conflicts; the CFG correctly does not invent filtering, sorting or an empty-result write.
- **save-summaries-remain-processing-obligations**: Each physical call still has actual payload/category/operation/optional label operands. Caller-site wrapper construction, save-time settings/clocks, dynamic storage address and conditional directory effects must be represented in revised processing. The standalone storage body does not by itself fulfill all 25 occurrence-specific write relations.

## Remote source sites

- skill/scripts/src/api/bulk-lookup.ts:183: ir_175 → ir_230
- skill/scripts/src/api/indexing.ts:62: ir_346 → ir_403
- skill/scripts/src/api/indexing.ts:119: ir_366 → ir_424
- skill/scripts/src/api/indexing.ts:152: ir_387 → ir_446
- skill/scripts/src/api/metadata.ts:42: ir_246 → ir_301
- skill/scripts/src/api/metadata.ts:64: ir_260 → ir_315
- skill/scripts/src/api/metadata.ts:86: ir_274 → ir_329
- skill/scripts/src/api/realtime.ts:28: ir_190 → ir_245
- skill/scripts/src/api/realtime.ts:48: ir_204 → ir_259
- skill/scripts/src/api/realtime.ts:68: ir_218 → ir_273
- skill/scripts/src/api/realtime.ts:88: ir_232 → ir_287
- skill/scripts/src/api/reports.ts:100: ir_110 → ir_146
- skill/scripts/src/api/searchConsole.ts:102: ir_312 → ir_368

## Physical saveResult sites

- skill/scripts/src/api/bulk-lookup.ts:188: ir_180 → ir_235
- skill/scripts/src/api/indexing.ts:76: ir_357 → ir_414
- skill/scripts/src/api/indexing.ts:101: ir_422 → ir_481
- skill/scripts/src/api/indexing.ts:133: ir_377 → ir_435
- skill/scripts/src/api/indexing.ts:189: ir_407 → ir_466
- skill/scripts/src/api/metadata.ts:51: ir_250 → ir_305
- skill/scripts/src/api/metadata.ts:73: ir_264 → ir_319
- skill/scripts/src/api/metadata.ts:91: ir_278 → ir_333
- skill/scripts/src/api/realtime.ts:35: ir_194 → ir_249
- skill/scripts/src/api/realtime.ts:55: ir_208 → ir_263
- skill/scripts/src/api/realtime.ts:75: ir_222 → ir_277
- skill/scripts/src/api/realtime.ts:95: ir_236 → ir_291
- skill/scripts/src/api/reports.ts:105: ir_115 → ir_151
- skill/scripts/src/api/searchConsole.ts:118: ir_317 → ir_373
- skill/scripts/src/index.ts:73: ir_437 → ir_497
- skill/scripts/src/index.ts:104: ir_450 → ir_511
- skill/scripts/src/index.ts:135: ir_463 → ir_525
- skill/scripts/src/index.ts:162: ir_476 → ir_539
- skill/scripts/src/index.ts:200: ir_489 → ir_552
- skill/scripts/src/index.ts:222: ir_499 → ir_563
- skill/scripts/src/index.ts:252: ir_514 → ir_579
- skill/scripts/src/index.ts:272: ir_525 → ir_591
- skill/scripts/src/index.ts:292: ir_536 → ir_603
- skill/scripts/src/index.ts:316: ir_555 → ir_626
- skill/scripts/src/index.ts:343: ir_574 → ir_649

Accepted graph syntax, matching source spans and physical-site presence are not semantic correctness, dynamic reachability or verified demand-transfer evidence.
Inspect selected revised processing, rereview and final propagation separately; immutable initial and revision-candidate snapshots remain distinct.
This helper reads saved JSON only and invokes no compiler, validator, tests, backend, model, Skill or replay.
