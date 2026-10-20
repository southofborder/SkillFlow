## Description:

Use Codex safely for repo-aware coding with explicit approvals, sandbox choices, MCP boundaries, and PR-ready verification workflows.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and engineering teams use this skill to run Codex as a repo-aware coding agent with explicit safety boundaries, scoped edits, verification steps, and review-ready handoffs.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Codex runs may send prompts, selected repository context, and tool results to OpenAI services.

Mitigation: Install and use this skill only when that data sharing is acceptable for the target repository and task.

Risk: Remote MCP servers, Codex Cloud apply, app-server integrations, full-access sandboxing, and persistent ~/codex/ notes can expand data access or local side effects.

Mitigation: Keep those modes opt-in, review scopes and diffs before applying changes, and use explicit user approval for irreversible or high-trust operations.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/ivangdavila/skills/codex)
- [Skill Homepage](https://clawic.com/skills/codex)
- [Install and Auth](artifact/install-and-auth.md)
- [Repo Execution](artifact/repo-execution.md)
- [Approvals and Sandbox](artifact/approvals-and-sandbox.md)
- [MCP and Cloud](artifact/mcp-and-cloud.md)

## Skill Output:

**Output Type(s):** [Guidance, Markdown, Shell commands, Configuration]

**Output Format:** [Markdown guidance with inline shell commands and configuration examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [None]

## Skill Version(s):

1.0.0 (source: frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
