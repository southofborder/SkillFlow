## Description:

Professional Figma design analysis and asset export. Use for extracting design data, exporting assets in multiple formats, auditing accessibility compliance, analyzing design systems, and generating comprehensive design documentation. Read-only analysis of Figma files with powerful export and reporting capabilities.

This skill is ready for commercial/non-commercial use.

## Publisher:

[maddiedreese](https://clawhub.ai/user/maddiedreese)

### License/Terms of Use:


## Use Case:

Developers, designers, and design-system teams use this skill to inspect Figma files, export assets, audit accessibility and style consistency, extract design tokens, and generate design documentation from read-only Figma API data.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Generated HTML reports can include unescaped Figma content that may run active browser content when opened.

Mitigation: Treat generated HTML reports as unsafe unless the Figma file and its collaborators are trusted; review reports before sharing or opening them in privileged browser contexts.

Risk: Figma access tokens can expose design files beyond the intended task scope if mishandled.

Mitigation: Use a least-privileged Figma token from a secret store or environment variable and avoid passing tokens through command-line arguments.

Risk: Asset export workflows can write many generated files into the local workspace.

Mitigation: Run exports into a dedicated output directory and review generated files before reuse or publication.

Risk: Dependencies are specified with lower bounds rather than fully pinned versions.

Mitigation: Install dependencies in an isolated environment and prefer pinned dependency versions for reviewed deployments.

## Reference(s):

- [Figma API Reference](references/figma-api-reference.md)
- [Design Patterns & Component Best Practices](references/design-patterns.md)
- [Accessibility Guidelines for Figma Design](references/accessibility-guidelines.md)
- [Export Formats and Specifications](references/export-formats.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Files, Guidance]

**Output Format:** [Markdown guidance with inline shell commands, generated reports, JSON design data, design-token files, and exported image or document assets]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Uses read-only Figma API access; generated files may include asset exports, manifests, reports, and documentation.]

## Skill Version(s):

2.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
