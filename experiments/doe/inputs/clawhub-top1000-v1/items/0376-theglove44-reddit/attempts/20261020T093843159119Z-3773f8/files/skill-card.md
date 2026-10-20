## Description:

Browse, search, post, and moderate Reddit. Read-only works without auth; posting/moderation requires OAuth setup.

This skill is ready for commercial/non-commercial use.

## Publisher:

[theglove44](https://clawhub.ai/user/theglove44)

### License/Terms of Use:

MIT

## Use Case:

External users and developers use this skill to let an agent browse subreddit posts and comments, search Reddit, and perform authenticated posting or moderation tasks when OAuth and permissions are configured.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: The skill can post replies, submit posts, and perform moderation actions on live Reddit communities.

Mitigation: Require explicit human confirmation before any posting or moderation command is run.

Risk: OAuth tokens are stored locally at ~/.reddit-token.json and can be reused until revoked or deleted.

Mitigation: Protect the token file, delete it when not needed, and use a dedicated Reddit app or account where possible.

Risk: Credential handling is risky if account usernames or passwords are exposed to the agent environment.

Mitigation: Do not set REDDIT_USERNAME or REDDIT_PASSWORD for this skill; prefer the documented OAuth flow with tightly scoped operational use.

## Reference(s):

- [ClawHub Reddit skill page](https://clawhub.ai/theglove44/skills/reddit)
- [Reddit app preferences](https://www.reddit.com/prefs/apps)
- [Reddit OAuth access token endpoint](https://www.reddit.com/api/v1/access_token)
- [README.md](artifact/README.md)
- [SKILL.md](artifact/SKILL.md)

## Skill Output:

**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance]

**Output Format:** [Markdown guidance with inline shell commands; CLI commands return JSON for Reddit data and action results.]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Read-only commands can run without authentication; posting and moderation commands require Reddit OAuth and relevant account permissions.]

## Skill Version(s):

1.0.0 (source: server release metadata)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
