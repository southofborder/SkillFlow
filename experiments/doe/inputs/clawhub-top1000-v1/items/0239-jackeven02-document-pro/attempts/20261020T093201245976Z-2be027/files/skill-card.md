## Description:

Document Pro helps agents read, parse, extract, summarize, and convert common document formats including PDF, DOCX, PPTX, XLSX, TXT, and Markdown.

This skill is ready for commercial/non-commercial use.

## Publisher:

[jackeven02](https://clawhub.ai/user/jackeven02)

### License/Terms of Use:


## Use Case:

Employees, external users, developers, and agents use this skill to inspect user-provided documents, extract text or tables, summarize reports and papers, identify key points, and prepare conversion guidance for common document formats.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill may read document contents that contain sensitive or confidential information.

Mitigation: Use it only with files the user explicitly intends the agent to inspect, and avoid exposing extracted content beyond the requested task.

Risk: Conversions, exports, or file writes could unintentionally change or replace original documents.

Mitigation: Require explicit user instructions before any conversion, export, or file write, and preserve originals when producing derived files.

Risk: Scanned PDFs, complex layouts, images, charts, and tables may produce incomplete or lossy extraction results.

Mitigation: Use OCR when needed and verify important extracted content against the source document before relying on it.

## Reference(s):

- [Document Pro ClawHub Release](https://clawhub.ai/jackeven02/skills/document-pro)
- [jackeven02 ClawHub Publisher Profile](https://clawhub.ai/user/jackeven02)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown or plain text, sometimes with inline code or shell command examples for document extraction and conversion.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include document type, page count, summaries, key points, extracted table data, keywords, and suggested next actions.]

## Skill Version(s):

1.0.0 (source: SKILL.md frontmatter and server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
