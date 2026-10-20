## Description:

Generate images using Qwen Image API (Alibaba Cloud DashScope). Use when users request image generation with Chinese prompts or need high-quality AI-generated images from text descriptions.

This skill is ready for commercial/non-commercial use.

## Publisher:

[robin797860](https://clawhub.ai/user/robin797860)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to generate images from Chinese or English text prompts through Alibaba Cloud DashScope/Qwen Image. It returns temporary image URLs for markdown display and can save generated images locally when requested.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Paid DashScope API credentials may be exposed when passed through command-line arguments or logs.

Mitigation: Prefer DASHSCOPE_API_KEY or a protected secret store, and avoid putting API keys in shared commands, logs, or shell history.

Risk: Prompts are sent to Alibaba Cloud DashScope for image generation.

Mitigation: Use the skill only when the user is comfortable sending the prompt content to that third-party service.

Risk: Disabling SSL verification for downloads can weaken transport-integrity checks.

Mitigation: Keep certificate verification enabled unless a trusted network environment requires otherwise and the download-integrity risk is accepted.

## Reference(s):

- [Qwen Image Skill Page](https://clawhub.ai/robin797860/skills/qwen-image)
- [Alibaba Cloud DashScope](https://dashscope.aliyuncs.com/)
- [DashScope API Key Console](https://dashscope.console.aliyun.com/)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Files]

**Output Format:** [Plain-text script output with MEDIA_URL or MEDIA markers, rendered by the agent as markdown image links.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Returns temporary Alibaba Cloud OSS image URLs by default; local image files are created only when a filename is requested.]

## Skill Version(s):

1.0.0 (source: server release metadata, released 2026-02-06)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
