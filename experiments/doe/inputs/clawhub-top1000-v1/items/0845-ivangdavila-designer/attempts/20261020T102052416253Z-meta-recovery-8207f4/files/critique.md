# Critique, Presentation and Stakeholders

Scope: the part of the job where the work is judged by people. A design that cannot survive a review does not ship, and most designs die here for reasons that have nothing to do with the design.

**Contents:** [Present the Constraints First](#present-the-constraints-first) · [The Presentation Structure](#the-presentation-structure) · [How Many Options to Show](#how-many-options-to-show) · [Running a Critique](#running-a-critique) · [Giving Feedback](#giving-feedback) · [Receiving Feedback](#receiving-feedback) · [Translating Vague Feedback](#translating-vague-feedback) · [Stakeholders](#stakeholders) · [Deadlock](#deadlock) · [Write It Down](#write-it-down)

**Before a review**, read `## Findings` and `## Brands` in `~/Clawic/data/designer/memory.md` and open any `artifacts/decision-*.md` the `## Boxes` index names for this surface. Most review disagreements are decisions that were already made and never written down; producing the record ends the argument in one line.

## Present the Constraints First

The order that determines whether a review is about the work or about taste:

1. **The problem**, in one sentence, in the user's or the business's terms
2. **The constraints** that were fixed before design started — platform, brand, budget, deadline, technical, legal
3. **The evidence** that informed the direction, if any
4. **The work**
5. **The specific decision being asked for**, and from whom

Skipping to step 4 is the single most common cause of a review that turns into a preference contest: with no constraints stated, everyone evaluates against their own, and every one of them is different.

**Name the decision you need.** "I need a yes or no on this navigation model by Thursday" produces a decision; "here's where I've got to" produces opinions.

## The Presentation Structure

- **State the recommendation up front**, not at the end. An audience that does not know where you are heading spends the whole presentation guessing.
- **Show the work at the fidelity that matches the question.** Wireframes invite structural feedback; polished visuals invite pixel feedback. Presenting a high-fidelity mock when you need a structural decision guarantees you get the wrong conversation.
- **Show it in context**: the screen inside the device, the logo on the actual card, the page at the size people will see it, the email in a real inbox. Work presented on a beautiful gradient background is being sold, not reviewed.
- **Narrate the user's path, not the layers.** "She arrives from the invoice email and needs to confirm one number" beats "here's the header, here's the table".
- **Explain each significant decision with its reason and its rejected alternative.** A decision with a stated tradeoff is defensible; a decision presented as obvious invites someone to prove it is not.
- **Pre-empt the two objections you already know are coming.** Raising them yourself converts a challenge into a discussion you have prepared for.

## How Many Options to Show

| Situation | Show |
|---|---|
| A decision inside an existing system | One. A system exists to reduce optionality, and offering three suggests it does not |
| A direction to be set (identity, campaign, a new surface) | Two or three genuinely distinct directions, plus your recommendation and why |
| A client who has asked for options | The contracted number, all of them defensible, with a stated recommendation |
| Any situation | Never three equal options with no recommendation — that delegates your job to someone less equipped to do it |

**Never present work you do not want chosen.** Filler options exist to make the favourite look good, and they get chosen often enough to make the tactic expensive.

## Running a Critique

A critique is not approval; it is a working session to improve the work. Say so at the start, because half the room assumes otherwise.

Format that works:

1. **Presenter frames** (2 min): the problem, the constraints, and specifically what feedback is wanted — "I want feedback on the information hierarchy, not on the colors, which are fixed by the brand"
2. **Silent review** (3-5 min): everyone looks before anyone talks, which prevents the first speaker from anchoring the room
3. **Observations before judgments**: what people notice, before what they think
4. **Questions**: "what happens when there are no results?", "why is this a dropdown?"
5. **Feedback against the stated goal only**
6. **Presenter restates** what they heard and what they will do

Rules that keep it useful: **the loudest person is not the decider** — say who is; **no redesigning in the room** — a critique that generates a solution has skipped diagnosing the problem; and **timebox it**, because critique quality falls off sharply after about 45 minutes.

## Giving Feedback

The structure: **observation → impact → question.**

> "The primary button sits below the fold on a 360px screen [observation], so a first-time visitor may never see it [impact]. Was that deliberate, or is there a constraint I'm missing [question]?"

- **Never open with "I would…"** — it makes it about your taste and moves the work toward your version rather than toward its own best version.
- **Tie feedback to a goal, a principle, or evidence.** If it ties to none of those, it is a preference, and it should be labelled as one out loud: "this is a preference, feel free to ignore it."
- **Be specific about the element**, not about the whole. "This feels off" is not feedback; "the two headings are the same size so the hierarchy is flat" is.
- **Ask before assuming a mistake.** Most odd decisions have a constraint behind them.
- **Say what is working, and why.** Not for morale — so the next iteration does not delete the part that was right.

## Receiving Feedback

- **Feedback is data about a reaction, not an instruction.** Someone's stated solution is usually a bad fix for a real problem; your job is to find the problem behind it.
- **Ask "what makes you say that?"** before defending anything. It is the single highest-yield question in this domain, and it converts an opinion into a diagnosis.
- **Do not defend in the room.** Note, restate, and come back with a response. Defending on the spot commits you to a position before you have thought.
- **Separate the three kinds**: a constraint you did not know about (accept immediately), a real problem with a proposed bad solution (accept the problem, redesign the solution), and a preference with no basis (name it as such, politely, once).
- **The same feedback from three different people is a real signal**, whatever you think of it individually.
- **Nobody owes you their reasoning.** A stakeholder who cannot articulate why is still reacting to something; find it.

## Translating Vague Feedback

| They say | Usually means | Show them |
|---|---|---|
| "Make it pop" | Hierarchy is flat; nothing dominates | One version with the primary element two steps up in size or weight |
| "It feels cluttered" | Grouping is unclear; uniform gaps | Two versions with the spacing rules of `layout.md` applied |
| "It looks cheap" | Too many type sizes, weights and colors; misalignment | A version regenerated from the scale (`typography.md`) |
| "I don't like the blue" | Almost never the hue — usually contrast, saturation or how much of it there is | The same layout at three saturations and two coverage levels |
| "Can we make the logo bigger" | The brand does not feel present, or the hierarchy puts it in the wrong place | The current version beside one with the logo bigger — the comparison usually answers it |
| "It's too plain" | The brand's character is not expressed in type, imagery or motion | One version with a distinctive element added; not more color |
| "Users won't understand it" | An untested assumption on both sides | A five-second test with five people (`research.md`) |
| "It doesn't feel like us" | The palette is right and the type, radius, rhythm and imagery are not (`brand.md`) | A side-by-side against the guidelines |
| Anything else | An unnamed reaction | "What were you expecting to see here?" |

## Stakeholders

- **Identify the decider before the review**, by name. A review with no named decider produces consensus-shaped mush and a second review.
- **Map who must approve, who must be consulted, and who must merely be informed** — and stop treating the third group's comments as approvals.
- **Brief senior stakeholders before the group review.** Surprising an executive in a room guarantees a defensive reaction; the pre-brief converts them into someone who already has a position.
- **Engineering is a stakeholder from the start.** A feasibility objection in the final review costs a week; the same objection in a sketch review costs an hour (`handoff.md`).
- **Legal, compliance and accessibility owners are the same case** — early is cheap, late is a redesign.
- **When a stakeholder overrules on preference alone**, record the decision, who made it and on what basis. Not as leverage — so the next designer does not spend a week re-deriving why the product is like this.

## Deadlock

When a decision will not resolve, in order:

1. **Restate the goal both sides claim to serve.** Disagreements often dissolve when the goal turns out to be two different goals.
2. **Convert it to a testable question** and run the smallest study (`research.md`). Five sessions cost less than the third meeting.
3. **Time-box the reversible option.** If it can be changed later, ship one, set a review date, and stop arguing.
4. **Escalate to the named decider** with both options, the tradeoff, and your recommendation. Escalating without a recommendation is asking someone with less context to do your job.
5. **Disagree and commit, in writing.** Record the decision, the dissent and the trigger that would revisit it. This is the artifact that prevents the same argument in six months.

## Write It Down

- **Any decision made in a review that will constrain future work** — a navigation model, a brand direction, a rejected option, a deliberate accessibility exception — → `artifacts/decision-<topic>.md`, its own file, with its `## Boxes` line and a read condition naming the surface. Include: what was decided, who decided, the alternatives rejected, the reason, and what would trigger revisiting it.
- **The review itself** — date, what was reviewed, who attended, the outcome — → a row in `~/Clawic/data/designer/sessions/<year>.md`.
- **A stakeholder, their role and how they prefer to be briefed** → the shared `~/Clawic/data/contacts/contacts.md`, one row per person, referenced elsewhere by name only.
- **A recurring review pattern** — a stakeholder who always raises the same objection, a step that always gets skipped — → `## Pain Points` in `memory.md`, because it changes how the next review is run.
