# Frozen GA4 modeling limitations retained by the backend comparison

This is an assistant inspection of the copied input, not a new target answer,
human gold label, or measurement of completed propagation. The fixed input SHA-256
is `9c75db1428450c1bb5593b75b40b17d6c9e3d47d1efbcaca793f2fc026a960a4`.
The frozen source text was not changed. The backend comparison must preserve these
limitations rather than silently supplying new processing semantics.

## Explicitly unmodeled instructions

- `block_017 / ir_029`: the selected analyst analysis call lacks the selected
  function's instantiated input, result and side-effect relations. The relevant
  gap is `/payload/processing_gaps/2`, with `unmodeled=true`, `outputs=[0]`, and
  `control=true`. R05 retains the corresponding requirement gap. `SKILL.md:55`
  describes analysis followed by saving and reading results; the distinct exports
  in `scripts/src/index.ts:55–361` do not identify the actual selected call merely
  by being present elsewhere in the graph. Its return is not a saved-path identity.
- `block_152 / ir_301`: recursive directory creation is not represented as a
  filesystem-structure update. The gap is `/payload/processing_gaps/28`, with
  `unmodeled=true` and location `directory`. `scripts/src/core/storage.ts:67`
  checks existence before `mkdirSync`; the existing-directory route bypasses
  `ir_301` and reaches the later wrapper, serialization and file-write operations.
  This is a gap on the missing-directory route, not evidence that every save is
  unmodeled. R08 retains cwd/path and filename-collision uncertainty; R10 retains
  the real requirement to save the complete supplied result.

## Reindexing loop and bounded outcomes

`block_119 / ir_238` is `capture_reindex_try_completion`. Its existing gap is
`/payload/processing_gaps/21`. The loop includes `ir_230` merge, `ir_232` member,
`ir_238` bounded try, success/error collection at `ir_240` or `ir_242–243`,
`ir_252` merge, and the aggregate save at `ir_255` after loop exit.

`scripts/src/index.ts:301` calls `requestIndexing(url, {save:false})` per member;
`scripts/src/api/indexing.ts:57` obtains the client, publishes, and projects the
response. The fixed four cases distinguish normal return, pre-request failure,
request failure, and failure after response acquisition. The normal case calls
`notification_helper`; its caller-specific publish, projection, and client-state
effects are not instantiated. Explicit `network_send` templates within `ir_238`
occur in request-failure event 9 and after-response event 13. Their presence does
not establish complete normal-call network behavior.

The source spreads `...result` after its initial `url` field. The returned
notification URL may therefore replace the input URL. Occurrence pairing must be
preserved without claiming that every saved record contains the original URL.
The per-member `save:false` also does not cancel the batch save outside the member
catch. A failure of that final save can prevent normal return.

## Input-wide scope

The selected input contains 36 processing gaps, including the two explicitly
unmodeled instructions above. Of 50 Task realizations, 45 are partial, one is
retained-only, one is unmapped, and three are expressed (R17, R18 and R39): 47
realizations retain gaps. Six Task source issues remain unresolved. Only two
structured constraints are supplied, both `requires_prior`: `ir_282 → ir_288`
for R04 and `ir_305 → ir_306` for R10.

These counts describe the frozen model. Actual processed/blocked instructions,
resolved boundaries, sensitive comparisons, DOE findings and limitations must be
read from the new offline worker result. A faster completed backend does not by
itself resolve these source/model relationships or establish absence of DOE.
