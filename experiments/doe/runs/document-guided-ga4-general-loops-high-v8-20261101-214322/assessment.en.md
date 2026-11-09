# GA4 v8 online validation: closed-run assessment

**The run closed, but did not complete the main data propagation or produce a useful substantive DOE conclusion.** It saved a reproducible partial diagnostic result: 29 of 420 IR processed, 5 visited unmodeled cutoffs and 386 blocked IR. No sink-level necessity/sensitivity comparison was computed. The sole replay matched with zero new model starts.

This is the one authorized fresh 16-file GA4 run, requested as `gpt-6.1-sol / high / openai` with two workers. The implementation and source remained unchanged during analysis and replay. All 18 requests consistently used that configuration; public transport logs do not independently attest backend model configuration. No Skill code was executed. Reports for the three authorized small Skills are separate.

## Actual coverage

| Measure | Actual result | Interpretation |
|---|---:|---|
| Selected CFG | 420 IR; 194 blocks; 285 edges | Generated representation, not source coverage |
| Compiled processing present | 372/420 (88.57%) | Annotation coverage, not successful propagation |
| Source-declared unmodeled IR | 48/420 | Five reached as cutoffs; 43 blocked upstream |
| Actually processed IR | **29/420 (6.90%)** | Setup/module/help prefix and control records |
| Visited unmodeled / blocked | 5 / 386 | Main API, persistence and loop paths unresolved |
| Source remote API positions resolved | **0/13** | Static call sites, not runtime invocation counts |
| Source `saveResult` positions resolved | **0/25** | Shared storage implementation is not a 26th site |
| Explicit source `for-of` loop sites propagated | **0/3** | No online validation of these loops was reached |
| Sensitivity declarations resolved | **0/57** across 23 declared scopes | Missing propagation, not absence of sensitivity |
| Compiled boundary coordinates unresolved | 14:9 network, 3 model observation, 2 storage | Different denominator from source call sites |

All 13 API, 25 save and 3 loop source positions have candidate-family mappings, but candidate presence is not correct modeling or propagated coverage. The run has no real nested, retry or pagination source-loop case; it cannot validate those capabilities online. The selected propagation has 29 records and 35 Data objects, with no resolved sink records. Reached setup/module/help tool-delivery operations have `effect:null`; therefore `sinks=[]` also cannot be read as no delivery. Source and generated-IR denominators must remain separate.

[Complete source-site mappings and evidence](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-coverage.md); [machine-readable mappings](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-coverage.json).

## Where the main flow stopped

| First visited cutoff | Representation problem | Layer |
|---|---|---|
| ir_019 | dotenv internal uncertainty expanded into an unmodeled whole boundary | Processing abstraction; real library-precision limits also remain |
| ir_035 / ir_039 | Internal invocation is split in CFG but its completion is not linked for processing | CFG/processing alignment |
| ir_053 | Parameter binder has no actual CFG inputs | CFG operand linkage |
| ir_419 | Exception completion merge lacks some real originating operands | CFG/processing alignment |

The earlier independent 48 IR audit classified 43 primary CFG/processing mismatches, 4 overbroad unsupported judgments and 1 mixed boundary/source-precision gap. These were source-unmodeled declarations, not 48 schema-rejected records. The full frozen package is intact, but downstream SOURCE views omitted known function bodies, including `getAvailableFields` and part of `inspectUrl`; summaries did not replace that source evidence. The actual solver honored explicit cutoff semantics and returned. This result is not evidence of a live nonconvergent loop: all three inventoried source loops were blocked before propagation.

[48 IR source/interface audit](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/unmodeled-ir-audit/assessment.en.md).

## DOE usefulness and source correctness

A `doe-result.json` exists with `status:partial`, but it contains **zero substantive sink judgments**. Demand and sensitivity derivations and computed constraint results are empty. The 46 Task realization records are 45 partial and 1 unmapped. The 787 diagnostics overlap causal gaps and affected positions; they are not 787 independent bugs or privacy findings. `expected_sinks=0` describes the generated resolved inventory, not the Skill source.

There are 0 supported and 0 contradicted emitted DOE conclusions, with an emitted-judgment denominator of 0. The 14 unresolved declared boundaries are not 14 negative judgments. DOE accuracy, precision and recall are **not estimable** here. This result is useful for failure localization, but does not determine which actual sensitive payloads are unnecessary.

The final source-review request completed and retained 10 issues: 2 CFG, 5 processing and 3 task-correspondence issues. Fresh independent source checking corroborated the 10 core defect statements, while finding one localization error: F002 points at `block_084/instructions/1` (dispatch ir_170); the bad request construction is at `instructions/0` (ir_169). Its top-level `inspectionUrl/siteUrl` conflicts with source `requestBody` nesting. This correction is recorded only in the audit, preserving the original review.

