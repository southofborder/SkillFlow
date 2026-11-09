# GA4 backend-r3 online assessment

Propagation did not start, and no DOE result was produced. The fresh run failed while expanding its processing answer with `KeyError: 'segments'`. This is an interface implementation defect exposed by an allowed optional-field omission; this run did not reach the r3 propagation or DOE backend. It is not evidence of backend acceleration or a backend convergence failure.

The complete 16-file frozen GA4 package was used with `gpt-6.1-sol / high / openai`, two analysis workers, seven normal stages, one structural correction per stage and one shared semantic repair round. No old answers were imported. The controller has closed and its sole zero-model replay reproduced the failure. All original answers and failure receipts remain unchanged.

## Failure and scope

Task, flow and CFG generation completed. The new CFG has 208 blocks and 468 IR. Processing returned a complete answer, but no processing candidate was accepted and no annotation was selected. Task-correspondence, sensitivity, unified source review, propagation and DOE were not reached. The 468 generated IR are not an engine-reported blocked set: no propagation coverage was calculated.

Three of the answer's 22 bounded case candidates omit `segments`: `ir_027`, `ir_029` and `ir_031`, each at `/segments/0/cases/2`. Each is a `local_error` / `throw` candidate. The emitted format marks this field optional, and the typed case supplies an empty-list default. The expander then serializes with `exclude_unset=True` and directly indexes `case["segments"]`, losing the default and raising the exception. The first unsafe access is at frozen `annotation_wire.py:501`; further direct accesses also exist. This location is derived from saved source and answer inspection; the saved receipt does not contain a Python traceback.

The relevant interface files are byte-identical to their paused-v9 versions. The defect predates r3. The immediate omission is valid; that does not establish that the rest of this large processing answer would pass later validation or source review after the defect is fixed. See the [separate static diagnosis](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/ga4-failure-audit/diagnosis.en.md) and [exact evidence](D:/projects/SkillFlow/output/verification/backend-r3-online-20261104/ga4-failure-audit/evidence.json).

Processing's correction allowance was not exhausted. Its `KeyError` was recorded as an implementation execution error rather than a model-correctable structural error. The run's only structural correction belonged to Task. No semantic repair was launched. The batch remains frozen; no answer was patched, no failure was retried and no additional replay was performed.

## Coverage and usefulness

| Measure | Actual result |
|---|---|
| Generated CFG | 208 blocks, 468 IR |
| Propagation | Not started; no processed records or computed coverage |
| Source-boundary propagation | No computed evidence for the 13 inventoried API sites, 25 saveResult sites or 3 source loops |
| Source semantic correctness | Not established by this failed run; no unified review or selected annotation |
| DOE | No artifact; neither an excess conclusion nor a no-excess conclusion |
| Residual blocker | Interface expansion, before propagation |

The independent source inventory is an assistant audit criterion, not human gold. Its counts do not turn absent propagation records into checked source relationships. No general accuracy, precision, recall or direct-GPT advantage can be estimated from this failed case.

## Calls, public tokens and elapsed time

| Measure | Value |
|---|---:|
| Actual native starts | 5 |
| Normal generation requests reached | 4 |
| Structural corrections | 1, Task |
| Semantic repair requests | 0 |
| Extra transport attempts | 0 |
| Input tokens | 459,522 |
| Cached input tokens, already included in input | 61,440 |
| Output tokens | 102,863 |
| Total public tokens | 562,385 |
| Complete / partial / unknown final-response usage | 5 / 0 / 0 |
| Main analysis | 2,033.837 s, 33 min 53.84 s |
| Controller wall time, including replay | 2,047.202 s |
| Sole replay | Matched, 12.542 s, 0 new native starts |

Analysis ran from 2026-11-04 05:23:50.739 UTC to 05:57:44.576 UTC. The controller closed at 05:57:57.940 UTC. There are no propagation, DOE or save component timings because those components were not entered. Native request durations overlap across workers; their sum of 2,341.619 s is not wall time. Public native start-to-finish span is 2,031.572 s. Provider-internal HTTP attempt counts and unreported failed-attempt usage remain unknown. No currency or assistant-audit cost is inferred.

## Scope-aware comparison

The older v8 GA4 run reached propagation and published a partial DOE, processing 29/420 generated IR, with no resolved inventoried API/save sites. It used 18 starts, 2,309,177 public tokens and 12,884.530 s of analysis. The present run stopped earlier and used fewer resources; that is a cheaper failure, not a speedup for equivalent analysis.

The v9 online controller remains paused and has no delivered terminal completion for comparison. The separate fixed-input offline r2 test returned propagation in 1,052.546 s with 326/347 IR processed, then hit its authorized 30-minute combined cap in DOE without a complete DOE/save. That input differs from the fresh 468-IR CFG here. This fresh run therefore does not establish whether r3 completes full GA4 propagation and DOE within a useful time.

## Saved evidence

- [Structured assessment](run-summary.json), including source-scope limits and provenance.
- [Mechanical metrics](mechanical-evidence.json), with original-artifact hashes.
- [Original terminal result](result.json), [processing validation](steps/processing/calls/a001/validation.json), [processing chain](steps/processing/calls/chain.json).
- [Public metrics](metrics.json), [controller closure](controller-finished.json), [sole replay receipt](replay-check.json).

The controller's implementation check reports unchanged files. Final r3 Python SHA is `5ccbc1941be908ff20b15d7a56a631e678285b42a255031d29505ec6a0495637`; broader provenance SHA is `9ae31392bf97b0ae8c5ae75c48d1994e8b303b68cda6d532eb4b96f508c56703`. Source SHA is `3b6eef9f43262d96949e30fe0c39797fe680c578ac5e90bf367da15592445bbd`. This assessment adds documentation only.
