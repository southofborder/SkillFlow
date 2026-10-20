# Delegation and Saying No — Getting Work Off the Plate

Scope: moving work to someone else, and refusing work that should never arrive. Both are the same skill — deciding what you will not personally do — and both fail for the same reason: the decision is made without transferring authority or without naming the trade.

**Before delegating or declining**, read `## Commitments`, `## Constraints` and the shared `~/Clawic/data/contacts/contacts.md`. Handing the third item this month to the same overloaded person is a delegation that comes back.

**Contents:** [What Can Be Delegated](#what-can-be-delegated) · [The Delegation Brief](#the-delegation-brief) · [Levels of Authority](#levels-of-authority) · [Follow-Up Without Micromanaging](#follow-up-without-micromanaging) · [Saying No](#saying-no) · [When You Have Nobody to Delegate To](#when-you-have-nobody-to-delegate-to) · [What to Write Down](#what-to-write-down)

## What Can Be Delegated

Sort the list by the question "why is this mine?" — the honest answer is usually one of four, and only one of them justifies keeping it.

| Answer | Verdict |
|---|---|
| Only I have the authority or the relationship | Keep |
| Only I have the skill, and teaching costs more than the work is worth this quarter | Keep for now, schedule the teaching if it recurs |
| It is faster if I do it | Delegate — this reasoning is true once and false forever after; each repetition compounds the bottleneck |
| I like doing it / I do not trust them / I would have to explain it | Delegate, and notice that the reason is about you, not the work |

The teaching math: teaching costs roughly 2-3× doing it yourself the first time and about 1.2× the second. Anything recurring more than three times pays back inside a quarter. Anything genuinely one-off with a hard deadline does not — do it and move on rather than delegating out of principle.

## The Delegation Brief

Boomerang work — the task that returns worse than if you had done it — comes from a missing piece here. Four lines, always:

1. **Outcome, not steps.** "The report is ready for the board by Thursday" rather than a procedure. Steps produce a person doing your method badly; outcomes produce a person solving the problem.
2. **Success criteria.** What "good" looks like, what must be true, and the quality tier (A/B/C, `overload.md`). Unstated criteria are discovered at review time, which is the expensive moment.
3. **Authority level** (below), stated explicitly. This is the piece most often skipped and the one that causes the most rework.
4. **Date, and one check-in before it.** The check-in is at roughly the one-third point — early enough that a wrong direction costs little, late enough that there is something to look at.

Add context nobody would guess: who cares about this, what was already tried, which constraint is non-negotiable. And say what happens if it slips — the person needs to know whether to escalate or absorb.

## Levels of Authority

State the number, or state the sentence. Ambiguity here is the whole problem.

| Level | Sentence |
|---|---|
| 1 | "Do exactly this and report back" — training or high risk only |
| 2 | "Research and recommend; I decide" |
| 3 | "Decide, but tell me before you act" |
| 4 | "Decide and act; tell me afterwards" |
| 5 | "Own it; I do not need to know" |

Most delegation fails between 2 and 4: the delegator meant 3, the person heard 5, and the surprise costs more than the task. Moving a person up a level is a deliberate act worth naming out loud — it is also the cheapest development tool available to a manager (`manager.md`).

## Follow-Up Without Micromanaging

- **One scheduled check-in beats five drop-ins.** Drop-ins signal distrust and interrupt them exactly as much as they interrupt you.
- **Ask about the outcome, not the method.** "How does it look against Thursday?" not "have you started section 2?"
- **Log it once**: `## Commitments` as `owed to me`, with the person, the date and the last nudge. Chasing from memory is how the follow-up either never happens or happens three times.
- **Nudge on the schedule you set, not when anxiety arrives.** A weekly waiting-on sweep as a `## Due` row makes anxiety unnecessary.
- **When it comes back wrong**, fix the brief, not the person: which of the four lines was missing? Almost always criteria or authority.
- **Accept 80%.** Work returned at 80% of your version, on time, without your hours, is a win. Rewriting it silently teaches the person that delegation to them is theatre, and guarantees the next one comes back at 60%.

## Saying No

Refusal is delegation to nobody, and it needs the same explicitness.

- **Buy the pause.** "Let me check what that displaces and come back to you today." Almost every bad yes is given inside the conversation that requested it; the arithmetic never fits in that moment.
- **Trade, do not add.** "I can do that if <existing item> moves to <date>." This converts a personal refusal into a shared prioritization, which is what it is.
- **Give the choice upward when the requester is your manager.** "Here is what is in flight; I can do two of these three this month — which two?" Managers routinely do not know the queue, and this is the correct escalation, not a complaint.
- **Decline cleanly when it is a no**: "I can't take that on and give it the attention it needs." No apology stack, no elaborate justification — a long explanation reads as an opening position.
- **Say it early.** A no on day one is information; a no on the deadline is a failure, whatever the reason.
- **Beware the small yes.** Requests below the threshold where you check capacity are where overcommitment actually enters. A standing rule (`safety_posture` in `config.yaml`, e.g. "no same-day yes above 2 h") closes exactly that gap.

## When You Have Nobody to Delegate To

Common for freelancers, individual contributors, students and parents. The moves that remain, in order of yield:

- **Delegate to a future decision**: park it explicitly to a dated slot in `## Someday` rather than carrying it as guilt.
- **Delegate to a tool or a rule**: an email filter, a template, a scheduled payment, a standing order in the shared house. Anything decided once is decided forever.
- **Delegate down in quality**: C-tier is a form of delegation to the fact that nobody will notice.
- **Buy it**: hours of cleaning, admin, or childcare that release peak-window hours are usually the cheapest capacity available (`freelancer.md`, `parent.md`).
- **Trade with a peer**: swap the task each of you dreads; both get done faster because neither is avoided.

## What to Write Down

- Every delegated item goes to `## Commitments` as `owed to me`, with the date and the check-in; every promise you make goes in as `owed by me`.
- The person goes to the shared `~/Clawic/data/contacts/contacts.md` — name, key, role, preferred channel, one line of context. Update the existing row rather than adding a second; never write anything private about them.
- A brief worth reusing (a recurring report, an onboarding task) goes to `~/Clawic/data/productivity/artifacts/delegation-brief-<thing>.md` with its `## Boxes` line — the second delegation of the same work should cost minutes.
- Wording that worked for declining or renegotiating goes to `artifacts/no-scripts.md`, the same file `overload.md` writes to.
- A pattern of boomerang work from one source goes to `## Friction`, with which of the four brief lines keeps being missing.
