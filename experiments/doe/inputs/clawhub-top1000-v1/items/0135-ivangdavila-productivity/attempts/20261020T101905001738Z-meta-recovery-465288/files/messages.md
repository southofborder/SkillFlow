# Messages — Email, Chat, and the Response Contract

Scope: the incoming stream — email, chat, DMs, tickets — and why it eats days. The failure is almost never volume; it is that the stream has no schedule and no stated response time, so it becomes an interrupt-driven job on top of the real one.

**Before redesigning anyone's message handling**, read `## Constraints`, `## Friction` and `## Due` in `~/Clawic/data/productivity/memory.md`. A support role with a contractual response time and a manager with a full inbox need opposite advice.

**Contents:** [The Response Contract](#the-response-contract) · [Batching](#batching) · [Processing a Batch](#processing-a-batch) · [Writing So the Thread Ends](#writing-so-the-thread-ends) · [Chat Specifically](#chat-specifically) · [Inbox Bankruptcy](#inbox-bankruptcy) · [What to Write Down](#what-to-write-down)

## The Response Contract

Everything else depends on this. A response time that is never stated gets set by your fastest reply: answer in two minutes once and two minutes becomes the expectation, permanently.

- **State it, in the signature, the status line, or once per relationship**: "Email within one working day, chat twice a day at 11:00 and 16:00, phone for anything that cannot wait."
- **Then hold it.** The contract's value is entirely in its reliability — a stated four hours honored beats a stated one hour honored half the time, because the second one trains people to escalate.
- **Give one real emergency channel.** Without it, everything becomes urgent by default because nobody has another way to reach you. With it, almost nobody uses it.
- **Team norms beat personal ones.** If a team's implicit standard is minutes, an individual contract fails; propose the norm at team level with the meeting-audit style evidence (`meetings.md`).

## Batching

- **Two or three fixed windows a day**, none of them first thing. Opening the inbox first thing hands the day's agenda to whoever wrote overnight, and it converts the peak window into other people's work.
- **Closed between windows.** Closed, not muted: an unread badge is a self-delivered interruption (`focus.md`).
- **Length-capped.** 30 minutes per window with a timer. Uncapped processing expands to fill the day and the last third of it is low-value.
- **Cost of the alternative:** with ~23 minutes of resumption cost per interruption, ten reactive checks can consume more of the day than the messages themselves.
- **Exception, honestly stated:** on-call, support rotations and client-facing roles with contractual SLAs are interrupt-driven by design. There the play is different — protect one block per day and accept the rest, rather than pretending batching is available.

## Processing a Batch

Same five destinations as any inbox (`capture.md`), applied per message. Every message leaves the inbox; none goes back.

| Message | Move |
|---|---|
| Reply takes under 2 minutes | Reply now, inside the window only |
| Needs work from you | Extract the action into `## Tasks` with an estimate; archive the mail, do not use the inbox as the task list |
| Needs someone else | Forward with an explicit ask and a date, log it in `## Commitments` as `owed to me` |
| You promised something | `## Commitments` as `owed by me`, with the date |
| Information, no action | Archive. Searching later is cheaper than filing now — folder taxonomies cost more than they return |
| Newsletter, notification, automated | Unsubscribe or filter at the source; a rule written once beats a decision made weekly |
| Group thread you were CC'd on | Read last message only, act only if named. CC is broadcast, not assignment |

Inbox zero is a processing outcome, not a life goal: the value is that nothing hides, not that the number is 0. An inbox used as a to-do list fails because it sorts by arrival time, which correlates with nothing.

## Writing So the Thread Ends

Message volume is largely self-generated: every ambiguous message buys a reply asking what you meant.

- **Ask, deadline, context — in that order, in the first two lines.** A request buried under three paragraphs of background gets a "sorry, what do you need?" and doubles the thread.
- **Offer options, not open questions.** "Tuesday 10:00 or Thursday 15:00?" ends a thread that "when are you free?" extends by four messages.
- **One topic per message.** Two questions in one email reliably return one answer, and the second question comes back a week later as a surprise.
- **Close the loop explicitly**: "Nothing needed from you" or "I'll take it from here" stops the courtesy replies that make up a third of most inboxes.
- **Choose the channel by response time needed and by durability**: decisions and anything anyone will need to find again go to email or a document; chat is for things that can be lost.

## Chat Specifically

- **Status line as a contract**: "heads down until 11:00" answers the question people would otherwise ask you.
- **Threads, always.** A channel of unthreaded messages forces everyone to read everything, which is a tax multiplied by the channel's membership.
- **Do not answer the "hi" — answer the question.** "Hi" with no content is a request for synchronous attention with no information; reply with "hi — what's up?" and continue working, or wait.
- **Mute channels, not people.** The people are the signal.
- **Notifications: mentions and DMs only.** Channel-wide alerts turn a shared workspace into a paging system.
- **The message you are about to send at 22:00** schedules itself for the morning unless it is genuinely urgent — otherwise you are writing your team's response contract for them.

## Inbox Bankruptcy

For 5,000 unread. Processing them is a week of work that will not happen.

1. Archive everything older than 30 days in one action. It is searchable; nothing is destroyed.
2. Process the last 30 days properly, top to bottom, in one 60-minute pass.
3. Send one message to anyone who might be waiting: "Catching up after a backlog — if something is still open, resend it." Almost nothing comes back, which is itself the finding.
4. Set the response contract and the windows before the inbox refills; without that step, the same state returns in about two months.

## What to Write Down

- Actions extracted from messages go to `## Tasks`; promises and awaited replies to `## Commitments` with the person's name pointing at `contacts.md`.
- The response contract, once the user commits to it, is a declaration: `config.yaml` under the `conventions` preference area, with the windows as a `## Due` row if they need reminding.
- A channel that keeps generating overload — a person, a channel, a recurring alert — goes to `## Friction`, with the countermeasure applied.
- Reusable wording that ended a recurring thread type (a scope-creep reply, a status update template, a handover note) goes to `~/Clawic/data/productivity/artifacts/message-templates.md` with its `## Boxes` line.
- Never store an account password, token, or dial-in passcode found in a message. Strip it to a pointer (`env:`, `keychain:`, `1password:`) before anything is written.
