# Small paired endpoint-prompt validation

The tool compares a frozen baseline prompt with the current prompt. Its pool contains four independently authored English development cases: two annotation cases, one legitimate review control, and one review candidate with an excessive acquisition seed and missing receiver content demands. Both review arms inspect exactly the same frozen candidate. Task is an explicit authored fixture; it is not extracted by an extra model call. Each experiment records which cases and frozen baseline it selected.

The v2 tool supports an explicit subset of these cases; the default remains all four cases and eight starting chains. Each selected case has one baseline and one latest chain, with deterministic alternating arm order. Both arms use identical model inputs, strict validators, current v5 structural correction, JSON normalization, JSON Output, SSE, and transport settings. Only the initial prompt differs. Structure correction runs under the existing unlimited policy; semantic repair, quality reruns, and a formal three-case rerun are not part of this experiment. Historical v1 experiments retain their exact four-case/eight-chain shape; read-only verification does not authorize replay under a changed implementation.

The tool uses production `ResponseChain` and the existing recorder and transport. It preserves raw responses, diagnostics, request identities, final accepted-call selection, interruption, recovery, and zero-API replay. Credentials are loaded only if a missing request actually needs a live client. Unexpected implementation failures stop execution; they are not classified as model-correctable errors.

```text
python -m tools.doe.endpoint_validation prepare --baseline-dir <frozen-source> --run-dir <new-directory> [--case <supported-case-name> ...] [--env-file <configuration>]
python -m tools.doe.endpoint_validation run --run-dir <prepared-directory> [--env-file <configuration>]
python -m tools.doe.endpoint_validation replay --run-dir <recorded-directory>
```

Preparation freezes source, CFG, sealed Task, candidates, external relationship checks, baseline source, both rendered prompts, public configuration, and implementation identity. Baseline rendering is network-disabled and checks that all SkillFlow imports come from the frozen source. The paired `INPUT` blocks must be identical. Examples and expected findings are not copied into actual inputs.

First-response protocol validity, successful completed analysis, normalization, final chain status, and actual structural corrections are distinct measures. A legal `cannot_assess` is protocol-valid but stops as a semantic failure. A transport failure or truncation with no validated candidate leaves first-response legality unknown. No accepted response is resent during resume or replay.

Metrics use all actual recorded HTTP attempts, including failed attempts where the provider supplies usage. Input, output, total, reasoning/cache breakdowns, HTTP retries, actual returned model names, call durations, and total online wall time are retained. Reasoning and cache fields are not added to total tokens. Missing usage remains unknown or a known subtotal. Online timing and call identities are frozen before replay; replay cannot inflate the online cost.

The semantic assessment checks actual endpoint input demands, acquisition and observation scope, legitimate whole-value/conservative demands, and review target/evidence namespaces. A complete or structurally legal response is not sufficient to pass it. An explicit whole-object requirement may justify whole-value demand; merely placing that demand on an acquisition output is not automatically an error. Review findings outside the registered defects require separate assessment rather than automatic false-positive classification.

The fixtures and assessment are assistant-authored. This small paired development validation cannot establish generalized first-response accuracy, retry-rate reduction, semantic completeness, global minimality, or absence of DOE. Results must state separately whether the observed corrections decreased, whether total measured tokens decreased, and whether the required semantic relationships were preserved.

## Observed run: 2026-10-17

The local [run overview](../../experiments/doe/runs/endpoint-prompt-online-v1-20261017-230227/index.html) preserves all eight initial chains and the additional structural correction. The baseline had 4/4 legal initial responses and zero corrections; the latest prompt had 3/4 legal initial responses and one correction. The latest negative review invented an extra `requirement_id_note` field; strict validation rejected it, and the next complete response was accepted. The all-initial-responses-legal gate was therefore not met, and retry reduction was not demonstrated.

| Measurement | Baseline | Latest, including correction |
|---|---:|---:|
| Logical requests / HTTP attempts | 4 / 4 | 5 / 5 |
| Input tokens | 64,776 | 104,034 |
| Output tokens, including reasoning | 177,782 | 113,103 |
| Total tokens | 242,558 | 217,137 |
| Sum of request seconds | 826.239 | 538.051 |

All nine attempts supplied usage; there were no HTTP retries, truncations, JSON normalizations, semantic repairs, or quality reruns. The request used `deepseek-v4-flash` with `reasoning_effort=max`; the API reported `deepseek-flash`. Actual online wall time was 1,384.703 seconds. Zero-API replay matched all eight recorded decisions after metrics were frozen.

The latest annotation established field-value demands on the actual delivery inputs where the baseline had only upstream construction seeds. Both arms preserved whole acquisition and the legitimate whole-value control. The latest negative review identified both registered defects; the baseline identified the missing receiver demand but accepted the excessive acquisition seed. The latest review also raised source-supported omissions in the authored Task and sensitivity fixture, which are recorded as additional findings rather than automatic false positives. Its repair wording still needs care: preserving the actual construction does not imply retaining redundant upstream demand seeds.

