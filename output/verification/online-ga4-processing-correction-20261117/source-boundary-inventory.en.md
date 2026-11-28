# Fresh-run source and boundary inventory

This is a passive inventory of the complete source frozen inside
`document-guided-ga4-processing-correction-high-20261117-110830`. All 16 readable
files match their saved raw hashes and physical inventory, totaling 155,170
bytes. Source SHA-256 is
`3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`.
No prior model answer or graph was imported. No Skill, compiler, analysis engine,
validator, model request or replay was executed by this audit.

There are **13 distinct direct remote API source sites**, **25 internal
`saveResult` caller sites**, and **7 explicit filesystem source sites**. These
are physical source counts, not dynamic call frequencies or evidence of generated
coverage, propagation reach or DOE. SDK internals are outside this source bundle.
The machine inventory records exact lines, callers, source excerpts and hashes
in `source-boundary-inventory.json`.

| Direct remote boundary | Source location under `skill/scripts/src/` |
| --- | --- |
| General GA4 report | `api/reports.ts:100` |
| Bulk URL report | `api/bulk-lookup.ts:183` |
| Active users, events, pages, sources | `api/realtime.ts:28,48,68,88` |
| Dimensions, metrics, full metadata | `api/metadata.ts:42,64,86` |
| Search analytics query | `api/searchConsole.ts:102` |
| URL update and removal notifications | `api/indexing.ts:62,119` |
| URL inspection | `api/indexing.ts:152` |

Every remote invocation has an actual `client` receiver. GA4 requests additionally
derive a property identifier; Search Console query and URL inspection derive a
site URL. `core/client.ts` contains cached clients, validation branches,
credentials and auth scopes. A future generated representation must preserve
these relationships where used, rather than treating an effect description or
recipient label as a data dependency. The inventory does not assume SDK
implementation details or infer extra network calls from constructors.

The 25 save callers comprise 14 API-module sites and 11 orchestration sites in
`index.ts`. All are statement calls that discard the returned path. The public
`saveResult` function itself does return the path at `core/storage.ts:94`; these
facts must remain distinct. Caller sites feed one physical `writeFileSync` at
line 92 through the actual wrapper at lines 58–95. It reads fresh settings,
forms a category path, conditionally creates the directory at lines 68–69,
creates a timestamped sanitized filename, and serializes
`{metadata:{savedAt,category,operation,propertyId,...truthy extraInfo},data}`.
The path timestamp and metadata timestamp are distinct source clock reads. A
plain statement that the original response was saved does not by itself establish
this caller-to-wrapper-to-write relationship.

The other filesystem sites are `existsSync` at storage lines 68, 104 and 127,
`readFileSync` at 109 and `readdirSync` at 131. `loadResult` returns null on absence
or caught read/parse failure. `listResults` filters JSON names, maps paths, orders
them and applies an optional limit. `getLatestResult` selects an optional
operation match and loads the first remaining path. These operations require
versions, existence/count conditions and member relationships to be represented
accurately; a summary source span alone cannot establish them.

Several source distinctions will guide the later audit:

- `reports.ts:77–100` actually destructures `filters` and `orderBy`, but never
  inserts them into the remote request, despite the API reference listing them
  as options. Their real read must remain recorded. This inventory does not
  establish whether a particular task makes either field deletable or whether a
  promised filtering/sorting behavior constitutes a semantic mismatch.
- `compareDateRanges` performs two separate requests with different ranges and
  `save:false`, then pairs each range with its corresponding result before one
  aggregate save. Member/range identity cannot be dropped through shared values.
- `reindexUrls` and `checkIndexStatus` catch failures per URL, preserve the current
  URL in result rows and save the aggregate. The API-level `requestIndexingBatch`
  also runs sequentially with inner saves disabled, but has no per-item catch.
  Combining these behaviors into one generic loop would change the source.
- API `save` defaults and explicit `save:false` are meaningful. The Skill's broad
  statement that all results auto-save does not erase these actual branches.
- `SKILL.md:53–64` requires reading saved JSON and creating a Markdown summary
  with tables, trends and recommendations. The TypeScript source contains no
  Markdown summary writer or exact saved-file/field selection. This is a separate
  documented obligation, not proof that an invented writer or particular field
  mapping exists.
- `index.ts:364–405` directly prints help under its execution guard. The exported
  functions are independent capabilities; the guard does not run all analyses.

No generated graph has been audited at this snapshot. Later reporting will
separate structural acceptance, source-supported representation, actual
propagation reach and demand/DOE results. Each unobserved layer remains unknown,
not zero. This inventory now waits for the root's graph-ready notification.
