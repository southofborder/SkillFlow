# ClawHub privacy audit comparison

The three runs started from the same 100 versioned source packages and 1,673 files.

| Method | Requested model / effort | Workers | Completed | Partial | Failed | Model starts | Starts without usage | Known input + output tokens | Wall hours |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| strong-model | gpt-6.1-sol / high | 6 | 76 | 24 | 0 | 100 | 0 | 6,377,820 | 2.07 |
| semia | gpt-6.1-sol / high | 2 | 1 | 0 | 99 | 401 | 282 | 17,015,483 | 10.72 |
| skillprivus | gpt-6.1-sol / high | 4 | 5 | 52 | 43 | 275 | 0 | 15,136,235 | 7.21 |

## Native outputs

| Method | Native measurement | Cases with a recorded count | Cases with at least one | Recorded total |
| --- | --- | ---: | ---: | ---: |
| strong-model | operation count | 100 | 100 | 1,595 |
| strong-model | potential excess count | 100 | 100 | 606 |
| strong-model | unknown count | 100 | 100 | 623 |
| strong-model | rejected evidence count | 100 | 11 | 22 |
| semia | native finding count | 1 | 1 | 172 |
| semia | validation count | 100 | 8 | 120 |
| skillprivus | move count | 53 | 53 | 2,066 |
| skillprivus | violation count | 53 | 30 | 133 |
| skillprivus | incomplete judgments | 53 | 50 | 368 |

SkillPrivus screened out 3 cases, counted in its completed status. Semia left detection unrun in 99 cases. All three reported their native finding or claim count for 0 cases.

## Where the runs ended

- **Strong model.** All 100 cases returned an answer. Sixteen answers declared incomplete coverage. Source-range review moved another eight cases from completed to partial. It rejected 22 cited rows across 11 cases. The 606 retained excess claims have source locations that passed structural checks.
- **Semia.** Of 100 cases, 92 received no visible model answer, and 2 received answers before a CLI failure stopped synthesis. Five more used their full synthesis budget without producing a valid SDL candidate. The remaining case reached the built-in detector. Across 401 native starts, 119 returned a visible answer. Of the other 282 starts, 264 ended with workspace routing discovery failure, 16 with routing discovery timeout, and 2 at the native request deadline without a terminal turn. These 282 starts have no public usage record. The local prompt hashes and complete prepared-source fences were verified for all 401 starts. [Runtime diagnostics](runtime-diagnostics.json)
- **SkillPrivus.** Two cases completed the full analysis, three were screened out, and 52 were partial. All 43 failed cases had evidence-validation errors, four during screening and 39 during extraction. The screening decisions were still available for 39 cases that later failed extraction. Of 53 cases with a contextual-integrity violation count, 30 had one or more recorded violations. [Case records](results.jsonl)

Semia reached detection only on `clawhub-0413`. The strong model recorded 17 operations and 10 excess claims for that package. Semia recorded 172 findings. SkillPrivus stopped before contextual-integrity judgment because an extraction citation pointed to lines 227–247 and the quoted text matches lines 228–248. [Matched case and result references](runtime-diagnostics.json)

## Interpretation

- The direct baseline used one request per case. Its counts retain claims whose source path and line range passed structural checks.
- Semia used pinned upstream synthesis and the built-in detector. The complete-text renderer applied upstream normalization. The optional recommendation stage was outside this run.
- SkillPrivus used the controlled paper-based reimplementation. Screening, evidence checks and contextual-integrity judgments have separate outcomes.
- Direct excess claims, Semia detector findings and SkillPrivus contextual-integrity violations have different definitions. Accuracy, precision, recall and F1 were not evaluated because this cohort has no independent labels. Worker counts and model-call budgets affect wall hours.
- The direct baseline returned results for all 100 cases in this run. The controlled SkillPrivus arm produced 53 validated operation ledgers. Semia's observed end-to-end availability was dominated by CLI routing failures. With no three-way case carrying all native measurements, the run supports a comparison of availability, failure stage and recorded cost. It leaves relative detection quality undetermined.
- Cached input tokens are part of input tokens. Reasoning output tokens are part of output tokens.

[Summary data](summary.json) · [Case records and native artifact references](results.jsonl)
