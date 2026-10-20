## Description:

The directory for AI agent services. Discover tools, platforms, and infrastructure built for agents.

This skill is ready for commercial/non-commercial use.

## Publisher:

[aerialcombat](https://clawhub.ai/user/aerialcombat)

### License/Terms of Use:


## Use Case:

Agents and developers use this skill to discover AI agent services, fetch service metadata, and locate service-specific skill.md files for integration review.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill directs agents to fetch and follow mutable remote skill.md files, which can change after review.

Mitigation: Review each remote skill.md before use and require approval before following instructions from newly fetched service files.

Risk: Remote service instructions could request sensitive actions such as reading files, using credentials, running commands, changing configuration, or sending data externally.

Mitigation: Approve sensitive actions explicitly and limit credentials, filesystem access, command execution, and outbound data sharing to the minimum needed.

## Reference(s):

- [Agent Directory on ClawHub](https://clawhub.ai/aerialcombat/skills/agent-directory)
- [ctxly.com](https://ctxly.com)
- [Services JSON endpoint](https://ctxly.com/services.json)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline bash commands and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Guides agents to fetch mutable remote service metadata and skill.md files.]

## Skill Version(s):

1.2.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
