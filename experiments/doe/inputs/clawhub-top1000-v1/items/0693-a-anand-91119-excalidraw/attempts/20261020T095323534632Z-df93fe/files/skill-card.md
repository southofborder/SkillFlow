## Description:

Generate hand-drawn style diagrams, flowcharts, and architecture diagrams as PNG images from Excalidraw JSON.

This skill is ready for commercial/non-commercial use.

## Publisher:

[a-anand-91119](https://clawhub.ai/user/a-anand-91119)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to create Excalidraw JSON for flowcharts, architecture diagrams, and other hand-drawn style diagrams, then render them as PNG images.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Setup installs Node dependencies and downloads fonts at setup time, creating supply-chain exposure.

Mitigation: Run setup as an unprivileged user, avoid sudo, prefer npm ci from the lockfile, and review dependency updates before installation.

Risk: The documented workflow uses predictable /tmp input and output names, which can be unsafe when content or names are influenced by others.

Mitigation: Use unique temporary input and output paths for each render job.

Risk: The server security verdict is suspicious because setup-time downloads and temporary-file behavior need review before deployment.

Mitigation: Review and scan the skill before deployment and update vulnerable transitive dependencies.

## Reference(s):

- [Excalidraw Element Schema Reference](references/element-schema.md)
- [ClawHub Skill Page](https://clawhub.ai/a-anand-91119/skills/excalidraw)

## Skill Output:

**Output Type(s):** [Code, Shell commands, Guidance, Files]

**Output Format:** [Markdown guidance with Excalidraw JSON snippets and shell commands; rendered output is a PNG file.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses Excalidraw element arrays and a local Node renderer.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
