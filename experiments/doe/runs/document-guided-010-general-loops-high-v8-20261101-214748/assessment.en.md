# 010 catalog-query: v8 online validation

**The run closed with useful partial request/response propagation, but it did not finish the required file write and items return. It emitted no substantive sensitive-data DOE comparison.** The useful prefix preserves all four optional-argument alternatives and the corresponding `index.search` responses. The missing completion is explicit: 19 of 23 IR processed, one source-unmodeled write and three downstream blocked IR. The sole zero-model replay matched.

This fresh development-case run requested `gpt-6.1-sol / high / openai`, with two workers, seven normal semantic requests, one structural correction per stage and one shared semantic repair round. All three frozen source files match the pre-run inventory; source and implementation were unchanged. No historical Task, CFG or answer was imported, and no Skill code was executed.

## Actual coverage and useful results

| Measure | Actual result |
|---|---:|
| Generated CFG | 23 IR, 11 blocks, 12 edges |
| Compiled processing | 22 / 23 IR |
| Actually processed | **19 / 23 (82.61%)** |
| Source-unmodeled cutoff / downstream blocked | 1 / 3 |
| Request-file acquisition | **1 / 1 source position resolved** |
| Search request and response | **1 / 1 source call position resolved** |
| Count-file persistence | **0 / 1** |
| Unchanged items return | **0 / 1** |
| Saved propagation | 19 records, 26 Data objects |
| Resolved sink positions | 13: 12 model observations and 1 external-tool delivery |
| Unresolved compiled sink coordinates | 1: model observation at ir_022 |

The last inventory is incomplete as a source census: `ir_020` has no modeled write operation, so the required `count.txt` storage boundary is absent from the compiled sink list altogether. It remains an unresolved source boundary in this audit. Ordinary return is not automatically a user-output sink.

The saved request alternatives carry these fields, preserving the original selected Data identities:

| from_date branch | limit branch | Actual request fields |
|---|---|---|
| Omitted | Omitted | query |
| Present | Omitted | query, from_date |
| Omitted | Present | query, limit |
| Present | Present | query, from_date, limit |

`query` is the original `request.term`; included optional values are the original corresponding fields. Existence flags are not request payload, missing arguments are not replaced with null/defaults, and no fuzzy expansion is introduced. Each request alternative is paired with its own acquired response using the same predecessor bindings. Four alternatives at one static call are not four executed calls. The `loop_summary` content name is used for these correlated branch facts; the CFG has no loop. This is useful symbolic provenance evidence, not a concrete-execution or general feasibility proof.

Source requirements: [workflow lines 5–15](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/source/inputs/package/references/workflow.md:5), [omission settings](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/source/inputs/package/query.yaml:1). Exact request/response identities and all seven source-criterion assessments are in the [independent source audit](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small010-source-audit.json).

## The concrete blocker and its layer

At `ir_019`, propagation correctly selects `total` from each paired search response. At `ir_020`, the model declares the entire required write unmodeled because the source does not specify replacement versus append and does not name a serializer. The engine then stops the block's OUT and does not reach `ir_022`'s `items` selection or `ir_023`'s return.

The two reasons need separate treatment:

- **Update mode:** the frozen [WriteOp type](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/implementation-snapshot/src/skillflow/propagation/contracts/specs.py:131) requires `replace`, `append` or `delete`. It has no generic unknown-mode storage write. The source says to write the response total to `count.txt` without explicitly discussing an existing file's update policy. This is an interface-granularity issue combined with the model's choice to abstain; this audit does not force a particular mode or invent an old-file state.
- **Serializer:** the frozen [endpoint-demand guidance](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/implementation-snapshot/src/skillflow/propagation/contracts/format_instructions.py:10) explicitly preserves abstract result-to-write relationships without inventing a serializer and states that open encoding alone creates no gap. That reason is overbroad. The total payload, destination and after-search ordering are already known. Exact encoding uncertainty should not by itself erase that known boundary.

This was **not a structural rejection of `ir_020`**: the source-unmodeled record has an empty `validation_errors` list. It was not a propagation crash or a loop-convergence failure. The backend returned the documented partial result and retained the preceding records. The serial dependence on the unmodeled write then blocked an otherwise declared unchanged-items return.

