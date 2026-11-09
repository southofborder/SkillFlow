# Specific demand relocation, CFG evidence and Task prohibitions

**Result: partial semantic acceptance.** The latest review names the two actual redundant demands, resolves them through the real repair context, and explicitly relocates them to the receiver input while removing the upstream copies. It separately identifies the missing Task exclusion. One CFG-evidence reason still attributes source-supported field membership to a bare result operand, so the preregistered all-CFG-reasons gate is not fully met.

Both arms completed 2/2 first responses with zero structural corrections. This run does not demonstrate fewer corrections. Latest total tokens increased by 9.48% and summed request time increased by 14.40%; it does not demonstrate cost reduction.

## Production change and offline verification

Only review/prompts.py and contracts/format_instructions.py changed among the 145 frozen production Python files. The seven Prompt sections, strict Schema, business fields, runtime contract and analysis algorithms remain. The existing independent calibration example is reused; its demand references are generated from that example rather than copied from evaluated Skills. No teaching scenario was added. Each paired Prompt grew by 1,094 characters/UTF-8 bytes (approximately 1.05-1.17%).

The final offline regression receipts contain **300 distinct passing tests** after deduplicating JUnit node identities: 142 semantic tests, 135 persistence/provenance/sensitivity tests, 16 persistent Task-path tests and 7 additional coordinate tests. The 25-test focused receipt overlaps those groups. Development failures and their final reruns remain in the receipts; this is not a whole-repository pytest claim.

[Offline receipts](verification/regression/summary.json) · [Preflight source and Prompt checks](verification/preflight.json) · [Readiness gate](verification/ready.json) · [Preregistered assessment](assessment-plan.json) · [Change explanation](changes.md)

## Actual online use

| Measurement | Exact previous-run latest Prompt baseline | Latest Prompt |
|---|---:|---:|
| First completed legal responses | 2/2 | 2/2 |
| Logical requests | 2 | 2 |
| Structural corrections | 0 | 0 |
| HTTP attempts | 2 | 2 |
| HTTP retries | 0 | 0 |
| JSON normalizations | 0 | 0 |
| Input tokens | 51,552 | 51,980 |
| Output tokens, including reasoning | 62,519 | 72,900 |
| Total tokens | 114,071 | 124,880 |
| Sum of request seconds | 304.765 | 348.662 |

The four logical requests used four HTTP attempts and 238,951 total tokens. Online wall time was 662.888 seconds, excluding preparation and replay. Model requested: deepseek-v4-flash; actual reported model: deepseek-flash; reasoning_effort=max. No semantic repair, quality rerun, Task extraction, connection probe or formal 001/010/013 rerun occurred.

All four attempts supplied usage. Provider-reported reasoning was 60,434 baseline and 70,710 latest, already included in output/total tokens. Cache-hit prompt tokens were 51,200 baseline and 24,704 latest, also already included; the differing cache distributions and reasoning variation preclude a causal price or stable performance claim. Initial-request and whole-chain totals coincide because no correction was required.

| Actual review | Arm | First legal | Findings | Total tokens | Request seconds |
|---|---|---|---:|---:|---:|
| [custody_release](cases/review_custody_release/baseline/calls/review/a001/response.json) | baseline | True | 0 | 55,365 | 147.630 |
| [custody_release](cases/review_custody_release/latest/calls/review/a001/response.json) | latest | True | 0 | 65,195 | 191.271 |
| [voucher_delivery](cases/review_voucher_delivery/latest/calls/review/a001/response.json) | latest | True | 4 | 59,685 | 157.391 |
| [voucher_delivery](cases/review_voucher_delivery/baseline/calls/review/a001/response.json) | baseline | True | 4 | 58,706 | 157.135 |

## Relationship assessment

- **Exact relocation:** latest names ann_0095 and ann_0099, includes both in finding.target_ids, points to deliver input[0] paths claim_id and credit, and explicitly removes their upstream copies while keeping actual build/selection operations. The read-only production repair-context builder resolves both to the two existing build demands and the delivery parent. Baseline says add or relocate but does not identify the two redundant placements. No repair model was called, so actual repair success remains unmeasured.
- **Task prohibition:** both arms separately report the explicit private_case_note exclusion missing from Task. Latest uses a source-only domain=task broadened_requirement objection against existing R1/R2, which is a valid isolated Task-revision route. The additional sensitivity finding does not replace that prohibition. Neither positive control invents a prohibition from privacy wording alone.
- **Acquisition versus demand:** both arms retain the complete read and possible observation while removing the unsupported whole-value task demand; neither narrows the actual acquisition to make the demand appear correct.
- **CFG evidence residual:** latest F003 says the CFG output contains private_case_note, but its actual object is only {type: result, identifier: voucher}. Source evidence supports that field; the CFG operand supports output identity. This small attribution overstatement remains in both arms. Other relevant CFG reasons explicitly distinguish the operand from annotation demand lists. The extra sensitivity finding is source-supported and is not classified as a substantive false positive.
- **Legitimate control:** both whole-object/Boolean-return review controls have zero findings. Independent upstream/return demands, supported controls, conditional construction and conservative relations are additionally covered by offline tests. The unconditional live negative fixture does not itself measure conditional-demand repair.

[Independent assistant review and actual resolved repair targets](assessment-reviews.assistant.md) · [Machine-readable assessment](assessment.assistant.json) · [Frozen online metrics](metrics.json) · [Zero-API replay](replay.json)

The baseline is byte-identical to the latest production Prompts in the preceding focused run. These two fixtures are reused development material. No responses were selected, edited or rerun for quality. Literal source field names in this assessment describe the actual evaluated input/output; they are not hardcoded production rules. The observations establish neither generalization nor semantic completeness. No conclusion here proves minimality or absence of DOE.
