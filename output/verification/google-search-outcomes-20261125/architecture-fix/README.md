# Isolated proposal: unavailable input in an infeasible sibling case

This directory contains a proposed patch and authored offline verification. It is **not applied to the frozen production source**. No model, network request, Skill execution, or retained-run replay was performed.

`src/skillflow/propagation/failure_scope.py` is a copy of the frozen module with one change in `dependencies()`: use the existing typed selector classification to exclude reads and effects of a case that is definitely impossible on the current available input snapshot. Literal guards use `literal_choice`; result/field guards use `selector_outcomes`. Guard operand reads are always retained. Unknown, missing, or unavailable guard values remain conservative. All protected public ports remain declared writes/clears.

`architecture-fix.patch` is the source-only unified diff. The new regression module is `tests/test_infeasible_case_failure_scope.py`; it can be copied to a production test directory only after the running audit has closed and root authorizes integration. The local `conftest.py` loads the isolated module into the test process without changing any production file.

Verification:

- Original frozen module: all 8 regression variants fail as expected, because an unavailable dependency used only by the impossible sibling blocks the selected case.
- Isolated patch: 20 new regressions and 54 existing protected-outcome, runtime-failure-locality and explicit-loop tests pass: **74 passed**.
- New tests exercise normal/throw mirrors, literal/result-field selectors, outcome-value/operation dependencies, feasible errors, unknown guards and unavailable control inputs.
- Production module SHA-256 is unchanged; see `acceptance.json`, `baseline-tests.xml` and `scoped-tests.xml`.

To rerun only the isolated suite, put the production `src`, repository root and installed offline pytest dependencies on `PYTHONPATH`, set `PYTHONDONTWRITEBYTECODE=1`, then invoke the bundled Python with `-B -m pytest <this-directory>/tests -p no:cacheprovider`. Direct any pytest temporary directory and reports inside this directory. Set `SKILLFLOW_ARCH_FIX_BASELINE=1` only for the original-module comparison; otherwise leave it unset.
