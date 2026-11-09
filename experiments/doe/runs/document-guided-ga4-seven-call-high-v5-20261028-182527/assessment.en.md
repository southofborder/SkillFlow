# GA4 seven-call High: real-run assessment

**The run reached publication of a DOE artifact, but did not produce complete or actionable DOE conclusions.** The selected result is `partial` and `diagnostic_only=true`. All 14 emitted data comparisons remain unresolved under analysis limitations. There are no `excess_supported` or `possible_excess` conclusions. This is not evidence that the Skill is safe or contains no DOE.

This was one fresh run of the program-assembled seven-call workflow, with `gpt-6.1-sol / high / openai`, two dependency workers and no independent user task. The purpose basis was the complete frozen Skill. No old Task, CFG, annotation or answer was reused. The Skill was not installed or executed. No target configuration/monitoring probe or final model polishing call was added.

## Actual outcome and coverage

The selected combination is recorded in [selection.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/selection.json); its annotation is `revision/annotation`, assembled by the program from the three semantic fragments. The artifact and producer checks passed. Successful compilation and graph review are narrower than source-semantic completeness.

| Check | Observed result |
|---|---|
| Pipeline / DOE | `partial` / `partial` |
| Selected source review | Response completed, but diagnostic-only; two material task-correspondence findings remain |
| CFG | 63 blocks, 126 IR instructions |
| Propagation | `incomplete`: 8 processed, 2 unmodeled cutoffs, 116 blocked; 8 saved IR records |
| Processing gaps | 54 source-origin gaps; 50 explicitly unmodeled IRs and 4 precision gaps |
| Known compiled sink positions | 13 declared; 5 resolved, 8 unresolved, 0 processed-with-no-occurrence |
| Resolved sink types | 4 model observations and 1 storage write |
| Demand | `partial`; 51 requirements: 45 partial, 3 unmapped, 3 expressed |
| Demand diagnostics | 59 global blockers: 48 requirement-expression gaps, 4 unbound requirements, 7 Task source issues |
| Sensitivity | `partial`; 21 declarations across 18 scopes; 1 declaration resolved, 20 unresolved |
| DOE data comparisons | 14 `no_excess_established`, all limited; 0 supported excess, 0 possible excess |
| Constraint | The sole check is `not_established`; no preservation entry was produced |

The `5 / 5` resolved-sink table is not full sink coverage: it excludes the eight known unresolved positions. It also cannot enumerate unknown sink contents inside unmodeled IRs. Repeated element occurrences and per-data comparisons are not independent leak counts. Each `no_excess_established` row explicitly states that relevant limitations leave the comparison unresolved; none is a safety verdict or a removal certificate.

Primary evidence: [propagation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/propagation/manifest.json), [demand support](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/doe/audit/demand-support.json), [DOE result](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/doe/doe-result.json), and [machine-readable completion audit](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/outcome-audit.json).

## Where propagation actually stopped

Only two of the 50 declared unmodeled IRs were reached as cutoffs. The other 48 were already blocked by upstream coverage. Describing this run as 50 separately encountered cache failures would be incorrect.

* **`ir_003`, import/evaluate the selected interface:** this block has 54 outgoing edges; its cutoff blocks 115 successor instructions. It combines interface acquisition, dependency initialization, `dotenv.config()` and the facade help predicate. [settings.ts:5](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/scripts/src/config/settings.ts:5) imports dotenv and calls `config()` at line 9; [index.ts:12](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/scripts/src/index.ts:12) begins module imports and re-exports. The namespace result can be represented opaquely, but its creation is combined with environment effects whose post-state was not modeled. A pure receive/no-op replacement would conceal those effects. This is a granularity and initialization-modeling barrier, not an observed failure in the later client-cache getter.
* **`ir_005`, documented direct execution:** its cutoff blocks one subsequent instruction in that block. [index.ts:365](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/scripts/src/index.ts:365) supplies an explicit predicate and a literal help output. Existing CFG branching can in principle separate the printing and non-printing paths. Keeping them inside one atomic `execute_code` instruction leaves a guarded-delivery gap; pretending that the entire action is a pure opaque computation would not repair its side effects or initialization dependency.

