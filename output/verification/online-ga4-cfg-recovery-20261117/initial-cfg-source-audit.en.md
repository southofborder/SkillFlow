# Provisional source audit of the accepted initial CFG

Run: `document-guided-ga4-cfg-recovery-high-20261117-135205`.
Frozen implementation: `694561928259d08c00492843a036ad0196460f785e6bd5d2fb1e07ba8ef59445`.
Source: `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.

This is a passive audit of this run's initial graph, not a final selected-graph or DOE assessment. The saved graph receipt accepted `calls/a001` with no structural correction or JSON normalization. The saved graph contains 215 blocks, 489 instructions and 192 edges. Structural acceptance is a recorded fact; no validator or compiler was rerun for this audit. This first-try submission did not exercise the new mixed-error correction or missing-CFG recovery paths online.

The complete frozen package contains 16 files and 155,170 bytes. Every physical file matches this run's saved snapshot hash and inventory. `initial-cfg-source-audit.json` binds the inspected artifacts and lists every source site, exact matching raw instruction, canonical instruction ID, and all eleven merge records. `audit_initial_cfg_source.py` uses only standard-library text/JSON/hash reads and writes this new report. No project imports, analysis/compiler/backend, Skill, model, test or replay was executed.

## Site presence versus exposed dependencies

| Physical source sites | Initial-CFG records | Interpretation |
| --- | --- | --- |
| 13 direct remote API calls | 13 unique external records | Source-site presence; only six expose result operands for the client and request or request ingredients. |
| 25 internal `saveResult` callers | 25 unique `save_result` records | All retain payload and category/operation information or ingredients and omit an unused filepath output. These remain opaque caller summaries. |
| 7 filesystem calls in `storage.ts` | 7 corresponding records | Three existence checks plus mkdir, write, read and readdir; no claim yet about their task demand or reached execution. |

The seven remote records with collapsed dependencies are four realtime requests (`ir_202`, `ir_209`, `ir_216`, `ir_223`) and three metadata requests (`ir_230`, `ir_239`, `ir_248`). Their source explicitly obtains `client = getClient()` and `property = getPropertyId()` before sending the request (`realtime.ts:24–32,44–52,64–72,84–92`; `metadata.ts:38–44,60–66,82–88`). The authored IR inputs contain the external resource identity and fixed request literals, or just the resource for metadata. Client/property acquisition, cache behavior, current settings, and property/name construction occur only in metadata prose. There is no produced receiver/property operand at those sites.

The other six remote records explicitly consume client handles and a request value or request fields: general report `ir_099`, bulk report `ir_160`, Search Console query `ir_173`, indexing publish/update `ir_258`, publish/delete `ir_270`, and inspection `ir_283`. This is an observable granularity distinction, not a six-of-thirteen overall correctness score. Source text and prose for the seven collapsed sites are retained. Processing and source review must determine whether their internal acquisitions and interface obligations are represented soundly; their absence from serialized input operands must not become evidence that those inputs are unnecessary.

Each `save_result` call is still a summary of the real callee. Some input operands are ingredients rather than the exact final argument: e.g. `ir_101` consumes `report_dimensions` and the original date value, while its metadata specifies `dimensions.join('_') || 'custom'` and the original string-only extra. Interface necessity must be checked against the actual callee arguments and transformations, not justified by the current IR operand list itself. A single standalone storage body does not prove all 25 caller-to-writer field relations.

The standalone storage implementation does expose the settings result, category directory, conditional recursive mkdir, path ingredients, separately named filename and metadata clock resources, serialization, replacing write and public path return (`storage.ts:58–95`). The wrapper expression retains `metadata.savedAt`, category, operation, save-time `settings.propertyId`, truthy optional extraInfo and the incoming data. Internal callers discard the returned path, matching the source. Ambient settings/cache/clock work inside call summaries still needs corresponding processing evidence.

## Loops, control and collection semantics

Four explicit collection headers preserve actual collection operands in `has_member` dispatches: URL normalization, low-level batch indexing, high-level reindexing and high-level status checking. Their merge inputs name distinct initial and body-produced versions; none of these headers self-reads its output as the prior version. All eleven authored merge predecessor arrays match the actual incoming block references in the saved edge list. This is a passive relation comparison, not an execution or propagation result.

The low-level batch source awaits each notification and appends only on fulfillment; rejection propagates before the next URL and aggregate save (`indexing.ts:89–105`). The graph exposes fulfillment/rejection dispatch and distinct exception exit. The high-level reindex/status loops catch per-item errors, preserve the input URL in failure rows, suppress child saves, and save an aggregate even for an empty input (`index.ts:301–345`). Their recorded success/failure accumulator predecessors agree with those branches. Some try-body work, request preparation and successful append are still summarized in one operation; processing must retain member/URL pairing and any required control, counts or prior effects.

Storage filters are represented differently: `select_and_sort_json_paths` summarizes `.json` filtering, path construction and descending filename ordering; `filter_paths_by_operation` summarizes sanitization and substring filtering. The metadata correctly records the actual operations at `storage.ts:132–139,162–163`. The separate limit branch tests `limit !== undefined`, matching the source rather than truthiness. These summary records avoid an explicit filter-loop carry, but structured membership/order/size and selected-output dependencies have not yet been certified by processing/source review. Structural acceptance alone cannot demonstrate those relationships.

## Preserved mismatches and missing links

- `reports.ts:78–86` really destructures `filters` and `orderBy`, while the request at lines 92–98 omits both. The graph retains the whole options input and labels those fields unused in metadata; it does not create explicit selected outputs for them. Their actual read/observation fact and the documentation's filtering/sorting obligation must both survive the eventual report. No deletability conclusion is made here.
- The documented saved-JSON-to-Markdown summary obligation is in top-level constraints and diagnostics. The graph has no runtime read/write continuation selecting this invocation's files and producing the required summary. The source provides no implemented invocation-to-file association or exact summary filename. Keeping that gap explicit is appropriate; task correspondence must not silently discard the documented output obligation or map unrelated latest/list examples as its provenance.
- Date comparison still requires ordered association of both input ranges/results; high-level child save suppression and output aggregation need processing verification. Source statements about universal autosave are not a substitute for the actual conditional/empty-input branches.
- The initial graph preserves notes about unsent report filters, unsorted page ranking, independent keyword/device and SEO/country queries, metadata wrapper shape, and the direct-command help-only path. These are model-authored diagnostic notes, not completed source-review findings.

No field-level requirement, deletable input, propagation reach or DOE outcome is established by this provisional audit. Final reporting must use the ultimately selected graph and the completed processing/review evidence, if produced. The present counts show physical source-site representation and identify concrete dependencies still requiring scrutiny; they do not support broad coverage, accuracy or performance claims.
