The closed GA4 interface-r4 run represents all **13 inventoried API request sites, 25 `saveResult` call sites, and three explicit source loops**, and each mapped boundary has nonempty computed facts in the saved propagation records. This is a finite source-boundary finding. It does not establish exact request construction, payload bytes, path feasibility, complete source semantics, complete DOE, or general accuracy.

The audited run is `experiments/doe/runs/document-guided-ga4-interface-r4-high-20261104-173522`. The selection is `graph/revision.json` and `revision/annotation`; the selected CFG has 169 blocks and 369 IR. The propagation manifest marks all 369 IR processed. Its single diagnostic is discussed below. All 16 frozen source files match the hashes in the independently prepared `source-audit/boundary-inventory.json`. This audit reads source text and saved JSON with the Python standard library only. It neither invokes SkillFlow nor executes the Skill, solver, loader, target, replay, or a model. The original inspected artifacts remained unchanged during extraction.

The detailed evidence is in `boundary-evidence.json`, including source hashes, original artifact hashes, each of the 38 inventory-site mappings, exact operation coordinates, request/response Data IDs, save-input provenance, and save/return identity checks. `loop-audit.json` supplies the independent loop analysis. The extractor is preserved as `extract_boundary_evidence.py`.

The broader `correctness-relations.json` assesses every S01-S24 source criterion using this boundary evidence and the separate DOE audit. It records a concrete cache-state identity contradiction at S05: `ir_356` reads `core.client.cached_bindings`, while the represented initialization/reset/construction writes update three different individual client locations without connecting that aggregate read. It also retains the direct realtime identity collapse, absent declared `.env` creation, filepath binding gaps, incomplete helper/error versions, demand-applicability gaps and final review ownership error. The boundary counts below do not override these broader correctness findings.

The 13 API source sites map to seven primary computed API instructions. Each primary instruction has a compiled call and a saved remote `deliver`/`receive` pair with nonempty request and response facts:

| Frozen source site(s) | Primary API IR | Source boundary represented |
|---|---|---|
| `api/reports.ts:100` | `ir_189` | `runReport` |
| `api/realtime.ts:28,48,68,88` | `ir_198` | Four realtime entry functions share one entry-dependent `runRealtimeReport` boundary |
| `api/metadata.ts:42,64,86` | `ir_207` | Dimensions, metrics, and full metadata share one `getMetadata` boundary |
| `api/searchConsole.ts:102` | `ir_226` | `searchanalytics.query` |
| `api/indexing.ts:152` | `ir_238` | `urlInspection.index.inspect` |
| `api/indexing.ts:62,119` | `ir_257` | Update and removal share an entry-dependent `urlNotifications.publish` boundary |
| `api/bulk-lookup.ts:183` | `ir_272` | Nonempty bulk lookup `runReport` |

Paths in the tables are relative to frozen `source/inputs/package/scripts/src/`. Shared representation matters: the saved direct realtime boundary has one request Data identity, and its request is produced by opaque `ir_196` computation from the entry name and property. It does not separately resolve four concrete dimension/metric request objects. The shared publication request retains explicit `requestBody.url` and `requestBody.type` structure, but the entry-dependent choice between `URL_UPDATED` and `URL_DELETED` is opaque. Metadata preserves three later result alternatives, while sharing the initial response. These are computed counterparts to all the cited sites, not 13 independently resolved executions.

Caller expansions add further copies of source boundaries. Across the complete saved records, 38 remote send/receive operation pairs have the same compiled request ID, actual request Data-ID sets, endpoint, and alternative member/predecessor bindings. This supports pairing within the represented operations. It does not establish exact SDK internals, credential transmission, or runtime call counts. The endpoint is the modeled Google service; caller getter summaries leave cached-client credential provenance unexpanded.

The 25 source `saveResult` sites map to 18 primary write instructions:

| Frozen source site(s) | Primary save IR | Payload alternatives at this write |
|---|---|---:|
| `api/reports.ts:105` | `ir_192` | 2 |
| `api/realtime.ts:35,55,75,95` | `ir_201` | 1 |
| `api/metadata.ts:51,73,91` | `ir_219` | 3 |
| `api/searchConsole.ts:118` | `ir_230` | 1 |
| `api/indexing.ts:76,133,189` | `ir_263` | 5 |
| `api/indexing.ts:101` | `ir_175` | 2 |
| `api/bulk-lookup.ts:188` | `ir_275` | 1 |
| `index.ts:73,104,135,162` | `ir_034,ir_045,ir_056,ir_067` respectively | 1 each |
| `index.ts:200,222` | `ir_078,ir_089` respectively | 1 each |
| `index.ts:252,272,292` | `ir_102,ir_111,ir_120` respectively | 1 each |
| `index.ts:316,343` | `ir_141,ir_162` respectively | 14 each |

For every one of these 18 primary save instructions, the first serialization input is exactly the Data-ID set of the actual incoming value argument; the serialization outputs exactly equal the write inputs. The original values also exactly match the corresponding function return-input Data-ID sets. This checks recorded version continuity through the save and return. It does not equate the returned value with its serialized bytes.

Several distinctions survive in those facts:

