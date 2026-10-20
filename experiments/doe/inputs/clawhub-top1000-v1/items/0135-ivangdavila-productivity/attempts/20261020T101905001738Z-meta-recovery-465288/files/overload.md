# Overload — Triage When Everything Is Due

Scope: the user is drowning right now. This is a cutting procedure, not a planning session. No new system gets built while someone is underwater.

**Before triaging**, read `## Tasks`, `## Commitments`, `## Constraints` and `## Due` in `~/Clawic/data/productivity/memory.md` (or the files `## Boxes` points to), and the shared `~/Clawic/data/projects/`. A triage that starts from what the user remembers under stress will miss the commitment that is actually on fire.

**Contents:** [The Triage Pass](#the-triage-pass) · [The Cut Ladder](#the-cut-ladder) · [Renegotiation Scripts](#renegotiation-scripts) · [Overload That Is Not Overload](#overload-that-is-not-overload) · [After the Fire](#after-the-fire)

## The Triage Pass

Twenty minutes, in this order. Skipping step 1 is what makes triage feel like more work.

1. **Empty the head onto one list.** Everything owed to anyone, including the invisible ones: the email that needs a reply, the form, the birthday. Unwritten commitments are what generate the drowning feeling, not the written ones.
2. **Put a real date and a real estimate on each.** Estimate in hours, before any multiplier.
3. **Compute the arithmetic out loud** (SKILL.md Capacity Math): capacity for the period, committed load = Σ estimate × calibration ratio, overcommitment = the difference. Say the number. "You are 14 hours over on a 9-hour week" ends the argument about willpower.
4. **Cut until committed load ≤ capacity.** The Cut Ladder decides what goes; the amount is fixed by arithmetic, not by mood.
5. **Send one renegotiation message today.** Not three, not later. The cut is not real until someone else knows.
6. **Pick the single next action** and start it inside the session, even for 10 minutes. Triage that ends in a tidy list and no movement re-fills within a day.

## The Cut Ladder

Cut in this order, taking whole items, never a percentage off every item. A plan at 90% on eight things finishes nothing and disappoints eight people.

| Rung | What it means | Test |
|---|---|---|
| 1. Delete | Nobody is waiting; the deadline was self-imposed and invented | If it silently vanished, who notices in 30 days? Nobody → gone |
| 2. Not now | Real, but not this period; it goes to `## Someday` with a date to reconsider | Would you swap it for something already committed? No → not now |
| 3. Shrink | Ship the B-tier version: the memo instead of the deck, the draft instead of the polish | What is the minimum that achieves the actual purpose? |
| 4. Delegate | Someone else can do it at 80% quality, with decision rights (`delegation.md`) | Is your involvement about competence, or about control? |
| 5. Move the date | Renegotiate before the deadline, not after — the cost of a message today is a fraction of the cost of a miss on Friday | Who owns the date, and have they been told? |
| 6. Protect | What survives: fewest items, each with a first physical action | Can each survivor state its next 2-minute action? |

Quality tiers make step 3 usable: **A-tier** is work someone external judges (client deliverable, public writing) · **B-tier** just has to function (internal doc, plan, personal organization) · **C-tier** is done-beats-good (routine replies, throwaway scripts). Overload is nearly always A-tier standards applied to B and C work. Set the tier before starting, never during.

## Renegotiation Scripts

Same structure every time: state the constraint, offer a choice, name the date. No apology first — an apology invites a negotiation about the apology.

- **Move a date:** "X will be ready on <new date> instead of <old>. If <old date> is fixed, I can deliver <reduced scope> by then. Which do you prefer?"
- **Trade, not add:** "I can take that on if <existing item> moves to <date>. Otherwise the earliest I can start is <date>."
- **Decline outright:** "I can't take that on and give it the attention it needs."
- **Escalate the choice upward:** "Here is what is in flight and what each costs. I can do two of the three this month. Which two?" — this converts a personal failure into a management decision, which is what it already was.
- **Buy time honestly:** "Give me until <today + 1 day> and I'll come back with a date I can hold" — only when you will actually do the arithmetic first.

## Overload That Is Not Overload

Three patterns look identical from inside and need a different fix. Getting this wrong wastes the session.

| Looks like | Actually | Go to |
|---|---|---|
| Too much work | One dreaded item generating avoidance across everything else | `procrastination.md` — the list is fine, one item is radioactive |
| Too much work | Fragmentation: total hours fit, but no continuous block exists | `meetings.md`, `focus.md` |
| Too much work | Depletion: the same load was fine in March and is impossible now | `energy.md`, `burnout.md` — cutting alone will not restore capacity |
| Genuinely too much, every period, structurally | The job is designed for more than one person | Name it as a structural fact and route to the role file; a personal system cannot absorb a headcount gap |

## After the Fire

Do this in the same session, before the relief wears off, or the same overload rebuilds within a month.

- Write the cut list into the current `reviews/<year>.md` entry: what was dropped, who was told, and the date. This is how "what did I drop this quarter" stops being a mystery.
- Update `## Commitments` — the dropped rows are deleted, the moved dates are corrected, the delegated ones flip to `owed to me` with the person's name pointing at `contacts.md`.
- Write the intake pattern into `## Friction` if a source keeps producing overload: which channel, which person, which hour of the week. Two occurrences make it a pattern worth a rule.
- If a specific decline or renegotiation worked, save the wording to `~/Clawic/data/productivity/artifacts/no-scripts.md` with its `## Boxes` line, and reuse it — the wording is the hard part, not the decision.
- If overload arrived because a yes was given inside a meeting with no arithmetic, that belongs in `## Friction` too, and the counter-rule ("no same-day yes above 2 h") goes in `config.yaml` under `safety_posture`.
