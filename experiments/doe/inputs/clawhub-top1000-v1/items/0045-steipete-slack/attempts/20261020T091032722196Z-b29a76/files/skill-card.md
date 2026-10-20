## Description:

Use when you need to control Slack from Clawdbot via the slack tool, including reacting to messages or pinning/unpinning items in Slack channels or DMs.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Employees and external collaborators use this skill to let an agent perform configured Slack bot actions such as reading messages, sending or editing replies, managing reactions, managing pins, and fetching member or emoji information.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Slack message, pin, and reaction actions can change shared channel or DM content.

Mitigation: Install only when Clawdbot should act in Slack with its configured bot permissions, and review send, edit, delete, pin, and unpin actions before use.

Risk: Member information requests can expose user details beyond what is needed for a task.

Mitigation: Request member information only when it is necessary for the current Slack workflow.

## Reference(s):


## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with JSON action examples for Slack tool calls.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces agent-facing instructions for using configured Slack bot permissions; it does not include executable code.]

## Skill Version(s):

1.0.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