- Direct report, realtime, and bulk saves retain their corresponding received response versions. Search Console selects `response.data` at `ir_228` before saving/returning it. Metadata separately selects and wraps dimensions at `ir_210`, metrics at `ir_213`, or retains the full response at `ir_215`; all three predecessor-correlated values reach the shared save at `ir_219`.
- The shared indexing save has four inspection-result alternatives with inspection-response ancestry and one publication-result alternative with publication-response ancestry. It does not replace an inspection result with a report response. Exact publication fallbacks and some inspection projections are opaque computations, so ancestry alone does not prove field equality or complete plaintext inclusion.
- `compareDateRanges` has distinct period-1 and period-2 response IDs at `ir_074` and `ir_076`, and the saved comparison explicitly places them under `period1.data` and `period2.data` with their respective dates. Both child calls pass `save:false` and contain no storage write; the outer comparison is saved at `ir_078`. This absence is source-supported, not an uncovered child save.
- The live snapshot expands only the source's active-user, page, and event calls (`ir_083`, `ir_085`, `ir_087`), while the independent realtime-sources capability is represented through the shared direct entry. `availableFields` acquires/saves full metadata at `ir_180`; its following dimension/metric-count logs do not reduce that returned version to counts.

Including caller expansions and the standalone storage entry, the records contain 44 storage-write positions. Another 14 writes update runtime context, for 58 write positions in total. All 58 compiled writes use `replace`. The saved-file state updates are weak because the selected-path and load-path endpoints are symbolic may-alias locations; this does not introduce source append semantics or establish a definite filename alias. Source `storage.ts:80-92` wraps the actual data with metadata and serializes the wrapper. Caller save summaries retain their own incoming data, category/operation information, current property, and saved-at clock observation, but use opaque serialization with `possible` dependencies. Exact saved bytes, omission of undefined properties, concrete path uniqueness, and filesystem failure ordering are not proved by these records. The independently modeled storage function does not fill in missing caller execution detail.

All three explicit loops have computed final writes and save/return version links:

| Source loop | Member/child call | Final save and return | Recorded final collection alternatives |
|---|---|---|---:|
| `api/indexing.ts:95` | `ir_170` / `ir_171` | `ir_175` / `ir_177` | 2 |
| `index.ts:305` | `ir_128` / `ir_131` | `ir_141` / `ir_143` | 14 |
| `index.ts:328` | `ir_149` / `ir_152` | `ir_162` / `ir_164` | 14 |

The member scopes are distinct. Normal request/response pairs and caught-error acquisitions retain the corresponding member bindings. The wrapper failure items retain the original URL and caught-error predecessor. None of the three child-call summaries writes storage, consistent with their `save:false` argument. The uncaught batch call has no invented catch-to-next-item route. Empty source collections do not imply a child request; final collection saves remain separate. The bulk helper's separate empty-normalized-input arm likewise returns before getter/date/API/save (`bulk-lookup.ts:158-164`, `ir_268`/`ir_269`). These are conditional source explanations; unknown public inputs still leave the nonempty branches represented.

Loop alternatives are static summaries, not concrete iteration counts. Six of the fourteen final reindex collection identities and six of the fourteen final status collection identities retain explicit `multiple_generations` predecessor ambiguity. Reindex result spread, some error timing/partial mutation, and final serialization remain opaque or expressly limited. The status success item retains only URL, indexed status, and the selected `indexStatus`; its `PASS` comparison is present, but its resulting boolean is unknown in the facts. No extra loop cutoff or omitted inventoried loop boundary was found in this narrow audit.

There are three distinct residual layers. First, a **source/CFG workflow gap** remains outside the finite API/save inventory: the Skill requires analysis, automatic saving, reading the corresponding saved JSON, and a Markdown summary in `results/summaries`, but no supplied implementation/selected CFG connects these into that continuation. The selected processing gaps at `ir_349` and `ir_350` state this explicitly. Independently selecting the latest file does not establish association with the preceding analysis invocation.

Second, **processing precision gaps** remain even though no IR is marked unmodeled: the selected annotation contains 20 processing gaps, all with `unmodeled:false`. They include opaque request construction and serialization, private getter/date behavior, client-cache credential provenance, conditional filesystem effects, and loop error/version detail. A processed mark means the submitted model was processed, not that these source relationships became exact.

Third, the saved records show a **branch-correlation limitation** at loading. `ir_322` records the successful outcome's `succeeded` value going to `block_142` and the caught-error outcome's false value going to `block_143`. Nevertheless, `ir_323` in the successful arm retains both outcome objects. Its `value` selection on the caught-error object emits the sole `missing_part` diagnostic and yields an empty alternative; its valid parsed Data survives to `ir_324`. This is concrete spurious cross-arm retention in the saved facts. It is not evidence that an inventoried API/save boundary was skipped or that the successfully parsed returned value was replaced.

The finite audit therefore supports represented and computed boundary coverage with retained versions and request/receiver associations, subject to the shared entries and precision limits above. DOE and constraint conclusions require their separate audit. No whole-source equivalence, general precision/recall, complete workflow implementation, or absence of excess exposure follows from these counts.