Later cached-client creation, throwing paths, conditional saves and caught-error relations remain separately declared limitations. Resolving the two early cutoffs would expose these later paths; it would not automatically solve them. Missing concrete runtime values or an actual API response should also be distinguished from representation limits: static opaque acquisitions can retain unknown values, while unknown mandatory state changes cannot be silently discarded under the current cutoff policy.

## Remaining semantic errors

The final independent source review retains two findings, both owned by task-correspondence. Read-only source checks support them:

1. **F001 — actual whole-response propagation was promoted to whole-response necessity.** [SKILL.md:70](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/SKILL.md:70) names the required analysis content and associations. [index.ts:55](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/scripts/src/index.ts:55) and [index.ts:235](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/scripts/src/index.ts:235) really do place whole child responses into composite objects, save them and return them. This establishes the implemented data flow; it does not establish that every opaque response member is necessary at every receiver. Persistence obligations must be considered at their own receivers.
2. **F002 — summary input was assigned whole-value preservation.** [SKILL.md:63](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/source/inputs/package/SKILL.md:63) requires reading saved JSON and producing tables, trends and recommendations. It does not require every acquired field to enter the summary receiver. The executable demand for `ir_123` still preserves the whole input; nearby prose about omitting fields from Markdown cannot narrow that demand.

These errors can suppress DOE detection even after propagation improves. Fixing them must not automatically shrink actual propagation or invent a missing field mapping. The source review successfully identified them, but the single shared repair round was already consumed; they therefore remain in the selected diagnostic result. See [final review](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/revision/review/result.json).

## Requests, structural failures and repair

The nominal seven-call path was exercised, including program assembly with zero annotation-generation calls. Actual execution required **17 CLI model requests**:

| Request category | Count | Public input tokens | Public output tokens | Input + output |
|---|---:|---:|---:|---:|
| Normal semantic stages | 7 | 649,725 | 103,450 | 753,175 |
| Shared semantic repair | 6 | 606,895 | 78,497 | 685,392 |
| Structural corrections | 4 | 282,701 | 36,667 | 319,368 |
| Total | **17** | **1,539,321** | **218,614** | **1,757,935** |

The initial pass used 10 requests, including three corrections. Its review found one Task, two CFG and six annotation problems, triggering the single shared Task + CFG dependency closure. That closure used six semantic requests and one additional structural correction. Task/flow, Task/CFG repair and task-correspondence/sensitivity ran concurrently within the two-worker limit.

Observed format/reference failures, with all raw answers preserved:

* Initial processing omitted 62 control terminators: 6 dispatch and 56 return instructions. The full 124-ID graph was present in both the saved view and the actual delivered prompt. The generic fragment schema and initial output instructions did not explicitly state that control terminators also require coverage. One whole-object correction supplied complete coverage.
* Initial sensitivity had one invalid nested scope. Its correction fixed that record, after which 29 additional reference/scope errors became visible. Sixteen valid declarations were retained and the stage was marked partial. This shows that the intended early error aggregation did not expose all cross-reference errors before the first correction. The rebuilt sensitivity later passed on its first response with 21 declarations.
* Initial task-correspondence used an unsupported nested `each` demand path. One record correction passed.
* Revision-processing supplied 22 of 126 required IRs. The complete new CFG and previous complete fragment were delivered. The repair context was target-oriented, but did not explicitly require a complete replacement covering the current graph. The program expected a new whole fragment, not an implicit merge across CFG versions. One whole-object correction passed. The evidence establishes a coverage/contract failure and a prompt-clarity weakness, not loss of records by the adapter or inability to represent every omitted operation.

There were five structurally invalid response artifacts across those chains; the second invalid sensitivity response was retained and partially isolated, not retried again. No second semantic-repair round or manual target feedback was added. No top-level `cannot_assess` branch was used. Its removal did not eliminate local unknowns or create complete analysis.

