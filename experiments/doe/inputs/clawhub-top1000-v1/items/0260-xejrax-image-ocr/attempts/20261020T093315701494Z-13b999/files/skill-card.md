## Description:

Extract text from images using Tesseract OCR.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xejrax](https://clawhub.ai/user/xejrax)

### License/Terms of Use:


## Use Case:

Developers and agent users use this skill to extract text from images with Tesseract OCR, including PNG, JPEG, TIFF, and BMP files.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The documented Tesseract installation changes system packages with administrator privileges.

Mitigation: Review and approve the package install command before running it, and install only from trusted package repositories.

Risk: OCR processes image files selected by the user, which may contain sensitive text.

Mitigation: Run OCR only on images the user intends to process and handle extracted text according to the applicable data handling requirements.

## Reference(s):

- [Image Ocr on ClawHub](https://clawhub.ai/xejrax/skills/image-ocr)

## Skill Output:

**Output Type(s):** [text, shell commands, guidance]

**Output Format:** [Plain text and Markdown with inline shell commands]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires Tesseract to be installed before OCR commands can run.]

## Skill Version(s):

1.0.0 (source: release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
