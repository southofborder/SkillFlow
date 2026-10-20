## Description:

Control desktop applications on Windows: launch, close, focus, resize, move windows, simulate keyboard and mouse input, manage processes, control VS Code, read clipboard, and capture screen information.

This skill is ready for commercial/non-commercial use.

## Publisher:

[lexylent](https://clawhub.ai/user/lexylent)

### License/Terms of Use:


## Use Case:

Developers and agent users use this skill to let an agent operate Windows desktop applications through explicit PowerShell actions for window management, input simulation, VS Code control, process management, clipboard access, screenshots, and display inspection.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill gives an agent broad control over Windows desktop applications.

Mitigation: Install it only when that control is intentional, and limit use to explicit user-requested tasks.

Risk: Window closing, process termination, and simulated input can disrupt active work or affect the wrong application.

Mitigation: Confirm destructive actions first and verify the intended window is focused before sending input.

Risk: Screenshot and clipboard actions can expose sensitive information.

Mitigation: Avoid these commands around sensitive data and warn before overwriting clipboard contents.

Risk: VS Code extension installation can add untrusted software to the user's environment.

Mitigation: Install extensions only after independently verifying the publisher and extension identifier.

## Reference(s):

- [ClawHub release page](https://clawhub.ai/lexylent/skills/desktop-control-win)

## Skill Output:

**Output Type(s):** [Shell commands, Code, Files, Configuration, Guidance]

**Output Format:** [Markdown with PowerShell command examples and script-backed text output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces PowerShell invocations and local script output for Windows desktop automation.]

## Skill Version(s):

1.0.1 (source: server-resolved release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
