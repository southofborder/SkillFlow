# Ranked follow-up from the closed current GA4

Proposal only. This note changes no production code, prompt, controller, frozen
artifact, test or budget. The current run and its sole replay are closed. A later
implementation and any later real experiment must not reuse their authorization.

1. **Synchronize the entire processing wire grammar with every relevant prompt.**
   This has the clearest direct evidence: a001 duplicated the root table and
   used mnemonic names, while the prompt only illustrated `v0`. Publish the exact
   identifier pattern, unique root members and definition names, one final table,
   reference/escape shapes, finite expansion and complete payload obligations from
   the same grammar source used by the codec. Apply it to initial processing,
   revision, local correction and full fallback. Give a small payload-first,
   single-final-table example with forward references and an escaped literal;
   allow the existing plain complete response. Do not relax name, duplicate,
   reference, expansion or fragment validation. Offline tests must assert the
   actual rules in generated prompts, not merely the presence of `v0`.

2. **Expose independent raw-wire errors in the existing one correction.**
   Add an optional bounded, read-only object-pair diagnostic scan after strict
   parsing rejects an identifiable shared envelope. For the observed a001 it
   could report both duplicate table occurrences and invalid definition/reference
   name syntax, without choosing any definition. Keep root rejection, raw hash
   and text, occurrence-qualified raw locations, exact grouped counts and bounded
   examples. Do not expand references or run schema/semantic checks on ambiguous
   data. On scan limits or broken syntax, state the precise diagnostic limitation
   and keep the complete replacement fallback with all source and raw candidate.
   Test identical, disjoint and unequal duplicate tables, marker escapes, invalid
   names, accurate locations, resource limits and unchanged call counts. The
   detailed boundary is in `processing-pair-diagnostic-followup.en.md`.

3. **Preserve causal ownership of graph validation failures before choosing
   correction scope.** The observed missing-endpoint root diagnostic was caused
   by two blocks already rejected for local read-before-definition errors. Record
   this relation explicitly instead of treating every cascading root error as an
   independent reason to regenerate the whole graph. Compute the repair scope
   from primary owners plus actual producer/control/edge dependencies; in this
   case a head-only replacement is not justified because body carry producers
   were missing. Keep the root evidence, full source and strict whole-graph checks
   on the merged candidate. An unexplained endpoint or an unbounded/uncertain
   dependency closure still requires complete replacement. Offline tests should
   distinguish true missing endpoints from rejected-block cascades, include both
   loop heads and bodies when needed, and reject incomplete local repairs. No
   saving can be claimed from the 1,250-character two-head inventory alone.

4. **Keep timing diagnosis separated from representation diagnosis.** The saved
   correction process hit the total 2,700-second deadline and public logs show
   three internal retry causes. Preserve the current native/outer retry budgets,
   failure receipts and terminal replay. Reconcile public event intervals, complete
   delivery sizes and known/unknown usage without classifying elapsed time as
   generation or assuming a new network-only timeout. The observed whole-output
   correction workload is worth preventing, but shortening it cannot promise that
   a network-reset or server-closed stream will complete. Transport changes need
   their own concrete evidence and offline acceptance; increasing deadlines or
   retries is not part of this proposal.

Before considering another real experiment, injected offline regressions should
cover this malformed shared response shape, single-correction completion and
failure, plain/shared logical equivalence, graph dependency closure and strict
full validation, source-preserving correction input, fatal receipt replay and
unchanged seven-normal-request/two-worker/budget policy. Do not migrate or repair
the closed experiment's records. Existing input display gains should be retained;
no additional source or contract truncation is proposed.

The expected benefit is reducing avoidable representation failures and broad
regeneration. Actual output-size, timing and semantic benefit remain hypotheses
until valid later outputs provide evidence.
