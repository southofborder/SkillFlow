## Description:

Assistance with writing literature reviews by searching for academic sources via Semantic Scholar, OpenAlex, Crossref and PubMed APIs.

This skill is ready for commercial/non-commercial use.

## Publisher:

[weird-aftertaste](https://clawhub.ai/user/weird-aftertaste)

### License/Terms of Use:


## Use Case:

External users and developers use this skill to search academic literature, retrieve paper metadata, compare sources, and draft literature review sections with citations.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Literature search terms, configured polite-contact email values, and optional API keys may be sent to academic provider APIs.

Mitigation: Avoid sensitive private research queries when provider exposure is unacceptable, and configure only the API credentials needed for the selected providers.

Risk: Generated review drafts and bibliographies may contain incomplete or misleading citation details from upstream metadata.

Mitigation: Cross-check important citations against DOI or PMID records before relying on them in a literature review.

## Reference(s):

- [Semantic Scholar Graph API](https://api.semanticscholar.org/graph/v1)
- [OpenAlex API](https://api.openalex.org)
- [Crossref Works API](https://api.crossref.org/works)
- [NCBI Entrez E-utilities](https://eutils.ncbi.nlm.nih.gov/entrez/eutils)
- [ClawHub Skill Page](https://clawhub.ai/weird-aftertaste/skills/literature-review)

## Skill Output:

**Output Type(s):** [text, markdown, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with shell command examples and JSON search results from the helper script]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Search results can include paper identifiers, DOIs, titles, years, authors, abstracts, venues, citation counts, and source labels.]

## Skill Version(s):

1.2.0 (source: frontmatter and release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
