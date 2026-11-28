# Independent review of the lossless source-review display

Review result: no blocking correctness finding in the reviewed implementation. This review inspected code and existing offline receipts; it did not run a model, execute a Skill, run an analysis pipeline, or replay any historical run. Root retains responsibility for offline acceptance and the single authorized fresh GA4 launch.

Reviewed files and SHA-256 values:

- `src/skillflow/document_guided/review_display.py`: `f09b4b67ba191eb42a7be0741d14bfcf77c41ccf84d3d433053de943a5d07cf8`.
- `src/skillflow/document_guided/source_review.py`: `b0c5dde0684a2c3c2fd93d8bb7f944d5cae1910137f26b4b0ca2d0a0a9f71754` (including adaptive whole-presentation selection).
- `src/skillflow/document_guided/runner.py`: `4707dd77ee062fc8f504ba75c3c8d0af5838195b2bf01a434bcb1b16e74030f8`.

## Preservation and collision handling

The display encoder fingerprints exact JSON with object insertion order retained. It does not canonicalize away key order, array occurrence order, numeric distinctions, missing fields, explicit null, conditions, receiver identities, or input paths. Shared definitions replace repeated serialized values; they do not collapse array occurrences or contract checks. The decoder copies referenced values at each occurrence, so the restored obligations do not share mutable aliases.

All dictionaries containing reserved marker keys are escaped before value sharing. Literal `$ref`, `$rows`, and `$literal_object` objects therefore survive, including nested previously encoded displays. Inventory rows retain the exact ordered column set of each record; different field sets distinguish absent fields from explicit null. Row reconstruction treats resulting keys as ordinary data. Literal object reconstruction likewise does not reinterpret the newly reconstructed keys as control markers.

Definitions can reference strictly smaller original subvalues. The program-produced representation consequently has no cyclic reference construction. The decoder separately rejects cycles, missing or mistyped references, ambiguous marker objects, duplicate column sets or column names, malformed row widths or indices, duplicate literal keys, unsupported envelope identities and non-JSON values. It validates unused definitions too. Excessive decode recursion raises an explicit error rather than producing partial material.

## Integration, coordinates and compatibility

`shared-v2` considers wrapping the existing complete logical compact-review payload immediately before rendering. It uses the marked display only when its serialized JSON plus the full legend (including the added newline) is strictly shorter than the ordinary logical JSON. Otherwise it emits the original logical JSON with no legend. The remaining instructions, response format, delimiters and source section are identical to the existing compact view, so this choice cannot enlarge the complete request relative to that view. Equality selects ordinary JSON as well. The codec API itself consistently returns a marked display; this presentation decision belongs to the renderer.

The complete numbered source remains a separate unchanged section and is not an encoder argument. The contract bodies stay in annotation, and the complete inventory remains represented in either presentation. Physical request and response obligations retain separate IDs. When the display is chosen, its legend explicitly requires the normal response schema and expanded logical target coordinates; it warns against using table or envelope positions as review targets. When ordinary JSON is chosen, the unchanged compact-view coordinate instructions apply directly.

Target validation, ownership resolution, contract-check validation, material hashing and review-result identities still operate on the full local logical material. A shared definition cannot itself become a valid review target. The inspected tests cover full and partial material, correction ownership, complete contract inventories and literal marker content.

The original `compact-v1` name remains unchanged, and absent-view legacy material still follows its original rendering and request-failure behavior. The saved material selects its own view. The new default is explicitly `shared-v2`, paired with guided-run identity v12; the unchanged fragment response schema remains v4. Normal stage count, worker count, Task isolation and correction/repair budgets are unchanged in the inspected runner policy. No additional model stage or transport-cap increase was introduced.

## Generality and measured size

Production code contains no GA4 name, source path, fixed operation count, obligation count, scope count, measured request size or special treatment of a historical run. The table paths refer only to the common review-inventory schema. Exact-value sharing and candidate selection use serialized content and character length. The default therefore applies to future Skills and differently sized inventories.

The existing production-codec measurement receipt reports an exact serialized round trip and unchanged source section. Its module hash matches the reviewed module. It measures complete delivery, including the legend and transport envelope, at 903,775 characters versus 1,079,505 before the change, leaving 144,801 characters below the unchanged 1,048,576-character cap. The diagnosis separates the actual transmitted payload from the much larger local audit material; the recorded excess came principally from annotation, mandatory inventory and CFG material, not duplicated full fragments in this particular request.

These are preservation and request-size results. They do not prove that a model will correctly interpret every shared reference or complete every semantic check. The display is visible JSON with an explicit legend, but model usability remains an outcome for the authorized fresh run. Future irreducible material can still exceed the unchanged cap; the implementation must retain the existing explicit pre-start rejection in that case. It contains no truncation, contract omission, automatic splitting or extra semantic request fallback.

## Review evidence and limits

Inspected the production module, the affected renderer and saved-material branches, the runner identity/policy, the new codec and source-review test files, legacy-view tests, transport limit tests, and `size-audit/production-codec-measurement.json` plus `request-size-breakdown.json`. A follow-up static inspection verified the adaptive whole-presentation branch and updated the renderer hash above; no blocking finding was identified. The codec and measured profitable GA4 representation are unchanged by that branch. Test execution and integrated offline acceptance are owned by the implementation/test agents and root; this note does not independently claim those suites passed. No historical artifacts were changed by this review. The only file authored by this reviewer is this note.
