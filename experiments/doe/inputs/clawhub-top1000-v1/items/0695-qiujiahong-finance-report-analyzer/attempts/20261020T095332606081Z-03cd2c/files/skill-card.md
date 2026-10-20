## Description:

Analyze financial data from uploaded Excel/PDF files and generate interactive reports with sparkline trend charts, with optional PDF, DOCX, Markdown, and HTML output.

This skill is ready for commercial/non-commercial use.

## Publisher:

[qiujiahong](https://clawhub.ai/user/qiujiahong)

### License/Terms of Use:

MIT

## Use Case:

External users, developers, and analysts use this skill to turn uploaded financial spreadsheets or PDFs into structured company analysis reports with metrics, trends, forecast markers, and optional industry context. It is suited for report generation from local files or explicitly approved Feishu file workflows.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The security evidence reports local credential use, external file transfer, runtime package installation, and unsafe document conversion settings.

Mitigation: Review before installing, run in an isolated environment with pinned dependencies, and prefer local HTML output.

Risk: Processing untrusted spreadsheets or PDFs may expose the agent environment to unsafe content or misleading financial data.

Mitigation: Avoid untrusted inputs and verify generated analysis against authoritative financial sources before use.

Risk: Feishu workflows may download, upload, or send files using workspace credentials.

Mitigation: Require explicit approval before any Feishu credential use, file download, report upload, or message send.

## Reference(s):

- [Financial Metrics Reference](references/metrics.md)
- [ClawHub Skill Page](https://clawhub.ai/qiujiahong/skills/finance-report-analyzer)

## Skill Output:

**Output Type(s):** [Analysis, Files, Markdown, Shell commands, Configuration instructions]

**Output Format:** [HTML report files with optional PDF, DOCX, or Markdown outputs, plus Markdown guidance and shell command examples for acquisition and delivery workflows]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [HTML is always generated as the base report; PDF, DOCX, and Markdown depend on local conversion tools.]

## Skill Version(s):

1.2.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
