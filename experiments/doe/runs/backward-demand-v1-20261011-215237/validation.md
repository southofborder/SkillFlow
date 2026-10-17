# Backward-demand acceptance record

The analysis is offline. No model requests, Skill executions, reannotation,
upstream migrations, or final sensitivity/DOE judgments were performed.
The candidates and semantic review opinions are assistant-authored offline
materials, not model experiment outputs, gold labels, or independent approval.

## Test evidence

- Full regression: `python -B -X utf8 -m pytest tests -q -p no:cacheprovider`.
- Final affected-area regression: `python -B -X utf8 -m pytest tests/doe tests/common/test_source_lines.py -q -p no:cacheprovider`.
- The initial full regression had one obsolete CLI help-list assertion. Its
  expected command list was updated; existing commands remain checked. Final
  affected-area tests also include output-directory isolation, shared retained
  restriction context, partial-order writes, weak aliases, and deletion.
- The final merged status below uses the most recent result for each test ID;
  repeated tests are not added twice. It is not represented as a second full-suite run.

```json
{
  "full_regression": {
    "failed": 1,
    "passed": 2785,
    "skipped": 1
  },
  "final_doe_and_source_lines": {
    "passed": 283,
    "skipped": 1
  },
  "final_unique_test_statuses": {
    "passed": 2792,
    "skipped": 1
  }
}
```

[Full JUnit record](validation/junit-full.xml) · [Final affected-area JUnit record](validation/junit-final-doe.xml)

## Three-case execution

All 7/8/9 Task requirements remain represented in the goal coverage, and all
6/12/16 recorded sinks have comparisons. Each case was replayed without API
calls. Final business JSON matches the reviewed preflight byte for byte;
the last changes affect output isolation and presentation only.
The baseline verified all frozen Task/annotation files before and after preparation.
The three original propagation fact digests were also checked again here.

| Case | Requirements | Goals | Shared derivations | Sinks | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| 001 | 7 | 16 | 149 | 6 | complete |
| 010 | 8 | 14 | 210 | 12 | complete |
| 013 | 9 | 50 | 418 | 16 | complete |

## Interpretation boundaries

- 001: model-side filter fields remain demanded without becoming notification
  tool arguments. Processed count remains opaque and can retain broader input
  content; the file/model observation is not declared reducible to five fields.
- 010: optional parameter values, member-presence controls, the constructed
  request, and the external response remain distinct. Ordinary return retains
  the response items identity without a fabricated delivery event.
- 013: the environment observation has a field demand for FAST_KEY, while
  response classifiers retain conservative demands on their respective first,
  retry, and archive responses. This is not a final exposure judgment.
- Constraints and prohibitions remain shared review context. Their retention
  is not a verified predicate or a positive demand for prohibited content.
- Nested element scopes that exceed the v1 domain and unresolved prior append
  content retain explicit limitations; they do not authorize deletion.

HTML/Markdown share a presentation model. File links and HTML anchors are
checked statically. Pixel-level browser inspection was not performed because
the browser tool blocked the local file protocol; no workaround was used.
CLI help was also checked from outside the repository without path injection.

Reference validity, deterministic rules, and replay consistency do not prove
semantic completeness, indispensability, global minimization, or absence of DOE.
