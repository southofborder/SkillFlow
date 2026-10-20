# Evidence

Scope: finding out whether a design works, with the smallest study that answers the question. Persona and journey-map generation without users is `ux-researcher`; this is testing with actual people and reading the result honestly.

**Contents:** [Pick the Method by Question](#pick-the-method-by-question) · [Sample Size](#sample-size) · [Running a Usability Test](#running-a-usability-test) · [Writing Tasks](#writing-tasks) · [Metrics](#metrics) · [Quick Methods](#quick-methods) · [A/B Tests](#ab-tests) · [Analytics as a Complement](#analytics-as-a-complement) · [Severity and Reporting](#severity-and-reporting) · [Write It Down](#write-it-down)

**Before running anything**, read `## Findings` in `~/Clawic/data/designer/memory.md` and open any `artifacts/research-*.md` its `## Boxes` index names. Re-running a study whose answer is already recorded is the most common waste in this domain, and a finding that reappears is more important than a new one.

## Pick the Method by Question

| Question | Method | Participants |
|---|---|---|
| Can people complete this task? | Moderated usability test | 5 per audience |
| Where exactly do they get stuck? | Same, with think-aloud | 5 per audience |
| Do people understand what this is? | Five-second test | 20-50 |
| Do people know where to click? | First-click test | 20-50 |
| Is the navigation structure right? | Tree test (no visuals) or card sort | 30+ |
| Which version performs better? | A/B test with a real metric | Whatever the power calculation says |
| Why do people do what analytics shows? | Interviews, or session recordings + interviews | 5-8 |
| How usable is it, comparably? | SUS or a task-success benchmark | 20+ |
| What do people actually do all day? | Diary study or contextual inquiry | 5-12 |

**Two questions this table cannot answer**: "which do you prefer?" (preference and performance diverge constantly) and "would you use this?" (stated intent is a poor predictor of behavior). Ask people to *do*, not to *predict*.

## Sample Size

The formula behind SKILL.md Rule 9: `found = 1 − (1 − L)ⁿ`, where L is the probability one participant reveals a given problem. With L ≈ 0.31 (Nielsen and Landauer), five participants surface roughly 84% of problems and ten roughly 97%.

Three qualifications that get dropped when the "five users" figure is quoted:

- **Five per distinct audience, not five in total.** Two genuinely different user groups need ten sessions, because the problems each hits are different.
- **L varies with the interface.** A messy, novel interface has a higher L (problems are everywhere, five is plenty); a polished one has a lower L, and five sessions will miss things.
- **Five finds problems; it does not measure anything.** A 4-of-5 completion rate carries a 95% adjusted-Wald interval of roughly 36-97%. Reporting "80% task success" from five people is a fabricated number, and it will be quoted back for a year.

For a rate you intend to report, plan for 20+ per cell, and state the interval alongside the point estimate every time.

## Running a Usability Test

1. **Write the question first.** "Can a new user connect their first data source without help?" — not "let's test the onboarding".
2. **Recruit for behavior, not demographics.** The screener asks what someone has done recently, not who they are; a screener that lets in the wrong people ruins the study before it starts.
3. **Test the test.** One pilot session, always. It catches broken prototypes, ambiguous tasks and a session that runs 30 minutes over.
4. **Set expectations**: we are testing the design, not you; there is no wrong answer; please think aloud; I will not help, but you can ask.
5. **Shut up.** The most common moderator failure is rescuing the participant. Silence is data. Count to five before speaking.
6. **Ask only non-leading follow-ups**: "What are you looking for?", "What did you expect to happen?", "Tell me what you're thinking." Never "Was that confusing?" and never "Did you see the button?"
7. **Note behavior, not interpretation.** "Scrolled past the CTA three times" is data; "didn't notice the CTA" is already a conclusion.
8. **Debrief the same day.** Findings decay fast, and a session that is not written up within 24 hours becomes an anecdote.

**Unmoderated tests** scale and remove moderator bias at the cost of follow-up questions and of knowing whether the participant was paying attention. Use them for simple, well-specified tasks and for larger samples; use moderated for anything exploratory.

## Writing Tasks

- **Scenario, not instruction.** "You need to expense last week's client dinner" beats "click the Add Expense button", which tests reading, not design.
- **Never use the interface's own words** in the task. If the button says "Compose" and the task says "compose a message", the task has given away the answer.
- **One clear completion state** per task, so success is not a judgment call.
- **Order tasks from independent to dependent**, and reset state between participants — the second participant should not inherit the first one's data.
- **Three to five tasks per session** for a 45-minute slot. More produces fatigue and shallow data.

## Metrics

| Metric | Definition | Watch out for |
|---|---|---|
| Task success | Binary, against a pre-agreed completion state | Partial success needs a rule decided *before* the sessions |
| Time on task | Successful attempts only | Averaging in failures makes a broken flow look fast |
| Error rate | Deviations from the ideal path | Only meaningful if the ideal path was defined up front |
| Assists | Times the moderator had to intervene | The most honest measure of whether it works unaided |
| SUS | 10-item questionnaire, 0-100 scale | 68 is the average in Sauro's benchmark database; ~80+ is top quartile. It is **not** a percentage |
| Confidence rating | Post-task, 1-5 | High-confidence failures are the dangerous ones — the user thinks they succeeded |

SUS is comparative, not diagnostic: it tells you whether this is better than last time or than the benchmark, never what to fix.

## Quick Methods

Cheap enough to run inside a design session:

- **Five-second test** — show the screen for five seconds, then ask what it is, who it is for, and what they could do here. Answers to the first two are the value proposition test; failures here explain most "users don't get it" complaints (SKILL.md It Looks Off).
- **First-click test** — where do people click first for a given task? First-click research (Bailey) found task success far more likely when the first click is correct — on the order of 87% versus 46% — which makes this the highest-value quick test for navigation.
- **Tree test** — the labels and hierarchy with no visual design at all. It separates "the navigation is badly labelled" from "the navigation is badly styled", which no amount of arguing in a review will.
- **Card sort** — how users group concepts, before you invent categories for them. Open sort to discover, closed sort to validate.
- **Preference test** — the weakest method in this list. Useful for brand and aesthetic direction, worthless for usability, and it should never be described as a usability result.

## A/B Tests

- **One variable at a time**, or the result names no cause.
- **Calculate the sample and the duration before starting**, from the baseline rate and the smallest difference worth acting on. A test without a stopping rule gets stopped when it looks good, which is how noise becomes a decision.
- **Run full weeks.** Traffic composition differs by day; a Tuesday-to-Thursday test measures Tuesday-to-Thursday users.
- **Never peek and stop early.** Repeated significance checks on accumulating data inflate false positives dramatically.
- **A flat result is a result**: it means the change did not matter at this sample, which is useful information about where to spend the next effort.
- **Small samples lie loudly.** A conversion difference over a few hundred visits usually is not one.

## Analytics as a Complement

Analytics says *what* and *how many*; research says *why*. Neither replaces the other:

- **Use analytics to choose what to test.** The step with the largest drop-off is where five sessions are worth the most.
- **Session recordings show behavior but not intent** — rage clicks and dead clicks are excellent problem detectors and terrible explanations.
- **Segment before concluding.** An overall metric that has not moved often hides two segments moving in opposite directions.
- **Support tickets and sales objections are free research.** The questions sales answers repeatedly are the objections the page should handle (`marketing.md`).

## Severity and Reporting

Rank every finding, or the team fixes the easy ones:

| Severity | Definition |
|---|---|
| Critical | Blocks task completion, or causes data loss or a wrong irreversible action |
| Serious | Task completed with significant difficulty or an assist |
| Moderate | Slows the user or causes visible confusion, then recovers |
| Minor | Noticed but no measurable impact |

A report that is read contains: the question, what was done and with whom, the findings ranked by severity with the evidence for each (how many participants, what they did), and a recommendation per finding. A video montage is persuasive and is not a report; do both. Findings without recommendations get filed and forgotten.

## Write It Down

- **The study itself** — date, method, participants per audience, tasks, what was tested — → a row in `~/Clawic/data/designer/sessions/<year>.md`, so the research history is visible without opening every report.
- **The full report with severity-ranked findings and evidence** → `artifacts/research-<study>-<yyyy-mm>.md`, its own file, with its `## Boxes` line and a read condition naming the surface or the question.
- **Any finding that changes a design decision** → `## Findings` in `~/Clawic/data/designer/memory.md`: one line, with the date, the surface, what was found, the evidence, and what changed. This is the section that turns an opinion argument into a lookup.
- **A recurring finding across studies** → promote it to `## Pain Points`, because it is a systems problem rather than a screen problem.
- **Participants** are never stored: no names, no contact details, no recordings, no quotes attributable to an individual, under `~/Clawic/data/`. Record the audience segment and the count. A client-side research contact who is a professional relationship goes in the shared `~/Clawic/data/contacts/contacts.md` as a colleague, never as a participant.
