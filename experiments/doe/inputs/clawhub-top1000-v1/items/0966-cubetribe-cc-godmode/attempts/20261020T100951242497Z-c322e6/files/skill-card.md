## Description:

Self-orchestrating multi-agent development workflows. You say WHAT, the AI decides HOW.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cubetribe](https://clawhub.ai/user/cubetribe)

### License/Terms of Use:

MIT

## Use Case:

Developers and engineering teams use this skill to coordinate multi-agent software workflows for feature work, bug fixes, API changes, refactoring, research, issue processing, and release preparation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Agents may perform broad runtime code, shell, network, screenshot, and GitHub operations when users invoke workflows.

Mitigation: Install only where that authority is intended, run workflows in a controlled workspace, and require human confirmation before PR merges, releases, issue closures, or other irreversible operations.

Risk: Runtime GitHub and agent integrations may use credentials or account access.

Mitigation: Use least-privilege tokens, prefer short-lived credentials where possible, and keep credentials out of prompts, reports, screenshots, and committed files.

Risk: Browser testing and screenshots may expose private application data.

Mitigation: Run Playwright against test or sanitized accounts and review screenshots before sharing or committing them.

Risk: MCP packages installed through unpinned npx or global package flows can change outside the skill release.

Mitigation: Pin MCP package versions or install them locally under a reviewed dependency workflow.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/cubetribe/skills/cc-godmode)
- [cubetribe publisher profile](https://clawhub.ai/user/cubetribe)
- [OpenClaw GodMode repository](https://github.com/cubetribe/openclaw-godmode-skill)
- [cubetribe GitHub profile](https://github.com/cubetribe)
- [OpenClaw](https://openclaw.ai)
- [Claude Code](https://claude.ai/code)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown guidance with workflow reports, code suggestions, shell commands, and configuration snippets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The package is documentation-only at install time; runtime actions depend on the user's agent tools, binaries, network access, and credentials.]

## Skill Version(s):

5.11.3 (source: server release metadata, artifact frontmatter, clawdis.yaml, CHANGELOG released 2026-02-16)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
