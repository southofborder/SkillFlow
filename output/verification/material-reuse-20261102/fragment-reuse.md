# Fragment validation and sensitivity projection reuse

The change reuses one checked processing expansion within each fragment validation or assembly. It does not persist cached state or add model fields, protocols or stages. Public `validate_fragment`, `assemble_fragments` and `expand_processing` return shapes remain unchanged.

The existing case/local-reference lowering now supplies short-lived alias and member-scope tables when processing is expanded. Sensitivity declarations use these same tables, then undergo their existing scope/reference/source-evidence checks. They no longer copy and expand the complete processing fragment once per declaration. Mapping and sensitivity validation inside assembly share the already checked processing base. Mapping validation and final full combined compilation remain.

For a synthetic two-IR case fixture with 13 sensitivity declarations, full expansions fell from 18 to 3. Three measured assembly runs had median duration 0.8685 seconds before and 0.2537 seconds after. Full wire/raw/compiled/coordinate-map hashes were identical. Both benchmark sides used the same current CFG index and flat lowering; the before side loaded the saved former fragment validator. This isolates fragment reuse and is not an estimate of online latency or token savings.

The focused suite passed 65 tests. Nine new cases check constant expansion counts for 1, 13 and 40 declarations, identical full compilation, member/case projection against the original full-expansion path, separate duplicate occurrences and response identities, local non-observation, unchanged source scopes and error coordinates, input immutability, and rejection of changed material on a separate call. Existing case pipeline and DOE member tests also pass. Two initial new-test assertions were corrected to match established record ordering and schema diagnostics; the initial failures remain described in fragment-acceptance.json.

No source relationship, data version, candidate/occurrence identity, local return, boundary receiver, uncertainty or model ownership is changed. The existing historical runs and failure records were not modified, loaded through a backend, or replayed. The optimization does not solve the semantic CFG/processing mismatches observed in those runs.

Artifacts: fragment-benchmark.json, fragment-tests.xml, fragment-acceptance.json. Exact pre-edit files are retained under before/src/skillflow/document_guided/.
