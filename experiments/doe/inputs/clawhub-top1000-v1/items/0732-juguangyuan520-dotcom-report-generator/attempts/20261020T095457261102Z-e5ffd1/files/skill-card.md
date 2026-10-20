## Description:

Generates a structured report HTML based on a specific template.

This skill is ready for commercial/non-commercial use.

## Publisher:

[juguangyuan520-dotcom](https://clawhub.ai/user/juguangyuan520-dotcom)

### License/Terms of Use:


## Use Case:

Agents use this skill to turn user-provided report content into a responsive HTML report and guide screenshot capture for sharing or presentation.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Raw report content may be rendered into local HTML without escaping before browser viewing.

Mitigation: Use trusted report text only, or sanitize input before generation and render screenshots in a sandboxed browser with scripts and network access disabled.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/juguangyuan520-dotcom/skills/report-generator)
- [Publisher profile](https://clawhub.ai/user/juguangyuan520-dotcom)

## Skill Output:

**Output Type(s):** [text, code, shell commands, configuration, guidance]

**Output Format:** [JSON input guidance and generated HTML file path, with instructions for screenshot capture]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Produces a local HTML report from structured report fields and expects a browser-capable agent to capture screenshots when needed.]

## Skill Version(s):

1.0.2 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
