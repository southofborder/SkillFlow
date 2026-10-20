## Description:

Helps agents retrieve Twitter/X posts, profiles, follower activity, and meme-token evidence through the 6551 API.

This skill is ready for commercial/non-commercial use.

## Publisher:

[infra403](https://clawhub.ai/user/infra403)

### License/Terms of Use:

MIT-0

## Use Case:

Agents and their users can investigate Twitter/X accounts, posts, follower changes, and meme-token activity, or monitor selected accounts for new events.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The 6551 service receives the API token and the accounts, searches, tweet IDs, and watchlists queried.

Mitigation: Use this skill only if you trust the 6551 service with that token and query data.

Risk: Deleted-tweet retrieval and persistent account monitoring may expose sensitive activity.

Mitigation: Use these features only for legitimate, authorized purposes and review or remove server-side watch entries you create.

## Reference(s):

- [Opentwitter on ClawHub](https://clawhub.ai/infra403/skills/opentwitter-2)
- [6551 API token access](http://app.newsliquid.com/mcp)

## Skill Output:

**Output Type(s):** [Text, Markdown, Shell commands, Guidance]

**Output Format:** [Text or Markdown with API request examples and retrieved data summaries]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Requires an OPENNEWS_TOKEN and curl to query the 6551 service.]

## Skill Version(s):

0.1.1 (source: ClawHub release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
