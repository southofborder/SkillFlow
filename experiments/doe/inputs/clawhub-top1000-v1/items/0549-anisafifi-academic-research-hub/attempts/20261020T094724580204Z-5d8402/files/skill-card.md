## Description:

Search academic papers across arXiv, PubMed, and Semantic Scholar, retrieve paper metadata, download available PDFs, and export citations or bibliographies.

This skill is ready for commercial/non-commercial use.

## Publisher:

[anisafifi](https://clawhub.ai/user/anisafifi)

### License/Terms of Use:

Proprietary

## Use Case:

External researchers, students, and developers use this skill to search scholarly databases, retrieve paper metadata, download available arXiv PDFs, and export citations or bibliographies for literature reviews.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Installing unpinned Python dependencies or using elevated privileges can increase local environment risk.

Mitigation: Install in a virtual environment, avoid elevated privileges, and prefer pinned dependencies or a reviewed lockfile.

Risk: Academic searches and PDF downloads use network access and can write files to local output directories.

Mitigation: Use downloads deliberately, keep result counts small, and choose output directories you are comfortable modifying.

Risk: Documentation mentions Google Scholar support, but the inspected script only implements arXiv, PubMed, and Semantic Scholar sources.

Mitigation: Rely on the implemented sources unless Google Scholar behavior is separately reviewed and added.

## Reference(s):

- [ClawHub Skill Page](https://clawhub.ai/anisafifi/skills/academic-research-hub)
- [Academic Research Hub Readme](artifact/references/readme.md)
- [arXiv API Documentation](https://arxiv.org/help/api)
- [PubMed E-utilities Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [Semantic Scholar API](https://api.semanticscholar.org/)

## Skill Output:

**Output Type(s):** [text, markdown, JSON, BibTeX, RIS, files, shell commands, guidance]

**Output Format:** [Plain text, JSON, BibTeX, RIS, Markdown, and downloaded PDF files.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May write search results via --output and download available arXiv PDFs via --download and --output-dir.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
