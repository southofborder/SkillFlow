## Description:

Computer Use lets agents control a headless Linux desktop through Xvfb, XFCE, xdotool actions, screenshots, and optional VNC live viewing.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ram-raghav-s](https://clawhub.ai/user/ram-raghav-s)

### License/Terms of Use:


## Use Case:

Developers and engineers use this skill to give an agent GUI-level control of a headless Linux desktop for browser and desktop application workflows. It provides setup guidance and shell actions for screenshots, mouse movement, clicking, dragging, scrolling, typing, key presses, waiting, zoomed screenshots, and live VNC viewing.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill installs persistent remote desktop control with weak access controls.

Mitigation: Install only on an isolated server or VM, require localhost-only binding and authentication for VNC and noVNC, and do not expose ports 5900 or 6080 publicly.

Risk: The setup makes system-wide desktop changes that can affect the host environment.

Mitigation: Review the generated systemd services before running setup-vnc.sh and be prepared to remove the services and restore /usr/bin/xfdesktop.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ram-raghav-s/skills/computer-use)

## Skill Output:

**Output Type(s):** [text, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance, shell commands, status text, and base64-encoded PNG screenshots]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses a 1024x768 Xvfb display on :99 and returns screenshots after most actions.]

## Skill Version(s):

1.2.1 (source: frontmatter and ClawHub release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
