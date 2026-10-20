## Description:

Convert documents and files to Markdown using markitdown for LLM processing or text analysis.

This skill is ready for commercial/non-commercial use.

## Publisher:

[steipete](https://clawhub.ai/user/steipete)

### License/Terms of Use:


## Use Case:

Developers and agents use this skill to convert PDFs, Office documents, web and data files, images, audio, archives, YouTube URLs, and EPubs into Markdown for LLM processing or text analysis.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill runs a third-party conversion command through uvx at runtime.

Mitigation: Use it only on files selected for conversion, and prefer a pinned or reviewed markitdown version when handling sensitive content.

Risk: Document conversion may process sensitive local files or optionally use an external Document Intelligence endpoint.

Mitigation: Run in a sandbox with limited file, credential, and network access, and enable external document processing only when approved for the data.

## Reference(s):


## Skill Output:

**Output Type(s):** [markdown, shell commands, guidance, configuration]

**Output Format:** [Markdown guidance with inline shell commands and optional Markdown file output]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can write converted Markdown to stdout or an output file; first run may cache dependencies.]

## Skill Version(s):

1.0.0 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
