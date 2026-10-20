# Methods — GTD, PARA, OKR, Kanban, Bullet Journal

Scope: choosing a named system, adapting it, and mixing without collision. Recorded in `method`. Default is `none`: the plain loop of capture → prioritize → plan → review works, and adopting a named method is a decision that should follow a diagnosed failure, not precede it.

**Before recommending a method**, read `config.yaml` for `method` and `task_tool`, and `## Friction` in `~/Clawic/data/productivity/memory.md`. Someone who has already abandoned two methods has a failure mode, not a method shortage.

**Contents:** [Pick by Failure Mode](#pick-by-failure-mode) · [The Methods, Honestly](#the-methods-honestly) · [Mixing Without Collision](#mixing-without-collision) · [Adapting a Method](#adapting-a-method) · [Switching Methods](#switching-methods) · [What to Write Down](#what-to-write-down)

## Pick by Failure Mode

| The pain | Method that addresses it | Why |
|---|---|---|
| Dropped balls, no trust in the list | GTD | Its entire design is leak-proof capture plus a review that empties it |
| Everything gets done, none of it matters | OKR, or a quarterly goal set | Forces a small number of outcomes with a date, and makes the rest visibly optional |
| Too many things in flight, nothing finishes | Kanban with WIP limits | The only method whose core mechanic is a hard cap (SKILL.md Rule 4) |
| Notes and files everywhere, nothing findable | PARA | An organizing scheme for information, not a task system — pairs with any of the above |
| Digital tools do not stick; screens fragment attention | Bullet journal | Analog friction is the feature: rewriting a task is an implicit review of whether it still matters |
| No pain, just curiosity about systems | None | Adopting a method to feel organized is the most reliable way to spend a month producing nothing (`procrastination.md`) |

## The Methods, Honestly

**GTD** (Allen). Capture everything, clarify into next actions, organize by context, review weekly, engage. What it genuinely solves: leakage, and the mental load of unfinished loops.
Cost: the weekly review is load-bearing. Without it, GTD degrades into a very large list of stale next actions, which is worse than no system because it looks like one. Contexts (`@calls`, `@errands`) were designed for a world where location determined what was possible; energy and available block length are the more useful axes now.

**PARA** (Forte). Projects, Areas, Resources, Archive — four buckets for information.
What it solves: where does this note go. Cost: the Project/Area boundary generates endless re-filing debates. Rule that ends them: a Project has a finish line and a date; an Area never finishes (health, finances, the team). Archive aggressively — an archive you can search beats a taxonomy you maintain.

**Bullet journal** (Carroll). Rapid logging with symbols, daily and monthly spreads, and migration: at each period boundary, every unfinished task is rewritten by hand or dropped.
What it solves: migration is the best deletion mechanism any method has, because the cost of rewriting forces a judgment. Cost: no search, no reminders, no sharing, and the aesthetic versions on social media are a different hobby with the same name.

**Kanban** (Anderson, from Toyota's system). Columns for workflow state, an explicit WIP limit per column, pull rather than push.
What it solves: parallelism and invisible queues. Cost: needs a real workflow to model — a personal board with To Do / Doing / Done and no limit is a list with extra steps. The limit is the method; without it there is nothing left.

**OKR** (Grove, popularized by Doerr). Three to five objectives per quarter, each with measurable key results.
What it solves: drift, and the absence of an explicit "not this quarter". Cost: designed for organizational alignment, so the personal version inherits ceremony it does not need. Key results must be outcomes ("30 paying customers"), not activities ("publish 12 posts") — the activity version is a to-do list wearing a strategy costume.

**Time blocking / time boxing.** Every hour assigned in advance (`planning.md`).
What it solves: it forces the capacity confrontation, which is exactly why people abandon it — the blown block is a visible failure. Cost: a poor fit above roughly one unavoidable interruption per hour.

**Pomodoro** (Cirillo). 25 minutes work, 5 minutes break, longer break every fourth.
What it solves: initiation, and the recording of how many units a task really took. Cost: cutting a flow state hurts more than the timer helps once the work is moving (`focus.md`).

**Eat the frog** (Tracy). Hardest item first, before anything else.
What it solves: the dread that contaminates a whole day. Cost: fails when the frog is a 6-hour item in a 90-minute morning; then it is a decomposition problem.

**Weekly big rocks** (Covey's illustration). Place the important large items first; small work fills the gaps.
What it solves: the pattern where urgent-small crowds out important-large. It is a scheduling order, not a system, and it composes with everything here.

## Mixing Without Collision

Methods conflict in exactly two places. Everywhere else they compose.

1. **Two capture points.** GTD's inbox plus a bullet journal's daily log plus an app inbox means three, and trust degrades to the least-read one. Pick one capture point regardless of how many methods are in play (`capture.md`).
2. **Two competing review cadences.** A GTD weekly review plus an OKR check-in plus a bullet-journal monthly migration is three ceremonies competing for the same hour, and the loser is skipped silently. Merge them into one weekly and one monthly slot with a combined agenda (`reviews.md`).

The stable combination for most people: **one capture point + a strict ranked list + WIP limit 3 + one weekly review + a quarterly goal set**. That is the intersection of everything above, it fits on an index card, and it survives a bad month.

## Adapting a Method

- **Keep the mechanic, drop the ceremony.** GTD's value is capture plus review; the context taxonomy is optional. Kanban's value is the WIP limit; the swimlanes are optional. Any part you cannot explain the purpose of is ceremony.
- **A method is not a religion, and it is not a personality.** The user who says "I do GTD" and has not reviewed in six weeks does not do GTD; they own a large list. Say it neutrally and fix the review.
- **Adapt only after running it as written for a month.** Adaptations made on day one are almost always removals of the uncomfortable part, which is usually the load-bearing part.
- **Write the adapted version down** once it stabilizes, or the next bad week reverts it silently.

## Switching Methods

Switching costs about two weeks of degraded output plus the risk of losing items in transit. Justified when the mechanism is genuinely wrong for the pain; not justified when the current method is simply not being run.

1. **Diagnose first.** Did the method fail, or was it never executed? Missing reviews means the method never ran, and the next one will fail identically.
2. **Do not migrate the backlog.** Rebuild from live sources (`capture.md`); the backlog is what made the old system unreadable.
3. **Run one cycle before judging** — a full week including a review, or a full quarter for a goal method.
4. **Change one thing at a time.** Switching method and tool together makes the result uninterpretable, and tool changes are the usual disguise for method avoidance (`tools.md`).

## What to Write Down

- The chosen method is a declaration: `method` in `config.yaml`. Any adaptation of it (which parts kept, which dropped) goes under the `conventions` preference area.
- The adapted system, once stable, is worth `~/Clawic/data/productivity/artifacts/operating-system.md` with its `## Boxes` line — a one-page description of how this person's system actually works, which is also what they hand a new manager or assistant.
- Review and reset cadences from the method become rows in `## Due`, merged rather than stacked.
- A method that was tried and abandoned, with why, goes to `## Friction`. It is the single most useful line for preventing the same failed adoption in a year.
- Goal sets produced by an OKR-style quarter go to `artifacts/goals-<quarter>.md`, with each goal's row in `## Goals` and its project in the shared `~/Clawic/data/projects/`.
