## Description:

Edit images with AI inpainting, outpainting, background removal, upscaling, and restoration tools.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ivangdavila](https://clawhub.ai/user/ivangdavila)

### License/Terms of Use:


## Use Case:

Developers and image editors use this skill to choose AI image-editing techniques and follow practical workflows for object removal, outpainting, background removal, upscaling, restoration, and style transfer.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Some documented cloud workflows upload selected images, masks, prompts, or metadata to third-party providers.

Mitigation: Confirm the image and related metadata may be sent to the named provider before using cloud examples; prefer local tools for private, regulated, customer, family, or confidential images.

Risk: Local tool installation commands can install image-processing dependencies into the user's environment.

Mitigation: Install dependencies in an isolated environment and review package versions before use.

Risk: AI restoration and enhancement can alter important visual details such as faces, edges, texture, or image grain.

Mitigation: Preserve the original file, save edits separately, and review outputs manually before relying on them.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/ivangdavila/skills/image-edit)
- [Background Removal](artifact/background-removal.md)
- [Inpainting](artifact/inpainting.md)
- [Outpainting](artifact/outpainting.md)
- [Image Restoration](artifact/restoration.md)
- [Style Transfer](artifact/style-transfer.md)
- [Image Editing Tools](artifact/tools.md)
- [Upscaling](artifact/upscaling.md)
- [remove.bg API](https://api.remove.bg/v1.0/removebg)
- [ClipDrop Remove Background API](https://clipdrop-api.co/remove-background/v1)
- [Photoroom Segment API](https://sdk.photoroom.com/v1/segment)
- [Stability AI Image-to-Image API](https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image)
- [Magnific Upscale API](https://api.magnific.ai/v1/upscale)

## Skill Output:

**Output Type(s):** [guidance, markdown, code, shell commands, configuration]

**Output Format:** [Markdown guidance with code snippets and shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes local and cloud image-editing workflows; some cloud examples require API keys and may upload selected images to third-party providers.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
