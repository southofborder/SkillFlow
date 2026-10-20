## Description:

Use when you have a written implementation plan to execute in a separate session with review checkpoints.

This skill is ready for commercial/non-commercial use.

## Publisher:

[chenleiyanquan](https://clawhub.ai/user/chenleiyanquan)

### License/Terms of Use:


## Use Case:

Developers and coding agents use this skill to execute a written implementation plan in small batches with review checkpoints, verification, and clarification pauses when blocked.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: A written plan may include destructive commands, deployments, secrets, production data, or other high-impact actions.

Mitigation: Review the plan before execution and pause for clarification when a step is unclear, blocked, or repeatedly fails verification.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/chenleiyanquan/skills/executing-plans)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Shell commands]

**Output Format:** [Markdown guidance with optional shell command output in progress reports]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The skill produces workflow guidance and status reports; it does not bundle code, persistence, or hidden data access.]

## Skill Version(s):

0.1.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
