## Description:

Monitor RSS and Atom feeds for content research. Track blogs, news sites, newsletters, and any feed source. Use when monitoring competitors, tracking industry news, finding content ideas, or building a personal news aggregator. Supports multiple feeds with categories, filters, and summaries.

This skill is ready for commercial/non-commercial use.

## Publisher:

[dimitripantzos](https://clawhub.ai/user/dimitripantzos)

### License/Terms of Use:


## Use Case:

Content researchers, marketers, developers, and analysts use this skill to manage RSS or Atom feed lists, check recent items, filter by category or keywords, and produce list, ideas, or JSON output for monitoring news, competitors, newsletters, and technical topics.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill fetches arbitrary RSS or Atom URLs from the host environment.

Mitigation: Use only trusted feed URLs, run it where localhost, private-network, and cloud metadata services are not exposed to the process, and add URL validation, redirect limits, and private-address blocking before broad or scheduled use.

Risk: Remote feed text is printed to the terminal without sanitization.

Mitigation: Review output before reuse and add terminal-output sanitization before using the skill in automated reporting or scheduled checks.

Risk: Feed responses are not bounded by an explicit response-size limit.

Mitigation: Add response-size limits before broad deployment or use in unattended cron-style checks.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/dimitripantzos/skills/rss-reader)
- [ClawHub publisher profile](https://clawhub.ai/user/dimitripantzos)

## Skill Output:

**Output Type(s):** [Text, Markdown, JSON, Shell commands, Configuration]

**Output Format:** [Console text, Markdown-style content idea summaries, or JSON arrays from the RSS CLI]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Output is generated from configured RSS or Atom feeds and may include remote titles, links, dates, categories, and descriptions.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
