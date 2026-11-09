# 013 source-fetch-with-fallback: backend-r3 online assessment

Propagation is incomplete: 19/27 generated IR were processed, four status-file writes were cut off as unmodeled, and four following returns were blocked. A partial DOE was saved, but all 13 sensitive-data comparisons are explicitly unresolved. The reached request/response and credential boundaries provide useful partial lineage; the run does not establish a complete return/status workflow or an actionable DOE verdict.

The fresh run used `gpt-6.1-sol / high / openai`, two workers and the same frozen source. It selected the initial graph and annotation, with no semantic repair. The controller has closed and its sole zero-call replay matched. The incomplete result was produced quickly by the backend; this is not a convergence stall.

## Specific propagation blocker

The four unmodeled sites are `ir_014`, `ir_018`, `ir_022` and `ir_026`, the status-log append operations on the terminal outcome branches. Their following returns, `ir_015`, `ir_019`, `ir_023` and `ir_027`, are blocked. There are zero `unresolved_binding`, not-reached or not-solved IR. Four unmodeled declarations correspond to four actually reached cutoffs in this case.

The CFG assigns each write a public output representing the entire post-append file: `result_008`, `result_011`, `result_014` and `result_017`. These four outputs have no CFG consumers. Source line 16 requires appending the status, not returning or rereading the entire updated file. The existing write operation can express `mode: append` and record the state change, but it has no result slot that processing can bind to those public whole-file values.

The model's inability to bind the current CFG outputs is therefore a real mismatch under that graph, while the implication that ordinary append cannot be analyzed is too broad. The primary failure is CFG/processing alignment: unused post-write public outputs turn an expressible side effect into an unmodeled IR. A conceptually smaller representation would omit those unused outputs and retain the append side effect. No replacement was compiled, executed or substituted during this audit, so that observation is not evidence that an edited candidate has completed.

The unified review returned no findings and did not trigger the available semantic repair. It missed this specific alignment issue. The remedy would require CFG ownership, not just a new processing local or an invented read. This audit does not alter the frozen implementation or candidate.

## Coverage, DOE and evidence limits

| Measure | Actual result |
|---|---|
| Generated IR processed | 19/27, 70.37% |
| Unmodeled cutoffs / downstream blocked | 4 / 4 |
| Saved sink positions | 21: 18 contract-default model observations and 3 external-tool boundaries |
| Status-file append completion | 0/4 terminal branches |
| Terminal return completion | 0/4 terminal branches |
| Sensitive declarations | 1/1 resolved |
| Sensitive comparisons | 13, all unresolved / `no_excess_established` |
| Established excess / actionable reductions | 0 / 0 |

Source acquisition is recorded at 2/2 sites, requests/responses at 3/3 sites, and corresponding body/error projections at 4/4 paths. The first and retry fast responses have distinct IDs. Both fast requests retain the same actual source_id and FAST_KEY versions; archive receives only the original source_id. Body/error and status projections retain their respective acquired outcome. These facts are useful even though all four actual returns remain blocked.

Static tool sites and alternative paths are not dynamic call counts. Default model observations are contract possibilities, separate from explicit tool arguments. The source review and [independent source audit](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/013-source-audit/source-audit.md) must not be replaced by the generated-IR percentage. The audit's exact Data/receiver/version evidence is recorded in [source-audit.json](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/013-source-audit/source-audit.json).

In addition to the cutoff, task-correspondence retains a reference error: R3's `only_if` condition uses a raw `segments/ops/expression` path rather than an indexed normalized-expression target. Constraint/requirement gaps and source limits remain. The saved DOE contains four upstream diagnostics, eight upstream-coverage entries, eight processing gaps, six requirement-expression gaps, two task-source issues and one unbound requirement. These are distinct diagnostics, not 29 independent source defects.

All 13 comparison reasons explicitly state that relevant limitations leave the comparison unresolved, neither a safe verdict nor evidence of removable content; all reductions are null. All ten constraint checks are `not_established`, including the declared archive-specific prohibition despite its recorded request excluding the key. No published excess claim was contradicted, because none was made. No source accuracy, precision or recall score follows from these unresolved comparisons.

## Actual calls, public tokens and time

| Measure | Value |
|---|---:|
| Actual native starts | 9 |
| Normal semantic requests | 7 |
| Structural corrections | 2: processing and task-correspondence |
| Shared semantic repair / extra transport attempts | 0 / 0 |
| Input tokens | 226,576 |
| Cached input, included in input | 106,368 |
| Output tokens | 28,752 |
| Total public tokens | 255,328 |
| Complete / partial / unknown final-response usage | 9 / 0 / 0 |
| Main analysis | 816.010 s, 13 min 36.01 s |
| Public native start-to-finish span | 807.025 s |
| Propagation compute / save / total | 0.244 / 1.546 / 2.314 s |
| DOE load / compute / post-compute publication | 1.281 / 2.160 / 1.242 s |
| DOE total | 4.806 s |
| Sole matched replay, zero new starts | 21.840 s |
| Controller wall including replay | 838.836 s |

Component intervals are nested and nonadditive. Per-stage wall times and category costs are preserved in [run-summary.json](run-summary.json); parallel stages overlap. All accepted public response identities have known usage, while provider-internal HTTP attempts and unreported internal failed-attempt usage remain unknown. No monetary cost or assistant-audit usage is fabricated.

## Scope-aware comparison and artifacts

Old v8 013 processed 15/26 IR, with one cutoff and ten blocked. The first/retry fast terminal outcomes were blocked, while two archive terminal branches were reached. It used 13 starts, 375,925 public tokens and 940.263 s. This run uses 9 starts, 255,328 tokens and 816.010 s, but all four status writes/returns are now blocked. More processed IR with different lost terminal coverage is not uniformly better completion, and lower cost is not evidence of a complete-flow speedup. Paused v9 remains a nonterminal old run, not a completed comparison.

- [Structured assessment](run-summary.json), [mechanical metrics](mechanical-evidence.json).
- [Propagation records](propagation/records.json), [DOE result](doe/doe-result.json), [unified review](review/result.json).
- [Public metrics](metrics.json), [component timing](component-timing.json), [sole replay](replay-check.json).

The implementation check remains unchanged. Python SHA is `5ccbc1941be908ff20b15d7a56a631e678285b42a255031d29505ec6a0495637`, broader provenance SHA `9ae31392bf97b0ae8c5ae75c48d1994e8b303b68cda6d532eb4b96f508c56703`, source SHA `fd57bfb1f4c45a3d6d22f015bfcf9cf9f86f812c01d523c996918540bef606da`. This report uses saved source/JSON only, without new calls, replay or Skill execution.