Observed total tokens fell by 10.48%, while input tokens and static prompt size increased. Most output tokens were provider-reported reasoning. This single interleaved sample, with cache and generation variation, does not establish a stable cost reduction or a causal retry improvement. Detailed accepted-response and derivation checks remain external assistant assessments, not an independent expert gold standard.

## Focused recheck: 2026-10-18

The [focused run](../../experiments/doe/runs/review-output-tightening-v1-20261018-111357/index.html) reuses only the two review fixtures, four starting chains. Its baseline is the exact latest Prompt from the previous run. The production edits replace existing review/shared endpoint text: checks have exact permitted fields, explanation belongs in reason, and redundant endpoint-only upstream seeds move while actual operations, independent demands and conservative relations remain. The seven sections and existing full example remain; each Prompt grew by 351 characters/UTF-8 bytes, with no Schema or business-field change.

Disjoint offline groups passed 82 Prompt/semantic, 135 persistence/provenance/sensitivity, 13 subset-runner and 19 existing-runner tests. The first run's one stale wording assertion was updated and its complete group passed on rerun; logs preserve both attempts.

| Measurement | Baseline, including correction | Latest |
|---|---:|---:|
| First completed legal responses | 1/2 | 2/2 |
| Structural corrections | 1 | 0 |
| Logical requests / HTTP attempts | 3 / 3 | 2 / 2 |
| Total tokens | 142,420 | 125,100 |
| Sum of request seconds | 359.023 | 352.631 |

Baseline invented a reason_unused field, rejected at its exact requirement-check path. Its next complete response removed only that field. Latest had no extra fields or normalization. Both arms detected the two controlled defects and accepted the legitimate whole-value/Boolean control. Latest advice explicitly permits relocation, but also tells the repairer to keep construction-level demands, leaving ambiguity in this delivery-only case. It also overclaims a CFG citation's support for annotation operations and misses the Task exclusion reported by baseline. These findings prevent a full semantic-success claim; no semantic repair or quality rerun followed.

Total usage was 267,520 tokens over five HTTP attempts, with no retries. Online wall time was 721.868 seconds, and zero-API replay matched all four decisions. Latest whole-chain tokens were 12.16% lower, but its initial requests alone were 2.91% higher (125,100 versus 121,558). Avoiding the 20,862-token correction explains the whole-chain reduction. Cache distributions differ, so these token totals are not an invoice comparison. This is a development recheck, not held-out accuracy, stable retry improvement, or repair-success evidence. Conditional build.when preservation was checked offline, not by the unconditional live negative fixture.

## Specific demands, CFG evidence and Task exclusions: 2026-10-18

The [targeted run](../../experiments/doe/runs/review-demand-evidence-v1-20261018-114358/index.html) again uses only the two existing English review development fixtures. Baseline initial Prompts are byte-identical to the preceding run's latest Prompts. Both arms share actual inputs, strict validation, correction and transport settings. Only two production files changed: review Prompt instructions/example and the shared endpoint/CFG format explanation. The seven sections, business fields, runtime contract and analysis algorithms remain. The existing calibration example generates its concrete demand references from its own candidate, without importing evaluated Skill fields or answers; no teaching scenario was added. Each Prompt grew by 1,094 characters/UTF-8 bytes, approximately 1.05-1.17%.

Before online requests, the final offline receipts passed 300 distinct tests after JUnit-node deduplication: 142 semantic, 135 persistence/provenance/sensitivity, 16 persistent Task paths, and 7 additional coordinate tests. The focused 25-test receipt overlaps those groups. Earlier development failures and final reruns remain recorded; this is not an all-repository pytest claim.

| Measurement | Exact previous-run latest baseline | Latest |
|---|---:|---:|
| First completed legal responses | 2/2 | 2/2 |
| Structural corrections | 0 | 0 |
| Logical requests / HTTP attempts | 2 / 2 | 2 / 2 |
| Input tokens | 51,552 | 51,980 |
| Output tokens, including reasoning | 62,519 | 72,900 |
| Total tokens | 114,071 | 124,880 |
| Sum of request seconds | 304.765 | 348.662 |

Latest explicitly identifies the two existing redundant upstream content demands, includes their review IDs in finding.target_ids, states the destination receiver input and field paths, and requires removing the original placements while preserving build/selection operations. A read-only call to the actual repair-context builder confirms that those IDs resolve to the two original demands and delivery parent. Baseline gives generic add-or-relocate advice without the exact old placements or explicit removal. No semantic repair was called, so this validates advice resolvability rather than actual repair success.

