# Accepted Task and source correspondence

This passive audit examines the current run's accepted `task/task.json` against
the same complete frozen source. The saved Task result is complete, its first
call `calls/task/a001` has saved validation status `valid`, and there was no Task
structural correction. Task SHA-256 is
`5db95526cac4f51cf151d7b48cee8d895f7fea1f9a89b4691bad26a9b90525b9`;
its source identity matches the fresh source inventory. Saved acceptance is not
a claim that every intended behavior is implemented or that whole-chain semantic
review has completed.

The Task contains 52 requirements and 10 interpretation issues: seven marked
resolved and three unresolved with specific source conflicts. The requirements
describe intended outputs, actions and conditions independently of any CFG IDs.
`analysis-results` applies API functions to the requested analysis, while the
remaining named capabilities retain their individual deliverables. The count
does not mean all capabilities must execute during one invocation.

The accepted Task preserves these consequential source distinctions:

- `save-by-default` retains automatic JSON saving as the default and honors
  `save=false` on functions exposing the option. `combined-result-storage`
  suppresses component saves for comparison and relevant batch operations while
  retaining the aggregate save under the operation's actual save behavior.
- `save-result` describes the public storage function's wrapper and returned
  filepath. That return is not a requirement for each internal save caller to
  observe or retain it: all 25 inventoried internal callers discard it.
- `summary-input` requires reading saved JSON, and `summary-output` requires
  Markdown tables, trends and recommendations under `results/summaries/`.
  The `summary-trigger` issue gives a concrete reason for treating the direct
  three-phase workflow as authoritative rather than requiring an additional
  user-trigger condition inferred from a tip. This settles the Task
  interpretation; it does not supply the absent implementation or an exact
  saved-file/field-to-summary mapping.
- `compare-periods` preserves first/second range-to-result pairing and shared
  dimensions/metrics. The high-level indexing requirements preserve URL-member
  association and per-URL errors while continuing. Low-level batch indexing
  explicitly conditions its ordered result on successful completion and does
  not invent the high-level catch behavior.
- Empty bulk lookup returns zero rows without a remote request or save.
  Dimension/metric listings require all entries and named descriptive fields;
  the separate full-metadata requirement explicitly asks for the full response.
  These are distinct output scopes for later demand selection.

The Task correctly retains documented custom-report filters and sort order,
while `ga4-filter-and-sort` records that the actual implementation reads these
options but omits them from its request. A `resolved` interpretation here does
not mean the implementation discrepancy is repaired. Similarly,
`latest-operation-match` retains the documented operation-specific selector
despite the implementation's substring match. Later analysis must report such
mismatches rather than deleting intended output obligations to make the observed
code appear sufficient.

The three unresolved issues are localized: calendar-month versus illustrated
rolling-period meaning for an unqualified comparison; conflicting clicks versus
impressions ranking for the shared top-pages function; and query-by-device
association versus two separate reports for keyword analysis. Each names the
affected requirements, source locations and the semantic difference that matters.
None uses opacity or absent execution as its reason, and none justifies making
unrelated Task obligations unresolved.

One concrete evidence-location defect remains in `combined-result-storage`:

| Evidence range in `skill/scripts/src/index.ts` | Actual aggregate save |
| --- | --- |
| 178–199 | line 200, comparison |
| 304–315 | line 316, re-index aggregate |
| 327–342 | line 343, index-status aggregate |

The cited reasons say those ranges store the combined results, but each range
ends immediately before the relevant save statement. The requirement itself is
supported by the complete source. This is a precise locator correction for
source review, not evidence of a missing operation or a reason to discard the
Task. Extending those end lines to 200, 316 and 343 would include the statements.
This audit leaves the accepted Task and run artifacts unchanged.

Exact selected requirements, issues, finding locations and saved artifact hashes
are in `accepted-task-source-audit.json`. No compiler, Task validator, analysis
engine, model, Skill or replay was invoked. Generated CFG source faithfulness,
demand seeds, contract review, propagation reach and DOE remain separate layers
to assess when their current-run artifacts exist.
