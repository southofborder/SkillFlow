## Description:

Generates editable PowerPoint presentations from JSON slide specifications, including cover, agenda, content, table, chart, timeline, image, quote, summary, and contact slides.

This skill is ready for commercial/non-commercial use.

## Publisher:

[tobewin](https://clawhub.ai/user/tobewin)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, business users, and agents use this skill to turn structured JSON content into standard editable PPTX presentations for reports, lectures, pitches, and project updates.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The workflow depends on installing python-pptx from pip, so dependency version drift or an unpinned install can affect behavior.

Mitigation: Install in a virtual environment and pin the dependency version before using the generator in repeatable workflows.

Risk: JSON slide input can reference local image paths and choose the output path, causing the script to read referenced files and write the requested PPTX file.

Mitigation: Review JSON inputs before execution, especially image_path and output values, and run the generator in a workspace where intended reads and writes are acceptable.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/tobewin/skills/pptx-generator)
- [Publisher profile](https://clawhub.ai/user/tobewin)

## Skill Output:

**Output Type(s):** [Files, Shell commands, Configuration instructions]

**Output Format:** [PPTX file generated from JSON input, with Markdown and shell command guidance for the agent workflow]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The generated presentation is editable in PowerPoint-compatible tools; JSON input controls slide type, style, content, images, footer, page numbers, and output path.]

## Skill Version(s):

2.0.3 (source: server release evidence; artifact frontmatter and script report 2.0.0)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
