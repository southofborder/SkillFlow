## Description:

Cron Mastery guides agents in using OpenClaw cron scheduling for precise reminders, recurring maintenance jobs, and choosing Cron instead of Heartbeat for time-sensitive tasks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[i-mw](https://clawhub.ai/user/i-mw)

### License/Terms of Use:


## Use Case:

Developers and OpenClaw agents use this skill to create reliable scheduled reminders, recurring reports, and maintenance sweeps while choosing the appropriate timing mechanism for urgency.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Reusable scheduling examples may contain fixed Telegram recipients or example timezones.

Mitigation: Replace delivery recipients and timezones with user-confirmed values before creating cron jobs.

Risk: Recurring summaries or reminders may send information through external delivery channels.

Mitigation: Require explicit user consent before scheduling email summaries or external delivery.

Risk: Troubleshooting guidance includes deleting global cron state.

Mitigation: Do not delete cron state unless a backup exists and a supported recovery procedure is available.

## Reference(s):

- [Cron Examples & Templates](references/templates.md)
- [ClawHub Skill Page](https://clawhub.ai/i-mw/skills/cron-mastery)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with JSON cron examples and inline shell-style troubleshooting commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include cron schedule payloads, timezone assumptions, delivery-channel settings, and maintenance actions that require user confirmation.]

## Skill Version(s):

1.0.3 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
