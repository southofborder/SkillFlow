## Description:

Creates, edits, and validates DCC-MCP tool skill packages, including SKILL.md and tools.yaml.

This skill is ready for commercial/non-commercial use.

## Publisher:

[loonghao](https://clawhub.ai/user/loonghao)

### License/Terms of Use:

MIT-0

## Use Case:

Developers use this skill to scaffold and validate DCC-MCP skill packages, including their metadata, tool declarations, and supporting scripts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Scaffolding can write a new skill package to the selected parent directory.

Mitigation: Review the destination directory before authorizing creation.

Risk: Installing an unreviewed revision can introduce unwanted skill behavior.

Mitigation: Use the documented pinned, verified installation procedure when installing from GitHub.

## Reference(s):

- [ClawHub skill release](https://clawhub.ai/loonghao/skills/dcc-mcp-skills-creator)
- [Skill homepage](https://github.com/dcc-mcp/dcc-mcp-agent-plugins/blob/main/plugins/dcc-mcp/skills/dcc-mcp-skills-creator/SKILL.md)
- [Package validation](artifact/references/PACKAGE_VALIDATION.md)
- [Verified install](artifact/references/VERIFIED_INSTALL.md)

## Skill Output:

**Output Type(s):** [Code, Configuration, Guidance]

**Output Format:** [Markdown, YAML, and Python files; text validation feedback]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can create files in a user-selected parent directory.]

## Skill Version(s):

0.19.113 (source: release metadata and SKILL.md)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
