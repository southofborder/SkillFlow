## Description:

Provides GitLab CLI (glab) command guidance and workflows for merge requests, CI/CD, issues, releases, repositories, authentication, and other GitLab operations.

This skill is ready for commercial/non-commercial use.

## Publisher:

[vince-winkintel](https://clawhub.ai/user/vince-winkintel)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and engineering teams use this reference to plan and carry out GitLab CLI tasks, including managing merge requests, issues, pipelines, repositories, and releases.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Authenticated write, delete, approval, merge, or credential operations may affect the wrong GitLab account or resource.

Mitigation: Confirm the GitLab host, visible account, project or group, and operation scope before running commands.

Risk: Governance transcript sync can upload agent session content and persist background synchronization.

Mitigation: Review upload scope, stored credentials, and scheduled jobs before enabling or repeating setup.

Risk: Orbit and skills installation or updates can introduce remote content or executables.

Mitigation: Inspect the source and target release, choose the intended install scope, and approve downloads or automatic execution explicitly.

## Reference(s):

- [GitLab REST API documentation](https://docs.gitlab.com/api/)
- [GitLab GraphQL documentation](https://docs.gitlab.com/api/graphql/)
- [GitLab CLI environment variables](https://docs.gitlab.com/cli/configuration/#environment-variables)
- [ClawHub skill release](https://clawhub.ai/vince-winkintel/skills/gitlab-cli-skills)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Guidance]

**Output Format:** [Markdown with command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Reference guidance; executing suggested commands may change GitLab resources.]

## Skill Version(s):

1.13.32 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
