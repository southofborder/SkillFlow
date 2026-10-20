## Description:

A skill for personal growth and self-improvement.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xrowgmbh](https://clawhub.ai/user/xrowgmbh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers use this skill to reflect on work in the named GitLab project, identify substantive improvements, and prepare separate merge requests for distinct issues. It also directs the agent to close its own older merge requests after 10 days without acceptance.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill directs the agent to create merge requests and close older ones without clearly requiring user approval.

Mitigation: Require explicit approval for proposed repository changes and each merge-request closure; limit use to the named project with narrowly scoped credentials.

Risk: The skill relies on separate GitLab Agent guidance that is not included in this release artifact.

Mitigation: Inspect the separate gitlab-agent skill before use.

## Reference(s):

- [helm-openclaw project](https://gitlab.com/xrow-public/helm-openclaw)

## Skill Output:

**Output Type(s):** [Text, Markdown, Guidance, GitLab merge-request actions]

**Output Format:** [Markdown merge-request content and GitLab project updates]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Creates separate merge requests for distinct issues; may close the agent's older unaccepted merge requests.]

## Skill Version(s):

1.114.1 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
