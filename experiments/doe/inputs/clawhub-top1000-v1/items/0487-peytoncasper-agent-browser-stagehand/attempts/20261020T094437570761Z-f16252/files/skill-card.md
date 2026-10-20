## Description:

Automate web browser interactions using natural language via CLI commands.

This skill is ready for commercial/non-commercial use.

## Publisher:

[peytoncasper](https://clawhub.ai/user/peytoncasper)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to navigate websites, interact with page elements, extract structured web data, capture screenshots, and manage browser sessions through Stagehand CLI commands.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill grants broad browser automation authority, including web access, session reuse, downloads, and optional remote browser execution.

Mitigation: Use it only in workspaces where broad browser automation is acceptable, isolate or clear browser profiles before sensitive account use, and treat downloaded files as untrusted.

Risk: The reviewed artifact documents installing and linking an npm CLI, but the CLI implementation was not included in the artifact evidence.

Mitigation: Verify the actual npm package or source before running npm install or npm link.

Risk: Persistent Chrome profile behavior may retain saved passwords, cookies, and authenticated sessions between runs.

Mitigation: Use isolated profiles for sensitive operations and clear session state when a task is complete.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/peytoncasper/skills/agent-browser-stagehand)
- [Browser Automation Examples](EXAMPLES.md)
- [Browser Automation CLI Reference](REFERENCE.md)

## Skill Output:

**Output Type(s):** [shell commands, configuration, text, files, guidance]

**Output Format:** [Markdown guidance with CLI commands; browser commands return JSON and may create PNG screenshots or downloaded files.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses a persistent Chrome profile when local mode is selected; screenshots are written under ./agent/browser_screenshots/ and downloads under ./agent/downloads/.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
