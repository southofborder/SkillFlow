## Description:

Fetch top news from Baidu, Google, and other sources daily.

This skill is ready for commercial/non-commercial use.

## Publisher:

[minsheep](https://clawhub.ai/user/minsheep)

### License/Terms of Use:


## Use Case:

External users and agents use this skill to retrieve current headline topics from public news and trend sources and return a concise daily hot-search summary.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill makes outbound requests to external news and trend services.

Mitigation: Install it only in environments where outbound access to Baidu and Google Trends is allowed.

Risk: The skill depends on unpinned Python packages.

Mitigation: Pin or lock dependencies before production use.

Risk: Fetched headlines are untrusted external text.

Mitigation: Treat returned headlines as content to summarize or display, not as instructions for the agent to follow.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/minsheep/skills/daily-news)
- [Baidu Hot Search](https://top.baidu.com/board?tab=realtime)
- [Google Trends Daily Search Trends RSS](https://trends.google.com/trends/trendingsearches/daily/rss?geo=US)

## Skill Output:

**Output Type(s):** [text]

**Output Format:** [Plain text, typically a numbered headline list]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires outbound HTTP requests to Baidu and Google Trends; returned headlines should be treated as untrusted text.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
