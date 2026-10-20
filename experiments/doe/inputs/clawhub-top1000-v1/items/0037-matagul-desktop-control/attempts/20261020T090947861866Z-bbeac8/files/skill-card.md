## Description:

Advanced desktop automation with mouse, keyboard, screen capture, window management, clipboard operations, and optional higher-level task planning.

This skill is ready for commercial/non-commercial use.

## Publisher:

[matagul](https://clawhub.ai/user/matagul)

### License/Terms of Use:


## Use Case:

Developers and agent builders use this skill to automate local desktop workflows that require mouse movement, keyboard input, screenshots, image matching, pixel inspection, window activation, or clipboard access.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can control the active desktop session, including mouse movement, clicks, keyboard input, hotkeys, and application focus.

Mitigation: Use it only in trusted desktop sessions, keep failsafe enabled, and review planned actions before allowing automation near sensitive applications.

Risk: The skill can capture screenshots and read or write clipboard contents, which may expose private documents, passwords, tokens, or other sensitive data.

Mitigation: Avoid running it while sensitive material is visible or stored in the clipboard, and clear sensitive clipboard contents before use.

Risk: Server security guidance says some sensitive actions bypass the advertised approval mode.

Mitigation: Do not rely on approval mode as a complete control until the code is fixed; use external supervision and restrict the operating environment.

## Reference(s):

- [Desktop Control on ClawHub](https://clawhub.ai/matagul/skills/desktop-control)
- [Publisher profile: matagul](https://clawhub.ai/user/matagul)

## Skill Output:

**Output Type(s):** [Code, Shell commands, Configuration, Guidance]

**Output Format:** [Markdown documentation with Python and shell code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May produce screenshots or interact with the active desktop session when its Python APIs are executed.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
