# Saved coverage comparison with the retained parent

The selected CFG is identical in both runs (489 IR). Current diagnostic propagation reports 451 processed / 6 unmodeled / 32 blocked, versus parent 470 / 4 / 15. All changes reconcile exactly: 470 - 34 lost + 15 gained = 451.

The 34 losses form four exact tails: `ir_167`–`ir_179` (13), `ir_311`–`ir_317` (7), `ir_329`–`ir_335` (7), and `ir_346`–`ir_352` (7). Each first IR is newly excluded by strict processing validation. `ir_167` binds five undefined output locals; the three loop bodies place nested cases where only ordinary case segments are supported. Their successors are blocked. These four validation gaps were outside the later 27-IR processing-revision scope and remain selected after that revision failed.

The 15 gains are `ir_001`–`ir_013` and `ir_436`–`ir_437`. Current processing models the dotenv interface as a read and metadata logging as count computation plus console delivery; the parent cut these paths at validation-unmodeled `ir_001` and source-unmodeled `ir_436`. Reaching the new summaries does not establish their semantic correctness. The source-backed JavaScript-undefined gaps at `ir_289` and `ir_295` remain in both runs.

Both runs have the same-position `missing_part` diagnostics at `ir_457` and `ir_459`, involving unrefined generated wrappers. Those IR remain counted processed, and the diagnostics do not explain the four new cutoff tails. Current saved diagnostics contain zero typed operation faults.

Source boundary record reach is remote 12/13, save 24/25 and filesystem 7/7. The Search Console request at `ir_173` and save at `ir_177` are blocked behind `ir_167`. Of the 13 previously audited receiver omissions, 12 sites are processed and one is blocked. All eight audited response-tuple projection omissions are processed. Their source-correctness audit is still bound to the selected annotation; these reach counts do not resolve the errors. Loop aggregate-save reach also does not establish nonempty-body coverage when all three child body roots are unmodeled.

The observed coverage decrease is fully accounted for by different generated processing and its strict exclusions. It is not evidence that lossless encoding dropped input material. Input fidelity does not guarantee valid model output or correct source modeling. Separately, graph-repair format/capability defects are documented in `revision-graph-audit.en.md`. The two runs have different implementation pins, including propagation runner/solver and several DOE modules, so this is not a controlled encoding-only or unchanged-backend comparison. No broad absence-of-bugs claim follows.

Exact changed IDs, validation messages, source statuses, wrapper records and implementation differences are in `coverage-parent-comparison.json`. This audit reads saved artifacts only; no model, Skill, backend, validation replay or historical run was executed.
