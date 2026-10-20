## Description:

Extract text from PDF files for LLM processing.

This skill is ready for commercial/non-commercial use.

## Publisher:

[xejrax](https://clawhub.ai/user/xejrax)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to extract plain text from PDF files, including page ranges, so PDF content can be processed by an LLM.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill requires installing the poppler-utils system package to provide pdftotext.

Mitigation: Install poppler-utils only through a trusted system package manager after approving the added dependency.

Risk: PDF text extraction can expose the contents of selected PDFs to downstream LLM processing.

Mitigation: Use the skill only on PDFs the agent is authorized to process and handle extracted text under the applicable data policy.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/xejrax/skills/pdf-extract)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, guidance]

**Output Format:** [Markdown with inline bash commands and plain-text extraction guidance]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires the pdftotext binary from the poppler-utils package.]

## Skill Version(s):

1.0.0 (source: server-resolved release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
