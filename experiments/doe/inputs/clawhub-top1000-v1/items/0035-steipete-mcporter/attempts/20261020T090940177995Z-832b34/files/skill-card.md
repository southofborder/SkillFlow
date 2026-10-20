## Description:

Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to operate the mcporter CLI for discovering MCP servers, invoking tools, managing OAuth and configuration, running daemons, and generating client or type artifacts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill enables broad MCP operations, including OAuth login, configuration changes, daemon control, remote MCP URLs, and stdio commands.

Mitigation: Confirm each OAuth login, configuration change, daemon action, remote MCP URL, and --stdio command before use.

Risk: The security summary reports broad MCP, auth, config, local command, and daemon capabilities without enough scoping or safety guidance.

Mitigation: Install only when broad mcporter authority is intended, and avoid sending secrets or running scripts unless the server or local code is trusted.

## Reference(s):

- [Mcporter homepage](http://mcporter.dev)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/mcporter)

## Skill Output:

**Output Type(s):** [shell commands, configuration, code, guidance]

**Output Format:** [Markdown with inline shell commands and CLI examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce JSON-oriented guidance when using mcporter JSON arguments or --output json.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
