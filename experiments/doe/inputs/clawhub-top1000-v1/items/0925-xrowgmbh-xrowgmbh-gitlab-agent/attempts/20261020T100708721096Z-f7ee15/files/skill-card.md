## Description:

Operates assigned GitLab work with owner-verified project access and guarded merge request delivery.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xrowgmbh](https://clawhub.ai/user/xrowgmbh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and project teams use this skill to discover and handle assigned GitLab issues, incidents, and merge requests, including code changes, reviews, and delivery.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Broad GitLab permissions can change projects and work items without routine human approval.

Mitigation: Use a dedicated low-privilege GitLab account and token restricted to intended projects.

Risk: The recurring job can repeatedly create branches and merge requests, change labels, and trigger pipelines.

Mitigation: Review or disable the recurring job before enabling autonomous operation.

Risk: Eligible merge requests may be approved and merged by the agent itself.

Mitigation: Review or disable the self-merge path and require human review where appropriate.

## Reference(s):

- [GitLab Agent release](https://clawhub.ai/xrowgmbh/skills/xrowgmbh-gitlab-agent)
- [Documentation style](references/documentation-style.md)
- [GitLab project permissions](https://docs.gitlab.com/user/permissions/#default-roles)
- [OpenClaw skill creation](https://docs.openclaw.ai/tools/creating-skills)
- [CI Tools Components Catalog](https://ci-tools.xrow.de/)

## Skill Output:

**Output Type(s):** [Guidance, Code, Shell commands, Configuration, Markdown]

**Output Format:** [Text, Markdown, code, and shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May also update GitLab issues, labels, branches, pipelines, and merge requests.]

## Skill Version(s):

1.114.0 (source: ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
