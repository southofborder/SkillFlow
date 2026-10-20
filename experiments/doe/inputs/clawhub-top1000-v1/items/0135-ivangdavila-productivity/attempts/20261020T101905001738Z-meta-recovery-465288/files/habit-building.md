# Habit Building — Making a Behavior Survive Bad Weeks

Scope: designing repeated behavior so it outlives motivation. A habit is a behavior with a cue and a low enough cost that it happens on the worst day of the month, not the best one.

**Before designing or debugging a habit**, read `## Habits`, `## Constraints` and `## Energy Patterns` in `~/Clawic/data/productivity/memory.md` (or the file `## Boxes` names). The most common mistake is adding a fourth habit while two are already broken.

**Contents:** [The Design](#the-design) · [Cue, Not Willpower](#cue-not-willpower) · [The Timeline and Its Dips](#the-timeline-and-its-dips) · [Never Miss Twice](#never-miss-twice) · [Tracking Without a Second Job](#tracking-without-a-second-job) · [Breaking a Habit](#breaking-a-habit) · [Debugging a Failed Habit](#debugging-a-failed-habit) · [What to Write Down](#what-to-write-down)

## The Design

Every habit gets four fields before it starts, and the second one is the one people skip.

1. **Behavior**, stated observably: "read 10 pages", not "read more".
2. **Minimum version**, the one that counts on the worst day: one page, two push-ups, opening the file. This is the actual habit; the full version is what happens when conditions allow.
3. **Cue**: an existing routine, a fixed time, or a place — never a feeling. "After I pour coffee" is a cue; "when I feel like it" is a wish.
4. **Why**, in one line the user believes. A habit whose purpose is borrowed from an article dies at the first inconvenience.

Start with one habit. Two simultaneous new habits roughly halve the chance of either surviving, because both draw on the same finite supply of attention to novelty — and both break in the same bad week, which then reads as total failure.

## Cue, Not Willpower

- **Stack on something already automatic**: "after brushing my teeth, I…". The existing routine supplies the reliability.
- **Same place, same time** where possible. Context is a cue: an environment that only ever hosts the behavior starts triggering it.
- **Make the first action cost seconds.** Book on the pillow, shoes by the door, file already open. Friction at the start is the entire battle; friction after the start barely matters.
- **Implementation intention format** (Gollwitzer, `procrastination.md`): "When <cue>, I will <minimum version> at <place>." Written down, once.
- **Identity framing beats target framing** for behaviors meant to be permanent: "I'm someone who runs" survives a missed week; "run 4× a week" is failed by it.
- **Reduce the decision to zero.** Any habit that requires choosing what, when, or where each time is a series of decisions, and decisions run out (`energy.md`).

## The Timeline and Its Dips

Lally's UCL study found automaticity took a **median of 66 days**, with a range of **18 to 254** depending on the person and the behavior — simple daily actions at the fast end, complex ones far slower. The useful reading is not the 66: it is the width. Anyone quitting at week 3 because it "should be automatic by now" is quitting inside the normal range.

Predictable dips, worth naming in advance so they are not read as failure:

- **Week 1**: novelty carries it. Nothing has been proven yet.
- **Weeks 2-3**: novelty gone, automaticity not arrived. The highest-risk window; this is where the minimum version earns its keep.
- **Weeks 4-8**: it works but feels effortful, and progress becomes invisible because the gains are now small relative to the baseline.
- **First disruption** — travel, illness, a deadline week — is the real test, and it is not optional. Plan the travel version of the habit before the travel, not during.

## Never Miss Twice

- One miss is inside the noise of any real life. Two consecutive misses is the new pattern establishing itself, and it is the point where the identity claim starts eroding.
- The restart is always the **minimum version**, never the full version. Returning at full size after a break is how a two-day gap becomes a two-month gap: the full version is what was too expensive in the first place.
- **Same day or next day, not Monday.** Waiting for a clean restart date adds up to six lost days and converts a lapse into a decision.
- **Log the restart, not the break.** What gets recorded shapes what the user believes about themselves; a record full of breaks reads as evidence of failure.
- **Streaks are a tool with a sharp edge.** They motivate until they end, and then the loss of the number becomes a reason to stop entirely. If streak loss has already ended one habit for this user, count total days instead, where a miss costs one unit rather than everything.

## Tracking Without a Second Job

- Track one thing: did the minimum version happen, yes or no. Duration, quality and mood are analytics nobody reviews.
- Visible beats digital for most people — a wall calendar in the room where the habit happens, marked immediately.
- **Every tracked thing has a review row in `## Due`** or it stops being tracked. Data nobody reads is another abandoned commitment, and abandoning it costs more than never starting it.
- The monthly habit check answers exactly three questions: which are running, which broke and why, which should be dropped. Dropping is a legitimate outcome — three habits kept beats seven attempted.
- If the user declined measurement (`measurement` preference area), skip tracking entirely and rely on the cue plus a monthly conversation. The habit works without a tracker; it does not work without a cue.

## Breaking a Habit

Removal is a different mechanism from addition, and the same advice does not transfer.

- **Raise friction at the cue, not at the moment of temptation.** The phone in another room beats resisting the phone in your hand, because resistance is spent per exposure.
- **Substitute rather than subtract.** A cue with no response attached keeps firing; give it a different, cheaper response.
- **Remove the trigger from the environment first.** Most "willpower failures" are exposure failures, and exposure is a design choice.
- **Break the chain early.** The reachable decision point is "open the app", not "put the phone down after 40 minutes".
- **Anything with dependency characteristics** — substances, gambling, compulsive patterns that persist despite real harm — is out of this skill's scope and belongs with a clinician (SKILL.md Red Flags).

## Debugging a Failed Habit

| Symptom | Cause | Fix |
|---|---|---|
| Never starts | No cue, or a cue that does not reliably happen | Attach to something that already happens daily |
| Starts, dies in week 2-3 | Full version was the target; no minimum version exists | Define the minimum, restart there |
| Works on good days only | The habit costs more than a bad day has available | Halve it; a habit you can do while ill is the right size |
| Broke during travel or a deadline week | No disrupted-context version | Write the travel version now, before the next trip |
| Guilt after a miss, then abandonment | All-or-nothing framing, usually streak-driven | Never miss twice; count total days instead of streak |
| Habit runs but nothing improves | The behavior is not connected to the outcome | Check the "why"; a habit that is not the bottleneck is a hobby |
| Four habits, all faltering | Too many at once | Keep one, park the rest in `## Someday` with a date |

## What to Write Down

- Each habit gets a row in `## Habits` — behavior, minimum version, cue, start date, last break, current state. Past 15 rows, or 40 lines, it splits to `~/Clawic/data/productivity/habits.md` with the same headings.
- A break and its restart update the row in the same session; the row is the memory that makes "never miss twice" enforceable, because nobody remembers whether yesterday counted.
- The monthly habit check is a `## Due` row.
- A habit dropped deliberately is deleted from `## Habits` and named in the current `reviews/<year>.md` entry — otherwise it reappears as guilt in the next quarterly reset.
- A durable health fact behind a habit (medication timing, a physiotherapy protocol the user states) goes to the shared `~/Clawic/data/health/profile.md`, one dated line, and the habit row here just names it.
