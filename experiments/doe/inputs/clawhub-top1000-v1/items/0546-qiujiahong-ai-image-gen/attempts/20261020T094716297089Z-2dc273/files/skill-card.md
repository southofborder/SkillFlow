## Description:

AI Image Gen helps agents generate images from text prompts through a Gemini Flash Image compatible API, with documented model options for common aspect ratios and standard, 2K, and 4K resolutions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[qiujiahong](https://clawhub.ai/user/qiujiahong)

### License/Terms of Use:

MIT

## Use Case:

Developers and agents use this skill to convert user image requests into prompts and API calls that save generated image files locally.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Prompts and API credentials are sent to configurable third-party endpoints, which can expose sensitive content if the endpoint is not trusted.

Mitigation: Review the provider endpoint before use, avoid sensitive prompts, and use a narrowly scoped, revocable API key.

Risk: The script accepts an output path and can write files locally, which is risky when untrusted requests choose paths.

Mitigation: Constrain output locations to an approved workspace and review paths before execution.

Risk: The documentation claims editing and image-to-image support, but the packaged script only implements text-prompt image generation.

Mitigation: Treat editing and image-to-image workflows as unsupported until the package includes clear implementation and scoping.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/qiujiahong/skills/ai-image-gen)
- [FoxCode API key registration](https://foxcode.rjj.cc/auth/register?aff=R0P5ZY)

## Skill Output:

**Output Type(s):** [Shell commands, Configuration instructions, Files, Guidance]

**Output Format:** [Markdown guidance with inline shell commands and generated image file paths]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires IMAGE_GEN_API_KEY and can write image files to a selected local output path.]

## Skill Version(s):

1.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
