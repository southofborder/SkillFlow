# Capture — One Inbox, and Lists Worth Trusting

Scope: getting commitments out of the head and into a place that gets read again. This is the foundation everything else stands on: prioritizing a list nobody trusts is theatre.

**Before working on capture**, read `## Tasks`, `## Someday` and `## Due` in `~/Clawic/data/productivity/memory.md` (or the files `## Boxes` names). Adding a second capture point when one already exists is the most common way this gets worse.

**Contents:** [Why Capture Fails](#why-capture-fails) · [The Rules That Make a List Trusted](#the-rules-that-make-a-list-trusted) · [Phrasing a Task So Future You Can Start It](#phrasing-a-task-so-future-you-can-start-it) · [The Sweep](#the-sweep) · [Sorting: Five Destinations](#sorting-five-destinations) · [Rescuing a Dead List](#rescuing-a-dead-list) · [What to Write Down](#what-to-write-down)

## Why Capture Fails

An open loop keeps consuming attention until it has a destination the mind believes in (Zeigarnik effect). Three failure modes, in order of frequency:

1. **Capture is slower than the thought.** Above roughly 30 seconds — unlock, open app, choose project, add tags — capture stops happening during the moments that produce commitments: meetings, walks, showers, the school gate.
2. **The destination is never read.** Capture without a sweep converts the inbox into a landfill; after the third unread week the mind correctly stops trusting it and goes back to remembering.
3. **There are several inboxes.** Notes app, email flags, chat stars, paper, plus the "I'll remember" bucket. With N inboxes, trust is the trust of the least-read one, not the average.

## The Rules That Make a List Trusted

- **One capture point.** Any tool, chosen for speed of entry only (`tools.md`). Everything else is a source that gets drained into it, not a second list.
- **Capture is dumb, sorting is smart.** Never classify at capture time: no project, no tag, no priority. Classification at capture is what pushes it past 30 seconds.
- **One sweep cadence, written into `## Due`.** Weekly is the floor; daily for high-intake weeks. A capture point with no sweep row does not exist.
- **Everything leaves the inbox at the sweep.** Not "reviewed", left. An item still in the inbox after two sweeps is being avoided — decide it or delete it (`procrastination.md`).
- **Deletion is a feature.** A list where nothing is ever deleted is read as untrustworthy within weeks, because most of it is visibly dead.
- **Capture other people's requests the same way.** A verbal "can you...?" that never gets captured is the classic dropped ball, and the one that costs relationship credit.

## Phrasing a Task So Future You Can Start It

The gap between capture and execution is a translation problem: you write for someone with less context than you have right now.

| Captured as | Fails because | Rewrite |
|---|---|---|
| "Taxes" | A category, not an action | "Download the Q2 invoices from the billing portal" |
| "Follow up with Ana" | No channel, no content | "Email Ana: does the pricing memo need legal review?" |
| "Think about the roadmap" | Thinking is not observable, so it never starts | "List the three roadmap options in a doc, one line each" |
| "Fix the onboarding doc" | Scope unknown; the estimate is impossible | "Rewrite the onboarding doc's first section (30 min)" |
| "Look into CRMs" | Research with no exit condition runs forever | "Pick 3 CRMs and write one line each on price and import" |

Formula: **verb + object + where it happens**, small enough that the first two minutes are obvious. If a next action starts with "figure out", "look into" or "think about", the real first action is the physical thing you would do first — usually opening a specific document.

## The Sweep

Fifteen minutes, on the cadence in `## Due`, usually attached to the weekly review.

1. Drain every source into the one inbox: chat stars, email flags, paper, the notes app, the whiteboard photo.
2. Process top to bottom, no skipping — skipping is how the avoided item survives forever.
3. For each item, one of the five destinations below. No item returns to the inbox.
4. Re-read anything already in `## Tasks` older than 30 days: still true? still yours? still worth it?
5. End with the inbox empty. Empty is the point; the list beneath it does not need to be short.

## Sorting: Five Destinations

| Item | Destination |
|---|---|
| Under 2 minutes, and you are in a sweep | Do it now (Allen's two-minute rule) — never during focused work, only in the sweep |
| A concrete action you own | `## Tasks`, phrased as verb + object + where, with an estimate |
| Multi-step work with an outcome | A project file in the shared `~/Clawic/data/projects/`, with exactly one next action copied into `## Tasks` |
| Someone else's action, or a promise you made | `## Commitments`, with the direction and the person's name pointing at `contacts.md` |
| Interesting, not committed | `## Someday`, with the date parked; reconsidered at the quarterly reset |
| Reference material with no action | Out of the productivity system entirely — notes are not tasks, and mixing them is what makes lists unreadable |

Anything with a hard date also gets the date; anything recurring becomes a `## Due` row instead of a repeated capture.

## Rescuing a Dead List

When someone arrives with 300 items they have not looked at in months, do not process them one by one — that is a week of work and it will not happen.

1. **Declare bankruptcy on the old list**: move the whole thing to `## Someday` in one action, or an `artifacts/old-list-<date>.md` if it is long.
2. **Rebuild from the live sources**: what is due in the next 14 days, what other people are waiting on, what is on the calendar. That is the real list, and it is usually under 20 items.
3. **Mine the archive once, on a timer.** Twenty minutes pulling out anything still alive, then stop. What was not worth 20 minutes of rescue was not worth doing.
4. **Fix the mechanism before refilling**: which of the three failure modes killed it? Rebuilding without that answer buys about six weeks.

## What to Write Down

- Sorted items go to their destination in the same turn as the sweep: `## Tasks`, `## Commitments`, `## Someday`, or a project file in `~/Clawic/data/projects/`.
- The sweep itself updates its `## Due` row with the date it ran.
- A capture channel that keeps leaking (verbal requests in meetings, chat DMs that never arrive) is a `## Friction` line, and the countermeasure is a rule, not more discipline.
- If the user designs an intake or triage rule that works — what always gets deleted, what always becomes a project — save it to `~/Clawic/data/productivity/artifacts/triage-policy.md` with its `## Boxes` line.
- A stated preference about phrasing or tooling (`task_phrasing`, `task_tool`) is a declaration: it goes to `config.yaml`, never to memory.
