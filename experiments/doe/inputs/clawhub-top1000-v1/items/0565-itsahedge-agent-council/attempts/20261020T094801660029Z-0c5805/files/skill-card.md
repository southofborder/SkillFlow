## Description:

Complete toolkit for creating autonomous AI agents and managing Discord channels for OpenClaw.

This skill is ready for commercial/non-commercial use.

## Publisher:

[itsahedge](https://clawhub.ai/user/itsahedge)

### License/Terms of Use:

MIT

## Use Case:

Developers and engineers use this skill to create OpenClaw agent workspaces, bind agents to Discord channels, and manage Discord channel setup or renaming for multi-agent systems.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Scripts can read Discord bot credentials and make Discord channel changes.

Mitigation: Run only in an OpenClaw environment where the operator has reviewed the Discord bot permissions and is comfortable with channel creation or renaming.

Risk: Generated gateway configuration commands may include unsafe or untrusted channel context.

Mitigation: Review generated config.patch commands before applying them, especially when channel context or existing prompts may contain untrusted text.

Risk: Workspace rewrite behavior can alter Markdown files and may be unsafe around untrusted symlinks or sensitive files.

Mitigation: Use the workspace rewrite option only on trusted workspaces and review changed files before committing or deploying them.

Risk: The skill can add recurring cron jobs and restart the OpenClaw gateway.

Mitigation: Confirm scheduled jobs, time zones, and gateway restart impact before accepting optional cron setup or applying configuration changes.

## Reference(s):

- [Agent Council on ClawHub](https://clawhub.ai/itsahedge/skills/agent-council)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw Agents Documentation](https://docs.openclaw.ai/agents)
- [OpenClaw Discord Channel Documentation](https://docs.openclaw.ai/channels/discord)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell commands and JSON configuration examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce SOUL.md and HEARTBEAT.md content, OpenClaw gateway configuration patches, Discord channel setup steps, and cron setup guidance.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