The [source](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/source/inputs/package/references/workflow.md:21) and [selected processing gap](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/revision/annotation/audit/compiled-response.json) remain unchanged.

## DOE, correctness and review limits

All 13 sink records have empty `data_reviews`. There are **zero emitted sensitive-data comparisons**, so supported/contradicted positive conclusions are both zero with a conclusion denominator of zero. There are no sensitivity declarations or resolved sensitive scopes. This is justified by the actual source: arbitrary request terms and result items are not a grounded secret category, and no runtime values are supplied. Zero declarations is **not itself an annotation error**, but it also does not certify all future query or response content nonsensitive.

The trace can show what the search tool and possible model observations receive. It cannot establish a whole-workflow DOE verdict. The system saved 20 demands, but demand/sensitivity derivation maps are empty in this DOE output. Both calculated constraint checks (`at_most` and `requires_prior`) are `not_established` because reachable propagation is incomplete. The 11 Task realizations are 7 expressed, 2 partial and 2 retained-only. Fourteen diagnostic records include overlapping coverage and task-expression limitations; they are not 14 independent privacy defects.

The initial source review raised one supported issue: the original CFG treated “parameter descriptions do not instruct validation/normalization” as a prohibition. The revised CFG correctly distinguishes absence of a requirement from prohibition, while retaining unchanged-value requirements. The final review has **zero findings**, but does not remove the storage cutoff; the result remains `partial/diagnostic_only`. A clean findings list is therefore not evidence of complete propagation or semantic success.

No general accuracy percentage, precision, recall or superiority to direct GPT is estimated. The seven pre-run source criteria are assistant judgments, not human gold. The results support a narrower positive statement: the request construction, branch correspondence and response identity in the processed prefix are useful and source-consistent; required output completion remains unresolved.

## Actual public cost and time

| Request group | Native starts | Public tokens |
|---|---:|---:|
| Normal semantic requests | 7 | 170,083 |
| Semantic repair and dependent rebuilding | 5 | 138,964 |
| Structural correction | 1 | 25,659 |
| **Total** | **13** | **334,706** |

Public usage is **303,288 input tokens**, including **155,520 cached input**, plus **31,418 output tokens**. The **12,792 reasoning-output tokens** are an output subset. Cache and reasoning counters are not added again. All 13 accepted finals have complete public usage; request totals, public turn receipts and `metrics.json` agree, and answer/delivery hashes match.

| Time measure | Duration |
|---|---:|
| Main analysis | **15 min 14.98 s** (914.9828548 s) |
| Propagation stage, included above | 39.144467 s |
| DOE stage, included above | 77.327567 s |
| Sole zero-model replay | **90.8301103 s**, matched, zero new starts |
| Total controller wall time | **16 min 47.38 s** (1007.377318 s) |

Stage times include local checking, reconstruction and saving, and parallel stages overlap. Analysis started at **2026-11-02 02:30:34 China time**, ended at **02:45:49**, and the controller closed after replay at **02:47:21**.

Outer retries, public reconnect/error events, pre-launch input rejections and recorded tool/delegation items were all zero. Public logs expose 13 unique CLI thread/turn identities, not provider response IDs. Requested model settings were consistent; there was no independent backend model attestation or extra probe. Provider HTTP attempts, any additional unreported work, currency amounts and human review minutes remain unknown. Historical research and post-run assistant audit costs are separate, not silently counted as zero.

[Detailed accounting and protocol report](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small010-cost.md) · [Per-request accounting and hashes](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small010-cost.json).

## Preserved artifacts

The sole replay matched with zero new native starts, and implementation SHA-256 remained `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b`. Source SHA-256 is `66bc23209ed1dccd2232511bd2933a076c2bb101e0b180737668b78f6dad618c`. Frozen answers, rejected drafts, original reviews and prior failures have not been rewritten.

[Structured summary](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/run-summary.json) · [Propagation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/propagation/manifest.json) · [DOE result](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/doe/doe-result.json) · [Replay receipt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-010-general-loops-high-v8-20261101-214748/replay-check.json).

This report belongs to the four-run validation. Follow-up offline simplification is separate and did not affect this run. The audit read saved JSON and frozen source only; it did not invoke loaders, compilation, solving, another replay, model targets or Skill execution.