## Time and cost scope

| Measurement | Observed |
|---|---:|
| Start / main analysis end, China time | 2026-10-28 18:28:25 / 19:46:33 |
| Main analysis wall time | **4,688.206 s — 78 min 8.21 s** |
| Native durations summed, including parallel overlap | 5,004.640 s — 83 min 24.64 s |
| First native start to last native completion | 4,170.944 s — 69 min 30.94 s |
| Last native completion to analysis end | 516.325 s — 8 min 36.32 s |
| Propagation stage | 153.223 s |
| DOE stage | 361.477 s |
| Subsequent offline replay | 462.097 s — 7 min 42.10 s; zero new model requests |
| Controller lifetime through verification | 5,150.621 s — 85 min 50.62 s |
| Cached input, a subset of input | 381,824 tokens |
| Reported reasoning output, a subset of output | 54,261 tokens |

The independent passive recount exactly matches [metrics.json](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/metrics.json). All 17 public turns have complete input/output and reported detail fields; no public usage duplication, unknown duration or unknown native start was found. Raw events do not contain a total field: the total above is derived as input + output. Cached input and reasoning output are not added again.

**There was an internal CLI reconnect.** Initial processing emitted `Reconnecting... 2/5 (request timed out)` and eventually returned a complete answer. The outer Client launched no extra network attempts. Those are different accounting levels. The actual HTTP attempt count and any separately unreported consumption of the failed internal attempt remain unknown. The public token total is verifiable completed-turn usage, not a verified complete bill; no currency amount is inferred. Preparation, coding/assessment assistant effort and human review time are not measured by this target-call ledger.

Against the preceding eight-call High run on the same frozen 16-file source package, observed CLI starts fell from 18 to 17, but public tokens rose from 1,525,001 to 1,757,935 (**+15.27%**) and main wall time rose from 65 min 56.43 s to 78 min 8.21 s (**+18.50%**). **This run does not demonstrate acceleration.** The older run produced no DOE, while this one computed a partial propagation/DOE artifact; prompts, derived analysis and workflow changed, and this run contains an internal reconnect. These observations do not isolate the causal effect of reducing the fixed call count. No direct-GPT comparison was run here.

## Reproducibility and immediate priorities

All 17 actual request records and launch arguments specify `gpt-6.1-sol / high / openai`; they use the same recorded CLI executable, whose current hash matches the protocol. Public streams contain 17 distinct threads, one completed turn and one agent-message item each, and no tool/delegation items. No hidden reasoning text was exported. No answer was overwritten, manually replaced or regenerated outside the declared correction and shared-repair policies.

The source freeze is `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`: 16 readable files, 155,170 UTF-8 bytes. The implementation snapshot and end-of-run check both equal `27c96eafa74c9c1f957df4116369198981f72833dd69d28b18ded84bf4c835d8`. [Replay](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/replay-check.json) matched the saved result, added zero native markers and did not convert the partial result into a complete one. The controller is closed.

The next small changes should address observed failures rather than add another generic execution engine: make complete-replacement versus record-correction contracts explicit for all fragments; aggregate record typing and cross-reference errors before spending the one correction; separate the known import/help boundaries from initialization gaps; and correct whole-payload necessity at the task-correspondence layer. Genuine external-state and downstream cache limitations must remain visible. No further implementation change or real run was performed during this assessment.

The seven-call plumbing, independent branches, program assembly, valid-record retention and replay worked. The empirical goal of complete DOE on this complex Skill did not. The current evidence establishes neither a practical advantage over direct GPT nor the absence of future value in the method.

Artifacts: [run summary and per-request accounting](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/run-summary.json), [protocol](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/run-protocol.json), [final DOE](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/doe/doe-result.json), [generated DOE view](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/doe/report.html), [implementation check](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-seven-call-high-v5-20261028-182527/implementation-check.json).
