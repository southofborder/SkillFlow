## Description:

Helps agents scrape and crawl websites with Scrapling using HTTP requests, browser automation, concurrent spiders, and adaptive parsing.

This skill is ready for commercial/non-commercial use.

## Publisher:

[d4vinci](https://clawhub.ai/user/d4vinci)

### License/Terms of Use:

BSD 3-Clause

## Use Case:

Developers and other agents use this skill to extract website content, build scraping scripts, and crawl pages with HTTP or browser-based tools.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Scraping or anti-bot features may access sites without authorization.

Mitigation: Scrape only authorized sites and respect site rules and access restrictions.

Risk: Cookies, proxy credentials, and saved browser state can expose sensitive data.

Mitigation: Use real credentials only when necessary and clear local state and caches afterward.

Risk: An exposed MCP HTTP server may allow unauthorized remote access.

Mitigation: Do not expose the server without authentication and TLS.

Risk: Unpinned package or container updates can change the software being run.

Mitigation: Pin package and Docker image versions where possible.

## Reference(s):

- [Scrapling documentation](https://scrapling.readthedocs.io/en/latest/index.html)
- [Scrapling Official Skill on ClawHub](https://clawhub.ai/d4vinci/skills/scrapling-official)
- [Choosing a fetcher](artifact/references/fetching/choosing.md)
- [Spider getting started](artifact/references/spiders/getting-started.md)
- [MCP server guide](artifact/references/mcp-server.md)

## Skill Output:

**Output Type(s):** [Text, Markdown, Code, Shell commands, Guidance]

**Output Format:** [Markdown with Python and shell examples; extracted page text or Markdown when run]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Scraping workflows may save extracted content to local files.]

## Skill Version(s):

0.5.0 (source: ClawHub release; skill frontmatter says 0.5)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
