# General correction implementation and the sole fresh GA4 result

The general fix is implemented and offline accepted. The fresh GA4 analysis
**failed structurally, without a native timeout**, and its sole zero-call replay
matched. This run did not reach processing, field-level input assessments or DOE.
It does not establish that the earlier processing timeout is resolved.

The accepted implementation is
`ce895cd759ec42da20bb93a2f1efcf8699078f7233047f7caf4f31908f1cdc69`:
complete shared-output grammar, bounded definite raw-format diagnostics, typed
CFG causal evidence and correction permissions based on actual dependencies.
Strict acceptance and complete source/contracts remain required. Offline evidence
contains **2,367 distinct latest passes, one Windows symlink-privilege skip and
zero unresolved failures**. Original failures and corrective receipts are
preserved; this is not one all-green or whole-repository execution. See the
[offline assessment](../processing-correction-20261117/offline-assessment.en.md).

Exactly one new run was dispatched:
`document-guided-ga4-processing-correction-high-20261117-110830`, with the same
16-file source, fixed CLI, `gpt-6.1-sol/high/openai`, seven configured normal
requests, two workers and unchanged correction/repair/transport budgets.
Analysis took **2,201.020 seconds**. Its actual stages were:

| Stage | Actual result |
| --- | --- |
| Task / flow | Accepted on their first responses |
| CFG | First response rejected; one block corrected; later compiler errors remained |
| Processing / correspondence / sensitivity | Skipped because an accepted CFG was unavailable |
| Source review | Five Task findings retained, one CFG finding quarantined; correction exhausted |
| Shared semantic repair | Unused because its entry conditions required an accepted CFG or selected annotation |
| Propagation / input assessments / DOE | Not run; there is no established deletion result |

Three distinct causes explain the result.

1. **The one CFG correction did not receive all independently detectable errors.**
   The first wire preflight stopped at missing dispatch inputs in block183.
   The 2,039-character correction replaced only that block; every other block,
   edge and entry stayed identical. Compiler validation then exposed pre-existing
   self-reads in blocks222 and234 and ten endpoint errors caused by rejecting
   those blocks. The new causal evidence correctly identified that relationship,
   but arrived after the one correction was spent. Actual dependency-closure
   editing was therefore not exercised. The original response had 258 blocks,
   619 instructions and 246 edges; it was never an accepted CFG.
2. **Failed-stage review guidance and the allowed target inventory disagreed.**
   The prompt permitted `stage:<owner>` for an actual failed stage, and listed
   graph as failed. The inventory contained only 76 Task targets, with no graph
   stage target. Both review attempts were rejected for `stage:graph`. The
   correction returned `{"replacements":[]}`, leaving the allegation unchanged.
   The relevant source-review implementation is unchanged from this task's
   baseline. This is a latent target-contract gap, not evidence that arbitrary
   stage strings should be accepted.
3. **Repair admission independently excluded this failure state.**
   Even if the graph finding had a legitimate target, the runner required an
   accepted Task and CFG for upstream or fragment repair, or an already selected
   annotation. These conditions were false. Fixing the target inventory alone
   would not enter shared repair. Local review isolation itself worked: five
   Task findings survived and only one CFG allegation was quarantined.

The [stage evidence](processing-stage-failure-final.en.md) binds the exact code
locations, prompts, candidates, diagnostics, isolation result and routing gate.
The [source/CFG audit](rejected-cfg-source-audit.en.md) found authored boundary
records for all 13 remote sites, 25 save callers and seven filesystem sites in
the rejected candidate. These are candidate-presence counts, not accepted graph,
field-level caller-to-writer or propagation coverage. The separate Task audit
also retains three storage evidence ranges ending one line before their actual
save statements. No analyzed Skill was changed or executed.

Actual cost was **six native starts: four normal requests and two structural
corrections**, with zero semantic repair calls and zero outer retries. All six
native processes exited with code 0 and have final public usage: **568,349 input
+ 67,678 output = 636,027 tokens**. Cached input and reasoning tokens are subsets;
unreported provider-internal retry usage and billed currency remain unknown.
The configured seven-request schedule is not a claim of seven successful calls.

The first CFG process completed after **1,796.828 seconds**, returning 176,427
characters. It recorded one internal server WebSocket closure; Task and flow
each recorded an early reset followed by a request timeout and then completed.
Five stderr sampling retry lines overlap two stdout notices; they must not be
summed as independent calls. No 2700-second native deadline was reached. Complete
deliveries ranged from 186,460 to 389,408 characters, below the unchanged adapter
limit. Public elapsed times and polling intervals do not measure pure generation
time. See the [cost/timing evidence](final-cost-provenance.en.txt).

The sole controller-owned replay matched in **9.336 seconds**, with zero new
starts and an unchanged complete native marker inventory. All 208 runtime pins,
16 source files, helpers and executables matched. Independent observation queried
all eight recorded wrapper/controller/native PIDs and found none remaining;
an initial empty-PID observation was preserved as invalid and superseded.
All 488 baseline-protected historical files were checked separately at closeout.

The [follow-up proposal](followup-plan.zh.md) prioritizes same-budget diagnostic
aggregation, one authoritative failed-stage target policy, then an explicit
decision and tests for missing-CFG repair admission. These are proposals only.
No second fix or additional run/replay was performed. This run and its sole
replay are closed; the authorization is consumed.
