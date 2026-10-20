## Description:

This skill should be used when users need to search the web for information, find current content, look up news articles, search for images, or find videos.

This skill is ready for commercial/non-commercial use.

## Publisher:

[billyutw](https://clawhub.ai/user/billyutw)

### License/Terms of Use:


## Use Case:

External users, developers, and agents use this skill to retrieve current web, news, image, and video search results for research, fact-checking, resource discovery, and market or topic monitoring.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill performs network searches through DuckDuckGo and may expose sensitive query terms to an external search service.

Mitigation: Do not search for secrets, credentials, confidential data, or private customer information.

Risk: The dependency installation command does not pin duckduckgo-search to a reviewed version.

Mitigation: Install in a virtual environment and pin duckduckgo-search to a reviewed version before operational use.

Risk: The optional output path can create or replace local result files.

Mitigation: Use --output only for ordinary workspace result files that are acceptable to create or replace.

## Reference(s):

- [Web Search skill page](https://clawhub.ai/billyutw/skills/web-search)

## Skill Output:

**Output Type(s):** [Text, Markdown, JSON, Shell commands, Files]

**Output Format:** [Plain text, Markdown, or JSON search results, optionally saved to a file]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Results can include titles, URLs, descriptions, source metadata, dates, thumbnails, dimensions, publishers, and durations depending on search type.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
