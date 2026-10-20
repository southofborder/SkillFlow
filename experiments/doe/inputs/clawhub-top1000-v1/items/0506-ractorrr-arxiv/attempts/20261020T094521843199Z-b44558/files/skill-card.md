## Description:

Search, download, and summarize academic papers from arXiv. Built for AI/ML researchers.

This skill is ready for commercial/non-commercial use.

## Publisher:

[ractorrr](https://clawhub.ai/user/ractorrr)

### License/Terms of Use:

MIT

## Use Case:

Researchers, students, technical writers, learners, and security professionals use this skill to search arXiv, inspect paper metadata and abstracts, download PDFs, and manage a reading list.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill contacts arXiv and can download PDFs to a local papers folder.

Mitigation: Review requested downloads and set ARXIV_PAPERS_DIR to an intended folder before running download commands.

Risk: When MONGODB_URI is configured, the skill can write paper metadata and reading status to MongoDB.

Mitigation: Use a database account limited to the intended database and collection.

Risk: The release uses open-ended dependency versions.

Mitigation: Install in an isolated environment and pin dependencies for governed deployments.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/ractorrr/skills/arxiv)
- [arXiv API documentation](https://arxiv.org/help/api)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, files, guidance]

**Output Format:** [Markdown, plain text, JSON, and downloaded PDF files]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Can contact arXiv, save PDFs to a configured local folder, and optionally store paper metadata and reading status in MongoDB.]

## Skill Version(s):

1.0.4 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
