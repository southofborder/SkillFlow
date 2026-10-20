## Description:

Coordinates multi-agent work through a local shared blackboard, task budgets, advisory permission checks, and persistent project context.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jovancoding](https://clawhub.ai/user/jovancoding)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and teams use this skill to coordinate agents within a trusted workspace, track task budgets and shared progress, and assess proposed access to sensitive operations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Persistent coordination files can retain sensitive project details or personal data in permission justifications.

Mitigation: Use a trusted workspace with restricted local file access; omit secrets, credentials, and personal data from justifications and project context.

Risk: Advisory grant tokens could be mistaken for authorization to perform sensitive operations.

Mitigation: Require separate human approval and authenticated identity checks before payments, database access, email, or exports.

## Reference(s):

- [Network-AI skill listing](https://clawhub.ai/jovancoding/skills/network-ai)
- [Network-AI homepage](https://network-ai.org)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Markdown]

**Output Format:** [Markdown with shell commands and coordination summaries]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Runs locally and maintains persistent workspace coordination state; permission decisions are advisory.]

## Skill Version(s):

5.16.0 (source: server-resolved release and bundled skill.json)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
