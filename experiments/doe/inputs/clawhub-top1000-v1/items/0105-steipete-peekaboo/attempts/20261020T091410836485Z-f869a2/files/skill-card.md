## Description:

Capture and automate macOS UI with the Peekaboo CLI.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and automation-focused users use this skill to let an agent inspect, capture, and operate macOS application interfaces through Peekaboo CLI commands.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill enables broad macOS screen inspection, clipboard access, dialog interaction, and input control.

Mitigation: Install only from trusted Peekaboo package sources, grant Screen Recording and Accessibility permissions deliberately, and review automation actions before allowing clicks, typing, clipboard reads, or dialog interaction.

Risk: Command examples may expose sensitive text if reused with real credentials or private clipboard data.

Mitigation: Use placeholder values in examples, avoid entering real passwords through shared prompts or logs, and clear or avoid sensitive clipboard contents before running automation.

## Reference(s):

- [Peekaboo homepage](https://peekaboo.boo)
- [ClawHub skill page](https://clawhub.ai/steipete/skills/peekaboo)
- [Publisher profile](https://clawhub.ai/user/steipete)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Configuration]

**Output Format:** [Markdown with inline shell commands and command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include JSON-producing Peekaboo command examples for scripting.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
