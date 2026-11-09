# GA4 boundary-alignment v6: closed-run assessment

**This run did not produce a complete or useful DOE conclusion. It stopped at delivery of the unified source-review request, before propagation or DOE ran.** The model did not refuse to annotate the Skill: all six preceding semantic stages produced usable structural artifacts, and the program assembled a compilable candidate. The immediate blocker was an oversized program-generated review input. This is an engineering failure in input construction and delivery, not a demonstrated semantic limitation of GPT or a successful capability result.

## Run and preservation

The sole new run used configured `gpt-6.1-sol / high / openai`, two workers and the seven-stage protocol. It began on 2026-10-29 at 00:17:31 China time. The same frozen 16-file, 155170-byte source was used, with source digest `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. Task, CFG and all fragments were regenerated; no historical answers were reused. The implementation digest was `5c448e80e8a2b363301c50cdbdd1d09f3651ba172146aefa35e4cdc37ce16221` and its final check found no changed files. No Skill was installed or executed, and there were no model probes or model-based monitoring calls. Runtime identity here describes the explicit launch configuration; it is not an independent server attestation.

Original requests, both processing answers, all other answers, the rejected review input, stderr, failure records and the failed replay remain intact. This assessment adds records; it does not relabel or repair the frozen run.

## Actual completion

| Component | Result |
|---|---|
| Task | First answer accepted; 48 requirements and 8 recorded issues |
| Flow | First answer accepted |
| CFG | First answer accepted; 140 blocks, 349 IR, 162 edges |
| Processing | 349 records accepted after one selected-record structural correction |
| Task correspondence | First answer accepted; 48 realizations, 87 top-level demands and 83 operation-demand records |
| Sensitivity | First answer accepted; 80 declarations |
| Program assembly | Compiled candidate saved; 19 processing limitations retained |
| Unified source review | Request rejected before a review answer existed |
| Semantic repair | Not used; no review findings existed to authorize its dependency closure |
| Propagation / DOE | Not executed; computed coverage and findings are unknown, not zero exposure |

The processing fragment contains 27 case summaries, 7 may-state writes and 3 for_each records. All 349 IR have records and none of the 19 gaps is marked unmodeled. **These are structural coverage facts, not proof that all 349 IR propagate correctly or that the model's semantics are correct.** The three for_each records describe URL normalization and file-path construction. The API batch/reindex paths instead retain explicit CFG loops and declared limitations about dynamic selection and member pairing. Their requested occurrence-level properties were not established by this run. Cross-invocation cache transitions, exact counts, result-file ownership, summary implementation and installer effects also remain recorded limits or source questions. The missing source review means none should be presented as independently adjudicated.

The processing correction addressed source-evidence inheritance and invalid placement of cases in a segment slot. It replaced selected records rather than requesting another complete annotation. Its complete answer is retained separately from the initially invalid answer.

## Why the run stopped

The native CLI rejected `turn/start` with `input_too_large` (code -32602): **2,002,990 delivered characters exceeded the 1,048,576-character maximum**. It exited after 3.47 seconds, with no complete review answer or usage receipt. The review body contains 2,002,778 Unicode characters, plus a 212-character delivery envelope. These are character-limit measurements, never substitutes for actual tokens.

The expanded `target_index` contains **8,040 mechanical locators and 1,264,426 characters**. It alone exceeds the delivery limit and accounts for most of the prompt. Arithmetically removing that expanded directory leaves about 738,352 body characters, including source and semantic material. This is evidence for a narrow next change: use existing record IDs and checked field paths instead of shipping the full expanded leaf directory. It is not a validated replacement prompt, and no material was dropped or resent in this run.

The offline tests covered the new semantic mechanisms and representative source projections but did not catch the actual large graph's final delivery-size limit. That is an acceptance gap in this implementation. The correct next fix is input organization, not a weaker semantic standard or a new sampling attempt inside the stopped run.

There were 11 background model-catalog refresh timeout lines in native stderr. Earlier stages nevertheless returned complete answers. These warnings are separate from the explicit input_too_large failure; their causal effect on latency is not established. There were zero outer transport retries.

## Replay and monitoring defects

The one automatic zero-model replay lasted **903.68 seconds (15 min 3.68 sec)**. It launched **zero new native requests**, but its result-consistency check failed: `Replayed guided decisions differ from saved results`. This is a failed replay, not a pass with a caveat.

The live outer handler recorded `ValueError: CLI produced no complete answer; this is not an eligible transient network retry`. Saved-call restoration raises `SavedCallFailure` while retaining `error_type=ValueError`; the outer handler formats the wrapper class name instead. The constructed replay reason is `SavedCallFailure: CLI produced no complete answer; this is not an eligible transient network retry`. Comparing those strings proves at least one differing decision field. This diagnosis used saved records and the existing exception constructor; no second whole-run replay was performed.

The saved top-level run status is failed, but the last stage table still says review=running. The controller then spent time in offline replay. Root initially treated the stale stage as an ongoing review and corrected that statement after inspecting completion and native records. Future observation must prioritize run completion/failure markers, and terminal error handling should close the active stage. No frozen stage record was rewritten here.

## Cost and time

There were **8 actual CLI process starts**: seven planned semantic stage requests, including the rejected review request, plus one processing correction. Seven complete model answers were saved; one of them was the initially invalid processing answer. Six semantic stages completed. Public known usage totals **874,398 tokens**: 708,965 input and 165,433 output. Cached input is 299,648 and reported reasoning output is 27,373; these are subsets and are not added again. The rejected request has unknown usage. Native internal HTTP attempt counts and monetary cost are unavailable. Public completed events contained seven agent messages and no observed tool execution or delegation; hidden reasoning was neither read nor exported.

| Native request | Seconds | Input | Cached input subset | Output | Known total |
|---|---:|---:|---:|---:|---:|
| flow | 174.92 | 78739 | 77568 | 3223 | 81962 |
| graph | 528.64 | 31328 | 12288 | 48587 | 79915 |
| processing | 711.29 | 95866 | 95744 | 54860 | 150726 |
| processing correction | 105.51 | 143063 | 12288 | 6710 | 149773 |
| review | 3.47 | unknown | unknown | unknown | unknown |
| sensitivity | 199.52 | 132927 | 12288 | 10747 | 143674 |
| task | 411.59 | 81492 | 77184 | 16918 | 98410 |
| task-correspondence | 443.36 | 145550 | 12288 | 24388 | 169938 |

The main analysis took **2773.17 seconds (46 min 13.17 sec)** to fail. Program assembly/compilation alone occupied **706.10 seconds (about 11 min 46 sec)**. The controller, including the one replay and closure checks, lasted **3677.36 seconds (about 61 min 17 sec)**. Per-request times overlap because of the two-worker schedule; their sum is not wall-clock duration.

The preceding High run used 17 requests, 1,757,935 known public tokens and 78 min 8.21 sec, and reached a partial DOE result with only 8/126 IR processed. This run used fewer requests and known tokens, but stopped earlier in the pipeline and produced no DOE. **No speed, accuracy or completeness advantage is established by that difference.** The increase from 126 to 349 IR also changes the amount of represented work and does not by itself demonstrate improved source coverage.

## Implementation and offline evidence

Implemented components include shared boundary granularity, nonrecursive call outcomes, bounded may-state summaries, a single each after field prefixes, source-evidence and complete-fragment checks, program assembly and sparse review ownership. The affected-interface suite passed 473 tests in 234.26 seconds. A fresh post-fix suite passed 100 in 60.86 seconds; these suites overlap. Independent final integration checks passed 11 in 14.41 seconds. A wider historical suite was stopped and is not claimed to have passed. All of these were zero-model engineering checks.

The next narrow work is to replace the expanded review locator directory with compact record-level addressing, apply a local delivery-length check, normalize saved failure identity during replay, and close terminal progress states. The ordinary boundary and loop semantics still require a completed source review and actual propagation/DOE on a future authorized run. No generic cache or exception engine is indicated by the observed delivery failure.

## Evidence

- [Machine summary](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/run-summary.json), [failure attribution](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/failure-analysis.json), [public cost ledger](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/metrics.json).
- [Original run decision](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/result.json), [main completion](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/analysis-finished.json), [replay failure](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/replay-check.json), [unchanged implementation](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/implementation-check.json).
- [Compiled candidate](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/annotation/audit/compiled-response.json), [model-facing assembled annotation](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/annotation/audit/wire-annotation.json), [processing fragment and limits](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/steps/processing/value.json).
- [Rejected review prompt](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/review/prompt.txt), [native rejection](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/transport/review/5110701dc279a61998ded0136021ce0f98f9edc827e50b288b02fe67fba7aaa1/attempt-001/stderr.txt), [frozen run protocol](D:/projects/SkillFlow/experiments/doe/runs/document-guided-ga4-boundary-high-v6-20261029-001632/run-protocol.json).
- [Chinese design/offline report](D:/projects/SkillFlow/docs/doe/abstraction-alignment-v6-offline.zh.md), [machine offline acceptance](D:/projects/SkillFlow/output/verification/boundary-alignment-v6/offline-acceptance.json).
