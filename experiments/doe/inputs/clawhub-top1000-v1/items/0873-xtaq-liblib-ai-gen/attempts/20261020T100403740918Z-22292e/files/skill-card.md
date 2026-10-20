## Description:

Generate images with Seedream4.5 and videos with Kling via LiblibAI API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xtaq](https://clawhub.ai/user/xtaq)

### License/Terms of Use:


## Use Case:

Developers and external users use this skill to generate images, text-to-video clips, image-to-video clips, and task status checks through the LiblibAI API from an agent workflow.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Prompts, reference image URLs, and generated-media requests are sent to the external LiblibAI API.

Mitigation: Do not submit confidential prompts, private image URLs, regulated data, or internal-only media unless organizational policy permits use of LiblibAI for that content.

Risk: The skill requires LiblibAI API credentials through environment variables.

Mitigation: Store LIB_ACCESS_KEY and LIB_SECRET_KEY in protected environment variables and do not commit them to source control or logs.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/xtaq/skills/liblib-ai-gen)
- [LiblibAI API endpoint](https://openapi.liblibai.cloud)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown with shell commands and JSON API results]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include generated task identifiers, progress updates, image URLs, or video URLs returned by LiblibAI.]

## Skill Version(s):

1.0.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
