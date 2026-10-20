# Reviews — The Loop That Keeps the System Trusted

Scope: the weekly, monthly and quarterly resets. A review is the only mechanism that removes dead items, and a list nobody prunes stops being read within about a month — which is how systems die, not by being badly designed.

**Before running any review**, read `## Tasks`, `## Commitments`, `## Goals`, `## Due` and `## Friction` in `~/Clawic/data/productivity/memory.md` (or the files `## Boxes` names), the last two entries of `reviews/<year>.md`, and the shared `~/Clawic/data/projects/`. A review that does not compare against the last one is a planning session with a nostalgic name.

**Contents:** [The Weekly Review](#the-weekly-review) · [The Monthly Review](#the-monthly-review) · [The Quarterly Reset](#the-quarterly-reset) · [Deleting Without Guilt](#deleting-without-guilt) · [When Reviews Keep Being Skipped](#when-reviews-keep-being-skipped) · [Restarting After a Long Gap](#restarting-after-a-long-gap) · [What to Write Down](#what-to-write-down)

## The Weekly Review

Thirty minutes, on `review_day`, at the same time each week — a floating review is a skipped review. Six steps, in order; the order matters because closing before planning is what prevents carry-over from becoming invisible debt.

1. **Close the week.** What shipped? Say it explicitly, including the small things — the week always feels emptier than it was, and that feeling is what erodes trust in the system.
2. **Sweep the inboxes** to empty (`capture.md`), including the physical ones.
3. **Walk `## Commitments`.** Anything `owed to me` past its date gets a nudge drafted now; anything `owed by me` gets a date or a renegotiation message.
4. **Prune `## Tasks`.** Every item: still true, still mine, still worth it? Third carry-over means decide it now — do it, delegate it, or kill it (`procrastination.md`).
5. **Check the numbers.** Planned vs actual hours; add any estimate pairs to `## Calibration` and recompute the ratio. This is the step that makes next week's plan better, and it is the first one people drop.
6. **Set next week**: one priority, capacity computed, protected blocks placed, and an explicit list of what is not happening (`planning.md`).

Five questions if the full version is too heavy: what got done, what stalled, what should be dropped, what is blocked on someone, what is the one priority next week. That version takes ten minutes and keeps the loop alive; a heavy review that gets skipped is worth less than a light one that happens.

## The Monthly Review

Forty-five minutes, once. Different altitude — patterns, not items.

- **One pattern from the four weekly entries.** Where did the hours actually go versus where they were planned? What kind of item keeps carrying over? Which day of the week keeps collapsing?
- **Goal check.** Each goal in `## Goals`: on track, at risk, or dead. "At risk" with no change decided is "dead" with better manners.
- **Calibration review.** Is the ratio moving? A ratio that keeps rising means scope is growing during the work, not that the estimates are worse.
- **One change for next month**, stated as a rule rather than an intention: "no same-day yes above 2 h" rather than "be more careful about commitments". One change, not five.
- **Habit check** (`habit-building.md`): which are running, which broke, which to drop.
- **Constraint sweep**: has anything permanent changed — a new standing meeting, a schedule, a person? Update `## Constraints`, because every plan reads from it.

## The Quarterly Reset

Ninety minutes, every 13 weeks. This is the only review that is allowed to change the shape of the system.

- **Close each goal explicitly**: hit, renewed with a new date, or cancelled with a reason. Nothing survives by inertia. A goal in its third quarter unfinished is either the only goal now or it is cancelled.
- **Two or three outcomes for the coming quarter**, each with a project file in the shared `~/Clawic/data/projects/` and a date.
- **Empty `## Someday` out loud.** Anything parked over a year: promote it with a date or delete it. A someday list that only grows becomes a museum of guilt.
- **Audit the recurring load**: every meeting (`meetings.md`), every `## Due` row, every tracked thing. Each one justifies itself or goes. Recurring commitments are the only load that grows without anyone deciding.
- **Review the system itself.** What part of this was not used in three months? Delete it. Complexity added in a good quarter is what makes the system unusable in a hard one.
- **Check the closed-project list**: anything in the projects box closed for over a quarter moves to `projects/archive/`.

## Deleting Without Guilt

The review's actual product is deletions, and this is where most reviews fail — people carry items forward because deleting feels like admitting something.

- **Deleting is not failing; keeping a dead item is.** Every dead item taxes the reading of every live one, so the cost is paid on the whole list.
- **The 30-day test**: if it vanished silently, who notices within 30 days? Nobody → delete, and do not archive it "just in case" — the just-in-case pile is the graveyard with better lighting.
- **Say who was told.** A dropped commitment that involved another person is not dropped until they know. Draft the message inside the review.
- **Write the deletion down** in the review entry. "What did I drop this quarter" is a question that comes back, usually in a performance conversation, and having the list is worth the two lines.
- **Third carry-over is a decision point, always.** An item that has survived three reviews without progress is not a task; it is a signal about priorities or fear.

## When Reviews Keep Being Skipped

Three consecutive skipped reviews means the review is wrong, not the person. Diagnose in this order:

| Cause | Tell | Fix |
|---|---|---|
| Too long | It gets scheduled and then postponed | Cut to the five questions, ten minutes |
| Bad slot | Friday evening, when the week's energy is gone | Move to Friday morning or Monday's first hour, and put it in `## Due` |
| Nothing to review | The system is not used during the week, so the review has no input | Fix capture first (`capture.md`); the review is downstream |
| Emotionally costly | It reads as a weekly audit of failures | Start with what shipped, and record restarts rather than breaks (`coaching.md`) |
| No consequence | Nothing changes as a result, so it is correctly deprioritized | Each review must end in one deletion and one placed block, or it is not a review |

## Restarting After a Long Gap

Someone returning after months does not need a catch-up review; they need one that produces relief in twenty minutes.

1. **Do not process the backlog.** Everything older than 30 days goes to `## Someday` or an `artifacts/old-list-<date>.md` in one action.
2. **Rebuild from live sources**: what is due in 14 days, who is waiting, what is on the calendar. Usually under 20 items.
3. **One priority for the coming week**, one protected block, one message sent to whoever is waiting.
4. **Set the next review date before ending the session**, and write it into `## Due`. Without a date, this becomes the last review again.
5. **Name what changed** so the gap does not repeat: a life event, a role change, or a system that was too heavy. That line goes in the review entry.

## What to Write Down

- Every review writes its entry into `reviews/<year>.md` — date, type, what shipped, what stalled, what was dropped and who was told, the capacity numbers, next period's one priority. Create the file with its `## Boxes` line the first time.
- Update the review's `## Due` row with the run date in the same turn; an overdue row is stated at the next session's start.
- Estimate pairs found during the review go to `## Calibration`, with the ratio recomputed.
- Goal outcomes update `## Goals`; project outcomes update the file in the shared `~/Clawic/data/projects/`.
- A pattern named in a monthly or quarterly review goes to `## Friction`, and the rule it produced goes to `config.yaml` under the relevant preference area.
- A review format the user actually keeps using goes to `~/Clawic/data/productivity/artifacts/review-template.md` with its `## Boxes` line.
