## Description:

Helps agents query and manage Linear issues, projects, teams, cycles, and labels through a connected account.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and teams use this skill to find and update Linear work items and, when explicitly approved, connect an account or automate Linear actions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Connecting an account grants access to its Linear workspace.

Mitigation: Confirm the connection with the user and review OAuth scopes before authorizing access.

Risk: Writes and automations can change Linear records or trigger subsequent actions.

Mitigation: Prefer reads; obtain explicit approval for writes and automations after confirming the target and effect.

Risk: Triggers and destinations can continue forwarding future event data.

Mitigation: Review each event source and destination before enabling it, and remove it when no longer needed.

## Reference(s):

- [Linear GraphQL documentation](https://linear.app/developers/graphql)
- [Linear API and webhooks](https://linear.app/docs/api-and-webhooks)
- [Maton documentation](https://docs.maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Linear event triggers](references/linear/triggers.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Code, Guidance]

**Output Format:** [Markdown with command and GraphQL examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Responses depend on the connected account's permissions.]

## Skill Version(s):

1.2.12 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
