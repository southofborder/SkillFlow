# Prioritizing — Deciding What Is Actually First

Scope: choosing the order when the list is legitimate and still too long to do at once. If the list itself exceeds capacity, cut first (`overload.md`); this file assumes what remains has to be sequenced.

**Before ordering anything**, read `## Tasks`, `## Goals` and `## Constraints` in `~/Clawic/data/productivity/memory.md` (or the files `## Boxes` names), plus the shared `~/Clawic/data/projects/`. An order that ignores a goal already committed is just a preference.

**Contents:** [The Four Questions](#the-four-questions) · [Ranking Methods and When Each One Breaks](#ranking-methods-and-when-each-one-breaks) · [WIP Limits](#wip-limits) · [Urgency Is a Property of the Requester](#urgency-is-a-property-of-the-requester) · [When Two Things Are Genuinely Equal](#when-two-things-are-genuinely-equal) · [Writing the Decision Down](#writing-the-decision-down)

## The Four Questions

Ask in this order and stop at the first one that produces a clear winner. Most ties break at question 2.

1. **What breaks if this slips a week?** Irreversible loss (a hearing, a flight, a funding window, a customer who leaves) outranks everything reversible, regardless of size.
2. **What unblocks other people?** Work that is somebody else's dependency has hidden multiplier cost: your 1-hour review holding a 3-person team for a day costs 3 person-days, not 1 hour.
3. **What is the cost of delay per unit of effort?** `priority score = value at stake ÷ estimated hours`, computed for the same time window. This is the WSJF idea (Reinertsen) in its usable form: the expensive item is not the big one, it is the one where waiting costs the most per hour spent.
4. **What only you can do?** Everything else is a delegation candidate before it is a scheduling candidate (`delegation.md`).

Worked example: a 6-hour proposal worth 20k against a 1-hour reference call that unblocks a hire. Q1 no irreversible loss either way; Q2 the call unblocks another person; done — the call goes first, and it costs an hour, not a day.

## Ranking Methods and When Each One Breaks

One default: a strict ordered list, one winner per slot. The methods below are tie-breakers for specific shapes of list, not replacements.

| Method | Good for | Where it breaks |
|---|---|---|
| Strict ranked list (default) | Any list under ~20 items with one owner | Needs re-sorting whenever something arrives; that is a feature, do it at the review |
| Eisenhower (urgent × important) | Teaching someone that urgency and importance are different axes | Everything lands in "urgent and important" because urgency is self-reported; useless without a hard cap per quadrant |
| Cost of delay ÷ effort (WSJF) | A queue of comparable work items with real stakes | Requires a value estimate; garbage in, confident garbage out |
| MoSCoW (must/should/could/won't) | Scoping one deliverable with a stakeholder | Degrades fast: everything becomes "must" unless "won't" has entries — an empty won't-list means the scoping did not happen |
| Eat the frog (hardest first) | Days with one dreaded item that poisons the rest | Wrong when the frog is a 6-hour task and the day has 90 minutes; then it is a starting problem (`procrastination.md`) |
| Two-minute rule (Allen) | Clearing small items during a sweep, not during focused work | Becomes an all-day loop of small things if applied continuously; it belongs inside the inbox sweep only |
| Round-robin across projects | Nothing | Guarantees maximum WIP and maximum cycle time — see below |

## WIP Limits

The single highest-leverage constraint in this file, because it is arithmetic rather than judgment.

Little's Law: `average cycle time = WIP ÷ throughput`. At a steady 2 finished items per week, 6 open items average 3 weeks each; 3 open items average 1.5 weeks each. Throughput is identical — only the waiting changes, plus the switching cost that actually lowers throughput.

- Default `wip_limit` is 3 active projects and 1 active task. Starting a fourth requires naming which one is parked and writing it into `## Tasks` with status `parked`.
- The limit applies to *started* work, not to the list. A 40-item list with 2 things in flight is healthy; a 6-item list with 6 in flight is a stall.
- Parking is not abandoning: a parked item keeps its next action written down, so restarting costs minutes instead of a re-read.
- Signal you are over the limit: several items in progress for more than two weeks with no visible movement. Age of work in progress, not count of tasks, is the honest health metric.

## Urgency Is a Property of the Requester

Urgency travels with whoever asked, not with the work. Three defenses:

- **Ask for the actual date and what happens then.** "When do you need it, and what does it block?" A surprising share of urgent requests return a date next month.
- **Default response window, published.** If everything is answered in ten minutes, everything becomes urgent by training (`messages.md`).
- **Same-day yes is where overcommitment enters.** A rule in `config.yaml` under `safety_posture` — "no same-day yes above 2 h" — costs one sentence in the moment and prevents the pattern.

Recency masquerades as priority too: the item asked for most recently feels most important for roughly an hour. Re-sorting the list at the review rather than at each arrival is what neutralizes it.

## When Two Things Are Genuinely Equal

Rare, and usually a sign the criteria are too coarse. Break the tie with, in order: the one with a real external date; the one that unblocks a person; the one already started (finishing beats starting, always); the smaller one, to reduce WIP; a coin. Never split the slot between them — two half-done items is the worst outcome available and it is the one most people choose.

## Writing the Decision Down

- The chosen order goes into `## Tasks` in `~/Clawic/data/productivity/memory.md`, and the parked item keeps its `parked` status and its next action.
- If a project got parked or killed, update its file in the shared `~/Clawic/data/projects/` — `status: blocked` or `cancelled — <date>` with one line of why. A project silently abandoned reappears as guilt in three months.
- If the same criteria settle the order repeatedly, that is a triage policy: save it to `~/Clawic/data/productivity/artifacts/triage-policy.md` with its `## Boxes` line, and apply it without re-deriving it. Deriving a good ordering rule takes a quarter of observation; nobody should pay that twice.
- If a stated priority keeps losing to whoever asked last, that is a `## Friction` line, not a moral failing — and it is what makes the case for the response-window rule.
