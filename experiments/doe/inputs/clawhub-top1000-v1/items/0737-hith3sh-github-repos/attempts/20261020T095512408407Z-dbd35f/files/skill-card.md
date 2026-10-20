## Description:

Work with GitHub repositories, issues, pull requests, commits, branches, releases, and workflows via the GitHub REST and GraphQL APIs.

This skill is ready for commercial/non-commercial use.

## Publisher:

[hith3sh](https://clawhub.ai/user/hith3sh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and operators use this skill to inspect and manage GitHub repositories, issues, pull requests, branches, releases, and workflow runs through an authenticated ClawLink connection.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill uses a GitHub integration through ClawLink, so access depends on the connected account and granted repository permissions.

Mitigation: Before installing, verify trust in the ClawLink plugin and grant only the GitHub repository permissions needed for the intended work.

Risk: Write, delete, workflow, and deployment actions can modify repositories or affect external systems.

Mitigation: Review previews carefully and require explicit user confirmation before approving write, destructive, workflow, or deployment actions.

Risk: Continued access may remain available after the user stops relying on the skill.

Mitigation: Revoke the GitHub connection or remove the plugin when it is no longer needed.

## Reference(s):

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [ClawLink Docs](https://docs.claw-link.dev/openclaw)
- [ClawLink Verification](https://claw-link.dev/verify)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance, API calls]

**Output Format:** [Markdown with bash commands and JSON tool-call examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires a connected GitHub account through ClawLink for live GitHub operations.]

## Skill Version(s):

1.0.5 (source: release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
