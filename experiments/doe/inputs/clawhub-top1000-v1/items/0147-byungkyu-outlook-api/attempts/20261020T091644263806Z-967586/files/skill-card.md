## Description:

Connects an agent to an authorized Outlook account to read and manage email, folders, calendar events, and contacts through Microsoft Graph.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

People and developers use this skill to find and manage Outlook messages, folders, meetings, and contacts in an account they have authorized. It can also guide approved, ongoing automations that perform Outlook actions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Access to private email, calendar events, and contacts may expose sensitive information.

Mitigation: Use an explicitly authorized account, prefer limited read-only access, and share only the information needed for the task.

Risk: Sending messages or modifying and deleting Outlook data can have unintended consequences.

Mitigation: Confirm the account, exact target, content, and intended effect with the user before every write.

Risk: Triggers and destinations can create persistent data flows or unattended actions.

Mitigation: Request separate explicit approval for each automation and destination, and verify recipients and destinations before activation.

## Reference(s):

- [Outlook skill on ClawHub](https://clawhub.ai/byungkyu/skills/outlook-api)
- [Maton](https://maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Microsoft Graph API overview](https://learn.microsoft.com/en-us/graph/api/overview)
- [Maton API gateway skill](https://clawhub.ai/byungkyu/api-gateway)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Code, Configuration guidance]

**Output Format:** [Markdown with command and API examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include account-scoped Outlook results; approved actions can change account data.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
