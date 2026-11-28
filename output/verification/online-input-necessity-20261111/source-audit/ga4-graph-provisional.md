# GA4 provisional initial CFG source audit

Status: **PROVISIONAL INITIAL CFG ONLY**. Captured 2026-11-11T18:08:45.584080+08:00.

The initial CFG has 535 instructions, 228 blocks and 206 edges. Its SHA-256 is `36c917c757a32b14a14ba3abce30bab26dae49e8cae0a79bedc9d5e4b22cf016`.

All 13 explicit remote call sites and 25 saveResult invocation sites in the independent original-source inventory have a corresponding CFG instruction. Every mapped physical call line matches the instruction source excerpt. All 25 internal save calls have empty outputs, preserving the discarded returned path. All 3 explicit URL loops retain member selection, predecessor merges, exits and backedges.

These are source-site correspondence counts. They are not propagation coverage, runtime counts, accepted contract counts or a complete DOE result. The graph contains independent exported entries and call summaries; helper summaries do not create additional physical source-site counts.

## Remote source crosswalk

| Source ID | Function | Source call line | CFG instruction | JSON pointer |
|---|---|---|---|---|
| R01 | runReport | scripts/src/api/reports.ts:100 | ir_101 | `/cfg/blocks/block_050/instructions/0` |
| R02 | getMetricsForUrls | scripts/src/api/bulk-lookup.ts:183 | ir_163 | `/cfg/blocks/block_079/instructions/0` |
| R03 | getActiveUsers | scripts/src/api/realtime.ts:28 | ir_208 | `/cfg/blocks/block_099/instructions/0` |
| R04 | getRealtimeEvents | scripts/src/api/realtime.ts:48 | ir_218 | `/cfg/blocks/block_104/instructions/0` |
| R05 | getRealtimePages | scripts/src/api/realtime.ts:68 | ir_228 | `/cfg/blocks/block_109/instructions/0` |
| R06 | getRealtimeSources | scripts/src/api/realtime.ts:88 | ir_238 | `/cfg/blocks/block_114/instructions/0` |
| R07 | getAvailableDimensions | scripts/src/api/metadata.ts:42 | ir_248 | `/cfg/blocks/block_119/instructions/0` |
| R08 | getAvailableMetrics | scripts/src/api/metadata.ts:64 | ir_260 | `/cfg/blocks/block_125/instructions/0` |
| R09 | getPropertyMetadata | scripts/src/api/metadata.ts:86 | ir_272 | `/cfg/blocks/block_131/instructions/0` |
| R10 | querySearchAnalytics | scripts/src/api/searchConsole.ts:102 | ir_177 | `/cfg/blocks/block_084/instructions/0` |
| R11 | requestIndexing | scripts/src/api/indexing.ts:62 | ir_282 | `/cfg/blocks/block_136/instructions/0` |
| R12 | removeFromIndex | scripts/src/api/indexing.ts:119 | ir_299 | `/cfg/blocks/block_144/instructions/0` |
| R13 | inspectUrl | scripts/src/api/indexing.ts:152 | ir_317 | `/cfg/blocks/block_152/instructions/0` |

## Save source crosswalk

