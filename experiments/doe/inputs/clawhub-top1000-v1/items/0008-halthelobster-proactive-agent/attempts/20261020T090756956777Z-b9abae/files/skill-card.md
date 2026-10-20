## Description:

Transform AI agents from task-followers into proactive partners that anticipate needs and continuously improve, using WAL Protocol, Working Buffer, Autonomous Crons, and battle-tested patterns.

This skill is ready for commercial/non-commercial use.

## Publisher:

[halthelobster](https://clawhub.ai/user/halthelobster)

### License/Terms of Use:

MIT

## Use Case:

Developers and agent operators use this skill to configure an AI agent for proactive assistance, persistent memory, self-healing workflows, reverse prompting, and periodic check-ins while preserving human approval for external actions.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Persistent memory and full-exchange logging can capture personal or third-party details without enough user control.

Mitigation: Require approval before writing sensitive details to memory, disable automatic full-exchange logging, and periodically audit generated memory files.

Risk: Self-modification guidance can alter AGENTS.md or similar policy files in ways the user did not review.

Mitigation: Require explicit human approval and diff review before modifying agent policy, governance, or operating-instruction files.

Risk: The BOOTSTRAP auto-follow/delete behavior can execute local bootstrap instructions and remove evidence before review.

Mitigation: Treat BOOTSTRAP content as proposed setup data, review it before use, and require approval before deleting it.

Risk: Heartbeat cleanup behavior can close apps, tabs, or move files while the user still needs them.

Mitigation: Turn cleanup into a proposed-action report and wait for confirmation before closing applications, tabs, or moving files.

Risk: Credential and environment-file handling depends on local hygiene and can expose secrets if templates are used carelessly.

Mitigation: Add a real .gitignore before storing credentials, keep secrets out of memory files, and run the included security audit before deployment.

## Reference(s):

- [Onboarding Flow Reference](references/onboarding-flow.md)
- [Security Patterns Reference](references/security-patterns.md)

## Skill Output:

**Output Type(s):** [markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands and starter configuration files]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes reusable local memory, onboarding, heartbeat, tool, user, and agent-governance templates.]

## Skill Version(s):

3.1.0 (source: artifact/SKILL.md frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
