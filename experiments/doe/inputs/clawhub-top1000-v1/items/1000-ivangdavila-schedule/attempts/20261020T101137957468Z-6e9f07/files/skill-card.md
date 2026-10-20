## Description:

Program recurring or one-time tasks. User defines what to do, skill handles when.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:


## Use Case:

External users and agent operators use Schedule to create, confirm, store, and cancel one-time or recurring jobs while keeping task actions user-defined and permission-scoped.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Job descriptions, schedule preferences, and execution history are stored locally and may contain sensitive user-provided text.

Mitigation: Avoid putting secrets in job descriptions, and delete jobs or history that should no longer be retained.

Risk: A scheduled job may require other skills or permissions to perform the user-defined action.

Mitigation: Review and approve every listed skill or permission requirement before enabling or running the job.

Risk: Ambiguous dates, missing timezones, DST changes, or travel can cause a job to run at an unintended time.

Mitigation: Confirm exact date, time, and timezone when creating jobs, and clarify whether schedules should follow the user or remain fixed.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ivangdavila/skills/schedule)
- [Job storage format](artifact/jobs.md)
- [Cron patterns reference](artifact/patterns.md)
- [Scheduling traps](artifact/traps.md)

## Skill Output:

**Output Type(s):** [text, markdown, configuration, shell commands, guidance]

**Output Format:** [Markdown guidance with JSON job definitions and cron or ISO schedule values]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can describe local schedule files under ~/schedule/ and explicit skill or permission requirements for a job.]

## Skill Version(s):

1.0.2 (source: frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