| Source ID | Function | Source call line | CFG instruction | JSON pointer |
|---|---|---|---|---|
| S01 | runReport | scripts/src/api/reports.ts:105 | ir_104 | `/cfg/blocks/block_051/instructions/1` |
| S02 | getMetricsForUrls | scripts/src/api/bulk-lookup.ts:188 | ir_166 | `/cfg/blocks/block_080/instructions/1` |
| S03 | getActiveUsers | scripts/src/api/realtime.ts:35 | ir_210 | `/cfg/blocks/block_100/instructions/0` |
| S04 | getRealtimeEvents | scripts/src/api/realtime.ts:55 | ir_220 | `/cfg/blocks/block_105/instructions/0` |
| S05 | getRealtimePages | scripts/src/api/realtime.ts:75 | ir_230 | `/cfg/blocks/block_110/instructions/0` |
| S06 | getRealtimeSources | scripts/src/api/realtime.ts:95 | ir_240 | `/cfg/blocks/block_115/instructions/0` |
| S07 | getAvailableDimensions | scripts/src/api/metadata.ts:51 | ir_252 | `/cfg/blocks/block_121/instructions/0` |
| S08 | getAvailableMetrics | scripts/src/api/metadata.ts:73 | ir_264 | `/cfg/blocks/block_127/instructions/0` |
| S09 | getPropertyMetadata | scripts/src/api/metadata.ts:91 | ir_274 | `/cfg/blocks/block_132/instructions/0` |
| S10 | querySearchAnalytics | scripts/src/api/searchConsole.ts:118 | ir_180 | `/cfg/blocks/block_085/instructions/1` |
| S11 | requestIndexing | scripts/src/api/indexing.ts:76 | ir_291 | `/cfg/blocks/block_140/instructions/0` |
| S12 | requestIndexingBatch | scripts/src/api/indexing.ts:101 | ir_348 | `/cfg/blocks/block_167/instructions/0` |
| S13 | removeFromIndex | scripts/src/api/indexing.ts:133 | ir_308 | `/cfg/blocks/block_148/instructions/0` |
| S14 | inspectUrl | scripts/src/api/indexing.ts:189 | ir_330 | `/cfg/blocks/block_158/instructions/0` |
| S15 | siteOverview | scripts/src/index.ts:73 | ir_397 | `/cfg/blocks/block_184/instructions/6` |
| S16 | trafficAnalysis | scripts/src/index.ts:104 | ir_407 | `/cfg/blocks/block_186/instructions/5` |
| S17 | contentPerformance | scripts/src/index.ts:135 | ir_417 | `/cfg/blocks/block_188/instructions/5` |
| S18 | userBehavior | scripts/src/index.ts:162 | ir_427 | `/cfg/blocks/block_190/instructions/5` |
| S19 | compareDateRanges | scripts/src/index.ts:200 | ir_437 | `/cfg/blocks/block_192/instructions/5` |
| S20 | liveSnapshot | scripts/src/index.ts:222 | ir_444 | `/cfg/blocks/block_193/instructions/4` |
| S21 | searchConsoleOverview | scripts/src/index.ts:252 | ir_455 | `/cfg/blocks/block_195/instructions/6` |
| S22 | keywordAnalysis | scripts/src/index.ts:272 | ir_464 | `/cfg/blocks/block_197/instructions/4` |
| S23 | seoPagePerformance | scripts/src/index.ts:292 | ir_473 | `/cfg/blocks/block_199/instructions/4` |
| S24 | reindexUrls | scripts/src/index.ts:316 | ir_367 | `/cfg/blocks/block_175/instructions/0` |
| S25 | checkIndexStatus | scripts/src/index.ts:343 | ir_386 | `/cfg/blocks/block_182/instructions/0` |

## Field and control relationships

### G01 — represented

Settings acquisition retains all six actual fields, while property and site helpers identify their own selected fields. Validation records falsy tests and constant error strings. These statements support narrower reverse requirements, but processing contracts are needed to determine whether value, presence or another information property is actually demanded.

CFG: ir_017, ir_020, ir_023, ir_026.

Source: `scripts/src/config/settings.ts:40-74`; `scripts/src/core/client.ts:45-53`; `scripts/src/core/client.ts:128-133`.

### G02 — represented_with_pending_transfer

GA4 handle construction maps only clientEmail/privateKey into credential fields. Search Console/Indexing auth summaries record the same fields and both scopes, with a fresh settings read. That read is summary metadata rather than a separate result operand at ir_047/ir_057; later processing must represent its source provenance. The CFG alone does not prove credential wire transmission, SDK-required scope minimality or correct input necessity.

CFG: ir_038, ir_047, ir_057.

Source: `scripts/src/core/client.ts:23-42`; `scripts/src/core/client.ts:67-79`.

### G03 — represented

Report unpacking explicitly identifies filters/orderBy as unused and leaves them out of its outputs; the base request consumes property, parsed range, dimensions and metrics. A separate truthy-limit branch and predecessor merge retain optional-limit behavior. Actual absence from the request is not evidence that the documented filter/sort purpose is fulfilled.

CFG: ir_091, ir_095, ir_097, ir_099, ir_101.

Source: `scripts/src/api/reports.ts:20-28`; `scripts/src/api/reports.ts:78-100`.

### G04 — represented

