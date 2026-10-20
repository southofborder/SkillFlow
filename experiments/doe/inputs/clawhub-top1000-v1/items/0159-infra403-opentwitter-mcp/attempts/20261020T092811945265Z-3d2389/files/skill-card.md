## Description:

Provides Twitter/X profiles, posts, search, follower activity, deleted posts, and meme-token evidence through the 6551 API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[infra403](https://clawhub.ai/user/infra403)

### License/Terms of Use:

MIT-0

## Use Case:

Developers and other users query Twitter/X accounts and posts, monitor account activity, and examine meme-token evidence through the 6551 service.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The 6551/OpenNews service receives the bearer token and submitted accounts, searches, tweet IDs, and watchlists.

Mitigation: Use the service only if you trust it with those credentials and queries; keep the bearer token private.

Risk: Deleted-post retrieval, follower events, watchlists, and real-time subscriptions can enable sensitive account monitoring.

Mitigation: Review monitoring needs before enabling these features and remove watched accounts when monitoring is no longer needed.

## Reference(s):

- [ClawHub skill listing](https://clawhub.ai/infra403/skills/opentwitter-mcp)
- [6551 API token access](http://app.newsliquid.com/mcp)

## Skill Output:

**Output Type(s):** [Shell commands, Guidance]

**Output Format:** [Markdown with bash and JSON examples]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [API requests require an OPENNEWS_TOKEN bearer token; rate limits apply.]

## Skill Version(s):

1.0.2 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
