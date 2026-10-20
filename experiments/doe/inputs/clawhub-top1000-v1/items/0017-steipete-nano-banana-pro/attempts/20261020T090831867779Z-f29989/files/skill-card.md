## Description:

Generate and edit images with Nano Banana Pro (Gemini 3 Pro Image), including text-to-image and image-to-image workflows at 1K, 2K, or 4K resolution.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to generate new images or edit existing images through Google's Gemini 3 Pro Image API, saving PNG outputs at the requested resolution.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Gemini API keys can be exposed if pasted into chat or passed on the command line with --api-key.

Mitigation: Prefer GEMINI_API_KEY in a protected environment and avoid sharing keys in prompts, chat, logs, or shell history.

Risk: Prompts and input images are sent to Google's API during generation or editing.

Mitigation: Avoid confidential prompts or private images unless Google API upload is acceptable for the user and organization.

Risk: The helper script declares minimum dependency versions without a lockfile.

Mitigation: Pin dependencies or use a lockfile before routine use.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/steipete/skills/nano-banana-pro)

## Skill Output:

**Output Type(s):** [Guidance, Shell commands, Configuration instructions, Files]

**Output Format:** [Markdown guidance with inline shell commands and PNG image files from the helper script]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [The helper script saves a PNG file to the selected output path and prints the resolved file path; it may also print model text returned by the API.]

## Skill Version(s):

1.0.1 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