Both arms separately find the explicit source exclusion missing from Task and the supported sensitivity omission. Latest uses a source-only isolated Task objection, without letting correct field selection or sensitivity replace the Task restriction. Both legitimate whole-object/Boolean controls have zero findings. Both arms preserve whole acquisition/possible observation while rejecting its unsupported whole-value task demand. These observations do not show a paired advantage in Task-prohibition detection: baseline also detected it on this execution.

The strict semantic gate remains **partial**. Latest's additional sensitivity finding says that a CFG result operand contains a named field. The source supports the field, but the actual CFG operand only defines a result symbol; its citation reason mixes source membership with graph identity. Baseline has the same limited overstatement. This is not an invented field or false sensitivity finding, but it fails the preregistered requirement that every CFG citation reason stay within the resolved graph object's facts. The other relevant CFG reasons explicitly distinguish operand identity from annotation demand lists.

All four initial responses were also the final accepted responses; there were no corrections, normalization, transport retries, semantic repairs, quality reruns, connection probes or formal 001/010/013 reruns. Total usage was 238,951 tokens and online wall time was 662.888 seconds. Metrics and call identities were frozen before zero-API replay, which matched all decisions. The requested model was deepseek-v4-flash with max reasoning; the API reported deepseek-flash.

Latest tokens increased 9.48% and summed request time increased 14.40%. No correction-rate or cost improvement is demonstrated. Provider reasoning counts (60,434 baseline; 70,710 latest) are already included in output/total tokens, and prompt cache-hit counts differ (51,200 versus 24,704); these small reused-fixture observations are not invoice comparisons or stable-rate estimates. The [full assessment](../../experiments/doe/runs/review-demand-evidence-v1-20261018-114358/assessment.assistant.html) separates the measured improvement, residual provenance issue, actual costs, and offline versus live coverage.

## Field attribution recheck: 2026-10-18

The [field-attribution run](../../experiments/doe/runs/cfg-evidence-attribution-v1-20261018-121347/index.html) freezes the preceding latest Prompt as its baseline and reuses the same two English review fixtures, four starting chains. The shared CFG rule now distinguishes source-stated member existence/sensitivity from bare result-symbol identity, while still allowing explicit graph literals, paths and constraints as evidence for their actual recorded facts. The review format and self-check apply this boundary to every reason, including relative clauses. The existing complete lesson separates source field relations from graph symbol definition/use. No teaching scenario, business field, Schema rule or analysis algorithm was added; seven sections remain. Each Prompt grew by 454 characters/UTF-8 bytes, approximately 0.43-0.48%.

Offline receipts passed 281 distinct tests: 142 Prompt/semantic, 129 recording/recovery/correction, and 10 new attribution cases after deduplicating the overlapping 21-test focused group. Explicit CFG literals, constraints and metadata remain legal; real references with incorrect interpretations remain structurally legal, with no keyword-based semantic validator. The actual repair request still resolves named demand IDs, and Task prohibitions retain source-only routing.

| Measurement | Baseline | Latest |
|---|---:|---:|
| First complete model responses legal | 2/2 | 2/2 |
| Structural corrections | 0 | 0 |
| Logical requests | 2 | 2 |
| HTTP attempts / transport retries | 2 / 0 | 3 / 1 |
| Input tokens | 51,980 | 52,136 reported subtotal; full total unknown |
| Output tokens, including reasoning | 82,548 | 73,616 reported subtotal; full total unknown |
| Total tokens | 134,528 | 125,752 reported subtotal; full total unknown |
| Sum of request seconds | 406.317 | 374.577 |

The latest negative review retains all four substantive findings. Its sensitivity finding uses source evidence only for member presence/private context. Two CFG citations define/use actual result symbols without attributing field contents to those operands. Both arms retain exact redundant-demand relocation, the separate Task exclusion finding, whole acquisition/observation and the legitimate whole-object/Boolean positive control. Baseline still says a bare result operand contains the private member. The latest passes the preregistered attribution and preservation checks on this sample; this is not a general correctness or completeness claim, and no actual semantic repair was executed.

All four logical requests completed with zero structural corrections or JSON normalization. The latest positive control had one earlier WinError 10060 connection failure, retried under the existing transport policy; that failed HTTP attempt supplied no usage. First-response legality concerns the first complete model candidate, not the first HTTP attempt. Missing usage remains unknown, so the 125,752-token latest subtotal cannot establish full-cost reduction. The combined reported subtotal is 260,280 tokens across five HTTP attempts. Reasoning/cache details are included in those totals, not added again; no invoice comparison is made.

Online wall time was 791.094 seconds. Requested model: deepseek-v4-flash at max reasoning; reported model: deepseek-flash. Call identities and timing were frozen before zero-API replay, which matched all four decisions. There were no quality reruns, Task/annotation generation, semantic repair or formal 001/010/013 reruns. Two reused assistant-authored fixtures cannot establish stable retry rates, generalized accuracy or semantic completeness.
