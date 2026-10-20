## Description:

Presentation Slides helps agents generate CellCog-powered slide decks for pitch, keynote, business, educational, investor, and similar presentation workflows in PDF or native PPTX format.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cellcog](https://clawhub.ai/user/cellcog)

### License/Terms of Use:

MIT-0

## Use Case:

Developers, agents, and business users use this skill to request presentation decks through CellCog for business, sales, education, events, investor updates, and image slideshow workflows. It is intended for generating polished presentation files from prompts, outlines, metrics, source material, and requested design direction.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill includes unpinned CellCog installation commands, which can introduce supply-chain uncertainty.

Mitigation: Prefer pinned or otherwise verified CellCog package versions before using the skill in controlled environments.

Risk: Presentation prompts and supplied files may be sent to CellCog's service.

Mitigation: Use the skill only with material approved for CellCog processing and avoid submitting confidential or regulated content unless appropriate agreements and controls are in place.

Risk: CELLCOG_API_KEY is required to use the skill.

Mitigation: Store CELLCOG_API_KEY as a secret, avoid printing it in logs, and rotate it if exposure is suspected.

Risk: The skill directs users to rely on the separate cellcog skill for SDK details.

Mitigation: Review the cellcog skill and its setup guidance before depending on SDK behavior in production workflows.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/cellcog/skills/presentation-slides-cellcog)
- [CellCog Website](https://cellcog.ai)
- [CellCog Publisher Profile](https://clawhub.ai/user/cellcog)

## Skill Output:

**Output Type(s):** [Guidance, Code, Shell commands, Configuration instructions, Files]

**Output Format:** [Markdown guidance with Python snippets and shell commands; downstream CellCog output as PDF, PPTX, or interactive HTML presentation files.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires python3, the cellcog dependency, and CELLCOG_API_KEY. The skill recommends creative chat mode for presentation generation.]

## Skill Version(s):

1.0.21 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
