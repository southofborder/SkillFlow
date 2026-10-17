# Targeted prompt rework and first-response screening

The objective is fewer mechanically invalid first responses without sacrificing semantic fidelity. Static prompt length is a secondary measure. A shorter reference that requires additional full-response corrections has not demonstrated lower end-to-end cost.

The annotation and review templates retain seven sections: authority, input, format, workflow, rules, examples, and self-check. This change concentrates on exact formats, shared decisions, and the examples actually sent. It does not change business fields, strict schemas, the runtime contract, or propagation and DOE rules.

## Exact, executable teaching content

An example may omit an explicitly identified outer context, but cannot omit required fields inside the displayed object. In particular, operation evidence, expression evidence, and demand reasons are retained. Tests extract examples from the final rendered request and validate the shown objects in their declared synthetic context; testing an unrendered full fixture is insufficient.

The coordinate reference distinguishes complete IR/block targets with `path: []`, actual operand targets, and operation-consumption slots. A general realization correspondence is not automatically an executable demand. An operation slot resolves through its ValueRef to the enclosing IR operand; controls and payloads remain separate.

An IR with operations but only null effects still needs `empty_effect_evidences`. Processing and operation evidence remains nonempty, while a null event omits event-level evidence or uses an empty list. A true CFG evidence target remains valid; prior missing-path errors do not justify banning CFG evidence.

Review examples use actual check/finding structures, not merely another copy of annotation examples. Accepted checks include `finding_indexes: []`. Existing goals are checked exactly as listed in the supplied goal index. A missing seed is reported against an existing realization or operation parent, not an invented goal pointer.

## Semantic distinctions retained

- A non-action `self` target on an output-producing operation denotes that output, not its attached expression. Filter-root truth cannot represent the member predicate; a real Boolean computation can legitimately carry truth demand.
- `expected` and `expected_path` constrain the required original-value relation. They do not execute a selection, narrow an acquired container, or validate a sensitivity scope merely because a local has a field-like name.
- Conditional build membership uses `when`. Presence controls are not payload values, and `expected` is not a Boolean inclusion predicate.
- Required delivery and write content is preserved at its actual consumed slot. An action alone does not preserve the payload; neither an upstream seed nor matching Data identity transfers demand to every recipient.
- An unspecified encoding does not itself create a source obligation. Preserve any actual unexpressed requirement as a gap, without inventing an encoding or erasing a supported abstract result-to-write relation.

Source-only Task extraction, fixed Task identity, four-axis review, and one shared semantic-repair budget remain. Normal / annotation-repair / isolated-Task-revision routes retain three / five / six semantic calls. Production structural correction remains unlimited.

## Mechanical diagnostics and protocol

Protocol `skillflow-structural-correction-v5` keeps raw validation diagnostics and a deterministic mapping to the model-visible display. Failed union alternatives for one CFG target are grouped at the actual candidate object with the allowed forms. Raw branch expansion counts are not counts of independent mistakes.

Independent errors are collected only after their prerequisites hold. Unknown references must not generate dependent semantic-binding errors. The program does not add missing paths, move evidence, create demands, or catch arbitrary implementation failures as a reason to call the model again.

The correction request keeps the same frozen input, authority, compact format, and semantic obligations. It contains one current candidate, current diagnostics, and only relevant short corrective examples. Original responses and restricted JSON-normalization receipts remain unchanged. The injected service, durable runner, loading, and replay rebuild the same request. Old request chains are not migrated.

## Eight first-response requests

The immediately preceding production prompts are frozen as the baseline. Four new English materials are created independently of teaching cases: two annotation materials and two review materials. Task fixtures have explicit assistant-authored provenance. Both review arms receive the same frozen candidate. No Task extraction, DOE call, semantic repair, or additional reviewer is run.

Each material has one baseline and one revised request, interleaved for eight logical calls. The model configuration, strict validator, restricted JSON normalization, and transport policy are shared. Transport retries are counted separately. A complete invalid response is preserved and diagnosed, but this experimental screen does not start a correction request. That is a distinct first-response experiment, not an attempt cap imposed on the production correction loop.

The prepared source, CFG, Task, review candidates, prompts, and external assessment expectations are frozen before calls. Expected answers are absent from model inputs. No candidate or expectation is changed after seeing results, and there is no quality rerun. User interruption prevents later requests; resuming consumes already accepted responses rather than resending them.

The structural/semantic screening gate requires all four revised responses to be valid, the preregistered relation checks to hold, the review positive control to have no new material false finding, and the negative control to identify its material defects at valid targets. New findings outside the preregistered set receive separate assistant assessment, not automatic false-positive classification.

Report provider input, output, reasoning/cache subdivisions, elapsed time, errors, and first-response validity separately. Missing usage is unknown. Reasoning is already included in output tokens. If reported first-response total tokens do not decrease, do not claim first-response savings. This experiment does not measure complete correction-chain cost and cannot establish that it decreased. If both arms are initially valid, there is no demonstrated improvement in correction frequency.

The experiment ends after these eight requests and offline replay, regardless of outcome. A new formal three-case run requires a separate decision. Historical artifacts remain unchanged.

The separate experiment uses `skillflow-first-response-screen-v1` and these commands:

```text
python -m tools.doe.compare_prompts screen-prepare --baseline-dir <frozen-current-source> --run-dir <new-directory> [--env-file <configuration>]
python -m tools.doe.compare_prompts screen-run --run-dir <prepared-directory> [--env-file <configuration>]
python -m tools.doe.compare_prompts screen-replay --run-dir <screen-directory>
```

The prepared manifest binds both rendered prompts, exact shared inputs, assistant-authored fixture provenance, external preregistration, public configuration, and current implementation. The baseline is rendered in an isolated offline subprocess from its frozen source snapshot. It is not a second production entry. Calls and their usage are frozen before replay; replay does not create a new response or overwrite the original timing.

## Offline acceptance and reporting

The regression covers final rendered examples and section order, target forms, evidence levels, realization/seed consistency, goal-index coverage, field identity, optional controls, true Boolean versus collection truth, and supported conservative behavior. Valid but semantically wrong examples must not be described as semantically verified merely because reference validation succeeds.

Recovery tests include acceptance before interruption, invalid and truncated responses, failed requests, identity/configuration tampering, and zero-API replay. Language checks preserve genuine multilingual inputs and quoted evidence. Reports distinguish engineering validation, model behavior, and assistant assessment; none is independent expert ground truth or proof of semantic completeness.

## Recorded first screen (2026-10-16)

The [eight-response screen](../../experiments/doe/runs/prompt-first-response-v1-20261016-190040/index.html) completed and replayed with zero API calls. The gate **did not pass**: the frozen current-production baseline had 2/4 valid first responses and the revised prompts had 3/4. Revised annotation B still placed parameter-content demands upstream of the receiving operation. Both negative-review responses missed the broad read-output demand and used annotation-operation paths as invalid CFG evidence.

Total provider tokens were 281,964 for baseline and 285,677 for revised, a 1.32% increase. This does not establish first-response token savings or complete correction-chain savings. There were eight logical requests, eight HTTP attempts, no retries, no applied JSON normalization, and no correction or repair requests. No formal three-case rerun followed. The [assistant assessment](../../experiments/doe/runs/prompt-first-response-v1-20261016-190040/assessment.assistant.json) is separate from the metrics frozen before semantic review; neither is independent expert ground truth.
