## Description:

Search and analyze Reddit content using semantic AI search via the reddapi.dev HTTP API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[dowands](https://clawhub.ai/user/dowands)

### License/Terms of Use:

MIT-0

## Use Case:

External users, developers, and product researchers use this skill to search Reddit discussions, identify user pain points, monitor sentiment, compare products, and validate business ideas with Reddit-sourced feedback.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Reddit research prompts, date filters, and related parameters are sent to the reddapi.dev service.

Mitigation: Avoid entering secrets, customer data, internal strategy, regulated personal data, or confidential product plans into search prompts.

Risk: Search results and AI summaries may be incomplete, stale, biased toward indexed subreddits, or misleading for high-impact decisions.

Mitigation: Use Reddit findings as directional research and verify important conclusions against primary sources or additional evidence before acting.

## Reference(s):

- [ClawHub skill page](https://clawhub.ai/dowands/skills/reddit-insights)
- [reddapi.dev](https://reddapi.dev)
- [Semantic search API](https://reddapi.dev/api/v1/search/semantic)
- [Vector search API](https://reddapi.dev/api/v1/search/vector)
- [MCP endpoint](https://reddapi.dev/api/mcp)

## Skill Output:

**Output Type(s):** [guidance, shell commands, configuration, markdown, API calls]

**Output Format:** [Markdown with inline JSON and bash code blocks]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [May include API request examples, response shapes, query strategies, and setup guidance for REDDAPI_API_KEY.]

## Skill Version(s):

2.3.0 (source: server release evidence)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
