# Independent isolation review follow-up

The three previously reported issues are resolved in the inspected code and pass focused regressions: fragment targets survive receipt regeneration without bypassing same-operation conflicts; malformed annotation-view values raise a typed error; duplicate/conflict hashes identify raw candidate records.

Two additional context edges found during test development were fixed by root: unknown fragment keys with null values are rejected explicitly, and falsey non-dict stage-failure tables no longer bypass validation.

The final new integrity module passed **10/10** cases. One case exercises **60 deterministic malformed source-review JSON variants**; all produced recorded diagnostics, retained the exact candidate/hash, and left the selected material unchanged. No uncaught exception or acceptance bypass was observed in that bounded set. The earlier 7-pass receipt is retained separately and is not added to the final distinct-case count.

Current file hashes and both XML receipts are bound in `independent-isolation-review-followup.json`. Only the new test module was edited by this agent during the follow-up; root owns the production corrections. This is scoped offline evidence, not full acceptance or semantic proof. No model, Skill, historical analysis or historical replay was run, and frozen artifacts were unchanged.
