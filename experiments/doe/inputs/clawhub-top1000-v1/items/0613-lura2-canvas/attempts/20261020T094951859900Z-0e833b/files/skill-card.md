## Description:

Display and control HTML content on connected Mac, iOS, or Android OpenClaw nodes through a web-based canvas with live reload and remote actions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[lura2](https://clawhub.ai/user/lura2)

### License/Terms of Use:


## Use Case:

Developers and agent users use this skill to present, navigate, update, snapshot, and hide HTML canvas content on connected OpenClaw Mac, iOS, and Android nodes for dashboards, visualizations, games, and demos.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Remote WebView JavaScript execution can affect pages shown in the canvas.

Mitigation: Use eval only on trusted pages and keep canvas actions scoped to trusted OpenClaw nodes.

Risk: Canvas snapshots may capture private or sensitive content.

Mitigation: Treat snapshots as sensitive and avoid capturing canvases that display private data.

Risk: Navigating nodes to untrusted URLs can expose users and node canvases to unsafe content.

Mitigation: Use trusted URLs and trusted networks when presenting or navigating canvas content.

## Reference(s):

- [Canvas skill page](https://clawhub.ai/lura2/skills/canvas)

## Skill Output:

**Output Type(s):** [guidance, markdown, code, shell commands, configuration]

**Output Format:** [Markdown guidance with inline command, JSON configuration, and HTML code examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include canvas action commands for presenting, navigating, evaluating JavaScript in, snapshotting, or hiding node canvases.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