The bulk empty-input branch returns before client acquisition, filter/request assembly and saving. The nonempty request includes normalized URL membership, selected metrics, dimensions and parsed range. No remote action is represented on the empty branch.

CFG: ir_149, ir_154, ir_155, ir_156, ir_161, ir_163.

Source: `scripts/src/api/bulk-lookup.ts:78-98`; `scripts/src/api/bulk-lookup.ts:149-191`.

### G05 — represented

Metadata dimensions and metrics each project only their named response array with the source empty-array fallback. The whole full-metadata reply remains separate. Projection keeps member contents unchanged; no artificial apiName/uiName/description-only member filter was inserted into actual forward facts.

CFG: ir_248, ir_250, ir_252, ir_254, ir_260, ir_262, ir_264, ir_266, ir_272, ir_274, ir_276.

Source: `scripts/src/api/metadata.ts:38-95`.

### G06 — represented

Inspection separates base indexStatus/link, mobile usability and rich results, then assembles the direct return. The high-level status loop appends only the normal indexStatus projection plus the input URL and PASS-derived indexed flag. Reverse demand for that workflow should not automatically retain unrelated mobile/rich/link fields.

CFG: ir_317, ir_319, ir_321, ir_325, ir_328, ir_378, ir_380.

Source: `scripts/src/api/indexing.ts:146-193`; `scripts/src/index.ts:324-345`.

### G07 — represented

All 25 source saveResult sites are present with empty outputs, matching discarded helper paths. The separately callable storage.save entry builds and returns the filepath after write success. Filename construction has no data/propertyId operand; wrapper construction separately consumes data and settings.propertyId. This preserves the distinction between path text dependencies and successful write/control dependencies.

CFG: ir_483, ir_491, ir_495, ir_496, ir_497.

Source: `scripts/src/core/storage.ts:58-95`.

### G08 — represented_with_pending_closed_output_contracts

Nine non-loop high-level aggregate constructions retain explicit ordered field-to-input mappings, including period1/period2 pairing. Closed outer shape is source-supported; nested whole SDK replies remain opaque and do not gain closed field coverage from these wrappers. Processing/output_parts and task mapping are still needed before a whole-output necessity conclusion.

CFG: ir_395, ir_405, ir_415, ir_425, ir_436, ir_443, ir_453, ir_462, ir_471.

Source: `scripts/src/index.ts:55-295`.

### G09 — represented_with_pending_invocation_semantics

The three URL loops have distinct collection/current-member/result operands, predecessor merges, exhausted exits and backedges. Low-level batching propagates exceptions without an aggregate save; high-level loops merge success and caught-error appends back into the same loop. These source relationships are represented, but occurrence preservation and propagation remain unverified until processing and backend results exist.

CFG: ir_338, ir_340, ir_341, ir_343, ir_345, ir_356, ir_358, ir_359, ir_361, ir_363, ir_365, ir_375, ir_377, ir_378, ir_380, ir_382, ir_384.

Source: `scripts/src/api/indexing.ts:89-105`; `scripts/src/index.ts:301-345`.

### G10 — explicit_source_limit

Graph constraint 2 records the declared analysis-save-summary obligation. The source has independent save/read utilities and no implemented summary writer; this audit has not found or invented a Markdown summary write boundary. Its 13 remote/25 save denominator excludes that missing implementation and SDK internals.

CFG: ir_496, ir_502, ir_504, ir_526, ir_534.

Source: `SKILL.md:53-64`; `SKILL.md:129-142`; `scripts/src/core/storage.ts:58-171`.

## Evidence and remaining work

The companion `ga4-graph-provisional.json` records exact pointers, source lines, call operands, outputs, loop edges, original-source verification and the initial CFG hash. Original source files remained byte-identical. Only new audit files were written; the pipeline received no feedback.

Graph artifact: `D:\Projects\SkillFlow\experiments\doe\runs\document-guided-ga4-input-necessity-high-20261111-173347\graph\initial.json`.

The pending checks are processing/input contract source support, exact output demands, hidden settings reads inside invocation summaries, per-occurrence propagation and final selected-graph correspondence. If repair changes the graph, the initial pointers in this report are superseded for final claims; preserve this capture and produce a new final crosswalk.
