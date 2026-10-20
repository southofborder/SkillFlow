## Description:

Create, list, modify, remove, and monitor scheduled cron jobs for system task automation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[picaye](https://clawhub.ai/user/picaye)

### License/Terms of Use:


## Use Case:

Developers and system operators use this skill to ask an agent for cron syntax, crontab inspection commands, schedule examples, and proposed commands for adding, removing, testing, and monitoring cron jobs.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Persistent cron changes can continue running commands after the agent session ends.

Mitigation: Ask the agent to show the exact crontab entry before installation, back up the current crontab, and approve only entries with expected schedules, commands, paths, and output handling.

Risk: Cron removal commands can delete unintended entries if the match pattern is too broad.

Mitigation: Request a removal diff or filtered preview before applying changes, and prefer interactive review for ambiguous crontab edits.

Risk: Examples involving deletion, service restart, or privileged log paths can affect system availability or require elevated permissions.

Mitigation: Test commands manually first, scope file paths narrowly, and require explicit approval before running destructive, service-management, or privileged-path operations.

## Reference(s):

- [Cron Scheduler on ClawHub](https://clawhub.ai/picaye/skills/cron-scheduler)
- [picaye publisher profile](https://clawhub.ai/user/picaye)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown with shell command examples and cron configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces proposed cron entries and operational commands for review before execution.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
