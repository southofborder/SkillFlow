# Focused review-output validation

**Structure improved in this paired sample; the repair-suggestion objective is only partially met.** Latest had two legal initial responses and zero structural corrections. Baseline had one legal initial response and one correction. Both arms found the two main controlled defects and accepted the legitimate whole-value/Boolean control. Latest advice and evidence still have substantive caveats.

## Focused implementation and offline evidence

The seven Prompt sections remain unchanged. Exact permitted check keys are listed once in FORMAT; extra explanation belongs in reason. Existing repair guidance and the same complete example now distinguish actual select_part/build/when operations from the demands attached to them. Only redundant endpoint-content seeds should move; independent upstream/return requirements and conservative dependencies remain supported.

No business field, Schema, runtime rule, analysis algorithm, or long example was added. Among 145 frozen production Python files, only review/prompts.py and contracts/format_instructions.py changed. The other 143 files are byte-identical. Each live Prompt grew by 351 characters/UTF-8 bytes, about 0.34–0.38%; the example itself grew by 12 characters.

Final disjoint offline groups passed **82 + 135 + 13 + 19 = 249 tests**. The first semantic run had one old wording assertion failure; its explicit finding_indexes wording was updated and all 82 tests passed on rerun. Initial failure and rerun logs remain available. Strict extra-key rejection, raw-response preservation, rendered examples, conditional demand, persistence, interruption, accepted-response protection and zero-API replay were retained.

[Change notes](changes.md) · [Source and size preflight](verification/preflight.json) · [Prompt regression](verification/prompt-and-persistence/semantics-rerun.json) · [Persistence regression](verification/prompt-and-persistence/persistence.json) · [Runner regressions](verification/runner/summary.json)

## Actual calls and cost

| Metric | Baseline, including correction | Latest |
|---|---:|---:|
| First completed legal responses | 1/2 | 2/2 |
| Logical calls | 3 | 2 |
| HTTP attempts | 3 | 2 |
| Structural corrections | 1 | 0 |
| JSON normalizations | 0 | 0 |
| HTTP retries | 0 | 0 |
| Input tokens | 70,430 | 51,552 |
| Output tokens, reasoning included | 71,990 | 73,548 |
| Total tokens | 142,420 | 125,100 |
| Reasoning breakdown, already in output | 68,332 | 71,295 |
| Cache-hit input breakdown, already in input | 68,224 | 24,832 |
| Cache-miss input breakdown, already in input | 2,206 | 26,720 |
| Sum of request seconds | 359.023 | 352.631 |

All five HTTP attempts supplied usage. There were **267,520 total tokens**, and online wall time was **721.868 seconds (12 minutes 1.9 seconds)**, excluding preparation and replay. The requested model was deepseek-v4-flash with reasoning_effort=max; all accepted calls reported deepseek-flash. No extra probe, quality rerun, Task extraction or semantic repair was sent.

Including correction, latest total tokens were **12.16% lower** and summed request seconds **1.78% lower**. Initial requests alone used **121,558 baseline versus 125,100 latest tokens**, so latest was **2.91% higher** before corrections. The baseline correction added **20,862 tokens and 7.593 seconds**. The measured whole-chain token saving is therefore from avoiding that one correction, not from cheaper initial prompts.

Reasoning/cache fields are breakdowns and are not added to totals. Cache-hit distributions differ substantially; token count is not a provider invoice comparison. With two reused cases and stochastic generation, this is neither a stable cost guarantee nor a generalized retry-rate result.

## Semantic findings and remaining issues

| Check | Baseline | Latest |
|---|---|---|
| Legitimate whole memo deposit and Boolean return | Accepted, no false finding | Accepted, no false finding |
| Acquisition-only whole-value Task seed | Found | Found |
| Missing actual receiver field-value demands | Found | Found |
| Redundant upstream-seed repair advice | Adds receiver demands without explicit relocation | Explicit relocation exception added, but keep construction-level demands remains ambiguous |
| Missing private-note sensitivity | Found | Found |
| Missing Task exclusion for private note | Found | Not reported |

Latest F002 says both keep construction-level demands and relocate a build-slot demand if it serves only this delivery. In this candidate the build-slot seeds have exactly that delivery-only purpose. The explicit relocation clause is an improvement, but the reviewer should identify and move those seeds rather than give potentially conflicting keep/add instructions. Independent upstream demands and conservative relations must still be preserved. No actual semantic repair was executed, so this experiment does not establish repair success.

Latest F002 uses a legal whole-IR CFG coordinate, but its reason says the instruction contains build and deliver operations. Those operations are in raw_annotation; the CFG instruction contains only the submission opcode/input, with no such atomic-operation list. Candidate target IDs locate those annotation facts. A valid target does not establish adequate evidentiary support.

Baseline also identifies the missing source prohibition in the frozen Task; latest does not. Labeling private_case_note as sensitive does not replace retaining its Task restriction. This additional omission is recorded separately from the two main controlled checks. The fixture expectation is not rewritten and is not an expert gold standard.

## First invalid response and accepted correction

Baseline voucher a001 invented requirement_checks[0].reason_unused, an empty string outside the permitted fields. Strict validation rejected it. The complete a002 response was accepted; the original first-response failure remains counted. Latest voucher a001 was accepted without normalization or structural correction. No program deleted an extra field to improve the measurement.

[Baseline raw response](cases/review_voucher_delivery/baseline/calls/review/a001/response.json) · [Diagnostic](cases/review_voucher_delivery/baseline/calls/review/a001/validation.json) · [Baseline accepted review](cases/review_voucher_delivery/baseline/review.json) · [Latest accepted review](cases/review_voucher_delivery/latest/review.json)

## Reproducibility and scope

Both baseline Prompts match the previous run’s latest Prompts byte for byte. Inputs, frozen candidate, strict validator, current v5 correction and model configuration are identical between arms. Only the initial Prompt differs; case order was counterbalanced. These two cases were reused for development and are not held-out evaluation. Preservation of conditional build.when is covered offline, not by the unconditional live voucher fixture.

Call-file identities, usage and timing were frozen before replay. Zero-API replay matched all four chain decisions. The first-response structure gate is met by latest in this sample; semantic suggestion/evidence quality is not fully met. No further model requests or Prompt edits were made to select a better outcome.

[Independent assistant assessment](assessment-reviews.assistant.md) · [Frozen metrics](metrics.json) · [Zero-API replay](replay.json) · [Pre-call assessment plan](assessment-plan.json) · [Assessment bindings](assessment.assistant.json)
