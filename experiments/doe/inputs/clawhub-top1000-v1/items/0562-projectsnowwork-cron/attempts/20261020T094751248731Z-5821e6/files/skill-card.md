## Description:

Local-first recurring schedule engine for reminders, repeated tasks, and time-based execution plans.

This skill is ready for commercial/non-commercial use.

## Publisher:

[projectsnowwork](https://clawhub.ai/user/projectsnowwork)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agent users use Cron to capture recurring intentions as local schedules, inspect upcoming runs, and pause or resume repeated jobs without external sync.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Local schedule records can include job titles, notes, tags, timing, status, and stats that may be sensitive.

Mitigation: Confirm job details before adding, pausing, or resuming schedules, and review local OpenClaw memory files according to the user's data handling expectations.

Risk: The skill defaults new jobs to the Asia/Tokyo timezone when no timezone is specified.

Mitigation: Ask for or provide an explicit timezone when creating schedules for users in other regions.

## Reference(s):

- [Cron Philosophy](references/philosophy.md)
- [Cron on ClawHub](https://clawhub.ai/projectsnowwork/skills/cron)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown with inline shell commands and local JSON state descriptions]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Stores disclosed local JSON state for jobs, runs, and stats under the OpenClaw memory directory.]

## Skill Version(s):

1.0.0 (source: server release metadata and skill.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
