# Planning — Days, Weeks, Quarters, and Estimates That Hold

Scope: turning a prioritized list into a plan with hours in it, and making the estimates less wrong over time. Horizon comes from `planning_horizon`; block length from `deep_work_block_min`.

**Before planning**, read `## Constraints`, `## Energy Patterns`, `## Calibration`, `## Tasks` and `## Due` in `~/Clawic/data/productivity/memory.md` (or the files `## Boxes` names), plus the shared `~/Clawic/data/projects/`. Planning around a school run you were told about last month is the difference between a plan and a fantasy.

**Contents:** [Capacity First, Always](#capacity-first-always) · [Estimation](#estimation) · [The Weekly Plan](#the-weekly-plan) · [The Daily Plan](#the-daily-plan) · [Time Blocking](#time-blocking) · [The Quarter](#the-quarter) · [When the Plan Breaks Mid-Week](#when-the-plan-breaks-mid-week) · [What to Write Down](#what-to-write-down)

## Capacity First, Always

A plan that has not stated its capacity is a wish list with dates on it. Four numbers, in order (SKILL.md Capacity Math):

1. `capacity = focus_hours_target × working days − meeting hours`. Default: 3 × 5 − 6 = 9 h of real focus in a normal week.
2. `committed load = Σ (estimate × ratio)` from `## Calibration`.
3. `overcommitment = load − capacity`. Positive means something is cut today.
4. `safe fill = capacity ÷ ratio` — the hours you may actually schedule. With a 1.6 ratio and 9 h capacity, schedule about 5.6 h and leave the rest open.

The unscheduled remainder is not slack to be recovered by a better calendar; it is where the overruns land. Take it out and every overrun becomes a missed commitment instead of an absorbed one.

Applying `commitment_posture` on top: `conservative` multiplies the load by a further 1.3 before comparing, `balanced` by 1.0, `aggressive` by 0.85. Aggressive is defensible for one sprint before a hard external date, never as a standing setting.

## Estimation

Estimating is a measurement problem, and the measurement is personal.

- **The ratio.** `ratio = Σ actual ÷ Σ estimated` over the last 5-10 pairs in `## Calibration`. Until five pairs exist, use 1.5 and say out loud that it is a placeholder rather than a finding. The planning fallacy (Kahneman and Tversky) survives experience and expertise; it does not survive a multiplier drawn from your own history.
- **Estimate the piece, not the project.** Anything estimated above 4 hours is a container, not a task: break it until each part is between 30 minutes and 4 hours, then sum. Sums of small estimates are wrong by a smaller factor than one large estimate.
- **Keep a separate ratio per work type when they diverge.** Writing and reviewing behave differently; if writing runs 2.0 and review runs 1.1, one blended 1.6 makes both plans wrong. Split only when you have five pairs on each side.
- **The estimate is recorded before the work, not after.** An estimate reconstructed afterwards is a memory of the outcome.
- **Anything involving another person gets calendar time, not work time.** A 20-minute review that needs a colleague is a 3-day item; put the dependency date in `## Commitments` as `owed to me`.

Worked example: five items estimated at 1, 2, 2, 1, 3 = 9 h. Ratio 1.6 → load 14.4 h. Capacity 9 h. Overcommitment 5.4 h → cut two items now, or move one date. Doing this on Monday costs one message; doing it on Friday costs a reputation.

## The Weekly Plan

Twenty minutes, on the day before the week starts or the first hour of it, using `week_start`.

1. **One priority for the week.** The thing that, if it alone landed, makes the week a success. One, not three.
2. **Read the constraints and the calendar.** Fixed points first: meetings, the school run, on-call, therapy, travel.
3. **Compute capacity** with the actual meeting hours of that week, not the average one.
4. **Place two or three protected blocks** in the user's peak window from `## Energy Patterns`, one of them on the week's priority, on the earliest day it can go — the week's later days are always the ones that evaporate.
5. **Fill to `safe fill`, then stop.** The remaining items stay in `## Tasks` unscheduled.
6. **Name the deletions.** What is not happening this week is stated explicitly, so it is not a silent debt.

## The Daily Plan

Five minutes, at the end of the previous day rather than the start of the current one — the evening version costs less willpower and removes the morning decision.

- **One must-win**, plus at most two secondary items. Three real items is a full day once meetings and messages are counted.
- **Every item carries its first physical action**, written in the item: "open the migration doc, list the three tables" — not "work on migration".
- **Match to energy, not to importance**: hard work in the peak window, admin in the trough. Reversing this is the single most common cause of "I had time and did nothing".
- **The lists that survive contact** end with a shutdown step: what tomorrow's must-win is, written before the laptop closes (`artifacts/shutdown-routine.md` if one exists).

## Time Blocking

- A block is an appointment whose title is the task, not the topic. "Deep work" as a block title is how blocks get traded away.
- Default length is `deep_work_block_min` (90). Below ~50 minutes there is not enough runway for demanding work; above ~120 most people's return drops sharply.
- 10-15 minutes between blocks, minimum. Back-to-back blocks turn the first overrun into a cascade for the whole day.
- **Interrupt rate decides whether strict blocking works at all.** Above roughly one unavoidable interruption per hour, blocking a full day produces a daily record of failure: block one window, run a list around it.
- A blown block is data, not sin: record planned vs actual in `sessions/<year>.md` and it becomes the block length that fits.
- If `calendar_owned` is false, blocks go in as declinable holds and the defense moves to influence (`meetings.md`).

## The Quarter

Every 13 weeks, one hour. Only three questions matter, and the third is the one people skip.

- **What are the two or three outcomes for this quarter?** More than three is a list of hopes; each needs a date and a project in the shared projects box.
- **What is being explicitly not done?** Written down, so it stops generating background guilt.
- **What did last quarter's goals actually do?** Each one closed, renewed with a new date, or cancelled with a reason. A goal that survives three quarters by inertia is a goal nobody believes in — cancel it out loud.

## When the Plan Breaks Mid-Week

It will. The response is a cut, not a rewrite: rewriting the plan resets the measurement and hides the overrun.

- Keep the original plan visible; strike the items that will not happen and note where they went (next week, dropped, delegated).
- One re-plan per week maximum. If it needs a second, the estimates or the capacity number are wrong — fix the number, not the plan.
- An emergency that consumed the week goes into the review as a capacity fact, so next quarter's planning knows how often emergencies actually happen. Most people plan as if the answer is never; the honest answer is usually one week in four.

## What to Write Down

- Estimate and actual for anything you planned, as a pair in `## Calibration` — and recompute the ratio in the same turn. This is the one habit that makes every future plan better.
- Detail worth keeping (interruptions, planned vs actual block minutes) goes to `sessions/<year>.md`.
- Fixed points discovered while planning (a standing meeting, a care schedule) go to `## Constraints`; long ones to the file named by `constraints_file`.
- The week's cuts and the week's one priority go into the current `reviews/<year>.md` entry at review time.
- A planning template the user actually keeps using goes to `~/Clawic/data/productivity/artifacts/weekly-plan-template.md` with its `## Boxes` line — the format that survives is personal and worth not re-deriving.
