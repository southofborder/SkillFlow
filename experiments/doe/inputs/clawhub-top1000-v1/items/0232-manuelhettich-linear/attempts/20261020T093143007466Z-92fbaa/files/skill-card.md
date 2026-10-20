## Description:

Query and manage Linear issues, projects, and team workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[manuelhettich](https://clawhub.ai/user/manuelhettich)

### License/Terms of Use:


## Use Case:

Developers and team members use this skill to query Linear work, create and update issues, add comments, assign owners, set priorities, review projects, and prepare standup summaries from an agent workflow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can read and change Linear workspace data through an API key.

Mitigation: Use a least-privilege Linear API key and review write actions such as issue creation, comments, status changes, priority updates, and assignment changes before execution.

Risk: The script handles user-supplied issue titles, comments, project names, and usernames when building Linear API requests.

Mitigation: Avoid using the helper with untrusted Linear content until the script uses GraphQL variables and safe JSON encoding.

Risk: Team cache files may expose workspace metadata in a shared temporary directory.

Mitigation: Use a private cache path and restrict file permissions when running the skill in multi-user or shared environments.

## Reference(s):

- [Linear](https://linear.app)
- [Linear GraphQL API](https://api.linear.app/graphql)
- [ClawHub Linear Skill](https://clawhub.ai/manuelhettich/skills/linear)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown and plain text with shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires LINEAR_API_KEY and uses Linear API responses for issue, project, team, branch, and standup output.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
