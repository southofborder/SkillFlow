## Description:

Helps agents search and manage Jira issues, projects, and workflows through a Maton-managed connection.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

Jira users and developers use this skill to find issues with JQL, manage issues and projects, and plan approved workflow or automation actions through Maton.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Maton acts as the OAuth gateway to the connected Jira account.

Mitigation: Confirm the Jira account, connection, and required OAuth scopes before authorizing access.

Risk: Writes and deletions can change Jira data.

Mitigation: Require explicit user confirmation before modifying or deleting data.

Risk: Hosted functions, triggers, and destinations can keep running or forward data.

Mitigation: Require explicit confirmation before creating or changing automation or data destinations.

## Reference(s):

- [Jira skill release](https://clawhub.ai/byungkyu/skills/jira-api)
- [Maton](https://maton.ai)
- [Jira Cloud REST API introduction](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
- [Jira query language reference](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Code, Guidance]

**Output Format:** [Markdown with CLI and API examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Examples may include JSON responses and Jira issue details.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
