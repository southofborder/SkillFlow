# Small Skill 001 v8: closed-run assessment

**The run closed, but did not complete propagation or establish a useful substantive DOE conclusion.** It resolved the initial acquisition of `events.json` and a possible default-contract model observation of its `access_token` field. The actual record-selection, notification and count-file paths were blocked. The only emitted DOE comparison explicitly remained unresolved.

This was a fresh run of **conditional-notification**, using its frozen one-file English source and requested `gpt-6.1-sol / high / openai`, two workers, seven normal semantic requests, one structural correction per stage and one shared semantic repair round. This is a development case, not a held-out benchmark. Source and implementation checks passed; historical answers were not imported. The sole replay matched with zero new native starts.

## Actual coverage and DOE

| Measure | Actual result |
|---|---:|
| Selected CFG | 13 IR, 6 blocks, 7 edges |
| Compiled processing present | 12 / 13 IR (92.31%) |
| Actually processed IR | **2 / 13 (15.38%)** |
| Visited unmodeled cutoff | 1: `ir_003` |
| Downstream blocked IR | 10 |
| Source acquisition position resolved | 1 / 1 |
| Source notification position resolved | **0 / 1** |
| Source count-file write position resolved | **0 / 1** |
| Source per-record loop relation propagated | **0 / 1** |
| Recorded / unresolved declared sink coordinates | 1 / 6 |
| Sensitivity declarations resolved | 1 / 1 |
| Demand derivations | 0 |
| Emitted DOE comparisons | 1, explicitly unresolved |
| Constraint checks | 1, `not_established` |

These source denominators count static positions, not actual notification executions or records. The source acquisition, notification and persistence actions are distinct from the seven compiled sink coordinates, five of which are contract model observations. `expected_sinks=1` is the resolved propagation inventory; it is not a claim that the other six boundaries were analyzed.

The sole comparison is at the model observation following `ir_001`, with a direct `Credential` declaration on `each/access_token`. It reports `no_excess_established` and explicitly explains that limitations leave the comparison unresolved. Accordingly there are **zero supported conclusive DOE findings, zero contradicted conclusive findings, and one unresolved comparison**. This is not a safe verdict and not evidence that tokens are necessary. There are no computed notification payload, receiver-pairing or count-file necessity judgments. The 33 diagnostics overlap causes and affected locations, rather than representing 33 separate defects.

The initial credential boundary and the retained prohibition are useful diagnostic evidence. They do not make this an end-to-end successful data-minimization analysis. No DOE accuracy, precision or recall is reported from an unresolved comparison and unprocessed main paths.

## Concrete blocker and its layer

The source says to traverse the acquired records and select only when `opted_out` is not true and (`urgent` is true or `value >= 100`), then send that same record's original summary to its recipient. The generated CFG creates `ir_003` (`for_each_next`) with a collection input and **two outputs**: a Boolean `has_record` and a conditional `current_record`. Its `ir_004` terminator consumes only the Boolean.

The frozen processing interface instead provides a `member` operation with one member output, and a `branch` operation whose `has_member` predicate acts on a collection. The branch has targets but no Boolean result output. The selected graph therefore requires a coupled Boolean/member interface that the processing fragment cannot satisfy without changing the CFG or inventing traversal computation. The selected `ir_003` is explicitly unmodeled with no structure-validation errors. This is a **CFG/processing alignment blocker**, not evidence of slow loop convergence or a schema-rejected response.

The initial review's F001 requested a processing-only correction using member/typed-guard relations. The shared repair rebuilt processing, task correspondence and sensitivity, but retained the original CFG. The repaired processing explained the exact Boolean-versus-collection mismatch and kept the cutoff. The final review returned no findings, while the run correctly remained `partial/diagnostic_only`; an empty sparse findings list did not make the loop executable.

The relevant immutable code evidence is [MemberOp and BranchOp](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/implementation-snapshot/src/skillflow/propagation/contracts/specs.py:250) and [typed collection guards](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/implementation-snapshot/src/skillflow/propagation/loop_guards.py:5). This workflow can be expressed with existing loop relations arranged consistently; this result does not demonstrate that a generic new loop executor is required.

## Source correctness review

