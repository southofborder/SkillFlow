# Execution scope and preflight

This is a new three-case execution of the current constraint-enabled formal pipeline. It is not a continuation or reinterpretation of an older accepted response.

- Cases: 001, 010, and 013, executed sequentially.
- The existing selected CFGs and source packages passed the pinned pre-upgrade receipt check: 74 historical files were verified.
- The existing audited English input projection is reused. Case 001 has an explicit translation receipt; 010 and 013 retain the verified English inputs. No CFG extraction is performed.
- Active production source matched the snapshot used for the completed constraint implementation's offline validation before this run was prepared.
- The current interfaces include annotation v15, compiler v9, review v7, pipeline v7, and pilot v8.
- Public model configuration: official DeepSeek endpoint, `deepseek-v4-flash`, `max` reasoning, JSON Output, 600,000 ms timeout, and two transient retries. The credential is neither copied nor reported.
- Each case extracts a new source-only Task, annotates against that sealed Task, and undergoes semantic review. The two repair routes share at most one semantic repair. Structural corrections remain separate and unlimited.
- No connectivity probe, assistant-supplied candidate, manual response repair, or quality rerun is added.

The prior offline results and capability limits are documented in [the implementation report](../../../../docs/doe/constraint-implementation.md). They establish implementation consistency for the tested cases, not real-model semantic fidelity.

Online timings and the 100-file call inventory were frozen before zero-API replay. Token totals use reported HTTP usage exactly once; missing usage remains unknown. The [semantic assessment](assistant-review.md) separately checks constraint fidelity and completeness, separation from positive demands, and the available reduction evidence. Assistant assessment is not an independent human gold standard and was never supplied to the production review calls.

## Online execution receipt

The existing pilot command completed with all three cases terminal, no interruption, and no unstarted case. Its exit code confirms orchestration completed; it does not mean every case succeeded.

- 001: `failed` at annotation after three structural corrections; the final request failed with `IncompleteRead`. No accepted annotation or DOE was substituted.
- 010: `diagnostic`; initial review passed, original annotation selected, propagation complete, DOE partial.
- 013: `diagnostic`; one fixed-Task annotation repair, independent final review, `repair_limit` retained, repaired annotation selected, propagation and DOE calculation complete.
- Counts: 17 logical calls, seven structural corrections, one semantic repair, no Task revisions, 17 HTTP attempts, zero HTTP retries and zero JSON program normalizations.
- Initial joint annotation legality: 0/3. Initial Task responses: 3/3 structurally valid. These observations do not measure general accuracy.
- Known token subtotal: 1,065,598, with one failed HTTP attempt missing usage. Complete consumption is unknown. Reasoning and cache breakdowns are not counted twice.
- Original online time: 4,550.989651 seconds. Metrics preserve original terminal timestamps separately from replay time.

The [final reporting audit](verification/final-reporting-audit.assistant.md) independently checks metric arithmetic, input and implementation identity, selected stages and navigation. No production code, runtime contract, historical response or accepted annotation was modified for this experiment.

## Replay

Zero-API replay completed after final online metrics were frozen. The [replay summary](replay-summary.json) records `api_calls: 0`, no interruption, no unstarted case, and unchanged historical inputs. Its three case decisions exactly equal the original online decisions, including 001's annotation failure. No failed request was resent and no successful output was manufactured.

The [post-replay completion receipt](verification/completion.json) verifies:

- All 100 frozen call files are unchanged; recollected metrics record `call_files_unchanged: true`.
- Original terminal-summary identity and online timing are unchanged.
- All 74 historical files and 12 frozen pilot inputs still match.
- All 164 implementation files sealed by each case still match current files.
- Selected annotation/Task identities and stage decisions remain consistent with the earlier independent audit.

Propagation and formal DOE replay for 010 and 013 returned `matched`. These checks establish reproducibility of the saved material and computation, not semantic fidelity or absence of DOE. The [earlier audit snapshot](verification/final-reporting-audit.assistant.md) correctly records replay as pending at its own time; this completion receipt supersedes only that pending execution status, without rewriting the snapshot.

Final navigation was refreshed through the existing reporting helper, with a run-local semantic summary and links to the actual Task Markdown reports. The [navigation receipt](verification/navigation.json) records 354 valid local links across 41 report files. No production reporting implementation was changed.

## Scope of validation

This turn is an online validation of the already implemented contract. It does not claim a new full-repository test run. Prior offline implementation results remain separately documented in the linked implementation report.

No supported reduction was produced in these three cases. The run verifies recorded computation and frontend/backend separation for the available artifacts, but it does not supply a positive online example of a valid field reduction with constraint-preservation grounds. The source-fidelity gaps and unsupported review findings remain visible in the case assessments.
