## Description:

Instagram Reels helps agents create CellCog-powered social media videos and posts, including Instagram Reels, TikTok videos, Stories, carousels, and social posts from a prompt.

This skill is ready for commercial/non-commercial use.

## Publisher:

[cellcog](https://clawhub.ai/user/cellcog)

### License/Terms of Use:

MIT-0

## Use Case:

External creators, marketers, and agents use this skill to request short-form social video, carousel, Story, and static-post assets through CellCog. It is intended for campaign and social-content generation where the user supplies the creative brief and platform format.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Creative prompts and task details are sent to an external CellCog service.

Mitigation: Review CellCog's data-handling terms before using private campaigns, client materials, unpublished brand assets, or third-party media.

Risk: The skill recommends mutable, unpinned package installation commands.

Mitigation: Use pinned, reviewed package versions and install in a constrained environment.

Risk: The skill requires CELLCOG_API_KEY, which could expose service access if mishandled.

Mitigation: Provide only the required environment variable and limit the runtime to files needed for the task.

Risk: AI video generation quality and cost can be unpredictable for some prompts.

Mitigation: Set expectations for iteration, review generated media before publication, and avoid using unapproved third-party assets.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/cellcog/skills/instagram-reels-tiktok-cellcog)
- [CellCog Homepage](https://cellcog.ai)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration guidance]

**Output Format:** [Markdown with Python examples and setup commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires python3, the cellcog package, and CELLCOG_API_KEY for service access.]

## Skill Version(s):

1.0.18 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
