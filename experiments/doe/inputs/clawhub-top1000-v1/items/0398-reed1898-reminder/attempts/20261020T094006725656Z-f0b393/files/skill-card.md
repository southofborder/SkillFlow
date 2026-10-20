## Description:

Natural-language reminder secretary: capture events into git-synced workspace, schedule Telegram reminders via OpenClaw cron, and answer upcoming schedule queries.

This skill is ready for commercial/non-commercial use.

## Publisher:

[reed1898](https://clawhub.ai/user/reed1898)

### License/Terms of Use:


## Use Case:

Individuals and external users use this skill to turn natural-language schedule mentions into stored reminder events, Telegram cron notifications, and summaries of upcoming plans.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Broad natural-language mentions may create persistent cron-based Telegram reminders without a clear explicit confirmation step.

Mitigation: Use explicit reminder phrases, confirm ambiguous captures before scheduling, and review or cancel cron jobs when a casual mention is captured unintentionally.

Risk: Reminder data may be saved in the user's workspace events file.

Mitigation: Review stored event details and avoid placing secrets or unnecessarily sensitive information in reminder notes.

## Reference(s):


## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration]

**Output Format:** [Markdown responses with reminder confirmations, upcoming-event summaries, YAML event data, and cron scheduling actions.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May write reminder data to a workspace events.yml file and create persistent cron notifications.]

## Skill Version(s):

0.1.1 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
