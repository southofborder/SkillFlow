# Focus — Holding Attention Long Enough to Finish

Scope: the mechanics of sustained attention — block length, interruption surface, switching cost, single-tasking. Not starting (`procrastination.md`), not the calendar that leaves no room (`meetings.md`).

**Before changing anything about focus**, read `## Energy Patterns`, `## Friction` and `## Constraints` in `~/Clawic/data/productivity/memory.md`, plus `sessions/<year>.md` if `## Boxes` lists it — the user's real sustained block length is in there, and it beats any default.

**Contents:** [The Two Costs](#the-two-costs) · [Session Design](#session-design) · [Cutting the Interruption Surface](#cutting-the-interruption-surface) · [Single-Tasking Protocol](#single-tasking-protocol) · [Diagnosing a Focus Complaint](#diagnosing-a-focus-complaint) · [Environment](#environment) · [What to Write Down](#what-to-write-down)

## The Two Costs

- **Resumption cost.** After an interruption, returning to the original task takes real time — Mark's UC Irvine studies put the average around 23 minutes, and the interrupted work also comes back with more errors. The consequence is arithmetic: four interruptions in a 90-minute block leave close to zero usable minutes, so a "90-minute block with a few pings" is not a short block, it is no block.
- **Attention residue.** Switching before a task reaches a natural stopping point leaves part of attention on the abandoned task (Leroy). Practical effect: the cost is paid on the *next* task, which is why the day feels foggy rather than interrupted. Finishing a subtask, or writing the one line of what comes next, discharges most of it.

Both costs argue for the same thing: fewer, longer, cleaner blocks — and a written landing point whenever a block ends unfinished.

## Session Design

- **Start at 25 minutes when starting is the problem**, extend to `deep_work_block_min` (default 90) once the work is moving. The timer is an initiation device; keeping it after the work is flowing is where Pomodoro (Cirillo) turns from useful to disruptive.
- **Sustained ceiling: 3-4 hours a day** of cognitively demanding work for most people (Newport), and lower while sleep-deprived. Hours beyond that are shallow-work hours; planning them as deep hours is the root of most broken weeks (`planning.md`).
- **One target per session, written before it starts.** "Work on the report" is not a target; "the methods section drafted" is. A session with no exit condition ends when interrupted rather than when done.
- **End on a landing point.** Stop mid-sentence with the next move known, or write one line of "next: …". Tomorrow's start cost drops from minutes to seconds.
- **Measure planned vs actual once.** Two weeks of pairs in `sessions/<year>.md` gives the user's own sustainable block length, which is usually not 90 and always beats the default.

## Cutting the Interruption Surface

In descending order of effect. Doing only the first two eliminates the majority of interruptions for most people.

| Source | Move |
|---|---|
| Notifications on the device you work on | All off during a block, no exceptions list — an exceptions list is a notification system with extra steps. One escape hatch: a phone number that rings for genuine emergencies |
| Chat presence | Status set with a return time ("back at 11:00"), app closed rather than minimized (`messages.md`) |
| Email and chat in the peripheral vision | Closed, not muted. A visible unread badge is an interruption you deliver to yourself |
| Your own phone | Out of the room. In-pocket is not out of reach, and the reach is the habit |
| Colleagues or family walking in | A visible signal and a stated window: "focused until 11, then free" beats a closed door with no information |
| Your own task-switching | Keep a scratch line for intrusive thoughts, capture in 5 seconds, keep working (`capture.md`) |
| The work itself branching | Note the branch, do not follow it; a refactor discovered mid-task is a task, not part of this one |

## Single-Tasking Protocol

Multitasking is switching, and the switch is the cost. The protocol is short because it has to survive a bad day:

1. One window, one document, one target.
2. Everything that arrives goes to the scratch line, not to the hands.
3. When the pull to switch appears, name it out loud ("I want to check chat") and finish the current sentence or step first. Naming the impulse is what makes it optional.
4. At the end of the block, process the scratch line into the inbox, then take an actual break — not a screen with a different colour.

Exception with a real basis: pairing genuinely shallow work with a low-attention task (laundry, walking) costs little. The failure is pairing two tasks that both need language processing — a call and email are the canonical example, and neither gets done.

## Diagnosing a Focus Complaint

| Symptom | Likely mechanism | Move |
|---|---|---|
| Can start, cannot sustain past ~20 minutes | Interruption surface, or a target too vague to know progress | Cut notifications first, then define the exit condition |
| Cannot start at all | Initiation, not attention | `procrastination.md` |
| Focus fine in the morning, gone after lunch | Normal circadian trough, not a discipline failure | Schedule admin there; protect the peak (`energy.md`) |
| Focus collapsed over months, used to be fine | Depletion or life load, not technique | `energy.md`, `burnout.md` |
| Focus fine at home, impossible at the office | Environment and interruption culture | Environment section, then `meetings.md` |
| Lifelong, across every job and school | Possible executive-function difference | `adhd.md` — the strategies help regardless of diagnosis |
| Only on one specific task | Avoidance attached to that task, not a focus problem | `procrastination.md` |

## Environment

- **Cue separation.** One place, or one specific configuration, that means work. Cue-based state change costs nothing and works within about a week of consistency.
- **Sound.** Familiar and lyric-free is the safe default for verbal work; anything novel and lyric-heavy competes for the same processing. Noise-cancelling headphones also function as a social signal, which is half their value in an office.
- **Visible surface.** One document, no tabs from other projects. The other project's tab is a live interruption you built yourself.
- **Friction in the right direction.** The work opens in one click; the distraction takes four. Blockers help while the habit is being rebuilt and stop mattering afterwards.
- **Body.** Water, food, and a break with movement every block. A trough two hours after a heavy lunch is physiology, not weakness (`energy.md`).

## What to Write Down

- Session numbers — planned minutes, actual minutes, interruption count and source — go to `sessions/<year>.md`; if it does not exist yet, create it with its `## Boxes` line in the same turn.
- The sustainable block length derived from those numbers is a declaration once the user accepts it: `deep_work_block_min` in `config.yaml`.
- A recurring interruption source and the countermeasure that worked go to `## Friction`.
- A peak or trough window that appears twice goes to `## Energy Patterns`.
- A focus protocol that works for one specific recurring task (a weekly report, a hard call) is worth `~/Clawic/data/productivity/artifacts/focus-protocol-<task>.md` with its `## Boxes` line.
