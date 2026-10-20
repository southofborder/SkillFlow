## Description:

A Reddit API alternative on fetcher.sh for searching Reddit posts, subreddits, users, feeds, profiles, and comment trees through paid HTTP or MCP access without OAuth app registration.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fetcher-sh](https://clawhub.ai/user/fetcher-sh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to retrieve Reddit data for search, social listening, monitoring, sentiment-analysis inputs, and data pipeline workflows. It is suited for workflows that need Reddit post, comment, subreddit, feed, and user data without managing Reddit OAuth credentials.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Reddit search terms, subreddit names, post IDs, and usernames are sent to the third-party reddit.fetcher.sh service and paid calls may incur charges.

Mitigation: Use approved data-sharing workflows, avoid regulated or sensitive internal identifiers in requests, and review expected payment behavior before connecting agents.

Risk: Bearer API keys may be exposed if placed directly in shared MCP configuration files or committed examples.

Mitigation: Store the key in environment variables or a secrets manager and keep committed configuration free of live credentials.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/fetcher-sh/skills/reddit-api)
- [Server-resolved GitHub provenance](https://github.com/fetcher-sh/fetcher-skills/tree/main/skills/reddit-api)
- [Full agent setup](https://reddit.fetcher.sh/skill.md)
- [OpenAPI 3.1 contract](https://reddit.fetcher.sh/openapi.json)
- [Condensed catalog](https://reddit.fetcher.sh/llms.txt)
- [Reddit Fetcher site](https://reddit.fetcher.sh)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, API calls, markdown]

**Output Format:** [Markdown with HTTP examples, shell commands, JSON configuration, and endpoint reference tables]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Guidance covers paid third-party API calls, Bearer-key authentication, x402 payment flow, MCP configuration, and JSON API responses.]

## Skill Version(s):

0.1.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
