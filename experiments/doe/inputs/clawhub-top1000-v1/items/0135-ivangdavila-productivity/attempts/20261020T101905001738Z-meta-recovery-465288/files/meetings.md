# Meetings — Getting the Calendar Back

Scope: meeting load, meeting design, and defending time when other people schedule it. Whether the aggressive plays are available at all depends on `calendar_owned`.

**Before proposing calendar changes**, read `## Constraints`, `## Energy Patterns` and `## Due` in `~/Clawic/data/productivity/memory.md`, and `config.yaml` for `calendar_owned` and `deep_work_block_min`. Telling someone with no calendar control to decline meetings is how this skill loses credibility in one sentence.

**Contents:** [The Audit](#the-audit) · [The Cost Formula](#the-cost-formula) · [Declining and Shrinking](#declining-and-shrinking) · [Meeting Design](#meeting-design) · [Recurring Meetings](#recurring-meetings) · [1:1s](#11s) · [When You Do Not Own Your Calendar](#when-you-do-not-own-your-calendar) · [What to Write Down](#what-to-write-down)

## The Audit

Do this before any technique. One hour, once, and it settles most arguments.

1. Export or list two typical weeks of meetings with duration and attendee count.
2. Tag each: **decision** (a choice gets made), **information** (one-way), **coordination** (dependencies synced), **relationship** (1:1s, trust), **ritual** (exists because it exists).
3. Sum hours per tag. Information meetings are almost always the largest recoverable block, and are the ones a document replaces without loss.
4. Compute fragmentation: the number of *free intervals* ≥ `deep_work_block_min`. Five hours of meetings scattered across a day can leave zero such intervals — the total is not the problem, the placement is.
5. State both numbers to the user: hours, and usable blocks. People argue about the first and are moved by the second.

## The Cost Formula

`meeting cost = attendees × duration × loaded hourly rate`. Loaded rate ≈ salary ÷ 1,700 working hours × 1.3 for overhead — approximate on purpose; the ratio is what convinces, not the decimals.

A weekly 60-minute meeting with 8 people at a 60/hour loaded rate costs about 480 per session and roughly 25,000 a year. That number is the argument that gets a recurring meeting cancelled; "it feels like a lot of meetings" is not.

Second cost, usually larger and never on the invoice: a meeting at 11:00 does not cost one hour, it costs the morning, because the 90 minutes before it are not long enough for demanding work. Meetings at the edges of the day preserve blocks; meetings in the middle destroy them.

## Declining and Shrinking

In descending order of aggression. Pick the highest rung the user's position actually supports.

| Move | Wording |
|---|---|
| Ask the purpose | "What decision are we making? I'll send my input if I'm not needed live." |
| Send a delegate or a written input | "Marco is closer to this — he'll represent us and I'll read the notes." |
| Shorten | "Can we do this in 25?" — default meeting lengths are calendar defaults, not estimates |
| Attend part | "I only need the first 15 minutes — I'll drop after the pricing item." |
| Convert to async | "Here is a doc with my answer; comment and we skip the sync" (`messages.md`) |
| Decline with an alternative | "I have a conflict then — happy to do <time>, or answer by email today." |
| Decline outright | "I'm not going to add value there; loop me in on the outcome." |

Two structural moves that outperform any individual decline: **meeting-free half-days** blocked before the week fills, and **batching** — all recurring meetings on two days so the others stay whole. Batching is available even to people who cannot decline anything.

## Meeting Design

For meetings the user runs. Each rule removes a specific failure.

- **No agenda, no meeting.** The agenda is the list of decisions to make, not topics to discuss. Topics expand to the time available (Parkinson); decisions do not.
- **Default 25 or 50 minutes.** The 5-10 minutes buys the transition that back-to-back scheduling steals, and nothing of value is lost.
- **Smallest possible attendee list.** Everyone who is not a decision-maker or a required input is a reader of the notes. Cost scales linearly with heads; value does not.
- **Pre-read instead of presentation.** Send the document, spend the first 5-10 minutes reading it silently, then discuss. The presentation slot is where meetings go to become information broadcasts.
- **End with owner, action, date, out loud.** A decision without an owner is a topic that will return, and it returns at full price.
- **Cancel when the input is not ready.** Holding the slot "since we have it" is how a decision meeting becomes a ritual.

## Recurring Meetings

Recurring meetings are the largest silent cost on any calendar, because nobody re-approves them.

- Every recurring meeting gets an **expiry date** at creation — one quarter — and must be renewed deliberately. This single rule removes most ritual meetings without anyone having to say a meeting is useless.
- Review the whole recurring set quarterly, as a `## Due` row. For each: what decision does it produce? If none in the last month, cancel or halve the frequency.
- A recurring meeting whose agenda is "any updates?" is a status document that has not been written yet.
- Cancelling one slot is not a test — a two-week trial cancellation with an explicit "tell me what broke" is, and almost nothing breaks.

## 1:1s

The one recurring meeting worth defending, for both sides.

- Cadence: weekly for new or struggling reports, biweekly for stable senior ones. Skipping repeatedly costs more than the hour, because it is the channel where problems surface early.
- Owned by the report: their agenda first, the manager's items second. A manager-driven 1:1 becomes a status report and stops producing signal.
- 5-10 minutes of preparation beats 30 minutes of improvisation: last commitments, what they raised last time, one thing to notice out loud.
- Commitments made in a 1:1 go to `## Commitments` with direction and the person's name pointing at `contacts.md` — the fastest trust leak available is forgetting what you promised in a 1:1.
- Move it rather than cancel it; a cancelled 1:1 reads as a ranking (`manager.md`).

## When You Do Not Own Your Calendar

With `calendar_owned: false`, defense moves from refusal to influence.

- **Ask for the outcome, not the time.** "What do you need from me?" often converts a meeting into a two-line answer.
- **Protect one window, not the day.** One recurring block, defended as if it were an external meeting, and named after its actual purpose so it reads as work rather than free time.
- **Make the cost visible upward.** Present the audit numbers — hours by tag, usable blocks per week — to whoever owns the calendar. This is a management decision they can make and you cannot (`executive.md`, `manager.md`).
- **Use the edges.** If the middle is unavailable, the protected block is the first or last 90 minutes; that is a real trade against energy, and it is better than nothing.
- **Ration the negotiation.** Pick the two worst recurring meetings per quarter. Fighting every meeting spends credibility faster than it saves hours.

## What to Write Down

- The audit result — hours by tag, usable blocks, the worst offenders — goes to `~/Clawic/data/productivity/artifacts/meeting-audit-<date>.md` with its `## Boxes` line. It is the evidence for the next conversation and nobody wants to rebuild it.
- The quarterly recurring-meeting review is a `## Due` row.
- Fixed meetings that shape every plan (standup, on-call, a weekly ritual that cannot be moved) go to `## Constraints`.
- Commitments made in meetings go to `## Commitments`; the people to `contacts.md`, name and role only.
- A meeting charter or agenda template that worked goes to `artifacts/` — reusing it is how a meeting stays good after the person who fixed it stops attending.