All six pre-run assistant source criteria were examined separately from the target. They are not human gold:

- **Acquisition and sensitivity:** the full symbolic file is acquired without fabricated runtime records; `access_token` remains a distinct source-backed sensitive field. Default model visibility is labeled as a contract possibility, not an observed execution.
- **Selection:** the normalized expression retains the opt-out conjunction and urgency/threshold disjunction. It is declared correctly but never propagated.
- **Recipient/body/occurrence:** the candidate references the same record's recipient and original summary, with no rewrite. No actual loop-member or notification record exists to validate duplicate occurrence handling, once-per-selected-record behavior or receiver/body pairing.
- **Prohibition:** repair changed the access-token constraint from only the notification tool to all receiver boundaries. The computed constraint remains `not_established`; possible model visibility is not proof of measured disclosure or complete workflow violation.
- **Count:** the candidate retains the source's unresolved meaning of “processed records,” without substituting whole-record saving or a token payload. The count and write are unprocessed.
- **Receiving demands:** recipient, body and count demands exist, but actual demand derivations are empty and five `unbound_goal` diagnostics remain. Acquisition is not treated as blanket necessity for every later receiver.

Exact source ranges and saved-object coordinates are in the [independent source audit](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small001-source-audit.json). The source itself is [frozen SKILL.md](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/source/inputs/package/SKILL.md). No static conclusion is elevated to proof that all possible input records or task ambiguities have been resolved.

## Actual available cost

| Request category | Starts | Public tokens |
|---|---:|---:|
| Normal semantic requests | 7 | 163,143 |
| Shared semantic repair and dependent rebuilding | 4 | 107,796 |
| Structural corrections | 3 | 72,585 |
| **Total** | **14** | **343,524** |

Known usage is **312,448 input tokens**, including **172,032 cached input**, plus **31,076 output tokens**. The **16,251 reasoning-output tokens are a subset of output**, not extra usage. All 14 accepted finals have complete public usage. There were zero outer retries, zero prelaunch input rejections and zero public reconnect/error events.

| Time measure | Actual duration |
|---|---:|
| Main analysis | **15 min 37.32 s** (937.3180399 s) |
| Propagation stage, included above | 26.692454 s |
| DOE stage, included above | 29.087914 s |
| Sole replay | **45.747065 s**, matched, zero new starts |
| Controller start through closure | **16 min 24.47 s** (984.470494 s) |

Analysis ran from **2026-11-02 02:14:04 to 02:29:42 China time**; controller/replay closure was **02:30:29**. Stage durations include local validation and saving and are not solver-only or inference-only measurements.

Public metadata exposes 14 unique CLI thread/turn identities, no provider response IDs, and no recorded tool/delegation items. Every launch consistently requested the stated model/effort/provider, but the public events do not independently attest backend configuration. Exact provider HTTP attempts, unreported provider work, currency charges and human review time remain unknown. Post-run assistant auditing is separate from the target token total. Detailed reconciliation and stage timings are in the [cost/protocol report](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small001-cost.md) and [structured accounting](D:/projects/SkillFlow/output/verification/general-loops-v8-online-20261101/final-audit/small001-cost.json).

## Closure and evidence

The source snapshot SHA-256 is `d7548162e5d4de62ee90bd1763b1a701bcbe731c723d675d9d2e0dd8e5c989a6`; the one frozen source file matched its recorded hash. Implementation SHA-256 `a157d545f4eef0cddd1f669047bce1999e053896e5ba66ea9270e63aaf5e607b` remained unchanged. The existing controller performed exactly one [matched zero-model replay](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/replay-check.json). No new loader, compiler, solver, replay, model target or Skill execution was invoked for this audit.

Original source, answers, corrections, selected candidate, cutoff and review records remain unchanged. See the [structured run summary](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/run-summary.json), [actual propagation manifest](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/propagation/manifest.json) and [actual DOE result](D:/projects/SkillFlow/experiments/doe/runs/document-guided-001-general-loops-high-v8-20261101-214748/doe/doe-result.json). This report establishes a concrete front-end alignment failure on a small Skill; it establishes neither general accuracy nor an advantage over direct GPT. The other authorized runs continue under the existing queue, without any launch or control action by this audit.
