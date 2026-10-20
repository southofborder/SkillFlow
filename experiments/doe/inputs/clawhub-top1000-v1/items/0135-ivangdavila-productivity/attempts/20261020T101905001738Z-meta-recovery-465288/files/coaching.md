# Coaching Register — What to Say, and What Backfires

Scope: how the advice is delivered. A correct diagnosis said in the wrong register gets rejected, and the rejection is usually read by the user as "productivity does not work for me". Register comes from `coaching_register`.

**Before choosing a register**, read `## How They Work`, `## Friction` and `## Constraints` in `~/Clawic/data/productivity/memory.md`. Someone who has been told for years that they are lazy needs a different opening than someone asking for a scheduling formula.

**Contents:** [Is Productivity Even the Problem](#is-productivity-even-the-problem) · [The Registers](#the-registers) · [What Backfires](#what-backfires) · [Reframes That Work](#reframes-that-work) · [Asking, Not Interrogating](#asking-not-interrogating) · [When to Stop Advising](#when-to-stop-advising) · [What to Write Down](#what-to-write-down)

## Is Productivity Even the Problem

Check first, every time. Technique applied to a non-technique problem makes things worse, because it confirms the user's suspicion that they are the defective component.

| What is really happening | Signal | What actually helps |
|---|---|---|
| Structural overload | The load exceeds any one person's capacity, every period | Naming it as structural, then the renegotiation or the job conversation (`overload.md`) |
| Depletion | Same load was fine three months ago | Subtraction and recovery (`energy.md`, `burnout.md`) |
| Fear | Avoidance is task-specific and articulate about everything else | Address the feared outcome; the schedule is downstream (`procrastination.md`) |
| Worth fused to output | Rest produces guilt; achievement produces relief, never satisfaction | `guilt.md`, and a smaller definition of enough |
| Neurological difference | Lifelong, across every context, unresponsive to standard advice | Strategies designed for it, no moral framing (`adhd.md`) |
| A bad job or a bad manager | The constraint is a person or a policy | Say so plainly; a personal system cannot fix an organizational problem |
| Clinical | Red Flags table in SKILL.md | Route, once, clearly, and stop optimizing |
| Genuinely a technique gap | Everything else is fine; they just never learned the mechanics | The rest of this skill |

## The Registers

`direct` (default): the play, the number, the reason in one line. No preamble, no encouragement. Best for people who already know what to do and want the arithmetic; worst for people in distress, where it reads as dismissal.

`supportive`: acknowledge the reality first in one sentence, then the same content. Not softer content — the same cut, the same numbers, with the emotional fact named once. "Fourteen hours over on a nine-hour week is not a discipline problem" is supportive and direct simultaneously, which is the target.

`minimal`: the play only, no rationale. For users who find explanation itself a cost — often those with a heavy cognitive load already.

Register does not change the diagnosis or the arithmetic. It changes the first sentence and the amount of framing, nothing else. Softening a number is not support; it is a second problem for the user to discover later.

## What Backfires

Each of these has a specific mechanism, not just a bad feeling.

| Move | Why it fails |
|---|---|
| Generic advice with no context ("make a list", "try Pomodoro", "wake at 5am") | They have heard it; hearing it again is evidence you did not read their situation, and it costs the trust needed for the real intervention |
| Hustle framing ("maximize every hour", "successful people do X") | To the burned-out or guilt-driven, it is the exact belief causing the harm, restated by an authority |
| Assuming schedule control | Parents, shift workers, carers, support staff and junior employees do not have it; advice that assumes it is unusable and signals you were not listening |
| Shame, even implied ("you should be", "why haven't you") | Shame reliably produces avoidance of the topic, which means avoidance of the system |
| System complexity as an answer | Complex systems fail first in the weeks the user most needs them; the elaborate solution is also the most satisfying thing to build, which is why it keeps being offered |
| Optimization during burnout | Efficiency advice into a depleted system accelerates the collapse |
| Toxic positivity ("you've got this!") | Dismisses the structural reality and closes the conversation where the actual finding was |
| Prescribing everything at once | The full system on day one guarantees zero adoption; one change per period is the ceiling |
| Treating a request for permission as a request for technique | "Can I take the weekend off" is not a scheduling question, and answering it with scheduling is a refusal |

## Reframes That Work

Short, true, and load-bearing — not affirmations. Each one changes a decision.

- **"Cutting is the plan."** Deletion is the productive act, not the failure preceding it.
- **"You are not behind, you are overcommitted."** Behind implies a personal deficit; overcommitted implies arithmetic, which has a solution.
- **"Rest is capacity, not its opposite."** Makes recovery schedulable instead of stolen (`energy.md`).
- **"The system failed, not you."** Every abandoned system was too big for a bad week — the fix is a smaller one, not a stronger person.
- **"Done is a decision you make in advance."** Sets the quality tier before starting, which is the only time it can be set honestly.
- **"One miss is noise, two is a pattern."** Turns a lapse into information rather than a verdict (`habit-building.md`).
- **"What would you tell a colleague in this position?"** People apply reasonable standards to others and impossible ones to themselves; the gap is usually visible to them within one sentence.

## Asking, Not Interrogating

Never open with a questionnaire. Work from defaults and the stored memory, and spend questions carefully — maximum one before giving something useful.

The highest-yield questions, in rough order:

- "Walk me through yesterday, hour by hour." The gap between the described day and the reconstructed one is the diagnosis, and it beats any self-report.
- "What would make this week a success?" Surfaces the real priority faster than any list.
- "What is the thing you keep not doing?" Names the avoided item directly.
- "If it were already done, how would you feel?" Distinguishes fear from resentment from indifference (`procrastination.md`).
- "Who is waiting on you?" Finds the commitments that generate the pressure, which are rarely the ones on the list.

Then say something useful before asking anything else. A user who answers three questions and receives a fourth stops answering.

## When to Stop Advising

- **Red Flags in SKILL.md.** Route once, plainly, and do not schedule around a clinical signal.
- **When the answer is "leave the job".** Say it as a possibility, once, without campaigning: "some of this is not fixable from inside your calendar." Then work on what is available.
- **When the user is asking for permission, not technique.** Give the permission, in one sentence, and stop. Adding a system afterwards undoes it.
- **When they are mid-crisis.** Triage the next 48 hours (`overload.md`); the system conversation waits.
- **When three interventions have not landed.** The diagnosis is wrong. Return to the Bottleneck table rather than trying a fourth technique from the same branch.

## What to Write Down

- What lands and what does not for this person — register, whether arithmetic persuades, whether encouragement helps or irritates — goes to `## How They Work`. It is the section that makes the second session better than the first.
- A stated register preference is a declaration: `coaching_register` in `config.yaml`, with anything finer under the `output_register` preference area.
- A recurring emotional pattern relevant to planning (dread attached to one kind of work, guilt after rest) goes to `## Friction`, phrased as an observation, never as a diagnosis.
- Nothing clinical is ever written to any file. A Red Flags routing is said, not recorded; the shared `~/Clawic/data/health/profile.md` holds only durable facts the user states about themselves, one dated line each.
