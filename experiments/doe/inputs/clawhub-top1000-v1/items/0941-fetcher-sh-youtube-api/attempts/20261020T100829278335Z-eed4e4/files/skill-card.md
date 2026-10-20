## Description:

A YouTube API alternative on fetcher.sh for paid, plain HTTP access to YouTube search, channel, video, playlist, comments, hashtag, and trending data without OAuth or daily quota limits.

This skill is ready for commercial/non-commercial use.

## Publisher:

[fetcher-sh](https://clawhub.ai/user/fetcher-sh)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and agents use this skill to query YouTube data through fetcher.sh for search, monitoring, analytics inputs, content discovery, and trend tracking workflows. It is most relevant when an agent needs YouTube data through HTTP GET or MCP calls without using the official YouTube Data API quota model.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill sends YouTube search terms, channel IDs, video IDs, playlist IDs, and related request data to youtube.fetcher.sh.

Mitigation: Confirm that requests are appropriate for the external service before use, especially for sensitive searches or automated workflows.

Risk: Calls can consume prepaid credits or x402 pay-per-call funds.

Mitigation: Protect FETCHER_API_KEY as a billing credential and confirm before enabling workflows that could make many paid calls.

## Reference(s):

- [Server-resolved GitHub provenance](https://github.com/fetcher-sh/fetcher-skills/tree/main/skills/youtube-api)
- [ClawHub skill page](https://clawhub.ai/fetcher-sh/skills/youtube-api)
- [Full agent setup](https://youtube.fetcher.sh/skill.md)
- [OpenAPI 3.1 contract](https://youtube.fetcher.sh/openapi.json)
- [Condensed catalog](https://youtube.fetcher.sh/llms.txt)
- [Service site](https://youtube.fetcher.sh)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, API calls, code]

**Output Format:** [Markdown with bash, JSON, and HTTP endpoint examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May describe paid fetcher.sh HTTP GET or MCP calls and credential handling for FETCHER_API_KEY.]

## Skill Version(s):

0.1.0 (source: release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