Other concrete defects include filter/client initialization order, aggregate-cache reads versus separately written cache locations, missing per-member client acquisition effects, a known inspection response projection classified as unavailable, missing GA4 row-value demands, and overly broad discovery-result demands. Real whole-metadata requirements remain distinct. These source findings are not an end-to-end DOE accuracy score. Assistant source criteria are exploratory, not human gold.

[Independent DOE/source review with exact source ranges](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-doe.md); [structured evidence](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-doe.json).

## Calls, tokens and wall time

| Request category | Actual starts | Public tokens |
|---|---:|---:|
| Normal semantic requests |7|779,488|
| Shared semantic repair and dependent rebuilding |6|888,604|
| Structural corrections |5|641,085|
| **Total** |**18**|**2,309,177**|

Known public usage is 1,981,141 input tokens, including 928,512 cached-input tokens, plus 328,036 output tokens. The 62,953 reasoning-output tokens are an output subset, not additional consumption. Corrections and repair account for 66.24% of public tokens; that allocation does not prove all such work was avoidable. All 18 accepted finals have complete public usage, and saved answer/delivery hashes reconcile. Zero outer network retries were launched.

**Six internal reconnect events** occurred: initial and revised review each recorded 2/5, 3/5 and 4/5 reconnect messages with OS 10054. Both ultimately returned accepted complete answers. Exact provider HTTP attempts and any additional unreported failed-attempt usage remain unknown. Public logs expose 18 unique CLI thread/turn identities, no provider response IDs and no recorded tool/delegation items. No currency amount, human review time or complete research/auditing cost is inferred.

| Time measure | Actual duration |
|---|---:|
| Main analysis |3 h 34 m 44.53 s (12,884.53026 s)|
| Propagation stage, included above |38 m 51.87 s (2,331.873455 s)|
| DOE stage, included above |43 m 39.58 s (2,619.58253 s)|
| Sole zero-model replay |54 m 10.07 s (3,250.0749269 s)|
| Controller start through closure |4 h 28 m 55.26 s (16,135.258536 s)|

Analysis ran from 2026-11-01 21:44:56 to 2026-11-02 01:19:40 China time; controller/replay closure was 02:13:51. Stage clocks include validation, reconstruction and saving; they are not solver-only measurements, and parallel-stage durations overlap. Four successful nonblocking stack samples during the propagation stage found that core calculation had already returned and the process was reconstructing/validating annotation for saving. The previously reported 185 full expansions is a conditional static path lower bound, not a measured execution count.

[Full accounting, per-request usage and stage timing](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-cost-protocol.md); [structured accounting](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/ga4-cost-protocol.json); [separate performance audit](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/propagation-performance-audit/assessment.en.md).

## Scope-aware comparison and preserved evidence

| Run | Actual propagation/DOE scope | Starts | Public tokens | Main seconds |
|---|---|---:|---:|---:|
| v5 |8/126 IR; 5 resolved/8 unresolved sink positions; 14 unresolved/no-excess-established comparisons |17|1,757,935|4,688.20623|
| v7 |262 IR not solved; DOE raised missing member-scope error; no DOE file |17|2,184,745|7,902.34070|
| v8 |29/420 IR; 0 resolved sink judgments; partial diagnostic DOE saved |18|2,309,177|12,884.53026|

v8 uses 5.70% more public tokens and 63.05% more main time than v7; compared with v5, increases are 31.36% and 174.83%. Graph size and achieved scope differ. Saving diagnostic DOE and a matching full replay improves failure handling relative to v7, but does not establish complete analysis, acceleration, accuracy or an advantage over direct GPT. Historical failures remain unchanged.

The sole replay matched with 0 new native starts. Source SHA-256 is `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`; implementation SHA-256 is `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`, unchanged. Frozen source, raw answers, corrections, retained review findings and failure markers were not rewritten. Audits used saved JSON and source, without invoking loaders, compilers, solvers, another replay or targets.

[Structured run summary](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/run-summary.json); [actual propagation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/propagation/manifest.json); [actual DOE result](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/doe/doe-result.json); [replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-general-loops-high-v8-20261101-214322/replay-check.json).

This assessment is one part of the authorized GA4 plus three-small-Skill validation. Redundant verification/reconstruction simplification is a separate follow-up, authorized after all four result/cost reports are delivered. No such changes were used for this result. That simplification can reduce local overhead, while the source/CFG/processing blockers identified above still require semantic alignment.
