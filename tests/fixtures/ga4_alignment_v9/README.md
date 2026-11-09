# GA4 v9 alignment regression source snapshots

These ten files are byte-identical extracts of the full sixteen-file frozen
GA4 v8 package. `provenance.json` records the original directory and every file
SHA-256. Tests verify the copied bytes before constructing materials. They do
not import old answers, resume a run, replay historical data, call a model, or
execute TypeScript. The original source and runs are not modified.

Authored candidates are in
`tests/document_guided/ga4_alignment_v9_cases.py`; assertions are in
`tests/document_guided/test_ga4_alignment_v9.py`. These are finite boundary
projections used to test the compiler and deterministic analysis. They are not
an alternative implementation of GA4, a complete GA4 CFG, or evidence that a
model independently generates the corrected forms.

| Regression | Source basis | Deliberate scope |
|---|---|---|
| Public URLs, normalization, filter and early empty return | `api/bulk-lookup.ts:64–99,149–190` | Existing client normal path; unknown trim/slash values remain opaque; duplicate and empty occurrences stay exact |
| Nested inspection request, source result projection and undefined | `api/indexing.ts:146–193` | Normal response/save path; field fallbacks keep their real inputs but are not a JavaScript evaluator |
| dotenv and getSettings versions | `config/settings.ts:5–9,40–48` | Normal config return; possible environment update remains separate from config's return; unknown precedence and overwritten keys are not solved |
| Cache and clock | `core/client.ts:67–122`; `api/indexing.ts:57–79` | Existing versus newly created indexing client; same read/write location; fallback clock is a separate acquisition; no exact cross-call cache executor |
| Protected errors, batch and catch-and-continue | Existing `ga4_boundary_cases` snapshots, `api/indexing.ts:89–105`, `index.ts:301–346` | Existing bounded cases preserve real protected-call exception sources and per-occurrence alternatives; no general exception executor |
| Comparison passed to saveResult | `index.ts:171–203`; `core/storage.ts:55–92` | Existing category directory normal path; actual period reports enter the metadata/data wrapper; filename/serialization remain abstract |
| Nested row value paths | `api/reports.ts:33–42` | Original nested row structure plus an **explicit synthetic consumer declaration**, separately identified as `ROW-CONSUMER-VARIANT.md` |
| Discovery versus whole metadata | `api/metadata.ts:38–55,81–95`; `references/api-reference.md:165–193` | Field-limited discovery requirement versus real full metadata requirement |
| Positive DOE and necessary-use negative | Same metadata boundaries plus `SENSITIVE-VARIANT.md` | **Explicit synthetic privateToken declaration**, not a claim that original GA4 metadata contains a sensitive field |

The ordinary save fixtures project a logical payload boundary rather than
claiming to execute `JSON.stringify`. The comparison fixture additionally
preserves the actual saved wrapper fields and returns a distinct generated
filepath. The filename's dynamic resolution is left symbolic.

The batch tests preserve source occurrence selectors and a value demand on
the whole result array when that whole result is required by source. There is
no new `preserve=order` property. An independent order-only requirement cannot
be silently rewritten as a whole-value demand, and is not proved by this
regression suite. Natural-language case conditions remain possible branches.

All fixtures and audit labels stay outside online target input packages.
