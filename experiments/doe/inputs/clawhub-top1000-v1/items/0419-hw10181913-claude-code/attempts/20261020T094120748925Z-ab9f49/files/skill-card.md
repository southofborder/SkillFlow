## Description:

Provides OpenClaw users with local Claude Code documentation summaries, workflow guidance, troubleshooting help, and command examples.

This skill is ready for commercial/non-commercial use.

## Publisher:

[hw10181913](https://clawhub.ai/user/hw10181913)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill in OpenClaw to look up Claude Code guidance, troubleshooting notes, and suggested development workflows without leaving their agent session.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill describes task and subagent features that may be mistaken for real automation.

Mitigation: Treat task outputs as guidance and use OpenClaw automation tools only after reviewing the intended action.

Risk: Some documentation examples show remote installer commands that users could run directly.

Mitigation: Do not pipe remote installers into a shell; download, pin, and verify installer content before execution.

Risk: The MCP filesystem example can broaden file access if copied without review.

Mitigation: Only add filesystem MCP access with a pinned and verified package and with file access restricted to the minimum required paths.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/hw10181913/skills/claude-code)
- [Claude Code Docs](https://code.claude.com/docs)
- [Claude Code Quickstart](https://code.claude.com/docs/en/quickstart)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code Common Workflows](https://code.claude.com/docs/en/common-workflows)
- [OpenClaw](https://openclaw.ai)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown-style text with inline shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Static documentation cache; task command prints guidance rather than executing automation.]

## Skill Version(s):

1.0.0 (source: server release metadata, README version)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
