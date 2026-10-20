## Description:

Create, inspect, process, and optimize image files and visual assets with reliable format choice, resizing, compression, color-profile, metadata, and platform-export checks.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, designers, marketers, and content teams use this skill to choose safe image processing, export, optimization, metadata, and platform-delivery workflows for web, social, ecommerce, photography, branding, screenshots, and accessibility contexts.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Command examples that use package runners can execute unpinned tool versions in sensitive workspaces.

Mitigation: Prefer locally installed, pinned image-processing tools with a lockfile, or run commands in a low-privilege environment.

Risk: Metadata-stripping or image-conversion commands can overwrite inputs or remove orientation, rights, or provenance metadata that the workflow needs.

Mitigation: Work from a copy or preserved master file and confirm metadata decisions before running destructive commands.

## Reference(s):

- [ClawHub Image skill page](https://clawhub.ai/ivangdavila/skills/image)
- [Image skill homepage](https://clawic.com/skills/image)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration guidance]

**Output Format:** [Markdown guidance with optional code blocks and shell command examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Advisory output; commands should be reviewed and adapted before execution.]

## Skill Version(s):

1.0.4 (source: frontmatter and server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
