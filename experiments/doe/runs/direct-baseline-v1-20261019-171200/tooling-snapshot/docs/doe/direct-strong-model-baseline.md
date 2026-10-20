# Direct strong-model replacement experiment

This experiment tests whether one carefully specified source-only request can
produce (a) a usable task-related sensitive-data minimization audit and (b) a
semantically complete, cross-checkable analysis chain. It deliberately does not
require the model to reproduce SkillFlow identifiers or internal schemas.

The protocol is exploratory. References and semantic assessments are produced by
separate model reviewers, without independent human validation. Historical
SkillFlow output is background, never the oracle. The current experiment does
not compare the two methods using the same underlying model and cannot isolate
an architectural effect from a model effect.

Separate reviewer contexts use the same configured model family as the target.
They reduce access to previous answers and experiment identities, but correlated
model errors and common interpretation biases remain possible.

## Fixed inputs and prompts

The pilot uses the audited English source packages for 001, 010 and 013, with no
independent user request. Their conclusions are relative to declared purpose.
The new source corpus contains four controlled triplets, with independent tasks
and source-explicit mechanisms. Its construction categories are not gold labels.
That explicit mechanism detail makes it easier than many underspecified real
Skills; twelve cases are only four scenario families, not twelve independent
real-world domains.

The maintained templates are in `tools/doe/direct_prompts/`: `audit.txt`,
`chain.txt`, `shared.txt`, and `review.txt`. Shared rules state the abstract
runtime defaults and their exceptions. No evaluated answer is used as a teaching
example. Frozen per-trial prompt snapshots bind the complete source text, task,
rules and deliverable. The independent review also receives exactly the first
visible answer, without gold, scores or correction advice.

The pilot has six original answers and six independent reviews. At most one
development revision may follow; any revision must be recorded and the complete
pilot rerun, without replacing the old results. The held-out phase freezes the
selected templates, runs each of twelve cases in both deliverables three times,
and independently reviews the first repeat only. It has 72 originals and 24
reviews. Quality resampling is forbidden.

The original pilot produced agreement between both assessors: two of three
direct audits satisfied the exploratory reference, all three original chains
did, and both sets of three independently reviewed answers did. The audit error
asserted user delivery for ordinary returns. A separate pilot-only developer
recommended the single allowed revision: the same two-sentence final check of
recipient evidence and conditional preservation premises in both templates.
Final templates live in `direct_prompts/revision1/`; shared rules and the review
template remain unchanged. The complete pilot is rerun without replacing v1.
Consequently the effective schedule has 120 target trials: original pilot 12,
revised pilot 12 and final held-out 96. Previously prepared v1 held-out requests
remain unexecuted; preparation is not a target call. No second revision is allowed.

The original and revised pilot observations are development results; variation
between single samples does not establish that the reminder caused a change.

## Execution and receipts

Each trial uses a new collaboration subagent with `fork_turns="none"`, without
model or effort override. It receives the entire saved prompt as its message;
it is told not to use tools, read files, search, delegate, message or request a
follow-up. The expected runtime configuration is `gpt-6.1-sol / ultra` and is
checked against each trial's own local receipt.

This is protocol isolation, not a hard filesystem/tool sandbox. Base
instructions and available capabilities remain part of the runtime. Tools,
extra turns or configuration mismatch are recorded as violations, not silently
replaced. The currently encrypted collaboration task payload does not permit an
independent receipt-level equality proof between delivered and saved prompts;
where unavailable, the delivery audit records that limitation explicitly.

Only visible final-answer text and allowlisted per-trial metadata are exported.
Usage is filtered by the exact child thread and turn and deduplicated by response
ID. Reasoning and cache fields are subdivisions, not amounts added to total
tokens. Unknown usage remains unknown. No monetary billing amount is inferred.
Root orchestration, reference authoring and scoring are separate from target
trial usage. Raw rollouts and hidden reasoning are not copied into the project.

## Independent assessment

Two separate source-only reference authors write and seal their records before
target output. Identity-masked answer packets hide arm/repeat labels and execution
order. The packet supplies each anonymous answer's requested content so an audit
is not unfairly required to include a full chain. Those requirements and answer
structure reveal artifact kind, and correction notes may reveal review status;
this is identity masking, not complete experimental-condition blinding. Two fresh semantic
assessors check all agreed mandatory source facts, relevant boundaries, judgments,
versions, conditions, recipients and function-preserving reductions. Additional
source-supported findings are not automatically false positives merely because
they were absent from a reference.

Outputs are classified as `satisfies_reference`, `substantive_error`, or
`indeterminate`. Disagreements remain visible rather than automatically becoming
a pass or failure. Source-evidenced follow-up adjudication is stored separately;
it does not rewrite the original scores or target output. Engineering protocol
status and semantic correctness are reported separately.

The useful conclusions are: how often direct audit works on these cases, whether
full-chain reconstruction adds or loses accuracy, which errors one independent
review fixes, and how reproducible those results are. A competitive direct
baseline would leave SkillFlow's empirical advantage unestablished in this
experiment. Neither a perfect small sample nor isolated failures settle the
general value of the method. A same-model comparison is a subsequent experiment.

## Local tools and replay

```powershell
python -m tools.doe.direct_experiment pilot
python -m tools.doe.direct_experiment expanded
python -m tools.doe.direct_experiment revision1
python -m tools.doe.direct_corpus verify
python -m pytest tests/doe/test_direct_baseline.py tests/doe/test_direct_experiment.py -q
```

Preparation makes no model calls. After dispatch, import a particular child with
`python -m tools.doe.direct_baseline import --run-dir RUN --trial-id ID
--agent-name EXACT_CANONICAL_AGENT_PATH --root-session-id ROOT_ID`.

The revision command requires the pilot-only development decision. It preserves
`schedule.json` and writes `schedule-revision1.json`; the latter is the effective
120-call schedule. Dispatch must never execute the superseded v1 held-out IDs.

`python -m tools.doe.direct_experiment review --run-dir RUN --trial-id ID`
prepares, but does not dispatch, its independent review. `direct_assessment
packets` creates identity-masked visible-answer packets; assessor records are
external semantic judgments, not results of structural validation.

```powershell
python -m tools.doe.direct_baseline replay --run-dir RUN --sessions-dir C:/Users/24831/.codex/sessions
python -m tools.doe.direct_assessment report --run-dir RUN
```

Replay re-renders saved prompts, verifies source/output hashes, reparses exact
allowlisted receipt records and regenerates assessment aggregation without model
or network calls. It does not regenerate the same model answer or independently
prove the human-language judgments correct.
