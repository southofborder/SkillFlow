## Description:

Helps agents access GitHub repositories, issues, pull requests, and related workflows through a user-authorized Maton connection.

This skill is ready for commercial/non-commercial use.

## Publisher:

[byungkyu](https://clawhub.ai/user/byungkyu)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and other GitHub users use this skill to inspect repositories, manage issues and pull requests, and set up approved GitHub automations through Maton.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Connecting GitHub can grant access beyond the intended task.

Mitigation: Review requested OAuth scopes and authorize only the access needed.

Risk: Repository changes and persistent automations can have lasting effects.

Mitigation: Confirm each write and automation step with the user; keep triggers narrowly scoped.

Risk: Third-party trigger destinations can receive event data.

Mitigation: Use external destinations only after the user approves the host and data flow.

## Reference(s):

- [GitHub skill release](https://clawhub.ai/byungkyu/skills/github-api)
- [GitHub REST API documentation](https://docs.github.com/en/rest)
- [GitHub event reference](references/github/triggers.md)
- [Maton homepage](https://maton.ai)
- [Maton documentation](https://docs.maton.ai)
- [Maton CLI manual](https://cli.maton.ai/manual)
- [Maton API gateway skill](https://clawhub.ai/byungkyu/api-gateway)

## Skill Output:

**Output Type(s):** [Text, Shell commands, Code, Configuration guidance]

**Output Format:** [Markdown with command and code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires network access and a user-authorized Maton connection.]

## Skill Version(s):

1.2.5 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
