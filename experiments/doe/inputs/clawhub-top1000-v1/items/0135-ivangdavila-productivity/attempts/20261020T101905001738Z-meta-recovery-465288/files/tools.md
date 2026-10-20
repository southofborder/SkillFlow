# Tools — Apps, Churn, and Migrations

Scope: choosing where the system physically lives, and resisting the app change that is really an avoidance move. Recorded in `task_tool`. Tool is the last decision, never the first: the mechanism (`methods.md`) determines what the tool must do.

**Before recommending any tool**, read `config.yaml` for `task_tool` and `method`, and `## Friction` in `~/Clawic/data/productivity/memory.md`. A third app in a year is the finding, not the request.

**Contents:** [What a Tool Must Do](#what-a-tool-must-do) · [Choosing](#choosing) · [Tool Churn](#tool-churn) · [Migration Checklist](#migration-checklist) · [The Minimum Stack](#the-minimum-stack) · [Automation](#automation) · [What to Write Down](#what-to-write-down)

## What a Tool Must Do

Four requirements. Everything else is preference, and preference is where months get lost.

1. **Capture in under 30 seconds** from wherever thoughts arrive — phone, keyboard shortcut, paper. This one requirement eliminates most candidates (`capture.md`).
2. **Show today without configuration.** If the daily view needs a saved filter to be useful, it will be abandoned during the first bad week.
3. **Survive neglect.** After two ignored weeks it must still be openable without a cleanup project. Tools that punish absence with red overdue counts get closed instead of opened.
4. **Export in a readable format.** Plain text, Markdown or CSV. A system you cannot leave is a system that owns you, and every tool eventually changes its pricing or its product direction.

Nice, not necessary: collaboration, natural-language dates, recurring tasks, tags, calendar sync. Useful for some, none of them decisive.

## Choosing

| Situation | Fit | Why |
|---|---|---|
| Solo, technical, wants ownership | Plain Markdown files, which is what this skill uses by default | Zero lock-in, greppable, works with any editor, and the agent can read and write it directly |
| Solo, wants a polished daily loop | Any mainstream task app | The differences between them matter far less than the review habit |
| Shared work with a team | The team's existing tool, plus a personal list | Never run your personal system inside the team tool: their reorganizations become your outages |
| Attention fragmented by screens | Paper, one notebook | Analog friction is a feature; the rewrite is a review (`methods.md`) |
| Heavy meeting load, calendar-driven | Calendar plus a short list | The calendar is already the source of truth for the day (`calendar-planner`) |
| Constant tool-switching history | Whatever is already open, no change | The tool is not the problem; changing it again postpones the diagnosis |

Cost is rarely decisive: a paid app that is opened daily returns its price in one recovered commitment. The decisive factor is capture speed followed by whether the daily view is honest.

## Tool Churn

Migration feels like progress: a new app is clean, every list starts empty, and nothing has failed in it yet. Then the same failure arrives in about six weeks, because the failure was never in the tool.

Tells: a new app in the last three months · time spent configuring exceeds time spent executing · the same list exists in two places · the phrase "once I get this set up properly" · researching apps during a week with a stalled item.

The rule: **no tool change while an item is stuck.** Unstick the item first — the urge usually disappears with it. If it survives a week, the change may be real.

Legitimate reasons to switch, all mechanical: capture is genuinely slower than 30 seconds; the tool is being shut down or has changed its terms; a shared workflow requires it; the current tool cannot express the mechanism the method needs (no WIP limit, no recurring tasks). "It feels cluttered" is not on the list — clutter is a pruning problem, and a review fixes it in twenty minutes (`reviews.md`).

## Migration Checklist

When a switch is justified, it costs about two weeks of degraded output. Reduce it:

1. **Export the old system first**, as a file, before touching the new tool. Screenshots are not an export.
2. **Do not migrate the backlog.** Rebuild from live sources: due in 14 days, who is waiting, what is on the calendar. Park the export as `artifacts/old-list-<date>.md` with its `## Boxes` line.
3. **Recreate only what was used.** Every view, tag and automation must earn its way back in by being missed, not by having existed.
4. **Run both for one week maximum.** Longer means two systems, which means neither is trusted.
5. **Delete the old one at the end of the week**, or set a hard date. A dormant old system is a second inbox in waiting.
6. **Rerun the first review in the new tool** before declaring the switch done. A tool that has not survived a review has not been tested.

## The Minimum Stack

Five slots. Filling more than five is where systems become jobs.

- **Capture**: one place, fastest possible.
- **List**: where tasks and projects live. Can be the same as capture.
- **Calendar**: time-bound commitments only. Tasks belong on the list, not on the calendar, or dropped blocks quietly become invisible debt.
- **Notes**: reference material, deliberately separate from tasks — mixing them is what makes both unreadable.
- **Durable memory**: `~/Clawic/data/productivity/`, where constraints, patterns, commitments and artifacts survive across sessions and across tool changes.

The last slot is the one people lack, and it is why every tool migration loses the accumulated knowledge of how the person works. Notes and tasks are replaceable; the calibration ratio and the constraints are not.

## Automation

Worth building only for something that recurs and is genuinely mechanical.

- **Filters and rules on incoming mail** are the highest-return automation available: a rule written once removes a decision every week (`messages.md`).
- **Templates** for recurring deliverables — a weekly report, a project kickoff, a review — remove setup cost and drift at the same time. They live in `artifacts/`.
- **Recurring items** belong in `## Due` when they are cadences the agent should surface, and in the task tool when they are the user's own routine. Both is duplication, and duplication is how a cadence quietly stops being trusted.
- **Do not automate a broken process.** Automating a report nobody reads produces the report faster, forever.
- **Never store a credential to make an automation work.** The token, password or app key goes to the OS keychain, the user's password manager, or an environment variable, and only the pointer is written: `env:TODOIST_TOKEN`, `keychain:work-mail`, `1password:Personal/Calendar`. Nothing under `~/Clawic/data/` ever holds the value.

## What to Write Down

- The chosen tool is a declaration: `task_tool` in `config.yaml`, with tool-specific conventions under the `conventions` preference area.
- A migration goes to `~/Clawic/data/productivity/artifacts/tool-migration-<date>.md` with its `## Boxes` line: what moved, what was deliberately dropped, and what broke. The next migration reads it and is cheaper.
- The exported old list, if kept, is `artifacts/old-list-<date>.md`, with a date to delete it at the quarterly reset.
- A churn pattern — three tools in a year, always at the same point in the cycle — goes to `## Friction`, and the underlying failure is what gets fixed.
- Any credential encountered while setting up a tool is replaced by its `<kind>:<locator>` pointer before anything is written, and that substitution is stated in one line.
