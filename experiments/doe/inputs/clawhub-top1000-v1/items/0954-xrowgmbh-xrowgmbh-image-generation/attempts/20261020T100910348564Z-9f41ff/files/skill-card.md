## Description:

Create or revise document, PDF, web, or review images with the requested format, sharp raster output, and artifact validation.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xrowgmbh](https://clawhub.ai/user/xrowgmbh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and engineers use this skill to create or revise images for documents, web pages, reviews, and release artifacts, then validate the resulting files and rebuilt documents.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Image-generation guidance may lead to output that misses the requested format, resolution, or readability requirements.

Mitigation: Confirm the requested format and target dimensions, then inspect the generated image and its actual downstream rendering before release.

Risk: The bundled checker verifies sibling-file presence and freshness, but not image quality or format correctness.

Mitigation: Use the checker as a structural check only and separately review the generated files and rebuilt documents.

## Reference(s):

- [Image Generation on ClawHub](https://clawhub.ai/xrowgmbh/skills/xrowgmbh-image-generation)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Image files]

**Output Format:** [Markdown guidance and shell commands; generated image files in SVG, PNG, and WebP formats]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Image formats and dimensions follow the task requirements.]

## Skill Version(s):

1.114.1 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
